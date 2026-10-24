"""Offline tools from the Question Answering and Research Guide: `interpret: ...` (task, constraints, ambiguity), `research plan: ...` (is it time-sensitive,
search queries, source checks), `rag demo: question ||| passage ||| passage` (a tiny retrieval-then-ground demo). Pure Python, four languages.
These are teaching aids using keyword rules: they do not search the web and do not judge truth."""
from __future__ import annotations
import math, re
from textutil import fold, entry, LANGS

_T = lambda en, fr, rw, sw: {"en": en, "fr": fr, "rw": rw, "sw": sw}


def _out(id_, title, body):
    return entry(id_, "ai_lab", title, body if isinstance(body, dict) else {l: body for l in LANGS})


def _kw(s):
    return [fold(x) for x in s.split("|")]


TASKS = [
    ("translation", _T("translation", "traduction", "ubuhinduzi", "tafsiri"), _kw("translate|traduis|traduire|hindura|tafsiri|ubuhinduzi")),
    ("code", _T("code", "code", "code", "msimbo"), _kw("code|python|javascript|function|bug|script|program|programme|porogaramu|msimbo")),
    ("calculation", _T("calculation", "calcul", "kubara", "hesabu"), _kw("calculate|compute|how much|how many|total|percent|calcule|combien|bara|hesabu|ngapi|asilimia|\\d+\\s*[\\+\\-\\*/x]\\s*\\d+")),
    ("creative", _T("creative work", "création", "guhanga", "ubunifu"), _kw("write a poem|story|poem|song|slogan|imagine|poeme|histoire|ikinyoma|igisigo|hadithi|shairi")),
    ("advice", _T("advice", "conseil", "inama", "ushauri"), _kw("should i|what should|advice|recommend|dois-je|conseil|nakagombye|inama|nifanye|ushauri|nifanye nini")),
    ("explanation", _T("explanation", "explication", "ibisobanuro", "maelezo"), _kw("explain|how does|how do|why|what is|what are|explique|comment|pourquoi|qu'est|sobanura|kuki|ni iki|eleza|kwa nini|ni nini")),
    ("factual", _T("factual question", "question factuelle", "ikibazo cy'ukuri", "swali la ukweli"), _kw("who|when|where|which|how old|qui|quand|ou |quel|nde|ryari|he |gani|lini|wapi")),
    ("action", _T("action", "action", "igikorwa", "kitendo"), _kw("send|book|schedule|remind|open|create a file|envoie|reserve|rappelle|ohereza|nibutsa|tuma|kumbusha")),
]
TIME = _kw("today|now|current|currently|latest|newest|recent|this week|this year|tonight|price|prices|cost|open now|available|is still|aujourd'hui|maintenant|actuel|actuellement|dernier|derniere|prix|disponible|uyu munsi|ubu|none|vuba|igiciro|leo|sasa|hivi sasa|bei|ya hivi karibuni|inapatikana")
PLACE = _kw("in rwanda|in kigali|in africa|in my country|near me|au rwanda|a kigali|en afrique|mu rwanda|i kigali|nchini rwanda|kigali|karibu nami|hano")
VAGUE = _kw("it|this|that|those|them|he|she|ce|ca|cela|ceci|il|elle|ils|icyo|iyi|iki|yo|huyu|huyo|hicho|hii|hiyo")
FORMAT = [
    (_kw("table|tableau|imbonerahamwe|jedwali"), _T("a table", "un tableau", "imbonerahamwe", "jedwali")),
    (_kw("steps|step by step|etapes|pas a pas|intambwe|hatua"), _T("numbered steps", "des étapes numérotées", "intambwe zibaze", "hatua zenye namba")),
    (_kw("list|liste|urutonde|orodha|bullet"), _T("a list", "une liste", "urutonde", "orodha")),
    (_kw("short|brief|briefly|summary|summarize|court|bref|resume|ngufi|incamake|fupi|muhtasari"), _T("a short answer", "une réponse courte", "igisubizo kigufi", "jibu fupi")),
    (_kw("detailed|in detail|detaille|en detail|birambuye|kwa kina"), _T("a detailed answer", "une réponse détaillée", "igisubizo kirambuye", "jibu la kina")),
    (_kw("code block|code|script"), _T("code", "du code", "code", "msimbo")),
]
LANGREQ = [("English", _kw("in english|en anglais|mu cyongereza|kwa kiingereza")), ("French", _kw("in french|en francais|mu gifaransa|kwa kifaransa")),
           ("Kinyarwanda", _kw("in kinyarwanda|en kinyarwanda|mu kinyarwanda|kwa kinyarwanda")), ("Kiswahili", _kw("in swahili|in kiswahili|en swahili|mu giswahili|kwa kiswahili"))]
