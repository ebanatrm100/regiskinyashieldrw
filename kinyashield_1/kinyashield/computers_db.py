"""Types of computers for the AI Assistant (offline). Pure Python, no Streamlit.

Each entry explains briefly what the computer is and how it works, in en/fr/rw/sw, with a real photo where one is known.
Photos are NOT stored in the repo and no photo link is guessed: when someone asks, resolve_image() asks Wikipedia for the lead image of the
matching article, and uses it only if it is hosted on Wikimedia Commons (free licences). If the photo cannot be loaded (no internet, no
Commons image) the answer is shown as text only with a note. The caption links to the Wikipedia article, where the author and licence are listed. fr/rw/sw wording is a draft for fluent review.
Not every machine ever built is listed: this is a curated set of the main types. Unknown questions fall through to the guide / AI."""
from __future__ import annotations
import re, unicodedata
from urllib.parse import quote

LANGS = ("en", "fr", "rw", "sw")
COMMONS_FILE = "https://commons.wikimedia.org/wiki/File:"
COMMONS_PATH = "https://commons.wikimedia.org/wiki/Special:FilePath/"

# key: (aliases, commons file name or None, 'photo'|'diagram'|None, {lang: (name, how it works, examples, typical use)})
_DATA = {
    "computer": (["computer", "computers", "a computer", "ordinateur", "mudasobwa", "kompyuta"], None, None, {
        "en": ("How a computer works", "Every computer follows the same cycle: input, processing, storage and output. Input devices (keyboard, mouse, touchscreen, sensors) send data in. The processor (CPU) follows program instructions step by step, using fast memory (RAM) for work in progress. Storage (SSD or disk) keeps programs and files when the power is off. Output devices (screen, speaker, printer) show the result. The operating system manages all of this and lets programs share the hardware.",
               "Desktop, laptop, tablet, smartphone, server, supercomputer", "Everything from calculators to phones to data centres uses this cycle."),
        "fr": ("Comment fonctionne un ordinateur", "Tout ordinateur suit le même cycle : entrée, traitement, stockage et sortie. Les périphériques d'entrée (clavier, souris, écran tactile, capteurs) envoient les données. Le processeur (CPU) suit pas à pas les instructions des programmes en utilisant la mémoire vive (RAM) pour le travail en cours. Le stockage (SSD ou disque) conserve programmes et fichiers hors tension. Les périphériques de sortie (écran, haut-parleur, imprimante) montrent le résultat. Le système d'exploitation gère le tout et permet aux programmes de partager le matériel.",
               "Ordinateur de bureau, portable, tablette, smartphone, serveur, superordinateur", "Des calculatrices aux téléphones et aux centres de données, tout suit ce cycle."),
        "rw": ("Uko mudasobwa ikora", "Mudasobwa zose zikurikiza uruhererekane rumwe: kwinjiza, gutunganya, kubika no gusohora. Ibyinjiza (clavier, souris, ecran ikorwaho, ibyuma bipima) byohereza amakuru. Processeur (CPU) ikurikiza amabwiriza ya porogaramu intambwe ku yindi ikoresheje RAM yihuta ibika by'agateganyo. Ububiko (SSD cyangwa disque) bubika porogaramu na dosiye n'iyo umuriro wazimye. Ibisohoka (ecran, indangururamajwi, imprimante) bigaragaza igisubizo. Sisitemu y'imikorere iyobora ibyo byose igatuma porogaramu zisangira ibyuma.",
               "Desktop, laptop, tablet, smartphone, seriveri, supercomputer", "Kuva kuri kalkulatrisi kugeza kuri telefoni n'ibigo bya data, byose bikurikiza uru ruhererekane."),
        "sw": ("Jinsi kompyuta inavyofanya kazi", "Kila kompyuta hufuata mzunguko mmoja: ingizo, uchakataji, uhifadhi na towe. Vifaa vya ingizo (kibodi, kipanya, skrini ya kugusa, vihisi) hutuma data. Kichakataji (CPU) hufuata maagizo ya programu hatua kwa hatua kikitumia RAM ya haraka kwa kazi inayoendelea. Hifadhi (SSD au diski) huweka programu na mafaili umeme ukizimwa. Vifaa vya towe (skrini, spika, printa) huonyesha matokeo. Mfumo wa uendeshaji husimamia yote na kuziruhusu programu kushiriki vifaa.",
               "Desktop, laptop, tablet, simu janja, seva, supercomputer", "Kuanzia kikokotoo hadi simu na vituo vya data, vyote hufuata mzunguko huu."),
    }),
    "desktop": (["ordinateur de bureau", "mudasobwa ya desktop", "kompyuta ya mezani", "desktop computer", "desktop", "pc", "personal computer", "tower pc", "desktop pc"],
                "Personal computer, exploded 5.svg", "diagram", {
        "en": ("Desktop computer", "A desktop is a personal computer meant to stay on a desk. A case holds the motherboard, the processor (CPU) that runs instructions, memory (RAM) for work in progress, storage (SSD or hard disk) for files, and a power supply. You give input with a keyboard and mouse and see output on a separate monitor. The CPU loads the operating system and programs from storage into RAM and runs them.",
               "Dell OptiPlex, HP Pro, home-built PCs", "Office work, study, gaming, design; easy to upgrade and repair."),
        "fr": ("Ordinateur de bureau", "Un ordinateur de bureau est un ordinateur personnel destiné à rester sur un bureau. Un boîtier contient la carte mère, le processeur (CPU) qui exécute les instructions, la mémoire vive (RAM) pour le travail en cours, le stockage (SSD ou disque dur) pour les fichiers et l'alimentation. On saisit avec le clavier et la souris et on voit le résultat sur un écran séparé. Le CPU charge le système d'exploitation et les programmes du stockage vers la RAM et les exécute.",
               "Dell OptiPlex, HP Pro, PC assemblés", "Bureautique, études, jeux, conception ; facile à mettre à niveau et à réparer."),
        "rw": ("Mudasobwa ikoreshwa ku meza (desktop)", "Desktop ni mudasobwa y'umuntu ku giti cye ishyirwa ku meza. Mu gasanduku harimo carte mère (motherboard), processeur (CPU) ukora amabwiriza, RAM ibika by'agateganyo ibyo urimo gukora, ububiko (SSD cyangwa hard disk) bubika dosiye, n'ikiyiha amashanyarazi. Winjiza amakuru ukoresheje clavier na souris, ukabona ibisubizo kuri ecran itandukanye. CPU ikura sisitemu n'porogaramu mu bubiko ikazishyira muri RAM ikazikoresha.",
               "Dell OptiPlex, HP Pro, izikoranywe n'abantu", "Akazi ko mu biro, kwiga, imikino, gushushanya; biroroshye kuzivugurura no kuzikora."),
        "sw": ("Kompyuta ya mezani (desktop)", "Desktop ni kompyuta binafsi inayokaa mezani. Kasha lina motherboard, kichakataji (CPU) kinachotekeleza maagizo, RAM kwa kazi inayoendelea, hifadhi (SSD au diski ngumu) kwa mafaili, na chanzo cha umeme. Unaingiza data kwa kibodi na kipanya na kuona matokeo kwenye skrini tofauti. CPU hupakia mfumo wa uendeshaji na programu kutoka hifadhini hadi RAM na kuziendesha.",
               "Dell OptiPlex, HP Pro, kompyuta zilizounganishwa nyumbani", "Kazi za ofisini, masomo, michezo, usanifu; ni rahisi kuboresha na kutengeneza."),
    }),
    "laptop": (["ordinateur portable", "mudasobwa igendanwa", "kompyuta mpakato", "laptop", "laptops", "notebook computer", "notebook pc"],
               "X7200 laptop computer.JPG", "photo", {
        "en": ("Laptop", "A laptop is a portable computer that puts the screen, keyboard, touchpad, battery and the computer parts in one folding body. It works like a desktop (CPU, RAM, storage, operating system) but uses lower-power parts and a rechargeable battery, and it manages heat with small fans and heat pipes.",
               "Lenovo ThinkPad, HP, Dell XPS, MacBook", "Work and study on the move; usually harder to upgrade than a desktop."),
        "fr": ("Ordinateur portable", "Un ordinateur portable réunit l'écran, le clavier, le pavé tactile, la batterie et les composants dans un seul boîtier pliant. Il fonctionne comme un ordinateur de bureau (CPU, RAM, stockage, système d'exploitation) mais avec des composants moins gourmands et une batterie rechargeable, et il évacue la chaleur avec de petits ventilateurs et des caloducs.",
               "Lenovo ThinkPad, HP, Dell XPS, MacBook", "Travail et études en déplacement ; en général plus difficile à mettre à niveau qu'un ordinateur de bureau."),
        "rw": ("Mudasobwa igendanwa (laptop)", "Laptop ni mudasobwa ishobora kugendanwa ifite ecran, clavier, touchpad, batiri n'ibice by'ingenzi byose mu mubiri umwe ukunjwa. Ikora nka desktop (CPU, RAM, ububiko, sisitemu) ariko ikoresha ibice bigabanya amashanyarazi na batiri ishyirwamo umuriro, kandi ikonjesha ikoresheje udukoresho duhuha n'imiyoboro y'ubushyuhe.",
               "Lenovo ThinkPad, HP, Dell XPS, MacBook", "Gukora no kwiga uri mu rugendo; akenshi biragoye kuyivugurura kurusha desktop."),
        "sw": ("Kompyuta mpakato (laptop)", "Laptop ni kompyuta inayobebeka yenye skrini, kibodi, touchpad, betri na vipuri vya msingi katika mwili mmoja unaokunjika. Inafanya kazi kama desktop (CPU, RAM, hifadhi, mfumo wa uendeshaji) lakini hutumia vipuri vinavyotumia umeme kidogo na betri inayochajiwa, na hupoza joto kwa feni ndogo na mirija ya joto.",
               "Lenovo ThinkPad, HP, Dell XPS, MacBook", "Kazi na masomo popote ulipo; mara nyingi ni ngumu kuboresha kuliko desktop."),
    }),
    "tablet": (["tablette", "tablettes", "kompyuta kibao", "tablet", "tablets", "tablet computer", "ipad"],
               "IPad 2 White on table.jpg", "photo", {
        "en": ("Tablet", "A tablet is a flat touchscreen computer with no physical keyboard. Everything (processor, memory, storage, battery, wireless chips, sensors) sits behind the glass screen. You tap and swipe; the touch layer sends the position of your finger to the processor, which runs apps from an operating system such as Android or iPadOS.",
               "iPad, Samsung Galaxy Tab", "Reading, video, drawing, light work, learning apps."),
        "fr": ("Tablette", "Une tablette est un ordinateur plat à écran tactile sans clavier physique. Tout (processeur, mémoire, stockage, batterie, puces sans fil, capteurs) se trouve derrière l'écran en verre. On touche et on fait glisser ; la couche tactile envoie la position du doigt au processeur, qui exécute des applications sous un système comme Android ou iPadOS.",
               "iPad, Samsung Galaxy Tab", "Lecture, vidéo, dessin, travail léger, applications éducatives."),
        "rw": ("Tablet", "Tablet ni mudasobwa iringaniye ifite ecran ukoraho kandi idafite clavier nyayo. Ibice byose (processeur, RAM, ububiko, batiri, ibyo kuvugana nta nsinga, ibyuma bipima) biri inyuma y'ikirahuri cya ecran. Ukoraho ukanyerereza urutoki; igice gikorwaho kimenyesha processeur aho urutoki rwahereye, na yo igakoresha porogaramu zo muri sisitemu nka Android cyangwa iPadOS.",
               "iPad, Samsung Galaxy Tab", "Gusoma, kureba amashusho, gushushanya, akazi koroheje, porogaramu zo kwiga."),
        "sw": ("Kompyuta kibao (tablet)", "Tablet ni kompyuta bapa yenye skrini ya kugusa isiyo na kibodi halisi. Kila kitu (kichakataji, RAM, hifadhi, betri, chipu za wireless, vihisi) kiko nyuma ya skrini ya kioo. Unagusa na kutelezesha; safu ya kugusa hutuma mahali kidole kilipo kwa kichakataji, kinachoendesha programu za mfumo kama Android au iPadOS.",
               "iPad, Samsung Galaxy Tab", "Kusoma, video, kuchora, kazi nyepesi, programu za kujifunza."),
    }),
    "smartphone": (["smartphone", "smartphones", "telephone intelligent", "simu janja", "telefoni igezweho", "smart phone", "mobile phone", "cell phone", "cellphone", "android phone", "iphone", "telephone igezweho"],
                   "Android foldable smartphone.jpg", "photo", {
        "en": ("Smartphone", "A smartphone is a pocket-sized computer that can also make calls. A system-on-a-chip combines the processor, graphics and modem. It talks to the mobile network through a radio and antenna, to the internet by Wi-Fi or mobile data, and uses sensors (camera, GPS, accelerometer) and a touchscreen. Apps run on Android or iOS.",
               "Samsung Galaxy, iPhone, Tecno, Infinix", "Calls, messaging, mobile money, photos, internet, apps."),
        "fr": ("Smartphone", "Un smartphone est un ordinateur de poche qui permet aussi de téléphoner. Un système sur puce réunit le processeur, le graphisme et le modem. Il communique avec le réseau mobile par radio et antenne, avec Internet par Wi-Fi ou données mobiles, et utilise des capteurs (caméra, GPS, accéléromètre) et un écran tactile. Les applications tournent sous Android ou iOS.",
               "Samsung Galaxy, iPhone, Tecno, Infinix", "Appels, messages, mobile money, photos, Internet, applications."),
        "rw": ("Telefoni igezweho (smartphone)", "Smartphone ni mudasobwa ntoya ujyana mu mufuka ishobora no guhamagara. Agace kamwe (system-on-a-chip) kagizwe na processeur, igice cy'amashusho na modem. Ivugana n'umuyoboro wa telefoni ikoresheje radiyo na antene, ikavugana na internet ikoresheje Wi-Fi cyangwa data, kandi ikoresha ibyuma bipima (kamera, GPS, accelerometer) na ecran ikorwaho. Porogaramu ziba kuri Android cyangwa iOS.",
               "Samsung Galaxy, iPhone, Tecno, Infinix", "Guhamagara, kohererezanya ubutumwa, mobile money, amafoto, internet, porogaramu."),
        "sw": ("Simu janja (smartphone)", "Simu janja ni kompyuta ya mfukoni inayoweza pia kupiga simu. Chipu moja (system-on-a-chip) huunganisha kichakataji, michoro na modemu. Huwasiliana na mtandao wa simu kwa redio na antena, na intaneti kwa Wi-Fi au data, na hutumia vihisi (kamera, GPS, accelerometer) na skrini ya kugusa. Programu huendeshwa kwenye Android au iOS.",
               "Samsung Galaxy, iPhone, Tecno, Infinix", "Kupiga simu, ujumbe, pesa mtandao, picha, intaneti, programu."),
    }),
    "smartwatch": (["smartwatch", "smart watch", "montre connectee", "saa janja", "isaha igezweho", "apple watch", "wearable"],
                   "Apple Watch Series 8 Midnight Aluminium Case.jpg", "photo", {
        "en": ("Smartwatch", "A smartwatch is a tiny wrist-worn computer. A low-power chip runs a small operating system, while sensors measure movement and (on many models) heart rate. It usually pairs with a phone over Bluetooth to show notifications, and a small battery typically lasts from about a day to a few days.",
               "Apple Watch, Samsung Galaxy Watch, Garmin", "Notifications, time, step and heart-rate tracking, quick payments."),
        "fr": ("Montre connectée", "Une montre connectée est un minuscule ordinateur porté au poignet. Une puce à faible consommation exécute un petit système d'exploitation, tandis que des capteurs mesurent les mouvements et, sur beaucoup de modèles, la fréquence cardiaque. Elle se couple généralement à un téléphone en Bluetooth pour afficher les notifications, et sa petite batterie dure en général d'environ un jour à quelques jours.",
               "Apple Watch, Samsung Galaxy Watch, Garmin", "Notifications, heure, suivi des pas et du rythme cardiaque, paiements rapides."),
        "rw": ("Isaha igezweho (smartwatch)", "Smartwatch ni mudasobwa nto cyane wambara ku kuboko. Agace gakoresha amashanyarazi make gakoresha sisitemu nto, ibyuma bipima bigapima imigendere kandi ku nyinshi bigapima umutima. Akenshi ihuzwa na telefoni ikoresheje Bluetooth kugira ngo yereke ubutumwa, kandi batiri yayo nto imara hagati y'umunsi umwe n'iminsi mike.",
               "Apple Watch, Samsung Galaxy Watch, Garmin", "Kwerekana ubutumwa, isaha, gukurikirana intambwe n'umutima, kwishyura vuba."),
        "sw": ("Saa janja (smartwatch)", "Saa janja ni kompyuta ndogo sana inayovaliwa mkononi. Chipu inayotumia umeme kidogo huendesha mfumo mdogo, na vihisi hupima mwendo na (kwenye modeli nyingi) mapigo ya moyo. Mara nyingi huunganishwa na simu kwa Bluetooth kuonyesha arifa, na betri yake ndogo kwa kawaida hudumu siku moja hadi chache.",
               "Apple Watch, Samsung Galaxy Watch, Garmin", "Arifa, saa, kufuatilia hatua na mapigo ya moyo, malipo ya haraka."),
    }),
    "chromebook": (["chromebook", "chromebooks", "chrome os"],
                   "Samsung Series 3 Chromebook.JPG", "photo", {
        "en": ("Chromebook", "A Chromebook is a laptop that runs ChromeOS, an operating system built around the Chrome browser. Most apps and files live online, so it needs modest hardware, starts fast and updates itself. It still has a CPU, RAM and (small) storage like any laptop.",
               "Samsung Chromebook, Acer Chromebook", "Schools, web browsing, documents online, low-cost computing."),
        "fr": ("Chromebook", "Un Chromebook est un ordinateur portable sous ChromeOS, un système d'exploitation construit autour du navigateur Chrome. La plupart des applications et des fichiers sont en ligne : le matériel peut donc être modeste, le démarrage rapide et les mises à jour automatiques. Il a quand même un CPU, de la RAM et un (petit) stockage comme tout portable.",
               "Samsung Chromebook, Acer Chromebook", "Écoles, navigation web, documents en ligne, informatique à faible coût."),
        "rw": ("Chromebook", "Chromebook ni laptop ikoresha ChromeOS, sisitemu yubakiye kuri Chrome browser. Porogaramu na dosiye byinshi biba kuri internet, bityo ibice bikenewe biba byoroheje, ifunguka vuba kandi ihindura yo ubwayo. Na yo ifite CPU, RAM n'ububiko (buto) nk'izindi laptop.",
               "Samsung Chromebook, Acer Chromebook", "Amashuri, gusoma kuri internet, inyandiko za interineti, mudasobwa z'igiciro gito."),
        "sw": ("Chromebook", "Chromebook ni laptop inayotumia ChromeOS, mfumo uliojengwa kuzunguka kivinjari cha Chrome. Programu na mafaili mengi yako mtandaoni, hivyo vifaa vinaweza kuwa vya kawaida, huwaka haraka na hujisasisha yenyewe. Bado ina CPU, RAM na hifadhi (ndogo) kama laptop yoyote.",
               "Samsung Chromebook, Acer Chromebook", "Shule, kuvinjari wavuti, hati mtandaoni, kompyuta za gharama nafuu."),
    }),
    "allinone": (["all-in-one", "all in one", "all-in-one computer", "imac"],
                 "Imac 16-9.png", "photo", {
        "en": ("All-in-one computer", "An all-in-one puts the computer parts (CPU, RAM, storage) behind the screen, so the monitor and computer are one unit with a single power cable. It works like a desktop but takes less space and has fewer cables; it is usually harder to upgrade.",
               "Apple iMac, HP All-in-One, Lenovo IdeaCentre AIO", "Home, reception desks, schools, shops."),
        "fr": ("Ordinateur tout-en-un", "Un tout-en-un place les composants (CPU, RAM, stockage) derrière l'écran : écran et ordinateur forment une seule unité avec un seul câble d'alimentation. Il fonctionne comme un ordinateur de bureau mais prend moins de place et a moins de câbles ; il est en général plus difficile à mettre à niveau.",
               "Apple iMac, HP All-in-One, Lenovo IdeaCentre AIO", "Maison, accueils, écoles, boutiques."),
        "rw": ("Mudasobwa yose-mu-rimwe (all-in-one)", "All-in-one ishyira ibice bya mudasobwa (CPU, RAM, ububiko) inyuma ya ecran, bityo ecran na mudasobwa biba ikintu kimwe gifite umugozi umwe w'amashanyarazi. Ikora nka desktop ariko ifata umwanya muto kandi ifite imigozi mike; akenshi biragoye kuyivugurura.",
               "Apple iMac, HP All-in-One, Lenovo IdeaCentre AIO", "Mu rugo, ku meza yakira abantu, mu mashuri, mu maduka."),
        "sw": ("Kompyuta moja-kwa-moja (all-in-one)", "All-in-one huweka vipuri vya kompyuta (CPU, RAM, hifadhi) nyuma ya skrini, hivyo skrini na kompyuta ni kifaa kimoja chenye waya mmoja wa umeme. Hufanya kazi kama desktop lakini huchukua nafasi ndogo na ina nyaya chache; mara nyingi ni ngumu kuboresha.",
               "Apple iMac, HP All-in-One, Lenovo IdeaCentre AIO", "Nyumbani, mapokezi, shule, maduka."),
    }),
    "server": (["server", "servers", "serveur", "serveurs", "seriveri", "seva", "web server", "rack server", "data center", "datacenter", "data centre"],
               "Computer server rack.jpg", "photo", {
        "en": ("Server", "A server is a computer that serves other computers over a network. It has the same parts as other computers, but with more cores, more RAM, redundant power supplies and storage built to run day and night. Servers are mounted in racks in data centres. When your phone opens a website, a server receives the request, finds or builds the page and sends it back.",
               "Web servers, mail servers, database servers, cloud servers", "Websites, email, apps, files, databases, cloud services."),
        "fr": ("Serveur", "Un serveur est un ordinateur qui rend service à d'autres ordinateurs via un réseau. Il a les mêmes composants que les autres, mais avec plus de cœurs, plus de RAM, des alimentations redondantes et un stockage conçu pour fonctionner jour et nuit. Les serveurs sont montés dans des baies dans des centres de données. Quand votre téléphone ouvre un site, un serveur reçoit la requête, trouve ou construit la page et la renvoie.",
               "Serveurs web, serveurs de messagerie, serveurs de bases de données, serveurs cloud", "Sites web, e-mail, applications, fichiers, bases de données, services cloud."),
        "rw": ("Seriveri (server)", "Seriveri ni mudasobwa ikorera izindi mudasobwa ikoresheje umuyoboro. Ifite ibice bimwe n'izindi, ariko ifite cores nyinshi, RAM nyinshi, ibyo kuyiha amashanyarazi byisubiramo n'ububiko bwakorewe gukora amanywa n'ijoro. Seriveri zishyirwa mu bubiko bw'ibyuma (rack) mu bigo bya data centre. Telefoni yawe iyo ifunguye urubuga, seriveri yakira ubusabe, igashaka cyangwa igategura urupapuro ikarugusubiza.",
               "Seriveri z'urubuga, iz'imeri, iz'ububikoshingiro, iza cloud", "Imbuga, imeri, porogaramu, dosiye, ububikoshingiro, serivisi za cloud."),
        "sw": ("Seva (server)", "Seva ni kompyuta inayotumikia kompyuta nyingine kupitia mtandao. Ina vipuri vilevile kama kompyuta nyingine, lakini vina cores nyingi, RAM nyingi, vyanzo vya umeme vya akiba na hifadhi iliyojengwa kufanya kazi mchana na usiku. Seva huwekwa kwenye rafu ndani ya vituo vya data. Simu yako inapofungua tovuti, seva hupokea ombi, hupata au kutengeneza ukurasa na kuurudisha.",
               "Seva za wavuti, barua pepe, hifadhidata, wingu (cloud)", "Tovuti, barua pepe, programu, mafaili, hifadhidata, huduma za wingu."),
    }),
    "mainframe": (["mainframe", "mainframes", "ordinateur central", "mudasobwa nkuru", "mainframe computer", "ibm z", "ibm mainframe"],
                  "IBM Z14 (36084219181).jpg", "photo", {
        "en": ("Mainframe", "A mainframe is a large, very reliable computer built to process huge numbers of transactions at once. It has many processors and input/output channels, can swap failed parts while running, and shares its power among thousands of users and jobs at the same time.",
               "IBM Z series", "Banks, airlines, governments, insurance and payment processing."),
        "fr": ("Ordinateur central (mainframe)", "Un ordinateur central est une grande machine très fiable conçue pour traiter un très grand nombre de transactions à la fois. Il a de nombreux processeurs et canaux d'entrée/sortie, peut remplacer des pièces défaillantes en cours de fonctionnement et partage sa puissance entre des milliers d'utilisateurs et de tâches simultanément.",
               "IBM Z", "Banques, compagnies aériennes, administrations, assurances et paiements."),
        "rw": ("Mainframe (mudasobwa nkuru)", "Mainframe ni mudasobwa nini cyane yizewe yakorewe gukora ibikorwa byinshi icyarimwe (transactions). Ifite processeur nyinshi n'inzira nyinshi z'amakuru, ishobora gusimbuza ibice byapfuye ikomeje gukora, kandi igabanya imbaraga zayo hagati y'abakoresha n'imirimo ibihumbi icyarimwe.",
               "IBM Z", "Amabanki, ibigo by'indege, leta, ubwishingizi n'ibyo kwishyura."),
        "sw": ("Mainframe (kompyuta kuu)", "Mainframe ni kompyuta kubwa na ya kuaminika sana iliyojengwa kuchakata miamala mingi sana kwa wakati mmoja. Ina vichakataji vingi na njia nyingi za kuingiza/kutoa data, inaweza kubadilisha vipuri vilivyoharibika ikiendelea kufanya kazi, na hugawa nguvu yake kati ya maelfu ya watumiaji na kazi kwa wakati mmoja.",
               "IBM Z", "Benki, mashirika ya ndege, serikali, bima na malipo."),
    }),
    "supercomputer": (["supercomputer", "supercomputers", "super computer", "superordinateur", "superordinateurs", "kompyuta kuu", "mudasobwa nkuru cyane"],
                      "Summit (supercomputer).jpg", "photo", {
        "en": ("Supercomputer", "A supercomputer links thousands of processors (often with GPUs) by a very fast network so they all work on one huge problem in parallel. The problem is split into small pieces, each piece is computed on a different node, and the results are combined. Powerful cooling, often liquid, removes the heat. Speed is measured in FLOPS (floating-point operations per second).",
               "Summit, Frontier, Fugaku, Cray-1 (an early example)", "Weather and climate models, medicine research, physics, engineering simulations."),
        "fr": ("Superordinateur", "Un superordinateur relie des milliers de processeurs (souvent avec des GPU) par un réseau très rapide pour qu'ils travaillent ensemble sur un problème immense, en parallèle. Le problème est découpé en petits morceaux, chaque morceau est calculé sur un nœud différent, puis les résultats sont combinés. Un refroidissement puissant, souvent liquide, évacue la chaleur. La vitesse se mesure en FLOPS (opérations à virgule flottante par seconde).",
               "Summit, Frontier, Fugaku, Cray-1 (un exemple ancien)", "Modèles météo et climatiques, recherche médicale, physique, simulations d'ingénierie."),
        "rw": ("Supercomputer", "Supercomputer ihuza processeur ibihumbi (akenshi hamwe na GPU) ikoresheje umuyoboro wihuta cyane kugira ngo zikorere hamwe ikibazo kinini icyarimwe (parallel). Ikibazo kigabanywamo uduce duto, buri gace kigakorwa kuri node itandukanye, ibisubizo bikongera guhuzwa. Gukonjesha bikomeye, akenshi ukoresheje amazi, bikuraho ubushyuhe. Umuvuduko upimwa muri FLOPS.",
               "Summit, Frontier, Fugaku, Cray-1 (urugero rwa kera)", "Ibigereranyo by'ikirere n'imihindagurikire yacyo, ubushakashatsi mu buvuzi, fiziki, ibigereranyo by'ubwubatsi."),
        "sw": ("Kompyuta kuu-sana (supercomputer)", "Supercomputer huunganisha maelfu ya vichakataji (mara nyingi na GPU) kwa mtandao wa kasi sana ili vifanye kazi pamoja kwenye tatizo kubwa kwa wakati mmoja (parallel). Tatizo hugawanywa vipande vidogo, kila kipande hukokotolewa kwenye nodi tofauti, kisha matokeo huunganishwa. Upozaji mkubwa, mara nyingi wa maji, huondoa joto. Kasi hupimwa kwa FLOPS.",
               "Summit, Frontier, Fugaku, Cray-1 (mfano wa zamani)", "Mifano ya hali ya hewa na tabianchi, utafiti wa tiba, fizikia, uigaji wa uhandisi."),
    }),
    "minicomputer": (["minicomputer", "minicomputers", "mini-ordinateur", "minicomputer", "mini computer", "pdp-11", "pdp 11", "pdp11"],
                     "PDP-11-70.JPG", "photo", {
        "en": ("Minicomputer", "A minicomputer was a mid-sized computer from the 1960s to 1980s, smaller and cheaper than a mainframe but bigger than a PC. It had a central processor, core or semiconductor memory and ran several terminals or machines at once. It was later replaced by PCs and servers.",
               "DEC PDP-11, VAX", "Laboratories, factories, universities, small companies (historic)."),
        "fr": ("Mini-ordinateur", "Un mini-ordinateur était une machine de taille moyenne des années 1960 à 1980, plus petite et moins chère qu'un ordinateur central mais plus grande qu'un PC. Il avait un processeur central, une mémoire à tores ou à semi-conducteurs et gérait plusieurs terminaux ou machines à la fois. Il a ensuite été remplacé par les PC et les serveurs.",
               "DEC PDP-11, VAX", "Laboratoires, usines, universités, petites entreprises (historique)."),
        "rw": ("Minicomputer", "Minicomputer yari mudasobwa y'ubunini buringaniye yo mu myaka ya 1960–1980, ntoya kandi ihendutse kuruta mainframe ariko nini kuruta PC. Yari ifite processeur nkuru, ububiko bw'amakuru kandi yakoreshwaga n'abantu benshi cyangwa ibyuma byinshi icyarimwe. Nyuma yasimbujwe PC na seriveri.",
               "DEC PDP-11, VAX", "Laboratwari, inganda, kaminuza, ibigo bito (mu mateka)."),
        "sw": ("Kompyuta ndogo-kati (minicomputer)", "Minicomputer ilikuwa kompyuta ya ukubwa wa kati ya miaka ya 1960–1980, ndogo na nafuu kuliko mainframe lakini kubwa kuliko PC. Ilikuwa na kichakataji kikuu, kumbukumbu ya core au semiconductor na iliendesha vituo au mashine kadhaa kwa wakati mmoja. Baadaye ilibadilishwa na PC na seva.",
               "DEC PDP-11, VAX", "Maabara, viwanda, vyuo vikuu, kampuni ndogo (kihistoria)."),
    }),
    "sbc": (["raspberry pi", "raspberrypi", "single board computer", "single-board computer", "sbc", "rpi"],
            "RaspberryPi.jpg", "photo", {
        "en": ("Single-board computer (Raspberry Pi)", "A single-board computer puts the processor, memory, ports and connectors on one small circuit board about the size of a credit card. You add a memory card for storage, a power supply, a screen and a keyboard. It runs a normal operating system such as Linux, and its GPIO pins let it control lights, sensors and motors.",
               "Raspberry Pi, BeagleBone", "Learning to code, small servers, robots, sensors and prototypes."),
        "fr": ("Ordinateur monocarte (Raspberry Pi)", "Un ordinateur monocarte place le processeur, la mémoire, les ports et les connecteurs sur une petite carte de la taille d'une carte bancaire. On ajoute une carte mémoire pour le stockage, une alimentation, un écran et un clavier. Il exécute un système normal comme Linux, et ses broches GPIO permettent de piloter des lumières, des capteurs et des moteurs.",
               "Raspberry Pi, BeagleBone", "Apprendre à programmer, petits serveurs, robots, capteurs et prototypes."),
        "rw": ("Mudasobwa ku ikarita imwe (Raspberry Pi)", "Single-board computer ishyira processeur, RAM, ibyinjirizo n'ibisohokerwamo ku ikarita imwe ntoya ingana n'ikarita ya banki. Wongeraho ikarita y'ububiko, ikiyiha amashanyarazi, ecran na clavier. Ikoresha sisitemu isanzwe nka Linux, kandi utwenge twayo twa GPIO tuyemerera gucunga amatara, ibyuma bipima n'imodoka z'amashanyarazi (motors).",
               "Raspberry Pi, BeagleBone", "Kwiga gukora porogaramu, seriveri nto, robo, ibyuma bipima na prototypes."),
        "sw": ("Kompyuta ya ubao-mmoja (Raspberry Pi)", "Single-board computer huweka kichakataji, RAM, bandari na viunganishi kwenye ubao mdogo mmoja wa ukubwa wa kadi ya benki. Unaongeza kadi ya kumbukumbu kwa hifadhi, chanzo cha umeme, skrini na kibodi. Huendesha mfumo wa kawaida kama Linux, na pini zake za GPIO huiwezesha kudhibiti taa, vihisi na motori.",
               "Raspberry Pi, BeagleBone", "Kujifunza kuandika programu, seva ndogo, roboti, vihisi na mifano ya majaribio."),
    }),
    "microcontroller": (["arduino", "arduino uno", "microcontroller", "microcontrollers", "micro controller", "embedded computer", "embedded system", "embedded systems"],
                        "Arduino Uno - R3.jpg", "photo", {
        "en": ("Microcontroller / embedded computer (Arduino)", "A microcontroller is a tiny computer on a single chip with a processor, a little memory and input/output pins. It has no screen or operating system: it runs one program stored in its flash memory, over and over, reading sensors and switching things on or off. Embedded computers like this are hidden inside machines.",
               "Arduino Uno, ESP32, controllers inside washing machines and cars", "Appliances, cars, sensors, irrigation or cold-storage monitors, toys."),
        "fr": ("Microcontrôleur / ordinateur embarqué (Arduino)", "Un microcontrôleur est un minuscule ordinateur sur une seule puce, avec un processeur, un peu de mémoire et des broches d'entrée/sortie. Il n'a ni écran ni système d'exploitation : il exécute un seul programme stocké en mémoire flash, en boucle, lit des capteurs et active ou coupe des appareils. Les ordinateurs embarqués de ce type sont cachés dans les machines.",
               "Arduino Uno, ESP32, contrôleurs dans les machines à laver et les voitures", "Appareils ménagers, voitures, capteurs, surveillance d'irrigation ou de chambres froides, jouets."),
        "rw": ("Microcontroller / mudasobwa ihishe mu cyuma (Arduino)", "Microcontroller ni mudasobwa nto cyane iri ku gice kimwe (chip) gifite processeur, ububiko buke n'utwenge two kwinjiza/gusohora. Nta ecran cyangwa sisitemu ifite: ikora porogaramu imwe ibitse muri flash, ikayisubiramo, ikasoma ibyuma bipima ikazimya cyangwa igacana ibindi. Mudasobwa nk'izi ziba zihishe mu mashini.",
               "Arduino Uno, ESP32, ibyuma bicunga imashini zimesa n'imodoka", "Ibikoresho byo mu rugo, imodoka, ibyuma bipima, gukurikirana kuhira cyangwa ubukonje, ibikinisho."),
        "sw": ("Microcontroller / kompyuta iliyofichwa (Arduino)", "Microcontroller ni kompyuta ndogo sana kwenye chipu moja yenye kichakataji, kumbukumbu kidogo na pini za kuingiza/kutoa. Haina skrini wala mfumo wa uendeshaji: huendesha programu moja iliyohifadhiwa kwenye flash, tena na tena, ikisoma vihisi na kuwasha au kuzima vifaa. Kompyuta za aina hii hufichwa ndani ya mashine.",
               "Arduino Uno, ESP32, vidhibiti ndani ya mashine za kufua na magari", "Vifaa vya nyumbani, magari, vihisi, ufuatiliaji wa umwagiliaji au baridi, vitu vya kuchezea."),
    }),
    "console": (["console de jeux", "konsoli ya michezo", "konsoli", "game console", "games console", "gaming console", "video game console", "playstation", "ps5", "xbox", "nintendo switch"],
                "Black and white Playstation 5 base edition with controller.png", "photo", {
        "en": ("Game console", "A game console is a computer specialised for games. It has a CPU and a powerful graphics processor (GPU) sharing fast memory, an optical drive or fast SSD and wireless controllers. Game software is written for one fixed set of hardware, so games run consistently, and the output goes to a TV.",
               "PlayStation, Xbox, Nintendo Switch", "Video games, streaming video, online play."),
        "fr": ("Console de jeu", "Une console de jeu est un ordinateur spécialisé pour les jeux. Elle a un CPU et un processeur graphique (GPU) puissant partageant une mémoire rapide, un lecteur optique ou un SSD rapide et des manettes sans fil. Les jeux sont écrits pour un matériel fixe, donc ils fonctionnent de façon constante, et l'image va vers un téléviseur.",
               "PlayStation, Xbox, Nintendo Switch", "Jeux vidéo, vidéo en continu, jeu en ligne."),
        "rw": ("Konsole y'imikino (game console)", "Game console ni mudasobwa yakorewe imikino. Ifite CPU na GPU ikomeye zisangira RAM yihuta, disiki ya optical cyangwa SSD yihuta n'amamanette adafite insinga. Imikino yandikirwa ibyuma bidahinduka, bityo ikora kimwe, kandi ishusho ijya kuri televiziyo.",
               "PlayStation, Xbox, Nintendo Switch", "Imikino ya videwo, kureba videwo kuri internet, gukina kuri internet."),
        "sw": ("Konsoli ya michezo (game console)", "Game console ni kompyuta maalum kwa michezo. Ina CPU na kichakataji cha picha chenye nguvu (GPU) vinavyoshiriki kumbukumbu ya kasi, diski ya optiki au SSD ya kasi na vidhibiti visivyo na waya. Michezo huandikwa kwa vifaa visivyobadilika, hivyo hufanya kazi kwa uthabiti, na picha huenda kwenye televisheni.",
               "PlayStation, Xbox, Nintendo Switch", "Michezo ya video, kutiririsha video, kucheza mtandaoni."),
    }),
    "analog": (["ordinateur analogique", "mudasobwa ya analog", "kompyuta ya analogi", "analog computer", "analogue computer", "analog computers", "differential analyzer", "differential analyser"],
               "NASA Differential Analyzer.jpg", "photo", {
        "en": ("Analog computer", "An analog computer solves problems with continuously varying physical quantities such as voltage, gears or fluid flow instead of numbers made of 0s and 1s. Parts such as amplifiers, integrators and gears are connected so that their behaviour mirrors the equation to be solved, and the answer is read from a meter or plotter.",
               "Differential analyzer, slide rule, mechanical fire-control computers", "Historic simulation of motion, flight and engineering equations."),
        "fr": ("Ordinateur analogique", "Un ordinateur analogique résout les problèmes avec des grandeurs physiques qui varient de façon continue, comme la tension, les engrenages ou l'écoulement d'un fluide, au lieu de nombres faits de 0 et de 1. Des éléments comme les amplificateurs, les intégrateurs et les engrenages sont reliés pour que leur comportement imite l'équation à résoudre ; la réponse se lit sur un cadran ou un traceur.",
               "Analyseur différentiel, règle à calcul, calculateurs mécaniques de tir", "Simulation historique de mouvement, de vol et d'équations d'ingénierie."),
        "rw": ("Mudasobwa ya analog", "Analog computer ikemura ibibazo ikoresheje ingano z'umubiri zihindagurika buri gihe nka voltage, amapine cyangwa imigendere y'amazi, aho gukoresha imibare igizwe na 0 na 1. Ibice nk'amplifiers, integrators n'amapine bihuzwa ku buryo imikorere yabyo ihuye n'ingingo (equation) igomba gukemurwa, igisubizo kigasomwa kuri cadran cyangwa traceur.",
               "Differential analyzer, règle à calcul, mashini za kera zo kurasa", "Gukora ibigereranyo bya kera by'imigendere, indege n'ingingo z'ubwubatsi."),
        "sw": ("Kompyuta ya analogi", "Kompyuta ya analogi hutatua matatizo kwa kutumia kiasi cha kimwili kinachobadilika mfululizo kama volteji, gia au mtiririko wa maji badala ya nambari za 0 na 1. Sehemu kama vikuza sauti, viunganishi na gia huunganishwa ili tabia yake ifanane na mlinganyo unaotatuliwa, na jibu husomwa kwenye kipimo au kichora.",
               "Differential analyzer, rula ya kukokotoa, kompyuta za kale za kulenga", "Uigaji wa kihistoria wa mwendo, safari za anga na milinganyo ya uhandisi."),
    }),
    "eniac": (["eniac", "first computer", "first computers", "vacuum tube computer", "first generation computer", "first generation computers"],
              "ENIAC-changing a tube (cropped).jpg", "photo", {
        "en": ("ENIAC (an early electronic computer)", "ENIAC, finished in 1945 in the USA, was one of the first large general-purpose electronic digital computers. It used about 17,000 vacuum tubes as switches to do arithmetic, and it was programmed by rewiring cables and setting switches. It filled a large room, used a great deal of power, and tubes had to be replaced often.",
               "ENIAC, UNIVAC", "Ballistics tables and scientific calculations in the 1940s."),
        "fr": ("ENIAC (un des premiers ordinateurs électroniques)", "L'ENIAC, achevé en 1945 aux États-Unis, fut l'un des premiers grands ordinateurs numériques électroniques à usage général. Il utilisait environ 17 000 tubes à vide comme interrupteurs pour calculer, et se programmait en rebranchant des câbles et en réglant des commutateurs. Il occupait une grande salle, consommait beaucoup d'énergie et il fallait remplacer souvent des tubes.",
               "ENIAC, UNIVAC", "Tables balistiques et calculs scientifiques dans les années 1940."),
        "rw": ("ENIAC (imwe mu mudasobwa za mbere za elegitoronike)", "ENIAC, yarangiye mu 1945 muri Amerika, yari imwe mu mudasobwa nini za mbere za elegitoronike za digital zikora imirimo itandukanye. Yakoreshaga amatiyo y'ubusa (vacuum tubes) agera ku 17.000 nk'ibyuma bifunga kandi bigafungura mu kubara, ikagirwa porogaramu uhinduye imigozi n'ibyuma bifunga. Yari ifite icyumba kinini, yarakoreshaga amashanyarazi menshi kandi amatiyo yasimbuzwaga kenshi.",
               "ENIAC, UNIVAC", "Imbonerahamwe z'amasasu n'ibarurishamibare bya siyansi mu myaka ya 1940."),
        "sw": ("ENIAC (kompyuta ya kwanza ya elektroniki)", "ENIAC, iliyokamilika mwaka 1945 Marekani, ilikuwa mojawapo ya kompyuta kubwa za kwanza za kielektroniki za dijitali za matumizi ya jumla. Ilitumia takriban mirija 17,000 ya utupu kama swichi kufanya hesabu, na ilipangwa kwa kubadilisha nyaya na kuweka swichi. Ilijaza chumba kikubwa, ilitumia umeme mwingi na mirija ilibadilishwa mara nyingi.",
               "ENIAC, UNIVAC", "Majedwali ya balistiki na hesabu za kisayansi miaka ya 1940."),
    }),
    "quantum": (["quantum computer", "quantum computers", "ordinateur quantique", "mudasobwa ya quantum", "kompyuta ya quantum", "kompyuta ya kwanta", "quantum computing", "qubit", "qubits"],
                None, None, {
        "en": ("Quantum computer", "A quantum computer uses qubits instead of ordinary bits. A qubit can be in a combination of 0 and 1 at once (superposition) and qubits can be linked (entanglement); algorithms steer these states so wrong answers cancel and right ones are more likely when measured. Today's machines are small and noisy, are kept near absolute zero in some designs, and help only with certain problems, not everyday tasks.",
               "IBM Quantum, Google Sycamore", "Research in chemistry, materials, cryptography and optimisation; not a replacement for normal computers."),
        "fr": ("Ordinateur quantique", "Un ordinateur quantique utilise des qubits au lieu de bits ordinaires. Un qubit peut être dans une combinaison de 0 et de 1 à la fois (superposition) et les qubits peuvent être liés (intrication) ; les algorithmes dirigent ces états pour que les mauvaises réponses s'annulent et que les bonnes soient plus probables à la mesure. Les machines actuelles sont petites et bruitées, certaines sont maintenues près du zéro absolu, et n'aident que pour certains problèmes, pas pour les tâches quotidiennes.",
               "IBM Quantum, Google Sycamore", "Recherche en chimie, matériaux, cryptographie et optimisation ; ne remplace pas les ordinateurs ordinaires."),
        "rw": ("Mudasobwa ya quantum", "Quantum computer ikoresha qubits aho gukoresha bits zisanzwe. Qubit ishobora kuba 0 na 1 icyarimwe (superposition) kandi qubits zishobora guhuzwa (entanglement); algorithms ziyobora ibyo bihe ku buryo ibisubizo bitari byo bivanaho, ibiboneye bikarushaho kuboneka iyo bipimwe. Imashini z'ubu ni nto kandi zigira urusaku, zimwe zibikwa hafi y'ubukonje bwa zero absolu, kandi zifasha ku bibazo bimwe gusa, ntizikora imirimo ya buri munsi.",
               "IBM Quantum, Google Sycamore", "Ubushakashatsi muri chimie, ibikoresho, cryptographie na optimisation; ntisimbura mudasobwa zisanzwe."),
        "sw": ("Kompyuta ya quantum", "Kompyuta ya quantum hutumia qubits badala ya bits za kawaida. Qubit inaweza kuwa mchanganyiko wa 0 na 1 kwa wakati mmoja (superposition) na qubits zinaweza kuunganishwa (entanglement); algoriti huelekeza hali hizi ili majibu yasiyo sahihi yafutike na sahihi yawe na uwezekano mkubwa yakipimwa. Mashine za leo ni ndogo na zenye kelele, baadhi hudumishwa karibu na sifuri kabisa, na husaidia matatizo fulani tu, si kazi za kila siku.",
               "IBM Quantum, Google Sycamore", "Utafiti wa kemia, vifaa, usimbaji fiche na uboreshaji; haichukui nafasi ya kompyuta za kawaida."),
    }),
    "workstation": (["workstation", "workstations", "station de travail", "kituo cha kazi", "graphics workstation"],
                    None, None, {
        "en": ("Workstation", "A workstation is a high-performance desktop-class computer for demanding professional work. It has a many-core CPU, lots of error-correcting RAM, a professional graphics card and fast storage, so heavy programs such as 3D design, video editing or engineering simulation run smoothly and reliably.",
               "Dell Precision, HP Z, Apple Mac Pro", "3D modelling, video editing, engineering, scientific computing."),
        "fr": ("Station de travail", "Une station de travail est un ordinateur de type bureau très performant pour des travaux professionnels exigeants. Elle a un CPU à nombreux cœurs, beaucoup de RAM à correction d'erreurs, une carte graphique professionnelle et un stockage rapide, de sorte que les logiciels lourds (conception 3D, montage vidéo, simulation) fonctionnent de façon fluide et fiable.",
               "Dell Precision, HP Z, Apple Mac Pro", "Modélisation 3D, montage vidéo, ingénierie, calcul scientifique."),
        "rw": ("Workstation (mudasobwa y'akazi gakomeye)", "Workstation ni mudasobwa ikomeye ku rwego rwa desktop yagenewe imirimo y'umwuga isaba byinshi. Ifite CPU ifite cores nyinshi, RAM nyinshi ikosora amakosa, ikarita y'amashusho y'umwuga n'ububiko bwihuta, bityo porogaramu ziremereye nko gushushanya muri 3D, guhindura videwo cyangwa gukora ibigereranyo by'ubwubatsi zikora neza kandi zizewe.",
               "Dell Precision, HP Z, Apple Mac Pro", "Gushushanya muri 3D, guhindura videwo, ubwubatsi, ibarurishamibare bya siyansi."),
        "sw": ("Kituo cha kazi (workstation)", "Workstation ni kompyuta ya daraja la desktop yenye utendaji wa juu kwa kazi za kitaalamu zinazohitaji nguvu. Ina CPU yenye cores nyingi, RAM nyingi inayorekebisha makosa, kadi ya picha ya kitaalamu na hifadhi ya kasi, hivyo programu nzito kama usanifu wa 3D, uhariri wa video au uigaji wa uhandisi hufanya kazi vizuri na kwa uhakika.",
               "Dell Precision, HP Z, Apple Mac Pro", "Uundaji wa 3D, uhariri wa video, uhandisi, kompyuta za kisayansi."),
    }),
}

