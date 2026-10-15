"""Evaluate the detector on a labelled CSV.
  python evaluate.py dev      (data/dev_messages.csv: used while tuning rules)
  python evaluate.py test     (data/test_messages.csv: held out, do NOT tune on it)
Prediction 'suspicious' = any verdict other than 'No known warning signs detected'.
"""
import csv, json, sys, pathlib
from detector import analyze

def run(split):
    path = pathlib.Path("data") / f"{split}_messages.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out, tp = [], dict(tp=0, tn=0, fp=0, fn=0)
    by_lang = {}
    for r in rows:
        res = analyze(r["text"])
        pred = "suspicious" if res.predicted_suspicious else "legitimate"
        ok = pred == r["label"]
        key = ("tp" if pred == "suspicious" else "tn") if ok else ("fp" if pred == "suspicious" else "fn")
        tp[key] += 1
        bl = by_lang.setdefault(r["language"], dict(tp=0, tn=0, fp=0, fn=0)); bl[key] += 1
        out.append(dict(id=r["id"], label=r["label"], pred=pred, verdict=res.label, ok=ok,
                        category=r["category"], language=r["language"],
                        rules=[f.rule_id for f in res.findings], text=r["text"]))
    return out, tp, by_lang

def metrics(c):
    n = sum(c.values()); p = c["tp"]+c["fp"]; a = c["tp"]+c["fn"]
    return dict(n=n, accuracy=round((c["tp"]+c["tn"])/n, 3) if n else None,
                precision=round(c["tp"]/p, 3) if p else None, recall=round(c["tp"]/a, 3) if a else None, **c)

if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    out, c, bl = run(split)
    summary = dict(split=split, overall=metrics(c), by_language={k: metrics(v) for k, v in bl.items()})
    print(json.dumps(summary, indent=1))
    miss = [o for o in out if not o["ok"]]
    print(f"\n{len(miss)} wrong of {len(out)}:")
    for o in miss:
        print(f"- {o['id']} [{o['language']}/{o['category']}] label={o['label']} got='{o['verdict']}' rules={o['rules']}\n    {o['text']}")
    pathlib.Path("results").mkdir(exist_ok=True)
    json.dump(dict(summary=summary, items=out), open(f"results/{split}_results.json", "w"), indent=1, ensure_ascii=False)
