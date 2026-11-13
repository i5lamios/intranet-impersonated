"""AD address book, cached in memory.

Replaces ab.example.com (PHP): that page bound to a DC over plain LDAP on every search and put the search text
straight into the LDAP filter. Here one LDAPS connection (dc01, fallback dc02) refreshes a snapshot every
REFRESH seconds; searching/sorting happens in the browser, photos are served from the cache with an ETag.
Same population as before (people/contacts in OU=Company with a phone, not hidden from the GAL) minus disabled
accounts.
"""
import hashlib
import logging
import os
import ssl
import threading
import time
from collections import Counter

from ldap3 import Connection, Server, ServerPool, Tls, FIRST, SUBTREE

log = logging.getLogger("directory")

BASE = os.environ.get("LDAP_BASE", "OU=Company,DC=company,DC=az")
HOSTS = os.environ.get("LDAP_HOSTS", "dc01.example.com,dc02.example.com").split(",")
BIND = os.environ.get("LDAP_BIND", "svc-portal@example.com")
CA = os.environ.get("LDAP_CA", "/etc/ssl/company-ca.pem")
REFRESH = int(os.environ.get("DIRECTORY_REFRESH", "600"))
# People: anyone with a phone, plus mailbox users with a real name and a first.last login (no shared / platform
# accounts such as "bd", "chirag1"). Hide anyone else from the directory with msExchHideFromAddressLists.
FILTER = ("(&(objectCategory=person)(|(objectClass=user)(objectClass=contact))"
          "(!(msExchHideFromAddressLists=TRUE))(!(userAccountControl:1.2.840.113556.1.4.803:=2))"
          "(|(telephoneNumber=*)(mobile=*)(&(objectClass=user)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*.*))))")
ATTRS = ["objectGUID", "sAMAccountName", "displayName", "givenName", "sn", "title", "department", "company",
         "physicalDeliveryOfficeName", "l", "telephoneNumber", "mobile", "mail", "manager", "thumbnailPhoto", "ipPhone",
         "distinguishedName"]
PUBLIC = ("id", "username", "name", "title", "department", "office", "phone", "mobile", "mail", "extension", "has_photo")


def _v(e, a):
    v = e.get(a)
    if isinstance(v, list):
        v = v[0] if v else None
    return v.strip() if isinstance(v, str) else v


# AD placeholders some people typed instead of leaving the field empty ("N/A", "-", "yox", ...)
BLANK = {"n/a", "na", "n\\a", "n.a.", "-", "--", "—", ".", "0", "none", "null", "nil", "yox", "нет", "no", "tbd", "x"}


def _c(a, k):
    v = (_v(a, k) or "").strip()
    if k in ("telephoneNumber", "mobile", "ipPhone") and not any(ch.isdigit() for ch in v):
        return ""   # "N/D", "N\\D", an e-mail address typed into the phone field, ...
    return "" if v.lower() in BLANK else v


