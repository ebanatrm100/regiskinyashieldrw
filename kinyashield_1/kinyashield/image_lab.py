"""Offline image-prompt tools from the AI Image Generation Techniques Guide: prompt improver/critic, score sheet, rule-of-thirds and
aspect-ratio calculators, latent-size demo and a tiny denoising demo. Pure Python, strict commands, four languages.
The assistant does NOT generate pictures; it writes and checks prompts. Detection is by simple keyword lists (a teaching aid, not a judge of quality)."""
from __future__ import annotations
import math, re
from textutil import fold, entry, LANGS

_T = lambda en, fr, rw, sw: {"en": en, "fr": fr, "rw": rw, "sw": sw}


def _out(id_, title, body):
    t = title if isinstance(title, dict) else {l: title for l in LANGS}
    b = body if isinstance(body, dict) else {l: body for l in LANGS}
    return entry(id_, "image_lab", t, b)


# ingredient -> (names per language, detection keywords (folded), suggested addition per language)
ING = [
    ("subject", _T("Subject", "Sujet", "Insanganyamatsiko", "Mada"), None, None),
    ("action", _T("Action", "Action", "Igikorwa", "Kitendo"),
     "walking|running|standing|sitting|holding|looking|working|playing|smiling|flying|marche|court|debout|assis|tient|regarde|travaille|joue|sourit|agenda|ahagaze|yicaye|ufashe|arareba|akora|aseka|anatembea|amesimama|ameshika|anatazama|anafanya|anacheza",
     _T("add what the subject is doing (e.g. walking slowly)", "ajoutez ce que fait le sujet (p. ex. marche lentement)", "ongeraho icyo insanganyamatsiko ikora (urugero: agenda buhoro)", "ongeza kile mada inafanya (mf. anatembea polepole)")),
    ("environment", _T("Environment", "Environnement", "Ibidukikije", "Mazingira"),
     "street|forest|city|beach|mountain|room|kitchen|market|field|farm|village|garden|sky|river|lake|desert|rue|foret|ville|plage|montagne|salle|cuisine|marche|champ|ferme|village|jardin|ciel|riviere|lac|desert|umuhanda|ishyamba|umujyi|inyanja|umusozi|isoko|umurima|umudugudu|ubusitani|ikiyaga|mto|barabara|msitu|jiji|pwani|mlima|chumba|soko|shamba|kijiji|bustani|ziwa|jangwa",
     _T("add where and when (place, season, weather)", "ajoutez où et quand (lieu, saison, météo)", "ongeraho aho n'igihe (ahantu, igihembwe, ikirere)", "ongeza wapi na lini (mahali, msimu, hali ya hewa)")),
    ("composition", _T("Composition", "Composition", "Imiterere", "Muundo"),
     "close-up|close up|wide|top-down|overhead|centered|centred|rule of thirds|portrait|landscape|aerial|low angle|high angle|symmetr|gros plan|grand angle|vue du dessus|centre|paysage|plan large|hejuru|hafi|mlalo|wima|karibu|pana|katikati",
     _T("add a framing (close-up, wide, top-down, rule of thirds)", "ajoutez un cadrage (gros plan, large, vue du dessus, règle des tiers)", "ongeraho imiterere (close-up, yagutse, ireba hejuru, rule of thirds)", "ongeza muundo (close-up, pana, mtazamo wa juu, kanuni ya theluthi)")),
    ("lighting", _T("Lighting", "Lumière", "Urumuri", "Mwanga"),
     "light|lighting|sunlight|golden hour|blue hour|sunset|sunrise|studio|rim light|backlit|overcast|neon|candle|shadow|lumiere|eclairage|coucher de soleil|lever du soleil|heure doree|ombre|urumuri|izuba|igicucu|mwanga|jua|machweo|alfajiri|kivuli",
     _T("add one clear light source (soft window light, golden hour)", "ajoutez une source de lumière claire (lumière douce de fenêtre, heure dorée)", "ongeraho isoko imwe y'urumuri (urumuri rworoshye rw'idirishya, golden hour)", "ongeza chanzo kimoja wazi cha mwanga (mwanga laini wa dirisha, golden hour)")),
    ("palette", _T("Colour palette", "Palette de couleurs", "Amabara", "Paleti ya rangi"),
     "palette|colour|color|warm|cool|pastel|muted|monochrome|teal|amber|red|blue|green|yellow|orange|purple|pink|black|white|couleur|chaud|froid|rouge|bleu|vert|jaune|noir|blanc|ibara|amabara|utukura|ubururu|icyatsi|umuhondo|rangi|nyekundu|bluu|kijani|njano|nyeusi|nyeupe",
     _T("name a colour palette (warm earth tones, teal and amber)", "nommez une palette (tons terre chauds, sarcelle et ambre)", "vuga amabara (amabara y'ubutaka ashyushye, teal na amber)", "taja paleti ya rangi (rangi za udongo joto, teal na amber)")),
    ("style", _T("Visual style", "Style visuel", "Uburyo bw'ishusho", "Mtindo wa kuona"),
     "photorealistic|photo|cinematic|watercolor|watercolour|3d|render|illustration|comic|oil painting|sketch|anime|vector|realistic|photoreal|photographie|cinematographique|aquarelle|rendu|bande dessinee|peinture|croquis|realiste|ifoto|sinema|igishushanyo|nyakuri|picha halisi|rangi za maji|mchoro|katuni",
     _T("choose ONE style (photorealistic, watercolour, 3D render)", "choisissez UN style (photoréaliste, aquarelle, rendu 3D)", "hitamo UBURYO BUMWE (nyakuri nk'ifoto, watercolor, 3D)", "chagua MTINDO MMOJA (kama picha halisi, rangi za maji, 3D)")),
    ("texture", _T("Materials / texture", "Matières / textures", "Ibikoresho / imiterere y'ubuso", "Vifaa / umbile"),
     "texture|metal|wood|glass|fabric|wet|rough|smooth|knitted|leather|stone|reflection|matiere|bois|verre|tissu|mouille|lisse|cuir|pierre|reflet|igiti|ibirahure|umwenda|utose|chuma|mbao|kioo|kitambaa|lowa|laini|ngozi|jiwe",
     _T("add a material or texture (wet pavement, brushed metal)", "ajoutez une matière ou texture (chaussée mouillée, métal brossé)", "ongeraho ibikoresho cyangwa imiterere (umuhanda utose, icyuma)", "ongeza kifaa au umbile (lami iliyolowa, chuma kilichosuguliwa)")),
    ("camera", _T("Camera language", "Langage photographique", "Ururimi rwa kamera", "Lugha ya kamera"),
     "wide-angle|wide angle|macro|depth of field|bokeh|lens|35mm|50mm|85mm|telephoto|fisheye|grand-angle|profondeur de champ|objectif|ubujyakuzimu|lenzi|kina cha uwanja",
     _T("optional: add camera language (macro, shallow depth of field)", "facultatif : ajoutez un langage photo (macro, faible profondeur de champ)", "bitari ngombwa: ongeraho ururimi rwa kamera (macro, ubujyakuzimu buto)", "hiari: ongeza lugha ya kamera (macro, kina kidogo cha uwanja)")),
    ("quality", _T("Quality goals", "Objectifs de qualité", "Intego z'ubuziranenge", "Malengo ya ubora"),
     "focal point|coherent|natural shadows|balanced|sharp|detailed|clear focus|point focal|coherent|equilibre|net|detaille|aho amaso ahurira|kitovu|wazi|undani",
     _T("add quality goals (clear focal point, natural shadows, coherent anatomy)", "ajoutez des objectifs de qualité (point focal net, ombres naturelles, anatomie cohérente)", "ongeraho intego z'ubuziranenge (aho amaso ahurira, igicucu karemano, umubiri uhuje)", "ongeza malengo ya ubora (kitovu wazi, vivuli asilia, anatomia thabiti)")),
    ("ratio", _T("Aspect ratio", "Format", "Ingano (aspect ratio)", "Uwiano wa picha"),
     "16:9|4:3|3:2|1:1|9:16|2:3|3:4|square|portrait|landscape|aspect|carre|paysage|kare|mraba|mlalo|wima",
     _T("add an aspect ratio (landscape 16:9, square 1:1, portrait 9:16)", "ajoutez un format (paysage 16:9, carré 1:1, portrait 9:16)", "ongeraho ingano (landscape 16:9, kare 1:1, portrait 9:16)", "ongeza uwiano (mlalo 16:9, mraba 1:1, wima 9:16)")),
    ("constraints", _T("Constraints", "Contraintes", "Imbogamizi", "Vikwazo"),
     "without|no text|avoid|exclude|must include|only|sans|eviter|exclure|doit inclure|uniquement|nta |utarimo|bila|epuka|usijumuishe",
     _T("state what must be included or excluded (e.g. no text)", "indiquez ce qui doit figurer ou être exclu (p. ex. pas de texte)", "vuga ibigomba kubamo cyangwa gukurwamo (urugero: nta nyandiko)", "taja kinachopaswa kuwepo au kuachwa (mf. bila maandishi)")),
]
_ING = [(k, n, [fold(x) for x in kw.split("|")] if kw else None, add) for k, n, kw, add in ING]

