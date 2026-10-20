"""Name meanings for the AI Assistant (offline). Pure Python, no Streamlit.

This is a curated list of common names (Rwandan/Kinyarwanda, biblical, Arabic, Swahili, African, French, English and others),
NOT every name in the world. Meanings follow common reference usage; many names have more than one explanation and spellings vary.
fr/rw/sw wording is a draft pending review by fluent speakers. Unknown names fall through to the AI (if configured)."""
from __future__ import annotations
import re, unicodedata

LANGS = ("en", "fr", "rw", "sw")

ORIGIN = {  # key: (en, fr, rw, sw)
    "rw": ("Kinyarwanda", "kinyarwanda", "Ikinyarwanda", "Kinyarwanda"),
    "he": ("Hebrew", "hébraïque", "Igiheburayo", "Kiebrania"),
    "gr": ("Greek", "grecque", "Ikigereki", "Kigiriki"),
    "la": ("Latin", "latine", "Ikilatini", "Kilatini"),
    "ar": ("Arabic", "arabe", "Icyarabu", "Kiarabu"),
    "sw": ("Swahili", "swahilie", "Igiswahili", "Kiswahili"),
    "en": ("English", "anglaise", "Icyongereza", "Kiingereza"),
    "ge": ("Germanic", "germanique", "Igikerumani (Germanic)", "Kijerumani cha kale (Germanic)"),
    "fr": ("French", "française", "Igifaransa", "Kifaransa"),
    "ce": ("Celtic/Irish", "celtique/irlandaise", "Igiselitike/Igirilande", "Kiselti/Kiayalandi"),
    "ak": ("Akan (Ghana)", "akan (Ghana)", "Akan (Ghana)", "Akan (Ghana)"),
    "ig": ("Igbo (Nigeria)", "igbo (Nigeria)", "Igbo (Nigeria)", "Igbo (Nigeria)"),
    "yo": ("Yoruba (Nigeria)", "yoruba (Nigeria)", "Yoruba (Nigeria)", "Yoruba (Nigeria)"),
    "zu": ("Zulu (South Africa)", "zoulou (Afrique du Sud)", "Zulu (Afurika y'Epfo)", "Kizulu (Afrika Kusini)"),
    "ki": ("Kikuyu (Kenya)", "kikuyu (Kenya)", "Kikuyu (Kenya)", "Kikuyu (Kenya)"),
    "sa": ("Sanskrit/Hindi", "sanskrite/hindi", "Igisansikiriti/Igihindi", "Kisanskriti/Kihindi"),
    "ja": ("Japanese", "japonaise", "Igiyapani", "Kijapani"),
    "pe": ("Persian", "persane", "Igiperisi", "Kiajemi"),
    "on": ("Old Norse", "vieux norrois", "Old Norse", "Kinorse cha kale (Old Norse)"),
}

