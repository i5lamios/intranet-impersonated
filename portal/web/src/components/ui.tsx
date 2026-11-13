// Small shared pieces: help "?" link, tabs, modal, sign-in / role notices, loading hook, people photos.
import {useCallback, useEffect, useRef, useState, type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import {Link} from 'react-router';
import {api} from '../lib/api';
import {t} from '../lib/i18n';
import {kc} from '../lib/kc';

// Round "?" next to a section title → its Help Center article
export const HelpQ = ({slug}: {slug: string}) =>
  <Link className="hq" to={`/help/${slug}`} title={t('How it works')} aria-label={t('How it works')}>?</Link>;

export const Tabs = ({items, cur}: {items: [string, string][]; cur: string}) =>
  <div className="tabs">{items.map(([h, label]) => <Link key={h} to={h} className={h === cur ? 'on' : ''}>{label}</Link>)}</div>;

export function Modal({onClose, children}: {onClose: () => void; children: ReactNode}) {
  return createPortal(<div className="modal" onClick={e => { const el = e.target as HTMLElement;
    if (el === e.currentTarget || el.closest('[data-close]')) onClose(); }}>
    <div className="modal-box">{children}</div></div>, document.body);
}

export const NeedLogin = () => <div className="panel empty" style={{marginTop: 28}}><p>{t('Please log in to continue.')}</p>
  <button className="btn" onClick={() => kc.login({redirectUri: location.href})}>{t('Log in')}</button></div>;
export const NeedRole = ({group}: {group: string}) =>
  <div className="panel empty" style={{marginTop: 28}}>{t('AD group {g} required', {g: group})}</div>;
export const ErrorPanel = ({error}: {error: unknown}) =>
  <div className="panel empty" style={{marginTop: 28}}>{t('Error')}: {error instanceof Error ? error.message : String(error)}</div>;

// load data for a page: {data, error, reload}; data stays undefined until the first answer (the page shows nothing meanwhile)
export function useLoad<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<{data?: T; error?: unknown}>({});
  const [n, setN] = useState(0);
  useEffect(() => {
    let live = true;
    fn().then(data => live && setState({data}), error => live && setState({error}));
    return () => { live = false; };
  }, [...deps, n]);   // eslint-disable-line react-hooks/exhaustive-deps
  const reload = useCallback(() => setN(x => x + 1), []);
  return {...state, reload};
}

// ---------- people photos (AD), loaded when they scroll into view; the directory has ~500 people ----------
const photoCache = new Map<string, Promise<string | null>>();
export function photo(id: string) {
  if (!photoCache.has(id)) photoCache.set(id, api<Blob>(`/api/directory/${id}/photo`).then(b => URL.createObjectURL(b)).catch(() => null));
  return photoCache.get(id)!;
}
export const initials = (n?: string | null) => (n || '?').split(/\s+/).map(w => w[0]).slice(0, 2).join('').toUpperCase();
type Who = {id?: string; name?: string | null; has_photo?: boolean};
export function Avatar({p, className = 'av', style}: {p: Who; className?: string; style?: React.CSSProperties}) {
  const ref = useRef<HTMLSpanElement>(null);
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    if (!p.has_photo || !p.id || !ref.current) return;
    let live = true;
    const load = () => photo(p.id!).then(u => { if (live && u) setSrc(u); });
    if (!('IntersectionObserver' in window)) { load(); return () => { live = false; }; }
    const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); load(); } }, {rootMargin: '300px'});
    io.observe(ref.current);
    return () => { live = false; io.disconnect(); };
  }, [p.id, p.has_photo]);
  return src ? <img className={className} src={src} alt="" /> : <span ref={ref} className={className} style={style}>{initials(p.name)}</span>;
}

// photos for [data-ph] avatars inside server HTML (news text): swapped in place when they scroll into view
export function fillPhotos(root: HTMLElement | null) {
  if (!root) return;
  const swap = async (el: HTMLElement) => {
    const u = await photo(el.dataset.ph!);
    if (u && el.isConnected) { const img = document.createElement('img'); img.className = el.className; img.src = u; img.alt = ''; el.replaceWith(img); }
  };
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { io!.unobserve(e.target); swap(e.target as HTMLElement); } }), {rootMargin: '300px'}) : null;
  root.querySelectorAll<HTMLElement>('[data-ph]').forEach(el => { if (el.dataset.ph) io ? io.observe(el) : swap(el); });
}
