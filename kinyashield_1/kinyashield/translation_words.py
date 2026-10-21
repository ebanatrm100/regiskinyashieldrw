"""Word and short-phrase dictionary: English | French | Kinyarwanda | Kiswahili | note (optional).
One entry per line, fields separated by "|", alternatives inside one language separated by " / " (the first is the main one).
Used by translate_db (exact lookups from any of the four languages into any other) and for the word-by-word breakdown of a sentence that is not in the bank.
Kinyarwanda and Kiswahili are a DRAFT written for review by fluent speakers; where speakers normally keep the English or French word, that word is given."""

_RAW = """
# ---- pronouns and question words (Kinyarwanda and Kiswahili words change with the noun they go with; the note says so) ----
I|je / moi|njye|mimi|
you|tu / toi / vous|wowe / uri|wewe|"muri / mwe" is the polite or plural "you" in Kinyarwanda; "ninyi" is plural in Kiswahili.
he / she|il / elle|we|yeye|Kinyarwanda and Kiswahili do not mark he or she.
we|nous|twe / turi|sisi|
they|ils / elles|bo / bari|wao|
my|mon / ma / mes|-anjye (for example izina ryanjye)|-angu (for example jina langu)|The ending changes with the word it goes with.
your|ton / ta / tes / votre|-awe (for example izina ryawe)|-ako (for example jina lako, simu yako)|The ending changes with the word it goes with.
our|notre / nos|-acu (for example izina ryacu)|-etu (for example jina letu)|The ending changes with the word it goes with.
who|qui|nde|nani|
what|quoi / que|iki|nini|
which|quel / lequel|-he (uwuhe, iyihe, ikihe)|-pi (yupi, ipi, upi)|The ending changes with the word it goes with.
whose|à qui|uwa nde / icya nde|wa nani / ya nani|
where|où|he|wapi|
when|quand|ryari|lini|
why|pourquoi|kuki / kubera iki|kwa nini / mbona|
how|comment|ute / gute|vipi / jinsi gani|
this|ce / cet / cette / ceci|uyu / iki / ibi / uru|huyu / hii / hiki / huu|The form changes with the word it goes with.
that|ce / cela|uwo / icyo / ibyo|huyo / hiyo / hicho|
and|et|na / kandi|na / pamoja na|
or|ou|cyangwa|au / ama|
but|mais|ariko|lakini / ila|
because|parce que|kubera ko / kuko|kwa sababu / kwa kuwa|
if|si|niba|kama / ikiwa|
not|ne ... pas / pas|nta- / ntabwo|si / hapana|
yes|oui|yego|ndiyo / ndio|
no|non|oya|hapana|
with|avec|na / hamwe na|na / pamoja na|
without|sans|nta / udafite|bila|
for|pour|kuri / kugira ngo|kwa / kwa ajili ya|
from|de / depuis|kuva|kutoka|
to|à / vers|kuri / ku|kwa / hadi|
in|dans / en|mu|katika / ndani ya|
on|sur|ku|juu ya / kwenye|
all|tout / tous|byose / bose|yote / wote|
some|quelques / certains|bimwe / bamwe|baadhi ya|
many|beaucoup / nombreux|byinshi / benshi|mengi / wengi|
few|peu|bike / bake|machache / wachache|
more|plus|byinshi / ibindi|zaidi|
less|moins|bike|pungufu / kidogo|
other|autre|ikindi / undi|nyingine / mwingine|
every|chaque|buri|kila|
only|seulement / seul|gusa|tu / peke yake|
also|aussi|na none / nanone|pia / vilevile|
again|encore / de nouveau|kandi / nanone / subira|tena|
already|déjà|bimaze|tayari|
still|encore / toujours|haracyari / n'ubu|bado|
very|très|cyane|sana|
please|s'il vous plaît|nyabuneka / mbijeje|tafadhali|
sorry|désolé|ihangane / mbabarira|samahani / pole|
thanks|merci|murakoze|asante|
welcome|bienvenue|murakaza neza|karibu|
hello|bonjour / salut|muraho / mwaramutse|hujambo / habari|
goodbye|au revoir|murabeho / tuzahurira|kwaheri|

# ---- the assistant and owners ----
owner|propriétaire|nyiri / nyirubwite (for example nyir'inzu = house owner)|mmiliki / mwenyewe|"nyirawe" means "his / her / its owner".
to own|posséder / être propriétaire de|gutunga / kuba nyiri|kumiliki|
master|maître|shebuja / databuja|bwana / bosi|
creator|créateur|uwaremye / uwakoze|muumbaji / mtengenezaji|
developer|développeur|uwakoze porogaramu|msanidi programu / msanidi|
engineer|ingénieur|injeniyeri|mhandisi|
specialist|spécialiste|inzobere|mtaalamu|
expert|expert|inzobere|mtaalamu / mbobezi|
assistant|assistant|umufasha|msaidizi|
robot|robot|robo|roboti|
artificial intelligence|intelligence artificielle|ubwenge buhangano / AI|akili bandia / akili unde|

# ---- computers and devices ----
computer|ordinateur|mudasobwa|kompyuta|
laptop|ordinateur portable|mudasobwa igendanwa / laptop|kompyuta mpakato / laptop|
tablet|tablette|tablette|kishikwambi / tableti|
smartphone|smartphone / téléphone intelligent|telefone igezweho / smartphone|simu janja / simu ya kisasa|
phone|téléphone|telefone|simu|
mobile phone|téléphone portable|telefone igendanwa|simu ya mkononi|
screen|écran|ecran|skrini|
keyboard|clavier|clavier / kibodi|kibodi|
mouse|souris|souris|kipanya|
printer|imprimante|imashini isohora / printer|printa / kichapishi|
battery|batterie|batiri|betri|
charger|chargeur|chargeur|chaja|
device|appareil|igikoresho|kifaa|
hardware|matériel informatique|ibikoresho bya mudasobwa|maunzi|
software|logiciel|porogaramu|programu|
application|application|porogaramu|programu / programu tumizi|
app|appli|porogaramu|programu|
program|programme|porogaramu|programu|
system|système|sisitemu|mfumo|
operating system|système d'exploitation|sisitemu y'imikorere|mfumo endeshi|
server|serveur|seriveri|seva|
data|données|amakuru / data|data / takwimu / taarifa|
database|base de données|ububiko bw'amakuru|hifadhidata|
storage|stockage|ububiko|hifadhi|
memory|mémoire|ububiko bw'agateganyo (RAM) / kwibuka|kumbukumbu|
file|fichier|dosiye|faili|
folder|dossier|ububiko bwa dosiye / dosiye|folda / saraka|
document|document|inyandiko|hati / waraka|
photo|photo|ifoto|picha|
video|vidéo|video|video|
image|image|ishusho|picha / taswira|
sound|son|ijwi / amajwi|sauti|
camera|caméra|kamera|kamera|
microphone|microphone|mikoro|maikrofoni|
network|réseau|umuyoboro / network|mtandao|
internet|internet|interineti|intaneti / mtandao|
Wi-Fi|Wi-Fi|WiFi|WiFi|
website|site web|urubuga rwa interineti|tovuti|
web page|page web|paji ya interineti|ukurasa wa tovuti|
browser|navigateur|mushakisha / browser|kivinjari|
search|recherche|gushakisha / ishakisha|utafutaji / kutafuta|
link|lien|link / umurongo|kiungo|
email|courriel / e-mail|imeri|barua pepe|
message|message|ubutumwa|ujumbe|
text message|SMS / message texte|ubutumwa bugufi (SMS)|ujumbe mfupi (SMS)|
call|appel|guhamagara / telefone|simu / kupiga simu|
contact|contact|umuntu mushakira / contact|mawasiliano / mtu wa mawasiliano|
account|compte|konti|akaunti|
user|utilisateur|ukoresha / umukoresha|mtumiaji|
administrator|administrateur|umuyobozi wa sisitemu|msimamizi|
profile|profil|umwirondoro|wasifu|
settings|paramètres|igenamiterere|mipangilio|
menu|menu|menu|menyu|
button|bouton|buto|kitufe|
icon|icône|ishusho ntoya (icon)|ikoni|
notification|notification|imenyesha|arifa|
update|mise à jour|ivugurura|sasisho|
version|version|verisiyo|toleo|
install|installer|gushyiraho porogaramu|kusakinisha|
copy|copie|kopi|nakala|
backup|sauvegarde|kopi y'ubwirinzi|nakala rudufu|
digital|numérique|ry'ikoranabuhanga / digitale|dijitali|
technology|technologie|ikoranabuhanga|teknolojia|
code|code|kode|msimbo|
programming|programmation|gukora porogaramu|upangaji programu|
website address|adresse du site|aderesi y'urubuga|anwani ya tovuti|
cloud|cloud / nuage|igicu (cloud)|wingu|
connection|connexion|ihuza / connexion|muunganisho|
signal|signal|ikimenyetso / signal|mawimbi|
speed|vitesse|umuvuduko|kasi|
memory card|carte mémoire|ikarita y'ububiko|kadi ya kumbukumbu|
flash drive|clé USB|flash|flash|

# ---- cybersecurity ----
security|sécurité|umutekano|usalama|
cybersecurity|cybersécurité|umutekano wa interineti|usalama wa mtandao|
safety|sûreté / sécurité|umutekano|usalama|
safe|sûr / en sécurité|butekanye / -tekanye|salama|
dangerous|dangereux|biteje akaga / bibi|hatari|
danger|danger|akaga|hatari|
risk|risque|ingaruka / ibyago|hatari / hatari ya madhara|
threat|menace|iterabwoba|tishio|
attack|attaque|igitero|shambulio|
attacker|attaquant|uwagabye igitero|mshambuliaji|
hacker|pirate informatique / hacker|hakeri / uwinjira mu mudasobwa nta ruhushya|mdukuzi / hakeri|
hacking|piratage|ukwinjira mu mudasobwa nta ruhushya|udukuzi|
hacked|piraté|yinjiwemo n'abagizi ba nabi|imedukuliwa|
password|mot de passe|ijambo ry'ibanga|nenosiri|
PIN|code PIN|PIN / umubare w'ibanga|PIN / nambari ya siri|
one-time code|code à usage unique|kode ikoreshwa rimwe|msimbo wa mara moja|
username|nom d'utilisateur|izina ry'ukoresha|jina la mtumiaji|
login|connexion|kwinjira|kuingia|
logout|déconnexion|gusohoka|kutoka|
two-factor authentication|authentification à deux facteurs|kwemeza kabiri|uthibitishaji wa hatua mbili|
authentication|authentification|kwemeza uwo uri we|uthibitishaji|
verification|vérification|igenzura / kugenzura|uthibitisho|
identity|identité|umwirondoro|utambulisho|
ID card|carte d'identité|indangamuntu|kitambulisho|
permission|autorisation|uruhushya|ruhusa|
access|accès|kwinjira / uburenganzira bwo kwinjira|ufikiaji|
virus|virus|virusi|virusi|
antivirus|antivirus|porogaramu irwanya virusi|kinga-virusi|
malware|logiciel malveillant|porogaramu y'ubugizi bwa nabi (malware)|programu hasidi|
ransomware|rançongiciel|ransomware / porogaramu ifunga amakuru igasaba incungu|programu ya kikombozi|
spyware|logiciel espion|spyware / porogaramu ikurikirana rwihishwa|programu ya upelelezi|
phishing|hameçonnage|phishing / uburiganya bwo gushuka kuri interineti|ulaghai wa kuvizia taarifa (phishing)|
scam|arnaque|ubutekamutwe|ulaghai / utapeli|
scammer|escroc|umutekamutwe|tapeli / mlaghai|
fraud|fraude|uburiganya|ulaghai / udanganyifu|
fraudster|fraudeur|umuriganya|mlaghai|
thief|voleur|umujura|mwizi|
theft|vol|ubujura|wizi|
spam|spam / courrier indésirable|spam / ubutumwa butakenewe|barua taka|
fake|faux|igihimbano / -a ibinyoma|bandia / feki|
suspicious|suspect|bikemangwa|ya kutia shaka|
trust|confiance|icyizere / kwizera|imani / kuamini|
privacy|vie privée|ibanga ry'umuntu|faragha|
confidential|confidentiel|ibanga|siri / ya siri|
secret|secret|ibanga|siri|
encryption|chiffrement|ubwihisho bw'amakuru (encryption)|usimbaji fiche|
firewall|pare-feu|firewall / urukuta rurinda umuyoboro|ngome ya mtandao (firewall)|
VPN|VPN|VPN|VPN|
vulnerability|vulnérabilité|intege nke (z'ubwirinzi)|udhaifu|
patch|correctif|igikosora (patch)|kiraka / sasisho la usalama|
breach|violation de données / fuite|kumeneka kw'amakuru / kwinjirwamo|uvunjaji wa usalama|
data breach|fuite de données|kumeneka kw'amakuru|uvujaji wa data|
leak|fuite|kumeneka|kuvuja|
identity theft|usurpation d'identité|kwiba umwirondoro|wizi wa utambulisho|
impersonation|usurpation|kwiyitirira undi muntu|kujifanya mtu mwingine|
blackmail|chantage|iterabwoba ry'amafaranga|vitisho vya kudai pesa|
extortion|extorsion|kwambura abantu amafaranga ku ngufu|kunyang'anya kwa vitisho|
backup|sauvegarde|kopi y'ubwirinzi|nakala rudufu|
protect|protéger|kurinda|kulinda|
protection|protection|uburinzi|ulinzi|
defence|défense|ubwirinzi|ulinzi|
detection|détection|kumenya / igenzura|ugunduzi|
prevention|prévention|kwirinda|kuzuia|
incident|incident|ibyabaye / ikibazo cy'umutekano|tukio la usalama|
response|réponse|igisubizo / uko bikemurwa|mwitikio|
recovery|récupération / rétablissement|gusubiza uko byari bimeze|urejeshaji|
policy|politique|politiki|sera|
rule|règle|itegeko|kanuni|
law|loi|itegeko|sheria|
evidence|preuve|ibimenyetso|ushahidi|
report|signalement / rapport|raporo / kumenyekanisha|ripoti|
alert|alerte|impuruza|tahadhari|
warning|avertissement|umuburo|onyo|
awareness|sensibilisation|ubukangurambaga|uhamasishaji|
training|formation|amahugurwa|mafunzo|
staff|personnel|abakozi|wafanyakazi|
student|élève / étudiant|umunyeshuri|mwanafunzi|
secure|sécurisé|birinzwe / bifite umutekano|salama / iliyolindwa|
unsafe|dangereux / non sécurisé|butatekanye|si salama|
lock|verrou / cadenas|ingufuri|kufuli|
key|clé|urufunguzo|ufunguo|
to hack|pirater|kwinjira mu mudasobwa nta ruhushya|kudukua|
to steal|voler|kwiba|kuiba|
to scam|escroquer|gutekera umutwe|kutapeli / kulaghai|
to trick|tromper|gushuka|kudanganya|
to protect|protéger|kurinda|kulinda|
to encrypt|chiffrer|guhisha amakuru|kusimba fiche|
to verify|vérifier|kugenzura|kuthibitisha|
to confirm|confirmer|kwemeza|kuthibitisha|
to suspect|soupçonner|gukeka|kushuku|
to avoid|éviter|kwirinda|kuepuka|
to detect|détecter|kumenya / kubona|kugundua|
to log out|se déconnecter|gusohoka|kutoka|
to install|installer|gushyiraho|kusakinisha|
to update|mettre à jour|kuvugurura|kusasisha|
to save|enregistrer / sauvegarder|kubika|kuhifadhi|
to search|chercher / rechercher|gushakisha|kutafuta|
to type|taper|kwandika (kuri clavier)|kuandika / kuchapa|
to print|imprimer|gusohora / kuprinta|kuchapisha / kuprinta|
to copy|copier|gukopera|kunakili|
to paste|coller|gushyira ibyakopowe|kubandika|
to connect|connecter|guhuza|kuunganisha|
to disconnect|déconnecter|gutandukanya|kukatisha muunganisho|
to turn on|allumer|gucana / gufungura|kuwasha|
to turn off|éteindre|kuzimya|kuzima|
to restart|redémarrer|gutangira bundi bushya|kuwasha upya|
to charge|charger|gushyira umuriro (muri telefone)|kuchaji|

# ---- money and banking ----
bank|banque|banki|benki|
bank account|compte bancaire|konti ya banki|akaunti ya benki|
money|argent|amafaranga|pesa / fedha|
cash|espèces|amafaranga y'intoki|pesa taslimu|
card|carte|ikarita|kadi|
credit card|carte de crédit|ikarita y'inguzanyo|kadi ya mkopo|
debit card|carte de débit|ikarita ya banki|kadi ya malipo|
loan|prêt|inguzanyo|mkopo|
interest|intérêt|inyungu|riba|
payment|paiement|kwishyura / ubwishyu|malipo|
fee|frais|amafaranga yo kwishyura (frais)|ada|
price|prix|igiciro|bei|
cost|coût|igiciro|gharama|
receipt|reçu|inyemezabwishyu|risiti|
invoice|facture|fagitire|ankara|
balance|solde|amafaranga asigaye kuri konti|salio|
transfer|transfert / virement|kohereza amafaranga|uhamisho|
withdrawal|retrait|kubikuza|kutoa pesa|
deposit|dépôt|kubitsa|amana / kuweka pesa|
savings|épargne|ubwizigame|akiba|
debt|dette|umwenda|deni|
tax|impôt|umusoro|kodi|
income|revenu|amafaranga winjiza|mapato|
salary|salaire|umushahara|mshahara|
profit|bénéfice|inyungu|faida|
loss|perte|igihombo|hasara|
budget|budget|ingengo y'imari|bajeti|
insurance|assurance|ubwishingizi|bima|
mobile money|argent mobile|mobile money|pesa za simu / M-Pesa|
exchange rate|taux de change|igipimo cy'ivunjisha|kiwango cha ubadilishaji|
to pay|payer|kwishyura|kulipa|
to borrow|emprunter|kuguza|kukopa|
to lend|prêter|guha inguzanyo / kuguriza|kukopesha|
to save money|économiser|kuzigama|kuweka akiba|
to spend|dépenser|gukoresha amafaranga|kutumia pesa|
to withdraw|retirer|kubikuza|kutoa|
to deposit|déposer|kubitsa|kuweka|
to transfer|transférer|kohereza|kuhamisha|

# ---- school and work ----
school|école|ishuri|shule|
class|classe|ishuri / icyiciro|darasa|
lesson|leçon|isomo|somo|
exam|examen|ikizamini|mtihani|
test|test / contrôle|isuzuma|jaribio|
homework|devoirs|umukoro|kazi ya nyumbani|
grade|note|amanota|alama / daraja|
certificate|certificat|icyemezo|cheti|
degree|diplôme|impamyabumenyi|shahada|
knowledge|connaissance|ubumenyi|maarifa|
education|éducation|uburezi / uburere|elimu|
research|recherche|ubushakashatsi|utafiti|
science|science|ubumenyi bw'ubuhanga (science)|sayansi|
mathematics|mathématiques|imibare|hisabati|
history|histoire|amateka|historia|
geography|géographie|ubumenyi bw'isi (geography)|jiografia|
library|bibliothèque|isomero|maktaba|
university|université|kaminuza|chuo kikuu|
job|emploi / travail|akazi|kazi|
employee|employé|umukozi|mfanyakazi|
employer|employeur|umukoresha|mwajiri|
manager|directeur / responsable|umuyobozi|meneja|
company|entreprise|ikigo / sosiyete|kampuni|
business|affaires / commerce|ubucuruzi|biashara|
trader|commerçant|umucuruzi|mfanyabiashara|
market|marché|isoko|soko|
customer|client|umukiriya|mteja|
meeting|réunion|inama|mkutano|
project|projet|umushinga|mradi|
report|rapport|raporo|ripoti|
plan|plan|igenamigambi / gahunda|mpango|
schedule|horaire / programme|gahunda|ratiba|
deadline|date limite|itariki ntarengwa|tarehe ya mwisho|
salary|salaire|umushahara|mshahara|
interview|entretien|ikiganiro cyo gushaka akazi (interview)|usaili|
application letter|lettre de candidature|ibaruwa isaba akazi|barua ya maombi ya kazi|
CV|CV|CV|wasifu (CV)|
cooperative|coopérative|koperative|ushirika / chama cha ushirika|
to study|étudier|kwiga|kusoma|
to teach|enseigner|kwigisha|kufundisha|
to learn|apprendre|kwiga|kujifunza|
to practise|pratiquer / s'entraîner|kwitoza|kufanya mazoezi|
to write|écrire|kwandika|kuandika|
to read|lire|gusoma|kusoma|
to count|compter|kubara|kuhesabu|
to calculate|calculer|kubara|kukokotoa|
to solve|résoudre|gukemura|kutatua|
to explain|expliquer|gusobanura|kueleza|
to translate|traduire|guhindura (mu rundi rurimi)|kutafsiri|
to ask|demander|kubaza|kuuliza|
to answer|répondre|gusubiza|kujibu|
to choose|choisir|guhitamo|kuchagua|
to decide|décider|gufata icyemezo|kuamua|
to start|commencer|gutangira|kuanza|
to finish|finir|kurangiza|kumaliza|
to try|essayer|kugerageza|kujaribu|
to change|changer|guhindura|kubadilisha|
to build|construire|kubaka|kujenga|
to create|créer|kurema / gukora|kuunda / kutengeneza|
to use|utiliser|gukoresha|kutumia|
to need|avoir besoin de|gukenera|kuhitaji|
to find|trouver|kubona / gusanga|kupata / kutafuta|
to lose|perdre|gutakaza / kubura|kupoteza|
to win|gagner|gutsinda|kushinda|
to look|regarder|kureba|kuangalia|
to bring|apporter|kuzana|kuleta|
to put|mettre|gushyira|kuweka|
to keep|garder|kubika / kugumana|kuweka / kuhifadhi|
to follow|suivre|gukurikira|kufuata|
to show|montrer|kwereka|kuonyesha|
to tell|dire / raconter|kubwira|kuambia|
to call someone|appeler|guhamagara|kupigia simu|
to meet|rencontrer|guhura|kukutana|
to visit|visiter|gusura|kutembelea|
to travel|voyager|gutembera / kugenda|kusafiri|
to arrive|arriver|kugera|kufika|
to leave|partir|kugenda / kuva|kuondoka|
to return|revenir / rendre|kugaruka / gusubiza|kurudi / kurudisha|
to begin|commencer|gutangira|kuanza|
to stop|arrêter|guhagarara / guhagarika|kuacha / kusimamisha|
to continue|continuer|gukomeza|kuendelea|
to forget|oublier|kwibagirwa|kusahau|
to believe|croire|kwemera / kwizera|kuamini|
to hope|espérer|kwiringira / kwizera|kutumaini|
to feel|ressentir|kumva|kuhisi|
to wash|laver|kwoza|kuosha|
to cook|cuisiner|guteka|kupika|
to plant|planter|guhinga / gutera|kupanda|
to harvest|récolter|gusarura|kuvuna|

# ---- adjectives and everyday words ----
easy|facile|byoroshye|rahisi|
difficult|difficile|bigoye|ngumu / vigumu|
fast|rapide|byihuta|haraka|
slow|lent|bitinda / buhoro|polepole|
cheap|bon marché|bihendutse|nafuu|
expensive|cher|bihenze|ghali|
free|gratuit / libre|ubuntu / ku buntu|bure|
true|vrai|ukuri|kweli / ya kweli|
false|faux|ibinyoma|uongo|
correct|correct|ni byo / byuzuye neza|sahihi|
wrong|faux / incorrect|si byo / ikosa|si sahihi / makosa|
right|droite / droit|iburyo / uburenganzira|kulia / haki|
left|gauche|ibumoso|kushoto|
important|important|by'ingenzi|muhimu|
urgent|urgent|byihutirwa|ya dharura|
ready|prêt|byiteguye|tayari|
open|ouvert|bifunguye|wazi|
closed|fermé|bifunze|imefungwa|
full|plein|byuzuye|imejaa|
empty|vide|ubusa / bidafite ikintu|tupu|
hot|chaud|bishyushye|moto|
cold|froid|bikonje|baridi|
clean|propre|bisukuye|safi|
dirty|sale|byanduye|chafu|
strong|fort|bikomeye|imara / nguvu|
weak|faible|bitagira imbaraga / byoroshye|dhaifu|
young|jeune|muto|mdogo / kijana|
old|vieux|ushaje / mukuru|mzee / kuukuu|
beautiful|beau / belle|byiza / mwiza|nzuri / -zuri|
happy|content / heureux|ndishimye / yishimye|furaha / mwenye furaha|
sad|triste|biteye agahinda|huzuni / -enye huzuni|
angry|en colère|arakaye|hasira / -enye hasira|
alone|seul|wenyine|peke yake|
together|ensemble|hamwe|pamoja|
right now|maintenant|ubu nonaha|sasa hivi|
soon|bientôt|vuba|hivi karibuni|
early|tôt|kare|mapema|
late|tard|bitinze / nyuma|kuchelewa / marehemu|
first|premier|uwa mbere|wa kwanza|
last|dernier|uwa nyuma|wa mwisho|
next|prochain|ukurikira|ijayo / inayofuata|
new|nouveau|gishya / mushya|mpya|
always|toujours|buri gihe|daima / kila mara|
sometimes|parfois|rimwe na rimwe|wakati mwingine|
often|souvent|kenshi|mara nyingi|
never|jamais|ntabwo / ntibigera|kamwe / hapana kamwe|
nothing|rien|nta kintu|hakuna kitu|
everything|tout|byose|kila kitu|
someone|quelqu'un|umuntu|mtu fulani|
something|quelque chose|ikintu|kitu fulani|
nobody|personne|ntawe|hakuna mtu|
everyone|tout le monde|bose|kila mtu / wote|
here|ici|hano|hapa|
there|là|aho / hariya|pale|
near|près|hafi|karibu|
far|loin|kure|mbali|
up|en haut|hejuru|juu|
down|en bas|hasi|chini|
inside|dedans|imbere / mu|ndani|
outside|dehors|hanze|nje|
front|devant|imbere|mbele|
behind|derrière|inyuma|nyuma|
between|entre|hagati|kati ya|
under|sous|munsi|chini ya|
above|au-dessus|hejuru ya|juu ya|
big|grand|binini|kubwa / -kubwa|
small|petit|bito|ndogo / -dogo|
long|long|birebire|ndefu / -refu|
short|court|bigufi|fupi|
many people|beaucoup de gens|abantu benshi|watu wengi|
people|gens / personnes|abantu|watu|
world|monde|isi|dunia|
life|vie|ubuzima|maisha|
death|mort|urupfu|kifo|
age|âge|imyaka|umri|
birthday|anniversaire|isabukuru|siku ya kuzaliwa|
holiday|vacances / jour férié|ikiruhuko|likizo|
weather|météo / temps|ikirere|hali ya hewa|
water|eau|amazi|maji|
electricity|électricité|amashanyarazi|umeme|
light|lumière|urumuri|mwanga|
power cut|coupure de courant|kubura k'umuriro|kukatika kwa umeme|
energy|énergie|ingufu|nishati|
information|information|amakuru|taarifa / habari|
news|nouvelles / actualités|amakuru mashya|habari|
story|histoire / récit|inkuru|hadithi|
idea|idée|igitekerezo|wazo|
opinion|avis / opinion|igitekerezo|maoni|
reason|raison|impamvu|sababu|
example|exemple|urugero|mfano|
meaning|sens / signification|ibisobanuro|maana|
definition|définition|ibisobanuro|ufafanuzi / maana|
solution|solution|igisubizo|suluhisho|
result|résultat|ibyavuyemo|matokeo|
goal|objectif|intego|lengo|
success|succès|intsinzi / iterambere|mafanikio|
mistake|erreur|ikosa|kosa|
error|erreur|ikosa|hitilafu|
number|numéro / nombre|umubare / nomero|nambari / namba|
phone number|numéro de téléphone|nomero ya telefone|namba ya simu|
address|adresse|aderesi|anwani|
date|date|itariki|tarehe|
time|temps / heure|igihe / isaha|wakati / muda|
place|lieu|ahantu|mahali|
way|chemin / manière|inzira / uburyo|njia / njia ya|
thing|chose|ikintu|kitu|
part|partie|igice|sehemu|
group|groupe|itsinda|kundi|
team|équipe|ikipe|timu|
community|communauté|umuryango / abaturage|jamii|
government|gouvernement|leta|serikali|
president|président|perezida|rais|
minister|ministre|minisitiri|waziri|
citizen|citoyen|umuturage|raia|
police station|commissariat|sitasiyo ya polisi|kituo cha polisi|
court|tribunal|urukiko|mahakama|
hospital|hôpital|ibitaro|hospitali|
clinic|clinique|ivuriro|kliniki|
pharmacy|pharmacie|farumasi|duka la dawa|
health|santé|ubuzima|afya|
disease|maladie|indwara|ugonjwa|
vaccine|vaccin|urukingo|chanjo|
farming|agriculture|ubuhinzi|kilimo|
crop|culture|igihingwa|zao|
seed|semence|imbuto|mbegu|
fertilizer|engrais|ifumbire|mbolea|
harvest|récolte|isarura|mavuno|
rain|pluie|imvura|mvua|
soil|sol / terre|ubutaka|udongo|
drought|sécheresse|amapfa / izuba ryinshi|ukame|
storage|stockage|ububiko|hifadhi|
food|nourriture|ibiryo|chakula|
water bottle|bouteille d'eau|icupa ry'amazi|chupa ya maji|

# ---- short useful sentences about safety (so a common request is answered exactly) ----
Do not share your password|Ne partagez pas votre mot de passe|Ntugasangize undi muntu ijambo ryawe ry'ibanga|Usimshirikishe mtu nenosiri lako|
Never share your PIN|Ne partagez jamais votre code PIN|Ntuzigere usangiza undi muntu PIN yawe|Kamwe usishiriki PIN yako|
Do not click this link|Ne cliquez pas sur ce lien|Ntukande kuri iyi link|Usibonyeze kiungo hiki|
This message is a scam|Ce message est une arnaque|Ubu butumwa ni ubutekamutwe|Ujumbe huu ni ulaghai|
I think I was hacked|Je pense avoir été piraté|Ndakeka ko banyinjiyemo|Nadhani nimedukuliwa|
Please help me|Aidez-moi s'il vous plaît|Mumfashe nyabuneka|Tafadhali nisaidie|
I need help|J'ai besoin d'aide|Nkeneye ubufasha|Ninahitaji msaada|
Is this safe?|Est-ce sûr ?|Ibi biratekanye?|Hii ni salama?|
Is it a scam?|Est-ce une arnaque ?|Ni ubutekamutwe?|Je, ni ulaghai?|
Where can I report this?|Où puis-je signaler cela ?|Nabimenyekanisha he?|Naweza kuripoti hili wapi?|
How can I protect myself?|Comment me protéger ?|Nakwirinda nte?|Ninawezaje kujilinda?|
I lost my phone|J'ai perdu mon téléphone|Nabuze telefone yanjye|Nimepoteza simu yangu|
My account was blocked|Mon compte a été bloqué|Konti yanjye yafunzwe|Akaunti yangu imezuiwa|
I forgot my password|J'ai oublié mon mot de passe|Nibagiwe ijambo ry'ibanga|Nimesahau nenosiri langu|
Change your password|Changez votre mot de passe|Hindura ijambo ryawe ry'ibanga|Badilisha nenosiri lako|
Use a strong password|Utilisez un mot de passe fort|Koresha ijambo ry'ibanga rikomeye|Tumia nenosiri imara|
Update your phone|Mettez à jour votre téléphone|Vugurura telefone yawe|Sasisha simu yako|
Who is the owner of this app?|Qui est le propriétaire de cette application ?|Nyiri iyi porogaramu ni nde?|Mmiliki wa programu hii ni nani?|
Who owns this?|À qui appartient ceci ?|Ibi ni ibya nde?|Hii ni ya nani?|
What do you mean?|Que voulez-vous dire ?|Urashaka kuvuga iki?|Unamaanisha nini?|
Can you repeat?|Pouvez-vous répéter ?|Wasubiramo?|Unaweza kurudia?|
Speak slowly please|Parlez lentement s'il vous plaît|Vuga buhoro nyabuneka|Tafadhali zungumza polepole|
I do not understand|Je ne comprends pas|Simbyumva|Sielewi|
I understand|Je comprends|Ndabyumva|Naelewa|
Do you speak English?|Parlez-vous anglais ?|Muvuga Icyongereza?|Unazungumza Kiingereza?|
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
