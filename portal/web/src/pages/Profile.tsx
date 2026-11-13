// My profile: own AD contact details (mobile, office and photo editable; office phone and extension read-only) + links.
import {useEffect, useState} from 'react';
import {Link} from 'react-router';
import {api, fail, upload} from '../lib/api';
import {fmtDate, t} from '../lib/i18n';
import {pushState, pushToggle, type PushState} from '../lib/push';
import {guard} from '../lib/session';
import {toast} from '../lib/toast';
import {PasskeySection} from '../components/Passkeys';
import {ErrorPanel, HelpQ, initials, photo, useLoad} from '../components/ui';

type P = {id?: string; name: string; title?: string; department?: string; mail?: string; extension?: string; phone?: string; mobile?: string;
  office?: string; offices: string[]; editable: boolean; protected?: boolean; has_photo?: boolean;
  history: {field: string; new_value?: string; changed_at: string}[]};
const FIELD = (): Record<string, string> => ({telephoneNumber: t('Office phone'), mobile: t('Mobile'), physicalDeliveryOfficeName: t('Office'), thumbnailPhoto: t('Photo')});
const pushLabel = (s: PushState | null) => s ? ({on: t('On in this browser — tap to turn off'), off: t('Off — tap to turn on'), denied: t('Blocked in browser settings'),
  unsupported: t('Not supported in this browser'), ios: t('On iPhone: add the intranet to the home screen first')})[s] : '';

export function Profile() {
  const {data: p, error, reload} = useLoad(() => api<P>('/api/profile'));
  const [ps, setPs] = useState<PushState | null>(null), [ph, setPh] = useState<string | null>(null);
  useEffect(() => { pushState().then(setPs); }, []);
  useEffect(() => { setPh(null); if (p?.has_photo && p.id) photo(p.id).then(setPh); }, [p]);
  useEffect(() => () => { guard.dirty = false; }, []);
  if (error) return <ErrorPanel error={error} />;
  if (!p) return null;
  const Ro = ({k, v}: {k: string; v?: string}) => <><dt>{k}</dt><dd>{v || '—'}</dd></>;
  const save = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any;
    try { const r = await api<{changed: string[]}>('/api/profile', {method: 'PUT', json: {mobile: f.mobile.value, office: f.office.value}});
      guard.dirty = false; toast(r.changed.length ? t('Saved') : t('Nothing changed')); } catch (err) { fail(err); }
  };
  const newPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => { const file = e.target.files?.[0]; if (!file) return;
    try { await upload('/api/profile/photo', file); toast(t('Photo updated')); setPh(URL.createObjectURL(file)); } catch (err) { fail(err); } };
  const delPhoto = async () => { if (!confirm(t('Remove your photo?'))) return;
    try { await api('/api/profile/photo', {method: 'DELETE'}); toast(t('Photo removed')); setPh(null); reload(); } catch (err) { fail(err); } };
  return <>
    <h1>{t('My profile')} <HelpQ slug="my-profile" /></h1>
    <div className="person panel"><div>{ph ? <img className="ph" id="ph" src={ph} alt="" /> : <div id="ph" className="ph">{initials(p.name)}</div>}
      {p.editable && <div className="row" style={{marginTop: 10}}><label className="btn ghost small">📷 {t('Change photo')}<input type="file" accept="image/*" id="pf" hidden onChange={newPhoto} /></label>
        {(p.has_photo || ph) && <button className="btn ghost small" id="pdel" onClick={delPhoto}>{t('Remove')}</button>}</div>}</div>
      <div><h2 style={{marginTop: 0}}>{p.name}</h2>
        <dl><Ro k={t('Title')} v={p.title} /><Ro k={t('Department')} v={p.department} /><Ro k={t('E-mail')} v={p.mail} />{p.extension && <Ro k={t('Extension')} v={p.extension} />}
          {p.phone && p.phone !== p.extension && <Ro k={t('Office phone')} v={p.phone} />}</dl>
        <p className="muted">{t('Name, title, department, office phone and extension are kept by HR and IT — ask them to change these.')}</p>
        <form id="pf2" className="stack" style={{maxWidth: 520}} onInput={() => { guard.dirty = true; }} onSubmit={save}>
          <label>{t('Mobile')}<input name="mobile" maxLength={40} defaultValue={p.mobile} disabled={!p.editable} placeholder="+994 50 000 00 00" /></label>
          <label>{t('Office')}<input name="office" maxLength={80} list="offs" defaultValue={p.office} disabled={!p.editable} />
            <datalist id="offs">{p.offices.map(o => <option key={o} value={o} />)}</datalist></label>
          {p.editable ? <div className="row"><button className="btn">{t('Save')}</button><span className="muted">{t('Saved to Active Directory: Outlook, phones and the directory update within minutes.')}</span></div>
            : <p className="muted">{p.protected ? t('Your account is an admin or service account: the intranet does not change it. Ask IT.') : t('Profile editing is not available yet.')}</p>}
        </form></div></div>
    <PasskeySection />
    <div className="grid" style={{marginTop: 18}}>
      <a className="tile" style={{'--c': 'var(--sc-blue)'} as React.CSSProperties} href="https://sso.example.com/realms/company/account/account-security/signing-in" target="_blank" rel="noopener"><div className="i">🔐</div><b>{t('Sign-in and 2FA')}</b><span>{t('Authenticator app for SSO')}</span></a>
      <Link className="tile" style={{'--c': 'var(--sc-red)'} as React.CSSProperties} to="/help/change-password"><div className="i">🔑</div><b>{t('Change password')}</b><span>{t('How to change your password')}</span></Link>
      <Link className="tile" style={{'--c': 'var(--sc-green)'} as React.CSSProperties} to="/training"><div className="i">🎓</div><b>{t('My certificates')}</b><span>{t('Training and expiry dates')}</span></Link>
      <a className="tile push-tile" style={{'--c': 'var(--sc-navy)'} as React.CSSProperties} href="#" id="pt" onClick={async e => { e.preventDefault(); try { setPs(await pushToggle()); } catch (err) { fail(err); } }}>
        <div className="i">🔔</div><b>{t('Notifications')}</b><span id="pts">{pushLabel(ps)}</span></a>
    </div>
    {p.history.length > 0 && <><h2>{t('Recent changes')}</h2><table className="list"><tbody>{p.history.map((h, i) =>
      <tr key={i}><td>{FIELD()[h.field] || h.field}</td><td>{h.new_value || '—'}</td><td className="muted">{fmtDate(h.changed_at)}</td></tr>)}</tbody></table></>}
  </>;
}
