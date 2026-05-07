# Pegasus Games — Portfolio Competitive Audit

Audit date: 2026-05-04. Five flagship apps audited against the
inline §1–§8 competitive benchmark. Per-app reports live at
`<App>/COMPETITIVE_AUDIT.md`. This document summarizes findings and
ranks fix effort.

## Cross-portfolio findings (patterns that recur)

These appeared in 3+ of the 5 audits — fixing them once at the
template level pays for itself across the portfolio.

| Pattern | Affected | Fix |
|---|---|---|
| **Headline subtitle clipping** ("iving controls" / "rom easy 4-tube" / "[…]al tiles combine") | WaterSort 02 + 06, PipeConnect 02, Puzzle2048 02 | Bug in the screenshot-headline overlay generator — text is being clipped mid-word at both ends. Fix in `scripts/wrap_screenshots.py` or whichever generator produces the framed PNGs. One fix, four apps healed. |
| **Generic preamble openings** (encyclopedia / mechanic / clichéd) | WaterSort, Nonogram, UnblockPuzzle, PipeConnect, Puzzle2048 | All five lead with category description, mechanic restatement, or "ultimate / impossible to put down" cliché instead of a sensory hook. Treat the leader-format rewrite as the standard pattern for new apps; backfill the 5 here. |
| **Missing keywords** (relaxing / satisfying / ASMR / offline / brain / free) | All 5 to varying degrees | Most-missing terms across portfolio: `ASMR` (5/5 missing), `brain` (4/5), `relaxing` (3/5), `free` (4/5). All are honest claims for these mechanics but require §6 ASMR threshold (2/3) to be hit before claiming `ASMR`. |
| **No haptic feedback** | Nonogram, PipeConnect, Puzzle2048, UnblockPuzzle (4 of 5) | Only WaterSort has `navigator.vibrate` calls. Adding 6–10 LOC of `vibrate(8)` on key interaction + `vibrate([20,40,20])` on win to each game lifts the §6 ASMR score and unlocks `ASMR` keyword honestly. ~30 min per app. |
| **Generic booster names** (Hint / Undo / Reset / Skip) | All 5 | None of the audited apps use thematic booster names. Each per-app audit proposes 3 named replacements specific to its mechanic — collectively 15 booster renames, ~3–5 hours total. |
| **Theme-unlock progress invisible on menu** | WaterSort, Nonogram, PipeConnect, Puzzle2048 | All four have a theme/palette unlock ladder driving the meta-loop, but none show "next theme unlocks at level X" on the home menu. The loop is present but not *felt*. Single shared HUD component would fix all four. |
| **Theme/screen meta-loop NOT mentioned in store listing** | All 5 | Every app has a stronger meta-loop in code than the listing communicates. Marketing copy under-sells the existing product. |
| **Flat-SVG icons** | Nonogram, PipeConnect, Puzzle2048, UnblockPuzzle (4 of 5) | Only WaterSort has illustrated 2D depth; the other four are flat geometric. Severity varies: Nonogram's flat-SVG is on-brand (warm-paper aesthetic), Puzzle2048's flat-SVG is actively damaging (indistinguishable from 30+ canonical 2048 clones). |
| **`playError` dead code** | PipeConnect (confirmed); audit other apps | PipeConnect has `playError` defined with zero callers. Worth a portfolio-wide grep — dead audio code across apps suggests a shared template seed that wasn't fully wired. |

## Per-app verdict roll-up

| App | Most important issue | BLOCKERs | Effort to flagship |
|---|---|---|---|
| **WaterSort** | Screenshots 04 & 05 have headlines that contradict the screen pictured (mismatched subjects) | 3 | ~7 h base + 14 h optional |
| **Nonogram** | Opening line is an encyclopedia entry ("A nonogram is a logic grid"); screenshot 03 modal sits on a darkened/blurred board (SHIP_GAME §3.1.3 anti-pattern) | 2 | ~5.5 h base + ~9 h optional (Picture Gallery) |
| **PipeConnect** | 157-byte full_description (substantively empty) + only 1 of the required 2–8 phone screenshots published | 3 | ~11–14 h |
| **Puzzle2048** | Icon is canonical 2/4/8/2048 layout in cream/tan/orange/yellow on black — visually identical to 30+ Play Store clones; will not differentiate at thumbnail | 4 | ~13 h |
| **UnblockPuzzle** | Screenshot 06 headline says "500+ JAMS" but `LEVELS.length` = 150 (verifiable content lie, Play Store Misleading Behavior policy risk) | 1 | ~2 h |

