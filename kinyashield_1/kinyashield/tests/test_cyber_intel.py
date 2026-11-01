import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from datetime import date
import cyber_intel as ci
T = date(2026, 11, 1)
def rng(q):
    p = ci.parse_time(q, T); return p and (p["start"], p["end"])
assert rng("cybercrime news last week") == (date(2026, 10, 19), date(2026, 10, 25))
assert rng("actualité cyber la semaine dernière") == rng("amakuru ya cyber icyumweru gishize") == (date(2026, 10, 19), date(2026, 10, 25))
assert rng("habari za usalama wa mtandao jana") == (date(2026, 10, 31),) * 2
assert rng("scams in 2025") == (date(2025, 1, 1), date(2025, 12, 31))
assert rng("last 2 months cyber awareness") == rng("ibyaha bya cyber mu mezi abiri ashize") == (date(2026, 9, 1), date(2026, 11, 1))
assert rng("ransomware") is None and rng("cybersecurity") is None          # no period named: the tab asks with choices
assert set(ci.KEYS) >= {"today", "yesterday", "this_week", "last_week", "last_month", "last_2_months"}
assert ci.trust_kind("https://www.cisa.gov/x") == "official" and ci.trust_kind("https://random-blog.example/x") is None
feed = b"""<rss><channel><item><title>Police arrest ransomware gang suspects</title><link>https://www.bleepingcomputer.com/a</link><pubDate>Fri, 30 Oct 2026 10:00:00 GMT</pubDate><description>d</description></item>
<item><title>Old story</title><link>https://www.bleepingcomputer.com/b</link><pubDate>Fri, 01 Jan 2021 10:00:00 GMT</pubDate></item></channel></rss>"""
def ok(): return ("feed", feed)
def bad(): raise OSError("down")
res = ci.search({"start": date(2026, 10, 26), "end": T}, ["crime", "security"], "en", "", fetch_jobs=[("BleepingComputer", "research", ("crime",), ok), ("Broken", "research", ("security",), bad)])
assert res["sources"] == [("BleepingComputer", "research", 1)] and res["failed"] == ["Broken"], res
print("OK cyber intel")
