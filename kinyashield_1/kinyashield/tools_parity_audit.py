"""Parity audit: finds every per-language dict (en/fr/rw/sw) in the knowledge modules with a missing, empty or untranslated language."""
import os; sys_path_fix = __import__("sys").path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sys, types, importlib, collections
for n in ("streamlit",):
    if n not in sys.modules:
        try: importlib.import_module(n)
        except Exception: sys.modules[n] = types.ModuleType(n)
L = ("en", "fr", "rw", "sw")
MODS = """ai_guide_1 ai_guide_db computers_db cyber_db cyber_terms_1 cyber_terms_2 cyber_terms_3 cyber_terms_4 cyber_terms_5 cyber_terms_6 cyber_terms_7
definitions_db defs_computing defs_health_farm defs_language defs_science defs_society greetings_db image_guide_db images_db knowledge_base knowledge_code
knowledge_cosmos knowledge_general knowledge_history knowledge_life knowledge_more knowledge_stem names_db owner_db phones_db physics_data physics_db quiz_data
research_guide_db safety_rules safety_rules_more scams_data scams_db trust_db trusted_sources tutor_db writing_db translation_bank register_data""".split()
SHORT = 12  # texts shorter than this may legitimately be identical (numbers, names)

def walk(o, path, out, seen):
    if id(o) in seen: return
    seen.add(id(o))
    if isinstance(o, dict):
        ks = set(o)
        if ks and ks <= set(L) and "en" in ks:
            out.append((path, o)); return
        for k, v in o.items(): walk(v, path + "/" + str(k)[:25], out, seen)
    elif isinstance(o, (list, tuple)):
        for i, v in enumerate(o): walk(v, path + f"[{i}]", out, seen)

def text(v):
    if isinstance(v, (list, tuple)): return " ".join(map(str, v))
    return str(v or "")

def audit():
    rep = collections.OrderedDict()
    for m in MODS:
        try: mod = importlib.import_module(m)
        except Exception as e:
            rep[m] = {"import_error": repr(e)}; continue
        found = []
        for name in dir(mod):
            if name.startswith("__"): continue
            v = getattr(mod, name)
            if isinstance(v, (dict, list, tuple)): walk(v, name, found, set())
        miss = empty = same = 0; ex = []
        for path, d in found:
            en = text(d.get("en")).strip()
            for l in L[1:]:
                if l not in d and en: miss += 1; ex.append(("missing", l, path)); continue
                t = text(d[l]).strip()
                if not t and en: empty += 1; ex.append(("empty", l, path))
                elif t == en and len(en) > SHORT: same += 1; ex.append(("same-as-en", l, path))
        rep[m] = {"dicts": len(found), "missing": miss, "empty": empty, "same_as_en": same, "examples": ex[:60]}
    return rep

if __name__ == "__main__":
    r = audit(); bad = 0
    for m, x in r.items():
        if "import_error" in x: print(m, "IMPORT ERROR", x["import_error"]); continue
        flag = x["missing"] + x["empty"] + x["same_as_en"]; bad += flag
        print(f"{m:22} dicts={x['dicts']:5} missing={x['missing']:4} empty={x['empty']:4} same={x['same_as_en']:4}")
        for e in x["examples"][:60]: print("      ", e)
    print("TOTAL PROBLEMS", bad)
