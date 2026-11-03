"""World toolkit for the assistant: currency conversion (live rates, all world currencies), unit conversion, time and time zones, facts about every country
(capital, currency, calling code, languages, continent), distances between places, and date calculations. Understands English, French, Kinyarwanda and Kiswahili.
answer(question, lang) -> markdown text in the user's language, or None when the message is not one of these requests. Pure Python (urllib + zoneinfo); rates are fetched live
(open.er-api.com, then frankfurter.app), cached for an hour, and replaced by a clearly labelled approximate offline table when no network answers."""
from __future__ import annotations
import json
import math
import re
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone

from textutil import fold
import world_data as WD

# ------------------------------------------------------------------ small helpers
_NUM = r"\d[\d,._ ]*(?:\.\d+)?"


def _num(s: str):
    s = (s or "").strip().replace(" ", "")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        parts = s.split(",")
        s = s.replace(",", "") if (len(parts) > 2 or len(parts[-1]) == 3) else s.replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def _fmt(x: float, small: bool = False) -> str:
    if x == 0:
        return "0"
    ax = abs(x)
    if ax >= 100:
        s = f"{x:,.2f}"
    elif ax >= 1:
        s = f"{x:,.3f}"
    else:
        s = f"{x:,.6f}"
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return s


# ------------------------------------------------------------------ currencies
# code -> (English name, aliases in the four languages; all folded)
CUR = {
    "USD": ("US dollar", "usd dollar dollars us dollar us dollars american dollar dollar americain dollars americains dolari dolari y amerika amadolari dolari za amerika dola dola za marekani dola ya marekani $ us$ buck bucks"),
    "EUR": ("Euro", "eur euro euros ewuro amayero yuro ayero iyero €"),
    "GBP": ("British pound", "gbp pound pounds pound sterling pounds sterling british pound livre sterling livres sterling ipawundi pauni paundi mapaundi mapawundi £ sterling"),
    "RWF": ("Rwandan franc", "rwf frw rwandan franc rwandan francs franc rwandais francs rwandais amafaranga y u rwanda amafaranga yu rwanda amafaranga y'u rwanda ifaranga ry u rwanda faranga ya rwanda faranga za rwanda amafaranga y'amanyarwanda amafaranga"),
    "KES": ("Kenyan shilling", "kes kenyan shilling kenyan shillings shilling kenyan shilingi ya kenya shilingi za kenya shilingi ya kikenya amashiringi ya kenya"),
    "UGX": ("Ugandan shilling", "ugx ugandan shilling ugandan shillings shilling ougandais shilingi ya uganda amashiringi ya uganda"),
    "TZS": ("Tanzanian shilling", "tzs tanzanian shilling tanzanian shillings shilling tanzanien shilingi ya tanzania amashiringi ya tanzaniya"),
    "BIF": ("Burundian franc", "bif burundian franc burundian francs franc burundais amafaranga y uburundi faranga ya burundi"),
    "CDF": ("Congolese franc", "cdf congolese franc congolese francs franc congolais amafaranga ya kongo faranga ya kongo"),
    "XOF": ("West African CFA franc", "xof franc cfa francs cfa cfa west african franc fcfa"),
    "XAF": ("Central African CFA franc", "xaf central african franc franc cfa beac"),
    "JPY": ("Japanese yen", "jpy yen yens japanese yen ¥ yeni"),
    "CNY": ("Chinese yuan", "cny yuan renminbi rmb chinese yuan yuan chinois ubushinwa yuan"),
    "INR": ("Indian rupee", "inr rupee rupees indian rupee roupie roupies roupie indienne rupia"),
    "NGN": ("Nigerian naira", "ngn naira nigerian naira"),
    "GHS": ("Ghanaian cedi", "ghs cedi cedis ghanaian cedi"),
    "ZAR": ("South African rand", "zar rand south african rand rand sud africain randi"),
    "ETB": ("Ethiopian birr", "etb birr ethiopian birr"),
    "AED": ("UAE dirham", "aed dirham dirhams uae dirham emirati dirham dirham des emirats"),
    "SAR": ("Saudi riyal", "sar riyal riyals saudi riyal"),
    "QAR": ("Qatari riyal", "qar qatari riyal"),
    "CHF": ("Swiss franc", "chf swiss franc swiss francs franc suisse francs suisses"),
    "CAD": ("Canadian dollar", "cad canadian dollar canadian dollars dollar canadien dollars canadiens"),
    "AUD": ("Australian dollar", "aud australian dollar australian dollars dollar australien dollars australiens"),
    "NZD": ("New Zealand dollar", "nzd new zealand dollar kiwi dollar"),
    "RUB": ("Russian ruble", "rub ruble rubles rouble roubles russian ruble"),
    "KRW": ("South Korean won", "krw won korean won"),
    "TRY": ("Turkish lira", "try lira turkish lira livre turque"),
    "BRL": ("Brazilian real", "brl real reais brazilian real"),
    "MXN": ("Mexican peso", "mxn peso pesos mexican peso peso mexicain"),
    "EGP": ("Egyptian pound", "egp egyptian pound livre egyptienne"),
    "MAD": ("Moroccan dirham", "mad moroccan dirham dirham marocain"),
    "SGD": ("Singapore dollar", "sgd singapore dollar"),
    "HKD": ("Hong Kong dollar", "hkd hong kong dollar"),
    "SEK": ("Swedish krona", "sek swedish krona krona kronor couronne suedoise"),
    "NOK": ("Norwegian krone", "nok norwegian krone krone couronne norvegienne"),
    "DKK": ("Danish krone", "dkk danish krone couronne danoise"),
    "PLN": ("Polish zloty", "pln zloty polish zloty"),
    "THB": ("Thai baht", "thb baht thai baht"),
    "IDR": ("Indonesian rupiah", "idr rupiah indonesian rupiah"),
    "MYR": ("Malaysian ringgit", "myr ringgit malaysian ringgit"),
    "PHP": ("Philippine peso", "php philippine peso peso philippin"),
    "PKR": ("Pakistani rupee", "pkr pakistani rupee"),
    "BDT": ("Bangladeshi taka", "bdt taka bangladeshi taka"),
    "ILS": ("Israeli shekel", "ils shekel shekels israeli shekel"),
    "ZMW": ("Zambian kwacha", "zmw kwacha zambian kwacha"),
    "MWK": ("Malawian kwacha", "mwk malawian kwacha"),
    "MZN": ("Mozambican metical", "mzn metical mozambican metical"),
    "SSP": ("South Sudanese pound", "ssp south sudanese pound"),
    "SDG": ("Sudanese pound", "sdg sudanese pound"),
    "SOS": ("Somali shilling", "sos somali shilling"),
    "DZD": ("Algerian dinar", "dzd algerian dinar dinar algerien"),
    "TND": ("Tunisian dinar", "tnd tunisian dinar dinar tunisien"),
    "KWD": ("Kuwaiti dinar", "kwd kuwaiti dinar"),
    "BTC": ("Bitcoin", "btc bitcoin bitcoins"),
}
def _build_aliases():
    out = {}
    for code, (name, al) in CUR.items():
        out[fold(name)] = code
        out[code.lower()] = code
        toks = al.split(" ")
        # greedy: register every 1..4 word window as an alias candidate only for the explicit phrases listed (multi-word) and single words
        i = 0
        while i < len(toks):
            out.setdefault(fold(toks[i]), code)
            i += 1
        for n in (2, 3, 4):
            for j in range(len(toks) - n + 1):
                ph = " ".join(toks[j:j + n])
                out.setdefault(fold(ph), code)
    # words that are ambiguous when taken alone must not point to a single currency by accident
    for amb in ("franc", "francs", "shilling", "shillings", "pound", "pounds", "dinar", "dirham", "krona", "krone", "peso", "rupee", "rupees", "riyal", "kwacha", "lira", "real", "won", "amafaranga", "cfa", "dollar", "dollars"):
        out.pop(amb, None)
    out.update({"dollar": "USD", "dollars": "USD", "us dollar": "USD", "franc": "RWF", "francs": "RWF", "amafaranga": "RWF", "rwandan": "RWF", "pound": "GBP", "pounds": "GBP", "shilling": "KES", "shillings": "KES",
                "rupee": "INR", "rupees": "INR", "dirham": "AED", "riyal": "SAR", "peso": "MXN", "lira": "TRY", "real": "BRL", "won": "KRW"})
    return out