_WIKI = {"desktop": "Desktop computer", "laptop": "Laptop", "tablet": "Tablet computer", "smartphone": "Smartphone", "smartwatch": "Smartwatch",
         "chromebook": "Chromebook", "allinone": "All-in-one computer", "server": "Server (computing)", "mainframe": "Mainframe computer",
         "supercomputer": "Supercomputer", "minicomputer": "Minicomputer", "sbc": "Single-board computer", "microcontroller": "Microcontroller",
         "console": "Video game console", "analog": "Analog computer", "eniac": "ENIAC", "quantum": "Quantum computing", "workstation": "Workstation", "computer": "Computer"}

_OVERVIEW = {
    "en": ("Types of computers",
           "Computers come in many forms, from tiny chips to room-sized machines. All of them take input, process it with a processor using memory and a program, store data, and give output. Types covered here are listed below; ask about any one (for example “how does a supercomputer work?”) for a short explanation and a photo.",
           "Everyday: desktop, laptop, tablet, smartphone, smartwatch, Chromebook, all-in-one, game console.", "Large and shared: server, mainframe, supercomputer, minicomputer, workstation.",
           "Small and embedded: Raspberry Pi (single-board), Arduino (microcontroller).", "Historic and special: ENIAC (early electronic), analog computer, quantum computer."),
    "fr": ("Types d'ordinateurs",
           "Les ordinateurs existent sous de nombreuses formes, de minuscules puces à des machines grandes comme une salle. Tous reçoivent des données, les traitent avec un processeur, de la mémoire et un programme, les stockent et fournissent un résultat. Les types couverts sont listés ci-dessous ; demandez-en un (par exemple « comment fonctionne un superordinateur ? ») pour une courte explication et une photo.",
           "Courants : ordinateur de bureau, portable, tablette, smartphone, montre connectée, Chromebook, tout-en-un, console de jeu.", "Grands et partagés : serveur, ordinateur central, superordinateur, mini-ordinateur, station de travail.",
           "Petits et embarqués : Raspberry Pi (monocarte), Arduino (microcontrôleur).", "Historiques et spéciaux : ENIAC (premier électronique), ordinateur analogique, ordinateur quantique."),
    "rw": ("Ubwoko bwa mudasobwa",
           "Mudasobwa ziza mu buryo butandukanye, kuva ku tuntu duto cyane kugeza ku mashini zingana icyumba. Zose zakira amakuru, ziyatunganyiriza muri processeur zikoresheje ububiko na porogaramu, zikayabika, zigatanga igisubizo. Ubwoko bwose buvugwa hano burondowe hasi; baza ku bwo ushaka (urugero «supercomputer ikora ite?») uhabwe ibisobanuro bigufi n'ifoto.",
           "Izikoreshwa buri munsi: desktop, laptop, tablet, smartphone, smartwatch, Chromebook, all-in-one, game console.", "Nini zisangiwe: seriveri, mainframe, supercomputer, minicomputer, workstation.",
           "Nto zihishe: Raspberry Pi (ikarita imwe), Arduino (microcontroller).", "Iza kera n'iz'umwihariko: ENIAC, mudasobwa ya analog, mudasobwa ya quantum."),
    "sw": ("Aina za kompyuta",
           "Kompyuta zipo kwa maumbo mengi, kutoka chipu ndogo hadi mashine zinazojaza chumba. Zote hupokea data, huichakata kwa kichakataji kwa kutumia kumbukumbu na programu, huihifadhi na kutoa matokeo. Aina zilizoshughulikiwa zimeorodheshwa hapa chini; uliza kuhusu yoyote (mfano «supercomputer inafanyaje kazi?») upate maelezo mafupi na picha.",
           "Za kila siku: desktop, laptop, tablet, simu janja, saa janja, Chromebook, all-in-one, konsoli ya michezo.", "Kubwa na za kushirikiwa: seva, mainframe, supercomputer, minicomputer, workstation.",
           "Ndogo zilizofichwa: Raspberry Pi (ubao-mmoja), Arduino (microcontroller).", "Za kihistoria na maalum: ENIAC, kompyuta ya analogi, kompyuta ya quantum."),
}

