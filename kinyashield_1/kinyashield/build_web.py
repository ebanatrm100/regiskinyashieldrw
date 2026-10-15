"""Build the browser version.
  python build_web.py
Writes:
  web/index.html     complete standalone page (host anywhere: GitHub Pages, Netlify, a USB stick)
  web/artifact.html  same page as a fragment for claude.ai artifacts
Both contain the rules and strings inline, so they work offline and send nothing anywhere."""
import json, pathlib, export_rules

def main():
    data = export_rules.build()
    web = pathlib.Path("web")
    css, body = (web / "style.css").read_text(encoding="utf-8"), (web / "body.html").read_text(encoding="utf-8")
    det, app = (web / "detector.js").read_text(encoding="utf-8"), (web / "app.js").read_text(encoding="utf-8")
    ask = (web / "ask.js").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    scripts = (f'<script id="ks-data" type="application/json">{payload}</script>\n'
               f"<script>\n{det}\n</script>\n<script>\n{ask}\n</script>\n<script>\n{app}\n</script>")
    desc = "Cybersecurity and AI for digital safety, plus answers to any question, in English, French, Kinyarwanda and Kiswahili."
    page = f"<style>\n{css}\n</style>\n{body}\n{scripts}\n"
    csp = ("default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; "
           "base-uri 'none'; form-action 'none'")
    standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                  f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n'
                  f'<meta name="description" content="{desc}">\n<title>Regis KinyaShield RW</title>\n'
                  f"</head>\n<body>\n{page}</body>\n</html>\n")
    (web / "index.html").write_text(standalone, encoding="utf-8")
    fragment = ('<title>Regis KinyaShield RW</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + page)
    (web / "artifact.html").write_text(fragment, encoding="utf-8")
    print("index.html", len(standalone) // 1024, "KB | artifact.html", len(fragment) // 1024, "KB")

if __name__ == "__main__":
    main()
