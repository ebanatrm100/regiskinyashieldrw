"""Fast live look-up for the AI Assistant: when a question is about something current or factual, fetch several public sources AT THE SAME TIME
(Wikipedia in the user's language and in English, plus the DuckDuckGo instant-answer service) and hand the text to the AI as untrusted reference data.
Used (a) next to Gemini's own web search, and (b) as the only live source when Gemini search is unavailable or the AI is an open-model server.
Hard time limit (DEADLINE seconds) so the answer is never held up; every failure returns None. Nothing is invented: text and links come from the sources."""
from __future__ import annotations
import json
import re
import threading
import urllib.parse
import urllib.request
from functools import lru_cache

import webref

DEADLINE = 4.5
UA = webref.UA

_LIVE = re.compile(
    r"\b(?:latest|current(?:ly)?|today|tonight|now|recent(?:ly)?|news|this (?:week|month|year)|right now|price|prices|cost of|exchange rate|rate of|weather|forecast|score|results?|"
    r"who is (?:the )?(?:current )?(?:president|prime minister|minister|ceo|governor|mayor)|president of|how much is|when (?:is|does|will)|release date|new law|update|202\d|"
    r"derni(?:er|ere|ers|eres)|actuel(?:le|s)?|aujourd'hui|maintenant|actualit\w+|prix|taux|meteo|resultat\w*|cette (?:semaine|annee)|"
    r"uyu munsi|ubu|amakuru (?:mashya|agezweho)|igiciro|ibiciro|ikirere|uyu mwaka|"
    r"leo|sasa|habari|bei|hali ya hewa|matokeo|mwaka huu|wiki hii)\b", re.I)
_PERSONAL = re.compile(r"\b(?:my|mon|ma|mes|yanjye|wangu|changu)\b.*\b(?:password|pin|otp|mot de passe|ijambo ry'ibanga|nywila)\b", re.I)


def needs_live(question: str) -> bool:
    """True when the question is probably about something current or checkable online, so a live lookup is worth doing."""
    q = (question or "").strip()
    if len(q) < 8 or len(q) > 400 or _PERSONAL.search(q):
        return False
    return bool(_LIVE.search(q))


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=DEADLINE) as r:  # noqa: S310 (fixed https hosts only)
        return json.loads(r.read().decode("utf-8", "replace"))


def _wiki_pages(query: str, lang: str):
    host = webref.WIKI.get(lang, "en")
    params = {"action": "query", "format": "json", "redirects": 1, "generator": "search", "gsrsearch": query, "gsrlimit": 3, "gsrnamespace": 0,
              "prop": "extracts|info", "exintro": 1, "explaintext": 1, "exlimit": 3, "exchars": 1500, "inprop": "url"}
    data = _get(f"https://{host}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    return [(p.get("title", ""), webref._clean(p.get("extract", "")), p.get("fullurl", "")) for p in pages if (p.get("extract") or "").strip()]


def _ddg(query: str):
    data = _get("https://api.duckduckgo.com/?" + urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "skip_disambig": 1, "no_redirect": 1}))
    out = []
    if data.get("AbstractText"):
        out.append((data.get("Heading") or query, webref._clean(data["AbstractText"]), data.get("AbstractURL") or ""))
    for t in (data.get("RelatedTopics") or [])[:3]:
        if isinstance(t, dict) and t.get("Text"):
            out.append((query, webref._clean(t["Text"]), t.get("FirstURL") or ""))
    return out


@lru_cache(maxsize=256)
def fetch(question: str, lang: str = "en"):
    """List of (title, text, url) from several sources fetched in parallel, within DEADLINE seconds. [] when nothing was found."""
    q = re.sub(r"[?!]+$", "", (question or "").strip())[:200]
    jobs = {"w_lang": lambda: _wiki_pages(q, lang), "ddg": lambda: _ddg(q)}
    if lang != "en":
        jobs["w_en"] = lambda: _wiki_pages(q, "en")
    res: dict = {}

    def run(name, fn):
        try:
            res[name] = fn()
        except Exception:
            res[name] = []

    threads = [threading.Thread(target=run, args=(n, f), daemon=True) for n, f in jobs.items()]
    for t in threads:
        t.start()
    for t in threads:
        t.join(DEADLINE)
    seen, items = set(), []
    for name in ("ddg", "w_lang", "w_en"):
        for title, text, url in res.get(name, []) or []:
            key = (url or title).lower()
            if text and key not in seen:
                seen.add(key)
                items.append((title, text, url))
    return items[:6]


def reference_text(items) -> str:
    return "\n\n".join(f"[{i}] {t}: {x[:1200]} ({u})" for i, (t, x, u) in enumerate(items, 1))


def sources_line(items, lang: str = "en") -> str:
    head = {"en": "Live sources checked", "fr": "Sources consultées en direct", "rw": "Amasoko yarebwe ako kanya", "sw": "Vyanzo vilivyokaguliwa moja kwa moja"}.get(lang, "Live sources checked")
    links = [f"- [{t}]({u})" for t, _x, u in items if u][:4]
    return f"\n\n**{head}:**\n" + "\n".join(links) if links else ""
