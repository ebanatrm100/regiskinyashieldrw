"""Page background for the Streamlit app: the owner's sky-and-clouds picture behind everything, with the content on a light, slightly transparent panel
so every existing element (title, tabs, results, chat, sidebar) stays clearly readable. Pure Python (no Streamlit), never raises.

The picture is embedded in the page as a data URI, so no extra file serving or internet access is needed. assets/sky_background.jpg is made by
tools/make_sky_background.py (it removes the big REGIS' WORLD title from the original picture)."""
from __future__ import annotations
import base64, functools, pathlib

_IMAGE = pathlib.Path(__file__).parent / "assets" / "sky_background.jpg"
INK = "#10243a"          # text colour used on the panel (dark navy, high contrast on white)

_RULES = """
.stApp{background-color:#1e88e5 !important;background-image:url("__IMG__") !important;background-size:cover !important;
background-position:center top !important;background-repeat:no-repeat !important;background-attachment:fixed !important}
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
@media (max-width:640px){.stApp .block-container,.stApp [data-testid="stMainBlockContainer"]{padding:1rem .9rem 1.8rem !important;border-radius:16px;margin-top:3rem !important}}
"""


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
        return "<style>" + _RULES.replace("__IMG__", img).replace("__INK__", INK).replace("\n", " ") + "</style>"
    except Exception:
        return ""
