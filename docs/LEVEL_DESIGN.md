# Level Design — Solvability Guarantee

Every puzzle app in the Pegasus Games portfolio MUST guarantee that all
generated levels are solvable. Unsolvable levels in production lead
directly to 1-star reviews, refund requests, and the kind of negative
signal that hurts ranking and Play Store discoverability.

This document is the canonical reference for how to build level
generators correctly and how to verify them before shipping.

---

## The mistake to avoid

**Pure random shuffle does NOT produce solvable puzzles.**

Concrete example from this repo: the v1.6.2 WaterSortPuzzle generator used
Fisher-Yates shuffle to distribute balls across tubes. A BFS solver run
against the resulting 500 levels found **295 unsolvable levels (59%)** —
mostly in the 1-empty-tube difficulty bands. Players reaching level ~71
hit a wall of unwinnable puzzles.

Random shuffles fall apart when:

- The puzzle has tight constraints (few empty slots, many colors/pieces)
- The state space has dead-end attractors (configurations from which
  the goal is provably unreachable)
- There is no oracle telling you when a generated instance is bad

This is true for ball-sort, sokoban-style pushers, sliding-tile,
unblock, jigsaw, and most "rearrange to a target" puzzles.

---

## The pattern that works: reverse-construction from solved state

Start from the solved goal state. Apply random "anti-moves" — the exact
inverses of valid forward moves. After N anti-moves, you have a state
from which the chain of anti-moves played in reverse is a guaranteed
winning sequence of valid forward moves.

Three properties to enforce:

1. **Each anti-move must be the inverse of a legal forward move.**
   If forward play has rules ("can only pour onto same-color top"),
   then your anti-move must move pieces FROM a position the forward
   move would have created. For ball-sort:
   - DST = the tube that received balls in the forward move (must
     have ≥1 ball of some color on top)
   - SRC = the tube that lost balls (must be empty OR top match the
     color being moved back, so the forward replay lands legally)

2. **Scramble enough to be non-trivial.** A small number of anti-moves
   can wander back to (or close to) the solved state. After scrambling,
   if `isSolvedState(tubes)` returns true, scramble more. WaterSortPuzzle
   uses `max(80, 60 * numColors)` initial anti-moves and re-rolls in
   batches of 40 if still solved.

3. **Verify with an actual solver before shipping.** Generate, run a
   BFS/DFS solver, fail the build if any level is unsolvable. This is
   the SHIP_GAME.md Phase 5 check that should not be skipped for any
   app with procedurally-generated levels.

---

## Reference implementation: WaterSortPuzzle

See `WaterSortPuzzle/android/app/src/main/assets/game.html` line ~494,
`generateLevel(numTubes, numColors, seed)`. It implements:

- Solved-state initialization (each color in its own full tube)
- Anti-move scrambling with run-length-aware multi-ball moves
- Post-check that re-scrambles if the state collapsed back to solved

The same structure can be adapted to any pour/sort/swap puzzle.

---

## Verification: required Phase 5 step

For any app with a procedural level generator, run a solver against
the FULL level set before each release build. This catches regressions
from level-generator changes and seeds that sneak through.

Reference solver template: `verify_watersort_levels.py` at repo root.
It implements a generic ball-sort BFS solver with state canonicalization
(sorted tube tuples) — fast enough for 500-level sets.

For non-ball-sort puzzle types, copy the structure:
1. Replicate the JS RNG + generator in Python (LCG state must match
   bit-for-bit so generated levels are identical between JS and the
   verifier).
2. Implement an `is_won(state)` predicate matching the JS win condition.
3. Implement a `legal_moves(state)` generator matching the JS move rules.
4. Run BFS with `canon(state)` for hashing (collapse symmetries).
5. Fail the build on any unsolvable or timeout level.

---

## Per-puzzle-type guidance

| Puzzle type | Anti-move definition | Notes |
|---|---|---|
| Ball sort / Water sort | Take top-stack of color C from a tube; place on a tube that is empty OR top-color C. | Verified pattern in WaterSortPuzzle. |
| Sliding tile (15-puzzle) | Slide the empty cell in the inverse direction of the forward move. | Solvability also depends on board parity; pure random shuffle gives ~50% unsolvable. |
| Unblock me | Move a block backward along its constrained axis. | Forward rules only allow horizontal-or-vertical-along-axis; same constraint applies in reverse. |
| Sokoban-style | Pull the box backward (and step into its previous cell). | Note: forward play PUSHES, reverse must PULL — implement explicitly. |
| Pipe connect / flow | Build the solved network first, then disconnect at random; player reconnects. | Simpler than anti-moves: deconstruct the goal. |
| Nonogram | Generate the solution image first, derive the row/column clues from it. | Clues are deterministic from the solution; solvability is automatic. |
| 2048-style merging | Not applicable — 2048 generates tiles in real time, not pre-built levels. | Difficulty comes from runtime tile spawning. |
| Trivia / quiz | Not applicable — solvability is per-question; ensure each Q has exactly one declared correct answer. | Verify with a script that asserts `correct_index in range(len(options))`. |

---

## How to know if your generator is broken before users do

Add this to your release checklist (`SHIP_GAME.md` Phase 5):

```
[ ] Run the per-app level-solvability verifier
[ ] Confirm 0 unsolvable, 0 trivial-already-won levels
[ ] If any failures: do NOT ship; fix the generator first
```

Skipping this check is the same risk class as skipping
`pre_publish_check.py`. The build artifact looks fine, but the user
experience is broken in a way the build pipeline can't see.
