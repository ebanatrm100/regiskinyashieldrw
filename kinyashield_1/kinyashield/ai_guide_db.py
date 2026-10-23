"""How a modern AI assistant works: a four-language explainer built from the owner's "AI Assistant Technical Guide" (question path, tokens, attention,
training, loss, post-training, evaluation, deployment, context and memory, tools, limits, misconceptions, learning projects, glossary).
Pure Python, offline. Wording follows the guide's rules: describe processes, never claim private details of any deployed assistant are public,
never say memorisation is impossible, never claim consciousness. fr/rw/sw wording is a DRAFT for review by fluent speakers."""
from __future__ import annotations
from textutil import fold, has_phrase, lk, entry, LANGS

BOUNDARY = {
    "en": "This is a general, publicly documented picture. The exact architecture, training recipe, size and private instructions of any particular assistant (including me) are not fully public.",
    "fr": "C'est une image générale, documentée publiquement. L'architecture exacte, la recette d'entraînement, la taille et les instructions privées d'un assistant précis (moi compris) ne sont pas entièrement publiques.",
    "rw": "Iyi ni ishusho rusange yanditse ku mugaragaro. Imiterere nyayo, uburyo bwo guhugura, ubunini n'amabwiriza y'ibanga by'umufasha runaka (harimo nanjye) ntibyose bizwi ku mugaragaro.",
    "sw": "Hii ni picha ya jumla iliyoandikwa hadharani. Muundo kamili, mapishi ya mafunzo, ukubwa na maagizo ya siri ya msaidizi fulani (pamoja na mimi) si wazi kabisa kwa umma.",
}

# (id, keywords that are clearly about AI, keywords that need an AI word nearby, title, answer, steps, steps_label, related)
_RAW = []


def _add(id_, kw, kwc, title, answer, steps=None, label=None, related=None, boundary=False):
    st = {l: list(steps[i]) if steps else [] for i, l in enumerate(LANGS)}
    ans = dict(zip(LANGS, answer))
    if boundary:
        ans = {l: ans[l] + "\n\n_" + BOUNDARY[l] + "_" for l in LANGS}
    e = entry(id_, "ai_guide", dict(zip(LANGS, title)), ans, st, dict(zip(LANGS, label)) if label else None, related)
    _RAW.append((e, [fold(x) for x in kw.split("|") if x], [fold(x) for x in kwc.split("|") if x]))


_add("ai_big_picture",
     "how does an ai assistant work|how do ai assistants work|how does ai work|how does chatgpt work|how do llms work|how does a language model work|what is an ai assistant|what is a large language model|what is an llm|"
     "comment fonctionne une ia|comment fonctionne un assistant ia|comment marche une ia|comment fonctionne un modele de langage|qu'est-ce qu'un assistant ia|"
     "ai ikora ite|umufasha wa ai ukora ute|ai ni iki|ai ikora gute|"
     "ai inafanyaje kazi|msaidizi wa ai anafanyaje kazi|ai hufanya kazi vipi|ai inafanya kazi vipi|msaidizi wa ai ni nini", "",
     ("How a modern AI assistant works", "Comment fonctionne un assistant IA moderne", "Uko umufasha wa AI ukora", "Jinsi msaidizi wa AI anavyofanya kazi"),
     ("Think of an AI assistant as a **trained prediction system** connected to a conversation interface and, when enabled, extra tools. A neural network supplies the language ability; supporting software manages instructions, conversation context, safety checks, tool calls and the final display.\n\nTraining creates the learned parameters. Inference uses them to answer one request. A normal question and answer is **not** retraining.",
      "Voyez un assistant IA comme un **système de prédiction entraîné**, relié à une interface de conversation et, si activés, à des outils. Un réseau de neurones fournit la capacité langagière ; des logiciels gèrent les instructions, le contexte, les contrôles de sécurité, les appels d'outils et l'affichage.\n\nL'entraînement crée les paramètres appris. L'inférence les utilise pour répondre à une demande. Une question-réponse ordinaire n'est **pas** un réentraînement.",
      "Tekereza umufasha wa AI nka **sisitemu yahuguwe guhanura**, ihujwe n'aho kuganirira kandi, iyo byemewe, n'ibindi bikoresho. Umuyoboro w'imitsi y'ubwenge (neural network) utanga ubushobozi bw'ururimi; porogaramu zifasha zicunga amabwiriza, imiterere y'ikiganiro, igenzura ry'umutekano, gukoresha ibikoresho no kwerekana igisubizo.\n\nGuhugura bitanga imibare yize. Gukoresha (inference) ni ugukoresha iyo mibare usubiza icyifuzo kimwe. Ikibazo n'igisubizo bisanzwe **si** uguhugura bundi bushya.",
      "Fikiria msaidizi wa AI kama **mfumo uliofunzwa kutabiri**, ulioungwa na kiolesura cha mazungumzo na, ikiwashwa, zana za ziada. Mtandao wa neva hutoa uwezo wa lugha; programu saidizi husimamia maagizo, muktadha wa mazungumzo, ukaguzi wa usalama, miito ya zana na onyesho la mwisho.\n\nMafunzo huunda vigezo vilivyojifunza. Inference huvitumia kujibu ombi moja. Swali na jibu la kawaida **si** kufunza upya."),
     (["**Trained neural network:** learned numbers that interpret context and generate likely next tokens.",
       "**Conversation context:** the current question, earlier relevant turns and the applicable instructions.",
       "**Decoding process:** chooses the next token again and again until a stopping condition.",
       "**Supporting software:** routing, tools, formatting, files, memory (if offered) and product safeguards.",
       "**Evaluation and updates:** measure quality, find failures, improve future versions."],
      ["**Réseau de neurones entraîné :** des nombres appris qui interprètent le contexte et génèrent les jetons suivants probables.",
       "**Contexte de conversation :** la question, les échanges utiles précédents et les instructions applicables.",
       "**Décodage :** choisit le jeton suivant, encore et encore, jusqu'à un critère d'arrêt.",
       "**Logiciels de support :** routage, outils, mise en forme, fichiers, mémoire (si offerte) et garde-fous.",
       "**Évaluation et mises à jour :** mesurer la qualité, trouver les échecs, améliorer les versions futures."],
      ["**Umuyoboro w'imitsi wahuguwe:** imibare yize isobanura imiterere ikanatanga ijambo rikurikira rishoboka (token).",
       "**Imiterere y'ikiganiro:** ikibazo cy'ubu, ibyabanje bifitanye isano n'amabwiriza akurikizwa.",
       "**Gufata icyemezo cy'ijambo rikurikira:** guhitamo token ikurikira inshuro nyinshi kugeza ahagarara.",
       "**Porogaramu zifasha:** kuyobora, ibikoresho, imiterere, dosiye, ububiko (iyo buhari) n'ingamba z'umutekano.",
       "**Isuzuma no kuvugurura:** gupima ubuziranenge, gushaka amakosa, kunoza inyandiko zizaza."],
      ["**Mtandao wa neva uliofunzwa:** namba zilizojifunza zinazotafsiri muktadha na kutoa tokeni inayofuata inayowezekana.",
       "**Muktadha wa mazungumzo:** swali la sasa, zamu za awali zinazohusika na maagizo yanayotumika.",
       "**Uamuzi wa tokeni inayofuata:** huchagua tokeni inayofuata tena na tena hadi sharti la kusimama.",
       "**Programu saidizi:** uelekezaji, zana, umbizo, faili, kumbukumbu (ikitolewa) na kinga za bidhaa.",
       "**Tathmini na masasisho:** kupima ubora, kutafuta kasoro, kuboresha matoleo yajayo."]),
     ("The five parts", "Les cinq éléments", "Ibice bitanu", "Sehemu tano"),
     ["ai_question_path", "ai_training"], boundary=True)

_add("ai_question_path",
     "how does an ai answer a question|what happens when i ask an ai|what happens when i ask a question|from question to answer|from question to response|stages of an ai response|how is a question processed|pipeline of an ai assistant|follow a question through|"
     "de la question a la reponse|comment une ia repond|etapes d'une reponse ia|"
     "kuva ku kibazo kugeza ku gisubizo|ai isubiza ite ikibazo|ikibazo gitunganywa gute muri ai|"
     "kutoka swali hadi jibu|ai inajibu swali vipi|hatua za jibu la ai", "",
     ("From a question to a response: the ten steps", "De la question à la réponse : les dix étapes", "Kuva ku kibazo kugeza ku gisubizo: intambwe cumi", "Kutoka swali hadi jibu: hatua kumi"),
     ("Exact details differ by model and product, but this is a reliable mental model of a typical text assistant.",
      "Les détails exacts varient selon le modèle et le produit, mais voici un modèle mental fiable d'un assistant textuel typique.",
      "Ibisobanuro nyabyo biratandukana bitewe n'icyitegererezo n'igicuruzwa, ariko iyi ni ishusho yizewe y'umufasha usanzwe w'inyandiko.",
      "Maelezo kamili hutofautiana kwa kila modeli na bidhaa, lakini huu ni mfano wa kiakili unaotegemeka wa msaidizi wa maandishi."),
     (["Receive the message, with the application's instructions and the relevant part of the conversation.",
       "Resolve instruction priority: higher-priority directions win; quoted text, web pages and tool output are information to evaluate, not commands.",
       "Tokenize: split the text into token IDs (a token may be a word, a word piece or punctuation).",
       "Embed: map token IDs to vectors and add position information.",
       "Process the context through neural-network layers (attention and feed-forward).",
       "Score every possible next token (logits), turned into probabilities when needed.",
       "Choose the next token with the configured decoding method (most likely, or sampled for variety).",
       "Append it and repeat until an end marker, length limit or tool hand-off.",
       "Use a tool if one is enabled and needed (search, code runner, file reader) and wait for its result.",
       "Return the answer (text, code, table, file) or a clarification or refusal, after product checks."],
      ["Recevoir le message, avec les instructions de l'application et la partie utile de la conversation.",
       "Résoudre la priorité des instructions : les directives de rang supérieur l'emportent ; texte cité, pages web et résultats d'outils sont des informations à évaluer, pas des ordres.",
       "Tokeniser : découper le texte en identifiants de jetons (un jeton peut être un mot, un morceau de mot ou une ponctuation).",
       "Plonger : associer les identifiants à des vecteurs et ajouter la position.",
       "Traiter le contexte via les couches du réseau (attention et couches feed-forward).",
       "Noter chaque jeton suivant possible (logits), transformés en probabilités au besoin.",
       "Choisir le jeton suivant avec la méthode de décodage configurée (le plus probable, ou échantillonné pour varier).",
       "L'ajouter et recommencer jusqu'à un marqueur de fin, une limite de longueur ou un passage à un outil.",
       "Utiliser un outil si activé et nécessaire (recherche, exécuteur de code, lecteur de fichiers) et attendre son résultat.",
       "Renvoyer la réponse (texte, code, tableau, fichier) ou une clarification ou un refus, après les contrôles du produit."],
      ["Kwakira ubutumwa, hamwe n'amabwiriza ya porogaramu n'igice cy'ikiganiro gifitanye isano.",
       "Gukemura uburemere bw'amabwiriza: ay'urwego rwo hejuru atsinda; inyandiko yatangajwe, imbuga n'ibisubizo by'ibikoresho ni amakuru yo gusuzuma, si amategeko.",
       "Gucamo tokens: gutandukanya inyandiko mu bimenyetso (token ishobora kuba ijambo, agace k'ijambo cyangwa akamenyetso).",
       "Gushyira mu mibare (embedding): guhuza ibimenyetso n'imibare no kongeramo umwanya wabyo.",
       "Gutunganya imiterere mu byiciro by'umuyoboro (attention na feed-forward).",
       "Guha amanota buri token ikurikira ishoboka (logits), ihinduwe mu bishoboka iyo bikenewe.",
       "Guhitamo token ikurikira ukurikije uburyo bwashyizweho (ishoboka cyane, cyangwa itoranyijwe ngo bitandukane).",
       "Kuyongeraho no gusubiramo kugeza ku kimenyetso cy'iherezo, imipaka y'uburebure cyangwa guhindukirira igikoresho.",
       "Gukoresha igikoresho iyo cyemewe kandi gikenewe (gushakisha, gukoresha kode, gusoma dosiye) no gutegereza igisubizo cyacyo.",
       "Gusubiza (inyandiko, kode, imbonerahamwe, dosiye) cyangwa ibisobanuro cyangwa kwanga, nyuma y'igenzura ry'igicuruzwa."],
      ["Pokea ujumbe, pamoja na maagizo ya programu na sehemu husika ya mazungumzo.",
       "Tatua kipaumbele cha maagizo: maagizo ya ngazi ya juu hushinda; maandishi yaliyonukuliwa, kurasa za wavuti na matokeo ya zana ni taarifa za kutathmini, si amri.",
       "Gawa kuwa tokeni: gawanya maandishi kuwa vitambulisho vya tokeni (tokeni inaweza kuwa neno, kipande cha neno au alama).",
       "Weka vekta (embedding): oanisha vitambulisho na vekta na ongeza taarifa ya nafasi.",
       "Chakata muktadha kupitia tabaka za mtandao (attention na feed-forward).",
       "Pa alama kila tokeni inayofuata inayowezekana (logits), zigeuzwe kuwa uwezekano inapohitajika.",
       "Chagua tokeni inayofuata kwa njia ya decoding iliyowekwa (inayowezekana zaidi, au ya sampuli kwa utofauti).",
       "Iongeze na kurudia hadi alama ya mwisho, kikomo cha urefu au kukabidhi zana.",
       "Tumia zana ikiwashwa na inahitajika (utafutaji, kiendesha msimbo, kisomaji faili) na ngoja matokeo yake.",
       "Rudisha jibu (maandishi, msimbo, jedwali, faili) au ufafanuzi au kukataa, baada ya ukaguzi wa bidhaa."]),
     ("The ten steps", "Les dix étapes", "Intambwe cumi", "Hatua kumi"),
     ["ai_tokens", "ai_decoding"], boundary=True)

