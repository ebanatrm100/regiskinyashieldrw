import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cyber_explain as X, cyber_intel_ui as ui
CASES = {"arrest": "Police arrest ransomware gang suspects", "ransomware": "New ransomware hits hospital network", "deadline": "Deadline to fix CVE-2026-1234 in Acme Router",
         "data_breach": "Telecom confirms data breach exposing customers", "vulnerability": "Zero-day exploited in browser, patch now", "phishing": "Fake bank SMS phishing campaign",
         "scam": "Mobile money fraud rises in East Africa", "malware": "Android spyware found in fake apps", "ddos": "DDoS attack takes bank site offline", "ai_threat": "Deepfake voice used to trick finance staff",
         "awareness": "Ten tips to stay safe online", "generic": "Company announces quarterly results"}
for kind, title in CASES.items():
    assert X.kind_of({"title": title}) == kind, (kind, X.kind_of({"title": title}))
assert X.kind_of({"title": "x", "recurring": True}) == "event"
for kind in X.TXT:
    for l in X.LANGS:
        e = X.explain({"title": CASES.get(kind, "x"), "recurring": kind == "event"}, l)
        assert e["what"] and e["why"] and e["do"] and len(e["what"]) > 40 and e["kind_name"], (kind, l)
    assert len({X.explain({"title": CASES.get(kind, "x"), "recurring": kind == "event"}, l)["what"] for l in X.LANGS}) == 4, kind      # four real translations
assert all(X.digest([{"title": CASES["phishing"]}], l) for l in X.LANGS) and X.digest([], "en") == ""
assert set(ui.EX) == {"en", "fr", "rw", "sw"} and all(set(ui.EX[l]) == set(ui.EX["en"]) for l in ui.EX)
print("OK cyber explain")
