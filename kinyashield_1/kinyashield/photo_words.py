"""Photos for any word: parse an explicit photo request ("photos of a lion", "montre-moi une photo de ...", "amafoto ya ...", "picha za ...")
and choose the best photo search term for an answered entry (its English title when the person wrote in another language).
Pure Python, no network here; the photos themselves come from images_db (Wikimedia Commons)."""
from __future__ import annotations
import re

_FR = r"(?:montre(?:z)?(?:-moi)?|affiche(?:z)?|donne(?:z)?(?:-moi)?|je veux|voir)\s+(?:des?\s+|les\s+|quelques\s+)?(?:photos?|images?)\s+(?:de la|de l'|de|du|des|d')\s*"
_EN = r"(?:(?:show|give|get|find|display|send)(?:\s+me)?(?:\s+some|\s+all)?\s+(?:photos?|pictures?|images?|pics?)\s+(?:of|for)|(?:photos?|pictures?|images?|pics?)\s+(?:of|for)|(?:show|display)\s+me)\s+"
_RW = r"(?:(?:ndeshya|nyereka|mpa|nshaka|erekana)\s+)?(?:amafoto|ifoto|amashusho|ishusho)\s+(?:ya|y'|za|z'|ry'|rya|ry|ku|kuri)\s*"
_SW = r"(?:(?:nionyeshe|onyesha|nipe|nataka)\s+)?(?:picha|taswira|foto)\s+(?:za|ya|ye|wa)\s+"
_FRAMES = re.compile(r"^\s*(?:" + "|".join([_EN, _FR, _RW, _SW]) + r")(?P<t>.+?)\s*[?!.]*\s*$", re.I)
_FR_BARE = re.compile(r"^\s*(?:photos?|images?)\s+(?:de la|de l'|de|du|des|d')\s*(?P<t>.+?)\s*[?!.]*\s*$", re.I)
_LEAD = re.compile(r"^(?:the|a|an|some|le|la|les|un|une|des)\s+", re.I)
_AI_WORDS = re.compile(r"\b(?:ai|ia|generate|generated|generation|create|draw|make)\b", re.I)


def explicit_term(question):
    """The word to photograph in an explicit photo request, else None. Rejects very long text and requests to generate images."""
    q = (question or "").strip()
    if not q or len(q) > 90 or "\n" in q:
        return None
    m = _FRAMES.match(q) or _FR_BARE.match(q)
    if not m:
        return None
    t = _LEAD.sub("", m.group("t").strip().strip("\"'")).strip()
    if not t or len(t.split()) > 5 or _AI_WORDS.search(t) or re.fullmatch(r"[\d\W_]+", t):
        return None
    return t


def search_term(entry, typed_term, lang="en"):
    """Best search term: a curated photo_query, else (for a non-English question) the entry's short English title, else the typed word."""
    if entry:
        if entry.get("photo_query"):
            return entry["photo_query"]
        title = ((entry.get("title") or {}).get("en") or "").strip()
        title = re.sub(r"\s*[\(\[].*?[\)\]]", "", title).strip(" :.-")
        if lang != "en" and title and 1 <= len(title.split()) <= 3 and not re.search(r"\d", title):
            return title
    return typed_term


NO_PHOTO = {"en": "No suitable free photo was found for “{t}”. Try another spelling or the English word.",
            "fr": "Aucune photo libre adaptée n'a été trouvée pour « {t} ». Essayez une autre orthographe ou le mot en anglais.",
            "rw": "Nta foto ikwiye yabonetse kuri «{t}». Gerageza indi nyandiko cyangwa ijambo mu Cyongereza.",
            "sw": "Hakuna picha huru inayofaa iliyopatikana kwa «{t}». Jaribu tahajia nyingine au neno la Kiingereza."}
HEAD = {"en": "Photos of **{t}**", "fr": "Photos de **{t}**", "rw": "Amafoto ya **{t}**", "sw": "Picha za **{t}**"}
