"""Owner-supplied Kinyarwanda dictionary (461 words/phrases, each with a Kinyarwanda meaning).
- find(question, lang): "X ni iki", "igisobanuro cya X", "what does X mean in Kinyarwanda", ... (and a bare word when the interface is Kinyarwanda).
- reference_for(question): the matching entries as reference text for the online AI, so Kinyarwanda answers use these exact terms and meanings.
The meanings are marked in the source file as drafts that need expert checking; the answers say so and nothing is invented beyond the file."""
from __future__ import annotations
import re
from textutil import fold, entry, LANGS
from inkoranyamagambo_data import ROWS


def _k(s):
    return re.sub(r"\s+", " ", fold(s.replace("’", "'")).strip(" ?!.,;:\"'«»"))


_BY = {}
for _w, _t, _d in ROWS:
    _BY.setdefault(_k(_w), (_w, _t, _d))
_MAX_WORDS = max(len(k.split()) for k in _BY)
_MANY = {"umuryango", "imbuto", "igihe", "kugira"}      # the source file warns these have several meanings depending on the sentence

NOTE = {
    "rw": "Igisobanuro cy'ibanze cyateguwe; gisaba kugenzurwa n'inzobere mu Kinyarwanda.",
    "en": "Basic draft meaning (in Kinyarwanda) from your dictionary file; it still needs checking by a Kinyarwanda language expert.",
    "fr": "Sens de base provisoire (en kinyarwanda) tiré de votre fichier de dictionnaire ; il doit encore être vérifié par un expert du kinyarwanda.",
    "sw": "Maana ya msingi ya rasimu (kwa Kinyarwanda) kutoka faili lako la kamusi; bado inahitaji kukaguliwa na mtaalamu wa Kinyarwanda.",
}
MANY = {"rw": "Iri jambo rishobora kugira ibisobanuro bitandukanye bitewe n'interuro; hano ni icy'ibanze.",
        "en": "This word can have different meanings depending on the sentence; this is the basic one.",
        "fr": "Ce mot peut avoir des sens différents selon la phrase ; voici le sens de base.",
        "sw": "Neno hili linaweza kuwa na maana tofauti kulingana na sentensi; hii ni ya msingi."}
LAB = {"rw": ("Ubwoko", "Inkoranyamagambo y'Ikinyarwanda"), "en": ("Type", "Kinyarwanda dictionary"), "fr": ("Type", "Dictionnaire de kinyarwanda"), "sw": ("Aina", "Kamusi ya Kinyarwanda")}
HELP = {"rw": f"Mfite amagambo n'imvugo {len(ROWS)} afite ibisobanuro mu Kinyarwanda. Baza urugero: «umuntu ni iki?», «igisobanuro cya umwana», «sobanura ijambo ubwoba».",
        "en": f"I have {len(ROWS)} Kinyarwanda words and phrases with Kinyarwanda meanings. Ask for example: “what does umuntu mean in Kinyarwanda?”",
        "fr": f"J'ai {len(ROWS)} mots et expressions en kinyarwanda avec leur sens en kinyarwanda. Demandez par exemple : « que signifie umuntu en kinyarwanda ? »",
        "sw": f"Nina maneno na misemo {len(ROWS)} ya Kinyarwanda yenye maana kwa Kinyarwanda. Uliza kwa mfano: «umuntu ina maana gani kwa Kinyarwanda?»"}

