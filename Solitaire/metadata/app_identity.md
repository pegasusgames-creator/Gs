# Solitaire Identity

Shipping name **Solitaire** (store title "Solitaire: Klondike Card Game").
Analog: the category-leading classic Klondike apps. Matched on feel (tap to
move, drag and drop, free undo, auto-finish, daily deal, draw 1 / draw 3,
cascading win), differentiated by a numbered campaign where every deal is
verified winnable and a Hint that follows a real winning line.

- Category: card (classic patience / Klondike)
- Layout: D (vertical card feed: Continue, Daily Deal and the event card
  stack down the menu like dealt cards; no traditional hero art)
- Mascot: M0 (no mascot; the cards are the character)
- Voice: V5 (calm / zen): "Breathe, then build.", "Keep playing",
  "Same cards from the top."
- Texture: T4 (material: woven felt table with a fractal-noise weave under
  the cards, ivory card faces with a soft drop shadow)
- Mood string: sea-glass felt

Sea-glass teal felt under light linen chrome. Daylight `#e3f1ee` linen,
`#fafdfc` surfaces, `#10302c` ink text, deep-teal accent `#127a6f`, a teal
felt table (`#7fc2b6` → `#5aa597`) and brick-red card backs. No sibling uses
a teal card table (WaterSort ocean blue, Nonogram cream/coral, 2048 sand/gold,
Unblock mint, PipeConnect sky, Afterimage blueprint cyan, Hunch sage, Overlay
pink-grey, Sudoku lilac, Sokoban clay). Midnight (800 coins) is a deep
night-teal table `#0d1f1d`. Seven table themes recolour the felt, the
card-back weave, its trim and the empty-pile outlines: Sea Glass, Clubhouse
Baize, Harbor, Midnight, Desert Sand, Velvet, Graphite. Card faces stay ivory
in every theme so ranks always read.

Content: 500 numbered draw-1 deals + a 364-day Daily Deal pool, mined by
`test/gen_levels.js` (seeded deal, solver, greedy no-peek playouts to grade),
built by `test/build_levels.js`, gated by
`scripts/check_solitaire_winnable.py` (re-deal each seed bit-exactly and
replay its stored winning line to four complete foundations). Campaign runs
quick openers → long games; the Daily Deal is easy Mon/Tue, medium Wed–Fri,
hard Sat/Sun. Random deals (draw 1 or draw 3) use a life; numbered deals and
the Daily Deal are free. Hint = next move of the stored line, else a bounded
solver from the current position, else an honest "no sure win found" move.

Anti-patterns check: board-first table with tap-to-best-spot + drag, not a
button stack; celebration is the classic bouncing card cascade with trails,
not a generic star burst; app-specific copy ("Deal 12 won!", "Same cards from
the top", "Every card is face-up — finishing for you"); Settings adds
Solitaire-only rows (left-handed layout, four-colour suits, vibration).

## Menu-must-pass checklist (skin v2 — see CLAUDE.md)
- [x] Icon tiles filled & brand-tinted with depth (shared skin, teal tint)
- [x] Motif felt (~13-15%) and masked out of the center: card outlines + suits
- [x] Emblem reads the core mechanic in one glance (an Ace fanned over a red
      7 and a face-down card)
- [x] Hero CTA dominates (deep-teal gradient + spade glyph + shine)
- [x] Wordmark gradient 2 stops, deep teal, ≥4.5:1 on both themes
- [x] Family layout, own world (felt table, card motif, teal accent)
- [x] Daylight + Midnight + 5 table themes, prefers-reduced-motion respected

## Phase 8 self-check

1. Side-by-side vs siblings: the only card game in the family; teal felt and
   playing cards share nothing with the grid / tile siblings.
2. Voice: calm copy throughout the menu, sheets and tutorial.
3. Identity element: the fanned Ace emblem and the felt table.
4. Anonymous screenshot: a Klondike tableau on teal felt reads instantly.
