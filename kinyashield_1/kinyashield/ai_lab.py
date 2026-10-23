"""Small, safe, offline demos taken from the "learning project" section of the AI Technical Guide: a token counter, an attention calculation,
a next-word predictor with its loss, a loss calculator, a gradient-descent experiment, the chmod worked example, and a strict calculator.
Pure Python (standard library only); no file access, no network, no eval(). Output is a guide-shaped entry in four languages.
The token splitter is a TEACHING illustration, not the tokenizer of any real model."""
from __future__ import annotations
import ast, math, operator, re
from textutil import fold, lk, entry, LANGS

_ONE = lambda text: {l: text for l in LANGS}


def _out(id_, title, body):
    return entry(id_, "ai_lab", title if isinstance(title, dict) else _ONE(title), body if isinstance(body, dict) else _ONE(body))


def _T(en, fr, rw, sw):
    return {"en": en, "fr": fr, "rw": rw, "sw": sw}


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# ------------------------------------------------------------------ 1. token counter (illustration)
def split_tokens(text, max_piece=4):
    """Teaching tokenizer: words and punctuation, and long words cut into pieces of at most `max_piece` letters (so one token is not always one word)."""
    out = []
    for m in re.finditer(r"\w+|[^\w\s]", text, re.UNICODE):
        w = m.group(0)
        if len(w) <= 6 or not w.isalpha():
            out.append(w)
        else:
            out.append(w[:max_piece])
            out += ["##" + w[i:i + max_piece] for i in range(max_piece, len(w), max_piece)]
    return out


def token_demo(text):
    toks = split_tokens(text)
    words = re.findall(r"\w+", text, re.UNICODE)
    ids = [(sum(ord(c) * (i + 1) for i, c in enumerate(t)) % 50000) for t in toks]
    head = _T("Token counter (teaching illustration)", "Compteur de jetons (illustration pédagogique)", "Kubara tokens (urugero rwo kwigisha)", "Kihesabu tokeni (mfano wa kufundishia)")
    body = _T(
        f"Text: “{text[:200]}”\n\n- **Words:** {len(words)}\n- **Tokens:** {len(toks)}\n- **Tokens:** `{' | '.join(toks[:60])}`{' …' if len(toks) > 60 else ''}\n- **Pretend IDs:** `{ids[:20]}`\n\nOne token is not always one word: long words are cut into pieces and punctuation counts too. This is a simple teaching splitter; real models use their own learned tokenizers, so real counts differ.",
        f"Texte : « {text[:200]} »\n\n- **Mots :** {len(words)}\n- **Jetons :** {len(toks)}\n- **Jetons :** `{' | '.join(toks[:60])}`{' …' if len(toks) > 60 else ''}\n- **Identifiants fictifs :** `{ids[:20]}`\n\nUn jeton n'est pas toujours un mot : les mots longs sont coupés et la ponctuation compte. C'est un découpeur pédagogique simple ; les vrais modèles ont leurs propres tokeniseurs appris, donc les vrais nombres diffèrent.",
        f"Inyandiko: «{text[:200]}»\n\n- **Amagambo:** {len(words)}\n- **Tokens:** {len(toks)}\n- **Tokens:** `{' | '.join(toks[:60])}`{' …' if len(toks) > 60 else ''}\n- **Nomero z'ikitegererezo:** `{ids[:20]}`\n\nToken imwe ntiba ijambo rimwe buri gihe: amagambo maremare acibwamo ibice kandi utumenyetso nako kabarwa. Ni igikoresho cyoroshye cyo kwigisha; ibyitegererezo nyabyo bifite tokenizers zabyo, bityo imibare nyayo iratandukanye.",
        f"Maandishi: «{text[:200]}»\n\n- **Maneno:** {len(words)}\n- **Tokeni:** {len(toks)}\n- **Tokeni:** `{' | '.join(toks[:60])}`{' …' if len(toks) > 60 else ''}\n- **Vitambulisho bandia:** `{ids[:20]}`\n\nTokeni moja si neno moja kila mara: maneno marefu hukatwa vipande na alama pia huhesabiwa. Hiki ni kigawaji rahisi cha kufundishia; modeli halisi zina tokenizer zake zilizojifunzwa, kwa hiyo hesabu halisi hutofautiana.")
    return _out("lab_tokens", head, body)


