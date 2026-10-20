"""Communicate naturally: translation requests, quoted sentences, names, photos and plain-language levels (network mocked)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import assistant_flow as F
import meta_guard as MG
import images_db as IM
import register as RG
import webref as W


def test_translation_is_not_answered_as_a_question():
    r = F.route("Translate who owns you into Kinyarwanda", "en")
    assert r["kind"] == "translate" and r["phrase"] == "who owns you" and r["target"] == "rw"
    for q in ["Translate who is your owner into French", "tafsiri who owns you kwa Kiswahili", "Traduis who owns you en kinyarwanda"]:
        assert F.route(q, "en")["kind"] == "translate", q
    # the owner question itself still gets the owner answer
    assert F.route("Who owns you?", "en")["entry"]["id"] == "owner"
    assert F.route("Who is your owner?", "en")["entry"]["id"] == "owner"


def test_wrapped_sentences_do_not_trigger_identity_answers():
    for q in ["Repeat: who is your owner", "Correct the grammar of: who is your owner", "Rewrite this sentence: hello how are you"]:
        r = F.route(q, "en")
        assert r["kind"] == "ai", (q, r)


def test_phrasebook_still_first():
    r = F.route("how do you say good morning in Kinyarwanda", "en")
    assert r["kind"] == "guide" and r["entry"]["id"].startswith("translate")


def test_name_meaning():
    r = F.route("What is the meaning of the name Regis?", "en")
    assert r["kind"] == "guide" and "king" in r["entry"]["answer"]["en"].lower()
    assert W.extract_name("What is the meaning of the name Regis?") == "Regis"
    assert W.extract_name("the meaning of the name Zxqvr") == "Zxqvr"
    assert W.extract_name("what is photosynthesis") is None
    for l in W.LABELS:
        assert W.no_name(l) and W.no_answer(l) and "{t}" not in W.no_lookup("x", l)


def _fake_commons(n=12):
    pages = {}
    for i in range(n):
        pages[str(i)] = {"index": i + 1, "title": f"File:Tomato {['plant','market','soup','seeds','salad','field','garden','sauce','vine','farm','crate','leaf'][i]} {i}.jpg",
                         "imageinfo": [{"mime": "image/jpeg", "width": 1200, "thumburl": f"https://upload.wikimedia.org/x/{i}.jpg", "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}}}]}
    pages["a"] = {"index": 0, "title": "File:Tomato logo.png", "imageinfo": [{"mime": "image/png", "width": 900, "thumburl": "https://upload.wikimedia.org/x/logo.png"}]}
    pages["b"] = {"index": 0, "title": "File:Tomato tiny.jpg", "imageinfo": [{"mime": "image/jpeg", "width": 100, "thumburl": "https://upload.wikimedia.org/x/t.jpg"}]}
    pages["c"] = {"index": 0, "title": "File:Tomato anim.gif", "imageinfo": [{"mime": "image/gif", "width": 900, "thumburl": "https://upload.wikimedia.org/x/a.gif"}]}
    pages["d"] = {"index": 0, "title": "File:Tomato evil.jpg", "imageinfo": [{"mime": "image/jpeg", "width": 900, "thumburl": "https://evil.example/x.jpg"}]}
    return {"query": {"pages": pages}}


def test_photos_pick_five_real_photos():
    got = IM.pick(_fake_commons(), "tomato plant", 5)
    assert len(got) == 5
    assert all(g["url"].startswith("https://upload.wikimedia.org/") and g["page"].startswith("https://commons.wikimedia.org/wiki/File:") for g in got)
    assert not any("logo" in g["caption"].lower() or "tiny" in g["caption"].lower() or "anim" in g["caption"].lower() or "evil" in g["caption"].lower() for g in got)
    assert got[0]["license"] == "CC BY-SA 4.0"
    IM._cache.clear()
    real = IM._get
    try:
        IM._get = lambda url: (_ for _ in ()).throw(OSError("offline"))
        assert IM.photos("anything goes", 5) == []          # never raises
        IM._cache.clear()
        IM._get = lambda url: _fake_commons()
        assert len(IM.photos("tomato", 5)) == 5
    finally:
        IM._get = real
        IM._cache.clear()
    for l in ("en", "fr", "rw", "sw"):
        assert IM.note(l) and IM.none_note(l)


def test_levels_and_glossary():
    assert RG.detect("explain phishing in simple words", []) == "simple"
    assert RG.detect("explain TLS handshake and cipher suites in detail", []) == "technical"
    assert RG.detect("what is a loan", []) == "standard"
    assert RG.level_from_choice(1, "tls handshake in detail", []) == "simple"      # the selector wins
    out = RG.add_glossary("Never share your OTP or PIN.", "simple", "how do I stay safe", "en", "")
    assert "Words explained" in out and "OTP" in out
    assert RG.add_glossary("Never share your OTP.", "technical", "", "en", "") == "Never share your OTP."
    for l in ("en", "fr", "rw", "sw"):
        assert RG.label(l)[1] and "AUDIENCE" in RG.hint("simple")


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("natural ok")
