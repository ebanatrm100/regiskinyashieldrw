"""Multilingual support (offline part): a phrasebook of everyday, farming, money and digital-safety phrases in English, French, Kinyarwanda and Kiswahili,
with the natural wording people actually use (not word-for-word) and short usage notes. Pure Python.
The phrasebook is a curated list, not a full translator: other texts go to the AI, which is told to translate for meaning and politeness.
Kinyarwanda and Kiswahili are a draft for review by a fluent speaker."""
from __future__ import annotations
import re
from textutil import fold, has_phrase, lk, entry, LANGS

NAMES = {"en": {"en": "English", "fr": "French", "rw": "Kinyarwanda", "sw": "Swahili"},
         "fr": {"en": "anglais", "fr": "français", "rw": "kinyarwanda", "sw": "swahili"},
         "rw": {"en": "Icyongereza", "fr": "Igifaransa", "rw": "Ikinyarwanda", "sw": "Igiswahili"},
         "sw": {"en": "Kiingereza", "fr": "Kifaransa", "rw": "Kinyarwanda", "sw": "Kiswahili"}}
_ALIASES = {"en": ("english", "anglais", "icyongereza", "cyongereza", "kiingereza", "englais"), "fr": ("french", "francais", "igifaransa", "gifaransa", "kifaransa"),
            "rw": ("kinyarwanda", "ikinyarwanda", "kinyarwand", "rwanda language"), "sw": ("swahili", "kiswahili", "igiswahili", "giswahili", "swahili language")}