# ------------------------------------------------------------------ 2. attention demo (tiny worked calculation)
_ATT_TOKENS = ["The", "book", "it"]
_ATT_K = [[0.1, 0.0], [0.9, 0.5], [0.4, 0.3]]
_ATT_V = [[0.0, 0.1], [1.0, 0.2], [0.2, 0.8]]
_ATT_Q = [0.8, 0.5]          # query for the word "it"


def softmax(xs):
    m = max(xs)
    es = [math.exp(x - m) for x in xs]
    s = sum(es)
    return [e / s for e in es]


def attention_numbers():
    d = len(_ATT_Q)
    scores = [sum(q * k for q, k in zip(_ATT_Q, key)) / math.sqrt(d) for key in _ATT_K]
    w = softmax(scores)
    out = [sum(w[i] * _ATT_V[i][j] for i in range(len(w))) for j in range(len(_ATT_V[0]))]
    return scores, w, out


def attention_demo():
    scores, w, out = attention_numbers()
    rows = "\n".join(f"| {t} | {_fmt(s)} | {_fmt(a)} |" for t, s, a in zip(_ATT_TOKENS, scores, w))
    head = _T("Attention in a tiny worked example", "L'attention dans un petit exemple chiffré", "Attention mu rugero ruto rw'imibare", "Attention katika mfano mdogo wa hesabu")
    common = f"\n\n| Token | score = q·k/√2 | weight (softmax) |\n|---|---|---|\n{rows}\n\nWeighted sum of the value vectors = **[{_fmt(out[0])}, {_fmt(out[1])}]**"
    body = _T(
        "Sentence: “The book … it”. The query vector for “it” is q = [0.8, 0.5]. Each token has a key vector k and a value vector v (made-up numbers). Steps: score = q·k/√d, softmax turns scores into weights that add to 1, then mix the value vectors by those weights." + common + "\n\nThe largest weight goes to “book”, so the new representation of “it” draws mostly on “book”. Attention is a calculation, not human concentration.",
        "Phrase : « Le livre … il ». Le vecteur requête de « il » est q = [0,8 ; 0,5]. Chaque jeton a un vecteur clé k et un vecteur valeur v (nombres inventés). Étapes : score = q·k/√d, le softmax transforme les scores en poids de somme 1, puis on mélange les vecteurs valeur selon ces poids." + common + "\n\nLe plus grand poids va à « livre » : la nouvelle représentation de « il » s'appuie surtout sur « livre ». L'attention est un calcul, pas de la concentration humaine.",
        "Interuro: «Igitabo … cyo». Vector ya query ya «cyo» ni q = [0.8, 0.5]. Buri token ifite vector ya key k n'iya value v (imibare y'urugero). Intambwe: score = q·k/√d, softmax ihindura amanota mu buremere buteranya 1, hanyuma bavanga value vectors hakurikijwe ubwo buremere." + common + "\n\nUburemere bunini bujya kuri «igitabo», bityo ishusho nshya ya «cyo» ishingira cyane kuri «igitabo». Attention ni kubara, si ukwitondera nk'umuntu.",
        "Sentensi: «Kitabu … kilikuwa». Vekta ya query ya «kilikuwa» ni q = [0.8, 0.5]. Kila tokeni ina vekta ya key k na ya value v (namba za kubuni). Hatua: score = q·k/√d, softmax hubadilisha alama kuwa uzito wenye jumla 1, kisha huchanganya vekta za value kwa uzito huo." + common + "\n\nUzito mkubwa zaidi unaenda kwa «kitabu», kwa hiyo uwakilishi mpya wa «kilikuwa» hutegemea zaidi «kitabu». Attention ni hesabu, si umakini wa binadamu.")
    return _out("lab_attention", head, body)


