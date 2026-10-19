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
# KINYASHIELD_SKY_BG_V1: sky-and-clouds picture as the page background; content sits on a light panel so it stays readable
try:
    import app_background as _bg

    _bg_css = _bg.css()
    if _bg_css:
        st.markdown(_bg_css, unsafe_allow_html=True)
except Exception:
    pass
if lang != "en":
    st.info(t["draft_note"])

_chat_labels = {"en": "AI Assistant", "rw": "Umufasha wa AI", "sw": "Msaidizi wa AI", "fr": "Assistant IA"}
_chat_label = _chat_labels.get(str(lang).lower(), "AI Assistant")
try:
    import org_ui as _org
    _org_label = _org.TAB.get(str(lang).lower(), _org.TAB["en"])
except Exception:  # the business tab is optional; the other tabs never depend on it
    _org = None
    _org_label = None
_tab_names = [t["tab_check"], t["tab_learn"], t["tab_about"], _chat_label] + ([_org_label] if _org else [])
_tabs = st.tabs(_tab_names)
tab_check, tab_learn, tab_about, tab_chat = _tabs[:4]
tab_org = _tabs[4] if _org else None
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

    # KINYASHIELD_INTERACTIVE_V1 : interactive assistant (scam detector -> offline guide -> AI)
    _L = {
        "en": dict(sugg="Try asking", rel="Related questions", steps="What to do", src="From the KinyaShield guide",
                   force="Always ask the AI (skip the offline guide)", thinking="KinyaShield AI is preparing an answer…",
                   scam_head="This looks like a message you received. Result from the KinyaShield checker:", reasons="Why", next="What to do next",
                   more="Open the Check tab for highlighted wording and full details.", noai="I have no reliable offline answer to that, and the AI chat is not set up yet (add GEMINI_API_KEY in Secrets). Try rewording, or pick a suggested question.",
                   err="KinyaShield AI could not answer right now. The offline guide and the Check tab still work."),
        "fr": dict(sugg="Essayez de demander", rel="Questions liées", steps="Que faire", src="Du guide KinyaShield",
                   force="Toujours demander à l'IA (ignorer le guide hors ligne)", thinking="KinyaShield IA prépare une réponse…",
                   scam_head="Cela ressemble à un message reçu. Résultat du vérificateur KinyaShield :", reasons="Pourquoi", next="Que faire ensuite",
                   more="Ouvrez l'onglet Vérifier pour les mots surlignés et tous les détails.", noai="Je n'ai pas de réponse fiable hors ligne et le chat IA n'est pas encore configuré (ajoutez GEMINI_API_KEY dans Secrets). Reformulez ou choisissez une question proposée.",
                   err="KinyaShield IA n'a pas pu répondre maintenant. Le guide hors ligne et l'onglet Vérifier fonctionnent toujours."),
        "rw": dict(sugg="Gerageza kubaza", rel="Ibibazo bifitanye isano", steps="Icyo gukora", src="Mu gitabo cya KinyaShield",
                   force="Burigihe baza AI (reka igitabo kidakoresha murandasi)", thinking="KinyaShield AI iratekereza igisubizo…",
                   scam_head="Ibi bisa n'ubutumwa wakiriye. Igisubizo cy'ugenzura rya KinyaShield:", reasons="Impamvu", next="Icyo gukora gikurikira",
                   more="Fungura igice cya «Genzura» urebe amagambo yagaragajwe n'ibisobanuro byose.", noai="Nta gisubizo cyizewe mfite hano, kandi ikiganiro cya AI ntikirashyirwaho (shyiramo GEMINI_API_KEY muri Secrets). Ongera ubyandike cyangwa uhitemo ikibazo cyatanzwe.",
                   err="KinyaShield AI ntiyashoboye gusubiza ubu. Igitabo n'igice cya «Genzura» biracyakora."),
        "sw": dict(sugg="Jaribu kuuliza", rel="Maswali yanayohusiana", steps="Cha kufanya", src="Kutoka mwongozo wa KinyaShield",
                   force="Muulize AI kila mara (ruka mwongozo wa nje ya mtandao)", thinking="KinyaShield AI inaandaa jibu…",
                   scam_head="Hii inaonekana kama ujumbe uliopokea. Matokeo ya kikagua cha KinyaShield:", reasons="Kwa nini", next="Cha kufanya baadaye",
                   more="Fungua kichupo cha «Hakiki» kuona maneno yaliyoangaziwa na maelezo kamili.", noai="Sina jibu la kuaminika nje ya mtandao, na gumzo la AI bado halijawekwa (ongeza GEMINI_API_KEY kwenye Secrets). Andika tofauti au chagua swali lililopendekezwa.",
                   err="KinyaShield AI haikuweza kujibu sasa. Mwongozo na kichupo cha «Hakiki» bado vinafanya kazi."),
    }
    _lk = _chat_lang if _chat_lang in _L else "en"
    _T = _L[_lk]
    try:
        from assistant_flow import route as _route, suggested as _suggested, related as _related, format_guide as _format_guide
        _flow_ok = True
    except Exception:
        _flow_ok = False  # the plain AI chat below still works

    _history_key = f"kinyashield_chat_history_{_chat_lang}"
    _rel_key = f"kinyashield_related_{_chat_lang}"
    if _history_key not in st.session_state:
        st.session_state[_history_key] = []
    if _rel_key not in st.session_state:
        st.session_state[_rel_key] = []

    _clear_labels = {"en": "Clear conversation", "rw": "Siba ikiganiro", "sw": "Futa mazungumzo", "fr": "Effacer la conversation"}
    if st.button(_clear_labels.get(_chat_lang, "Clear conversation"), key=f"clear_chat_{_chat_lang}"):
        st.session_state[_history_key] = []
        st.session_state[_rel_key] = []
        st.rerun()

    _force_ai = st.checkbox(_T["force"], key=f"force_ai_{_chat_lang}", value=False)
    _search_labels = {"en": "Search the web for current information and show sources (needs the AI key)",
                      "fr": "Rechercher sur le web des informations récentes et montrer les sources (clé IA requise)",
                      "rw": "Shakisha kuri interineti amakuru agezweho werekane amasoko (bisaba urufunguzo rwa AI)",
                      "sw": "Tafuta wavuti kwa taarifa za sasa na uonyeshe vyanzo (inahitaji ufunguo wa AI)"}
    _use_search = st.checkbox(_search_labels.get(_chat_lang, _search_labels["en"]), key=f"use_search_{_chat_lang}", value=False)
    try:  # tutor quiz + document assistant (each works on its own; the chat below does not depend on them)
        import study_ui as _study
        from assistant_engine import answer_question as _answer_doc
        _study.render_quiz(st, _chat_lang)
        _study.render_docs(st, _chat_lang, lambda _qq, _dd: _answer_doc(question=_qq, history=[], language_name=LANG_NAMES.get(lang, "English"), document=_dd))
    except Exception:
        st.caption("…")

    for _message in st.session_state[_history_key]:
        with st.chat_message(_message["role"]):
            st.markdown(_message["content"])
            if _message.get("image"):  # photo for a computer answer (Wikimedia Commons); text above is complete without it
                try:
                    st.image(_message["image"]["url"], caption=_message["image"]["caption"], width=480)
                    st.markdown(f"[Wikipedia / Wikimedia Commons]({_message['image']['page']})")
                except Exception:
                    st.caption(_message["image"].get("fallback", ""))
            elif _message.get("image_note"):
                st.caption(_message["image_note"])
            if _message.get("gallery"):  # photos for a phone-brands list (Wikimedia Commons); the text list above is complete without them
                try:
                    _g = _message["gallery"]
                    for _row in range(0, len(_g), 4):
                        _cols = st.columns(4)
                        for _col, _it in zip(_cols, _g[_row:_row + 4]):
                            with _col:
                                st.image(_it["url"], caption=_it["name"], use_container_width=True)
                                st.markdown(f"[Commons]({_it['page']})")
                    if _message.get("gallery_note"):
                        st.caption(_message["gallery_note"])
                except Exception:
                    pass

    _clicked = None
    if _flow_ok:
        _chips = [(f"sg_{i}", t_) for i, t_ in _suggested(_chat_lang)] if not st.session_state[_history_key] else \
                 [(f"rl_{i}", t_) for i, t_ in st.session_state[_rel_key]]
        if _chips:
            st.caption(_T["sugg"] if not st.session_state[_history_key] else _T["rel"])
            for _n, (_cid, _ctitle) in enumerate(_chips):
                if st.button(_ctitle, key=f"chip_{_chat_lang}_{_cid}_{len(st.session_state[_history_key])}"):
                    _clicked = _ctitle

    _prompt = st.chat_input(
        _chat_placeholder.get(_chat_lang, "Ask a question…"),
        key=f"chat_input_{_chat_lang}",
    )
    _q = _clicked or _prompt
    if _q:
        _hist = st.session_state[_history_key]
        _hist.append({"role": "user", "content": _q})
        _routed = _route(_q, _chat_lang, force_ai=_force_ai) if _flow_ok else {"kind": "ai"}
        st.session_state[_rel_key] = []
        if _routed["kind"] == "scam":
            _r = _routed["result"]
            _lines = [f"**{_T['scam_head']}** {_r.label}", ""]
            _main = [f_ for f_ in _r.findings if f_.severity != "low"]
            if _main:
                _lines.append(f"*{_T['reasons']}*")
                _lines += [f"- {f_.title.get(_lk, f_.title['en'])}" for f_ in _main]
                _lines.append("")
            _lines.append(f"*{_T['next']}*")
            _lines += [f"{n}. {s_}" for n, s_ in enumerate(_routed["steps"], 1)]
            _lines += ["", f"_{_T['more']}_"]
            _hist.append({"role": "assistant", "content": "\n".join(_lines), "kind": "note"})
            st.rerun()
        elif _routed["kind"] == "guide":
            _e = _routed["entry"]
            _msg_out = {"role": "assistant", "content": _format_guide(_e, _chat_lang, _T["steps"], _T["src"]), "kind": "note"}
            if _e.get("gallery"):
                try:
                    import phones_db as _pdb
                    with st.spinner("…"):
                        _g = _pdb.resolve_many(_e["gallery"], _chat_lang)
                    if _g:
                        _msg_out["gallery"] = _g
                        if len(_g) < len(_e["gallery"]):
                            _msg_out["gallery_note"] = _pdb.gallery_note(_chat_lang)
                    else:
                        _msg_out["image_note"] = _pdb.missing_photo_note(_chat_lang)
                except Exception:
                    pass
            elif _e.get("kind") == "phone" and _e.get("image_query"):
                try:
                    import phones_db as _pdb
                    with st.spinner("…"):
                        _img = _pdb.resolve_image(_e, _chat_lang)
                    if _img:
                        _img["fallback"] = _pdb.missing_photo_note(_chat_lang)
                        _msg_out["image"] = _img
                    else:
                        _msg_out["image_note"] = _pdb.missing_photo_note(_chat_lang)
                except Exception:
                    pass
            elif _e.get("image_query"):
                try:
                    import computers_db as _cdb
                    with st.spinner("…"):
                        _img = _cdb.resolve_image(_e, _chat_lang)
                    if _img:
                        _img["fallback"] = _cdb.missing_photo_note(_chat_lang)
                        _msg_out["image"] = _img
                    else:
                        _msg_out["image_note"] = _cdb.missing_photo_note(_chat_lang)
                except Exception:
                    pass
            _hist.append(_msg_out)
            st.session_state[_rel_key] = _related(_e, _chat_lang)
            st.rerun()
        else:
            with st.chat_message("user"):
                st.markdown(_q)
            with st.chat_message("assistant"):
                _msg, _kind = None, None
                try:
                    from assistant_engine import answer_question
                    with st.spinner(_T["thinking"]):
                        _msg = answer_question(
                            question=_q,
                            history=[m_ for m_ in _hist[:-1] if m_.get("kind") != "note"],
                            language_name=LANG_NAMES.get(lang, "English"),
                            use_search=_use_search,
                        )
                except Exception as _chat_error:
                    _msg = _T["noai"] if _chat_error.__class__.__name__ == "MissingAPIKeyError" else _T["err"]
                    _kind = "note"
                _hist.append({"role": "assistant", "content": _msg, **({"kind": _kind} if _kind else {})})
            st.rerun()


if tab_org is not None:
    with tab_org:
        try:
            _org.render(st, str(lang).lower())
        except Exception:
            st.warning("Business & Schools tab could not load. The other tabs still work.")
