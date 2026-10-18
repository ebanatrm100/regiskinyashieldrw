import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assistant_flow import route, format_guide


class Owner(unittest.TestCase):
    def test_owner_question_in_all_languages(self):
        for q, l in [("Who is your owner", "en"), ("who owns you?", "en"), ("who is the owner of this app", "en"), ("Qui est ton propriétaire ?", "fr"), ("qui te possède", "fr"),
                     ("Nyirawe ni nde?", "rw"), ("Ni nde nyirawe", "rw"), ("Mmiliki wako ni nani?", "sw"), ("nani anakumiliki", "sw")]:
            r = route(q, l)
            self.assertEqual(r["entry"]["id"], "owner", q)
            self.assertIn("Regis TWIRINGIYIMANA", format_guide(r["entry"], l, "s", "src"), q)

    def test_answer_matches_question_language_and_role(self):
        for q, word in [("who owns you", "Cybersecurity and Infrastructure Security Engineer"), ("Qui est ton propriétaire", "ingénieur en cybersécurité et en sécurité des infrastructures"),
                        ("Nyirawe ni nde?", "injeniyeri"), ("Mmiliki wako ni nani", "Mhandisi wa Usalama wa Mtandao na Miundombinu")]:
            txt = format_guide(route(q, "en")["entry"], "en", "s", "src")   # chat language en, question language differs
            self.assertIn(word, txt, q)

    def test_other_questions_not_hijacked(self):
        for q in ["who owns Tecno", "who is the owner of Apple", "what is ownership", "Mmiliki wa nyumba", "my phone owner", "who is the president of france"]:
            self.assertNotEqual(route(q, "en").get("entry", {}).get("id"), "owner", q)

    def test_scam_detector_still_first(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN to 0788123456 now to unblock it, or you lose your money today."
        self.assertEqual(route(msg, "en")["kind"], "scam")


if __name__ == "__main__":
    unittest.main()
