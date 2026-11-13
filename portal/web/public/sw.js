// Company Intranet service worker: push notifications (no offline caching — content is always live).
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('push', e => {
  let d = {};
  try { d = e.data.json(); } catch { d = {title: 'Company', body: e.data ? e.data.text() : ''}; }
  e.waitUntil(self.registration.showNotification(d.title || 'Company', {
    // renotify: a second message with the same tag (the banner) pops up again instead of silently replacing the first
    body: d.body || '', tag: d.tag || d.url || 'intranet', renotify: true, data: {url: d.url || '/'},
    icon: '/app-192.png', badge: '/badge-96.png'}));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL(e.notification.data.url || '/', self.location.origin).href;
  e.waitUntil(clients.matchAll({type: 'window', includeUncontrolled: true}).then(list => {
    for (const c of list) if (c.url.startsWith(self.location.origin)) { c.navigate(url); return c.focus(); }
    return clients.openWindow(url);
  }));
});
