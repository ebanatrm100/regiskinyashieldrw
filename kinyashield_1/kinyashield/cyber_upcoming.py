"""Cyber Intel, UPCOMING part: what is scheduled or due in a future period (tomorrow, next week, next month, upcoming ...).
Pure Python (no Streamlit). Nobody can know future attacks, so this lists only things that really are scheduled or due:
  * recurring security-calendar items computed by rule (Microsoft Patch Tuesday = 2nd Tuesday, Oracle Critical Patch Update = 3rd Tuesday of Jan/Apr/Jul/Oct,
    Safer Internet Day = 2nd Tuesday of February, Data Privacy Day = 28 January, World Password Day = 1st Thursday of May,
    Cybersecurity Awareness Month = October, Computer Security Day = 30 November). These are labelled "recurring calendar rule": check the publisher for changes.
  * remediation deadlines (dueDate) that CISA set in its Known Exploited Vulnerabilities catalogue, fetched live.
Time phrases are understood in English, French, Kinyarwanda and Kiswahili. Every failure is soft."""
from __future__ import annotations
import json
import re
import time
from datetime import date, datetime, timedelta

import cyber_intel as ci
from textutil import fold

FUTURE_KEYS = ("tomorrow", "next_week", "next_2_weeks", "next_month", "next_3_months", "rest_of_year", "next_year")
_UP = r"upcoming|coming|next|ahead|forthcoming|a venir|prochain\w*|bientot|izaza|izaza|yaza|gitaha|utaha|gutaha|ukurikira|zijazo|ujao|ijayo|zijazo|kesho|hazaza|ejo hazaza|future"
_SIMPLE = (
    ("tomorrow", r"\btomorrow\b|\bdemain\b|\bejo hazaza\b|\bejo kuri\b|\bkesho\b"),
    ("next_2_weeks", r"\bnext (?:2|two) weeks\b|\b(?:2|deux) prochaines semaines\b|\bibyumweru (?:2|bibiri) bitaha\b|\bwiki (?:2|mbili) zijazo\b"),
    ("next_week", r"\bnext week\b|\bsemaine prochaine\b|\bla semaine prochaine\b|\bicyumweru gitaha\b|\bwiki ijayo\b"),
    ("next_3_months", r"\bnext (?:3|three) months\b|\b(?:3|trois) prochains mois\b|\bamezi (?:3|atatu) ari imbere\b|\bamezi atatu azaza\b|\bmiezi (?:3|mitatu) ijayo\b"),
    ("next_month", r"\bnext month\b|\bmois prochain\b|\ble mois prochain\b|\bukwezi gutaha\b|\bmwezi ujao\b"),
    ("next_year", r"\bnext year\b|\bannee prochaine\b|\bl'annee prochaine\b|\bumwaka utaha\b|\bmwaka ujao\b"),
    ("rest_of_year", r"\brest of (?:the|this) year\b|\bremainder of the year\b|\ble reste de l'annee\b|\bsalan'? ?(?:y'?)?umwaka\b|\bmwezi ujao wa mwaka\b|\bmwaka huu uliobaki\b|\bkuva ubu kugeza ku musozo w'umwaka\b"),
    ("upcoming", r"\b(?:upcoming|forthcoming|coming (?:days|weeks|events|soon)|what is coming|what'?s coming|a venir|prochains? jours|prochaines? semaines|iminsi izaza|ibizaza|ibigiye kuba|yaza|zijazo|siku zijazo|kinachokuja|vitakavyokuja|matukio yajayo)\b"),
)
LABELS = {
    "en": {"tomorrow": "Tomorrow", "next_week": "Next week", "next_2_weeks": "Next two weeks", "next_month": "Next month", "next_3_months": "Next three months",
           "rest_of_year": "Rest of this year", "next_year": "Next year", "upcoming": "Upcoming (next 30 days)", "n_days": "Next {n} days", "n_weeks": "Next {n} weeks", "n_months": "Next {n} months"},
    "fr": {"tomorrow": "Demain", "next_week": "La semaine prochaine", "next_2_weeks": "Les deux prochaines semaines", "next_month": "Le mois prochain", "next_3_months": "Les trois prochains mois",
           "rest_of_year": "Le reste de l'année", "next_year": "L'année prochaine", "upcoming": "À venir (30 prochains jours)", "n_days": "{n} prochains jours", "n_weeks": "{n} prochaines semaines", "n_months": "{n} prochains mois"},
    "rw": {"tomorrow": "Ejo hazaza", "next_week": "Icyumweru gitaha", "next_2_weeks": "Ibyumweru bibiri bitaha", "next_month": "Ukwezi gutaha", "next_3_months": "Amezi atatu ari imbere",
           "rest_of_year": "Igisigaye cy'uyu mwaka", "next_year": "Umwaka utaha", "upcoming": "Ibigiye kuza (iminsi 30)", "n_days": "Iminsi {n} iri imbere", "n_weeks": "Ibyumweru {n} biri imbere", "n_months": "Amezi {n} ari imbere"},
    "sw": {"tomorrow": "Kesho", "next_week": "Wiki ijayo", "next_2_weeks": "Wiki mbili zijazo", "next_month": "Mwezi ujao", "next_3_months": "Miezi mitatu ijayo",
           "rest_of_year": "Salio la mwaka huu", "next_year": "Mwaka ujao", "upcoming": "Yajayo (siku 30)", "n_days": "Siku {n} zijazo", "n_weeks": "Wiki {n} zijazo", "n_months": "Miezi {n} ijayo"},
}
KEYS = ("tomorrow", "next_week", "next_2_weeks", "next_month", "next_3_months", "rest_of_year", "next_year")


