"""Message-specific details for the Check tab: pulls the concrete facts out of the pasted message (amounts, phone numbers, link domains, deadlines, what it asks the
person to do) and explains each one in English, French, Kinyarwanda and Kiswahili, so the advice talks about THIS message, not scams in general.
Pure Python. Links are only parsed as text, never opened. fr/rw/sw wording is a DRAFT for review by fluent speakers."""
import re
from textutil import fold

LANGS = ("en", "fr", "rw", "sw")
# official domains of organisations people in Rwanda / East Africa often see impersonated (a link to anything else claiming to be them is a red flag)
OFFICIAL = {
    "mtn": ("mtn.co.rw", "mtn.com", "mtn.co.ug", "mtn.co.za"), "airtel": ("airtel.co.rw", "airtel.com", "airtel.africa", "airtelmoney.com"), "bk": ("bk.rw", "bkgroup.rw"),
    "equity": ("equitybankgroup.com", "equitygroupholdings.com"), "irembo": ("irembo.gov.rw",), "rra": ("rra.gov.rw",), "rdb": ("rdb.rw",), "rssb": ("rssb.rw",), "nida": ("nida.gov.rw",),
    "bnr": ("bnr.rw",), "police": ("police.gov.rw",), "eucl": ("reg.rw", "eucl.reg.rw"), "momo": ("mtn.co.rw", "momo.mtn.com"), "whatsapp": ("whatsapp.com", "wa.me"),
    "facebook": ("facebook.com", "fb.com", "meta.com"), "google": ("google.com", "accounts.google.com"), "microsoft": ("microsoft.com", "live.com", "office.com"),
    "paypal": ("paypal.com",), "dhl": ("dhl.com",), "fedex": ("fedex.com",), "netflix": ("netflix.com",), "binance": ("binance.com",), "amazon": ("amazon.com",), "apple": ("apple.com", "icloud.com"),
    "vodacom": ("vodacom.co.tz", "vodacom.com"), "mpesa": ("vodafone.com", "safaricom.co.ke", "vodacom.co.tz"), "tigo": ("tigo.co.tz", "tigo.com"), "ecobank": ("ecobank.com",), "cogebanque": ("cogebanque.co.rw",),
}
_SHORT = ("bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rb.gy", "is.gd", "shorturl.at", "tiny.cc", "ow.ly", "goo.gl", "wa.me", "t.me")
_RISKY_TLD = ("xyz", "top", "click", "icu", "online", "site", "club", "link", "live", "vip", "shop", "cfd", "sbs", "cyou", "buzz", "work", "monster", "rest", "gq", "tk", "ml", "ga", "cf")
_URL = re.compile(r"(?:https?://|www\.)[^\s<>\"')]+|\b[a-z0-9][a-z0-9\-]*(?:\.[a-z0-9\-]+)*\.(?:com|net|org|xyz|info|top|online|site|club|link|click|icu|live|shop|vip|app|co|rw|ke|tz|ug|gov|buzz|cfd|sbs|work)(?:/[^\s<>\"')]*)?", re.I)
_PHONE = re.compile(r"(?<![\d.])(\+?\d[\d \-]{8,14}\d)(?![\d.])")
_AMOUNT = re.compile(r"(?:(?:rwf|frw|usd|eur|kes|ksh|tzs|tsh|ugx|\$|€|£)\s?\d[\d.,]*(?:\s?(?:k|m|million|millions)\b)?|\b\d[\d.,]*(?:\s?(?:k|m|million|millions))?\s?(?:rwf|frw|usd|eur|kes|ksh|tzs|tsh|ugx|dollars?|euros?|\$|€))", re.I)
_DEADLINE = re.compile(r"\b(?:within|in|dans les|dans|mu|ndani ya|ndani)\s+(?:the next\s+)?\d+\s?(?:hours?|hrs?|minutes?|mins?|days?|heures?|jours?|masaha|iminota|iminsi|saa|dakika|siku)\b|\b(?:today|tonight|right now|immediately|asap|aujourd'hui|ce soir|maintenant|immediatement|uyu munsi|ubu|ako kanya|leo|sasa hivi|mara moja)\b|\b(?:before|avant|mbere ya|kabla ya)\s+(?:friday|monday|tuesday|wednesday|thursday|saturday|sunday|midnight|noon|vendredi|lundi|mardi|mercredi|jeudi|samedi|dimanche)\b", re.I)
_CODE = re.compile(r"(?<!\d)(\d{4,8})(?!\d)")
_PAYVERB = re.compile(r"\b(?:pay|send|transfer|deposit|wire|remit|buy|top ?up|payer|envoyez|envoyer|verse[rz]?|virement|depos\w+|renvoyez|ohereza|ohere|kohereza|kwishyura|wishyure|mwishyure|banza wishyure|shyiramo|tuma|tumeni|lipa|weka|nirudishie|rudisha|toa)\w*", re.I)

