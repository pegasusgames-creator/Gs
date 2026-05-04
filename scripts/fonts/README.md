# Vendored fonts

These TTFs are checked into the repo so `wrap_screenshots.py` and
`wrap_tablet_screenshots.py` produce identical output across machines.

- `Poppins-Bold.ttf` — used for headlines and footer
- `Poppins-Medium.ttf` — used for subtitles

Sourced from https://github.com/google/fonts/tree/main/ofl/poppins
(SIL Open Font License). Don't replace these silently — Poppins glyph
widths are the basis of `_wrap_to_width()`'s 92%-of-canvas threshold,
so swapping fonts will change which subtitles fit on one line.
