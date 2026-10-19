"""Writing assistant (offline part): ready-to-edit templates for emails, CVs, applications, reports, proposals and everyday messages,
in English, French, Kinyarwanda and Kiswahili. Pure Python. Placeholders are in [square brackets]; nothing is invented about the user.
fr/rw/sw wording is a draft for fluent review. Personalised drafting and "improve my text" go to the AI (see assistant_engine)."""
from __future__ import annotations
from textutil import fold, has_phrase, lk, entry, LANGS

PH = {"en": ("Your name", "Recipient name", "Date"), "fr": ("Votre nom", "Nom du destinataire", "Date"),
      "rw": ("Izina ryawe", "Izina ry'uwo wandikiye", "Itariki"), "sw": ("Jina lako", "Jina la mpokeaji", "Tarehe")}
_LABEL = {"en": "Template (copy it, replace the [brackets], delete what does not apply)", "fr": "Modèle (copiez-le, remplacez les [crochets], supprimez ce qui ne s'applique pas)",
          "rw": "Icyitegererezo (kigukoporore, usimbuze ibiri mu [dukane], ukureho ibitajyanye)", "sw": "Kiolezo (kinakili, badilisha maneno ya [mabano], futa yasiyohusika)"}
_TIPS_LABEL = {"en": "Tips to make it better", "fr": "Conseils pour l'améliorer", "rw": "Inama zo kuyinoza", "sw": "Vidokezo vya kuboresha"}
_ASK_AI = {"en": "For a version written around your real details, give me the facts (who, what, when) or tick “Always ask the AI”, and paste your own text to have it improved.",
           "fr": "Pour une version adaptée à vos vrais détails, donnez-moi les faits (qui, quoi, quand) ou cochez « Toujours demander à l'IA », et collez votre texte pour l'améliorer.",
           "rw": "Ushaka verisiyo ikoze ku makuru yawe nyayo, mbwira ibyo (nde, iki, ryari) cyangwa uhitemo «Burigihe baza AI», ushyiremo inyandiko yawe ngo inozwe.",
           "sw": "Kwa toleo lililoandikwa kwa maelezo yako halisi, nipe ukweli (nani, nini, lini) au chagua «Muulize AI kila mara», na ubandike maandishi yako yaboreshwe."}

# id: (aliases per lang, title per lang, body per lang, tips per lang)
T = {}

def _t(id_, al, title, body, tips):
    T[id_] = dict(al=al, title=title, body=dict(zip(LANGS, body)), tips=dict(zip(LANGS, tips)))

_t("email", ("formal email|professional email|business email|email|e-mail|formal letter|letter",
             "e-mail professionnel|courriel|e-mail|mail|lettre formelle|lettre",
             "imeri|ibaruwa isanzwe|ibaruwa|imeri y'umwuga",
             "barua pepe|barua rasmi|barua"),
   {"en": "Professional email", "fr": "E-mail professionnel", "rw": "Imeri y'umwuga", "sw": "Barua pepe ya kitaalamu"},
   ("Subject: [Topic in a few words]\n\nDear [Recipient name],\n\nI am writing to [state your purpose in one sentence].\n\n[Give the important details: what, when, why. Keep it short.]\n\nCould you please [the action you need] by [date]? Please tell me if you need anything else from me.\n\nThank you for your time.\n\nKind regards,\n[Your name]\n[Phone / email]",
    "Objet : [Sujet en quelques mots]\n\nBonjour [Nom du destinataire],\n\nJe vous écris afin de [indiquer l'objet en une phrase].\n\n[Donnez les détails importants : quoi, quand, pourquoi. Restez bref.]\n\nPourriez-vous [l'action demandée] avant le [date] ? N'hésitez pas à me dire si vous avez besoin d'autres informations.\n\nJe vous remercie de votre attention.\n\nCordialement,\n[Votre nom]\n[Téléphone / e-mail]",
    "Insanganyamatsiko: [Icyo ivuga mu magambo make]\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nNandikiye [kuvuga impamvu mu nteruro imwe].\n\n[Tanga amakuru y'ingenzi: iki, ryari, kubera iki. Bigire bigufi.]\n\nMwabishobora [igikorwa ukeneye] bitarenze [itariki]? Mumbwire niba hari ibindi mukeneye.\n\nMurakoze ku gihe cyanyu.\n\nMugire amahoro,\n[Izina ryawe]\n[Telefone / imeri]",
    "Kichwa: [Mada kwa maneno machache]\n\nMheshimiwa [Jina la mpokeaji],\n\nNakuandikia ili [kueleza lengo kwa sentensi moja].\n\n[Toa maelezo muhimu: nini, lini, kwa nini. Yawe mafupi.]\n\nTafadhali, unaweza [hatua unayohitaji] kabla ya [tarehe]? Niambie ukihitaji kitu kingine kutoka kwangu.\n\nAsante kwa muda wako.\n\nKwa heshima,\n[Jina lako]\n[Simu / barua pepe]"),
   (["A clear subject line helps the reader open and sort it.", "Put the request in the first two sentences.", "One email, one purpose. Check names, dates and attachments before sending."],
    ["Un objet clair aide à ouvrir et classer le message.", "Mettez la demande dans les deux premières phrases.", "Un e-mail, un objectif. Vérifiez noms, dates et pièces jointes avant d'envoyer."],
    ["Umutwe usobanutse utuma imeri isomwa ikanabikwa neza.", "Shyira icyo usaba mu nteruro ebyiri za mbere.", "Imeri imwe, intego imwe. Genzura amazina, amatariki n'ibyometsweho mbere yo kohereza."],
    ["Kichwa wazi humsaidia msomaji kufungua na kupanga barua.", "Weka ombi katika sentensi mbili za kwanza.", "Barua moja, lengo moja. Hakiki majina, tarehe na viambatisho kabla ya kutuma."]))

