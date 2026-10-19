"""Business and school protection: review many suspicious messages at once, see trends, brief staff.
Pure logic (no Streamlit), reusing the existing detector. Nothing is written to disk or sent anywhere.
Counts are only of the messages the organisation pasted or uploaded; they are not a measure of all attacks."""
from __future__ import annotations
import csv
import io
import re
from collections import Counter
from detector import analyze, next_steps

LANGS = ("en", "fr", "rw", "sw")
MAX_MESSAGES = 300
MAX_CHARS = 3000          # per message
VERDICT_ORDER = {"high": 0, "verify": 1, "ok": 2}
DATE_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})")


def split_messages(blob):
    """Messages separated by a line containing only --- (or three or more blank lines)."""
    parts = re.split(r"\n\s*-{3,}\s*\n|\n\s*\n\s*\n\s*\n", (blob or "").replace("\r\n", "\n"))
    return [p.strip() for p in parts if p.strip()]


def parse_csv(data: bytes):
    """CSV with a header. Columns used (any case): message/text, date, channel, reported_by."""
    text = data.decode("utf-8-sig", errors="replace")
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        low = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        msg = low.get("message") or low.get("text") or low.get("sms") or ""
        if msg:
            rows.append({"message": msg, "date": low.get("date", ""), "channel": low.get("channel", ""),
                         "reported_by": low.get("reported_by", "") or low.get("reporter", "")})
    return rows


def review(items):
    """items: list of dicts (message, date, channel, reported_by) or plain strings. Returns list of records."""
    out = []
    for i, it in enumerate(list(items)[:MAX_MESSAGES], 1):
        if isinstance(it, str):
            it = {"message": it}
        msg = (it.get("message") or "")[:MAX_CHARS]
        res = analyze(msg)
        signs = [f for f in res.findings if f.severity != "low"]
        d = it.get("date", "")
        out.append({"n": i, "message": msg, "date": d if DATE_RE.match(d or "") else "", "channel": it.get("channel", "") or "—",
                    "reported_by": it.get("reported_by", ""), "verdict": res.verdict, "language": res.language,
                    "signs": [f.rule_id for f in signs], "result": res})
    out.sort(key=lambda r: (VERDICT_ORDER[r["verdict"]], -len(r["signs"]), r["n"]))
    return out


def summary(records):
    c = Counter(r["verdict"] for r in records)
    signs = Counter(s for r in records for s in r["signs"])
    channels = Counter(r["channel"] for r in records if r["verdict"] != "ok")
    by_day = Counter(r["date"] for r in records if r["date"] and r["verdict"] != "ok")
    by_month = Counter(r["date"][:7] for r in records if r["date"] and r["verdict"] != "ok")
    langs = Counter(r["language"] for r in records if r["verdict"] != "ok")
    return {"total": len(records), "high": c["high"], "verify": c["verify"], "ok": c["ok"], "signs": signs,
            "channels": channels, "by_day": dict(sorted(by_day.items())), "by_month": dict(sorted(by_month.items())), "langs": langs}


def trend_note(by_month, lang="en"):
    """Plain wording only when there are at least two months; never claims more than the pasted data shows."""
    m = list(by_month.items())
    if len(m) < 2:
        return ""
    (m0, a), (m1, b) = m[-2], m[-1]
    k = 0 if b > a else 1 if b < a else 2
    tpl = {"en": ("Flagged messages went up", "Flagged messages went down", "Flagged messages stayed the same"),
           "fr": ("Les messages signalés sont en hausse", "Les messages signalés sont en baisse", "Les messages signalés sont stables"),
           "rw": ("Ubutumwa bwagaragajwe bwariyongereye", "Ubutumwa bwagaragajwe bwaragabanutse", "Ubutumwa bwagaragajwe ntibwahindutse"),
           "sw": ("Ujumbe uliotiliwa shaka umeongezeka", "Ujumbe uliotiliwa shaka umepungua", "Ujumbe uliotiliwa shaka haujabadilika")}[lang][k]
    tail = {"en": "({a} in {m0}, {b} in {m1}; only the messages you added).", "fr": "({a} en {m0}, {b} en {m1} ; seulement les messages ajoutés).",
            "rw": "({a} muri {m0}, {b} muri {m1}; ubwo wongeyemo gusa).", "sw": "({a} mwezi {m0}, {b} mwezi {m1}; ujumbe ulioongeza tu)."}[lang]
    return tpl + " " + tail.format(a=a, b=b, m0=m0, m1=m1)


def rule_text(rule_id, lang):
    """(title, why, advice) for a rule id in one language."""
    from safety_rules import RULES
    for r in RULES:
        if r["id"] == rule_id:
            return r["title"][lang], r["why"][lang], r["advice"][lang]
    return rule_id, "", ""


