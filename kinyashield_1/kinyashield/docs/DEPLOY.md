# Putting KinyaShield RW where anyone can open it

The browser version is one file: `web/index.html`. It has the rules inside, needs no server and no install, and sends nothing anywhere. It works in current Chrome, Firefox, Safari and Edge on phones and computers.

## Option 1: GitHub Pages (free, permanent link)
1. Create a GitHub repository, for example `kinyashield-rw`.
2. Upload `web/index.html` (you can rename it to `index.html` at the top level).
3. Settings, Pages, Source: "Deploy from a branch", Branch: `main`, folder `/ (root)`.
4. After a minute the page is at `https://<your-name>.github.io/kinyashield-rw/`.

## Option 2: Netlify Drop (fastest)
Go to app.netlify.com/drop and drag the `web` folder in. You get a link immediately. Create a free account to keep it.

## Option 3: Send the file
Share `index.html` by WhatsApp or USB. People open it in their phone browser. It still works offline once opened.

## Option 4: Streamlit Community Cloud (the Python version)
`app.py` is the Streamlit version. Push the project to GitHub, choose the repo at share.streamlit.io, main file `app.py`. Needs internet and a free account. Streamlit was not available where this was built, so test it locally first with `streamlit run app.py`.

## Before telling the public
- Have fluent speakers review French, Kinyarwanda and Kiswahili (`docs/review_*.csv`).
- Check the NCSA web address in `trusted_sources.py` and add official reporting channels you have verified yourself.
- Keep the "decision aid, not a guarantee" wording.
- The feedback box stores reports only in the visitor's own browser. Nothing reaches you unless they copy and send it. If you want reports delivered to you, that needs a small server and a privacy notice first.

## Updating
Edit `safety_rules.py` or `ui_strings.py`, then run:
```
python check_all.py
python -m unittest discover -s tests
python tests/dump_parity.py && python build_web.py && node tests/parity.js
python evaluate.py dev
```
