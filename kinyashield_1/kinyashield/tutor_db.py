"""Personal AI tutor (offline part): worked, step-by-step solutions for arithmetic, percentages, linear and quadratic equations,
plus a pointer to the practice quiz. Pure Python. Exact fractions are used, so answers are exact, not rounded guesses.
Explanations of other topics, and checking a learner's own working, go to the AI (assistant_engine, TUTORING rules).
fr/rw/sw wording is a draft for fluent review."""
from __future__ import annotations
import re
from fractions import Fraction
from textutil import fold, has_phrase, lk, entry, LANGS


# ---------- tiny polynomial algebra over exact fractions: {degree: coefficient} ----------
def _padd(a, b, sign=1):
    r = dict(a)
    for d, c in b.items():
        r[d] = r.get(d, 0) + sign * c
    return {d: c for d, c in r.items() if c != 0}


def _pmul(a, b):
    r = {}
    for d1, c1 in a.items():
        for d2, c2 in b.items():
            r[d1 + d2] = r.get(d1 + d2, 0) + c1 * c2
    return {d: c for d, c in r.items() if c != 0}


class _Parser:
    def __init__(self, s, var):
        self.s, self.i, self.var = s, 0, var

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ""

    def expr(self):
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.s[self.i]; self.i += 1
            v = _padd(v, self.term(), 1 if op == "+" else -1)
        return v

    def term(self):
        v = self.unary()
        while True:
            ch = self.peek()
            if ch in ("*", "/"):
                self.i += 1
                r = self.unary()
                if ch == "*":
                    v = _pmul(v, r)
                else:
                    if set(r) != {0}:
                        raise ValueError("division by a variable")
                    d = r[0]
                    v = {k: c / d for k, c in v.items()}
            elif ch and (ch.isdigit() or ch in "(.," or ch == self.var):   # implicit multiplication: 2x, 3(x+1), (x+1)(x-1)
                v = _pmul(v, self.unary())
            else:
                return v

    def unary(self):
        if self.peek() == "-":
            self.i += 1
            return {d: -c for d, c in self.unary().items()}
        if self.peek() == "+":
            self.i += 1
            return self.unary()
        return self.power()

    def power(self):
        b = self.atom()
        if self.peek() == "^":
            self.i += 1
            neg = False
            if self.peek() == "-":
                neg = True; self.i += 1
            m = re.match(r"\d+", self.s[self.i:])
            if not m:
                raise ValueError("bad exponent")
            self.i += m.end()
            e = int(m.group())
            if e > 6 or neg:
                raise ValueError("exponent")
            r = {0: Fraction(1)}
            for _ in range(e):
                r = _pmul(r, b)
            return r
        return b

    def atom(self):
        ch = self.peek()
        if ch == "(":
            self.i += 1
            v = self.expr()
            if self.peek() != ")":
                raise ValueError("missing )")
            self.i += 1
            return v
        m = re.match(r"\d+(?:[.,]\d+)?", self.s[self.i:])
        if m:
            self.i += m.end()
            return {0: Fraction(m.group().replace(",", "."))} if Fraction(m.group().replace(",", ".")) != 0 else {}
        if ch == self.var and ch:
            self.i += 1
            return {1: Fraction(1)}
        raise ValueError("unexpected " + repr(ch))


def _poly(s, var):
    p = _Parser(s, var)
    v = p.expr()
    if p.i != len(s):
        raise ValueError("trailing text")
    return v


def _num(f):
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    dec = float(f)
    return f"{f.numerator}/{f.denominator} (≈ {dec:.4g})"


