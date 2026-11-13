// Page frame: header (brand, menu, language, notifications, user), emergency banner, page, footer.
import {useEffect, useState} from 'react';
import {Link, NavLink, Outlet, useBlocker, useLocation} from 'react-router';
import {api} from '../lib/api';
import {LANGS, lang, setLang, t} from '../lib/i18n';
import {kc} from '../lib/kc';
import {pushState, pushToggle, type PushState} from '../lib/push';
import {guard, session} from '../lib/session';
import {toast} from '../lib/toast';
import {setTheme, theme as currentTheme} from '../lib/theme';
import {PasskeyOffer} from './Passkeys';

// usage analytics: route pattern only (IDs removed), no names
function track(path: string) {
  if (!kc.authenticated) return;
  const page = path.replace(/\/\d+$/, '/:id').replace(/^\/directory\/[^/]+$/, '/directory/:id')
    .replace(/^\/help\/[^/]+$/, '/help/:slug').replace(/^\/admin\/help\/.+$/, '/admin/help/edit').replace(/\/$/, '') || '/';
  api('/api/track', {method: 'POST', json: {page, lang}}).catch(() => {});
}

export function Layout({onLang}: {onLang: (l: string) => void}) {
  const loc = useLocation();
  const on = !!kc.authenticated, me = session.me;
  const [open, setOpen] = useState(false);
  const [bell, setBell] = useState<PushState | null>(null);
  const [theme, setT] = useState(currentTheme());
  useEffect(() => { const f = () => setT(currentTheme()); addEventListener('themechange', f); return () => removeEventListener('themechange', f); }, []);

  // leaving a page with unsaved changes asks first
  const blocker = useBlocker(({currentLocation, nextLocation}) => guard.dirty && currentLocation.pathname !== nextLocation.pathname);
  useEffect(() => {
    if (blocker.state !== 'blocked') return;
    if (confirm(t('Discard unsaved changes?'))) { guard.dirty = false; blocker.proceed(); } else blocker.reset();
  }, [blocker]);
  useEffect(() => { const f = (e: BeforeUnloadEvent) => { if (guard.dirty) e.preventDefault(); };
    addEventListener('beforeunload', f); return () => removeEventListener('beforeunload', f); }, []);

  useEffect(() => { track(loc.pathname); scrollTo(0, 0); setOpen(false); }, [loc.pathname]);
  useEffect(() => { if (on) pushState().then(setBell); }, [on]);

  const nav: [string, string, boolean][] = [
    ['/', 'Home', true], ['/news', 'News', true], ['/directory', 'Directory', true], ['/hse', 'HSE', on], ['/training', 'Training', on],
    ['/docs', 'Documents', !!me?.features.docs], ['/rooms', 'Rooms', !!me?.features.rooms], ['/help', 'Help', true],
    ['/admin', 'Admin', !!(me && (me.editor || me.roles.it || me.roles.hse))],
  ];
  const tp = (kc.tokenParsed || {}) as {name?: string; preferred_username?: string};
  const toggleBell = async () => {
    try {
      const st = await pushToggle(); setBell(st);
      if (st === 'denied') toast(t('Notifications are blocked in the browser settings'));
      if (st === 'ios') toast(t('On iPhone: add the intranet to the home screen first'));
      if (st === 'unsupported') toast(t('Not supported in this browser'));
    } catch (e) { toast(t('Error') + ': ' + (e as Error).message); }
  };
  const changeLang = (l: string) => {
    if (guard.dirty && !confirm(t('Discard unsaved changes?'))) return;
    guard.dirty = false; setLang(l); onLang(l);
  };

  return <>
    <Banner />
    <header className={open ? 'open' : ''}><div className="wrap bar">
      <Link to="/" className="brand"><img src={theme === 'dark' ? '/logo-white.png' : '/logo.png'} alt="Company" /><span className="t">Intranet<small>{t('Internal portal')}</small></span></Link>
      <nav id="nav" onClick={e => { if ((e.target as HTMLElement).closest('a')) setOpen(false); }}>
        {nav.filter(n => n[2]).map(([h, l]) => <NavLink key={h} to={h} end={h === '/'} className={({isActive}) => isActive ? 'on' : ''}>{t(l)}</NavLink>)}
      </nav>
      <div className="auth">
        <select id="lang" aria-label="Language" value={lang} onChange={e => changeLang(e.target.value)}>
          {Object.entries(LANGS).map(([k, v]) => <option key={k} value={k} title={v}>{k.toUpperCase()}</option>)}</select>
        <button className="btn ghost bell" id="theme" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title={theme === 'dark' ? t('Light theme') : t('Dark theme')} aria-label={theme === 'dark' ? t('Light theme') : t('Dark theme')}>{theme === 'dark' ? '☀️' : '🌙'}</button>
        {on && <button className="btn ghost bell" id="bell" onClick={toggleBell} title={bell === 'on' ? t('Notifications are on') : t('Turn on notifications')}>{bell === 'on' ? '🔔' : '🔕'}</button>}
        {!on && <button className="btn" id="login" onClick={() => kc.login({redirectUri: location.href, locale: lang})}>{t('Log in')}</button>}
        {on && <span className="who" id="who"><b>{tp.name || tp.preferred_username}</b></span>}
        {on && <button className="btn ghost" id="logout" onClick={() => kc.logout({redirectUri: location.origin + '/'})}>{t('Log out')}</button>}
        <button className="btn ghost menu" id="menu" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? '✕' : '☰'}</button>
      </div>
    </div></header>
    <main className="wrap" id="view"><Outlet /></main>
    <footer>{t('Company · internal use only')}</footer>
    {on && <PasskeyOffer />}
  </>;
}

type B = {active: boolean; text?: string; level?: string; id?: string};
// 1) a new message pops up in the middle of the screen once (per browser); 2) then a slim bar stays on top
function Banner() {
  const [b, setB] = useState<B | null>(null);
  const [, redraw] = useState(0);
  useEffect(() => {
    if (!kc.authenticated) return;
    const load = () => api<B>('/api/banner').then(setB).catch(() => {});
    load(); const id = setInterval(load, 5 * 60 * 1000); addEventListener('banner', load);
    return () => { clearInterval(id); removeEventListener('banner', load); };
  }, []);
  if (!b?.active) return null;
  const icon = b.level === 'danger' ? '⚠️' : b.level === 'warning' ? '❗' : 'ℹ️';
  const seen = localStorage.getItem('banner-seen') === b.id, closed = sessionStorage.getItem('banner-closed') === b.id;
  return <>
    {!seen && <div className="bpop" role="alertdialog"><div className={`bpop-box ${b.level}`}><div className="bpop-i">{icon}</div><div className="bpop-t">{b.text}</div>
      <button className="btn" autoFocus onClick={() => { localStorage.setItem('banner-seen', b.id!); redraw(x => x + 1); }}>{t('OK, understood')}</button></div></div>}
    {!closed && <div id="banner" className={`banner ${b.level}`} role="alert"><div className="wrap"><span>{icon}</span><span className="bt">{b.text}</span>
      {b.level !== 'danger' && <button className="x" aria-label={t('Close')} onClick={() => { sessionStorage.setItem('banner-closed', b.id!); redraw(x => x + 1); }}>×</button>}</div></div>}
  </>;
}
