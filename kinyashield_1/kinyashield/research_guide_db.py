"""How an AI assistant understands a question, researches and composes an answer: four-language explainers built from the owner's
"AI Assistant Question Answering and Research Guide" (interpreting, external research, RAG, tool calls, composing, safety, mistakes, the
current-question example, what is not publicly knowable, glossary, reading). Pure Python, offline. Describes public methods only; never
claims private details of any deployed assistant. fr/rw/sw wording is a DRAFT for review by fluent speakers."""
from __future__ import annotations
from textutil import fold, has_phrase, entry, LANGS
from ai_guide_db import BOUNDARY

_RAW = []


def _add(id_, kw, kwc, title, answer, steps=None, label=None, related=None, boundary=False):
    st = {l: list(steps[i]) if steps else [] for i, l in enumerate(LANGS)}
    ans = dict(zip(LANGS, answer))
    if boundary:
        ans = {l: ans[l] + "\n\n_" + BOUNDARY[l] + "_" for l in LANGS}
    e = entry(id_, "ai_guide", dict(zip(LANGS, title)), ans, st, dict(zip(LANGS, label)) if label else None, related)
    _RAW.append((e, [fold(x) for x in kw.split("|") if x], [fold(x) for x in kwc.split("|") if x]))


_add("qa_interpret",
     "how does an ai understand a question|how does ai interpret a question|how does ai understand my question|how is a question interpreted|how does an ai know what i mean|"
     "comment l'ia comprend une question|comment l'ia interprete une question|comment une ia comprend ma question|"
     "ai yumva ikibazo ite|ai isobanukirwa ikibazo ite|ai ifata ikibazo ite|"
     "ai inaelewaje swali|ai hufasiri swali vipi|ai inaelewa vipi swali langu", "",
     ("How a question is interpreted (5 steps)", "Comment une question est interprétée (5 étapes)", "Uko ikibazo gisobanurwa (intambwe 5)", "Jinsi swali linavyofasiriwa (hatua 5)"),
     ("Before answering, a good assistant works out **what you really need**. Try `interpret: your question` and I will show the task type, constraints and any ambiguity.",
      "Avant de répondre, un bon assistant cherche **ce dont vous avez vraiment besoin**. Essayez `interpret: votre question` : je montre le type de tâche, les contraintes et l'ambiguïté éventuelle.",
      "Mbere yo gusubiza, umufasha mwiza amenya **ibyo ukeneye by'ukuri**. Gerageza `interpret: ikibazo cyawe` nkwereke ubwoko bw'umurimo, imbogamizi n'ibitumvikana.",
      "Kabla ya kujibu, msaidizi mzuri hubaini **unachohitaji kweli**. Jaribu `interpret: swali lako` nikuonyeshe aina ya kazi, vikwazo na utata."),
     (["**Identify the task:** factual question, explanation, translation, code, calculation, advice, creative work or action.",
       "**Extract constraints:** requested format, language, audience, length, deadlines, budget and explicit rules.",
       "**Use relevant context:** earlier messages or supplied files can clarify what a short follow-up means.",
       "**Resolve ambiguity:** infer a reasonable meaning when it is safe, or ask a clarifying question when a missing detail would materially change the answer.",
       "**Select a response strategy:** answer directly, reason step by step, search, inspect a file, calculate, or combine methods."],
      ["**Identifier la tâche :** question factuelle, explication, traduction, code, calcul, conseil, création ou action.",
       "**Extraire les contraintes :** format demandé, langue, public, longueur, délais, budget et règles explicites.",
       "**Utiliser le contexte utile :** les messages précédents ou fichiers fournis éclairent ce que veut dire une relance courte.",
       "**Lever l'ambiguïté :** déduire un sens raisonnable quand c'est sûr, ou poser une question quand un détail manquant changerait vraiment la réponse.",
       "**Choisir une stratégie :** répondre directement, raisonner par étapes, chercher, lire un fichier, calculer, ou combiner."],
      ["**Menya umurimo:** ikibazo cy'ukuri, ibisobanuro, ubuhinduzi, code, kubara, inama, guhanga cyangwa igikorwa.",
       "**Kuramo imbogamizi:** imiterere isabwa, ururimi, abo bigenewe, uburebure, igihe ntarengwa, ingengo y'imari n'amategeko asobanutse.",
       "**Koresha amakuru akwiye:** ubutumwa bwabanje cyangwa dosiye zatanzwe bisobanura ikibazo kigufi gikurikira.",
       "**Gukemura ibitumvikana:** gufata ubusobanuro bukwiye iyo bidateje ikibazo, cyangwa kubaza iyo ikibura cyahindura igisubizo cyane.",
       "**Guhitamo uburyo:** gusubiza ako kanya, gutekereza intambwe ku yindi, gushakisha, gusoma dosiye, kubara, cyangwa guhuza."],
      ["**Tambua kazi:** swali la ukweli, maelezo, tafsiri, msimbo, hesabu, ushauri, ubunifu au kitendo.",
       "**Toa vikwazo:** umbizo lililoombwa, lugha, hadhira, urefu, tarehe za mwisho, bajeti na sheria wazi.",
       "**Tumia muktadha husika:** ujumbe wa awali au faili zilizotolewa hufafanua swali fupi la kufuatilia.",
       "**Tatua utata:** kisia maana ya busara ikiwa ni salama, au uliza swali la ufafanuzi pale undani unaokosekana ungebadilisha jibu.",
       "**Chagua mkakati:** jibu moja kwa moja, fikiri hatua kwa hatua, tafuta, kagua faili, kokotoa, au changanya mbinu."]),
     ("The five steps", "Les cinq étapes", "Intambwe eshanu", "Hatua tano"), ["ai_question_path", "qa_compose"])

