"""Real-photo search across several sources: parallel merge, failing source skipped, cache, safety, https-only links (no network: sources are faked)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for k in ("PIXABAY_API_KEY", "PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY"):
    os.environ.pop(k, None)
import web_photos as W, image_pool as POOL


def _fake(name, n=3, boom=False, calls=None):
    def f(q, page, per):
        if calls is not None:
            calls.append(name)
        if boom:
            raise OSError("down")
        return [W._item(f"https://img.example.org/{name}/{i}.jpg", f"https://img.example.org/{name}/{i}.jpg", f"{q} {i}", "Ann", "CC BY 4.0", f"https://example.org/{name}/{i}", name) for i in range(n)]
    return f


def test_sources_merge_interleave_and_survive_a_failing_source():
    old = W.SOURCES; POOL.HEALTH.reset(); W.CACHE.clear()
    try:
        calls = []
        W.SOURCES = [("A", _fake("A", calls=calls)), ("B", _fake("B", boom=True, calls=calls)), ("C", _fake("C", 2, calls=calls))]
        r = W.search("tomato harvest")
        names = [i["source"] for i in r["items"]]
        assert names[:2] == ["A", "C"] and set(names) == {"A", "C"} and len(names) == 5, names     # interleaved, B skipped
        assert r["sources"]["B"] is None and r["sources"]["A"] == 3
        n = len(calls)
        again = W.search("tomato harvest")
        assert again["cached"] and len(calls) == n                 # served from the shared cache: no new source calls
        assert not POOL.HEALTH.available("web:B")                  # the failing source is cooling down
        W.CACHE.clear(); calls.clear()
        W.search("maize")
        assert "B" not in calls                                    # ...and is not asked again during the cool-down
    finally:
        W.SOURCES = old; POOL.HEALTH.reset(); W.CACHE.clear()


def test_safety_and_url_rules():
    assert W.search("nude people")["blocked"] and W.search("x")["items"] == []
    assert W._safe_url("http://a.example.org/x.jpg") == "" and W._safe_url("https://127.0.0.1/x.jpg") == "" and W._safe_url("https://user:pw@a.example.org/x") == ""
    assert W._safe_url("https://a.example.org/x.jpg") == "https://a.example.org/x.jpg"
    assert W._item("http://bad", None, "t", "", "", "", "S") is None


def test_older_shape_and_credit_and_sources_list():
    old = W.SOURCES; POOL.HEALTH.reset(); W.CACHE.clear()
    try:
        W.SOURCES = [("A", _fake("A"))]
        ph = W.photos("lion", 2)
        assert len(ph) == 2 and set(ph[0]) == {"caption", "url", "license", "page"} and ph[0]["url"].startswith("https://")
        assert "CC BY 4.0" in W.credit(W.search("lion")["items"][0])
    finally:
        W.SOURCES = old; POOL.HEALTH.reset(); W.CACHE.clear()
    assert W.configured()[:2] == ["Wikimedia Commons", "Openverse"] and all(l in W.NOTE and l in W.BLOCKED for l in ("en", "fr", "rw", "sw"))


if __name__ == "__main__":
    test_sources_merge_interleave_and_survive_a_failing_source(); test_safety_and_url_rules(); test_older_shape_and_credit_and_sources_list(); print("web photos OK")
