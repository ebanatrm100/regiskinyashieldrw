"""Question Answering and Research guide: topics in four languages, lookups in each language, tools, routing."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import research_guide_db as G, research_lab as L, assistant_flow as F

LANGS = ("en", "fr", "rw", "sw")


def test_topics_complete_in_four_languages():
    assert len(G._RAW) >= 12
    import ai_guide_db as A
    for e, kw, kwc in G._RAW:
        assert kw or kwc
        for l in LANGS:
            assert e["title"][l].strip() and len(e["answer"][l]) > 30, (e["id"], l)
        assert len({len(e["steps"][l]) for l in LANGS}) == 1, e["id"]
        for l in LANGS:
            if e["steps"][l]:
                assert e["steps_label"][l].strip()
        for r in e["related"]:
            assert r in G.IDS or r in A.IDS, (e["id"], r)
    n = {i: len(G.find(q)["steps"]["en"]) for i, q in [("interpret", "how does an ai understand a question"), ("research", "how does ai research"), ("rag", "what is rag"), ("compose", "how does ai compose an answer"), ("mistakes", "why does ai make mistakes")]}
    assert n == {"interpret": 5, "research": 7, "rag": 6, "compose": 6, "mistakes": 7}
    assert len(G.find("how to build a question answering assistant")["steps"]["fr"]) == 8


def test_honesty_points():
    assert "not the same as executing" in G.find("what is a tool call")["answer"]["en"]
    assert "not automatically true" in G.find("how does ai research")["answer"]["en"]
    assert "does not guarantee correctness" in G.find("what is rag")["answer"]["en"]
    assert "private" in G.find("what is not publicly knowable about ai")["answer"]["en"]


def test_lookup_in_every_language():
    assert G.find("qu'est-ce que le rag")["id"] == "qa_rag"
    assert G.find("rag ni iki")["id"] == "qa_rag"
    assert G.find("rag ni nini")["id"] == "qa_rag"
    assert G.find("pourquoi l'ia fait des erreurs")["id"] == "qa_mistakes"
    assert G.find("kwa nini ai hufanya makosa")["id"] == "qa_mistakes"
    assert G.find("what is a transformer")["id"] == "qa_term_transformer"
    assert G.find("what is phishing") is None


def test_tools():
    a = L.find("interpret: Which free website streams this film in Rwanda today? answer in a short list")["answer"]["en"]
    assert "Time-sensitive" in a and "Location matters" in a
    assert "ask which thing" in L.find("interpret: what about it?")["answer"]["en"]
    p = L.find("research plan: current price of maize in Kigali")["answer"]["fr"] if False else L.find("plan de recherche: prix actuel du maïs au Rwanda", "fr")["answer"]["fr"]
    assert "oui" in p and p.count("Rwanda") == 0 or "rwanda" in p
    r = L.find("rag demo: How long do tomatoes keep? ||| Tomatoes keep for about one week. ||| Maize is dried to 13%. ||| The bank opens at 8am.")["answer"]["en"]
    assert "> Tomatoes keep for about one week. [1]" in r
    n = L.find("rag demo: who won the cup ||| Tomatoes keep one week ||| maize dried")["answer"]["en"]
    assert "no support" in n or "found no support" in n
    assert L.find("what is a cat") is None


def test_routing():
    for q, kind in [("what is rag", "ai_guide"), ("rag demo: q ||| a b ||| c d", "ai_lab"), ("research plan: price of maize today", "ai_lab")]:
        r = F.route(q, "en")
        assert r["kind"] == "guide" and r["entry"]["kind"] == kind, (q, r["kind"])


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("research guide OK", n)
