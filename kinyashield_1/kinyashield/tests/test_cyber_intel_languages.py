"""The Cyber News tab must understand the same question in English, French, Kinyarwanda and Kiswahili: same period, same topic, no stray search words."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from datetime import date
import cyber_intel as ci, cyber_upcoming as cu
T = date(2026, 11, 1)
ROWS = [  # (period key, topics, en, fr, rw, sw)
    ("last_week", {"security"}, "ransomware attacks last week", "attaques de rançongiciel la semaine dernière", "ibitero bya ransomware icyumweru gishize", "mashambulizi ya ransomware wiki iliyopita"),
    ("yesterday", {"crime"}, "phishing scams yesterday", "arnaques par hameçonnage hier", "uburiganya bwa phishing ejo hashize", "ulaghai wa phishing jana"),
    ("this_month", {"security"}, "data breaches this month", "fuites de données ce mois-ci", "uvujaji wa data uku kwezi", "uvujaji wa data mwezi huu"),
    ("last_2_months", {"crime"}, "cybercrime arrests last 2 months", "arrestations de cybercriminels les 2 derniers mois", "abafashwe bakoze ibyaha bya interineti mu mezi 2 ashize", "kukamatwa kwa wahalifu wa mtandaoni miezi 2 iliyopita"),
    ("year", {"crime"}, "mobile money fraud in 2025", "fraude mobile money en 2025", "uburiganya bwa mobile money mu 2025", "ulaghai wa pesa za simu mwaka 2025"),
    ("today", {"awareness"}, "cybersecurity awareness tips today", "conseils de sensibilisation aujourd'hui", "inama z'ubukangurambaga uyu munsi", "vidokezo vya uhamasishaji leo"),
    ("these_days", {"security"}, "hacking news these days", "piratage ces derniers jours", "udukuzi mu minsi ishize", "udukuzi siku hizi"),
    ("last_year", {"crime"}, "scams last year", "arnaques l'année dernière", "uburiganya umwaka ushize", "ulaghai mwaka uliopita"),
    ("this_week", {"security"}, "malware this week", "logiciels malveillants cette semaine", "malware iki cyumweru", "programu hasidi wiki hii"),
]
bad = []
for key, topics, *qs in ROWS:
    for lang, q in zip(("en", "fr", "rw", "sw"), qs):
        p = ci.parse_time(q, T)
        if not p or p["key"] != key:
            bad.append((lang, q, "period", p and p["key"]))
        tp = set(ci.parse_topics(q))
        if not (topics & tp):
            bad.append((lang, q, "topic", tp))
        ex = ci.extra_terms(q)
        if ex and ex not in ("mobile money", "pesa simu"):
            bad.append((lang, q, "extra", ex))
FUT = [("next_week", "what is coming next week", "ce qui arrive la semaine prochaine", "ibizaza icyumweru gitaha", "yajayo wiki ijayo"),
       ("next_month", "upcoming events next month", "événements à venir le mois prochain", "ibizaza ukwezi gutaha", "matukio yajayo mwezi ujao"),
       ("tomorrow", "what happens tomorrow", "que se passe-t-il demain", "ibizaba ejo hazaza", "kinachotokea kesho")]
for key, *qs in FUT:
    for lang, q in zip(("en", "fr", "rw", "sw"), qs):
        p = cu.parse_future(q, T)
        if not p or p["key"] != key:
            bad.append((lang, q, "future", p and p["key"]))
assert not bad, bad
# the English-language sources get English search words, the local-language sources get the user's words
assert ci.english_terms("rancongiciel Rwanda") == "ransomware Rwanda" and ci.english_terms("hameçonnage") == "phishing" and ci.english_terms("udukuzi") == "hacking"
jobs = ci.build_jobs({"start": date(2026, 10, 1), "end": T}, ["security"], "fr", "rançongiciel")
names = [j[0] for j in jobs]
assert "news:security" in names and "news-en:security" in names and "official" in names
print("OK cyber intel languages")
