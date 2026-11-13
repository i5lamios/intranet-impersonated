// HR documents: a Company Cloud folder, sub-folders = sections.
import {useState} from 'react';
import {api, openFile} from '../lib/api';
import {fmtDate, norm, t} from '../lib/i18n';
import {session} from '../lib/session';
import {ErrorPanel, useLoad} from '../components/ui';

type Item = {name: string; path: string; dir?: boolean; size: number; modified: string; children?: Item[]};
const fsize = (n: number) => n > 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB';
const ext = (n: string) => n.split('.').pop()!.toLowerCase();
const ficon = (n: string) => ({pdf: '📕', doc: '📘', docx: '📘', xls: '📗', xlsx: '📗', ppt: '📙', pptx: '📙', jpg: '🖼️', png: '🖼️', zip: '🗜️', txt: '📄'} as Record<string, string>)[ext(n)] || '📄';
const count = (items: Item[]): number => items.reduce((n, i) => n + (i.dir ? count(i.children || []) : 1), 0);

export function Docs() {
  const {data: d, error} = useLoad(() => api<{items: Item[]; folder: string}>('/api/docs'));
  const [q, setQ] = useState('');
  if (error) return <ErrorPanel error={error} />;
  if (!d) return null;
  const w = norm(q), shown = (f: Item) => !w || norm(f.name.replace(/\.[^.]+$/, '') + ext(f.name).toUpperCase()).includes(w);
  const hasHit = (it: Item): boolean => (it.children || []).some(c => c.dir ? hasHit(c) : shown(c));
  const Files = ({items}: {items: Item[]}) => <>{items.filter(i => !i.dir).map(f =>
    <a key={f.path} className="doc" href="#" hidden={!shown(f)} onClick={e => { e.preventDefault(); openFile('/api/docs/file?path=' + encodeURIComponent(f.path), f.path.split('/').pop()); }}>
      <span className="fi">{ficon(f.name)}</span>
      <span><b>{f.name.replace(/\.[^.]+$/, '')}</b><small>{ext(f.name).toUpperCase()} · {fsize(f.size)} · {fmtDate(f.modified)}</small></span></a>)}</>;
  const Section = ({it, lvl}: {it: Item; lvl: number}) =>
    <details className="docsec" open={w ? hasHit(it) : lvl === 0}><summary><b>📁 {it.name}</b><span className="cnt">{count(it.children || [])}</span></summary>
      <div className="docs"><Files items={it.children || []} /></div>{(it.children || []).filter(c => c.dir).map(c => <Section key={c.path} it={c} lvl={lvl + 1} />)}</details>;
  const top = d.items.filter(i => !i.dir), dirs = d.items.filter(i => i.dir);
  return <>
    <div className="row" style={{justifyContent: 'space-between'}}><h1>{t('HR documents')}</h1>
      {session.me?.editor && <a className="btn ghost" href={d.folder} target="_blank" rel="noopener">{t('Manage in Cloud')}</a>}</div>
    <p className="muted">{t('Policies, forms, templates')}</p>
    <div className="filters"><input id="dq" placeholder={t('Search documents')} value={q} onChange={e => setQ(e.target.value)} /></div>
    <div id="dl">{top.length > 0 && <div className="docs"><Files items={top} /></div>}
      {dirs.map(i => <Section key={i.path} it={i} lvl={0} />)}
      {!dirs.length && !top.length && <div className="panel empty">{t('No documents yet')}</div>}</div>
  </>;
}
