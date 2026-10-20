"""Messages that QUOTE or WRAP another sentence ("Translate who owns you into Kinyarwanda", "Repeat: my password is ...",
"Correct the grammar of: who is your owner") must be treated as a task about that sentence, not answered as if the quoted
sentence had been asked directly. This module detects such wrappers so identity, greeting, name and definition finders do not hijack them.
Pure Python, four languages."""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
from textutil import fold

LANG_WORDS = {
    "rw": ["kinyarwanda", "ikinyarwanda", "kinyarwandaa"],
    "fr": ["french", "francais", "français", "igifaransa", "kifaransa"],
    "sw": ["swahili", "kiswahili", "igiswahili"],
    "en": ["english", "anglais", "icyongereza", "kiingereza", "englishi"],
}
_LANG_ALT = "|".join(sorted((w for ws in LANG_WORDS.values() for w in ws), key=len, reverse=True))
_Q = "[\"“”'«»]?"

_TRANSLATE = [
    rf"^\s*(?:please\s+)?translate\s+(?:the\s+)?(?:(?:phrase|sentence|word|words|text|question)\s+)?{_Q}(?P<p>.+?){_Q}\s+(?:in)?to\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:please\s+)?translate\s+(?:the\s+)?(?:(?:phrase|sentence|word|words|text|question)\s+)?(?:in(?:to)?\s+(?P<l>{_LANG_ALT})\s*[:\-]?\s*)?{_Q}(?P<p>.+?){_Q}\s*$",
    rf"^\s*how\s+(?:do|would|can|should)\s+(?:you|i|we)\s+say\s+{_Q}(?P<p>.+?){_Q}\s+in\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:what\s+is|what's)\s+{_Q}(?P<p>.+?){_Q}\s+in\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*traduis(?:ez)?(?:-moi)?\s+{_Q}(?P<p>.+?){_Q}\s+(?:en|vers)\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*comment\s+(?:dit|dire|on dit)(?:-on)?\s+{_Q}(?P<p>.+?){_Q}\s+en\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:hindura|humura|vuga)\s+{_Q}(?P<p>.+?){_Q}\s+mu\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:{_Q}(?P<p>.+?){_Q})\s+(?:bivuga gute|byumvikana gute|bihinduka gute)\s+mu\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:tafsiri|nitafsirie|fasiri)\s+{_Q}(?P<p>.+?){_Q}\s+(?:kwa|kwenda|kuwa|katika|hadi)\s+(?P<l>{_LANG_ALT})\b",
    rf"^\s*(?:niambie|sema)\s+{_Q}(?P<p>.+?){_Q}\s+(?:kwa|kwa lugha ya)\s+(?P<l>{_LANG_ALT})\b",
]
_TRANSLATE_RE = [re.compile(p, re.I | re.S) for p in _TRANSLATE]

# Other wrappers: the quoted sentence is material to work on, not a question for this assistant.
_WRAP = re.compile(
    r"^\s*(?:please\s+)?(?:repeat|say|echo|quote|type|print|spell|copy|paraphrase|rephrase|reword|rewrite|proofread|correct|fix the grammar|check the grammar|"
    r"summari[sz]e|shorten|continue|complete|finish|répète|repete|dis|redis|reformule|corrige|resume|résume|subiramo|subiza|vuga|andika|rudia|sahihisha|"
    r"rudia|sema|rudisha|fupisha)\b[^.?!]*?[:\"“«']",
    re.I,
)
_META_SENTENCE = re.compile(r"\b(?:the (?:phrase|sentence|question|words?)|this (?:phrase|sentence|question)|ngo|que)\b", re.I)
_WRAP_PLAIN = re.compile(r"^\s*(?:please\s+)?(?:repeat after me|say exactly|répète après moi|subiramo nyuma yanjye|rudia baada yangu)\b", re.I)


