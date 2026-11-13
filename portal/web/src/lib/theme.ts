// Light / dark theme: the person's choice (localStorage "theme"), otherwise the system setting. Sets <html data-theme>.
export type Theme = 'light' | 'dark';
const sys = matchMedia('(prefers-color-scheme: dark)');
const saved = () => localStorage.getItem('theme') as Theme | null;
export const theme = (): Theme => saved() || (sys.matches ? 'dark' : 'light');
const apply = () => { document.documentElement.dataset.theme = theme(); };
apply();
sys.addEventListener('change', () => { if (!saved()) { apply(); dispatchEvent(new Event('themechange')); } });
export function setTheme(t: Theme) { localStorage.setItem('theme', t); apply(); dispatchEvent(new Event('themechange')); }
