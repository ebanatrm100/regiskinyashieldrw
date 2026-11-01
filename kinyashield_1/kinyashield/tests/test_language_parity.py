"""Whatever the assistant does for an English request must also happen for the same request in French, Kinyarwanda and Kiswahili."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import assistant_flow as F
import image_gen as G
import photo_words as P

def kind(q, l):
    if G.parse_request(q): return "draw"
    if P.explicit_term(q): return "photo"
    d = F.route(q, l)
    e = d.get("entry") or {}
    return d["kind"] if d["kind"] != "guide" else e.get("id", "")

CASES = [  # (what it should do, {lang: request})
    ("draw", {"en": "Draw a cat on a roof", "fr": "Dessine un chat sur un toit", "rw": "Kora ishusho y'injangwe ku gisenge", "sw": "Chora picha ya paka juu ya paa"}),
    ("photo", {"en": "Show me photos of a lion", "fr": "Montre-moi des photos d'un lion", "rw": "Nyereka amafoto y'intare", "sw": "Nionyeshe picha za simba"}),
    ("translate", {"en": "Translate 'good morning my friend' into French", "fr": "Traduis « bonjour mon ami » en swahili", "rw": "Hindura 'mwaramutse nshuti yanjye' mu Cyongereza", "sw": "Tafsiri 'habari za asubuhi rafiki' kwa Kinyarwanda"}),
    ("tutor_quiz", {"en": "Quiz me on cybersecurity", "fr": "Fais-moi un quiz sur la cybersécurité", "rw": "Mbaza ibibazo bya cybersecurity", "sw": "Nipime maswali ya usalama wa mtandao"}),
    ("tutor_lin", {"en": "Solve 2x + 6 = 14", "fr": "Résous 2x + 6 = 14", "rw": "Kemura 2x + 6 = 14", "sw": "Tatua 2x + 6 = 14"}),
    ("tpl_cv", {"en": "Help me write a CV", "fr": "Aide-moi à écrire un CV", "rw": "Mfasha kwandika CV", "sw": "Nisaidie kuandika wasifu CV"}),
    ("ai", {"en": "Tell me a joke", "fr": "Raconte-moi une blague", "rw": "Mbwira urwenya", "sw": "Niambie utani"}),
    ("ai", {"en": "Give me a recipe for ugali", "fr": "Donne-moi une recette d'ugali", "rw": "Mpa uburyo bwo guteka ubugali", "sw": "Nipe mapishi ya ugali"}),
    ("ai", {"en": "What is the weather in Kigali today?", "fr": "Quel temps fait-il à Kigali aujourd'hui ?", "rw": "Ikirere i Kigali uyu munsi kimeze gute?", "sw": "Hali ya hewa Kigali leo ikoje?"}),
]
bad = []
for want, qs in CASES:
    for l, q in qs.items():
        got = kind(q, l)
        if got != want:
            bad.append((l, q[:40], want, got))
# an e-mail request must give an e-mail / letter template in every language, never a scam guide
for l, q in {"en": "Write an email asking my boss for leave", "fr": "Écris un e-mail pour demander un congé à mon patron",
             "rw": "Ndandikira umukoresha wanjye ibaruwa isaba ikiruhuko", "sw": "Niandikie barua pepe ya kuomba likizo kwa bosi wangu"}.items():
    if not kind(q, l).startswith("tpl_"):
        bad.append((l, q[:40], "tpl_*", kind(q, l)))
assert not bad, bad
print("OK language parity", sum(len(q) for _, q in CASES) + 4, "requests")
