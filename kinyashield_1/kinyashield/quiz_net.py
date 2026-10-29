"""Networks quiz topic ("networks"): ports, acronyms, OSI layers, transport protocols, subnetting (computed with the ipaddress module, so every answer is exact),
binary/decimal/hex conversion, address types and 76 hand-written concept questions. fr/rw/sw wording is a draft for fluent review. Deterministic (fixed seeds)."""
import ipaddress
from quiz_gen_util import rnd, place, tokens, mask, LANGS
from quiz_cyber_gen import Q_TERM, SLIP, ACRONYMS

T = lambda en, fr, rw, sw: (en, fr, rw, sw)
# ---------- ports
PORTS = [("HTTP", 80, "TCP"), ("HTTPS", 443, "TCP"), ("FTP (control)", 21, "TCP"), ("SSH", 22, "TCP"), ("Telnet", 23, "TCP"), ("SMTP", 25, "TCP"), ("DNS", 53, "UDP/TCP"),
    ("DHCP server", 67, "UDP"), ("DHCP client", 68, "UDP"), ("TFTP", 69, "UDP"), ("Kerberos", 88, "TCP/UDP"), ("POP3", 110, "TCP"), ("NTP", 123, "UDP"), ("NetBIOS session", 139, "TCP"),
    ("IMAP", 143, "TCP"), ("SNMP", 161, "UDP"), ("BGP", 179, "TCP"), ("LDAP", 389, "TCP/UDP"), ("SMB", 445, "TCP"), ("IKE (IPsec)", 500, "UDP"), ("Syslog", 514, "UDP"),
    ("SMTP submission", 587, "TCP"), ("LDAPS", 636, "TCP"), ("IMAPS", 993, "TCP"), ("POP3S", 995, "TCP"), ("MS SQL Server", 1433, "TCP"), ("RADIUS authentication", 1812, "UDP"),
    ("OpenVPN", 1194, "UDP"), ("Oracle database", 1521, "TCP"), ("NFS", 2049, "TCP/UDP"), ("MySQL", 3306, "TCP"), ("RDP", 3389, "TCP"), ("PostgreSQL", 5432, "TCP"),
    ("VNC", 5900, "TCP"), ("Redis", 6379, "TCP"), ("HTTP alternate", 8080, "TCP"), ("MongoDB", 27017, "TCP")]
QP1 = T("Which default port does {s} use?", "Quel port par défaut utilise {s} ?", "{s} ikoresha port ihabwa mbere ni iyihe?", "{s} hutumia mlango upi kwa chaguo-msingi?")
QP2 = T("Which service normally uses port {p}?", "Quel service utilise normalement le port {p} ?", "Serivisi ikunze gukoresha port {p} ni iyihe?", "Huduma gani kwa kawaida hutumia mlango {p}?")
WP = T("{s} uses port {p} ({t}).", "{s} utilise le port {p} ({t}).", "{s} ikoresha port {p} ({t}).", "{s} hutumia mlango {p} ({t}).")
SP = T("Well-known ports are fixed by IANA; learn the common ones in pairs (HTTP 80 / HTTPS 443, SMTP 25 / IMAP 143).", "Les ports connus sont fixés par l'IANA ; apprenez les courants par paires (HTTP 80 / HTTPS 443, SMTP 25 / IMAP 143).",
       "Port zizwi zashyizweho na IANA; wige izisanzwe mu bikombe (HTTP 80 / HTTPS 443, SMTP 25 / IMAP 143).", "Milango maarufu imewekwa na IANA; jifunze ya kawaida kwa jozi (HTTP 80 / HTTPS 443, SMTP 25 / IMAP 143).")
# ---------- protocols -> transport / layer
TRANSPORT = [("HTTP", "TCP"), ("HTTPS", "TCP"), ("SSH", "TCP"), ("FTP", "TCP"), ("SMTP", "TCP"), ("IMAP", "TCP"), ("POP3", "TCP"), ("Telnet", "TCP"), ("RDP", "TCP"), ("BGP", "TCP"),
    ("DHCP", "UDP"), ("TFTP", "UDP"), ("NTP", "UDP"), ("SNMP", "UDP"), ("Syslog", "UDP"), ("RIP", "UDP"), ("RADIUS", "UDP"), ("VoIP media (RTP)", "UDP")]
QT = T("Which transport protocol does {s} normally use?", "Quel protocole de transport {s} utilise-t-il normalement ?", "{s} ikunze gukoresha protocole ki yo gutwara?", "{s} kwa kawaida hutumia itifaki gani ya usafirishaji?")
WT = T("{s} normally runs over {t}.", "{s} fonctionne normalement sur {t}.", "{s} ikunze gukora kuri {t}.", "{s} kwa kawaida hufanya kazi juu ya {t}.")
ST = T("TCP is used when every byte must arrive in order; UDP when speed matters more than perfect delivery.", "TCP sert quand chaque octet doit arriver dans l'ordre ; UDP quand la vitesse compte plus que la livraison parfaite.",
       "TCP ikoreshwa iyo buri byte rigomba kugera ku murongo; UDP iyo umuvuduko ufite agaciro kurusha kugerwaho neza.", "TCP hutumika kila baiti inapofika kwa mpangilio; UDP kasi inapozidi uhakika wa kufikisha.")
