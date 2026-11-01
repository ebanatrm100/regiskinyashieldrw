"""Plain-language explanations for Cyber News items, in English, French, Kinyarwanda and Kiswahili. Pure Python, works offline.
Each item is sorted into a kind of event (ransomware, phishing, data breach, vulnerability ...) by its headline and summary, then explained with three parts:
what it means, why it matters, and what to do. These are general explanations of the KIND of event; they do not claim facts about the specific story beyond its headline.
fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import re
from textutil import fold

LANGS = ("en", "fr", "rw", "sw")

# kind -> regex on folded title+summary (first match in this order wins)
RULES = (
    ("deadline", r"\bdeadline to fix\b|\bdate limite\b|\bitariki ntarengwa\b"),
    ("arrest", r"arrest\w*|charged|sentenced|extradit\w*|indict\w*|convicted|takedown|taken down|seiz\w*|dismantl\w*|arrete\w*|condamn\w*|interpelle\w*|abafashwe|kukamatwa|wamekamatwa|amekamatwa"),
    ("ransomware", r"ransomware|rancongiciel|ransom\b|extortion|extorsion"),
    ("data_breach", r"data breach|breach\w*|data leak\w*|leaked|exposed (?:data|records)|stolen data|fuite\w* de donnees|uvujaji|ibura ry'amakuru"),
    ("vulnerability", r"cve-\d|vulnerabilit\w*|zero-?day|patch\w*|exploit\w*|security update|faille\w*|udhaifu|intege nke|known exploited"),
    ("phishing", r"phishing|smishing|vishing|spoof\w*|fake (?:website|site|login|email|sms)|hameconnage|quishing|business email compromise|\bbec\b"),
    ("scam", r"scam\w*|fraud\w*|swindl\w*|mobile money|sim swap|romance|investment (?:scam|fraud)|fake job|arnaque\w*|escroquerie\w*|ulaghai|uburiganya|utapeli|ubutekamutwe"),
    ("malware", r"malware|trojan|spyware|botnet|infostealer|stealer|keylogger|virus|worm|backdoor|logiciel\w* malveillant\w*|programu hasidi"),
    ("ddos", r"ddos|denial[- ]of[- ]service|outage|deni de service"),
    ("ai_threat", r"deepfake|voice clon\w*|ai[- ]generated|generative ai|hypertrucage|clone vocal"),
    ("event", r"awareness month|safer internet day|data privacy day|password day|computer security day|patch tuesday|critical patch update|journee|umunsi|siku ya"),
    ("awareness", r"awareness|tips?|how to|guide|guidance|protect(?:ing)? yourself|stay safe|advice|best practice|training|sensibilisation|conseils?|ubukangurambaga|inama|uhamasishaji|vidokezo"),
)

TXT = {
    "ransomware": (
        ("Ransomware locks a victim's files or systems and the criminals demand money to unlock them, often also threatening to publish stolen data.",
         "Un rançongiciel verrouille les fichiers ou systèmes d'une victime ; les criminels exigent de l'argent pour les débloquer et menacent souvent de publier les données volées.",
         "Ransomware ifunga amadosiye cyangwa sisitemu z'uwayikorewe, abagizi ba nabi bagasaba amafaranga yo kuyafungura, kenshi banakangisha gutangaza amakuru bibye.",
         "Ransomware hufunga faili au mifumo ya mwathirika na wahalifu hudai pesa za kuzifungua, mara nyingi wakitishia kuchapisha data walizoiba."),
        ("It can stop a business or school for days and cost money, records and trust. Paying does not guarantee the files come back.",
         "Cela peut arrêter une entreprise ou une école pendant des jours et coûter argent, données et confiance. Payer ne garantit pas la récupération.",
         "Bishobora guhagarika ikigo cyangwa ishuri iminsi myinshi bigatwara amafaranga, amakuru n'icyizere. Kwishyura ntibyemeza ko amadosiye azagaruka.",
         "Inaweza kusimamisha biashara au shule kwa siku nyingi na kugharimu pesa, kumbukumbu na uaminifu. Kulipa hakuhakikishi faili kurudi."),
        ("Keep offline backups and test restoring them; install updates; do not open unexpected attachments; if hit, disconnect the device and report to your IT team, the police or the national CERT, and do not rush to pay.",
         "Gardez des sauvegardes hors ligne et testez leur restauration ; installez les mises à jour ; n'ouvrez pas de pièces jointes inattendues ; en cas d'attaque, déconnectez l'appareil et signalez à votre équipe IT, à la police ou au CERT national, sans payer précipitamment.",
         "Bika kopi (backup) zitari kuri interineti kandi ugerageze kuzigarura; shyiraho ivugurura; ntukingure ibyometsweho utiteze; niba wibasiwe, ukure igikoresho kuri interineti, umenyeshe abashinzwe IT, polisi cyangwa CERT y'igihugu, kandi ntukihutire kwishyura.",
         "Hifadhi nakala nje ya mtandao na ujaribu kuzirejesha; sakinisha masasisho; usifungue viambatisho usivyotarajia; ukishambuliwa, tenganisha kifaa na uripoti kwa timu ya IT, polisi au CERT ya taifa, na usikimbilie kulipa.")),
    "arrest": (
        ("Police or courts took action against suspected cybercriminals: arrests, charges, convictions, or the shutdown of criminal websites and servers.",
         "La police ou la justice a agi contre des cybercriminels présumés : arrestations, inculpations, condamnations ou fermeture de sites et serveurs criminels.",
         "Polisi cyangwa inkiko zafashe ingamba ku bakekwaho ibyaha byo kuri interineti: gufatwa, kurega, guhamwa n'icyaha cyangwa gufunga imbuga na seriveri z'abagizi ba nabi.",
         "Polisi au mahakama zimechukua hatua dhidi ya washukiwa wa uhalifu wa mtandaoni: kukamatwa, mashtaka, hukumu au kufungwa kwa tovuti na seva za wahalifu."),
        ("It shows that cybercrime is investigated and that victims can report it. A suspect is presumed innocent until a court decides.",
         "Cela montre que la cybercriminalité fait l'objet d'enquêtes et que les victimes peuvent la signaler. Un suspect est présumé innocent jusqu'à la décision d'un tribunal.",
         "Bigaragaza ko ibyaha byo kuri interineti bikurikiranwa kandi ko abahohotewe bashobora kubitangaho amakuru. Ukekwa afatwa nk'umwere kugeza urukiko rwemeje.",
         "Inaonyesha kuwa uhalifu wa mtandaoni huchunguzwa na waathirika wanaweza kuripoti. Mshukiwa huchukuliwa kuwa hana hatia hadi mahakama iamue."),
        ("If you were a victim, keep evidence (screenshots, receipts, numbers) and report to the police and your bank or mobile-money provider; do not trust anyone who offers to 'recover your money' for a fee.",
         "Si vous êtes victime, gardez les preuves (captures, reçus, numéros) et signalez à la police et à votre banque ou opérateur ; méfiez-vous de ceux qui proposent de « récupérer votre argent » contre paiement.",
         "Niba wahohotewe, bika ibimenyetso (amafoto y'ecran, inyemezabwishyu, nimero) maze ubimenyeshe polisi na banki cyangwa sosiyete ya mobile money; wirinde abakwizeza «kugarura amafaranga yawe» bagusaba kwishyura.",
         "Ukiwa mwathirika, hifadhi ushahidi (picha za skrini, risiti, namba) na uripoti polisi na benki au kampuni ya pesa za simu; usiwaamini wanaotoa «kurudisha pesa zako» kwa ada.")),
    "data_breach": (
        ("A data breach means personal or business information (names, phone numbers, passwords, ID or bank details) was exposed or stolen from an organisation.",
         "Une fuite de données signifie que des informations personnelles ou d'entreprise (noms, numéros, mots de passe, pièces d'identité, coordonnées bancaires) ont été exposées ou volées.",
         "Ibura ry'amakuru risobanura ko amakuru bwite cyangwa y'ikigo (amazina, nimero, amagambo y'ibanga, indangamuntu, amakuru ya banki) yagaragaye cyangwa yibwe.",
         "Uvujaji wa data humaanisha taarifa binafsi au za biashara (majina, namba, nywila, kitambulisho, taarifa za benki) zimefichuka au kuibwa."),
        ("Criminals use leaked data for phishing, identity theft and account takeover, sometimes months later.",
         "Les criminels utilisent les données volées pour l'hameçonnage, l'usurpation d'identité et le piratage de comptes, parfois des mois plus tard.",
         "Abagizi ba nabi bakoresha amakuru yibwe mu buriganya bwa phishing, kwiba indangamuntu no gufata konti, rimwe na rimwe nyuma y'amezi.",
         "Wahalifu hutumia data iliyovuja kwa ulaghai wa phishing, wizi wa utambulisho na kuteka akaunti, wakati mwingine miezi baadaye."),
        ("Change the password of any affected service and everywhere you reused it, turn on two-step verification, watch your accounts, and be careful with messages that mention your leaked details.",
         "Changez le mot de passe du service concerné et partout où vous l'avez réutilisé, activez la vérification en deux étapes, surveillez vos comptes et méfiez-vous des messages qui citent vos données.",
         "Hindura ijambo ry'ibanga rya serivisi yagizweho ingaruka n'ahandi wararikoresheje, fungura kwemeza mu byiciro bibiri, kurikirana konti zawe kandi witondere ubutumwa buvuga amakuru yawe yavuye.",
         "Badilisha nywila ya huduma iliyoathirika na kila mahali ulipoitumia tena, washa uthibitisho wa hatua mbili, fuatilia akaunti zako na uwe makini na ujumbe unaotaja taarifa zako zilizovuja.")),
    "vulnerability": (
        ("A vulnerability is a weakness in software or devices that attackers can use. A 'zero-day' is one attackers use before a fix exists; a CVE number is its public ID.",
         "Une vulnérabilité est une faille d'un logiciel ou appareil que des attaquants peuvent exploiter. Un « zero-day » est exploité avant qu'un correctif n'existe ; le numéro CVE est son identifiant public.",
         "Intege nke (vulnerability) ni icyuho muri porogaramu cyangwa igikoresho abagizi ba nabi bashobora gukoresha. «Zero-day» ni icyo bakoresha mbere y'uko gikosorwa; nimero ya CVE ni indangamuntu yacyo rusange.",
         "Udhaifu (vulnerability) ni pengo kwenye programu au kifaa wavamizi wanaweza kutumia. «Zero-day» ni ule unaotumiwa kabla ya marekebisho kuwepo; namba ya CVE ni kitambulisho chake cha umma."),
        ("Unpatched devices are attacked quickly, often within days, including phones, routers and servers.",
         "Les appareils non corrigés sont attaqués rapidement, souvent en quelques jours : téléphones, routeurs, serveurs.",
         "Ibikoresho bitavuguruwe byibasirwa vuba, kenshi mu minsi mike: telefoni, routeur na seriveri.",
         "Vifaa visivyosasishwa hushambuliwa haraka, mara nyingi ndani ya siku chache: simu, vipanga njia na seva."),
        ("Install the update from the official source as soon as it is available, turn on automatic updates, and replace devices that no longer receive updates.",
         "Installez la mise à jour depuis la source officielle dès qu'elle est disponible, activez les mises à jour automatiques et remplacez les appareils qui n'en reçoivent plus.",
         "Shyiraho ivugurura rivuye ku isoko ryemewe rikimara kuboneka, fungura ivugurura rya buri gihe kandi usimbuze ibikoresho bitagihabwa ivugurura.",
         "Sakinisha sasisho kutoka chanzo rasmi mara tu linapopatikana, washa masasisho ya kiotomatiki na ubadilishe vifaa visivyopata masasisho tena.")),
    "phishing": (
        ("Phishing is a fake message, call or website that pretends to be a bank, operator, employer or official to steal your passwords, PINs, codes or money.",
         "L'hameçonnage est un faux message, appel ou site qui se fait passer pour une banque, un opérateur, un employeur ou une autorité afin de voler vos mots de passe, PIN, codes ou argent.",
         "Phishing ni ubutumwa, guhamagara cyangwa urubuga rw'impimbano rwiyita banki, sosiyete y'itumanaho, umukoresha cyangwa urwego rwa leta ngo bwibe amagambo y'ibanga, PIN, kode cyangwa amafaranga yawe.",
         "Phishing ni ujumbe, simu au tovuti bandia inayojifanya benki, kampuni ya simu, mwajiri au ofisi ya serikali kuiba nywila, PIN, misimbo au pesa zako."),
        ("It is the most common way accounts and mobile money are emptied, and messages look more convincing every year.",
         "C'est la façon la plus courante de vider comptes et mobile money, et les messages sont de plus en plus convaincants.",
         "Ni inzira ikunze cyane yo gusiba konti na mobile money, kandi ubutumwa burushaho kumera nk'ukuri buri mwaka.",
         "Ndiyo njia inayotumika zaidi kumaliza akaunti na pesa za simu, na jumbe zinazidi kuaminika kila mwaka."),
        ("Do not click links or share PIN/OTP. Contact the organisation using the number or app you already trust, and paste the message into the Check tab of KinyaShield.",
         "Ne cliquez pas sur les liens et ne partagez ni PIN ni OTP. Contactez l'organisation via le numéro ou l'application que vous connaissez, et collez le message dans l'onglet Vérifier de KinyaShield.",
         "Ntukande ku murongo kandi ntuhe PIN cyangwa OTP. Hamagara ikigo kuri nimero cyangwa porogaramu usanzwe wizera, ushyire ubutumwa mu gice cya «Genzura» cya KinyaShield.",
         "Usibofye viungo wala kushiriki PIN/OTP. Wasiliana na shirika kwa namba au programu unayoiamini, na ubandike ujumbe kwenye kichupo cha Kagua cha KinyaShield.")),
    "scam": (
        ("A scam tricks people into sending money or giving details, for example fake mobile-money messages, fake jobs, romance or investment promises.",
         "Une arnaque pousse les gens à envoyer de l'argent ou à donner des informations : faux messages mobile money, faux emplois, promesses amoureuses ou d'investissement.",
         "Uburiganya butera abantu kohereza amafaranga cyangwa gutanga amakuru, urugero ubutumwa bw'impimbano bwa mobile money, akazi k'impimbano, urukundo cyangwa ubwizerwe bw'ishoramari.",
         "Ulaghai hudanganya watu kutuma pesa au kutoa taarifa, kwa mfano jumbe bandia za pesa za simu, kazi bandia, mapenzi au ahadi za uwekezaji."),
        ("Victims often lose savings and cannot recover them; scammers target people who are in a hurry or hopeful.",
         "Les victimes perdent souvent leurs économies sans pouvoir les récupérer ; les escrocs visent les personnes pressées ou pleines d'espoir.",
         "Abahohotewe akenshi batakaza ubwizigame ntibabugarure; abatekamutwe bibasira abihuta cyangwa bafite icyizere.",
         "Waathirika mara nyingi hupoteza akiba bila kurudishiwa; matapeli huwalenga wenye haraka au matumaini."),
        ("Never pay to receive money, a prize or a job. Verify through an official channel, take time before paying, and report to your provider and the police.",
         "Ne payez jamais pour recevoir de l'argent, un prix ou un emploi. Vérifiez par un canal officiel, prenez le temps avant de payer et signalez à votre opérateur et à la police.",
         "Ntukishyure ngo wakire amafaranga, igihembo cyangwa akazi. Genzura unyuze ku nzira yemewe, fata umwanya mbere yo kwishyura kandi umenyeshe sosiyete na polisi.",
         "Usilipe kupokea pesa, zawadi au kazi. Hakiki kupitia njia rasmi, chukua muda kabla ya kulipa na uripoti kwa kampuni yako na polisi.")),
    "malware": (
        ("Malware is harmful software (viruses, trojans, spyware, bots, info-stealers) that spies on you, steals data or takes control of a device.",
         "Un logiciel malveillant (virus, cheval de Troie, logiciel espion, botnet, voleur d'informations) espionne, vole des données ou prend le contrôle d'un appareil.",
         "Malware ni porogaramu yangiza (virusi, trojan, spyware, bot, abiba amakuru) ikunyuza, yiba amakuru cyangwa ifata igikoresho.",
         "Malware ni programu hasidi (virusi, trojan, spyware, bot, wanaoiba taarifa) inayokupeleleza, kuiba data au kuchukua udhibiti wa kifaa."),
        ("It often arrives through fake apps, cracked software or attachments, and can hide for a long time.",
         "Il arrive souvent via de fausses applications, des logiciels piratés ou des pièces jointes, et peut se cacher longtemps.",
         "Akenshi igera ku bikoresho binyuze muri porogaramu z'impimbano, porogaramu zangijwe cyangwa ibyometsweho, kandi ishobora kwihisha igihe kirekire.",
         "Mara nyingi huja kupitia programu bandia, programu zilizovunjwa au viambatisho, na inaweza kujificha kwa muda mrefu."),
        ("Install apps only from official stores, keep the system updated, use a trusted security app, and if the device behaves strangely, change passwords from a clean device.",
         "N'installez des applications que depuis les boutiques officielles, tenez le système à jour, utilisez un antivirus fiable et, si l'appareil se comporte étrangement, changez vos mots de passe depuis un appareil sain.",
         "Shyiraho porogaramu zivuye mu maduka yemewe gusa, vugurura sisitemu, koresha porogaramu yizewe y'umutekano, kandi niba igikoresho gitangiye gukora nabi, hindura amagambo y'ibanga ukoresheje igikoresho kizima.",
         "Sakinisha programu kutoka maduka rasmi tu, sasisha mfumo, tumia programu ya usalama inayoaminika, na kifaa kikifanya vibaya, badilisha nywila kwa kifaa safi.")),
    "ddos": (
        ("A DDoS attack floods a website or service with traffic so that real users cannot reach it; an outage is when a service stops working.",
         "Une attaque DDoS inonde un site ou service de trafic pour que les vrais utilisateurs ne puissent plus y accéder ; une panne est un arrêt de service.",
         "Igitero cya DDoS cyuzuza urubuga cyangwa serivisi n'ibisabwa byinshi kugira ngo abakoresha nyabo batabasha kuyigeraho; guhagarara ni igihe serivisi itagikora.",
         "Shambulio la DDoS hufurika tovuti au huduma kwa trafiki ili watumiaji halisi washindwe kuifikia; hitilafu ni huduma kuacha kufanya kazi."),
        ("It can cut access to banking, government or school services for hours.",
         "Elle peut couper l'accès aux services bancaires, publics ou scolaires pendant des heures.",
         "Gishobora guhagarika serivisi za banki, leta cyangwa amashuri mu masaha menshi.",
         "Inaweza kukata upatikanaji wa huduma za benki, serikali au shule kwa saa nyingi."),
        ("Use the official app or branch if a site is down, and be careful: criminals sometimes send fake 'service restored, log in here' messages during outages.",
         "Utilisez l'application officielle ou l'agence si un site est en panne et soyez prudent : des criminels envoient parfois de faux messages « service rétabli, connectez-vous ici ».",
         "Koresha porogaramu cyangwa ishami ryemewe iyo urubuga rudakora kandi witonde: abagizi ba nabi rimwe na rimwe bohereza ubutumwa bw'impimbano «serivisi yagarutse, injira hano».",
         "Tumia programu au tawi rasmi tovuti ikiwa chini na uwe makini: wahalifu wakati mwingine hutuma jumbe bandia «huduma imerudi, ingia hapa».")),
    "ai_threat": (
        ("AI can be used to copy a voice, create fake videos (deepfakes) or write convincing scam messages.",
         "L'IA peut servir à copier une voix, créer de fausses vidéos (deepfakes) ou rédiger des messages d'arnaque convaincants.",
         "AI ishobora gukoreshwa mu gukopera ijwi, gukora amashusho y'impimbano (deepfakes) cyangwa kwandika ubutumwa bw'uburiganya busa n'ukuri.",
         "AI inaweza kutumika kunakili sauti, kutengeneza video bandia (deepfakes) au kuandika jumbe za ulaghai zinazoshawishi."),
        ("A familiar voice or face is no longer proof of who is calling.",
         "Une voix ou un visage familier ne prouve plus l'identité de l'appelant.",
         "Ijwi cyangwa isura bimenyerewe ntibikiri gihamya y'uwo uvugana na we.",
         "Sauti au uso unaojulikana si ushahidi tena wa anayepiga."),
        ("If someone asks for money urgently, hang up and call back on a number you know; agree a family code word; do not send money on voice or video alone.",
         "Si quelqu'un demande de l'argent d'urgence, raccrochez et rappelez sur un numéro connu ; convenez d'un mot de code familial ; n'envoyez pas d'argent sur la seule base d'une voix ou vidéo.",
         "Niba umuntu agusabye amafaranga byihutirwa, hagarika uhamagare kuri nimero uzi; mwemeranye ijambo ry'ibanga mu muryango; ntukohereze amafaranga ushingiye ku ijwi cyangwa video gusa.",
         "Mtu akiomba pesa haraka, kata simu upige tena kwa namba unayoijua; kubaliana neno la siri la familia; usitume pesa kwa sauti au video pekee.")),
    "deadline": (
        ("CISA (the US cyber agency) gives organisations a deadline to fix a vulnerability that criminals are already using in real attacks.",
         "La CISA (agence cyber américaine) fixe aux organisations une échéance pour corriger une vulnérabilité déjà utilisée dans de vraies attaques.",
         "CISA (urwego rwa Amerika rushinzwe umutekano wa interineti) rutanga igihe ntarengwa ku bigo cyo gukosora intege nke abagizi ba nabi bamaze gukoresha mu bitero nyabyo.",
         "CISA (shirika la usalama wa mtandao la Marekani) hutoa tarehe ya mwisho kwa mashirika kurekebisha udhaifu ambao wahalifu tayari wanautumia katika mashambulizi halisi."),
        ("If you use the named product, it is a signal to update now, not later.",
         "Si vous utilisez le produit cité, c'est un signal pour mettre à jour maintenant.",
         "Niba ukoresha igicuruzwa cyavuzwe, ni ikimenyetso cyo kuvugurura nonaha.",
         "Ukitumia bidhaa iliyotajwa, ni ishara ya kusasisha sasa, si baadaye."),
        ("Check the vendor's official security page, install the fix, and if no fix exists follow the vendor's advice to reduce the risk.",
         "Consultez la page de sécurité officielle de l'éditeur, installez le correctif et, s'il n'existe pas, suivez les consignes du fournisseur pour réduire le risque.",
         "Reba urupapuro rw'umutekano rwemewe rw'uwakoze igicuruzwa, ushyireho ikosora, kandi niba ritari ryaboneka kurikiza inama z'uwo mutanga serivisi mu kugabanya ibyago.",
         "Angalia ukurasa rasmi wa usalama wa muuzaji, sakinisha marekebisho, na kama hayapo fuata ushauri wa muuzaji kupunguza hatari.")),
    "event": (
        ("This is a regular date in the security calendar: a scheduled software-update day or an awareness day or month.",
         "C'est une date régulière du calendrier de sécurité : jour de mises à jour logicielles planifiées ou journée/mois de sensibilisation.",
         "Iyi ni itariki isanzwe mu ngengabihe y'umutekano: umunsi w'ivugurura rya porogaramu cyangwa umunsi/ukwezi k'ubukangurambaga.",
         "Hii ni tarehe ya kawaida kwenye kalenda ya usalama: siku ya masasisho ya programu iliyopangwa au siku/mwezi wa uhamasishaji."),
        ("It is a good moment to update devices, review passwords and talk with family, colleagues or students about safe habits.",
         "C'est un bon moment pour mettre à jour vos appareils, revoir vos mots de passe et parler de bonnes habitudes à votre famille, collègues ou élèves.",
         "Ni igihe cyiza cyo kuvugurura ibikoresho, gusuzuma amagambo y'ibanga no kuganira n'umuryango, bagenzi cyangwa abanyeshuri ku myitwarire myiza.",
         "Ni wakati mzuri wa kusasisha vifaa, kukagua nywila na kuzungumza na familia, wafanyakazi au wanafunzi kuhusu tabia salama."),
        ("Plan the update, install it from official sources, and use the day to teach one safe habit.",
         "Planifiez la mise à jour, installez-la depuis les sources officielles et profitez-en pour enseigner une bonne habitude.",
         "Tegura ivugurura, urishyireho ruvuye ku masoko yemewe kandi ukoreshe uwo munsi wigisha umuco umwe mwiza.",
         "Panga masasisho, yasakinishe kutoka vyanzo rasmi na utumie siku hiyo kufundisha tabia moja salama.")),
    "awareness": (
        ("This is advice or an awareness campaign that helps people recognise and avoid online threats.",
         "Il s'agit de conseils ou d'une campagne de sensibilisation pour aider à reconnaître et éviter les menaces en ligne.",
         "Ni inama cyangwa ubukangurambaga bufasha abantu kumenya no kwirinda ibyago byo kuri interineti.",
         "Huu ni ushauri au kampeni ya uhamasishaji inayosaidia watu kutambua na kuepuka vitisho vya mtandaoni."),
        ("Most attacks succeed because of human habits (rushing, reusing passwords, trusting a message), so awareness is the cheapest protection.",
         "La plupart des attaques réussissent à cause d'habitudes humaines (précipitation, mots de passe réutilisés, confiance dans un message) ; la sensibilisation est donc la protection la moins chère.",
         "Ibitero byinshi bigerwaho kubera imyitwarire y'abantu (kwihuta, gukoresha ijambo ry'ibanga rimwe, kwizera ubutumwa), bityo ubukangurambaga ni bwo burinzi buhendutse.",
         "Mashambulizi mengi hufaulu kwa tabia za binadamu (haraka, kutumia nywila ileile, kuamini ujumbe), kwa hiyo uhamasishaji ndio ulinzi wa bei nafuu."),
        ("Pick one tip and apply it today: two-step verification, a unique password manager entry, checking a sender before you click.",
         "Choisissez un conseil et appliquez-le aujourd'hui : vérification en deux étapes, mot de passe unique, vérification de l'expéditeur avant de cliquer.",
         "Hitamo inama imwe uyikoreshe uyu munsi: kwemeza mu byiciro bibiri, ijambo ry'ibanga ryihariye, kugenzura uwohereje mbere yo gukanda.",
         "Chagua kidokezo kimoja ukitumie leo: uthibitisho wa hatua mbili, nywila ya kipekee, kuhakiki mtumaji kabla ya kubofya.")),
    "generic": (
        ("This is a cybersecurity news item from a trusted publisher; open it for the full facts.",
         "Il s'agit d'une actualité de cybersécurité d'un éditeur fiable ; ouvrez-la pour les détails complets.",
         "Iyi ni inkuru y'umutekano wa interineti ituruka ku mutangaza wizewe; yifungure ubone ibisobanuro byuzuye.",
         "Hii ni habari ya usalama wa mtandao kutoka kwa mchapishaji anayeaminika; ifungue upate maelezo kamili."),
        ("Keeping up with real incidents helps you spot the same tricks when they reach you.",
         "Suivre les incidents réels vous aide à reconnaître les mêmes ruses quand elles vous atteignent.",
         "Gukurikira ibyabaye nyabyo bigufasha kumenya uburiganya bumwe iyo bukugezeho.",
         "Kufuatilia matukio halisi hukusaidia kutambua hila zilezile zinapokufikia."),
        ("Check whether it concerns a product, bank or service you use; if so follow the publisher's advice and update your passwords and software.",
         "Vérifiez si cela concerne un produit, une banque ou un service que vous utilisez ; si oui, suivez les conseils de l'éditeur et mettez à jour mots de passe et logiciels.",
         "Reba niba bigukoraho (igicuruzwa, banki cyangwa serivisi ukoresha); niba ari ko biri, kurikiza inama z'umutangaza kandi uvugurure amagambo y'ibanga na porogaramu.",
         "Angalia kama inahusu bidhaa, benki au huduma unayotumia; ikiwa ndiyo, fuata ushauri wa mchapishaji na usasishe nywila na programu."),
    ),
}
LABEL = {"en": ("What it means", "Why it matters", "What you can do"), "fr": ("Ce que cela signifie", "Pourquoi c'est important", "Que faire"),
         "rw": ("Icyo bisobanura", "Impamvu bifite akamaro", "Icyo wakora"), "sw": ("Maana yake", "Kwa nini ni muhimu", "Unachoweza kufanya")}
KIND_NAME = {
    "ransomware": ("Ransomware", "Rançongiciel", "Ransomware", "Ransomware"), "arrest": ("Arrests and takedowns", "Arrestations et démantèlements", "Gufata no gufunga", "Kukamatwa na kufungwa"),
    "data_breach": ("Data breaches", "Fuites de données", "Ibura ry'amakuru", "Uvujaji wa data"), "vulnerability": ("Vulnerabilities and updates", "Vulnérabilités et mises à jour", "Intege nke n'ivugurura", "Udhaifu na masasisho"),
    "phishing": ("Phishing", "Hameçonnage", "Phishing", "Phishing"), "scam": ("Scams and fraud", "Arnaques et fraudes", "Uburiganya n'ubujura", "Ulaghai na udanganyifu"),
    "malware": ("Malware", "Logiciels malveillants", "Malware", "Programu hasidi"), "ddos": ("DDoS and outages", "DDoS et pannes", "DDoS no guhagarara", "DDoS na hitilafu"),
    "ai_threat": ("AI-powered threats", "Menaces liées à l'IA", "Ibyago bya AI", "Vitisho vya AI"), "deadline": ("Fix deadlines", "Échéances de correction", "Amatariki ntarengwa yo gukosora", "Tarehe za mwisho za marekebisho"),
    "event": ("Calendar dates", "Dates du calendrier", "Amatariki mu ngengabihe", "Tarehe za kalenda"), "awareness": ("Awareness and advice", "Sensibilisation et conseils", "Ubukangurambaga n'inama", "Uhamasishaji na ushauri"),
    "generic": ("Other news", "Autres actualités", "Andi makuru", "Habari nyingine"),
}


def kind_of(item: dict) -> str:
    if item.get("recurring"):
        return "event"
    text = fold(f'{item.get("title", "")} {item.get("summary", "")}')
    for kind, rx in RULES:
        if re.search(rx, text):
            return kind
    return "generic"


def explain(item: dict, lang: str = "en") -> dict:
    """{'kind','kind_name','what','why','do','labels'} in the language (English if unknown)."""
    li = LANGS.index(lang) if lang in LANGS else 0
    k = kind_of(item)
    what, why, do = TXT[k]
    return {"kind": k, "kind_name": KIND_NAME[k][li], "what": what[li], "why": why[li], "do": do[li], "labels": LABEL[LANGS[li]]}


_SUM = {"en": ("In this period the trusted sources gave {n} results. Most common kinds: {kinds}.", "Most useful habit this period: {tip}"),
        "fr": ("Sur cette période, les sources fiables ont donné {n} résultats. Types les plus fréquents : {kinds}.", "Habitude la plus utile sur cette période : {tip}"),
        "rw": ("Muri iki gihe amasoko yizewe yatanze ibisubizo {n}. Ubwoko bwiganje: {kinds}.", "Umuco w'ingenzi muri iki gihe: {tip}"),
        "sw": ("Katika kipindi hiki vyanzo vya kuaminika vilitoa matokeo {n}. Aina zinazojitokeza zaidi: {kinds}.", "Tabia muhimu zaidi kipindi hiki: {tip}")}
_TIP = {"ransomware": 2, "data_breach": 2, "vulnerability": 2, "phishing": 2, "scam": 2, "malware": 2, "arrest": 2, "ai_threat": 2, "ddos": 2, "deadline": 2, "event": 2, "awareness": 2, "generic": 2}
_TIPS = {"en": {"ransomware": "keep offline backups.", "data_breach": "use a different password for every service and turn on two-step verification.", "vulnerability": "install updates quickly.", "phishing": "never click links or share codes; verify through the official channel.",
                "scam": "never pay to receive money, a prize or a job.", "malware": "install apps only from official stores.", "arrest": "keep evidence and report crime to the police.", "ai_threat": "call back on a known number before sending money.",
                "ddos": "use the official app or branch when a site is down.", "deadline": "install pending security updates.", "event": "update your devices.", "awareness": "apply one safety tip today.", "generic": "stay alert and verify before you act."},
         "fr": {"ransomware": "gardez des sauvegardes hors ligne.", "data_breach": "un mot de passe différent par service et vérification en deux étapes.", "vulnerability": "installez vite les mises à jour.", "phishing": "ne cliquez pas sur les liens et ne partagez aucun code ; vérifiez par le canal officiel.",
                "scam": "ne payez jamais pour recevoir de l'argent, un prix ou un emploi.", "malware": "n'installez que depuis les boutiques officielles.", "arrest": "gardez les preuves et signalez à la police.", "ai_threat": "rappelez sur un numéro connu avant d'envoyer de l'argent.",
                "ddos": "utilisez l'application officielle ou l'agence en cas de panne.", "deadline": "installez les mises à jour de sécurité en attente.", "event": "mettez vos appareils à jour.", "awareness": "appliquez un conseil de sécurité aujourd'hui.", "generic": "restez vigilant et vérifiez avant d'agir."},
         "rw": {"ransomware": "bika kopi zitari kuri interineti.", "data_breach": "koresha ijambo ry'ibanga ritandukanye kuri buri serivisi kandi ufungure kwemeza mu byiciro bibiri.", "vulnerability": "shyiraho ivugurura vuba.", "phishing": "ntukande ku nzira cyangwa gutanga kode; genzura unyuze ku nzira yemewe.",
                "scam": "ntukishyure ngo wakire amafaranga, igihembo cyangwa akazi.", "malware": "shyiraho porogaramu ziva mu maduka yemewe gusa.", "arrest": "bika ibimenyetso ubimenyeshe polisi.", "ai_threat": "hamagara kuri nimero uzi mbere yo kohereza amafaranga.",
                "ddos": "koresha porogaramu cyangwa ishami ryemewe iyo urubuga rudakora.", "deadline": "shyiraho ivugurura ry'umutekano ritegereje.", "event": "vugurura ibikoresho byawe.", "awareness": "koresha inama imwe y'umutekano uyu munsi.", "generic": "ba maso kandi ugenzure mbere yo gukora."},
         "sw": {"ransomware": "hifadhi nakala nje ya mtandao.", "data_breach": "tumia nywila tofauti kwa kila huduma na washa uthibitisho wa hatua mbili.", "vulnerability": "sakinisha masasisho haraka.", "phishing": "usibofye viungo wala kushiriki misimbo; hakiki kupitia njia rasmi.",
                "scam": "usilipe kupokea pesa, zawadi au kazi.", "malware": "sakinisha programu kutoka maduka rasmi tu.", "arrest": "hifadhi ushahidi na uripoti polisi.", "ai_threat": "piga tena kwa namba unayoijua kabla ya kutuma pesa.",
                "ddos": "tumia programu au tawi rasmi tovuti ikiwa chini.", "deadline": "sakinisha masasisho ya usalama yanayosubiri.", "event": "sasisha vifaa vyako.", "awareness": "tumia kidokezo kimoja cha usalama leo.", "generic": "kuwa macho na uhakiki kabla ya kutenda."}}


def digest(items: list, lang: str = "en") -> str:
    """A short plain-language summary of a result list (counts by kind, and one habit that matters most). '' when there are no items."""
    if not items:
        return ""
    li = LANGS.index(lang) if lang in LANGS else 0
    counts: dict = {}
    for it in items:
        k = kind_of(it)
        counts[k] = counts.get(k, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    kinds = ", ".join(f"{KIND_NAME[k][li]} ({c})" for k, c in ranked[:4])
    top = next((k for k, _c in ranked if k not in ("event", "generic")), ranked[0][0])
    a, b = _SUM[LANGS[li]]
    return a.format(n=len(items), kinds=kinds) + " " + b.format(tip=_TIPS[LANGS[li]][top])