AUD = [(_kw("for kids|for a child|for children|pour les enfants|ku bana|kwa watoto"), _T("children", "enfants", "abana", "watoto")),
       (_kw("beginner|beginners|for beginners|debutant|abatangiye|wanaoanza|simple terms|simple words"), _T("beginners", "débutants", "abatangiye", "wanaoanza")),
       (_kw("expert|experts|technical|expert|ab'inzobere|wataalamu"), _T("experts", "experts", "inzobere", "wataalamu"))]
_WORDS = re.compile(r"\b(?:in|en|mu|kwa|within|under)?\s*(\d{1,4})\s*(?:words|mots|amagambo|maneno|sentences|phrases|interuro|sentensi|lines|lignes)\b", re.I)


def _any(q, kws):
    return any(k in q for k in kws)


def _pad(s):
    return " " + fold(s) + " "


def interpret(text, lang="en"):
    q = _pad(text)
    task = next((t for t in TASKS if any((re.search(k, q) if "\\" in k else (" " + k.strip() + " " in q or q.strip().startswith(k.strip()) if len(k.strip()) <= 4 else k in q)) for k in t[2])), None)
    tname = task[1][lang] if task else _T("general request", "demande générale", "icyifuzo rusange", "ombi la jumla")[lang]
    cons = []
    for kws, name in FORMAT:
        if _any(q, kws):
            cons.append(("format", name[lang]))
    for name, kws in LANGREQ:
        if _any(q, kws):
            cons.append(("language", name))
    for kws, name in AUD:
        if _any(q, kws):
            cons.append(("audience", name[lang]))
    m = _WORDS.search(text)
    if m:
        cons.append(("length", m.group(0).strip()))
    words = fold(text).split()
    vague = len(words) <= 5 and any(w in VAGUE for w in words)
    time_ = _any(q, TIME)
    place = _any(q, PLACE)
    L = {"en": ("Task", "Constraints found", "none found", "Ambiguity", "Looks clear enough to answer.", "Very short and refers to something not named (“it/this/that”): I would use the earlier conversation, or ask which thing you mean.", "Strategy", "Time-sensitive: a search or a dated source is needed; do not answer from memory alone.", "Location matters: check the answer for the right country.", "Answer directly from general knowledge, then say how sure you are.", "Interpreting is a rule-based illustration, not a full understanding."),
         "fr": ("Tâche", "Contraintes trouvées", "aucune", "Ambiguïté", "Semble assez clair pour répondre.", "Très court et renvoie à une chose non nommée (« ça/ce/cela ») : j'utiliserais la conversation précédente, ou je demanderais de quoi il s'agit.", "Stratégie", "Sensible au temps : il faut une recherche ou une source datée ; ne pas répondre de mémoire seulement.", "Le lieu compte : vérifier la réponse pour le bon pays.", "Répondre directement avec les connaissances générales, puis dire le degré de certitude.", "L'interprétation est une illustration à règles, pas une compréhension complète."),
         "rw": ("Umurimo", "Imbogamizi zabonetse", "nta zibonetse", "Ibitumvikana", "Bisa n'ibisobanutse bihagije gusubiza.", "Ni ngufi cyane kandi rivuga ikintu kitavuzwe izina («iki/iyo/ibyo»): nakoresha ikiganiro cyabanje, cyangwa nkabaza ikintu ushaka kuvuga.", "Uburyo", "Bishingiye ku gihe: hakenewe gushakisha cyangwa inkomoko ifite itariki; ntusubize mu bwenge bwonyine.", "Aho biri ni ngombwa: genzura igisubizo ku gihugu gikwiye.", "Subiza ako kanya mu bumenyi rusange, hanyuma uvuge uko wizeye.", "Gusobanura ni urugero rukoresha amategeko, si ugusobanukirwa byuzuye."),
         "sw": ("Kazi", "Vikwazo vilivyopatikana", "hakuna", "Utata", "Inaonekana wazi vya kutosha kujibu.", "Ni fupi sana na inarejea kitu kisichotajwa («hiki/hicho/hilo»): ningetumia mazungumzo ya awali, au kuuliza unamaanisha kipi.", "Mkakati", "Inategemea wakati: utafutaji au chanzo chenye tarehe kinahitajika; usijibu kwa kumbukumbu pekee.", "Mahali ni muhimu: hakiki jibu kwa nchi sahihi.", "Jibu moja kwa moja kwa maarifa ya jumla, kisha sema una uhakika kiasi gani.", "Ufasiri ni kielelezo cha kanuni, si uelewa kamili.")}[lang]
    lines = [f"**{L[0]}:** {tname}", f"**{L[1]}:** " + ("; ".join(f"{k}: {v}" for k, v in cons) if cons else L[2]),
             f"**{L[3]}:** {L[5] if vague else L[4]}", "", f"**{L[6]}:**"]
    if time_:
        lines.append("- " + L[7])
    if place:
        lines.append("- " + L[8])
    if not time_ and not place:
        lines.append("- " + L[9])
    lines += ["", f"_{L[10]}_"]
    return _out("qa_interpret_tool", _T("Question interpreter", "Interprétation de la question", "Gusobanura ikibazo", "Ufasiri wa swali"), "\n".join(lines))


