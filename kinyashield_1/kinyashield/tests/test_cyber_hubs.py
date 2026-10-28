"""Cybersecurity overview hubs: questions in four languages reach the right hub, and every hub is complete in all four languages."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import streamlit  # noqa
except Exception:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
import assistant_flow as F, cyber_playbook_db as P

CASES = [
    ("what are the types of malware", "en", "cyb_malware_types"), ("quels sont les types de logiciels malveillants", "fr", "cyb_malware_types"),
    ("Ni ubuhe bwoko bwa malware?", "rw", "cyb_malware_types"), ("Aina za programu hasidi ni zipi?", "sw", "cyb_malware_types"),
    ("cybersecurity tools list", "en", "cyb_security_tools"), ("quels sont les outils de cybersécurité", "fr", "cyb_security_tools"),
    ("Ni ibihe bikoresho by'umutekano wa interineti?", "rw", "cyb_security_tools"), ("Zana za usalama wa mtandao ni zipi?", "sw", "cyb_security_tools"),
    ("what do security engineers do", "en", "cyb_engineer_role"), ("what does a soc analyst do", "en", "cyb_engineer_role"),
    ("injeniyeri w'umutekano akora iki", "rw", "cyb_engineer_role"), ("mhandisi wa usalama hufanya nini", "sw", "cyb_engineer_role"),
    ("what are social engineering techniques", "en", "cyb_social_engineering"), ("Abatekamutwe batuma bate abantu bohereza amafaranga?", "rw", "cyb_social_engineering"),
    ("how do hackers steal passwords", "en", "cyb_password_attacks"), ("comment les pirates volent des mots de passe", "fr", "cyb_password_attacks"), ("Wadukuzi huiba nywila vipi?", "sw", "cyb_password_attacks"),
    ("how to do a security audit", "en", "cyb_security_audit"), ("jinsi ya kufanya ukaguzi wa usalama", "sw", "cyb_security_audit"),
    ("what are the most common scams in Rwanda", "en", "cyb_scam_catalog"), ("Ni ubuhe buriganya bukunze kuba mu Rwanda?", "rw", "cyb_scam_catalog"), ("quelles sont les arnaques courantes au Rwanda", "fr", "cyb_scam_catalog"),
    ("how do I protect my company network", "en", "cyb_secure_network"), ("comment protéger mon réseau d'entreprise", "fr", "cyb_secure_network"),
    ("Nakwirinda nte uburiganya bwa mobile money?", "rw", "cyb_protect_momo"), ("Nitaepukaje utapeli wa pesa za simu?", "sw", "cyb_protect_momo"),
]
NEW = ["cyb_malware_types", "cyb_security_tools", "cyb_engineer_role", "cyb_social_engineering", "cyb_password_attacks", "cyb_security_audit", "cyb_scam_catalog"]


def test_routing():
    bad = []
    for q, l, want in CASES:
        r = F.route(q, l); e = r.get("entry") or {}
        got = (e.get("id") if isinstance(e, dict) else None) or r.get("id")
        if got != want:
            bad.append((q, l, want, got, r["kind"]))
    assert not bad, bad


def test_new_hubs_complete_in_four_languages():
    by = {e["id"]: e for e, _ in P._RAW}
    for i in NEW:
        e = by[i]
        for l in ("en", "fr", "rw", "sw"):
            assert e["title"][l].strip() and len(e["answer"][l]) > 120 and len(e["steps"][l]) >= 8 and e["steps_label"][l].strip(), (i, l)
        assert len({len(e["steps"][l]) for l in ("en", "fr", "rw", "sw")}) == 1, i   # same number of points in every language
    assert len(P.IDS) == len(set(P.IDS))


def test_safe_framing():
    by = {e["id"]: e for e, _ in P._RAW}
    assert "written permission" in " ".join(by["cyb_security_tools"]["steps"]["en"]) + by["cyb_security_tools"]["answer"]["en"]
    assert "Awareness" in by["cyb_password_attacks"]["answer"]["en"]


if __name__ == "__main__":
    test_routing(); test_new_hubs_complete_in_four_languages(); test_safe_framing(); print("cyber hubs OK")
