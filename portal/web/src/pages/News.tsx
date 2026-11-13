// News feed and article page.
import {useEffect, useMemo, useRef, useState} from 'react';
import {Link, useNavigate, useParams, type NavigateFunction} from 'react-router';
import {api, openFile} from '../lib/api';
import {fmtDate, lang, norm, t} from '../lib/i18n';
import {Avatar, ErrorPanel, HelpQ, fillPhotos, initials, useLoad} from '../components/ui';

export type NewsPerson = {id: string; name: string};
export type News = {
  id: number; title: string; summary: string; cover?: string | null; pinned?: boolean; published?: boolean; lang: string;
  published_at?: string | null; updated_at?: string; created_at?: string; body_html: string; people?: NewsPerson[];
  i18n?: Record<string, {title?: string; summary?: string; body_html?: string}>; attachments?: {id: string; name: string; size: number}[];
};
// the reader's language when the post has it, otherwise the main version
export const loc = (n: News): News => (n.lang !== lang && n.i18n?.[lang]) ? {...n, ...n.i18n[lang]} : n;

// News page: one list (date · text · picture) with search; on desktop a People panel (new colleagues and role
// changes from the posts of the last 60 days, labelled on the right)
const BADGE: Record<string, [string, string]> = {en: ['New', 'New role'], ru: ['Новый', 'Новая должность'], az: ['Yeni', 'Yeni vəzifə']};
const Icon = () => <svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
  <path d="M4 5h13v14H6a2 2 0 0 1-2-2z" /><path d="M17 8h3v9a2 2 0 0 1-2 2" /><path d="M7 9h7M7 12h7M7 15h4" /></svg>;

function Thumb({n}: {n: News}) {
  if (n.cover) return <span className="nth" style={{backgroundImage: `url('${n.cover}')`}} />;
  const ps = (n.people || []).slice(0, 4);
  if (ps.length) return <span className={`nth faces f${ps.length}`}>{ps.map(p => <Avatar key={p.id} p={{...p, has_photo: !!p.id}} />)}</span>;
  return <span className="nth none"><Icon /></span>;
}

export function NewsRow({n}: {n: News}) {
  const d = new Date(n.published_at || n.updated_at!), mon = d.toLocaleDateString(lang === 'az' ? 'az-Latn' : lang, {month: 'short'});
  return <Link className="nrow" to={`/news/${n.id}`}>
    <span className="nd"><b>{d.getDate()}</b><small>{mon.replace('.', '')}</small><small>{d.getFullYear()}</small></span>
    <span className="nb">{n.pinned && <span className="badge pin">{t('Pinned')}</span>}<b className="nt">{n.title}</b><span className="sum">{n.summary}</span></span>
    <Thumb n={n} /></Link>;
}
export const NewsRows = ({items, compact}: {items: News[]; compact?: boolean}) => items.length
  ? <div className={`nlist${compact ? ' compact' : ''}`}>{items.map(loc).map(n => <NewsRow key={n.id} n={n} />)}</div>
  : <div className="panel empty">{t('No news yet')}</div>;

type NP = {id?: string; name: string; role: string; kind: string};
export function NewsList() {
  const {data, error} = useLoad(() => Promise.all([api<News[]>('/api/news?limit=50'), api<NP[]>('/api/news/people?days=60&lang=' + lang).catch(() => [] as NP[])]));
  const [q, setQ] = useState('');
  const items = useMemo(() => (data?.[0] || []).map(n => ({n: loc(n), key: norm([n.title, n.summary, ...Object.values(n.i18n || {}).flatMap(v => [v.title, v.summary]),
    ...(n.people || []).map(p => p.name)].join(' '))})), [data]);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [news, people] = data, [bNew, bRole] = BADGE[lang] || BADGE.en;
  const words = norm(q).trim().split(/\s+/).filter(Boolean), hit = items.filter(x => words.every(w => x.key.includes(w)));
  return <>
    <h1>{t('News')} <HelpQ slug="intranet-start" /></h1><p className="muted">{t('From HR and management')}</p>
    <div className="nwrap"><div><input type="search" id="nq" className="nq" placeholder={t('Search news…')} aria-label={t('Search news…')} value={q} onChange={e => setQ(e.target.value)} />
      <div className="nlist" id="nl">{hit.length ? hit.map(x => <NewsRow key={x.n.id} n={x.n} />) : <div className="empty">{t(news.length ? 'Nothing found' : 'No news yet')}</div>}</div></div>
    {people.length > 0 && <aside className="npeople"><h4>{t('People')}</h4><small className="muted">{t('Last 60 days')}</small>{people.map((p, i) =>
      <Link key={i} className="np" to={p.id ? '/directory/' + p.id : '/directory?q=' + encodeURIComponent(p.name)}>
        <Avatar p={{...p, has_photo: !!p.id}} /><span className="pn"><b>{p.name}</b><small>{p.role}</small></span>
        <span className={`nbg ${p.kind}`}>{p.kind === 'role' ? bRole : bNew}</span></Link>)}</aside>}</div>
  </>;
}

