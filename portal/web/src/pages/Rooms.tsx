// Meeting rooms: day timeline (Exchange free/busy) + booking from the intranet; week view; the QR door page.
import {Fragment, useEffect, useRef, useState} from 'react';
import {Link, useNavigate, useParams, useSearchParams} from 'react-router';
import {api, fail} from '../lib/api';
import {dayName, fmtDate, fmtTime, norm, t, ymd} from '../lib/i18n';
import {session} from '../lib/session';
import {toast} from '../lib/toast';
import {Avatar, ErrorPanel, HelpQ, Modal, useLoad} from '../components/ui';
import {chatUrl, dial, type Person} from './People';

const H0 = 8, H1 = 20, STEP = 15;
const toMin = (hm: string) => { const [h, m] = hm.split(':').map(Number); return h * 60 + m; };
const toHm = (n: number) => `${String(Math.floor(n / 60) % 24).padStart(2, '0')}:${String(n % 60).padStart(2, '0')}`;
const pct = (hm: string) => { const [h, m] = hm.split(':').map(Number); return Math.min(100, Math.max(0, ((h + m / 60) - H0) / (H1 - H0) * 100)); };
const nowMin = (d: Date) => d.getHours() * 60 + d.getMinutes();
const hm0 = (iso: string) => iso.slice(11, 16);
const sameMail = (a?: string, b?: string) => !!a && !!b && a.toLowerCase() === b.toLowerCase();

type Org = Person & {name: string};
type Ev = {start: string; end: string; subject?: string; status?: string; organizer?: Org | null};
type Room = {name: string; mail: string; events: Ev[]; error?: string};
type Day = {enabled: boolean; rooms: Room[]};
type Mine = {id: number; room: string; room_name: string; subject: string; starts: string; ends: string; series?: string | null;
  checked_in?: boolean; checkin_open?: boolean; editable?: boolean};
type Bk = {id: number; day: string; start: string; end: string; room: string; subject: string; attendees: string[]};
type BookArgs = {day: string; start: string; room?: string; bk?: Bk; endAt?: string};

// what a room is doing at this moment; back-to-back meetings count as one busy stretch
function roomNow(x: Room, now: Date) {
  const m = nowMin(now);
  const evs = x.events.map(e => ({a: toMin(hm0(e.start)), b: toMin(hm0(e.end)), e})).filter(v => v.b > m).sort((p, q) => p.a - q.a);
  const cur = evs.find(v => v.a <= m);
  if (!cur) return {busy: false as const, until: evs[0] ? evs[0].a : null};
  let end = cur.b;
  evs.forEach(v => { if (v.a <= end) end = Math.max(end, v.b); });
  return {busy: true as const, end, left: end - m, ev: cur.e};
}

async function myBookings() {
  let failed = false;
  const list = await api<Mine[]>('/api/rooms/mine').catch(() => { failed = true; return [] as Mine[]; });
  return {list, failed};
}

export function Rooms() {
  const [qs] = useSearchParams(), day = qs.get('day') || ymd(new Date()), week = qs.get('view') === 'week';
  return week ? <WeekView key={day} day={day} /> : <DayView key={day} day={day} />;
}

// dialogs shared by the day and week views
function useRoomDialogs(rooms: Room[], reload: () => void) {
  const nav = useNavigate();
  const [book, setBook] = useState<BookArgs | null>(null), [cancelSeries, setCancelSeries] = useState<number | null>(null);
  const [event, setEvent] = useState<{e: Ev; room?: Room; mine?: Mine} | null>(null);
  const editBk = async (id: number) => {
    try { const bk = await api<Bk>('/api/rooms/book/' + id); setBook({day: bk.day, start: bk.start, room: bk.room, bk}); } catch (err) { fail(err); }
  };
  const del = async (id: number, all: boolean) => {
    try { await api(`/api/rooms/book/${id}${all ? '?series=1' : ''}`, {method: 'DELETE'}); toast(t('Booking cancelled')); reload(); } catch (err) { fail(err); }
  };
  const cancelBk = (id: number, series: boolean) => { if (series) setCancelSeries(id); else if (confirm(t('Cancel this booking?'))) del(id, false); };
  const checkin = async (id: number) => {
    try { await api(`/api/rooms/book/${id}/checkin`, {method: 'POST'}); toast(t('Checked in')); reload(); } catch (err) { fail(err); }
  };
  const dialogs = <>
    {book && <BookDialog rooms={rooms} {...book} onClose={() => setBook(null)} onDone={d => { setBook(null); nav('/rooms?day=' + d); reload(); }} />}
    {event && <EventDialog {...event} onClose={() => setEvent(null)} onEdit={id => { setEvent(null); editBk(id); }} onCancel={id => { setEvent(null); cancelBk(id, !!event.mine?.series); }} />}
    {cancelSeries !== null && <Modal onClose={() => setCancelSeries(null)}><h2 style={{marginTop: 0}}>{t('Cancel this booking?')}</h2><p className="muted">{t('This booking repeats.')}</p>
      <div className="row"><button className="btn danger" onClick={() => { setCancelSeries(null); del(cancelSeries, false); }}>{t('Only this date')}</button>
        <button className="btn danger" onClick={() => { setCancelSeries(null); del(cancelSeries, true); }}>{t('This and later dates')}</button>
        <button className="btn ghost" data-close>{t('Close')}</button></div></Modal>}
  </>;
  return {dialogs, setBook, setEvent, editBk, cancelBk, checkin, open: !!(book || event || cancelSeries !== null)};
}

