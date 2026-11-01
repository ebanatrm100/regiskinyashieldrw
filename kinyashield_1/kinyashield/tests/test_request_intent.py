"""Examples, follow-ups and 'what happened this week' requests are answered as asked, never replaced by a definition of a keyword in them."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from datetime import date
import request_intent as R, assistant_flow as F, chat_news as CN, cyber_intel as ci

H = [{"role": "user", "content": "What is phishing?"}, {"role": "assistant", "content": "Phishing is a fake message that steals your details.", "kind": "note"}]
def kind(q, lang="en", hist=H):
    d = F.route(q, lang, history=hist)
    return d["kind"] if d["kind"] != "ai" else "ai:" + str(d.get("intent"))

CASES = [  # (language, message, expected route)
    ("en", "give me example of this", "ai:example"), ("en", "Give me an example of this", "ai:example"), ("en", "explain more", "ai:followup"), ("en", "why?", "ai:followup"), ("en", "another one", "ai:followup"),
    ("en", "give me an example of ransomware", "ai:example"), ("en", "Tell me cybercrimes which happened this week", "cyber_news"), ("en", "what cyberattacks happened today?", "cyber_news"), ("en", "latest ransomware news", "cyber_news"),
    ("fr", "donne-moi un exemple", "ai:example"), ("fr", "plus de détails", "ai:followup"), ("fr", "Donne-moi un exemple de hameçonnage", "ai:example"), ("fr", "Quelles cyberattaques ont eu lieu cette semaine ?", "cyber_news"), ("fr", "actualité du piratage hier", "cyber_news"),
    ("rw", "mpa urugero", "ai:example"), ("rw", "komeza", "ai:followup"), ("rw", "Mpa urugero rw'uburiganya", "ai:example"), ("rw", "ni ibihe byaha byo kuri interineti byabaye icyumweru gishize?", "cyber_news"), ("rw", "amakuru y'ibitero uyu munsi", "cyber_news"),
    ("sw", "nipe mfano", "ai:example"), ("sw", "eleza zaidi", "ai:followup"), ("sw", "Nipe mfano wa ulaghai", "ai:example"), ("sw", "habari za uhalifu wa mtandaoni wiki hii", "cyber_news"), ("sw", "mashambulizi yaliyotokea leo", "cyber_news"),
]
bad = [(l, q, want, kind(q, l)) for l, q, want in CASES if kind(q, l) != want]
assert not bad, bad
# ordinary questions keep their normal route
for q in ("What is phishing?", "How do I protect my phone?", "Send your PIN today to win a prize"):
    assert F.route(q, "en", history=H)["kind"] in ("guide", "scam", "ai") and F.route(q, "en", history=H).get("intent") is None, q
# a follow-up without any earlier conversation is not forced onto a topic
assert F.route("explain more", "en", history=[]).get("intent") is None
# the question sent to the AI carries what "this" refers to and an instruction to do what was asked
info = R.classify("give me example of this", "en", H)
rq = R.resolve("give me example of this", info, "en")
assert "What is phishing?" in rq and "EXAMPLES" in rq and "definition" in rq
# no time named: ask which period, remember the topic; the reply "this week" continues the request
d = F.route("Tell me cybercrimes", "en", history=H)
assert d["kind"] == "ai" or d["kind"] == "guide" or d["kind"] == "cyber_news"      # (no event words: ordinary route)
d = F.route("latest cybercrime news", "en", history=H)
assert d["kind"] == "cyber_news" and d["period"] is None      # no time named: the chat asks which period
ask = CN.ask_period("fr")
assert "Quelle période" in ask and ci.LABELS["fr"]["this_week"] in ask
H2 = H + [{"role": "user", "content": "cybercrime news"}, {"role": "assistant", "content": ask, "kind": "note", "news_ctx": {"topics": ["crime"], "text": "cybercrime news"}}]
d = F.route("this week", "en", history=H2)
assert d["kind"] == "cyber_news" and d["period"]["key"] == "this_week" and d["ctx"]["topics"] == ["crime"]
d = F.route("la semaine dernière", "fr", history=H2)
assert d["kind"] == "cyber_news" and d["period"]["key"] == "last_week"
# the answer text: dated, sourced, summarised; empty and failing sources are explained
feed = b"""<rss><channel><item><title>Police arrest ransomware gang suspects</title><link>https://www.bleepingcomputer.com/a</link><pubDate>%s</pubDate></item></channel></rss>"""
today = ci.today_local()
from email.utils import format_datetime
from datetime import datetime, timezone
pub = format_datetime(datetime.now(timezone.utc)).encode()
per = ci.period_from_key("these_days")
txt = CN.answer(per, ["crime"], "", "fr", fetch_jobs=[("BleepingComputer", "research", ("crime",), lambda: ("feed", feed % pub))])
assert "Police arrest" in txt and "bleepingcomputer.com" in txt and str(today) in txt
none = CN.answer(per, ["crime"], "", "rw", fetch_jobs=[("X", "research", ("crime",), lambda: (_ for _ in ()).throw(OSError("down")))])
assert "Nta kintu" in none
print("OK request intent")
