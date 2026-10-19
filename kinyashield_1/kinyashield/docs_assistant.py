"""Document assistant: read an uploaded PDF / Word (.docx) / text file, summarise it, pull out key details and answer questions from it.
Pure Python (pypdf is optional for PDFs). Everything here is EXTRACTIVE: it selects and quotes sentences that are really in the document and
never adds facts. Nothing is saved to disk. Scanned PDFs (pictures of pages) contain no text and cannot be read without OCR."""
from __future__ import annotations
import io, math, re, zipfile
from collections import Counter
from textutil import fold, LANGS

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARS = 400_000
EXTS = ("pdf", "docx", "txt", "md", "csv", "log")


class DocError(Exception):
    """A readable message for the user (the text is safe to show)."""


MSG = {
    "empty": {"en": "I could not find any text in this file. If it is a scanned PDF (a photo of pages), it has no text to read; paste the text instead.",
              "fr": "Je n'ai trouvé aucun texte dans ce fichier. S'il s'agit d'un PDF scanné (photo de pages), il n'a pas de texte à lire ; collez le texte à la place.",
              "rw": "Nta nyandiko nabonye muri iyi dosiye. Niba ari PDF yafotowe (amafoto y'impapuro), nta nyandiko ifite yasomwa; shyiramo inyandiko ubwayo.",
              "sw": "Sikuona maandishi yoyote kwenye faili hii. Kama ni PDF iliyoskaniwa (picha za kurasa), haina maandishi ya kusoma; bandika maandishi badala yake."},
    "big": {"en": "This file is larger than 10 MB. Please upload a smaller file or part of it.", "fr": "Ce fichier dépasse 10 Mo. Envoyez un fichier plus petit ou une partie.",
            "rw": "Iyi dosiye irenze MB 10. Shyiramo ito cyangwa igice cyayo.", "sw": "Faili hii inazidi MB 10. Pakia faili ndogo au sehemu yake."},
    "type": {"en": "I can read PDF, Word (.docx), .txt, .md and .csv files.", "fr": "Je peux lire les fichiers PDF, Word (.docx), .txt, .md et .csv.",
             "rw": "Nshobora gusoma PDF, Word (.docx), .txt, .md na .csv.", "sw": "Naweza kusoma faili za PDF, Word (.docx), .txt, .md na .csv."},
    "nopdf": {"en": "PDF reading is not installed on this server (pypdf). Word, text and CSV files still work.", "fr": "La lecture des PDF n'est pas installée sur ce serveur (pypdf). Word, texte et CSV fonctionnent.",
              "rw": "Gusoma PDF ntibyashyizweho kuri iyi seriveri (pypdf). Word, inyandiko na CSV biracyakora.", "sw": "Kusoma PDF hakujasakinishwa kwenye seva hii (pypdf). Word, maandishi na CSV bado vinafanya kazi."},
    "bad": {"en": "I could not open this file; it may be damaged or password-protected.", "fr": "Impossible d'ouvrir ce fichier ; il est peut-être abîmé ou protégé par mot de passe.",
            "rw": "Sinashoboye gufungura iyi dosiye; ishobora kuba yangiritse cyangwa ifite ijambo ry'ibanga.", "sw": "Sikuweza kufungua faili hii; huenda imeharibika au ina nywila."},
}


def extract_pages(name, data):
    """Return a list of page/section texts. Raises DocError with a safe message."""
    if len(data) > MAX_BYTES:
        raise DocError("big")
    ext = (name or "").rsplit(".", 1)[-1].lower() if "." in (name or "") else ""
    pages = []
    try:
        if ext == "pdf":
            try:
                from pypdf import PdfReader
            except Exception:
                raise DocError("nopdf")
            rd = PdfReader(io.BytesIO(data))
            if getattr(rd, "is_encrypted", False):
                try:
                    rd.decrypt("")
                except Exception:
                    raise DocError("bad")
            for pg in rd.pages:
                pages.append((pg.extract_text() or "").strip())
        elif ext == "docx":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                xml = z.read("word/document.xml").decode("utf8", "ignore")
            xml = re.sub(r"</w:p>", "\n", xml)
            xml = re.sub(r"<w:tab/>", "\t", xml)
            xml = re.sub(r"<[^>]+>", "", xml)
            import html
            pages = [html.unescape(xml).strip()]
        elif ext in ("txt", "md", "csv", "log"):
            for enc in ("utf-8-sig", "utf-16", "latin-1"):
                try:
                    pages = [data.decode(enc)]
                    break
                except Exception:
                    continue
        else:
            raise DocError("type")
    except DocError:
        raise
    except Exception:
        raise DocError("bad")
    pages = [re.sub(r"[ \t]+", " ", p).strip() for p in pages]
    if not any(pages):
        raise DocError("empty")
    total = 0
    out = []
    for p in pages:
        out.append(p[: max(0, MAX_CHARS - total)])
        total += len(out[-1])
    return out