# (en, fr, rw, sw, note-en)
P = [
    ("Hello", "Bonjour", "Muraho", "Habari / Hujambo", "Greetings change with the time of day in Kinyarwanda (Mwaramutse = good morning, Mwiriwe = good afternoon/evening)."),
    ("Good morning", "Bonjour", "Mwaramutse", "Habari za asubuhi", ""),
    ("Good evening", "Bonsoir", "Mwiriwe", "Habari za jioni", ""),
    ("Good night", "Bonne nuit", "Murare neza", "Usiku mwema / Lala salama", ""),
    ("How are you?", "Comment allez-vous ?", "Amakuru?", "Habari yako? / U hali gani?", "In Kinyarwanda the usual answer is “Ni meza” (good). Use the plural “Mumeze mute?” for respect or several people."),
    ("I am fine", "Je vais bien", "Ndi muzima / Meze neza", "Sijambo / Nzuri", ""),
    ("Thank you", "Merci", "Murakoze", "Asante", "Murakoze is already polite (plural form); “Urakoze” is the informal singular."),
    ("Thank you very much", "Merci beaucoup", "Murakoze cyane", "Asante sana", ""),
    ("You are welcome", "De rien", "Nta kibazo / Ntacyo", "Karibu / Starehe", ""),
    ("Please", "S'il vous plaît", "Nyamuneka", "Tafadhali", ""),
    ("Excuse me", "Excusez-moi", "Mbabarira", "Samahani", "Also used for “sorry” in everyday speech."),
    ("I am sorry", "Je suis désolé(e)", "Mbabarira / Ndasaba imbabazi", "Samahani / Pole", "In Kiswahili “Pole” expresses sympathy (“sorry for your trouble”); “Samahani” apologises."),
    ("Yes", "Oui", "Yego", "Ndiyo", ""),
    ("No", "Non", "Oya", "Hapana", ""),
    ("Goodbye", "Au revoir", "Murabeho", "Kwa heri", ""),
    ("See you tomorrow", "À demain", "Ejo tuzabonana", "Tuonane kesho", ""),
    ("Welcome", "Bienvenue", "Murakaza neza", "Karibu / Karibuni", "Karibuni is the plural (several people)."),
    ("What is your name?", "Comment vous appelez-vous ?", "Witwa nde?", "Jina lako nani?", "For a respected person, Kiswahili: “Naomba kujua jina lako” (May I know your name)."),
    ("My name is ...", "Je m'appelle ...", "Nitwa ...", "Jina langu ni ...", ""),
    ("I don't understand", "Je ne comprends pas", "Sinumva", "Sielewi", ""),
    ("Please speak slowly", "Parlez lentement, s'il vous plaît", "Nyamuneka muvuge buhoro", "Tafadhali ongea polepole", ""),
    ("Please repeat", "Pouvez-vous répéter ?", "Mwabisubiramo?", "Tafadhali rudia", ""),
    ("Do you speak English?", "Parlez-vous anglais ?", "Mwavuga Icyongereza?", "Unaongea Kiingereza?", ""),
    ("Can you help me?", "Pouvez-vous m'aider ?", "Mwamfasha?", "Unaweza kunisaidia?", ""),
    ("I need help", "J'ai besoin d'aide", "Nkeneye ubufasha", "Ninahitaji msaada", ""),
    ("I am lost", "Je suis perdu(e)", "Nayobye", "Nimepotea", ""),
    ("Call the police", "Appelez la police", "Muhamagare Polisi", "Piga simu polisi", ""),
    ("I need a doctor", "J'ai besoin d'un médecin", "Nkeneye muganga", "Ninahitaji daktari", ""),
    ("Where is the toilet?", "Où sont les toilettes ?", "Ubwiherero buri he?", "Choo kiko wapi?", ""),
    ("Where is the bank?", "Où est la banque ?", "Banki iri he?", "Benki iko wapi?", ""),
    ("What time is it?", "Quelle heure est-il ?", "Ni saa ngahe?", "Ni saa ngapi?", ""),
    ("How much is this?", "Combien ça coûte ?", "Ibi ni angahe?", "Hii ni shilingi ngapi? / Bei gani?", "In shops you can also say “Ni angahe?” (How much?)."),
    ("It is too expensive", "C'est trop cher", "Birahenze cyane", "Ni ghali sana", ""),
    ("I would like to buy ...", "Je voudrais acheter ...", "Nshaka kugura ...", "Ningependa kununua ...", ""),
    ("Water", "Eau", "Amazi", "Maji", ""),
    ("Market", "Marché", "Isoko", "Soko", ""),
    ("I am hungry", "J'ai faim", "Ndashonje", "Nina njaa", ""),
    ("I am a farmer", "Je suis agriculteur / agricultrice", "Ndi umuhinzi / umuhinzi", "Mimi ni mkulima", ""),
    ("I am a student", "Je suis étudiant(e)", "Ndi umunyeshuri", "Mimi ni mwanafunzi", ""),
    ("Congratulations", "Félicitations", "Ndagushimiye", "Hongera", "In Kinyarwanda use “Mwishimiye” or “Ndabashimiye” for several people."),
    ("Happy birthday", "Joyeux anniversaire", "Isabukuru nziza", "Heri ya siku ya kuzaliwa", ""),
    ("Happy new year", "Bonne année", "Umwaka mushya muhire", "Heri ya mwaka mpya", ""),
    ("Good luck", "Bonne chance", "Amahirwe masa", "Bahati njema", ""),
    ("I agree", "Je suis d'accord", "Ndabyemeye", "Nakubali", ""),
    ("Never share your PIN", "Ne partagez jamais votre code PIN", "Ntuzigere usangiza undi muntu PIN yawe", "Usishiriki PIN yako na mtu yeyote kamwe", ""),
    ("Do not click suspicious links", "Ne cliquez pas sur les liens suspects", "Ntukande ku mirongo ikemangwa", "Usibofye viungo vinavyotia shaka", ""),
    ("Is this message real?", "Ce message est-il authentique ?", "Ubu butumwa ni ukuri?", "Je, ujumbe huu ni halisi?", ""),
    ("I will call you back", "Je vous rappelle", "Ndagusubiza kuri telefone", "Nitakupigia tena", ""),
    ("My phone number is ...", "Mon numéro de téléphone est ...", "Nomero yanjye ya telefone ni ...", "Namba yangu ya simu ni ...", ""),
]
_INDEX = {}
for i, row in enumerate(P):
    for j, l in enumerate(LANGS):
        for variant in row[j].split(" / "):
            key = fold(re.sub(r"\(.*?\)", "", variant)).strip(" ?.!")
            if key:
                _INDEX.setdefault(key, i)

_LAB = {"en": "Translations", "fr": "Traductions", "rw": "Ubusobanuro", "sw": "Tafsiri"}
_NOTE = {"en": "These are natural everyday phrases, not word-for-word translations. Kinyarwanda and Kiswahili are a draft: ask a fluent speaker to confirm important texts.",
         "fr": "Ce sont des phrases naturelles du quotidien, pas des traductions mot à mot. Le kinyarwanda et le swahili sont un brouillon : faites confirmer les textes importants par un locuteur.",
         "rw": "Ni interuro zisanzwe zikoreshwa, si ubusobanuro bw'ijambo ku rindi. Ikinyarwanda n'Igiswahili ni igerageza: saba umuvuga neza kwemeza inyandiko z'ingenzi.",
         "sw": "Hizi ni sentensi za kawaida za kila siku, si tafsiri neno kwa neno. Kinyarwanda na Kiswahili ni rasimu: mwombe mzungumzaji fasaha athibitishe maandishi muhimu."}