_PRE = r"(?:(?:ijambo|imvugo|the word|le mot|neno)\s+)?"
_W = r"(?P<w>[^?!.]{1,40}?)"
_PATS = [  # (pattern, needs_kinyarwanda_mention_for_non_rw)
    re.compile(rf"^{_PRE}{_W}\s+(?:ni iki|ni ikihe|bisobanura iki|bivuze iki|bivuga iki|risobanura iki|rivuze iki|rivuga iki|ni ryari)$"),
    re.compile(rf"^(?:igisobanuro|ibisobanuro|ubusobanuro)\s+(?:bya|cya|bwa)\s+{_PRE}{_W}$"),
    re.compile(rf"^(?:sobanura|mbwira|mpa igisobanuro cya|mpa ibisobanuro bya)\s+{_PRE}{_W}$"),
    re.compile(rf"^what (?:does|is the meaning of)\s+{_PRE}{_W}\s+mean(?:\s+in kinyarwanda)?$"),
    re.compile(rf"^(?:meaning|definition) of\s+{_PRE}{_W}(?:\s+in kinyarwanda)?$"),
    re.compile(rf"^define\s+{_PRE}{_W}(?:\s+in kinyarwanda)?$"),
    re.compile(rf"^(?:que signifie|que veut dire|c'est quoi|qu'est-ce que)\s+{_PRE}{_W}(?:\s+en kinyarwanda)?$"),
    re.compile(rf"^(?:maana ya|nini maana ya)\s+{_PRE}{_W}(?:\s+(?:kwa|katika) kinyarwanda)?$"),
    re.compile(rf"^{_PRE}{_W}\s+(?:ina maana gani|inamaanisha nini)(?:\s+(?:kwa|katika) kinyarwanda)?$"),
]


def _lookup(word):
    key = _k(word)
    key = re.sub(r"^(?:ijambo|imvugo|the word|le mot|neno)\s+", "", key)
    return _BY.get(key)


def _entry(row, lang):
    w, t, d = row
    k = lang if lang in LAB else "en"
    out = {}
    for l in LANGS:
        lines = [f"**{w}**" + (f" ({LAB[l][0]}: {t})" if t else "") + f"\n\n{d}"]
        if _k(w) in _MANY:
            lines.append(f"_{MANY[l]}_")
        lines.append(f"_{NOTE[l]}_")
        out[l] = "\n\n".join(lines)
    return entry("ink_" + _k(w).replace(" ", "_"), "definition", {l: f"{w} — {LAB[l][1]}" for l in LANGS}, out)


def find(question, lang="en", explicit_only=False):
    """A dictionary entry for a question about a word in the owner's Kinyarwanda dictionary, else None."""
    raw = (question or "").strip()
    if not raw or len(raw) > 90:
        return None
    q = _k(raw)
    if re.fullmatch(r"(?:inkoranyamagambo|inkoranyamagambo y'ikinyarwanda|kinyarwanda dictionary|dictionnaire de kinyarwanda|kamusi ya kinyarwanda)", q):
        return entry("ink_help", "definition", {l: LAB[l][1] for l in LANGS}, dict(HELP))
    mentions = "kinyarwanda" in q
    for p in _PATS:
        m = p.match(q)
        if m:
            row = _lookup(m.group("w"))
            if row and (lang == "rw" or mentions or len(_k(row[0])) >= 5):
                return _entry(row, lang)
    if not explicit_only and lang == "rw" and len(q.split()) <= _MAX_WORDS:
        row = _BY.get(q)
        if row:
            return _entry(row, lang)
    return None


def reference_for(question, limit=10, max_chars=2200):
    """Dictionary entries for the words in the question, as text for the AI prompt (data, not instructions); '' when none."""
    q = _k(question or "")
    if not q:
        return ""
    toks = []
    for t in q.split():                                   # "n'umubyeyi" = "na umubyeyi": also try the word after the apostrophe
        toks.append(t)
        if "'" in t and len(t.split("'", 1)[1]) >= 3:
            toks.append(t.split("'", 1)[1])
    found, seen = [], set()
    for n in range(min(_MAX_WORDS, len(toks)), 0, -1):          # longer phrases first
        for i in range(len(toks) - n + 1):
            key = " ".join(toks[i:i + n])
            row = _BY.get(key)
            if row and key not in seen and (len(key) >= 4 or n > 1):
                seen.add(key)
                found.append(row)
    found = sorted(found, key=lambda r: -len(r[0]))[:limit]
    out, size = [], 0
    for w, t, d in found:
        line = f"- {w} ({t}): {d}"
        if size + len(line) > max_chars:
            break
        out.append(line)
        size += len(line)
    return "\n".join(out)
