import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import room_banner as R


class RoomBanner(unittest.TestCase):
    def test_illustration_is_bundled_and_valid_svg(self):
        svg = R.illustration_svg()
        self.assertTrue(svg.lstrip().startswith("<svg"))
        self.assertIn("</svg>", svg)
        self.assertLess(len(svg), 400_000)

    def test_fallback_is_a_labelled_illustration_in_every_language(self):
        for l in ("en", "fr", "rw", "sw"):
            p = R.pick(l, photo=None)
            self.assertEqual(p["kind"], "illustration")
            self.assertTrue(p["caption"])
        self.assertNotEqual(R.pick("en", photo=None)["caption"], R.pick("fr", photo=None)["caption"])

    def test_photo_caption_links_to_the_article_for_credit(self):
        p = R.pick("en", photo={"url": "https://upload.wikimedia.org/a.jpg", "page": "https://en.wikipedia.org/wiki/X", "title": "X"})
        self.assertEqual((p["kind"], p["src"]), ("photo", "https://upload.wikimedia.org/a.jpg"))
        self.assertIn("Wikimedia Commons", p["caption"])
        self.assertEqual(p["page"], "https://en.wikipedia.org/wiki/X")

    def _fresh(self):
        R._cache.update({"photo": None, "at": 0.0})

    def test_offline_lookup_fails_quietly_and_retries_later(self):
        self._fresh()
        with mock.patch.object(R, "_get_json", side_effect=OSError("offline")):
            self.assertIsNone(R.find_photo())
            self.assertIsNone(R.find_photo())  # inside the retry window: no new request
        self._fresh()

    def test_only_commons_non_svg_verified_images_are_accepted(self):
        data = {"thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Room.jpg/640px-Room.jpg"},
                "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Security_operations_center"}}}
        self._fresh()
        with mock.patch.object(R, "_get_json", return_value=data), mock.patch.object(R, "_is_image", return_value=True):
            self.assertEqual(R.find_photo()["url"], data["thumbnail"]["source"])
        for bad in ("https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/Logo.png", "https://example.com/wikipedia/commons/x.jpg.svg",
                    "https://upload.wikimedia.org/wikipedia/commons/a/ab/Diagram.svg"):
            self._fresh()
            with mock.patch.object(R, "_get_json", return_value={"thumbnail": {"source": bad}}), mock.patch.object(R, "_is_image", return_value=True):
                self.assertIsNone(R.find_photo(), bad)
        self._fresh()
        with mock.patch.object(R, "_get_json", return_value=data), mock.patch.object(R, "_is_image", return_value=False):
            self.assertIsNone(R.find_photo())
        self._fresh()


if __name__ == "__main__":
    unittest.main()
