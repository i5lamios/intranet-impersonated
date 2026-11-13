"""3CX V20 integration (XAPI, OAuth client credentials from 3CX Admin → Integrations → API).

* Presence: every 3CX user's status (Available / Away / DND …, registered or not) and active calls → coloured dot in
  the directory, matched to AD by e-mail address.
* Click-to-call: rings the signed-in user's own extension, then dials the colleague (Users/Pbx.MakeCall).
* Hourly sync (THREECX_SYNC = off | dryrun | apply):
    - AD ipPhone ← the user's 3CX extension number (writes as svc-intranet-ad, may only touch ipPhone + profile fields);
    - 3CX company phonebook ← staff mobiles / office phones from AD (contacts tagged "AD-sync"; removed when the
      person leaves), so calls from colleagues' mobiles show their name.
"""
import logging
import os
import re
import threading
import time

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .core import User, current_user, directory, secret

log = logging.getLogger("3cx")
URL = os.environ.get("THREECX_URL", "https://3cx.example.com:5001").rstrip("/")
CLIENT = os.environ.get("THREECX_CLIENT_ID", "")
SYNC = os.environ.get("THREECX_SYNC", "off")            # off | dryrun | apply
TAG = "AD-sync"
CA = os.environ.get("THREECX_CA", True)                 # public Let's Encrypt cert → system CAs

router = APIRouter()


class PBX:
    def __init__(self):
        self.s = requests.Session()
        self._token, self._exp = None, 0
        self.users, self.oncall, self.updated = {}, set(), 0
        self._lock = threading.Lock()

    @property
    def enabled(self):
        return bool(CLIENT and secret("THREECX_SECRET", ""))

    def _auth(self):
        if time.time() > self._exp - 60:
            r = self.s.post(f"{URL}/connect/token", timeout=15, verify=CA, data={
                "grant_type": "client_credentials", "client_id": CLIENT, "client_secret": secret("THREECX_SECRET")})
            r.raise_for_status()
            j = r.json()
            self._token, self._exp = j["access_token"], time.time() + int(j.get("expires_in", 3600))
        return {"Authorization": "Bearer " + self._token}

    def req(self, method, path, **kw):
        r = self.s.request(method, f"{URL}/xapi/v1{path}", headers=self._auth(), timeout=20, verify=CA, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"3CX {method} {path}: {r.status_code} {r.text[:200]}")
        return r.json() if r.content and "json" in r.headers.get("content-type", "") else None

    def get_all(self, path, params):
        out, skip = [], 0
        while True:
            page = self.req("GET", path, params={**params, "$top": 500, "$skip": skip})["value"]
            out += page
            if len(page) < 500:
                return out
            skip += 500

    # ---- presence ----
    def poll(self):
        tick = 0
        while True:
            try:
                if tick % 3 == 0:
                    users = self.get_all("/Users", {"$select": "Id,Number,FirstName,LastName,EmailAddress,CurrentProfileName,IsRegistered"})
                    with self._lock:
                        self.users = {(u.get("EmailAddress") or "").lower(): u for u in users if u.get("EmailAddress")}
                calls = self.req("GET", "/ActiveCalls")["value"]
                busy = set()
                for c in calls:
                    for side in (c.get("Caller") or "", c.get("Callee") or ""):
                        m = re.match(r"\s*(\d{2,6})\b", side)
                        if m:
                            busy.add(m.group(1))
                with self._lock:
                    self.oncall, self.updated = busy, time.time()
            except Exception as e:
                log.warning("3cx poll: %s", e)
                time.sleep(20)
            tick += 1
            time.sleep(10)

    def state(self, u):
        if u["Number"] in self.oncall:
            return "oncall"
        if not u.get("IsRegistered"):
            return "offline"
        p = (u.get("CurrentProfileName") or "").lower()
        return "available" if p in ("available", "") else "dnd" if "dnd" in p or "do not" in p else "away"

    def presence(self):
        people = directory.people()
        with self._lock:
            out = {}
            for p in people:
                u = self.users.get(p["mail"]) if p["mail"] else None
                if u:
                    out[p["id"]] = {"ext": u["Number"], "state": self.state(u), "profile": u.get("CurrentProfileName") or ""}
            return out

    def ext_of(self, email):
        with self._lock:
            u = self.users.get((email or "").lower())
            return u["Number"] if u else None

    # ---- sync ----
    def sync(self, apply):
        from .profile import _conn, WRITER, writable        # AD writer (ipPhone); never admins/service accounts
        from ldap3 import MODIFY_REPLACE
        actions = []
        users = self.get_all("/Users", {"$select": "Number,EmailAddress"})
        ext = {(u.get("EmailAddress") or "").lower(): u["Number"] for u in users if u.get("EmailAddress")}
        people = [p for p in directory.people()]
        # 1. AD ipPhone ← extension
        changes = []
        for p in people:
            e = ext.get(p["mail"]) if p["mail"] else None
            if e and directory.attr(p["id"], "ipPhone") != e and writable(directory.dn(p["id"])):
                changes.append((p, e))
        if changes:
            actions.append(f"AD ipPhone: {len(changes)} to set")
            if apply:
                pw = secret("AD_WRITE_PASSWORD", "")
                with _conn(WRITER, pw) as c:
                    for p, e in changes:
                        c.modify(directory.dn(p["id"]), {"ipPhone": [(MODIFY_REPLACE, [e])]})
        # 2. phonebook ← AD (tagged contacts)
        have = {c.get("Email", "").lower() or f"id{c['Id']}": c for c in
                self.get_all("/Contacts", {"$filter": f"Tag eq '{TAG}'"})}
        want = {}
        for p in people:
            if not p["mail"] or not (p["mobile"] or p["phone"]):
                continue
            first, _, last = p["name"].partition(" ")
            want[p["mail"]] = {"FirstName": first, "LastName": last, "CompanyName": "Company", "Department": p["department"],
                               "Title": p["title"], "Email": p["mail"], "Mobile2": p["mobile"] or "",
                               "Business": "" if p["mail"] in ext else (p["phone"] or ""), "Tag": TAG}
        add = [w for k, w in want.items() if k not in have]
        upd = [(have[k]["Id"], w) for k, w in want.items() if k in have and any((have[k].get(f) or "") != (w[f] or "") for f in w)]
        gone = [c["Id"] for k, c in have.items() if k not in want]
        actions.append(f"phonebook: +{len(add)} ~{len(upd)} -{len(gone)}")
        if apply:
            for w in add:
                self.req("POST", "/Contacts", json=w)
            for cid, w in upd:
                self.req("PATCH", f"/Contacts({cid})", json=w)
            if gone:
                self.req("POST", "/Contacts/Pbx.DeleteContactsById", json={"ids": gone})
        log.info("3cx sync (%s): %s", "apply" if apply else "dry-run", "; ".join(actions))
        return actions

    def sync_loop(self):
        while True:
            try:
                self.sync(SYNC == "apply")
            except Exception as e:
                log.error("3cx sync: %s", e)
            time.sleep(3600)


