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
    "rw": ["kinyarwanda", "ikinyarwanda", "ururimi rw'ikinyarwanda", "kinyarwandaa", "kinya", "rw"],
    "fr": ["french", "francais", "français", "igifaransa", "gifaransa", "kifaransa", "fr"],
    "sw": ["swahili", "kiswahili", "igiswahili", "giswahili", "kiswahilii", "sw"],
    "en": ["english", "anglais", "icyongereza", "cyongereza", "kiingereza", "englishi", "en"],
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


# --- full parser: "Translate this word from French to Kinyarwanda: bonjour", "translate hello from English to Swahili", "traduis merci du français au kinyarwanda", ...
_VERB = re.compile(r"^\s*(?:please\s+|s'il vous pla[iî]t\s+|nyabuneka\s+|tafadhali\s+)?(?:can you\s+|could you\s+|peux-tu\s+|pouvez-vous\s+)?(?:translate|translation of|traduis(?:ez)?(?:-moi)?|traduire|hindura|humura|tafsiri|nitafsirie|fasiri)\b\s*", re.I)
_FILLER = re.compile(r"^(?:(?:this|the|that|ce|cette|le|la|iri|iyi|neno hili|hili)\s+)(?:words?|phrases?|sentences?|texts?|mots?|expressions?|jambo|amagambo|interuro|inyandiko|neno|maneno|sentensi|maandishi)\s*(?:for me|pour moi|for us)?\s*", re.I)
_LA = r"(?:the\s+|le\s+|la\s+|l['’]|ururimi\s+rw['’]?\s*|lugha\s+ya\s+)?"
_SRC_RE = re.compile(r"(?:\bfrom\b|\bdu\b|\bde la\b|\bde l['’]|\bde\b|\bd['’]|\bdes\b|\bkuva\s+mu\b|\bkuva\b|\bkutoka\s+kwa\b|\bkutoka\b)\s*" + _LA + r"(?P<l>" + _LANG_ALT + r")\b", re.I)
_TGT_RE = re.compile(r"(?:\bto\b|\binto\b|\bin\b|\ben\b|\bvers\b|\bau\b|\bà\b|\ba\b|\bmu\b|\bkwenda\b|\bkwa\b|\bujya\s+mu\b|\bkuwa\b|\bhadi\b)\s*" + _LA + r"(?P<l>" + _LANG_ALT + r")\b", re.I)


def _code(word):
    w = fold(word)
    for c, ws in LANG_WORDS.items():
        if w in [fold(x) for x in ws]:
            return c
    return ""


def parse_translation_full(question):
    """(phrase, source_code, target_code) for "Translate <this word> from X to Y[: text]" in English, French, Kinyarwanda and Kiswahili, else None.
    source_code may be '' when no source language is named. Needs a target language and a non-empty phrase."""
    q = (question or "").strip()
    if not q or len(q) > 400:
        return None
    v = _VERB.match(q)
    if not v:
        return None
    body = q[v.end():]
    src = tgt = ""
    spans = []
    for m in _SRC_RE.finditer(body):
        c = _code(m.group("l"))
        if c:
            src = c
            spans.append(m.span())
            break
    taken = [s for s in spans]
    tm = [m for m in _TGT_RE.finditer(body) if _code(m.group("l")) and not any(a <= m.start() < b for a, b in taken)]
    if not tm:
        return None
    m = tm[-1] if not src else tm[0] if len(tm) == 1 else tm[-1]
    tgt = _code(m.group("l"))
    spans.append(m.span())
    if src and src == tgt:
        return None
    colon = re.search(r"[:：]\s*(.+)$", body, re.S)
    if colon and not any(a <= colon.start() < b for a, b in spans):
        phrase = colon.group(1)
    else:
        rest, last = [], 0
        for a, b in sorted(spans):
            rest.append(body[last:a]); last = b
        rest.append(body[last:])
        phrase = " ".join(x.strip() for x in rest if x.strip())
        phrase = re.sub(r"\s+", " ", phrase)
    if not colon:
        stripped = _FILLER.sub("", phrase.strip(), count=1)
        if stripped.strip() and stripped != phrase.strip():
            phrase = stripped
    phrase = phrase.strip(" \"'“”«»:.-?!")
    if not phrase or len(phrase) > 300:
        return None
    return phrase, src, tgt


def parse_translation(question):
    """(phrase, target_code) when the message asks to translate a sentence into a language, else None. target_code may be '' if only the phrase is clear."""
    q = (question or "").strip()
    if not q or len(q) > 400:
        return None
    full = parse_translation_full(q)
    if full is not None:
        return full[0], full[2]
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


