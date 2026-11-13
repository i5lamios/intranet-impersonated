// Short message at the bottom of the screen (outside React, so any code can call it).
export function toast(msg: string) {
  const el = document.createElement('div'); el.className = 'toast'; el.textContent = msg;
  document.body.append(el); setTimeout(() => el.remove(), 3500);
}
