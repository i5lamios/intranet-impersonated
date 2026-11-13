// Directory (AD address book) and person page.
import {Fragment, useEffect, useMemo, useRef, useState, type ReactNode} from 'react';
import {Link, useNavigate, useParams, useSearchParams} from 'react-router';
import {api, fail} from '../lib/api';
import {norm, t} from '../lib/i18n';
import {session} from '../lib/session';
import {toast} from '../lib/toast';
import {Avatar, ErrorPanel, HelpQ, initials, photo, useLoad} from '../components/ui';

export type Person = {
  id: string; name: string; title?: string; department?: string; office?: string; company?: string; phone?: string; mobile?: string;
  extension?: string; mail?: string; username?: string; has_photo?: boolean;
};
type Dir = {people: Person[]; departments: string[]; offices: string[]; updated?: string};
type Presence = {people: Record<string, {state: string; profile?: string; ext?: string}>; me?: unknown};

// 3CX presence: refreshed while a directory page is open
let presence: Presence = {people: {}}, presenceAt = 0;
async function loadPresence() {
  if (!session.me?.features.pbx) return presence;
  if (Date.now() - presenceAt > 15000) { try { presence = await api<Presence>('/api/phone/presence'); presenceAt = Date.now(); } catch { /* keep the last */ } }
  return presence;
}
const PSTATE = (): Record<string, string> => ({available: t('Available'), oncall: t('On a call'), away: t('Away'), dnd: t('Do not disturb'), offline: t('Offline')});
const Dot = ({id}: {id: string}) => { const x = presence.people[id];
  return x ? <i className={`pdot ${x.state}`} title={PSTATE()[x.state] + (x.profile && x.state !== 'oncall' ? ' · ' + x.profile : '')} /> : null; };
export async function callNumber(number: string) {
  try { const r = await api<{from: string}>('/api/phone/call', {method: 'POST', json: {destination: number}}); toast(t('Your phone {ext} is ringing — pick up to connect', {ext: r.from})); }
  catch (err) { fail(err); }
}

let dirCache: Dir | null = null;
const loadDir = async () => dirCache || (dirCache = await api<Dir>('/api/directory'));

// Avatars: brand-tinted initials until the AD photo arrives
const TINTS = ['#1b2b5b', '#2e6db4', '#3aa655', '#c8102e', '#0e7490', '#6d28d9', '#b45309'];
const tint = (s?: string) => TINTS[[...(s || '')].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7) % TINTS.length];
const Av = ({p, cls = ''}: {p: Person; cls?: string}) => <Avatar p={p} className={`av ${cls}`.trim()} style={{background: tint(p.name)}} />;
const svg = (d: string) => <svg viewBox="0 0 24 24"><path d={d} /></svg>;
const I = {
  phone: svg('M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z'),
  mobile: svg('M16 1H8a3 3 0 0 0-3 3v16a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3V4a3 3 0 0 0-3-3zm-4 21a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5-4H7V4h10z'),
  mail: svg('M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z'),
  chat: svg('M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z'),
  pbx: svg('M12 1a9 9 0 0 0-9 9v7a3 3 0 0 0 3 3h3v-8H5v-2a7 7 0 0 1 14 0v2h-4v8h4v1h-7v2h6a3 3 0 0 0 3-3V10a9 9 0 0 0-9-9z'),
  search: svg('M15.5 14h-.8l-.3-.3A6.5 6.5 0 1 0 14 15.5l.3.3v.8l5 5 1.5-1.5zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9z'),
  pin: svg('M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z'),
};
const digits = (n?: string) => (n || '').replace(/[^\d+]/g, '');
// Calls. Desktop: every number goes to the 3CX web client (#/people?phone=N opens its dialer with the number — one
// press on the green button; tested 2026-11-01, 3CX gives no auto-dial link), always in
// the same "3cx" tab — no Windows "how do you want to call" chooser. Phone: internal extensions go to 3CX, mobile and
// other outside numbers to the normal cellular dialer (tel:).
const ON_PHONE = matchMedia('(pointer:coarse)').matches || /Android|iPhone|iPad/i.test(navigator.userAgent);
const isExt = (n: string) => digits(n).replace('+', '').length <= 4;
const pbx = () => session.me?.features.phone ? session.me.features.phone.replace(/\/?$/, '/') : '';
type DialLink = {href: string; target?: string; rel?: string};
export const dial = (n: string): DialLink => (ON_PHONE && !isExt(n)) || !pbx() ? {href: 'tel:' + digits(n)}
  : {href: pbx() + '#/people?phone=' + encodeURIComponent(digits(n)), target: '3cx', rel: 'noopener'};