_t("cv", ("cv|curriculum vitae|resume|my cv|write a cv|cv template",
          "cv|curriculum vitae|curriculum|modele de cv|faire un cv|rediger un cv",
          "cv|amateka y'akazi|kwandika cv|icyitegererezo cya cv",
          "cv|wasifu|wasifu wa kazi|resume|kuandika cv"),
   {"en": "CV (resume) structure", "fr": "Structure d'un CV", "rw": "Imiterere ya CV", "sw": "Muundo wa CV (wasifu)"},
   ("[YOUR FULL NAME]\n[Phone] | [Email] | [Town, Country] | [LinkedIn, optional]\n\nPROFILE\n[2-3 lines: who you are, your main strength, the job you want. Only true facts.]\n\nEXPERIENCE (most recent first)\n[Job title] - [Organisation], [Town]   [Month Year - Month Year]\n- [What you did + result, e.g. \"Managed 12 suppliers and cut delays by a measured amount\"]\n- [Another achievement]\n\nEDUCATION\n[Qualification] - [School/University], [Year]\n\nSKILLS\n[Skill 1], [Skill 2], [Language: level], [Computer skills]\n\nREFEREES\n[Name, role, contact] or \"Available on request\"",
    "[VOTRE NOM COMPLET]\n[Téléphone] | [E-mail] | [Ville, Pays] | [LinkedIn, facultatif]\n\nPROFIL\n[2-3 lignes : qui vous êtes, votre atout principal, le poste visé. Uniquement des faits vrais.]\n\nEXPÉRIENCE (la plus récente d'abord)\n[Intitulé du poste] - [Organisation], [Ville]   [Mois Année - Mois Année]\n- [Ce que vous avez fait + résultat]\n- [Autre réalisation]\n\nFORMATION\n[Diplôme] - [École/Université], [Année]\n\nCOMPÉTENCES\n[Compétence 1], [Compétence 2], [Langue : niveau], [Informatique]\n\nRÉFÉRENCES\n[Nom, fonction, contact] ou « Disponibles sur demande »",
    "[IZINA RYAWE RYUZUYE]\n[Telefone] | [Imeri] | [Umujyi, Igihugu] | [LinkedIn, si ubishaka]\n\nIBYAWE BIGUFI\n[Imirongo 2-3: uwo uri we, ubushobozi bwawe bukuru, akazi ushaka. Ukuri gusa.]\n\nUBURAMBE (utangire n'ubwa vuba)\n[Umwanya w'akazi] - [Ikigo], [Umujyi]   [Ukwezi Umwaka - Ukwezi Umwaka]\n- [Icyo wakoze + icyo cyatanze]\n- [Ikindi wagezeho]\n\nAMASHURI\n[Impamyabumenyi] - [Ishuri/Kaminuza], [Umwaka]\n\nUBUMENYI\n[Ubumenyi 1], [Ubumenyi 2], [Ururimi: urwego], [Mudasobwa]\n\nABAHAMYA\n[Izina, umwanya, uko wamubona] cyangwa «Barahari nibabisabwa»",
    "[JINA LAKO KAMILI]\n[Simu] | [Barua pepe] | [Mji, Nchi] | [LinkedIn, hiari]\n\nUTANGULIZI\n[Mistari 2-3: wewe ni nani, nguvu yako kuu, kazi unayotaka. Ukweli tu.]\n\nUZOEFU (wa hivi karibuni kwanza)\n[Cheo] - [Taasisi], [Mji]   [Mwezi Mwaka - Mwezi Mwaka]\n- [Ulichofanya + matokeo]\n- [Mafanikio mengine]\n\nELIMU\n[Cheti/Shahada] - [Shule/Chuo], [Mwaka]\n\nUJUZI\n[Ujuzi 1], [Ujuzi 2], [Lugha: kiwango], [Kompyuta]\n\nWADHAMINI\n[Jina, cheo, mawasiliano] au \"Wanapatikana ukihitaji\""),
   (["Keep it to one or two pages and put the most relevant things first.", "Describe results (what changed because of you), not only duties.", "Adapt it to each job using words from the advert. Never include false information.", "Use a professional email address and ask someone to proofread it."],
    ["Une ou deux pages, le plus pertinent d'abord.", "Décrivez des résultats (ce qui a changé grâce à vous), pas seulement des tâches.", "Adaptez-le à chaque poste avec les mots de l'annonce. Aucune fausse information.", "Adresse e-mail professionnelle ; faites-le relire."],
    ["Paji imwe cyangwa ebyiri, ibijyanye cyane n'akazi bibanze.", "Vuga ibyo wagezeho (icyahindutse kubera wowe), udavuga imirimo gusa.", "Ihuze na buri kazi ukoresheje amagambo yo mu itangazo. Ntushyiremo ibinyoma.", "Koresha imeri y'umwuga kandi usabe undi kuyisoma."],
    ["Ukurasa mmoja au miwili, vinavyohusika zaidi vikitangulia.", "Eleza matokeo (kilichobadilika kwa sababu yako), si majukumu tu.", "Ibadilishe kwa kila kazi kwa maneno ya tangazo. Usiweke taarifa za uongo.", "Tumia barua pepe ya kitaalamu na mwombe mtu aisome."]))

_t("cover", ("cover letter|application letter|job application|application email|letter of application|motivation letter|apply for a job|apply for the job",
             "lettre de motivation|lettre de candidature|candidature|postuler",
             "ibaruwa isaba akazi|ibaruwa y'ubusabe|isaba akazi|gusaba akazi",
             "barua ya maombi ya kazi|barua ya kuomba kazi|maombi ya kazi|kuomba kazi"),
   {"en": "Job application / cover letter", "fr": "Lettre de candidature", "rw": "Ibaruwa isaba akazi", "sw": "Barua ya maombi ya kazi"},
   ("[Your name]\n[Phone] | [Email]\n[Date]\n\n[Recipient name / Hiring Manager]\n[Organisation]\n\nSubject: Application for [Job title] - [Your name]\n\nDear [Recipient name],\n\nI am applying for the position of [Job title] advertised on [where you saw it]. I am [one line about you, e.g. a graduate in ... / a ... with N years of experience].\n\nIn my work at [organisation] I [one real achievement with a result]. I also have [skill or qualification] that matches your need for [requirement from the advert].\n\nI would welcome the chance to discuss how I can contribute to [organisation]. My CV is attached, and I can be reached on [phone].\n\nYours sincerely,\n[Your name]",
    "[Votre nom]\n[Téléphone] | [E-mail]\n[Date]\n\n[Nom du destinataire / Responsable du recrutement]\n[Organisation]\n\nObjet : Candidature au poste de [Intitulé du poste] - [Votre nom]\n\nMadame, Monsieur,\n\nJe me permets de postuler au poste de [Intitulé du poste] publié sur [source de l'annonce]. Je suis [une ligne sur vous].\n\nDans mon travail chez [organisation], j'ai [une réalisation réelle avec un résultat]. Je possède aussi [compétence ou diplôme] qui correspond à votre besoin de [exigence de l'annonce].\n\nJe serais heureux(se) de vous rencontrer pour discuter de ma contribution à [organisation]. Mon CV est joint ; je suis joignable au [téléphone].\n\nVeuillez agréer, Madame, Monsieur, mes salutations distinguées.\n[Votre nom]",
    "[Izina ryawe]\n[Telefone] | [Imeri]\n[Itariki]\n\n[Izina ry'uwo wandikiye / Ushinzwe gutanga akazi]\n[Ikigo]\n\nIngingo: Gusaba umwanya wa [Izina ry'akazi] - [Izina ryawe]\n\nMuraho neza,\n\nNandikiye gusaba umwanya wa [Izina ry'akazi] watangajwe kuri [aho wawubonye]. Ndi [umurongo umwe ukuvuga].\n\nMu kazi nakoreye [ikigo], nagezeho [icyo wagezeho koko n'umusaruro]. Mfite kandi [ubumenyi cyangwa impamyabumenyi] bijyanye n'ibyo mukeneye bya [icyo itangazo risaba].\n\nNakwishimira kubonana namwe tukaganira ku mumaro nagirira [ikigo]. CV yanjye iri ku ibaruwa; mwanyandikira cyangwa mugahamagara kuri [telefone].\n\nMurakoze,\n[Izina ryawe]",
    "[Jina lako]\n[Simu] | [Barua pepe]\n[Tarehe]\n\n[Jina la mpokeaji / Meneja wa Ajira]\n[Taasisi]\n\nKichwa: Maombi ya nafasi ya [Cheo cha kazi] - [Jina lako]\n\nMheshimiwa,\n\nNaomba nafasi ya [Cheo cha kazi] iliyotangazwa [mahali ulipoiona]. Mimi ni [sentensi moja kukuhusu].\n\nNilipofanya kazi [taasisi], nilifanikisha [mafanikio halisi yenye matokeo]. Pia nina [ujuzi au cheti] kinacholingana na mahitaji yenu ya [hitaji kwenye tangazo].\n\nNingefurahi kupata nafasi ya kujadili mchango wangu kwa [taasisi]. CV yangu imeambatishwa, na ninapatikana kwa [simu].\n\nKwa heshima,\n[Jina lako]"),
   (["Name the exact job and where you saw it.", "Give one real achievement that matches the advert; do not repeat the whole CV.", "Keep it under one page, polite and specific, and check the name of the organisation.", "Never pay money to apply for a job: that is a common scam."],
    ["Nommez le poste exact et la source de l'annonce.", "Donnez une réalisation réelle liée à l'annonce ; ne répétez pas tout le CV.", "Moins d'une page, poli et précis ; vérifiez le nom de l'organisation.", "Ne payez jamais pour postuler : c'est une arnaque courante."],
    ["Vuga akazi nyirizina n'aho wakabonye.", "Tanga ikintu kimwe wagezeho gihuye n'itangazo; ntusubiremo CV yose.", "Bigire munsi y'urupapuro rumwe, by'icyubahiro kandi bisobanutse; genzura izina ry'ikigo.", "Ntukishyure ngo usabe akazi: ni uburiganya busanzwe."],
    ["Taja kazi halisi na mahali ulipoliona.", "Toa mafanikio moja halisi yanayolingana na tangazo; usirudie CV yote.", "Chini ya ukurasa mmoja, kwa heshima na mahususi; hakiki jina la taasisi.", "Usilipe pesa kuomba kazi: ni utapeli unaojulikana."]))

