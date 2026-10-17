"""Greetings for the AI Assistant (offline). Pure Python, no Streamlit.

When a message is just a greeting (hello, good morning, mwaramutse, bonjour, jambo, thank you, goodbye ...), the assistant answers it correctly in
that greeting's own language and explains it in all four languages (en / fr / rw / sw): what it means, which language it is from and when to use it.
Asking "what does Mwaramutse mean?" gives only the explanation. A message that contains anything else (a real question) is NOT treated as a greeting,
so it keeps going to the definitions, the guide, the scam checker or the AI as before. "types of greetings" gives an overview table.
fr / rw / sw wording is a draft for review by fluent speakers; the replies are standard courtesies, not translations of Claude's own voice."""
from __future__ import annotations
import re
from names_db import fold as _fold

LANGS = ("en", "fr", "rw", "sw")


def fold(s):
    return re.sub(r"\s+", " ", _fold(s).replace("'", " ").replace("-", " ")).strip()


LANG_LABEL = {"en": "English", "fr": "Français", "rw": "Kinyarwanda", "sw": "Kiswahili"}

# origin code -> name in en / fr / rw / sw
ORIGIN = {
    "en": ("English", "anglais", "Icyongereza", "Kiingereza"), "fr": ("French", "français", "Igifaransa", "Kifaransa"),
    "rw": ("Kinyarwanda", "kinyarwanda", "Ikinyarwanda", "Kinyarwanda"), "sw": ("Swahili", "swahili", "Igiswahili", "Kiswahili"),
    "es": ("Spanish", "espagnol", "Icyesipanyoli", "Kihispania"), "it": ("Italian", "italien", "Igitaliyani", "Kiitaliano"),
    "de": ("German", "allemand", "Ikidage", "Kijerumani"), "pt": ("Portuguese", "portugais", "Igiporutugali", "Kireno"),
    "ar": ("Arabic", "arabe", "Icyarabu", "Kiarabu"), "hi": ("Hindi", "hindi", "Igihindi", "Kihindi"),
    "ja": ("Japanese", "japonais", "Ikiyapani", "Kijapani"), "zh": ("Chinese", "chinois", "Igishinwa", "Kichina"),
    "ko": ("Korean", "coréen", "Ikikoreya", "Kikorea"), "he": ("Hebrew", "hébreu", "Igiheburayo", "Kiebrania"),
    "ru": ("Russian", "russe", "Ikirusiya", "Kirusi"), "tr": ("Turkish", "turc", "Igiturukiya", "Kituruki"),
    "zu": ("Zulu", "zoulou", "Igizulu", "Kizulu"), "ak": ("Twi (Akan)", "twi (akan)", "Igitwi (Akan)", "Kitwi (Akan)"),
    "lg": ("Luganda", "luganda", "Ikiganda", "Kiganda"), "ln": ("Lingala", "lingala", "Ikilingala", "Kilingala"),
    "haw": ("Hawaiian", "hawaïen", "Igihawayi", "Kihawai"),
}

HELP = {"en": "How can I help you?", "fr": "Comment puis-je vous aider ?", "rw": "Nabafasha iki?", "sw": "Nikusaidie nini?"}

# kind -> equivalents in en / fr / rw / sw (what the greeting is called in each of the four languages)
EQ = {
    "hello": ("Hello", "Bonjour / Salut", "Muraho", "Hujambo / Jambo"),
    "casual": ("What's up?", "Quoi de neuf ? / Salut", "Muraho (mu buryo bworoheje)", "Mambo? / Vipi?"),
    "morning": ("Good morning", "Bonjour (le matin)", "Mwaramutse", "Habari za asubuhi"),
    "afternoon": ("Good afternoon", "Bonjour / Bon après-midi", "Mwiriwe", "Habari za mchana"),
    "evening": ("Good evening", "Bonsoir", "Mwiriwe", "Habari za jioni"),
    "night": ("Good night", "Bonne nuit", "Ijoro ryiza", "Usiku mwema"),
    "howareyou": ("How are you?", "Comment allez-vous ? / Ça va ?", "Amakuru? / Mumeze mute?", "Habari yako? / Hali yako?"),
    "fine": ("I'm fine", "Je vais bien / Ça va bien", "Meze neza / Ni meza", "Sijambo / Nzuri"),
    "welcome": ("Welcome", "Bienvenue", "Murakaza neza / Ikaze", "Karibu"),
    "bye": ("Goodbye", "Au revoir", "Murabeho", "Kwaheri"),
    "seeyou": ("See you later", "À bientôt", "Tuzongera kubonana", "Tutaonana"),
    "thanks": ("Thank you", "Merci", "Murakoze", "Asante"),
    "youarewelcome": ("You're welcome", "De rien", "Ntacyo", "Karibu / Haina shida"),
    "sorry": ("Sorry / Excuse me", "Désolé / Excusez-moi / Pardon", "Mbabarira", "Samahani"),
    "sympathy": ("Sorry for your trouble (be strong)", "Courage !", "Komera", "Pole"),
    "please": ("Please", "S'il vous plaît", "Nyamuneka", "Tafadhali"),
    "congrats": ("Congratulations", "Félicitations / Bravo", "Ndabashimiye", "Hongera"),
    "birthday": ("Happy birthday", "Joyeux anniversaire", "Isabukuru nziza", "Heri ya kuzaliwa"),
    "newyear": ("Happy New Year", "Bonne année", "Umwaka mushya muhire", "Heri ya mwaka mpya"),
    "christmas": ("Merry Christmas", "Joyeux Noël", "Noheli nziza", "Krismasi njema"),
    "easter": ("Happy Easter", "Joyeuses Pâques", "Pasika nziza", "Pasaka njema"),
    "eid": ("Eid Mubarak (blessed Eid)", "Aïd Moubarak", "Eid Mubarak (Eid nziza)", "Eid Mubarak / Idd njema"),
    "ramadan": ("Ramadan Mubarak", "Ramadan Moubarak", "Ramadan Mubarak", "Ramadhani Mubarak"),
    "getwell": ("Get well soon", "Bon rétablissement", "Uzakire vuba", "Upone haraka"),
    "goodluck": ("Good luck", "Bonne chance", "Amahirwe masa", "Bahati njema / Kila la heri"),
    "nicemeet": ("Nice to meet you", "Enchanté(e)", "Nishimiye kukumenya", "Nimefurahi kukutana nawe"),
    "respect": ("Shikamoo (respectful greeting to an elder)", "Shikamoo (salutation respectueuse à un aîné)", "Shikamoo (indamutso y'icyubahiro ku mukuru)", "Shikamoo"),
    "respectreply": ("Marahaba (the elder's reply)", "Marahaba (réponse de l'aîné)", "Marahaba (igisubizo cy'umukuru)", "Marahaba"),
    "salam": ("Peace be upon you", "Que la paix soit sur vous", "Amahoro abe kuri mwe", "Amani iwe juu yenu"),
    "praise": ("Praise be to Jesus (Christian greeting)", "Louange à Jésus (salutation chrétienne)", "Yezu ashimwe", "Yesu asifiwe"),
    "salamreply": ("And upon you be peace", "Et sur vous la paix", "Namwe amahoro abe kuri mwe", "Nawe amani iwe juu yako"),
    "hellobye": ("Hello / Goodbye (informal)", "Salut (bonjour ou au revoir, familier)", "Muraho / Murabeho (mu buryo bworoheje)", "Hujambo / Kwaheri (kwa kawaida)"),
    "peace": ("Peace (hello / goodbye)", "Paix (bonjour / au revoir)", "Amahoro (muraho / murabeho)", "Amani (salamu / kwaheri)"),
    "travel": ("Safe journey", "Bon voyage", "Urugendo rwiza", "Safari njema"),
    "niceday": ("Have a nice day", "Bonne journée", "Gira umunsi mwiza", "Siku njema"),
    "blessing": ("God bless you", "Que Dieu vous bénisse", "Imana iguhe umugisha", "Mungu akubariki"),
    "enjoymeal": ("Enjoy your meal", "Bon appétit", "Murye neza", "Karibu chakula"),
}

