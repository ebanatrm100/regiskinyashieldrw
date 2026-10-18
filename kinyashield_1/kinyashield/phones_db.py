"""Mobile-phone brands for the AI Assistant (offline text, optional photos). Pure Python, no Streamlit.

What is stored: ~50 phone brands with the company that makes them, its home country, some well-known product lines and the phone software.
Only widely known facts are stored, nothing is invented; companies change (brands are sold, closed or merged), so the answer says to check the maker's own site for the newest models.
Texts are built from labelled fields (Manufacturer / Country / Notable lines / Software) in en/fr/rw/sw; the fr/rw/sw wording is a draft for fluent review.

Photos are NOT stored in the repo and no photo link is guessed. resolve_image() searches Wikimedia Commons (free-licence files only) for a photo of the
brand's phones and skips files whose name looks like a logo, icon, screenshot or shop picture; if nothing suitable is found, or there is no internet,
the text answer is shown alone with a note. The caption names the Commons file and links to its page, where author and licence are listed.
A found photo may show a different model of the same brand than the one you have in mind."""
from __future__ import annotations
import re, unicodedata
from urllib.parse import quote

LANGS = ("en", "fr", "rw", "sw")
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_PAGE = "https://commons.wikimedia.org/wiki/"

_COUNTRY = {  # key: (en, fr, rw, sw)
    "us": ("USA", "États-Unis", "Leta Zunze Ubumwe za Amerika", "Marekani"),
    "kr": ("South Korea", "Corée du Sud", "Koreya y'Epfo", "Korea Kusini"),
    "cn": ("China", "Chine", "Ubushinwa", "China"),
    "fi": ("Finland", "Finlande", "Finilande", "Ufini"),
    "jp": ("Japan", "Japon", "Ubuyapani", "Japani"),
    "tw": ("Taiwan", "Taïwan", "Tayiwani", "Taiwan"),
    "uk": ("United Kingdom", "Royaume-Uni", "Ubwongereza", "Uingereza"),
    "nl": ("Netherlands", "Pays-Bas", "Ubuholandi", "Uholanzi"),
    "ca": ("Canada", "Canada", "Kanada", "Kanada"),
    "in": ("India", "Inde", "Ubuhinde", "India"),
    "fr": ("France", "France", "Ubufaransa", "Ufaransa"),
    "rw": ("Rwanda (assembled in Kigali)", "Rwanda (assemblé à Kigali)", "u Rwanda (bateranyirizwa i Kigali)", "Rwanda (hukusanywa Kigali)"),
}

