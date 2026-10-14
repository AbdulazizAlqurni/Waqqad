"""Round 3: the symbol only. The grid of four diamonds and its spark, which
can become a flame.

Each variant is the round 2 grid (three navy tiles, spark lifted 10) with a
different spark. Motion uses two systems that share one controller in the Lab:
SMIL <animate> for shape morphs (diamond -> flame, flicker), because it runs in
every browser and inside <img>; CSS (spark-motion.css) for the grid's entrance
and for the small floating diamonds.
"""
import math

import flame as F

R2 = math.sqrt(2)
TILE, GAP, LIFT, RX = 24, 5, 10, 2.2
D = (TILE + GAP) / 2 * R2
POS = {"L": (50 - D, 50), "R": (50 + D, 50), "B": (50, 50 + D)}
SX, SY = 50, 50 - D - LIFT * R2          # spark centre
VIEW = (-12, -30, 124, 130)              # room for the tallest flame and for motion
LEAN_LEFT = True                          # flames lean left: forward for Arabic readers
CORE = "#FFE3A8"                          # proposed light amber for the flame's core (question F-2)

SPLINE = ".35 0 .2 1"


def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def tile_el(cx, cy, fill, key):
    h = TILE / 2
    return (f'<g transform="translate({n(cx)} {n(cy)})"><g class="wq-t wq-t{key}">'
            f'<rect x="{-h}" y="{-h}" width="{TILE}" height="{TILE}" rx="{RX}" fill="{fill}" '
            f'transform="rotate(45)"/></g></g>')


def anim(name, values, dur, repeat=False, attr="d", begin="indefinite"):
    vals = ";".join(values)
    k = len(values)
    times = ";".join(n(i / (k - 1)) for i in range(k))
    splines = ";".join([SPLINE] * (k - 1))
    rep = ' repeatCount="indefinite"' if repeat else ""
    return (f'<animate data-a="{name}" attributeName="{attr}" begin="{begin}" dur="{dur}s" fill="freeze"'
            f'{rep} calcMode="spline" keyTimes="{times}" keySplines="{splines}" values="{vals}"/>')


def loop_anim(values, times, dur, attr="d"):
    """A self-running loop for the stand-alone motion files."""
    splines = ";".join([SPLINE] * (len(values) - 1))
    return (f'<animate attributeName="{attr}" begin="0s" dur="{dur}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="{";".join(n(t) for t in times)}" keySplines="{splines}" '
            f'values="{";".join(values)}"/>')


def fl(spec, **kw):
    return F.shape(spec, mirror=LEAN_LEFT, **kw)


DIA = F.shape(F.DIAMOND)
EMB = {k: fl(v) for k, v in F.EMBER.items()}
FAC = {k: fl(v) for k, v in F.FACET.items()}
COREF = F.core_frames(LEAN_LEFT)
CORE0 = F.spline(F.EMBER["a"], mirror=LEAN_LEFT, scale=0.01, dy=6)  # core collapsed to a point


def inner(scale):
    """Diamond with a flame-shaped hole: one path, even-odd fill."""
    return {k: DIA + F.spline(F.EMBER[k], mirror=LEAN_LEFT, scale=scale, dy=4) for k in F.EMBER}


INNER = inner(0.4)
INNER_BIG = inner(0.52)


VARIANTS = {
    "ignite": dict(
        name="Ignite", ar="الاشتعال", tag="Lift at rest",
        idea="Your favourite, unchanged at rest: the lifted diamond. When it moves, the diamond catches fire. It becomes a flame, flickers, then settles back into a diamond. The logo stays calm on contracts and stamps; the flame lives on screens.",
        motion="Hover: the diamond ignites and keeps burning while you stay. Entrance: the grid assembles, the spark rises, ignites, then settles. Loop: it breathes between diamond and flame.",
        small="At rest it is the round 2 mark, so it holds at 16 px.",
        rest="diamond"),
    "ember": dict(
        name="Ember", ar="الجمرة",
        idea="The spark is a soft flame whose bulb sits exactly where the diamond sat. The grid is the torch and the flame is what it carries.",
        motion="Hover: the flame stretches taller. Loop: a slow flicker. Entrance: it grows out of a diamond.",
        small="Reads as a drop of amber below 24 px. Watch that it never reads as water.",
        rest="flame"),
    "core": dict(
        name="Ember core", ar="قلب الجمرة",
        idea="The same flame with a pale hot core. It is the richest of the five and the most like real fire, but it needs a second amber.",
        motion="Hover: the core brightens and both layers flicker out of step, which reads as heat. Loop: a living flame for video backgrounds.",
        small="The core vanishes below 32 px and leaves the plain Ember.",
        rest="flame"),
    "facet": dict(
        name="Facet", ar="اللهب المضلّع",
        idea="A geometric flame: the lower half is exactly the diamond, and the top splits into two tongues. It is cut from the same straight lines as the grid, so it stays Najdi and institutional.",
        motion="Hover: the tongues trade heights, like a flame caught in a draught. Loop: a crisp, angular flicker.",
        small="The two tongues hold down to 24 px; at 16 px it reads as a pointed diamond.",
        rest="flame"),
    "rising": dict(
        name="Rising embers", ar="الشرر الصاعد",
        idea="The diamond stays whole, and three smaller diamonds rise from it in a zigzag like a flame's tongue. It grows out of Burst, your maybe: a flame drawn only in diamonds.",
        motion="Hover: the embers drift higher. Loop: they rise and fade, one after another, for ever.",
        small="The embers drop out below 32 px and leave the round 2 mark. Close to the old pixel flame if overdone.",
        rest="flame"),
    "inner": dict(
        name="Inner flame", ar="الشعلة الكامنة",
        idea="The diamond keeps its shape, and a small flame is cut out of it. From far away it is the diamond; up close the fire is inside. It is the quietest flame and the most institutional.",
        motion="Hover: the hollow flame grows and flickers inside the diamond. Loop: a slow inner flicker.",
        small="Below 32 px the hole closes and it reads as the plain diamond.",
        rest="flame"),
    "burst": dict(
        name="Burst", ar="التطاير", tag="Round 2 · maybe",
        idea="Round 2's Burst, kept for comparison: three chips fly off the spark.",
        motion="Hover: the chips drift out. Loop: they burst and fade like embers.",
        small="The chips vanish below 32 px.",
        rest="flame"),
}