function Toolbar({day, week, d0, label, onBook}: {day: string; week: boolean; d0: Date; label: string; onBook: () => void}) {
  const nav = useNavigate();
  const shift = (n: number) => { const x = new Date(d0); x.setDate(x.getDate() + n); return ymd(x); }, n = week ? 7 : 1, q = week ? '&view=week' : '';
  return <>
    <div className="row" style={{justifyContent: 'space-between'}}><h1>{t('Meeting rooms')} <HelpQ slug="book-meeting-room" /></h1>
      <button className="btn" id="bk" onClick={onBook}>+ {t('Book a room')}</button></div>
    <div className="row rbar"><div className="row">
      <Link className="btn ghost small" to={`/rooms?day=${shift(-n)}${q}`}>‹</Link>
      <b className="rdate">{label}</b>
      <Link className="btn ghost small" to={`/rooms?day=${shift(n)}${q}`}>›</Link>
      <Link className="btn ghost small" to={`/rooms${week ? '?view=week' : ''}`}>{t('Today')}</Link>
      <input type="date" id="dpick" value={day} className="small-input" onChange={e => nav(`/rooms?day=${e.target.value}${q}`)} /></div>
      <div className="seg"><Link to={`/rooms?day=${day}`} className={week ? '' : 'on'}>{t('Day')}</Link><Link to={`/rooms?day=${day}&view=week`} className={week ? 'on' : ''}>{t('Week')}</Link></div></div>
  </>;
}

function BookingCards({list, failed, onCheckin, onEdit, onCancel}: {list: Mine[]; failed: boolean; onCheckin: (id: number) => void; onEdit: (id: number) => void; onCancel: (id: number, series: boolean) => void}) {
  const now = new Date(), tom = new Date(now); tom.setDate(tom.getDate() + 1);
  const label = (b: Mine) => { const k = b.starts.slice(0, 10); return k === ymd(now) ? t('Today') : k === ymd(tom) ? t('Tomorrow') : `${fmtDate(b.starts)}, ${dayName(new Date(b.starts))}`; };
  let last = '';
  return <aside className="rside"><h2>{t('My bookings')}</h2>
    {list.length ? list.map(b => { const g = label(b), head = g === last ? null : <h3>{g}</h3>; last = g;
      return <Fragment key={b.id}>{head}<div className="bkc"><span className="bkt">{fmtTime(b.starts)}–{fmtTime(b.ends)}</span><b>{b.subject}</b>
        <small>{b.room_name}{b.series ? ' · ↻ ' + t('Repeats') : ''}{b.checked_in ? ' · ✓ ' + t('Checked in') : ''}</small>
        <div className="row">{b.checkin_open && <button className="btn small" onClick={() => onCheckin(b.id)}>{t('Check in')}</button>}
          {b.editable && <button className="btn small ghost" onClick={() => onEdit(b.id)}>{t('Edit')}</button>}
          <button className="btn small danger" onClick={() => onCancel(b.id, !!b.series)}>{t('Cancel')}</button></div></div></Fragment>; })
      : <div className="panel empty">{t(failed ? 'Could not load your bookings. Refresh the page.' : 'No upcoming bookings')}</div>}
    <p className="muted">{t('Only meetings booked here can be changed here. Change Outlook meetings in Outlook.')}</p></aside>;
}