# ---------- language text ----------
TX = {
    "en": dict(title_pct="Percentage", title_lin="Equation", title_quad="Quadratic equation", title_calc="Calculation", steps="Step by step",
               pct="{p}% of {n} = {n} × {p} ÷ 100 = **{r}**", pct1="Write the percentage as a fraction of 100: {p}/100.", pct2="Multiply by the number: {n} × {p} ÷ 100.",
               lin1="Write the equation as (left side) − (right side) = 0: {lin} = 0.", lin2="Move the constant to the other side: {a}{v} = {nb}.", lin3="Divide both sides by {a}: {v} = {x}.",
               check="Check: put {v} = {x} back into the original equation; both sides should be equal.",
               quad1="Write it as ax² + bx + c = 0 with a = {a}, b = {b}, c = {c}.", quad2="Discriminant D = b² − 4ac = {D}.",
               quad_two="D > 0, so there are two real solutions: x = (−b ± √D) ÷ 2a → x₁ = {x1}, x₂ = {x2}.", quad_one="D = 0, so there is one repeated solution: x = −b ÷ 2a = {x1}.",
               quad_none="D < 0, so there is no real solution (the graph never touches the x-axis).",
               ident="Both sides are always equal: every value of x is a solution.", nosol="The equation can never be true: there is no solution.",
               calc1="Work in the order: brackets, powers, multiplication/division (left to right), then addition/subtraction (left to right).", calc2="Result: **{r}**.",
               ans="Answer", noset="This tutor solves exact arithmetic and equations in one unknown (up to x²). For other problems, show me your working and ask for help, or tick “Always ask the AI”."),
    "fr": dict(title_pct="Pourcentage", title_lin="Équation", title_quad="Équation du second degré", title_calc="Calcul", steps="Pas à pas",
               pct="{p} % de {n} = {n} × {p} ÷ 100 = **{r}**", pct1="Écrivez le pourcentage comme une fraction de 100 : {p}/100.", pct2="Multipliez par le nombre : {n} × {p} ÷ 100.",
               lin1="Écrivez l'équation sous la forme (gauche) − (droite) = 0 : {lin} = 0.", lin2="Passez la constante de l'autre côté : {a}{v} = {nb}.", lin3="Divisez les deux côtés par {a} : {v} = {x}.",
               check="Vérification : remettez {v} = {x} dans l'équation de départ ; les deux côtés doivent être égaux.",
               quad1="Écrivez-la ax² + bx + c = 0 avec a = {a}, b = {b}, c = {c}.", quad2="Discriminant D = b² − 4ac = {D}.",
               quad_two="D > 0 : deux solutions réelles : x = (−b ± √D) ÷ 2a → x₁ = {x1}, x₂ = {x2}.", quad_one="D = 0 : une solution double : x = −b ÷ 2a = {x1}.",
               quad_none="D < 0 : pas de solution réelle (la courbe ne coupe jamais l'axe des x).",
               ident="Les deux côtés sont toujours égaux : tout x est solution.", nosol="L'équation n'est jamais vraie : pas de solution.",
               calc1="Ordre : parenthèses, puissances, multiplication/division (de gauche à droite), puis addition/soustraction (de gauche à droite).", calc2="Résultat : **{r}**.",
               ans="Réponse", noset="Ce tuteur résout l'arithmétique exacte et les équations à une inconnue (jusqu'à x²). Pour le reste, montrez-moi votre démarche ou cochez « Toujours demander à l'IA »."),
    "rw": dict(title_pct="Ijanisha", title_lin="Ikigereranyo (equation)", title_quad="Ikigereranyo cya kabiri (x²)", title_calc="Kubara", steps="Intambwe ku yindi",
               pct="{p}% bya {n} = {n} × {p} ÷ 100 = **{r}**", pct1="Andika ijanisha nk'agace k'ijana: {p}/100.", pct2="Kuba umubare: {n} × {p} ÷ 100.",
               lin1="Andika ikigereranyo nka (ibumoso) − (iburyo) = 0: {lin} = 0.", lin2="Jyana umubare utahindagurika ku rundi ruhande: {a}{v} = {nb}.", lin3="Gabanya impande zombi na {a}: {v} = {x}.",
               check="Igenzura: subiza {v} = {x} mu kigereranyo cya mbere; impande zombi zigomba kungana.",
               quad1="Cyandike nka ax² + bx + c = 0 ahari a = {a}, b = {b}, c = {c}.", quad2="Discriminant D = b² − 4ac = {D}.",
               quad_two="D > 0, rero hari ibisubizo bibiri nyabyo: x = (−b ± √D) ÷ 2a → x₁ = {x1}, x₂ = {x2}.", quad_one="D = 0, rero hari igisubizo kimwe gisubiramo: x = −b ÷ 2a = {x1}.",
               quad_none="D < 0, nta gisubizo nyacyo gihari (igishushanyo ntikigera ku murongo wa x).",
               ident="Impande zombi zihora zingana: agaciro kose ka x ni igisubizo.", nosol="Ikigereranyo nticyigera kiba ukuri: nta gisubizo.",
               calc1="Gukurikiranya: utubari, ingufu, gukuba/kugabanya (uva ibumoso), hanyuma guteranya/gukuramo (uva ibumoso).", calc2="Igisubizo: **{r}**.",
               ans="Igisubizo", noset="Uyu mwigisha ukemura imibare nyayo n'ibigereranyo bifite ikitazwi kimwe (kugeza kuri x²). Ibindi, nyereka uko wabikoze cyangwa uhitemo «Burigihe baza AI»."),
    "sw": dict(title_pct="Asilimia", title_lin="Mlinganyo (equation)", title_quad="Mlinganyo wa daraja la pili", title_calc="Hesabu", steps="Hatua kwa hatua",
               pct="{p}% ya {n} = {n} × {p} ÷ 100 = **{r}**", pct1="Andika asilimia kama sehemu ya 100: {p}/100.", pct2="Zidisha kwa namba: {n} × {p} ÷ 100.",
               lin1="Andika mlinganyo kama (kushoto) − (kulia) = 0: {lin} = 0.", lin2="Hamisha namba isiyobadilika upande wa pili: {a}{v} = {nb}.", lin3="Gawanya pande zote mbili kwa {a}: {v} = {x}.",
               check="Hakiki: rudisha {v} = {x} kwenye mlinganyo wa awali; pande zote mbili zinapaswa kuwa sawa.",
               quad1="Uandike kama ax² + bx + c = 0 ambapo a = {a}, b = {b}, c = {c}.", quad2="Kibaguzi D = b² − 4ac = {D}.",
               quad_two="D > 0, kwa hiyo kuna suluhisho mbili halisi: x = (−b ± √D) ÷ 2a → x₁ = {x1}, x₂ = {x2}.", quad_one="D = 0, kwa hiyo kuna suluhisho moja linalojirudia: x = −b ÷ 2a = {x1}.",
               quad_none="D < 0, hakuna suluhisho halisi (grafu haigusi mhimili wa x).",
               ident="Pande zote daima ni sawa: thamani yoyote ya x ni suluhisho.", nosol="Mlinganyo haiwi kweli kamwe: hakuna suluhisho.",
               calc1="Mpangilio: mabano, nguvu, kuzidisha/kugawanya (kutoka kushoto), kisha kujumlisha/kutoa (kutoka kushoto).", calc2="Matokeo: **{r}**.",
               ans="Jibu", noset="Mwalimu huyu hutatua hesabu halisi na milinganyo ya kitu kimoja kisichojulikana (hadi x²). Kwa mengine, nionyeshe hatua zako au chagua «Muulize AI kila mara»."),
}
_FILL = {"en": r"calculate|compute|evaluate|solve|simplify|find x|find the value of|what is|what's|whats|how much is|work out|the answer to|please|step by step|show steps|show me|equation|for x",
         "fr": r"calcule|calculer|calculez|resous|resoudre|resolvez|simplifie|simplifier|combien font|combien fait|combien|que vaut|quel est|quelle est|equation|pas a pas|s'il vous plait|svp|pour x",
         "rw": r"kubara|bara|kemura|gukemura|ni angahe|ni iki|ikigereranyo|intambwe ku yindi|nyamuneka|ubare",
         "sw": r"hesabu|tatua|kutatua|ni ngapi|ni nini|mlinganyo|hatua kwa hatua|tafadhali|nisaidie kutatua|pata thamani ya"}