const Tel = ({n, children}: {n: string; children?: ReactNode}) => <a {...dial(n)}>{children ?? n}</a>;
export const chatUrl = (p: Person) => p.mail && p.username ? `https://chat.example.com/company/messages/@${encodeURIComponent(p.username)}` : '';

function Actions({p, big = false}: {p: Person; big?: boolean}) {
  const main = p.extension || p.phone;
  const B = ({l, icon, label, cls = ''}: {l: DialLink; icon: ReactNode; label: string; cls?: string}) =>
    <a className={`act ${cls}`.trim()} {...l} title={label} aria-label={label}>{icon}{big && <span>{label}</span>}</a>;
  return <>
    {main && <B l={dial(main)} icon={I.phone} label={t('Call') + ' ' + main} cls="primary" />}
    {p.mobile && <B l={dial(p.mobile)} icon={I.mobile} label={t('Mobile') + ' ' + p.mobile} />}
    {p.mail && <B l={{href: 'mailto:' + p.mail}} icon={I.mail} label={t('E-mail')} cls="k-mail" />}
    {chatUrl(p) && <B l={{href: chatUrl(p), target: '_blank', rel: 'noopener'}} icon={I.chat} label="Chat" cls="k-chat" />}
  </>;
}

type SortKey = 'name' | 'department' | 'office';
export function Directory() {
  const {data: dir, error} = useLoad(async () => { const d = await loadDir(); await loadPresence(); return d; });
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get('q') || ''), [dept, setDept] = useState(params.get('dept') || ''), [off, setOff] = useState('');
  const [sortKey, setSort] = useState<SortKey>('name'), [mode, setMode] = useState(localStorage.getItem('dirView') || 'cards');
  const [, tick] = useState(0);
  const nav = useNavigate(), qRef = useRef<HTMLInputElement>(null);
  useEffect(() => { if (dir && !matchMedia('(pointer:coarse)').matches) qRef.current?.focus(); }, [dir]);
  useEffect(() => {                                  // keep the address in step with the search
    const s = new URLSearchParams(); if (q) s.set('q', q); if (dept) s.set('dept', dept);
    setParams(s, {replace: true});
  }, [q, dept, setParams]);
  useEffect(() => { const id = setInterval(async () => { if (!session.me?.features.pbx) return; presenceAt = 0; await loadPresence(); tick(x => x + 1); }, 30000);
    return () => clearInterval(id); }, []);
  const rows = useMemo(() => {
    if (!dir) return [];
    const words = norm(q).trim().split(/\s+/).filter(Boolean);
    return dir.people.filter(p => (!dept || p.department === dept) && (!off || p.office === off) &&
      words.every(w => norm([p.name, p.title, p.department, p.office, p.phone, p.mobile, p.extension, p.mail, p.username].join(' ')).includes(w)))
      .sort((a, b) => (sortKey === 'name' ? 0 : (a[sortKey] || '￿').localeCompare(b[sortKey] || '￿', 'az')) || a.name.localeCompare(b.name, 'az'));
  }, [dir, q, dept, off, sortKey]);
  if (error) return <ErrorPanel error={error} />;
  if (!dir) return null;
  const open = (e: React.MouseEvent, id: string) => { if (!(e.target as HTMLElement).closest('a,button')) nav('/directory/' + id); };
  const Card = ({p}: {p: Person}) => <div className="pcard" onClick={e => open(e, p.id)}>
    <div className="pc-top"><span className="avw"><Av p={p} cls="lg" /><Dot id={p.id} /></span><div className="pc-id"><b>{p.name}</b><span>{p.title || ' '}</span></div></div>
    <div className="pc-tags">{p.department && <span className="tag">{p.department}</span>}{p.office && <span className="tag ghost">{I.pin}{p.office}</span>}</div>
    <div className="pc-foot"><span className="pc-num">{p.extension ? <>{t('Ext.')} <b>{p.extension}</b></> : p.phone || p.mobile || ''}</span>
      <span className="acts"><Actions p={p} /></span></div></div>;
  const groupOf = (p: Person) => sortKey === 'name' ? (p.name || '?')[0].toUpperCase() : (p[sortKey] || t('Other'));
  const groups: [string, Person[]][] = [];
  rows.forEach(p => { const k = groupOf(p); if (!groups.length || groups[groups.length - 1][0] !== k) groups.push([k, []]); groups[groups.length - 1][1].push(p); });
  const setM = (m: string) => (e: React.MouseEvent) => { e.preventDefault(); setMode(m); localStorage.setItem('dirView', m); };
  return <>
    <div className="dhead"><div><h1>{t('Directory')} <HelpQ slug="directory-calls" /></h1>
      <p className="muted">{t('{n} colleagues — Active Directory, updated {d}', {n: dir.people.length, d: (dir.updated || '').slice(0, 16).replace('T', ' ')})}</p></div></div>
    <div className="dsearch">{I.search}<input id="q" ref={qRef} type="search" autoComplete="off" placeholder={t('Name, title, department, phone, e-mail')} value={q} onChange={e => setQ(e.target.value)} /></div>
    <div className="dfilters"><select id="dept" value={dept} onChange={e => setDept(e.target.value)}><option value="">{t('All departments')}</option>{dir.departments.map(d => <option key={d}>{d}</option>)}</select>
      <select id="off" value={off} onChange={e => setOff(e.target.value)}><option value="">{t('All offices')}</option>{dir.offices.map(d => <option key={d}>{d}</option>)}</select>
      <select id="sort" value={sortKey} onChange={e => setSort(e.target.value as SortKey)}><option value="name">{t('Sort: name')}</option><option value="department">{t('Sort: department')}</option><option value="office">{t('Sort: office')}</option></select>
      <span className="muted" id="cnt">{t('{n} shown', {n: rows.length})}</span>
      <div className="vswitch" id="mode" role="group" aria-label={t('Display')}><span>{t('Display')}</span>
        <a href="#" className={mode === 'cards' ? 'on' : ''} title={t('Cards')} onClick={setM('cards')}><svg viewBox="0 0 24 24"><path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3zm10 0h8v8h-8z" /></svg>{t('Cards')}</a>
        <a href="#" className={mode === 'list' ? 'on' : ''} title={t('List')} onClick={setM('list')}><svg viewBox="0 0 24 24"><path d="M3 5h18v2H3zm0 6h18v2H3zm0 6h18v2H3z" /></svg>{t('List')}</a></div></div>
    <div id="out">{!rows.length ? <div className="panel empty">{t('Nothing found')}</div>
      : mode === 'list' ? <table className="people"><thead><tr><th>{t('Name')}</th><th className="opt">{t('Department')}</th><th className="opt">{t('Office')}</th>
          <th className="opt">{t('Ext.')}</th><th className="opt">{t('Phone')}</th><th></th></tr></thead><tbody>{rows.map(p =>
          <tr key={p.id} onClick={e => open(e, p.id)}>
            <td><div className="pcell"><span className="avw"><Av p={p} /><Dot id={p.id} /></span><span className="pn"><b>{p.name}</b><small className="muted">{p.title}</small>
              {p.extension && <small className="m-ext">{t('Ext.')} <b>{p.extension}</b></small>}</span></div></td>
            <td className="opt">{p.department}</td><td className="opt">{p.office}</td>
            <td className="num opt">{p.extension && <b>{p.extension}</b>}</td>
            <td className="num opt">{p.phone && p.phone !== p.extension ? p.phone : ''}{p.mobile && <div>{p.mobile}</div>}</td>
            <td className="tacts"><span className="acts"><Actions p={p} /></span></td></tr>)}</tbody></table>
      : groups.map(([g, ps]) => <Fragment key={g}><h2 className="dgroup"><span>{g}</span><small>{ps.length}</small></h2>
          <div className="pgrid">{ps.map(p => <Card key={p.id} p={p} />)}</div></Fragment>)}</div>
  </>;
}

