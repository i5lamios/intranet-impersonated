"""Meeting rooms around the booking itself: door check-in, release of unused rooms, door QR signs, colleagues' free/busy,
usage report for IT (AD group Intranet-IT-Editors).

Check-in works for intranet bookings only: Outlook meetings are not in room_bookings, so they are never released.
Anyone signed in can check in at the door (the QR sign opens /rooms/door/<room>), from 10 minutes before the start.
Release is OFF until ROOM_RELEASE_FROM is set (YYYY-MM-DD): put the signs on the doors first. Only bookings made on or
after that date are released, ROOM_RELEASE_MIN (10) minutes after the start, or after booking if that was later.
"""
import logging
import os
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import segno
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from . import rooms as ews
from .core import SITE, User, current_user, directory, mail_configured, mail_frame, pool, role, send_mail

log = logging.getLogger("rooms")
router = APIRouter()
RELEASE_FROM = os.environ.get("ROOM_RELEASE_FROM", "").strip()
RELEASE_MIN = int(os.environ.get("ROOM_RELEASE_MIN", "10"))
EARLY = timedelta(minutes=10)
H0, H1 = 8, 20                                       # working hours in the report, same as the room timeline
rooms = None                                         # the Rooms object of main.py, set by start()
_report = {}


def invite_note():
    return (f"<p>Check in at the room door, or the room is released {RELEASE_MIN} minutes after the start.</p>" if RELEASE_FROM else "")


def checkin_open(b):
    now = datetime.now()
    return not b["checked_in_at"] and b["starts"] - EARLY <= now <= b["ends"]


def _key(room_mail):
    return room_mail.split("@")[0].lower()


def _room(key):
    for name, mail in ews.ROOMS:
        if _key(mail) == key.lower():
            return name, mail
    raise HTTPException(404, "unknown room")


@router.get("/api/rooms/door/{key}")
def door(key: str, user: User = Depends(current_user)):
    """What the sign on the door needs: the room, and the booking that can be checked in now."""
    name, mail = _room(key)
    with pool.connection() as c:
        b = c.execute("SELECT id, subject, starts, ends, checked_in_at FROM room_bookings WHERE room=%s AND released_at IS NULL "
                      "AND starts - interval '10 minutes' <= localtimestamp AND ends > localtimestamp ORDER BY starts LIMIT 1", (mail,)).fetchone()
    return {"name": name, "mail": mail, "booking": b and {"id": b["id"], "subject": b["subject"], "starts": b["starts"].isoformat(timespec="minutes"),
                                                          "ends": b["ends"].isoformat(timespec="minutes"), "checked_in": bool(b["checked_in_at"])}}


@router.post("/api/rooms/book/{bid}/checkin")
def checkin(bid: int, user: User = Depends(current_user)):
    with pool.connection() as c:
        b = c.execute("SELECT * FROM room_bookings WHERE id=%s AND released_at IS NULL", (bid,)).fetchone()
        if not b:
            raise HTTPException(404)
        if not checkin_open(b) and not b["checked_in_at"]:
            raise HTTPException(409, "check-in opens 10 minutes before the start")
        c.execute("UPDATE room_bookings SET checked_in_at=coalesce(checked_in_at, now()) WHERE id=%s", (bid,))
    return {"checked_in": True}


class FreeBusyIn(BaseModel):
    people: list[str] = Field(max_length=60)
    day: date
    start: str = Field(pattern=r"^\d{2}:\d{2}$")
    end: str = Field(pattern=r"^\d{2}:\d{2}$")


@router.post("/api/rooms/availability")
def availability(q: FreeBusyIn, user: User = Depends(current_user)):
    known = {p["mail"].lower() for p in directory.people() if p.get("mail")}
    people = [m.lower() for m in q.people if m.lower() in known]
    if not people or not rooms.enabled:
        return {}
    try:
        start = datetime.combine(q.day, datetime.strptime(q.start, "%H:%M").time())
        end = datetime.combine(q.day, datetime.strptime(q.end, "%H:%M").time())
        return ews.availability(people, start, end)
    except ValueError:
        raise HTTPException(422, "invalid time")
    except Exception as e:                           # the dialog simply shows no status
        log.warning("availability: %s", e)
        return {}


@router.get("/api/rooms/signs")
def signs(user: User = Depends(role("it"))):
    out = []
    for name, mail in ews.ROOMS:
        url = f"{SITE}/rooms/door/{_key(mail)}"
        out.append({"name": name, "url": url, "svg": segno.make(url, error="m").svg_inline(border=4, omitsize=True)})
    return out


