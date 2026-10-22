# 90-day open-source assistant plan: what is built, what is not

Status key: **DONE** in the repo and tested · **READY** code/template exists, needs your resources · **NOT POSSIBLE HERE** needs people, GPUs or paid services.

| Item from the plan | Status | Where |
|---|---|---|
| Serve open LLMs (vLLM / llama.cpp / Ollama) behind the app | DONE (provider switch, mock-server tested; not tested against a real model) | `llm_backend.py`, `docs/OPEN_MODEL_GUIDE.md` |
| Translation pivot (NLLB/MbazaNLP style) | DONE in code, tested with mocks; live NLLB endpoint untested | `translator.py`, `open_model.py` |
| Hand-written translation bank (en/fr/rw/sw) | DONE (379 rows; rw/sw are drafts for native review) | `translation_bank.py` |
| Auto-detect language | DONE (word-list detector, toggle in the UI) | `langdetect_lite.py` |
| Writing help, tutoring, document Q&A, phrasebook, multilingual UI | DONE (earlier work) | `writing_db.py`, `tutor_db.py`, `docs_assistant.py`, `ui_strings.py` |
| Privacy | PARTLY: offline answers stay local; Gemini/Wikipedia/translator calls send text out | `docs/OPEN_MODEL_GUIDE.md` §5 |
| Fair-use counters (freemium groundwork) | DONE: per-session counters and optional limit | `usage.py` |
| Accounts, login, billing, paid tiers | NOT BUILT: needs an auth provider and payment processor | – |
| Evaluation: BLEU/chrF | DONE (dependency-free; use sacrebleu for publishable numbers) | `eval/metrics.py`, `eval/eval_translation.py` |
| 100–200 bilingual prompts | PARTLY: 71 prompts (route checks) so far | `eval/prompts.csv` |
| Human rubric sheet | DONE (sheet generated; humans must fill it) | `eval/results/review_sheet.csv` |
| Human testers / native-speaker review | NOT POSSIBLE HERE | – |
| LoRA fine-tuning | READY: dataset builder (5,389 seed examples) + template; **not run, no GPU** | `training/` |
| Model hosting on a GPU | NOT POSSIBLE HERE (Streamlit Cloud cannot host it) | guide §1 |
| Speech (ASR/TTS) | NOT BUILT (optional in the plan) | – |

Corrections to the plan: BLOOM is under the RAIL licence (not Apache-2.0); NLLB-derived weights may be non-commercial; "no external APIs" is not true while Gemini or Wikipedia lookups are enabled.
