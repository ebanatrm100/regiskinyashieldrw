import unittest, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from detector import analyze, highlight_spans
from safety_rules import RULES
import ui_html as ui

def v(t): return analyze(t).verdict

class Context(unittest.TestCase):
    def test_warning_about_pin_is_not_request(self):
        self.assertEqual(v("Never share your PIN with anyone."), "ok")
        self.assertEqual(v("We will never ask you to send your password."), "ok")
        self.assertEqual(v("Your OTP is 123456. Do not share it with anyone."), "ok")
        self.assertEqual(v("Ntugasangize iyi kode n'undi muntu."), "ok")
    def test_negation_cannot_hide_a_real_request(self):
        self.assertNotEqual(v("Do not delay, send your PIN now."), "ok")
        self.assertNotEqual(v("Do not delay and send your PIN."), "ok")
    def test_request_is_flagged(self):
        r = analyze("Please send your PIN to verify.")
        self.assertEqual(r.findings[0].rule_id, "credential_request")
        self.assertEqual(r.findings[0].evidence[0][2].lower(), "send your pin")
    def test_urgency_or_link_alone_is_not_flagged(self):
        self.assertEqual(v("Please come immediately, see https://example.org/map"), "ok")
    def test_mistake_needs_money(self):
        self.assertEqual(v("I sent you the file by mistake."), "ok")
        self.assertNotEqual(v("I sent you 5,000 RWF by mistake, send back the money."), "ok")
    def test_protective_text_is_reported(self):
        self.assertTrue(analyze("Never share your PIN.").protective)

class Verdicts(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(v("Hello, how are you?"), "ok")
        self.assertEqual(v("You have won a prize!"), "verify")
        self.assertEqual(v("Your account has been locked. Send your PIN immediately."), "high")
    def test_empty_and_odd_input(self):
        for t in ("", "   ", None, "😀" * 50, "a" * 20000):
            self.assertEqual(analyze(t).verdict, "ok")

class Display(unittest.TestCase):
    def test_html_is_escaped(self):
        r = analyze("<script>alert(1)</script> send your PIN")
        out = ui.highlighted_message_html(r) + ui.finding_cards_html(r)
        self.assertNotIn("<script>", out)
    def test_spans_do_not_overlap(self):
        r = analyze("Your account has been locked. Verify your account at http://203.0.113.9/x now. Send your PIN.")
        sp = highlight_spans(r)
        for a, b in zip(sp, sp[1:]):
            self.assertLessEqual(a[1], b[0])

class Rules(unittest.TestCase):
    def test_every_rule_complete_and_regex_valid(self):
        from safety_rules import LANGS
        ids = set()
        for r in RULES:
            self.assertNotIn(r["id"], ids); ids.add(r["id"])
            for k in ("title", "why", "advice"):
                for l in LANGS:
                    self.assertTrue(r[k][l].strip(), (r["id"], k, l))
            lists = [g.values() for g in r["groups"]] if "groups" in r else [r["patterns"].values()]
            for vals in lists:
                for pats in vals:
                    for p in pats:
                        re.compile(p)
                        self.assertTrue(p.isascii(), (r["id"], p))

class FourLanguages(unittest.TestCase):
    def test_protective_wording_in_every_language(self):
        for t in ("Never share your PIN with anyone.",
                  "Ne communiquez jamais votre mot de passe a personne.",
                  "Ntugasangize iyi kode n'undi muntu.",
                  "Usishiriki nenosiri lako na mtu yeyote."):
            self.assertEqual(v(t), "ok", t)
    def test_requests_in_every_language(self):
        for t in ("Please send your PIN to verify.",
                  "Veuillez envoyer votre code PIN pour vérifier.",
                  "Mpa kode wakiriye kuri telefoni yawe.",
                  "Tafadhali tuma PIN yako ili kuthibitisha."):
            self.assertNotEqual(v(t), "ok", t)
    def test_accents_and_case_do_not_matter(self):
        self.assertEqual(v("VÉRIFIEZ VOTRE COMPTE sur http://203.0.113.9/x"), v("verifiez votre compte sur http://203.0.113.9/x"))
        self.assertNotEqual(v("Envoyez votre code PIN"), "ok")
    def test_nonbreaking_space_amounts(self):
        self.assertNotEqual(v("Versez\u00a050\u00a0000\u00a0RWF de frais de visa avant de commencer. Offre d'emploi a Dubai."), "ok")
    def test_language_guess(self):
        self.assertEqual(analyze("Bonjour, votre compte sera suspendu, merci").language, "fr")
        self.assertEqual(analyze("Habari, akaunti yako itafungwa, asante tafadhali").language, "sw")

class Combinations(unittest.TestCase):
    def test_needs_both_cues(self):
        self.assertEqual(v("Brother, I am stuck in traffic, I will be late."), "ok")
        self.assertNotEqual(v("Mum it is me, I changed my number. I need money for an emergency."), "ok")
        self.assertEqual(v("Please send me the report. It is me again."), "ok")
    def test_job_fee(self):
        self.assertNotEqual(v("Job offer in Dubai. Deposit 50,000 RWF for visa processing before you start."), "ok")
        self.assertEqual(v("Your loan of 200,000 RWF has been approved and will be paid on Monday."), "ok")
    def test_whatsapp_recruiter(self):
        self.assertNotEqual(v("I saw your CV. Please contact our recruiter on WhatsApp."), "ok")
        self.assertEqual(v("Please send me your updated CV, I will forward it."), "ok")

if __name__ == "__main__":
    unittest.main()
