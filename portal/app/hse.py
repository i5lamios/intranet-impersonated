"""HSE board (home page + /hse) and hazard / near-miss reporting. Editors = AD group Intranet-HSE-Editors.

Board: days without a lost-time incident (from the last LTI date), best record, man-hours YTD, safety moment of the week,
YTD counts of reports. Reports: any signed-in employee, optionally anonymous (no name stored at all); photos are
private (HSE, reporter, action owners). New reports are e-mailed to HSE_MAIL once the intranet mail account is configured.

Follow-up: HSE sets the risk and adds corrective actions (owner from AD, due date). The owner gets an e-mail + push,
sees the action on /hse and marks it done with a note; overdue actions are reminded weekly (copy HSE). A report closes
only when its actions are done. The reporter (unless anonymous) is told by e-mail + push when the status changes.
"""
import logging
import os
import threading
import time
from datetime import date, datetime
from html import escape

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from .core import (SITE, User, current_user, directory, mail_configured, mail_frame, me_person, pool, private_path, role,
                   run_schema, sanitize, save_private, send_mail)
from .push import notify_users

log = logging.getLogger("hse")
HSE_MAIL = os.environ.get("HSE_MAIL", "hse@example.com")
KINDS = ("near_miss", "unsafe_act", "unsafe_condition", "good_practice")
STATUSES = ("new", "review", "closed")
RISKS = ("low", "medium", "high")
LABELS = {"near_miss": "Near miss", "unsafe_act": "Unsafe act", "unsafe_condition": "Unsafe condition",
          "good_practice": "Good practice"}
STATUS_LABELS = {"new": "New", "review": "In review", "closed": "Closed"}

run_schema("""
CREATE TABLE IF NOT EXISTS hse_board (
  id int PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  last_lti date, record_days int, manhours_ytd bigint, target text NOT NULL DEFAULT '',
  moment_title text NOT NULL DEFAULT '', moment_html text NOT NULL DEFAULT '',
  updated_by text, updated_at timestamptz
);
CREATE TABLE IF NOT EXISTS hse_reports (
  id serial PRIMARY KEY,
  kind text NOT NULL, happened_at timestamp NOT NULL, location text NOT NULL, description text NOT NULL,
  action text NOT NULL DEFAULT '', photo text, anonymous boolean NOT NULL DEFAULT false,
  reporter text, reporter_name text,                -- NULL when anonymous
  status text NOT NULL DEFAULT 'new', hse_comment text NOT NULL DEFAULT '',
  created_at timestamptz NOT NULL DEFAULT now(), updated_by text, updated_at timestamptz
);
ALTER TABLE hse_reports ADD COLUMN IF NOT EXISTS risk text NOT NULL DEFAULT '';
CREATE TABLE IF NOT EXISTS hse_actions (
  id serial PRIMARY KEY, report_id int NOT NULL REFERENCES hse_reports(id) ON DELETE CASCADE,
  title text NOT NULL, owner_id text NOT NULL, owner_name text NOT NULL, due date NOT NULL,
  status text NOT NULL DEFAULT 'open', done_note text NOT NULL DEFAULT '', done_at timestamptz, done_by text,
  created_by text, created_at timestamptz NOT NULL DEFAULT now(), reminded_on date
);
CREATE INDEX IF NOT EXISTS hse_actions_report ON hse_actions (report_id);
CREATE INDEX IF NOT EXISTS hse_actions_owner ON hse_actions (owner_id);
""")

router = APIRouter()
hse = role("hse")


def _board():
    with pool.connection() as c:
        b = c.execute("SELECT * FROM hse_board WHERE id=1").fetchone() or {}
        counts = {r["kind"]: r["n"] for r in c.execute(
            "SELECT kind, count(*) AS n FROM hse_reports WHERE created_at >= date_trunc('year', now()) GROUP BY kind")}
        open_n = c.execute("SELECT count(*) AS n FROM hse_reports WHERE status <> 'closed'").fetchone()["n"]
        acts = c.execute("SELECT count(*) FILTER (WHERE status='open') AS open, "
                         "count(*) FILTER (WHERE status='open' AND due < current_date) AS overdue FROM hse_actions").fetchone()
    days = (date.today() - b["last_lti"]).days if b.get("last_lti") else None
    return {"days_without_lti": days, "record_days": max(b.get("record_days") or 0, days or 0) or None,
            "last_lti": b["last_lti"].isoformat() if b.get("last_lti") else None,
            "manhours_ytd": b.get("manhours_ytd"), "target": b.get("target", ""),
            "moment_title": b.get("moment_title", ""), "moment_html": b.get("moment_html", ""),
            "counts": {k: counts.get(k, 0) for k in KINDS}, "open": open_n,
            "actions_open": acts["open"], "actions_overdue": acts["overdue"],
            "updated_at": b["updated_at"].isoformat() if b.get("updated_at") else None}


