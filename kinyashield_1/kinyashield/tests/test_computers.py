import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import computers_db
from assistant_flow import route, format_guide

class Computers(unittest.TestCase):
    def test_complete_in_four_languages(self):
        self.assertGreaterEqual(computers_db.COUNT, 18)
        for k, (aliases, f, kind, texts) in computers_db._DATA.items():
            self.assertIn(k, computers_db._WIKI)
            for l in computers_db.LANGS:
                self.assertEqual(len(texts[l]), 4, (k, l))
                self.assertTrue(all(x.strip() for x in texts[l]), (k, l))
    def test_questions_route_to_computers(self):
        for q, l, cid in [("how does a laptop work", "en", "computer_laptop"), ("what is a server", "en", "computer_server"),
                          ("ni iki seriveri", "rw", "computer_server"), ("comment fonctionne un superordinateur", "fr", "computer_supercomputer"),
                          ("simu janja ni nini", "sw", "computer_smartphone"), ("raspberry pi", "en", "computer_sbc"), ("ENIAC", "en", "computer_eniac"),
                          ("how does a computer work", "en", "computer_computer"), ("types of computers", "en", "computer_types")]:
            r = route(q, l); self.assertEqual(r["kind"], "guide", q); self.assertEqual(r["entry"]["id"], cid, q)
    def test_other_questions_not_hijacked(self):
        for q in ["what is a computer virus", "what does DNS mean", "what is the meaning of life", "how does a server get hacked", "what should I do if I lose my mobile phone"]:
            self.assertFalse(str(route(q, "en").get("entry", {}).get("id", "")).startswith("computer_"), q)
    def test_scam_detector_still_first(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN to 0788123456 now to unblock it, or you lose your money today."
        self.assertEqual(route(msg, "en")["kind"], "scam")
    def test_format_guide_works(self):
        e = route("how does a laptop work", "en")["entry"]
        self.assertIn("Laptop", format_guide(e, "en", "Steps", "src"))
    def test_photo_failure_is_graceful(self):
        e = route("laptop", "en")["entry"]
        computers_db._CACHE.clear()
        with mock.patch.object(computers_db, "_get_json", side_effect=OSError("offline")), mock.patch.object(computers_db, "_head_ok", side_effect=OSError("offline")):
            self.assertIsNone(computers_db.resolve_image(e, "en"))
        self.assertTrue(computers_db.missing_photo_note("rw"))
    def test_only_commons_images_accepted(self):
        e = route("laptop", "en")["entry"]
        computers_db._CACHE.clear()
        fair = {"thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/x.jpg/320px-x.jpg"}, "originalimage": {"source": "https://upload.wikimedia.org/wikipedia/en/a/ab/x.jpg"}}
        with mock.patch.object(computers_db, "_get_json", return_value=fair), mock.patch.object(computers_db, "_head_ok", return_value=False):
            self.assertIsNone(computers_db.resolve_image(e, "en"))
        computers_db._CACHE.clear()
        free = {"thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/x.jpg/320px-x.jpg"}, "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Laptop"}}}
        with mock.patch.object(computers_db, "_get_json", return_value=free):
            r = computers_db.resolve_image(e, "fr")
        self.assertIn("/wikipedia/commons/", r["url"]); self.assertIn("Laptop", r["caption"]); self.assertTrue(r["page"].startswith("https://en.wikipedia.org"))
        computers_db._CACHE.clear()

if __name__ == "__main__":
    unittest.main()