# ------------------------------------------------------------------ 3. next-word predictor + loss
_SAMPLE = "the cat sat on the mat . the cat ate the fish . the dog sat on the log . the cat sat on the mat ."


def bigram_counts(text):
    toks = re.findall(r"[a-z']+|\.", text.lower())
    table = {}
    for a, b in zip(toks, toks[1:]):
        table.setdefault(a, {})
        table[a][b] = table[a].get(b, 0) + 1
    return table


def next_word_distribution(text, word):
    c = bigram_counts(text).get(word.lower())
    if not c:
        return None
    tot = sum(c.values())
    return sorted(((w, n, n / tot) for w, n in c.items()), key=lambda x: (-x[2], x[0]))


def next_word_demo(text=None, word="the"):
    text = text or _SAMPLE
    dist = next_word_distribution(text, word)
    head = _T("Tiny next-word predictor", "Petit prédicteur de mot suivant", "Uhanura ijambo rikurikira muto", "Kitabiri neno linalofuata kidogo")
    if dist is None:
        msg = _T(f"The word “{word}” never appears before another word in that text, so this tiny model has nothing to predict from. Try a longer sample.",
                 f"Le mot « {word} » n'apparaît jamais avant un autre mot dans ce texte : ce petit modèle n'a rien pour prédire. Essayez un texte plus long.",
                 f"Ijambo «{word}» ntiriboneka mbere y'irindi muri iyi nyandiko, bityo iki cyitegererezo ntacyo gishingiraho. Gerageza inyandiko ndende.",
                 f"Neno «{word}» halionekani kabla ya neno lingine kwenye maandishi hayo, kwa hiyo modeli hii ndogo haina cha kutabiri. Jaribu maandishi marefu.")
        return _out("lab_nextword", head, msg)
    rows = "\n".join(f"| {w} | {n} | {_fmt(p)} | {_fmt(-math.log(p))} |" for w, n, p in dist)
    top = dist[0]
    sample = text if len(text) < 160 else text[:160] + " …"
    body = _T(
        f"Training text: “{sample}”\n\nA bigram model counts which word follows which. After **“{word}”**:\n\n| next word | count | probability | loss = −ln P |\n|---|---|---|---|\n{rows}\n\nThe most likely continuation is “{top[0]}” (P = {_fmt(top[2])}). If the true next word were that one, the loss would be {_fmt(-math.log(top[2]))}: higher probability on the correct word means lower loss. A real language model does the same job with a neural network, over a huge vocabulary and long context. Use `next word after cat in: your text` to try your own.",
        f"Texte d'entraînement : « {sample} »\n\nUn modèle bigramme compte quel mot suit quel mot. Après **« {word} »** :\n\n| mot suivant | nombre | probabilité | perte = −ln P |\n|---|---|---|---|\n{rows}\n\nLa suite la plus probable est « {top[0]} » (P = {_fmt(top[2])}). Si le vrai mot suivant était celui-là, la perte serait {_fmt(-math.log(top[2]))} : plus la probabilité du bon mot est haute, plus la perte est faible. Un vrai modèle fait le même travail avec un réseau de neurones, un immense vocabulaire et un long contexte. Essayez `next word after cat in: votre texte`.",
        f"Inyandiko yo guhugura: «{sample}»\n\nIcyitegererezo cya bigram kibara ijambo rikurikira irindi. Nyuma ya **«{word}»**:\n\n| ijambo rikurikira | umubare | amahirwe | loss = −ln P |\n|---|---|---|---|\n{rows}\n\nIkurikira rishoboka cyane ni «{top[0]}» (P = {_fmt(top[2])}). Iyo ijambo nyaryo rikurikira riza kuba iryo, loss yaba {_fmt(-math.log(top[2]))}: amahirwe menshi ku ijambo nyaryo asobanura loss nto. Icyitegererezo nyacyo gikora ibisa n'ibyo gikoresheje neural network, amagambo menshi n'imiterere ndende. Gerageza `next word after cat in: inyandiko yawe`.",
        f"Maandishi ya mafunzo: «{sample}»\n\nModeli ya bigram huhesabu neno gani hufuata neno gani. Baada ya **«{word}»**:\n\n| neno linalofuata | idadi | uwezekano | loss = −ln P |\n|---|---|---|---|\n{rows}\n\nMwendelezo unaowezekana zaidi ni «{top[0]}» (P = {_fmt(top[2])}). Ikiwa neno sahihi linalofuata lingekuwa hilo, loss ingekuwa {_fmt(-math.log(top[2]))}: uwezekano mkubwa kwa neno sahihi humaanisha loss ndogo. Modeli halisi hufanya kazi hiyo kwa mtandao wa neva, msamiati mkubwa na muktadha mrefu. Jaribu `next word after cat in: maandishi yako`.")
    return _out("lab_nextword", head, body)


