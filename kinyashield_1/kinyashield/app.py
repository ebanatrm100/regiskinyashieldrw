"""KinyaShield RW: Streamlit interface (developer / hosted-on-Streamlit-Cloud version).
Run: streamlit run app.py
The browser version that needs no server is web/index.html (see docs/DEPLOY.md)."""
import csv
import pathlib

import streamlit as st

import ui_html as ui
from detector import analyze
from safety_rules import LANG_NAMES, LANGS
from trusted_sources import NOTE, SOURCES

st.set_page_config(page_title="KinyaShield RW", page_icon="\U0001F6E1", layout="centered")

lang = st.sidebar.radio("Language", LANGS, format_func=lambda x: LANG_NAMES[x])
t = ui.STR[lang]
st.markdown(ui.CSS, unsafe_allow_html=True)
st.markdown(ui.hero_html(lang), unsafe_allow_html=True)
if lang != "en":
    st.info(t["draft_note"])

tab_check, tab_learn, tab_about = st.tabs([t["tab_check"], t["tab_learn"], t["tab_about"]])

with tab_check:
    examples = {}
    p = pathlib.Path(__file__).parent / "data" / "dev_messages.csv"
    if p.exists():
        with open(p, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["language"] == lang:
                    examples[r["text"][:60] + "…"] = r["text"]
    choice = st.selectbox(t["examples"], ["—"] + list(examples))
    text = st.text_area(t["paste"], value=examples.get(choice, ""), height=150,
                        placeholder=t["placeholder"], key=f"msg_{lang}_{choice}")
    go = st.button(t["analyze"], type="primary", use_container_width=True)
    st.caption(t["privacy"])
    if go and text.strip():
        res = analyze(text)
        st.markdown(ui.verdict_html(res, lang), unsafe_allow_html=True)
        st.caption(f"{t['detected']}: {LANG_NAMES[res.language]}")
        a, b, c = st.tabs([t["evidence"], t["findings"], t["steps"]])
        with a:
            st.markdown(ui.highlighted_message_html(res), unsafe_allow_html=True)
            pr = ui.protective_html(res)
            if pr:
                st.markdown(f"**{t['protective']}**")
                st.markdown(pr, unsafe_allow_html=True)
        with b:
            cards = ui.finding_cards_html(res, lang)
            st.markdown(cards or f'<div class="ks-card low"><p>{t["none_found"]}</p></div>', unsafe_allow_html=True)
            low = ui.low_cards_html(res, lang)
            if low:
                st.markdown(f"**{t['low']}**")
                st.markdown(low, unsafe_allow_html=True)
        with c:
            st.markdown(ui.steps_html(res, lang), unsafe_allow_html=True)
    elif go:
        st.info(t["paste_first"])

with tab_learn:
    st.subheader(t["learn_title"])
    for tip in t["tips"]:
        st.markdown(f"- {tip}")

with tab_about:
    st.subheader(t["about_title"])
    for line in t["about"]:
        st.markdown(f"- {line}")
    st.subheader(t["sources_title"])
    for s in SOURCES:
        st.markdown(f"- **{s['name']}**: {s['use'].get(lang, s['use']['en'])}" + (f" ({s['url']})" if s["url"] else ""))
    st.caption(t["sources_note"])
