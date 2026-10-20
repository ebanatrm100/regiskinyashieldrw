"""Understand the real problem: work out what the person is trying to achieve, how urgent it is, how they feel,
and whether the request is too vague to answer well. Pure Python, four languages, no network.

Two uses:
  1. clarify(question, lang): a too-vague opener ("help", "I have a problem", "write something") gets one short question with
     clear choices instead of a generic or wrong answer (offline, instant).
  2. hint(intent, lang): a short brief added to the AI's instructions (task type, urgency, emotion), so the AI answers the goal behind the words.
Keyword rules are transparent and deliberately modest; they only steer, and the AI is told to correct them when the message says otherwise."""
from __future__ import annotations
from dataclasses import dataclass, field
from textutil import fold, has_phrase, lk, entry, LANGS

TASKS = {
    "write": ["write", "draft", "compose", "rewrite", "proofread", "improve my", "cover letter", "cv", "resume", "email", "ecris", "redige", "andika", "tunga", "barua", "ibaruwa", "lettre"],
    "learn": ["explain", "teach", "understand", "how does", "why does", "help me learn", "study", "homework", "exam", "expliquer", "comprendre", "apprendre", "sobanura", "nsobanurira", "kwiga", "eleza", "nielewe", "jifunza"],
    "fix": ["not working", "doesn't work", "does not work", "error", "broken", "stuck", "failed", "can't", "cannot", "won't", "ne marche pas", "panne", "ntikora", "sikorera", "haifanyi kazi", "imeshindwa", "bug"],
    "decide": ["should i", "which is better", "best way to", "what should i do", "is it worth", "advice", "dois-je", "quel est le meilleur", "nkore iki", "nakora iki", "nifanye nini", "nifanye vipi", "ni iyihe nziza"],
    "verify": ["is this real", "is it real", "is this a scam", "is it safe", "legit", "genuine", "fake", "suspicious", "est-ce une arnaque", "est-ce fiable", "ni ukuri", "ni uburiganya", "ni ubutekamutwe", "ni kweli", "ni ulaghai", "ni salama"],
    "translate": ["translate", "in kinyarwanda", "in french", "in swahili", "in english", "traduis", "traduire", "humura", "bivuga gute", "tafsiri", "ina maana gani"],
    "calculate": ["calculate", "compute", "solve", "how much", "how many", "percentage", "convert", "calcule", "combien", "bara", "kubara", "hesabu", "ngapi"],
}

