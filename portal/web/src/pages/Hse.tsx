// HSE board, hazard / near-miss reporting, HSE team views (AD group Intranet-HSE-Editors).
import {useEffect, useState} from 'react';
import {Link, useNavigate, useSearchParams} from 'react-router';
import {api, fail, openFile, upload} from '../lib/api';
import {useEditor} from '../lib/editor';
import {fmtDate, fmtTime, t} from '../lib/i18n';
import {guard, session} from '../lib/session';
import {toast} from '../lib/toast';
import {ErrorPanel, HelpQ, Modal, NeedRole, useLoad} from '../components/ui';
import type {Person} from './People';
import {AdminTabs} from './Admin';

export const KIND = (): Record<string, string> => ({near_miss: t('Near miss'), unsafe_act: t('Unsafe act'), unsafe_condition: t('Unsafe condition'), good_practice: t('Good practice')});
const STATUS = (): Record<string, string> => ({new: t('New'), review: t('In review'), closed: t('Closed')});
const RISK = (): Record<string, string> => ({low: t('Low'), medium: t('Medium'), high: t('High')});

type Board = {days_without_lti: number | null; last_lti?: string | null; record_days?: number | null; manhours_ytd?: number | null;
  counts: Record<string, number>; target?: string; moment_title?: string; moment_html?: string};
type Report = {id: number; kind: string; location: string; happened_at: string; status: string; hse_comment?: string;
  description?: string; action?: string; photo?: string; anonymous?: boolean; reporter_name?: string; risk?: string;
  actions?: Action[]; actions_total?: number; actions_done?: number};
export type Action = {id: number; report_id: number; title: string; owner_id: string; owner_name: string; due: string; status: string;
  overdue: boolean; done_note?: string; done_at?: string; kind?: string; location?: string; description?: string; happened_at?: string; photo?: string; risk?: string};
const Due = ({a}: {a: Action}) => a.status === 'done' ? <span className="badge st-closed">✓ {t('Done')}</span>
  : <span className={`badge ${a.overdue ? 'st-new' : 'st-review'}`}>{a.overdue ? t('Overdue') : t('Due')} {fmtDate(a.due, {day: 'numeric', month: 'short'})}</span>;

export function HseBoard() {
  const {data, error, reload} = useLoad(() => Promise.all([api<Board>('/api/hse'), api<Report[]>('/api/hse/reports/mine'), api<Action[]>('/api/hse/actions/mine')]));
  const [done, setDone] = useState<Action | null>(null);
  useEffect(() => { if (data && location.hash === '#my-actions') document.getElementById('my-actions')?.scrollIntoView(); }, [!!data]);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [h, mine, acts] = data, K = KIND(), S = STATUS();
  return <>
    <div className="row" style={{justifyContent: 'space-between'}}><h1>{t('HSE board')} <HelpQ slug="report-hazard" /></h1>
      <Link className="btn" to="/hse/report">⚠️ {t('Report a hazard')}</Link></div>
    <div className="hse-big"><div className="hse-days big"><b className={h.days_without_lti == null ? 'na' : ''}>{h.days_without_lti ?? t('not set')}</b><span>{t('days without a lost-time incident')}</span>
      {h.last_lti && <small>{t('last LTI: {d}', {d: fmtDate(h.last_lti)})}</small>}</div>
      <div className="hse-grid">
        {!!h.record_days && <div className="kpi"><b>{h.record_days}</b><span>{t('best record, days')}</span></div>}
        {!!h.manhours_ytd && <div className="kpi"><b>{Number(h.manhours_ytd).toLocaleString()}</b><span>{t('man-hours this year')}</span></div>}
        {Object.entries(K).map(([k, label]) => <div className="kpi" key={k}><b>{h.counts[k]}</b><span>{label} · {t('this year')}</span></div>)}
      </div></div>
    {h.target && <div className="panel hse-target">🎯 {h.target}</div>}
    {/* safety moment: editor HTML, sanitised by the server */}
    {h.moment_title && <article><div className="inner"><span className="badge pub">{t('Safety moment')}</span><h1>{h.moment_title}</h1>
      <div className="prose" dangerouslySetInnerHTML={{__html: h.moment_html || ''}} /></div></article>}
    {acts.length > 0 && <><h2 id="my-actions">{t('My HSE actions')}</h2><div className="reports">{acts.map(a => <div className={`panel report action ${a.status}`} key={a.id}>
      <div className="row" style={{justifyContent: 'space-between'}}><b>{a.title}</b><Due a={a} /></div>
      <p className="muted">#{a.report_id} · {K[a.kind!]} · {a.location} · {fmtDate(a.happened_at)}</p><p>{a.description}</p>
      {a.status === 'done' ? <p className="muted"><b>{t('What was done')}:</b> {a.done_note}</p>
        : <div className="row"><button className="btn small" onClick={() => setDone(a)}>✓ {t('Mark done')}</button>
          {a.photo && <button className="btn ghost small" onClick={() => openFile('/api/hse/photo/' + a.photo)}>📷 {t('Photo')}</button>}</div>}</div>)}</div></>}
    {done && <DoneDialog a={done} onClose={() => setDone(null)} onDone={reload} />}
    <h2>{t('My reports')}</h2>{mine.length ? <table className="list"><tbody>{mine.map(r => <tr key={r.id}><td>#{r.id}</td><td>{K[r.kind]}</td><td>{r.location}</td>
      <td className="muted">{fmtDate(r.happened_at)}</td><td><span className={`badge st-${r.status}`}>{S[r.status]}</span></td>
      <td className="muted">{r.actions_total ? t('Actions {d}/{n}', {d: r.actions_done, n: r.actions_total}) : ''}</td><td className="muted">{r.hse_comment}</td></tr>)}</tbody></table>
      : <p className="muted">{t('You have not reported anything yet. Every report helps — thank you!')}</p>}
  </>;
}

