"""AI image generation, explained and coached in four languages, built from the owner's "AI Image Generation Techniques Guide":
the creation process, the 12 techniques, the ingredients of a strong prompt, weak vs strong prompts, composition, improving a first result,
common problems and fixes, training, what can and cannot be claimed, a practice plan, a glossary and further reading.
Pure Python, offline. IMPORTANT: this app explains and writes/checks prompts; it does not itself generate pictures (no image model is connected),
and it never claims private details of any commercial model. fr/rw/sw wording is a DRAFT for review by fluent speakers."""
from __future__ import annotations
from textutil import fold, has_phrase, lk, entry, LANGS

NOT_GEN = {
    "en": "Note: this assistant explains image generation and writes or checks prompts for you; it does not draw pictures itself. Paste the prompt into the image tool you use.",
    "fr": "Note : cet assistant explique la génération d'images et rédige ou vérifie vos prompts ; il ne dessine pas lui-même. Collez le prompt dans l'outil d'image que vous utilisez.",
    "rw": "Icyitonderwa: uyu mufasha asobanura gukora amashusho akoresheje AI kandi yandika cyangwa agenzura prompts zawe; ntashushanya ubwe. Shyira prompt mu gikoresho cy'amashusho ukoresha.",
    "sw": "Kumbuka: msaidizi huyu anaeleza uzalishaji wa picha na kuandika au kukagua prompts zako; hachori picha mwenyewe. Bandika prompt kwenye zana ya picha unayotumia.",
}
BOUNDARY = {
    "en": "These are techniques common across the field. The exact architecture, training data, sampler and safety system of any particular commercial model may be private, may change, and cannot be independently verified here. No prompt formula guarantees a perfect result.",
    "fr": "Ce sont des techniques courantes du domaine. L'architecture exacte, les données d'entraînement, l'échantillonneur et le système de sécurité d'un modèle commercial précis peuvent être privés, changer, et ne sont pas vérifiables ici. Aucune formule de prompt ne garantit un résultat parfait.",
    "rw": "Ubu ni uburyo busanzwe muri uru rwego. Imiterere nyayo, amakuru yo guhugura, sampler n'uburyo bw'umutekano by'icyitegererezo cyihariye bishobora kuba ibanga, bishobora guhinduka, kandi ntibishobora kugenzurwa hano. Nta formule ya prompt yemeza ibisubizo byuzuye.",
    "sw": "Hizi ni mbinu za kawaida katika uwanja huu. Muundo kamili, data ya mafunzo, sampler na mfumo wa usalama wa modeli fulani ya kibiashara vinaweza kuwa vya siri, vinaweza kubadilika, na haviwezi kuthibitishwa hapa. Hakuna fomula ya prompt inayohakikisha matokeo kamilifu.",
}

_RAW = []


def _add(id_, kw, kwc, title, answer, steps=None, label=None, related=None, boundary=False, photo=None):
    st = {l: list(steps[i]) if steps else [] for i, l in enumerate(LANGS)}
    ans = dict(zip(LANGS, answer))
    tail = {l: "\n\n_" + (BOUNDARY[l] if boundary else "") + "_" for l in LANGS}
    if boundary:
        ans = {l: ans[l] + tail[l] for l in LANGS}
    e = entry(id_, "image_guide", dict(zip(LANGS, title)), ans, st, dict(zip(LANGS, label)) if label else None, related)
    if photo:
        e["photo_query"] = photo
    _RAW.append((e, [fold(x) for x in kw.split("|") if x], [fold(x) for x in kwc.split("|") if x]))


# ---------------------------------------------------------------- 1. the process
_add("img_process",
     "how does ai image generation work|how do ai image generators work|how does ai create images|how does ai make pictures|how are ai images made|image creation process|process of ai image generation|how does an ai draw|text to image|text-to-image|"
     "comment fonctionne la generation d'images|comment l'ia cree des images|comment l'ia genere des images|processus de creation d'image|"
     "ai ikora amashusho ite|uko ai ikora amashusho|ai ishushanya ite|"
     "ai inatengenezaje picha|uzalishaji wa picha kwa ai|ai huchora vipi", "",
     ("How AI creates an image: the seven steps", "Comment l'IA crée une image : les sept étapes", "Uko AI ikora ishusho: intambwe zirindwi", "Jinsi AI inavyounda picha: hatua saba"),
     ("This is a high-level workflow, not a disclosure of every private implementation detail. Different systems use different architectures and stages. Related ideas: `explain diffusion`, `image prompt ingredients`, `improve prompt: your idea`.",
      "C'est un flux de travail général, pas la divulgation de chaque détail privé d'implémentation. Les systèmes diffèrent par leurs architectures et étapes. Voir aussi : `explain diffusion`, `image prompt ingredients`, `improve prompt: votre idée`.",
      "Iyi ni gahunda rusange, si ugutangaza buri kantu k'ibanga ko gushyira mu bikorwa. Sisitemu zitandukanye zikoresha imiterere n'intambwe zitandukanye. Reba kandi: `explain diffusion`, `image prompt ingredients`, `improve prompt: igitekerezo cyawe`.",
      "Huu ni mtiririko wa ngazi ya juu, si ufichuzi wa kila undani wa siri wa utekelezaji. Mifumo tofauti hutumia miundo na hatua tofauti. Angalia pia: `explain diffusion`, `image prompt ingredients`, `improve prompt: wazo lako`."),
     (["**Interpret the request:** subject, action, setting, mood, style, composition and format.",
       "**Build a visual plan:** what belongs in the foreground, middle ground and background.",
       "**Encode the prompt:** turn words into numbers a model can process.",
       "**Generate visual content:** a trained generative model creates an image consistent with the prompt.",
       "**Refine details:** learned patterns for shape, lighting, texture, colour, perspective and style.",
       "**Evaluate the result:** prompt accuracy, visual coherence and applicable safety constraints.",
       "**Return the image** through the user interface."],
      ["**Interpréter la demande :** sujet, action, décor, ambiance, style, composition et format.",
       "**Construire un plan visuel :** ce qui va au premier plan, au plan intermédiaire et à l'arrière-plan.",
       "**Encoder le prompt :** transformer les mots en nombres que le modèle sait traiter.",
       "**Générer le contenu visuel :** un modèle génératif entraîné crée une image cohérente avec le prompt.",
       "**Affiner les détails :** motifs appris pour formes, lumière, texture, couleur, perspective et style.",
       "**Évaluer le résultat :** fidélité au prompt, cohérence visuelle et contraintes de sécurité applicables.",
       "**Renvoyer l'image** via l'interface."],
      ["**Gusobanukirwa icyifuzo:** insanganyamatsiko, igikorwa, aho biri, umutima w'ishusho, uburyo, imiterere n'ingano.",
       "**Gukora igishushanyo mbonera:** ibijya imbere, hagati n'inyuma.",
       "**Guhindura prompt mu mibare:** guhindura amagambo mo imibare icyitegererezo gishobora gutunganya.",
       "**Gukora ishusho:** icyitegererezo cya generative cyahuguwe gikora ishusho ihuye na prompt.",
       "**Kunoza utuntu duto:** imiterere yize ku mashusho, urumuri, imiterere y'ubuso, amabara, perspective n'uburyo.",
       "**Gusuzuma ibyavuyemo:** ukuri kuri prompt, guhuza kw'ishusho n'amategeko y'umutekano akurikizwa.",
       "**Gusubiza ishusho** unyuze mu miyoboro y'ukoresha."],
      ["**Tafsiri ombi:** mada, kitendo, mazingira, hali, mtindo, muundo na umbizo.",
       "**Jenga mpango wa kuona:** nini kiende mbele, katikati na nyuma.",
       "**Simba prompt:** badilisha maneno kuwa namba ambazo modeli inaweza kuchakata.",
       "**Zalisha maudhui ya kuona:** modeli ya generative iliyofunzwa huunda picha inayolingana na prompt.",
       "**Boresha undani:** mifumo iliyojifunzwa ya umbo, mwanga, umbile, rangi, mtazamo na mtindo.",
       "**Tathmini matokeo:** usahihi wa prompt, mshikamano wa kuona na vikwazo vya usalama vinavyotumika.",
       "**Rudisha picha** kupitia kiolesura."]),
     ("The seven steps", "Les sept étapes", "Intambwe zirindwi", "Hatua saba"), ["img_techniques", "img_ingredients"], boundary=True)

