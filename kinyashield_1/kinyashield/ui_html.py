"""Pure HTML/CSS builders for the interface (no Streamlit import, so they can be tested)."""
import html
from detector import highlight_spans, next_steps, VERDICTS, NO_GUARANTEE

from ui_strings import UI as STR

LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 72" width="56" height="63" role="img" aria-label="KinyaShield shield logo">'
    '<defs><linearGradient id="ksg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b6e4f"/><stop offset="1" stop-color="#1a8fc4"/></linearGradient></defs>'
    '<path d="M32 3 L58 12 V35 C58 52 46 63 32 69 C18 63 6 52 6 35 V12 Z" fill="url(#ksg)"/>'
    '<path d="M32 9 L52 16 V35 C52 48 43 57 32 62 C21 57 12 48 12 35 V16 Z" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.5"/>'
    '<path d="M24 22 V50 M24 36 L40 22 M28.5 32.5 L41 50" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    '</svg>'
)

CSS = """
<style>
:root{--ks-ok:#1b8a5a;--ks-warn:#c27c0e;--ks-bad:#c0392b;--ks-line:rgba(128,128,128,.28);
}
.ks-hero,.ks-verdict,.ks-msg,.ks-card,.ks-steps,.ks-note{color:var(--text-color,inherit)}
.ks-hero{display:flex;gap:16px;align-items:center;padding:18px 20px;border-radius:16px;margin-bottom:14px;
background:linear-gradient(135deg,rgba(11,110,79,.16),rgba(26,143,196,.16));border:1px solid var(--ks-line)}
.ks-hero h1{margin:0;font-size:1.7rem;line-height:1.15;color:inherit}
.ks-hero p{margin:4px 0 0;opacity:.85;color:inherit}
.ks-pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.75rem;border:1px solid var(--ks-line);margin-right:6px;color:inherit}
.ks-verdict{border-radius:14px;padding:16px 18px;margin:12px 0;border:2px solid;display:flex;gap:14px;align-items:center;color:inherit}
.ks-verdict.ok{border-color:var(--ks-ok);background:rgba(27,138,90,.12)}
.ks-verdict.verify{border-color:var(--ks-warn);background:rgba(194,124,14,.14)}
.ks-verdict.high{border-color:var(--ks-bad);background:rgba(192,57,43,.14)}
.ks-verdict .ic{font-size:1.9rem;line-height:1}
.ks-verdict b{font-size:1.2rem}
.ks-verdict small{display:block;opacity:.85;margin-top:2px}
.ks-msg{white-space:pre-wrap;word-wrap:break-word;padding:14px;border-radius:12px;background:var(--secondary-background-color,#f1f6f9);border:1px solid var(--ks-line);color:inherit;line-height:1.6}
.ks-msg mark{padding:1px 3px;border-radius:4px;color:inherit}
.ks-msg mark.high{background:rgba(192,57,43,.35)}
.ks-msg mark.medium{background:rgba(230,160,30,.40)}
.ks-card{border-radius:12px;padding:12px 14px;margin:8px 0;background:var(--secondary-background-color,#f1f6f9);border:1px solid var(--ks-line);border-left:6px solid;color:inherit}
.ks-card.high{border-left-color:var(--ks-bad)}.ks-card.medium{border-left-color:var(--ks-warn)}.ks-card.low{border-left-color:#7f8c8d}
.ks-card h4{margin:0 0 4px;font-size:1rem}.ks-card p{margin:3px 0;font-size:.93rem}
.ks-card code{font-size:.85rem;padding:1px 5px;border-radius:4px;background:rgba(128,128,128,.18)}
.ks-steps{padding-left:1.2rem;color:inherit}.ks-steps li{margin:6px 0}
.ks-note{font-size:.85rem;opacity:.8;margin-top:10px;color:inherit}
@media(max-width:640px){.ks-hero{flex-direction:column;text-align:center}.ks-hero h1{font-size:1.4rem}.ks-verdict{flex-direction:column;text-align:center}}
</style>
"""

ICON = {"ok": "&#9989;", "verify": "&#9888;&#65039;", "high": "&#128721;"}


def _e(s):
    return html.escape(s, quote=True)


def hero_html(lang="en"):
    t = STR[lang]
    return (f'<div class="ks-hero">{LOGO_SVG}<div><h1>KinyaShield RW</h1><p>{_e(t["tagline"])}</p>'
            f'<p><span class="ks-pill">English</span><span class="ks-pill">Français</span><span class="ks-pill">Kinyarwanda</span><span class="ks-pill">Kiswahili</span></p></div></div>')


def verdict_html(result, lang="en"):
    v = result.verdict
    return (f'<div class="ks-verdict {v}"><div class="ic">{ICON[v]}</div><div><b>{_e(VERDICTS[v][lang])}</b>'
            f'<small>{_e(NO_GUARANTEE[lang])}</small></div></div>')


def highlighted_message_html(result):
    text, out, pos = result.text, [], 0
    for s, e, sev in highlight_spans(result):
        out.append(_e(text[pos:s]))
        out.append(f'<mark class="{sev}">{_e(text[s:e])}</mark>')
        pos = e
    out.append(_e(text[pos:]))
    return f'<div class="ks-msg">{"".join(out)}</div>'


def finding_cards_html(result, lang="en", include_low=False):
    cards = []
    for f in result.findings:
        if f.severity == "low" and not include_low:
            continue
        quotes = " ".join(f"<code>{_e(q)}</code>" for _, _, q in f.evidence[:3])
        cards.append(f'<div class="ks-card {f.severity}"><h4>{_e(f.title[lang])}</h4>'
                     f'<p>{_e(f.why[lang])}</p><p>{quotes}</p></div>')
    return "".join(cards)


def low_cards_html(result, lang="en"):
    return "".join(f'<div class="ks-card low"><h4>{_e(f.title[lang])}</h4><p>{_e(f.why[lang])}</p></div>'
                   for f in result.findings if f.severity == "low")


def protective_html(result):
    if not result.protective:
        return ""
    q = " ".join(f"<code>{_e(t)}</code>" for _, _, t in result.protective)
    return f'<div class="ks-card low"><p>{q}</p></div>'


def steps_html(result, lang="en"):
    return '<ol class="ks-steps">' + "".join(f"<li>{_e(s)}</li>" for s in next_steps(result, lang)) + "</ol>"
