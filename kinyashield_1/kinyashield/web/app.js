(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("ks-data").textContent);
  var K = window.KinyaDetector;
  var $ = function (id) { return document.getElementById(id); };
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode: page still works */ } }
  };
  var SIZES = [100, 112, 125, 140], THEMES = ["auto", "light", "dark"];
  var state = { lang: "en", tab: "check", last: null, exampleActive: false, size: 0, theme: "auto", fb: [], fbPicked: null };

  function t(k) { var s = D.ui[state.lang][k]; return s === undefined ? D.ui.en[k] : s; }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }

  var ICONS = {
    ok: '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l3 3 5-6"/></svg>',
    verify: '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3L2.5 20h19L12 3z"/><path d="M12 10v4.5M12 17.4v.1"/></svg>',
    high: '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2.5h8L21.5 8v8L16 21.5H8L2.5 16V8z"/><path d="M9 9l6 6M15 9l-6 6"/></svg>'
  };

  /* ---------- static text ---------- */
  function renderStatic() {
    document.documentElement.lang = state.lang;
    $("tagline").textContent = t("tagline");
    $("pasteLbl").textContent = t("paste");
    $("msg").placeholder = t("placeholder");
    $("privacy").textContent = t("privacy");
    $("go").textContent = t("analyze");
    $("clear").textContent = t("clear");
    $("tab-check").textContent = t("tab_check"); $("tab-learn").textContent = t("tab_learn"); $("tab-about").textContent = t("tab_about");
    $("langseg").setAttribute("aria-label", t("language"));
    $("sizeBtn").textContent = "A+ " + SIZES[state.size] + "%"; $("sizeBtn").setAttribute("aria-label", t("text_size"));
    $("themeBtn").textContent = t("theme") + ": " + t("theme_" + state.theme);
    var note = $("draftNote"); note.hidden = state.lang === "en"; note.textContent = t("draft_note");
    $("exTag").hidden = !state.exampleActive; $("exTag").textContent = t("example_note");
    var seg = clear($("langseg"));
    D.langs.forEach(function (l) {
      var b = el("button", "", D.langNames[l]); b.type = "button"; b.setAttribute("lang", l);
      b.setAttribute("aria-pressed", String(l === state.lang));
      b.addEventListener("click", function () { setLang(l); });
      seg.appendChild(b);
    });
    var sel = clear($("examples")), first = el("option", "", t("examples") + " …"); first.value = ""; sel.appendChild(first);
    (D.examples[state.lang] || []).forEach(function (ex, i) {
      var o = el("option", "", (ex.text.length > 58 ? ex.text.slice(0, 58) + "…" : ex.text)); o.value = String(i); sel.appendChild(o);
    });
    renderLearn(); renderAbout();
  }

  function renderLearn() {
    var p = clear($("p-learn")), box = el("div"); box.style.cssText = "display:flex;flex-direction:column;gap:14px";
    box.appendChild(el("h3", "", t("learn_title")));
    var ol = el("ol", "steps"); t("tips").forEach(function (x) { ol.appendChild(el("li", "", x)); }); box.appendChild(ol);
    box.appendChild(el("h3", "", t("scam_types_title")));
    var grid = el("div", "scamlist");
    D.rules.forEach(function (r) {
      if (r.severity === "low") return;
      var c = el("div", "card"); c.appendChild(el("span", "sev " + r.severity, t("sev_" + r.severity)));
      c.appendChild(el("h4", "", r.title[state.lang])); c.appendChild(el("p", "", r.why[state.lang]));
      var a = el("p", "small"); a.textContent = r.advice[state.lang]; c.appendChild(a); grid.appendChild(c);
    });
    box.appendChild(grid); p.appendChild(box);
  }

  function renderAbout() {
    var p = clear($("p-about")), box = el("div"); box.style.cssText = "display:flex;flex-direction:column;gap:12px";
    box.appendChild(el("h3", "", t("about_title")));
    var ul = el("ul", "about plain"); t("about").forEach(function (x) { ul.appendChild(el("li", "", x)); }); box.appendChild(ul);
    box.appendChild(el("p", "small", t("works_offline")));
    box.appendChild(el("h3", "", t("sources_title")));
    var s = el("ul", "sources plain");
    D.sources.forEach(function (src) {
      var li = el("li"); li.appendChild(el("strong", "", src.name)); li.appendChild(document.createTextNode(": " + (src.use[state.lang] || src.use.en)));
      if (src.url) { li.appendChild(document.createTextNode(" ")); var c = el("code", "", src.url); li.appendChild(c); }
      s.appendChild(li);
    });
    box.appendChild(s); box.appendChild(el("p", "small", t("sources_note")));
    box.appendChild(el("p", "small", t("version") + " " + D.version + " · " + D.rules.length + " " + t("rules_count") + " · " + D.langs.join(" / ")));
    p.appendChild(box);
  }

  /* ---------- result ---------- */
  function renderResult(res) {
    var out = clear($("result"));
    if (!res) return;
    var v = el("div", "verdict " + res.verdict);
    var ic = el("div"); ic.innerHTML = ICONS[res.verdict]; v.appendChild(ic);
    var vt = el("div"); vt.appendChild(el("h2", "", D.verdicts[res.verdict][state.lang])); vt.appendChild(el("p", "", D.noGuarantee[state.lang])); v.appendChild(vt);
    out.appendChild(v);
    out.appendChild(el("p", "small", t("detected") + ": " + D.langNames[res.language]));

    var sec = el("div"); sec.appendChild(el("h3", "", t("evidence")));
    var m = el("div", "msg"), pos = 0;
    K.highlightSpans(res).forEach(function (sp) {
      if (sp[0] > pos) m.appendChild(document.createTextNode(res.text.slice(pos, sp[0])));
      m.appendChild(el("mark", sp[2], res.text.slice(sp[0], sp[1]))); pos = sp[1];
    });
    if (pos < res.text.length) m.appendChild(document.createTextNode(res.text.slice(pos)));
    sec.appendChild(m); out.appendChild(sec);

    var main = res.findings.filter(function (f) { return f.severity !== "low"; });
    var low = res.findings.filter(function (f) { return f.severity === "low"; });
    var fsec = el("div"); fsec.appendChild(el("h3", "", t("findings")));
    var cards = el("div", "cards");
    if (!main.length) cards.appendChild(el("div", "card", t("none_found")));
    main.forEach(function (f) { cards.appendChild(card(f, true)); });
    fsec.appendChild(cards); out.appendChild(fsec);
    if (low.length) {
      var lsec = el("div"); lsec.appendChild(el("h3", "", t("low")));
      var lc = el("div", "cards"); low.forEach(function (f) { lc.appendChild(card(f, false)); }); lsec.appendChild(lc); out.appendChild(lsec);
    }
    if (res.protective.length) {
      var psec = el("div"); psec.appendChild(el("h3", "", t("protective")));
      var pc = el("div", "card"); res.protective.forEach(function (sp) { pc.appendChild(el("code", "", sp[2])); pc.appendChild(document.createTextNode(" ")); });
      psec.appendChild(pc); out.appendChild(psec);
    }
    var ssec = el("div"); ssec.appendChild(el("h3", "", t("steps")));
    var ol = el("ol", "steps"); K.nextSteps(D, res, state.lang).forEach(function (s) { ol.appendChild(el("li", "", s)); });
    ssec.appendChild(ol); out.appendChild(ssec);

    var act = el("div", "row"), cp = el("button", "btn ghost", t("copy_summary")); cp.type = "button";
    cp.addEventListener("click", function () { copyText(summary(res), cp, t("copy_summary")); });
    act.appendChild(cp); out.appendChild(act);
    out.appendChild(feedbackBox(res));
  }

  function card(f, withEvidence) {
    var c = el("div", "card"); c.appendChild(el("span", "sev " + f.severity, t("sev_" + f.severity)));
    c.appendChild(el("h4", "", f.title[state.lang])); c.appendChild(el("p", "", f.why[state.lang]));
    if (withEvidence) { var p = el("p"); f.evidence.slice(0, 3).forEach(function (e) { p.appendChild(el("code", "", e[2])); p.appendChild(document.createTextNode(" ")); }); c.appendChild(p); }
    return c;
  }

  function summary(res) {
    var lines = ["KinyaShield RW: " + D.verdicts[res.verdict][state.lang], ""];
    var main = res.findings.filter(function (f) { return f.severity !== "low"; });
    lines.push(t("reasons") + ":");
    if (!main.length) lines.push("- " + t("no_reasons"));
    main.forEach(function (f) { lines.push("- " + f.title[state.lang]); });
    lines.push("", t("steps") + ":");
    K.nextSteps(D, res, state.lang).forEach(function (s, i) { lines.push((i + 1) + ". " + s); });
    lines.push("", D.noGuarantee[state.lang]);
    return lines.join("\n");
  }

  function copyText(text, btn, label) {
    function fallback() {
      var ta = el("textarea", "exp"); ta.value = text; ta.readOnly = true; btn.parentNode.parentNode.appendChild(ta); ta.focus(); ta.select();
      btn.textContent = t("copy_failed");
    }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { btn.textContent = t("copied"); setTimeout(function () { btn.textContent = label; }, 1800); }, fallback);
      } else fallback();
    } catch (e) { fallback(); }
  }

  /* ---------- feedback (stored on this device only) ---------- */
  function loadFb() { try { state.fb = JSON.parse(store.get("ks_feedback") || "[]"); } catch (e) { state.fb = []; } if (!Array.isArray(state.fb)) state.fb = []; }
  function csvCell(s) { s = String(s == null ? "" : s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
  function fbCsv() {
    var head = ["time", "ui_language", "message_language", "verdict", "feedback", "rules", "text"];
    return [head.join(",")].concat(state.fb.map(function (r) { return head.map(function (h) { return csvCell(r[h]); }).join(","); })).join("\n");
  }
  function feedbackBox(res) {
    var box = el("div", "card"); box.appendChild(el("h4", "", t("feedback_q")));
    var row = el("div", "fb"), picked = null, btns = [];
    [["right", t("fb_right")], ["missed", t("fb_missed")], ["false_alarm", t("fb_false")]].forEach(function (o) {
      var b = el("button", "chip", o[1]); b.type = "button"; b.setAttribute("aria-pressed", "false"); btns.push(b);
      b.addEventListener("click", function () {
        picked = o[0]; btns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        state.fb.push({ time: new Date().toISOString(), ui_language: state.lang, message_language: res.language, verdict: res.verdict, feedback: o[0],
          rules: res.findings.map(function (f) { return f.id; }).join(" "), text: inc.checked ? res.text : "" });
        store.set("ks_feedback", JSON.stringify(state.fb)); status.textContent = t("fb_thanks") + " (" + state.fb.length + " " + t("fb_count") + ")";
      });
      row.appendChild(b);
    });
    box.appendChild(row);
    var incRow = el("label", "small"); incRow.style.cssText = "display:flex;gap:8px;align-items:center;margin-top:10px";
    var inc = el("input"); inc.type = "checkbox"; inc.id = "fbInclude"; incRow.appendChild(inc); incRow.appendChild(document.createTextNode(t("fb_include"))); box.appendChild(incRow);
    var status = el("p", "small"); status.setAttribute("role", "status"); box.appendChild(status);
    var ex = el("div", "row"), exp = el("button", "chip", t("fb_export")); exp.type = "button";
    exp.addEventListener("click", function () { copyText(fbCsv(), exp, t("fb_export")); });
    var clr = el("button", "chip", t("fb_clear")); clr.type = "button";
    clr.addEventListener("click", function () { state.fb = []; store.set("ks_feedback", "[]"); status.textContent = ""; });
    ex.appendChild(exp); ex.appendChild(clr); box.appendChild(ex);
    box.appendChild(el("p", "small", t("fb_help")));
    return box;
  }

  /* ---------- actions ---------- */
  function run() {
    var text = $("msg").value;
    if (!text.trim()) { state.last = null; var o = clear($("result")); o.appendChild(el("div", "card", t("paste_first"))); return; }
    state.last = K.analyze(D, text); renderResult(state.last);
  }
  function setLang(l) {
    state.lang = l; store.set("ks_lang", l);
    if (state.exampleActive) { loadExample(0); } else { renderStatic(); renderResult(state.last); }
  }
  function loadExample(i) {
    var ex = (D.examples[state.lang] || [])[i]; if (!ex) { renderStatic(); return; }
    $("msg").value = ex.text; state.exampleActive = true; renderStatic(); run();
  }
  function setTab(name) {
    state.tab = name;
    ["check", "learn", "about"].forEach(function (n) { $("p-" + n).hidden = n !== name; $("tab-" + n).setAttribute("aria-selected", String(n === name)); });
  }
  function applyTheme() {
    var r = document.documentElement; if (state.theme === "auto") r.removeAttribute("data-theme"); else r.setAttribute("data-theme", state.theme);
  }

  function init() {
    loadFb();
    var saved = store.get("ks_lang"), nav = ((navigator.language || "en") + "").slice(0, 2).toLowerCase();
    state.lang = D.langs.indexOf(saved) >= 0 ? saved : (D.langs.indexOf(nav) >= 0 ? nav : "en");
    var sz = parseInt(store.get("ks_size") || "0", 10); state.size = sz >= 0 && sz < SIZES.length ? sz : 0;
    var th = store.get("ks_theme"); state.theme = THEMES.indexOf(th) >= 0 ? th : "auto";
    document.documentElement.style.fontSize = SIZES[state.size] + "%"; applyTheme();
    $("go").addEventListener("click", function () { state.exampleActive = false; $("exTag").hidden = true; run(); });
    $("clear").addEventListener("click", function () { $("msg").value = ""; state.exampleActive = false; state.last = null; clear($("result")); $("exTag").hidden = true; $("msg").focus(); });
    $("msg").addEventListener("input", function () { if (state.exampleActive) { state.exampleActive = false; $("exTag").hidden = true; } });
    $("examples").addEventListener("change", function (e) { if (e.target.value !== "") loadExample(parseInt(e.target.value, 10)); });
    $("sizeBtn").addEventListener("click", function () { state.size = (state.size + 1) % SIZES.length; store.set("ks_size", String(state.size)); document.documentElement.style.fontSize = SIZES[state.size] + "%"; renderStatic(); });
    $("themeBtn").addEventListener("click", function () { state.theme = THEMES[(THEMES.indexOf(state.theme) + 1) % THEMES.length]; store.set("ks_theme", state.theme); applyTheme(); renderStatic(); });
    ["check", "learn", "about"].forEach(function (n) { $("tab-" + n).addEventListener("click", function () { setTab(n); }); });
    loadExample(0);
  }
  init();
})();