@router.get("/api/hse")
def board(user: User = Depends(current_user)):
    return _board()


class BoardIn(BaseModel):
    last_lti: date | None = None
    record_days: int | None = Field(default=None, ge=0, le=100000)
    manhours_ytd: int | None = Field(default=None, ge=0)
    target: str = Field(default="", max_length=200)
    moment_title: str = Field(default="", max_length=200)
    moment_html: str = Field(default="", max_length=100_000)


@router.put("/api/hse/board")
def board_set(b: BoardIn, user: User = Depends(hse)):
    if b.last_lti and b.last_lti > date.today():
        raise HTTPException(422, "the last LTI date is in the future")
    with pool.connection() as c:
        c.execute("INSERT INTO hse_board (id, last_lti, record_days, manhours_ytd, target, moment_title, moment_html, "
                  "updated_by, updated_at) VALUES (1,%s,%s,%s,%s,%s,%s,%s,now()) ON CONFLICT (id) DO UPDATE SET "
                  "last_lti=EXCLUDED.last_lti, record_days=EXCLUDED.record_days, manhours_ytd=EXCLUDED.manhours_ytd, "
                  "target=EXCLUDED.target, moment_title=EXCLUDED.moment_title, moment_html=EXCLUDED.moment_html, "
                  "updated_by=EXCLUDED.updated_by, updated_at=now()",
                  (b.last_lti, b.record_days, b.manhours_ytd, b.target.strip(), b.moment_title.strip(),
                   sanitize(b.moment_html), user.username))
    return _board()


# ---------- reports ----------
class ReportIn(BaseModel):
    kind: str = Field(pattern="^(" + "|".join(KINDS) + ")$")
    happened_at: datetime
    location: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10, max_length=4000)
    action: str = Field(default="", max_length=2000)
    photo: str | None = Field(default=None, max_length=60)
    anonymous: bool = False


@router.post("/api/hse/photo", status_code=201)
async def photo_upload(file: UploadFile = File(...), user: User = Depends(current_user)):
    return {"name": save_private(await file.read(15 * 1024 * 1024 + 1), "hse")}


@router.post("/api/hse/reports", status_code=201)
def report_create(r: ReportIn, user: User = Depends(current_user)):
    if r.happened_at.replace(tzinfo=None) > datetime.now():
        raise HTTPException(422, "the time is in the future")
    if r.photo:
        private_path("hse", r.photo)
    with pool.connection() as c:
        row = c.execute(
            "INSERT INTO hse_reports (kind, happened_at, location, description, action, photo, anonymous, reporter, "
            "reporter_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (r.kind, r.happened_at.replace(tzinfo=None), r.location.strip(), r.description.strip(), r.action.strip(),
             r.photo, r.anonymous, None if r.anonymous else user.username, None if r.anonymous else user.name)).fetchone()
    if mail_configured():
        threading.Thread(target=_notify, args=(row["id"], r, None if r.anonymous else user.name), daemon=True).start()
    return {"id": row["id"]}


def _notify(rid, r, who):
    labels = LABELS
    try:
        body = (f"<p><b>{labels[r.kind]}</b> — {escape(r.location)}, {r.happened_at:%d.%m.%Y %H:%M}<br>"
                f"Reported by: {escape(who) if who else '<i>anonymous</i>'}</p><p>{escape(r.description)}</p>"
                + (f"<p><b>Immediate action:</b> {escape(r.action)}</p>" if r.action else "")
                + f'<p><a href="{SITE}/admin/hse/reports" style="color:#2E6DB4">Open in the intranet →</a></p>')
        send_mail(HSE_MAIL, f"HSE report #{rid}: {labels[r.kind]} — {r.location}", mail_frame(f"HSE report #{rid}", body))
    except Exception as e:
        log.error("hse notify: %s", e)


