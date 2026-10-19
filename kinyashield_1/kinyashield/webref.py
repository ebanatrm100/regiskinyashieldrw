"""Look up almost any word or topic in Wikipedia (en/fr/rw/sw) and, for English words, Wiktionary.
Used by the AI Assistant when a question is just a word or short topic that the offline banks do not cover.
Needs internet; every failure returns None and the chat carries on. Nothing is invented: text and links come from the source.
Wikipedia/Wiktionary text is CC BY-SA 4.0, so the source link is always shown."""
from __future__ import annotations
import html
import json
import re
import threading
import urllib.parse
import urllib.request
from functools import lru_cache

UA = "KinyaShieldRW/1.0 (https://regiskinyashieldrw.streamlit.app; educational safety assistant)"
TIMEOUT = 6
WIKI = {"en": "en", "fr": "fr", "rw": "rw", "sw": "sw"}
MAX_WORDS = 6

# Question frames removed to find the word or topic. Longest first.
_FRAMES = [
    r"give me (?:all |full |complete )?(?:the )?(?:information|info|details|facts) (?:about|on)", r"tell me (?:everything )?(?:about|more about)", r"what (?:is|are|was|were)(?:\s+(?:a|an|the))?",
    r"who (?:is|was|are|were)", r"what does(?:\s+the word)?", r"(?:the )?meaning of", r"(?:the )?definition of", r"define", r"explain(?: to me)?", r"describe", r"information (?:about|on)",
    r"qu'est-?ce que c'est(?:\s+que)?", r"qu'est-?ce qu(?:e|')\s*(?:est|c'est)?", r"c'est quoi", r"qui (?:est|etait)", r"(?:la )?definition de", r"(?:le )?sens de", r"explique(?:z)?(?:-moi)?", r"parle(?:z)?-moi de", r"informations? sur",
    r"(?:ni )?iki(?:ki)? ?ni iki", r"(?:ni )?iki", r"(?:ni )?nde", r"busobanura iki", r"sobanura", r"mbwira(?: byinshi)? kuri", r"amakuru (?:ku|kuri|kuri)", r"icyo (?:bisobanura|bivuze)",
    r"ni nini", r"nini maana ya", r"maana ya", r"ni nani", r"eleza", r"nieleze(?: kuhusu)?", r"niambie (?:kuhusu|habari za)", r"habari kuhusu",
]
_FRAME_RE = re.compile(r"^\s*(?:" + "|".join(_FRAMES) + r")\s+", re.I)
_TAIL_RE = re.compile(r"\s+(?:mean|means|meaning|stand for|stands for|signifie|bisobanura|maana|inamaanisha|ni iki|ni nde|ni nini|ni nani|\?)\s*$", re.I)
_NOT_A_TERM = re.compile(r"\b(?:how (?:do|can|to|should)|why|when|where|can you|could you|please (?:help|write)|write me|create|make me|translate|solve|calculate|compare|difference between|vs\.?)\b", re.I)


def extract_term(question: str):
    """The word or short topic the user is asking about, or None when the message is a real question or a task."""
    q = (question or "").strip().strip("?!.\"' ").strip()
    if not q or len(q) > 80 or "\n" in q:
        return None
    if _NOT_A_TERM.search(q):
        return None
    for _ in range(2):
        q2 = _FRAME_RE.sub("", q).strip()
        if q2 == q:
            break
        q = q2
    q = _TAIL_RE.sub("", q).strip().strip("?!.\"' ").strip()
    q = re.sub(r"^(?:the|a|an|le|la|les|un|une)\s+", "", q, flags=re.I)
    if not q or len(q.split()) > MAX_WORDS or re.fullmatch(r"[\d\W_]+", q):
        return None
    return q


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 (fixed https hosts only)
        return json.loads(r.read().decode("utf-8", "replace"))


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = html.unescape(text)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()


