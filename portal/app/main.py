"""Company Intranet: home, HR news (with editor panel) and the AD address book (replaces ab.example.com).

Auth: the browser signs in with Keycloak (keycloak-js, client `intranet`) and sends the access token as a Bearer
header. The API checks the signature (JWKS), issuer and authorised party. Authorisation comes from AD groups only
(Keycloak passes the user's AD groups in the `groups` claim): editors = AD group `Intranet-HR-Editors`.
"""
import hashlib
import io
import logging
import os
import re
import time
import uuid
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

import requests
from fastapi import Depends, FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from requests_ntlm import HttpNtlmAuth
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from . import analytics, audit, certs, helpcenter, helpdesk, hrpeople, hse, passkeyalerts, profile, push, threecx
from . import digest as digest_cfg
from .cloud_docs import CLOUD, ROOT, Docs
from .core import (MAIL_LOGO, UPLOADS, User, current_user, directory, editor, plain, pool, run_schema, sanitize,
                   summary_of)
from .digest import Digest
from . import rooms as ews
from . import roomops
from .rooms import Rooms
from .weather import Weather

STATIC = os.path.join(os.path.dirname(__file__), "static")
PHONE_URL = os.environ.get("PHONE_URL", "https://company.3cx.example:5001/")      # 3CX web client

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
  id          serial PRIMARY KEY,
  title       text NOT NULL,
  summary     text NOT NULL DEFAULT '',
  body_md     text NOT NULL DEFAULT '',
  body_html   text NOT NULL DEFAULT '',
  cover       text,
  pinned      boolean NOT NULL DEFAULT false,
  published   boolean NOT NULL DEFAULT false,
  published_at timestamptz,
  created_by  text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_by  text,
  updated_at  timestamptz
);
CREATE INDEX IF NOT EXISTS news_feed ON news (published, pinned DESC, published_at DESC);
-- languages: title/summary/body_html are the main version (lang); i18n = {"ru": {title, summary, body_html}, ...}
ALTER TABLE news ADD COLUMN IF NOT EXISTS lang text NOT NULL DEFAULT 'en';
ALTER TABLE news ADD COLUMN IF NOT EXISTS i18n jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE news ADD COLUMN IF NOT EXISTS layout text NOT NULL DEFAULT 'large';     -- card size: large / medium / small
ALTER TABLE news ADD COLUMN IF NOT EXISTS emailed_at timestamptz;                       -- last "E-mail to all staff"
ALTER TABLE news ADD COLUMN IF NOT EXISTS attachments jsonb NOT NULL DEFAULT '[]'::jsonb;  -- [{id, name, size}], files in UPLOADS/newsfiles
CREATE TABLE IF NOT EXISTS banner (
  id          int PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  text        text NOT NULL DEFAULT '',
  level       text NOT NULL DEFAULT 'info',
  active      boolean NOT NULL DEFAULT false,
  until       timestamptz,
  updated_by  text,
  updated_at  timestamptz
);
CREATE TABLE IF NOT EXISTS birthdays (            -- keyed by AD objectGUID; year optional (HR only, never shown to staff)
  person_id   text PRIMARY KEY,
  month       int NOT NULL CHECK (month BETWEEN 1 AND 12),
  day         int NOT NULL CHECK (day BETWEEN 1 AND 31),
  updated_by  text,
  updated_at  timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE birthdays ADD COLUMN IF NOT EXISTS year int CHECK (year BETWEEN 1930 AND 2015);
ALTER TABLE birthdays DROP CONSTRAINT IF EXISTS birthdays_year_check;
ALTER TABLE birthdays ADD CONSTRAINT birthdays_year_check CHECK (year >= 1930);
CREATE TABLE IF NOT EXISTS room_bookings (        -- bookings made from the intranet (organizer = booker; NULL = old intranet@ ones)
  id          serial PRIMARY KEY,
  item_id     text NOT NULL,
  room        text NOT NULL,
  starts      timestamp NOT NULL,                 -- Asia/Baku local time
  ends        timestamp NOT NULL,
  subject     text NOT NULL,
  username    text NOT NULL,
  email       text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE room_bookings ADD COLUMN IF NOT EXISTS organizer text;
ALTER TABLE room_bookings ADD COLUMN IF NOT EXISTS series text;                      -- same value = one repeating booking
ALTER TABLE room_bookings ADD COLUMN IF NOT EXISTS checked_in_at timestamptz;
ALTER TABLE room_bookings ADD COLUMN IF NOT EXISTS released_at timestamptz;          -- nobody checked in, room given back
CREATE TABLE IF NOT EXISTS digest_log (           -- weekly e-mail, one row per ISO week
  week        text PRIMARY KEY,
  status      text NOT NULL,
  items       int NOT NULL DEFAULT 0,
  sent_at     timestamptz NOT NULL DEFAULT now(),
  error       text
);
"""
run_schema(SCHEMA)

directory.start()
docs, rooms, weather = Docs(), Rooms(), Weather()
digest = Digest(pool)
digest.start()

log = logging.getLogger("portal")
app = FastAPI(title="Company Intranet", docs_url=None, redoc_url=None, openapi_url=None)
for _r in (roomops.router, hse.router, certs.router, helpcenter.router, profile.router, hrpeople.router, analytics.router, push.router, threecx.router, helpdesk.router, audit.router):
    app.include_router(_r)
certs.start()
hse.start()
threecx.start()
passkeyalerts.start()
audit.start()
roomops.start(rooms)

# ---------- news ----------
# Body = HTML from the WYSIWYG editor (TinyMCE), sanitised in core.sanitize.


class NewsLang(BaseModel):
    title: str = Field(default="", max_length=200)
    summary: str = Field(default="", max_length=500)
    body_html: str = Field(default="", max_length=500_000)


class NewsFile(BaseModel):
    id: str = Field(pattern=r"^[0-9a-f]{32}\.[a-z0-9]{2,5}$")
    name: str = Field(min_length=1, max_length=200)
    size: int = 0


class NewsIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    summary: str = Field(default="", max_length=500)       # empty → first sentences of the text
    body_html: str = Field(default="", max_length=500_000)
    cover: str | None = Field(default=None, max_length=200)
    pinned: bool = False
    published: bool = False
    lang: str = Field(default="en", pattern="^(en|ru|az)$")                 # language of the main version above
    i18n: dict[str, NewsLang] = Field(default_factory=dict)                  # other languages (optional)
    layout: str = Field(default="large", pattern="^(large|medium|small)$")
    email: bool = False                                                       # also e-mail it to all staff (published only)
    news_date: date | None = None                                             # news date (e.g. an older HR e-mail); empty → publish day
    attachments: list[NewsFile] = Field(default_factory=list, max_length=10)


def _public(row):
    row = dict(row)
    row.pop("body_md", None)                              # legacy Markdown source (pre-WYSIWYG), unused
    for k in ("published_at", "created_at", "updated_at", "emailed_at"):
        if row.get(k):
            row[k] = row[k].isoformat()
    return row


@app.get("/api/news")
def list_news(limit: int = 20, offset: int = 0, drafts: bool = False, user: User = Depends(current_user)):
    limit = max(1, min(limit, 50))
    show_drafts = False
    if drafts:
        show_drafts = user.editor
    with pool.connection() as c:
        rows = c.execute(
            "SELECT id, title, summary, cover, pinned, published, published_at, created_by, updated_at, lang, layout, emailed_at, attachments, body_html, "
            "(SELECT coalesce(jsonb_object_agg(k, v - 'body_html'), '{}'::jsonb) FROM jsonb_each(i18n) AS x(k, v)) AS i18n FROM news "
            + ("" if show_drafts else "WHERE published ")
            + "ORDER BY pinned DESC, coalesce(published_at, created_at) DESC LIMIT %s OFFSET %s",
            (limit, offset)).fetchall()
    out = []
    for r in rows:
        r = _public(r)
        # colleagues the post introduces: photo collage when there is no cover, and names for the search
        r["people"] = [{"id": p["id"], "name": p["name"]} for p in news_people(r.pop("body_html"))]
        out.append(r)
    return out


# Person cards in a post: <h3><a href="/directory/ID">Name</a></h3><p><strong>Role</strong>, …</p>.
# The <h2> above them says whether they are new or changed roles ("Role changes", "Vəzifə …", "Назначение" …).
_H23 = re.compile(r"<(h2|h3)[^>]*>(.*?)</\1>\s*(<p[^>]*>.*?</p>)?", re.S | re.I)
_ROLE_H2 = re.compile(r"role|position|appoint|promot|vəzifə|təyin|назнач|должност|перевод", re.I)


def news_people(html):
    kind, seen, out = "new", set(), []
    for m in _H23.finditer(html or ""):
        if m.group(1).lower() == "h2":
            kind = "role" if _ROLE_H2.search(plain(m.group(2))) else "new"
            continue
        a = re.fullmatch(r'\s*<a [^>]*href="/directory(?:/([0-9a-f-]{36}))?[^"]*"[^>]*>(.*?)</a>\s*', m.group(2), re.S)
        if not a:
            continue
        name = plain(a.group(2)).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        para = m.group(3) or ""
        strong = re.search(r"<strong>(.*?)</strong>", para, re.S)
        role = plain(strong.group(1) if strong else para).strip().rstrip(".,")
        out.append({"id": a.group(1) or "", "name": name, "role": role[:120], "kind": kind})
    return out


@app.get("/api/news/people")
def news_people_recent(lang: str = "en", days: int = 60, user: User = Depends(current_user)):
    """New colleagues and role changes from posts of the last `days` days, newest first, in the reader's language."""
    with pool.connection() as c:
        rows = c.execute("SELECT id, lang, body_html, i18n, published_at FROM news WHERE published AND published_at > now() - make_interval(days => %s) "
                         "ORDER BY published_at DESC", (max(1, min(days, 365)),)).fetchall()
    out, seen = [], set()
    for r in rows:
        body = r["body_html"] if r["lang"] == lang else ((r["i18n"] or {}).get(lang) or {}).get("body_html") or r["body_html"]
        for p in news_people(body):
            key = p["id"] or p["name"]
            if key not in seen:
                seen.add(key)
                out.append({**p, "post": r["id"], "date": r["published_at"].isoformat()})
    return out


@app.get("/api/news/{nid}")
def get_news(nid: int, user: User = Depends(current_user)):
    with pool.connection() as c:
        row = c.execute("SELECT * FROM news WHERE id=%s", (nid,)).fetchone()
    if not row:
        raise HTTPException(404)
    if not row["published"] and not user.editor:
        raise HTTPException(404)
    return _public(row)


def _prepare(n: NewsIn):
    html = sanitize(n.body_html)
    if not plain(html) and "<img" not in html:
        raise HTTPException(422, "text is empty")
    cover = _cover(n.cover)
    if not cover:                                         # no cover chosen → first picture in the text
        m = re.search(r'<img[^>]+src="(/uploads/[0-9a-f]{32}\.jpg)"', html)
        cover = m.group(1) if m else None
    other = {}
    for lg, v in n.i18n.items():                          # translations: kept only when they have a title and text
        if lg in ("en", "ru", "az") and lg != n.lang:
            b = sanitize(v.body_html)
            if v.title.strip() and (plain(b) or "<img" in b):
                other[lg] = {"title": v.title.strip(), "summary": v.summary.strip() or summary_of(b), "body_html": b}
    files = []
    for a in n.attachments:
        if not os.path.exists(os.path.join(NEWS_FILES, a.id)):
            raise HTTPException(422, f"attachment {a.name} is missing - upload it again")
        files.append({"id": a.id, "name": a.name, "size": os.path.getsize(os.path.join(NEWS_FILES, a.id))})
    if sum(f["size"] for f in files) > MAIL_MAX:
        raise HTTPException(422, "attachments: max 20 MB in total (they are sent by e-mail)")
    return html, n.summary.strip() or summary_of(html), cover, Jsonb(other), Jsonb(files)


@app.post("/api/news", status_code=201)
def create_news(n: NewsIn, user: User = Depends(editor)):
    html, summary, cover, other, files = _prepare(n)
    when = _news_date(n)
    with pool.connection() as c:
        row = c.execute(
            "INSERT INTO news (title, summary, body_html, cover, pinned, published, published_at, created_by, lang, i18n, layout, attachments) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (n.title, summary, html, cover, n.pinned, n.published,
             (when or datetime.now(timezone.utc)) if n.published else None, user.username, n.lang, other, n.layout, files)).fetchone()
    if n.published:
        push.notify_all(n.title, summary, f"/news/{row['id']}")
    return {"id": row["id"], **_email_all(row["id"], n)}


@app.put("/api/news/{nid}")
def update_news(nid: int, n: NewsIn, user: User = Depends(editor)):
    html, summary, cover, other, files = _prepare(n)
    when = _news_date(n)
    with pool.connection() as c:
        was = c.execute("SELECT published FROM news WHERE id=%s", (nid,)).fetchone()
        row = c.execute(
            "UPDATE news SET title=%s, summary=%s, body_md='', body_html=%s, cover=%s, pinned=%s, published=%s, "
            # a new date replaces the stored one; the same day keeps the original time
            # unpublishing keeps the date, so publishing again does not move the post to today
            "published_at = CASE WHEN NOT %s THEN published_at "
            "WHEN %s::timestamptz IS NOT NULL AND (published_at IS NULL OR (published_at AT TIME ZONE 'Asia/Baku')::date <> %s::date) THEN %s::timestamptz "
            "WHEN published_at IS NULL THEN now() ELSE published_at END, "
            "lang=%s, i18n=%s, layout=%s, attachments=%s, updated_by=%s, updated_at=now() WHERE id=%s RETURNING id",
            (n.title, summary, html, cover, n.pinned, n.published,
             n.published, when, n.news_date, when, n.lang, other, n.layout, files, user.username, nid)).fetchone()
    if not row:
        raise HTTPException(404)
    if n.published and was and not was["published"]:
        push.notify_all(n.title, summary, f"/news/{nid}")
    return {"id": nid, **_email_all(nid, n)}


def _news_date(n: NewsIn):
    """The chosen news date at 09:00 Baku time (today = now); no future dates - there is no scheduling."""
    if not n.news_date:
        return None
    today = datetime.now(timezone(timedelta(hours=4))).date()
    if n.news_date > today:
        raise HTTPException(422, "The news date cannot be in the future")
    d = n.news_date
    return datetime.now(timezone.utc) if d == today else datetime(d.year, d.month, d.day, 9, tzinfo=timezone(timedelta(hours=4)))


def _email_all(nid, n: NewsIn):
    """The editor ticked "E-mail to all staff": send the saved post to DIGEST_TO (allstaff@) from hrnews@."""
    if not (n.email and n.published):
        return {}
    if not digest.configured:
        return {"mail_error": "mail account not configured"}
    with pool.connection() as c:
        row = c.execute("SELECT * FROM news WHERE id=%s", (nid,)).fetchone()
    try:
        digest_cfg.send_post(row, files=news_files(row))
    except Exception as e:
        return {"mail_error": str(e)[:300]}
    with pool.connection() as c:
        c.execute("UPDATE news SET emailed_at=now() WHERE id=%s", (nid,))
    return {"emailed": digest_cfg.TO}


# ---- attachments: Office/PDF/text/images, signed-in staff only (never under the public /uploads/ URL) ----
NEWS_FILES = os.path.join(UPLOADS, "newsfiles")
FILE_TYPES = {"pdf": "application/pdf", "doc": "application/msword", "xls": "application/vnd.ms-excel",
              "ppt": "application/vnd.ms-powerpoint", "txt": "text/plain", "csv": "text/csv", "jpg": "image/jpeg",
              "jpeg": "image/jpeg", "png": "image/png",
              "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}
MAGIC = {"pdf": (b"%PDF-",), "doc": (b"\xd0\xcf\x11\xe0",), "xls": (b"\xd0\xcf\x11\xe0",), "ppt": (b"\xd0\xcf\x11\xe0",),
         "docx": (b"PK\x03\x04",), "xlsx": (b"PK\x03\x04",), "pptx": (b"PK\x03\x04",), "png": (b"\x89PNG",),
         "jpg": (b"\xff\xd8",), "jpeg": (b"\xff\xd8",)}
MAIL_MAX = 20 * 1024 * 1024


@app.post("/api/news/files", status_code=201)
async def news_file_upload(file: UploadFile = File(...), user: User = Depends(editor)):
    name = os.path.basename(file.filename or "file").strip()[:200] or "file"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in FILE_TYPES:
        raise HTTPException(422, "allowed: PDF, Word, Excel, PowerPoint, text, CSV, JPG, PNG")
    data = await file.read(15 * 1024 * 1024 + 1)
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "max 15 MB per file")
    if ext in MAGIC and not data.startswith(MAGIC[ext]):
        raise HTTPException(422, "the file content does not match its type")
    os.makedirs(NEWS_FILES, exist_ok=True)
    fid = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(NEWS_FILES, fid), "wb") as f:
        f.write(data)
    return {"id": fid, "name": name, "size": len(data)}


