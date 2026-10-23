import os, sys, io, contextlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deploy"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_open_model as M, check_endpoint as C


def test_check():
    for k in ("LLM_PROVIDER", "LLM_BASE_URL", "GEMINI_API_KEY", "TRANSLATOR", "TRANSLATOR_URL"):
        os.environ.pop(k, None)
    with contextlib.redirect_stdout(io.StringIO()):
        assert C.run() == 1                       # nothing configured -> clear failure, no crash
    srv, url = M._server()
    os.environ.update(LLM_PROVIDER="openai", LLM_BASE_URL=url, LLM_MODEL="m", LLM_API_KEY="SECRETKEY")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert C.run() == 0
    assert "OK chat" in buf.getvalue() and "SECRETKEY" not in buf.getvalue()
    srv.shutdown()


if __name__ == "__main__":
    test_check(); print("deploy ok")
