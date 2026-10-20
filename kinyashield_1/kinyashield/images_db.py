"""Up to five real photographs for any keyword, from Wikimedia Commons (free-licence photos with their own pages and credits).
Never invents or draws anything: if Commons has no suitable photo, fewer (or none) are shown and the text answer stands alone.
Needs internet; every failure returns []. Photos can illustrate a topic loosely, so each one shows its Commons title and licence."""
from __future__ import annotations
import html
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://commons.wikimedia.org/w/api.php"
PAGE = "https://commons.wikimedia.org/wiki/"
UA = "KinyaShieldRW/1.0 (https://regiskinyashieldrw.streamlit.app; educational safety assistant)"
TIMEOUT = 6
MIN_WIDTH = 480
# Titles that are almost never a useful photo of the thing itself.
SKIP = ("logo", "icon", "screenshot", "wordmark", "diagram", "chart", "graph", "map of", "flag of", "coat of arms", "poster", "banner", "cover", "stamp", "signature",
        "infographic", "illustration", "drawing", "clipart", "vector", "scan of", "page ", "manuscript", "sticker", "meme", "advert", "ad ", "qr code", "cropped")
# Photos of private people are never searched for.
_cache: dict = {}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 (fixed https host)
        return json.loads(r.read().decode("utf-8", "replace"))


def _url(query, limit=24):
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": limit, "gsrsearch": query + " filetype:bitmap",
         "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 480}
    return API + "?" + urllib.parse.urlencode(p)


def _text(v):
    return html.unescape(re.sub(r"<[^>]+>", "", str(v or ""))).strip()


def pick(data, term, n=5):
    """From a Commons API result choose up to n different JPEG/PNG photos that look like real photographs of the term."""
    pages = list(((data or {}).get("query") or {}).get("pages", {}).values())
    pages.sort(key=lambda p: p.get("index", 999))
    t = re.sub(r"[^a-z0-9 ]", "", term.lower()).split()
    scored, seen, counts = [], set(), {}
    for p in pages:
        title = str(p.get("title", ""))
        low = title.lower()
        info = (p.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or ""
        if info.get("mime") not in ("image/jpeg", "image/png") or not url.startswith("https://upload.wikimedia.org/"):
            continue
        if (info.get("width") or 0) < MIN_WIDTH or any(w in low for w in SKIP):
            continue
        name = re.sub(r"\.(jpe?g|png)$", "", title.replace("File:", "", 1), flags=re.I)
        key = re.sub(r"[\d_\W]+", "", name.lower())[:24]
        if name.lower() in seen or counts.get(key, 0) >= 2:   # the same file twice, or a long numbered series of one subject: keep the variety
            continue
        seen.add(name.lower())
        counts[key] = counts.get(key, 0) + 1
        meta = info.get("extmetadata") or {}
        lic = _text((meta.get("LicenseShortName") or {}).get("value"))
        hit = sum(1 for w in t if w in low)           # the title mentions the term: more likely to show the thing itself
        scored.append((-hit, p.get("index", 999), {"caption": name.replace("_", " ")[:90], "url": url, "license": lic,
                                                      "page": PAGE + urllib.parse.quote(title.replace(" ", "_"), safe=":_")}))
    scored.sort(key=lambda s: (s[0], s[1]))
    return [s[2] for s in scored[:n]]


def photos(term, n=5):
    """Up to n photos for the keyword. Never raises; cached per process (failures too)."""
    term = (term or "").strip()
    if not term or len(term) > 60:
        return []
    key = (term.lower(), n)
    if key in _cache:
        return _cache[key]
    out = []
    try:
        out = pick(_get(_url(term)), term, n)
        if len(out) < n and " " in term:                   # a long phrase found too little: try its last (most specific) word too
            more = pick(_get(_url(term.split()[-1])), term.split()[-1], n)
            have = {o["url"] for o in out}
            out += [m for m in more if m["url"] not in have][: n - len(out)]
    except Exception:
        out = out or []
    _cache[key] = out
    return out


def photos_parallel(terms, n=5):
    """photos() for several terms at once; returns {term: [...]}."""
    with ThreadPoolExecutor(max_workers=min(6, max(1, len(terms)))) as ex:
        return dict(zip(terms, ex.map(lambda t: photos(t, n), terms)))


NOTE = {"en": "Photos from Wikimedia Commons (free licences). They illustrate the topic and may be only loosely related; tap a link to see the credit.",
        "fr": "Photos de Wikimedia Commons (licences libres). Elles illustrent le sujet et peuvent n'être que vaguement liées ; touchez un lien pour voir le crédit.",
        "rw": "Amafoto aturuka kuri Wikimedia Commons (uburenganzira bwemewe). Agaragaza isomo ariko ashobora kutaryerekeyeho neza; kanda link urebe nyirayo.",
        "sw": "Picha kutoka Wikimedia Commons (leseni huru). Zinaonyesha mada lakini zinaweza kuhusiana kwa mbali tu; bonyeza kiungo kuona mmiliki."}
NONE = {"en": "No suitable free photo was found for this word.", "fr": "Aucune photo libre adaptée n'a été trouvée pour ce mot.",
        "rw": "Nta foto ikwiye yabonetse kuri iri jambo.", "sw": "Hakuna picha huru inayofaa iliyopatikana kwa neno hili."}


def note(lang="en"):
    return NOTE.get(lang, NOTE["en"])


def none_note(lang="en"):
    return NONE.get(lang, NONE["en"])
