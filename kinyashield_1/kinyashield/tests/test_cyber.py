"""Cybersecurity glossary: data quality, routing in four languages, photos subject, and no clash with the scam catalogue."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cyber_db as C
import assistant_flow as F


def test_data_is_complete_and_valid():
    assert C.COUNT >= 250
    assert C.validate() == []
    for r in C.TERMS:
        assert len(r[4].split()) <= 8, r[0]


def test_terms_answer_in_every_language():
    for q, l in [("what is a firewall", "en"), ("firewall ni iki", "rw"), ("maana ya firewall", "sw"), ("qu'est-ce que le pare-feu", "fr"), ("encryption", "en"), ("define zero-day", "en"),
                 ("what is SIEM", "en"), ("what is a botnet", "en"), ("what is MFA", "en"), ("uses of VPN", "en"), ("what does hashing mean", "en")]:
        r = F.route(q, l)
        assert r["kind"] == "guide" and r["entry"]["id"].startswith("cyber_"), (q, r["kind"], r.get("entry", {}).get("id"))
        e = r["entry"]
        assert e.get("photo_query"), q
        txt = F.format_guide(e, l, "s", "src")
        assert len(txt) > 150 and "Meaning" in txt or "Sens" in txt or "Icyo bivuze" in txt or "Maana" in txt, q


def test_applications_are_in_every_answer():
    row = C.lookup("firewall")
    for j in (7, 9, 11, 13):
        assert len(row[j]) > 40


def test_lists_and_clash_with_scams():
    assert F.route("list all cybersecurity terms", "en")["entry"]["id"] == "cyber_list"
    assert F.route("termes de cybersécurité", "fr")["entry"]["id"] == "cyber_list"
    assert F.route("malware terms", "en")["entry"]["id"] == "cyber_cat_malware"
    assert F.route("methods of scams in terms of cybersecurity", "en")["entry"]["id"] == "scam_list"
    e = F.route("what is phishing", "en")["entry"]
    assert e["id"] == "scam_phishing" and e.get("photo_query")           # the scam catalogue answers, and it still gets photos
    assert len(C.overview("en")["steps"]["en"]) <= 16                    # one readable line per category


def test_other_questions_not_hijacked():
    for q in ["how do I make a strong password", "I clicked a link, what now", "what is a mango", "translate firewall into french", "who owns you"]:
        r = F.route(q, "en")
        assert not str(r.get("entry", {}).get("id", "")).startswith("cyber_"), q


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("cyber ok")
