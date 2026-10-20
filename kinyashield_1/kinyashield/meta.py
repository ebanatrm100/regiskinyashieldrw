"""Requests ABOUT a sentence (translate it, rewrite it, summarise it ...) are not questions to the assistant itself.
"Translate who owns you into Kinyarwanda" asks for a translation of that sentence; it must not trigger the owner answer.
detect(question) finds such commands so the router can keep the quoted text away from the content finders (owner, greetings, names ...).
Pure Python, four languages."""
from __future__ import annotations
import re
from textutil import fold

CODES = {"english": "en", "anglais": "en", "icyongereza": "en", "cyongereza": "en", "kiingereza": "en", "en": "en",
         "french": "fr", "francais": "fr", "igifaransa": "fr", "gifaransa": "fr", "kifaransa": "fr", "fr": "fr",
         "kinyarwanda": "rw", "ikinyarwanda": "rw", "kinyarwanda": "rw", "rw": "rw",
         "swahili": "sw", "kiswahili": "sw", "igiswahili": "sw", "giswahili": "sw", "sw": "sw"}
NAMES = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}
_LANG = r"(english|anglais|icyongereza|cyongereza|kiingereza|french|francais|igifaransa|gifaransa|kifaransa|kinyarwanda|ikinyarwanda|swahili|kiswahili|igiswahili|giswahili)"

_TRANSLATE = [
    re.compile(r"^(?:please |pls |can you |could you )?(?:translate|translation of)\s+(.+?)\s+(?:in|into|to|in to)\s+(?:the )?" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:please |can you |could you )?(?:translate|traduis|traduire|traduisez)\s+(?:en\s+)?" + _LANG + r"\s*[:,-]\s*(.+)$", re.I | re.S),
    re.compile(r"^(?:how (?:do|would|can) (?:you|i|we) say|how to say|how (?:do|would) i say|say)\s+(.+?)\s+in\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:what is|what's|whats)\s+(.+?)\s+in\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:please |pouvez-vous |peux-tu )?(?:traduis|traduire|traduisez)\s+(.+?)\s+en\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:comment (?:dit-on|dire|on dit))\s+(.+?)\s+en\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:vuga|andika|sobanura|hindura)\s+(.+?)\s+mu\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(.+?)\s+(?:bivuga gute|byandikwa gute|ni iki)\s+mu\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:tafadhali )?(?:tafsiri|tafsiri kwa|fasiri)\s+(.+?)\s+(?:kwa|kuwa|kwenda|kuingia)\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
    re.compile(r"^(?:niambie|sema)\s+(.+?)\s+(?:kwa)\s+" + _LANG + r"\s*[.?!]*$", re.I | re.S),
]
_TASK = re.compile(r"^(?:please |can you |could you )?(summari[sz]e|paraphrase|rewrite|rephrase|proofread|correct|fix the grammar of|shorten|expand|spell|repeat after me|resume|reformule|corrige|fasihisha|fupisha|andika upya|ongera wandike)\b[\s:,-]+(.+)$", re.I | re.S)


def _strip(text: str) -> str:
    return text.strip().strip("\"'“”‘’«»").strip()


def detect(question: str):
    """{'kind': 'translate', 'text', 'target'} | {'kind': 'task', 'verb', 'text'} | None."""
    q = (question or "").strip()
    if not q or len(q) > 1500:
        return None
    for rx in _TRANSLATE:
        m = rx.match(q)
        if m:
            a, b = m.group(1), m.group(2)
            lang_word, text = (a, b) if fold(a) in CODES else (b, a)
            code = CODES.get(fold(lang_word))
            text = _strip(text)
            if code and text:
                return {"kind": "translate", "text": text, "target": code}
    m = _TASK.match(q)
    if m:
        return {"kind": "task", "verb": m.group(1).lower(), "text": _strip(m.group(2))}
    return None
