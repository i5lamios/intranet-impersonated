// IT Help Center: how-to articles in en / ru / az (edited by Intranet-IT-Editors).
import {useEffect, useRef, useState} from 'react';
import {Link, useNavigate, useParams} from 'react-router';
import {api, fail} from '../lib/api';
import {useEditor} from '../lib/editor';
import {fmtDate, lang, norm, pick, t, type Localised} from '../lib/i18n';
import {guard, session} from '../lib/session';
import {toast} from '../lib/toast';
import {ErrorPanel, NeedRole, useLoad} from '../components/ui';
import {AdminTabs} from './Admin';

const CATS = (): Record<string, [string, string]> => ({apps: ['🧭', t('Intranet & apps')], accounts: ['🔑', t('Accounts & passwords')], mail: ['✉️', t('E-mail & phone')],
  remote: ['🌐', t('Remote access & VPN')], devices: ['💻', t('Computers & printers')], security: ['🛡️', t('Security')], support: ['🛠️', t('Getting help')],
  admin: ['⚙️', t('Admin guides')]});      // admin = editors only (the API hides it from others)
type Article = {slug: string; category: string; sort: number; title: Record<string, string>; body: Record<string, string>; published: boolean; updated_at: string};

export function HelpHome() {
  const {data: items, error} = useLoad(() => api<Article[]>('/api/help'));
  const [q, setQ] = useState('');
  const sent = useRef(new Set<string>()), missT = useRef<number>(0);
  const w = norm(q), C = CATS();
  const hits = (items || []).filter(x => !w || norm(pick(x.title as Localised)).includes(w));
  const none = !!w && !hits.length;
  // tell IT what people look for and do not find (once per search, after typing stops)
  useEffect(() => {
    clearTimeout(missT.current);
    if (none && w.length >= 3 && !sent.current.has(w))
      missT.current = window.setTimeout(() => { sent.current.add(w); api('/api/help/search-miss', {method: 'POST', json: {q: q.trim().slice(0, 80)}}).catch(() => {}); }, 1500);
  }, [none, w, q]);
  if (error) return <ErrorPanel error={error} />;
  if (!items) return null;
  return <>
    <div className="row" style={{justifyContent: 'space-between'}}><h1>{t('IT Help Center')}</h1></div>
    <p className="muted">{t('Short instructions from IT. Not found what you need? Ask the IT Helpdesk.')}</p>
    <div className="filters"><input id="hq" placeholder={t('Search: password, phone, VPN…')} value={q} onChange={e => setQ(e.target.value)} /></div>
    <div className="helpcats" id="hl">{Object.entries(C).map(([k, [icon, label]]) => { const a = hits.filter(x => x.category === k);
      return a.length > 0 && <section className="panel" key={k}><h3>{icon} {label}</h3>{a.map(x => <Link key={x.slug} className="hlink" to={`/help/${x.slug}`}>{pick(x.title as Localised)}
        {!x.published && <> <span className="badge draft">{t('Draft')}</span></>}</Link>)}</section>; })}</div>
    {none && <div className="panel empty" id="hnone">{t('Nothing found — IT sees what people search for and adds instructions.')}</div>}
    <div className="panel help-cta">🛠️ {t('Still need help?')} <Link to="/report-problem">{t('Report a problem to IT')}</Link> · <a href="https://helpdesk.example.com">{t('IT Helpdesk')}</a></div>
  </>;
}