CONFLICTS = [
    ("photorealistic|photoreal|photo|realiste|nyakuri|picha halisi", "watercolor|watercolour|cartoon|anime|comic|aquarelle|bande dessinee|rangi za maji|katuni",
     _T("photorealistic and a drawn style (watercolour/cartoon) pull in opposite directions", "photoréaliste et un style dessiné (aquarelle/dessin animé) tirent en sens opposé", "nyakuri nk'ifoto n'uburyo bw'igishushanyo (watercolor/cartoon) birahabanye", "picha halisi na mtindo wa kuchora (rangi za maji/katuni) vinakinzana")),
    ("sunset|golden hour|sunrise|coucher de soleil|heure doree|machweo", "midnight|night|blue hour|nuit|minuit|ijoro|usiku",
     _T("sunset/golden hour and night give two different times of day", "coucher de soleil/heure dorée et nuit donnent deux moments différents", "izuba rirenga/golden hour n'ijoro bivuga ibihe bibiri bitandukanye", "machweo/golden hour na usiku ni nyakati mbili tofauti")),
    ("close-up|close up|macro|gros plan", "wide shot|wide-angle|aerial|panorama|plan large|grand angle",
     _T("close-up and wide/aerial framing conflict", "gros plan et cadrage large/aérien se contredisent", "close-up n'ishusho yagutse/ireba hejuru birahabanye", "close-up na muundo pana/wa juu vinakinzana")),
    ("minimal|minimalist|simple|minimaliste", "crowded|busy|many objects|cluttered|bondee|encombre|akajagari|msongamano",
     _T("minimal and crowded/busy ask for opposite things", "minimaliste et encombré demandent des choses opposées", "byoroshye n'akajagari bisaba ibihabanye", "rahisi na msongamano vinahitaji vitu kinyume")),
]
_CONF = [([fold(x) for x in a.split("|")], [fold(x) for x in b.split("|")], msg) for a, b, msg in CONFLICTS]

