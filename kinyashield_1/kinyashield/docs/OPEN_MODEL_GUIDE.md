# Using a free / open-source model with KinyaShield RW

The app keeps Gemini as the default. Nothing changes unless you add the settings below (Streamlit Cloud → Settings → Secrets, or environment variables). Never put keys in the repo.

## 1. Run an open model on your own server
Streamlit Community Cloud cannot run a 4B+ model. Run the model elsewhere and point the app at it. Any OpenAI-compatible server works:

| Server | Command (example) |
|---|---|
| vLLM (GPU) | `vllm serve <hf-model-id> --port 8000` |
| llama.cpp (CPU or small GPU, GGUF files) | `llama-server -m model.gguf --port 8080` |
| Ollama | `ollama serve` then `ollama pull <model>` |

Use HTTPS in front of it (e.g. a reverse proxy) when it is not on the same machine. The app refuses plain `http://` except for localhost.

## 2. Secrets
```
LLM_PROVIDER = "openai"                 # also accepts vllm, llamacpp, ollama, sglang, tgi
LLM_BASE_URL = "https://your-server/v1"
LLM_MODEL    = "<model name the server exposes>"
LLM_API_KEY  = "<token, if your server requires one>"
LLM_ENGLISH_ONLY = "1"                  # model answers English only -> use the translation pivot (see below)
TRANSLATOR = "hf"                       # or "llm"; with TRANSLATOR_URL / TRANSLATOR_API_KEY
AI_MESSAGES_PER_SESSION = "30"          # optional fair-use limit per browser session (0 = unlimited)
```
With no `LLM_PROVIDER`, the app uses Gemini if `GEMINI_API_KEY` is set, otherwise the open model if `LLM_BASE_URL` is set.

## 3. Translation pivot (English-only models)
When `LLM_ENGLISH_ONLY=1` and the user writes in French / Kinyarwanda / Kiswahili: translate to English → ask the model → translate back (NLLB codes `eng_Latn fra_Latn kin_Latn swh_Latn`). If a translation step fails, the user gets an honest notice rather than a made-up answer. Quick everyday phrases come from the hand-written bank and never need a model.

## 4. Check before you commit to a model
- **Licences differ and matter** (Apache-2.0, MIT, Llama community licence, RAIL, non-commercial NLLB-derived weights). Read each model card; do not assume "open" means "free for commercial use".
- A **base** model cannot chat until it is instruction-tuned (see `training/`).
- Kinyarwanda/Kiswahili quality varies a lot by model; measure with `eval/` before trusting it.
- Hardware rule of thumb: 4B model in 4-bit ≈ 3–4 GB VRAM; 12B ≈ 8–10 GB; CPU-only works for small GGUF models but slowly.

## 5. Privacy
Only the local/offline answers stay inside the app. Gemini, Wikipedia/Wiktionary lookups and any translation service you configure receive the text of the question. Say so honestly to users; do not claim "fully local" unless you run everything yourself.

## 6. One-command setup (files in `deploy/`)
1. `cp deploy/env.example .env` and fill in `MODEL_ID` and a long random `MODEL_API_KEY`.
2. GPU: `docker compose -f deploy/docker-compose.vllm.yml up -d` · CPU: `docker compose -f deploy/docker-compose.llamacpp.yml up -d`.
3. Put HTTPS in front, copy `deploy/secrets.example.toml` into Streamlit Secrets with your real values.
4. Verify: `python -I deploy/check_endpoint.py`, then `python -I eval/run_eval.py --live`.
