/* KinyaShield guide retrieval. Works offline on the written guide only; says "no answer" instead of guessing.
   Shared by the browser page and the Node tests. */
(function (root) {
  "use strict";
  function fold(K, s) { return K.fold(String(s || "")).toLowerCase().replace(/[^a-z0-9'\.\- ]+/g, " ").replace(/\s+/g, " ").trim(); }
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  var cache = {};
  function kwRegex(kw) {
    if (cache[kw]) return cache[kw];
    var star = /\*$/.test(kw), base = esc(kw.replace(/\*$/, ""));
    var r = new RegExp("(^| )" + base + (star ? "[a-z0-9']*" : "") + "(?= |$)");
    return (cache[kw] = r);
  }
  var STOP = {};
  /* Score every entry. A keyword counts 2 points per word, so a phrase beats a single common word. */
  function search(K, G, query, lang) {
    var q = fold(K, query), out = [];
    if (q.length < 2) return out;
    G.forEach(function (e) {
      var score = 0, hits = [];
      Object.keys(e.keywords).forEach(function (l) {
        var w = l === lang ? 1.25 : 1;
        e.keywords[l].forEach(function (kw) {
          if (kwRegex(kw).test(q)) { var n = kw.replace(/\*$/, "").split(" ").length; score += 2 * n * w; hits.push(kw); }
        });
      });
      if (score > 0) out.push({ entry: e, score: score, hits: hits });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    return out;
  }
  /* Accept the best match only if it is clearly ahead; otherwise the caller says it does not know. */
  function best(results) {
    if (!results.length) return null;
    var top = results[0];
    if (top.score < 2) return null;
    return top;
  }
  var api = { search: search, best: best, fold: fold };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.KinyaAsk = api;
})(typeof window !== "undefined" ? window : this);
