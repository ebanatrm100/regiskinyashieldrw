# Evaluation: what the numbers mean

All messages are short, fictional, and written by the project owner with Claude's help. None is a real message. The rules were also written by the same people, so every figure below is optimistic.

| Set | Size | Role | Result |
|---|---|---|---|
| `data/dev_messages.csv` | 153 (en, fr, rw, sw) | Used while writing rules | 100%. Proves nothing: the rules were fitted to it. |
| `data/test_messages.csv` (round 1, before any fix) | 64 (16 per language) | Blind test, run once | **79.7% accuracy, 88% precision, 68.8% recall, 3 false alarms, 10 missed** |
| Same 64 after general fixes | 64 | Not independent | 93.8%. Do not quote as evidence. |
| `data/archive/test_v1_seen_and_tuned_on.csv` | 65 | Earlier test, partly seen, one fix made after seeing it | Moved into dev |

Round 1 by language: English 68.8%, French 81.2%, Kinyarwanda 87.5%, Kiswahili 81.2% (16 messages each, so one message is 6 points).

## What round 1 showed
- The 3 false alarms were genuine congratulations ("you won first prize in the school science fair"). Fixed by reading achievement wording in the same sentence, unless money, a link or a "claim/pay/click" word is also there.
- Misses were new wordings (accidental transfer, gift-card requests, romance/419 stories, "guaranteed" returns) and messages that sound normal. A rule list will always have this ceiling.
- Still missed after the fixes: an "I am a soldier abroad" story, a "guaranteed" crypto offer, "accidentally sent" with a normal tone, and an official-sounding tax request in Kinyarwanda.

## Your earlier numbers
10 of 10 on the original sample and 2 of 11 on the challenge set came from your own files, which were never available here, so they were not re-run.

## How to get real evidence
1. Collect real messages people received (with permission, names and numbers removed). Aim for 200 or more per language, half legitimate.
2. Have two fluent reviewers label each one and write why. Keep them away from the rules.
3. Freeze that set. Run `python evaluate.py test` once. Report that number, whatever it is.
4. Fix the rules using a different dev set. Never tune on the frozen set.
5. Compare against a multilingual model (XLM-RoBERTa, mBERT) on the same frozen set before claiming either is better.

Report precision and recall separately. A false alarm on a genuine bank notice teaches users to ignore the tool.
