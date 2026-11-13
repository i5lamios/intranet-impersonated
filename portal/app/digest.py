"""Weekly news e-mail: every DIGEST_WEEKDAY (0 = Monday) after DIGEST_HOUR (Asia/Baku) the news published since the
last digest go to DIGEST_TO (allstaff@) from DIGEST_FROM (hrnews@, svc-intranet has Send As), via Exchange SMTP 587.
One row per ISO week in digest_log makes the two replicas send it once; no news → nothing is sent.
"""
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta
from html import escape

from .core import MAIL_LOGO, UPLOADS, mail_configured, send_mail

log = logging.getLogger("digest")

ENABLED = os.environ.get("DIGEST_ENABLED", "0") == "1"
TO = os.environ.get("DIGEST_TO", "allstaff@example.com")
FROM = os.environ.get("DIGEST_FROM", "hrnews@example.com")
FROM_NAME = os.environ.get("DIGEST_FROM_NAME", "Company HR")
WEEKDAY = int(os.environ.get("DIGEST_WEEKDAY", "0"))
HOUR = int(os.environ.get("DIGEST_HOUR", "9"))
SITE = os.environ.get("SITE_URL", "https://intranet.example.com")

MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avqust", "sentyabr", "oktyabr", "noyabr", "dekabr"]




def en_date(d):
    return f"{d.day} {d:%B} {d.year}"