_FILL_RE = re.compile(r"(?<![a-z0-9])(?:" + "|".join(_FILL.values()) + r")(?![a-z0-9])")
_PCT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:%|percent|per cent|pour cent|pourcent|ku ijana|asilimia)\s*(?:of|de|d'|ya|y'|bya|wa|cha)?\s*(\d+(?:[.,]\d+)?)")
_PCT2 = re.compile(r"(?:asilimia)\s*(\d+(?:[.,]\d+)?)\s*(?:ya|ya)\s*(\d+(?:[.,]\d+)?)")


def _clean(question):
    s = str(question or "")
    for a, b in (("²", "^2"), ("³", "^3"), ("×", "*"), ("·", "*"), ("÷", "/"), ("−", "-"), ("–", "-"), ("—", "-"), ("√", "sqrt")):
        s = s.replace(a, b)
    return fold(s)


def _plain(f):
    f = Fraction(f)
    return str(f.numerator) if f.denominator == 1 else f"({f.numerator}/{f.denominator})"


def solve(question, lang="en"):
    """Guide-shaped entry with a worked solution, or None if the text is not a supported maths problem."""
    k = lk(lang)
    q = _clean(question)
    if not q or len(q) > 120:
        return None
    t = TX[k]
    # percentage: "15% of 240"
    m = _PCT.search(q) or _PCT2.search(q)
    if m and not re.search(r"[a-z]{3,}", _FILL_RE.sub(" ", q[:m.start()] + " " + q[m.end():])):
        p, n = Fraction(m.group(1).replace(",", ".")), Fraction(m.group(2).replace(",", "."))
        return _mk(k, "tutor_pct", t["title_pct"], t["pct"].format(p=_num(p), n=_num(n), r=_num(n * p / 100)), [t["pct1"].format(p=_num(p)), t["pct2"].format(p=_num(p), n=_num(n))])
    body = _FILL_RE.sub(" ", q)
    body = re.sub(r"(?<![a-z])(?:then|and|the|of|is|a|an|in|if|=\s*\?|\?)(?![a-z])", " ", body)
    body = body.replace("?", " ").replace(",", ".").replace(" ", "")
    if not body or not re.fullmatch(r"[0-9a-z+\-*/^().=]+", body) or not re.search(r"\d", body):
        return None
    letters = set(re.findall(r"[a-z]", body))
    if len(letters) > 1 or "sqrt" in body:
        return None
    var = next(iter(letters)) if letters else ""
    if var and var in "e" and not re.search(r"\d" + var + r"|" + var + r"\d|\^|=", body):
        return None
    try:
        if "=" in body:
            if body.count("=") != 1 or not var:
                return None
            left, right = body.split("=")
            if not left or not right:
                return None
            diff = _padd(_poly(left, var), _poly(right, var), -1)
            return _equation(k, t, diff, var)
        if not re.search(r"[+\-*/^]", body.lstrip("-")) or var:
            return None
        val = _poly(body, "")
        if set(val) - {0}:
            return None
        r = val.get(0, Fraction(0))
        return _mk(k, "tutor_calc", t["title_calc"], f"{question.strip()} = **{_num(r)}**", [t["calc1"], t["calc2"].format(r=_num(r))])
    except (ValueError, ZeroDivisionError, RecursionError):
        return None


