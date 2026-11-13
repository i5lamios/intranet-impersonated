// Certificates & training: my certificates; HSE dashboard, matrix, editing, types, import.
import {useState} from 'react';
import {api, fail, openFile, upload} from '../lib/api';
import {fmtDate, norm, t} from '../lib/i18n';
import {session} from '../lib/session';
import {toast} from '../lib/toast';
import {ErrorPanel, HelpQ, Modal, NeedRole, useLoad} from '../components/ui';
import {AdminTabs} from './Admin';
import type {Person} from './People';

const STATUS = (): Record<string, string> => ({expired: t('Expired'), d30: t('Due ≤ 30 days'), d60: t('Due ≤ 60 days'), d90: t('Due ≤ 90 days'), valid: t('Valid'), none: t('No expiry')});
type Cert = {id: number; person_id: string; name: string; department?: string; type_id: number; type_name: string; number?: string; provider?: string;
  issued?: string | null; expires?: string | null; status: string; days_left?: number | null; file?: string | null; notes?: string};
type CType = {id: number; name: string; validity_months?: number | null; sort: number; active: boolean};
const Badge = ({c}: {c: Cert}) => <span className={`cert ${c.status}`}>{STATUS()[c.status]}{c.days_left != null && c.days_left >= 0 && c.status !== 'valid' ? ` · ${c.days_left} ${t('d')}` : ''}</span>;

export function MyCerts() {
  const {data: certs, error} = useLoad(() => api<Cert[]>('/api/certs/mine'));
  if (error) return <ErrorPanel error={error} />;
  if (!certs) return null;
  return <><h1>{t('My certificates')} <HelpQ slug="my-certificates" /></h1>
    <p className="muted">{t('Training and certificates recorded by HSE. Something missing or wrong? Tell HSE.')}</p>
    {certs.length ? <table className="list"><thead><tr><th>{t('Certificate')}</th><th>{t('Number')}</th><th>{t('Issued')}</th><th>{t('Expires')}</th><th>{t('Status')}</th><th></th></tr></thead><tbody>
      {certs.map(c => <tr key={c.id}><td><b>{c.type_name}</b></td><td>{c.number}</td><td>{fmtDate(c.issued)}</td><td>{fmtDate(c.expires) || '—'}</td><td><Badge c={c} /></td>
        <td>{c.file && <button className="btn ghost small" onClick={() => openFile(`/api/certs/${c.id}/file`)}>{t('Scan')}</button>}</td></tr>)}</tbody></table>
      : <div className="panel empty">{t('No certificates recorded yet')}</div>}</>;
}

type All = {certs: Cert[]; summary: Record<string, number>; people: number};
const loadAll = () => Promise.all([api<All>('/api/certs'), api<CType[]>('/api/certs/types'), api<{people: Person[]}>('/api/directory')]);
const HseOnly = ({children}: {children: React.ReactNode}) => session.me?.roles.hse ? <>{children}</> : <NeedRole group="Intranet-HSE-Editors" />;