def loss_value(p):
    return -math.log(p)


def loss_demo(p):
    head = _T("Cross-entropy loss for one prediction", "Perte d'entropie croisée pour une prédiction", "Cross-entropy loss ku guhanura kumwe", "Cross-entropy loss kwa ubashiri mmoja")
    if not (0 < p <= 1):
        return _out("lab_loss", head, _T("The probability must be greater than 0 and at most 1, for example `loss 0.8`.", "La probabilité doit être supérieure à 0 et au plus 1, par exemple `loss 0.8`.",
                                        "Amahirwe agomba kuba arenze 0 kandi atarenze 1, urugero `loss 0.8`.", "Uwezekano lazima uwe zaidi ya 0 na usizidi 1, mfano `loss 0.8`."))
    nats, bits = -math.log(p), -math.log2(p)
    rows = "\n".join(f"| {q} | {_fmt(-math.log(q))} |" for q in (0.99, 0.9, 0.5, 0.1, 0.01))
    body = _T(f"If the model gives the correct next token probability **P = {_fmt(p, 4)}**, then\n\n`Loss = − ln P = {_fmt(nats, 4)}` nats ({_fmt(bits, 4)} bits).\n\n| P(correct token) | loss |\n|---|---|\n{rows}\n\nHigher probability on the correct token means lower loss. Loss alone does not prove quality: also test on unseen examples.",
              f"Si le modèle donne au bon jeton suivant la probabilité **P = {_fmt(p, 4)}**, alors\n\n`Perte = − ln P = {_fmt(nats, 4)}` nats ({_fmt(bits, 4)} bits).\n\n| P(bon jeton) | perte |\n|---|---|\n{rows}\n\nPlus la probabilité du bon jeton est haute, plus la perte est faible. La perte seule ne prouve pas la qualité : testez aussi sur des exemples inédits.",
              f"Iyo icyitegererezo gihaye token nyayo ikurikira amahirwe **P = {_fmt(p, 4)}**, noneho\n\n`Loss = − ln P = {_fmt(nats, 4)}` nats ({_fmt(bits, 4)} bits).\n\n| P(token nyayo) | loss |\n|---|---|\n{rows}\n\nAmahirwe menshi ku token nyayo asobanura loss nto. Loss yonyine ntihamya ubuziranenge: gerageza no ku ngero zitabonywe.",
              f"Ikiwa modeli inatoa tokeni sahihi inayofuata uwezekano **P = {_fmt(p, 4)}**, basi\n\n`Loss = − ln P = {_fmt(nats, 4)}` nats ({_fmt(bits, 4)} bits).\n\n| P(tokeni sahihi) | loss |\n|---|---|\n{rows}\n\nUwezekano mkubwa kwa tokeni sahihi humaanisha loss ndogo. Loss pekee haithibitishi ubora: jaribu pia kwa mifano ambayo haijawahi kuonekana.")
    return _out("lab_loss", head, body)


# ------------------------------------------------------------------ 4. gradient descent experiment
def gradient_steps(xs=(1, 2, 3), ys=(2, 4, 6), w=0.0, lr=0.05, n=6):
    rows = []
    for step in range(n + 1):
        pred = [w * x for x in xs]
        loss = sum((p - y) ** 2 for p, y in zip(pred, ys)) / len(xs)
        grad = sum(2 * (p - y) * x for p, y, x in zip(pred, ys, xs)) / len(xs)
        rows.append((step, w, loss, grad))
        w = w - lr * grad
    return rows