def spark(variant, t, live=False):
    """SVG for the spark at (SX, SY): a <g class="wq-s"> so the CSS entrance can lift it."""
    ink, amber = t["ink"], t["spark"]
    mono = ink == amber
    inside = ""
    if variant in ("ignite",):
        a = ""
        if live:
            a = (anim("in", [DIA, EMB["a"]], .38) + anim("flicker", [EMB["a"], EMB["c"], EMB["b"], EMB["a"]], 1.1, True)
                 + anim("out", [EMB["a"], DIA], .5))
        inside = f'<path class="wq-sf" fill="{amber}" d="{DIA}">{a}</path>'
        if live and not mono:
            c = (anim("in", [CORE0, COREF["a"]], .38) + anim("flicker", [COREF["b"], COREF["a"], COREF["c"], COREF["b"]], .8, True)
                 + anim("out", [COREF["a"], CORE0], .4))
            inside += f'<path fill="{CORE}" d="{CORE0}">{c}</path>'
    elif variant in ("ember", "core"):
        a = ""
        if live:
            a = (anim("in", [EMB["a"], EMB["c"]], .4) + anim("flicker", [EMB["c"], EMB["b"], EMB["a"], EMB["c"]], 1.2, True)
                 + anim("out", [EMB["c"], EMB["a"]], .5))
        inside = f'<path class="wq-sf" fill="{amber}" d="{EMB["a"]}">{a}</path>'
        if variant == "core" and not mono:
            c = ""
            if live:
                c = (anim("in", [COREF["a"], COREF["c"]], .4) + anim("flicker", [COREF["b"], COREF["c"], COREF["a"], COREF["b"]], .85, True)
                     + anim("out", [COREF["c"], COREF["a"]], .5))
            inside += f'<path fill="{CORE}" d="{COREF["a"]}">{c}</path>'
    elif variant == "facet":
        a = ""
        if live:
            a = (anim("in", [FAC["a"], FAC["c"]], .35) + anim("flicker", [FAC["c"], FAC["b"], FAC["a"], FAC["c"]], 1.0, True)
                 + anim("out", [FAC["c"], FAC["a"]], .45))
        inside = f'<path class="wq-sf" fill="{amber}" d="{FAC["a"]}">{a}</path>'
    elif variant == "inner":
        a = ""
        if live:
            a = (anim("in", [INNER["a"], INNER_BIG["c"]], .4)
                 + anim("flicker", [INNER_BIG["c"], INNER_BIG["b"], INNER_BIG["a"], INNER_BIG["c"]], 1.1, True)
                 + anim("out", [INNER_BIG["c"], INNER["a"]], .5))
        inside = f'<path class="wq-sf" fill="{amber}" fill-rule="evenodd" d="{INNER["a"]}">{a}</path>'
    elif variant in ("rising", "burst"):
        inside = f'<path class="wq-sf" fill="{amber}" d="{DIA}"/>'
    return f'<g transform="translate({n(SX)} {n(SY)})"><g class="wq-s">{inside}</g></g>'


def chips(variant, t):
    """Small diamonds around the spark (Rising and Burst), each in a class the CSS moves."""
    if variant == "rising":
        spec = ((-3, -26, 11), (6, -39, 7.5), (-1, -50, 4.5))  # a zigzag tongue, shrinking upward
    elif variant == "burst":
        spec = ((15, -19, 7), (25, -6.5, 5), (5, -29, 3.6))
    else:
        return ""
    out = ""
    for i, (dx, dy, size) in enumerate(spec, 1):
        if LEAN_LEFT and variant == "rising":
            dx = -dx
        h = size / 2
        out += (f'<g transform="translate({n(SX + dx)} {n(SY + dy)})"><g style="--dx:{n(dx)}px;--dy:{n(dy)}px" '
                f'class="wq-c wq-c{i}"><rect x="{n(-h)}" y="{n(-h)}" width="{n(size)}" height="{n(size)}" '
                f'rx="{n(size * .12)}" fill="{t["spark"]}" transform="rotate(45)"/></g></g>')
    return out