export function HseReport() {
  const nav = useNavigate();
  const now = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  const [photoName, setPhoto] = useState<string | null>(null), [phs, setPhs] = useState('');
  useEffect(() => () => { guard.dirty = false; }, []);
  const pick = async (e: React.ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (!f) return; setPhs(t('Uploading…'));
    try { setPhoto((await upload<{name: string}>('/api/hse/photo', f)).name); setPhs('✓ ' + f.name); } catch (err) { setPhs(''); fail(err); } };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any;
    try {
      const r = await api<{id: number}>('/api/hse/reports', {method: 'POST', json: {kind: f.kind.value, happened_at: f.happened_at.value, location: f.location.value,
        description: f.description.value, action: f.action.value, photo: photoName, anonymous: f.anonymous.checked}});
      guard.dirty = false; toast(t('Thank you! Report #{id} sent to HSE', {id: r.id})); nav('/hse');
    } catch (err) { fail(err); }
  };
  return <>
    <p style={{marginTop: 20}}><Link to="/hse">← {t('HSE board')}</Link></p><h1>{t('Report a hazard')} <HelpQ slug="report-hazard" /></h1>
    <p className="muted">{t('Saw something unsafe, a near miss, or good practice? Tell HSE — it takes a minute.')}</p>
    <form id="rf" className="panel stack" style={{maxWidth: 760}} onInput={() => { guard.dirty = true; }} onSubmit={submit}>
      <div className="kinds">{Object.entries(KIND()).map(([k, l], i) => <label className="kind" key={k}><input type="radio" name="kind" value={k} defaultChecked={!i} /><span>{['⚠️', '🚶', '🏗️', '👍'][i]} {l}</span></label>)}</div>
      <div className="row"><label>{t('When')}<input type="datetime-local" name="happened_at" defaultValue={now} max={now} required /></label>
        <label style={{flex: 1}}>{t('Where')}<input name="location" required maxLength={200} placeholder={t('Site, office, vessel, area')} style={{width: '100%'}} /></label></div>
      <label>{t('What happened / what did you see?')}<textarea name="description" required minLength={10} maxLength={4000} rows={5} /></label>
      <label>{t('Immediate action taken (if any)')}<textarea name="action" maxLength={2000} rows={2} /></label>
      <div className="row"><label className="btn ghost small">📷 {t('Add a photo')}<input type="file" accept="image/*" capture="environment" id="ph" hidden onChange={pick} /></label><span id="phs" className="muted">{phs}</span></div>
      <label className="check"><input type="checkbox" name="anonymous" /> {t('Report anonymously (your name is not stored)')}</label>
      <div className="row"><button className="btn">{t('Send to HSE')}</button></div></form>
  </>;
}


