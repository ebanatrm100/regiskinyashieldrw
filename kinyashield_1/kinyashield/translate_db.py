"""Multilingual support (offline part): a phrasebook of everyday, farming, money and digital-safety phrases in English, French, Kinyarwanda and Kiswahili,
with the natural wording people actually use (not word-for-word) and short usage notes. Pure Python.
The phrasebook is a curated list, not a full translator: other texts go to the AI, which is told to translate for meaning and politeness.
Kinyarwanda and Kiswahili are a draft for review by a fluent speaker."""
from __future__ import annotations
import re
from textutil import fold, has_phrase, lk, entry, LANGS

NAMES = {"en": {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Swahili"},
         "fr": {"en": "anglais", "fr": "français", "rw": "kinyarwanda", "sw": "swahili"},
         "rw": {"en": "Icyongereza", "fr": "Igifaransa", "rw": "Ikinyarwanda", "sw": "Igiswahili"},
         "sw": {"en": "Kiingereza", "fr": "Kifaransa", "rw": "Kinyarwanda", "sw": "Kiswahili"}}
_ALIASES = {"en": ("english", "anglais", "icyongereza", "cyongereza", "kiingereza", "englais", "en"), "fr": ("french", "francais", "igifaransa", "gifaransa", "kifaransa", "fr"),
            "rw": ("kinyarwanda", "ikinyarwanda", "kinyarwand", "rwanda language", "rw", "kinya"), "sw": ("swahili", "kiswahili", "igiswahili", "giswahili", "swahili language", "sw")}

# (en, fr, rw, sw, note-en)
P = [
    ("Hello", "Bonjour", "Muraho", "Habari / Hujambo", "Greetings change with the time of day in Kinyarwanda (Mwaramutse = good morning, Mwiriwe = good afternoon/evening)."),
    ("Good morning", "Bonjour", "Mwaramutse", "Habari za asubuhi", ""),
    ("Good evening", "Bonsoir", "Mwiriwe", "Habari za jioni", ""),
    ("Good night", "Bonne nuit", "Murare neza", "Usiku mwema / Lala salama", ""),
    ("How are you?", "Comment allez-vous ?", "Amakuru?", "Habari yako? / U hali gani?", "In Kinyarwanda the usual answer is “Ni meza” (good). Use the plural “Mumeze mute?” for respect or several people."),
    ("I am fine", "Je vais bien", "Ndi muzima / Meze neza", "Sijambo / Nzuri", ""),
    ("Thank you", "Merci", "Murakoze / Urakoze", "Asante", "Murakoze is already polite (plural form); “Urakoze” is the informal singular."),
    ("Thank you very much", "Merci beaucoup", "Murakoze cyane", "Asante sana", ""),
    ("You are welcome", "De rien", "Nta kibazo / Ntacyo", "Karibu / Starehe", ""),
    ("Please", "S'il vous plaît", "Nyamuneka", "Tafadhali", ""),
    ("Excuse me", "Excusez-moi", "Mbabarira", "Samahani", "Also used for “sorry” in everyday speech."),
    ("I am sorry", "Je suis désolé(e)", "Mbabarira / Ndasaba imbabazi", "Samahani / Pole", "In Kiswahili “Pole” expresses sympathy (“sorry for your trouble”); “Samahani” apologises."),
    ("Yes", "Oui", "Yego", "Ndiyo", ""),
    ("No", "Non", "Oya", "Hapana", ""),
    ("Goodbye", "Au revoir", "Murabeho", "Kwa heri", ""),
    ("See you tomorrow", "À demain", "Ejo tuzabonana", "Tuonane kesho", ""),
    ("Welcome", "Bienvenue", "Murakaza neza", "Karibu / Karibuni", "Karibuni is the plural (several people)."),
    ("What is your name?", "Comment vous appelez-vous ?", "Witwa nde?", "Jina lako nani?", "For a respected person, Kiswahili: “Naomba kujua jina lako” (May I know your name)."),
    ("My name is ...", "Je m'appelle ...", "Nitwa ...", "Jina langu ni ...", ""),
    ("I don't understand", "Je ne comprends pas", "Sinumva", "Sielewi", ""),
    ("Please speak slowly", "Parlez lentement, s'il vous plaît", "Nyamuneka muvuge buhoro", "Tafadhali ongea polepole", ""),
    ("Please repeat", "Pouvez-vous répéter ?", "Mwabisubiramo?", "Tafadhali rudia", ""),
    ("Do you speak English?", "Parlez-vous anglais ?", "Mwavuga Icyongereza?", "Unaongea Kiingereza?", ""),
    ("Can you help me?", "Pouvez-vous m'aider ?", "Mwamfasha?", "Unaweza kunisaidia?", ""),
    ("I need help", "J'ai besoin d'aide", "Nkeneye ubufasha", "Ninahitaji msaada", ""),
    ("I am lost", "Je suis perdu(e)", "Nayobye", "Nimepotea", ""),
    ("Call the police", "Appelez la police", "Muhamagare Polisi", "Piga simu polisi", ""),
    ("I need a doctor", "J'ai besoin d'un médecin", "Nkeneye muganga", "Ninahitaji daktari", ""),
    ("Where is the toilet?", "Où sont les toilettes ?", "Ubwiherero buri he?", "Choo kiko wapi?", ""),
    ("Where is the bank?", "Où est la banque ?", "Banki iri he?", "Benki iko wapi?", ""),
    ("What time is it?", "Quelle heure est-il ?", "Ni saa ngahe?", "Ni saa ngapi?", ""),
    ("How much is this?", "Combien ça coûte ?", "Ibi ni angahe?", "Hii ni shilingi ngapi? / Bei gani?", "In shops you can also say “Ni angahe?” (How much?)."),
    ("It is too expensive", "C'est trop cher", "Birahenze cyane", "Ni ghali sana", ""),
    ("I would like to buy ...", "Je voudrais acheter ...", "Nshaka kugura ...", "Ningependa kununua ...", ""),
    ("Water", "Eau", "Amazi", "Maji", ""),
    ("Market", "Marché", "Isoko", "Soko", ""),
    ("I am hungry", "J'ai faim", "Ndashonje", "Nina njaa", ""),
    ("I am a farmer", "Je suis agriculteur / agricultrice", "Ndi umuhinzi / umuhinzi", "Mimi ni mkulima", ""),
    ("I am a student", "Je suis étudiant(e)", "Ndi umunyeshuri", "Mimi ni mwanafunzi", ""),
    ("Congratulations", "Félicitations", "Ndagushimiye", "Hongera", "In Kinyarwanda use “Mwishimiye” or “Ndabashimiye” for several people."),
    ("Happy birthday", "Joyeux anniversaire", "Isabukuru nziza", "Heri ya siku ya kuzaliwa", ""),
    ("Happy new year", "Bonne année", "Umwaka mushya muhire", "Heri ya mwaka mpya", ""),
    ("Good luck", "Bonne chance", "Amahirwe masa", "Bahati njema", ""),
    ("I agree", "Je suis d'accord", "Ndabyemeye", "Nakubali", ""),
    ("Never share your PIN", "Ne partagez jamais votre code PIN", "Ntuzigere usangiza undi muntu PIN yawe", "Usishiriki PIN yako na mtu yeyote kamwe", ""),
    ("Do not click suspicious links", "Ne cliquez pas sur les liens suspects", "Ntukande ku mirongo ikemangwa", "Usibofye viungo vinavyotia shaka", ""),
    ("Is this message real?", "Ce message est-il authentique ?", "Ubu butumwa ni ukuri?", "Je, ujumbe huu ni halisi?", ""),
    ("I will call you back", "Je vous rappelle", "Ndagusubiza kuri telefone", "Nitakupigia tena", ""),
    ("My phone number is ...", "Mon numéro de téléphone est ...", "Nomero yanjye ya telefone ni ...", "Namba yangu ya simu ni ...", ""),
]
try:  # the large curated bank (words, numbers, phrases, digital safety); rows already in P are not duplicated
    from translation_bank import BANK as _BANK
    _seen = {fold(r[0].split(" / ")[0]).strip(" ?.!") for r in P}
    P += [r for r in _BANK if fold(r[0].split(" / ")[0]).strip(" ?.!") not in _seen]
except ImportError:
    pass
try:  # more everyday words (food, animals, family, body, colours, numbers, time, places, transport, home, verbs); rows already present are not duplicated
    from translation_words_2 import WORDS as _WORDS2
    _seen = {fold(r[0].split(" / ")[0]).strip(" ?.!") for r in P}
    for _r in _WORDS2:
        _k = fold(_r[0].split(" / ")[0]).strip(" ?.!")
        if _k not in _seen:
            _seen.add(_k)
            P.append(_r)
except ImportError:
    pass
try:  # the word and short-phrase dictionary (computing, cybersecurity, money, school, work, everyday words); first entry wins
    from translation_words import WORDS as _WORDS
    _seen = {fold(r[0].split(" / ")[0]).strip(" ?.!") for r in P}
    for _r in _WORDS:
        _k = fold(_r[0].split(" / ")[0]).strip(" ?.!")
        if _k not in _seen:
            _seen.add(_k)
            P.append(_r)
except ImportError:
    pass


def _key(variant):
    v = fold(re.sub(r"\(.*?\)", "", variant)).strip(" ?.!,;:\"'")
    return re.sub(r"\s+", " ", v)


_NS = {l: {} for l in LANGS}                 # per language: folded text without spaces -> row number ("uri uwande" finds "uri uwa nde")
_INDEX = {}                                  # any language -> first row (kept for older callers)
_IDX = {l: {} for l in LANGS}                # per language: folded text -> row number
for i, row in enumerate(P):
    for j, l in enumerate(LANGS):
        for variant in row[j].split(" / "):
            keys = [_key(variant)]
            if l == "en" and keys[0].startswith("to ") and len(keys[0]) > 5:
                keys.append(keys[0][3:])          # "to hack" is also found as "hack"
            for key in keys:
                if key:
                    _INDEX.setdefault(key, i)
                    _IDX[l].setdefault(key, i)
                    _NS[l].setdefault(re.sub(r"[\s'’-]+", "", key), i)

_LAB = {"en": "Translations", "fr": "Traductions", "rw": "Ubusobanuro", "sw": "Tafsiri"}
_NOTE = {"en": "These are natural everyday phrases, not word-for-word translations. Kinyarwanda and Kiswahili are a draft: ask a fluent speaker to confirm important texts.",
         "fr": "Ce sont des phrases naturelles du quotidien, pas des traductions mot à mot. Le kinyarwanda et le swahili sont un brouillon : faites confirmer les textes importants par un locuteur.",
         "rw": "Ni interuro zisanzwe zikoreshwa, si ubusobanuro bw'ijambo ku rindi. Ikinyarwanda n'Igiswahili ni igerageza: saba umuvuga neza kwemeza inyandiko z'ingenzi.",
         "sw": "Hizi ni sentensi za kawaida za kila siku, si tafsiri neno kwa neno. Kinyarwanda na Kiswahili ni rasimu: mwombe mzungumzaji fasaha athibitishe maandishi muhimu."}
_NOTE_LAB = {"en": "Usage note", "fr": "Note d'usage", "rw": "Icyitonderwa", "sw": "Maelezo ya matumizi"}
_NOHIT = {"en": "I do not have that exact phrase in my phrasebook. For an accurate translation of your own text, tick “Always ask the AI”: it translates for meaning and politeness, and you should have important texts confirmed by a fluent speaker.",
          "fr": "Je n'ai pas cette phrase exacte dans mon lexique. Pour une traduction précise de votre texte, cochez « Toujours demander à l'IA » : elle traduit le sens et le niveau de politesse ; faites confirmer les textes importants.",
          "rw": "Iyi nteruro ntabwo iri mu gitabo cyanjye. Ushaka ubusobanuro nyabwo bw'inyandiko yawe, hitamo «Burigihe baza AI»: ibusobanura ku bw'ubusobanuro n'icyubahiro; saba kwemeza inyandiko z'ingenzi.",
          "sw": "Sina sentensi hiyo kamili kwenye kitabu changu. Kwa tafsiri sahihi ya maandishi yako, chagua «Muulize AI kila mara»: hutafsiri maana na heshima; thibitisha maandishi muhimu."}

_PATS = [
    re.compile(r"^(?:how (?:do|can) (?:you|i) say|how to say|how would you say|say|translate|translation of|what is|what's)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:in|into|to)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^(?:comment (?:dit|dire|on dit)[- ](?:on|t-on|ton)?|traduire|traduis|traduction de|comment dire)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:en|au|vers)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+(?:mu|bivuga iki mu|muri)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^(?:tafsiri|nitafsirie)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:kwa|kuwa|kwenda)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+(?:ni nini|kwa)\s+(?:kwa\s+)?(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+in\s+(?P<l>[a-z ]+?)\??$"),
]


def _lang_of(word):
    w = fold(word).strip()
    for code, al in _ALIASES.items():
        if w in {fold(a) for a in al}:
            return code
    return None


def _render(i, target, k):
    row = P[i]
    order = [target] + [l for l in LANGS if l != target] if target else list(LANGS)
    lines = []
    for l in order:
        lines.append(f"- **{NAMES[k][l]}**: {row[LANGS.index(l)]}")
    ans = "\n".join(lines)
    note = row[4]
    return ans, note


def find(question, lang="en"):
    """Phrasebook answer for 'how do you say X in Kinyarwanda' / 'X in French' / 'translate X to Swahili' / 'common phrases'; else None."""
    k = lk(lang)
    q = fold(question).strip(" ?.!")
    if not q or len(q) > 140:
        return None
    # phrasebook list
    if has_phrase(q, ["phrasebook", "common phrases", "useful phrases", "basic phrases", "everyday phrases", "greetings in kinyarwanda", "phrases en kinyarwanda", "phrases courantes", "expressions courantes",
                      "interuro zisanzwe", "interuro z'ingenzi", "misemo ya kawaida", "sentensi za kawaida", "misemo ya kila siku"]):
        lines = [f"- **{r[LANGS.index(k)]}**  ·  " + "  ·  ".join(f"{r[LANGS.index(l)]}" for l in LANGS if l != k) for r in P[:26]]
        ttl = {"en": "Common phrases in four languages", "fr": "Phrases courantes en quatre langues", "rw": "Interuro zisanzwe mu ndimi enye", "sw": "Misemo ya kawaida katika lugha nne"}
        ans = {l: "\n".join(lines) + "\n\n" + _NOTE[l] for l in LANGS}
        return entry("phrasebook", "translate", ttl, ans)
    for pat in _PATS:
        m = pat.match(q)
        if not m:
            continue
        target = _lang_of(m.group("l"))
        if target is None:
            continue
        res = translate(m.group("p"), target, k)
        if res is None:
            return None   # not in the bank: the AI (which translates for meaning) or the honest fallback handles it
        return render(res, k)
    return None


# ---------------------------------------------------------------------------------------------------------------------------
# Exact lookup of a phrase in the curated bank, from any of the four languages into any of them.
# A row is returned only when the text matches exactly (after removing punctuation, accents and a leading article), so nothing is guessed.
_ART = {"en": ("the ", "a ", "an "), "fr": ("le ", "la ", "les ", "l'", "un ", "une ", "des "), "rw": (), "sw": ()}


def _variants(text):
    base = _key(text)
    outs = [base]
    for arts in _ART.values():
        for a in arts:
            if base.startswith(a) and len(base) > len(a) + 1:
                outs.append(base[len(a):])
    if base.startswith("to ") and len(base) > 4:
        outs.append(base[3:])
    for v in list(outs):   # plurals: "apples" -> "apple", "berries" -> "berry", "buses" -> "bus" (only tried after the exact text)
        if len(v) > 3 and v.endswith("ies"):
            outs.append(v[:-3] + "y")
        if len(v) > 4 and v.endswith("es"):
            outs.append(v[:-2])
        if len(v) > 3 and v.endswith("s") and not v.endswith("ss"):
            outs.append(v[:-1])
    return list(dict.fromkeys(outs))


def match(phrase, source_hint=None, strict=False):
    """(row index, source language) for an exact bank match, else None. English is tried first, then the interface language, then the others.
    With strict=True the named source language is tried FIRST (the person said "from French")."""
    if strict and source_hint:
        order = [source_hint] + [l for l in ["en"] + list(LANGS) if l != source_hint]
        order = list(dict.fromkeys(order))
    else:
        order = ["en"] + [l for l in ([source_hint] if source_hint else []) if l != "en"] + [l for l in LANGS if l not in ("en", source_hint)]
    for l in order:
        for v in _variants(phrase):
            i = _IDX[l].get(v)
            if i is not None:
                return i, l
    for l in order:   # spacing and apostrophes ignored: "uri uwande" = "uri uwa nde", "ijambo ribanga" = "ijambo ry'ibanga" is NOT matched (letters differ)
        for v in _variants(phrase):
            v2 = re.sub(r"[\s'’-]+", "", v)
            if len(v2) >= 5:
                i = _NS[l].get(v2)
                if i is not None:
                    return i, l
    return None


def translate(phrase, target, ui_lang="en", source=None):
    """Dict with the main translation, the source language, the other languages and a usage note; or None when the phrase is not in the bank.
    source: the language the person named ("from French"); it is tried first."""
    hit = match(phrase, source, True) if source else match(phrase, lk(ui_lang))
    if hit is None:
        return None
    i, src = hit
    row = P[i]
    outs = {l: row[LANGS.index(l)] for l in LANGS}
    others = []   # the same spelling can be a different word in another language ("bibi": Kinyarwanda "bad", Kiswahili "grandmother"): show those readings too
    seen = {i}
    for l in LANGS:
        for v in _variants(phrase)[:1]:
            j = _IDX[l].get(v)
            if j is not None and j not in seen:
                seen.add(j)
                others.append({"row": j, "source": l, "text": {x: P[j][LANGS.index(x)] for x in LANGS}})
    return {"row": i, "source": src, "target": target, "text": outs, "note": row[4], "others": others[:2]}


def _words(text):
    return {w for w in re.split(r"[^a-z0-9']+", fold(text)) if len(w) > 2}


def suggest(phrase, n=3):
    """Closest bank rows (English side) sharing words with the phrase: shown when there is no exact match, so the person can see what is available."""
    ws = _words(phrase)
    if not ws:
        return []
    scored = []
    for i, row in enumerate(P):
        overlap = len(ws & _words(row[0]))
        if overlap:
            scored.append((overlap / (len(_words(row[0])) or 1), -len(row[0]), i))
    scored.sort(reverse=True)
    return [i for _, _, i in scored[:n]]


_BEST = {"en": "Translation", "fr": "Traduction", "rw": "Ubusobanuro", "sw": "Tafsiri"}
_ALSO = {"en": "Also in", "fr": "Aussi en", "rw": "No mu", "sw": "Pia kwa"}
_OTHER = {"en": "It can also mean", "fr": "Cela peut aussi signifier", "rw": "Bishobora no gusobanura", "sw": "Linaweza pia kumaanisha"}
_ASKED = {"en": "Source", "fr": "Texte d'origine", "rw": "Inyandiko y'ibanze", "sw": "Maandishi asilia"}
_MAYBE = {"en": "These are everyday translations written by hand, not machine output. Kinyarwanda and Kiswahili are a draft: ask a fluent speaker to confirm anything important.",
          "fr": "Ce sont des traductions courantes écrites à la main, pas une traduction automatique. Le kinyarwanda et le swahili sont un brouillon : faites confirmer ce qui est important.",
          "rw": "Ni ubusobanuro busanzwe bwanditswe n'intoki, si ubwa mudasobwa. Ikinyarwanda n'Igiswahili ni igerageza: saba umuvuga neza kwemeza ibiri ngombwa.",
          "sw": "Hizi ni tafsiri za kawaida zilizoandikwa kwa mkono, si za mashine. Kinyarwanda na Kiswahili ni rasimu: mwombe mzungumzaji fasaha athibitishe jambo muhimu."}


def render(result, ui_lang="en"):
    """Guide-shaped entry for a bank translation, written in the interface language."""
    t = result["target"]
    row = result["row"]
    out = {}
    for l in LANGS:
        first = lambda lang: result["text"][lang].split(" / ")[0]
        alts = result["text"][t].split(" / ")
        lines = [f"**{NAMES[l][t]}:** {alts[0]}"]
        if len(alts) > 1:
            lines.append("_" + " · ".join(alts[1:]) + "_")
        src = result["source"]
        if src != t:
            lines.append(f"{_ASKED[l]} ({NAMES[l][src]}): {first(src)}")
        others = [x for x in LANGS if x not in (t, src)]
        if others:
            lines.append(f"{_ALSO[l]}: " + "  ·  ".join(f"{NAMES[l][x]}: {first(x)}" for x in others))
        for o in result.get("others", []):
            lines.append(f"_{_OTHER[l]} ({NAMES[l][o['source']]}): “{o['text'][o['source']].split(' / ')[0]}” = {o['text'][t].split(' / ')[0]}_")
        if result["note"] and l == "en":
            lines.append(f"*{_NOTE_LAB[l]}:* {result['note']}")
        lines.append(f"_{_MAYBE[l]}_")
        out[l] = "\n\n".join(lines)
    title = {l: f"{_BEST[l]}: {result['text'][t].split(' / ')[0]}" for l in LANGS}
    return entry("translate_" + str(row), "translate", title, out)


def render_suggestions(phrase, rows, ui_lang="en"):
    """Honest 'not in my bank' answer with the closest entries."""
    lines = {}
    for l in LANGS:
        head = {"en": "I do not have a checked translation of this in my bank, and I will not guess. Closest entries I do have:",
                "fr": "Je n'ai pas de traduction vérifiée de ceci dans mon lexique, et je ne vais pas deviner. Entrées les plus proches :",
                "rw": "Nta busobanuro bwemejwe bw'iyi nyandiko mfite mu gitabo cyanjye, kandi sinshaka kuvuga ibitari byo. Ibyegereye mfite:",
                "sw": "Sina tafsiri iliyothibitishwa ya hili kwenye kitabu changu, na sitakisia. Maingizo yaliyo karibu zaidi:"}[l]
        body = "\n".join("- " + "  ·  ".join(f"{P[i][LANGS.index(x)].split(' / ')[0]}" for x in LANGS) for i in rows)
        tail = {"en": "For a full translation of your own text, tick “Always ask the AI” (needs the AI key) or ask a fluent speaker.",
                "fr": "Pour une traduction complète de votre texte, cochez « Toujours demander à l'IA » (clé IA requise) ou demandez à un locuteur.",
                "rw": "Ushaka ubusobanuro bwuzuye bw'inyandiko yawe, hitamo «Burigihe baza AI» (bisaba urufunguzo rwa AI) cyangwa ubaze umuvuga neza.",
                "sw": "Kwa tafsiri kamili ya maandishi yako, chagua «Muulize AI kila mara» (inahitaji ufunguo wa AI) au mwombe mzungumzaji fasaha."}[l]
        lines[l] = head + ("\n\n" + body if body else "") + "\n\n" + tail
    title = {"en": "No checked translation", "fr": "Pas de traduction vérifiée", "rw": "Nta busobanuro bwemejwe", "sw": "Hakuna tafsiri iliyothibitishwa"}
    return entry("translate_none", "translate", title, lines)


def breakdown(phrase, target):
    """Word-by-word help for a sentence that is not in the bank: [(piece of the sentence, translation)] for every word or short phrase the dictionary knows.
    This is NOT a sentence translation (grammar, word order and endings differ between the languages); it only gives the meaning of the pieces that are known."""
    toks = [t for t in re.split(r"\s+", (phrase or "").strip()) if t]
    out, i = [], 0
    while i < len(toks):
        hit = None
        for n in range(min(4, len(toks) - i), 0, -1):
            piece = " ".join(toks[i:i + n])
            m = match(piece)
            if m is not None:
                row = P[m[0]]
                tr = row[LANGS.index(target)].split(" / ")[0].rstrip(" ?!.")
                if _key(piece) != _key(tr):
                    hit = (piece.strip(" ?.!,;:\"'"), tr, n)
                break
        if hit:
            out.append(hit[:2])
            i += hit[2]
        else:
            i += 1
    return out