_add("qa_research",
     "how does ai research|how does ai search the web|how does an ai assistant research|how does ai do research|external research|how does web search work for ai|how does ai find current information|can ai browse the internet|"
     "comment l'ia fait des recherches|comment l'ia cherche sur le web|recherche externe ia|l'ia peut-elle naviguer sur internet|"
     "ai ikora ubushakashatsi ite|ai ishakisha kuri internet ite|ubushakashatsi bwa ai|"
     "ai hufanya utafiti vipi|ai hutafuta mtandaoni vipi|utafiti wa nje wa ai", "",
     ("How external research works (7 steps)", "Comment fonctionne la recherche externe (7 étapes)", "Uko ubushakashatsi bwo hanze bukora (intambwe 7)", "Jinsi utafiti wa nje unavyofanya kazi (hatua 7)"),
     ("A model's learned knowledge is **not** live web access. Without a search or retrieval tool it cannot check a current website. When a search tool is available, a research workflow can add fresh evidence. Try `research plan: your question`.\n\n**A search result is not automatically true:** pages can be outdated, irrelevant, misleading or inaccessible, so verification remains necessary.",
      "Les connaissances apprises d'un modèle ne sont **pas** un accès web en direct. Sans outil de recherche, il ne peut pas vérifier un site actuel. Avec un outil de recherche, un flux de recherche peut apporter des preuves récentes. Essayez `research plan: votre question`.\n\n**Un résultat de recherche n'est pas automatiquement vrai :** les pages peuvent être périmées, hors sujet, trompeuses ou inaccessibles ; la vérification reste nécessaire.",
      "Ubumenyi bwize n'icyitegererezo **si** uburyo bwo kugera kuri internet mu gihe nyacyo. Nta gikoresho cyo gushakisha, ntigishobora kugenzura urubuga rwa none. Iyo gihari, ubushakashatsi bushobora kongeramo ibimenyetso bishya. Gerageza `research plan: ikibazo cyawe`.\n\n**Igisubizo cyo gushakisha si ukuri ako kanya:** impapuro zishobora kuba zishaje, zidafite aho zihuriye, zishuka cyangwa zidashobora gufungurwa, bityo kugenzura biracyakenewe.",
      "Maarifa yaliyojifunzwa ya modeli **si** ufikiaji wa moja kwa moja wa mtandao. Bila zana ya utafutaji, haiwezi kukagua tovuti ya sasa. Zana ya utafutaji ikipatikana, mtiririko wa utafiti unaweza kuongeza ushahidi mpya. Jaribu `research plan: swali lako`.\n\n**Matokeo ya utafutaji si kweli moja kwa moja:** kurasa zinaweza kuwa za zamani, zisizohusika, za kupotosha au zisizofikika, kwa hivyo uthibitishaji bado unahitajika."),
     (["**Turn the question into focused search queries.**",
       "**Retrieve relevant results** and open the useful pages.",
       "**Prefer authoritative, primary and recent sources** where freshness matters.",
       "**Check that the source really supports the claim:** inspect dates, scope and limitations.",
       "**Compare sources** when important facts conflict or one result is not enough.",
       "**Write the summary in original wording** and cite sources next to the claims they support.",
       "**State uncertainty** when evidence is missing, conflicting, outdated or region-specific."],
      ["**Transformer la question en requêtes de recherche ciblées.**",
       "**Récupérer les résultats pertinents** et ouvrir les pages utiles.",
       "**Préférer des sources faisant autorité, primaires et récentes** quand la fraîcheur compte.",
       "**Vérifier que la source soutient vraiment l'affirmation :** regarder dates, portée et limites.",
       "**Comparer les sources** quand des faits importants se contredisent ou qu'un seul résultat ne suffit pas.",
       "**Rédiger le résumé avec ses propres mots** et citer les sources à côté des affirmations qu'elles soutiennent.",
       "**Dire l'incertitude** quand les preuves manquent, se contredisent, sont dépassées ou propres à une région."],
      ["**Guhindura ikibazo mu bibazo byo gushakisha bisobanutse.**",
       "**Kuvana ibisubizo bikwiye** ugafungura impapuro zifasha.",
       "**Guhitamo inkomoko yizewe, y'ibanze kandi nshya** aho igihe gifite akamaro.",
       "**Kugenzura ko inkomoko ishyigikira koko ibivugwa:** reba amatariki, ubwo bugari n'imbibi.",
       "**Kugereranya inkomoko** iyo amakuru y'ingenzi ahabanye cyangwa igisubizo kimwe kidahagije.",
       "**Kwandika incamake mu magambo yawe** ugatanga inkomoko iruhande rw'ibyo zishyigikira.",
       "**Kuvuga ukutizera** iyo ibimenyetso bibura, bihabanye, bishaje cyangwa bireba akarere kamwe."],
      ["**Geuza swali kuwa maswali ya utafutaji yaliyolengwa.**",
       "**Pata matokeo husika** na ufungue kurasa muhimu.",
       "**Pendelea vyanzo vyenye mamlaka, vya msingi na vipya** ambapo upya ni muhimu.",
       "**Hakiki kama chanzo kinaunga mkono dai kweli:** angalia tarehe, wigo na mipaka.",
       "**Linganisha vyanzo** pale ukweli muhimu unapogongana au tokeo moja halitoshi.",
       "**Andika muhtasari kwa maneno yako** na taja vyanzo karibu na madai vinavyounga mkono.",
       "**Eleza kutokuwa na uhakika** ushahidi ukikosekana, ukigongana, ukiwa wa zamani au wa eneo fulani."]),
     ("The seven steps", "Les sept étapes", "Intambwe zirindwi", "Hatua saba"), ["qa_rag", "qa_example"], boundary=True)

_add("qa_rag",
     "what is rag|what is retrieval augmented generation|what is retrieval-augmented generation|how does rag work|explain rag|retrieval augmented generation|rag in ai|how does an ai answer from documents|vector search|vector database|semantic search|"
     "qu'est-ce que le rag|generation augmentee par la recherche|generation augmentee par recuperation|comment fonctionne le rag|recherche vectorielle|recherche semantique|"
     "rag ni iki|rag ikora ite|gushakisha mu buryo bw'ubusobanuro|"
     "rag ni nini|rag inafanyaje kazi|utafutaji wa vekta|utafutaji wa maana", "",
     ("Retrieval-Augmented Generation, RAG (6 steps)", "Génération augmentée par récupération, RAG (6 étapes)", "Retrieval-Augmented Generation, RAG (intambwe 6)", "Retrieval-Augmented Generation, RAG (hatua 6)"),
     ("RAG combines **retrieval** with **generation**, so an assistant can answer from documents, knowledge bases or current sources. Try `rag demo: your question ||| passage one ||| passage two ||| passage three` to see a tiny version run.\n\n**RAG improves access to relevant information but does not guarantee correctness:** retrieval can return the wrong passages, and a model can still misread correct evidence.",
      "Le RAG combine la **récupération** et la **génération** pour répondre à partir de documents, de bases de connaissances ou de sources actuelles. Essayez `rag demo: votre question ||| passage un ||| passage deux ||| passage trois` pour voir une version minuscule.\n\n**Le RAG améliore l'accès à l'information pertinente sans garantir l'exactitude :** la récupération peut renvoyer de mauvais passages, et un modèle peut mal lire une preuve correcte.",
      "RAG ihuza **gushakisha** na **gukora igisubizo**, ku buryo umufasha ashobora gusubiza ashingiye ku nyandiko, ububiko bw'ubumenyi cyangwa inkomoko za none. Gerageza `rag demo: ikibazo cyawe ||| igice cya mbere ||| igice cya kabiri ||| igice cya gatatu` ubone verisiyo ntoya.\n\n**RAG yongera uburyo bwo kubona amakuru akwiye ariko ntiyemeza ukuri:** gushakisha bishobora kuzana ibice bitari byo, kandi icyitegererezo gishobora gusoma nabi ibimenyetso bikwiye.",
      "RAG huchanganya **urejeshaji** na **uzalishaji**, ili msaidizi ajibu kutoka hati, hifadhi za maarifa au vyanzo vya sasa. Jaribu `rag demo: swali lako ||| kifungu cha kwanza ||| kifungu cha pili ||| kifungu cha tatu` kuona toleo dogo.\n\n**RAG huboresha ufikiaji wa taarifa husika lakini haihakikishi usahihi:** urejeshaji unaweza kurudisha vifungu visivyo sahihi, na modeli bado inaweza kusoma vibaya ushahidi sahihi."),
     (["**Prepare the source material:** extract text, split long documents into chunks and keep useful metadata.",
       "**Create an index:** many systems compute embeddings and store them in a vector index or database.",
       "**Convert the question** into a search query or an embedding.",
       "**Retrieve relevant passages** with keyword, semantic, vector or hybrid search.",
       "**Add the retrieved passages** to the model's context.",
       "**Generate an answer grounded in those passages** and, when possible, link each claim to its source."],
      ["**Préparer les sources :** extraire le texte, découper les longs documents en morceaux et garder des métadonnées utiles.",
       "**Créer un index :** beaucoup de systèmes calculent des embeddings et les stockent dans un index ou une base vectorielle.",
       "**Convertir la question** en requête de recherche ou en embedding.",
       "**Récupérer les passages pertinents** par recherche par mots-clés, sémantique, vectorielle ou hybride.",
       "**Ajouter les passages récupérés** au contexte du modèle.",
       "**Générer une réponse fondée sur ces passages** et, si possible, relier chaque affirmation à sa source."],
      ["**Gutegura inkomoko:** gukuramo inyandiko, kugabanya inyandiko ndende mu bice no kubika amakuru y'inyongera.",
       "**Gukora index:** sisitemu nyinshi zibara embeddings zikazibika muri vector index cyangwa database.",
       "**Guhindura ikibazo** mu cyifuzo cyo gushakisha cyangwa mu embedding.",
       "**Kuvana ibice bikwiye** hakoreshejwe gushakisha amagambo, ubusobanuro, vector cyangwa uruvange.",
       "**Kongera ibice byavuyemo** mu bwenge bw'icyitegererezo (context).",
       "**Gukora igisubizo gishingiye kuri ibyo bice** kandi, iyo bishoboka, guhuza buri gisobanuro n'inkomoko yacyo."],
      ["**Tayarisha chanzo:** toa maandishi, gawa hati ndefu vipande na uhifadhi metadata muhimu.",
       "**Unda faharasa:** mifumo mingi hukokotoa embeddings na kuzihifadhi kwenye faharasa au hifadhidata ya vekta.",
       "**Geuza swali** kuwa ombi la utafutaji au embedding.",
       "**Rejesha vifungu husika** kwa utafutaji wa maneno, maana, vekta au mchanganyiko.",
       "**Ongeza vifungu vilivyorejeshwa** kwenye muktadha wa modeli.",
       "**Zalisha jibu linalotegemea vifungu hivyo** na, inapowezekana, unganisha kila dai na chanzo chake."]),
     ("The six steps", "Les six étapes", "Intambwe esheshatu", "Hatua sita"), ["qa_research", "ai_embeddings"])