# Name | other spellings (comma separated, or -) | origin key | W = also an ordinary word (needs the word "name" in the question) or - | en | fr | rw | sw
_TABLE = """
Mugisha|-|rw|-|lucky, blessed one|chanceux, béni|umunyamahirwe, uhiriwe|mwenye bahati, aliyebarikiwa
Keza|-|rw|-|beautiful, good|beau (belle), bon (bonne)|nziza, nyamwiza|mzuri, mwema
Ineza|-|rw|-|kindness, goodness|bonté, gentillesse|ineza, ubugwaneza|wema, fadhili
Iradukunda|-|rw|-|God loves us|Dieu nous aime|Imana iradukunda|Mungu anatupenda
Ishimwe|-|rw|-|praise, thanksgiving|louange, action de grâce|ishimwe, gushimira|sifa, shukrani
Nshuti|-|rw|-|friend|ami(e)|inshuti|rafiki
Umutoni|-|rw|-|favoured, cherished one|favori(te), chéri(e)|uwatoneshejwe, ukundwa|mpendwa, aliyependelewa
Uwera|-|rw|-|pure, holy one|pur(e), saint(e)|umuziranenge|safi, mtakatifu
Dusabimana|-|rw|-|let us ask God (we pray to God)|prions Dieu|dusabe Imana|tumwombe Mungu
Hakizimana|-|rw|-|God saves|Dieu sauve|Imana ikiza|Mungu huokoa
Mukunzi|-|rw|-|beloved one|bien-aimé(e)|ukundwa|mpendwa
Nkurunziza|-|rw|-|bearer of good news|porteur de bonne nouvelle|uzana inkuru nziza|mleta habari njema
Byiringiro|-|rw|-|hope|espoir|ibyiringiro|matumaini
Rukundo|-|rw|-|love|amour|urukundo|upendo
Gisubizo|-|rw|-|answer (to a prayer)|réponse (à une prière)|igisubizo|jibu
Kwizera|-|rw|-|trust, hope, faith|confiance, espoir, foi|kwizera|imani, tumaini
Tuyishime|-|rw|-|let us rejoice and give thanks|réjouissons-nous et rendons grâce|dushime|tushangilie na kushukuru
Ngabo|-|rw|-|shield, protector|bouclier, protecteur|ingabo|ngao, mlinzi
Mahoro|-|rw|-|peace|paix|amahoro|amani
Uwamahoro|-|rw|-|child of peace, peaceful one|enfant de la paix|uw'amahoro|mtoto wa amani
Isimbi|-|rw|-|pearl, cowrie shell|perle, cauri|isimbi|lulu, kauri
Ingabire|-|rw|-|gift|don, cadeau|impano|zawadi
Impano|-|rw|-|gift, talent|don, talent|impano|zawadi, kipaji
Mukiza|-|rw|-|saviour, healer|sauveur, guérisseur|ukiza|mwokozi, mponyaji
Uwimana|-|rw|-|one who belongs to God|celui (celle) qui appartient à Dieu|uw'Imana|wa Mungu
Mugabo|-|rw|-|man, brave man|homme, brave|umugabo|mwanaume, shujaa
John|jean,johan,johannes,yohana,yohani,juan,ivan|he|-|God is gracious|Dieu est miséricordieux|Imana igira ubuntu|Mungu ni mwenye neema
David|davide,daudi|he|-|beloved|bien-aimé|ukundwa|mpendwa
Daniel|daniele,danieli|he|-|God is my judge|Dieu est mon juge|Imana ni umucamanza wanjye|Mungu ni hakimu wangu
Samuel|samweli|he|-|God has heard|Dieu a entendu|Imana yumvise|Mungu amesikia
Joseph|josef,yosefu,josephine,jose|he|-|he will add (God will increase)|il ajoutera (Dieu augmentera)|azongera (Imana izongera)|ataongeza (Mungu ataongeza)
Michael|michel,mikaeli,miguel,mikael|he|-|who is like God?|qui est comme Dieu ?|ni nde uhwanye n'Imana?|ni nani aliye kama Mungu?
Gabriel|gabrieli,gabriella|he|-|God is my strength|Dieu est ma force|Imana ni imbaraga zanjye|Mungu ni nguvu yangu
Raphael|rafael,rafaeli|he|-|God has healed|Dieu a guéri|Imana yakijije|Mungu ameponya
Emmanuel|emanuel,emmanuelle,manuel,imanueli|he|-|God is with us|Dieu est avec nous|Imana turi kumwe|Mungu yu pamoja nasi
Joshua|josue,yoshua,yoshuwa|he|-|the Lord is salvation|le Seigneur est salut|Uwiteka ni agakiza|Bwana ni wokovu
Joel|yoeli|he|-|the Lord is God|le Seigneur est Dieu|Uwiteka ni Imana|Bwana ni Mungu
Elijah|elie,eliya,elias|he|-|my God is the Lord|mon Dieu est le Seigneur|Imana yanjye ni Uwiteka|Mungu wangu ni Bwana
Isaac|isaka,isack|he|-|he laughs|il rit|aseka|anacheka
Jacob|jacques,yakobo,jakob|he|-|supplanter (he who holds the heel)|celui qui supplante (qui tient le talon)|usimbura (ufashe agatsinsino)|anayeshika kisigino, mwenye kuchukua nafasi
Benjamin|benyamini,benjamine|he|-|son of the right hand|fils de la main droite|umuhungu w'ukuboko kw'iburyo|mwana wa mkono wa kuume
Sarah|sara|he|-|princess|princesse|umwamikazi|binti mfalme
Rebecca|rebeka,rebecca|he|-|to bind, captivating|lier, captivante|guhuza, ukurura|kufunga, mvutiaji
Rachel|rachelle,raheli|he|-|ewe (female sheep)|brebis|intama y'ingore|kondoo jike
Elizabeth|elisabeth,elizabeti,elisabetta|he|-|my God is an oath (God's promise)|mon Dieu est un serment (promesse de Dieu)|Imana yanjye ni indahiro|Mungu wangu ni kiapo (ahadi ya Mungu)
Hannah|hanna,anna,ana,anne|he|-|grace, favour|grâce, faveur|ubuntu, igikundiro|neema, upendeleo
Esther|ester,estere|pe|-|star|étoile|inyenyeri|nyota
Eve|eva,eve,hawa,awa|he|W|life, living one|vie, vivante|ubuzima, ubaho|uhai, aliye hai
Abigail|abigaili|he|-|my father is joy|mon père est joie|data ni ibyishimo|baba yangu ni furaha
Matthew|matthieu,mathayo,matayo,mateo|he|-|gift of the Lord|don du Seigneur|impano y'Uwiteka|zawadi ya Bwana
Thomas|tomasi,tom,thom|he|-|twin|jumeau|impanga|pacha
Simon|simeon,simoni|he|-|he has heard|il a entendu|yumvise|amesikia
Nathan|nathanael,nathaniel,natan|he|-|he gave (God has given)|il a donné|yatanze|alitoa
Jonathan|yonatani|he|-|the Lord has given|le Seigneur a donné|Uwiteka yatanze|Bwana ametoa
Moses|moise,musa,mose|he|-|drawn out (of the water)|tiré (des eaux)|uwakuwe mu mazi|aliyevutwa (majini)
Abraham|ibrahim,abrahamu,abraham|he|-|father of many|père d'une multitude|se w'abatari bake|baba wa wengi
Noah|noe,nuhu|he|-|rest, comfort|repos, consolation|ikiruhuko, ihumure|raha, faraja
Solomon|salomon,suleiman,sulemani|he|-|peaceful|pacifique|w'amahoro|mwenye amani
Jeremiah|jeremie,yeremia,jeremy|he|-|the Lord will lift up|le Seigneur élèvera|Uwiteka azazamura|Bwana atainua
Ezra|ezra|he|-|help|aide|ubufasha|msaada
Levi|lewi|he|-|joined, attached|uni, attaché|uhuje, uhambiriye|aliyeunganishwa
Mary|marie,maria,mariam,maryam,miriam,mariamu|he|-|of uncertain origin; often linked to "beloved" or "wished-for child"|origine incertaine ; souvent liée à « bien-aimée » ou « enfant désirée »|inkomoko ntizwi neza; akenshi ifitanye isano na «ukundwa» cyangwa «umwana wifujwe»|asili haijulikani; mara nyingi huhusishwa na «mpendwa» au «mtoto aliyetamaniwa»
Peter|pierre,petro,pedro,petri|gr|-|rock|pierre, roc|urutare|mwamba
Paul|paul,paulo,pauline,paula,paulina|la|-|small, humble|petit, humble|muto, woroheje|mdogo, mnyenyekevu
Andrew|andre,andrea,andereya|gr|-|manly, brave|viril, courageux|intwari|jasiri
Philip|philippe,filipo,felipe,phillip|gr|-|lover of horses|ami des chevaux|ukunda amafarasi|mpenda farasi
Stephen|stephane,steven,stefano,stefano,stefani|gr|-|crown|couronne|ikamba, ingofero y'ishema|taji
James|jacques,yakobo,jaime|he|-|supplanter (a form of Jacob)|celui qui supplante (forme de Jacob)|usimbura (inyito ya Jacob)|mwenye kuchukua nafasi (umbo la Jacob)
Christopher|christophe,kristofa|gr|-|bearer of Christ|porteur du Christ|uheka Kristo|abebaye Kristo
George|georges,jorge,yohana,gorge|gr|-|farmer|agriculteur|umuhinzi|mkulima
Nicholas|nicolas,nikolasi,nicola|gr|-|victory of the people|victoire du peuple|intsinzi y'abaturage|ushindi wa watu
Theodore|theodor,theodoro,theodule|gr|-|gift of God|don de Dieu|impano y'Imana|zawadi ya Mungu
Timothy|timothee,timotheo,timoteo|gr|-|honouring God|qui honore Dieu|wubaha Imana|mwenye kumheshimu Mungu
Sophia|sophie,sofia,sofi|gr|-|wisdom|sagesse|ubwenge|hekima
Irene|irene,irena|gr|-|peace|paix|amahoro|amani
Catherine|katherine,kathryn,katarina,katherina,katrina,cathy|gr|-|pure|pure|umuziranenge|safi
Alexander|alexandre,alexandra,alex,aleksandr,iskander|gr|-|defender of men|défenseur des hommes|umurinzi w'abantu|mlinzi wa watu
Victor|victoire,viktor,victoria|la|-|conqueror, winner|vainqueur|uwatsinze|mshindi
Vincent|vincens,vicenti|la|-|conquering|qui vainc|utsinda|mshinda
Clement|clemence,clementine,clemente|la|-|merciful, gentle|clément, doux|ugira imbabazi|mwenye huruma
Patrick|patrice,patricia,patrizio|la|-|nobleman|noble|umunyacyubahiro|mtukufu
Felix|felicien,felicity,felicite|la|-|happy, fortunate|heureux, chanceux|wishimye, umunyamahirwe|mwenye furaha, bahati
Mark|marc,marco,marko,marcus,marcel|la|W|dedicated to Mars (the Roman god of war)|consacré à Mars (dieu romain de la guerre)|uwegurirwa Mars (imana y'intambara)|aliyewekwa wakfu kwa Mars
Lawrence|laurent,lorenzo,laurence,lawrence,lorenz|la|-|from Laurentum (linked to the laurel)|de Laurentum (lié au laurier)|w'i Laurentum (afitanye isano n'igiti cya laurier)|wa Laurentum (anayehusiana na mlaureli)
Innocent|innocente,innocens|la|-|innocent, harmless|innocent, inoffensif|umwere|asiye na hatia
Olivier|oliver,olivia,oliva|la|-|olive tree|olivier|igiti cya olive|mzeituni
Justin|justine,justus|la|-|just, fair|juste, équitable|ukiranuka|mwadilifu
Valentin|valentine,valentino,valentina|la|-|strong, healthy|fort, en bonne santé|ukomeye, ufite ubuzima bwiza|mwenye nguvu na afya
Dieudonné|dieudonn|fr|-|given by God|donné par Dieu|watanzwe n'Imana|aliyepewa na Mungu
Fidèle|fideline|fr|-|faithful|fidèle|umwizerwa|mwaminifu
Pacifique|pacifica|fr|-|peaceful|paisible|w'amahoro|mwenye amani
Espérance|esperanza|fr|-|hope|espoir|ibyiringiro|tumaini
Providence|providence|fr|W|divine care, foresight|soin divin, prévoyance|ubwitange bw'Imana|utunzaji wa Mungu
Prosper|prospere|fr|W|fortunate, successful|prospère, chanceux|utera imbere|mwenye mafanikio
Désiré|desire,desiree,desire|fr|W|desired, wished-for|désiré|wifujwe|aliyetamaniwa
Théogène|theogene|fr|-|born of God|né de Dieu|wavutse ku Mana|aliyezaliwa na Mungu
Immaculée|immaculate|fr|-|spotless, without stain|sans tache|utagira ikizinga|asiye na doa
Ange|angel,angelique,angelina|gr|-|angel, messenger|ange, messager|umumalayika, intumwa|malaika, mjumbe
Béatrice|beatrix,beata|la|-|she who brings happiness (blessed)|celle qui rend heureux (bénie)|uzana ibyishimo (uhiriwe)|mleta furaha (mbarikiwa)
Aline|adeline,alina|ge|-|noble|noble|umunyacyubahiro|mtukufu
Diane|diana,dianne|la|-|divine (from the Roman goddess Diana)|divine (de la déesse romaine Diane)|w'ubumana (ukomoka ku mana y'Abaroma Diana)|wa kimungu (kutoka mungu wa kike wa Kirumi Diana)
Christine|christina,kristina,kristine,tina|gr|-|follower of Christ|disciple du Christ|umukristo|mfuasi wa Kristo
Bernard|bernardo,bernadette,benard|ge|-|brave as a bear|courageux comme un ours|intwari nk'idubu|jasiri kama dubu
Alphonse|alfonso,alphonsine,alfons|ge|-|noble and ready|noble et prêt|umunyacyubahiro witeguye|mtukufu aliye tayari
Eric|erik,erick,erica,eriki|on|-|eternal ruler|souverain éternel|umutegetsi ubaho iteka|mtawala wa milele
William|guillaume,willem,wilhelm,willy|ge|-|resolute protector|protecteur résolu|umurinzi udacika intege|mlinzi shupavu
Robert|robert,roberto,roberta,rob|ge|-|bright fame|gloire éclatante|icyamamare cyaka|sifa angavu
Richard|ricardo,richie,ricky|ge|-|brave ruler|souverain courageux|umutegetsi w'intwari|mtawala jasiri
Henry|henri,enrique,harry,heinrich,henrik|ge|-|ruler of the home|souverain du foyer|umutegetsi w'urugo|mtawala wa nyumbani
Charles|charlie,carlos,karl,carl,charlotte,carol|ge|-|free man|homme libre|umuntu w'ubuntu (utari imbata)|mtu huru
Edward|edouard,eduardo,ed,eddie|ge|-|wealthy guardian|gardien riche|umurinzi ukize|mlinzi tajiri
Emma|ema,emma|ge|-|whole, universal|entière, universelle|yuzuye, rusange|kamili, ya ulimwengu
Jennifer|jenny,jenifer,jenna|ce|-|fair one, white wave|la belle, vague blanche|nziza, umuhengeri w'umweru|mrembo, wimbi jeupe
Michelle|michele,micheline|he|-|who is like God? (feminine of Michael)|qui est comme Dieu ? (féminin de Michel)|ni nde uhwanye n'Imana? (igitsina gore cya Michael)|ni nani aliye kama Mungu? (kike cha Michael)
Brian|bryan,brien|ce|-|high, noble|élevé, noble|ukomeye, w'icyubahiro|mkuu, mtukufu
Kevin|kevin,keven|ce|-|kind, gentle, handsome|doux, bienveillant, beau|wuje urukundo, mwiza|mpole, mzuri
Dennis|denis,dennys,dionysius|gr|-|follower of Dionysus (the Greek god of wine)|disciple de Dionysos (dieu grec du vin)|umukurikiye Dionysus (imana y'inzoga y'Abagereki)|mfuasi wa Dionysus (mungu wa divai wa Kigiriki)
Rose|rosa,rosine,rosette,rosemary|en|W|rose (the flower)|rose (la fleur)|roza (ururabo)|waridi (ua)
Lily|lilly,lili,lilian,liliane|en|W|lily (the flower, a symbol of purity)|lys (la fleur, symbole de pureté)|lily (ururabo, ikimenyetso cy'ubuziranenge)|yungiyungi (ua, ishara ya usafi)
Daisy|daisi|en|W|day's eye (a small white flower)|œil du jour (petite fleur blanche)|ijisho ry'umunsi (ururabo ruto rwera)|jicho la siku (ua dogo jeupe)
Grace|gracia,gracie,gratia|en|W|God's favour, kindness|faveur de Dieu, bonté|ubuntu bw'Imana, ubugwaneza|neema ya Mungu, wema
Faith|foi,fe|en|W|trust, belief|confiance, croyance|kwizera|imani
Hope|hope|en|W|hope, expectation|espoir, attente|ibyiringiro|matumaini
Joy|joie,joyce|en|W|joy, delight|joie, plaisir|ibyishimo|furaha
Blessing|benediction,blessings|en|W|blessing, divine favour|bénédiction, faveur divine|umugisha|baraka
Gift|gifty|en|W|gift, present|don, cadeau|impano|zawadi
Precious|precieuse|en|W|precious, valuable|précieux (précieuse)|igiciro gihanitse, w'agaciro|thamani, mpendwa
Patience|patience|en|W|patience, endurance|patience, endurance|kwihangana|subira, uvumilivu
Peace|paix|en|W|peace, calm|paix, calme|amahoro|amani
Sandra|alexandra,sandrine,sandy|gr|-|defender of men (short for Alexandra)|défenseur des hommes (forme courte d'Alexandra)|umurinzi w'abantu (impfunyapfunyo ya Alexandra)|mlinzi wa watu (kifupi cha Alexandra)
Linda|lynda,belinda|ge|-|beautiful (Spanish/Portuguese), also "gentle" in Germanic names|belle (espagnol/portugais), aussi « douce » en germanique|nziza (mu cyesipanyoli/igiporutigali)|mrembo (Kihispania/Kireno)
Amina|aminah,amine,aminata|ar|-|trustworthy, faithful|digne de confiance, fidèle|wizerwa|mwaminifu
Fatima|fatma,fatuma,fatou,fatimah|ar|-|captivating (also "one who abstains")|captivante (aussi « celle qui s'abstient »)|ukurura (kandi «wirinda»)|mvutiaji (pia «anayejizuia»)
Hassan|hasan,hasani|ar|-|good, handsome|bon, beau|mwiza, w'agaciro|mzuri, mwema
Hussein|husein,hussain,husseini,husayn|ar|-|little good one (diminutive of Hassan)|petit bon (diminutif de Hassan)|muto mwiza (ikiyongera cya Hassan)|mdogo mwema (kidogo cha Hassan)
Omar|umar,omari|ar|-|long-lived, flourishing|qui vit longtemps, florissant|uramba, utera imbere|mwenye maisha marefu, anayestawi
Ali|aly,ali|ar|-|high, exalted|élevé, sublime|waruhutse, ushyizwe hejuru|aliyetukuka, juu
Ahmed|ahmad,ahmadi,hamidi|ar|-|most praised|le plus loué|ushimwa cyane|mwenye kusifiwa zaidi
Muhammad|mohammed,mohamed,muhammed,mohamad,mohammad|ar|-|praiseworthy, much praised|digne de louanges|ukwiye gushimwa|anayestahili kusifiwa
Ibrahim|ibrahima,ibraheem|ar|-|father of many (Arabic form of Abraham)|père d'une multitude (forme arabe d'Abraham)|se w'abatari bake (inyito y'Icyarabu ya Abraham)|baba wa wengi (umbo la Kiarabu la Abraham)
Yusuf|yusufu,youssef,yousuf,yussuf|ar|-|he will add (Arabic form of Joseph)|il ajoutera (forme arabe de Joseph)|azongera (inyito y'Icyarabu ya Joseph)|ataongeza (umbo la Kiarabu la Joseph)
Aisha|aicha,aysha,ayesha,aishah|ar|-|alive, living|vivante|ubaho|aliye hai
Zainab|zaynab,zeinab,zeynab,zainabu|ar|-|fragrant tree (also "ornament of the father")|arbre parfumé (aussi « parure du père »)|igiti gihumura (kandi «umurimbo wa se»)|mti wenye harufu nzuri (pia «pambo la baba»)
Khadija|khadija,khadijah,hadija,hadija,khadidja|ar|-|early baby, born prematurely|enfant née avant terme|umwana wavutse imburagihe|mtoto aliyezaliwa kabla ya wakati
Salim|salima,salma,selim,salimu|ar|-|safe, sound, peaceful|sain et sauf, paisible|wabungabunzwe, w'amahoro|salama, mwenye amani
Karim|kareem,karima|ar|-|generous|généreux|utanga|mkarimu
Rashid|rashidi,rachid,rasheed|ar|-|rightly guided|bien guidé|uyobowe neza|aliyeongozwa vyema
Samira|samir,sameera|ar|-|companion in evening conversation|compagnon (compagne) des conversations du soir|mugenzi w'ibiganiro by'ijoro|mwenza wa mazungumzo ya jioni
Layla|laila,leila,leyla,lailah|ar|-|night|nuit|ijoro|usiku
Jamal|jamil,jamila,jamilah|ar|-|beauty|beauté|ubwiza|uzuri
Hamza|hamzah,hamisi|ar|-|lion, strong|lion, fort|intare, ukomeye|simba, mwenye nguvu
Said|saidi,saeed,sa'id,saidy|ar|W|happy, fortunate|heureux, chanceux|wishimye, ufite amahirwe|mwenye furaha, bahati
Juma|jumaa,jumanne,juma|sw|-|born on Friday|né un vendredi|wavutse ku wa gatanu|aliyezaliwa Ijumaa
Baraka|barak,barack|sw|-|blessing|bénédiction|umugisha|baraka
Zawadi|zawadi|sw|-|gift|cadeau|impano|zawadi
Upendo|upendo|sw|-|love|amour|urukundo|upendo
Furaha|furaha|sw|-|joy, happiness|joie, bonheur|ibyishimo|furaha
Neema|neema|sw|-|grace, favour|grâce, faveur|ubuntu, igikundiro|neema
Tumaini|tumaini|sw|-|hope|espoir|ibyiringiro|tumaini
Imani|imani|sw|-|faith|foi|kwizera|imani
Zuri|zuri|sw|-|beautiful|beau (belle)|nziza|mzuri
Jabari|jabari|sw|-|brave, valiant|brave, vaillant|intwari|jasiri
Rehema|rehema,rahma,rahima|sw|-|mercy, compassion|miséricorde, compassion|imbabazi|rehema, huruma
Subira|subira|sw|-|patience|patience|kwihangana|subira, uvumilivu
Asha|asha,aisha|sw|-|life (also "hope" in some traditions)|vie (aussi « espoir » dans certaines traditions)|ubuzima|uhai
Kamau|kamau|ki|-|quiet warrior|guerrier discret|intwari ituje|shujaa mtulivu
Kwame|kwame|ak|-|born on Saturday (male)|né un samedi (garçon)|wavutse ku wa gatandatu (umuhungu)|aliyezaliwa Jumamosi (mwanaume)
Kofi|kofi|ak|-|born on Friday (male)|né un vendredi (garçon)|wavutse ku wa gatanu (umuhungu)|aliyezaliwa Ijumaa (mwanaume)
Ama|ama|ak|-|born on Saturday (female)|née un samedi (fille)|wavutse ku wa gatandatu (umukobwa)|aliyezaliwa Jumamosi (mwanamke)
Kojo|kojo|ak|-|born on Monday (male)|né un lundi (garçon)|wavutse ku wa mbere (umuhungu)|aliyezaliwa Jumatatu (mwanaume)
Abena|abena|ak|-|born on Tuesday (female)|née un mardi (fille)|wavutse ku wa kabiri (umukobwa)|aliyezaliwa Jumanne (mwanamke)
Chinedu|chinedu|ig|-|God leads|Dieu guide|Imana iyobora|Mungu huongoza
Chidi|chidi|ig|-|God exists|Dieu existe|Imana ibaho|Mungu yupo
Chioma|chioma|ig|-|God is good|Dieu est bon|Imana ni nziza|Mungu ni mwema
Ifeanyi|ifeanyi|ig|-|nothing is impossible for God|rien n'est impossible à Dieu|nta kidashoboka ku Mana|hakuna lisilowezekana kwa Mungu
Emeka|emeka|ig|-|great deeds (God has done great things)|grandes œuvres (Dieu a fait de grandes choses)|ibikorwa bikomeye|matendo makuu
Ayo|ayo|yo|-|joy|joie|ibyishimo|furaha
Tunde|tunde,babatunde|yo|-|returns (the father has returned)|revient (le père est revenu)|agarutse|amerudi
Ayodele|ayodele|yo|-|joy has come home|la joie est rentrée à la maison|ibyishimo byageze mu rugo|furaha imerudi nyumbani
Thabo|thabo|zu|-|joy|joie|ibyishimo|furaha
Sipho|sipho|zu|-|gift|don, cadeau|impano|zawadi
Themba|themba|zu|-|hope, trust|espoir, confiance|ibyiringiro, kwizera|tumaini, imani
Lindiwe|lindiwe|zu|-|the awaited one|celle (celui) qu'on attendait|uwategerejwe|aliyengojewa
Thandi|thandi|zu|-|loved one|bien-aimé(e)|ukundwa|mpendwa
Priya|priya|sa|-|beloved, dear|bien-aimé(e), cher (chère)|ukundwa|mpendwa
Raj|raj,raja|sa|-|king, ruler|roi, souverain|umwami|mfalme
Anand|anand,ananda|sa|-|joy, bliss|joie, félicité|ibyishimo|furaha
Arjun|arjun,arjuna|sa|-|bright, shining, white|brillant, lumineux, blanc|urabagirana, rwera|angavu, mweupe
Aarav|aarav|sa|-|peaceful, calm|paisible, calme|w'amahoro, utuje|mwenye amani, mtulivu
Ananya|ananya|sa|-|unique, without another|unique, sans pareil|udasanzwe, wihariye|wa pekee
Regis|Régis|la|-|of the king (Latin rex = king)|du roi (latin rex = roi)|uw'umwami (Ikilatini rex = umwami)|wa mfalme (Kilatini rex = mfalme)
Sakura|sakura|ja|-|cherry blossom|fleur de cerisier|ururabo rw'igiti cya cherry|ua la mcheri
Yuki|yuki|ja|-|snow (also "happiness" depending on the characters)|neige (aussi « bonheur » selon les caractères)|urubura (rimwe na rimwe «ibyishimo»)|theluji (pia «furaha» kulingana na herufi)
""".strip()