def gradient_demo():
    rows = gradient_steps()
    table = "\n".join(f"| {s} | {_fmt(w, 4)} | {_fmt(l, 4)} | {_fmt(g, 4)} |" for s, w, l, g in rows)
    head = _T("Gradient descent experiment", "Expérience de descente de gradient", "Igerageza rya gradient descent", "Jaribio la gradient descent")
    body = _T(
        f"A one-parameter linear model **y = w·x** is fitted to the data x = [1, 2, 3], y = [2, 4, 6] (the true w is 2). Start at w = 0 with learning rate 0.05. Each step: compute the mean-squared loss, compute the gradient (how the loss changes if w changes), then update **w ← w − lr·gradient**.\n\n| step | w | loss | gradient |\n|---|---|---|---|\n{table}\n\nThe loss falls and w moves toward 2. A learning rate that is too large can overshoot; too small is slow. Real training does this for billions of parameters.",
        f"Un modèle linéaire à un paramètre **y = w·x** est ajusté aux données x = [1, 2, 3], y = [2, 4, 6] (le vrai w vaut 2). On part de w = 0 avec un taux d'apprentissage de 0,05. À chaque étape : calculer la perte quadratique moyenne, calculer le gradient (comment la perte change si w change), puis mettre à jour **w ← w − lr·gradient**.\n\n| étape | w | perte | gradient |\n|---|---|---|---|\n{table}\n\nLa perte diminue et w se rapproche de 2. Un taux trop grand peut dépasser la cible ; trop petit est lent. Le vrai entraînement fait cela pour des milliards de paramètres.",
        f"Icyitegererezo cya linear gifite parameter imwe **y = w·x** gihuzwa n'amakuru x = [1, 2, 3], y = [2, 4, 6] (w nyayo ni 2). Dutangira kuri w = 0 na learning rate 0.05. Kuri buri ntambwe: kubara loss, kubara gradient (uko loss ihinduka iyo w ihindutse), hanyuma kuvugurura **w ← w − lr·gradient**.\n\n| intambwe | w | loss | gradient |\n|---|---|---|---|\n{table}\n\nLoss iragabanuka kandi w igana kuri 2. Learning rate nini cyane ishobora kurengera; nto cyane itinda. Guhugura nyako bikora ibi ku bilioni za parameters.",
        f"Modeli ya mstari yenye kigezo kimoja **y = w·x** inafananishwa na data x = [1, 2, 3], y = [2, 4, 6] (w halisi ni 2). Anza w = 0 na learning rate 0.05. Kila hatua: kokotoa loss, kokotoa gradient (loss hubadilikaje w ikibadilika), kisha sasisha **w ← w − lr·gradient**.\n\n| hatua | w | loss | gradient |\n|---|---|---|---|\n{table}\n\nLoss hupungua na w hukaribia 2. Learning rate kubwa mno inaweza kupita lengo; ndogo mno ni polepole. Mafunzo halisi hufanya hili kwa mabilioni ya vigezo.")
    return _out("lab_gradient", head, body)


# ------------------------------------------------------------------ 5. chmod worked example
_PERM_NAME = {
    "en": ("read", "write", "execute"), "fr": ("lecture", "écriture", "exécution"), "rw": ("gusoma", "kwandika", "gukora (execute)"), "sw": ("kusoma", "kuandika", "kutekeleza"),
}
_WHO = {"en": ("owner", "group", "others"), "fr": ("propriétaire", "groupe", "autres"), "rw": ("nyirayo", "itsinda", "abandi"), "sw": ("mmiliki", "kikundi", "wengine")}
_NONE = {"en": "no permissions", "fr": "aucune permission", "rw": "nta burenganzira", "sw": "hakuna ruhusa"}


def chmod_parse(mode):
    digits = mode[-3:]
    if not re.fullmatch(r"[0-7]{3}", digits):
        return None
    return [int(d) for d in digits]