_add("qa_tool_calls",
     "how does a tool call work|what is a tool call|does the ai run the tool|does ai execute tools|ai tool request|function calling|how does an ai use tools to answer|can ai run code|can ai search files|ai connectors|"
     "comment fonctionne un appel d'outil|qu'est-ce qu'un appel d'outil|l'ia execute-t-elle les outils|appel de fonction ia|"
     "tool call ni iki|ai ikoresha ibikoresho ite|ai irakoresha ibikoresho|"
     "tool call ni nini|ai hutumia zana vipi|je ai inaendesha zana", "",
     ("How tool use works", "Comment fonctionne l'utilisation d'outils", "Uko gukoresha ibikoresho bikora", "Jinsi matumizi ya zana yanavyofanya kazi"),
     ("A tool-enabled assistant can **request** an operation through a structured tool call. External software performs the operation and returns a result, and the model uses that result to continue.\n\n**Generating a tool request is not the same as executing it.** The surrounding application validates and runs supported operations. Tools may fail, lack access, return partial data or need your permission, and an assistant must never claim a search, calculation, file review or action happened unless it actually did.",
      "Un assistant doté d'outils peut **demander** une opération par un appel d'outil structuré. Un logiciel externe l'exécute et renvoie un résultat que le modèle utilise pour continuer.\n\n**Générer une demande d'outil n'est pas l'exécuter.** L'application qui l'entoure valide et exécute les opérations prises en charge. Les outils peuvent échouer, manquer d'accès, renvoyer des données partielles ou demander votre permission ; un assistant ne doit jamais prétendre qu'une recherche, un calcul, une lecture de fichier ou une action a eu lieu si ce n'est pas le cas.",
      "Umufasha ufite ibikoresho ashobora **gusaba** igikorwa akoresheje tool call itunganyije. Porogaramu yo hanze iragikora ikagarura igisubizo, icyitegererezo kigakomeza gikoresha icyo gisubizo.\n\n**Gutanga icyifuzo cy'igikoresho si ukigikoresha.** Porogaramu ikikije igenzura ikanakora ibikorwa bishyigikiwe. Ibikoresho bishobora gukora nabi, kubura uburenganzira, gutanga amakuru atuzuye cyangwa gusaba uruhushya rwawe; umufasha ntagomba kuvuga ko gushakisha, kubara, gusoma dosiye cyangwa igikorwa byakozwe niba bitakozwe.",
      "Msaidizi mwenye zana anaweza **kuomba** operesheni kupitia mwito wa zana uliopangiliwa. Programu ya nje hutekeleza na kurudisha matokeo, na modeli huyatumia kuendelea.\n\n**Kutoa ombi la zana si kulitekeleza.** Programu inayozunguka huthibitisha na kuendesha operesheni zinazoungwa mkono. Zana zinaweza kushindwa, kukosa ufikiaji, kurudisha data pungufu au kuhitaji ruhusa yako; msaidizi hapaswi kamwe kudai utafutaji, hesabu, ukaguzi wa faili au kitendo kimefanyika kama hakikufanyika."),
     (["**Web search:** retrieve pages and current information.",
       "**File tools:** search, read, summarise or compare supplied documents.",
       "**Code execution:** run calculations or analyse data in a controlled environment.",
       "**Image tools:** interpret supplied images, or create or edit images when supported.",
       "**Application connectors:** reach an authorised external service when the integration is connected.",
       "**Scheduling or automation tools:** create reminders or recurring tasks when permitted."],
      ["**Recherche web :** récupérer des pages et des informations actuelles.",
       "**Outils de fichiers :** chercher, lire, résumer ou comparer des documents fournis.",
       "**Exécution de code :** faire des calculs ou analyser des données dans un environnement contrôlé.",
       "**Outils d'image :** interpréter des images fournies, ou en créer ou modifier si c'est pris en charge.",
       "**Connecteurs d'applications :** accéder à un service externe autorisé quand l'intégration est connectée.",
       "**Outils de planification ou d'automatisation :** créer des rappels ou tâches récurrentes si c'est permis."],
      ["**Gushakisha kuri interineti:** kuvana impapuro n'amakuru ya none.",
       "**Ibikoresho bya dosiye:** gushakisha, gusoma, kugabanya cyangwa kugereranya inyandiko zatanzwe.",
       "**Gukoresha code:** gukora imibare cyangwa gusesengura amakuru mu kibanza kigenzurwa.",
       "**Ibikoresho by'amashusho:** gusobanura amashusho yatanzwe, cyangwa gukora cyangwa guhindura iyo bishyigikiwe.",
       "**Connectors za porogaramu:** kugera kuri serivisi yemewe yo hanze iyo ihuzwa.",
       "**Ibikoresho byo gutegura cyangwa automation:** gukora ibyibutsa cyangwa imirimo isubirwamo iyo byemewe."],
      ["**Utafutaji wa wavuti:** pata kurasa na taarifa za sasa.",
       "**Zana za faili:** tafuta, soma, fupisha au linganisha hati zilizotolewa.",
       "**Utekelezaji wa msimbo:** fanya hesabu au chambua data katika mazingira yanayodhibitiwa.",
       "**Zana za picha:** fasiri picha zilizotolewa, au unda au hariri picha inapoungwa mkono.",
       "**Viunganishi vya programu:** fikia huduma ya nje iliyoidhinishwa pale muunganisho upo.",
       "**Zana za ratiba au otomatiki:** unda vikumbusho au kazi za kurudia inaporuhusiwa."]),
     ("Typical tools", "Outils courants", "Ibikoresho bisanzwe", "Zana za kawaida"), ["ai_tools", "qa_compose"])

