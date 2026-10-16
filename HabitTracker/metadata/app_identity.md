# Habit Tracker Identity

Utility-track TEMPLATE (docs/UTILITY_SHELL.md) and a finished app in its own right.

- Category: tracker (daily habits) — Google PRODUCTIVITY, not a health app
- Layout: G (calendar / streak grid — the home is a 7-day strip + today's ring + checklist; no menu)
- Mascot: M4 (spirit-of-the-app abstract — the progress ring, check "pop" burst, all-done confetti)
- Voice: V2 (encouraging coach) — "Lovely work. See you tomorrow." / "A free day. Enjoy it."
- Texture: T1 (flat clean cards, soft shadows, rounded 18 px) — the shell's neutral finish
- Mood string: ring-violet

Porcelain-lavender Daylight (`#F5F3FA`, violet accent `#5B3FD1`); Dark ships free
(a tool, not a coin unlock); four more accents (Ocean free, Forest/Ember/Rose Pro,
24-h rewarded trial). Every habit carries its own colour from a 12-swatch set that
keeps a white glyph >= 3:1. Identity element: the check ring that fills and pops.
No mascot, no currency, no levels — calm, private, offline.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] Not centre-aligned everything — left-aligned rows, offset ring card
- [x] Own SVG icon set (35 habit glyphs drawn for this app)
- [x] Mixed case body copy; caps only on section labels
- [x] No currency
- [x] Varied shapes: ring buttons, pill nav, chip strip, heat-map cells
- [x] Not a symmetric column: week strip + ring card + list + collapsible "not today"
- [x] No generic "Level complete" — the summary card turns into "All done for today!"
- [x] Settings reorganised around a tool (data/export, reminders, purchases)
