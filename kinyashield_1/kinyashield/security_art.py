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


# ------------------------------------------------------------------ left side: tagline + locks + servers, and right side: cybersecurity room
TAGLINE = "LET THE SKY NOT BE THE LIMIT"
_FONT = "Arial, Helvetica, sans-serif"


def _tagline_band(x, y, h, w=46):
    """The tagline turned 90 degrees, on a navy band, drawn on top of the art (in front of it)."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w // 2}" fill="{NAVY}" fill-opacity=".86" stroke="{CYAN}" stroke-width="3"/>'
            f'<text transform="translate({x + w / 2:.1f} {y + h / 2:.1f}) rotate(90)" text-anchor="middle" dominant-baseline="central" font-family="{_FONT}" '
            f'font-weight="700" font-size="25" letter-spacing="5" fill="{WHITE}">{TAGLINE}</text>')


def left_svg():
    """Left side: five lock signs and a server stack, with the tagline turned 90 degrees in front of them."""
    locks = "".join(f'<g transform="translate(58 {16 + i * 118}) scale(.62)">{_lock_cell(i)}</g>' for i in range(5))
    servers = f'<g transform="translate(40 650) scale(.66)">{_rack(10, 10, 6, 160, with_lock=2) + _rack(190, 180, 4, 100)}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 1000" width="260" height="1000">{_DEFS}'
            f'<g filter="url(#s)">{locks}{servers}</g><g filter="url(#s)">{_tagline_band(8, 30, 940)}</g></svg>')


def _screen(x, y, w, h, kind):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#06182e" stroke="{CYAN}" stroke-width="1.6"/>']
    if kind == "term":
        for i in range(max(2, int((h - 6) // 6))):
            ln = 8 + (i * 37) % int(max(10, w - 20))
            out.append(f'<rect x="{x + 4}" y="{y + 4 + i * 6}" width="{min(ln, w - 8)}" height="2.2" fill="{GREEN if i % 4 else CYAN}" opacity=".9"/>')
    elif kind == "graph":
        pts = " ".join(f"{x + 4 + i * (w - 8) / 7:.1f},{y + h - 6 - ((i * 53) % 7 + 1) * (h - 14) / 9:.1f}" for i in range(8))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{GREEN}" stroke-width="1.8"/>')
        for i in range(5):
            out.append(f'<rect x="{x + 5 + i * (w - 10) / 5:.1f}" y="{y + h - 5 - (i * 29) % 9 - 3}" width="{(w - 10) / 5 - 3:.1f}" height="{(i * 29) % 9 + 3}" fill="{CYAN}" opacity=".7"/>')
    else:  # network map: nodes and links
        nodes = [(.2, .3), (.5, .2), (.8, .35), (.35, .65), (.7, .7), (.5, .5)]
        for a, b in ((0, 1), (1, 2), (0, 3), (3, 5), (5, 2), (5, 4), (1, 5)):
            out.append(f'<line x1="{x + nodes[a][0] * w:.1f}" y1="{y + nodes[a][1] * h:.1f}" x2="{x + nodes[b][0] * w:.1f}" y2="{y + nodes[b][1] * h:.1f}" stroke="{CYAN}" stroke-width="1" opacity=".8"/>')
        for i, (nx, ny) in enumerate(nodes):
            out.append(f'<circle cx="{x + nx * w:.1f}" cy="{y + ny * h:.1f}" r="2.6" fill="{AMBER if i == 4 else GREEN}"/>')
    return "".join(out)


def _workstation(cx, y, s, kinds):
    """Desk with two monitors, keyboard, mouse, a computer tower and an office chair, in a frontal view."""
    m = [_screen(-56, -50, 52, 40, kinds[0]), _screen(4, -50, 52, 40, kinds[1])]
    return (f'<g transform="translate({cx} {y}) scale({s})">'
            f'<rect x="-64" y="0" width="128" height="9" rx="3" fill="#2a5f9a" stroke="{CYAN}" stroke-width="1.4"/>'
            f'<rect x="-60" y="9" width="6" height="34" fill="#16406f"/><rect x="54" y="9" width="6" height="34" fill="#16406f"/>'
            f'<rect x="-30" y="-10" width="4" height="10" fill="#7fb0d8"/><rect x="30" y="-10" width="4" height="10" fill="#7fb0d8"/>'
            f'{"".join(m)}'
            f'<rect x="-24" y="-5" width="40" height="5" rx="1.5" fill="#cfe6f7"/><rect x="21" y="-4" width="7" height="4" rx="2" fill="#cfe6f7"/>'
            f'<rect x="66" y="-26" width="20" height="35" rx="2.5" fill="#0e2f57" stroke="{CYAN}" stroke-width="1.2"/><circle cx="72" cy="-18" r="2" fill="{GREEN}"/><rect x="71" y="-8" width="10" height="2" fill="#6fa8d6"/><rect x="71" y="-3" width="10" height="2" fill="#6fa8d6"/>'
            f'<rect x="-17" y="16" width="34" height="30" rx="9" fill="#0d3563" stroke="#4aa8d8" stroke-width="1.2"/><rect x="-3" y="46" width="6" height="12" fill="#55799c"/>'
            f'<path d="M-20 62 H20 M0 58 V62" stroke="#55799c" stroke-width="3" stroke-linecap="round"/></g>')


def room_svg():
    """A security operations room: video wall, rows of analyst workstations with two monitors each, a server rack and a lit ceiling."""
    wall = (f'<rect x="0" y="0" width="360" height="236" fill="url(#w)"/><rect x="0" y="236" width="360" height="284" fill="url(#f)"/>'
            f'<rect x="20" y="8" width="320" height="6" rx="3" fill="{CYAN}" opacity=".55"/><rect x="20" y="22" width="320" height="3" rx="1.5" fill="{CYAN}" opacity=".3"/>'
            f'{_screen(28, 40, 96, 74, "map")}'
            f'<rect x="136" y="40" width="88" height="74" rx="3" fill="#06182e" stroke="{CYAN}" stroke-width="1.6"/>'
            f'<g transform="translate(180 70) scale(.3)"><path d="M0 -70 L60 -44 V8 C60 50 30 72 0 90 C-30 72 -60 50 -60 8 V-44 Z" fill="{NAVY}" stroke="{CYAN}" stroke-width="7"/><path d="M-28 6 L-6 28 L32 -22" fill="none" stroke="{GREEN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<text x="180" y="109" text-anchor="middle" font-family="{_FONT}" font-size="8" letter-spacing="1.5" fill="{GREEN}">SYSTEM SECURE</text>'
            f'{_screen(236, 40, 96, 74, "graph")}'
            f'<rect x="28" y="124" width="304" height="3" fill="{CYAN}" opacity=".4"/>'
            + "".join(f'<circle cx="{40 + i * 22}" cy="138" r="2.6" fill="{GREEN if i % 3 else AMBER}"/>' for i in range(10))
            + f'<g transform="translate(272 136) scale(.3)">{_rack(0, 0, 4, 160, with_lock=None)}</g>'
            f'<text x="28" y="226" text-anchor="start" font-family="{_FONT}" font-size="8.5" font-weight="700" letter-spacing="3" fill="{CYAN}" opacity=".85">SECURITY OPERATIONS ROOM</text>')
    back = "".join(_workstation(cx, 292, .66, k) for cx, k in ((64, ("term", "graph")), (170, ("map", "term")), (276, ("graph", "map"))))
    front = "".join(_workstation(cx, 420, .98, k) for cx, k in ((98, ("term", "map")), (252, ("graph", "term"))))
    defs = ('<defs><linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b2f5c"/><stop offset="1" stop-color="#071d3a"/></linearGradient>'
            '<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a2548"/><stop offset="1" stop-color="#04122a"/></linearGradient></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 520" width="360" height="520">{_DEFS}{defs}'
            f'<clipPath id="c"><rect x="0" y="0" width="360" height="520" rx="22"/></clipPath>'
            f'<g filter="url(#s)"><g clip-path="url(#c)">{wall}{back}{front}</g>'
            f'<rect x="1.5" y="1.5" width="357" height="517" rx="21" fill="none" stroke="{CYAN}" stroke-width="3"/></g></svg>')


def left_uri():
    return _uri(left_svg())


def room_uri():
    return _uri(room_svg())


def locks_row_with_tagline_svg():
    """Phone layout: five locks in a row with the tagline underneath."""
    cells = "".join(f'<g transform="translate({i * 200} 0)" filter="url(#s)">{_lock_cell(i)}</g>' for i in range(5))
    text = (f'<text x="500" y="262" text-anchor="middle" font-family="{_FONT}" font-weight="700" font-size="46" letter-spacing="9" fill="{WHITE}" stroke="{NAVY}" stroke-width="1.2" paint-order="stroke">{TAGLINE}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 290" width="1000" height="290">{_DEFS}{cells}{text}</svg>'


def locks_row_uri():
    return _uri(locks_row_with_tagline_svg())
