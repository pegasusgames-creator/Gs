# Block Puzzle Identity

- Category: puzzle (score chase / block placement, 8×8)
- Layout: A (family shell: hero Play CTA, daily pill, icon grid)
- Mascot: M0 (no mascot; the glossy glazed tiles carry the personality)
- Voice: V6 (enthusiastic arcade): "NICE!" → "GREAT!" → "AMAZING!" → "UNREAL!" → "LEGENDARY!", "BOOM!", "REVIVED!"
- Texture: T4 (material: glossy ceramic glaze tiles on a glazed tray)
- Mood string: rose-glaze arcade

A ceramic studio where every drop is a glazed tile settling into a blush
tray. Daylight "Rose Glaze" is a pale rose board with a raspberry accent;
Midnight Glaze is the coin-bought dark look. Seven tile colours (cobalt,
jade, vermilion, amber, violet, teal, lime) stay readable on every theme;
themes re-glaze the tray and all seven tiles (Celadon, Delft Blue,
Majolica, Raku, Stoneware, Midnight Glaze).

Core loop: three-piece tray, drag with a ghost lifted above the finger,
full rows and columns clear together, combo multiplier ×1…×8 with a
3-move grace, Spotless bonus for an empty board, per-run goal ladder
(100 → 2000) that awards 1-3 stars. The dealer is adaptive (small pieces
when crowded, big pieces as the score climbs) and fair: it never deals a
tray with nothing placeable while any shape still fits — gated by
`scripts/check_blockpuzzle_fair.py` (500 seeded greedy-bot runs + 366
daily seeds replayed for determinism, plus 50 JS golden traces).

Fail state: "No room!" card — one free video revive per run (empties the
densest 4×4, deals a fresh tray) and up to two heart revives. Boosters:
💣 Bomb (main, `hintCount`; 3×3 blast, solver marks the strongest spot),
↻ Rotate (tap pieces to turn them until the tray is used), ⟳ Refresh
(new tray dealt to fit). Daily = date-seeded piece sequence shared by all
players, weekday target 700 (Mon) → 1500 (Sun), streak.

Distinct from siblings: Puzzle2048 (number merge on a sand board),
Sokoban (pushing crates in a clay warehouse), FlappyWings (one-tap
flyer, peach sky). No sibling uses a rose/raspberry family. No
third-party marks or look-alike trade dress (deliberately unlike the
dark-blue leaders of the genre).

## Menu-must-pass checklist (skin v2 — see CLAUDE.md)
- [x] Icon tiles filled & brand-tinted with depth (never outline-on-white)
- [x] Motif felt (~14% berry ink: L, T, square, bar outlines) and masked out of the center
- [x] Emblem reads the core mechanic in one glance (a domino dropping into the last gap of a row)
- [x] Hero CTA dominates (raspberry gradient + depth + glyph + shine)
- [x] Wordmark gradient clean (2 stops #7d1f47 → #a82a5c, ≥4.5:1)
- [x] Family-consistent yet distinct vs every sibling
- [x] Light + midnight correct; reduced-motion respected; no competing shim