# ---------------------------------------------------------------- 2. techniques (12)
_add("img_techniques",
     "main techniques of ai image generation|techniques of ai image generation|technical ideas behind ai image generation|image generation techniques|how are ai images generated technically|"
     "techniques de generation d'images|principales techniques de generation d'image|"
     "uburyo bwo gukora amashusho ya ai|ibyibanze bya tekiniki bya ai y'amashusho|"
     "mbinu za uzalishaji wa picha kwa ai|mbinu kuu za ai ya picha", "",
     ("The 12 main techniques behind AI image generation", "Les 12 techniques principales de la génération d'images par IA", "Uburyo 12 bukuru bwa AI ikora amashusho", "Mbinu kuu 12 za uzalishaji wa picha kwa AI"),
     ("Many systems combine several of these; not every model uses every technique (for example, not every image model uses diffusion). Ask about any one by name, e.g. `explain diffusion`, `what is latent space`, `what is inpainting`.",
      "Beaucoup de systèmes en combinent plusieurs ; tous les modèles n'utilisent pas chaque technique (par exemple, tous n'emploient pas la diffusion). Demandez-en une par son nom, p. ex. `explain diffusion`, `what is latent space`, `what is inpainting`.",
      "Sisitemu nyinshi zihuza nyinshi muri zo; si buri cyitegererezo gikoresha buri buryo (urugero, si buri cyose gikoresha diffusion). Baza kimwe ukoresheje izina ryacyo, urugero `explain diffusion`, `what is latent space`, `what is inpainting`.",
      "Mifumo mingi huchanganya kadhaa; si kila modeli hutumia kila mbinu (kwa mfano, si zote hutumia diffusion). Uliza moja kwa jina, mf. `explain diffusion`, `what is latent space`, `what is inpainting`."),
     (["**Machine learning:** learn visual patterns from examples instead of hand-writing a rule for every picture.",
       "**Neural networks:** layers of mathematical operations that turn input into features such as edges, shapes, objects, textures and relationships.",
       "**Text encoding:** words and phrases become numbers that keep meaning (“golden-hour light”, “misty forest”).",
       "**Diffusion and denoising:** learn to reverse a gradual noising process; start from noise and remove it step by step, guided by the prompt.",
       "**Latent-space generation:** work in a compressed representation, then decode to pixels, which saves computation.",
       "**Attention and cross-attention:** connect parts of the prompt to visual features (“red umbrella”, “rainy street”).",
       "**Image–text training:** learn associations between descriptions and pictures; data quality and diversity affect accuracy and bias.",
       "**Conditioning and controls:** guide with text, reference images, pose, depth, edge maps, masks or layouts, when the tool supports them.",
       "**Fine-tuning and preference alignment:** adapt a general model to a style, task or quality preference.",
       "**Upscaling and detail enhancement:** raise resolution or refine details; it cannot recover information that was never there.",
       "**Inpainting and editing:** change a selected region and keep the rest; masks mark what to replace, remove or extend.",
       "**Safety checks:** safeguards on requests and outputs, such as prompt screening and output checks; they vary by system."],
      ["**Apprentissage automatique :** apprendre des motifs visuels à partir d'exemples au lieu d'écrire une règle pour chaque image.",
       "**Réseaux de neurones :** couches d'opérations mathématiques qui transforment l'entrée en traits : bords, formes, objets, textures, relations.",
       "**Encodage du texte :** mots et phrases deviennent des nombres qui gardent le sens (« lumière dorée », « forêt brumeuse »).",
       "**Diffusion et débruitage :** apprendre à inverser un bruitage progressif ; partir du bruit et l'enlever pas à pas, guidé par le prompt.",
       "**Génération dans l'espace latent :** travailler dans une représentation compressée, puis décoder en pixels, ce qui économise du calcul.",
       "**Attention et attention croisée :** relier des parties du prompt à des traits visuels (« parapluie rouge », « rue pluvieuse »).",
       "**Entraînement image–texte :** apprendre les liens entre descriptions et images ; qualité et diversité des données influencent exactitude et biais.",
       "**Conditionnement et contrôles :** guider par texte, images de référence, pose, profondeur, cartes de contours, masques ou mises en page, si l'outil le permet.",
       "**Affinage et alignement sur les préférences :** adapter un modèle général à un style, une tâche ou une préférence de qualité.",
       "**Agrandissement et amélioration des détails :** augmenter la résolution ou affiner ; impossible de retrouver une information jamais présente.",
       "**Retouche (inpainting) et édition :** modifier une zone choisie et garder le reste ; les masques marquent ce qu'il faut remplacer, retirer ou étendre.",
       "**Contrôles de sécurité :** garde-fous sur les demandes et les sorties (filtrage des prompts, contrôle des sorties) ; ils varient selon le système."],
      ["**Machine learning:** kwiga imiterere y'amashusho mu ngero aho kwandika itegeko kuri buri shusho.",
       "**Neural networks:** ibyiciro by'ibikorwa by'imibare bihindura ibyinjijwe mu miterere nk'impande, imiterere, ibintu, imiterere y'ubuso n'isano.",
       "**Gufata inyandiko mu mibare:** amagambo n'interuro bihinduka imibare ibika ubusobanuro («urumuri rwa zahabu», «ishyamba ririmo igihu»).",
       "**Diffusion na denoising:** kwiga gusubiza inyuma uburyo bwo kongera urusaku buhoro buhoro; gutangira ku rusaku ukarukuraho intambwe ku yindi, uyobowe na prompt.",
       "**Gukora mu latent space:** gukorera mu buryo bugabanyije, hanyuma ugahindura mo pixels, bigabanya imibare.",
       "**Attention na cross-attention:** guhuza ibice bya prompt n'imiterere y'ishusho («umutaka utukura», «umuhanda urimo imvura»).",
       "**Guhugura ishusho–inyandiko:** kwiga isano hagati y'ibisobanuro n'amashusho; ubuziranenge n'ubwoko bw'amakuru bigira ingaruka ku kuri no ku kubogama.",
       "**Conditioning n'ibigenzura:** kuyobora hakoreshejwe inyandiko, amashusho y'ibisobanuro, uko umuntu ahagaze, ubujyakuzimu, ikarita y'impande, masks cyangwa imiterere, iyo igikoresho kibishyigikiye.",
       "**Fine-tuning n'ihuzwa n'ibyifuzo:** guhuza icyitegererezo rusange n'uburyo, umurimo cyangwa ibyifuzo by'ubuziranenge.",
       "**Upscaling no kunoza utuntu duto:** kongera ubuziranenge cyangwa kunoza; ntibishobora kugarura amakuru atigeze abaho.",
       "**Inpainting no guhindura:** guhindura agace gatoranyijwe ukabungabunga ibisigaye; masks zerekana ibyo gusimbuza, gukuraho cyangwa kwagura.",
       "**Igenzura ry'umutekano:** ingamba ku byifuzo no ku bisohoka, nko gusuzuma prompt n'ibisohoka; biratandukana hagati ya sisitemu."],
      ["**Machine learning:** kujifunza mifumo ya kuona kutoka mifano badala ya kuandika kanuni kwa kila picha.",
       "**Mitandao ya neva:** tabaka za shughuli za hisabati zinazogeuza ingizo kuwa vipengele kama kingo, maumbo, vitu, umbile na uhusiano.",
       "**Usimbaji wa maandishi:** maneno na vifungu huwa namba zinazohifadhi maana («mwanga wa dhahabu», «msitu wenye ukungu»).",
       "**Diffusion na denoising:** kujifunza kugeuza mchakato wa kuongeza kelele taratibu; kuanza na kelele na kuiondoa hatua kwa hatua, ukiongozwa na prompt.",
       "**Uzalishaji katika latent space:** kufanya kazi katika uwakilishi uliobanwa, kisha kusimbua kuwa pikseli, jambo linalopunguza hesabu.",
       "**Attention na cross-attention:** kuunganisha sehemu za prompt na vipengele vya kuona («mwavuli mwekundu», «barabara ya mvua»).",
       "**Mafunzo ya picha–maandishi:** kujifunza uhusiano kati ya maelezo na picha; ubora na utofauti wa data huathiri usahihi na upendeleo.",
       "**Conditioning na vidhibiti:** kuongoza kwa maandishi, picha rejea, mkao, kina, ramani za kingo, masks au mpangilio, zana ikiunga mkono.",
       "**Fine-tuning na upatanishi wa mapendeleo:** kurekebisha modeli ya jumla kwa mtindo, kazi au upendeleo wa ubora.",
       "**Upscaling na uboreshaji wa undani:** kuongeza ubora au kuboresha undani; haiwezi kurejesha taarifa ambayo haikuwepo kamwe.",
       "**Inpainting na uhariri:** kubadilisha eneo lililochaguliwa na kuacha kilichobaki; masks huonyesha cha kubadilisha, kuondoa au kupanua.",
       "**Ukaguzi wa usalama:** kinga kwa maombi na matokeo, kama uchujaji wa prompt na ukaguzi wa matokeo; hutofautiana kwa mfumo."]),
     ("The 12 techniques", "Les 12 techniques", "Uburyo 12", "Mbinu 12"), ["img_process", "img_diffusion"], boundary=True)

# ---------------------------------------------------------------- diffusion + latent + cross-attention (single explainers)
_add("img_diffusion",
     "explain diffusion|what is diffusion|diffusion model|diffusion models|denoising|what is denoising|how does diffusion work|stable diffusion|diffusion et debruitage|modele de diffusion|diffusion ni iki|diffusion ni nini|"
     "mfano wa diffusion|icyitegererezo cya diffusion", "",
     ("Diffusion and denoising", "Diffusion et débruitage", "Diffusion na denoising", "Diffusion na denoising"),
     ("Many modern image generators learn to **reverse a gradual corruption process**. Training adds noise to pictures in many steps and teaches the model to predict (and so remove) that noise. To create an image, start from **pure noise** and repeatedly remove a little noise, guided by the prompt, until a coherent image emerges. **Not every image model uses diffusion.** Try `denoising demo` for a tiny numeric example.",
      "Beaucoup de générateurs d'images modernes apprennent à **inverser un processus de dégradation progressive**. À l'entraînement, on ajoute du bruit aux images en de nombreuses étapes et on apprend au modèle à prédire (donc retirer) ce bruit. Pour créer une image, on part de **bruit pur** et on retire un peu de bruit à chaque étape, guidé par le prompt, jusqu'à une image cohérente. **Tous les modèles d'image n'utilisent pas la diffusion.** Essayez `denoising demo` pour un petit exemple chiffré.",
      "Abakora amashusho benshi ba none biga **gusubiza inyuma uburyo bwo kwangiza buhoro buhoro**. Mu guhugura, bongera urusaku ku mashusho mu ntambwe nyinshi bakigisha icyitegererezo guhanura (bityo gukuraho) urwo rusaku. Gukora ishusho, utangira ku **rusaku rutavangiye** ukarukuraho gake gake, uyobowe na prompt, kugeza ishusho ihuje ibonetse. **Si buri cyitegererezo cy'amashusho gikoresha diffusion.** Gerageza `denoising demo` ubone urugero rw'imibare.",
      "Vizalishaji vingi vya kisasa vya picha hujifunza **kugeuza mchakato wa uharibifu wa taratibu**. Katika mafunzo, kelele huongezwa kwenye picha kwa hatua nyingi na modeli hufundishwa kutabiri (na hivyo kuondoa) kelele hiyo. Kuunda picha, anza na **kelele safi** na uondoe kelele kidogo kidogo, ukiongozwa na prompt, hadi picha yenye mshikamano ipatikane. **Si kila modeli ya picha hutumia diffusion.** Jaribu `denoising demo` kwa mfano mdogo wa namba."),
     related=["img_latent", "img_crossattn"])

