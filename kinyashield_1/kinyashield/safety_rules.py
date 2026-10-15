"""KinyaShield RW: rule definitions and safety advice, in four languages.

Languages: en (English), fr (Francais), rw (Kinyarwanda), sw (Kiswahili).

Authoring rules (checked by check_all.py):
- Patterns are raw strings (r"...") and must be ASCII only. Text is accent-folded
  before matching (e -> e, c -> c), so write "verifiez", not "verifiez" with accents.
- Patterns are shared with the web app through rules.json (python export_rules.py).
- fr, rw and sw wording is DRAFT until reviewed by fluent speakers.
- "low" severity only supports other findings; it never raises a verdict alone.
"""

LANGS = ["en", "fr", "rw", "sw"]
LANG_NAMES = {"en": "English", "fr": "Français", "rw": "Kinyarwanda", "sw": "Kiswahili"}

# A match is ignored when one of these matches the text just before it in the same
# sentence: the sentence is a warning ("never share your PIN"), not a request.
PROTECTIVE_PREFIX = {
    "en": [
        r"\b(?:never|do not|don't|dont|should not|shouldn't|must not|mustn't|won't|will not|not to)\s+(?:ever\s+)?$",
        r"\b(?:never|no\s+\w+|nobody|not|n't|don't|won't)\b[^,;]*\b(?:ask|asks|asking|request|requests|require|requires|tell)\w*\b[^,;]*$",
    ],
    "fr": [
        r"\bn(?:e|')\s*$",
        r"\bjamais\s+$",
        r"\b(?:aucun\w*|personne|jamais|pas)\b[^,;]*\b(?:demand|exig|solicit)\w*\b[^,;]*$",
    ],
    "rw": [
        r"\b(?:ntugasangize|ntugatange|ntukohereze|ntukamuhe|ntukabwire|ntuzigere|ntituzigera|ntituzigere)\b[^,;]*$",
    ],
    "sw": [
        r"\b(?:kamwe|hatutakuomba|hatutaomba|hatuombi|haitakuuliza|hawatakuuliza|hatutakuuliza|hakuna\s+\w+\s+itakayokuomba)\b[^,;]*$",
    ],
}

MONEY_EN = r"(?:money|funds|amount|rwf|frw|\d[\d,. ]*\s?(?:rwf|frw))"