## Ranked fix effort (cheapest → most expensive)

### 1. UnblockPuzzle — ~2 hours
Closest to flagship-ready. One BLOCKER (the "500+ JAMS" honesty fail)
is a 30-minute headline/screenshot fix. Polish is mostly copy work
plus 5 minutes of `navigator.vibrate` to lock 3/3 ASMR. The strong
6-tier theme meta-loop is already shipped; the listing just doesn't
mention it.

### 2. Nonogram — ~5.5 hours base
Two BLOCKERs are quick: rewrite the opening line (~15 min) and re-shoot
screenshot 03 with a clean board behind the modal instead of blurred
(~30 min). Polish covers booster renames (Magnifying Glass / Smart
Mark / Eraser), keyword inserts, and adding `navigator.vibrate`. The
big optional add is a Picture Gallery meta-loop (~1 day) — the single
highest-impact distinctive feature you could add to a nonogram in
this portfolio (cf. Hungry Cat Picross). Defer for now; ship without
and pick up in a v1.1.

### 3. WaterSort — ~7 hours base, ~21 hours full-flagship
Hero app. BLOCKERs are concentrated in the screenshot pipeline —
re-capture slots 04 and 05 from the actual Daily Missions screen and
a multi-day streak overlay, fix the headline-overlay generator that's
clipping subheads on 02 and 06. Listing copy is closer to ready than
the other four (already has `relaxing`, `satisfying`, `offline`).
Optional 14h is the icon regeneration to 3D-rendered glass-flask
scene + season-pass UI inside the game; both are appropriate Hero-app
DEFERs once base ships.

### 4. PipeConnect — ~11–14 hours
Largest delta from current state. Both BLOCKERs are content-floor
problems — 157-byte description and 1-of-7 screenshots — so most of
the effort is producing missing assets, not rewriting existing ones.
Capture 6 fresh emulator screenshots, write a 600-char description
from scratch, optionally regenerate the icon to isometric-3D pipes.
Code touches are small (haptic + canvas pulse + booster renames +
stronger hint algorithm).

### 5. Puzzle2048 — ~13 hours
Highest-risk app. Four BLOCKERs because the 2048 genre is brutally
crowded — listing/screenshot/icon all need to differentiate or the
app will not surface in search. Effort split: ~5 h asset (icon
regeneration is non-negotiable; recommend cool-teal/violet 3D hero
tile mid-merge to break from canonical Cirulli palette), ~6 h code
(haptics + 3 named boosters + particle/shake on big merges + theme
unlock progress on menu), ~2 h copy (full description rewrite). Even
with all this, expect harder organic ranking than the other four
because of genre saturation.

## Recommended sequencing

If shipping at 2 apps/week per CLAUDE.md cadence, suggested order:

1. **Week 1:** UnblockPuzzle (2 h) + Nonogram (5.5 h) — both close to
   ready, low risk, opens the portfolio with two genuinely-distinct
   logic puzzles
2. **Week 2:** WaterSort base fixes (7 h, ship base) + PipeConnect
   (11–14 h) — start the WaterSort 3D icon work in parallel as a
   week-3 polish pass
3. **Week 3:** Puzzle2048 (13 h) — slot last because the icon
   regeneration is on the critical path and the genre saturation
   means it's the most-likely-to-flop release; better to ship after
   the other four have data

## Portfolio-wide actions before any of the 5 ship

These are template-level fixes that avoid repeating the same defect
across remaining ~190 apps:

1. **Fix the headline-overlay generator** (`scripts/wrap_screenshots.py`)
   — both-ends clipping on subtitles is hitting at least 4 of 5 apps
2. **Add a "Next theme unlocks at level X" HUD** to the shared menu
   pattern — affects 4 of 5 audited and will affect every future app
3. **Standardize a `vibrate()` call site** in the shared SFX layer of
   `_template/game.html` so new apps get haptic by default
4. **Add a leader-format-opening bullet** to `QUALITY_PLAYBOOK.md`
   §store-listings — every audited app failed §1 the same way
5. **Run a portfolio-wide grep for `playError` and other dead audio
   functions** seeded from the template — prune or wire them
