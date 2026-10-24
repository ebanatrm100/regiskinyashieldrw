# Question Answering and Research Guide: coverage

Source: "How an AI Assistant Understands, Researches, and Answers" (owner's document). Offline, English / French / Kinyarwanda / Kiswahili (fr/rw/sw are drafts for fluent review).

| Guide section | In the assistant |
|---|---|
| 1 Big picture, 2 language model, 3 training | already in `ai_guide_db` (ai_big_picture, ai_tokens … ai_training) |
| 4 Interpreting a question | qa_interpret + tool `interpret: …` |
| 5 External research | qa_research + tool `research plan: …` |
| 6 RAG | qa_rag + tool `rag demo: question ||| passage ||| passage` |
| 7 Tool use | qa_tool_calls |
| 8 Composing answers | qa_compose |
| 9 Safety, privacy, reliability | qa_safety (includes prompt-injection rule) |
| 10 Why AI makes mistakes | qa_mistakes |
| 11 Current-question example | qa_example |
| 12 What is not publicly knowable | qa_unknowable |
| 13 Beginner path | qa_learning_path |
| 14 Glossary | RAG, retrieval, tool call, language model, transformer, pretraining added; the rest exist in ai_guide_db |
| 15 Further reading, Final principle | qa_reading, qa_final |

The system prompt (`assistant_engine.py`) also carries the answering/research rules, so the online AI follows them in all four languages.
Limits: the tools are keyword-rule teaching aids; they do not search the web or judge truth.
