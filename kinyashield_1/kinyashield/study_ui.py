"""Streamlit pieces for the AI Assistant tab: the practice quiz (Personal AI tutor) and the document assistant.
Kept out of app.py so the logic modules stay testable without Streamlit. Nothing here writes to disk."""
from __future__ import annotations
import hashlib
import quiz_data as QD
import docs_assistant as DA

U = {
    "en": dict(quiz="Study: practice quiz", topic="Topic", all="All topics", n="Questions", new="New questions", check="Check my answers", choose="Choose an answer",
               right="Correct.", wrong="Not quite.", answer="Right answer", why="Why", slip="Common mistake", score="Your score", retry="Try another set for more practice.",
               unanswered="Not answered.", docs="Document assistant: upload a file", up="Upload a PDF, Word (.docx) or text file", read="File read", chars="characters", pages="pages/sections",
               summ="Summarise", det="Find key details", ask="Ask a question about the document", go="Find the answer", ai="Use AI on this document (sends its text to Gemini)",
               clear="Remove document", noai="The AI is not set up yet (add GEMINI_API_KEY in Secrets). The automatic summary and search still work.", err="The AI could not answer now. The automatic summary and search still work.",
               privacy="Your file is read in memory for this session and is not saved by the app. Do not upload secrets.", ai_summ="Summarise this document for me in clear, short points. List the most important facts, numbers, dates and any deadlines or actions. Use only the document.",
               ai_det="From the document only, list the key details: names of organisations and people, dates, deadlines, amounts, obligations and contact details. Quote the exact words, and say 'not stated' for anything missing."),
    "fr": dict(quiz="Étudier : quiz d'entraînement", topic="Thème", all="Tous les thèmes", n="Questions", new="Nouvelles questions", check="Vérifier mes réponses", choose="Choisissez une réponse",
               right="Correct.", wrong="Pas tout à fait.", answer="Bonne réponse", why="Pourquoi", slip="Erreur fréquente", score="Votre score", retry="Essayez une autre série pour vous entraîner davantage.",
               unanswered="Pas de réponse.", docs="Assistant de documents : envoyer un fichier", up="Envoyez un PDF, un fichier Word (.docx) ou un texte", read="Fichier lu", chars="caractères", pages="pages/sections",
               summ="Résumer", det="Trouver les détails clés", ask="Posez une question sur le document", go="Trouver la réponse", ai="Utiliser l'IA sur ce document (envoie son texte à Gemini)",
               clear="Retirer le document", noai="L'IA n'est pas encore configurée (ajoutez GEMINI_API_KEY dans Secrets). Le résumé et la recherche automatiques fonctionnent.", err="L'IA n'a pas pu répondre maintenant. Le résumé et la recherche automatiques fonctionnent.",
               privacy="Votre fichier est lu en mémoire pour cette session et n'est pas enregistré par l'application. N'envoyez pas de secrets.", ai_summ="Résume ce document en points courts et clairs. Liste les faits, chiffres, dates et échéances ou actions les plus importants. Utilise uniquement le document.",
               ai_det="À partir du document uniquement, liste les détails clés : organisations et personnes, dates, échéances, montants, obligations et coordonnées. Cite les mots exacts et indique « non précisé » pour ce qui manque."),
    "rw": dict(quiz="Kwiga: ikizamini cyo kwitoza", topic="Isomo", all="Amasomo yose", n="Ibibazo", new="Ibibazo bishya", check="Genzura ibisubizo byanjye", choose="Hitamo igisubizo",
               right="Ni byo.", wrong="Si ko biri.", answer="Igisubizo nyacyo", why="Impamvu", slip="Ikosa risanzwe", score="Amanota yawe", retry="Gerageza urundi rutonde ngo wongere witoze.",
               unanswered="Nta gisubizo.", docs="Umufasha w'inyandiko: shyiramo dosiye", up="Shyiramo PDF, Word (.docx) cyangwa inyandiko", read="Dosiye yasomwe", chars="inyuguti", pages="amapaji/ibice",
               summ="Incamake", det="Shakisha amakuru y'ingenzi", ask="Baza ikibazo ku nyandiko", go="Shakisha igisubizo", ai="Koresha AI kuri iyi nyandiko (yohereza umwandiko kuri Gemini)",
               clear="Kuraho inyandiko", noai="AI ntirashyirwaho (shyiramo GEMINI_API_KEY muri Secrets). Incamake no gushakisha byikora biracyakora.", err="AI ntiyashoboye gusubiza ubu. Incamake no gushakisha byikora biracyakora.",
               privacy="Dosiye yawe isomerwa mu kibuga mu isomo ryawe kandi ntibikwa na porogaramu. Ntukohereze ibanga.", ai_summ="Mpa incamake y'iyi nyandiko mu ngingo ngufi zisobanutse. Andika ibintu by'ingenzi, imibare, amatariki n'ibigomba gukorwa. Koresha inyandiko gusa.",
               ai_det="Ukurikije inyandiko gusa, andika amakuru y'ingenzi: ibigo n'abantu, amatariki, ibigomba kurangizwa, amafaranga, inshingano n'uko wabavugisha. Andika amagambo nyayo, kandi ushyiremo «ntibivugwa» ku bibura."),
    "sw": dict(quiz="Jifunze: jaribio la mazoezi", topic="Mada", all="Mada zote", n="Maswali", new="Maswali mapya", check="Kagua majibu yangu", choose="Chagua jibu",
               right="Sahihi.", wrong="Si kabisa.", answer="Jibu sahihi", why="Kwa nini", slip="Kosa la kawaida", score="Alama zako", retry="Jaribu seti nyingine kwa mazoezi zaidi.",
               unanswered="Hakujibiwa.", docs="Msaidizi wa hati: pakia faili", up="Pakia PDF, faili la Word (.docx) au maandishi", read="Faili limesomwa", chars="herufi", pages="kurasa/sehemu",
               summ="Fupisha", det="Tafuta maelezo muhimu", ask="Uliza swali kuhusu hati", go="Tafuta jibu", ai="Tumia AI kwenye hati hii (hutuma maandishi kwa Gemini)",
               clear="Ondoa hati", noai="AI bado haijawekwa (ongeza GEMINI_API_KEY kwenye Secrets). Muhtasari na utafutaji wa kiotomatiki bado vinafanya kazi.", err="AI haikuweza kujibu sasa. Muhtasari na utafutaji wa kiotomatiki bado vinafanya kazi.",
               privacy="Faili lako husomwa kwenye kumbukumbu kwa kipindi hiki na halihifadhiwi na programu. Usipakie siri.", ai_summ="Nifupishie hati hii kwa pointi fupi na wazi. Orodhesha ukweli muhimu, namba, tarehe na tarehe za mwisho au hatua. Tumia hati pekee.",
               ai_det="Kutoka kwenye hati pekee, orodhesha maelezo muhimu: taasisi na watu, tarehe, tarehe za mwisho, kiasi, wajibu na mawasiliano. Nukuu maneno halisi, na andika 'haijatajwa' kwa kisichokuwepo."),
}


