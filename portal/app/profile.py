"""Self-service profile: each signed-in user edits their OWN mobile, office and photo in AD (office phone and extension
are kept by IT/HR - the HR People page writes phone/office with the same account).

Writes go over LDAPS as `svc-intranet-ad`, which may write only telephoneNumber, mobile, physicalDeliveryOfficeName,
thumbnailPhoto and ipPhone on user objects under OU=Company (admin accounts are protected by AdminSDHolder).
The target DN is looked up from the token's user name — never taken from the request. Every change is logged.
Name, title, department and manager stay with HR.
"""
import io
import logging
import os
import re
import ssl

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from ldap3 import BASE as BASE_SCOPE, MODIFY_DELETE, MODIFY_REPLACE, SUBTREE, Connection, Server, ServerPool, Tls, FIRST
from ldap3.utils.conv import escape_filter_chars
from PIL import Image, ImageOps
from pydantic import BaseModel, Field

from .core import CA, UPLOADS, User, current_user, directory, me_person, pool, run_schema, secret
from .directory import BASE as AD_BASE, HOSTS

WRITER = os.environ.get("AD_WRITE_BIND", "svc-intranet-ad@example.com")
READ_ATTRS = ["displayName", "title", "department", "company", "mail", "telephoneNumber", "mobile",
              "physicalDeliveryOfficeName", "ipPhone", "manager", "sAMAccountName", "thumbnailPhoto", "adminCount"]

run_schema("""
CREATE TABLE IF NOT EXISTS profile_changes (
  id serial PRIMARY KEY, username text NOT NULL, field text NOT NULL, old_value text, new_value text,
  changed_by text NOT NULL, changed_at timestamptz NOT NULL DEFAULT now()
);
""")

log = logging.getLogger("profile")
router = APIRouter()
PHONE = re.compile(r"^[+0-9 ()\-./]{3,30}( ?(ext|доб|daxili)\.? ?[0-9]{1,6})?$", re.I)


def _conn(user=None, password=None):
    tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=CA)
    srv = ServerPool([Server(h, port=636, use_ssl=True, tls=tls, connect_timeout=5) for h in HOSTS], FIRST, active=1, exhaust=60)
    return Connection(srv, user=user or os.environ.get("LDAP_BIND", "svc-portal@example.com"),
                      password=password or secret("LDAP_PASSWORD"), auto_bind=True, receive_timeout=20)


def _me(username):
    with _conn() as c:
        c.search(AD_BASE, f"(&(objectCategory=person)(objectClass=user)(sAMAccountName={escape_filter_chars(username)}))",
                 SUBTREE, attributes=READ_ATTRS)
        if not c.entries:
            raise HTTPException(404, "your account is not in the Company staff OU")
        e = c.entries[0]
    v = lambda a: (e[a].value if a in e and e[a].value is not None else "")
    return e.entry_dn, {"name": v("displayName"), "title": v("title"), "department": v("department"), "company": v("company"),
                        "mail": v("mail"), "phone": v("telephoneNumber"), "mobile": v("mobile"),
                        "office": v("physicalDeliveryOfficeName"), "extension": v("ipPhone"),
                        "has_photo": bool(v("thumbnailPhoto")),
                        "protected": not writable(e.entry_dn)}


# Strict access: the intranet writes only to ordinary staff accounts. Never to AD-protected admins (adminCount=1),
# members (also nested) of privileged groups, service accounts, or anything outside OU=Company.
PRIVILEGED = ("Domain Admins", "Enterprise Admins", "Schema Admins", "Administrators", "Account Operators", "Server Operators",
              "Backup Operators", "Print Operators", "Group Policy Creator Owners", "DnsAdmins", "Key Admins",
              "Enterprise Key Admins", "Organization Management", "Exchange Trusted Subsystem", "Exchange Windows Permissions")
_priv_dns = None


def writable(dn):
    """True only for an ordinary staff user (see above). Checked on every write and shown as 'protected'."""
    global _priv_dns
    if not dn or not dn.lower().endswith("," + AD_BASE.lower()):
        return False
    with _conn() as c:
        if _priv_dns is None:                               # privileged groups anywhere in the domain
            root = ",".join(x for x in AD_BASE.split(",") if x.strip().upper().startswith("DC="))
            c.search(root, "(&(objectClass=group)(|" + "".join(f"(sAMAccountName={escape_filter_chars(g)})" for g in PRIVILEGED) + "))",
                     SUBTREE, attributes=["cn"])
            found = [e.entry_dn for e in c.entries]
            if len(found) < 5:                              # fail closed if the lookup looks wrong
                log.error("privileged group lookup found only %d groups - refusing AD writes", len(found))
                return False
            _priv_dns = found
        flt = ("(&(objectCategory=person)(objectClass=user)(!(adminCount=1))(!(sAMAccountName=svc*))"
               + "".join(f"(!(memberOf:1.2.840.113556.1.4.1941:={escape_filter_chars(g)}))" for g in _priv_dns) + ")")
        c.search(dn, flt, BASE_SCOPE, attributes=["sAMAccountName"])
        return bool(c.entries)