# kind -> (title en/fr/rw/sw, when to use en/fr/rw/sw)
KIND = {
    "hello": ("General greeting", "Salutation générale", "Indamutso rusange", "Salamu ya kawaida",
              "A general greeting you can use at any time of day when you meet someone or start a conversation.",
              "Salutation générale, utilisable à toute heure quand on rencontre quelqu'un ou commence une conversation.",
              "Indamutso rusange ushobora gukoresha igihe icyo ari cyo cyose uhuye n'umuntu cyangwa utangiye ikiganiro.",
              "Salamu ya kawaida unayoweza kutumia wakati wowote unapokutana na mtu au kuanza mazungumzo."),
    "casual": ("Casual greeting", "Salutation familière", "Indamutso yoroheje", "Salamu isiyo rasmi",
               "An informal greeting between friends or people of the same age; avoid it with elders or in formal situations.",
               "Salutation familière entre amis ou personnes du même âge ; à éviter avec des aînés ou en situation formelle.",
               "Indamutso itaboneye hagati y'inshuti cyangwa abangana; irinde kuyikoresha ku bakuru cyangwa mu birori by'icyubahiro.",
               "Salamu isiyo rasmi kati ya marafiki au rika moja; epuka kuitumia kwa wazee au hali rasmi."),
    "morning": ("Morning greeting", "Salutation du matin", "Indamutso y'igitondo", "Salamu ya asubuhi",
                "Used from sunrise until around midday.", "Employé du lever du soleil jusqu'à environ midi.",
                "Ikoreshwa kuva izuba rirashe kugeza ahagana saa sita z'amanywa.", "Hutumika kuanzia mawio hadi takriban adhuhuri."),
    "afternoon": ("Afternoon greeting", "Salutation de l'après-midi", "Indamutso ya nyuma ya saa sita", "Salamu ya mchana",
                  "Used from around midday until late afternoon.", "Employé de midi jusqu'en fin d'après-midi.",
                  "Ikoreshwa kuva saa sita z'amanywa kugeza nimugoroba.", "Hutumika kuanzia adhuhuri hadi alasiri."),
    "evening": ("Evening greeting", "Salutation du soir", "Indamutso ya nimugoroba", "Salamu ya jioni",
                "Used from late afternoon until night.", "Employé de la fin d'après-midi jusqu'à la nuit.",
                "Ikoreshwa kuva nimugoroba kugeza ijoro.", "Hutumika kuanzia jioni hadi usiku."),
    "night": ("Night farewell", "Salutation de la nuit", "Gusezera nijoro", "Kuaga usiku",
              "Said when parting for the night or going to bed, not as a first greeting.",
              "Dit en se quittant pour la nuit ou en allant dormir, pas comme première salutation.",
              "Bivugwa mu gusezera nijoro cyangwa mbere yo kuryama, si indamutso yo guhura.",
              "Husemwa wakati wa kuagana usiku au kabla ya kulala, si salamu ya kukutana."),
    "howareyou": ("Asking how someone is", "Demander des nouvelles", "Kubaza uko umuntu ameze", "Kuulizia hali",
                  "Asks about the other person's well-being. It is polite to answer and ask back.",
                  "Prend des nouvelles de l'autre personne. Il est poli de répondre puis de demander en retour.",
                  "Ubaza uko undi ameze. Ni ikinyabupfura gusubiza ukabaza nawe.",
                  "Huuliza hali ya mtu mwingine. Ni adabu kujibu na kuuliza pia."),
    "fine": ("Saying you are well", "Dire que l'on va bien", "Kuvuga ko umeze neza", "Kusema uko uko vizuri",
             "A normal answer to \"How are you?\", saying that you are well.",
             "Réponse habituelle à « Comment ça va ? » pour dire qu'on va bien.",
             "Igisubizo gisanzwe kuri \"Amakuru?\" kivuga ko umeze neza.",
             "Jibu la kawaida kwa \"Habari?\" linaloeleza kuwa uko vizuri."),
    "welcome": ("Welcome", "Accueil", "Kwakira", "Kukaribisha",
                "Said to greet someone who arrives or joins you.", "Dit pour accueillir quelqu'un qui arrive ou vous rejoint.",
                "Bivugwa mu kwakira umuntu ugeze cyangwa waje.", "Husemwa kumkaribisha mtu anayefika au kujiunga nawe."),
    "bye": ("Goodbye", "Au revoir", "Gusezera", "Kuaga",
            "Said when leaving or ending a conversation.", "Dit en partant ou en terminant une conversation.",
            "Bivugwa mu gusezera cyangwa mu gusoza ikiganiro.", "Husemwa unapoondoka au kumaliza mazungumzo."),
    "seeyou": ("See you later", "À bientôt", "Gusezera uzongera kubona", "Kuaga ukitarajia kuonana",
               "Said when you expect to meet the person again.", "Dit quand on pense revoir la personne.",
               "Bivugwa mu gusezera ukeka ko muzongera kubonana.", "Husemwa unapotarajia kuonana tena na mtu."),
    "thanks": ("Thanking someone", "Remercier", "Gushimira", "Kushukuru",
               "Shows gratitude. A common reply is \"you're welcome\".", "Exprime la gratitude. Réponse courante : « de rien ».",
               "Bigaragaza ugushimira. Igisubizo gisanzwe ni \"ntacyo\".", "Huonyesha shukrani. Jibu la kawaida ni \"karibu\"."),
    "youarewelcome": ("Replying to thanks", "Répondre à un remerciement", "Gusubiza ugushimira", "Kujibu shukrani",
                      "A polite reply after someone thanks you.", "Réponse polie quand quelqu'un vous remercie.",
                      "Igisubizo cy'ikinyabupfura iyo umuntu agushimiye.", "Jibu la adabu mtu anapokushukuru."),
    "sorry": ("Apologising / excuse me", "S'excuser", "Gusaba imbabazi", "Kuomba msamaha",
              "Used to apologise or to politely get someone's attention.", "Sert à s'excuser ou à attirer poliment l'attention.",
              "Bikoreshwa mu gusaba imbabazi cyangwa kwitaba mu kinyabupfura.", "Hutumika kuomba msamaha au kuvuta usikivu kwa adabu."),
    "sympathy": ("Showing sympathy", "Témoigner de la compassion", "Guhumuriza", "Kuonyesha huruma",
                 "Said to someone who is hurt, tired, grieving or facing difficulty.",
                 "Dit à quelqu'un qui souffre, est fatigué, en deuil ou en difficulté.",
                 "Bivugwa ku muntu ufite ikibazo, unaniwe cyangwa wabuze uwe.", "Husemwa kwa mtu aliyeumia, kuchoka, kufiwa au mwenye shida."),
    "please": ("Please", "S'il vous plaît", "Gusaba mu kinyabupfura", "Ombi la adabu",
               "Added to a request to be polite.", "Ajouté à une demande par politesse.", "Byongerwa ku busabe kugira ngo bube mu kinyabupfura.", "Huongezwa kwenye ombi kwa adabu."),
    "congrats": ("Congratulating", "Féliciter", "Gushimira ibyagezweho", "Kupongeza",
                 "Said to praise someone's success or good news.", "Dit pour saluer la réussite ou une bonne nouvelle de quelqu'un.",
                 "Bivugwa mu gushima intsinzi cyangwa inkuru nziza y'umuntu.", "Husemwa kupongeza mafanikio au habari njema ya mtu."),
    "birthday": ("Birthday wish", "Vœux d'anniversaire", "Kwifuriza isabukuru", "Salamu za kuzaliwa",
                 "Said on someone's birthday.", "Dit le jour de l'anniversaire de quelqu'un.", "Bivugwa ku munsi w'amavuko w'umuntu.", "Husemwa siku ya kuzaliwa kwa mtu."),
    "newyear": ("New Year wish", "Vœux de nouvelle année", "Kwifuriza umwaka mushya", "Salamu za mwaka mpya",
                "Said around 31 December and 1 January.", "Dit autour du 31 décembre et du 1er janvier.",
                "Bivugwa hafi ya tariki ya 31 Ukuboza na 1 Mutarama.", "Husemwa karibu na tarehe 31 Desemba na 1 Januari."),
    "christmas": ("Christmas wish", "Vœux de Noël", "Kwifuriza Noheli", "Salamu za Krismasi",
                  "Said around 25 December.", "Dit autour du 25 décembre.", "Bivugwa hafi ya tariki ya 25 Ukuboza.", "Husemwa karibu na tarehe 25 Desemba."),
    "easter": ("Easter wish", "Vœux de Pâques", "Kwifuriza Pasika", "Salamu za Pasaka",
               "Said around Easter.", "Dit à l'approche de Pâques.", "Bivugwa mu gihe cya Pasika.", "Husemwa wakati wa Pasaka."),
    "eid": ("Eid greeting", "Salutation de l'Aïd", "Indamutso ya Eid", "Salamu za Idd",
            "Said by and to Muslims at the Eid festivals.", "Dit entre musulmans lors des fêtes de l'Aïd.",
            "Bivugwa n'Abayisilamu mu minsi mikuru ya Eid.", "Husemwa na Waislamu wakati wa sikukuu za Idd."),
    "ramadan": ("Ramadan greeting", "Salutation du Ramadan", "Indamutso ya Ramadan", "Salamu za Ramadhani",
                "Said during the month of Ramadan.", "Dit pendant le mois de Ramadan.", "Bivugwa mu kwezi kwa Ramadan.", "Husemwa wakati wa mwezi wa Ramadhani."),
    "getwell": ("Get-well wish", "Vœux de rétablissement", "Kwifuriza gukira", "Kutakia kupona",
                "Said to someone who is ill or hurt.", "Dit à quelqu'un de malade ou blessé.", "Bivugwa ku muntu urwaye cyangwa wakomeretse.", "Husemwa kwa mtu mgonjwa au aliyejeruhiwa."),
    "goodluck": ("Good-luck wish", "Souhait de chance", "Kwifuriza amahirwe", "Kutakia bahati",
                 "Said before an exam, trip, interview or challenge.", "Dit avant un examen, un voyage, un entretien ou un défi.",
                 "Bivugwa mbere y'ikizamini, urugendo, ikiganiro cy'akazi cyangwa ikibazo kigoye.", "Husemwa kabla ya mtihani, safari, usaili au changamoto."),
    "nicemeet": ("Meeting someone for the first time", "Première rencontre", "Guhura ku nshuro ya mbere", "Kukutana kwa mara ya kwanza",
                 "Said when you meet someone for the first time.", "Dit quand on rencontre quelqu'un pour la première fois.",
                 "Bivugwa uhuye n'umuntu ku nshuro ya mbere.", "Husemwa unapokutana na mtu kwa mara ya kwanza."),
    "respect": ("Respectful greeting", "Salutation respectueuse", "Indamutso y'icyubahiro", "Salamu ya heshima",
                "In Swahili-speaking regions a younger person greets an elder with this out of respect; the elder replies \"Marahaba\".",
                "Dans les régions swahiliphones, un plus jeune salue ainsi un aîné par respect ; l'aîné répond « Marahaba ».",
                "Mu duce twavuga igiswahili, umuto aramutsa umukuru atya amwubaha; umukuru asubiza ati \"Marahaba\".",
                "Katika maeneo ya Kiswahili, mdogo humsalimu mkubwa hivi kwa heshima; mkubwa hujibu \"Marahaba\"."),
    "respectreply": ("Reply to Shikamoo", "Réponse à Shikamoo", "Igisubizo kuri Shikamoo", "Jibu la Shikamoo",
                     "The traditional reply an elder gives to \"Shikamoo\".", "Réponse traditionnelle de l'aîné à « Shikamoo ».",
                     "Igisubizo gisanzwe umukuru atanga kuri \"Shikamoo\".", "Jibu la jadi la mkubwa kwa \"Shikamoo\"."),
    "salam": ("Greeting of peace", "Salutation de paix", "Indamutso y'amahoro", "Salamu ya amani",
              "A greeting of peace used by Muslims and in many Arabic-speaking places; the reply is \"wa alaykum as-salam\".",
              "Salutation de paix utilisée par les musulmans et dans de nombreux pays arabophones ; réponse : « wa alaykum as-salam ».",
              "Indamutso y'amahoro ikoreshwa n'Abayisilamu no mu bihugu byinshi bivuga icyarabu; igisubizo ni \"wa alaykum as-salam\".",
              "Salamu ya amani inayotumiwa na Waislamu na maeneo mengi ya Kiarabu; jibu ni \"wa alaykum as-salam\"."),
    "praise": ("Christian greeting of praise", "Salutation chrétienne de louange", "Indamutso y'abakristu", "Salamu ya Wakristo",
               "A greeting used among Christians, especially in Rwanda (\"Yezu ashimwe\") and East Africa (\"Yesu asifiwe\"). It means \"Praise be to Jesus\" and is answered with \"Iteka ryose\" / \"Milele\" (forever) and \"Amen\".",
               "Salutation utilisée entre chrétiens, surtout au Rwanda (« Yezu ashimwe ») et en Afrique de l'Est (« Yesu asifiwe »). Elle signifie « Louange à Jésus » et on répond « Iteka ryose » / « Milele » (pour toujours) et « Amen ».",
               "Indamutso ikoreshwa mu bakristu, cyane cyane mu Rwanda (\"Yezu ashimwe\") no muri Afurika y'Iburasirazuba (\"Yesu asifiwe\"). Isobanura \"Yezu ahabwe ishimwe\" kandi isubizwa \"Iteka ryose\" / \"Milele\" (iteka) na \"Amen\".",
               "Salamu inayotumiwa kati ya Wakristo, hasa Rwanda (\"Yezu ashimwe\") na Afrika Mashariki (\"Yesu asifiwe\"). Inamaanisha \"Yesu asifiwe\" na hujibiwa \"Milele\" / \"Iteka ryose\" na \"Amina\"."),
    "salamreply": ("Reply to the greeting of peace", "Réponse à la salutation de paix", "Igisubizo ku ndamutso y'amahoro", "Jibu la salamu ya amani",
                   "The reply to \"as-salamu alaykum\".", "La réponse à « as-salamu alaykum ».", "Igisubizo kuri \"as-salamu alaykum\".", "Jibu la \"as-salamu alaykum\"."),
    "hellobye": ("Hello or goodbye (informal)", "Bonjour ou au revoir (familier)", "Muraho cyangwa murabeho (bworoheje)", "Salamu au kwaheri (kwa kawaida)",
                 "An informal word used both to say hello and to say goodbye.", "Mot familier qui sert à la fois à dire bonjour et au revoir.",
                 "Ijambo ryoroheje rikoreshwa mu kuramutsa no mu gusezera.", "Neno lisilo rasmi linalotumika kusalimu na kuaga."),
    "peace": ("Greeting of peace", "Salutation de paix", "Indamutso y'amahoro", "Salamu ya amani",
              "A word meaning peace, used for hello and goodbye.", "Mot qui signifie la paix, utilisé pour dire bonjour et au revoir.",
              "Ijambo risobanura amahoro, rikoreshwa mu kuramutsa no gusezera.", "Neno linalomaanisha amani, linalotumika kusalimu na kuaga."),
    "travel": ("Travel wish", "Souhait de voyage", "Kwifuriza urugendo rwiza", "Kutakia safari njema",
               "Said to someone who is leaving on a journey.", "Dit à quelqu'un qui part en voyage.", "Bivugwa ku muntu ugiye mu rugendo.", "Husemwa kwa mtu anayeondoka safarini."),
    "niceday": ("Wishing a good day", "Souhait de bonne journée", "Kwifuriza umunsi mwiza", "Kutakia siku njema",
                "Said when parting to wish someone a good day.", "Dit en se quittant pour souhaiter une bonne journée.",
                "Bivugwa mu gusezera wifuriza undi umunsi mwiza.", "Husemwa wakati wa kuagana kumtakia mtu siku njema."),
    "blessing": ("Blessing", "Bénédiction", "Umugisha", "Baraka",
                 "A religious well-wish, often used when thanking or parting.", "Souhait religieux, souvent utilisé pour remercier ou se quitter.",
                 "Icyifuzo gishingiye ku idini, gikunze gukoreshwa mu gushimira cyangwa gusezera.", "Takwimu ya kidini, mara nyingi hutumika kushukuru au kuaga."),
    "enjoymeal": ("Mealtime wish", "Souhait pour le repas", "Kwifuriza kurya neza", "Kutakia mlo mwema",
                  "Said before a meal.", "Dit avant un repas.", "Bivugwa mbere yo kurya.", "Husemwa kabla ya mlo."),
}

