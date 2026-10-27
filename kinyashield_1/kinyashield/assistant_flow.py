"""Routing for the AI Assistant tab. Pure Python (no Streamlit) so it can be tested.

Order of attempts for each question:
  1. Does it look like a suspicious message the user pasted?  -> the existing scam detector (unchanged).
  1b. Is the whole message a greeting (hello, mwaramutse, bonjour, jambo, thank you ...)? -> a correct reply + explanation in four languages (greetings_db.py).
  2. Is it a question about the meaning of a known name?      -> name meaning (names_db.py, a curated list, not every name).
  2b. Is it just "what is X" for a listed term?                -> short definition (definitions_db.py, a curated bank, not every word).
  2c. Privacy/trust answers, worked maths, phrasebook, writing templates (trust_db, tutor_db, translate_db, writing_db).
  3. Does the offline guide have a reliable answer?           -> guide answer with steps and related questions.
  4. Otherwise                                                  -> caller sends it to the AI (Gemini) if configured.
The scam detector, rules and Check tab are not modified by this module."""
from __future__ import annotations
import re
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

def _optional(module, name="find"):
    """Import a feature module's finder; the feature simply switches off if the module is missing or broken."""
    try:
        return getattr(__import__(module, fromlist=[name]), name)
    except Exception:
        return None


_find_tutor = _optional("tutor_db")        # worked maths solutions + pointer to the practice quiz
_find_translate = _optional("translate_db")  # phrasebook: "how do you say X in Kinyarwanda"
_parse_translation_full = _optional("meta_guard", "parse_translation_full")  # (phrase, source, target)
_parse_translation = _optional("meta_guard", "parse_translation")  # "Translate X into Kinyarwanda": X is material to translate, not a question to answer
_is_wrapper = _optional("meta_guard", "is_wrapper")                # "Repeat / rewrite / correct: X"
_find_cyber = _optional("cyber_db")  # cybersecurity terms (meaning, applications, photos)
_find_cyber_compare = _optional("cyber_compare")  # "difference between X and Y" / "X vs Y" for two glossary terms
_find_clarify = _optional("intent", "clarify")  # too-vague opener ("help", "I have a problem") -> ask what is needed, with choices
_find_trust = _optional("trust_db")        # privacy, limits, source policy, where to verify
_find_ai_lab = _optional("ai_lab")        # AI-guide demos: token counter, attention, next word, loss, gradient, chmod, strict calculator
_find_image_lab = _optional("image_lab")       # image-prompt tools (improve/score/thirds/ratio/latent/denoise), four languages
_find_image_guide = _optional("image_guide_db")  # AI image generation guide (process, techniques, prompts, composition, fixes), four languages
_find_research_lab = _optional("research_lab")       # interpret / research plan / rag demo tools, four languages
_find_cyber_playbook = _optional("cyber_playbook_db")  # overview guides: hacker methods, attack families, how engineers protect systems, scam prevention, after a scam, careers
_find_research_guide = _optional("research_guide_db")  # how an AI interprets, researches (RAG, tools) and composes answers, four languages
_find_ink = _optional("inkoranyamagambo")      # owner-supplied Kinyarwanda dictionary (461 words with Kinyarwanda meanings)
_find_ai_guide = _optional("ai_guide_db")  # how AI assistants work (from the AI Technical Guide), four languages
_find_writing = _optional("writing_db")    # templates: emails, CVs, applications, reports, proposals, messages

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


def _attach_photo_query(entry):
    """A scam method that is also a glossary term gets that term's photo subject, so it still shows up to five photos."""
    try:
        import cyber_db
        row = cyber_db.lookup(entry["title"]["en"])
        if row is not None and not entry.get("photo_query"):
            entry["photo_query"] = row[4]
    except Exception:
        pass


