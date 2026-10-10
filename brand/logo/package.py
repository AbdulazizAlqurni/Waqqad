"""The final logo package: brand/waqqad-logo/.

    python3 package.py        -> every SVG variant, the README and guidelines.html
    node package.js           -> the PNGs, the favicon.ico and the PDF

Approved: the symbol (round 4) and the name in Reem Kufi SemiBold with a real
shadda, WAQQAD spaced under د ا ق (round 5). Stacked is the lead lockup;
horizontal has equal standing.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402
import final as FS  # noqa: E402
import typography as T  # noqa: E402

PKG = os.path.join(HERE, "..", "waqqad-logo")
VOICE = "reem_kufi_600"
NAVY, AMBER, WHITE, TEAL, MIST, PALE = FS.NAVY, FS.AMBER, FS.WHITE, "#007C91", "#F3F5F8", FS.PALE

T.THEMES.update({
    "full-colour": dict(ink=NAVY, latin=TEAL, sym="light"),
    "on-dark": dict(ink=WHITE, latin=WHITE, sym="dark"),
    "navy-bg": dict(ink=WHITE, latin=WHITE, sym="dark", bg=NAVY),
    "mono-navy": dict(ink=NAVY, latin=NAVY, sym="mono"),
    "mono-white": dict(ink=WHITE, latin=WHITE, sym="mono-white"),
})
VARIANTS = ["full-colour", "on-dark", "navy-bg", "mono-navy", "mono-white"]

# clear space and minimum sizes (also written into the README and the PDF)
S_H = T.ALEF_H * T.LOCKUP["mark_h"] / (FS.BOX[3] - FS.BOX[1])        # symbol scale, horizontal
S_V = T.ALEF_H * T.LOCKUP["stack_mark_h"] / (FS.BOX[3] - FS.BOX[1])  # symbol scale, stacked
X_H, X_V = 2 * FS.TIP * S_H, 2 * FS.TIP * S_V                        # x = width of the amber diamond
MIN = {"stacked": "72 px tall on screen, 20 mm tall in print",
       "horizontal": "120 px wide on screen, 35 mm wide in print",
       "symbol": "16 px on screen, 6 mm in print"}


def the_word():
    return T.word_from_font(B.SRC["outlines"]["arabic_shadda"][VOICE])


def lockup(kind, theme, word=None, margin=0.12):
    w = word or the_word()
    els, box = (T.stacked if kind == "stacked" else T.horizontal)(w, theme)
    return T.doc(els, box, theme, margin=margin), els, box


def write(path, text):
    p = os.path.join(PKG, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def svg_files():
    files = {}
    w = the_word()
    for kind in ("stacked", "horizontal"):
        for v in VARIANTS:
            files[f"svg/{kind}/waqqad-logo-{kind}-{v}.svg"] = lockup(kind, v, w)[0]
    for v in ("full-colour", "on-dark", "mono-navy", "mono-white"):
        ink = WHITE if v in ("on-dark", "mono-white") else NAVY
        files[f"svg/name/waqqad-name-{v}.svg"] = T.doc([w.make(ink)], w.box, "full-colour", margin=0.04)
    sym = {"full-colour": FS.symbol("light"), "on-dark": FS.symbol("dark"),
           "navy-bg": FS.symbol("dark", bg=NAVY, margin=FS.CLEAR, square=True),
           "mono-navy": FS.symbol("mono"), "mono-white": FS.symbol("mono-white")}
    for v, s in sym.items():
        files[f"svg/symbol/waqqad-symbol-{v}.svg"] = s
    files["icons/waqqad-app-icon.svg"] = FS.app_icon()
    return files


def copy_motion():
    src = os.path.join(HERE, "final", "symbol")
    for sub in ("motion", "video"):
        dst = os.path.join(PKG, "motion" if sub == "motion" else "motion/video")
        os.makedirs(dst, exist_ok=True)
        for fn in os.listdir(os.path.join(src, sub)):
            shutil.copy2(os.path.join(src, sub, fn), os.path.join(dst, fn))


# ---------------------------------------------------------------- figures for the PDF

def clear_space(kind):
    _, els, box = lockup(kind, "full-colour")
    x = X_V if kind == "stacked" else X_H
    x0, y0, x1, y1 = box
    m = x * 1.6
    frame = (f'<rect x="{FS.n(x0 - x)}" y="{FS.n(y0 - x)}" width="{FS.n(x1 - x0 + 2 * x)}" height="{FS.n(y1 - y0 + 2 * x)}" '
             f'fill="none" stroke="{AMBER}" stroke-width="1.2" stroke-dasharray="5 4"/>'
             f'<rect x="{FS.n(x0)}" y="{FS.n(y0)}" width="{FS.n(x1 - x0)}" height="{FS.n(y1 - y0)}" fill="none" '
             f'stroke="#8FA1B8" stroke-width=".8"/>')
    # one x-unit marker in the top-left gap
    mk = B.diamond(x0 - x / 2, y0 - x / 2, x / R2_, x * 0.05, AMBER)[0]
    lab = (f'<text x="{FS.n(x0 - x / 2)}" y="{FS.n(y0 - x / 2 + 3)}" font-family="IBM Plex Mono, monospace" '
           f'font-size="{FS.n(x * .32)}" text-anchor="middle" fill="{NAVY}">x</text>')
    return T.doc([frame, mk, lab] + els, (x0 - m, y0 - m, x1 + m, y1 + m), "full-colour", margin=0)


R2_ = 2 ** 0.5


def misuse():
    """Eight ways not to use the logo, each drawn for real."""
    base, els, box = lockup("horizontal", "full-colour")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w_plex = T.word_from_font(B.SRC["outlines"]["arabic_shadda"]["plex_ar_700"])
    inner = "".join(els)
    flame = base.replace(f'd="{FS.DIA}"/>', f'd="{FS.FL["a"]}"/><path fill="{PALE}" d="{FS.CO["a"]}"/>')
    # symbol on the wrong side: mirror the arrangement, not the shapes
    w = the_word()
    sym, sbox = T.place(T.symbol_art("light"), T.ALEF_H, x_right=w.box[0] - T.ALEF_H * T.LOCKUP["gap"], top=w.alef_top)
    wrong = T.doc([w.make(NAVY), sym], T.grow(w.box, sbox), "full-colour")
    items = [
        ("Don't stretch or squash it", T.doc([f'<g transform="translate({FS.n(cx)} {FS.n(cy)}) scale(1.35 0.8) translate({FS.n(-cx)} {FS.n(-cy)})">{inner}</g>'], box, "full-colour")),
        ("Don't recolour the tiles", base.replace(f'fill="{NAVY}" transform="rotate(45)"', f'fill="{TEAL}" transform="rotate(45)"')),
        ("Don't rotate it", T.doc([f'<g transform="rotate(-10 {FS.n(cx)} {FS.n(cy)})">{inner}</g>'], box, "full-colour", margin=.3)),
        ("Don't show the flame in print", flame),
        ("Don't retype the name", lockup("horizontal", "full-colour", w_plex)[0]),
        ("Don't move the symbol to the left", wrong),
        ("Don't add shadows or outlines", T.doc([f'<g style="filter:drop-shadow(6px 8px 4px rgba(0,0,0,.45))">{inner}</g>'], box, "full-colour")),
        ("Don't place it on amber or busy colour", T.doc([f'<rect x="{FS.n(x0 - 30)}" y="{FS.n(y0 - 30)}" width="{FS.n(x1 - x0 + 60)}" height="{FS.n(y1 - y0 + 60)}" fill="{AMBER}"/>', inner], (x0 - 30, y0 - 30, x1 + 30, y1 + 30), "full-colour", margin=0)),
    ]
    return items


# ---------------------------------------------------------------- README

README = """# وقّاد · Waqqad logo

