"""Routing for the AI Assistant tab. Pure Python (no Streamlit) so it can be tested.

Order of attempts for each question:
  1. Does it look like a suspicious message the user pasted?  -> the existing scam detector (unchanged).
  2. Is it a question about the meaning of a known name?      -> name meaning (names_db.py, a curated list, not every name).
  3. Does the offline guide have a reliable answer?           -> guide answer with steps and related questions.
  4. Otherwise                                                  -> caller sends it to the AI (Gemini) if configured.
The scam detector, rules and Check tab are not modified by this module."""
from __future__ import annotations
from detector import analyze, next_steps
from guide_search import best, BY_ID
try:
    from names_db import find as _find_name
except Exception:  # the name-meaning feature is optional; everything else keeps working
    _find_name = None

LANGS = ("en", "fr", "rw", "sw")
SUGGESTED = ["shared_pin", "verify_sender", "strong_passwords", "lost_phone", "post_harvest_fresh", "write_cv"]
MIN_MESSAGE_LEN = 50


def _lk(lang):
    lang = str(lang).lower()
    return lang if lang in LANGS else "en"


def suggested(lang):
    k = _lk(lang)
    return [(i, BY_ID[i]["title"][k]) for i in SUGGESTED if i in BY_ID]


def related(entry, lang):
    k = _lk(lang)
    return [(r, BY_ID[r]["title"][k]) for r in entry.get("related", []) if r in BY_ID]


def format_guide(entry, lang, steps_label, source_label):
    k = _lk(lang)
    steps_label = (entry.get("steps_label") or {}).get(k, steps_label)
    lines = [f"**{entry['title'][k]}**", "", entry["answer"][k], "", f"*{steps_label}*"]
    lines += [f"{n}. {s}" for n, s in enumerate(entry["steps"][k], 1)]
    lines += ["", f"_{source_label}_"]
    return "\n".join(lines)


def route(question, lang, force_ai=False):
    """Return {'kind': 'scam'|'guide'|'ai', ...}. Never raises for ordinary text."""
    q = (question or "").strip()
    k = _lk(lang)
    if not force_ai and len(q) >= MIN_MESSAGE_LEN:
        res = analyze(q)
        if res.verdict != "ok":
            return {"kind": "scam", "result": res, "steps": next_steps(res, k)}
    if not force_ai and _find_name is not None:
        named = _find_name(q, k)
        if named is not None:
            return {"kind": "guide", "entry": named}
    if not force_ai:
        entry = best(q, k)
        if entry is not None:
            return {"kind": "guide", "entry": entry}
    return {"kind": "ai"}
