import os, sys, re, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_background as B

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Background(unittest.TestCase):
    def test_picture_is_bundled_and_light_enough_to_embed(self):
        p = os.path.join(HERE, "assets", "galaxy_background.jpg")
        self.assertTrue(os.path.isfile(p))
        self.assertLess(os.path.getsize(p), 400_000)

    def test_css_embeds_the_picture_and_keeps_text_dark_on_a_light_panel(self):
        c = B.css()
        self.assertTrue(c.startswith("<style>") and c.endswith("</style>"))
        self.assertIn("url(\"data:image/jpeg;base64,", c)
        self.assertIn(".stApp{", c)
        self.assertIn("cover !important", c)
        self.assertNotIn("rgba(255,255,255,.93)", c)     # the white layer is gone
        self.assertIn("background:transparent !important;border-radius:0", c)
        self.assertIn(B.LIGHT, c)                        # light text straight on the galaxy
        self.assertIn(B.INK, c)
        self.assertNotIn("__IMG__", c)
        self.assertNotIn("__INK__", c)
        self.assertNotIn("\n", c)

    def test_lock_signs_left_and_servers_right_sit_behind_the_content(self):
        c = B.css()
        self.assertEqual(c.count("data:image/svg+xml;base64,"), 4)   # each picture embedded once
        self.assertIn("right 1.5vw center", c)          # cybersecurity room on the right
        self.assertIn("(100vw - var(--ks-sb) - 460px)", c)   # panel narrowed so the side columns stay free (art is never under the panel)
        self.assertIn("left calc(var(--ks-sb) + 1.5vw) center", c)  # lock column on the left, moved right of the sidebar when it is open
        self.assertNotIn("__", c)
        import security_art as A
        self.assertEqual(A.locks_svg().count("<g transform=\"translate(0 "), 5)
        left = A.left_svg()                                # left: five locks + servers, tagline turned 90 degrees in front
        self.assertIn("LET THE SKY NOT BE THE LIMIT", left)
        self.assertIn("rotate(90)", left)
        self.assertEqual(left.count('scale(.62)'), 5)
        self.assertTrue(left.index("rotate(90)") > left.index('scale(.66)'))   # text is drawn after (in front of) locks and servers
        room = A.room_svg()
        self.assertIn("SECURITY OPERATIONS ROOM", room)
        self.assertGreaterEqual(room.count('stroke="#6fe3ff" stroke-width="1.6"'), 9)   # monitors on the wall and at the desks
        self.assertIn("LET THE SKY NOT BE THE LIMIT", A.locks_row_with_tagline_svg())
        for svg in (A.locks_svg(), A.locks_svg(True), A.servers_svg(), A.left_svg(), A.room_svg(), A.locks_row_with_tagline_svg()):
            self.assertTrue(svg.startswith("<svg") and svg.endswith("</svg>"))
            self.assertNotIn("http://www.w3.org/1999/xlink", svg)
            self.assertNotIn("<image", svg)
            self.assertNotIn("<script", svg)

    def test_art_failure_falls_back_to_plain_sky(self):
        import security_art as A
        old = B._art
        try:
            B._art = None
            c = B.css()
            self.assertIn("data:image/jpeg;base64,", c)
            self.assertNotIn("svg+xml", c)
            self.assertNotIn("__", c)
        finally:
            B._art = old

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

    def test_gold_ring_in_all_four_corners(self):
        h = B.rings_html()
        for corner in ("tl", "tr", "bl", "br"):
            self.assertIn(f'class="ks-ring {corner}"', h)
        c = B.css()
        self.assertIn("data:image/png;base64,", c)
        self.assertIn("position:fixed", c)
        self.assertIn("pointer-events:none", c)             # never blocks a click
        for rule in (".ks-ring.tl{", ".ks-ring.tr{", ".ks-ring.bl{", ".ks-ring.br{"):
            self.assertIn(rule, c)

    def test_galaxy_is_the_page_background(self):
        try:
            from PIL import Image
        except Exception:
            self.skipTest("Pillow not installed")
        im = Image.open(os.path.join(HERE, "assets", "galaxy_background.jpg"))
        self.assertGreater(im.height, im.width)             # the portrait galaxy photo
        self.assertLess(sum(im.convert("L").resize((1, 1)).getdata()), 90)   # dark enough for light text


if __name__ == "__main__":
    unittest.main()
