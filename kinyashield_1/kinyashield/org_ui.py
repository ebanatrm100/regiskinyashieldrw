"""Streamlit tab for businesses and schools: review many messages, trends, staff briefing, report download.
Session only: nothing is saved by the app. Logic lives in org_dashboard.py (testable without Streamlit)."""
from __future__ import annotations
import org_dashboard as OD
from detector import next_steps

TAB = {"en": "Business & Schools", "fr": "Entreprises et écoles", "rw": "Ubucuruzi n'amashuri", "sw": "Biashara na Shule"}

U = {
    "en": dict(title="Protect your organisation", intro="Paste suspicious messages your staff or students received, or upload a CSV. KinyaShield reviews them all, shows the warning signs, trends, and prepares a briefing for your team.",
               org="Organisation name (optional)", paste="Paste messages (separate each message with a line containing only ---)", up="Or upload a CSV (columns: message, date YYYY-MM-DD, channel, reported_by)",
               run="Review messages", none="Add at least one message first.", cap="Only the first {n} messages are reviewed.", sample="Load sample (synthetic) messages",
               privacy="Messages are checked in this session and not saved by the app. Do not include passwords, PINs or customers' private data. Remove names if you can.",
               total="Reviewed", high="High concern", verify="To verify", ok="No warning signs", queue="Review queue", signs="Warning signs", trends="Trends",
               by_sign="Most common warning signs", by_chan="Flagged by channel", by_month="Flagged by month", by_day="Flagged by day",
               filt="Show", f_all="All", f_flag="Flagged only", why="Why it was flagged", steps="Safe next steps", msg="Message", nothing="No warning signs found. This does not prove it is safe.",
               brief="Staff briefing", brief_dl="Download briefing (.md)", rep_dl="Download report (.csv)", hide="Leave message text out of the report",
               edu="Teach your staff", edu_note="The briefing uses the warning signs found in your own messages. Share it, then repeat the review every month.",
               limit="Counts cover only the messages you added. A message with no warning signs is not proven safe, and a flagged one is not proven a scam. Verify through official channels.",
               col=dict(n="No", v="Verdict", d="Date", c="Channel", s="Warning signs", m="Message"), vl=dict(high="High concern", verify="To verify", ok="No warning signs")),
    "fr": dict(title="Protégez votre organisation", intro="Collez les messages suspects reçus par votre personnel ou vos élèves, ou envoyez un CSV. KinyaShield les examine tous, montre les signes d'alerte, les tendances et prépare une note pour votre équipe.",
               org="Nom de l'organisation (facultatif)", paste="Collez les messages (séparez chaque message par une ligne contenant seulement ---)", up="Ou envoyez un CSV (colonnes : message, date AAAA-MM-JJ, channel, reported_by)",
               run="Examiner les messages", none="Ajoutez d'abord au moins un message.", cap="Seuls les {n} premiers messages sont examinés.", sample="Charger des messages d'exemple (synthétiques)",
               privacy="Les messages sont vérifiés pendant cette session et ne sont pas enregistrés par l'application. N'incluez pas de mots de passe, PIN ni données privées de clients. Retirez les noms si possible.",
               total="Examinés", high="Très préoccupants", verify="À vérifier", ok="Sans signe d'alerte", queue="File d'examen", signs="Signes d'alerte", trends="Tendances",
               by_sign="Signes d'alerte les plus fréquents", by_chan="Signalés par canal", by_month="Signalés par mois", by_day="Signalés par jour",
               filt="Afficher", f_all="Tous", f_flag="Signalés seulement", why="Pourquoi il est signalé", steps="Prochaines étapes sûres", msg="Message", nothing="Aucun signe d'alerte. Cela ne prouve pas qu'il est sûr.",
               brief="Note pour le personnel", brief_dl="Télécharger la note (.md)", rep_dl="Télécharger le rapport (.csv)", hide="Ne pas inclure le texte des messages dans le rapport",
               edu="Sensibilisez votre personnel", edu_note="La note utilise les signes d'alerte trouvés dans vos propres messages. Partagez-la, puis refaites l'examen chaque mois.",
               limit="Les chiffres ne couvrent que les messages ajoutés. Un message sans signe d'alerte n'est pas prouvé sûr, et un message signalé n'est pas prouvé frauduleux. Vérifiez par les canaux officiels.",
               col=dict(n="N°", v="Verdict", d="Date", c="Canal", s="Signes d'alerte", m="Message"), vl=dict(high="Très préoccupant", verify="À vérifier", ok="Sans signe d'alerte")),
    "rw": dict(title="Kurinda ikigo cyawe", intro="Shyiramo ubutumwa bukemangwa abakozi cyangwa abanyeshuri bakiriye, cyangwa ushyiremo CSV. KinyaShield ibusuzuma bwose, ikerekana ibimenyetso, uko bihinduka, ikanategurira ikipe yawe incamake.",
               org="Izina ry'ikigo (si itegeko)", paste="Shyiramo ubutumwa (butandukanye ukoresheje umurongo urimo --- gusa)", up="Cyangwa ushyiremo CSV (inkingi: message, date YYYY-MM-DD, channel, reported_by)",
               run="Suzuma ubutumwa", none="Banza wongeremo nibura ubutumwa bumwe.", cap="Ubutumwa {n} bwa mbere ni bwo busuzumwa gusa.", sample="Shyiramo ubutumwa bw'icyitegererezo (bwakozwe)",
               privacy="Ubutumwa busuzumirwa muri iri somo kandi ntibubikwa na porogaramu. Ntushyiremo amagambo y'ibanga, PIN cyangwa amakuru bwite y'abakiriya. Kuraho amazina niba bishoboka.",
               total="Bwasuzumwe", high="Impungenge nyinshi", verify="Bwo kugenzura", ok="Nta bimenyetso", queue="Urutonde rwo gusuzuma", signs="Ibimenyetso", trends="Uko bihinduka",
               by_sign="Ibimenyetso bigaragara cyane", by_chan="Ubwagaragajwe ukurikije inzira", by_month="Ubwagaragajwe ku kwezi", by_day="Ubwagaragajwe ku munsi",
               filt="Erekana", f_all="Bwose", f_flag="Ubwagaragajwe gusa", why="Impamvu bwagaragajwe", steps="Intambwe zikurikira zitekanye", msg="Ubutumwa", nothing="Nta bimenyetso. Ibi ntibyemeza ko butekanye.",
               brief="Incamake y'abakozi", brief_dl="Manura incamake (.md)", rep_dl="Manura raporo (.csv)", hide="Ntushyire umwandiko w'ubutumwa muri raporo",
               edu="Igisha abakozi bawe", edu_note="Incamake ikoresha ibimenyetso byabonetse mu butumwa bwawe bwite. Yisangize, hanyuma usubiremo isuzuma buri kwezi.",
               limit="Imibare ireba gusa ubutumwa wongeyemo. Ubutumwa budafite ibimenyetso ntibwemejwe ko butekanye, kandi ubwagaragajwe ntibwemejwe ko ari uburiganya. Genzura unyuze mu nzira zemewe.",
               col=dict(n="No", v="Icyemezo", d="Itariki", c="Inzira", s="Ibimenyetso", m="Ubutumwa"), vl=dict(high="Impungenge nyinshi", verify="Bwo kugenzura", ok="Nta bimenyetso")),
    "sw": dict(title="Linda taasisi yako", intro="Bandika ujumbe unaotia shaka waliopokea wafanyakazi au wanafunzi, au pakia CSV. KinyaShield huukagua wote, huonyesha dalili, mwelekeo, na kuandaa muhtasari kwa timu yako.",
               org="Jina la taasisi (si lazima)", paste="Bandika ujumbe (tenganisha kila ujumbe kwa mstari wenye --- pekee)", up="Au pakia CSV (safu: message, date YYYY-MM-DD, channel, reported_by)",
               run="Kagua ujumbe", none="Ongeza angalau ujumbe mmoja kwanza.", cap="Ujumbe {n} wa kwanza pekee ndio hukaguliwa.", sample="Pakia ujumbe wa mfano (wa kutengenezwa)",
               privacy="Ujumbe hukaguliwa kwenye kipindi hiki na haujahifadhiwa na programu. Usiweke nywila, PIN au taarifa za siri za wateja. Ondoa majina ukiweza.",
               total="Umekaguliwa", high="Wasiwasi mkubwa", verify="Wa kuthibitisha", ok="Bila dalili", queue="Foleni ya ukaguzi", signs="Dalili", trends="Mwelekeo",
               by_sign="Dalili zinazoonekana zaidi", by_chan="Uliotiliwa shaka kwa njia", by_month="Uliotiliwa shaka kwa mwezi", by_day="Uliotiliwa shaka kwa siku",
               filt="Onyesha", f_all="Yote", f_flag="Uliotiliwa shaka pekee", why="Kwa nini umetiliwa shaka", steps="Hatua salama zinazofuata", msg="Ujumbe", nothing="Hakuna dalili. Hii haithibitishi kuwa ni salama.",
               brief="Muhtasari wa wafanyakazi", brief_dl="Pakua muhtasari (.md)", rep_dl="Pakua ripoti (.csv)", hide="Usijumuishe maandishi ya ujumbe kwenye ripoti",
               edu="Wafundishe wafanyakazi wako", edu_note="Muhtasari hutumia dalili zilizopatikana kwenye ujumbe wako mwenyewe. Ushiriki, kisha rudia ukaguzi kila mwezi.",
               limit="Takwimu zinahusu ujumbe ulioongeza tu. Ujumbe usio na dalili haujathibitishwa kuwa salama, na ulioripotiwa haujathibitishwa kuwa ulaghai. Thibitisha kupitia njia rasmi.",
               col=dict(n="Na", v="Uamuzi", d="Tarehe", c="Njia", s="Dalili", m="Ujumbe"), vl=dict(high="Wasiwasi mkubwa", verify="Wa kuthibitisha", ok="Bila dalili")),
}

