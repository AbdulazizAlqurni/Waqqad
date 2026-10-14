---
name: waqqad-brand
description: >-
  The approved وقّاد (Waqqad) brand identity, with the real logo files, colours, fonts, layout rules and the "Ignite" motion. Use this skill whenever you make anything for Waqqad or وقّاد / وقاد, the Saudi company: documents, proposals, quotations, invoices, contracts, letters, slide decks, social posts and avatars, website pages, landing pages, artifacts, dashboards, email signatures, business cards, certificates, banners or videos. Also use it when the user says "our brand", "our logo", "on-brand", "our colours", "Waqqad style" or "هوية وقّاد", or asks to put the logo on something, even if they don't name the brand. This replaces the old identity (the blue flame and Janna LT); never use the old one.
---

# وقّاد · Waqqad brand

Use this skill to make on-brand work for Waqqad. It contains the approved logo files, so **place the real files; never redraw, retype or approximate the logo.**

## The brand in one minute

- **The name**: وقّاد means kindling: bright, sharp-minded, the one who lights things. The company builds governance systems for Saudi charities, universities and institutions. Its work has to look trustworthy enough for a board to sign.
- **The symbol**: four squares on a grid turned 45°. The grid stands for the structure and the institution. The top square has lifted out and turned amber: that is the spark, the idea that comes out of the structure.
- **The name in the logo**: وقّاد in Reem Kufi SemiBold with a real shadda, and WAQQAD letter-spaced underneath in IBM Plex Sans.
- **Motion**: on screens, the amber diamond can ignite into an upright amber flame with a pale core, then settle back. In print and in still images, the logo is always the still diamond.
- **The feel**: modern Saudi institution. Institutional first, clever second, and calm, with plenty of white or Mist space. The spark is the only flourish.

## Files in this skill

```
assets/svg/stacked/      waqqad-logo-stacked-{full-colour,on-dark,navy-bg,mono-navy,mono-white}.svg
assets/svg/horizontal/   waqqad-logo-horizontal-{…same five…}.svg
assets/svg/symbol/       waqqad-symbol-{…same five…}.svg
assets/png/…             PNG copies (lockups 2400 px wide, symbol 1024 px) for Word, PowerPoint, images
assets/icons/            app icon (SVG, 1024 PNG), favicon.ico, favicon-32.png
assets/motion/           live SVG + waqqad-symbol-motion.css/.js (hover "Ignite"), loop and intro SVGs
references/tokens.css    colour and type tokens, ready to paste
references/logo-guidelines.md   the full logo rules (clear space, sizes, misuse, motion timings)
```

Read `references/logo-guidelines.md` when a job needs exact rules: clear space, minimum sizes, motion timings, or anything unusual.

## Pick the logo file

**Lockups:**
- **Stacked** is the lead lockup. Use it for square or tall spaces: covers, social posts and avatars, title slides, splash screens, certificates and posters.
- **Horizontal** has equal standing. Use it for wide, short spaces: website headers, letterheads, document headers, contracts, invoices, email signatures, slide footers.
- **Symbol alone**: app icons, favicons, avatars, small corner marks, or where the full logo already appears nearby.

**Colour version, by background:**
- `full-colour` on white, Mist or light photos.
- `on-dark` on navy or dark photos, including a navy band or area of your own layout.
- `navy-bg` only for a standalone logo image that must carry its own navy box: a profile picture, or a logo file sent to a partner. Inside a layout that already has navy, use `on-dark`.
- `mono-navy` for single-ink printing: stamps, embossing, fax, engraving.
- `mono-white` reversed out of a dark ground, in one colour.
- When an image has both grounds (say, a navy band over a Mist band), the version follows the ground the logo sits on.

**Format:**
- **SVG** for HTML, artifacts and web, inlined or embedded.
- **PNG** for .docx, .pptx and image composites.

