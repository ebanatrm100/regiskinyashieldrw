"""The same request must work in English, French, Kinyarwanda and Kiswahili (behaviour parity, not only data)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import detector, image_gen as G
from assistant_flow import route
SCAMS = {"fr": ["Vous avez gagné 5 millions ! Envoyez d'abord 10000 pour payer les frais afin de recevoir votre prix sur MoMo", "Félicitations vous avez gagné un prix, payez de petits frais pour le recevoir"],
         "rw": ["Watsinze miliyoni 5! Ohereza 10000 ubanze wishyure kugira ngo wakire igihembo cyawe kuri MoMo", "Wahawe igihembo, ishyura amafaranga make kugira ngo ugihabwe"],
         "sw": ["Umeshinda milioni 5! Tuma 10000 kwanza kulipa ada ili upokee zawadi yako kwenye MoMo"],
         "en": ["You won 5 million! Send 10000 first to pay the fee to receive your prize on MoMo"]}
for l, ts in SCAMS.items():
    for t in ts:
        r = detector.analyze(t)
        assert r.verdict == "high" and "advance_fee" in [f.rule_id for f in r.findings], (l, t, r.verdict)
for l, t in [("fr", "Bonjour, on se voit demain pour le déjeuner"), ("rw", "Mwiriwe neza, turabashimira uyu munsi"), ("sw", "Habari, tunaonana kesho kwa chakula"), ("en", "Hi, see you tomorrow for lunch")]:
    assert detector.analyze(t).verdict == "ok", (l, t)
LOG = {"en": "how do i analyze a log file", "fr": "comment analyser un fichier journal log", "rw": "nasesengura dosiye ya log nte", "sw": "nachambuaje faili la log"}
for l, q in LOG.items():
    r = route(q, l, history=[]); assert r["kind"] == "guide" and r["entry"]["id"] == "log_analyzer_help", (l, r["kind"])
assert route("what is a blog", "en", history=[])["kind"] != "guide" or route("what is a blog", "en", history=[])["entry"]["id"] != "log_analyzer_help"
ATT = {"en": "types of cyber attacks", "fr": "types de cyberattaques", "rw": "ubwoko bw'ibitero bya cyber", "sw": "aina za mashambulizi ya mtandao"}
for l, q in ATT.items():
    r = route(q, l, history=[]); assert r["kind"] == "guide" and r["entry"]["id"] == "cyb_attack_types", (l, r["kind"])
IMG = {"en": ["draw a pastor in a church", "make a picture of Kigali at night"], "fr": ["dessine un pasteur dans une église", "fais-moi une photo de Kigali la nuit"],
       "rw": ["shushanya umupasiteri mu itorero", "kora ifoto ya Kigali nijoro"], "sw": ["chora mchungaji kanisani", "tengeneza picha ya Kigali usiku"]}
for l, qs in IMG.items():
    for q in qs:
        assert G.parse_request(q), (l, q)
print("OK parity behaviour")
