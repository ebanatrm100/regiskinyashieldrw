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
_CROWN = pathlib.Path(__file__).parent / "assets" / "crown_small.png"
INK = "#10243a"          # dark text, used only on the light cards/chat bubbles
LIGHT = "#f2f7ff"        # text colour used directly on the galaxy

# Layout idea: the pictures live in the free space BESIDE the white content panel, never under it. The panel is narrowed on mid-size windows to keep a
# side column free; when the window is too small for side columns (phones, narrow windows) the pictures move to the top and bottom edges.
# --ks-sb is the width of the open sidebar, --ks-m the free space on each side of the panel.
_VARS = """
.stApp{--ks-ringimg:url("__RING__");--ks-crownimg:url("__CROWN__");--ks-room:url("__ROOM__");--ks-servers:url("__SERVERS__");--ks-locksrow:url("__LOCKSROW__");--ks-left:url("__LEFT__");--ks-img:url("__IMG__")}
"""
_VARS_PLAIN = """
.stApp{--ks-ringimg:url("__RING__");--ks-crownimg:url("__CROWN__");--ks-img:url("__IMG__")}
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
background-size:auto min(64vh,560px,calc((var(--ks-m) - 2vw - 12px) / .692)),auto min(68vh,640px,calc((var(--ks-m) - 2vw - 12px) / .26)),cover !important;
background-position:right 1.5vw center,left calc(var(--ks-sb) + 1.5vw) center,center top !important}
__SEL__ .block-container,__SEL__ [data-testid="stMainBlockContainer"]{max-width:min(736px,calc(100vw - var(--ks-sb) - 460px)) !important;margin-top:3.4rem !important}
"""
_OPEN = '.stApp:has([data-testid="stSidebar"][aria-expanded="true"])'
_CLOSED = '.stApp:not(:has([data-testid="stSidebar"][aria-expanded="true"]))'

_PANEL = """
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stBottom"],
[data-testid="stBottom"]>div{background:transparent !important}
.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{background:transparent !important;border-radius:0;
padding:1.4rem 1.6rem 2.2rem !important;margin:3.4rem auto 7rem !important;width:calc(100% - 1.2rem) !important;box-shadow:none;border:0;color:__LIGHT__}
[data-testid="stSidebar"]>div:first-child{background:rgba(5,11,30,.72) !important}
.stApp .block-container h1,.stApp .block-container h2,.stApp .block-container h3,.stApp .block-container h4,
.stApp .block-container label,.stApp .block-container [data-testid="stWidgetLabel"] *,
.stApp .block-container [data-testid="stCaptionContainer"] *,.stApp .block-container button[role="tab"] *,
.stApp .block-container [data-testid="stMarkdownContainer"]:not([data-testid="stAlert"] *):not([data-testid="stChatMessage"] *):not(.ks-card *):not(.ks-msg *) :not(a):not(code):not(mark),
.stApp .block-container [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] :not(a){color:__LIGHT__ !important;text-shadow:0 1px 3px rgba(0,0,12,.85)}
.stApp .block-container a{color:#9fd0ff !important}
.stApp .block-container .ks-hero,.stApp .block-container .ks-verdict{background:rgba(5,11,30,.62) !important;color:__LIGHT__ !important}
.stApp .block-container .ks-steps,.stApp .block-container .ks-note{color:__LIGHT__ !important;text-shadow:0 1px 3px rgba(0,0,12,.85)}
.stApp .block-container .ks-msg,.stApp .block-container .ks-card{background:#f1f6f9 !important;color:__INK__ !important;text-shadow:none}
.stApp .block-container .ks-msg *,.stApp .block-container .ks-card *{color:__INK__ !important;text-shadow:none}
.stApp .block-container [data-testid="stChatMessage"]{background:rgba(228,240,252,.92) !important;border-radius:14px}
.stApp .block-container [data-testid="stChatMessage"] *,.stApp .block-container [data-testid="stAlert"] *{color:__INK__ !important;text-shadow:none}
[data-testid="stElementContainer"]:has(style){display:none !important}
.ks-ring{position:fixed;width:min(230px,24vw);aspect-ratio:472/190;pointer-events:none;z-index:0;opacity:.96;filter:drop-shadow(0 0 7px rgba(255,200,40,.6))}
.ks-ring i{position:absolute;display:block;background-repeat:no-repeat;background-size:contain}
.ks-ring .r{left:0;right:0;bottom:0;height:51.6%;background-image:var(--ks-ringimg);background-position:center}
.ks-ring .c{width:34%;aspect-ratio:132/88;bottom:44%;background-image:var(--ks-crownimg)}
.ks-ring.tl .c,.ks-ring.bl .c{left:12%}.ks-ring.tr .c,.ks-ring.br .c{right:12%;transform:scaleX(-1)}
.ks-ring.tr .r{transform:scaleX(-1)}.ks-ring.bl .r{transform:scaleY(-1)}.ks-ring.br .r{transform:scale(-1,-1)}
.ks-ring.tl{top:3.4rem;left:10px}.ks-ring.tr{top:3.4rem;right:10px}.ks-ring.bl{bottom:10px;left:10px}.ks-ring.br{bottom:10px;right:10px}
@media (min-width:900px){.stApp:has([data-testid="stSidebar"][aria-expanded="true"]) .ks-ring.tl,.stApp:has([data-testid="stSidebar"][aria-expanded="true"]) .ks-ring.bl{left:calc(21rem + 10px)}}
@media (max-width:640px){.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{padding:1rem .9rem 1.8rem !important}.ks-ring{width:22vw;opacity:.55}}
"""
_COMPACT_MARGIN = """
.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{margin-top:5.4rem !important}
"""


def _full_rules():
    one = _ART_FULL.replace("__SEL__", _CLOSED).replace("__SB__", "0px")
    two = _ART_FULL.replace("__SEL__", _OPEN).replace("__SB__", "21rem")
    return "@media (min-width:900px){" + one + "}\n@media (min-width:1240px){" + two + "}\n"


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
        return "<style>" + rules.replace("__IMG__", img).replace("__RING__", ring_uri()).replace("__CROWN__", crown_uri()).replace("__LIGHT__", LIGHT).replace("__INK__", INK).replace("\n", " ") + "</style>"
    except Exception:
        return ""