_TAGS = {  # short note per kind of brand: (en, fr, rw, sw)
    "major": ("A widely used phone brand with models from low to high price.", "Une marque de téléphones très répandue, avec des modèles de tous les prix.",
              "Ni ikirango cya telefoni gikoreshwa cyane, gifite ubwoko buhendutse n'ubuhenze.", "Ni chapa ya simu inayotumika sana, yenye simu za bei ya chini hadi ya juu."),
    "premium": ("Best known for premium (high-price) phones.", "Surtout connue pour ses téléphones haut de gamme.",
                "Izwi cyane kuri telefoni z'igiciro cyo hejuru.", "Inajulikana zaidi kwa simu za hali ya juu (bei ya juu)."),
    "budget": ("Best known for affordable phones that many first-time smartphone buyers choose.", "Surtout connue pour ses téléphones abordables, souvent choisis pour un premier smartphone.",
               "Izwi cyane kuri telefoni zihendutse abantu benshi bagura bwa mbere.", "Inajulikana zaidi kwa simu za bei nafuu zinazochaguliwa na wengi wanaonunua simu janja kwa mara ya kwanza."),
    "gaming": ("Makes phones built for mobile gaming (fast chips, cooling, fast screens).", "Fabrique des téléphones conçus pour le jeu mobile (puces rapides, refroidissement, écrans fluides).",
               "Ikora telefoni zagenewe imikino (processeur yihuta, gukonjesha, ecran yihuta).", "Hutengeneza simu zilizoundwa kwa michezo (chipu za haraka, upozaji, skrini za haraka)."),
    "rugged": ("Makes tough phones built to survive drops, dust and water.", "Fabrique des téléphones robustes, conçus pour résister aux chutes, à la poussière et à l'eau.",
               "Ikora telefoni zikomeye zishobora kwihanganira kugwa, umukungugu n'amazi.", "Hutengeneza simu imara zinazostahimili kuanguka, vumbi na maji."),
    "feature": ("Known for very low-cost phones, including simple feature phones with long battery life.", "Connue pour des téléphones très bon marché, y compris des téléphones basiques à longue autonomie.",
                "Izwi kuri telefoni zihendutse cyane, harimo izoroheje (feature phones) zimara umuriro igihe kirekire.", "Inajulikana kwa simu za bei nafuu sana, ikiwemo simu rahisi (feature phones) zenye betri ya muda mrefu."),
    "design": ("A newer brand known for its distinctive see-through design and clean software.", "Une marque récente connue pour son design transparent distinctif et son logiciel épuré.",
               "Ni ikirango gishya kizwi ku gishushanyo cyihariye gisa n'icyerekana imbere na porogaramu yoroshye.", "Chapa mpya inayojulikana kwa muundo wake wa pekee unaoonekana ndani na programu safi."),
    "repair": ("Designed to be repairable and long-lasting, with parts that can be replaced.", "Conçue pour être réparable et durable, avec des pièces remplaçables.",
               "Yagenewe gusanwa no kumara igihe kirekire, ifite ibice bishobora gusimburwa.", "Imeundwa kutengenezeka na kudumu, ikiwa na vipuri vinavyoweza kubadilishwa."),
    "sub": ("A sub-brand: it is sold under its own name but belongs to the company shown below.", "Une sous-marque : vendue sous son propre nom mais appartenant à l'entreprise indiquée ci-dessous.",
            "Ni ikirango gishamikiye: kigurishwa ku izina ryacyo ariko ni icy'ikigo cyavuzwe hepfo.", "Chapa tanzu: inauzwa kwa jina lake lakini inamilikiwa na kampuni iliyoonyeshwa hapa chini."),
    "inactive": ("No longer sells new phones under its own name, but older phones are still in use.", "Ne vend plus de nouveaux téléphones sous son propre nom, mais d'anciens modèles sont encore utilisés.",
                 "Ntigicuruza telefoni nshya ku izina ryacyo, ariko izishaje ziracyakoreshwa.", "Haiuzi tena simu mpya kwa jina lake, lakini simu za zamani bado zinatumika."),
    "local": ("An African-assembled brand: its phones were assembled in Kigali. Check the maker for current availability.", "Une marque assemblée en Afrique : ses téléphones étaient assemblés à Kigali. Vérifiez auprès du fabricant la disponibilité actuelle.",
              "Ni ikirango cyateranyirijwe muri Afurika: telefoni zacyo zateranyirizwaga i Kigali. Reba kuri uruganda ko zikiboneka.", "Chapa iliyokusanywa Afrika: simu zake zilikusanywa Kigali. Angalia kwa mtengenezaji kama bado zinapatikana."),
}

_LBL = {  # manufacturer, country, notable lines, software, type, more
    "en": ("Manufacturer", "Country", "Notable lines", "Software", "Check the maker's own website for the newest models; brands and ranges change."),
    "fr": ("Fabricant", "Pays", "Gammes connues", "Logiciel", "Consultez le site du fabricant pour les modèles les plus récents ; les marques et gammes évoluent."),
    "rw": ("Uruganda", "Igihugu", "Ibyamamaye", "Porogaramu", "Reba urubuga rw'uruganda ku bishya; ibirango n'ibyo bikora birahinduka."),
    "sw": ("Mtengenezaji", "Nchi", "Mifano maarufu", "Programu", "Angalia tovuti ya mtengenezaji kwa miundo mipya; chapa na safu hubadilika."),
}