function DayView({day}: {day: string}) {
  const {data, error, reload} = useLoad(() => Promise.all([api<Day>('/api/rooms?day=' + day), myBookings()]), [day]);
  const r = data?.[0], mineR = data?.[1], mine = mineR?.list || [];
  const D = useRoomDialogs(r?.rooms || [], reload);
  const [qk, setQk] = useState<{x: number; top: number; room: string; start: number; limit: number} | null>(null);
  const dragging = useRef(false), stateRef = useRef({open: false, qk: false});
  stateRef.current = {open: D.open, qk: !!qk};
  const today = day === ymd(new Date());
  // live view: every 3 s while the page is visible and no dialog is open; redraw when something changed and each minute today
  useEffect(() => {
    if (!data) return;
    const stamp = () => today ? new Date().getMinutes() : 0, sig = JSON.stringify([data[0], data[1].list, stamp()]);
    const id = setInterval(async () => {
      if (document.hidden || stateRef.current.open || stateRef.current.qk || dragging.current) return;
      try {
        const [r2, m2] = await Promise.all([api<Day>('/api/rooms?day=' + day), api<Mine[]>('/api/rooms/mine').catch(() => data[1].list)]);
        if (JSON.stringify([r2, m2, stamp()]) !== sig) reload();
      } catch { /* try again in 3 s */ }
    }, 3000);
    return () => clearInterval(id);
  }, [data, day, today, reload]);
  if (error) return <ErrorPanel error={error} />;
  if (!r || !mineR) return null;
  const d0 = new Date(day + 'T00:00'), now = new Date();
  const hm = now.getHours() + now.getMinutes() / 60;
  const nowPct = today && hm > H0 && hm < H1 ? (hm - H0) / (H1 - H0) * 100 : null;
  const myEv = (e: Ev, mail: string) => mine.some(m => m.room === mail && m.starts.slice(0, 16) === e.start && m.ends.slice(0, 16) === e.end) || sameMail(e.organizer?.mail, session.me?.email);
  const bookNow = (x: Room) => { const s = Math.ceil(nowMin(new Date()) / STEP) * STEP, st = roomNow(x, new Date());
    D.setBook({day, start: toHm(s), room: x.mail, endAt: toHm(Math.min(s + 60, st.busy || st.until === null ? 24 * 60 - STEP : st.until))}); };
  return <>
    <Toolbar day={day} week={false} d0={d0} label={`${fmtDate(d0)}, ${dayName(d0)}`} onBook={() => D.setBook({day, start: '09:00'})} />
    <div className="rlay"><div className="rmain">
      {today && r.enabled && <div className="rnow">{r.rooms.map(x => { const s = roomNow(x, now), o = s.busy ? s.ev.organizer : null;
        return <div key={x.mail} className={`rcard ${s.busy ? 'busy' : 'free'}`}><div className="rtop"><b>{x.name}</b><span className="pill">{t(s.busy ? 'Busy' : 'Free')}</span></div>
          <p>{s.busy ? t('{n} min left', {n: s.left}) + ` · ${t('Free at {t}', {t: toHm(s.end)})}` : s.until === null ? t('Free all day') : t('Free until {t}', {t: toHm(s.until)})}</p>
          {s.busy && <small>{s.ev.subject || t('Busy')}{o ? ' · ' + o.name : ''}</small>}
          {!s.busy && <button className="btn small" onClick={() => bookNow(x)}>{t('Book now')}</button>}</div>; })}</div>}
      {r.enabled ? <><div className="rooms"><div className="hours">{Array.from({length: H1 - H0 + 1}, (_, i) => <span key={i} style={{left: `${i / (H1 - H0) * 100}%`}}>{H0 + i}:00</span>)}</div>
        {r.rooms.map(x => <div className="room" key={x.mail}><div className="rn"><b>{x.name}</b></div>
          <Lane room={x} day={day} nowPct={nowPct} now={now} myEv={myEv} dragging={dragging}
            onEvent={e => D.setEvent({e, room: x, mine: mine.find(m => m.room === x.mail && m.starts.slice(0, 16) === e.start && m.ends.slice(0, 16) === e.end)})}
            onRange={(a, b) => D.setBook({day, start: toHm(a), room: x.mail, endAt: toHm(b)})}
            onSlot={(clientX, top, start, limit) => setQk({x: clientX, top, room: x.mail, start, limit})} /></div>)}</div>
        <p className="muted rhint">{t('Click a free slot for quick times, or drag to choose. Outlook bookings show here too.')}</p></>
        : <div className="panel empty">{t('Rooms are not connected yet')}</div>}</div>
      <BookingCards {...mineR} onCheckin={D.checkin} onEdit={D.editBk} onCancel={D.cancelBk} /></div>
    {qk && <QuickTimes {...qk} onClose={() => setQk(null)} onPick={end => { setQk(null); D.setBook({day, start: toHm(qk.start), room: qk.room, endAt: toHm(end)}); }} />}
    {D.dialogs}
  </>;
}

