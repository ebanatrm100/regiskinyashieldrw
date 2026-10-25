import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import quiz_data as QD
import tutor_db

qs = [q for q in QD.QUESTIONS if q["topic"] == "cybersecurity"]
assert len(qs) >= 80, len(qs)
seen = set()
for q in qs:
    for lang in ("en", "fr", "rw", "sw"):
        opts = QD.options(q, lang)
        assert len(opts) >= 2 and all(str(o).strip() for o in opts), (q["q"]["en"], lang)
        assert 0 <= q["ans"] < len(opts), (q["q"]["en"], lang)
    assert q["q"]["en"] not in seen, q["q"]["en"]
    seen.add(q["q"]["en"])
    for f in (q["q"], q["why"], q["slip"]):
        assert all(str(f[l]).strip() for l in ("en", "fr", "rw", "sw")), q["q"]["en"]
assert "cybersecurity" in QD.TOPICS
assert len(QD.pick("cybersecurity", 10, 1)) == 10
for l in ("en", "fr", "rw", "sw"):
    assert "ybers" in tutor_db._QUIZ_MSG[l] or "ybersecurity" in tutor_db._QUIZ_MSG[l], l
print("ok quiz_cyber", len(qs))