_t("leave", ("leave request|request leave|ask for leave|day off|sick leave|permission to be absent|annual leave|vacation request",
             "demande de conge|demander un conge|conge maladie|demande d'absence|jour de conge",
             "gusaba ikiruhuko|ikiruhuko|ibaruwa isaba ikiruhuko|gusaba uruhushya|uruhushya",
             "ombi la likizo|kuomba likizo|likizo|ruhusa ya kutokuwepo|likizo ya ugonjwa"),
   {"en": "Leave request", "fr": "Demande de congé", "rw": "Gusaba ikiruhuko", "sw": "Ombi la likizo"},
   ("Subject: Leave request - [Your name], [dates]\n\nDear [Recipient name],\n\nI would like to request [number] days of [annual / sick / other] leave from [start date] to [end date]. I plan to return to work on [return date].\n\nBefore I leave I will [hand over / finish ...] and [colleague name] can assist with urgent matters.\n\nPlease let me know if you approve or need more information.\n\nThank you,\n[Your name]",
    "Objet : Demande de congé - [Votre nom], [dates]\n\nBonjour [Nom du destinataire],\n\nJe souhaite demander [nombre] jours de congé [annuel / maladie / autre] du [date de début] au [date de fin]. Je reprendrai mon travail le [date de reprise].\n\nAvant mon départ, je [transmettrai / terminerai ...] et [nom du collègue] pourra aider pour les urgences.\n\nMerci de me dire si vous approuvez ou si vous avez besoin d'informations.\n\nCordialement,\n[Votre nom]",
    "Ingingo: Gusaba ikiruhuko - [Izina ryawe], [amatariki]\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nNshaka gusaba iminsi [umubare] y'ikiruhuko [cya buri mwaka / cy'uburwayi / ikindi] kuva ku wa [itariki yo gutangira] kugeza ku wa [itariki yo kurangiriza]. Nzasubira ku kazi ku wa [itariki yo gusubirira].\n\nMbere yo kugenda nzaba [nashyikirije / narangije ...], kandi [izina ry'mukozi mugenzi] ashobora gufasha mu by'ingenzi.\n\nMumbwire niba mubyemeye cyangwa mukeneye andi makuru.\n\nMurakoze,\n[Izina ryawe]",
    "Kichwa: Ombi la likizo - [Jina lako], [tarehe]\n\nMheshimiwa [Jina la mpokeaji],\n\nNaomba likizo ya siku [idadi] ya [mwaka / ugonjwa / nyingine] kuanzia [tarehe ya kuanza] hadi [tarehe ya kumaliza]. Nitarejea kazini tarehe [tarehe ya kurudi].\n\nKabla ya kuondoka nitakuwa [nimekabidhi / nimemaliza ...], na [jina la mwenzangu] anaweza kusaidia mambo ya dharura.\n\nTafadhali niambie kama umekubali au unahitaji maelezo zaidi.\n\nAsante,\n[Jina lako]"),
   (["Ask early and give exact dates.", "Say how your work will be covered.", "For sick leave, attach a medical note if your employer requires one."],
    ["Demandez tôt avec des dates précises.", "Dites comment votre travail sera couvert.", "Pour un congé maladie, joignez un certificat si l'employeur l'exige."],
    ["Saba hakiri kare utange amatariki nyayo.", "Vuga uko akazi kawe kazakorwa.", "Ku kiruhuko cy'uburwayi, ongeraho icyemezo cya muganga niba umukoresha agisaba."],
    ["Omba mapema na toa tarehe kamili.", "Eleza kazi yako itashughulikiwa vipi.", "Kwa likizo ya ugonjwa, ambatisha cheti cha daktari kama mwajiri anahitaji."]))