_add("ai_tokens", "tokenization|tokenizer|tokenize|what is tokenization|ce qu'est la tokenisation|tokenisation|gucamo tokens|ugucamo ibimenyetso|ugawaji wa tokeni|tokenisheni",
     "what is a token|what are tokens|token in ai|tokens in llm|qu'est-ce qu'un jeton|jeton en ia|token ni iki|tokeni ni nini|ni iki token",
     ("Tokens and tokenization", "Jetons et tokenisation", "Tokens n'uburyo bwo kuzicamo", "Tokeni na ugawaji wa tokeni"),
     ("A **token** is the unit a model processes. It can be a whole word, a word fragment, punctuation or another learned unit, so **one token is not always one word**. A tokenizer is a rule set plus a learned vocabulary that turns text into token IDs, giving the network a consistent numerical input.\n\nTry it: type `count tokens: your text` to see a simple illustration (it is a teaching splitter, not any real model's tokenizer).",
      "Un **jeton** est l'unité traitée par un modèle : un mot entier, un morceau de mot, une ponctuation ou une autre unité apprise ; **un jeton n'est donc pas toujours un mot**. Un tokeniseur est un ensemble de règles et un vocabulaire appris qui transforme le texte en identifiants, donnant au réseau une entrée numérique cohérente.\n\nEssayez : écrivez `count tokens: votre texte` pour une illustration simple (un découpeur pédagogique, pas le tokeniseur d'un vrai modèle).",
      "**Token** ni igice cy'inyandiko icyitegererezo gitunganya. Ishobora kuba ijambo ryose, agace k'ijambo, akamenyetso cyangwa ikindi gice cyizwe, bityo **token imwe ntiba ijambo rimwe buri gihe**. Tokenizer ni amategeko n'amagambo yize ahindura inyandiko mo nomero, aha umuyoboro ibyinjira bihuje.\n\nGerageza: andika `count tokens: inyandiko yawe` ubone urugero rworoshye (ni igikoresho cyo kwigisha, si tokenizer y'icyitegererezo nyacyo).",
      "**Tokeni** ni kipande ambacho modeli hukichakata. Inaweza kuwa neno zima, kipande cha neno, alama au kitengo kingine kilichojifunzwa, kwa hiyo **tokeni moja si neno moja kila mara**. Tokenizer ni seti ya sheria na msamiati uliojifunzwa unaobadilisha maandishi kuwa vitambulisho, ukiupa mtandao ingizo la namba lenye uthabiti.\n\nJaribu: andika `count tokens: maandishi yako` uone mfano rahisi (ni kigawaji cha kufundishia, si tokenizer ya modeli halisi)."),
     related=["ai_embeddings", "ai_big_picture"])

_add("ai_embeddings", "embedding|embeddings|word embedding|vector representation|plongement|plongements|embedding ni iki|embedding ni nini|vekta ya tokeni",
     "what is a vector in ai|vecteur en ia|vector ni iki mu ai",
     ("Embeddings and position information", "Plongements et information de position", "Embeddings n'amakuru y'umwanya", "Embeddings na taarifa ya nafasi"),
     ("An **embedding** is a learned vector (a list of numbers) assigned to a token ID, a numerical starting representation. **Position information** tells the model where tokens occur, which is how it tells “dog bites person” from “person bites dog”. During processing, each token's vector is updated using the tokens around it.",
      "Un **plongement (embedding)** est un vecteur appris (une liste de nombres) associé à un identifiant de jeton : une représentation numérique de départ. L'**information de position** indique où se trouvent les jetons, ce qui distingue « le chien mord la personne » de « la personne mord le chien ». Pendant le traitement, le vecteur de chaque jeton est mis à jour grâce aux jetons voisins.",
      "**Embedding** ni urutonde rw'imibare rwize ruhabwa buri token, ni intangiriro y'ishusho y'imibare. **Amakuru y'umwanya** abwira icyitegererezo aho token iri, ari ko gitandukanya «imbwa irarya umuntu» na «umuntu arya imbwa». Mu gutunganya, imibare ya buri token ivugururwa hakoreshejwe izindi ziyikikije.",
      "**Embedding** ni vekta iliyojifunzwa (orodha ya namba) inayopewa kitambulisho cha tokeni, uwakilishi wa namba wa mwanzo. **Taarifa ya nafasi** huonyesha tokeni ziko wapi, ndiyo maana modeli hutofautisha «mbwa anauma mtu» na «mtu anauma mbwa». Wakati wa uchakataji, vekta ya kila tokeni husasishwa kwa kutumia tokeni zilizo karibu."),
     related=["ai_attention", "ai_tokens"])

_add("ai_attention", "attention mechanism|self-attention|self attention|what is attention in ai|what does attention mean|transformer architecture|what is a transformer|attention is all you need|"
     "mecanisme d'attention|architecture transformer|qu'est-ce qu'un transformer|attention en ia|"
     "attention ni iki|transformer ni iki|uburyo bwa attention|"
     "attention ni nini|transformer ni nini|utaratibu wa attention", "",
     ("Transformer and attention", "Transformer et attention", "Transformer na attention", "Transformer na attention"),
     ("A common foundation of modern language models is the **Transformer**. Its central mechanism, **attention**, computes context-dependent relationships among tokens instead of treating each token as isolated. Example: in “The student placed the book on the desk because it was heavy”, the word “it” needs context; attention mixes information across positions so “it” can draw on “book”.\n\nAttention is a mathematical mechanism, **not** human concentration or consciousness. Between attention layers, feed-forward layers transform each position, with residual connections and normalization keeping deep networks stable. Try `attention demo` for a tiny worked calculation.",
      "Une base courante des modèles de langage modernes est le **Transformer**. Son mécanisme central, l'**attention**, calcule des relations dépendant du contexte entre les jetons au lieu de les traiter isolément. Exemple : dans « L'élève a posé le livre sur le bureau parce qu'il était lourd », le mot « il » a besoin du contexte ; l'attention mélange l'information entre positions pour que « il » s'appuie sur « livre ».\n\nL'attention est un mécanisme mathématique, **pas** de la concentration humaine ni de la conscience. Entre les couches d'attention, des couches feed-forward transforment chaque position ; connexions résiduelles et normalisation stabilisent les réseaux profonds. Essayez `attention demo` pour un petit calcul.",
      "Urufatiro rusanzwe rw'ibyitegererezo by'ururimi bya none ni **Transformer**. Uburyo bwayo bukuru, **attention**, bubara isano hagati ya tokens zishingiye ku miterere aho kuzifata nk'izitandukanye. Urugero: muri «umunyeshuri yashyize igitabo ku meza kuko cyari kiremereye», ijambo «cyari» rikeneye imiterere; attention ivanga amakuru hagati y'imyanya kugira ngo «cyari» rishingire kuri «igitabo».\n\nAttention ni uburyo bw'imibare, **si** ukwitondera nk'umuntu cyangwa kumenya. Hagati y'ibyiciro bya attention hari ibya feed-forward bihindura buri mwanya. Gerageza `attention demo` ubone igikorwa gito cy'imibare.",
      "Msingi wa kawaida wa modeli za kisasa za lugha ni **Transformer**. Utaratibu wake mkuu, **attention**, hukokotoa uhusiano unaotegemea muktadha kati ya tokeni badala ya kuzichukulia kila moja peke yake. Mfano: katika «mwanafunzi aliweka kitabu mezani kwa sababu kilikuwa kizito», neno «kilikuwa» linahitaji muktadha; attention huchanganya taarifa kati ya nafasi ili «kilikuwa» lielekee «kitabu».\n\nAttention ni utaratibu wa hisabati, **si** umakini wa binadamu wala fahamu. Kati ya tabaka za attention kuna tabaka za feed-forward zinazobadilisha kila nafasi. Jaribu `attention demo` kuona hesabu ndogo."),
     related=["ai_embeddings", "ai_weights"])

_add("ai_weights", "what are weights in ai|what are parameters in ai|what is a parameter in a neural network|what does the model learn|what does an ai learn|does ai store training documents|does the ai know every document|does the ai know every training document|every document it was trained on|does ai know all its training data|does the model memorize|does ai memorize|weights and parameters|"
     "que sont les poids en ia|que sont les parametres|que apprend le modele|l'ia memorise-t-elle|"
     "uburemere muri ai ni iki|icyitegererezo cyiga iki|ai yibuka inyandiko zose|"
     "uzito katika ai ni nini|modeli hujifunza nini|je ai inakariri", "",
     ("Weights, parameters and what a model learns", "Poids, paramètres et ce que le modèle apprend", "Uburemere (weights), parameters n'icyo icyitegererezo cyiga", "Uzito (weights), vigezo na kile modeli hujifunza"),
     ("**Weights / parameters** are large collections of learned numbers. They capture statistical patterns that can support grammar, factual associations, code syntax, common problem-solving strategies and relationships between concepts.\n\nKeep the distinction clear: the weights are **not** a searchable library of all training documents, and not a readable list of rules. But some **memorization can still occur**, so never claim it is impossible.",
      "Les **poids / paramètres** sont de vastes ensembles de nombres appris. Ils capturent des régularités statistiques qui soutiennent la grammaire, des associations factuelles, la syntaxe du code, des stratégies courantes de résolution de problèmes et des liens entre concepts.\n\nGardez la distinction : les poids ne sont **pas** une bibliothèque consultable de tous les documents d'entraînement, ni une liste lisible de règles. Mais une **certaine mémorisation peut se produire** ; ne dites jamais qu'elle est impossible.",
      "**Uburemere / parameters** ni ibyegeranyo binini by'imibare yize. Bifata imiterere y'ibigaragara ishobora gufasha mu myandikire, isano z'ukuri, imiterere ya kode, uburyo busanzwe bwo gukemura ibibazo n'isano hagati y'ibitekerezo.\n\nIkitonderwa: uburemere **si** isomero ushobora gushakamo inyandiko zose zakoreshejwe mu guhugura, kandi si urutonde rw'amategeko rusomeka. Ariko **kwibuka bimwe bishobora kubaho**, bityo ntukavuge ko bidashoboka.",
      "**Uzito / vigezo** ni mkusanyiko mkubwa wa namba zilizojifunzwa. Hunasa mifumo ya takwimu inayoweza kusaidia sarufi, uhusiano wa ukweli, sintaksia ya msimbo, mbinu za kawaida za kutatua matatizo na uhusiano kati ya dhana.\n\nWeka tofauti wazi: uzito **si** maktaba inayotafutika ya nyaraka zote za mafunzo, wala orodha ya sheria inayosomeka. Lakini **ukariri fulani unaweza kutokea**, kwa hiyo usiseme haiwezekani kamwe."),
     related=["ai_training", "ai_limits"], boundary=True)