_add("img_latent", "latent space|what is latent space|latent diffusion|latent-space generation|espace latent|nini maana ya latent space|latent space ni iki|latent space ni nini", "",
     ("Latent-space generation", "Génération dans l'espace latent", "Gukora mu latent space", "Uzalishaji katika latent space"),
     ("Many systems generate inside a **compressed mathematical representation** called latent space, then **decode** it into pixels. That can reduce computation compared with generating every pixel directly. Try `latent demo 512x512` to see how much smaller an example latent can be (real systems differ).",
      "Beaucoup de systèmes génèrent dans une **représentation mathématique compressée** appelée espace latent, puis la **décodent** en pixels. Cela peut réduire le calcul par rapport à la génération directe de chaque pixel. Essayez `latent demo 512x512` pour voir de combien un latent d'exemple est plus petit (les vrais systèmes diffèrent).",
      "Sisitemu nyinshi zikorera mu **buryo bw'imibare bugabanyije** bwitwa latent space, hanyuma **bugahindurwa** mo pixels. Ibi bishobora kugabanya imibare ugereranyije no gukora buri pixel mu buryo butaziguye. Gerageza `latent demo 512x512` urebe urugero rw'uko latent iba nto (sisitemu nyazo ziratandukanye).",
      "Mifumo mingi huzalisha ndani ya **uwakilishi wa hisabati uliobanwa** unaoitwa latent space, kisha **husimbua** kuwa pikseli. Hilo linaweza kupunguza hesabu ikilinganishwa na kuzalisha kila pikseli moja kwa moja. Jaribu `latent demo 512x512` kuona jinsi latent ya mfano inavyokuwa ndogo (mifumo halisi hutofautiana)."),
     related=["img_diffusion"])

_add("img_crossattn", "cross-attention|cross attention|attention in image generation|how does the prompt connect to the image|how does ai connect words to pictures|attention croisee|cross-attention ni iki|cross-attention ni nini", "",
     ("Attention and cross-attention in images", "Attention et attention croisée en génération d'images", "Attention na cross-attention mu mashusho", "Attention na cross-attention katika picha"),
     ("Attention connects the **relevant parts of a prompt with visual features**: “red umbrella” links an umbrella with the colour red, and “rainy street” links to the surrounding environment. This is why precise wording (and not contradictory wording) helps. Related: `what is attention in ai`.",
      "L'attention relie les **parties pertinentes du prompt aux traits visuels** : « parapluie rouge » associe un parapluie et la couleur rouge, « rue pluvieuse » renvoie à l'environnement. C'est pourquoi des mots précis (et non contradictoires) aident. Voir aussi : `what is attention in ai`.",
      "Attention ihuza **ibice bifitanye isano bya prompt n'imiterere y'ishusho**: «umutaka utukura» uhuza umutaka n'ibara ritukura, «umuhanda urimo imvura» uhuza n'ibiwukikije. Ni yo mpamvu amagambo asobanutse (kandi adahabanye) afasha. Reba: `what is attention in ai`.",
      "Attention huunganisha **sehemu husika za prompt na vipengele vya kuona**: «mwavuli mwekundu» huunganisha mwavuli na rangi nyekundu, «barabara ya mvua» huunganisha na mazingira yanayozunguka. Ndiyo maana maneno sahihi (na yasiyokinzana) husaidia. Angalia: `what is attention in ai`."),
     related=["img_diffusion", "img_ingredients"])

# ---------------------------------------------------------------- 3. prompt ingredients
_add("img_ingredients",
     "image prompt ingredients|ingredients of a strong image prompt|what makes a good image prompt|how to write a good image prompt|how to write an image prompt|how do i write a prompt for ai images|prompt engineering for images|good prompt for ai image|strong image prompt|how to describe an image to ai|"
     "ingredients d'un bon prompt d'image|comment ecrire un bon prompt d'image|comment ecrire un prompt pour une image|bon prompt pour image|"
     "uko wandika prompt nziza y'ishusho|ibigize prompt ikomeye y'ishusho|"
     "jinsi ya kuandika prompt nzuri ya picha|viungo vya prompt imara ya picha", "",
     ("Ingredients of a strong image prompt (12)", "Ingrédients d'un bon prompt d'image (12)", "Ibigize prompt ikomeye y'ishusho (12)", "Viungo vya prompt imara ya picha (12)"),
     ("Use a clear order and include important details **without conflicting instructions**. Then try `improve prompt: your idea` and I will check which ingredients you have, find conflicts and write a stronger version.",
      "Suivez un ordre clair et mettez les détails importants **sans consignes contradictoires**. Puis essayez `improve prompt: votre idée` : je vérifie quels ingrédients vous avez, repère les conflits et rédige une version plus forte.",
      "Koresha uko bikurikirana neza kandi ushyiremo ibikomeye **utarimo amabwiriza ahabanye**. Hanyuma gerageza `improve prompt: igitekerezo cyawe` ndebe ibigize ufite, mbone ibihabanye nandike verisiyo ikomeye.",
      "Tumia mpangilio wazi na uweke undani muhimu **bila maagizo yanayokinzana**. Kisha jaribu `improve prompt: wazo lako` nikague viungo ulivyo navyo, nitafute migongano na niandike toleo imara zaidi."),
     (["**Subject:** the main person, animal, object, place or scene.",
       "**Action or state:** what the subject is doing.",
       "**Environment:** location, season, weather and background.",
       "**Composition:** close-up, medium, wide, top-down, centred, rule of thirds.",
       "**Lighting:** soft window light, dramatic side light, golden hour, studio, rim light, overcast.",
       "**Colour palette:** warm earth tones, cool blues, complementary colours, muted pastels, high contrast.",
       "**Visual style:** photorealistic, editorial photo, watercolour, 3D render, comic illustration.",
       "**Materials and texture:** brushed metal, wet pavement, knitted fabric, glass reflections.",
       "**Camera language:** wide-angle, macro, shallow depth of field, portrait-lens look, when useful.",
       "**Quality goals:** clear focal point, coherent anatomy, natural shadows, balanced composition, readable shapes.",
       "**Aspect ratio:** square, portrait or landscape, if supported.",
       "**Constraints:** what must be included and what must be excluded."],
      ["**Sujet :** la personne, l'animal, l'objet, le lieu ou la scène principale.",
       "**Action ou état :** ce que fait le sujet.",
       "**Environnement :** lieu, saison, météo et arrière-plan.",
       "**Composition :** gros plan, plan moyen, plan large, vue du dessus, centré, règle des tiers.",
       "**Lumière :** lumière douce de fenêtre, éclairage latéral dramatique, heure dorée, studio, contre-jour, ciel couvert.",
       "**Palette de couleurs :** tons terre chauds, bleus froids, couleurs complémentaires, pastels doux, fort contraste.",
       "**Style visuel :** photoréaliste, photo éditoriale, aquarelle, rendu 3D, illustration de bande dessinée.",
       "**Matières et textures :** métal brossé, chaussée mouillée, tricot, reflets sur le verre.",
       "**Langage photographique :** grand-angle, macro, faible profondeur de champ, rendu d'objectif portrait, si utile.",
       "**Objectifs de qualité :** point focal net, anatomie cohérente, ombres naturelles, composition équilibrée, formes lisibles.",
       "**Format :** carré, portrait ou paysage, si pris en charge.",
       "**Contraintes :** ce qui doit figurer et ce qui doit être exclu."],
      ["**Insanganyamatsiko:** umuntu, itungo, ikintu, ahantu cyangwa ibyabaye by'ingenzi.",
       "**Igikorwa cyangwa imimerere:** icyo insanganyamatsiko ikora.",
       "**Ibidukikije:** ahantu, igihembwe, ikirere n'inyuma.",
       "**Imiterere (composition):** close-up, hagati, ishusho yagutse, ireba hejuru, hagati, rule of thirds.",
       "**Urumuri:** urumuri rworoshye rw'idirishya, urumuri rw'uruhande rukomeye, golden hour, studio, ibicu bitwikiriye.",
       "**Amabara:** amabara y'ubutaka ashyushye, ubururu bukonje, amabara yuzuzanya, pastel zoroshye, itandukaniro rinini.",
       "**Uburyo bw'ishusho:** nyakuri nk'ifoto, ifoto y'itangazamakuru, watercolor, 3D, igishushanyo cy'inkuru.",
       "**Ibikoresho n'imiterere y'ubuso:** icyuma cyogejwe, umuhanda utose, imyenda iboshye, ibirahure bigaragaza.",
       "**Ururimi rwa kamera:** wide-angle, macro, ubujyakuzimu buto, lens ya portrait, iyo bikenewe.",
       "**Intego z'ubuziranenge:** aho amaso ahurira hasobanutse, umubiri uhuje, igicucu karemano, imiterere iringaniye, ishusho isomeka.",
       "**Ingano (aspect ratio):** kare, portrait cyangwa landscape, iyo bishyigikiwe.",
       "**Imbogamizi:** ibigomba kubamo n'ibigomba gukurwamo."],
      ["**Mada:** mtu, mnyama, kitu, mahali au tukio kuu.",
       "**Kitendo au hali:** kile mada inafanya.",
       "**Mazingira:** mahali, msimu, hali ya hewa na mandharinyuma.",
       "**Muundo (composition):** close-up, wastani, pana, mtazamo wa juu, katikati, kanuni ya theluthi.",
       "**Mwanga:** mwanga laini wa dirisha, mwanga mkali wa pembeni, golden hour, studio, mwanga wa nyuma, anga la mawingu.",
       "**Paleti ya rangi:** rangi za udongo joto, bluu baridi, rangi zinazokamilishana, pastel laini, utofauti mkubwa.",
       "**Mtindo wa kuona:** kama picha halisi, picha ya uhariri, rangi za maji, 3D, mchoro wa katuni.",
       "**Vifaa na umbile:** chuma kilichosuguliwa, lami iliyolowa, kitambaa kilichofumwa, mwangaza kwenye kioo.",
       "**Lugha ya kamera:** wide-angle, macro, kina kidogo cha uwanja, mwonekano wa lenzi ya picha-mtu, inapofaa.",
       "**Malengo ya ubora:** kitovu wazi, anatomia thabiti, vivuli asilia, muundo uliosawazika, maumbo yanayosomeka.",
       "**Uwiano wa picha:** mraba, wima au mlalo, ukiungwa mkono.",
       "**Vikwazo:** kinachopaswa kuwepo na kinachopaswa kuachwa."]),
     ("The 12 ingredients", "Les 12 ingrédients", "Ibigize 12", "Viungo 12"), ["img_weak_strong", "img_composition"], boundary=False, photo="Golden hour (photography)")

