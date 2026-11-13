// IT: how the meeting rooms are used, and the QR signs for the doors.
import {useState} from 'react';
import {Link, useSearchParams} from 'react-router';
import {api} from '../lib/api';
import {dayName, t} from '../lib/i18n';
import {session} from '../lib/session';
import {ErrorPanel, NeedRole, useLoad} from '../components/ui';
import {AdminTabs} from './Admin';

// one measure, one hue: the title names it, each column carries its value on hover and the table below repeats the numbers
function Bars({title, rows}: {title: string; rows: {l: string; v: number}[]}) {
  const max = Math.max(10, ...rows.map(r => r.v));
  return <section className="panel"><h3>{title}</h3><div className="vbars">{rows.map(r => <div key={r.l} className="vb" title={`${r.l}: ${r.v}%`}>
    <div className="vt"><i style={{height: `${r.v / max * 100}%`}}>{r.v === max && r.v ? <span>{r.v}%</span> : null}</i></div><b>{r.l}</b></div>)}</div>
    <details><summary>{t('Show as table')}</summary><table className="list"><tbody>{rows.map(r => <tr key={r.l}><td>{r.l}</td><td>{r.v}%</td></tr>)}</tbody></table></details></section>;
}

type Report = {workdays: number; missing: number; release_on: boolean; rooms: {name: string; use: number; meetings: number; hours: number}[];
  intranet: {booked: number; checked_in: number; no_checkin: number; released: number}; hours: {h: number; use: number}[]; weekdays: {d: number; use: number}[]};
type Sign = {name: string; url: string; svg: string};

export const RoomsAdmin = () => session.me?.roles.it ? <Usage /> : <NeedRole group="Intranet-IT-Editors" />;
function Usage() {
  const [params] = useSearchParams(), days = +(params.get('days') || 0) || 30;
  const {data, error} = useLoad(() => Promise.all([api<Report>('/api/rooms/report?days=' + days), api<Sign[]>('/api/rooms/signs')]), [days]);
  const [one, setOne] = useState<number | null>(null);
  if (error) return <><AdminTabs cur="/admin/rooms" /><ErrorPanel error={error} /></>;
  if (!data) return <><AdminTabs cur="/admin/rooms" /><p className="muted">{t('Loading…')}</p></>;
  const [a, signs] = data, n = a.intranet;
  const wd = (i: number) => { const x = new Date(2024, 0, 1); x.setDate(1 + i); return dayName(x, 'short'); };
  // one sign on its own: the others are hidden while printing
  const printOne = (i: number) => {
    setOne(i); document.body.classList.add('print-one');
    addEventListener('afterprint', () => { document.body.classList.remove('print-one'); setOne(null); }, {once: true});
    setTimeout(() => print(), 50);
  };
  return <><AdminTabs cur="/admin/rooms" /><div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Meeting rooms')}</h1>
    <div className="seg">{[7, 30, 90].map(d => <Link key={d} to={`/admin/rooms?days=${d}`} className={d === days ? 'on' : ''}>{t('{n} days', {n: d})}</Link>)}</div></div>
    <p className="muted">{t('Working hours 8:00–20:00, Monday to Friday, {n} working days.', {n: a.workdays})}{a.missing ? ' ' + t('{n} days could not be read from Exchange.', {n: a.missing}) : ''}</p>
    <div className="rstats">{a.rooms.map(r => <div key={r.name} className="panel rstat"><small>{r.name}</small><b>{r.use}%</b><span>{t('of working hours in use')}</span><span>{t('{n} meetings, {h} hours', {n: r.meetings, h: r.hours})}</span></div>)}
      <div className="panel rstat"><small>{t('Booked on the intranet')}</small><b>{n.booked}</b><span>{t('Checked in: {a}', {a: n.checked_in})}</span><span>{t('No check-in: {a}', {a: n.no_checkin})}</span>{a.release_on && <span>{t('Released: {a}', {a: n.released})}</span>}</div></div>
    <div className="rcharts"><Bars title={t('Busiest hours, share of rooms in use')} rows={a.hours.map(h => ({l: h.h + ':00', v: h.use}))} />
      <Bars title={t('Busiest days, share of working hours in use')} rows={a.weekdays.map(w => ({l: wd(w.d), v: w.use}))} /></div>
    <div className="row noprint" style={{justifyContent: 'space-between', marginTop: 22}}><h2>{t('Door signs')}</h2><button className="btn" id="pr" onClick={() => print()}>{t('Print signs')}</button></div>
    <p className="muted noprint">{t('One A4 sign per room. Scanning opens the room page: status, check-in and booking. It needs the office network or VPN.')}</p>
    <div className="dsigns">{signs.map((s, i) => <div key={s.url} className={`dsign${one === i ? ' pone' : ''}`}><button className="btn small ghost dpr" onClick={() => printOne(i)}>{t('Print')}</button>
      <img src="/logo.png" alt="Company" /><h2>{s.name}</h2>
      {/* QR code: SVG made by the server (segno) from the room URL */}
      <div className="qr" dangerouslySetInnerHTML={{__html: s.svg}} />
      <p><b>Scan to check in or book</b><br />Qeydiyyat və ya sifariş üçün skan edin<br />Сканируйте, чтобы отметиться или забронировать</p></div>)}</div></>;
}
