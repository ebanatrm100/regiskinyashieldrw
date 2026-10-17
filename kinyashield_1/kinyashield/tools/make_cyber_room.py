"""Generates assets/cyber_room.svg: an ORIGINAL illustration of a security operations room (not a photograph).
Run: python tools/make_cyber_room.py"""
import random, pathlib, os
COMPUTERS_ONLY = os.environ.get("COMPUTERS_ONLY") == "1"
random.seed(7)
W, H = 1200, 420
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Illustration of a cybersecurity operations room">')
a('''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050a16"/><stop offset="1" stop-color="#0c1830"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1428"/><stop offset="1" stop-color="#050a14"/></linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0d2a4d"/><stop offset=".5" stop-color="#103a66"/><stop offset="1" stop-color="#0d2a4d"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#2ee6a6" stop-opacity=".28"/><stop offset="1" stop-color="#2ee6a6" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
</defs>''')
a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
# ceiling light strips
for i in range(5):
    y = 14 + i * 9
    a(f'<rect x="{300 + i*14}" y="{y}" width="{600 - i*28}" height="3" rx="1.5" fill="#6fd3ff" opacity="{0.55 - i*0.08:.2f}"/>')
# video wall (three panels, slight perspective)
a('<rect x="210" y="52" width="780" height="206" rx="8" fill="#081426" stroke="#1d4f86" stroke-width="2"/>')
a('<rect x="214" y="56" width="772" height="198" rx="6" fill="url(#wall)"/>')
a('<rect x="214" y="56" width="772" height="198" rx="6" fill="url(#glow)"/>')
# centre panel: world-map dots + shield
a('<rect x="404" y="64" width="392" height="182" rx="4" fill="#06101f" stroke="#1d6fb0" stroke-width="1.5"/>')
cont = [(470, 110, 60, 34), (560, 100, 90, 44), (560, 160, 52, 40), (660, 108, 80, 50), (720, 170, 40, 26), (500, 190, 34, 22)]
for cx, cy, w, h in cont:
    for _ in range(int(w * h / 22)):
        x = cx + random.random() * w
        y = cy + random.random() * h
        a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.5" fill="#35c9ff" opacity="{random.uniform(.35, .9):.2f}"/>')
# attack arcs
for x1, y1, x2, y2, c in [(500, 130, 650, 120, "#ff5d5d"), (620, 175, 520, 195, "#ffb020"), (690, 140, 560, 110, "#ff5d5d"), (470, 120, 720, 175, "#ffb020")]:
    mx, my = (x1 + x2) / 2, min(y1, y2) - 38
    a(f'<path d="M{x1} {y1} Q{mx} {my} {x2} {y2}" fill="none" stroke="{c}" stroke-width="1.6" opacity=".85"/>')
    a(f'<circle cx="{x2}" cy="{y2}" r="3.5" fill="{c}"/><circle cx="{x1}" cy="{y1}" r="2.5" fill="#fff" opacity=".8"/>')