_NAMES = []       # list of dicts
_INDEX = {}       # folded token -> list of name dicts


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "")).replace("’", "'").replace("‘", "'")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]+", " ", s)).strip()


def _load():
    for line in _TABLE.splitlines():
        p = line.split("|")
        if len(p) != 8:
            raise ValueError("bad names row: " + line[:40])
        name, alias, org, word, *mean = p
        d = {"name": name, "aliases": [] if alias == "-" else alias.split(","), "origin": org,
             "word": word == "W", "meaning": dict(zip(LANGS, mean))}
        _NAMES.append(d)
        for key in {fold(name), *[fold(a) for a in d["aliases"]]}:
            if key:
                _INDEX.setdefault(key, []).append(d)


_load()
COUNT = len(_NAMES)

STRICT_CUES = {"name", "names", "izina", "amazina", "by'izina", "y'izina", "ry'izina", "prenom", "prenoms", "nom", "jina", "majina"}
_MEANING_WORDS = {"ibisobanuro", "meaning", "mean", "means", "meant", "origin", "origins", "risobanura", "bisobanura", "bisobanuro", "signification",
                  "signifie", "signifient", "origine", "maana", "inamaanisha", "unamaanisha", "asili", "kimaanishi"}


def _tokens(q):
    return fold(q).split()