_STOP = set(fold("""the a an of to in on for and or is are was were be it this that with as at by from what which who how when where why do does did can could should
le la les un une des de du et ou est sont ce cela avec pour dans sur par que qui quoi comment quand ou pourquoi
ni na mu ku ya wa za ry'u kuri iki ute ryari he ngo
ya wa za kwa ni na katika hii hiyo gani nini lini wapi""").split())


def _words(s):
    return [w for w in re.findall(r"[a-z0-9']+", fold(s)) if w not in _STOP and len(w) > 1]


def plan(text, lang="en"):
    q = _pad(text)
    ws = _words(text)
    core = " ".join(ws[:8])
    time_ = _any(q, TIME)
    place = _any(q, PLACE)
    L = {"en": ("Research plan", "Time-sensitive?", "yes: freshness matters, so check dates", "no: stable knowledge may be enough, but verify important claims", "Location-dependent?", "yes", "no", "Search queries to try", "official", "latest", "Source checks", "Prefer official, primary and recent sources.", "Open the page: does it really support the claim? Check date, scope and limits.", "Compare two or more sources if facts conflict.", "Cite sources next to the claims; if evidence is missing or conflicting, say so.", "This app cannot search for you here; use these steps with a search tool or a trusted website."),
         "fr": ("Plan de recherche", "Sensible au temps ?", "oui : la fraîcheur compte, vérifiez les dates", "non : des connaissances stables peuvent suffire, mais vérifiez les points importants", "Dépend du lieu ?", "oui", "non", "Requêtes à essayer", "officiel", "dernier", "Vérification des sources", "Préférez des sources officielles, primaires et récentes.", "Ouvrez la page : soutient-elle vraiment l'affirmation ? Vérifiez date, portée et limites.", "Comparez deux sources ou plus si les faits se contredisent.", "Citez les sources à côté des affirmations ; si les preuves manquent ou se contredisent, dites-le.", "Cette application ne peut pas chercher pour vous ici ; suivez ces étapes avec un outil de recherche ou un site de confiance."),
         "rw": ("Gahunda yo gushakisha", "Bishingiye ku gihe?", "yego: igihe gifite akamaro, genzura amatariki", "oya: ubumenyi buhamye bushobora gukwira, ariko genzura iby'ingenzi", "Bishingiye ku hantu?", "yego", "oya", "Ibibazo byo gushakisha", "official", "latest", "Kugenzura inkomoko", "Hitamo inkomoko yemewe, y'ibanze kandi nshya.", "Fungura urupapuro: rushyigikira koko ibivugwa? Reba itariki, ubwo bugari n'imbibi.", "Gereranya inkomoko ebyiri cyangwa nyinshi iyo amakuru ahabanye.", "Tanga inkomoko iruhande rw'ibivugwa; niba ibimenyetso bibura cyangwa bihabanye, ubivuge.", "Iyi porogaramu ntishobora gushakisha hano; kurikiza izi ntambwe ukoresheje igikoresho cyo gushakisha cyangwa urubuga rwizewe."),
         "sw": ("Mpango wa utafiti", "Inategemea wakati?", "ndiyo: upya ni muhimu, hakiki tarehe", "hapana: maarifa thabiti yanaweza kutosha, lakini hakiki mambo muhimu", "Inategemea mahali?", "ndiyo", "hapana", "Maswali ya utafutaji ya kujaribu", "rasmi", "mpya", "Ukaguzi wa vyanzo", "Pendelea vyanzo rasmi, vya msingi na vipya.", "Fungua ukurasa: unaunga mkono dai kweli? Angalia tarehe, wigo na mipaka.", "Linganisha vyanzo viwili au zaidi ukweli ukigongana.", "Taja vyanzo karibu na madai; ushahidi ukikosekana au ukigongana, sema.", "Programu hii haiwezi kukutafutia hapa; fuata hatua hizi kwa zana ya utafutaji au tovuti ya kuaminika.")}[lang]
    if not core:
        return None
    qs = [core, f"{core} {L[8]}"] + ([f"{core} {L[9]}"] if time_ else []) + ([f"{core} Rwanda"] if place and "rwanda" not in core else [])
    lines = [f"**{L[1]}** " + (L[2] if time_ else L[3]), f"**{L[4]}** " + (L[5] if place else L[6]), "", f"**{L[7]}:**"] + [f"- `{x}`" for x in qs] + ["", f"**{L[10]}:**"] + [f"- {L[i]}" for i in (11, 12, 13, 14)] + ["", f"_{L[15]}_"]
    return _out("qa_plan_tool", _T("Research plan", "Plan de recherche", "Gahunda yo gushakisha", "Mpango wa utafiti"), "\n".join(lines))


