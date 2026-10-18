"""Page background for the Streamlit app: the owner's sky-and-clouds picture behind everything, with the content on a light, slightly transparent panel
so every existing element (title, tabs, results, chat, sidebar) stays clearly readable. Pure Python (no Streamlit), never raises.

The picture is embedded in the page as a data URI, so no extra file serving or internet access is needed. assets/sky_background.jpg is made by
tools/make_sky_background.py (it removes the big REGIS' WORLD title from the original picture)."""
from __future__ import annotations
import base64, functools, pathlib
try:
    import security_art as _art
except Exception:  # the decorations are optional; the sky picture and the readable panel work without them
    _art = None

_IMAGE = pathlib.Path(__file__).parent / "assets" / "sky_background.jpg"
INK = "#10243a"          # text colour used on the panel (dark navy, high contrast on white)

# Layout idea: the pictures live in the free space BESIDE the white content panel, never under it. The panel is narrowed on mid-size windows to keep a
# side column free; when the window is too small for side columns (phones, narrow windows) the pictures move to the top and bottom edges.
# --ks-sb is the width of the open sidebar, --ks-m the free space on each side of the panel.
_VARS = """
.stApp{--ks-room:url("__ROOM__");--ks-servers:url("__SERVERS__");--ks-locksrow:url("__LOCKSROW__");--ks-left:url("__LEFT__");--ks-img:url("__IMG__")}
"""
_VARS_PLAIN = """
.stApp{--ks-img:url("__IMG__")}
"""

_PLAIN_BG = """
.stApp{background-color:#1e88e5 !important;background-image:var(--ks-img) !important;background-size:cover !important;
background-position:center top !important;background-repeat:no-repeat !important;background-attachment:fixed !important}
"""

_ART_BASE = """
.stApp{background-color:#1e88e5 !important;
background-image:var(--ks-room),var(--ks-servers),var(--ks-locksrow),var(--ks-img) !important;
background-size:auto 120px,auto 110px,min(260px,64vw) auto,cover !important;
background-position:right 6px bottom 6px,left 6px bottom 6px,center 5px,center top !important;
background-repeat:no-repeat !important;background-attachment:fixed !important}
"""

_ART_FULL = """
__SEL__{--ks-sb:__SB__;--ks-m:max(230px,calc((100vw - var(--ks-sb) - 736px) / 2));
background-image:var(--ks-room),var(--ks-left),var(--ks-img) !important;
background-size:auto min(64vh,560px,calc((var(--ks-m) - 2vw - 12px) / .692)),auto min(88vh,760px,calc((var(--ks-m) - 2vw - 12px) / .26)),cover !important;
background-position:right 1.5vw center,left calc(var(--ks-sb) + 1.5vw) center,center top !important}
__SEL__ .block-container,__SEL__ [data-testid="stMainBlockContainer"]{max-width:min(736px,calc(100vw - var(--ks-sb) - 460px)) !important;margin-top:3.4rem !important}
"""
_OPEN = '.stApp:has([data-testid="stSidebar"][aria-expanded="true"])'
_CLOSED = '.stApp:not(:has([data-testid="stSidebar"][aria-expanded="true"]))'

_PANEL = """
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stBottom"],
[data-testid="stBottom"]>div{background:transparent !important}
.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{background:rgba(255,255,255,.93) !important;border-radius:22px;
padding:1.4rem 1.6rem 2.2rem !important;margin:3.4rem auto 7rem !important;width:calc(100% - 1.2rem) !important;
box-shadow:0 12px 44px rgba(8,40,90,.28);border:1px solid rgba(255,255,255,.7);color:__INK__}
[data-testid="stSidebar"]>div:first-child{background:rgba(255,255,255,.95) !important}
.stApp .block-container h1,.stApp .block-container h2,.stApp .block-container h3,.stApp .block-container h4,
.stApp .block-container label,.stApp .block-container [data-testid="stWidgetLabel"] *,
.stApp .block-container [data-testid="stCaptionContainer"] *,.stApp .block-container button[role="tab"] *,
.stApp .block-container [data-testid="stMarkdownContainer"] :not(a):not(code):not(mark),
[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] :not(a){color:__INK__ !important}
.stApp .block-container .ks-msg,.stApp .block-container .ks-card{background:#f1f6f9 !important;color:__INK__ !important}
.stApp .block-container [data-testid="stChatMessage"]{background:rgba(228,240,252,.9) !important;border-radius:14px}
[data-testid="stElementContainer"]:has(style){display:none !important}
@media (max-width:640px){.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{padding:1rem .9rem 1.8rem !important;border-radius:16px}}
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
        return "<style>" + rules.replace("__IMG__", img).replace("__INK__", INK).replace("\n", " ") + "</style>"
    except Exception:
        return ""
