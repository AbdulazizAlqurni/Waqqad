"""Round 5: typography only. The name beside the approved symbol.

    python3 typography.py   -> v5/type/*.svg and the Lab page

Each voice sets وقّاد with a real shadda (the diamond shadda is retired),
scaled so every alef is the same height, and composes it with the final
symbol (final.py) as a horizontal and a stacked lockup. The symbol itself is
not touched here.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402  (Latin line, sources)
import final as FS  # noqa: E402  (the approved symbol)
import pathkit as pk  # noqa: E402

OUT = os.path.join(HERE, "v5", "type")
ALEF_H = 91.2

THEMES = {
    "light": dict(ink=FS.NAVY, latin=B.COLOR["teal"], sym="light"),
    "dark": dict(ink=FS.WHITE, latin=FS.WHITE, sym="dark", bg=FS.NAVY),
    "mono": dict(ink=FS.NAVY, latin=FS.NAVY, sym="mono"),
}

LOCKUP = dict(mark_h=1.0, gap=0.55, latin_cap=20, latin_gap=9,          # horizontal
              stack_mark_h=1.3, stack_gap=0.34, stack_latin_cap=17, stack_latin_gap=16)

VOICES = {
    "current": dict(name="Current Kufi", ar="الكوفي الحالي", key="noto_kufi_900", tag="reference",
                    face="Noto Kufi Arabic, Black · SIL OFL",
                    idea="The drafts' Kufi, now with a real shadda. Heavy and flat; the yardstick for the other five."),
    "grid": dict(name="Grid Kufi", ar="الكوفي المربّع", key=None,
                 face="Custom: drawn on cells, one cell stroke, one cell space",
                 idea="Square Kufi on the same 45° logic as the symbol's grid, with diamond dots on the ق and a square-cut shadda. The only voice no one else can have.",
                 risk="Square Kufi takes a moment to read, and it is the hardest to set small."),
    "reem": dict(name="Reem Kufi", ar="ريم كوفي", key="reem_kufi_700",
                 face="Reem Kufi, Bold · SIL OFL",
                 idea="Fatimid geometric Kufi: a tall alef, a slanted dal, a calligrapher's shadda. Heritage made modern, and the most elegant.",
                 risk="Lighter strokes than the tiles, so the symbol can look heavy beside it."),
    "changa": dict(name="Changa", ar="تشانجا", key="changa_800",
                   face="Changa, ExtraBold · SIL OFL",
                   idea="Condensed technical Kufi. Its dots are already diamonds, which rhyme with the symbol, and its و ends in a cut.",
                   risk="Common in tech and gaming; it leans product rather than institution."),
    "readex": dict(name="Readex Pro", ar="ريدكس برو", key="readex_700",
                   face="Readex Pro, Bold · SIL OFL",
                   idea="A modern sans with diamond dots and open, rounded letters. The friendliest, and the easiest to read at a glance.",
                   risk="Its round letters sit softly beside the sharp diamonds."),
    "plex": dict(name="IBM Plex Sans Arabic", ar="بليكس عربي", key="plex_ar_700",
                 face="IBM Plex Sans Arabic, Bold · SIL OFL",
                 idea="The system typeface itself, so logo, interface and documents share one voice. The quietest and most institutional.",
                 risk="Anyone can set it, so the name alone is not ownable; the symbol does the work."),
}


class Word:
    def __init__(self, make, box, alef_top, qaf_right):
        self.make, self.box, self.alef_top, self.qaf_right = make, box, alef_top, qaf_right


def word_from_font(rec):
    """Clusters for وقّاد: 0 و, 1 ق with its dots and shadda, 3 ا, 4 د."""
    glyphs = rec["glyphs"]
    alef = [s for g in glyphs if g["cluster"] == 3 for s in pk.parse(g["d"])]
    s = ALEF_H / -pk.bbox(alef)[1]
    subs, qaf, waw = [], [], []
    for g in glyphs:
        sp = pk.transform(pk.parse(g["d"]), s)
        subs += sp
        if g["cluster"] == 1 and "0651" not in g["name"] and "shadda" not in g["name"]:
            qaf += sp
        if g["cluster"] == 0:
            waw += sp
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])  # noqa: E731
    body = max(qaf, key=lambda q: area(pk.bbox([q])))
    d = pk.to_d(subs)
    # the Latin line ends at the qaf, or a clear gap before the waw's tail if that curls further left
    latin_end = min(pk.bbox([body])[2], pk.bbox(waw)[0] - 0.14 * ALEF_H)
    return Word(lambda fill: f'<path fill="{fill}" d="{d}"/>', pk.bbox(subs), -ALEF_H, latin_end)


def word_grid():
    """Square Kufi وقّاد on cells (round 2's grid Kufi plus a square-cut shadda)."""
    c = ALEF_H / 6
    cells = [(2, 2, 1, 4), (0, 5, 3, 1), (4, 0, 1, 6), (4, 5, 3, 1),
             (6, 3, 3, 1), (6, 5, 3, 1), (6, 3, 1, 3), (8, 3, 1, 3),
             (10, 3, 3, 1), (10, 5, 3, 1), (10, 3, 1, 3), (12, 3, 1, 3),
             (12, 5, 1, 3), (9, 7, 4, 1)]
    y0 = -6 * c
    rects = [(x * c, y * c + y0, w * c, h * c) for x, y, w, h in cells]
    # shadda: three short stems on a bar, half-cell strokes, centred over the qaf
    hs = c * 0.5
    sy1, sy0 = y0 - 0.25 * c, y0 - 1.45 * c
    sh = [(6.25 * c, sy1 - hs, 2.5 * c, hs)] + [(x * c, sy0, hs, sy1 - sy0) for x in (6.25, 7.25, 8.25)]
    allr = rects + sh

    def make(fill):
        d = "".join(f"M{FS.n(x)} {FS.n(y)}H{FS.n(x + w)}V{FS.n(y + h)}H{FS.n(x)}Z" for x, y, w, h in allr)
        dots = "".join(B.diamond((col + .5) * c, 1.5 * c + y0, c * .92, c * .1, fill)[0] for col in (6, 8))
        return f'<path fill="{fill}" d="{d}"/>' + dots

    xs = [r[0] for r in allr] + [r[0] + r[2] for r in allr]
    ys = [r[1] for r in allr] + [r[1] + r[3] for r in allr]
    return Word(make, (min(xs), min(ys), max(xs), max(ys)), -ALEF_H, 8.4 * c)


def word(key):
    if key == "grid":
        return word_grid()
    return word_from_font(B.SRC["outlines"]["arabic_shadda"][VOICES[key]["key"]])


def symbol_art(theme):
    t = FS.THEMES[theme]
    return FS.tiles(t) + FS.spark(t), FS.BOX


def place(art_box, h, x_left=None, x_right=None, top=None, cx=None):
    """Scale the symbol to height h and position it; returns (svg group, bbox)."""
    (art, (x0, y0, x1, y1)) = art_box
    s = h / (y1 - y0)
    w = (x1 - x0) * s
    if cx is not None:
        tx = cx - w / 2 - x0 * s
    elif x_left is not None:
        tx = x_left - x0 * s
    else:
        tx = x_right - w - x0 * s
    ty = top - y0 * s
    return (f'<g transform="translate({FS.n(tx)} {FS.n(ty)}) scale({s:.4f})">{art}</g>',
            (x0 * s + tx, top, x0 * s + tx + w, top + h))


def doc(els, box, theme, margin=0.12):
    x0, y0, x1, y1 = box
    m = (y1 - y0) * margin
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    bg = THEMES[theme].get("bg")
    b = f'<rect x="{FS.n(x0)}" y="{FS.n(y0)}" width="{FS.n(x1 - x0)}" height="{FS.n(y1 - y0)}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{FS.n(x0)} {FS.n(y0)} {FS.n(x1 - x0)} {FS.n(y1 - y0)}" '
            f'width="{FS.n(x1 - x0)}" height="{FS.n(y1 - y0)}">{b}{"".join(els)}</svg>')


