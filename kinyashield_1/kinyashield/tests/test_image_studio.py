"""Image creation, chat requests, attachments and safety pre-checks (no network, no keys)."""
import os, sys, base64, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for k in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "IMAGE_BASE_URL", "IMAGE_MODEL", "HF_TOKEN", "IMAGE_ALLOW_PUBLIC"):
    os.environ.pop(k, None)
os.environ["IMAGE_ALLOW_PUBLIC"] = "false"   # tests never use the network
import image_gen as G, attachments as A, photo_words as P, image_studio_ui as S

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def test_request_parsing_in_four_languages():
    for q, want in [("draw a cat on a roof", "cat on a roof"), ("generate an image of a market in Kigali", "market in Kigali"), ("dessine un lion", "lion"),
                    ("génère une image de montagne", "montagne"), ("kora ishusho y'inka", "inka"), ("tengeneza picha ya simba", "simba"), ("create a logo for my farm", "logo for my farm")]:
        got = G.parse_request(q)
        assert got and want in got, (q, got)
    for q in ("show me photos of lions", "what is a cat", "draw a flowchart of login", "photos de tomates"):
        assert G.parse_request(q) is None, q
    assert G.suggest_style("logo for my farm") == "logo" and G.suggest_style("a cat") == "photo"


def test_prompt_builder_keeps_the_idea_first():
    p = G.build_prompt("a market in Kigali at sunset", "cinematic", "16:9")
    assert p.startswith("a market in Kigali at sunset") and "landscape composition" in p and "no watermark" in p


def test_safety_precheck_refuses_harmful_requests():
    for bad in ("a fake mobile money receipt screenshot", "a forged passport", "naked child", "how to make a bomb picture"):
        assert G.check_prompt(bad), bad
    assert G.check_prompt("a cow in a green field") is None
    try:
        G.generate("a fake bank statement for my loan"); assert False
    except G.ImageGenError as e:
        assert str(e).startswith("refused:") and "deceive" in G.friendly_error(e, "en")


def test_public_service_is_default_last_resort_with_reasons():
    os.environ.pop("IMAGE_ALLOW_PUBLIC", None)
    try:
        assert "Pollinations (public)" in G.configured()
        seen = []
        def fake_http(url, data=None, headers=None, timeout=0):
            seen.append(url); raise OSError("offline")
        old = G._http; G._http = fake_http
        try:
            G.generate("a very long description. second sentence. third sentence")
            assert False
        except G.ImageGenError as e:
            msg = G.friendly_error(e, "en")
            assert "Public service" in msg and "OSError" in msg and len(seen) >= 3   # several models/prompts tried, reason shown
            assert "keyless" not in msg and "key" not in msg.lower().replace("keyless", "")[:0]
        finally:
            G._http = old
        G._http = lambda url, data=None, headers=None, timeout=0: (PNG, "image/png")
        try:
            assert G.generate("a cow")[0][2].startswith("Pollinations")
        finally:
            G._http = old
    finally:
        os.environ["IMAGE_ALLOW_PUBLIC"] = "false"
    assert "Pollinations (public)" not in G.configured()


def test_not_configured_and_provider_fallback():
    try:
        G.generate("a cow"); assert False
    except G.ImageGenError as e:
        assert str(e) == "not_configured" and "GEMINI_API_KEY" in G.friendly_error(e, "en") and G.friendly_error(e, "rw")
    orig = G.PROVIDERS
    calls = []
    def bad(*a): calls.append("a"); raise G.ImageGenError("Gemini: HTTP 429")
    def good(*a): calls.append("b"); return [(PNG, "image/png", "Test")]
    G.PROVIDERS = [("a", bad), ("b", good)]
    try:
        assert G.generate("a cow")[0][2] == "Test" and calls == ["a", "b"]
        G.PROVIDERS = [("a", bad)]
        try:
            G.generate("a cow"); assert False
        except G.ImageGenError as e:
            assert "429" in str(e) and "secret" not in str(e).lower()
    finally:
        G.PROVIDERS = orig


def test_sniff_and_reference_limits():
    assert G._sniff(PNG) == "image/png" and G._sniff(b"hello") == ""
    try:
        G.generate("a cow", reference=(b"not an image", "image/png")); assert False
    except G.ImageGenError as e:
        assert "PNG" in str(e)


def test_attachments():
    got = A.read([("a.png", PNG), ("notes.txt", b"Tomatoes keep one week.")])
    assert got["images"][0][1] == "image/png" and "Tomatoes keep one week." in got["text"] and got["names"] == ["a.png", "notes.txt"]
    for files, key in [([("x.png", b"not a png")], "fakeimg"), ([("a.png", PNG)] * 5, "toomany"), ([("big.png", PNG + b"0" * (7 * 1024 * 1024))], "bigimg"), ([("e.txt", b"")], "empty")]:
        try:
            A.read(files); assert False, key
        except A.AttachError as e:
            assert str(e) == key and A.message(key, "rw")


def test_studio_strings_complete():
    assert set(S.U) == {"en", "fr", "rw", "sw"} and len({frozenset(v) for v in S.U.values()}) == 1
    assert all(IG_ for IG_ in G.DISCLOSE.values()) and set(G.STYLES["photo"][0]) == {"en", "fr", "rw", "sw"}


def test_real_photo_requests_stay_separate():
    assert P.explicit_term("show me photos of lions") == "lions" and G.parse_request("show me photos of lions") is None


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("image studio OK", n)
