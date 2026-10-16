import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import names_db
from assistant_flow import route, format_guide

class Names(unittest.TestCase):
    def test_table_is_complete_in_four_languages(self):
        self.assertGreaterEqual(names_db.COUNT, 150)
        for d in names_db._NAMES:
            self.assertIn(d["origin"], names_db.ORIGIN, d["name"])
            for l in names_db.LANGS:
                self.assertTrue(d["meaning"][l].strip(), (d["name"], l))
    def test_no_duplicate_primary_names(self):
        n = [d["name"] for d in names_db._NAMES]
        self.assertEqual(len(n), len(set(n)))
    def test_questions_in_each_language(self):
        for q, l, name in [("What does the name Aline mean?", "en", "Aline"), ("meaning of Uwimana", "en", "Uwimana"),
                           ("izina Mugisha risobanura iki", "rw", "Mugisha"), ("signification du prénom Béatrice", "fr", "Béatrice"),
                           ("maana ya jina Baraka", "sw", "Baraka"), ("Hamza", "en", "Hamza")]:
            r = route(q, l); self.assertEqual(r["kind"], "guide", q); self.assertIn(name, r["entry"]["names"], q)
    def test_ordinary_words_are_not_hijacked(self):
        for q in ["meaning of life", "what does DNS mean", "what is the meaning of peace", "what does hope mean", "How do I write a CV?", "what he said",
                  "what is your name"]:
            self.assertNotEqual(route(q, "en").get("entry", {}).get("id"), "name_meaning", q)
    def test_word_names_need_the_word_name(self):
        self.assertEqual(route("meaning of the name Grace", "en")["entry"]["names"], ["Grace"])
    def test_unknown_name_goes_on(self):
        self.assertNotEqual(route("what does the name Zzyzx mean", "en")["kind"], "scam")
        self.assertEqual(route("what does the name Zzyzx mean", "en")["kind"], "ai")
    def test_format_uses_name_label(self):
        e = route("what does the name Aline mean", "en")["entry"]
        out = format_guide(e, "en", "Steps", "src")
        self.assertIn("About this name", out); self.assertIn("noble", out); self.assertNotIn("*Steps*", out)
    def test_scam_and_guide_still_work(self):
        self.assertEqual(route("I gave my PIN to someone who called", "en")["entry"]["id"], "shared_pin")

if __name__ == "__main__":
    unittest.main()
