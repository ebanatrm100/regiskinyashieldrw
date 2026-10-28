"""Gap-fill from the cybersecurity coverage audit: new glossary terms and scam families answer in four languages."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import streamlit  # noqa
except Exception:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
import cyber_db as C, scams_db as S, assistant_flow as F

NEW_TERMS = ["confidentiality", "integrity", "availability", "hacker", "access control list", "identity provider", "service account", "authenticator app", "anti-forensics", "human firewall",
             "chaos engineering", "post-exploitation", "war driving", "time bomb", "thread hijacking", "unpatched vulnerability", "diceware", "credit freeze", "llm jailbreak", "model theft",
             "airdrop scam", "nft scam", "approval phishing", "crypto mixer", "bridge hack", "blockchain analysis", "red flags", "push fatigue", "parental control", "cybercrime law"]
NEW_SCAMS = ["fakeinsurance", "usedgoods", "fakecertificate", "goldscam", "juicejacking", "browserext", "surveyscam", "socialverify", "faithscam", "tollsms", "cardtrap"]

def test_glossary_valid_and_new_terms_found():
    assert C.validate() == []
    assert C.COUNT >= 770
    assert [t for t in NEW_TERMS if not C.lookup(t)] == []

def test_new_scam_families_complete():
    for k in NEW_SCAMS:
        v = S.DATA[k]
        assert v[0] and len(v) == 5, k
        for lang_block in v[1:]:
            assert len(lang_block) == 4 and all(len(x.strip()) > 30 for x in lang_block), k
    assert S.COUNT >= 100

def test_questions_route_in_all_languages():
    cases = [("what is confidentiality", "en", "confidentiality"), ("c'est quoi un hacker", "fr", "hacker"), ("hacker ni iki", "rw", "hacker"), ("nini maana ya service account", "sw", "service-account"),
             ("what is a toll scam", "en", "tollsms"), ("ulaghai wa dhahabu", "sw", "goldscam"), ("uburiganya bwa airdrop ya crypto", "rw", "airdrop-scam"),
             ("signes d'arnaque", "fr", "scam-red-flags"), ("dalili za utapeli", "sw", "scam-red-flags"), ("what is juice jacking", "en", "juicejacking"), ("arnaque assurance", "fr", "fakeinsurance")]
    for q, l, frag in cases:
        r = F.route(q, l); e = r.get("entry") or {}
        assert r["kind"] == "guide" and frag in str(e.get("id", "")), (q, l, r["kind"], e.get("id"))

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("cyber gap OK")
