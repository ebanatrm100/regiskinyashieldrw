import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from scam_corpus import CORPUS
from benign_corpus import BENIGN
import detector as D, message_ai as A, scam_scen_core as C
C.load()
LANGS = ("en", "fr", "rw", "sw")
# 1. every scenario is complete in all four languages and gives specific steps
assert len(C.SCENARIOS) >= 100, len(C.SCENARIOS)
ids = [s["id"] for s in C.SCENARIOS]
assert len(ids) == len(set(ids)), "duplicate scenario ids"
for s in C.SCENARIOS:
    for l in LANGS:
        assert s["name"][l].strip() and len(s["why"][l]) > 40, (s["id"], l)
        assert len(s["do"][l]) >= 2, (s["id"], l, "needs at least two specific steps")
    assert len(s["groups"]) >= 2 or s["id"] in ("ussd_call_forward",), (s["id"], "too broad: one cue alone")
# 2. every scam message must be raised and name a specific situation
unnamed = []
for lang, t in CORPUS:
    a = A.assess(t, lang, D.analyze(t), use_ai=False)
    assert a["verdict"] != "ok", ("scam shown as no warning", lang, t[:70])
    if not C.match(t, lang):
        unnamed.append((lang, t[:60]))
assert not unnamed, unnamed
# 3. harmless messages stay unflagged
for lang, t in BENIGN:
    a = A.assess(t, lang, D.analyze(t), use_ai=False)
    assert a["verdict"] == "ok", ("harmless message flagged", lang, t[:70], a["kind"])
# 4. even a clean result gives steps about THIS message (its link / number / amount)
t = "Hello, see https://www.example-store.com/order/123 for your order. Call 0788123456 about 25,000 RWF."
for lang in LANGS:
    a = A.assess(t, lang, D.analyze(t), use_ai=False)
    joined = " ".join(a["do"])
    assert "example-store.com" in joined and "0788123456" in joined, (lang, a["do"])
print("OK", len(C.SCENARIOS), "scenarios;", len(CORPUS), "scam and", len(BENIGN), "harmless messages")