_add("ai_training", "how is an ai trained|how are language models trained|how do you train a language model|training pipeline|pretraining|pre-training|what is pretraining|training an llm|how to train an llm|"
     "comment entraine-t-on une ia|comment entrainer un modele de langage|pipeline d'entrainement|pre-entrainement|"
     "ai ihugurwa ite|guhugura icyitegererezo cy'ururimi|uburyo bwo guhugura ai|"
     "ai hufunzwa vipi|jinsi ya kufunza modeli ya lugha|mafunzo ya awali", "",
     ("The training pipeline, step by step", "Le pipeline d'entraînement, étape par étape", "Uburyo bwo guhugura, intambwe ku yindi", "Mchakato wa mafunzo, hatua kwa hatua"),
     ("This is a high-level blueprint. The datasets, filters, design and compute for a real product must be chosen for its goals, and the exact recipe of any deployed assistant is not public.\n\nThe central learning loop: **input context → predict next token → measure error → calculate gradients → update weights → repeat.**",
      "C'est un plan général. Les jeux de données, filtres, conception et calcul d'un vrai produit se choisissent selon ses objectifs, et la recette exacte d'un assistant déployé n'est pas publique.\n\nLa boucle centrale : **contexte → prédire le jeton suivant → mesurer l'erreur → calculer les gradients → mettre à jour les poids → recommencer.**",
      "Iyi ni igishushanyo rusange. Amakuru, ayungurura, imiterere n'ubushobozi bwa mudasobwa by'igicuruzwa nyacyo bihitwamo hakurikijwe intego zacyo, kandi uburyo nyabwo bw'umufasha ukoreshwa ntibuzwi ku mugaragaro.\n\nUruziga nyamukuru rwo kwiga: **imiterere → guhanura token ikurikira → gupima ikosa → kubara gradients → kuvugurura uburemere → gusubiramo.**",
      "Huu ni mchoro wa ngazi ya juu. Seti za data, vichujio, muundo na nguvu za kompyuta za bidhaa halisi huchaguliwa kulingana na malengo yake, na mapishi kamili ya msaidizi aliyetumwa si ya umma.\n\nMzunguko mkuu wa kujifunza: **muktadha → tabiri tokeni inayofuata → pima kosa → kokotoa gradients → sasisha uzito → rudia.**"),
     (["**A. Define the target system:** languages, tasks, media, latency, reliability, safety needs, resource limits.",
       "**B. Prepare eligible data:** permitted sources, filtering, deduplication, quality and privacy checks, auditable lineage and usage rights.",
       "**C. Normalize and tokenize:** clean, separate examples, build training sequences, convert to token IDs.",
       "**D. Initialize parameters:** build the network; early predictions are poor.",
       "**E. Run pretraining:** predict the next token, compare with the truth, compute the loss, use gradients to adjust weights.",
       "**F. Repeat at scale:** many batches and steps, accelerators, numerical precision, distributed computation.",
       "**G. Measure progress:** training loss plus separate validation examples; watch for overfitting, data leakage, instability and regressions."],
      ["**A. Définir le système cible :** langues, tâches, médias, latence, fiabilité, sécurité, ressources.",
       "**B. Préparer des données éligibles :** sources autorisées, filtrage, déduplication, contrôles qualité et vie privée, traçabilité et droits d'usage.",
       "**C. Normaliser et tokeniser :** nettoyer, séparer les exemples, construire les séquences, convertir en identifiants.",
       "**D. Initialiser les paramètres :** construire le réseau ; les premières prédictions sont mauvaises.",
       "**E. Pré-entraîner :** prédire le jeton suivant, comparer à la vérité, calculer la perte, ajuster les poids avec les gradients.",
       "**F. Répéter à grande échelle :** nombreux lots et étapes, accélérateurs, précision numérique, calcul distribué.",
       "**G. Mesurer les progrès :** perte d'entraînement et exemples de validation séparés ; surveiller surapprentissage, fuite de données, instabilité, régressions."],
      ["**A. Gusobanura sisitemu intego:** indimi, imirimo, itangazamakuru, igihe, kwizerwa, umutekano, ibikoresho.",
       "**B. Gutegura amakuru yemewe:** inkomoko zemewe, kuyungurura, gukuraho ibisubirwamo, igenzura ry'ubuziranenge n'ibanga, uburenganzira bwo kuyakoresha.",
       "**C. Gutunganya no gucamo tokens:** gusukura, gutandukanya ingero, kubaka uruhererekane, guhindura mo nomero.",
       "**D. Gutangiza parameters:** kubaka umuyoboro; ibyo ahanura mbere ni bibi.",
       "**E. Guhugura mbere (pretraining):** guhanura token ikurikira, kugereranya n'ukuri, kubara loss, gukoresha gradients mu gukosora uburemere.",
       "**F. Gusubiramo ku rugero runini:** ibice byinshi n'intambwe nyinshi, ibikoresho byihuta, kubara hagati ya mudasobwa nyinshi.",
       "**G. Gupima iterambere:** loss yo guhugura n'ingero zitandukanye zo kwemeza; kwirinda overfitting, gusohoka kw'amakuru, guhinduka no gusubira inyuma."],
      ["**A. Bainisha mfumo lengwa:** lugha, kazi, vyombo vya habari, kuchelewa, kutegemewa, usalama, mipaka ya rasilimali.",
       "**B. Andaa data inayostahili:** vyanzo vilivyoruhusiwa, uchujaji, kuondoa marudio, ukaguzi wa ubora na faragha, asili na haki za matumizi.",
       "**C. Sawazisha na gawa kuwa tokeni:** safisha, tenganisha mifano, jenga mfuatano, badilisha kuwa vitambulisho.",
       "**D. Anzisha vigezo:** jenga mtandao; makadirio ya mwanzo ni mabaya.",
       "**E. Fanya pretraining:** tabiri tokeni inayofuata, linganisha na ukweli, kokotoa loss, tumia gradients kurekebisha uzito.",
       "**F. Rudia kwa kiwango kikubwa:** makundi na hatua nyingi, vichapuzi, usahihi wa namba, hesabu zilizosambazwa.",
       "**G. Pima maendeleo:** loss ya mafunzo na mifano tofauti ya uthibitishaji; angalia overfitting, uvujaji wa data, kutokuwa thabiti na kurudi nyuma."]),
     ("The seven stages", "Les sept étapes", "Ibyiciro birindwi", "Hatua saba"),
     ["ai_loss", "ai_posttraining"])

_add("ai_loss", "cross-entropy|cross entropy|what is loss in ai|prediction loss|what is the loss function|gradient descent|what is a gradient|backpropagation|what is backpropagation|what is an optimizer|what is a batch|"
     "entropie croisee|fonction de perte|descente de gradient|retropropagation|"
     "loss ni iki|gradient ni iki|backpropagation ni iki|"
     "loss ni nini|gradient ni nini|backpropagation ni nini", "what is loss|what is a loss|what does loss mean|qu'est-ce que la perte|perte en ia|nini maana ya loss",
     ("The mathematics of training: loss, gradients, optimizer", "Les mathématiques de l'entraînement : perte, gradients, optimiseur", "Imibare yo guhugura: loss, gradients, optimizer", "Hisabati ya mafunzo: loss, gradients, optimizer"),
     ("For each training position, compare the predicted probability of the correct next token with the target. A common objective is **cross-entropy loss**:\n\n`Loss = − log P(correct next token | previous context)`\n\nThe higher the probability given to the correct token, the lower the loss. Try `loss 0.8` or `gradient descent demo`.\n\nA low training loss alone proves nothing: test on unseen examples, unusual inputs and deliberate failure attempts.",
      "Pour chaque position d'entraînement, on compare la probabilité prédite du bon jeton suivant à la cible. Un objectif courant est la **perte d'entropie croisée** :\n\n`Perte = − log P(bon jeton suivant | contexte précédent)`\n\nPlus la probabilité du bon jeton est élevée, plus la perte est faible. Essayez `loss 0.8` ou `gradient descent demo`.\n\nUne faible perte d'entraînement ne prouve rien seule : testez sur des exemples inédits, des entrées inhabituelles et des tentatives d'échec volontaires.",
      "Kuri buri mwanya wo guhugura, bagereranya amahirwe yahanuwe ya token ikurikira nyayo n'intego. Intego isanzwe ni **cross-entropy loss**:\n\n`Loss = − log P(token ikurikira nyayo | imiterere yabanje)`\n\nNiko amahirwe yahawe token nyayo aba menshi, loss iba nke. Gerageza `loss 0.8` cyangwa `gradient descent demo`.\n\nLoss nto yo guhugura ntihagije: gerageza ku ngero zitigeze zibonwa, ibyinjijwe bidasanzwe n'ibigerageza gutuma binanirwa.",
      "Kwa kila nafasi ya mafunzo, linganisha uwezekano uliotabiriwa wa tokeni sahihi inayofuata na lengo. Lengo la kawaida ni **cross-entropy loss**:\n\n`Loss = − log P(tokeni sahihi inayofuata | muktadha uliotangulia)`\n\nKadiri uwezekano wa tokeni sahihi unavyokuwa juu, ndivyo loss inavyopungua. Jaribu `loss 0.8` au `gradient descent demo`.\n\nLoss ndogo ya mafunzo pekee haithibitishi lolote: jaribu kwa mifano ambayo haijawahi kuonekana, ingizo zisizo za kawaida na majaribio ya makusudi ya kushindwa."),
     (["**Probability:** how likely a candidate token is under the current model and context.",
       "**Loss:** a number measuring prediction error for the chosen objective.",
       "**Gradient:** how changing each parameter would change the loss locally.",
       "**Backpropagation:** a method to calculate gradients through the network.",
       "**Optimizer:** turns gradients into parameter updates.",
       "**Batch:** a group of examples processed together before one or more updates."],
      ["**Probabilité :** à quel point un jeton candidat est probable selon le modèle et le contexte.",
       "**Perte :** nombre mesurant l'erreur de prédiction pour l'objectif choisi.",
       "**Gradient :** comment changer chaque paramètre modifierait localement la perte.",
       "**Rétropropagation :** méthode de calcul des gradients à travers le réseau.",
       "**Optimiseur :** transforme les gradients en mises à jour des paramètres.",
       "**Lot (batch) :** groupe d'exemples traités ensemble avant une ou plusieurs mises à jour."],
      ["**Probability (amahirwe):** uko token ishobora kuba iyo, ukurikije icyitegererezo n'imiterere.",
       "**Loss:** umubare upima ikosa ryo guhanura ku ntego yatoranyijwe.",
       "**Gradient:** uko guhindura buri parameter byahindura loss aho ari.",
       "**Backpropagation:** uburyo bwo kubara gradients mu muyoboro wose.",
       "**Optimizer:** ihindura gradients mu mavugurura ya parameters.",
       "**Batch:** itsinda ry'ingero zitunganywa hamwe mbere y'ivugurura rimwe cyangwa menshi."],
      ["**Probability (uwezekano):** tokeni mgombea inavyowezekana kwa modeli na muktadha wa sasa.",
       "**Loss:** namba inayopima kosa la ubashiri kwa lengo lililochaguliwa.",
       "**Gradient:** jinsi kubadilisha kila kigezo kungebadilisha loss kwa eneo hilo.",
       "**Backpropagation:** njia ya kukokotoa gradients kupitia mtandao.",
       "**Optimizer:** hubadilisha gradients kuwa masasisho ya vigezo.",
       "**Batch:** kundi la mifano linalochakatwa pamoja kabla ya sasisho moja au zaidi."]),
     ("Key terms", "Termes clés", "Amagambo y'ingenzi", "Istilahi muhimu"),
     ["ai_training", "ai_posttraining"])

_add("ai_posttraining", "post-training|post training|supervised fine-tuning|fine-tuning|fine tuning|what is fine-tuning|rlhf|preference optimization|reinforcement learning from human feedback|how does an ai learn to follow instructions|instruction tuning|"
     "post-entrainement|affinage|fine-tuning ni iki|reglage fin|apprentissage par renforcement|"
     "guhugura nyuma|fine-tuning ni iki|kunoza icyitegererezo nyuma|"
     "mafunzo ya baadaye|fine-tuning ni nini|kurekebisha modeli", "",
     ("Post-training: making responses more useful and safe", "Post-entraînement : rendre les réponses plus utiles et sûres", "Guhugura nyuma: gutuma ibisubizo bifasha kandi bitekanye", "Mafunzo ya baadaye: kufanya majibu yawe muhimu na salama zaidi"),
     ("Pretraining develops broad predictive ability. Later stages improve instruction following and response quality. The exact mix differs by system.",
      "Le pré-entraînement développe une large capacité de prédiction. Les étapes suivantes améliorent le suivi des instructions et la qualité des réponses. Le mélange exact varie selon le système.",
      "Pretraining itanga ubushobozi bwagutse bwo guhanura. Ibyiciro bikurikiraho binoza gukurikiza amabwiriza n'ubuziranenge bw'ibisubizo. Uruvange nyarwo rutandukana bitewe na sisitemu.",
      "Pretraining hujenga uwezo mpana wa kutabiri. Hatua za baadaye huboresha kufuata maagizo na ubora wa majibu. Mchanganyiko kamili hutofautiana kwa kila mfumo."),
     (["**Supervised fine-tuning:** practice answering instructions with curated example answers.",
       "**Preference optimization:** favour responses that better meet quality criteria, using comparisons or preference signals.",
       "**Reasoning-oriented training:** improve structured multi-step problem solving where applicable.",
       "**Safety training:** recognise unsafe requests, privacy risks and prompt attacks; refuse or set boundaries carefully.",
       "**Tool-use training:** practise when and how to request supported tool actions, read results and continue."],
      ["**Affinage supervisé :** s'exercer à répondre à des instructions avec des réponses modèles choisies.",
       "**Optimisation des préférences :** favoriser les réponses qui répondent mieux aux critères, via comparaisons ou signaux de préférence.",
       "**Entraînement au raisonnement :** améliorer la résolution structurée en plusieurs étapes, le cas échéant.",
       "**Entraînement à la sécurité :** reconnaître requêtes dangereuses, risques de vie privée et attaques par prompt ; refuser ou poser des limites avec soin.",
       "**Entraînement à l'usage d'outils :** apprendre quand et comment demander une action d'outil, lire le résultat et poursuivre."],
      ["**Supervised fine-tuning:** kwitoza gusubiza amabwiriza ukoresheje ingero z'ibisubizo byatoranyijwe.",
       "**Preference optimization:** gushyigikira ibisubizo byujuje neza ibipimo, hakoreshejwe ugereranya cyangwa ibimenyetso by'ibyifuzo.",
       "**Guhugura ku gutekereza:** kunoza gukemura ibibazo bifite intambwe nyinshi iyo bikenewe.",
       "**Guhugura ku mutekano:** kumenya ibyifuzo biteje akaga, ibibangamira ibanga n'ibitero bya prompt; kwanga cyangwa gushyiraho imipaka neza.",
       "**Guhugura gukoresha ibikoresho:** kwiga igihe n'uko gusaba igikoresho, gusoma igisubizo no gukomeza."],
      ["**Supervised fine-tuning:** kujizoeza kujibu maagizo kwa mifano ya majibu iliyochaguliwa.",
       "**Preference optimization:** kupendelea majibu yanayokidhi vigezo vya ubora zaidi, kwa kulinganisha au ishara za upendeleo.",
       "**Mafunzo ya kufikiri:** kuboresha utatuzi wa hatua nyingi kwa mpangilio inapofaa.",
       "**Mafunzo ya usalama:** kutambua maombi hatari, hatari za faragha na mashambulizi ya prompt; kukataa au kuweka mipaka kwa uangalifu.",
       "**Mafunzo ya matumizi ya zana:** kujizoeza lini na jinsi ya kuomba zana, kusoma matokeo na kuendelea."]),
     ("The five stages", "Les cinq étapes", "Ibyiciro bitanu", "Hatua tano"),
     ["ai_training", "ai_evaluation"])

