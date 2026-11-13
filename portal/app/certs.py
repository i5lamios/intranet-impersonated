"""Certificates & training (BOSIET, medicals, rope access …): expiry tracking. Managed by AD group Intranet-HSE-Editors.

Everyone sees their own certificates (/training). HSE sees the dashboard (expired / due in 30-60-90 days), the
people × certificate matrix, imports from Excel and keeps scans (private files). Reminders at 60/30/7/0 days (and once
expired) by e-mail to the person, copy HSE_MAIL, plus the AD manager from 30 days, plus a push to the person's phone /
browser; a monthly summary (expired + due within 60 days) to HSE on the 1st. On once CERT_ALERTS=1 and mail works.
"""
import logging
import os
import re
import threading
import time
from datetime import date, datetime
from html import escape

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .push import notify_users
from .core import (SITE, User, current_user, directory, mail_configured, mail_frame, me_person, pool, private_path,
                   role, run_schema, save_private, send_mail)

log = logging.getLogger("certs")
HSE_MAIL = os.environ.get("HSE_MAIL", "hse@example.com")
ALERTS = os.environ.get("CERT_ALERTS", "0") == "1"
THRESHOLDS = (60, 30, 7, 0)
MANAGER_FROM = 30                                          # the manager is copied from this many days before expiry

run_schema("""
CREATE TABLE IF NOT EXISTS cert_types (
  id serial PRIMARY KEY, name text NOT NULL UNIQUE, validity_months int, active boolean NOT NULL DEFAULT true,
  sort int NOT NULL DEFAULT 100
);
CREATE TABLE IF NOT EXISTS certs (
  id serial PRIMARY KEY, person_id text NOT NULL, type_id int NOT NULL REFERENCES cert_types(id),
  number text NOT NULL DEFAULT '', provider text NOT NULL DEFAULT '', issued date, expires date,
  file text, notes text NOT NULL DEFAULT '', updated_by text, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS certs_person ON certs (person_id);
CREATE TABLE IF NOT EXISTS cert_alerts (
  cert_id int NOT NULL REFERENCES certs(id) ON DELETE CASCADE, threshold int NOT NULL,
  sent_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (cert_id, threshold)
);
INSERT INTO cert_types (name, validity_months, sort) SELECT * FROM (VALUES
  ('BOSIET / FOET', 48, 10), ('HUET / CA-EBS', 48, 20), ('Offshore medical', 24, 30), ('H2S awareness', 24, 40),
  ('First aid at work', 36, 50), ('Fire warden', 36, 60), ('Working at height', 24, 70),
  ('Confined space entry', 36, 80), ('IRATA rope access', 36, 90), ('Banksman / slinger', 36, 100)
) v(name, validity_months, sort) WHERE NOT EXISTS (SELECT 1 FROM cert_types);
""")

router = APIRouter()
hse = role("hse")


def status_of(expires):
    if not expires:
        return "none"
    d = (expires - date.today()).days
    return "expired" if d < 0 else "d30" if d <= 30 else "d60" if d <= 60 else "d90" if d <= 90 else "valid"


def _row(r, people=None):
    d = dict(r)
    for k in ("issued", "expires"):
        d[k] = d[k].isoformat() if d.get(k) else None
    d["updated_at"] = d["updated_at"].isoformat(timespec="minutes") if d.get("updated_at") else None
    d["status"] = status_of(r["expires"])
    d["days_left"] = (r["expires"] - date.today()).days if r["expires"] else None
    if people is not None:
        p = people.get(r["person_id"], {})
        d.update(name=p.get("name", "?"), department=p.get("department", ""), title=p.get("title", ""))
    return d


SELECT = "SELECT c.*, t.name AS type_name FROM certs c JOIN cert_types t ON t.id = c.type_id "
NEWER = " AND NOT EXISTS (SELECT 1 FROM certs n WHERE n.person_id = c.person_id AND n.type_id = c.type_id AND n.expires > c.expires)"


# ---------- types ----------
@router.get("/api/certs/types")
def types(user: User = Depends(current_user)):
    with pool.connection() as c:
        return c.execute("SELECT * FROM cert_types ORDER BY sort, name").fetchall()


class TypeIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    validity_months: int | None = Field(default=None, ge=1, le=240)
    active: bool = True
    sort: int = 100


@router.post("/api/certs/types", status_code=201)
def type_add(t: TypeIn, user: User = Depends(hse)):
    with pool.connection() as c:
        return c.execute("INSERT INTO cert_types (name, validity_months, active, sort) VALUES (%s,%s,%s,%s) RETURNING id",
                         (t.name.strip(), t.validity_months, t.active, t.sort)).fetchone()


@router.put("/api/certs/types/{tid}")
def type_set(tid: int, t: TypeIn, user: User = Depends(hse)):
    with pool.connection() as c:
        c.execute("UPDATE cert_types SET name=%s, validity_months=%s, active=%s, sort=%s WHERE id=%s",
                  (t.name.strip(), t.validity_months, t.active, t.sort, tid))
    return {"ok": True}


# ---------- certificates ----------
@router.get("/api/certs/mine")
def mine(user: User = Depends(current_user)):
    p = me_person(user)
    if not p:
        return []
    with pool.connection() as c:
        rows = c.execute(SELECT + "WHERE c.person_id=%s ORDER BY t.sort, c.expires", (p["id"],)).fetchall()
    return [_row(r) for r in rows]


@router.get("/api/certs")
def all_certs(user: User = Depends(hse)):
    people = {p["id"]: p for p in directory.people()}
    with pool.connection() as c:
        rows = c.execute(SELECT + "ORDER BY c.expires NULLS LAST").fetchall()
    out = [_row(r, people) for r in rows if r["person_id"] in people]          # left the company → hidden
    summary = {k: sum(1 for r in out if r["status"] == k) for k in ("expired", "d30", "d60", "d90", "valid", "none")}
    return {"certs": out, "summary": summary, "people": len({r["person_id"] for r in out})}


class CertIn(BaseModel):
    person_id: str = Field(max_length=64)
    type_id: int
    number: str = Field(default="", max_length=100)
    provider: str = Field(default="", max_length=200)
    issued: date | None = None
    expires: date | None = None
    file: str | None = Field(default=None, max_length=60)
    notes: str = Field(default="", max_length=1000)


def _check(c, x: CertIn):
    if not directory.person(x.person_id):
        raise HTTPException(404, "person not found")
    t = c.execute("SELECT * FROM cert_types WHERE id=%s", (x.type_id,)).fetchone()
    if not t:
        raise HTTPException(404, "certificate type not found")
    if x.file:
        private_path("certs", x.file)
    expires = x.expires
    if not expires and x.issued and t["validity_months"]:                      # default: issued + validity
        m = x.issued.month - 1 + t["validity_months"]
        y, m = x.issued.year + m // 12, m % 12 + 1
        expires = date(y, m, min(x.issued.day, 28))
    if x.issued and expires and expires < x.issued:
        raise HTTPException(422, "expires before issued")
    return expires


@router.post("/api/certs", status_code=201)
def cert_add(x: CertIn, user: User = Depends(hse)):
    with pool.connection() as c:
        exp = _check(c, x)
        return c.execute("INSERT INTO certs (person_id, type_id, number, provider, issued, expires, file, notes, updated_by) "
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                         (x.person_id, x.type_id, x.number.strip(), x.provider.strip(), x.issued, exp, x.file,
                          x.notes.strip(), user.username)).fetchone()


@router.put("/api/certs/{cid}")
def cert_set(cid: int, x: CertIn, user: User = Depends(hse)):
    with pool.connection() as c:
        exp = _check(c, x)
        row = c.execute("UPDATE certs SET person_id=%s, type_id=%s, number=%s, provider=%s, issued=%s, expires=%s, file=%s, "
                        "notes=%s, updated_by=%s, updated_at=now() WHERE id=%s RETURNING id",
                        (x.person_id, x.type_id, x.number.strip(), x.provider.strip(), x.issued, exp, x.file,
                         x.notes.strip(), user.username, cid)).fetchone()
        c.execute("DELETE FROM cert_alerts WHERE cert_id=%s", (cid,))           # renewed → reminders start again
    if not row:
        raise HTTPException(404)
    return {"ok": True}