def _equation(k, t, diff, var):
    deg = max(diff) if diff else 0
    a, b, c = diff.get(2, Fraction(0)), diff.get(1, Fraction(0)), diff.get(0, Fraction(0))
    if deg == 0:
        return _mk(k, "tutor_lin", t["title_lin"], t["ident"] if not diff else t["nosol"], [])
    if deg == 1:
        x = -c / b
        lin = f"{_plain(b)}{var}" + (f" + {_plain(c)}" if c > 0 else f" − {_plain(-c)}" if c < 0 else "")
        steps = [t["lin1"].format(lin=lin), t["lin2"].format(a=_plain(b), v=var, nb=_plain(-c)), t["lin3"].format(a=_plain(b), v=var, x=_num(x)), t["check"].format(v=var, x=_num(x))]
        return _mk(k, "tutor_lin", t["title_lin"], f"**{var} = {_num(x)}**", steps)
    if deg == 2:
        D = b * b - 4 * a * c
        steps = [t["quad1"].format(a=_num(a), b=_num(b), c=_num(c)), t["quad2"].format(D=_num(D))]
        if D > 0:
            import math
            sq = Fraction(D)
            root = None
            n_, d_ = sq.numerator, sq.denominator
            rn, rd = math.isqrt(n_), math.isqrt(d_)
            if rn * rn == n_ and rd * rd == d_:
                root = Fraction(rn, rd)
            if root is not None:
                x1, x2 = (-b + root) / (2 * a), (-b - root) / (2 * a)
                steps.append(t["quad_two"].format(x1=_num(x1), x2=_num(x2)))
                ans = f"**{var}₁ = {_num(x1)}, {var}₂ = {_num(x2)}**"
            else:
                r = math.sqrt(float(D))
                x1, x2 = (-float(b) + r) / (2 * float(a)), (-float(b) - r) / (2 * float(a))
                steps.append(t["quad_two"].format(x1=f"{x1:.6g}", x2=f"{x2:.6g}"))
                ans = f"**{var}₁ ≈ {x1:.6g}, {var}₂ ≈ {x2:.6g}**"
        elif D == 0:
            x1 = -b / (2 * a)
            steps.append(t["quad_one"].format(x1=_num(x1)))
            ans = f"**{var} = {_num(x1)}**"
        else:
            steps.append(t["quad_none"])
            ans = t["quad_none"]
        return _mk(k, "tutor_quad", t["title_quad"], ans, steps)
    return None