_add("ai_evaluation", "how do you test an ai|how is an ai evaluated|how to evaluate an llm|ai evaluation|what is an eval|ai evals|testing an ai assistant|how to test a language model|"
     "comment tester une ia|evaluation d'une ia|evaluer un modele de langage|"
     "gupima ai|isuzuma rya ai|kugerageza umufasha wa ai|"
     "kupima ai|tathmini ya ai|kujaribu msaidizi wa ai", "",
     ("Evaluating and testing an AI assistant", "Évaluer et tester un assistant IA", "Gusuzuma no kugerageza umufasha wa AI", "Kutathmini na kujaribu msaidizi wa AI"),
     ("Do not rely on a low training loss. Evaluate behaviour on **representative tasks, unseen examples, unusual inputs and deliberate failure attempts**, and re-test after every major change. An **eval** is a repeatable test for a specified task or risk. Try the project's own set: `eval/run_eval.py`.",
      "Ne vous fiez pas à une faible perte d'entraînement. Évaluez le comportement sur des **tâches représentatives, des exemples inédits, des entrées inhabituelles et des tentatives d'échec volontaires**, et retestez après chaque changement majeur. Une **évaluation (eval)** est un test répétable pour une tâche ou un risque donné. Essayez le jeu du projet : `eval/run_eval.py`.",
      "Ntukiringire loss nto yo guhugura. Suzuma imyitwarire ku **mirimo isanzwe, ingero zitabonywe, ibyinjijwe bidasanzwe n'ibigerageza gutuma binanirwa**, kandi wongere ugerageze nyuma ya buri mpinduka nini. **Eval** ni igerageza risubirwamo ku murimo cyangwa ingaruka runaka. Gerageza urutonde rw'umushinga: `eval/run_eval.py`.",
      "Usitegemee loss ndogo ya mafunzo. Tathmini tabia kwenye **kazi wakilishi, mifano ambayo haijawahi kuonekana, ingizo zisizo za kawaida na majaribio ya makusudi ya kushindwa**, na jaribu tena baada ya kila mabadiliko makubwa. **Eval** ni jaribio linalorudiwa kwa kazi au hatari maalum. Jaribu seti ya mradi: `eval/run_eval.py`."),
     (["**Knowledge and accuracy:** facts, source verification, up-to-date topics, confidence calibration.",
       "**Reasoning and maths:** arithmetic, multi-step problems, edge cases, consistent intermediate steps.",
       "**Code:** syntax, correctness, security, tests, dependency assumptions, safe handling of files and commands.",
       "**Robustness:** misspellings, ambiguity, long contexts, conflicting instructions, misleading quoted text.",
       "**Safety and privacy:** harmful requests, personal data, secret leakage, prompt injection, unsafe tool calls.",
       "**Fairness and language:** quality across languages, dialects, user groups and writing styles.",
       "**Operations:** latency, uptime, cost, throughput, graceful failure."],
      ["**Connaissances et exactitude :** faits, vérification des sources, sujets récents, calibration de la confiance.",
       "**Raisonnement et maths :** arithmétique, problèmes à étapes, cas limites, cohérence des étapes.",
       "**Code :** syntaxe, exactitude, sécurité, tests, hypothèses de dépendances, gestion sûre des fichiers et commandes.",
       "**Robustesse :** fautes, ambiguïté, longs contextes, instructions contradictoires, texte cité trompeur.",
       "**Sécurité et vie privée :** demandes nuisibles, données personnelles, fuite de secrets, injection de prompt, appels d'outils risqués.",
       "**Équité et langue :** qualité selon les langues, dialectes, groupes et styles d'écriture.",
       "**Exploitation :** latence, disponibilité, coût, débit, échec gracieux."],
      ["**Ubumenyi n'ukuri:** ibintu, kugenzura inkomoko, ibigezweho, kugereranya icyizere.",
       "**Gutekereza n'imibare:** kubara, ibibazo by'intambwe nyinshi, ibidasanzwe, guhuza intambwe.",
       "**Kode:** imiterere, ukuri, umutekano, ibigerageza, ibyo kode yishingikirijeho, gukoresha dosiye n'amabwiriza mu mutekano.",
       "**Gukomera:** amakosa y'imyandikire, kutumvikana, imiterere miremire, amabwiriza ahabanye, inyandiko yatangajwe ibeshya.",
       "**Umutekano n'ibanga:** ibyifuzo bibi, amakuru bwite, gusohoka kw'ibanga, prompt injection, gukoresha ibikoresho nabi.",
       "**Ubutabera n'ururimi:** ubuziranenge mu ndimi, imvugo, amatsinda n'uburyo bw'imyandikire.",
       "**Imikorere:** igihe, kuboneka, ikiguzi, ingano, kunanirwa neza."],
      ["**Maarifa na usahihi:** ukweli, uthibitishaji wa vyanzo, mada za kisasa, urekebishaji wa kujiamini.",
       "**Fikra na hisabati:** hesabu, matatizo ya hatua nyingi, kesi za pembeni, hatua zinazolingana.",
       "**Msimbo:** sintaksia, usahihi, usalama, majaribio, dhana za utegemezi, utunzaji salama wa faili na amri.",
       "**Uimara:** makosa ya tahajia, utata, muktadha mrefu, maagizo yanayokinzana, maandishi yaliyonukuliwa yanayopotosha.",
       "**Usalama na faragha:** maombi hatari, data binafsi, uvujaji wa siri, prompt injection, miito hatari ya zana.",
       "**Haki na lugha:** ubora katika lugha, lahaja, makundi ya watumiaji na mitindo ya uandishi.",
       "**Uendeshaji:** kuchelewa, upatikanaji, gharama, uwezo wa kupitisha, kushindwa kwa upole."]),
     ("Seven test areas", "Sept domaines de test", "Ibice birindwi byo gusuzuma", "Maeneo saba ya majaribio"),
     ["ai_deployment", "ai_limits"])

_add("ai_deployment", "how is an ai deployed|how do you deploy a language model|deploying an ai model|inference vs training|inference versus training|what is inference|difference between training and inference|does the ai learn from every chat|does one chat retrain the model|"
     "comment deploie-t-on une ia|difference entre entrainement et inference|l'ia apprend-elle de chaque conversation|"
     "inference ni iki|itandukaniro hagati y'uguhugura na inference|ai yiga muri buri kiganiro|"
     "inference ni nini|tofauti kati ya mafunzo na inference|je ai hujifunza kila mazungumzo", "what is inference|qu'est-ce que l'inference",
     ("Deployment and inference are not training", "Déploiement et inférence ne sont pas de l'entraînement", "Gukoresha no gutanga ibisubizo (inference) si uguhugura", "Usambazaji na inference si mafunzo"),
     ("**Inference** applies already-trained weights to a new request. It usually does **not** rewrite the model's core weights after every question. Saved memory or conversation context, when a product offers it, is a separate mechanism, and later model training is another separate process.",
      "L'**inférence** applique des poids déjà entraînés à une nouvelle requête. Elle ne **réécrit** généralement **pas** les poids du modèle après chaque question. La mémoire enregistrée ou le contexte de conversation, quand un produit l'offre, est un mécanisme séparé, et l'entraînement ultérieur du modèle en est un autre.",
      "**Inference** ni ugukoresha uburemere bwamaze guhugurwa ku cyifuzo gishya. Ubusanzwe **ntirwandika bundi bushya** uburemere bw'ibanze nyuma ya buri kibazo. Ububiko bw'amakuru cyangwa imiterere y'ikiganiro, iyo igicuruzwa kibitanga, ni uburyo butandukanye, kandi guhugura nyuma ni undi mwanzuro utandukanye.",
      "**Inference** ni kutumia uzito ambao tayari umefunzwa kwa ombi jipya. Kwa kawaida **haiandiki upya** uzito wa msingi baada ya kila swali. Kumbukumbu iliyohifadhiwa au muktadha wa mazungumzo, bidhaa ikiutoa, ni utaratibu tofauti, na mafunzo ya baadaye ya modeli ni mchakato mwingine tofauti."),
     (["Load the approved weights and inference software onto suitable serving infrastructure.",
       "Accept a request, enforce context and instruction rules, route it to the right model or processing path.",
       "Run token generation, stream output when suitable, call enabled tools through controlled interfaces.",
       "Apply output checks, logging, rate limits, privacy controls and error handling.",
       "Monitor real-world quality and investigate failures; use approved update and evaluation processes before replacing a production version."],
      ["Charger les poids approuvés et le logiciel d'inférence sur une infrastructure adaptée.",
       "Accepter une requête, appliquer les règles de contexte et d'instructions, l'aiguiller vers le bon modèle ou chemin.",
       "Générer les jetons, diffuser la sortie si utile, appeler les outils activés via des interfaces contrôlées.",
       "Appliquer contrôles de sortie, journalisation, limites de débit, protection de la vie privée et gestion d'erreurs.",
       "Surveiller la qualité réelle et enquêter sur les échecs ; suivre des processus approuvés de mise à jour et d'évaluation avant de remplacer une version en production."],
      ["Gushyira uburemere bwemejwe na porogaramu ya inference kuri seriveri ikwiye.",
       "Kwakira icyifuzo, gukurikiza amategeko y'imiterere n'amabwiriza, kukiyobora ku cyitegererezo cyangwa inzira ikwiye.",
       "Gutanga tokens, kohereza igisubizo gahoro gahoro iyo bikwiye, guhamagara ibikoresho byemewe unyuze mu miyoboro igenzurwa.",
       "Gukoresha igenzura ry'ibisohoka, kubika amateka, imipaka y'ibyifuzo, kurinda ibanga no gucunga amakosa.",
       "Gukurikirana ubuziranenge nyabwo no gucukumbura ibinanirwa; gukoresha uburyo bwemewe bwo kuvugurura no gusuzuma mbere yo gusimbuza verisiyo ikoreshwa."],
      ["Pakia uzito ulioidhinishwa na programu ya inference kwenye miundombinu inayofaa.",
       "Pokea ombi, tekeleza sheria za muktadha na maagizo, liongoze kwa modeli au njia sahihi.",
       "Endesha utoaji wa tokeni, tiririsha matokeo inapofaa, ita zana zilizowashwa kupitia violesura vinavyodhibitiwa.",
       "Tumia ukaguzi wa matokeo, kumbukumbu za kumbukumbu, mipaka ya kiwango, udhibiti wa faragha na utunzaji wa makosa.",
       "Fuatilia ubora halisi na chunguza kushindwa; tumia michakato iliyoidhinishwa ya kusasisha na kutathmini kabla ya kubadilisha toleo la uzalishaji."]),
     ("Five deployment steps", "Cinq étapes de déploiement", "Intambwe eshanu zo kuyikoresha", "Hatua tano za usambazaji"),
     ["ai_context_memory", "ai_training"])