# key: (aliases, brand, company, country, notable lines, software, tag, Commons photo search)
_DATA = {
    "samsung": (["samsung", "samsung galaxy", "galaxy phone", "samsung phone"], "Samsung Galaxy", "Samsung Electronics", "kr", "Galaxy S, Galaxy A, Galaxy Z (foldables)", "Android (One UI)", "major", "Samsung Galaxy smartphone"),
    "iphone": (["iphone", "apple iphone", "apple phone", "iphones"], "Apple iPhone", "Apple Inc.", "us", "iPhone, iPhone Pro, iPhone SE", "iOS", "premium", "Apple iPhone smartphone"),
    "xiaomi": (["xiaomi", "xiaomi phone", "mi phone"], "Xiaomi", "Xiaomi Corporation", "cn", "Xiaomi (number series), Xiaomi T, Xiaomi Mix", "Android (HyperOS / MIUI)", "major", "Xiaomi smartphone"),
    "huawei": (["huawei", "huawei phone"], "Huawei", "Huawei Technologies", "cn", "Mate, P series, Nova, Pura", "HarmonyOS / Android-based", "premium", "Huawei smartphone"),
    "oppo": (["oppo", "oppo phone"], "OPPO", "OPPO (Guangdong OPPO Mobile Telecommunications)", "cn", "Find, Reno, A series", "Android (ColorOS)", "major", "OPPO smartphone"),
    "vivo": (["vivo", "vivo phone"], "vivo", "Vivo Communication Technology", "cn", "X, V, Y series", "Android (Funtouch OS / OriginOS)", "major", "vivo smartphone"),
    "tecno": (["tecno", "tecno phone", "tecno mobile", "tecno camon", "tecno spark"], "TECNO", "Transsion Holdings", "cn", "Camon, Spark, Phantom, Pova", "Android (HiOS)", "budget", "Tecno Camon smartphone"),
    "infinix": (["infinix", "infinix phone", "infinix hot", "infinix note"], "Infinix", "Transsion Holdings", "cn", "Hot, Note, Zero, Smart", "Android (XOS)", "budget", "Infinix smartphone"),
    "itel": (["itel", "itel phone", "itel mobile"], "itel", "Transsion Holdings", "cn", "A series, P series, feature phones", "Android and simple phone software", "budget", "itel phone"),
    "honor": (["honor phone", "honor magic", "honor mobile", "honor smartphone"], "Honor", "Honor Device Co.", "cn", "Magic, Honor X, Honor Play", "Android (MagicOS)", "major", "Honor Magic smartphone"),
    "oneplus": (["oneplus", "one plus", "oneplus phone"], "OnePlus", "OnePlus Technology (Shenzhen)", "cn", "OnePlus (number series), Nord", "Android (OxygenOS)", "major", "OnePlus smartphone"),
    "realme": (["realme", "realme phone"], "realme", "realme Mobile Telecommunications", "cn", "Number series, GT, C series", "Android (realme UI)", "budget", "realme smartphone"),
    "redmi": (["redmi", "redmi phone", "redmi note"], "Redmi", "Xiaomi Corporation", "cn", "Redmi, Redmi Note, Redmi A", "Android (HyperOS / MIUI)", "sub", "Xiaomi Redmi Note smartphone"),
    "poco": (["poco", "poco phone", "pocophone"], "POCO", "Xiaomi Corporation", "cn", "POCO F, POCO X, POCO M", "Android (HyperOS / MIUI)", "sub", "Xiaomi Poco smartphone"),
    "iqoo": (["iqoo", "iqoo phone"], "iQOO", "vivo (Vivo Communication Technology)", "cn", "iQOO (number series), iQOO Neo, iQOO Z", "Android (OriginOS / Funtouch OS)", "sub", "iQOO smartphone"),
    "pixel": (["google pixel", "pixel phone", "pixel smartphone", "pixel phones"], "Google Pixel", "Google LLC (Alphabet)", "us", "Pixel, Pixel Pro, Pixel a, Pixel Fold", "Android (made by Google)", "premium", "Google Pixel smartphone"),
    "motorola": (["motorola", "motorola phone", "moto g", "moto razr", "motorola razr"], "Motorola", "Motorola Mobility (owned by Lenovo)", "us", "Moto G, Moto E, Edge, Razr (flip)", "Android", "major", "Motorola Moto smartphone"),
    "nokia": (["nokia", "nokia phone", "nokia mobile"], "Nokia", "HMD Global (uses the Nokia name under licence)", "fi", "Nokia G, Nokia C, Nokia feature phones", "Android and simple phone software", "major", "Nokia mobile phone"),
    "hmd": (["hmd", "hmd phone", "hmd global"], "HMD", "HMD Global", "fi", "HMD Fusion, HMD Pulse, HMD feature phones", "Android and simple phone software", "major", "HMD smartphone"),
    "sony": (["sony xperia", "xperia", "sony phone", "sony smartphone"], "Sony Xperia", "Sony Corporation", "jp", "Xperia 1, Xperia 5, Xperia 10", "Android", "premium", "Sony Xperia smartphone"),
    "lg": (["lg phone", "lg mobile", "lg smartphone", "lg velvet", "lg wing"], "LG", "LG Electronics", "kr", "LG G, LG V, Velvet, Wing", "Android", "inactive", "LG smartphone"),
    "htc": (["htc", "htc phone", "htc desire", "htc u"], "HTC", "HTC Corporation", "tw", "Desire, U series, Wildfire", "Android", "major", "HTC smartphone"),
    "asus": (["asus phone", "asus rog phone", "rog phone", "zenfone", "asus zenfone"], "ASUS ROG Phone / Zenfone", "ASUS (ASUSTeK Computer)", "tw", "ROG Phone (gaming), Zenfone", "Android", "gaming", "Asus ROG Phone"),
    "lenovo": (["lenovo phone", "lenovo smartphone", "lenovo mobile"], "Lenovo", "Lenovo Group", "cn", "Lenovo K, Lenovo Legion Phone, Motorola (owned)", "Android", "major", "Lenovo smartphone"),
    "zte": (["zte", "zte phone", "zte blade", "zte axon"], "ZTE", "ZTE Corporation", "cn", "Blade, Axon", "Android", "major", "ZTE Blade smartphone"),
    "nubia": (["nubia", "nubia phone", "nubia z"], "Nubia", "Nubia Technology (originally a ZTE subsidiary)", "cn", "Nubia Z, Nubia Flip", "Android", "sub", "Nubia Z smartphone"),
    "redmagic": (["redmagic", "red magic", "red magic phone", "redmagic phone"], "RedMagic", "Nubia Technology", "cn", "RedMagic (number series)", "Android (RedMagic OS)", "gaming", "RedMagic gaming phone"),
    "blackshark": (["black shark", "blackshark", "black shark phone"], "Black Shark", "Black Shark Technology (backed by Xiaomi)", "cn", "Black Shark (number series)", "Android (JOYUI)", "gaming", "Black Shark gaming phone"),
    "nothing": (["nothing phone", "nothing phone 1", "nothing phone 2", "nothing technology"], "Nothing Phone", "Nothing Technology", "uk", "Phone (1), Phone (2), Phone (3)", "Android (Nothing OS)", "design", "Nothing Phone smartphone"),
    "fairphone": (["fairphone", "fairphone phone"], "Fairphone", "Fairphone B.V.", "nl", "Fairphone (number series)", "Android", "repair", "Fairphone smartphone"),
    "blackberry": (["blackberry", "blackberry phone", "blackberry keyboard phone"], "BlackBerry", "BlackBerry Limited (phones were once made under licence by TCL)", "ca", "Bold, Curve, Key series", "BlackBerry OS / Android", "inactive", "BlackBerry smartphone"),
    "alcatel": (["alcatel", "alcatel phone", "alcatel mobile"], "Alcatel", "TCL Communication (uses the Alcatel name under licence)", "fr", "Alcatel 1 series, 3 series", "Android and simple phone software", "budget", "Alcatel smartphone"),
    "tcl": (["tcl phone", "tcl mobile", "tcl smartphone"], "TCL", "TCL Technology", "cn", "TCL 10, TCL 20, TCL 30 series", "Android", "budget", "TCL smartphone"),
    "meizu": (["meizu", "meizu phone"], "Meizu", "Meizu Technology", "cn", "Meizu (number series), Meizu Note", "Android (Flyme)", "major", "Meizu smartphone"),
    "gionee": (["gionee", "gionee phone"], "Gionee", "Gionee Communication Equipment", "cn", "Elife, Marathon", "Android", "inactive", "Gionee smartphone"),
    "lava": (["lava phone", "lava mobile", "lava smartphone", "lava blaze"], "Lava", "Lava International", "in", "Blaze, Agni, Yuva", "Android", "budget", "Lava smartphone"),
    "micromax": (["micromax", "micromax phone"], "Micromax", "Micromax Informatics", "in", "In series, Canvas", "Android", "budget", "Micromax smartphone"),
    "jio": (["jiophone", "jio phone", "jio phones"], "JioPhone", "Reliance Jio Infocomm", "in", "JioPhone, JioPhone Next", "KaiOS / Android-based", "feature", "JioPhone"),
    "sharp": (["sharp aquos", "aquos", "sharp phone", "sharp smartphone"], "Sharp Aquos", "Sharp Corporation", "jp", "Aquos R, Aquos Sense", "Android", "major", "Sharp Aquos smartphone"),
    "kyocera": (["kyocera", "kyocera phone", "kyocera duraforce"], "Kyocera", "Kyocera Corporation", "jp", "DuraForce, Torque", "Android", "rugged", "Kyocera smartphone"),
    "ulefone": (["ulefone", "ulefone phone"], "Ulefone", "Ulefone", "cn", "Armor series, Note series", "Android", "rugged", "Ulefone Armor smartphone"),
    "doogee": (["doogee", "doogee phone"], "Doogee", "Doogee", "cn", "S series, V series", "Android", "rugged", "Doogee smartphone"),
    "oukitel": (["oukitel", "oukitel phone"], "Oukitel", "Oukitel", "cn", "WP series, C series", "Android", "rugged", "Oukitel smartphone"),
    "blackview": (["blackview", "blackview phone"], "Blackview", "Blackview", "cn", "BV series, A series", "Android", "rugged", "Blackview smartphone"),
    "cubot": (["cubot", "cubot phone"], "Cubot", "Cubot", "cn", "KingKong, Note, Pocket", "Android", "budget", "Cubot smartphone"),
    "umidigi": (["umidigi", "umidigi phone"], "UMIDIGI", "UMIDIGI", "cn", "A series, G series, Power", "Android", "budget", "UMIDIGI smartphone"),
    "wiko": (["wiko", "wiko phone"], "Wiko", "Wiko (owned by Tinno Mobile)", "fr", "Y series, T series, Power", "Android", "budget", "Wiko smartphone"),
    "sonim": (["sonim", "sonim phone"], "Sonim", "Sonim Technologies", "us", "XP series", "Android", "rugged", "Sonim rugged phone"),
    "hisense": (["hisense phone", "hisense smartphone", "hisense mobile"], "Hisense", "Hisense Group", "cn", "Infinity, King Kong", "Android", "budget", "Hisense smartphone"),
    "mara": (["mara phone", "mara phones", "mara x", "mara z", "mara group"], "Mara Phones", "Mara Group", "rw", "Mara X, Mara Z", "Android", "local", "Mara smartphone"),
}