_HEAD = _T("Prompt check", "Vérification du prompt", "Isuzuma rya prompt", "Ukaguzi wa prompt")


def _has(q, kws):
    return any(k in q for k in kws)


def improve(prompt, lang="en"):
    q = fold(prompt)
    if len(prompt.strip()) < 3:
        return None
    present, missing = [], []
    for k, n, kws, add in _ING:
        if k == "subject":
            present.append(n[lang]) if len(prompt.split()) >= 1 else None
            continue
        (present if _has(q, kws) else missing).append((n, add))
    present_names = [p if isinstance(p, str) else p[0][lang] for p in present]
    conflicts = [m[lang] for a, b, m in _CONF if _has(q, a) and _has(q, b)]
    n_words = len(prompt.split())
    # a rebuilt prompt: keep the user's words, then append sensible, clearly-marked slots to fill
    slots = {"en": ["[time & weather]", "[composition]", "[one light source]", "[colour palette]", "[one style]", "[aspect ratio]", "[exclusions]"],
             "fr": ["[moment & météo]", "[composition]", "[une source de lumière]", "[palette]", "[un style]", "[format]", "[exclusions]"],
             "rw": ["[igihe n'ikirere]", "[imiterere]", "[isoko imwe y'urumuri]", "[amabara]", "[uburyo bumwe]", "[ingano]", "[ibyo wirinda]"],
             "sw": ["[wakati na hali ya hewa]", "[muundo]", "[chanzo kimoja cha mwanga]", "[paleti]", "[mtindo mmoja]", "[uwiano]", "[vizuizi]"]}[lang]
    rebuilt = prompt.strip().rstrip(".") + ", " + ", ".join(s for s, (k, n, kws, add) in zip(slots, [x for x in _ING if x[0] in ("environment", "composition", "lighting", "palette", "style", "ratio", "constraints")]) if not _has(q, kws))
    L = {
        "en": ("Ingredients found", "Missing ingredients", "Conflicts", "No conflicts found.", "Short prompt: add more detail.", "Stronger version to fill in", "Replace each [slot] with your choice, delete the ones you do not need, and keep it free of contradictions. Generate, then change one thing at a time.", "Score your result with `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`."),
        "fr": ("Ingrédients trouvés", "Ingrédients manquants", "Conflits", "Aucun conflit trouvé.", "Prompt court : ajoutez des détails.", "Version plus forte à compléter", "Remplacez chaque [emplacement] par votre choix, supprimez ceux inutiles et évitez les contradictions. Générez, puis changez une chose à la fois.", "Notez le résultat avec `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`."),
        "rw": ("Ibigize byabonetse", "Ibigize bibura", "Ibihabanye", "Nta bihabanye byabonetse.", "Prompt ni ngufi: ongeraho utuntu.", "Verisiyo ikomeye yo kuzuza", "Simbuza buri [slot] n'amahitamo yawe, ukureho ibitari ngombwa, kandi wirinde ibihabanye. Kora ishusho, hanyuma uhindure ikintu kimwe icyarimwe.", "Tanga amanota ukoresheje `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`."),
        "sw": ("Viungo vilivyopatikana", "Viungo vinavyokosekana", "Migongano", "Hakuna migongano iliyopatikana.", "Prompt fupi: ongeza undani.", "Toleo imara la kujaza", "Badilisha kila [slot] kwa chaguo lako, futa usiyohitaji, na epuka migongano. Zalisha, kisha badilisha kitu kimoja kwa wakati.", "Pa alama matokeo kwa `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`."),
    }[lang]
    lines = [f"**{L[0]}:** " + (", ".join(present_names) or "—"), "", f"**{L[1]}:**"]
    lines += [f"- {n[lang]}: {add[lang]}" for n, add in missing] or ["- —"]
    lines += ["", f"**{L[2]}:** " + ("; ".join(conflicts) if conflicts else L[3])]
    if n_words < 6:
        lines += ["", L[4]]
    lines += ["", f"**{L[5]}:**", "", f"> {rebuilt}", "", L[6], "", L[7]]
    from image_guide_db import NOT_GEN
    lines += ["", f"_{NOT_GEN[lang]}_"]
    return _out("img_improve_prompt", _HEAD, "\n".join(lines))