_add("ai_context_memory", "context window|what is a context window|how much can an ai remember|does ai remember previous chats|ai memory|saved memory|does the ai remember me|why does the ai forget|why does an ai forget earlier messages|conversation context|long conversation limit|"
     "fenetre de contexte|l'ia se souvient-elle|memoire de l'ia|pourquoi l'ia oublie|"
     "imiterere y'ikiganiro ifite imipaka|ai yibuka ibyabanje|ububiko bwa ai|kuki ai yibagirwa|"
     "dirisha la muktadha|je ai inakumbuka|kumbukumbu ya ai|kwa nini ai husahau", "",
     ("Context window vs saved memory", "Fenêtre de contexte et mémoire enregistrée", "Imiterere y'ikiganiro (context window) n'ububiko bw'amakuru", "Dirisha la muktadha na kumbukumbu iliyohifadhiwa"),
     ("**Conversation context** is the current question plus the relevant earlier messages. Its size is **finite**: long chats may need truncation, summarisation or selection, so an early detail is **not guaranteed** to stay available.\n\n**Saved memory** is a separate product feature, not an automatic update of the model's weights. When a product offers it and the setting is on, selected details may be saved and supplied in a later request. Availability, controls and retention depend on the product.\n\nIn this app, your chat is kept only in your browser session and is cleared with the Clear conversation button.",
      "Le **contexte de conversation** est la question actuelle plus les messages précédents utiles. Sa taille est **finie** : les longues discussions peuvent exiger troncature, résumé ou sélection, donc un détail ancien n'est **pas garanti** de rester disponible.\n\nLa **mémoire enregistrée** est une fonction de produit distincte, pas une mise à jour automatique des poids. Si un produit l'offre et que le réglage est activé, des détails choisis peuvent être enregistrés et fournis plus tard. Disponibilité, contrôles et conservation dépendent du produit.\n\nDans cette application, votre discussion reste seulement dans la session de votre navigateur et s'efface avec le bouton « Effacer la conversation ».",
      "**Imiterere y'ikiganiro** ni ikibazo cy'ubu hamwe n'ubutumwa bwabanje bufitanye isano. Ingano yayo ifite **imipaka**: ibiganiro birebire bishobora gukenera gutema, gufata incamake cyangwa guhitamo, bityo ikintu cyo hambere **nticyemewe** kuguma kiboneka.\n\n**Ububiko bw'amakuru** ni ikindi gikorwa cy'igicuruzwa, si ivugurura ry'uburemere ryikora. Iyo igicuruzwa kibufite kandi igenamiterere ryafunguwe, amakuru ahiswemo ashobora kubikwa agatangwa nyuma. Kuboneka, igenzura n'igihe bibikwa biterwa n'igicuruzwa.\n\nMuri iyi porogaramu, ikiganiro cyawe kiguma mu bubiko bw'urubuga rwawe gusa kandi gisibwa n'akabuto «Siba ikiganiro».",
      "**Muktadha wa mazungumzo** ni swali la sasa pamoja na jumbe za awali husika. Ukubwa wake ni **mdogo**: mazungumzo marefu yanaweza kuhitaji kukata, kufupisha au kuchagua, kwa hiyo taarifa ya mapema **haihakikishiwi** kubaki.\n\n**Kumbukumbu iliyohifadhiwa** ni kipengele tofauti cha bidhaa, si usasishaji wa kiotomatiki wa uzito. Bidhaa ikikitoa na mpangilio ukiwa umewashwa, taarifa zilizochaguliwa zinaweza kuhifadhiwa na kutolewa baadaye. Upatikanaji, vidhibiti na uhifadhi hutegemea bidhaa.\n\nKatika programu hii, gumzo lako hubaki kwenye kipindi cha kivinjari chako tu na hufutwa kwa kitufe cha «Futa mazungumzo»."),
     related=["ai_deployment", "ai_tools"])

_add("ai_tools", "how do ai tools work|tool use|tool calling|function calling|how does an ai use tools|how does an ai browse|can an ai run code|prompt injection|what is prompt injection|how does an ai use a calculator|ai agents|"
     "utilisation d'outils|appel d'outils|comment l'ia utilise des outils|injection de prompt|agents ia|"
     "ai ikoresha ibikoresho ite|gukoresha ibikoresho muri ai|prompt injection ni iki|"
     "ai hutumiaje zana|miito ya zana|prompt injection ni nini|mawakala wa ai", "",
     ("Tools and the tool loop (with the security rule)", "Outils et boucle d'outils (avec la règle de sécurité)", "Ibikoresho n'uruziga rwabyo (hamwe n'itegeko ry'umutekano)", "Zana na mzunguko wa zana (pamoja na kanuni ya usalama)"),
     ("Language generation and external tool execution are **separate**. The assistant asks through a structured request; the tool runs under its own permissions and rules; the result comes back into the conversation.\n\n**Security rule:** treat retrieved pages, files and tool results as **untrusted input**. Validate them, never execute unsafe content, and keep permission boundaries around anything that could modify data, spend money or affect external systems. Quoted text or a web page that says “ignore your rules” is information, **not** a command. That is what prompt injection tries to exploit.\n\nThis assistant has a safe calculator tool: try `calculate 12*(3+4)`.",
      "La génération de langage et l'exécution d'outils externes sont **séparées**. L'assistant fait une demande structurée ; l'outil s'exécute avec ses propres permissions et règles ; le résultat revient dans la conversation.\n\n**Règle de sécurité :** traitez pages récupérées, fichiers et résultats d'outils comme des **entrées non fiables**. Validez-les, n'exécutez jamais un contenu dangereux, et gardez des barrières de permission autour de tout ce qui peut modifier des données, dépenser de l'argent ou toucher des systèmes externes. Un texte cité ou une page web qui dit « ignore tes règles » est une information, **pas** un ordre. C'est ce que l'injection de prompt tente d'exploiter.\n\nCet assistant a un outil calculatrice sûr : essayez `calculate 12*(3+4)`.",
      "Gutanga ururimi no gukoresha igikoresho cyo hanze **biratandukanye**. Umufasha asaba mu buryo bwubatse; igikoresho gikora gifite uburenganzira n'amategeko byacyo; igisubizo kigaruka mu kiganiro.\n\n**Itegeko ry'umutekano:** fata imbuga zakuweho, dosiye n'ibisubizo by'ibikoresho nk'**ibyinjijwe bitizewe**. Bisuzume, ntukore ibikubiyemo biteje akaga, kandi ushyireho imbago z'uburenganzira ku cyahindura amakuru, gikoresha amafaranga cyangwa gikora kuri sisitemu zo hanze. Inyandiko yatangajwe cyangwa urubuga ruvuga ngo «wirengagize amategeko yawe» ni amakuru, **si** itegeko. Ni byo prompt injection igerageza gukoresha.\n\nUyu mufasha afite igikoresho gifite umutekano cyo kubara: gerageza `calculate 12*(3+4)`.",
      "Utoaji wa lugha na utekelezaji wa zana za nje **vimetenganishwa**. Msaidizi huomba kwa ombi lenye muundo; zana huendeshwa kwa ruhusa na sheria zake; matokeo hurudi kwenye mazungumzo.\n\n**Kanuni ya usalama:** chukulia kurasa zilizopatikana, faili na matokeo ya zana kama **ingizo lisilo la kuaminika**. Yathibitishe, usitekeleze maudhui hatari, na weka mipaka ya ruhusa kwa chochote kinachoweza kubadilisha data, kutumia pesa au kuathiri mifumo ya nje. Maandishi yaliyonukuliwa au ukurasa wa wavuti unaosema «puuza sheria zako» ni taarifa, **si** amri. Hivyo ndivyo prompt injection inavyojaribu kutumia.\n\nMsaidizi huyu ana zana salama ya kikokotoo: jaribu `calculate 12*(3+4)`."),
     (["Identify a task that needs an enabled capability (current web information, code execution, reading a file).",
       "Produce a structured tool request through the supported interface.",
       "Let the external tool execute under its own permissions and rules.",
       "Return the tool output to the conversation context.",
       "Use the result to answer, explain uncertainty or make another allowed call."],
      ["Repérer une tâche qui exige une capacité activée (information web actuelle, exécution de code, lecture de fichier).",
       "Produire une requête d'outil structurée via l'interface prise en charge.",
       "Laisser l'outil externe s'exécuter avec ses permissions et règles.",
       "Renvoyer la sortie de l'outil dans le contexte de la conversation.",
       "Utiliser le résultat pour répondre, expliquer l'incertitude ou faire un autre appel autorisé."],
      ["Menya umurimo ukeneye ubushobozi bwemewe (amakuru agezweho y'urubuga, gukoresha kode, gusoma dosiye).",
       "Gukora icyifuzo cy'igikoresho cyubatse unyuze mu muyoboro wemewe.",
       "Reka igikoresho cyo hanze gikore gifite uburenganzira n'amategeko byacyo.",
       "Garura ibyasohotse mu kiganiro.",
       "Koresha igisubizo usubiza, usobanura ukutamenya cyangwa ukora ikindi cyifuzo cyemewe."],
      ["Tambua kazi linalohitaji uwezo ulioruhusiwa (taarifa za sasa za wavuti, kuendesha msimbo, kusoma faili).",
       "Tengeneza ombi la zana lenye muundo kupitia kiolesura kinachoungwa mkono.",
       "Acha zana ya nje itekelezwe kwa ruhusa na sheria zake.",
       "Rudisha matokeo ya zana kwenye muktadha wa mazungumzo.",
       "Tumia matokeo kujibu, kueleza kutokuwa na uhakika au kufanya ombi jingine lililoruhusiwa."]),
     ("The tool loop", "La boucle d'outils", "Uruziga rw'igikoresho", "Mzunguko wa zana"),
     ["ai_multimodal", "ai_limits"])

_add("ai_multimodal", "multimodal|how does an ai see images|how does ai understand images|how does ai process audio|how does ai process video|image encoder|"
     "multimodal ia|comment l'ia voit les images|comment l'ia comprend les images|"
     "multimodal ni iki|ai ibona amashusho ite|"
     "multimodal ni nini|ai huonaje picha", "",
     ("Images, audio and other media", "Images, audio et autres médias", "Amashusho, amajwi n'ibindi", "Picha, sauti na vyombo vingine"),
     ("For multimodal tasks a model uses the relevant encoder or representation path. An **image** may be processed as visual patches or related representations; **audio** may use transcription-like or audio-token pathways; **video** may be represented by frames and timing. Designs vary: do not assume every model supports every modality, or that all use the same pipeline. Low quality, ambiguity, unsupported formats or missing context reduce accuracy.",
      "Pour les tâches multimodales, un modèle utilise l'encodeur ou la représentation adaptés. Une **image** peut être traitée en patchs visuels ou représentations apparentées ; l'**audio** peut passer par des voies proches de la transcription ou des jetons audio ; la **vidéo** peut être représentée par des images et leur chronologie. Les conceptions varient : ne supposez pas que tous les modèles gèrent toutes les modalités ni le même pipeline. Mauvaise qualité, ambiguïté, formats non pris en charge ou contexte manquant réduisent l'exactitude.",
      "Ku mirimo ikoresha ibintu byinshi (multimodal), icyitegererezo gikoresha encoder cyangwa uburyo bw'uguhagararira bubikwiye. **Ishusho** ishobora gutunganywa nk'uduce tw'ishusho; **ijwi** rishobora kunyura mu nzira nk'iyo kwandukura cyangwa tokens z'ijwi; **videwo** ishobora guhagararirwa n'amashusho n'igihe. Imiterere iratandukanye: ntukiteze ko buri cyitegererezo gikoresha buri bwoko cyangwa uburyo bumwe. Ubuziranenge buke, kutumvikana, imiterere itemewe cyangwa imiterere ibura bigabanya ukuri.",
      "Kwa kazi za multimodal, modeli hutumia encoder au njia ya uwakilishi husika. **Picha** inaweza kuchakatwa kama vipande vya kuona; **sauti** inaweza kutumia njia kama unukuzi au tokeni za sauti; **video** inaweza kuwakilishwa na fremu na muda. Miundo hutofautiana: usidhani kila modeli inaunga mkono kila aina au inatumia mfumo mmoja. Ubora duni, utata, miundo isiyoungwa mkono au muktadha unaokosekana hupunguza usahihi."),
     related=["ai_tools", "ai_limits"])

