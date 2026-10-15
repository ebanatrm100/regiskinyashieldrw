"""Write what the Python detector says about many messages, for tests/parity.js to compare."""
import csv, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from detector import analyze

EXTRA = [
    "", "   ", "😀😀 send your PIN 😀", "VÉRIFIEZ VOTRE COMPTE sur http://203.0.113.9/x immédiatement",
    "Versez 50 000 RWF de frais de visa avant de commencer. Offre d'emploi a Dubai.",
    "ENVOYEZ VOTRE CODE PIN", "Never share your PIN. Send your PIN now.", "Do not delay, send your PIN.",
    "I’ve won ’ quotes ‘ test: you’ve won a prize, pay 5,000 RWF to claim",
    "Umeshinda! Tuma TSh 10,000 ya usafirishaji ili uipate.", "İstanbul ÇÖĞŞ send your password",
    "a" * 3000, "Ntugasangize iyi kode n'undi muntu.", "Hongera, umeshinda nafasi ya kwanza kwenye maonyesho ya sayansi!",
    "Congratulations, you won first prize! Click http://bit.ly/x to claim",
]
texts = []
for split in ("dev", "test"):
    with open(f"data/{split}_messages.csv", encoding="utf-8") as fh:
        texts += [r["text"] for r in csv.DictReader(fh)]
texts += EXTRA
out = []
for t in texts:
    r = analyze(t)
    out.append({
        "text": t, "verdict": r.verdict, "language": r.language,
        "findings": [{"id": f.rule_id, "ev": [[s, e] for s, e, _ in f.evidence]} for f in r.findings],
        "protective": sorted([[s, e] for s, e, _ in r.protective]),
    })
pathlib.Path("results").mkdir(exist_ok=True)
json.dump(out, open("results/parity_python.json", "w", encoding="utf-8"), ensure_ascii=False)
print("dumped", len(out))
