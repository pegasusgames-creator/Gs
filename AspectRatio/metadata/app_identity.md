# Aspect Ratio Calculator Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: calculator (ratios and sizes) — Google TOOLS, Apple UTILITIES
- **Layout archetype**: I (toolbox / direct tool) — opens straight on the calculator, no menu, three tabs: Resize · Convert · Saved (+ pushed Batch list for Pro)
- **Mascot pattern**: M0 (no mascot — the numbers carry the personality; identity element = a landscape frame crossed by a dashed portrait crop)
- **Voice**: V8 (direct minimal) — "Keep the shape, change the size", "Exact: 1920 × 1080 is exactly 16:9."; no coaching, no guilt
- **Texture**: T2 (soft glassmorphism, kept flat) — pale cards on a blush ground, a graph-paper preview frame, tabular numerals
- **Mood string**: tool-clean

Blush Daylight (`#F7F0EE`, deep-teal accent `#1B6B73`) with a free teal-black Dark; Ocean free, Ember / Violet / Rose / Forest
are Pro accents (24-hour rewarded trial). Deliberately far from Age Calculator's caramel-cream, HabitTracker's lavender
and the portfolio's blue/green calculator family.

## What the app does (and the rules it states)
- Resize: width and height with the ratio, the width or the height locked; live preview frame; the reduced ratio (GCD);
  presets for social / video / print (+ your own); largest centered crop at six ratios; swap; copyable results.
- Rounding is stated on screen: derived pixel sizes are rounded half up to whole pixels (1000 px at 16:9 = 562.5 -> 563) and
  the exact value is shown; crops round DOWN so they never exceed the image. 1..100,000 px per side.
- Convert: px / in / cm / mm at any DPI 1..2400. 1 in = 2.54 cm = 25.4 mm exactly; inches shown to 3 decimals, cm to 2,
  mm to 1, rounded half up; physical sizes become whole pixels first.
- Saved: own presets (3 free), batch list (Pro), history of the last 40 calculations with Clear + Undo.
- `scripts/check_aspectratio_math.py` runs the app's pure maths block (`@@ARMATH`) under node against an independent
  Python reference built on `fractions` (reduction, half-way roundings, lock modes, clamping, units, parsing, crops,
  batch, the preset table incl. A-/US paper sizes).

## Pro (pro_lifetime, $5.99) and Remove ads ($2.99)
Pro: unlimited saved presets (free: 3), batch list, extra accents, no ads. Both purchases non-consumable.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] Not a symmetric centred column: preview card, field grid, chip grid, list groups
- [x] Own SVG icon set and illustrations (frame, ruler, bookmark, crop)
- [x] Mixed case body copy; caps only on section labels
- [x] No currency, no levels, no streaks, no guilt notifications
- [x] Opening line is the tool itself, not "Welcome to Aspect Ratio Calculator"