@app.get("/api/news/{nid}/files/{fid}")
def news_file(nid: int, fid: str, request: Request, user: User = Depends(current_user)):
    with pool.connection() as c:
        row = c.execute("SELECT published, attachments FROM news WHERE id=%s", (nid,)).fetchone()
    att = next((a for a in (row["attachments"] if row else []) if a["id"] == fid), None)
    if not att or (not row["published"] and not user.editor):
        raise HTTPException(404)
    path = os.path.join(NEWS_FILES, fid)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path, media_type=FILE_TYPES[fid.rsplit(".", 1)[1]], filename=att["name"])


def news_files(row):
    """(name, bytes, content type) of a post's attachments, for the e-mail."""
    out = []
    for a in row.get("attachments") or []:
        path = os.path.join(NEWS_FILES, a["id"])
        if os.path.exists(path):
            with open(path, "rb") as f:
                out.append((a["name"], f.read(), FILE_TYPES[a["id"].rsplit(".", 1)[1]]))
    return out


@app.post("/api/news/{nid}/mail-test")
def news_mail_test(nid: int, user: User = Depends(editor)):
    """The saved version, as all staff would get it, to the editor only."""
    if not digest.configured:
        raise HTTPException(503, "mail account not configured")
    if not user.email:
        raise HTTPException(422, "your account has no e-mail")
    with pool.connection() as c:
        row = c.execute("SELECT * FROM news WHERE id=%s", (nid,)).fetchone()
    if not row:
        raise HTTPException(404)
    try:
        digest_cfg.send_post(row, user.email, files=news_files(row))
    except Exception as e:
        log.error("mail: %s", e)                             # the reason stays in the log, not in the answer
        raise HTTPException(502, "send failed")
    return {"sent_to": user.email}


