import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assistant_flow import route, suggested, related

SCAM = "Dear customer you won 5,000,000 RWF. Send your PIN and a 20000 RWF fee to claim prize at http://bit.ly/x1 today"

class Flow(unittest.TestCase):
    def test_pasted_scam_uses_existing_detector(self):
        r = route(SCAM, "en"); self.assertEqual(r["kind"], "scam"); self.assertNotEqual(r["result"].verdict, "ok")
    def test_guide_answer_in_each_language(self):
        for q, l, i in [("I shared my PIN with someone", "en", "shared_pin"), ("j'ai perdu mon téléphone", "fr", "lost_phone"),
                        ("Nimepoteza simu yangu", "sw", "lost_phone"), ("I gave my PIN to someone who called", "rw", "shared_pin")]:
            r = route(q, l); self.assertEqual((r["kind"], r["entry"]["id"]), ("guide", i), q)
    def test_unknown_goes_to_ai(self):
        self.assertEqual(route("who is the president of france", "en")["kind"], "ai")
    def test_force_ai_skips_guide_and_detector(self):
        self.assertEqual(route(SCAM, "en", force_ai=True)["kind"], "ai")
    def test_chips_exist_in_all_languages(self):
        for l in ("en", "fr", "rw", "sw"):
            self.assertGreaterEqual(len(suggested(l)), 5)
            self.assertTrue(related(route("How do I write a CV?", "en")["entry"], l))

if __name__ == "__main__":
    unittest.main()
