"""Shared pieces: config, DB pool, Keycloak token check + AD-group roles, HTML sanitiser, directory, mail."""
import html as htmllib
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

import jwt
import nh3
from fastapi import Depends, HTTPException, Request
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from .directory import Directory

ISSUER = os.environ.get("OIDC_ISSUER", "https://sso.example.com/realms/company")
CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "intranet")
UPLOADS = os.environ.get("UPLOAD_DIR", "/data/uploads")
SITE = os.environ.get("SITE_URL", "https://intranet.example.com")
CA = os.environ.get("LDAP_CA", "/etc/ssl/company-ca.pem")

# Intranet-News-Editors was renamed Intranet-HR-Editors (2026-11-03); the old name is still accepted until
# Keycloak has synced the rename and everyone has logged in again - then drop OLD_HR_GROUP.
OLD_HR_GROUP = "Intranet-News-Editors"
# Authorisation = AD security groups (Keycloak passes them in the `groups` claim). Never Keycloak-only roles.
GROUPS = {
    "news": os.environ.get("EDITOR_GROUP", "Intranet-HR-Editors"),     # HR: news, birthdays, banner, e-mail, people
    "hse": os.environ.get("HSE_GROUP", "Intranet-HSE-Editors"),        # HSE board, reports, certificates
    "it": os.environ.get("IT_GROUP", "Intranet-IT-Editors"),           # IT: help centre, analytics + every role above
}


def secret(name, default=None):
    path = os.environ.get(f"{name}_FILE")
    if path and os.path.exists(path):
        return open(path).read().strip()
    if name in os.environ:
        return os.environ[name]
    if default is not None:
        return default
    raise KeyError(name)


pool = ConnectionPool(
    f"host={os.environ.get('DB_HOST', 'db.example.com')} dbname=portal user=portal "
    f"password={secret('DB_PASSWORD')} sslmode=prefer connect_timeout=10",
    min_size=1, max_size=6, kwargs={"row_factory": dict_row}, open=True)


def run_schema(sql):
    with pool.connection() as c:
        c.execute("SELECT pg_advisory_lock(4242)")       # both replicas start together
        try:
            c.execute(sql)
        finally:
            c.execute("SELECT pg_advisory_unlock(4242)")


directory = Directory(password=secret("LDAP_PASSWORD"))

# ---------- auth ----------
_jwks = jwt.PyJWKClient(f"{ISSUER}/protocol/openid-connect/certs", cache_keys=True, lifespan=3600)


class User(BaseModel):
    username: str
    name: str
    email: str = ""
    groups: list[str]

    def has(self, role):
        # IT (Intranet-IT-Editors) administers the whole intranet; HR and HSE get only their own sections
        names = {GROUPS[role], GROUPS["it"]} | ({OLD_HR_GROUP} if role == "news" else set())
        return any(g in self.groups for g in names)

    @property
    def editor(self):
        return self.has("news")


def current_user(request: Request) -> User:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "login required")
    try:
        token = auth[7:]
        key = _jwks.get_signing_key_from_jwt(token).key
        # leeway: the Swarm nodes' clocks differ by a fraction of a second, so a token just issued by Keycloak on
        # another node could look "issued in the future" and fail at random
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=ISSUER, options={"verify_aud": False}, leeway=30)
    except Exception:
        raise HTTPException(401, "invalid token")
    if claims.get("azp") != CLIENT_ID:
        raise HTTPException(401, "wrong client")
    user = User(username=claims.get("preferred_username", ""), name=claims.get("name", ""),
                email=(claims.get("email") or "").lower(), groups=claims.get("groups", []))
    request.state.user = user                            # for the audit log (main.py middleware)
    return user


def optional_user(request: Request):
    try:
        return current_user(request) if request.headers.get("authorization") else None
    except HTTPException:
        return None


def role(name):
    def dep(user: User = Depends(current_user)) -> User:
        if not user.has(name):
            raise HTTPException(403, f"AD group {GROUPS[name]} required")
        return user
    return dep


editor = role("news")


def me_person(user: User):
    """The signed-in user's directory entry (objectGUID id) or None."""
    pid = directory.find(user.username) or (directory.find(user.email) if user.email else None)
    return directory.person(pid) if pid else None


# ---------- HTML from the WYSIWYG editor ----------
ALLOWED_TAGS = {"p", "br", "strong", "em", "b", "i", "u", "s", "span", "sub", "sup", "a", "ul", "ol", "li", "h2", "h3",
                "h4", "blockquote", "img", "hr", "table", "caption", "colgroup", "col", "thead", "tbody", "tfoot", "tr",
                "th", "td", "figure", "figcaption", "code", "pre"}
# no "color" / "background-color": hard-coded text colours clash with the dark theme
STYLES = {"text-align", "text-decoration", "padding-left", "margin-left", "list-style-type",
          "width", "height", "border", "border-collapse", "border-color", "border-style", "border-width",
          "vertical-align", "float", "margin", "margin-right"}
_NO_SRC = re.compile(r"<img(?![^>]*\bsrc=)[^>]*>")             # images whose source was removed


def _attr(tag, attr, value):
    if tag == "img" and attr == "src" and not value.startswith("/uploads/"):
        return None
    return value


def sanitize(html: str) -> str:
    return _NO_SRC.sub("", nh3.clean(
        html, tags=ALLOWED_TAGS, attribute_filter=_attr, filter_style_properties=STYLES,
        attributes={"*": {"style"}, "a": {"href", "title", "target"}, "img": {"src", "alt", "width", "height"},
                    "th": {"colspan", "rowspan", "scope"}, "td": {"colspan", "rowspan"}, "col": {"span"}, "ol": {"start"}},
        url_schemes={"https", "mailto", "tel"}, link_rel="noopener noreferrer"))