@router.delete("/api/certs/{cid}", status_code=204)
def cert_del(cid: int, user: User = Depends(hse)):
    with pool.connection() as c:
        c.execute("DELETE FROM certs WHERE id=%s", (cid,))
    return Response(status_code=204)


@router.post("/api/certs/file", status_code=201)
async def file_upload(file: UploadFile = File(...), user: User = Depends(hse)):
    return {"name": save_private(await file.read(15 * 1024 * 1024 + 1), "certs", allow_pdf=True)}


@router.get("/api/certs/{cid}/file")
def file_get(cid: int, user: User = Depends(current_user)):
    with pool.connection() as c:
        r = c.execute("SELECT person_id, file FROM certs WHERE id=%s", (cid,)).fetchone()
    if not r or not r["file"]:
        raise HTTPException(404)
    if not user.has("hse"):
        p = me_person(user)
        if not p or p["id"] != r["person_id"]:
            raise HTTPException(404)
    path = private_path("certs", r["file"])
    return FileResponse(path, media_type="application/pdf" if path.endswith(".pdf") else "image/jpeg",
                        headers={"Cache-Control": "private, no-store"})


class ImportIn(BaseModel):
    text: str = Field(max_length=500_000)


_D = re.compile(r"^\s*(\d{1,2})[./-](\d{1,2})[./-](\d{4})\s*$|^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$")


def _date(s):
    m = _D.match(s or "")
    if not m:
        return None
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m.group(1) else \
        date(int(m.group(4)), int(m.group(5)), int(m.group(6)))


@router.post("/api/certs/import")
def cert_import(x: ImportIn, user: User = Depends(hse)):
    """Excel rows (tab or ;): person (username / e-mail / full name), certificate type, issued, expires [, number]."""
    with pool.connection() as c:
        tmap = {t["name"].lower(): t["id"] for t in c.execute("SELECT id, name FROM cert_types")}
        saved, problems = 0, []
        for line in x.text.splitlines():
            if not line.strip():
                continue
            cols = [s.strip() for s in re.split(r"\t|;", line)]
            if len(cols) < 4:
                problems.append(line[:80]); continue
            pid = directory.find(cols[0])
            tid = tmap.get(cols[1].lower())
            try:
                issued, expires = _date(cols[2]), _date(cols[3])
            except ValueError:
                issued = expires = None
            if not pid or not tid or not (issued or expires):
                problems.append(line[:80]); continue
            c.execute("INSERT INTO certs (person_id, type_id, number, issued, expires, updated_by) VALUES (%s,%s,%s,%s,%s,%s)",
                      (pid, tid, cols[4] if len(cols) > 4 else "", issued, expires, user.username))
            saved += 1
    return {"saved": saved, "problems": problems}


# ---------- reminders ----------
def start():
    if ALERTS:
        threading.Thread(target=_loop, name="cert-alerts", daemon=True).start()


def _loop():
    while True:
        try:
            if datetime.now().hour >= 8 and mail_configured():
                remind()
                summary()
        except Exception as e:
            log.error("cert alerts: %s", e)
        time.sleep(1800)


