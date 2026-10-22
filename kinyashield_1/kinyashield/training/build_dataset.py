"""Builds instruction-tuning data (JSONL, chat format) from the hand-written content already in this repo:
translation bank, cybersecurity glossary, and scam guidance. Output: training/out/train.jsonl and val.jsonl.
    python -I training/build_dataset.py
Every record is {"messages":[{"role":"user",...},{"role":"assistant",...}], "lang":..., "source":...}.
This is a SEED set (a few thousand rows at most) for LoRA tuning of an open model; it is not enough on its own to teach a
base model a language. Rows in Kinyarwanda/Kiswahili are drafts that need fluent-speaker review before training."""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import translation_bank as tb
import cyber_db

L = ["en", "fr", "rw", "sw"]
NAME = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}
ASK = {"en": "Translate '{t}' into {n}.", "fr": "Traduis « {t} » en {n}.", "rw": "Humura '{t}' mu {n}.", "sw": "Tafsiri '{t}' kwa {n}."}
WHAT = {"en": "What is {t}?", "fr": "Qu'est-ce que {t} ?", "rw": "{t} ni iki?", "sw": "{t} ni nini?"}


def rec(lang, user, answer, source):
    return {"messages": [{"role": "user", "content": user}, {"role": "assistant", "content": answer}], "lang": lang, "source": source}


def translation_rows():
    for row in tb.BANK:
        alts = [c.split(" / ") for c in row[:4]]
        for i, s in enumerate(L):
            for j, t in enumerate(L):
                if i != j:
                    yield rec(s, ASK[s].format(t=alts[i][0].strip(), n=NAME[t]), alts[j][0].strip(), "translation_bank")


def cyber_rows():
    # TERMS row layout: id, en name, aliases, category, photo, {fr,sw,rw names}, en meaning, en use, fr meaning, fr use, rw meaning, rw use, sw meaning, sw use
    for r in cyber_db.TERMS:
        names = {"en": r[1], **r[5]}
        for k, mi in (("en", 6), ("fr", 8), ("rw", 10), ("sw", 12)):
            yield rec(k, WHAT[k].format(t=names[k]), f"{r[mi]} {r[mi + 1]}", "cyber_glossary")


def build(seed=7, val_share=0.05):
    rows = list(translation_rows()) + list(cyber_rows())
    random.Random(seed).shuffle(rows)
    n = max(1, int(len(rows) * val_share))
    return rows[n:], rows[:n]


def main():
    train, val = build()
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    for name, data in (("train.jsonl", train), ("val.jsonl", val)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            for r in data:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"train {len(train)}  val {len(val)}  -> {out}")


if __name__ == "__main__":
    main()