def _looks_like(text, target):
    """True when the text plausibly is in the target language (stops MT returning English or gibberish as 'Kinyarwanda')."""
    try:
        from detector import detect_language, fold as dfold
        got = detect_language(dfold(text))
    except Exception:
        return True
    if got == target:
        return True
    # short texts carry few marker words: accept when no other language is clearly detected and it differs from the source text
    return got == "en" and target != "en" and False


def machine_translate(phrase, target, source=None, timeout=7):
    """Translated text from MyMemory, or None. Never raises. Output in the wrong language, or unchanged, is rejected."""
    try:
        src = source or _guess_source(phrase)
        if target not in ("en", "fr", "rw", "sw") or src == target:
            return None
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode({"q": phrase[:450], "langpair": f"{src}|{target}"})
        req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0 (educational safety assistant)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (fixed https host)
            data = json.loads(r.read().decode("utf-8", "replace"))
        out = ((data.get("responseData") or {}).get("translatedText") or "").strip()
        if not out or out.upper().startswith(("MYMEMORY WARNING", "INVALID", "PLEASE SELECT", "QUERY LENGTH")) or out.lower() == phrase.lower():
            return None
        if target == "rw" and set(out.lower().split()) & {"the", "is", "are", "of", "and", "you", "your", "who", "what"}:
            return None          # English words inside a "Kinyarwanda" answer: reject instead of showing it
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


_PIECES = {"en": "Meaning of the words I know in your text (not a full sentence translation, because word order and endings differ between the languages)",
           "fr": "Sens des mots que je connais dans votre texte (ce n'est pas une traduction de la phrase, car l'ordre des mots et les terminaisons diffèrent d'une langue à l'autre)",
           "rw": "Ibisobanuro by'amagambo nzi mu nyandiko yawe (si ubusobanuro bw'interuro yose, kuko uko amagambo akurikirana n'iherezo ryayo bitandukana)",
           "sw": "Maana ya maneno ninayoyajua kwenye maandishi yako (si tafsiri ya sentensi nzima, kwa sababu mpangilio wa maneno na miisho hutofautiana)"}
_NEED_KEY = {"en": "For a full, natural translation of any sentence, the AI translator needs GEMINI_API_KEY in the app's Secrets. Until then I answer exactly what is in my hand-written bank, or ask in the form “How do you say … in Kinyarwanda”.",
             "fr": "Pour une traduction complète et naturelle de n'importe quelle phrase, le traducteur IA a besoin de GEMINI_API_KEY dans les Secrets de l'application. D'ici là, je réponds exactement avec ma banque écrite à la main.",
             "rw": "Kugira ngo mpindure interuro iyo ari yo yose neza kandi mu buryo busanzwe, umusemuzi wa AI akeneye GEMINI_API_KEY mu Secrets za porogaramu. Mbere y'aho, mpa ibisubizo biri mu bubiko bwanjye bwanditswe n'intoki gusa.",
             "sw": "Ili kutafsiri sentensi yoyote kikamilifu na kwa asili, mfasiri wa AI anahitaji GEMINI_API_KEY kwenye Secrets za programu. Hadi hapo, ninajibu kile kilicho kwenye benki yangu iliyoandikwa kwa mkono tu."}


def translation_answer(phrase, target, ui_lang, source=None):
    """Answer text for a translation request when no AI is available. Order: curated bank (exact), checked machine translation, then the honest
    fallback: the words I do know, word by word, with a clear note that this is not a sentence translation."""
    k = ui_lang if ui_lang in NAMES else "en"
    if not target:
        target = {"en": "rw", "rw": "en", "fr": "en", "sw": "en"}[k]
    TD = None
    try:
        import translate_db as TD
        res = TD.translate(phrase, target, k, source)
        if res is not None:
            return TD.render(res, k)["answer"][k], True
    except Exception:
        TD = None
    out = machine_translate(phrase, target, source)
    if out and target != "rw":     # Kinyarwanda machine output is too unreliable to present as an answer
        return f"**{NAMES[k][target]}:** {out}\n\n_{MT_NOTE[k]}_", True
    parts = []
    if TD is not None:
        try:
            pieces = TD.breakdown(phrase, target)
            if pieces:
                parts.append(f"**{_PIECES[k]} → {NAMES[k][target]}:**\n\n" + "\n".join(f"- **{a}** → {b}" for a, b in pieces))
            sug = TD.suggest(phrase)
            if sug:
                parts.append(TD.render_suggestions(phrase, sug, k)["answer"][k])
        except Exception:
            pass
    if parts:
        return "\n\n".join(parts) + f"\n\n_{_NEED_KEY[k]}_", False
    return MT_FAIL[k] + f"\n\n_{_NEED_KEY[k]}_", False
