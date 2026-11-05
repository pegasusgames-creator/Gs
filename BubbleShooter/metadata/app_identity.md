# Bubble Shooter Identity

Shipping name **Bubble Shooter** (store title "Bubble Shooter: Pop & Rescue").
Analog: the category-leading bubble shooters — matched on feel (drag-to-aim
dotted trajectory with a wall bounce, a ghost bubble at the landing cell,
snap-to-grid, 3-match pops, unsupported clusters falling, combos, a free
colour swap, shot-limited goal levels with stars, boosters, continues),
with ORIGINAL art and names: the critters are "Pips" — round, eared,
blinking little creatures in glass bubbles; no witches, owls or licensed
characters, and no look-alike trade dress.

- Category: casual (arcade aim-and-match)
- Layout: F (direct-to-game — the hero CTA resumes the next level; the board fills the screen with a five-tool bottom bar)
- Mascot: M1 (anthropomorphized game element — the Pips blink and bob inside their glass bubbles and float away with a heart when freed)
- Voice: V6 (enthusiastic arcade) — "Combo ×3!", "Nice drop!", "Avalanche!", "Bubbly brilliant!"
- Texture: T2 (soft glass — glossy radial-lit bubbles, glass Pip pods, a clear rounded board panel over a faint fizz motif)
- Mood string: lime-soda fizz

Lime-soda paper with a cobalt straw. Daylight `#e9f4cc` key-lime ground,
`#fbfdf3` surfaces, `#1c2710` olive-ink text, cobalt accent `#1f5bc4`
and a tangerine "hot" colour for danger and combos — a family no sibling
uses (WaterSort ocean blue, Nonogram cream/coral, 2048 sand/gold, Unblock
mint, PipeConnect sky, Afterimage blueprint, Minesweeper khaki/petrol,
Block Puzzle rose, Sudoku lilac, Sokoban clay, Solitaire felt green).
Midnight (800 coins) is a night garden: deep green-black `#0f1a13` with
bright glowing bubbles. Seven board themes recolour all six bubble
colours, the board panel, its rim and the aim line: Lime Soda, Lagoon,
Orchard, Midnight, Candy, Dusk, Ember. A Settings toggle adds a symbol to
every colour (● ▲ ■ ◆ ★ ♥) for colour-blind players.

Content: 500 levels mined by `test/gen_levels.py` (11 symmetric shape
families × clustered colouring) and verified by
`scripts/check_bubbleshooter_levels.py` — a greedy bot that aims at every
reachable landing cell (straight or off either wall) for the current and
next bubble clears each level's goal within its bubble limit in a majority
of 5 seeded colour queues (19+ of 20 for levels 1–20), and the queue the
first attempt deals is one of the bot's wins. Goals: clear the board (252),
free the Pips (149), reach a score (99). Colours ramp 3 → 6, rows 3 → 10.
Daily = a campaign board picked by weekday band (Mon gentle → Sun tough),
mirrored and recoloured, with its verified queue. Endless = survival with
a new row every five misses.

Anti-patterns check: board-first canvas with a tool bar (Menu · Fireball ·
Bomb · Rainbow · Restart), not a button stack; the celebration is the
remaining bubbles raining off the board plus a bubbles-left bonus, not a
generic "Level Complete!"; losing is "Out of bubbles!" with keep-your-board
continues; Settings has game-specific Vibration and Colour-symbol rows.

## Menu-must-pass checklist (skin v2 — see CLAUDE.md)
- [x] Icon tiles filled & brand-tinted with depth (never outline-on-white)
- [x] Motif felt (~14%) and masked out of the center; no dead mid-section
- [x] Emblem reads the core mechanic in one glance (a launcher, a dotted bank shot, a hanging cluster about to pop)
- [x] Hero CTA dominates (cobalt gradient + glyph + shine); one line at 330–360 px
- [x] Wordmark gradient clean (2 cobalt stops, ≥4.5:1 on both grounds)
- [x] Family layout, own world (lime soda) and accent (cobalt + tangerine)
- [x] Daylight + Midnight + 5 board themes correct; `prefers-reduced-motion` respected

## Phase 8 self-check

1. Side-by-side vs shipped apps: different product (aim-and-shoot canvas, lime/cobalt palette, glossy bubbles).
2. Voice: arcade call-outs on combos and big drops.
3. Identity element: the Pips in their glass bubbles + the dotted bank-shot line.
4. Anonymous screenshot: a hex board of glossy bubbles with a dotted aim line and a launcher — instantly this app.
