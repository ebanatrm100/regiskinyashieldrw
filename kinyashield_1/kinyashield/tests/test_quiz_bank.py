import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import quiz_data as QD
LANGS = ("en", "fr", "rw", "sw")
for topic in ("cybersecurity", "networks"):
    qs = [q for q in QD.QUESTIONS if q["topic"] == topic]
    assert len(qs) >= 500, (topic, len(qs))
    seen = set()
    for q in qs:
        for l in LANGS:
            assert q["q"][l].strip() and q["why"][l].strip() and q["slip"][l].strip(), (topic, q["q"]["en"])
            o = QD.options(q, l)
            assert len(o) >= 3 and all(str(x).strip() for x in o), (topic, q["q"]["en"], l)
            assert len(set(o)) == len(o), ("duplicate options", topic, q["q"]["en"], l, o)
            assert len(o) == len(QD.options(q, "en"))
        assert 0 <= q["ans"] < len(QD.options(q, "en"))
        assert q["q"]["en"] not in seen, ("duplicate question", q["q"]["en"])
        seen.add(q["q"]["en"])
        assert "{" not in q["q"]["en"] and "{" not in q["why"]["en"]
        # a masked description must not give away the correct answer
        if "“" in q["q"]["en"]:
            d = q["q"]["en"].split("“", 1)[1].lower()
            right = str(QD.options(q, "en")[q["ans"]]).lower().split(" (")[0]
            assert len(right) < 4 or right not in d, ("answer leaked", q["q"]["en"], right)
    print(topic, len(qs))
assert "networks" in QD.TOPICS and all(QD.TOPICS["networks"][l] for l in LANGS)
assert len(QD.pick("networks", 30, 1)) == 30
print("OK")
