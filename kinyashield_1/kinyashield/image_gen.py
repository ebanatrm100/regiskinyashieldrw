"""AI image generation for KinyaShield RW: a provider chain (Gemini image model, any OpenAI-compatible images endpoint, Hugging Face, and an OPT-IN public
keyless service), prompt builder with style presets, aspect ratios, a safety pre-check, and chat-request parsing in four languages.
Pure Python (urllib); the Gemini path imports google-genai lazily. No key is ever printed or returned in an error. Nothing is stored on disk.

Secrets (Streamlit > Settings > Secrets), all optional; the first provider that works is used:
  GEMINI_API_KEY (+ _2.._4)   uses model IMAGE_MODEL_GEMINI (default gemini-2.5-flash-image)
  IMAGE_BASE_URL, IMAGE_MODEL, IMAGE_API_KEY   any OpenAI-compatible /images/generations server
  HF_TOKEN                    Hugging Face Inference (model HF_IMAGE_MODEL, default black-forest-labs/FLUX.1-schnell; HF_IMAGE_URL overrides the address)
  IMAGE_ALLOW_PUBLIC=false    turns OFF the last-resort free keyless public service (Pollinations), which is ON by default. Only the PROMPT text is sent; it is third-party and not private.
Quality depends on the provider you configure; a generated image can contain errors (hands, lettering, geometry) and must be checked."""
from __future__ import annotations
import base64, json, re, threading, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import settings
import image_pool as POOL
from textutil import fold

TIMEOUT = 120
MAX_REF_BYTES = 6 * 1024 * 1024


class ImageGenError(RuntimeError):
    """Readable, secret-free reason why no image was produced."""


ASPECTS = {"1:1": (1024, 1024), "16:9": (1344, 768), "9:16": (768, 1344), "4:3": (1152, 864), "3:4": (864, 1152), "3:2": (1248, 832)}

STYLES = {  # id -> (label per language, English prompt fragment)
    "photo": ({"en": "Realistic photo", "fr": "Photo réaliste", "rw": "Ifoto nyakuri", "sw": "Picha halisi"}, "photorealistic photograph, natural lighting, sharp focus, realistic textures, balanced composition"),
    "cinematic": ({"en": "Cinematic", "fr": "Cinématographique", "rw": "Nka filime", "sw": "Kisinema"}, "cinematic still, dramatic lighting, shallow depth of field, rich colour grading, clear focal point"),
    "watercolor": ({"en": "Watercolour", "fr": "Aquarelle", "rw": "Watercolor", "sw": "Rangi za maji"}, "soft watercolour painting, visible paper texture, gentle colour washes"),
    "illustration": ({"en": "Illustration", "fr": "Illustration", "rw": "Igishushanyo", "sw": "Mchoro"}, "clean digital illustration, bold shapes, coherent palette, clear outlines"),
    "3d": ({"en": "3D render", "fr": "Rendu 3D", "rw": "3D", "sw": "Mchoro wa 3D"}, "high quality 3D render, soft studio lighting, detailed materials"),
    "logo": ({"en": "Logo / icon", "fr": "Logo / icône", "rw": "Logo / ikimenyetso", "sw": "Nembo / ikoni"}, "simple flat vector logo, minimal, strong silhouette, plain background, no text"),
    "poster": ({"en": "Poster", "fr": "Affiche", "rw": "Ipaji yamamaza", "sw": "Bango"}, "poster composition, strong visual hierarchy, bold colours, generous empty space for text added later"),
}
QUALITY = "clear focal point, coherent anatomy, consistent shadows and perspective, balanced composition, no distorted hands or faces, no watermark, no unreadable text"


