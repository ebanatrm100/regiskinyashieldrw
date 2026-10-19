"""Tests for the business and school dashboard logic (no Streamlit needed)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import org_dashboard as O

CSV = (b"message,date,channel,reported_by\n"
       b"Send your PIN now to claim your prize,2026-09-03,SMS,A\n"
       b"Meeting at 3pm in room 4,2026-10-01,email,B\n"
       b"Pay a small fee to receive your 500000 RWF inheritance. Do not tell anyone,2026-10-04,WhatsApp,C\n"
       b"=HYPERLINK(\"http://x\"),not-a-date,=cmd,D\n")


def test_split():
    assert O.split_messages("a\n---\nb\n\n\n\n\nc\n") == ["a", "b", "c"]
    assert O.split_messages("") == []


def test_review_and_summary():
    recs = O.review(O.parse_csv(CSV))
    assert len(recs) == 4
    assert recs[0]["verdict"] == "high"                      # most urgent first
    assert [r["verdict"] for r in recs] == sorted([r["verdict"] for r in recs], key=lambda v: O.VERDICT_ORDER[v])
    s = O.summary(recs)
    assert s["total"] == 4 and s["high"] + s["verify"] + s["ok"] == 4
    assert s["ok"] >= 1
    assert all(r["date"] == "" for r in recs if r["channel"] == "=cmd")   # bad date is dropped, not trusted


def test_limits():
    recs = O.review(["x"] * 400)
    assert len(recs) == O.MAX_MESSAGES


def test_trend_needs_two_months():
    assert O.trend_note({"2026-09": 2}, "en") == ""
    for l in O.LANGS:
        assert "3" in O.trend_note({"2026-09": 1, "2026-10": 3}, l)


def test_briefing_all_languages():
    recs = O.review(O.parse_csv(CSV))
    for l in O.LANGS:
        b = O.staff_briefing(recs, l, "School")
        assert b.startswith("# ") and "School" in b and "1." in b


def test_csv_report_is_safe_and_optional_text():
    recs = O.review(O.parse_csv(CSV))
    rep = O.report_csv(recs, "en")
    assert "'=HYPERLINK" in rep and "'=cmd" in rep
    assert "message" not in O.report_csv(recs, "en", include_text=False).splitlines()[0].split(",")[-1]


def test_ui_strings_complete():
    import org_ui
    keys = set(org_ui.U["en"])
    for l in O.LANGS:
        assert set(org_ui.U[l]) == keys and l in org_ui.TAB
        assert set(org_ui.U[l]["col"]) == set(org_ui.U["en"]["col"])


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("org tests ok")
