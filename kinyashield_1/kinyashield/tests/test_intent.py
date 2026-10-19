"""intent.py: understanding the real problem (offline, four languages)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import intent as I
import assistant_flow as F


def test_vague_openers_ask_what_is_needed():
    for q, l in [("help", "en"), ("I have a problem", "en"), ("aide-moi", "fr"), ("mfasha", "rw"), ("nisaidie", "sw")]:
        r = F.route(q, l)
        assert r["kind"] == "guide" and r["entry"]["id"] == "intent_clarify", (q, r["kind"])
        assert len(r["entry"]["answer"][l]) > 200
    assert I.clarify("help", "en") is not None


def test_not_vague_when_there_is_content_or_history():
    assert I.clarify("help me write a cv", "en") is None
    assert not I.analyze("help", [{"role": "user", "content": "x"}], "en").vague   # a follow-up, not an empty opener
    assert F.route("hello", "en")["entry"]["id"] != "intent_clarify"


def test_task_urgency_distress():
    it = I.analyze("I was hacked and I am scared, my money is gone", None, "en")
    assert it.urgent and it.distressed
    assert I.analyze("Should I buy a laptop or a phone", None, "en").task == "decide"
    assert I.analyze("Solve 2x+3=11", None, "en").task == "calculate"
    assert I.analyze("is this a scam", None, "en").task == "verify"
    assert I.analyze("Pesa zimepotea na naogopa sana", None, "sw").distressed and I.analyze("Pesa zimepotea na naogopa sana", None, "sw").urgent
    assert "URGENT" in I.hint(it) and "worried" in I.hint(it)
    assert I.hint(I.analyze("what is a mango", None, "en")) == ""


def test_frame_guide_text():
    out = I.frame_guide_text("STEPS", "I was hacked and I am scared", None, "en")
    assert out.startswith("I'm sorry") and "Time matters" in out and "STEPS" in out
    assert I.frame_guide_text("STEPS", "how do I make a strong password", None, "en") == "STEPS"
    for l in I.LANGS:
        assert I.CALM[l] and I.TIME[l]


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("intent ok")