_add("img_weak_strong", "weak prompt vs strong prompt|weak vs strong prompt|example of a good image prompt|example of a strong prompt|example image prompt|bad prompt vs good prompt|prompt example for ai image|"
     "prompt faible et prompt fort|exemple de bon prompt|exemple de prompt d'image|"
     "prompt idakomeye na prompt ikomeye|urugero rwa prompt nziza|"
     "prompt dhaifu na prompt imara|mfano wa prompt nzuri", "",
     ("Weak prompt vs strong prompt", "Prompt faible et prompt fort", "Prompt idakomeye na prompt ikomeye", "Prompt dhaifu na prompt imara"),
     ("**Weak:** “Make a beautiful city.”\n\n**Stronger:** “Create a cinematic, photorealistic view of a modern city street after rain at blue hour. Reflect warm shop lights across wet pavement, place a few pedestrians in the middle distance, use a leading line toward a softly illuminated skyline, add realistic reflections and atmospheric depth, keep the street as the focal point, use a balanced teal-and-amber palette, and choose a landscape composition.”\n\n**Why it helps:** clear subject, time, weather, lighting, composition, palette, style and focal point. No wording guarantees a perfect result.",
      "**Faible :** « Fais une belle ville. »\n\n**Plus fort :** « Crée une vue cinématographique et photoréaliste d'une rue moderne après la pluie, à l'heure bleue. Reflète les lumières chaudes des boutiques sur la chaussée mouillée, place quelques piétons au plan intermédiaire, utilise une ligne de fuite vers un horizon urbain doucement éclairé, ajoute des reflets réalistes et de la profondeur atmosphérique, garde la rue comme point focal, utilise une palette équilibrée sarcelle et ambre, au format paysage. »\n\n**Pourquoi ça aide :** sujet, moment, météo, lumière, composition, palette, style et point focal clairs. Aucune formulation ne garantit un résultat parfait.",
      "**Idakomeye:** «Kora umujyi mwiza.»\n\n**Ikomeye kurushaho:** «Kora ishusho ya sinema, nyakuri nk'ifoto, y'umuhanda w'umujyi wa none nyuma y'imvura mu isaha y'ubururu. Erekana amatara ashyushye y'amaduka agaragara ku muhanda utose, shyiramo abanyamaguru bake hagati, koresha umurongo uyobora ku nzu zimurikirwa buhoro, ongeramo ibigaragara nyabyo n'ubujyakuzimu bw'ikirere, ugumane umuhanda nk'ahantu amaso ahurira, koresha amabara ya teal na amber aringaniye, uhitemo ishusho ya landscape.»\n\n**Impamvu bifasha:** insanganyamatsiko, igihe, ikirere, urumuri, imiterere, amabara, uburyo n'aho amaso ahurira bisobanutse. Nta nteruro yemeza ibisubizo byuzuye.",
      "**Dhaifu:** «Tengeneza jiji zuri.»\n\n**Imara zaidi:** «Unda mwonekano wa sinema, kama picha halisi, wa barabara ya kisasa ya jiji baada ya mvua wakati wa blue hour. Onyesha taa joto za maduka zikiakisi kwenye lami iliyolowa, weka watembea kwa miguu wachache katikati ya umbali, tumia mstari unaoongoza kuelekea mandhari ya jiji inayomulikwa taratibu, ongeza mwangaza halisi na kina cha anga, weka barabara kama kitovu, tumia paleti iliyosawazika ya teal na amber, na uchague muundo wa mlalo.»\n\n**Kwa nini inasaidia:** mada, wakati, hali ya hewa, mwanga, muundo, paleti, mtindo na kitovu vyote ni wazi. Hakuna maneno yanayohakikisha matokeo kamilifu."),
     related=["img_ingredients"])

# ---------------------------------------------------------------- 5. composition
_add("img_composition", "composition techniques|image composition|composition tips|rule of thirds|what is the rule of thirds|leading lines|focal point|visual hierarchy|how to compose an image|negative space|"
     "techniques de composition|regle des tiers|lignes de fuite|point focal|hierarchie visuelle|composition d'image|"
     "uburyo bwo gutunganya ishusho|rule of thirds ni iki|umurongo uyobora|"
     "mbinu za muundo wa picha|kanuni ya theluthi|mistari inayoongoza|kitovu cha picha", "",
     ("Composition techniques that make images work", "Techniques de composition qui font une bonne image", "Uburyo bwo gutunganya ishusho bukora neza", "Mbinu za muundo zinazofanya picha ifanye kazi"),
     ("Strong images guide the eye. Try `rule of thirds 1920x1080` to see exactly where the grid lines and power points fall for your picture size.",
      "Les bonnes images guident l'œil. Essayez `rule of thirds 1920x1080` pour voir où tombent les lignes et points forts de la grille pour votre format.",
      "Amashusho meza ayobora ijisho. Gerageza `rule of thirds 1920x1080` urebe aho imirongo n'ingingo z'ingenzi z'urushundura ziri ku ngano y'ishusho yawe.",
      "Picha nzuri huongoza jicho. Jaribu `rule of thirds 1920x1080` kuona mahali mistari na pointi kuu za gridi zinapoangukia kwa ukubwa wa picha yako."),
     (["Create **one clear focal point** to guide attention.",
       "Use **visual hierarchy**: the most important element is the strongest.",
       "Apply the **rule of thirds** when suitable.",
       "Use **leading lines**: roads, paths, shadows or architecture.",
       "**Separate subject from background** with contrast, lighting, distance or depth of field.",
       "Balance **negative space** and avoid unnecessary clutter.",
       "Keep **perspective, horizon, scale and architecture** consistent.",
       "Keep **shadow direction and reflections** consistent with the light.",
       "Choose a **deliberate colour palette** instead of letting too many colours compete."],
      ["Créez **un point focal net** pour guider l'attention.",
       "Utilisez la **hiérarchie visuelle** : l'élément le plus important est le plus fort.",
       "Appliquez la **règle des tiers** quand elle convient.",
       "Utilisez des **lignes de fuite** : routes, chemins, ombres ou architecture.",
       "**Séparez le sujet du fond** par le contraste, la lumière, la distance ou la profondeur de champ.",
       "Équilibrez l'**espace négatif** et évitez l'encombrement inutile.",
       "Gardez **perspective, horizon, échelle et architecture** cohérents.",
       "Gardez **direction des ombres et reflets** cohérents avec la lumière.",
       "Choisissez une **palette délibérée** plutôt que trop de couleurs en concurrence."],
      ["Shyiraho **aho amaso ahurira hamwe hasobanutse** kuyobora ubwitonzi.",
       "Koresha **uburyo bw'ibyingenzi mu maso**: ikintu cy'ingenzi kiba gikomeye kurusha ibindi.",
       "Koresha **rule of thirds** iyo bikwiye.",
       "Koresha **imirongo iyobora**: imihanda, inzira, igicucu cyangwa inyubako.",
       "**Tandukanya insanganyamatsiko n'inyuma** ukoresheje itandukaniro, urumuri, intera cyangwa ubujyakuzimu.",
       "Ringaniza **umwanya ubuze ikintu** wirinde akajagari katari ngombwa.",
       "Gumana **perspective, umurongo w'ikirere, ingano n'inyubako** bihuje.",
       "Gumana **icyerekezo cy'igicucu n'ibigaragara** bihuye n'urumuri.",
       "Hitamo **amabara abigambiriwe** aho kureka amabara menshi yivuguruza."],
      ["Unda **kitovu kimoja wazi** kuongoza umakini.",
       "Tumia **uongozi wa kuona**: kipengele muhimu zaidi kiwe na nguvu zaidi.",
       "Tumia **kanuni ya theluthi** inapofaa.",
       "Tumia **mistari inayoongoza**: barabara, njia, vivuli au usanifu.",
       "**Tenganisha mada na mandharinyuma** kwa utofauti, mwanga, umbali au kina cha uwanja.",
       "Sawazisha **nafasi tupu** na epuka msongamano usio wa lazima.",
       "Weka **mtazamo, upeo wa macho, kipimo na usanifu** vilingane.",
       "Weka **mwelekeo wa vivuli na mwangaza** unaolingana na mwanga.",
       "Chagua **paleti ya rangi ya makusudi** badala ya rangi nyingi kushindana."]),
     ("Nine composition techniques", "Neuf techniques de composition", "Uburyo icyenda bwo gutunganya", "Mbinu tisa za muundo"), ["img_ingredients", "img_improve"], photo="Rule of thirds")