# kind ~ aliases (first = display name) ~ origin ~ reply in that language
ROWS = """
hello ~ hello,hello there,helo,hullo ~ en ~ Hello! 👋
hello ~ hi,hi there,hiya,hey,hey there,heya,hiii,hii ~ en ~ Hi there! 👋
hello ~ good day,goodday,g day,howdy ~ en ~ Good day! 👋
casual ~ what s up,whats up,wassup,sup,wazzup,yo ~ en ~ Hey! All good here. What's up with you?
morning ~ good morning,morning,gm,good mornin,mornin,top of the morning ~ en ~ Good morning! ☀️
afternoon ~ good afternoon,afternoon ~ en ~ Good afternoon! 🌤️
evening ~ good evening,evening ~ en ~ Good evening! 🌆
night ~ good night,goodnight,night night,nite nite,nighty night,gn,sweet dreams ~ en ~ Good night! Sleep well. 🌙
howareyou ~ how are you,how r u,how are u,how are you doing,how is it going,how s it going,hows it going,how are things,how you doing,how have you been,hru,how do you do,how is everything,how s life ~ en ~ I'm doing well, thank you for asking! How are you?
fine ~ i am fine,i m fine,im fine,i am good,i m good,im good,fine thanks,fine thank you,i am well,i am doing well,not bad,all good,doing well,fine,i am great,i m great,im great,great thanks ~ en ~ Glad to hear that! 😊
welcome ~ welcome,welcome back,welcome aboard ~ en ~ Thank you! 😊
bye ~ bye,goodbye,good bye,bye bye,farewell,cheerio,so long,bye for now ~ en ~ Goodbye! Take care. 👋
seeyou ~ see you,see you later,see you soon,see you tomorrow,see ya,cya,catch you later,talk to you later,ttyl,until next time ~ en ~ See you later! Take care. 👋
thanks ~ thank you,thanks,thx,ty,thank u,many thanks,thanks a lot,thanks so much,much appreciated,i appreciate it,appreciated ~ en ~ You're welcome! 😊
youarewelcome ~ you are welcome,you re welcome,your welcome,youre welcome,no problem,no worries,not at all,my pleasure,anytime ~ en ~ Happy to help! 😊
sorry ~ sorry,i am sorry,i m sorry,im sorry,my bad,apologies,my apologies,excuse me,pardon me,forgive me ~ en ~ No problem at all.
sympathy ~ sorry to hear that,be strong,stay strong,hang in there ~ en ~ Thank you for the kind words. 💙
please ~ please,pls,plz,kindly ~ en ~ Of course, please go ahead.
congrats ~ congratulations,congrats,well done,kudos,good job,great job,nice work,bravo ~ en ~ Thank you so much! 😊
birthday ~ happy birthday,hbd,happy bday,happy birth day,many happy returns ~ en ~ Thank you! 🎂 Happy birthday to whoever is celebrating!
newyear ~ happy new year,hny,happy 2027,happy new years ~ en ~ Happy New Year to you too! 🎉
christmas ~ merry christmas,happy christmas,xmas greetings,happy xmas,season s greetings,happy holidays ~ en ~ Merry Christmas to you too! 🎄
easter ~ happy easter ~ en ~ Happy Easter to you too! 🐣
getwell ~ get well soon,get well,feel better,feel better soon,hope you feel better ~ en ~ Thank you for the kind wishes. Take care too.
goodluck ~ good luck,best of luck,all the best,break a leg,best wishes,fingers crossed ~ en ~ Thank you! Good luck to you too. 🍀
nicemeet ~ nice to meet you,pleased to meet you,good to meet you,glad to meet you,lovely to meet you ~ en ~ Nice to meet you too! 😊
travel ~ safe journey,safe travels,have a safe trip,happy journey ~ en ~ Thank you! Safe journey to you too.
niceday ~ have a nice day,have a good day,have a great day,enjoy your day,good day to you ~ en ~ Thank you, you too! ☀️
blessing ~ god bless you,god bless,bless you,blessings ~ en ~ Thank you, and may you be blessed too. 🙏
enjoymeal ~ enjoy your meal,enjoy your food,enjoy the meal ~ en ~ Thank you, enjoy yours too!
morning ~ bonjour le matin ~ fr ~ Bonjour !
hello ~ bonjour,bonjour a tous,allo,bonjour madame,bonjour monsieur,bonjour tout le monde ~ fr ~ Bonjour ! 👋
hello ~ salut,coucou,salut a tous,slt,bjr ~ fr ~ Salut ! 👋
evening ~ bonsoir,bonsoir a tous,bonne soiree ~ fr ~ Bonsoir ! 🌆
night ~ bonne nuit,bonne nuit a tous,fais de beaux reves ~ fr ~ Bonne nuit ! Dormez bien. 🌙
afternoon ~ bon apres midi,bonne apres midi ~ fr ~ Bon après-midi ! 🌤️
howareyou ~ ca va,comment ca va,comment allez vous,comment vas tu,comment tu vas,tu vas bien,vous allez bien,comment vous allez,ca roule,la forme ~ fr ~ Ça va très bien, merci ! Et vous ?
casual ~ quoi de neuf,quoi d neuf,ca gaze ~ fr ~ Rien de spécial, et toi ?
fine ~ ca va bien,je vais bien,tres bien,bien merci,ca va merci,tout va bien,ca va tres bien,je vais tres bien,pas mal ~ fr ~ Content de l'entendre ! 😊
welcome ~ bienvenue,soyez le bienvenu,sois le bienvenu ~ fr ~ Merci ! 😊
bye ~ au revoir,adieu,a plus,a plus tard,a la prochaine ~ fr ~ Au revoir ! Prenez soin de vous. 👋
seeyou ~ a bientot,a demain,a tout de suite,on se voit bientot ~ fr ~ À bientôt ! 👋
thanks ~ merci,merci beaucoup,mille mercis,merci bien,je vous remercie,je te remercie ~ fr ~ De rien ! 😊
youarewelcome ~ de rien,je vous en prie,pas de souci,avec plaisir,il n y a pas de quoi ~ fr ~ Avec plaisir ! 😊
sorry ~ desole,desolee,je suis desole,pardon,excusez moi,excuse moi,mes excuses ~ fr ~ Il n'y a pas de mal.
sympathy ~ courage,bon courage,tenez bon,sois fort,soyez fort,mes condoleances ~ fr ~ Merci pour vos mots. 💙
please ~ s il vous plait,s il te plait,svp,stp,sil vous plait,sil te plait ~ fr ~ Bien sûr, allez-y.
congrats ~ felicitations,bien joue,bravo a toi,bravo a vous ~ fr ~ Merci beaucoup ! 😊
birthday ~ joyeux anniversaire,bon anniversaire,joyeux anniv ~ fr ~ Merci ! 🎂 Joyeux anniversaire à la personne concernée !
newyear ~ bonne annee,bonne annee et bonne sante,meilleurs voeux ~ fr ~ Bonne année à vous aussi ! 🎉
christmas ~ joyeux noel,joyeuses fetes,bonnes fetes ~ fr ~ Joyeux Noël à vous aussi ! 🎄
easter ~ joyeuses paques,bonnes paques ~ fr ~ Joyeuses Pâques à vous aussi ! 🐣
getwell ~ bon retablissement,prompt retablissement,remets toi vite,retablis toi vite ~ fr ~ Merci pour vos bons voeux. Prenez soin de vous aussi.
goodluck ~ bonne chance,tous mes voeux de reussite,bon courage pour ~ fr ~ Merci ! Bonne chance à vous aussi. 🍀
nicemeet ~ enchante,enchantee,ravi de vous rencontrer,ravie de vous rencontrer,heureux de vous connaitre ~ fr ~ Enchanté ! 😊
travel ~ bon voyage,bonne route ~ fr ~ Merci ! Bon voyage à vous aussi.
niceday ~ bonne journee,passez une bonne journee,bonne journee a vous ~ fr ~ Merci, à vous aussi ! ☀️
blessing ~ que dieu vous benisse,dieu vous benisse ~ fr ~ Merci, que Dieu vous bénisse aussi. 🙏
enjoymeal ~ bon appetit ~ fr ~ Merci, bon appétit à vous aussi !
hello ~ muraho,muraho neza,mwaramutse muraho ~ rw ~ Muraho! 👋
morning ~ mwaramutse,mwaramutse neza,mwaramutse mwese,mwaramutse bose ~ rw ~ Mwaramutse! ☀️
afternoon ~ mwiriwe,mwiriwe neza,mwiriwe mwese,mwiriwe bose ~ rw ~ Mwiriwe! 🌤️
night ~ ijoro ryiza,mugire ijoro ryiza ~ rw ~ Ijoro ryiza! Muryame neza. 🌙
howareyou ~ amakuru,amakuru yawe,amakuru se,amakuru yanyu,umeze ute,mumeze mute,ni amahoro,muraho amakuru ~ rw ~ Ni meza, murakoze! Mwe se?
fine ~ meze neza,ni meza,ni byiza,nta kibazo,meze neza murakoze ~ rw ~ Ni byiza kubyumva! 😊
welcome ~ murakaza neza,ikaze,ikaze neza,mwakiriwe ~ rw ~ Murakoze! 😊
bye ~ murabeho,mugire amahoro,urabeho ~ rw ~ Murabeho! Mugire amahoro. 👋
seeyou ~ turabonana,tuzabonana,tuzongera kubonana vuba,ejo tuzabonana ~ rw ~ Turabonana! 👋
thanks ~ murakoze,murakoze cyane,urakoze,urakoze cyane,warakoze,warakoze cyane,ndagushimiye,murakoze mwese ~ rw ~ Ntacyo! 😊
youarewelcome ~ ntacyo,nta cyo ~ rw ~ Murakoze! 😊
sorry ~ mbabarira,mumbabarire,umbabarire,nsabye imbabazi,mbabarire ~ rw ~ Nta kibazo.
sympathy ~ komera,mukomere,komera cyane,mukomere cyane,ihangane ~ rw ~ Murakoze kubw'amagambo meza. 💙
please ~ nyamuneka,ndakwinginze,ndabinginze,mbasabye ~ rw ~ Yego, tangira.
congrats ~ ndabashimiye,mwakoze neza ~ rw ~ Murakoze cyane! 😊
birthday ~ isabukuru nziza,isabukuru y amavuko nziza,isabukuru y amavuko ~ rw ~ Murakoze! 🎂 Isabukuru nziza ku wizihiza!
newyear ~ umwaka mushya muhire,umwaka mushya muhire mwese ~ rw ~ Namwe umwaka mushya muhire! 🎉
christmas ~ noheli nziza,noheli nziza n umwaka mushya muhire,noheli ~ rw ~ Namwe Noheli nziza! 🎄
easter ~ pasika nziza ~ rw ~ Namwe Pasika nziza! 🐣
getwell ~ uzakire vuba,gira ubuzima bwiza,komera uzakire,mukire vuba ~ rw ~ Murakoze kubwo kunyifuriza ibyiza. Namwe mwiyiteho.
goodluck ~ amahirwe masa,amahirwe,ugire amahirwe masa,mugire amahirwe masa ~ rw ~ Murakoze! Namwe amahirwe masa. 🍀
nicemeet ~ nishimiye kukumenya,twishimiye kubamenya,nishimiye guhura nawe,ndishimye kukumenya ~ rw ~ Nanjye nishimiye kubamenya! 😊
travel ~ urugendo rwiza,mugire urugendo rwiza,ugire urugendo rwiza ~ rw ~ Murakoze! Namwe urugendo rwiza.
niceday ~ gira umunsi mwiza,mugire umunsi mwiza,umunsi mwiza ~ rw ~ Murakoze, namwe! ☀️
blessing ~ imana iguhe umugisha,imana ibahe umugisha,imana ikugumane ~ rw ~ Murakoze, Imana ibahe umugisha namwe. 🙏
enjoymeal ~ murye neza,urye neza,ngaho murye ~ rw ~ Murakoze, namwe murye neza!
hello ~ hujambo,jambo,hamjambo,jambo bwana ~ sw ~ Sijambo! 👋
hello ~ habari,habari gani,habari yako ~ sw ~ Nzuri! Habari yako?
casual ~ mambo,mambo vipi,vipi,vipi vipi,niaje ~ sw ~ Poa! Mambo vipi?
morning ~ habari za asubuhi,asubuhi njema,subalkheri ~ sw ~ Nzuri! Habari za asubuhi. ☀️
afternoon ~ habari za mchana,mchana mwema ~ sw ~ Nzuri! Habari za mchana. 🌤️
evening ~ habari za jioni,jioni njema ~ sw ~ Nzuri! Habari za jioni. 🌆
night ~ usiku mwema,lala salama,laleni salama ~ sw ~ Usiku mwema! Lala salama. 🌙
howareyou ~ hali yako,u hali gani,hali gani,habari za siku,habari za leo,habari za kazi,habari za nyumbani ~ sw ~ Nzuri sana, asante! Wewe je?
fine ~ sijambo,nzuri,nzuri sana,salama,nzuri asante,sina neno,ni mzima,mzima ~ sw ~ Nafurahi kusikia hivyo! 😊
welcome ~ karibu,karibuni,karibu sana,karibu tena ~ sw ~ Asante! 😊
bye ~ kwaheri,kwaherini,kwaheri ya kuonana,baadaye ~ sw ~ Kwaheri! Jitunze. 👋
seeyou ~ tutaonana,tuonane,tutaonana baadaye,tutaonana kesho,tuonane tena ~ sw ~ Tutaonana! 👋
thanks ~ asante,asante sana,ahsante,ahsante sana,shukrani,nashukuru,asanteni ~ sw ~ Karibu! 😊
youarewelcome ~ haina shida,hakuna shida,hakuna matata,usijali ~ sw ~ Asante! 😊
sorry ~ samahani,naomba msamaha,nisamehe,msamaha ~ sw ~ Hakuna shida.
sympathy ~ pole,pole sana,pole kwa kazi,pole na msiba,pole na safari ~ sw ~ Asante kwa maneno mazuri. 💙
please ~ tafadhali,tafadhali sana,naomba ~ sw ~ Ndiyo, endelea tafadhali.
congrats ~ hongera,hongera sana,hongereni,vizuri sana ~ sw ~ Asante sana! 😊
birthday ~ heri ya kuzaliwa,heri ya siku ya kuzaliwa,furaha ya siku ya kuzaliwa ~ sw ~ Asante! 🎂 Heri ya kuzaliwa kwa anayesherehekea!
newyear ~ heri ya mwaka mpya,mwaka mpya mwema,heri ya mwaka mpya mwema ~ sw ~ Nawe heri ya mwaka mpya! 🎉
christmas ~ krismasi njema,heri ya krismasi,heri ya krismas ~ sw ~ Nawe Krismasi njema! 🎄
easter ~ pasaka njema,heri ya pasaka ~ sw ~ Nawe Pasaka njema! 🐣
getwell ~ upone haraka,pona haraka,upone upesi,pole na ugonjwa ~ sw ~ Asante kwa matakwa mema. Jitunze pia.
goodluck ~ bahati njema,kila la heri,heri njema,nakutakia kila la heri ~ sw ~ Asante! Kila la heri nawe pia. 🍀
nicemeet ~ nimefurahi kukutana nawe,nafurahi kukujua,nimefurahi kukuona ~ sw ~ Nami nimefurahi kukutana nawe! 😊
travel ~ safari njema,safari salama,nakutakia safari njema ~ sw ~ Asante! Safari njema nawe pia.
niceday ~ siku njema,siku njema kwako,uwe na siku njema ~ sw ~ Asante, nawe pia! ☀️
blessing ~ mungu akubariki,mungu akubariki sana,mungu awabariki ~ sw ~ Asante, Mungu akubariki pia. 🙏
enjoymeal ~ karibu chakula,furahia chakula,mlo mwema ~ sw ~ Asante, nawe karibu!
respect ~ shikamoo,shikamoo mzee ~ sw ~ Marahaba! 🙏
respectreply ~ marahaba ~ sw ~ Karibu! Nikusaidie nini?
hello ~ hola,hola amigo ~ es ~ ¡Hola! 👋
morning ~ buenos dias,buen dia ~ es ~ ¡Buenos días! ☀️
afternoon ~ buenas tardes ~ es ~ ¡Buenas tardes! 🌤️
night ~ buenas noches ~ es ~ ¡Buenas noches! 🌙
bye ~ adios,hasta luego,hasta la vista,hasta manana ~ es ~ ¡Adiós! 👋
thanks ~ gracias,muchas gracias,mil gracias ~ es ~ ¡De nada! 😊
please ~ por favor ~ es ~ Claro, adelante.
howareyou ~ como estas,como esta usted,que tal ~ es ~ ¡Muy bien, gracias! ¿Y tú?
hellobye ~ ciao,ciao ciao ~ it ~ Ciao! 👋
morning ~ buongiorno ~ it ~ Buongiorno! ☀️
evening ~ buonasera ~ it ~ Buonasera! 🌆
night ~ buonanotte ~ it ~ Buonanotte! 🌙
bye ~ arrivederci,a presto ~ it ~ Arrivederci! 👋
thanks ~ grazie,grazie mille ~ it ~ Prego! 😊
hello ~ hallo,hallo zusammen,servus,moin ~ de ~ Hallo! 👋
morning ~ guten morgen ~ de ~ Guten Morgen! ☀️
afternoon ~ guten tag ~ de ~ Guten Tag! 🌤️
evening ~ guten abend ~ de ~ Guten Abend! 🌆
night ~ gute nacht ~ de ~ Gute Nacht! 🌙
bye ~ auf wiedersehen,tschuss,tschus,bis bald,bis spater ~ de ~ Auf Wiedersehen! 👋
thanks ~ danke,danke schon,vielen dank ~ de ~ Bitte schön! 😊
howareyou ~ wie geht s,wie geht es dir,wie geht es ihnen ~ de ~ Gut, danke! Und dir?
hello ~ ola,oi ~ pt ~ Olá! 👋
morning ~ bom dia ~ pt ~ Bom dia! ☀️
afternoon ~ boa tarde ~ pt ~ Boa tarde! 🌤️
night ~ boa noite ~ pt ~ Boa noite! 🌙
bye ~ tchau,ate logo,ate amanha ~ pt ~ Tchau! 👋
thanks ~ obrigado,obrigada,muito obrigado,muito obrigada ~ pt ~ De nada! 😊
praise ~ yezu ashimwe,yezu kristu ashimwe,yesu ashimwe ~ rw ~ Iteka ryose. Amen! 🙏
praise ~ yesu asifiwe,bwana yesu asifiwe ~ sw ~ Milele na milele. Amina! 🙏
salam ~ as salamu alaykum,assalamu alaikum,assalamu alaykum,salam alaikum,salaam alaykum,salam alaykum,asalam alaikum,asalamu alaykum,assalamualaikum,peace be upon you,salam,salaam ~ ar ~ Wa alaykum as-salam wa rahmatullah! 🤝
salamreply ~ wa alaykum as salam,wa alaikum assalam,walaykum assalam,waalaikumsalam,wa alaykum salam ~ ar ~ Wa alaykum as-salam! 🤝
hello ~ marhaba,marhaban,ahlan,ahlan wa sahlan ~ ar ~ Marhaba! 👋
morning ~ sabah al khair,sabah alkhair ~ ar ~ Sabah an-nur! ☀️
thanks ~ shukran,shukran jazilan,jazakallah khair ~ ar ~ Afwan! 😊
bye ~ ma a salama,maa salama,ma salama ~ ar ~ Ma'a salama! 👋
eid ~ eid mubarak,eid,happy eid,eid said,aid moubarak,idd mubarak ~ ar ~ Eid Mubarak to you too! Khair mubarak. 🌙
ramadan ~ ramadan mubarak,ramadan kareem,ramadhan mubarak,ramadhan kareem,ramadan moubarak ~ ar ~ Ramadan Mubarak to you too! 🌙
hello ~ namaste,namaskar,namaskaram ~ hi ~ Namaste! 🙏
thanks ~ dhanyavad,shukriya ~ hi ~ Swagat hai! 😊
hello ~ konnichiwa,kon nichi wa ~ ja ~ Konnichiwa! 👋
morning ~ ohayo,ohayou,ohayo gozaimasu,ohayou gozaimasu ~ ja ~ Ohayō gozaimasu! ☀️
evening ~ konbanwa,konban wa ~ ja ~ Konbanwa! 🌆
night ~ oyasumi,oyasumi nasai ~ ja ~ Oyasumi nasai! 🌙
thanks ~ arigato,arigatou,arigato gozaimasu,arigatou gozaimasu ~ ja ~ Dō itashimashite! 😊
bye ~ sayonara,sayounara,ja ne,mata ne ~ ja ~ Sayōnara! 👋
hello ~ ni hao,nihao,ni hao ma ~ zh ~ Nǐ hǎo! 👋
bye ~ zaijian,zai jian ~ zh ~ Zàijiàn! 👋
thanks ~ xie xie,xiexie ~ zh ~ Bú kèqì! 😊
hello ~ annyeong,annyeonghaseyo,annyeong haseyo ~ ko ~ Annyeonghaseyo! 👋
thanks ~ kamsahamnida,gamsahamnida,gomawo ~ ko ~ Cheonmanyeyo! 😊
peace ~ shalom,shalom aleichem,shalom aleykhem ~ he ~ Shalom! 🕊️
hello ~ privet,zdravstvuyte,zdravstvuyte,zdrastvuyte ~ ru ~ Privet! 👋
morning ~ dobroe utro ~ ru ~ Dobroe utro! ☀️
thanks ~ spasibo,spasibo bolshoe ~ ru ~ Pozhaluysta! 😊
bye ~ do svidaniya,poka,do svidanya ~ ru ~ Do svidaniya! 👋
hello ~ merhaba,merhabalar ~ tr ~ Merhaba! 👋
morning ~ gunaydin ~ tr ~ Günaydın! ☀️
thanks ~ tesekkurler,tesekkur ederim,sag olun ~ tr ~ Rica ederim! 😊
hello ~ sawubona,sawubona mfowethu,yebo sawubona ~ zu ~ Yebo, sawubona! 👋
thanks ~ ngiyabonga,ngiyabonga kakhulu ~ zu ~ Wamukelekile! 😊
bye ~ hamba kahle,sala kahle ~ zu ~ Sala kahle! 👋
welcome ~ akwaaba,akwaba ~ ak ~ Medaase! 😊
thanks ~ medaase,medaase paa ~ ak ~ Yɛn ara! 😊
howareyou ~ oli otya,wasuze otya,osiibye otya ~ lg ~ Ngumu, weebale! Naawe oli otya?
thanks ~ webale,webale nyo,weebale ~ lg ~ Kale! 😊
hello ~ mbote,mbote na yo,mbote na bino ~ ln ~ Mbote! 👋
thanks ~ melesi,melesi mingi ~ ln ~ Bopesi! 😊
hello ~ aloha ~ haw ~ Aloha! 🌺
"""

