"""More cybersecurity overview hubs found missing by a routing probe: types of malware, security tools by job, what security engineers do, social-engineering
techniques, how passwords get stolen, a basic security audit, common scams by theme (Rwanda / East Africa), plus extra phrasings for existing guides.
Awareness-level and defensive: what attackers do so people can spot and stop it; no step-by-step attack instructions. Tools are named only as well-known
examples and must be used only on systems you own or have written permission to test. fr/rw/sw wording is a DRAFT for fluent review.
Registered from cyber_playbook_db.py with register(add, raw)."""
from textutil import fold

EXTRA_KW = {
    "cyb_secure_network": "how do i protect my company network|how to protect my company network|how to protect a company network|how to protect my business network|how do i secure my company network|how to secure a company network|how to secure my office network|how do i secure my home wifi|how to secure my home wifi|how to secure my wifi|how to secure my wifi router|how to protect my home network|how to secure a small business network|best practices for network security|best practices for securing a network|network security tips|comment bien securiser un reseau"
                          "|comment proteger mon reseau d'entreprise|comment proteger le reseau de mon entreprise|comment securiser le reseau de mon entreprise|comment securiser mon wifi a la maison|comment proteger mon reseau domestique"
                          "|uko warinda umuyoboro w'ikigo cyanjye|uko warinda umuyoboro w'ikigo|uko nakwirinda umuyoboro w'ikigo cyanjye|uko warinda wifi y'iwanjye|uko wakwirinda wifi yo mu rugo"
                          "|jinsi ya kulinda mtandao wa kampuni yangu|jinsi ya kulinda mtandao wa biashara yangu|jinsi ya kulinda wifi ya nyumbani|jinsi ya kulinda mtandao wa ofisi",
    "cyb_protect_momo": "how do i avoid mobile money scams|how to avoid mobile money scams|how can i avoid mobile money scams|how to protect my mobile money|avoid momo scams|how to avoid momo scams"
                        "|comment eviter les arnaques mobile money|comment eviter les arnaques a l'argent mobile|arnaques mobile money|arnaques a l'argent mobile"
                        "|nakwirinda nte uburiganya bwa mobile money|nakwirinda nte uburiganya bwa momo|uburiganya bwa mobile money|uburiganya bwa momo|uko wakwirinda uburiganya bwa mobile money|uko wakwirinda uburiganya bwa momo"
                        "|nitaepukaje utapeli wa pesa za simu|utapeli wa pesa za simu|utapeli wa mobile money|jinsi ya kuepuka utapeli wa pesa za simu|jinsi ya kuepuka utapeli wa mobile money",
    "cyb_personal_protection": "nigira nte umutekano wa interineti|nigira nte umutekano kuri interineti|nakwirinda nte kuri interineti|nigira nte umutekano wa murandasi|nifanyeje kuwa salama mtandaoni|nawezaje kuwa salama mtandaoni|comment me proteger sur internet|comment me proteger en ligne",
    "cyb_social_engineering": "abatekamutwe batuma bate abantu|uko abatekamutwe bagushuka|abatekamutwe bakora bate|abatekamutwe bashuka abantu bate|comment les escrocs manipulent les gens|comment les escrocs trompent les gens|matapeli hudanganyaje watu|matapeli hufanyaje",
    "cyb_defender_methods": "how do banks protect customers|how do banks protect their customers|how do banks keep money safe online|how do banks secure online banking|how do companies keep data safe|comment les banques protegent leurs clients|banki zirinda zite abakiriya|benki hulindaje wateja",
}

_L = lambda *x: list(x)


def _finish(raw):
    """After the new hubs exist: add extra phrasings, and let the specific new hubs win a phrase an older, broader guide also claimed."""
    for e, kws in raw:
        if e["id"] in EXTRA_KW:
            kws.extend(fold(k) for k in EXTRA_KW[e["id"]].split("|") if k.strip())
    mine = set()
    for e, kws in raw:
        if e["id"] in NEW_IDS:
            mine.update(kws)
    for e, kws in raw:
        if e["id"] not in NEW_IDS and e["id"] in ("cyb_accounts_hacked", "cyb_careers", "cyb_defender_methods", "cyb_hacker_methods"):
            kws[:] = [k for k in kws if k not in mine]


NEW_IDS = ("cyb_malware_types", "cyb_security_tools", "cyb_engineer_role", "cyb_social_engineering", "cyb_password_attacks", "cyb_security_audit", "cyb_scam_catalog")