class Directory:
    def __init__(self, password):
        self._pw = password
        self._people, self._by_dn, self._photos = {}, {}, {}
        self._depts, self._offices = [], []
        self.updated = None
        self._lock = threading.Lock()
        self._wake = threading.Event()

    # ---- refresh ----
    def start(self):
        threading.Thread(target=self._loop, name="directory", daemon=True).start()

    def _loop(self):
        while True:
            try:
                self.refresh()
            except Exception as e:                      # keep serving the last good snapshot
                log.error("directory refresh failed: %s", e)
            self._wake.wait(REFRESH if self.updated else 30)
            self._wake.clear()

    def refresh_soon(self):
        """After a profile change: re-read AD now instead of waiting for the next cycle."""
        self._wake.set()

    def refresh(self):
        tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=CA)
        pool = ServerPool([Server(h, port=636, use_ssl=True, tls=tls, connect_timeout=5) for h in HOSTS], FIRST,
                          active=1, exhaust=60)
        with Connection(pool, user=BIND, password=self._pw, auto_bind=True, read_only=True,
                        receive_timeout=30) as c:
            entries = c.extend.standard.paged_search(BASE, FILTER, SUBTREE, attributes=ATTRS, paged_size=500,
                                                     generator=False)
        people, by_dn, photos = {}, {}, {}
        for e in entries:
            a = e.get("attributes") or {}
            if not a:
                continue
            guid = a.get("objectGUID")
            pid = str(guid).strip("{}") if guid else hashlib.sha1(e["dn"].encode()).hexdigest()[:32]
            photo = a.get("thumbnailPhoto")
            photo = photo[0] if isinstance(photo, list) and photo else photo
            p = {"id": pid, "username": (_v(a, "sAMAccountName") or "").lower(),
                 "name": _v(a, "displayName") or " ".join(x for x in (_v(a, "givenName"), _v(a, "sn")) if x),
                 "title": _c(a, "title"), "department": _c(a, "department"),
                 "office": _c(a, "physicalDeliveryOfficeName"), "city": _c(a, "l"),
                 "company": _c(a, "company"), "phone": _c(a, "telephoneNumber").replace("+", ""),
                 "mobile": _c(a, "mobile"), "mail": (_v(a, "mail") or "").lower(),
                 "manager_dn": _v(a, "manager") or "", "has_photo": bool(photo),
                 "extension": _c(a, "ipPhone"), "dn": e["dn"]}
            people[pid] = p
            by_dn[e["dn"].lower()] = pid
            if photo:
                photos[pid] = (bytes(photo), '"' + hashlib.sha1(photo).hexdigest()[:16] + '"')
        offices = self._normalise_offices(people.values())
        with self._lock:
            self._people, self._by_dn, self._photos = people, by_dn, photos
            self._depts = sorted({p["department"] for p in people.values() if p["department"]}, key=str.lower)
            self._offices = offices
            self.updated = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        log.info("directory: %d people, %d photos", len(people), len(photos))

    @staticmethod
    def _normalise_offices(people):
        # "Base yard" / "Base Yard" / "base yard " → one value (most common spelling wins)
        groups = {}
        for p in people:
            o = p["office"]
            if o:
                groups.setdefault(" ".join(o.lower().split()), Counter())[o] += 1
        canon = {k: c.most_common(1)[0][0] for k, c in groups.items()}
        for p in people:
            if p["office"]:
                p["office"] = canon[" ".join(p["office"].lower().split())]
        return sorted(set(canon.values()), key=str.lower)

    # ---- reads ----
    def people(self):
        with self._lock:
            return sorted(({k: p[k] for k in PUBLIC} for p in self._people.values()), key=lambda p: p["name"].lower())

    def org(self):
        """Everyone with department/title and the id of their AD manager (None if unset or not listed)."""
        with self._lock:
            return [{"id": p["id"], "name": p["name"], "title": p["title"], "department": p["department"],
                     "office": p["office"], "has_photo": p["has_photo"],
                     "manager": self._by_dn.get(p["manager_dn"].lower()) if p["manager_dn"] else None}
                    for p in self._people.values()]

    def find(self, key):
        """Match a username, e-mail or full name (case-insensitive) → person id."""
        k = " ".join(key.lower().split())
        with self._lock:
            for p in self._people.values():
                if k in (p["username"], p["mail"], " ".join(p["name"].lower().split())) or \
                        (p["mail"] and k == p["mail"].split("@")[0]):
                    return p["id"]
        return None

    def dn(self, pid):
        with self._lock:
            return self._people[pid]["dn"]

    def attr(self, pid, name):
        """Current AD value of a few raw attributes (for sync jobs)."""
        key = {"ipPhone": "extension"}[name]
        with self._lock:
            return self._people.get(pid, {}).get(key, "")

    def departments(self):
        return self._depts

    def offices(self):
        return self._offices

    def person(self, pid):
        with self._lock:
            p = self._people.get(pid) or next((x for x in self._people.values() if x["username"] == pid.lower()), None)
            if not p:
                return None
            out = {k: v for k, v in p.items() if k not in ("manager_dn", "dn")}
            mid = self._by_dn.get(p["manager_dn"].lower()) if p["manager_dn"] else None
            out["manager"] = {"id": mid, "name": self._people[mid]["name"]} if mid else None
            out["reports"] = sorted(({"id": x["id"], "name": x["name"], "title": x["title"]} for x in self._people.values()
                                     if x["manager_dn"] and self._by_dn.get(x["manager_dn"].lower()) == p["id"]),
                                    key=lambda r: r["name"].lower())
            return out

    def photo(self, pid):
        with self._lock:
            return self._photos.get(pid, (None, None))