export function HelpArticle() {
  const {slug} = useParams();
  const {data: a, error} = useLoad(() => api<Article>('/api/help/' + encodeURIComponent(slug!)), [slug]);
  const [voted, setVoted] = useState<null | boolean>(null);
  if (error) return <ErrorPanel error={error} />;
  if (!a) return null;
  const vote = async (yes: boolean) => {
    try { await api('/api/help/' + encodeURIComponent(slug!) + '/feedback', {method: 'POST', json: {helpful: yes}}); } catch { /* the thanks shows anyway */ }
    setVoted(yes);
  };
  return <>
    <p style={{marginTop: 20}}><Link to="/help">← {t('IT Help Center')}</Link></p>
    <article><div className="inner"><span className="badge pub">{(CATS()[a.category] || ['', a.category])[1]}</span><h1>{pick(a.title as Localised)}</h1>
      {!a.body[lang] && <p className="muted">{t('This article is not yet translated — showing the English version.')}</p>}
      {/* article: editor HTML, sanitised by the server */}
      <div className="prose" dangerouslySetInnerHTML={{__html: pick(a.body as Localised)}} />
      <p className="muted" style={{marginTop: 24}}>{t('Updated {d}', {d: fmtDate(a.updated_at)})}</p>
      <div className="helpful" id="hf">{voted === null ? <><b>{t('Was this helpful?')}</b>
        <button className="btn ghost small" onClick={() => vote(true)}>👍 {t('Yes')}</button><button className="btn ghost small" onClick={() => vote(false)}>👎 {t('No')}</button></>
        : voted ? <>✅ {t('Thank you!')}</>
        : <>{t('Thank you — IT will improve this instruction.')} <a href="https://helpdesk.example.com" target="_blank" rel="noopener">{t('Create a request in the IT Helpdesk')}</a></>}</div></div></article>
  </>;
}

const ItOnly = ({children}: {children: React.ReactNode}) => session.me?.roles.it ? <>{children}</> : <NeedRole group="Intranet-IT-Editors" />;

export const HelpEdit = () => <ItOnly><Editor /></ItOnly>;
function Editor() {
  const {slug} = useParams(), nav = useNavigate(), isNew = slug === 'new';
  const {data: a, error} = useLoad<Article>(() => isNew ? Promise.resolve({slug: '', category: 'accounts', sort: 100, title: {}, body: {}, published: true, updated_at: ''})
    : api<Article>('/api/help/' + slug), [slug]);
  const store = useRef<{title: Record<string, string>; body: Record<string, string>}>({title: {}, body: {}});
  const [cur, setCur] = useState('en'), [title, setTitle] = useState('');
  const [ref, ed] = useEditor(a ? a.body.en || '' : undefined, {minHeight: 420});
  useEffect(() => { if (a) { store.current = {title: {...a.title}, body: {...a.body}}; setTitle(a.title.en || ''); } }, [a]);
  if (error) return <ErrorPanel error={error} />;
  if (!a) return null;
  const keep = () => { store.current.title[cur] = title; if (ed) store.current.body[cur] = ed.getContent(); };
  const switchLang = (l: string) => { keep(); setCur(l); setTitle(store.current.title[l] || ''); ed?.setContent(store.current.body[l] || ''); };
  const del = async () => { if (!confirm(t('Delete this article?'))) return;
    try { await api('/api/help/' + slug, {method: 'DELETE'}); guard.dirty = false; nav('/admin/help'); } catch (err) { fail(err); } };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); if (!ed) return;
    keep(); await ed.uploadImages(); keep(); const f = e.currentTarget.elements as any;
    try { const r = await api<{slug: string}>(isNew ? '/api/help' : '/api/help/' + slug, {method: isNew ? 'POST' : 'PUT',
      json: {slug: f.slug.value, category: f.category.value, sort: +f.sort.value || 100, published: f.published.checked, title: store.current.title, body: store.current.body}});
      guard.dirty = false; toast(t('Saved')); nav('/help/' + r.slug); } catch (err) { fail(err); }
  };
  return <><AdminTabs cur="/admin/help" /><p><Link to="/admin/help">← {t('Help Center articles')}</Link></p>
    <form id="af" className="editor" onInput={() => { guard.dirty = true; }} onSubmit={submit}><div className="sheet">
      <div className="tabs" id="lt">{['en', 'ru', 'az'].map(l => <a key={l} href="#" className={l === cur ? 'on' : ''} onClick={e => { e.preventDefault(); switchLang(l); }}>{l.toUpperCase()}</a>)}</div>
      <input className="doc-title" id="ti" maxLength={200} placeholder={t('Title')} value={title} onChange={e => setTitle(e.target.value)} /><textarea id="bd" ref={ref} /></div>
      <aside className="side"><div className="panel">
        <label>{t('Address')}<input name="slug" required pattern="[a-z0-9][a-z0-9-]{1,60}" defaultValue={a.slug} placeholder="vpn-setup" /></label>
        <label>{t('Category')}<select name="category" defaultValue={a.category}>{Object.entries(CATS()).map(([k, [, l]]) => <option key={k} value={k}>{l}</option>)}</select></label>
        <label>{t('Order')}<input type="number" name="sort" defaultValue={a.sort} /></label>
        <label className="check"><input type="checkbox" name="published" defaultChecked={a.published} /> {t('Published')}</label>
        <button className="btn">{t('Save')}</button>
        {!isNew && <button type="button" className="btn danger" id="adel" onClick={del}>{t('Delete')}</button>}</div>
        <p className="muted">{t('English is required; Russian and Azerbaijani are shown when present.')}</p></aside></form></>;
}

