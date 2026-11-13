// Passkey offer after sign-in on a phone, and the My profile section (list / rename / delete / add).
import {useEffect, useState} from 'react';
import {fmtDate, t} from '../lib/i18n';
import {addPasskey, deletePasskey, deviceCan, later, listPasskeys, renamePasskey, shouldOffer, type Passkey} from '../lib/passkeys';
import {toast} from '../lib/toast';
import {Modal} from './ui';

export function PasskeyOffer() {
  const [show, setShow] = useState(false);
  useEffect(() => { shouldOffer().then(setShow); }, []);
  if (!show) return null;
  return <Modal onClose={() => setShow(false)}><div className="pkoffer"><div className="pki">🔐</div><h2>{t('Sign in with Face ID or fingerprint')}</h2>
    <p>{t('Set up a passkey on this phone: next time you sign in with Face ID, fingerprint or the phone PIN instead of a password. Outside the office it also replaces the one-time code.')}</p>
    <div className="row"><button className="btn" id="pkgo" onClick={() => addPasskey()}>{t('Set up passkey')}</button>
      <button className="btn ghost" id="pkno" onClick={() => { later(); setShow(false); }}>{t('Not now')}</button></div></div></Modal>;
}

export function PasskeySection() {
  const [list, setList] = useState<Passkey[] | null>(null), [can, setCan] = useState(true), [n, setN] = useState(0);
  useEffect(() => { listPasskeys().then(setList, () => setList(null)); deviceCan().then(setCan); }, [n]);
  if (!list) return <section id="pks" className="pks"></section>;
  const oops = () => toast(t('Could not finish. Try again or ask IT.'));
  const rename = async (c: Passkey) => {
    const v = prompt(t('Name for this passkey, e.g. My iPhone'), c.userLabel || '');
    if (v === null || !v.trim()) return;
    try { await renamePasskey(c.id, v.trim().slice(0, 60)); toast(t('Saved')); setN(x => x + 1); } catch { oops(); }
  };
  const del = async (c: Passkey) => {
    if (!confirm(t('Delete this passkey? You will sign in with your password on that device.'))) return;
    try { await deletePasskey(c.id); toast(t('Passkey removed')); setN(x => x + 1); } catch { oops(); }
  };
  return <section id="pks" className="pks"><h2>{t('Passkeys')}</h2>
    <p className="muted">{t('Sign in with Face ID, fingerprint or the device PIN instead of a password. Outside the office a passkey also replaces the one-time code.')}</p>
    {list.length ? <table className="list pkl"><tbody>{list.map(c => <tr key={c.id}><td><b>{c.userLabel || t('Passkey')}</b><small className="muted">{t('Added')} {fmtDate(c.createdDate)}</small></td>
      <td className="row"><button className="btn small ghost" onClick={() => rename(c)}>{t('Rename')}</button><button className="btn small danger" onClick={() => del(c)}>{t('Delete')}</button></td></tr>)}</tbody></table>
      : <div className="panel empty">{t('No passkeys yet.')}</div>}
    <div className="row" style={{marginTop: 10}}><button className="btn" id="pkadd" onClick={() => addPasskey()}>+ {t('Add a passkey')}</button>
      {!can && <span className="muted">{t('This device cannot hold a passkey. Use your phone.')}</span>}</div></section>;
}
