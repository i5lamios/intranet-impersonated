// Calls to the portal API with the Keycloak token; errors carry the server's message and the HTTP status.
import {kc} from './kc';
import {t} from './i18n';
import {toast} from './toast';

export class ApiError extends Error { constructor(msg: string, public status: number) { super(msg); } }

type Opts = Omit<RequestInit, 'body'> & {json?: unknown; body?: BodyInit};

export async function api<T = any>(path: string, opts: Opts = {}): Promise<T> {
  const {json, ...init} = opts;
  const headers: Record<string, string> = {...(init.headers as Record<string, string> || {})};
  if (kc.authenticated) {
    try { await kc.updateToken(30); } catch { kc.login({redirectUri: location.href}); }
    headers.Authorization = 'Bearer ' + kc.token;
  }
  if (json !== undefined) { headers['Content-Type'] = 'application/json'; init.body = JSON.stringify(json); }
  const r = await fetch(path, {...init, headers});
  if (!r.ok) {
    let msg = r.status + '';
    try { const j = await r.json(); msg = typeof j.detail === 'string' ? j.detail : (j.detail || []).map((d: any) => d.msg || d).join('; '); } catch { /* not JSON */ }
    throw new ApiError(msg, r.status);
  }
  if (r.status === 204) return null as T;
  return ((r.headers.get('content-type') || '').includes('json') ? r.json() : r.blob()) as Promise<T>;
}

export function upload<T = any>(path: string, file: Blob & {name?: string}) {
  const fd = new FormData(); fd.append('file', file, file.name || 'image.png');
  return api<T>(path, {method: 'POST', body: fd});
}

export const fail = (err: unknown) => toast(t('Error') + ': ' + (err instanceof Error ? err.message : String(err)));

// authenticated download → new tab (PDF / images / text) or save
export async function openFile(path: string, name?: string) {
  const w = window.open('', '_blank');
  try {
    const b = await api<Blob>(path), u = URL.createObjectURL(b);
    if (/^(application\/pdf|image\/|text\/plain)/.test(b.type) && w) w.location.href = u;
    else { w?.close(); const a = document.createElement('a'); a.href = u; a.download = name || 'file'; a.click(); }
    setTimeout(() => URL.revokeObjectURL(u), 60000);
  } catch (err) { w?.close(); fail(err); }
}
