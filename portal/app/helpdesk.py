"""Report a problem to IT: a short form (what, how urgent, where, screenshot) that becomes a ServiceDesk Plus request
(helpdesk.example.com, REST API v3) with the reporter as the requester and the technical details IT always asks for
(browser, device, office, phone) filled in. "My requests" shows the live status from ServiceDesk.

API key: secret SDP_KEY (technician API key generated in ServiceDesk → Personalize → API key). Without it the request
is e-mailed to HELPDESK_MAIL (Reply-To = the reporter) and kept here, so nothing is lost.
"""
import html
import json
import logging
import os
import time

import requests
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from .core import (CA, User, current_user, mail_configured, mail_frame, me_person, pool, private_path, run_schema,
                   save_private, secret, send_mail)

log = logging.getLogger("helpdesk")
SDP = os.environ.get("SDP_URL", "https://helpdesk.example.com").rstrip("/")
HELPDESK_MAIL = os.environ.get("HELPDESK_MAIL", "helpdesk@example.com")
CATEGORIES = {"computer": "Computer / laptop", "printer": "Printer / scanner", "mail": "E-mail / Outlook",
              "phone": "Phone / 3CX", "network": "Network / Wi-Fi / VPN", "access": "Password / access",
              "software": "Software / application", "other": "Other"}
URGENCY = {"blocked": "I cannot work", "degraded": "I can work, but it needs fixing", "request": "Question or request"}

run_schema("""
CREATE TABLE IF NOT EXISTS helpdesk_requests (
  id serial PRIMARY KEY, username text NOT NULL, name text NOT NULL DEFAULT '', category text NOT NULL,
  urgency text NOT NULL, subject text NOT NULL, description text NOT NULL, location text NOT NULL DEFAULT '',
  file text, sdp_id text, sent_by text NOT NULL DEFAULT '', error text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS helpdesk_requests_user ON helpdesk_requests (username);
""")

router = APIRouter()


def _key():
    return secret("SDP_KEY", "")


def _verify():
    return CA if os.path.exists(CA) and os.environ.get("SDP_CA") == "company" else True


def _sdp(method, path, timeout=20, **kw):
    r = requests.request(method, f"{SDP}/api/v3/{path}", headers={"authtoken": _key(),
                         "Accept": "application/vnd.manageengine.sdp.v3+json"}, timeout=timeout, verify=_verify(), **kw)
    try:
        data = r.json()
    except ValueError:
        r.raise_for_status()
        raise RuntimeError(f"ServiceDesk answered HTTP {r.status_code} without JSON")
    st = data.get("response_status") or {}
    st = st[0] if isinstance(st, list) and st else st
    if r.status_code >= 400 or (isinstance(st, dict) and st.get("status") == "failed"):
        msgs = "; ".join(m.get("message", "") for m in (st.get("messages") or []) if isinstance(m, dict))
        raise RuntimeError(f"ServiceDesk HTTP {r.status_code}: {msgs or str(data)[:200]}")
    return data


@router.get("/api/helpdesk/config")
def config(user: User = Depends(current_user)):
    return {"categories": list(CATEGORIES), "urgency": list(URGENCY), "api": bool(_key()), "url": SDP}


@router.post("/api/helpdesk/file", status_code=201)
async def file_upload(file: UploadFile = File(...), user: User = Depends(current_user)):
    return {"name": save_private(await file.read(15 * 1024 * 1024 + 1), "helpdesk")}


class ProblemIn(BaseModel):
    category: str = Field(pattern="^(" + "|".join(CATEGORIES) + ")$")
    urgency: str = Field(pattern="^(" + "|".join(URGENCY) + ")$")
    subject: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5, max_length=6000)
    location: str = Field(default="", max_length=200)
    file: str | None = Field(default=None, max_length=60)
    page: str = Field(default="", max_length=300)
    screen: str = Field(default="", max_length=40)


