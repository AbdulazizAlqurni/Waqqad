"""Build the Waqqad logo set from one source of truth.

    python3 build.py            -> writes v1/*.svg and ../logo-lab.html

Every geometry decision lives in CFG below, so a design round is an edit to
CFG plus a rebuild. The outlined glyphs (Kufi wordmark, Plex wordmark, Plex
Latin) are lifted from the received drafts and never redrawn by hand.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pathkit as pk  # noqa: E402

RECEIVED = os.path.join(HERE, "received")
OUT = os.path.join(HERE, "v1")

COLOR = {
    "navy": "#0B1F3A",
    "teal": "#007C91",
    "amber": "#F2A93B",
    "mist": "#F3F5F8",
    "white": "#FFFFFF",
    "teal_light": "#7FD1DE",  # used by the drafts on navy; not yet in the palette
}

# ink: letters and grid; spark: the amber piece; accent: rule and Latin on A/C
THEMES = {
    "light": dict(bg=None, ink=COLOR["navy"], spark=COLOR["amber"], accent=COLOR["teal"]),
    "dark": dict(bg=COLOR["navy"], ink=COLOR["white"], spark=COLOR["amber"], accent=COLOR["teal_light"]),
    "mono": dict(bg=None, ink=COLOR["navy"], spark=COLOR["navy"], accent=COLOR["navy"]),
}

CFG = {
    # A · Sharara: 2x2 grid rotated 45 deg, top tile lifted and amber
    "A": dict(tile=24, gap=5, lift=7, rx=2.2,
              lockup_mark_h=1.0,     # mark height / wordmark height (alef top to baseline)
              lockup_gap=0.55,       # space between wordmark and mark, in wordmark heights
              latin_cap=20,          # WAQQAD cap height in wordmark units
              spark=22),
    # B · Logotype
    "B": dict(rule=4, rule_gap_tail=12, latin_cap=20.9, spark=30),
    # C · Waw monogram
    "C": dict(ring_r=23, stroke=14, spark=14,
              lockup_mark_h=1.25, lockup_gap=0.6, latin_cap=16.8),
    # clear space around every file = this fraction of the logo height
    "margin": 0.14,
}


# ---------------------------------------------------------------- sources

def _read(name):
    with open(os.path.join(RECEIVED, name), encoding="utf-8") as f:
        return f.read()


def _paths(svg):
    return re.findall(r'<path transform="translate\(([\d.]+) ([\d.]+)\)" fill="[^"]+" d="([^"]+)"', svg)


def load_sources():
    a, b, c = _paths(_read("A_lockup.svg")), _paths(_read("B_logotype.svg")), _paths(_read("C_lockup.svg"))
    latin = pk.parse(a[1][2])
    return {
        "kufi_A": pk.parse(a[0][2]),           # baseline at y=0, alef top -91.2
        "kufi_B": pk.parse(b[0][2]),           # heavier cut, alef top -121.6
        "plex_C": pk.parse(c[0][2]),           # Plex Sans Arabic with shadda
        "latin": pk.split_glyphs(latin, {2, 4, 6, 8, 10}),  # W A Q Q A D, cap 18.148
    }


LATIN_CAP = 18.148


# ---------------------------------------------------------------- primitives

class Art:
    """A list of SVG elements in one coordinate space, plus its ink bbox."""

    def __init__(self, els=None, box=None):
        self.els = els or []
        self.box = box

    def add(self, el, box):
        self.els.append(el)
        if self.box is None:
            self.box = box
        else:
            x0, y0, x1, y1 = self.box
            self.box = (min(x0, box[0]), min(y0, box[1]), max(x1, box[2]), max(y1, box[3]))
        return self

    def placed(self, s, tx, ty):
        """This art scaled by s then moved by (tx, ty), as one <g>."""
        x0, y0, x1, y1 = self.box
        g = f'<g transform="translate({_n(tx)} {_n(ty)}) scale({_n(s, 4)})">'
        return g + "".join(self.els) + "</g>", (x0 * s + tx, y0 * s + ty, x1 * s + tx, y1 * s + ty)


def _n(v, p=2):
    s = f"{v:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def diamond(cx, cy, size, rx, fill):
    """Square of side `size` rotated 45 deg around its centre."""
    h = size / 2
    el = (f'<rect x="{_n(cx - h)}" y="{_n(cy - h)}" width="{_n(size)}" height="{_n(size)}" '
          f'rx="{_n(rx)}" fill="{fill}" transform="rotate(45 {_n(cx)} {_n(cy)})"/>')
    # rounded corners pull the tips in by rx*(sqrt2-1)
    r = size / 2 ** 0.5 - rx * (2 ** 0.5 - 1)
    return el, (cx - r, cy - r, cx + r, cy + r)


def path_el(subs, fill):
    return f'<path fill="{fill}" d="{pk.to_d(subs)}"/>', pk.bbox(subs)


def svg_doc(art, theme, margin_ratio=None, square=False, bg_rx=None):
    x0, y0, x1, y1 = art.box
    h = y1 - y0
    m = (CFG["margin"] if margin_ratio is None else margin_ratio) * h
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    if square:
        w, hh = x1 - x0, y1 - y0
        side = max(w, hh)
        x0 -= (side - w) / 2
        y0 -= (side - hh) / 2
        x1, y1 = x0 + side, y0 + side
    w, hh = x1 - x0, y1 - y0
    bg = ""
    if theme["bg"]:
        rx = f' rx="{_n(bg_rx)}"' if bg_rx else ""
        bg = f'<rect x="{_n(x0)}" y="{_n(y0)}" width="{_n(w)}" height="{_n(hh)}"{rx} fill="{theme["bg"]}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{_n(x0)} {_n(y0)} {_n(w)} {_n(hh)}" '
            f'width="{_n(w)}" height="{_n(hh)}">' + bg + "".join(art.els) + "</svg>")


def latin_line(glyphs, cap, x_left, x_right, baseline, fill):
    """WAQQAD at `cap` height, letter gaps stretched so ink spans x_left..x_right."""
    s = cap / LATIN_CAP
    scaled = [pk.transform(g, s) for g in glyphs]
    widths = [pk.bbox(g)[2] - pk.bbox(g)[0] for g in scaled]
    gap = (x_right - x_left - sum(widths)) / (len(glyphs) - 1)
    art, cursor = Art(), x_left
    subs = []
    for g, w in zip(scaled, widths):
        gx0 = pk.bbox(g)[0]
        subs += pk.transform(g, 1, 1, cursor - gx0, baseline)
        cursor += w + gap
    el, box = path_el(subs, fill)
    return el, box, gap / cap


def latin_natural(glyphs, cap, tracking_em):
    """Natural width of WAQQAD at `cap` with extra tracking in cap units."""
    s = cap / LATIN_CAP
    ws = [pk.bbox(g)[2] - pk.bbox(g)[0] for g in (pk.transform(g, s) for g in glyphs)]
    natural_gaps = []
    for i in range(len(glyphs) - 1):
        a, b = pk.bbox(pk.transform(glyphs[i], s)), pk.bbox(pk.transform(glyphs[i + 1], s))
        natural_gaps.append(b[0] - a[2])
    return sum(ws) + sum(natural_gaps) + tracking_em * cap * (len(glyphs) - 1)


# ---------------------------------------------------------------- A · Sharara

def mark_A(t, cfg=None):
    c = cfg or CFG["A"]
    tile, gap, lift, rx = c["tile"], c["gap"], c["lift"], c["rx"]
    step = tile + gap
    o = 50 - step / 2  # grid centred on (50, 50) before rotation
    cells = [(o, o, "spark"), (o + step, o, "ink"), (o, o + step, "ink"), (o + step, o + step, "ink")]
    art = Art()
    for cx, cy, role in cells:
        if role == "spark":
            cx, cy = cx - lift, cy - lift  # lifted along the grid's diagonal
        # rotate centre 45 deg about (50, 50) so every tile stays axis-free
        dx, dy = cx - 50, cy - 50
        rx_, ry_ = 50 + (dx - dy) * 0.70710678, 50 + (dx + dy) * 0.70710678
        el, box = diamond(rx_, ry_, tile, rx, t[role])
        art.add(el, box)
    return art


def lockup_A(src, t):
    c = CFG["A"]
    word = src["kufi_A"]
    art = Art()
    el, wbox = path_el(word, t["ink"])
    art.add(el, wbox)
    # spark replaces the shadda, centred over the two qaf dots
    dots = pk.bbox(word[2:4])
    dcx = (dots[0] + dots[2]) / 2
    sp = c["spark"]
    half = sp / 2 ** 0.5
    el, box = diamond(dcx, dots[1] - 6 - half, sp, sp * 0.12, t["spark"])
    art.add(el, box)
    # mark: scaled so its height matches alef top to baseline, aligned to that band
    word_h = -wbox[1]
    m = mark_A(t)
    mh = m.box[3] - m.box[1]
    s = word_h * c["lockup_mark_h"] / mh
    gap = word_h * c["lockup_gap"]
    tx = wbox[2] + gap - m.box[0] * s
    ty = wbox[1] - m.box[1] * s
    el, box = m.placed(s, tx, ty)
    art.add(el, box)
    # WAQQAD tucked under د ا ق, from the dal's left edge to the qaf's right edge,
    # baseline level with the bottom of the waw's tail
    qaf = pk.bbox(word[4:5])
    el, box, _ = latin_line(src["latin"], c["latin_cap"], wbox[0], qaf[2], wbox[3], t["accent"])
    art.add(el, box)
    return art


def wordmark_A(src, t):
    """A's wordmark on its own: Kufi with the spark as shadda."""
    c = CFG["A"]
    word = src["kufi_A"]
    art = Art()
    el, wbox = path_el(word, t["ink"])
    art.add(el, wbox)
    dots = pk.bbox(word[2:4])
    sp = c["spark"]
    el, box = diamond((dots[0] + dots[2]) / 2, dots[1] - 6 - sp / 2 ** 0.5, sp, sp * 0.12, t["spark"])
    art.add(el, box)
    return art