@app.delete("/api/news/{nid}", status_code=204)
def delete_news(nid: int, user: User = Depends(editor)):
    with pool.connection() as c:
        c.execute("DELETE FROM news WHERE id=%s", (nid,))
    return Response(status_code=204)


def _cover(path):
    if not path:
        return None
    if not path.startswith("/uploads/") or "/" in path[len("/uploads/"):] or ".." in path:
        raise HTTPException(422, "cover must be an uploaded image")
    return path


@app.post("/api/uploads", status_code=201)
async def upload(file: UploadFile = File(...), user: User = Depends(editor)):
    data = await file.read(15 * 1024 * 1024 + 1)
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "max 15 MB")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        raise HTTPException(422, "not an image")
    img = img.convert("RGB")               # drops EXIF/GPS metadata as well
    img.thumbnail((1600, 1600))
    name = f"{uuid.uuid4().hex}.jpg"
    img.save(os.path.join(UPLOADS, name), "JPEG", quality=85, optimize=True)
    return {"url": f"/uploads/{name}"}


@app.get("/uploads/{name}")
def get_upload(name: str):
    if "/" in name or ".." in name or not name.endswith(".jpg"):
        raise HTTPException(404)
    path = os.path.join(UPLOADS, name)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=31536000, immutable"})


# ---------- directory (address book) ----------
@app.get("/api/directory")
def dir_list(user: User = Depends(current_user)):
    return {"updated": directory.updated, "people": directory.people(), "departments": directory.departments(),
            "offices": directory.offices()}


