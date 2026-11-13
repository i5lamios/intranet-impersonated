#!/usr/bin/env python3
"""Headless Chromium signed in as any user via Keycloak admin impersonation.

usage:  asme.py <username> <url> [<url> ...]          screenshots -> $SHOTS_DIR (default ./shots)
        asme.py --mobile <username> <url> ...         same, phone viewport/user agent

Configuration (environment variables, or a KEY=VALUE file named by KC_ENV_FILE):
  KC_URL             base URL of Keycloak, e.g. https://sso.example.com   (add /auth for legacy < 17 installs)
  KC_REALM           realm that holds the users and the intranet client
  KC_ADMIN_USER      admin account allowed to impersonate (needs realm-management: impersonation)
  KC_ADMIN_PASSWORD
  KC_ADMIN_REALM     realm the admin logs in to (default: master)
  CHROMIUM           browser binary (default: auto-detect chromium / google-chrome)
  SHOTS_DIR          output directory (default: ./shots)

Every impersonation is written to the Keycloak admin/event log (IMPERSONATE) - that is intended.
The admin token lives ~60 s, so one is fetched per browser session, never cached.
"""
import json, os, re, shutil, sys, urllib.parse, urllib.request


def load_env():
    path = os.environ.get("KC_ENV_FILE")
    if path:
        for line in open(os.path.expanduser(path)):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing {name} (see header of asme.py)")
    return v


def http(url, data=None, token=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, body, {"Authorization": f"Bearer {token}"} if token else {})
    return json.load(urllib.request.urlopen(req))


def admin_token():
    k, realm = need("KC_URL").rstrip("/"), os.environ.get("KC_ADMIN_REALM", "master")
    return http(f"{k}/realms/{realm}/protocol/openid-connect/token", {
        "client_id": "admin-cli", "grant_type": "password",
        "username": need("KC_ADMIN_USER"), "password": need("KC_ADMIN_PASSWORD")})["access_token"]


def user_id(username):
    k, realm = need("KC_URL").rstrip("/"), need("KC_REALM")
    users = http(f"{k}/admin/realms/{realm}/users?exact=true&username={urllib.parse.quote(username)}", token=admin_token())
    if not users:
        sys.exit(f"user {username!r} not found in realm {realm}")
    return users[0]["id"]


def chromium_path():
    p = os.environ.get("CHROMIUM") or next((shutil.which(b) for b in ("chromium", "chromium-browser", "google-chrome") if shutil.which(b)), None)
    if not p:
        sys.exit("no Chromium found; set CHROMIUM=/path/to/binary")
    return p


MOBILE_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36"


def session(p, username, width=1400, height=900, mobile=False):
    """Return (browser, context) whose cookie jar already holds the impersonated Keycloak SSO session.
    Any app that logs in through the same realm is then signed in as that user without a password."""
    uid = user_id(username)
    b = p.chromium.launch(executable_path=chromium_path(), args=["--no-sandbox"])
    extra = {"user_agent": MOBILE_UA} if mobile else {}
    ctx = b.new_context(viewport={"width": 390 if mobile else width, "height": 844 if mobile else height},
                        ignore_https_errors=True, is_mobile=mobile, has_touch=mobile,
                        device_scale_factor=1, locale="en-US", **extra)
    k, realm = need("KC_URL").rstrip("/"), need("KC_REALM")
    # ctx.request shares the context's cookie jar: the impersonation response sets KEYCLOAK_IDENTITY etc. there
    r = ctx.request.post(f"{k}/admin/realms/{realm}/users/{uid}/impersonation",
                         headers={"Authorization": f"Bearer {admin_token()}"})
    assert r.ok, f"impersonation failed: HTTP {r.status} {r.text()[:200]}"
    return b, ctx


def main(argv):
    mobile = "--mobile" in argv
    argv = [a for a in argv if a != "--mobile"]
    if len(argv) < 2:
        sys.exit(__doc__)
    from playwright.sync_api import sync_playwright
    load_env()
    out = os.environ.get("SHOTS_DIR", "shots")
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b, ctx = session(p, argv[0], mobile=mobile)
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        for url in argv[1:]:
            pg.goto(url, wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(1500)  # let SPA routers / late XHRs settle
            name = re.sub(r"[^a-z0-9]+", "-", url.split("//", 1)[-1].lower()).strip("-")[:60]
            pg.screenshot(path=f"{out}/{name}.png")
            print(f"{name} | landed on {pg.url[:90]}")
        b.close()
        for e in errors:
            print("PAGEERROR:", e)
        sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