def mark_svg(variant, t, live=False, cls_extra="", bg=None, view=VIEW, loop_file=False):
    tiles = "".join(tile_el(*POS[k], t["ink"], k) for k in ("L", "R", "B"))
    body = tiles + spark(variant, t, live=live) + chips(variant, t)
    if loop_file:
        body = tiles + loop_spark(variant, t) + chips(variant, t)
    x, y, w, h = view
    bgr = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    style = f'--wq-ink:{t["ink"]};--wq-spark:{t["spark"]};--wq-lift:{n(LIFT * R2)}px'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="wq wq-{variant}{cls_extra}" viewBox="{x} {y} {w} {h}" '
            f'width="{w}" height="{h}" style="{style}">' + bgr + body + "</svg>")


def bbox_view(variant, margin=6):
    """Tight square view for static files: grid plus this variant's tallest point."""
    top = {"ignite": SY - F.H, "ember": SY - 41, "core": SY - 41, "facet": SY - 37, "inner": SY - F.H,
           "rising": SY - 50 - 3.2, "burst": SY - 29 - 2.6}[variant]
    x0, x1 = POS["L"][0] - F.H, POS["R"][0] + F.H
    if variant == "burst":
        x1 = max(x1, SX + 25 + 3.6)
    y1 = POS["B"][1] + F.H
    y0 = top
    w, h = x1 - x0, y1 - y0
    side = max(w, h) + 2 * margin
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return (round(cx - side / 2, 2), round(cy - side / 2, 2), round(side, 2), round(side, 2))


def loop_spark(variant, t):
    """Spark for the stand-alone looping files (video, web backgrounds)."""
    amber = t["spark"]
    mono = t["ink"] == amber
    if variant == "ignite":
        vals = [DIA, DIA, EMB["a"], EMB["c"], EMB["b"], EMB["a"], EMB["c"], EMB["a"], DIA]
        times = [0, .22, .32, .42, .52, .62, .72, .82, 1]
        out = f'<path fill="{amber}" d="{DIA}">{loop_anim(vals, times, 4.2)}</path>'
        if not mono:
            cv = [CORE0, CORE0, COREF["a"], COREF["c"], COREF["b"], COREF["a"], COREF["c"], COREF["a"], CORE0]
            out += f'<path fill="{CORE}" d="{CORE0}">{loop_anim(cv, times, 4.2)}</path>'
    elif variant in ("ember", "core"):
        vals = [EMB["a"], EMB["c"], EMB["b"], EMB["a"]]
        out = f'<path fill="{amber}" d="{EMB["a"]}">{loop_anim(vals, [0, .33, .66, 1], 1.6)}</path>'
        if variant == "core" and not mono:
            cv = [COREF["b"], COREF["c"], COREF["a"], COREF["b"]]
            out += f'<path fill="{CORE}" d="{COREF["b"]}">{loop_anim(cv, [0, .33, .66, 1], 1.1)}</path>'
    elif variant == "facet":
        vals = [FAC["a"], FAC["c"], FAC["b"], FAC["a"]]
        out = f'<path fill="{amber}" d="{FAC["a"]}">{loop_anim(vals, [0, .33, .66, 1], 1.4)}</path>'
    elif variant == "inner":
        vals = [INNER["a"], INNER_BIG["c"], INNER_BIG["b"], INNER["a"]]
        out = f'<path fill="{amber}" fill-rule="evenodd" d="{INNER["a"]}">{loop_anim(vals, [0, .33, .66, 1], 2)}</path>'
    else:
        out = f'<path fill="{amber}" d="{DIA}"/>'
    return f'<g transform="translate({n(SX)} {n(SY)})">{out}</g>'


def tile_svg(variant, bg="#0B1F3A", dark=None, pad=0.17):
    x, y, w, h = bbox_view(variant, margin=0)
    s = 100 * (1 - 2 * pad) / w
    tx, ty = 100 * pad - x * s, 100 * pad - y * s
    inner_svg = mark_svg(variant, dark)
    body = inner_svg[inner_svg.index(">") + 1:-len("</svg>")]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
            f'<rect width="100" height="100" rx="22" fill="{bg}"/>'
            f'<g transform="translate({n(tx)} {n(ty)}) scale({s:.4f})">{body}</g></svg>')


def spark_only_svg(t):
    """Just the igniting spark, for small UI (a button icon)."""
    style = f'--wq-ink:{t["ink"]};--wq-spark:{t["spark"]};--wq-lift:{n(LIFT * R2)}px'
    x, y = SX - 24, SY - 46
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="wq wq-ignite" viewBox="{n(x)} {n(y)} 48 66" '
            f'width="48" height="66" style="{style}">' + spark("ignite", t, live=True) + "</svg>")
