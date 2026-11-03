"""Reference data about the countries of the world: names (English, French), capital, currency, calling code, main time zone, capital coordinates, main languages, continent.
Facts that rarely change; the app presents them as reference information (check an official source for legal or financial decisions)."""
from __future__ import annotations

_RAW = """
AF|Afghanistan|Afghanistan|Kabul|AFN|93|Asia/Kabul|34.53|69.17|Dari, Pashto|Asia
AL|Albania|Albanie|Tirana|ALL|355|Europe/Tirane|41.33|19.82|Albanian|Europe
DZ|Algeria|Algérie|Algiers|DZD|213|Africa/Algiers|36.75|3.06|Arabic, Tamazight|Africa
AD|Andorra|Andorre|Andorra la Vella|EUR|376|Europe/Andorra|42.51|1.52|Catalan|Europe
AO|Angola|Angola|Luanda|AOA|244|Africa/Luanda|-8.84|13.23|Portuguese|Africa
AG|Antigua and Barbuda|Antigua-et-Barbuda|St. John's|XCD|1|America/Antigua|17.12|-61.85|English|North America
AR|Argentina|Argentine|Buenos Aires|ARS|54|America/Argentina/Buenos_Aires|-34.60|-58.38|Spanish|South America
AM|Armenia|Arménie|Yerevan|AMD|374|Asia/Yerevan|40.18|44.51|Armenian|Asia
AU|Australia|Australie|Canberra|AUD|61|Australia/Sydney|-35.28|149.13|English|Oceania
AT|Austria|Autriche|Vienna|EUR|43|Europe/Vienna|48.21|16.37|German|Europe
AZ|Azerbaijan|Azerbaïdjan|Baku|AZN|994|Asia/Baku|40.41|49.87|Azerbaijani|Asia
BS|Bahamas|Bahamas|Nassau|BSD|1|America/Nassau|25.05|-77.35|English|North America
BH|Bahrain|Bahreïn|Manama|BHD|973|Asia/Bahrain|26.23|50.59|Arabic|Asia
BD|Bangladesh|Bangladesh|Dhaka|BDT|880|Asia/Dhaka|23.81|90.41|Bengali|Asia
BB|Barbados|Barbade|Bridgetown|BBD|1|America/Barbados|13.10|-59.61|English|North America
BY|Belarus|Biélorussie|Minsk|BYN|375|Europe/Minsk|53.90|27.57|Belarusian, Russian|Europe
BE|Belgium|Belgique|Brussels|EUR|32|Europe/Brussels|50.85|4.35|Dutch, French, German|Europe
BZ|Belize|Belize|Belmopan|BZD|501|America/Belize|17.25|-88.77|English|North America
BJ|Benin|Bénin|Porto-Novo|XOF|229|Africa/Porto-Novo|6.50|2.63|French|Africa
BT|Bhutan|Bhoutan|Thimphu|BTN|975|Asia/Thimphu|27.47|89.64|Dzongkha|Asia
BO|Bolivia|Bolivie|Sucre|BOB|591|America/La_Paz|-19.03|-65.26|Spanish, Quechua, Aymara|South America
BA|Bosnia and Herzegovina|Bosnie-Herzégovine|Sarajevo|BAM|387|Europe/Sarajevo|43.86|18.41|Bosnian, Croatian, Serbian|Europe
BW|Botswana|Botswana|Gaborone|BWP|267|Africa/Gaborone|-24.65|25.91|English, Setswana|Africa
BR|Brazil|Brésil|Brasília|BRL|55|America/Sao_Paulo|-15.79|-47.88|Portuguese|South America
BN|Brunei|Brunéi|Bandar Seri Begawan|BND|673|Asia/Brunei|4.89|114.94|Malay|Asia
BG|Bulgaria|Bulgarie|Sofia|BGN|359|Europe/Sofia|42.70|23.32|Bulgarian|Europe
BF|Burkina Faso|Burkina Faso|Ouagadougou|XOF|226|Africa/Ouagadougou|12.37|-1.52|French|Africa
BI|Burundi|Burundi|Gitega|BIF|257|Africa/Bujumbura|-3.43|29.92|Kirundi, French, English|Africa
CV|Cape Verde|Cap-Vert|Praia|CVE|238|Atlantic/Cape_Verde|14.93|-23.51|Portuguese|Africa
KH|Cambodia|Cambodge|Phnom Penh|KHR|855|Asia/Phnom_Penh|11.56|104.92|Khmer|Asia
CM|Cameroon|Cameroun|Yaoundé|XAF|237|Africa/Douala|3.85|11.50|French, English|Africa
CA|Canada|Canada|Ottawa|CAD|1|America/Toronto|45.42|-75.70|English, French|North America
CF|Central African Republic|République centrafricaine|Bangui|XAF|236|Africa/Bangui|4.36|18.56|French, Sango|Africa
TD|Chad|Tchad|N'Djamena|XAF|235|Africa/Ndjamena|12.13|15.06|French, Arabic|Africa
CL|Chile|Chili|Santiago|CLP|56|America/Santiago|-33.45|-70.67|Spanish|South America
CN|China|Chine|Beijing|CNY|86|Asia/Shanghai|39.90|116.41|Mandarin Chinese|Asia
CO|Colombia|Colombie|Bogotá|COP|57|America/Bogota|4.71|-74.07|Spanish|South America
KM|Comoros|Comores|Moroni|KMF|269|Indian/Comoro|-11.70|43.26|Comorian, Arabic, French|Africa
CG|Republic of the Congo|Congo-Brazzaville|Brazzaville|XAF|242|Africa/Brazzaville|-4.27|15.28|French|Africa
CD|DR Congo|RD Congo|Kinshasa|CDF|243|Africa/Kinshasa|-4.44|15.27|French|Africa
CR|Costa Rica|Costa Rica|San José|CRC|506|America/Costa_Rica|9.93|-84.08|Spanish|North America
CI|Ivory Coast|Côte d'Ivoire|Yamoussoukro|XOF|225|Africa/Abidjan|6.82|-5.28|French|Africa
HR|Croatia|Croatie|Zagreb|EUR|385|Europe/Zagreb|45.81|15.98|Croatian|Europe
CU|Cuba|Cuba|Havana|CUP|53|America/Havana|23.11|-82.37|Spanish|North America
CY|Cyprus|Chypre|Nicosia|EUR|357|Asia/Nicosia|35.19|33.38|Greek, Turkish|Europe
CZ|Czech Republic|Tchéquie|Prague|CZK|420|Europe/Prague|50.08|14.44|Czech|Europe
DK|Denmark|Danemark|Copenhagen|DKK|45|Europe/Copenhagen|55.68|12.57|Danish|Europe
DJ|Djibouti|Djibouti|Djibouti|DJF|253|Africa/Djibouti|11.59|43.15|French, Arabic|Africa
DM|Dominica|Dominique|Roseau|XCD|1|America/Dominica|15.30|-61.39|English|North America
DO|Dominican Republic|République dominicaine|Santo Domingo|DOP|1|America/Santo_Domingo|18.49|-69.93|Spanish|North America
EC|Ecuador|Équateur|Quito|USD|593|America/Guayaquil|-0.18|-78.47|Spanish|South America
EG|Egypt|Égypte|Cairo|EGP|20|Africa/Cairo|30.04|31.24|Arabic|Africa
SV|El Salvador|Salvador|San Salvador|USD|503|America/El_Salvador|13.69|-89.22|Spanish|North America
GQ|Equatorial Guinea|Guinée équatoriale|Malabo|XAF|240|Africa/Malabo|3.75|8.78|Spanish, French, Portuguese|Africa
ER|Eritrea|Érythrée|Asmara|ERN|291|Africa/Asmara|15.32|38.93|Tigrinya, Arabic, English|Africa
EE|Estonia|Estonie|Tallinn|EUR|372|Europe/Tallinn|59.44|24.75|Estonian|Europe
SZ|Eswatini|Eswatini|Mbabane|SZL|268|Africa/Mbabane|-26.32|31.14|Swati, English|Africa
ET|Ethiopia|Éthiopie|Addis Ababa|ETB|251|Africa/Addis_Ababa|9.03|38.74|Amharic|Africa
FJ|Fiji|Fidji|Suva|FJD|679|Pacific/Fiji|-18.14|178.44|English, Fijian, Hindi|Oceania
FI|Finland|Finlande|Helsinki|EUR|358|Europe/Helsinki|60.17|24.94|Finnish, Swedish|Europe
FR|France|France|Paris|EUR|33|Europe/Paris|48.86|2.35|French|Europe
GA|Gabon|Gabon|Libreville|XAF|241|Africa/Libreville|0.42|9.47|French|Africa
GM|Gambia|Gambie|Banjul|GMD|220|Africa/Banjul|13.45|-16.58|English|Africa
GE|Georgia|Géorgie|Tbilisi|GEL|995|Asia/Tbilisi|41.72|44.79|Georgian|Asia
DE|Germany|Allemagne|Berlin|EUR|49|Europe/Berlin|52.52|13.40|German|Europe
GH|Ghana|Ghana|Accra|GHS|233|Africa/Accra|5.60|-0.19|English|Africa
GR|Greece|Grèce|Athens|EUR|30|Europe/Athens|37.98|23.73|Greek|Europe
GD|Grenada|Grenade|St. George's|XCD|1|America/Grenada|12.05|-61.75|English|North America
GT|Guatemala|Guatemala|Guatemala City|GTQ|502|America/Guatemala|14.63|-90.51|Spanish|North America
GN|Guinea|Guinée|Conakry|GNF|224|Africa/Conakry|9.64|-13.58|French|Africa
GW|Guinea-Bissau|Guinée-Bissau|Bissau|XOF|245|Africa/Bissau|11.86|-15.60|Portuguese|Africa
GY|Guyana|Guyana|Georgetown|GYD|592|America/Guyana|6.80|-58.16|English|South America
HT|Haiti|Haïti|Port-au-Prince|HTG|509|America/Port-au-Prince|18.59|-72.31|French, Haitian Creole|North America
HN|Honduras|Honduras|Tegucigalpa|HNL|504|America/Tegucigalpa|14.07|-87.19|Spanish|North America
HU|Hungary|Hongrie|Budapest|HUF|36|Europe/Budapest|47.50|19.04|Hungarian|Europe
IS|Iceland|Islande|Reykjavik|ISK|354|Atlantic/Reykjavik|64.15|-21.94|Icelandic|Europe
IN|India|Inde|New Delhi|INR|91|Asia/Kolkata|28.61|77.21|Hindi, English|Asia
ID|Indonesia|Indonésie|Jakarta|IDR|62|Asia/Jakarta|-6.21|106.85|Indonesian|Asia
IR|Iran|Iran|Tehran|IRR|98|Asia/Tehran|35.69|51.39|Persian|Asia
IQ|Iraq|Irak|Baghdad|IQD|964|Asia/Baghdad|33.31|44.37|Arabic, Kurdish|Asia
IE|Ireland|Irlande|Dublin|EUR|353|Europe/Dublin|53.35|-6.26|Irish, English|Europe
IL|Israel|Israël|Jerusalem|ILS|972|Asia/Jerusalem|31.77|35.22|Hebrew, Arabic|Asia
IT|Italy|Italie|Rome|EUR|39|Europe/Rome|41.90|12.50|Italian|Europe
JM|Jamaica|Jamaïque|Kingston|JMD|1|America/Jamaica|17.97|-76.79|English|North America
JP|Japan|Japon|Tokyo|JPY|81|Asia/Tokyo|35.68|139.69|Japanese|Asia
JO|Jordan|Jordanie|Amman|JOD|962|Asia/Amman|31.95|35.93|Arabic|Asia
KZ|Kazakhstan|Kazakhstan|Astana|KZT|7|Asia/Almaty|51.17|71.43|Kazakh, Russian|Asia
KE|Kenya|Kenya|Nairobi|KES|254|Africa/Nairobi|-1.29|36.82|Swahili, English|Africa
KI|Kiribati|Kiribati|Tarawa|AUD|686|Pacific/Tarawa|1.45|173.03|English, Gilbertese|Oceania
KW|Kuwait|Koweït|Kuwait City|KWD|965|Asia/Kuwait|29.38|47.99|Arabic|Asia
KG|Kyrgyzstan|Kirghizistan|Bishkek|KGS|996|Asia/Bishkek|42.87|74.59|Kyrgyz, Russian|Asia
LA|Laos|Laos|Vientiane|LAK|856|Asia/Vientiane|17.97|102.60|Lao|Asia
LV|Latvia|Lettonie|Riga|EUR|371|Europe/Riga|56.95|24.11|Latvian|Europe
LB|Lebanon|Liban|Beirut|LBP|961|Asia/Beirut|33.89|35.50|Arabic|Asia
LS|Lesotho|Lesotho|Maseru|LSL|266|Africa/Maseru|-29.31|27.48|Sesotho, English|Africa
LR|Liberia|Libéria|Monrovia|LRD|231|Africa/Monrovia|6.30|-10.80|English|Africa
LY|Libya|Libye|Tripoli|LYD|218|Africa/Tripoli|32.89|13.19|Arabic|Africa
LI|Liechtenstein|Liechtenstein|Vaduz|CHF|423|Europe/Vaduz|47.14|9.52|German|Europe
LT|Lithuania|Lituanie|Vilnius|EUR|370|Europe/Vilnius|54.69|25.28|Lithuanian|Europe
LU|Luxembourg|Luxembourg|Luxembourg|EUR|352|Europe/Luxembourg|49.61|6.13|Luxembourgish, French, German|Europe
MG|Madagascar|Madagascar|Antananarivo|MGA|261|Indian/Antananarivo|-18.88|47.51|Malagasy, French|Africa
MW|Malawi|Malawi|Lilongwe|MWK|265|Africa/Blantyre|-13.96|33.77|English, Chichewa|Africa
MY|Malaysia|Malaisie|Kuala Lumpur|MYR|60|Asia/Kuala_Lumpur|3.14|101.69|Malay|Asia
MV|Maldives|Maldives|Malé|MVR|960|Indian/Maldives|4.18|73.51|Dhivehi|Asia
ML|Mali|Mali|Bamako|XOF|223|Africa/Bamako|12.64|-8.00|French|Africa
MT|Malta|Malte|Valletta|EUR|356|Europe/Malta|35.90|14.51|Maltese, English|Europe
MH|Marshall Islands|Îles Marshall|Majuro|USD|692|Pacific/Majuro|7.09|171.38|Marshallese, English|Oceania
MR|Mauritania|Mauritanie|Nouakchott|MRU|222|Africa/Nouakchott|18.08|-15.98|Arabic|Africa
MU|Mauritius|Maurice|Port Louis|MUR|230|Indian/Mauritius|-20.16|57.50|English, French|Africa
MX|Mexico|Mexique|Mexico City|MXN|52|America/Mexico_City|19.43|-99.13|Spanish|North America
FM|Micronesia|Micronésie|Palikir|USD|691|Pacific/Pohnpei|6.92|158.16|English|Oceania
MD|Moldova|Moldavie|Chișinău|MDL|373|Europe/Chisinau|47.01|28.86|Romanian|Europe
MC|Monaco|Monaco|Monaco|EUR|377|Europe/Monaco|43.74|7.42|French|Europe
MN|Mongolia|Mongolie|Ulaanbaatar|MNT|976|Asia/Ulaanbaatar|47.89|106.91|Mongolian|Asia
ME|Montenegro|Monténégro|Podgorica|EUR|382|Europe/Podgorica|42.44|19.26|Montenegrin|Europe
MA|Morocco|Maroc|Rabat|MAD|212|Africa/Casablanca|34.02|-6.84|Arabic, Tamazight|Africa
MZ|Mozambique|Mozambique|Maputo|MZN|258|Africa/Maputo|-25.97|32.57|Portuguese|Africa
MM|Myanmar|Birmanie|Naypyidaw|MMK|95|Asia/Yangon|19.76|96.08|Burmese|Asia
NA|Namibia|Namibie|Windhoek|NAD|264|Africa/Windhoek|-22.56|17.08|English|Africa
NR|Nauru|Nauru|Yaren|AUD|674|Pacific/Nauru|-0.55|166.92|Nauruan, English|Oceania
NP|Nepal|Népal|Kathmandu|NPR|977|Asia/Kathmandu|27.72|85.32|Nepali|Asia
NL|Netherlands|Pays-Bas|Amsterdam|EUR|31|Europe/Amsterdam|52.37|4.90|Dutch|Europe
NZ|New Zealand|Nouvelle-Zélande|Wellington|NZD|64|Pacific/Auckland|-41.29|174.78|English, Māori|Oceania
NI|Nicaragua|Nicaragua|Managua|NIO|505|America/Managua|12.11|-86.24|Spanish|North America
NE|Niger|Niger|Niamey|XOF|227|Africa/Niamey|13.51|2.11|French|Africa
NG|Nigeria|Nigeria|Abuja|NGN|234|Africa/Lagos|9.08|7.40|English|Africa
KP|North Korea|Corée du Nord|Pyongyang|KPW|850|Asia/Pyongyang|39.04|125.76|Korean|Asia
MK|North Macedonia|Macédoine du Nord|Skopje|MKD|389|Europe/Skopje|41.99|21.43|Macedonian|Europe
NO|Norway|Norvège|Oslo|NOK|47|Europe/Oslo|59.91|10.75|Norwegian|Europe
OM|Oman|Oman|Muscat|OMR|968|Asia/Muscat|23.59|58.41|Arabic|Asia
PK|Pakistan|Pakistan|Islamabad|PKR|92|Asia/Karachi|33.68|73.05|Urdu, English|Asia
PW|Palau|Palaos|Ngerulmud|USD|680|Pacific/Palau|7.50|134.62|Palauan, English|Oceania
PS|Palestine|Palestine|Ramallah|ILS|970|Asia/Gaza|31.90|35.20|Arabic|Asia
PA|Panama|Panama|Panama City|PAB|507|America/Panama|8.98|-79.52|Spanish|North America
PG|Papua New Guinea|Papouasie-Nouvelle-Guinée|Port Moresby|PGK|675|Pacific/Port_Moresby|-9.44|147.18|English, Tok Pisin|Oceania
PY|Paraguay|Paraguay|Asunción|PYG|595|America/Asuncion|-25.26|-57.58|Spanish, Guarani|South America
PE|Peru|Pérou|Lima|PEN|51|America/Lima|-12.05|-77.04|Spanish|South America
PH|Philippines|Philippines|Manila|PHP|63|Asia/Manila|14.60|120.98|Filipino, English|Asia
PL|Poland|Pologne|Warsaw|PLN|48|Europe/Warsaw|52.23|21.01|Polish|Europe
PT|Portugal|Portugal|Lisbon|EUR|351|Europe/Lisbon|38.72|-9.14|Portuguese|Europe
QA|Qatar|Qatar|Doha|QAR|974|Asia/Qatar|25.29|51.53|Arabic|Asia
RO|Romania|Roumanie|Bucharest|RON|40|Europe/Bucharest|44.43|26.10|Romanian|Europe
RU|Russia|Russie|Moscow|RUB|7|Europe/Moscow|55.76|37.62|Russian|Europe
RW|Rwanda|Rwanda|Kigali|RWF|250|Africa/Kigali|-1.94|30.06|Kinyarwanda, French, English, Swahili|Africa
KN|Saint Kitts and Nevis|Saint-Christophe-et-Niévès|Basseterre|XCD|1|America/St_Kitts|17.30|-62.72|English|North America
LC|Saint Lucia|Sainte-Lucie|Castries|XCD|1|America/St_Lucia|14.01|-60.99|English|North America
VC|Saint Vincent and the Grenadines|Saint-Vincent-et-les-Grenadines|Kingstown|XCD|1|America/St_Vincent|13.16|-61.22|English|North America
WS|Samoa|Samoa|Apia|WST|685|Pacific/Apia|-13.83|-171.76|Samoan, English|Oceania
SM|San Marino|Saint-Marin|San Marino|EUR|378|Europe/San_Marino|43.94|12.45|Italian|Europe
ST|São Tomé and Príncipe|Sao Tomé-et-Principe|São Tomé|STN|239|Africa/Sao_Tome|0.34|6.73|Portuguese|Africa
SA|Saudi Arabia|Arabie saoudite|Riyadh|SAR|966|Asia/Riyadh|24.71|46.68|Arabic|Asia
SN|Senegal|Sénégal|Dakar|XOF|221|Africa/Dakar|14.72|-17.47|French|Africa
RS|Serbia|Serbie|Belgrade|RSD|381|Europe/Belgrade|44.79|20.45|Serbian|Europe
SC|Seychelles|Seychelles|Victoria|SCR|248|Indian/Mahe|-4.62|55.45|Seychellois Creole, English, French|Africa
SL|Sierra Leone|Sierra Leone|Freetown|SLE|232|Africa/Freetown|8.48|-13.23|English|Africa
SG|Singapore|Singapour|Singapore|SGD|65|Asia/Singapore|1.35|103.82|English, Malay, Mandarin, Tamil|Asia
SK|Slovakia|Slovaquie|Bratislava|EUR|421|Europe/Bratislava|48.15|17.11|Slovak|Europe
SI|Slovenia|Slovénie|Ljubljana|EUR|386|Europe/Ljubljana|46.06|14.51|Slovene|Europe
SB|Solomon Islands|Îles Salomon|Honiara|SBD|677|Pacific/Guadalcanal|-9.43|159.95|English|Oceania
SO|Somalia|Somalie|Mogadishu|SOS|252|Africa/Mogadishu|2.05|45.32|Somali, Arabic|Africa
ZA|South Africa|Afrique du Sud|Pretoria|ZAR|27|Africa/Johannesburg|-25.75|28.19|Zulu, Xhosa, Afrikaans, English (11 official)|Africa
KR|South Korea|Corée du Sud|Seoul|KRW|82|Asia/Seoul|37.57|126.98|Korean|Asia
SS|South Sudan|Soudan du Sud|Juba|SSP|211|Africa/Juba|4.85|31.58|English|Africa
ES|Spain|Espagne|Madrid|EUR|34|Europe/Madrid|40.42|-3.70|Spanish|Europe
LK|Sri Lanka|Sri Lanka|Sri Jayawardenepura Kotte|LKR|94|Asia/Colombo|6.93|79.86|Sinhala, Tamil|Asia
SD|Sudan|Soudan|Khartoum|SDG|249|Africa/Khartoum|15.50|32.56|Arabic, English|Africa
SR|Suriname|Suriname|Paramaribo|SRD|597|America/Paramaribo|5.85|-55.20|Dutch|South America
SE|Sweden|Suède|Stockholm|SEK|46|Europe/Stockholm|59.33|18.07|Swedish|Europe
CH|Switzerland|Suisse|Bern|CHF|41|Europe/Zurich|46.95|7.45|German, French, Italian, Romansh|Europe
SY|Syria|Syrie|Damascus|SYP|963|Asia/Damascus|33.51|36.28|Arabic|Asia
TW|Taiwan|Taïwan|Taipei|TWD|886|Asia/Taipei|25.03|121.57|Mandarin Chinese|Asia
TJ|Tajikistan|Tadjikistan|Dushanbe|TJS|992|Asia/Dushanbe|38.56|68.77|Tajik|Asia
TZ|Tanzania|Tanzanie|Dodoma|TZS|255|Africa/Dar_es_Salaam|-6.16|35.75|Swahili, English|Africa
TH|Thailand|Thaïlande|Bangkok|THB|66|Asia/Bangkok|13.76|100.50|Thai|Asia
TL|Timor-Leste|Timor oriental|Dili|USD|670|Asia/Dili|-8.56|125.57|Tetum, Portuguese|Asia
TG|Togo|Togo|Lomé|XOF|228|Africa/Lome|6.13|1.22|French|Africa
TO|Tonga|Tonga|Nukuʻalofa|TOP|676|Pacific/Tongatapu|-21.14|-175.20|Tongan, English|Oceania
TT|Trinidad and Tobago|Trinité-et-Tobago|Port of Spain|TTD|1|America/Port_of_Spain|10.66|-61.51|English|North America
TN|Tunisia|Tunisie|Tunis|TND|216|Africa/Tunis|36.81|10.18|Arabic|Africa
TR|Turkey|Turquie|Ankara|TRY|90|Europe/Istanbul|39.93|32.86|Turkish|Asia
TM|Turkmenistan|Turkménistan|Ashgabat|TMT|993|Asia/Ashgabat|37.96|58.33|Turkmen|Asia
TV|Tuvalu|Tuvalu|Funafuti|AUD|688|Pacific/Funafuti|-8.52|179.20|Tuvaluan, English|Oceania
UG|Uganda|Ouganda|Kampala|UGX|256|Africa/Kampala|0.35|32.58|English, Swahili|Africa
UA|Ukraine|Ukraine|Kyiv|UAH|380|Europe/Kyiv|50.45|30.52|Ukrainian|Europe
AE|United Arab Emirates|Émirats arabes unis|Abu Dhabi|AED|971|Asia/Dubai|24.45|54.38|Arabic|Asia
GB|United Kingdom|Royaume-Uni|London|GBP|44|Europe/London|51.51|-0.13|English|Europe
US|United States|États-Unis|Washington, D.C.|USD|1|America/New_York|38.91|-77.04|English|North America
UY|Uruguay|Uruguay|Montevideo|UYU|598|America/Montevideo|-34.90|-56.19|Spanish|South America
UZ|Uzbekistan|Ouzbékistan|Tashkent|UZS|998|Asia/Tashkent|41.30|69.24|Uzbek|Asia
VU|Vanuatu|Vanuatu|Port Vila|VUV|678|Pacific/Efate|-17.73|168.32|Bislama, English, French|Oceania
VA|Vatican City|Vatican|Vatican City|EUR|379|Europe/Vatican|41.90|12.45|Italian, Latin|Europe
VE|Venezuela|Venezuela|Caracas|VES|58|America/Caracas|10.48|-66.90|Spanish|South America
VN|Vietnam|Viêt Nam|Hanoi|VND|84|Asia/Ho_Chi_Minh|21.03|105.85|Vietnamese|Asia
YE|Yemen|Yémen|Sana'a|YER|967|Asia/Aden|15.37|44.19|Arabic|Asia
ZM|Zambia|Zambie|Lusaka|ZMW|260|Africa/Lusaka|-15.39|28.32|English|Africa
ZW|Zimbabwe|Zimbabwe|Harare|USD|263|Africa/Harare|-17.83|31.05|English, Shona, Ndebele|Africa
"""

