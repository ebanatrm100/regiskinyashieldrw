"""Scenario engine for the Check tab: a library of scam situations (scam_scen_*.py), each detected by several cue groups that must ALL be present, with its own
explanation and specific steps in English, French, Kinyarwanda and Kiswahili. Matching is done on accent-folded text. A cue found only inside a warning sentence
("never share your PIN") does not count. Awareness only. fr/rw/sw wording is a DRAFT for review by fluent speakers."""
import re
from textutil import fold

LANGS = ("en", "fr", "rw", "sw")
_F = re.I


def P(latin, bantu):
    """Latin-script stems match at a word start; Kinyarwanda/Kiswahili stems also match after a short subject prefix (n-, u-, tu-, ni-, wa-...)."""
    return r"(?:\b(?:" + latin + r")\w*|\b\w{0,4}(?:" + bantu + r")\w*)"

V = {   # cue vocabularies: multilingual regexes on folded text (stems; \w* lets suffixes through)
 "PAY": P("pay|paid|payment|deposit|transfer|send|sent|wire|remit|envoy|vers|paie|depos|virement", "ohereza|ohere|kohereza|kwishyur|ishyur|twohereze|tuma|lipa|malipo|toa pesa|weka pesa|kubitsa|bitsa"),
 "FEE": r"\b(?:fee|fees|charge|charges|tax|insurance|processing|registration|clearance|activation|frais|taxe|assurance|dedouanement|ikiguzi|ubwishyu|ada|kodi|bima|gharama|amafaranga y\w+)\b",
 "MONEY": r"(?:\b(?:money|cash|funds|argent|fonds|amafaranga|ifaranga|pesa|fedha|rwf|frw|usd|dollars?|euros?|kes|ugx|tzs)\b|\d[\d.,]*\s?(?:rwf|frw|usd|eur|kes|ugx|tzs|\$|k\b)|[$€]\s?\d)",
 "CODE": r"\b(?:otp|pin|passcode|password|cvv|verification code|one[- ]time|code|kode|msimbo|nenosiri|mot de passe|ijambo ry'ibanga|umubare w'ibanga|namba ya siri|seed phrase|recovery phrase|secret phrase)\b",
 "LINK": r"(?:https?://|\bwww\.|\b[a-z0-9-]+\.(?:com|net|org|xyz|info|top|online|site|club|link|click|icu|live|shop|vip|app|co)\b|\bbit\.ly|\btinyurl|\bwa\.me|\bt\.me|\bcutt\.ly|\brb\.gy)",
 "URG": r"\b(?:urgent|urgently|immediately|right now|asap|today only|last chance|final notice|within \d+ ?(?:hours?|minutes?|days?|hrs?)|expires?|hurry|quickly|urgence|immediatement|maintenant|dernier avis|dans les \d+|vuba|ako kanya|byihutirwa|uyu munsi gusa|mu masaha|haraka|sasa hivi|mara moja|leo tu|ndani ya saa|siku \d+)\w*",
 "WIN": r"\b(?:you (?:have )?won|winner|congratulations|congrats|prize|lottery|jackpot|you (?:are|have been) selected|gagn|felicitations|loterie|cadeau|watsinze|wegukanye|igihembo|tombola|umeshinda|zawadi|bahati nasibu|umechaguliwa)\w*",
 "FREE": r"\b(?:free|gratuit|gratis|bure|ku buntu|bonus|promo|promotion|giveaway)\w*",
 "JOB": r"\b(?:job|jobs|vacancy|vacancies|recruit|hiring|work from home|salary|employment|emploi|recrut|poste|akazi|ikiraka|kazi|ajira|mshahara|umushahara|interview|hr manager)\w*",
 "LOAN": r"\b(?:loan|loans|credit|borrow|pret|emprunt|inguzanyo|kuguza|mkopo|mikopo|kukopa)\w*",
 "INVEST": r"\b(?:invest|investment|profit|profits|returns?|roi|dividend|double your|trading|trader|forex|crypto|bitcoin|usdt|binance|mining|investi|rendement|ishoramari|inyungu|uwekezaji|faida|kuwekeza)\w*",
 "GUAR": r"\b(?:guarantee|guaranteed|risk[- ]free|sure profit|100 ?%|daily|weekly|per day|per week|every day|garanti|sans risque|byizewe|hakika|uhakika|bila hatari|kila siku|kila wiki|buri munsi|buri cyumweru|mu masaha \d+|in \d+ (?:days?|hours?))\w*",
 "ACCT": r"\b(?:account|acct|wallet|card|sim|line|compte|carte|konti|ikarita|akaunti|kadi|laini|profile|page)\b",
 "BLOCK": r"\b(?:block|blocked|suspend|suspended|closed|close|deactivat|disabled|expire|locked|restrict|terminated|bloque|suspendu|ferme|desactiv|izafungwa|yafunzwe|izahagarikwa|ifunzwe|itafungwa|imefungwa|itasimamishwa|imesimamishwa|kufungwa|izafungwa)\w*",
 "VERIFY": P("verify|verification|confirm|update|validate|reactivate|re-?register|kyc|verifier|confirmer|mettre a jour|valider", "emeza|vugurura|genzura|thibitisha|hakiki|sasisha|ongera wiyandikishe|wiyandikishe"),
 "CLICK": P("click|tap|open|visit|follow|log ?in|sign ?in|scan|cliquez|ouvrez|visitez|connectez|scannez", "kanda|fungura|injira|sura|bofya|fungua|ingia|skani"),
 "CALL": P("call|phone|contact|whatsapp|text|dial|reply|message us|appelez|contactez|ecrivez", "hamagara|vugana|andikira|subiza|piga|wasiliana|jibu"),
 "ORG": r"\b(?:mtn|airtel|tigo|momo|mobile money|bank of kigali|bk|equity|i&m|cogebanque|ecobank|access bank|bnr|rra|rdb|irembo|rssb|nida|eucl|wasac|police|rnp|rib|ministry|government|gouvernement|leta|serikali|banque|bank|banki|visa|mastercard|paypal|whatsapp|facebook|instagram|tiktok|google|microsoft|apple|netflix|amazon|dhl|fedex|ups|unicef|undp|world bank|red cross|western union|moneygram|binance|safaricom|vodacom|mpesa|m-pesa)\b",
 "PARCEL": r"\b(?:parcel|package|shipment|delivery|courier|customs|cargo|colis|livraison|douane|ipaki|igicuruzwa|mzigo|kifurushi|forodha|ubwikorezi)\w*",
 "SECRET": r"\b(?:do not tell|don't tell|keep (?:it|this)|tell no one|confidential|ne le dites|gardez le secret|ntubibwire|bigire ibanga|usimwambie|weka siri|ibanga|siri)\b",
 "LOVE": r"\b(?:my love|darling|honey|sweetheart|dear friend|my dear|beautiful|handsome|mon amour|cheri|mukunzi|nkunda|mpenzi|nakupenda|i love you|marry|marriage|relationship|widow|widower|single)\b",
 "ABROAD": r"\b(?:abroad|overseas|usa|america|canada|uk|london|dubai|qatar|saudi|europe|germany|australia|military|army|soldier|oil rig|engineer|doctor in|iburaya|hanze|ughaib|nje ya nchi|ulaya|marekani)\b",
 "GIFT": r"\b(?:gift card|itunes|google play|steam|amazon card|voucher|carte cadeau|ikarita y'impano|kadi ya zawadi)\b",
 "CRYPTO": r"\b(?:crypto|bitcoin|btc|ethereum|eth|usdt|nft|airdrop|wallet connect|metamask|trust wallet|binance|seed phrase|recovery phrase|token)\b",
 "SELL": r"\b(?:for sale|selling|buy|buyer|seller|item|product|order|ad|advert|marketplace|jiji|a vendre|acheter|vendeur|acheteur|kugura|kugurisha|umuguzi|gucuruza|kuuza|mnunuzi|muuzaji|bidhaa)\w*",
 "HOUSE": r"\b(?:house|apartment|rent|rental|landlord|room|plot|land|property|villa|maison|appartement|loyer|terrain|propriete|inzu|ubukode|ikibanza|isambu|nyumba|kodi ya nyumba|kiwanja|ardhi)\w*",
 "SCHOOL": r"\b(?:school|university|scholarship|tuition|fees|admission|exam|results|ishuri|kaminuza|buruse|amashuri|shule|chuo|ufadhili|bursary)\w*",
 "TECH": r"\b(?:virus|infected|hacked|malware|security alert|suspicious (?:login|sign[- ]in|activity)|microsoft|windows|apple support|tech support|antivirus|unusual activity)\b",
 "OFFICIAL": r"\b(?:police|court|tribunal|arrest|warrant|summons|fine|prosecutor|ministry|tax|revenue|rra|customs|immigration|interpol|fbi|cid|rib|rnp|inspector|officer|polisi|mahakama|kodi|faini|amande)\w*",
 "BOSS": r"\b(?:ceo|director|boss|manager|md|chairman|principal|head of|patron|directeur|chef|umuyobozi|mkurugenzi|bosi)\b",
 "FAMILY": r"\b(?:mum|mom|mother|dad|father|son|daughter|brother|sister|uncle|aunt|grandma|maman|papa|fils|fille|frere|soeur|mama|papa|mwana|murumuna|musaza|mukuru|mama|baba|kaka|dada|mjomba)\b",
 "EMERG": r"\b(?:accident|hospital|emergency|arrested|jail|stranded|stuck|surgery|sick|died|death|urgence|hopital|arrete|bloque a|bitaro|impanuka|afunzwe|yarwaye|yapfuye|hospitali|ajali|amekamatwa|amefariki|mgonjwa)\w*",
 "CHAR": r"\b(?:donate|donation|charity|orphan|orphans|help the needy|fundraising|don |dons|orphelin|inkunga|impano|imfubyi|kugira ubuntu|michango|yatima|msaada wa)\w*",
 "OFFER": r"\b(?:offer|deal|discount|cheap|special price|limited|promo|reduction|bon plan|igabanyirizwa|igiciro cyiza|punguzo|bei nafuu)\w*",
 "APK": r"\b(?:apk|install|download|app|application|software|anydesk|teamviewer|quicksupport|rustdesk|installez|telechargez|shyiraho|kuramo|pakua|sakinisha|programu)\w*",
 "NEWNUM": r"\b(?:new number|changed (?:my )?number|lost my phone|this is my new|nouveau numero|numero a change|nimero nshya|namba mpya|nimepoteza simu)\b",
 "REFUND": r"(?:" + P("refund|reimburse|reversal|reverse|chargeback|rembours|annul|renvoyez|rendez", "gusubizwa|gusubiza|kugaruza|kurejeshewa|rejeshewa|rejesha|rudisha|rudishie|nsubiza|ansubize|uyansubize") + r"|\b(?:send|give|return|pay|transfer) (?:it |the money |me |this |them |that )*back\b|\bback to me\b)",
 "MISTAKE": r"\b(?:by mistake|mistakenly|wrong number|wrong transfer|sent (?:to )?you|par erreur|erreur|kubw'impanuka|kwibeshya|nabibeshye|nimekosea|kimakosa|kwibeshyaho)\b",
 "GROUP": r"\b(?:join|group|vip|channel|telegram|signals|members|community|rejoindre|groupe|injira mu|itsinda|jiunge|kikundi)\b",
 "TASK": r"\b(?:task|tasks|like|likes|rate|rating|review|reviews|subscribe|boost|commission|per task|part[- ]time|tache|taches|umurimo|kazi ndogo|kupenda|kutathmini)\w*",
 "SURVEY": r"\b(?:survey|questionnaire|poll|feedback|sondage|ubushakashatsi|utafiti|dodoso)\w*",
 "DELIVER": r"\b(?:deliver|delivery fee|shipping|shipping fee|redelivery|reschedule|livraison|frais de livraison|gutwara|ubwikorezi|usafirishaji|ada ya usafirishaji)\w*",
 "SUBS": r"\b(?:subscription|renewal|renew|billed|charged|auto[- ]renew|abonnement|renouvel|facture|kwiyandikisha|usajili|umezwe|ushuru)\w*",
 "SUPPORT": r"\b(?:support|helpdesk|help desk|customer care|customer service|service client|assistance|agent|ubufasha|huduma kwa wateja|serivisi z'abakiriya)\b",
 "ATTACH": r"\b(?:attached|attachment|invoice|receipt|statement|document|pdf|zip|docx|xlsx|enable (?:content|macros)|piece jointe|facture|recu|ifatanyijwe|inyemezabwishyu|iliyoambatishwa|ankara|risiti)\w*",
 "SHARE": r"\b(?:shared (?:a|an|with)|has shared|shared you|invited you|share your|partage|yagusangije|amekushirikisha|amekualika)\w*",
}
V = {k: re.compile(v, _F) for k, v in V.items()}
_NEG = re.compile(r"\b(?:never|do not|don't|dont|do n't|should not|must not|will not|won't|not to|jamais|ne (?:pas|partagez|donnez|communiquez|cliquez)|ntuzigere|ntugasangize|ntukagire|ntukohereze|ntugatange|kamwe|usishiriki|usitoe|usibofye|hatutakuomba|hatutaomba|hatuombi)\b", _F)


