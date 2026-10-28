"""Cybersecurity glossary for the AI Assistant: meaning, real-world use and photos, in English, French, Kinyarwanda and Kiswahili.
Pure Python (no Streamlit). Data lives in cyber_terms_1.py ... cyber_terms_24.py (any that exist are loaded).

Row = (id, English name, aliases, category, photo query, local names {fr,sw,rw} or None,
       en_meaning, en_use, fr_meaning, fr_use, rw_meaning, rw_use, sw_meaning, sw_use)

Questions it answers: "what is a firewall", "meaning of phishing", "define ransomware", "firewall", "applications of encryption", "cybersecurity terms",
"list all cybersecurity terms", "malware terms". Only a whole-term lookup is answered here (so "what is phishing and how do I avoid it" still goes to the
step-by-step guide). Kinyarwanda and Kiswahili text is a draft for review by fluent speakers."""
from __future__ import annotations
import importlib
import re
from textutil import fold, lk, entry, LANGS

CATS = {
    "foundations": ("Foundations", "Fondamentaux", "Ibanze", "Misingi"),
    "malware": ("Malware (harmful software)", "Logiciels malveillants", "Porogaramu z'ubugizi bwa nabi (malware)", "Programu hasidi (malware)"),
    "social": ("Social engineering and scams", "Ingénierie sociale et arnaques", "Uburiganya bukoresha abantu (social engineering)", "Ulaghai wa kijamii (social engineering)"),
    "attacks": ("Common attacks", "Attaques courantes", "Ibitero bikunze kubaho", "Mashambulizi ya kawaida"),
    "network": ("Network and infrastructure security", "Sécurité des réseaux et infrastructures", "Umutekano w'imiyoboro n'ibikorwaremezo", "Usalama wa mitandao na miundombinu"),
    "crypto": ("Cryptography", "Cryptographie", "Ubwihisho bw'amakuru (cryptography)", "Kriptografia"),
    "identity": ("Identity and access", "Identité et accès", "Ukwemeza uwo uri we n'uburenganzira", "Utambulisho na ufikiaji"),
    "appsec": ("Application security", "Sécurité des applications", "Umutekano wa porogaramu", "Usalama wa programu"),
    "cloud": ("Cloud and devices", "Cloud et appareils", "Cloud n'ibikoresho", "Cloud na vifaa"),
    "operations": ("Security operations and response", "Opérations de sécurité et réponse", "Imikorere y'umutekano n'igisubizo ku bitero", "Operesheni za usalama na mwitikio"),
    "governance": ("Law, standards and risk", "Loi, normes et risques", "Amategeko, ibipimo n'ingaruka", "Sheria, viwango na hatari"),
    "people": ("People and roles", "Personnes et rôles", "Abantu n'inshingano", "Watu na majukumu"),
    "defense": ("Defences and good practice", "Défenses et bonnes pratiques", "Uburyo bwo kwirinda n'imikorere myiza", "Ulinzi na mazoea mazuri"),
    "practice": ("Good practice", "Bonnes pratiques", "Imikorere myiza", "Mazoea mazuri"),
    "privacy": ("Privacy", "Vie privée", "Ibanga ry'umuntu", "Faragha"),
}

TERMS = []
for _i in range(1, 40):
    try:
        _m = importlib.import_module(f"cyber_terms_{_i}")
    except ImportError:
        continue
    TERMS += list(getattr(_m, f"TERMS_{_i}", []))

_BY_ID = {r[0]: r for r in TERMS}
COUNT = len(TERMS)


def validate(rows=None):
    """List of problems in the data (empty list = fine). Used by tests and by whoever writes new rows."""
    rows = TERMS if rows is None else rows
    errs, seen = [], set()
    for r in rows:
        if len(r) != 14:
            errs.append(f"{r[0] if r else '?'}: {len(r)} fields, expected 14")
            continue
        rid = r[0]
        if rid in seen:
            errs.append(f"{rid}: duplicate id")
        seen.add(rid)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", rid):
            errs.append(f"{rid}: id must be lowercase letters, digits and hyphens")
        if not isinstance(r[2], list) or not r[2]:
            errs.append(f"{rid}: aliases must be a non-empty list")
        if r[3] not in CATS:
            errs.append(f"{rid}: unknown category {r[3]!r}")
        if not str(r[4]).strip():
            errs.append(f"{rid}: photo query is empty")
        if r[5] is not None and not (isinstance(r[5], dict) and set(r[5]) <= {"fr", "sw", "rw"}):
            errs.append(f"{rid}: local names must be None or a dict with fr/sw/rw")
        for j in range(6, 14):
            t = str(r[j]).strip()
            if len(t) < 25:
                errs.append(f"{rid}: field {j} is empty or too short")
            if len(t) > 560:
                errs.append(f"{rid}: field {j} is too long ({len(t)} chars); keep it to a few sentences")
        # the English and local texts must differ (a copied English text in the French/Kinyarwanda/Kiswahili field is a mistake)
        for j in (8, 10, 12):
            if str(r[j]).strip() == str(r[6]).strip():
                errs.append(f"{rid}: field {j} repeats the English meaning")
    return errs