_add("qa_compose",
     "how does ai compose an answer|how are answers composed|how does ai write an answer|how does an ai structure its answer|how does ai format answers|how does ai decide how to answer|"
     "comment l'ia compose une reponse|comment l'ia redige une reponse|comment l'ia structure sa reponse|"
     "ai ikora igisubizo ite|ai itunganya igisubizo ite|"
     "ai hutunga jibu vipi|ai hupanga jibu vipi", "",
     ("How answers are composed (6 steps)", "Comment les réponses sont composées (6 étapes)", "Uko ibisubizo bitunganywa (intambwe 6)", "Jinsi majibu yanavyotungwa (hatua 6)"),
     ("A good answer is **chosen, ordered, formatted and checked**, not just generated.",
      "Une bonne réponse est **choisie, ordonnée, mise en forme et vérifiée**, pas seulement générée.",
      "Igisubizo cyiza **gitoranywa, gitegurwa, gitunganywa kandi kigenzurwa**, ntikiba gusa ugikora.",
      "Jibu zuri **huchaguliwa, hupangwa, hufomatiwa na hukaguliwa**, si kuzalishwa tu."),
     (["**Choose the main answer** that best addresses the user's intent.",
       "**Order the explanation usefully:** the direct answer first, then reasoning or supporting details.",
       "**Use the right format:** plain language, numbered steps, code, a table, citations or a downloadable document.",
       "**Check consistency** with the user's explicit constraints and the evidence available.",
       "**Separate facts, estimates, assumptions, recommendations and uncertainty.**",
       "**Never claim a search, calculation, file review or external action happened unless it actually happened.**"],
      ["**Choisir la réponse principale** qui répond le mieux à l'intention de l'utilisateur.",
       "**Ordonner utilement l'explication :** la réponse directe d'abord, puis le raisonnement ou les détails.",
       "**Utiliser le bon format :** langage simple, étapes numérotées, code, tableau, citations ou document à télécharger.",
       "**Vérifier la cohérence** avec les contraintes explicites de l'utilisateur et les preuves disponibles.",
       "**Séparer faits, estimations, hypothèses, recommandations et incertitudes.**",
       "**Ne jamais prétendre qu'une recherche, un calcul, une lecture de fichier ou une action externe a eu lieu si ce n'est pas le cas.**"],
      ["**Guhitamo igisubizo nyamukuru** gikwiranye n'icyo ukoresha ashaka.",
       "**Gutegura ibisobanuro mu buryo bufasha:** igisubizo kitaziguye mbere, hanyuma impamvu cyangwa utuntu dushyigikira.",
       "**Gukoresha imiterere ikwiye:** ururimi rworoshye, intambwe zibaze, code, imbonerahamwe, inkomoko cyangwa inyandiko yo gukuramo.",
       "**Kugenzura guhuza** n'imbogamizi zasobanuwe n'ibimenyetso bihari.",
       "**Gutandukanya ukuri, ibigereranyo, ibitekerezo, inama n'ukutizera.**",
       "**Ntuzigere uvuga ko gushakisha, kubara, gusoma dosiye cyangwa igikorwa cyo hanze cyakozwe niba kitakozwe.**"],
      ["**Chagua jibu kuu** linalolenga vyema nia ya mtumiaji.",
       "**Panga maelezo kwa manufaa:** jibu la moja kwa moja kwanza, kisha hoja au undani wa kuunga mkono.",
       "**Tumia umbizo sahihi:** lugha rahisi, hatua zenye namba, msimbo, jedwali, manukuu au hati ya kupakua.",
       "**Hakiki uthabiti** na vikwazo vya wazi vya mtumiaji na ushahidi uliopo.",
       "**Tenganisha ukweli, makadirio, dhana, mapendekezo na kutokuwa na uhakika.**",
       "**Kamwe usidai utafutaji, hesabu, ukaguzi wa faili au kitendo cha nje kimefanyika kama hakikufanyika.**"]),
     ("The six steps", "Les six étapes", "Intambwe esheshatu", "Hatua sita"), ["qa_interpret", "qa_safety"])