# ---------------------------------------------------------------- 6. improving the first result
_add("img_improve", "improving the first result|how to improve an ai image|improve my ai image|how to fix an ai image|how do i improve the first result|iterate on ai image|how to refine an ai image|ai image is not what i wanted|"
     "ameliorer le premier resultat|comment ameliorer une image ia|affiner une image ia|"
     "kunoza ishusho ya mbere|nanoza nte ishusho ya ai|"
     "kuboresha matokeo ya kwanza|jinsi ya kuboresha picha ya ai", "",
     ("Improving the first result (7 steps)", "Améliorer le premier résultat (7 étapes)", "Kunoza ibyavuye bwa mbere (intambwe 7)", "Kuboresha matokeo ya kwanza (hatua 7)"),
     ("Do not restart a good image for a small fault, and do not change everything at once.",
      "Ne recommencez pas une bonne image pour un petit défaut, et ne changez pas tout d'un coup.",
      "Ntutangire bundi bushya ishusho nziza kubera ikosa rito, kandi ntuhindure byose icyarimwe.",
      "Usianze upya picha nzuri kwa kosa dogo, na usibadilishe kila kitu mara moja."),
     (["Compare the image **with the request**, not only with general attractiveness.",
       "Identify the **three most important errors** (wrong subject, weak composition, inconsistent lighting...).",
       "**Revise only the relevant prompt details**; avoid changing everything at once.",
       "Use a **reference image, mask, pose guide or layout control** if available and the composition must stay stable.",
       "**Generate alternatives** when possible and compare accuracy, composition, lighting, anatomy and readability.",
       "Keep **text inside images short** and verify the spelling: generated lettering can be wrong.",
       "Use **targeted editing** for small fixes instead of restarting a successful image."],
      ["Comparez l'image **à la demande**, pas seulement à son attrait général.",
       "Repérez les **trois erreurs les plus importantes** (mauvais sujet, composition faible, lumière incohérente...).",
       "**Révisez seulement les détails concernés** du prompt ; évitez de tout changer d'un coup.",
       "Utilisez une **image de référence, un masque, un guide de pose ou un contrôle de mise en page** si disponible et si la composition doit rester stable.",
       "**Générez des variantes** si possible et comparez exactitude, composition, lumière, anatomie et lisibilité.",
       "Gardez le **texte dans l'image court** et vérifiez l'orthographe : les lettres générées peuvent être fausses.",
       "Faites une **retouche ciblée** pour les petits défauts plutôt que de relancer une image réussie."],
      ["Gereranya ishusho **n'icyifuzo**, si gusa n'ubwiza rusange.",
       "Menya **amakosa atatu y'ingenzi** (insanganyamatsiko itari yo, imiterere idakomeye, urumuri rudahuye...).",
       "**Hindura gusa utuntu twa prompt dufitanye isano**; wirinde guhindura byose icyarimwe.",
       "Koresha **ishusho y'ibisobanuro, mask, uyobora uko ahagaze cyangwa uyobora imiterere** iyo biboneka kandi imiterere igomba kuguma.",
       "**Kora andi mashusho** iyo bishoboka ugereranye ukuri, imiterere, urumuri, umubiri no gusomeka.",
       "Gumana **inyandiko iri mu shusho ngufi** kandi ugenzure imyandikire: inyuguti zakozwe zishobora kuba zibeshye.",
       "Koresha **guhindura kwihariye** ku makosa mato aho gutangira bundi bushya ishusho yagenze neza."],
      ["Linganisha picha **na ombi**, si tu mvuto wa jumla.",
       "Tambua **makosa matatu muhimu zaidi** (mada isiyo sahihi, muundo dhaifu, mwanga usioendana...).",
       "**Rekebisha tu undani husika wa prompt**; epuka kubadilisha kila kitu mara moja.",
       "Tumia **picha rejea, mask, mwongozo wa mkao au udhibiti wa mpangilio** ikiwa inapatikana na muundo lazima ubaki.",
       "**Zalisha mbadala** inapowezekana na ulinganishe usahihi, muundo, mwanga, anatomia na usomekaji.",
       "Weka **maandishi ndani ya picha mafupi** na hakiki tahajia: herufi zilizozalishwa zinaweza kuwa na makosa.",
       "Tumia **uhariri maalum** kwa marekebisho madogo badala ya kuanza upya picha iliyofanikiwa."]),
     ("The seven steps", "Les sept étapes", "Intambwe zirindwi", "Hatua saba"), ["img_problems", "img_score"])

# ---------------------------------------------------------------- 8. training
_add("img_training", "how is an ai image model trained|how are image generators trained|training an image model|what does image model training involve|how to train an image generator|training of image generation|"
     "comment entraine-t-on un modele d'image|entrainement d'un generateur d'images|"
     "guhugura icyitegererezo cy'amashusho|ai y'amashusho ihugurwa ite|"
     "modeli ya picha hufunzwa vipi|mafunzo ya kizalishaji cha picha", "",
     ("What training an image model usually involves (8 steps)", "Ce que comprend l'entraînement d'un modèle d'image (8 étapes)", "Ibijyanye no guhugura icyitegererezo cy'amashusho (intambwe 8)", "Mafunzo ya modeli ya picha kwa kawaida yanahusisha nini (hatua 8)"),
     ("The same learning loop as other models: predict, measure the error, compute gradients, update the parameters, repeat. For a diffusion system the loss is often the **denoising prediction error**. Exact recipes of commercial models are not public.",
      "La même boucle d'apprentissage que les autres modèles : prédire, mesurer l'erreur, calculer les gradients, mettre à jour les paramètres, recommencer. Pour un système de diffusion, la perte est souvent l'**erreur de prédiction du débruitage**. Les recettes exactes des modèles commerciaux ne sont pas publiques.",
      "Uruziga rumwe rwo kwiga nk'ibindi byitegererezo: guhanura, gupima ikosa, kubara gradients, kuvugurura parameters, gusubiramo. Muri sisitemu ya diffusion, loss akenshi ni **ikosa ryo guhanura denoising**. Uburyo nyabwo bw'ibyitegererezo by'ubucuruzi si rusange.",
      "Mzunguko ule ule wa kujifunza kama modeli nyingine: tabiri, pima kosa, kokotoa gradients, sasisha vigezo, rudia. Kwa mfumo wa diffusion, loss mara nyingi ni **kosa la utabiri wa denoising**. Mapishi kamili ya modeli za kibiashara si ya umma."),
     (["**Data preparation:** process suitable image and text data, remove corrupted examples, manage duplicates and quality, apply privacy and permission safeguards.",
       "**Pretraining:** optimise a generative model on large-scale data to learn visual structure and text–image relationships.",
       "**Objective function:** a numerical loss for training error, such as denoising prediction error in diffusion.",
       "**Backpropagation:** gradients showing how each parameter contributed to the error.",
       "**Optimisation:** update the parameters with a gradient-based optimiser.",
       "**Evaluation:** prompt adherence, visual quality, diversity, robustness, bias and safety.",
       "**Fine-tuning:** adapt behaviour with curated examples, feedback or preference-based methods.",
       "**Deployment:** run the model on suitable hardware, manage memory and latency, connect it to an interface."],
      ["**Préparation des données :** traiter des données image et texte adaptées, retirer les exemples corrompus, gérer doublons et qualité, appliquer des garanties de vie privée et de permission.",
       "**Pré-entraînement :** optimiser un modèle génératif sur de très grandes données pour apprendre la structure visuelle et les liens texte–image.",
       "**Fonction objectif :** une perte numérique mesurant l'erreur, comme l'erreur de prédiction du débruitage en diffusion.",
       "**Rétropropagation :** gradients montrant la contribution de chaque paramètre à l'erreur.",
       "**Optimisation :** mettre à jour les paramètres avec un optimiseur à gradient.",
       "**Évaluation :** fidélité au prompt, qualité visuelle, diversité, robustesse, biais et sécurité.",
       "**Affinage :** adapter le comportement avec des exemples choisis, des retours ou des méthodes de préférence.",
       "**Déploiement :** exécuter le modèle sur du matériel adapté, gérer mémoire et latence, le relier à une interface."],
      ["**Gutegura amakuru:** gutunganya amakuru y'amashusho n'inyandiko akwiye, gukuraho ingero zangiritse, gucunga ibisubirwamo n'ubuziranenge, gukurikiza ibanga n'uburenganzira.",
       "**Pretraining:** gutunganya icyitegererezo cya generative ku makuru manini ngo cyige imiterere y'amashusho n'isano ry'inyandiko–ishusho.",
       "**Objective function:** loss y'imibare ipima ikosa, nka denoising prediction error muri diffusion.",
       "**Backpropagation:** gradients zerekana uko buri parameter yagize uruhare mu makosa.",
       "**Optimisation:** kuvugurura parameters hakoreshejwe optimizer ya gradient.",
       "**Isuzuma:** gukurikiza prompt, ubuziranenge bw'ishusho, ubwoko, gukomera, kubogama n'umutekano.",
       "**Fine-tuning:** guhindura imyitwarire ukoresheje ingero zatoranyijwe, ibitekerezo cyangwa uburyo bushingiye ku byifuzo.",
       "**Deployment:** gukoresha icyitegererezo kuri mudasobwa ikwiye, gucunga memory na latency, kukihuza n'imiyoboro."],
      ["**Maandalizi ya data:** chakata data ya picha na maandishi inayofaa, ondoa mifano iliyoharibika, simamia marudio na ubora, tumia kinga za faragha na ruhusa.",
       "**Pretraining:** boresha modeli ya generative kwa data kubwa kujifunza muundo wa kuona na uhusiano wa maandishi–picha.",
       "**Objective function:** loss ya namba inayopima kosa la mafunzo, kama kosa la utabiri wa denoising katika diffusion.",
       "**Backpropagation:** gradients zinazoonyesha kila kigezo kilichangiaje kosa.",
       "**Optimisation:** sasisha vigezo kwa optimizer ya gradient.",
       "**Tathmini:** kufuata prompt, ubora wa kuona, utofauti, uimara, upendeleo na usalama.",
       "**Fine-tuning:** rekebisha tabia kwa mifano iliyochaguliwa, maoni au mbinu za mapendeleo.",
       "**Deployment:** endesha modeli kwenye vifaa vinavyofaa, simamia kumbukumbu na kuchelewa, iunganishe na kiolesura."]),
     ("The eight steps", "Les huit étapes", "Intambwe umunani", "Hatua nane"), ["img_diffusion", "img_techniques"], boundary=True)