URGENT = {
    "en": ["hacked", "stolen", "scammed", "i sent money", "i gave my pin", "i shared my pin", "i shared my otp", "i clicked", "i installed", "money is gone", "lost money", "blackmail", "blackmailing", "threaten", "emergency", "right now", "urgent", "account taken", "locked out", "ransom"],
    "fr": ["pirate", "vole", "arnaque", "j'ai envoye de l'argent", "j'ai donne mon pin", "j'ai clique", "j'ai installe", "argent perdu", "chantage", "urgence", "tout de suite", "bloque", "rancon"],
    "rw": ["yaribwe", "yibwe", "natekewe", "natekewe umutwe", "nohereje amafaranga", "nahaye pin", "nasangije kode", "nakanze", "nashyizeho", "amafaranga yanjye yagiye", "iterabwoba", "byihutirwa", "ubu nonaha", "konti yanjye yafashwe", "yafunzwe"],
    "sw": ["imedukuliwa", "imeibiwa", "nimetapeliwa", "nilituma pesa", "nilitoa pin", "nilishiriki msimbo", "nilibonyeza", "nilisakinisha", "pesa zimepotea", "vitisho", "dharura", "sasa hivi", "haraka", "akaunti imechukuliwa", "imefungwa"],
}
BEGINNER = {
    "en": ["beginner", "i am new", "i'm new", "new to this", "simple words", "simple terms", "in simple", "explain like", "eli5", "for dummies", "i don't understand", "i do not understand", "i know nothing", "what does that mean", "i am a student", "layman"],
    "fr": ["debutant", "je suis nouveau", "mots simples", "simplement", "je ne comprends pas", "je ne connais rien", "pour les nuls"],
    "rw": ["natangiye", "ndi mushya", "mu magambo yoroshye", "yoroheje", "sinumva", "ntacyo menya", "ntabizi"],
    "sw": ["mwanzo", "mimi ni mgeni", "maneno rahisi", "kwa urahisi", "sielewi", "sijui chochote"],
}
EXPERT = {
    "en": ["technical", "in detail", "in depth", "advanced", "rigorous", "derive", "derivation", "protocol", "architecture", "implementation", "algorithm", "complexity", "specification", "rfc", "cryptographic", "asymptotic", "i am an engineer", "i'm an engineer", "i am a developer", "as a professional", "peer-reviewed"],
    "fr": ["technique", "en detail", "approfondi", "avance", "demontrer", "protocole", "architecture", "implementation", "algorithme", "je suis ingenieur", "je suis developpeur"],
    "rw": ["mu buryo bwa tekiniki", "birambuye", "ndi injeniyeri", "ndi umutekinisiye", "protocol", "architecture"],
    "sw": ["kiufundi", "kwa undani", "kina", "mhandisi", "msanidi programu", "protokali"],
}
DISTRESS = {
    "en": ["scared", "afraid", "panic", "panicking", "ashamed", "embarrassed", "desperate", "worried", "stressed", "i don't know what to do", "i do not know what to do", "please help", "i'm lost", "crying", "devastated"],
    "fr": ["peur", "paniq", "honte", "desespere", "inquiet", "stresse", "je ne sais pas quoi faire", "aidez-moi", "au secours"],
    "rw": ["mfite ubwoba", "ndumiwe", "mfite isoni", "nihebye", "mfite impungenge", "sinzi icyo gukora", "mfashe", "ntabaza"],
    "sw": ["naogopa", "hofu", "aibu", "nimekata tamaa", "wasiwasi", "sijui nifanye nini", "nisaidie tafadhali", "nimechanganyikiwa"],
}
# Openers that say almost nothing about the goal.
VAGUE = {
    "en": ["help", "help me", "i need help", "i have a problem", "i have a question", "can you help", "can you help me", "i need something", "something is wrong", "it is not working", "it's not working", "fix it", "write something", "do it", "what should i do", "i want to ask"],
    "fr": ["aide", "aidez-moi", "aide-moi", "j'ai besoin d'aide", "j'ai un probleme", "j'ai une question", "pouvez-vous m'aider", "ca ne marche pas", "ecris quelque chose", "que faire", "que dois-je faire"],
    "rw": ["mfasha", "ndashaka ubufasha", "mfite ikibazo", "nkeneye ubufasha", "ntabwo bikora", "ntikora", "nkore iki", "nakora iki", "ndashaka kubaza"],
    "sw": ["nisaidie", "naomba msaada", "nina tatizo", "nina swali", "haifanyi kazi", "nifanye nini", "naweza kuuliza", "ninahitaji msaada"],
}

