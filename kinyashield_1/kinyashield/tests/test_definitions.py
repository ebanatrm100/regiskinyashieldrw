import os, sys, unittest, collections, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import definitions_db as D
from assistant_flow import route, format_guide


def eid(q, lang="en"):
    r = route(q, lang)
    return r.get("entry", {}).get("id") if r["kind"] == "guide" else r["kind"]


class Definitions(unittest.TestCase):
    def test_bank_is_large_and_complete_in_four_languages(self):
        self.assertGreaterEqual(D.count(), 180)
        for r in D.ROWS:
            self.assertIn(r["cat"], "lgcsmweha", r["titles"]["en"])
            for l in D.LANGS:
                self.assertTrue(r["titles"][l].strip(), (r["titles"]["en"], l))
                self.assertGreater(len(r["defs"][l]), 40, (r["titles"]["en"], l))

    def test_each_alias_points_to_one_entry_unless_listed(self):
        seen = collections.defaultdict(set)
        for i, r in enumerate(D.ROWS):
            for n in list(r["aliases"]) + list(r["titles"].values()):
                for form in {n, re.sub(r"\([^)]*\)", " ", n)}:
                    k = D._key(D.fold(form).split())
                    for v in (D._variants(k) if k else []):
                        seen[v].add(i)
        # Only these deliberate overlaps exist (the earlier entry in the bank wins)
        allowed = {"porogaramu", "programu", "imibare", "computer program"}
        clashes = {" ".join(k): [D.ROWS[j]["titles"]["en"] for j in v] for k, v in seen.items()
                   if len(v) > 1 and not any(a in " ".join(k) for a in allowed)}
        self.assertEqual(clashes, {})

    def test_definition_questions_in_each_language(self):
        cases = [("What is English?", "en", "def_english"), ("what is a computer", "en", "def_computer"), ("define noun", "en", "def_noun"),
                 ("c'est quoi un ordinateur ?", "fr", "def_computer"), ("Qu'est-ce que le Wi-Fi ?", "fr", "def_wi_fi"),
                 ("Mudasobwa ni iki?", "rw", "def_computer"), ("Icyongereza ni iki", "rw", "def_english"), ("Ikinyarwanda ni iki?", "rw", "def_kinyarwanda"),
                 ("Kompyuta ni nini?", "sw", "def_computer"), ("maana ya kivumishi", "sw", "def_adjective"), ("What is democracy", "en", "def_democracy"),
                 ("what is photosynthesis", "en", "def_photosynthesis"), ("what is post-harvest loss", "en", "def_post_harvest_loss"),
                 ("what is malaria", "en", "def_malaria"), ("what is mobile money", "en", "def_mobile_money"), ("what is GDP", "en", "def_gdp")]
        for q, l, want in cases:
            self.assertEqual(eid(q, l), want, q)

    def test_answer_text_follows_the_asked_language(self):
        for l, word in [("en", "network"), ("fr", "réseau"), ("rw", "umuyoboro"), ("sw", "mtandao")]:
            r = route({"en": "what is a network", "fr": "qu'est-ce qu'un réseau", "rw": "umuyoboro ni iki", "sw": "mtandao ni nini"}[l], l)
            self.assertEqual(r["kind"], "guide")
            text = format_guide(r["entry"], l, "Steps", "Source")
            self.assertIn(word, text.lower(), l)

    def test_health_definitions_carry_a_medical_note(self):
        r = route("what is malaria", "en")
        self.assertIn("not medical advice", " ".join(r["entry"]["steps"]["en"]).lower())

    def test_other_routes_are_not_hijacked(self):
        # computers keep their photo answers, names keep name meanings, the guide keeps its longer answers
        self.assertEqual(route("how does a laptop work", "en")["entry"]["id"][:4], "comp")
        self.assertNotEqual(eid("what is a laptop"), "def_computer")
        self.assertEqual(route("what does the name Aline mean", "en")["entry"]["id"], "name_meaning")
        for q in ["what is DNS", "what is phishing", "what is an IP address", "how do I improve my English", "how does a computer work",
                  "what is your name", "meaning of life", "what is the mean of 4, 6 and 8"]:
            self.assertFalse(str(eid(q)).startswith("def_"), q)

    def test_unknown_terms_go_on_to_the_ai(self):
        for q in ["what is flibbertigibbet", "what is the capital of Peru", "mudasobwa ya quantum ni iki cyane cyane ku mashuri makuru"]:
            self.assertFalse(str(eid(q)).startswith("def_"), q)

    def test_scam_detection_still_wins(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN and OTP to 0788123456 now to get your prize of 500000 RWF or lose it."
        self.assertEqual(route(msg, "en")["kind"], "scam")


if __name__ == "__main__":
    unittest.main()
