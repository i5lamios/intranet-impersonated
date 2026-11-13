// HR admin (AD group Intranet-HR-Editors): news + editor, people (AD job data), birthdays, emergency banner, weekly e-mail.
import {useEffect, useMemo, useRef, useState} from 'react';
import {Link, useNavigate, useParams} from 'react-router';
import {api, fail, upload} from '../lib/api';
import {useEditor} from '../lib/editor';
import {fmtDate, lang, monthName, norm, t, ymd} from '../lib/i18n';
import {guard, session} from '../lib/session';
import {toast} from '../lib/toast';
import {ErrorPanel, Modal, NeedRole, Tabs, useLoad} from '../components/ui';
import {fileSize, type News} from './News';

// One admin area. Sections follow AD groups: HR = Intranet-HR-Editors, HSE = Intranet-HSE-Editors,
// IT = Intranet-IT-Editors (IT also sees every section — the role check is done by the API too).
type Section = {key: 'news' | 'hse' | 'it'; icon: string; name: string; group: string; items: [string, string, string][]};
export const SECTIONS = (): Section[] => [
  {key: 'news', icon: '📰', name: t('HR & communications'), group: 'Intranet-HR-Editors', items: [
    ['/admin/news', t('News'), t('Write, publish and pin news')], ['/admin/people', t('People'), t('Job title, department, manager in AD')],
    ['/admin/birthdays', t('Birthdays'), t('Dates and who is shown')],
    ['/admin/banner', t('Emergency banner'), t('Red banner on every page + push')], ['/admin/email', t('Weekly e-mail'), t('Digest to all staff')]]},
  {key: 'hse', icon: '🦺', name: t('HSE'), group: 'Intranet-HSE-Editors', items: [
    ['/admin/hse/reports', t('Hazard reports'), t('Review and close staff reports')], ['/admin/hse', t('HSE board'), t('LTI date, targets, message')],
    ['/admin/training', t('Certificates'), t('Expiry dashboard and editing')], ['/admin/training/matrix', t('Training matrix'), t('Who holds what')],
    ['/admin/training/types', t('Certificate types'), t('Types and validity')]]},
  {key: 'it', icon: '🖥️', name: t('IT'), group: 'Intranet-IT-Editors', items: [
    ['/admin/help', t('Help Center articles'), t('Instructions in en / ru / az')], ['/admin/rooms', t('Meeting rooms'), t('Room usage and door QR signs')], ['/admin/analytics', t('Usage analytics'), t('Who uses the intranet')],
    ['/admin/audit', t('Audit log'), t('Who changed what')]]},
];
export const mySections = () => SECTIONS().filter(x => session.me?.roles[x.key]);
// the cheat sheet (Help Center, category "admin", editors only) for each admin page
const guide = (cur: string) => cur.startsWith('/admin/news') ? 'admin-news' : cur.startsWith('/admin/hse') ? 'admin-hse'
  : cur.startsWith('/admin/people') ? 'admin-people' : cur.startsWith('/admin/training') ? 'admin-training' : /^\/admin\/(help|analytics|audit|rooms)/.test(cur) ? 'admin-it' : 'admin-hr';
export function AdminTabs({cur}: {cur: string}) {
  const secs = mySections(), here = secs.find(x => x.items.some(([h]) => cur === h || cur.startsWith(h + '/'))) || secs[0];
  if (!here) return null;
  const on = here.items.map(([h]) => h).filter(h => cur === h || cur.startsWith(h + '/')).sort((a, b) => b.length - a.length)[0];
  return <>
    <div className="adminbar"><Link to="/admin" className="adm-home">⚙️ {t('Admin')}</Link>{secs.map(x =>
      <Link key={x.key} to={x.items[0][0]} className={x === here ? 'on' : ''}>{x.icon} {x.name}</Link>)}
      <Link className="adm-help" to={`/help/${guide(cur)}`} title={t('Admin guides')}>? {t('How to')}</Link></div>
    <Tabs items={here.items.map(([h, l]) => [h, l])} cur={on} />
  </>;
}

export function AdminHome() {
  const secs = mySections();
  if (!secs.length) return <NeedRole group="Intranet-HR-Editors / Intranet-HSE-Editors / Intranet-IT-Editors" />;
  return <><h1>⚙️ {t('Admin')}</h1><p className="muted">{t('Everything editors manage, in one place. You see the sections of your AD groups.')}</p>
    <div className="admgrid">{secs.map(x => <section key={x.key} className="admsec"><h2>{x.icon} {x.name}</h2><small className="muted">{t('AD group')} {x.group}</small>
      {x.items.map(([h, l, d]) => <Link key={h} className="admlink" to={h}><b>{l}</b><span>{d}</span></Link>)}</section>)}</div></>;
}

