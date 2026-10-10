"""The approved symbol (round 4) and everything that ships with it.

    python3 final.py     -> brand/logo/final/symbol/** and the Lab page

At rest: the Lift mark, three navy tiles and the amber diamond lifted 10.
In motion ("Ignite"): only the amber diamond changes. It becomes an upright
amber flame with a pale core, burns while you hover, and settles back into
the diamond. The tiles never move on hover.

Earlier rounds stay frozen in received/, v1/, v2/ and v3/.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flame as F  # noqa: E402

OUT = os.path.join(HERE, "final", "symbol")
R2 = math.sqrt(2)

NAVY, AMBER, PALE, WHITE = "#0B1F3A", "#F2A93B", "#FFE3A8", "#FFFFFF"
THEMES = {
    "light": dict(ink=NAVY, spark=AMBER, core=PALE),
    "dark": dict(ink=WHITE, spark=AMBER, core=PALE),
    "mono": dict(ink=NAVY, spark=NAVY, core=None),
    "mono-white": dict(ink=WHITE, spark=WHITE, core=None),
}

# geometry (units of the 100-unit drawing)
TILE, GAP, LIFT, RX = 24, 5, 10, 2.2
D = (TILE + GAP) / 2 * R2                 # tile centre to grid centre
POS = {"L": (50 - D, 50), "R": (50 + D, 50), "B": (50, 50 + D)}
SX, SY = 50, 50 - D - LIFT * R2           # the spark's centre
TIP = TILE / R2 - RX * (R2 - 1)           # centre to tip of a rounded tile
BOX = (50 - D - TIP, SY - TIP, 50 + D + TIP, 50 + D + TIP)   # the mark at rest
CLEAR = TILE / R2                          # clear space: half the spark's width

# motion
EASE = ".35 0 .2 1"
T_IN, T_BURN, T_OUT, T_CORE_BURN = .38, 1.1, .5, .8

DIA = F.shape(F.DIAMOND)
FL = {k: F.spline(v) for k, v in F.FLAME.items()}
CO = {k: F.spline(v, scale=.42, dy=6) for k, v in F.FLAME.items()}
CO0 = F.spline(F.FLAME["a"], scale=0, dy=6)  # the core collapsed to a point: draws nothing


def n(v, p=2):
    s = f"{v:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def view(margin=0.0, square=False, top_room=0.0, bottom_room=0.0):
    x0, y0, x1, y1 = BOX
    y0 -= top_room
    y1 += bottom_room
    x0, y0, x1, y1 = x0 - margin, y0 - margin, x1 + margin, y1 + margin
    if square:
        w, h = x1 - x0, y1 - y0
        s = max(w, h)
        x0, y0 = x0 - (s - w) / 2, y0 - (s - h) / 2
        x1, y1 = x0 + s, y0 + s
    return x0, y0, x1 - x0, y1 - y0


def anim(name, values, dur, repeat=False, attr="d"):
    k = len(values)
    rep = ' repeatCount="indefinite"' if repeat else ""
    return (f'<animate data-a="{name}" attributeName="{attr}" begin="indefinite" dur="{dur}s" fill="freeze"'
            f'{rep} calcMode="spline" '
            f'keyTimes="{";".join(n(i / (k - 1), 4) for i in range(k))}" '
            f'keySplines="{";".join([EASE] * (k - 1))}" values="{";".join(values)}"/>')


def timeline(values, times, dur, attr="d", repeat=True, type_=None):
    """One self-running SMIL track (for files that play on their own)."""
    tag = "animateTransform" if type_ else "animate"
    t = f' type="{type_}"' if type_ else ""
    rep = ' repeatCount="indefinite"' if repeat else ' fill="freeze"'
    return (f'<{tag} attributeName="{attr}"{t} begin="0s" dur="{dur}s"{rep} calcMode="spline" '
            f'keyTimes="{";".join(n(x, 4) for x in times)}" keySplines="{";".join([EASE] * (len(values) - 1))}" '
            f'values="{";".join(values)}"/>')


def tiles(t, intro=None):
    out = ""
    for i, k in enumerate(("L", "B", "R")):
        cx, cy = POS[k]
        h = TILE / 2
        a = ""
        if intro:
            s0 = .08 * i / intro
            vals, times = ["0", "1.06", "1", "1"], [s0, s0 + .4 / intro, s0 + .55 / intro, 1]
            if s0 > 0:
                vals, times = ["0"] + vals, [0] + times
            a = timeline(vals, times, intro, attr="transform", repeat=False, type_="scale")
        out += (f'<g transform="translate({n(cx)} {n(cy)})"><g class="wq-t wq-t{i + 1}">{a}<rect x="{-h}" y="{-h}" '
                f'width="{TILE}" height="{TILE}" rx="{RX}" fill="{t["ink"]}" transform="rotate(45)"/></g></g>')
    return out


def spark(t, mode="static", d=None, core_d=None):
    """mode: static | live (hover kit) | loop (self-running file)."""
    amber, core = t["spark"], t["core"]
    if mode == "live":
        body = (f'<path class="wq-sf" fill="{amber}" d="{DIA}">'
                + anim("in", [DIA, FL["a"]], T_IN)
                + anim("flicker", [FL["a"], FL["c"], FL["b"], FL["a"]], T_BURN, True)
                + anim("out", [FL["a"], DIA], T_OUT) + "</path>")
        if core:
            body += (f'<path fill="{core}" d="{CO0}">'
                     + anim("in", [CO0, CO["a"]], T_IN)
                     + anim("flicker", [CO["b"], CO["a"], CO["c"], CO["b"]], T_CORE_BURN, True)
                     + anim("out", [CO["a"], CO0], T_OUT - .1) + "</path>")
    elif mode == "loop":
        vals = [DIA, DIA, FL["a"], FL["c"], FL["b"], FL["a"], FL["c"], FL["a"], DIA, DIA]
        times = [0, .2, .29, .4, .51, .62, .73, .84, .95, 1]
        body = f'<path fill="{amber}" d="{DIA}">{timeline(vals, times, 4.4)}</path>'
        if core:
            cv = [CO0, CO0, CO["a"], CO["b"], CO["c"], CO["a"], CO["b"], CO["a"], CO0, CO0]
            body += f'<path fill="{core}" d="{CO0}">{timeline(cv, times, 4.4)}</path>'
    else:
        body = f'<path fill="{amber}" d="{d or DIA}"/>'
        if core_d and core:
            body += f'<path fill="{core}" d="{core_d}"/>'
    return f'<g transform="translate({n(SX)} {n(SY)})"><g class="wq-s">{body}</g></g>'


def svg(content, vb, cls="", style="", bg=None, extra=""):
    x, y, w, h = vb
    b = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{bg}"/>' if bg else ""
    c = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(x)} {n(y)} {n(w)} {n(h)}" '
            f'width="{n(w)}" height="{n(h)}"{c}{st}{extra}>{b}{content}</svg>')


def symbol(theme="light", bg=None, margin=4, square=False):
    t = THEMES[theme]
    return svg(tiles(t) + spark(t), view(margin, square), bg=bg)


def symbol_live(theme="light"):
    """Inline SVG for the web: hover kit hooks; the flame rises above the box
    (give the svg overflow: visible)."""
    t = THEMES[theme]
    return svg(tiles(t) + spark(t, "live"), view(2), cls="wq wq-ignite", style=f"--wq-ink:{t['ink']}",
               extra=' overflow="visible" role="img" aria-label="وقّاد"')


def spark_live_only(theme="dark"):
    """Only the igniting spark, for small UI such as a button icon."""
    t = THEMES[theme]
    x0, y0 = SX - TIP - 1, SY - TIP - 1
    return svg(spark(t, "live"), (x0, y0, 2 * TIP + 2, 2 * TIP + 2), cls="wq wq-ignite",
               extra=' overflow="visible" aria-hidden="true"')


def symbol_loop(theme="light", bg=None):
    t = THEMES[theme]
    return svg(tiles(t) + spark(t, "loop"), view(4, top_room=48), bg=bg)


def symbol_intro(theme="dark", bg=NAVY, dur=5.0):
    """Plays once: tiles pop, the spark rises and warms, ignites, burns, settles."""
    t = THEMES[theme]
    T = lambda s: s / dur  # noqa: E731
    lift = LIFT * R2
    # spark: scale at home, rise, warm, ignite, burn, settle
    rise = timeline([f"0 {n(lift)}", f"0 {n(lift)}", "0 -3", "0 0", "0 0"],
                    [0, T(.64), T(1.04), T(1.35), 1], dur, attr="transform", repeat=False, type_="translate")
    grow = timeline(["0", "0", "1", "1"], [0, T(.25), T(.64), 1], dur, attr="transform", repeat=False, type_="scale")
    warm = timeline([t["ink"], t["ink"], t["spark"], t["spark"]], [0, T(.69), T(1.08), 1], dur, attr="fill", repeat=False)
    keys = [0, T(1.35), T(1.73), T(2.1), T(2.5), T(2.9), T(3.3), T(3.8), 1]
    shape = timeline([DIA, DIA, FL["a"], FL["c"], FL["b"], FL["c"], FL["a"], DIA, DIA], keys, dur, repeat=False)
    core = ""
    if t["core"]:
        cshape = timeline([CO0, CO0, CO["a"], CO["b"], CO["c"], CO["b"], CO["a"], CO0, CO0], keys, dur, repeat=False)
        core = f'<path fill="{t["core"]}" d="{CO0}">{cshape}</path>'
    sp = (f'<g transform="translate({n(SX)} {n(SY)})"><g>{rise}<g>{grow}'
          f'<path fill="{t["ink"]}" d="{DIA}">{warm}{shape}</path>{core}</g></g></g>')
    # equal room above and below, so the mark at rest sits in the middle of the frame
    return svg(tiles(t, intro=dur) + sp, view(4, square=True, top_room=48, bottom_room=48), bg=bg)


def app_icon(bg=NAVY, pad=.2):
    t = THEMES["dark"]
    x, y, w, h = view(0, square=True)
    s = 100 * (1 - 2 * pad) / w
    tx, ty = 100 * pad - x * s, 100 * pad - y * s
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
            f'<rect width="100" height="100" rx="22" fill="{bg}"/>'
            f'<g transform="translate({n(tx)} {n(ty)}) scale({s:.4f})">{tiles(t)}{spark(t)}</g></svg>')


def frame(d, core_d, theme="dark", bg=NAVY):
    t = THEMES[theme]
    return svg(tiles(t) + spark(t, d=d, core_d=core_d), view(6, square=True, top_room=46), bg=bg)


def construction():
    """Drawing of the geometry: the unrotated cells, the lift, the clear space."""
    t = THEMES["light"]
    x, y, w, h = view(CLEAR + 8, square=True)
    guide = "#8FA1B8"
    g = []
    # clear-space frame
    bx0, by0, bx1, by1 = BOX
    g.append(f'<rect x="{n(bx0 - CLEAR)}" y="{n(by0 - CLEAR)}" width="{n(bx1 - bx0 + 2 * CLEAR)}" '
             f'height="{n(by1 - by0 + 2 * CLEAR)}" fill="none" stroke="{AMBER}" stroke-width=".5" stroke-dasharray="2 2"/>')
    g.append(f'<rect x="{n(bx0)}" y="{n(by0)}" width="{n(bx1 - bx0)}" height="{n(by1 - by0)}" fill="none" '
             f'stroke="{guide}" stroke-width=".35"/>')
    # the 2x2 grid before rotation, and the spark's home cell
    cells = ""
    step = TILE + GAP
    for cx, cy in ((-step / 2, -step / 2), (step / 2, -step / 2), (-step / 2, step / 2), (step / 2, step / 2)):
        cells += (f'<rect x="{n(cx - TILE / 2)}" y="{n(cy - TILE / 2)}" width="{TILE}" height="{TILE}" rx="{RX}" '
                  f'fill="none" stroke="{guide}" stroke-width=".35" stroke-dasharray="1.2 1.2"/>')
    g.append(f'<g transform="translate(50 50) rotate(45)">{cells}</g>')
    body = tiles(t) + spark(t)
    # lift arrow from home to spark centre
    hy = 50 - D
    g.append(f'<line x1="{n(SX - 22)}" y1="{n(hy)}" x2="{n(SX - 22)}" y2="{n(SY)}" stroke="{guide}" stroke-width=".4"/>')
    for yy in (hy, SY):
        g.append(f'<line x1="{n(SX - 24.5)}" y1="{n(yy)}" x2="{n(SX - 19.5)}" y2="{n(yy)}" stroke="{guide}" stroke-width=".4"/>')
    lab = 'font-family="IBM Plex Mono, monospace" font-size="3.2" fill="#5A6B82"'
    g.append(f'<text x="{n(SX - 26)}" y="{n((hy + SY) / 2 + 1)}" text-anchor="end" {lab}>lift 10</text>')
    g.append(f'<text x="{n(bx0 - CLEAR + 1.5)}" y="{n(by0 - CLEAR + 4.5)}" {lab}>clear space = ½ spark</text>')
    g.append(f'<text x="{n(bx0)}" y="{n(by1 + 5)}" {lab}>tile 24 · gap 5 · corner 2.2 · 45°</text>')
    return svg("".join(g) + body, (x, y, w, h))


MOTION_CSS = """/* Waqqad symbol: the motion kit for the web.
 * Pair with waqqad-symbol-motion.js. The SVG is waqqad-symbol-live.svg,
 * pasted inline. Only the spark moves; the tiles never do on hover. */
