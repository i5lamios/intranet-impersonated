"""HR people editor: HR (AD group Intranet-HR-Editors) keeps staff job data in AD from the intranet.

Two service accounts, each limited by AD ACLs on user objects under OU=Company:
  svc-intranet-hr  title, department, company, manager            (AD_HR_WRITE_*; this page only)
  svc-intranet-ad  telephoneNumber, mobile, physicalDeliveryOfficeName (the self-service profile account)
The target is looked up again in AD and must pass profile.writable(): an ordinary staff user under OU=Company, not an
admin, a member of a privileged group or a service account.
Every change goes to profile_changes with the HR editor's user name.
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from ldap3 import BASE as SCOPE_BASE, MODIFY_DELETE, MODIFY_REPLACE
from pydantic import BaseModel, Field

from .core import User, directory, pool, role, secret
from .directory import BASE as AD_BASE
from .profile import PHONE, WRITER, _conn, writable

HR_WRITER = os.environ.get("AD_HR_WRITE_BIND", "svc-intranet-hr@example.com")
HR_ATTRS = {"title": "title", "department": "department", "company": "company", "manager": "manager"}
SELF_ATTRS = {"office": "physicalDeliveryOfficeName", "phone": "telephoneNumber", "mobile": "mobile"}

router = APIRouter()
hr = role("news")


@router.get("/api/hr/people")
def people(user: User = Depends(hr)):
    with directory._lock:
        ps = list(directory._people.values())
        by_dn = dict(directory._by_dn)
    out = []
    for p in ps:
        mid = by_dn.get(p["manager_dn"].lower()) if p["manager_dn"] else None
        out.append({k: p[k] for k in ("id", "name", "username", "mail", "title", "department", "company", "office", "phone", "mobile")}
                   | {"manager": mid, "configured": bool(secret("AD_HR_WRITE_PASSWORD", ""))})
    return sorted(out, key=lambda x: x["name"].lower())


class PersonIn(BaseModel):                                   # only the fields HR changed; None = leave as it is
    title: str | None = Field(default=None, max_length=128)
    department: str | None = Field(default=None, max_length=64)
    company: str | None = Field(default=None, max_length=64)
    manager: str | None = Field(default=None, max_length=40)  # directory id, "" = none
    office: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=40)
    mobile: str | None = Field(default=None, max_length=40)


@router.put("/api/hr/people/{pid}")
def update(pid: str, p: PersonIn, user: User = Depends(hr)):
    try:
        dn = directory.dn(pid)
    except KeyError:
        raise HTTPException(404)
    for k in ("phone", "mobile"):
        v = (getattr(p, k) or "").strip()
        if v and not PHONE.match(v):
            raise HTTPException(422, f"{k}: not a phone number")
    manager_dn = ""
    if p.manager:
        if p.manager == pid:
            raise HTTPException(422, "a person cannot be their own manager")
        try:
            manager_dn = directory.dn(p.manager)
        except KeyError:
            raise HTTPException(422, "manager not found in the directory")
    want = {k: v.strip() for k, v in p.model_dump().items() if v is not None and k != "manager"}
    if p.manager is not None:
        want["manager"] = manager_dn

    with _conn() as c:                                       # current values, straight from AD
        c.search(dn, "(objectClass=*)", SCOPE_BASE, attributes=["objectClass", "adminCount", "sAMAccountName",
                                                                 *HR_ATTRS.values(), *SELF_ATTRS.values()])
        if not c.entries:
            raise HTTPException(404)
        e = c.entries[0]
    classes = [x.lower() for x in e["objectClass"].values]
    if "user" not in classes or "computer" in classes or not dn.lower().endswith(AD_BASE.lower()):
        raise HTTPException(422, "only staff accounts can be edited here (not contacts)")
    if not writable(dn):
        raise HTTPException(403, "protected account (admin, privileged or service account) - IT changes it in AD")
    cur = lambda a: str(e[a].value) if a in e and e[a].value is not None else ""

    done = []
    for attrs, bind, pw_name in ((HR_ATTRS, HR_WRITER, "AD_HR_WRITE_PASSWORD"), (SELF_ATTRS, WRITER, "AD_WRITE_PASSWORD")):
        mods, log = {}, []
        for field, attr in attrs.items():
            if field not in want:
                continue
            old, new = cur(attr), want[field]
            if old == new:
                continue
            if new:
                mods[attr] = [(MODIFY_REPLACE, [new])]
            elif old:
                mods[attr] = [(MODIFY_DELETE, [])]
            log.append((attr, old, new))
        if not mods:
            continue
        pw = secret(pw_name, "")
        if not pw:
            raise HTTPException(503, "editing staff data is not configured yet (AD service account)")
        with _conn(bind, pw) as w:
            if not w.modify(dn, mods):
                raise HTTPException(502, f"AD refused the change: {w.result.get('description')}" +
                                    (f" ({', '.join(done)} already saved)" if done else ""))
        with pool.connection() as db:
            for attr, old, new in log:
                db.execute("INSERT INTO profile_changes (username, field, old_value, new_value, changed_by) VALUES (%s,%s,%s,%s,%s)",
                           (cur("sAMAccountName").lower(), attr, old, new, user.username))
        done += [a for a, _, _ in log]
    if done:
        directory.refresh_soon()
    return {"changed": done}


@router.get("/api/hr/people/{pid}/history")
def history(pid: str, user: User = Depends(hr)):
    try:
        uname = directory.person(pid)["username"]
    except Exception:
        raise HTTPException(404)
    with pool.connection() as db:
        rows = db.execute("SELECT field, old_value, new_value, changed_by, changed_at FROM profile_changes WHERE username=%s "
                          "ORDER BY changed_at DESC LIMIT 30", (uname,)).fetchall()
    return [dict(r) | {"changed_at": r["changed_at"].isoformat(timespec="minutes")} for r in rows]