@app.get("/api/directory/{pid}")
def dir_person(pid: str, user: User = Depends(current_user)):
    p = directory.person(pid)
    if not p:
        raise HTTPException(404)
    return p


_hr_photos = {}       # pid → (time, bytes|None): Exchange high-resolution photos, 12 h


def _hr_photo(pid):
    """Best photo: one uploaded in My profile (512 px) → Exchange (240 px, if the person has one) → AD thumbnail."""
    path = os.path.join(UPLOADS, "photos", f"{pid}.jpg") if re.fullmatch(r"[0-9a-f-]{32,36}", pid) else None
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    hit = _hr_photos.get(pid)
    if hit and time.time() - hit[0] < 43200:
        return hit[1]
    data = None
    p = directory.person(pid)
    if p and p.get("mail"):
        try:
            r = requests.get(ews.EWS.replace("Exchange.asmx", "Exchange.asmx/s/GetUserPhoto"), params={"email": p["mail"], "size": "HR240x240"},
                             auth=HttpNtlmAuth(ews.USER, ews._password()), timeout=10)
            if r.status_code == 200 and r.content[:2] == b"\xff\xd8" and len(r.content) > 2500:   # a real photo, not the 64 px stub
                data = r.content
        except Exception:
            data = None
    _hr_photos[pid] = (time.time(), data)
    return data


@app.get("/api/directory/{pid}/photo")
def dir_photo(pid: str, request: Request, user: User = Depends(current_user)):
    photo = _hr_photo(pid)
    etag = '"' + hashlib.sha1(photo).hexdigest()[:16] + '"' if photo else None
    if not photo:
        photo, etag = directory.photo(pid)
    if not photo:
        raise HTTPException(404)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)
    return Response(photo, media_type="image/jpeg", headers={"ETag": etag, "Cache-Control": "private, max-age=3600"})


