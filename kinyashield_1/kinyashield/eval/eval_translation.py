"""Score any translator against the hand-written translation bank (BLEU / chrF per direction).
    python -I eval/eval_translation.py            -> scores the built-in bank (should be ~100: it is the reference)
    python -I eval/eval_translation.py --live     -> scores translator.translate() (NLLB / LLM) when TRANSLATOR is configured
The first alternative of each bank row is the reference."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import metrics
import translation_bank as tb

LANGS = ("en", "fr", "rw", "sw")


def pairs():
    rows = []
    for row in tb.BANK:
        first = [c.split(" / ")[0].strip() for c in row[:4]]
        rows.append(dict(zip(LANGS, first)))
    return rows


def evaluate(fn, rows=None, limit=None):
    """fn(text, src, tgt) -> str|None. Returns {(src,tgt): {bleu, chrf, n, failed}}."""
    rows = (rows or pairs())[:limit]
    out = {}
    for s in LANGS:
        for t in LANGS:
            if s == t:
                continue
            hyps, refs, failed = [], [], 0
            for r in rows:
                h = fn(r[s], s, t)
                if not h:
                    failed += 1; h = ""
                hyps.append(h); refs.append(r[t])
            res = metrics.corpus(hyps, refs); res["failed"] = failed
            out[(s, t)] = res
    return out


def _bank_fn(text, src, tgt):
    for r in pairs():
        if r[src] == text:
            return r[tgt]
    return None


def main():
    live = "--live" in sys.argv
    if live:
        import translator
        if not translator.available():
            print("No translator configured (set TRANSLATOR / TRANSLATOR_URL). Nothing to score."); return 1
        fn, limit = translator.translate, 50
    else:
        fn, limit = _bank_fn, None
    print(f"{'pair':8}{'BLEU':>8}{'chrF':>8}{'n':>6}{'failed':>8}")
    for (s, t), r in evaluate(fn, limit=limit).items():
        print(f"{s}->{t:5}{r['bleu']:8.1f}{r['chrf']:8.1f}{r['n']:6}{r['failed']:8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