def _write(dn, changes: dict, who: str, old: dict):
    if not writable(dn):
        raise HTTPException(403, "this account is protected (admin, privileged or service account) - IT changes it in AD")
    pw = secret("AD_WRITE_PASSWORD", "")
    if not pw:
        raise HTTPException(503, "profile editing is not configured")
    mods = {attr: ([(MODIFY_REPLACE, [val])] if val not in ("", None) else [(MODIFY_DELETE, [])]) for attr, val in changes.items()}
    with _conn(WRITER, pw) as c:
        if not c.modify(dn, mods):
            log.warning("profile write refused for %s (%s): %s", who, ",".join(mods), c.result.get("description"))
            raise HTTPException(502, f"AD refused the change: {c.result.get('description')}")
    with pool.connection() as db:
        for attr, val in changes.items():
            db.execute("INSERT INTO profile_changes (username, field, old_value, new_value, changed_by) VALUES (%s,%s,%s,%s,%s)",
                       (who, attr, "(photo)" if attr == "thumbnailPhoto" else str(old.get(attr, "")),
                        "(photo)" if attr == "thumbnailPhoto" and val else ("" if val is None else str(val)), who))


@router.get("/api/profile")
def profile(user: User = Depends(current_user)):
    _, me = _me(user.username)
    me["offices"] = directory.offices()
    me["editable"] = bool(secret("AD_WRITE_PASSWORD", "")) and not me["protected"]
    with pool.connection() as db:
        me["history"] = [dict(r, changed_at=r["changed_at"].isoformat(timespec="minutes")) for r in db.execute(
            "SELECT field, new_value, changed_at FROM profile_changes WHERE username=%s ORDER BY changed_at DESC LIMIT 10",
            (user.username,))]
    pid = directory.find(user.username)
    me["id"] = pid
    return me


class ProfileIn(BaseModel):
    mobile: str = Field(default="", max_length=40)
    office: str = Field(default="", max_length=80)


@router.put("/api/profile")
def profile_set(p: ProfileIn, user: User = Depends(current_user)):
    """Staff change only their mobile, office (and photo). Office phone and extension are kept by IT/HR."""
    if p.mobile.strip() and not PHONE.match(p.mobile.strip()):
        raise HTTPException(422, "mobile: use digits, spaces, + ( ) - only")
    dn, cur = _me(user.username)
    if cur["protected"]:
        raise HTTPException(403, "admin and service accounts are protected - IT changes them in AD")
    want = {"mobile": p.mobile.strip(), "physicalDeliveryOfficeName": " ".join(p.office.split())}
    old = {"mobile": cur["mobile"], "physicalDeliveryOfficeName": cur["office"]}
    changes = {k: v for k, v in want.items() if v != old[k]}
    if changes:
        _write(dn, changes, user.username, old)
        directory.refresh_soon()
    return {"changed": sorted(changes)}


@router.post("/api/profile/photo")
async def profile_photo(file: UploadFile = File(...), user: User = Depends(current_user)):
    data = await file.read(15 * 1024 * 1024 + 1)
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "max 15 MB")
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except Exception:
        raise HTTPException(422, "not an image")
    dn, cur = _me(user.username)
    if cur["protected"]:
        raise HTTPException(403, "admin and service accounts are protected - IT changes them in AD")
    side = min(img.size)                                   # centre square crop → 256 px (Outlook/Exchange size)
    img = img.crop(((img.width - side) // 2, (img.height - side) // 2, (img.width + side) // 2, (img.height + side) // 2))
    me = me_person(user)
    if me:                                                 # sharp copy for the intranet (AD keeps only the small one)
        os.makedirs(os.path.join(UPLOADS, "photos"), exist_ok=True)
        img.resize((512, 512), Image.LANCZOS).save(os.path.join(UPLOADS, "photos", f"{me['id']}.jpg"), "JPEG", quality=86, optimize=True)
    img = img.resize((256, 256), Image.LANCZOS)
    for q in (88, 80, 70, 60, 50):                         # thumbnailPhoto must stay under 100 KB
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() < 95_000:
            break
    _write(dn, {"thumbnailPhoto": buf.getvalue()}, user.username, {})
    directory.refresh_soon()
    return {"ok": True}


@router.delete("/api/profile/photo")
def profile_photo_delete(user: User = Depends(current_user)):
    dn, cur = _me(user.username)
    if cur["protected"]:
        raise HTTPException(403, "admin and service accounts are protected - IT changes them in AD")
    me = me_person(user)
    if me and os.path.exists(os.path.join(UPLOADS, "photos", f"{me['id']}.jpg")):
        os.remove(os.path.join(UPLOADS, "photos", f"{me['id']}.jpg"))
    _write(dn, {"thumbnailPhoto": None}, user.username, {})
    directory.refresh_soon()
    return {"ok": True}
