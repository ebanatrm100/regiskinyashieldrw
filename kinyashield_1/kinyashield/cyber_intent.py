"""Intent matching for the cybersecurity playbook: natural paraphrases in English, French, Kinyarwanda and Kiswahili.
find_id(question) -> playbook id or None. Used by cyber_playbook_db.find() only when no exact phrase matched. Vocabulary is accent-folded."""
from __future__ import annotations
import re
from textutil import fold, has_phrase

_T = lambda s: set(s.split())

SCAM = _T("scam scams scammer scammers fraud frauds fraudster fraudsters swindle swindlers conman cons trap traps trick tricks "
          "arnaque arnaques escroquerie escroqueries escroc escrocs fraude fraudes piege pieges "
          "uburiganya abatekamutwe umutekamutwe ubutekamutwe amayeri igitego "
          "utapeli matapeli tapeli ulaghai walaghai mtego mitego")
AVOID = _T("avoid prevent protect stop escape fall falling beware safe safely spot recognise recognize identify detect defend resist guard tips advice steer "
           "eviter prevenir proteger empecher tomber reperer reconnaitre detecter conseils garder "
           "kwirinda nirinda nirinde wirinde irinda guhagarika kutagwa kugwa kumenya gutahura inama wirinda twirinde kurinda "
           "epuka kuepuka kuzuia kulinda kujikinga kuanguka tambua kutambua ushauri jikinga")
TRICK = _T("trick tricks deceive fool manipulate lure convince cheat work operate "
           "tromper tromperie manipulent piegent fonctionnent "
           "bariganya baratekera bakora bashuka bayobya "
           "hudanganya hulaghai hufanya hutumia")
HAPPENED = ["i was scammed", "i got scammed", "i have been scammed", "i ve been scammed", "been scammed", "i am scammed", "i was hacked", "i got hacked", "got hacked", "i lost money", "i fell for", "i fell victim",
            "after being scammed", "after a scam", "after i was scammed", "scammed me", "someone scammed", "was scammed", "i was cheated", "i was defrauded", "money was stolen", "my account was hacked",
            "j'ai ete arnaque", "ai ete arnaque", "ai ete escroque", "je me suis fait arnaquer", "apres une arnaque", "apres avoir ete arnaque", "victime d'une arnaque", "victime d'arnaque", "on m'a arnaque", "j'ai ete pirate", "mon compte a ete pirate", "mon compte a ete piratee",
            "nariganyijwe", "naribwe", "banyibye amafaranga", "namaze kuriganywa", "nyuma yo kuriganywa", "ndiganyijwe", "natekewe umutwe", "nibwe amafaranga", "konti yanjye yibwe", "konti yanjye yahawe",
            "nimedanganywa", "nimetapeliwa", "nilitapeliwa", "nimeibiwa pesa", "baada ya kutapeliwa", "baada ya utapeli", "nimekuwa mwathirika wa utapeli", "akaunti yangu imedukuliwa", "nimedukuliwa"]
HACKER = _T("hacker hackers cybercriminal cybercriminals cyber-criminals attacker attackers criminals cybercrooks "
            "pirate pirates cybercriminel cybercriminels attaquant attaquants "
            "abahackers abahacker abagizi abateye abatera abashimusi umuhacker "
            "wadukuzi mdukuzi wahalifu mshambuliaji washambuliaji")
ACT = _T("attack attacks hack hacks work operate trick break breach steal target infiltrate methods ways techniques tactics tools how "
         "attaquent attaquer pirater piratent methodes techniques astuces fonctionnent volent ciblent tactiques comment "
         "batera gutera ibitero uburyo amayeri bakora bakoresha biba bacengera "
         "washambulia kushambulia mbinu hudukua kudukua hufanya wanavyofanya huiba wanatumia hutumia jinsi")
SKIP = _T("account accounts phone phones whatsapp wifi wi-fi password passwords compte comptes telephone telephones konti telefone akaunti simu nywila")
ENGINEER = _T("engineer engineers defender defenders professionals experts analysts companies organisations organizations administrators admins "
              "ingenieurs defenseurs professionnels experts analystes entreprises "
              "injeniyeri abashinzwe impuguke abahanga abakozi "
              "wahandisi wataalamu watetezi wachambuzi")
PROTECT = _T("protect secure defend safeguard harden prevent defence defense protection protecting securing "
             "protegent proteger securisent securiser defendre protection defense "
             "barinda kurinda gucunga gukingira umutekano "
             "hulinda kulinda ulinzi huimarisha")
SYSTEM = _T("system systems network networks data infrastructure servers computers "
            "systemes reseaux donnees "
            "sisitemu imiyoboro amakuru "
            "mifumo mitandao")


def _toks(q):
    return set(re.split(r"[^a-z0-9']+", q)) - {""}


def find_id(question):
    q = fold(question)
    if not q or len(q) > 200:
        return None
    t = _toks(q) | set(re.split(r"[' ]+", q))
    if has_phrase(q, HAPPENED):
        return "cyb_if_scammed"
    if (t & SCAM) and (t & AVOID):
        return "cyb_scam_prevention"
    if (t & SCAM) and (t & TRICK) and not (t & HACKER):
        return "cyb_scam_prevention"
    if (t & ENGINEER) and (t & PROTECT) and (t & SYSTEM):
        return "cyb_defender_methods"
    if (t & HACKER) and (t & ACT) and not (t & SKIP):
        return "cyb_hacker_methods"
    return None