# ---------- org chart ----------
@app.get("/api/org")
def org(user: User = Depends(current_user)):
    return directory.org()


# ---------- birthdays (entered by HR; year optional, for HR only - staff see day + month) ----------
def _bdays(year=False):
    with pool.connection() as c:
        rows = c.execute("SELECT person_id, month, day, year FROM birthdays").fetchall()
    return {r["person_id"]: ((r["month"], r["day"], r["year"]) if year else (r["month"], r["day"])) for r in rows}


@app.get("/api/birthdays")
def birthdays(days: int = 14, user: User = Depends(current_user)):
    today, people = date.today(), {p["id"]: p for p in directory.people()}
    out = []
    for pid, (m, d) in _bdays().items():
        p = people.get(pid)
        if not p:
            continue                                      # left the company / hidden from the GAL
        for y in (today.year, today.year + 1):
            try:
                when = date(y, m, d)
            except ValueError:                            # 29 Feb in a normal year
                when = date(y, 3, 1)
            if when >= today:
                break
        delta = (when - today).days
        if delta <= max(0, min(days, 60)):
            out.append({"id": pid, "name": p["name"], "title": p["title"], "department": p["department"],
                        "has_photo": p["has_photo"], "month": m, "day": d, "in_days": delta})
    return sorted(out, key=lambda x: (x["in_days"], x["name"].lower()))


@app.get("/api/admin/birthdays")
def birthdays_all(user: User = Depends(editor)):
    b = _bdays(year=True)
    return [{"id": p["id"], "name": p["name"], "department": p["department"], "username": p["username"],
             **dict(zip(("month", "day", "year"), b.get(p["id"], (None, None, None))))} for p in directory.people()]


class BirthdayIn(BaseModel):
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    year: int | None = Field(default=None, ge=1930)


def _set_bday(c, pid, month, day, who, year=None):
    if month is None or day is None:
        c.execute("DELETE FROM birthdays WHERE person_id=%s", (pid,))
        return
    date(year or 2024, month, day)                        # raises ValueError for 31.04, 29.02.1990 etc.
    if year is not None and not 1930 <= year <= date.today().year:
        raise ValueError("year")
    c.execute("INSERT INTO birthdays (person_id, month, day, year, updated_by) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (person_id) "
              "DO UPDATE SET month=EXCLUDED.month, day=EXCLUDED.day, year=EXCLUDED.year, updated_by=EXCLUDED.updated_by, updated_at=now()",
              (pid, month, day, year, who))


@app.put("/api/admin/birthdays/{pid}")
def birthday_set(pid: str, b: BirthdayIn, user: User = Depends(editor)):
    if not directory.person(pid):
        raise HTTPException(404)
    try:
        with pool.connection() as c:
            _set_bday(c, pid, b.month, b.day, user.username, b.year)
    except ValueError:
        raise HTTPException(422, "invalid date")
    return {"ok": True}


class BirthdayImport(BaseModel):
    text: str = Field(max_length=200_000)


_DATE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})|(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?")


@app.post("/api/admin/birthdays/import")
def birthday_import(b: BirthdayImport, user: User = Depends(editor)):
    """Lines copied from Excel: <username | e-mail | full name> <tab or ;> <date: dd.mm[.yyyy] or yyyy-mm-dd>."""
    done, missing, bad = 0, [], []
    with pool.connection() as c:
        for line in b.text.splitlines():
            if not line.strip():
                continue
            m = None
            for m in _DATE.finditer(line):
                pass                                      # the last date on the line
            if not m:
                bad.append(line.strip()[:80]); continue
            who = line[:m.start()].strip(" \t;,")
            y, mo, d = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(6), m.group(5), m.group(4))
            y = int(y) if y and len(y) == 4 else None     # 2-digit years are ambiguous: day and month only
            pid = directory.find(who) if who else None
            if not pid:
                missing.append(who[:80] or line.strip()[:80]); continue
            try:
                _set_bday(c, pid, int(mo), int(d), user.username, y); done += 1
            except ValueError:
                bad.append(line.strip()[:80])
    return {"saved": done, "not_found": missing, "invalid": bad}


# ---------- emergency banner ----------
class BannerIn(BaseModel):
    text: str = Field(default="", max_length=500)
    level: str = Field(default="info", pattern="^(info|warning|danger)$")
    active: bool = False
    until: datetime | None = None


@app.get("/api/banner")
def banner(user: User = Depends(current_user)):
    with pool.connection() as c:
        row = c.execute("SELECT text, level, active, until, updated_at FROM banner WHERE id=1").fetchone()
    if not row or not row["active"] or not row["text"] or (row["until"] and row["until"] < datetime.now(timezone.utc)):
        return {"active": False}
    return {"active": True, "text": row["text"], "level": row["level"],
            "until": row["until"].isoformat() if row["until"] else None, "id": row["updated_at"].isoformat()}


@app.get("/api/admin/banner")
def banner_get(user: User = Depends(editor)):
    with pool.connection() as c:
        row = c.execute("SELECT text, level, active, until FROM banner WHERE id=1").fetchone()
    row = dict(row) if row else {"text": "", "level": "info", "active": False, "until": None}
    row["until"] = row["until"].isoformat() if row["until"] else None
    return row


