"""IT Help Center: short how-to articles from IT in en / ru / az, for signed-in staff (help for people who cannot sign
in is the password site and the Helpdesk); edited by AD group Intranet-IT-Editors."""
from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from .analytics import _hash
from .core import User, current_user, pool, role, run_schema, sanitize
from .helpseed import ARTICLES

LANGS = ("en", "ru", "az")
CATEGORIES = ("apps", "accounts", "mail", "remote", "devices", "security", "support", "admin")   # admin = editors only

run_schema("""
CREATE TABLE IF NOT EXISTS help_articles (
  id serial PRIMARY KEY, slug text NOT NULL UNIQUE, category text NOT NULL, sort int NOT NULL DEFAULT 100,
  title jsonb NOT NULL, body jsonb NOT NULL, published boolean NOT NULL DEFAULT true,
  updated_by text, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS help_seeded (slug text PRIMARY KEY);
-- "Was this helpful?": one vote per person per article (salted hash, no names); searches that found nothing
CREATE TABLE IF NOT EXISTS help_feedback (slug text NOT NULL, voter text NOT NULL, helpful boolean NOT NULL,
  at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (slug, voter));
CREATE TABLE IF NOT EXISTS help_search_miss (id bigserial PRIMARY KEY, q text NOT NULL, at timestamptz NOT NULL DEFAULT now());
""")
with pool.connection() as _c:                        # starter articles: added once (deleting one keeps it deleted), then
    done = {r["slug"] for r in _c.execute("SELECT slug FROM help_seeded").fetchall()}
    for a in ARTICLES:
        if a["slug"] in done:                        # they follow this file until IT edits them on the site
            _c.execute("UPDATE help_articles SET title=%s, body=%s, updated_at=now() WHERE slug=%s AND updated_by='seed' "
                       "AND (title<>%s OR body<>%s)", (Jsonb(a["title"]), Jsonb(a["body"]), a["slug"], Jsonb(a["title"]), Jsonb(a["body"])))
            continue
        _c.execute("INSERT INTO help_articles (slug, category, sort, title, body, published, updated_by) VALUES (%s,%s,%s,%s,%s,%s,'seed') "
                   "ON CONFLICT (slug) DO NOTHING",
                   (a["slug"], a["category"], a["sort"], Jsonb(a["title"]), Jsonb(a["body"]), a.get("published", True)))
        _c.execute("INSERT INTO help_seeded (slug) VALUES (%s) ON CONFLICT DO NOTHING", (a["slug"],))

router = APIRouter()
it = role("it")


def _out(r, full=True):
    d = dict(r)
    d["updated_at"] = d["updated_at"].isoformat(timespec="minutes")
    if not full:
        d.pop("body")
    return d


def _editor(u: User) -> bool:
    """Admin guides (category "admin") are for people with an editor role (HR, HSE or IT AD group)."""
    return any(u.has(k) for k in ("news", "hse", "it"))


@router.get("/api/help")
def articles(all: bool = False, user: User = Depends(current_user)):
    with pool.connection() as c:
        rows = c.execute("SELECT * FROM help_articles " + ("" if all else "WHERE published ") +
                         "ORDER BY category, sort, slug").fetchall()
    ed = _editor(user)
    return [_out(r, False) for r in rows if ed or r["category"] != "admin"]


@router.get("/api/help/{slug}")
def article(slug: str, user: User = Depends(current_user)):
    with pool.connection() as c:
        r = c.execute("SELECT * FROM help_articles WHERE slug=%s", (slug,)).fetchone()
    if not r or (r["category"] == "admin" and not _editor(user)):
        raise HTTPException(404)
    return _out(r)


class ArticleIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    category: str = Field(pattern="^(" + "|".join(CATEGORIES) + ")$")
    sort: int = 100
    title: dict[str, str]
    body: dict[str, str]
    published: bool = True


def _clean(a: ArticleIn):
    title = {k: v.strip()[:200] for k, v in a.title.items() if k in LANGS and v.strip()}
    body = {k: sanitize(v) for k, v in a.body.items() if k in LANGS and v.strip()}
    if "en" not in title:
        raise HTTPException(422, "an English title is required")
    return Jsonb(title), Jsonb(body)


@router.post("/api/help", status_code=201)
def create(a: ArticleIn, user: User = Depends(it)):
    t, b = _clean(a)
    with pool.connection() as c:
        if c.execute("SELECT 1 FROM help_articles WHERE slug=%s", (a.slug,)).fetchone():
            raise HTTPException(409, "this address is taken")
        c.execute("INSERT INTO help_articles (slug, category, sort, title, body, published, updated_by) "
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)", (a.slug, a.category, a.sort, t, b, a.published, user.username))
    return {"slug": a.slug}


@router.put("/api/help/{slug}")
def update(slug: str, a: ArticleIn, user: User = Depends(it)):
    t, b = _clean(a)
    with pool.connection() as c:
        r = c.execute("UPDATE help_articles SET slug=%s, category=%s, sort=%s, title=%s, body=%s, published=%s, "
                      "updated_by=%s, updated_at=now() WHERE slug=%s RETURNING slug",
                      (a.slug, a.category, a.sort, t, b, a.published, user.username, slug)).fetchone()
    if not r:
        raise HTTPException(404)
    return {"slug": a.slug}


@router.delete("/api/help/{slug}", status_code=204)
def delete(slug: str, user: User = Depends(it)):
    with pool.connection() as c:
        c.execute("DELETE FROM help_articles WHERE slug=%s", (slug,))
    return Response(status_code=204)


class Vote(BaseModel):
    helpful: bool


@router.post("/api/help/{slug}/feedback", status_code=204)
def vote(slug: str, v: Vote, user: User = Depends(current_user)):
    with pool.connection() as c:
        if not c.execute("SELECT 1 FROM help_articles WHERE slug=%s", (slug,)).fetchone():
            raise HTTPException(404)
        c.execute("INSERT INTO help_feedback (slug, voter, helpful) VALUES (%s,%s,%s) ON CONFLICT (slug, voter) "
                  "DO UPDATE SET helpful=EXCLUDED.helpful, at=now()", (slug, _hash(user.username), v.helpful))
    return Response(status_code=204)


class Miss(BaseModel):
    q: str = Field(min_length=3, max_length=80)


@router.post("/api/help/search-miss", status_code=204)
def search_miss(m: Miss, user: User = Depends(current_user)):
    with pool.connection() as c:
        c.execute("INSERT INTO help_search_miss (q) VALUES (%s)", (" ".join(m.q.lower().split()),))
        c.execute("DELETE FROM help_search_miss WHERE at < now() - interval '180 days'")
    return Response(status_code=204)


@router.get("/api/help-stats")
def help_stats(user: User = Depends(it)):
    with pool.connection() as c:
        votes = c.execute("SELECT slug, count(*) FILTER (WHERE helpful) AS yes, count(*) FILTER (WHERE NOT helpful) AS no "
                          "FROM help_feedback GROUP BY slug").fetchall()
        misses = c.execute("SELECT q, count(*) AS n, max(at)::date AS last FROM help_search_miss WHERE at > now() - interval '90 days' "
                           "GROUP BY q ORDER BY n DESC, last DESC LIMIT 30").fetchall()
    return {"votes": {v["slug"]: {"yes": v["yes"], "no": v["no"]} for v in votes},
            "misses": [{"q": m["q"], "n": m["n"], "last": m["last"].isoformat()} for m in misses]}