def route(question, lang, force_ai=False):
    """Return {'kind': 'scam'|'guide'|'ai', ...}. Never raises for ordinary text."""
    q = (question or "").strip()
    k = _lk(lang)
    if not force_ai and len(q) >= MIN_MESSAGE_LEN:
        res = analyze(q)
        if res.verdict != "ok":
            return {"kind": "scam", "result": res, "steps": next_steps(res, k)}
    if not force_ai and _parse_translation is not None:
        _src = ""
        tr = None
        try:
            _full = _parse_translation_full(q) if _parse_translation_full is not None else None
            if _full is not None:
                tr, _src = (_full[0], _full[2]), _full[1]
            else:
                tr = _parse_translation(q)
        except Exception:
            tr = None
        if tr is not None:
            hit = None
            try:  # curated bank first: exact, hand-written translations between the four languages
                import translate_db as _td
                _target = tr[1] or {"en": "rw", "rw": "en", "fr": "en", "sw": "en"}[k]
                _res = _td.translate(tr[0], _target, k, _src or None)
                if _res is not None:
                    hit = _td.render(_res, k)
            except Exception:
                hit = None
            if hit is None and _find_translate is not None and not _src:
                try:
                    hit = _find_translate(q, k)
                except Exception:
                    hit = None
            if hit is not None:
                return {"kind": "guide", "entry": hit}
            return {"kind": "translate", "phrase": tr[0], "target": tr[1], "source": _src}
    if not force_ai and _is_wrapper is not None:
        try:
            if _is_wrapper(q):
                return {"kind": "ai"}   # the quoted sentence is material to work on, never a question for the offline finders
        except Exception:
            pass
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
    for _finder in ((_find_ai_lab, _find_image_lab, _find_research_lab, _find_research_guide, _find_ai_guide, _find_image_guide, _find_cyber_playbook) if not force_ai else ()):   # AI-guide demos (strict commands) and "how does an AI assistant work" topics
        if _finder is None:
            continue
        try:
            _hit = _finder(q, k)
        except Exception:
            _hit = None
        if _hit is not None:
            return {"kind": "guide", "entry": _hit}
    if not force_ai and _find_cyber is not None:   # "list all cybersecurity terms" / "malware terms": the glossary lists (unless the question is about scam METHODS)
        try:
            cyber_list = _find_cyber(q, k)
        except Exception:
            cyber_list = None
        if cyber_list is not None and cyber_list["kind"] == "cyber_list" and not re.search(
                r"scam|fraud|arnaque|uburiganya|ubutekamutwe|ulaghai|tapeli|method|methode|méthode|uburyo|mbinu|ways|techniques", q, re.I):
            return {"kind": "guide", "entry": cyber_list}
    if not force_ai and _find_cyber_compare is not None:   # "difference between a virus and a worm", "red team vs blue team"
        try:
            _cmp = _find_cyber_compare(q, k)
        except Exception:
            _cmp = None
        if _cmp is not None:
            return {"kind": "guide", "entry": _cmp}
    if not force_ai and _find_scam is not None:    # the scam-methods catalogue (list, or one method by a short question) is richer than the glossary: description, example, protection
        try:
            scam0 = _find_scam(q, k)
        except Exception:
            scam0 = None
        if scam0 is not None and (scam0["kind"] == "scam_list" or len(q.split()) <= 4):
            _attach_photo_query(scam0)
            return {"kind": "guide", "entry": scam0}
    if not force_ai and _find_cyber is not None:   # cybersecurity glossary: meaning, applications and photos for a security term
        try:
            cyber = _find_cyber(q, k)
        except Exception:
            cyber = None
        if cyber is not None:
            return {"kind": "guide", "entry": cyber}
    if not force_ai and _find_clarify is not None:
        try:
            asked = _find_clarify(q, k)
        except Exception:
            asked = None
        if asked is not None:
            return {"kind": "guide", "entry": asked}
    if not force_ai:
        for _finder in (_find_trust, _find_tutor, _find_translate, _find_writing):
            if _finder is None:
                continue
            try:
                hit = _finder(q, k)
            except Exception:  # one broken feature must never break the chat
                hit = None
            if hit is not None:
                return {"kind": "guide", "entry": hit}
    if not force_ai and _find_definition is not None:
        defined = _find_definition(q, k)
        if defined is not None:
            return {"kind": "guide", "entry": defined}
    if not force_ai and _find_ink is not None:   # "umuntu ni iki?", "igisobanuro cya umwana": the owner's dictionary, when the word is in it
        try:
            _ink = _find_ink(q, k, True)
        except Exception:
            _ink = None
        if _ink is not None:
            return {"kind": "guide", "entry": _ink}
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
        if scam is not None and (scam["kind"] == "scam_list" or entry is None or len(q.split()) <= 4 or (scam["kind"] == "scam_method" and entry.get("id") == "phishing_basics")):
            return {"kind": "guide", "entry": scam}
        # Phone brands / "list of phone brands": a list question is answered here; a single brand needs a short question or no better guide answer.
        if phone is not None and (phone["kind"] == "phone_list" or entry is None or len(q.split()) <= 4):
            return {"kind": "guide", "entry": phone}
        # A long question that the cyber/general guide also answers (e.g. "what do I do if my phone is stolen") stays with the guide.
        if comp is not None and (entry is None or len(q.split()) <= 4):
            return {"kind": "guide", "entry": comp}
        if entry is not None:
            return {"kind": "guide", "entry": entry}
    if not force_ai and _find_ink is not None:   # a bare dictionary word in the Kinyarwanda interface
        try:
            _ink = _find_ink(q, k, False)
        except Exception:
            _ink = None
        if _ink is not None:
            return {"kind": "guide", "entry": _ink}
    return {"kind": "ai"}
