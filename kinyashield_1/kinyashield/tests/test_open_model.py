"""Open-model backend, translation pivot and language detection, tested against a local mock server (no network, no GPU)."""
import json, os, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import settings, llm_backend as L, translator as T, open_model as OM, langdetect_lite as D

SEEN = []


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append((self.path, self.headers.get("Authorization"), body))
        if self.path.endswith("/chat/completions"):
            msgs = body["messages"]
            last, sysm = msgs[-1]["content"], msgs[0]["content"]
            if "careful translator" in sysm:            # the model acting as translator
                tgt = "Kinyarwanda" if "to Kinyarwanda" in sysm else "English"
                out = ("EN:" if tgt == "English" else "RW:") + last
            elif last == "FAIL":
                self.send_response(500); self.end_headers(); return
            else:
                out = "ANSWER(" + last + ")"
            data = {"choices": [{"message": {"content": "<think>x</think>" + out}}]}
        else:                                           # hf translation endpoint
            p = body["parameters"]
            data = [{"translation_text": f"{p['src_lang']}>{p['tgt_lang']}:{body['inputs']}"}]
        raw = json.dumps(data).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)


def _server():
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def _env(**kw):
    for k in ("LLM_PROVIDER", "LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY", "LLM_ENGLISH_ONLY", "TRANSLATOR", "TRANSLATOR_URL", "TRANSLATOR_API_KEY", "GEMINI_API_KEY"):
        os.environ.pop(k, None)
    os.environ.update({k: v for k, v in kw.items()})


def test_provider_selection():
    _env(); assert L.provider() == ""
    _env(GEMINI_API_KEY="k"); assert L.provider() == "gemini"
    _env(LLM_BASE_URL="http://localhost:8000/v1"); assert L.provider() == "openai"
    _env(GEMINI_API_KEY="k", LLM_PROVIDER="vllm", LLM_BASE_URL="http://localhost:8000/v1"); assert L.provider() == "openai"
    _env(GEMINI_API_KEY="k", LLM_PROVIDER="gemini"); assert L.provider() == "gemini"


def test_base_url_is_validated():
    for bad in ["", "ftp://x/v1", "http://example.com/v1", "javascript:alert(1)", "https:///v1"]:
        try:
            L.validate_base_url(bad); raise AssertionError(bad)
        except L.LLMError:
            pass
    assert L.validate_base_url("https://my.server/v1/") == "https://my.server/v1"
    assert L.validate_base_url("http://localhost:8000/v1") == "http://localhost:8000/v1"


def test_chat_roundtrip_history_and_errors():
    srv, url = _server()
    _env(LLM_BASE_URL=url + "/v1", LLM_MODEL="m", LLM_API_KEY="secret-token")
    SEEN.clear()
    out = L.openai_chat("SYS", [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}, {"role": "tool", "content": "x"}], "hello")
    assert out == "ANSWER(hello)"                                   # <think> block removed
    path, auth, body = SEEN[-1]
    assert path == "/v1/chat/completions" and auth == "Bearer secret-token" and body["model"] == "m"
    assert [m["role"] for m in body["messages"]] == ["system", "user", "assistant", "user"]
    try:
        L.openai_chat("SYS", [], "FAIL"); raise AssertionError
    except L.LLMError as e:
        assert "500" in str(e) and "secret-token" not in str(e)
    _env(LLM_BASE_URL=url + "/v1")
    try:
        L.openai_chat("SYS", [], "x"); raise AssertionError                # no model configured
    except L.LLMError:
        pass
    srv.shutdown()


def test_translation_pivot_with_llm_translator():
    srv, url = _server()
    _env(LLM_BASE_URL=url + "/v1", LLM_MODEL="m", LLM_ENGLISH_ONLY="true", TRANSLATOR="llm")
    system = "Answer in Kinyarwanda throughout."
    out = OM.answer(system, [{"role": "user", "content": "mbere"}], "Ni iki firewall?", "Kinyarwanda", "rw", False)
    assert out == "RW:ANSWER(EN:Ni iki firewall?)"                  # question -> English -> model -> back to Kinyarwanda
    out = OM.answer("Answer in English throughout.", [], "What is a firewall?", "English", "en", True)
    assert out.startswith("ANSWER(What is a firewall?)") and "Web search is only available with Gemini" in out
    _env(LLM_BASE_URL=url + "/v1", LLM_MODEL="m")                    # English-only flag off: asked directly
    assert OM.answer(system, [], "Ni iki firewall?", "Kinyarwanda", "rw", False) == "ANSWER(Ni iki firewall?)"
    srv.shutdown()


def test_translator_hf_endpoint_and_fallbacks():
    srv, url = _server()
    _env(TRANSLATOR="hf", TRANSLATOR_URL=url + "/model", TRANSLATOR_API_KEY="t")
    assert T.available() and T.translate("hello", "en", "rw") == "eng_Latn>kin_Latn:hello"
    assert T.translate("x", "en", "xx") is None and T.translate("same", "en", "en") == "same"
    _env(TRANSLATOR="hf", TRANSLATOR_URL="http://example.com/model")   # insecure URL: refused, returns None instead of sending
    assert T.translate("hello", "en", "rw") is None
    _env(); assert not T.available() and T.translate("hello", "en", "rw") is None
    srv.shutdown()


def test_language_detection():
    for text, want in [("What is a firewall?", "en"), ("comment choisir un mot de passe", "fr"), ("Ndashaka kumenya icyo firewall ni", "rw"), ("Naomba msaada kuhusu akaunti yangu", "sw"),
                       ("traduis who is your owner en kinyarwanda", "fr"), ("tafsiri hello kwa kinyarwanda", "sw"), ("hindura hello mu gifaransa", "rw")]:
        assert D.detect_confident(text) == want, text
    for text in ["firewall", "password", "ni", "12345", ""]:
        assert D.detect_confident(text) is None, text


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("open model ok")
