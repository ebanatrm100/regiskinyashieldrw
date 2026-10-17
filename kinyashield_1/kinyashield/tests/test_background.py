import os, sys, re, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_background as B

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Background(unittest.TestCase):
    def test_picture_is_bundled_and_light_enough_to_embed(self):
        p = os.path.join(HERE, "assets", "sky_background.jpg")
        self.assertTrue(os.path.isfile(p))
        self.assertLess(os.path.getsize(p), 400_000)

    def test_css_embeds_the_picture_and_keeps_text_dark_on_a_light_panel(self):
        c = B.css()
        self.assertTrue(c.startswith("<style>") and c.endswith("</style>"))
        self.assertIn("url(\"data:image/jpeg;base64,", c)
        self.assertIn(".stApp{", c)
        self.assertIn("background-size:cover", c)
        self.assertIn("rgba(255,255,255,.93)", c)         # content panel
        self.assertIn(B.INK, c)
        self.assertNotIn("__IMG__", c)
        self.assertNotIn("__INK__", c)
        self.assertNotIn("\n", c)

    def test_missing_picture_means_no_css_and_no_crash(self):
        old = B._IMAGE
        try:
            B._IMAGE = old.with_name("does_not_exist.jpg")
            B.data_uri.cache_clear()
            self.assertEqual(B.css(), "")
        finally:
            B._IMAGE = old
            B.data_uri.cache_clear()

    def test_app_uses_the_background_and_no_longer_shows_the_old_pictures(self):
        src = open(os.path.join(HERE, "app.py"), encoding="utf-8").read()
        self.assertIn("app_background", src)
        self.assertNotIn("room_banner", src)
        self.assertNotIn("st.image(", src.split("with tab_check:")[0])
        for gone in ("regis_world_1.jpg", "regis_world_2.jpg", "cyber_room.svg", "cyber_room_computers.svg"):
            self.assertFalse(os.path.exists(os.path.join(HERE, "assets", gone)), gone)

    def test_title_is_removed_but_sky_details_remain(self):
        try:
            import numpy as np
            from PIL import Image
        except Exception:
            self.skipTest("numpy/Pillow not installed")
        im = np.asarray(Image.open(os.path.join(HERE, "assets", "sky_background.jpg")).convert("RGB")).astype(float)
        title = im[200:380, 300:1250]                      # where the big title used to be
        self.assertLess(title.std(axis=(0, 1)).max(), 14)  # plain sky now
        self.assertGreater(title[..., 2].mean(), 180)      # still blue sky
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        yellow = (r > 200) & (g > 150) & (b < 90)
        self.assertEqual(int(yellow[100:420, 150:1400].sum()), 0)      # crown and ring are gone
        tagline = im[414:434, 500:1020].max(axis=2)
        self.assertGreater((tagline > 235).sum(), 300)                 # the small tagline is still there
        plane = im[470:520, 1060:1125].max(axis=2)
        self.assertGreater((plane > 235).sum(), 100)                   # paper plane too


if __name__ == "__main__":
    unittest.main()
