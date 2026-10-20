"""Communicate naturally: choose how simply or technically to explain, and explain unfamiliar words.
  detect(question, history)  -> "simple" | "standard" | "technical" (the person can override it with the selector in the chat tab)
  hint(level)                -> instruction for the AI
  add_glossary(text, ...)    -> appends short plain-language meanings of jargon found in an offline answer
Keyword-based and modest by design; the selector always wins. Pure Python, four languages."""
from __future__ import annotations
from textutil import fold, has_phrase, lk, LANGS
from register_data import GLOSSARY

LEVELS = ("simple", "standard", "technical")

BEGINNER = ["simple words", "simply", "like i'm 5", "like im 5", "eli5", "i don't understand", "i dont understand", "i do not understand", "i'm new", "i am new", "beginner", "i know nothing", "in plain words",
            "in plain english", "easy words", "not technical", "dumb it down", "what does that mean",
            "en termes simples", "je ne comprends pas", "debutant", "mots simples", "explique simplement",
            "mu magambo yoroshye", "ntabwo numva", "simbyumva", "sinumva", "nsobanurira byoroshye", "ndi mushya",
            "kwa maneno rahisi", "sielewi", "mimi ni mgeni", "nieleze kwa urahisi", "maneno rahisi"]
TECHNICAL = ["technical", "in detail", "in depth", "deep dive", "under the hood", "step by step technical", "for an expert", "i am an engineer", "i'm an engineer", "i am a developer", "i'm a developer",
             "techniquement", "en detail", "en profondeur", "je suis ingenieur", "je suis developpeur",
             "mu buryo bwa tekiniki", "birambuye", "ndi injeniyeri", "ndi umu developer",
             "kiufundi", "kwa undani", "mimi ni mhandisi", "mimi ni msanidi"]
JARGON = ["tcp", "udp", "tls", "ssl", "handshake", "regex", "kernel", "packet", "subnet", "cipher", "payload", "exploit", "cvss", "cve", "oauth", "jwt", "sha256", "sha-256", "rsa", "aes", "latency", "throughput",
          "xss", "sql injection", "csrf", "dns", "bgp", "iptables", "nmap", "metasploit", "reverse shell", "privilege escalation", "pentest", "siem", "mitre", "nist", "hmac", "pbkdf2", "bcrypt", "api", "endpoint",
          "docker", "kubernetes", "asymptotic", "eigenvalue", "lagrangian", "hamiltonian", "differential equation", "stochastic", "polymorphism", "recursion", "mutex", "idempotent"]


def detect(question, history=None):
    q = fold(question)
    past = " ".join(fold(m.get("content", "")) for m in (history or []) if m.get("role") == "user")
    blob = q + " | " + past
    if has_phrase(blob, [fold(w) for w in BEGINNER]):
        return "simple"
    if has_phrase(blob, [fold(w) for w in TECHNICAL]):
        return "technical"
    if sum(1 for j in JARGON if has_phrase(blob, [j])) >= 2:
        return "technical"
    return "standard"


HINTS = {
    "simple": ("AUDIENCE: a beginner. Use short sentences and everyday words, as if talking to a friend who has never studied the subject. Explain every technical or unfamiliar word the first time you use it, "
               "in a few plain words (for example: 'phishing (a fake message that tricks you)'). Use one familiar everyday comparison where it helps (market, farm, household). Give small steps, one idea at a time. No jargon, no acronyms without explanation."),
    "standard": ("AUDIENCE: a general reader. Use clear everyday language. The first time you use a technical term, give a short explanation in brackets. Keep it practical and well organised; do not oversimplify facts or talk down."),
    "technical": ("AUDIENCE: a technical reader. Use precise terminology without explaining basic terms; include mechanisms, conditions, edge cases, formulas or commands where they help, and name standards or specifications only when you are sure they exist. "
                  "Be concise and direct; skip beginner analogies. Still state assumptions and uncertainty."),
}
COMMON = ("COMMUNICATE NATURALLY: write the way a knowledgeable, kind person talks: direct, warm, no corporate filler, no lecture. Answer first, then explain. Match the person's language and level; if they switch, switch with them. "
          "Prefer concrete words over abstract ones. If you must use a term the person may not know, explain it right there instead of sending them elsewhere. Do not overwhelm: lead with the 2 or 3 things that matter most, offer to go deeper.")


def hint(level):
    return COMMON + "\n" + HINTS.get(level, HINTS["standard"])


TITLE = {"en": "Words explained", "fr": "Mots expliqués", "rw": "Amagambo asobanuwe", "sw": "Maneno yaliyofafanuliwa"}
_SKIP_KINDS = {"intent", "greeting", "owner", "name", "definition", "glossary"}


def terms_in(text, skip_text="", limit=4):
    """Glossary entries whose words appear in `text` (and not in skip_text, the question the person already asked about)."""
    t, s = fold(text), fold(skip_text)
    out = []
    for aliases, defs in GLOSSARY:
        al = [fold(a) for a in aliases]
        if has_phrase(t, al) and not has_phrase(s, al):
            out.append(defs)
        if len(out) >= limit:
            break
    return out


def add_glossary(text, level, question="", lang="en", kind=""):
    """Append 'Words explained' to an offline answer for beginners and general readers (not for technical readers)."""
    if level == "technical" or kind in _SKIP_KINDS:
        return text
    k = lk(lang)
    found = terms_in(text, question, limit=4 if level == "simple" else 3)
    if not found:
        return text
    return text + f"\n\n**{TITLE[k]}**\n" + "\n".join(f"- {d[k]}" for d in found)


LABEL = {"en": ("How should I explain?", ["Auto", "Simple", "Standard", "Technical"]),
         "fr": ("Comment dois-je expliquer ?", ["Auto", "Simple", "Standard", "Technique"]),
         "rw": ("Nsobanure nte?", ["Byikora", "Byoroshye", "Bisanzwe", "Bya tekiniki"]),
         "sw": ("Nieleze vipi?", ["Otomatiki", "Rahisi", "Kawaida", "Kitaalamu"])}


def label(lang):
    return LABEL[lk(lang)]


def level_from_choice(choice_index, question, history):
    """0 = auto, 1..3 = fixed level."""
    return LEVELS[choice_index - 1] if choice_index in (1, 2, 3) else detect(question, history)
