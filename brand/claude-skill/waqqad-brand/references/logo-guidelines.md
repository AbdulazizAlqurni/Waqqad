# وقّاد · Waqqad logo

> Copied from the brand package README. In this skill the files live under `assets/`:
> `svg/…` → `assets/svg/…`, `png/…` → `assets/png/…`, `icons/png/…` and `icons/…` → `assets/icons/…`, `motion/…` → `assets/motion/…`.
> Not in the skill: `motion/video/` (the MP4 intro) and the guidelines PDF; use the repository copies.
> The skill carries the most-used files; the full package (all PNGs, the video, the guidelines PDF) is in the
> repository AbdulazizAlqurni/Waqqad under `brand/waqqad-logo/`.

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
  - Stacked: 72 px tall on screen, 20 mm tall in print.
  - Horizontal: 120 px wide on screen, 35 mm wide in print.
  - Symbol: 16 px on screen, 6 mm in print. Below that size, use the app icon file.

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
