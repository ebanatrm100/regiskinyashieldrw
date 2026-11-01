"""Runs the Cyber News tab against a strict fake Streamlit (writing a widget's own session key raises, as in real Streamlit) in every language and state."""
import sys, os, traceback
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from unittest.mock import MagicMock
import cyber_intel_ui as ui, cyber_intel as ci, cyber_upcoming as cu
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
for lang in ("en","fr","rw","sw"):
    for go, text in ((False,""),(True,"ransomware"),(True,"cybercrime last week"),(True,"upcoming next month"),(True,"phishing last week and upcoming")):
        st = make(go, text)
        try:
            ui.render(st, lang)
            # second pass with state kept
            st2 = make(False); st2.session_state = st.session_state
            ui.render(st2, lang)
        except Exception:
            bad += 1
            print("FAIL", lang, repr(text)); traceback.print_exc(limit=4); break
assert bad == 0

# deeper: click through every button state and render with real result data (offline fake fetch)
import cyber_intel as ci
from datetime import date
feed=b"""<rss><channel><item><title>Police arrest ransomware gang suspects</title><link>https://www.bleepingcomputer.com/a</link><pubDate>Fri, 30 Oct 2026 10:00:00 GMT</pubDate><description>d</description></item></channel></rss>"""
orig = ci.build_jobs
ci.build_jobs = lambda period, topics, lang, extra: [("BleepingComputer","research",("crime","security"),lambda: ("feed",feed))]
import cyber_upcoming as cu
cu.ci._http = lambda url, accept="": b'{"vulnerabilities":[]}'
bad2=0
for lang in ("en","fr","rw","sw"):
    for text, clicks in (("cybercrime last week", ()), ("cybercrime last week", (f"intel_refresh_{lang}",f"intel_ai_{lang}",f"intel_tr_{lang}")), ("upcoming next month", ()), ("ransomware", (f"intel_pick_this_week_{lang}",)),
                         ("ransomware", (f"intel_pickf_next_week_{lang}",)), ("ransomware", (f"intel_pick_custom_{lang}",f"intel_custom_go_{lang}")), ("x", (f"intel_change_{lang}",))):
        st = make(True, text, clicks=clicks)
        try:
            ui.render(st, lang)
            for _ in range(3):
                st2 = make(False, clicks=clicks); st2.session_state = st.session_state; ui.render(st2, lang)
        except Exception:
            bad2+=1; print("FAIL2", lang, text, clicks); traceback.print_exc(limit=5)
assert bad2 == 0
print("OK cyber intel ui")