type Stats = {votes: Record<string, {yes: number; no: number}>; misses: {q: string; n: number; last: string}[]};
export const HelpAdmin = () => <ItOnly><ArticleList /></ItOnly>;
function ArticleList() {
  const {data, error} = useLoad(() => Promise.all([api<Article[]>('/api/help?all=true'), api<Stats>('/api/help-stats').catch(() => ({votes: {}, misses: []} as Stats))]));
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [items, st] = data, C = CATS();
  return <><AdminTabs cur="/admin/help" /><div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Help Center articles')}</h1>
    <Link className="btn" to="/admin/help/new">+ {t('New article')}</Link></div>
    <table className="list"><thead><tr><th>{t('Title')}</th><th>{t('Category')}</th><th>{t('Status')}</th><th title={t('Was this helpful?')}>👍 / 👎</th><th>{t('Updated')}</th><th></th></tr></thead><tbody>
      {items.length ? items.map(a => { const v = st.votes[a.slug];
        return <tr key={a.slug}><td><b>{pick(a.title as Localised)}</b><div className="muted" style={{fontSize: 12}}>/help/{a.slug}</div></td>
          <td>{C[a.category] ? C[a.category].join(' ') : a.category}</td>
          <td>{a.published === false ? <span className="badge draft">{t('Draft')}</span> : <span className="badge pub">{t('Published')}</span>}</td>
          <td>{v ? <><span className="vote yes">{v.yes}</span> / <span className="vote no">{v.no}</span></> : <span className="muted">—</span>}</td>
          <td className="muted">{fmtDate(a.updated_at)}</td>
          <td style={{textAlign: 'right', whiteSpace: 'nowrap'}}><Link className="btn small ghost" to={`/help/${a.slug}`}>{t('View')}</Link>{' '}
            <Link className="btn small ghost" to={`/admin/help/${a.slug}`}>{t('Edit')}</Link></td></tr>; })
        : <tr><td colSpan={6} className="empty">{t('No articles yet')}</td></tr>}</tbody></table>
    <h2>{t('Searches that found nothing')} <small className="muted">{t('last 90 days')}</small></h2>
    {st.misses.length ? <table className="list"><thead><tr><th>{t('Search')}</th><th>{t('Times')}</th><th>{t('Last')}</th></tr></thead><tbody>
      {st.misses.map(m => <tr key={m.q}><td><b>{m.q}</b></td><td>{m.n}</td><td className="muted">{fmtDate(m.last)}</td></tr>)}</tbody></table>
      : <div className="panel empty">{t('None yet')}</div>}</>;
}