# ---------------------------------------------------------------- 9. what can be claimed
_add("img_claims", "what can be claimed about this assistant|can you generate images|can you draw|can you create images|can this assistant make pictures|do you generate images|are ai images always accurate|do ai images have errors|can ai images be wrong|what are the limits of ai images|"
     "peux-tu generer des images|peux-tu dessiner|sais-tu creer des images|les images ia sont-elles toujours exactes|limites des images ia|"
     "ushobora gukora amashusho|ushobora gushushanya|amashusho ya ai ni ukuri buri gihe|imbibi z'amashusho ya ai|"
     "unaweza kutengeneza picha|unaweza kuchora|je picha za ai ni sahihi kila mara|mipaka ya picha za ai", "",
     ("What this assistant can and cannot claim about images", "Ce que cet assistant peut et ne peut pas affirmer sur les images", "Ibyo uyu mufasha ashobora kandi adashobora kuvuga ku mashusho", "Kile msaidizi huyu anaweza na asichoweza kudai kuhusu picha"),
     ("**What I do:** explain how AI image generation works, teach prompt writing and composition, check and strengthen your prompts, calculate grids and ratios, and help you judge and improve results.\n\n**What I do not do:** draw the picture myself (no image model is connected here) or reveal private details of any commercial image model.\n\nGenerated images can look convincing while still having **errors in geometry, lettering, object relationships or factual accuracy**. Treat any image as a draft to check. Avoid treating one prompt formula as a guaranteed secret recipe: strong output combines a capable model, clear instructions, suitable controls, iterative evaluation and careful editing.",
      "**Ce que je fais :** expliquer le fonctionnement de la génération d'images par IA, enseigner l'écriture de prompts et la composition, vérifier et renforcer vos prompts, calculer grilles et formats, et vous aider à juger et améliorer les résultats.\n\n**Ce que je ne fais pas :** dessiner moi-même l'image (aucun modèle d'image n'est connecté ici) ni révéler des détails privés d'un modèle d'image commercial.\n\nUne image générée peut paraître convaincante tout en contenant des **erreurs de géométrie, de lettrage, de relations entre objets ou d'exactitude factuelle**. Traitez toute image comme un brouillon à vérifier. Évitez de croire qu'une formule de prompt est une recette secrète garantie : un bon résultat combine un modèle capable, des instructions claires, des contrôles adaptés, une évaluation itérative et une retouche soignée.",
      "**Ibyo nkora:** gusobanura uko AI ikora amashusho, kwigisha kwandika prompts n'imiterere, kugenzura no gukomeza prompts zawe, kubara imirongo n'ingano, no kugufasha gusuzuma no kunoza ibisubizo.\n\n**Ibyo ntakora:** gushushanya ishusho ubwanjye (nta cyitegererezo cy'amashusho gihujwe hano) cyangwa gutangaza amakuru y'ibanga y'icyitegererezo cy'ubucuruzi.\n\nAmashusho yakozwe ashobora kugaragara neza ariko arimo **amakosa mu miterere, mu nyuguti, mu isano y'ibintu cyangwa mu kuri**. Fata ishusho iyo ari yo yose nk'igishushanyo cyo kugenzura. Wirinde gufata formule imwe ya prompt nk'ibanga ryemeza: ibisubizo bikomeye bihuza icyitegererezo gishoboye, amabwiriza asobanutse, ibigenzura bikwiye, isuzuma risubirwamo no guhindura witonze.",
      "**Ninachofanya:** kueleza jinsi uzalishaji wa picha kwa AI unavyofanya kazi, kufundisha uandishi wa prompt na muundo, kukagua na kuimarisha prompts zako, kukokotoa gridi na uwiano, na kukusaidia kutathmini na kuboresha matokeo.\n\n**Nisichofanya:** kuchora picha mwenyewe (hakuna modeli ya picha iliyounganishwa hapa) au kufichua undani wa siri wa modeli ya picha ya kibiashara.\n\nPicha zilizozalishwa zinaweza kuonekana za kusadikika huku zikiwa na **makosa ya jiometri, herufi, uhusiano wa vitu au usahihi wa ukweli**. Chukulia picha yoyote kama rasimu ya kukagua. Epuka kuchukulia fomula moja ya prompt kama mapishi ya siri yenye uhakika: matokeo imara huchanganya modeli yenye uwezo, maagizo wazi, vidhibiti vinavyofaa, tathmini ya kurudia na uhariri makini."),
     related=["img_process", "img_problems"])

# ---------------------------------------------------------------- 10. practice plan
_add("img_practice", "image practice plan|beginner practice plan for ai images|practice plan|how do i practice ai image generation|exercises for ai image generation|ai image exercises|how do i get better at prompts|"
     "plan d'entrainement images ia|exercices pour la generation d'images|"
     "gahunda yo kwitoza amashusho ya ai|imyitozo y'amashusho ya ai|"
     "mpango wa mazoezi ya picha za ai|mazoezi ya uzalishaji wa picha", "",
     ("Beginner practice plan (6 exercises)", "Plan d'entraînement pour débutants (6 exercices)", "Gahunda yo kwitoza y'abatangiye (imyitozo 6)", "Mpango wa mazoezi kwa wanaoanza (mazoezi 6)"),
     ("Change **one thing at a time** and compare. Score each result with `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2` and keep notes about what worked.",
      "Changez **une seule chose à la fois** et comparez. Notez chaque résultat avec `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2` et gardez des notes sur ce qui a marché.",
      "Hindura **ikintu kimwe icyarimwe** ugereranye. Tanga amanota buri gisubizo ukoresheje `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2` kandi wandike ibyagenze neza.",
      "Badilisha **kitu kimoja kwa wakati** na ulinganishe. Pa alama kila matokeo kwa `score image: accuracy 4, composition 3, lighting 5, detail 4, coherence 2` na weka maelezo ya yaliyofaulu."),
     (["**Lighting:** one subject with soft daylight, golden-hour light and dramatic studio light; compare shadows and mood.",
       "**Composition:** centred, rule-of-thirds and close-up versions of one subject; compare visual focus.",
       "**Colour:** keep subject and composition fixed and change only the palette.",
       "**Prompt:** start short, then add subject, setting, lighting, composition and style one at a time.",
       "**Editing:** use a supported mask or editing feature to fix one area and keep the rest.",
       "**Evaluation:** score prompt accuracy, composition, lighting, detail and coherence from 1 to 5; record what worked."],
      ["**Lumière :** un sujet avec lumière du jour douce, heure dorée et éclairage de studio dramatique ; comparez ombres et ambiance.",
       "**Composition :** versions centrée, règle des tiers et gros plan d'un sujet ; comparez la focalisation.",
       "**Couleur :** gardez sujet et composition fixes et changez seulement la palette.",
       "**Prompt :** commencez court, puis ajoutez sujet, décor, lumière, composition et style un par un.",
       "**Retouche :** utilisez un masque ou une fonction d'édition pour corriger une zone et garder le reste.",
       "**Évaluation :** notez fidélité, composition, lumière, détail et cohérence de 1 à 5 ; consignez ce qui a marché."],
      ["**Urumuri:** insanganyamatsiko imwe n'urumuri rworoshye rw'amanywa, golden hour n'urumuri rukomeye rwa studio; gereranya igicucu n'umutima w'ishusho.",
       "**Imiterere:** verisiyo iri hagati, rule of thirds na close-up y'insanganyamatsiko imwe; gereranya aho amaso ahurira.",
       "**Amabara:** gumana insanganyamatsiko n'imiterere uhindure amabara gusa.",
       "**Prompt:** tangira ngufi, hanyuma wongereho insanganyamatsiko, aho biri, urumuri, imiterere n'uburyo kimwe kimwe.",
       "**Guhindura:** koresha mask cyangwa igikoresho cyo guhindura ukosore agace kamwe usigaze ibindi.",
       "**Isuzuma:** tanga amanota ku kuri kwa prompt, imiterere, urumuri, utuntu duto no guhuza kuva kuri 1 kugeza kuri 5; wandike ibyagenze neza."],
      ["**Mwanga:** mada moja kwa mwanga laini wa mchana, golden hour na mwanga mkali wa studio; linganisha vivuli na hisia.",
       "**Muundo:** matoleo ya katikati, kanuni ya theluthi na close-up ya mada moja; linganisha mwelekeo wa kuona.",
       "**Rangi:** weka mada na muundo vilivyo na ubadilishe paleti tu.",
       "**Prompt:** anza fupi, kisha ongeza mada, mazingira, mwanga, muundo na mtindo moja moja.",
       "**Uhariri:** tumia mask au kipengele cha uhariri kurekebisha eneo moja na kuacha kilichobaki.",
       "**Tathmini:** pa alama usahihi wa prompt, muundo, mwanga, undani na mshikamano kutoka 1 hadi 5; andika kilichofaa."]),
     ("The six exercises", "Les six exercices", "Imyitozo itandatu", "Mazoezi sita"), ["img_score", "img_improve"])

# ---------------------------------------------------------------- 12. further reading
_add("img_reading", "image generation further reading|where can i learn ai image generation|ai image generation courses|diffusion models course|diffusers documentation|ddpm paper|latent diffusion paper|image generation references|"
     "ou apprendre la generation d'images|ressources sur la generation d'images|lectures complementaires images ia|"
     "aho nasoma amashusho ya ai|amasomo y'amashusho ya ai|"
     "wapi kujifunza uzalishaji wa picha|vyanzo vya kusoma kuhusu picha za ai", "",
     ("Further reading on image generation", "Pour aller plus loin sur la génération d'images", "Gusoma byinshi ku gukora amashusho", "Usomaji zaidi kuhusu uzalishaji wa picha"),
     ("These public sources explain **general techniques and terminology**; they do not reveal private details of a particular model. Check each address yourself.\n\n- OpenAI, Image generation in the API: https://platform.openai.com/docs/guides/image-generation\n- OpenAI, Images in ChatGPT: https://help.openai.com/en/articles/8932459-dall-e-in-chatgpt\n- Hugging Face, Diffusion Models course: https://huggingface.co/learn/diffusion-course/en/unit0/1\n- Hugging Face, Diffusers documentation: https://huggingface.co/docs/diffusers/index\n- Denoising Diffusion Probabilistic Models (paper): https://arxiv.org/abs/2006.11239\n- Latent Diffusion Models (paper): https://arxiv.org/abs/2112.10752",
      "Ces sources publiques expliquent les **techniques et la terminologie générales** ; elles ne révèlent pas les détails privés d'un modèle précis. Vérifiez chaque adresse vous-même.\n\n- OpenAI, génération d'images dans l'API : https://platform.openai.com/docs/guides/image-generation\n- OpenAI, images dans ChatGPT : https://help.openai.com/en/articles/8932459-dall-e-in-chatgpt\n- Hugging Face, cours sur les modèles de diffusion : https://huggingface.co/learn/diffusion-course/en/unit0/1\n- Hugging Face, documentation Diffusers : https://huggingface.co/docs/diffusers/index\n- Denoising Diffusion Probabilistic Models (article) : https://arxiv.org/abs/2006.11239\n- Latent Diffusion Models (article) : https://arxiv.org/abs/2112.10752",
      "Aya masoko rusange asobanura **uburyo n'amagambo rusange**; ntatangaza amakuru y'ibanga y'icyitegererezo runaka. Genzura buri aderesi wowe ubwawe.\n\n- OpenAI, Image generation in the API: https://platform.openai.com/docs/guides/image-generation\n- OpenAI, Images in ChatGPT: https://help.openai.com/en/articles/8932459-dall-e-in-chatgpt\n- Hugging Face, Diffusion Models course: https://huggingface.co/learn/diffusion-course/en/unit0/1\n- Hugging Face, Diffusers documentation: https://huggingface.co/docs/diffusers/index\n- Denoising Diffusion Probabilistic Models (paper): https://arxiv.org/abs/2006.11239\n- Latent Diffusion Models (paper): https://arxiv.org/abs/2112.10752",
      "Vyanzo hivi vya umma vinaeleza **mbinu na istilahi za jumla**; havifichui undani wa siri wa modeli fulani. Hakiki kila anwani mwenyewe.\n\n- OpenAI, Image generation in the API: https://platform.openai.com/docs/guides/image-generation\n- OpenAI, Images in ChatGPT: https://help.openai.com/en/articles/8932459-dall-e-in-chatgpt\n- Hugging Face, Diffusion Models course: https://huggingface.co/learn/diffusion-course/en/unit0/1\n- Hugging Face, Diffusers documentation: https://huggingface.co/docs/diffusers/index\n- Denoising Diffusion Probabilistic Models (paper): https://arxiv.org/abs/2006.11239\n- Latent Diffusion Models (paper): https://arxiv.org/abs/2112.10752"),
     related=["img_techniques"])

