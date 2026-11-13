"""Admin audit log for IT (AD group Intranet-IT-Editors): who changed what in the editor sections.

One row per successful change made through an editor route (news, banner, weekly e-mail, birthdays, people in AD,
HSE board / reports / actions, certificates, Help Center). Written by the HTTP middleware in main.py from RULES, so a
new editor route is logged by adding one line here. Ordinary staff actions (bookings, hazard reports, profile) are
not logged. Kept for 2 years.

Also the daily security summary for IT: failed sign-ins on SSO (Keycloak events, same client as passkey alerts) and
yesterday's admin changes, mailed to SECURITY_MAIL after 08:00 when there is something to report.
"""
import html
import json
import logging
import os
import re
import secrets as pysecrets
import threading
import time
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from fastapi import APIRouter, Depends

from .core import SITE, User, directory, mail_configured, mail_frame, pool, role, run_schema, secret, send_mail

log = logging.getLogger("audit")
SECURITY_MAIL = os.environ.get("SECURITY_MAIL", "it@example.com")
BAKU = ZoneInfo("Asia/Baku")

run_schema("""
CREATE TABLE IF NOT EXISTS audit_log (
  id bigserial PRIMARY KEY, at timestamptz NOT NULL DEFAULT now(), username text NOT NULL, name text NOT NULL DEFAULT '',
  area text NOT NULL, action text NOT NULL, target text NOT NULL DEFAULT '', detail text NOT NULL DEFAULT '',
  ip text NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS audit_log_at ON audit_log (at);
CREATE TABLE IF NOT EXISTS security_summary (day date PRIMARY KEY, sent_at timestamptz NOT NULL DEFAULT now());
""")

# (method, path pattern, area, action). The first group of the pattern is the target (id / slug).
RULES = [(m, re.compile("^" + p + "$"), area, action) for m, p, area, action in [
    ("POST", r"/api/news", "news", "created"), ("PUT", r"/api/news/(\d+)", "news", "edited"),
    ("DELETE", r"/api/news/(\d+)", "news", "deleted"),
    ("PUT", r"/api/admin/banner", "banner", "changed"), ("PUT", r"/api/admin/digest", "digest", "switched"),
    ("POST", r"/api/admin/digest/test", "digest", "test sent"),
    ("PUT", r"/api/admin/birthdays/([\w-]+)", "birthdays", "edited"), ("POST", r"/api/admin/birthdays/import", "birthdays", "imported"),
    ("PUT", r"/api/hr/people/([\w-]+)", "people", "edited"),
    ("PUT", r"/api/hse/board", "hse-board", "changed"), ("PUT", r"/api/hse/reports/(\d+)", "hse-report", "edited"),
    ("POST", r"/api/hse/reports/(\d+)/actions", "hse-action", "created"), ("PUT", r"/api/hse/actions/(\d+)", "hse-action", "edited"),
    ("POST", r"/api/hse/actions/(\d+)/reopen", "hse-action", "reopened"), ("DELETE", r"/api/hse/actions/(\d+)", "hse-action", "deleted"),
    ("POST", r"/api/certs/types", "cert-type", "created"), ("PUT", r"/api/certs/types/(\d+)", "cert-type", "edited"),
    ("POST", r"/api/certs", "cert", "created"), ("PUT", r"/api/certs/(\d+)", "cert", "edited"),
    ("DELETE", r"/api/certs/(\d+)", "cert", "deleted"), ("POST", r"/api/certs/import", "cert", "imported"),
    ("POST", r"/api/help", "help", "created"), ("PUT", r"/api/help/([a-z0-9-]+)", "help", "edited"),
    ("DELETE", r"/api/help/([a-z0-9-]+)", "help", "deleted"),
]]
AREAS = sorted({r[2] for r in RULES})
PERSON_AREAS = ("people", "birthdays")                    # the target is a directory id → shown as the person's name
# request fields worth showing (never free text bodies, dates of birth or file contents)
FIELDS = ("title", "slug", "name", "category", "status", "risk", "level", "active", "on", "pinned", "published", "due",
          "department", "company", "expires", "validity_months")
PERSON_FIELDS = ("person_id", "owner_id", "manager")


def match(method, path):
    for m, rx, area, action in RULES:
        if m == method:
            g = rx.match(path)
            if g:
                return area, action, (g.group(1) if g.groups() else "")
    return None


def _person(pid):
    p = directory.person(pid) if pid else None
    return (p or {}).get("name") or ""


def _detail(body):
    try:
        d = json.loads(body) if body else {}
    except Exception:
        return ""
    if not isinstance(d, dict):
        return ""
    out = []
    for k in FIELDS:
        v = d.get(k)
        if isinstance(v, dict):                            # {"en": ..., "ru": ...}
            v = v.get("en") or next(iter(v.values()), "")
        if v is None or v == "":
            continue
        out.append(f"{k}: {str(v)[:120]}")
    for k in PERSON_FIELDS:
        if d.get(k):
            out.append(f"{k.replace('_id', '')}: {_person(str(d[k])) or '?'}")
    if isinstance(d.get("text"), str) and "level" in d:   # the emergency banner's text is the change itself
        out.append(f"text: {d['text'][:160]}")
    return "; ".join(out)[:600]