# ---------------------------------------------------------------- B · Logotype

def logotype_B(src, t):
    c = CFG["B"]
    word = src["kufi_B"]
    art = Art()
    el, wbox = path_el(word, t["ink"])
    art.add(el, wbox)
    dots = pk.bbox(word[2:4])
    sp = c["spark"]
    el, box = diamond((dots[0] + dots[2]) / 2, dots[1] - 6.5 - sp / 2 ** 0.5, sp, sp * 0.12, t["spark"])
    art.add(el, box)
    # rule: same depth as the drafts (26 below baseline), from the dal's left edge
    # to just short of where the waw's tail lands, so the tail swings past its end
    tail = pk.bbox(word[6:7])
    ry, rh = 26, c["rule"]
    x1 = tail[0] - c["rule_gap_tail"]
    art.add(f'<rect x="{_n(wbox[0])}" y="{ry}" width="{_n(x1 - wbox[0])}" height="{rh}" '
            f'rx="{_n(rh / 2)}" fill="{t["accent"]}"/>', (wbox[0], ry, x1, ry + rh))
    # WAQQAD right-aligned to the rule's end, hanging under it
    cap = c["latin_cap"]
    w = latin_natural(src["latin"], cap, 0.12)
    base = ry + rh + 10 + cap
    el, box, _ = latin_line(src["latin"], cap, x1 - w, x1, base, t["ink"])
    art.add(el, box)
    return art


