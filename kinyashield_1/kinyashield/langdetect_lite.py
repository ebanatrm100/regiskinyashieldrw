"""Small offline language detector for the four supported languages (English, French, Kinyarwanda, Kiswahili).
It counts distinctive everyday words; a word used by two languages ("ni", "na") gives each a half vote. It returns None when it is not sure,
so the app then keeps the interface language. Heuristic, not a trained model: short or mixed messages may be left undetected."""
from __future__ import annotations
import re
from textutil import fold

_W = {
    "en": "the is are was were what whats how why who where when which can could would should do does did you your my me we our this that these those with for and of to in on at from about "
          "please help write explain translate give tell show have has had not it its be been will hello hi hey good morning thanks thank sorry yes i am i'm don't isn't there here also any some more "
          "make create need want know like use using",
    "fr": "le la les des une est sont que qui quoi comment pourquoi quel quelle quels quand ou je tu il elle nous vous ils mon ma mes ton ta tes pour avec dans sur pas et ce cette ces c'est qu'est "
          "d'un l'on du au aux ne plus mais donc bonjour bonsoir merci salut svp aide moi toi suis es sommes etes avoir etre faire peut peux veux voudrais besoin sans chez entre apres avant de en un mot passe choisir traduis traduire traduit explique expliquer ecris ecrire",
    "rw": "ni nde iki iyi uyu uru ubu mu ku ko ngo kuki gute ute he ryari angahe ingahe nshaka ndashaka mfasha mbwira sobanura nkeneye murakoze urakoze muraho mwaramutse mwiriwe amakuru ibi ibyo "
          "byose cyangwa kandi ariko kubera nta ntabwo ntibyemewe nkore nte mbese reka yego oya konti ubutumwa amafaranga telefone interineti ijambo ibanga ubufasha nyabuneka uri wowe njye twe "
          "bo bari ndi turi muri uwa uwo icyo iyo aho uko ryo rwa bya cya mwese abantu umuntu igihe kugira gukora kuba kubona kumenya gushaka hindura humura andika",
    "sw": "wa ya za kwa na katika kwamba nini nani wapi lini vipi gani naomba nataka nisaidie eleza tafadhali asante habari jambo sana hii huu hiki yangu wako yako kuhusu kuna sina hakuna mimi wewe "
          "yeye sisi ninyi wao ni sio si je kwa nini pia lakini kama au ndiyo hapana akaunti ujumbe pesa simu mtandao nenosiri msaada samahani karibu rafiki kila kitu mtu watu wakati kufanya kuwa kuona kujua kutaka tafsiri fasiri andika",
}
_VOTES: dict[str, dict[str, float]] = {}
for _l, _words in _W.items():
    for _w in _words.split():
        _VOTES.setdefault(fold(_w).replace("'", ""), {})[_l] = 1.0
for _tok, _d in _VOTES.items():
    for _l in _d:
        _d[_l] = 1.0 / len(_d)

MIN_EVIDENCE = 1.0      # at least this many votes for the winner
MIN_SHARE = 0.6        # and at least this share of all votes


def scores(text: str) -> dict:
    out = {l: 0.0 for l in _W}
    for tok in re.split(r"[^a-z0-9']+", fold(text)):
        tok = tok.replace("'", "")
        if len(tok) < 1:
            continue
        for l, v in _VOTES.get(tok, {}).items():
            out[l] += v
    return out


def detect(text: str):
    """(language code or None, share of the votes won by that language)."""
    sc = scores(text)
    total = sum(sc.values())
    if total <= 0:
        return None, 0.0
    best = max(sc, key=sc.get)
    return best, sc[best] / total


_COMMANDS = {"fr": {"traduis", "traduire", "traduisez", "traduction"}, "rw": {"hindura", "humura"}, "sw": {"tafsiri", "fasiri", "nitafsirie"}}


def detect_confident(text: str):
    """Language code only when the evidence is clear; otherwise None. A message that starts with a translate command ("traduis ...", "tafsiri ...")
    is in that command's language even when the text to translate is English."""
    first = (fold(text).split() or [""])[0]
    for l, words in _COMMANDS.items():
        if first in words:
            return l
    best, share = detect(text)
    if best is None:
        return None
    sc = scores(text)
    if sc[best] >= MIN_EVIDENCE and share >= MIN_SHARE:
        return best
    return None