Version 1.0 · October 2026 · approved by the partners.

This folder is the logo and everything needed to use it. The guidelines PDF
(`waqqad-logo-guidelines.pdf`) shows all of it on 13 pages. This file says the
same in text, and tells you which file to pick.

## The idea

**وقّاد** means kindling, bright, sharp-minded. The logo says it in two parts:

- **The symbol.** Four squares on a grid turned 45°: the structure, the
  institution, the system that stands up to scrutiny. The top square has
  lifted out and turned amber. That is the spark: the idea that comes out of
  the structure.
- **The name.** وقّاد in Reem Kufi SemiBold, a geometric Kufi with a tall alef
  and a calligrapher's shadda, with **WAQQAD** spaced underneath in IBM Plex Sans.

On screen the spark comes alive. When you hover, when a page loads, and in
videos, the amber diamond ignites into an upright flame with a pale core,
burns, then settles back into the diamond. In print, and anywhere that
cannot move, the logo is always the still diamond, never the flame.

## The two lockups

| | When to use it |
|---|---|
| **Stacked** (lead) | Square and tall spaces: covers, social avatars and posts, the app splash, signage, stands, merchandise. |
| **Horizontal** | Wide, short spaces: website and app headers, letterheads, contracts, email signatures, slides, invoices. |