# ---------------------------------------------------------------- score sheet
CRIT = [("accuracy", _T("Prompt accuracy", "Fidélité au prompt", "Ukuri kuri prompt", "Usahihi wa prompt"), "accuracy|fidelite|ukuri|usahihi"),
        ("composition", _T("Composition", "Composition", "Imiterere", "Muundo"), "composition|imiterere|muundo"),
        ("lighting", _T("Lighting", "Lumière", "Urumuri", "Mwanga"), "lighting|lumiere|urumuri|mwanga"),
        ("detail", _T("Detail", "Détail", "Utuntu duto", "Undani"), "detail|details|utuntu|undani"),
        ("coherence", _T("Coherence", "Cohérence", "Guhuza", "Mshikamano"), "coherence|guhuza|mshikamano")]
_FIX = {"accuracy": _T("Rewrite the subject/action more precisely.", "Réécrivez sujet/action plus précisément.", "Ongera wandike insanganyamatsiko/igikorwa neza.", "Andika upya mada/kitendo kwa usahihi zaidi."),
        "composition": _T("Name one focal point and a framing (rule of thirds, leading lines).", "Nommez un point focal et un cadrage (règle des tiers, lignes de fuite).", "Vuga aho amaso ahurira n'imiterere (rule of thirds, imirongo iyobora).", "Taja kitovu na muundo (kanuni ya theluthi, mistari inayoongoza)."),
        "lighting": _T("Specify one light source and a time of day.", "Précisez une source de lumière et un moment de la journée.", "Garagaza isoko imwe y'urumuri n'igihe cy'umunsi.", "Taja chanzo kimoja cha mwanga na wakati wa siku."),
        "detail": _T("Add materials/textures; simplify tiny details.", "Ajoutez matières/textures ; simplifiez les petits détails.", "Ongeraho ibikoresho/imiterere; woroshye utuntu duto cyane.", "Ongeza vifaa/umbile; rahisisha undani mdogo sana."),
        "coherence": _T("Fix anatomy, perspective and shadows with a retry, closer crop or inpainting.", "Corrigez anatomie, perspective et ombres : nouvel essai, cadrage serré ou retouche.", "Kosora umubiri, perspective n'igicucu ukoresheje igerageza rishya, gutema hafi cyangwa inpainting.", "Rekebisha anatomia, mtazamo na vivuli kwa jaribio jipya, kukata karibu au inpainting.")}
