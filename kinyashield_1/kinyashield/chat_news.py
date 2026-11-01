"""Cyber news inside the AI Assistant chat: "tell me cybercrimes that happened this week" gets real, dated, sourced results (same engine as the Cyber News tab),
and a question with no time asks which period (with choices). Pure Python; the network part is cyber_intel.search, which fails soft."""
from __future__ import annotations
import cyber_intel as ci
import cyber_upcoming as cu
import cyber_explain as cx

_ASK = {
    "en": ("Which period do you want? Reply with one of these (or type your own, like “last 2 months”):", "Past", "Upcoming", "You can also open the Cyber News tab for buttons, more results and explanations."),
    "fr": ("Quelle période voulez-vous ? Répondez avec l'une de ces options (ou écrivez la vôtre, par exemple « les 2 derniers mois ») :", "Passé", "À venir", "Vous pouvez aussi ouvrir l'onglet Actualité cyber pour des boutons, plus de résultats et des explications."),
    "rw": ("Ushaka igihe kingana iki? Subiza uhitemo kimwe muri ibi (cyangwa wandike icyawe, urugero «amezi 2 ashize»):", "Ibyashize", "Ibigiye kuza", "Ushobora no gufungura igice cya Amakuru ya Cyber kubona amabuto, ibisubizo byinshi n'ibisobanuro."),
    "sw": ("Unataka kipindi gani? Jibu kwa moja ya hizi (au andika chako, mfano «miezi 2 iliyopita»):", "Zilizopita", "Zijazo", "Unaweza pia kufungua kichupo cha Habari za Cyber kwa vitufe, matokeo zaidi na maelezo."),
}
_HEAD = {"en": "Cyber information", "fr": "Informations cyber", "rw": "Amakuru ya cyber", "sw": "Taarifa za cyber"}
_NONE = {"en": "I found nothing from the trusted sources for this period (or they could not be reached just now). Try a longer period, or open the Cyber News tab.",
         "fr": "Je n'ai rien trouvé dans les sources fiables pour cette période (ou elles sont injoignables en ce moment). Essayez une période plus longue ou ouvrez l'onglet Actualité cyber.",
         "rw": "Nta kintu nabonye mu masoko yizewe muri iki gihe (cyangwa ntiyabonetse ubu). Gerageza igihe kirekire cyangwa ufungure igice cya Amakuru ya Cyber.",
         "sw": "Sikupata kitu kutoka vyanzo vya kuaminika kwa kipindi hiki (au havikufikika sasa). Jaribu kipindi kirefu au fungua kichupo cha Habari za Cyber."}
_NOTE = {"en": "Headlines come from the publishers linked; they are not independently verified by KinyaShield. Open each link for the facts.",
         "fr": "Les titres viennent des éditeurs liés ; KinyaShield ne les a pas vérifiés indépendamment. Ouvrez chaque lien pour les faits.",
         "rw": "Imitwe iva ku batangaza bahujwe; KinyaShield ntiyabigenzuye ukwayo. Fungura buri murongo urebe ukuri.",
         "sw": "Vichwa vinatoka kwa wachapishaji walioungwa; KinyaShield haikuvihakiki kivyake. Fungua kila kiungo kupata ukweli."}
_TOPIC = {"en": {"security": "Cybersecurity", "awareness": "Awareness", "crime": "Cybercrime"}, "fr": {"security": "Cybersécurité", "awareness": "Sensibilisation", "crime": "Cybercriminalité"},
          "rw": {"security": "Umutekano wa interineti", "awareness": "Ubukangurambaga", "crime": "Ibyaha byo kuri interineti"}, "sw": {"security": "Usalama wa mtandao", "awareness": "Uhamasishaji", "crime": "Uhalifu wa mtandaoni"}}


def ask_period(lang: str = "en") -> str:
    lang = lang if lang in _ASK else "en"
    a, past, up, tail = _ASK[lang]
    L = ci.LABELS[lang]
    past_keys = ("today", "yesterday", "this_week", "last_week", "this_month", "last_month", "last_3_months", "this_year", "last_year")
    return (f"{a}\n\n**{past}:** " + " · ".join(L[k] for k in past_keys) + f"\n\n**{up}:** " + " · ".join(cu.LABELS[lang][k] for k in cu.KEYS[:5]) + f"\n\n_{tail}_")


def answer(period: dict, topics, text: str, lang: str = "en", fetch_jobs=None) -> str:
    """Markdown answer: dated results for the period, a plain-language summary and the sources. Never raises."""
    lang = lang if lang in _HEAD else "en"
    topics = [t for t in (topics or ci.TOPICS) if t in ci.TOPICS] or list(ci.TOPICS)
    try:
        if period.get("future"):
            res = cu.search(period, topics, lang)
            label = cu.label(period, lang)
        else:
            res = ci.search(period, topics, lang, text, fetch_jobs=fetch_jobs)
            label = ci.label(period, lang)
    except Exception:
        return _NONE[lang]
    allitems = [it for t in res["topics"] for it in (res["items"].get(t) or [])]
    head = f"**{_HEAD[lang]} · {label}** ({period['start']} → {period['end']})"
    if not allitems:
        return head + "\n\n" + _NONE[lang]
    out = [head, "", cx.digest(allitems, lang), ""]
    for t in res["topics"]:
        items = (res["items"].get(t) or [])[:6]
        if not items:
            continue
        out.append(f"**{_TOPIC[lang][t]}**")
        for it in items:
            title = it["title"].replace("[", "(").replace("]", ")")
            link = f"[{title}]({it['url']})" if it.get("url") else title
            out.append(f"- {link} — {it['source']} · {it['date']}")
        out.append("")
    out.append(f"_{_NOTE[lang]} {_ASK[lang][3]}_")
    return "\n".join(out)
