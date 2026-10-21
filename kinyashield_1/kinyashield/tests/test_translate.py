"""Translations: exact bank answers, word dictionary, reverse lookup, word-by-word fallback, honest wording."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import translate_db as T
import translation_words as W
import meta_guard as MG
import assistant_flow as F


def t(phrase, target, src_ui="en"):
    r = T.translate(phrase, target, src_ui)
    return r and r["text"][target]


def test_owner_questions_in_every_language():
    for q in ["who is your owner", "Who owns you?", "Who is your owner?"]:
        assert t(q, "rw").startswith("Uri uwa nde?"), q
        assert "Nyirawe ni nde?" in t(q, "rw")
        assert t(q, "fr").startswith("Qui est ton propriétaire ?")
        assert t(q, "sw").startswith("Mmiliki wako ni nani?")
    # typing it back in Kinyarwanda (with or without the space) finds the English sentence
    assert t("uri uwa nde", "en").startswith("Who is your owner?")
    assert t("uri uwande", "en").startswith("Who is your owner?")
    assert t("Qui est ton propriétaire ?", "rw").startswith("Uri uwa nde?")


def test_words_all_directions():
    cases = [("password", "rw", "Ijambo ry'ibanga"), ("password", "sw", "Nenosiri"), ("password", "fr", "Mot de passe"), ("nenosiri", "rw", "Ijambo ry'ibanga"),
             ("pare-feu", "sw", "ngome ya mtandao (firewall)"), ("antivirus", "rw", "porogaramu irwanya virusi"), ("encryption", "fr", "chiffrement"),
             ("hacker", "rw", "Hakeri"), ("scam", "rw", "Ubutekamutwe"), ("security", "sw", "Usalama"), ("computer", "rw", "Mudasobwa"), ("umutekano", "fr", "Sécurité")]
    for phrase, target, want in cases:
        got = t(phrase, target)
        assert got and got.lower().startswith(want.lower()), (phrase, target, got)


def test_dictionary_is_clean():
    assert len(W.WORDS) >= 400
    for row in W.WORDS:
        assert len(row) == 5 and all(row[:4]), row
    # no Kinyarwanda or Kiswahili field may just repeat the French or English one by accident, unless it is a loan word kept on purpose
    allowed = {"VPN", "robot", "video", "ID", "CV", "spam", "menu", "PIN", "Wi-Fi", "WiFi", "app", "code", "police", "internet", "protocol"}
    for en, fr, rw, sw, _ in W.WORDS:
        for l, v in (("rw", rw), ("sw", sw)):
            if v.lower() == en.lower() and en not in allowed and " " not in en:
                raise AssertionError((en, l))


def test_breakdown_is_honest():
    pieces = T.breakdown("who is the owner of this firewall", "rw")
    texts = " ".join(a + b for a, b in pieces)
    assert "nyiri" in texts and "uyu" in texts
    ans, ok = MG.translation_answer("the sky is very beautiful today", "rw", "en")
    assert ok is False and "not a full sentence translation" in ans and "GEMINI_API_KEY" in ans


def test_bank_exact_in_chat_route():
    for q, l in [("translate hello into kinyarwanda", "en"), ("how do you say password in Kiswahili", "en"), ("Traduis mot de passe en kinyarwanda", "fr"), ("translate firewall into french", "en")]:
        r = F.route(q, l)
        assert r["kind"] == "guide" and r["entry"]["id"].startswith("translate_"), (q, r["kind"])




def test_more_words_plurals_codes_and_ambiguity():
    assert t("apple", "fr") == "pomme" and t("apples", "fr") == "pomme"
    assert t("banana", "rw").startswith("Igitoki") and t("eat", "sw") == "Kula" and t("to eat", "fr") == "Manger"
    assert t("Monday", "rw") == "Kuwa mbere" and t("seven", "rw") == "Karindwi" and t("water", "sw") == "Maji"
    for q, code in [("translate how are you into rw", "rw"), ("translate hello into sw", "sw"), ("translate thanks to fr", "fr")]:
        assert MG.parse_translation(q)[1] == code, q
    r = T.translate("bibi", "fr", "en")            # Kinyarwanda "bad" and Kiswahili "grandmother"
    assert r["others"] and any("grand" in o["text"]["fr"] for o in r["others"] + [r])


def test_cyberattack_and_owner_still_right_after_new_words():
    assert t("who is your owner", "rw").startswith("Uri uwa nde?")
    assert t("cyberattack", "sw") == "shambulio la mtandaoni"

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("translate ok")
