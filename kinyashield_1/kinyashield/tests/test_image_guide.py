"""AI Image Generation guide: four-language topics, problem finder, glossary, prompt tools, routing."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import image_guide_db as G, image_lab as L, assistant_flow as F

LANGS = ("en", "fr", "rw", "sw")


def test_every_topic_complete_in_four_languages():
    assert len(G._RAW) >= 14
    for e, kw, kwc in G._RAW:
        assert kw or kwc
        for l in LANGS:
            assert e["title"][l].strip() and len(e["answer"][l]) > 30, (e["id"], l)
        assert len({len(e["steps"][l]) for l in LANGS}) == 1, e["id"]
        for l in LANGS:
            if e["steps"][l]:
                assert e["steps_label"][l].strip()
        for r in e["related"]:
            assert r in G.IDS or r.startswith("img_"), (e["id"], r)
    assert len(G.find("how does ai image generation work")["steps"]["en"]) == 7
    assert len(G.find("main techniques of ai image generation")["steps"]["sw"]) == 12
    assert len(G.find("image prompt ingredients")["steps"]["rw"]) == 12
    assert len(G.TERMS) == 14


def test_honest_boundaries():
    e = G.find("can you generate images")
    assert "do not" in e["answer"]["en"] and "ne fais pas" in e["answer"]["fr"]
    assert "private" in G.find("how does ai image generation work")["answer"]["en"]


def test_problem_finder_and_glossary():
    assert G.find("my image has bad hands")["id"] == "img_problem_3"
    assert G.find("the lighting looks wrong in my ai image")["id"] == "img_problem_2"
    assert G.find("what is inpainting")["id"] == "img_term_inpainting"
    assert G.find("what is phishing") is None
    for i in range(len(G.PROBLEMS)):
        assert all(G.problem_entry(i)["answer"][l].strip() for l in LANGS)


def test_four_language_lookup():
    assert G.find("Comment écrire un bon prompt d'image ?")["id"] == "img_ingredients"
    assert G.find("jinsi ya kuandika prompt nzuri ya picha")["id"] == "img_ingredients"
    assert G.find("uko wandika prompt nziza y'ishusho")["id"] == "img_ingredients"


def test_prompt_tools():
    r = L.find("improve prompt: cat", "fr")
    assert "Ingrédients manquants" in r["answer"]["fr"] and "pas dessiner" in r["answer"]["fr"] or "ne dessine pas" in r["answer"]["fr"]
    c = L.find("improve prompt: photorealistic watercolor sunset at night")["answer"]["en"]
    assert "photorealistic and a drawn style" in c and "two different times" in c
    s = L.find("score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2")["answer"]["en"]
    assert "3.6/5" in s and "Coherence" in s
    assert "x = 640 and 1280" in L.find("rule of thirds 1920x1080")["answer"]["en"]
    assert "9:16" in L.find("aspect ratio 1080x1920")["answer"]["en"]
    assert "16,384" in L.find("latent demo 512x512")["answer"]["en"]
    assert L.find("denoising demo") and L.find("what is a cat") is None


def test_routing():
    for q, kind in [("how does ai image generation work", "image_guide"), ("improve prompt: a dog on a beach", "image_lab")]:
        r = F.route(q, "en")
        assert r["kind"] == "guide" and r["entry"]["kind"] == kind, (q, r["kind"])
    assert F.route("what is phishing", "en")["kind"] != "guide" or F.route("what is phishing", "en")["entry"]["kind"] not in ("image_guide", "image_lab")


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("image guide OK", n)
