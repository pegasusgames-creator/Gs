# Word Search — identity

- **Category**: word puzzle (Google GAME_WORD)
- **Layout archetype**: A (hero Play over a calm button stack; the emblem carries the identity)
- **Mascot pattern**: M4 (spirit-of-the-app: a small letter grid with two highlighter sweeps — WORD across, BIRD on the diagonal)
- **Voice**: V7 (educational warm: theme facts as hidden messages, "Bonus word RATTLE!", "The 6 leftover letters hide a message")
- **Texture**: T3 (subtle paper: warm puzzle-book paper with a fine dot grain, translucent highlighter capsules)
- **Mood string**: heather puzzle-book dusk

## The game in one line
The classic word search, tuned for calm and readability: big letters on a paper board, a
drag-to-select highlight that snaps to the 8 directions (or tap first + tap last), found words
crossed off below the grid, hints that flash a first letter, bonus words and hidden messages.

## What makes it distinct in the portfolio
- Mechanic: straight-line letter selection over a stored letter grid (no sibling selects lines of
  letters; WordScramble/WordGuess are not built yet).
- Palette: heather-lilac page `#efe6f0` + plum accent `#8b3f87` on warm paper `#fffcf8`
  (Sudoku is blue-lavender + indigo, BlockPuzzle rose-pink, Nonogram cream + coral).
- Icon focal: a 4×4 letter grid with two translucent highlighter capsules crossing.
- Content: 500 stored campaign grids mined by `test/gen_levels.py` from 60 curated, family-friendly
  theme lists; gate `scripts/check_wordsearch_valid.py` proves every listed word appears exactly
  once on a straight line, no blocklisted word reads in any of the 8 directions, and the grid size
  / word count / directions match the band. Daily and Endless grids are built on-device with the
  same rules (`test/verify_runtime_boards.js` re-checks 700 of them through the gate).

## Progression
- Chapters of 50 = grid sizes 6×6 → 15×15; 8 → 20 words.
- Directions: levels 1-15 across/down; 16-50 + down-right diagonal; 51-100 + up-right;
  101-150 + backwards (W, N); 151+ all eight.
- Every 10th level up to 350: hidden-message ending (leftover letters spell a line or a true fact).
- About one level in three hides an unlisted bonus word (+10 coins).
- Stars: 1 + beat par time + no hints. Par = words × (2 + 0.85 × size) s.
- Daily: Monday 8×8 → Sunday 14×14, bonus word every day. Endless: 10×10-13×13, one ❤ each.

## Accessibility
Letters sized to the board (about 22 px cells at 15×15 on a 360 px phone, up to 50 px on tablets),
tap-tap selection for players who cannot drag, "Hide found" to shorten long word lists, vibration
toggle, synthesized sounds behind the Sound toggle, `prefers-reduced-motion` respected.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] App-specific celebration copy ("All words found! 🔎", "Daily grid solved!", the revealed message)
- [x] Own emblem and icon art (letter grid + highlighter), no shared icon composition
- [x] App-specific settings (vibration) and footer tools (Hint with badge, Hide found, Restart)
- [x] Footer tools with icon + label + booster badge, not generic pills
- [x] Words are English; the listing says so in every locale