_TYPES = {  # kinds of phones, shown in the overview
    "en": ("Smartphone (touchscreen, apps, internet)", "Feature phone (simple, calls and texts, long battery)", "Foldable and flip phone", "Rugged phone (dust, water, drops)", "Gaming phone (fast chip, cooling)"),
    "fr": ("Smartphone (écran tactile, applications, Internet)", "Téléphone basique (appels et SMS, longue autonomie)", "Téléphone pliable et à clapet", "Téléphone robuste (poussière, eau, chutes)", "Téléphone de jeu (puce rapide, refroidissement)"),
    "rw": ("Smartphone (ecran ikorwaho, porogaramu, internet)", "Telefoni yoroheje (guhamagara na SMS, umuriro umara igihe)", "Telefoni ikunjwa", "Telefoni ikomeye (umukungugu, amazi, kugwa)", "Telefoni y'imikino (processeur yihuta, gukonjesha)"),
    "sw": ("Simu janja (skrini ya kugusa, programu, intaneti)", "Simu rahisi (kupiga na kutuma SMS, betri ya muda mrefu)", "Simu inayokunjika", "Simu imara (vumbi, maji, kuanguka)", "Simu ya michezo (chipu ya haraka, upozaji)"),
}
_TITLE = {"en": "Phone brands and their manufacturers", "fr": "Marques de téléphones et leurs fabricants",
          "rw": "Ibirango bya telefoni n'inganda zibikora", "sw": "Chapa za simu na watengenezaji wake"}