def _day_stats(d):
    try:
        return d, rooms.day(d)
    except Exception as e:
        log.warning("report %s: %s", d, e)
        return d, None


@router.get("/api/rooms/report")
def report(days: int = 30, user: User = Depends(role("it"))):
    if days not in (7, 30, 90):
        raise HTTPException(422, "days: 7, 30 or 90")
    hit = _report.get(days)
    if hit and time.time() - hit[0] < 900:
        return hit[1]
    today = date.today()
    work = [d for d in (today - timedelta(days=i) for i in range(days)) if d.weekday() < 5]
    with ThreadPoolExecutor(4) as ex:
        results = list(ex.map(_day_stats, work))
    seen = [r for r in results if r[1] is not None]
    per = defaultdict(lambda: {"meetings": 0, "minutes": 0})
    hours, weekdays = defaultdict(int), defaultdict(int)
    span = H1 * 60
    for d, data in seen:
        for r in data:
            for e in r["events"]:
                a = max(_mins(e["start"]), H0 * 60)
                b = min(_mins(e["end"]) if e["end"][:10] == e["start"][:10] else span, span)
                if b <= a:
                    continue
                per[r["mail"]]["meetings"] += 1
                per[r["mail"]]["minutes"] += b - a
                weekdays[d.weekday()] += b - a
                for h in range(H0, H1):
                    hours[h] += max(0, min(b, (h + 1) * 60) - max(a, h * 60))
    n, cap = len(ews.ROOMS) or 1, len(seen) or 1
    with pool.connection() as c:
        db = c.execute("SELECT count(*) AS booked, count(checked_in_at) AS checked_in, count(released_at) AS released, "
                       "count(*) FILTER (WHERE checked_in_at IS NULL AND released_at IS NULL AND ends < localtimestamp) AS no_checkin "
                       "FROM room_bookings WHERE starts >= %s AND starts < localtimestamp", (today - timedelta(days=days),)).fetchone()
    out = {"days": days, "workdays": len(seen), "missing": len(work) - len(seen),
           "rooms": [{"name": nm, "meetings": per[m]["meetings"], "hours": round(per[m]["minutes"] / 60, 1),
                      "use": round(per[m]["minutes"] / ((H1 - H0) * 60 * cap) * 100)} for nm, m in ews.ROOMS],
           "hours": [{"h": h, "use": round(hours[h] / (60 * n * cap) * 100)} for h in range(H0, H1)],
           "weekdays": [{"d": i, "use": round(weekdays[i] / ((H1 - H0) * 60 * n * max(1, sum(1 for x, _ in seen if x.weekday() == i))) * 100)} for i in range(5)],
           "intranet": dict(db), "release_on": bool(RELEASE_FROM)}
    _report[days] = (time.time(), out)
    return out


def _mins(iso):
    return int(iso[11:13]) * 60 + int(iso[14:16])


# ---------- release of rooms nobody checked in to ----------
def start(room_days):
    global rooms
    rooms = room_days
    if RELEASE_FROM:
        threading.Thread(target=_loop, name="room-release", daemon=True).start()


def _loop():
    while True:
        try:
            release()
        except Exception as e:
            log.error("room release: %s", e)
        time.sleep(60)


def release():
    with pool.connection() as c:                     # the UPDATE claims each row, so the other replica skips it
        rows = c.execute("UPDATE room_bookings SET released_at=now() WHERE organizer IS NOT NULL AND checked_in_at IS NULL AND released_at IS NULL "
                         "AND ends > localtimestamp AND created_at >= %s::date "
                         "AND greatest(starts, created_at::timestamp) < localtimestamp - make_interval(mins => %s) RETURNING *",
                         (RELEASE_FROM, RELEASE_MIN)).fetchall()
    for b in rows:
        try:
            ews.cancel(b["item_id"], b["organizer"])
        except Exception as e:                       # try again next minute
            log.error("release %s: %s", b["id"], e)
            with pool.connection() as c:
                c.execute("UPDATE room_bookings SET released_at=NULL WHERE id=%s", (b["id"],))
            continue
        rooms.forget(b["starts"].date())
        log.info("released booking %s", b["id"])
        if mail_configured():
            html = mail_frame("Room released", f"<p><b>{ews.escape(b['subject'])}</b> at {b['starts']:%H:%M}: nobody checked in within "
                              f"{RELEASE_MIN} minutes, so the room was given back and the meeting cancelled.</p>"
                              f'<p><a href="{SITE}/rooms">Book again</a></p>')
            try:
                send_mail(b["email"], f"Room released: {b['subject']}", html)
            except Exception as e:
                log.warning("release mail: %s", e)