def build_prompt(idea, style="photo", aspect="1:1", extra=""):
    """A stronger prompt from the person's idea (their own words are kept first), following the guide: subject first, then style, quality goals, constraints."""
    idea = re.sub(r"\s+", " ", (idea or "").strip())
    if not idea:
        raise ImageGenError("Describe the picture first.")
    frag = STYLES.get(style, STYLES["photo"])[1]
    ratio = {"16:9": "landscape composition", "9:16": "portrait composition", "1:1": "square composition", "4:3": "landscape composition", "3:4": "portrait composition", "3:2": "landscape composition"}.get(aspect, "")
    parts = [idea.rstrip(".")] + ([extra.strip().rstrip(".")] if extra.strip() else []) + [frag, ratio, QUALITY]
    return ". ".join(p for p in parts if p)


# ---- safety pre-check: this app is for safety education, so it refuses what would help harm or deceive
_BLOCK = [
    (r"\b(?:nude|naked|nsfw|porn|sexual|erotic|undress)\b.*\b(?:child|kid|minor|boy|girl|teen|student|school)\b|\b(?:child|kid|minor|teen)\b.*\b(?:nude|naked|nsfw|porn|sexual|erotic)\b", "minors"),
    (r"\b(?:fake|forged|counterfeit|fraudulent)\b.*\b(?:id|passport|receipt|invoice|banknote|money|certificate|diploma|mobile money|momo|screenshot|bank statement|stamp|visa)\b", "fake_documents"),
    (r"\b(?:make|build|how to make|instructions for)\b.*\b(?:bomb|explosive|chemical weapon|nerve agent|ricin)\b", "weapons"),
    (r"\b(?:deepfake|fake photo of|fake image of)\b.*\b(?:president|minister|politician|real person|my (?:teacher|neighbour|neighbor|ex)|celebrity)\b", "impersonation"),
    (r"\b(?:phishing|scam)\b.*\b(?:page|site|login|portal|screen)\b.*\b(?:look(?:s|ing)? (?:like|real)|clone|imitat\w+)\b", "phishing"),
]
_BLOCK_RE = [(re.compile(p, re.I | re.S), tag) for p, tag in _BLOCK]
REFUSAL = {
    "en": "I can't create that picture because it could help hurt or deceive people. I can make an honest alternative (an original, clearly fictional or educational image) if you describe it differently.",
    "fr": "Je ne peux pas créer cette image car elle pourrait aider à nuire ou à tromper. Je peux faire une alternative honnête (une image originale, clairement fictive ou éducative) si vous la décrivez autrement.",
    "rw": "Sinshobora gukora iyi shusho kuko yafasha kugirira nabi cyangwa kubeshya abantu. Nshobora gukora indi nziza (ishusho yihariye, y'ibihimbano bigaragara cyangwa yo kwigisha) nuyivuga ukundi.",
    "sw": "Siwezi kuunda picha hiyo kwa sababu inaweza kusaidia kudhuru au kudanganya watu. Naweza kutengeneza mbadala ya uaminifu (picha asili, ya kubuni dhahiri au ya elimu) ukiielezea tofauti.",
}


def check_prompt(text):
    """None when allowed, else a short tag of the refusal reason."""
    t = fold(text or "")
    for rx, tag in _BLOCK_RE:
        if rx.search(t):
            return tag
    return None


# ---- providers
def _err_text(e):
    return f"HTTP {e.code}" if isinstance(e, urllib.error.HTTPError) else e.__class__.__name__


def _http(url, data=None, headers=None, timeout=TIMEOUT):
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "KinyaShieldRW/1.0"}, method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:   # noqa: S310 (https checked by the callers)
        return r.read(), r.headers.get("Content-Type", "")


