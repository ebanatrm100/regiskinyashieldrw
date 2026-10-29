"""Helpers shared by the generated quiz sets (quiz_cyber_gen.py, quiz_net.py): seeded shuffling and four-language question templates."""
import random, re

LANGS = ("en", "fr", "rw", "sw")


def rnd(seed):
    return random.Random(seed)


def place(r, correct, wrong):
    """(options, answer_index): the correct option and the wrong ones in a seeded random order."""
    wrong = [w for w in dict.fromkeys(wrong) if w != correct]
    assert len(wrong) >= 2, (correct, wrong)
    opts = list(wrong) + [correct]
    r.shuffle(opts)
    return opts, opts.index(correct)


def L(en, fr, rw, sw):
    return (en, fr, rw, sw)


_STOP = set("the a an and or of to in on for with from by as at is are be this that these those its their your our into over under using use used via per vs".split())


def tokens(name):
    """Significant words (4+ letters) and acronyms (3+ letters in capitals or in brackets) of a term name."""
    out = set()
    for m in re.finditer(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9\-+/']*", name or ""):
        w = m.group(0).strip("-'/")
        lw = w.lower()
        if lw in _STOP:
            continue
        if len(w) >= 4 or (len(w) >= 3 and w.isupper()):
            out.add(lw)
    return out


def mask(text, toks, phrases=()):
    for p in phrases:
        p = re.sub(r"\s*\(.*?\)", "", p or "").strip()
        if len(p) >= 4:
            text = re.sub(re.escape(p), "____", text, flags=re.I)
    """Replace every word that starts with one of the tokens by ____ so a description never gives away its own answer."""
    if not toks:
        return text
    rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toks, key=len, reverse=True)) + r")[\wÀ-ÿ'’-]*", re.I)
    return rx.sub("____", text)


def jaccard(a, b):
    a, b = set(re.findall(r"[a-z]{4,}", a.lower())), set(re.findall(r"[a-z]{4,}", b.lower()))
    return len(a & b) / max(1, len(a | b))
