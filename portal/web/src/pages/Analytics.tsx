// Intranet usage analytics for IT (AD group Intranet-IT-Editors). No names are stored — only salted hashes.
import {useState} from 'react';
import {Link, useSearchParams} from 'react-router';
import {api} from '../lib/api';
import {fmtDate, t} from '../lib/i18n';
import {session} from '../lib/session';
import {ErrorPanel, NeedRole, useLoad} from '../components/ui';
import {AdminTabs} from './Admin';

const PAGE = (p: string) => ({'/': t('Home'), '/news': t('News'), '/news/:id': t('News article'), '/directory': t('Directory'), '/directory/:id': t('Person page'),
  '/org': t('Org chart'), '/hse': t('HSE board'), '/hse/report': t('Report a hazard'), '/training': t('My certificates'), '/docs': t('HR documents'),
  '/rooms': t('Meeting rooms'), '/help': t('IT Help Center'), '/help/:slug': t('Help article'), '/me': t('My profile')} as Record<string, string>)[p] || p;

type A = {days: number; users: number; staff: number; wau: number; mobile_share: number; langs: {lang: string; users: number}[];
  daily: {day: string; users: number; views: number}[]; pages: {page: string; views: number; users: number}[];
  departments: {department?: string; users: number; staff: number}[]};

export const Analytics = () => session.me?.roles.it ? <Usage /> : <NeedRole group="Intranet-IT-Editors" />;
function Usage() {
  const [params] = useSearchParams(), days = +(params.get('days') || 30);
  const {data: a, error} = useLoad(() => api<A>('/api/analytics?days=' + days), [days]);
  const [tip, setTip] = useState<{text: string; left: number; top: number} | null>(null);
  if (error) return <ErrorPanel error={error} />;
  if (!a) return null;
  const max = Math.max(1, ...a.daily.map(d => d.users)), pmax = Math.max(1, ...a.pages.map(p => p.views));
  const langs = Object.fromEntries(a.langs.map(l => [l.lang || '?', l.users]));
  const short = (d?: string) => fmtDate(d, {day: 'numeric', month: 'short'});
  return <><AdminTabs cur="/admin/analytics" /><div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Usage analytics')}</h1>
    <div className="seg">{[7, 30, 90, 365].map(d => <Link key={d} to={`/admin/analytics?days=${d}`} className={d === days ? 'on' : ''}>{d} {t('d')}</Link>)}</div></div>
    <div className="kpis">
      <div className="kpi"><b>{a.users}</b><span>{t('people used the intranet ({d} days)', {d: a.days})}</span></div>
      <div className="kpi"><b>{a.staff ? Math.round(100 * a.users / a.staff) : 0}%</b><span>{t('of {n} staff in the directory', {n: a.staff})}</span></div>
      <div className="kpi"><b>{a.wau}</b><span>{t('active in the last 7 days')}</span></div>
      <div className="kpi"><b>{a.mobile_share}%</b><span>{t('page views from phones')}</span></div>
      <div className="kpi small"><b>{['en', 'ru', 'az'].map(l => `${l.toUpperCase()} ${langs[l] || 0}`).join(' · ')}</b><span>{t('people by language')}</span></div></div>
    <h2>{t('Active people per day')}</h2>
    <div className="panel"><div className="bars" role="img" aria-label={t('Active people per day')}>{a.daily.length ? a.daily.map(d =>
      <div key={d.day} className="dbar" style={{height: `${Math.max(2, 100 * d.users / max)}%`}}
        onMouseEnter={e => { const r = e.currentTarget.getBoundingClientRect();
          setTip({text: `${short(d.day)}: ${d.users} ${t('people')}, ${d.views} ${t('views')}`, left: r.left + r.width / 2 + scrollX, top: r.top + scrollY - 8}); }}
        onMouseLeave={() => setTip(null)} />) : <p className="muted">{t('No data yet')}</p>}</div>
      <div className="bars-axis"><span>{short(a.daily[0]?.day)}</span><span>{t('max {n}', {n: max})}</span><span>{short(a.daily[a.daily.length - 1]?.day)}</span></div></div>
    <div className="split2"><div><h2>{t('Most visited')}</h2><table className="list"><thead><tr><th>{t('Page')}</th><th>{t('Views')}</th><th>{t('People')}</th></tr></thead><tbody>
      {a.pages.map(p => <tr key={p.page}><td>{PAGE(p.page)}<div className="ibar" style={{width: `${100 * p.views / pmax}%`}}></div></td><td>{p.views}</td><td>{p.users}</td></tr>)}</tbody></table></div>
      <div><h2>{t('Adoption by department')}</h2><table className="list"><thead><tr><th>{t('Department')}</th><th>{t('People')}</th><th>%</th></tr></thead><tbody>
        {a.departments.map((d, i) => { const pc = d.staff ? Math.min(100, Math.round(100 * d.users / d.staff)) : 0;
          return <tr key={i}><td>{d.department || t('Other')}<div className="ibar" style={{width: `${pc}%`}}></div></td><td>{d.users} / {d.staff || '—'}</td><td>{d.staff ? pc + '%' : ''}</td></tr>; })}</tbody></table></div></div>
    <p className="muted">{t('Privacy: no names are stored — each person is counted by a salted hash; page addresses are stored without IDs.')}</p>
    {tip && <div className="tip" style={{left: tip.left, top: tip.top}}>{tip.text}</div>}</>;
}
