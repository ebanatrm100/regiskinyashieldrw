"""Writes eval/prompts.csv: bilingual test prompts with the route we EXPECT (guide = answered offline, scam = scam detector, translate = translation request, ai = needs the model, any = offline or model are both acceptable)."""
import csv, os
P = [
 # (lang, prompt, expected_kind, intent)
 ("en","Who is your owner?","guide","owner"),("fr","Qui est ton propriétaire ?","guide","owner"),("rw","Nyirawe ni nde?","guide","owner"),("sw","Mmiliki wako ni nani?","guide","owner"),
 ("en","Translate who is your owner into Kinyarwanda","guide","translate"),("en","Translate password into French","guide","translate"),
 ("en","Translate scam into Kiswahili","guide","translate"),("fr","Traduis mot de passe en kinyarwanda","guide","translate"),
 ("sw","Tafsiri nenosiri kwa Kifaransa","guide","translate"),("rw","Humura ijambo ry'ibanga mu cyongereza","guide","translate"),
 ("en","Hello","guide","greeting"),("fr","Bonjour","guide","greeting"),("rw","Muraho","guide","greeting"),("sw","Habari","guide","greeting"),
 ("en","What is phishing?","guide","cyber"),("en","What is ransomware?","guide","cyber"),("en","What is a firewall?","guide","cyber"),
 ("en","What is two-factor authentication?","guide","cyber"),("en","What is a VPN?","guide","cyber"),("en","What is malware?","guide","cyber"),
 ("fr","Qu'est-ce que le hameçonnage ?","guide","cyber"),("fr","Qu'est-ce qu'un pare-feu ?","guide","cyber"),("sw","Ransomware ni nini?","guide","cyber"),
 ("rw","Firewall ni iki?","guide","cyber"),("en","List all cybersecurity terms","guide","cyber_list"),("fr","Liste des termes de cybersécurité","guide","cyber_list"),
 ("en","What is encryption?","guide","cyber"),("en","What is a botnet?","guide","cyber"),("en","What is SQL injection?","guide","cyber"),
 ("en","How do I make a strong password?","guide","howto"),("en","How do I spot a scam?","guide","howto"),("en","How do I protect my phone?","any","howto"),
 ("fr","Comment protéger mon téléphone ?","any","howto"),("sw","Jinsi ya kulinda simu yangu?","any","howto"),("rw","Nakwirinda nte ubutekamutwe?","any","howto"),
 ("en","What is a computer?","guide","definition"),("en","What is the internet?","guide","definition"),("en","What is a CPU?","guide","definition"),
 ("en","What is Ohm's law?","guide","physics"),("en","What is the formula for kinetic energy?","guide","physics"),("en","Newton's second law","guide","physics"),
 ("fr","Quelle est la loi d'Ohm ?","guide","physics"),("sw","Sheria ya Ohm ni nini?","guide","physics"),
 ("en","Dear customer your MTN account is blocked send your PIN to 0788000000 now","scam","scam"),
 ("en","Congratulations you won 5,000,000 RWF lottery pay 20,000 fee to claim","scam","scam"),
 ("fr","Votre compte est bloqué, envoyez votre code PIN immédiatement","scam","scam"),
 ("sw","Hongera umeshinda zawadi kubwa, tuma pesa elfu 20 ili upokee zawadi yako","scam","scam"),
 ("rw","Wegukanye miliyoni 5, ohereza amafaranga 20,000 ubone igihembo","scam","scam"),
 ("en","I sent money to the wrong number, please reverse it, this is urgent send now","scam","scam"),
 ("en","Click http://bit.ly/claim-prize to verify your bank account or it will be closed","scam","scam"),
 ("en","Help me write a polite email to my landlord about a broken window","any","writing"),
 ("en","Explain photosynthesis to a 10 year old","ai","tutor"),("en","Summarise the causes of World War I","ai","tutor"),
 ("fr","Explique-moi la photosynthèse simplement","ai","tutor"),("sw","Nieleze jinsi mvua inavyotokea","ai","tutor"),
 ("rw","Sobanura uko imvura iboneka","ai","tutor"),("en","Write a short poem about Kigali","any","writing"),
 ("en","Give me tips for a job interview","any","writing"),("en","Correct this sentence: me and him goes to school","ai","writing"),
 ("fr","Écris un court message de remerciement à mon professeur","ai","writing"),("sw","Andika barua fupi ya kuomba kazi","any","writing"),
 ("rw","Mfasha kwandika ibaruwa isaba akazi","any","writing"),("en","What is the capital of Kenya and why was it chosen?","ai","qa"),
 ("en","Explain how vaccines work","ai","qa"),("en","How does compound interest work?","any","qa"),("fr","Pourquoi le ciel est-il bleu ?","ai","qa"),
 ("sw","Kwa nini bahari ni ya chumvi?","ai","qa"),("rw","Kuki ikirere ari ubururu?","ai","qa"),
 ("en","Translate 'the meeting starts at nine tomorrow' into Kinyarwanda","translate","translate_long"),
 ("en","Translate 'please call me when you arrive' into French","translate","translate_long"),
 ("fr","Traduis 'merci beaucoup pour votre aide' en swahili","translate","translate_long"),
]

def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["language", "prompt", "expected_kind", "intent"]); w.writerows(P)
    print(len(P), "prompts ->", path)

if __name__ == "__main__":
    main()
