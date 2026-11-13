// Language (en default, ru, az), translations and date formats. The App re-renders everything when the language changes.
import {DICT} from './dict';

export const LANGS = {en: 'English', ru: 'Русский', az: 'Azərbaycanca'} as const;
export type Lang = keyof typeof LANGS;
const LOCALE: Record<Lang, string> = {en: 'en-GB', ru: 'ru-RU', az: 'az-Latn-AZ'};

const saved = localStorage.getItem('lang');
export let lang: Lang = saved && saved in LANGS ? (saved as Lang) : 'en';
document.documentElement.lang = lang;
export function setLang(l: string) {
  lang = l in LANGS ? (l as Lang) : 'en';
  localStorage.setItem('lang', lang); document.documentElement.lang = lang;
}

// t('English text', {n: 3}) → translation (falls back to English); {n} placeholders are filled in
export function t(key: string, vars?: Record<string, string | number | null | undefined>): string {
  let s = (lang !== 'en' && DICT[lang]?.[key]) || key;
  if (vars) s = s.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''));
  return s;
}
export type Localised = Partial<Record<Lang, string>> | null | undefined;
export const pick = (obj: Localised): string => obj ? (obj[lang] || obj.en || Object.values(obj)[0] || '') : '';

type D = string | number | Date | null | undefined;
export const fmtDate = (s: D, opts: Intl.DateTimeFormatOptions = {day: 'numeric', month: 'long', year: 'numeric'}) =>
  s ? new Date(s).toLocaleDateString(LOCALE[lang], opts) : '';
export const fmtTime = (s: D) => s ? new Date(s).toLocaleTimeString(LOCALE[lang], {hour: '2-digit', minute: '2-digit'}) : '';
export const monthName = (m: number) => new Date(2024, m - 1, 1).toLocaleDateString(LOCALE[lang], {month: 'long'});
export const dayName = (d: Date, style: 'long' | 'short' | 'narrow' = 'long') => d.toLocaleDateString(LOCALE[lang], {weekday: style});
export const ymd = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
export const norm = (s: string | null | undefined) => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ı/g, 'i').replace(/ə/g, 'e');