def favicon_B(t):
    art = Art()
    art.add('<rect x="0" y="0" width="100" height="100" rx="22" fill="%s"/>' % COLOR["navy"], (0, 0, 100, 100))
    el, _ = diamond(50, 42, 34, 4.08, t["spark"])
    art.els.append(el)
    art.els.append('<rect x="26" y="70" width="48" height="6" rx="3" fill="%s"/>' % COLOR["teal_light"])
    return art


# ---------------------------------------------------------------- C · Waw

def mark_C(t, ink=None):
    c = CFG["C"]
    ink = ink or t["ink"]
    r, sw = c["ring_r"], c["stroke"]
    art = Art()
    art.add(f'<circle cx="63" cy="36" r="{r}" fill="none" stroke="{ink}" stroke-width="{sw}"/>',
            (63 - r - sw / 2, 36 - r - sw / 2, 63 + r + sw / 2, 36 + r + sw / 2))
    art.add(f'<path d="M63 59C63 76 54 84 36 84" fill="none" stroke="{ink}" stroke-width="{sw}" '
            f'stroke-linecap="round"/>', (36 - sw / 2, 59, 63 + sw / 2, 84 + sw / 2))
    el, box = diamond(17, 84, c["spark"], 3, t["spark"])
    art.add(el, box)
    return art


def lockup_C(src, t):
    c = CFG["C"]
    word = src["plex_C"]
    art = Art()
    el, wbox = path_el(word, t["ink"])
    art.add(el, wbox)
    alef = pk.bbox(word[1:2])
    word_h = -alef[1]
    m = mark_C(t)
    mh = m.box[3] - m.box[1]
    s = word_h * c["lockup_mark_h"] / mh
    tx = wbox[2] + word_h * c["lockup_gap"] - m.box[0] * s
    ty = (alef[1] + wbox[3]) / 2 - (m.box[1] + m.box[3]) / 2 * s
    el, box = m.placed(s, tx, ty)
    art.add(el, box)
    # WAQQAD tucked under د ا ق, baseline level with the bottom of the waw's tail
    qaf = pk.bbox(word[3:4])
    tail_bottom = pk.bbox(word[7:8])[3]
    el, box, _ = latin_line(src["latin"], c["latin_cap"], wbox[0], qaf[2] - 6, tail_bottom, t["accent"])
    art.add(el, box)
    return art


