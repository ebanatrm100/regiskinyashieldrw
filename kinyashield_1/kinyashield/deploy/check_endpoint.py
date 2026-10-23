"""Checks that your model server is reachable and answers, using the SAME settings the app reads (env vars or .streamlit/secrets.toml).
    python -I deploy/check_endpoint.py
Prints OK/FAIL per step and never prints keys."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import llm_backend as L, translator as T


def run():
    ok = True
    p = L.provider()
    print("provider:", p or "(none set)")
    if p != "openai":
        print("FAIL: set LLM_BASE_URL (and LLM_PROVIDER=openai) first. See docs/OPEN_MODEL_GUIDE.md"); return 1
    t = time.time()
    try:
        a = L.openai_chat("Answer in one short sentence.", [], "Say hello.", max_tokens=40)
        print(f"OK chat answered in {time.time() - t:.1f}s: {a[:80]!r}")
    except L.LLMError as e:
        print("FAIL chat:", e); ok = False
    if T.available():
        r = T.translate("Hello, how are you?", "en", "rw")
        print("OK translator:" if r else "FAIL translator returned nothing", (r or "")[:80])
        ok = ok and bool(r)
    else:
        print("translator: not configured (fine if the model handles your languages itself)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