def _u(lang):
    return U.get(lang, U["en"])


def render_quiz(st, lang):
    u = _u(lang)
    topics = ["all"] + list(QD.TOPICS)
    with st.expander(u["quiz"]):
        c1, c2 = st.columns(2)
        with c1:
            topic = st.selectbox(u["topic"], topics, format_func=lambda t: u["all"] if t == "all" else QD.TOPICS[t][lang], key=f"quiz_topic_{lang}")
        with c2:
            n = st.slider(u["n"], 3, 30, 5, key=f"quiz_n_{lang}")
        seed_key, chk_key = f"quiz_seed_{lang}", f"quiz_checked_{lang}"
        if seed_key not in st.session_state:
            st.session_state[seed_key] = 0
        if st.button(u["new"], key=f"quiz_new_{lang}"):
            st.session_state[seed_key] += 1
            st.session_state[chk_key] = False
        seed = st.session_state[seed_key]
        sig_key = f"quiz_sig_{lang}"
        if st.session_state.get(sig_key) != (topic, n, seed):   # a different set of questions: forget the old result
            st.session_state[sig_key] = (topic, n, seed)
            st.session_state[chk_key] = False
        qs = QD.pick(topic, n, seed=f"{topic}-{n}-{seed}")
        checked = bool(st.session_state.get(chk_key))
        picks = []
        for i, q in enumerate(qs):
            opts = QD.options(q, lang)
            key = "quiz_" + hashlib.md5(f"{lang}|{topic}|{n}|{seed}|{i}|{q['q']['en']}".encode()).hexdigest()[:12]
            choice = st.radio(f"{i + 1}. {q['q'][lang]}", opts, index=None, key=key, disabled=checked)
            picks.append(None if choice is None else opts.index(choice))
        if st.button(u["check"], type="primary", key=f"quiz_check_{lang}"):
            st.session_state[chk_key] = True
            st.rerun()
        if checked:
            score = 0
            for i, (q, p) in enumerate(zip(qs, picks)):
                opts = QD.options(q, lang)
                if p == q["ans"]:
                    score += 1
                    st.success(f"{i + 1}. {u['right']} {q['why'][lang]}")
                elif p is None:
                    st.warning(f"{i + 1}. {u['unanswered']} **{u['answer']}:** {opts[q['ans']]}. {q['why'][lang]}")
                else:
                    st.error(f"{i + 1}. {u['wrong']} **{u['answer']}:** {opts[q['ans']]}.  \n**{u['why']}:** {q['why'][lang]}  \n**{u['slip']}:** {q['slip'][lang]}")
            st.markdown(f"**{u['score']}: {score} / {len(qs)}**  \n{u['retry']}")