_INTRO = {
    "en": "Here are {n} phone brands with the company that makes each one and its home country. {extra}Kinds of phones: {types}. Ask about any brand (for example “Tecno”, “Samsung” or “Google Pixel”) for more detail and a photo.",
    "fr": "Voici {n} marques de téléphones avec l'entreprise qui fabrique chacune et son pays. {extra}Types de téléphones : {types}. Demandez une marque (par exemple « Tecno », « Samsung » ou « Google Pixel ») pour plus de détails et une photo.",
    "rw": "Dore ibirango bya telefoni {n} hamwe n'ikigo gikora buri kimwe n'igihugu cyacyo. {extra}Ubwoko bwa telefoni: {types}. Baza ikirango icyo ari cyo cyose (urugero «Tecno», «Samsung» cyangwa «Google Pixel») kugira ngo ubone ibisobanuro n'ifoto.",
    "sw": "Hizi hapa chapa {n} za simu pamoja na kampuni inayotengeneza kila moja na nchi yake. {extra}Aina za simu: {types}. Uliza chapa yoyote (kwa mfano «Tecno», «Samsung» au «Google Pixel») kwa maelezo zaidi na picha.",
}
_EXTRA = {
    "en": "(You asked for {want}; {have} are listed here.) ", "fr": "(Vous en avez demandé {want} ; {have} sont listées ici.) ",
    "rw": "(Wasabye {want}; hano hari {have}.) ", "sw": "(Uliomba {want}; zilizoorodheshwa hapa ni {have}.) ",
}
_UI = {  # steps label, photo caption, photo-missing note, gallery note
    "en": ("Key facts", "Photo from Wikimedia Commons: “{t}” (author and licence on the file page). It may show a different model of the same brand.",
           "The photo could not be loaded right now (it needs internet access). The explanation above is complete without it.", "Photos could not be found for the other brands right now."),
    "fr": ("À retenir", "Photo de Wikimedia Commons : « {t} » (auteur et licence sur la page du fichier). Elle peut montrer un autre modèle de la même marque.",
           "La photo n'a pas pu être chargée pour le moment (accès Internet requis). L'explication ci-dessus est complète sans elle.", "Les photos des autres marques n'ont pas pu être trouvées pour le moment."),
    "rw": ("Ibyingenzi", "Ifoto iva kuri Wikimedia Commons: «{t}» (uwayifashe n'uruhushya biri ku rupapuro rwayo). Ishobora kwerekana indi modeli y'ikirango kimwe.",
           "Ifoto ntibashije kuboneka ubu (bisaba internet). Ibisobanuro biri hejuru byuzuye idafite ifoto.", "Amafoto y'ibindi birango ntiyabonetse ubu."),
    "sw": ("Mambo muhimu", "Picha kutoka Wikimedia Commons: «{t}» (mwandishi na leseni ziko kwenye ukurasa wa faili). Inaweza kuonyesha modeli tofauti ya chapa hiyo hiyo.",
           "Picha haikuweza kupakiwa sasa (inahitaji intaneti). Maelezo yaliyo hapo juu yanajitosheleza bila hiyo.", "Picha za chapa nyingine hazikupatikana kwa sasa."),
}