ALIAS = _build_aliases()
# country name -> currency ("convert to the money of Japan")
_COUNTRY_NAMES = {}
for _c in WD.COUNTRIES:
    _COUNTRY_NAMES[fold(_c["en"])] = _c["iso"]
    _COUNTRY_NAMES[fold(_c["fr"])] = _c["iso"]
for _k, _v in WD.ALIASES.items():
    _COUNTRY_NAMES[fold(_k)] = _v

OFFLINE_RATES = {   # approximate units per 1 USD, used only when no live source answers (clearly labelled to the user)
    "USD": 1, "EUR": 0.92, "GBP": 0.78, "RWF": 1440, "KES": 129, "UGX": 3650, "TZS": 2650, "BIF": 2900, "CDF": 2850, "XOF": 600, "XAF": 600, "JPY": 150, "CNY": 7.2, "INR": 84, "NGN": 1550, "GHS": 15, "ZAR": 18,
    "ETB": 125, "AED": 3.67, "SAR": 3.75, "QAR": 3.64, "CHF": 0.88, "CAD": 1.38, "AUD": 1.52, "NZD": 1.66, "RUB": 95, "KRW": 1380, "TRY": 34, "BRL": 5.6, "MXN": 19.5, "EGP": 49, "MAD": 9.8, "SGD": 1.33, "HKD": 7.8,
    "SEK": 10.5, "NOK": 10.8, "DKK": 6.9, "PLN": 4.0, "THB": 34, "IDR": 15800, "MYR": 4.4, "PHP": 57, "PKR": 278, "BDT": 120, "ILS": 3.7, "ZMW": 27, "MWK": 1740, "MZN": 64, "SSP": 1300, "SDG": 600, "SOS": 570,
    "DZD": 134, "TND": 3.1, "KWD": 0.31,
}
_RATES = {"t": 0.0, "rates": None, "source": "", "updated": ""}
RATE_TTL = 3600
RATE_TIMEOUT = 5