_UI = {  # (steps label, examples, typical use, photo caption, [unused], photo-missing note)
    "en": ("Key facts", "Examples", "Typical use", "Photo from the Wikipedia article “{t}”, hosted on Wikimedia Commons (author and licence on the file page)", "", "The photo could not be loaded right now (it needs internet access). The explanation above is complete."),
    "fr": ("À retenir", "Exemples", "Usage courant", "Photo de l'article Wikipédia « {t} », hébergée sur Wikimedia Commons (auteur et licence sur la page du fichier)", "", "La photo n'a pas pu être chargée pour le moment (accès Internet requis). L'explication ci-dessus est complète."),
    "rw": ("Ibyingenzi", "Ingero", "Icyo ikoreshwa", "Ifoto iva ku rupapuro rwa Wikipedia «{t}», ibitse kuri Wikimedia Commons (uwayifashe n'uruhushya biri ku rupapuro rwayo)", "", "Ifoto ntibashije kuboneka ubu (bisaba internet). Ibisobanuro biri hejuru byuzuye."),
    "sw": ("Mambo muhimu", "Mifano", "Matumizi ya kawaida", "Picha kutoka makala ya Wikipedia «{t}», iliyohifadhiwa Wikimedia Commons (mwandishi na leseni ziko kwenye ukurasa wa faili)", "", "Picha haikuweza kupakiwa sasa (inahitaji intaneti). Maelezo yaliyo juu yamekamilika."),
}