_PHONE_WORDS = {"phone", "phones", "mobile", "mobiles", "smartphone", "smartphones", "cellphone", "cellphones", "telephone", "telephones", "handset", "handsets",
                "telephone", "telephones", "telephone", "portable", "portables", "telefoni", "telefone", "simu", "simujanja", "iphone", "iphones", "android"}
_LIST_WORDS = {"brand", "brands", "type", "types", "kind", "kinds", "list", "manufacturer", "manufacturers", "manufacturing", "company", "companies", "maker", "makers", "models", "model",
               "marque", "marques", "fabricant", "fabricants", "entreprise", "entreprises", "liste", "ubwoko", "bwoko", "ibirango", "ikirango", "inganda", "uruganda", "ikigo", "ibigo",
               "chapa", "aina", "watengenezaji", "mtengenezaji", "kampuni", "orodha", "mifano", "modeles", "types", "different", "existing", "popular", "modern"}
_CUES = {"what", "whats", "how", "who", "explain", "tell", "about", "describe", "show", "photo", "photos", "picture", "pictures", "image", "images", "make", "makes", "made", "maker", "manufacturer",
         "company", "owns", "own", "iki", "ninde", "bikora", "sobanura", "ifoto", "ishusho", "quoi", "qui", "comment", "fabrique", "explique", "nini", "nani", "inatengenezwa", "picha", "eleza", "ni"}
