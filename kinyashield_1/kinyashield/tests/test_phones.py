import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import phones_db
from assistant_flow import route, format_guide


class Phones(unittest.TestCase):
    def test_at_least_50_brands_complete_in_four_languages(self):
        self.assertGreaterEqual(phones_db.COUNT, 50)
        for k, (aliases, brand, company, country, lines, os_, tag, q) in phones_db._DATA.items():
            self.assertTrue(all(str(x).strip() for x in (aliases, brand, company, lines, os_, q)), k)
            self.assertIn(country, phones_db._COUNTRY, k)
            self.assertIn(tag, phones_db._TAGS, k)
            for l in phones_db.LANGS:
                e = phones_db._entry(k)
                self.assertTrue(e["title"][l] and e["answer"][l] and len(e["steps"][l]) == 5, (k, l))

    def test_no_duplicate_aliases_across_brands(self):
        seen = {}
        for alias, key in phones_db._INDEX:
            self.assertNotIn(alias, seen, alias) if seen.get(alias, key) != key else None
            seen[alias] = key

    def test_list_question_gives_all_brands_with_gallery(self):
        r = route("give me 50 types of phones or brands of phones with their manufacturing company and their photos", "en")
        e = r["entry"]
        self.assertEqual(e["id"], "phone_list")
        self.assertEqual(len(e["gallery"]), phones_db.COUNT)
        self.assertGreaterEqual(len(e["steps"]["en"]), 50)
        txt = format_guide(e, "en", "Steps", "src")
        for must in ("Samsung Electronics", "Apple Inc.", "Transsion Holdings", "Xiaomi Corporation"):
            self.assertIn(must, txt)

    def test_requested_number_limits_the_list(self):
        e = route("list 10 phone brands", "en")["entry"]
        self.assertEqual(len(e["gallery"]), 10)
        e = route("give me 100 phone brands", "en")["entry"]
        self.assertEqual(len(e["gallery"]), phones_db.COUNT)
        self.assertIn("100", e["answer"]["en"])

    def test_lists_in_all_languages(self):
        for q, l in [("marques de téléphones", "fr"), ("ibirango bya telefoni", "rw"), ("chapa za simu", "sw")]:
            self.assertEqual(route(q, l)["entry"]["id"], "phone_list", q)

    def test_single_brands(self):
        for q, l, pid in [("Tecno", "en", "phone_tecno"), ("who makes Infinix phones", "en", "phone_infinix"), ("what is Huawei", "en", "phone_huawei"),
                          ("iphone", "en", "phone_iphone"), ("google pixel", "en", "phone_pixel"), ("Honor phone", "en", "phone_honor"), ("nokia", "fr", "phone_nokia")]:
            self.assertEqual(route(q, l)["entry"]["id"], pid, q)

    def test_facts(self):
        self.assertIn("Transsion Holdings", phones_db._entry("tecno")["steps"]["en"][0])
        self.assertIn("Samsung Electronics", phones_db._entry("samsung")["steps"]["en"][0])
        self.assertIn("Kigali", phones_db._entry("mara")["steps"]["en"][1])
        self.assertIn("Corée du Sud", phones_db._entry("samsung")["steps"]["fr"][1])

    def test_other_questions_not_hijacked(self):
        for q in ["what should I do if I lose my phone", "types of phone scams", "what is the meaning of honor", "nothing", "my phone number was used by a scammer",
                  "how do I protect my phone from viruses", "what is a smartphone", "types of computers", "what is android", "how does a phone work"]:
            self.assertFalse(str(route(q, "en").get("entry", {}).get("id", "")).startswith("phone_"), q)

    def test_scam_detector_still_first(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN to 0788123456 now to unblock it, or you lose your money today."
        self.assertEqual(route(msg, "en")["kind"], "scam")

    def test_pick_photo_skips_logos_and_wrong_types(self):
        data = {"query": {"pages": {
            "1": {"title": "File:Samsung logo.png", "index": 1, "imageinfo": [{"mime": "image/png", "thumburl": "https://upload.wikimedia.org/a/logo.png"}]},
            "2": {"title": "File:Galaxy.svg", "index": 2, "imageinfo": [{"mime": "image/svg+xml", "thumburl": "https://upload.wikimedia.org/a/g.svg.png"}]},
            "3": {"title": "File:Galaxy S9 front.jpg", "index": 3, "imageinfo": [{"mime": "image/jpeg", "thumburl": "https://upload.wikimedia.org/a/s9.jpg"}]},
            "4": {"title": "File:Other.jpg", "index": 4, "imageinfo": [{"mime": "image/jpeg", "thumburl": "https://evil.example/o.jpg"}]}}}}
        self.assertEqual(phones_db.pick_photo(data), ("File:Galaxy S9 front.jpg", "https://upload.wikimedia.org/a/s9.jpg"))
        self.assertIsNone(phones_db.pick_photo({}))
        self.assertIsNone(phones_db.pick_photo({"query": {"pages": {"1": {"title": "File:x.jpg", "imageinfo": [{"mime": "image/jpeg", "thumburl": "https://evil.example/x.jpg"}]}}}}))

    def test_photo_success_and_offline_failure(self):
        phones_db._CACHE.clear()
        good = {"query": {"pages": {"3": {"title": "File:Galaxy S9 front.jpg", "index": 1, "imageinfo": [{"mime": "image/jpeg", "thumburl": "https://upload.wikimedia.org/a/s9.jpg"}]}}}}
        e = phones_db._entry("samsung")
        with mock.patch.object(phones_db, "_get_json", return_value=good):
            img = phones_db.resolve_image(e, "en")
        self.assertEqual(img["url"], "https://upload.wikimedia.org/a/s9.jpg")
        self.assertIn("commons.wikimedia.org/wiki/File:Galaxy_S9_front.jpg", img["page"])
        phones_db._CACHE.clear()
        with mock.patch.object(phones_db, "_get_json", side_effect=OSError("offline")):
            self.assertIsNone(phones_db.resolve_image(e, "en"))
            self.assertEqual(phones_db.resolve_many(e and [{"name": "x", "query": "q"}], "en"), [])
        self.assertTrue(phones_db.missing_photo_note("rw"))

    def test_resolve_many_returns_found_only(self):
        phones_db._CACHE.clear()
        def fake(url, timeout=6):
            if "Good" in url:
                return {"query": {"pages": {"1": {"title": "File:A.jpg", "index": 1, "imageinfo": [{"mime": "image/jpeg", "thumburl": "https://upload.wikimedia.org/a.jpg"}]}}}}
            raise OSError("no")
        with mock.patch.object(phones_db, "_get_json", side_effect=fake):
            out = phones_db.resolve_many([{"name": "G", "query": "Good phone"}, {"name": "B", "query": "Bad phone"}], "en")
        self.assertEqual([o["name"] for o in out], ["G"])


if __name__ == "__main__":
    unittest.main()