const fileIcon = (name: string) => /\.pdf$/i.test(name) ? '📕' : /\.(xlsx?|csv)$/i.test(name) ? '📗' : /\.(pptx?)$/i.test(name) ? '📙' : /\.(jpe?g|png)$/i.test(name) ? '🖼️' : '📘';
export const fileSize = (s: number) => s >= 1048576 ? (s / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(s / 1024)) + ' KB';

export function NewsItem() {
  const {id} = useParams();
  const {data, error} = useLoad(() => api<News>('/api/news/' + id).then(loc), [id]);
  const prose = useRef<HTMLDivElement>(null), nav = useNavigate();
  useEffect(() => { if (data) personCards(prose.current!, nav); }, [data, nav]);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const n = data;
  // the cover is the list picture; on the article it shows only when the text does not already have it
  return <article>{n.cover && !n.body_html.includes(n.cover) && <img className="cover" src={n.cover} alt="" />}<div className="inner">
    {!n.published && <span className="badge draft">{t('Draft')}</span>}<h1>{n.title}</h1>
    <p className="muted">{fmtDate(n.published_at || n.created_at)}</p>
    {/* body: HTML from the editor, sanitised by the server (core.sanitize) */}
    <div className="prose" ref={prose} dangerouslySetInnerHTML={{__html: n.body_html}} />
    {!!n.attachments?.length && <><h3 className="att-h">📎 {t('Attachments')}</h3><div className="docs">{n.attachments.map(a =>
      <a key={a.id} className="doc" href="#" onClick={e => { e.preventDefault(); openFile(`/api/news/${id}/files/${a.id}`, a.name); }}>
        <span className="fi">{fileIcon(a.name)}</span><span><b>{a.name}</b><small>{fileSize(a.size)}</small></span></a>)}</div></>}
    <p style={{marginTop: 24}}><Link to="/news">← {t('All news')}</Link></p></div></article>;
}

// A heading that is only a link to a colleague (<h3><a href="/directory/ID">Name</a></h3>, or /directory?q=Name for
// people not in the directory) + the paragraph under it → a person card with the directory photo.
// Links to intranet pages open in the app.
function personCards(root: HTMLElement, nav: NavigateFunction) {
  root.querySelectorAll('h3').forEach(h => {
    const a = h.querySelector<HTMLAnchorElement>('a[href^="/directory"]');
    if (!a || h.textContent!.trim() !== a.textContent!.trim()) return;
    const card = document.createElement('div'); card.className = 'npcard';
    const href = a.getAttribute('href')!, pid = href.startsWith('/directory/') ? href.split('/')[2] : '';
    const pav = document.createElement('a'); pav.className = 'pav'; pav.href = href;
    const av = document.createElement('span'); av.className = 'av lg'; av.dataset.ph = pid; av.textContent = initials(a.textContent);
    pav.append(av); const body = document.createElement('div'); card.append(pav, body);
    h.before(card);
    const next = h.nextElementSibling;
    body.append(h);
    if (next && next.tagName === 'P') body.append(next);
  });
  root.querySelectorAll<HTMLAnchorElement>('a[href^="/"]').forEach(a => {
    a.removeAttribute('target');
    a.onclick = e => { if (!e.ctrlKey && !e.metaKey) { e.preventDefault(); nav(a.getAttribute('href')!); } };
  });
  fillPhotos(root);
}