def _mk(k, id_, title_, answer, steps):
    ttl = {l: TX[l][{"tutor_pct": "title_pct", "tutor_lin": "title_lin", "tutor_quad": "title_quad", "tutor_calc": "title_calc"}[id_]] for l in LANGS}
    ans = {l: answer for l in LANGS}
    st = {l: list(steps) for l in LANGS}
    # steps text is already in the chat language k; the same lists are stored for every language key
    return entry(id_, "tutor", ttl, ans, st, {l: TX[l]["steps"] for l in LANGS})


_QUIZ_WORDS = {"en": "quiz me|quiz|test me|practice questions|practice quiz|exam questions|revision questions|give me questions|mcq|multiple choice|practise",
               "fr": "quiz|interroge moi|interrogez moi|teste moi|questions d'entrainement|questions de revision|exercices|qcm|entrainement",
               "rw": "ikizamini|ibibazo byo kwitoza|nkorere ikizamini|kwitoza|ibibazo by'imyitozo|ibizamini",
               "sw": "jaribio|nipime|maswali ya mazoezi|maswali ya kujifunza|mazoezi|nijaribu"}
_QUIZ_MSG = {"en": "I have a **practice quiz** with answer checking and explanations of each mistake. Open **“Study: practice quiz”** just above the message box, choose a topic (maths, physics, science, digital safety, world knowledge), answer, and press *Check my answers*.\n\nYou can also ask me for a worked solution, for example “solve 2x + 3 = 11”, “15% of 240” or “x^2 - 5x + 6 = 0”, or ask me to explain any topic step by step.",
             "fr": "J'ai un **quiz d'entraînement** qui corrige vos réponses et explique chaque erreur. Ouvrez **« Étudier : quiz d'entraînement »** juste au-dessus de la zone de message, choisissez un thème (maths, physique, sciences, sécurité numérique, culture générale), répondez, puis *Vérifier mes réponses*.\n\nDemandez aussi une solution détaillée, par exemple « résous 2x + 3 = 11 », « 15 % de 240 » ou « x^2 - 5x + 6 = 0 », ou l'explication pas à pas d'un sujet.",
             "rw": "Mfite **ikizamini cyo kwitoza** gisuzuma ibisubizo byawe kikanasobanura buri kosa. Fungura **«Kwiga: ikizamini cyo kwitoza»** hejuru y'aho wandikira, uhitemo isomo (imibare, ubugenge, siyansi, umutekano wa digitale, ubumenyi rusange), usubize, ukande *Genzura ibisubizo byanjye*.\n\nNanone ushobora gusaba igisubizo gisobanuye, urugero «kemura 2x + 3 = 11», «15% ya 240» cyangwa «x^2 - 5x + 6 = 0», cyangwa gusobanurirwa isomo intambwe ku yindi.",
             "sw": "Nina **jaribio la mazoezi** linalokagua majibu yako na kueleza kila kosa. Fungua **«Jifunze: jaribio la mazoezi»** juu ya kisanduku cha ujumbe, chagua mada (hisabati, fizikia, sayansi, usalama wa kidijitali, maarifa ya jumla), jibu, kisha bonyeza *Kagua majibu yangu*.\n\nUnaweza pia kuomba suluhisho la hatua kwa hatua, mfano «tatua 2x + 3 = 11», «asilimia 15 ya 240» au «x^2 - 5x + 6 = 0», au uombe maelezo ya mada yoyote hatua kwa hatua."}
_QUIZ_TITLE = {"en": "Practice quiz", "fr": "Quiz d'entraînement", "rw": "Ikizamini cyo kwitoza", "sw": "Jaribio la mazoezi"}


def find(question, lang="en"):
    """Worked maths solution, or a pointer to the practice quiz, or None."""
    k = lk(lang)
    q = fold(question)
    if not q:
        return None
    if len(q.split()) <= 10 and any(has_phrase(q, w.split("|")) for w in _QUIZ_WORDS.values()):
        return entry("tutor_quiz", "tutor", dict(_QUIZ_TITLE), dict(_QUIZ_MSG))
    return solve(question, k)