_add("qa_safety",
     "ai safety privacy and reliability|safety privacy reliability ai|how does ai handle privacy|how does ai stay safe|does ai protect my privacy|how does ai treat web pages and documents|prompt injection|should i trust documents the ai reads|"
     "surete confidentialite et fiabilite ia|comment l'ia protege la vie privee|injection de prompt|"
     "umutekano ibanga no kwizerwa kwa ai|ai irinda ibanga ite|prompt injection ni iki|"
     "usalama faragha na uaminifu wa ai|ai inalindaje faragha|prompt injection ni nini", "",
     ("Safety, privacy and reliability (6 rules)", "Sécurité, confidentialité et fiabilité (6 règles)", "Umutekano, ibanga no kwizerwa (amategeko 6)", "Usalama, faragha na uaminifu (kanuni 6)"),
     ("A responsible assistant follows product rules, protects personal data and treats outside text as **information to evaluate, never as commands** (this is the defence against prompt injection).",
      "Un assistant responsable suit les règles du produit, protège les données personnelles et traite les textes extérieurs comme des **informations à évaluer, jamais comme des ordres** (c'est la défense contre l'injection de prompt).",
      "Umufasha ushinzwe akurikiza amategeko y'igicuruzwa, arinda amakuru bwite kandi afata inyandiko zo hanze nk'**amakuru yo gusuzuma, ntanarimwe nk'amategeko** (ni yo ngabo irwanya prompt injection).",
      "Msaidizi anayewajibika hufuata kanuni za bidhaa, hulinda data binafsi na hutendea maandishi ya nje kama **taarifa za kutathmini, kamwe si amri** (huu ni ulinzi dhidi ya prompt injection)."),
     (["**Follow the applicable system and product rules** while answering requests.",
       "**Decline or redirect** requests that would facilitate serious harm, illegal activity or privacy violations.",
       "**Minimise exposure** of personal or confidential information.",
       "**Treat external documents and web pages as data to evaluate,** not automatically trusted instructions.",
       "**Verify important medical, legal, financial, security or other high-impact claims** with reliable sources and qualified professionals.",
       "**Be transparent about limitations** and never fabricate citations, capabilities or results."],
      ["**Suivre les règles système et produit applicables** en répondant aux demandes.",
       "**Refuser ou rediriger** les demandes qui faciliteraient un tort grave, une activité illégale ou une atteinte à la vie privée.",
       "**Minimiser l'exposition** des informations personnelles ou confidentielles.",
       "**Traiter documents et pages web externes comme des données à évaluer,** pas comme des instructions de confiance.",
       "**Vérifier les affirmations importantes (médicales, juridiques, financières, de sécurité...)** auprès de sources fiables et de professionnels qualifiés.",
       "**Être transparent sur les limites** et ne jamais inventer de citations, capacités ou résultats."],
      ["**Gukurikiza amategeko ya sisitemu n'igicuruzwa** mu gusubiza ibyifuzo.",
       "**Kwanga cyangwa kuyobora ahandi** ibyifuzo byakoroshya ibibi bikomeye, ibikorwa binyuranyije n'amategeko cyangwa gukoza isoni ibanga.",
       "**Kugabanya kugaragaza** amakuru bwite cyangwa y'ibanga.",
       "**Gufata inyandiko n'impapuro zo hanze nk'amakuru yo gusuzuma,** si amabwiriza yizewe ako kanya.",
       "**Kugenzura ibivugwa by'ingenzi (ubuvuzi, amategeko, imari, umutekano...)** ku nkomoko yizewe no ku banyamwuga babifitiye ubushobozi.",
       "**Kuba mu mucyo ku mbibi** ntuzigere ukora inkomoko, ubushobozi cyangwa ibisubizo by'ibihimbano."],
      ["**Fuata kanuni husika za mfumo na bidhaa** unapojibu maombi.",
       "**Kataa au elekeza upya** maombi yanayoweza kuwezesha madhara makubwa, shughuli haramu au ukiukaji wa faragha.",
       "**Punguza kufichua** taarifa binafsi au za siri.",
       "**Tendea hati na kurasa za wavuti za nje kama data ya kutathmini,** si maagizo yanayoaminika moja kwa moja.",
       "**Thibitisha madai muhimu ya afya, sheria, fedha, usalama au yenye athari kubwa** kwa vyanzo vya kuaminika na wataalamu wenye sifa.",
       "**Kuwa wazi kuhusu mipaka** na kamwe usibuni manukuu, uwezo au matokeo."]),
     ("The six rules", "Les six règles", "Amategeko atandatu", "Kanuni sita"), ["ai_limits", "qa_mistakes"])

_add("qa_mistakes",
     "why does ai make mistakes|why can ai be wrong|why does ai get things wrong|why do ai answers have errors|reasons ai is wrong|why is ai sometimes wrong|how to check ai answers|how do i verify ai answers|"
     "pourquoi l'ia fait des erreurs|pourquoi l'ia se trompe|comment verifier les reponses de l'ia|"
     "kuki ai ikora amakosa|kuki ai ibeshya|uko wagenzura ibisubizo bya ai|"
     "kwa nini ai hufanya makosa|kwa nini ai hukosea|jinsi ya kuhakiki majibu ya ai", "",
     ("Why AI can make mistakes (7 reasons)", "Pourquoi l'IA peut se tromper (7 raisons)", "Impamvu AI ishobora gukora amakosa (impamvu 7)", "Kwa nini AI inaweza kukosea (sababu 7)"),
     ("**Confident wording does not prove a claim is correct.** Useful practice: verify important claims, ask for sources, test code in a safe environment and compare results with authoritative documentation.",
      "**Un ton assuré ne prouve pas qu'une affirmation est correcte.** Bonne pratique : vérifier les affirmations importantes, demander des sources, tester le code dans un environnement sûr et comparer avec la documentation officielle.",
      "**Amagambo yizeye ntibyerekana ko ibivugwa ari ukuri.** Imyitozo ifasha: genzura ibivugwa by'ingenzi, saba inkomoko, gerageza code ahantu hizewe kandi ugereranye n'inyandiko z'inzego zemewe.",
      "**Maneno ya kujiamini hayathibitishi dai ni sahihi.** Mazoea mazuri: thibitisha madai muhimu, omba vyanzo, jaribu msimbo katika mazingira salama na linganisha na nyaraka zenye mamlaka."),
     (["**Pattern-based generation** can produce plausible statements that are false.",
       "**Training data** can be incomplete, outdated, inconsistent or biased.",
       "**Ambiguous questions** can be interpreted incorrectly.",
       "**Search tools** may find poor sources or miss the best one.",
       "**Long context** can omit details, exceed limits or cause confusion.",
       "**Images, calculations, code and complex logic** can contain subtle errors.",
       "**Confident wording** does not prove a claim is correct."],
      ["**La génération par motifs** peut produire des affirmations plausibles mais fausses.",
       "**Les données d'entraînement** peuvent être incomplètes, périmées, incohérentes ou biaisées.",
       "**Les questions ambiguës** peuvent être mal interprétées.",
       "**Les outils de recherche** peuvent trouver de mauvaises sources ou manquer la meilleure.",
       "**Un long contexte** peut omettre des détails, dépasser les limites ou créer de la confusion.",
       "**Images, calculs, code et logique complexe** peuvent contenir des erreurs subtiles.",
       "**Un ton assuré** ne prouve pas qu'une affirmation est correcte."],
      ["**Gukora hashingiwe ku miterere** bishobora gutanga ibisa n'ukuri ariko atari ukuri.",
       "**Amakuru yo guhugura** ashobora kuba atuzuye, ashaje, ahabanye cyangwa abogamye.",
       "**Ibibazo bitumvikana** bishobora gusobanurwa nabi.",
       "**Ibikoresho byo gushakisha** bishobora kubona inkomoko mbi cyangwa kubura nziza.",
       "**Context ndende** ishobora gusiga utuntu, kurenga imbibi cyangwa gutera urujijo.",
       "**Amashusho, imibare, code n'ibitekerezo bikomeye** bishobora kugira amakosa mato.",
       "**Amagambo yizeye** ntibyerekana ko ibivugwa ari ukuri."],
      ["**Uzalishaji unaotegemea mifumo** unaweza kutoa kauli zinazokubalika lakini za uongo.",
       "**Data ya mafunzo** inaweza kuwa pungufu, ya zamani, isiyoendana au yenye upendeleo.",
       "**Maswali yenye utata** yanaweza kufasiriwa vibaya.",
       "**Zana za utafutaji** zinaweza kupata vyanzo hafifu au kukosa bora.",
       "**Muktadha mrefu** unaweza kuacha undani, kuvuka mipaka au kuleta mkanganyiko.",
       "**Picha, hesabu, msimbo na mantiki changamano** vinaweza kuwa na makosa madogo.",
       "**Maneno ya kujiamini** hayathibitishi dai ni sahihi."]),
     ("The seven reasons", "Les sept raisons", "Impamvu ndwi", "Sababu saba"), ["ai_hallucination", "qa_safety"])

