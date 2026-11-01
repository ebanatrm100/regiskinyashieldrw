"""What is the user actually asking for? Pure Python, English / French / Kinyarwanda / Kiswahili.
The offline guides and Wikipedia look-ups answer DEFINITION questions ("what is phishing"). They must not answer other kinds of request just because a keyword matched:
  * "example"  : "give me an example", "mpa urugero", "nipe mfano"       -> the AI gives concrete examples
  * "followup" : "explain more", "why?", "give me an example of this"     -> the AI answers about the previous topic, using the conversation
  * "events"   : "cybercrimes that happened this week", "latest news"     -> real, dated results (Cyber News engine for cyber topics, AI with live search otherwise)
  * "period"   : the user just answered a "which period?" question        -> continues that news request
classify() returns None for ordinary questions, which keep the normal route."""
from __future__ import annotations
import re
from textutil import fold

_EXAMPLE = re.compile(
    r"\bexamples?\b|\bfor (?:instance|example)\b|\bsamples?\b|\bcase stud(?:y|ies)\b|\breal (?:cases?|stories|life)\b|\bshow me one\b|"
    r"\bexemples?\b|\bpar exemple\b|\bcas (?:reels?|concrets?)\b|\bun cas\b|"
    r"\burugero\b|\bingero\b|\bingero z\w+\b|\bdosiye y'urugero\b|\bmfano\b|\bmifano\b|\bmatukio halisi\b", re.I)
_FOLLOW = re.compile(
    r"^(?:ok(?:ay)?[ ,]+|and |so |please |now |then )?(?:"
    r"(?:give|show|tell|send) me (?:an? |some |one |more |another |other )*(?:example|examples|one|more|details?|info|detail)(?: (?:of|about|for|on) (?:this|that|it|these|those|the same))?|"
    r"(?:an? )?(?:example|examples)(?: (?:of|about|for) (?:this|that|it|these|those))?|another(?: one| example)?|more(?: examples| details| info| please)?|again|"
    r"explain(?: (?:this|that|it|them|these|those))?(?: (?:more|further|again|better|simply|in detail|in simple words|clearly))?|elaborate|go on|continue|carry on|"
    r"why(?: is that| is it| so| does that happen)?|how(?: so| come| does (?:it|that|this) work)?|what do you mean|what does (?:this|that|it) mean|"
    r"in (?:simple|simpler|plain) (?:words|terms)|simpler|shorter|longer|more detail|in detail|summari[sz]e(?: (?:this|that|it))?|translate(?: (?:this|that|it))?|"
    r"(?:and )?what about (?:the )?(?:other|next|rest)|what next|what should i do(?: then| now)?|is (?:it|that|this) (?:true|real|dangerous|safe)|"
    r"donne(?:z)?(?:-moi)? (?:un |des |encore un |d'autres )?(?:exemple|exemples|details?|plus)(?: (?:de|sur) (?:ceci|cela|ça|ca|ce|tout ça))?|un exemple(?: (?:de|sur) (?:ceci|cela|ça|ca))?|encore(?: un exemple)?|"
    r"plus(?: de d[ée]tails| d'exemples)?|explique(?:z)?(?:-moi)?(?: (?:ça|ca|cela|ceci))?(?: (?:plus|mieux|encore|simplement|en d[ée]tail))?|pourquoi(?: ça| cela)?|comment ça|continue(?:z)?|r[ée]sume(?: (?:ça|ca|cela))?|traduis(?: (?:ça|ca|cela))?|"
    r"mpa urugero(?: (?:rwa|rw'|kuri) (?:ibi|iki|ibyo|icyo))?|urugero(?: rwa (?:ibi|iki|ibyo))?|mpa ingero|ongera(?: ibindi)?|ibindi|komeza|bisobanure(?: neza| birambuye)?|sobanura(?: neza| byinshi| birambuye)?|mbwira byinshi|kubera iki|byakorwa bite|"
    r"nipe mfano(?: wa (?:hili|hii|haya|hiki))?|mfano(?: wa (?:hili|hii|haya))?|zaidi|nipe zaidi|eleza(?: zaidi| vizuri| kwa urahisi)?|kwa nini(?: hivyo)?|endelea|fupisha(?: hili| hii)?|tafsiri(?: hili| hii)?"
    r")[?!. ]*$", re.I)
_TIME = re.compile(
    r"\b(?:today|tonight|yesterday|this (?:week|month|year)|last (?:week|month|year|\d+ (?:days?|weeks?|months?))|past (?:\d+ )?(?:days?|weeks?|months?)|these days|recently|lately|right now|currently|"
    r"aujourd'hui|hier|cette (?:semaine|annee)|ce mois|(?:la )?semaine derniere|(?:le )?mois dernier|ces derniers jours|recemment|en ce moment|"
    r"uyu munsi|ejo hashize|iki cyumweru|icyumweru gishize|uku kwezi|ukwezi gushize|uyu mwaka|umwaka ushize|mu minsi ishize|vuba aha|ubu|"
    r"leo|jana|wiki hii|wiki iliyopita|mwezi huu|mwezi uliopita|mwaka huu|mwaka uliopita|siku hizi|hivi karibuni|sasa hivi)\b", re.I)
