"""Runs the Cyber News tab against a strict fake Streamlit (writing a widget's own session key raises, as in real Streamlit) in every language and state."""
import sys, os, traceback
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from unittest.mock import MagicMock
import log_analyzer_ui as ui
from datetime import date

clicks_g=()
def make(go=False, text="", chosen=None, clicks=()):
    global clicks_g; clicks_g=clicks
    st = MagicMock()
    class SS(dict):
        wk=set()
        def __setitem__(self,k,v):
            if k in self.wk: raise RuntimeError(f'st.session_state.{k} cannot be modified after the widget with key {k} is instantiated')
            super().__setitem__(k,v)
    st.session_state = SS()
    def columns(n, *a, **k):
        n = n if isinstance(n, int) else len(n)
        cs=[MagicMock() for _ in range(n)]
        for c in cs: c.date_input.return_value = date(2026,10,1); c.button.side_effect = lambda label, key=None, **k: key in clicks_g
        return cs
    st.columns.side_effect = columns
    st.text_input.side_effect = lambda *a, **k: (st.session_state.wk.add(k.get('key')), text)[1]
    st.multiselect.side_effect = lambda *a, **k: (st.session_state.wk.add(k.get('key')), chosen or ['security','awareness','crime'])[1]
    st.form_submit_button.return_value = go
    st.button.side_effect = lambda label, key=None, **k: key in clicks
    st.form.return_value.__enter__ = lambda s: s
    st.form.return_value.__exit__ = lambda *a: False
    st.expander.return_value.__enter__ = lambda s: s
    st.expander.return_value.__exit__ = lambda *a: False
    st.spinner.return_value.__enter__ = lambda s: s
    st.spinner.return_value.__exit__ = lambda *a: False
    st.date_input.return_value = date(2026,10,1)
    return st

bad = 0
for lang in ("en", "fr", "rw", "sw"):
    for clicks, go, text in (((), False, ""), ((f"logan_demo_{lang}",), False, ""), ((f"logan_demo_{lang}", f"logan_ai_{lang}"), False, ""), ((), True, "Oct 31 10:00:00 h sshd[1]: Failed password for root from 8.8.8.8 port 22 ssh2\n" * 8)):
        st = make(go, text, clicks=clicks)
        st.text_area.return_value = text
        st.file_uploader.return_value = None
        st.metric = MagicMock()
        try:
            ui.render(st, lang)
            for _ in range(2):
                st2 = make(False, clicks=clicks); st2.session_state = st.session_state; st2.text_area.return_value = ""; st2.file_uploader.return_value = None
                ui.render(st2, lang)
        except Exception:
            bad += 1
            traceback.print_exc(limit=5)
assert bad == 0
print("OK log analyzer ui")
