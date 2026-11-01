"""Cyber Intel: current, sourced information about CYBERSECURITY, AWARENESS and CYBERCRIME for a chosen time period.
Pure Python (no Streamlit). Understands time phrases in English, French, Kinyarwanda and Kiswahili ("last week", "la semaine dernière",
"icyumweru gishize", "wiki iliyopita", "last 2 months", "in September", "2025" ...). When a question names no period, the caller asks the user to choose one.

Where the information comes from (nothing is invented; every item is a headline with a link to its publisher):
  * Google News search with a date range, KEPT ONLY WHEN THE PUBLISHER IS ON THE TRUSTED LIST below (official bodies, CERTs, police, security vendors and research, major news agencies)
  * direct RSS/Atom feeds of trusted publishers (CISA, UK NCSC, KrebsOnSecurity, BleepingComputer, The Hacker News, SANS ISC, The Record ...)
  * the CISA Known Exploited Vulnerabilities catalogue (dated additions) and critical CVEs from the NVD (US NIST)
Direct feeds only keep recent items, so for long periods most results come from the dated news search. Everything fails soft: an unreachable source is skipped and listed."""
from __future__ import annotations
import concurrent.futures as cf
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from textutil import fold

UA = "KinyaShieldRW/1.0 (https://regiskinyashieldrw.streamlit.app; cyber awareness; contact via the app)"
TZ = timezone(timedelta(hours=2))          # Africa/Kigali
HTTP_TIMEOUT = 8
TOTAL_TIMEOUT = 12
CACHE_SECONDS = 600
TOPICS = ("security", "awareness", "crime")

# ---------------------------------------------------------------- trusted publishers: domain -> kind (official / research / news)
TRUSTED = {}
for _d in ("cisa.gov us-cert.gov ic3.gov fbi.gov justice.gov ftc.gov nist.gov gov.uk ncsc.gov.uk europol.europa.eu enisa.europa.eu cert.europa.eu interpol.int unodc.org itu.int "
           "ncsa.gov.rw risa.gov.rw police.gov.rw minict.gov.rw bnr.rw gov.rw africacert.org afripol.africa-union.org nca.gov.uk cyber.gov.au cyber.gc.ca cert.fr ssi.gouv.fr").split():
    TRUSTED[_d] = "official"
for _d in ("krebsonsecurity.com bleepingcomputer.com thehackernews.com therecord.media securityweek.com darkreading.com sans.org isc.sans.edu microsoft.com blog.google security.googleblog.com "
           "cloud.google.com mandiant.com talosintelligence.com welivesecurity.com sophos.com malwarebytes.com schneier.com kaspersky.com crowdstrike.com paloaltonetworks.com "
           "unit42.paloaltonetworks.com checkpoint.com research.checkpoint.com proofpoint.com trendmicro.com eset.com cisco.com symantec-enterprise-blogs.security.com").split():
    TRUSTED[_d] = "research"
for _d in ("reuters.com apnews.com bbc.com bbc.co.uk theguardian.com wired.com arstechnica.com aljazeera.com france24.com rfi.fr lemonde.fr newtimes.co.rw ktpress.rw igihe.com "
           "techcabal.com techpoint.africa itweb.co.za scmagazine.com infosecurity-magazine.com cyberscoop.com helpnetsecurity.com").split():
    TRUSTED[_d] = "news"


def trust_kind(url_or_host: str):
    """'official' / 'research' / 'news' when the host (or a parent domain) is on the trusted list, else None."""
    host = urllib.parse.urlparse(url_or_host if "//" in url_or_host else "//" + url_or_host).hostname or ""
    host = host.lower()
    parts = host.split(".")
    for i in range(len(parts) - 1):
        k = TRUSTED.get(".".join(parts[i:]))
        if k:
            return k
    return None


# ---------------------------------------------------------------- time phrases
_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12,
              "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six_": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "douze": 12,
              "moja": 1, "mbili": 2, "miwili": 2, "wawili": 2, "tatu": 3, "tatu_": 3, "nne": 4, "tano": 5, "sita": 6, "saba": 7, "nane": 8, "tisa": 9, "kumi": 10,
              "abiri": 2, "atatu": 3, "ine": 4, "atanu": 5, "rimwe": 1, "kimwe": 1, "umwe": 1}
_UNITS = (("hours", r"hours?|heures?|amasaha|masaa"), ("days", r"days?|jours?|iminsi|siku|munsi"), ("weeks", r"weeks?|semaines?|ibyumweru|cyumweru|wiki|majuma"),
          ("months", r"months?|mois|amezi|mezi|kwezi|miezi|mwezi"), ("years", r"years?|ans?|annees?|imyaka|myaka|umwaka|mwaka|miaka"))
_PAST = r"last|past|previous|dernier|derniers|derniere|dernieres|ashize|ishize|gishize|yashize|iliyopita|zilizopita|zilizopita|uliopita|kwa|mu|muri|ces|les"

