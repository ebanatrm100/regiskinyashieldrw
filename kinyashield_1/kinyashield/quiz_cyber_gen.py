"""Generated cybersecurity quiz questions (topic "cybersecurity"): description -> term from the 772-term glossary, description -> scam from the scam catalogue,
and acronym expansions. Every question is built from data that already exists in four languages (cyber_db, scams_db); descriptions are masked so they never
contain the answer. Distractors come from the same category but never share words, aliases or wording with the answer. fr/rw/sw wording comes from the glossary
drafts and is for review by fluent speakers."""
import re
from quiz_gen_util import rnd, place, tokens, mask, jaccard, LANGS

Q_TERM = ("Which term matches this description? “{d}”", "Quel terme correspond à cette description ? « {d} »", "Ni irihe jambo rihuye n'ibisobanuro bikurikira? «{d}»", "Ni neno gani linalolingana na maelezo haya? «{d}»")
Q_SCAM = ("Which scam is described here? “{d}”", "De quelle arnaque s'agit-il ? « {d} »", "Ubu ni uburiganya bwa bwoko ki? «{d}»", "Huu ni utapeli wa aina gani? «{d}»")
SLIP = ("These terms are related but mean different things: {o}. Read the key idea in the description, not a familiar word.",
        "Ces termes sont proches mais différents : {o}. Cherchez l'idée clé de la description, pas un mot familier.",
        "Aya magambo arahura ariko afite ibisobanuro bitandukanye: {o}. Reba igitekerezo nyamukuru mu bisobanuro, si ijambo usanzwe uzi.",
        "Maneno haya yanahusiana lakini yana maana tofauti: {o}. Tafuta wazo kuu katika maelezo, si neno unalolijua.")
WHY = ("“{n}”: {m}", "« {n} » : {m}", "«{n}»: {m}", "«{n}»: {m}")
SKIP_NAME = re.compile(r"^(types of|famous|well-known|common |how to|checking|cybersecurity (roles|agencies)|security tools|firewall and|malware analysis and|digital forensics tools|detection methods|attacks on|hardware attacks|red flags|reading a|cyber hygiene|cybersecurity$|osint tools|password auditing|wi-fi auditing|vulnerability scanners|internet scanners|forensic|mobile money|rwanda|national cyber|personal data|data protection laws|malabo)", re.I)

