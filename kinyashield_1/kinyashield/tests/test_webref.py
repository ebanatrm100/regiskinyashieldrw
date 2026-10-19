"""webref: term extraction and formatting, with the network mocked (Wikipedia is not reachable from the test sandbox)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import webref as W


def test_extract_term():
    cases = {"photosynthesis": "photosynthesis", "What is photosynthesis?": "photosynthesis", "what is a black hole": "black hole",
             "meaning of resilience": "resilience", "explain inflation": "inflation", "tell me about Rwanda": "Rwanda", "define entropy": "entropy",
             "what does the word ubiquitous mean": "ubiquitous", "Qu'est-ce que la photosynthèse ?": "photosynthèse", "c'est quoi un virus": "virus",
             "maana ya demokrasia": "demokrasia", "Ni iki fotosintezi": "fotosintezi", "Tomato": "Tomato"}
    for q, want in cases.items():
        assert W.extract_term(q) == want, (q, W.extract_term(q))
    for q in ["how do I reset my password", "write me an email to my boss", "translate hello to french", "", "12345", "why is the sky blue",
              "what is the difference between a virus and a worm", " ".join(["word"] * 12)]:
        assert W.extract_term(q) is None, q


def _fake_get(url):
    if "wikipedia.org" in url:
        host = url.split("//")[1].split(".")[0]
        if host != "en":
            return {"query": {"pages": {}}}
        return {"query": {"pages": {"1": {"index": 1, "title": "Photosynthesis", "extract": "Photosynthesis is a process used by plants.", "fullurl": "https://en.wikipedia.org/wiki/Photosynthesis", "pageprops": {}},
                                    "2": {"index": 2, "title": "Light", "extract": "Light is radiation."}}}}
    if "wiktionary" in url:
        return {"en": [{"partOfSpeech": "Noun", "definitions": [{"definition": "<b>The</b> process &amp; more"}]}]}
    raise OSError


def test_lookup_and_format():
    W.lookup.cache_clear()
    real = W._get
    W._get = _fake_get
    try:
        info = W.lookup("photosynthesis", "en")
        assert info["wiki"]["title"] == "Photosynthesis" and info["dict"][0][1][0] == "The process & more"
        out = W.format_answer(info, "en")
        assert "Photosynthesis is a process" in out and "https://en.wikipedia.org/wiki/Photosynthesis" in out and "CC BY-SA" in out
        fr = W.lookup("photosynthesis", "fr")            # no French page in the fake: falls back to English and says so
        assert fr["wiki"]["lang"] == "en" and "anglais" in W.format_answer(fr, "fr")
        assert "Photosynthesis is a process" in W.reference_text(info)
        assert W.source_line(info, "sw").startswith("\n\nChanzo")
    finally:
        W._get = real
        W.lookup.cache_clear()


def test_lookup_never_raises_and_disambiguation():
    W.lookup.cache_clear()
    real = W._get

    def boom(url):
        raise OSError("offline")
    W._get = boom
    try:
        assert W.lookup("anything", "en") is None
    finally:
        W._get = real
        W.lookup.cache_clear()
    W._get = lambda url: {"query": {"pages": {"1": {"index": 1, "title": "Mercury", "extract": "Mercury may refer to:", "pageprops": {"disambiguation": ""}},
                                              "2": {"index": 2, "title": "Mercury (planet)", "extract": "Mercury is the smallest planet.", "fullurl": "u"}}}}
    try:
        w = W.wikipedia("mercury", "en")
        assert w["title"] == "Mercury (planet)" and "smallest planet" in w["extract"]
    finally:
        W._get = real


def test_wiktionary_only_single_english_words():
    assert W.wiktionary("black hole") is None and W.wiktionary("123") is None


def test_labels_complete():
    keys = set(W.LABELS["en"])
    assert all(set(W.LABELS[l]) == keys for l in ("fr", "rw", "sw"))


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("webref ok")