def _neg_before(f, start):
    """True when the sentence part before `start` carries a prohibition ('never share your PIN'): the cue is a warning, not a request."""
    last = 0
    for m in re.finditer(r"[.!?\n]\s", f[:start]):
        last = m.end()
    return bool(_NEG.search(f[last:start][-90:]))


def _group_regex(g):
    """A group is a cue name from V, 'r:regex', or a tuple/list of those (any one of them is enough)."""
    if isinstance(g, (tuple, list)):
        return re.compile("|".join("(?:" + (x[2:] if x.startswith("r:") else V[x].pattern) + ")" for x in g), _F)
    return re.compile(g[2:], _F) if g.startswith("r:") else V[g]


SCENARIOS = []          # filled by scam_scen_*.py through add()


def add(sid, sev, groups, name, why, do, strong=False):
    """name/why/do: 4-tuples (en, fr, rw, sw). `do` uses ' | ' between steps. groups: names from V or 'r:regex'. strong=True: a high scenario that is enough alone for 'high'."""
    SCENARIOS.append({"id": sid, "sev": sev, "groups": [_group_regex(g) for g in groups], "gn": list(groups), "name": dict(zip(LANGS, name)), "why": dict(zip(LANGS, why)),
                      "do": {l: [s.strip() for s in d.split("|") if s.strip()] for l, d in zip(LANGS, do)}, "strong": strong})