_CUES = {"what", "whats", "how", "work", "works", "working", "explain", "explains", "photo", "photos", "picture", "pictures", "image", "images", "show", "type", "types", "kind", "kinds",
         "define", "definition", "meaning", "about", "tell", "describe", "difference", "iki", "ikora", "ikoreshwa", "bikora", "sobanura", "risobanura", "ifoto", "ishusho", "ubwoko", "bwoko",
         "quoi", "comment", "fonctionne", "fonctionnent", "expliquer", "explique", "definition", "signifie", "nini", "inafanyaje", "inafanya", "hufanya", "kazi", "picha", "aina", "eleza", "maana", "ni"}
_AMBIGUOUS = {"console", "konsoli", "sbc", "rpi", "pc", "wearable", "server", "servers", "serveur", "serveurs", "seva", "seriveri", "ibm z", "ps5", "xbox", "seva"}  # bare mention alone is not enough
_HOW_CUES = {"how", "work", "works", "working", "explain", "comment", "fonctionne", "ikora", "ikorana", "uburyo", "inafanyaje", "hufanya", "inafanya"}
_BLOCK = {"virus", "viruses", "hack", "hacked", "hacker", "hackers", "malware", "password", "passwords", "scam", "phishing", "security", "secure", "stolen", "lost", "lose", "steal", "theft",
          "infected", "attack", "attacked", "breach", "ransomware", "perdu", "vole", "volee", "piratage", "pirate", "yibwe", "yatakaye", "yazimiye", "yibasiwe", "imbwa", "ukwiba", "umutekano", "iba", "wizi", "imeibiwa", "umepotea", "potea", "iliibiwa", "usalama", "mtego"}