def _iso(d):
    for k in ("happened_at", "created_at", "updated_at", "done_at"):
        if d.get(k):
            d[k] = d[k].isoformat(timespec="minutes")
    if d.get("due"):
        d["due"] = d["due"].isoformat()
    return d


def _out(r, full):
    d = _iso(dict(r))
    if not full:
        d.pop("reporter", None)
    return d


def _action(a):
    d = _iso(dict(a))
    d["overdue"] = a["status"] == "open" and a["due"] < date.today()
    return d


@router.get("/api/hse/reports")
def report_list(status: str = "", user: User = Depends(hse)):
    with pool.connection() as c:
        if status == "overdue":
            rows = c.execute("SELECT * FROM hse_reports WHERE id IN (SELECT report_id FROM hse_actions WHERE status='open' "
                             "AND due < current_date) ORDER BY created_at DESC").fetchall()
        else:
            rows = c.execute("SELECT * FROM hse_reports " + ("WHERE status=%s " if status else "") +
                             "ORDER BY created_at DESC LIMIT 500", ((status,) if status else ())).fetchall()
        acts = c.execute("SELECT * FROM hse_actions WHERE report_id = ANY(%s) ORDER BY due, id",
                         ([r["id"] for r in rows],)).fetchall()
    out = [_out(r, True) for r in rows]
    for r in out:
        r["actions"] = [_action(a) for a in acts if a["report_id"] == r["id"]]
    return out


@router.get("/api/hse/reports/mine")
def report_mine(user: User = Depends(current_user)):
    with pool.connection() as c:
        rows = c.execute("SELECT r.*, (SELECT count(*) FROM hse_actions a WHERE a.report_id=r.id) AS actions_total, "
                         "(SELECT count(*) FROM hse_actions a WHERE a.report_id=r.id AND a.status='done') AS actions_done "
                         "FROM hse_reports r WHERE reporter=%s ORDER BY created_at DESC LIMIT 100", (user.username,)).fetchall()
    return [_out(r, False) for r in rows]


class ReportUpdate(BaseModel):
    status: str = Field(pattern="^(" + "|".join(STATUSES) + ")$")
    hse_comment: str = Field(default="", max_length=4000)
    risk: str = Field(default="", pattern="^(|" + "|".join(RISKS) + ")$")


@router.put("/api/hse/reports/{rid}")
def report_update(rid: int, u: ReportUpdate, user: User = Depends(hse)):
    with pool.connection() as c:
        old = c.execute("SELECT * FROM hse_reports WHERE id=%s", (rid,)).fetchone()
        if not old:
            raise HTTPException(404)
        if u.status == "closed":
            n = c.execute("SELECT count(*) AS n FROM hse_actions WHERE report_id=%s AND status='open'", (rid,)).fetchone()["n"]
            if n:
                raise HTTPException(409, f"{n} action(s) still open — finish or delete them first")
        c.execute("UPDATE hse_reports SET status=%s, hse_comment=%s, risk=%s, updated_by=%s, updated_at=now() WHERE id=%s",
                  (u.status, u.hse_comment.strip(), u.risk, user.username, rid))
    if old["reporter"] and (old["status"] != u.status or old["hse_comment"] != u.hse_comment.strip()):
        _bg(_tell_reporter, dict(old), u.status, u.hse_comment.strip())
    return {"ok": True}


def _bg(fn, *args):
    threading.Thread(target=lambda: _safe(fn, *args), daemon=True).start()


def _safe(fn, *args):
    try:
        fn(*args)
    except Exception as e:
        log.error("hse %s: %s", fn.__name__, e)


def _person_by_username(username):
    pid = directory.find(username or "")
    return directory.person(pid) if pid else None


def _tell_reporter(r, status, comment):
    title = f"Your HSE report #{r['id']}: {STATUS_LABELS[status].lower()}"
    notify_users([r["reporter"]], title, comment or f"{LABELS[r['kind']]} — {r['location']}", "/hse", f"hse-report-{r['id']}")
    p = _person_by_username(r["reporter"])
    if not (p and p.get("mail") and mail_configured()):
        return
    body = (f"<p>Dear {escape(p['name'])},</p><p>Thank you for your report <b>#{r['id']}</b> "
            f"({LABELS[r['kind']]} — {escape(r['location'])}, {r['happened_at']:%d.%m.%Y}).</p>"
            f"<p>Status: <b>{STATUS_LABELS[status]}</b></p>"
            + (f"<p><b>HSE comment:</b> {escape(comment)}</p>" if comment else "")
            + f'<p><a href="{SITE}/hse" style="color:#2E6DB4">My reports →</a></p>')
    send_mail(p["mail"], title, mail_frame("HSE report update", body))


