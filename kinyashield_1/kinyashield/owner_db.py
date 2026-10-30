"""Owner question for the AI Assistant: "Who is your owner?" / "Who owns you?" in English, French, Kinyarwanda and Kiswahili.
Pure Python, no Streamlit. The answer is fixed text supplied by the project owner. The question is answered in the language it was asked in
(or the chat language if that cannot be told). fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import re, unicodedata

NAME = "Regis TWIRINGIYIMANA"
LANGS = ("en", "fr", "rw", "sw")
ANSWER = {
    "en": f"My owner is **{NAME}**, a Cybersecurity and Infrastructure Security Engineer and a specialist in Cybersecurity.",
    "fr": f"Mon propriétaire est **{NAME}**, ingénieur en cybersécurité et en sécurité des infrastructures, et spécialiste en cybersécurité.",
    "rw": f"Nyirinjye ni **{NAME}**, injeniyeri w'umutekano wa interineti n'ibikorwaremezo (Cybersecurity and Infrastructure Security Engineer) akaba n'inzobere mu mutekano wa interineti (Cybersecurity).",
    "sw": f"Mmiliki wangu ni **{NAME}**, Mhandisi wa Usalama wa Mtandao na Miundombinu (Cybersecurity and Infrastructure Security Engineer) na mtaalamu wa Usalama wa Mtandao (Cybersecurity).",
}
TITLE = {"en": "My owner", "fr": "Mon propriétaire", "rw": "Nyirinjye", "sw": "Mmiliki wangu"}

# words that say "owner / owns" and words that point at the assistant ("you", "your", "this app"), per language
_OWN = {
    "en": {"owner", "owners", "owns", "own", "owned", "ownership", "proprietor"},
    "fr": {"proprietaire", "proprietaires", "possede", "appartiens", "appartient", "possedes"},
    "rw": {"nyirawe", "nyirinjye", "nyiri", "nyirubwite", "nyirabyo", "nyirayo", "nyirarwo", "nyirubwenge"},
    "sw": {"mmiliki", "anakumiliki", "akumiliki", "anamiliki", "umiliki", "mwenyewe"},
}
_POINT = {"you", "your", "yours", "this", "assistant", "app", "ai", "bot", "kinyashield", "kinyashield's",
          "ton", "ta", "tes", "votre", "vos", "vous", "te", "tu", "t'", "wawe", "wako", "ako", "yako", "uru", "iyi", "huyu", "hii"}
_ASK = {"who", "whom", "qui", "nde", "nani", "ninde", "ni", "is", "est", "ndiye"}


def _fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


def asked_language(question):
    """Return the language code if the question asks who owns the assistant, else None."""
    text = _fold(question)
    if not text or len(text) > 120:
        return None
    toks = set(re.split(r"[' \-]+", text)) | set(text.split())
    if len(text.split()) > 12:
        return None
    for lang, words in _OWN.items():
        if toks & words:
            if toks & _POINT or (lang == "rw" and toks & {"nyirawe", "nyirinjye"}) or (lang == "sw" and toks & {"anakumiliki", "akumiliki"}):
                return lang
    if re.search(r"\buri uwa nde\b|\bqui t'a (cree|fait|developpe|concu|programme|construit)\b|\bqui t'a donne naissance\b", text):
        return "rw" if "uri uwa" in text else "fr"
    # who created / made / built you
    if re.search(r"\bwho (created|made|built|developed|designed|programmed|invented|is behind|is the creator of|is the developer of|is the author of) (you|this app|this assistant|kinyashield)\b|\bwho is your (creator|developer|maker|author)\b", text):
        return "en"
    if re.search(r"\bqui (est|sont) (ton|votre) (createur|developpeur|concepteur)\b|\bqui a (cree|developpe|concu|fabrique|programme) (cette application|cet assistant|kinyashield)\b", text):
        return "fr"
    if re.search(r"\bni nde (wakwiyubatse|wagukoze|waguhanze|wagukoreye|wagushyizeho|wakoze iyi porogaramu|wakoze kinyashield)\b|\bnde wakwubatse\b|\bnde wagukoze\b|\bumuremyi wawe ni nde\b|\bwakuremye ni nde\b", text):
        return "rw"
    if re.search(r"\bnani (alikuunda|alikutengeneza|alikuumba|aliyekuunda|aliyekutengeneza|alikubuni|alikuandika)\b|\bmuundaji wako ni nani\b|\bmtengenezaji wako ni nani\b|\bnani aliyeunda (programu hii|kinyashield)\b", text):
        return "sw"
    return None


def find(question, lang="en"):
    """Guide-shaped entry with the owner answer, in the language the question was asked in (or `lang` if that is the same / unknown)."""
    asked = asked_language(question)
    if asked is None:
        return None
    entry = {"id": "owner", "related": [], "kind": "owner", "title": {}, "answer": {}, "steps": {}, "steps_label": {}}
    for l in LANGS:
        use = asked if l == (lang if lang in LANGS else "en") else l   # shown in the chat language ...
        entry["title"][l], entry["answer"][l], entry["steps"][l], entry["steps_label"][l] = TITLE[l], ANSWER[l], [], ""
    entry["answer"][lang if lang in LANGS else "en"] = ANSWER[asked]   # ... but answered in the language it was asked in
    entry["title"][lang if lang in LANGS else "en"] = TITLE[asked]
    return entry
