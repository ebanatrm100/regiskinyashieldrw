"""Compare two cybersecurity terms: "difference between a virus and a worm", "red team vs blue team", "encryption versus hashing",
"différence entre phishing et smishing", "itandukaniro hagati ya virus na worm", "tofauti kati ya virus na worm", "compare X and Y".
find(question, lang) -> a guide-shaped entry with both terms side by side (meaning, where used, what to do), or None when the question is not a comparison
or either side is not a known glossary term. Uses only the glossary (cyber_db); it never invents a difference."""
from __future__ import annotations
import re
from textutil import fold, entry, LANGS
import cyber_db as C

_LEAD = r"(?:what(?:'s| is| are)?\s+(?:the\s+)?|quelle(?:s)? (?:est|sont) (?:la |les )?|qu'est[- ]ce que |ni iki |ni ikihe |nini |ni ipi )?"
_PATTERNS = [
    re.compile(r"^" + _LEAD + r"(?:differences?|difference|distinction|diff)\s+(?:between|entre|hagati ya|kati ya|of)\s+(?P<a>.+?)\s+(?:and|et|na|vs\.?|versus|or|ou|au)\s+(?P<b>.+)$"),
    re.compile(r"^" + _LEAD + r"(?:itandukaniro hagati ya|itandukaniro rya|itandukaniro|tofauti kati ya|tofauti ya)\s+(?P<a>.+?)\s+(?:and|et|na|vs\.?|versus|au|ama)\s+(?P<b>.+)$"),
    re.compile(r"^(?:compare|comparer|compare[zr]?|gereranya|linganisha|compare between)\s+(?P<a>.+?)\s+(?:and|et|na|with|avec|to|a|vs\.?|versus|au)\s+(?P<b>.+)$"),
    re.compile(r"^(?P<a>.+?)\s+(?:vs\.?|versus|compared (?:to|with)|contre|or)\s+(?P<b>.+?)(?:\s+(?:difference|differences|compared|comparison|difference\?))?$"),
    re.compile(r"^(?:is|est[- ]ce que)\s+(?:a |an |the |un |une |le |la )?(?P<a>.+?)\s+(?:the same as|same as|different from|different than|identique a|la meme chose que|pareil que|is the same as)\s+(?:a |an |the |un |une |le |la )?(?P<b>.+)$"),
]
_STRIP = re.compile(r"^(?:a|an|the|un|une|le|la|les|l'|des|ni|iyo)\s+|\s+(?:attack|attacks|attaque|attaques|software|logiciel|malware|ibitero|shambulio)$")


def _side(s):
    s = fold(s).strip(" ?.!,")
    for _ in range(2):
        s = _STRIP.sub("", s).strip()
    return s


_ALIAS = {"virus": "computer virus", "worm": "computer worm", "worms": "computer worm", "viruses": "computer virus", "ver": "computer worm", "ver informatique": "computer worm",
          "2fa": "two-factor authentication", "dos": "denial-of-service (dos) attack", "ddos": "distributed denial-of-service (ddos)", "pentest": "penetration testing (pentest)",
          "penetration test": "penetration testing (pentest)", "vulnerability scan": "vulnerability scanning", "hashing": "hashing", "iam": "identity and access management (iam)",
          "authn": "authentication", "authz": "authorization", "authorisation": "authorization", "cert": "digital certificate", "ids": "intrusion detection system (ids)", "ips": "intrusion prevention system (ips)"}


def _row(s):
    for cand in (_ALIAS.get(s, s), s, s.replace("-", " "), s.replace(" ", "-"), re.sub(r"s$", "", s)):
        r = C.lookup(cand)
        if r:
            return r
    return None


def find(question, lang="en"):
    q = fold(question).strip(" ?.!")
    if not q or len(q) > 140:
        return None
    for rx in _PATTERNS:
        m = rx.match(q)
        if not m:
            continue
        a, b = _row(_side(m.group("a"))), _row(_side(m.group("b")))
        if a and b and a[0] != b[0]:
            return _build(a, b)
        return None
    return None


_LAB = {"en": ("Where each is used and what to do", "Compare: "), "fr": ("Où on les rencontre et que faire", "Comparer : "),
        "rw": ("Aho bikoreshwa n'icyo gukora", "Gereranya: "), "sw": ("Mahali vinapotumika na cha kufanya", "Linganisha: ")}
_J = {"en": 6, "fr": 8, "rw": 10, "sw": 12}


def _name(r, l):
    local = (r[5] or {}).get(l) if l != "en" else None
    return r[1] + (f" — {local}" if local else "")


def _build(a, b):
    title, answer, steps, label = {}, {}, {}, {}
    for l in LANGS:
        j = _J[l]
        title[l] = f"{_LAB[l][1]}{a[1]} / {b[1]}"
        answer[l] = f"**{_name(a, l)}**: {a[j]}\n\n**{_name(b, l)}**: {b[j]}"
        steps[l] = [f"**{a[1]}**: {a[j + 1]}", f"**{b[1]}**: {b[j + 1]}"]
        label[l] = _LAB[l][0]
    e = entry("cybercmp_" + a[0] + "_" + b[0], "cyber", title, answer, steps, label)
    e["photo_query"] = a[4]
    e["priority"] = True
    return e