def _http_json(url, timeout=RATE_TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": "KinyaShieldRW/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:      # noqa: S310 (fixed https URLs)
        return json.loads(r.read().decode("utf-8", "replace"))


def get_rates(fetch=None, now=None):
    """({code: units per 1 USD}, source label, 'updated' text, live: bool). Never raises."""
    t = now if now is not None else time.time()
    if _RATES["rates"] and fetch is None and t - _RATES["t"] < RATE_TTL:
        return _RATES["rates"], _RATES["source"], _RATES["updated"], True
    fetch = fetch or _http_json
    for url, parse in (("https://open.er-api.com/v6/latest/USD", lambda d: (d["rates"], "open.er-api.com", d.get("time_last_update_utc", ""))),
                       ("https://api.frankfurter.app/latest?from=USD", lambda d: ({**d["rates"], "USD": 1}, "frankfurter.app (European Central Bank)", d.get("date", "")))):
        try:
            rates, src, upd = parse(fetch(url))
            rates = {k.upper(): float(v) for k, v in rates.items() if isinstance(v, (int, float)) and v > 0}
            if len(rates) > 10 and "RWF" in rates or len(rates) > 25:
                if fetch is _http_json:
                    _RATES.update(t=t, rates=rates, source=src, updated=upd)
                return rates, src, upd, True
        except Exception:      # noqa: BLE001
            continue
    return dict(OFFLINE_RATES), "offline approximate table", "", False


def convert_currency(amount, frm, to, rates):
    return amount / rates[frm] * rates[to] if frm in rates and to in rates else None


def currency_code(text: str):
    """ISO code for a currency word/phrase ('rwandan francs', 'euro', 'jpy', 'amadolari', 'money of Japan'), else None."""
    t = fold(text).strip(" .,;:!?'\"")
    t = re.sub(r"^(?:the|le|la|les|l'|des|de|du|d'|y'|ya|za|wa|mu|in|into|to|en|vers|kuri|kwa|a|an|of)\s+", "", t).strip()
    if not t:
        return None
    if t in ALIAS:
        return ALIAS[t]
    if re.fullmatch(r"[a-z]{3}", t) and t.upper() in OFFLINE_RATES:
        return t.upper()
    if re.fullmatch(r"[a-z]{3}", t):
        return t.upper()           # the live table may know it; unknown codes are reported later
    m = re.match(r"^(?:(?:the )?(?:money|currency|monnaie|devise|amafaranga|sarafu|pesa)\s+(?:of|de|du|y'|ya|za)\s+)?(.+)$", t)
    name = (m.group(1) if m else t).strip()
    iso = _COUNTRY_NAMES.get(name)
    if not iso:
        for pre in ("the ", "u ", "i "):
            if name.startswith(pre):
                iso = _COUNTRY_NAMES.get(name[len(pre):])
    if iso and iso in WD.BY_ISO:
        return WD.BY_ISO[iso]["cur"]
    # last words ("kenyan shilling" typed with a typo-free adjective): try the longest alias suffix
    parts = t.split(" ")
    for n in range(len(parts) - 1, 0, -1):
        suf = " ".join(parts[-n:])
        if suf in ALIAS:
            return ALIAS[suf]
    return None


_MAIN = ["USD", "EUR", "GBP", "RWF", "KES", "UGX", "TZS", "BIF", "CDF", "XOF", "ZAR", "NGN", "JPY", "CNY", "INR", "AED", "CAD", "AUD", "CHF"]
_ALL = re.compile(r"\b(?:all|every|everything|other|major|main|world|toutes?|tous|autres|principales?|byose|zose|izindi|yose|zote|nyingine|kuu)\b", re.I)
_SPLIT = re.compile(r"\s*(?:,|;|\band\b|\bet\b|\bna\b|\bn'|\bsaha\b|\bpamoja na\b|\bhamwe na\b|&|/|\bor\b|\bou\b)\s*", re.I)
_VERB = r"(?:convert(?:ir)?|converti(?:s|r|ssez)?|change(?:r|z)?|exchange|how much (?:is|are|does|do)|what(?:'s| is| are)|combien (?:font|fait|valent|vaut|ca fait|cela fait)|ca fait combien|c'est combien|quel(?:le)? est (?:le |la )?(?:valeur|montant)|hindura|bwira|mbwira|mpindurire|badilisha|nibadilishie|ni angahe|ni ngahe|ni kangahe|ni nini|je(?:,)?|thamani ya|ngapi)"
_PREP = r"(?:\s+(?:to|into|in|en|vers|mu|muri|kuri|kwa|kuwa|hadi|ndani ya|a|à|equals?)\s+|\s*(?:=>|->|→|=)\s*)"
_CURQ = re.compile(rf"^\W*(?:please\W+|s'il (?:te|vous) pla[iî]t\W+|nyabuneka\W+|tafadhali\W+)?(?:can you\W+|could you\W+|peux-tu\W+|pouvez-vous\W+)?(?:{_VERB}\W+)*(?:\W*(?:the\W+)?(?:value|amount|valeur|montant)\W+of\W+)?(?P<amt>{_NUM})?\s*(?P<frm>[^\d=→>]+?){_PREP}(?P<to>.+?)\s*[?!.]*$", re.I)
_BARE = re.compile(rf"^\W*(?:{_VERB}\W+)*(?P<amt>{_NUM})\s*(?P<frm>[A-Za-z$€£¥][A-Za-z$€£¥' .\-]*?)\s*[?!.]*$", re.I)
_RATEQ = re.compile(r"\b(?:exchange rate|rate|taux(?: de change)?|igiciro cy'ivunjisha|ivunjisha|kiwango cha (?:ubadilishaji|kubadilisha)|bei ya)\b", re.I)


def currency_answer(q: str, lang: str, fetch=None):
    m = _CURQ.match(q.strip())
    amt = None
    frm = to = None
    if m:
        amt = _num(m.group("amt")) if m.group("amt") else None
        frm_t, to_t = m.group("frm").strip(), m.group("to").strip()
        frm_t = re.sub(r"^(?:from|de|du|d'|kuva|kutoka|y'|ya)\s+", "", fold(frm_t)).strip()
        frm = currency_code(frm_t)
        to_parts = [p for p in _SPLIT.split(to_t) if p.strip()]
        if _ALL.search(to_t) and not any(currency_code(p) for p in to_parts):
            to = list(_MAIN)
        else:
            to = [c for c in (currency_code(p) for p in to_parts) if c]
            if not to and currency_code(to_t):
                to = [currency_code(to_t)]
    else:
        b = _BARE.match(q.strip())
        if b:
            amt = _num(b.group("amt"))
            frm = currency_code(fold(b.group("frm")))
            to = list(_MAIN) if frm else []
    if not frm or not to:
        return None
    if amt is None:
        amt = 1.0 if (_RATEQ.search(q) or not m or not m.group("amt")) else None
    if amt is None:
        return None
    if frm and not (frm in OFFLINE_RATES or frm in CUR or re.fullmatch(r"[A-Z]{3}", frm)):
        return None
    rates, src, upd, live = get_rates(fetch)
    for code in [frm] + to:
        if code not in rates:
            return _T[lang]["cur_unknown"].format(c=code)
    to = [c for c in dict.fromkeys(to) if c != frm] or [frm]
    name = lambda c: CUR.get(c, (c,))[0]            # noqa: E731
    lines = []
    if len(to) == 1:
        v = convert_currency(amt, frm, to[0], rates)
        lines.append(f"**{_fmt(amt)} {frm}** ({name(frm)}) = **{_fmt(v)} {to[0]}** ({name(to[0])})")
        r1 = convert_currency(1, frm, to[0], rates)
        r2 = convert_currency(1, to[0], frm, rates)
        lines.append(f"1 {frm} = {_fmt(r1)} {to[0]} · 1 {to[0]} = {_fmt(r2)} {frm}")
    else:
        lines.append(f"**{_fmt(amt)} {frm}** ({name(frm)}):")
        for c in to:
            lines.append(f"- {_fmt(convert_currency(amt, frm, c, rates))} **{c}** ({name(c)})")
    T = _T[lang]
    lines.append("")
    lines.append((T["rates_live"].format(src=src, upd_=(" (" + upd.strip() + ")" if upd and upd.strip() else "")) if live else T["rates_off"]))
    lines.append(T["rates_note"])
    return "\n".join(lines)


# ------------------------------------------------------------------ units
# category -> {unit: factor to the base unit}; temperature is handled separately
UNITS = {
    "length": ({"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254, "nmi": 1852, "um": 1e-6},
               {"m": "metre meter metres meters metre metres umunota metero mita", "km": "km kilometre kilometer kilometres kilometers kilometre kilometres kilometero kilomita", "cm": "cm centimetre centimeter centimetres centimeters centimetre sentimetero sentimita",
                "mm": "mm millimetre millimeter millimetres millimeters milimetero milimita", "mi": "mile miles mi mille milles maili", "yd": "yard yards yd yards", "ft": "ft foot feet pied pieds", "in": "inch inches in pouce pouces",
                "nmi": "nautical mile nautical miles nmi mille marin milles marins", "um": "micron micrometre micrometer"}),
    "mass": ({"kg": 1, "g": 0.001, "mg": 1e-6, "t": 1000, "lb": 0.45359237, "oz": 0.028349523125, "st": 6.35029318, "qt": 100},
             {"kg": "kg kilogram kilograms kilogramme kilogrammes kilo kilos kilogarama ikiro ibiro kilo", "g": "g gram grams gramme grammes garama", "mg": "mg milligram milligrams milligramme milligrammes", "t": "tonne tonnes ton tons metric ton tonnes metriques toni",
              "lb": "lb lbs pound pounds livre livres paundi mapaundi mapawundi pauni", "oz": "oz ounce ounces once onces", "st": "stone stones", "qt": "quintal quintals kwintali"}),
    "volume": ({"l": 1, "ml": 0.001, "m3": 1000, "gal": 3.785411784, "galuk": 4.54609, "cup": 0.2365882365, "tbsp": 0.01478676478, "tsp": 0.00492892159, "floz": 0.0295735296, "pt": 0.473176473, "qtus": 0.946352946},
               {"l": "l litre litres liter liters litiro", "ml": "ml millilitre millilitres milliliter milliliters mililita", "m3": "m3 cubic metre cubic meter cubic metres metre cube metres cubes",
                "gal": "gallon gallons us gallon gal galon", "galuk": "uk gallon imperial gallon", "cup": "cup cups tasse tasses kikombe", "tbsp": "tbsp tablespoon tablespoons cuillere a soupe", "tsp": "tsp teaspoon teaspoons cuillere a cafe",
                "floz": "fl oz fluid ounce fluid ounces", "pt": "pint pints pinte pintes", "qtus": "us quart quarts"}),
    "area": ({"m2": 1, "km2": 1e6, "ha": 10000, "acre": 4046.8564224, "ft2": 0.09290304, "mi2": 2589988.110336, "yd2": 0.83612736, "cm2": 1e-4},
             {"m2": "m2 square metre square meter square metres square meters metre carre metres carres", "km2": "km2 square kilometre square kilometer square kilometres kilometre carre kilometres carres", "ha": "ha hectare hectares hegitari",
              "acre": "acre acres", "ft2": "ft2 square foot square feet sq ft pied carre", "mi2": "mi2 square mile square miles sq mi", "yd2": "yd2 square yard square yards", "cm2": "cm2 square centimetre square centimeter"}),
    "speed": ({"ms": 1, "kmh": 1 / 3.6, "mph": 0.44704, "kn": 0.514444, "fts": 0.3048},
              {"ms": "m/s metre per second meters per second metres par seconde", "kmh": "km/h kmh kph kilometres per hour kilometers per hour kilometre heure kilometres heure km par heure km/hr", "mph": "mph miles per hour miles par heure",
               "kn": "knot knots kn noeud noeuds", "fts": "ft/s feet per second"}),
    "data": ({"b": 1, "kb": 1000, "mb": 1e6, "gb": 1e9, "tb": 1e12, "pb": 1e15, "kib": 1024, "mib": 1024 ** 2, "gib": 1024 ** 3, "tib": 1024 ** 4, "bit": 0.125, "kbit": 125, "mbit": 125000, "gbit": 125000000},
             {"b": "byte bytes octet octets", "kb": "kb kilobyte kilobytes ko kilooctet", "mb": "mb megabyte megabytes mo megaoctet", "gb": "gb gigabyte gigabytes go gigaoctet", "tb": "tb terabyte terabytes to teraoctet", "pb": "pb petabyte petabytes",
              "kib": "kib kibibyte", "mib": "mib mebibyte", "gib": "gib gibibyte", "tib": "tib tebibyte", "bit": "bit bits", "kbit": "kbit kilobit kilobits kbps", "mbit": "mbit megabit megabits mbps", "gbit": "gbit gigabit gigabits gbps"}),
    "time": ({"s": 1, "min": 60, "h": 3600, "d": 86400, "wk": 604800, "mo": 2629746, "yr": 31556952, "ms_": 0.001},
             {"s": "s sec second seconds seconde secondes isegonda sekunde", "min": "min minute minutes umunota iminota dakika", "h": "h hr hour hours heure heures isaha amasaha saa", "d": "day days jour jours umunsi iminsi siku",
              "wk": "week weeks semaine semaines icyumweru ibyumweru wiki", "mo": "month months mois ukwezi amezi mwezi miezi", "yr": "year years an ans annee annees umwaka imyaka mwaka miaka", "ms_": "millisecond milliseconds milliseconde millisecondes"}),
    "energy": ({"j": 1, "kj": 1000, "cal": 4.184, "kcal": 4184, "wh": 3600, "kwh": 3.6e6, "btu": 1055.05585},
               {"j": "j joule joules", "kj": "kj kilojoule kilojoules", "cal": "cal calorie calories", "kcal": "kcal kilocalorie kilocalories", "wh": "wh watt hour watt hours", "kwh": "kwh kilowatt hour kilowatt hours kilowattheure", "btu": "btu"}),
    "pressure": ({"pa": 1, "kpa": 1000, "bar": 100000, "psi": 6894.757, "atm": 101325, "mmhg": 133.322},
                 {"pa": "pa pascal pascals", "kpa": "kpa kilopascal kilopascals", "bar": "bar bars", "psi": "psi", "atm": "atm atmosphere atmospheres", "mmhg": "mmhg mm hg torr"}),
}
_TEMP = {"c": "celsius centigrade degree celsius degrees celsius c °c degres celsius degre celsius selisiyasi", "f": "fahrenheit degree fahrenheit degrees fahrenheit f °f degres fahrenheit", "k": "kelvin kelvins k"}
_UALIAS = {}
for _cat, (_f, _al) in UNITS.items():
    for _u, _names in _al.items():
        _UALIAS.setdefault(fold(_u), (_cat, _u))
        _toks = _names.split(" ")
        for _n in (1, 2, 3, 4):
            for _j in range(len(_toks) - _n + 1):
                _UALIAS.setdefault(fold(" ".join(_toks[_j:_j + _n])), (_cat, _u))
for _u, _names in _TEMP.items():
    _toks = _names.split(" ")
    for _n in (1, 2, 3):
        for _j in range(len(_toks) - _n + 1):
            _UALIAS.setdefault(fold(" ".join(_toks[_j:_j + _n])), ("temp", _u))
_UNITQ = re.compile(rf"^\W*(?:{_VERB}\W+)*(?P<amt>-?{_NUM})\s*(?P<frm>°?[A-Za-z/²³0-9' .\-]*?)(?:{_PREP}|\s+as\s+)(?P<to>°?[A-Za-z/²³0-9' .\-]+?)\s*[?!.]*$", re.I)


def _unit(text: str):
    t = fold(text).strip(" .,;:!?'\"")
    t = t.replace("²", "2").replace("³", "3").replace("degres ", "degree ").replace("°", "")
    t = re.sub(r"^(?:the|le|la|les|des|de|du|d'|ya|za|wa|y'|a|an|of|square|carre)\s+(?=\w)", lambda m: m.group(0) if m.group(0).strip() == "square" else "", t).strip()
    if t in _UALIAS:
        return _UALIAS[t]
    t2 = re.sub(r"\s+per\s+", " per ", t)
    return _UALIAS.get(t2)


def unit_answer(q: str, lang: str):
    m = _UNITQ.match(q.strip())
    if not m:
        return None
    amt = _num(m.group("amt"))
    if amt is None:
        return None
    a, b = _unit(m.group("frm")), _unit(m.group("to"))
    if not a or not b or a[0] != b[0]:
        return None
    cat = a[0]
    if cat == "temp":
        v = amt
        c = v if a[1] == "c" else (v - 32) * 5 / 9 if a[1] == "f" else v - 273.15
        out = c if b[1] == "c" else c * 9 / 5 + 32 if b[1] == "f" else c + 273.15
        sym = {"c": "°C", "f": "°F", "k": "K"}
        return f"**{_fmt(amt)} {sym[a[1]]}** = **{_fmt(out)} {sym[b[1]]}**"
    fac = UNITS[cat][0]
    out = amt * fac[a[1]] / fac[b[1]]
    nm = lambda u: u.replace("galuk", "UK gal").replace("qtus", "US qt").replace("ms_", "ms").replace("floz", "fl oz").replace("kmh", "km/h").replace("ms", "m/s") if u != "ms_" else "ms"       # noqa: E731
    return f"**{_fmt(amt)} {nm(a[1])}** = **{_fmt(out)} {nm(b[1])}**"


# ------------------------------------------------------------------ places: countries and cities
def find_place(text: str):
    """('country', country dict) or ('city', (name, lat, lon, iso, tz)) for a place name in any of the 4 languages, else None."""
    t = fold(text).strip(" .,;:!?'\"")
    t = re.sub(r"^(?:the|la|le|les|l'|u |i |in|at|a|au|aux|en|à|mu|muri|kuri|i)\s+(?=\w)", "", t).strip()
    t = re.sub(r"^(?:the|la|le|les|l'|u |i |au |en |mu |muri )", "", t).strip()
    if t in _COUNTRY_NAMES and _COUNTRY_NAMES[t] in WD.BY_ISO:
        return ("country", WD.BY_ISO[_COUNTRY_NAMES[t]])
    for c in WD.COUNTRIES:
        if fold(c["capital"]) == t:
            return ("city", (c["capital"], c["lat"], c["lon"], c["iso"], c["tz"]))
    for k, (la, lo, iso, tz) in WD.CITIES.items():
        if fold(k.strip()) == t:
            return ("city", (k.strip().title(), la, lo, iso, tz))
    return None


def _tz_for(place):
    kind, v = place
    return v["tz"] if kind == "country" else v[4]


def _label(place):
    kind, v = place
    return v["en"] if kind == "country" else v[0]


def _coords(place):
    kind, v = place
    return (v["lat"], v["lon"]) if kind == "country" else (v[1], v[2])


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0088 * 2 * math.asin(math.sqrt(d))


_TIMEQ = re.compile(r"^\W*(?:what(?:'s| is)? the (?:current |local )?time (?:is it )?(?:in|at)|what time is it (?:in|at)|current time (?:in|at)|local time (?:in|at)|time (?:in|at)|quelle heure est[- ]il (?:a|à|au|en)|quelle heure (?:a|à|au|en)|heure (?:a|à|au|en)|il est quelle heure (?:a|à|au|en)|isaha (?:i|ku|mu|kuri)|saa ngapi (?:ni )?(?:huko |kule )?|saa ngapi|ni saa ngapi (?:huko |kule )?|muri)\s*(?P<p>.+?)\s*[?!.]*$", re.I)
_TIMEQ2 = re.compile(r"^\W*(?P<p>.+?)\s+(?:time|current time|local time)\s*[?!.]*$", re.I)
_CONVT = re.compile(r"^\W*(?:convert\W+|what(?:'s| is)\W+)?(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s*(?P<ap>am|pm|h)?\s+(?:in\s+|at\s+|a\s+|à\s+|i\s+|ku\s+|saa\s+)?(?P<a>[a-zà-ÿ' .-]+?)\s+(?:time\s+)?(?:to|in|into|en|vers|mu|kuri|hadi)\s+(?P<b>[a-zà-ÿ' .-]+?)(?:\s+time)?\s*[?!.]*$", re.I)


def time_answer(q: str, lang: str, now=None):
    from zoneinfo import ZoneInfo
    T = _T[lang]
    now = now or datetime.now(timezone.utc)
    mc = _CONVT.match(q.strip())
    if mc:
        pa, pb = find_place(mc.group("a")), find_place(mc.group("b"))
        if pa and pb:
            h = int(mc.group("h")); mi = int(mc.group("m") or 0); ap = (mc.group("ap") or "").lower()
            if ap == "pm" and h < 12:
                h += 12
            if ap == "am" and h == 12:
                h = 0
            if h > 23 or mi > 59:
                return None
            za, zb = ZoneInfo(_tz_for(pa)), ZoneInfo(_tz_for(pb))
            t0 = datetime(now.year, now.month, now.day, h, mi, tzinfo=za)
            t1 = t0.astimezone(zb)
            day = "" if t1.date() == t0.date() else (" " + (T["next_day"] if t1.date() > t0.date() else T["prev_day"]))
            return f"**{t0:%H:%M}** {_label(pa)} ({_off(t0)}) = **{t1:%H:%M}**{day} {_label(pb)} ({_off(t1)})"
    m = _TIMEQ.match(q.strip()) or _TIMEQ2.match(q.strip())
    if not m:
        return None
    pl = find_place(m.group("p"))
    if not pl:
        return None
    tz = ZoneInfo(_tz_for(pl))
    t = now.astimezone(tz)
    kg = now.astimezone(ZoneInfo("Africa/Kigali"))
    dh = (t.utcoffset() - kg.utcoffset()).total_seconds() / 3600
    diff = "" if dh == 0 else " " + T["vs_kigali"].format(h=_fmt(abs(dh)), w=T["ahead"] if dh > 0 else T["behind"])
    return f"**{t:%H:%M}** · {t:%A %d %B %Y} · {_label(pl)} ({_off(t)}, {tz.key}){diff}"


def _off(t):
    s = t.utcoffset().total_seconds() / 3600
    return "UTC" + ("+" if s >= 0 else "-") + (f"{int(abs(s))}" if abs(s) % 1 == 0 else f"{abs(s):.2f}".rstrip("0"))


_FACTQ = re.compile(r"^\W*(?:what(?:'s| is| are)\s+)?(?:the\s+)?(?P<what>capital|currency|money|calling code|dialing code|dialling code|phone code|country code|international code|languages?|time ?zone|continent|official language)\s+(?:city\s+)?(?:of|in|for)\s+(?P<p>.+?)\s*[?!.]*$"
                    r"|^\W*(?:quelle? est|quel est|quelle est)\s+(?:la |le |l')?(?P<what2>capitale|monnaie|devise|indicatif(?: telephonique)?|langues?|fuseau horaire|continent)\s+(?:de la |du |de l'|de |d')\s*(?P<p2>.+?)\s*[?!.]*$"
                    r"|^\W*(?:umurwa mukuru|ifaranga|amafaranga|kode yo guhamagara|indimi|ikiganiro|umugabane)\s+(?:w'|wa|y'|ya|z'|za|bya|bw')\s*(?P<p3>.+?)(?:\s+ni\s+(?:iyihe|uwuhe|iki|izihe))?\s*[?!.]*$"
                    r"|^\W*(?:mji mkuu|sarafu|msimbo wa simu|lugha|saa za eneo|bara)\s+(?:la|ya|za|wa)\s*(?P<p4>.+?)(?:\s+ni\s+(?:nini|ipi|zipi|upi))?\s*[?!.]*$", re.I)
_ABOUTQ = re.compile(r"^\W*(?:tell me about|facts about|information (?:about|on)|info (?:on|about)|about|parle[- ]moi (?:de la |du |de l'|de |d')|informations? sur|dis[- ]moi (?:tout )?sur|mbwira ibya|menyesha amakuru ya|niambie kuhusu|habari za|taarifa za)\s+(?P<p>.+?)\s*[?!.]*$", re.I)
_WHICH = re.compile(r"^\W*(?:which|what)\s+country\s+(?:has|uses|is the capital|owns)\s+(?:the\s+)?(?P<w>.+?)\s*[?!.]*$|^\W*(?:quel pays (?:a|utilise)\s+(?:la |le |l')?(?P<w2>.+?))\s*[?!.]*$", re.I)


def _kind_of_fact(w: str) -> str:
    w = fold(w)
    for k, keys in (("capital", ("capital", "capitale", "umurwa mukuru", "mji mkuu")), ("currency", ("currency", "money", "monnaie", "devise", "ifaranga", "amafaranga", "sarafu")),
                    ("call", ("calling", "dialing", "dialling", "phone code", "country code", "international code", "indicatif", "kode yo guhamagara", "msimbo wa simu")), ("lang", ("language", "langue", "indimi", "lugha")),
                    ("tz", ("time zone", "timezone", "fuseau", "saa za eneo")), ("cont", ("continent", "umugabane", "bara"))):
        if any(x in w for x in keys):
            return k
    return "capital"


def country_answer(q: str, lang: str):
    T = _T[lang]
    qs = q.strip()
    m = _FACTQ.match(qs)
    if m:
        what = m.group("what") or m.group("what2") or qs.split()[0]
        p = m.group("p") or m.group("p2") or m.group("p3") or m.group("p4")
        pl = find_place(p)
        if pl and pl[0] == "country":
            c = pl[1]
            k = _kind_of_fact(what)
            nm = c["fr"] if lang == "fr" else c["en"]
            if k == "capital":
                return T["f_capital"].format(c=nm, v=c["capital"])
            if k == "currency":
                return T["f_currency"].format(c=nm, v=f"{CUR.get(c['cur'], (c['cur'],))[0]} ({c['cur']})")
            if k == "call":
                return T["f_call"].format(c=nm, v="+" + c["call"])
            if k == "lang":
                return T["f_lang"].format(c=nm, v=c["langs"])
            if k == "tz":
                from zoneinfo import ZoneInfo
                t = datetime.now(timezone.utc).astimezone(ZoneInfo(c["tz"]))
                return T["f_tz"].format(c=nm, v=f"{c['tz']} ({_off(t)})")
            return T["f_cont"].format(c=nm, v=c["cont"])
    m = _ABOUTQ.match(qs)
    if m:
        pl = find_place(m.group("p"))
        if pl and pl[0] == "country":
            c = pl[1]
            nm = c["fr"] if lang == "fr" else c["en"]
            from zoneinfo import ZoneInfo
            t = datetime.now(timezone.utc).astimezone(ZoneInfo(c["tz"]))
            return "\n".join([f"**{nm}**", f"- {T['l_capital']}: {c['capital']}", f"- {T['l_currency']}: {CUR.get(c['cur'], (c['cur'],))[0]} ({c['cur']})", f"- {T['l_call']}: +{c['call']}",
                              f"- {T['l_lang']}: {c['langs']}", f"- {T['l_cont']}: {c['cont']}", f"- {T['l_tz']}: {c['tz']} ({_off(t)})", f"- {T['l_now']}: {t:%H:%M}"])
    m = _WHICH.match(qs)
    if m:
        w = fold(m.group("w") or m.group("w2"))
        code = currency_code(w)
        if code:
            cs = [c for c in WD.COUNTRIES if c["cur"] == code]
            if cs:
                return T["which_cur"].format(v=f"{CUR.get(code, (code,))[0]} ({code})", cs=", ".join(c["fr"] if lang == "fr" else c["en"] for c in cs[:25]) + (" …" if len(cs) > 25 else ""))
    return None


_DISTQ = re.compile(r"^\W*(?:what(?:'s| is) the |how far is it |how far (?:is|are) )?(?:distance|how far)\s+(?:between|from)\s+(?P<a>.+?)\s+(?:and|to)\s+(?P<b>.+?)\s*[?!.]*$"
                    r"|^\W*(?:quelle est la )?distance (?:entre|de)\s+(?P<a2>.+?)\s+(?:et|a|à)\s+(?P<b2>.+?)\s*[?!.]*$"
                    r"|^\W*(?:intera|urugendo|ni intera ingahe|intera y'ahantu)\s+(?:hagati ya|kuva)\s+(?P<a3>.+?)\s+(?:na|kugeza)\s+(?P<b3>.+?)\s*[?!.]*$"
                    r"|^\W*(?:umbali|ni umbali gani)\s+(?:kati ya|kutoka)\s+(?P<a4>.+?)\s+(?:na|hadi|mpaka)\s+(?P<b4>.+?)\s*[?!.]*$", re.I)


def distance_answer(q: str, lang: str):
    m = _DISTQ.match(q.strip())
    if not m:
        return None
    g = m.groupdict()
    a = g["a"] or g["a2"] or g["a3"] or g["a4"]
    b = g["b"] or g["b2"] or g["b3"] or g["b4"]
    pa, pb = find_place(a), find_place(b)
    if not pa or not pb:
        return None
    km = haversine(_coords(pa), _coords(pb))
    T = _T[lang]
    hours = km / 850 + 0.5
    h, mn = int(hours), int(round((hours - int(hours)) * 60))
    nm = lambda p: (p[1]["capital"] if p[0] == "country" else p[1][0])          # noqa: E731
    la = f"{_label(pa)} ({nm(pa)})" if pa[0] == "country" else _label(pa)
    lb = f"{_label(pb)} ({nm(pb)})" if pb[0] == "country" else _label(pb)
    return T["dist"].format(a=la, b=lb, km=f"{km:,.0f}", mi=f"{km / 1.609344:,.0f}", fh=f"{h} h {mn:02d} min")


_ISO_DATE = r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})"
_DAYS = re.compile(rf"^\W*(?:how many days (?:are there )?(?:between|from)|days (?:between|from)|combien de jours (?:entre|depuis|de)|iminsi (?:hagati ya|kuva)|siku (?:kati ya|kutoka))\s+{_ISO_DATE}\s+(?:and|to|et|a|à|na|hadi|kugeza)\s+{_ISO_DATE}\s*[?!.]*$", re.I)
_DAYSTO = re.compile(rf"^\W*(?:how many days (?:until|till|to|before)|days (?:until|till|to)|combien de jours (?:avant|jusqu'au|jusqu'à)|iminsi isigaye kugeza|siku zilizobaki hadi)\s+{_ISO_DATE}\s*[?!.]*$", re.I)
_WEEKDAY = re.compile(rf"^\W*(?:what day (?:of the week )?is|which day is|quel jour (?:est|était|etait)|ni uwuhe munsi|ni siku gani)\s+(?:the\s+|le\s+|on\s+)?{_ISO_DATE}\s*[?!.]*$", re.I)
_ADD = re.compile(rf"^\W*(?:what(?:'s| is) the date|date)\s+(?P<n>\d+)\s+(?P<u>days?|weeks?|months?)\s+(?P<dir>from now|after|from today|ago|before)\s*[?!.]*$|^\W*(?:dans|il y a)\s+(?P<n2>\d+)\s+(?P<u2>jours?|semaines?|mois)\s*[?!.]*$", re.I)


