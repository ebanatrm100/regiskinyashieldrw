"""Answering with an OpenAI-compatible server (vLLM, llama.cpp, Ollama ...), with the optional translation pivot. No Streamlit, no extra packages."""
from __future__ import annotations
import llm_backend as _llm
import settings as _settings
import translator as _translator

_BACK_FAILED = {
    "rw": "Ntabashije guhindura iki gisubizo mu Kinyarwanda; dore mu Cyongereza.",
    "fr": "Je n'ai pas pu traduire cette réponse en français ; la voici en anglais.",
    "sw": "Sikuweza kutafsiri jibu hili kwa Kiswahili; hili hapa kwa Kiingereza.",
}
_NO_SEARCH = "\n\n_Web search is only available with Gemini, so this answer is not based on live sources. Check important facts with an official source._"


def answer(system, history, question, language_name, language_code, use_search):
    """Answer with an OpenAI-compatible server (vLLM, llama.cpp, Ollama ...). With LLM_ENGLISH_ONLY=true and a translator configured, questions in
    Kinyarwanda, French or Kiswahili go: translate to English -> model -> translate back (falls back to the English answer, and says so)."""
    note = _NO_SEARCH if use_search else ""
    code = language_code if language_code in _translator.NAME else None
    if _settings.flag("LLM_ENGLISH_ONLY") and code and code != "en" and _translator.available():
        q_en = _translator.translate(question, code, "en")
        if q_en:
            hist_en = []
            for m in list(history)[-4:]:
                text = str(m.get("content", "")).strip()
                if m.get("role") in {"user", "assistant"} and text:
                    t_en = _translator.translate(text[:1500], code, "en")
                    if t_en:
                        hist_en.append({"role": m["role"], "content": t_en})
            sys_en = system.replace(f"Answer in {language_name} throughout", "Answer in English throughout", 1) + \
                f"\n\nThe user's message was machine-translated from {language_name}; if it reads oddly, answer the most likely meaning."
            ans_en = _llm.openai_chat(sys_en, hist_en, q_en)
            back = _translator.translate(ans_en, "en", code)
            if back:
                return back + note
            return ans_en + "\n\n_" + _BACK_FAILED.get(code, "") + "_" + note
    return _llm.openai_chat(system, history, question) + note