_EVENT_WORDS = re.compile(
    r"\b(?:happen\w*|occurr?\w*|took place|reported|news|incidents?|cases?|\w*attacks?|breach\w*|arrests?|events?|latest|recent|cybercrimes?|scams?|frauds?|hacks?|what(?:'s| is) new|updates?|trending|statistics|stats|"
    r"s'est passe|se sont passes|ont eu lieu|a eu lieu|\w*attaques?|arriv\w+|actualites?|incidents?|cas|attaques?|arrestations?|derniers?|derniere\w*|nouveau\w*|"
    r"byabaye|byabaye|amakuru|ibyaha|ibitero|byafashwe|abafashwe|bishya|bishya|byagaragaye|"
    r"yaliyotokea|yalitokea|habari|matukio|mashambulizi|uhalifu|mapya|ya hivi karibuni)\b", re.I)
_LIST_ASK = re.compile(r"^(?:tell|give|show|list|what|which|any|are there|is there|report|find|get|search|dis|donne|montre|liste|quels?|quelles?|y a-t-il|mbwira|mpa|nyereka|ni ibihe|ni iki|hari|niambie|nipe|nionyeshe|orodhesha|ni zipi|je,)", re.I)
_CYBER = re.compile(r"cyber|hack|ransom|phish|malware|breach|data leak|scam|fraud|mobile money|sim swap|spyware|botnet|ddos|vulnerab|exploit|zero-?day|security|securit|arnaque|fraude|piratage|rancon|hameconn|"
                    r"umutekano|ibyaha|uburiganya|ubujura|ibitero|interineti|ulaghai|udukuzi|usalama|uhalifu|mtandao|mashambulizi|shambulio|wahalifu|uvujaji|programu hasidi|kuvuja", re.I)
_QUESTIONISH = re.compile(r"\b(?:what|which|who|how|when|where|why|tell|give|show|list|any|are|is|do|does|can)\b|\?$|^(?:quels?|quelles?|qui|comment|quand|ou|pourquoi|donne|dis|montre|ni|mbwira|mpa|nyereka|niambie|nipe|nionyeshe)\b", re.I)


def _last_turns(history):
    u = a = None
    for m in reversed(list(history or [])):
        c = str(m.get("content", "")).strip()
        if not c:
            continue
        if m.get("role") == "assistant" and a is None:
            a = m
        elif m.get("role") == "user" and u is None:
            u = m
        if u and a:
            break
    return u, a


def _previous_topic(history):
    """The last real question the user asked before this message (skipping bare follow-ups), or ''."""
    msgs = [m for m in (history or []) if m.get("role") == "user" and str(m.get("content", "")).strip()]
    for m in reversed(msgs):
        c = str(m["content"]).strip()
        if not _FOLLOW.match(fold(c)) and len(c) > 3:
            return c[:240]
    return ""


def classify(q: str, lang: str = "en", history=None):
    """None for an ordinary question, else {'intent': 'period'|'followup'|'example'|'events', 'topic': previous topic, 'cyber': bool, ...}."""
    raw = (q or "").strip()
    if not raw or len(raw) > 220 or "\n" in raw:
        return None
    f = fold(raw)
    words = len(f.split())
    hist = list(history or [])
    _u, last_a = _last_turns(hist)
    # 1. the answer to our "which period?" question
    ctx = (last_a or {}).get("news_ctx")
    if ctx:
        import cyber_intel as ci
        per = ci.parse_time(raw)
        if per is None:
            import cyber_upcoming as cu
            per = cu.parse_future(raw)
        if per is not None and words <= 8:
            return {"intent": "period", "news_ctx": ctx, "period": per}
    # 2. events / news in a time frame ("cybercrimes that happened this week")
    if (_TIME.search(f) or re.search(r"\b(?:latest|recent|news|actualites?|amakuru mashya|habari mpya|nouveautes?)\b", f)) and _EVENT_WORDS.search(f) and (_QUESTIONISH.search(raw) or _LIST_ASK.match(f) or words <= 7):
        return {"intent": "events", "cyber": bool(_CYBER.search(f)), "topic": _previous_topic(hist)}
    # 3. a bare follow-up that depends on the conversation
    if hist and last_a is not None and _FOLLOW.match(f):
        return {"intent": "example" if _EXAMPLE.search(f) else "followup", "topic": _previous_topic(hist), "last_answer": str(last_a.get("content", ""))[:400]}
    # 4. any request for examples (with or without a named subject)
    if _EXAMPLE.search(f) and words <= 16 and (_QUESTIONISH.search(raw) or _LIST_ASK.match(f) or words <= 8):
        anaphoric = bool(re.search(r"\b(?:this|that|it|these|those|ceci|cela|ca|ce|ibi|iki|ibyo|icyo|hili|hii|haya|hiyo)\b", f))
        return {"intent": "example", "topic": _previous_topic(hist) if (anaphoric or words <= 4) else "", "last_answer": str((last_a or {}).get("content", ""))[:400] if (anaphoric or words <= 4) else ""}
    return None


def resolve(q: str, info: dict, lang: str = "en") -> str:
    """The question to send to the AI: the user's words plus what they refer to, and an instruction to do exactly what was asked."""
    topic = info.get("topic") or ""
    ask = {"example": "The user wants concrete EXAMPLES. Give 2 to 4 clear, realistic examples (invented ones marked as examples, real ones only if you are sure), not a definition.",
           "followup": "This is a follow-up to the conversation. Answer exactly what is asked about the previous topic; do not restart with a definition.",
           "events": "The user wants specific recent events or news for the time they named. Answer with dated, specific items; if you cannot confirm real current events, say so plainly and tell them where to check; do not replace the answer with a definition."}[info["intent"]]
    return f"{q}\n\n[Instruction from the app: {ask}" + (f" The previous topic of the conversation was: \"{topic}\"." if topic else "") + (f" Your previous answer started: \"{info['last_answer']}\"." if info.get("last_answer") else "") + "]"
