"""Export everything the browser version needs to web/rules.json.
Python (safety_rules.py, ui_strings.py) stays the single source of truth."""
import csv, json, pathlib
from safety_rules import (RULES, PROTECTIVE_PREFIX, GENERAL_ADVICE, LANG_MARKERS, VERDICTS,
                          NO_GUARANTEE, LANGS, LANG_NAMES)
from ui_strings import UI
from trusted_sources import SOURCES, NOTE

def examples(per_lang_susp=4, per_lang_legit=3):
    out = {l: [] for l in LANGS}
    with open("data/dev_messages.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for l in LANGS:
        s = [r["text"] for r in rows if r["language"] == l and r["label"] == "suspicious"][:per_lang_susp]
        g = [r["text"] for r in rows if r["language"] == l and r["label"] == "legitimate"][:per_lang_legit]
        out[l] = [{"text": t, "kind": "suspicious"} for t in s] + [{"text": t, "kind": "legitimate"} for t in g]
    return out

def build():
    data = dict(rules=RULES, protective=PROTECTIVE_PREFIX, general=GENERAL_ADVICE, markers=LANG_MARKERS,
                verdicts=VERDICTS, noGuarantee=NO_GUARANTEE, langs=LANGS, langNames=LANG_NAMES, ui=UI,
                sources=SOURCES, sourcesNote=NOTE, examples=examples(), version="0.3.0-mvp")
    pathlib.Path("web").mkdir(exist_ok=True)
    with open("web/rules.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    return data

if __name__ == "__main__":
    d = build()
    print("exported", len(d["rules"]), "rules,", sum(len(v) for v in d["examples"].values()), "examples")
