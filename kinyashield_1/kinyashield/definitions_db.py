"""Definitions for the AI Assistant (offline). Pure Python, no Streamlit.

A curated bank of short definitions (language, computing, science, maths, society, economy, health, farming) in en / fr / rw / sw.
It is NOT every word or every definition: a question is answered here only when, after removing question words ("what is", "define",
"ni iki", "qu'est-ce que", "maana ya" ...), what remains is exactly a listed term. So "what is English" is answered, while longer
questions ("how do I improve my English") stay with the guide, and unknown terms go on to the AI. fr / rw / sw wording is a draft
for review by fluent speakers; health definitions carry a "not medical advice" note."""
from __future__ import annotations
import re
from names_db import fold as _fold


def fold(s):
    """names_db.fold, plus apostrophes and hyphens become spaces (c'est -> c est, Wi-Fi -> wi fi)."""
    return re.sub(r"\s+", " ", _fold(s).replace("'", " ").replace("-", " ")).strip()

LANGS = ("en", "fr", "rw", "sw")
_SEP = " ~ "

# words that only form the question, in all four languages (after names_db.fold: lower case, no accents, punctuation -> space)
_STOP = set("""what whats is are a an the define definition definitions of meaning mean means does do did please explain tell me about
who s meant by short brief simple give i want to know understand
qu est ce que quoi c le la les l un une des du de d signifie veut dire definis definir definition sens quel quelle
ni iki ibisobanuro bya risobanura isobanura bisobanura bisobanuro icyo uburyo busobanura ushaka kumenya nde ese
maana ya za nini eleza tafadhali ina maanisha nin""".split())

_DISCLAIMER = {
    "en": "This is a short definition. Ask a follow-up question if you want more detail or examples.",
    "fr": "Ceci est une définition courte. Posez une autre question pour plus de détails ou d'exemples.",
    "rw": "Iki ni igisobanuro kigufi. Baza ikindi kibazo niba ushaka ibisobanuro birambuye cyangwa ingero.",
    "sw": "Huu ni ufafanuzi mfupi. Uliza swali la ziada ukitaka maelezo zaidi au mifano.",
}
_HEALTH = {
    "en": "General information only, not medical advice. For symptoms or treatment, see a health worker or doctor.",
    "fr": "Information générale uniquement, pas un avis médical. Pour des symptômes ou un traitement, consultez un professionnel de santé.",
    "rw": "Ni amakuru rusange gusa, si inama za muganga. Ku bimenyetso cyangwa kuvurwa, genda ku muganga cyangwa ku kigo nderabuzima.",
    "sw": "Ni taarifa za jumla tu, si ushauri wa kitabibu. Kwa dalili au matibabu, muone mhudumu wa afya au daktari.",
}
_LABEL = {"en": "Note", "fr": "Note", "rw": "Icyitonderwa", "sw": "Kumbuka"}


def _load():
    from importlib import import_module
    rows = []
    for mod in ("defs_language", "defs_computing", "defs_science", "defs_society", "defs_health_farm"):
        try:
            text = import_module(mod).ROWS
        except Exception:  # a missing or broken file must never break the assistant
            continue
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            f = line.split(_SEP)
            if len(f) != 7:
                continue
            cat, titles, aliases, en, fr, rw, sw = (x.strip() for x in f)
            t = [x.strip() for x in titles.split(" / ")]
            if len(t) != 4:
                continue
            rows.append({"cat": cat, "titles": dict(zip(LANGS, t)), "aliases": [a.strip() for a in aliases.split(",") if a.strip()],
                         "defs": dict(zip(LANGS, (en, fr, rw, sw)))})
    return rows


ROWS = _load()


def _key(tokens):
    return tuple(t for t in tokens if t not in _STOP)


def _variants(key):
    """The key plus a simple plural/singular variant of its last word (computers <-> computer)."""
    yield key
    if key:
        last = key[-1]
        if len(last) > 3 and last.endswith("s"):
            yield key[:-1] + (last[:-1],)
        elif len(last) > 2:
            yield key[:-1] + (last + "s",)


def _build_index():
    idx = {}
    for i, r in enumerate(ROWS):
        names = list(r["aliases"]) + list(r["titles"].values())
        for n in names:
            # titles carry a bracketed hint such as "Inyuguti (alphabet)": index both the full form and the bracket-free form
            for form in {n, re.sub(r"\([^)]*\)", " ", n)}:
                key = _key(fold(form).split())
                if key:
                    for v in _variants(key):
                        idx.setdefault(v, i)
    return idx


_INDEX = _build_index()


def count():
    return len(ROWS)


def _entry(i):
    r = ROWS[i]
    note = _HEALTH if r["cat"] == "h" else _DISCLAIMER
    slug = re.sub(r"[^a-z0-9]+", "_", fold(r["titles"]["en"]).strip()).strip("_")
    return {
        "id": "def_" + slug,
        "title": dict(r["titles"]),
        "answer": dict(r["defs"]),
        "steps": {k: [note[k]] for k in LANGS},
        "steps_label": dict(_LABEL),
        "related": [],
    }


def find(question, lang="en"):
    """Return a guide-shaped entry when the question is just a request to define a listed term, else None."""
    q = (question or "").strip()
    if not q or len(q) > 90:
        return None
    toks = fold(q).split()
    if not toks or len(toks) > 9:
        return None
    key = _key(toks)
    if not key or len(key) > 5:
        return None
    for v in _variants(key):
        i = _INDEX.get(v)
        if i is not None:
            return _entry(i)
    return None
