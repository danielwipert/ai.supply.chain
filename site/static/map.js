// The home page map: draws the links, runs the "follow the chain" story,
// traces the chain on hover/tap, and opens a quick preview of each component.
(function () {
  "use strict";

  var data = JSON.parse(document.getElementById("map-data").textContent);
  var map = document.getElementById("map");
  var svg = map.querySelector(".edges");
  var SVG_NS = "http://www.w3.org/2000/svg";
  var wide = window.matchMedia("(min-width: 1100px)");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var nodeById = {};
  data.nodes.forEach(function (n) { nodeById[n.id] = n; });
  var tierById = {};
  data.tiers.forEach(function (t) { tierById[t.id] = t; });
  var nodeEls = {};
  map.querySelectorAll(".node").forEach(function (el) { nodeEls[el.dataset.id] = el; });
  var tierEls = Array.prototype.slice.call(map.querySelectorAll(".tier"));

  var parents = {}, children = {};
  data.nodes.forEach(function (n) { parents[n.id] = []; children[n.id] = []; });
  data.edges.forEach(function (e) { children[e.from].push(e.to); parents[e.to].push(e.from); });

  // ---------- drawing the links ----------
  var paths = [];

  function box(el, origin) {
    var r = el.getBoundingClientRect();
    var x = r.left - origin.left, y = r.top - origin.top;
    return { left: x, right: x + r.width, top: y, bottom: y + r.height, cx: x + r.width / 2, cy: y + r.height / 2 };
  }

  function curve(a, b, sameTier) {
    if (wide.matches) {
      if (sameTier) {
        return "M" + a.right + " " + a.cy + " C" + (a.right + 26) + " " + a.cy + " " + (b.right + 26) + " " + b.cy + " " + b.right + " " + b.cy;
      }
      var dx = (b.left - a.right) / 2;
      return "M" + a.right + " " + a.cy + " C" + (a.right + dx) + " " + a.cy + " " + (b.left - dx) + " " + b.cy + " " + b.left + " " + b.cy;
    }
    if (sameTier && Math.abs(a.cy - b.cy) < 4) {
      return "M" + a.cx + " " + a.bottom + " C" + a.cx + " " + (a.bottom + 22) + " " + b.cx + " " + (b.bottom + 22) + " " + b.cx + " " + b.bottom;
    }
    var dy = Math.min((b.top - a.bottom) / 2, 140);
    return "M" + a.cx + " " + a.bottom + " C" + a.cx + " " + (a.bottom + dy) + " " + b.cx + " " + (b.top - dy) + " " + b.cx + " " + b.top;
  }

  function draw() {
    if (!wide.matches) { svg.textContent = ""; paths = []; return; } // narrow screens use the timeline instead
    var origin = map.getBoundingClientRect();
    svg.setAttribute("viewBox", "0 0 " + origin.width + " " + origin.height);
    svg.textContent = "";
    paths = data.edges.map(function (e) {
      var a = nodeById[e.from], b = nodeById[e.to];
      var p = document.createElementNS(SVG_NS, "path");
      p.setAttribute("d", curve(box(nodeEls[e.from], origin), box(nodeEls[e.to], origin), a.tier === b.tier));
      p.style.setProperty("--ec", "var(--" + a.tier.toLowerCase() + ")");
      svg.appendChild(p);
      return { el: p, from: e.from, to: e.to };
    });
    applyHighlight(current);
  }

  var drawQueued = false;
  function queueDraw() {
    if (drawQueued) return;
    drawQueued = true;
    requestAnimationFrame(function () { drawQueued = false; draw(); });
  }

  // ---------- highlighting ----------
  // A highlight is {nodes: Set, edge: fn(from, to) -> bool, tier: id|null}, or null for "show everything".
  var current = null;

  function applyHighlight(h) {
    map.classList.toggle("is-dimmed", !!(h && h.nodes));
    Object.keys(nodeEls).forEach(function (id) {
      nodeEls[id].classList.toggle("is-lit", !!(h && h.nodes && h.nodes.has(id)));
    });
    tierEls.forEach(function (t) { t.classList.toggle("is-active", !!(h && h.tier === t.dataset.tier)); });
    paths.forEach(function (p) {
      var lit = !!(h && h.edge(p.from, p.to));
      p.el.classList.toggle("is-lit", lit);
      p.el.classList.toggle("is-dim", !!(h && h.nodes) && !lit);
    });
  }

  function walk(start, next) {
    var seen = new Set([start]), stack = [start];
    while (stack.length) {
      next[stack.pop()].forEach(function (id) { if (!seen.has(id)) { seen.add(id); stack.push(id); } });
    }
    return seen;
  }

  // Everything upstream and downstream of one component: its whole path through the chain.
  function traceHighlight(id) {
    var up = walk(id, parents), down = walk(id, children);
    var all = new Set(up);
    down.forEach(function (x) { all.add(x); });
    return {
      nodes: all, tier: null,
      edge: function (a, b) { return (up.has(a) && up.has(b)) || (down.has(a) && down.has(b)); },
    };
  }

  function tierHighlight(tierId) {
    var nodes = new Set(data.nodes.filter(function (n) { return n.tier === tierId; }).map(function (n) { return n.id; }));
    return {
      nodes: nodes, tier: tierId,
      edge: function (a, b) { return nodes.has(a) || nodes.has(b); },
    };
  }

  var everythingFlows = { nodes: null, tier: null, edge: function () { return true; } };

  function setHighlight(h) { current = h; applyHighlight(h); }

  // ---------- the story (wide screens: step panel; narrow screens: scroll) ----------
  var lastStep = data.tiers.length + 1;
  var step = 0;
  var panel = document.getElementById("story");
  var kicker = panel.querySelector("[data-story-kicker]");
  var headline = panel.querySelector("[data-story-headline]");
  var text = panel.querySelector("[data-story-text]");
  var body = panel.querySelector(".story-body");
  var prevBtn = panel.querySelector("[data-story-prev]");
  var nextLabel = panel.querySelector("[data-next-label]");
  var dots = panel.querySelectorAll("[data-go]");
  var introText = text.innerHTML;

  function stepHighlight(s) {
    if (s === 0) return null;
    if (s === lastStep) return everythingFlows;
    return tierHighlight(data.tiers[s - 1].id);
  }

  function goTo(s) {
    step = Math.max(0, Math.min(lastStep, s));
    if (step === 0) {
      kicker.textContent = "Start here";
      headline.textContent = data.story.intro.headline;
      text.innerHTML = introText;
    } else if (step === lastStep) {
      kicker.textContent = "The whole chain";
      headline.textContent = data.story.outro.headline;
      text.textContent = data.story.outro.text;
    } else {
      var tier = data.tiers[step - 1];
      var note = data.story.tiers[tier.id];
      kicker.textContent = "Step " + step + " of " + data.tiers.length + " · " + tier.id + " " + tier.name;
      headline.textContent = note.headline;
      text.textContent = note.text;
    }
    dots.forEach(function (d) {
      var n = Number(d.dataset.go);
      d.classList.toggle("is-current", n === step);
      d.classList.toggle("is-done", n < step);
      d.setAttribute("aria-selected", n === step ? "true" : "false");
    });
    prevBtn.disabled = step === 0;
    nextLabel.textContent = step === 0 ? "Start" : step === lastStep ? "Start over" : "Next";
    body.classList.remove("is-changing");
    void body.offsetWidth; // restart the fade animation
    body.classList.add("is-changing");
    if (!drawerOpen) setHighlight(stepHighlight(step));
  }

  panel.querySelector("[data-story-next]").addEventListener("click", function () { goTo(step === lastStep ? 0 : step + 1); });
  prevBtn.addEventListener("click", function () { goTo(step - 1); });
  dots.forEach(function (d) { d.addEventListener("click", function () { goTo(Number(d.dataset.go)); }); });

  document.addEventListener("keydown", function (e) {
    if (!wide.matches || drawerOpen || e.altKey || e.ctrlKey || e.metaKey) return;
    if (/input|textarea|select/i.test(document.activeElement.tagName)) return;
    if (e.key === "ArrowRight") { goTo(step + 1); }
    else if (e.key === "ArrowLeft") { goTo(step - 1); }
  });

  document.querySelectorAll("[data-story-start]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var behavior = reduceMotion.matches ? "auto" : "smooth";
      if (wide.matches) {
        goTo(1);
        document.querySelector(".map-wrap").scrollIntoView({ behavior: behavior, block: "start" });
      } else {
        document.getElementById("tier-T1").scrollIntoView({ behavior: behavior, block: "start" });
      }
    });
  });

  // Narrow screens: the tier in the middle of the screen is the current story step.
  var observer = new IntersectionObserver(function (entries) {
    if (wide.matches || drawerOpen) return;
    entries.forEach(function (entry) {
      if (entry.isIntersecting) setHighlight(tierHighlight(entry.target.dataset.tier));
    });
  }, { rootMargin: "-45% 0px -45% 0px" });
  tierEls.forEach(function (t) { observer.observe(t); });

  // ---------- hover tracing (mouse only) ----------
  function restore() {
    if (drawerOpen) return;
    if (wide.matches) setHighlight(stepHighlight(step));
    else setHighlight(null);
  }
  Object.keys(nodeEls).forEach(function (id) {
    var el = nodeEls[id];
    el.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse" && !drawerOpen) setHighlight(traceHighlight(id)); });
    el.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") restore(); });
    el.addEventListener("focus", function () { if (!drawerOpen) setHighlight(traceHighlight(id)); });
    el.addEventListener("blur", restore);
    el.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // let "open in new tab" work
      e.preventDefault();
      openDrawer(id, el);
    });
  });

  // ---------- quick preview drawer ----------
  var drawer = document.getElementById("drawer");
  var drawerBody = drawer.querySelector("[data-drawer-body]");
  var drawerPanel = drawer.querySelector(".drawer-panel");
  var drawerOpen = false;
  var returnFocus = null;
  var STATUS_TEXT = {
    planned: "In the research queue", draft: "Draft, not yet checked",
    verified: "Checked against sources", approved: "Reviewed and approved",
  };

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "style") node.style.cssText = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function flowList(title, ids, emptyText) {
    var items = ids.map(function (id) {
      var n = nodeById[id];
      var b = el("button", { type: "button", style: "--tc: var(--" + n.tier.toLowerCase() + ")", text: n.label });
      b.addEventListener("click", function () { openDrawer(id, nodeEls[id]); });
      return b;
    });
    if (!items.length) items = [el("p", { class: "muted small", text: emptyText })];
    return el("div", {}, [el("h3", { text: title })].concat(items));
  }

  function openDrawer(id, from) {
    var n = nodeById[id], tier = tierById[n.tier];
    if (!drawerOpen) returnFocus = from || null;
    drawerPanel.style.setProperty("--tc", "var(--" + n.tier.toLowerCase() + ")");
    drawerBody.textContent = "";
    drawerBody.appendChild(el("div", { class: "drawer-meta" }, [
      el("a", { class: "tier-chip", href: "t/" + n.tier + "/", style: "--tc: var(--" + n.tier.toLowerCase() + ")" }, [
        el("span", { class: "mono", text: n.tier }), document.createTextNode(" " + tier.name),
      ]),
      el("span", { class: "status status-" + n.status }, [el("span", { class: "dot" }), document.createTextNode(STATUS_TEXT[n.status])]),
    ]));
    drawerBody.appendChild(el("h2", { id: "drawer-title", text: n.name }));
    drawerBody.appendChild(el("p", { class: "lead", text: n.summary || "Who makes it, where, how concentrated it is and what it costs: coming once research on this card is done." }));
    drawerBody.appendChild(el("div", { class: "drawer-makers" }, [el("b", { text: "Main makers" }), document.createTextNode(n.makers)]));
    drawerBody.appendChild(el("div", { class: "drawer-flow" }, [
      flowList("Fed by", parents[id], "Start of the chain"),
      flowList("Feeds", children[id], "End of the chain"),
    ]));
    drawerBody.appendChild(el("a", { class: "btn btn-primary", href: "c/" + id + "/" }, [
      document.createTextNode("Open the full card"),
    ]));

    drawerOpen = true;
    drawer.classList.add("is-open");
    drawer.removeAttribute("inert");
    drawer.setAttribute("aria-hidden", "false");
    setHighlight(traceHighlight(id));
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.toggle("is-focus", k === id); });
    drawer.querySelector(".drawer-close").focus({ preventScroll: true });
  }

  function closeDrawer() {
    if (!drawerOpen) return;
    drawerOpen = false;
    drawer.classList.remove("is-open");
    drawer.setAttribute("inert", "");
    drawer.setAttribute("aria-hidden", "true");
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.remove("is-focus"); });
    if (returnFocus) returnFocus.focus({ preventScroll: true });
    restore();
  }

  drawer.querySelectorAll("[data-drawer-close]").forEach(function (b) { b.addEventListener("click", closeDrawer); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  // ---------- start ----------
  function onLayoutChange() {
    closeDrawer();
    if (wide.matches) goTo(step); else setHighlight(null);
    queueDraw();
  }
  if (wide.addEventListener) wide.addEventListener("change", onLayoutChange);
  new ResizeObserver(queueDraw).observe(map);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(queueDraw);
  goTo(0);
  if (!wide.matches) setHighlight(null);
  draw();
})();
