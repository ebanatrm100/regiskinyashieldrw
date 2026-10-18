"""Routing for the AI Assistant tab. Pure Python (no Streamlit) so it can be tested.

Order of attempts for each question:
  1. Does it look like a suspicious message the user pasted?  -> the existing scam detector (unchanged).
  1b. Is the whole message a greeting (hello, mwaramutse, bonjour, jambo, thank you ...)? -> a correct reply + explanation in four languages (greetings_db.py).
  2. Is it a question about the meaning of a known name?      -> name meaning (names_db.py, a curated list, not every name).
  2b. Is it just "what is X" for a listed term?                -> short definition (definitions_db.py, a curated bank, not every word).
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

try:
    from owner_db import find as _find_owner
except Exception:  # the owner answer is optional
    _find_owner = None

try:
    from greetings_db import find as _find_greeting
except Exception:  # the greetings feature is optional
    _find_greeting = None

try:
    from definitions_db import find as _find_definition
except Exception:  # the definitions feature is optional
    _find_definition = None

try:
    from computers_db import find as _find_computer
except Exception:  # the computers feature is optional
    _find_computer = None

try:
    from phones_db import find as _find_phone
except Exception:  # the phone-brands feature is optional
    _find_phone = None

try:
    from physics_db import find as _find_physics
except Exception:  # the physics-formulas feature is optional
    _find_physics = None

try:
    from scams_db import find as _find_scam
except Exception:  # the scam-methods catalogue is optional
    _find_scam = None

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
    if not entry["steps"][k]:  # a plain answer with no steps (for example the owner answer)
        return f"**{entry['title'][k]}**\n\n{entry['answer'][k]}"
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
    if not force_ai and _find_owner is not None:
        owner = _find_owner(q, k)
        if owner is not None:
            return {"kind": "guide", "entry": owner}
    if not force_ai and _find_greeting is not None:
        greeted = _find_greeting(q, k)
        if greeted is not None:
            return {"kind": "guide", "entry": greeted}
    if not force_ai and _find_name is not None:
        named = _find_name(q, k)
        if named is not None:
            return {"kind": "guide", "entry": named}
    if not force_ai and _find_definition is not None:
        defined = _find_definition(q, k)
        if defined is not None:
            return {"kind": "guide", "entry": defined}
    if not force_ai:
        entry = best(q, k)
        comp = _find_computer(q, k) if _find_computer is not None else None
        phone = _find_phone(q, k) if _find_phone is not None else None
        scam = _find_scam(q, k) if _find_scam is not None else None
        # Physics formulas: a question that names a formula (or asks for the formulas of a topic) is answered here before the general guide.
        physics = _find_physics(q, k) if _find_physics is not None else None
        if physics is not None:
            return {"kind": "guide", "entry": physics}
        # "Methods of scams": a list question is answered here; a single method needs a short question or no better guide answer.
        if scam is not None and (scam["kind"] == "scam_list" or entry is None or len(q.split()) <= 4):
            return {"kind": "guide", "entry": scam}
        # Phone brands / "list of phone brands": a list question is answered here; a single brand needs a short question or no better guide answer.
        if phone is not None and (phone["kind"] == "phone_list" or entry is None or len(q.split()) <= 4):
            return {"kind": "guide", "entry": phone}
        # A long question that the cyber/general guide also answers (e.g. "what do I do if my phone is stolen") stays with the guide.
        if comp is not None and (entry is None or len(q.split()) <= 4):
            return {"kind": "guide", "entry": comp}
        if entry is not None:
            return {"kind": "guide", "entry": entry}
    return {"kind": "ai"}
