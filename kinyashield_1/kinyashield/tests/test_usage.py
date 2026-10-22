import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import usage as U


def test_counters_and_limit():
    os.environ.pop("AI_MESSAGES_PER_SESSION", None)
    st = {}
    assert U.allowed(st) and U.limit() == 0
    U.record(st, "ai"); U.record(st, "offline"); U.record(st, "scam")
    assert "1 AI answers" in U.caption(st, "en") and "2 offline" in U.caption(st, "en") and "/" not in U.caption(st, "en")
    os.environ["AI_MESSAGES_PER_SESSION"] = "2"
    assert U.allowed(st) and "/ 2" in U.caption(st, "en")
    U.record(st, "ai")
    assert not U.allowed(st) and "2" in U.over_message("en")
    for l in ("fr", "rw", "sw"):
        assert U.over_message(l) != U.over_message("en") and U.caption(st, l)
    os.environ["AI_MESSAGES_PER_SESSION"] = "abc"
    assert U.limit() == 0 and U.allowed(st)
    os.environ.pop("AI_MESSAGES_PER_SESSION")


if __name__ == "__main__":
    test_counters_and_limit(); print("usage ok")