_CLARIFY = {
    "en": ("Happy to help. To give you something useful rather than a guess, tell me which of these is closest:",
           ["I got a suspicious message, call or link and want to know if it is safe.", "Something already happened (I shared a code, sent money, was hacked, lost my phone).",
            "I need to write something (a CV, an email, an application, a report).", "I want to learn or understand a topic, or practise for a test.",
            "Something is not working (an app, an account, a phone).", "Something else: describe the situation in one or two sentences."],
           "Useful details: what you were trying to do, what happened instead, and what result you want."),
    "fr": ("Avec plaisir. Pour vous donner quelque chose d'utile plutôt qu'une supposition, dites-moi laquelle de ces situations est la plus proche :",
           ["J'ai reçu un message, un appel ou un lien suspect et je veux savoir s'il est sûr.", "Quelque chose s'est déjà passé (j'ai partagé un code, envoyé de l'argent, été piraté, perdu mon téléphone).",
            "Je dois écrire quelque chose (CV, e-mail, candidature, rapport).", "Je veux apprendre ou comprendre un sujet, ou m'entraîner pour un examen.",
            "Quelque chose ne marche pas (une appli, un compte, un téléphone).", "Autre chose : décrivez la situation en une ou deux phrases."],
           "Détails utiles : ce que vous essayiez de faire, ce qui s'est passé à la place, et le résultat que vous voulez."),
    "rw": ("Ndagufasha. Kugira ngo mpe icyagufasha aho kugerageza, mbwira ikiri hafi y'ibi:",
           ["Nakiriye ubutumwa, guhamagarwa cyangwa link bikemangwa kandi ndashaka kumenya niba bitekanye.", "Hari ikimaze kuba (nasangije kode, nohereje amafaranga, natekewe umutwe, nabuze telefone).",
            "Nkeneye kwandika ikintu (CV, imeri, ibaruwa isaba akazi, raporo).", "Ndashaka kwiga cyangwa gusobanukirwa isomo, cyangwa kwitoza ikizamini.",
            "Hari ikidakora (porogaramu, konti, telefone).", "Ikindi: sobanura ikibazo mu nteruro imwe cyangwa ebyiri."],
           "Amakuru afasha: icyo wageragezaga gukora, ibyabaye, n'icyo ushaka kugeraho."),
    "sw": ("Nitafurahi kusaidia. Ili nikupe kitu cha manufaa badala ya kukisia, niambie lipi kati ya haya liko karibu zaidi:",
           ["Nimepokea ujumbe, simu au kiungo cha kutia shaka na nataka kujua kama ni salama.", "Kuna kitu kimeshatokea (nilishiriki msimbo, nilituma pesa, nilidukuliwa, nilipoteza simu).",
            "Nahitaji kuandika kitu (CV, barua pepe, ombi la kazi, ripoti).", "Nataka kujifunza au kuelewa mada, au kujizoeza mtihani.",
            "Kuna kitu hakifanyi kazi (programu, akaunti, simu).", "Jingine: eleza hali kwa sentensi moja au mbili."],
           "Maelezo yanayosaidia: ulichokuwa unajaribu kufanya, kilichotokea badala yake, na matokeo unayotaka."),
}


@dataclass
class Intent:
    task: str = "chat"
    urgent: bool = False
    distressed: bool = False
    vague: bool = False
    level: str = ""          # "beginner", "expert" or "" (unknown)
    signals: list = field(default_factory=list)


def analyze(question, history=None, lang="en") -> Intent:
    """history: previous chat messages (a vague message after real conversation is a follow-up, not an empty opener)."""
    q = fold(question)
    k = lk(lang)
    out = Intent()
    if not q:
        return out
    for l in LANGS:   # people mix languages, so every language's words are checked
        if has_phrase(q, [fold(w) for w in URGENT[l]]):
            out.urgent = True
        if has_phrase(q, [fold(w) for w in DISTRESS[l]]):
            out.distressed = True
    if has_phrase(q, [fold(w) for l in LANGS for w in EXPERT[l]]):
        out.level = "expert"
    elif has_phrase(q, [fold(w) for l in LANGS for w in BEGINNER[l]]):
        out.level = "beginner"
    for task, words in TASKS.items():
        if has_phrase(q, [fold(w) for w in words]):
            out.task = task
            break
    if not history and len(q.split()) <= 6:
        if any(q.strip(" .!?'") == fold(v).strip(" .!?'") for l in LANGS for v in VAGUE[l]):
            out.vague = True
    out.signals = [s for s, on in (("urgent", out.urgent), ("distressed", out.distressed), ("vague", out.vague)) if on]
    return out


def clarify(question, lang="en"):
    """Guide-shaped entry that asks what the person needs, or None when the opener is not vague."""
    it = analyze(question, None, lang)
    if not it.vague:
        return None
    k = lk(lang)
    intro, options, tip = _CLARIFY[k]
    ans = {l: _CLARIFY[l][0] + "\n\n" + "\n".join(f"- {o}" for o in _CLARIFY[l][1]) + "\n\n_" + _CLARIFY[l][2] + "_" for l in LANGS}
    title = {"en": "What do you need?", "fr": "De quoi avez-vous besoin ?", "rw": "Ukeneye iki?", "sw": "Unahitaji nini?"}
    return entry("intent_clarify", "intent", title, ans)