SAMPLE = [
    {"message": "URGENT: your mobile money account will be blocked. Send your PIN now to verify.", "date": "2026-09-05", "channel": "SMS", "reported_by": "Front desk"},
    {"message": "Congratulations! You won a scholarship of 2,000,000 RWF. Pay a small processing fee first to receive it.", "date": "2026-09-18", "channel": "WhatsApp", "reported_by": "Student"},
    {"message": "Hello, the staff meeting is moved to Thursday 10am in the main hall.", "date": "2026-10-02", "channel": "email", "reported_by": "Admin"},
    {"message": "Boss here, I am in a meeting. Buy gift cards now and send me the codes. Do not tell anyone.", "date": "2026-10-09", "channel": "WhatsApp", "reported_by": "Accountant"},
    {"message": "Your parcel is held. Click the link to pay the customs fee and confirm your account password.", "date": "2026-10-11", "channel": "SMS", "reported_by": "Teacher"},
]


def render(st, lang):
    lang = lang if lang in U else "en"
    u = U[lang]
    st.subheader(u["title"])
    st.write(u["intro"])
    st.caption(u["privacy"])
    key = f"org_{lang}"
    org = st.text_input(u["org"], key=key + "_name")
    if st.button(u["sample"], key=key + "_sample"):
        st.session_state[key + "_text"] = "\n---\n".join(s["message"] for s in SAMPLE)
        st.session_state[key + "_rows"] = SAMPLE
    blob = st.text_area(u["paste"], key=key + "_text", height=170)
    up = st.file_uploader(u["up"], type=["csv"], key=key + "_csv")
    if not st.button(u["run"], type="primary", key=key + "_run", use_container_width=True):
        if not st.session_state.get(key + "_records"):
            return
    else:
        items = []
        if up is not None:
            try:
                items += OD.parse_csv(up.getvalue())
            except Exception:
                st.error("CSV?")
        pasted = OD.split_messages(blob)
        sample_rows = st.session_state.get(key + "_rows") or []
        if sample_rows and len(pasted) == len(sample_rows) and all(p == s["message"] for p, s in zip(pasted, sample_rows)):
            items += sample_rows            # untouched sample keeps its dates and channels
        else:
            items += pasted
        if not items:
            st.info(u["none"])
            return
        if len(items) > OD.MAX_MESSAGES:
            st.caption(u["cap"].format(n=OD.MAX_MESSAGES))
        st.session_state[key + "_records"] = OD.review(items)
    recs = st.session_state[key + "_records"]
    s = OD.summary(recs)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(u["total"], s["total"]); c2.metric(u["high"], s["high"]); c3.metric(u["verify"], s["verify"]); c4.metric(u["ok"], s["ok"])
    st.caption(u["limit"])

    st.markdown(f"### {u['queue']}")
    show = st.radio(u["filt"], [u["f_flag"], u["f_all"]], horizontal=True, key=key + "_filt")
    for r in recs:
        if show == u["f_flag"] and r["verdict"] == "ok":
            continue
        icon = {"high": "🔴", "verify": "🟠", "ok": "🟢"}[r["verdict"]]
        head = f"{icon} #{r['n']} · {u['vl'][r['verdict']]} · {r['channel']}" + (f" · {r['date']}" if r["date"] else "")
        with st.expander(head):
            st.text(r["message"][:600])
            if not r["signs"]:
                st.write(u["nothing"])
            for rid in r["signs"]:
                title, why, adv = OD.rule_text(rid, lang)
                st.markdown(f"**{title}**  \n{u['why']}: {why}")
            if r["signs"]:
                st.markdown(f"**{u['steps']}**")
                for step in next_steps(r["result"], lang)[:4]:
                    st.markdown(f"- {step}")

    st.markdown(f"### {u['trends']}")
    import pandas as pd
    if s["signs"]:
        st.caption(u["by_sign"])
        st.bar_chart(pd.Series({OD.rule_text(k, lang)[0]: v for k, v in s["signs"].most_common(8)}))
    if s["channels"]:
        st.caption(u["by_chan"])
        st.bar_chart(pd.Series(dict(s["channels"])))
    if len(s["by_month"]) >= 2:
        st.caption(u["by_month"])
        st.bar_chart(pd.Series(s["by_month"]))
        st.write(OD.trend_note(s["by_month"], lang))
    elif s["by_day"]:
        st.caption(u["by_day"])
        st.bar_chart(pd.Series(s["by_day"]))

    st.markdown(f"### {u['edu']}")
    st.caption(u["edu_note"])
    brief = OD.staff_briefing(recs, lang, org.strip())
    with st.expander(u["brief"]):
        st.markdown(brief)
    st.download_button(u["brief_dl"], brief.encode("utf-8"), file_name="staff_briefing.md", mime="text/markdown", key=key + "_dlb")
    hide = st.checkbox(u["hide"], key=key + "_hide")
    st.download_button(u["rep_dl"], OD.report_csv(recs, lang, include_text=not hide).encode("utf-8-sig"), file_name="suspicious_messages_report.csv", mime="text/csv", key=key + "_dlr")