_FILLER = set("""my dear friend friends there sir madam mister mr mrs miss everyone all guys team ai bot assistant kinyashield claude regis shield
mon ami amie cher chere tous toutes mwese bose wese rafiki yangu neza sana cyane very much so lot lots many beaucoup mille you u doing today going
tonight this toi boss bro sis buddy mate pal""".split())
_STOP = set("""what whats does do is are the a an word words phrase expression greeting greetings salutation salutations say mean means meaning meant of define definition
explain translate translation how to in
ni iki risobanura bisobanura isobanura bivuze bivuga ivuga ushaka kuvuga ibisobanuro bya
qu est ce que c quoi le la l mot veut dire signifie signification
maana ya neno inamaanisha nini eleza tafsiri
vous tu""".split())
_CUES = set("""mean means meaning meant explain define definition translate translation
risobanura bisobanura isobanura bivuze ibisobanuro signifie signification veut
maana inamaanisha eleza tafsiri""".split())
_OVERVIEW_WORDS = set("greeting greetings salutation salutations indamutso indamutso salamu".split())
_OVERVIEW_ALL = set("all types kinds list every ubwoko bwose liste tous toutes aina orodha zote".split())
_OVERVIEW_ORDER = ["hello", "morning", "afternoon", "evening", "night", "howareyou", "fine", "welcome", "nicemeet", "bye", "seeyou", "thanks", "youarewelcome",
                   "sorry", "please", "congrats", "birthday", "newyear", "christmas", "easter", "eid", "getwell", "goodluck", "travel", "niceday", "respect", "salam", "praise"]


