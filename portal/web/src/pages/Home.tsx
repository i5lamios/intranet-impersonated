// Home: HSE strip, applications, colleague search, latest news; side: weather, birthdays.
import {useEffect, useState} from 'react';
import {Link, useNavigate} from 'react-router';
import {api} from '../lib/api';
import {dayName, fmtDate, lang, t} from '../lib/i18n';
import {kc} from '../lib/kc';
import {session} from '../lib/session';
import {Avatar, ErrorPanel, HelpQ, useLoad} from '../components/ui';
import {NewsRows, type News} from './News';

const tiles = (): [string, string, string, string, string, string?][] => [
  ['☁️', 'Company Cloud', t('Files'), 'https://cloud.example.com', 'var(--sc-blue)', 'cloud'],
  ['💬', 'Company Chat', t('Team chat'), 'https://chat.example.com/oauth/gitlab/login', 'var(--sc-green)', 'chat'],
  ['✉️', t('Mail'), t('Outlook on the web'), 'https://mail.example.com/owa', 'var(--sc-navy)', 'mobile-mail'],
  ['📞', t('Phone'), t('3CX web client, calls'), session.me?.features.phone || 'https://company.3cx.example:5001/', 'var(--sc-green)', 'directory-calls'],
  ['❓', t('IT Help Center'), t('Instructions from IT'), '/help', 'var(--sc-blue)'],
  ['🆘', t('Report a problem'), t('Something broken? Tell IT'), '/report-problem', 'var(--sc-red)', 'report-problem'],
  ['🛠️', 'IT Helpdesk', t('Requests to IT'), 'https://helpdesk.example.com', 'var(--sc-red)'],
  ['🔐', 'Company Vault', t('Passwords (IT)'), 'https://dvls.example.com', 'var(--sc-navy)'],
  ['👤', t('My profile'), t('Phone, photo, 2FA, notifications'), '/me', 'var(--sc-blue)', 'my-profile'],
];

export function Home() {
  const {data: news, error} = useLoad(() => api<News[]>('/api/news?limit=5'));
  const [q, setQ] = useState(''), nav = useNavigate();
  const tp = (kc.tokenParsed || {}) as {given_name?: string; preferred_username?: string};
  if (error) return <ErrorPanel error={error} />;
  if (!news) return null;
  return <>
    {kc.authenticated && <div className="hello">{t('Welcome, {name}', {name: tp.given_name || tp.preferred_username})}</div>}
    {kc.authenticated && <ForYou />}
    {kc.authenticated && <HseWidget />}
    <div className="home"><div className="home-main">
      <h2>{t('Applications')} <HelpQ slug="intranet-start" /></h2><div className="grid">{tiles().map(([i, n, d, u, c, h]) =>
        <div className="tilew" key={n}>{u.startsWith('/')
          ? <Link className="tile" style={{'--c': c} as React.CSSProperties} to={u}><div className="i">{i}</div><b>{n}</b><span>{d}</span></Link>
          : <a className="tile" style={{'--c': c} as React.CSSProperties} href={u}><div className="i">{i}</div><b>{n}</b><span>{d}</span></a>}{h && <HelpQ slug={h} />}</div>)}</div>
      <h2>{t('Find a colleague')}</h2>
      <form className="filters" id="qf" style={{marginTop: 0}} onSubmit={e => { e.preventDefault(); nav('/directory?q=' + encodeURIComponent(q)); }}>
        <input name="q" placeholder={t('Name, title, department, phone')} value={q} onChange={e => setQ(e.target.value)} /><button className="btn">{t('Search')}</button></form>
      <h2>{t('Latest news')} <Link to="/news" className="muted" style={{fontWeight: 400}}>— {t('all')}</Link></h2><NewsRows items={news} compact />
    </div><aside className="home-side"><Weather />{kc.authenticated && <Birthdays />}</aside></div>
  </>;
}

// things waiting for me: certificates expiring within 60 days, open HSE actions
type MyCert = {id: number; type_id: number; type_name: string; expires?: string | null; days_left?: number | null};
type MyAction = {id: number; title: string; due: string; status: string; overdue: boolean};
function ForYou() {
  const [items, setItems] = useState<[string, boolean, React.ReactNode][]>([]);
  useEffect(() => {
    Promise.all([api<MyCert[]>('/api/certs/mine').catch(() => []), api<MyAction[]>('/api/hse/actions/mine').catch(() => [])]).then(([certs, acts]) => {
      const out: [string, boolean, React.ReactNode][] = [];
      certs.filter(c => c.days_left != null && c.days_left <= 60 && !certs.some(o => o.type_id === c.type_id && (o.expires || '') > (c.expires || '')))
        .forEach(c => out.push(['/training', c.days_left! <= 7, <>🎓 <b>{c.type_name}</b> {c.days_left! < 0 ? t('certificate has expired ({d})', {d: fmtDate(c.expires)})
          : t('certificate expires in {n} days ({d})', {n: c.days_left, d: fmtDate(c.expires)})}</>]));
      acts.filter(a => a.status === 'open').forEach(a => out.push(['/hse#my-actions', a.overdue, <>🦺 {t('HSE action for you')}: <b>{a.title}</b> · {a.overdue ? t('overdue since {d}', {d: fmtDate(a.due)}) : t('due {d}', {d: fmtDate(a.due)})}</>]));
      setItems(out);
    });
  }, []);
  if (!items.length) return null;
  return <div className="foryou" id="foryou">{items.map(([to, red, body], i) => <Link key={i} to={to} className={red ? 'red' : ''}>{body}</Link>)}</div>;
}

