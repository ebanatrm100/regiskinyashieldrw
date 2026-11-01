"""The 'Cyber News' tab (Cyber Intel): current, sourced information on cybersecurity, awareness and cybercrime for a chosen period.
Asks which period when the question names none. Logic lives in cyber_intel.py (pure Python, tested without Streamlit)."""
from __future__ import annotations
import re
from datetime import timedelta

import cyber_intel as ci

TAB = {"en": "Cyber News", "fr": "Actualité cyber", "rw": "Amakuru ya Cyber", "sw": "Habari za Cyber"}
S = {
    "en": dict(title="Current cybersecurity, awareness and cybercrime information", intro="Ask in your own words, for example “ransomware attacks last week”, “mobile money fraud in Rwanda this month” or “phishing alerts yesterday”. Results are headlines from trusted publishers (official bodies, CERTs, police, security researchers, news agencies), each with a link to read the original.",
               ask="What do you want to know?", ph="e.g. cybercrime arrests last two months", topics="Topics", t_security="Cybersecurity", t_awareness="Awareness", t_crime="Cybercrime", go="Search",
               which="Which time period do you want?", which_help="You did not say when, so please choose a period (or type it, for example “last week”).", custom_go="Search these dates", start="From", end="To",
               shown="Showing", period_word="period", found="results from trusted sources", none="Nothing from the trusted sources was found for this period. Try a longer period or different words.",
               change="Choose another period", official="Official body", research="Security research", news="News agency", sources="Sources that gave results", failed="Not reachable this time",
               dropped="Nothing matched your extra words ({w}), so the search was widened to the whole topic.", note="These are headlines and short summaries from the publishers listed, not verified by KinyaShield. Open the link and compare with an official source before acting. Direct feeds only keep recent items, so for long periods most results come from a dated news search limited to trusted publishers. Nothing here is legal, financial or investigation advice.",
               fetched="Fetched", loading="Searching trusted sources…", topic_note="Topics searched", empty_q="Type a question, or just choose the topics and a period."),
    "fr": dict(title="Informations actuelles sur la cybersécurité, la sensibilisation et la cybercriminalité", intro="Posez votre question librement, par exemple « attaques de rançongiciel la semaine dernière », « fraude mobile money au Rwanda ce mois-ci » ou « alertes d'hameçonnage hier ». Les résultats sont des titres de sources fiables (organismes officiels, CERT, police, chercheurs en sécurité, agences de presse), chacun avec un lien vers l'original.",
               ask="Que voulez-vous savoir ?", ph="ex. arrestations de cybercriminels ces deux derniers mois", topics="Sujets", t_security="Cybersécurité", t_awareness="Sensibilisation", t_crime="Cybercriminalité", go="Rechercher",
               which="Quelle période voulez-vous ?", which_help="Vous n'avez pas précisé la période ; choisissez-en une (ou écrivez-la, par exemple « la semaine dernière »).", custom_go="Rechercher ces dates", start="Du", end="Au",
               shown="Affichage", period_word="période", found="résultats de sources fiables", none="Aucun résultat des sources fiables pour cette période. Essayez une période plus longue ou d'autres mots.",
               change="Choisir une autre période", official="Organisme officiel", research="Recherche en sécurité", news="Agence de presse", sources="Sources ayant donné des résultats", failed="Injoignables cette fois",
               dropped="Rien ne correspondait à vos mots en plus ({w}) ; la recherche a été élargie à tout le sujet.", note="Ce sont des titres et courts résumés des éditeurs listés, non vérifiés par KinyaShield. Ouvrez le lien et comparez avec une source officielle avant d'agir. Les flux directs ne gardent que les éléments récents ; pour les longues périodes, la plupart des résultats viennent d'une recherche d'actualités datée limitée aux éditeurs fiables. Rien ici n'est un conseil juridique, financier ou d'enquête.",
               fetched="Récupéré", loading="Recherche dans les sources fiables…", topic_note="Sujets recherchés", empty_q="Saisissez une question, ou choisissez simplement les sujets et une période."),
    "rw": dict(title="Amakuru agezweho ku mutekano wa interineti, ubukangurambaga n'ibyaha byo kuri interineti", intro="Baza mu magambo yawe, urugero «ibitero bya ransomware icyumweru gishize», «uburiganya bwa mobile money mu Rwanda uku kwezi» cyangwa «amakuru y'uburiganya ejo hashize». Ibisubizo ni imitwe y'inkuru ivuye ku bitangazamakuru n'ibigo byizewe (inzego za leta, CERT, polisi, abashakashatsi, ibigo by'amakuru), buri kimwe gifite umurongo ujya ku nkuru ya nyayo.",
               ask="Urashaka kumenya iki?", ph="urugero: abafashwe bakoze ibyaha byo kuri interineti mu mezi abiri ashize", topics="Ingingo", t_security="Umutekano wa interineti", t_awareness="Ubukangurambaga", t_crime="Ibyaha byo kuri interineti", go="Shakisha",
               which="Ushaka igihe kingana iki?", which_help="Ntiwavuze igihe, none hitamo igihe (cyangwa ukyandike, urugero «icyumweru gishize»).", custom_go="Shakisha ayo matariki", start="Kuva", end="Kugeza",
               shown="Herekanwa", period_word="igihe", found="ibisubizo biva ku masoko yizewe", none="Nta kintu cyabonetse ku masoko yizewe muri iki gihe. Gerageza igihe kirekire cyangwa andi magambo.",
               change="Hitamo ikindi gihe", official="Urwego rwemewe", research="Ubushakashatsi ku mutekano", news="Ikigo cy'amakuru", sources="Amasoko yatanze ibisubizo", failed="Ntiyabonetse iki gihe",
               dropped="Nta kintu cyahuye n'amagambo wongeyeho ({w}), bityo gushakisha byagutse ku ngingo yose.", note="Iyi ni imitwe n'incamake bitangwa n'abatangaza bavuzwe, KinyaShield ntiyabigenzuye. Fungura umurongo kandi ugereranye n'isoko ryemewe mbere yo gufata icyemezo. Ibyakirwa mu buryo butaziguye bibika ibya vuba gusa, bityo ku bihe birebure ibisubizo byinshi bivuye mu gushakisha amakuru ku matariki bigarukira ku batangaza bizewe. Nta kintu hano ari inama y'amategeko, y'imari cyangwa y'iperereza.",
               fetched="Byakuwe", loading="Turashakisha mu masoko yizewe…", topic_note="Ingingo zashakishijwe", empty_q="Andika ikibazo, cyangwa uhitemo ingingo n'igihe gusa."),
    "sw": dict(title="Taarifa za sasa za usalama wa mtandao, uhamasishaji na uhalifu wa mtandaoni", intro="Uliza kwa maneno yako, kwa mfano «mashambulizi ya ransomware wiki iliyopita», «ulaghai wa pesa za simu Rwanda mwezi huu» au «tahadhari za hadaa jana». Matokeo ni vichwa vya habari kutoka kwa wachapishaji wa kuaminika (taasisi rasmi, CERT, polisi, watafiti wa usalama, mashirika ya habari), kila kimoja na kiungo cha asili.",
               ask="Unataka kujua nini?", ph="mf. kukamatwa kwa wahalifu wa mtandaoni miezi miwili iliyopita", topics="Mada", t_security="Usalama wa mtandao", t_awareness="Uhamasishaji", t_crime="Uhalifu wa mtandaoni", go="Tafuta",
               which="Unataka kipindi gani?", which_help="Hukutaja wakati, tafadhali chagua kipindi (au kiandike, mfano «wiki iliyopita»).", custom_go="Tafuta tarehe hizi", start="Kuanzia", end="Hadi",
               shown="Inaonyesha", period_word="kipindi", found="matokeo kutoka vyanzo vya kuaminika", none="Hakuna kilichopatikana kutoka vyanzo vya kuaminika kwa kipindi hiki. Jaribu kipindi kirefu au maneno mengine.",
               change="Chagua kipindi kingine", official="Taasisi rasmi", research="Utafiti wa usalama", news="Shirika la habari", sources="Vyanzo vilivyotoa matokeo", failed="Havikufikika safari hii",
               dropped="Hakuna kilicholingana na maneno yako ya ziada ({w}), kwa hiyo utafutaji ulipanuliwa kwa mada nzima.", note="Hivi ni vichwa vya habari na muhtasari mfupi kutoka kwa wachapishaji walioorodheshwa, havijathibitishwa na KinyaShield. Fungua kiungo na ulinganishe na chanzo rasmi kabla ya kuchukua hatua. Mitiririko ya moja kwa moja huhifadhi vitu vya hivi karibuni tu, hivyo kwa vipindi virefu matokeo mengi hutoka kwenye utafutaji wa habari wenye tarehe unaoishia kwa wachapishaji wa kuaminika. Hakuna hapa ni ushauri wa kisheria, kifedha au wa uchunguzi.",
               fetched="Imepatikana", loading="Inatafuta kwenye vyanzo vya kuaminika…", topic_note="Mada zilizotafutwa", empty_q="Andika swali, au chagua mada na kipindi tu."),
}
_BADGE = {"official": "official", "research": "research", "news": "news"}


