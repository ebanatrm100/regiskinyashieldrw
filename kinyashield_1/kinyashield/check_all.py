"""Run before anything else:  python check_all.py
Compiles every .py file, validates every rule pattern (regex valid, ASCII only, lower-case),
and checks that every text exists in all four languages."""
import py_compile, re, sys, pathlib

bad = 0
def fail(*a):
    global bad
    bad += 1
    print("PROBLEM:", *a)

files = sorted(pathlib.Path(".").glob("*.py")) + sorted(pathlib.Path("tests").glob("*.py")) + sorted(pathlib.Path("data").glob("*.py"))
for p in files:
    try:
        py_compile.compile(str(p), doraise=True)
        print("compiled ", p)
    except py_compile.PyCompileError as e:
        fail("SYNTAX ERROR", e)

if not bad:
    from safety_rules import RULES, LANGS, PROTECTIVE_PREFIX, GENERAL_ADVICE, VERDICTS, NO_GUARANTEE
    from ui_strings import UI

    def check_pattern(where, pat):
        try:
            re.compile(pat)
        except re.error as e:
            fail("bad regex", where, e)
        if not pat.isascii():
            fail("non-ASCII pattern (write accent-free)", where)
        if pat != pat.lower() and not re.search(r"\\[A-Z]", pat):
            fail("pattern should be lower-case", where)

    ids = set()
    for r in RULES:
        if r["id"] in ids: fail("duplicate rule id", r["id"])
        ids.add(r["id"])
        for k in ("title", "why", "advice"):
            for l in LANGS:
                if not r[k].get(l, "").strip(): fail("missing", r["id"], k, l)
        if "groups" in r:
            for gi, g in enumerate(r["groups"]):
                if not any(g.values()): fail("empty group", r["id"], gi)
                for l, pats in g.items():
                    for pat in pats: check_pattern(f'{r["id"]}.group{gi}.{l}', pat)
        else:
            for l, pats in r["patterns"].items():
                for pat in pats: check_pattern(f'{r["id"]}.{l}', pat)
    for l, pats in PROTECTIVE_PREFIX.items():
        for pat in pats: check_pattern(f"protective.{l}", pat)
    for l in LANGS:
        if len(GENERAL_ADVICE[l]) != len(GENERAL_ADVICE["en"]): fail("general advice length", l)
        for v in VERDICTS: 
            if not VERDICTS[v].get(l): fail("verdict", v, l)
        if not NO_GUARANTEE.get(l): fail("no_guarantee", l)
        for k in UI["en"]:
            if k not in UI[l]: fail("ui string missing", k, l)
            elif isinstance(UI["en"][k], list) and len(UI[l][k]) != len(UI["en"][k]): fail("ui list length", k, l)
    print("rules checked:", len(RULES), "| languages:", ", ".join(LANGS))
print("FAILED" if bad else "ALL OK")
sys.exit(1 if bad else 0)
