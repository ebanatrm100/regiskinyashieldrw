# Offline keyword search over knowledge_base.ENTRIES. Says "no answer" instead of guessing.
import re, unicodedata
from knowledge_base import ENTRIES, BY_ID

def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'.\- ]+", " ", s)).strip()

_STOP = set("the a an and or of to in on for is are was were do does did how what when where why who which can could should would i my me we you your it its this that these those with from at by as be been am not no et ou de du des la le les un une est sont que qui quoi comment pourquoi quand ou mon ma mes ton ta tes au aux en dans pour par sur avec sans ce ces cette nous vous je tu il elle nke nte ni ari mu ku kuri na se cyangwa kandi ya wa za cya bya bwa rwa rya ry uko iki ikihe ubwo yanjye wanjye zanjye ni ndi nta ya la za wa kwa na au ni ya wa la za je nini lini wapi vipi gani yangu wangu zangu langu".split())
_TITLE_TOKENS = {}


def _toks(text):
    return [w for w in fold(text).replace("'", " ").split() if len(w) > 2 and w not in _STOP]


def _title_index():
    if not _TITLE_TOKENS:
        for e in ENTRIES:
            for l, t in e["title"].items():
                _TITLE_TOKENS[(e["id"], l)] = (fold(t).rstrip(" ?.!"), _toks(t))
    return _TITLE_TOKENS


def _title_score(e, q, qtoks):
    """Strong score when the question is the entry's title (any language) or contains most of its key words."""
    best = 0.0
    qs = q.rstrip(" ?.!")
    idx = _title_index()
    for l in e["title"]:
        full, toks = idx[(e["id"], l)]
        if full and (qs == full or full in qs):
            return 60.0
        if len(toks) >= 3:
            hit = sum(1 for t in toks if t in qtoks)
            if hit >= 3 and hit / len(toks) >= 0.75:
                best = max(best, 14.0 * hit / len(toks))
    return best


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
        # Score each language on its own and keep the best, so a word that exists in all four languages is not counted four times.
        for l, kws in e["keywords"].items():
            w = 1.25 if l == lang else 1.0
            sub = 0.0
            for kw in kws:
                if _rx(kw).search(q):
                    sub += 2 * len(kw.rstrip("*").split(" ")) * w
            score = max(score, sub)
        score = max(score, _title_score(e, q, set(_toks(q))))
        if score > 0:
            out.append((score, e))
    out.sort(key=lambda x: -x[0])
    return out

def best(query, lang="en"):
    r = search(query, lang)
    return r[0][1] if r and r[0][0] >= 2 else None