def _md(text: str) -> str:
    return re.sub(r"[\[\]]", lambda m: "(" if m.group() == "[" else ")", text or "")


def render_results(st, res: dict, lang: str, tx: dict):
    p = res["period"]
    st.markdown(f"**{tx['shown']}:** {ci.label(p, lang)} ({p['start']} → {p['end']}) · {res['total']} {tx['found']}")
    if res.get("extra_dropped"):
        st.caption(tx["dropped"].format(w=res["extra_dropped"]))
    if not res["total"]:
        st.info(tx["none"])
    names = {"security": tx["t_security"], "awareness": tx["t_awareness"], "crime": tx["t_crime"]}
    for t in res["topics"]:
        items = res["items"].get(t) or []
        if not items:
            continue
        st.subheader(f"{names[t]} ({len(items)})")
        for it in items:
            st.markdown(f"**[{_md(it['title'])}]({it['url']})**  \n:gray[{_md(it['source'])} · {tx[_BADGE.get(it['kind'], 'news')]} · {it['date']}]")
            if it.get("summary"):
                st.caption(_md(it["summary"]))
    if res.get("sources"):
        st.caption(f"**{tx['sources']}:** " + ", ".join(f"{n} ({c})" for n, _k, c in res["sources"][:14]))
    if res.get("failed"):
        st.caption(f"{tx['failed']}: " + ", ".join(res["failed"][:10]))
    st.caption(f"{tx['fetched']}: {res['fetched']} (Kigali)")
    st.caption(tx["note"])