_TYPE_WORDS = {"type", "types", "kind", "kinds", "list", "all", "ubwoko", "bwoko", "aina", "types"}
_COMPUTER_WORDS = {"computer", "computers", "ordinateur", "ordinateurs", "mudasobwa", "kompyuta"}


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


_INDEX = []  # (alias folded, key), longest alias first
for _k, (_aliases, *_rest) in _DATA.items():
    for _a in _aliases:
        _INDEX.append((fold(_a), _k))
_INDEX.sort(key=lambda t: -len(t[0]))
COUNT = len(_DATA)


def _alias_hits(text):
    padded = f" {text} "
    seen, hits = set(), []
    for alias, key in _INDEX:
        if f" {alias} " in padded and key not in seen:
            seen.add(key)
            hits.append((key, alias))
    return hits


def photo_url(file_name, width=640):
    return COMMONS_PATH + quote(file_name.replace(" ", "_")) + f"?width={width}"


def page_url(file_name):
    return COMMONS_FILE + quote(file_name.replace(" ", "_"))


def _entry(key, lang):
    aliases, file_name, kind, texts = _DATA[key]
    entry = {"id": "computer_" + key, "related": [], "kind": "computer", "key": key, "title": {}, "answer": {}, "steps": {}, "steps_label": {},
             "image_query": {"wiki": _WIKI[key], "file": file_name}}
    for l in LANGS:
        name, how, examples, use = texts[l]
        u = _UI[l]
        entry["title"][l] = name
        entry["answer"][l] = how
        entry["steps"][l] = [f"{u[1]}: {examples}", f"{u[2]}: {use}"]
        entry["steps_label"][l] = u[0]
    return entry


