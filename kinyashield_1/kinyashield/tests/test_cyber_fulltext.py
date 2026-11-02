import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import base64
import cyber_fulltext as F
import ai_status

PG = ('<html><title>T</title><nav><p>menu menu menu menu menu menu menu menu menu menu menu</p></nav><article>'
      '<p>Attackers breached the ministry network on Monday and stole thousands of records, officials said.</p><p>Subscribe to our newsletter now please</p>'
      '<p>The ministry said systems were restored and passwords reset for all users after the incident.</p></article></html>')
t, text = F.extract(PG)
assert "breached" in text and "restored" in text and "menu" not in text and "newsletter" not in text
for bad in ("http://127.0.0.1/x", "file:///etc/passwd", "http://169.254.169.254/", "http://localhost/", "ftp://example.com"):
    assert not F.check_url(bad), bad
u = base64.urlsafe_b64encode(b"\x08\x13\x22\x4chttps://example.com/news/a1\xd2\x01").decode().rstrip("=")
r = F.fetch_story("https://news.google.com/rss/articles/" + u, fetch=lambda x: (PG, x))
assert r["url"] == "https://example.com/news/a1" and r["text"] and not r["error"]
assert F.fetch_story("http://127.0.0.1/", fetch=None)["error"] in ("blocked", "unreachable")
def boom(x): raise OSError("net")
assert F.fetch_story("https://example.com/a", fetch=boom)["error"] == "unreachable"
assert F.fetch_story("https://example.com/a", fetch=lambda x: ("<html></html>", x))["error"] == "empty"
asked = []
ai_status.ask = lambda q, lang="en", use_search=False: (asked.append(q) or ("ok", None))
for lang in ("en", "fr", "rw", "sw"):
    assert F.explain_story({"title": "H", "source": "S", "date": "d"}, text, lang) == ("ok", None)
assert "breached" in asked[0] and "untrusted" in asked[0] and "Kinyarwanda" in asked[2]
print("OK cyber fulltext")