_add("qa_example",
     "example of answering a current question|how does ai answer a current question|how would an ai find a free legal stream|which free website streams this film|how to answer a time-sensitive question|time-sensitive question|"
     "exemple de reponse a une question d'actualite|comment l'ia repond a une question d'actualite|question dependante du temps|"
     "urugero rwo gusubiza ikibazo cya none|ikibazo gishingiye ku gihe|"
     "mfano wa kujibu swali la sasa|swali linalotegemea wakati", "",
     ("Example: answering a current question", "Exemple : répondre à une question d'actualité", "Urugero: gusubiza ikibazo cya none", "Mfano: kujibu swali la sasa"),
     ("Question: “Which free website streams this film in Rwanda today?” The honest path is to search, verify, and **say clearly when no reliable evidence exists** rather than invent a working link.",
      "Question : « Quel site gratuit diffuse ce film au Rwanda aujourd'hui ? » La démarche honnête : chercher, vérifier, et **dire clairement quand aucune preuve fiable n'existe** plutôt que d'inventer un lien qui marche.",
      "Ikibazo: «Ni uwuhe rubuga rutishyuzwa rwerekana iyi filime mu Rwanda uyu munsi?» Inzira y'ukuri: gushakisha, kugenzura, no **kuvuga neza igihe nta bimenyetso byizewe bihari** aho guhimba link ikora.",
      "Swali: «Ni tovuti gani ya bure inaonyesha filamu hii nchini Rwanda leo?» Njia ya uaminifu: tafuta, hakiki, na **sema wazi wakati hakuna ushahidi wa kuaminika** badala ya kubuni kiungo kinachofanya kazi."),
     (["**Recognise** a time-sensitive and location-dependent availability question.",
       "**Search** for the exact film title, legal free streaming and Rwanda availability.",
       "**Check** official streaming providers and reputable availability listings.",
       "**Confirm** that the result offers the complete film (not a trailer) and plays in the user's region.",
       "**If no reliable evidence confirms a free legal stream, say so clearly** instead of inventing a link.",
       "**Offer legitimate next steps** without describing paid options as free."],
      ["**Reconnaître** une question de disponibilité sensible au temps et au lieu.",
       "**Chercher** le titre exact du film, la diffusion gratuite légale et la disponibilité au Rwanda.",
       "**Vérifier** les fournisseurs officiels de streaming et des annuaires de disponibilité réputés.",
       "**Confirmer** que le résultat offre le film complet (pas une bande-annonce) et se lit dans la région de l'utilisateur.",
       "**Si aucune preuve fiable ne confirme un streaming gratuit légal, le dire clairement** au lieu d'inventer un lien.",
       "**Proposer des suites légitimes** sans présenter des options payantes comme gratuites."],
      ["**Kumenya** ko ari ikibazo cy'uboneka gishingiye ku gihe n'ahantu.",
       "**Gushakisha** izina nyaryo rya filime, kuyireba ku buntu mu buryo bwemewe n'uko iboneka mu Rwanda.",
       "**Kugenzura** abatanga serivisi za streaming bemewe n'urutonde rwizewe rw'uboneka.",
       "**Kwemeza** ko igisubizo gitanga filime yuzuye (si trailer) kandi ikinirwa mu karere k'ukoresha.",
       "**Iyo nta kimenyetso cyizewe gihari, kubivuga neza** aho guhimba link.",
       "**Gutanga ibikurikiraho byemewe** utavuga ko ibyishyurwa ari ubuntu."],
      ["**Tambua** swali la upatikanaji linalotegemea wakati na mahali.",
       "**Tafuta** jina kamili la filamu, utiririshaji halali wa bure na upatikanaji nchini Rwanda.",
       "**Kagua** watoa huduma rasmi wa utiririshaji na orodha za upatikanaji zinazoheshimika.",
       "**Thibitisha** kuwa tokeo linatoa filamu kamili (si trela) na linacheza katika eneo la mtumiaji.",
       "**Ikiwa hakuna ushahidi wa kuaminika, sema wazi** badala ya kubuni kiungo.",
       "**Toa hatua halali zinazofuata** bila kuelezea chaguo za kulipia kama za bure."]),
     ("The six steps", "Les six étapes", "Intambwe esheshatu", "Hatua sita"), ["qa_research", "qa_compose"])

_add("qa_unknowable",
     "what is not publicly knowable about ai|what do we not know about ai models|private details of an ai model|can an ai reveal its hidden instructions|does ai show its reasoning|what is not publicly known about ai|how many parameters does the ai have|what data was the ai trained on|"
     "ce qui n'est pas public sur l'ia|details prives d'un modele ia|l'ia peut-elle reveler ses instructions cachees|combien de parametres a l'ia|"
     "ibitazwi ku mugaragaro kuri ai|ai ifite parameters zingahe|ai yahuguwe ku makuru ayahe|"
     "yasiyojulikana hadharani kuhusu ai|ai ina vigezo vingapi|ai ilifunzwa kwa data gani", "",
     ("What a general guide cannot tell you", "Ce qu'un guide général ne peut pas dire", "Ibyo igitabo rusange kidashobora kukubwira", "Kile mwongozo wa jumla hauwezi kukuambia"),
     ("A public explanation cannot establish every detail of a deployed model: its **private architecture, exact parameter count, complete training data, internal instructions, hidden reasoning traces, safety implementation or all inference settings.** These can vary by model version and product configuration.\n\n**A useful distinction:** general machine-learning principles can be explained; confidential or undocumented specifics must not be guessed. An assistant's final answer also does not expose every internal computation behind it.",
      "Une explication publique ne peut pas établir chaque détail d'un modèle déployé : son **architecture privée, son nombre exact de paramètres, ses données d'entraînement complètes, ses instructions internes, ses traces de raisonnement cachées, sa sécurité ou tous ses réglages d'inférence.** Cela varie selon la version et la configuration du produit.\n\n**Distinction utile :** les principes généraux de l'apprentissage automatique s'expliquent ; les détails confidentiels ou non documentés ne doivent pas être devinés. La réponse finale d'un assistant n'expose pas non plus chaque calcul interne.",
      "Ibisobanuro rusange ntibishobora kwemeza buri kantu k'icyitegererezo cyashyizwe mu bikorwa: **imiterere y'ibanga, umubare nyawo wa parameters, amakuru yose yo guhugura, amabwiriza y'imbere, uburyo bw'ibitekerezo bwihishe, uburyo bw'umutekano cyangwa igenamiterere ryose rya inference.** Ibi bishobora guhinduka bitewe na verisiyo n'igenamiterere ry'igicuruzwa.\n\n**Itandukaniro rifasha:** amahame rusange ya machine learning arasobanurwa; ibanga cyangwa ibitanditse ntibigomba gukekwa. Igisubizo cya nyuma nacyo ntikigaragaza buri mibare y'imbere yakozwe.",
      "Maelezo ya umma hayawezi kuthibitisha kila undani wa modeli iliyotumwa: **muundo wa siri, idadi kamili ya vigezo, data kamili ya mafunzo, maagizo ya ndani, athari za fikra zilizofichwa, utekelezaji wa usalama au mipangilio yote ya inference.** Haya yanaweza kutofautiana kwa toleo na usanidi wa bidhaa.\n\n**Tofauti muhimu:** kanuni za jumla za ujifunzaji wa mashine zinaweza kuelezwa; maelezo ya siri au yasiyoandikwa hayapaswi kubashiriwa. Jibu la mwisho la msaidizi pia halifichui kila hesabu ya ndani."),
     related=["ai_big_picture", "qa_safety"])

