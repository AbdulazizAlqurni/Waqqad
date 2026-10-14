// Waqqad symbol: the motion kit for the web.
// Inline waqqad-symbol-live.svg, include waqqad-symbol-motion.css, then:
//   WaqqadSymbol.bind(el)        hover/focus/tap on el lights the spark
//   WaqqadSymbol.entrance(svg)   page-load entrance (rise, ignite, settle)
//   WaqqadSymbol.burn(svg, on)   keep the flame lit, e.g. while loading
(function (root) {
  var IN = 380, BURN_AFTER_ENTRANCE = 1950;
  var reduce = root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function anims(svg, name) { return svg ? svg.querySelectorAll('animate[data-a="' + name + '"]') : []; }
  function run(list, fn) { for (var i = 0; i < list.length; i++) { try { list[i][fn](); } catch (e) {} } }
  function ignite(svg) {
    if (!svg || reduce || svg._lit) return;
    clearTimeout(svg._t);
    run(anims(svg, "flicker"), "endElement");
    run(anims(svg, "in"), "beginElement");
    svg._t = setTimeout(function () { run(anims(svg, "flicker"), "beginElement"); }, IN);
    svg._lit = true;
  }
  function settle(svg) {
    if (!svg || !svg._lit || svg._hold) return;
    clearTimeout(svg._t);
    run(anims(svg, "flicker"), "endElement");
    run(anims(svg, "out"), "beginElement");
    svg._lit = false;
  }
  function bind(el, svg) {
    svg = svg || el.querySelector("svg.wq");
    ["mouseenter", "focusin"].forEach(function (e) { el.addEventListener(e, function () { ignite(svg); }); });
    ["mouseleave", "focusout"].forEach(function (e) { el.addEventListener(e, function () { settle(svg); }); });
    el.addEventListener("touchstart", function () { ignite(svg); setTimeout(function () { settle(svg); }, 1600); }, { passive: true });
  }
  function entrance(svg) {
    if (!svg || reduce) return;
    svg.classList.remove("wq-intro"); void svg.getBoundingClientRect(); svg.classList.add("wq-intro");
    setTimeout(function () { ignite(svg); }, 1350);
    setTimeout(function () { settle(svg); }, 1350 + BURN_AFTER_ENTRANCE);
    setTimeout(function () { svg.classList.remove("wq-intro"); }, 2400);
  }
  function burn(svg, on) {
    svg._hold = !!on;
    if (on) { svg._lit = false; ignite(svg); } else { settle(svg); }
  }
  root.WaqqadSymbol = { ignite: ignite, settle: settle, bind: bind, entrance: entrance, burn: burn };
})(window);
