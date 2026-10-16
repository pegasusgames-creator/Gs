# Sokoban Identity

- **Category**: puzzle (classic warehouse box-pushing)
- **Layout archetype**: A (hero Play + Daily + icon row — the family shell's menu)
- **Mascot pattern**: M1 (anthropomorphized game elements: the keeper's eyes follow each move; crates smile once docked)
- **Voice**: V3 (playful narrator: "Every crate tucked in — the foreman approves.")
- **Texture**: T4 (wood/material: brick walls, plank floor, braced wooden crates)
- **Mood string**: cozy clay warehouse

The app should feel like a tidy little warehouse at golden hour: warm
terracotta brick, honey-wood crates, teal docks. Tactile above all —
crates slide, thud and chime; a wedged crate shakes gently; undo is free.

## Palette
Daylight (default): clay `#f6e6da` background, terracotta accent `#b4532c`,
crates `#e0a052`, docks `#2a8a7d`, keeper `#3b6fb6`. No sibling uses a
clay/terracotta family (Nonogram cream, Puzzle2048 sand, UB mint,
PipeConnect sky, Afterimage blueprint). Midnight = warm charcoal (800-coin
unlock). Six more board themes recolour walls/floor/crates/docks/keeper.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- Not A+M0+V1+T1: varies mascot (M1), voice (V3) and texture (T4).
- Copy is hand-written for this game; no "Welcome to…" opener.
- Every listed feature exists in code (hints from stored solutions, deadlock
  warning, daily tiers, Endless generator, 7 themes, haptics toggle).
