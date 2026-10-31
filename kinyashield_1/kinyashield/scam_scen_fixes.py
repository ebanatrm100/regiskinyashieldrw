"""Cue widenings for situations in scam_scen_1/2 found too strict when tested on realistic messages in four languages (tests/scam_corpus.py)."""
from scam_scen_core import widen

widen("investment_guaranteed", 1, r"\b\w*izewe\b|\bnta mpungenge\b|\bhakuna hatari\b|\bsans risque\b|\bzero risk\b|\bbila hatari\b|\bbila shaka\b")
widen("investment_guaranteed", 2, r"\b(?:gagn\w+|benefice\w*|win|earn|receive|get \d+|ubone|upate|pata|inyungu|faida)\b")
widen("loan_app_threat", 1, r"\b(?:overdue|repay\w*|owe\w*|debt|due|late|arrears|ideni|deni|retard|impaye|ukopo|inguzanyo|mkopo)\b")
widen("loan_app_threat", 2, r"\b(?:all your contacts|your (?:contacts|family|friends|employer|boss)|tes contacts|vos contacts|abantu muziranye|marafiki zako)\b")
widen("deposit_before_viewing", 1, r"\b(?:avansi|avance|amana|arrhes|akiba|kodi ya kwanza)\b|\bsend (?:a |the )?deposit\b")
widen("fake_utility_token", 2, r"\b(?:buy|purchase|achetez|acheter|gura|agura|kugura|nunua|kununua)\w*")
widen("overpayment", 0, r"\b(?:goods|payment|paid|sent|marchandise|bidhaa|malipo|amafaranga)\b")
widen("overpayment", 1, r"\b(?:instead of|more than|extra|too much|plus que|byinshi|zaidi)\b")
