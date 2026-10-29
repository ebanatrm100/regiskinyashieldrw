"""Real photos from the open web, from several licensed sources at once, with credit and licence for each picture.

  Wikimedia Commons (always)      free-licence photos            no key
  Openverse (always)              Creative Commons images        no key (optional OPENVERSE_CLIENT_ID + OPENVERSE_CLIENT_SECRET for higher limits)
  Pixabay                         free-to-use photos             PIXABAY_API_KEY
  Pexels                          free-to-use photos             PEXELS_API_KEY
  Unsplash                        free-to-use photos             UNSPLASH_ACCESS_KEY

All sources are searched in parallel with short time-outs; a source that fails is skipped for a growing cool-down and the others still answer. Results are
cached (one hour) so many people asking for the same thing cost one search. Pictures are linked, never copied through this server (fast, light, scalable).
Safe-search is on. This is a licensed-image search, NOT a scraper of every website: copying pictures from arbitrary pages would break licences, so it does not.
Every failure returns []. Item: {thumb, url, title, creator, license, page, source}; photos() adapts to the older {caption,url,license,page} shape."""
from __future__ import annotations
import json, re, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import settings
import image_pool as POOL

UA = "KinyaShieldRW/1.0 (https://regiskinyashieldrw.streamlit.app; educational safety assistant)"
TIMEOUT = 7
CACHE = POOL.Cache(max_bytes=20 * 1024 * 1024, ttl=3600, max_items=3000)
_BLOCK = re.compile(r"\b(?:nude|naked|nsfw|porn|erotic|sex|sexy|xxx|gore|corpse|undress|lingerie|nudity)\b", re.I)
_TOKEN = {"v": None, "exp": 0.0}


def _get(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=TIMEOUT) as r:    # noqa: S310 (https hosts fixed below)
        return json.loads(r.read().decode("utf-8", "replace"))


def _safe_url(u):
    """https only, a real host name (no IP literals, no localhost, no credentials)."""
    try:
        p = urllib.parse.urlparse(str(u or ""))
    except Exception:
        return ""
    host = p.hostname or ""
    if p.scheme != "https" or not host or "@" in p.netloc or host == "localhost" or re.fullmatch(r"[\d.:]+", host) or "." not in host:
        return ""
    return str(u)


def _item(thumb, url, title, creator, lic, page, source):
    thumb, url, page = _safe_url(thumb), _safe_url(url) or _safe_url(thumb), _safe_url(page)
    if not thumb:
        return None
    return {"thumb": thumb, "url": url or thumb, "title": re.sub(r"\s+", " ", str(title or "")).strip()[:100] or source, "creator": str(creator or "")[:60],
            "license": str(lic or "")[:50], "page": page or url or thumb, "source": source}


# ------------------------------------------------------------------ sources
def _wikimedia(q, page, n):
    if page > 1:
        return []
    import images_db
    return [_item(p["url"], p["url"], p["caption"], "", p.get("license", ""), p["page"], "Wikimedia Commons") for p in images_db.photos(q, n, extra=False)]


def _openverse_headers():
    cid, sec = settings.get("OPENVERSE_CLIENT_ID"), settings.get("OPENVERSE_CLIENT_SECRET")
    if not (cid and sec):
        return {}
    if _TOKEN["v"] and _TOKEN["exp"] > time.time() + 60:
        return {"Authorization": "Bearer " + _TOKEN["v"]}
    try:
        body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": sec}).encode()
        req = urllib.request.Request("https://api.openverse.org/v1/auth_tokens/token/", data=body, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:                                  # noqa: S310
            d = json.loads(r.read().decode())
        _TOKEN["v"], _TOKEN["exp"] = d.get("access_token"), time.time() + int(d.get("expires_in", 3600))
        return {"Authorization": "Bearer " + _TOKEN["v"]} if _TOKEN["v"] else {}
    except Exception:
        return {}


def _openverse(q, page, n):
    u = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "page": page, "page_size": n, "mature": "false", "category": "photograph"})
    out = []
    for r in (_get(u, _openverse_headers()).get("results") or []):
        lic = (r.get("license") or "").upper() + (" " + r["license_version"] if r.get("license_version") else "")
        out.append(_item(r.get("thumbnail") or r.get("url"), r.get("url"), r.get("title"), r.get("creator"), lic.strip(), r.get("foreign_landing_url"), "Openverse"))
    return out


def _pixabay(q, page, n):
    k = settings.get("PIXABAY_API_KEY")
    if not k:
        raise KeyError("no key")
    u = "https://pixabay.com/api/?" + urllib.parse.urlencode({"key": k, "q": q, "image_type": "photo", "safesearch": "true", "per_page": max(3, n), "page": page})
    return [_item(r.get("webformatURL"), r.get("largeImageURL"), r.get("tags"), r.get("user"), "Pixabay Content License", r.get("pageURL"), "Pixabay") for r in (_get(u).get("hits") or [])[:n]]


