"""Regression tests for the rules added after testing on unseen messages (safety_rules_more.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from detector import analyze

MUST_FLAG = {
    "blackmail": ["I recorded you on your webcam. Send 100 USD in bitcoin or I will send the video to your contacts",
                  "Nous avons filmé votre écran. Payez 200 USD sinon je publie la vidéo à vos contacts."],
    "payment_redirect": ["CEO here. Urgent wire transfer needed to a new supplier account today. Keep this confidential.",
                         "Our bank details have changed. Please send all future payments to this new account number."],
    "credential_request": ["Hello it's the bank, please read me the code we just sent",
                           "Hello, this is IT support. We need your password to fix your mailbox, reply urgently",
                           "Ntimugire kure, ndi umuyobozi wa banki. Mumpe kode yoherejwe kuri telefone yanyu"],
    "account_threat": ["Dear customer your MTN MoMo account is suspended. Call 0788123456 now to reactivate",
                       "Click here to update your WhatsApp verification code or your account will be deleted"],
    "new_number_money": ["Mama nimbwira ko telefone yanjye yibwe, nyoherereza amafaranga kuri iyi nimero nshya vuba",
                         "Habari, simu yangu imeibiwa, hii ni namba mpya, nitumie pesa 50000 haraka"],
    "fee_to_start": ["Pay the visa processing fee of 300 USD today to secure your work abroad placement"],
    "card_details_request": ["Win a free iPhone 16! Just complete this survey and enter your card details to cover shipping"],
    "lookalike_domain": ["Your Netflix payment failed. Update billing at netflix-billing-help.com within 24h"],
    "romance_money": ["Hi dear, I am a US soldier looking for love. I need money for my flight ticket to come see you"],
}

MUST_STAY_QUIET = [
    "Your OTP is 4821. Do not share it with anyone, including bank staff.",
    "Hi, I lost my phone yesterday and got a new SIM. This is my new number, save it please.",
    "The soldier in the film was brilliant, I need to send you the ticket link for Saturday",
    "Your account statement is ready. Never share your PIN with anyone.",
    "Please send me the report by Friday and the new supplier contract when ready.",
    "Nous avons changé de bureau, notre nouvelle adresse est rue de la Paix 12.",
    "Jambo, kikao cha wazazi kitakuwa Ijumaa saa nne asubuhi shuleni.",
    "Meeting moved to 3pm tomorrow, see agenda attached from last week",
]


def test_flags():
    for rid, msgs in MUST_FLAG.items():
        for m in msgs:
            ids = [f.rule_id for f in analyze(m).findings]
            assert rid in ids, (rid, m, ids)
            assert analyze(m).verdict != "ok", m


def test_quiet():
    for m in MUST_STAY_QUIET:
        assert analyze(m).verdict == "ok", (m, [f.rule_id for f in analyze(m).findings])


def test_all_rules_have_four_languages():
    from safety_rules import RULES, LANGS
    for r in RULES:
        for k in ("title", "why", "advice"):
            assert all(r[k].get(l) for l in LANGS), (r["id"], k)


if __name__ == "__main__":
    test_flags(); test_quiet(); test_all_rules_have_four_languages(); print("new rules ok")