def widen(sid, index, regex):
    """Let an existing situation's cue group `index` also match `regex` (a pattern added after probing real messages)."""
    for s in SCENARIOS:
        if s["id"] == sid:
            s["groups"][index] = re.compile("(?:" + s["groups"][index].pattern + ")|(?:" + regex + ")", _F)
            return
    raise KeyError(sid)


def match(text, lang="en"):
    """Scenarios whose cue groups are ALL present. -> list of dicts (id, sev, name, why, do, quotes, strong) ordered high first."""
    f = fold(text or "")
    k = lang if lang in LANGS else "en"
    out = []
    for s in SCENARIOS:
        quotes, ok = [], True
        for g in s["groups"]:
            hit = None
            for m in g.finditer(f):
                if not _neg_before(f, m.start()):
                    hit = m
                    break
            if hit is None:
                ok = False
                break
            q = (text or "")[hit.start():hit.end()].strip()
            if q and q.lower() not in [x.lower() for x in quotes]:
                quotes.append(q[:60])
        if ok:
            out.append({"id": s["id"], "sev": s["sev"], "name": s["name"][k], "why": s["why"][k], "do": s["do"][k], "quotes": quotes[:4], "strong": s["strong"], "ngroups": len(s["groups"])})
    out.sort(key=lambda x: (0 if x["sev"] == "high" else 1, -x["ngroups"]))
    return out


def load():
    for mod in ("scam_scen_1", "scam_scen_2", "scam_scen_3", "scam_scen_4", "scam_scen_5", "scam_scen_6", "scam_scen_7", "scam_scen_fixes"):
        try:
            __import__(mod)
        except ImportError:
            pass
