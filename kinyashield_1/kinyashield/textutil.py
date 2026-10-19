"""Small shared helpers for the assistant modules (pure Python, no Streamlit)."""
from __future__ import annotations
import re, unicodedata

LANGS = ("en", "fr", "rw", "sw")


def fold(s):
    """Lower-case, accent-free, punctuation-light text used for matching."""
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\-+*/=^%.,:@() ]+", " ", s)).strip()


def words(s):
    return [w for w in re.split(r"[^a-z0-9]+", fold(s)) if w]


def has_phrase(text, phrases):
    """True if any phrase occurs in the (already folded) text as whole words."""
    for p in phrases:
        if re.search(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", text):
            return True
    return False


def lk(lang):
    lang = str(lang).lower()
    return lang if lang in LANGS else "en"


def entry(id_, kind, title, answer, steps=None, steps_label=None, related=None):
    """Build a guide-shaped entry (what assistant_flow.format_guide expects). Each argument is {lang: text}."""
    steps = steps or {l: [] for l in LANGS}
    steps_label = steps_label or {l: "" for l in LANGS}
    return {"id": id_, "kind": kind, "title": title, "answer": answer, "steps": steps, "steps_label": steps_label, "related": related or []}
