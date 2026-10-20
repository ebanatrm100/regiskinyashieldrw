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
        if info.get("closest"):
            parts.append(f"_{closest_note(lang)}_")
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


# ---------------------------------------------------------------- names, closest match, honest fallback
_NAME_RE = re.compile(r"(?:\bname|\bnames|\bprenom|\bprénom|\bnom|\bizina|\bamazina|\bjina|\bmajina)\s+[\"'“«]?(?P<n>[^\s?.!,\"'”»]+)", re.I)
_NAME_STOP = {"mean", "means", "meaning", "of", "is", "for", "called", "the", "a", "an", "and", "or", "that", "this", "in", "my", "your", "his", "her", "to", "what", "who",
              "signifie", "ni", "ry", "rya", "ni", "kuri", "ya", "wa", "la", "le", "du", "de"}


def extract_name(question: str):
    """The given name being asked about ('meaning of the name Regis' -> 'Regis'), or None."""
    q = (question or "").strip()
    if not q or len(q) > 120:
        return None
    for m in _NAME_RE.finditer(q):
        n = m.group("n").strip("-'")
        if 2 <= len(n) <= 30 and n.lower() not in _NAME_STOP and n.isalpha():
            return n[:1].upper() + n[1:]
    return None


@lru_cache(maxsize=256)
def lookup_name(name: str, lang: str = "en"):
    """Wikipedia 'given name' page and English Wiktionary entry for a first name. Returns the same shape as lookup() or None."""
    res = {"wiki": None, "dict": None}

    def w():
        try:
            for q in (f"{name} given name", f"{name} (name)"):
                page = wikipedia(q, lang if lang in WIKI else "en")
                if page and name.lower() in page["title"].lower():
                    res["wiki"] = page
                    return
            if lang != "en":
                page = wikipedia(f"{name} given name", "en")
                if page and name.lower() in page["title"].lower():
                    res["wiki"] = page
        except Exception:
            pass

    def d():
        try:
            res["dict"] = wiktionary(name)
        except Exception:
            pass

    ts = [threading.Thread(target=w), threading.Thread(target=d)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(TIMEOUT + 2)
    if not res["wiki"] and not res["dict"]:
        return None
    return {"term": name, "wiki": res["wiki"], "dict": res["dict"], "name": True}


@lru_cache(maxsize=256)
def closest_match(question: str, lang: str = "en"):
    """Best Wikipedia match for a whole question (used only when nothing better exists). Marked 'closest' so the answer says it may not fit."""
    q = re.sub(r"\s+", " ", (question or "").strip().strip("?!. "))
    if not q or len(q.split()) > 18:
        return None
    try:
        page = wikipedia(q, lang if lang in WIKI else "en") or (wikipedia(q, "en") if lang != "en" else None)
    except Exception:
        return None
    if not page or page["ambiguous"]:
        return None
    return {"term": page["title"], "wiki": page, "dict": None, "closest": True}


_CLOSEST = {"en": "This is the closest match I found for your question. It may not answer exactly what you asked.",
            "fr": "Voici la correspondance la plus proche trouvée pour votre question. Elle peut ne pas répondre exactement à ce que vous demandez.",
            "rw": "Iki ni cyo cyegereye cyane nabonye ku kibazo cyawe. Gishobora kudasubiza neza icyo wabajije.",
            "sw": "Hiki ndicho kinacholingana zaidi nilichopata kwa swali lako. Huenda kisijibu hasa ulichouliza."}
_NONAME = {"en": "I could not find a reliable source for the meaning of this name. Name meanings often differ by language and family, so ask someone from that culture, or tell me the language it comes from.",
           "fr": "Je n'ai pas trouvé de source fiable pour le sens de ce prénom. Les sens varient selon la langue et la famille ; demandez à quelqu'un de cette culture ou dites-moi sa langue d'origine.",
           "rw": "Ntabashije kubona isoko yizewe ku bisobanuro by'iri zina. Ibisobanuro by'amazina biratandukana bitewe n'ururimi n'umuryango; baza umuntu wo muri uwo muco, cyangwa umbwire ururimi rikomokamo.",
           "sw": "Sikupata chanzo cha kuaminika kuhusu maana ya jina hili. Maana za majina hutofautiana kwa lugha na familia; muulize mtu wa utamaduni huo, au niambie lugha inayotoka."}
NO_ANSWER = {
    "en": "I do not have an answer to that yet, and the online AI service is not available right now.\n\nWhat usually works:\n- Ask about one word or topic (for example “tomato” or “inflation”): I can look it up and show photos.\n- Ask about phones, scams, passwords, physics formulas, names, writing templates or practice quizzes.\n- Paste a suspicious message in the Check tab.\n- Try again later for open questions that need the AI.",
    "fr": "Je n'ai pas encore de réponse à cela, et le service d'IA en ligne n'est pas disponible pour le moment.\n\nCe qui marche généralement :\n- Demandez un mot ou un sujet (par exemple « tomate » ou « inflation ») : je peux le chercher et montrer des photos.\n- Posez des questions sur les téléphones, les arnaques, les mots de passe, les formules de physique, les prénoms, les modèles de rédaction ou les quiz.\n- Collez un message suspect dans l'onglet Vérifier.\n- Réessayez plus tard pour les questions ouvertes qui demandent l'IA.",
    "rw": "Nta gisubizo ndagira kuri ibyo ubu, kandi serivisi ya AI yo kuri interineti ntiboneka ubu.\n\nIbikunze gukora:\n- Baza ijambo rimwe cyangwa isomo (urugero «inyanya» cyangwa «inflation»): nshobora kurishakisha nkakwereka amafoto.\n- Baza ku matelefone, uburiganya, amagambo y'ibanga, formula za fizike, amazina, inyandikorugero cyangwa ibizamini byo kwitoza.\n- Shyira ubutumwa bukemangwa mu gice cya «Genzura».\n- Ongera ugerageze nyuma ku bibazo bifunguye bikeneye AI.",
    "sw": "Sina jibu kwa hilo bado, na huduma ya AI mtandaoni haipatikani sasa.\n\nKinachofanya kazi kwa kawaida:\n- Uliza neno moja au mada (mfano «nyanya» au «inflation»): naweza kulitafuta na kuonyesha picha.\n- Uliza kuhusu simu, utapeli, nywila, fomula za fizikia, majina, violezo vya uandishi au maswali ya mazoezi.\n- Bandika ujumbe wa kutia shaka kwenye kichupo cha Hakiki.\n- Jaribu tena baadaye kwa maswali huru yanayohitaji AI.",
}


def no_answer(lang="en"):
    return NO_ANSWER.get(lang, NO_ANSWER["en"])


def no_name(lang="en"):
    return _NONAME.get(lang, _NONAME["en"])


def closest_note(lang="en"):
    return _CLOSEST.get(lang, _CLOSEST["en"])


_NOLOOKUP = {"en": "I could not look up “{t}” right now. The lookup needs an internet connection and may be busy. Please try again in a moment; I will then show the meaning, a source and photos.",
             "fr": "Je n'ai pas pu rechercher « {t} » pour le moment. La recherche demande une connexion internet et peut être occupée. Réessayez dans un instant ; je montrerai alors le sens, une source et des photos.",
             "rw": "Ntabashije gushakisha «{t}» ubu. Gushakisha bisaba interineti kandi bishobora kuba byuzuye. Ongera ugerageze nyuma gato; nzakwereka ibisobanuro, isoko n'amafoto.",
             "sw": "Sikuweza kutafuta «{t}» sasa hivi. Utafutaji unahitaji mtandao na unaweza kuwa na shughuli nyingi. Jaribu tena baadaye kidogo; nitaonyesha maana, chanzo na picha."}


def no_lookup(term, lang="en"):
    return _NOLOOKUP.get(lang, _NOLOOKUP["en"]).format(t=term)