def _pexels(q, page, n):
    k = settings.get("PEXELS_API_KEY")
    if not k:
        raise KeyError("no key")
    u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "per_page": n, "page": page})
    return [_item((r.get("src") or {}).get("medium"), (r.get("src") or {}).get("large"), r.get("alt"), r.get("photographer"), "Pexels License", r.get("url"), "Pexels") for r in (_get(u, {"Authorization": k}).get("photos") or [])]


def _unsplash(q, page, n):
    k = settings.get("UNSPLASH_ACCESS_KEY")
    if not k:
        raise KeyError("no key")
    u = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": n, "page": page, "content_filter": "high"})
    return [_item((r.get("urls") or {}).get("small"), (r.get("urls") or {}).get("regular"), r.get("alt_description"), (r.get("user") or {}).get("name"), "Unsplash License", (r.get("links") or {}).get("html"), "Unsplash")
            for r in (_get(u, {"Authorization": "Client-ID " + k}).get("results") or [])]


SOURCES = [("Wikimedia Commons", _wikimedia), ("Openverse", _openverse), ("Pixabay", _pixabay), ("Pexels", _pexels), ("Unsplash", _unsplash)]


def configured():
    names = ["Wikimedia Commons", "Openverse"]
    for nm, key in (("Pixabay", "PIXABAY_API_KEY"), ("Pexels", "PEXELS_API_KEY"), ("Unsplash", "UNSPLASH_ACCESS_KEY")):
        if settings.get(key):
            names.append(nm)
    return names


def _run(name, fn, q, page, n):
    if not POOL.HEALTH.available("web:" + name):
        return name, None
    try:
        items = [i for i in fn(q, page, n) if i]
        POOL.HEALTH.ok("web:" + name)
        return name, items
    except KeyError:
        return name, None                                   # not configured
    except Exception as e:
        POOL.HEALTH.fail("web:" + name, POOL.classify(f"{e.__class__.__name__} {getattr(e, 'code', '')}"))
        return name, None


def search(query, page=1, per_source=8):
    """{'items': [...], 'sources': {name: count or None}, 'blocked': bool, 'cached': bool}. Sources are queried in parallel; results are interleaved so every source
    contributes, de-duplicated by picture address."""
    q = re.sub(r"\s+", " ", str(query or "")).strip()[:80]
    page = max(1, min(int(page or 1), 20))
    if len(q) < 2:
        return {"items": [], "sources": {}, "blocked": False, "cached": False}
    if _BLOCK.search(q):
        return {"items": [], "sources": {}, "blocked": True, "cached": False}
    key = POOL.Cache.key("web", q.lower(), page, per_source, ",".join(configured()))
    hit = CACHE.get(key)
    if hit:
        return dict(hit, cached=True)
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as ex:
        res = list(ex.map(lambda s: _run(s[0], s[1], q, page, per_source), SOURCES))
    lists = [(nm, items or []) for nm, items in res]
    seen, items = set(), []
    for i in range(per_source):
        for nm, lst in lists:
            if i < len(lst) and lst[i]["thumb"] not in seen:
                seen.add(lst[i]["thumb"]); items.append(lst[i])
    out = {"items": items, "sources": {nm: (len(items_) if items_ is not None else None) for nm, items_ in res}, "blocked": False, "cached": False}
    if items:
        CACHE.put(key, out, 400 * len(items) + 200)
    return out


def photos(term, n=5):
    """Older shape for the chat: up to n {caption, url, license, page}; never raises."""
    try:
        r = search(term, 1, max(4, n))
        return [{"caption": (i["title"] + (" · " + i["creator"] if i["creator"] else ""))[:90], "url": i["thumb"], "license": i["license"], "page": i["page"]} for i in r["items"][:n]]
    except Exception:
        return []


def credit(i):
    bits = [i["title"]] + ([i["creator"]] if i.get("creator") else []) + ([i["license"]] if i.get("license") else []) + [i["source"]]
    return " · ".join(b for b in bits if b)


NOTE = {"en": "Photos are searched in several licensed image sources at once. Each shows its creator and licence; open the source page before reusing a photo, and check that its licence allows your use.",
        "fr": "Les photos sont cherchées dans plusieurs sources d'images sous licence à la fois. Chacune indique son auteur et sa licence ; ouvrez la page source avant de réutiliser une photo et vérifiez que la licence permet votre usage.",
        "rw": "Amafoto arashakishwa mu mbuga nyinshi z'amashusho zifite uruhushya icyarimwe. Buri foto yerekana uwayikoze n'uruhushya; fungura urupapuro rwayo mbere yo kuyongera gukoresha kandi urebe ko uruhushya rwemera icyo ushaka.",
        "sw": "Picha zinatafutwa kwenye vyanzo kadhaa vya picha zenye leseni kwa wakati mmoja. Kila moja inaonyesha mmiliki na leseni; fungua ukurasa wa chanzo kabla ya kutumia tena na hakikisha leseni inaruhusu matumizi yako."}
BLOCKED = {"en": "I do not search for that kind of content.", "fr": "Je ne recherche pas ce type de contenu.", "rw": "Sishakisha ibyo bikubiye.", "sw": "Situmii utafutaji wa maudhui ya aina hiyo."}