_t("resign", ("resignation letter|resignation|resign|quit my job|notice of resignation",
              "lettre de demission|demission|demissionner",
              "ibaruwa yo kwegura|kwegura|gusezera ku kazi|ibaruwa isezera",
              "barua ya kujiuzulu|kujiuzulu|kuacha kazi"),
   {"en": "Resignation letter", "fr": "Lettre de démission", "rw": "Ibaruwa yo kwegura", "sw": "Barua ya kujiuzulu"},
   ("[Date]\n\nDear [Recipient name],\n\nI am writing to resign from my position as [Job title] at [Organisation]. My last working day will be [date], in line with my [notice period] notice.\n\nThank you for the opportunities I have had here. I will do my best to complete my tasks and help hand over to [colleague/successor] before I leave.\n\nSincerely,\n[Your name]",
    "[Date]\n\nBonjour [Nom du destinataire],\n\nJe vous informe de ma démission du poste de [Intitulé du poste] au sein de [Organisation]. Mon dernier jour de travail sera le [date], conformément à mon préavis de [durée].\n\nJe vous remercie des opportunités reçues. Je ferai de mon mieux pour terminer mes tâches et préparer la passation avec [collègue/successeur].\n\nCordialement,\n[Votre nom]",
    "[Itariki]\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nNandikiye kubamenyesha ko neguye ku mwanya wa [Izina ry'akazi] muri [Ikigo]. Umunsi wanjye wa nyuma ku kazi uzaba ku wa [itariki], nk'uko biteganywa n'igihe cyo kubimenyesha cya [igihe].\n\nNshimiye amahirwe nahawe hano. Nzagerageza kurangiza imirimo yanjye no gufasha gushyikiriza [mugenzi/uzansimbura] mbere yo kugenda.\n\nMurakoze,\n[Izina ryawe]",
    "[Tarehe]\n\nMheshimiwa [Jina la mpokeaji],\n\nNaandika kuwajulisha kujiuzulu kwangu nafasi ya [Cheo] katika [Taasisi]. Siku yangu ya mwisho kazini itakuwa [tarehe], kulingana na notisi yangu ya [muda].\n\nAsante kwa fursa nilizopata hapa. Nitajitahidi kumaliza kazi zangu na kukabidhi kwa [mwenzangu/mrithi] kabla sijaondoka.\n\nKwa heshima,\n[Jina lako]"),
   (["Check your contract for the notice period.", "Stay short, polite and factual; keep a copy.", "Save the explanations for a conversation if you wish."],
    ["Vérifiez le préavis dans votre contrat.", "Restez bref, poli et factuel ; gardez une copie.", "Gardez les explications pour une discussion si vous le souhaitez."],
    ["Reba mu masezerano igihe cyo kubimenyesha.", "Bigire bigufi, by'icyubahiro kandi by'ukuri; ubike kopi.", "Ibisobanuro ubibike mu kiganiro niba ubishaka."],
    ["Angalia mkataba kwa muda wa notisi.", "Iwe fupi, ya heshima na ya kweli; hifadhi nakala.", "Maelezo zaidi yaachwe kwa mazungumzo ukipenda."]))

_t("thanks", ("thank you message|thank you note|thank you email|thank you letter|thanks message|appreciation message|message of thanks",
              "message de remerciement|lettre de remerciement|mot de remerciement|remerciements",
              "ubutumwa bwo gushimira|ibaruwa ishimira|gushimira",
              "ujumbe wa shukrani|barua ya shukrani|kushukuru"),
   {"en": "Thank-you message", "fr": "Message de remerciement", "rw": "Ubutumwa bwo gushimira", "sw": "Ujumbe wa shukrani"},
   ("Dear [Name],\n\nThank you very much for [what they did]. It helped me [the difference it made].\n\nI really appreciate your [time / support / generosity].\n\nWith gratitude,\n[Your name]",
    "Bonjour [Nom],\n\nMerci beaucoup pour [ce qu'il/elle a fait]. Cela m'a permis de [ce que cela a changé].\n\nJ'apprécie sincèrement votre [temps / soutien / générosité].\n\nAvec toute ma gratitude,\n[Votre nom]",
    "Muraho neza [Izina],\n\nMurakoze cyane kuri [icyo yakoze]. Byamfashije [icyo byahinduye].\n\nNshimira by'ukuri [igihe / ubufasha / ubutwari] bwanyu.\n\nMurakoze,\n[Izina ryawe]",
    "Mpendwa [Jina],\n\nAsante sana kwa [ulichofanya]. Kimenisaidia [mabadiliko yaliyotokea].\n\nNathamini sana [muda / msaada / ukarimu] wako.\n\nKwa shukrani,\n[Jina lako]"),
   (["Say exactly what you are thankful for.", "Mention the result: it shows the help mattered.", "Send it soon after the event."],
    ["Dites précisément ce dont vous êtes reconnaissant(e).", "Mentionnez le résultat : cela montre que l'aide a compté.", "Envoyez-le peu après l'événement."],
    ["Vuga neza icyo ushimira.", "Vuga ingaruka: bigaragaza ko ubufasha bwari ingenzi.", "Ubyohereze vuba nyuma y'ibyabaye."],
    ["Taja hasa unachoshukuru.", "Taja matokeo: yanaonyesha msaada ulikuwa muhimu.", "Tuma muda mfupi baada ya tukio."]))

_t("apology", ("apology message|apology letter|apology email|apologise|apologize|say sorry|message to apologise",
               "message d'excuse|lettre d'excuse|presenter mes excuses|s'excuser|excuses",
               "ubutumwa busaba imbabazi|gusaba imbabazi|ibaruwa isaba imbabazi",
               "ujumbe wa kuomba msamaha|kuomba msamaha|barua ya kuomba radhi|kuomba radhi"),
   {"en": "Apology message", "fr": "Message d'excuses", "rw": "Ubutumwa busaba imbabazi", "sw": "Ujumbe wa kuomba msamaha"},
   ("Dear [Name],\n\nI am sorry for [what happened]. I understand it caused [the effect on them], and that was not my intention.\n\nTo put it right, I will [what you will do] by [when].\n\nThank you for your patience.\n\n[Your name]",
    "Bonjour [Nom],\n\nJe suis désolé(e) pour [ce qui s'est passé]. Je comprends que cela a causé [l'effet sur la personne], et ce n'était pas mon intention.\n\nPour réparer, je vais [ce que vous ferez] d'ici le [date].\n\nMerci de votre patience.\n\n[Votre nom]",
    "Muraho neza [Izina],\n\nNsabye imbabazi kuri [ibyabaye]. Ndumva byateye [ingaruka yagize], kandi si ko nabishakaga.\n\nKugira ngo mbikosore, nzakora [icyo uzakora] bitarenze [itariki].\n\nMurakoze kwihangana.\n\n[Izina ryawe]",
    "Mpendwa [Jina],\n\nSamahani kwa [kilichotokea]. Naelewa kuwa kilisababisha [athari kwake], na haikuwa nia yangu.\n\nKurekebisha, nitafanya [utakachofanya] kabla ya [tarehe].\n\nAsante kwa uvumilivu.\n\n[Jina lako]"),
   (["Name what happened without excuses.", "Say what you will do to repair it, and do it.", "Keep it short and sincere."],
    ["Nommez les faits sans vous justifier.", "Dites ce que vous ferez pour réparer, et faites-le.", "Restez bref et sincère."],
    ["Vuga ibyabaye utitwaza impamvu.", "Vuga icyo uzakora ngo ubikosore, kandi ukore.", "Bigire bigufi kandi by'ukuri."],
    ["Taja kilichotokea bila visingizio.", "Sema utakachofanya kurekebisha, kisha ukifanye.", "Iwe fupi na ya dhati."]))

