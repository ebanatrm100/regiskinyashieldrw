"""Log Analyzer: scans pasted or uploaded logs and reports security threats, system errors and suspicious activity. Pure Python (no Streamlit, no network).
Reads: Linux auth/syslog (SSH, sudo, useradd ...), Apache/Nginx access logs (common/combined), Windows event exports (text, CSV or XML with Event IDs), firewall logs (iptables/UFW),
JSON-lines logs and any plain text with timestamps. Everything runs in memory; nothing is stored or sent anywhere. Secrets found in a log are masked in the report.
Each finding has a severity, a MITRE ATT&CK reference, evidence (counts, addresses, sample lines with line numbers) and advice in English, French, Kinyarwanda and Kiswahili.
Detection is rule-based and explainable: a finding is a lead to investigate, never proof of compromise, and a clean result does not prove a system is safe.
fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import csv
import io
import ipaddress
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from urllib.parse import unquote_plus

LANGS = ("en", "fr", "rw", "sw")
MAX_BYTES = 5_000_000
MAX_LINES = 200_000
SEV = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}

# ------------------------------------------------------------------ rule catalogue: id -> (severity, MITRE, titles[4], why[4], do[4])
R: dict = {}


def _r(rid, sev, mitre, title, why, do):
    R[rid] = dict(sev=sev, mitre=mitre, title=dict(zip(LANGS, title)), why=dict(zip(LANGS, why)), do=dict(zip(LANGS, do)))


_r("ssh_bruteforce", "high", "T1110 Brute Force",
   ("Repeated failed logins (password guessing)", "Échecs de connexion répétés (devinette de mots de passe)", "Kwinjira bikanwa kenshi (guhimba amagambo y'ibanga)", "Kushindwa kuingia mara kwa mara (kubahatisha nywila)"),
   ("One address tried many passwords or user names. Attackers do this automatically against SSH, RDP, web logins and mail.", "Une même adresse a essayé de nombreux mots de passe ou noms d'utilisateur. Les attaquants le font automatiquement contre SSH, RDP, sites web et messagerie.",
    "Aderesi imwe yagerageje amagambo y'ibanga cyangwa amazina menshi. Abagizi ba nabi babikora byikora kuri SSH, RDP, imbuga na imeri.", "Anwani moja ilijaribu nywila au majina mengi. Wavamizi hufanya hivi kiotomatiki dhidi ya SSH, RDP, tovuti na barua pepe."),
   ("Block the address at the firewall or with fail2ban; require keys or two-step verification; disable password login for SSH; use long unique passwords.", "Bloquez l'adresse au pare-feu ou avec fail2ban ; exigez clés ou double authentification ; désactivez les mots de passe pour SSH ; utilisez des mots de passe longs et uniques.",
    "Hagarika iyo aderesi kuri firewall cyangwa ukoresheje fail2ban; saba imfunguzo cyangwa kwemeza mu byiciro bibiri; hagarika kwinjira n'ijambo ry'ibanga kuri SSH; koresha amagambo y'ibanga maremare kandi atandukanye.",
    "Zuia anwani kwenye firewall au kwa fail2ban; hitaji funguo au uthibitisho wa hatua mbili; zima kuingia kwa nywila kwenye SSH; tumia nywila ndefu na za kipekee."))
_r("password_spraying", "high", "T1110.003 Password Spraying",
   ("One address trying many different user names", "Une adresse qui essaie de nombreux noms d'utilisateur", "Aderesi imwe igerageza amazina menshi y'abakoresha", "Anwani moja ikijaribu majina mengi ya watumiaji"),
   ("Trying one or two common passwords against many accounts avoids lock-outs and is a classic way to find weak accounts.", "Essayer un ou deux mots de passe courants sur beaucoup de comptes évite les verrouillages ; c'est une méthode classique pour trouver les comptes faibles.",
    "Kugerageza ijambo ry'ibanga rimwe cyangwa abiri risanzwe kuri konti nyinshi birinda gufungwa; ni uburyo busanzwe bwo kubona konti zifite intege nke.", "Kujaribu nywila moja au mbili za kawaida kwa akaunti nyingi huepuka kufungwa; ni njia ya kawaida ya kupata akaunti dhaifu."),
   ("Check which of those accounts exist, force password changes on weak ones, turn on two-step verification and lock out repeated failures.", "Vérifiez lesquels de ces comptes existent, forcez le changement des mots de passe faibles, activez la double authentification et le verrouillage.",
    "Reba konti zibaho muri izo, usabe guhindura amagambo y'ibanga adakomeye, ufungure kwemeza mu byiciro bibiri n'ugufunga nyuma yo kunanirwa kenshi.", "Angalia akaunti zipi zipo, lazimisha kubadilisha nywila dhaifu, washa uthibitisho wa hatua mbili na kufunga baada ya kushindwa mara nyingi."))
_r("login_after_failures", "critical", "T1078 Valid Accounts",
   ("A successful login right after many failures from the same address", "Connexion réussie juste après de nombreux échecs depuis la même adresse", "Kwinjira byagenze neza nyuma y'ibikanywe byinshi biturutse kuri aderesi imwe", "Kuingia kulikofaulu baada ya kushindwa mara nyingi kutoka anwani ileile"),
   ("This is the pattern of a successful password-guessing attack: the attacker may now be inside.", "C'est le schéma d'une attaque par devinette réussie : l'attaquant est peut-être déjà à l'intérieur.",
    "Ni ishusho y'igitero cyo guhimba ijambo ry'ibanga cyagezweho: uwateye ashobora kuba yamaze kwinjira.", "Huu ni mfano wa shambulio la kubahatisha nywila lililofaulu: mshambuliaji anaweza kuwa ndani tayari."),
   ("Treat the account as compromised: disable it, reset its password and keys, check what that session did, look for new users, cron jobs and keys, and block the address.", "Considérez le compte comme compromis : désactivez-le, réinitialisez mot de passe et clés, examinez ce que la session a fait, cherchez nouveaux utilisateurs, tâches cron et clés, bloquez l'adresse.",
    "Fata konti nk'iyibwe: yifunge, uhindure ijambo ry'ibanga n'imfunguzo, urebe ibyakozwe muri iyo session, ushake abakoresha bashya, imirimo ya cron n'imfunguzo, uhagarike iyo aderesi.",
    "Chukulia akaunti kama imevamiwa: izime, badilisha nywila na funguo, kagua kilichofanywa kwenye kikao hicho, tafuta watumiaji wapya, kazi za cron na funguo, na uzuie anwani."))
_r("root_login", "high", "T1078.003 Local Accounts",
   ("Direct login as root / administrator", "Connexion directe en root / administrateur", "Kwinjira ukoresheje root / administrator mu buryo bwa mbere", "Kuingia moja kwa moja kama root / administrator"),
   ("Direct privileged logins remove accountability and are a favourite target.", "Les connexions privilégiées directes suppriment la traçabilité et sont une cible favorite.", "Kwinjira ufite uburenganzira bwuzuye bivanaho kumenya uwakoze icyo gikorwa kandi ni intego ikunzwe.", "Kuingia moja kwa moja kwa mamlaka kamili huondoa uwajibikaji na ni shabaha inayopendwa."),
   ("Disable direct root login over the network; use named accounts with sudo and log who did what.", "Désactivez la connexion root à distance ; utilisez des comptes nominatifs avec sudo.", "Hagarika kwinjira nka root unyuze ku muyoboro; koresha konti zifite amazina na sudo.", "Zima kuingia kama root kupitia mtandao; tumia akaunti zenye majina na sudo."))
_r("account_created", "high", "T1136 Create Account",
   ("A user account was created or added to a privileged group", "Un compte utilisateur a été créé ou ajouté à un groupe privilégié", "Konti y'umukoresha yaremwe cyangwa yongewe mu itsinda ry'abafite uburenganzira bwuzuye", "Akaunti ya mtumiaji imeundwa au kuongezwa kwenye kundi lenye mamlaka"),
   ("Attackers who get in often create their own account to come back later.", "Les attaquants qui entrent créent souvent leur propre compte pour revenir.", "Abagizi ba nabi bamaze kwinjira akenshi bihangira konti kugira ngo bazagaruke.", "Wavamizi wakishaingia mara nyingi huunda akaunti yao ili kurudi baadaye."),
   ("Confirm the change was planned by an administrator; if not, disable the account and investigate how it was created.", "Vérifiez que le changement était prévu par un administrateur ; sinon désactivez le compte et enquêtez.", "Emeza ko impinduka yateguwe n'umuyobozi; niba atari ko, funga konti ukore iperereza.", "Thibitisha kuwa mabadiliko yalipangwa na msimamizi; kama sivyo, zima akaunti na uchunguze."))
_r("sudo_abuse", "medium", "T1548.003 Sudo and Sudo Caching",
   ("Failed or risky use of sudo", "Usage raté ou risqué de sudo", "Gukoresha sudo byanze cyangwa bifite ibyago", "Matumizi yaliyoshindwa au hatari ya sudo"),
   ("Failed sudo attempts or commands that open a shell/change permissions can mean someone is trying to gain full control.", "Des échecs sudo ou des commandes ouvrant un shell/modifiant des droits peuvent signaler une tentative de prise de contrôle.", "Ibigeragezo bya sudo byanze cyangwa amategeko afungura shell/ahindura uburenganzira bishobora kwerekana ugerageza kwigarurira sisitemu.", "Majaribio ya sudo yaliyoshindwa au amri zinazofungua shell/kubadilisha ruhusa zinaweza kuashiria mtu anajaribu kuchukua udhibiti."),
   ("Check who ran these commands and whether it was expected; restrict sudo to what each admin needs.", "Vérifiez qui a lancé ces commandes et si c'était attendu ; limitez sudo au nécessaire.", "Reba uwakoresheje ayo mategeko niba byari bitegerejwe; ugabanye sudo ku byo buri muyobozi akeneye.", "Angalia aliyeendesha amri hizo na kama ilitarajiwa; punguza sudo kwa kile kila msimamizi anachohitaji."))
_r("web_sqli", "high", "T1190 Exploit Public-Facing Application",
   ("SQL injection attempts against the website", "Tentatives d'injection SQL contre le site", "Ibigeragezo byo gushyiramo SQL ku rubuga", "Majaribio ya SQL injection dhidi ya tovuti"),
   ("Requests contain SQL fragments (UNION SELECT, ' OR 1=1, sleep()). If the site is vulnerable, attackers can read or change the database.", "Des requêtes contiennent des fragments SQL (UNION SELECT, ' OR 1=1, sleep()). Si le site est vulnérable, la base peut être lue ou modifiée.",
    "Ibisabwa birimo ibice bya SQL (UNION SELECT, ' OR 1=1, sleep()). Niba urubuga rufite intege nke, abagizi ba nabi bashobora gusoma cyangwa guhindura database.", "Maombi yana vipande vya SQL (UNION SELECT, ' OR 1=1, sleep()). Tovuti ikiwa na udhaifu, wavamizi wanaweza kusoma au kubadilisha hifadhidata."),
   ("Use prepared statements and input validation, put a web application firewall in front, check whether any request got a 200 response with unusual size, and block the sources.", "Utilisez des requêtes préparées et la validation des entrées, placez un WAF, vérifiez si une requête a reçu un 200 de taille inhabituelle et bloquez les sources.",
    "Koresha prepared statements no kugenzura ibyinjijwe, shyiraho WAF, urebe niba hari ikibazo cyasubijwe 200 gifite ubunini budasanzwe, uhagarike aho byaturutse.", "Tumia prepared statements na uhakiki wa pembejeo, weka WAF, angalia kama ombi lolote lilipata 200 yenye ukubwa usio wa kawaida na uzuie vyanzo."))
_r("web_xss", "medium", "T1059.007 JavaScript",
   ("Cross-site scripting (XSS) attempts", "Tentatives de cross-site scripting (XSS)", "Ibigeragezo bya cross-site scripting (XSS)", "Majaribio ya cross-site scripting (XSS)"),
   ("Requests contain script tags or event handlers that try to run attacker code in visitors' browsers.", "Des requêtes contiennent des balises script ou gestionnaires d'événements visant à exécuter du code dans le navigateur des visiteurs.", "Ibisabwa birimo script cyangwa event handlers bigamije gukoresha code y'uwateye mu mushakisha z'abasura.", "Maombi yana lebo za script au vidhibiti vya matukio vinavyojaribu kuendesha msimbo wa mshambuliaji kwenye vivinjari vya wageni."),
   ("Encode output, set a Content-Security-Policy, and validate input.", "Encodez les sorties, définissez une Content-Security-Policy et validez les entrées.", "Hindura ibisohoka (encode), shyiraho Content-Security-Policy kandi ugenzure ibyinjijwe.", "Simba matokeo, weka Content-Security-Policy na uhakiki pembejeo."))
_r("web_traversal", "high", "T1083 File and Directory Discovery",
   ("Path traversal / local file inclusion attempts", "Tentatives de traversée de répertoire / inclusion de fichiers locaux", "Ibigeragezo byo kugera ku madosiye atagenewe (path traversal / LFI)", "Majaribio ya path traversal / local file inclusion"),
   ("Requests with ../ or /etc/passwd try to read files outside the web folder, such as passwords and keys.", "Des requêtes avec ../ ou /etc/passwd tentent de lire des fichiers hors du dossier web (mots de passe, clés).", "Ibisabwa bifite ../ cyangwa /etc/passwd bigerageza gusoma amadosiye hanze y'ububiko bw'urubuga (amagambo y'ibanga, imfunguzo).", "Maombi yenye ../ au /etc/passwd hujaribu kusoma faili nje ya folda ya wavuti (nywila, funguo)."),
   ("Normalise and whitelist file paths in the application, run the web server with minimal rights, and check for any 200 responses to these requests.", "Normalisez et filtrez les chemins de fichiers, exécutez le serveur avec le minimum de droits et vérifiez les réponses 200.", "Genzura kandi wemerere inzira z'amadosiye zizwi gusa, koresha seriveri ufite uburenganzira buke kandi urebe ibisubizo 200.", "Sanifisha na orodhesha njia za faili zinazoruhusiwa, endesha seva kwa ruhusa ndogo na angalia majibu ya 200."))
_r("web_cmdi", "critical", "T1059 Command and Scripting Interpreter",
   ("Command injection / remote code execution attempts", "Tentatives d'injection de commandes / exécution de code à distance", "Ibigeragezo byo gushyiramo amategeko / gukoresha code kure", "Majaribio ya command injection / utekelezaji wa msimbo wa mbali"),
   ("Requests contain shell commands (wget, curl, bash, nc), Log4Shell (${jndi:) or Shellshock patterns. A successful one gives the attacker control of the server.", "Des requêtes contiennent des commandes shell (wget, curl, bash, nc), des motifs Log4Shell (${jndi:) ou Shellshock. Réussie, l'attaque donne le contrôle du serveur.",
    "Ibisabwa birimo amategeko ya shell (wget, curl, bash, nc), Log4Shell (${jndi:) cyangwa Shellshock. Iyo bigezweho, uwateye afata seriveri.", "Maombi yana amri za shell (wget, curl, bash, nc), Log4Shell (${jndi:) au Shellshock. Likifaulu, mshambuliaji anadhibiti seva."),
   ("Patch the affected software immediately, check outbound connections and new processes on that server, and block the sources.", "Corrigez immédiatement les logiciels concernés, examinez les connexions sortantes et nouveaux processus du serveur, bloquez les sources.", "Vugurura vuba porogaramu zagizweho ingaruka, urebe imiyoboro isohoka n'imirimo mishya kuri iyo seriveri, uhagarike aho byaturutse.", "Sasisha mara moja programu zilizoathirika, angalia miunganisho ya kutoka na michakato mipya kwenye seva hiyo na uzuie vyanzo."))
_r("web_sensitive_files", "high", "T1552 Unsecured Credentials",
   ("Probing for sensitive files (.env, .git, backups, keys)", "Recherche de fichiers sensibles (.env, .git, sauvegardes, clés)", "Gushaka amadosiye y'ibanga (.env, .git, backup, imfunguzo)", "Kutafuta faili nyeti (.env, .git, nakala rudufu, funguo)"),
   ("Bots look for configuration files, database dumps and private keys left on web servers.", "Des robots cherchent fichiers de configuration, sauvegardes de bases et clés privées laissés sur les serveurs web.", "Za robo zishaka amadosiye ya configuration, backup za database n'imfunguzo z'ibanga zasizwe kuri seriveri.", "Roboti hutafuta faili za usanidi, nakala za hifadhidata na funguo za siri zilizoachwa kwenye seva."),
   ("Make sure such files are not in the web root, return 404 for them, and rotate any secret that was exposed.", "Assurez-vous que ces fichiers ne sont pas dans la racine web, renvoyez 404 et renouvelez tout secret exposé.", "Menya neza ko ayo madosiye atari mu bubiko rusange bw'urubuga, usubize 404, uhindure ibanga ryose ryagaragaye.", "Hakikisha faili hizo hazipo kwenye root ya wavuti, rudisha 404 na ubadilishe siri yoyote iliyofichuka."))
_r("web_admin_probe", "medium", "T1595 Active Scanning",
   ("Probing of admin and login pages", "Sondage des pages d'administration et de connexion", "Gusuzuma impapuro z'ubuyobozi n'iz'kwinjira", "Kuchunguza kurasa za usimamizi na kuingia"),
   ("Repeated requests to wp-login, phpmyadmin, /admin or manager pages usually come from automated attack tools.", "Des requêtes répétées vers wp-login, phpmyadmin, /admin ou manager viennent le plus souvent d'outils d'attaque automatiques.", "Ibisabwa byinshi kuri wp-login, phpmyadmin, /admin cyangwa manager akenshi bituruka ku bikoresho by'ibitero byikora.", "Maombi ya mara kwa mara kwa wp-login, phpmyadmin, /admin au manager mara nyingi hutoka kwa zana za mashambulizi za kiotomatiki."),
   ("Hide or restrict admin pages (allow-list IPs, VPN), add rate limiting and two-step verification.", "Masquez ou restreignez les pages admin (liste d'IP autorisées, VPN), limitez le débit et ajoutez la double authentification.", "Hisha cyangwa ugabanye impapuro z'ubuyobozi (IP zemewe, VPN), ugabanye ibisabwa kandi ufungure kwemeza mu byiciro bibiri.", "Ficha au zuia kurasa za admin (IP zinazoruhusiwa, VPN), weka kikomo cha maombi na uthibitisho wa hatua mbili."))
_r("web_scanner", "medium", "T1595.002 Vulnerability Scanning",
   ("Known hacking or scanning tools in use", "Outils de piratage ou d'analyse connus utilisés", "Ibikoresho by'abagizi ba nabi bizwi bikoreshwa", "Zana zinazojulikana za udukuzi au uchunguzi zinatumika"),
   ("The user-agent names tools such as sqlmap, nikto, nmap, masscan, hydra or gobuster.", "Le user-agent nomme des outils comme sqlmap, nikto, nmap, masscan, hydra ou gobuster.", "User-agent ivuga ibikoresho nka sqlmap, nikto, nmap, masscan, hydra cyangwa gobuster.", "User-agent inataja zana kama sqlmap, nikto, nmap, masscan, hydra au gobuster."),
   ("Block those sources; if it was your own authorised test, record it so it is not confused with a real attack.", "Bloquez ces sources ; si c'était votre test autorisé, notez-le pour ne pas le confondre avec une vraie attaque.", "Hagarika iyo masoko; niba byari ikizamini cyawe cyemewe, kibike kugira ngo kidatekerezwa nk'igitero nyacyo.", "Zuia vyanzo hivyo; ikiwa ilikuwa jaribio lako lililoidhinishwa, liandike ili lisichanganywe na shambulio halisi."))
_r("http_scan_404", "medium", "T1595.003 Wordlist Scanning",
   ("Many 'not found' requests from one address (directory scan)", "Nombreuses requêtes « introuvable » d'une adresse (balayage de répertoires)", "Ibisabwa byinshi «ntibiboneka» biturutse kuri aderesi imwe (gusaka ububiko)", "Maombi mengi ya «haipatikani» kutoka anwani moja (kuchanganua folda)"),
   ("An address requesting hundreds of non-existent pages is searching for hidden files and entry points.", "Une adresse qui demande des centaines de pages inexistantes cherche fichiers cachés et points d'entrée.", "Aderesi isaba impapuro amajana zitabaho iba ishaka amadosiye yihishe n'aho yinjirira.", "Anwani inayoomba mamia ya kurasa zisizokuwepo inatafuta faili zilizofichwa na maeneo ya kuingilia."),
   ("Rate-limit or block the address and review what it did get a 200 for.", "Limitez le débit ou bloquez l'adresse et examinez les pages qui ont reçu un 200.", "Ugabanye ibisabwa cyangwa uhagarike iyo aderesi urebe ibyo yabonye 200.", "Weka kikomo cha maombi au uzuie anwani na uangalie ilichopata 200."))
_r("http_login_bruteforce", "high", "T1110 Brute Force",
   ("Repeated login attempts on a web login page", "Tentatives répétées sur une page de connexion web", "Ibigeragezo byinshi byo kwinjira ku rupapuro rw'urubuga", "Majaribio ya mara kwa mara ya kuingia kwenye ukurasa wa kuingia wa wavuti"),
   ("Many POST requests to a login URL from one address, or many 401/403 answers, point to password guessing against the site.", "De nombreuses requêtes POST vers une page de connexion depuis une adresse, ou beaucoup de 401/403, indiquent une devinette de mots de passe.", "POST nyinshi kuri URL yo kwinjira ziturutse kuri aderesi imwe, cyangwa 401/403 nyinshi, bigaragaza guhimba amagambo y'ibanga.", "Maombi mengi ya POST kwa URL ya kuingia kutoka anwani moja, au majibu mengi ya 401/403, yanaashiria kubahatisha nywila."),
   ("Add rate limiting, a CAPTCHA or lock-out and two-step verification; block the address.", "Ajoutez limitation de débit, CAPTCHA ou verrouillage et double authentification ; bloquez l'adresse.", "Shyiraho imbibi z'ibisabwa, CAPTCHA cyangwa gufunga na kwemeza mu byiciro bibiri; uhagarike aderesi.", "Weka kikomo cha maombi, CAPTCHA au kufunga na uthibitisho wa hatua mbili; zuia anwani."))
_r("request_flood", "high", "T1498 Network Denial of Service",
   ("Request flood from one address (possible denial-of-service)", "Déluge de requêtes d'une adresse (déni de service possible)", "Ibisabwa byinshi cyane biturutse kuri aderesi imwe (DoS bishoboka)", "Mafuriko ya maombi kutoka anwani moja (huenda DoS)"),
   ("An unusually high number of requests per minute can exhaust the server and make it unavailable.", "Un nombre anormalement élevé de requêtes par minute peut épuiser le serveur et le rendre indisponible.", "Ibisabwa byinshi bidasanzwe mu munota bishobora kunaniza seriveri ikaba itagikora.", "Idadi isiyo ya kawaida ya maombi kwa dakika inaweza kuchosha seva na kuifanya isipatikane."),
   ("Rate-limit, use a CDN or DDoS protection, and block the offending addresses.", "Limitez le débit, utilisez un CDN ou une protection DDoS et bloquez les adresses fautives.", "Gabanya ibisabwa, koresha CDN cyangwa uburinzi bwa DDoS kandi uhagarike aderesi zikora ibyo.", "Weka kikomo, tumia CDN au ulinzi wa DDoS na uzuie anwani zinazohusika."))
_r("server_errors", "medium", "T1499 Endpoint Denial of Service",
   ("Many server errors (HTTP 5xx)", "Nombreuses erreurs serveur (HTTP 5xx)", "Amakosa menshi ya seriveri (HTTP 5xx)", "Makosa mengi ya seva (HTTP 5xx)"),
   ("A burst of 500-series errors means the application is failing, from a bug, an overloaded server or an attack that crashes it.", "Une rafale d'erreurs 500 signale une application en échec : bug, serveur surchargé ou attaque qui la fait tomber.", "Amakosa 500 menshi yerekana ko porogaramu ihura n'ikibazo: bug, seriveri iremerewe cyangwa igitero kiyisenya.", "Wingi wa makosa ya 500 unaonyesha programu inashindwa: hitilafu, seva imezidiwa au shambulio linaiangusha."),
   ("Check the application and server logs at those times, recent deployments, and whether the errors line up with the suspicious requests.", "Examinez journaux applicatifs et serveur à ces moments, les déploiements récents et le lien avec les requêtes suspectes.", "Reba logs za porogaramu na seriveri muri ibyo bihe, ivugurura rya vuba no kureba niba hari isano n'ibisabwa biteye inkeke.", "Angalia kumbukumbu za programu na seva nyakati hizo, usambazaji wa hivi karibuni na kama makosa yanaendana na maombi ya kutiliwa shaka."))
_r("port_scan", "high", "T1046 Network Service Discovery",
   ("Port scan: one address touching many ports", "Balayage de ports : une adresse qui touche de nombreux ports", "Gusuzuma ports: aderesi imwe ikora ku miryango myinshi", "Uchanganuzi wa port: anwani moja ikigusa port nyingi"),
   ("Attackers scan ports to learn which services are open before attacking them.", "Les attaquants balayent les ports pour savoir quels services sont ouverts avant d'attaquer.", "Abagizi ba nabi basuzuma ports kugira ngo bamenye serivisi zifunguye mbere yo gutera.", "Wavamizi huchanganua port kujua huduma zipi zimefunguliwa kabla ya kushambulia."),
   ("Close services you do not need, allow only required ports, block the scanner and watch for follow-up attacks on the ports it found open.", "Fermez les services inutiles, n'autorisez que les ports nécessaires, bloquez le scanner et surveillez les attaques sur les ports découverts.", "Funga serivisi udakeneye, wemerere ports zikenewe gusa, uhagarike usuzuma kandi ukurikirane ibitero kuri ports yasanze zifunguye.", "Funga huduma usizozihitaji, ruhusu port zinazohitajika tu, zuia mchanganuzi na ufuatilie mashambulizi kwenye port alizozikuta wazi."))
_r("firewall_blocks", "low", "T1595 Active Scanning",
   ("Many connections blocked by the firewall", "Nombreuses connexions bloquées par le pare-feu", "Imiyoboro myinshi yahagaritswe na firewall", "Miunganisho mingi imezuiwa na firewall"),
   ("The firewall is doing its job; large counts show background scanning or targeted probing.", "Le pare-feu fait son travail ; de grands nombres révèlent des balayages de fond ou des sondes ciblées.", "Firewall irakora; umubare munini werekana gusuzuma kwa buri munsi cyangwa gukurikirana intego runaka.", "Firewall inafanya kazi yake; idadi kubwa inaonyesha uchanganuzi wa kawaida au uchunguzi uliolengwa."),
   ("Review the top blocked sources and ports; add long-term blocks for repeat offenders.", "Examinez les sources et ports les plus bloqués ; bloquez durablement les récidivistes.", "Suzuma aderesi na ports zihagaritswe cyane; ushyireho ihagarikwa rirambye ku bagaruka.", "Kagua vyanzo na port zilizozuiwa zaidi; weka vizuizi vya muda mrefu kwa wanaorudia."))
_r("malicious_command", "critical", "T1059 Command and Scripting Interpreter",
   ("Commands typical of an intruder or malware", "Commandes typiques d'un intrus ou d'un logiciel malveillant", "Amategeko asanzwe akoreshwa n'umwinjiro cyangwa malware", "Amri za kawaida za mvamizi au programu hasidi"),
   ("Examples: encoded PowerShell, downloading and running scripts (curl|bash, certutil), reverse shells, credential dumping tools such as mimikatz.", "Exemples : PowerShell encodé, téléchargement et exécution de scripts (curl|bash, certutil), reverse shells, outils de vol d'identifiants comme mimikatz.",
    "Urugero: PowerShell yahinduwe, gukuramo no gukoresha scripts (curl|bash, certutil), reverse shells, ibikoresho byiba amagambo y'ibanga nka mimikatz.", "Mifano: PowerShell iliyosimbwa, kupakua na kuendesha script (curl|bash, certutil), reverse shell, zana za kuiba stakabadhi kama mimikatz."),
   ("Isolate the machine from the network, preserve the logs and memory if you can, find which account ran it, and rebuild from a clean image after investigation.", "Isolez la machine du réseau, conservez journaux et mémoire si possible, trouvez le compte utilisé, puis reconstruisez depuis une image saine après enquête.",
    "Tandukanya mudasobwa n'umuyoboro, ubike logs na memory niba bishoboka, umenye konti yabikoresheje, hanyuma usubizeho ukoresheje image nzima nyuma y'iperereza.", "Tenga mashine na mtandao, hifadhi kumbukumbu na memory ikiwezekana, tambua akaunti iliyoitumia, kisha jenga upya kutoka picha safi baada ya uchunguzi."))
_r("persistence", "high", "T1053 Scheduled Task/Job",
   ("Persistence: new scheduled job, service, startup entry or SSH key", "Persistance : nouvelle tâche planifiée, service, entrée de démarrage ou clé SSH", "Kwihisha: igikorwa gishya giteganyijwe, serivisi, itangira rya sisitemu cyangwa urufunguzo rwa SSH", "Kudumu: kazi mpya iliyopangwa, huduma, kipengee cha kuanza au ufunguo wa SSH"),
   ("Intruders add cron jobs, services, Run keys or authorized_keys entries so they can return after a reboot.", "Les intrus ajoutent tâches cron, services, clés Run ou authorized_keys pour revenir après un redémarrage.", "Abinjira bongeramo cron jobs, serivisi, Run keys cyangwa authorized_keys kugira ngo bagaruke nyuma yo gutangira sisitemu.", "Wavamizi huongeza kazi za cron, huduma, funguo za Run au authorized_keys ili kurudi baada ya kuwasha upya."),
   ("Review the new entries, remove any you did not create, and find how they were added.", "Examinez les nouvelles entrées, supprimez celles que vous n'avez pas créées et trouvez comment elles ont été ajoutées.", "Suzuma ibishya, ukureho ibyo utaremye kandi umenye uko byongewemo.", "Kagua vipengee vipya, ondoa ulivyovitengeneza na ujue jinsi vilivyoongezwa."))
_r("log_tampering", "critical", "T1070 Indicator Removal",
   ("Signs of log deletion or history clearing", "Signes de suppression de journaux ou d'effacement d'historique", "Ibimenyetso byo gusiba logs cyangwa amateka y'amategeko", "Dalili za kufuta kumbukumbu au historia ya amri"),
   ("Attackers clear logs and shell history to hide what they did. A cleared audit log (Windows event 1102) is serious.", "Les attaquants effacent journaux et historique pour cacher leurs traces. Un journal d'audit effacé (événement Windows 1102) est grave.", "Abagizi ba nabi basiba logs n'amateka kugira ngo bahishe ibyo bakoze. Gusiba audit log (event ya Windows 1102) ni ikibazo gikomeye.", "Wavamizi hufuta kumbukumbu na historia kuficha walichofanya. Kumbukumbu ya ukaguzi iliyofutwa (tukio la Windows 1102) ni jambo zito."),
   ("Send logs to a separate server so they cannot be erased locally; investigate who cleared them and what happened just before.", "Envoyez les journaux vers un serveur séparé pour qu'ils ne soient pas effaçables ; enquêtez sur qui les a effacés et ce qui s'est passé avant.", "Ohereza logs kuri seriveri yihariye kugira ngo zitasibwa aho ziri; ukore iperereza ku wazisibye n'ibyabaye mbere gato.", "Tuma kumbukumbu kwenye seva tofauti ili zisifutwe hapo; chunguza aliyezifuta na kilichotokea kabla yake."))
_r("windows_failed_logons", "high", "T1110 Brute Force",
   ("Many failed Windows logons (event 4625) or account lock-outs (4740)", "Nombreuses ouvertures de session Windows échouées (événement 4625) ou verrouillages (4740)", "Kwinjira kwinshi kunaniwe kuri Windows (event 4625) cyangwa gufungwa konti (4740)", "Kuingia mara nyingi kulikoshindwa kwenye Windows (tukio 4625) au kufungwa akaunti (4740)"),
   ("Repeated failures can mean password guessing against Remote Desktop, file shares or domain accounts.", "Des échecs répétés peuvent signaler une devinette de mots de passe sur le Bureau à distance, partages ou comptes de domaine.", "Kunanirwa kenshi bishobora kwerekana guhimba amagambo y'ibanga kuri Remote Desktop, ububiko busangiwe cyangwa konti za domain.", "Kushindwa mara kwa mara kunaweza kumaanisha kubahatisha nywila kwenye Remote Desktop, folda za pamoja au akaunti za domain."),
   ("Do not expose RDP to the internet; use a VPN and two-step verification; check the source addresses and lock out repeat offenders.", "N'exposez pas RDP sur Internet ; utilisez un VPN et la double authentification ; vérifiez les adresses sources et verrouillez les récidivistes.", "Ntushyire RDP kuri interineti; koresha VPN na kwemeza mu byiciro bibiri; genzura aderesi zaturutseho ufunge abagaruka.", "Usiweke RDP wazi kwenye mtandao; tumia VPN na uthibitisho wa hatua mbili; angalia anwani za chanzo na ufunge wanaorudia."))
_r("windows_privileged_change", "high", "T1098 Account Manipulation",
   ("Windows privileged change (new admin, scheduled task, new service, audit policy)", "Changement privilégié Windows (nouvel admin, tâche planifiée, nouveau service, politique d'audit)", "Impinduka ikomeye kuri Windows (admin mushya, igikorwa giteganyijwe, serivisi nshya, politiki y'ubugenzuzi)", "Mabadiliko ya kimamlaka ya Windows (msimamizi mpya, kazi iliyopangwa, huduma mpya, sera ya ukaguzi)"),
   ("Events 4720, 4728/4732/4756, 4698, 7045 and 4719 show accounts, groups, tasks, services or audit settings changing.", "Les événements 4720, 4728/4732/4756, 4698, 7045 et 4719 montrent des changements de comptes, groupes, tâches, services ou audit.", "Events 4720, 4728/4732/4756, 4698, 7045 na 4719 zerekana impinduka kuri konti, amatsinda, imirimo, serivisi cyangwa ubugenzuzi.", "Matukio 4720, 4728/4732/4756, 4698, 7045 na 4719 yanaonyesha mabadiliko ya akaunti, makundi, kazi, huduma au ukaguzi."),
   ("Confirm each change was authorised; investigate any that were not.", "Confirmez que chaque changement était autorisé ; enquêtez sur les autres.", "Emeza ko buri mpinduka yari yemewe; ukore iperereza ku zitari zemewe.", "Thibitisha kila badiliko lilikuwa limeidhinishwa; chunguza yasiyoidhinishwa."))
_r("rdp_external", "medium", "T1021.001 Remote Desktop Protocol",
   ("Remote Desktop (RDP) logons", "Connexions Bureau à distance (RDP)", "Kwinjira kuri Remote Desktop (RDP)", "Kuingia kwa Remote Desktop (RDP)"),
   ("Logon type 10 means remote desktop. From a public address it is risky unless expected.", "Le type de connexion 10 signifie bureau à distance. Depuis une adresse publique, c'est risqué sauf si attendu.", "Ubwoko bwa 10 bivuga remote desktop. Iturutse kuri aderesi rusange ni ikibazo keretse bitegerejwe.", "Aina ya kuingia 10 inamaanisha remote desktop. Kutoka anwani ya umma ni hatari isipokuwa ilitarajiwa."),
   ("Verify the user and address; restrict RDP to VPN.", "Vérifiez l'utilisateur et l'adresse ; limitez RDP au VPN.", "Genzura umukoresha na aderesi; ugabanye RDP kuri VPN gusa.", "Hakiki mtumiaji na anwani; weka RDP kwa VPN pekee."))
_r("secrets_in_logs", "medium", "T1552.001 Credentials In Files",
   ("Passwords, tokens or keys written in the log", "Mots de passe, jetons ou clés écrits dans le journal", "Amagambo y'ibanga, tokens cyangwa imfunguzo byanditswe muri log", "Nywila, tokeni au funguo zimeandikwa kwenye kumbukumbu"),
   ("Anyone who can read the log can reuse these secrets. They are masked in this report.", "Quiconque lit le journal peut réutiliser ces secrets. Ils sont masqués dans ce rapport.", "Umuntu wese ushobora gusoma log ashobora gukoresha ayo mabanga. Yahishwe muri iri raporo.", "Yeyote anayeweza kusoma kumbukumbu anaweza kutumia siri hizi. Zimefichwa kwenye ripoti hii."),
   ("Change those secrets now, stop the application from logging them, and restrict who can read logs.", "Changez ces secrets maintenant, empêchez l'application de les journaliser et limitez l'accès aux journaux.", "Hindura ayo mabanga ubu, uhagarike porogaramu kuyandika muri log kandi ugabanye abasoma logs.", "Badilisha siri hizo sasa, zuia programu kuziandika na upunguze wanaosoma kumbukumbu."))
_r("system_errors", "medium", "T1499 Endpoint Denial of Service",
   ("System faults: crashes, memory, disk or service failures", "Pannes système : plantages, mémoire, disque ou services en échec", "Ibibazo bya sisitemu: kwangirika, memory, disk cyangwa serivisi zinaniwe", "Hitilafu za mfumo: kuanguka, kumbukumbu, diski au huduma kushindwa"),
   ("Out-of-memory kills, segmentation faults, disk-full or I/O errors and failed services cause outages and can also follow an attack.", "Arrêts par manque de mémoire, erreurs de segmentation, disque plein ou erreurs E/S et services en échec causent des pannes et peuvent suivre une attaque.", "Gukurwaho kubera memory, segmentation fault, disk yuzuye cyangwa amakosa ya I/O n'serivisi zinaniwe bitera guhagarara kandi bishobora gukurikira igitero.", "Kuuawa kwa michakato kwa kukosa kumbukumbu, segmentation fault, diski kujaa au makosa ya I/O na huduma zilizoshindwa husababisha kusimama na pia zaweza kufuata shambulio."),
   ("Free disk space or add memory, restart failed services, check hardware health, and review what changed just before the first error.", "Libérez de l'espace disque ou ajoutez de la mémoire, redémarrez les services, vérifiez le matériel et examinez ce qui a changé avant la première erreur.", "Shyiraho umwanya kuri disk cyangwa wongere memory, utangirize serivisi zinaniwe, urebe ubuzima bw'ibikoresho kandi urebe ibyahindutse mbere y'ikosa rya mbere.", "Futa nafasi ya diski au ongeza kumbukumbu, anzisha upya huduma zilizoshindwa, kagua afya ya vifaa na uangalie kilichobadilika kabla ya kosa la kwanza."))
_r("error_levels", "low", "—",
   ("Errors and critical messages in the log", "Erreurs et messages critiques dans le journal", "Amakosa n'ubutumwa bukomeye muri log", "Makosa na ujumbe muhimu kwenye kumbukumbu"),
   ("The log contains ERROR / CRITICAL / FATAL entries that deserve a look even when no attack is visible.", "Le journal contient des entrées ERROR / CRITICAL / FATAL qui méritent un examen même sans attaque visible.", "Log irimo ERROR / CRITICAL / FATAL zikwiye kurebwa nubwo nta gitero kigaragara.", "Kumbukumbu ina ERROR / CRITICAL / FATAL zinazostahili kuangaliwa hata bila shambulio linaloonekana."),
   ("Group the messages by source and fix the most frequent first.", "Regroupez les messages par source et corrigez d'abord les plus fréquents.", "Teranya ubutumwa ku isoko maze ukosore ibikunze kugaragara mbere.", "Pangia ujumbe kwa chanzo na urekebishe zinazojirudia zaidi kwanza."))
_r("clean", "info", "—",
   ("No known attack pattern found", "Aucun schéma d'attaque connu trouvé", "Nta shusho ry'igitero rizwi ryabonetse", "Hakuna mfumo wa shambulio unaojulikana uliopatikana"),
   ("None of the built-in rules matched. That does not prove the system is safe: logs only show what was recorded.", "Aucune règle intégrée n'a correspondu. Cela ne prouve pas que le système est sûr : les journaux ne montrent que ce qui a été enregistré.", "Nta tegeko ryo mu cyuma ryahuye. Ibi ntibyemeza ko sisitemu itekanye: logs zerekana gusa ibyanditswe.", "Hakuna kanuni iliyolingana. Hii haithibitishi mfumo uko salama: kumbukumbu zinaonyesha tu kilichorekodiwa."),
   ("Keep collecting logs, include more sources (firewall, authentication, application) and look again after any incident.", "Continuez à collecter les journaux, ajoutez d'autres sources (pare-feu, authentification, application) et réexaminez après tout incident.", "Komeza ukusanye logs, wongereho andi masoko (firewall, kwinjira, porogaramu) kandi usubiremo nyuma ya buri kibazo.", "Endelea kukusanya kumbukumbu, ongeza vyanzo vingine (firewall, uthibitishaji, programu) na uangalie tena baada ya tukio lolote."))


# ------------------------------------------------------------------ parsing
_IP = r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"
_IP_RE = re.compile(_IP)
_MONTH = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
_TS_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})")
_TS_APACHE = re.compile(r"(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})")
_TS_SYSLOG = re.compile(r"\b([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\b")
_TS_US = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})[ ,]+(\d{1,2}):(\d{2}):(\d{2})(?:\s*([AP]M))?", re.I)
_EVID = re.compile(r"(?:event ?id|eventid)[\"'>=:\s]*(\d{3,5})", re.I)
_ACCESS = re.compile(r'(?P<ip>' + _IP + r')\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+"(?P<m>[A-Z]{3,8})\s+(?P<path>\S+)(?:\s+HTTP/[\d.]+)?"\s+(?P<st>\d{3})\s+(?P<sz>\d+|-)(?:\s+"(?P<ref>[^"]*)"\s+"(?P<ua>[^"]*)")?')
_URL = re.compile(r"https?://[^\s'\"<>)\]]+", re.I)
_HASH = re.compile(r"\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40}|[a-fA-F0-9]{32})\b")


def _ts(line: str, year: int):
    try:
        m = _TS_ISO.search(line)
        if m:
            return datetime(*map(int, m.groups()))
        m = _TS_APACHE.search(line)
        if m and m.group(2).lower() in _MONTH:
            return datetime(int(m.group(3)), _MONTH[m.group(2).lower()], int(m.group(1)), int(m.group(4)), int(m.group(5)), int(m.group(6)))
        m = _TS_SYSLOG.search(line)
        if m and m.group(1).lower() in _MONTH:
            return datetime(year, _MONTH[m.group(1).lower()], int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
        m = _TS_US.search(line)
        if m:
            mo, d, y, h, mi, s, ap = m.groups()
            h = int(h)
            if ap:
                h = h % 12 + (12 if ap.upper() == "PM" else 0)
            return datetime(int(y), int(mo), int(d), h, int(mi), int(s))
    except Exception:
        return None
    return None


def normalise(text: str) -> list:
    """Turn any supported input (plain text, JSON lines, JSON array, CSV export, XML events) into a list of one-line strings."""
    text = (text or "").replace("\x00", "")
    s = text.lstrip()
    lines = None
    if s[:1] in "[{":
        try:
            data = json.loads(s)
            rows = data if isinstance(data, list) else (data.get("records") or data.get("events") or data.get("logs") or [data]) if isinstance(data, dict) else []
            lines = [" ".join(f"{k}={v}" for k, v in _flat(r).items()) for r in rows if isinstance(r, dict)]
        except Exception:
            rows = []
            for ln in text.splitlines():
                ln = ln.strip()
                if ln[:1] == "{":
                    try:
                        rows.append(" ".join(f"{k}={v}" for k, v in _flat(json.loads(ln)).items()))
                        continue
                    except Exception:
                        pass
                rows.append(ln)
            lines = rows if any("=" in r for r in rows[:5]) else None
    if lines is None and "<Event" in text and "</Event>" in text:
        lines = [re.sub(r"<[^>]*?([A-Za-z]+)(?: Name=\"(\w+)\")?[^>]*>([^<]*)", lambda m: f" {m.group(2) or m.group(1)}={m.group(3).strip()}" if m.group(3).strip() else " ", blk) for blk in text.split("</Event>")]
        lines = [re.sub(r"\s+", " ", x).strip() for x in lines if x.strip()]
    if lines is None:
        head = text.splitlines()[:1]
        if head and "," in head[0] and re.search(r"event ?id|source network|account name|logon", head[0], re.I):
            try:
                rd = csv.DictReader(io.StringIO(text))
                lines = [" ".join(f"{k}={v}" for k, v in row.items() if v) for row in rd]
            except Exception:
                lines = None
    if lines is None:
        lines = text.splitlines()
    return [ln.rstrip() for ln in lines if ln.strip()]


def _flat(d, pre=""):
    out = {}
    for k, v in d.items():
        key = f"{pre}{k}"
        if isinstance(v, dict):
            out.update(_flat(v, key + "."))
        elif isinstance(v, list):
            out[key] = ",".join(str(x) for x in v[:5])
        else:
            out[key] = v
    return out


_LOGISH = re.compile(r"sshd|sudo|kernel:|systemd|cron|\bHTTP/\d|\"(?:GET|POST|HEAD|PUT) |SRC=\d|DPT=|event ?id|\b(?:INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|DEBUG)\b|failed password|accepted (?:password|publickey)|\w+=\S+ \w+=\S+", re.I)


def looks_like_log(text: str) -> bool:
    """True for text that looks like a log (several lines with timestamps or typical log words)."""
    lines = [l for l in (text or "").splitlines() if l.strip()][:200]
    if len(lines) < 3:
        return False
    hit = sum(1 for l in lines if (_ts(l, 2000) is not None) or _LOGISH.search(l))
    return hit / len(lines) >= 0.6


# ------------------------------------------------------------------ masking
_SECRET_KV = re.compile(r"(?i)\b(pass(?:word|wd)?|pin|secret|api[_-]?key|access[_-]?key|token|authorization|auth|client_secret)(\s*[=:]\s*)(\"[^\"]+\"|'[^']+'|\S+)")
_SECRETS = (_SECRET_KV, re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{16,}"), re.compile(r"\bAKIA[0-9A-Z]{16}\b"), re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
            re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"))


def mask(line: str) -> str:
    out = _SECRET_KV.sub(lambda m: f"{m.group(1)}{m.group(2)}***", line)
    for rx in _SECRETS[1:]:
        out = rx.sub("***", out)
    return out


def _has_secret(line: str) -> bool:
    m = _SECRET_KV.search(line)
    if m and len(m.group(3).strip("\"'")) >= 4 and not m.group(3).startswith(("***", "[", "{", "<")) and not re.match(r"(?i)(?:null|none|true|false|redacted|hidden)", m.group(3).strip("\"'")):
        return True
    return any(rx.search(line) for rx in _SECRETS[1:])


# ------------------------------------------------------------------ detection patterns
_P = {k: re.compile(v, re.I) for k, v in dict(
    sqli=r"union(?:\s|\+|/\*.*?\*/)+(?:all\s+)?select|'\s*(?:or|and)\s*'?\d|\b(?:or|and)\s+\d+\s*=\s*\d+|information_schema|sleep\s*\(\s*\d|benchmark\s*\(|waitfor\s+delay|xp_cmdshell|load_file\s*\(|into\s+outfile|;\s*drop\s+table|extractvalue\s*\(|updatexml\s*\(",
    xss=r"<script|javascript:|onerror\s*=|onload\s*=|<svg[^>]*on\w+=|<iframe|document\.cookie|alert\s*\(",
    traversal=r"\.\./|\.\.\\|/etc/(?:passwd|shadow|hosts)|/proc/self|boot\.ini|win\.ini|c:\\windows|php://|file://|expect://",
    cmdi=r"(?:;|\||`|\$\(|&&)\s*(?:cat|ls|id|whoami|uname|wget|curl|nc|ncat|bash|sh|python\d?|perl|php|powershell|cmd|ping|rm|chmod|echo)\b|\$\{jndi:|\(\)\s*\{\s*:;\s*\}|/bin/(?:ba)?sh|cmd\.exe|eval\s*\(|base64_decode\s*\(|passthru\s*\(|shell_exec\s*\(|(?:c99|r57|wso|b374k|webshell|cmd|eval-stdin)\.php",
    sensitive=r"/\.env\b|/\.git(?:/|$)|wp-config|\.htpasswd|id_rsa|/\.ssh/|backup\.(?:sql|zip|tar|gz)|dump\.sql|\.sql(?:\.gz)?(?:\?|$)|/phpinfo|/server-status|\.bak(?:\?|$)|\.swp(?:\?|$)|web\.config|/\.aws/|appsettings\.json|composer\.(?:json|lock)",
    admin=r"wp-login\.php|/xmlrpc\.php|/wp-admin|phpmyadmin|/pma/|/administrator(?:/|\b)|/admin(?:/|\b)|/manager/html|/cgi-bin/|/actuator|/solr/|/jenkins|/vendor/phpunit|/boaform|/HNAP1|/setup\.cgi",
    scanner=r"sqlmap|nikto|nmap|masscan|zgrab|nessus|acunetix|dirbuster|gobuster|wpscan|hydra|burpsuite|nuclei|openvas|w3af|metasploit|havij|arachni|whatweb|feroxbuster|\bffuf\b",
    login_path=r"login|signin|sign-in|wp-login|/auth|xmlrpc|user/login|admin",
    fw_action=r"\b(?:BLOCK|DROP|DENY|REJECT|DENIED|BLOCKED)\b",
    malicious=r"powershell(?:\.exe)?\s+.*(?:-enc(?:odedcommand)?\b|-e\s+[a-z0-9+/=]{20,}|downloadstring|iex\s*\(|invoke-expression|-nop\b|-w\s+hidden|bypass)|certutil.*-urlcache|bitsadmin.*/transfer|(?:wget|curl)[^|\n]*\|\s*(?:sudo\s+)?(?:ba)?sh\b|base64\s+(?:-d|--decode)[^|\n]*\|\s*(?:ba)?sh|\bnc(?:at)?\s+.*\s-e\s|bash\s+-i\s*>&\s*/dev/tcp|/dev/tcp/\d|mkfifo\s+/tmp|python\d?\s+-c\s+.*socket|mimikatz|sekurlsa|procdump.*lsass|lsass\.dmp|net\s+user\s+\S+\s+\S+\s+/add|vssadmin\s+delete\s+shadows|bcdedit.*recoveryenabled\s+no|chmod\s+(?:\+x|[0-7]*7[0-7]*)\s+/tmp/|/tmp/\.\w+|xmrig|minerd|cryptonight|stratum\+tcp",
    persistence=r"crontab\[\d+\]:\s*\(\S+\)\s*(?:BEGIN EDIT|REPLACE|DELETE)|/etc/cron\.(?:d|daily|hourly)/\S+.*(?:created|new|wrote)|created symlink|systemctl\s+(?:enable|daemon-reload)|authorized_keys|schtasks\s+/create|currentversion\\run\b|/etc/rc\.local|ld\.so\.preload|launchagents|a service was installed|a scheduled task was created",
    tamper=r"logs?\s+(?:file\s+)?(?:was\s+|were\s+|has been\s+)?(?:cleared|deleted|truncated)|audit log\s+(?:was\s+)?cleared|history\s+-c\b|unset\s+histfile|histfile=/dev/null|rm\s+(?:-\w+\s+)*/var/log|shred\s+\S*log|wevtutil\s+cl\b|truncate\s+-s\s*0\s+\S*log|>\s*/var/log/",
    acct=r"useradd\[\d+\]:\s*new user|new user:\s*name=|adduser\[|\buseradd\b|usermod\b.*-a?G|gpasswd.*(?:add|-a)\b|added to (?:group|sudo|wheel)|net localgroup administrators .* /add|a user account was created|member was added to a (?:security-enabled )?(?:local|global|universal)",
    sudo=r"sudo:.*(?:authentication failure|incorrect password|NOT in sudoers)|sudo:.*COMMAND=.*(?:/bin/(?:ba)?sh\b|\bsu\b|chmod\s+(?:\+s|777|u\+s)|chown\s+root|visudo|\bpasswd\b|/etc/shadow|/etc/sudoers)",
    syserr=r"kernel panic|out of memory|oom-killer|killed process|segfault|segmentation fault|i/o error|no space left on device|filesystem.*read-only|ext4-fs error|call trace|machine check|failed to start|entered failed state|main process exited, code=(?:exited|killed)|start request repeated too quickly|disk.*(?:failure|failing)",
    errlevel=r"\b(?:ERROR|CRITICAL|FATAL|EMERG|ALERT|SEVERE)\b",
).items()}
_SSH_FAIL = re.compile(r"(?:Failed (?:password|publickey|keyboard-interactive/pam) for (?:invalid user )?(?P<u>\S+) from (?P<ip>" + _IP + r")|Invalid user (?P<u2>\S*) from (?P<ip2>" + _IP + r")|authentication failure;.*?rhost=(?P<ip3>" + _IP + r")(?:\s+user=(?P<u3>\S+))?)", re.I)
_SSH_OK = re.compile(r"Accepted (?:password|publickey|keyboard-interactive/pam) for (?P<u>\S+) from (?P<ip>" + _IP + r")", re.I)
_GEN_FAIL = re.compile(r"(?:login|logon|authentication|auth) (?:failed|failure|error)|failed login|bad password|invalid (?:password|credentials)|incorrect password|access denied for user", re.I)
_FW = re.compile(r"SRC=(?P<src>" + _IP + r").*?DPT=(?P<dpt>\d+)|\bsrc=(?P<src2>" + _IP + r").*?dport=(?P<dpt2>\d+)|from (?P<src3>" + _IP + r") port (?P<dpt3>\d+) .*?(?:blocked|denied|dropped)", re.I)
_CMD_NOT_WEB = re.compile(r"COMMAND=|CommandLine|process_name|ProcessName|history|bash|cmd\.exe|powershell|ps1|sh -c|execve|auditd|type=EXECVE|4688", re.I)
_PRIV_WIN = {"4719", "4697"}
_PERSIST_WIN = {"4698", "7045"}
_ACCT_WIN = {"4720", "4728", "4732", "4756"}
_FAIL_WIN = {"4625", "4740", "4771", "4776"}


def _is_public(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def _valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


class _F:
    """Collects one finding."""
    __slots__ = ("rid", "count", "ips", "users", "samples", "extra")

    def __init__(self, rid):
        self.rid, self.count, self.ips, self.users, self.samples, self.extra = rid, 0, Counter(), Counter(), [], {}

    def hit(self, n, raw, ip=None, user=None, weight=1):
        self.count += weight
        if ip:
            self.ips[ip] += weight
        if user:
            self.users[user] += weight
        if len(self.samples) < 4:
            self.samples.append((n, mask(raw)[:240]))


def analyze(text: str, year: int | None = None, thresholds: dict | None = None) -> dict:
    """Scan the log text. Returns a language-neutral result; use localize()/to_markdown() to present it. Never raises on ordinary text."""
    th = dict(fail=5, fail_hi=20, spray_users=5, fail_before_ok=3, scan404=20, login_posts=10, auth_codes=10, e5xx=10, flood_min=100, ports=10, fw_blocks=20, errors=3)
    th.update(thresholds or {})
    year = year or datetime.now().year
    truncated = len(text or "") > MAX_BYTES
    lines = normalise((text or "")[:MAX_BYTES])
    if len(lines) > MAX_LINES:
        lines, truncated = lines[:MAX_LINES], True
    F: dict = {}

    def f(rid):
        return F.setdefault(rid, _F(rid))

    fails_by_ip: dict = defaultdict(int)
    users_by_ip: dict = defaultdict(set)
    all_ips, users_all = Counter(), Counter()
    status_c, level_c = Counter(), Counter()
    first = last = None
    parsed_ts = 0
    s404, s_auth, s5xx = Counter(), Counter(), Counter()
    ports_by_ip: dict = defaultdict(set)
    posts_login = Counter()
    per_min: dict = defaultdict(Counter)
    web_total = 0
    urls, hashes = Counter(), Counter()
    for n, raw in enumerate(lines, 1):
        ts = _ts(raw, year)
        if ts:
            parsed_ts += 1
            first = ts if first is None or ts < first else first
            last = ts if last is None or ts > last else last
        for ip in _IP_RE.findall(raw)[:6]:
            if _valid_ip(ip):
                all_ips[ip] += 1
        for u in _URL.findall(raw)[:3]:
            urls[mask(u)[:200]] += 1
        for h in _HASH.findall(raw)[:2]:
            hashes[h.lower()] += 1
        lv = _P["errlevel"].search(raw)
        if lv:
            level_c[lv.group(0).upper()] += 1
        low = raw.lower()
        # --- web access lines
        am = _ACCESS.match(raw) or _ACCESS.search(raw)
        is_web = bool(am)
        if am:
            web_total += 1
            ip, meth, path, st = am.group("ip"), am.group("m"), am.group("path"), am.group("st")
            ua, ref = am.group("ua") or "", am.group("ref") or ""
            status_c[st] += 1
            dec = unquote_plus(unquote_plus(path))
            blob = f"{dec} {ua} {ref}"
            for key, rid in (("sqli", "web_sqli"), ("xss", "web_xss"), ("traversal", "web_traversal"), ("cmdi", "web_cmdi")):
                if _P[key].search(blob):
                    f(rid).hit(n, raw, ip)
            if _P["sensitive"].search(dec):
                f("web_sensitive_files").hit(n, raw, ip)
            if _P["admin"].search(dec):
                f("web_admin_probe").hit(n, raw, ip)
            if _P["scanner"].search(ua):
                f("web_scanner").hit(n, raw, ip)
            if st == "404":
                s404[ip] += 1
            if st in ("401", "403"):
                s_auth[ip] += 1
            if st.startswith("5"):
                s5xx[ip] += 1
                f("server_errors").hit(n, raw, ip)
            if meth == "POST" and _P["login_path"].search(dec):
                posts_login[ip] += 1
            tsw = _ts(raw, year)
            if tsw:
                per_min[ip][tsw.strftime("%Y-%m-%d %H:%M")] += 1
        # --- authentication
        m = _SSH_FAIL.search(raw)
        if m:
            ip = m.group("ip") or m.group("ip2") or m.group("ip3")
            u = m.group("u") or m.group("u2") or m.group("u3") or ""
            fails_by_ip[ip] += 1
            if u:
                users_by_ip[ip].add(u)
                users_all[u] += 1
            f("ssh_bruteforce").hit(n, raw, ip, u)
        else:
            m2 = _SSH_OK.search(raw)
            if m2:
                ip, u = m2.group("ip"), m2.group("u")
                users_all[u] += 1
                if fails_by_ip.get(ip, 0) >= th["fail_before_ok"]:
                    f("login_after_failures").hit(n, raw, ip, u)
                if u == "root":
                    f("root_login").hit(n, raw, ip, u)
            elif _GEN_FAIL.search(raw) and not is_web:
                ips = [i for i in _IP_RE.findall(raw) if _valid_ip(i)]
                if ips:
                    fails_by_ip[ips[0]] += 1
                    f("ssh_bruteforce").hit(n, raw, ips[0])
        # --- Windows event IDs
        ev = _EVID.search(raw)
        if ev:
            eid = ev.group(1)
            ips = [i for i in _IP_RE.findall(raw) if _valid_ip(i) and i not in ("0.0.0.0", "127.0.0.1")]
            ip = ips[0] if ips else None
            um = re.search(r"(?:account ?name|targetusername|user)[=:\s]+([^\s,;]+)", raw, re.I)
            user = um.group(1) if um else None
            if eid in _FAIL_WIN:
                fails_by_ip[ip or "?"] += 1
                if ip and user:
                    users_by_ip[ip].add(user)
                f("windows_failed_logons").hit(n, raw, ip, user)
            elif eid in _ACCT_WIN:
                f("account_created").hit(n, raw, ip, user)
            elif eid in _PRIV_WIN:
                f("windows_privileged_change").hit(n, raw, ip, user)
            elif eid in _PERSIST_WIN:
                f("persistence").hit(n, raw, ip, user)
            elif eid == "1102" or eid == "104":
                f("log_tampering").hit(n, raw, ip, user)
            elif eid == "4624" and re.search(r"logon ?type[=:\s]+10\b", raw, re.I) and ip and _is_public(ip):
                f("rdp_external").hit(n, raw, ip, user)
        # --- firewall
        fm = _FW.search(raw)
        if fm and _P["fw_action"].search(raw) or (fm and "SRC=" in raw):
            src = fm.group("src") or fm.group("src2") or fm.group("src3")
            dpt = fm.group("dpt") or fm.group("dpt2") or fm.group("dpt3")
            if src and dpt:
                ports_by_ip[src].add(dpt)
                f("firewall_blocks").hit(n, raw, src)
        # --- host activity (not web access lines)
        if not is_web:
            if _P["malicious"].search(raw):
                f("malicious_command").hit(n, raw, (_IP_RE.findall(raw) or [None])[0])
            if _P["sudo"].search(raw):
                f("sudo_abuse").hit(n, raw)
            if _P["acct"].search(raw) and not (ev and ev.group(1) not in _ACCT_WIN):
                f("account_created").hit(n, raw)
            if _P["persistence"].search(raw):
                f("persistence").hit(n, raw)
            if _P["tamper"].search(raw):
                f("log_tampering").hit(n, raw)
            if _P["syserr"].search(raw):
                f("system_errors").hit(n, raw)
        elif _P["malicious"].search(raw) and _CMD_NOT_WEB.search(raw):
            f("malicious_command").hit(n, raw, am.group("ip"))
        if _has_secret(raw):
            f("secrets_in_logs").hit(n, raw)
    # --- aggregate rules
    for ip, cnt in list(fails_by_ip.items()):
        pass
    sb = F.get("ssh_bruteforce")
    if sb:
        keep = {ip: c for ip, c in sb.ips.items() if c >= th["fail_before_ok"] or c >= 1}
        if sb.count < th["fail"] and not any(c >= th["fail"] for c in sb.ips.values()):
            del F["ssh_bruteforce"]
        else:
            sb.extra["critical_at"] = th["fail_hi"]
        for ip, users in users_by_ip.items():
            if len(users) >= th["spray_users"]:
                sp = f("password_spraying")
                sp.hit(0, f"{ip} tried {len(users)} different user names: " + ", ".join(sorted(users)[:6]), ip, weight=len(users))
    wf = F.get("windows_failed_logons")
    if wf and wf.count < th["fail"]:
        del F["windows_failed_logons"]
    for ip, c in s404.items():
        if c >= th["scan404"]:
            f("http_scan_404").hit(0, f"{ip}: {c} requests answered 404", ip, weight=c)
    for ip in set(posts_login) | set(s_auth):
        if posts_login[ip] >= th["login_posts"] or s_auth[ip] >= th["auth_codes"]:
            f("http_login_bruteforce").hit(0, f"{ip}: {posts_login[ip]} login POSTs, {s_auth[ip]} answers 401/403", ip, weight=max(posts_login[ip], s_auth[ip]))
    if "server_errors" in F and F["server_errors"].count < th["e5xx"] and not (web_total >= 20 and F["server_errors"].count / web_total >= 0.05):
        del F["server_errors"]
    for ip, mins in per_min.items():
        worst = max(mins.values())
        if worst >= th["flood_min"]:
            f("request_flood").hit(0, f"{ip}: {worst} requests in one minute", ip, weight=worst)
    for ip, ports in ports_by_ip.items():
        if len(ports) >= th["ports"]:
            f("port_scan").hit(0, f"{ip} touched {len(ports)} different ports: " + ", ".join(sorted(ports, key=int)[:10]), ip, weight=len(ports))
    fb = F.get("firewall_blocks")
    if fb and fb.count < th["fw_blocks"]:
        del F["firewall_blocks"]
    if "web_admin_probe" in F and F["web_admin_probe"].count < 3:
        del F["web_admin_probe"]
    se = level_c.get("ERROR", 0) + level_c.get("CRITICAL", 0) + level_c.get("FATAL", 0) + level_c.get("EMERG", 0) + level_c.get("ALERT", 0) + level_c.get("SEVERE", 0)
    if se >= th["errors"] and "system_errors" not in F:
        e = f("error_levels")
        e.count = se
        for n, raw in enumerate(lines, 1):
            if _P["errlevel"].search(raw):
                e.samples.append((n, mask(raw)[:240]))
                if len(e.samples) >= 3:
                    break
    # --- results
    findings = []
    for rid, fd in F.items():
        sev = R[rid]["sev"]
        if rid == "ssh_bruteforce" and any(c >= th["fail_hi"] for c in fd.ips.values()):
            sev = "critical"
        findings.append({"id": rid, "severity": sev, "mitre": R[rid]["mitre"], "count": fd.count, "ips": [(ip, c, _is_public(ip)) for ip, c in fd.ips.most_common(8)],
                         "users": fd.users.most_common(6), "samples": fd.samples})
    findings.sort(key=lambda x: (-SEV[x["severity"]], -x["count"]))
    if not findings:
        findings.append({"id": "clean", "severity": "info", "mitre": "—", "count": 0, "ips": [], "users": [], "samples": []})
    weight = {"critical": 40, "high": 20, "medium": 8, "low": 2, "info": 0}
    score = min(100, sum(weight[x["severity"]] for x in findings))
    level = "critical" if score >= 70 else "high" if score >= 40 else "medium" if score >= 15 else "low" if score > 0 else "none"
    return {
        "stats": {"lines": len(lines), "with_time": parsed_ts, "first": first.isoformat(" ") if first else None, "last": last.isoformat(" ") if last else None,
                  "web_requests": web_total, "status": dict(status_c.most_common(8)), "levels": dict(level_c), "truncated": truncated},
        "findings": findings, "score": score, "level": level,
        "top_ips": [(ip, c, _is_public(ip)) for ip, c in all_ips.most_common(10)], "top_users": users_all.most_common(8),
        "iocs": {"ips": [ip for ip, _c in all_ips.most_common(60) if _is_public(ip)][:40], "urls": [u for u, _c in urls.most_common(25)], "hashes": [h for h, _c in hashes.most_common(20)]},
    }


# ------------------------------------------------------------------ presentation
LBL = {
    "en": dict(risk="Risk level", score="Risk score", lines="Lines read", period="Period", findings="Findings", evidence="Evidence", sources="Top addresses", users="Accounts seen", mitre="MITRE ATT&CK", why="Why it matters", do="What to do",
               levels={"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "none": "No known pattern", "info": "Info"}, times="occurrences", pub="public", priv="private", trunc="The log was longer than the limit, so only the first part was read.",
               caveat="This is rule-based screening. A finding is a lead to investigate, not proof of a break-in, and a clean result does not prove the system is safe. Logs are processed in memory only; secrets are masked.",
               iocs="Indicators to check", none_time="no timestamps found"),
    "fr": dict(risk="Niveau de risque", score="Score de risque", lines="Lignes lues", period="Période", findings="Constats", evidence="Preuves", sources="Adresses principales", users="Comptes observés", mitre="MITRE ATT&CK", why="Pourquoi c'est important", do="Que faire",
               levels={"critical": "Critique", "high": "Élevé", "medium": "Moyen", "low": "Faible", "none": "Aucun schéma connu", "info": "Info"}, times="occurrences", pub="publique", priv="privée", trunc="Le journal dépassait la limite : seule la première partie a été lue.",
               caveat="Il s'agit d'un filtrage par règles. Un constat est une piste à examiner, pas la preuve d'une intrusion, et un résultat propre ne prouve pas que le système est sûr. Les journaux sont traités en mémoire uniquement ; les secrets sont masqués.",
               iocs="Indicateurs à vérifier", none_time="aucun horodatage trouvé"),
    "rw": dict(risk="Urwego rw'ibyago", score="Amanota y'ibyago", lines="Imirongo isomwe", period="Igihe", findings="Ibyabonetse", evidence="Ibimenyetso", sources="Aderesi z'ingenzi", users="Konti zabonetse", mitre="MITRE ATT&CK", why="Impamvu bifite akamaro", do="Icyo wakora",
               levels={"critical": "Gikomeye cyane", "high": "Hejuru", "medium": "Hagati", "low": "Hasi", "none": "Nta shusho rizwi", "info": "Amakuru"}, times="inshuro", pub="rusange", priv="bwite", trunc="Log yarengeje igipimo, bityo igice cya mbere gusa cyasomwe.",
               caveat="Ni isuzuma rishingiye ku mategeko. Icyabonetse ni ikimenyetso cyo gukurikirana, si gihamya y'uko hinjiwe, kandi ibisubizo bisa neza ntibyemeza ko sisitemu itekanye. Logs zitunganyirizwa mu kwibuka gusa; amabanga arahishwa.",
               iocs="Ibimenyetso byo kugenzura", none_time="nta gihe cyabonetse"),
    "sw": dict(risk="Kiwango cha hatari", score="Alama ya hatari", lines="Mistari iliyosomwa", period="Kipindi", findings="Matokeo", evidence="Ushahidi", sources="Anwani kuu", users="Akaunti zilizoonekana", mitre="MITRE ATT&CK", why="Kwa nini ni muhimu", do="Unachoweza kufanya",
               levels={"critical": "Hatari sana", "high": "Juu", "medium": "Wastani", "low": "Chini", "none": "Hakuna mfumo unaojulikana", "info": "Taarifa"}, times="mara", pub="ya umma", priv="ya ndani", trunc="Kumbukumbu ilizidi kikomo, hivyo sehemu ya kwanza tu ilisomwa.",
               caveat="Huu ni uchujaji wa kanuni. Tokeo ni kidokezo cha kuchunguza, si ushahidi wa uvamizi, na tokeo safi halithibitishi mfumo uko salama. Kumbukumbu huchakatwa kwenye kumbukumbu ya kompyuta tu; siri zimefichwa.",
               iocs="Viashiria vya kukagua", none_time="hakuna muda uliopatikana"),
}


def localize(finding: dict, lang: str = "en") -> dict:
    """Finding with title / why / do in the language (English if unknown)."""
    lang = lang if lang in LANGS else "en"
    r = R[finding["id"]]
    return dict(finding, title=r["title"][lang], why=r["why"][lang], do=r["do"][lang])


def to_markdown(res: dict, lang: str = "en", max_findings: int = 12) -> str:
    lang = lang if lang in LANGS else "en"
    L = LBL[lang]
    s = res["stats"]
    out = [f"**{L['risk']}: {L['levels'][res['level']]}** ({L['score']}: {res['score']}/100) · {L['lines']}: {s['lines']}"
           + (f" · {L['period']}: {s['first']} → {s['last']}" if s["first"] else f" · {L['period']}: {L['none_time']}")]
    if s.get("truncated"):
        out.append(f"_{L['trunc']}_")
    for fd in res["findings"][:max_findings]:
        x = localize(fd, lang)
        head = f"### [{L['levels'][x['severity']]}] {x['title']}" + (f" — {x['count']} {L['times']}" if x["count"] else "")
        out += ["", head, f"{L['why']}: {x['why']}", f"{L['do']}: {x['do']}"]
        if x["mitre"] != "—":
            out.append(f"{L['mitre']}: {x['mitre']}")
        if x["ips"]:
            out.append(f"{L['sources']}: " + ", ".join(f"{ip} ({c}, {L['pub'] if p else L['priv']})" for ip, c, p in x["ips"][:5]))
        if x["samples"]:
            out.append(f"{L['evidence']}:")
            out += [f"    line {n}: {t}" if n else f"    {t}" for n, t in x["samples"][:3]]
    out += ["", f"_{L['caveat']}_"]
    return "\n".join(out)
