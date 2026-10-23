"""Page background for the Streamlit app: the owner's galaxy picture behind the whole page (no white panel), light text on top, and the gold crown with its ring in the four corners. Pure Python (no Streamlit), never raises.

The picture is embedded in the page as a data URI, so no extra file serving or internet access is needed. assets/sky_background.jpg is made by
tools/make_sky_background.py (it removes the big REGIS' WORLD title from the original picture)."""
from __future__ import annotations
import base64, functools, pathlib
try:
    import security_art as _art
except Exception:  # the decorations are optional; the sky picture and the readable panel work without them
    _art = None

_IMAGE = pathlib.Path(__file__).parent / "assets" / "galaxy_background.jpg"
_RING = pathlib.Path(__file__).parent / "assets" / "ring_small.png"
_COLLAGE = pathlib.Path(__file__).parent / "assets" / "panel_collage.jpg"
_CROWN = pathlib.Path(__file__).parent / "assets" / "crown_small.png"
INK = "#05070f"          # dark text, used only on the light cards/chat bubbles
LIGHT = "#f2f7ff"        # text colour used directly on the galaxy

# Layout idea: the pictures live in the free space BESIDE the white content panel, never under it. The panel is narrowed on mid-size windows to keep a
# side column free; when the window is too small for side columns (phones, narrow windows) the pictures move to the top and bottom edges.
# --ks-sb is the width of the open sidebar, --ks-m the free space on each side of the panel.
_VARS = """
.stApp{--ks-ringimg:url("__RING__");--ks-crownimg:url("__CROWN__");--ks-collage:url("__COLLAGE__");--ks-room:url("__ROOM__");--ks-servers:url("__SERVERS__");--ks-locksrow:url("__LOCKSROW__");--ks-left:url("__LEFT__");--ks-img:url("__IMG__")}
"""
_VARS_PLAIN = """
.stApp{--ks-ringimg:url("__RING__");--ks-crownimg:url("__CROWN__");--ks-collage:url("__COLLAGE__");--ks-img:url("__IMG__")}
"""

_PLAIN_BG = """
.stApp{background-color:#050b1e !important;background-image:var(--ks-img) !important;background-size:cover !important;
background-position:center top !important;background-repeat:no-repeat !important;background-attachment:fixed !important}
"""

_ART_BASE = """
.stApp{background-color:#050b1e !important;
background-image:var(--ks-room),var(--ks-servers),var(--ks-locksrow),var(--ks-img) !important;
background-size:auto 120px,auto 110px,min(260px,64vw) auto,cover !important;
background-position:right 6px bottom 6px,left 6px bottom 6px,center 5px,center top !important;
background-repeat:no-repeat !important;background-attachment:fixed !important}
"""

_ART_FULL = """
__SEL__{--ks-sb:__SB__;--ks-m:max(230px,calc((100vw - var(--ks-sb) - 736px) / 2));
background-image:var(--ks-room),var(--ks-left),var(--ks-img) !important;
background-size:auto min(50vh,500px,calc((var(--ks-m) - 2vw - 12px) / .692)),auto min(46vh,520px,calc((var(--ks-m) - 2vw - 12px) / .26)),cover !important;
background-position:right 1.5vw center,left calc(var(--ks-sb) + 1.5vw) center,center top !important}
__SEL__ .block-container,__SEL__ [data-testid="stMainBlockContainer"]{max-width:min(736px,calc(100vw - var(--ks-sb) - 460px)) !important;margin-top:3.4rem !important}
"""
_OPEN = '.stApp:has([data-testid="stSidebar"][aria-expanded="true"])'
_CLOSED = '.stApp:not(:has([data-testid="stSidebar"][aria-expanded="true"]))'