def staff_briefing(records, lang="en", org="", top=5):
    """Awareness briefing built from the warning signs actually seen in this organisation's messages."""
    s = summary(records)
    H = {"en": ("Staff awareness briefing", "What we saw in the messages reviewed", "Warning signs most often seen", "What to do",
                "Golden rules for everyone", "Not a complete picture: it covers only the messages added, and a message with no warning signs is not proven safe."),
         "fr": ("Note de sensibilisation du personnel", "Ce que nous avons vu dans les messages examinés", "Signes d'alerte les plus fréquents", "Que faire",
                "Règles d'or pour tous", "Image incomplète : seuls les messages ajoutés sont couverts, et un message sans signe d'alerte n'est pas prouvé sûr."),
         "rw": ("Incamake yo gukangurira abakozi", "Ibyo twabonye mu butumwa bwasuzumwe", "Ibimenyetso by'ubuhemu bigaragara cyane", "Icyo gukora",
                "Amategeko y'ingenzi kuri bose", "Ishusho si yuzuye: ni ubutumwa bwongewemo gusa, kandi ubutumwa budafite ibimenyetso ntibwemejwe ko butekanye."),
         "sw": ("Muhtasari wa uhamasishaji wa wafanyakazi", "Tulichoona kwenye ujumbe uliokaguliwa", "Dalili za hatari zinazoonekana zaidi", "Cha kufanya",
                "Kanuni muhimu kwa kila mtu", "Picha si kamili: ni ujumbe ulioongezwa tu, na ujumbe usio na dalili haujathibitishwa kuwa salama.")}[lang]
    rules = {"en": ["Never share a PIN, password or one-time code with anyone, including someone claiming to be the bank, mobile money, boss or IT.",
                    "Do not open links or attachments you did not expect. Type the official address yourself.",
                    "Pressure, secrecy and 'pay a fee to receive money' are warning signs. Stop and verify.",
                    "Verify any payment or account change by calling a number you already know, not the one in the message.",
                    "Report suspicious messages to the person responsible for security and to your provider."],
             "fr": ["Ne partagez jamais un PIN, un mot de passe ou un code à usage unique, même avec quelqu'un qui se dit banque, mobile money, chef ou service informatique.",
                    "N'ouvrez pas de liens ou pièces jointes inattendus. Tapez vous-même l'adresse officielle.",
                    "Pression, secret et « payez des frais pour recevoir de l'argent » sont des signes d'alerte. Arrêtez et vérifiez.",
                    "Vérifiez tout paiement ou changement de compte en appelant un numéro que vous connaissez déjà, pas celui du message.",
                    "Signalez les messages suspects au responsable de la sécurité et à votre opérateur."],
             "rw": ["Ntugasangire umuntu PIN, ijambo ry'ibanga cyangwa kode ikoreshwa rimwe, nubwo yaba yiyita banki, mobile money, umuyobozi cyangwa ushinzwe IT.",
                    "Ntukingure link cyangwa dosiye utari witeze. Andika wowe ubwawe aderesi yemewe.",
                    "Igitutu, ibanga no «kwishyura amafaranga ngo wakire amafaranga» ni ibimenyetso by'ubuhemu. Hagarara ugenzure.",
                    "Genzura buri kwishyura cyangwa guhindura konti uhamagara nimero usanzwe uzi, atari iyo mu butumwa.",
                    "Menyesha ubutumwa bukemangwa ushinzwe umutekano n'umukoresha wawe wa telefone."],
             "sw": ["Usishiriki kamwe PIN, nywila au msimbo wa mara moja na yeyote, hata anayejidai kuwa benki, mobile money, bosi au IT.",
                    "Usifungue viungo au viambatisho usivyotarajia. Andika mwenyewe anwani rasmi.",
                    "Shinikizo, usiri na 'lipa ada ili upokee pesa' ni dalili za hatari. Simama na uthibitishe.",
                    "Thibitisha malipo au mabadiliko ya akaunti kwa kupiga namba unayoijua tayari, si ile iliyo kwenye ujumbe.",
                    "Ripoti ujumbe unaotia shaka kwa mhusika wa usalama na mtoa huduma wako."]}[lang]
    lines = [f"# {H[0]}" + (f" - {org}" if org else ""), "",
             f"## {H[1]}",
             {"en": f"{s['total']} messages reviewed: {s['high']} high concern, {s['verify']} to verify, {s['ok']} with no warning signs.",
              "fr": f"{s['total']} messages examinés : {s['high']} très préoccupants, {s['verify']} à vérifier, {s['ok']} sans signe d'alerte.",
              "rw": f"Ubutumwa {s['total']} bwasuzumwe: {s['high']} buteye impungenge nyinshi, {s['verify']} bwo kugenzura, {s['ok']} nta bimenyetso.",
              "sw": f"Ujumbe {s['total']} umekaguliwa: {s['high']} wa wasiwasi mkubwa, {s['verify']} wa kuthibitisha, {s['ok']} bila dalili."}[lang], "",
             f"## {H[2]}"]
    if not s["signs"]:
        lines.append("-")
    for rid, n in s["signs"].most_common(top):
        title, why, adv = rule_text(rid, lang)
        lines += [f"- **{title}** ({n}): {why}", f"  - {H[3]}: {adv}"]
    lines += ["", f"## {H[4]}"] + [f"{i}. {r}" for i, r in enumerate(rules, 1)] + ["", f"_{H[5]}_"]
    return "\n".join(lines)


def _safe(v):
    v = str(v)
    return "'" + v if v[:1] in ("=", "+", "-", "@", "\t", "\r") else v


def report_csv(records, lang="en", include_text=True):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["no", "verdict", "date", "channel", "reported_by", "language", "warning_signs", "next_steps"] + (["message"] if include_text else []))
    for r in records:
        titles = "; ".join(rule_text(s, lang)[0] for s in r["signs"])
        steps = " | ".join(next_steps(r["result"], lang)[:3])
        row = [r["n"], r["verdict"], r["date"], _safe(r["channel"]), _safe(r["reported_by"]), r["language"], titles, steps]
        if include_text:
            t = r["message"].replace("\n", " ")
            row.append(_safe(t))   # stops spreadsheet formula injection
        w.writerow(row)
    return buf.getvalue()