def _key(tokens, drop):
    return tuple(t for t in tokens if t not in _FILLER and t not in drop)


def _load():
    rows = []
    for line in ROWS.strip().splitlines():
        f = [x.strip() for x in line.split(" ~ ")]
        if len(f) != 4:
            raise ValueError("bad greeting row: " + line[:50])
        kind, aliases, origin, reply = f
        if kind not in EQ or kind not in KIND or origin not in ORIGIN:
            raise ValueError("unknown kind/origin: " + line[:50])
        al = [a.strip() for a in aliases.split(",") if a.strip()]
        rows.append({"kind": kind, "aliases": al, "origin": origin, "reply": reply, "display": al[0].title() if origin in ("en", "fr", "rw", "sw", "es", "it", "de", "pt") else al[0].title()})
    return rows


ROWS_PARSED = _load()


def _display(row):
    return row["aliases"][0]


def _build_index():
    idx = {}
    for i, r in enumerate(ROWS_PARSED):
        for a in r["aliases"]:
            toks = fold(a).split()
            for drop in (frozenset(),):
                k = _key(toks, drop)
                if k:
                    idx.setdefault(k, i)
    return idx


_INDEX = _build_index()
# display names with proper capitals / accents for the first alias of each row (what the user typed is shown instead when available)


def count():
    return len(ROWS_PARSED)