COUNTRIES = []
for _ln in _RAW.strip().splitlines():
    f = _ln.split("|")
    COUNTRIES.append(dict(iso=f[0], en=f[1], fr=f[2], capital=f[3], cur=f[4], call=f[5], tz=f[6], lat=float(f[7]), lon=float(f[8]), langs=f[9], cont=f[10]))
BY_ISO = {c["iso"]: c for c in COUNTRIES}

# names people type in Kinyarwanda, Kiswahili, French and English slang -> ISO (folded keys, see world_tools.fold)
ALIASES = {
    "u rwanda": "RW", "urwanda": "RW", "uburundi": "BI", "u burundi": "BI", "ubugande": "UG", "uganda": "UG", "kenya": "KE", "tanzaniya": "TZ", "tanzania": "TZ", "kongo": "CD", "drc": "CD", "dr congo": "CD", "congo kinshasa": "CD", "congo brazzaville": "CG",
    "amerika": "US", "leta zunze ubumwe z amerika": "US", "usa": "US", "u s a": "US", "us": "US", "america": "US", "united states of america": "US", "etats unis": "US", "etats-unis": "US", "marekani": "US", "states": "US", "ubwongereza": "GB", "uk": "GB", "u k": "GB", "england": "GB", "britain": "GB", "great britain": "GB", "angleterre": "GB", "uingereza": "GB",
    "ubufaransa": "FR", "ufaransa": "FR", "ubudage": "DE", "ujerumani": "DE", "allemagne": "DE", "germany": "DE", "ubushinwa": "CN", "uchina": "CN", "china": "CN", "ubuyapani": "JP", "japani": "JP", "ubuhinde": "IN", "uhindi": "IN", "ubutaliyani": "IT", "italia": "IT", "ubuhorandi": "NL", "uholanzi": "NL", "holland": "NL",
    "afurika y epfo": "ZA", "afrika kusini": "ZA", "afrique du sud": "ZA", "south africa": "ZA", "misiri": "EG", "misiri ": "EG", "egypte": "EG", "ubusuwisi": "CH", "uswisi": "CH", "ububiligi": "BE", "ubelgiji": "BE", "ubuhispaniya": "ES", "uhispania": "ES", "ubuportigali": "PT", "ureno": "PT", "ubwami bw abarabu": "AE", "uarabuni": "AE", "dubai": "AE", "emirats": "AE",
    "arabiya sawudite": "SA", "saudia": "SA", "uturuki": "TR", "turukiya": "TR", "ubuyobozi bw uburusiya": "RU", "uburusiya": "RU", "urusi": "RU", "canada": "CA", "kanada": "CA", "ostralie": "AU", "australia": "AU", "ostraliya": "AU", "burezili": "BR", "brazil": "BR", "brasil": "BR", "ubuhinde ": "IN",
    "ivory coast": "CI", "cote d ivoire": "CI", "cote divoire": "CI", "korea": "KR", "south korea": "KR", "north korea": "KP", "czechia": "CZ", "swaziland": "SZ", "burma": "MM", "cape verde": "CV", "cabo verde": "CV", "timor leste": "TL", "east timor": "TL", "palestine": "PS", "vatican": "VA", "holy see": "VA",
}

