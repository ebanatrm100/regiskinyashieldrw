"""Warm-up: once per server process (this module stays loaded between Streamlit reruns), in a background thread, load the big guides and compile their patterns
so the first question of the first visitor is as fast as the later ones."""
import threading

_STARTED = False


def _run():
    try:
        import assistant_flow as af
        for q in ("hello", "what is phishing", "types of cyber attacks", "mbinu za ulaghai"):
            af.route(q, "en", history=[])
        import cyber_intel, cyber_upcoming, log_analyzer, image_director  # noqa: F401
    except Exception:
        pass


def start() -> bool:
    global _STARTED
    if _STARTED:
        return False
    _STARTED = True
    threading.Thread(target=_run, daemon=True).start()
    return True