def _d(s):
    s = s.strip()
    if "/" in s:
        dd, mm, yy = s.split("/")
        return date(int(yy), int(mm), int(dd))
    return date.fromisoformat(s)


def date_answer(q: str, lang: str, today=None):
    T = _T[lang]
    today = today or datetime.now(timezone(timedelta(hours=2))).date()
    try:
        m = _DAYS.match(q.strip())
        if m:
            a, b = _d(m.group(1)), _d(m.group(2))
            n = abs((b - a).days)
            return T["days_between"].format(a=a.isoformat(), b=b.isoformat(), n=f"{n:,}", w=f"{n // 7} {T['weeks']} {n % 7} {T['days']}")
        m = _DAYSTO.match(q.strip())
        if m:
            d = _d(m.group(1)); n = (d - today).days
            return T["days_to"].format(d=d.isoformat(), n=f"{abs(n):,}") if n >= 0 else T["days_since"].format(d=d.isoformat(), n=f"{abs(n):,}")
        m = _WEEKDAY.match(q.strip())
        if m:
            d = _d(m.group(1))
            return T["weekday"].format(d=d.isoformat(), w=T["wd"][d.weekday()])
        m = _ADD.match(q.strip())
        if m:
            n = int(m.group("n") or m.group("n2")); u = fold(m.group("u") or m.group("u2"))
            days = n * (7 if u.startswith(("week", "semaine")) else 30 if u.startswith(("month", "mois")) else 1)
            back = bool(m.group("dir") and m.group("dir").lower() in ("ago", "before")) or ("il y a" in q.lower())
            d = today - timedelta(days=days) if back else today + timedelta(days=days)
            return T["date_is"].format(d=d.isoformat(), w=T["wd"][d.weekday()])
    except (ValueError, OverflowError):
        return None
    return None