def remind():
    people = {p["id"]: p for p in directory.people()}
    org = {o["id"]: o["manager"] for o in directory.org()}
    with pool.connection() as c:
        # renewed by adding a new record (not editing the old one) → the old one stays quiet
        rows = c.execute(SELECT + "WHERE c.expires IS NOT NULL AND c.expires <= current_date + 60" + NEWER).fetchall()
        for r in rows:
            left = (r["expires"] - date.today()).days
            th = next((t for t in sorted(THRESHOLDS) if left <= t), None)
            p = people.get(r["person_id"])
            if th is None or not p or not p.get("mail"):
                continue
            if not c.execute("INSERT INTO cert_alerts (cert_id, threshold) VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING 1",
                             (r["id"], th)).fetchone():
                continue                                   # already sent (the other replica, or earlier)
            when = "has expired" if left < 0 else "expires today" if left == 0 else f"expires in {left} days"
            mgr = people.get(org.get(r["person_id"]) or "") if th <= MANAGER_FROM else None
            to = [p["mail"], HSE_MAIL] + ([mgr["mail"]] if mgr and mgr.get("mail") else [])
            body = (f"<p>Dear {escape(p['name'])},</p><p>Your <b>{escape(r['type_name'])}</b> certificate {when} "
                    f"({r['expires']:%d.%m.%Y}). Please arrange the renewal with HSE.</p>"
                    + (f"<p style='color:#6B7280'>Copy to your manager, {escape(mgr['name'])}.</p>" if mgr else "")
                    + f'<p><a href="{SITE}/training" style="color:#2E6DB4">My certificates →</a></p>')
            try:
                send_mail(to, f"Certificate {when}: {r['type_name']} — {p['name']}", mail_frame("Certificate reminder", body))
                notify_users([p.get("username")], f"{r['type_name']}: certificate {when}",
                             f"{r['expires']:%d.%m.%Y} — please arrange the renewal with HSE", "/training", f"cert-{r['id']}")
            except Exception as e:
                c.execute("DELETE FROM cert_alerts WHERE cert_id=%s AND threshold=%s", (r["id"], th))
                log.error("cert alert %s: %s", r["id"], e)


def summary():
    """1st of the month (first run after 08:00): expired + due within 60 days, to HSE. Claimed in settings (2 replicas)."""
    today = date.today()
    if today.day != 1:
        return
    key = f"{today:%Y-%m}"
    with pool.connection() as c:
        if not c.execute("INSERT INTO settings (key, value) VALUES ('cert_summary', %s) ON CONFLICT (key) DO UPDATE "
                         "SET value=EXCLUDED.value WHERE settings.value <> EXCLUDED.value RETURNING 1", (key,)).fetchone():
            return
        rows = c.execute(SELECT + "WHERE c.expires IS NOT NULL AND c.expires <= current_date + 60" + NEWER +
                         " ORDER BY c.expires").fetchall()
    people = {p["id"]: p for p in directory.people()}
    rows = [r for r in rows if r["person_id"] in people]
    expired = [r for r in rows if r["expires"] < today]
    due = [r for r in rows if r["expires"] >= today]

    def table(items):
        if not items:
            return "<p style='color:#6B7280'>None.</p>"
        tr = "".join(f"<tr><td style='padding:4px 8px;border-bottom:1px solid #EEF2F7'>{escape(people[r['person_id']]['name'])}</td>"
                     f"<td style='padding:4px 8px;border-bottom:1px solid #EEF2F7;color:#6B7280'>{escape(people[r['person_id']]['department'])}</td>"
                     f"<td style='padding:4px 8px;border-bottom:1px solid #EEF2F7'>{escape(r['type_name'])}</td>"
                     f"<td style='padding:4px 8px;border-bottom:1px solid #EEF2F7;white-space:nowrap'>{r['expires']:%d.%m.%Y}</td></tr>"
                     for r in items)
        return f"<table cellpadding='0' cellspacing='0' style='border-collapse:collapse;font-size:14px;width:100%'>{tr}</table>"
    body = (f"<p><b>{len(expired)}</b> expired · <b>{len(due)}</b> due within 60 days.</p>"
            f"<h3 style='color:#D2262F;margin:18px 0 6px'>Expired</h3>{table(expired)}"
            f"<h3 style='color:#1B2B5B;margin:18px 0 6px'>Due within 60 days</h3>{table(due)}"
            f'<p><a href="{SITE}/admin/training" style="color:#2E6DB4">Certificates dashboard →</a></p>')
    try:
        send_mail(HSE_MAIL, f"Certificates — {today:%B %Y}: {len(expired)} expired, {len(due)} due within 60 days",
                  mail_frame("Monthly certificate summary", body))
    except Exception:
        with pool.connection() as c:                       # try again in 30 minutes
            c.execute("DELETE FROM settings WHERE key='cert_summary' AND value=%s", (key,))
        raise
    log.info("cert summary sent: %d expired, %d due", len(expired), len(due))