_add("qa_final", "final principle of reliable answering|what makes an ai answer reliable|how to get reliable answers from ai|reliable answering|"
     "principe final des reponses fiables|ce qui rend une reponse ia fiable|"
     "ihame rya nyuma ry'ibisubizo byizewe|icyo gituma igisubizo cya ai cyizerwa|"
     "kanuni ya mwisho ya majibu ya kuaminika|nini hufanya jibu la ai liaminike", "",
     ("Final principle: reliable answering", "Principe final : des réponses fiables", "Ihame rya nyuma: ibisubizo byizewe", "Kanuni ya mwisho: majibu ya kuaminika"),
     ("Reliable answering combines **a trained model, clear instructions, relevant context, suitable tools, source verification, careful formatting and honest treatment of uncertainty.** No single technique guarantees a correct answer every time.",
      "Une réponse fiable combine **un modèle entraîné, des instructions claires, un contexte pertinent, des outils adaptés, la vérification des sources, une mise en forme soignée et un traitement honnête de l'incertitude.** Aucune technique seule ne garantit une réponse correcte à chaque fois.",
      "Igisubizo cyizewe gihuza **icyitegererezo cyahuguwe, amabwiriza asobanutse, context ikwiye, ibikoresho bikwiye, kugenzura inkomoko, imiterere inoze n'ubunyangamugayo ku kutizera.** Nta buryo bumwe bwemeza igisubizo cy'ukuri buri gihe.",
      "Kujibu kwa kuaminika huchanganya **modeli iliyofunzwa, maagizo wazi, muktadha husika, zana zinazofaa, uthibitishaji wa vyanzo, uumbizaji makini na uaminifu kuhusu kutokuwa na uhakika.** Hakuna mbinu moja inayohakikisha jibu sahihi kila mara."),
     related=["qa_mistakes", "qa_safety"])

_add("qa_reading", "ai research guide further reading|further reading on how ai answers|where to read about rag|rag reading list|how chatgpt is developed|llm fundamentals|optimizing llm accuracy|generative ai glossary|"
     "lectures sur le fonctionnement des reponses ia|ressources sur le rag|"
     "aho gusoma kuri rag|amasomo ya ai n'ubushakashatsi|"
     "vyanzo vya kusoma kuhusu rag|usomaji zaidi kuhusu majibu ya ai", "",
     ("Further reading: how AI answers and researches", "Pour aller plus loin : comment l'IA répond et cherche", "Gusoma byinshi: uko AI isubiza ikanashakisha", "Usomaji zaidi: jinsi AI inavyojibu na kutafiti"),
     ("These public sources explain **general techniques**; they do not reveal private details of a particular model. Check each address yourself.\n\n- How ChatGPT and foundation models are developed (OpenAI Help Center): https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-foundation-models-are-developed\n- LLM Fundamentals (Microsoft Learn): https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals\n- Retrieval-Augmented Generation (Google Cloud): https://cloud.google.com/use-cases/retrieval-augmented-generation\n- Optimizing LLM Accuracy (OpenAI API docs): https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy\n- Generative AI glossary (Google Cloud): https://docs.cloud.google.com/docs/generative-ai/glossary",
      "Ces sources publiques expliquent des **techniques générales** ; elles ne révèlent pas les détails privés d'un modèle précis. Vérifiez chaque adresse vous-même.\n\n- How ChatGPT and foundation models are developed (OpenAI Help Center) : https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-foundation-models-are-developed\n- LLM Fundamentals (Microsoft Learn) : https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals\n- Retrieval-Augmented Generation (Google Cloud) : https://cloud.google.com/use-cases/retrieval-augmented-generation\n- Optimizing LLM Accuracy (OpenAI API docs) : https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy\n- Generative AI glossary (Google Cloud) : https://docs.cloud.google.com/docs/generative-ai/glossary",
      "Aya masoko rusange asobanura **uburyo rusange**; ntatangaza amakuru y'ibanga y'icyitegererezo runaka. Genzura buri aderesi wowe ubwawe.\n\n- How ChatGPT and foundation models are developed (OpenAI Help Center): https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-foundation-models-are-developed\n- LLM Fundamentals (Microsoft Learn): https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals\n- Retrieval-Augmented Generation (Google Cloud): https://cloud.google.com/use-cases/retrieval-augmented-generation\n- Optimizing LLM Accuracy (OpenAI API docs): https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy\n- Generative AI glossary (Google Cloud): https://docs.cloud.google.com/docs/generative-ai/glossary",
      "Vyanzo hivi vya umma vinaeleza **mbinu za jumla**; havifichui undani wa siri wa modeli fulani. Hakiki kila anwani mwenyewe.\n\n- How ChatGPT and foundation models are developed (OpenAI Help Center): https://help.openai.com/en/articles/7842364-how-chatgpt-and-our-foundation-models-are-developed\n- LLM Fundamentals (Microsoft Learn): https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals\n- Retrieval-Augmented Generation (Google Cloud): https://cloud.google.com/use-cases/retrieval-augmented-generation\n- Optimizing LLM Accuracy (OpenAI API docs): https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy\n- Generative AI glossary (Google Cloud): https://docs.cloud.google.com/docs/generative-ai/glossary"),
     related=["ai_references"])