def resolve(key: str, today: date | None = None, n: int = 0):
    t = today or ci.today_local()
    mon = t - timedelta(days=t.weekday())
    if key == "tomorrow":
        return t + timedelta(days=1), t + timedelta(days=1)
    if key == "next_week":
        return mon + timedelta(days=7), mon + timedelta(days=13)
    if key == "next_2_weeks":
        return t + timedelta(days=1), t + timedelta(days=14)
    if key == "next_month":
        first = ci._add_months(t.replace(day=1), 1)
        return first, ci._month_end(first.year, first.month)
    if key == "next_3_months":
        return t + timedelta(days=1), ci._add_months(t, 3)
    if key == "rest_of_year":
        return t + timedelta(days=1), date(t.year, 12, 31)
    if key == "next_year":
        return date(t.year + 1, 1, 1), date(t.year + 1, 12, 31)
    if key == "upcoming":
        return t + timedelta(days=1), t + timedelta(days=30)
    if key == "n_days" and n:
        return t + timedelta(days=1), t + timedelta(days=n)
    if key == "n_weeks" and n:
        return t + timedelta(days=1), t + timedelta(days=7 * n)
    if key == "n_months" and n:
        return t + timedelta(days=1), ci._add_months(t, n)
    raise ValueError(key)


def parse_future(text: str, today: date | None = None):
    """The future period named in the text, or None."""
    q = fold(text)
    if not q:
        return None
    t = today or ci.today_local()
    unit_map = (("days", r"days?|jours?|iminsi|siku"), ("weeks", r"weeks?|semaines?|ibyumweru|wiki|majuma"), ("months", r"months?|mois|amezi|mezi|miezi"))
    for u, rx in unit_map:
        m = re.search(rf"(?:next|coming|prochains?|prochaines?)\s+(\d{{1,2}})\s+(?:{rx})\b|\b(\d{{1,2}})\s+(?:prochains?|prochaines?)\s+(?:{rx})\b|\bin\s+(\d{{1,2}})\s+(?:{rx})\b|\b(?:{rx})\s+(\d{{1,2}})\s+(?:izaza|zijazo|ijayo|ziko imbere|ari imbere|biri imbere|iri imbere)\b", q)
        if m:
            n = int(next(g for g in m.groups() if g))
            if 1 <= n <= 36:
                key = {"days": "n_days", "weeks": "n_weeks", "months": "n_months"}[u]
                s, e = resolve(key, t, n)
                return {"key": key, "n": n, "start": s, "end": e, "future": True}
    for key, rx in _SIMPLE:
        if re.search(rx, q):
            s, e = resolve(key, t)
            return {"key": key, "start": s, "end": e, "future": True}
    return None


def period_from_key(key: str, today: date | None = None):
    s, e = resolve(key, today)
    return {"key": key, "start": s, "end": e, "future": True}