// HR pages: signed in + editor (the API checks again)
const HrOnly = ({children}: {children: React.ReactNode}) => session.me?.editor ? <>{children}</> : <NeedRole group="Intranet-HR-Editors" />;
const Pub = ({n}: {n: {published?: boolean}}) => n.published ? <span className="badge pub">{t('Published')}</span> : <span className="badge draft">{t('Draft')}</span>;

export const AdminList = () => <HrOnly><NewsAdminList /></HrOnly>;
function NewsAdminList() {
  const {data: news, error} = useLoad(() => api<(News & {emailed_at?: string})[]>('/api/news?limit=50&drafts=true'));
  if (error) return <ErrorPanel error={error} />;
  if (!news) return null;
  return <><AdminTabs cur="/admin/news" /><div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Manage news')}</h1>
    <Link className="btn" to="/admin/news/new">+ {t('New post')}</Link></div>
    <table className="list"><thead><tr><th>{t('Title')}</th><th>{t('Status')}</th><th>{t('Date')}</th><th></th></tr></thead><tbody>
      {news.length ? news.map(n => <tr key={n.id}><td><b>{n.title}</b></td><td><Pub n={n} />{n.emailed_at && <> <span className="badge" title={fmtDate(n.emailed_at)}>✉️ {t('E-mailed')}</span></>}
        {n.pinned && <span className="badge pin">{t('Pinned')}</span>}</td><td className="muted">{fmtDate(n.published_at || n.updated_at)}</td>
        <td><Link className="btn small ghost" to={`/admin/news/${n.id}`}>{t('Edit')}</Link></td></tr>)
        : <tr><td colSpan={4} className="empty">{t('No posts yet')}</td></tr>}</tbody></table></>;
}