export const CertAdmin = () => <HseOnly><Dashboard /></HseOnly>;
function Dashboard() {
  const {data, error, reload} = useLoad(loadAll);
  const [q, setQ] = useState(''), [st, setSt] = useState(''), [ty, setTy] = useState('');
  const [dlg, setDlg] = useState<null | {c?: Cert}>(null), [imp, setImp] = useState(false);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [all, types, dir] = data, S = STATUS(), sum = all.summary, w = norm(q);
  const rows = all.certs.filter(c => (!st || c.status === st) && (!ty || c.type_id === +ty) && (!w || norm(`${c.name} ${c.department} ${c.type_name}`).includes(w)));
  return <><AdminTabs cur="/admin/training" /><div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Certificates dashboard')}</h1>
    <div className="row"><button className="btn ghost" id="imp" onClick={() => setImp(true)}>{t('Import from Excel')}</button><button className="btn" id="add" onClick={() => setDlg({})}>+ {t('Add certificate')}</button></div></div>
    <div className="kpis">{['expired', 'd30', 'd60', 'd90', 'valid'].map(k => <a key={k} className={`kpi ${k}`} href="#" onClick={e => { e.preventDefault(); setSt(k); }}><b>{sum[k]}</b><span>{S[k]}</span></a>)}
      <div className="kpi"><b>{all.people}</b><span>{t('people with records')}</span></div></div>
    <div className="filters"><input id="cq" placeholder={t('Name, department, certificate')} value={q} onChange={e => setQ(e.target.value)} />
      <select id="cst" value={st} onChange={e => setSt(e.target.value)}><option value="">{t('All statuses')}</option>{Object.entries(S).map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select>
      <select id="cty" value={ty} onChange={e => setTy(e.target.value)}><option value="">{t('All certificates')}</option>{types.map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select></div>
    <table className="list"><thead><tr><th>{t('Name')}</th><th>{t('Department')}</th><th>{t('Certificate')}</th><th>{t('Expires')}</th><th>{t('Status')}</th><th></th></tr></thead><tbody id="crows">
      {rows.length ? rows.map(c => <tr key={c.id}><td><b>{c.name}</b></td><td className="muted">{c.department}</td><td>{c.type_name}</td><td>{fmtDate(c.expires) || '—'}</td><td><Badge c={c} /></td>
        <td><button className="btn ghost small" onClick={() => setDlg({c})}>{t('Edit')}</button></td></tr>)
        : <tr><td colSpan={6} className="empty">{t('Nothing found')}</td></tr>}</tbody></table>
    {dlg && <CertDialog types={types} people={dir.people} c={dlg.c} onClose={() => setDlg(null)} onDone={reload} />}
    {imp && <ImportDialog onClose={() => setImp(false)} onDone={reload} />}</>;
}

export const CertMatrix = () => <HseOnly><Matrix /></HseOnly>;
function Matrix() {
  const {data, error} = useLoad(loadAll);
  const [d, setD] = useState('');
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [all, types] = data;
  const used = types.filter(x => all.certs.some(c => c.type_id === x.id));
  const people = new Map<string, {name: string; department?: string; certs: Record<number, Cert>}>();
  all.certs.forEach(c => { if (!people.has(c.person_id)) people.set(c.person_id, {name: c.name, department: c.department, certs: {}});
    const p = people.get(c.person_id)!, cur = p.certs[c.type_id];
    if (!cur || (c.expires || '9999') > (cur.expires || '9999')) p.certs[c.type_id] = c; });
  const depts = [...new Set([...people.values()].map(p => p.department || ''))].sort();
  return <><AdminTabs cur="/admin/training/matrix" /><h1>{t('Training matrix')}</h1>
    <div className="filters"><select id="md" value={d} onChange={e => setD(e.target.value)}><option value="">{t('All departments')}</option>{depts.map(x => <option key={x}>{x}</option>)}</select>
      <span className="legend">{['expired', 'd30', 'd60', 'valid'].map(k => <span key={k} className={`cert ${k}`}>{STATUS()[k]}</span>).reduce<React.ReactNode[]>((a, x) => a.length ? [...a, ' ', x] : [x], [])}</span></div>
    {!used.length && <div className="panel empty">{t('No certificates recorded yet')}</div>}
    <div className="matrix-wrap" hidden={!used.length}><table className="matrix"><thead><tr><th>{t('Name')}</th>{used.map(x => <th key={x.id}><span>{x.name}</span></th>)}</tr></thead><tbody id="mrows">
      {[...people.values()].filter(p => !d || p.department === d).sort((a, b) => a.name.localeCompare(b.name)).map(p =>
        <tr key={p.name + p.department}><td><b>{p.name}</b><small>{p.department}</small></td>{used.map(x => { const c = p.certs[x.id];
          return <td key={x.id} className={c ? 'cell ' + c.status : ''} title={c ? fmtDate(c.expires) || STATUS().none : ''}>{c ? (c.expires ? c.expires.slice(2, 7).split('-').reverse().join('/') : '✓') : ''}</td>; })}</tr>)}</tbody></table></div></>;
}

export const CertTypes = () => <HseOnly><Types /></HseOnly>;
function Types() {
  const {data: types, error, reload} = useLoad(() => api<CType[]>('/api/certs/types'));
  if (error) return <ErrorPanel error={error} />;
  if (!types) return null;
  const save = async (x: CType, tr: HTMLTableRowElement) => {
    const v = (c: string) => tr.querySelector<HTMLInputElement>(c)!;
    const body = {name: v('.n').value, validity_months: v('.v').value ? +v('.v').value : null, sort: +v('.s').value || 100, active: v('.a').checked};
    try { await api('/api/certs/types' + (x.id ? '/' + x.id : ''), {method: x.id ? 'PUT' : 'POST', json: body}); toast(t('Saved')); if (!x.id) reload(); } catch (err) { fail(err); }
  };
  return <><AdminTabs cur="/admin/training/types" /><h1>{t('Certificate types')}</h1>
    <p className="muted">{t('Validity is used to fill the expiry date from the issue date.')}</p>
    <table className="list"><thead><tr><th>{t('Name')}</th><th>{t('Validity, months')}</th><th>{t('Order')}</th><th>{t('Active')}</th><th></th></tr></thead><tbody>
      {[...types, {id: 0, name: '', validity_months: null, sort: 100, active: true}].map(x => <tr key={x.id + ':' + types.length}>
        <td><input className="n" defaultValue={x.name} placeholder={x.id ? '' : t('New type')} style={{width: '100%'}} /></td>
        <td><input className="v" type="number" min="1" max="240" defaultValue={x.validity_months ?? ''} style={{width: 90}} /></td>
        <td><input className="s" type="number" defaultValue={x.sort} style={{width: 80}} /></td><td><input className="a" type="checkbox" defaultChecked={x.active} /></td>
        <td><button className="btn small" onClick={e => save(x, e.currentTarget.closest('tr')!)}>{x.id ? t('Save') : t('Add')}</button></td></tr>)}</tbody></table></>;
}

function CertDialog({types, people, c: c0, onClose, onDone}: {types: CType[]; people: Person[]; c?: Cert; onClose: () => void; onDone: () => void}) {
  const c = c0 || {person_id: '', type_id: types[0]?.id, number: '', provider: '', issued: null, expires: null, file: null, notes: ''} as Partial<Cert>;
  const [file, setFile] = useState(c.file), [fs, setFs] = useState(c.file ? '✓ ' + t('attached') : '');
  const pick = async (e: React.ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (!f) return;
    try { setFile((await upload<{name: string}>('/api/certs/file', f)).name); setFs('✓ ' + f.name); } catch (err) { fail(err); } };
  const del = async () => { if (!confirm(t('Delete this certificate?'))) return;
    try { await api('/api/certs/' + c.id, {method: 'DELETE'}); onClose(); onDone(); } catch (err) { fail(err); } };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any;
    const p = people.find(x => x.name === f.who.value) || (c.id && c.name === f.who.value ? {id: c.person_id} : null);
    if (!p) return toast(t('Choose a person from the list'));
    const body = {person_id: p.id, type_id: +f.type_id.value, issued: f.issued.value || null, expires: f.expires.value || null,
      number: f.number.value, provider: f.provider.value, notes: f.notes.value, file};
    try { await api('/api/certs' + (c.id ? '/' + c.id : ''), {method: c.id ? 'PUT' : 'POST', json: body}); onClose(); toast(t('Saved')); onDone(); } catch (err) { fail(err); }
  };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{c.id ? t('Edit certificate') : t('Add certificate')}</h2><form id="cf" className="stack" onSubmit={submit}>
    <label>{t('Person')}<input name="who" list="ppl" required defaultValue={c.id ? c.name : ''} autoComplete="off" />
      <datalist id="ppl">{people.map(p => <option key={p.id} value={p.name}>{p.department}</option>)}</datalist></label>
    <label>{t('Certificate')}<select name="type_id" defaultValue={c.type_id}>{types.filter(x => x.active || x.id === c.type_id).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
    <div className="row"><label>{t('Issued')}<input type="date" name="issued" defaultValue={c.issued || ''} /></label>
      <label>{t('Expires')}<input type="date" name="expires" defaultValue={c.expires || ''} /></label></div>
    <p className="muted" style={{margin: 0}}>{t('Leave “Expires” empty to calculate it from the certificate validity.')}</p>
    <div className="row"><label>{t('Number')}<input name="number" maxLength={100} defaultValue={c.number} /></label>
      <label style={{flex: 1}}>{t('Training provider')}<input name="provider" maxLength={200} defaultValue={c.provider} style={{width: '100%'}} /></label></div>
    <label>{t('Notes')}<input name="notes" maxLength={1000} defaultValue={c.notes} /></label>
    <div className="row"><label className="btn ghost small">📎 {t('Scan (PDF or photo)')}<input type="file" accept="application/pdf,image/*" id="cfile" hidden onChange={pick} /></label><span id="cfs" className="muted">{fs}</span></div>
    <div className="row"><button className="btn">{t('Save')}</button><button type="button" className="btn ghost" data-close>{t('Close')}</button>
      {c.id && <button type="button" className="btn danger" id="cdel" style={{marginLeft: 'auto'}} onClick={del}>{t('Delete')}</button>}</div></form></Modal>;
}

function ImportDialog({onClose, onDone}: {onClose: () => void; onDone: () => void}) {
  const [text, setText] = useState(''), [res, setRes] = useState('');
  const run = async () => { try { const r = await api<{saved: number; problems: string[]}>('/api/certs/import', {method: 'POST', json: {text}});
    setRes(t('{n} saved', {n: r.saved}) + (r.problems.length ? ` · ${t('not imported')}: ${r.problems.join(' | ')}` : ''));
    if (r.saved) onDone(); } catch (err) { fail(err); } };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{t('Import from Excel')}</h2>
    <p className="muted">{t('Copy rows from Excel: person (user name, e-mail or full name), certificate type (exact name), issued, expires, number. Dates as 15.03.2026 or 2026-03-15.')}</p>
    <textarea id="it" rows={10} style={{width: '100%'}} placeholder={'admin.user\tBOSIET / FOET\t15.03.2024\t15.03.2028\tA-1234'} value={text} onChange={e => setText(e.target.value)} />
    <div className="row"><button className="btn" id="go" onClick={run}>{t('Import')}</button><button className="btn ghost" data-close>{t('Close')}</button><span id="ir" className="muted">{res}</span></div></Modal>;
}