def label(period: dict, lang: str = "en") -> str:
    L = LABELS.get(lang, LABELS["en"])
    if period.get("key") == "custom":
        return f'{period["start"]} – {period["end"]}'
    return L[period["key"]].format(n=period.get("n", ""))


# ---------------------------------------------------------------- recurring calendar (rules, not live data)
def _nth_weekday(y: int, m: int, weekday: int, n: int) -> date:
    d = date(y, m, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(days=7 * (n - 1))


_EV = {
    "patch": ("Microsoft Patch Tuesday: monthly security updates", "Patch Tuesday de Microsoft : mises à jour de sécurité mensuelles", "Patch Tuesday ya Microsoft: ivugurura ry'umutekano ryo buri kwezi", "Patch Tuesday ya Microsoft: masasisho ya usalama ya kila mwezi",
              "Install the updates when they appear; criminals start attacking unpatched systems within days.", "Installez les mises à jour dès leur publication ; les criminels attaquent vite les systèmes non corrigés.",
              "Shyiraho ivugurura rikimara kugaragara; abagizi ba nabi batangira gutera sisitemu zitavuguruwe mu minsi mike.", "Sakinisha masasisho yanapotoka; wahalifu hushambulia mifumo isiyosasishwa ndani ya siku chache.", "https://msrc.microsoft.com/update-guide", ("security",)),
    "oracle": ("Oracle Critical Patch Update (quarterly)", "Mise à jour critique trimestrielle d'Oracle", "Ivugurura rikomeye rya Oracle (buri gihembwe)", "Sasisho Muhimu la Oracle (kila robo mwaka)",
               "Organisations running Oracle products should schedule patching.", "Les organisations utilisant Oracle doivent planifier l'application des correctifs.", "Ibigo bikoresha Oracle bigomba gutegura kuvugurura.", "Mashirika yanayotumia Oracle yapange ratiba ya kusasisha.", "https://www.oracle.com/security-alerts/", ("security",)),
    "sid": ("Safer Internet Day", "Journée pour un Internet plus sûr", "Umunsi wa Interineti itekanye", "Siku ya Mtandao Salama",
            "Awareness campaigns on safe use of the internet, especially for young people.", "Campagnes de sensibilisation à l'usage sûr d'Internet, surtout pour les jeunes.", "Ubukangurambaga ku gukoresha interineti mu mutekano, cyane cyane urubyiruko.", "Kampeni za uhamasishaji kuhusu matumizi salama ya mtandao, hasa kwa vijana.", "https://www.saferinternetday.org", ("awareness",)),
    "dpd": ("Data Privacy Day (28 January)", "Journée de la protection des données (28 janvier)", "Umunsi wo kurinda amakuru bwite (28 Mutarama)", "Siku ya Faragha ya Data (28 Januari)",
            "Awareness about protecting personal data.", "Sensibilisation à la protection des données personnelles.", "Ubukangurambaga ku kurinda amakuru bwite.", "Uhamasishaji kuhusu kulinda taarifa binafsi.", "", ("awareness",)),
    "pwd": ("World Password Day", "Journée mondiale du mot de passe", "Umunsi mpuzamahanga w'ijambo ry'ibanga", "Siku ya Nywila Duniani",
            "A reminder to use long, unique passwords and multi-factor authentication.", "Rappel : mots de passe longs et uniques, et authentification multifacteur.", "Kwibutsa gukoresha amagambo y'ibanga maremare kandi atandukanye no kwemeza mu byiciro byinshi.", "Ukumbusho wa kutumia nywila ndefu, za kipekee na uthibitisho wa hatua nyingi.", "", ("awareness",)),
    "month": ("Cybersecurity Awareness Month (October)", "Mois de la cybersécurité (octobre)", "Ukwezi k'ubukangurambaga ku mutekano wa interineti (Ukwakira)", "Mwezi wa Uhamasishaji wa Usalama wa Mtandao (Oktoba)",
              "A month of awareness activities by governments and organisations.", "Un mois d'activités de sensibilisation par les États et organisations.", "Ukwezi k'ibikorwa by'ubukangurambaga bikorwa na leta n'ibigo.", "Mwezi wa shughuli za uhamasishaji na serikali na mashirika.", "https://www.cisa.gov/cybersecurity-awareness-month", ("awareness",)),
    "csd": ("International Computer Security Day (30 November)", "Journée internationale de la sécurité informatique (30 novembre)", "Umunsi mpuzamahanga w'umutekano wa mudasobwa (30 Ugushyingo)", "Siku ya Kimataifa ya Usalama wa Kompyuta (30 Novemba)",
            "A good day to update devices and back up important files.", "Bon moment pour mettre à jour vos appareils et sauvegarder vos fichiers importants.", "Umunsi mwiza wo kuvugurura ibikoresho no kubika kopi z'amadosiye y'ingenzi.", "Siku nzuri ya kusasisha vifaa na kuhifadhi nakala za faili muhimu.", "", ("awareness",)),
}
_ORDER = {"en": 0, "fr": 1, "rw": 2, "sw": 3}


def calendar_items(start: date, end: date, lang: str = "en"):
    li = _ORDER.get(lang, 0)
    out = []

    def add(key, d):
        if start <= d <= end:
            e = _EV[key]
            out.append({"title": e[li], "url": e[8], "date": d, "summary": e[4 + li], "source": {"patch": "Microsoft", "oracle": "Oracle"}.get(key, "Security calendar"),
                        "kind": "official" if e[8] else "news", "recurring": True, "topics": e[9]})
    for y in range(start.year, end.year + 1):
        for m in range(1, 13):
            add("patch", _nth_weekday(y, m, 1, 2))
            if m in (1, 4, 7, 10):
                add("oracle", _nth_weekday(y, m, 1, 3))
        add("sid", _nth_weekday(y, 2, 1, 2))
        add("dpd", date(y, 1, 28))
        add("pwd", _nth_weekday(y, 5, 3, 1))
        add("csd", date(y, 11, 30))
        for day in (1,):
            add("month", date(y, 10, day))
    return out


# ---------------------------------------------------------------- live: CISA remediation deadlines
def parse_kev_due(data: bytes, start: date, end: date):
    try:
        rows = json.loads(data.decode("utf-8", "replace")).get("vulnerabilities", [])
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            d = date.fromisoformat(r.get("dueDate", ""))
        except Exception:
            continue
        if start <= d <= end and re.fullmatch(r"CVE-\d{4}-\d{3,7}", r.get("cveID", "")):
            what = f'{r.get("vendorProject", "")} {r.get("product", "")}'.strip()
            ran = str(r.get("knownRansomwareCampaignUse", "")).lower() == "known"
            out.append({"title": f'Deadline to fix {r["cveID"]} in {what} (set by CISA for an actively exploited vulnerability)', "url": ci.KEV_PAGE, "date": d,
                        "summary": ci._strip(r.get("shortDescription", "")) + (" Known to be used in ransomware attacks." if ran else ""), "source": "CISA KEV", "kind": "official",
                        "recurring": False, "topics": ("security", "crime") if ran else ("security",)})
    return out


_CACHE: dict = {}


def search(period: dict, topics=None, lang: str = "en", fetch=None, fresh: bool = False, now: float | None = None):
    """{'period','topics','items':{topic:[...]},'total','failed','fetched','live':bool}. fetch(url)->bytes lets tests avoid the network."""
    topics = [t for t in (topics or ci.TOPICS) if t in ci.TOPICS] or list(ci.TOPICS)
    s, e = period["start"], period["end"]
    key = (s, e, tuple(topics), lang)
    t0 = now if now is not None else time.time()
    if fetch is None and not fresh and key in _CACHE and t0 - _CACHE[key][0] < ci.CACHE_SECONDS:
        return _CACHE[key][1]
    items, failed, live = calendar_items(s, e, lang), [], False
    try:
        data = (fetch or ci._http)(ci.KEV_URL)
        items += parse_kev_due(data, s, e)
        live = True
    except Exception:
        failed.append("CISA KEV")
    by = {t: [] for t in topics}
    for it in sorted(items, key=lambda x: x["date"]):
        for t in it["topics"]:
            if t in by:
                by[t].append(it)
    for t in by:
        by[t] = by[t][:40]
    res = {"period": period, "topics": topics, "items": by, "failed": failed, "live": live, "total": sum(len(v) for v in by.values()), "fetched": datetime.now(ci.TZ).strftime("%Y-%m-%d %H:%M")}
    if fetch is None and live:
        _CACHE[key] = (t0, res)
    return res