**Placement:**
- Arabic documents read right to left, so the logo sits at the **top-right** (the start side).
- Keep clear space around the logo: at least the width of the amber diamond on every side. The SVG and PNG files already include this padding inside their box. To line the visible logo up with a margin, offset the box by its padding (about 12% of the logo's height). Don't add more space than that.
- Don't go below the minimum sizes:
  - stacked: 72 px or 20 mm tall
  - horizontal: 120 px or 35 mm wide
  - symbol: 16 px or 6 mm

## Colour

| Token | HEX | Use |
|---|---|---|
| Navy | `#0B1F3A` | The main colour: headings, body text on light, dark backgrounds, table headers |
| Teal | `#007C91` | Accents: links, rules, buttons, highlights, WAQQAD on light (4.9:1 on white) |
| Amber | `#F2A93B` | **Only the spark in the logo.** Never use it for text, buttons, backgrounds or charts |
| Mist | `#F3F5F8` | Page and section backgrounds, cards, table stripes |
| White | `#FFFFFF` | Grounds, and text on navy |
| Pale core | `#FFE3A8` | Inside the animated flame only |

Contrast rules:
- Teal text works on white and Mist, but not on navy (about 3.3:1). On navy, use white text, and use teal only for fills, pills, rules and icons that sit behind white text.
- Navy on Mist and white on navy both pass easily.

Aim for proportions of roughly 60% white or Mist, 30% navy and 10% teal. In a single social image, a navy band with a Mist band counts. Amber appears only inside the logo, which is why it reads as the spark. When data needs more colours, use tints of navy and teal, not new hues.

## Typography

- **IBM Plex Sans Arabic** for Arabic text: headings 600, body 400.
- **IBM Plex Sans** for Latin text, at the same weights.
- Both are free on Google Fonts. In web work, load them with the `@import` in `references/tokens.css`.
- **Reem Kufi** appears only inside the logo files. Never type the name in it, and never type وقّاد as a substitute for the logo. Place the file.
- In .docx and .pptx, set the font names to "IBM Plex Sans Arabic" and "IBM Plex Sans", and set `rtl`/`bidi` for Arabic paragraphs. If the reader may not have the fonts installed, tell the user to install them from Google Fonts, or embed them where the format allows.
- Arabic is the primary language. Set Arabic text right-aligned, with the page direction RTL.
- Numerals: use Arabic-Indic numerals (٢٣) in Arabic copy unless the user writes Western ones; follow the user. Set URLs, emails and phone numbers in IBM Plex Sans, left to right (`dir="ltr"` on that span).

## Doing the work, by output

**HTML pages and artifacts:**
1. Paste `references/tokens.css`.
2. Inline the SVG for the logo you picked: read the file and paste its `<svg>`.
3. Use `dir="rtl"` and `lang="ar"` for Arabic pages.
4. For the hover effect, inline `assets/motion/waqqad-symbol-live.svg`, include the CSS and JS from `assets/motion/`, and call `WaqqadSymbol.bind(element)`.
5. For a loader, use `waqqad-symbol-loop.svg`, which plays on its own even as an `<img>`.
6. For a page-load intro, call `WaqqadSymbol.entrance(svg)`.

**Word documents** (proposals, contracts, letters, invoices):
1. Put the horizontal `full-colour` PNG in the header at the top-right, about 35–45 mm wide.
2. Make headings navy, Plex Sans Arabic 600, and use teal for rules and table header accents.
3. Use Mist for table stripes.
4. Optionally, put the symbol PNG small in the footer.

**Slides:**
- Title slide: a navy background with the stacked `on-dark` PNG.
- Content slides: a white background, navy headings, and the horizontal logo small in a corner (top-right for Arabic decks).
- Section dividers: navy or Mist backgrounds.

**PDF**: build it as HTML with the rules above, then print it.

**Social posts and images**:
- Compose at the platform size, 1080×1080 or 1080×1350, with margins of about 8–9% (around 96 px).
- Use a navy or Mist ground, or a navy band over a Mist band.
- Put the stacked logo at the top-right, about 20–25% of the canvas height. On small images, use the symbol instead.
- Order the content: the headline (Plex Sans Arabic 600) in the upper part, the details (date, time, place) below it, and the call to action or URL at the bottom.
- Leave generous space. One message per image.

**Avatars and icons**: use `assets/icons/waqqad-app-icon-1024.png`, the navy tile with the symbol.

**Video**:
- Open with the Ignite intro: `assets/motion/waqqad-symbol-intro-navy.svg`. The repository also has a 1080p MP4 at `brand/waqqad-logo/motion/video/`.
- Use navy grounds and white type.

## Never

These rules keep the identity recognisable and protect its credibility with boards and procurement officers:

- Don't stretch, squash, rotate or recolour the logo.
- Don't rearrange its parts. The symbol always sits at the start, on the right of the name.
- Don't show the flame in print or still images. The flame belongs to motion.
- Don't use amber outside the logo, or add shadows, outlines, glows or gradients to the logo.
- Don't put the logo on amber, on busy patterns, or on photos where it loses contrast.
- Don't use the old identity: the blue flame, the purple calligraphic flame, or Janna LT. If an old template shows them, replace them.
- Don't place a diamond on the ق as a shadda. That idea was retired. The logo files have the correct real shadda.

## Before you deliver, check

1. The logo comes from `assets/`, in the right lockup and version for the background.
2. The logo sits at the top-right in Arabic layouts and has its clear space.
3. Colours are only navy, teal, Mist and white, with amber only inside the logo.
4. Text is IBM Plex Sans Arabic / IBM Plex Sans, and Arabic text is RTL.
5. Nothing shows the old flame logo or the old fonts.