ACRONYMS = [("CIA triad", "Confidentiality, Integrity, Availability"), ("MFA", "Multi-Factor Authentication"), ("2FA", "Two-Factor Authentication"), ("OTP", "One-Time Password"),
    ("IDS", "Intrusion Detection System"), ("IPS", "Intrusion Prevention System"), ("SIEM", "Security Information and Event Management"), ("SOC", "Security Operations Center"),
    ("EDR", "Endpoint Detection and Response"), ("XDR", "Extended Detection and Response"), ("MDR", "Managed Detection and Response"), ("NDR", "Network Detection and Response"),
    ("DLP", "Data Loss Prevention"), ("VPN", "Virtual Private Network"), ("WAF", "Web Application Firewall"), ("DDoS", "Distributed Denial of Service"), ("DoS", "Denial of Service"),
    ("XSS", "Cross-Site Scripting"), ("CSRF", "Cross-Site Request Forgery"), ("SSRF", "Server-Side Request Forgery"), ("IDOR", "Insecure Direct Object Reference"), ("XXE", "XML External Entity"),
    ("RCE", "Remote Code Execution"), ("LFI", "Local File Inclusion"), ("MITM", "Man-in-the-Middle"), ("PKI", "Public Key Infrastructure"), ("CA", "Certificate Authority"),
    ("TLS", "Transport Layer Security"), ("SSL", "Secure Sockets Layer"), ("SSH", "Secure Shell"), ("AES", "Advanced Encryption Standard"), ("ECC", "Elliptic Curve Cryptography"),
    ("SHA", "Secure Hash Algorithm"), ("HMAC", "Hash-based Message Authentication Code"), ("IAM", "Identity and Access Management"), ("PAM", "Privileged Access Management"),
    ("RBAC", "Role-Based Access Control"), ("ABAC", "Attribute-Based Access Control"), ("DAC", "Discretionary Access Control"), ("SSO", "Single Sign-On"), ("SAML", "Security Assertion Markup Language"),
    ("LDAP", "Lightweight Directory Access Protocol"), ("CVE", "Common Vulnerabilities and Exposures"), ("CVSS", "Common Vulnerability Scoring System"), ("CWE", "Common Weakness Enumeration"),
    ("OWASP", "Open Worldwide Application Security Project"), ("NIST", "National Institute of Standards and Technology"), ("GDPR", "General Data Protection Regulation"),
    ("PCI DSS", "Payment Card Industry Data Security Standard"), ("HIPAA", "Health Insurance Portability and Accountability Act"), ("SOAR", "Security Orchestration, Automation and Response"),
    ("APT", "Advanced Persistent Threat"), ("IOC", "Indicator of Compromise"), ("TTP", "Tactics, Techniques and Procedures"), ("RAT", "Remote Access Trojan"), ("C2", "Command and Control"),
    ("BEC", "Business Email Compromise"), ("SPF", "Sender Policy Framework"), ("DKIM", "DomainKeys Identified Mail"), ("DMARC", "Domain-based Message Authentication, Reporting and Conformance"),
    ("DNSSEC", "Domain Name System Security Extensions"), ("HSTS", "HTTP Strict Transport Security"), ("CSP", "Content Security Policy"), ("CORS", "Cross-Origin Resource Sharing"),
    ("SAST", "Static Application Security Testing"), ("DAST", "Dynamic Application Security Testing"), ("IAST", "Interactive Application Security Testing"), ("RASP", "Runtime Application Self-Protection"),
    ("SBOM", "Software Bill of Materials"), ("SDLC", "Software Development Life Cycle"), ("CISO", "Chief Information Security Officer"), ("DPO", "Data Protection Officer"),
    ("BCP", "Business Continuity Plan"), ("DRP", "Disaster Recovery Plan"), ("RTO", "Recovery Time Objective"), ("RPO", "Recovery Point Objective"), ("BIA", "Business Impact Analysis"),
    ("UEBA", "User and Entity Behavior Analytics"), ("CASB", "Cloud Access Security Broker"), ("CSPM", "Cloud Security Posture Management"), ("SASE", "Secure Access Service Edge"),
    ("ZTNA", "Zero Trust Network Access"), ("NGFW", "Next-Generation Firewall"), ("UTM", "Unified Threat Management"), ("TPM", "Trusted Platform Module"), ("HSM", "Hardware Security Module"),
    ("FIDO2", "Fast IDentity Online 2"), ("PII", "Personally Identifiable Information"), ("CTF", "Capture The Flag"), ("CERT", "Computer Emergency Response Team"),
    ("CSIRT", "Computer Security Incident Response Team"), ("OSINT", "Open-Source Intelligence"), ("ARP", "Address Resolution Protocol"), ("NAC", "Network Access Control"),
    ("ISMS", "Information Security Management System"), ("GRC", "Governance, Risk and Compliance"), ("MTTR", "Mean Time To Respond (or Recover)"), ("PEN test", "Penetration test")]
AQ = ("What does {a} stand for?", "Que signifie {a} ?", "{a} ni impfunyisho y'iki?", "{a} inasimamia nini?")
AWHY = ("{a} stands for {e}.", "{a} signifie {e}.", "{a} bivuga {e}.", "{a} inamaanisha {e}.")
ASLIP = ("The expansions look alike. Learn each acronym with the idea it names, not just its letters.", "Les développements se ressemblent. Apprenez chaque sigle avec l'idée qu'il désigne, pas seulement ses lettres.",
         "Ibisobanuro by'impfunyisho bisa. Iga buri funyisho n'igitekerezo gisobanura, si inyuguti gusa.", "Visanuku hufanana. Jifunze kila kifupi pamoja na wazo lake, si herufi tu.")


def _label(t, lang):
    return t[1] if lang == "en" else (t[5] or {}).get(lang) or t[1]


def _terms():
    import cyber_db
    return cyber_db.TERMS


