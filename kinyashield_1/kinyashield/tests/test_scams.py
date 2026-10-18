import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scams_db
from assistant_flow import route, format_guide


class Scams(unittest.TestCase):
    def test_complete_in_four_languages(self):
        self.assertGreaterEqual(scams_db.COUNT, 40)
        for k, v in scams_db.DATA.items():
            self.assertEqual(len(v), 5, k)
            self.assertTrue(v[0], k)
            for i in range(1, 5):
                self.assertEqual(len(v[i]), 4, (k, i))
                self.assertTrue(all(x.strip() for x in v[i]), (k, i))

    def test_list_questions_in_all_languages(self):
        for q, l in [("methods of scams in terms of cybersecurity", "en"), ("give me millions of types of scams with description and examples", "en"),
                     ("méthodes d'arnaque", "fr"), ("uburyo bw'uburiganya bwo kuri interineti", "rw"), ("mbinu za ulaghai", "sw"), ("types of cyber attacks", "en")]:
            e = route(q, l)["entry"]
            self.assertEqual(e["id"], "scam_list", q)
            self.assertEqual(len(e["steps"][l]), scams_db.COUNT, q)

    def test_list_has_description_example_and_protection_and_is_honest(self):
        e = route("methods of scams in terms of cybersecurity", "en")["entry"]
        txt = format_guide(e, "en", "Steps", "src")
        for must in ("Phishing", "SIM swap", "Ransomware", "Example:", "How to protect yourself:", "not a complete list"):
            self.assertIn(must, txt)
        big = route("give me millions of types of scams", "en")["entry"]
        self.assertIn("1,000,000", big["answer"]["en"])
        self.assertIn(str(scams_db.COUNT), big["answer"]["en"])

    def test_requested_number_limits_list(self):
        self.assertEqual(len(route("list 10 types of scams", "en")["entry"]["steps"]["en"]), 10)

    def test_single_methods(self):
        for q, l, sid in [("what is phishing", "en", "scam_phishing"), ("SIM swap", "en", "scam_simswap"), ("romance scam", "en", "scam_romance"),
                          ("how does vishing work", "en", "scam_vishing"), ("quishing", "en", "scam_quishing"), ("deepfake", "fr", "scam_deepfake")]:
            self.assertEqual(route(q, l)["entry"]["id"], sid, q)

    def test_personal_questions_not_hijacked(self):
        for q in ["how do I protect myself from scams", "how do I know a message is a scam", "I gave my PIN to someone who called"]:
            self.assertNotEqual(route(q, "en").get("entry", {}).get("id", ""), "scam_list", q)

    def test_no_instructions_for_committing_fraud(self):
        bad = ("step-by-step to scam", "how to steal", "how to hack someone")
        for v in scams_db.DATA.values():
            for lang in v[1:]:
                for t in lang:
                    self.assertFalse(any(b in t.lower() for b in bad))

    def test_scam_detector_still_first(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN to 0788123456 now to unblock it, or you lose your money today."
        self.assertEqual(route(msg, "en")["kind"], "scam")

    def test_phone_and_computer_lists_still_work(self):
        self.assertEqual(route("give me 50 types of phones with manufacturers", "en")["entry"]["id"], "phone_list")
        self.assertEqual(route("types of computers", "en")["entry"]["id"], "computer_types")


if __name__ == "__main__":
    unittest.main()