# ------------------------------------------------------------------ translations of the fixed texts
_T = {
    "en": dict(rates_live="Live rates from {src}{upd_}.", rates_off="No live exchange-rate service answered, so this uses an approximate offline table. Check your bank or an official source before any real transaction.", rates_note="Market rates differ from bank and mobile-money rates (they add fees and a margin).",
               cur_unknown="I do not have an exchange rate for {c}.", next_day="(next day)", prev_day="(previous day)", vs_kigali="{h} h {w} Kigali", ahead="ahead of", behind="behind",
               f_capital="The capital of **{c}** is **{v}**.", f_currency="The currency of **{c}** is the **{v}**.", f_call="The international calling code of **{c}** is **{v}**.", f_lang="Main languages of **{c}**: {v}.", f_tz="Main time zone of **{c}**: {v}.", f_cont="**{c}** is in **{v}**.",
               l_capital="Capital", l_currency="Currency", l_call="Calling code", l_lang="Languages", l_cont="Continent", l_tz="Time zone", l_now="Local time now", which_cur="Countries using the {v}: {cs}.",
               dist="The straight-line (great-circle) distance between **{a}** and **{b}** is about **{km} km** ({mi} miles). A flight would take roughly {fh} (estimate; real routes and times differ).",
               days_between="Between **{a}** and **{b}** there are **{n} days** ({w}).", days_to="There are **{n} days** until **{d}**.", days_since="**{d}** was **{n} days** ago.", weekday="**{d}** is a **{w}**.", date_is="That date is **{d}** ({w}).", weeks="weeks", days="days",
               wd=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], title="World tools"),
    "fr": dict(rates_live="Taux en direct de {src}{upd_}.", rates_off="Aucun service de taux de change en direct n'a répondu : j'utilise une table approximative hors ligne. Vérifiez auprès de votre banque ou d'une source officielle avant toute opération réelle.", rates_note="Les taux du marché diffèrent de ceux des banques et du mobile money (frais et marge en plus).",
               cur_unknown="Je n'ai pas de taux de change pour {c}.", next_day="(jour suivant)", prev_day="(jour précédent)", vs_kigali="{h} h {w} Kigali", ahead="d'avance sur", behind="de retard sur",
               f_capital="La capitale de **{c}** est **{v}**.", f_currency="La monnaie de **{c}** est le/la **{v}**.", f_call="L'indicatif téléphonique international de **{c}** est **{v}**.", f_lang="Langues principales de **{c}** : {v}.", f_tz="Fuseau horaire principal de **{c}** : {v}.", f_cont="**{c}** est en **{v}**.",
               l_capital="Capitale", l_currency="Monnaie", l_call="Indicatif", l_lang="Langues", l_cont="Continent", l_tz="Fuseau horaire", l_now="Heure locale", which_cur="Pays qui utilisent la monnaie {v} : {cs}.",
               dist="La distance à vol d'oiseau (orthodromique) entre **{a}** et **{b}** est d'environ **{km} km** ({mi} miles). Un vol durerait environ {fh} (estimation ; les routes et durées réelles varient).",
               days_between="Entre le **{a}** et le **{b}**, il y a **{n} jours** ({w}).", days_to="Il reste **{n} jours** avant le **{d}**.", days_since="Le **{d}** était il y a **{n} jours**.", weekday="Le **{d}** est un **{w}**.", date_is="Cette date est le **{d}** ({w}).", weeks="semaines", days="jours",
               wd=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"], title="Outils du monde"),
    "rw": dict(rates_live="Igiciro cy'ivunjisha kiri ako kanya kiva kuri {src}{upd_}.", rates_off="Nta serivisi y'igiciro cy'ivunjisha ikora ubu yabonetse, bityo nakoresheje imbonerahamwe y'ibigereranyo. Genzura muri banki cyangwa ahantu hemewe mbere yo gukora igikorwa nyacyo.", rates_note="Igiciro cy'isoko gitandukanye n'icya banki n'icya mobile money (hiyongeraho amafaranga y'inyongera).",
               cur_unknown="Nta giciro cy'ivunjisha mfite cya {c}.", next_day="(umunsi ukurikira)", prev_day="(umunsi ubanziriza)", vs_kigali="amasaha {h} {w} Kigali", ahead="imbere ya", behind="inyuma ya",
               f_capital="Umurwa mukuru wa **{c}** ni **{v}**.", f_currency="Ifaranga rya **{c}** ni **{v}**.", f_call="Kode mpuzamahanga yo guhamagara ya **{c}** ni **{v}**.", f_lang="Indimi nkuru za **{c}**: {v}.", f_tz="Isaha nkuru ya **{c}**: {v}.", f_cont="**{c}** iri muri **{v}**.",
               l_capital="Umurwa mukuru", l_currency="Ifaranga", l_call="Kode yo guhamagara", l_lang="Indimi", l_cont="Umugabane", l_tz="Isaha", l_now="Igihe cyaho ubu", which_cur="Ibihugu bikoresha {v}: {cs}.",
               dist="Intera y'igicuro (mu murongo ugororotse) hagati ya **{a}** na **{b}** ni nka **{km} km** ({mi} miles). Indege yatwara nka {fh} (ni ikigereranyo; inzira n'igihe nyacyo biratandukana).",
               days_between="Hagati ya **{a}** na **{b}** hari **iminsi {n}** ({w}).", days_to="Hasigaye **iminsi {n}** kugeza ku wa **{d}**.", days_since="**{d}** hashize **iminsi {n}**.", weekday="**{d}** ni **{w}**.", date_is="Iyo tariki ni **{d}** ({w}).", weeks="ibyumweru", days="iminsi",
               wd=["kuwa mbere", "kuwa kabiri", "kuwa gatatu", "kuwa kane", "kuwa gatanu", "kuwa gatandatu", "ku cyumweru"], title="Ibikoresho by'isi"),
    "sw": dict(rates_live="Viwango vya moja kwa moja kutoka {src}{upd_}.", rates_off="Hakuna huduma ya viwango vya kubadilisha fedha iliyojibu, kwa hiyo nimetumia jedwali la makadirio. Hakiki na benki yako au chanzo rasmi kabla ya muamala halisi.", rates_note="Viwango vya soko ni tofauti na vya benki na pesa za simu (zinaongeza ada na faida).",
               cur_unknown="Sina kiwango cha kubadilisha cha {c}.", next_day="(siku inayofuata)", prev_day="(siku iliyopita)", vs_kigali="saa {h} {w} Kigali", ahead="mbele ya", behind="nyuma ya",
               f_capital="Mji mkuu wa **{c}** ni **{v}**.", f_currency="Sarafu ya **{c}** ni **{v}**.", f_call="Msimbo wa kimataifa wa simu wa **{c}** ni **{v}**.", f_lang="Lugha kuu za **{c}**: {v}.", f_tz="Saa kuu ya **{c}**: {v}.", f_cont="**{c}** iko **{v}**.",
               l_capital="Mji mkuu", l_currency="Sarafu", l_call="Msimbo wa simu", l_lang="Lugha", l_cont="Bara", l_tz="Eneo la saa", l_now="Saa ya huko sasa", which_cur="Nchi zinazotumia {v}: {cs}.",
               dist="Umbali wa mstari ulionyooka kati ya **{a}** na **{b}** ni takriban **{km} km** (maili {mi}). Ndege ingechukua takriban {fh} (makadirio; njia na muda halisi hutofautiana).",
               days_between="Kati ya **{a}** na **{b}** kuna **siku {n}** ({w}).", days_to="Zimebaki **siku {n}** hadi **{d}**.", days_since="**{d}** ilikuwa **siku {n}** zilizopita.", weekday="**{d}** ni **{w}**.", date_is="Tarehe hiyo ni **{d}** ({w}).", weeks="wiki", days="siku",
               wd=["Jumatatu", "Jumanne", "Jumatano", "Alhamisi", "Ijumaa", "Jumamosi", "Jumapili"], title="Zana za dunia"),
}