_t("followup", ("follow up email|follow-up email|follow up message|follow up|reminder email|reminder message|payment reminder|chase",
                "e-mail de relance|relance|message de relance|rappel de paiement|rappel",
                "ubutumwa bwo kwibutsa|kwibutsa|ibaruwa yo kwibutsa|kwibutsa kwishyura",
                "ujumbe wa ukumbusho|ukumbusho|barua ya kufuatilia|kukumbusha malipo"),
   {"en": "Follow-up / reminder", "fr": "Relance / rappel", "rw": "Kwibutsa / gukurikirana", "sw": "Ukumbusho / kufuatilia"},
   ("Subject: Follow-up: [topic] ([date or reference])\n\nDear [Recipient name],\n\nI am following up on [what you sent or asked] on [date]. I have not yet received [what you are waiting for].\n\nCould you please [action] by [new date]? If you already did, please ignore this message and tell me so I can update my records.\n\nThank you,\n[Your name]",
    "Objet : Relance : [sujet] ([date ou référence])\n\nBonjour [Nom du destinataire],\n\nJe reviens vers vous au sujet de [ce que vous avez envoyé ou demandé] du [date]. Je n'ai pas encore reçu [ce que vous attendez].\n\nPourriez-vous [action] avant le [nouvelle date] ? Si c'est déjà fait, ignorez ce message et dites-le-moi pour que je mette à jour mes dossiers.\n\nMerci,\n[Votre nom]",
    "Ingingo: Kwibutsa: [ingingo] ([itariki cyangwa nomero])\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nNkurikiranye kuri [icyo wohereje cyangwa wasabye] cyo ku wa [itariki]. Ntabwo ndakira [icyo utegereje].\n\nMwabishobora [igikorwa] bitarenze [itariki nshya]? Niba mwarabikoze, mwirengagize ubu butumwa ariko mumbwire ngo mpindure inyandiko zanjye.\n\nMurakoze,\n[Izina ryawe]",
    "Kichwa: Ufuatiliaji: [mada] ([tarehe au rejea])\n\nMheshimiwa [Jina la mpokeaji],\n\nNafuatilia [ulichotuma au kuomba] cha tarehe [tarehe]. Bado sijapokea [unachosubiri].\n\nTafadhali unaweza [hatua] kabla ya [tarehe mpya]? Kama umeshafanya, puuza ujumbe huu na uniambie ili nisasishe kumbukumbu zangu.\n\nAsante,\n[Jina lako]"),
   (["Mention the date and reference of your first message.", "Stay polite and give a clear new deadline.", "For payments, include the amount and the account to pay (check it yourself, never from an unknown message)."],
    ["Rappelez la date et la référence du premier message.", "Restez poli et donnez une nouvelle échéance claire.", "Pour un paiement, indiquez le montant et le compte (vérifiez-le vous-même)."],
    ["Vuga itariki n'inomero y'ubutumwa bwa mbere.", "Komeza kuba ucishije make kandi utange itariki nshya isobanutse.", "Ku kwishyura, shyiraho amafaranga na konti (ubigenzure wowe ubwawe)."],
    ["Taja tarehe na rejea ya ujumbe wa kwanza.", "Kuwa na adabu na toa tarehe mpya wazi.", "Kwa malipo, weka kiasi na akaunti (hakiki mwenyewe)."]))

_t("complaint", ("complaint letter|complaint email|complaint|make a complaint|formal complaint|complain",
                 "lettre de reclamation|reclamation|plainte|se plaindre",
                 "ibaruwa y'ikirego|ikirego|kwijujuta|gutanga ikirego",
                 "barua ya malalamiko|malalamiko|kulalamika"),
   {"en": "Complaint letter", "fr": "Lettre de réclamation", "rw": "Ibaruwa y'ikirego", "sw": "Barua ya malalamiko"},
   ("Subject: Complaint about [product/service] - [reference or date]\n\nDear [Recipient name],\n\nOn [date] I [bought / used] [product or service] ([order or reference number]). Unfortunately [describe the problem factually].\n\nI would like you to [the solution you want: refund / repair / replacement / explanation] by [date].\n\nI attach [receipt / photos / messages]. Please confirm that you have received this complaint.\n\nSincerely,\n[Your name] [Phone]",
    "Objet : Réclamation concernant [produit/service] - [référence ou date]\n\nBonjour [Nom du destinataire],\n\nLe [date], j'ai [acheté / utilisé] [produit ou service] ([numéro de commande ou référence]). Malheureusement, [décrivez le problème de façon factuelle].\n\nJe souhaite que vous [la solution voulue : remboursement / réparation / remplacement / explication] avant le [date].\n\nJe joins [reçu / photos / messages]. Merci de confirmer la réception de cette réclamation.\n\nCordialement,\n[Votre nom] [Téléphone]",
    "Ingingo: Ikirego kuri [igicuruzwa/serivisi] - [nomero cyangwa itariki]\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nKu wa [itariki] naguze/nakoresheje [igicuruzwa cyangwa serivisi] ([nomero y'itumiza]). Ikibabaje, [sobanura ikibazo mu buryo bw'ukuri].\n\nNifuza ko mwakora [igisubizo ushaka: gusubizwa amafaranga / gukosora / gusimbuza / ibisobanuro] bitarenze [itariki].\n\nMboherereje [inyemezabwishyu / amafoto / ubutumwa]. Mwemeze ko mwakiriye iki kirego.\n\nMurakoze,\n[Izina ryawe] [Telefone]",
    "Kichwa: Malalamiko kuhusu [bidhaa/huduma] - [rejea au tarehe]\n\nMheshimiwa [Jina la mpokeaji],\n\nTarehe [tarehe] nilinunua/nilitumia [bidhaa au huduma] ([nambari ya oda]). Kwa bahati mbaya, [eleza tatizo kwa ukweli].\n\nNaomba mfanye [suluhisho unalotaka: kurejeshewa pesa / kutengeneza / kubadilisha / maelezo] kabla ya [tarehe].\n\nNimeambatisha [risiti / picha / ujumbe]. Tafadhali thibitisheni mmepokea malalamiko haya.\n\nKwa heshima,\n[Jina lako] [Simu]"),
   (["Stick to facts and dates; stay calm.", "Say exactly what outcome you want and by when.", "Keep receipts, photos and a copy of what you sent."],
    ["Restez factuel, avec des dates ; gardez votre calme.", "Dites précisément le résultat voulu et le délai.", "Gardez reçus, photos et copie de l'envoi."],
    ["Komeza ku bintu n'amatariki; ugumane ituze.", "Vuga neza icyo ushaka n'igihe.", "Bika inyemezabwishyu, amafoto na kopi y'ibyo wohereje."],
    ["Shikilia ukweli na tarehe; tulia.", "Sema wazi unachotaka na lini.", "Hifadhi risiti, picha na nakala ya ulichotuma."]))

