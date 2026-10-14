"""Outline Arabic and Latin text from open fonts into SVG path data.

Used once per typography round: shapes text with HarfBuzz, so Arabic joins and
ligatures come out right, and writes the outlines to type_outlines.json, so
build.py never needs the fonts. Needs `pip install fonttools uharfbuzz`.

    python3 typeset.py            # fetch fonts if missing, rewrite type_outlines.json
"""
import json
import os
import sys
import urllib.parse
import urllib.request

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("WAQQAD_FONT_CACHE", os.path.join(HERE, ".fonts"))
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# every face is SIL Open Font License, from the Google Fonts repository
FONTS = {
    "noto_kufi": ("notokufiarabic", "NotoKufiArabic[wght].ttf"),
    "reem_kufi": ("reemkufi", "ReemKufi[wght].ttf"),
    "kufam": ("kufam", "Kufam[wght].ttf"),
    "plex_ar": ("ibmplexsansarabic", "IBMPlexSansArabic-Bold.ttf"),
    "plex_ar_semi": ("ibmplexsansarabic", "IBMPlexSansArabic-SemiBold.ttf"),
    "readex": ("readexpro", "ReadexPro[HEXP,wght].ttf"),
    "changa": ("changa", "Changa[wght].ttf"),
    "alexandria": ("alexandria", "Alexandria[wght].ttf"),
    "messiri": ("elmessiri", "ElMessiri[wght].ttf"),
    "plex_en": ("ibmplexsans", "IBMPlexSans[wdth,wght].ttf"),
}


def font_path(key):
    fam, fn = FONTS[key]
    path = os.path.join(CACHE, fn)
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(GF + fam + "/" + urllib.parse.quote(fn), path)
    return path


def shape(key, text, size=100, variations=None, features=None):
    """Return glyph outlines for `text` at `size` units per em, baseline y=0,
    y pointing down (SVG). Each glyph: dict(cluster, d, x0, y0, x1, y1)."""
    path = font_path(key)
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    if variations:
        font.set_variations(variations)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True})

    tt = TTFont(path)
    if variations and "fvar" in tt:
        from fontTools.varLib.instancer import instantiateVariableFont
        tt = instantiateVariableFont(tt, variations, inplace=False)
    upem = tt["head"].unitsPerEm
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = size / upem

    glyphs, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        pen = SVGPathPen(gs)
        ox, oy = x + pos.x_offset, pos.y_offset
        tp = TransformPen(pen, (s, 0, 0, -s, ox * s, -oy * s))
        gs[name].draw(tp)
        d = pen.getCommands()
        x += pos.x_advance
        if d:
            glyphs.append(dict(cluster=info.cluster, name=name, d=d))
    return glyphs, x * s


ARABIC = "وقاد"
ARABIC_SHADDA = "وقّاد"   # round 5 on: a real shadda on the qaf
LATIN = "WAQQAD"

# name -> (font key, weight variations or None)
SETS = {
    "noto_kufi_900": ("noto_kufi", {"wght": 900}),
    "noto_kufi_700": ("noto_kufi", {"wght": 700}),
    "reem_kufi_700": ("reem_kufi", {"wght": 700}),
    "reem_kufi_600": ("reem_kufi", {"wght": 600}),   # the approved voice (round 5: one step lighter)
    "reem_kufi_500": ("reem_kufi", {"wght": 500}),
    "kufam_800": ("kufam", {"wght": 800}),
    "plex_ar_700": ("plex_ar", None),
    "readex_700": ("readex", {"wght": 700, "HEXP": 0}),
    "changa_800": ("changa", {"wght": 800}),
    "alexandria_800": ("alexandria", {"wght": 800}),
    "messiri_700": ("messiri", {"wght": 700}),
}


def main():
    out = {"arabic": {}, "latin": {}}
    for name, (key, var) in SETS.items():
        glyphs, adv = shape(key, ARABIC, 100, var)
        out["arabic"][name] = dict(glyphs=glyphs, advance=adv, font=FONTS[key][1])
    out["arabic_shadda"] = {}
    for name, (key, var) in SETS.items():
        glyphs, adv = shape(key, ARABIC_SHADDA, 100, var)
        out["arabic_shadda"][name] = dict(glyphs=glyphs, advance=adv, font=FONTS[key][1])
    for w in (500, 600):
        glyphs, adv = shape("plex_en", LATIN, 100, {"wght": w, "wdth": 100})
        out["latin"][f"plex_{w}"] = dict(glyphs=glyphs, advance=adv, font=FONTS["plex_en"][1])
    with open(os.path.join(HERE, "type_outlines.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("wrote type_outlines.json:", ", ".join(out["arabic"]))


if __name__ == "__main__":
    sys.exit(main())
