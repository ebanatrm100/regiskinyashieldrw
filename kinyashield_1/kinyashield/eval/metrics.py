"""Dependency-free BLEU (sentence, smoothed) and chrF, so translation quality can be scored without installing sacrebleu.
For publishable numbers use sacrebleu on the same files; these are close but not identical to its output."""
import math
from collections import Counter


def _ngrams(tokens, n):
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def tokenize(text):
    out, cur = [], ""
    for ch in (text or "").lower():
        if ch.isalnum() or ch in "'’":
            cur += ch
        else:
            if cur: out.append(cur); cur = ""
            if not ch.isspace(): out.append(ch)
    if cur: out.append(cur)
    return out


def bleu(hyp, ref, max_n=4):
    h, r = tokenize(hyp), tokenize(ref)
    if not h or not r:
        return 0.0
    logs = 0.0
    for n in range(1, max_n + 1):
        hn, rn = _ngrams(h, n), _ngrams(r, n)
        total = max(sum(hn.values()), 0)
        match = sum(min(c, rn[g]) for g, c in hn.items())
        logs += math.log((match + 1) / (total + 1))          # add-one smoothing
    bp = 1.0 if len(h) > len(r) else math.exp(1 - len(r) / len(h))
    return 100.0 * bp * math.exp(logs / max_n)


def _chars(text, n):
    s = "".join((text or "").split())
    return Counter(s[i:i + n] for i in range(len(s) - n + 1))


def chrf(hyp, ref, max_n=6, beta=2.0):
    ps, rs = [], []
    for n in range(1, max_n + 1):
        h, r = _chars(hyp, n), _chars(ref, n)
        if not h or not r:
            continue
        m = sum(min(c, r[g]) for g, c in h.items())
        ps.append(m / sum(h.values())); rs.append(m / sum(r.values()))
    if not ps:
        return 0.0
    p, r = sum(ps) / len(ps), sum(rs) / len(rs)
    if p + r == 0:
        return 0.0
    return 100.0 * (1 + beta ** 2) * p * r / (beta ** 2 * p + r)


def corpus(hyps, refs):
    n = max(len(hyps), 1)
    return {"bleu": sum(bleu(h, r) for h, r in zip(hyps, refs)) / n,
            "chrf": sum(chrf(h, r) for h, r in zip(hyps, refs)) / n, "n": len(hyps)}