# ---------- corrective actions ----------
class ActionIn(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    owner_id: str = Field(max_length=64)
    due: date


@router.post("/api/hse/reports/{rid}/actions", status_code=201)
def action_add(rid: int, a: ActionIn, user: User = Depends(hse)):
    p = directory.person(a.owner_id)
    if not p:
        raise HTTPException(404, "person not found")
    with pool.connection() as c:
        r = c.execute("SELECT * FROM hse_reports WHERE id=%s", (rid,)).fetchone()
        if not r:
            raise HTTPException(404)
        row = c.execute("INSERT INTO hse_actions (report_id, title, owner_id, owner_name, due, created_by) "
                        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING *", (rid, a.title.strip(), p["id"], p["name"], a.due,
                                                                     user.username)).fetchone()
        if r["status"] == "new":
            c.execute("UPDATE hse_reports SET status='review', updated_by=%s, updated_at=now() WHERE id=%s", (user.username, rid))
    _bg(_tell_owner, dict(row), dict(r), p, "assigned")
    return _action(row)


@router.put("/api/hse/actions/{aid}")
def action_set(aid: int, a: ActionIn, user: User = Depends(hse)):
    p = directory.person(a.owner_id)
    if not p:
        raise HTTPException(404, "person not found")
    with pool.connection() as c:
        old = c.execute("SELECT * FROM hse_actions WHERE id=%s", (aid,)).fetchone()
        if not old:
            raise HTTPException(404)
        row = c.execute("UPDATE hse_actions SET title=%s, owner_id=%s, owner_name=%s, due=%s, reminded_on=NULL WHERE id=%s "
                        "RETURNING *", (a.title.strip(), p["id"], p["name"], a.due, aid)).fetchone()
        r = c.execute("SELECT * FROM hse_reports WHERE id=%s", (row["report_id"],)).fetchone()
    if old["owner_id"] != p["id"] and row["status"] == "open":
        _bg(_tell_owner, dict(row), dict(r), p, "assigned")
    return _action(row)


@router.post("/api/hse/actions/{aid}/reopen")
def action_reopen(aid: int, user: User = Depends(hse)):
    with pool.connection() as c:
        row = c.execute("UPDATE hse_actions SET status='open', done_at=NULL, done_by=NULL, reminded_on=NULL WHERE id=%s "
                        "RETURNING report_id", (aid,)).fetchone()
        if not row:
            raise HTTPException(404)
        c.execute("UPDATE hse_reports SET status='review' WHERE id=%s AND status='closed'", (row["report_id"],))
    return {"ok": True}


@router.delete("/api/hse/actions/{aid}", status_code=204)
def action_del(aid: int, user: User = Depends(hse)):
    with pool.connection() as c:
        c.execute("DELETE FROM hse_actions WHERE id=%s", (aid,))
    return Response(status_code=204)


@router.get("/api/hse/actions/mine")
def actions_mine(user: User = Depends(current_user)):
    p = me_person(user)
    if not p:
        return []
    with pool.connection() as c:
        rows = c.execute("SELECT a.*, r.kind, r.location, r.description, r.happened_at, r.photo, r.risk FROM hse_actions a "
                         "JOIN hse_reports r ON r.id = a.report_id WHERE a.owner_id=%s AND "
                         "(a.status='open' OR a.done_at > now() - interval '30 days') ORDER BY a.status DESC, a.due",
                         (p["id"],)).fetchall()
    return [_action(a) for a in rows]


class DoneIn(BaseModel):
    note: str = Field(min_length=3, max_length=2000)


