# Intranet portal

Company intranet: FastAPI backend + TypeScript/React frontend, one Docker image. Sign-in via Keycloak (OIDC, public
client with PKCE); authorisation = AD security groups passed in the token's `groups` claim. Languages en / ru / az.

Ported from a previous deployment by the same author. Hostnames, company name, domain and people were replaced with
placeholders (`example.com`, `Company`, `admin.user`, `10.0.0.x`). **Adapt them before deploying.** No secrets are in this repo.

## Layout
| path | what |
|---|---|
| `portal/app/` | FastAPI API (`main.py` routes; one module per feature) — serves the built frontend from `app/static` |
| `portal/web/` | React + Vite frontend (`src/pages`, `src/components`, UI strings in `src/lib/dict.ts`; TinyMCE self-hosted in `public/vendor`) |
| `portal/Dockerfile` | 2-stage build: node 20 → `npm run build` (type-checks), python 3.13 → uvicorn :8080 |
| `deploy/stack.example.yml` | Docker Swarm stack as it ran (Traefik labels, NFS uploads volume, Swarm secrets, branding configs) |
| `deploy/SETUP-NOTES.md` | Per-feature notes: DB, AD service accounts and rights, roles, mail, 3CX, room booking, push |
| `deploy/ci-workflow.example.yml` | CI template (move to `.github/workflows/` when ready): build → GHCR → pin tag in the stack → deploy via self-hosted runner (adapt) |

## Features (module → page)
news + editor (`main.py`, TinyMCE, nh3 sanitising) · directory + org chart from AD (`directory.py`) · HR people editing →
AD (`hrpeople.py`) · own profile → AD (`profile.py`) · HR documents from Nextcloud (`cloud_docs.py`) · meeting rooms via
Exchange EWS (`rooms.py`, `roomops.py`) · weekly news e-mail (`digest.py`) · weather (`weather.py`, Open-Meteo) ·
HSE board + hazard reports (`hse.py`) · certificates/training (`certs.py`) · Help Center (`helpcenter.py`, seed `helpseed.py`) ·
IT helpdesk → ServiceDesk Plus or mail (`helpdesk.py`) · Web Push (`push.py`) · analytics (`analytics.py`) · audit (`audit.py`) ·
passkey-added alerts from Keycloak events (`passkeyalerts.py`) · 3CX presence/click-to-call/sync (`threecx.py`).
Drop modules the new company does not need (remove the router include in `main.py` and the page in `web/src`).

## Configuration
All via environment variables (see `deploy/stack.example.yml`); passwords via `*_FILE` pointing to Docker secrets.
Key ones: `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `DB_HOST`/`DB_PASSWORD_FILE` (PostgreSQL), `LDAP_HOSTS`, `LDAP_BASE`,
`LDAP_BIND`/`LDAP_PASSWORD_FILE`, `LDAP_CA`, `EDITOR_GROUP`/`HSE_GROUP`/`IT_GROUP` (AD group names), `SITE_URL`,
`EWS_URL`, `SMTP_HOST`, `ROOMS`, `CLOUD_URL`. Grep `os.environ.get(` in `portal/app` for the full list and defaults —
**defaults still point at `example.com` placeholders.**

## Branding
The stack mounts `brand.css`, `logo.png`, `logo-white.png`, `icon.png`, `app-*.png`, `badge-96.png` into `app/static/`
from a `branding/` folder that is NOT included — create one for the new company.

## Build / run
```
cd portal && docker build -t intranet .
cd portal/web && npm ci && npm run build      # frontend only, type-check
```
After every deploy, load the site headless and fail on any JS `pageerror` — one broken module blanks every page.