type Full = Person & {manager?: Person | null; reports: Person[]};
export function Person() {
  const {id} = useParams();
  const {data, error} = useLoad(async () => {
    const [p, all] = await Promise.all([api<Full>('/api/directory/' + encodeURIComponent(id!)), loadDir()]);
    const full = all.people.find(x => x.id === p.id) || {} as Person;
    p.extension = p.extension || full.extension; p.has_photo = p.has_photo ?? full.has_photo;
    await loadPresence();
    return {p, all};
  }, [id]);
  const [ph, setPh] = useState<string | null>(null);
  useEffect(() => { setPh(null); if (data?.p.has_photo) photo(data.p.id).then(setPh); }, [data]);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const {p, all} = data;
  const pr = presence.people[p.id], canCall = !!(session.me?.features.pbx && presence.me);
  const Row = ({k, v}: {k: string; v: ReactNode}) => v ? <><dt>{k}</dt><dd>{v}</dd></> : null;
  const byId = new Map(all.people.map(x => [x.id, x]));
  const Mini = ({x}: {x: Person}) => <Link className="mini" to={`/directory/${x.id}`}><Av p={x} /><span><b>{x.name}</b><small>{x.title || ''}</small></span></Link>;
  const mates = p.department ? all.people.filter(x => x.department === p.department && x.id !== p.id).sort((a, b) => a.name.localeCompare(b.name, 'az')) : [];
  return <>
    <p className="back"><Link to="/directory">← {t('Directory')}</Link></p>
    <section className="phero"><div className="phero-band"></div><div className="phero-main">
      {ph ? <img className="phero-ph" src={ph} alt="" /> : <div className="phero-ph" id="ph" style={{background: tint(p.name)}}>{initials(p.name)}</div>}
      <div className="phero-id"><h1>{p.name}</h1><p>{p.title || ' '}</p>
        <div className="pc-tags">{p.department && <Link className="tag" to={`/directory?dept=${encodeURIComponent(p.department)}`}>{p.department}</Link>}
          {p.office && <span className="tag ghost">{I.pin}{p.office}</span>}
          {pr && <span className={`pstate ${pr.state}`}><Dot id={p.id} /> {PSTATE()[pr.state]}</span>}</div></div>
      <div className="phero-act acts big"><Actions p={p} big />
        {canCall && (pr || p.phone || p.mobile) && <button className="act primary" id="c3" onClick={() => callNumber(pr ? pr.ext! : (p.phone || p.mobile)!)}>{I.pbx}<span>{t('Call from my phone')}</span></button>}</div></div></section>
    <div className="pcols">
      <div className="panel"><h3>{t('Contact')}</h3><dl className="kv">
        <Row k={t('Extension')} v={p.extension && <Tel n={p.extension}><b>{p.extension}</b></Tel>} />
        <Row k={t('Phone')} v={p.phone && p.phone !== p.extension && <Tel n={p.phone} />} />
        <Row k={t('Mobile')} v={p.mobile && <Tel n={p.mobile} />} />
        <Row k={t('E-mail')} v={p.mail && <a href={`mailto:${p.mail}`}>{p.mail}</a>} />
        <Row k={t('Office')} v={p.office} /><Row k={t('Company')} v={p.company} /></dl>
        {!p.extension && !p.phone && !p.mobile && <p className="muted">{t('No phone number in Active Directory.')}</p>}</div>
      <div className="panel"><h3>{t('Organisation')}</h3>
        {p.manager && <><div className="lbl">{t('Manager')}</div><Mini x={byId.get(p.manager.id) || p.manager} /></>}
        {p.reports.length > 0 && <><div className="lbl">{t('Direct reports')} · {p.reports.length}</div><div className="minis">{p.reports.map(r => <Mini key={r.id} x={byId.get(r.id) || r} />)}</div></>}
        {!p.manager && !p.reports.length && <p className="muted">{t('Managers are not yet set in AD')}</p>}</div></div>
    {mates.length > 0 && <><h2 className="dgroup"><span>{t('Same department')}</span><small>{mates.length}</small></h2>
      <div className="minis wide">{mates.slice(0, 18).map(x => <Mini key={x.id} x={x} />)}</div>
      {mates.length > 18 && <p><Link to={`/directory?dept=${encodeURIComponent(p.department!)}`}>{t('All {n} in {d} →', {n: mates.length, d: p.department})}</Link></p>}</>}
  </>;
}