RULES = [
    {
        "id": "credential_request",
        "severity": "high",
        "suppress_if_protective": True,
        "title": {
            "en": "Asks for a PIN, password or code",
            "fr": "Demande un code PIN, un mot de passe ou un code",
            "rw": "Irasaba PIN, ijambo ry'ibanga cyangwa kode",
            "sw": "Inaomba PIN, nenosiri au msimbo",
        },
        "why": {
            "en": "Genuine banks, mobile-money companies and officials do not ask you to send or read out a PIN, password or one-time code.",
            "fr": "Les vraies banques, opérateurs de mobile money et autorités ne vous demandent jamais d'envoyer ou de lire à voix haute un code PIN, un mot de passe ou un code à usage unique.",
            "rw": "Banki, ibigo bya mobile money n'abayobozi nyakuri ntibasaba kohereza cyangwa kuvuga PIN, ijambo ry'ibanga cyangwa kode y'inyongera.",
            "sw": "Benki, kampuni za pesa kwa simu na maafisa halali hawakuombi kutuma wala kusoma kwa sauti PIN, nenosiri au msimbo wa mara moja.",
        },
        "advice": {
            "en": "Do not send or read out the code. Contact the organisation using a number from its official website or your card.",
            "fr": "N'envoyez pas le code et ne le lisez pas. Contactez l'organisme avec un numéro tiré de son site officiel ou de votre carte.",
            "rw": "Ntukohereze cyangwa ngo uvuge iyo kode. Hamagara ikigo ukoresheje nimero iri ku rubuga rwacyo rwemewe cyangwa ku ikarita yawe.",
            "sw": "Usitume wala usisome msimbo huo. Wasiliana na taasisi kwa kutumia namba iliyo kwenye tovuti yake rasmi au kwenye kadi yako.",
        },
        "patterns": {
            "en": [r"\b(?:send|share|give|tell|provide|reply with|forward|confirm|enter|read out)\b[^.!?\n]{0,40}?\b(?:pin|password|passcode|otp|cvv|verification code|one[- ]time (?:code|password)|secret code|secret number|secret pin|\d+[- ]?digit (?:code|pin)|code (?:we|i|that we) (?:just )?(?:sent|texted))\b"],
            "fr": [r"\b(?:envoyez?|envoyer|donnez?|donner|communiquez?|communiquer|partagez?|partager|fournissez?|fournir|transmettez?|transmettre|confirmez?|confirmer|saisissez?|saisir|lisez|dites(?:-moi)?|repondez avec)\b[^.!?\n]{0,40}?\b(?:pin|code pin|mot de passe|code secret|code de verification|code otp|otp|cvv|code confidentiel|code a \d+ chiffres|code recu par sms)\b"],
            "rw": [r"\b(?:ohereza|mpa|mpe|tanga|mbwira|tuma)\b[^.!?\n]{0,40}?\b(?:pin|umubare w'ibanga|ijambo ry'ibanga|kode|code|otp|password)\b"],
            "sw": [r"\b(?:tuma|nitumie|toa|nipe|nipatie|nitajie|thibitisha|weka|ingiza|jibu na|shiriki|mpe|mwambie)\b[^.!?\n]{0,40}?\b(?:pin|nambari ya siri|namba ya siri|nenosiri|neno la siri|msimbo|msimbo wa tarakimu \d+|kodi|code|otp|cvv)\b"],
        },
    },
    {
        "id": "advance_fee",
        "severity": "high",
        "suppress_if_protective": True,
        "title": {
            "en": "Asks you to pay first to receive something",
            "fr": "Demande de payer d'abord pour recevoir quelque chose",
            "rw": "Irasaba kubanza kwishyura kugira ngo ubone ikintu",
            "sw": "Inakuomba ulipe kwanza ili upokee kitu",
        },
        "why": {
            "en": "Scams often ask for a small 'fee' before a prize, loan, parcel or scholarship is released. The reward never arrives.",
            "fr": "Les arnaques demandent souvent de petits « frais » avant de débloquer un gain, un prêt, un colis ou une bourse. Rien n'arrive jamais.",
            "rw": "Abatekamutwe bakunze gusaba 'amafaranga make' mbere yo kukugezaho igihembo, inguzanyo, ipaki cyangwa buruse. Igihembo ntikiza.",
            "sw": "Matapeli mara nyingi huomba 'ada ndogo' kabla ya kutoa zawadi, mkopo, kifurushi au ufadhili. Hakuna kinachofika.",
        },
        "advice": {
            "en": "Do not pay. Check with the organisation directly, using contact details you find yourself.",
            "fr": "Ne payez pas. Vérifiez auprès de l'organisme avec des coordonnées que vous trouvez vous-même.",
            "rw": "Ntukishyure. Baza ikigo ubwacyo ukoresheje amakuru wibonera ubwawe.",
            "sw": "Usilipe. Thibitisha moja kwa moja na taasisi ukitumia mawasiliano unayoyapata mwenyewe.",
        },
        "patterns": {
            "en": [
                r"\b(?:pay|send|deposit|transfer)\b[^.!?\n]{0,40}?\b(?:fee|fees|charge|charges|tax|registration|processing|clearance|shipping|delivery)\b[^.!?\n]{0,60}?\b(?:to (?:receive|claim|release|get|unlock|activate|collect)|before (?:you )?(?:receive|collect|claim)|in order to)\b",
                r"\bto (?:receive|claim|release|collect|unlock)\b[^.!?\n]{0,40}\b(?:prize|scholarship|loan|parcel|package|reward|gift|funds)\b[^.!?\n]{0,50}\b(?:pay|send|deposit)\b[^.!?\n]{0,30}\b(?:fee|fees|rwf|frw)\b",
            ],
            "fr": [
                r"\b(?:payez?|payer|versez?|verser|envoyez?|envoyer|deposez?|transferez?)\b[^.!?\n]{0,40}?\b(?:frais|taxe|taxes|droits?|commission|caution)\b[^.!?\n]{0,60}?\b(?:pour (?:recevoir|obtenir|debloquer|reclamer|retirer|toucher|activer)|avant de (?:recevoir|retirer|toucher))\b",
                r"\bpour (?:recevoir|reclamer|debloquer|retirer|toucher|obtenir)\b[^.!?\n]{0,40}\b(?:prix|gain|gains|bourse|pret|colis|cadeau|fonds|lot)\b[^.!?\n]{0,50}\b(?:payez?|envoyez?|versez?)\b[^.!?\n]{0,30}\b(?:frais|rwf|frw|fcfa|usd)\b",
            ],
            "rw": [
                r"\b(?:ishyura|kwishyura|ohereza|tanga)\b[^.!?\n]{0,50}?\b(?:amafaranga|frw|rwf|ubwishyu|frais)\b[^.!?\n]{0,60}?\b(?:kugira ngo|kugirango|mbere yo)\b",
            ],
            "sw": [
                r"\b(?:lipa|tuma|weka|toa)\b[^.!?\n]{0,50}?\b(?:ada|ushuru|gharama|malipo|tsh|rwf|frw|kes)\b[^.!?\n]{0,60}?\b(?:ili (?:u(?:i|ya|zi|li)?(?:pate|pokee)|kupokea|kupata|kutoa|kuchukua)|kabla ya kupokea)\b",
                r"\bili (?:upokee|upate|kupokea|kupata|uchukue)\b[^.!?\n]{0,40}\b(?:zawadi|tuzo|mkopo|ufadhili|kifurushi|fedha|pesa)\b[^.!?\n]{0,50}\b(?:lipa|tuma)\b[^.!?\n]{0,30}\b(?:ada|ushuru|tsh|rwf|frw|kes)\b",
            ],
        },
    },
    {
        "id": "remote_access",
        "severity": "high",
        "suppress_if_protective": True,
        "title": {
            "en": "Asks you to install remote-control software",
            "fr": "Demande d'installer un logiciel de contrôle à distance",
            "rw": "Irasaba gushyira kuri telefoni porogaramu yo kuyigenzura kure",
            "sw": "Inakuomba usakinishe programu ya kudhibiti simu kwa mbali",
        },
        "why": {
            "en": "Remote-access apps let someone see and control your phone or bank app.",
            "fr": "Ces applications permettent à quelqu'un de voir et de contrôler votre téléphone ou votre appli bancaire.",
            "rw": "Porogaramu zo kugenzura kure zituma undi muntu abona kandi agakoresha telefoni yawe cyangwa porogaramu ya banki.",
            "sw": "Programu hizi humruhusu mtu kuona na kudhibiti simu au programu yako ya benki.",
        },
        "advice": {
            "en": "Do not install it. End the conversation and contact your bank through its official channel.",
            "fr": "Ne l'installez pas. Coupez la conversation et contactez votre banque par son canal officiel.",
            "rw": "Ntuyishyire kuri telefoni. Hagarika ikiganiro maze uvugane na banki yawe unyuze mu nzira yemewe.",
            "sw": "Usiisakinishe. Maliza mazungumzo na uwasiliane na benki yako kupitia njia rasmi.",
        },
        "patterns": {
            "en": [r"\b(?:install|download)\b[^.!?\n]{0,30}\b(?:anydesk|teamviewer|quicksupport|remote (?:access|support|control) (?:app|software))\b"],
            "fr": [r"\b(?:installez?|installer|telechargez?|telecharger)\b[^.!?\n]{0,30}\b(?:anydesk|teamviewer|quicksupport|application de (?:controle|prise en main|assistance) a distance|logiciel de controle a distance)\b"],
            "rw": [],
            "sw": [r"\b(?:sakinisha|pakua|install)\b[^.!?\n]{0,30}\b(?:anydesk|teamviewer|quicksupport|programu ya kudhibiti simu)\b"],
        },
    },
    {
        "id": "mistaken_transfer",
        "severity": "medium",
        "suppress_if_protective": False,
        "title": {
            "en": "Says money was sent by mistake and asks for it back",
            "fr": "Dit avoir envoyé de l'argent par erreur et le réclame",
            "rw": "Ivuga ko amafaranga yoherejwe kubw'impanuka kandi irayasaba",
            "sw": "Inasema pesa zilitumwa kimakosa na inazidai",
        },
        "why": {
            "en": "A common trick: a fake or reversed payment, then a request to 'return' the money.",
            "fr": "Astuce courante : un faux paiement ou un paiement annulé, puis une demande de « rendre » l'argent.",
            "rw": "Uburiganya buzwi: bohereza amafaranga y'ibinyoma, hanyuma bagusaba 'kuyasubiza'.",
            "sw": "Mbinu ya kawaida: malipo bandia au yaliyorudishwa, kisha ombi la 'kurudisha' pesa.",
        },
        "advice": {
            "en": "Check your own balance in your official app or at an agent. Do not send money back until you have confirmed it really arrived.",
            "fr": "Vérifiez votre solde dans l'appli officielle ou chez un agent. Ne renvoyez rien avant d'avoir confirmé que l'argent est vraiment arrivé.",
            "rw": "Reba amafaranga ufite muri porogaramu yemewe cyangwa ku mukozi. Ntusubize amafaranga utarabyemeza ko yaje koko.",
            "sw": "Angalia salio lako kwenye programu rasmi au kwa wakala. Usirudishe pesa hadi uthibitishe kuwa zimefika kweli.",
        },
        "patterns": {
            "en": [
                r"\b(?:sent|transferred|deposited)\b[^.!?\n]{0,30}\b" + MONEY_EN + r"\b[^.!?\n]{0,40}\b(?:by mistake|mistakenly|accidentally|wrong number|in error)\b",
                r"\b(?:by mistake|mistakenly|accidentally|wrong number)\b[^.!?\n]{0,60}\b(?:send back|return|refund)\b[^.!?\n]{0,30}\b(?:money|funds|amount|rwf|frw)\b",
                r"\b(?:send back|return)\b[^.!?\n]{0,15}\b(?:my|the)\b[^.!?\n]{0,15}\b(?:money|funds|amount|cash)\b",
            ],
            "fr": [
                r"\b(?:envoye|envoyer|transfere|transferer|depose|deposer|verse|verser|vire|virer)\b[^.!?\n]{0,30}\b(?:argent|fonds|montant|somme|rwf|frw|fcfa|\d[\d,. ]*\s?(?:rwf|frw|fcfa))\b[^.!?\n]{0,40}\b(?:par erreur|par megarde|a tort|mauvais numero)\b",
                r"\b(?:par erreur|mauvais numero)\b[^.!?\n]{0,60}\b(?:renvoyez|rembours\w*|retournez|rendez)\b[^.!?\n]{0,30}\b(?:argent|fonds|montant|somme)\b",
                r"\b(?:renvoyez|rendez|retournez)(?:-moi)?\s+(?:mon\s+|l')?(?:argent|fonds|montant)\b",
            ],
            "rw": [
                r"\b(?:nakohereje|nohereje|bakohereje)\b[^.!?\n]{0,50}\b(?:kubw'impanuka|kwibeshya|nabi)\b",
                r"\b(?:nsubiza|subiza)\b[^.!?\n]{0,20}\bamafaranga\b",
            ],
            "sw": [
                r"\b(?:nimekutumia|nimetuma|nilituma)\b[^.!?\n]{0,30}\b(?:pesa|fedha|kiasi|tsh|rwf|frw|kes|\d[\d,\.]*\s?(?:tsh|rwf|frw|kes))\b[^.!?\n]{0,40}\b(?:kimakosa|kwa makosa|namba mbaya)\b",
                r"\b(?:nirudishie|rudisha)\b[^.!?\n]{0,20}\b(?:pesa|fedha)\b",
            ],
        },
    },
    {
        "id": "prize_claim",
        "severity": "medium",
        "suppress_if_protective": False,
        # Genuine achievement wording in the same sentence cancels the match, unless the sentence
        # also contains money, a link or an action word (claim, pay, click...), which is how scams talk.
        "unless": [r"\b(?:first|second|third|1st|2nd|3rd) (?:prize|place)\b", r"\b(?:premier|deuxieme|troisieme) (?:prix|place)\b",
                   r"\bnafasi ya (?:kwanza|pili|tatu)\b", r"\bumwanya wa (?:mbere|kabiri|gatatu)\b",
                   r"\b(?:science fair|concours de sciences|maonyesho ya sayansi|irushanwa)\b"],
        "keep_if": [r"\d[\d,. ]*\s?(?:rwf|frw|fcfa|tsh|kes|ugx|usd|eur)\b", r"https?://",
                    r"\b(?:claim|collect|reply|click|pay|payez|cliquez|reclamer|lipa|bofya|ishyura|kanda)\b"],
        "title": {
            "en": "Says you won or were selected for a prize",
            "fr": "Annonce que vous avez gagné ou été sélectionné",
            "rw": "Ivuga ko watsinze cyangwa watoranyijwe guhabwa igihembo",
            "sw": "Inasema umeshinda au umechaguliwa kupata zawadi",
        },
        "why": {
            "en": "Unexpected prize messages are among the most common scams. You cannot win a draw you never entered.",
            "fr": "Les messages de gain inattendus figurent parmi les arnaques les plus courantes. On ne peut pas gagner un tirage auquel on n'a pas participé.",
            "rw": "Ubutumwa buvuga ko watsindiye igihembo utazi ni bumwe mu buriganya busanzwe. Ntushobora gutsinda tombola utigeze ugiramo uruhare.",
            "sw": "Ujumbe wa zawadi usiotarajiwa ni miongoni mwa utapeli unaojulikana zaidi. Huwezi kushinda droo ambayo hukushiriki.",
        },
        "advice": {
            "en": "Ignore it unless you know you entered. Never pay or share personal details to 'claim' a prize.",
            "fr": "Ignorez-le sauf si vous savez avoir participé. Ne payez jamais et ne donnez aucune information personnelle pour « réclamer » un gain.",
            "rw": "Ntibugire icyo bukubwira keretse ubizi ko wagiye muri iyo tombola. Ntukishyure cyangwa ngo utange amakuru bwite 'kugira ngo uhabwe' igihembo.",
            "sw": "Usiujali isipokuwa unajua ulishiriki. Usilipe wala kutoa taarifa binafsi ili 'kudai' zawadi.",
        },
        "patterns": {
            "en": [r"\b(?:you(?:'ve| have)? won|you were selected|you have been selected|selected to receive|lucky (?:draw|winner)|winner!)\b"],
            "fr": [r"\b(?:vous avez gagne|vous etes (?:le |la )?(?:gagnant|gagnante|selectionne|selectionnee|choisi|choisie)|gagnant du tirage|tirage au sort)\b"],
            "rw": [r"\b(?:watsindiye|mwatsindiye|wegukanye|mwegukanye|watoranyijwe|mwatoranyijwe)\b"],
            "sw": [r"\b(?:umeshinda|umechaguliwa kupokea|umechaguliwa kupata|umechaguliwa kuwa mshindi|mshindi wa bahati nasibu|droo ya bahati nasibu)\b"],
        },
    },
    {
        "id": "account_threat",
        "severity": "medium",
        "suppress_if_protective": True,
        "title": {
            "en": "Threatens to block or close your account or SIM",
            "fr": "Menace de bloquer ou fermer votre compte ou SIM",
            "rw": "Iragutera ubwoba ko konti cyangwa SIM yawe izafungwa",
            "sw": "Inatishia kufunga au kuzuia akaunti au laini yako",
        },
        "why": {
            "en": "Fear of losing access is used to rush people into clicking or sharing details.",
            "fr": "La peur de perdre l'accès sert à vous pousser à cliquer ou à donner vos informations.",
            "rw": "Ubwoba bwo gutakaza konti bukoreshwa kugira ngo abantu bihute gukanda cyangwa gutanga amakuru.",
            "sw": "Hofu ya kupoteza huduma hutumiwa kukusukuma ubonyeze viungo au utoe taarifa.",
        },
        "advice": {
            "en": "Do not follow links in the message. Open your official app or visit the provider yourself to check.",
            "fr": "Ne suivez pas les liens du message. Ouvrez votre appli officielle ou rendez-vous chez l'opérateur pour vérifier.",
            "rw": "Ntukande amahuza ari mu butumwa. Fungura porogaramu yemewe cyangwa ujye ku kigo ubwawe urebe.",
            "sw": "Usifuate viungo vilivyomo kwenye ujumbe. Fungua programu rasmi au tembelea mtoa huduma mwenyewe ukague.",
        },
        "patterns": {
            "en": [r"\b(?:account|sim|line|card|wallet)\b[^.!?\n]{0,40}\b(?:will be|has been|is being|been|was)\s+(?:suspended|blocked|closed|deactivated|locked|terminated)\b"],
            "fr": [r"\b(?:compte|carte|sim|ligne|portefeuille)\b[^.!?\n]{0,40}\b(?:sera|a ete|est|va etre|sont)\s+(?:suspendu|bloque|ferme|desactive|verrouille|resilie)(?:e|s|es)?\b"],
            "rw": [r"\b(?:konti|sim|karita)\b[^.!?\n]{0,40}\b(?:izafungwa|yafunzwe|ifunzwe|izahagarikwa|yahagaritswe|izasibwa)\b"],
            "sw": [r"\b(?:akaunti|laini|kadi|sim)\b[^.!?\n]{0,40}\b(?:itafungwa|imefungwa|itazuiwa|imezuiwa|itasimamishwa|imesimamishwa|itafutwa|imefutwa)\b"],
        },
    },
    {
        "id": "account_verification_request",
        "severity": "medium",
        "suppress_if_protective": True,
        "title": {
            "en": "Asks you to verify or update account details",
            "fr": "Demande de vérifier ou mettre à jour les informations du compte",
            "rw": "Irasaba kwemeza cyangwa kuvugurura amakuru ya konti",
            "sw": "Inakuomba uthibitishe au usasishe taarifa za akaunti",
        },
        "why": {
            "en": "'Verify your account' messages are often used to collect your login or ID details.",
            "fr": "Les messages « vérifiez votre compte » servent souvent à récupérer vos identifiants ou vos données d'identité.",
            "rw": "Ubutumwa busaba 'kwemeza konti' bukunze gukoreshwa mu gukusanya amakuru yo kwinjira cyangwa indangamuntu.",
            "sw": "Ujumbe wa 'thibitisha akaunti yako' mara nyingi hutumika kukusanya taarifa za kuingia au utambulisho.",
        },
        "advice": {
            "en": "Do not use links or numbers from the message. Go to the official website or branch yourself.",
            "fr": "N'utilisez ni liens ni numéros du message. Allez vous-même sur le site officiel ou en agence.",
            "rw": "Ntukoreshe amahuza cyangwa nimero ziri mu butumwa. Jya ku rubuga rwemewe cyangwa ku biro ubwawe.",
            "sw": "Usitumie viungo au namba zilizo kwenye ujumbe. Nenda mwenyewe kwenye tovuti rasmi au tawi.",
        },
        "patterns": {
            "en": [r"\b(?:verify|update|confirm|reactivate|re-?register)\b[^.!?\n]{0,25}\b(?:your )?(?:account|sim(?: card)?|kyc|identity|bank details|national id|id number|nida)\b"],
            "fr": [r"\b(?:verifiez?|verifier|mettez a jour|mettre a jour|confirmez?|confirmer|reactivez?|actualisez?)\b[^.!?\n]{0,25}\b(?:votre |vos )?(?:compte|sim|kyc|identite|coordonnees bancaires|donnees bancaires|numero d'identite|carte d'identite|nida)\b"],
            "rw": [r"\b(?:w?emeze|emeza|vugurura|uvugurure)\b[^.!?\n]{0,25}\b(?:konti|sim|nomero|amakuru yawe)\b"],
            "sw": [r"\b(?:ku)?(?:thibitisha|sasisha|hakiki)\b[^.!?\n]{0,25}\b(?:akaunti|laini|taarifa zako|taarifa za benki|namba yako|kitambulisho)\b"],
        },
    },
    {
        "id": "risky_link",
        "severity": "medium",
        "suppress_if_protective": False,
        "title": {
            "en": "Contains a link that hides or disguises its destination",
            "fr": "Contient un lien qui masque sa destination",
            "rw": "Ifite ihuza ritagaragaza aho rijya",
            "sw": "Ina kiungo kinachoficha kinakoelekea",
        },
        "why": {
            "en": "Shortened links, raw IP addresses and unusual web endings are often used to hide a fake site.",
            "fr": "Les liens raccourcis, les adresses IP brutes et les extensions inhabituelles servent souvent à cacher un faux site.",
            "rw": "Amahuza magufi, aderesi z'imibare n'iherezo ridasanzwe ry'urubuga bikunze gukoreshwa mu guhisha urubuga rw'uburiganya.",
            "sw": "Viungo vifupi, anwani za IP na miisho isiyo ya kawaida hutumiwa mara nyingi kuficha tovuti bandia.",
        },
        "advice": {
            "en": "Do not open it. Type the organisation's official address yourself.",
            "fr": "Ne l'ouvrez pas. Tapez vous-même l'adresse officielle de l'organisme.",
            "rw": "Ntuyifungure. Andika ubwawe aderesi yemewe y'ikigo.",
            "sw": "Usikifungue. Andika mwenyewe anwani rasmi ya taasisi.",
        },
        "patterns": {
            "any": [r"\b(?:bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|rb\.gy|shorturl\.at)/\S+",
                    r"https?://\d{1,3}(?:\.\d{1,3}){3}\S*",
                    r"https?://[^\s/]+\.(?:xyz|top|click|tk|icu|buzz|gq|cf)\b\S*"],
        },
    },
    {
        "id": "too_good_offer",
        "severity": "medium",
        "suppress_if_protective": True,
        "title": {
            "en": "Promises unrealistic money",
            "fr": "Promet de l'argent irréaliste",
            "rw": "Isezeranya amafaranga adashoboka",
            "sw": "Inaahidi pesa zisizo halisi",
        },
        "why": {
            "en": "Guaranteed or very fast returns are a classic sign of an investment scam.",
            "fr": "Des gains garantis ou très rapides sont un signe classique d'arnaque à l'investissement.",
            "rw": "Inyungu zemewe cyangwa zihuta cyane ni ikimenyetso gisanzwe cy'uburiganya mu ishoramari.",
            "sw": "Faida ya uhakika au ya haraka sana ni dalili ya kawaida ya utapeli wa uwekezaji.",
        },
        "advice": {
            "en": "Do not invest. Check whether the company is registered with the proper authority.",
            "fr": "N'investissez pas. Vérifiez que la société est enregistrée auprès de l'autorité compétente.",
            "rw": "Ntugashore. Reba niba ikigo cyanditse mu rwego rubifitiye ububasha.",
            "sw": "Usiwekeze. Hakiki kama kampuni imesajiliwa na mamlaka husika.",
        },
        "patterns": {
            "en": [r"\b(?:double your money|guaranteed returns?|easy money)\b", r"\bearn\b[^.!?\n]{0,25}\b(?:daily|per day|every day|weekly)\b"],
            "fr": [r"\b(?:doublez votre argent|rendements? garantis?|argent facile|gains? garantis?)\b", r"\bgagnez\b[^.!?\n]{0,25}\b(?:par jour|chaque jour|quotidien\w*|par semaine)\b"],
            "rw": [],
            "sw": [r"\b(?:mara mbili ya pesa yako|faida ya uhakika|pesa rahisi)\b", r"\b(?:pata|chuma)\b[^.!?\n]{0,25}\b(?:tsh|rwf|frw|kes|pesa|shilingi)\b[^.!?\n]{0,15}\b(?:kila siku|kwa siku|kila wiki)\b"],
        },
    },
    {
        "id": "upfront_payment_offer",
        "severity": "high",
        "suppress_if_protective": False,
        "title": {
            "en": "Asks for a payment up front for an offer (job, loan)",
            "fr": "Demande un paiement d'avance pour une offre (emploi, prêt)",
            "rw": "Irasaba kwishyura mbere ku mirimo cyangwa inguzanyo",
            "sw": "Inaomba malipo ya awali kwa ofa (kazi, mkopo)",
        },
        "why": {
            "en": "A real employer or lender does not ask for insurance, visa or processing money before paying you or starting work.",
            "fr": "Un vrai employeur ou prêteur ne demande pas d'argent pour l'assurance, le visa ou le dossier avant de vous payer ou de commencer.",
            "rw": "Umukoresha cyangwa umuguzanyi nyawe ntasaba amafaranga y'ubwishingizi, viza cyangwa ay'ibyangombwa mbere yo kuguha amafaranga cyangwa akazi.",
            "sw": "Mwajiri au mkopeshaji halali haombi pesa za bima, viza au usindikaji kabla ya kukulipa au kuanza kazi.",
        },
        "advice": {
            "en": "Do not pay anything up front. Check the offer with the organisation using contact details you find yourself.",
            "fr": "Ne payez rien d'avance. Vérifiez l'offre auprès de l'organisme avec des coordonnées que vous trouvez vous-même.",
            "rw": "Ntukishyure mbere. Baza ikigo ukoresheje amakuru wibonera ubwawe.",
            "sw": "Usilipe chochote mapema. Hakiki ofa na taasisi kwa mawasiliano unayoyapata mwenyewe.",
        },
        "groups": [
            {
                "en": [r"\b(?:job offer|vacancy|we are hiring|recruiting|work abroad|you qualify|you are eligible|pre-?approved|loan offer)\b"],
                "fr": [r"\b(?:offre d'emploi|poste vacant|nous recrutons|travailler a l'etranger|vous etes eligible|vous etes preapprouve|offre de pret)\b"],
                "rw": [r"\b(?:amahirwe y'akazi|akazi hanze y'igihugu|wujuje ibisabwa|inguzanyo wemerewe)\b"],
                "sw": [r"\b(?:nafasi ya kazi|ofa ya kazi|tunaajiri|kazi nje ya nchi|umeidhinishwa mkopo|ofa ya mkopo)\b"],
            },
            {
                "en": [r"\b(?:deposit|pay|send)\b[^.!?\n]{0,30}\b(?:\d[\d,. ]*\s?(?:rwf|frw|usd|ksh|tsh|eur)|(?:rwf|frw|usd|ksh|tsh|eur)\s?\d[\d,. ]*)\b[^.!?\n]{0,40}\b(?:insurance|processing|visa|clearance|activation|upfront|admin|first|before)\b"],
                "fr": [r"\b(?:versez|payez|envoyez|deposez)\b[^.!?\n]{0,30}\b(?:\d[\d,. ]*\s?(?:rwf|frw|fcfa|usd|eur)|(?:rwf|frw|fcfa|usd|eur)\s?\d[\d,. ]*)\b[^.!?\n]{0,40}\b(?:assurance|visa|dedouanement|activation|d'avance|avant)\b"],
                "rw": [r"\b(?:ohereza|ishyura|tanga)\b[^.!?\n]{0,30}\b(?:\d[\d,. ]*\s?(?:frw|rwf)|(?:frw|rwf)\s?\d[\d,. ]*)\b[^.!?\n]{0,40}\b(?:ubwishingizi|viza|frais|mbere)\b"],
                "sw": [r"\b(?:lipa|tuma|weka)\b[^.!?\n]{0,30}\b(?:\d[\d,. ]*\s?(?:tsh|kes|ugx|rwf|frw|usd)|(?:tsh|kes|ugx|rwf|frw|usd)\s?\d[\d,. ]*)\b[^.!?\n]{0,40}\b(?:bima|viza|usindikaji|mapema|kwanza|kabla)\b"],
            },
        ],
    },
    {
        "id": "family_emergency_money",
        "severity": "medium",
        "suppress_if_protective": False,
        "title": {
            "en": "Pretends to be a relative in trouble and asks for money",
            "fr": "Se fait passer pour un proche en difficulté et demande de l'argent",
            "rw": "Yiyita umuvandimwe ufite ikibazo igusaba amafaranga",
            "sw": "Inajifanya kuwa ndugu mwenye shida na kuomba pesa",
        },
        "why": {
            "en": "Scammers claim to be a family member with a new number or an emergency so you send money before thinking.",
            "fr": "Les escrocs prétendent être un proche avec un nouveau numéro ou une urgence pour que vous envoyiez de l'argent sans réfléchir.",
            "rw": "Abatekamutwe biyita abavandimwe bafite nimero nshya cyangwa ikibazo kugira ngo wohereze amafaranga utabanje gutekereza.",
            "sw": "Matapeli hudai kuwa ndugu mwenye namba mpya au dharura ili utume pesa kabla ya kufikiri.",
        },
        "advice": {
            "en": "Call the person on their old number, or ask a question only they could answer, before sending anything.",
            "fr": "Appelez la personne sur son ancien numéro, ou posez une question que seule elle connaît, avant d'envoyer quoi que ce soit.",
            "rw": "Hamagara uwo muntu kuri nimero ye isanzwe, cyangwa umubaze ikibazo wenyine azi, mbere yo kohereza ikintu icyo ari cyo cyose.",
            "sw": "Mpigie mtu huyo kwa namba yake ya zamani, au muulize swali ambalo yeye tu anajua, kabla ya kutuma chochote.",
        },
        "groups": [
            {
                "en": [r"\b(?:it is me|it's me|this is your (?:mum|mom|dad|son|daughter|brother|sister)|i changed my number|my new number|new number|lost my phone|my phone (?:is )?(?:broken|stolen|lost)|using (?:a )?friend's (?:number|phone)|i am stuck at|i'm stuck at|stranded)\b"],
                "fr": [r"\b(?:c'est moi|j'ai change de numero|nouveau numero|j'ai perdu mon telephone|mon telephone est (?:casse|perdu|vole)|j'utilise le numero d'un|je suis bloque)\b"],
                "rw": [r"\b(?:ndi mubyara wawe|ndi mama|ndi papa|ndi musaza wawe|ndi mushiki wawe|nahinduye nimero|nimero nshya|telefoni yanjye (?:yangiritse|yibwe)|nagize ikibazo|ndi mu kaga)\b"],
                "sw": [r"\b(?:ni mimi|nimebadilisha namba|namba mpya|nimepoteza simu|simu yangu (?:imeibiwa|imeharibika)|natumia namba ya rafiki|nimekwama)\b"],
            },
            {
                "en": [r"\b(?:send|give|lend|transfer)\b[^.!?\n]{0,20}\b(?:me|us)\b[^.!?\n]{0,30}\b(?:money|cash|airtime|\d[\d,. ]*\s?(?:rwf|frw|usd))\b", r"\bi need\b[^.!?\n]{0,15}\b(?:money|cash|airtime)\b"],
                "fr": [r"\b(?:envoie|envoyez|donne|donnez|prete|pretez)(?:-moi)?\b[^.!?\n]{0,25}\b(?:argent|credit|\d[\d,. ]*\s?(?:rwf|frw|fcfa|usd))\b", r"\bj'ai besoin d'argent\b"],
                "rw": [r"\b(?:ohereza|mpa|ndakeneye)\b[^.!?\n]{0,30}\bamafaranga\b"],
                "sw": [r"\b(?:nitumie|tuma|nipe|nikopeshe)\b[^.!?\n]{0,25}\b(?:pesa|fedha|hela|tsh|kes|ugx|rwf|frw)\b", r"\bnahitaji pesa\b", r"\bninahitaji pesa\b"],
            },
        ],
    },
    {
        "id": "offplatform_contact",
        "severity": "medium",
        "suppress_if_protective": False,
        "title": {
            "en": "Pushes you to continue a job offer on WhatsApp or Telegram",
            "fr": "Vous pousse à poursuivre une offre d'emploi sur WhatsApp ou Telegram",
            "rw": "Igukururira kuri WhatsApp cyangwa Telegram ku kazi",
            "sw": "Inakuvuta kwenye WhatsApp au Telegram kwa ofa ya kazi",
        },
        "why": {
            "en": "Fake job offers quickly move the conversation to a private chat so nobody can check them.",
            "fr": "Les fausses offres d'emploi déplacent vite la conversation vers une messagerie privée pour échapper aux vérifications.",
            "rw": "Amatangazo y'akazi y'ibinyoma ahita yimura ikiganiro kuri messagerie yihariye kugira ngo hatagira ugenzura.",
            "sw": "Ofa bandia za kazi huhamisha mazungumzo haraka kwenye gumzo la faragha ili kuepuka uhakiki.",
        },
        "advice": {
            "en": "Check the company and the recruiter on official sources before replying.",
            "fr": "Vérifiez l'entreprise et le recruteur sur des sources officielles avant de répondre.",
            "rw": "Genzura ikigo n'uwakoresha mu nzira zemewe mbere yo gusubiza.",
            "sw": "Hakiki kampuni na mwajiri kwa vyanzo rasmi kabla ya kujibu.",
        },
        "groups": [
            {
                "en": [r"\b(?:recruiter|hiring manager|vacancy|job offer|your cv|saw your cv|work from home)\b"],
                "fr": [r"\b(?:recruteur|offre d'emploi|votre cv|poste vacant|teletravail)\b"],
                "rw": [r"\b(?:umukoresha|cv yawe|amahirwe y'akazi|gusaba akazi)\b"],
                "sw": [r"\b(?:mwajiri|nafasi ya kazi|cv yako|kazi ya nyumbani)\b"],
            },
            {
                "en": [r"\b(?:contact|message|chat|text|reach|add)\b[^.!?\n]{0,30}\b(?:whatsapp|telegram|signal)\b"],
                "fr": [r"\b(?:contactez|ecrivez|discutez|joignez|ajoutez)\b[^.!?\n]{0,30}\b(?:whatsapp|telegram|signal)\b"],
                "rw": [r"\b(?:vugana|andikira|twandikire|hamagara|ongeraho)\b[^.!?\n]{0,30}\b(?:whatsapp|telegram)\b"],
                "sw": [r"\b(?:wasiliana|andika|ongea|ongeza)\b[^.!?\n]{0,30}\b(?:whatsapp|telegram)\b"],
            },
        ],
    },
    {
        "id": "gift_card_request",
        "severity": "medium",
        "suppress_if_protective": True,
        "title": {
            "en": "Asks you to buy gift cards or vouchers for someone",
            "fr": "Vous demande d'acheter des cartes cadeaux ou des bons pour quelqu'un",
            "rw": "Igusaba kugura amakarita y'impano cyangwa ama-vocha",
            "sw": "Inakuomba ununue kadi za zawadi au vocha kwa ajili ya mtu",
        },
        "why": {
            "en": "Scammers pose as a boss or official and ask for gift-card codes because they are hard to trace or reverse.",
            "fr": "Les escrocs se font passer pour un chef ou un officiel et demandent des codes de cartes cadeaux, difficiles à tracer ou à annuler.",
            "rw": "Abatekamutwe biyita abayobozi bagusaba kode z'amakarita y'impano kuko bigoye kuzikurikirana cyangwa kuzisubiza.",
            "sw": "Matapeli hujifanya kuwa mkuu wa kazi au afisa na kuomba misimbo ya kadi za zawadi kwa sababu ni vigumu kufuatilia au kurudisha.",
        },
        "advice": {
            "en": "Do not buy or send codes. Confirm the request face to face or by calling the person on a number you already know.",
            "fr": "N'achetez ni n'envoyez de codes. Confirmez la demande en personne ou en appelant la personne sur un numéro que vous connaissez déjà.",
            "rw": "Ntugure cyangwa ngo wohereze kode. Emeza icyo gusaba imbonankubone cyangwa uhamagare uwo muntu kuri nimero usanzwe uzi.",
            "sw": "Usinunue wala kutuma misimbo. Thibitisha ombi ana kwa ana au kwa kumpigia mtu huyo kwa namba unayoijua tayari.",
        },
        "patterns": {
            "en": [r"\b(?:buy|purchase|get)\b[^.!?\n]{0,30}\b(?:gift ?cards?|google play|itunes|steam|amazon vouchers?)\b"],
            "fr": [r"\b(?:achetez|acheter|achete)\b[^.!?\n]{0,30}\b(?:cartes? cadeaux?|google play|itunes|steam)\b"],
            "rw": [r"\b(?:gura|ugure|kugura)\b[^.!?\n]{0,30}\b(?:google play|itunes|steam|amakarita y'impano)\b"],
            "sw": [r"\b(?:nunua|ununue|kununua)\b[^.!?\n]{0,30}\b(?:vocha|google play|itunes|steam|kadi za zawadi)\b"],
        },
    },
    {
        "id": "pressure",
        "severity": "low",
        "suppress_if_protective": False,
        "title": {"en": "Uses time pressure", "fr": "Met la pression sur le temps",
                  "rw": "Ikoresha igitutu cy'igihe", "sw": "Inatumia shinikizo la muda"},
        "why": {
            "en": "Urgency alone is common in normal messages. It matters only when combined with other warning signs.",
            "fr": "L'urgence seule est courante dans les messages normaux. Elle ne compte que combinée à d'autres signes.",
            "rw": "Kwihutisha ubwabyo bikunze kuba mu butumwa busanzwe. Bifite uburemere gusa iyo byiyongereye ku bindi bimenyetso.",
            "sw": "Haraka peke yake ni jambo la kawaida kwenye jumbe za kawaida. Ni muhimu pale tu inapoambatana na dalili nyingine.",
        },
        "advice": {"en": "Take a minute to check before acting.", "fr": "Prenez une minute pour vérifier avant d'agir.",
                   "rw": "Fata umunota wo kugenzura mbere yo gukora.", "sw": "Chukua dakika moja kuhakiki kabla ya kutenda."},
        "patterns": {
            "en": [r"\b(?:immediately|right now|within (?:\d+|one|two) ?(?:hours?|minutes?)|urgent(?:ly)?|last warning|act now|today only)\b"],
            "fr": [r"\b(?:immediatement|tout de suite|maintenant|dans les (?:\d+|deux) ?(?:heures?|minutes?)|sous (?:\d+) ?(?:heures?|minutes?)|urgent|dernier avertissement|aujourd'hui seulement|agissez vite)\b"],
            "rw": [r"\b(?:byihuse|ako kanya|ubu nonaha|mu masaha \d+|mu minota \d+|uyu munsi gusa)\b"],
            "sw": [r"\b(?:haraka|mara moja|sasa hivi|ndani ya saa \d+|ndani ya dakika \d+|leo tu|onyo la mwisho)\b"],
        },
    },
    {
        "id": "secrecy",
        "severity": "low",
        "suppress_if_protective": False,
        "title": {"en": "Asks you to keep it secret", "fr": "Demande de garder le secret",
                  "rw": "Irasaba kubigira ibanga", "sw": "Inakuomba uweke siri"},
        "why": {
            "en": "Scammers often ask for secrecy so family or friends cannot warn you.",
            "fr": "Les escrocs demandent souvent le secret pour que vos proches ne puissent pas vous alerter.",
            "rw": "Abatekamutwe bakunze gusaba ibanga kugira ngo umuryango cyangwa inshuti zitakuburira.",
            "sw": "Matapeli mara nyingi huomba siri ili familia au marafiki wasikuonye.",
        },
        "advice": {"en": "Talk to someone you trust before acting.", "fr": "Parlez à quelqu'un de confiance avant d'agir.",
                   "rw": "Vugana n'umuntu wizeye mbere yo gukora.", "sw": "Zungumza na mtu unayemwamini kabla ya kutenda."},
        "patterns": {
            "en": [r"\b(?:do not tell|don't tell|keep (?:this|it) (?:a )?secret|tell no one)\b"],
            "fr": [r"\b(?:ne le dites a personne|ne dites rien a personne|gardez (?:ceci|cela|le) secret|n'en parlez a personne)\b"],
            "rw": [r"\b(?:ntugire uwo ubwira|bigire ibanga)\b"],
            "sw": [r"\b(?:usimwambie mtu|usimwambie yeyote|weka siri|iweke siri)\b"],
        },
    },
    {
        "id": "link_present",
        "severity": "low",
        "suppress_if_protective": False,
        "title": {"en": "Contains a link", "fr": "Contient un lien", "rw": "Ifite ihuza", "sw": "Ina kiungo"},
        "why": {
            "en": "Most messages with links are harmless; links matter when other warning signs are present.",
            "fr": "La plupart des messages avec liens sont inoffensifs; les liens comptent s'il y a d'autres signes.",
            "rw": "Ubutumwa bwinshi bufite amahuza ntibubi; amahuza agira uburemere iyo hari ibindi bimenyetso.",
            "sw": "Jumbe nyingi zenye viungo hazina madhara; viungo ni muhimu pale kuna dalili nyingine.",
        },
        "advice": {"en": "Prefer typing official addresses yourself.", "fr": "Préférez taper vous-même les adresses officielles.",
                   "rw": "Ahubwo wandike ubwawe aderesi zemewe.", "sw": "Afadhali andika mwenyewe anwani rasmi."},
        "patterns": {"any": [r"https?://\S+"]},
    },
]