def tile(mark_art, bg, pad=0.2, rx_ratio=0.22):
    """App-icon tile: mark optically centred on a rounded square."""
    x0, y0, x1, y1 = mark_art.box
    side = 100
    inner = side * (1 - 2 * pad)
    s = inner / max(x1 - x0, y1 - y0)
    tx = (side - (x1 - x0) * s) / 2 - x0 * s
    ty = (side - (y1 - y0) * s) / 2 - y0 * s
    art = Art()
    art.add(f'<rect width="100" height="100" rx="{_n(side * rx_ratio)}" fill="{bg}"/>', (0, 0, 100, 100))
    el, _ = mark_art.placed(s, tx, ty)
    art.els.append(el)
    return art


# ---------------------------------------------------------------- build

def build():
    src = load_sources()
    files = {}
    for name, th in THEMES.items():
        sfx = "" if name == "light" else "_" + name
        files[f"A_mark{sfx}"] = svg_doc(mark_A(th), th, square=True)
        files[f"A_lockup{sfx}"] = svg_doc(lockup_A(src, th), th)
        files[f"A_wordmark{sfx}"] = svg_doc(wordmark_A(src, th), th)
        files[f"B_logotype{sfx}"] = svg_doc(logotype_B(src, th), th)
        files[f"C_mark{sfx}"] = svg_doc(mark_C(th), th, square=True)
        files[f"C_lockup{sfx}"] = svg_doc(lockup_C(src, th), th)
    dark = THEMES["dark"]
    files["A_tile"] = svg_doc(tile(mark_A(dark), COLOR["navy"], pad=0.19), dict(bg=None), margin_ratio=0)
    files["B_favicon"] = svg_doc(favicon_B(THEMES["light"]), dict(bg=None), margin_ratio=0)
    files["C_tile"] = svg_doc(tile(mark_C(dark), COLOR["navy"], pad=0.17), dict(bg=None), margin_ratio=0)

    os.makedirs(OUT, exist_ok=True)
    for k, v in files.items():
        with open(os.path.join(OUT, k + ".svg"), "w", encoding="utf-8") as f:
            f.write(v)
    return files


def received():
    out = {}
    for fn in sorted(os.listdir(RECEIVED)):
        if fn.endswith(".svg"):
            out[fn[:-4]] = _read(fn)
    return out


# ---------------------------------------------------------------- lab page