# --- matching -------------------------------------------------------------------------------------------------------------------
_INDEX = {}      # folded alias or name -> term id
for _r in TERMS:
    names = [_r[1]] + list(_r[2]) + list((_r[5] or {}).values())
    for _n in names:
        for _v in {fold(re.sub(r"\(.*?\)", "", _n)).strip(), fold(_n).strip()}:
            if _v and len(_v) >= 2:
                _INDEX.setdefault(_v, _r[0])

try:   # extra names for existing terms (cyber_alias_extra.py); never overrides a name that is already taken
    from cyber_alias_extra import ALIASES as _EXTRA_ALIASES
    _ids = {r[0] for r in TERMS}
    for _rid, _als in _EXTRA_ALIASES.items():
        if _rid in _ids:
            for _a in _als:
                for _v in {fold(re.sub(r"\(.*?\)", "", _a)).strip(), fold(_a).strip()}:
                    if _v and len(_v) >= 2:
                        _INDEX.setdefault(_v, _rid)
except ImportError:
    pass

_FRAME = re.compile(
    r"^(?:what(?:'s| is| are| was| does| do)?|whats|who is|define|definition of|meaning of|the meaning of|explain|describe|tell me about|tell me more about|give me|show me|"
    r"what is the meaning of|what does|how does|how do|"
    r"qu'est-ce que|qu'est ce que|c'est quoi|definition de|le sens de|explique|expliquez|parle-moi de|"
    r"ni iki|iki ni iki|sobanura|busobanura iki|icyo bisobanura|amakuru kuri|mbwira kuri|"
    r"nini maana ya|maana ya|ni nini|eleza|nieleze|niambie kuhusu)\s+", re.I)
_TAIL = re.compile(r"\s+(?:mean|means|meaning|definition|work|works|stand for|stands for|is used for|used for|in cybersecurity|in cyber security|in security|in it|signifie|veut dire|"
                   r"bisobanura|bivuze|maana|inamaanisha|ni iki|ni nini|kuhusu usalama wa mtandao|en cybersecurite|en cybersécurité)$", re.I)
_USES = re.compile(r"\b(?:applications?|uses?|usage|use cases?|examples?|used for|where is it used|utilisations?|usages?|applications?|ikoreshwa|ikoreshwa he|matumizi|inatumika wapi)\b", re.I)
_NOT = re.compile(r"\b(?:how (?:do|can|to|should) i|should i|can i|is it safe|am i|did i|i (?:was|got|have|clicked|sent|shared|lost)|help me|my |write|translate|solve|calculate|compare|difference between|vs\.?|"
                  r"comment (?:puis|dois|faire)|nakora|nifanye)\b", re.I)
_LISTW = re.compile(r"\b(?:all|every|list|complete|full|types|terms|glossary|dictionary|vocabulary|tous|toutes|liste|glossaire|vocabulaire|byose|zose|urutonde|yote|orodha|msamiati)\b", re.I)
_CYBER = re.compile(r"\b(?:cyber ?security|cyber ?securite|cybersecurite|cyber|security|secure|securite|umutekano|usalama|hacking|infosec)\b", re.I)
_TERMW = re.compile(r"\b(?:terms?|words?|vocabulary|glossary|dictionary|terminology|termes?|mots?|vocabulaire|glossaire|amagambo|inkoranyamagambo|istilahi|msamiati|maneno|kamusi)\b", re.I)


def _extract(question):
    q = (question or "").strip().strip("?!.\"' ").strip()
    if not q or len(q) > 110 or "\n" in q:
        return None
    for _ in range(2):
        q2 = _FRAME.sub("", q).strip()
        q2 = re.sub(r"^(?:a|an|the|le|la|les|l'|un|une)\s+", "", q2, flags=re.I)
        if q2 == q:
            break
        q = q2
    q = _TAIL.sub("", q).strip().strip("?!.\"' ").strip()
    return q or None


def lookup(term_text):
    """Term row for an exact name/alias (any language), or None."""
    q = fold(term_text or "")
    for v in (q, re.sub(r"^(?:a|an|the)\s+", "", q), q.rstrip("s") if len(q) > 4 else q):
        rid = _INDEX.get(v)
        if rid:
            return _BY_ID[rid]
    return None


def related(row, n=4):
    """Other terms in the same category (for 'see also')."""
    return [r for r in TERMS if r[3] == row[3] and r[0] != row[0]][:n]