type Version = {title?: string; summary?: string; body_html?: string};
type Att = {id: string; name: string; size: number};
type EditNews = News & {emailed_at?: string | null; layout?: string};
export const AdminEdit = () => <HrOnly><NewsEditor /></HrOnly>;
function NewsEditor() {
  const {id} = useParams(), nav = useNavigate(), isNew = id === 'new';
  const {data: n, error} = useLoad<EditNews>(() => isNew ? Promise.resolve({id: 0, title: '', summary: '', body_html: '', cover: null, pinned: false,
    published: false, lang: 'en', i18n: {}, layout: 'large'} as EditNews) : api<EditNews>('/api/news/' + id), [id]);
  // one version per language: the main one (n.lang) + optional translations (readers see their language, else the main one)
  const store = useRef<Record<string, Version>>({en: {}, ru: {}, az: {}});
  const [cur, setCur] = useState('en');
  const [cover, setCover] = useState<string | null>(null), [atts, setAtts] = useState<Att[]>([]);
  const [title, setTitle] = useState(''), [summary, setSummary] = useState('');
  const [ref, ed] = useEditor(n ? store.current[n.lang || 'en']?.body_html || n.body_html || '' : undefined, {people: true});
  const form = useRef<HTMLFormElement>(null);
  useEffect(() => {
    if (!n) return;
    store.current = {en: {}, ru: {}, az: {}};
    store.current[n.lang || 'en'] = {title: n.title, summary: n.summary, body_html: n.body_html};
    Object.entries(n.i18n || {}).forEach(([l, v]) => { if (store.current[l]) store.current[l] = {...v}; });
    const l = n.lang || 'en'; setCur(l); setTitle(store.current[l].title || ''); setSummary(store.current[l].summary || '');
    setCover(n.cover || null); setAtts([...(n.attachments || [])]);
  }, [n]);
  useEffect(() => { if (ed) guard.dirty = false; }, [ed]);
  if (error) return <ErrorPanel error={error} />;
  if (!n) return null;
  const dirty = () => { guard.dirty = true; };
  const keep = () => { store.current[cur] = {title, summary, body_html: ed?.getContent() ?? store.current[cur].body_html}; };
  const switchLang = (l: string) => { keep(); setCur(l); setTitle(store.current[l].title || ''); setSummary(store.current[l].summary || ''); ed?.setContent(store.current[l].body_html || ''); };
  const addFiles = async (files: FileList) => { for (const f of [...files]) { try { const a = await upload<Att>('/api/news/files', f); setAtts(x => [...x, a]); dirty(); } catch (err) { fail(err); } } };
  const mailTest = async () => {
    if (guard.dirty) return toast(t('Save the post first - the test shows the saved version'));
    try { const r = await api<{sent_to: string}>(`/api/news/${id}/mail-test`, {method: 'POST'}); toast(t('Sent to {to}', {to: r.sent_to})); } catch (err) { fail(err); }
  };
  const del = async () => { if (confirm(t('Delete this post?'))) { await api('/api/news/' + id, {method: 'DELETE'}); guard.dirty = false; toast(t('Deleted')); nav('/admin/news'); } };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget, published = ((e.nativeEvent as SubmitEvent).submitter as HTMLElement | null)?.dataset.pub === '1';
    if (!ed) return;
    await ed.uploadImages(); keep();
    const s = store.current;
    const filled = (l: string) => (s[l].title || '').trim().length >= 3 && /\S/.test((s[l].body_html || '').replace(/<(?!img)[^>]*>|&nbsp;/g, ' '));
    const main = [n.lang || 'en', 'en', 'az', 'ru'].find(filled);
    if (!main) return toast(t('Write a title and text in at least one language'));
    const emailBox = (f.elements.namedItem('email') as HTMLInputElement).checked, email = published && emailBox;
    if (emailBox && !published) return toast(t('Only published posts can be e-mailed'));
    if (email && !confirm(n.emailed_at ? t('This post was already e-mailed on {d}. Send it to all staff again?', {d: fmtDate(n.emailed_at)})
                                       : t('Send this post to all staff by e-mail now?'))) return;
    const i18n = Object.fromEntries(['en', 'ru', 'az'].filter(l => l !== main && filled(l)).map(l => [l, s[l]]));
    const val = (k: string) => (f.elements.namedItem(k) as HTMLInputElement);
    try {
      const r = await api<{id: number; mail_error?: string; emailed?: string}>(isNew ? '/api/news' : '/api/news/' + id, {method: isNew ? 'POST' : 'PUT',
        json: {title: s[main].title, summary: s[main].summary, body_html: s[main].body_html, lang: main, i18n,
               layout: n.layout || 'large', news_date: val('ndate').value || null, cover, pinned: val('pinned').checked, published, email, attachments: atts}});
      guard.dirty = false;
      if (r.mail_error) alert(t('Saved, but the e-mail was not sent: {e}', {e: r.mail_error}));
      else toast(r.emailed ? t('Published and e-mailed to {to}', {to: r.emailed}) : published ? t('Published') : t('Draft saved'));
      nav('/news/' + r.id);
    } catch (err) { fail(err); }
  };
  return <>
    <div className="row" style={{justifyContent: 'space-between', marginTop: 20}}>
      <Link to="/admin/news" className="muted">← {t('All posts')}</Link>
      <span className="row"><a className="adm-help" href="/help/admin-news" target="_blank" rel="noopener" title={t('Admin guides')}>? {t('How to')}</a><Pub n={n} /></span></div>
    <form id="f" className="editor" ref={form} onInput={dirty} onSubmit={submit}>
      <div className="sheet"><div className="tabs" id="lt">{['en', 'ru', 'az'].map(l =>
        <a key={l} href="#" className={l === cur ? 'on' : ''} onClick={e => { e.preventDefault(); switchLang(l); }}>{l.toUpperCase()}{l === (n.lang || 'en') ? ' ★' : ''}</a>)}</div>
        <input name="title" className="doc-title" maxLength={200} placeholder={t('Title')} value={title} onChange={e => setTitle(e.target.value)} /><textarea id="body" ref={ref} /></div>
      <aside className="side">
        <div className="panel"><b>{t('Publish')}</b>
          <button type="submit" className="btn" data-pub="1">{n.published ? t('Update') : t('Publish')}</button>
          <button type="submit" className="btn ghost" data-pub="0">{n.published ? t('Unpublish') : t('Save draft')}</button>
          <label className="ndate">{t('News date')}<input type="date" name="ndate" max={ymd(new Date())} defaultValue={n.published_at ? ymd(new Date(n.published_at)) : ''} /></label>
          <small className="muted">{t('Empty = the day it is published. Use an earlier date for older announcements.')}</small>
          <label className="check"><input type="checkbox" name="pinned" defaultChecked={n.pinned} /> {t('Pin to top')}</label>
          <label className="check"><input type="checkbox" name="email" /> ✉️ {t('E-mail to all staff')}</label>
          <small className="muted">{n.emailed_at ? t('E-mailed on {d}', {d: fmtDate(n.emailed_at)}) + ' · ' : ''}{t('Sent with Publish / Update, all languages in one e-mail')}</small>
          {!isNew && <button type="button" className="btn ghost small" id="mtest" onClick={mailTest}>{t('Send a test to me')}</button>}</div>
        <div className="panel"><b>{t('Cover picture')}</b><div id="cov" className="coverpick">{cover ? <img src={cover} alt="" /> : <span className="muted">{t('None')}</span>}</div>
          <div className="row"><label className="btn ghost small">{t('Choose')}<input type="file" accept="image/*" hidden onChange={async e => {
              const file = e.target.files?.[0]; if (file) { try { setCover((await upload<{url: string}>('/api/uploads', file)).url); dirty(); } catch (err) { fail(err); } } }} /></label>
            {cover && <button type="button" className="btn ghost small" onClick={() => { setCover(null); dirty(); }}>{t('Remove')}</button>}</div>
          <small className="muted">{t('If empty, the first picture in the text is used')}</small></div>
        <div className="panel"><b>📎 {t('Attachments')}</b><div id="atts">{atts.map((a, i) => <div className="attrow" key={a.id}><span>📄 {a.name} <small className="muted">{fileSize(a.size)}</small></span>
          <button type="button" className="btn ghost small" title={t('Remove')} onClick={() => { setAtts(x => x.filter((_, j) => j !== i)); dirty(); }}>✕</button></div>)}</div>
          <label className="btn ghost small">{t('Add files')}<input type="file" multiple hidden accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.jpg,.jpeg,.png"
            onChange={async e => { if (e.target.files) await addFiles(e.target.files); e.target.value = ''; }} /></label>
          <small className="muted">{t('Shown under the post and attached to the e-mail. Max 15 MB per file, 20 MB in total.')}</small></div>
        <div className="panel"><b>{t('Summary')}</b>
          <textarea name="summary" maxLength={500} rows={4} placeholder={t('If empty, the start of the text')} value={summary} onChange={e => setSummary(e.target.value)} /></div>
        <p className="muted">{t('★ = main language. Write the other languages in their tabs; empty ones show the main version.')}</p>
        {!isNew && <button type="button" className="btn danger" id="del" onClick={del}>{t('Delete post')}</button>}
      </aside></form>
  </>;
}

