"""Language parity: every knowledge entry is found by its own title in en, fr, rw and sw, and no per-language text is missing."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import streamlit  # noqa
except Exception:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
import guide_search as G, knowledge_base as K, tools_parity_audit as A

def test_every_title_finds_its_entry_in_all_languages():
    bad = [(l, e["id"]) for e in K.BY_ID.values() for l in ("en", "fr", "rw", "sw") if (G.best(e["title"][l], l) or {}).get("id") != e["id"]]
    assert not bad, bad[:10]

def test_no_missing_language_text():
    rep = A.audit(); problems = []
    for m, x in rep.items():
        assert "import_error" not in x, (m, x)
        problems += [(m, e) for e in x["examples"] if e[0] in ("missing", "empty") and m not in ("safety_rules", "safety_rules_more")]
    assert not problems, problems[:10]

if __name__ == "__main__":
    test_every_title_finds_its_entry_in_all_languages(); test_no_missing_language_text(); print("parity OK")