HINTS = {
    "write": "The person wants a piece of writing. Ask yourself who will read it and what they want that reader to do, then produce a complete ready-to-use draft with [placeholders], not advice about writing.",
    "learn": "The person wants to understand, not just receive facts. Find the gap in their understanding, start from what they likely know, use one concrete example, and finish with a quick check question.",
    "fix": "The person has something broken. Aim at getting it working again: likely causes ordered by probability, the quickest test for each, and what to try first. Ask for the error message or the exact step that fails if you need it.",
    "decide": "The person must choose or act. Give a clear recommendation with the main reason and the trade-off, state what would change it, and name the one fact you need if it is missing.",
    "verify": "The person wants to know whether something is real or safe. Give a clear leaning with the specific signs, how to verify independently through official channels, and what to do if they already acted.",
    "translate": "The person wants meaning carried across languages: natural wording in the right register, a note on tone or regional differences, and keep names, numbers and amounts unchanged.",
    "calculate": "The person wants a correct number they can use. Show the steps briefly, check the arithmetic, state units and assumptions, and give the final answer clearly.",
    "chat": "",
}


def hint(it: Intent) -> str:
    parts = []
    if HINTS.get(it.task):
        parts.append("Likely task: " + HINTS[it.task])
    if it.level == "beginner":
        parts.append("The person signals they are a beginner: use plain everyday words and short sentences, one idea at a time, explain every technical term in brackets the first time, and use a familiar everyday comparison.")
    elif it.level == "expert":
        parts.append("The person signals technical knowledge: be precise, use the correct terminology without over-explaining basics, include mechanisms, constraints and edge cases, and say where the evidence is weak.")
    if it.urgent:
        parts.append("URGENT: this may be an incident that is happening or just happened. Put the first protective actions at the very top (stop further loss, secure accounts, contact the bank or provider through official channels, keep evidence), before any explanation.")
    if it.distressed:
        parts.append("The person sounds worried or upset. Open with one calm sentence that acknowledges it without drama, say that this is common and fixable where true, then give clear small steps. Never blame them.")
    return "\n".join(parts)


CALM = {"en": "I'm sorry this happened. It is more common than people admit, it is not your fault, and there are steps that can limit the damage. Let's take them one by one.",
        "fr": "Je suis désolé que cela vous arrive. C'est plus courant qu'on ne le dit, ce n'est pas votre faute, et des mesures peuvent limiter les dégâts. Avançons pas à pas.",
        "rw": "Mbabajwe n'ibyakubayeho. Bibaho kenshi kurusha uko abantu babivuga, si wowe nyirabayazana, kandi hari intambwe zishobora kugabanya ibyangiritse. Tuzikurikire imwe imwe.",
        "sw": "Pole kwa yaliyotokea. Hutokea mara nyingi kuliko watu wanavyokubali, si kosa lako, na kuna hatua zinazoweza kupunguza madhara. Tuzichukue moja baada ya nyingine."}
TIME = {"en": "Time matters: do the first steps now, and phone your bank or provider on the number printed on your card or official website.",
        "fr": "Le temps compte : faites les premières étapes maintenant et appelez votre banque ou opérateur au numéro figurant sur votre carte ou son site officiel.",
        "rw": "Igihe ni ingenzi: kora intambwe za mbere ubu nonaha, uhamagare banki cyangwa umukoresha wawe kuri nimero iri ku ikarita yawe cyangwa ku rubuga rwemewe.",
        "sw": "Muda ni muhimu: chukua hatua za kwanza sasa, na mpigie benki au mtoa huduma wako kwa namba iliyo kwenye kadi yako au tovuti rasmi."}


def frame_guide_text(text, question, history=None, lang="en"):
    """Wrap an offline guide answer: a calm opening line when the person sounds distressed, a time reminder when it is urgent."""
    it = analyze(question, history, lang)
    k = lk(lang)
    if it.distressed:
        text = CALM[k] + "\n\n" + text
    if it.urgent:
        text = text + "\n\n**" + TIME[k] + "**"
    return text