type Bd = {id: string; name: string; department?: string; username?: string; day?: number | null; month?: number | null; year?: number | null};
export const AdminBirthdays = () => <HrOnly><Birthdays /></HrOnly>;
function Birthdays() {
  const {data, error, reload} = useLoad(() => api<Bd[]>('/api/admin/birthdays'));
  const [q, setQ] = useState(''), [miss, setMiss] = useState(false), [imp, setImp] = useState(''), [res, setRes] = useState('');
  const [, redraw] = useState(0);
  const years = useMemo(() => Array.from({length: new Date().getFullYear() - 1940 + 1}, (_, i) => new Date().getFullYear() - i), []);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const all = data, w = norm(q);
  const save = async (p: Bd, tr: HTMLTableRowElement) => {
    const v = (c: string) => +(tr.querySelector<HTMLSelectElement>(c)!.value) || null;
    const d = v('.bd'), m = v('.bm'), y = v('.by');
    if ((d && !m) || (m && !d)) return;
    try { await api('/api/admin/birthdays/' + p.id, {method: 'PUT', json: {day: d, month: m, year: d ? y : null}}); Object.assign(p, {day: d, month: m, year: y}); redraw(x => x + 1); toast(t('Saved')); } catch (err) { fail(err); }
  };
  const doImport = async () => { try {
    const r = await api<{saved: number; not_found: string[]; invalid: string[]}>('/api/admin/birthdays/import', {method: 'POST', json: {text: imp}});
    setRes(t('{n} saved', {n: r.saved}) + (r.not_found.length ? `; ${t('not found')}: ${r.not_found.join(', ')}` : '') + (r.invalid.length ? `; ${t('bad date')}: ${r.invalid.join(', ')}` : ''));
    if (r.saved) reload(); } catch (err) { fail(err); } };
  return <><AdminTabs cur="/admin/birthdays" /><h1>{t('Birthdays')}</h1>
    <p className="muted">{t('The year is optional and visible only here; staff see day and month only.')} {t('{a} of {b} filled.', {a: all.filter(p => p.month).length, b: all.length})}</p>
    <details className="panel"><summary><b>{t('Paste from Excel')}</b></summary>
      <p className="muted">{t('Two columns: user name, e-mail or full name, and the date (15.03 or 15.03.1990)')}</p>
      <textarea id="imp" rows={8} style={{width: '100%'}} placeholder={'admin.user\t15.03.1990'} value={imp} onChange={e => setImp(e.target.value)} />
      <div className="row"><button className="btn" id="impb" onClick={doImport}>{t('Import')}</button><span id="impr" className="muted">{res}</span></div></details>
    <div className="filters"><input id="bq" placeholder={t('Filter')} value={q} onChange={e => setQ(e.target.value)} />
      <label className="check"><input type="checkbox" checked={miss} onChange={e => setMiss(e.target.checked)} /> {t('Only missing')}</label></div>
    <table className="list"><thead><tr><th>{t('Name')}</th><th>{t('Department')}</th><th>{t('Birthday')}</th></tr></thead><tbody id="brows">
      {all.filter(p => (!w || norm(p.name + ' ' + p.department + ' ' + p.username).includes(w)) && (!miss || !p.month)).map(p =>
        <tr key={p.id} onChange={e => save(p, e.currentTarget)}><td><b>{p.name}</b></td><td className="muted">{p.department}</td><td><div className="row" style={{gap: 6}}>
          <select className="bd" defaultValue={p.day ?? ''}><option value="">—</option>{Array.from({length: 31}, (_, i) => <option key={i} value={i + 1}>{i + 1}</option>)}</select>
          <select className="bm" defaultValue={p.month ?? ''}><option value="">—</option>{Array.from({length: 12}, (_, i) => <option key={i} value={i + 1}>{monthName(i + 1)}</option>)}</select>
          <select className="by" aria-label={t('Year')} defaultValue={p.year ?? ''}><option value="">{t('Year')}</option>{years.map(y => <option key={y} value={y}>{y}</option>)}</select></div></td></tr>)}</tbody></table></>;
}