_REORD = re.compile(rf"^\W*(?:(?:{_VERB})\W+)*(?P<frm>[^\d]+?)\s+(?P<amt>-?{_NUM})\s+(?P<rest>.*)$", re.I)
_LEAD = re.compile(r"^(?:ni\s+)?(?:angahe|ngahe|kangahe|ngapi|nini|sawa na|kiasi gani|shilingi ngapi|pesa ngapi)?\s*", re.I)


def _reorder(q: str):
    """'amadolari 100 ni angahe mu mafaranga y'u Rwanda' / 'badilisha dola 100 kuwa shilingi za kenya' -> '100 amadolari mu mafaranga ...' (currency or unit written before the number)."""
    m = _REORD.match(q.strip())
    if not m:
        return None
    frm = m.group("frm").strip()
    if not (currency_code(frm) or _unit(frm)):
        return None
    rest = _LEAD.sub("", m.group("rest").strip())
    return f"{m.group('amt')} {frm} {_PREPW[lang_hint()]} {rest}" if not re.match(r"^(?:to|into|in|en|vers|mu|muri|kuri|kwa|kuwa|hadi|ndani ya|a|à)\b", rest, re.I) else f"{m.group('amt')} {frm} {rest}"


_PREPW = {"en": "to", "fr": "en", "rw": "mu", "sw": "kuwa"}
_LANG = ["en"]


def lang_hint():
    return _LANG[0]


def answer(question: str, lang: str = "en", fetch=None, now=None, today=None):
    """Markdown answer for a world-toolkit request, or None. Never raises."""
    q = (question or "").strip()
    if not q or len(q) > 220 or "\n" in q:
        return None
    lang = lang if lang in _T else "en"
    _LANG[0] = lang
    try:
        alt = _reorder(q)
        variants = ([alt] if alt else []) + [q]
        for q in variants:
          for fn in (lambda: time_answer(q, lang, now), lambda: distance_answer(q, lang), lambda: date_answer(q, lang, today), lambda: country_answer(q, lang), lambda: unit_answer(q, lang), lambda: currency_answer(q, lang, fetch)):
            r = fn()
            if r:
                return r
    except Exception:      # noqa: BLE001
        return None
    return None