def register(add, raw):

    # ---------------------------------------------------------------- types of malware
    add("cyb_malware_types",
        "types of malware|kinds of malware|malware types|what are the types of malware|what are the different types of malware|different types of malware|list of malware types|types of viruses|kinds of viruses|categories of malware|types of harmful software|types of malicious software|types of computer viruses|what is malware and its types|"
        "types de logiciels malveillants|types de malwares|quels sont les types de malware|quels sont les types de logiciels malveillants|differents types de malware|categories de malwares|types de virus informatiques|"
        "ubwoko bwa malware|ubwoko bwa porogaramu z'ubugizi bwa nabi|ni ubuhe bwoko bwa malware|ubwoko bwa virusi za mudasobwa|ubwoko bw'ama malware|ubwoko bwa virusi|"
        "aina za programu hasidi|aina za malware|aina za virusi za kompyuta|ni aina gani za malware|aina za virusi",
        ("Types of malware (harmful software) and how to stop each", "Types de logiciels malveillants (malware) et comment les arrêter", "Ubwoko bwa malware (porogaramu z'ubugizi bwa nabi) n'uko wahagarika buri bwoko", "Aina za programu hasidi (malware) na jinsi ya kuzizuia"),
        ("**Malware** is any software made to harm, spy on, control or steal from a device. Types differ by what they do and how they spread. Most reach people through **phishing, fake apps, cracked software, infected USB sticks and unpatched systems**.",
         "Un **malware** est tout logiciel conçu pour nuire, espionner, contrôler ou voler. Les types diffèrent par leur action et leur propagation. La plupart arrivent par **hameçonnage, fausses applications, logiciels crackés, clés USB infectées et systèmes non mis à jour**.",
         "**Malware** ni porogaramu yose yakozwe kugira ngo yangize, irebe rwihishwa, igenzure cyangwa yibe. Ubwoko butandukanira ku byo bukora n'uko bukwirakwira. Bwinshi butugeraho binyuze kuri **phishing, porogaramu z'impimbano, porogaramu zahinduwe (crack), USB zanduye na sisitemu zitavuguruwe**.",
         "**Malware** ni programu yoyote iliyotengenezwa kudhuru, kupeleleza, kudhibiti au kuiba. Aina hutofautiana kwa kazi na jinsi zinavyosambaa. Nyingi hufika kupitia **hadaa (phishing), programu bandia, programu zilizovunjwa (crack), USB zilizoambukizwa na mifumo isiyosasishwa**."),
        (_L("**1. Virus:** attaches itself to a file or program and spreads when you run it. *Stop it:* antivirus, do not open unknown files, keep software updated.",
            "**2. Worm:** spreads by itself across networks without you doing anything. *Stop it:* patch quickly, firewall, network segmentation.",
            "**3. Trojan horse:** looks useful (a free game, a cracked program, a fake update) but hides harmful code. *Stop it:* install only from official stores and the real vendor site.",
            "**4. Ransomware:** locks or encrypts files and demands payment (often with a threat to leak data). *Stop it:* offline backups (3-2-1), updates, no unknown attachments, MFA. Do not rely on paying.",
            "**5. Spyware, keyloggers, stalkerware and infostealers:** secretly record what you type or steal saved passwords, cookies and wallets. *Stop it:* check app permissions, MFA/passkeys, remove unknown apps, antivirus.",
            "**6. Adware, PUPs and scareware (fake antivirus):** flood you with ads or fake alarms to make you pay or install more. *Stop it:* do not call numbers in pop-ups; close the tab; uninstall unknown programs.",
            "**7. Bots and botnets:** your device is remote-controlled to attack others (DDoS) or send spam; common on cameras and routers with default passwords. *Stop it:* change default passwords, update firmware.",
            "**8. Rootkits and backdoors:** hide deep in the system and keep secret access. *Stop it:* Secure Boot, EDR, trusted sources; a clean reinstall may be needed.",
            "**9. Fileless and macro malware:** runs in memory or through Office macros and built-in tools instead of an obvious file. *Stop it:* block macros from the internet, EDR, least privilege.",
            "**10. Others:** banking trojans on phones (steal SMS codes), cryptojackers (use your CPU), wipers (destroy data), logic bombs. *Signs of infection:* slowness, unknown apps, pop-ups, battery drain, strange charges. *Act:* disconnect, scan, change passwords from a clean device, tell your bank."),
         _L("**1. Virus :** s'attache à un fichier ou programme et se propage quand vous l'exécutez. *Stop :* antivirus, n'ouvrez pas de fichiers inconnus, mises à jour.",
            "**2. Ver (worm) :** se propage seul à travers les réseaux sans action de votre part. *Stop :* correctifs rapides, pare-feu, segmentation.",
            "**3. Cheval de Troie :** semble utile (jeu gratuit, programme cracké, fausse mise à jour) mais cache du code nuisible. *Stop :* installez seulement depuis les boutiques officielles et le vrai site de l'éditeur.",
            "**4. Rançongiciel (ransomware) :** verrouille ou chiffre les fichiers et exige un paiement (souvent avec menace de fuite). *Stop :* sauvegardes hors ligne (3-2-1), mises à jour, pas de pièces jointes inconnues, MFA. Ne comptez pas sur le paiement.",
            "**5. Logiciels espions, keyloggers, stalkerware et infostealers :** enregistrent ce que vous tapez ou volent mots de passe, cookies et portefeuilles. *Stop :* vérifier les permissions, MFA/passkeys, supprimer les applications inconnues, antivirus.",
            "**6. Adware, PUP et scareware (faux antivirus) :** vous inondent de pub ou de fausses alertes pour vous faire payer ou installer plus. *Stop :* n'appelez pas les numéros des pop-ups ; fermez l'onglet ; désinstallez les programmes inconnus.",
            "**7. Bots et botnets :** votre appareil est piloté à distance pour attaquer d'autres (DDoS) ou envoyer du spam ; courant sur caméras et routeurs aux mots de passe par défaut. *Stop :* changer les mots de passe par défaut, mettre à jour le firmware.",
            "**8. Rootkits et portes dérobées :** se cachent au cœur du système et gardent un accès secret. *Stop :* Secure Boot, EDR, sources fiables ; une réinstallation propre peut être nécessaire.",
            "**9. Malwares sans fichier et à macros :** s'exécutent en mémoire ou via des macros Office et outils intégrés. *Stop :* bloquer les macros venant d'Internet, EDR, moindre privilège.",
            "**10. Autres :** chevaux de Troie bancaires sur téléphone (volent les codes SMS), cryptojackers (utilisent votre processeur), wipers (détruisent les données), bombes logiques. *Signes :* lenteur, applications inconnues, pop-ups, batterie qui chute, débits étranges. *Agir :* déconnecter, analyser, changer les mots de passe depuis un appareil sain, prévenir la banque."),
         _L("**1. Virus:** yifatanya na dosiye cyangwa porogaramu ikikwirakwiza iyo uyikoresheje. *Kuyirinda:* antivirus, ntufungure dosiye zitazwi, vugurura porogaramu.",
            "**2. Worm:** yikwirakwiza ubwayo mu miyoboro nta cyo ukoze. *Kuyirinda:* vugurura vuba, firewall, gutandukanya umuyoboro.",
            "**3. Trojan horse:** isa n'ifite akamaro (umukino w'ubuntu, porogaramu ya crack, ivugurura ry'impimbano) ariko ihishe code mbi. *Kuyirinda:* shyiraho gusa ziva mu maduka yemewe no ku rubuga nyarwo rw'uwayikoze.",
            "**4. Ransomware:** ifunga dosiye ikazisaba kwishyura (akenshi ikanavuga ko izasohora amakuru). *Kuyirinda:* backups zitari kuri interineti (3-2-1), ivugurura, nta attachments zitazwi, MFA. Ntukizere ko kwishyura bikemura.",
            "**5. Spyware, keyloggers, stalkerware na infostealers:** zandika ibyo wandika rwihishwa cyangwa zibye amagambo y'ibanga, cookies na wallets. *Kuyirinda:* genzura uburenganzira bwa porogaramu, MFA/passkeys, kuraho porogaramu zitazwi, antivirus.",
            "**6. Adware, PUPs na scareware (antivirus y'impimbano):** zikuzuza amatangazo cyangwa impuruza z'impimbano ngo wishyure cyangwa ushyireho izindi. *Kuyirinda:* ntuhamagare nimero ziri mu pop-ups; funga tab; kuraho porogaramu zitazwi.",
            "**7. Bots na botnets:** igikoresho cyawe kigenzurwa kure ngo gitere abandi (DDoS) cyangwa cyohereze spam; bikunze kuba kuri kamera na router zifite amagambo y'ibanga ya mbere. *Kuyirinda:* hindura amagambo y'ibanga ya mbere, vugurura firmware.",
            "**8. Rootkits na backdoors:** zihisha imbere muri sisitemu zikagumana uburenganzira bw'ibanga. *Kuyirinda:* Secure Boot, EDR, inkomoko zizewe; rimwe bisaba kongera gushyiraho sisitemu.",
            "**9. Fileless na macro malware:** ikorera mu kwibuka cyangwa binyuze kuri macros za Office n'ibikoresho bisanzwe. *Kuyirinda:* hagarika macros ziva kuri interineti, EDR, uburenganzira buke bukenewe.",
            "**10. Izindi:** banking trojans kuri telefone (ziba kode za SMS), cryptojackers (zikoresha CPU yawe), wipers (zisenya amakuru), logic bombs. *Ibimenyetso:* gutinda, porogaramu zitazwi, pop-ups, batiri ipfa vuba, kwishyuzwa bidasanzwe. *Icyo gukora:* kuzimya interineti, gusuzuma, guhindura amagambo y'ibanga uri ku gikoresho gisukuye, kubwira banki."),
         _L("**1. Virusi:** hujiambatisha kwenye faili au programu na kusambaa unapoiendesha. *Kuzuia:* antivirus, usifungue faili zisizojulikana, sasisha programu.",
            "**2. Worm:** hujisambaza yenyewe kupitia mitandao bila wewe kufanya chochote. *Kuzuia:* sasisha haraka, firewall, mgawanyo wa mtandao.",
            "**3. Trojan horse:** inaonekana ya manufaa (mchezo wa bure, programu iliyovunjwa, sasisho bandia) lakini imeficha msimbo hatari. *Kuzuia:* sakinisha kutoka maduka rasmi na tovuti halisi ya mtengenezaji tu.",
            "**4. Ransomware:** hufunga au kusimba faili na kudai malipo (mara nyingi na tishio la kuvujisha data). *Kuzuia:* nakala rudufu nje ya mtandao (3-2-1), masasisho, usifungue viambatisho visivyojulikana, MFA. Usitegemee kulipa.",
            "**5. Spyware, keyloggers, stalkerware na infostealers:** hurekodi unachoandika kwa siri au kuiba nywila, cookies na pochi. *Kuzuia:* kagua ruhusa za programu, MFA/passkeys, ondoa programu zisizojulikana, antivirus.",
            "**6. Adware, PUPs na scareware (antivirus bandia):** hukujaza matangazo au tahadhari bandia ili ulipe au usakinishe zaidi. *Kuzuia:* usipige namba za pop-up; funga kichupo; ondoa programu zisizojulikana.",
            "**7. Bots na botnets:** kifaa chako hudhibitiwa kwa mbali kushambulia wengine (DDoS) au kutuma spam; hutokea sana kwenye kamera na router zenye nywila za mwanzo. *Kuzuia:* badilisha nywila za mwanzo, sasisha firmware.",
            "**8. Rootkits na backdoors:** hujificha ndani ya mfumo na kuweka ufikiaji wa siri. *Kuzuia:* Secure Boot, EDR, vyanzo vinavyoaminika; wakati mwingine kusakinisha upya kunahitajika.",
            "**9. Fileless na macro malware:** hufanya kazi kwenye kumbukumbu au kupitia macros za Office na zana zilizojengewa. *Kuzuia:* zuia macros kutoka intaneti, EDR, haki ndogo kabisa.",
            "**10. Nyingine:** banking trojans kwenye simu (huiba misimbo ya SMS), cryptojackers (hutumia CPU yako), wipers (huharibu data), logic bombs. *Dalili:* kasi ndogo, programu zisizojulikana, pop-ups, betri kuisha haraka, makato ya ajabu. *Chukua hatua:* tenganisha intaneti, kagua, badilisha nywila kutoka kifaa safi, mjulishe benki.")),
        ("Types of malware", "Types de malware", "Ubwoko bwa malware", "Aina za malware"))

    # ---------------------------------------------------------------- security tools by job
    add("cyb_security_tools",
        "cybersecurity tools|cyber security tools|security tools|list of cybersecurity tools|cybersecurity tools list|tools used in cybersecurity|tools used by security engineers|tools used by hackers|hacking tools|tools security professionals use|what tools do cybersecurity professionals use|best cybersecurity tools|common cybersecurity tools|popular security tools|"
        "outils de cybersecurite|outils de securite|liste des outils de cybersecurite|quels sont les outils de cybersecurite|outils des pirates|outils de piratage|outils utilises en cybersecurite|"
        "ibikoresho by'umutekano wa interineti|ibikoresho by'umutekano|ibikoresho bya cybersecurity|ibikoresho abahackers bakoresha|ibikoresho by'abashinzwe umutekano|ni ibihe bikoresho by'umutekano wa interineti|ibikoresho bikoreshwa mu mutekano wa interineti|"
        "zana za usalama wa mtandao|zana za cybersecurity|vifaa vya usalama wa mtandao|zana wanazotumia wataalamu wa usalama|zana za wadukuzi|zana za usalama|ni zana gani za usalama wa mtandao",
        ("Cybersecurity tools by job (defenders, testers, investigators)", "Outils de cybersécurité par métier (défenseurs, testeurs, enquêteurs)", "Ibikoresho by'umutekano wa interineti ukurikije umurimo (abarinzi, abagerageza, abakora iperereza)", "Zana za usalama wa mtandao kulingana na kazi (watetezi, wajaribu, wachunguzi)"),
        ("Security work uses many tools; none is magic and each fits a job. Below are **well-known examples** by purpose. Use scanners and testing tools **only on systems you own or have written permission to test**: using them on others is illegal.",
         "Le travail de sécurité utilise beaucoup d'outils ; aucun n'est magique et chacun sert un usage. Voici des **exemples connus** par objectif. N'utilisez scanners et outils de test **que sur des systèmes qui vous appartiennent ou avec autorisation écrite** : les utiliser sur d'autres est illégal.",
         "Akazi k'umutekano gakoresha ibikoresho byinshi; nta gifite igitangaza kandi buri kimwe gifite icyo gikora. Hano ni **ingero zizwi** ukurikije intego. Koresha scanners n'ibikoresho byo kugerageza **gusa kuri sisitemu zawe cyangwa ufite uruhushya rwanditse**: kubikoresha ku bandi binyuranyije n'amategeko.",
         "Kazi ya usalama hutumia zana nyingi; hakuna ya uchawi na kila moja ina kazi yake. Hapa kuna **mifano inayojulikana** kulingana na madhumuni. Tumia scanners na zana za majaribio **kwenye mifumo yako tu au ukiwa na idhini ya maandishi**: kuzitumia kwa wengine ni kinyume cha sheria."),
        (_L("**Everyday protection:** password manager (Bitwarden, KeePass), authenticator app, built-in antivirus (Microsoft Defender), automatic updates, disk encryption (BitLocker, VeraCrypt), a trusted VPN.",
            "**Network defence:** firewalls (pfSense, OPNsense, Fortinet, Palo Alto), IDS/IPS (Snort, Suricata), web application firewall (WAF), DNS filtering, network access control.",
            "**Monitoring and response (SOC):** SIEM (Splunk, Elastic/ELK, Wazuh), EDR/XDR (Microsoft Defender for Endpoint, CrowdStrike, SentinelOne), SOAR for automatic playbooks, ticketing for incidents.",
            "**Vulnerability management:** scanners (Nessus, OpenVAS, Qualys), web testing (OWASP ZAP, Burp Suite), dependency and container scanning, patch management.",
            "**Authorised testing (penetration testers, red teams):** Kali Linux, Nmap (network mapping), Metasploit, Wireshark (packet analysis), John the Ripper/Hashcat (password auditing). Only with written permission and a defined scope.",
            "**Digital forensics and malware analysis:** Autopsy, Volatility (memory), disk imaging tools, sandboxes and online scanners such as VirusTotal.",
            "**Cryptography and secrets:** OpenSSL, GnuPG/PGP, certificate management, secrets vaults and hardware security keys (FIDO2).",
            "**Threat intelligence and OSINT:** MISP, VirusTotal, Shodan and Censys (see what your own systems expose), Have I Been Pwned (check your own email for breaches).",
            "**Awareness and governance:** phishing-simulation and training platforms, risk registers, compliance checklists (ISO 27001, NIST CSF, CIS Controls)."),
         _L("**Protection quotidienne :** gestionnaire de mots de passe (Bitwarden, KeePass), appli d'authentification, antivirus intégré (Microsoft Defender), mises à jour automatiques, chiffrement du disque (BitLocker, VeraCrypt), un VPN fiable.",
            "**Défense réseau :** pare-feu (pfSense, OPNsense, Fortinet, Palo Alto), IDS/IPS (Snort, Suricata), pare-feu applicatif web (WAF), filtrage DNS, contrôle d'accès réseau.",
            "**Surveillance et réponse (SOC) :** SIEM (Splunk, Elastic/ELK, Wazuh), EDR/XDR (Microsoft Defender for Endpoint, CrowdStrike, SentinelOne), SOAR pour les playbooks automatiques, tickets d'incident.",
            "**Gestion des vulnérabilités :** scanners (Nessus, OpenVAS, Qualys), tests web (OWASP ZAP, Burp Suite), analyse des dépendances et conteneurs, gestion des correctifs.",
            "**Tests autorisés (pentesteurs, red teams) :** Kali Linux, Nmap (cartographie réseau), Metasploit, Wireshark (analyse de paquets), John the Ripper/Hashcat (audit de mots de passe). Uniquement avec autorisation écrite et périmètre défini.",
            "**Forensique et analyse de malwares :** Autopsy, Volatility (mémoire), outils d'imagerie disque, bacs à sable et scanners en ligne comme VirusTotal.",
            "**Cryptographie et secrets :** OpenSSL, GnuPG/PGP, gestion de certificats, coffres de secrets et clés de sécurité matérielles (FIDO2).",
            "**Renseignement sur les menaces et OSINT :** MISP, VirusTotal, Shodan et Censys (voir ce que vos propres systèmes exposent), Have I Been Pwned (vérifier votre propre e-mail).",
            "**Sensibilisation et gouvernance :** plateformes de simulation d'hameçonnage et de formation, registres de risques, listes de conformité (ISO 27001, NIST CSF, CIS Controls)."),
         _L("**Kwirinda buri munsi:** password manager (Bitwarden, KeePass), porogaramu ya authenticator, antivirus isanzwemo (Microsoft Defender), ivugurura rikora ryonyine, encryption ya disiki (BitLocker, VeraCrypt), VPN yizewe.",
            "**Kurinda umuyoboro:** firewalls (pfSense, OPNsense, Fortinet, Palo Alto), IDS/IPS (Snort, Suricata), web application firewall (WAF), DNS filtering, network access control.",
            "**Gukurikirana no gusubiza (SOC):** SIEM (Splunk, Elastic/ELK, Wazuh), EDR/XDR (Microsoft Defender for Endpoint, CrowdStrike, SentinelOne), SOAR ya playbooks zikora ubwazo, tickets z'ibitero.",
            "**Gucunga intege nke:** scanners (Nessus, OpenVAS, Qualys), kugerageza web (OWASP ZAP, Burp Suite), gusuzuma dependencies na containers, gucunga ivugurura.",
            "**Kugerageza byemewe (pentesters, red teams):** Kali Linux, Nmap (gushushanya umuyoboro), Metasploit, Wireshark (gusesengura ipaki), John the Ripper/Hashcat (gusuzuma amagambo y'ibanga). Gusa ufite uruhushya rwanditse n'urwego rugenwe.",
            "**Forensics no gusesengura malware:** Autopsy, Volatility (kwibuka), ibikoresho byo gufotora disiki, sandboxes na scanners zo kuri interineti nka VirusTotal.",
            "**Cryptography n'amabanga:** OpenSSL, GnuPG/PGP, gucunga certificates, secrets vaults n'imfunguzo z'umutekano (FIDO2).",
            "**Threat intelligence na OSINT:** MISP, VirusTotal, Shodan na Censys (kureba ibyo sisitemu zawe zerekana), Have I Been Pwned (genzura imeri yawe).",
            "**Gukangurira no kuyobora:** porogaramu zo kwigana phishing no guhugura, risk registers, urutonde rw'ubuhuza (ISO 27001, NIST CSF, CIS Controls)."),
         _L("**Ulinzi wa kila siku:** kidhibiti cha nywila (Bitwarden, KeePass), programu ya authenticator, antivirus iliyojengewa (Microsoft Defender), masasisho ya kiotomatiki, usimbaji wa diski (BitLocker, VeraCrypt), VPN inayoaminika.",
            "**Ulinzi wa mtandao:** firewalls (pfSense, OPNsense, Fortinet, Palo Alto), IDS/IPS (Snort, Suricata), web application firewall (WAF), DNS filtering, network access control.",
            "**Ufuatiliaji na mwitikio (SOC):** SIEM (Splunk, Elastic/ELK, Wazuh), EDR/XDR (Microsoft Defender for Endpoint, CrowdStrike, SentinelOne), SOAR kwa playbooks za kiotomatiki, tiketi za matukio.",
            "**Usimamizi wa udhaifu:** scanners (Nessus, OpenVAS, Qualys), majaribio ya wavuti (OWASP ZAP, Burp Suite), ukaguzi wa dependencies na containers, usimamizi wa viraka.",
            "**Majaribio yaliyoidhinishwa (pentesters, red teams):** Kali Linux, Nmap (kuchora ramani ya mtandao), Metasploit, Wireshark (uchambuzi wa pakiti), John the Ripper/Hashcat (ukaguzi wa nywila). Kwa idhini ya maandishi na wigo uliobainishwa tu.",
            "**Forensics na uchambuzi wa malware:** Autopsy, Volatility (kumbukumbu), zana za kunakili diski, sandboxes na scanners za mtandaoni kama VirusTotal.",
            "**Kriptografia na siri:** OpenSSL, GnuPG/PGP, usimamizi wa vyeti, secrets vaults na funguo za usalama za kimwili (FIDO2).",
            "**Threat intelligence na OSINT:** MISP, VirusTotal, Shodan na Censys (kuona mifumo yako inaonyesha nini), Have I Been Pwned (kagua barua pepe yako).",
            "**Uhamasishaji na utawala:** majukwaa ya kuiga hadaa na mafunzo, risk registers, orodha za kufuata (ISO 27001, NIST CSF, CIS Controls).")),
        ("Tools by purpose", "Outils par usage", "Ibikoresho ukurikije intego", "Zana kulingana na madhumuni"))

    # ---------------------------------------------------------------- what security engineers do
    add("cyb_engineer_role",
        "what do security engineers do|what does a security engineer do|what does a cybersecurity engineer do|what do cybersecurity engineers do|role of a cybersecurity engineer|role of a security engineer|cybersecurity engineer job|security engineer job|security analyst job|what does a soc analyst do|what do soc analysts do|what is a soc analyst|what is a security operations centre job|what is a security operations center job|how do cybersecurity engineers work|responsibilities of a security engineer|duties of a security engineer|what is a penetration tester job|what do cybersecurity professionals do|"
        "que font les ingenieurs en cybersecurite|que fait un ingenieur en cybersecurite|role d'un ingenieur en cybersecurite|metier d'analyste soc|que fait un analyste soc|responsabilites d'un ingenieur securite|que font les professionnels de la cybersecurite|"
        "injeniyeri w'umutekano akora iki|injeniyeri z'umutekano zikora iki|inshingano z'injeniyeri w'umutekano|akazi k'umutekano wa interineti|umusesenguzi wa soc akora iki|abashinzwe umutekano wa interineti bakora iki|"
        "mhandisi wa usalama hufanya nini|wahandisi wa usalama hufanya nini|majukumu ya mhandisi wa usalama wa mtandao|mchambuzi wa soc hufanya nini|kazi ya mhandisi wa usalama|wataalamu wa usalama wa mtandao hufanya nini",
        ("What security engineers and defenders actually do", "Ce que font vraiment les ingénieurs et défenseurs en sécurité", "Icyo injeniyeri n'abarinzi b'umutekano bakora koko", "Wahandisi na watetezi wa usalama hufanya nini hasa"),
        ("Cybersecurity is a team sport with several roles. Together they **prevent** problems, **detect** them early, **respond** when they happen and **prove** that controls work. Here is what each role does day to day.",
         "La cybersécurité est un sport d'équipe avec plusieurs rôles. Ensemble ils **préviennent** les problèmes, les **détectent** tôt, **réagissent** quand ils arrivent et **prouvent** que les contrôles fonctionnent. Voici ce que fait chaque rôle au quotidien.",
         "Umutekano wa interineti ni umukino w'ikipe ufite inshingano nyinshi. Hamwe **bakumira** ibibazo, **babitahura** hakiri kare, **basubiza** igihe bibaye kandi **berekana** ko uburyo bwo kurinda bukora. Dore icyo buri nshingano ikora buri munsi.",
         "Usalama wa mtandao ni mchezo wa timu wenye majukumu mengi. Kwa pamoja **huzuia** matatizo, **hugundua** mapema, **hukabiliana** yanapotokea na **huthibitisha** kuwa vidhibiti vinafanya kazi. Hivi ndivyo kila jukumu hufanya kila siku."),
        (_L("**Security engineer:** builds and maintains defences: secure configurations, firewalls, identity and access (MFA, least privilege), encryption, patching, hardening servers and cloud accounts.",
            "**SOC analyst (security operations centre):** watches alerts from SIEM and EDR, decides what is real, investigates and escalates. Works in shifts; speed and good notes matter.",
            "**Incident responder:** when an attack happens: contain it, remove the attacker, recover from clean backups, preserve evidence and run a lessons-learned review.",
            "**Penetration tester / red team:** with written permission, simulates attackers to find weaknesses before criminals do, then reports how to fix them. **Blue team** defends; **purple team** helps both learn.",
            "**Vulnerability management analyst:** scans, ranks flaws by risk (CVSS and real exposure) and tracks fixes until closed.",
            "**Security architect:** designs systems securely from the start (zero trust, segmentation, secure design reviews, threat modelling).",
            "**Digital forensic and malware analysts:** reconstruct what happened from disks, memory and logs; study malware to write detections.",
            "**GRC, compliance and privacy (DPO):** policies, risk registers, audits (ISO 27001, NIST CSF, data-protection law), vendor checks and evidence for regulators.",
            "**Awareness trainer and champions:** teach staff to spot phishing and report incidents, because people are the first and last line of defence.",
            "**How to start:** learn networking, Linux, the web and basic scripting; practise on legal labs and CTFs; earn entry certifications (for example Security+). Ask «how to start a career in cybersecurity» for a roadmap."),
         _L("**Ingénieur sécurité :** construit et maintient les défenses : configurations sûres, pare-feu, identité et accès (MFA, moindre privilège), chiffrement, correctifs, durcissement des serveurs et comptes cloud.",
            "**Analyste SOC (centre d'opérations de sécurité) :** surveille les alertes du SIEM et de l'EDR, décide ce qui est réel, enquête et escalade. Travaille en équipes tournantes ; vitesse et bonnes notes comptent.",
            "**Répondant aux incidents :** lors d'une attaque : la contenir, chasser l'attaquant, restaurer depuis des sauvegardes saines, préserver les preuves et faire un retour d'expérience.",
            "**Pentesteur / red team :** avec autorisation écrite, simule des attaquants pour trouver les faiblesses avant les criminels, puis explique comment corriger. La **blue team** défend ; la **purple team** aide les deux à apprendre.",
            "**Analyste gestion des vulnérabilités :** scanne, classe les failles par risque (CVSS et exposition réelle) et suit les corrections jusqu'à clôture.",
            "**Architecte sécurité :** conçoit des systèmes sûrs dès le départ (zero trust, segmentation, revues de conception, modélisation des menaces).",
            "**Analystes forensique et malware :** reconstituent ce qui s'est passé à partir des disques, de la mémoire et des journaux ; étudient les malwares pour écrire des détections.",
            "**GRC, conformité et vie privée (DPO) :** politiques, registres de risques, audits (ISO 27001, NIST CSF, loi de protection des données), contrôle des fournisseurs et preuves pour les régulateurs.",
            "**Formateur sensibilisation et relais :** apprennent au personnel à repérer l'hameçonnage et à signaler les incidents, car les personnes sont la première et la dernière ligne de défense.",
            "**Pour débuter :** apprenez les réseaux, Linux, le web et un peu de script ; entraînez-vous sur des labs légaux et CTF ; passez des certifications d'entrée (par exemple Security+). Demandez « comment commencer une carrière en cybersécurité »."),
         _L("**Security engineer (injeniyeri w'umutekano):** yubaka kandi agakomeza uburinzi: igenamiterere ryizewe, firewalls, ukwemeza uwo uri we n'uburenganzira (MFA, uburenganzira buke), encryption, ivugurura, gukomeza seriveri na konti za cloud.",
            "**SOC analyst (ikigo gikurikirana umutekano):** areba impuruza za SIEM na EDR, agafata icyemezo ku by'ukuri, agakora iperereza agatanga raporo hejuru. Akora mu byiciro by'amasaha; umuvuduko n'inyandiko nziza biraremereye.",
            "**Incident responder:** igitero kibaye: akigabanya, agakura umushimusi, agasubiza ibintu kuri backups zisukuye, akabika ibimenyetso agakora isuzuma ry'amasomo.",
            "**Penetration tester / red team:** afite uruhushya rwanditse, yigana abashimusi kugira ngo abone intege nke mbere y'abagizi ba nabi, hanyuma agasobanura uko bikosorwa. **Blue team** irinda; **purple team** ifasha impande zombi kwiga.",
            "**Vulnerability management analyst:** asuzuma, agashyira intege nke mu byiciro ku byago (CVSS n'uko zigaragara) agakurikirana gukosora kugeza birangiye.",
            "**Security architect:** ategura sisitemu zizewe kuva ku ntangiriro (zero trust, gutandukanya, isuzuma ry'igishushanyo, threat modelling).",
            "**Forensic na malware analysts:** basubiza inyuma ibyabaye bakoresheje disiki, kwibuka na logs; biga malware kugira ngo bandike uburyo bwo gutahura.",
            "**GRC, ubuhuza n'ibanga (DPO):** amabwiriza, risk registers, igenzura (ISO 27001, NIST CSF, itegeko ryo kurengera amakuru), kugenzura abatanga serivisi n'ibimenyetso ku bagenzuzi.",
            "**Abigisha no kumenyekanisha:** bigisha abakozi gutahura phishing no kubimenyekanisha, kuko abantu ari rwo rwego rwa mbere n'urwa nyuma rwo kwirinda.",
            "**Uko watangira:** iga imiyoboro, Linux, web n'ibanze bya scripting; itoze mu ma labs yemewe na CTF; ufate impamyabumenyi z'intangiriro (urugero Security+). Baza «uko watangira umwuga wa cybersecurity»."),
         _L("**Security engineer (mhandisi wa usalama):** hujenga na kudumisha ulinzi: usanidi salama, firewalls, utambulisho na ufikiaji (MFA, haki ndogo), usimbaji, viraka, kuimarisha seva na akaunti za cloud.",
            "**SOC analyst (kituo cha operesheni za usalama):** hufuatilia tahadhari za SIEM na EDR, kuamua kipi ni halisi, kuchunguza na kupandisha ngazi. Hufanya kazi kwa zamu; kasi na maandishi mazuri ni muhimu.",
            "**Incident responder:** shambulio likitokea: huzuia, kumwondoa mshambulizi, kurejesha kutoka nakala safi, kuhifadhi ushahidi na kufanya mapitio ya mafunzo.",
            "**Penetration tester / red team:** kwa idhini ya maandishi, huiga washambuliaji kupata udhaifu kabla ya wahalifu, kisha huripoti jinsi ya kurekebisha. **Blue team** hutetea; **purple team** husaidia pande zote kujifunza.",
            "**Vulnerability management analyst:** hukagua, kupanga udhaifu kwa hatari (CVSS na mfichuo halisi) na kufuatilia marekebisho hadi kukamilika.",
            "**Security architect:** hubuni mifumo salama tangu mwanzo (zero trust, mgawanyo, mapitio ya muundo, threat modelling).",
            "**Forensic na malware analysts:** huunda upya kilichotokea kutoka diski, kumbukumbu na logs; husoma malware kuandika ugunduzi.",
            "**GRC, ufuasi na faragha (DPO):** sera, risk registers, ukaguzi (ISO 27001, NIST CSF, sheria ya ulinzi wa data), ukaguzi wa wasambazaji na ushahidi kwa wadhibiti.",
            "**Wakufunzi wa uhamasishaji:** hufundisha wafanyakazi kutambua hadaa na kuripoti matukio, kwa sababu watu ni safu ya kwanza na ya mwisho ya ulinzi.",
            "**Jinsi ya kuanza:** jifunze mitandao, Linux, wavuti na scripting ya msingi; jizoeze kwenye maabara halali na CTF; pata vyeti vya awali (mfano Security+). Uliza «jinsi ya kuanza taaluma ya cybersecurity».")),
        ("Roles in cybersecurity", "Rôles en cybersécurité", "Inshingano mu mutekano wa interineti", "Majukumu katika usalama wa mtandao"))

    # ---------------------------------------------------------------- social engineering
    add("cyb_social_engineering",
        "social engineering techniques|what are social engineering techniques|types of social engineering|social engineering methods|social engineering attacks|how does social engineering work|examples of social engineering|how to prevent social engineering|how to avoid social engineering|how to defend against social engineering|psychological tricks scammers use|manipulation tactics scammers use|how do scammers manipulate people|"
        "techniques d'ingenierie sociale|types d'ingenierie sociale|methodes d'ingenierie sociale|attaques d'ingenierie sociale|comment fonctionne l'ingenierie sociale|se proteger de l'ingenierie sociale|astuces psychologiques des escrocs|"
        "uburyo bwa social engineering|ubwoko bwa social engineering|uko social engineering ikora|uko wakwirinda social engineering|amayeri ya social engineering|uburiganya bukoresha abantu|uko abatekamutwe bakoresha imitekerereze|"
        "mbinu za social engineering|aina za social engineering|social engineering hufanyaje|jinsi ya kuepuka social engineering|mbinu za kisaikolojia za matapeli|ulaghai wa kijamii|jinsi matapeli wanavyodanganya watu",
        ("Social engineering: the tricks that manipulate people, and how to resist them", "Ingénierie sociale : les astuces qui manipulent les gens et comment y résister", "Social engineering: amayeri akoresha abantu n'uko wayirwanya", "Social engineering: hila zinazodanganya watu na jinsi ya kuzipinga"),
        ("**Social engineering** attacks people, not computers: the criminal tricks you into giving access, money or secrets. It works because it uses normal human instincts. Knowing the **levers** and the **techniques** makes them easy to spot.",
         "L'**ingénierie sociale** attaque les personnes, pas les ordinateurs : le criminel vous pousse à donner accès, argent ou secrets. Elle marche car elle exploite des réflexes humains normaux. Connaître les **leviers** et les **techniques** aide à les repérer.",
         "**Social engineering** itera abantu, si mudasobwa: umugizi wa nabi aragushuka ngo uhe uburenganzira, amafaranga cyangwa amabanga. Ikora kuko ikoresha imyitwarire y'ikiremwamuntu isanzwe. Kumenya **ibikoresho** n'**uburyo** bituma byoroha kubibona.",
         "**Social engineering** hushambulia watu, si kompyuta: mhalifu hukudanganya ili umpe ufikiaji, pesa au siri. Hufanya kazi kwa sababu hutumia silika za kawaida za binadamu. Kujua **vishawishi** na **mbinu** hurahisisha kuzitambua."),
        (_L("**Levers they pull:** authority (\"I am your boss/bank/police\"), urgency (\"in 10 minutes\"), fear (blocked account, arrest), greed (prize, easy money), trust and kindness (\"please help me\"), curiosity (\"see this photo\"), and social proof (\"everyone already paid\").",
            "**Phishing, smishing, vishing, quishing:** fake emails, SMS, calls and QR codes that push you to a fake page or to share a code.",
            "**Pretexting and impersonation:** a made-up story and a false identity (bank officer, IT support, MTN/Airtel agent, manager asking for an urgent payment: BEC).",
            "**Baiting and quid pro quo:** a free USB stick, free software or a \"free service\" in exchange for your login or an installed app.",
            "**Tailgating and shoulder surfing:** following someone through a door or watching your screen and PIN in public.",
            "**Romance, friendship and sextortion tricks:** weeks of trust-building, then a money request or a threat to share private images.",
            "**Fake emergencies and deepfakes:** a cloned voice or video of a relative or boss asking for money fast.",
            "**How to resist:** (1) **Pause**: urgency is the alarm. (2) **Verify on a second channel**: call back on a number you already have. (3) **Never share PIN, OTP or password** with anyone. (4) **Ask something only the real person knows** (agree a family code word). (5) **Check the address and sender details**, not the display name. (6) **Report and tell someone**: scammers rely on secrecy. (7) Organisations: callback rules for payments, two-person approval, regular awareness training."),
         _L("**Leviers utilisés :** autorité (« je suis votre patron/banque/police »), urgence (« dans 10 minutes »), peur (compte bloqué, arrestation), cupidité (gain, argent facile), confiance et gentillesse (« aidez-moi »), curiosité (« regardez cette photo »), preuve sociale (« tout le monde a déjà payé »).",
            "**Hameçonnage, smishing, vishing, quishing :** faux e-mails, SMS, appels et QR codes qui vous poussent vers une fausse page ou à partager un code.",
            "**Prétexte et usurpation d'identité :** histoire inventée et fausse identité (agent bancaire, support informatique, agent MTN/Airtel, directeur demandant un paiement urgent : fraude au président).",
            "**Appât et donnant-donnant :** une clé USB gratuite, un logiciel ou un « service gratuit » contre vos identifiants ou l'installation d'une appli.",
            "**Filature et regard par-dessus l'épaule :** suivre quelqu'un à travers une porte ou observer votre écran et PIN en public.",
            "**Ruses sentimentales et sextorsion :** des semaines pour gagner confiance, puis demande d'argent ou menace de diffuser des images privées.",
            "**Fausses urgences et deepfakes :** voix ou vidéo clonée d'un proche ou d'un patron demandant vite de l'argent.",
            "**Comment résister :** (1) **Faites une pause** : l'urgence est l'alarme. (2) **Vérifiez par un second canal** : rappelez un numéro que vous avez déjà. (3) **Ne donnez jamais PIN, OTP ou mot de passe**. (4) **Posez une question que seule la vraie personne connaît** (mot-code familial). (5) **Vérifiez l'adresse et l'expéditeur**, pas le nom affiché. (6) **Signalez et parlez-en** : les escrocs comptent sur le secret. (7) Organisations : rappel obligatoire pour les paiements, double validation, formations régulières."),
         _L("**Ibyo bakoresha:** ubutegetsi («ndi umuyobozi wawe/banki/polisi»), kwihutisha («mu minota 10»), ubwoba (konti ifunzwe, gufungwa), umururumba (igihembo, amafaranga yoroshye), icyizere n'ineza («mfasha»), amatsiko («reba iyi foto»), n'icyizere rusange («bose barishyuye»).",
            "**Phishing, smishing, vishing, quishing:** imeri, SMS, guhamagara na QR code by'impimbano bigukanda ku rupapuro rw'impimbano cyangwa gusangiza kode.",
            "**Pretexting no kwiyoberanya:** inkuru ihimbano n'umwirondoro w'ikinyoma (umukozi wa banki, IT support, umukozi wa MTN/Airtel, umuyobozi usaba kwishyura byihuse: BEC).",
            "**Baiting na quid pro quo:** USB y'ubuntu, porogaramu cyangwa «serivisi y'ubuntu» usabwa guha konti yawe cyangwa gushyiraho porogaramu.",
            "**Tailgating na shoulder surfing:** gukurikira umuntu mu muryango cyangwa kureba ecran na PIN yawe ahantu hahurira abantu.",
            "**Uburiganya bw'urukundo, ubucuti na sextortion:** ibyumweru byo kubaka icyizere, hanyuma gusaba amafaranga cyangwa iterabwoba ryo gusohora amafoto bwite.",
            "**Impanuka z'ibinyoma na deepfakes:** ijwi cyangwa videwo bya mwene wanyu cyangwa umuyobozi byakopwe bisaba amafaranga byihuse.",
            "**Uko wabirwanya:** (1) **Hagarara gato**: kwihutishwa ni impuruza. (2) **Genzura ukoresheje undi muyoboro**: hamagara nimero usanzwe ufite. (3) **Ntuzigere uha undi PIN, OTP cyangwa ijambo ry'ibanga**. (4) **Baza ikintu umuntu nyawe wenyine azi** (ijambo ry'ibanga ry'umuryango). (5) **Genzura aderesi n'uwohereje**, si izina rigaragara. (6) **Menyesha ubibwire umuntu**: abatekamutwe bashingira ku ibanga. (7) Ibigo: guhamagara kugenzura ubwishyu, abantu babiri bemeza, amahugurwa asanzwe."),
         _L("**Vishawishi wanavyotumia:** mamlaka («mimi ni bosi/benki/polisi»), haraka («ndani ya dakika 10»), hofu (akaunti kufungwa, kukamatwa), tamaa (zawadi, pesa rahisi), uaminifu na wema («nisaidie»), udadisi («ona picha hii»), na ushahidi wa kijamii («wote wamelipa»).",
            "**Hadaa, smishing, vishing, quishing:** barua pepe, SMS, simu na misimbo ya QR bandia inayokupeleka kwenye ukurasa bandia au kushiriki msimbo.",
            "**Pretexting na kujifanya mtu mwingine:** hadithi ya kubuni na utambulisho wa uongo (afisa wa benki, msaada wa IT, wakala wa MTN/Airtel, meneja anayeomba malipo ya haraka: BEC).",
            "**Baiting na quid pro quo:** USB ya bure, programu au «huduma ya bure» badala ya akaunti yako au kusakinisha programu.",
            "**Tailgating na shoulder surfing:** kumfuata mtu mlangoni au kuangalia skrini na PIN yako hadharani.",
            "**Hila za mapenzi, urafiki na sextortion:** wiki za kujenga uaminifu, kisha ombi la pesa au kitisho cha kusambaza picha za faragha.",
            "**Dharura bandia na deepfakes:** sauti au video iliyonakiliwa ya ndugu au bosi anayeomba pesa haraka.",
            "**Jinsi ya kupinga:** (1) **Simama kidogo**: haraka ni kengele ya hatari. (2) **Hakiki kwa njia ya pili**: piga tena kwa namba uliyonayo. (3) **Kamwe usimpe mtu PIN, OTP au nywila**. (4) **Uliza kitu anachokijua mtu halisi tu** (neno la siri la familia). (5) **Kagua anwani na mtumaji**, si jina linaloonekana. (6) **Ripoti na umwambie mtu**: matapeli hutegemea usiri. (7) Mashirika: kupiga tena kuhakiki malipo, idhini ya watu wawili, mafunzo ya mara kwa mara.")),
        ("Social engineering", "Ingénierie sociale", "Social engineering", "Social engineering"))

    # ---------------------------------------------------------------- how passwords get stolen
    add("cyb_password_attacks",
        "how do hackers steal passwords|how do attackers steal passwords|how do hackers get passwords|how are passwords stolen|how do attackers crack passwords|how do hackers crack passwords|password attacks|types of password attacks|how do passwords get hacked|how passwords get stolen|how do hackers guess passwords|how do hackers hack passwords|ways passwords are stolen|"
        "comment les pirates volent des mots de passe|comment les pirates volent les mots de passe|comment les mots de passe sont voles|attaques de mots de passe|types d'attaques de mots de passe|comment les pirates devinent les mots de passe|comment les pirates piratent les mots de passe|"
        "uko abahackers biba amagambo y'ibanga|uko amagambo y'ibanga yibwa|ibitero ku magambo y'ibanga|ubwoko bw'ibitero ku magambo y'ibanga|abahackers bakoresha uburyo ki biba amagambo y'ibanga|uko abahackers bamenya amagambo y'ibanga|"
        "wadukuzi huiba nywila vipi|jinsi nywila zinavyoibwa|mashambulizi ya nywila|aina za mashambulizi ya nywila|jinsi wadukuzi wanavyoiba nywila|wadukuzi hufanyaje kuiba nywila",
        ("How passwords get stolen or guessed, and how to protect yours", "Comment les mots de passe sont volés ou devinés, et comment protéger les vôtres", "Uko amagambo y'ibanga yibwa cyangwa akagerageza, n'uko warinda ayawe", "Jinsi nywila zinavyoibwa au kukisiwa, na jinsi ya kulinda zako"),
        ("Passwords are stolen far more often by **tricks and leaks** than by clever guessing. The best protection is a **long unique password for every account + multi-factor authentication (MFA) or passkeys**. (Awareness only: this explains the methods defenders block.)",
         "Les mots de passe sont bien plus souvent volés par des **ruses et fuites** que par des devinettes astucieuses. La meilleure protection : **un mot de passe long et unique par compte + authentification multifacteur (MFA) ou passkeys**. (Sensibilisation seulement : on explique les méthodes que les défenseurs bloquent.)",
         "Amagambo y'ibanga yibwa cyane **binyuze mu mayeri no kumeneka kw'amakuru** kuruta kuyagerageza. Uburinzi bwiza ni **ijambo ry'ibanga rirerire kandi ryihariye kuri buri konti + multi-factor authentication (MFA) cyangwa passkeys**. (Ni ukwigisha gusa: busobanura uburyo abarinzi bahagarika.)",
         "Nywila huibwa mara nyingi zaidi kwa **hila na uvujaji** kuliko kukisia kwa ujanja. Ulinzi bora ni **nywila ndefu ya kipekee kwa kila akaunti + uthibitishaji wa hatua nyingi (MFA) au passkeys**. (Uhamasishaji tu: inaeleza mbinu ambazo watetezi huzuia.)"),
        (_L("**Phishing and fake login pages:** you type your password into a lookalike page. *Defence:* check the address, open sites yourself, use passkeys (they refuse fake sites).",
            "**Infostealers and keyloggers:** malware on your device records or steals saved passwords and session cookies. *Defence:* official apps only, no cracked software, antivirus, remove unknown apps.",
            "**Credential stuffing:** passwords leaked from one site are tried on many others. *Defence:* never reuse passwords; check your email on Have I Been Pwned.",
            "**Brute force, dictionary and password spraying:** programs try many guesses; short or common passwords (123456, password, names, dates) fall quickly. *Defence:* 14+ characters or a passphrase, lockouts and rate limits.",
            "**Data breaches and weak hashing:** stolen databases can be cracked offline when sites store passwords badly. *Defence (for developers):* salted slow hashes (Argon2, bcrypt); for users, unique passwords limit the damage.",
            "**Social tricks:** fake IT support, shoulder surfing, someone watching you type a PIN. *Defence:* never tell anyone a password or code.",
            "**Session and cookie theft, SIM swap, MFA fatigue:** attackers skip the password. *Defence:* log out of shared devices, protect your SIM with a PIN and your mobile-money PIN, never approve MFA prompts you did not start.",
            "**Public Wi-Fi and evil twins:** fake hotspots capture traffic. *Defence:* HTTPS only, VPN, avoid logging in to banking on public Wi-Fi.",
            "**Your checklist:** password manager, unique passwords, MFA/passkeys on email, banking, mobile money and social media, a recovery email and phone you control, and change a password at once if it appears in a breach."),
         _L("**Hameçonnage et fausses pages de connexion :** vous saisissez le mot de passe sur une page imitée. *Défense :* vérifiez l'adresse, ouvrez les sites vous-même, utilisez des passkeys (elles refusent les faux sites).",
            "**Infostealers et keyloggers :** un malware enregistre ou vole mots de passe enregistrés et cookies de session. *Défense :* applications officielles, pas de logiciels crackés, antivirus, supprimer les applis inconnues.",
            "**Credential stuffing :** les mots de passe fuités d'un site sont essayés sur beaucoup d'autres. *Défense :* ne jamais réutiliser ; vérifiez votre e-mail sur Have I Been Pwned.",
            "**Force brute, dictionnaire et password spraying :** des programmes essaient beaucoup de combinaisons ; mots de passe courts ou courants (123456, password, prénoms, dates) tombent vite. *Défense :* 14+ caractères ou une phrase secrète, verrouillage et limites d'essais.",
            "**Fuites de données et hachage faible :** des bases volées se cassent hors ligne quand les sites stockent mal les mots de passe. *Défense (développeurs) :* hachages lents salés (Argon2, bcrypt) ; pour les utilisateurs, des mots de passe uniques limitent les dégâts.",
            "**Ruses sociales :** faux support informatique, regard par-dessus l'épaule, quelqu'un qui voit votre PIN. *Défense :* ne dites jamais un mot de passe ou code.",
            "**Vol de session/cookie, SIM swap, fatigue MFA :** l'attaquant contourne le mot de passe. *Défense :* déconnectez-vous des appareils partagés, protégez votre SIM et le PIN d'argent mobile, n'approuvez jamais une demande MFA que vous n'avez pas lancée.",
            "**Wi-Fi public et faux points d'accès :** les faux hotspots capturent le trafic. *Défense :* HTTPS uniquement, VPN, évitez la banque sur Wi-Fi public.",
            "**Votre check-list :** gestionnaire de mots de passe, mots de passe uniques, MFA/passkeys sur e-mail, banque, argent mobile et réseaux sociaux, e-mail et téléphone de récupération que vous contrôlez, et changez-le tout de suite s'il apparaît dans une fuite."),
         _L("**Phishing n'impapuro z'impimbano zo kwinjira:** wandika ijambo ry'ibanga ku rupapuro rusa n'urwukuri. *Kwirinda:* genzura aderesi, fungura imbuga ubwawe, koresha passkeys (zanga imbuga z'impimbano).",
            "**Infostealers na keyloggers:** malware ku gikoresho cyawe yandika cyangwa ikiba amagambo y'ibanga abitswe na cookies. *Kwirinda:* porogaramu zemewe gusa, nta porogaramu za crack, antivirus, kuraho izitazwi.",
            "**Credential stuffing:** amagambo y'ibanga yamenetse ku rubuga rumwe agerageza ku zindi nyinshi. *Kwirinda:* ntuzongere gukoresha ijambo rimwe; genzura imeri yawe kuri Have I Been Pwned.",
            "**Brute force, dictionary na password spraying:** porogaramu zigerageza byinshi; amagambo magufi cyangwa asanzwe (123456, password, amazina, amatariki) yanyuranwa vuba. *Kwirinda:* inyuguti 14+ cyangwa interuro y'ibanga, gufunga nyuma y'ibigerageza byinshi.",
            "**Kumeneka kw'amakuru na hashing mbi:** database zibwe zishobora gucibwa nta interineti iyo imbuga zibika nabi amagambo y'ibanga. *Kwirinda (abategura):* hashes zitinda zifite salt (Argon2, bcrypt); ku bakoresha, amagambo yihariye agabanya ibyangirika.",
            "**Amayeri y'abantu:** IT support y'impimbano, kureba hejuru y'urutugu, umuntu ureba PIN yawe. *Kwirinda:* ntuzigere uvuga ijambo ry'ibanga cyangwa kode.",
            "**Kwiba session/cookie, SIM swap, MFA fatigue:** umushimusi arenga ijambo ry'ibanga. *Kwirinda:* sohoka ku bikoresho dusangiye, rinda SIM na PIN ya mobile money, ntuzigere wemeza icyifuzo cya MFA utatangije.",
            "**Wi-Fi rusange na evil twins:** hotspots z'impimbano zifata amakuru. *Kwirinda:* HTTPS gusa, VPN, irinde banki kuri Wi-Fi rusange.",
            "**Urutonde rwawe:** password manager, amagambo yihariye, MFA/passkeys ku imeri, banki, mobile money n'imbuga nkoranyambaga, imeri na telefone yo kugarura ugenzura, kandi uhindure ijambo ry'ibanga ako kanya nirigaragara mu byamenetse."),
         _L("**Hadaa na kurasa za kuingia bandia:** unaandika nywila kwenye ukurasa unaofanana. *Ulinzi:* kagua anwani, fungua tovuti mwenyewe, tumia passkeys (hukataa tovuti bandia).",
            "**Infostealers na keyloggers:** malware kwenye kifaa hurekodi au kuiba nywila zilizohifadhiwa na cookies za kikao. *Ulinzi:* programu rasmi tu, hakuna programu zilizovunjwa, antivirus, ondoa programu zisizojulikana.",
            "**Credential stuffing:** nywila zilizovuja kutoka tovuti moja hujaribiwa kwenye nyingi. *Ulinzi:* usitumie nywila moja tena; kagua barua pepe yako kwenye Have I Been Pwned.",
            "**Brute force, dictionary na password spraying:** programu hujaribu kukisia mengi; nywila fupi au za kawaida (123456, password, majina, tarehe) huvunjika haraka. *Ulinzi:* herufi 14+ au kauli ya siri, kufungwa na kikomo cha majaribio.",
            "**Uvujaji wa data na hashing dhaifu:** hifadhidata zilizoibwa huvunjwa nje ya mtandao tovuti zikihifadhi nywila vibaya. *Ulinzi (watengenezaji):* hashes za polepole zenye salt (Argon2, bcrypt); kwa watumiaji, nywila za kipekee hupunguza madhara.",
            "**Hila za kijamii:** msaada bandia wa IT, kuangalia juu ya bega, mtu anayeona PIN yako. *Ulinzi:* kamwe usimwambie mtu nywila au msimbo.",
            "**Wizi wa kikao/cookie, SIM swap, MFA fatigue:** mshambulizi hupita nywila. *Ulinzi:* toka kwenye vifaa vya pamoja, linda SIM na PIN ya pesa za simu, kamwe usikubali ombi la MFA ambalo hukuanzisha.",
            "**Wi-Fi ya umma na evil twins:** hotspots bandia hunasa trafiki. *Ulinzi:* HTTPS tu, VPN, epuka benki kwenye Wi-Fi ya umma.",
            "**Orodha yako:** kidhibiti cha nywila, nywila za kipekee, MFA/passkeys kwenye barua pepe, benki, pesa za simu na mitandao ya kijamii, barua pepe na simu ya kurejesha unayodhibiti, na ubadilishe nywila mara moja ikionekana kwenye uvujaji.")),
        ("How passwords get stolen", "Comment les mots de passe sont volés", "Uko amagambo y'ibanga yibwa", "Jinsi nywila zinavyoibwa"))

    # ---------------------------------------------------------------- basic security audit
    add("cyb_security_audit",
        "how to do a security audit|how to conduct a security audit|how to perform a security audit|security audit checklist|how to audit security|how to check if my system is secure|how to test if my network is secure|how to assess security|how to do a risk assessment|basic security assessment|cybersecurity checklist for small business|security review checklist|how to check if my website is secure|how do i know if my system is secure|how to carry out a security assessment|"
        "comment faire un audit de securite|comment realiser un audit de securite|checklist audit de securite|comment verifier la securite de mon systeme|evaluation des risques de securite|liste de controle de cybersecurite|comment savoir si mon systeme est securise|"
        "uko wakora igenzura ry'umutekano|uko wasuzuma umutekano wa sisitemu|urutonde rwo kugenzura umutekano|uko wasuzuma ibyago by'umutekano|igenzura ry'umutekano|uko wamenya niba sisitemu yanjye itekanye|"
        "jinsi ya kufanya ukaguzi wa usalama|orodha ya ukaguzi wa usalama|jinsi ya kukagua usalama wa mfumo|jinsi ya kutathmini hatari za usalama|jinsi ya kujua mfumo wangu ni salama",
        ("How to do a basic security audit or risk assessment", "Comment faire un audit de sécurité ou une évaluation des risques de base", "Uko wakora igenzura ry'umutekano cyangwa isuzuma ry'ibyago ry'ibanze", "Jinsi ya kufanya ukaguzi wa msingi wa usalama au tathmini ya hatari"),
        ("A security audit asks three questions: **what do we have, what could go wrong, and are our protections really working?** This is a practical small-organisation version based on NIST CSF and CIS Controls. For legal or certification audits (ISO 27001, regulators) hire a qualified auditor.",
         "Un audit de sécurité pose trois questions : **qu'avons-nous, que peut-il arriver et nos protections fonctionnent-elles vraiment ?** Voici une version pratique pour petites organisations, fondée sur NIST CSF et CIS Controls. Pour les audits légaux ou de certification (ISO 27001, régulateurs), faites appel à un auditeur qualifié.",
         "Igenzura ry'umutekano ribaza ibibazo bitatu: **dufite iki, ni iki gishobora kuba, kandi uburyo bwacu bwo kurinda bukora koko?** Iyi ni verisiyo ifatika ku bigo bito ishingiye kuri NIST CSF na CIS Controls. Ku igenzura ry'amategeko cyangwa impamyabumenyi (ISO 27001, abagenzuzi) fata umugenzuzi wabigize umwuga.",
         "Ukaguzi wa usalama huuliza maswali matatu: **tuna nini, nini kinaweza kwenda vibaya, na ulinzi wetu unafanya kazi kweli?** Hii ni toleo la vitendo kwa mashirika madogo kulingana na NIST CSF na CIS Controls. Kwa ukaguzi wa kisheria au vyeti (ISO 27001, wadhibiti) ajiri mkaguzi mwenye sifa."),
        (_L("**1. Scope and inventory:** list devices, accounts, apps, websites, cloud services and who owns each. You cannot protect what you do not know you have.",
            "**2. Find the valuable data:** customer records, money, mobile-money access, passwords, business secrets; note where it is stored and who can reach it.",
            "**3. Identify threats and risks:** for each asset, what could happen (phishing, ransomware, theft, insider, outage) and rate **likelihood × impact** (low, medium, high). Fix the highest first.",
            "**4. Check accounts and access:** MFA on email, admin and money accounts; remove former staff; no shared logins; least privilege.",
            "**5. Check updates and vulnerabilities:** operating systems, apps, router, website plug-ins patched; run a vulnerability scan on systems you own.",
            "**6. Check backups:** 3-2-1 rule, one copy offline, and **test a restore** (many backups fail only when needed).",
            "**7. Check network and devices:** firewall on, strong Wi-Fi (WPA2/WPA3), guest network, disk encryption, screen locks, antivirus/EDR, no exposed remote desktop.",
            "**8. Check logging and response:** are sign-ins logged, are alerts watched, is there a written incident plan with phone numbers?",
            "**9. Check people:** awareness training, a phishing test, a clear way to report suspicious messages without blame.",
            "**10. Report and retest:** write findings by priority with an owner and date, fix them, then check again every 6-12 months. Test only systems you own or have written permission to test."),
         _L("**1. Périmètre et inventaire :** listez appareils, comptes, applications, sites, services cloud et leur responsable. On ne protège pas ce qu'on ne connaît pas.",
            "**2. Repérer les données de valeur :** fichiers clients, argent, accès argent mobile, mots de passe, secrets d'affaires ; notez où elles sont et qui y accède.",
            "**3. Identifier menaces et risques :** pour chaque actif, ce qui peut arriver (hameçonnage, rançongiciel, vol, interne, panne) et notez **probabilité × impact** (faible, moyen, élevé). Traitez les plus élevés d'abord.",
            "**4. Vérifier comptes et accès :** MFA sur e-mail, admin et comptes d'argent ; retirer les anciens employés ; pas de comptes partagés ; moindre privilège.",
            "**5. Vérifier mises à jour et vulnérabilités :** systèmes, applications, routeur, extensions de site à jour ; lancez un scan de vulnérabilités sur vos propres systèmes.",
            "**6. Vérifier les sauvegardes :** règle 3-2-1, une copie hors ligne, et **testez une restauration** (beaucoup de sauvegardes échouent seulement au moment du besoin).",
            "**7. Vérifier réseau et appareils :** pare-feu actif, Wi-Fi solide (WPA2/WPA3), réseau invité, chiffrement du disque, verrouillage d'écran, antivirus/EDR, pas de bureau à distance exposé.",
            "**8. Vérifier journaux et réponse :** les connexions sont-elles journalisées, les alertes surveillées, existe-t-il un plan d'incident écrit avec numéros ?",
            "**9. Vérifier les personnes :** formation, test d'hameçonnage, moyen clair de signaler un message suspect sans reproche.",
            "**10. Rapporter et retester :** consignez les constats par priorité avec responsable et date, corrigez, puis revérifiez tous les 6 à 12 mois. Ne testez que des systèmes qui vous appartiennent ou avec autorisation écrite."),
         _L("**1. Urwego n'urutonde:** andika ibikoresho, konti, porogaramu, imbuga, serivisi za cloud n'ubishinzwe. Ntushobora kurinda ibyo utazi ko ufite.",
            "**2. Shaka amakuru y'agaciro:** amadosiye y'abakiriya, amafaranga, uburenganzira bwa mobile money, amagambo y'ibanga, amabanga y'ubucuruzi; andika aho abitse n'ubishobora kuyageraho.",
            "**3. Menya iterabwoba n'ibyago:** kuri buri kintu, ibyashoboka (phishing, ransomware, kwibwa, umukozi w'imbere, kuzimya) ushyire **amahirwe × ingaruka** (hasi, hagati, hejuru). Banza ibiri hejuru.",
            "**4. Genzura konti n'uburenganzira:** MFA ku imeri, admin na konti z'amafaranga; kuraho abakozi bagiye; nta konti dusangiye; uburenganzira buke bukenewe.",
            "**5. Genzura ivugurura n'intege nke:** sisitemu, porogaramu, router, ibyongerwa by'urubuga bivuguruye; kora vulnerability scan kuri sisitemu zawe.",
            "**6. Genzura backups:** itegeko rya 3-2-1, kopi imwe itari kuri interineti, kandi **gerageza kugarura** (backups nyinshi zinanirwa gusa igihe zikenewe).",
            "**7. Genzura umuyoboro n'ibikoresho:** firewall ifunguye, Wi-Fi ikomeye (WPA2/WPA3), umuyoboro w'abashyitsi, encryption ya disiki, gufunga ecran, antivirus/EDR, nta remote desktop ku mugaragaro.",
            "**8. Genzura logs no gusubiza:** kwinjira birandikwa, impuruza zirakurikiranwa, hari gahunda y'ibitero yanditse ifite nimero?",
            "**9. Genzura abantu:** amahugurwa, igerageza rya phishing, uburyo bugaragara bwo kumenyekanisha ubutumwa bukemangwa nta gucirwa urubanza.",
            "**10. Tanga raporo wongere ugerageze:** andika ibyabonetse ukurikije ibyihutirwa hamwe n'ubibazwa n'itariki, ukosore, hanyuma wongere ugenzure buri mezi 6-12. Gerageza gusa sisitemu zawe cyangwa ufite uruhushya rwanditse."),
         _L("**1. Wigo na orodha:** orodhesha vifaa, akaunti, programu, tovuti, huduma za cloud na mmiliki wa kila kimoja. Huwezi kulinda usichokijua.",
            "**2. Tafuta data muhimu:** rekodi za wateja, pesa, ufikiaji wa pesa za simu, nywila, siri za biashara; andika ilipo na nani anaifikia.",
            "**3. Tambua vitisho na hatari:** kwa kila mali, nini kinaweza kutokea (hadaa, ransomware, wizi, mtu wa ndani, kuharibika) na kadiria **uwezekano × athari** (chini, wastani, juu). Shughulikia za juu kwanza.",
            "**4. Kagua akaunti na ufikiaji:** MFA kwenye barua pepe, admin na akaunti za pesa; ondoa wafanyakazi walioondoka; hakuna akaunti za pamoja; haki ndogo kabisa.",
            "**5. Kagua masasisho na udhaifu:** mifumo, programu, router, viongezi vya tovuti vimesasishwa; fanya vulnerability scan kwenye mifumo yako.",
            "**6. Kagua nakala rudufu:** kanuni ya 3-2-1, nakala moja nje ya mtandao, na **jaribu kurejesha** (nakala nyingi hushindwa wakati wa kuhitajika tu).",
            "**7. Kagua mtandao na vifaa:** firewall imewashwa, Wi-Fi imara (WPA2/WPA3), mtandao wa wageni, usimbaji wa diski, kufunga skrini, antivirus/EDR, hakuna remote desktop wazi.",
            "**8. Kagua logs na mwitikio:** kuingia kunarekodiwa, tahadhari zinafuatiliwa, kuna mpango wa matukio ulioandikwa wenye namba?",
            "**9. Kagua watu:** mafunzo, jaribio la hadaa, njia wazi ya kuripoti ujumbe wa kutiliwa shaka bila lawama.",
            "**10. Ripoti na ujaribu tena:** andika matokeo kwa kipaumbele na mwenye jukumu na tarehe, rekebisha, kisha kagua tena kila miezi 6-12. Jaribu mifumo yako tu au ukiwa na idhini ya maandishi.")),
        ("Security audit steps", "Étapes d'un audit de sécurité", "Intambwe z'igenzura ry'umutekano", "Hatua za ukaguzi wa usalama"))

    # ---------------------------------------------------------------- common scams by theme
    add("cyb_scam_catalog",
        "common scams in rwanda|common scams in africa|common scams in east africa|most common scams|common types of scams|types of scams in rwanda|scams in rwanda|what are the most common scams|popular scams|scam types explained|categories of scams|scams to watch out for|biggest scams today|most common scams in rwanda|what scams exist in rwanda|common online scams|common scams today|scam categories|"
        "arnaques courantes au rwanda|arnaques courantes|arnaques les plus courantes|types d'arnaques courantes|arnaques en afrique|categories d'arnaques|arnaques a connaitre|quelles sont les arnaques courantes|arnaques frequentes|"
        "uburiganya bukunze kuba mu rwanda|uburiganya bukunze kubaho|ni ubuhe buriganya bukunze kuba|uburiganya bwo muri afurika|ubwoko bw'uburiganya bukunze kubaho|ni ubuhe buriganya bukunze kuba mu rwanda|uburiganya bwa none|"
        "utapeli wa kawaida nchini rwanda|utapeli wa kawaida|aina za utapeli zinazojulikana|utapeli katika afrika mashariki|aina za utapeli ni zipi|matapeli wa kawaida|ni utapeli gani ni wa kawaida",
        ("Common scams by theme (Rwanda and East Africa) and how to avoid each", "Arnaques courantes par thème (Rwanda et Afrique de l'Est) et comment les éviter", "Uburiganya bukunze kubaho ukurikije ingingo (u Rwanda na Afurika y'Iburasirazuba) n'uko wabwirinda", "Utapeli wa kawaida kwa mada (Rwanda na Afrika Mashariki) na jinsi ya kuuepuka"),
        ("Scams change names but follow a few **patterns**: they imitate someone you trust, rush you, and ask for money, a code or your login. Here are the main themes. Say **\"list all types of scams\"** for the full catalogue of 100 scams, or the name of one scam for details.",
         "Les arnaques changent de nom mais suivent quelques **schémas** : elles imitent quelqu'un de confiance, vous pressent et demandent argent, code ou identifiants. Voici les grands thèmes. Dites **« liste de tous les types d'arnaques »** pour le catalogue complet de 100 arnaques, ou le nom d'une arnaque pour les détails.",
         "Uburiganya buhindura amazina ariko bukurikiza **uburyo buke**: bwigana umuntu wizeye, bukwihutisha, bugasaba amafaranga, kode cyangwa konti yawe. Dore ingingo nyamukuru. Vuga **«urutonde rw'ubwoko bwose bw'uburiganya»** ubone urutonde rwuzuye rw'uburiganya 100, cyangwa izina ry'uburiganya runaka kugira ngo ubone ibisobanuro.",
         "Utapeli hubadilisha majina lakini hufuata **mifumo** michache: huiga mtu unayemwamini, hukuharakisha, na kuomba pesa, msimbo au akaunti yako. Hizi ndizo mada kuu. Sema **«orodha ya aina zote za utapeli»** kupata orodha kamili ya utapeli 100, au jina la utapeli mmoja kwa maelezo."),
        (_L("**Mobile money and SIM:** \"sent by mistake, please return\", fake customer care or agent, SIM swap, USSD tricks. *Rule:* never share PIN/OTP; check the balance yourself in the official menu; ask the operator to reverse, not the stranger.",
            "**Phishing and impersonation:** fake bank, MTN/Airtel, RRA, Irembo or police messages with links or urgent threats. *Rule:* do not click; open the official app or type the address yourself.",
            "**Jobs, visas and scholarships:** pay-to-apply fees, fake recruiters, overseas jobs that can end in trafficking. *Rule:* real employers do not charge to hire; verify with the official embassy or ministry.",
            "**Shopping and marketplaces:** fake shops, fake proof of payment, overpayment refund trick, deposit-first sellers, fake delivery fees. *Rule:* pay on delivery or through protected payment; check the seller and reviews.",
            "**Investment, crypto, betting and doubling money:** Ponzi schemes, \"guaranteed returns\", pig butchering, forex or crypto tutors. *Rule:* guaranteed high profit is the red flag; check the licence with the regulator.",
            "**Romance, friendship and sextortion:** an online lover who needs money or threatens to share images. *Rule:* never send money or intimate images to someone you have not met; reverse-search their photos.",
            "**Prizes, lotteries, giveaways, charity and religious appeals:** you \"won\" something you never entered, or a fake fundraiser. *Rule:* real prizes never need a fee; verify charities.",
            "**Tech support, fake apps and loan apps:** pop-ups \"your phone has a virus\", APK files, instant-loan apps that steal contacts. *Rule:* official stores only; never install remote-control apps for a stranger.",
            "**Family emergency, voice cloning and deepfakes:** \"it's me, I'm in trouble, send money\". *Rule:* call back on the known number; agree a family code word.",
            "**Business scams:** invoice and bank-detail changes (BEC), fake tenders, domain-renewal and fake government fines. *Rule:* verify any payment change by phone with a known number and use two-person approval. If you already paid or shared a code: ask «what to do if I was scammed»."),
         _L("**Argent mobile et SIM :** « envoyé par erreur, merci de renvoyer », faux service client ou agent, SIM swap, astuces USSD. *Règle :* ne donnez jamais PIN/OTP ; vérifiez le solde vous-même dans le menu officiel ; demandez à l'opérateur d'annuler, pas à l'inconnu.",
            "**Hameçonnage et usurpation :** faux messages de banque, MTN/Airtel, RRA, Irembo ou police avec liens ou menaces urgentes. *Règle :* ne cliquez pas ; ouvrez l'appli officielle ou tapez l'adresse vous-même.",
            "**Emplois, visas et bourses :** frais pour postuler, faux recruteurs, emplois à l'étranger pouvant finir en traite. *Règle :* un vrai employeur ne fait pas payer l'embauche ; vérifiez auprès de l'ambassade ou du ministère.",
            "**Achats et places de marché :** fausses boutiques, faux justificatifs de paiement, ruse du trop-perçu, vendeurs exigeant un acompte, faux frais de livraison. *Règle :* payez à la livraison ou via un paiement protégé ; vérifiez vendeur et avis.",
            "**Investissement, crypto, paris et doublement d'argent :** schémas de Ponzi, « rendements garantis », pig butchering, formateurs forex ou crypto. *Règle :* un gros profit garanti est le signal d'alerte ; vérifiez la licence auprès du régulateur.",
            "**Romance, amitié et sextorsion :** un amoureux en ligne qui veut de l'argent ou menace de diffuser des images. *Règle :* n'envoyez jamais argent ni images intimes à quelqu'un que vous n'avez pas rencontré ; faites une recherche inversée de ses photos.",
            "**Gains, loteries, concours, charité et appels religieux :** vous avez « gagné » sans avoir participé, ou fausse collecte. *Règle :* un vrai gain n'exige jamais de frais ; vérifiez les associations.",
            "**Support technique, fausses applis et applis de prêt :** pop-ups « votre téléphone a un virus », fichiers APK, applis de prêt instantané qui volent les contacts. *Règle :* boutiques officielles uniquement ; n'installez jamais d'appli de prise en main pour un inconnu.",
            "**Urgence familiale, clonage de voix et deepfakes :** « c'est moi, j'ai un problème, envoie de l'argent ». *Règle :* rappelez le numéro connu ; convenez d'un mot-code familial.",
            "**Arnaques aux entreprises :** factures et changements de coordonnées bancaires (fraude au président), faux appels d'offres, renouvellement de domaine et fausses amendes officielles. *Règle :* vérifiez tout changement de paiement par téléphone sur un numéro connu et exigez une double validation. Si vous avez déjà payé ou donné un code : demandez « que faire si j'ai été arnaqué »."),
         _L("**Mobile money na SIM:** «nohereje kubw'impanuka, nsubiza», serivisi y'abakiriya cyangwa umukozi w'impimbano, SIM swap, amayeri ya USSD. *Itegeko:* ntuzigere utanga PIN/OTP; reba amafaranga ubwawe mu menu yemewe; saba sosiyete gusubiza, si umuntu utazi.",
            "**Phishing no kwiyoberanya:** ubutumwa bw'impimbano bwa banki, MTN/Airtel, RRA, Irembo cyangwa polisi bufite link cyangwa iterabwoba ryihutirwa. *Itegeko:* ntukande; fungura porogaramu yemewe cyangwa wandike aderesi ubwawe.",
            "**Akazi, viza na buruse:** amafaranga yo gusaba akazi, abashaka abakozi b'impimbano, akazi ko hanze gashobora kuvamo gucuruza abantu. *Itegeko:* umukoresha nyawe ntacisha amafaranga ngo agutange; genzura kuri ambasade cyangwa minisiteri.",
            "**Guhaha no mu isoko rya interineti:** amaduka y'impimbano, gihamya y'ubwishyu y'impimbano, uburiganya bw'amafaranga arenze, abagurisha basaba avansi, amafaranga y'impimbano yo kugezwaho. *Itegeko:* ishyura wakiriye cyangwa unyuze mu bwishyu burinzwe; genzura umugurisha n'ibitekerezo.",
            "**Ishoramari, crypto, kubeta no kongera amafaranga kabiri:** gahunda za Ponzi, «inyungu yemewe», pig butchering, abigisha forex cyangwa crypto. *Itegeko:* inyungu nini yemezwa ni ikimenyetso gikomeye; genzura uruhushya ku rwego rubishinzwe.",
            "**Urukundo, ubucuti na sextortion:** umukunzi wo kuri interineti usaba amafaranga cyangwa uteza ubwoba bwo gusohora amafoto. *Itegeko:* ntuzigere wohereza amafaranga cyangwa amafoto y'ubwambure ku utarigeze ubonana; shakisha amafoto ye ukoresheje reverse search.",
            "**Ibihembo, tombola, giveaways, ubugiraneza n'ibyifuzo by'amadini:** «watsinze» ikintu utigeze witabira, cyangwa gukusanya inkunga y'impimbano. *Itegeko:* igihembo nyacyo ntigisaba amafaranga; genzura imiryango.",
            "**Tech support, porogaramu z'impimbano n'iz'inguzanyo:** pop-ups «telefone yawe ifite virusi», dosiye za APK, porogaramu z'inguzanyo zihuse ziba contacts. *Itegeko:* amaduka yemewe gusa; ntuzigere ushyiraho porogaramu yo kugenzura kure ku muntu utazi.",
            "**Impanuka y'umuryango, gukopera ijwi na deepfakes:** «ni njye, mfite ikibazo, ohereza amafaranga». *Itegeko:* hamagara nimero uzi; mwumvikane ijambo ry'ibanga ry'umuryango.",
            "**Uburiganya mu bucuruzi:** fagitire no guhindura konti ya banki (BEC), amasoko y'impimbano, kongera domain n'ibihano bya Leta by'impimbano. *Itegeko:* genzura impinduka zose z'ubwishyu kuri telefone ukoresheje nimero uzi kandi usabe abantu babiri kwemeza. Niba waramaze kwishyura cyangwa gutanga kode: baza «nkore iki nariganyijwe»."),
         _L("**Pesa za simu na SIM:** «nimetuma kimakosa, rudisha», huduma kwa wateja au wakala bandia, SIM swap, hila za USSD. *Kanuni:* kamwe usitoe PIN/OTP; angalia salio mwenyewe kwenye menyu rasmi; mwombe mtoa huduma kurejesha, si mgeni.",
            "**Hadaa na kujifanya mtu mwingine:** jumbe bandia za benki, MTN/Airtel, RRA, Irembo au polisi zenye viungo au vitisho vya haraka. *Kanuni:* usibofye; fungua programu rasmi au andika anwani mwenyewe.",
            "**Kazi, viza na ufadhili:** ada za kuomba kazi, waajiri bandia, kazi za nje zinazoweza kuishia kwenye usafirishaji wa binadamu. *Kanuni:* mwajiri halisi hatozi ada ya kuajiri; hakiki kwa ubalozi au wizara.",
            "**Ununuzi na masoko ya mtandaoni:** maduka bandia, uthibitisho bandia wa malipo, hila ya malipo ya ziada, wauzaji wanaodai amana, ada bandia za uwasilishaji. *Kanuni:* lipa unapopokea au kwa malipo yaliyolindwa; kagua muuzaji na maoni.",
            "**Uwekezaji, crypto, kubeti na kuongeza pesa mara mbili:** Ponzi, «faida ya uhakika», pig butchering, wakufunzi wa forex au crypto. *Kanuni:* faida kubwa ya uhakika ni alama ya hatari; hakiki leseni kwa mdhibiti.",
            "**Mapenzi, urafiki na sextortion:** mpenzi wa mtandaoni anayehitaji pesa au anayetishia kusambaza picha. *Kanuni:* kamwe usitume pesa au picha za faragha kwa usiyekutana naye; tafuta picha zake kwa reverse search.",
            "**Zawadi, bahati nasibu, giveaways, hisani na maombi ya kidini:** «umeshinda» ulichokiingia hukuingia, au michango bandia. *Kanuni:* zawadi halisi haihitaji ada; hakiki mashirika.",
            "**Msaada wa kiufundi, programu bandia na programu za mikopo:** pop-ups «simu yako ina virusi», faili za APK, programu za mkopo wa haraka zinazoiba anwani. *Kanuni:* maduka rasmi tu; kamwe usisakinishe programu ya kudhibiti kwa mgeni.",
            "**Dharura ya familia, kunakili sauti na deepfakes:** «ni mimi, nina shida, tuma pesa». *Kanuni:* piga tena kwa namba unayoijua; kubaliane neno la siri la familia.",
            "**Utapeli wa biashara:** ankara na mabadiliko ya akaunti ya benki (BEC), zabuni bandia, upyaji wa domain na faini bandia za serikali. *Kanuni:* hakiki mabadiliko ya malipo kwa simu kwa namba unayoijua na utumie idhini ya watu wawili. Kama tayari ulilipa au kutoa msimbo: uliza «nifanye nini nikitapeliwa».")),
        ("Scam themes", "Thèmes d'arnaques", "Ingingo z'uburiganya", "Mada za utapeli"))
    _finish(raw)