def _text(row, l, uses_first=False):
    j = {"en": 6, "fr": 8, "rw": 10, "sw": 12}[l]
    meaning, use = row[j], row[j + 1]
    local = (row[5] or {}).get(l) if l != "en" else None
    head = f"**{row[1]}**" + (f" — {local}" if local else "")
    lab = {"en": ("Meaning", "Where it is used and what to do", "Category", "See also"),
           "fr": ("Sens", "Où on le rencontre et que faire", "Catégorie", "Voir aussi"),
           "rw": ("Icyo bivuze", "Aho bikoreshwa n'icyo gukora", "Icyiciro", "Reba na"),
           "sw": ("Maana", "Inatumika wapi na la kufanya", "Kundi", "Tazama pia")}[l]
    cat = CATS[row[3]][LANGS.index(l)]
    rel = ", ".join(r[1] for r in related(row))
    parts = [f"**{lab[0]}:** {meaning}", f"**{lab[1]}:** {use}", f"_{lab[2]}: {cat}_"]
    if uses_first:
        parts[0], parts[1] = parts[1], parts[0]
    if rel:
        parts.append(f"_{lab[3]}: {rel}_")
    return "\n\n".join(parts)


def term_entry(row, uses_first=False):
    e = entry("cyber_" + row[0], "cyber", {l: row[1] + ((" — " + (row[5] or {}).get(l)) if (row[5] or {}).get(l) else "") if l != "en" else row[1] for l in LANGS},
              {l: _text(row, l, uses_first) for l in LANGS})
    e["photo_query"] = row[4]
    e["priority"] = True
    return e


def overview(lang="en", cat=None):
    rows = [r for r in TERMS if cat is None or r[3] == cat]
    title = {"en": "Cybersecurity terms", "fr": "Termes de cybersécurité", "rw": "Amagambo y'umutekano wa interineti", "sw": "Istilahi za usalama wa mtandao"}
    intro = {"en": "{n} cybersecurity terms with their meaning, where they are used and photos. Type any term (for example “firewall”, “phishing”, “encryption”) to see its full explanation.",
             "fr": "{n} termes de cybersécurité avec leur sens, leurs usages et des photos. Tapez un terme (par exemple « pare-feu », « phishing », « chiffrement ») pour voir l'explication complète.",
             "rw": "Amagambo {n} y'umutekano wa interineti afite ibisobanuro, aho akoreshwa n'amafoto. Andika ijambo (urugero «firewall», «phishing», «encryption») urebe ibisobanuro byuzuye.",
             "sw": "Istilahi {n} za usalama wa mtandao zenye maana, matumizi na picha. Andika istilahi yoyote (kwa mfano «firewall», «phishing», «encryption») uone maelezo kamili."}
    def _name(r, l):
        local = (r[5] or {}).get(l) if l != "en" else None
        return r[1] + (f" ({local})" if local else "")

    if cat is None:   # all terms: one line per category (readable) instead of 281 numbered lines
        steps = {}
        for l in LANGS:
            lines = []
            for c, names in CATS.items():
                in_c = [r for r in rows if r[3] == c]
                if in_c:
                    lines.append(f"**{names[LANGS.index(l)]} ({len(in_c)}):** " + ", ".join(_name(r, l) for r in in_c))
            steps[l] = lines
    else:
        steps = {l: [f"**{_name(r, l)}**" for r in rows] for l in LANGS}
    e = entry("cyber_list" if cat is None else "cyber_cat_" + cat, "cyber_list", title, {l: intro[l].format(n=len(rows)) for l in LANGS}, steps,
              {l: (title[l] if cat is None else CATS[cat][LANGS.index(l)]) for l in LANGS})
    e["priority"] = True
    return e


def find(question, lang="en"):
    """Guide-shaped entry for a cybersecurity-term question, or None."""
    q = (question or "").strip()
    if not q or len(q) > 120 or _NOT.search(q):
        return None
    folded = fold(q)
    # glossary / list requests
    if (_TERMW.search(q) or _TERMW.search(folded)) and (_CYBER.search(folded) or _LISTW.search(folded)) and len(folded.split()) <= 9:
        for cat, names in CATS.items():
            if cat in ("defense", "practice", "privacy"):
                continue
            if any(re.search(r"(?<![a-z])" + re.escape(fold(n.split(" (")[0].split(" and ")[0])) + r"(?![a-z])", folded) for n in names[:1]) and _TERMW.search(q):
                return overview(lang, cat)
        for cat, key in (("malware", r"\bmalware\b"), ("social", r"\bsocial engineering\b|\bscam"), ("crypto", r"\bcrypto"), ("network", r"\bnetwork")):
            if re.search(key, folded) and re.search(r"\bterms?\b|\bglossary\b|\bvocabulary\b", folded):
                return overview(lang, cat)
        return overview(lang)
    uses = bool(_USES.search(q))
    term = _extract(_USES.sub(" ", re.sub(r"\b(?:of|for|de|du|des|za|wa|ya|bya|mu|ku)\b", " ", q)).strip() if uses else q)
    if not term or len(term.split()) > 5:
        return None
    row = lookup(term)
    if row is None:
        return None
    return term_entry(row, uses_first=uses)