function DoneDialog({a, onClose, onDone}: {a: Action; onClose: () => void; onDone: () => void}) {
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const note = (e.currentTarget.elements as any).note.value;
    try { await api(`/api/hse/actions/${a.id}/done`, {method: 'POST', json: {note}}); toast(t('Thank you! HSE has been told')); onClose(); onDone(); } catch (err) { fail(err); }
  };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{t('Mark done')}</h2><p><b>{a.title}</b></p>
    <form className="stack" onSubmit={submit}><label>{t('What was done?')}<textarea name="note" required minLength={3} maxLength={2000} rows={4} autoFocus /></label>
      <div className="row"><button className="btn">{t('Done')}</button><button type="button" className="btn ghost" data-close>{t('Close')}</button></div></form></Modal>;
}

const HseOnly = ({children}: {children: React.ReactNode}) => session.me?.roles.hse ? <>{children}</> : <NeedRole group="Intranet-HSE-Editors" />;

export const HseReports = () => <HseOnly><Reports /></HseOnly>;
function Reports() {
  const [params] = useSearchParams(), st = params.get('status') || '';
  const {data, error, reload} = useLoad(() => Promise.all([api<Report[]>('/api/hse/reports' + (st ? '?status=' + st : '')), api<Board & {actions_open: number; actions_overdue: number}>('/api/hse'),
    api<{people: Person[]}>('/api/directory')]), [st]);
  const [dlg, setDlg] = useState<null | {r: Report; a?: Action}>(null);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [rows, h, dir] = data, K = KIND(), S = STATUS(), R = RISK();
  const save = async (r: Report, el: HTMLElement) => { try { await api('/api/hse/reports/' + r.id, {method: 'PUT',
    json: {status: el.querySelector<HTMLSelectElement>('.st')!.value, risk: el.querySelector<HTMLSelectElement>('.rk')!.value,
      hse_comment: el.querySelector<HTMLInputElement>('.cm')!.value}}); toast(t('Saved')); reload(); } catch (err) { fail(err); } };
  const act = async (path: string, method: string, ok: string) => { try { await api(path, {method}); toast(ok); reload(); } catch (err) { fail(err); } };
  return <><AdminTabs cur="/admin/hse/reports" /><h1>{t('Reports')}</h1>
    <div className="kpis" style={{marginBottom: 14}}><div className="kpi"><b>{h.actions_open}</b><span>{t('open actions')}</span></div>
      <Link className="kpi expired" to="/admin/hse/reports?status=overdue"><b>{h.actions_overdue}</b><span>{t('overdue actions')}</span></Link></div>
    <div className="seg">{[['', t('All')], ...Object.entries(S), ['overdue', t('Overdue actions')]].map(([k, l]) => <Link key={k} to={`/admin/hse/reports${k ? '?status=' + k : ''}`} className={k === st ? 'on' : ''}>{l}</Link>)}</div>
    <div className="reports">{rows.length ? rows.map(r => <div className="panel report" key={r.id}>
      <div className="row" style={{justifyContent: 'space-between'}}><b>#{r.id} · {K[r.kind]} · {r.location}</b>
        <span className="muted">{fmtDate(r.happened_at)} {fmtTime(r.happened_at)} · {r.anonymous ? t('anonymous') : r.reporter_name}</span></div>
      <p>{r.description}</p>{r.action && <p className="muted"><b>{t('Immediate action')}:</b> {r.action}</p>}
      {r.photo && <button className="btn ghost small" onClick={() => openFile('/api/hse/photo/' + r.photo)}>📷 {t('Photo')}</button>}
      <div className="actions-box"><b>{t('Corrective actions')}</b>
        {r.actions!.map(a => <div className="arow" key={a.id}><span className="at">{a.title}<small>{a.owner_name}{a.done_note ? ' · ' + a.done_note : ''}</small></span><Due a={a} />
          {a.status === 'open' ? <button className="btn ghost small" onClick={() => setDlg({r, a})}>{t('Edit')}</button>
            : <button className="btn ghost small" onClick={() => act(`/api/hse/actions/${a.id}/reopen`, 'POST', t('Reopened'))}>{t('Reopen')}</button>}
          <button className="btn ghost small" title={t('Delete')} onClick={() => confirm(t('Delete this action?')) && act(`/api/hse/actions/${a.id}`, 'DELETE', t('Deleted'))}>✕</button></div>)}
        <button className="btn ghost small" onClick={() => setDlg({r})}>+ {t('Add action')}</button></div>
      <div className="row"><select className="st" defaultValue={r.status}>{Object.entries(S).map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select>
        <select className="rk" defaultValue={r.risk || ''} title={t('Risk')}><option value="">{t('Risk')}: —</option>{Object.entries(R).map(([k, l]) => <option key={k} value={k}>{t('Risk')}: {l}</option>)}</select>
        <input className="cm" style={{flex: 1}} maxLength={4000} placeholder={t('Comment for the reporter')} defaultValue={r.hse_comment} />
        <button className="btn small sv" onClick={e => save(r, (e.currentTarget as HTMLElement).closest('.report')!)}>{t('Save')}</button></div>
      {!r.anonymous && <p className="muted" style={{fontSize: 13}}>{t('The reporter is told by e-mail when the status or comment changes.')}</p>}</div>)
      : <div className="panel empty">{t('No reports')}</div>}</div>
    {dlg && <ActionDialog {...dlg} people={dir.people} onClose={() => setDlg(null)} onDone={reload} />}</>;
}

function ActionDialog({r, a, people, onClose, onDone}: {r: Report; a?: Action; people: Person[]; onClose: () => void; onDone: () => void}) {
  const week = new Date(Date.now() + 7 * 864e5).toISOString().slice(0, 10);
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any;
    const p = people.find(x => x.name === f.who.value) || (a && a.owner_name === f.who.value ? {id: a.owner_id} : null);
    if (!p) return toast(t('Choose a person from the list'));
    try { await api(a ? `/api/hse/actions/${a.id}` : `/api/hse/reports/${r.id}/actions`, {method: a ? 'PUT' : 'POST',
      json: {title: f.title.value, owner_id: p.id, due: f.due.value}}); toast(a ? t('Saved') : t('Action added — the owner gets an e-mail')); onClose(); onDone(); } catch (err) { fail(err); }
  };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{a ? t('Edit action') : t('Add action')}</h2><p className="muted">#{r.id} · {KIND()[r.kind]} · {r.location}</p>
    <form className="stack" onSubmit={submit}><label>{t('What must be done')}<textarea name="title" required minLength={3} maxLength={500} rows={3} defaultValue={a?.title} autoFocus /></label>
      <label>{t('Owner')}<input name="who" list="ppl" required defaultValue={a?.owner_name || ''} autoComplete="off" />
        <datalist id="ppl">{people.map(p => <option key={p.id} value={p.name}>{p.department}</option>)}</datalist></label>
      <label>{t('Due date')}<input type="date" name="due" required defaultValue={a?.due || week} /></label>
      <div className="row"><button className="btn">{t('Save')}</button><button type="button" className="btn ghost" data-close>{t('Close')}</button></div></form></Modal>;
}