@app.put("/api/admin/banner")
def banner_set(b: BannerIn, user: User = Depends(editor)):
    with pool.connection() as c:
        old = c.execute("SELECT text, active FROM banner WHERE id=1").fetchone()
        c.execute("INSERT INTO banner (id, text, level, active, until, updated_by, updated_at) VALUES (1,%s,%s,%s,%s,%s,now()) "
                  "ON CONFLICT (id) DO UPDATE SET text=EXCLUDED.text, level=EXCLUDED.level, active=EXCLUDED.active, "
                  "until=EXCLUDED.until, updated_by=EXCLUDED.updated_by, updated_at=now()",
                  (b.text.strip(), b.level, b.active, b.until, user.username))
    if b.active and b.text.strip() and (not old or not old["active"] or old["text"] != b.text.strip()):
        push.notify_all({"danger": "⚠️ Company", "warning": "❗ Company"}.get(b.level, "Company"), b.text.strip(), "/", "banner")
    return {"ok": True}


# ---------- HR documents (Cloud folder) ----------
@app.get("/api/docs")
def docs_list(user: User = Depends(current_user)):
    if not docs.enabled:
        raise HTTPException(503, "document library not configured")
    try:
        return {"items": docs.tree(), "folder": docs_folder_url()}
    except Exception:
        raise HTTPException(502, "Cloud is not reachable")


def docs_folder_url():
    return f"{CLOUD}/apps/files/files?dir={quote('/' + ROOT)}"


@app.get("/api/docs/file")
def docs_file(path: str, download: bool = False, user: User = Depends(current_user)):
    try:
        r = docs.open(path)
    except ValueError:
        raise HTTPException(400)
    except FileNotFoundError:
        raise HTTPException(404)
    name = path.rsplit("/", 1)[-1]
    ctype = r.headers.get("content-type", "application/octet-stream")
    inline = not download and ctype.split(";")[0] in ("application/pdf", "image/jpeg", "image/png", "text/plain")
    headers = {"Content-Disposition": f"{'inline' if inline else 'attachment'}; filename*=UTF-8''{quote(name)}",
               "Cache-Control": "private, no-store"}
    if r.headers.get("content-length"):
        headers["Content-Length"] = r.headers["content-length"]
    return StreamingResponse(r.iter_content(65536), media_type=ctype, headers=headers)


# ---------- meeting rooms (Exchange free/busy) ----------
@app.get("/api/rooms")
def rooms_day(day: date | None = None, user: User = Depends(current_user)):
    if not rooms.enabled:
        return {"enabled": False, "rooms": rooms.names()}
    day = day or date.today()
    if abs((day - date.today()).days) > 60:
        raise HTTPException(422, "date out of range")
    try:
        data = rooms.day(day)
    except Exception:
        raise HTTPException(502, "Exchange is not reachable")
    # organizer of intranet bookings (from our own records) so colleagues know whom to talk to
    with pool.connection() as c:
        mine = c.execute("SELECT room, starts, ends, username FROM room_bookings WHERE starts::date=%s", (day,)).fetchall()
    who = {(b["room"], b["starts"].strftime("%Y-%m-%dT%H:%M"), b["ends"].strftime("%Y-%m-%dT%H:%M")): b["username"] for b in mine}
    by_name = {p["name"].lower(): p for p in directory.people()}
    out = []
    for r in data:
        evs = []
        try:                                             # Outlook bookings: organizer from the room calendar
            org = ews.organizers(r["mail"], day) if r["events"] else {}
        except Exception:
            org = {}
        for ev in r["events"]:
            u = who.get((r["mail"], ev["start"], ev["end"]))
            pid = directory.find(u) if u else None
            p = directory.person(pid) if pid else None
            if not p and (ev["start"], ev["end"]) in org:
                hit = by_name.get(org[(ev["start"], ev["end"])].lower())
                p = directory.person(hit["id"]) if hit else {"name": org[(ev["start"], ev["end"])]}
            evs.append({**ev, "organizer": {k: p.get(k) for k in ("id", "name", "title", "mail", "extension", "phone", "mobile", "username", "has_photo")} if p else None})
        out.append({**r, "events": evs})
    return {"enabled": True, "day": day.isoformat(), "rooms": out}


class BookingIn(BaseModel):
    room: str = Field(max_length=200)
    day: date
    start: str = Field(pattern=r"^\d{2}:\d{2}$")
    end: str = Field(pattern=r"^\d{2}:\d{2}$")
    subject: str = Field(min_length=2, max_length=120)
    attendees: list[str] = Field(default_factory=list, max_length=60)
    repeat: str = Field(default="none", pattern="^(none|weekly|biweekly|monthly)$")
    count: int = Field(default=1, ge=1, le=12)


def _series_days(day, repeat, count):
    """Dates of a repeating booking; monthly keeps the day of the month (the 31st falls on the last day of shorter months)."""
    if repeat == "none":
        return [day]
    if repeat in ("weekly", "biweekly"):
        return [day + timedelta(days=(7 if repeat == "weekly" else 14) * i) for i in range(count)]
    out = []
    for i in range(count):
        y, m = day.year + (day.month - 1 + i) // 12, (day.month - 1 + i) % 12 + 1
        out.append(date(y, m, min(day.day, monthrange(y, m)[1])))
    return out


