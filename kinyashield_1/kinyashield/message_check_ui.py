"""Streamlit part of the powerful message check (kept out of app.py)."""
from __future__ import annotations
import dataclasses, hashlib
import streamlit as st
import message_ai as M
from safety_rules import LANG_NAMES


def _e(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _ask_factory(lang):
    def ask(prompt):
        from assistant_engine import answer_question
        return answer_question(question=prompt, history=[], language_name=LANG_NAMES.get(lang, "English"), language_code=lang)
    return ask


def analyse(text, lang, result, use_ai):
    """Cached per message+language+AI flag so reruns of the page do not call the AI again."""
    key = "kinyashield_msg_" + hashlib.sha256(f"{lang}|{int(use_ai)}|{text}".encode("utf-8")).hexdigest()[:24]
    if key not in st.session_state:
        with st.spinner(M.LABELS[lang]["wait"]):
            st.session_state[key] = M.assess(text, lang, result, use_ai=use_ai, ask=_ask_factory(lang) if use_ai else None)
    return st.session_state[key]


def merged_result(result, a):
    """The rule Result with the final (rules + AI) verdict, so the existing banner shows it."""
    return dataclasses.replace(result, verdict=a["verdict"])


def render(a, lang):
    L = M.LABELS[lang]
    cls = {"ok": "low", "verify": "medium", "high": "high"}.get(a["verdict"], "medium")
    badge = L["ai"] if a["source"] == "rules+ai" else L["rules"]
    st.markdown(f'<div class="ks-card {cls}"><h4>🧠 {_e(L["title"])} · <small>{_e(badge)}</small></h4><p><b>{_e(a["kind"])}</b></p>'
                f'<p>{_e(a["summary"])}</p></div>', unsafe_allow_html=True)
    if a.get("ai_error"):
        st.caption(L["noai"])
    def block(title, items, ordered=False):
        if not items:
            return
        st.markdown(f"**{title}**")
        for i, x in enumerate(items, 1):
            st.markdown(f"{i}. {x}" if ordered else f"- {x}")
    block(L["why"], a["reasons"])
    block(L["do"], a["do"], ordered=True)
    block(L["verify"], a["verify"])
    block(L["dont"], a["dont"])
    if a.get("missing"):
        st.caption(a["missing"])
    st.caption(L["limits"])