// one room's timeline: events, "now" line, click a free slot (quick times) or drag with the mouse to choose
function Lane({room, nowPct, now, myEv, dragging, onEvent, onRange, onSlot}: {room: Room; day: string; nowPct: number | null; now: Date;
    myEv: (e: Ev, mail: string) => boolean; dragging: React.RefObject<boolean>; onEvent: (e: Ev) => void; onRange: (a: number, b: number) => void;
    onSlot: (x: number, top: number, start: number, limit: number) => void}) {
  const ref = useRef<HTMLDivElement>(null), dragged = useRef(false);
  const [sel, setSel] = useState<[number, number] | null>(null);
  const spans = room.events.map(e => [toMin(hm0(e.start)), toMin(hm0(e.end))]);
  const at = (x: number) => { const b = ref.current!.getBoundingClientRect(), m = H0 * 60 + (x - b.left) / b.width * (H1 - H0) * 60;
    return Math.max(H0 * 60, Math.min(H1 * 60, Math.floor(m / STEP) * STEP)); };
  const limits = (m: number) => [Math.max(H0 * 60, ...spans.filter(v => v[1] <= m).map(v => v[1])), Math.min(H1 * 60, ...spans.filter(v => v[0] >= m).map(v => v[0]))];
  const down = (e: React.PointerEvent) => {                  // drag with the mouse; on touch screens the finger scrolls the timeline
    dragged.current = false;
    if (e.pointerType !== 'mouse' || (e.target as HTMLElement).closest('.ev')) return;
    const a = at(e.clientX), [lo, hi] = limits(a); let b = a;
    const move = (v: PointerEvent) => { b = Math.max(lo, Math.min(hi, at(v.clientX) + STEP)); if (Math.abs(b - a) <= STEP) return;
      dragged.current = true; dragging.current = true; setSel([Math.min(a, b), Math.max(a, b)]); };
    const up = () => { removeEventListener('pointermove', move); removeEventListener('pointerup', up); dragging.current = false;
      if (dragged.current) { setSel(null); onRange(Math.min(a, b), Math.max(a, b)); } };
    addEventListener('pointermove', move); addEventListener('pointerup', up);
  };
  const click = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.ev') || dragged.current) return;
    const m = at(e.clientX); onSlot(e.clientX, ref.current!.getBoundingClientRect().bottom + 4, m, limits(m)[1]);
  };
  return <div className="lane" ref={ref} onPointerDown={down} onClick={click}>
    {nowPct !== null && <i className="now" style={{left: `${nowPct}%`}} />}
    {room.events.map((e, i) => { const me = myEv(e, room.mail), who = me ? t('You') : e.organizer ? e.organizer.name : '';
      return <span key={i} className={['ev', e.status === 'Tentative' && 'tent', who && 'has-org', me && 'mine', new Date(e.end) < now && 'past'].filter(Boolean).join(' ')}
        style={{left: `${pct(e.start.slice(11))}%`, width: `${Math.max(1.5, pct(e.end.slice(11)) - pct(e.start.slice(11)))}%`}}
        title={`${e.start.slice(11)}–${e.end.slice(11)} ${e.subject || ''}${who ? ' · ' + who : ''}`} onClick={() => onEvent(e)}>
        {e.subject || t('Busy')}<em>{e.start.slice(11)}{who ? ' · ' + who : ''}</em></span>; })}
    {room.error ? <span className="muted">{t('Error')}</span> : !room.events.length && <span className="free">{t('Free all day')}</span>}
    {sel && <i className="sel" style={{left: pct(toHm(sel[0])) + '%', width: pct(toHm(sel[1])) - pct(toHm(sel[0])) + '%'}}>{toHm(sel[0])}–{toHm(sel[1])}</i>}
  </div>;
}