def build(Q):
    r = rnd("cyber-gen-1")
    out, seen = [], set()
    terms = [t for t in _terms() if not SKIP_NAME.search(t[1])]
    by_cat = {}
    for t in terms:
        by_cat.setdefault(t[3], []).append(t)
    idx = {"en": 6, "fr": 8, "rw": 10, "sw": 12}
    for t in terms:
        if t[1] in seen:
            continue
        descs = {}
        ok = True
        for l in LANGS:
            toks = tokens(t[1]) | tokens(_label(t, l)) | {x for a in t[2] if len(a) >= 4 for x in tokens(a)}
            d = mask(t[idx[l]].strip(), toks, [t[1], _label(t, l)] + list(t[2]))
            words = d.split()
            if len(words) < 8 or d.count("____") > max(2, len(words) // 4) or len(d) > 330:
                ok = False
                break
            descs[l] = d
        if not ok:
            continue
        pool = [x for x in by_cat[t[3]] if x is not t] + [x for x in terms if x[3] != t[3]][:0]
        r.shuffle(pool)
        wrong = []
        for x in pool:
            if len(wrong) == 3:
                break
            if tokens(x[1]) & tokens(t[1]) or jaccard(x[6], t[6]) > 0.2 or x[1] in seen and False:
                continue
            if {a.lower() for a in x[2]} & {a.lower() for a in t[2]} or any(_label(x, l) == _label(t, l) for l in LANGS):
                continue
            if x[1].lower() in t[6].lower() or t[1].lower() in x[6].lower():       # one is defined in terms of the other
                continue
            wrong.append(x)
        if len(wrong) < 3:
            continue
        opts = {}
        ans = None
        order = list(wrong) + [t]
        r.shuffle(order)
        ans = order.index(t)
        for l in LANGS:
            opts[l] = [_label(x, l) for x in order]
        names = ", ".join(_label(x, "en") for x in wrong)
        why = tuple(WHY[i].format(n=_label(t, l), m=t[idx[l]].strip()) for i, l in enumerate(LANGS))
        slip = tuple(SLIP[i].format(o=", ".join(_label(x, l) for x in wrong)) for i, l in enumerate(LANGS))
        q = tuple(Q_TERM[i].format(d=descs[l]) for i, l in enumerate(LANGS))
        out.append(Q("cybersecurity", q, opts, ans, why, slip))
        seen.add(t[1])
    # ---- scams: description -> scam name
    try:
        import scams_db
        data = scams_db.DATA
        keys = [k for k in scams_db.ORDER if k in data]
        for k in keys:
            names, en, fr, rw, sw = data[k]
            loc = {"en": en, "fr": fr, "rw": rw, "sw": sw}
            toks = {x for a in names for x in tokens(a)} | {x for l in LANGS for x in tokens(loc[l][0])}
            d = {l: mask(loc[l][1].strip(), toks, list(names) + [loc[l][0]]) for l in LANGS}
            if any(len(d[l].split()) < 8 or d[l].count("____") > 3 for l in LANGS):
                continue
            pool = [x for x in keys if x != k]
            r.shuffle(pool)
            wrong = []
            for x in pool:
                if len(wrong) == 3:
                    break
                nx = data[x][1][0]
                if tokens(nx) & tokens(en[0]) or jaccard(data[x][1][1], en[1]) > 0.18 or nx.lower() in en[1].lower() or en[0].lower() in data[x][1][1].lower():
                    continue
                wrong.append(x)
            if len(wrong) < 3:
                continue
            order = wrong + [k]
            r.shuffle(order)
            opts = {l: [loc_name(data, x, l) for x in order] for l in LANGS}
            q = tuple(Q_SCAM[i].format(d=d[l]) for i, l in enumerate(LANGS))
            why = tuple(f"{loc[l][0]}: {loc[l][1]} " + loc[l][3] for l in LANGS)
            slip = tuple(SLIP[i].format(o=", ".join(loc_name(data, x, l) for x in wrong)) for i, l in enumerate(LANGS))
            out.append(Q("cybersecurity", q, opts, order.index(k), why, slip))
    except Exception:
        pass
    # ---- acronyms
    exps = [e for _, e in ACRONYMS]
    for i, (a, e) in enumerate(ACRONYMS):
        others = [x for x in exps if x != e and jaccard(x, e) < 0.5 and not (set(re.findall(r"[A-Za-z]+", x)) == set(re.findall(r"[A-Za-z]+", e)))]
        r.shuffle(others)
        opts, ans = place(r, e, others[:3])
        out.append(Q("cybersecurity", tuple(AQ[j].format(a=a) for j in range(4)), opts, ans, tuple(AWHY[j].format(a=a, e=e) for j in range(4)), ASLIP))
    return out


def loc_name(data, k, l):
    return data[k][1 + LANGS.index(l)][0]
