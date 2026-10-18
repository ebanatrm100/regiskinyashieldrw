"""Physics formulas for the AI Assistant (offline). Pure Python, no Streamlit. Data lives in physics_data.py.

Questions it answers (en/fr/rw/sw): "all physics formulas", "mechanics formulas", "formula for kinetic energy", "Ohm's law", "what is Newton's second law",
"physics constants". Each formula is shown with what every symbol means (with SI units) and its topic. Standard textbook formulas; the answer is a reference, not a
substitute for a teacher or textbook (some formulas hold only under conditions, e.g. constant acceleration, ideal gas, small angles). fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import re, unicodedata
from physics_data import TOPICS, TERMS, FORMULAS

LANGS = ("en", "fr", "rw", "sw")
COUNT = len(FORMULAS)
_BY_ID = {f[0]: f for f in FORMULAS}

_UI = {  # where, topic, list intro, constants title, constants intro, caveat
    "en": ("Where", "Topic", "Here are {n} standard physics formulas, grouped by topic, in SI units. Ask for one by name (for example “kinetic energy formula” or “Ohm's law”) to see what every symbol means. Many formulas only hold under conditions (for example constant acceleration or an ideal gas).",
           "Physics constants and SI units", "Common physical constants (approximate values) and the SI base units."),
    "fr": ("Où", "Sujet", "Voici {n} formules de physique classiques, classées par thème, en unités SI. Demandez-en une par son nom (par exemple « formule énergie cinétique » ou « loi d'Ohm ») pour voir la signification de chaque symbole. Beaucoup de formules ne valent que sous conditions (par exemple accélération constante ou gaz parfait).",
           "Constantes physiques et unités SI", "Constantes physiques courantes (valeurs approchées) et unités de base du SI."),
    "rw": ("Aho", "Ingingo", "Dore formula {n} z'ibanze za fiziki, zitondaguye ku ngingo, mu bipimo bya SI. Baza imwe ku izina ryayo (urugero «kinetic energy formula» cyangwa «Ohm's law») urebe icyo buri kimenyetso bisobanura. Formula nyinshi zikora ari uko hari ibisabwa (urugero icyihutishi kidahinduka cyangwa umwuka mwiza).",
           "Ibipimo bihoraho bya fiziki n'ibipimo bya SI", "Ibipimo bihoraho bisanzwe (agaciro kegereje) n'ibipimo by'ibanze bya SI."),
    "sw": ("Ambapo", "Mada", "Hizi hapa fomula {n} za kawaida za fizikia, zimepangwa kwa mada, kwa vipimo vya SI. Uliza moja kwa jina (kwa mfano «kinetic energy formula» au «Ohm's law») uone maana ya kila ishara. Fomula nyingi zinafaa chini ya masharti tu (kwa mfano kasi isiyobadilika au gesi bora).",
           "Viwango vya fizikia na vipimo vya SI", "Viwango vya kawaida vya fizikia (thamani za makadirio) na vipimo vya msingi vya SI."),
}
_TOPIC_WORDS = {
    "mechanics": ["mechanics", "kinematics", "dynamics", "motion", "forces", "mecanique", "mouvement", "mekaniki", "mwendo", "ingendo"],
    "energy": ["energy", "work", "power", "energie", "travail", "puissance", "ingufu", "nishati", "kazi"],
    "gravitation": ["gravitation", "gravity", "orbits", "gravite", "rukuruzi", "mvuto"],
    "rotation": ["rotation", "rotational", "circular", "rotatif", "circulaire", "kuzenguruka", "mzunguko"],
    "waves": ["waves", "wave", "sound", "oscillations", "shm", "ondes", "son", "oscillation", "imiraba", "ijwi", "mawimbi", "sauti", "mitetemo"],
    "fluids": ["fluids", "fluid", "hydrostatics", "fluides", "fluide", "amazi", "vimiminika"],
    "thermo": ["thermodynamics", "thermo", "heat", "thermal", "gases", "thermodynamique", "chaleur", "ubushyuhe", "joto"],
    "electricity": ["electricity", "electric", "circuits", "circuit", "electrical", "electricite", "amashanyarazi", "umeme", "saketi"],
    "magnetism": ["magnetism", "magnetic", "induction", "magnetisme", "magnetique", "rukuruzi", "sumaku"],
    "optics": ["optics", "light", "lenses", "optique", "lumiere", "urumuri", "mwanga", "optiki"],
    "modern": ["modern", "quantum", "nuclear", "relativity", "atomic", "moderne", "quantique", "nucleaire", "relativite", "nyuklia", "kisasa"],
}
_PHYS = {"physics", "physic", "physique", "fiziki", "fizika", "fizikia", "phys"}
_FORM = {"formula", "formulas", "formulae", "equation", "equations", "formule", "formules", "equations", "fomula", "formula", "ikinyabutabire", "ibikinyabutabire", "mlinganyo", "milinganyo", "calculate", "calculer", "calcul", "kubara", "kokotoa"}
_LISTW = {"all", "every", "list", "tous", "toutes", "liste", "byose", "zose", "orodha", "yote", "types", "important", "main", "basic", "needed", "essential"}
_CONST = {"constants", "constant", "constantes", "ibipimo", "viwango", "kisimbuzi", "units"}
_BLOCK = {"scam", "scams", "fraud", "phishing", "password", "virus", "hack", "hacked", "malware", "pin"}
_CUES = {"what", "whats", "how", "explain", "tell", "about", "define", "show", "give", "state", "write", "quoi", "comment", "expliquer", "explique", "donne", "iki", "sobanura", "nini", "eleza", "toa", "ni"}


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("²", "2").replace("³", "3")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


def _variants(text):
    """The folded text with apostrophes removed (snell's -> snells, l'energie -> lenergie) and with apostrophes as spaces (l'energie -> l energie)."""
    return [text.replace("'", ""), text.replace("'", " ")]


_INDEX = []   # (alias, formula id)
for _f in FORMULAS:
    for _a in list(_f[2]) + list(_f[5]) + [_f[0]]:
        _INDEX.extend((v, _f[0]) for v in _variants(fold(_a)))
_INDEX = sorted(set(_INDEX), key=lambda t: -len(t[0]))


def _lk(lang):
    return lang if lang in LANGS else "en"


def _term_line(key, lang):
    sym, unit, *names = TERMS[key]
    return f"**{sym}** — {names[LANGS.index(_lk(lang))]} ({unit})"


def _entry(fid):
    f = _BY_ID[fid]
    entry = {"id": "physics_" + fid, "related": [], "kind": "physics", "title": {}, "answer": {}, "steps": {}, "steps_label": {}, "priority": True}
    for i, l in enumerate(LANGS):
        u = _UI[l]
        entry["title"][l] = f[2][i]
        entry["answer"][l] = f"`{f[3]}`\n\n*{u[1]}: {TOPICS[f[1]][i]}*"
        entry["steps"][l] = [_term_line(k, l) for k in f[4]] or [f[3]]
        entry["steps_label"][l] = u[0]
    return entry


def overview(lang="en", topic=None):
    items = [f for f in FORMULAS if topic is None or f[1] == topic]
    entry = {"id": "physics_list" if topic is None else "physics_topic_" + topic, "related": [], "kind": "physics_list", "title": {}, "answer": {}, "steps": {}, "steps_label": {}, "priority": True}
    for i, l in enumerate(LANGS):
        u = _UI[l]
        entry["title"][l] = (_TITLE[l] if topic is None else TOPICS[topic][i])
        entry["answer"][l] = u[2].format(n=len(items))
        entry["steps"][l] = [f"**{f[2][i]}** — `{f[3]}`" + (f"  ·  *{TOPICS[f[1]][i]}*" if topic is None else "") for f in items]
        entry["steps_label"][l] = u[1] + ": " + (", ".join(TOPICS[k][i].split(" (")[0] for k in TOPICS) if topic is None else TOPICS[topic][i])
    return entry


_TITLE = {"en": "Physics formulas", "fr": "Formules de physique", "rw": "Formula za fiziki", "sw": "Fomula za fizikia"}

_CONSTANTS = [
    ("c", "2.998 × 10⁸ m/s", "speed of light in vacuum", "vitesse de la lumière dans le vide", "umuvuduko w'urumuri mu cyuho", "kasi ya mwanga katika ombwe"),
    ("g", "9.81 m/s²", "gravitational acceleration at Earth's surface", "accélération de la pesanteur à la surface de la Terre", "icyihutishi cy'uburemere ku isi", "kuongeza kasi kwa mvuto juu ya uso wa dunia"),
    ("G", "6.674 × 10⁻¹¹ N·m²/kg²", "gravitational constant", "constante gravitationnelle", "igipimo cy'uburemere rusange", "kisimbuzi cha mvuto"),
    ("h", "6.626 × 10⁻³⁴ J·s", "Planck constant", "constante de Planck", "igipimo cya Planck", "kisimbuzi cha Planck"),
    ("k_B", "1.381 × 10⁻²³ J/K", "Boltzmann constant", "constante de Boltzmann", "igipimo cya Boltzmann", "kisimbuzi cha Boltzmann"),
    ("N_A", "6.022 × 10²³ /mol", "Avogadro constant", "constante d'Avogadro", "igipimo cya Avogadro", "kisimbuzi cha Avogadro"),
    ("R", "8.314 J/(mol·K)", "universal gas constant", "constante des gaz parfaits", "igipimo rusange cy'imyuka", "kisimbuzi cha gesi"),
    ("e", "1.602 × 10⁻¹⁹ C", "elementary charge", "charge élémentaire", "umubyigano w'ibanze", "chaji ya msingi"),
    ("ε₀", "8.854 × 10⁻¹² F/m", "permittivity of free space", "permittivité du vide", "permittivity y'icyuho", "ruhusa ya nafasi tupu"),
    ("μ₀", "4π × 10⁻⁷ T·m/A", "permeability of free space", "perméabilité du vide", "permeability y'icyuho", "upenyezaji wa nafasi tupu"),
    ("k", "8.988 × 10⁹ N·m²/C²", "Coulomb constant", "constante de Coulomb", "igipimo cya Coulomb", "kisimbuzi cha Coulomb"),
    ("σ", "5.670 × 10⁻⁸ W/(m²·K⁴)", "Stefan–Boltzmann constant", "constante de Stefan–Boltzmann", "igipimo cya Stefan–Boltzmann", "kisimbuzi cha Stefan–Boltzmann"),
    ("mₑ", "9.109 × 10⁻³¹ kg", "electron mass", "masse de l'électron", "ubuzito bwa electron", "wingi wa elektroni"),
    ("mₚ", "1.673 × 10⁻²⁷ kg", "proton mass", "masse du proton", "ubuzito bwa proton", "wingi wa protoni"),
    ("atm", "1.013 × 10⁵ Pa", "standard atmospheric pressure", "pression atmosphérique normale", "igitutu cy'ikirere gisanzwe", "shinikizo la kawaida la angahewa"),
    ("v_sound", "≈ 343 m/s (air, 20 °C)", "speed of sound in air", "vitesse du son dans l'air", "umuvuduko w'ijwi mu kirere", "kasi ya sauti hewani"),
]
_SI = {"en": "SI base units: metre (m, length), kilogram (kg, mass), second (s, time), ampere (A, current), kelvin (K, temperature), mole (mol, amount of substance), candela (cd, luminous intensity).",
       "fr": "Unités de base du SI : mètre (m, longueur), kilogramme (kg, masse), seconde (s, temps), ampère (A, courant), kelvin (K, température), mole (mol, quantité de matière), candela (cd, intensité lumineuse).",
       "rw": "Ibipimo by'ibanze bya SI: metero (m, uburebure), kilogramu (kg, ubuzito), isegonda (s, igihe), ampere (A, umuriro), kelvin (K, ubushyuhe), mole (mol, ingano y'ibintu), candela (cd, ubukana bw'urumuri).",
       "sw": "Vipimo vya msingi vya SI: mita (m, urefu), kilogramu (kg, wingi), sekunde (s, muda), ampere (A, mkondo), kelvin (K, halijoto), mole (mol, kiasi cha dutu), kandela (cd, mwangaza)."}


def constants(lang="en"):
    entry = {"id": "physics_constants", "related": [], "kind": "physics_list", "title": {}, "answer": {}, "steps": {}, "steps_label": {}, "priority": True}
    for i, l in enumerate(LANGS):
        u = _UI[l]
        entry["title"][l], entry["answer"][l] = u[3], u[4] + "\n\n" + _SI[l]
        entry["steps"][l] = [f"**{c[0]}** = {c[1]} — {c[2 + i]}" for c in _CONSTANTS]
        entry["steps_label"][l] = u[3]
    return entry


def find(question, lang="en"):
    """Guide-shaped entry for a physics-formula question, or None. Entries carry priority=True so they win over the general guide when the question names a formula."""
    q = (question or "").strip()
    if not q or len(q) > 160:
        return None
    raw = fold(q)
    text = _variants(raw)[0]
    alt = _variants(raw)[1]
    toks = text.split()
    tset = set(toks) | set(alt.split())
    if not toks or (tset & _BLOCK):
        return None
    has_form = bool(tset & _FORM) or "=" in q
    if (tset & _CONST) and (tset & _PHYS or "physical" in tset or "physics" in text) and len(toks) <= 8:
        return constants(lang)
    topic = next((t for t, ws in _TOPIC_WORDS.items() if tset & set(ws)), None)
    if has_form and (tset & _PHYS or tset & _LISTW or (topic and len(toks) <= 5)) and len(toks) <= 12:
        # one named formula wins over a topic list ("kinetic energy formula")
        for alias, fid in _INDEX:
            if len(alias.split()) >= 2 and (f" {alias} " in f" {text} " or f" {alias} " in f" {alt} "):
                return _entry(fid)
        return overview(lang, topic if topic and not (tset & _PHYS and tset & {"all", "every", "tous", "toutes", "byose", "yote"}) else None)
    padded, padded2 = f" {text} ", f" {alt} "
    for alias, fid in _INDEX:
        if f" {alias} " in padded or f" {alias} " in padded2:
            multi = len(alias.split()) >= 2
            if multi and (has_form or (tset & _CUES) or len(toks) <= 4):
                return _entry(fid)
            if has_form and len(toks) <= 10:
                return _entry(fid)
    return None