_SC = re.compile(r"^\s*(?:score|rate|note|noter|tanga amanota|pa alama)\s+(?:image|picture|ishusho|picha|l'image|my image)\s*[:\-]?\s*(.+)$", re.I | re.S)


def score(text, lang="en"):
    m = _SC.match(text.strip())
    if not m:
        return None
    body = fold(m.group(1))
    vals, bad = {}, []
    for k, n, kws in CRIT:
        mm = re.search(r"(?:" + kws + r")\W{0,3}(\d+(?:[.,]\d+)?)", body)
        if mm:
            v = float(mm.group(1).replace(",", "."))
            if 1 <= v <= 5:
                vals[k] = v
            else:
                bad.append(n[lang])
    if not vals:
        msg = _T("Use numbers from 1 to 5, e.g. `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`.",
                 "Utilisez des nombres de 1 à 5, p. ex. `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`.",
                 "Koresha imibare kuva kuri 1 kugeza kuri 5, urugero `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`.",
                 "Tumia namba kutoka 1 hadi 5, mf. `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2`.")
        return _out("img_score", _T("Image score sheet", "Fiche de notation d'image", "Urupapuro rw'amanota y'ishusho", "Karatasi ya alama za picha"), msg)
    avg = sum(vals.values()) / len(vals)
    low = [k for k, v in sorted(vals.items(), key=lambda kv: kv[1]) if v <= 2] or [min(vals, key=vals.get)]
    names = {k: n for k, n, _ in CRIT}
    L = {"en": ("Scores", "Average", "Biggest weakness(es) to fix first", "Not counted (use 1 to 5)"),
         "fr": ("Notes", "Moyenne", "Principale(s) faiblesse(s) à corriger d'abord", "Non comptées (utilisez 1 à 5)"),
         "rw": ("Amanota", "Impuzandengo", "Intege nke nini zo gukosora mbere", "Ntibibaze (koresha 1 kugeza 5)"),
         "sw": ("Alama", "Wastani", "Udhaifu mkuu wa kurekebisha kwanza", "Hazikuhesabiwa (tumia 1 hadi 5)")}[lang]
    lines = [f"**{L[0]}:**"] + [f"- {names[k][lang]}: {_f(v)}/5" for k, v in vals.items()] + ["", f"**{L[1]}:** {_f(avg)}/5", "", f"**{L[2]}:**"]
    lines += [f"- {names[k][lang]} — {_FIX[k][lang]}" for k in low[:3]]
    if bad:
        lines += ["", f"_{L[3]}: {', '.join(bad)}_"]
    return _out("img_score", _T("Image score sheet", "Fiche de notation d'image", "Urupapuro rw'amanota y'ishusho", "Karatasi ya alama za picha"), "\n".join(lines))


def _f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- calculators
_DIM = re.compile(r"(\d{2,5})\s*[x×*]\s*(\d{2,5})")


def _dims(q):
    m = _DIM.search(q)
    if not m:
        return None
    w, h = int(m.group(1)), int(m.group(2))
    return (w, h) if 16 <= w <= 20000 and 16 <= h <= 20000 else None


