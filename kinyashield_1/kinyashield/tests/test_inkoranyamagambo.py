"""The owner's Kinyarwanda dictionary: 461 entries, lookups in four languages, AI reference text, honest draft note."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import inkoranyamagambo as I, assistant_flow as F
from inkoranyamagambo_data import ROWS


def test_all_rows_loaded():
    assert len(ROWS) == 461 and all(w and d for w, _, d in ROWS)
    assert len({I._k(w) for w, _, _ in ROWS}) == 461


def test_questions_find_the_owners_definition():
    for q, l in [("umuntu ni iki?", "rw"), ("igisobanuro cya umwana", "rw"), ("sobanura ijambo ubwoba", "rw"), ("what does umuntu mean in Kinyarwanda?", "en"),
                 ("que signifie umwana en kinyarwanda", "fr"), ("maana ya ubwoba kwa kinyarwanda", "sw"), ("ubwoba", "rw")]:
        r = F.route(q, l)
        assert r["kind"] == "guide" and r["entry"]["id"].startswith("ink_"), (q, r["kind"], r.get("entry", {}).get("id"))
    e = I.find("umuntu ni iki", "rw")
    assert "Ikiremwamuntu kimwe" in e["answer"]["rw"] and "inzobere" in e["answer"]["rw"]
    assert "draft" in I.find("what does umuntu mean in Kinyarwanda", "en")["answer"]["en"]


def test_multi_meaning_words_are_flagged_and_unknown_is_ignored():
    assert "ibisobanuro bitandukanye" in I.find("umuryango ni iki", "rw")["answer"]["rw"]
    assert I.find("what is phishing", "en") is None and I.find("zzzz ni iki", "rw") is None


def test_ai_reference_lists_matching_terms():
    ref = I.reference_for("Umwana n'umubyeyi bafite ubwoba bwinshi mu ishuri")
    for w in ("umwana", "umubyeyi", "ubwoba", "ishuri"):
        assert w in ref
    assert I.reference_for("hello world") == ""


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("inkoranyamagambo OK", n)