// small menu under a clicked free slot: 30 min / 1 hour / 2 hours
function QuickTimes({x, top, start, limit, onClose, onPick}: {x: number; top: number; start: number; limit: number; onClose: () => void; onPick: (end: number) => void}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const close = (e: Event) => { if (e.type === 'click' && ref.current?.contains(e.target as Node)) return; onClose(); };
    const id = setTimeout(() => { addEventListener('click', close, true); addEventListener('scroll', close, true); });
    return () => { clearTimeout(id); removeEventListener('click', close, true); removeEventListener('scroll', close, true); };
  }, [onClose]);
  return <div className="qk" ref={ref} style={{top, left: Math.max(8, Math.min(innerWidth - 300, x - 140))}}><b>{toHm(start)}</b>
    {([[30, '30 min'], [60, '1 hour'], [120, '2 hours']] as [number, string][]).map(([n, l]) =>
      <button key={n} className="btn small ghost" disabled={start + n > limit} onClick={() => onPick(start + n)}>{t(l)}</button>)}</div>;
}

// Monday to Friday: one row per room, a day strip with the free hours; a day opens the day view
function WeekView({day}: {day: string}) {
  const d0 = new Date(day + 'T00:00'), mon = new Date(d0); mon.setDate(d0.getDate() - (d0.getDay() + 6) % 7);
  const days = Array.from({length: 5}, (_, i) => { const x = new Date(mon); x.setDate(mon.getDate() + i); return x; });
  const {data, error, reload} = useLoad(() => Promise.all([Promise.all(days.map(x => api<Day>('/api/rooms?day=' + ymd(x)))), myBookings()]), [day]);
  const D = useRoomDialogs(data?.[0][0].rooms || [], reload);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [week, mineR] = data, rooms = week[0].rooms, now = new Date(), span = (H1 - H0) * 60;
  const freeH = (list: Ev[]) => { let busy = 0, end = H0 * 60;
    list.map(e => [toMin(hm0(e.start)), toMin(hm0(e.end))]).sort((p, q) => p[0] - q[0]).forEach(([a, b]) => {
      a = Math.max(a, end); b = Math.min(b, H1 * 60); if (b > a) { busy += b - a; end = b; } });
    return Math.round((span - busy) / 30) / 2; };
  const Cell = ({x, i}: {x: Room; i: number}) => { const list = week[i].rooms.find(y => y.mail === x.mail)?.events || [];
    const mineE = (e: Ev) => mineR.list.some(m => m.room === x.mail && m.starts.slice(0, 16) === e.start) || sameMail(e.organizer?.mail, session.me?.email);
    return <Link className="wcell" to={`/rooms?day=${ymd(days[i])}`}><span className="wbar">{list.map((e, j) => <i key={j} className={mineE(e) ? 'mine' : ''}
      style={{left: `${pct(hm0(e.start))}%`, width: `${Math.max(1.5, pct(hm0(e.end)) - pct(hm0(e.start)))}%`}} />)}</span>
      <small>{t('{n} h free', {n: freeH(list)})}</small>
      {list.slice(0, 3).map((e, j) => <span key={j} className={`wev ${mineE(e) ? 'mine' : ''}`}>{hm0(e.start)} {e.subject || t('Busy')}</span>)}
      {list.length > 3 && <span className="muted wmore">+{list.length - 3}</span>}</Link>; };
  return <>
    <Toolbar day={day} week={true} d0={mon} label={`${fmtDate(days[0])} – ${fmtDate(days[4])}`} onBook={() => D.setBook({day, start: '09:00'})} />
    <div className="rlay"><div className="rmain"><div className="week"><div className="wgrid"><span></span>
      {days.map(x => <b key={ymd(x)} className={`wday ${ymd(x) === ymd(now) ? 'on' : ''}`}>{dayName(x)}<small>{fmtDate(x)}</small></b>)}
      {rooms.map(x => <Fragment key={x.mail}><b className="wroom">{x.name}</b>{days.map((_, i) => <Cell key={i} x={x} i={i} />)}</Fragment>)}</div></div>
      <p className="muted rhint">{t('Open a day to book. Bars show busy time between {a}:00 and {b}:00.', {a: H0, b: H1})}</p></div>
      <BookingCards {...mineR} onCheckin={D.checkin} onEdit={D.editBk} onCancel={D.cancelBk} /></div>
    {D.dialogs}
  </>;
}

