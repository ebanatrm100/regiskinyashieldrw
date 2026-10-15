// node tests/parity.js : the browser detector must give the same answers as the Python one.
const fs = require("fs");
const D = JSON.parse(fs.readFileSync("web/rules.json", "utf8"));
const K = require("../web/detector.js");
const py = JSON.parse(fs.readFileSync("results/parity_python.json", "utf8"));
let bad = 0;
// Python indexes code points, JavaScript indexes UTF-16 units: only compare spans when no astral characters.
const astral = (s) => /[\ud800-\udfff]/.test(s);
py.forEach((p, i) => {
  const r = K.analyze(D, p.text);
  const jsF = r.findings.map((f) => f.id + ":" + (astral(p.text) ? "" : JSON.stringify(f.evidence.map((e) => [e[0], e[1]]))));
  const pyF = p.findings.map((f) => f.id + ":" + (astral(p.text) ? "" : JSON.stringify(f.ev)));
  const jsP = astral(p.text) ? "" : JSON.stringify(r.protective.map((e) => [e[0], e[1]]).sort());
  const pyP = astral(p.text) ? "" : JSON.stringify(p.protective);
  if (r.verdict !== p.verdict || r.language !== p.language || JSON.stringify(jsF) !== JSON.stringify(pyF) || jsP !== pyP) {
    bad++;
    console.log("MISMATCH #" + i, JSON.stringify(p.text.slice(0, 80)), "\n  py:", p.verdict, p.language, JSON.stringify(pyF), pyP, "\n  js:", r.verdict, r.language, JSON.stringify(jsF), jsP);
  }
});
console.log(bad ? `FAILED: ${bad} of ${py.length} differ` : `PARITY OK: ${py.length} messages identical (verdict, language, rules, evidence spans, protective spans)`);
process.exit(bad ? 1 : 0);