def _segments(q):
    return [s for s in re.split(r"[,;!?.¡¿…]+|\band\b|\bet\b|\bna\b|\bkandi\b|\bpuis\b", q, flags=re.I) if s and s.strip()]


def _lookup(seg):
    """Return (row index, explain_only) for one segment, or None."""
    toks = fold(seg).split()
    if not toks or len(toks) > 8:
        return None
    k = _key(toks, frozenset())
    if k in _INDEX:
        return _INDEX[k], False
    k2 = _key(toks, _STOP)
    if k2 and k2 != k and k2 in _INDEX:
        return _INDEX[k2], True
    return None


def _explain_lines(row, typed):
    kind, origin = row["kind"], row["origin"]
    eq, kd = EQ[kind], KIND[kind]
    names = ORIGIN[origin]
    meta = {
        "en": "“{g}” — language: {o}. In English: “{m}”. ",
        "fr": "« {g} » — langue : {o}. En français : « {m} ». ",
        "rw": "“{g}” — ururimi: {o}. Mu Kinyarwanda: “{m}”. ",
        "sw": "“{g}” — lugha: {o}. Kwa Kiswahili: “{m}”. ",
    }
    out = []
    for n, l in enumerate(LANGS):
        out.append(f"- **{LANG_LABEL[l]}:** " + meta[l].format(g=typed, o=names[n], m=eq[n]) + kd[4 + n])
    return out