def _has_cue(tokens, strict):
    ts = set(tokens)
    if ts & STRICT_CUES:
        return True
    return (not strict) and bool(ts & _MEANING_WORDS)


def find(question, lang="en", max_names=3):
    """Return a guide-shaped entry for the question, or None.

    Rules (to avoid hijacking ordinary questions):
      * a known name AND a cue word ("name", "meaning", "izina", "signification", "maana"...) -> answer;
      * names that are also ordinary words (Grace, Hope, Joy, Rose...) need the word "name"/"izina"/"prénom"/"jina" itself;
      * a message that is only a name (1-2 words), e.g. "Aline" -> answer.
    """
    q = (question or "").strip()
    if not q or len(q) > 200:
        return None
    toks = _tokens(q)
    if not toks:
        return None
    found = []
    seen = set()
    for t in toks:
        for d in _INDEX.get(t, []):
            if d["name"] not in seen:
                seen.add(d["name"]); found.append(d)
    if not found:
        return None
    bare = len(toks) <= 2 and all(t in _INDEX for t in toks)
    ok = []
    for d in found:
        if bare and not d["word"]:
            ok.append(d)
        elif _has_cue(toks, strict=d["word"]):
            ok.append(d)
    if not ok:
        return None
    return build_entry(ok[:max_names], lang)


