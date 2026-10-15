/* KinyaShield RW detector (browser). Mirrors detector.py step for step.
   Parity with the Python version is checked by tests/parity.js. */
(function (root) {
  "use strict";
  var FLAGS = "gi";

  function fold(text) {
    text = text || "";
    var out = "";
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      if (ch === "’" || ch === "‘") { out += "'"; continue; }
      if (ch === " " || ch === " ") { out += " "; continue; }
      if (ch.charCodeAt(0) < 128) { out += ch; continue; }
      var d = ch.normalize("NFD").replace(/[̀-ͯ]/g, "");
      out += d.length === 1 ? d : ch;
    }
    return out;
  }

  function detectLanguage(D, folded) {
    var t = " " + folded.toLowerCase().replace(/[^a-z0-9' ]+/g, " ") + " ";
    var best = "en", bestN = 1;
    D.langs.forEach(function (lang) {
      var n = 0;
      D.markers[lang].forEach(function (m) { if (t.indexOf(" " + m + " ") !== -1) n++; });
      if (n > bestN) { best = lang; bestN = n; }
    });
    return best;
  }

  function sentencePrefix(text, start) {
    var last = 0, re = /[.!?\n]\s/g, m, head = text.slice(0, start);
    while ((m = re.exec(head)) !== null) last = m.index + m[0].length;
    return text.slice(last, start);
  }

  function sentence(text, start, end) {
    var first = 0, re = /[.!?\n]\s/g, m, head = text.slice(0, start);
    while ((m = re.exec(head)) !== null) first = m.index + m[0].length;
    var tail = text.slice(end), nx = /[.!?\n]\s/.exec(tail);
    return nx ? text.slice(first, end + nx.index + 1) : text.slice(first);
  }

  function anyMatch(patterns, s) {
    for (var i = 0; i < patterns.length; i++) if (new RegExp(patterns[i], "i").test(s)) return true;
    return false;
  }

  function isProtective(D, folded, start) {
    var prefix = sentencePrefix(folded, start).toLowerCase();
    var langs = Object.keys(D.protective);
    for (var i = 0; i < langs.length; i++) {
      var pats = D.protective[langs[i]];
      for (var j = 0; j < pats.length; j++) if (new RegExp(pats[j], "i").test(prefix)) return true;
    }
    return false;
  }

  function benignContext(folded, start, end, rule) {
    var sent = sentence(folded, start, end);
    if (!anyMatch(rule.unless, sent)) return false;
    return !anyMatch(rule.keep_if || [], sent);
  }

  function analyze(D, rawText) {
    var original = rawText || "";
    var folded = fold(original);
    var lang = detectLanguage(D, folded);
    var findings = [], protective = [];

    D.rules.forEach(function (rule) {
      var spans = [];
      if (rule.groups) {
        var found = [];
        for (var gi = 0; gi < rule.groups.length; gi++) {
          var hit = null, group = rule.groups[gi];
          Object.keys(group).forEach(function (l) {
            group[l].forEach(function (pat) {
              var m = new RegExp(pat, "i").exec(folded);
              if (m && (hit === null || m.index < hit[0])) hit = [m.index, m.index + m[0].length, original.slice(m.index, m.index + m[0].length)];
            });
          });
          if (hit === null) { found = []; break; }
          found.push(hit);
        }
        spans = spans.concat(found);
      } else {
        Object.keys(rule.patterns).forEach(function (l) {
          rule.patterns[l].forEach(function (pat) {
            var re = new RegExp(pat, FLAGS), m;
            while ((m = re.exec(folded)) !== null) {
              if (m[0].length === 0) { re.lastIndex++; continue; }
              var s = m.index, e = m.index + m[0].length;
              if (rule.suppress_if_protective && isProtective(D, folded, s)) { protective.push([s, e, original.slice(s, e)]); continue; }
              if (rule.unless && rule.unless.length && benignContext(folded, s, e, rule)) continue;
              spans.push([s, e, original.slice(s, e)]);
            }
          });
        });
      }
      if (spans.length) {
        var seen = {}, uniq = [];
        spans.forEach(function (sp) { var k = sp[0] + ":" + sp[1] + ":" + sp[2]; if (!seen[k]) { seen[k] = 1; uniq.push(sp); } });
        uniq.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
        findings.push({ id: rule.id, severity: rule.severity, title: rule.title, why: rule.why, advice: rule.advice, evidence: uniq });
      }
    });

    var highs = findings.filter(function (f) { return f.severity === "high"; }).length;
    var meds = findings.filter(function (f) { return f.severity === "medium"; }).length;
    var lows = findings.filter(function (f) { return f.severity === "low"; }).length;
    var nonlow = highs + meds, verdict;
    if (highs >= 2 || (highs >= 1 && (nonlow >= 2 || lows >= 1)) || (meds >= 2 && lows >= 1)) verdict = "high";
    else if (nonlow >= 1) verdict = "verify";
    else verdict = "ok";
    var order = { high: 0, medium: 1, low: 2 };
    findings.sort(function (a, b) { return order[a.severity] - order[b.severity]; });
    return { verdict: verdict, language: lang, findings: findings, protective: protective, text: original, folded: folded };
  }

  function highlightSpans(result) {
    var spans = [];
    result.findings.forEach(function (f) {
      if (f.severity === "low") return;
      f.evidence.forEach(function (e) { spans.push([e[0], e[1], f.severity]); });
    });
    spans.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
    var merged = [];
    spans.forEach(function (sp) {
      var last = merged[merged.length - 1];
      if (last && sp[0] <= last[1]) {
        last[1] = Math.max(last[1], sp[1]);
        if (sp[2] === "high" || last[2] === "high") last[2] = "high";
      } else merged.push([sp[0], sp[1], sp[2]]);
    });
    return merged;
  }

  function nextSteps(D, result, lang) {
    var steps = [];
    result.findings.forEach(function (f) {
      if (f.severity !== "low" && steps.indexOf(f.advice[lang]) === -1) steps.push(f.advice[lang]);
    });
    D.general[lang].forEach(function (g) { if (steps.indexOf(g) === -1) steps.push(g); });
    return steps;
  }

  var api = { fold: fold, analyze: analyze, highlightSpans: highlightSpans, nextSteps: nextSteps, detectLanguage: detectLanguage };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.KinyaDetector = api;
})(typeof window !== "undefined" ? window : this);
