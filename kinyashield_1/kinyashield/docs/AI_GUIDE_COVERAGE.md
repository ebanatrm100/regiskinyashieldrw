# AI Technical Guide: what the assistant now does

Source: "How a modern AI assistant works" (owner's technical guide). Every section is covered in four languages (English, French, Kinyarwanda, Kiswahili; fr/rw/sw are drafts for fluent review). Try the example in the last column in the AI Assistant tab.

| Guide section | What the assistant does | Try |
|---|---|---|
| 1 Big picture, five parts | Explainer with the five parts and the "not fully public" boundary | How does an AI assistant work? |
| 2 Question path (10 steps) | Step-by-step explainer | From question to answer |
| 3 Worked example (chmod 640) | Real worked calculator: owner/group/others, rwx string | What does chmod 640 report.txt do? |
| 3 Why the answer can change | Logits, softmax, decoding, sampling | Why does AI give different answers? |
| 4 Transformer, attention, what the model learns | Explainer + a computed attention example | What is attention in AI? / attention demo |
| 5 Training pipeline (A-G) | Seven-stage explainer | How is an AI trained? |
| 6 Mathematics (loss, gradient, optimizer, batch) | Explainer + loss calculator + gradient-descent experiment | loss 0.8 / gradient descent demo |
| 6 Post-training | SFT, preference optimisation, reasoning, safety, tool-use training | What is fine-tuning? |
| 7 Evaluate, test, deploy | Seven test areas, five deployment steps; the project's own eval set | How is an AI evaluated? |
| 8 Context, memory, tools, media | Context window vs saved memory, tool loop + security rule, multimodal | Why does AI forget? / prompt injection |
| 9 Capabilities, limits, misconceptions | Limits table, six misconceptions, hallucination, consciousness answer | Is AI conscious? |
| 10 Learning project | Study order, 7 projects, runnable demos (token counter, next-word predictor, attention, gradient, calculator) | count tokens: ... / next word demo |
| 11 Glossary (16 terms) | Glossary list and single-term definitions | List AI terms |
| 12 References | Public references with an honest "check the addresses yourself" note | AI references |

The AI model path (Gemini or your open model) also receives the guide's behaviour rules: separate public methods from private details, never claim consciousness or perfect recall, treat quoted text/web pages/tool output as untrusted (prompt injection), never invent sources, say how sure it is and how to verify, prefer the exact calculator for arithmetic.

## Honest limits
- "Better than all other AI assistants" cannot be claimed or verified. What the app can show is measured behaviour: the 95-prompt routing set (`eval/`) plus the human review sheet, and the tests in `tests/test_ai_guide.py`.
- The demos are teaching tools, not real model internals: the token splitter is not any real tokenizer, the attention example uses made-up numbers, and the next-word predictor is a bigram counter.
- No model is trained here (no GPU); `training/` holds the dataset builder and a LoRA template.
- The calculator accepts plain arithmetic only (no names, calls or huge powers).