LAYERS = {1: T("Layer 1 – Physical", "Couche 1 – Physique", "Urwego rwa 1 – Physical", "Safu ya 1 – Physical"), 2: T("Layer 2 – Data link", "Couche 2 – Liaison de données", "Urwego rwa 2 – Data link", "Safu ya 2 – Data link"),
    3: T("Layer 3 – Network", "Couche 3 – Réseau", "Urwego rwa 3 – Network", "Safu ya 3 – Network"), 4: T("Layer 4 – Transport", "Couche 4 – Transport", "Urwego rwa 4 – Transport", "Safu ya 4 – Transport"),
    5: T("Layer 5 – Session", "Couche 5 – Session", "Urwego rwa 5 – Session", "Safu ya 5 – Session"), 6: T("Layer 6 – Presentation", "Couche 6 – Présentation", "Urwego rwa 6 – Presentation", "Safu ya 6 – Presentation"),
    7: T("Layer 7 – Application", "Couche 7 – Application", "Urwego rwa 7 – Application", "Safu ya 7 – Application")}
OSI = [("HTTP", 7), ("DNS", 7), ("SMTP", 7), ("FTP", 7), ("SSH", 7), ("DHCP", 7), ("TLS encryption/decryption of data", 6), ("Data format conversion and compression", 6), ("Opening, maintaining and closing a dialogue between two applications", 5),
    ("TCP", 4), ("UDP", 4), ("Port numbers", 4), ("Segments", 4), ("IP address", 3), ("IPv6", 3), ("ICMP", 3), ("Router", 3), ("Packets", 3), ("MAC address", 2), ("Switch", 2),
    ("Ethernet frames", 2), ("Bridge", 2), ("Hub", 1), ("Repeater", 1), ("Cables and radio signals (bits)", 1), ("Network interface card (NIC) at the lowest level: voltage and pulses", 1)]
QO = T("At which OSI layer does this work: {s}?", "À quelle couche OSI se situe : {s} ?", "Ibi bikorera ku rwego rwa OSI rwa he: {s}?", "Hili linafanya kazi katika safu gani ya OSI: {s}?")
WO = T("{s} belongs to the {l}.", "{s} appartient à la {l}.", "{s} ni ikya {l}.", "{s} ni la {l}.")
SO = T("Remember the order from the bottom: Physical, Data link, Network, Transport, Session, Presentation, Application.", "Retenez l'ordre du bas vers le haut : Physique, Liaison, Réseau, Transport, Session, Présentation, Application.",
       "Wibuke uko bikurikirana uhereye hasi: Physical, Data link, Network, Transport, Session, Presentation, Application.", "Kumbuka mpangilio kutoka chini: Physical, Data link, Network, Transport, Session, Presentation, Application.")
QL = T("What is the name of OSI layer {n}?", "Quel est le nom de la couche OSI {n} ?", "Urwego rwa OSI rwa {n} rwitwa iki?", "Safu ya OSI namba {n} inaitwaje?")
WL = T("OSI layer {n} is {l}.", "La couche OSI {n} est : {l}.", "Urwego rwa OSI rwa {n} ni {l}.", "Safu ya OSI namba {n} ni {l}.")
PDU = [("Bits", 1), ("Frame", 2), ("Packet", 3), ("Segment (TCP) or datagram (UDP)", 4), ("Data (message)", 7)]
QU = T("Which unit of data (PDU) is used at OSI layer {n}?", "Quelle unité de données (PDU) est utilisée à la couche OSI {n} ?", "Ni uwuhe mubare w'amakuru (PDU) ukoreshwa ku rwego rwa OSI rwa {n}?", "Ni kipimo gani cha data (PDU) kinatumika kwenye safu ya OSI namba {n}?")
# ---------- address types
TYPES = T("Private (RFC 1918)", "Privée (RFC 1918)", "Y'ibanga (RFC 1918)", "Ya faragha (RFC 1918)"), T("Public", "Publique", "Rusange", "Ya umma"), T("Loopback (this computer)", "Bouclage (cet ordinateur)", "Loopback (iyi mudasobwa)", "Loopback (kompyuta hii)"),\
    T("Link-local (APIPA)", "Lien local (APIPA)", "Link-local (APIPA)", "Link-local (APIPA)"), T("Multicast", "Multidiffusion (multicast)", "Multicast", "Multicast")
ADDR = [("10.0.0.5", 0), ("10.200.13.7", 0), ("172.16.4.9", 0), ("172.31.255.1", 0), ("192.168.0.10", 0), ("192.168.100.200", 0), ("8.8.8.8", 1), ("1.1.1.1", 1), ("41.186.12.5", 1), ("172.32.0.1", 1), ("172.15.9.9", 1),
    ("193.0.14.129", 1), ("100.20.30.40", 1), ("196.12.130.45", 1), ("127.0.0.1", 2), ("127.5.5.5", 2), ("169.254.10.20", 3), ("169.254.200.1", 3), ("224.0.0.5", 4), ("239.1.1.1", 4), ("224.0.0.251", 4), ("11.0.0.1", 1), ("192.169.1.1", 1), ("10.255.255.254", 0)]
QA = T("What type of IPv4 address is {a}?", "De quel type est l'adresse IPv4 {a} ?", "Aderesi ya IPv4 {a} ni iyo mu bwoko ki?", "Anwani ya IPv4 {a} ni ya aina gani?")
WA = T("{a} is a {t} address.", "{a} est une adresse {t}.", "{a} ni aderesi {t}.", "{a} ni anwani {t}.")
SA = T("Private: 10/8, 172.16/12, 192.168/16. Loopback: 127/8. APIPA: 169.254/16. Multicast: 224–239.", "Privées : 10/8, 172.16/12, 192.168/16. Bouclage : 127/8. APIPA : 169.254/16. Multicast : 224–239.",
       "Iby'ibanga: 10/8, 172.16/12, 192.168/16. Loopback: 127/8. APIPA: 169.254/16. Multicast: 224–239.", "Za faragha: 10/8, 172.16/12, 192.168/16. Loopback: 127/8. APIPA: 169.254/16. Multicast: 224–239.")