.wq { overflow: visible; }
.wq .wq-t, .wq .wq-s { transform-box: fill-box; transform-origin: 50% 50%; }

/* entrance: add .wq-intro once (the script does this for you) */
.wq-intro .wq-t { animation: wq-pop .55s cubic-bezier(.2, .8, .2, 1) both; }
.wq-intro .wq-t2 { animation-delay: .08s; }
.wq-intro .wq-t3 { animation-delay: .16s; }
.wq-intro .wq-s { animation: wq-rise 1.1s .25s cubic-bezier(.3, .7, .2, 1) both; }
.wq-intro .wq-sf { animation: wq-warm 1.1s .25s both; }

@keyframes wq-pop { 0% { transform: scale(0); opacity: 0; } 70% { transform: scale(1.06); opacity: 1; } 100% { transform: scale(1); } }
@keyframes wq-rise {
  0% { transform: translateY(14.14px) scale(0); }
  35% { transform: translateY(14.14px) scale(1); }
  72% { transform: translateY(-3px); }
  100% { transform: translateY(0); }
}
@keyframes wq-warm { 0%, 40% { fill: var(--wq-ink, #0B1F3A); } 75%, 100% { fill: #F2A93B; } }

@media (prefers-reduced-motion: reduce) {
  .wq *, .wq { animation: none !important; transition: none !important; }
}
"""

MOTION_JS = """// Waqqad symbol: the motion kit for the web.
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
"""


def build():
    os.makedirs(OUT, exist_ok=True)
    files = {
        "waqqad-symbol.svg": symbol("light"),
        "waqqad-symbol-on-dark.svg": symbol("dark"),
        "waqqad-symbol-navy-bg.svg": symbol("dark", bg=NAVY, margin=CLEAR, square=True),
        "waqqad-symbol-mono.svg": symbol("mono"),
        "waqqad-symbol-mono-white.svg": symbol("mono-white"),
        "waqqad-app-icon.svg": app_icon(),
        "motion/waqqad-symbol-live.svg": symbol_live("light"),
        "motion/waqqad-symbol-live-on-dark.svg": symbol_live("dark"),
        "motion/waqqad-symbol-loop.svg": symbol_loop("light"),
        "motion/waqqad-symbol-loop-navy.svg": symbol_loop("dark", bg=NAVY),
        "motion/waqqad-symbol-intro-navy.svg": symbol_intro("dark", bg=NAVY),
        "motion/waqqad-symbol-intro.svg": symbol_intro("light", bg=None),
        "motion/waqqad-symbol-motion.css": MOTION_CSS,
        "motion/waqqad-symbol-motion.js": MOTION_JS,
    }
    for k, v in files.items():
        p = os.path.join(OUT, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(v)
    return files


def lab_data(files):
    return {
        "live": {"dark": symbol_live("dark"), "light": symbol_live("light")},
        "sparkOnly": spark_live_only("dark"),
        "static": {k: files[k] for k in ("waqqad-symbol.svg", "waqqad-symbol-on-dark.svg", "waqqad-symbol-mono.svg",
                                         "waqqad-symbol-mono-white.svg", "waqqad-app-icon.svg")},
        "loop": files["motion/waqqad-symbol-loop.svg"],
        "intro": files["motion/waqqad-symbol-intro-navy.svg"],
        "poster": frame(FL["a"], CO["a"]),
        "frames": [
            {"label": "Rest", "svg": frame(DIA, None)},
            {"label": "Ignite · 0.38 s", "svg": frame(FL["a"], CO["a"])},
            {"label": "Burn · sway left", "svg": frame(FL["b"], CO["b"])},
            {"label": "Burn · tall", "svg": frame(FL["c"], CO["c"])},
            {"label": "Settle · 0.5 s", "svg": frame(DIA, None)},
        ],
        "construction": construction(),
        "files": sorted(list(files) + ["png/waqqad-app-icon-1024.png", "png/waqqad-app-icon-512.png",
                                       "png/waqqad-app-icon-180.png", "png/favicon-32.png", "png/favicon-16.png",
                                       "png/waqqad-symbol-1024.png", "png/waqqad-symbol-on-dark-1024.png",
                                       "video/waqqad-symbol-intro-1080p.mp4",
                                       "video/waqqad-symbol-intro-1080p.webm"]),
    }


def write_lab(data):
    """The symbol's sign-off sheet: brand/symbol.html (the Lab moves on to type)."""
    with open(os.path.join(HERE, "signoff_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    page = tpl.replace("/*DATA*/{}", json.dumps(data, ensure_ascii=False)).replace("/*MOTION_CSS*/", MOTION_CSS)
    # the hosted preview publishes the video next to the page; the repo page points into final/
    with open(os.path.join(HERE, "symbol.fragment.html"), "w", encoding="utf-8") as f:
        f.write(page.replace("/*VIDEO_SRC*/", "waqqad-symbol-intro-1080p"))
    page = page.replace("/*VIDEO_SRC*/", "logo/final/symbol/video/waqqad-symbol-intro-1080p")
    head, _, body = page.partition("</style>")
    with open(os.path.join(HERE, "..", "symbol.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


if __name__ == "__main__":
    files = build()
    write_lab(lab_data(files))
    print(f"final symbol: {len(files)} files -> {OUT}")
