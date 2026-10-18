import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import physics_db
from physics_data import TOPICS, TERMS, FORMULAS
from assistant_flow import route, format_guide


class Physics(unittest.TestCase):
    def test_data_complete(self):
        self.assertGreaterEqual(len(FORMULAS), 110)
        ids = [f[0] for f in FORMULAS]
        self.assertEqual(len(ids), len(set(ids)))
        for fid, topic, names, formula, terms, extra in FORMULAS:
            self.assertIn(topic, TOPICS, fid)
            self.assertEqual(len(names), 4, fid)
            self.assertTrue(all(n.strip() for n in names) and formula.strip(), fid)
            for k in terms:
                self.assertIn(k, TERMS, (fid, k))
        for k, v in TERMS.items():
            self.assertEqual(len(v), 6, k)
            self.assertTrue(all(str(x).strip() for x in v), k)
        for k, v in TOPICS.items():
            self.assertEqual(len(v), 4, k)
        self.assertEqual(set(f[1] for f in FORMULAS), set(TOPICS))        # every topic has formulas

    def test_key_formulas_are_correct(self):
        by = {f[0]: f[3] for f in FORMULAS}
        expect = {"newton2": "F = ma", "ke": "KE = ½mv²", "pe": "PE = mgh", "ohm": "V = IR", "emc2": "E = mc²", "wavespeed": "v = fλ", "suvat1": "v = u + at",
                  "suvat2": "s = ut + ½at²", "suvat3": "v² = u² + 2as", "gravlaw": "F = G m₁m₂ / r²", "idealgas": "PV = nRT = NkT", "coulomb": "F = k q₁q₂ / r²",
                  "photon": "E = hf = hc / λ", "snell": "n₁ sinθ₁ = n₂ sinθ₂", "pendulum": "T = 2π√(L / g)", "hydrostatic": "P = ρgh", "heat": "Q = mcΔT", "carnot": "η = 1 − T_c / T_h"}
        for k, v in expect.items():
            self.assertEqual(by[k], v, k)

    def test_questions_in_all_languages(self):
        for q, l, pid in [("all physics formulas", "en", "physics_list"), ("kinetic energy formula", "en", "physics_ke"), ("Ohm's law", "en", "physics_ohm"),
                          ("snell's law", "en", "physics_snell"), ("mechanics formulas", "en", "physics_topic_mechanics"), ("formulas of electricity", "en", "physics_topic_electricity"),
                          ("formule de l'énergie cinétique", "fr", "physics_ke"), ("loi d'Ohm", "fr", "physics_ohm"), ("formule pression", "fr", "physics_pressure"),
                          ("formula ya fiziki zose", "rw", "physics_list"), ("fomula za fizikia", "sw", "physics_list"), ("physics constants", "en", "physics_constants"),
                          ("what is e=mc2", "en", "physics_emc2"), ("the formula for resistance in series", "en", "physics_series"), ("pendulum period", "en", "physics_pendulum")]:
            r = route(q, l)
            self.assertEqual(r["entry"]["id"], pid, q)

    def test_answer_has_symbols_and_units_in_each_language(self):
        e = route("Ohm's law", "en")["entry"]
        for l, word in [("en", "resistance"), ("fr", "résistance"), ("rw", "resistance"), ("sw", "upinzani")]:
            txt = format_guide(e, l, "s", "src")
            self.assertIn("V = IR", txt)
            self.assertIn(word, txt, l)
            self.assertIn("(Ω)", txt)

    def test_overview_lists_all_formulas(self):
        e = route("all physics formulas", "en")["entry"]
        self.assertEqual(len(e["steps"]["en"]), physics_db.COUNT)
        self.assertEqual(route("optics formulas", "en")["entry"]["id"], "physics_topic_optics")

    def test_other_questions_not_hijacked(self):
        for q, bad in [("how does a laptop work", "physics"), ("my password formula", "physics"), ("how do I write a CV", "physics"), ("methods of scams", "physics"),
                       ("give me 50 types of phones", "physics"), ("who owns you", "physics"), ("what is a formula", "physics"), ("maths formulas", "physics")]:
            self.assertFalse(str(route(q, "en").get("entry", {}).get("id", "")).startswith(bad), q)

    def test_scam_detector_still_first(self):
        msg = "URGENT: your MTN MoMo account is blocked. Send your PIN to 0788123456 now to unblock it, or you lose your money today."
        self.assertEqual(route(msg, "en")["kind"], "scam")


if __name__ == "__main__":
    unittest.main()