a('<path d="M600 78 L632 90 V122 C632 140 618 152 600 160 C582 152 568 140 568 122 V90 Z" fill="#0b8f6a" stroke="#38f2b0" stroke-width="2.5" opacity=".95"/>')
a('<path d="M586 118 L597 129 L616 104" fill="none" stroke="#eafff7" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
# left panel: line chart
a('<rect x="224" y="64" width="170" height="182" rx="4" fill="#06101f" stroke="#1d6fb0" stroke-width="1.5"/>')
for i in range(5):
    a(f'<line x1="234" x2="384" y1="{90 + i*30}" y2="{90 + i*30}" stroke="#12345a" stroke-width="1"/>')
pts = [(236, 210), (262, 192), (288, 200), (314, 150), (340, 164), (366, 112), (384, 124)]
a('<polyline points="' + " ".join(f"{x},{y}" for x, y in pts) + '" fill="none" stroke="#38f2b0" stroke-width="3"/>')
a('<polyline points="' + " ".join(f"{x},{y + 22}" for x, y in pts) + '" fill="none" stroke="#35c9ff" stroke-width="2" opacity=".7"/>')
a('<rect x="236" y="72" width="70" height="8" rx="2" fill="#35c9ff" opacity=".7"/><rect x="236" y="230" width="46" height="6" rx="2" fill="#38f2b0" opacity=".6"/>')
# right panel: bars + alert list
a('<rect x="806" y="64" width="170" height="182" rx="4" fill="#06101f" stroke="#1d6fb0" stroke-width="1.5"/>')
for i, hh in enumerate([40, 64, 30, 78, 52, 90]):
    a(f'<rect x="{820 + i*24}" y="{168 - hh}" width="16" height="{hh}" rx="2" fill="{["#35c9ff","#38f2b0","#35c9ff","#ffb020","#38f2b0","#ff5d5d"][i]}"/>')
for i, c in enumerate(["#ff5d5d", "#ffb020", "#38f2b0", "#38f2b0"]):
    a(f'<circle cx="826" cy="{190 + i*14}" r="4" fill="{c}"/><rect x="838" y="{187 + i*14}" width="{110 - i*14}" height="6" rx="2" fill="#1d4f86"/>')
# stand glow
a('<rect x="190" y="262" width="820" height="4" fill="#38f2b0" opacity=".35" filter="url(#blur)"/>')
# floor
a(f'<polygon points="0,{H} {W},{H} {W},282 0,282" fill="url(#floor)"/>')
for i in range(-6, 19):
    a(f'<line x1="{600 + i*45}" y1="282" x2="{600 + i*190 - 600*3 + 600*2}" y2="{H}" stroke="#12335c" stroke-width="1" opacity=".35"/>')
# desk rows with monitors and analysts
def desk(cx, y, s, analyst=True):
    w = 150 * s
    a(f'<rect x="{cx - w/2:.0f}" y="{y}" width="{w:.0f}" height="{10*s:.0f}" rx="3" fill="#13294a"/>')
    for dx in (-0.28, 0.0, 0.28):
        mw, mh = 40 * s, 26 * s
        x = cx + dx * w * 1.0 - mw / 2
        a(f'<rect x="{x:.0f}" y="{y - mh - 3*s:.0f}" width="{mw:.0f}" height="{mh:.0f}" rx="2" fill="#07243f" stroke="#35c9ff" stroke-width="{1.2*s:.1f}"/>')
        for k in range(3):
            a(f'<rect x="{x + 4*s:.0f}" y="{y - mh + (4 + k*7)*s:.0f}" width="{(mw - 8*s) * random.uniform(.4, .95):.0f}" height="{3*s:.1f}" rx="1" fill="{random.choice(["#38f2b0","#35c9ff","#ffb020"])}" opacity=".8"/>')
    if analyst:
        for dx in (-0.2, 0.2):
            hx = cx + dx * w
            a(f'<circle cx="{hx:.0f}" cy="{y + 12*s:.0f}" r="{7*s:.1f}" fill="#02060f"/>')
            a(f'<path d="M{hx - 13*s:.0f} {y + 30*s:.0f} Q{hx:.0f} {y + 14*s:.0f} {hx + 13*s:.0f} {y + 30*s:.0f} Z" fill="#02060f"/>')
for cx in (270, 600, 930):
    desk(cx, 318, 1.15, analyst=not COMPUTERS_ONLY)
for cx in (150, 440, 760, 1050):
    desk(cx, 292, 0.8, analyst=not COMPUTERS_ONLY)
for cx in (60, 1140):
    desk(cx, 372, 1.5, analyst=False)
if COMPUTERS_ONLY:
    # server racks along both side walls and tower computers under the desks: computers only, no people
    for rx in (8, 1128):
        a(f'<rect x="{rx}" y="96" width="64" height="196" rx="3" fill="#061327" stroke="#1d6fb0" stroke-width="1.5"/>')
        for j in range(11):
            yy = 104 + j * 17
            a(f'<rect x="{rx + 5}" y="{yy}" width="54" height="12" rx="2" fill="#0b2a4a"/>')
            for q in range(3):
                a(f'<circle cx="{rx + 12 + q*9}" cy="{yy + 6}" r="2" fill="{random.choice(["#38f2b0", "#38f2b0", "#35c9ff", "#ffb020"])}"/>')
            a(f'<rect x="{rx + 40}" y="{yy + 4}" width="14" height="4" rx="1" fill="#1d4f86"/>')
    for cx in (270, 600, 930):
        for dx in (-45, 45):
            a(f'<rect x="{cx + dx - 11}" y="{318 + 14}" width="22" height="34" rx="3" fill="#0b2a4a" stroke="#1d6fb0" stroke-width="1"/><circle cx="{cx + dx}" cy="{318 + 24}" r="2.5" fill="#38f2b0"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
a('</svg>')
pathlib.Path(__file__).resolve().parent.parent.joinpath("assets", "cyber_room_computers.svg" if COMPUTERS_ONLY else "cyber_room.svg").write_text("\n".join(o), encoding="utf-8")
print("ok")