def record(user, method, path, body, ip, created=None):
    """Called by the middleware after a successful request. Never raises."""
    try:
        hit = match(method, path)
        if not hit or not user:
            return
        area, action, target = hit
        if area in PERSON_AREAS and target:
            target = _person(target) or target
        if not target and isinstance(created, dict):       # POST: the new object's id / slug
            target = str(created.get("id") or created.get("slug") or "")
        with pool.connection() as c:
            c.execute("INSERT INTO audit_log (username, name, area, action, target, detail, ip) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                      (user.username[:64], user.name[:120], area, action, target[:120], _detail(body), ip[:64]))
            if pysecrets.randbelow(200) == 0:
                c.execute("DELETE FROM audit_log WHERE at < now() - interval '2 years'")
    except Exception as e:
        log.error("audit: %s", e)


router = APIRouter()
it = role("it")


@router.get("/api/admin/audit")
def audit_list(area: str = "", who: str = "", days: int = 30, offset: int = 0, user: User = Depends(it)):
    days, offset = max(1, min(days, 730)), max(0, offset)
    where, args = ["at > now() - make_interval(days => %s)"], [days]
    if area in AREAS:
        where.append("area = %s"); args.append(area)
    if who.strip():
        where.append("(username ILIKE %s OR name ILIKE %s)"); args += [f"%{who.strip()[:60]}%"] * 2
    w = " AND ".join(where)
    with pool.connection() as c:
        rows = c.execute(f"SELECT id, at, username, name, area, action, target, detail, ip FROM audit_log WHERE {w} "
                         "ORDER BY id DESC LIMIT 101 OFFSET %s", (*args, offset)).fetchall()
    return {"areas": AREAS, "more": len(rows) > 100, "rows": rows[:100]}


# ---------- daily security summary ----------
KC = os.environ.get("KC_URL", "https://sso.example.com")
REALM = "company"
CLIENT = os.environ.get("KC_EVENTS_CLIENT", "intranet-events")
# sign-in errors that are noise (expired tab, cancelled window), not a wrong password or code
NOISE = {"cookie_not_found", "expired_code", "invalid_code", "rejected_by_user", "consent_denied", "session_expired"}


def start():
    if secret("KC_EVENTS_SECRET", ""):
        threading.Thread(target=_loop, name="security-summary", daemon=True).start()


def _loop():
    while True:
        try:
            if datetime.now(BAKU).hour >= 8 and mail_configured():
                summary()
        except Exception as e:
            log.error("security summary: %s", e)
        time.sleep(1800)


def _events(day):
    r = requests.post(f"{KC}/realms/{REALM}/protocol/openid-connect/token", timeout=15,
                      data={"grant_type": "client_credentials", "client_id": CLIENT, "client_secret": secret("KC_EVENTS_SECRET")})
    r.raise_for_status()
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = requests.get(f"{KC}/admin/realms/{REALM}/events", headers=h, timeout=30,
                     params=[("type", "LOGIN_ERROR"), ("max", 2000), ("dateFrom", (day - timedelta(days=1)).isoformat()), ("dateTo", day.isoformat())])
    r.raise_for_status()
    lo = datetime.combine(day, datetime.min.time(), BAKU).timestamp() * 1000
    return [e for e in r.json() if lo <= e["time"] < lo + 86400000 and e.get("error") not in NOISE]


def summary(day=None, to=None):
    """Yesterday (Baku time): failed SSO sign-ins + admin changes → one mail to IT. Quiet days send nothing."""
    test = day is not None or to is not None
    day = day or (datetime.now(BAKU).date() - timedelta(days=1))
    if not test:
        with pool.connection() as c:                       # claimed first: the two replicas don't both send
            if not c.execute("INSERT INTO security_summary (day) VALUES (%s) ON CONFLICT DO NOTHING RETURNING 1", (day,)).fetchone():
                return
    ev = _events(day)
    with pool.connection() as c:
        changes = c.execute("SELECT area, count(*) AS n FROM audit_log WHERE (at AT TIME ZONE 'Asia/Baku')::date = %s "
                            "GROUP BY area ORDER BY n DESC", (day,)).fetchall()
    if not ev and not changes:
        return
    esc = html.escape
    users = Counter((e.get("details") or {}).get("username") or "(unknown)" for e in ev)
    ips = Counter(e.get("ipAddress") or "?" for e in ev)
    kinds = Counter(e.get("error") or "?" for e in ev)
    td = 'style="padding:4px 12px 4px 0;border-bottom:1px solid #DCE3EE"'
    table = lambda rows: ('<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px">'
                          + "".join(f"<tr><td {td}>{esc(str(k))}</td><td {td}><b>{n}</b></td></tr>" for k, n in rows) + "</table>")
    body = f"<p>{day.strftime('%d.%m.%Y')}, Baku time.</p>"
    if ev:
        loud = [u for u, n in users.items() if n >= 5]
        body += f"<p><b>Failed sign-ins on SSO: {len(ev)}</b> ({', '.join(f'{esc(k)} {n}' for k, n in kinds.most_common(5))})</p>"
        if loud:
            body += f'<p style="color:#B91C1C"><b>5 or more failures:</b> {esc(", ".join(sorted(loud)))} — check with the person.</p>'
        body += "<p>By account</p>" + table(users.most_common(10)) + "<p>By address</p>" + table(ips.most_common(10))
    else:
        body += "<p>No failed sign-ins on SSO.</p>"
    if changes:
        body += (f"<p><b>Admin changes in the intranet: {sum(r['n'] for r in changes)}</b></p>" + table([(r["area"], r["n"]) for r in changes])
                 + f'<p><a href="{SITE}/admin/audit" style="color:#2E6DB4">Open the audit log</a></p>')
    send_mail(to or SECURITY_MAIL, f"Security summary {day.strftime('%d.%m.%Y')}: {len(ev)} failed sign-ins",
              mail_frame("Daily security summary", body))
    log.info("security summary %s: %d failed sign-ins, %d change areas", day, len(ev), len(changes))