def chmod_demo(mode, filename=None):
    parts = chmod_parse(mode)
    title = _ONE(f"chmod {mode}" + (f" {filename}" if filename else ""))
    if parts is None:
        return _out("lab_chmod", title, _T("Use three octal digits from 0 to 7, for example `chmod 640 report.txt`.", "Utilisez trois chiffres octaux de 0 à 7, par exemple `chmod 640 report.txt`.",
                                         "Koresha imibare itatu y'octal kuva kuri 0 kugeza kuri 7, urugero `chmod 640 report.txt`.", "Tumia tarakimu tatu za oktali kutoka 0 hadi 7, mfano `chmod 640 report.txt`."))
    body = {}
    for l in LANGS:
        lines = []
        sym = ""
        for who, d in zip(_WHO[l], parts):
            bits = [(d & 4, _PERM_NAME[l][0], "r"), (d & 2, _PERM_NAME[l][1], "w"), (d & 1, _PERM_NAME[l][2], "x")]
            have = [n for b, n, _ in bits if b]
            sym += "".join(c if b else "-" for b, _, c in bits)
            lines.append(f"- **{who}** ({d}): " + (", ".join(have) if have else _NONE[l]))
        intro = {"en": f"`chmod {mode}` sets the permissions of {('`' + filename + '`') if filename else 'the file'} to `{sym}`. Each digit is the sum read = 4, write = 2, execute = 1:",
                 "fr": f"`chmod {mode}` règle les permissions de {('`' + filename + '`') if filename else 'le fichier'} sur `{sym}`. Chaque chiffre est la somme lecture = 4, écriture = 2, exécution = 1 :",
                 "rw": f"`chmod {mode}` ishyiraho uburenganzira bwa {('`' + filename + '`') if filename else 'dosiye'} kuri `{sym}`. Buri mubare ni igiteranyo cya gusoma = 4, kwandika = 2, gukora = 1:",
                 "sw": f"`chmod {mode}` huweka ruhusa za {('`' + filename + '`') if filename else 'faili'} kuwa `{sym}`. Kila tarakimu ni jumla ya kusoma = 4, kuandika = 2, kutekeleza = 1:"}[l]
        extra = ""
        if parts == [6, 4, 0]:
            extra = {"en": "\n\nSo 640 gives the owner read/write, the group read, and others no permissions.", "fr": "\n\nDonc 640 donne au propriétaire lecture/écriture, au groupe la lecture, et aux autres aucune permission.",
                     "rw": "\n\nRero 640 iha nyirayo gusoma/kwandika, itsinda gusoma, abandi nta burenganzira.", "sw": "\n\nKwa hiyo 640 humpa mmiliki kusoma/kuandika, kikundi kusoma, na wengine hakuna ruhusa."}[l]
        body[l] = intro + "\n\n" + "\n".join(lines) + extra
    return _out("lab_chmod", title, body)


# ------------------------------------------------------------------ 6. strict calculator (no eval)
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class CalcError(ValueError):
    pass


def safe_eval(expr):
    """Arithmetic only: numbers, + - * / // % ** and parentheses. Anything else (names, calls, attributes, huge powers) is refused."""
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    if len(expr) > 120:
        raise CalcError("too long")
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError:
        raise CalcError("syntax")

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and (abs(b) > 64 or abs(a) > 1e6):
                raise CalcError("power too large")
            try:
                return _BIN[type(n.op)](a, b)
            except ZeroDivisionError:
                raise CalcError("division by zero")
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UN:
            return _UN[type(n.op)](ev(n.operand))
        raise CalcError("not arithmetic")

    v = ev(tree)
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        raise CalcError("not finite")
    return v


