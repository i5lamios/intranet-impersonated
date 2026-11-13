TinyMCE 8.10.1 (npm `tinymce`), GPLv2+ (`license_key: 'gpl'`, internal self-hosted use) — minified subset:
core, dom model, silver theme, default icons, oxide skin, plugins used by src/lib/editor.ts.
`langs/az.js`, `langs/ru.js` from npm `tinymce-i18n` (langs8); wrong labels are overridden in src/lib/editor.ts (`AZ_FIX`).
Upgrade: replace these files from the new npm tarballs, keep the same subset.