_BLOCK = {"scam", "scams", "scammer", "fraud", "virus", "viruses", "hack", "hacked", "hacker", "malware", "password", "passwords", "phishing", "stolen", "lost", "lose", "steal", "theft", "number", "numbers",
          "infected", "attack", "breach", "ransomware", "perdu", "vole", "piratage", "arnaque", "yibwe", "yatakaye", "ubujura", "wizi", "imeibiwa", "umepotea", "matapeli", "sim", "momo", "airtime",
          "network", "networks", "plan", "plans", "tariff", "insurance", "repair", "fix", "broken", "battery", "charge", "charger", "slow", "signal", "protect", "secure", "security", "safe", "block", "blocked", "call", "calls"}


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


_INDEX = sorted(((fold(a), k) for k, (aliases, *_r) in _DATA.items() for a in aliases), key=lambda t: -len(t[0]))
COUNT = len(_DATA)
ORDER = list(_DATA)


def _alias_hits(text):
    padded, seen, hits = f" {text} ", set(), []
    for alias, key in _INDEX:
        if f" {alias} " in padded and key not in seen:
            seen.add(key)
            hits.append((key, alias))
    return hits


def _lk(lang):
    return lang if lang in LANGS else "en"


def _country(code, lang):
    return _COUNTRY[code][LANGS.index(_lk(lang))]


def _entry(key, lang=None):
    aliases, brand, company, country, lines, os_, tag, q = _DATA[key]
    entry = {"id": "phone_" + key, "related": [], "kind": "phone", "key": key, "title": {}, "answer": {}, "steps": {}, "steps_label": {},
             "image_query": {"search": q, "wiki": brand}}
    for i, l in enumerate(LANGS):
        lab = _LBL[l]
        entry["title"][l] = brand
        entry["answer"][l] = _TAGS[tag][i]
        entry["steps"][l] = [f"{lab[0]}: {company}", f"{lab[1]}: {_country(country, l)}", f"{lab[2]}: {lines}", f"{lab[3]}: {os_}", lab[4]]
        entry["steps_label"][l] = _UI[l][0]
    return entry


