# Mahjong Solitaire — identity

- **Category**: board / tile-matching puzzle (Google GAME_BOARD)
- **Layout archetype**: A (hero Play over a calm button stack; the emblem carries the identity)
- **Mascot pattern**: M4 (spirit-of-the-app: a small tile stack with its matching free pair lit)
- **Voice**: V5 (calm / zen: "Serene clear", "Never truly stuck")
- **Texture**: T4 (wood / material: honey-teak table grain, ivory tiles with jade backs)
- **Mood string**: honey-teak tea table

## The game in one line
Classic mahjong solitaire (match two free identical tiles) tuned for readability and calm:
big original SVG tile faces, held tiles dimmed, free undo, solver-backed hints, a shuffle
that re-deals what is left so it stays clearable.

## What makes it distinct in the portfolio
- Mechanic: free-tile pair matching on stacked 3D layouts (no sibling stacks tiles).
- Palette: honey wood `#f0dfbd` + jade `#1f7a5c` (Solitaire is sea-glass teal felt, Sokoban clay,
  Puzzle2048 sand cream — none pairs warm honey wood with jade).
- Icon focal: three stacked ivory tiles on jade backs with a lit matching pair.
- Content: 500 reverse-dealt campaign deals (gate `scripts/check_mahjong_solvable.py` replays each),
  21 layout families (traditional Turtle + 20 originals), date-seeded daily, endless boards.

## Accessibility
High-contrast tiles (whiter faces, deeper inks, corner numbers), "Dim held tiles" toggle,
vibration toggle, tiles sized to the screen (about 40 px wide on a 360 px phone for the largest
boards, up to 96 px on tablets), `prefers-reduced-motion` respected.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] App-specific celebration copy ("Serene clear! Cleared in 1:42 (par 2:05), no shuffle")
- [x] Own tile art and suit colours; no Unicode mahjong glyphs (they tofu on many devices)
- [x] App-specific settings (high-contrast tiles, dim held tiles, vibration)
- [x] Footer tools with icon + label + booster badge, not generic pills
