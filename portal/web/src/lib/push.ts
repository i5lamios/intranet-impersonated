// Browser push: service worker registration and per-browser opt-in.
import {api} from './api';

export type PushState = 'on' | 'off' | 'denied' | 'ios' | 'unsupported';
const supported = () => 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
const isIOS = () => /iPhone|iPad|iPod/.test(navigator.userAgent);
const standalone = () => matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone;
const b64 = (s: string) => { const p = '='.repeat((4 - s.length % 4) % 4), r = atob((s + p).replace(/-/g, '+').replace(/_/g, '/'));
  return Uint8Array.from([...r].map(c => c.charCodeAt(0))); };
const send = (s: PushSubscription) => { const j = s.toJSON();
  return api('/api/push/subscribe', {method: 'POST', json: {endpoint: j.endpoint, p256dh: j.keys!.p256dh, auth: j.keys!.auth}}); };

export async function registerSW() {
  if ('serviceWorker' in navigator) { try { await navigator.serviceWorker.register('/sw.js'); } catch { /* no SW: no push */ } }
}

export async function pushState(): Promise<PushState> {
  if (!supported()) return isIOS() && !standalone() ? 'ios' : 'unsupported';
  if (Notification.permission === 'denied') return 'denied';
  const reg = await navigator.serviceWorker.ready;
  return (await reg.pushManager.getSubscription()) ? 'on' : 'off';
}

// on every visit: hand this browser's subscription to the server again. The server drops subscriptions the push service
// rejects once, and browsers renew them now and then; without this the bell stays on and nothing arrives.
export async function pushSync() {
  if (!supported() || Notification.permission !== 'granted') return;
  const sub = await (await navigator.serviceWorker.ready).pushManager.getSubscription();
  if (sub) await send(sub).catch(() => {});
}

export async function pushToggle(): Promise<PushState> {
  const st = await pushState();
  if (st !== 'on' && st !== 'off') return st;
  const reg = await navigator.serviceWorker.ready;
  const sub = await reg.pushManager.getSubscription();
  if (sub) {
    await api('/api/push/unsubscribe', {method: 'POST', json: {endpoint: sub.endpoint}}).catch(() => {});
    await sub.unsubscribe(); return 'off';
  }
  if (await Notification.requestPermission() !== 'granted') return 'denied';
  const {key} = await api<{key: string}>('/api/push/key');
  await send(await reg.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: b64(key)}));
  return 'on';
}
