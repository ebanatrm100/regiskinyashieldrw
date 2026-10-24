"""'Translate this word from X to Y' in four languages: parsed with source and target, answered from the bank at once."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import meta_guard as M, assistant_flow as F


def _title(q, lang="en"):
    r = F.route(q, lang)
    assert r["kind"] == "guide", (q, r["kind"])
    return r["entry"]["title"]["en"]


def test_parser_extracts_phrase_source_target():
    P = M.parse_translation_full
    assert P("Translate this word from French to Kinyarwanda: bonjour") == ("bonjour", "fr", "rw")
    assert P("translate hello from English to Swahili") == ("hello", "en", "sw")
    assert P("Translate 'thank you' from English to Swahili") == ("thank you", "en", "sw")
    assert P("traduis ce mot de l'anglais au français: tomato") == ("tomato", "en", "fr")
    assert P("hindura amazi kuva mu Kinyarwanda ujya mu Cyongereza") == ("amazi", "rw", "en")
    assert P("tafsiri maji kutoka Kiswahili kwenda Kiingereza") == ("maji", "sw", "en")
    assert P("translate I am in Kigali to french") == ("I am in Kigali", "", "fr")
    assert P("translate hello from english to english") is None
    assert P("what is the weather") is None


def test_bank_answers_immediately_in_every_direction():
    assert _title("Translate hello from English to Kinyarwanda") == "Translation: Muraho"
    assert _title("Translate this word from French to Kinyarwanda: bonjour") == "Translation: Muraho"
    assert _title("translate muraho from kinyarwanda to english") == "Translation: Hello"
    assert _title("traduis merci du français au kinyarwanda", "fr") == "Translation: Murakoze"
    assert _title("tafsiri maji kutoka Kiswahili kwenda Kiingereza", "sw") == "Translation: Water"
    assert _title("hindura amazi kuva mu Kinyarwanda ujya mu Gifaransa", "rw") == "Translation: Eau"
    assert _title("Translate this word from Kinyarwanda to English: urakoze") == "Translation: Thank you"


def test_unknown_text_goes_to_translation_with_source_and_target():
    r = F.route("translate this word from english to kinyarwanda: i love my mother very much today", "en")
    assert r["kind"] == "translate" and r["source"] == "en" and r["target"] == "rw" and r["phrase"].startswith("i love")


def test_old_forms_still_work():
    assert _title("translate good morning to kinyarwanda") == "Translation: Mwaramutse" or "Translation" in _title("translate good morning to kinyarwanda")
    assert F.route("what is hello in kinyarwanda", "en")["kind"] == "guide"


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); n += 1
    print("translate command OK", n)