# ---------- subnetting
QM1 = T("What is the subnet mask of /{n}?", "Quel est le masque de sous-réseau de /{n} ?", "Subnet mask ya /{n} ni iyihe?", "Barakoa ya subnet ya /{n} ni ipi?")
QM2 = T("Which CIDR prefix matches the mask {m}?", "Quel préfixe CIDR correspond au masque {m} ?", "Ni prefix ya CIDR iyihe ihuye na mask {m}?", "Ni kiambishi cha CIDR kipi kinalingana na barakoa {m}?")
WM = T("/{n} means {n} network bits, which is the mask {m}.", "/{n} signifie {n} bits de réseau, soit le masque {m}.", "/{n} bivuga bits {n} z'umuyoboro, ari yo mask {m}.", "/{n} inamaanisha biti {n} za mtandao, yaani barakoa {m}.")
SM = T("Count the 1-bits of the mask: 255 = 8 bits, 254 = 7, 252 = 6, 248 = 5, 240 = 4, 224 = 3, 192 = 2, 128 = 1.", "Comptez les bits à 1 du masque : 255 = 8 bits, 254 = 7, 252 = 6, 248 = 5, 240 = 4, 224 = 3, 192 = 2, 128 = 1.",
       "Bara bits za 1 muri mask: 255 = 8, 254 = 7, 252 = 6, 248 = 5, 240 = 4, 224 = 3, 192 = 2, 128 = 1.", "Hesabu biti za 1 za barakoa: 255 = 8, 254 = 7, 252 = 6, 248 = 5, 240 = 4, 224 = 3, 192 = 2, 128 = 1.")
QH = T("How many usable host addresses does a /{n} network have?", "Combien d'adresses d'hôtes utilisables comporte un réseau /{n} ?", "Umuyoboro wa /{n} ufite aderesi z'ibikoresho zikoreshwa zingahe?", "Mtandao wa /{n} una anwani ngapi za wenyeji zinazotumika?")
WH = T("2^{h} − 2 = {r} usable hosts (the network and broadcast addresses are not usable).", "2^{h} − 2 = {r} hôtes utilisables (l'adresse réseau et celle de diffusion ne sont pas utilisables).", "2^{h} − 2 = {r} (aderesi y'umuyoboro n'iy'ikwirakwizwa ntizikoreshwa).", "2^{h} − 2 = {r} (anwani ya mtandao na ya matangazo hazitumiki).")
SH = T("Remember to subtract the 2 reserved addresses.", "N'oubliez pas de retirer les 2 adresses réservées.", "Ibuka gukuramo aderesi 2 zabikiwe.", "Kumbuka kutoa anwani 2 zilizohifadhiwa.")
QN = T("What is the network address of {ip}/{n}?", "Quelle est l'adresse réseau de {ip}/{n} ?", "Aderesi y'umuyoboro ya {ip}/{n} ni iyihe?", "Anwani ya mtandao ya {ip}/{n} ni ipi?")
QB = T("What is the broadcast address of {ip}/{n}?", "Quelle est l'adresse de diffusion de {ip}/{n} ?", "Aderesi y'ikwirakwizwa ya {ip}/{n} ni iyihe?", "Anwani ya matangazo ya {ip}/{n} ni ipi?")
QF = T("What is the first usable host address in the network of {ip}/{n}?", "Quelle est la première adresse d'hôte utilisable du réseau de {ip}/{n} ?", "Aderesi ya mbere ikoreshwa mu muyoboro wa {ip}/{n} ni iyihe?", "Anwani ya kwanza ya mwenyeji inayotumika katika mtandao wa {ip}/{n} ni ipi?")
QLH = T("What is the last usable host address in the network of {ip}/{n}?", "Quelle est la dernière adresse d'hôte utilisable du réseau de {ip}/{n} ?", "Aderesi ya nyuma ikoreshwa mu muyoboro wa {ip}/{n} ni iyihe?", "Anwani ya mwisho ya mwenyeji inayotumika katika mtandao wa {ip}/{n} ni ipi?")
WN = T("The network of {ip}/{n} is {net}–{bc}: network address {net}, broadcast {bc}, usable hosts {f} to {l}.", "Le réseau de {ip}/{n} va de {net} à {bc} : adresse réseau {net}, diffusion {bc}, hôtes utilisables de {f} à {l}.",
       "Umuyoboro wa {ip}/{n} ni {net}–{bc}: aderesi y'umuyoboro {net}, ikwirakwizwa {bc}, ibikoresho kuva {f} kugeza {l}.", "Mtandao wa {ip}/{n} ni {net}–{bc}: anwani ya mtandao {net}, matangazo {bc}, wenyeji kuanzia {f} hadi {l}.")
SN = T("Apply the mask to the address (bitwise AND) to get the network; set all host bits to 1 for the broadcast.", "Appliquez le masque à l'adresse (ET bit à bit) pour obtenir le réseau ; mettez tous les bits d'hôte à 1 pour la diffusion.",
       "Shyira mask kuri aderesi (AND bit ku bit) ubone umuyoboro; shyira bits zose z'ibikoresho kuri 1 ubone ikwirakwizwa.", "Tumia barakoa kwenye anwani (AND biti kwa biti) kupata mtandao; weka biti zote za mwenyeji kuwa 1 kupata matangazo.")
