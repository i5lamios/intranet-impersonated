# Intranet app — setup notes (from the original deployment; adapt names/hosts)

## Company Intranet app (apps/portal) — 2026-10-31
- News: PostgreSQL `portal`@db-server (table `news`, created by the app), images on NFS `/srv/nfs/portal/uploads`
  (re-encoded JPEG ≤1600 px, EXIF stripped). Editors = AD group `Intranet-HR-Editors` (members:
  `HR-Group`, admin.user; `groups` claim of client `intranet`) → "İdarəetmə · Admin" menu (hidden for others; API returns 403): Word-like editor (TinyMCE 8, self-hosted in
  `static/vendor/tinymce`, GPL, Azerbaijani UI, paste from Word, pictures/tables), Publish / Save draft, pin, cover
  (default = first picture), summary (default = start of the text). HTML is sanitised server-side (nh3 allow-list,
  images only from `/uploads/`).
- Directory (replaces ab.example.com): LDAPS dc01/02 as `svc-portal` (AD, read-only), snapshot every 10 min,
  same population as the old PHP page minus disabled accounts; photos from `thumbnailPhoto`; login required.
- ab.example.com: Traefik redirects `input.php?too=X` → `/directory?q=X`, `detailed.php?uid=X` → `/directory/X`,
  everything else → `/directory`. Old server 10.0.0.x (CentOS 7 + VestaCP) still serves until the DNS A record moves.
- Org chart `/org`: from AD `manager` (reporting lines) — not filled in AD yet (2026-10-31), so it shows departments.
- HR documents `/docs`: Cloud folder `HR Sənədləri` (+ Policies/Forms/Templates) of local Cloud user `intranet`
  (10 GB, app token = swarm secret `portal_cloud_token`), to be shared (edit) with AD group `NC-HR-Docs`
  (DomainLocal: HR-Group + admin.user) — shared (edit) 2026-10-31; group sharing on
  (`shareapi_allow_group_sharing=yes`, only `NC-*` AD groups exist in Cloud). Downloads are streamed by the app
  (signed-in staff only).
- Birthdays: HR enters day+month in Admin → Ad günləri (or pastes from Excel); table `birthdays` keyed by AD objectGUID.
  AD has no birth date attribute.
- Emergency banner: Admin → Elan (info / warning / emergency, optional end time); shown on every page.
- Meeting rooms `/rooms` and weekly e-mail (Monday 09:00, news since the last one, `hrnews@` → `allstaff@`) need AD
  user `svc-intranet` with mailbox `intranet@` (Send As on hrnews) → swarm secret `portal_svc_password`, then
  `ROOMS`, `DIGEST_ENABLED=1` in the stack. Exchange has no room mailboxes yet.
- Weather: Open-Meteo (internet from the Swarm), `WEATHER_PLACES`.
- Languages: en (default) / ru / az, per browser (`localStorage.lang`); UI strings in `apps/portal/web/src/lib/dict.ts`
  (key = English text). Help Center articles hold all three languages.
- Roles (AD groups, DomainLocal, OU Groups): `Intranet-HR-Editors` (HR: news, people page, birthdays, banner, e-mail; was Intranet-News-Editors),
  `Intranet-HSE-Editors` (HSE board, reports, certificates — members: admin.user; add the HSE team),
  `Intranet-IT-Editors` (IT-Group + admin.user): **all** admin sections (news/HR, HSE, certificates, Help Center,
  analytics, cancel any room booking). HR and HSE see only their own sections.
- HSE `/hse`: days without LTI (from the last LTI date HSE enters), record, man-hours, safety moment; hazard / near-miss
  reports by anyone (anonymous = no name stored), photos private under `uploads/hse/`; mail to `HSE_MAIL` when mail works.
- Certificates `/training`: types (10 seeded, editable), records per person (objectGUID), scans private under
  `uploads/certs/`, dashboard, matrix, Excel import; reminders 60/30/7/0 days with `CERT_ALERTS=1` + mail.
- Help Center `/help`: public read (also for people who cannot log in), 5 starter articles seeded on first start.
- Service accounts (2026-10-31, passwords in ops `portal.env`, swarm secrets): `svc-intranet` (mailbox `intranet@`,
  hidden, only EWS + SMTP; Send As `hrnews@`) → weekly e-mail, HSE/certificate mails, room booking;
  `svc-intranet-ad` → write telephoneNumber, mobile, physicalDeliveryOfficeName, thumbnailPhoto, ipPhone on users under
  OU=Company (ACL backup `<ops secrets store>`). Both: password never expires.
  `svc-intranet-hr` (2026-11-03) → write title, department, company, manager on users under OU=Company (HR People page,
  /admin/people); password = Docker secret `portal_ad_hr_write_password` (AD_HR_WRITE_PASSWORD in ops portal.env).
- My profile `/me` (replaces the SSO "My account" tile): own phone, mobile, office, photo → AD; DN from the token's user
  name only; table `profile_changes` logs every change. Links: SSO 2FA, password help, certificates, notifications.
- Push: Web Push/VAPID (key pair generated once in table `settings`), service worker `/sw.js`, manifest (installable);
  sent on news publish and banner switch-on; table `push_subs`. iPhone: only when added to the home screen.
- Analytics `/admin/analytics` (Intranet-IT-Editors): page views with salted user hash, department, language, device;
  400 days.
- 3CX (`threecx.py`): presence dots + click-to-call + hourly sync (AD ipPhone ← extension, 3CX company phonebook ←
  AD mobiles/phones, tag `AD-sync`), needs XAPI client → `THREECX_CLIENT_ID` + swarm secret `portal_3cx_secret`
  (`THREECX_SECRET_FILE`); `THREECX_SYNC` dryrun → apply after reviewing the log.
- Room booking: meeting created in the `intranet@` calendar (room = resource, booker = attendee) via EWS; table
  `room_bookings`; limits 07:00–21:00, ≤ 4 h, ≤ 60 days ahead, ≤ 10 upcoming per person.
- Pipeline: `.github/workflows/portal.yml` builds ghcr.io/OWNER/portal:<sha>, the runner job pins it in
  `stacks/portal/stack.yml` (commit by ci) and deploys.

## Rule: authorisation groups live in AD
Keycloak holds no roles/groups of its own for apps; it mirrors AD groups (read-only LDAP group mapper, recursive) and
passes them in tokens. Apps check AD group names. Cloud only provisions AD groups named `NC-*`.