T = {
 "amount_pay": {"en": "It names an amount ({x}) and asks you to pay or send money. Genuine prizes, loans, jobs, parcels and refunds never require you to pay first.",
                "fr": "Il cite un montant ({x}) et vous demande de payer ou d'envoyer de l'argent. Les vrais gains, prêts, emplois, colis et remboursements n'exigent jamais de payer d'abord.",
                "rw": "Ivuga amafaranga ({x}) ikagusaba kwishyura cyangwa kohereza. Ibihembo, inguzanyo, akazi, ibipfunyika n'ibisubizwa by'ukuri ntibisaba kwishyura mbere.",
                "sw": "Inataja kiasi ({x}) na kukuomba ulipe au utume pesa. Zawadi, mikopo, ajira, vifurushi na marejesho halisi hayahitaji kulipa kwanza."},
 "amount": {"en": "It mentions money ({x}). Do not rely on a figure in a message: check balances in your own app or bank.",
            "fr": "Il mentionne de l'argent ({x}). Ne vous fiez pas à un chiffre dans un message : vérifiez vos soldes dans votre appli ou banque.",
            "rw": "Havugwa amafaranga ({x}). Ntukizere umubare uri mu butumwa: reba amafaranga yawe muri porogaramu cyangwa banki yawe.",
            "sw": "Inataja pesa ({x}). Usitegemee kiasi kilichomo kwenye ujumbe: kagua salio kwenye programu au benki yako."},
 "phone": {"en": "It gives a number to call or pay ({x}). A number inside a message can belong to the scammer: find the organisation's official number yourself, and never send money to a number just because a message says so.",
           "fr": "Il donne un numéro à appeler ou à payer ({x}). Un numéro dans un message peut appartenir à l'escroc : trouvez vous-même le numéro officiel et n'envoyez jamais d'argent à un numéro parce qu'un message le dit.",
           "rw": "Itanga nimero yo guhamagara cyangwa yo kwishyura ({x}). Nimero iri mu butumwa ishobora kuba iy'umutekamutwe: shaka ubwawe nimero yemewe y'ikigo kandi ntukohereze amafaranga kuri nimero kuko ubutumwa buyivuze.",
           "sw": "Inatoa namba ya kupiga au kulipa ({x}). Namba iliyo ndani ya ujumbe inaweza kuwa ya tapeli: tafuta mwenyewe namba rasmi ya shirika na usitume pesa kwa namba kwa sababu ujumbe unasema hivyo."},
 "deadline": {"en": "It sets a deadline (“{x}”). Real banks, operators and authorities do not demand answers or payment within hours; rushing you is how scammers stop you from checking.",
              "fr": "Il fixe un délai (« {x} »). Les vraies banques, opérateurs et autorités n'exigent pas de réponse ou de paiement en quelques heures ; vous presser empêche de vérifier.",
              "rw": "Ishyiraho igihe ntarengwa («{x}»). Amabanki, sosiyete n'ubuyobozi nyabwo ntibisaba igisubizo cyangwa kwishyura mu masaha make; kukwihutisha ni uburyo bwo kukubuza kugenzura.",
              "sw": "Inaweka muda wa mwisho («{x}»). Benki, kampuni na mamlaka halisi hazidai jibu au malipo ndani ya masaa; kukuharakisha ni mbinu ya kukuzuia kuhakiki."},
 "url_short": {"en": "The link «{x}» is shortened, so you cannot see where it leads. Do not open it; ask the sender for the full address through another channel.",
               "fr": "Le lien « {x} » est raccourci : on ne voit pas où il mène. Ne l'ouvrez pas ; demandez l'adresse complète à l'expéditeur par un autre canal.",
               "rw": "Link «{x}» ni ngufi, ntushobora kubona aho igana. Ntuyifungure; saba uwohereje aderesi yuzuye unyuze ku rundi rubuga.",
               "sw": "Kiungo «{x}» kimefupishwa, huwezi kuona kinakoelekea. Usikifungue; muombe mtumaji anwani kamili kwa njia nyingine."},
 "url_brand": {"en": "The link «{x}» uses the name “{b}” but is not an official {b} address (official sites use {o}). This is the classic fake-website trick.",
               "fr": "Le lien « {x} » utilise le nom « {b} » mais n'est pas une adresse officielle de {b} (les sites officiels utilisent {o}). C'est le piège classique du faux site.",
               "rw": "Link «{x}» ikoresha izina «{b}» ariko si aderesi yemewe ya {b} (imbuga nyazo zikoresha {o}). Ni uburiganya busanzwe bw'urubuga rw'impimbano.",
               "sw": "Kiungo «{x}» kinatumia jina «{b}» lakini si anwani rasmi ya {b} (tovuti rasmi hutumia {o}). Hii ni hila ya kawaida ya tovuti bandia."},
 "url_tld": {"en": "The link «{x}» ends in .{t}, an address type often used for throw-away scam sites. Real organisations use their own well-known domain.",
             "fr": "Le lien « {x} » finit par .{t}, un type d'adresse souvent utilisé pour des sites d'arnaque jetables. Les vraies organisations utilisent leur domaine connu.",
             "rw": "Link «{x}» irangirira kuri .{t}, ubwoko bw'aderesi bukunze gukoreshwa mu mbuga z'uburiganya z'igihe gito. Ibigo nyabyo bikoresha domaine yabyo izwi.",
             "sw": "Kiungo «{x}» kinaishia .{t}, aina ya anwani inayotumiwa mara nyingi kwa tovuti za utapeli za muda mfupi. Mashirika halisi hutumia kikoa chao kinachojulikana."},
 "url_hyphen": {"en": "The link «{x}» is a long, hyphenated address. Scam sites often stuff real brand words into odd addresses to look genuine.",
                "fr": "Le lien « {x} » est une adresse longue avec des tirets. Les faux sites glissent souvent de vrais noms de marque dans des adresses étranges.",
                "rw": "Link «{x}» ni aderesi ndende ifite utumenyetso. Imbuga z'uburiganya zikunze gushyiramo amazina y'ibigo nyabyo kugira ngo zisa n'izukuri.",
                "sw": "Kiungo «{x}» ni anwani ndefu yenye vistari. Tovuti za utapeli mara nyingi huweka majina halisi ya chapa ili zionekane halali."},
 "url_plain": {"en": "It contains the link «{x}». Do not log in, pay or enter codes through a link you were sent; type the official address yourself or use the official app.",
               "fr": "Il contient le lien « {x} ». Ne vous connectez, ne payez et n'entrez aucun code via un lien reçu ; tapez l'adresse officielle ou utilisez l'appli officielle.",
               "rw": "Irimo link «{x}». Ntuzigere winjira, wishyura cyangwa wandika kode unyuze kuri link wohererejwe; andika wowe aderesi yemewe cyangwa ukoreshe porogaramu yemewe.",
               "sw": "Una kiungo «{x}». Usiingie, kulipa au kuweka msimbo kupitia kiungo ulichotumiwa; andika mwenyewe anwani rasmi au tumia programu rasmi."},
 "ask_code": {"en": "It asks for a PIN, password or code. No bank, operator or company needs these from you, and a code you receive is a key to your account.",
              "fr": "Il demande un PIN, mot de passe ou code. Aucune banque, opérateur ou entreprise n'en a besoin, et un code reçu est la clé de votre compte.",
              "rw": "Irasaba PIN, ijambo ry'ibanga cyangwa kode. Nta banki, sosiyete cyangwa ikigo bikenera ibi, kandi kode wahawe ni urufunguzo rwa konti yawe.",
              "sw": "Inaomba PIN, nenosiri au msimbo. Hakuna benki, kampuni ya simu au shirika linalohitaji hivi, na msimbo uliopokea ni ufunguo wa akaunti yako."},
 "ask_install": {"en": "It asks you to install or open a file or app. Install only from the official app store, never from a link or file sent to you.",
                 "fr": "Il vous demande d'installer ou d'ouvrir un fichier ou une appli. N'installez que depuis la boutique officielle, jamais via un lien ou fichier reçu.",
                 "rw": "Irasaba gushyiraho cyangwa gufungura dosiye cyangwa porogaramu. Shyiraho gusa izituruka mu iduka ryemewe, ntuzigere ukoresha link cyangwa dosiye wohererejwe.",
                 "sw": "Inakuomba kusakinisha au kufungua faili au programu. Sakinisha kutoka duka rasmi pekee, kamwe si kupitia kiungo au faili ulilotumiwa."},
 "ask_secret": {"en": "It asks you to keep this secret. Anyone who wants you to hide a request from family, your bank or colleagues is trying to stop people from warning you.",
                "fr": "Il demande de garder le secret. Quiconque veut vous faire cacher une demande à votre famille, banque ou collègues veut empêcher qu'on vous prévienne.",
                "rw": "Irasaba kubigira ibanga. Uwifuza ko ugira ibanga icyo asaba imiryango, banki cyangwa abakozi mukorana aba ashaka kubuza abantu kukuburira.",
                "sw": "Inakuomba kuiweka siri. Anayetaka ufiche ombi kutoka kwa familia, benki au wafanyakazi wenzako anajaribu kuzuia watu wasikuonye."},
 "ask_personal": {"en": "It asks for personal details (ID number, card number, date of birth or similar). These are used for identity theft and for taking over your accounts.",
                  "fr": "Il demande des données personnelles (numéro d'identité, de carte, date de naissance…). Elles servent au vol d'identité et à prendre le contrôle de vos comptes.",
                  "rw": "Irasaba amakuru bwite (nimero y'indangamuntu, y'ikarita, itariki y'amavuko…). Akoreshwa mu kwiba umwirondoro no gufata konti zawe.",
                  "sw": "Inaomba taarifa binafsi (namba ya kitambulisho, kadi, tarehe ya kuzaliwa…). Hutumika kuiba utambulisho na kuchukua akaunti zako."},
 "ask_callback": {"en": "It wants you to call back or reply. Replying confirms your number is active and starts a conversation designed to pressure you; call only an official number you looked up yourself.",
                  "fr": "Il veut que vous rappeliez ou répondiez. Répondre confirme que votre numéro est actif et lance une conversation conçue pour vous presser ; appelez seulement un numéro officiel trouvé par vous-même.",
                  "rw": "Irashaka ko uhamagara cyangwa usubiza. Gusubiza byemeza ko nimero yawe ikora kandi bitangiza ikiganiro cyagenewe kugukanda; hamagara gusa nimero yemewe wishakiye.",
                  "sw": "Inataka upige tena au ujibu. Kujibu kunathibitisha namba yako inatumika na kuanzisha mazungumzo ya kukushinikiza; piga namba rasmi uliyoitafuta mwenyewe tu."},
}
_PERSONAL = re.compile(r"\b(?:id number|national id|nida|passport|date of birth|dob|card number|cvv|bank account number|mother'?s maiden|numero de (?:carte|piece|identite)|date de naissance|nimero y'indangamuntu|indangamuntu yawe|itariki y'amavuko|nambari ya (?:kitambulisho|kadi)|namba ya kitambulisho|tarehe ya kuzaliwa)\b", re.I)
_CODEW = re.compile(r"\b(?:pin|otp|password|passcode|one[- ]time|verification code|code|kode|msimbo|nenosiri|mot de passe|ijambo ry'ibanga|umubare w'ibanga|namba ya siri|cvv|recovery phrase|seed phrase)\b", re.I)
_INSTALLW = re.compile(r"\b(?:install|download|apk|anydesk|teamviewer|enable (?:content|macros)|open the attachment|installez|telechargez|shyiraho|kuramo|fungura dosiye|pakua|sakinisha|fungua faili)\b", re.I)
_SECRETW = re.compile(r"\b(?:do not tell|don't tell|keep (?:it|this) (?:secret|confidential|between us)|tell no one|confidential|ne le dites|gardez le secret|ntubibwire|bigire ibanga|usimwambie|weka siri|usiseme)\b", re.I)
_CALLW = re.compile(r"\b(?:call (?:back|us|me|now)|reply|text (?:us|me)|whatsapp (?:us|me)|contact us on|rappelez|repondez|ecrivez-nous|hamagara|subiza|nsubiza|andikira|piga simu|jibu|tuandikie)\b", re.I)
_NEG = re.compile(r"\b(?:never|do not|don't|dont|should not|must not|will not|won't|jamais|ne (?:pas|partagez|donnez|communiquez)|ntuzigere|ntugasangize|ntukagire|kamwe|usishiriki|usimpe|usitoe)\b", re.I)


