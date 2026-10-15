# KinyaShield RW (MVP)

Paste a suspicious message. KinyaShield shows which exact words are risky, why, and what to do next, in **English, Français, Kinyarwanda and Kiswahili**. It uses written rules you can read, not a hidden model. It is a decision aid and cannot prove a message is safe.

## Open it in any browser
Open `web/index.html` (double-click it, or host it: see `docs/DEPLOY.md`). Nothing to install; works offline once loaded; the message never leaves the page.

## Developer commands
```
python check_all.py                      # compile, validate every pattern, check all 4 languages are complete
python -m unittest discover -s tests     # 19 tests
python evaluate.py dev                   # 153 messages, rules were tuned on these
python evaluate.py test                  # blind set: now used once, see docs/EVALUATION.md
python tests/dump_parity.py && python build_web.py && node tests/parity.js
streamlit run app.py                     # optional Python/Streamlit version
```

## Files
| File | Purpose |
|---|---|
| `safety_rules.py` | All rules, patterns (accent-free ASCII) and advice in 4 languages. Edit this to change behaviour. |
| `ui_strings.py` | Interface text in 4 languages |
| `detector.py` / `web/detector.js` | Same detector in Python and JavaScript (parity-tested) |
| `build_web.py`, `export_rules.py` | Build `web/index.html` from the rules |
| `web/index.html` | The complete browser app (single file) |
| `app.py`, `ui_html.py` | Streamlit version |
| `data/` | `dev_messages.csv`, `test_messages.csv`, `archive/` |
| `docs/` | `EVALUATION.md`, `DEPLOY.md`, `MVP_STATUS.md`, reviewer sheets `review_*.csv`, screenshots |

## Honest status
Blind test round 1: 79.7% accuracy, 88% precision, 68.8% recall on 64 fictional messages. French, Kinyarwanda and Kiswahili wording are drafts awaiting fluent reviewers. No real messages, users or official reporting contacts are included yet. See `docs/EVALUATION.md` and `docs/MVP_STATUS.md`.

## Ask tab (added in 0.3.1)
- `knowledge_base.py`: 27 original answers in en/fr/rw/sw (written for this project, nothing copied). `web/ask.js` does keyword retrieval and says "no reliable answer" instead of guessing.
- Optional "Claude AI" mode appears only inside claude.ai (via the `sample` capability); it needs the viewer's consent, can be wrong, and is absent in the standalone file.
- Tests: `node tests/ask_test.js`. fr/rw/sw guide text is a draft until fluent speakers review it.

## Deploying the Streamlit app
- Main file path in Streamlit Cloud: `kinyashield_1/kinyashield/app.py`.
- Add `GEMINI_API_KEY = "..."` in the app's Secrets (never in code). Without it, the AI chat shows "not configured"; the checker and the offline safety guide still work.
- Browser-only version (no server, works offline): `kinyashield_1/index.html`.