def _wanted_count(text):
    m = re.search(r"\b(\d{1,3})\b", text)
    if m:
        return int(m.group(1))
    words = {"ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100, "dix": 10, "vingt": 20, "trente": 30, "quarante": 40, "cinquante": 50, "cent": 100}
    for w, n in words.items():
        if f" {w} " in f" {text} ":
            return n
    return None


def overview(lang="en", want=None):
    """Guide-shaped entry listing the brands (all of them, or the first `want` if fewer were asked for), with a photo gallery request."""
    have = COUNT
    keys = ORDER
    if want is not None and 0 < want < COUNT:
        keys, have = ORDER[:want], want
    entry = {"id": "phone_list", "related": [], "kind": "phone_list", "key": "list", "title": {}, "answer": {}, "steps": {}, "steps_label": {},
             "gallery": [{"key": k, "name": _DATA[k][1], "query": _DATA[k][7]} for k in keys]}
    for i, l in enumerate(LANGS):
        extra = _EXTRA[l].format(want=want, have=COUNT) if (want is not None and want > COUNT) else ""
        entry["title"][l] = _TITLE[l]
        entry["answer"][l] = _INTRO[l].format(n=have, extra=extra, types="; ".join(_TYPES[l]))
        entry["steps"][l] = [f"**{_DATA[k][1]}** — {_DATA[k][2]} ({_country(_DATA[k][3], l)}) — {_DATA[k][5]}" for k in keys] + [_LBL[l][4]]
        entry["steps_label"][l] = _UI[l][0]
    return entry


def find(question, lang="en"):
    """Guide-shaped entry for a question about phone brands / one phone brand, or None.

    A list question needs a phone word and a list word (brands, types, manufacturers, list ...). A single brand needs a known brand alias and either to be
    (almost) just that name or to carry a cue such as what/who/how/photo/ni iki. Questions about scams, lost phones, numbers, repairs, etc. are never taken."""
    q = (question or "").strip()
    if not q or len(q) > 200:
        return None
    text = fold(q)
    toks = text.split()
    if not toks:
        return None
    tset = set(toks)
    if tset & _BLOCK:
        return None
    hits = _alias_hits(text)
    if (tset & _PHONE_WORDS) and (tset & _LIST_WORDS) and len(toks) <= 25 and (len(hits) != 1 or len(toks) > 6 or (tset & {"brands", "types", "list", "manufacturers", "marques", "ibirango", "chapa"})):
        return overview(lang, _wanted_count(text))
    if not hits:
        return None
    key, alias = hits[0]
    bare = len(toks) <= 4 and all(t in alias.split() or t in {"a", "the", "un", "une", "le", "la"} for t in toks)
    if bare or (tset & _CUES):
        return _entry(key, lang)
    return None


# ---------------------------------------------------------------- photos
def _get_json(url, timeout=6):
    import json, urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0 (educational app; ebanatrm100@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


_SKIP = ("logo", "icon", "screenshot", "wordmark", "store", "shop", "booth", "exhibition", "advert", "poster", "banner", "diagram", "chart", "map", "flag", "ceo", "headquarters", "factory", "building", "building")
_CACHE = {}


def _search_url(query, limit=10):
    return (COMMONS_API + "?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=" + str(limit) + "&gsrsearch=" + quote(query)
            + "&prop=imageinfo&iiprop=url|mime&iiurlwidth=360")


def pick_photo(data):
    """From a Commons API result choose the first JPEG/PNG whose title does not look like a logo/screenshot/shop picture. Returns (title, thumb_url) or None."""
    pages = list(((data or {}).get("query") or {}).get("pages", {}).values())
    pages.sort(key=lambda p: p.get("index", 999))
    for p in pages:
        title = str(p.get("title", ""))
        low = title.lower()
        info = (p.get("imageinfo") or [{}])[0]
        mime, url = info.get("mime", ""), info.get("thumburl") or ""
        if mime not in ("image/jpeg", "image/png") or not url.startswith("https://upload.wikimedia.org/"):
            continue
        if any(w in low for w in _SKIP):
            continue
        return title, url
    return None


def resolve_image(entry, lang="en"):
    """Return {'url', 'page', 'caption'} for one phone entry, or None. Never raises. Cached per process (failures too)."""
    try:
        q = (entry or {}).get("image_query")
        if not q:
            return None
        return _resolve(q["search"], lang)
    except Exception:
        return None


def _resolve(query, lang="en"):
    try:
        if query not in _CACHE:
            found = None
            try:
                got = pick_photo(_get_json(_search_url(query)))
                if got:
                    found = {"title": got[0], "url": got[1]}
            except Exception:
                found = None
            _CACHE[query] = found
        f = _CACHE[query]
        if not f:
            return None
        title = f["title"].replace("File:", "", 1)
        return {"url": f["url"], "page": COMMONS_PAGE + quote(f["title"].replace(" ", "_"), safe=":_"), "caption": _UI[_lk(lang)][1].format(t=title)}
    except Exception:
        return None


def resolve_many(items, lang="en", workers=8):
    """Photos for a list of {'name','query'} items, looked up in parallel. Returns [{'name','url','page'}] for the ones found. Never raises."""
    out = []
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            results = list(ex.map(lambda it: _resolve(it["query"], lang), items))
        for it, r in zip(items, results):
            if r:
                out.append({"name": it["name"], "url": r["url"], "page": r["page"]})
    except Exception:
        pass
    return out


def missing_photo_note(lang="en"):
    return _UI[_lk(lang)][2]


def gallery_note(lang="en"):
    return _UI[_lk(lang)][3]