def thirds(q, lang="en"):
    if not re.match(r"^\s*(rule of thirds|regle des tiers|règle des tiers|rule of thirds)\b", q, re.I):
        return None
    d = _dims(q)
    if not d:
        return None
    w, h = d
    xs, ys = [round(w / 3), round(2 * w / 3)], [round(h / 3), round(2 * h / 3)]
    pts = [(x, y) for y in ys for x in xs]
    body = _T(f"For a {w}x{h} picture:\n- Vertical lines at x = {xs[0]} and {xs[1]}\n- Horizontal lines at y = {ys[0]} and {ys[1]}\n- Four power points (x, y): " + ", ".join(map(str, pts)) + "\n\nPlace the main subject (or its eyes/centre of interest) near one power point and let the longer side of the picture hold the leading line.",
              f"Pour une image {w}x{h} :\n- Lignes verticales en x = {xs[0]} et {xs[1]}\n- Lignes horizontales en y = {ys[0]} et {ys[1]}\n- Quatre points forts (x, y) : " + ", ".join(map(str, pts)) + "\n\nPlacez le sujet principal (ou ses yeux/centre d'intérêt) près d'un point fort et laissez la ligne de fuite suivre le grand côté.",
              f"Ku shusho ya {w}x{h}:\n- Imirongo ihagaze kuri x = {xs[0]} na {xs[1]}\n- Imirongo iryamye kuri y = {ys[0]} na {ys[1]}\n- Ingingo enye z'ingenzi (x, y): " + ", ".join(map(str, pts)) + "\n\nShyira insanganyamatsiko nkuru (cyangwa amaso yayo) hafi y'imwe mu ngingo, imirongo iyobora ikurikire uruhande rurerure.",
              f"Kwa picha ya {w}x{h}:\n- Mistari wima kwenye x = {xs[0]} na {xs[1]}\n- Mistari mlalo kwenye y = {ys[0]} na {ys[1]}\n- Pointi nne kuu (x, y): " + ", ".join(map(str, pts)) + "\n\nWeka mada kuu (au macho yake) karibu na pointi moja na acha mstari unaoongoza ufuate upande mrefu.")
    return _out("img_thirds", _T("Rule-of-thirds grid", "Grille de la règle des tiers", "Urushundura rwa rule of thirds", "Gridi ya kanuni ya theluthi"), body)


def ratio(q, lang="en"):
    if not re.match(r"^\s*(aspect ratio|ratio|format|uwiano|ingano)\b", q, re.I):
        return None
    d = _dims(q)
    if not d:
        return None
    w, h = d
    g = math.gcd(w, h)
    rw_, rh_ = w // g, h // g
    kind = _T("landscape" if w > h else "portrait" if h > w else "square", "paysage" if w > h else "portrait" if h > w else "carré", "landscape" if w > h else "portrait" if h > w else "kare", "mlalo" if w > h else "wima" if h > w else "mraba")
    common = [(16, 9), (4, 3), (3, 2), (1, 1), (9, 16), (3, 4), (2, 3)]
    nearest = min(common, key=lambda c: abs(c[0] / c[1] - w / h))
    body = _T(f"{w}x{h} = ratio {rw_}:{rh_} ({kind['en']}), {w * h / 1e6:.2f} megapixels. Nearest common ratio: {nearest[0]}:{nearest[1]}.",
              f"{w}x{h} = format {rw_}:{rh_} ({kind['fr']}), {w * h / 1e6:.2f} mégapixels. Format courant le plus proche : {nearest[0]}:{nearest[1]}.",
              f"{w}x{h} = ingano {rw_}:{rh_} ({kind['rw']}), megapixels {w * h / 1e6:.2f}. Ingano isanzwe yegereye: {nearest[0]}:{nearest[1]}.",
              f"{w}x{h} = uwiano {rw_}:{rh_} ({kind['sw']}), megapikseli {w * h / 1e6:.2f}. Uwiano wa kawaida wa karibu: {nearest[0]}:{nearest[1]}.")
    return _out("img_ratio", _T("Aspect ratio", "Format de l'image", "Ingano y'ishusho", "Uwiano wa picha"), body)


