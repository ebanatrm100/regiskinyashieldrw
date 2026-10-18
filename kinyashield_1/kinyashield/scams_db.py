"""Scam and cyber-fraud methods for the AI Assistant (offline). Pure Python, no Streamlit.

Answers "what are the methods of scams in cybersecurity" with a catalogue of the main scam families, each with a description, an invented example and how to protect yourself,
in en/fr/rw/sw, and answers questions about one method (phishing, SIM swap, ransomware ...). The data lives in scams_data.py.
Honest limits: this is NOT every scam that exists (criminals invent new variations constantly; there is no complete list, and nothing close to millions of separate methods:
there are a few dozen families with endless variations). The text is protective (recognise and resist), not instructions for committing fraud. fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import re, unicodedata
from scams_data import DATA

LANGS = ("en", "fr", "rw", "sw")
COUNT = len(DATA)
ORDER = list(DATA)

_UI = {  # steps label, example, protect, list intro, note
    "en": ("Key facts", "Example", "How to protect yourself", "Here are {n} main methods used to scam people online and by phone, each with a description, an example and how to protect yourself. {extra}This is a guide to the main families, not a complete list: criminals keep inventing new variations, so there is no full list. If a message is urgent, asks for a PIN, code or money, or sounds too good to be true, stop and check through an official channel. Ask about any method by name (for example “phishing” or “SIM swap”) for more.",
           "(You asked for {want}; {have} main methods are listed here.) "),
    "fr": ("À retenir", "Exemple", "Comment vous protéger", "Voici {n} méthodes principales utilisées pour arnaquer les gens en ligne et par téléphone, chacune avec une description, un exemple et la façon de se protéger. {extra}C'est un guide des grandes familles, pas une liste complète : les criminels inventent sans cesse de nouvelles variantes, il n'existe donc pas de liste exhaustive. Si un message est urgent, demande un PIN, un code ou de l'argent, ou semble trop beau pour être vrai, arrêtez-vous et vérifiez par un canal officiel. Demandez une méthode par son nom (par exemple « phishing » ou « SIM swap ») pour en savoir plus.",
           "(Vous en avez demandé {want} ; {have} méthodes principales sont listées ici.) "),
    "rw": ("Ibyingenzi", "Urugero", "Uko wakwirinda", "Dore uburyo {n} bw'ingenzi bukoreshwa mu kuriganya abantu kuri interineti no kuri telefoni, buri bumwe bufite ibisobanuro, urugero n'uburyo bwo kwirinda. {extra}Ni umurongo w'ubwoko bukuru, ntabwo ari urutonde rwuzuye: abagizi ba nabi bahora bahimba ubundi buryo, nta rutonde rwuzuye ruriho. Niba ubutumwa bwihutirwa, busaba PIN, kode cyangwa amafaranga, cyangwa bumeze nk'aho ari byiza birenze, hagarara ugenzure unyuze mu nzira yemewe. Baza uburyo ubwo ari bwo bwose ku izina (urugero «phishing» cyangwa «SIM swap»).",
           "(Wasabye {want}; hano hari uburyo {have} bw'ingenzi.) "),
    "sw": ("Mambo muhimu", "Mfano", "Jinsi ya kujilinda", "Hizi hapa mbinu {n} kuu zinazotumiwa kuwatapeli watu mtandaoni na kwa simu, kila moja ikiwa na maelezo, mfano na jinsi ya kujilinda. {extra}Huu ni mwongozo wa makundi makuu, si orodha kamili: wahalifu wanaendelea kubuni mbinu mpya, kwa hiyo hakuna orodha kamili. Ujumbe ukiwa wa dharura, unaomba PIN, msimbo au pesa, au unaonekana mzuri kupita kiasi, simama na uhakiki kupitia njia rasmi. Uliza mbinu yoyote kwa jina (kwa mfano «phishing» au «SIM swap»).",
           "(Uliomba {want}; mbinu kuu {have} zimeorodheshwa hapa.) "),
}
_TITLE = {"en": "Methods of scams and cyber fraud", "fr": "Méthodes d'arnaque et de cyberfraude", "rw": "Uburyo bw'uburiganya n'ubujura bwo kuri interineti", "sw": "Mbinu za ulaghai na udanganyifu wa mtandaoni"}

_SCAM_WORDS = {"scam", "scams", "scammer", "scammers", "scamming", "fraud", "frauds", "fraudster", "cybercrime", "cybercrimes", "cyberattack", "cyberattacks", "cyber", "cybersecurity", "hacking", "swindle", "swindles", "tricks",
               "arnaque", "arnaques", "fraude", "fraudes", "escroquerie", "escroqueries", "cyberattaque", "cyberattaques", "cybersecurite", "cybercriminalite",
               "uburiganya", "uburyo", "ubujura", "ikinyoma", "abatekamutwe", "gutekinika", "ulaghai", "utapeli", "matapeli", "udanganyifu", "uhalifu", "usalama"}
_LIST_WORDS = {"method", "methods", "type", "types", "kind", "kinds", "list", "ways", "way", "technique", "techniques", "tricks", "forms", "all", "every", "different", "existing", "common", "main", "examples", "example",
               "methode", "methodes", "type", "types", "sorte", "sortes", "liste", "manieres", "techniques", "formes", "tous", "toutes", "exemples", "differentes", "existantes",
               "uburyo", "ubwoko", "bwoko", "urutonde", "ingero", "byose", "zose", "ibyo", "mbinu", "aina", "orodha", "njia", "zote", "mifano", "tofauti"}
_Q_WORDS = {"what", "whats", "how", "who", "explain", "tell", "about", "describe", "define", "meaning", "mean", "iki", "ninde", "sobanura", "quoi", "comment", "qu'est", "explique", "nini", "nani", "eleza", "maana", "ni", "give", "show"}
_NOT_LIST = {"protect", "prevent", "avoid", "report", "stop", "recover", "victim", "protegez", "proteger", "eviter", "kwirinda", "kujilinda", "jilinda"}


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


_INDEX = sorted(((fold(a), k) for k, v in DATA.items() for a in v[0]), key=lambda t: -len(t[0]))


def _lk(lang):
    return lang if lang in LANGS else "en"


def _alias_hits(text):
    padded, seen, hits = f" {text} ", set(), []
    for alias, key in _INDEX:
        if f" {alias} " in padded and key not in seen:
            seen.add(key)
            hits.append((key, alias))
    return hits


def _text(key, lang):
    return DATA[key][1 + LANGS.index(_lk(lang))]


def _entry(key):
    entry = {"id": "scam_" + key, "related": [], "kind": "scam_method", "key": key, "title": {}, "answer": {}, "steps": {}, "steps_label": {}}
    for l in LANGS:
        name, what, example, protect = _text(key, l)
        u = _UI[l]
        entry["title"][l], entry["answer"][l] = name, what
        entry["steps"][l] = [f"{u[1]}: {example}", f"{u[2]}: {protect}"]
        entry["steps_label"][l] = u[0]
    return entry


def _wanted(text):
    m = re.search(r"\b(\d{1,7})\b", text)
    if m:
        return int(m.group(1))
    words = {"ten": 10, "twenty": 20, "fifty": 50, "hundred": 100, "thousand": 1000, "million": 1000000, "millions": 1000000, "millions of": 1000000, "dix": 10, "vingt": 20, "cinquante": 50, "cent": 100, "mille": 1000}
    for w, n in words.items():
        if f" {w} " in f" {text} ":
            return n
    return None


def overview(lang="en", want=None):
    keys, have = ORDER, COUNT
    if want is not None and 0 < want < COUNT:
        keys, have = ORDER[:want], want
    entry = {"id": "scam_list", "related": [], "kind": "scam_list", "key": "list", "title": {}, "answer": {}, "steps": {}, "steps_label": {}}
    for l in LANGS:
        u = _UI[l]
        extra = u[4].format(want=f"{want:,}", have=COUNT) if (want is not None and want > COUNT) else ""
        entry["title"][l] = _TITLE[l]
        entry["answer"][l] = u[3].format(n=have, extra=extra)
        rows = []
        for k in keys:
            name, what, example, protect = _text(k, l)
            rows.append(f"**{name}** — {what} *{u[1]}:* {example} *{u[2]}:* {protect}")
        entry["steps"][l] = rows
        entry["steps_label"][l] = u[0]
    return entry


def find(question, lang="en"):
    """Guide-shaped entry for a question about scam methods, or None.

    List: a scam word (scam, fraud, cybercrime ...) AND a list word (methods, types, list, examples ...), and not a personal "how do I protect / I was scammed" question.
    One method: a known alias, either (almost) just the name or with a cue such as what/how/explain/ni iki."""
    q = (question or "").strip()
    if not q or len(q) > 220:
        return None
    text = fold(q)
    toks = text.split()
    if not toks:
        return None
    tset = set(toks) | set(re.split(r"[' \-]+", text))
    hits = _alias_hits(text)
    if (tset & _SCAM_WORDS) and (tset & _LIST_WORDS) and len(toks) <= 30 and not (tset & _NOT_LIST) and not (len(hits) == 1 and len(toks) <= 6 and not (tset & {"methods", "types", "list", "kinds", "examples"})):
        return overview(lang, _wanted(text))
    if not hits:
        return None
    key, alias = hits[0]
    bare = len(toks) <= 4 and all(t in alias.split() or t in {"a", "an", "the", "un", "une", "le", "la"} for t in toks)
    if bare or (tset & _Q_WORDS) or (tset & _LIST_WORDS):
        return _entry(key)
    return None
