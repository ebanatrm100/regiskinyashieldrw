"""KinyaShield RW detector: transparent rules with context handling, four languages.

Text is accent-folded character by character (positions never shift), then every
rule's patterns (all languages) are applied. Returns exact evidence spans, the
reason, and safe next steps. It never claims a message is safe or proves a scam.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Tuple

from safety_rules import (RULES, PROTECTIVE_PREFIX, GENERAL_ADVICE, LANG_MARKERS,
                          VERDICTS, NO_GUARANTEE, LANGS)

# ASCII flag: \b and \w behave exactly like in the browser (JavaScript) version.
FLAGS = re.IGNORECASE | re.ASCII


@dataclass
class Finding:
    rule_id: str
    severity: str
    title: dict
    why: dict
    advice: dict
    evidence: List[Tuple[int, int, str]] = field(default_factory=list)


@dataclass
class Result:
    verdict: str
    language: str
    findings: List[Finding]
    protective: List[Tuple[int, int, str]]
    text: str          # original text (for display)
    folded: str        # accent-folded text (what rules matched on)

    @property
    def label(self):
        return VERDICTS[self.verdict]["en"]

    @property
    def predicted_suspicious(self):
        return self.verdict != "ok"


def fold(text):
    """Remove accents one character at a time so string positions stay identical."""
    out = []
    for ch in (text or ""):
        if ch in "\u2019\u2018":
            out.append("'")
            continue
        if ch in "\u00a0\u202f":
            out.append(" ")
            continue
        d = "".join(c for c in unicodedata.normalize("NFD", ch) if not unicodedata.combining(c))
        out.append(d if len(d) == 1 else ch)
    return "".join(out)


def detect_language(folded):
    t = " " + re.sub(r"[^a-z0-9' ]+", " ", folded.lower()) + " "
    best, best_n = "en", 1
    for lang in LANGS:
        n = sum(1 for m in LANG_MARKERS[lang] if " " + m + " " in t)
        if n > best_n:
            best, best_n = lang, n
    return best


def _sentence_prefix(text, start):
    last = 0
    for m in re.finditer(r"[.!?\n]\s", text[:start]):
        last = m.end()
    return text[last:start]


def _sentence(text, start, end):
    first = 0
    for m in re.finditer(r"[.!?\n]\s", text[:start]):
        first = m.end()
    nxt = re.search(r"[.!?\n]\s", text[end:])
    return text[first:end + nxt.start() + 1] if nxt else text[first:]


def _benign_context(folded, start, end, rule):
    """True when the sentence reads as a genuine achievement, not a scam (see rule 'unless'/'keep_if')."""
    sent = _sentence(folded, start, end)
    if not any(re.search(p, sent, FLAGS) for p in rule["unless"]):
        return False
    return not any(re.search(p, sent, FLAGS) for p in rule.get("keep_if", []))


def _protective(folded, start):
    prefix = _sentence_prefix(folded, start).lower()
    for pats in PROTECTIVE_PREFIX.values():
        for p in pats:
            if re.search(p, prefix, FLAGS):
                return True
    return False


def analyze(raw_text):
    original = raw_text or ""
    folded = fold(original)
    lang = detect_language(folded)
    findings, protective = [], []
    for rule in RULES:
        spans = []
        if "groups" in rule:
            # combination rule: every group must match somewhere in the message
            found = []
            for group in rule["groups"]:
                hit = None
                for pats in group.values():
                    for pat in pats:
                        m = re.search(pat, folded, FLAGS)
                        if m and (hit is None or m.start() < hit[0]):
                            hit = (m.start(), m.end(), original[m.start():m.end()])
                if hit is None:
                    found = []
                    break
                found.append(hit)
            spans.extend(found)
        else:
            for pats in rule["patterns"].values():
                for pat in pats:
                    for m in re.finditer(pat, folded, FLAGS):
                        if rule["suppress_if_protective"] and _protective(folded, m.start()):
                            protective.append((m.start(), m.end(), original[m.start():m.end()]))
                            continue
                        if rule.get("unless") and _benign_context(folded, m.start(), m.end(), rule):
                            continue
                        spans.append((m.start(), m.end(), original[m.start():m.end()]))
        if spans:
            findings.append(Finding(rule["id"], rule["severity"], rule["title"], rule["why"],
                                    rule["advice"], sorted(set(spans))))
    highs = sum(f.severity == "high" for f in findings)
    meds = sum(f.severity == "medium" for f in findings)
    lows = sum(f.severity == "low" for f in findings)
    nonlow = highs + meds
    if highs >= 2 or (highs >= 1 and (nonlow >= 2 or lows >= 1)) or (meds >= 2 and lows >= 1):
        verdict = "high"
    elif nonlow >= 1:
        verdict = "verify"
    else:
        verdict = "ok"
    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: order[f.severity])
    return Result(verdict, lang, findings, protective, original, folded)


def highlight_spans(result):
    """Merged (start, end, severity) spans for display; low findings are skipped."""
    spans = []
    for f in result.findings:
        if f.severity == "low":
            continue
        for s, e, _ in f.evidence:
            spans.append((s, e, f.severity))
    spans.sort()
    merged = []
    for s, e, sev in spans:
        if merged and s <= merged[-1][1]:
            ps, pe, psev = merged[-1]
            merged[-1] = (ps, max(pe, e), "high" if "high" in (psev, sev) else psev)
        else:
            merged.append((s, e, sev))
    return merged


def next_steps(result, lang="en"):
    steps = []
    for f in result.findings:
        if f.severity != "low" and f.advice[lang] not in steps:
            steps.append(f.advice[lang])
    for g in GENERAL_ADVICE[lang]:
        if g not in steps:
            steps.append(g)
    return steps
