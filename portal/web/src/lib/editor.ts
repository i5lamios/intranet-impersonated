// @ts-nocheck — TinyMCE is a global script (/vendor/tinymce), not typed here
// Word-like editor (TinyMCE 8, self-hosted under /vendor/tinymce, GPL). The server sanitises the HTML again.
import {useEffect, useRef, useState} from 'react';
import {api, upload} from './api';
import {lang, norm, t} from './i18n';
import {guard} from './session';
import {theme} from './theme';

const esc = (v: unknown) => String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const initials = (n: string) => esc((n || '?').split(/\s+/).map(w => w[0]).slice(0, 2).join('').toUpperCase());
// a plain modal outside React (opened from inside TinyMCE)
const modal = (html: string) => {
  const m = document.createElement('div'); m.className = 'modal';
  m.innerHTML = `<div class="modal-box">${html}</div>`;
  m.addEventListener('click', e => { if (e.target === m || e.target.closest('[data-close]')) m.remove(); });
  document.body.append(m); return m;
};

const TINY = '/vendor/tinymce';
const AZ_FIX = {   // community az pack: wrong or missing labels
  'Insert table': 'Cədvəl əlavə et', 'Bullet list': 'Markerli siyahı', 'Numbered list': 'Nömrəli siyahı',
  'Align left': 'Sola', 'Align center': 'Mərkəzə', 'Align right': 'Sağa', 'Justify': 'Eninə', 'Image': 'Şəkil',
  'Upload': 'Yüklə', 'Words': 'Söz', 'Insert/edit image': 'Şəkil əlavə et', 'Insert/edit link': 'Keçid əlavə et',
  'Background color': 'Fon rəngi', 'Decrease indent': 'Girintini azalt', 'Increase indent': 'Girintini artır',
  'Undo': 'Geri al', 'Redo': 'Təkrarla', 'Fullscreen': 'Tam ekran', 'Strikethrough': 'Üstüxətli', 'Blocks': 'Üslub',
  'Insert row before': 'Yuxarıya sətir', 'Insert row after': 'Aşağıya sətir', 'Delete row': 'Sətri sil',
  'Insert column before': 'Sola sütun', 'Insert column after': 'Sağa sütun', 'Delete column': 'Sütunu sil',
};
const BLOCKS = {
  en: 'Paragraph=p; Heading=h2; Subheading=h3; Small heading=h4; Quote=blockquote',
  ru: 'Абзац=p; Заголовок=h2; Подзаголовок=h3; Малый заголовок=h4; Цитата=blockquote',
  az: 'Mətn=p; Başlıq=h2; Alt başlıq=h3; Kiçik başlıq=h4; Sitat=blockquote',
};
const dark = () => theme() === 'dark';
const PLACEHOLDER = {en: 'Type here or paste from Word', ru: 'Введите текст или вставьте из Word', az: 'Mətni burada yazın və ya Word-dən yapışdırın'};
const loadScript = src => new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.append(s); });
const loaded = new Set();
async function loadTiny() {
  if (!window.tinymce) await loadScript(TINY + '/tinymce.min.js');
  if (lang !== 'en' && !loaded.has(lang)) {
    await loadScript(`${TINY}/langs/${lang}.js`); loaded.add(lang);
    if (lang === 'az') tinymce.addI18n('az', AZ_FIX);
  }
  return window.tinymce;
}

