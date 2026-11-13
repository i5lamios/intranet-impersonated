// Admin audit log for IT (AD group Intranet-IT-Editors): who changed what in the editor sections.
import {useState} from 'react';
import {api} from '../lib/api';
import {fmtDate, fmtTime, t} from '../lib/i18n';
import {session} from '../lib/session';
import {ErrorPanel, NeedRole, useLoad} from '../components/ui';
import {AdminTabs} from './Admin';

type Row = {id: number; at: string; username: string; name: string; area: string; action: string; target: string; detail: string; ip: string};
type Log = {areas: string[]; more: boolean; rows: Row[]};
const AREA = (): Record<string, string> => ({news: t('News'), banner: t('Emergency banner'), digest: t('Weekly e-mail'), birthdays: t('Birthdays'),
  people: t('People'), 'hse-board': t('HSE board'), 'hse-report': t('Hazard reports'), 'hse-action': t('Corrective actions'),
  cert: t('Certificates'), 'cert-type': t('Certificate types'), help: t('Help Center articles')});
const ACTION = (): Record<string, string> => ({created: t('created'), edited: t('edited'), deleted: t('deleted'), changed: t('changed'),
  switched: t('switched on / off'), imported: t('imported from a list'), reopened: t('reopened'), 'test sent': t('test sent')});

export const Audit = () => session.me?.roles.it ? <AuditLog /> : <NeedRole group="Intranet-IT-Editors" />;
function AuditLog() {
  const [area, setArea] = useState(''), [who, setWho] = useState(''), [q, setQ] = useState(''), [days, setDays] = useState(30), [offset, setOffset] = useState(0);
  const {data, error} = useLoad(() => api<Log>(`/api/admin/audit?days=${days}&offset=${offset}&area=${area}&who=${encodeURIComponent(q)}`), [area, q, days, offset]);
  if (error) return <ErrorPanel error={error} />;
  const A = AREA(), X = ACTION();
  return <><AdminTabs cur="/admin/audit" /><h1>{t('Audit log')}</h1>
    <p className="muted">{t('Every change made by an editor: news, banner, people, HSE, certificates and help articles. Kept for 2 years.')}</p>
    <form className="filters" onSubmit={e => { e.preventDefault(); setOffset(0); setQ(who.trim()); }}>
      <select value={area} onChange={e => { setOffset(0); setArea(e.target.value); }} aria-label={t('Section')}>
        <option value="">{t('All sections')}</option>{(data?.areas || Object.keys(A)).map(a => <option key={a} value={a}>{A[a] || a}</option>)}</select>
      <select value={days} onChange={e => { setOffset(0); setDays(+e.target.value); }} aria-label={t('Period')}>
        {[7, 30, 90, 365, 730].map(d => <option key={d} value={d}>{t('{d} days', {d})}</option>)}</select>
      <input value={who} onChange={e => setWho(e.target.value)} placeholder={t('Who: name or login')} />
      <button className="btn ghost">{t('Search')}</button></form>
    {!data ? null : data.rows.length ? <table className="list"><thead><tr><th>{t('When')}</th><th>{t('Who')}</th><th>{t('Section')}</th><th>{t('What')}</th></tr></thead>
      <tbody>{data.rows.map(r => <tr key={r.id}><td className="muted" style={{whiteSpace: 'nowrap'}}>{fmtDate(r.at, {day: 'numeric', month: 'short', year: 'numeric'})} {fmtTime(r.at)}</td>
        <td><b>{r.name || r.username}</b><div className="muted">{r.username}{r.ip ? ' · ' + r.ip : ''}</div></td><td>{A[r.area] || r.area}</td>
        <td>{X[r.action] || r.action}{r.target ? <> · <b>{r.target}</b></> : null}{r.detail ? <div className="muted">{r.detail}</div> : null}</td></tr>)}</tbody></table>
      : <p className="muted">{t('No changes in this period.')}</p>}
    <div className="row" style={{marginTop: 14}}>{offset > 0 && <button className="btn ghost small" onClick={() => setOffset(Math.max(0, offset - 100))}>← {t('Newer')}</button>}
      {data?.more && <button className="btn ghost small" onClick={() => setOffset(offset + 100)}>{t('Older')} →</button>}</div></>;
}