def _sniff(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return ""


def _gemini_keys():
    out = []
    for name in ("GEMINI_API_KEY",) + tuple(f"GEMINI_API_KEY_{i}" for i in range(2, 9)):
        v = settings.get(name)
        if v and v not in out:
            out.append(v)
    return out


def _gem_reason(e):
    """Short, secret-free reason for a failed Gemini call (quota, model not available, key rejected...)."""
    t = str(e)
    for code, word in (("429", "quota or rate limit (images may not be included in the free tier)"), ("403", "key not allowed for images"), ("401", "key rejected"), ("404", "image model not available for this key"),
                       ("400", "request refused (try a simpler description)"), ("503", "service busy"), ("500", "service error")):
        if code in t[:200]:
            return word
    return e.__class__.__name__


def _gemini(prompt, aspect, n, reference, key=None):
    keys = [key] if key else _gemini_keys()
    if not keys:
        raise ImageGenError("no Gemini key")
    from google import genai
    from google.genai import types
    first = settings.get("IMAGE_MODEL_GEMINI", "gemini-2.5-flash-image")
    models = [first] + [m for m in ("gemini-2.5-flash-image", "gemini-2.5-flash-image-preview", "gemini-2.0-flash-preview-image-generation", "gemini-2.0-flash-exp-image-generation") if m != first]
    parts = [types.Part.from_text(text=prompt + f"\nAspect ratio {aspect}.")]
    if reference:
        parts.insert(0, types.Part.from_bytes(data=reference[0], mime_type=reference[1]))
    out, last = [], None
    for key in keys:
        client = genai.Client(api_key=key)
        for model in models:
          for _ in range(n - len(out)):
            if len(out) >= n:
                break
            try:
                resp = client.models.generate_content(model=model, contents=[types.Content(role="user", parts=parts)],
                                                      config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]))
                got = False
                for cand in (getattr(resp, "candidates", None) or []):
                    for p in (getattr(getattr(cand, "content", None), "parts", None) or []):
                        inline = getattr(p, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            data = inline.data if isinstance(inline.data, (bytes, bytearray)) else base64.b64decode(inline.data)
                            out.append((bytes(data), _sniff(bytes(data)) or "image/png", "Gemini"))
                            got = True
                            break
                    if got:
                        break
                if not got:
                    last = "no image returned (the prompt may have been declined)"
            except Exception as e:
                last = _gem_reason(e)
                break
          if out:
            break
        if out:
            return out
    raise ImageGenError("Gemini: " + (last or "failed"))


def _openai(prompt, aspect, n, reference, suffix=""):
    base, model = settings.get("IMAGE_BASE_URL" + suffix), settings.get("IMAGE_MODEL" + suffix)
    if not base or not model:
        raise ImageGenError("no IMAGE_BASE_URL/IMAGE_MODEL")
    u = urllib.parse.urlparse(base)
    if u.scheme != "https" and u.hostname not in ("localhost", "127.0.0.1"):
        raise ImageGenError("IMAGE_BASE_URL must be https")
    w, h = ASPECTS.get(aspect, (1024, 1024))
    headers = {"Content-Type": "application/json", "User-Agent": "KinyaShieldRW/1.0"}
    if settings.get("IMAGE_API_KEY" + suffix):
        headers["Authorization"] = "Bearer " + settings.get("IMAGE_API_KEY" + suffix)
    try:
        raw, _ = _http(base.rstrip("/") + "/images/generations", json.dumps({"model": model, "prompt": prompt, "n": n, "size": f"{w}x{h}", "response_format": "b64_json"}).encode(), headers)
        items = json.loads(raw.decode("utf-8", "replace")).get("data") or []
        out = []
        for it in items[:n]:
            if it.get("b64_json"):
                d = base64.b64decode(it["b64_json"])
            elif it.get("url") and it["url"].startswith("https://"):
                d, _ = _http(it["url"])
            else:
                continue
            out.append((d, _sniff(d) or "image/png", "Image server"))
        if out:
            return out
        raise ImageGenError("Image server returned no image")
    except ImageGenError:
        raise
    except Exception as e:
        raise ImageGenError("Image server: " + _err_text(e)) from None


HF_MODELS = ("black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0")


def _hf(prompt, aspect, n, reference, token=None, model=None):
    tok = token or settings.get("HF_TOKEN")
    if not tok:
        raise ImageGenError("no HF_TOKEN")
    model = model or settings.get("HF_IMAGE_MODEL", HF_MODELS[0])
    url = (settings.get("HF_IMAGE_URL") if model == settings.get("HF_IMAGE_MODEL", HF_MODELS[0]) else "") or f"https://router.huggingface.co/hf-inference/models/{model}"
    w, h = ASPECTS.get(aspect, (1024, 1024))
    out, last = [], None
    for _ in range(n):
        try:
            raw, ctype = _http(url, json.dumps({"inputs": prompt, "parameters": {"width": w, "height": h}}).encode(),
                               {"Authorization": "Bearer " + tok, "Content-Type": "application/json", "Accept": "image/png", "User-Agent": "KinyaShieldRW/1.0"})
            if _sniff(raw):
                out.append((raw, _sniff(raw), "Hugging Face"))
            else:
                last = "unexpected response"
        except Exception as e:
            last = _err_text(e)
    if out:
        return out
    raise ImageGenError("Hugging Face: " + (last or "failed"))


_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36", "Accept": "image/*,*/*;q=0.8"}


def _public(prompt, aspect, n, reference, seed=0):
    """Keyless public service (Pollinations). ON by default as the last resort so picture creation keeps working; set IMAGE_ALLOW_PUBLIC=false to disable.
    Only the prompt text is sent. Tries several models and a shortened prompt before giving up."""
    if not settings.flag("IMAGE_ALLOW_PUBLIC", True):
        raise ImageGenError("public service not enabled")
    w, h = ASPECTS.get(aspect, (1024, 1024))
    short = prompt.split(". ")[0][:300]
    attempts = [(prompt[:700], "flux"), (short, "flux"), (short, "turbo"), (short, "")]
    out, last = [], None
    for i in range(n):
        for text, model in attempts:
            try:
                q = f"?width={w}&height={h}&nologo=true&seed={i + 7 + seed}" + (f"&model={model}" if model else "")
                raw, _ = _http("https://image.pollinations.ai/prompt/" + urllib.parse.quote(text) + q, headers=_UA, timeout=75)
                if _sniff(raw):
                    out.append((raw, _sniff(raw), "Pollinations (public)"))
                    break
                last = "unexpected response"
            except Exception as e:
                last = _err_text(e)
    if out:
        return out
    raise ImageGenError("Public service: " + (last or "failed"))


PROVIDERS = [("gemini", _gemini), ("openai", _openai), ("hf", _hf), ("public", _public)]
_ORDER = ("gemini", "openai", "hf", "public")


def _slots():
    """Every configured service as (unique name, kind, call(prompt, aspect, n, reference, seed)). Each key/token/endpoint is its own slot, so one that runs
    out of quota is skipped on its own while the others keep working."""
    out = []
    for i, k in enumerate(_gemini_keys(), 1):
        out.append((f"gemini#{i}", "gemini", lambda p, a, n, r, sd, k=k: _gemini(p, a, n, r, key=k)))
    for suf in ("", "_2", "_3", "_4"):
        if settings.get("IMAGE_BASE_URL" + suf) and settings.get("IMAGE_MODEL" + suf):
            out.append((f"server{suf or '_1'}", "openai", lambda p, a, n, r, sd, suf=suf: _openai(p, a, n, r, suffix=suf)))
    toks = []
    for nm in ("HF_TOKEN", "HF_TOKEN_2", "HF_TOKEN_3", "HF_TOKEN_4"):
        v = settings.get(nm)
        if v and v not in toks:
            toks.append(v)
    first = settings.get("HF_IMAGE_MODEL", HF_MODELS[0])
    models = [first] + [m for m in HF_MODELS if m != first]
    for ti, t in enumerate(toks, 1):
        for m in models:
            out.append((f"hf#{ti}:{m.split('/')[-1]}", "hf", lambda p, a, n, r, sd, t=t, m=m: _hf(p, a, n, r, token=t, model=m)))
    if settings.flag("IMAGE_ALLOW_PUBLIC", True):
        out.append(("public", "public", lambda p, a, n, r, sd: _public(p, a, n, r, seed=sd)))
    return out


def _ordered(slots):
    """Quality order (Gemini, own server, Hugging Face, public) but keys of the same kind start at a rotating position, spreading load evenly."""
    rot = POOL.rotate()
    out = []
    for kind in _ORDER:
        grp = [x for x in slots if x[1] == kind]
        if grp:
            o = rot % len(grp)
            out += grp[o:] + grp[:o]
    return out


def configured():
    """Names of the providers that have what they need in Secrets (for a status line)."""
    names = []
    if _gemini_keys():
        names.append("Gemini" + (f" ×{len(_gemini_keys())}" if len(_gemini_keys()) > 1 else ""))
    if any(x[1] == "openai" for x in _slots()):
        names.append("Image server")
    if settings.get("HF_TOKEN"):
        names.append("Hugging Face")
    if settings.flag("IMAGE_ALLOW_PUBLIC", True):
        names.append("Pollinations (public)")
    return names


def status():
    """{'ready': n, 'cooling': n, 'total': n, 'active': n, 'waiting': n, 'cached': n}: for the studio status line."""
    sl = _slots(); snap = POOL.HEALTH.snapshot()
    cooling = sum(1 for n, _, _ in sl if snap.get(n, 0) > 0)
    g = POOL.GATE.stats()
    return {"ready": len(sl) - cooling, "cooling": cooling, "total": len(sl), "active": g["active"], "waiting": g["waiting"], "cached": POOL.CACHE.stats()["items"]}


def _one(prompt, aspect, reference, seed):
    """One picture from the best available service; raises ImageGenError("failed: ...") with every reason."""
    slots = _ordered(_slots())
    if not slots:
        raise ImageGenError("not_configured")
    reasons = []

    def attempt(nm, kd, f):
        try:
            res = f(prompt, aspect, 1, reference if kd == "gemini" else None, seed)
            if res:
                POOL.HEALTH.ok(nm)
                return res[0]
        except ImageGenError as e:
            msg = str(e)
            if not (msg.startswith("no ") or msg == "public service not enabled"):
                POOL.HEALTH.fail(nm, POOL.classify(msg)); reasons.append(msg)
        except Exception as e:
            POOL.HEALTH.fail(nm, "other"); reasons.append(f"{nm}: {_err_text(e)}")
        return None

    live = [x for x in slots if POOL.HEALTH.available(x[0])]
    for x in live or slots:        # when every service is cooling down, try them all once anyway rather than refusing
        res = attempt(*x)
        if res:
            return res
    raise ImageGenError("failed: " + ("; ".join(dict.fromkeys(reasons)) if reasons else "no service returned a picture"))


def fair_use(who, cost=1):
    """(allowed, seconds_to_wait) for one visitor. Limits per minute/hour come from Secrets IMAGE_PER_MINUTE (default 6) and IMAGE_PER_HOUR (default 40); 0 = no limit. IMAGE_GLOBAL_PER_MINUTE (default 0 = off) caps the whole app."""
    ok, wait = POOL.LIMITER.check(who or "anon", settings.number("IMAGE_PER_MINUTE", 6), settings.number("IMAGE_PER_HOUR", 40), cost)
    if ok and settings.number("IMAGE_GLOBAL_PER_MINUTE", 0):      # optional cap for the whole app, protects your provider quota from many new tabs
        ok, wait = POOL.LIMITER.check("__all__", settings.number("IMAGE_GLOBAL_PER_MINUTE", 0), 0, cost)
    return ok, wait


def generate(prompt, aspect="1:1", n=1, reference=None, variant=0):
    """[(bytes, mime, provider)]. Identical requests are served from a shared cache; otherwise the request waits (bounded) for a free slot, then the pictures
    are made in parallel from the healthiest services, rotating over all keys. `variant` > 0 asks for a different picture of the same idea (skips the cache).
    reference=(bytes, mime) asks for an edit/variation when supported (Gemini). Raises ImageGenError with the reasons (no secrets)."""
    n = max(1, min(int(n or 1), 4))
    tag = check_prompt(prompt)
    if tag:
        raise ImageGenError("refused:" + tag)
    if reference and (len(reference[0]) > MAX_REF_BYTES or not _sniff(reference[0])):
        raise ImageGenError("The reference photo must be a PNG, JPG or WEBP under 6 MB.")
    POOL.configure(settings.number("IMAGE_MAX_CONCURRENT", 6) or 6, settings.number("IMAGE_CACHE_MB", 120) or 120)
    POOL.count("requests")
    ckey = None if (reference or variant) else POOL.Cache.key("img", prompt, aspect, n)
    if ckey:
        hit = POOL.CACHE.get(ckey)
        if hit:
            POOL.count("cache_hits")
            return [(b, m, pv) for b, m, pv in hit]
    if not _slots():
        raise ImageGenError("not_configured")
    leader = True
    if ckey:                                   # the same request already being made right now: wait for it and share the result instead of paying twice
        leader, ev = POOL.FLIGHT.begin(ckey)
        if not leader:
            ev.wait(timeout=float(settings.number("IMAGE_QUEUE_WAIT", 45) or 45))
            hit = POOL.CACHE.get(ckey)
            if hit:
                POOL.count("cache_hits")
                return [(b, m, pv) for b, m, pv in hit]
            leader = True                      # the leader failed or timed out: make our own
    try:
        return _generate_locked(prompt, aspect, n, reference, variant, ckey)
    finally:
        if ckey and leader:
            POOL.FLIGHT.done(ckey)


def _generate_locked(prompt, aspect, n, reference, variant, ckey):
    if not POOL.GATE.acquire(timeout=float(settings.number("IMAGE_QUEUE_WAIT", 45) or 45)):
        POOL.count("busy")
        raise ImageGenError("busy")
    try:
        text = prompt if not variant else prompt + f". Variation {variant + 1}: a different composition and angle"
        out, errs = [], []
        if n == 1:
            try:
                out.append(_one(text, aspect, reference, variant))
            except ImageGenError as e:
                errs.append(e)
        else:
            with ThreadPoolExecutor(max_workers=n) as ex:
                futs = [ex.submit(_one, text, aspect, reference, variant * 10 + i) for i in range(n)]
                for f in futs:
                    try:
                        out.append(f.result())
                    except ImageGenError as e:
                        errs.append(e)
        if not out:
            POOL.count("failures")
            raise errs[0] if errs else ImageGenError("failed: no image returned")
        POOL.count("images", len(out))
    finally:
        POOL.GATE.release()
    if ckey and len(out) == n:
        POOL.CACHE.put(ckey, list(out), sum(len(b) for b, _, _ in out))
    return out


NOT_CONFIGURED = {
    "en": "Image creation is not switched on yet. The owner can enable it in Streamlit Secrets with a Gemini key (GEMINI_API_KEY), or HF_TOKEN (Hugging Face, free), or IMAGE_BASE_URL + IMAGE_MODEL. Meanwhile I can write a strong prompt for you to use in any image tool.",
    "fr": "La création d'images n'est pas encore activée. Le propriétaire peut l'activer dans les Secrets Streamlit avec une clé Gemini (GEMINI_API_KEY), ou HF_TOKEN (Hugging Face, gratuit), ou IMAGE_BASE_URL + IMAGE_MODEL. En attendant, je peux rédiger un bon prompt à utiliser dans n'importe quel outil d'image.",
    "rw": "Gukora amashusho ntibirashyirwaho. Nyiri porogaramu ashobora kubishyiraho muri Streamlit Secrets akoresheje urufunguzo rwa Gemini (GEMINI_API_KEY), cyangwa HF_TOKEN (Hugging Face, ku buntu), cyangwa IMAGE_BASE_URL + IMAGE_MODEL. Muri aka kanya nshobora kukwandikira prompt ikomeye wakoresha mu gikoresho icyo ari cyo cyose cy'amashusho.",
    "sw": "Uundaji wa picha haujawashwa bado. Mmiliki anaweza kuuwasha kwenye Streamlit Secrets kwa ufunguo wa Gemini (GEMINI_API_KEY), au HF_TOKEN (Hugging Face, bure), au IMAGE_BASE_URL + IMAGE_MODEL. Kwa sasa naweza kukuandikia prompt imara ya kutumia kwenye zana yoyote ya picha.",
}
FAILED = {
    "en": "I could not create the picture right now: every image service I tried failed (reasons below). Try again in a moment or use a shorter, simpler description.",
    "fr": "Je n'ai pas pu créer l'image pour le moment : tous les services d'images essayés ont échoué (raisons ci-dessous). Réessayez dans un instant ou utilisez une description plus courte et simple.",
    "rw": "Sinashoboye gukora ishusho ubu: serivisi zose z'amashusho nagerageje ntizakoze (impamvu ziri hasi). Ongera ugerageze nyuma gato cyangwa ukoreshe ibisobanuro bigufi kandi byoroshye.",
    "sw": "Sikuweza kuunda picha sasa: huduma zote za picha nilizojaribu zimeshindwa (sababu ziko chini). Jaribu tena baadaye kidogo au tumia maelezo mafupi na rahisi.",
}
BUSY = {"en": "Many people are creating pictures right now and the waiting line is full. Please try again in a few seconds.",
        "fr": "Beaucoup de personnes créent des images en ce moment et la file d'attente est pleine. Réessayez dans quelques secondes.",
        "rw": "Abantu benshi barimo gukora amashusho ubu kandi umurongo wuzuye. Ongera ugerageze nyuma y'amasegonda make.",
        "sw": "Watu wengi wanaunda picha sasa na foleni imejaa. Tafadhali jaribu tena baada ya sekunde chache."}
LIMIT = {"en": "You have created many pictures in a short time. To keep the service fair for everyone, please wait about {s} seconds and try again.",
         "fr": "Vous avez créé beaucoup d'images en peu de temps. Pour que le service reste équitable pour tous, attendez environ {s} secondes puis réessayez.",
         "rw": "Wakoze amashusho menshi mu gihe gito. Kugira ngo serivisi ibe ingana kuri bose, tegereza nka {s} amasegonda ongera ugerageze.",
         "sw": "Umeunda picha nyingi ndani ya muda mfupi. Ili huduma iwe ya haki kwa wote, subiri takriban sekunde {s} kisha ujaribu tena."}
DISCLOSE = {"en": "AI-generated image. It may contain errors (hands, lettering, geometry) and is not a real photograph; check it before you share or rely on it.",
            "fr": "Image générée par IA. Elle peut contenir des erreurs (mains, texte, géométrie) et n'est pas une vraie photographie ; vérifiez-la avant de la partager.",
            "rw": "Ishusho yakozwe na AI. Ishobora kugira amakosa (ibiganza, inyuguti, imiterere) kandi si ifoto nyayo; yigenzure mbere yo kuyisangiza abandi.",
            "sw": "Picha iliyozalishwa na AI. Inaweza kuwa na makosa (mikono, herufi, jiometri) na si picha halisi; ikague kabla ya kuishiriki."}


def friendly_error(exc, lang="en"):
    msg = str(exc)
    k = lang if lang in REFUSAL else "en"
    if msg.startswith("refused:"):
        return REFUSAL[k]
    if msg == "not_configured":
        return NOT_CONFIGURED[k]
    if msg == "busy":
        return BUSY[k]
    if msg.startswith("limit:"):
        return LIMIT[k].format(s=msg.split(":", 1)[1])
    if msg.startswith("The reference") or msg.startswith("Describe"):
        return msg
    detail = msg[len("failed: "):] if msg.startswith("failed: ") else ""
    return FAILED[k] + (f"\n\n_({detail[:220]})_" if detail else "")


# ---- chat request parsing ("draw a cat on a roof", "génère une image de ...", "kora ishusho ya ...", "tengeneza picha ya ...")
_VERB = r"(?:generate|create|make|draw|paint|design|produce|render|imagine|sketch|illustrate|génère|genere|générer|crée|cree|créer|dessine|dessiner|fais|fabrique|peins|kora|shushanya|ntegurira|nkorera|nshushanyiriza|tengeneza|nitengenezee|chora|nichoree|unda)"
_NOUN = r"(?:an?\s+|the\s+|une?\s+|des\s+|some\s+)?(?:image|picture|photo|illustration|drawing|painting|poster|logo|icon|artwork|wallpaper|portrait|banner|cartoon|image|dessin|affiche|logo|icône|ishusho|igishushanyo|logo|ifoto|picha|mchoro|nembo|bango)"
_REQ = [
    re.compile(rf"^\s*(?:please\s+|s'il te pla[iî]t\s+|nyabuneka\s+|tafadhali\s+)?(?:can you\s+|could you\s+|peux-tu\s+|pouvez-vous\s+)?{_VERB}(?:\s+me|\s+moi)?\s+(?P<noun>{_NOUN})\s+(?P<prep>of|about|showing|with|for|de|d'|du|des|pour|ya|y'|za|wa|kuri|yerekana|ina|kwa)\s*(?P<idea>.+?)\s*$", re.I | re.S),
    re.compile(rf"^\s*(?:draw|paint|sketch|illustrate|dessine|peins|chora|shushanya)(?:\s+me|\s+moi)?\s+(?P<idea>.+?)\s*$", re.I | re.S),
    re.compile(rf"^\s*(?:image|picture|draw|imagine|dessine|ishusho|picha)\s*[:：]\s*(?P<idea>.+?)\s*$", re.I | re.S),
]
_REAL = re.compile(r"^\s*(?:show|give|find|get|display|montre|affiche|ndeshya|nyereka|nionyeshe|onyesha)\b", re.I)


def parse_request(question):
    """The picture idea when the message asks to CREATE an image, else None. Requests to show/find existing photos are not creation requests."""
    q = (question or "").strip()
    if not q or len(q) > 600 or _REAL.match(q):
        return None
    for rx in _REQ:
        m = rx.match(q)
        if m:
            idea = m.group("idea").strip(" \"'“”«».")
            noun = (m.groupdict().get("noun") or "").lower()
            kept = re.search(r"(logo|poster|icon|icône|banner|wallpaper|cartoon|portrait|affiche|nembo|bango)", noun)
            if kept and (m.groupdict().get("prep") or "").lower() in ("for", "pour", "kuri", "kwa", "of", "de", "d'", "du", "des", "ya", "y'", "za", "wa"):
                idea = f"{kept.group(1)} for {idea}" if (m.groupdict().get("prep") or "").lower() in ("for", "pour", "kuri", "kwa") else f"{kept.group(1)} of {idea}"
            if 2 <= len(idea) <= 500 and not re.match(r"^(?:a|an|the)?\s*(?:flowchart|diagram|chart|graph|table|plan|function|class|script|program)\b", idea, re.I):
                return idea
    return None


def suggest_style(idea):
    """A style id guessed from the words of the idea (logo, poster, cartoon...), else 'photo'."""
    t = fold(idea or "")
    for words, sid in ((("logo", "icon", "icone", "nembo", "ikimenyetso"), "logo"), (("poster", "affiche", "banner", "bango"), "poster"), (("cartoon", "illustration", "comic", "drawing", "mchoro", "igishushanyo"), "illustration"),
                       (("watercolor", "watercolour", "aquarelle"), "watercolor"), (("3d", "render"), "3d"), (("cinematic", "movie", "film"), "cinematic")):
        if any(w in t.split() or (len(w) > 4 and w in t) for w in words):
            return sid
    return "photo"