def grow(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def horizontal(w, theme):
    t, c = THEMES[theme], LOCKUP
    els, box = [w.make(t["ink"])], w.box
    sym, sbox = place(symbol_art(t["sym"]), ALEF_H * c["mark_h"], x_left=w.box[2] + ALEF_H * c["gap"], top=w.alef_top)
    els.append(sym)
    box = grow(box, sbox)
    base = max(w.box[3], c["latin_gap"] + c["latin_cap"])
    el, lbox = B.latin_line(B.SRC["latin"], c["latin_cap"], w.box[0], w.qaf_right, base, t["latin"])
    els.append(el)
    return els, grow(box, lbox)


def stacked(w, theme):
    t, c = THEMES[theme], LOCKUP
    cx = (w.box[0] + w.box[2]) / 2
    mh = ALEF_H * c["stack_mark_h"]
    top = w.box[1] - ALEF_H * c["stack_gap"] - mh
    sym, sbox = place(symbol_art(t["sym"]), mh, cx=cx, top=top)
    els, box = [w.make(t["ink"]), sym], grow(w.box, sbox)
    base = w.box[3] + c["stack_latin_gap"] + c["stack_latin_cap"]
    el, lbox = B.latin_line(B.SRC["latin"], c["stack_latin_cap"], w.box[0], w.box[2], base, t["latin"])
    els.append(el)
    return els, grow(box, lbox)


def name_only(w, theme):
    return [w.make(THEMES[theme]["ink"])], w.box


def build():
    B.SRC = B.load_sources()
    os.makedirs(OUT, exist_ok=True)
    data = {}
    for k, meta in VOICES.items():
        w = word(k)
        files = {}
        for theme in ("light", "dark", "mono"):
            for kind, fn in (("h", horizontal), ("v", stacked), ("name", name_only)):
                els, box = fn(w, theme)
                files[f"{kind}_{theme}"] = doc(els, box, theme, margin=0.02 if kind == "name" else 0.12)
        for name, svg in files.items():
            with open(os.path.join(OUT, f"{k}_{name}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
        data[k] = dict(meta, **{k2: files[k2] for k2 in ("h_light", "h_dark", "v_light", "v_dark", "name_light", "h_mono")})
    return data


def write_lab(data):
    with open(os.path.join(HERE, "lab_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    page = tpl.replace("/*DATA*/{}", json.dumps(data, ensure_ascii=False)).replace("/*MOTION_CSS*/", FS.MOTION_CSS)
    with open(os.path.join(HERE, "lab.fragment.html"), "w", encoding="utf-8") as f:
        f.write(page)
    head, _, body = page.partition("</style>")
    with open(os.path.join(HERE, "..", "logo-lab.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


if __name__ == "__main__":
    voices = build()
    write_lab({"voices": voices, "live": {"light": FS.symbol_live("light"), "dark": FS.symbol_live("dark")},
               "icon": FS.app_icon()})
    print(f"v5 typography: {len(voices)} voices -> {OUT}")
