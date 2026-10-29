"""Practice questions for the Personal AI tutor. Every question has a correct answer, an explanation (why), and a note on the usual mistake (slip),
in English, French, Kinyarwanda and Kiswahili. `opts` is one list (shared by every language: numbers, symbols, names) or a {lang: list} dict.
`ans` is the index of the correct option. fr/rw/sw wording is a draft for fluent review; the facts and numbers are standard textbook values."""
LANGS = ("en", "fr", "rw", "sw")
TOPICS = {
    "math": {"en": "Mathematics", "fr": "Mathématiques", "rw": "Imibare", "sw": "Hisabati"},
    "physics": {"en": "Physics", "fr": "Physique", "rw": "Ubugenge (Physics)", "sw": "Fizikia"},
    "science": {"en": "General science", "fr": "Sciences générales", "rw": "Siyansi rusange", "sw": "Sayansi ya jumla"},
    "cybersecurity": {"en": "Cybersecurity", "fr": "Cybersécurité", "rw": "Umutekano w'ikoranabuhanga (Cybersecurity)", "sw": "Usalama wa mtandao (Cybersecurity)"},
    "networks": {"en": "Networks", "fr": "Réseaux", "rw": "Imiyoboro (Networks)", "sw": "Mitandao (Networks)"},
    "cyber": {"en": "Digital safety", "fr": "Sécurité numérique", "rw": "Umutekano wa digitale", "sw": "Usalama wa kidijitali"},
    "world": {"en": "World knowledge", "fr": "Culture générale", "rw": "Ubumenyi rusange", "sw": "Maarifa ya jumla"},
}


def Q(topic, q, opts, ans, why, slip):
    return dict(topic=topic, q=dict(zip(LANGS, q)), opts=opts, ans=ans, why=dict(zip(LANGS, why)), slip=dict(zip(LANGS, slip)))


