import os, sys, unittest, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import greetings_db as G
from assistant_flow import route, format_guide


def answer(q, lang="en"):
    r = route(q, lang)
    return (r["kind"], r.get("entry", {}).get("id", ""), format_guide(r["entry"], lang, "Steps", "Source") if r["kind"] == "guide" else "")


class Greetings(unittest.TestCase):
    def test_tables_are_complete(self):
        self.assertGreaterEqual(G.count(), 170)
        for kind, eq in G.EQ.items():
            self.assertEqual(len(eq), 4, kind)
            self.assertTrue(all(x.strip() for x in eq), kind)
            self.assertIn(kind, G.KIND, kind)
            self.assertEqual(len(G.KIND[kind]), 8, kind)
            self.assertTrue(all(x.strip() for x in G.KIND[kind]), kind)
        for o, names in G.ORIGIN.items():
            self.assertEqual(len(names), 4, o)
        for r in G.ROWS_PARSED:
            self.assertTrue(r["reply"].strip())

    def test_each_alias_belongs_to_one_greeting(self):
        seen = collections.defaultdict(set)
        for i, r in enumerate(G.ROWS_PARSED):
            for a in r["aliases"]:
                k = G._key(G.fold(a).split(), frozenset())
                if k:
                    seen[k].add(i)
        clashes = {" ".join(k): sorted((G.ROWS_PARSED[j]["kind"], G.ROWS_PARSED[j]["origin"]) for j in v) for k, v in seen.items() if len(v) > 1}
        self.assertEqual(clashes, {})

    def test_correct_reply_in_the_greeting_language(self):
        cases = [("Hello", "Hello!"), ("good morning", "Good morning!"), ("Mwaramutse", "Mwaramutse!"), ("Mwiriwe", "Mwiriwe!"), ("Muraho", "Muraho!"),
                 ("Bonjour", "Bonjour !"), ("Bonsoir", "Bonsoir !"), ("Jambo", "Jambo") if False else ("Hujambo", "Sijambo!"), ("shikamoo", "Marahaba!"),
                 ("thank you", "You're welcome!"), ("Murakoze", "Ntacyo!"), ("Merci", "De rien !"), ("Asante", "Karibu!"), ("goodbye", "Goodbye!"),
                 ("Murabeho", "Murabeho!"), ("Kwaheri", "Kwaheri!"), ("au revoir", "Au revoir !"), ("good night", "Good night!"), ("Ijoro ryiza", "Ijoro ryiza!"),
                 ("assalamu alaikum", "Wa alaykum as-salam"), ("Eid Mubarak", "Eid Mubarak to you too!"), ("happy birthday", "Thank you!"),
                 ("Isabukuru nziza", "Murakoze!"), ("Hola", "¡Hola!"), ("Namaste", "Namaste!"), ("how are you", "I'm doing well"), ("Amakuru?", "Ni meza, murakoze!"),
                 ("ça va ?", "Ça va très bien"), ("Habari yako", "Nzuri"), ("Karibu", "Asante!"), ("Murakaza neza", "Murakoze!")]
        for q, want in cases:
            kind, _id, text = answer(q)
            self.assertEqual(kind, "guide", q)
            self.assertIn(want, text, q)
            self.assertTrue(_id.startswith("greeting_"), q)

    def test_explained_in_all_four_languages_whatever_the_page_language(self):
        for lang in ("en", "fr", "rw", "sw"):
            _k, _i, text = answer("Mwaramutse", lang)
            for label in ("English", "Français", "Kinyarwanda", "Kiswahili"):
                self.assertIn(f"**{label}:**", text, (lang, label))
            for meaning in ("Good morning", "Bonjour (le matin)", "Habari za asubuhi"):
                self.assertIn(meaning, text, (lang, meaning))

    def test_filler_words_are_ignored(self):
        for q in ["good morning my friend", "Hello there!", "thank you very much", "Mwaramutse neza", "hi everyone", "Bonjour tout le monde", "thanks a lot"]:
            self.assertTrue(answer(q)[1].startswith("greeting_"), q)

    def test_asking_what_a_greeting_means_explains_without_replying(self):
        for q in ["what does Mwaramutse mean?", "meaning of bonjour", "Muraho bisobanura iki", "maana ya karibu", "what is hello"]:
            kind, gid, text = answer(q)
            self.assertTrue(gid.startswith("greeting_"), q)
            self.assertNotIn("How can I help you?", text, q)
            self.assertNotIn("Nabafasha iki?", text, q)
            self.assertIn("**Kiswahili:**", text)

    def test_two_greetings_in_one_message_get_two_replies(self):
        _k, _i, text = answer("hello, how are you?")
        self.assertIn("Hello!", text)
        self.assertIn("I'm doing well", text)

    def test_overview_of_greeting_types(self):
        for q in ["types of greetings", "all greetings", "liste des salutations"]:
            self.assertEqual(answer(q)[1], "greetings_overview", q)
        self.assertIn("Mwaramutse", answer("types of greetings")[2])

    def test_real_questions_are_not_treated_as_greetings(self):
        for q in ["hello, what is DNS?", "good morning routine for productivity", "how do I write a thank you email", "thank you for the explanation of phishing and what to do next",
                  "what is the capital of Peru", "what is English", "what does the name Aline mean", "how does a laptop work", "tell me about good night sleep"]:
            self.assertFalse(answer(q)[1].startswith("greeting_"), q)

    def test_other_routes_still_work(self):
        self.assertEqual(answer("what is English")[1], "def_english")
        self.assertEqual(answer("what does the name Aline mean")[1], "name_meaning")
        self.assertEqual(answer("how to greet people")[1], "greetings")

    def test_scam_detection_still_wins_over_a_friendly_opening(self):
        msg = "Hello dear! Your MTN MoMo account is blocked. Send your PIN and OTP to 0788123456 now to get your prize of 500000 RWF or lose it."
        self.assertEqual(route(msg, "en")["kind"], "scam")

    def test_force_ai_skips_greetings(self):
        self.assertEqual(route("hello", "en", force_ai=True)["kind"], "ai")


if __name__ == "__main__":
    unittest.main()