def _plain(t):
    return t.strip().rstrip(".,;:!?)")


def domain_of(url):
    u = re.sub(r"^[a-z]+://", "", url.strip(), flags=re.I)
    u = re.split(r"[/?#]", u, 1)[0].lower().strip(".")
    u = u.split("@")[-1].split(":")[0]
    return re.sub(r"^www\.", "", u)


def _brand_in(domain_folded):
    hits = []
    toks = [t for t in re.split(r"[.\-_0-9]+", domain_folded) if t]
    for b, offs in OFFICIAL.items():
        near = any(t == b or (len(b) >= 4 and b in t) or (len(b) <= 3 and t.startswith(b) and len(t) >= len(b) + 3) for t in toks)
        if near and not any(domain_folded == o or domain_folded.endswith("." + o) for o in offs):
            hits.append((b, offs))
    return hits


def _unprotected(f, m):
    """True when the match is not inside a prohibition ('never share your PIN')."""
    last = 0
    for s in re.finditer(r"[.!?\n]\s", f[:m.start()]):
        last = s.end()
    return not _NEG.search(f[last:m.start()][-80:])


def facts(text):
    """Dict of the concrete things found in the message (for display and for tests)."""
    f = fold(text or "")
    out = {"amounts": [], "phones": [], "urls": [], "deadlines": [], "asks": []}
    for m in _AMOUNT.finditer(text or ""):
        a = _plain(m.group(0))
        if a not in out["amounts"] and re.search(r"\d", a):
            out["amounts"].append(a)
    for m in _PHONE.finditer(text or ""):
        p = _plain(m.group(1))
        digits = re.sub(r"\D", "", p)
        if 9 <= len(digits) <= 14 and p not in out["phones"]:
            out["phones"].append(p)
    for m in _URL.finditer(text or ""):
        u = _plain(m.group(0))
        if "@" in u and "/" not in u:
            continue
        if re.fullmatch(r"\d[\d.]*", u):
            continue
        if u not in out["urls"]:
            out["urls"].append(u)
    for m in _DEADLINE.finditer(f):
        d = _plain(text[m.start():m.end()])
        if d.lower() not in [x.lower() for x in out["deadlines"]]:
            out["deadlines"].append(d)
    pay = any(_unprotected(f, m) for m in _PAYVERB.finditer(f))
    if pay and out["amounts"]:
        out["asks"].append("amount_pay")
    _req = re.compile(r"\b(?:send|share|give|provide|enter|reply|forward|confirm|tell|read out|donnez|envoyez|communiquez|saisissez|tanga|ohereza|mpa|andika|emeza|toa|tuma|nipe|weka|nitumie|nyoherereza)\w*", re.I)
    if any(_unprotected(f, m) for m in _CODEW.finditer(f)) and any(_unprotected(f, m) for m in _req.finditer(f)):
        out["asks"].append("ask_code")
    if _INSTALLW.search(f):
        out["asks"].append("ask_install")
    if _SECRETW.search(f):
        out["asks"].append("ask_secret")
    if _PERSONAL.search(f):
        out["asks"].append("ask_personal")
    if _CALLW.search(f):
        out["asks"].append("ask_callback")
    return out