_PANEL = """
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stBottom"],
[data-testid="stBottom"]>div{background:transparent !important}
.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{background-color:#0a0828 !important;background-image:var(--ks-collage) !important;
background-size:100% auto !important;background-repeat:repeat-y !important;border-radius:22px;
padding:1.4rem 1.6rem 2.2rem !important;margin:3.4rem auto 7rem !important;width:calc(100% - 1.2rem) !important;
box-shadow:0 0 44px rgba(130,90,255,.55);border:2px solid rgba(220,230,255,.75);color:__LIGHT__}
__SIDEBAR__
.stApp .block-container h1,.stApp .block-container h2,.stApp .block-container h3,.stApp .block-container h4,
.stApp .block-container label,.stApp .block-container [data-testid="stWidgetLabel"] *,
.stApp .block-container [data-testid="stCaptionContainer"] *,.stApp .block-container button[role="tab"] *,
.stApp .block-container [data-testid="stMarkdownContainer"]:not([data-testid="stAlert"] *):not([data-testid="stChatMessage"] *):not(.ks-card *):not(.ks-msg *) :not(a):not(code):not(mark):not(.ks-card):not(.ks-msg):not(.ks-card *):not(.ks-msg *),
.stApp .block-container [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] :not(a){color:__LIGHT__ !important;text-shadow:0 0 6px rgba(0,0,12,.95),0 1px 3px rgba(0,0,12,.95)}
.stApp .block-container a{color:#9fd0ff !important}
.stApp .block-container .ks-hero,.stApp .block-container .ks-verdict{background:rgba(5,11,30,.62) !important;color:__LIGHT__ !important}
.stApp .block-container .ks-steps,.stApp .block-container .ks-note{color:__LIGHT__ !important;text-shadow:0 0 6px rgba(0,0,12,.95),0 1px 3px rgba(0,0,12,.95)}
.stApp .block-container .ks-msg,.stApp .block-container .ks-card{background:#f1f6f9 !important;color:__INK__ !important;text-shadow:none}
.stApp .block-container .ks-msg *,.stApp .block-container .ks-card *{color:__INK__ !important;text-shadow:none}
.stApp .block-container [data-testid="stChatMessage"]{background:rgba(228,240,252,.92) !important;border-radius:14px}
.stApp .block-container [data-testid="stChatMessage"] *{color:__INK__ !important;text-shadow:none}
.stApp .block-container [data-testid="stAlert"],.stApp .block-container [data-testid="stAlert"]>div{background:rgba(4,6,30,.90) !important;border-radius:12px;box-shadow:0 0 0 2px #ffcf33}
.stApp .block-container [data-testid="stAlert"] *{color:#ffcf33 !important;fill:#ffcf33 !important;font-weight:600;text-shadow:none}
[data-testid="stElementContainer"]:has(style){display:none !important}
__CHIPS__
.ks-ring{position:fixed;width:min(400px,32vw);aspect-ratio:472/190;pointer-events:none;z-index:1;opacity:.96;filter:drop-shadow(0 0 7px rgba(255,200,40,.6))}
.ks-ring i{position:absolute;display:block;background-repeat:no-repeat;background-size:contain}
.ks-ring .r{left:0;right:0;bottom:0;height:51.6%;background-image:var(--ks-ringimg);background-position:center}
.ks-ring .c{width:34%;aspect-ratio:132/88;bottom:44%;background-image:var(--ks-crownimg)}
.ks-ring.tl .c,.ks-ring.bl .c{left:12%}.ks-ring.tr .c,.ks-ring.br .c{right:12%;transform:scaleX(-1)}
.ks-ring.tr .r{transform:scaleX(-1)}.ks-ring.bl .r{transform:scaleY(-1)}.ks-ring.br .r{transform:scale(-1,-1)}
.ks-ring.tl{top:3.4rem;left:10px}.ks-ring.tr{top:3.4rem;right:10px}.ks-ring.bl{bottom:10px;left:10px}.ks-ring.br{bottom:10px;right:10px}
@media (min-width:900px){.stApp:has([data-testid="stSidebar"][aria-expanded="true"]) .ks-ring.tl,.stApp:has([data-testid="stSidebar"][aria-expanded="true"]) .ks-ring.bl{left:calc(21rem + 10px)}}
@media (max-width:640px){.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{padding:1rem .9rem 1.8rem !important}.ks-ring{width:30vw;opacity:.6}}
"""
_EXC = ('[data-testid="stMarkdownContainer"]:not([data-testid="stAlert"] *):not([data-testid="stChatMessage"] *):not(.ks-card *):not(.ks-msg *)'
        ':not([data-testid="stWidgetLabel"] *):not([data-testid="stCaptionContainer"] *):not([data-testid="stCheckbox"] *):not([data-testid="stRadio"] *)'
        ':not([data-baseweb="tab-list"] *):not(.ks-hero *):not(.ks-verdict *)')
_BLOCKS = ("p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol")
_CHIP_BG = "background:rgba(4,6,30,.80) !important;border-radius:10px;padding:.15em .6em !important;width:fit-content;max-width:100%;box-shadow:0 0 0 1px rgba(200,215,255,.25)"
CHIPS = (",".join(f".stApp .block-container {_EXC} > {t}" for t in _BLOCKS) + "{" + _CHIP_BG + "}\n"
         ".stApp .block-container [data-testid=\"stMarkdownContainer\"] > ul,.stApp .block-container [data-testid=\"stMarkdownContainer\"] > ol{padding-left:1.8em !important}\n"
         ".stApp .block-container [data-testid=\"stWidgetLabel\"],.stApp .block-container [data-testid=\"stCaptionContainer\"],"
         ".stApp .block-container [data-testid=\"stCheckbox\"] label,.stApp .block-container [data-testid=\"stRadio\"] label,"
         ".stApp .block-container .ks-steps,.stApp .block-container .ks-note,.stApp .block-container [data-testid=\"stExpander\"] summary{" + _CHIP_BG + "}\n"
         ".stApp .block-container [data-baseweb=\"tab-list\"]{background:rgba(4,6,30,.85) !important;border-radius:14px;padding:4px 8px;box-shadow:0 0 0 1px rgba(200,215,255,.3)}\n"
         ".stApp .block-container .ks-hero,.stApp .block-container .ks-verdict{background:rgba(4,6,30,.86) !important;box-shadow:0 0 0 1px rgba(200,215,255,.3)}\n")
