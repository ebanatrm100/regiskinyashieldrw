# MVP status

The MVP is the smallest version that does the whole job once: paste a message, get a plain-language verdict with the exact words that caused it, safe next steps, in the user's language.

## Done
- Checks pasted messages in English, French, Kinyarwanda and Kiswahili (interface and rules).
- Verdict in three levels, exact highlighted wording, reason and advice for each finding.
- Context rules: "never share your PIN" is a warning, not a request; congratulations are not prizes; "I sent the file by mistake" is not a money scam.
- Two-cue rules for stories with no keyword: relative in trouble plus money, job offer plus up-front fee, job plus WhatsApp.
- One-file browser version that works in any browser, on phones, offline once loaded, no data leaves the page.
- Learn tab, About tab with limits, text size, light and dark theme, copy summary.
- Feedback buttons that save on the visitor's device and export as CSV.
- 19 unit tests, a parity test (browser and Python give identical answers on 232 messages), a checker that catches syntax errors and missing translations, and two datasets with a documented honest evaluation.
- Reviewer sheets for French, Kinyarwanda and Kiswahili.

## Not done (needs people or decisions, not code)
- Native-speaker review of French, Kinyarwanda and Kiswahili (drafts now).
- Real messages and a frozen blind test set (current accuracy is on fictional data).
- Verified official contacts and reporting channels.
- A public link (needs your GitHub or Netlify account).
- User testing with 5 to 10 people, including people with low digital experience.
- Privacy review before collecting any real messages.
- Comparison with a multilingual model.
- Optional later: SMS or voice input, report-to-authority flow, accounts.
