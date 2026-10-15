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
# Optional AI chat engine; the original detector remains unchanged.

st.set_page_config(page_title="KinyaShield RW", page_icon="\U0001F6E1", layout="centered")

lang = st.sidebar.radio("Language", LANGS, format_func=lambda x: LANG_NAMES[x])
t = ui.STR[lang]
st.markdown(ui.CSS, unsafe_allow_html=True)
st.markdown(ui.hero_html(lang), unsafe_allow_html=True)
if lang != "en":
    st.info(t["draft_note"])

_chat_labels = {"en": "AI Assistant", "rw": "Umufasha wa AI", "sw": "Msaidizi wa AI", "fr": "Assistant IA"}
_chat_label = _chat_labels.get(str(lang).lower(), "AI Assistant")
tab_check, tab_learn, tab_about, tab_chat = st.tabs([t["tab_check"], t["tab_learn"], t["tab_about"], _chat_label])
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

# KINYASHIELD_CHAT_UPGRADE_V1
# This additional tab leaves the original Check, Learn and About content intact.
with tab_chat:
    _chat_titles = {
        "en": "Ask KinyaShield AI",
        "rw": "Baza KinyaShield AI",
        "sw": "Uliza KinyaShield AI",
        "fr": "Demandez à KinyaShield AI",
    }
    _chat_descriptions = {
        "en": "Ask questions, request explanations, or ask follow-up questions. Answers are AI-generated and may be wrong.",
        "rw": "Baza ibibazo, saba ibisobanuro cyangwa ukomeze ikiganiro. Ibisubizo bitangwa na AI bishobora kuba birimo amakosa.",
        "sw": "Uliza maswali, omba maelezo au uliza maswali ya kufuatilia. Majibu ya AI yanaweza kuwa na makosa.",
        "fr": "Posez des questions, demandez des explications ou poursuivez la conversation. Les réponses de l'IA peuvent être erronées.",
    }
    _chat_privacy = {
        "en": "Privacy reminder: do not paste passwords, PINs, one-time codes, personal account details, or private information.",
        "rw": "Icyibutsa cy'umutekano: ntushyiremo ijambo ry'ibanga, PIN, kode ikoreshwa rimwe, amakuru ya konti cyangwa andi makuru bwite.",
        "sw": "Kumbusho la faragha: usiweke nywila, PIN, misimbo ya matumizi ya mara moja, taarifa za akaunti au taarifa za siri.",
        "fr": "Rappel de confidentialité : ne saisissez pas de mot de passe, PIN, code à usage unique ni donnée personnelle ou privée.",
    }
    _chat_placeholder = {
        "en": "Ask a question…",
        "rw": "Andika ikibazo…",
        "sw": "Andika swali…",
        "fr": "Écrivez votre question…",
    }
    _chat_lang = str(lang).lower()
    _chat_title = _chat_titles.get(_chat_lang, "Ask KinyaShield AI")
    st.subheader(_chat_title)
    st.write(_chat_descriptions.get(_chat_lang, _chat_descriptions["en"]))
    st.info(_chat_privacy.get(_chat_lang, _chat_privacy["en"]))
    st.warning(
        "AI assistant is for general help and education. It does not replace the "
        "existing Check tab, official advice, or independent verification. "
        "Never rely on a green/safe-sounding answer alone to trust a link or message."
    )

    # KINYASHIELD_PART2_V1 : offline safety guide (no API key needed)
    _g_labels = {
        "en": ("Safety guide (works offline)", "Ask a safety question, e.g. 'I shared my PIN'", "What to do", "Related questions",
               "I do not have a reliable answer in my guide, so I will not guess. Try rewording it, or use the AI chat below."),
        "fr": ("Guide de s\u00e9curit\u00e9 (hors ligne)", "Posez une question de s\u00e9curit\u00e9, ex. \u00ab j'ai donn\u00e9 mon PIN \u00bb", "Que faire", "Questions li\u00e9es",
               "Je n'ai pas de r\u00e9ponse fiable dans mon guide, donc je ne vais pas deviner. Reformulez ou utilisez le chat IA ci-dessous."),
        "rw": ("Igitabo cy'umutekano (gikora nta murandasi)", "Baza ikibazo cy'umutekano, urugero 'natanze PIN'", "Icyo gukora", "Ibibazo bifitanye isano",
               "Nta gisubizo cyizewe mfite mu gitabo cyanjye, ntabwo rero ndakeka. Ongera ubyandike, cyangwa ukoreshe ikiganiro cya AI hepfo."),
        "sw": ("Mwongozo wa usalama (bila mtandao)", "Uliza swali la usalama, mf. 'nimetoa PIN'", "Cha kufanya", "Maswali yanayohusiana",
               "Sina jibu la kuaminika kwenye mwongozo wangu, kwa hiyo sitakisia. Andika tofauti au tumia gumzo la AI hapa chini."),
    }
    _gl = _g_labels.get(str(lang).lower(), _g_labels["en"])
    try:
        from guide_search import best as _guide_best, BY_ID as _GUIDE_BY_ID
        _gl_key = str(lang).lower() if str(lang).lower() in ("en", "fr", "rw", "sw") else "en"
        with st.expander(_gl[0], expanded=False):
            _gq = st.text_input(_gl[1], key=f"guide_q_{_gl_key}")
            if _gq.strip():
                _ge = _guide_best(_gq, _gl_key)
                if _ge is None:
                    st.info(_gl[4])
                else:
                    st.markdown(f"**{_ge['title'][_gl_key]}**")
                    st.write(_ge["answer"][_gl_key])
                    st.markdown(f"*{_gl[2]}*")
                    for _s in _ge["steps"][_gl_key]:
                        st.markdown(f"1. {_s}")
                    _rel = [_GUIDE_BY_ID[r]["title"][_gl_key] for r in _ge["related"] if r in _GUIDE_BY_ID]
                    if _rel:
                        st.caption(_gl[3] + ": " + " | ".join(_rel))
    except Exception:
        # The guide is optional; the rest of the app keeps working without it.
        pass

    _history_key = f"kinyashield_chat_history_{_chat_lang}"
    if _history_key not in st.session_state:
        st.session_state[_history_key] = []

    _clear_labels = {"en": "Clear conversation", "rw": "Siba ikiganiro", "sw": "Futa mazungumzo", "fr": "Effacer la conversation"}
    if st.button(_clear_labels.get(_chat_lang, "Clear conversation"), key=f"clear_chat_{_chat_lang}"):
        st.session_state[_history_key] = []
        st.rerun()

    for _message in st.session_state[_history_key]:
        with st.chat_message(_message["role"]):
            st.markdown(_message["content"])

    _prompt = st.chat_input(
        _chat_placeholder.get(_chat_lang, "Ask a question…"),
        key=f"chat_input_{_chat_lang}",
    )
    if _prompt:
        # Save and display the user's message immediately; do not alter detector.py.
        st.session_state[_history_key].append({"role": "user", "content": _prompt})
        with st.chat_message("user"):
            st.markdown(_prompt)
        with st.chat_message("assistant"):
            try:
                from assistant_engine import answer_question, MissingAPIKeyError
                with st.spinner("KinyaShield AI is preparing an answer…"):
                    _answer = answer_question(
                        question=_prompt,
                        history=st.session_state[_history_key][:-1],
                        language_name=LANG_NAMES.get(lang, "English"),
                    )
            except Exception as _chat_error:
                if _chat_error.__class__.__name__ == "MissingAPIKeyError":
                    st.error(
                        "AI chat is not configured yet. Add a GEMINI_API_KEY secret in "
                        "GitHub Codespaces for development. For Streamlit Community Cloud, "
                        "also add GEMINI_API_KEY in the deployed app's Secrets settings. "
                        "Do not put the key in app.py or commit it to GitHub."
                    )
                else:
                    st.error(
                        "KinyaShield AI could not generate a response. Check that the API "
                        "key is valid, the selected model is available, the dependency "
                        "installed successfully, and your API quota/network are available. "
                        "Please try again later. Your original scam checker is unchanged."
                    )
            else:
                st.markdown(_answer)
                st.session_state[_history_key].append(
                    {"role": "assistant", "content": _answer}
                )