_MONTHS = {}
for _i, _names in enumerate(("january janvier mutarama januari", "february fevrier gashyantare februari", "march mars werurwe machi", "april avril mata aprili", "may mai gicurasi mei",
                             "june juin kamena juni", "july juillet nyakanga julai", "august aout kanama agosti", "september septembre nzeri septemba", "october octobre ukwakira oktoba",
                             "november novembre ugushyingo novemba", "december decembre ukuboza desemba"), 1):
    for _n in _names.split():
        _MONTHS[_n] = _i

_SIMPLE = (   # folded-text patterns for fixed periods, most specific first
    ("last_week", r"\b(?:last|previous) week\b|\bsemaine (?:derniere|passee|precedente)\b|\bicyumweru (?:gishize|cyashize)\b|\bwiki (?:iliyopita|uliopita)\b"),
    ("this_week", r"\bthis week\b|\bcette semaine\b|\b(?:muri )?iki cyumweru\b|\bwiki hii\b"),
    ("last_month", r"\b(?:last|previous) month\b|\ble mois (?:dernier|passe|precedent)\b|\bukwezi gushize\b|\bmwezi (?:uliopita|jana)\b"),
    ("this_month", r"\bthis month\b|\bce mois(?:-ci)?\b|\buku kwezi\b|\bmwezi huu\b"),
    ("last_year", r"\b(?:last|previous) year\b|\bl'annee (?:derniere|passee|precedente)\b|\bannee (?:derniere|passee)\b|\bumwaka ushize\b|\bmwaka (?:jana|uliopita)\b"),
    ("this_year", r"\bthis year\b|\bcette annee\b|\buyu mwaka\b|\bmwaka huu\b"),
    ("yesterday", r"\byesterday\b|\bhier\b|\bejo hashize\b|\bejo\b(?! hazaza)|\bjana\b"),
    ("today", r"\btoday\b|\btonight\b|\baujourd'hui\b|\baujourdhui\b|\buyu munsi\b|\bleo\b"),
    ("these_days", r"\bthese days\b|\brecent(?:ly)?\b|\blately\b|\bces derniers jours\b|\bces jours-ci\b|\bces jours\b|\ben ce moment\b|\bmu minsi ishize\b|\bsiku hizi\b|\bsiku za karibuni\b|\bkaribuni\b"),
)

KEYS = ("today", "yesterday", "these_days", "this_week", "last_week", "this_month", "last_month", "last_2_months", "last_3_months", "last_6_months", "this_year", "last_year", "last_2_years")

LABELS = {
    "en": {"today": "Today", "yesterday": "Yesterday", "these_days": "These days (last 7 days)", "this_week": "This week", "last_week": "Last week", "this_month": "This month",
           "last_month": "Last month", "last_2_months": "Last two months", "last_3_months": "Last three months", "last_6_months": "Last six months", "this_year": "This year",
           "last_year": "Last year", "last_2_years": "Last two years", "custom": "Pick my own dates", "n_hours": "Last {n} hours", "n_days": "Last {n} days", "n_weeks": "Last {n} weeks",
           "n_months": "Last {n} months", "n_years": "Last {n} years", "month": "{m} {y}", "year": "Year {y}"},
    "fr": {"today": "Aujourd'hui", "yesterday": "Hier", "these_days": "Ces derniers jours (7 jours)", "this_week": "Cette semaine", "last_week": "La semaine dernière", "this_month": "Ce mois-ci",
           "last_month": "Le mois dernier", "last_2_months": "Les deux derniers mois", "last_3_months": "Les trois derniers mois", "last_6_months": "Les six derniers mois", "this_year": "Cette année",
           "last_year": "L'année dernière", "last_2_years": "Les deux dernières années", "custom": "Choisir mes dates", "n_hours": "Dernières {n} heures", "n_days": "{n} derniers jours",
           "n_weeks": "{n} dernières semaines", "n_months": "{n} derniers mois", "n_years": "{n} dernières années", "month": "{m} {y}", "year": "Année {y}"},
    "rw": {"today": "Uyu munsi", "yesterday": "Ejo hashize", "these_days": "Mu minsi ishize (iminsi 7)", "this_week": "Iki cyumweru", "last_week": "Icyumweru gishize", "this_month": "Uku kwezi",
           "last_month": "Ukwezi gushize", "last_2_months": "Amezi abiri ashize", "last_3_months": "Amezi atatu ashize", "last_6_months": "Amezi atandatu ashize", "this_year": "Uyu mwaka",
           "last_year": "Umwaka ushize", "last_2_years": "Imyaka ibiri ishize", "custom": "Hitamo amatariki yanjye", "n_hours": "Amasaha {n} ashize", "n_days": "Iminsi {n} ishize",
           "n_weeks": "Ibyumweru {n} bishize", "n_months": "Amezi {n} ashize", "n_years": "Imyaka {n} ishize", "month": "{m} {y}", "year": "Umwaka wa {y}"},
    "sw": {"today": "Leo", "yesterday": "Jana", "these_days": "Siku hizi (siku 7)", "this_week": "Wiki hii", "last_week": "Wiki iliyopita", "this_month": "Mwezi huu",
           "last_month": "Mwezi uliopita", "last_2_months": "Miezi miwili iliyopita", "last_3_months": "Miezi mitatu iliyopita", "last_6_months": "Miezi sita iliyopita", "this_year": "Mwaka huu",
           "last_year": "Mwaka uliopita", "last_2_years": "Miaka miwili iliyopita", "custom": "Chagua tarehe zangu", "n_hours": "Saa {n} zilizopita", "n_days": "Siku {n} zilizopita",
           "n_weeks": "Wiki {n} zilizopita", "n_months": "Miezi {n} iliyopita", "n_years": "Miaka {n} iliyopita", "month": "{m} {y}", "year": "Mwaka {y}"},
}
MONTH_NAMES = {"en": "January February March April May June July August September October November December".split(),
               "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
               "rw": "Mutarama Gashyantare Werurwe Mata Gicurasi Kamena Nyakanga Kanama Nzeri Ukwakira Ugushyingo Ukuboza".split(),
               "sw": "Januari Februari Machi Aprili Mei Juni Julai Agosti Septemba Oktoba Novemba Desemba".split()}


