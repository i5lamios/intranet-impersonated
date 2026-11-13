# Intranet frontend

TypeScript + React 19 + React Router 7, built with Vite. The portal image builds it (`apps/portal/Dockerfile`, stage `web`)
and serves `dist/` as `app/static`; the API and URLs are unchanged.

- `src/main.tsx`: sign-in check (Keycloak), routes. `src/components/Layout.tsx`: header, menu, banner.
- `src/pages/*`: one file per area (News, People, Rooms, Hse, Training, Help, Admin, Profile...).
- `src/lib/*`: API calls, translations (`dict.ts`, English key → ru / az), Keycloak, push, passkeys, TinyMCE editor.
- Styles: `src/app.css` (class names as before) + `/brand.css` from `branding/` (mounted by the stack).
- `public/`: service worker, Keycloak silent check page, manifest, TinyMCE (self-hosted, GPL).

Local: `npm ci && npm run build` (type check + build). Node 20. Server HTML (news, help, safety moment) is sanitised by the API
before it is shown with `dangerouslySetInnerHTML`.