def rag(text, lang="en"):
    parts = [p.strip() for p in text.split("|||")]
    if len(parts) < 3 or not all(parts):
        msg = _T("Use: `rag demo: your question ||| passage one ||| passage two ||| passage three`", "Utilisez : `rag demo: votre question ||| passage un ||| passage deux ||| passage trois`",
                 "Koresha: `rag demo: ikibazo cyawe ||| igice cya mbere ||| igice cya kabiri ||| igice cya gatatu`", "Tumia: `rag demo: swali lako ||| kifungu cha kwanza ||| kifungu cha pili ||| kifungu cha tatu`")
        return _out("qa_rag_tool", _T("RAG demo", "Démo RAG", "Urugero rwa RAG", "Onyesho la RAG"), msg)
    qw, passages = set(_words(parts[0])), parts[1:9]
    docs = [_words(p) for p in passages]
    n = len(docs)
    df = {}
    for d in docs:
        for w in set(d):
            df[w] = df.get(w, 0) + 1
    scored = []
    for i, d in enumerate(docs):
        s = sum((1 + math.log((n + 1) / (df.get(w, 0) + 0.5))) for w in qw if w in d) / math.sqrt(len(d) + 1)
        scored.append((s, i))
    scored.sort(reverse=True)
    best = scored[0]
    L = {"en": ("Question", "Retrieval ranking (keyword overlap, a simple stand-in for vector search)", "score", "Grounded answer (built only from the best passage)", "No passage shares meaningful words with the question: a grounded assistant should say it found no support rather than guess.", "Check: retrieval may pick the wrong passage and a model can still misread a correct one. Always read the source."),
         "fr": ("Question", "Classement de récupération (mots communs, simple substitut de la recherche vectorielle)", "score", "Réponse fondée (construite uniquement à partir du meilleur passage)", "Aucun passage ne partage de mots significatifs avec la question : un assistant fondé doit dire qu'il n'a trouvé aucun appui plutôt que deviner.", "Vérification : la récupération peut choisir le mauvais passage et un modèle peut mal lire un bon passage. Lisez toujours la source."),
         "rw": ("Ikibazo", "Urutonde rwo gushakisha (amagambo ahuriweho, isimbura yoroheje ya vector search)", "amanota", "Igisubizo gishingiye ku nkomoko (gikozwe gusa mu gice cyiza)", "Nta gice gihuje amagambo y'ingenzi n'ikibazo: umufasha ushingiye ku nkomoko agomba kuvuga ko nta shyigikiro yabonye aho gukeka.", "Genzura: gushakisha bishobora guhitamo igice kitari cyo kandi icyitegererezo gishobora gusoma nabi igice cyiza. Soma inkomoko buri gihe."),
         "sw": ("Swali", "Orodha ya urejeshaji (maneno yanayofanana, mbadala rahisi ya utafutaji wa vekta)", "alama", "Jibu linalotegemea chanzo (limejengwa kwa kifungu bora pekee)", "Hakuna kifungu kinachoshiriki maneno muhimu na swali: msaidizi anayetegemea chanzo anapaswa kusema hakupata msaada badala ya kubahatisha.", "Hakiki: urejeshaji unaweza kuchagua kifungu kisicho sahihi na modeli bado inaweza kusoma vibaya kifungu sahihi. Soma chanzo kila mara.")}[lang]
    lines = [f"**{L[0]}:** {parts[0]}", "", f"**{L[1]}:**"]
    for rank, (s, i) in enumerate(scored, 1):
        lines.append(f"{rank}. [{i + 1}] {L[2]} {s:.2f}: {passages[i][:110]}{'…' if len(passages[i]) > 110 else ''}")
    lines += ["", f"**{L[3]}:**", ""]
    lines += [f"> {passages[best[1]]} [{best[1] + 1}]" if best[0] > 0 else L[4]]
    lines += ["", f"_{L[5]}_"]
    return _out("qa_rag_tool", _T("RAG demo", "Démo RAG", "Urugero rwa RAG", "Onyesho la RAG"), "\n".join(lines))


_CMD = re.compile(r"^\s*(interpret|interpreter|interpréter|sobanura ikibazo|fasiri swali)\s*:\s*(.+)$|^\s*(research plan|plan de recherche|gahunda yo gushakisha|mpango wa utafiti)\s*:\s*(.+)$|^\s*(rag demo|démo rag|demo rag)\s*:\s*(.+)$", re.I | re.S)


def find(question, lang="en"):
    t = (question or "").strip()
    if not t or len(t) > 1500:
        return None
    m = _CMD.match(t)
    if not m:
        return None
    if m.group(2):
        return interpret(m.group(2).strip(), lang)
    if m.group(4):
        return plan(m.group(4).strip(), lang)
    return rag(m.group(6).strip(), lang)