def details(text, lang="en", limit=7):
    """Message-specific explanation lines (most important first), in `lang`."""
    k = lang if lang in LANGS else "en"
    d = facts(text)
    lines = []
    for u in d["urls"][:3]:
        dom = domain_of(u)
        fd = fold(dom)
        if dom in _SHORT or any(dom.endswith(s) for s in _SHORT[:-2]):
            lines.append(T["url_short"][k].format(x=dom))
            continue
        brands = _brand_in(fd)
        if brands:
            b, offs = brands[0]
            lines.append(T["url_brand"][k].format(x=dom, b=b.upper() if len(b) <= 4 else b.capitalize(), o=" / ".join(offs[:2])))
            continue
        tld = dom.rsplit(".", 1)[-1] if "." in dom else ""
        if tld in _RISKY_TLD:
            lines.append(T["url_tld"][k].format(x=dom, t=tld))
        elif dom.count("-") >= 2:
            lines.append(T["url_hyphen"][k].format(x=dom))
        else:
            lines.append(T["url_plain"][k].format(x=dom))
    for a in d["asks"]:
        if a == "amount_pay":
            lines.append(T["amount_pay"][k].format(x=", ".join(d["amounts"][:3])))
        else:
            lines.append(T[a][k])
    if d["amounts"] and "amount_pay" not in d["asks"]:
        lines.append(T["amount"][k].format(x=", ".join(d["amounts"][:3])))
    if d["phones"]:
        lines.append(T["phone"][k].format(x=", ".join(d["phones"][:2])))
    if d["deadlines"]:
        lines.append(T["deadline"][k].format(x=d["deadlines"][0]))
    return lines[:limit]