def _typed_display(seg, row):
    s = re.sub(r"\s+", " ", seg.strip().strip("!?.,;:¡¿"))
    return s[:1].upper() + s[1:] if s else _display(row).title()


_TITLE = {"en": "Greeting", "fr": "Salutation", "rw": "Indamutso", "sw": "Salamu"}
_LABEL_STEPS = {"en": "Try also", "fr": "Essayez aussi", "rw": "Gerageza no", "sw": "Jaribu pia"}
_STEP = {
    "en": "Greet me in any language, or ask \"what does Mwaramutse mean?\" or \"types of greetings\".",
    "fr": "Saluez-moi dans n'importe quelle langue, ou demandez « que signifie Mwaramutse ? » ou « types de salutations ».",
    "rw": "Ndamutse mu rurimi urwo ari rwo rwose, cyangwa ubaze uti \"Mwaramutse bisobanura iki?\" cyangwa \"ubwoko bw'indamutso\".",
    "sw": "Nisalimie kwa lugha yoyote, au uliza \"Mwaramutse ina maana gani?\" au \"aina za salamu\".",
}


def _overview(lang):
    k = lang if lang in LANGS else "en"
    ix = LANGS.index(k)
    head = {"en": "Greetings in English, French, Kinyarwanda and Swahili", "fr": "Salutations en anglais, français, kinyarwanda et swahili",
            "rw": "Indamutso mu Cyongereza, Igifaransa, Ikinyarwanda n'Igiswahili", "sw": "Salamu kwa Kiingereza, Kifaransa, Kinyarwanda na Kiswahili"}[k]
    lines = []
    for kind in _OVERVIEW_ORDER:
        eq = EQ[kind]
        title = KIND[kind][ix]
        lines.append(f"- **{title}** — " + " · ".join(f"{LANG_LABEL[l]}: {eq[n]}" for n, l in enumerate(LANGS)))
    tip = {"en": "Type any of them and I will reply and explain it in all four languages.", "fr": "Écrivez l'une d'elles et je répondrai en l'expliquant dans les quatre langues.",
           "rw": "Andika imwe muri zo nzagusubize kandi nyisobanure mu ndimi enye zose.", "sw": "Andika yoyote kati yao nitakujibu na kuieleza kwa lugha zote nne."}[k]
    return {"id": "greetings_overview", "title": {l: head for l in LANGS}, "answer": {l: head + ":\n\n" + "\n".join(lines) for l in LANGS},
            "steps": {l: [tip] for l in LANGS}, "steps_label": {l: _LABEL_STEPS[l] for l in LANGS}, "related": []}