// a booking: time, subject, organizer with call / e-mail / chat (Outlook bookings: organizer unknown to the intranet)
function EventDialog({e, room, mine, onClose, onEdit, onCancel}: {e: Ev; room?: Room; mine?: Mine; onClose: () => void; onEdit: (id: number) => void; onCancel: (id: number) => void}) {
  const o = e.organizer;
  const Call = ({n}: {n: string}) => <a className="btn small ghost" {...dial(n)}>📞 {n}</a>;
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{e.subject || t('Busy')}</h2>
    <p className="muted">{room ? room.name : ''} · {fmtDate(e.start)} {e.start.slice(11)}–{e.end.slice(11)}</p>
    {o ? <div className="evorg">
      {(() => { const inner = <><Avatar p={o} /><span><b>{o.name}</b><small>{t('Organizer')}{o.title ? ' · ' + o.title : ''}</small></span></>;
        return o.id ? <Link className="mini" to={`/directory/${o.id}`} onClick={onClose}>{inner}</Link> : <a className="mini">{inner}</a>; })()}
      <div className="row">{(o.extension || o.phone) && <Call n={(o.extension || o.phone)!} />}{o.mobile && <Call n={o.mobile} />}
        {o.mail && <a className="btn small ghost" href={'mailto:' + o.mail}>✉️ {t('E-mail')}</a>}
        {chatUrl(o) && <a className="btn small ghost" href={chatUrl(o)} target="_blank" rel="noopener">💬 Chat</a>}</div></div>
      : <p className="muted">{t('Organizer not known')}</p>}
    <div className="row" style={{marginTop: 14}}>{mine?.editable && <button type="button" className="btn" id="evedit" onClick={() => onEdit(mine.id)}>{t('Edit')}</button>}
      {mine && <button type="button" className="btn danger" id="evcancel" onClick={() => onCancel(mine.id)}>{t('Cancel')}</button>}
      <button type="button" className="btn ghost" data-close>{t('Close')}</button></div></Modal>;
}

let people: Person[] | null = null;              // directory, for the colleague picker
async function directoryPeople() {
  if (!people) people = (await api<{people: Person[]}>('/api/directory')).people.filter(p => p.mail && p.mail.toLowerCase() !== (session.me?.email || '').toLowerCase());
  return people;
}

// 24-hour quarter-hour lists: the native time picker follows the browser locale (AM/PM, every minute)
function TimeSel({name, value, onChange}: {name: string; value: string; onChange: (v: string) => void}) {
  const opts = Array.from({length: 96}, (_, i) => toHm(i * 15));
  if (!opts.includes(value)) { opts.push(value); opts.sort(); }      // an Outlook booking at 10:10 keeps its time
  return <select name={name} required value={value} onChange={e => onChange(e.target.value)}>{opts.map(o => <option key={o}>{o}</option>)}</select>;
}