def latent(q, lang="en"):
    if not re.match(r"^\s*latent demo\b", q, re.I):
        return None
    d = _dims(q) or (512, 512)
    w, h = d
    f = 8
    lw, lh = max(1, w // f), max(1, h // f)
    ratio_ = (w * h * 3) / (lw * lh * 4)
    body = _T(f"Illustration only (real systems differ): a {w}x{h} RGB picture has {w * h * 3:,} values. If a model compresses each side by {f} and keeps 4 channels, the latent is {lw}x{lh}x4 = {lw * lh * 4:,} values, about {ratio_:.0f} times fewer to process. The decoder then turns the latent back into pixels.",
              f"Illustration seulement (les vrais systèmes diffèrent) : une image RVB {w}x{h} compte {w * h * 3:,} valeurs. Si un modèle compresse chaque côté par {f} et garde 4 canaux, le latent fait {lw}x{lh}x4 = {lw * lh * 4:,} valeurs, soit environ {ratio_:.0f} fois moins à traiter. Le décodeur retransforme ensuite le latent en pixels.",
              f"Ni urugero gusa (sisitemu nyazo ziratandukanye): ishusho RGB {w}x{h} ifite agaciro {w * h * 3:,}. Niba icyitegererezo kigabanya buri ruhande ku {f} kigakomeza imiyoboro 4, latent ni {lw}x{lh}x4 = {lw * lh * 4:,}, ni ukuvuga inshuro zigera kuri {ratio_:.0f} nke zo gutunganya. Decoder igarura latent mo pixels.",
              f"Mfano tu (mifumo halisi hutofautiana): picha ya RGB {w}x{h} ina thamani {w * h * 3:,}. Modeli ikibana kila upande kwa {f} na kuweka chaneli 4, latent ni {lw}x{lh}x4 = {lw * lh * 4:,}, takriban mara {ratio_:.0f} chache za kuchakata. Kisha decoder hurejesha latent kuwa pikseli.")
    return _out("img_latent_demo", _T("Latent size demo", "Démo de taille latente", "Urugero rw'ingano ya latent", "Onyesho la ukubwa wa latent"), body)


def denoise(q, lang="en"):
    if not re.match(r"^\s*denoising demo\s*$", q, re.I):
        return None
    clean = [0.0, 0.2, 0.9, 0.9, 0.2, 0.0]
    noise = [0.5, -0.4, 0.3, -0.5, 0.45, -0.3]
    cur = [c + n for c, n in zip(clean, noise)]
    rows = []
    for step in range(4):
        err = sum(abs(a - b) for a, b in zip(cur, clean)) / len(clean)
        rows.append(f"step {step}: [" + ", ".join(f"{x:.2f}" for x in cur) + f"]  error {err:.2f}")
        cur = [x + 0.5 * (c - x) for x, c in zip(cur, clean)]  # remove half the predicted noise each step
    pad = _T("Toy example: a 6-pixel 'picture' with a bright centre. Each step removes half of the predicted noise, so the error shrinks. Real models predict the noise with a neural network guided by the prompt.",
             "Exemple jouet : une « image » de 6 pixels avec un centre lumineux. Chaque étape retire la moitié du bruit prédit, donc l'erreur diminue. Les vrais modèles prédisent le bruit avec un réseau de neurones guidé par le prompt.",
             "Urugero rworoheje: «ishusho» ya pixels 6 ifite hagati hererana. Buri ntambwe ikuraho kimwe cya kabiri cy'urusaku rwahanuwe, bityo ikosa rigabanuka. Ibyitegererezo nyabyo bihanura urusaku na neural network iyobowe na prompt.",
             "Mfano wa kuchezea: «picha» ya pikseli 6 yenye kati angavu. Kila hatua huondoa nusu ya kelele iliyotabiriwa, hivyo kosa hupungua. Modeli halisi hutabiri kelele kwa mtandao wa neva ukiongozwa na prompt.")
    return _out("img_denoise_demo", _T("Denoising demo", "Démo de débruitage", "Urugero rwa denoising", "Onyesho la denoising"),
                {l: pad[l] + "\n\n```\ntarget: [" + ", ".join(f"{x:.2f}" for x in clean) + "]\n" + "\n".join(rows) + "\n```" for l in LANGS})


_IMP = re.compile(r"^\s*(?:improve|check|critique|review|strengthen|ameliorer|améliorer|verifier|vérifier|noza|genzura|boresha|kagua)\s+(?:my\s+|mon\s+|ma\s+)?(?:image\s+|ai\s+image\s+)?prompt\s*[:\-]\s*(.+)$", re.I | re.S)


def find(question, lang="en"):
    t = question.strip()
    if not t or len(t) > 900:
        return None
    m = _IMP.match(t)
    if m:
        return improve(m.group(1).strip(), lang)
    for f in (score, thirds, ratio, latent, denoise):
        r = f(t, lang)
        if r:
            return r
    return None