def find(question, lang="en"):
    """Return a guide-shaped entry when the whole message is a greeting (or a request to explain one), else None."""
    q = (question or "").strip()
    if not q or len(q) > 70:
        return None
    toks = set(fold(q).split())
    if (toks & _OVERVIEW_WORDS) and (toks & _OVERVIEW_ALL) and len(toks) <= 8:
        return _overview(lang)
    if toks and toks <= (_OVERVIEW_WORDS | {"the", "my", "all", "les", "des", "des", "za", "ya"}) and toks & _OVERVIEW_WORDS:
        return _overview(lang)
    segs = _segments(q)
    if not segs or len(segs) > 3:
        return None
    found = []
    for s in segs:
        r = _lookup(s)
        if r is None:
            return None
        found.append((s, r[0], r[1]))
    seen, blocks, explain_only = set(), [], any(e for _, _, e in found)
    first = ROWS_PARSED[found[0][1]]
    for s, i, _e in found:
        row = ROWS_PARSED[i]
        typed = _typed_display(s, row) if not _e else row["aliases"][0].title()
        if (row["kind"], typed.lower()) in seen:
            continue
        seen.add((row["kind"], typed.lower()))
        blocks.append((typed, row))
    help_lang = first["origin"] if first["origin"] in LANGS else (lang if lang in LANGS else "en")
    k = lang if lang in LANGS else "en"
    parts = []
    if not explain_only:
        parts.append("**" + " ".join(row["reply"] for _t, row in blocks) + f"** {HELP[help_lang]}")
    for typed, row in blocks:
        parts.append("\n".join(_explain_lines(row, typed)))
    answer = "\n\n".join(parts)
    title = blocks[0][0] if len(blocks) == 1 else " · ".join(b[0] for b in blocks)
    return {"id": "greeting_" + re.sub(r"[^a-z0-9]+", "_", fold(title)).strip("_"), "title": {l: title for l in LANGS}, "answer": {l: answer for l in LANGS},
            "steps": {l: [_STEP[l]] for l in LANGS}, "steps_label": dict(_LABEL_STEPS), "related": []}
