"""Chat attachments: photos (PNG/JPG/WEBP) and documents (PDF/Word/txt/md/csv/log). Validates size and real file type (not just the extension), extracts document
text with docs_assistant, and returns safe, readable messages in four languages. Nothing is written to disk; everything stays in the session.
Photos are only understood by the Gemini AI (vision); documents work with any configured AI."""
from __future__ import annotations
import docs_assistant as DA
import image_gen as IG

IMG_EXTS = ("png", "jpg", "jpeg", "webp")
ALL_EXTS = list(IMG_EXTS) + list(DA.EXTS)
MAX_IMG = 6 * 1024 * 1024
MAX_FILES = 4


class AttachError(Exception):
    """Message key; use message(key, lang)."""


MSG = {
    "bigimg": {"en": "A photo must be smaller than 6 MB.", "fr": "Une photo doit faire moins de 6 Mo.", "rw": "Ifoto igomba kuba iri munsi ya MB 6.", "sw": "Picha lazima iwe chini ya MB 6."},
    "fakeimg": {"en": "That file is not a real PNG, JPG or WEBP photo.", "fr": "Ce fichier n'est pas une vraie photo PNG, JPG ou WEBP.", "rw": "Iyi dosiye si ifoto nyayo ya PNG, JPG cyangwa WEBP.", "sw": "Faili hilo si picha halisi ya PNG, JPG au WEBP."},
    "toomany": {"en": f"Attach at most {MAX_FILES} files at a time.", "fr": f"Joignez au plus {MAX_FILES} fichiers à la fois.", "rw": f"Shyiramo dosiye zitarenze {MAX_FILES} icyarimwe.", "sw": f"Ambatisha faili zisizozidi {MAX_FILES} kwa wakati mmoja."},
    "vision": {"en": "To understand photos the AI needs a Gemini key (GEMINI_API_KEY) in Secrets. Documents and text still work.", "fr": "Pour comprendre les photos, l'IA a besoin d'une clé Gemini (GEMINI_API_KEY) dans les Secrets. Les documents et le texte fonctionnent toujours.",
               "rw": "Kugira ngo AI isobanukirwe amafoto ikeneye urufunguzo rwa Gemini (GEMINI_API_KEY) muri Secrets. Inyandiko n'amagambo biracyakora.", "sw": "Ili kuelewa picha AI inahitaji ufunguo wa Gemini (GEMINI_API_KEY) kwenye Secrets. Hati na maandishi bado vinafanya kazi."},
}


def message(key, lang="en"):
    m = MSG.get(key)
    if m:
        return m.get(lang, m["en"])
    return DA.MSG.get(key, DA.MSG["bad"]).get(lang, DA.MSG["bad"]["en"])


def read(files):
    """files: iterable of (name, bytes). Returns {'images': [(bytes, mime, name)], 'text': str, 'names': [...]}; raises AttachError(key)."""
    files = list(files or [])
    if len(files) > MAX_FILES:
        raise AttachError("toomany")
    images, texts, names = [], [], []
    for name, data in files:
        ext = (name or "").rsplit(".", 1)[-1].lower() if "." in (name or "") else ""
        if ext in IMG_EXTS:
            if len(data) > MAX_IMG:
                raise AttachError("bigimg")
            mime = IG._sniff(data)
            if not mime:
                raise AttachError("fakeimg")
            images.append((data, mime, name))
        else:
            try:
                pages = DA.extract_pages(name, data)
            except DA.DocError as e:
                raise AttachError(str(e)) from None
            texts.append(f"=== {name} ===\n" + DA.full_text(pages))
        names.append(name)
    return {"images": images, "text": "\n\n".join(texts)[:DA.MAX_CHARS], "names": names}
