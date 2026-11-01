import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from datetime import date
import cyber_upcoming as U
T = date(2026, 11, 1)
def k(q):
    p = U.parse_future(q, T); return p and p["key"]
assert k("upcoming cybersecurity events") == "upcoming" and k("what is coming next week") == "next_week"
assert k("ibizaza ukwezi gutaha") == k("le mois prochain") == k("matukio yajayo mwezi ujao") == "next_month"
assert k("wiki ijayo") == k("la semaine prochaine") == k("icyumweru gitaha") == "next_week" and k("kesho") == k("demain") == k("tomorrow") == "tomorrow"
assert k("next 3 weeks") == "n_weeks" and k("ransomware") is None and k("last week") is None
assert U.resolve("next_week", T) == (date(2026, 11, 2), date(2026, 11, 8))
ev = U.calendar_items(date(2026, 11, 2), date(2027, 2, 28), "en")
dates = {(e["title"][:9], e["date"]) for e in ev}
assert ("Microsoft", date(2026, 11, 10)) in dates and ("Microsoft", date(2026, 12, 8)) in dates and ("Safer Int", date(2027, 2, 9)) in dates and ("Oracle Cr", date(2027, 1, 19)) in dates
assert any(e["date"] == date(2027, 1, 28) for e in ev)
kev = json.dumps({"vulnerabilities": [{"cveID": "CVE-2026-1234", "vendorProject": "Acme", "product": "Router", "dueDate": "2026-11-20", "shortDescription": "Bug", "knownRansomwareCampaignUse": "Known"},
                                       {"cveID": "CVE-2026-9999", "vendorProject": "X", "product": "Y", "dueDate": "2026-01-01"}]}).encode()
res = U.search(U.period_from_key("next_month", T) | {}, ["security", "crime", "awareness"], "fr", fetch=lambda url: kev)
res2 = U.search({"key": "next_3_months", "start": date(2026, 11, 2), "end": date(2027, 1, 31), "future": True}, ["security", "crime"], "fr", fetch=lambda url: kev)
assert res2["live"] and any("CVE-2026-1234" in i["title"] for i in res2["items"]["crime"]) and all("CVE-2026-9999" not in i["title"] for t in res2["items"] for i in res2["items"][t])
def boom(url): raise OSError("down")
res3 = U.search({"key": "next_week", "start": date(2026, 11, 2), "end": date(2026, 11, 8), "future": True}, None, "rw", fetch=boom)
assert res3["failed"] == ["CISA KEV"] and not res3["live"]
import cyber_intel_ui as ui
assert set(ui.X) == {"en", "fr", "rw", "sw"} and all(set(ui.X[l]) == set(ui.X["en"]) for l in ui.X)
print("OK cyber upcoming")
