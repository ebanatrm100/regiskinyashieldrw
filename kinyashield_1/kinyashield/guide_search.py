# Offline keyword search over knowledge_base.ENTRIES. Says "no answer" instead of guessing.
import re, unicodedata
from knowledge_base import ENTRIES, BY_ID

def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'.\- ]+", " ", s)).strip()

_cache = {}
def _rx(kw):
    if kw not in _cache:
        star = kw.endswith("*")
        _cache[kw] = re.compile("(^| )" + re.escape(kw.rstrip("*")) + ("[a-z0-9']*" if star else "") + "(?= |$)")
    return _cache[kw]

def search(query, lang="en"):
    q = fold(query); out = []
    if len(q) < 2:
        return out
    for e in ENTRIES:
        score = 0.0
        for l, kws in e["keywords"].items():
            w = 1.25 if l == lang else 1.0
            for kw in kws:
                if _rx(kw).search(q):
                    score += 2 * len(kw.rstrip("*").split(" ")) * w
        if score > 0:
            out.append((score, e))
    out.sort(key=lambda x: -x[0])
    return out

def best(query, lang="en"):
    r = search(query, lang)
    return r[0][1] if r and r[0][0] >= 2 else None