def full_text(pages):
    return "\n\n".join(f"[Page {i}]\n{p}" if len(pages) > 1 else p for i, p in enumerate(pages, 1) if p)


# ---------- sentences ----------
_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9\"'(\[])|\n{2,}|\n(?=[-•*\d]+[.)]?\s)")


def sentences(pages):
    """[(page_no, sentence)] with very short fragments removed."""
    out = []
    for pn, p in enumerate(pages, 1):
        for s in _SPLIT.split(p.replace("\r", "")):
            s = re.sub(r"\s+", " ", s).strip()
            if 25 <= len(s) <= 600:
                out.append((pn, s))
    return out


_STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been being it its this that these those i you he she we they them his her our your their my me not no so do does did
have has had will would can could may might must shall should than then there here which who whom what when where why how also into about over under more most such only very can per via
le la les un une des du de d l et ou mais si en au aux pour par avec sans sur sous dans est sont etait etre a ont ce cet cette ces je tu il elle nous vous ils elles mon ma mes ton ta tes son sa ses notre votre leur ne pas plus que qui quoi dont ou comme aussi tres
na ni ya wa kwa cha vya za la pa ku mu ya ili au lakini kama katika huu hii hiki hizi huo hao wao sisi wewe yeye mimi sana pia tu bado kuwa alikuwa
n' y' w' b' i' u' ku mu mu mu cyangwa ariko niba mu ya na ni bya bwa rya rwa cya ikigo uyu iyi iki aba abo ibyo iryo uko aho kandi nta si
""".split())


def _tokens(s):
    return [w for w in re.findall(r"[a-z0-9]+", fold(s)) if w not in _STOP and len(w) > 2]


def summarize(pages, n=5):
    """Extractive summary: the n highest-scoring sentences, in document order. Returns [(page, sentence)]."""
    sents = sentences(pages)
    if not sents:
        return []
    freq = Counter(w for _, s in sents for w in _tokens(s))
    if not freq:
        return sents[:n]
    top = max(freq.values())
    scored = []
    for idx, (pn, s) in enumerate(sents):
        toks = _tokens(s)
        if not toks:
            continue
        score = sum(freq[w] / top for w in set(toks)) / math.sqrt(len(toks) + 4)
        if idx < 3:
            score *= 1.25   # openings often state the purpose
        scored.append((score, idx))
    pick = sorted(i for _, i in sorted(scored, reverse=True)[:n])
    return [sents[i] for i in pick]


# ---------- key details ----------
_MONTHS = r"jan(?:uary|vier|uari)?|feb(?:ruary|vrier|ruari)?|mar(?:ch|s|ch)?|apr(?:il)?|avr(?:il)?|may|mai|jun(?:e)?|juin|jul(?:y)?|juil(?:let)?|aug(?:ust)?|aout|sep(?:t(?:ember|embre)?)?|oct(?:ober|obre)?|nov(?:ember|embre)?|dec(?:ember|embre)?|desemba|novemba|oktoba|septemba|agosti|julai|juni|aprili|mei|machi|februari|januari"
_PATTERNS = {
    "dates": [re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), re.compile(r"\b\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}\b"),
              re.compile(r"\b\d{1,2}(?:st|nd|rd|th|er)?\s+(?:de\s+)?(?:" + _MONTHS + r")[a-z]*\.?,?\s+\d{4}\b", re.I),
              re.compile(r"\b(?:" + _MONTHS + r")[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b", re.I)],
    "money": [re.compile(r"(?:RWF|FRW|Frw|USD|EUR|KES|UGX|TZS|US\$|\$|€|£)\s?\d[\d,. ]*\d|\b\d[\d,. ]*\d\s?(?:RWF|FRW|Frw|USD|EUR|KES|UGX|TZS|dollars|euros|francs)\b", re.I)],
    "percent": [re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|percent|per cent|pour cent)")],
    "emails": [re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")],
    "phones": [re.compile(r"(?<![\w/])\+?\d{1,3}[ \-]?\(?\d{2,4}\)?[ \-]?\d{3}[ \-]?\d{3,4}(?![\w/])")],
    "links": [re.compile(r"\bhttps?://[^\s<>\")]+|\bwww\.[^\s<>\")]+", re.I)],
}
_DEADLINE = re.compile(r"\b(deadline|due|no later than|before|by the end of|expires?|expiry|valid until|must be|required|penalty|date limite|avant le|au plus tard|echeance|expire|obligatoire|tarehe ya mwisho|mwisho wa|kabla ya|lazima|itariki ntarengwa|bitarenze|agomba|ni itegeko)\b", re.I)
LABELS = {
    "dates": {"en": "Dates", "fr": "Dates", "rw": "Amatariki", "sw": "Tarehe"},
    "money": {"en": "Amounts of money", "fr": "Montants", "rw": "Amafaranga", "sw": "Kiasi cha pesa"},
    "percent": {"en": "Percentages", "fr": "Pourcentages", "rw": "Ijanisha", "sw": "Asilimia"},
    "emails": {"en": "Email addresses", "fr": "Adresses e-mail", "rw": "Imeri", "sw": "Barua pepe"},
    "phones": {"en": "Phone-like numbers", "fr": "Numéros de téléphone (possibles)", "rw": "Nomero zisa na telefone", "sw": "Namba zinazofanana na simu"},
    "links": {"en": "Links", "fr": "Liens", "rw": "Imirongo (links)", "sw": "Viungo"},
    "deadline": {"en": "Sentences about deadlines, conditions or obligations", "fr": "Phrases sur délais, conditions ou obligations", "rw": "Interuro zivuga ku matariki ntarengwa, ibisabwa cyangwa inshingano", "sw": "Sentensi kuhusu tarehe za mwisho, masharti au wajibu"},
}


def key_details(pages, limit=12):
    """{'dates': [...], 'money': [...], ... 'deadline': [(page, sentence)]} : only strings that really occur in the text."""
    text = "\n".join(pages)
    found = {}
    for key, pats in _PATTERNS.items():
        seen, items = set(), []
        for p in pats:
            for m in p.finditer(text):
                v = m.group().strip(" .,;")
                if v.lower() not in seen and len(v) >= 3:
                    seen.add(v.lower()); items.append(v)
        if key == "phones":
            items = [v for v in items if len(re.sub(r"\D", "", v)) >= 9]
        found[key] = items[:limit]
    found["deadline"] = [(pn, s) for pn, s in sentences(pages) if _DEADLINE.search(s)][:limit]
    return found


# ---------- question answering (retrieval) ----------
def answer(question, pages, n=3):
    """Passages of the document most relevant to the question: [(score, page, passage)]. Empty list = nothing relevant found."""
    qt = set(_tokens(question))
    if not qt:
        return []
    sents = sentences(pages)
    if not sents:
        return []
    df = Counter()
    for _, s in sents:
        for w in set(_tokens(s)):
            df[w] += 1
    N = len(sents)
    scored = []
    for i, (pn, s) in enumerate(sents):
        toks = set(_tokens(s))
        # stem-lite: also match on 5-letter prefixes (plural/verb endings in en/fr/sw)
        hit = {w for w in qt if w in toks or any(len(w) >= 5 and len(t) >= 5 and t[:5] == w[:5] for t in toks)}
        if not hit:
            continue
        score = sum(math.log(1 + N / (1 + df.get(w, 0))) for w in hit) / math.sqrt(len(qt))
        scored.append((score, i))
    scored.sort(reverse=True)
    out = []
    used = set()
    for score, i in scored[: n * 3]:
        if any(abs(i - j) <= 1 for j in used):
            continue
        used.add(i)
        pn = sents[i][0]
        ctx = " ".join(s for _, s in sents[max(0, i - 0): i + 2] if True)
        out.append((round(score, 2), pn, sents[i][1]))
        if len(out) == n:
            break
    # a single weak keyword match is not an answer
    if out and out[0][0] < 0.9 and len(qt) >= 3:
        return []
    return out


HEAD = {
    "summary": {"en": "Summary (sentences taken from your document)", "fr": "Résumé (phrases tirées de votre document)", "rw": "Incamake (interuro zavanywe mu nyandiko yawe)", "sw": "Muhtasari (sentensi zilizotolewa kwenye hati yako)"},
    "details": {"en": "Key details found in the text", "fr": "Détails clés trouvés dans le texte", "rw": "Amakuru y'ingenzi yabonetse mu nyandiko", "sw": "Maelezo muhimu yaliyopatikana kwenye maandishi"},
    "answer": {"en": "What the document says about this", "fr": "Ce que dit le document à ce sujet", "rw": "Icyo inyandiko ivuga kuri ibi", "sw": "Hati inasema nini kuhusu hili"},
    "none": {"en": "I could not find this in the document. It may use different words, or the document may not say it. Try other keywords from the document.",
             "fr": "Je n'ai pas trouvé cela dans le document. Il utilise peut-être d'autres mots, ou ne le dit pas. Essayez d'autres mots du document.",
             "rw": "Sinabibonye muri iyi nyandiko. Ishobora gukoresha andi magambo, cyangwa ntibivugwamo. Gerageza andi magambo yo mu nyandiko.",
             "sw": "Sikuipata hii kwenye hati. Inaweza kutumia maneno mengine, au haisemi. Jaribu maneno mengine kutoka kwenye hati."},
    "page": {"en": "page", "fr": "page", "rw": "paji", "sw": "ukurasa"},
    "note": {"en": "_This is an automatic extract: it quotes your document and may miss context. Check important points in the original. For a fuller explanation, tick “Use AI on this document” (needs the AI key)._",
             "fr": "_Ceci est un extrait automatique : il cite votre document et peut manquer de contexte. Vérifiez les points importants dans l'original. Pour une explication plus complète, cochez « Utiliser l'IA sur ce document » (clé IA requise)._",
             "rw": "_Iyi ni incamake yikora: ivuga ibiri mu nyandiko yawe kandi ishobora kubura imvano. Genzura ibyingenzi mu nyandiko y'umwimerere. Ushaka ibisobanuro byuzuye, hitamo «Koresha AI kuri iyi nyandiko» (bisaba urufunguzo rwa AI)._",
             "sw": "_Huu ni muhtasari wa kiotomatiki: unanukuu hati yako na unaweza kukosa muktadha. Hakiki mambo muhimu kwenye asili. Kwa maelezo kamili, chagua «Tumia AI kwenye hati hii» (inahitaji ufunguo wa AI)._"},
    "nodetail": {"en": "No dates, amounts, emails or links were found.", "fr": "Aucune date, aucun montant, e-mail ou lien trouvé.", "rw": "Nta matariki, amafaranga, imeri cyangwa imirongo yabonetse.", "sw": "Hakuna tarehe, kiasi, barua pepe au viungo vilivyopatikana."},
}


def render_summary(pages, lang, n=5):
    items = summarize(pages, n)
    if not items:
        return HEAD["none"][lang]
    multi = len(pages) > 1
    lines = [f"**{HEAD['summary'][lang]}**", ""]
    for pn, s in items:
        lines.append(f"- {s}" + (f" ({HEAD['page'][lang]} {pn})" if multi else ""))
    return "\n".join(lines) + "\n\n" + HEAD["note"][lang]


def render_details(pages, lang):
    d = key_details(pages)
    multi = len(pages) > 1
    lines = [f"**{HEAD['details'][lang]}**", ""]
    any_ = False
    for key in ("dates", "money", "percent", "emails", "phones", "links"):
        if d[key]:
            any_ = True
            lines.append(f"*{LABELS[key][lang]}:* " + "; ".join(d[key]))
    if d["deadline"]:
        any_ = True
        lines.append(f"\n*{LABELS['deadline'][lang]}:*")
        lines += [f"- {s}" + (f" ({HEAD['page'][lang]} {pn})" if multi else "") for pn, s in d["deadline"]]
    if not any_:
        return HEAD["nodetail"][lang]
    return "\n".join(lines) + "\n\n" + HEAD["note"][lang]


def render_answer(question, pages, lang):
    hits = answer(question, pages)
    if not hits:
        return HEAD["none"][lang]
    multi = len(pages) > 1
    lines = [f"**{HEAD['answer'][lang]}**", ""]
    lines += [f"> {s}" + (f"  \n> ({HEAD['page'][lang]} {pn})" if multi else "") for _, pn, s in hits]
    return "\n".join(lines) + "\n\n" + HEAD["note"][lang]