@router.post("/api/helpdesk/requests", status_code=201)
def create(x: ProblemIn, request: Request, user: User = Depends(current_user)):
    if x.file:
        private_path("helpdesk", x.file)
    p = me_person(user) or {}
    e = html.escape
    facts = [("Reported by", f"{user.name} ({user.username})"), ("E-mail", user.email),
             ("Department", p.get("department", "")), ("Office", p.get("office", "")),
             ("Phone", " / ".join(v for v in (p.get("extension"), p.get("phone"), p.get("mobile")) if v)),
             ("Where", x.location.strip()), ("Category", CATEGORIES[x.category]), ("Urgency", URGENCY[x.urgency]),
             ("Browser / device", request.headers.get("user-agent", "")[:300]), ("Screen", x.screen),
             ("Came from page", x.page), ("IP address", request.headers.get("x-forwarded-for", "").split(",")[0].strip()
                                         or (request.client.host if request.client else ""))]
    desc = (f"<div>{e(x.description.strip()).replace(chr(10), '<br>')}</div><br><table>"
            + "".join(f"<tr><td style='color:#6B7280;padding-right:12px'>{k}</td><td>{e(v)}</td></tr>" for k, v in facts if v)
            + "</table><p style='color:#6B7280'>Sent from the intranet (Report a problem).</p>")
    subject = ("[URGENT] " if x.urgency == "blocked" else "") + f"{CATEGORIES[x.category]}: {x.subject.strip()}"
    with pool.connection() as c:
        rid = c.execute("INSERT INTO helpdesk_requests (username, name, category, urgency, subject, description, location, "
                        "file) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                        (user.username, user.name, x.category, x.urgency, x.subject.strip(), x.description.strip(),
                         x.location.strip(), x.file)).fetchone()["id"]
    sdp_id, sent_by, err = None, "", None
    if _key():
        try:
            req = {"subject": subject[:250], "description": desc, "requester": {"email_id": user.email or user.username}}
            data = _sdp("POST", "requests", data={"input_data": json.dumps({"request": req})})
            sdp_id, sent_by = str(data["request"]["id"]), "api"
            if x.file:
                try:
                    with open(private_path("helpdesk", x.file), "rb") as f:
                        _sdp("PUT", f"requests/{sdp_id}/upload", files={"input_file": ("screenshot.jpg", f, "image/jpeg")})
                except Exception as ex:
                    log.warning("helpdesk: attachment to %s failed: %s", sdp_id, ex)
        except Exception as ex:
            err = str(ex)[:500]
            log.error("helpdesk: ServiceDesk API failed, falling back to e-mail: %s", ex)
    if not sdp_id:
        if not mail_configured():
            raise HTTPException(503, "the helpdesk cannot be reached right now — please call IT")
        try:
            att = []
            if x.file:
                with open(private_path("helpdesk", x.file), "rb") as f:
                    att = [("screenshot.jpg", f.read(), "image/jpeg")]
            send_mail(HELPDESK_MAIL, subject, mail_frame("Problem report", desc), attachments=att,
                      reply_to=user.email or None, sender_name=f"{user.name} via Intranet")
            sent_by = "mail"
        except Exception as ex:
            log.error("helpdesk mail: %s", ex)
            raise HTTPException(503, "the helpdesk cannot be reached right now — please call IT")
    with pool.connection() as c:
        c.execute("UPDATE helpdesk_requests SET sdp_id=%s, sent_by=%s, error=%s WHERE id=%s", (sdp_id, sent_by, err, rid))
    return {"id": rid, "sdp_id": sdp_id, "sent_by": sent_by, "url": _link(sdp_id)}


def _link(sdp_id):
    return f"{SDP}/WorkOrder.do?woMode=viewWO&woID={sdp_id}" if sdp_id else None


_status: dict[str, tuple[float, str]] = {}


def _live_status(sdp_id):
    hit = _status.get(sdp_id)
    if hit and time.time() - hit[0] < 300:
        return hit[1]
    try:
        st = ((_sdp("GET", f"requests/{sdp_id}", timeout=5).get("request") or {}).get("status") or {}).get("name", "")
    except Exception as ex:
        log.warning("helpdesk status %s: %s", sdp_id, ex)
        st = hit[1] if hit else ""
    _status[sdp_id] = (time.time(), st)
    return st


@router.get("/api/helpdesk/requests/mine")
def mine(user: User = Depends(current_user)):
    with pool.connection() as c:
        rows = c.execute("SELECT id, category, urgency, subject, sdp_id, sent_by, created_at FROM helpdesk_requests "
                         "WHERE username=%s ORDER BY created_at DESC LIMIT 20", (user.username,)).fetchall()
    out = []
    for i, r in enumerate(rows):
        d = dict(r, created_at=r["created_at"].isoformat(timespec="minutes"), url=_link(r["sdp_id"]))
        d["status"] = _live_status(r["sdp_id"]) if r["sdp_id"] and _key() and i < 10 else ""
        out.append(d)
    return out