# ---------------------------------------------------------------- 7. common problems and fixes (list + single-problem finder)
PROBLEMS = [
    ("wrong subject|wrong-looking subject|wrong looking subject|wrong object|not what i asked|sujet incorrect|mauvais sujet|insanganyamatsiko itari yo|mada isiyo sahihi",
     ("Wrong-looking subject", "Sujet qui a l'air faux", "Insanganyamatsiko ibonekana nabi", "Mada inaonekana vibaya"),
     ("Describe distinctive features, pose, viewpoint and relative size more precisely.", "Décrivez plus précisément les traits distinctifs, la pose, le point de vue et la taille relative.",
      "Sobanura neza ibiyiranga, uko ihagaze, aho ireba n'ingano ugereranyije.", "Eleza kwa usahihi zaidi sifa bainishi, mkao, mtazamo na ukubwa linganishi.")),
    ("crowded|too busy|cluttered|too many objects|too many things|encombre|trop charge|trop d'objets|akajagari|byinshi cyane|msongamano|vitu vingi",
     ("Crowded composition", "Composition encombrée", "Imiterere irimo akajagari", "Muundo wenye msongamano"),
     ("Reduce the number of objects and specify one focal point with a simpler background.", "Réduisez le nombre d'objets et précisez un point focal avec un arrière-plan plus simple.",
      "Gabanya umubare w'ibintu ushyireho aho amaso ahurira hamwe n'inyuma horoshye.", "Punguza idadi ya vitu na ueleze kitovu kimoja chenye mandharinyuma rahisi.")),
    ("inconsistent lighting|lighting is wrong|lighting looks wrong|light looks wrong|lighting looks off|shadows look wrong|shadows are wrong|wrong shadows|lumiere incoherente|ombres incorrectes|urumuri rudahuye|igicucu kibeshya|mwanga usioendana|vivuli vibaya",
     ("Inconsistent lighting", "Éclairage incohérent", "Urumuri rudahuye", "Mwanga usioendana"),
     ("Specify one main light source and a clear time of day.", "Précisez une source de lumière principale et un moment de la journée clair.",
      "Garagaza isoko imwe y'urumuri n'igihe cy'umunsi gisobanutse.", "Taja chanzo kimoja kikuu cha mwanga na wakati wazi wa siku.")),
    ("bad hands|hands look wrong|extra fingers|weird hands|faces look wrong|distorted face|artifacts|artefacts|deformed|mains bizarres|doigts en trop|visage deforme|ibiganza bibi|intoki nyinshi|mikono mibaya|vidole vingi|uso uliopotoka",
     ("Artifacts in hands, faces or objects", "Artefacts sur les mains, visages ou objets", "Amakosa ku biganza, mu maso cyangwa ku bintu", "Dosari kwenye mikono, nyuso au vitu"),
     ("Try another generation, a closer crop, or supported inpainting tools to redo just that area.", "Essayez une autre génération, un cadrage plus serré ou les outils de retouche (inpainting) pour refaire seulement cette zone.",
      "Gerageza indi shusho, gutema hafi cyangwa ibikoresho bya inpainting bishyigikiwe kugira ngo usubiremo agace gusa.", "Jaribu uzalishaji mwingine, kukata karibu zaidi, au zana za inpainting zinazoungwa mkono kurudia eneo hilo tu.")),
    ("generic|boring|looks generic|bland|plain|generique|banal|insipide|isanzwe cyane|haina mvuto|ya kawaida mno",
     ("Generic appearance", "Apparence générique", "Isura isanzwe cyane", "Mwonekano wa kawaida mno"),
     ("Add meaningful setting details, deliberate composition and a coherent palette.", "Ajoutez des détails de décor significatifs, une composition délibérée et une palette cohérente.",
      "Ongeraho utuntu tw'ibidukikije dufite icyo tuvuze, imiterere ibigambiriwe n'amabara ahuje.", "Ongeza undani wa mazingira wenye maana, muundo wa makusudi na paleti inayoshikamana.")),
    ("conflicting instructions|contradictory prompt|styles conflict|mixed styles|instructions contradictoires|prompt contradictoire|amabwiriza ahabanye|maagizo yanayokinzana",
     ("Conflicting instructions", "Consignes contradictoires", "Amabwiriza ahabanye", "Maagizo yanayokinzana"),
     ("Remove incompatible styles or contradictory camera and lighting directions.", "Retirez les styles incompatibles ou les directives de caméra et de lumière contradictoires.",
      "Kuraho uburyo budahuye cyangwa amabwiriza ya kamera n'urumuri ahabanye.", "Ondoa mitindo isiyooana au maelekezo ya kamera na mwanga yanayokinzana.")),
    ("unreadable details|tiny details|small details unreadable|text in image is wrong|wrong spelling in image|wrong text|lettering|texte illisible|petits details illisibles|fautes dans le texte de l'image|inyandiko mu shusho ni mbi|maandishi kwenye picha yana makosa|undani mdogo hausomeki",
     ("Unreadable small details (and wrong lettering)", "Petits détails illisibles (et lettrage faux)", "Utuntu duto dudasomeka (n'inyuguti zibeshye)", "Undani mdogo usiosomeka (na herufi zisizo sahihi)"),
     ("Simplify the scene, enlarge the important element, or edit the area separately. Keep text inside images short and check the spelling.", "Simplifiez la scène, agrandissez l'élément important ou retouchez la zone séparément. Gardez le texte court et vérifiez l'orthographe.",
      "Oroshya ishusho, wongere ingano y'ikintu cy'ingenzi cyangwa uhindure agace ukwako. Gumana inyandiko ngufi kandi ugenzure imyandikire.", "Rahisisha eneo, kuza kipengele muhimu, au hariri eneo kando. Weka maandishi mafupi na hakiki tahajia.")),
]
_PROB_KW = [[fold(x) for x in kws.split("|")] for kws, _, _ in PROBLEMS]

_add("img_problems", "common problems with ai images|problems with ai images|ai image problems|common ai image mistakes|how to fix ai image problems|ai image troubleshooting|"
     "problemes courants des images ia|erreurs courantes des images ia|"
     "ibibazo bisanzwe by'amashusho ya ai|amakosa asanzwe y'amashusho ya ai|"
     "matatizo ya kawaida ya picha za ai|makosa ya kawaida ya picha za ai", "",
     ("Common problems and fixes (7)", "Problèmes courants et solutions (7)", "Ibibazo bisanzwe n'uko bikosorwa (7)", "Matatizo ya kawaida na suluhisho (7)"),
     ("Describe your problem in your own words (for example “my image has bad hands” or “the lighting looks wrong”) and I will give the specific fix.",
      "Décrivez votre problème avec vos mots (par exemple « mon image a de mauvaises mains » ou « la lumière est fausse ») et je donnerai la solution précise.",
      "Sobanura ikibazo cyawe mu magambo yawe (urugero «ishusho yanjye ifite ibiganza bibi» cyangwa «urumuri rurasa nabi») nkwereke igisubizo cyihariye.",
      "Eleza tatizo lako kwa maneno yako (mfano «picha yangu ina mikono mibaya» au «mwanga unaonekana vibaya») nitakupa suluhisho mahususi."),
     None,
     ("Problem — fix", "Problème — solution", "Ikibazo — igisubizo", "Tatizo — suluhisho"), ["img_improve", "img_prompt_tips"])
# the generator above yields lists per language; materialise them (the entry was built from a generator of 4 lists)
_e, _k, _kc = _RAW[-1]
_e["steps"] = {l: [f"**{p[1][i]}** — {p[2][i]}" for p in PROBLEMS] for i, l in enumerate(LANGS)}


def problem_entry(i):
    _, t, f = PROBLEMS[i]
    return entry(f"img_problem_{i}", "image_guide", dict(zip(LANGS, t)), dict(zip(LANGS, f)), None, None, ["img_problems", "img_improve"])


