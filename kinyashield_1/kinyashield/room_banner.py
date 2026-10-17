"""Banner picture of a cybersecurity room for the top of the Streamlit page. Pure Python (no Streamlit), never raises.

1) A real photograph: the lead image of a Wikipedia article about security / network operations centres, accepted only when it is hosted
   on Wikimedia Commons (free licences), is not an SVG, and the server confirms the URL is an image. Credit and licence are on the linked article.
   Nothing is stored in the repo and no photo link is guessed. A failed lookup is retried after 10 minutes.
2) Otherwise an original illustration of the same kind of room (assets/cyber_room.svg), clearly labelled as an illustration, so the page always has a picture."""
from __future__ import annotations
import base64, html, pathlib, time
from urllib.parse import quote

ARTICLES = ["Security operations center", "Network operations center"]
_ASSET = pathlib.Path(__file__).parent / "assets" / "cyber_room.svg"
_cache = {"photo": None, "at": 0.0}
_RETRY_SECONDS = 600

_TXT = {
    "en": ("Illustration of a cybersecurity room: teams watch for threats around the clock.", "Photo: {t} (Wikimedia Commons, free licence). Author and licence are on Wikipedia."),
    "fr": ("Illustration d'une salle de cybersécurité : des équipes surveillent les menaces jour et nuit.", "Photo : {t} (Wikimedia Commons, licence libre). Auteur et licence sur Wikipédia."),
    "rw": ("Igishushanyo cy'icyumba cy'umutekano wo kuri interineti: amatsinda akurikirana ibyago amanywa n'ijoro.", "Ifoto: {t} (Wikimedia Commons, uruhushya rwisanzuye). Uwayifotoye n'uruhushya biri kuri Wikipedia."),
    "sw": ("Mchoro wa chumba cha usalama wa mtandao: timu hufuatilia vitisho mchana na usiku.", "Picha: {t} (Wikimedia Commons, leseni huru). Mpiga picha na leseni ziko Wikipedia."),
}


def _get_json(url, timeout=5):
    import json, urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0 (educational app; ebanatrm100@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _is_image(url, timeout=5):
    import urllib.request
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "KinyaShieldRW/1.0 (educational app; ebanatrm100@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return 200 <= r.status < 300 and str(r.headers.get("Content-Type", "")).startswith("image/")


def find_photo():
    """Return {'url', 'page', 'title'} or None. Cached; failures are retried after _RETRY_SECONDS."""
    now = time.time()
    if _cache["photo"] is not None:
        return _cache["photo"] or None
    if now - _cache["at"] < _RETRY_SECONDS and _cache["at"]:
        return None
    _cache["at"] = now
    for title in ARTICLES:
        try:
            slug = quote(title.replace(" ", "_"), safe="_()")
            data = _get_json("https://en.wikipedia.org/api/rest_v1/page/summary/" + slug)
            for key in ("thumbnail", "originalimage"):
                src = (data.get(key) or {}).get("source") or ""
                if "/wikipedia/commons/" in src and not src.lower().endswith((".svg", ".tif", ".tiff")) and _is_image(src):
                    page = data.get("content_urls", {}).get("desktop", {}).get("page", "https://en.wikipedia.org/wiki/" + slug)
                    _cache["photo"] = {"url": src, "page": page, "title": title}
                    return _cache["photo"]
        except Exception:
            continue
    return None


def illustration_svg():
    try:
        return _ASSET.read_text(encoding="utf-8")
    except Exception:
        return None


def pick(lang="en", photo="auto"):
    """What to show: {'kind': 'photo'|'illustration', 'src': url or raw SVG text, 'caption': str, 'page': url or None}, or None.
    photo='auto' looks a photo up; pass a dict or None to control it (tests). Never raises."""
    try:
        k = lang if lang in _TXT else "en"
        p = find_photo() if photo == "auto" else photo
        if p:
            return {"kind": "photo", "src": p["url"], "caption": _TXT[k][1].format(t=p["title"]), "page": p["page"]}
        svg = illustration_svg()
        if svg:
            return {"kind": "illustration", "src": svg, "caption": _TXT[k][0], "page": None}
    except Exception:
        pass
    return None