@router.post("/api/hse/actions/{aid}/done")
def action_done(aid: int, d: DoneIn, user: User = Depends(current_user)):
    with pool.connection() as c:
        a = c.execute("SELECT * FROM hse_actions WHERE id=%s", (aid,)).fetchone()
        if not a:
            raise HTTPException(404)
        p = me_person(user)
        if not user.has("hse") and not (p and p["id"] == a["owner_id"]):
            raise HTTPException(403, "only the action owner or HSE")
        if a["status"] == "done":
            return {"ok": True}
        c.execute("UPDATE hse_actions SET status='done', done_note=%s, done_at=now(), done_by=%s WHERE id=%s",
                  (d.note.strip(), user.username, aid))
        left = c.execute("SELECT count(*) AS n FROM hse_actions WHERE report_id=%s AND status='open'",
                         (a["report_id"],)).fetchone()["n"]
        r = c.execute("SELECT * FROM hse_reports WHERE id=%s", (a["report_id"],)).fetchone()
    if mail_configured():
        _bg(_tell_hse_done, dict(a), dict(r), user.name or user.username, d.note.strip(), left)
    return {"ok": True}


def _report_line(r):
    return (f"<p><b>Report #{r['id']}</b> — {LABELS[r['kind']]}, {escape(r['location'])}, {r['happened_at']:%d.%m.%Y}"
            + (f", risk <b>{r['risk']}</b>" if r.get("risk") else "") + f"<br>{escape(r['description'][:600])}</p>")


def _tell_owner(a, r, p, why):
    when = f"{a['due']:%d.%m.%Y}"
    title = f"HSE action for you: {a['title'][:80]}" if why == "assigned" else f"HSE action overdue: {a['title'][:80]}"
    notify_users([p.get("username")], title, f"Due {when}", "/hse", f"hse-action-{a['id']}")
    if not (p.get("mail") and mail_configured()):
        return
    lead = ("HSE has asked you to take this action" if why == "assigned"
            else f"This action was due on <b>{when}</b> and is still open")
    body = (f"<p>Dear {escape(p['name'])},</p><p>{lead}:</p>"
            f"<p style='font-size:17px'><b>{escape(a['title'])}</b><br>Due: <b>{when}</b></p>{_report_line(r)}"
            f"<p>When it is done, open the HSE board and press <b>Mark done</b> with a short note of what was done.</p>"
            f'<p><a href="{SITE}/hse" style="color:#2E6DB4">My HSE actions →</a></p>')
    send_mail([p["mail"]] + ([HSE_MAIL] if why != "assigned" else []), title, mail_frame("HSE action", body))


def _tell_hse_done(a, r, who, note, left):
    body = (f"<p><b>{escape(who)}</b> finished the action <b>{escape(a['title'])}</b>.</p><p><b>What was done:</b> "
            f"{escape(note)}</p>{_report_line(r)}"
            + ("<p><b>All actions of this report are done</b> — it can be closed.</p>" if not left
               else f"<p>{left} action(s) of this report still open.</p>")
            + f'<p><a href="{SITE}/admin/hse/reports" style="color:#2E6DB4">Open in the intranet →</a></p>')
    send_mail(HSE_MAIL, f"HSE action done (report #{r['id']}): {a['title'][:80]}", mail_frame("HSE action done", body))


def start():
    threading.Thread(target=_loop, name="hse-actions", daemon=True).start()


def _loop():
    while True:
        try:
            if datetime.now().hour >= 8:
                remind()
        except Exception as e:
            log.error("hse reminders: %s", e)
        time.sleep(1800)


def remind():
    """Open actions on / past their due date: owner (copy HSE) on the due date, then once a week."""
    with pool.connection() as c:
        rows = c.execute("UPDATE hse_actions SET reminded_on=current_date WHERE status='open' AND due <= current_date AND "
                         "(reminded_on IS NULL OR reminded_on <= current_date - 7) RETURNING *").fetchall()
        reports = {r["id"]: r for r in c.execute("SELECT * FROM hse_reports WHERE id = ANY(%s)",
                                                  ([a["report_id"] for a in rows],))}
    for a in rows:
        p = directory.person(a["owner_id"])
        if p:
            _safe(_tell_owner, dict(a), dict(reports[a["report_id"]]), p, "overdue")


@router.get("/api/hse/photo/{name}")
def photo_get(name: str, user: User = Depends(current_user)):
    path = private_path("hse", name)
    if not user.has("hse"):
        p = me_person(user)
        with pool.connection() as c:
            if not c.execute("SELECT 1 FROM hse_reports r WHERE photo=%s AND (reporter=%s OR EXISTS (SELECT 1 FROM hse_actions a "
                             "WHERE a.report_id=r.id AND a.owner_id=%s))", (name, user.username, p["id"] if p else "")).fetchone():
                raise HTTPException(404)
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=3600"})