_add("img_prompt_tips", "image prompt tips|tips for ai image prompts|prompt tips|prompt formula|is there a magic prompt|secret prompt|best prompt for ai images|"
     "conseils pour prompts d'image|prompt magique|"
     "inama ku prompts z'amashusho|prompt y'ubumaji|"
     "vidokezo vya prompt za picha|prompt ya siri", "",
     ("Prompt tips (and why there is no magic formula)", "Conseils de prompt (et pourquoi il n'y a pas de formule magique)", "Inama ku prompts (n'impamvu nta formule y'ubumaji ibaho)", "Vidokezo vya prompt (na kwa nini hakuna fomula ya uchawi)"),
     ("Strong output usually comes from a **capable model, clear instructions, suitable controls, iterative evaluation and careful editing**, not from a secret recipe.",
      "Un bon résultat vient d'ordinaire d'un **modèle capable, d'instructions claires, de contrôles adaptés, d'une évaluation itérative et d'une retouche soignée**, pas d'une recette secrète.",
      "Ibisubizo bikomeye ubusanzwe bituruka ku **cyitegererezo gishoboye, amabwiriza asobanutse, ibigenzura bikwiye, isuzuma risubirwamo no guhindura witonze**, si ku buryo bw'ibanga.",
      "Matokeo imara kwa kawaida hutokana na **modeli yenye uwezo, maagizo wazi, vidhibiti vinavyofaa, tathmini ya kurudia na uhariri makini**, si mapishi ya siri."),
     (["Put the **subject first**, then setting, light, composition and style, in a consistent order.",
       "Say **what you want**; list essential exclusions separately and briefly.",
       "Use **concrete words** (“wet pavement”, “soft window light”) instead of vague ones (“nice”, “beautiful”).",
       "Pick **one style and one light source**; avoid mixing contradictory styles.",
       "Change **one thing per attempt** so you can see what caused the difference.",
       "Check the picture against the request and fix the **three biggest errors** first."],
      ["Mettez le **sujet en premier**, puis décor, lumière, composition et style, dans un ordre constant.",
       "Dites **ce que vous voulez** ; listez séparément et brièvement les exclusions essentielles.",
       "Utilisez des **mots concrets** (« chaussée mouillée », « lumière douce de fenêtre ») plutôt que vagues (« joli », « beau »).",
       "Choisissez **un style et une source de lumière** ; évitez de mélanger des styles contradictoires.",
       "Changez **une chose par essai** pour voir ce qui cause la différence.",
       "Comparez l'image à la demande et corrigez d'abord les **trois plus grosses erreurs**."],
      ["Shyira **insanganyamatsiko mbere**, hanyuma aho biri, urumuri, imiterere n'uburyo, mu buryo buhoraho.",
       "Vuga **ibyo ushaka**; andika ibyo wirinda ukwabyo kandi mu magambo make.",
       "Koresha **amagambo asobanutse** («umuhanda utose», «urumuri rworoshye rw'idirishya») aho gukoresha ayoroheje («byiza»).",
       "Hitamo **uburyo bumwe n'isoko imwe y'urumuri**; wirinde kuvanga uburyo buhabanye.",
       "Hindura **ikintu kimwe kuri buri igerageza** kugira ngo urebe icyateye itandukaniro.",
       "Gereranya ishusho n'icyifuzo ukosore mbere **amakosa atatu manini**."],
      ["Weka **mada kwanza**, kisha mazingira, mwanga, muundo na mtindo, kwa mpangilio thabiti.",
       "Sema **unachotaka**; orodhesha vizuizi muhimu kando na kwa ufupi.",
       "Tumia **maneno halisi** («lami iliyolowa», «mwanga laini wa dirisha») badala ya ya jumla («nzuri», «maridadi»).",
       "Chagua **mtindo mmoja na chanzo kimoja cha mwanga**; epuka kuchanganya mitindo inayokinzana.",
       "Badilisha **kitu kimoja kwa jaribio** ili uone kilichosababisha tofauti.",
       "Linganisha picha na ombi na urekebishe **makosa matatu makubwa** kwanza."]),
     ("Six tips", "Six conseils", "Inama esheshatu", "Vidokezo sita"), ["img_ingredients", "img_improve"])

# ---------------------------------------------------------------- 11. glossary (14 terms)
TERMS = [
    ("Generative model", "generative model|modele generatif|icyitegererezo cya generative|modeli ya generative", False,
     ("A trained model that produces new content such as images.", "Un modèle entraîné qui produit du nouveau contenu, comme des images.", "Icyitegererezo cyahuguwe gitanga ibishya nk'amashusho.", "Modeli iliyofunzwa inayozalisha maudhui mapya kama picha.")),
    ("Prompt", "prompt|prompts|invite de commande", True,
     ("Text instructions describing the intended result.", "Instructions textuelles décrivant le résultat voulu.", "Amabwiriza y'inyandiko asobanura ibyifuzwa.", "Maagizo ya maandishi yanayoeleza matokeo yanayokusudiwa.")),
    ("Token", "token|jeton|tokeni", True,
     ("A unit used to represent text for model processing.", "Une unité qui représente le texte pour le traitement par le modèle.", "Igice gihagararira inyandiko mu gutunganywa n'icyitegererezo.", "Kipande kinachowakilisha maandishi kwa uchakataji wa modeli.")),
    ("Embedding", "embedding|plongement", False,
     ("A numerical representation of information.", "Une représentation numérique d'une information.", "Ishusho y'imibare y'amakuru.", "Uwakilishi wa namba wa taarifa.")),
    ("Neural network", "neural network|reseau de neurones|umuyoboro w'imitsi|mtandao wa neva", False,
     ("A layered mathematical model with learnable parameters.", "Un modèle mathématique en couches avec des paramètres apprenables.", "Icyitegererezo cy'imibare gifite ibyiciro n'ibipimo bishobora kwiga.", "Modeli ya hisabati yenye tabaka na vigezo vinavyoweza kujifunza.")),
    ("Parameter", "parameter|parametre|kigezo", True,
     ("A learned numerical value inside a model.", "Une valeur numérique apprise à l'intérieur d'un modèle.", "Umubare wize uri mu cyitegererezo.", "Thamani ya namba iliyojifunzwa ndani ya modeli.")),
    ("Diffusion", "diffusion", True,
     ("A family of methods that learn to reverse a noise process.", "Une famille de méthodes qui apprennent à inverser un processus de bruitage.", "Umuryango w'uburyo bwiga gusubiza inyuma uburyo bw'urusaku.", "Familia ya mbinu zinazojifunza kugeuza mchakato wa kelele.")),
    ("Latent space", "latent space|espace latent", False,
     ("A compressed representation used for computation or generation.", "Une représentation compressée utilisée pour le calcul ou la génération.", "Uburyo bugabanyije bukoreshwa mu kubara cyangwa gukora.", "Uwakilishi uliobanwa unaotumika kwa hesabu au uzalishaji.")),
    ("Attention", "attention", True,
     ("A mechanism for weighting relationships between information elements.", "Un mécanisme qui pondère les relations entre éléments d'information.", "Uburyo bwo gupima isano hagati y'ibice by'amakuru.", "Utaratibu wa kupima uhusiano kati ya vipengele vya taarifa.")),
    ("Conditioning", "conditioning|conditionnement", False,
     ("Additional information used to guide generation.", "Informations supplémentaires utilisées pour guider la génération.", "Amakuru y'inyongera akoreshwa mu kuyobora gukora.", "Taarifa ya ziada inayotumika kuongoza uzalishaji.")),
    ("Fine-tuning", "fine-tuning|fine tuning|affinage", False,
     ("Further training that adapts a model to a task or behaviour.", "Entraînement supplémentaire qui adapte un modèle à une tâche ou un comportement.", "Guhugura kwiyongera guhindura icyitegererezo ku murimo cyangwa imyitwarire.", "Mafunzo ya ziada yanayorekebisha modeli kwa kazi au tabia.")),
    ("Inpainting", "inpainting|retouche generative|what is inpainting", False,
     ("Editing a selected region of an image.", "Modifier une région choisie d'une image.", "Guhindura agace gatoranyijwe k'ishusho.", "Kuhariri eneo lililochaguliwa la picha.")),
    ("Upscaling", "upscaling|upscale|agrandissement|what is upscaling", False,
     ("Increasing image resolution, sometimes with learned enhancement. It cannot recover information that was never present.", "Augmenter la résolution d'une image, parfois avec amélioration apprise. Cela ne retrouve pas une information jamais présente.", "Kongera ubuziranenge bw'ishusho, rimwe na rimwe hakoreshejwe kunoza kwize. Ntibishobora kugarura amakuru atigeze abaho.", "Kuongeza ubora wa picha, wakati mwingine kwa uboreshaji uliojifunzwa. Haiwezi kurejesha taarifa ambayo haikuwepo kamwe.")),
    ("Inference", "inference|inference|inferense", True,
     ("Running a trained model to generate an output.", "Exécuter un modèle entraîné pour produire une sortie.", "Gukoresha icyitegererezo cyahuguwe ngo gitange igisohoka.", "Kuendesha modeli iliyofunzwa kutoa matokeo.")),
]
_TERM_ENTRIES = [(n, [fold(x) for x in kw.split("|")], ctx, dict(zip(LANGS, d))) for n, kw, ctx, d in TERMS]
_CTX = ["image", "images", "picture", "pictures", "photo", "ai", "generat", "diffusion", "dall", "midjourney", "stable", "picha", "ishusho", "amashusho", "ia", "text to image", "prompt"]
_LIST = [fold(x) for x in ["image generation glossary", "ai image glossary", "glossary of image generation", "list image generation terms", "image generation terms", "glossaire de la generation d'images", "termes de la generation d'images",
                           "amagambo y'amashusho ya ai", "istilahi za picha za ai", "orodha ya istilahi za uzalishaji wa picha"]]
_ASK = [fold(x) for x in ["what is", "what's", "what are", "define", "meaning of", "explain", "qu'est-ce que", "qu'est-ce qu'un", "qu'est-ce qu'une", "c'est quoi", "definition de", "ni iki", "ni nini", "maana ya", "fafanua"]]
_TITLES = {"en": "Image-generation glossary", "fr": "Glossaire de la génération d'images", "rw": "Amagambo y'ingenzi y'amashusho ya AI", "sw": "Istilahi za uzalishaji wa picha"}


def _glossary():
    body = {l: "\n".join(f"- **{n}:** {d[l]}" for n, _, _, d in _TERM_ENTRIES) for l in LANGS}
    return entry("img_glossary", "image_guide", dict(_TITLES), body, None, None, ["img_techniques"])


def _has_ctx(q):
    return has_phrase(q, [fold(x) for x in _CTX])


def find(question, lang="en"):
    q = fold(question)
    if not q or len(q) > 170:
        return None
    if has_phrase(q, _LIST):
        return _glossary()
    for e, kw, kwc in _RAW:
        if kw and has_phrase(q, kw):
            return e
        if kwc and has_phrase(q, kwc) and _has_ctx(q):
            return e
    # a specific problem described in the user's own words
    for i, kws in enumerate(_PROB_KW):
        if has_phrase(q, kws) and (_has_ctx(q) or len(q.split()) <= 8):
            return problem_entry(i)
    if has_phrase(q, _ASK) and len(q.split()) <= 9:
        for name, kws, ctx, defs in _TERM_ENTRIES:
            if has_phrase(q, kws) and (not ctx or _has_ctx(q)):
                return entry("img_term_" + fold(name).replace(" ", "_"), "image_guide", {l: name for l in LANGS}, defs, None, None, ["img_glossary"])
    return None


IDS = [e["id"] for e, _, _ in _RAW] + ["img_glossary"]