export async function createEditor(target, html, {minHeight = 520, simple = false, people = false} = {}) {
  const tiny = await loadTiny();
  const [ed] = await tiny.init({
    target, license_key: 'gpl', base_url: TINY, suffix: '.min', language: lang === 'en' ? undefined : lang,
    promotion: false, branding: false, menubar: false, statusbar: !simple, elementpath: false, resize: false,
    plugins: 'lists advlist link autolink image table wordcount autoresize fullscreen searchreplace charmap',
    toolbar: simple ? 'undo redo | blocks | bold italic underline | bullist numlist | link image | removeformat'
      : `undo redo | blocks | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image table${people ? ' person' : ''} | charmap searchreplace removeformat | fullscreen`,
    toolbar_mode: 'wrap', toolbar_sticky: true, block_formats: BLOCKS[lang],
    // no text / background colours: they clash with the dark theme (and the server removes them anyway)
    min_height: minHeight, autoresize_bottom_margin: 40,
    skin: dark() ? 'oxide-dark' : 'oxide', content_css: TINY + `/skins/content/${dark() ? 'dark' : 'default'}/content.min.css`,
    content_style: 'body{font-family:"Segoe UI",Arial,sans-serif;font-size:16px;line-height:1.65;color:#1f2937;margin:16px 4px}' +
      'img{max-width:100%;height:auto;border-radius:6px}h2,h3,h4{color:#1B2B5B}blockquote{border-left:4px solid #2E6DB4;margin:0;padding:4px 16px;color:#6b7280}' +
      'table{border-collapse:collapse}td,th{border:1px solid #d6dde8;padding:6px 10px}' +
      // dark theme: the same colours as an article on the dark site
      (dark() ? 'body{background:#18202b;color:#e3e8ef}h2,h3,h4{color:#c9d6f3}a{color:#6fa8f2}blockquote{border-left-color:#6fa8f2;color:#9aa7b6}td,th{border-color:#2b3546}' : ''),
    placeholder: PLACEHOLDER[lang], relative_urls: false, remove_script_host: true,
    link_default_target: '_blank', link_assume_external_targets: 'https', link_target_list: false, link_title: false,
    image_description: true, image_dimensions: false, image_title: false, object_resizing: 'img',
    automatic_uploads: true, images_file_types: 'jpg,jpeg,png,gif,webp,bmp',
    images_upload_handler: async blob => (await upload('/api/uploads', blob.blob())).url,
    table_default_styles: {'border-collapse': 'collapse', width: '100%'}, table_default_attributes: {},
    table_advtab: false, table_cell_advtab: false, table_row_advtab: false, table_appearance_options: false,
    setup: e => {
      e.on('input change undo redo', () => { guard.dirty = true; });
      if (people) e.ui.registry.addButton('person', {icon: 'user', text: t('Colleague'), tooltip: t('Insert a colleague from the Directory'), onAction: () => pickPerson(e)});
    },
  });
  ed.setContent(html || ''); ed.undoManager.clear();
  return ed;
}
export const destroyEditors = () => { if (window.tinymce) tinymce.remove(); };
export const isEmpty = ed => !ed.getContent({format: 'text'}).trim() && !ed.getBody().querySelector('img');

// News: a colleague from the Directory as a person card (the article shows it with the photo):
// <h3><a href="/directory/ID">Name</a></h3><p><strong>Title</strong>, Department.</p>
let dir = null;
async function pickPerson(ed) {
  const bm = ed.selection.getBookmark(2, true);
  const m = modal(`<h2 style="margin-top:0">${t('Insert a colleague from the Directory')}</h2>
    <input id="pp" autocomplete="off" placeholder="${t('Type a name…')}" style="width:100%"><div class="pplist" id="ppl"></div>
    <div class="row" style="margin-top:12px"><button type="button" class="btn ghost" data-close>${t('Close')}</button></div>`);
  const q = m.querySelector('#pp'), l = m.querySelector('#ppl');
  q.focus();
  if (!dir) dir = (await api('/api/directory')).people;
  const draw = () => {
    const w = norm(q.value).trim();
    const hits = w.length < 2 ? [] : dir.filter(p => norm([p.name, p.title, p.department].join(' ')).includes(w)).slice(0, 10);
    l.innerHTML = hits.map((p, i) => `<button type="button" data-i="${dir.indexOf(p)}"><span class="av">${initials(p.name)}</span>
      <span><b>${esc(p.name)}</b><small>${esc([p.title, p.department].filter(Boolean).join(' · '))}</small></span></button>`).join('');
  };
  q.oninput = draw;
  q.onkeydown = e => { if (e.key === 'Enter') { e.preventDefault(); const b = l.querySelectorAll('[data-i]'); if (b.length === 1) b[0].click(); } };
  l.onclick = e => {
    const b = e.target.closest('[data-i]'); if (!b) return;
    const p = dir[+b.dataset.i], role = [p.title ? `<strong>${esc(p.title)}</strong>` : '', esc(p.department || '')].filter(Boolean).join(', ');
    m.remove(); ed.focus(); ed.selection.moveToBookmark(bm);
    ed.insertContent(`<h3><a href="/directory/${esc(p.id)}">${esc(p.name)}</a></h3><p>${role ? role + '.' : '&nbsp;'}</p><p>&nbsp;</p>`);
    guard.dirty = true;
  };
}

// React: a TinyMCE editor on a <textarea ref>; removed when the component goes away
export type TinyEditor = {getContent(o?: object): string; setContent(html: string): void; uploadImages(): Promise<unknown>; remove(): void};
export function useEditor(html: string | undefined, opts: {minHeight?: number; simple?: boolean; people?: boolean} = {}):
    [React.RefObject<HTMLTextAreaElement | null>, TinyEditor | null] {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [ed, setEd] = useState<TinyEditor | null>(null);
  useEffect(() => {
    if (html === undefined || !ref.current) return;
    let live = true, inst = null;
    createEditor(ref.current, html, opts).then(e => { inst = e; if (live) setEd(e); else e.remove(); });
    return () => { live = false; inst?.remove(); guard.dirty = false; };
  }, [html === undefined]);
  return [ref, ed];
}
