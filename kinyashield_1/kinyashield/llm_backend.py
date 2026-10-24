"""Choose where the AI answers come from. Pure Python (no Streamlit, no extra packages): works with Gemini (the default) or ANY server that speaks the
OpenAI chat-completions API, which is what vLLM (`vllm serve MODEL`), llama.cpp (`llama-server`), Ollama, SGLang and Hugging Face TGI/Inference Endpoints all offer.
That lets the project run on free open-source models (for example AfriqueGemma, Mistral, Dolly) that YOU host, without changing any app code.

Secrets / environment variables (set in Streamlit Community Cloud > App settings > Secrets):
  LLM_PROVIDER      "gemini" or "openai" (any OpenAI-compatible server). If empty: "gemini" when GEMINI_API_KEY exists, else "openai" when LLM_BASE_URL exists.
  LLM_BASE_URL      for example https://my-server.example.com/v1   (http is only accepted for localhost)
  LLM_MODEL         the model name the server expects, for example mistralai/Mistral-7B-Instruct-v0.3
  LLM_API_KEY       optional bearer token for your server
  LLM_ENGLISH_ONLY  "true" if the model is English-only: Kinyarwanda, French and Kiswahili questions are translated to English first and the answer is translated back
  TRANSLATOR        "hf" (a Hugging Face translation endpoint) or "llm" (the same model); see translator.py
Web search is a Gemini feature and is not available with an OpenAI-compatible server."""
from __future__ import annotations
import json
import re
import urllib.error
import urllib.request
from urllib.parse import urlparse

import settings

TIMEOUT = 90


class LLMError(RuntimeError):
    """The model server failed or returned something unusable. The message never contains secrets."""


def provider() -> str:
    """'gemini', 'openai' or '' (nothing configured)."""
    p = settings.get("LLM_PROVIDER").lower()
    if p in {"openai", "vllm", "llamacpp", "llama.cpp", "ollama", "sglang", "tgi", "openai-compatible"}:
        return "openai"
    if p == "gemini":
        return "gemini"
    if settings.get("GEMINI_API_KEY"):
        return "gemini"
    if settings.get("LLM_BASE_URL"):
        return "openai"
    return ""


def validate_base_url(url: str) -> str:
    """https, or http only for the same machine. Returns the URL without a trailing slash."""
    u = urlparse((url or "").strip())
    if u.scheme not in {"http", "https"} or not u.hostname:
        raise LLMError("LLM_BASE_URL must look like https://host/v1")
    if u.scheme == "http" and u.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise LLMError("LLM_BASE_URL must use https (http is only accepted for localhost)")
    return (url or "").strip().rstrip("/")


def _post(url: str, payload: dict, api_key: str = "", timeout: int = TIMEOUT) -> dict:
    headers = {"Content-Type": "application/json", "User-Agent": "KinyaShieldRW/1.0"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (scheme checked by validate_base_url)
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raise LLMError(f"The model server answered with HTTP {e.code}.") from None
    except Exception as e:
        raise LLMError(f"The model server could not be reached ({e.__class__.__name__}).") from None


def openai_chat(system: str, history, question: str, temperature: float = 0.4, max_tokens: int = 1800, history_limit: int = 12,
                base_url: str = "", model_name: str = "", key: str = "") -> str:
    """One chat completion from the configured OpenAI-compatible server (or from the explicit base_url/model_name/key given)."""
    base = validate_base_url(base_url or settings.get("LLM_BASE_URL"))
    model = model_name or settings.get("LLM_MODEL")
    if not model:
        raise LLMError("LLM_MODEL is not configured.")
    messages = [{"role": "system", "content": system}]
    for item in list(history or [])[-history_limit:]:
        role, content = item.get("role"), str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})
    data = _post(base + "/chat/completions", {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
                 key or settings.get("LLM_API_KEY"))
    try:
        text = (data["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        raise LLMError("The model server returned an unexpected response.") from None
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()   # some reasoning models print their notes
    if not text:
        raise LLMError("The model returned an empty answer.")
    return text


# ---- backup services: free-tier keys the owner can add in Secrets; each is tried in order when the main AI fails.
PRESETS = [  # (secret name, base url, default model, model secret name)
    ("GROQ_API_KEY", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", "GROQ_MODEL"),
    ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", "meta-llama/llama-3.3-70b-instruct:free", "OPENROUTER_MODEL"),
    ("MISTRAL_API_KEY", "https://api.mistral.ai/v1", "mistral-small-latest", "MISTRAL_MODEL"),
    ("TOGETHER_API_KEY", "https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo", "TOGETHER_MODEL"),
]


def backups():
    """[(label, base_url, model, key)] for every backup service whose key is present in Secrets."""
    out = []
    for name, base, model, mname in PRESETS:
        k = settings.get(name)
        if k:
            out.append((name.split("_")[0].title(), base, settings.get(mname) or model, k))
    return out


def backup_chat(system, history, question):
    """Try each backup service in turn; returns (label, text) or raises LLMError listing which ones failed (no secrets)."""
    errs = []
    for label, base, model, key in backups():
        try:
            return label, openai_chat(system, history, question, base_url=base, model_name=model, key=key)
        except Exception as e:
            errs.append(f"{label}: {str(e)[:80]}")
    raise LLMError("No backup AI service answered. " + "; ".join(errs) if errs else "No backup AI service is configured.")
