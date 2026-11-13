"""E-mail to the owner when a passkey is added to their SSO account (a stolen password plus office Wi-Fi would otherwise
be enough to add one and then reach Cloud from outside without OTP).

Reads Keycloak's stored events every 2 minutes with client `intranet-events` (service account, realm-management roles
view-events + view-users; secret KC_EVENTS_SECRET). Off when the secret is missing. One mail per user per minute of
adding, claimed in passkey_alerts so the two replicas don't both send.
"""
import html
import logging
import os
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from .core import mail_configured, mail_frame, pool, run_schema, secret, send_mail

log = logging.getLogger("passkeys")
KC = os.environ.get("KC_URL", "https://sso.example.com")
REALM = "company"
CLIENT = os.environ.get("KC_EVENTS_CLIENT", "intranet-events")
TYPE = "webauthn-passwordless"

run_schema("""
CREATE TABLE IF NOT EXISTS passkey_alerts (user_id text NOT NULL, minute bigint NOT NULL, sent_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, minute));
""")


def start():
    if secret("KC_EVENTS_SECRET", ""):
        threading.Thread(target=_loop, name="passkey-alerts", daemon=True).start()


def _token():
    r = requests.post(f"{KC}/realms/{REALM}/protocol/openid-connect/token", timeout=15,
                      data={"grant_type": "client_credentials", "client_id": CLIENT, "client_secret": secret("KC_EVENTS_SECRET")})
    r.raise_for_status()
    return r.json()["access_token"]


def _loop():
    since = int(time.time() * 1000) - 10 * 60 * 1000     # after a restart: look back 10 minutes (claims stop repeats)
    while True:
        try:
            if mail_configured():
                since = check(since)
        except Exception as e:
            log.error("passkey alerts: %s", e)
        time.sleep(120)


def check(since):
    tok = _token()
    h = {"Authorization": f"Bearer {tok}"}
    r = requests.get(f"{KC}/admin/realms/{REALM}/events", headers=h, timeout=20,
                     params=[("type", "UPDATE_CREDENTIAL"), ("type", "CUSTOM_REQUIRED_ACTION"), ("max", 200),
                             ("dateFrom", datetime.fromtimestamp(since / 1000, timezone.utc).strftime("%Y-%m-%d"))])
    r.raise_for_status()
    newest = since
    for e in r.json():
        d = e.get("details") or {}
        if e["time"] <= since or not e.get("userId"):
            continue
        newest = max(newest, e["time"])
        if d.get("credential_type") != TYPE and d.get("custom_required_action") != "webauthn-register-passwordless":
            continue
        with pool.connection() as c:                     # one mail per user per minute (both event types, both replicas)
            if not c.execute("INSERT INTO passkey_alerts (user_id, minute) VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING 1",
                             (e["userId"], e["time"] // 60000)).fetchone():
                continue
        u = requests.get(f"{KC}/admin/realms/{REALM}/users/{e['userId']}", headers=h, timeout=15).json()
        if u.get("email"):
            _mail(u, e)
    return newest


def _mail(u, e):
    when = datetime.fromtimestamp(e["time"] / 1000, ZoneInfo("Asia/Baku")).strftime("%d.%m.%Y %H:%M")
    ip = html.escape(e.get("ipAddress") or "")
    name = html.escape(" ".join(x for x in (u.get("firstName"), u.get("lastName")) if x) or u.get("username", ""))
    body = f"""<p>{name},</p>
<p>A passkey (Face ID / fingerprint / device PIN) was added to your Company account on <b>{when}</b> from {ip}.</p>
<p><b>If this was you</b>, nothing to do. <b>If it wasn't</b>, contact IT at once (Helpdesk or phone): IT removes the passkey
and resets your password. You can also delete it yourself in the intranet, <b>My profile → Passkeys</b>.</p>
<hr style="border:0;border-top:1px solid #DCE3EE">
<p>Hesabınıza <b>{when}</b> tarixində yeni passkey (Face ID / barmaq izi / PIN) əlavə edildi. Bunu siz etməmisinizsə, dərhal İT-yə müraciət edin.</p>
<p>К вашей учётной записи <b>{when}</b> добавлен новый ключ доступа (passkey). Если это были не вы, сразу обратитесь в ИТ.</p>"""
    send_mail(u["email"], "New passkey added to your Company account", mail_frame("New passkey added", body))
    log.info("passkey alert sent to %s", u.get("username"))