def _get_json(url, timeout=5):
    import json, urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0 (educational app; ebanatrm100@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _head_ok(url, timeout=5):
    import urllib.request
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "KinyaShieldRW/1.0 (educational app; ebanatrm100@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return 200 <= r.status < 300 and str(r.headers.get("Content-Type", "")).startswith("image/")


_CACHE = {}


def resolve_image(entry, lang="en"):
    """Return {'url', 'page', 'caption'} for a computer entry, or None. Never raises.

    1) lead image of the Wikipedia article (REST summary), accepted only if hosted on Wikimedia Commons (free licence);
    2) otherwise the Commons file named in the data, accepted only if the server confirms it is an image.
    Results (including failures) are cached for the life of the process, so one question costs at most a couple of requests."""
    try:
        q = entry.get("image_query")
        if not q:
            return None
        k = lang if lang in LANGS else "en"
        key = (q["wiki"], q.get("file"))
        if key not in _CACHE:
            found = None
            title = q["wiki"]
            page = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="_()")
            try:
                data = _get_json("https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(title.replace(" ", "_"), safe="_()"))
                src = (data.get("thumbnail") or {}).get("source") or ""
                orig = (data.get("originalimage") or {}).get("source") or ""
                if "/wikipedia/commons/" in src:
                    found = {"url": src, "page": data.get("content_urls", {}).get("desktop", {}).get("page", page), "wiki": title}
                elif "/wikipedia/commons/" in orig and not orig.lower().endswith((".svg", ".tif", ".tiff")):
                    found = {"url": orig, "page": page, "wiki": title}
            except Exception:
                found = None
            if found is None and q.get("file"):
                try:
                    url = photo_url(q["file"])
                    if _head_ok(url):
                        found = {"url": url, "page": page_url(q["file"]), "wiki": title}
                except Exception:
                    found = None
            _CACHE[key] = found
        found = _CACHE[key]
        if not found:
            return None
        return {"url": found["url"], "page": found["page"], "caption": _UI[k][3].format(t=found["wiki"])}
    except Exception:
        return None


def missing_photo_note(lang="en"):
    return _UI[lang if lang in LANGS else "en"][5]


def _overview(lang):
    entry = {"id": "computer_types", "related": [], "kind": "computer", "key": "types", "title": {}, "answer": {}, "steps": {}, "steps_label": {}}
    for l in LANGS:
        t, intro, *rows = _OVERVIEW[l]
        entry["title"][l], entry["answer"][l], entry["steps"][l], entry["steps_label"][l] = t, intro, list(rows), _UI[l][0]
    return entry


def find(question, lang="en"):
    """Return a guide-shaped entry for a question about a type of computer, or None.

    Rules (so ordinary questions are not hijacked): the question must be short, must name a known type of computer, and must either
    be just that name (1-3 words) or contain a cue such as what/how/explain/photo/ni iki/comment/nini. Words that are easily
    something else (console, server, summit...) need a cue. "types of computers" returns the overview."""
    q = (question or "").strip()
    if not q or len(q) > 140:
        return None
    text = fold(q)
    toks = text.split()
    if not toks:
        return None
    tset = set(toks)
    if (tset & _TYPE_WORDS) and (tset & _COMPUTER_WORDS) and len(toks) <= 10:
        hits_t = [h for h in _alias_hits(text) if h[0] != "computer"]
        if not hits_t:
            return _overview(lang)
    hits = _alias_hits(text)
    if not hits:
        return None
    key, alias = hits[0]
    if tset & _BLOCK:
        return None
    if key == "computer":
        if not (tset & _HOW_CUES) or len(toks) > 8 or len(hits) > 1:
            return None
    has_cue = bool(tset & _CUES)
    bare = len(toks) <= 3 and alias.replace(" ", "") == "".join(toks) or len(toks) <= 3 and all(t in alias.split() for t in toks)
    if bare and alias not in _AMBIGUOUS:
        return _entry(key, lang)
    if has_cue:
        return _entry(key, lang)
    return None