def parse_translation(question):
    """(phrase, target_code) when the message asks to translate a sentence into a language, else None. target_code may be '' if only the phrase is clear."""
    q = (question or "").strip()
    if not q or len(q) > 400:
        return None
    for rx in _TRANSLATE_RE:
        m = rx.match(q)
        if not m:
            continue
        phrase = (m.group("p") or "").strip(" \"'“”«»:.-")
        lang_word = fold(m.groupdict().get("l") or "")
        code = ""
        for c, ws in LANG_WORDS.items():
            if lang_word in [fold(w) for w in ws]:
                code = c
        if phrase and len(phrase) <= 300:
            return phrase, code
    return None


def is_wrapper(question):
    """True when the message asks the assistant to repeat, rewrite, correct or quote a sentence (so the sentence itself must not be answered)."""
    q = (question or "").strip()
    if not q or len(q) > 400:
        return False
    return bool(_WRAP.match(q) or _WRAP_PLAIN.match(q))


# --- machine translation fallback for when no AI is available (free MyMemory service; quality varies, especially for Kinyarwanda) ---
def _guess_source(text):
    try:
        from detector import detect_language, fold as dfold
        return detect_language(dfold(text)) or "en"
    except Exception:
        return "en"


def machine_translate(phrase, target, source=None, timeout=7):
    """Translated text from MyMemory, or None. Never raises."""
    try:
        src = source or _guess_source(phrase)
        if target not in ("en", "fr", "rw", "sw") or src == target:
            return None
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": phrase[:450], "langpair": f"{src}|{target}"})
        req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0 (educational safety assistant)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (fixed https host)
            data = json.loads(r.read().decode("utf-8", "replace"))
        out = ((data.get("responseData") or {}).get("translatedText") or "").strip()
        if not out or out.upper().startswith(("MYMEMORY WARNING", "INVALID", "PLEASE SELECT")) or out.lower() == phrase.lower():
            return None
        return out
    except Exception:
        return None


NAMES = {"en": {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Swahili"}, "fr": {"en": "anglais", "fr": "français", "rw": "kinyarwanda", "sw": "swahili"},
         "rw": {"en": "Icyongereza", "fr": "Igifaransa", "rw": "Ikinyarwanda", "sw": "Igiswahili"}, "sw": {"en": "Kiingereza", "fr": "Kifaransa", "rw": "Kinyarwanda", "sw": "Kiswahili"}}
MT_NOTE = {"en": "Automatic translation. It may be wrong or unnatural, especially for Kinyarwanda and Kiswahili; ask a fluent speaker to confirm anything important.",
           "fr": "Traduction automatique. Elle peut être fausse ou peu naturelle, surtout en kinyarwanda et en swahili ; faites confirmer ce qui est important par un locuteur courant.",
           "rw": "Ni ubusobanuro bwikora. Bushobora kuba bufite amakosa cyangwa budasanzwe, cyane mu Kinyarwanda no mu Giswahili; saba umuntu uzi ururimi neza kwemeza ibiri ngombwa.",
           "sw": "Tafsiri ya kiotomatiki. Inaweza kuwa na makosa au isiyo ya kawaida, hasa kwa Kinyarwanda na Kiswahili; mwombe mzungumzaji fasaha athibitishe jambo muhimu."}
MT_FAIL = {"en": "I could not translate that right now. Try again in a moment, or ask in the form “How do you say … in Kinyarwanda”.",
           "fr": "Je n'ai pas pu traduire cela pour le moment. Réessayez dans un instant, ou demandez sous la forme « Comment dit-on … en kinyarwanda ».",
           "rw": "Ntabashije kubisobanura ubu. Ongera ugerageze nyuma gato, cyangwa ubaze ugira uti «… bivuga gute mu Kinyarwanda».",
           "sw": "Sikuweza kutafsiri hilo sasa hivi. Jaribu tena baadaye kidogo, au uliza kwa namna «… kwa Kinyarwanda ni nini»."}


def translation_answer(phrase, target, ui_lang):
    """Plain, honest answer text for a translation request when no AI is available."""
    k = ui_lang if ui_lang in NAMES else "en"
    if not target:
        target = {"en": "rw", "rw": "en", "fr": "en", "sw": "en"}[k]
    out = machine_translate(phrase, target)
    if not out:
        return MT_FAIL[k], False
    return f"**{NAMES[k][target]}:** {out}\n\n_{MT_NOTE[k]}_", True
