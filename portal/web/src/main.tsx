// Company Intranet — entry: sign-in check, then the router. Pages live in src/pages.
import {StrictMode, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {createBrowserRouter, Navigate, RouterProvider, useLocation, type RouteObject} from 'react-router';
import './app.css';
import './lib/theme';                                  // before anything draws: no light flash in dark mode
import {Layout} from './components/Layout';
import {NeedLogin} from './components/ui';
import {api} from './lib/api';
import {lang, type Lang} from './lib/i18n';
import {kc} from './lib/kc';
import {actionDone} from './lib/passkeys';
import {pushSync, registerSW} from './lib/push';
import {session, type Me} from './lib/session';
import {Home} from './pages/Home';
import {NewsItem, NewsList} from './pages/News';
import {Directory, Person} from './pages/People';
import {Docs} from './pages/Docs';
import {Door, Rooms} from './pages/Rooms';
import {RoomsAdmin} from './pages/RoomsAdmin';
import {HseAdmin, HseBoard, HseReport, HseReports} from './pages/Hse';
import {CertAdmin, CertMatrix, CertTypes, MyCerts} from './pages/Training';
import {HelpAdmin, HelpArticle, HelpEdit, HelpHome} from './pages/Help';
import {AdminBanner, AdminBirthdays, AdminEdit, AdminEmail, AdminHome, AdminList, AdminPeople} from './pages/Admin';
import {Analytics} from './pages/Analytics';
import {Audit} from './pages/Audit';
import {Profile} from './pages/Profile';
import {ReportProblem} from './pages/ReportProblem';
import {t} from './lib/i18n';

// every page needs sign-in (all data does); when Keycloak did not answer the page shows a Log in button instead
const auth = (el: React.ReactNode) => kc.authenticated ? el : <NeedLogin />;
// old addresses (bookmarks, e-mails) → their place under /admin
const Moved = ({to}: {to: (p: string) => string}) => { const l = useLocation(); return <Navigate replace to={to(l.pathname) + l.search} />; };
const NotFound = () => <div className="panel empty" style={{marginTop: 28}}>{t('Page not found')}</div>;

const pages: [string, React.ReactNode][] = [
  ['/', <Home />], ['/news', <NewsList />], ['/news/:id', <NewsItem />],
  ['/directory', <Directory />], ['/directory/:id', <Person />],
  ['/docs', <Docs />], ['/rooms', <Rooms />], ['/rooms/door/:key', <Door />],
  ['/hse', <HseBoard />], ['/hse/report', <HseReport />], ['/training', <MyCerts />],
  ['/help', <HelpHome />], ['/help/:slug', <HelpArticle />], ['/me', <Profile />], ['/report-problem', <ReportProblem />],
  // everything editors manage lives under /admin (sections by AD group)
  ['/admin', <AdminHome />], ['/admin/news', <AdminList />], ['/admin/news/:id', <AdminEdit />],
  ['/admin/people', <AdminPeople />], ['/admin/birthdays', <AdminBirthdays />], ['/admin/banner', <AdminBanner />], ['/admin/email', <AdminEmail />],
  ['/admin/hse', <HseAdmin />], ['/admin/hse/reports', <HseReports />],
  ['/admin/training', <CertAdmin />], ['/admin/training/matrix', <CertMatrix />], ['/admin/training/types', <CertTypes />],
  ['/admin/help', <HelpAdmin />], ['/admin/help/:slug', <HelpEdit />],
  ['/admin/analytics', <Analytics />], ['/admin/rooms', <RoomsAdmin />], ['/admin/audit', <Audit />],
];
const moved: [string, (p: string) => string][] = [
  ['/org', () => '/directory'], ['/admin/new', () => '/admin/news/new'], ['/hse/admin', () => '/admin/hse'], ['/hse/reports', () => '/admin/hse/reports'],
  ['/training/admin', () => '/admin/training'], ['/training/matrix', () => '/admin/training/matrix'], ['/training/types', () => '/admin/training/types'],
  ['/help/edit/:slug', p => p.replace('/help/edit/', '/admin/help/')],
];

function App() {
  const [l, setL] = useState(lang);
  const routes: RouteObject[] = [{
    element: <Layout onLang={l => setL(l as Lang)} />,
    children: [
      ...pages.map(([path, el]) => ({path, element: auth(el)})),
      {path: '/admin/:id', element: <Moved to={p => p.replace('/admin/', '/admin/news/')} />},
      ...moved.map(([path, to]) => ({path, element: <Moved to={to} />})),
      {path: '*', element: <NotFound />},
    ],
  }];
  const [router] = useState(() => createBrowserRouter(routes));
  return <RouterProvider key={l} router={router} />;
}

// ---------- start ----------
let ssoOk = false;
kc.onActionUpdate = actionDone;                       // back from a Keycloak action (passkey added / removed)
try {
  await Promise.race([kc.init({onLoad: 'check-sso', pkceMethod: 'S256', checkLoginIframe: false,
      silentCheckSsoRedirectUri: location.origin + '/silent-check-sso.html', messageReceiveTimeout: 6000}),
    new Promise((_, no) => setTimeout(() => no(new Error('SSO timeout')), 8000))]);
  ssoOk = true;
} catch (e) { console.warn('SSO check failed:', e instanceof Error ? e.message : e); }
// retried: one failed call right after sign-in used to leave the page without Rooms, Documents and Admin in the menu
if (kc.authenticated) for (let i = 0; i < 3 && !session.me; i++) {
  try { session.me = await api<Me>('/api/me'); } catch { await new Promise(r => setTimeout(r, 500)); }
}
// not signed in → straight to the sign-in page (office PCs come back signed in via Kerberos). Once a minute at most, and
// not when Keycloak did not answer: then every page shows a Log in button.
const loginFirst = !kc.authenticated && ssoOk && Date.now() - (+(sessionStorage.getItem('auto-login') || 0)) > 60000;
if (loginFirst) { sessionStorage.setItem('auto-login', String(Date.now())); kc.login({redirectUri: location.href, locale: lang}); }
else {
  createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
  registerSW().then(() => { if (kc.authenticated) pushSync(); });
}