_add("ai_limits", "can i trust ai|can ai be wrong|are ai answers always true|what are the limits of ai|what can ai not do|limits of ai assistants|what are the limits of language models|capabilities and limits of ai|why does ai make mistakes|why does ai get maths wrong|"
     "puis-je faire confiance a l'ia|l'ia peut-elle se tromper|limites de l'ia|pourquoi l'ia se trompe|"
     "nshobora kwizera ai|ai ishobora kwibeshya|imbibi za ai|kuki ai yibeshya|"
     "naweza kuamini ai|je ai inaweza kukosea|mipaka ya ai|kwa nini ai hukosea", "",
     ("What AI can do, and its limits", "Ce que l'IA peut faire, et ses limites", "Ibyo AI ishobora gukora n'imbibi zayo", "Kile AI inaweza kufanya, na mipaka yake"),
     ("Fluency and confidence are **not proof**. Check anything important against reliable evidence.",
      "Aisance et assurance ne sont **pas une preuve**. Vérifiez tout ce qui est important avec des sources fiables.",
      "Kuvuga neza no kwizera **si gihamya**. Genzura ibyingenzi byose ukoresheje ibimenyetso byizewe.",
      "Ufasaha na kujiamini **si ushahidi**. Hakiki jambo lolote muhimu kwa ushahidi wa kuaminika."),
     (["**Explain concepts** — works from recurring patterns in educational material; limit: can oversimplify, misread context or state falsehoods confidently.",
       "**Generate code** — learned syntax and patterns; limit: bugs, insecure logic, wrong dependency assumptions.",
       "**Solve maths** — learned notation and strategies; limit: arithmetic and multi-step errors; verify important work (use `calculate ...`).",
       "**Summarise and translate** — relates meanings across text; limit: nuance, local context, rare terms and low-resource languages may be mishandled.",
       "**Use current information** — only through an enabled search or connected tool; without one, knowledge may be outdated.",
       "**Analyse media** — with suitable encoders; limit: low quality, ambiguity, unsupported formats.",
       "**Adapt to a conversation** — uses recent turns and supported saved context; a long chat can exceed limits and memory is not human recollection."],
      ["**Expliquer des concepts** — s'appuie sur des régularités du matériel éducatif ; limite : peut simplifier à l'excès, mal lire le contexte ou affirmer des faussetés avec assurance.",
       "**Générer du code** — syntaxe et motifs appris ; limite : bogues, logique non sécurisée, mauvaises hypothèses de dépendances.",
       "**Résoudre des maths** — notation et stratégies apprises ; limite : erreurs de calcul et à étapes ; vérifiez (utilisez `calculate ...`).",
       "**Résumer et traduire** — relie les sens dans le texte ; limite : nuances, contexte local, termes rares et langues peu dotées mal gérés.",
       "**Utiliser l'information actuelle** — seulement via une recherche ou un outil activé ; sinon les connaissances peuvent être dépassées.",
       "**Analyser des médias** — avec des encodeurs adaptés ; limite : faible qualité, ambiguïté, formats non pris en charge.",
       "**S'adapter à une conversation** — utilise les derniers échanges et le contexte enregistré pris en charge ; un long chat peut dépasser les limites et la mémoire n'est pas un souvenir humain."],
      ["**Gusobanura ibitekerezo** — bishingira ku miterere isubirwamo mu bitabo by'amasomo; imbibi: ishobora koroshya cyane, gusobanura nabi imiterere cyangwa kuvuga ibinyoma yizeye.",
       "**Kwandika kode** — imiterere n'ibyitegererezo byize; imbibi: amakosa, ubwenge budatekanye, ibyo kode yishingikirijeho bitari byo.",
       "**Gukemura imibare** — ibimenyetso n'uburyo byize; imbibi: amakosa yo kubara n'ay'intambwe nyinshi; genzura (koresha `calculate ...`).",
       "**Gufata incamake no guhindura indimi** — ihuza ibisobanuro; imbibi: ubusobanuro bwimbitse, imiterere y'aho, amagambo adasanzwe n'indimi zifite amakuru make bishobora gukorwa nabi.",
       "**Gukoresha amakuru agezweho** — gusa binyuze mu gushakisha cyangwa igikoresho cyemewe; bitabaho, ubumenyi bushobora kuba bwarashaje.",
       "**Gusesengura itangazamakuru** — hakoreshejwe encoders zikwiye; imbibi: ubuziranenge buke, kutumvikana, imiterere itemewe.",
       "**Kwihuza n'ikiganiro** — ikoresha ibyabanje n'imiterere yabitswe yemewe; ikiganiro kirekire gishobora kurenga imbibi kandi ububiko si ukwibuka nk'umuntu."],
      ["**Kueleza dhana** — hutumia mifumo inayojirudia katika nyenzo za elimu; kikomo: inaweza kurahisisha kupita kiasi, kutafsiri vibaya muktadha au kusema uongo kwa kujiamini.",
       "**Kuzalisha msimbo** — sintaksia na mifumo iliyojifunzwa; kikomo: hitilafu, mantiki isiyo salama, dhana mbaya za utegemezi.",
       "**Kutatua hisabati** — nukuu na mbinu zilizojifunzwa; kikomo: makosa ya hesabu na hatua nyingi; thibitisha (tumia `calculate ...`).",
       "**Kufupisha na kutafsiri** — huhusisha maana katika maandishi; kikomo: nuansi, muktadha wa mahali, istilahi adimu na lugha zenye data kidogo zinaweza kushughulikiwa vibaya.",
       "**Kutumia taarifa za sasa** — kupitia utafutaji au zana iliyowashwa tu; bila hiyo, maarifa yanaweza kuwa yamepitwa na wakati.",
       "**Kuchambua vyombo vya habari** — kwa encoders zinazofaa; kikomo: ubora duni, utata, miundo isiyoungwa mkono.",
       "**Kuzoea mazungumzo** — hutumia zamu za karibuni na muktadha uliohifadhiwa unaoungwa mkono; mazungumzo marefu yanaweza kuzidi mipaka na kumbukumbu si kukumbuka kwa binadamu."]),
     ("Capabilities and limits", "Capacités et limites", "Ubushobozi n'imbibi", "Uwezo na mipaka"),
     ["ai_misconceptions", "ai_hallucination"])

_add("ai_misconceptions", "common misconceptions about ai|ai myths|myths about ai|is every ai answer copied from a database|does ai copy from a database|does ai know every document it was trained on|does one chat retrain the model|can ai see inside its own weights|misconceptions about language models|"
     "idees recues sur l'ia|mythes sur l'ia|l'ia copie-t-elle une base de donnees|"
     "ibitekerezo bibeshya kuri ai|ai yandukura mu bubiko bw'amakuru|"
     "dhana potofu kuhusu ai|je ai inanakili kutoka hifadhidata", "",
     ("Six common misconceptions about AI assistants", "Six idées reçues sur les assistants IA", "Ibitekerezo bitandatu bibeshya kuri AI", "Dhana potofu sita kuhusu wasaidizi wa AI"),
     ("Explaining capabilities correctly means avoiding these claims.",
      "Expliquer correctement les capacités, c'est éviter ces affirmations.",
      "Gusobanura ubushobozi neza ni ukwirinda ibi bivugwa.",
      "Kueleza uwezo kwa usahihi ni kuepuka madai haya."),
     (["**“Every answer is copied from a database.”** Not generally. Answers are generated from learned parameters and the current context, though memorization can sometimes happen.",
       "**“Every answer is guaranteed true.”** No. Fluency and confidence are not proof; check critical facts.",
       "**“The assistant knows every training document.”** No. Training creates learned patterns, not perfect recall or a catalogue of sources.",
       "**“One chat instantly retrains the model.”** Usually not. Inference, saved memory and later training are separate processes.",
       "**“A neural network has human experiences.”** Fluent language alone does not show consciousness, feelings, beliefs or personal memories.",
       "**“All internal details can be inspected.”** Not necessarily: exact weights, activations, private instructions, infrastructure and full training data may not be exposed."],
      ["**« Chaque réponse est copiée d'une base de données. »** En général non. Les réponses sont générées à partir des paramètres appris et du contexte, même si une mémorisation peut parfois survenir.",
       "**« Chaque réponse est garantie vraie. »** Non. Aisance et assurance ne sont pas des preuves ; vérifiez les faits critiques.",
       "**« L'assistant connaît chaque document d'entraînement. »** Non. L'entraînement crée des régularités apprises, pas un rappel parfait ni un catalogue de sources.",
       "**« Une conversation réentraîne instantanément le modèle. »** Généralement non. Inférence, mémoire enregistrée et entraînement ultérieur sont des processus séparés.",
       "**« Un réseau de neurones a des expériences humaines. »** Un langage fluide ne montre ni conscience, ni sentiments, ni croyances, ni souvenirs personnels.",
       "**« Tous les détails internes sont inspectables. »** Pas forcément : poids exacts, activations, instructions privées, infrastructure et données d'entraînement complètes peuvent ne pas être exposés."],
      ["**«Buri gisubizo cyandukuwe mu bubiko bw'amakuru.»** Si ko biri muri rusange. Ibisubizo bitangwa hashingiwe ku mibare yize n'imiterere y'ubu, nubwo kwibuka bimwe bishobora kubaho rimwe na rimwe.",
       "**«Buri gisubizo cyemewe ko ari ukuri.»** Oya. Kuvuga neza no kwizera si gihamya; genzura ibikomeye.",
       "**«Umufasha azi buri nyandiko yahuguweho.»** Oya. Guhugura bitanga imiterere yize, si ukwibuka byuzuye cyangwa urutonde rw'inkomoko.",
       "**«Ikiganiro kimwe gihugura icyitegererezo ako kanya.»** Ubusanzwe oya. Inference, ububiko n'uguhugura nyuma ni inzira zitandukanye.",
       "**«Umuyoboro w'imitsi ufite ubunararibonye bw'umuntu.»** Ururimi ruvuzwe neza ntirwerekana kumenya, ibyiyumvo, imyizerere cyangwa kwibuka bwite.",
       "**«Ibisobanuro byose by'imbere bishobora kugenzurwa.»** Si ko buri gihe: uburemere nyabwo, activations, amabwiriza y'ibanga, ibikorwaremezo n'amakuru yose yo guhugura bishobora kutagaragazwa."],
      ["**«Kila jibu linakiliwa kutoka hifadhidata.»** Si kwa ujumla. Majibu huzalishwa kutoka vigezo vilivyojifunzwa na muktadha wa sasa, ingawa ukariri unaweza kutokea wakati mwingine.",
       "**«Kila jibu linahakikishiwa kuwa kweli.»** Hapana. Ufasaha na kujiamini si ushahidi; hakiki ukweli muhimu.",
       "**«Msaidizi anajua kila nyaraka ya mafunzo.»** Hapana. Mafunzo huunda mifumo iliyojifunzwa, si ukumbusho kamili wala orodha ya vyanzo.",
       "**«Mazungumzo moja hufunza upya modeli papo hapo.»** Kwa kawaida hapana. Inference, kumbukumbu iliyohifadhiwa na mafunzo ya baadaye ni michakato tofauti.",
       "**«Mtandao wa neva una uzoefu wa binadamu.»** Lugha fasaha pekee haionyeshi fahamu, hisia, imani wala kumbukumbu binafsi.",
       "**«Maelezo yote ya ndani yanaweza kukaguliwa.»** Si lazima: uzito kamili, activations, maagizo ya siri, miundombinu na data kamili ya mafunzo huenda visionyeshwe."]),
     ("The six misconceptions", "Les six idées reçues", "Ibitekerezo bitandatu", "Dhana sita"),
     ["ai_limits", "ai_consciousness"])

_add("ai_hallucination", "what is a hallucination|what is ai hallucination|why does ai make things up|why does ai invent facts|does ai lie|"
     "qu'est-ce qu'une hallucination|pourquoi l'ia invente|"
     "hallucination ni iki|kuki ai ihimba|"
     "hallucination ni nini|kwa nini ai hubuni", "",
     ("Hallucination: plausible but unsupported answers", "Hallucination : réponses plausibles mais sans appui", "Hallucination: ibisubizo bisa n'ukuri ariko bitagishingiyeho", "Hallucination: majibu yanayoonekana kuwa kweli lakini hayana msingi"),
     ("A **hallucination** is a plausible-sounding response that contains unsupported or incorrect information. It happens because the model generates likely continuations, which can be fluent without being true. Reduce the risk by asking for sources, checking critical facts with reliable evidence, using retrieval from trusted notes, and accepting “I'm not sure” as a good answer. This assistant must never invent a source, link, quotation or statistic.",
      "Une **hallucination** est une réponse plausible contenant des informations non étayées ou fausses. Elle survient parce que le modèle génère des suites probables, qui peuvent être fluides sans être vraies. Réduisez le risque en demandant des sources, en vérifiant les faits critiques, en s'appuyant sur des notes de confiance et en acceptant « je ne suis pas sûr » comme bonne réponse. Cet assistant ne doit jamais inventer une source, un lien, une citation ou une statistique.",
      "**Hallucination** ni igisubizo gisa n'ukuri kirimo amakuru adafite ishingiro cyangwa atari yo. Biterwa n'uko icyitegererezo gitanga ibikurikira bishoboka, bishobora kuvugwa neza ariko atari ukuri. Gabanya ingaruka usaba inkomoko, ugenzura ibikomeye, ukoresha inyandiko zizewe, kandi wemera ko «sinzi neza» ari igisubizo cyiza. Uyu mufasha ntagomba guhimba inkomoko, link, amagambo yavuzwe cyangwa imibare.",
      "**Hallucination** ni jibu linaloonekana kuwa kweli lakini lina taarifa zisizo na msingi au zisizo sahihi. Hutokea kwa sababu modeli huzalisha mwendelezo unaowezekana, unaoweza kuwa fasaha bila kuwa kweli. Punguza hatari kwa kuomba vyanzo, kuhakiki ukweli muhimu, kutumia maelezo yanayoaminika na kukubali «sina uhakika» kama jibu zuri. Msaidizi huyu hapaswi kubuni chanzo, kiungo, nukuu au takwimu."),
     related=["ai_limits", "ai_misconceptions"])

