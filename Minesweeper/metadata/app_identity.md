# Minesweeper Identity

Shipping name **Minesweeper** (store title "Minesweeper: No-Guess Logic").
Analog: the category-leading classic mine-hunting apps — matched on feel
(first tap always opens an area, long-press flag, chording, flag counter,
timer, zoom/pan on big fields, daily board), differentiated by a
no-guess campaign that is verified by a logic solver and hints that show
the numbers that prove each move.

- Category: puzzle (logic / deduction)
- Layout: F (direct-to-game — the hero CTA resumes the next field; the board fills the screen with a four-tool bottom bar)
- Mascot: M0 (no mascot — the minefield is the character)
- Voice: V2 (encouraging coach) — "Tap the ✕ — it is always safe", "Mine marked — carry on", hints that explain *why* a tile is safe
- Texture: T3 (survey-map paper: grain + topographic contour motif behind the menu, raised tiles on a pale field)
- Mood string: survey-map field

Petrol teal tiles on survey-map paper. Daylight `#e6e9d2` khaki-olive
ground, `#f8f9ee` surfaces, `#1d2619` ink text, petrol accent `#1f6f69`
and signal-red flags `#e0482a` — a family no sibling uses (WaterSort
ocean blue, Nonogram cream/coral, 2048 sand/gold, Unblock mint,
PipeConnect sky, Afterimage blueprint cyan, Hunch sage, Overlay
pink-grey, Sudoku lilac/indigo, Sokoban clay). Midnight (800 coins) is a
night survey: deep slate `#10181b` with lit teal tiles. Seven board themes
recolour every board role (covered tiles + bevels, open ground, grid lines,
flags, mines, number colours 1–8): Survey, Canyon, Glacier, Midnight,
Orchid, Harvest, Ember. Number colours pass 4.5:1 on the open ground and
digits 1–5 stay separable under protan/deutan/tritan simulation
(`test/check_colors.py`).

Content: 500 boards mined by `test/gen_levels.py` and verified by
`scripts/check_minesweeper_noguess.py` — every board (and each of its four
rotations/mirrors used by Daily/Endless) is solvable without guessing from
its stored safe first tile, using single-number, pair-subset and
mine-count reasoning. Boards grow 6×6/5 mines → 30×16/104 mines (shown
portrait, 16 wide), with par times from the board's 3BV. Daily (Mon small
→ Sun expert) and Endless draw transformed campaign boards.

Anti-patterns check: board-first canvas game screen with a tool bar
(Menu · Flag mode · Hint · Restart), not a button stack; celebration is a
cascade ripple across the cleared field plus "Field cleared!", not a
generic "Level Complete!"; losing is "Boom. That was a mine." with keep-
your-field second chances; Settings has game-specific Vibration and Board
Theme rows.

## Menu-must-pass checklist (skin v2 — see CLAUDE.md)
- [x] Icon tiles filled & brand-tinted with depth (never outline-on-white)
- [x] Motif felt (~14%) and masked out of the center; no dead mid-section
- [x] Emblem reads the core mechanic in one glance (numbers, a ✕ start tile, a flag, covered tiles)
- [x] Hero CTA dominates (petrol gradient + glyph + shine); one line at 330–360 px
- [x] Wordmark gradient clean (2 petrol stops, ≥4.5:1 on both grounds)
- [x] Family layout, own world (survey map) and accent (petrol + signal red)
- [x] Daylight + Midnight + 5 board themes correct; `prefers-reduced-motion` respected

## Phase 8 self-check

1. Side-by-side vs shipped apps: different product (canvas minefield, khaki/petrol palette).
2. Voice: coach lines on the board explain the logic.
3. Identity element: the ✕-marked safe start tile + petrol raised tiles.
4. Anonymous screenshot: a minefield with numbers and flags — instantly this app.