def render_docs(st, lang, ai_call):
    """ai_call(question, document_text) -> str; may raise (MissingAPIKeyError is reported as 'not set up')."""
    u = _u(lang)
    with st.expander(u["docs"]):
        st.caption(u["privacy"])
        up = st.file_uploader(u["up"], type=list(DA.EXTS), key=f"doc_up_{lang}")
        if up is None:
            return
        try:
            data = up.getvalue()
            sig = (up.name, len(data), hashlib.md5(data).hexdigest())
            cache = st.session_state.get("doc_cache")
            if not cache or cache["sig"] != sig:
                cache = {"sig": sig, "pages": DA.extract_pages(up.name, data)}
                st.session_state["doc_cache"] = cache
            pages = cache["pages"]
        except DA.DocError as e:
            st.warning(DA.MSG.get(str(e), DA.MSG["bad"])[lang if lang in DA.LANGS else "en"])
            return
        k = lang if lang in DA.LANGS else "en"
        st.caption(f"{u['read']}: {up.name} · {len(pages)} {u['pages']} · {sum(len(p) for p in pages):,} {u['chars']}")
        use_ai = st.checkbox(u["ai"], key=f"doc_ai_{lang}")
        out_key = f"doc_out_{lang}"
        c1, c2 = st.columns(2)
        want = None
        with c1:
            if st.button(u["summ"], key=f"doc_sum_{lang}", use_container_width=True):
                want = ("summary", "")
        with c2:
            if st.button(u["det"], key=f"doc_det_{lang}", use_container_width=True):
                want = ("details", "")
        question = st.text_input(u["ask"], key=f"doc_q_{lang}")
        if st.button(u["go"], key=f"doc_go_{lang}") and question.strip():
            want = ("answer", question.strip())
        if want:
            kind, qtext = want
            text = None
            if use_ai:
                prompt = {"summary": u["ai_summ"], "details": u["ai_det"], "answer": qtext}[kind]
                try:
                    with st.spinner("…"):
                        text = ai_call(prompt, DA.full_text(pages))
                except Exception as e:  # a missing key is reported plainly; any other failure gets a generic message
                    text = u["noai"] if e.__class__.__name__ == "MissingAPIKeyError" else u["err"]
            if text is None:
                text = {"summary": lambda: DA.render_summary(pages, k), "details": lambda: DA.render_details(pages, k), "answer": lambda: DA.render_answer(qtext, pages, k)}[kind]()
            st.session_state[out_key] = text
        if st.session_state.get(out_key):
            st.markdown(st.session_state[out_key])