Both are approved and carry equal weight. Pick the one that fits the space. Never build a third arrangement.

How they're built (the name's alef height = **A**):

- Horizontal: symbol height = A, and the symbol sits to the right of the name (where Arabic reading starts) with a gap of 0.55 A. WAQQAD runs under د ا ق, from the dal's edge to the qaf.
- Stacked: symbol height = 1.3 A, centred above the name, with a gap of 0.34 A. WAQQAD spans the full width of the name.

The symbol may also stand alone (app icon, favicon, avatar, a stamp seal, the
corner of a slide) once people already know the name, or where the full logo
appears nearby.

## Colour

| Name | HEX | RGB | Role |
|---|---|---|---|
| Navy | `#0B1F3A` | 11 31 58 | Tiles, the name, backgrounds |
| Amber | `#F2A93B` | 242 169 59 | The spark, and nothing else |
| Teal | `#007C91` | 0 124 145 | WAQQAD on light backgrounds; links and rules in documents |
| Mist | `#F3F5F8` | 243 245 248 | Paper and page backgrounds |
| White | `#FFFFFF` | 255 255 255 | Tiles, name and WAQQAD on navy |
| Pale core | `#FFE3A8` | 255 227 168 | Inside the flame. Motion only, never in print |

For print, ask the printer to match the HEX values; don't convert them by eye.

## Versions

| File suffix | Use it on |
|---|---|
| `full-colour` | White, Mist and light photos. The default. |
| `on-dark` | Navy and dark photos (transparent background, white letters). |
| `navy-bg` | When you need the navy box included, e.g. social posts and slides. |
| `mono-navy` | One-colour printing: stamps, embossing, fax, engraving, newspaper. |
| `mono-white` | One colour reversed out of a dark background or photo. |

## Clear space and minimum size

- Clear space: **x** on every side, where x is the width of the amber diamond in that lockup. Nothing else may enter it.
- The symbol on its own needs ½ x.
- Minimum sizes:
  - Stacked: {min_stacked}.
  - Horizontal: {min_horizontal}.
  - Symbol: {min_symbol}. Below that size, use the app icon file.

## Typography

- **Reem Kufi SemiBold** is used for the name inside the logo and nowhere
  else. Never type the name in it; use the logo files.
- **IBM Plex Sans Arabic**: headings 600, body 400.
- **IBM Plex Sans**: Latin, same weights.
- All three are free, under the SIL Open Font License, on Google Fonts.

## Motion: Ignite

| State | When | What moves | Timing |
|---|---|---|---|
| Rest | Always | Nothing | — |
| Ignite | Hover, keyboard focus, tap | Only the amber diamond: it becomes the flame, and the pale core grows | 0.38 s |
| Burn | While hovered or loading | The flame cycles three shapes; the core flickers out of step | 1.1 s and 0.8 s loops |
| Settle | Pointer leaves, load ends | The flame returns to the diamond | 0.5 s |
| Entrance | Page load, start of a video | Tiles pop in, the spark rises and warms, ignites, burns, settles | 3.8 s |

The tiles never move on hover. When the viewer prefers reduced motion, nothing moves.

For the web: paste `motion/waqqad-symbol-live.svg` inline, then include
`motion/waqqad-symbol-motion.css` and `motion/waqqad-symbol-motion.js`, and call
`WaqqadSymbol.bind(element)`. For video, use `motion/video/waqqad-symbol-intro-1080p.mp4`.

## Don't

- Stretch, squash or rotate the logo.
- Recolour the tiles, or use amber for anything but the spark.
- Show the flame in print or in still images. Its place is motion.
- Retype the name in any font, or rearrange the parts (the symbol always sits at the start, on the right).
- Add shadows, outlines, gradients or glows.
- Place it on amber, on busy patterns, or on photos where it loses contrast.

## Which file?

