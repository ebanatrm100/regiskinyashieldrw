"""One safe way for the tabs (Cyber News, Log Analyzer ...) to ask the AI and to tell the user the REAL reason when it does not answer.
ask() returns (text, None) on success or (None, code) with code in: no_key, quota, network, empty, error:<ExceptionName>. explain_failure() turns a code into a message in the four languages.
Secrets and request contents are never included in messages."""
from __future__ import annotations

_MSG = {
    "no_key": {"en": "The AI key is not set in this app's Streamlit Secrets (GEMINI_API_KEY). Add it under App settings, Secrets; the built-in explanations above still work.",
               "fr": "La clé IA n'est pas définie dans les Secrets Streamlit de l'application (GEMINI_API_KEY). Ajoutez-la dans Paramètres de l'application, Secrets ; les explications intégrées ci-dessus fonctionnent toujours.",
               "rw": "Urufunguzo rwa AI ntirushyizwe muri Streamlit Secrets y'iyi porogaramu (GEMINI_API_KEY). Rushyiremo muri App settings, Secrets; ibisobanuro biri hejuru biracyakora.",
               "sw": "Ufunguo wa AI haujawekwa kwenye Streamlit Secrets za programu hii (GEMINI_API_KEY). Uweke kwenye App settings, Secrets; maelezo yaliyomo hapo juu bado yanafanya kazi."},
    "quota": {"en": "The AI service says the daily or per-minute limit is used up. Try again in a few minutes; the built-in explanations above still work.",
              "fr": "Le service d'IA indique que la limite quotidienne ou par minute est atteinte. Réessayez dans quelques minutes ; les explications intégrées ci-dessus fonctionnent toujours.",
              "rw": "Serivisi ya AI ivuga ko igipimo cy'umunsi cyangwa cy'umunota cyashize. Ongera ugerageze nyuma y'iminota mike; ibisobanuro biri hejuru biracyakora.",
              "sw": "Huduma ya AI inasema kikomo cha siku au dakika kimeisha. Jaribu tena baada ya dakika chache; maelezo yaliyomo hapo juu bado yanafanya kazi."},
    "network": {"en": "The AI service could not be reached (network or time-out). Try again; the built-in explanations above still work.",
                "fr": "Le service d'IA est injoignable (réseau ou délai dépassé). Réessayez ; les explications intégrées ci-dessus fonctionnent toujours.",
                "rw": "Serivisi ya AI ntiyabonetse (umuyoboro cyangwa igihe cyarangiye). Ongera ugerageze; ibisobanuro biri hejuru biracyakora.",
                "sw": "Huduma ya AI haikufikika (mtandao au muda umeisha). Jaribu tena; maelezo yaliyomo hapo juu bado yanafanya kazi."},
    "empty": {"en": "The AI returned an empty answer. Try again; the built-in explanations above still work.", "fr": "L'IA a renvoyé une réponse vide. Réessayez ; les explications intégrées ci-dessus fonctionnent toujours.",
              "rw": "AI yasubije ubusa. Ongera ugerageze; ibisobanuro biri hejuru biracyakora.", "sw": "AI imerudisha jibu tupu. Jaribu tena; maelezo yaliyomo hapo juu bado yanafanya kazi."},
    "error": {"en": "The AI could not answer ({what}). Try again; the built-in explanations above still work.", "fr": "L'IA n'a pas pu répondre ({what}). Réessayez ; les explications intégrées ci-dessus fonctionnent toujours.",
              "rw": "AI ntiyashoboye gusubiza ({what}). Ongera ugerageze; ibisobanuro biri hejuru biracyakora.", "sw": "AI imeshindwa kujibu ({what}). Jaribu tena; maelezo yaliyomo hapo juu bado yanafanya kazi."},
}


def classify_error(exc: BaseException) -> str:
    name = exc.__class__.__name__
    text = str(exc).lower()
    if name == "MissingAPIKeyError" or "api_key is not configured" in text or "api key" in text and ("missing" in text or "not configured" in text):
        return "no_key"
    if "429" in text or "quota" in text or "resource_exhausted" in text or "rate limit" in text or "exhausted" in text:
        return "quota"
    if any(w in text for w in ("timed out", "timeout", "connection", "name or service", "unreachable", "urlopen", "ssl", "network")) or name in ("URLError", "TimeoutError", "ConnectionError"):
        return "network"
    return "error:" + name


def ask(question: str, lang: str = "en", use_search: bool = False):
    try:
        from assistant_engine import answer_question
        name = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}.get(lang, "English")
        out = answer_question(question=question, history=[], language_name=name, language_code=lang, use_search=use_search)
        out = (out or "").strip()
        return (out, None) if out else (None, "empty")
    except Exception as e:                                   # noqa: BLE001 (every failure is reported, none is hidden)
        return None, classify_error(e)


def explain_failure(code: str, lang: str = "en") -> str:
    lang = lang if lang in _MSG["no_key"] else "en"
    if code.startswith("error:"):
        return _MSG["error"][lang].format(what=code.split(":", 1)[1])
    return _MSG.get(code, _MSG["error"])[lang].format(what="?")
