"""Intranet usage analytics for IT (AD group Intranet-IT-Editors).

The browser reports each page view (route pattern only, e.g. /news/:id). Stored: day, page, a salted hash of the
user name (no names), department, language, mobile/desktop. Kept 400 days.
"""
import hashlib
import secrets as pysecrets
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from .core import User, current_user, directory, me_person, pool, role, run_schema

run_schema("""
CREATE TABLE IF NOT EXISTS settings (key text PRIMARY KEY, value text NOT NULL);
CREATE TABLE IF NOT EXISTS page_views (
  id bigserial PRIMARY KEY, day date NOT NULL DEFAULT current_date, ts timestamptz NOT NULL DEFAULT now(),
  page text NOT NULL, user_hash text NOT NULL, department text NOT NULL DEFAULT '', lang text NOT NULL DEFAULT '',
  mobile boolean NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS page_views_day ON page_views (day);
INSERT INTO settings (key, value) VALUES ('analytics_salt', md5(random()::text || clock_timestamp()::text))
  ON CONFLICT DO NOTHING;
""")

router = APIRouter()
it = role("it")
_salt = None


def _hash(username):
    global _salt
    if _salt is None:
        with pool.connection() as c:
            _salt = c.execute("SELECT value FROM settings WHERE key='analytics_salt'").fetchone()["value"]
    return hashlib.sha256((_salt + username.lower()).encode()).hexdigest()[:24]


class View(BaseModel):
    page: str = Field(max_length=80, pattern=r"^/[\w/:.-]*$")
    lang: str = Field(default="", max_length=5)


@router.post("/api/track", status_code=204)
def track(v: View, request: Request, user: User = Depends(current_user)):
    p = me_person(user)
    ua = request.headers.get("user-agent", "")
    with pool.connection() as c:
        c.execute("INSERT INTO page_views (page, user_hash, department, lang, mobile) VALUES (%s,%s,%s,%s,%s)",
                  (v.page, _hash(user.username), (p or {}).get("department", ""), v.lang[:5],
                   any(m in ua for m in ("Mobile", "Android", "iPhone"))))
        if pysecrets.randbelow(200) == 0:
            c.execute("DELETE FROM page_views WHERE day < current_date - 400")


@router.get("/api/analytics")
def report(days: int = 30, user: User = Depends(it)):
    days = max(7, min(days, 365))
    since = date.today() - timedelta(days=days - 1)
    q = lambda sql, *a: c.execute(sql, a).fetchall()
    with pool.connection() as c:
        daily = q("SELECT day, count(DISTINCT user_hash) AS users, count(*) AS views FROM page_views WHERE day >= %s "
                  "GROUP BY day ORDER BY day", since)
        uniq = c.execute("SELECT count(DISTINCT user_hash) AS n FROM page_views WHERE day >= %s", (since,)).fetchone()["n"]
        wau = c.execute("SELECT count(DISTINCT user_hash) AS n FROM page_views WHERE day >= current_date - 6").fetchone()["n"]
        pages = q("SELECT page, count(*) AS views, count(DISTINCT user_hash) AS users FROM page_views WHERE day >= %s "
                  "GROUP BY page ORDER BY views DESC LIMIT 15", since)
        depts = q("SELECT department, count(DISTINCT user_hash) AS users FROM page_views WHERE day >= %s "
                  "GROUP BY department ORDER BY users DESC", since)
        langs = q("SELECT lang, count(DISTINCT user_hash) AS users FROM page_views WHERE day >= %s GROUP BY lang", since)
        mobile = c.execute("SELECT count(*) FILTER (WHERE mobile) AS m, count(*) AS t FROM page_views WHERE day >= %s",
                           (since,)).fetchone()
        hours = q("SELECT extract(hour FROM ts AT TIME ZONE 'Asia/Baku')::int AS h, count(*) AS views FROM page_views "
                  "WHERE day >= %s GROUP BY h ORDER BY h", since)
    staff = len(directory.people())
    by_dept = {}
    for p in directory.people():
        by_dept[p["department"] or ""] = by_dept.get(p["department"] or "", 0) + 1
    return {"days": days, "staff": staff, "users": uniq, "wau": wau,
            "daily": [{"day": r["day"].isoformat(), "users": r["users"], "views": r["views"]} for r in daily],
            "pages": pages, "langs": langs, "hours": hours,
            "mobile_share": round(100 * mobile["m"] / mobile["t"]) if mobile["t"] else 0,
            "departments": [{"department": d["department"], "users": d["users"], "staff": by_dept.get(d["department"], 0)}
                            for d in depts]}