def plain(html: str) -> str:
    return " ".join(htmllib.unescape(nh3.clean(html.replace("<", " <"), tags=set())).split())


def summary_of(html: str, n=220) -> str:
    text = plain(html)
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


# ---------- mail (Exchange SMTP 587 as svc-intranet) ----------
SMTP_HOST = os.environ.get("SMTP_HOST", "mail.example.com")
SMTP_USER = os.environ.get("SMTP_USER", "svc-intranet@example.com")
MAIL_FROM = os.environ.get("MAIL_FROM", "intranet@example.com")
# e-mail logo: the templates point at the public website copy; send_mail swaps it for the brand logo inside the e-mail
# (static/logo.png, from branding/), so it shows anywhere without "download pictures"; the URL stays as the fallback
MAIL_LOGO = os.environ.get("MAIL_LOGO", "https://www.example.com/uploads/2023/06/company-logo-web.png")
_logo = []


def _mail_logo():
    if not _logo:
        try:
            import io
            from PIL import Image
            with Image.open(os.path.join(os.path.dirname(__file__), "static", "logo.png")) as im:
                im.thumbnail((400, 96))
                buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
            _logo.append(buf.getvalue())
        except Exception:
            _logo.append(None)
    return _logo[0]


def mail_configured():
    return bool(secret("SVC_PASSWORD", ""))


def send_mail(to, subject, html, text="", sender=None, sender_name="Company Intranet", attachments=(), inline=(),
              reply_to=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender or MAIL_FROM))
    msg["To"] = ", ".join(to) if isinstance(to, (list, tuple)) else to
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["Message-ID"] = make_msgid(domain="example.com")
    logo = _mail_logo() if f'src="{MAIL_LOGO}"' in html else None
    if logo:
        html = html.replace(f'src="{MAIL_LOGO}"', 'src="cid:logo@example.com"')
    msg.set_content(text or plain(html))
    msg.add_alternative(html, subtype="html")
    html_part = msg.get_payload()[-1]
    if logo:
        html_part.add_related(logo, maintype="image", subtype="png", cid="<logo@example.com>", disposition="inline")
    for cid, data in inline:                                # pictures shown inside the text: <img src="cid:...">
        html_part.add_related(data, maintype="image", subtype="jpeg", cid=f"<{cid}>", disposition="inline")
    for name, data, ctype in attachments:                  # (file name, bytes, "type/subtype")
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)
    ctx = ssl.create_default_context()
    if os.path.exists(CA):
        ctx.load_verify_locations(CA)
    with smtplib.SMTP(SMTP_HOST, 587, timeout=30) as s:
        s.starttls(context=ctx)
        s.login(SMTP_USER, secret("SVC_PASSWORD"))
        s.send_message(msg)


def mail_frame(title, body_html):
    """Branded e-mail wrapper (tables + inline styles for Outlook)."""
    return f"""<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#EEF2F7">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF2F7"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border:1px solid #DCE3EE">
<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td height="6" style="background:#3FA34D;font-size:0">&nbsp;</td>
<td height="6" style="background:#2E6DB4;font-size:0">&nbsp;</td><td height="6" style="background:#D2262F;font-size:0">&nbsp;</td></tr></table></td></tr>
<tr><td style="padding:18px 22px;border-bottom:1px solid #DCE3EE"><img src="{MAIL_LOGO}" height="34" alt="Company" style="display:block;border:0"></td></tr>
<tr><td style="padding:22px;font-family:Segoe UI,Arial,sans-serif;font-size:15px;line-height:1.55;color:#1F2937">
<div style="font-size:20px;font-weight:700;color:#1B2B5B;margin-bottom:12px">{htmllib.escape(title)}</div>{body_html}</td></tr>
<tr><td style="padding:14px 22px;font-family:Segoe UI,Arial,sans-serif;font-size:12px;color:#6B7280;border-top:1px solid #DCE3EE">
Company Intranet · <a href="{SITE}" style="color:#2E6DB4">intranet.example.com</a></td></tr></table></td></tr></table></body></html>"""


# ---------- private files (HSE photos, certificate scans): never under the public /uploads/ URL ----------
def save_private(data: bytes, subdir: str, allow_pdf=False) -> str:
    """Re-encode images to JPEG (drops EXIF/GPS), keep PDFs as-is (checked by magic). Returns the stored file name."""
    import io
    import uuid
    from PIL import Image
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "max 15 MB")
    folder = os.path.join(UPLOADS, subdir)
    os.makedirs(folder, exist_ok=True)
    if allow_pdf and data[:5] == b"%PDF-":
        name = f"{uuid.uuid4().hex}.pdf"
        with open(os.path.join(folder, name), "wb") as f:
            f.write(data)
        return name
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        raise HTTPException(422, "PDF or image required" if allow_pdf else "not an image")
    img = img.convert("RGB")
    img.thumbnail((2000, 2000))
    name = f"{uuid.uuid4().hex}.jpg"
    img.save(os.path.join(folder, name), "JPEG", quality=85, optimize=True)
    return name


def private_path(subdir: str, name: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{32}\.(jpg|pdf)", name or ""):
        raise HTTPException(404)
    path = os.path.join(UPLOADS, subdir, name)
    if not os.path.exists(path):
        raise HTTPException(404)
    return path