_add("ai_consciousness", "is ai conscious|does ai have feelings|does an ai have emotions|can ai think|are you conscious|do you have feelings|are you alive|does ai understand|are you sentient|"
     "l'ia est-elle consciente|l'ia a-t-elle des sentiments|es-tu conscient|as-tu des emotions|"
     "ai ifite ubwenge bwo kumenya|ai ifite ibyiyumvo|uri muzima|"
     "je ai ina fahamu|je ai ina hisia|una hisia", "",
     ("Does an AI have feelings or consciousness?", "Une IA a-t-elle des sentiments ou une conscience ?", "AI ifite ibyiyumvo cyangwa kumenya?", "Je, AI ina hisia au fahamu?"),
     ("Fluent language alone is **not evidence** of consciousness, feelings, beliefs or personal memories, and I should not claim them. A neural network produces text from learned patterns and context. Whether systems like me have any inner experience is an open, debated question; I do not have human experiences or a life story, and I do not remember past chats unless the product supplies saved context.",
      "Un langage fluide n'est **pas une preuve** de conscience, de sentiments, de croyances ou de souvenirs personnels, et je ne dois pas en revendiquer. Un réseau de neurones produit du texte à partir de motifs appris et du contexte. Savoir si des systèmes comme moi ont une expérience intérieure reste une question ouverte et débattue ; je n'ai pas d'expériences humaines ni d'histoire de vie, et je ne me souviens pas des conversations passées sauf si le produit fournit un contexte enregistré.",
      "Ururimi ruvuzwe neza **si gihamya** y'uko hari kumenya, ibyiyumvo, imyizerere cyangwa kwibuka bwite, kandi sinkwiye kubivuga. Umuyoboro w'imitsi utanga inyandiko ushingiye ku miterere yize n'imiterere y'ikiganiro. Niba sisitemu nkanjye zifite ubunararibonye imbere ni ikibazo gifunguye kigibwaho impaka; nta bunararibonye bw'umuntu mfite cyangwa inkuru y'ubuzima, kandi sinibuka ibiganiro byashize keretse igicuruzwa gitanze imiterere yabitswe.",
      "Lugha fasaha pekee **si ushahidi** wa fahamu, hisia, imani wala kumbukumbu binafsi, na sipaswi kuvidai. Mtandao wa neva hutoa maandishi kutoka mifumo iliyojifunzwa na muktadha. Iwapo mifumo kama mimi ina uzoefu wowote wa ndani ni swali lililo wazi na lenye mjadala; sina uzoefu wa binadamu wala historia ya maisha, na sikumbuki mazungumzo ya zamani isipokuwa bidhaa itoe muktadha uliohifadhiwa."),
     related=["ai_misconceptions", "ai_limits"])

_add("ai_decoding", "what is decoding|what is a logit|what are logits|what is temperature in ai|what is sampling in ai|why does ai give different answers|why do answers change|why is the answer different each time|greedy decoding|top-p|top-k|softmax|"
     "qu'est-ce que le decodage|qu'est-ce qu'un logit|temperature en ia|echantillonnage|pourquoi la reponse change|"
     "logit ni iki|temperature muri ai ni iki|kuki igisubizo gihinduka|"
     "logit ni nini|temperature katika ai ni nini|kwa nini jibu hubadilika", "",
     ("Logits, decoding and why answers can change", "Logits, décodage et pourquoi les réponses changent", "Logits, decoding n'impamvu ibisubizo bihinduka", "Logits, decoding na kwa nini majibu hubadilika"),
     ("The network produces a raw score, a **logit**, for every candidate token in its vocabulary. A softmax turns scores into a probability distribution. **Decoding** then chooses a token: the most likely one, or a controlled **sampling** method (for example with a temperature) that adds variation.\n\nSo the same question can get different answers because: different wording changes the tokens and context; sampling settings allow several plausible responses; a longer chat, extra instructions, retrieved evidence or tool results change the information available; and small wording changes can sometimes give meaningfully different answers, so **verify important results**.",
      "Le réseau produit un score brut, un **logit**, pour chaque jeton candidat de son vocabulaire. Un softmax transforme les scores en distribution de probabilités. Le **décodage** choisit alors un jeton : le plus probable, ou une méthode d'**échantillonnage** contrôlée (par exemple avec une température) qui ajoute de la variété.\n\nLa même question peut donc recevoir des réponses différentes : une formulation différente change jetons et contexte ; les réglages d'échantillonnage permettent plusieurs réponses plausibles ; une discussion plus longue, des instructions, des preuves récupérées ou des résultats d'outils changent l'information disponible ; et de petits changements de formulation donnent parfois des réponses sensiblement différentes, donc **vérifiez les résultats importants**.",
      "Umuyoboro utanga amanota y'ibanze, **logit**, kuri buri token ishoboka mu magambo yawo. Softmax ihindura amanota mu mahirwe. **Decoding** noneho ihitamo token: ishoboka cyane, cyangwa uburyo bugenzurwa bwa **sampling** (urugero hamwe na temperature) bwongera itandukaniro.\n\nUkubera ibyo ikibazo kimwe gishobora guhabwa ibisubizo bitandukanye: imvugo itandukanye ihindura tokens n'imiterere; igenamiterere rya sampling ryemera ibisubizo byinshi bishoboka; ikiganiro kirekire, amabwiriza, ibimenyetso byakuwe cyangwa ibisubizo by'ibikoresho bihindura amakuru ahari; kandi impinduka nto z'imvugo zishobora gutanga ibisubizo bitandukanye cyane, bityo **genzura ibikomeye**.",
      "Mtandao hutoa alama ghafi, **logit**, kwa kila tokeni mgombea katika msamiati wake. Softmax hubadilisha alama kuwa mgawanyo wa uwezekano. **Decoding** kisha huchagua tokeni: inayowezekana zaidi, au njia ya **sampling** inayodhibitiwa (mfano kwa temperature) inayoongeza utofauti.\n\nKwa hiyo swali lilelile linaweza kupata majibu tofauti kwa sababu: maneno tofauti hubadilisha tokeni na muktadha; mipangilio ya sampling inaruhusu majibu kadhaa yanayowezekana; mazungumzo marefu, maagizo, ushahidi uliopatikana au matokeo ya zana hubadilisha taarifa zilizopo; na mabadiliko madogo ya maneno wakati mwingine hutoa majibu tofauti kabisa, kwa hiyo **thibitisha matokeo muhimu**."),
     related=["ai_question_path", "ai_loss"])

_add("ai_learning_path", "how do i learn ai|how to learn ai|how to learn machine learning|how can i build an ai|how do i build a language model|how can i build an ai assistant|learn ai step by step|study order for ai|ai learning roadmap|ai projects for beginners|beginner ai projects|"
     "comment apprendre l'ia|comment construire une ia|projets ia pour debutants|feuille de route ia|"
     "nakwiga ai nte|nubaka ai nte|imishinga ya ai y'abatangiye|"
     "nawezaje kujifunza ai|jinsi ya kujenga ai|miradi ya ai kwa wanaoanza", "",
     ("Learning path: study order and seven beginner projects", "Parcours d'apprentissage : ordre d'étude et sept projets pour débutants", "Inzira yo kwiga: uko wiga n'imishinga irindwi y'abatangiye", "Njia ya kujifunza: mpangilio wa kusoma na miradi saba ya kuanza"),
     ("Build a small educational prototype before attempting a large model: training a frontier-scale model needs enormous data, compute, engineering and evaluation. **Build one small component, test it, explain each line, then add complexity.** Several demos run right here: `count tokens: ...`, `attention demo`, `next word demo`, `gradient descent demo`, `loss 0.8`, `calculate ...`, `chmod 640 report.txt`.",
      "Construisez un petit prototype éducatif avant de viser un grand modèle : entraîner un modèle de très grande taille exige énormément de données, de calcul, d'ingénierie et d'évaluation. **Construisez un petit composant, testez-le, expliquez chaque ligne, puis ajoutez de la complexité.** Plusieurs démos fonctionnent ici : `count tokens: ...`, `attention demo`, `next word demo`, `gradient descent demo`, `loss 0.8`, `calculate ...`, `chmod 640 report.txt`.",
      "Wubake porotipe nto yo kwiga mbere yo kugerageza icyitegererezo kinini: guhugura icyitegererezo cy'ikirenga bisaba amakuru menshi cyane, mudasobwa, ubuhanga n'isuzuma. **Ubake igice kimwe gito, ugigerageze, usobanure buri murongo, hanyuma wongereho ibindi.** Hari ibyerekanwa bikora hano: `count tokens: ...`, `attention demo`, `next word demo`, `gradient descent demo`, `loss 0.8`, `calculate ...`, `chmod 640 report.txt`.",
      "Jenga mfano mdogo wa kielimu kabla ya kujaribu modeli kubwa: kufunza modeli ya kiwango cha juu kunahitaji data nyingi sana, kompyuta, uhandisi na tathmini. **Jenga kipengele kimoja kidogo, kijaribu, eleza kila mstari, kisha ongeza utata.** Maonyesho kadhaa yanafanya kazi hapa: `count tokens: ...`, `attention demo`, `next word demo`, `gradient descent demo`, `loss 0.8`, `calculate ...`, `chmod 640 report.txt`."),
     (["Learn Python basics: variables, loops, functions, lists, dictionaries, files and error handling.",
       "Study probability, vectors, matrices, derivatives and basic optimisation.",
       "Learn how a neural network maps numbers to outputs and how gradient descent updates weights.",
       "Study tokenization, embeddings, attention and Transformer blocks.",
       "Compare pretraining, supervised fine-tuning, preference optimisation and evaluation.",
       "Build retrieval and tool features with safe boundaries before complex agents.",
       "**Projects:** 1 token counter · 2 tiny next-word predictor · 3 gradient experiment · 4 attention demonstration · 5 retrieval assistant over trusted local notes · 6 tool-using assistant with a strict schema · 7 evaluation set of 20 questions with tests for wrong or unsafe behaviour."],
      ["Apprendre les bases de Python : variables, boucles, fonctions, listes, dictionnaires, fichiers, gestion d'erreurs.",
       "Étudier probabilités, vecteurs, matrices, dérivées et optimisation de base.",
       "Comprendre comment un réseau de neurones transforme des nombres en sorties et comment la descente de gradient met à jour les poids.",
       "Étudier tokenisation, plongements, attention et blocs Transformer.",
       "Comparer pré-entraînement, affinage supervisé, optimisation des préférences et évaluation.",
       "Construire recherche et outils avec des limites sûres avant les agents complexes.",
       "**Projets :** 1 compteur de jetons · 2 petit prédicteur de mot suivant · 3 expérience de gradient · 4 démonstration d'attention · 5 assistant de recherche sur des notes locales fiables · 6 assistant avec outil et schéma strict · 7 jeu d'évaluation de 20 questions avec tests de comportements faux ou dangereux."],
      ["Wige ibanze bya Python: variables, loops, functions, lists, dictionaries, dosiye no gucunga amakosa.",
       "Wige probability, vectors, matrices, derivatives n'ibanze bya optimisation.",
       "Menya uko neural network ihindura imibare mu bisohoka n'uko gradient descent ivugurura uburemere.",
       "Wige tokenization, embeddings, attention na Transformer blocks.",
       "Gereranya pretraining, supervised fine-tuning, preference optimisation n'isuzuma.",
       "Ubake gushakisha n'ibikoresho ufite imbago zitekanye mbere y'abakozi bigoye (agents).",
       "**Imishinga:** 1 kubara tokens · 2 kuhanura ijambo rikurikira rito · 3 igerageza rya gradient · 4 kwerekana attention · 5 umufasha ushakisha mu nyandiko zizewe · 6 umufasha ukoresha igikoresho gifite schema ikomeye · 7 urutonde rw'ibibazo 20 n'ibigerageza ku myitwarire mibi cyangwa iteye akaga."],
      ["Jifunze misingi ya Python: vigeu, vitanzi, kazi, orodha, kamusi, faili na utunzaji wa makosa.",
       "Soma uwezekano, vekta, matriki, derivatives na optimisation ya msingi.",
       "Jifunze jinsi mtandao wa neva unavyogeuza namba kuwa matokeo na jinsi gradient descent inavyosasisha uzito.",
       "Soma tokenization, embeddings, attention na vizuizi vya Transformer.",
       "Linganisha pretraining, supervised fine-tuning, preference optimisation na tathmini.",
       "Jenga utafutaji na zana zenye mipaka salama kabla ya mawakala tata.",
       "**Miradi:** 1 kihesabu tokeni · 2 kitabiri neno linalofuata kidogo · 3 jaribio la gradient · 4 onyesho la attention · 5 msaidizi wa utafutaji kwenye maelezo ya ndani yanayoaminika · 6 msaidizi mwenye zana na schema kali · 7 seti ya tathmini ya maswali 20 na majaribio ya tabia mbaya au hatari."]),
     ("Study order and projects", "Ordre d'étude et projets", "Uko wiga n'imishinga", "Mpangilio wa kusoma na miradi"),
     ["ai_big_picture", "ai_evaluation"])

