import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study_ui, quiz_data as QD, docs_assistant as DA


class _Ctx:
    def __enter__(self): return self
    def __exit__(self, *a): return False


class _Up:
    def __init__(self, name, data): self.name, self._d = name, data
    def getvalue(self): return self._d


class FakeSt:
    """Minimal stand-in for streamlit: records output, answers widgets from `script`."""
    def __init__(self, script=None):
        self.session_state, self.out, self.script, self.pressed = {}, [], script or {}, set()
    def expander(self, *a, **k): return _Ctx()
    def spinner(self, *a, **k): return _Ctx()
    def columns(self, n): return [_Ctx() for _ in range(n)]
    def selectbox(self, label, options, format_func=str, key=None, **k):
        [format_func(o) for o in options]
        return self.script.get(key, options[0])
    def slider(self, label, lo, hi, value, key=None, **k): return self.script.get(key, value)
    def radio(self, label, options, index=0, key=None, **k): return self.script.get(key) if key in self.script else (options[index] if index is not None else None)
    def button(self, label, key=None, **k): return key in self.pressed
    def checkbox(self, label, key=None, **k): return self.script.get(key, False)
    def text_input(self, label, key=None, **k): return self.script.get(key, "")
    def file_uploader(self, label, type=None, key=None, **k): return self.script.get("upload")
    def rerun(self): pass
    def _w(self, kind): return lambda t, *a, **k: self.out.append((kind, str(t)))
    def __getattr__(self, name):
        if name in ("markdown", "caption", "success", "error", "warning", "info", "write"): return self._w(name)
        raise AttributeError(name)


class Quiz(unittest.TestCase):
    def test_all_questions_valid_in_all_languages(self):
        for q in QD.QUESTIONS:
            for l in QD.LANGS:
                opts = QD.options(q, l)
                self.assertTrue(0 <= q["ans"] < len(opts) and len(set(opts)) == len(opts), q["q"]["en"])
                for f in ("q", "why", "slip"):
                    self.assertTrue(q[f][l].strip(), (f, l, q["q"]["en"]))
            self.assertEqual(len({len(QD.options(q, l)) for l in QD.LANGS}), 1)

    def test_render_and_check(self):
        for lang in QD.LANGS:
            st = FakeSt()
            study_ui.render_quiz(st, lang)                       # first view: no result
            self.assertFalse(any("/" in t and "score" in t.lower() for _, t in st.out))
            st.pressed = {f"quiz_check_{lang}"}
            study_ui.render_quiz(st, lang)                       # press check with nothing answered
            st.pressed = set()
            study_ui.render_quiz(st, lang)
            kinds = [k for k, _ in st.out]
            self.assertIn("warning", kinds)
            self.assertTrue(any("/ 5" in t for k, t in st.out if k == "markdown"))

    def test_changing_topic_clears_result(self):
        st = FakeSt()
        st.pressed = {"quiz_check_en"}
        study_ui.render_quiz(st, "en"); st.pressed = set(); study_ui.render_quiz(st, "en")
        self.assertTrue(st.session_state["quiz_checked_en"])
        st.script["quiz_topic_en"] = "physics"
        study_ui.render_quiz(st, "en")
        self.assertFalse(st.session_state["quiz_checked_en"])


class Docs(unittest.TestCase):
    TXT = ("The cooperative sold 45 tonnes of tomatoes for RWF 18,500,000 in 2025. Losses fell from 22% to 15%. "
           "Members must pay the annual fee of RWF 12,000 before 31 March 2026. Contact secretary@coop.example. "
           "The main cause of losses was delay in transport to the market.").encode()

    def test_extract_txt_docx_and_errors(self):
        self.assertTrue(DA.extract_pages("a.txt", self.TXT)[0].startswith("The cooperative"))
        import io, zipfile
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("word/document.xml", "<w:document><w:p><w:r><w:t>Hello &amp; welcome to the report.</w:t></w:r></w:p></w:document>")
        self.assertIn("Hello & welcome", DA.extract_pages("a.docx", b.getvalue())[0])
        for name, data, code in [("a.exe", b"x", "type"), ("a.txt", b"   ", "empty"), ("a.txt", b"x" * (DA.MAX_BYTES + 1), "big"), ("a.docx", b"notazip", "bad")]:
            with self.assertRaises(DA.DocError) as c:
                DA.extract_pages(name, data)
            self.assertEqual(str(c.exception), code)

    def test_details_and_answers_quote_the_document(self):
        pg = DA.extract_pages("a.txt", self.TXT)
        d = DA.key_details(pg)
        self.assertIn("31 March 2026", d["dates"]); self.assertIn("22%", d["percent"]); self.assertIn("secretary@coop.example", d["emails"])
        self.assertTrue(any("RWF 12,000" in m for m in d["money"]))
        self.assertIn("annual fee", DA.render_answer("how much is the annual fee", pg, "en"))
        for l in DA.LANGS:                                        # unrelated question: honest "not found", never an invented answer
            self.assertEqual(DA.render_answer("who is the president of france", pg, l), DA.HEAD["none"][l])
        for s in DA.summarize(pg, 3):                             # every summary sentence really occurs in the document
            self.assertIn(s[1].rstrip(".")[:30], self.TXT.decode())

    def test_render_docs_flow_without_ai(self):
        st = FakeSt({"upload": _Up("r.txt", self.TXT)})
        st.pressed = {"doc_sum_en"}
        study_ui.render_docs(st, "en", lambda q, d: "AI")
        self.assertTrue(any("Summary" in t for _, t in st.out))
        st.script["doc_q_en"] = "when must members pay the fee"; st.pressed = {"doc_go_en"}
        study_ui.render_docs(st, "en", lambda q, d: "AI")
        self.assertIn("31 March 2026", st.session_state["doc_out_en"])

    def test_render_docs_ai_paths(self):
        st = FakeSt({"upload": _Up("r.txt", self.TXT), "doc_ai_en": True})
        st.pressed = {"doc_det_en"}
        study_ui.render_docs(st, "en", lambda q, d: "AI says " + str("annual fee" in d))
        self.assertEqual(st.session_state["doc_out_en"], "AI says True")
        def boom(q, d): raise RuntimeError("x")
        study_ui.render_docs(st, "en", boom)
        self.assertEqual(st.session_state["doc_out_en"], study_ui.U["en"]["err"])


if __name__ == "__main__":
    unittest.main()
