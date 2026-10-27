"""Cybersecurity knowledge expansion: new terms, new scams, natural-language routing to the playbook, and A-vs-B comparisons in four languages."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import streamlit  # noqa
except Exception:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
import assistant_flow as F, cyber_db as C, scams_db as S, cyber_intent as I, cyber_compare as X

def _id(q, lang="en"):
    r = F.route(q, lang)
    e = r.get("entry")
    return (e or {}).get("id") if isinstance(e, dict) else r["kind"]

def test_glossary_grew_and_validates():
    assert C.COUNT >= 670 and C.validate() == []
    for q, want in [("what is salami attack", "cyber_salami-attack"), ("port knocking", "cyber_port-knocking"), ("what is dsar", "cyber_dsar"), ("who is lockbit", "cyber_ransomware-groups"),
                    ("what is a reverse proxy", "cyber_forward-reverse-proxy"), ("reverse shell", "cyber_reverse-shell"), ("what is data diddling", "cyber_data-diddling")]:
        assert _id(q) == want, (q, _id(q))

def test_scam_catalogue_grew():
    assert S.COUNT >= 84
    for q, want in [("what is a task scam", "scam_taskscam"), ("fake payment screenshot", "scam_paymentproof"), ("electricity token scam", "scam_utilitybill"),
                    ("school fees scam", "scam_schoolfees"), ("affinity fraud", "scam_affinity"), ("what is a pump and dump", "scam_pumpdump"), ("mlm scam", "scam_mlm")]:
        assert _id(q) == want, (q, _id(q))

def test_natural_questions_reach_the_playbook_in_all_languages():
    cases = {"how do cybercriminals attack": "cyb_hacker_methods", "how can I avoid falling for scams": "cyb_scam_prevention", "what should I do after being scammed": "cyb_if_scammed",
             "I was scammed what now": "cyb_if_scammed", "how do scammers trick people": "cyb_scam_prevention", "comment éviter les arnaques": "cyb_scam_prevention",
             "j'ai été arnaqué que faire": "cyb_if_scammed", "Nirinda nte uburiganya?": "cyb_scam_prevention", "nimetapeliwa nifanye nini": "cyb_if_scammed",
             "jinsi ya kuepuka utapeli": "cyb_scam_prevention", "uko abahackers bateza ibitero": "cyb_hacker_methods", "wahandisi wa usalama hulindaje mifumo": "cyb_defender_methods",
             "comment les ingénieurs protègent les systèmes": "cyb_defender_methods"}
    for q, want in cases.items():
        assert _id(q, "en" if q.isascii() else "fr") == want, (q, _id(q))
    assert I.find_id("how do hackers hack whatsapp") is None      # specific questions keep their own guide

def test_comparisons():
    for q, l in [("red team vs blue team", "en"), ("difference between a virus and a worm", "en"), ("encryption vs hashing", "en"), ("différence entre phishing et smishing", "fr"),
                 ("itandukaniro hagati ya virus na worm", "rw"), ("tofauti kati ya phishing na vishing", "sw"), ("IDS vs IPS", "en")]:
        e = X.find(q, l)
        assert e and all(e["answer"][x].strip() and e["steps"][x] for x in ("en", "fr", "rw", "sw")), q
    assert X.find("cats vs dogs", "en") is None and X.find("what is phishing", "en") is None and X.find("phishing vs phishing", "en") is None

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("cyber more OK")
