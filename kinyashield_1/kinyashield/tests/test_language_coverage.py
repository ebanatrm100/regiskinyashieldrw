import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import assistant_flow as F
LANGS = ("en", "fr", "rw", "sw")
# (expected entry id prefix, question in en, fr, rw, sw)
CASES = [
 ("net_basics", "what is a computer network", "qu'est-ce qu'un réseau informatique", "umuyoboro wa mudasobwa ni iki", "mtandao wa kompyuta ni nini"),
 ("net_basics", "what are the types of networks", "quels sont les types de réseaux", "ni ubuhe bwoko bw'imiyoboro", "aina za mitandao ni zipi"),
 ("net_ip", "what is an IP address", "qu'est-ce qu'une adresse IP", "aderesi ya IP ni iki", "anwani ya IP ni nini"),
 ("net_subnetting", "explain subnetting", "explique le sous-réseau", "sobanura subnetting", "eleza subnetting"),
 ("net_ports", "what are common ports", "ports courants", "port zisanzwe", "milango ya kawaida"),
 ("net_devices", "router vs switch", "différence entre routeur et commutateur", "itandukaniro rya router na switch", "tofauti ya router na switch"),
 ("net_wifi_protect", "how do I protect my wifi", "comment protéger mon wifi", "nakwirinda nte wifi yanjye", "jinsi ya kulinda wifi yangu"),
 ("net_osi_tcpip", "osi model explained", "modèle osi expliqué", "osi model sobanuye", "eleza osi model"),
 ("net_troubleshoot", "network troubleshooting", "dépannage réseau", "gukemura ibibazo by'umuyoboro", "kutatua matatizo ya mtandao"),
 ("assistant_abilities", "what can you do", "que sais-tu faire", "ushobora gukora iki", "unaweza kufanya nini"),
 ("owner", "who created you", "qui t'a créé", "ni nde wakwiyubatse", "nani alikuunda"),
 ("cyber_|scam_", "what is ransomware", "qu'est-ce qu'un rançongiciel", "ransomware ni iki", "ransomware ni nini"),
 ("cyber_|scam_", "what is social engineering", "qu'est-ce que l'ingénierie sociale", "social engineering ni iki", "social engineering ni nini"),
 ("cyber_|scam_", "what is a DDoS attack", "qu'est-ce qu'une attaque DDoS", "DDoS ni iki", "DDoS ni nini"),
 ("cyber_use-after-free", "what is use-after-free", "qu'est-ce que Utilisation après libération", "Use-after-free ni iki", "Use-after-free ni nini"),
 ("cyb_hacker_methods", "how do hackers attack", "comment les hackers attaquent", "abahacker barwanya bate", "wadukuzi wanashambulia vipi"),
 ("cyb_accounts_hacked", "what should I do if my account is hacked", "que faire si mon compte est piraté", "nkore iki konti yanjye yibwe", "nifanye nini akaunti yangu ikidukuliwa"),
]
for case in CASES:
    want, qs = case[0], case[1:]
    for lang, q in zip(LANGS, qs):
        r = F.route(q, lang)
        assert r["kind"] in ("guide", "scam"), (lang, q, r["kind"])
        got = r["entry"]["id"]
        assert any(got == w or got.startswith(w) for w in want.split("|")), (lang, q, got, want)
        e = r["entry"]
        for l in LANGS:   # the entry must be complete in every language
            assert str(e["title"][l]).strip() and str(e["answer"][l]).strip(), (got, l)
        assert len(str(e["answer"][lang])) > 40
print("OK", len(CASES) * 4, "questions")
