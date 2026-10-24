"""Backups: Gemini keys/models are tried in turn, then backup services (Groq/OpenRouter/...); the 'not available' message only appears when nothing is configured."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for k in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "LLM_PROVIDER", "LLM_BASE_URL", "GROQ_API_KEY", "OPENROUTER_API_KEY", "MISTRAL_API_KEY", "TOGETHER_API_KEY"):
    os.environ.pop(k, None)

# streamlit / google-genai are not installable in the sandbox: minimal stand-ins so assistant_engine can be imported
if "streamlit" not in sys.modules:
    try:
        import streamlit  # noqa
    except Exception:
        st = types.ModuleType("streamlit"); st.secrets = {}; sys.modules["streamlit"] = st
        g = types.ModuleType("google"); ge = types.ModuleType("google.genai"); ge.types = types.ModuleType("google.genai.types")
        ge.Client = lambda **k: None; g.genai = ge
        sys.modules.update({"google": g, "google.genai": ge, "google.genai.types": ge.types})
import llm_backend as B


def test_backups_listed_from_secrets():
    assert B.backups() == []
    os.environ["GROQ_API_KEY"] = "x"; os.environ["OPENROUTER_API_KEY"] = "y"
    b = B.backups()
    assert [x[0] for x in b] == ["Groq", "Openrouter"] and b[0][1].startswith("https://api.groq.com")
    del os.environ["GROQ_API_KEY"]; del os.environ["OPENROUTER_API_KEY"]


def test_backup_chat_tries_in_order_and_reports_failures():
    calls = []
    orig = B.openai_chat
    def fake(system, history, question, **kw):
        calls.append(kw["base_url"])
        if "groq" in kw["base_url"]:
            raise B.LLMError("The model server answered with HTTP 429.")
        return "hello"
    B.openai_chat = fake
    try:
        os.environ["GROQ_API_KEY"] = "x"; os.environ["OPENROUTER_API_KEY"] = "y"
        label, text = B.backup_chat("s", [], "q")
        assert label == "Openrouter" and text == "hello" and len(calls) == 2
        B.openai_chat = lambda *a, **k: (_ for _ in ()).throw(B.LLMError("down"))
        try:
            B.backup_chat("s", [], "q"); assert False
        except B.LLMError as e:
            assert "Groq" in str(e) and "y" not in str(e).replace("Openrouter", "").replace("down", "").replace("Groq", "")
    finally:
        B.openai_chat = orig
        os.environ.pop("GROQ_API_KEY", None); os.environ.pop("OPENROUTER_API_KEY", None)


def test_no_services_gives_missing_key_error():
    import assistant_engine as E
    try:
        E.answer_question("hi", [], "English")
        assert False
    except E.MissingAPIKeyError as e:
        assert "GROQ_API_KEY" in str(e)


def test_backup_only_configuration_answers():
    import assistant_engine as E
    os.environ["GROQ_API_KEY"] = "x"
    orig = B.openai_chat
    B.openai_chat = lambda *a, **k: "backup answer"
    try:
        assert E.answer_question("hi", [], "English") == "backup answer"
    finally:
        B.openai_chat = orig
        os.environ.pop("GROQ_API_KEY", None)


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("ai fallback OK", n)