| You need | Use |
|---|---|
| Website header | `svg/horizontal/waqqad-logo-horizontal-full-colour.svg`, or the live symbol from `motion/` |
| Social avatar | `png/symbol/waqqad-symbol-navy-bg.png` or `icons/png/waqqad-app-icon-1024.png` |
| Social post or cover | `svg/stacked/` or `png/stacked/` |
| Letterhead, invoice, contract | `svg/horizontal/waqqad-logo-horizontal-full-colour.svg` |
| Stamp, engraving, one-colour print | `svg/*/…-mono-navy.svg` |
| Favicon | `icons/favicon.ico`, `icons/png/favicon-32.png` |
| App icon | `icons/waqqad-app-icon.svg`, `icons/png/waqqad-app-icon-1024.png` |
| Video intro | `motion/video/waqqad-symbol-intro-1080p.mp4` |
| Office documents (Word, PowerPoint) | the PNGs in `png/` |

## Folder

```
waqqad-logo/
  README.md                      this file
  waqqad-logo-guidelines.pdf     the guidelines, 13 pages
  svg/stacked/                   5 versions of the lead lockup
  svg/horizontal/                5 versions of the horizontal lockup
  svg/symbol/                    the symbol alone, 5 versions
  svg/name/                      the name alone, for designers only
  png/                           the same files as PNG (lockups 2400 px wide, symbol 1024 px)
  icons/                         app icon (SVG and PNG at 1024, 512, 180) and favicons (ICO, 32, 16)
  motion/                        live SVG and CSS/JS for the web, loop and intro SVGs, video/
```

Source: everything is generated by `brand/logo/package.py` (SVGs, README,
guidelines page) and `brand/logo/package.js` (PNGs, ICO, PDF) from the same
geometry that was reviewed in the Logo Lab, so the files always match each other.
"""


def readme():
    return README.replace("{min_stacked}", MIN["stacked"]).replace("{min_horizontal}", MIN["horizontal"]) \
        .replace("{min_symbol}", MIN["symbol"])


# ---------------------------------------------------------------- guidelines (HTML -> PDF)

def guidelines(files):
    s = lambda k: files[k]  # noqa: E731
    with open(os.path.join(HERE, "guidelines_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    data = {
        "cover": s("svg/stacked/waqqad-logo-stacked-on-dark.svg"),
        "stacked": s("svg/stacked/waqqad-logo-stacked-full-colour.svg"),
        "horizontal": s("svg/horizontal/waqqad-logo-horizontal-full-colour.svg"),
        "stackedDark": s("svg/stacked/waqqad-logo-stacked-on-dark.svg"),
        "horizontalDark": s("svg/horizontal/waqqad-logo-horizontal-on-dark.svg"),
        "symbol": s("svg/symbol/waqqad-symbol-full-colour.svg"),
        "symbolDark": s("svg/symbol/waqqad-symbol-on-dark.svg"),
        "name": s("svg/name/waqqad-name-full-colour.svg"),
        "construction": FS.construction(),
        "clearStacked": clear_space("stacked"),
        "clearHorizontal": clear_space("horizontal"),
        "versions": {v: {"stacked": s(f"svg/stacked/waqqad-logo-stacked-{v}.svg"),
                         "horizontal": s(f"svg/horizontal/waqqad-logo-horizontal-{v}.svg")} for v in VARIANTS},
        "frames": [{"label": "Rest", "svg": FS.frame(FS.DIA, None)},
                   {"label": "Ignite · 0.38 s", "svg": FS.frame(FS.FL["a"], FS.CO["a"])},
                   {"label": "Burn", "svg": FS.frame(FS.FL["b"], FS.CO["b"])},
                   {"label": "Burn", "svg": FS.frame(FS.FL["c"], FS.CO["c"])},
                   {"label": "Settle · 0.5 s", "svg": FS.frame(FS.DIA, None)}],
        "icon": FS.app_icon(),
        "monoNavyH": s("svg/horizontal/waqqad-logo-horizontal-mono-navy.svg"),
        "misuse": [{"label": a, "svg": b} for a, b in misuse()],
        "min": MIN,
    }
    return tpl.replace("/*DATA*/{}", json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    B.SRC = B.load_sources()
    if os.path.isdir(PKG):
        shutil.rmtree(PKG)
    files = svg_files()
    for k, v in files.items():
        write(k, v)
    copy_motion()
    write("README.md", readme())
    with open(os.path.join(HERE, "guidelines.html"), "w", encoding="utf-8") as f:
        f.write(guidelines(files))
    print(f"package: {len(files)} SVGs, README, guidelines.html -> {os.path.normpath(PKG)}")
