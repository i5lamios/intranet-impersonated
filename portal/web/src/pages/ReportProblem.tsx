// Report a problem to IT → a ServiceDesk Plus request (or e-mail to the helpdesk until the API key exists); my requests.
import {useEffect, useState} from 'react';
import {Link, useNavigate} from 'react-router';
import {api, fail, upload} from '../lib/api';
import {fmtDate, fmtTime, t} from '../lib/i18n';
import {guard} from '../lib/session';
import {toast} from '../lib/toast';
import {ErrorPanel, HelpQ, useLoad} from '../components/ui';

const CAT = (): Record<string, [string, string]> => ({computer: ['💻', t('Computer / laptop')], printer: ['🖨️', t('Printer / scanner')],
  mail: ['✉️', t('E-mail / Outlook')], phone: ['📞', t('Phone / 3CX')], network: ['📶', t('Network / Wi-Fi / VPN')],
  access: ['🔑', t('Password / access')], software: ['🧩', t('Software / application')], other: ['❔', t('Other')]});
const URG = (): Record<string, string> => ({blocked: t('I cannot work'), degraded: t('I can work, but it needs fixing'), request: t('Question or request')});
type Mine = {id: number; category: string; subject: string; sdp_id?: string | null; sent_by: string; created_at: string; url?: string | null; status: string};

// the page the user came from (for IT), kept across the form
const from = () => { try { const r = document.referrer ? new URL(document.referrer) : null; return r && r.origin === location.origin ? r.pathname : ''; } catch { return ''; } };

export function ReportProblem() {
  const nav = useNavigate();
  const {data: mine, error, reload} = useLoad(() => api<Mine[]>('/api/helpdesk/requests/mine'));
  const [file, setFile] = useState<string | null>(null), [fs, setFs] = useState(''), [busy, setBusy] = useState(false);
  useEffect(() => () => { guard.dirty = false; }, []);
  if (error) return <ErrorPanel error={error} />;
  const pick = async (e: React.ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (!f) return; setFs(t('Uploading…'));
    try { setFile((await upload<{name: string}>('/api/helpdesk/file', f)).name); setFs('✓ ' + f.name); } catch (err) { setFs(''); fail(err); } };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const form = e.currentTarget, f = form.elements as any; setBusy(true);
    try {
      const r = await api<{sdp_id?: string; sent_by: string}>('/api/helpdesk/requests', {method: 'POST', json: {category: f.category.value, urgency: f.urgency.value,
        subject: f.subject.value, description: f.description.value, location: f.location.value, file, page: from(), screen: `${screen.width}×${screen.height}`}});
      guard.dirty = false; toast(r.sdp_id ? t('Sent to IT — request #{n}', {n: r.sdp_id}) : t('Sent to IT by e-mail'));
      form.reset(); setFile(null); setFs(''); reload(); nav('/report-problem#mine', {replace: true});
    } catch (err) { fail(err); } finally { setBusy(false); }
  };
  const C = CAT(), U = URG();
  return <>
    <h1 style={{marginTop: 24}}>{t('Report a problem')} <HelpQ slug="report-problem" /></h1>
    <p className="muted">{t('Tell IT what is wrong. Your name, phone, office and browser are added for you, so IT can call you back.')}</p>
    <form className="panel stack" style={{maxWidth: 800}} onInput={() => { guard.dirty = true; }} onSubmit={submit}>
      <b>{t('What is it about?')}</b>
      <div className="kinds small">{Object.entries(C).map(([k, [i, l]], n) => <label className="kind" key={k}><input type="radio" name="category" value={k} defaultChecked={!n} /><span>{i} {l}</span></label>)}</div>
      <label>{t('In a few words')}<input name="subject" required minLength={3} maxLength={150} placeholder={t('e.g. The printer on the 2nd floor does not print')} style={{width: '100%'}} /></label>
      <label>{t('What happens? What did you try?')}<textarea name="description" required minLength={5} maxLength={6000} rows={5} placeholder={t('Error message, since when, does it happen to colleagues too')} /></label>
      <div className="row"><label>{t('How urgent?')}<select name="urgency" defaultValue="degraded">{Object.entries(U).map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select></label>
        <label style={{flex: 1}}>{t('Where are you?')}<input name="location" maxLength={200} placeholder={t('Office, floor, room or computer name')} style={{width: '100%'}} /></label></div>
      <div className="row"><label className="btn ghost small">📷 {t('Add a screenshot or photo')}<input type="file" accept="image/*" hidden onChange={pick} /></label><span className="muted">{fs}</span></div>
      <div className="row"><button className="btn" disabled={busy}>{busy ? t('Sending…') : t('Send to IT')}</button>
        <span className="muted">{t('Urgent and you cannot work? Also call IT.')}</span></div></form>
    <h2 id="mine">{t('My requests')}</h2>
    {!mine ? null : mine.length ? <table className="list"><tbody>{mine.map(r => <tr key={r.id}><td>{r.sdp_id ? (r.url ? <a href={r.url} target="_blank" rel="noopener">#{r.sdp_id}</a> : '#' + r.sdp_id) : '—'}</td>
      <td>{C[r.category]?.[0]} <b>{r.subject}</b></td><td className="muted">{fmtDate(r.created_at)} {fmtTime(r.created_at)}</td>
      <td>{r.status ? <span className="badge pub">{r.status}</span> : <span className="muted">{r.sent_by === 'mail' ? t('sent by e-mail') : ''}</span>}</td></tr>)}</tbody></table>
      : <p className="muted">{t('No requests yet.')} <Link to="/help">{t('IT Help Center')}</Link></p>}
  </>;
}