def today_local() -> date:
    return datetime.now(TZ).date()


def _add_months(d: date, n: int) -> date:
    m = d.year * 12 + (d.month - 1) + n
    y, mo = divmod(m, 12)
    mo += 1
    day = min(d.day, [31, 29 if (y % 4 == 0 and (y % 100 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1])
    return date(y, mo, day)


def _month_end(y: int, m: int) -> date:
    return _add_months(date(y, m, 1), 1) - timedelta(days=1)


def resolve(key: str, today: date | None = None, n: int | None = None, y: int | None = None, m: int | None = None):
    """(start, end) for a period key. Raises ValueError for an unknown key."""
    t = today or today_local()
    mon = t - timedelta(days=t.weekday())
    if key == "today":
        return t, t
    if key == "yesterday":
        return t - timedelta(days=1), t - timedelta(days=1)
    if key == "these_days":
        return t - timedelta(days=6), t
    if key == "this_week":
        return mon, t
    if key == "last_week":
        return mon - timedelta(days=7), mon - timedelta(days=1)
    if key == "this_month":
        return t.replace(day=1), t
    if key == "last_month":
        first = _add_months(t.replace(day=1), -1)
        return first, _month_end(first.year, first.month)
    if key == "last_2_months":
        return t - timedelta(days=61), t
    if key == "last_3_months":
        return t - timedelta(days=91), t
    if key == "last_6_months":
        return t - timedelta(days=182), t
    if key == "this_year":
        return date(t.year, 1, 1), t
    if key == "last_year":
        return date(t.year - 1, 1, 1), date(t.year - 1, 12, 31)
    if key == "last_2_years":
        return t - timedelta(days=730), t
    if key == "n_hours" and n:
        return t - timedelta(days=max(0, (n - 1) // 24)), t
    if key == "n_days" and n:
        return t - timedelta(days=n - 1), t
    if key == "n_weeks" and n:
        return t - timedelta(days=7 * n), t
    if key == "n_months" and n:
        return _add_months(t, -n), t
    if key == "n_years" and n:
        return _add_months(t, -12 * n), t
    if key == "year" and y:
        return date(y, 1, 1), min(date(y, 12, 31), t)
    if key == "month" and y and m:
        return date(y, m, 1), min(_month_end(y, m), t)
    raise ValueError(key)


def label(period: dict, lang: str = "en") -> str:
    L = LABELS.get(lang, LABELS["en"])
    k = period["key"]
    if k == "month":
        return L["month"].format(m=MONTH_NAMES.get(lang, MONTH_NAMES["en"])[period["m"] - 1], y=period["y"])
    if k == "year":
        return L["year"].format(y=period["y"])
    if k == "custom":
        return f'{period["start"]} – {period["end"]}'
    return L[k].format(n=period.get("n", ""))


def parse_time(text: str, today: date | None = None):
    """The period named in the text as {'key','start','end', ...}, or None when no period is named (the caller must then ask the user)."""
    q = fold(text)
    if not q:
        return None
    t = today or today_local()
    # "last 2 months", "past three weeks", "les 2 derniers mois", "mu mezi 2 ashize", "miezi 2 iliyopita"
    unit_rx = "|".join(f"(?P<{u}>{rx})" for u, rx in _UNITS)
    numw = "|".join(sorted(_NUM_WORDS, key=len, reverse=True))
    for m in re.finditer(rf"(?<![a-z0-9])(?P<n>\d{{1,3}}|{numw})\s+(?:(?:derniers?|dernieres?|last|past)\s+)?(?:{unit_rx})(?![a-z])|(?<![a-z0-9])(?:{unit_rx.replace('?P<', '?P<x')})\s+(?P<n2>\d{{1,3}}|{numw})(?![a-z0-9])", q):
        n_raw = m.group("n") or m.group("n2")
        n = int(n_raw) if n_raw.isdigit() else _NUM_WORDS.get(n_raw)
        unit = next((u for u, _ in _UNITS if m.group(u) or m.groupdict().get("x" + u)), None)
        if not n or not unit or not (1 <= n <= 120):
            continue
        around = q[max(0, m.start() - 14): m.end() + 22]
        if re.search(rf"\b(?:{_PAST})\b", around):
            key = {"hours": "n_hours", "days": "n_days", "weeks": "n_weeks", "months": "n_months", "years": "n_years"}[unit]
            if key == "n_months" and n == 2:
                key = "last_2_months"
            elif key == "n_months" and n == 3:
                key = "last_3_months"
            elif key == "n_months" and n == 6:
                key = "last_6_months"
            elif key == "n_years" and n == 2:
                key = "last_2_years"
            s, e = resolve(key, t, n)
            return {"key": key, "n": n, "start": s, "end": e}
    for key, rx in _SIMPLE:
        if re.search(rx, q):
            s, e = resolve(key, t)
            return {"key": key, "start": s, "end": e}
    # a month name (with an optional year), or a bare year such as 2025
    ym = re.search(r"\b(20[12]\d)\b", q)
    for m in re.finditer(r"\b([a-z]{3,12})\b", q):
        mo = _MONTHS.get(m.group(1))
        if not mo:
            continue
        if m.group(1) == "may" and not (ym or re.search(r"\b(?:in|of|during|since)\s+may\b", q)):
            continue
        y = int(ym.group(1)) if ym else (t.year if mo <= t.month else t.year - 1)
        if date(y, mo, 1) > t:
            continue
        s, e = resolve("month", t, y=y, m=mo)
        return {"key": "month", "y": y, "m": mo, "start": s, "end": e}
    if ym and int(ym.group(1)) <= t.year:
        y = int(ym.group(1))
        s, e = resolve("year", t, y=y)
        return {"key": "year", "y": y, "start": s, "end": e}
    return None


def period_from_key(key: str, today: date | None = None):
    s, e = resolve(key, today)
    return {"key": key, "start": s, "end": e}


def custom_period(start: date, end: date):
    if end < start:
        start, end = end, start
    return {"key": "custom", "start": start, "end": min(end, today_local())}


# ---------------------------------------------------------------- topics and extra search words
_TOPIC_WORDS = {
    "security": r"cyber ?security|cybersecurite|security|securite|data breach\w*|vulnerab\w*|cve\b|patch\w*|breach\w*|data leak\w*|hack\w*|malware|ransomware|zero-?day|exploit\w*|attack\w*|attaque\w*|virus|"
                r"umutekano|ibitero|igitero|shambulio|mashambulizi|usalama|udhaifu|intege nke|ikibazo cy'umutekano|uvujaji wa data|uvujaji|kuvuja|ibura ry'amakuru|ibura ry'ibanga|udukuzi|kudukua|programu hasidi|virusi|ubujura bw'amakuru|wizi wa data|"
                r"rancongiciel\w*|logiciels? malveillants?|piratage|pirates?|fuites? de donnees|faille\w*|vulnerabilite\w*|cyberattaque\w*|menace\w*|threat\w*",
    "awareness": r"awareness|sensibilisation|tips?|conseils?|training|campaign\w*|prevention|education|protect yourself|stay safe|ubukangurambaga|inama|uhamasishaji|vidokezo|elimu|kwirinda|kuririnda|amahugurwa|ubumenyi|formation\w*|bonnes pratiques|campagne\w*|mafunzo|kampeni|jinsi ya kujikinga|ushauri",
    "crime": r"cyber ?crime\w*|cybercriminal\w*|cybercriminalite|fraud\w*|scam\w*|arnaque\w*|arrest\w*|takedown|police|interpol|europol|ransomware|phishing|extortion|theft|"
             r"ibyaha|icyaha|abafashwe|gufatwa|uhalifu|wahalifu|mhalifu|uburiganya|ubujura|ulaghai|utapeli|ubutekamutwe|ukamatwa|kukamatwa|kuboneka|hameconnage|cybercriminel\w*|escroquerie\w*|extorsion|rancon\w*|vol de donnees|usurpation\w*|gendarmerie|justice|tribunal|condamn\w*|wizi|kukamatwa|mahakama|polisi",
}
_STOP = set(("what is are the a an of in on for about and or me please give tell show information info news latest current new updates update related to from with all any every "
             "quelles quels quel sont les des de la le du et ou en sur pour quoi donne moi montre informations nouvelles actualites derniere dernier "
             "ni iki ibihe amakuru yose ku kuri na cyangwa mpa nyereka amakuru "
             "ni nini habari zote za kuhusu na au nipe nionyeshe taarifa mpya ya "
             "ashize ishize gishize yashize iliyopita zilizopita uliopita byo bya cya mu muri interineti internet mtandao mtandaoni online cyber know like ago two three four five six seven eight nine ten "
             "deux trois quatre cinq sept huit neuf dix mois semaines jours annees quelles cette ces derniers dernieres y'ibyaha ibyaha y'amakuru ya'ibyaha wa ya kwa katika ndani "
             "bwa bwo bya byo cya cyo ibya ibyo uku uyu iki iyi izo uko bwa mu muri ukwezi gutaha icyumweru gitaha umwaka utaha ibizaza bizaza bigiye kuza mezi iminsi ibyumweru imyaka "
             "par des les aux au ces cette ce mois prochain prochaine prochains prochaines venir evenements actualite actualites nouvelles ont ete "
             "ibikorwa bakoze bakora yakozwe byakozwe ibikorwa vya ni la wa za kwa kuhusu miezi wiki siku miaka mwezi mwaka huu hii ujao ijayo zijazo yajayo matukio mpya upcoming next coming events event daily today week month year days weeks months years").split())


def parse_topics(text: str):
    q = fold(text)
    return [t for t in TOPICS if re.search(rf"(?<![a-z0-9])(?:{_TOPIC_WORDS[t]})", q)]


_FUTURE_RX = ((0, r"\b(?:next|upcoming|coming|prochain\w*|a venir|ibizaza|bizaza|gutaha|gitaha|utaha|ijayo|ujao|zijazo|yajayo|kesho|tomorrow|demain)\b"),)


def extra_terms(text: str) -> str:
    """Words the user typed that are not about time or the three generic topics (for example 'ransomware', 'Rwanda', 'mobile money'); used to narrow the search."""
    q = fold(text)
    for _k, rx in _SIMPLE:
        q = re.sub(rx, " ", q)
    q = re.sub(r"\b\d{1,3}\s+\w+\s+(?:ago|ashize|iliyopita)\b", " ", q)
    q = re.sub(r"\b(?:last|past|previous|dernier\w*)\b", " ", q)
    q = re.sub(r"\b20[12]\d\b", " ", q)
    q = re.sub(r"(?<![a-z0-9])(?:" + "|".join(_TOPIC_WORDS.values()) + r")(?![a-z0-9])", " ", q)      # whole topic phrases ("fuites de donnees", "programu hasidi")
    for _k, rx in _FUTURE_RX:
        q = re.sub(rx, " ", q)
    toks = [w for w in re.split(r"[^a-z0-9'\-]+", q) if w and len(w) > 2 and w not in _STOP and w not in _MONTHS and not w.isdigit()]
    toks = [w for w in toks if not any(re.fullmatch(rx, w) for _u, rx in _UNITS)]
    toks = [w for w in toks if not re.fullmatch(_TOPIC_WORDS["security"] + "|" + _TOPIC_WORDS["awareness"] + "|" + _TOPIC_WORDS["crime"], w)]
    return " ".join(toks[:5])


_TERM_EN = (   # (folded regex, English search term): the user's own words become English search words for the English-language sources
    (r"rancongiciel\w*|ibyorezo bya ransomware", "ransomware"), (r"hameconnage|ubutekamutwe bwa phishing|ulaghai wa phishing", "phishing"),
    (r"logiciels? malveillants?|programu hasidi|ibyuma byangiza", "malware"), (r"fuites? (?:de )?donnees|uvujaji (?:wa )?data|uvujaji|ibura ry'amakuru|kuvuga amakuru", "data breach"),
    (r"piratage|udukuzi|kudukua|ubujura bwo kuri interineti", "hacking"), (r"arnaques?|ulaghai|uburiganya|utapeli|ubutekamutwe", "scam"),
    (r"fraude|wizi wa mtandaoni|ubujura bw'amafaranga", "fraud"), (r"cybercriminalite|ibyaha bya interineti|ibyaha byo kuri interineti|uhalifu wa mtandaoni|uhalifu wa kimtandao", "cybercrime"),
    (r"cybercriminels|wahalifu wa mtandaoni|abakora ibyaha bya interineti", "cybercriminals"), (r"arrestations?|abafashwe|kukamatwa|ukamatwa", "arrested"),
    (r"pesa (?:za )?simu|amafaranga (?:yo )?(?:kuri )?telefoni|monnaie mobile", "mobile money"), (r"vulnerabilite\w*|udhaifu|intege nke", "vulnerability"),
    (r"deepfake\w*|hypertrucage\w*", "deepfake"), (r"rwanda|u rwanda", "Rwanda"), (r"afrique|afurika|africa", "Africa"), (r"banque|banki", "bank"), (r"mots? de passe|ijambo ry'ibanga|nywila", "password"),
    (r"sextorsion", "sextortion"), (r"usurpation d'identite|kwiba indangamuntu|wizi wa utambulisho", "identity theft"), (r"rancon", "ransom"),
)


def english_terms(extra: str) -> str:
    """The user's extra words as English search words ('rancongiciel Rwanda' -> 'ransomware Rwanda'); words with no known translation are kept (names, product names)."""
    q = fold(extra)
    out = []
    for rx, en in _TERM_EN:
        if re.search(rx, q):
            out.append(en)
            q = re.sub(rx, " ", q)
    rest = [w for w in re.split(r"[^a-z0-9'\-]+", q) if len(w) > 2 and w not in _STOP]
    return " ".join(dict.fromkeys(out + rest[:3]))[:80]


_LOCAL_BASE = {   # topic queries in the user's language, for news published in that language
    "fr": {"security": '(cybersécurité OR "fuite de données" OR vulnérabilité OR rançongiciel OR "logiciel malveillant" OR cyberattaque)',
           "awareness": '("sensibilisation cybersécurité" OR hameçonnage OR "conseils de sécurité" OR "arnaque en ligne")',
           "crime": '(cybercriminalité OR "fraude en ligne" OR cybercriminels OR "arnaque" OR "arrestation" OR "mobile money")'},
    "sw": {"security": '(usalama wa mtandao OR "uvujaji wa data" OR udukuzi OR "programu hasidi" OR ransomware)',
           "awareness": '("uhamasishaji usalama wa mtandao" OR "ulaghai mtandaoni" OR "tahadhari ya ulaghai")',
           "crime": '(uhalifu wa mtandaoni OR "ulaghai wa pesa za simu" OR "wahalifu wa mtandaoni" OR "kukamatwa" OR "ulaghai")'},
    "rw": {"security": '(umutekano wa interineti OR "ibitero bya interineti" OR "amakuru yibwe" OR ransomware)',
           "awareness": '("ubukangurambaga umutekano wa interineti" OR "uburiganya kuri interineti" OR "kwirinda uburiganya")',
           "crime": '(ibyaha byo kuri interineti OR "uburiganya bwa mobile money" OR "abafashwe uburiganya" OR "ubujura bwo kuri interineti")'},
}


# ---------------------------------------------------------------- fetching
def _http(url: str, accept: str = "application/xml, application/rss+xml, text/xml, */*") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:  # noqa: S310 (https URLs fixed in this module)
        return r.read(3_000_000)


def _strip(text: str, n: int = 260) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def _to_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(TZ).date()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_feed(data: bytes):
    """Items of an RSS 2.0 or Atom document: [{'title','url','date','summary','source','source_url'}]. Documents with a DOCTYPE/ENTITY are refused (XML-bomb safety)."""
    head = data[:4000].lower()
    if b"<!doctype" in head or b"<!entity" in head or b"<!entity" in data.lower():
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    out = []
    for el in root.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        f = {}
        for ch in el:
            n = _local(ch.tag)
            if n == "link":
                f["link"] = ch.get("href") or (ch.text or "").strip() if not f.get("link") or ch.get("rel") in (None, "alternate") else f["link"]
            elif n in ("title", "description", "summary", "content", "pubDate", "published", "updated", "date"):
                f.setdefault(n, (ch.text or "").strip())
            elif n == "source":
                f["source"] = (ch.text or "").strip()
                f["source_url"] = ch.get("url", "")
        d = _to_date(f.get("pubDate") or f.get("published") or f.get("updated") or f.get("date") or "")
        title = _strip(f.get("title", ""), 220)
        url = f.get("link", "")
        if title and d and url.startswith(("http://", "https://")):
            out.append({"title": title, "url": url, "date": d, "summary": _strip(f.get("description") or f.get("summary") or f.get("content") or ""),
                        "source": f.get("source", ""), "source_url": f.get("source_url", "")})
    return out


_CRIME = re.compile(r"\b(?:arrest\w*|charged|sentenced|extradit\w*|indict\w*|convicted|takedown|taken down|seiz\w*|dismantl\w*|cybercrim\w*|cybercriminal\w*|fraud\w*|scam\w*|extortion|"
                    r"money laundering|botnet|dark ?web|ransomware gang|arnaque\w*|interpol|europol|police)\b", re.I)
_AWARE = re.compile(r"\b(?:awareness|tips?|how to|guide|guidance|protect(?:ing)? yourself|stay safe|safer|campaign|training|advice|best practices?|learn|education|consumer alert|sensibilisation|conseils)\b", re.I)
_SEC = re.compile(r"\b(?:vulnerabilit\w*|cve-\d|patch\w*|zero-?day|exploit\w*|breach\w*|data leak\w*|malware|ransomware|attack\w*|advisory|backdoor|botnet|phishing|hack\w*|cyber ?security|cyber)\b", re.I)


def classify(item: dict, default: str | None = None):
    """Topics that an item belongs to, from its title and summary (plus the topic it was found under)."""
    txt = item["title"] + " " + item.get("summary", "")
    got = [t for t, rx in (("crime", _CRIME), ("awareness", _AWARE), ("security", _SEC)) if rx.search(txt)]
    if default and default not in got and not got:
        got = [default]
    return got


def _gnews_url(query: str, start: date, end: date, lang: str):
    hl, gl, ceid = {"fr": ("fr", "FR", "FR:fr"), "sw": ("sw", "KE", "KE:sw"), "rw": ("en-RW", "RW", "RW:en")}.get(lang, ("en-US", "US", "US:en"))
    q = f"{query} after:{start.isoformat()} before:{(end + timedelta(days=1)).isoformat()}"
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": hl, "gl": gl, "ceid": ceid})


_BASE_Q = {
    "security": '(cybersecurity OR "data breach" OR vulnerability OR ransomware OR malware OR "cyber attack")',
    "awareness": '("cybersecurity awareness" OR "phishing awareness" OR "online safety" OR "scam alert" OR "security tips")',
    "crime": '(cybercrime OR "cyber fraud" OR "online fraud" OR "cybercriminals arrested" OR "ransomware arrest" OR "mobile money fraud")',
}
_OFFICIAL_Q = "(site:interpol.int OR site:europol.europa.eu OR site:fbi.gov OR site:justice.gov OR site:ic3.gov OR site:ftc.gov OR site:cisa.gov OR site:ncsc.gov.uk OR site:enisa.europa.eu OR site:ncsa.gov.rw OR site:risa.gov.rw OR site:police.gov.rw)"
_LOCAL_Q = "(Rwanda OR Africa OR Kigali OR Kenya OR Nigeria) (cybersecurity OR cybercrime OR \"cyber fraud\" OR \"mobile money\" OR ransomware)"

FEEDS = (  # (name, url, kind, default topics)
    ("CISA advisories", "https://www.cisa.gov/cybersecurity-advisories/all.xml", "official", ("security",)),
    ("UK NCSC", "https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml", "official", ("security", "awareness")),
    ("KrebsOnSecurity", "https://krebsonsecurity.com/feed/", "research", ("crime", "security")),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/", "research", ("security", "crime")),
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews", "research", ("security", "crime")),
    ("SANS Internet Storm Center", "https://isc.sans.edu/rssfeed.xml", "research", ("security",)),
    ("The Record", "https://therecord.media/feed", "news", ("crime", "security")),
    ("SecurityWeek", "https://feeds.feedburner.com/securityweek", "research", ("security",)),
    ("Dark Reading", "https://www.darkreading.com/rss.xml", "research", ("security",)),
    ("Microsoft Security blog", "https://www.microsoft.com/en-us/security/blog/feed/", "research", ("security", "awareness")),
    ("Google Security blog", "https://security.googleblog.com/feeds/posts/default", "research", ("security", "awareness")),
    ("WeLiveSecurity (ESET)", "https://www.welivesecurity.com/en/feed/", "research", ("security", "awareness")),
)
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_PAGE = "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"


def parse_kev(data: bytes, start: date, end: date):
    try:
        rows = json.loads(data.decode("utf-8", "replace")).get("vulnerabilities", [])
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            d = date.fromisoformat(r.get("dateAdded", ""))
        except Exception:
            continue
        if start <= d <= end and re.fullmatch(r"CVE-\d{4}-\d{3,7}", r.get("cveID", "")):
            what = f'{r.get("vendorProject", "")} {r.get("product", "")}'.strip()
            out.append({"title": f'Actively exploited: {r["cveID"]} in {what} (added to the CISA Known Exploited Vulnerabilities catalogue)', "url": KEV_PAGE, "date": d,
                        "summary": _strip(r.get("shortDescription", "")) + (" Known to be used in ransomware attacks." if str(r.get("knownRansomwareCampaignUse", "")).lower() == "known" else ""),
                        "source": "CISA KEV", "source_url": "https://www.cisa.gov"})
    return out


def parse_nvd(data: bytes):
    try:
        rows = json.loads(data.decode("utf-8", "replace")).get("vulnerabilities", [])
    except Exception:
        return []
    out = []
    for r in rows:
        c = r.get("cve", {})
        cid = c.get("id", "")
        d = _to_date(c.get("published", ""))
        desc = next((x.get("value", "") for x in c.get("descriptions", []) if x.get("lang") == "en"), "")
        if re.fullmatch(r"CVE-\d{4}-\d{3,7}", cid) and d:
            out.append({"title": f"Critical vulnerability published: {cid}", "url": "https://nvd.nist.gov/vuln/detail/" + cid, "date": d, "summary": _strip(desc),
                        "source": "NIST NVD", "source_url": "https://nvd.nist.gov"})
    return out


def _nvd_url(start: date, end: date):
    s = max(start, end - timedelta(days=119))        # the NVD accepts at most 120 days per request
    return ("https://services.nvd.nist.gov/rest/json/cves/2.0?" + urllib.parse.urlencode({
        "pubStartDate": f"{s.isoformat()}T00:00:00.000", "pubEndDate": f"{end.isoformat()}T23:59:59.999", "cvssV3Severity": "CRITICAL", "resultsPerPage": 15}))


def _norm(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", fold(re.sub(r"\s+-\s+[^-]{2,40}$", "", title))).strip()[:90]


def _clean_gn_title(title: str, source: str) -> str:
    if source and title.endswith(" - " + source):
        return title[: -(len(source) + 3)].strip()
    return re.sub(r"\s+-\s+[^-]{2,40}$", "", title).strip()


def build_jobs(period: dict, topics, lang: str, extra: str):
    """The list of (name, kind, default_topics, fetch_function) to run. Pure; no network until the functions are called."""
    s, e = period["start"], period["end"]
    jobs = []
    ex_native = extra.strip()
    ex = english_terms(ex_native) if lang != "en" and ex_native else ex_native      # English-language sources get English search words
    for tp in topics:
        q = (f'"{ex}" ' if ex else "") + _BASE_Q[tp]
        if lang == "en":
            jobs.append((f"news:{tp}", "news", (tp,), lambda q=q: ("gn", _http(_gnews_url(q, s, e, "en")))))
        else:
            ql = (f'"{ex_native}" ' if ex_native else "") + _LOCAL_BASE[lang][tp]      # and news published in the user's own language
            jobs.append((f"news:{tp}", "news", (tp,), lambda q=ql: ("gn", _http(_gnews_url(q, s, e, lang)))))
            jobs.append((f"news-en:{tp}", "news", (tp,), lambda q=q: ("gn", _http(_gnews_url(q, s, e, "en")))))
    off = (f'"{ex}" ' if ex else "") + _OFFICIAL_Q
    jobs.append(("official", "official", tuple(topics), lambda: ("gn", _http(_gnews_url(off, s, e, "en")))))
    loc = (f'"{ex}" ' if ex else "") + _LOCAL_Q
    jobs.append(("local", "news", tuple(topics), lambda: ("gn", _http(_gnews_url(loc, s, e, "en" if lang in ("en", "rw") else lang)))))
    days_ago = (today_local() - s).days
    if days_ago <= 90 or (e - s).days <= 90:
        for name, url, kind, tps in FEEDS:
            if set(tps) & set(topics):
                jobs.append((name, kind, tps, lambda url=url: ("feed", _http(url))))
    if "security" in topics:
        jobs.append(("CISA KEV", "official", ("security",), lambda: ("kev", _http(KEV_URL, "application/json"))))
        jobs.append(("NIST NVD", "official", ("security",), lambda: ("nvd", _http(_nvd_url(s, e), "application/json"))))
    return jobs


_CACHE: dict = {}


def search(period: dict, topics=None, lang: str = "en", text: str = "", fetch_jobs=None, now: float | None = None):
    """Look-up with the user's extra words; when that finds nothing, repeat without them (extra words in a translated question can be too narrow)."""
    res = _search(period, topics, lang, text, fetch_jobs, now)
    if not res["total"] and extra_terms(text) and fetch_jobs is None:
        res = dict(_search(period, topics, lang, "", None, now), extra_dropped=extra_terms(text))
    return res


def _search(period: dict, topics=None, lang: str = "en", text: str = "", fetch_jobs=None, now: float | None = None):
    """Run the look-up. Returns {'period','topics','items':{topic:[item,...]},'sources':[(name,kind,count)],'failed':[name],'total':int,'fetched':str}.
    fetch_jobs lets tests supply jobs without a network. Results are cached for 10 minutes."""
    topics = [t for t in (topics or TOPICS) if t in TOPICS] or list(TOPICS)
    extra = extra_terms(text)
    extra_en = english_terms(extra) if (extra and lang != "en") else extra
    s, e = period["start"], period["end"]
    key = (s, e, tuple(topics), lang, extra)
    t0 = now if now is not None else time.time()
    hit = _CACHE.get(key)
    if hit and t0 - hit[0] < CACHE_SECONDS and fetch_jobs is None:
        return hit[1]
    jobs = fetch_jobs if fetch_jobs is not None else build_jobs(period, topics, lang, extra)
    results, failed = [], []
    ex = cf.ThreadPoolExecutor(max_workers=14)
    futs = {ex.submit(fn): (name, kind, tps) for name, kind, tps, fn in jobs}
    done, pending = cf.wait(futs, timeout=TOTAL_TIMEOUT)
    for f in pending:
        failed.append(futs[f][0])
        f.cancel()
    ex.shutdown(wait=False, cancel_futures=True)
    seen, by_topic, counts = set(), {t: [] for t in topics}, {}
    for f in done:
        name, kind, tps = futs[f]
        try:
            what, data = f.result()
            if what == "kev":
                items = parse_kev(data, s, e)
            elif what == "nvd":
                items = parse_nvd(data)
            else:
                items = parse_feed(data)
        except Exception:
            failed.append(name)
            continue
        added = 0
        for it in items:
            if not (s <= it["date"] <= e):
                continue
            src_url = it.get("source_url") or it["url"]
            k = trust_kind(src_url) if what == "gn" else (kind if what != "feed" else (trust_kind(it["url"]) or kind))
            if what == "gn":
                it["title"] = _clean_gn_title(it["title"], it.get("source", ""))
                it["summary"] = ""
            if not k:
                continue
            if extra and what == "feed" and not re.search(re.escape((extra_en or extra).split()[0]), it["title"] + " " + it["summary"], re.I):
                continue                      # direct feeds are not searched by the news engine, so apply the extra words here
            n = _norm(it["title"])
            if not n or n in seen:
                continue
            tt = [t for t in classify(it, None) if t in topics]
            if not tt:
                if what == "feed" and len(tps) > 1:
                    continue                    # a general security feed item that matches no topic keyword is not clearly on-topic
                tt = [t for t in tps if t in topics][:1]
            it = dict(it, kind=k, source=it.get("source") or name)
            if what == "gn" and "official" == name:
                it["kind"] = k
            seen.add(n)
            added += 1
            for t in tt[:2]:
                by_topic[t].append(it)
        counts[name] = (kind, added)
    for t in by_topic:
        by_topic[t].sort(key=lambda x: (x["date"], x["kind"] == "official"), reverse=True)
        by_topic[t] = by_topic[t][:20]
    res = {"period": period, "topics": topics, "items": by_topic, "failed": sorted(set(failed)), "total": sum(len(v) for v in by_topic.values()),
           "sources": sorted([(n, k, c) for n, (k, c) in counts.items() if c], key=lambda x: -x[2]), "fetched": datetime.now(TZ).strftime("%Y-%m-%d %H:%M")}
    if fetch_jobs is None and res["total"]:
        _CACHE[key] = (t0, res)
    return res
