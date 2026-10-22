import os, sys, csv, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "eval")); sys.path.insert(0, os.path.join(ROOT, "training"))
import metrics, eval_translation, run_eval, build_dataset


def test_metrics():
    assert metrics.bleu("the cat sat on the mat", "the cat sat on the mat") > 99
    assert metrics.chrf("Uri uwa nde?", "Uri uwa nde?") > 99
    assert metrics.chrf("zzzz", "Uri uwa nde?") < 10
    assert metrics.bleu("", "x") == 0.0
    assert metrics.bleu("a b c d e", "a b c d e") > metrics.bleu("a b x d e", "a b c d e")


def test_translation_eval_detects_failures():
    r = eval_translation.evaluate(lambda t, s, g: None, limit=5)
    assert all(v["failed"] == 5 and v["chrf"] == 0 for v in r.values())
    good = eval_translation.evaluate(eval_translation._bank_fn, limit=20)
    assert all(v["chrf"] > 90 for v in good.values())


def test_prompts_route():
    rows = run_eval.load()
    assert len(rows) >= 60 and {"en", "fr", "rw", "sw"} <= {r["language"] for r in rows}
    ok, bad, _ = run_eval.route_eval(rows)
    assert not bad, bad


def test_dataset():
    train, val = build_dataset.build()
    assert len(train) > 3000 and val
    r = train[0]
    assert [m["role"] for m in r["messages"]] == ["user", "assistant"] and r["messages"][1]["content"].strip()
    assert any("Uri uwa nde" in t["messages"][1]["content"] for t in train + val)


if __name__ == "__main__":
    test_metrics(); test_translation_eval_detects_failures(); test_prompts_route(); test_dataset(); print("eval ok")