GENERAL_ADVICE = {
    "en": [
        "Do not click links or call numbers from a message you did not expect.",
        "Never share a PIN, password or one-time code with anyone.",
        "Contact the organisation using details from its official website, card or branch.",
        "Talk to someone you trust before sending money.",
    ],
    "fr": [
        "Ne cliquez pas sur les liens et n'appelez pas les numéros d'un message inattendu.",
        "Ne partagez jamais un code PIN, un mot de passe ou un code à usage unique.",
        "Contactez l'organisme avec les coordonnées de son site officiel, de votre carte ou de son agence.",
        "Parlez à quelqu'un de confiance avant d'envoyer de l'argent.",
    ],
    "rw": [
        "Ntukande amahuza cyangwa ngo uhamagare nimero ziri mu butumwa utari witeze.",
        "Ntugatange PIN, ijambo ry'ibanga cyangwa kode y'inyongera ku muntu uwo ari we wese.",
        "Vugana n'ikigo ukoresheje amakuru ari ku rubuga rwemewe, ku ikarita cyangwa ku biro.",
        "Vugana n'umuntu wizeye mbere yo kohereza amafaranga.",
    ],
    "sw": [
        "Usibonyeze viungo wala kupiga namba zilizo kwenye ujumbe usioutarajia.",
        "Kamwe usishiriki PIN, nenosiri au msimbo wa mara moja na mtu yeyote.",
        "Wasiliana na taasisi kwa kutumia taarifa za tovuti yake rasmi, kadi yako au tawi.",
        "Zungumza na mtu unayemwamini kabla ya kutuma pesa.",
    ],
}

