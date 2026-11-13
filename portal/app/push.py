"""Browser push notifications (Web Push + VAPID). Users opt in per browser (🔔 in the header); the service worker
(/sw.js) shows the notification. Sent when news is published and when the emergency banner is switched on.
Messages travel encrypted through the browser vendor's push service (Google, Mozilla, Apple)."""
import base64
import json
import logging
import re
import threading

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from py_vapid import Vapid01
from cryptography.hazmat.primitives import serialization
from pywebpush import WebPushException, webpush

from .core import User, current_user, pool, run_schema

log = logging.getLogger("push")

run_schema("""
CREATE TABLE IF NOT EXISTS settings (key text PRIMARY KEY, value text NOT NULL);
CREATE TABLE IF NOT EXISTS push_subs (
  endpoint text PRIMARY KEY, p256dh text NOT NULL, auth text NOT NULL, username text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
""")


def _keys():
    with pool.connection() as c:
        row = c.execute("SELECT value FROM settings WHERE key='vapid_pem'").fetchone()
        if not row:
            v = Vapid01(); v.generate_keys()
            c.execute("INSERT INTO settings (key, value) VALUES ('vapid_pem', %s) ON CONFLICT DO NOTHING", (v.private_pem().decode(),))
            row = c.execute("SELECT value FROM settings WHERE key='vapid_pem'").fetchone()
    vapid = Vapid01.from_pem(row["value"].encode())
    raw = vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return vapid, base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


VAPID, PUBLIC_KEY = _keys()
router = APIRouter()


@router.get("/api/push/key")
def key():
    return {"key": PUBLIC_KEY}


# Only the browser vendors' push services: the server later POSTs to this address, so anything else would let a
# signed-in user point it at an internal system.
PUSH_HOSTS = r"^https://(fcm\.googleapis\.com|updates\.push\.services\.mozilla\.com|[a-z0-9-]+\.push\.apple\.com|[a-z0-9-]+\.notify\.windows\.com)/"


class Sub(BaseModel):
    endpoint: str = Field(max_length=1000, pattern=PUSH_HOSTS)
    p256dh: str = Field(max_length=200)
    auth: str = Field(max_length=100)


@router.post("/api/push/subscribe", status_code=204)
def subscribe(s: Sub, user: User = Depends(current_user)):
    with pool.connection() as c:
        c.execute("INSERT INTO push_subs (endpoint, p256dh, auth, username) VALUES (%s,%s,%s,%s) ON CONFLICT (endpoint) "
                  "DO UPDATE SET p256dh=EXCLUDED.p256dh, auth=EXCLUDED.auth, username=EXCLUDED.username",
                  (s.endpoint, s.p256dh, s.auth, user.username))
    return Response(status_code=204)


class Unsub(BaseModel):
    endpoint: str = Field(max_length=1000)


@router.post("/api/push/unsubscribe", status_code=204)
def unsubscribe(s: Unsub, user: User = Depends(current_user)):
    with pool.connection() as c:
        c.execute("DELETE FROM push_subs WHERE endpoint=%s AND username=%s", (s.endpoint, user.username))
    return Response(status_code=204)


def notify_all(title, body, url="/", tag=None):
    """Fire-and-forget: push to every subscribed browser; drop subscriptions the push service says are gone."""
    threading.Thread(target=_send_all, args=(title, body, url, tag), daemon=True).start()


def notify_users(usernames, title, body, url="/", tag=None):
    """Same, only to these people's browsers (user names as in AD / Keycloak)."""
    names = sorted({u.lower() for u in usernames if u})
    if names:
        threading.Thread(target=_send_all, args=(title, body, url, tag, names), daemon=True).start()


def _send_all(title, body, url, tag, names=None):
    with pool.connection() as c:
        subs = c.execute("SELECT * FROM push_subs" + (" WHERE lower(username) = ANY(%s)" if names else ""),
                         ((names,) if names else ())).fetchall()
    data = json.dumps({"title": title[:120], "body": body[:240], "url": url, "tag": tag or url})
    dead = []
    for s in subs:
        if not re.match(PUSH_HOSTS, s["endpoint"]):          # stored before the address check existed
            dead.append(s["endpoint"])
            continue
        try:
            webpush({"endpoint": s["endpoint"], "keys": {"p256dh": s["p256dh"], "auth": s["auth"]}}, data,
                    vapid_private_key=VAPID, vapid_claims={"sub": "mailto:it@example.com"}, ttl=86400, timeout=10)
        except WebPushException as e:
            if e.response is not None and e.response.status_code in (404, 410):
                dead.append(s["endpoint"])
            else:
                log.warning("push: %s", e)
        except Exception as e:
            log.warning("push: %s", e)
    if dead:
        with pool.connection() as c:
            c.execute("DELETE FROM push_subs WHERE endpoint = ANY(%s)", (dead,))
    log.info("push '%s': %d sent, %d expired", title, len(subs) - len(dead), len(dead))