type Banner = {text: string; level: string; active: boolean; until?: string | null};
export const AdminBanner = () => <HrOnly><BannerAdmin /></HrOnly>;
function BannerAdmin() {
  const {data: b, error} = useLoad(() => api<Banner>('/api/admin/banner'));
  if (error) return <ErrorPanel error={error} />;
  if (!b) return null;
  const local = (s?: string | null) => s ? new Date(new Date(s).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '';
  const submit = async (e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); const f = e.currentTarget.elements as any;
    try { await api('/api/admin/banner', {method: 'PUT', json: {text: f.text.value, level: f.level.value, active: f.active.checked,
      until: f.until.value ? new Date(f.until.value).toISOString() : null}}); toast(t('Saved')); sessionStorage.removeItem('banner-closed'); window.dispatchEvent(new Event('banner')); }
    catch (err) { fail(err); } };
  return <><AdminTabs cur="/admin/banner" /><h1>{t('Emergency banner')}</h1>
    <p className="muted">{t('Shown at the top of every intranet page')}</p>
    <form id="bf" className="panel stack" style={{maxWidth: 720}} onSubmit={submit}>
      <label>{t('Text')}<textarea name="text" rows={3} maxLength={500} defaultValue={b.text} /></label>
      <div className="row"><label>{t('Type')}<select name="level" defaultValue={b.level}>{[['info', 'ℹ️ ' + t('Info')], ['warning', '❗ ' + t('Warning')], ['danger', '⚠️ ' + t('Emergency')]].map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></label>
        <label>{t('Until')} <small className="muted">({t('empty = until switched off')})</small><input type="datetime-local" name="until" defaultValue={local(b.until)} /></label></div>
      <label className="check"><input type="checkbox" name="active" defaultChecked={b.active} /> <b>{t('Show the banner')}</b></label>
      <div className="row"><button className="btn">{t('Save')}</button></div></form></>;
}

type Digest = {on: boolean; configured: boolean; weekday: number; hour: number; from: string; to: string; items: number; html: string;
  log: {week: string; status: string; items: number; sent_at: string; error?: string}[]};
export const AdminEmail = () => <HrOnly><EmailAdmin /></HrOnly>;
function EmailAdmin() {
  const {data: d, error, reload} = useLoad(() => api<Digest>('/api/admin/digest'));
  if (error) return <ErrorPanel error={error} />;
  if (!d) return null;
  const st: Record<string, string> = {sent: t('sent'), empty: t('no news'), failed: t('failed'), sending: t('sending')};
  const wd = new Date(2024, 0, 1 + d.weekday).toLocaleDateString(lang, {weekday: 'long'});   // 2024-01-01 = Monday
  const toggle = async (e: React.ChangeEvent<HTMLInputElement>) => { const on = e.target.checked;
    try { await api('/api/admin/digest', {method: 'PUT', json: {on}}); toast(on ? t('Weekly e-mail is on') : t('Weekly e-mail is off')); reload(); } catch (err) { fail(err); } };
  const test = async () => { try { const r = await api<{sent_to: string}>('/api/admin/digest/test', {method: 'POST'}); toast(t('Sent to {to}', {to: r.sent_to})); } catch (err) { fail(err); } };
  return <><AdminTabs cur="/admin/email" /><h1>{t('Weekly e-mail')}</h1>
    <div className="panel stack"><div className="row" style={{alignItems: 'center', gap: 12}}>
      <label className="switch"><input type="checkbox" id="don" checked={d.on} onChange={toggle} /><span></span></label>
      <b>{d.on ? t('Weekly e-mail is on') : t('Weekly e-mail is off')}</b>
      {!d.configured && <span className="badge draft">{t('Mail account not configured')}</span>}</div>
      <div>{t('Every {day} at {h}:00', {day: wd, h: d.hour})} — <b>{d.from}</b> → <b>{d.to}</b></div>
      <div className="muted">{t('News published since the last e-mail; nothing is sent if there are none.')}</div>
      <div className="row"><button className="btn ghost" id="test" disabled={!d.items} onClick={test}>{t('Send a test to me')}</button><span className="muted">{t('{n} posts in the next e-mail', {n: d.items})}</span></div>
      {d.log.length > 0 && <table className="list"><tbody>{d.log.map((l, i) => <tr key={i}><td>{l.week}</td><td>{st[l.status] || l.status}</td><td>{l.items}</td>
        <td className="muted">{fmtDate(l.sent_at)}{l.error ? ' — ' + l.error : ''}</td></tr>)}</tbody></table>}</div>
    <h2>{t('Preview')}</h2><iframe id="pv" className="mailpv" sandbox="" srcDoc={d.html} /></>;
}

// People: HR keeps job title, department, company, manager, office and phones in AD (written by the API with
// limited service accounts; the Directory, Outlook and the org chart read them from AD)
type HrP = {id: string; name: string; username: string; mail?: string; title?: string; department?: string; company?: string; office?: string;
  phone?: string; mobile?: string; manager?: string | null; configured: boolean};
export const AdminPeople = () => <HrOnly><PeopleAdmin /></HrOnly>;
function PeopleAdmin() {
  const {data: all, error} = useLoad(() => api<HrP[]>('/api/hr/people'));
  const [q, setQ] = useState(''), [miss, setMiss] = useState(false), [edit, setEdit] = useState<HrP | null>(null);
  const [, redraw] = useState(0);
  if (error) return <ErrorPanel error={error} />;
  if (!all) return null;
  const byId = Object.fromEntries(all.map(p => [p.id, p]));
  const missing = (p: HrP) => !p.title || !p.department || !p.manager;
  const gap = <span className="badge draft">{t('missing')}</span>, w = norm(q);
  return <><AdminTabs cur="/admin/people" /><h1>{t('People')}</h1>
    <p className="muted">{t('Job data comes from Active Directory. Changes here are saved to AD and show in the Directory, Outlook and the org chart within a minute.')}</p>
    {all.length > 0 && !all[0].configured && <div className="panel" style={{borderColor: 'var(--sc-red)'}}>{t('Saving is not switched on yet - IT has to finish the AD setup.')}</div>}
    <div className="filters"><input id="pq" placeholder={t('Name, title, department')} value={q} onChange={e => setQ(e.target.value)} />
      <label className="check"><input type="checkbox" checked={miss} onChange={e => setMiss(e.target.checked)} /> {t('Needs attention')} ({all.filter(missing).length})</label></div>
    <table className="list"><thead><tr><th>{t('Name')}</th><th>{t('Job title')}</th><th>{t('Department')}</th><th>{t('Manager')}</th><th></th></tr></thead><tbody id="prows">
      {all.filter(p => (!miss || missing(p)) && (!w || norm([p.name, p.title, p.department, p.username].join(' ')).includes(w))).map(p => <tr key={p.id}>
        <td><b>{p.name}</b><br /><small className="muted">{p.mail || p.username}</small></td><td>{p.title || gap}</td>
        <td>{p.department || gap}</td><td>{p.manager && byId[p.manager] ? byId[p.manager].name : gap}</td>
        <td><button className="btn ghost small" onClick={() => setEdit(p)}>{t('Edit')}</button></td></tr>)}</tbody></table>
    <datalist id="mgrs">{all.map(p => <option key={p.id} value={p.name} />)}</datalist>
    {edit && <EditPerson p={edit} byId={byId} onClose={() => setEdit(null)} onSaved={() => redraw(x => x + 1)} />}</>;
}

function EditPerson({p, byId, onClose, onSaved}: {p: HrP; byId: Record<string, HrP>; onClose: () => void; onSaved: () => void}) {
  const [hist, setHist] = useState<React.ReactNode>(null);
  const Fld = ({k, l, v, ...attrs}: {k: string; l: string; v?: string | null} & React.InputHTMLAttributes<HTMLInputElement>) =>
    <label>{l}<input name={k} defaultValue={v || ''} {...attrs} /></label>;
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any, mname = f.manager.value.trim();
    const mgr = mname ? Object.values(byId).filter(x => x.name === mname) : [];
    if (mname && mgr.length !== 1) return toast(mgr.length ? t('Several people have this name - ask IT') : t('Choose the manager from the list'));
    const now: Record<string, string> = {title: f.title.value, department: f.department.value, company: f.company.value, manager: mgr[0] ? mgr[0].id : '',
      office: f.office.value, phone: f.phone.value, mobile: f.mobile.value};
    // send only what HR changed (the list shows phones without "+", so unchanged fields must not be written back)
    const json = Object.fromEntries(Object.entries(now).filter(([k, v]) => v.trim() !== String((p as any)[k] || '').trim()));
    if (!Object.keys(json).length) { onClose(); return toast(t('Nothing changed')); }
    try {
      const r = await api<{changed: string[]}>('/api/hr/people/' + p.id, {method: 'PUT', json});
      Object.assign(p, json); onClose(); onSaved(); toast(r.changed.length ? t('Saved to AD') : t('Nothing changed'));
    } catch (err) { fail(err); }
  };
  const history = async (e: React.SyntheticEvent<HTMLDetailsElement>) => { if (!e.currentTarget.open) return;
    const h = await api<{changed_at: string; changed_by: string; field: string; old_value?: string; new_value?: string}[]>(`/api/hr/people/${p.id}/history`).catch(() => []);
    setHist(h.length ? h.map((x, i) => <div key={i}>{x.changed_at.replace('T', ' ')} · <b>{x.changed_by}</b> · {x.field}: {x.old_value || '—'} → {x.new_value || '—'}</div>) : t('No changes yet')); };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{p.name}</h2><form id="pf" className="stack" onSubmit={submit}>
    <Fld k="title" l={t('Job title')} v={p.title} maxLength={128} />
    <div className="row"><Fld k="department" l={t('Department')} v={p.department} maxLength={64} list="deps" /><Fld k="company" l={t('Company')} v={p.company} maxLength={64} /></div>
    <Fld k="manager" l={t('Manager')} v={p.manager && byId[p.manager] ? byId[p.manager].name : ''} list="mgrs" autoComplete="off" />
    <div className="row"><Fld k="office" l={t('Office')} v={p.office} maxLength={128} /><Fld k="phone" l={t('Office phone')} v={p.phone} maxLength={40} /><Fld k="mobile" l={t('Mobile')} v={p.mobile} maxLength={40} /></div>
    <datalist id="deps">{[...new Set(Object.values(byId).map(x => x.department).filter(Boolean))].sort().map(d => <option key={d} value={d!} />)}</datalist>
    <div className="row"><button className="btn">{t('Save to AD')}</button><button type="button" className="btn ghost" data-close>{t('Close')}</button></div>
    <details onToggle={history}><summary className="muted">{t('History')}</summary><div id="ph" className="muted">{hist}</div></details></form></Modal>;
}