NOTES = {
    "A": dict(
        name="Sharara", ar="الشرارة", score=22,
        idea="Four diamonds on a Najdi grid; the top one lifts away and turns amber. Heavy Kufi wordmark whose shadda is the same spark.",
        keys=dict(lockup="A_lockup", lockupDark="A_lockup_dark", mark="A_mark", icon="A_tile", mono="A_lockup_mono"),
        fixed=[
            dict(id="A-1", text="WAQQAD ran into the tail of the و. It now sits under د ا ق, from the edge of the dal to the edge of the qaf, with its baseline level with the bottom of the tail."),
            dict(id="A-2", text="The spark over the qaf was cut off by the top edge of the file. Every file now has clear space around it."),
            dict(id="A-3", text="The mark looked small next to the heavy Kufi. It now matches the wordmark's height, from the top of the alef to the baseline."),
            dict(id="A-4", text="The drafts had no app icon for A. Added one: white grid and amber spark on navy."),
        ],
        open=[
            dict(id="A-5", text="Two amber pieces in one lockup: the shadda and the mark. They compete for attention. Keep both, or keep only the spark in the mark and set the shadda in navy?",
                 options=["Keep both sparks", "Spark in mark only"]),
            dict(id="A-6", text="How far the spark lifts off the grid. Now 7 units, about a quarter of a tile.",
                 options=["Quieter (5)", "Keep (7)", "Bolder (10)"]),
            dict(id="A-7", text="Tile corners. Sharp corners look carved and Najdi; rounder corners look friendlier and more like a tech product.",
                 options=["Sharp (0)", "Keep (2.2)", "Softer (5)"]),
            dict(id="A-8", text="WAQQAD is now spaced out to span د ا ق. Keep that wide institutional spacing, or set it tight and align it to the left?",
                 options=["Wide, spanning", "Tight, left"]),
        ],
    ),
    "B": dict(
        name="Logotype", ar="الاسم علامةً", score=19,
        idea="The word itself is the identity: heavy Kufi, the shadda replaced by the spark, a teal rule beneath, WAQQAD small in Plex.",
        keys=dict(lockup="B_logotype", lockupDark="B_logotype_dark", mark="B_favicon", icon="B_favicon", mono="B_logotype_mono"),
        fixed=[
            dict(id="B-1", text="The teal rule cut through the tail of the و. It now stops just before the tail, which swings past its end."),
            dict(id="B-2", text="The spark sat 7.6 units left of the centre of the qaf's dots. It is now centred over them."),
            dict(id="B-3", text="The rule stuck out past the word, by different amounts on each side. It now starts at the edge of the dal."),
            dict(id="B-4", text="WAQQAD is right-aligned to the end of the rule, so the rule, the Latin and the tail line up."),
        ],
        open=[
            dict(id="B-5", text="The favicon (spark over a rule) shares no shape with the word. Options: keep it, use قّ with the spark cropped from the word, or borrow A's grid mark.",
                 options=["Keep favicon", "Crop قّ from the word", "Use A's mark"]),
            dict(id="B-6", text="B's Kufi is a heavier cut than A's. Whichever direction wins, which weight should the wordmark use?",
                 options=["A's lighter cut", "B's heavier cut"]),
        ],
    ),
    "C": dict(
        name="Waw monogram", ar="حرف الواو", score=19,
        idea="A geometric و: a thick ring and a sweeping tail, with the spark leaving its tip. Set beside the name in Plex Sans Arabic.",
        keys=dict(lockup="C_lockup", lockupDark="C_lockup_dark", mark="C_mark", icon="C_tile", mono="C_lockup_mono"),
        fixed=[
            dict(id="C-1", text="WAQQAD ran into the tail of the و in the wordmark. It now sits under د ا ق, with its baseline level with the bottom of the tail."),
            dict(id="C-2", text="The monogram is now 1.25 times the alef's height, centred on the word, with more space so its spark no longer crowds the و of the word."),
            dict(id="C-3", text="Added a navy version of the mark (the drafts only had a navy tile)."),
        ],
        open=[
            dict(id="C-4", text="A perfect circle with an even stroke reads as a 9 or an o to non-Arabic readers. A squarer, Kufi-style head would tie C to the Kufi wordmark and to A's grid.",
                 options=["Keep the circle", "Try a Kufi head"]),
            dict(id="C-5", text="At the end of the tail the spark reads as a full stop. It could sit where the pen starts, at the top right of the ring.",
                 options=["Keep at tail", "Move to ring top"]),
            dict(id="C-6", text="The wordmark is Plex with a regular shadda, so the spark appears only in the mark. Use A's Kufi wordmark beside the و instead?",
                 options=["Keep Plex", "Use A's Kufi"]),
        ],
    ),
    "S": dict(
        idea="Decisions that hold whichever direction wins.",
        fixed=[
            dict(id="S-1", text="All files are rebuilt from one script (brand/logo/build.py). The letter outlines come from your drafts unchanged, and every spacing value is a named setting, so each round changes a setting rather than hand-editing paths."),
            dict(id="S-2", text="Coordinates are rounded to 2 decimals (the drafts used up to 17), which roughly halves the file sizes. Every variant now also comes in one-colour navy for stamps, embroidery and fax."),
        ],
        open=[
            dict(id="S-3", text="On navy the drafts use a light teal (#7FD1DE) that the palette doesn't list. Add it to the palette as Teal Light, or use white for the Latin and the rule on navy?",
                 options=["Add Teal Light", "White on navy"]),
            dict(id="S-4", text="Which direction should round 2 focus on? We can keep the other two as references.",
                 options=["A", "B", "C", "A mark + C energy"]),
        ],
    ),
}


def write_lab(v0, v1):
    with open(os.path.join(HERE, "lab_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    page = (tpl.replace("/*DATA*/{}", json.dumps({"v0": v0, "v1": v1}, ensure_ascii=False))
               .replace("/*NOTES*/{}", json.dumps(NOTES, ensure_ascii=False)))
    # fragment for the hosted preview (the host adds the document skeleton)
    with open(os.path.join(HERE, "lab.fragment.html"), "w", encoding="utf-8") as f:
        f.write(page)
    # full document for opening straight from the repo
    head, _, body = page.partition("</style>")
    with open(os.path.join(HERE, "..", "logo-lab.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


if __name__ == "__main__":
    v1 = build()
    v0 = received()
    write_lab(v0, v1)
    print(f"v1: {len(v1)} files -> {OUT}; lab page -> brand/logo-lab.html")
