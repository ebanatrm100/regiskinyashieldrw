"""Per-session usage counters and an optional fair-use limit on AI answers (pure Python; the caller passes st.session_state).
Set AI_MESSAGES_PER_SESSION in the app secrets to limit AI answers per browser session (0 or empty = unlimited). Offline answers are never limited.
This is a fair-use guard and a measurement aid, NOT billing: a visitor can reload the page to start a new session, and nothing is stored on a server.
Real quotas, logins and payments need a database and an authentication service."""
from __future__ import annotations
import settings

KEY = "kinyashield_usage"

CAPTION = {"en": "This session: {off} offline answers, {ai} AI answers{lim}", "fr": "Cette session : {off} réponses hors ligne, {ai} réponses IA{lim}",
           "rw": "Muri iri somo: ibisubizo {off} bidakoresha interineti, ibisubizo {ai} bya AI{lim}", "sw": "Kipindi hiki: majibu {off} ya nje ya mtandao, majibu {ai} ya AI{lim}"}
OVER = {"en": "You have reached the limit of {n} AI answers for this session. Offline answers, the message checker and the other tabs still work. Reload the page to start a new session.",
        "fr": "Vous avez atteint la limite de {n} réponses IA pour cette session. Les réponses hors ligne, le vérificateur de messages et les autres onglets fonctionnent toujours. Rechargez la page pour une nouvelle session.",
        "rw": "Wageze ku mubare ntarengwa w'ibisubizo {n} bya AI muri iri somo. Ibisubizo bidakoresha interineti, igenzura ry'ubutumwa n'izindi tabs biracyakora. Ongera ufungure paji utangire isomo rishya.",
        "sw": "Umefikia kikomo cha majibu {n} ya AI kwa kipindi hiki. Majibu ya nje ya mtandao, kikagua ujumbe na vichupo vingine bado vinafanya kazi. Pakia ukurasa upya kuanza kipindi kipya."}


def _d(state):
    d = state.get(KEY)
    if not isinstance(d, dict):
        d = {"ai": 0, "offline": 0, "scam": 0}
        state[KEY] = d
    return d


def limit() -> int:
    return max(0, settings.number("AI_MESSAGES_PER_SESSION", 0))


def record(state, kind: str):
    d = _d(state)
    d[kind] = d.get(kind, 0) + 1


def allowed(state) -> bool:
    n = limit()
    return n == 0 or _d(state)["ai"] < n


def caption(state, lang="en") -> str:
    d = _d(state)
    n = limit()
    lim = f" / {n}" if n else ""
    return CAPTION.get(lang, CAPTION["en"]).format(off=d["offline"] + d["scam"], ai=d["ai"], lim=lim if n else "")


def over_message(lang="en") -> str:
    return OVER.get(lang, OVER["en"]).format(n=limit())