QS = T("Splitting {net}/{p} into /{n} subnets gives how many subnets?", "Combien de sous-réseaux obtient-on en découpant {net}/{p} en /{n} ?", "Gutandukanya {net}/{p} mu bya /{n} bitanga subnets zingahe?", "Kugawanya {net}/{p} kuwa /{n} kunatoa subnet ngapi?")
WS = T("Borrowed bits = {n} − {p} = {b}, so 2^{b} = {r} subnets.", "Bits empruntés = {n} − {p} = {b}, donc 2^{b} = {r} sous-réseaux.", "Bits zatijwe = {n} − {p} = {b}, bityo 2^{b} = {r} subnets.", "Biti zilizokopwa = {n} − {p} = {b}, hivyo 2^{b} = {r} subnet.")
QSAME = T("Which host is in the same network as {ip}/{n}?", "Quel hôte est dans le même réseau que {ip}/{n} ?", "Ni uwuhe mudasobwa uri mu muyoboro umwe na {ip}/{n}?", "Ni mwenyeji yupi yuko katika mtandao mmoja na {ip}/{n}?")
WSAME = T("{ip2} is inside {net}/{n}, the same network as {ip}.", "{ip2} est dans {net}/{n}, le même réseau que {ip}.", "{ip2} iri muri {net}/{n}, umuyoboro umwe na {ip}.", "{ip2} iko ndani ya {net}/{n}, mtandao mmoja na {ip}.")
# ---------- binary
QDB = T("Convert the decimal number {d} to 8-bit binary.", "Convertissez le nombre décimal {d} en binaire sur 8 bits.", "Hindura umubare wa decimal {d} mu binary ya bits 8.", "Badilisha nambari ya desimali {d} kuwa binary ya biti 8.")
QBD = T("Convert the binary number {b} to decimal.", "Convertissez le nombre binaire {b} en décimal.", "Hindura umubare wa binary {b} mu decimal.", "Badilisha nambari ya binary {b} kuwa desimali.")
QDH = T("Convert the decimal number {d} to hexadecimal.", "Convertissez le nombre décimal {d} en hexadécimal.", "Hindura umubare wa decimal {d} mu hexadecimal.", "Badilisha nambari ya desimali {d} kuwa heksadesimali.")
QHD = T("Convert the hexadecimal number 0x{h} to decimal.", "Convertissez le nombre hexadécimal 0x{h} en décimal.", "Hindura umubare wa hexadecimal 0x{h} mu decimal.", "Badilisha nambari ya heksadesimali 0x{h} kuwa desimali.")
WB = T("{d} = {b} in binary = 0x{h} in hexadecimal.", "{d} = {b} en binaire = 0x{h} en hexadécimal.", "{d} = {b} muri binary = 0x{h} muri hexadecimal.", "{d} = {b} katika binary = 0x{h} katika heksadesimali.")
SB = T("Check with the place values 128, 64, 32, 16, 8, 4, 2, 1 (hex: 16s and 1s).", "Vérifiez avec les valeurs de position 128, 64, 32, 16, 8, 4, 2, 1 (hexa : 16 et 1).", "Genzura ukoresheje agaciro k'imyanya 128, 64, 32, 16, 8, 4, 2, 1 (hexa: 16 na 1).", "Hakiki kwa thamani za nafasi 128, 64, 32, 16, 8, 4, 2, 1 (heksa: 16 na 1).")
# ---------- facts (counts)
FACTS = [
 (T("How many bits does an IPv4 address have?", "Combien de bits comporte une adresse IPv4 ?", "Aderesi ya IPv4 igizwe na bits zingahe?", "Anwani ya IPv4 ina biti ngapi?"), ["8", "16", "32", "128"], 2, T("An IPv4 address has 32 bits (four octets of 8 bits).", "Une adresse IPv4 compte 32 bits (quatre octets de 8 bits).", "Aderesi ya IPv4 ifite bits 32 (octets enye za bits 8).", "Anwani ya IPv4 ina biti 32 (oktet nne za biti 8).")),
 (T("How many bits does an IPv6 address have?", "Combien de bits comporte une adresse IPv6 ?", "Aderesi ya IPv6 igizwe na bits zingahe?", "Anwani ya IPv6 ina biti ngapi?"), ["32", "64", "128", "256"], 2, T("An IPv6 address has 128 bits, written as 8 groups of hexadecimal digits.", "Une adresse IPv6 compte 128 bits, écrits en 8 groupes de chiffres hexadécimaux.", "Aderesi ya IPv6 ifite bits 128, yandikwa mu matsinda 8 y'imibare ya hexadecimal.", "Anwani ya IPv6 ina biti 128, huandikwa kwa vikundi 8 vya tarakimu za heksadesimali.")),
 (T("How many bits does a MAC address have?", "Combien de bits comporte une adresse MAC ?", "Aderesi ya MAC igizwe na bits zingahe?", "Anwani ya MAC ina biti ngapi?"), ["32", "48", "64", "128"], 1, T("A MAC address has 48 bits, written as six pairs of hexadecimal digits.", "Une adresse MAC compte 48 bits, écrits en six paires de chiffres hexadécimaux.", "Aderesi ya MAC ifite bits 48, yandikwa mu bikombe bitandatu by'imibare ya hexadecimal.", "Anwani ya MAC ina biti 48, huandikwa kwa jozi sita za tarakimu za heksadesimali.")),
 (T("How many layers does the OSI model have?", "Combien de couches compte le modèle OSI ?", "Modèle OSI ifite inzego zingahe?", "Modeli ya OSI ina safu ngapi?"), ["4", "5", "7", "9"], 2, T("The OSI model has 7 layers; the TCP/IP model has 4 (or 5).", "Le modèle OSI compte 7 couches ; le modèle TCP/IP en compte 4 (ou 5).", "OSI ifite inzego 7; TCP/IP ifite 4 (cyangwa 5).", "Modeli ya OSI ina safu 7; TCP/IP ina 4 (au 5).")),
 (T("How many layers does the classic TCP/IP model have?", "Combien de couches compte le modèle TCP/IP classique ?", "Modèle ya TCP/IP isanzwe ifite inzego zingahe?", "Modeli ya kawaida ya TCP/IP ina safu ngapi?"), ["3", "4", "6", "7"], 1, T("Network access, Internet, Transport and Application: 4 layers.", "Accès réseau, Internet, Transport et Application : 4 couches.", "Network access, Internet, Transport na Application: inzego 4.", "Network access, Internet, Transport na Application: safu 4.")),
 (T("How many bits are in one byte?", "Combien de bits y a-t-il dans un octet ?", "Bayite imwe ifite bits zingahe?", "Baiti moja ina biti ngapi?"), ["4", "8", "16", "32"], 1, T("One byte is 8 bits.", "Un octet fait 8 bits.", "Bayite imwe ni bits 8.", "Baiti moja ni biti 8.")),
 (T("How many wires are in the pairs of a standard Ethernet UTP cable (Cat5e/Cat6)?", "Combien de fils comporte un câble Ethernet UTP standard (Cat5e/Cat6) ?", "Insinga isanzwe ya Ethernet UTP (Cat5e/Cat6) ifite imirongo ingahe?", "Kebo ya kawaida ya Ethernet UTP (Cat5e/Cat6) ina nyuzi ngapi?"), ["4", "6", "8", "12"], 2, T("Four twisted pairs, so 8 wires, ending in an RJ-45 connector.", "Quatre paires torsadées, soit 8 fils, terminés par un connecteur RJ-45.", "Imirongo ine ihinye, ni ukuvuga 8, irangirira kuri RJ-45.", "Jozi nne zilizosokotwa, yaani nyuzi 8, zinaishia kwenye kiunganishi cha RJ-45.")),
 (T("What is the maximum length of a copper Ethernet segment (Cat5e/Cat6)?", "Quelle est la longueur maximale d'un segment Ethernet en cuivre (Cat5e/Cat6) ?", "Uburebure ntarengwa bw'insinga y'umuringa ya Ethernet (Cat5e/Cat6) ni ubuhe?", "Urefu wa juu wa sehemu ya Ethernet ya shaba (Cat5e/Cat6) ni upi?"), ["10 m", "55 m", "100 m", "500 m"], 2, T("100 metres.", "100 mètres.", "Metero 100.", "Mita 100.")),
 (T("What is the loopback IPv4 address?", "Quelle est l'adresse IPv4 de bouclage ?", "Aderesi ya IPv4 ya loopback ni iyihe?", "Anwani ya IPv4 ya loopback ni ipi?"), ["0.0.0.0", "127.0.0.1", "255.255.255.255", "192.168.0.1"], 1, T("127.0.0.1 always refers to the local computer itself.", "127.0.0.1 désigne toujours l'ordinateur local.", "127.0.0.1 ihora yerekeza kuri mudasobwa ubwayo.", "127.0.0.1 daima inarejelea kompyuta yenyewe.")),
 (T("What is the IPv4 limited broadcast address?", "Quelle est l'adresse de diffusion limitée IPv4 ?", "Aderesi y'ikwirakwizwa rya IPv4 ni iyihe?", "Anwani ya matangazo madogo ya IPv4 ni ipi?"), ["0.0.0.0", "127.255.255.255", "255.255.255.255", "224.0.0.1"], 2, T("255.255.255.255 reaches every host on the local network.", "255.255.255.255 atteint tous les hôtes du réseau local.", "255.255.255.255 igera ku bikoresho byose by'umuyoboro waho.", "255.255.255.255 hufikia wenyeji wote wa mtandao wa ndani.")),
 (T("What does a host with the address 169.254.x.x usually mean?", "Que signifie en général un hôte avec une adresse 169.254.x.x ?", "Mudasobwa ifite aderesi 169.254.x.x isanzwe bivuga iki?", "Mwenyeji mwenye anwani 169.254.x.x kwa kawaida inamaanisha nini?"),
  ["It has a public address", "It could not reach a DHCP server and gave itself an APIPA address", "It is a multicast host", "It is the default gateway"], 1, T("APIPA addresses appear when DHCP fails.", "Les adresses APIPA apparaissent quand le DHCP échoue.", "Aderesi za APIPA ziboneka iyo DHCP inaniwe.", "Anwani za APIPA huonekana DHCP inaposhindwa.")),
 (T("Which device operates mainly at OSI layer 2?", "Quel appareil fonctionne principalement à la couche OSI 2 ?", "Igikoresho gikorera cyane ku rwego rwa OSI rwa 2 ni ikihe?", "Kifaa gani hufanya kazi hasa katika safu ya OSI namba 2?"), ["Switch", "Router", "Repeater", "Proxy"], 0, T("A switch forwards frames using MAC addresses (layer 2).", "Un commutateur transmet des trames d'après les adresses MAC (couche 2).", "Switch yohereza amakadiri ikoresheje aderesi za MAC (urwego rwa 2).", "Swichi hutuma fremu kwa anwani za MAC (safu ya 2).")),
 (T("What is the purpose of the TCP three-way handshake?", "À quoi sert la poignée de main en trois temps de TCP ?", "Three-way handshake ya TCP ikora iki?", "Three-way handshake ya TCP ina kusudi gani?"), ["To establish a connection (SYN, SYN-ACK, ACK)", "To encrypt the data", "To assign an IP address", "To translate names"], 0, T("SYN, SYN-ACK, ACK sets up a reliable connection.", "SYN, SYN-ACK, ACK établit une connexion fiable.", "SYN, SYN-ACK, ACK itangiza ihuzwa ryizewe.", "SYN, SYN-ACK, ACK huanzisha muunganisho wa kuaminika.")),
 (T("Which Wi-Fi band usually has the longer range but is more crowded?", "Quelle bande Wi-Fi a en général la plus longue portée mais est la plus encombrée ?", "Ni ihe bande ya Wi-Fi ikunze kugira intera ndende ariko ikaba yuzuyeho abantu benshi?", "Bendi gani ya Wi-Fi kwa kawaida ina masafa marefu lakini imesongamana zaidi?"), ["2.4 GHz", "5 GHz", "60 GHz", "900 THz"], 0, T("2.4 GHz travels farther through walls but has fewer channels and more interference.", "Le 2,4 GHz traverse mieux les murs mais a moins de canaux et plus d'interférences.", "2.4 GHz inyura kure mu nkuta ariko ifite imiyoboro mike n'ibinyoteri byinshi.", "2.4 GHz husafiri mbali kupitia kuta lakini ina chaneli chache na usumbufu zaidi.")),
 (T("What does the TTL field in an IP packet prevent?", "Que empêche le champ TTL d'un paquet IP ?", "Umwanya wa TTL mu gapaki ka IP ubuza iki?", "Sehemu ya TTL katika pakiti ya IP huzuia nini?"), ["Packets circulating forever in a loop", "Packets being encrypted", "Duplicate MAC addresses", "Slow DNS answers"], 0, T("TTL is decreased at every router; at 0 the packet is dropped.", "Le TTL baisse à chaque routeur ; à 0 le paquet est supprimé.", "TTL igabanywa kuri buri router; igeze kuri 0 agapaki karajugunywa.", "TTL hupungua kwenye kila kipanga njia; ikifika 0 pakiti hutupwa.")),
 (T("What is the default administrative practice for unused switch ports?", "Quelle est la bonne pratique pour les ports de commutateur inutilisés ?", "Ni igikorwa cyiza ku port za switch zidakoreshwa ni iki?", "Ni utaratibu gani mzuri kwa milango ya swichi isiyotumika?"), ["Disable them", "Leave them open for guests", "Give them public IP addresses", "Connect them to each other"], 0, T("Disabling unused ports stops anyone from plugging in unnoticed.", "Désactiver les ports inutilisés empêche de se brancher sans se faire remarquer.", "Guhagarika port zidakoreshwa bibuza umuntu kwinjiza ibikoresho atabonetse.", "Kuzima milango isiyotumika huzuia mtu kuchomeka bila kuonekana.")),
 (T("Which tool lets you capture and inspect packets with a graphical interface?", "Quel outil permet de capturer et d'inspecter des paquets avec une interface graphique ?", "Ni igikoresho kihe cyemerera gufata no gusuzuma udupaki mu buryo bw'amashusho?", "Ni zana gani huruhusu kunasa na kukagua pakiti kwa kiolesura cha picha?"), ["Wireshark", "Photoshop", "Excel", "Notepad"], 0, T("Wireshark is the standard graphical packet analyser.", "Wireshark est l'analyseur de paquets graphique de référence.", "Wireshark ni igikoresho gisanzwe cyo gusesengura udupaki.", "Wireshark ni kichambuzi cha kawaida cha pakiti chenye picha.")),
]
FS = T("Read every option carefully; two of them often look alike.", "Lisez chaque option attentivement ; deux se ressemblent souvent.", "Soma buri gisubizo witonze; bibiri akenshi birasa.", "Soma kila chaguo kwa makini; mbili mara nyingi hufanana.")
ADD_W = T("The address {a}", "L'adresse {a}", "Aderesi {a}", "Anwani {a}")