_t("meeting", ("meeting request|request a meeting|invitation|invite|meeting invitation|schedule a meeting|invitation letter",
               "demande de reunion|invitation|inviter|planifier une reunion|convocation",
               "gusaba inama|ubutumire|ibaruwa y'ubutumire|gutumira|inama",
               "ombi la mkutano|mwaliko|kualika|barua ya mwaliko|mkutano"),
   {"en": "Meeting request / invitation", "fr": "Demande de réunion / invitation", "rw": "Gusaba inama / ubutumire", "sw": "Ombi la mkutano / mwaliko"},
   ("Subject: Meeting request: [topic]\n\nDear [Recipient name],\n\nI would like to meet to discuss [topic]. Would [date and time] suit you? It should take about [duration] at [place / online link].\n\nThe main points are: 1) [point] 2) [point].\n\nPlease confirm or suggest another time that works for you.\n\nThank you,\n[Your name]",
    "Objet : Demande de réunion : [sujet]\n\nBonjour [Nom du destinataire],\n\nJe souhaiterais vous rencontrer pour discuter de [sujet]. Le [date et heure] vous conviendrait-il ? Comptez environ [durée], à [lieu / lien en ligne].\n\nPoints principaux : 1) [point] 2) [point].\n\nMerci de confirmer ou de proposer un autre horaire.\n\nCordialement,\n[Votre nom]",
    "Ingingo: Gusaba inama: [ingingo]\n\nMuraho neza [Izina ry'uwo wandikiye],\n\nNifuza ko duhura tukaganira kuri [ingingo]. Ese [itariki n'isaha] byabagendekera neza? Bizamara hafi [igihe] kuri [ahantu / umurongo wa interineti].\n\nIngingo z'ingenzi: 1) [ingingo] 2) [ingingo].\n\nMwemeze cyangwa mutange ikindi gihe kibabereye.\n\nMurakoze,\n[Izina ryawe]",
    "Kichwa: Ombi la mkutano: [mada]\n\nMheshimiwa [Jina la mpokeaji],\n\nNingependa tukutane kujadili [mada]. Je, [tarehe na saa] inakufaa? Itachukua takriban [muda] katika [mahali / kiungo cha mtandaoni].\n\nHoja kuu: 1) [hoja] 2) [hoja].\n\nTafadhali thibitisha au pendekeza wakati mwingine.\n\nAsante,\n[Jina lako]"),
   (["Give date, time, place or link and length.", "List the main points so people can prepare.", "Ask for confirmation."],
    ["Indiquez date, heure, lieu ou lien et durée.", "Listez les points pour que chacun se prépare.", "Demandez une confirmation."],
    ["Tanga itariki, isaha, ahantu cyangwa umurongo n'igihe.", "Andika ingingo kugira ngo abantu bitegure.", "Saba kwemeza."],
    ["Toa tarehe, saa, mahali au kiungo na muda.", "Orodhesha hoja ili watu wajiandae.", "Omba uthibitisho."]))

_t("proposal", ("business proposal|proposal|project proposal|business plan proposal|funding proposal|grant proposal|pitch",
                "proposition commerciale|proposition de projet|proposition|business plan|dossier de financement",
                "umushinga|icyifuzo cy'umushinga|gutegura umushinga|proposal|ubusabe bw'inkunga",
                "pendekezo la biashara|pendekezo la mradi|pendekezo|mradi|ombi la ufadhili"),
   {"en": "Business proposal outline", "fr": "Plan d'une proposition commerciale", "rw": "Imiterere y'umushinga", "sw": "Muundo wa pendekezo la biashara"},
   ("1. TITLE and your organisation / contact details\n2. SUMMARY (5 lines): the problem, your solution, what you ask for, the result you expect\n3. THE PROBLEM: who is affected, how many, evidence (cite where each number comes from)\n4. YOUR SOLUTION: what you will do, for whom, and how it is different from what exists\n5. PLAN AND TIMELINE: main activities with dates and who is responsible\n6. BUDGET: each cost line with amount and currency, and what you contribute yourself\n7. RESULTS AND HOW YOU WILL MEASURE THEM: clear numbers or checks\n8. RISKS AND HOW YOU WILL MANAGE THEM\n9. YOUR TEAM: roles and relevant experience (true facts only)\n10. NEXT STEP: what decision or meeting you are asking for",
    "1. TITRE et coordonnées de votre organisation\n2. RÉSUMÉ (5 lignes) : le problème, votre solution, ce que vous demandez, le résultat attendu\n3. LE PROBLÈME : qui est touché, combien, preuves (citez la source de chaque chiffre)\n4. VOTRE SOLUTION : ce que vous ferez, pour qui, et en quoi c'est différent de l'existant\n5. PLAN ET CALENDRIER : activités principales, dates et responsables\n6. BUDGET : chaque ligne de coût avec montant et devise, et votre propre contribution\n7. RÉSULTATS ET MESURE : chiffres ou contrôles clairs\n8. RISQUES ET GESTION DES RISQUES\n9. VOTRE ÉQUIPE : rôles et expérience pertinente (faits vrais uniquement)\n10. PROCHAINE ÉTAPE : la décision ou la réunion que vous demandez",
    "1. UMUTWE n'amakuru y'ikigo cyawe\n2. INCAMAKE (imirongo 5): ikibazo, igisubizo cyawe, icyo usaba, umusaruro witeze\n3. IKIBAZO: ni bande bagifite, bangahe, ibimenyetso (vuga aho buri mubare wavuye)\n4. IGISUBIZO CYAWE: icyo uzakora, ku bantu bande, n'icyo gitandukanyeho n'ibisanzwe\n5. IGENAMIGAMBI N'IGIHE: ibikorwa by'ingenzi n'amatariki n'ababishinzwe\n6. ISUBIZWA RY'AMAFARANGA (BUDGET): buri kiguzi n'umubare n'ifaranga, n'ibyo wowe wishyira\n7. UMUSARURO N'UKO UZAPIMWA: imibare cyangwa ibigenzurwa bisobanutse\n8. ICYOHEREZA IBIBAZO N'UKO UZABICUNGA\n9. ITSINDA RYAWE: inshingano n'uburambe bujyanye (ukuri gusa)\n10. ICYIGANA GIKURIKIRA: icyemezo cyangwa inama usaba",
    "1. KICHWA na mawasiliano ya taasisi yako\n2. MUHTASARI (mistari 5): tatizo, suluhisho lako, unachoomba, matokeo unayotarajia\n3. TATIZO: nani anaathirika, wangapi, ushahidi (taja kila namba imetoka wapi)\n4. SULUHISHO LAKO: utakachofanya, kwa nani, na tofauti na vilivyopo\n5. MPANGO NA RATIBA: shughuli kuu, tarehe na wahusika\n6. BAJETI: kila gharama kwa kiasi na sarafu, na mchango wako mwenyewe\n7. MATOKEO NA JINSI YA KUYAPIMA: namba au vipimo wazi\n8. HATARI NA JINSI UTAKAVYOZISIMAMIA\n9. TIMU YAKO: majukumu na uzoefu husika (ukweli tu)\n10. HATUA INAYOFUATA: uamuzi au mkutano unaoomba"),
   (["Lead with the problem and the result, not the technology.", "Back every number with a source or say it is your estimate.", "Keep the budget realistic and explained line by line.", "Read the funder's rules and match their headings and page limits."],
    ["Commencez par le problème et le résultat, pas la technologie.", "Appuyez chaque chiffre par une source ou dites que c'est votre estimation.", "Budget réaliste, expliqué ligne par ligne.", "Lisez les règles du bailleur et suivez ses rubriques et limites de pages."],
    ["Tangira ku kibazo n'umusaruro, si ikoranabuhanga.", "Buri mubare ugire isoko, cyangwa uvuge ko ari uko wabikekaga.", "Budget ibe nyayo kandi isobanurwe umurongo ku wundi.", "Soma amabwiriza y'utanga inkunga ukurikize imitwe n'umubare w'amapaji."],
    ["Anza na tatizo na matokeo, si teknolojia.", "Kila namba iwe na chanzo, au sema ni makadirio yako.", "Bajeti iwe halisi na ieleweke mstari kwa mstari.", "Soma masharti ya mfadhili na ufuate vichwa na kikomo cha kurasa."]))