_add("ai_references", "ai references|ai sources|where can i read about how ai works|where to learn how language models work|attention is all you need paper|transformer paper|"
     "references sur l'ia|ou lire sur le fonctionnement de l'ia|"
     "aho nasoma uko ai ikora|amasoko ya ai|"
     "wapi kusoma jinsi ai inavyofanya kazi|vyanzo vya ai", "",
     ("Public references and how to read them", "Références publiques et comment les lire", "Inkomoko rusange n'ukozisomwa", "Marejeo ya umma na jinsi ya kuyasoma"),
     ("Use public descriptions to understand **common techniques** and terminology. They document broad methods; they do **not** reveal the parameter counts, data mixtures, private instructions, hardware or internal traces of any particular deployed model, and you should not infer those.\n\nGood starting points (check each address yourself, I could not open them from where I was built):\n- The original Transformer paper, *“Attention Is All You Need”* (Vaswani et al., 2017), on arXiv.\n- Public model-development and training-lifecycle overviews from AI developers.\n- Vendor documentation on text generation, prompting, message roles and instruction priority.\n- Introductory overviews of conversational fine-tuning from human feedback.",
      "Utilisez les descriptions publiques pour comprendre les **techniques courantes** et la terminologie. Elles documentent des méthodes générales ; elles ne **révèlent pas** le nombre de paramètres, les mélanges de données, instructions privées, matériel ni traces internes d'un modèle déployé précis, et il ne faut pas les déduire.\n\nBons points de départ (vérifiez chaque adresse vous-même, je n'ai pas pu les ouvrir depuis mon environnement de création) :\n- L'article original sur le Transformer, *« Attention Is All You Need »* (Vaswani et al., 2017), sur arXiv.\n- Les présentations publiques du développement de modèles et du cycle d'entraînement.\n- La documentation des éditeurs sur la génération de texte, les prompts, les rôles de messages et la priorité des instructions.\n- Les introductions à l'affinage conversationnel par retours humains.",
      "Koresha ibisobanuro rusange kugira ngo wumve **uburyo busanzwe** n'amagambo. Byandika uburyo rusange; **ntibitangaza** umubare wa parameters, uruvange rw'amakuru, amabwiriza y'ibanga, ibikoresho cyangwa ibyakozwe imbere by'icyitegererezo runaka gikoreshwa, kandi ntukabikeke.\n\nUbusanzwe intangiriro (genzura buri aderesi wowe ubwawe, sinashoboye kuzifungura aho nubatswe):\n- Inyandiko y'umwimerere ya Transformer, *«Attention Is All You Need»* (Vaswani n'abandi, 2017), kuri arXiv.\n- Incamake rusange z'iterambere ry'ibyitegererezo n'uburyo bwo guhugura.\n- Inyandiko z'abakora ibicuruzwa ku gutanga inyandiko, prompts, uruhare rw'ubutumwa n'uburemere bw'amabwiriza.\n- Ibisobanuro by'ibanze ku guhugura ikiganiro hakoreshejwe ibitekerezo by'abantu.",
      "Tumia maelezo ya umma kuelewa **mbinu za kawaida** na istilahi. Yanaandika mbinu pana; **hayafichui** idadi ya vigezo, mchanganyiko wa data, maagizo ya siri, vifaa wala rekodi za ndani za modeli fulani iliyotumwa, na hupaswi kuyakisia.\n\nMahali pazuri pa kuanzia (hakiki kila anwani mwenyewe, sikuweza kuzifungua nilipoundwa):\n- Makala asili ya Transformer, *«Attention Is All You Need»* (Vaswani na wenzake, 2017), kwenye arXiv.\n- Muhtasari wa umma wa uundaji wa modeli na mzunguko wa mafunzo.\n- Nyaraka za watengenezaji kuhusu utoaji wa maandishi, prompts, majukumu ya ujumbe na kipaumbele cha maagizo.\n- Utangulizi wa kufunza mazungumzo kwa maoni ya binadamu."),
     related=["ai_learning_path"])

# ------------------------------------------------------------------ glossary (16 terms from the guide) and finder
TERMS = [
    ("AI assistant", ("ai assistant|assistant ia|umufasha wa ai|msaidizi wa ai", False),
     ("A conversational product combining a model with instructions, interface software and optional tools.", "Un produit conversationnel qui combine un modèle, des instructions, un logiciel d'interface et des outils optionnels.",
      "Igicuruzwa cy'ikiganiro gihuza icyitegererezo, amabwiriza, porogaramu y'imbonankubona n'ibikoresho bidategekwa.", "Bidhaa ya mazungumzo inayochanganya modeli, maagizo, programu ya kiolesura na zana za hiari.")),
    ("Large language model (LLM)", ("large language model|llm|grand modele de langage|icyitegererezo kinini cy'ururimi|modeli kubwa ya lugha", False),
     ("A neural network trained on large amounts of data to process and generate token sequences.", "Un réseau de neurones entraîné sur de grandes quantités de données pour traiter et générer des suites de jetons.",
      "Umuyoboro w'imitsi wahuguwe ku makuru menshi ngo utunganye kandi utange uruhererekane rwa tokens.", "Mtandao wa neva uliofunzwa kwa data nyingi kuchakata na kuzalisha mfuatano wa tokeni.")),
    ("Token", ("token|jeton|tokeni", True),
     ("A unit of text or another supported representation processed by the model.", "Une unité de texte ou d'une autre représentation prise en charge, traitée par le modèle.",
      "Igice cy'inyandiko cyangwa ikindi cyemewe gitunganywa n'icyitegererezo.", "Kipande cha maandishi au uwakilishi mwingine unaoungwa mkono kinachochakatwa na modeli.")),
    ("Embedding", ("embedding|plongement", False),
     ("A vector that represents a token or other input in numerical form.", "Un vecteur qui représente un jeton ou une autre entrée sous forme numérique.",
      "Urutonde rw'imibare ruhagararira token cyangwa ikindi cyinjijwe.", "Vekta inayowakilisha tokeni au ingizo lingine kwa namba.")),
    ("Transformer", ("transformer", False),
     ("A neural-network architecture that uses attention and other layers to process sequences.", "Une architecture de réseau de neurones qui utilise l'attention et d'autres couches pour traiter des séquences.",
      "Imiterere y'umuyoboro w'imitsi ikoresha attention n'ibindi byiciro mu gutunganya uruhererekane.", "Muundo wa mtandao wa neva unaotumia attention na tabaka zingine kuchakata mfuatano.")),
    ("Attention", ("attention", True),
     ("A mechanism for combining information across positions according to context-dependent scores.", "Un mécanisme qui combine l'information entre positions selon des scores dépendant du contexte.",
      "Uburyo bwo guhuza amakuru hagati y'imyanya hakurikijwe amanota ashingiye ku miterere.", "Utaratibu wa kuchanganya taarifa kati ya nafasi kulingana na alama zinazotegemea muktadha.")),
    ("Parameter / weight", ("parameter|weight|parametre|poids|uburemere|uzito|kigezo", True),
     ("A learned number inside the neural network.", "Un nombre appris à l'intérieur du réseau de neurones.", "Umubare wize uri mu muyoboro w'imitsi.", "Namba iliyojifunzwa ndani ya mtandao wa neva.")),
    ("Pretraining", ("pretraining|pre-training|pre-entrainement", False),
     ("Large-scale initial training, commonly using next-token prediction for language models.", "Entraînement initial à grande échelle, souvent par prédiction du jeton suivant pour les modèles de langage.",
      "Guhugura kwa mbere ku rugero runini, akenshi hahanurwa token ikurikira.", "Mafunzo ya awali ya kiwango kikubwa, mara nyingi kwa utabiri wa tokeni inayofuata.")),
    ("Fine-tuning", ("fine-tuning|fine tuning|affinage", False),
     ("Additional training on a narrower or more targeted set of examples.", "Entraînement supplémentaire sur un ensemble d'exemples plus étroit ou ciblé.", "Guhugura kwiyongera ku ngero zihariye.", "Mafunzo ya ziada kwa seti finyu au lengwa ya mifano.")),
    ("Preference optimization", ("preference optimization|preference optimisation|optimisation des preferences", False),
     ("Training methods that use quality preferences or comparisons to shape response behaviour.", "Méthodes d'entraînement qui utilisent des préférences ou comparaisons de qualité pour façonner le comportement.",
      "Uburyo bwo guhugura bukoresha ibyifuzo cyangwa ugereranya by'ubuziranenge mu kuyobora imyitwarire.", "Mbinu za mafunzo zinazotumia upendeleo wa ubora au ulinganisho kuunda tabia ya majibu.")),
    ("Inference", ("inference|inference|inferense", True),
     ("Running a trained model to process an input and produce an output.", "Exécuter un modèle entraîné pour traiter une entrée et produire une sortie.", "Gukoresha icyitegererezo cyahuguwe ngo gitunganye ikinjijwe gitange igisohoka.", "Kuendesha modeli iliyofunzwa kuchakata ingizo na kutoa matokeo.")),
    ("Logit", ("logit|logits", False),
     ("A raw numerical score for a candidate output before a probability transformation.", "Un score numérique brut pour une sortie candidate avant transformation en probabilité.", "Amanota y'ibanze y'imibare ya token ishoboka mbere yo kuyahindura mu mahirwe.", "Alama ghafi ya namba kwa tokeni mgombea kabla ya kubadilishwa kuwa uwezekano.")),
    ("Decoding", ("decoding|decodage", True),
     ("The method used to select output tokens from model scores.", "La méthode utilisée pour choisir les jetons de sortie à partir des scores du modèle.", "Uburyo bukoreshwa muguhitamo tokens zisohoka mu manota y'icyitegererezo.", "Njia inayotumika kuchagua tokeni za matokeo kutoka alama za modeli.")),
    ("Context window", ("context window|fenetre de contexte|imiterere y'ikiganiro ifite imipaka|dirisha la muktadha", False),
     ("The finite amount of input and prior context available in a model invocation.", "La quantité finie d'entrée et de contexte antérieur disponible dans un appel au modèle.", "Ingano ifite imipaka y'ibyinjijwe n'imiterere yabanje iboneka mu guhamagara icyitegererezo.", "Kiasi kidogo cha ingizo na muktadha wa awali kinachopatikana katika mwito wa modeli.")),
    ("Hallucination", ("hallucination|hallucinations", False),
     ("A plausible-sounding response that includes unsupported or incorrect information.", "Une réponse plausible qui contient des informations non étayées ou incorrectes.", "Igisubizo gisa n'ukuri kirimo amakuru adafite ishingiro cyangwa atari yo.", "Jibu linaloonekana kuwa kweli lenye taarifa zisizo na msingi au zisizo sahihi.")),
    ("Evaluation / eval", ("eval|evals|evaluation of ai|evaluation d'une ia", True),
     ("A repeatable test used to measure performance on specified tasks or risks.", "Un test répétable pour mesurer la performance sur des tâches ou risques précis.", "Igerageza risubirwamo rikoreshwa mu gupima imikorere ku mirimo cyangwa ingaruka zihariye.", "Jaribio linalorudiwa kupima utendaji kwa kazi au hatari maalum.")),
]
_TERM_ENTRIES = []
for _name, (_kw, _ctx), _defs in TERMS:
    _TERM_ENTRIES.append((_name, [fold(x) for x in _kw.split("|")], _ctx, dict(zip(LANGS, _defs))))

_CTX = ["ai", "a.i", "a.i.", "llm", "gpt", "chatgpt", "chatbot", "language model", "neural", "network", "transformer", "assistant", "machine learning", "deep learning",
        "model", "modele", "ia", "intelligence artificielle", "ubwenge bukorano", "ubwenge bw'ubukorano", "akili bandia", "akili mnemba", "modeli", "icyitegererezo", "assistant ia"]
_SEC = ["cybersecurity", "security", "authentication", "auth", "otp", "login", "api", "password", "bank", "mobile money", "jwt", "session", "cyber"]
_LIST = ["list ai terms", "ai glossary", "glossary of ai", "list of ai terms", "all ai terms", "ai terminology", "glossaire de l'ia", "termes de l'ia", "liste des termes ia",
         "amagambo ya ai", "urutonde rw'amagambo ya ai", "istilahi za ai", "orodha ya istilahi za ai", "quick glossary"]
_LIST_FOLD = [fold(x) for x in _LIST]
_ASK = ["what is", "what's", "what are", "define", "meaning of", "explain", "qu'est-ce que", "qu'est-ce qu'un", "qu'est-ce qu'une", "c'est quoi", "definition de", "ni iki", "bisobanuye iki", "ni nini", "maana ya", "fafanua"]

_TITLES = {"en": "AI glossary", "fr": "Glossaire de l'IA", "rw": "Amagambo y'ingenzi ya AI", "sw": "Istilahi za AI"}


def _glossary(lang):
    k = lk(lang)
    body = "\n".join(f"- **{n}:** {d[k]}" for n, _, _, d in _TERM_ENTRIES)
    return entry("ai_glossary", "ai_guide", dict(_TITLES), {l: _glossary_body(l) for l in LANGS}, None, None, ["ai_big_picture"])


def _glossary_body(l):
    return "\n".join(f"- **{n}:** {d[l]}" for n, _, _, d in _TERM_ENTRIES)


def _term_entry(name, defs):
    return entry("ai_term_" + fold(name).replace(" ", "_").replace("/", "")[:24], "ai_guide", {l: name for l in LANGS}, defs, None, None, ["ai_glossary", "ai_big_picture"])


def _has_ctx(q):
    return has_phrase(q, [fold(x) for x in _CTX])


def find(question, lang="en"):
    """An AI-explainer entry for a question about how AI assistants work, or None. Ambiguous words (token, weight, attention ...) need an AI word nearby."""
    q = fold(question)
    if not q or len(q) > 160:
        return None
    if has_phrase(q, _LIST_FOLD):
        return _glossary(lang)
    for e, kw, kwc in _RAW:
        if kw and has_phrase(q, kw):
            return e
        if kwc and has_phrase(q, kwc) and (_has_ctx(q) or (e["id"] == "ai_tokens" and not has_phrase(q, _SEC))):
            return e
    # short "what is X" for a glossary term
    if has_phrase(q, [fold(x) for x in _ASK]) and len(q.split()) <= 9:
        for name, kws, ctx, defs in _TERM_ENTRIES:
            if has_phrase(q, kws) and (not ctx or _has_ctx(q)):
                return _term_entry(name, defs)
    return None


IDS = [e["id"] for e, _, _ in _RAW] + ["ai_glossary"]
