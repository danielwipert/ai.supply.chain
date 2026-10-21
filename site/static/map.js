// The home page map, vertical on every screen.
// - Draws the "river": a spine per stream, the data stream curving into the trunk where they merge.
// - Story: the tier in the middle of the screen is the current step (the rail on wide screens follows it).
// - Hovering a box traces everything upstream and downstream of it.
// - Clicking a box explodes it in place into a detail panel.
(function () {
  "use strict";

  var data = JSON.parse(document.getElementById("map-data").textContent);
  var map = document.getElementById("map");
  var svg = map.querySelector(".spine");
  var SVG_NS = "http://www.w3.org/2000/svg";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var nodeById = {}, tierById = {};
  data.nodes.forEach(function (n) { nodeById[n.id] = n; });
  data.tiers.forEach(function (t) { tierById[t.id] = t; });
  var nodeEls = {};
  map.querySelectorAll(".node").forEach(function (el) { nodeEls[el.dataset.id] = el; });
  var tierEls = {};
  map.querySelectorAll(".tier").forEach(function (el) { tierEls[el.dataset.tier] = el; });
  // Reading order: compute tiers, then the data stream, then the trunk (the order of tiers.json).
  var order = data.tiers.map(function (t) { return t.id; });

  var parents = {}, children = {};
  data.nodes.forEach(function (n) { parents[n.id] = []; children[n.id] = []; });
  data.edges.forEach(function (e) { children[e.from].push(e.to); parents[e.to].push(e.from); });

  // ---------- the river ----------
  function center(el, origin) {
    var r = el.getBoundingClientRect();
    return { x: r.left - origin.left + r.width / 2, y: r.top - origin.top + r.height / 2 };
  }

  var segs = []; // {el, tier} so the active tier's stretch can light up
  var mergeGapY = 0; // the gap just above the merge card, where the data stream crosses over

  function segment(a, b, colour, tier) {
    var d;
    if (Math.abs(a.x - b.x) < 1) {
      d = "M" + a.x + " " + a.y + " L" + b.x + " " + b.y;
    } else {
      // The data stream joining the trunk, routed like a subway line: straight down its own column,
      // across the gap just above the merge card, then down into the merge point. Never across boxes.
      var y = mergeGapY, r = 18, dir = b.x < a.x ? -1 : 1;
      d = "M" + a.x + " " + a.y + " L" + a.x + " " + (y - r) +
          " Q" + a.x + " " + y + " " + (a.x + dir * r) + " " + y +
          " L" + (b.x - dir * r) + " " + y +
          " Q" + b.x + " " + y + " " + b.x + " " + (y + r) +
          " L" + b.x + " " + b.y;
    }
    ["seg", "flow"].forEach(function (cls) {
      var p = document.createElementNS(SVG_NS, "path");
      p.setAttribute("d", d);
      p.setAttribute("class", cls);
      p.style.setProperty("--sc", colour);
      svg.appendChild(p);
      if (cls === "seg") segs.push({ el: p, tier: tier });
    });
  }

  function chain(points) {
    for (var i = 0; i + 1 < points.length; i++) segment(points[i].at, points[i + 1].at, points[i].colour, points[i].tier);
  }

  function dotsOf(stream, origin) {
    var el = map.querySelector('.stream[data-stream="' + stream + '"]');
    var pts = [];
    var head = el.querySelector(".stream-dot");
    if (head) pts.push({ at: center(head, origin), colour: stream === "data" ? "var(--d1)" : "var(--t1)", tier: null });
    el.querySelectorAll(".tier").forEach(function (t) {
      pts.push({ at: center(t.querySelector(".tier-dot"), origin), colour: "var(--" + t.dataset.tier.toLowerCase() + ")", tier: t.dataset.tier });
    });
    return pts;
  }

  function draw() {
    var origin = map.getBoundingClientRect();
    svg.setAttribute("viewBox", "0 0 " + origin.width + " " + origin.height);
    svg.textContent = "";
    segs = [];
    var compute = dotsOf("compute", origin), stream2 = dotsOf("data", origin), trunk = dotsOf("trunk", origin);
    var merge = { at: center(map.querySelector(".merge-dot"), origin), colour: "var(--t9)", tier: null };
    var end = { at: center(map.querySelector(".end-dot"), origin), colour: "var(--t11)", tier: null };
    mergeGapY = map.querySelector(".merge").getBoundingClientRect().top - origin.top - 22;
    if (Math.abs(stream2[0].at.x - compute[0].at.x) < 1) {
      // Narrow screens stack the streams, so the line runs through both, one after the other.
      chain(compute.concat(stream2, [merge]));
    } else {
      chain(compute.concat([merge]));
      chain(stream2.concat([merge]));
    }
    chain([merge].concat(trunk, [end]));
    lightSpine(currentTier);
  }

  var drawQueued = false;
  function queueDraw() {
    if (drawQueued) return;
    drawQueued = true;
    requestAnimationFrame(function () { drawQueued = false; draw(); });
  }

  function lightSpine(tierId) {
    segs.forEach(function (s) { s.el.classList.toggle("is-lit", !!tierId && s.tier === tierId); });
  }

  // ---------- tracing a box's path ----------
  function walk(start, next) {
    var seen = new Set([start]), stack = [start];
    while (stack.length) {
      next[stack.pop()].forEach(function (id) { if (!seen.has(id)) { seen.add(id); stack.push(id); } });
    }
    return seen;
  }

  function trace(id) {
    var lit = walk(id, parents);
    walk(id, children).forEach(function (x) { lit.add(x); });
    map.classList.add("is-tracing");
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.toggle("is-lit", lit.has(k)); });
  }

  function untrace() {
    if (openId) { trace(openId); return; }
    map.classList.remove("is-tracing");
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.remove("is-lit"); });
  }

  // ---------- the story (rail on wide screens; inline notes on narrow ones) ----------
  var rail = document.querySelector(".rail-card");
  var railKicker = document.querySelector("[data-rail-kicker]");
  var railHeadline = document.querySelector("[data-rail-headline]");
  var railText = document.querySelector("[data-rail-text]");
  var railNextLabel = document.querySelector("[data-rail-next-label]");
  var stepLinks = document.querySelectorAll("[data-step-link]");
  var introHTML = railText.innerHTML;
  var currentTier = null; // null = intro, "end" = past the last tier

  function streamName(tier) {
    return tier.stream === "trunk" ? "One stream" : data.story.streams[tier.stream].name;
  }

  function setCurrent(tierId) {
    if (tierId === currentTier) return;
    currentTier = tierId;
    Object.keys(tierEls).forEach(function (k) { tierEls[k].classList.toggle("is-active", k === tierId); });
    lightSpine(tierId);
    stepLinks.forEach(function (a) { a.classList.toggle("is-current", a.dataset.stepLink === tierId); });

    if (!tierId) {
      rail.style.removeProperty("--tc");
      railKicker.textContent = "Start here";
      railHeadline.textContent = data.story.intro.headline;
      railText.innerHTML = introHTML;
      railNextLabel.textContent = "Start";
    } else if (tierId === "end") {
      rail.style.setProperty("--tc", "var(--t11)");
      railKicker.textContent = "The whole chain";
      railHeadline.textContent = data.story.outro.headline;
      railText.textContent = data.story.outro.text;
      railNextLabel.textContent = "Back to the top";
    } else {
      var tier = tierById[tierId], note = data.story.tiers[tierId];
      rail.style.setProperty("--tc", "var(--" + tierId.toLowerCase() + ")");
      railKicker.textContent = streamName(tier) + " · " + tierId + " " + tier.name;
      railHeadline.textContent = note.headline;
      railText.textContent = note.text;
      railNextLabel.textContent = "Next";
    }
    rail.classList.remove("is-changing");
    void rail.offsetWidth; // restart the fade
    rail.classList.add("is-changing");
  }

  function scrollToEl(el) {
    el.scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "start" });
  }

  function step(delta) {
    var i = currentTier === null ? -1 : currentTier === "end" ? order.length : order.indexOf(currentTier);
    var next = i + delta;
    if (currentTier === "end" && delta > 0) { window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" }); return; }
    if (next < 0) return;
    if (next >= order.length) scrollToEl(document.getElementById("map-end"));
    else scrollToEl(tierEls[order[next]]);
  }
  document.querySelector("[data-rail-next]").addEventListener("click", function () { step(1); });
  document.querySelector("[data-rail-prev]").addEventListener("click", function () { step(-1); });
  document.querySelectorAll("[data-story-start]").forEach(function (b) {
    b.addEventListener("click", function () { scrollToEl(tierEls[order[0]]); });
  });

  // The tier crossing the middle of the screen is the current step.
  var watched = Object.keys(tierEls).map(function (k) { return tierEls[k]; });
  watched.push(document.getElementById("map-end"));
  var middle = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) setCurrent(e.target.id === "map-end" ? "end" : e.target.dataset.tier);
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  watched.forEach(function (w) { middle.observe(w); });
  // Above the map: back to the intro.
  new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) setCurrent(null); });
  }).observe(document.querySelector(".hero"));

  // ---------- exploding a box in place ----------
  var openId = null;
  var STATUS_TEXT = {
    planned: "In the research queue", draft: "Draft, not yet checked",
    verified: "Checked against sources", approved: "Reviewed and approved",
  };

  function el(tag, attrs, kids) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "style") node.style.cssText = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return node;
  }

  function pending() { return el("span", { class: "pending", text: "Pending research" }); }

  function tile(label, value, note) {
    return el("div", { class: "tile" }, [
      el("span", { class: "tile-label", text: label }),
      value ? el("span", { class: "tile-value cap", text: value }) : pending(),
      note ? el("span", { class: "tile-note", text: note }) : null,
    ]);
  }

  function makersSection(n) {
    var kids = [el("h4", { text: "Who makes it" })];
    if (n.detail && n.detail.makers.length) {
      n.detail.makers.forEach(function (m) {
        kids.push(el("div", { class: "ex-maker" }, [
          el("span", {}, [el("strong", { text: m.company }), m.country ? el("span", { class: "mono muted", text: " " + m.country }) : null]),
          m.share_text ? el("span", { class: "mono", text: m.share_text }) : el("span", { class: "pending", text: "Share pending" }),
          m.share != null ? el("span", { class: "share-bar" }, [el("span", { style: "width:" + Math.round(m.share * 100) + "%" })]) : null,
        ]));
      });
    } else {
      kids.push(el("p", { text: n.makers }));
    }
    if (!n.detail && n.alternatives && !/^(None|challenger|alternative|hyperscaler|startup|open-source)/i.test(n.alternatives)) {
      kids.push(el("p", { class: "small muted", text: "Also: " + n.alternatives }));
    }
    return el("div", { class: "explode-section" }, kids);
  }

  function flowList(title, ids, emptyText) {
    var kids = [el("h4", { text: title })];
    ids.forEach(function (id) {
      var m = nodeById[id];
      var b = el("button", { type: "button", style: "--tc: var(--" + m.tier.toLowerCase() + ")" },
        [el("span", { class: "mono", text: m.tier }), m.label]);
      b.addEventListener("click", function () { open(id, true); });
      kids.push(b);
    });
    if (!ids.length) kids.push(el("p", { class: "small muted", text: emptyText }));
    return el("div", {}, kids);
  }

  function render(n) {
    var d = n.detail || {};
    var closeBtn = el("button", { class: "btn btn-ghost btn-icon explode-close", type: "button", "aria-label": "Close" });
    closeBtn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
    closeBtn.addEventListener("click", function () { close(true); });
    return el("div", { class: "explode-card", style: "--tc: var(--" + n.tier.toLowerCase() + ")" }, [
      closeBtn,
      el("div", { class: "explode-meta" }, [
        el("span", { class: "status status-" + n.status }, [el("span", { class: "dot" }), STATUS_TEXT[n.status]]),
        n.concentration ? el("span", { class: "badge badge-" + n.concentration, text: n.concentration }) : null,
      ]),
      el("h3", { text: n.name }),
      el("p", { class: "lead", text: n.summary || "Its numbers (who makes it, how concentrated it is, what it costs) will appear here once research on this card is done." }),
      el("div", { class: "explode-grid" }, [
        makersSection(n),
        el("div", { class: "explode-section" }, [
          el("h4", { text: "At a glance" }),
          el("div", { class: "ex-tiles" }, [
            tile("Concentration", n.concentration, d.concentration_rule),
            tile("Price", d.price),
            tile("Lead time", d.lead_time),
          ]),
        ]),
      ]),
      d.why ? el("div", { class: "explode-section" }, [el("h4", { text: "Why it matters" }), el("p", { text: d.why })]) : null,
      el("div", { class: "explode-section ex-flow" }, [
        flowList("Fed by", parents[n.id], "Start of the chain"),
        flowList("Feeds", children[n.id], "End of the chain: you"),
      ]),
      el("div", { class: "ex-actions" }, [
        el("a", { class: "btn btn-primary", href: "c/" + n.id + "/" }, ["Open the full card"]),
        el("a", { class: "btn btn-ghost", href: "t/" + n.tier + "/" }, ["All of " + n.tier + " " + tierById[n.tier].name]),
      ]),
    ]);
  }

  function panelFor(tierId) { return document.getElementById("explode-" + tierId); }

  function close(restoreFocus) {
    if (!openId) return;
    var id = openId, n = nodeById[id];
    openId = null;
    nodeEls[id].classList.remove("is-open");
    nodeEls[id].setAttribute("aria-expanded", "false");
    panelFor(n.tier).classList.remove("is-open");
    if (restoreFocus) nodeEls[id].focus({ preventScroll: true });
    history.replaceState(null, "", location.pathname + location.search);
    untrace();
  }

  function open(id, scroll) {
    if (openId === id) { close(true); return; }
    close(false);
    var n = nodeById[id], panel = panelFor(n.tier);
    panel.querySelector(".explode-inner").replaceChildren(render(n));
    // force the closed state to paint before opening, so the panel animates
    void panel.offsetHeight;
    panel.classList.add("is-open");
    nodeEls[id].classList.add("is-open");
    nodeEls[id].setAttribute("aria-expanded", "true");
    openId = id;
    trace(id);
    history.replaceState(null, "", "#" + id);
    if (scroll) nodeEls[id].scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "center" });
  }

  Object.keys(nodeEls).forEach(function (id) {
    var node = nodeEls[id];
    node.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") trace(id); });
    node.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") untrace(); });
    node.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // let "open in new tab" work
      e.preventDefault();
      open(id, false);
    });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(true); });

  // ---------- start ----------
  new ResizeObserver(queueDraw).observe(map);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(queueDraw);
  draw();
  var fromLink = decodeURIComponent(location.hash.slice(1));
  if (nodeById[fromLink]) open(fromLink, true);
})();
