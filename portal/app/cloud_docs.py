"""HR document library: a folder in Company Cloud (Nextcloud), read over WebDAV.

The folder belongs to the local Cloud service user `intranet` and is shared (edit) with the AD group NC-HR-Docs, so HR
manages files in Cloud; the intranet lists them (sub-folders = sections) and streams downloads to signed-in staff.
"""
import os
import threading
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote

import requests

CLOUD = os.environ.get("CLOUD_URL", "https://cloud.example.com")
USER = os.environ.get("CLOUD_USER", "intranet")
ROOT = os.environ.get("CLOUD_DOCS_DIR", "HR Sənədləri")
TTL = 120
MAX_DEPTH = 4
NS = {"d": "DAV:", "oc": "http://owncloud.org/ns"}
PROPS = """<?xml version="1.0"?><d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns"><d:prop>
<d:getlastmodified/><d:getcontentlength/><d:getcontenttype/><d:resourcetype/><oc:size/></d:prop></d:propfind>"""


def _token():
    path = os.environ.get("CLOUD_TOKEN_FILE")
    if path and os.path.exists(path):
        return open(path).read().strip()
    return os.environ.get("CLOUD_TOKEN", "")


class Docs:
    def __init__(self):
        self._cache, self._at = None, 0
        self._lock = threading.Lock()
        self.s = requests.Session()
        self.base = f"{CLOUD}/remote.php/dav/files/{quote(USER)}/"
        self.prefix = f"/remote.php/dav/files/{quote(USER)}/{quote(ROOT)}/"

    @property
    def enabled(self):
        return bool(_token())

    def _url(self, rel):
        return self.base + quote(f"{ROOT}/{rel}".rstrip("/")) + ("/" if not rel or rel.endswith("/") else "")

    def _ls(self, rel):
        r = self.s.request("PROPFIND", self._url(rel.rstrip("/") + "/" if rel else ""), data=PROPS.encode(),
                           headers={"Depth": "1", "Content-Type": "application/xml"}, auth=(USER, _token()), timeout=20)
        r.raise_for_status()
        out = []
        for resp in ET.fromstring(r.content).findall("d:response", NS):
            href = unquote(resp.findtext("d:href", namespaces=NS))
            path = href.split(unquote(self.prefix), 1)[-1].strip("/")
            if path == rel.strip("/"):
                continue                                   # the folder itself
            p = resp.find("d:propstat/d:prop", NS)
            is_dir = p.find("d:resourcetype/d:collection", NS) is not None
            out.append({"path": path, "name": path.rsplit("/", 1)[-1], "dir": is_dir,
                        "size": int(p.findtext("oc:size", "0", NS) or p.findtext("d:getcontentlength", "0", NS) or 0),
                        "type": p.findtext("d:getcontenttype", "", NS), "modified": p.findtext("d:getlastmodified", "", NS)})
        return sorted(out, key=lambda x: (not x["dir"], x["name"].lower()))

    def _walk(self, rel="", depth=0):
        items = self._ls(rel)
        for it in items:
            if it["dir"] and depth < MAX_DEPTH:
                it["children"] = self._walk(it["path"], depth + 1)
        return [i for i in items if not i["name"].startswith(".")]

    def tree(self):
        with self._lock:
            if self._cache is None or time.time() - self._at > TTL:
                self._cache, self._at = self._walk(), time.time()
            return self._cache

    def open(self, rel):
        rel = rel.strip("/")
        if not rel or ".." in rel.split("/") or rel.startswith("."):
            raise ValueError("bad path")
        r = self.s.get(self._url(rel), auth=(USER, _token()), stream=True, timeout=60)
        if r.status_code == 404:
            raise FileNotFoundError(rel)
        r.raise_for_status()
        return r