_TEMPLATES = {
    "en": ("**{name}** is {a} {origin} name meaning “{m}”.", "About this name", "Origin: {origin}.",
           "Name meanings can vary by culture and family, and many names have more than one explanation; spellings also vary.",
           "The name {name}", "Names"),
    "fr": ("**{name}** est un prénom d'origine {origin} qui signifie « {m} ».", "À propos de ce nom", "Origine : {origin}.",
           "Le sens d'un nom peut varier selon la culture et la famille, et beaucoup de noms ont plusieurs explications ; l'orthographe varie aussi.",
           "Le nom {name}", "Noms"),
    "rw": ("**{name}** ni izina rifite inkomoko: {origin}. Risobanura «{m}».", "Ibyerekeye iri zina", "Inkomoko: {origin}.",
           "Ibisobanuro by'amazina bishobora gutandukana hakurikijwe umuco n'umuryango, kandi amazina menshi afite ibisobanuro birenze kimwe; imyandikire na yo iratandukana.",
           "Izina {name}", "Amazina"),
    "sw": ("**{name}** ni jina lenye asili ya {origin} linalomaanisha «{m}».", "Kuhusu jina hili", "Asili: {origin}.",
           "Maana za majina zinaweza kutofautiana kulingana na utamaduni na familia, na majina mengi yana maelezo zaidi ya moja; tahajia pia hutofautiana.",
           "Jina {name}", "Majina"),
}