def render(st, lang: str):
    lang = lang if lang in S else "en"
    tx = S[lang]
    ss = st.session_state
    kq, kp, kt, kc = (f"intel_{n}_{lang}" for n in ("q", "period", "topics", "custom"))
    st.subheader(tx["title"])
    st.write(tx["intro"])
    names = {"security": tx["t_security"], "awareness": tx["t_awareness"], "crime": tx["t_crime"]}
    with st.form(f"intel_form_{lang}"):
        text = st.text_input(tx["ask"], placeholder=tx["ph"], key=f"intel_text_{lang}", max_chars=200)
        chosen = st.multiselect(tx["topics"], list(ci.TOPICS), default=list(ci.TOPICS), format_func=lambda x: names[x], key=f"intel_topics_{lang}")
        go = st.form_submit_button(tx["go"])
    if go:
        topics = ci.parse_topics(text) or chosen or list(ci.TOPICS)
        per = ci.parse_time(text)
        ss[kq], ss[kt], ss[kp], ss[kc] = text, topics, per, False
    if kq not in ss:
        return
    if ss.get(kp) is None:                           # no period named: ask, with choices
        st.markdown(f"### {tx['which']}")
        st.caption(tx["which_help"])
        L = ci.LABELS[lang]
        cols = st.columns(3)
        for i, key in enumerate(ci.KEYS):
            if cols[i % 3].button(L[key], key=f"intel_pick_{key}_{lang}", use_container_width=True):
                ss[kp] = ci.period_from_key(key)
                st.rerun()
        if cols[len(ci.KEYS) % 3].button(L["custom"], key=f"intel_pick_custom_{lang}", use_container_width=True):
            ss[kc] = True
        if ss.get(kc):
            today = ci.today_local()
            a, b = st.columns(2)
            d1 = a.date_input(tx["start"], value=today - timedelta(days=30), max_value=today, key=f"intel_d1_{lang}")
            d2 = b.date_input(tx["end"], value=today, max_value=today, key=f"intel_d2_{lang}")
            if st.button(tx["custom_go"], key=f"intel_custom_go_{lang}"):
                ss[kp] = ci.custom_period(d1, d2)
                st.rerun()
        return
    per, topics = ss[kp], ss.get(kt) or list(ci.TOPICS)
    st.caption(f"{tx['topic_note']}: " + ", ".join(names[t] for t in topics))
    with st.spinner(tx["loading"]):
        res = ci.search(per, topics, lang, ss.get(kq, ""))
    render_results(st, res, lang, tx)
    if st.button(tx["change"], key=f"intel_change_{lang}"):
        ss[kp] = None
        st.rerun()