_t("report", ("report|write a report|report template|report structure|progress report|activity report|lab report|incident report",
              "rapport|rediger un rapport|modele de rapport|structure d'un rapport|rapport d'activite|rapport d'incident",
              "raporo|kwandika raporo|imiterere ya raporo|raporo y'ibikorwa|raporo y'ibyabaye",
              "ripoti|kuandika ripoti|muundo wa ripoti|ripoti ya shughuli|ripoti ya tukio"),
   {"en": "Report structure", "fr": "Structure d'un rapport", "rw": "Imiterere ya raporo", "sw": "Muundo wa ripoti"},
   ("TITLE: [What the report covers] - [Period] - [Author, date]\n\n1. SUMMARY: the 3-5 most important findings and what you recommend\n2. BACKGROUND / PURPOSE: why this report exists\n3. WHAT WAS DONE: activities or method, with dates\n4. FINDINGS / RESULTS: facts and figures (tables help); say which are measured and which are estimates\n5. PROBLEMS AND LESSONS: what did not go as planned and why\n6. RECOMMENDATIONS / NEXT STEPS: who should do what by when\n7. ANNEXES: data, photos, receipts, sources",
    "TITRE : [Objet du rapport] - [Période] - [Auteur, date]\n\n1. RÉSUMÉ : les 3 à 5 constats les plus importants et vos recommandations\n2. CONTEXTE / OBJECTIF : pourquoi ce rapport\n3. CE QUI A ÉTÉ FAIT : activités ou méthode, avec dates\n4. CONSTATS / RÉSULTATS : faits et chiffres (tableaux utiles) ; précisez mesuré ou estimé\n5. PROBLÈMES ET LEÇONS : ce qui ne s'est pas passé comme prévu et pourquoi\n6. RECOMMANDATIONS / PROCHAINES ÉTAPES : qui fait quoi pour quand\n7. ANNEXES : données, photos, reçus, sources",
    "UMUTWE: [Icyo raporo ivuga] - [Igihe] - [Uwayanditse, itariki]\n\n1. INCAMAKE: ibyagaragaye 3-5 by'ingenzi n'ibyo ugira inama\n2. INCUTI / INTEGO: impamvu y'iyi raporo\n3. IBYAKOZWE: ibikorwa cyangwa uburyo, n'amatariki\n4. IBYAGARAGAYE / IBIKURIKIRANO: ibintu n'imibare (imbonerahamwe zirafasha); vuga ibyapimwe n'ibyakekwe\n5. IBIBAZO N'AMASOMO: ibitagenze nk'uko byari biteganyijwe n'impamvu\n6. INAMA / IBIKURIKIRA: ninde ukora iki ryari\n7. IBIYONGERERWA: amakuru, amafoto, inyemezabwishyu, amasoko",
    "KICHWA: [Ripoti inahusu nini] - [Kipindi] - [Mwandishi, tarehe]\n\n1. MUHTASARI: matokeo 3-5 muhimu zaidi na mapendekezo yako\n2. UTANGULIZI / LENGO: kwa nini ripoti hii\n3. KILICHOFANYWA: shughuli au mbinu, na tarehe\n4. MATOKEO: ukweli na namba (jedwali husaidia); eleza zipi zimepimwa na zipi ni makadirio\n5. CHANGAMOTO NA MASOMO: kisichoenda kama ilivyopangwa na kwa nini\n6. MAPENDEKEZO / HATUA ZINAZOFUATA: nani afanye nini lini\n7. VIAMBATISHO: data, picha, risiti, vyanzo"),
   (["Put the conclusion first: busy readers read the summary only.", "Separate facts, estimates and opinions.", "Use short paragraphs, numbered headings and tables for figures.", "Say where each number came from."],
    ["Mettez la conclusion d'abord : le lecteur pressé ne lit que le résumé.", "Séparez faits, estimations et opinions.", "Paragraphes courts, titres numérotés, tableaux pour les chiffres.", "Dites d'où vient chaque chiffre."],
    ["Shyira umwanzuro ku isonga: usoma yihuta asoma incamake gusa.", "Tandukanya ibintu, ibyakekwe n'ibitekerezo.", "Ingingo ngufi, imitwe ifite imibare, imbonerahamwe ku mibare.", "Vuga aho buri mubare wavuye."],
    ["Weka hitimisho kwanza: msomaji mwenye haraka husoma muhtasari tu.", "Tenganisha ukweli, makadirio na maoni.", "Aya mafupi, vichwa vyenye namba, jedwali kwa namba.", "Sema kila namba imetoka wapi."]))

