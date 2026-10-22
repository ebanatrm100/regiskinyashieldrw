"""Translation used around an English-only model (translate the question to English, answer, translate back).
Pure Python. Providers (secret TRANSLATOR):
  "hf"   a Hugging Face translation model behind the Inference API or an Inference Endpoint. Secrets: TRANSLATOR_URL (full URL of the model endpoint),
         TRANSLATOR_API_KEY (HF token), optional. Meant for NLLB-style models: language codes eng_Latn, fra_Latn, kin_Latn, swh_Latn.
  "llm"  the configured chat model translates (works with any OpenAI-compatible server; quality follows the model).
Everything returns None on failure so the caller can fall back. Not tested against live servers from the build sandbox: run `python -m eval.eval_translation` against yours."""
from __future__ import annotations
import settings
import llm_backend

NLLB = {"en": "eng_Latn", "fr": "fra_Latn", "rw": "kin_Latn", "sw": "swh_Latn"}
NAME = {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Kiswahili"}


def provider() -> str:
    t = settings.get("TRANSLATOR").lower()
    if t in {"hf", "llm"}:
        return t
    return ""


def available() -> bool:
    p = provider()
    return bool(p == "hf" and settings.get("TRANSLATOR_URL")) or bool(p == "llm" and llm_backend.provider() == "openai")


def _hf(text: str, src: str, tgt: str):
    url = settings.get("TRANSLATOR_URL")
    llm_backend.validate_base_url(url)
    data = llm_backend._post(url, {"inputs": text, "parameters": {"src_lang": NLLB[src], "tgt_lang": NLLB[tgt]}}, settings.get("TRANSLATOR_API_KEY"), timeout=60)
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return (data[0].get("translation_text") or "").strip() or None
    return None


def _llm(text: str, src: str, tgt: str):
    system = (f"You are a careful translator. Translate the user's text from {NAME[src]} to {NAME[tgt]} for natural meaning and polite register, not word for word. "
              "Keep names, numbers, amounts and formatting. Output only the translation, nothing else.")
    out = llm_backend.openai_chat(system, [], text, temperature=0.1, max_tokens=1500, history_limit=0)
    return out.strip() or None


def translate(text: str, src: str, tgt: str):
    """Translated text or None. src and tgt are 'en', 'fr', 'rw' or 'sw'."""
    if not text or src == tgt or src not in NLLB or tgt not in NLLB:
        return text if src == tgt else None
    try:
        p = provider()
        if p == "hf":
            return _hf(text, src, tgt)
        if p == "llm":
            return _llm(text, src, tgt)
    except Exception:
        return None
    return None
