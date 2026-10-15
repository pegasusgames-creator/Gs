# Sudoku Identity

Shipping name **Sudoku** (store title "Sudoku: Logic Number Puzzle").
Analog: the category-leading classic Sudoku apps — matched on feel (big
readable grid, notes, remaining counts, mistakes limit, daily puzzle),
differentiated by technique-graded difficulty and hints that teach.

- Category: puzzle (logic / number placement)
- Layout: G (daily-puzzle-led — Daily puzzle tier + streak under the hero CTA)
- Mascot: M0 (no mascot — minimalist genre; the grid is the character)
- Voice: V8 (direct / minimal) — "Nine digits. One right answer."
- Texture: T3 (subtle paper grain under the board, notebook ruling in the menu motif)
- Mood string: ink-lilac

Indigo ink on lilac notebook paper. Daylight `#ebe8f7` paper, `#fbfaff`
surfaces, `#1d1a45` ink text and an indigo accent `#4f46c8` — a family no
sibling uses (WaterSort ocean blue, Nonogram cream/coral, 2048 sand/gold,
Unblock mint, PipeConnect sky, Afterimage blueprint cyan, Hunch sage,
Overlay pink-grey). Midnight (800 coins) is a deep ink-blue desk
`#141530`. Seven board themes recolour every board role (cells, box lines,
givens, entries, notes, highlights, conflicts): Ink, Pencil, Matcha,
Midnight, Coral, Ocean, Espresso.

Content: 500 puzzles mined by `test/gen_levels.py` and verified by
`scripts/check_sudoku_unique.py` — exactly one solution each, graded by a
technique solver into Easy (singles) / Medium (pointing, claiming, pairs) /
Hard (triples, quads, X-Wing) / Expert (XY-Wing, XYZ-Wing, Swordfish).
Daily (Mon Easy → Sun Expert) and Endless draw from a 120-puzzle pool
through a seeded relabel + row/column shuffle that keeps uniqueness and
grade. Hints fill a correct cell and name the technique that finds it.

Anti-patterns check: board-first game screen with a 9-key pad and tool row
(not a generic button stack); celebration is a unit-completion ripple
across the finished row/column/box, not a generic star burst; no
templated currency framing (lives are "second chances" after 3 mistakes).

## Menu-must-pass checklist (skin v2 — see CLAUDE.md)
- [x] Icon tiles filled & brand-tinted with depth (never outline-on-white)
- [x] Motif felt (~12-16%) and masked out of the center; no dead mid-section
- [x] Emblem reads the core mechanic in one glance (3×3 box mid-solve)
- [x] Hero CTA dominates (gradient + depth + glyph + shine)
- [x] Wordmark gradient clean (2 stops indigo ink, ≥4.5:1)
- [x] Family-consistent yet distinct vs every sibling
- [x] Light + midnight correct; reduced-motion respected; no competing shim