_add("qa_learning_path", "beginner path to build a question answering assistant|how to build a question answering assistant|how do i build an ai assistant|build a document search tool|build a rag assistant|how to build a chatbot with documents|"
     "comment construire un assistant de questions-reponses|construire un assistant ia|construire un chatbot avec des documents|"
     "uko wakubaka umufasha usubiza ibibazo|gukora chatbot ukoresheje inyandiko|"
     "jinsi ya kujenga msaidizi wa maswali na majibu|kujenga chatbot kwa hati", "",
     ("Beginner path: build a question-answering assistant (8 steps)", "Parcours débutant : construire un assistant de questions-réponses (8 étapes)", "Inzira y'umutangizi: kubaka umufasha usubiza ibibazo (intambwe 8)", "Njia ya mwanzo: jenga msaidizi wa maswali na majibu (hatua 8)"),
     ("Build small, transparent things first; each step prepares the next. Use only documents you are allowed to use.",
      "Construisez d'abord de petites choses transparentes ; chaque étape prépare la suivante. N'utilisez que des documents que vous avez le droit d'utiliser.",
      "Tangira wubaka ibintu bito bisobanutse; buri ntambwe itegura ikurikira. Koresha gusa inyandiko wemerewe gukoresha.",
      "Anza kujenga vitu vidogo vilivyo wazi; kila hatua huandaa inayofuata. Tumia hati unazoruhusiwa kutumia tu."),
     (["**Learn Python basics:** variables, conditions, loops, functions, lists, dictionaries and file handling.",
       "**Study** data structures, algorithms, probability, linear algebra and basic calculus.",
       "**Learn how neural networks train** using small, transparent examples.",
       "**Build a simple text classifier** before attempting a large language model.",
       "**Build a document search tool,** then add an LLM to explain the retrieved passages.",
       "**Learn** embeddings, vector search, RAG, evaluation and prompt design.",
       "**Add** safety checks, logging, error handling and tests.",
       "**Build a small question-answering assistant** using documents you are allowed to use."],
      ["**Apprendre les bases de Python :** variables, conditions, boucles, fonctions, listes, dictionnaires et fichiers.",
       "**Étudier** structures de données, algorithmes, probabilités, algèbre linéaire et calcul de base.",
       "**Apprendre comment s'entraînent les réseaux de neurones** avec de petits exemples transparents.",
       "**Construire un classifieur de texte simple** avant de viser un grand modèle de langage.",
       "**Construire un outil de recherche de documents,** puis ajouter un LLM qui explique les passages trouvés.",
       "**Apprendre** embeddings, recherche vectorielle, RAG, évaluation et conception de prompts.",
       "**Ajouter** contrôles de sécurité, journalisation, gestion d'erreurs et tests.",
       "**Construire un petit assistant de questions-réponses** avec des documents que vous avez le droit d'utiliser."],
      ["**Iga ibanze bya Python:** variables, conditions, loops, functions, lists, dictionaries no gukoresha dosiye.",
       "**Wige** imiterere y'amakuru, algorithms, probability, linear algebra na calculus y'ibanze.",
       "**Wige uko neural networks zihugurwa** ukoresheje ingero ntoya zisobanutse.",
       "**Kubaka text classifier yoroheje** mbere yo kugerageza icyitegererezo kinini cy'ururimi.",
       "**Kubaka igikoresho cyo gushakisha mu nyandiko,** hanyuma wongereho LLM isobanura ibice byabonetse.",
       "**Wige** embeddings, vector search, RAG, isuzuma no gutegura prompts.",
       "**Ongeraho** igenzura ry'umutekano, logging, gucunga amakosa n'ibizamini.",
       "**Kubaka umufasha muto usubiza ibibazo** ukoresheje inyandiko wemerewe gukoresha."],
      ["**Jifunze misingi ya Python:** vigeu, masharti, mizunguko, vitendakazi, orodha, kamusi na ushughulikiaji wa faili.",
       "**Soma** miundo ya data, algoriti, uwezekano, aljebra ya mstari na kalkulasi ya msingi.",
       "**Jifunze jinsi mitandao ya neva inavyofunzwa** kwa mifano midogo iliyo wazi.",
       "**Jenga kiainishi rahisi cha maandishi** kabla ya kujaribu modeli kubwa ya lugha.",
       "**Jenga zana ya kutafuta hati,** kisha ongeza LLM kueleza vifungu vilivyopatikana.",
       "**Jifunze** embeddings, utafutaji wa vekta, RAG, tathmini na usanifu wa prompt.",
       "**Ongeza** ukaguzi wa usalama, kumbukumbu, ushughulikiaji wa makosa na majaribio.",
       "**Jenga msaidizi mdogo wa maswali na majibu** kwa hati unazoruhusiwa kutumia."]),
     ("The eight steps", "Les huit étapes", "Intambwe umunani", "Hatua nane"), ["ai_learning_path", "qa_rag"])

# ---- glossary additions (terms from section 14 that the AI Technical Guide did not define)
TERMS = [
    ("RAG", "rag|retrieval-augmented generation|retrieval augmented generation|generation augmentee par la recherche",
     ("Retrieval-augmented generation: retrieve evidence, add it to the context, then generate an answer.", "Génération augmentée par récupération : récupérer des preuves, les ajouter au contexte, puis générer une réponse.", "Retrieval-augmented generation: kuvana ibimenyetso, kubyongera muri context, hanyuma gukora igisubizo.", "Retrieval-augmented generation: kurejesha ushahidi, kuuongeza kwenye muktadha, kisha kuzalisha jibu.")),
    ("Retrieval", "retrieval|recuperation|kuvana amakuru|urejeshaji",
     ("Finding relevant information from an external collection.", "Trouver des informations pertinentes dans une collection externe.", "Kubona amakuru akwiye mu bubiko bwo hanze.", "Kupata taarifa husika kutoka mkusanyiko wa nje.")),
    ("Tool call", "tool call|appel d'outil|tool calls",
     ("A structured request for external software to perform an operation.", "Une demande structurée pour qu'un logiciel externe effectue une opération.", "Icyifuzo gitunganyije kugira ngo porogaramu yo hanze ikore igikorwa.", "Ombi lililopangiliwa kwa programu ya nje kutekeleza operesheni.")),
    ("Language model", "language model|modele de langage|icyitegererezo cy'ururimi|modeli ya lugha",
     ("A model trained to learn patterns in language and to generate or interpret text.", "Un modèle entraîné à apprendre les motifs du langage et à générer ou interpréter du texte.", "Icyitegererezo cyahuguwe kwiga imiterere y'ururimi no gukora cyangwa gusobanura inyandiko.", "Modeli iliyofunzwa kujifunza mifumo ya lugha na kuzalisha au kufasiri maandishi.")),
    ("Transformer", "transformer|transformers",
     ("A neural-network architecture widely used for language models.", "Une architecture de réseau de neurones très utilisée pour les modèles de langage.", "Imiterere ya neural network ikoreshwa cyane mu byitegererezo by'ururimi.", "Muundo wa mtandao wa neva unaotumika sana kwa modeli za lugha.")),
    ("Pretraining", "pretraining|pre-training|pre-entrainement|pretraining ni iki",
     ("Broad initial training on large datasets.", "Entraînement initial large sur de grands jeux de données.", "Guhugura kwa mbere kwagutse ku makuru manini.", "Mafunzo ya awali mapana kwa seti kubwa za data.")),
]
_TERM_ENTRIES = [(n, [fold(x) for x in kw.split("|")], d) for n, kw, d in TERMS]
_ASK = [fold(x) for x in ["what is", "what's", "define", "meaning of", "explain", "qu'est-ce que", "qu'est-ce qu'un", "c'est quoi", "definition de", "ni iki", "ni nini", "maana ya"]]
_CTX = [fold(x) for x in ["ai", "ia", "llm", "model", "modele", "language", "retrieval", "tool", "assistant", "gpt", "chatbot", "neural", "transformer", "rag", "pretraining", "icyitegererezo", "modeli"]]


def find(question, lang="en"):
    q = fold(question)
    if not q or len(q) > 170:
        return None
    for e, kw, kwc in _RAW:
        if kw and has_phrase(q, kw):
            return e
        if kwc and has_phrase(q, kwc):
            return e
    if has_phrase(q, _ASK) and len(q.split()) <= 9:
        for name, kws, defs in _TERM_ENTRIES:
            if has_phrase(q, kws) and (name in ("RAG", "Retrieval", "Tool call", "Pretraining", "Transformer") or has_phrase(q, _CTX)):
                return entry("qa_term_" + fold(name).replace(" ", "_"), "ai_guide", {l: name for l in LANGS}, dict(zip(LANGS, defs)), None, None, ["qa_rag"])
    return None


IDS = [e["id"] for e, _, _ in _RAW]
