"""Routing evaluation + human-review sheet.
  python -I eval/run_eval.py            offline: checks which route each prompt takes (no model needed)
  python -I eval/run_eval.py --live     also asks the model (needs GEMINI_API_KEY or LLM_BASE_URL) and fills the Model Response column
Writes eval/results/review_sheet.csv with columns for a human to fill:
  Prompt | Language | Expected Intent | Route | Model Response | Correct (Y/N) | Fluency (1-5) | Comments"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import assistant_flow


def load(path=None):
    with open(path or os.path.join(HERE, "prompts.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def route_eval(rows):
    ok, bad, out = 0, [], []
    for r in rows:
        res = assistant_flow.route(r["prompt"], r["language"])
        got = res["kind"]
        out.append((r, res))
        if r["expected_kind"] == "any" or got == r["expected_kind"]:
            ok += 1
        else:
            bad.append((r["prompt"], r["expected_kind"], got))
    return ok, bad, out


def offline_text(res):
    if res["kind"] == "guide":
        return str(res.get("text") or res.get("answer") or res.get("entry", {}).get("title", ""))[:600]
    if res["kind"] == "scam":
        return "SCAM WARNING: " + str(getattr(res["result"], "verdict", ""))
    return ""


def live_answer(r):
    import assistant_engine, llm_backend   # needs streamlit + a provider; only used with --live
    names = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}
    return assistant_engine.ask(r["prompt"], language_name=names[r["language"]], language_code=r["language"])


def main():
    rows = load()
    ok, bad, out = route_eval(rows)
    print(f"route match: {ok}/{len(rows)}")
    for b in bad:
        print("  MISMATCH:", b)
    live = "--live" in sys.argv
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", "review_sheet.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Prompt", "Language", "Expected Intent", "Route", "Model Response", "Correct (Y/N)", "Fluency (1-5)", "Comments"])
        for r, res in out:
            resp = offline_text(res)
            if live and res["kind"] == "ai":
                try:
                    resp = live_answer(r)
                except Exception as e:
                    resp = f"[error: {type(e).__name__}]"
            w.writerow([r["prompt"], r["language"], r["intent"], res["kind"], resp, "", "", ""])
    print("review sheet ->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
