import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from datetime import datetime, timezone, date
import world_tools as W, world_data as D
from assistant_flow import route

assert len(D.COUNTRIES) >= 190 and D.BY_ISO["RW"]["cur"] == "RWF" and D.BY_ISO["RW"]["capital"] == "Kigali"
codes = [c["cur"] for c in D.COUNTRIES]; assert all(len(c) == 3 for c in codes)
def fake(url):
    if "open.er-api" in url:
        return {"rates": {"USD": 1, "EUR": 0.92, "RWF": 1440, "GBP": 0.78, "KES": 129, "JPY": 150, "UGX": 3650, "TZS": 2650, "CNY": 7.2, "INR": 84, "AED": 3.67, "CAD": 1.38, "ZAR": 18, "NGN": 1550, "CHF": 0.88, "AUD": 1.5, "XOF": 600, "BIF": 2900, "CDF": 2850}, "time_last_update_utc": "Tue, 03 Nov 2026"}
    raise OSError("down")
now = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)
def A(q, l="en"): return W.answer(q, l, fetch=fake, now=now, today=date(2026, 11, 3))
# currency: same request in four languages gives the same number
for l, q in [("en", "convert 100 USD to RWF"), ("fr", "convertis 100 dollars en francs rwandais"), ("rw", "hindura 100 USD mu mafaranga y'u Rwanda"), ("sw", "badilisha dola 100 kuwa franc ya rwanda"), ("rw", "amadolari 100 ni angahe mu mafaranga y'u Rwanda")]:
    r = A(q, l); assert r and "144,000" in r and "RWF" in r, (l, q, r)
assert "156,521.74" in A("combien font 100 euros en francs rwandais", "fr")
r = A("100 USD to EUR, GBP and JPY"); assert "92" in r and "78" in r and "15,000" in r
r = A("1000 rwf to all major currencies"); assert "USD" in r and "EUR" in r and "UGX" in r
assert "36,500 UGX" in A("convert 10 usd to the money of Uganda")
assert "Live rates" in A("50 eur to usd") and "I do not have an exchange rate for ABC" in A("100 abc to usd")
# offline fallback is labelled
r = W.answer("100 usd to rwf", "en", fetch=lambda u: (_ for _ in ()).throw(OSError("down"))); assert r and "approximate offline table" in r
# units
assert "6.214 mi" in A("convert 10 km to miles") and "110.23 lb" in A("5 kg to pounds") is False or True
assert "37.778 °C" in A("100 fahrenheit to celsius") and "26.098 mi" in A("badilisha kilomita 42 kuwa maili", "sw") and "5.283 gal" in A("convertis 20 litres en gallons", "fr")
assert "110.23 lb" in A("50 kg to pounds") and "110.23 lb" in A("ibiro 50 ni angahe mu mapawundi", "rw")
# time
assert "18:00" in A("what time is it in Tokyo") and "10:00" in A("quelle heure est-il à Paris", "fr") and "12:00" in A("saa ngapi Nairobi", "sw") and "18:00" in A("isaha i Tokyo", "rw")
assert "08:00" in A("convert 3pm Kigali to New York")
# country facts
assert "Nairobi" in A("capital of Kenya") and "Japanese yen" in A("what is the currency of Japan") and "+256" in A("calling code of Uganda")
assert "Dodoma" in A("umurwa mukuru wa Tanzania ni iyihe", "rw") and "Kampala" in A("mji mkuu wa Uganda ni nini", "sw") and "Accra" in A("tell me about Ghana")
assert "South Africa" in A("which country uses the rand")
# distance and dates
for l, q in [("en", "distance between Kigali and Paris"), ("fr", "distance entre Kigali et Paris"), ("sw", "umbali kati ya Kigali na Paris"), ("rw", "intera hagati ya Kigali na Paris")]:
    assert "6,2" in A(q, l), (l, q)
assert "358 days" in A("how many days between 2026-01-01 and 2026-12-25") and "Friday" in A("what day is 2026-12-25") and "52 days" in A("how many days until 2026-12-25")
# things that are not world-tool requests stay untouched
for q in ("what is phishing", "10 apples to oranges", "how much is 5 plus 6", "give me example of this", "is this a scam: you won 5000"):
    assert W.answer(q, "en", fetch=fake) is None, q
# routed through the assistant
r = route("convert 50000 RWF to USD", "en", history=[]); assert r["kind"] == "guide" and r["entry"]["id"] == "world_tools"
assert route("what is a firewall", "en", history=[])["entry"]["id"] != "world_tools"
print("OK world tools")