# well-known cities that are not capitals: name -> (lat, lon, ISO, IANA time zone) for distances and local times
CITIES = {
    "new york": (40.71, -74.01, "US", "America/New_York"), "los angeles": (34.05, -118.24, "US", "America/Los_Angeles"), "chicago": (41.88, -87.63, "US", "America/Chicago"), "san francisco": (37.77, -122.42, "US", "America/Los_Angeles"),
    "houston": (29.76, -95.37, "US", "America/Chicago"), "miami": (25.76, -80.19, "US", "America/New_York"), "toronto": (43.65, -79.38, "CA", "America/Toronto"), "vancouver": (49.28, -123.12, "CA", "America/Vancouver"),
    "sao paulo": (-23.55, -46.63, "BR", "America/Sao_Paulo"), "rio de janeiro": (-22.91, -43.17, "BR", "America/Sao_Paulo"), "istanbul": (41.01, 28.98, "TR", "Europe/Istanbul"), "dubai": (25.20, 55.27, "AE", "Asia/Dubai"),
    "mumbai": (19.08, 72.88, "IN", "Asia/Kolkata"), "bangalore": (12.97, 77.59, "IN", "Asia/Kolkata"), "shanghai": (31.23, 121.47, "CN", "Asia/Shanghai"), "hong kong": (22.32, 114.17, "HK", "Asia/Hong_Kong"),
    "osaka": (34.69, 135.50, "JP", "Asia/Tokyo"), "sydney": (-33.87, 151.21, "AU", "Australia/Sydney"), "melbourne": (-37.81, 144.96, "AU", "Australia/Melbourne"), "perth": (-31.95, 115.86, "AU", "Australia/Perth"),
    "lagos": (6.52, 3.38, "NG", "Africa/Lagos"), "johannesburg": (-26.20, 28.05, "ZA", "Africa/Johannesburg"), "cape town": (-33.92, 18.42, "ZA", "Africa/Johannesburg"), "mombasa": (-4.04, 39.67, "KE", "Africa/Nairobi"),
    "dar es salaam": (-6.79, 39.21, "TZ", "Africa/Dar_es_Salaam"), "goma": (-1.68, 29.22, "CD", "Africa/Lubumbashi"), "bukavu": (-2.50, 28.86, "CD", "Africa/Lubumbashi"), "bujumbura": (-3.38, 29.36, "BI", "Africa/Bujumbura"),
    "butare": (-2.60, 29.74, "RW", "Africa/Kigali"), "huye": (-2.60, 29.74, "RW", "Africa/Kigali"), "musanze": (-1.50, 29.63, "RW", "Africa/Kigali"), "rubavu": (-1.68, 29.26, "RW", "Africa/Kigali"), "gisenyi": (-1.70, 29.26, "RW", "Africa/Kigali"),
    "mumbai ": (19.08, 72.88, "IN", "Asia/Kolkata"), "karachi": (24.86, 67.01, "PK", "Asia/Karachi"), "casablanca": (33.57, -7.59, "MA", "Africa/Casablanca"), "barcelona": (41.39, 2.17, "ES", "Europe/Madrid"), "milan": (45.46, 9.19, "IT", "Europe/Rome"),
    "munich": (48.14, 11.58, "DE", "Europe/Berlin"), "geneva": (46.20, 6.14, "CH", "Europe/Zurich"), "frankfurt": (50.11, 8.68, "DE", "Europe/Berlin"), "saint petersburg": (59.93, 30.34, "RU", "Europe/Moscow"), "guangzhou": (23.13, 113.26, "CN", "Asia/Shanghai"),
}
