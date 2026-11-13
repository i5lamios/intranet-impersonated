// Passkeys (Face ID / fingerprint / phone PIN) for SSO sign-in. Kept in Keycloak; the intranet lists, renames and deletes
// them with the user's own token (Keycloak account API, role manage-account). Creating one must happen on
// sso.example.com (passkeys belong to that site): a one-step Keycloak action that comes straight back here.
import {t} from './i18n';
import {kc} from './kc';
import {toast} from './toast';

const ACC = 'https://sso.example.com/realms/company/account';
const TYPE = 'webauthn-passwordless';
export type Passkey = {id: string; userLabel?: string; createdDate: number};

async function acc<T = unknown>(path: string, opts: RequestInit = {}): Promise<T> {
  await kc.updateToken(30);
  const r = await fetch(ACC + path, {...opts, headers: {Authorization: 'Bearer ' + kc.token, Accept: 'application/json', 'Content-Type': 'application/json'}});
  if (!r.ok) throw Object.assign(new Error(r.status + ''), {status: r.status});
  return (r.status === 204 ? null : await r.json().catch(() => null)) as T;
}

export async function listPasskeys(): Promise<Passkey[]> {
  const all = await acc<{type: string; userCredentialMetadatas: {credential: Passkey}[]}[]>('/credentials');
  const c = all.find(x => x.type === TYPE);
  return c ? c.userCredentialMetadatas.map(m => m.credential) : [];
}
export const addPasskey = () => kc.login({action: 'webauthn-register-passwordless', redirectUri: location.href});
export const renamePasskey = (id: string, label: string) => acc(`/credentials/${encodeURIComponent(id)}/label`, {method: 'PUT', body: JSON.stringify(label)});
export async function deletePasskey(id: string) {
  try { await acc(`/credentials/${encodeURIComponent(id)}`, {method: 'DELETE'}); }
  catch (e) { if ((e as {status?: number}).status === 403) return kc.login({action: 'delete_credential:' + id, redirectUri: location.href}); throw e; }
}

// can this device hold a passkey with Face ID / fingerprint / PIN?
export async function deviceCan() {
  try { return !!window.PublicKeyCredential && await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable(); } catch { return false; }
}
const mobile = () => !!(navigator as any).userAgentData?.mobile || /Android|iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

// after sign-in on a phone without a passkey: offer one (again after 3 days when "Not now")
export async function shouldOffer() {
  if (!kc.authenticated || !mobile() || location.pathname.startsWith('/rooms/door')) return false;
  if (Date.now() - (+(localStorage.getItem('pk-later') || 0)) < 3 * 864e5) return false;
  if (!await deviceCan()) return false;
  try { return !(await listPasskeys()).length; } catch { return false; }
}
export const later = () => localStorage.setItem('pk-later', String(Date.now()));

// the result of a Keycloak action, after it sends the user back
export function actionDone(status: string, action: string) {
  if (!/webauthn|delete_credential/.test(action || '')) return;
  const add = action.startsWith('webauthn');
  if (status === 'success') toast(add ? t('Passkey added') : t('Passkey removed'));
  else if (status === 'error') toast(t('Could not finish. Try again or ask IT.'));
}