const FB_LABEL: Record<string, string> = {Free: 'Free', Tentative: 'Tentative', Busy: 'Busy', OOF: 'Out of office'};
function BookDialog({rooms, day: day0, start: start0, room, bk, endAt, onClose, onDone}: BookArgs & {rooms: Room[]; onClose: () => void; onDone: (day: string) => void}) {
  const [day, setDay] = useState(day0), [start, setStart] = useState(start0);
  const [end, setEnd] = useState(bk ? bk.end : endAt || toHm(Math.min(toMin(start0) + 60, 24 * 60 - 15)));
  const len = useRef(toMin(end) - toMin(start));
  const [repeat, setRepeat] = useState('none'), [busy, setBusy] = useState(false);
  const [chosen, setChosen] = useState<Map<string, string>>(new Map());   // mail → name
  const [fb, setFb] = useState<Record<string, string>>({});               // mail → Free / Tentative / Busy / OOF, for the chosen time
  const [list, setList] = useState<Person[]>([]), [q, setQ] = useState('');
  const pq = useRef<HTMLInputElement>(null), subj = useRef<HTMLInputElement>(null);
  useEffect(() => { subj.current?.focus(); directoryPeople().then(l => { setList(l);
    if (bk) setChosen(new Map(bk.attendees.map(mail => { const p = l.find(x => x.mail!.toLowerCase() === mail); return [mail, p ? p.name : mail]; }))); }).catch(() => {}); }, [bk]);
  useEffect(() => {                               // people already invited to this meeting would all read as busy
    if (bk || !chosen.size) return;
    const id = setTimeout(async () => {
      try { setFb(await api<Record<string, string>>('/api/rooms/availability', {method: 'POST', json: {people: [...chosen.keys()], day, start, end}})); } catch { /* no colours */ }
    }, 350);
    return () => clearTimeout(id);
  }, [chosen, day, start, end, bk]);
  const w = norm(q).trim();
  // best first: a name word that starts with the text ("ali" → Ali Aliyev before Natali), then other matches
  const rank = (p: Person) => { const n = norm(p.name); return w.split(/\s+/).every(x => n.split(/\s+/).some(y => y.startsWith(x))) ? 0 : n.includes(w) ? 1 : 2; };
  const hits = w.length < 2 ? [] : list.filter(p => !chosen.has(p.mail!.toLowerCase()) && norm([p.name, p.title, p.department, p.mail].join(' ')).includes(w))
    .sort((a, b) => rank(a) - rank(b) || a.name.localeCompare(b.name, 'az')).slice(0, 8);
  const add = (p: Person) => { setChosen(m => new Map(m).set(p.mail!.toLowerCase(), p.name)); setQ(''); pq.current?.focus(); };
  // moving the start keeps the meeting length
  const changeStart = (v: string) => { setStart(v); setEnd(toHm(Math.min(toMin(v) + Math.max(len.current, 15), 24 * 60 - 15))); };
  const changeEnd = (v: string) => { len.current = toMin(v) - toMin(start); setEnd(v); };
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); const f = e.currentTarget.elements as any; setBusy(true);
    const json: Record<string, unknown> = {room: f.room.value, subject: f.subject.value, day, start, end, attendees: [...chosen.keys()]};
    if (repeat !== 'none') Object.assign(json, {repeat, count: +f.count.value});
    try {
      const res = await api<{booked: number; skipped?: string[]}>('/api/rooms/book' + (bk ? '/' + bk.id : ''), {method: bk ? 'PUT' : 'POST', json});
      toast(bk ? t('Changed — everyone gets the update') : res.booked > 1 ? t('{n} meetings booked — invitations sent from your mailbox', {n: res.booked}) : t('Booked — invitations sent from your mailbox'));
      if (res.skipped?.length) alert(t('Not booked, the room is busy: {d}', {d: res.skipped.map(d => fmtDate(d)).join(', ')}));
      onDone(day);
    } catch (err) { fail(err); setBusy(false); }
  };
  return <Modal onClose={onClose}><h2 style={{marginTop: 0}}>{bk ? t('Change booking') : t('Book a room')}</h2><form id="bf" className="stack" onSubmit={submit}>
    <label>{t('Room')}<select name="room" defaultValue={room}>{rooms.map(x => <option key={x.mail} value={x.mail}>{x.name}</option>)}</select></label>
    <label>{t('Subject')}<input name="subject" ref={subj} required maxLength={120} placeholder={t('e.g. Weekly operations meeting')} defaultValue={bk ? bk.subject : ''} /></label>
    <div className="row"><label>{t('Date')}<input type="date" name="day" value={day} required onChange={e => setDay(e.target.value)} /></label>
      <label>{t('From')}<TimeSel name="start" value={start} onChange={changeStart} /></label>
      <label>{t('To')}<TimeSel name="end" value={end} onChange={changeEnd} /></label></div>
    {!bk && <div className="row"><label>{t('Repeat')}<select name="repeat" value={repeat} onChange={e => setRepeat(e.target.value)}><option value="none">{t('Does not repeat')}</option>
        <option value="weekly">{t('Every week')}</option><option value="biweekly">{t('Every 2 weeks')}</option><option value="monthly">{t('Every month')}</option></select></label>
      <label id="cntw" hidden={repeat === 'none'}>{t('Times')}<select name="count" defaultValue="5">{Array.from({length: 11}, (_, i) => <option key={i}>{i + 2}</option>)}</select></label></div>}
    <div className="fld"><span>{t('Invite colleagues')}</span><div className="picker"><div className="chips" id="chips">{[...chosen].map(([mail, name]) =>
      <span key={mail} className={`chip ${fb[mail] ? 'fb-' + fb[mail].toLowerCase() : ''}`}>{name}{FB_LABEL[fb[mail]] && <small>{t(FB_LABEL[fb[mail]])}</small>}
        <button type="button" aria-label={t('Remove')} onClick={e => { e.preventDefault(); setChosen(m => { const n = new Map(m); n.delete(mail); return n; }); }}>×</button></span>)}</div>
      <input id="pq" ref={pq} autoComplete="off" placeholder={t('Type a name…')} aria-label={t('Invite colleagues')} value={q} onChange={e => setQ(e.target.value)}
        // Enter adds only an unambiguous match; with several (two "Ziya"s) the person has to be clicked
        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); if (hits.length === 1) add(hits[0]); } }} />
      <div className="sugg" id="sugg" hidden={!hits.length}>{hits.map(p => <button type="button" key={p.id} onClick={() => add(p)}><b>{p.name}</b><small>{p.title || p.department || p.mail}</small></button>)}</div></div></div>
    <p className="muted">{t('You are the organizer: Outlook sends the invitation from you to everyone you add, and the room confirms it.')}</p>
    <p className="bnote">{t('Confirm the meeting with the QR code on the room door, from 10 minutes before the start until 10 minutes after. If nobody confirms, the room can be released.')}</p>
    <div className="row"><button className="btn" disabled={busy}>{bk ? t('Save changes') : t('Book')}</button><button type="button" className="btn ghost" data-close>{t('Close')}</button></div></form></Modal>;
}

