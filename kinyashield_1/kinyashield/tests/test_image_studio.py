"""Image creation, chat requests, attachments and safety pre-checks (no network, no keys)."""
import os, sys, base64, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for k in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "IMAGE_BASE_URL", "IMAGE_MODEL", "HF_TOKEN", "IMAGE_ALLOW_PUBLIC"):
    os.environ.pop(k, None)
os.environ["IMAGE_ALLOW_PUBLIC"] = "false"   # tests never use the network
import image_gen as G, attachments as A, photo_words as P, image_studio_ui as S

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def _fresh():
    import image_pool as P
    P.CACHE.clear(); P.HEALTH.reset()


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
    _fresh()
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
    _fresh()
    try:
        G.generate("a cow"); assert False
    except G.ImageGenError as e:
        assert str(e) == "not_configured" and "GEMINI_API_KEY" in G.friendly_error(e, "en") and G.friendly_error(e, "rw")
    orig = G._slots
    calls = []
    def bad(*a): calls.append("a"); raise G.ImageGenError("Gemini: quota or rate limit")
    def good(*a): calls.append("b"); return [(PNG, "image/png", "Test")]
    G._slots = lambda: [("a", "gemini", bad), ("b", "hf", good)]
    try:
        assert G.generate("a cow")[0][2] == "Test" and calls == ["a", "b"]
        _fresh(); G._slots = lambda: [("a", "gemini", bad)]
        try:
            G.generate("a cow"); assert False
        except G.ImageGenError as e:
            assert "quota" in str(e) and "secret" not in str(e).lower()
    finally:
        G._slots = orig; _fresh()


def test_scaling_cache_cooldown_rotation_parallel_and_limits():
    import image_pool as P, threading, time
    _fresh(); orig = G._slots; calls = []; lock = threading.Lock()
    def mk(name):
        def f(p, a, n, r, sd):
            with lock: calls.append(name)
            time.sleep(0.02)
            return [(PNG, "image/png", name)]
        return f
    G._slots = lambda: [("g1", "gemini", mk("g1")), ("g2", "gemini", mk("g2")), ("g3", "gemini", mk("g3"))]
    try:
        out = G.generate("a market", n=3)                    # parallel: three pictures, spread over the keys
        assert len(out) == 3 and len(set(calls)) >= 2
        before = len(calls)
        assert G.generate("a market", n=3) and len(calls) == before          # identical request: served from the cache
        G.generate("a market", n=1, variant=1); assert len(calls) == before + 1  # a variation skips the cache
        # rotation: single requests start at different keys
        _fresh(); calls.clear()
        for i in range(6): G.generate(f"p{i}")
        assert len(set(calls)) == 3 and max(calls.count(x) for x in set(calls)) <= 3
        # cooldown: a key that fails with quota is skipped afterwards
        _fresh(); calls.clear()
        def quota(p, a, n, r, sd):
            with lock: calls.append("bad")
            raise G.ImageGenError("Gemini: quota or rate limit")
        G._slots = lambda: [("g1", "gemini", quota), ("g2", "hf", mk("g2"))]
        G.generate("one"); G.generate("two"); G.generate("three")
        assert calls.count("bad") == 1 and calls.count("g2") == 3
        assert P.HEALTH.wait("g1") > 0 and G.status()["cooling"] == 1
    finally:
        G._slots = orig; _fresh()


def test_queue_is_bounded_and_fair_use_limits():
    import image_pool as P
    _fresh(); orig = G._slots
    G._slots = lambda: [("g1", "gemini", lambda *a: [(PNG, "image/png", "T")])]
    os.environ["IMAGE_QUEUE_WAIT"] = "1"; os.environ["IMAGE_MAX_CONCURRENT"] = "1"
    P.configure(1); g = P.GATE; assert g.size == 1 and g.acquire(1)              # the only slot is taken
    try:
        try:
            G.generate("queued"); assert False
        except G.ImageGenError as e:
            assert str(e) == "busy" and "waiting line" in G.friendly_error(e, "en") and G.friendly_error(e, "sw")
    finally:
        g.release(); G._slots = orig; os.environ.pop("IMAGE_QUEUE_WAIT", None); os.environ.pop("IMAGE_MAX_CONCURRENT", None); P.configure(6); _fresh()
    os.environ["IMAGE_PER_MINUTE"] = "2"
    try:
        P.LIMITER = P.Limiter()
        assert G.fair_use("v1")[0] and G.fair_use("v1")[0]
        ok, wait = G.fair_use("v1"); assert not ok and wait >= 1
        assert G.fair_use("v2")[0]                                                # another visitor is not affected
        assert "seconds" in G.friendly_error(G.ImageGenError("limit:30"), "en") and "30" in G.friendly_error(G.ImageGenError("limit:30"), "fr")
    finally:
        os.environ.pop("IMAGE_PER_MINUTE", None)


def test_identical_simultaneous_requests_share_one_generation():
    import threading, time
    os.environ["IMAGE_ALLOW_PUBLIC"] = "false"
    G.POOL.CACHE.clear(); G.POOL.HEALTH.reset()
    n = [0]; lock = threading.Lock(); old = G._slots
    def slow(p, a, c, r, sd):
        with lock: n[0] += 1
        time.sleep(0.2); return [(PNG, "image/png", "Fake")]
    G._slots = lambda: [("gemini#1", "gemini", slow)]
    try:
        out = []
        ts = [threading.Thread(target=lambda: out.append(G.generate("one shared idea", "1:1", 1))) for _ in range(25)]
        [t.start() for t in ts]; [t.join(20) for t in ts]
        assert len(out) == 25 and all(o[0][2] == "Fake" for o in out) and n[0] == 1, (len(out), n[0])
    finally:
        G._slots = old; G.POOL.CACHE.clear()


def test_pool_pieces():
    import image_pool as P
    c = P.Cache(max_bytes=100, ttl=60, max_items=3)
    for i in range(5): c.put(str(i), i, 30)
    assert c.get("0") is None and c.get("4") == 4 and c.stats()["bytes"] <= 100       # LRU + byte cap
    t = [0.0]; h = P.Health(clock=lambda: t[0])
    h.fail("x", "quota"); assert not h.available("x"); t[0] = 121; assert h.available("x")
    h.fail("x", "quota"); h.fail("x", "quota"); assert h.wait("x") > 400               # grows with repeated failure
    h.ok("x"); assert h.available("x")
    assert P.classify("Gemini: quota or rate limit") == "quota" and P.classify("HTTP 503") == "busy" and P.classify("key rejected") == "auth" and P.classify("weird") == "other"


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