export const HseAdmin = () => <HseOnly><BoardSettings /></HseOnly>;
function BoardSettings() {
  const {data: h, error} = useLoad(() => api<Board>('/api/hse'));
  const [ref, ed] = useEditor(h ? h.moment_html || '' : undefined, {minHeight: 280, simple: true});
  if (error) return <ErrorPanel error={error} />;
  if (!h) return null;
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any, num = (v: string) => v === '' ? null : Number(v);
    if (!ed) return;
    await ed.uploadImages();
    try { await api('/api/hse/board', {method: 'PUT', json: {last_lti: f.last_lti.value || null, record_days: num(f.record_days.value),
      manhours_ytd: num(f.manhours_ytd.value), target: f.target.value, moment_title: f.moment_title.value, moment_html: ed.getContent()}});
      guard.dirty = false; toast(t('Saved')); } catch (err) { fail(err); }
  };
  return <><AdminTabs cur="/admin/hse" /><h1>{t('Board settings')}</h1><form id="hf" className="stack" style={{maxWidth: 900}} onInput={() => { guard.dirty = true; }} onSubmit={submit}>
    <div className="panel row">
      <label>{t('Date of the last lost-time incident')}<input type="date" name="last_lti" defaultValue={h.last_lti || ''} /></label>
      <label>{t('Best record, days')}<input type="number" min="0" name="record_days" defaultValue={h.record_days ?? ''} /></label>
      <label>{t('Man-hours this year')}<input type="number" min="0" name="manhours_ytd" defaultValue={h.manhours_ytd ?? ''} /></label></div>
    <label>{t('Target / message of the month')}<input name="target" maxLength={200} defaultValue={h.target} style={{width: '100%'}} /></label>
    <label>{t('Safety moment — title')}<input name="moment_title" maxLength={200} defaultValue={h.moment_title} style={{width: '100%'}} /></label>
    <div className="sheet"><textarea id="mm" ref={ref} /></div>
    <div className="row"><button className="btn">{t('Save')}</button></div></form></>;
}