type Door = {name: string; mail: string; booking?: {id: number; subject: string; checked_in?: boolean} | null};
// the page behind the QR sign on a room door: status, check-in, book on the spot
export function Door() {
  const {key} = useParams(), today = ymd(new Date()), nav = useNavigate();
  const {data, error, reload} = useLoad(() => Promise.all([api<Door>('/api/rooms/door/' + key), api<Day>('/api/rooms?day=' + today)]), [key]);
  const [book, setBook] = useState<BookArgs | null>(null);
  const open = useRef(false); open.current = !!book;
  useEffect(() => { const id = setInterval(() => { if (!document.hidden && !open.current) reload(); }, 30000); return () => clearInterval(id); }, [reload]);
  if (error) return <ErrorPanel error={error} />;
  if (!data) return null;
  const [d, r] = data, x = r.rooms.find(y => y.mail === d.mail) || {events: [] as Ev[]} as Room, now = new Date(), s = roomNow(x, now), b = d.booking;
  const o = s.busy ? s.ev.organizer : null;
  const next = x.events.filter(e => toMin(hm0(e.start)) > nowMin(now)).slice(0, 3);
  const free = s.busy ? 0 : s.until === null ? 120 : s.until - nowMin(now);
  const checkin = async () => { try { await api(`/api/rooms/book/${b!.id}/checkin`, {method: 'POST'}); toast(t('Checked in')); reload(); } catch (err) { fail(err); } };
  const go = (n: number) => { const a = Math.ceil(nowMin(new Date()) / STEP) * STEP; setBook({day: today, start: toHm(a), room: d.mail, endAt: toHm(a + n)}); };
  return <><div className={`door ${s.busy ? 'busy' : 'free'}`}><h1>{d.name}</h1><span className="pill">{t(s.busy ? 'Busy' : 'Free')}</span>
    <p className="big">{s.busy ? t('{n} min left', {n: s.left}) : s.until === null ? t('Free all day') : t('Free until {t}', {t: toHm(s.until)})}</p>
    {s.busy && <p className="muted">{s.ev.subject || t('Busy')}{o ? ' · ' + o.name : ''}</p>}
    {b && (b.checked_in ? <p className="dok">✓ {t('Checked in')}: {b.subject}</p> : <button className="btn" id="dci" onClick={checkin}>{t('Check in')}: {b.subject}</button>)}
    {free >= 15 && <div className="row dbk">{([[15, '15 min'], [30, '30 min'], [60, '1 hour']] as [number, string][]).map(([n, l]) =>
      <button key={n} className="btn ghost" disabled={n > free} onClick={() => go(n)}>{t('Book')} {t(l)}</button>)}</div>}
    {next.length > 0 && <><h2>{t('Next')}</h2>{next.map((e, i) => <p key={i} className="dnext"><b>{hm0(e.start)}–{hm0(e.end)}</b> {e.subject || t('Busy')}</p>)}</>}
    <Link className="btn ghost small" to="/rooms">{t('All rooms')}</Link></div>
    {book && <BookDialog rooms={r.rooms} {...book} onClose={() => setBook(null)} onDone={d => { setBook(null); nav('/rooms?day=' + d); }} />}</>;
}