def build_entry(items, lang="en"):
    """Guide-shaped dict: title/answer/steps/related per language, plus a per-language steps label."""
    entry = {"id": "name_meaning", "related": [], "kind": "name", "names": [d["name"] for d in items],
             "title": {}, "answer": {}, "steps": {}, "steps_label": {}}
    for i, l in enumerate(LANGS):
        tpl, label, org_tpl, note, title_tpl, title_many = _TEMPLATES[l]
        answers, steps = [], []
        for d in items:
            og = ORIGIN[d["origin"]][i]
            answers.append(tpl.format(name=d["name"], origin=og, m=d["meaning"][l], a=("an" if og[:1] in "AEIOU" else "a")))
            steps.append(org_tpl.format(origin=og) if len(items) == 1 else f"{d['name']}: " + org_tpl.format(origin=og))
        if len(items[0]["aliases"]) and len(items) == 1:
            steps.append({"en": "Also written: ", "fr": "S'écrit aussi : ", "rw": "Yandikwa kandi: ", "sw": "Pia huandikwa: "}[l]
                         + ", ".join(a.capitalize() for a in items[0]["aliases"][:6]))
        steps.append(note)
        entry["answer"][l] = "\n\n".join(answers)
        entry["steps"][l] = steps
        entry["steps_label"][l] = label
        entry["title"][l] = title_tpl.format(name=items[0]["name"]) if len(items) == 1 else title_many + ": " + ", ".join(d["name"] for d in items)
    return entry