def calc_demo(expr):
    head = _T("Calculator", "Calculatrice", "Kubara", "Kikokotoo")
    try:
        v = safe_eval(expr)
    except CalcError as e:
        msg = _T("I can only do plain arithmetic: numbers, + − × ÷, powers (^) and parentheses, for example `calculate 12*(3+4)`.",
                 "Je ne sais faire que de l'arithmétique simple : nombres, + − × ÷, puissances (^) et parenthèses, par exemple `calculate 12*(3+4)`.",
                 "Nshobora kubara gusa imibare yoroshye: imibare, + − × ÷, imbaraga (^) n'utubuto, urugero `calculate 12*(3+4)`.",
                 "Naweza tu hesabu rahisi: namba, + − × ÷, nguvu (^) na mabano, mfano `calculate 12*(3+4)`.")
        return _out("lab_calc", head, msg)
    shown = _fmt(v, 10) if isinstance(v, float) else str(v)
    note = _T("Always double-check important calculations.", "Revérifiez toujours les calculs importants.", "Buri gihe subiramo kugenzura imibare y'ingenzi.", "Daima hakiki hesabu muhimu.")
    return _out("lab_calc", head, {l: f"`{expr.strip()}` = **{shown}**\n\n_{note[l]}_" for l in LANGS})


# ------------------------------------------------------------------ router
_R_TOKENS = re.compile(r"^\s*(?:count tokens|token count|tokenize|tokenise|compter les jetons|compte les jetons|bara tokens|bara token|hesabu tokeni)\s*[:\-]\s*(.+?)\s*$", re.I | re.S)
_R_ATT = re.compile(r"^\s*(?:attention (?:demo|example|exercise)|demo(?:nstration)? (?:of )?attention|d[ée]mo(?:nstration)? (?:de l')?attention|attention demo|erekana attention|onyesho la attention)\s*[.!?]?\s*$", re.I)
_R_NEXT_DEMO = re.compile(r"^\s*(?:next[- ]word (?:demo|predictor|example)|predict(?:or)? (?:the )?next word demo|pr[ée]dicteur de mot suivant|demo ya neno linalofuata|ijambo rikurikira demo)\s*[.!?]?\s*$", re.I)
_R_NEXT = re.compile(r"^\s*next[- ]word after\s+([A-Za-z']+)\s+in\s*[:\-]\s*(.+?)\s*$", re.I | re.S)
_R_LOSS = re.compile(r"^\s*(?:loss|cross[- ]entropy(?: loss)?|perte|kupoteza|loss ya)\s*(?:p\s*=\s*|=\s*|for\s+|of\s+)?\s*(\d*[.,]?\d+)\s*$", re.I)
_R_GRAD = re.compile(r"^\s*(?:gradient[- ]descent (?:demo|example|experiment)|gradient (?:demo|experiment)|d[ée]mo(?:nstration)? (?:de )?(?:la )?descente de gradient|igerageza rya gradient|jaribio la gradient)\s*[.!?]?\s*$", re.I)
_R_CHMOD = re.compile(r"(?:what does|ce que fait|que fait|icyo .* gikora|nini maana ya)?\s*\bchmod\s+([0-7]{3,4})(?:\s+([\w./~-]+))?", re.I)
_R_CALC = re.compile(r"^\s*(?:calculate|calc|compute|evaluate|calculer|calcule|kubara|bara|hesabu|kokotoa)\s*[:\-]?\s*([0-9(][0-9+\-*/().,^%×÷ \t]*)\s*=?\s*\??\s*$", re.I)


def find(question, lang="en"):
    """A lab entry when the message is one of the demo commands (strict patterns, so ordinary questions are never captured), else None."""
    q = str(question or "")
    if not q.strip() or len(q) > 600:
        return None
    m = _R_TOKENS.match(q)
    if m:
        return token_demo(m.group(1))
    if _R_ATT.match(q):
        return attention_demo()
    m = _R_NEXT.match(q)
    if m:
        return next_word_demo(m.group(2), m.group(1))
    if _R_NEXT_DEMO.match(q):
        return next_word_demo()
    m = _R_LOSS.match(q)
    if m:
        try:
            return loss_demo(float(m.group(1).replace(",", ".")))
        except ValueError:
            return None
    if _R_GRAD.match(q):
        return gradient_demo()
    m = _R_CHMOD.search(q) if len(q) < 90 else None
    if m:
        return chmod_demo(m.group(1), m.group(2))
    m = _R_CALC.match(q)
    if m:
        return calc_demo(m.group(1))
    return None