type Hse = {days_without_lti: number | null; record_days?: number; counts: Record<string, number>; moment_title?: string};
function HseWidget() {
  const [h, setH] = useState<Hse | null>(null);
  useEffect(() => { api<Hse>('/api/hse').then(setH).catch(() => {}); }, []);
  if (!h) return <div id="w-hse"></div>;
  const n = h.days_without_lti;
  return <div id="w-hse"><div className="hse-strip">
    <div className="hse-days"><b className={n == null ? 'na' : ''}>{n ?? t('not set')}</b><span>{t('days without a lost-time incident')}</span></div>
    {!!h.record_days && <div className="hse-stat"><b>{h.record_days}</b><span>{t('best record, days')}</span></div>}
    <div className="hse-stat"><b>{h.counts.near_miss}</b><span>{t('near misses reported this year')}</span></div>
    <div className="hse-stat"><b>{h.counts.good_practice + h.counts.unsafe_act + h.counts.unsafe_condition}</b><span>{t('observations this year')}</span></div>
    {h.moment_title && <Link className="hse-moment" to="/hse"><small>{t('Safety moment')}</small><b>{h.moment_title}</b></Link>}
    <div className="hse-actions"><Link className="btn" to="/hse/report">⚠️ {t('Report a hazard')}</Link><Link className="btn ghost" to="/hse">{t('HSE board')}</Link></div></div></div>;
}

type Place = {place: string; icon: string; temp: number; feels: number; wind: number; en: string; ru?: string; az: string;
  days: {date: string; icon: string; max: number; min: number}[]};
function Weather() {
  const [w, setW] = useState<Place[]>([]);
  useEffect(() => { api<Place[]>('/api/weather').then(setW).catch(() => {}); }, []);
  const desc = (p: Place) => ({en: p.en, ru: p.ru || p.en, az: p.az})[lang] || p.en;
  return <div id="w-weather">{w.map(p => <div className="widget weather" key={p.place}><div className="wh">{t('Weather')} — {p.place}</div>
    <div className="now"><span className="big">{p.icon}</span><div><b>{p.temp}°</b><small>{desc(p)}<br />{t('feels like {f}°, wind {w} m/s', {f: p.feels, w: p.wind})}</small></div></div>
    <div className="days">{p.days.map(d => <div key={d.date}><small>{dayName(new Date(d.date), 'short')}</small><span>{d.icon}</span><small>{d.max}° / {d.min}°</small></div>)}</div></div>)}</div>;
}

type Bday = {id: string; name: string; title?: string; department?: string; has_photo?: boolean; in_days: number; month: number; day: number};
function Birthdays() {
  const [all, setAll] = useState<Bday[] | null>(null);
  useEffect(() => { api<Bday[]>('/api/birthdays?days=60').then(setAll).catch(() => {}); }, []);
  if (!all) return <div id="w-bday"></div>;
  // the next two weeks; with none in that window, the next three (within 60 days) so the widget is never empty for long
  const soon = all.filter(x => x.in_days <= 14), b = soon.length ? soon : all.slice(0, 3);
  const when = (x: Bday) => x.in_days === 0 ? <b className="today">{t('Today')} 🎉</b> : x.in_days === 1 ? t('Tomorrow') : fmtDate(new Date(2024, x.month - 1, x.day), {day: 'numeric', month: 'long'});
  return <div id="w-bday"><div className="widget"><div className="wh">🎂 {t('Birthdays')}</div>
    {!soon.length && b.length > 0 && <p className="muted" style={{margin: '0 0 6px'}}>{t('Coming up')}</p>}
    {b.length ? b.slice(0, 8).map(x => <Link key={x.id} className={`bday ${x.in_days === 0 ? 'is-today' : ''}`} to={`/directory/${x.id}`}><Avatar p={x} />
      <span><b>{x.name}</b><small>{x.title || x.department}</small></span><span className="when">{when(x)}</span></Link>)
      : <p className="muted">{t('None in the next two weeks')}</p>}</div></div>;
}