pbx = PBX()


def start():
    if pbx.enabled:
        threading.Thread(target=pbx.poll, name="3cx-presence", daemon=True).start()
        if SYNC in ("dryrun", "apply"):
            threading.Thread(target=pbx.sync_loop, name="3cx-sync", daemon=True).start()


@router.get("/api/phone/presence")
def presence(user: User = Depends(current_user)):
    if not pbx.enabled:
        return {"enabled": False, "people": {}}
    return {"enabled": True, "people": pbx.presence(), "me": pbx.ext_of(user.email)}


class CallIn(BaseModel):
    destination: str = Field(min_length=2, max_length=30)


@router.post("/api/phone/call")
def call(c: CallIn, user: User = Depends(current_user)):
    if not pbx.enabled:
        raise HTTPException(503, "3CX is not connected")
    me = pbx.ext_of(user.email)
    if not me:
        raise HTTPException(404, "you have no 3CX extension linked to your e-mail")
    dest = re.sub(r"[^\d+*#]", "", c.destination)
    if len(dest) < 2:
        raise HTTPException(422, "invalid number")
    try:
        pbx.req("POST", "/Users/Pbx.MakeCall", json={"dn": me, "destination": dest})
    except Exception as e:
        log.error("3CX call: %s", e)
        raise HTTPException(502, "the phone system did not accept the call")
    return {"ok": True, "from": me}