# Words used only to guess the message language for display. Matching is on folded text.
LANG_MARKERS = {
    "en": ["the", "your", "you", "please", "account", "dear", "customer", "money", "pay", "send", "will", "with"],
    "fr": ["bonjour", "votre", "vous", "compte", "merci", "avez", "sera", "nous", "pour", "cher", "client", "argent", "mot de passe", "est", "les"],
    "rw": ["konti", "yawe", "amafaranga", "ohereza", "mpa", "kode", "mwiriwe", "murakoze", "frw", "kugira ngo", "watsindiye", "izafungwa", "umubare", "ibanga", "nsubiza"],
    "sw": ["habari", "yako", "wako", "akaunti", "asante", "tafadhali", "pesa", "tuma", "umeshinda", "nambari", "kwa", "ili", "mteja", "tsh", "na"],
}

VERDICTS = {
    "ok": {"en": "No known warning signs detected", "fr": "Aucun signe d'alerte connu détecté",
           "rw": "Nta bimenyetso by'uburiganya bizwi byabonetse", "sw": "Hakuna dalili za tahadhari zinazojulikana zilizogunduliwa"},
    "verify": {"en": "Verify before acting", "fr": "Vérifiez avant d'agir",
               "rw": "Banza ugenzure mbere yo gukora", "sw": "Hakiki kabla ya kutenda"},
    "high": {"en": "Multiple high-risk indicators detected", "fr": "Plusieurs indicateurs de risque élevé détectés",
             "rw": "Hari ibimenyetso byinshi by'ibyago bikomeye", "sw": "Viashiria vingi vya hatari kubwa vimegunduliwa"},
}
NO_GUARANTEE = {
    "en": "This is a decision aid, not a guarantee. A message with no warning signs can still be a scam.",
    "fr": "Ceci est une aide à la décision, pas une garantie. Un message sans signe d'alerte peut quand même être une arnaque.",
    "rw": "Iki ni igikoresho cyunganira ibyemezo, ntabwo ari ingwate. Ubutumwa butagaragaza ibimenyetso na bwo bushobora kuba uburiganya.",
    "sw": "Hiki ni kisaidizi cha uamuzi, si dhamana. Ujumbe usio na dalili bado unaweza kuwa utapeli.",
}