_t("congrats", ("congratulations message|congratulate|message of congratulations|birthday message|birthday wish|wedding message|good luck message|greeting message|wish message",
                "message de felicitations|feliciter|felicitations|message d'anniversaire|voeux|message de bonne chance",
                "ubutumwa bwo gushimira intsinzi|gushimira|ubutumwa bw'isabukuru|isabukuru|ubutumwa bw'ishimwe|kwifuriza",
                "ujumbe wa pongezi|pongezi|ujumbe wa siku ya kuzaliwa|kuzaliwa|salamu"),
   {"en": "Congratulations / good-wishes message", "fr": "Message de félicitations / de vœux", "rw": "Ubutumwa bw'ishimwe / bwo kwifuriza", "sw": "Ujumbe wa pongezi / salamu njema"},
   ("Dear [Name],\n\nCongratulations on [the achievement / event]! You worked hard for this and you deserve it.\n\nI wish you [joy / success / health] in [what comes next]. [Optional personal memory in one sentence.]\n\nWith warm wishes,\n[Your name]",
    "Cher/Chère [Nom],\n\nFélicitations pour [la réussite / l'événement] ! Vous avez travaillé dur et vous le méritez.\n\nJe vous souhaite [joie / succès / santé] pour [la suite]. [Souvenir personnel en une phrase, facultatif.]\n\nAvec mes meilleurs vœux,\n[Votre nom]",
    "Nshuti [Izina],\n\nNgushimiye kuri [icyo wagezeho / ibyabaye]! Wakoranye umwete kandi urakibikwiye.\n\nNkwifurije [ibyishimo / intsinzi / ubuzima bwiza] muri [ibikurikira]. [Icyibutsa cyawe mu nteruro imwe, si itegeko.]\n\nUbutumwa bwiza,\n[Izina ryawe]",
    "Mpendwa [Jina],\n\nHongera kwa [mafanikio / tukio]! Ulifanya kazi kwa bidii na unastahili.\n\nNakutakia [furaha / mafanikio / afya] katika [yanayofuata]. [Kumbukumbu binafsi kwa sentensi moja, hiari.]\n\nKwa salamu njema,\n[Jina lako]"),
   (["Mention the specific achievement or event.", "Add one personal line so it does not sound copied.", "Send it on the day or soon after."],
    ["Mentionnez la réussite ou l'événement précis.", "Ajoutez une ligne personnelle pour que le message ne paraisse pas copié.", "Envoyez-le le jour même ou peu après."],
    ["Vuga icyo wagezeho cyangwa ibyabaye by'ukuri.", "Ongeraho umurongo wawe bwite kugira ngo bidasa n'ibyakoporowe.", "Wohereze uwo munsi cyangwa nyuma yawo vuba."],
    ["Taja mafanikio au tukio mahususi.", "Ongeza mstari wa kibinafsi usionekane umenakiliwa.", "Tuma siku hiyo au baada yake kwa haraka."]))

_INTENT = {"en": ("write", "draft", "template", "sample", "example", "format", "help me", "compose", "how to write", "how do i write", "make me", "structure", "outline"),
           "fr": ("ecrire", "rediger", "modele", "exemple", "format", "aide-moi", "aidez-moi", "structure", "plan", "faire un", "comment ecrire"),
           "rw": ("kwandika", "andika", "icyitegererezo", "urugero", "umfashe", "nfasha", "imiterere", "nandika nte", "gutegura"),
           "sw": ("andika", "kuandika", "kiolezo", "mfano", "nisaidie", "unisaidie", "muundo", "jinsi ya kuandika")}
_IMPROVE = {"en": "improve my|proofread|rewrite my|correct my|polish my|edit my|make this sound|check my grammar|fix my writing|improve this",
            "fr": "ameliorer mon|corriger mon|reecrire mon|relire mon|ameliore ce|corrige ce",
            "rw": "kunoza inyandiko|nozaho|kosora inyandiko|kosora iyi|nosora",
            "sw": "boresha maandishi|sahihisha maandishi|andika upya|boresha hii|rekebisha maandishi"}
CHECKLIST = {
    "en": ["Purpose: can the reader tell in the first two sentences what you want?", "Reader: is the tone right (formal, friendly) for this person?", "Clarity: shorten long sentences; one idea per paragraph.", "Facts: check names, dates, amounts and attachments.", "Spelling and grammar: read it aloud once; ask someone to read it.", "Closing: say what should happen next and by when."],
    "fr": ["Objectif : le lecteur comprend-il dès les deux premières phrases ce que vous voulez ?", "Lecteur : le ton (formel, amical) convient-il ?", "Clarté : raccourcissez les phrases ; une idée par paragraphe.", "Faits : vérifiez noms, dates, montants et pièces jointes.", "Orthographe et grammaire : relisez à voix haute ; faites relire.", "Fin : dites ce qui doit se passer ensuite et pour quand."],
    "rw": ["Intego: usoma abona mu nteruro ebyiri za mbere icyo ushaka?", "Usoma: imvugo ikwiye (y'icyubahiro, y'ubucuti) kuri uyu muntu?", "Gusobanuka: gabanya interuro ndende; igitekerezo kimwe muri buri gika.", "Ukuri: genzura amazina, amatariki, imibare n'ibyometsweho.", "Imyandikire n'ikibonezamvugo: soma mu ijwi riranguruye; usabe undi gusoma.", "Umwanzuro: vuga icyakurikiraho n'igihe."],
    "sw": ["Lengo: msomaji anajua katika sentensi mbili za kwanza unachotaka?", "Msomaji: sauti (rasmi, ya kirafiki) inafaa?", "Uwazi: fupisha sentensi ndefu; wazo moja kwa aya.", "Ukweli: hakiki majina, tarehe, kiasi na viambatisho.", "Tahajia na sarufi: soma kwa sauti; mwombe mtu asome.", "Hitimisho: sema nini kifanyike baadaye na lini."]}


def _entry(tid, lang):
    t = T[tid]
    ans, title, steps = {}, {}, {}
    for l in LANGS:
        ans[l] = f"*{_LABEL[l]}*\n\n```\n{t['body'][l]}\n```\n\n{_ASK_AI[l]}"
        title[l] = t["title"][l]
        steps[l] = list(t["tips"][l])
    return entry("tpl_" + tid, "writing", title, ans, steps, dict(_TIPS_LABEL), related=["email_writing", "write_cv"])


def find(question, lang="en"):
    """A writing template when the question asks to write/draft one of the supported kinds of text; else None."""
    k = lk(lang)
    q = fold(question)
    if not q or len(q) > 220:
        return None
    # improve-my-text requests: show the checklist (the AI does the actual rewriting when a pasted text is present)
    for l in LANGS:
        if has_phrase(q, _IMPROVE[l].split("|")) and len(q.split()) <= 12:
            ans = {x: "\n".join(f"- {s}" for s in CHECKLIST[x]) + "\n\n" + _ASK_AI[x] for x in LANGS}
            title = {"en": "Improving your writing", "fr": "Améliorer votre texte", "rw": "Kunoza inyandiko yawe", "sw": "Kuboresha maandishi yako"}
            return entry("tpl_improve", "writing", title, ans)
    n = len(q.split())
    intent = any(has_phrase(q, _INTENT[l]) for l in LANGS)
    best, best_len = None, 0
    for tid, t in T.items():
        for l in LANGS:
            for a in t["al"][LANGS.index(l)].split("|"):
                if a and len(a) > best_len and has_phrase(q, [a]):
                    # one-word type aliases that are common words (letter, report, invitation ...) need a writing intent or a very short question
                    if (intent or n <= 4):
                        best, best_len = tid, len(a)
    return _entry(best, k) if best else None
