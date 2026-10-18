"""Original decorative artwork for the app background: five cybersecurity lock signs (left side) and cybersecurity servers (right side).
Pure Python (no Streamlit); every picture is drawn here as SVG, so nothing is downloaded and nothing copyrighted is copied.
The pictures are decoration only: app_background.py places them behind the content panel, in the free space beside it."""
from __future__ import annotations
import base64

NAVY, DEEP, CYAN, WHITE, GREEN, AMBER = "#0b2a52", "#123f75", "#6fe3ff", "#ffffff", "#7dff9c", "#ffc857"

_DEFS = ('<defs><filter id="s" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#04204a" flood-opacity=".55"/></filter>'
         '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c5ca8"/><stop offset="1" stop-color="#0b2a52"/></linearGradient></defs>')


def _padlock(extra_body="", keyhole=True, scale=1.0, cx=100, cy=105):
    """A padlock drawn in a 200x200 cell, centred on (cx, cy)."""
    k = ""
    if keyhole:
        k = f'<circle cx="100" cy="122" r="10" fill="{CYAN}"/><rect x="96" y="126" width="8" height="24" rx="3" fill="{CYAN}"/>'
    return (f'<g transform="translate({cx - 100 * scale:.1f} {cy - 105 * scale:.1f}) scale({scale})">'
            f'<path d="M70 92 V64 a30 30 0 0 1 60 0 V92" fill="none" stroke="{WHITE}" stroke-width="12" stroke-linecap="round"/>'
            f'<rect x="48" y="88" width="104" height="84" rx="15" fill="url(#g)" stroke="{CYAN}" stroke-width="4"/>{extra_body}{k}</g>')


def _lock_cell(i):
    if i == 0:       # plain padlock with a glow ring
        return f'<circle cx="100" cy="105" r="86" fill="none" stroke="{CYAN}" stroke-opacity=".55" stroke-width="3" stroke-dasharray="4 8"/>' + _padlock()
    if i == 1:       # padlock inside a shield
        shield = (f'<path d="M100 10 L170 36 V94 C170 140 138 166 100 188 C62 166 30 140 30 94 V36 Z" fill="{NAVY}" fill-opacity=".9" stroke="{CYAN}" stroke-width="5"/>')
        return shield + _padlock(scale=.62, cx=100, cy=98)
    if i == 2:       # circuit traces on the lock body
        c = (f'<g stroke="{CYAN}" stroke-width="3" fill="none" stroke-linecap="round"><path d="M60 150 H84 L92 140"/><path d="M140 150 H118 L108 140"/><path d="M60 104 H78"/><path d="M140 104 H122"/></g>'
             f'<g fill="{CYAN}"><circle cx="60" cy="150" r="4"/><circle cx="140" cy="150" r="4"/><circle cx="60" cy="104" r="4"/><circle cx="140" cy="104" r="4"/></g>')
        return _padlock(extra_body=c)
    if i == 3:       # check mark: locked and verified
        chk = f'<path d="M72 130 L94 152 L132 108" fill="none" stroke="{GREEN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
        return _padlock(extra_body=chk, keyhole=False)
    # 4: padlock with a key
    key = (f'<g transform="rotate(-35 150 160)"><circle cx="166" cy="170" r="17" fill="none" stroke="{AMBER}" stroke-width="8"/><circle cx="166" cy="170" r="5" fill="{AMBER}"/>'
           f'<rect x="96" y="166" width="54" height="8" rx="3" fill="{AMBER}"/><rect x="104" y="174" width="7" height="12" rx="2" fill="{AMBER}"/><rect x="118" y="174" width="7" height="9" rx="2" fill="{AMBER}"/></g>')
    return _padlock(scale=.92, cx=90, cy=98) + key


def locks_svg(horizontal=False):
    """Five lock signs: a vertical column (desktop) or a horizontal row (phones)."""
    cells = []
    for i in range(5):
        x, y = (i * 200, 0) if horizontal else (0, i * 200)
        cells.append(f'<g transform="translate({x} {y})" filter="url(#s)">{_lock_cell(i)}</g>')
    w, h = (1000, 200) if horizontal else (200, 1000)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{_DEFS}{"".join(cells)}</svg>'


def _rack(x, y, units, w, with_lock=None):
    h = 14 + units * 74
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{NAVY}" fill-opacity=".93" stroke="{CYAN}" stroke-width="4"/>']
    for u in range(units):
        uy = y + 14 + u * 74
        out.append(f'<rect x="{x + 12}" y="{uy}" width="{w - 24}" height="62" rx="7" fill="{DEEP}" stroke="#3aa9d6" stroke-width="2"/>')
        for n, col in enumerate((GREEN, CYAN, AMBER if u % 3 == 1 else GREEN)):
            out.append(f'<circle cx="{x + 28 + n * 14}" cy="{uy + 16}" r="4.5" fill="{col}"/>')
        for b in range(4):  # drive bays
            out.append(f'<rect x="{x + 24 + b * ((w - 60) // 4)}" y="{uy + 32}" width="{(w - 60) // 4 - 6}" height="18" rx="3" fill="#0a2349" stroke="#2c7fb0"/>')
        if with_lock is not None and u == with_lock:
            out.append(f'<g transform="translate({x + w - 52} {uy + 4}) scale(.24)">{_padlock()}</g>')
    return "".join(out)


def servers_svg():
    """Two server racks with blinking-light style LEDs, a padlock on one unit, and cables joining them."""
    body = (_rack(10, 10, 6, 160, with_lock=2) + _rack(190, 180, 4, 100, with_lock=None)
            + f'<path d="M170 470 C186 470 178 480 190 480" stroke="{CYAN}" stroke-width="4" fill="none"/>'
            f'<path d="M170 430 C186 430 178 420 190 420" stroke="{CYAN}" stroke-width="4" fill="none" stroke-dasharray="6 5"/>'
            f'<rect x="4" y="466" width="172" height="10" rx="4" fill="{NAVY}" opacity="0"/>'
            f'<g transform="translate(196 52) scale(.5)">'
            f'<path d="M100 10 L170 36 V94 C170 140 138 166 100 188 C62 166 30 140 30 94 V36 Z" fill="{NAVY}" fill-opacity=".92" stroke="{CYAN}" stroke-width="7"/>'
            f'<path d="M66 100 L90 124 L138 70" fill="none" stroke="{GREEN}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 500" width="300" height="500">{_DEFS}<g filter="url(#s)">{body}</g></svg>'


def _uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def locks_uri(horizontal=False):
    return _uri(locks_svg(horizontal))


def servers_uri():
    return _uri(servers_svg())