QUESTIONS = [
    Q("math", ("What is 15% of 240?", "Combien font 15 % de 240 ?", "15% ya 240 ni angahe?", "Asilimia 15 ya 240 ni ngapi?"),
      ["24", "36", "48", "15"], 1,
      ("10% of 240 is 24 and 5% is half of that, 12. So 15% = 24 + 12 = 36 (or 240 × 15 ÷ 100).", "10 % de 240 font 24 et 5 % en font la moitié, 12. Donc 15 % = 24 + 12 = 36 (ou 240 × 15 ÷ 100).", "10% ya 240 ni 24, naho 5% ni kimwe cya kabiri cyayo, 12. Rero 15% = 24 + 12 = 36 (cyangwa 240 × 15 ÷ 100).", "10% ya 240 ni 24 na 5% ni nusu yake, 12. Kwa hiyo 15% = 24 + 12 = 36 (au 240 × 15 ÷ 100)."),
      ("24 is only 10%. Remember to add the missing 5%.", "24 correspond seulement à 10 %. Il faut ajouter les 5 % restants.", "24 ni 10% gusa. Wibuke kongeraho 5% isigaye.", "24 ni 10% tu. Kumbuka kuongeza 5% iliyobaki.")),
    Q("math", ("Solve: 2x + 3 = 11", "Résolvez : 2x + 3 = 11", "Kemura: 2x + 3 = 11", "Tatua: 2x + 3 = 11"),
      ["x = 3", "x = 4", "x = 7", "x = 5.5"], 1,
      ("Subtract 3 from both sides: 2x = 8. Divide both sides by 2: x = 4. Check: 2×4 + 3 = 11.", "Soustrayez 3 des deux côtés : 2x = 8. Divisez par 2 : x = 4. Vérification : 2×4 + 3 = 11.", "Kuramo 3 ku mpande zombi: 2x = 8. Gabanya byombi na 2: x = 4. Igenzura: 2×4 + 3 = 11.", "Toa 3 pande zote mbili: 2x = 8. Gawanya kwa 2: x = 4. Hakiki: 2×4 + 3 = 11."),
      ("x = 7 comes from adding 3 instead of subtracting it; 5.5 comes from dividing 11 by 2 and forgetting the +3.", "x = 7 vient d'une addition de 3 au lieu d'une soustraction ; 5,5 vient de 11 ÷ 2 en oubliant le +3.", "x = 7 iva mu kongeraho 3 aho kuyikuramo; 5.5 iva mu kugabanya 11 na 2 wibagiwe +3.", "x = 7 hutokana na kuongeza 3 badala ya kutoa; 5.5 hutokana na kugawanya 11 kwa 2 ukisahau +3.")),
    Q("math", ("What is 6 + 4 × 3?", "Combien font 6 + 4 × 3 ?", "6 + 4 × 3 ni angahe?", "6 + 4 × 3 ni ngapi?"),
      ["30", "18", "24", "13"], 1,
      ("Multiplication comes before addition: 4 × 3 = 12, then 6 + 12 = 18.", "La multiplication passe avant l'addition : 4 × 3 = 12, puis 6 + 12 = 18.", "Gukuba biza mbere yo guteranya: 4 × 3 = 12, hanyuma 6 + 12 = 18.", "Kuzidisha kunatangulia kujumlisha: 4 × 3 = 12, kisha 6 + 12 = 18."),
      ("30 comes from working left to right (6 + 4 = 10, then × 3).", "30 vient d'un calcul de gauche à droite (6 + 4 = 10, puis × 3).", "30 iva mu kubara uva ibumoso ujya iburyo (6 + 4 = 10, hanyuma × 3).", "30 hutokana na kuhesabu kutoka kushoto kwenda kulia (6 + 4 = 10, kisha × 3).")),
    Q("math", ("The area of a rectangle 8 m long and 5 m wide is:", "L'aire d'un rectangle de 8 m de long et 5 m de large est :", "Ubuso bw'urukiramende rufite uburebure bwa m 8 n'ubugari bwa m 5 ni:", "Eneo la mstatili wenye urefu wa m 8 na upana wa m 5 ni:"),
      ["13 m²", "26 m", "40 m²", "40 m"], 2,
      ("Area = length × width = 8 × 5 = 40, and area is measured in square metres (m²).", "Aire = longueur × largeur = 8 × 5 = 40, en mètres carrés (m²).", "Ubuso = uburebure × ubugari = 8 × 5 = 40, bupimwa muri metero kare (m²).", "Eneo = urefu × upana = 8 × 5 = 40, hupimwa kwa mita za mraba (m²)."),
      ("26 m is the perimeter 2 × (8 + 5), a length not an area; 13 is only 8 + 5.", "26 m est le périmètre 2 × (8 + 5), une longueur et non une aire ; 13 n'est que 8 + 5.", "26 m ni impande zose 2 × (8 + 5), ni uburebure si ubuso; 13 ni 8 + 5 gusa.", "26 m ni mzunguko 2 × (8 + 5), urefu si eneo; 13 ni 8 + 5 tu.")),
    Q("math", ("3/4 + 1/4 = ?", "3/4 + 1/4 = ?", "3/4 + 1/4 = ?", "3/4 + 1/4 = ?"),
      ["4/8", "1", "3/16", "1/2"], 1,
      ("The denominators are equal, so add only the numerators: 3 + 1 = 4, giving 4/4 = 1.", "Les dénominateurs sont égaux : on n'additionne que les numérateurs, 3 + 1 = 4, donc 4/4 = 1.", "Ibice byo hasi ni bimwe, rero uteranya hejuru gusa: 3 + 1 = 4, bivamo 4/4 = 1.", "Vipande vya chini ni sawa, kwa hiyo jumlisha juu tu: 3 + 1 = 4, hivyo 4/4 = 1."),
      ("4/8 comes from adding the denominators too (4 + 4).", "4/8 vient d'une addition des dénominateurs aussi (4 + 4).", "4/8 iva mu guteranya n'ibice byo hasi (4 + 4).", "4/8 hutokana na kujumlisha pia vipande vya chini (4 + 4).")),
    Q("math", ("What is the average (mean) of 4, 8 and 12?", "Quelle est la moyenne de 4, 8 et 12 ?", "Impuzandengo ya 4, 8 na 12 ni iyihe?", "Wastani wa 4, 8 na 12 ni upi?"),
      ["6", "8", "9", "24"], 1,
      ("Add them (4 + 8 + 12 = 24) and divide by how many numbers there are (3): 24 ÷ 3 = 8.", "Additionnez (4 + 8 + 12 = 24) puis divisez par le nombre de valeurs (3) : 24 ÷ 3 = 8.", "Bateranye (4 + 8 + 12 = 24) ugabanye n'umubare wazo (3): 24 ÷ 3 = 8.", "Jumlisha (4 + 8 + 12 = 24) kisha gawanya kwa idadi ya namba (3): 24 ÷ 3 = 8."),
      ("24 is the total; the mean needs the division by 3.", "24 est le total ; la moyenne demande la division par 3.", "24 ni igiteranyo; impuzandengo ikenera kugabanya na 3.", "24 ni jumla; wastani unahitaji kugawanya kwa 3.")),
    Q("physics", ("What is the SI unit of force?", "Quelle est l'unité SI de la force ?", "Igipimo mpuzamahanga (SI) cy'imbaraga ni iki?", "Kipimo cha SI cha nguvu ni kipi?"),
      {"en": ["Joule", "Newton", "Watt", "Pascal"], "fr": ["Joule", "Newton", "Watt", "Pascal"], "rw": ["Joule", "Newton", "Watt", "Pascal"], "sw": ["Joule", "Newton", "Watt", "Pascal"]}, 1,
      ("Force is measured in newtons (N), from F = m × a, so 1 N = 1 kg·m/s².", "La force se mesure en newtons (N), d'après F = m × a, donc 1 N = 1 kg·m/s².", "Imbaraga zipimirwa muri newton (N), hakurikijwe F = m × a, bityo 1 N = 1 kg·m/s².", "Nguvu hupimwa kwa newton (N), kutoka F = m × a, hivyo 1 N = 1 kg·m/s²."),
      ("Joule is energy, watt is power, pascal is pressure.", "Le joule mesure l'énergie, le watt la puissance, le pascal la pression.", "Joule ni ingufu, watt ni ingufu mu gihe (power), pascal ni igitutu.", "Joule ni nishati, watt ni nguvu ya umeme (power), pascal ni shinikizo.")),
    Q("physics", ("A car travels 120 km in 2 hours at a steady speed. What is the speed?", "Une voiture parcourt 120 km en 2 heures à vitesse constante. Quelle est sa vitesse ?", "Imodoka ikora km 120 mu masaha 2 ku muvuduko uhoraho. Umuvuduko wayo ni uwuhe?", "Gari husafiri km 120 kwa saa 2 kwa kasi isiyobadilika. Kasi ni ipi?"),
      ["60 km/h", "240 km/h", "118 km/h", "122 km/h"], 0,
      ("Speed = distance ÷ time = 120 ÷ 2 = 60 km/h.", "Vitesse = distance ÷ temps = 120 ÷ 2 = 60 km/h.", "Umuvuduko = urugendo ÷ igihe = 120 ÷ 2 = 60 km/h.", "Kasi = umbali ÷ muda = 120 ÷ 2 = 60 km/h."),
      ("240 comes from multiplying instead of dividing.", "240 vient d'une multiplication au lieu d'une division.", "240 iva mu kugwiza aho kugabanya.", "240 hutokana na kuzidisha badala ya kugawanya.")),
    Q("physics", ("Ohm's law says that voltage V equals:", "La loi d'Ohm dit que la tension V est égale à :", "Itegeko rya Ohm rivuga ko voltage V ingana na:", "Sheria ya Ohm inasema voltage V ni sawa na:"),
      ["I ÷ R", "I × R", "R ÷ I", "I + R"], 1,
      ("V = I × R: voltage (volts) equals current (amperes) times resistance (ohms).", "V = I × R : la tension (volts) est le courant (ampères) multiplié par la résistance (ohms).", "V = I × R: voltage (volt) ingana n'umuyaga w'amashanyarazi (ampere) wikubye n'ukurwanya (ohm).", "V = I × R: voltage (volti) ni sawa na mkondo (ampea) mara upinzani (ohmu)."),
      ("I ÷ R is not a voltage; if you need I, then I = V ÷ R.", "I ÷ R n'est pas une tension ; pour trouver I, I = V ÷ R.", "I ÷ R si voltage; ushaka I, I = V ÷ R.", "I ÷ R si voltage; ukitaka I, I = V ÷ R.")),
    Q("physics", ("Near Earth's surface, the acceleration due to gravity is about:", "Près de la surface de la Terre, l'accélération de la pesanteur vaut environ :", "Hafi y'ubuso bw'isi, kwihuta kubera uburemere ni hafi ya:", "Karibu na uso wa Dunia, kasi ya mvutano ni takriban:"),
      ["9.8 m/s²", "98 m/s²", "0.98 m/s²", "3.0 × 10⁸ m/s"], 0,
      ("g ≈ 9.8 m/s² (often rounded to 10 m/s² for quick work).", "g ≈ 9,8 m/s² (souvent arrondi à 10 m/s² pour aller vite).", "g ≈ 9.8 m/s² (akenshi bashyira kuri 10 m/s² mu mibare yihuse).", "g ≈ 9.8 m/s² (mara nyingi hukadiriwa 10 m/s² kwa haraka)."),
      ("3.0 × 10⁸ m/s is the speed of light, a different quantity.", "3,0 × 10⁸ m/s est la vitesse de la lumière, une autre grandeur.", "3.0 × 10⁸ m/s ni umuvuduko w'urumuri, ni ikindi kintu.", "3.0 × 10⁸ m/s ni kasi ya mwanga, kiasi tofauti.")),
    Q("physics", ("What is the kinetic energy of a 2 kg object moving at 3 m/s?", "Quelle est l'énergie cinétique d'un objet de 2 kg se déplaçant à 3 m/s ?", "Ingufu zo kugenda (kinetic energy) z'igikoresho cya kg 2 kigenda kuri m/s 3 ni izihe?", "Nishati ya mwendo ya kitu cha kg 2 kinachosogea kwa m/s 3 ni ipi?"),
      ["6 J", "9 J", "18 J", "3 J"], 1,
      ("KE = ½ m v² = ½ × 2 × 3² = ½ × 2 × 9 = 9 J.", "Ec = ½ m v² = ½ × 2 × 3² = ½ × 2 × 9 = 9 J.", "KE = ½ m v² = ½ × 2 × 3² = ½ × 2 × 9 = 9 J.", "KE = ½ m v² = ½ × 2 × 3² = ½ × 2 × 9 = 9 J."),
      ("18 J forgets the ½; 6 J multiplies m × v instead of squaring v.", "18 J oublie le ½ ; 6 J fait m × v au lieu de mettre v au carré.", "18 J wibagiwe ½; 6 J ni m × v aho gukuba v kabiri.", "18 J umesahau ½; 6 J ni m × v badala ya kupiga v mraba.")),
    Q("physics", ("The speed of light in a vacuum is about:", "La vitesse de la lumière dans le vide est d'environ :", "Umuvuduko w'urumuri mu cyuho ni hafi ya:", "Kasi ya mwanga katika ombwe ni takriban:"),
      ["3 × 10⁸ m/s", "3 × 10⁶ m/s", "340 m/s", "3 × 10⁴ m/s"], 0,
      ("c ≈ 3 × 10⁸ m/s (299 792 458 m/s exactly).", "c ≈ 3 × 10⁸ m/s (299 792 458 m/s exactement).", "c ≈ 3 × 10⁸ m/s (299 792 458 m/s nyabyo).", "c ≈ 3 × 10⁸ m/s (hasa 299 792 458 m/s)."),
      ("340 m/s is roughly the speed of sound in air.", "340 m/s est à peu près la vitesse du son dans l'air.", "340 m/s ni hafi y'umuvuduko w'ijwi mu kirere.", "340 m/s ni takriban kasi ya sauti hewani.")),
    Q("science", ("Plants take in which gas for photosynthesis?", "Quel gaz les plantes absorbent-elles pour la photosynthèse ?", "Ibimera bifata iyihe gaze mu gukora ifoto-sintezi?", "Mimea huchukua gesi gani kwa usanisinuru?"),
      {"en": ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"], "fr": ["Dioxyde de carbone", "Oxygène", "Azote", "Hydrogène"], "rw": ["Dioxyde de carbone (CO₂)", "Oxygène (umwuka wa ogisijene)", "Azote", "Hydrogène"], "sw": ["Kaboni dayoksaidi", "Oksijeni", "Naitrojeni", "Haidrojeni"]}, 0,
      ("Plants use sunlight, water and carbon dioxide to make sugar, and release oxygen.", "Les plantes utilisent la lumière, l'eau et le dioxyde de carbone pour fabriquer du sucre et rejettent de l'oxygène.", "Ibimera bikoresha izuba, amazi na dioxyde de carbone bigakora isukari, bigasohora ogisijene.", "Mimea hutumia mwanga wa jua, maji na kaboni dayoksaidi kutengeneza sukari na hutoa oksijeni."),
      ("Oxygen is what plants release, not what they take in for making sugar.", "L'oxygène est ce que les plantes rejettent, pas ce qu'elles absorbent pour fabriquer le sucre.", "Ogisijene ni yo bisohora, si iyo bifata mu gukora isukari.", "Oksijeni ndiyo mimea hutoa, si inayochukua kutengeneza sukari.")),
    Q("science", ("What is the chemical formula of water?", "Quelle est la formule chimique de l'eau ?", "Formule ya shimi y'amazi ni iyihe?", "Fomula ya kemikali ya maji ni ipi?"),
      ["H₂O", "CO₂", "O₂", "NaCl"], 0,
      ("Each water molecule has 2 hydrogen atoms and 1 oxygen atom: H₂O.", "Chaque molécule d'eau a 2 atomes d'hydrogène et 1 atome d'oxygène : H₂O.", "Buri ngingo y'amazi ifite atome 2 za hydrogène n'imwe ya oxygène: H₂O.", "Kila molekuli ya maji ina atomi 2 za haidrojeni na 1 ya oksijeni: H₂O."),
      ("CO₂ is carbon dioxide, O₂ is oxygen gas and NaCl is table salt.", "CO₂ est le dioxyde de carbone, O₂ le dioxygène et NaCl le sel de table.", "CO₂ ni dioxyde de carbone, O₂ ni ogisijene n'NaCl ni umunyu.", "CO₂ ni kaboni dayoksaidi, O₂ ni oksijeni na NaCl ni chumvi ya mezani.")),
    Q("science", ("Pure water boils at sea level at:", "L'eau pure bout au niveau de la mer à :", "Amazi meza abira ku nyanja kuri:", "Maji safi huchemka usawa wa bahari kwa:"),
      ["100 °C", "90 °C", "212 °C", "0 °C"], 0,
      ("At standard sea-level pressure pure water boils at 100 °C (which is 212 °F). At altitude it boils at a lower temperature.", "À la pression normale au niveau de la mer, l'eau pure bout à 100 °C (soit 212 °F). En altitude, elle bout à une température plus basse.", "Ku gitutu gisanzwe cy'inyanja amazi meza abira kuri 100 °C (ni 212 °F). Ahantu hirengeye abira ku bushyuhe buto.", "Kwa shinikizo la kawaida la usawa wa bahari maji safi huchemka kwa 100 °C (sawa na 212 °F). Mahali pa juu huchemka kwa joto la chini."),
      ("212 is the same temperature written in °F; 0 °C is where water freezes.", "212 est la même température écrite en °F ; 0 °C est le point de congélation.", "212 ni ubushyuhe bumwe bwanditswe muri °F; 0 °C ni ho amazi akonja.", "212 ni joto hilo hilo kwa °F; 0 °C ndipo maji huganda.")),
    Q("science", ("Which organ pumps blood around the body?", "Quel organe pompe le sang dans le corps ?", "Ni uwuhe mubiri usunika amaraso mu mubiri wose?", "Kiungo gani husukuma damu mwilini?"),
      {"en": ["Heart", "Lungs", "Liver", "Kidneys"], "fr": ["Cœur", "Poumons", "Foie", "Reins"], "rw": ["Umutima", "Ibihaha", "Umwijima", "Impyiko"], "sw": ["Moyo", "Mapafu", "Ini", "Figo"]}, 0,
      ("The heart is a muscle that pumps blood through the blood vessels.", "Le cœur est un muscle qui pompe le sang dans les vaisseaux.", "Umutima ni imitsi isunika amaraso mu miyoboro y'amaraso.", "Moyo ni msuli unaosukuma damu kupitia mishipa ya damu."),
      ("The lungs exchange oxygen and carbon dioxide; the liver and kidneys clean the blood.", "Les poumons échangent l'oxygène et le CO₂ ; le foie et les reins nettoient le sang.", "Ibihaha bihana ogisijene na CO₂; umwijima n'impyiko bisukura amaraso.", "Mapafu hubadilishana oksijeni na kaboni dayoksaidi; ini na figo husafisha damu.")),
    Q("cyber", ("A message says it is from your bank and asks you to reply with your PIN. What is the safest action?", "Un message dit venir de votre banque et demande votre code PIN. Quelle est l'action la plus sûre ?", "Ubutumwa buvuga ko buturutse kuri banki yawe bugasaba PIN yawe. Igikorwa cyizewe ni ikihe?", "Ujumbe unadai ni wa benki yako na unaomba PIN yako. Hatua salama zaidi ni ipi?"),
      {"en": ["Reply quickly with the PIN", "Do not reply; contact the bank through its official app, card or branch", "Reply to ask whether it is real", "Forward it to friends"],
       "fr": ["Répondre vite avec le PIN", "Ne pas répondre ; contacter la banque par son application, sa carte ou son agence officielle", "Répondre pour demander si c'est vrai", "Le transférer à des amis"],
       "rw": ["Gusubiza vuba ushyiramo PIN", "Ntusubize; wivugishe na banki ukoresheje porogaramu yayo, ikarita cyangwa ishami ryayo ryemewe", "Gusubiza ubaza niba ari ukuri", "Kubwohereza inshuti"],
       "sw": ["Jibu haraka kwa PIN", "Usijibu; wasiliana na benki kupitia programu, kadi au tawi lake rasmi", "Jibu kuuliza kama ni kweli", "Tuma kwa marafiki"]}, 1,
      ("A real bank never asks for your PIN by message. Contact them only through a channel you already trust, not the one in the message.", "Une vraie banque ne demande jamais votre PIN par message. Contactez-la seulement par un canal que vous connaissez, pas celui du message.", "Banki nyayo ntiyigera isaba PIN yawe mu butumwa. Yivugishe gusa mu nzira usanzwe wizera, si iyo mu butumwa.", "Benki halisi haiombi PIN kwa ujumbe kamwe. Wasiliana nayo kwa njia unayoiamini tayari, si ile iliyo kwenye ujumbe."),
      ("Replying, even to ask, confirms your number is active and keeps you in the scammer's conversation.", "Répondre, même pour demander, confirme que votre numéro est actif et vous garde dans la conversation de l'escroc.", "Gusubiza, ndetse ubaza, byemeza ko nomero yawe ikora kandi bikugumisha mu kiganiro cy'umutekamutwe.", "Kujibu, hata kuuliza, kunathibitisha namba yako inatumika na kukuweka kwenye mazungumzo ya tapeli.")),
    Q("cyber", ("Which password is the strongest?", "Quel mot de passe est le plus solide ?", "Ijambo ry'ibanga rikomeye kurusha ayandi ni irihe?", "Nywila ipi ni imara zaidi?"),
      ["kigali123", "P@ssw0rd", "blue-tractor-river-lamp-47", "12345678"], 2,
      ("A long passphrase of unrelated words (and unique to this account) is much harder to guess than short clever-looking passwords.", "Une longue phrase de passe de mots sans lien (unique pour ce compte) est bien plus difficile à deviner que des mots de passe courts qui paraissent malins.", "Interuro ndende y'amagambo adafitanye isano (kandi idakoreshwa ahandi) igoye kuyiketsa kurusha amagambo magufi asa n'ayakomeye.", "Nenosiri refu la maneno yasiyohusiana (na la kipekee kwa akaunti hii) ni gumu kukisia kuliko nywila fupi zinazoonekana kuwa na werevu."),
      ("P@ssw0rd looks clever but is on every attacker's list of common patterns.", "P@ssw0rd paraît malin mais figure sur toutes les listes de modèles courants.", "P@ssw0rd igaragara nk'iyakomeye ariko iri ku rutonde rw'ibisanzwe abagizi ba nabi bazi.", "P@ssw0rd inaonekana na werevu lakini iko kwenye orodha ya mifumo ya kawaida ya washambulizi.")),
    Q("cyber", ("What is phishing?", "Qu'est-ce que l'hameçonnage (phishing) ?", "Phishing ni iki?", "Hadaa (phishing) ni nini?"),
      {"en": ["A fake message or site that tricks you into giving private information or money", "A type of computer game", "A way to make a phone faster", "A program that cleans viruses"],
       "fr": ["Un faux message ou site qui vous pousse à donner des informations privées ou de l'argent", "Un type de jeu vidéo", "Une façon d'accélérer un téléphone", "Un programme qui nettoie les virus"],
       "rw": ["Ubutumwa cyangwa urubuga rw'ibinyoma bigushuka ngo utange amakuru bwite cyangwa amafaranga", "Ubwoko bw'umukino wa mudasobwa", "Uburyo bwo kwihutisha telefone", "Porogaramu isukura virusi"],
       "sw": ["Ujumbe au tovuti bandia inayokudanganya utoe taarifa binafsi au pesa", "Aina ya mchezo wa kompyuta", "Njia ya kufanya simu iwe haraka", "Programu inayosafisha virusi"]}, 0,
      ("Phishing imitates a trusted sender (bank, mobile money, employer) to make you click, pay or reveal secrets.", "Le phishing imite un expéditeur de confiance (banque, mobile money, employeur) pour vous faire cliquer, payer ou révéler des secrets.", "Phishing yigana uwo wizeye (banki, mobile money, umukoresha) kugira ngo ukande, wishyure cyangwa utange ibanga.", "Phishing huiga mtumaji unayemwamini (benki, pesa ya simu, mwajiri) ili ubofye, ulipe au utoe siri."),
      ("Phishing is an attack, not a tool; the other options describe harmless or protective things.", "Le phishing est une attaque, pas un outil ; les autres choix décrivent des choses inoffensives ou protectrices.", "Phishing ni igitero, si igikoresho; ibindi ni ibintu bitangiza cyangwa birinda.", "Phishing ni shambulio, si zana; chaguzi nyingine zinaeleza vitu visivyo na madhara au vya kinga.")),
    Q("cyber", ("What does two-factor authentication (2FA) add?", "Qu'ajoute l'authentification à deux facteurs (2FA) ?", "Kwemeza mu byiciro bibiri (2FA) byongeraho iki?", "Uthibitishaji wa hatua mbili (2FA) unaongeza nini?"),
      {"en": ["A second proof of identity, besides the password", "A faster internet connection", "A longer password", "Free storage"],
       "fr": ["Une seconde preuve d'identité, en plus du mot de passe", "Une connexion internet plus rapide", "Un mot de passe plus long", "Du stockage gratuit"],
       "rw": ["Icyemezo cya kabiri cy'uwo uri we, hiyongereyeho ijambo ry'ibanga", "Interineti yihuta", "Ijambo ry'ibanga rirerire", "Ububiko bw'ubuntu"],
       "sw": ["Uthibitisho wa pili wa utambulisho, mbali na nywila", "Mtandao wa kasi zaidi", "Nywila ndefu zaidi", "Hifadhi ya bure"]}, 0,
      ("Even if someone learns your password, they still need the second factor (such as a code or an app approval). Never share that code with anyone.", "Même si quelqu'un connaît votre mot de passe, il lui faut le second facteur (code, approbation dans une application). Ne partagez jamais ce code.", "Nubwo umuntu yamenya ijambo ry'ibanga, aracyakeneye icya kabiri (kode cyangwa kwemeza muri porogaramu). Ntuzigere usangiza iyo kode.", "Hata mtu akijua nywila yako, bado anahitaji hatua ya pili (msimbo au idhini kwenye programu). Usishiriki msimbo huo na yeyote."),
      ("2FA does not speed anything up; it adds a step on purpose to protect the account.", "La 2FA n'accélère rien ; elle ajoute volontairement une étape pour protéger le compte.", "2FA ntiyihutisha; yongeraho intambwe ku bushake kugira ngo irinde konti.", "2FA haiongezi kasi; huongeza hatua kwa makusudi kulinda akaunti.")),
    Q("world", ("What is the capital of Rwanda?", "Quelle est la capitale du Rwanda ?", "Umurwa mukuru w'u Rwanda ni uwuhe?", "Mji mkuu wa Rwanda ni upi?"),
      ["Kigali", "Kampala", "Nairobi", "Bujumbura"], 0,
      ("Kigali is the capital and largest city of Rwanda.", "Kigali est la capitale et la plus grande ville du Rwanda.", "Kigali ni umurwa mukuru kandi ni umujyi munini w'u Rwanda.", "Kigali ni mji mkuu na mji mkubwa zaidi wa Rwanda."),
      ("Kampala is Uganda's capital, Nairobi is Kenya's and Bujumbura was Burundi's economic capital.", "Kampala est la capitale de l'Ouganda, Nairobi celle du Kenya, Bujumbura est la capitale économique du Burundi.", "Kampala ni umurwa mukuru wa Uganda, Nairobi ni uwa Kenya, Bujumbura ni umurwa w'ubukungu w'u Burundi.", "Kampala ni mji mkuu wa Uganda, Nairobi ni wa Kenya na Bujumbura ni mji mkuu wa kiuchumi wa Burundi.")),
    Q("world", ("Which is the largest ocean on Earth?", "Quel est le plus grand océan de la Terre ?", "Inyanja nini ku isi ni iyihe?", "Bahari kubwa zaidi duniani ni ipi?"),
      {"en": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"], "fr": ["Océan Pacifique", "Océan Atlantique", "Océan Indien", "Océan Arctique"], "rw": ["Pasifika", "Atalantika", "Inyanja y'u Buhindi", "Arctique"], "sw": ["Bahari ya Pasifiki", "Bahari ya Atlantiki", "Bahari ya Hindi", "Bahari ya Aktiki"]}, 0,
      ("The Pacific Ocean covers about a third of Earth's surface, more than all the land combined.", "L'océan Pacifique couvre environ un tiers de la surface de la Terre, plus que toutes les terres réunies.", "Pasifika ifata hafi kimwe cya gatatu cy'ubuso bw'isi, kirenze ubutaka bwose hamwe.", "Bahari ya Pasifiki inafunika karibu theluthi moja ya uso wa Dunia, zaidi ya nchi kavu zote pamoja."),
      ("The Atlantic is the second largest; the Arctic is the smallest.", "L'Atlantique est le deuxième ; l'Arctique est le plus petit.", "Atalantika ni iya kabiri; Arctique ni nto kuruta izindi.", "Atlantiki ni ya pili; Aktiki ndogo kuliko zote.")),
    Q("world", ("How many continents are there in the commonly taught seven-continent model?", "Combien de continents compte le modèle à sept continents le plus enseigné ?", "Ibyabumenyi (continents) ni bingahe mu buryo bwigishwa cyane bw'ibyabumenyi birindwi?", "Katika mfumo wa mabara saba unaofundishwa mara nyingi, kuna mabara mangapi?"),
      ["5", "6", "7", "8"], 2,
      ("Africa, Antarctica, Asia, Australia/Oceania, Europe, North America and South America make 7. (Some countries teach a 5- or 6-continent model.)", "Afrique, Antarctique, Asie, Océanie, Europe, Amérique du Nord et Amérique du Sud : 7. (Certains pays enseignent un modèle à 5 ou 6 continents.)", "Afurika, Antarctica, Aziya, Oseyaniya, Uburayi, Amerika y'Amajyaruguru n'iy'Amajyepfo: 7. (Ibindi bihugu byigisha 5 cyangwa 6.)", "Afrika, Antaktika, Asia, Australia/Oceania, Ulaya, Amerika Kaskazini na Amerika Kusini: 7. (Nchi nyingine hufundisha mfumo wa 5 au 6.)"),
      ("The number depends on the model taught; 7 is the one used in this question.", "Le nombre dépend du modèle enseigné ; 7 est celui utilisé ici.", "Umubare ushingira ku buryo bwigishwa; 7 ni wo ukoreshwa hano.", "Idadi hutegemea mfumo unaofundishwa; 7 ndio unaotumika hapa.")),
]


def options(q, lang):
    o = q["opts"]
    return o[lang] if isinstance(o, dict) else o


def pick(topic=None, n=5, seed=None):
    import random
    pool = [q for q in QUESTIONS if topic in (None, "all") or q["topic"] == topic]
    rnd = random.Random(seed)
    rnd.shuffle(pool)
    return pool[:n]


try:   # the standard cybersecurity question set (quiz_cyber.py); the quiz keeps working without it
    from quiz_cyber import build as _build_cyber
    QUESTIONS.extend(_build_cyber(Q))
except Exception:
    pass

try:   # 43 more standard cybersecurity questions (quiz_cyber2.py)
    from quiz_cyber2 import build as _build_cyber2
    QUESTIONS.extend(_build_cyber2(Q))
except Exception:
    pass


try:   # 800+ more cybersecurity questions generated from the glossary, scam catalogue and acronyms (quiz_cyber_gen.py)
    from quiz_cyber_gen import build as _build_cyber_gen
    QUESTIONS.extend(_build_cyber_gen(Q))
except Exception:
    pass

try:   # 600+ networking questions (quiz_net.py)
    from quiz_net import build as _build_net
    QUESTIONS.extend(_build_net(Q))
except Exception:
    pass