_NOTE_LAB = {"en": "Usage note", "fr": "Note d'usage", "rw": "Icyitonderwa", "sw": "Maelezo ya matumizi"}
_NOHIT = {"en": "I do not have that exact phrase in my phrasebook. For an accurate translation of your own text, tick “Always ask the AI”: it translates for meaning and politeness, and you should have important texts confirmed by a fluent speaker.",
          "fr": "Je n'ai pas cette phrase exacte dans mon lexique. Pour une traduction précise de votre texte, cochez « Toujours demander à l'IA » : elle traduit le sens et le niveau de politesse ; faites confirmer les textes importants.",
          "rw": "Iyi nteruro ntabwo iri mu gitabo cyanjye. Ushaka ubusobanuro nyabwo bw'inyandiko yawe, hitamo «Burigihe baza AI»: ibusobanura ku bw'ubusobanuro n'icyubahiro; saba kwemeza inyandiko z'ingenzi.",
          "sw": "Sina sentensi hiyo kamili kwenye kitabu changu. Kwa tafsiri sahihi ya maandishi yako, chagua «Muulize AI kila mara»: hutafsiri maana na heshima; thibitisha maandishi muhimu."}

_PATS = [
    re.compile(r"^(?:how (?:do|can) (?:you|i) say|how to say|how would you say|say|translate|translation of|what is|what's)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:in|into|to)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^(?:comment (?:dit|dire|on dit)[- ](?:on|t-on|ton)?|traduire|traduis|traduction de|comment dire)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:en|au|vers)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+(?:mu|bivuga iki mu|muri)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^(?:tafsiri|nitafsirie)\s+['\"]?(?P<p>.+?)['\"]?\s+(?:kwa|kuwa|kwenda)\s+(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+(?:ni nini|kwa)\s+(?:kwa\s+)?(?P<l>[a-z ]+?)\??$"),
    re.compile(r"^['\"]?(?P<p>.+?)['\"]?\s+in\s+(?P<l>[a-z ]+?)\??$"),
]


def _lang_of(word):
    w = fold(word).strip()
    for code, al in _ALIASES.items():
        if w in {fold(a) for a in al}:
            return code
    return None


def _render(i, target, k):
    row = P[i]
    order = [target] + [l for l in LANGS if l != target] if target else list(LANGS)
    lines = []
    for l in order:
        lines.append(f"- **{NAMES[k][l]}**: {row[LANGS.index(l)]}")
    ans = "\n".join(lines)
    note = row[4]
    return ans, note


def find(question, lang="en"):
    """Phrasebook answer for 'how do you say X in Kinyarwanda' / 'X in French' / 'translate X to Swahili' / 'common phrases'; else None."""
    k = lk(lang)
    q = fold(question).strip(" ?.!")
    if not q or len(q) > 140:
        return None
    # phrasebook list
    if has_phrase(q, ["phrasebook", "common phrases", "useful phrases", "basic phrases", "everyday phrases", "greetings in kinyarwanda", "phrases en kinyarwanda", "phrases courantes", "expressions courantes",
                      "interuro zisanzwe", "interuro z'ingenzi", "misemo ya kawaida", "sentensi za kawaida", "misemo ya kila siku"]):
        lines = [f"- **{r[LANGS.index(k)]}**  ·  " + "  ·  ".join(f"{r[LANGS.index(l)]}" for l in LANGS if l != k) for r in P[:26]]
        ttl = {"en": "Common phrases in four languages", "fr": "Phrases courantes en quatre langues", "rw": "Interuro zisanzwe mu ndimi enye", "sw": "Misemo ya kawaida katika lugha nne"}
        ans = {l: "\n".join(lines) + "\n\n" + _NOTE[l] for l in LANGS}
        return entry("phrasebook", "translate", ttl, ans)
    for pat in _PATS:
        m = pat.match(q)
        if not m:
            continue
        target = _lang_of(m.group("l"))
        if target is None:
            continue
        phrase = fold(re.sub(r"\(.*?\)", "", m.group("p"))).strip(" ?.!'\"")
        i = _INDEX.get(phrase)
        if i is None:
            return None   # not in the phrasebook: the AI (which translates for meaning) handles it when configured
        ans, note = _render(i, target, k)
        title = {l: f"“{P[i][LANGS.index(l)].split(' / ')[0]}” — {NAMES[l][target]}" for l in LANGS}
        # one language per answer would repeat the same table; build each language's text with that language's labels
        out = {}
        for l in LANGS:
            a, _ = _render(i, target, l)
            out[l] = f"**{_LAB[l]}** (→ {NAMES[l][target]}):\n\n{a}" + (f"\n\n*{_NOTE_LAB[l]}:* {note}" if note and l == "en" else "") + f"\n\n_{_NOTE[l]}_"
        return entry("translate_" + str(i), "translate", title, out)
    return None
