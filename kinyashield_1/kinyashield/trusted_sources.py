"""Trusted-source guidance. No phone numbers are stored here on purpose:
a wrong number in a safety tool is dangerous. Addresses must be verified by
the project owner before release."""

SOURCES = [
    {
        "name": "National Cyber Security Authority (NCSA), Rwanda",
        "use": {"en": "Official cyber-security guidance and awareness material for Rwanda.",
                "rw": "Inama n'ibikoresho byo gukangurira ku mutekano wa murandasi mu Rwanda.",
                "fr": "Conseils officiels et mat\u00e9riel de sensibilisation sur la cybers\u00e9curit\u00e9 au Rwanda.",
                "sw": "Mwongozo rasmi na vifaa vya uhamasishaji kuhusu usalama wa mtandao nchini Rwanda."},
        "url": "https://www.ncsa.gov.rw",
        "verified": False,
    },
    {
        "name": "Your bank or mobile-money provider (official website, card or branch)",
        "use": {"en": "The only reliable way to confirm a message that claims to come from them.",
                "rw": "Inzira yonyine yizewe yo kwemeza ubutumwa buvuga ko buturutse kuri bo.",
                "fr": "Le seul moyen fiable de confirmer un message qui pr\u00e9tend venir d'eux.",
                "sw": "Njia pekee ya kuaminika ya kuthibitisha ujumbe unaodai kutoka kwao."},
        "url": "",
        "verified": True,
    },
]
NOTE = {
    "en": "Addresses marked unverified must be checked by the project owner before release.",
    "rw": "Aderesi zanditseho 'unverified' zigomba kugenzurwa na nyiri umushinga mbere yo gusohora.",
    "fr": "Les adresses marquées « unverified » doivent être vérifiées par le propriétaire du projet avant la publication.",
    "sw": "Anwani zilizowekwa alama 'unverified' lazima zikaguliwe na mmiliki wa mradi kabla ya kutolewa.",
}