def _booking_times(b: BookingIn, user: User):
    if not rooms.enabled:
        raise HTTPException(503, "rooms are not connected")
    if b.room not in {m for _, m in ews.ROOMS}:
        raise HTTPException(404, "unknown room")
    if not user.email:
        raise HTTPException(422, "your account has no e-mail")
    try:
        start = datetime.combine(b.day, datetime.strptime(b.start, "%H:%M").time())
        end = datetime.combine(b.day, datetime.strptime(b.end, "%H:%M").time())
    except ValueError:
        raise HTTPException(422, "invalid time")
    if end <= start or end - start > timedelta(hours=4) or start.hour < 7 or (end.hour, end.minute) > (21, 0):
        raise HTTPException(422, "bookings are 07:00–21:00, at most 4 hours")
    if start < datetime.now() - timedelta(minutes=5) or b.day > date.today() + timedelta(days=400 if b.repeat != "none" else 60):
        raise HTTPException(422, "pick a time from now up to 60 days ahead")
    # only colleagues from the directory (no outside addresses through the intranet); the booker is the organizer
    known = {p["mail"].lower() for p in directory.people() if p.get("mail")}
    people = []
    for a in b.attendees:
        a = a.strip().lower()
        if a and a != user.email.lower() and a not in people:
            if a not in known:
                raise HTTPException(422, f"not in the directory: {a}")
            people.append(a)
    return start, end, people


def _room_free(room, day, start, end, ignore=None):
    rooms.forget(day)
    busy = next((r for r in rooms.day(day) if r["mail"] == room), {"events": []})["events"]
    s1, e1 = start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")
    for ev in busy:
        if ignore and (ev["start"], ev["end"]) == ignore:   # the booking that is being changed
            continue
        if ev["start"] < e1 and ev["end"] > s1:
            raise HTTPException(409, "the room is busy at that time")


@app.post("/api/rooms/book", status_code=201)
def room_book(b: BookingIn, user: User = Depends(current_user)):
    days = _series_days(b.day, b.repeat, b.count)
    with pool.connection() as c:
        mine = c.execute("SELECT count(*) AS n FROM room_bookings WHERE username=%s AND ends > now() AND released_at IS NULL",
                         (user.username,)).fetchone()["n"]
    if len(days) == 1 and mine >= 10:
        raise HTTPException(429, "you already have 10 upcoming bookings")
    if mine + len(days) > 30:
        raise HTTPException(429, "at most 30 upcoming bookings, repeating ones included")
    series = uuid.uuid4().hex if len(days) > 1 else None
    booked, skipped = [], []
    for d in days:                                   # one meeting per date: each can be changed or cancelled on its own
        one = b.model_copy(update={"day": d})
        start, end, people = _booking_times(one, user)
        try:
            _room_free(b.room, d, start, end)
        except HTTPException:
            if not series:
                raise
            skipped.append(d.isoformat())
            continue
        try:
            item = ews.book(b.room, start, end, b.subject.strip(), user.email, people, roomops.invite_note())
        except Exception as e:
            if not booked:
                raise upstream(e)
            skipped.append(d.isoformat())
            continue
        with pool.connection() as c:
            row = c.execute("INSERT INTO room_bookings (item_id, room, starts, ends, subject, username, email, organizer, series) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                            (item, b.room, start, end, b.subject.strip(), user.username, user.email, user.email, series)).fetchone()
        booked.append(row["id"])
        rooms.forget(d)
    if not booked:
        raise HTTPException(409, "the room is busy at all of those times")
    return {"id": booked[0], "booked": len(booked), "skipped": skipped}


def _my_booking(c, bid, user):
    row = c.execute("SELECT * FROM room_bookings WHERE id=%s", (bid,)).fetchone()
    if not row or (row["username"] != user.username and not user.has("it")):
        raise HTTPException(404)
    return row


@app.get("/api/rooms/book/{bid}")
def room_booking(bid: int, user: User = Depends(current_user)):
    with pool.connection() as c:
        row = _my_booking(c, bid, user)
    try:
        people = ews.attendees_of(row["item_id"], row["organizer"])
    except Exception:
        people = []
    if not row["organizer"]:                     # old intranet@ booking: the booker was the attendee
        people = [p for p in people if p != row["email"].lower()]
    return {"id": row["id"], "room": row["room"], "day": row["starts"].date().isoformat(), "start": row["starts"].strftime("%H:%M"),
            "end": row["ends"].strftime("%H:%M"), "subject": row["subject"], "attendees": people,
            "editable": bool(row["organizer"])}


@app.put("/api/rooms/book/{bid}")
def room_change(bid: int, b: BookingIn, user: User = Depends(current_user)):
    with pool.connection() as c:
        row = _my_booking(c, bid, user)
    if not row["organizer"]:
        raise HTTPException(409, "this older booking cannot be changed — cancel it and book again")
    start, end, people = _booking_times(b, user if row["username"] == user.username else
                                        User(username=row["username"], name="", email=row["email"], groups=user.groups))
    old = (row["starts"].strftime("%Y-%m-%dT%H:%M"), row["ends"].strftime("%Y-%m-%dT%H:%M"))
    _room_free(b.room, b.day, start, end, ignore=old if b.room == row["room"] else None)
    try:
        ews.update(row["item_id"], row["organizer"], b.room, start, end, b.subject.strip(), people)
    except Exception as e:
        raise upstream(e)
    with pool.connection() as c:
        c.execute("UPDATE room_bookings SET room=%s, starts=%s, ends=%s, subject=%s WHERE id=%s",
                  (b.room, start, end, b.subject.strip(), bid))
    rooms.forget(row["starts"].date()); rooms.forget(b.day)
    return {"id": bid}


@app.get("/api/rooms/mine")
def room_mine(user: User = Depends(current_user)):
    with pool.connection() as c:
        rows = c.execute("SELECT id, room, starts, ends, subject, organizer, series, checked_in_at FROM room_bookings "
                         "WHERE username=%s AND ends > now() AND released_at IS NULL ORDER BY starts", (user.username,)).fetchall()
    names = {m: n for n, m in ews.ROOMS}
    return [{"id": r["id"], "room": r["room"], "subject": r["subject"], "editable": bool(r["organizer"]),
             "room_name": names.get(r["room"], r["room"]), "starts": r["starts"].isoformat(timespec="minutes"),
             "ends": r["ends"].isoformat(timespec="minutes"), "series": bool(r["series"]), "checked_in": bool(r["checked_in_at"]),
             "checkin_open": roomops.checkin_open(r)} for r in rows]


@app.delete("/api/rooms/book/{bid}", status_code=204)
def room_cancel(bid: int, series: bool = False, user: User = Depends(current_user)):
    with pool.connection() as c:
        row = _my_booking(c, bid, user)
        todo = [row]
        if series and row["series"]:                 # this one and the later dates
            todo = c.execute("SELECT * FROM room_bookings WHERE series=%s AND starts >= %s AND released_at IS NULL ORDER BY starts",
                             (row["series"], row["starts"])).fetchall()
        for r in todo:
            try:
                ews.cancel(r["item_id"], r["organizer"])
            except Exception as e:
                raise upstream(e)
            c.execute("DELETE FROM room_bookings WHERE id=%s", (r["id"],))
            rooms.forget(r["starts"].date())
    return Response(status_code=204)


# ---------- weather ----------
@app.get("/api/weather")
def weather_now(user: User = Depends(current_user)):
    return weather.get()


# ---------- weekly e-mail ----------
@app.get("/api/admin/digest")
def digest_status(user: User = Depends(editor)):
    items, html = digest.preview()
    with pool.connection() as c:
        sent = c.execute("SELECT week, status, items, sent_at, error FROM digest_log ORDER BY sent_at DESC LIMIT 8").fetchall()
    return {"enabled": digest.is_on() and digest.configured, "on": digest.is_on(), "configured": digest.configured,
            "to": digest_cfg.TO, "from": digest_cfg.FROM,
            "weekday": digest_cfg.WEEKDAY, "hour": digest_cfg.HOUR,
            "items": len(items), "html": re.sub(r"cid:([0-9a-f]{32})@company\.az", r"/uploads/\1.jpg", html).replace(MAIL_LOGO, "/logo.png"),   # preview in the browser (the page only loads its own images)
            "log": [{**r, "sent_at": r["sent_at"].isoformat()} for r in sent]}


class DigestOn(BaseModel):
    on: bool


@app.put("/api/admin/digest")
def digest_switch(d: DigestOn, user: User = Depends(editor)):
    digest.set_on(d.on)
    return {"on": d.on}


@app.post("/api/admin/digest/test")
def digest_test(user: User = Depends(editor)):
    if not digest.configured:
        raise HTTPException(503, "mail account not configured")
    items, _ = digest.preview()
    if not items:
        raise HTTPException(422, "no news since the last weekly e-mail")
    to = user.email
    if not to:
        raise HTTPException(422, "your account has no e-mail")
    try:
        digest.send(to, items)
    except Exception as e:
        log.error("mail: %s", e)                             # the reason stays in the log, not in the answer
        raise HTTPException(502, "send failed")
    return {"sent_to": to, "items": len(items)}


# ---------- misc ----------
@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"username": user.username, "name": user.name, "email": user.email, "editor": user.editor,
            "roles": {k: user.has(k) for k in ("news", "hse", "it")},
            "features": {"docs": docs.enabled, "rooms": rooms.enabled, "rooms_list": rooms.names(), "phone": PHONE_URL,
                         "pbx": threecx.pbx.enabled, "profile": bool(profile.secret("AD_WRITE_PASSWORD", ""))}}