SIDEBAR = """
[data-testid="stSidebar"]{background-color:#0a0828 !important;background-image:var(--ks-collage) !important;background-size:100% auto !important;
background-repeat:repeat-y !important;border-right:2px solid rgba(220,230,255,.75);box-shadow:0 0 34px rgba(130,90,255,.55)}
[data-testid="stSidebar"]>div:first-child,[data-testid="stSidebarContent"],[data-testid="stSidebarHeader"]{background:transparent !important}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"]{background:rgba(4,6,30,.88) !important;border-radius:10px;padding:.2em .7em !important;width:fit-content;box-shadow:0 0 0 1px rgba(200,215,255,.35)}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *{color:#ffffff !important;font-weight:700 !important;text-shadow:none !important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{background:rgba(4,6,30,.88) !important;border-radius:12px;padding:.35em .9em !important;margin:.25em 0 !important;
box-shadow:0 0 0 1px rgba(200,215,255,.4)}
[data-testid="stSidebar"] [data-testid="stRadio"] label *{color:#ffffff !important;font-weight:700 !important;font-size:1.05rem !important;text-shadow:none !important}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:rgba(255,196,40,.30) !important;box-shadow:0 0 0 2px #ffd23f,0 0 14px rgba(255,210,63,.6)}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) *{color:#fff6cf !important}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked)>div:first-child{background-color:#ffd23f !important;border-color:#ffd23f !important}
[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapseButton"]{
background:rgba(4,6,30,.88) !important;border-radius:10px;box-shadow:0 0 0 1px rgba(255,255,255,.7)}
[data-testid="stSidebarCollapsedControl"] *,[data-testid="stExpandSidebarButton"] *,[data-testid="stSidebarCollapseButton"] *,
[data-testid="stHeader"] button *,[data-testid="stToolbar"] button *{color:#ffffff !important;fill:#ffffff !important;stroke:#ffffff}
"""
_COMPACT_MARGIN = """
.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{margin-top:5.4rem !important}
"""


def _full_rules():
    one = _ART_FULL.replace("__SEL__", _CLOSED).replace("__SB__", "0px")
    two = _ART_FULL.replace("__SEL__", _OPEN).replace("__SB__", "21rem")
    return "@media (min-width:900px){" + one + "}\n@media (min-width:1240px){" + two + "}\n"


_PANEL = _PANEL.replace("__CHIPS__", CHIPS).replace("__SIDEBAR__", SIDEBAR)
_RULES = _VARS + _ART_BASE + _PANEL + _COMPACT_MARGIN + _full_rules()
_PLAIN = _VARS_PLAIN + _PLAIN_BG + _PANEL


@functools.lru_cache(maxsize=1)
def data_uri():
    try:
        return "data:image/jpeg;base64," + base64.b64encode(_IMAGE.read_bytes()).decode("ascii")
    except Exception:
        return ""


@functools.lru_cache(maxsize=1)
def ring_uri():
    try:
        return "data:image/png;base64," + base64.b64encode(_RING.read_bytes()).decode("ascii")
    except Exception:
        return ""


def collage_uri():
    try:
        return "data:image/jpeg;base64," + base64.b64encode(_COLLAGE.read_bytes()).decode("ascii")
    except Exception:
        return ""


def crown_uri():
    try:
        return "data:image/png;base64," + base64.b64encode(_CROWN.read_bytes()).decode("ascii")
    except Exception:
        return ""


def rings_html():
    """The gold ring in the four corners of the page (fixed, never blocks clicks). '' if the picture is missing."""
    if not data_uri() or not ring_uri():
        return ""
    return "".join(f'<div class="ks-ring {c}"><i class="r"></i><i class="c"></i></div>' for c in ("tl", "tr", "bl", "br"))


def css():
    """The <style> block for st.markdown(..., unsafe_allow_html=True); '' if the picture is missing (the page then keeps its normal look)."""
    try:
        img = data_uri()
        if not img:
            return ""
        rules = _RULES
        if _art is not None:
            try:
                rules = (rules.replace("__SERVERS__", _art.servers_uri()).replace("__LOCKSROW__", _art.locks_row_uri())
                         .replace("__LEFT__", _art.left_uri()).replace("__ROOM__", _art.room_uri()))
            except Exception:
                pass
        if "__SERVERS__" in rules or "__LEFT__" in rules or "__ROOM__" in rules:  # decorations unavailable: plain sky picture only
            rules = _PLAIN
        return "<style>" + rules.replace("__IMG__", img).replace("__RING__", ring_uri()).replace("__CROWN__", crown_uri()).replace("__COLLAGE__", collage_uri()).replace("__LIGHT__", LIGHT).replace("__INK__", INK).replace("\n", " ") + "</style>"
    except Exception:
        return ""
