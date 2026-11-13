# intranet-ui-check

See an intranet exactly as a real user sees it — without knowing their password — by impersonating them
through the **Keycloak admin API** in a headless Chromium, then screenshotting pages and catching JS errors.

Works for any app behind the same Keycloak realm (intranet portal, file cloud, wiki …): the impersonation sets the
Keycloak SSO cookies in the browser context, so every OIDC/SAML client signs in silently.

## Files
| file | purpose |
|---|---|
| `asme.py` | `asme.py [--mobile] <username> <url>...` → screenshots in `./shots`, prints landing URL and any JS `pageerror`; exit 1 on errors. `session()` is importable for custom scripted flows. |
| `smoke.py` | Login-free post-deploy check: load URLs, fail on `pageerror` / failed script request. Run after every frontend deploy. |
| `setup-playwright.sh` | Installs Playwright from PyPI wheels into `./pwlib` on hosts with no pip. **Untested on a fresh host — verify the wheel picks.** |

## Configuration (env vars, or `KC_ENV_FILE=/path/to/file` with `KEY=VALUE` lines — keep that file outside the repo)
`KC_URL`, `KC_REALM`, `KC_ADMIN_USER`, `KC_ADMIN_PASSWORD`; optional `KC_ADMIN_REALM` (default `master`), `CHROMIUM`, `SHOTS_DIR`.

## Run
```
KC_ENV_FILE=~/secrets/keycloak.env PYTHONPATH=./pwlib python3 asme.py jdoe https://intranet.example.com/ https://intranet.example.com/rooms
python3 smoke.py https://intranet.example.com/        # needs playwright importable too (PYTHONPATH=./pwlib)
```

## Facts that matter
- Endpoint: `POST {KC_URL}/admin/realms/{realm}/users/{id}/impersonation` with a bearer admin token. The cookies come back
  on that response, so the request must go through the **browser context's** request object (`ctx.request`), which shares its cookie jar.
- Admin token (admin-cli, password grant) lives ~60 s → fetch a fresh one per session; never cache it.
- The admin needs the `impersonation` role of `realm-management` (and `view-users`). Prefer a dedicated account over the master admin.
- Every impersonation is audit-logged in Keycloak (admin events / `IMPERSONATE`). Tell the user whose view you are using and get their OK.
- Keycloak < 17 serves under `/auth`: put it in `KC_URL`.
- Impersonating a user does not bypass app-level authorisation — you see exactly what that user's groups/roles allow. That is the point.
- Use the system Chromium (`apt install chromium`); don't run `playwright install` (version mismatch). Needs `--no-sandbox` when run as root/in containers.
- Why the smoke test exists: one bad JS module can blank every page; screenshots of only the changed pages won't show it.

## Not included on purpose
No hostnames, realms, usernames or credentials. Supply your own via env.