def wikipedia(term: str, lang: str = "en"):
    """{'title','extract','url','lang','ambiguous'} for the best Wikipedia match, or None."""
    host = WIKI.get(lang, "en")
    params = {"action": "query", "format": "json", "redirects": 1, "generator": "search", "gsrsearch": term, "gsrlimit": 3,
              "gsrnamespace": 0, "prop": "extracts|pageprops|info", "exintro": 1, "explaintext": 1, "exlimit": 3, "exchars": 2600,
              "inprop": "url", "ppprop": "disambiguation"}
    data = _get(f"https://{host}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    pages = [p for p in pages if (p.get("extract") or "").strip()]
    if not pages:
        return None
    top = pages[0]
    amb = "disambiguation" in (top.get("pageprops") or {})
    pick = top
    if amb:
        alt = [p for p in pages if "disambiguation" not in (p.get("pageprops") or {})]
        pick = alt[0] if alt else top
    return {"title": pick.get("title", term), "extract": _clean(pick["extract"]), "url": pick.get("fullurl") or f"https://{host}.wikipedia.org/wiki/" + urllib.parse.quote(pick.get("title", term).replace(" ", "_")),
            "lang": host, "ambiguous": amb}


def wiktionary(term: str):
    """English dictionary entries: [(part_of_speech, [definitions])] or None. Single English words only."""
    if " " in term.strip() or not re.fullmatch(r"[A-Za-z'-]{2,40}", term.strip()):
        return None
    data = _get("https://en.wiktionary.org/api/rest_v1/page/definition/" + urllib.parse.quote(term.strip().lower()))
    out = []
    for block in data.get("en", [])[:4]:
        defs = [_clean(d.get("definition", "")) for d in block.get("definitions", [])[:3]]
        defs = [d for d in defs if d]
        if defs:
            out.append((block.get("partOfSpeech", ""), defs))
    return out or None


@lru_cache(maxsize=512)
def lookup(term: str, lang: str = "en"):
    """Combine both sources. Returns dict(term, wiki, dictionary) or None when nothing was found. Never raises."""
    res = {"wiki": None, "dict": None}

    def run(name, fn):
        try:
            res[name] = fn()
        except Exception:
            res[name] = None

    threads = [threading.Thread(target=run, args=("wiki", lambda: wikipedia(term, lang)))]
    if lang == "en":
        threads.append(threading.Thread(target=run, args=("dict", lambda: wiktionary(term))))
    for t in threads:
        t.start()
    for t in threads:
        t.join(TIMEOUT + 2)
    if res["wiki"] is None and lang != "en":           # small wikis lack many topics: fall back to English
        try:
            res["wiki"] = wikipedia(term, "en")
        except Exception:
            res["wiki"] = None
    if not res["wiki"] and not res["dict"]:
        return None
    return {"term": term, "wiki": res["wiki"], "dict": res["dict"]}


LABELS = {
    "en": dict(dict="Dictionary", about="About", src="Source", note="Check important facts with an official or specialist source.", amb="This word has several meanings; this is the closest match. Add a few more words to be specific.",
               en_fb="No page in your language was found, so this is from English Wikipedia.", lic="Text from Wikipedia/Wiktionary, CC BY-SA 4.0."),
    "fr": dict(dict="Dictionnaire", about="À propos", src="Source", note="Vérifiez les faits importants auprès d'une source officielle ou spécialisée.", amb="Ce mot a plusieurs sens ; voici la correspondance la plus proche. Ajoutez quelques mots pour préciser.",
               en_fb="Aucune page dans votre langue n'a été trouvée ; ceci vient de Wikipédia en anglais.", lic="Texte de Wikipédia/Wiktionnaire, CC BY-SA 4.0."),
    "rw": dict(dict="Inkoranyamagambo", about="Ibisobanuro", src="Isoko", note="Genzura amakuru y'ingenzi mu isoko ryemewe cyangwa ry'inzobere.", amb="Iri jambo rifite ibisobanuro byinshi; iki ni cyo cyegereye. Ongeraho amagambo make kugira ngo ugaragaze icyo ushaka.",
               en_fb="Nta paji mu rurimi rwawe yabonetse, bityo ibi bivuye kuri Wikipedia y'Icyongereza.", lic="Umwandiko wa Wikipedia/Wiktionary, CC BY-SA 4.0."),
    "sw": dict(dict="Kamusi", about="Kuhusu", src="Chanzo", note="Thibitisha ukweli muhimu na chanzo rasmi au cha kitaalamu.", amb="Neno hili lina maana kadhaa; hii ndiyo inayokaribia zaidi. Ongeza maneno machache kubainisha.",
               en_fb="Hakuna ukurasa kwa lugha yako, hivyo hii ni kutoka Wikipedia ya Kiingereza.", lic="Maandishi kutoka Wikipedia/Wiktionary, CC BY-SA 4.0."),
}


def format_answer(info: dict, lang: str = "en") -> str:
    """Plain, sourced answer used when no AI key is available (and as the reference text for the AI)."""
    L = LABELS.get(lang, LABELS["en"])
    parts = [f"## {info['term']}"]
    if info.get("dict"):
        parts.append(f"**{L['dict']}**")
        for pos, defs in info["dict"]:
            parts.append(f"*{pos}*")
            parts += [f"{i}. {d}" for i, d in enumerate(defs, 1)]
    w = info.get("wiki")
    if w:
        parts.append(f"**{L['about']}: {w['title']}**")
        parts.append(w["extract"])
        if w["ambiguous"]:
            parts.append(f"_{L['amb']}_")
        if w["lang"] != WIKI.get(lang, "en"):
            parts.append(f"_{L['en_fb']}_")
        parts.append(f"{L['src']}: [{w['title']} - Wikipedia]({w['url']})")
    parts.append(f"_{L['lic']} {L['note']}_")
    return "\n\n".join(parts)


def reference_text(info: dict) -> str:
    """Plain text handed to the AI as reference material."""
    bits = []
    if info.get("dict"):
        bits += [f"{pos}: " + "; ".join(defs) for pos, defs in info["dict"]]
    if info.get("wiki"):
        bits.append(f"Wikipedia ({info['wiki']['title']}): {info['wiki']['extract']}")
    return "\n".join(bits)[:6000]


def source_line(info: dict, lang: str = "en"):
    w = info.get("wiki")
    if not w:
        return ""
    L = LABELS.get(lang, LABELS["en"])
    return f"\n\n{L['src']}: [{w['title']} - Wikipedia]({w['url']}) · _{L['lic']}_"
