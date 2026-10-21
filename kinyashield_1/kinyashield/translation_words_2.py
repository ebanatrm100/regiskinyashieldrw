"""More everyday words for the hand-written dictionary: food, animals, family, body, colours, numbers, time, places, transport, home, clothes,
verbs, feelings and a few more technology words. Same format as translation_words.py: English | French | Kinyarwanda | Kiswahili | note.
Alternatives inside one language are separated by " / " (the first is the main one). English verbs are written "to eat / eat" so both forms are found.
Kinyarwanda and Kiswahili are a DRAFT for review by fluent speakers. Where a word is only one of several common choices, the note says so."""

_RAW = """
# ---- food and drink ----
food and drink|nourriture et boissons|ibiryo n'ibinyobwa|chakula na vinywaji|
fruit|fruit|imbuto|tunda / matunda|
vegetable|légume|imboga|mboga|
banana|banane|igitoki / umuneke|ndizi|"igitoki" is the general word; "umuneke" is the small sweet banana.
apple|pomme|pome / pomu|tufaha|
orange|orange|icunga|chungwa|
mango|mangue|umwembe|embe|
avocado|avocat|avoka|parachichi|
pineapple|ananas|inanasi|nanasi|
tomato|tomate|inyanya|nyanya|
onion|oignon|igitunguru|kitunguu|
carrot|carotte|karoti|karoti|
cabbage|chou|ikibabi cya shu / shu|kabichi|
potato|pomme de terre|ikirayi / ibirayi|kiazi / viazi|
sweet potato|patate douce|igijumba / ibijumba|kiazi kitamu / viazi vitamu|
cassava|manioc|umumbati / imyumbati|muhogo|
beans|haricots|ibishyimbo|maharagwe|
maize / corn|maïs|ibigori|mahindi|
rice|riz|umuceri|mchele / wali|"mchele" is raw rice; "wali" is cooked rice.
bread|pain|umugati|mkate|
milk|lait|amata|maziwa|
meat|viande|inyama|nyama|
fish|poisson|ifi / amafi|samaki|
egg|œuf|igi / amagi|yai / mayai|
salt|sel|umunyu|chumvi|
sugar|sucre|isukari|sukari|
oil|huile|amavuta|mafuta|
tea|thé|icyayi|chai|
coffee|café|ikawa|kahawa|
beer|bière|byeri / inzoga|bia / pombe|
juice|jus|umutobe|juisi|
honey|miel|ubuki|asali|
meal|repas|ifunguro|mlo / chakula|
breakfast|petit-déjeuner|ifunguro rya mu gitondo|kifungua kinywa|
lunch|déjeuner|ifunguro rya saa sita|chakula cha mchana|
dinner|dîner|ifunguro rya nimugoroba|chakula cha jioni|
# ---- animals ----
animal|animal|inyamaswa / itungo|mnyama / wanyama|
cow|vache|inka|ng'ombe|
goat|chèvre|ihene|mbuzi|
sheep|mouton|intama|kondoo|
pig|cochon|ingurube|nguruwe|
chicken|poulet / poule|inkoko|kuku|
dog|chien|imbwa|mbwa|
cat|chat|injangwe|paka|
bird|oiseau|inyoni|ndege|
fish (animal)|poisson (animal)|ifi|samaki|
lion|lion|intare|simba|
elephant|éléphant|inzovu|tembo|
monkey|singe|inkende|tumbili / nyani|
gorilla|gorille|ingagi|sokwe / gorila|
snake|serpent|inzoka|nyoka|
rat / mouse|rat / souris|imbeba|panya|
bee|abeille|inzuki|nyuki|
# ---- family and people ----
family|famille|umuryango|familia|
mother|mère|mama / nyina|mama|
father|père|papa / se|baba|
parents|parents|ababyeyi|wazazi|
child|enfant|umwana|mtoto|
children|enfants|abana|watoto|
son|fils|umuhungu|mwana wa kiume|
daughter|fille (enfant)|umukobwa|mwana wa kike|
brother|frère|musaza / umuvandimwe|kaka / ndugu|
sister|sœur|mushiki / umuvandimwe|dada / ndugu|
grandmother|grand-mère|nyogokuru|bibi|
grandfather|grand-père|sogokuru|babu|
husband|mari|umugabo|mume|
wife|épouse / femme|umugore|mke|
friend|ami|inshuti|rafiki|
neighbour|voisin|umuturanyi|jirani|
man|homme|umugabo|mwanamume|
woman|femme|umugore|mwanamke|
boy|garçon|umuhungu|mvulana|
girl|fille|umukobwa|msichana|
baby|bébé|uruhinja / umwana muto|mtoto mchanga|
teacher|enseignant / enseignante|umwarimu|mwalimu|
doctor|médecin|umuganga / muganga|daktari|
nurse|infirmier / infirmière|umuforomo / umuforomokazi|muuguzi / nesi|
farmer|agriculteur|umuhinzi|mkulima|
driver|chauffeur|umushoferi|dereva|
police officer|policier|umupolisi|polisi / askari polisi|
soldier|soldat|umusirikare|askari|
pastor|pasteur|umupasiteri|mchungaji|
shopkeeper|commerçant|umucuruzi|mfanyabiashara / muuzaji|
# ---- body and health ----
body|corps|umubiri|mwili|
head|tête|umutwe|kichwa|
face|visage|mu maso|uso|
eye|œil|ijisho / amaso|jicho / macho|
ear|oreille|ugutwi / amatwi|sikio / masikio|
nose|nez|izuru|pua|
mouth|bouche|umunwa|mdomo|
tongue|langue (organe)|ururimi|ulimi|
tooth|dent|iryinyo / amenyo|jino / meno|
hair|cheveux|umusatsi / imisatsi|nywele|
neck|cou|ijosi|shingo|
arm|bras|ukuboko|mkono|
hand|main|ikiganza|kiganja / mkono|
finger|doigt|urutoki|kidole|
leg|jambe|ukuguru|mguu|
foot|pied|ikirenge|unyayo / mguu|
heart|cœur|umutima|moyo|
blood|sang|amaraso|damu|
stomach|ventre / estomac|inda|tumbo|
back|dos|umugongo|mgongo|
skin|peau|uruhu|ngozi|
bone|os|igufwa / amagufwa|mfupa / mifupa|
pain|douleur|ububabare / uburibwe|maumivu|
fever|fièvre|umuriro (w'umubiri)|homa|
cough|toux|inkorora|kikohozi|
medicine|médicament|imiti / umuti|dawa|
# ---- colours ----
colour|couleur|ibara|rangi|
red|rouge|umutuku|nyekundu|
blue|bleu|ubururu|buluu|
green|vert|icyatsi|kijani|
yellow|jaune|umuhondo|njano|
black|noir|umukara|nyeusi|
white|blanc|umweru|nyeupe|
# ---- numbers ----
zero|zéro|zeru|sifuri|
one|un|rimwe / kimwe|moja|
two|deux|kabiri|mbili|
three|trois|gatatu|tatu|
four|quatre|kane|nne|
five|cinq|gatanu|tano|
six|six|gatandatu|sita|
seven|sept|karindwi|saba|
eight|huit|umunani|nane|
nine|neuf|icyenda|tisa|
ten|dix|icumi|kumi|
twenty|vingt|makumyabiri|ishirini|
fifty|cinquante|mirongo itanu|hamsini|
hundred|cent|ijana|mia moja|
thousand|mille|igihumbi|elfu moja|
million|million|miliyoni|milioni|
# ---- time ----
time (hour)|heure|isaha|saa|
second|seconde|isegonda|sekunde|
minute|minute|umunota|dakika|
hour|heure (durée)|isaha|saa / saa moja|
day|jour|umunsi|siku|
night|nuit|ijoro|usiku|
morning|matin|igitondo / mu gitondo|asubuhi|
afternoon|après-midi|ku manywa / igicamunsi|mchana / alasiri|
evening|soir|nimugoroba|jioni|
today|aujourd'hui|uyu munsi|leo|
tomorrow|demain|ejo / ejo hazaza|kesho|"ejo" means both tomorrow and yesterday; the verb tense shows which.
yesterday|hier|ejo hashize / ejo|jana|
now|maintenant|ubu|sasa|
week|semaine|icyumweru|wiki|
month|mois|ukwezi|mwezi|
year|année / an|umwaka|mwaka|
Monday|lundi|kuwa mbere|Jumatatu|
Tuesday|mardi|kuwa kabiri|Jumanne|
Wednesday|mercredi|kuwa gatatu|Jumatano|
Thursday|jeudi|kuwa kane|Alhamisi|
Friday|vendredi|kuwa gatanu|Ijumaa|
Saturday|samedi|kuwa gatandatu|Jumamosi|
Sunday|dimanche|ku cyumweru|Jumapili|
January|janvier|Mutarama|Januari|
February|février|Gashyantare|Februari|
March|mars|Werurwe|Machi|
April|avril|Mata|Aprili|
May|mai|Gicurasi|Mei|
June|juin|Kamena|Juni|
July|juillet|Nyakanga|Julai|
August|août|Kanama|Agosti|
September|septembre|Nzeri|Septemba|
October|octobre|Ukwakira|Oktoba|
November|novembre|Ugushyingo|Novemba|
December|décembre|Ukuboza|Desemba|
# ---- places and nature ----
house|maison|inzu|nyumba|
home|maison (chez soi)|urugo / iwacu|nyumbani|
village|village|umudugudu|kijiji|
city|ville|umujyi|mji / jiji|
country|pays|igihugu|nchi|
road|route|umuhanda|barabara|
river|rivière / fleuve|uruzi / umugezi|mto|
lake|lac|ikiyaga|ziwa|
mountain|montagne|umusozi / umusozi muremure|mlima|
forest|forêt|ishyamba|msitu|
sea|mer|inyanja|bahari|
sun|soleil|izuba|jua|
moon|lune|ukwezi|mwezi|
star|étoile|inyenyeri|nyota|
sky|ciel|ijuru / ikirere|anga / mbingu|
wind|vent|umuyaga|upepo|
fire|feu|umuriro|moto|
tree|arbre|igiti|mti|
flower|fleur|ururabo / ururabyo|ua / maua|
grass|herbe|ubwatsi|nyasi|
stone|pierre|ibuye|jiwe|
air|air|umwuka|hewa|
garden / field|jardin / champ|umurima|bustani / shamba|
church|église|itorero / kiliziya|kanisa|
mosque|mosquée|umusigiti|msikiti|
shop|boutique|iduka|duka|
restaurant|restaurant|resitora|mkahawa|
hotel|hôtel|hoteli|hoteli|
airport|aéroport|ikibuga cy'indege|uwanja wa ndege|
bus station|gare routière|gare|kituo cha basi|
# ---- transport ----
bus|bus|bisi|basi|
car|voiture|imodoka|gari / motokaa|
bicycle|vélo|igare|baiskeli|
motorbike|moto|moto|pikipiki|
plane|avion|indege|ndege|
train|train|gari ya moshi|treni / gari la moshi|
boat|bateau|ubwato|mashua / boti|
ticket|billet|itike|tiketi|
bag|sac|umufuka / isakoshi|mfuko / begi|
# ---- clothes and home ----
clothes|vêtements|imyenda|nguo|
shirt|chemise|ishati|shati|
trousers|pantalon|ipantaro|suruali|
dress|robe|ikanzu|gauni|
shoes|chaussures|inkweto|viatu|
hat|chapeau|ingofero|kofia|
door|porte|urugi / umuryango|mlango|
window|fenêtre|idirishya|dirisha|
table|table|ameza / meza|meza|
chair|chaise|intebe|kiti|
bed|lit|uburiri / igitanda|kitanda|
kitchen|cuisine|igikoni|jiko|
knife|couteau|icyuma|kisu|
spoon|cuillère|ikiyiko|kijiko|
plate|assiette|isahani|sahani|
cup|tasse|igikombe|kikombe|
bottle|bouteille|icupa|chupa|
soap|savon|isabune|sabuni|
book|livre|igitabo|kitabu|
pen|stylo|ikaramu|kalamu|
paper|papier|urupapuro / impapuro|karatasi|
letter|lettre|ibaruwa|barua|
newspaper|journal|ikinyamakuru|gazeti|
radio|radio|radiyo|redio|
television|télévision|televiziyo|televisheni|
# ---- verbs ----
to eat / eat|manger|kurya|kula|
to drink / drink|boire|kunywa|kunywa|
to sleep / sleep|dormir|kuryama / gusinzira|kulala|
to walk / walk|marcher|kugenda n'amaguru|kutembea|
to run / run|courir|kwiruka|kukimbia|
to come / come|venir|kuza|kuja|
to go / go|aller|kujya / kugenda|kwenda|
to give / give|donner|guha / gutanga|kupa / kutoa|
to take / take|prendre|gufata|kuchukua|
to see / see|voir|kubona|kuona|
to hear / hear|entendre|kumva|kusikia|
to speak / speak|parler|kuvuga|kuzungumza / kusema|
to love / love|aimer|gukunda|kupenda|
to want / want|vouloir|gushaka|kutaka|
to know / know|savoir / connaître|kumenya|kujua|
to think / think|penser|gutekereza|kufikiri|
to work / work|travailler|gukora|kufanya kazi|
to play / play|jouer|gukina|kucheza|
to buy / buy|acheter|kugura|kununua|
to sell / sell|vendre|gucuruza / kugurisha|kuuza|
to open / open|ouvrir|gufungura|kufungua|
to close / close|fermer|gufunga|kufunga|
to help / help|aider|gufasha|kusaidia|
to wait / wait|attendre|gutegereza|kusubiri|
to live / live|vivre / habiter|gutura / kubaho|kuishi|
to die / die|mourir|gupfa|kufa|
to sit / sit|s'asseoir|kwicara|kukaa|
to stand / stand|se tenir debout|guhagarara|kusimama|
to wake up / wake up|se réveiller|gukanguka|kuamka|
to laugh / laugh|rire|guseka|kucheka|
to cry / cry|pleurer|kurira|kulia|
to sing / sing|chanter|kuririmba|kuimba|
to dance / dance|danser|kubyina|kucheza ngoma|
to send / send|envoyer|kohereza|kutuma|
to receive / receive|recevoir|kwakira|kupokea|
to share / share|partager|gusangiza|kushiriki|
to remember / remember|se souvenir|kwibuka|kukumbuka|
to clean / clean|nettoyer|gusukura|kusafisha|
to pray / pray|prier|gusenga|kuomba / kusali|
to download / download|télécharger|gukurura / gukuramo|kupakua|
to upload / upload|téléverser|gushyiraho / kohereza|kupakia|
to delete / delete|supprimer|gusiba|kufuta|
to block / block|bloquer|guhagarika / kubuza|kuzuia|
to report / report (verb)|signaler|kumenyekanisha|kuripoti|
to open an account|ouvrir un compte|gufungura konti|kufungua akaunti|
to log in / log in|se connecter|kwinjira muri konti|kuingia kwenye akaunti|
# ---- feelings, qualities and ideas ----
good|bon / bien|byiza / -iza|nzuri / vizuri|"Byiza" changes its first letter with the noun it describes in Kinyarwanda.
bad|mauvais|bibi / -bi|mbaya / vibaya|
love (noun)|amour|urukundo|upendo|
peace|paix|amahoro|amani|
war|guerre|intambara|vita|
freedom|liberté|ubwisanzure / ubwigenge|uhuru|
truth|vérité|ukuri|ukweli|
lie (untruth)|mensonge|ikinyoma|uongo|
hope|espoir|ibyiringiro|matumaini|
God|Dieu|Imana|Mungu|
joy|joie|ibyishimo|furaha|
fear|peur|ubwoba|hofu|
help (noun)|aide|ubufasha|msaada|
work (noun)|travail|akazi|kazi|
gift|cadeau|impano|zawadi|
prize|prix|igihembo|zawadi / tuzo|
luck|chance|amahirwe|bahati|
name|nom|izina|jina|
word|mot|ijambo / amagambo|neno / maneno|
language|langue|ururimi / indimi|lugha|
question|question|ikibazo|swali|
answer|réponse|igisubizo|jibu|
problem|problème|ikibazo / ingorane|tatizo / shida|
song|chanson|indirimbo|wimbo|
music|musique|umuziki|muziki|
game|jeu|umukino|mchezo|
football|football|umupira w'amaguru|mpira wa miguu|
# ---- more technology and online words ----
cyberattack|cyberattaque|igitero cyo kuri interineti|shambulio la mtandaoni|
cybercrime|cybercriminalité|ibyaha byo kuri interineti|uhalifu wa mtandaoni|
data protection|protection des données|kurinda amakuru|ulinzi wa data|
social media|réseaux sociaux|imbuga nkoranyambaga|mitandao ya kijamii|
online|en ligne|kuri interineti|mtandaoni|
offline|hors ligne|nta interineti|nje ya mtandao|
website address|adresse du site|aderesi y'urubuga|anwani ya tovuti|
data|données|amakuru / data|data / taarifa|
"""


def _rows():
    out = []
    for line in _RAW.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4 or not all(parts[:4]):
            continue
        parts += [""] * (5 - len(parts))
        out.append(tuple(parts[:5]))
    return out


WORDS = _rows()