@app.get("/healthz")
def healthz():
    return {"ok": True}                                  # container health check; nothing about the data


def upstream(e):
    """Exchange refused or did not answer: the reason goes to the log, staff see a plain message."""
    log.error("Exchange: %s", e)
    if "no impersonation right" in str(e):               # the one reason staff can act on (ask IT for booking access)
        return HTTPException(502, f"Exchange: {e}")
    return HTTPException(502, "Exchange: the mail server did not accept the request, try again")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # audit log: editor routes only (audit.RULES); the body is read before the route so the changed fields can be noted
    audited = request.method in ("POST", "PUT", "DELETE") and audit.match(request.method, request.url.path)
    body = b""
    if audited and request.headers.get("content-type", "").startswith("application/json") \
            and int(request.headers.get("content-length") or 0) <= 600_000:
        body = await request.body()
    resp = await call_next(request)
    if audited and resp.status_code < 400:
        user = getattr(request.state, "user", None)
        ip = request.headers.get("x-real-ip") or (request.client.host if request.client else "")
        await run_in_threadpool(audit.record, user, request.method, request.url.path, body, ip)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
        "connect-src 'self' https://sso.example.com; frame-src 'self' https://sso.example.com; frame-ancestors 'self'; "
        "base-uri 'self'; form-action 'self' https://sso.example.com")
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    elif request.url.path.startswith("/assets/"):            # built frontend: file names change with every build
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.url.path.startswith("/vendor/"):
        resp.headers.setdefault("Cache-Control", "public, max-age=604800")
    elif "Cache-Control" not in resp.headers:
        # app shell (html / js / css): always revalidate (ETag → 304) so a deploy reaches everyone on the next click
        resp.headers["Cache-Control"] = "no-cache"
    return resp


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")


@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    # client-side routes (/news/3, /directory, /admin) → index.html; API/assets keep the 404
    if request.url.path.startswith(("/api/", "/uploads/", "/vendor/")) or "." in request.url.path.rsplit("/", 1)[-1]:
        return JSONResponse({"detail": getattr(exc, "detail", "not found")}, status_code=404)
    return FileResponse(os.path.join(STATIC, "index.html"))
