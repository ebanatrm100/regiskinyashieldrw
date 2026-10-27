"""Security playbooks for the AI Assistant (offline, four languages): what ATTACKERS do, what security ENGINEERS do to protect systems, and how ordinary people
PREVENT scams. Each topic is a guide-shaped entry (title, short intro, numbered points) found by keyword phrases in en/fr/rw/sw.
Data: playbook_attacks.py, playbook_defense.py, playbook_scams.py. Text is protective and educational (recognise, resist, defend); it contains no instructions for
carrying out attacks. fr/rw/sw wording is a draft for review by fluent speakers.

Row format used by the data files:
  P(id, keywords, title, intro, items, label, related)
  keywords = (en, fr, rw, sw): each a "|"-separated string of phrases; title/intro/label = (en, fr, rw, sw); items = [(en, fr, rw, sw), ...]"""
from __future__ import annotations
import importlib
from textutil import fold, has_phrase, entry, LANGS

PLAYBOOKS = []


def P(id_, kw, title, intro, items, label, related=()):
    return {"id": id_, "kw": {l: [fold(k) for k in kw[i].split("|") if k.strip()] for i, l in enumerate(LANGS)}, "title": dict(zip(LANGS, title)),
            "intro": dict(zip(LANGS, intro)), "items": [dict(zip(LANGS, it)) for it in items], "label": dict(zip(LANGS, label)), "related": list(related)}


for _m in ("playbook_attacks", "playbook_attacks2", "playbook_defense", "playbook_defense2", "playbook_scams", "playbook_scams2"):
    try:
        PLAYBOOKS += list(importlib.import_module(_m).build(P))
    except Exception:   # a missing or broken data file only switches that part off
        pass
BY_ID = {p["id"]: p for p in PLAYBOOKS}


def _to_entry(p):
    e = entry("pb_" + p["id"], "playbook", p["title"], p["intro"], {l: [it[l] for it in p["items"]] for l in LANGS}, p["label"], p["related"])
    e["priority"] = True
    return e


def count():
    return len(PLAYBOOKS)


_STOP = set("the a an and or of to in on for is are was were do does did how what when where why who which can could i my me we you your it its this that these those with from at by as be all list give show tell about please les des une un du de la le et ou est sont que qui quoi comment pourquoi quand mon ma mes au aux en dans pour par sur avec ce ces cette nous vous je tu il elle ni ari mu ku kuri na se cyangwa kandi ya wa za cya bya bwa rwa rya ry uko iki ikihe nini lini wapi vipi gani yangu wangu zangu langu kwa za la".split())


def _stem(w):
    return w[:-1] if len(w) > 4 and w.endswith("s") else w


def _toks(text):
    return {_stem(w) for w in text.replace("'", " ").split() if len(w) > 2 and w not in _STOP}


def find(question, lang="en"):
    """The playbook whose keyword phrase best matches the question: an exact phrase first (longest wins), else a tolerant word-overlap match."""
    q = fold(question or "")
    if not q or len(q) > 400:
        return None
    best, best_len = None, 0
    for p in PLAYBOOKS:
        for l in LANGS:
            for kw in p["kw"][l]:
                if len(kw) > best_len and has_phrase(q, [kw]):
                    best, best_len = p, len(kw)
    if best:
        return _to_entry(best)
    qt = _toks(q)
    if len(qt) < 2:
        return None
    top, top_score = None, 0.0
    for p in PLAYBOOKS:
        for l in LANGS:
            for kw in p["kw"][l]:
                kt = _toks(kw)
                if len(kt) < 2:
                    continue
                hit = len(kt & qt)
                if hit >= 2 and hit / len(kt) >= 0.75 and hit > top_score:
                    top, top_score = p, hit + hit / len(kt)
    return _to_entry(top) if top else None
