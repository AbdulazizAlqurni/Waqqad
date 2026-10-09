"""Build the Waqqad logo set from one source of truth.

    python3 build.py        -> writes v2/ (logo, spark variants, typography
                               variants, motion files) and ../logo-lab.html

Every geometry decision lives in CFG below, so a design round is an edit to
CFG plus a rebuild. Letter outlines come from the received drafts (current
Kufi wordmark, Plex Latin) and from type_outlines.json (made by typeset.py
from open fonts); nothing is redrawn by hand except the grid Kufi, which is
built from cells on purpose.

History: v1/ is round 1 as approved and stays frozen; received/ is the drafts.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pathkit as pk  # noqa: E402

RECEIVED = os.path.join(HERE, "received")
OUT = os.path.join(HERE, "v2")
R2 = math.sqrt(2)

COLOR = {
    "navy": "#0B1F3A",
    "teal": "#007C91",
    "amber": "#F2A93B",
    "mist": "#F3F5F8",
    "white": "#FFFFFF",
}

# ink: letters and grid; spark: the amber piece; accent: rule and Latin.
# Round 1 pick S-3: white, not light teal, for Latin and rule on navy.
THEMES = {
    "light": dict(bg=None, ink=COLOR["navy"], spark=COLOR["amber"], accent=COLOR["teal"]),
    "dark": dict(bg=COLOR["navy"], ink=COLOR["white"], spark=COLOR["amber"], accent=COLOR["white"]),
    "mono": dict(bg=None, ink=COLOR["navy"], spark=COLOR["navy"], accent=COLOR["navy"]),
}

CFG = {
    # The mark: 2x2 grid rotated 45 deg, top tile lifted and amber.
    # Round 1 picks: A-6 lift 10 (was 7), A-7 corners stay 2.2.
    "mark": dict(tile=24, gap=5, lift=10, rx=2.2),
    "lockup": dict(mark_h=1.0,          # mark height / wordmark height (alef top to baseline)
                   gap=0.55,            # wordmark to mark, in wordmark heights
                   latin_cap=20,        # WAQQAD cap height, wordmark units (alef = 91.2)
                   latin_gap=9,         # minimum space from the Arabic baseline to WAQQAD
                   shadda="ink"),       # A-5: the spark lives in the mark only
    "wordmark": dict(spark=22, spark_gap=6),
    # The logotype (old B), now in the lighter Kufi cut (B-6), sizes relative to alef 91.2
    "logotype": dict(rule=3, rule_depth=19.5, rule_gap_tail=9, latin_cap=15.7, latin_gap=7.5),
    "margin": 0.14,  # clear space around every file, fraction of logo height
}

ALEF_H = 91.2  # every wordmark is scaled so its alef is this tall


# ---------------------------------------------------------------- primitives

class Art:
    """A list of SVG elements in one coordinate space, plus its ink bbox."""

    def __init__(self):
        self.els, self.box = [], None

    def add(self, el, box):
        self.els.append(el)
        self.grow(box)
        return self

    def grow(self, box):
        if self.box is None:
            self.box = tuple(box)
        else:
            x0, y0, x1, y1 = self.box
            self.box = (min(x0, box[0]), min(y0, box[1]), max(x1, box[2]), max(y1, box[3]))

    def placed(self, s, tx, ty):
        x0, y0, x1, y1 = self.box
        g = f'<g transform="translate({n(tx)} {n(ty)}) scale({n(s, 4)})">'
        return g + "".join(self.els) + "</g>", (x0 * s + tx, y0 * s + ty, x1 * s + tx, y1 * s + ty)


def n(v, p=2):
    s = f"{v:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def diamond(cx, cy, size, rx, fill, cls=None, attrs=""):
    """Square of side `size` turned 45 deg around (cx, cy). With `cls`, the
    square sits in its own <g class> so CSS can move it without fighting the
    rotate attribute."""
    h = size / 2
    r = size / R2 - rx * (R2 - 1)  # rounded corners pull the tips in
    rect = (f'<rect x="{n(-h)}" y="{n(-h)}" width="{n(size)}" height="{n(size)}" rx="{n(rx)}" '
            f'fill="{fill}" transform="rotate(45)"{attrs}/>')
    inner = f'<g class="{cls}">{rect}</g>' if cls else rect
    return f'<g transform="translate({n(cx)} {n(cy)})">{inner}</g>', (cx - r, cy - r, cx + r, cy + r)


def diamond_outline(cx, cy, size, rx, stroke, width, cls=None):
    h = size / 2
    r = size / R2 + width / 2
    rect = (f'<rect x="{n(-h)}" y="{n(-h)}" width="{n(size)}" height="{n(size)}" rx="{n(rx)}" fill="none" '
            f'stroke="{stroke}" stroke-width="{n(width)}" pathLength="100" transform="rotate(45)"/>')
    inner = f'<g class="{cls}">{rect}</g>' if cls else rect
    return f'<g transform="translate({n(cx)} {n(cy)})">{inner}</g>', (cx - r, cy - r, cx + r, cy + r)


def path_el(subs, fill):
    return f'<path fill="{fill}" d="{pk.to_d(subs)}"/>', pk.bbox(subs)


def svg_doc(art, theme, margin_ratio=None, square=False, bg_rx=None, root_attrs="", style=""):
    x0, y0, x1, y1 = art.box
    m = (CFG["margin"] if margin_ratio is None else margin_ratio) * (y1 - y0)
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    if square:
        w, h = x1 - x0, y1 - y0
        side = max(w, h)
        x0 -= (side - w) / 2
        y0 -= (side - h) / 2
        x1, y1 = x0 + side, y0 + side
    w, h = x1 - x0, y1 - y0
    bg = ""
    if theme.get("bg"):
        rx = f' rx="{n(bg_rx)}"' if bg_rx else ""
        bg = f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}"{rx} fill="{theme["bg"]}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(x0)} {n(y0)} {n(w)} {n(h)}" '
            f'width="{n(w)}" height="{n(h)}"{root_attrs}>' + style + bg + "".join(art.els) + "</svg>")


# ---------------------------------------------------------------- sources

def _read(name):
    with open(os.path.join(RECEIVED, name), encoding="utf-8") as f:
        return f.read()


def _paths(svg):
    return re.findall(r'<path transform="translate\(([\d.]+) ([\d.]+)\)" fill="[^"]+" d="([^"]+)"', svg)


LATIN_CAP = 18.148


def load_sources():
    a = _paths(_read("A_lockup.svg"))
    with open(os.path.join(HERE, "type_outlines.json"), encoding="utf-8") as f:
        outlines = json.load(f)
    return {
        "kufi": pk.parse(a[0][2]),  # the drafts' Kufi: baseline y=0, alef top -91.2
        "latin": pk.split_glyphs(pk.parse(a[1][2]), {2, 4, 6, 8, 10}),  # W A Q Q A D, cap 18.148
        "outlines": outlines,
    }


def latin_line(glyphs, cap, x_left, x_right, baseline, fill):
    """WAQQAD at `cap` height, letter gaps stretched so ink spans x_left..x_right."""
    s = cap / LATIN_CAP
    scaled = [pk.transform(g, s) for g in glyphs]
    widths = [pk.bbox(g)[2] - pk.bbox(g)[0] for g in scaled]
    gap = (x_right - x_left - sum(widths)) / (len(glyphs) - 1)
    cursor, subs = x_left, []
    for g, w in zip(scaled, widths):
        subs += pk.transform(g, 1, 1, cursor - pk.bbox(g)[0], baseline)
        cursor += w + gap
    return path_el(subs, fill)


def latin_natural(glyphs, cap, tracking_em):
    s = cap / LATIN_CAP
    boxes = [pk.bbox(pk.transform(g, s)) for g in glyphs]
    ink = sum(b[2] - b[0] for b in boxes)
    gaps = sum(boxes[i + 1][0] - boxes[i][2] for i in range(len(boxes) - 1))
    return ink + gaps + tracking_em * cap * (len(glyphs) - 1)


# ---------------------------------------------------------------- words
#
# A Word is the Arabic name ready to compose: letter outlines plus the few
# landmarks the lockups need. Coordinates: baseline y=0, alef top y=-91.2.

class Word:
    def __init__(self, letters, dots, qaf_right, alef_top, extra=None):
        self.letters = letters      # list of (svg-element-maker(fill), bbox)
        self.dots = dots            # bbox of the qaf's two dots (the spark goes above)
        self.qaf_right = qaf_right  # x of the qaf's right edge (Latin ends here)
        self.alef_top = alef_top
        self.extra = extra or {}
        boxes = [b for _, b in letters]
        self.box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                    max(b[2] for b in boxes), max(b[3] for b in boxes))

    def art(self, fill):
        a = Art()
        for make, box in self.letters:
            a.add(make(fill), box)
        return a


def word_from_drafts(src):
    subs = src["kufi"]
    return Word(
        letters=[(lambda f, s=subs: path_el(s, f)[0], pk.bbox(subs))],
        dots=pk.bbox(subs[2:4]), qaf_right=pk.bbox(subs[4:5])[2], alef_top=-91.2)


def word_from_font(rec):
    """Word from typeset.py outlines: cluster 0 و, 1 ق (+dots), 2 ا, 3 د."""
    glyphs = rec["glyphs"]
    alef = [s for g in glyphs if g["cluster"] == 2 for s in pk.parse(g["d"])]
    s = ALEF_H / -pk.bbox(alef)[1]
    subs_all, qaf = [], []
    for g in glyphs:
        subs = pk.transform(pk.parse(g["d"]), s)
        subs_all += subs
        if g["cluster"] == 1:
            qaf += subs
    # dots: the qaf's subpaths that sit wholly above its body (the biggest shape)
    body = max(qaf, key=lambda sp: (lambda b: (b[2] - b[0]) * (b[3] - b[1]))(pk.bbox([sp])))
    by0 = pk.bbox([body])[1]
    dots = [sp for sp in qaf if pk.bbox([sp])[3] <= by0 + 1]
    return Word(
        letters=[(lambda f, ss=subs_all: path_el(ss, f)[0], pk.bbox(subs_all))],
        dots=pk.bbox(dots), qaf_right=pk.bbox([body])[2], alef_top=-ALEF_H,
        extra=dict(font=rec["font"]))


def word_grid_kufi(diamond_dots=True):
    """Square Kufi وقاد built on cells, stroke = space = one cell.

    Read right to left: و (square head, tail down and left), ق (square head
    joined to the alef along the baseline), ا, د. The qaf's dots are diamonds:
    the same piece as the mark, at letter scale."""
    c = ALEF_H / 6           # alef is six cells tall
    cells = [                 # (col, row, w, h); row 5 is the baseline row
        (2, 2, 1, 4), (0, 5, 3, 1),                              # د
        (4, 0, 1, 6),                                            # ا
        (4, 5, 3, 1),                                            # joint ا-ق on the baseline
        (6, 3, 3, 1), (6, 5, 3, 1), (6, 3, 1, 3), (8, 3, 1, 3),  # ق head
        (10, 3, 3, 1), (10, 5, 3, 1), (10, 3, 1, 3), (12, 3, 1, 3),  # و head
        (12, 5, 1, 3), (9, 7, 4, 1),                              # و tail
    ]
    y_off = -6 * c            # row 6 top = baseline
    rects = []
    for col, row, w, h in cells:
        rects.append((col * c, row * c + y_off, w * c, h * c))

    def make(fill, rects=rects):
        d = "".join(f"M{n(x)} {n(y)}H{n(x + w)}V{n(y + h)}H{n(x)}Z" for x, y, w, h in rects)
        dots = ""
        for col in (6, 8):
            dots += diamond((col + .5) * c, 1.5 * c + y_off, c * 0.92, c * 0.1, fill)[0]
        return f'<path fill="{fill}" d="{d}"/>' + dots

    xs = [r[0] for r in rects] + [r[0] + r[2] for r in rects]
    ys = [r[1] for r in rects] + [r[1] + r[3] for r in rects]
    box = (min(xs), min(ys), max(xs), max(ys))
    dr = c * 0.92 / R2
    dots = (6.5 * c - dr, 1.5 * c + y_off - dr, 8.5 * c + dr, 1.5 * c + y_off + dr)
    # Latin stops short of the waw's tail, which runs under column 9
    return Word(letters=[(make, box)], dots=dots, qaf_right=8.4 * c, alef_top=-ALEF_H,
                extra=dict(font="Built on the mark's grid"))


# ---------------------------------------------------------------- compositions

def shadda_spark(word, fill, size=None):
    c = CFG["wordmark"]
    sp = size or c["spark"]
    dcx = (word.dots[0] + word.dots[2]) / 2
    return diamond(dcx, word.dots[1] - c["spark_gap"] - sp / R2, sp, sp * 0.12, fill)


def wordmark(word, t, shadda="spark"):
    """The name alone: letters plus the spark as shadda (amber by default; ink
    when it sits beside the mark, per A-5)."""
    art = word.art(t["ink"])
    el, box = shadda_spark(word, t[shadda])
    return art.add(el, box)


def lockup(word, t, mark_fn=None):
    c = CFG["lockup"]
    art = word.art(t["ink"])
    el, box = shadda_spark(word, t[c["shadda"]] if t is not THEMES["mono"] else t["ink"])
    art.add(el, box)
    word_h = -word.alef_top
    m = (mark_fn or mark)(t)
    mh = m.box[3] - m.box[1]
    s = word_h * c["mark_h"] / mh
    tx = word.box[2] + word_h * c["gap"] - m.box[0] * s
    ty = word.alef_top - m.box[1] * s
    el, box = m.placed(s, tx, ty)
    art.add(el, box)
    # WAQQAD tucked under د ا ق, baseline level with the bottom of the waw's tail,
    # but never closer than latin_gap to the Arabic baseline (short tails)
    base = max(word.box[3], c["latin_gap"] + c["latin_cap"])
    el, box = latin_line(SRC["latin"], c["latin_cap"], word.box[0], word.qaf_right, base, t["accent"])
    return art.add(el, box)


def logotype(word, t):
    """Old direction B: the name, the spark, a rule that stops short of the tail."""
    c = CFG["logotype"]
    art = wordmark(word, t)
    tail_left = word.extra.get("tail_left", word.qaf_right + 18)
    x0, x1 = word.box[0], tail_left - c["rule_gap_tail"]
    ry, rh = c["rule_depth"], c["rule"]
    art.add(f'<rect x="{n(x0)}" y="{n(ry)}" width="{n(x1 - x0)}" height="{n(rh)}" rx="{n(rh / 2)}" '
            f'fill="{t["accent"]}"/>', (x0, ry, x1, ry + rh))
    cap = c["latin_cap"]
    w = latin_natural(SRC["latin"], cap, 0.12)
    base = ry + rh + c["latin_gap"] + cap
    el, box = latin_line(SRC["latin"], cap, x1 - w, x1, base, t["ink"])
    return art.add(el, box)


def favicon_logotype():
    art = Art()
    art.add(f'<rect width="100" height="100" rx="22" fill="{COLOR["navy"]}"/>', (0, 0, 100, 100))
    art.els.append(diamond(50, 42, 34, 4.08, COLOR["amber"])[0])
    art.els.append(f'<rect x="26" y="70" width="48" height="6" rx="3" fill="{COLOR["white"]}"/>')
    return art


def tile(mark_art, bg, pad=0.19, rx_ratio=0.22):
    """App-icon tile: mark centred on a rounded square."""
    x0, y0, x1, y1 = mark_art.box
    inner = 100 * (1 - 2 * pad)
    s = inner / max(x1 - x0, y1 - y0)
    tx = (100 - (x1 - x0) * s) / 2 - x0 * s
    ty = (100 - (y1 - y0) * s) / 2 - y0 * s
    art = Art()
    art.add(f'<rect width="100" height="100" rx="{n(100 * rx_ratio)}" fill="{bg}"/>', (0, 0, 100, 100))
    art.els.append(mark_art.placed(s, tx, ty)[0])
    return art


# ---------------------------------------------------------------- the mark and its spark variants
#
# Grid geometry before the spark: tile centres sit at distance d from (50, 50)
# along the axes (left, right, bottom, top). Class names are the hooks for
# spark-motion.css; static files simply carry them unused.

def _grid(tile_, gap):
    d = (tile_ + gap) / 2 * R2
    return d, {"L": (50 - d, 50), "R": (50 + d, 50), "B": (50, 50 + d), "T": (50, 50 - d)}


def star(cx, cy, r, fill, cls):
    k = r * 0.16
    d = (f"M0 {n(-r)}Q{n(k)} {n(-k)} {n(r)} 0Q{n(k)} {n(k)} 0 {n(r)}"
         f"Q{n(-k)} {n(k)} {n(-r)} 0Q{n(-k)} {n(-k)} 0 {n(-r)}Z")
    return (f'<g transform="translate({n(cx)} {n(cy)})"><g class="{cls}"><path fill="{fill}" d="{d}"/></g></g>',
            (cx - r, cy - r, cx + r, cy + r))


SPARKS = {
    "lift": dict(
        name="Lift", ar="الرفعة", tag="Round 1 mark",
        idea="The top tile leaves the grid and turns amber. The structure is the system; the piece that leaves it is the spark.",
        motion="Entrance: the grid pops in, the top tile rises out of its place and warms to amber. Hover: it lifts a little higher. Loop: it floats.",
        small="Holds at 16 px: the gap above the grid stays readable.",
    ),
    "glint": dict(
        name="Glint", ar="البريق",
        idea="A four-point glint flashes on the spark's corner, the way light catches a cut stone. The diamond stays whole; the glint makes it shine.",
        motion="Entrance: after the lift, the glint pops and turns a quarter. Hover: it flashes again. Loop: it twinkles every few seconds.",
        small="Below 24 px the glint disappears and you get the round 1 mark, which is a safe fallback.",
    ),
    "burst": dict(
        name="Burst", ar="التطاير",
        idea="Three chips fly off the spark, smaller as they go. It is the most literal spark of the five: something struck, something flying.",
        motion="Entrance: the chips burst out of the spark. Hover: they drift further out. Loop: they burst and fade, again and again, like embers.",
        small="The chips vanish below 32 px. Use the round 1 mark for icons.",
    ),
    "core": dict(
        name="Core", ar="النواة",
        idea="All four tiles stay navy and part slightly; the spark is born at the centre where they meet. Nothing leaves the system, and the idea comes from inside it.",
        motion="Entrance: the tiles start closed, then open as the spark ignites at the centre. Hover: they part further and the spark grows. Loop: it breathes, like a heartbeat.",
        small="The centre spark is tiny. Below 32 px it reads as four tiles, so icons need a larger spark.",
    ),
    "socket": dict(
        name="Socket", ar="المَقبس",
        idea="The spark rises out of its place and leaves an open seat behind, a thin V where it used to sit. The empty seat tells you where it came from: talent rising out of a structure.",
        motion="Entrance: the seat draws itself while the spark lifts out. Hover: the spark rises and the seat glows amber. Loop: the spark drops back in and lifts out, like a key turning.",
        small="The seat line thins out below 32 px. A 16 px version would drop it.",
    ),
    "halo": dict(
        name="Halo", ar="الوهج",
        idea="A thin amber ring around the spark: heat around a flame, with no flame drawn. It gives the spark weight without making it bigger.",
        motion="Entrance: the ring opens out from the spark. Hover: a second ring ripples out and fades. Loop: ripples, like a signal or a pulse.",
        small="The ring merges with the spark below 24 px into one bigger amber diamond, which still reads.",
    ),
}


def mark(t, variant="lift", cfg=None):
    c = dict(CFG["mark"], **(cfg or {}))
    tile_, gap, lift, rx = c["tile"], c["gap"], c["lift"], c["rx"]
    if variant == "core":
        tile_, gap = 22, 14
    d, pos = _grid(tile_, gap)
    art = Art()
    for key in ("L", "R", "B") + (("T",) if variant == "core" else ()):
        el, box = diamond(*pos[key], tile_, rx, t["ink"], cls=f"wq-t wq-t{key}")
        art.add(el, box)
    if variant == "core":
        el, box = diamond(50, 50, 9, 1, t["spark"], cls="wq-s", attrs=' class="wq-sf"')
        return art.add(el, box)

    sx, sy = pos["T"][0], pos["T"][1] - lift * R2
    if variant == "socket":
        # the empty seat: the lower half of the spark's place in the grid, open at the top
        hx, hy = pos["T"]
        r = (tile_ - 3) / R2
        art.add(f'<g class="wq-k"><path d="M{n(hx - r)} {n(hy)}L{n(hx)} {n(hy + r)}L{n(hx + r)} {n(hy)}" '
                f'fill="none" stroke="{t["ink"]}" stroke-width="2.6" stroke-linecap="round" '
                f'stroke-linejoin="round" pathLength="100"/></g>', (hx - r - 1.3, hy - 1.3, hx + r + 1.3, hy + r + 1.3))
    if variant == "halo":
        for cls in ("wq-r", "wq-h"):
            el, box = diamond_outline(sx, sy, tile_ + 11, rx + 1.5, t["spark"], 2, cls=cls)
            art.add(el, box)
    el, box = diamond(sx, sy, tile_, rx, t["spark"], cls="wq-s", attrs=' class="wq-sf"')
    art.add(el, box)
    if variant == "glint":
        el, box = star(sx + 12.5, sy - 12.5, 8.5, t["spark"], "wq-g")
        art.add(el, box)
    if variant == "burst":
        for i, (dx, dy, size) in enumerate(((15, -19, 7), (25, -6.5, 5), (5, -29, 3.6)), 1):
            el, box = diamond(sx + dx, sy + dy, size, size * 0.12, t["spark"],
                              cls=f"wq-c wq-c{i}", attrs="")
            el = el.replace('<g class="wq-c', f'<g style="--dx:{n(dx)}px;--dy:{n(dy)}px" class="wq-c', 1)
            art.add(el, box)
    return art


def mark_live(variant, t, view=(-12, -30, 124, 130)):
    """Inline SVG for the Lab: fixed viewBox with room to move, CSS hooks on."""
    art = mark(t, variant)
    lift = CFG["mark"]["lift"] * R2
    x, y, w, h = view
    return (f'<svg class="wq wq-{variant}" viewBox="{x} {y} {w} {h}" '
            f'style="--wq-ink:{t["ink"]};--wq-spark:{t["spark"]};--wq-lift:{n(lift)}px" aria-hidden="true">'
            + "".join(art.els) + "</svg>")


def motion_file(variant, t, css):
    """Stand-alone looping SVG for video and web: the mark plus its loop CSS."""
    art = mark(t, variant)
    lift = CFG["mark"]["lift"] * R2
    root = (f' class="wq wq-{variant} wq-loop" style="--wq-ink:{t["ink"]};--wq-spark:{t["spark"]};'
            f'--wq-lift:{n(lift)}px"')
    a2 = Art()
    a2.els, a2.box = art.els, (-12, -30, 112, 100)
    return svg_doc(a2, t, margin_ratio=0, root_attrs=root, style=f"<style>{css}</style>")


# ---------------------------------------------------------------- typography variants

TYPE = {
    "current": dict(name="Current Kufi", ar="الكوفي الحالي", tag="Round 1",
                    face="Noto Kufi Arabic, Black (from the drafts)",
                    idea="Heavy, flat and confident. The reference the other five are measured against."),
    "grid": dict(name="Grid Kufi", ar="الكوفي المربّع",
                 face="Custom: drawn on cells, one cell stroke, one cell space",
                 idea="Square Kufi built on the same grid as the mark, with diamond dots on the qaf. The name and the symbol become one system, and no one else can have it.",
                 risk="Square Kufi is harder to read at a glance, and at small sizes the counters close up."),
    "reem": dict(name="Reem Kufi", ar="ريم كوفي", key="reem_kufi_700",
                 face="Reem Kufi, Bold · SIL OFL",
                 idea="Fatimid geometric Kufi: a tall alef and a sharp, slanted dal. It reads as heritage made modern, and as the most elegant of the five.",
                 risk="Lighter strokes than the mark's tiles, so the lockup feels top-heavy unless the mark shrinks."),
    "changa": dict(name="Changa", ar="تشانجا", key="changa_800",
                   face="Changa, ExtraBold · SIL OFL",
                   idea="Condensed, technical Kufi whose dots are already diamonds, and whose و tail ends in a cut. It is the closest to software and the most compact.",
                   risk="Common in tech and gaming; it needs the spark to feel institutional."),
    "readex": dict(name="Readex Pro", ar="ريدكس برو", key="readex_700",
                   face="Readex Pro, Bold · SIL OFL",
                   idea="A modern sans with diamond dots and open, round letters. It is friendly and easy to read, and its Latin half matches if we ever need it.",
                   risk="Rounder than the mark; the diamonds have to carry the brand alone."),
    "plex": dict(name="IBM Plex Sans Arabic", ar="بليكس عربي", key="plex_ar_700",
                 face="IBM Plex Sans Arabic, Bold · SIL OFL",
                 idea="The system font itself. The quietest choice: the logo, the interface and the documents all share one typeface.",
                 risk="Anyone can set it, so the wordmark alone isn't ownable. The mark has to do the work."),
}


def type_word(key):
    if key == "current":
        return word_from_drafts(SRC)
    if key == "grid":
        return word_grid_kufi()
    return word_from_font(SRC["outlines"]["arabic"][TYPE[key]["key"]])


# ---------------------------------------------------------------- build

SRC = None


def build():
    global SRC
    SRC = load_sources()
    files = {}
    word = word_from_drafts(SRC)
    word.extra["tail_left"] = 208.9  # the drafts' waw: tail tip at y=+23
    for name, th in THEMES.items():
        sfx = "" if name == "light" else "_" + name
        files[f"mark{sfx}"] = svg_doc(mark(th), th, square=True)
        files[f"lockup{sfx}"] = svg_doc(lockup(word, th), th)
        files[f"wordmark{sfx}"] = svg_doc(wordmark(word, th), th)
        files[f"wordmark_ink{sfx}"] = svg_doc(wordmark(word, th, "ink"), th, margin_ratio=0.02)
        files[f"logotype{sfx}"] = svg_doc(logotype(word, th), th)
    files["tile"] = svg_doc(tile(mark(THEMES["dark"]), COLOR["navy"]), {}, margin_ratio=0)
    files["favicon_logotype"] = svg_doc(favicon_logotype(), {}, margin_ratio=0)

    with open(os.path.join(HERE, "spark-motion.css"), encoding="utf-8") as f:
        css = f.read()
    css_min = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css_min = re.sub(r"\s+", " ", css_min).strip()
    live = {}
    for v in SPARKS:
        for name in ("light", "dark", "mono"):
            th = THEMES[name]
            files[f"spark/{v}_{name}"] = svg_doc(mark(th, v), th, square=True)
        files[f"spark/{v}_tile"] = svg_doc(tile(mark(THEMES["dark"], v), COLOR["navy"]), {}, margin_ratio=0)
        files[f"spark/{v}_motion"] = motion_file(v, THEMES["light"], css_min)
        files[f"spark/{v}_motion_dark"] = motion_file(v, THEMES["dark"], css_min)
        live[v] = {"light": mark_live(v, THEMES["light"]), "dark": mark_live(v, THEMES["dark"])}

    for k in TYPE:
        w = type_word(k)
        for name in ("light", "dark"):
            th = THEMES[name]
            files[f"type/{k}_lockup_{name}"] = svg_doc(lockup(w, th), th)
            files[f"type/{k}_wordmark_{name}"] = svg_doc(wordmark(w, th), th)

    for k, v in files.items():
        p = os.path.join(OUT, k + ".svg")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(v)
    return files, live, css


def read_dir(d):
    out = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".svg"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                out[fn[:-4]] = f.read()
    return out


# ---------------------------------------------------------------- lab page

def write_lab(data):
    with open(os.path.join(HERE, "lab_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    css = data.pop("css")
    page = (tpl.replace("/*DATA*/{}", json.dumps(data, ensure_ascii=False))
               .replace("/*MOTION_CSS*/", css))
    with open(os.path.join(HERE, "lab.fragment.html"), "w", encoding="utf-8") as f:
        f.write(page)
    head, _, body = page.partition("</style>")
    with open(os.path.join(HERE, "..", "logo-lab.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def build_symbol():
    """Round 3: the symbol and its flame. Writes v3/symbol/ and returns Lab data."""
    import symbol as S
    out = os.path.join(HERE, "v3", "symbol")
    with open(os.path.join(HERE, "spark-motion.css"), encoding="utf-8") as f:
        css_min = re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)).strip()
    os.makedirs(out, exist_ok=True)
    data = {}
    for v, meta in S.VARIANTS.items():
        files = {}
        view = S.bbox_view(v)
        for name in ("light", "dark", "mono"):
            th = THEMES[name]
            files[name] = S.mark_svg(v, th, view=view, bg=th["bg"])
        files["tile"] = S.tile_svg(v, dark=THEMES["dark"])
        files["motion"] = S.mark_svg(v, THEMES["light"], loop_file=True, cls_extra=" wq-loop")
        files["motion_dark"] = S.mark_svg(v, THEMES["dark"], loop_file=True, cls_extra=" wq-loop", bg=COLOR["navy"])
        for k in ("motion", "motion_dark"):  # the small diamonds move with CSS: ship it inside
            head, _, rest = files[k].partition(">")
            files[k] = head + "><style>" + css_min + "</style>" + rest
        for k, svg in files.items():
            with open(os.path.join(out, f"{v}_{k}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
        data[v] = dict(meta, light=files["light"], tile=files["tile"],
                       live={"light": S.mark_svg(v, THEMES["light"], live=True),
                             "dark": S.mark_svg(v, THEMES["dark"], live=True)})
    return data


if __name__ == "__main__":
    build()  # round 2 files stay reproducible
    with open(os.path.join(HERE, "spark-motion.css"), encoding="utf-8") as f:
        css = f.read()
    import symbol as S
    data = {"variants": build_symbol(), "sparkIcon": S.spark_only_svg(THEMES["dark"]), "css": css}
    write_lab(data)
    print("v3 symbol ->", os.path.join(OUT.replace("v2", "v3"), "symbol"), "; lab page -> brand/logo-lab.html")
