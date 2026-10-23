"""The AI Technical Guide features: the explainer topics (four languages), the glossary, the demos and the strict calculator."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import ai_guide_db as G, ai_lab as L, assistant_flow as F

LANGS = ("en", "fr", "rw", "sw")


def test_every_topic_is_complete_in_four_languages():
    assert len(G._RAW) >= 20
    for e, kw, kwc in G._RAW:
        assert kw or kwc
        for l in LANGS:
            assert e["title"][l].strip() and len(e["answer"][l]) > 30, (e["id"], l)
        counts = {len(e["steps"][l]) for l in LANGS}
        assert len(counts) == 1, (e["id"], counts)        # same number of steps in every language
        for l in LANGS:
            if e["steps"][l]:
                assert e["steps_label"][l].strip(), (e["id"], l)
        for r in e["related"]:
            assert r in G.IDS, (e["id"], r)


def test_boundary_note_on_private_details():
    e = G.find("how does an ai assistant work")
    assert "not fully public" in e["answer"]["en"] and "pas entièrement publiques" in e["answer"]["fr"]


def test_misconceptions_and_honesty_rules_are_stated():
    m = G.find("common misconceptions about ai")
    assert len(m["steps"]["en"]) == 6
    w = G.find("does the model memorize training documents")
    assert "memorization can still occur" in w["answer"]["en"].lower() or "memorization can still occur" in w["answer"]["en"]
    c = G.find("are you conscious")
    assert "not evidence" in c["answer"]["en"]
    t = G.find("what is prompt injection")
    assert "untrusted" in t["answer"]["en"] and "not** a command" in t["answer"]["en"]


def test_questions_in_four_languages_reach_the_explainer():
    cases = [("How does an AI assistant work?", "en", "ai_big_picture"), ("Comment fonctionne une IA ?", "fr", "ai_big_picture"), ("ai inafanyaje kazi", "sw", "ai_big_picture"),
             ("ai ikora ite", "rw", "ai_big_picture"), ("what is attention in ai", "en", "ai_attention"), ("what is a logit", "en", "ai_decoding"),
             ("pourquoi l'ia se trompe", "fr", "ai_limits"), ("kwa nini ai hubuni", "sw", "ai_hallucination"), ("prompt injection ni iki", "rw", "ai_tools"),
             ("what is the difference between training and inference", "en", "ai_deployment"), ("how do i learn ai", "en", "ai_learning_path"),
             ("does one chat retrain the model", "en", "ai_deployment")]
    for q, l, want in cases:
        r = F.route(q, l)
        assert r["kind"] == "guide" and r["entry"]["id"] == want, (q, r["entry"]["id"] if r["kind"] == "guide" else r["kind"])


def test_glossary_and_terms():
    g = G.find("list ai terms")
    assert g["id"] == "ai_glossary" and g["answer"]["en"].count("\n- ") >= 15
    for l in LANGS:
        assert g["answer"][l].count("**") >= 32
    t = G.find("what is a logit")
    assert t["id"] == "ai_decoding"
    t2 = G.find("what is a context window")
    assert t2["id"] == "ai_context_memory"
    assert G.find("what is inference in an ai model")["id"] == "ai_deployment"


def test_ambiguous_words_need_an_ai_word_and_do_not_steal_other_topics():
    assert G.find("what is attention") is None                      # could be about anything
    assert G.find("what is a token in cybersecurity") is None
    for q in ("what is phishing?", "what is a firewall?", "Translate password into French", "hello", "who is your owner?", "list all cybersecurity terms"):
        r = F.route(q, "en")
        assert not (r["kind"] == "guide" and r["entry"].get("kind") in ("ai_guide", "ai_lab")), q


def test_token_counter_is_a_teaching_illustration():
    toks = L.split_tokens("Unbelievable cybersecurity, isn't it?")
    assert len(toks) > len("Unbelievable cybersecurity, isn't it?".split())     # one token is not one word
    assert toks[0] == "Unbe" and toks[1] == "##liev"
    r = L.find("count tokens: Unbelievable cybersecurity")
    assert r["id"] == "lab_tokens" and "teaching" in r["answer"]["en"]


def test_attention_numbers_are_correct():
    scores, w, out = L.attention_numbers()
    assert abs(sum(w) - 1) < 1e-9
    assert w[1] == max(w)                                                    # "book" gets the largest weight
    assert abs(out[0] - sum(wi * v[0] for wi, v in zip(w, L._ATT_V))) < 1e-12
    assert abs(scores[1] - (0.8 * 0.9 + 0.5 * 0.5) / math.sqrt(2)) < 1e-12


def test_loss_and_gradient_and_nextword():
    assert abs(L.loss_value(0.5) - math.log(2)) < 1e-12
    assert "0.2231" in L.find("loss 0.8")["answer"]["en"]
    assert "must be greater than 0" in L.find("loss 0")["answer"]["en"] or L.find("loss 0") is not None
    rows = L.gradient_steps()
    assert rows[0][2] > rows[3][2] > rows[6][2] and abs(rows[-1][1] - 2) < 0.2
    d = L.next_word_distribution("the cat sat. the cat ran. the dog sat.", "the")
    assert d[0][0] == "cat" and abs(d[0][2] - 2 / 3) < 1e-9 and abs(sum(p for _, _, p in d) - 1) < 1e-9


def test_chmod_worked_example():
    r = L.find("What does chmod 640 report.txt do?")
    a = r["answer"]["en"]
    assert "rw-r-----" in a and "owner" in a and "others no permissions" in a
    assert "rw-r--r--" in L.find("chmod 644 notes.txt")["answer"]["en"]
    assert "rwxr-xr-x" in L.find("chmod 755 run.sh")["answer"]["en"]
    assert "three octal digits" in L.chmod_demo("999")["answer"]["en"]
    assert "propriétaire" in L.find("chmod 640 report.txt")["answer"]["fr"]


def test_calculator_is_strict():
    assert L.safe_eval("12*(3+4)") == 84 and L.safe_eval("2^10") == 1024 and abs(L.safe_eval("10/4") - 2.5) < 1e-12
    for bad in ("__import__('os').system('id')", "2**100000", "10/0", "abs(-1)", "open('/etc/passwd')", "1e999*1e999", "(" * 50, "a+1", "[1]"):
        try:
            L.safe_eval(bad)
            assert False, bad
        except L.CalcError:
            pass
    assert L.find("calculate __import__('os')") is None                     # not even treated as a calculation
    assert "84" in L.find("calculate 12*(3+4)")["answer"]["en"]
    assert "= **84**" in L.find("calcule 12*(3+4)", "fr")["answer"]["fr"]


def test_demo_commands_do_not_capture_ordinary_questions():
    for q in ("calculate my risk of being scammed", "what is the loss of a stolen phone", "explain attention", "count the tokens please", "next word please", "what is gradient"):
        r = L.find(q)
        assert r is None, q


def test_demos_exist_in_all_four_languages():
    for q in ("attention demo", "next word demo", "gradient descent demo", "loss 0.5", "count tokens: hello world", "chmod 640 a.txt", "calculate 1+1"):
        e = L.find(q)
        for l in LANGS:
            assert e["title"][l].strip() and e["answer"][l].strip(), (q, l)


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("ai guide ok")