def az_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def render(items, week_label):
    navy, blue, mute = "#1B2B5B", "#2E6DB4", "#6B7280"
    cards = []
    for n in items:
        url = f"{SITE}/news/{n['id']}"
        img = (f'<tr><td><a href="{url}"><img src="{_cover_src(n["cover"])}" width="560" alt="" '
               f'style="display:block;width:100%;max-width:560px;border-radius:8px 8px 0 0;border:0"></a></td></tr>') if n.get("cover") else ""
        cards.append(f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #DCE3EE;border-radius:8px;margin:0 0 18px">
{img}<tr><td style="padding:16px 20px 18px;font-family:Segoe UI,Arial,sans-serif">
<div style="font-size:12px;color:{mute}">{az_date(n['published_at'])}</div>
<a href="{url}" style="display:block;font-size:19px;font-weight:700;color:{navy};text-decoration:none;margin:4px 0 8px">{escape(n['title'])}</a>
<div style="font-size:15px;line-height:1.5;color:#1F2937">{escape(n['summary'])}</div>
<a href="{url}" style="display:inline-block;margin-top:12px;color:{blue};font-weight:600;font-size:14px">Ətraflı · Read more →</a>
</td></tr></table>""")
    return f"""<!doctype html><html lang="az"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;background:#EEF2F7"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF2F7"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">
<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td height="6" style="background:#3FA34D;font-size:0;line-height:0">&nbsp;</td>
<td height="6" style="background:{blue};font-size:0;line-height:0">&nbsp;</td><td height="6" style="background:#D2262F;font-size:0;line-height:0">&nbsp;</td></tr></table></td></tr>
<tr><td style="background:#fff;padding:18px 20px;border-bottom:1px solid #DCE3EE"><img src="{MAIL_LOGO}" height="36" alt="Company" style="display:block;border:0"></td></tr>
<tr><td style="padding:22px 20px 6px;font-family:Segoe UI,Arial,sans-serif"><div style="font-size:22px;font-weight:700;color:{navy}">Həftənin xəbərləri</div>
<div style="font-size:14px;color:{mute}">News of the week · {week_label}</div></td></tr>
<tr><td style="padding:12px 20px">{''.join(cards)}</td></tr>
<tr><td style="padding:4px 20px 24px;font-family:Segoe UI,Arial,sans-serif;font-size:12px;color:{mute};text-align:center">
Bütün xəbərlər · All news: <a href="{SITE}/news" style="color:{blue}">intranet.example.com</a><br>Company · daxili istifadə üçün · internal use only</td></tr>
</table></td></tr></table></body></html>"""


# ---------- one post as an e-mail ("E-mail to all staff" in the news editor) ----------
ORDER = ("en", "az", "ru")                          # English first: the site's default language
_INLINE = {                                        # Outlook ignores most <style>: element styles go inline
    "p": "margin:0 0 12px", "h2": "font-size:18px;color:#1B2B5B;margin:20px 0 8px",
    "h3": "font-size:16px;color:#1B2B5B;margin:16px 0 4px", "ul": "margin:0 0 12px;padding-left:22px",
    "ol": "margin:0 0 12px;padding-left:22px", "li": "margin:0 0 4px", "a": "color:#2E6DB4",
    "img": "max-width:100%;height:auto;border:0;border-radius:6px", "blockquote": "margin:0 0 12px;padding:4px 14px;border-left:4px solid #2E6DB4;color:#6B7280",
    "td": "border:1px solid #DCE3EE;padding:6px 10px", "th": "border:1px solid #DCE3EE;padding:6px 10px",
}


_UPLOAD_IMG = re.compile(r'src="/uploads/([0-9a-f]{32}\.jpg)"')


def _cid(name):
    return name.replace(".jpg", "@example.com")


def _width(name, full=556):
    """Outlook desktop ignores max-width: give pictures their real width, at most the column."""
    try:
        from PIL import Image
        with Image.open(os.path.join(UPLOADS, name)) as im:
            return min(full, im.width)
    except Exception:
        return full


def mail_html(body):
    """Editor HTML → e-mail HTML: uploaded pictures embedded (cid:, sent inside the e-mail), other links absolute,
    inline styles."""
    body = re.sub(r'<img([^>]*?)src="/uploads/([0-9a-f]{32}\.jpg)"([^>]*)>', lambda m: (
        f'<img{m.group(1)}src="cid:{_cid(m.group(2))}"{re.sub(r"\s(width|height)=\"[^\"]*\"", "", m.group(3))} width="{_width(m.group(2))}">'), body)
    body = re.sub(r'(src|href)="/', lambda m: f'{m.group(1)}="{SITE}/', body)
    for tag, css in _INLINE.items():
        body = re.sub(rf'<{tag}(\s[^>]*)?>', lambda m, t=tag, c=css: _style(t, m.group(1) or "", c), body)
    return re.sub(r'<img((?:(?!width=)[^>])*)>', r'<img\1 width="556">', body)


def inline_images(html):
    """(cid, bytes) for every embedded picture in the rendered e-mail."""
    out = []
    for cid in dict.fromkeys(re.findall(r'src="cid:([0-9a-f]{32})@company\.az"', html)):
        path = os.path.join(UPLOADS, cid + ".jpg")
        if os.path.exists(path):
            with open(path, "rb") as f:
                out.append((f"{cid}@example.com", f.read()))
    return out


def _style(tag, attrs, css):
    if 'style="' in attrs:
        return "<" + tag + attrs.replace('style="', 'style="' + css + ";", 1) + ">"
    return f'<{tag}{attrs} style="{css}">'


def _cover_src(path):
    m = re.fullmatch(r"/uploads/([0-9a-f]{32}\.jpg)", path or "")
    return f"cid:{_cid(m.group(1))}" if m else SITE + escape(path)


def render_post(n):
    """All language versions of a post (EN, AZ, RU), in the intranet look."""
    url = f"{SITE}/news/{n['id']}"
    have = {n["lang"]: (n["title"], n["body_html"])}
    have.update({lg: (v["title"], v["body_html"]) for lg, v in (n.get("i18n") or {}).items() if v.get("title") and lg != n["lang"]})
    versions = [(lg, *have[lg]) for lg in ORDER if lg in have]
    nav = " · ".join(f'<a href="#l-{lg}" style="color:#2E6DB4;text-decoration:none;font-weight:600">{lg.upper()}</a>' for lg, _, _ in versions)
    parts = []
    for i, (lg, title, body) in enumerate(versions):
        parts.append(f"""<tr><td style="padding:{'22px' if i == 0 else '26px'} 22px 8px;font-family:Segoe UI,Arial,sans-serif;font-size:15px;line-height:1.55;color:#1F2937;{'' if i == 0 else 'border-top:1px solid #DCE3EE'}">
<a name="l-{lg}"></a><div style="font-size:11px;letter-spacing:.06em;color:#6B7280">{lg.upper()}</div>
<div style="font-size:22px;font-weight:700;color:#1B2B5B;margin:4px 0 14px">{escape(title)}</div>{mail_html(body)}</td></tr>""")
    cover = (f'<tr><td><a href="{url}"><img src="{_cover_src(n["cover"])}" width="600" alt="" style="display:block;width:100%;max-width:600px;border:0"></a></td></tr>'
             if n.get("cover") else "")
    return f"""<!doctype html><html lang="{versions[0][0]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;background:#EEF2F7"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF2F7"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border:1px solid #DCE3EE">
<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td height="6" style="background:#3FA34D;font-size:0;line-height:0">&nbsp;</td>
<td height="6" style="background:#2E6DB4;font-size:0;line-height:0">&nbsp;</td><td height="6" style="background:#D2262F;font-size:0;line-height:0">&nbsp;</td></tr></table></td></tr>
<tr><td style="padding:16px 22px;border-bottom:1px solid #DCE3EE"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
<td><img src="{MAIL_LOGO}" height="34" alt="Company" style="display:block;border:0"></td>
<td align="right" style="font-family:Segoe UI,Arial,sans-serif;font-size:12px;color:#6B7280">{en_date(n['published_at'] or datetime.now())}{'<br>' + nav if len(versions) > 1 else ''}</td></tr></table></td></tr>
{cover}{''.join(parts)}{_files(n)}
<tr><td style="padding:10px 22px 24px"><a href="{url}" style="display:inline-block;background:#2E6DB4;color:#fff;text-decoration:none;font-family:Segoe UI,Arial,sans-serif;font-weight:600;font-size:14px;padding:10px 18px;border-radius:6px">İntranetdə oxu · Read on the intranet</a></td></tr>
<tr><td style="padding:14px 22px;font-family:Segoe UI,Arial,sans-serif;font-size:12px;color:#6B7280;border-top:1px solid #DCE3EE;text-align:center">
Bütün xəbərlər · All news: <a href="{SITE}/news" style="color:#2E6DB4">intranet.example.com</a><br>Company · daxili istifadə üçün · internal use only</td></tr>
</table></td></tr></table></body></html>"""


def _files(n):
    if not n.get("attachments"):
        return ""
    rows = "".join(f'<div style="margin:4px 0">📎 {escape(a["name"])} <span style="color:#6B7280">({max(1, a["size"] // 1024)} KB)</span></div>'
                   for a in n["attachments"])
    return (f'<tr><td style="padding:6px 22px 4px;font-family:Segoe UI,Arial,sans-serif;font-size:14px;color:#1F2937">'
            f'<div style="font-weight:700;color:#1B2B5B;margin-bottom:4px">Əlavələr · Attachments · Вложения</div>{rows}</td></tr>')


def subject(n):
    """English title when there is one (site default), else the main one."""
    en = (n.get("i18n") or {}).get("en") or {}
    return n["title"] if n["lang"] == "en" or not en.get("title") else en["title"]


def send_post(n, to=None, files=()):
    html = render_post(n)
    send_mail(to or TO, subject(n), html, f"{n['title']}\n\n{SITE}/news/{n['id']}", sender=FROM, sender_name=FROM_NAME,
              attachments=files, inline=inline_images(html))


class Digest:
    def __init__(self, pool):
        self.pool = pool                                  # table digest_log: created with the schema in main.py

    @property
    def configured(self):
        return mail_configured()

    def items(self, since):
        with self.pool.connection() as c:
            return c.execute("SELECT id, title, summary, cover, published_at FROM news WHERE published AND published_at > %s "
                             "ORDER BY pinned DESC, published_at DESC LIMIT 20", (since,)).fetchall()

    def last_sent(self):
        with self.pool.connection() as c:
            row = c.execute("SELECT max(sent_at) AS t FROM digest_log WHERE status = 'sent'").fetchone()
        return row["t"] if row and row["t"] else datetime.now().astimezone() - timedelta(days=7)

    def preview(self):
        items = self.items(self.last_sent())
        return items, render(items, az_date(datetime.now()))

    def send(self, to, items):
        html = render(items, az_date(datetime.now()))
        send_mail(to, f"Həftənin xəbərləri · News of the week — {az_date(datetime.now())}", html,
                  "Həftənin xəbərləri · News of the week\n\n" + "\n".join(f"- {n['title']}\n  {SITE}/news/{n['id']}" for n in items),
                  sender=FROM, sender_name=FROM_NAME, inline=inline_images(html))

    # ---- on / off: switch in Admin → Weekly e-mail (settings 'digest_on'); DIGEST_ENABLED is only the default ----
    def is_on(self):
        with self.pool.connection() as c:
            row = c.execute("SELECT value FROM settings WHERE key='digest_on'").fetchone()
        return (row["value"] == "1") if row else ENABLED

    def set_on(self, on: bool):
        with self.pool.connection() as c:
            c.execute("INSERT INTO settings (key, value) VALUES ('digest_on', %s) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value",
                      ("1" if on else "0",))

    # ---- weekly schedule ----
    def start(self):
        threading.Thread(target=self._loop, name="digest", daemon=True).start()

    def _loop(self):
        while True:
            try:
                self.tick()
            except Exception as e:
                log.error("digest: %s", e)
            time.sleep(300)

    def tick(self):
        now = datetime.now()
        if now.weekday() != WEEKDAY or now.hour < HOUR or not self.configured or not self.is_on():
            return
        week = "%d-W%02d" % now.isocalendar()[:2]
        since = self.last_sent()
        with self.pool.connection() as c:                 # claim the week (the other replica gets no row back)
            if not c.execute("INSERT INTO digest_log (week, status) VALUES (%s, 'sending') ON CONFLICT DO NOTHING RETURNING week",
                             (week,)).fetchone():
                return
        items = self.items(since)
        status, err = ("empty", None) if not items else ("sent", None)
        if items:
            try:
                self.send(TO, items)
            except Exception as e:
                status, err = "failed", str(e)[:500]
        with self.pool.connection() as c:
            c.execute("UPDATE digest_log SET status=%s, items=%s, sent_at=now(), error=%s WHERE week=%s",
                      (status, len(items), err, week))
        log.info("digest %s: %s (%d items)", week, status, len(items))