def _ip(n):
    return str(ipaddress.IPv4Address(n))


def _mask(n):
    return _ip((0xFFFFFFFF << (32 - n)) & 0xFFFFFFFF)


def build(Q):
    from quiz_net_concepts import ROWS
    r = rnd("net-1")
    out = []

    def add(q, opts, ans, why, slip):
        out.append(Q("networks", q, opts, ans, why, slip))

    def fmt(tpl, **k):
        return tuple(tpl[i].format(**k) for i in range(4))

    def lang_opts(lists):
        return {l: lists[i] for i, l in enumerate(LANGS)}
    # ports
    for s, p, t in PORTS:
        wrong = r.sample([x for x in PORTS if x[1] != p], 3)
        opts, a = place(r, str(p), [str(x[1]) for x in wrong])
        add(fmt(QP1, s=s), opts, a, fmt(WP, s=s, p=p, t=t), SP)
        wrong = r.sample([x for x in PORTS if x[1] != p], 3)
        opts, a = place(r, s, [x[0] for x in wrong])
        add(fmt(QP2, p=p), opts, a, fmt(WP, s=s, p=p, t=t), SP)
    # transport
    for s, t in TRANSPORT:
        opts = ["TCP", "UDP", "ICMP", "ARP"]
        add(fmt(QT, s=s), opts, opts.index(t), fmt(WT, s=s, t=t), ST)
    # acronyms (network ones)
    NA = [("IP", "Internet Protocol"), ("TCP", "Transmission Control Protocol"), ("UDP", "User Datagram Protocol"), ("ICMP", "Internet Control Message Protocol"), ("ARP", "Address Resolution Protocol"),
          ("DNS", "Domain Name System"), ("DHCP", "Dynamic Host Configuration Protocol"), ("NAT", "Network Address Translation"), ("VLAN", "Virtual Local Area Network"), ("LAN", "Local Area Network"),
          ("WAN", "Wide Area Network"), ("MAN", "Metropolitan Area Network"), ("PAN", "Personal Area Network"), ("WLAN", "Wireless Local Area Network"), ("SSID", "Service Set Identifier"),
          ("MAC", "Media Access Control"), ("OSI", "Open Systems Interconnection"), ("TTL", "Time To Live"), ("MTU", "Maximum Transmission Unit"), ("QoS", "Quality of Service"),
          ("BGP", "Border Gateway Protocol"), ("OSPF", "Open Shortest Path First"), ("RIP", "Routing Information Protocol"), ("EIGRP", "Enhanced Interior Gateway Routing Protocol"),
          ("STP", "Spanning Tree Protocol"), ("HTTP", "HyperText Transfer Protocol"), ("FTP", "File Transfer Protocol"), ("SFTP", "SSH File Transfer Protocol"), ("SMTP", "Simple Mail Transfer Protocol"),
          ("IMAP", "Internet Message Access Protocol"), ("POP3", "Post Office Protocol version 3"), ("SNMP", "Simple Network Management Protocol"), ("NTP", "Network Time Protocol"),
          ("URL", "Uniform Resource Locator"), ("CDN", "Content Delivery Network"), ("ISP", "Internet Service Provider"), ("NIC", "Network Interface Card"), ("PoE", "Power over Ethernet"),
          ("UTP", "Unshielded Twisted Pair"), ("LACP", "Link Aggregation Control Protocol"), ("MPLS", "Multiprotocol Label Switching"), ("SD-WAN", "Software-Defined Wide Area Network"),
          ("CIDR", "Classless Inter-Domain Routing"), ("VLSM", "Variable Length Subnet Mask"), ("WPA", "Wi-Fi Protected Access"), ("WEP", "Wired Equivalent Privacy"), ("WPS", "Wi-Fi Protected Setup"),
          ("RADIUS", "Remote Authentication Dial-In User Service"), ("ACL", "Access Control List"), ("DMZ", "Demilitarized Zone"), ("TFTP", "Trivial File Transfer Protocol"), ("RDP", "Remote Desktop Protocol"),
          ("VoIP", "Voice over IP"), ("IoT", "Internet of Things"), ("IANA", "Internet Assigned Numbers Authority"), ("RTT", "Round-Trip Time"), ("SLA", "Service Level Agreement"), ("IPAM", "IP Address Management")]
    exps = [e for _, e in NA]
    AQ = T("What does {a} stand for?", "Que signifie {a} ?", "{a} ni impfunyisho y'iki?", "{a} inasimamia nini?")
    AW = T("{a} stands for {e}.", "{a} signifie {e}.", "{a} bivuga {e}.", "{a} inamaanisha {e}.")
    AS = T("The expansions look alike. Learn each acronym with the idea it names, not just its letters.", "Les développements se ressemblent. Apprenez chaque sigle avec l'idée qu'il désigne.", "Ibisobanuro bisa. Iga buri funyisho n'igitekerezo gisobanura.", "Visanuku hufanana. Jifunze kila kifupi pamoja na wazo lake.")
    for a, e in NA:
        wrong = r.sample([x for x in exps if x != e], 3)
        opts, i = place(r, e, wrong)
        add(fmt(AQ, a=a), opts, i, fmt(AW, a=a, e=e), AS)
    # OSI
    for s, n in OSI:
        wrong = r.sample([k for k in LAYERS if k != n], 3)
        order = wrong + [n]
        r.shuffle(order)
        add(fmt(QO, s=s), lang_opts([[LAYERS[k][i] for k in order] for i in range(4)]), order.index(n), tuple(WO[i].format(s=s, l=LAYERS[n][i]) for i in range(4)), SO)
    for n in LAYERS:
        wrong = r.sample([k for k in LAYERS if k != n], 3)
        order = wrong + [n]
        r.shuffle(order)
        add(fmt(QL, n=n), lang_opts([[LAYERS[k][i].split("–")[-1].strip() for k in order] for i in range(4)]), order.index(n), tuple(WL[i].format(n=n, l=LAYERS[n][i]) for i in range(4)), SO)
    for p, n in PDU:
        names = [x[0] for x in PDU]
        opts, i = place(r, p, [x for x in names if x != p][:3])
        add(fmt(QU, n=n), opts, i, tuple(f"{LAYERS[n][j]}: {p}." for j in range(4)), SO)
    # address types
    for a, k in ADDR:
        wrong = [x for x in range(5) if x != k]
        r.shuffle(wrong)
        order = wrong[:3] + [k]
        r.shuffle(order)
        add(fmt(QA, a=a), lang_opts([[TYPES[x][i] for x in order] for i in range(4)]), order.index(k), tuple(WA[i].format(a=a, t=TYPES[k][i]) for i in range(4)), SA)
    # subnet masks and hosts
    for n in range(8, 31):
        m = _mask(n)
        wrong = [_mask(x) for x in (n - 1, n + 1, n + 2, n - 2) if 1 <= x <= 31 and x != n]
        opts, i = place(r, m, wrong[:3])
        add(fmt(QM1, n=n), opts, i, fmt(WM, n=n, m=m), SM)
        wrong = [f"/{x}" for x in (n - 1, n + 1, n + 2, n - 2) if 1 <= x <= 31 and x != n]
        opts, i = place(r, f"/{n}", wrong[:3])
        add(fmt(QM2, m=m), opts, i, fmt(WM, n=n, m=m), SM)
    for n in range(16, 31):
        h = 32 - n
        res = 2 ** h - 2
        wrong = [2 ** h, 2 ** h - 1, 2 ** (h + 1) - 2, 2 ** (h - 1) - 2 if h > 2 else 6]
        opts, i = place(r, str(res), [str(x) for x in dict.fromkeys(wrong) if x != res][:3])
        add(fmt(QH, n=n), opts, i, fmt(WH, h=h, r=res), SH)
    # computed networks
    pools = [("192.168.%d.%d", (0, 254), (0, 254)), ("10.%d.%d.%d", None, None), ("172.%d.%d.%d", None, None)]
    prefixes = [20, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    k = 0
    while k < 140:
        base = r.choice(["192.168.%d.%d", "10.%d.%d.%d", "172.%d.%d.%d"])
        if base.startswith("192"):
            ip = base % (r.randint(0, 255), r.randint(1, 254))
        elif base.startswith("10"):
            ip = base % (r.randint(0, 255), r.randint(0, 255), r.randint(1, 254))
        else:
            ip = base % (r.randint(16, 31), r.randint(0, 255), r.randint(1, 254))
        n = r.choice(prefixes if not base.startswith("10") else prefixes + [16, 18])
        net = ipaddress.ip_network(f"{ip}/{n}", strict=False)
        if str(net.network_address) == ip or net.num_addresses < 4 or str(net.broadcast_address) == ip:
            continue
        step = net.num_addresses
        info = dict(ip=ip, n=n, net=str(net.network_address), bc=str(net.broadcast_address), f=_ip(int(net.network_address) + 1), l=_ip(int(net.broadcast_address) - 1))
        kind = k % 5
        if kind == 0:
            right, wr = info["net"], [_ip(int(net.network_address) + step), _ip(int(net.network_address) - step), info["f"], info["bc"]]
            q = QN
        elif kind == 1:
            right, wr = info["bc"], [info["l"], _ip(int(net.broadcast_address) + step), _ip(int(net.broadcast_address) - step), info["net"]]
            q = QB
        elif kind == 2:
            right, wr = info["f"], [info["net"], _ip(int(net.network_address) + 2), _ip(int(net.network_address) + step + 1), info["l"]]
            q = QF
        elif kind == 3:
            right, wr = info["l"], [info["bc"], _ip(int(net.broadcast_address) - 2), _ip(int(net.broadcast_address) + step - 1), info["f"]]
            q = QLH
        else:
            ip2 = _ip(int(net.network_address) + r.randint(1, step - 2))
            if ip2 == ip:
                continue
            right = ip2
            wr = [_ip(int(net.network_address) + step + r.randint(1, step - 2)), _ip(int(net.network_address) - r.randint(2, step - 1)), _ip(int(net.network_address) + 2 * step + 1)]
            info.update(ip2=ip2)
        wr = list(dict.fromkeys(x for x in wr if x != right))[:3]
        if len(wr) < 3:
            continue
        opts, i = place(r, right, wr)
        if kind == 4:
            add(fmt(QSAME, ip=ip, n=n), opts, i, fmt(WSAME, ip=ip, ip2=right, net=info["net"], n=n), SN)
        else:
            add(fmt(q, ip=ip, n=n), opts, i, fmt(WN, **info), SN)
        k += 1
    for p in (24, 25, 26, 27):
        for n in range(p + 1, min(p + 4, 31)):
            res, b = 2 ** (n - p), n - p
            opts, i = place(r, str(res), [str(x) for x in dict.fromkeys((res * 2, res // 2, res + 2, res * 4, res + 1, res * 8, res + 4)) if x != res and x > 0][:3])
            add(fmt(QS, net="192.168.1.0", p=p, n=n), opts, i, fmt(WS, n=n, p=p, b=b, r=res), SH)
    # binary / hex
    for d in (3, 5, 10, 12, 15, 17, 24, 31, 42, 64, 75, 100, 127, 128, 150, 172, 192, 200, 224, 240, 248, 252, 254, 255):
        b, h = format(d, "08b"), format(d, "X")
        near = [format(d ^ (1 << x), "08b") for x in (0, 1, 3, 6)]
        opts, i = place(r, b, near[:3])
        add(fmt(QDB, d=d), opts, i, fmt(WB, d=d, b=b, h=h), SB)
        wrong = [str(x) for x in (d + 1, d - 1, d + 16, d ^ 4, d ^ 8) if 0 <= x <= 255 and x != d][:3]
        opts, i = place(r, str(d), wrong)
        add(fmt(QBD, b=b), opts, i, fmt(WB, d=d, b=b, h=h), SB)
        if d > 15:
            wrong = [format(x, "X") for x in (d + 1, d - 1, d + 16, d ^ 0xF) if 0 <= x <= 255 and x != d][:3]
            opts, i = place(r, h, wrong)
            add(fmt(QDH, d=d), opts, i, fmt(WB, d=d, b=b, h=h), SB)
            wrong = [str(x) for x in (d + 1, d - 1, d + 16, d ^ 0xF) if 0 <= x <= 255 and x != d][:3]
            opts, i = place(r, str(d), wrong)
            add(fmt(QHD, h=h), opts, i, fmt(WB, d=d, b=b, h=h), SB)
    # facts
    for q, opts, ans, why in FACTS:
        add(q, opts, ans, why, FS)
    # concept rows
    groups = {}
    for g, term, *_ in ROWS:
        groups.setdefault(g, []).append(term)
    for g, term, en, fr, rw, sw in ROWS:
        texts = (en, fr, rw, sw)
        toks = tokens(term)
        d = [mask(t, toks, [term]) for t in texts]
        wrong = r.sample([x for x in groups[g] if x != term], 3)
        opts, i = place(r, term, wrong)
        q = tuple(Q_TERM[j].format(d=d[j]) for j in range(4))
        why = tuple(f"{term}: {texts[j]}" for j in range(4))
        slip = tuple(SLIP[j].format(o=", ".join(wrong)) for j in range(4))
        add(q, opts, i, why, slip)
    return out
