# Nonogram — Competitive Audit

> **STATUS: RESOLVED — 2026-05-12.** Implemented in the May 2026 audit
> pass: coin grants fixed (100/500), hint pack fixed (10), Season +
> Weekly Pass with full honored benefits, Reveal Cell / Reveal Row
> boosters, Free Coins / Continue / theme progress strip / theme-unlock
> card / 7-day login-streak ladder / weekly tournament / seasonal
> events / Settings Restore+Privacy links, new coin tiers, 13 locales
> translated, phone + tablet screenshots recaptured. Shipped as v1.1.0
> (pending Play App Signing setup + SKU creation). Kept for the record.


## §1 — Listing structure

Literal opening line of `metadata/en-US/full_description.txt`:

> "A nonogram is a logic grid. Each row and column has a list of
> numbers — the lengths of consecutive filled cells. Solve the logic
> and a small picture emerges. Also called picross, hanjie, or paint
> by numbers."

This is an **encyclopedia entry**, not a hook. It defines the genre
before promising the player anything they will *feel*. Picross /
Hanjie aliases belong further down for SEO, not in the lead. The
second paragraph ("This is the puzzle for the part of your day where
you want to think but not be timed") is closer to a leader and should
trade places.

Proposed leader-format rewrite:

```
Mark a row, count the column, and watch a tiny pixel-art picture
emerge from a grid of nothing — the puzzle for the part of your day
when you want to think, not race.

500 hand-made boards from a 5×5 morning warm-up to a 20×20 marathon.
No timer. No streak you can break by skipping a day. Just the slow
satisfaction of clue-driven logic.
```

(The genre aliases — picross, hanjie, paint by numbers — move to the
keyword-optimization paragraph further down.)

## §2 — Keywords

| Term | Status | Excerpt |
|---|---|---|
| `relaxing` | MISSING | — |
| `satisfying` | PRESENT | line 31: "Quiet, slow, satisfying" |
| `ASMR` | MISSING | — |
| `offline` | PRESENT | line 23: "Works fully offline" |
| `brain` | MISSING | — |
| `free` | MISSING | — |

**`relaxing` insertion** — replace line 22 ("Warm paper aesthetic — easy
on the eyes") with: "Warm paper aesthetic — relaxing on the eyes after
a long screen day". The product genuinely is calm-paced (no timer);
honest.

**`ASMR` insertion** — only honest if §6 hits 2/3. It does (sound +
animation), but barely. Add to a new bullet: "ASMR-tier feedback —
soft fill tones, gentle win arpeggio, ink-on-paper visuals". If you
add `navigator.vibrate(8)` per §6, this becomes safer to claim.

**`brain` insertion** — change line 9 ("ramping from 'I just learned
this' to 'this took me a week.'") to: "ramping from a brain-warmer 5×5
to a 20×20 you'll come back to for days". Genuinely a logic puzzle —
"brain" is honest.

**`free` insertion** — add a leading bullet under "✨ WHAT'S IN IT":
"• Free to play — every one of the 500 boards included, no paywall".
Verifiable from `iaps.json` (only Remove Ads, hint packs, lives —
levels are not gated).

## §3 — Meta-loop

Inventoried persistent progression in `game.html`:

- **Coins** (`state.coins`, line 1058) — per-level reward, not a loop
- **Level stars** (`state.levelStars`, line 1057) — per-level grade,
  hint usage gates 3-star (line 2191)
- **Completed levels** (`state.completedLevels`) — across all 4 grid
  sizes
- **Daily Challenge streak** (`state.dailyChallengeStreak`, line 1066) —
  +30 coins on streak day, daily-streak text on win overlay (line 734)
- **Themes screen** (`screen-themes` at line 875, `_THEMES_META` array
  at line 3477) — color-palette unlocks
- **Missions screen** (`screen-missions` at line 895)
- **Stats screen** (`Statistics` at line 667 with global rank, levels
  solved, total stars, coins, daily streak)
- `season_pass_monthly` IAP — wired but no in-game UI

**Meta-loop verdict: PRESENT but UNDERSPECIFIED for genre.** Themes +
missions + streak is the standard Pegasus four-layer stack. What's
missing — and what would make Nonogram distinctive — is a **Picture
Gallery**: every solved nonogram preserved as a thumbnail in a
scrollable gallery the player can revisit. This is the meta-loop
that *Hungry Cat Picross* and *Picross S7* (Switch) lean on hardest.
The pixel-art reveal IS the emotional payoff — letting it persist
into a gallery converts each session's solve into a long-term
collectible.

Sketch: add a "Gallery" tab on the menu. Each solved level shows the
final pixel-art preview at thumbnail size, tappable to open a card
with grid-size, time, hints-used, and date solved. Group by grid size.
Empty slots show locked silhouettes. ~1 day of work; the data
(`completedLevels`) is already persisted.

Competitor reference: *Nonogram Galaxy* surfaces solved-board
thumbnails in a "Stickers" book; *Hungry Cat Picross* makes the
gallery the entire menu.

## §5 — Booster economy

| UI label | Generic / Named | Source |
|---|---|---|
| **Undo** (line 674, `undoAction()` 2105) | Generic | Free unlimited (200-deep stack) |
| **Hint** (line 678, `useHint()` 2214) | Generic | `state.hintPack` IAP at $1.99, rewarded ad path |
| **Reset** (line 682, `resetPuzzle()` 2113) | Generic | Free unlimited |

All three are literal English verbs.

Three named replacements specific to Nonogram's mark-and-deduce
mechanic:

1. **Magnifying Glass** (replaces Hint) — reveals one correct fill in
   the current row or column the player is hovering near, not a random
   cell. Stronger than the current "fill any random correct cell"
   logic. Keeps `hint_pack` IAP wiring intact.
2. **Smart Mark** (replaces Reset, or new) — auto-applies X-marks to
   cells that can be logically deduced as empty from the current fill
   state (cells that no clue group of sufficient length could cover).
   Genuinely teaches deduction; the most requested booster in nonogram
   reviews.
3. **Eraser** (renames Reset) — same wipe, but framed in-genre.
   Pair with a paper-eraser sound effect.

## §6 — ASMR audit

**Sound** — Web Audio API at line 1096:
- `playFill` (line 1115): 440 Hz sine, 80 ms — soft ink-tap on cell fill
- `playClick` (line 1125): 600 Hz sine, 60 ms — UI tick
- `playWin` (line 1118): multi-tone arpeggio
- `playError` (line 1124): 180 Hz sawtooth, 250 ms
- Procedural ambient music engine at line 1136 (`_mCtx`/`_mGain` at 0.13)

**Haptic** — `grep -n "vibrat" game.html` returns **zero matches**.
None.

**Particle / animation:**
- `popIn` keyframe (line 605) — UI overlay entrance
- `shimmer` (line 612)
- `ls-fire` / `ls-card-in` (lines 2718–19) — Level Complete card
- `xPulseOrange` (line 3706)
- No in-game particle system (no confetti, no win-burst, no
  picture-reveal animation)

**Score: 2/3 sensory channels live (sound + animation; haptic absent).
Nonogram CAN claim ASMR per the threshold, but barely.** The animation
component is mostly UI chrome — there's no win-state visual ASMR like
a sweep that reveals the picture. Adding `navigator.vibrate(6)` on
`playFill` (line 1115) and `vibrate([20, 40, 20])` on `playWin` (line
1118) is ~10 LOC, lifts to 3/3 and makes the claim much safer. A
400 ms picture-reveal animation on `winPuzzle` (sweep the grid
left-to-right unhiding the final solid picture) would be the single
highest-leverage juice addition in the app.

## §7 — Icon production

`store/icon_512_playstore.png` — warm cream background, off-white
inner panel with rounded corners and sandy/tan grid lines, red filled
cells in a 5×5 pattern forming a small heart-adjacent shape. Tiny
clue dots sit above the grid. Color palette is intentionally muted —
brick red on warm cream. No specular, no lighting, no depth.

**Classification: flat illustrated 2D.**

This icon is intentionally on-brand with the listing's "Sunday paper"
promise — the warm-paper aesthetic is the product. **Don't 3D-render
it; that would break the brand.** A directional polish would be
showing the puzzle **mid-reveal** rather than fully solved: have a
fraction of cells unfilled or X-marked, with a partial silhouette
emerging. This sells the *act* of solving rather than just the result.
~2 hours of designer time; preserves identity.

POLISH not BLOCKER. Nonogram is not the hero app and the icon already
differentiates from generic logic-puzzle icons (most use blue/grey;
Nonogram's warm cream is distinctive).

## §8 — Screenshot order

| File | Headline | Phone content |
|---|---|---|
| `01.png` | "20×20 GRIDS / TIGHT CLUES" — sub "Late-game boards that need careful deduction." | Level 348, 20×20 mid-game, mostly filled red picture |
| `02.png` | "READ THE NUMBERS" — sub "Clue-driven logic. Pictures emerge as you solve." | Level 90 mid-game with clue numbers visible, partial fill |
| `03.png` | "PICTURE REVEALED" — sub "Each grid hides a small pixel-art surprise." | Solved overlay (3 stars, +15 coins, "Solved in 0:42") on a darkened/blurred board |
| `04.png` | "DAILY PICROSS" — sub "One fresh nonogram every morning, always solvable." | Daily mode mid-game with red picture forming |
| `05.png` | "TIMES AND STREAKS" — sub "Track best times for each grid size." | Statistics screen: Top 30%, 47/500 levels, 81 stars, 247 coins, 7-day streak |
| `06.png` | "FOUR GRID SIZES" — sub "From 5×5 warm-ups to 20×20 marathons." | Select Level grid showing 5×5 BEGINNER (filled green/red status) and 10×10 EASY |
| `07.png` | "NONOGRAM LOGIC" — sub "Reveal hidden pixel art with number clues." | Main menu: title "Nonogram / Paint by numbers, today's puzzle", Play / Daily / Levels buttons, Weekly Challenge banner |

| Slot | Expected | Actual | Verdict |
|---|---|---|---|
| 1 | value-prop | difficulty hook (20×20) | MISMATCH — leads with hard-mode, not the offer |
| 2 | mid-action | mid-action (clues visible) | MATCH |
| 3 | celebration | Solved overlay on darkened board | PARTIAL — modal-over-darkened-board is the SHIP_GAME §3.1.3 anti-pattern; should re-shoot with a clean board behind, not blurred |
| 4 | variety | Daily mode | PARTIAL — Daily reads as "event" content; OK if 5 carries variety |
| 5 | event | Stats screen | MISMATCH — Stats is retention proof (slot 7), not event (Daily already covers event) |
| 6 | booster | Level Select grid | MISMATCH — variety, not booster |
| 7 | social-proof | Main menu | MISMATCH — utility, not social proof; acceptable as brand-close |

Proposed reorder:
1. `07.png` (main menu) — value-prop
2. `02.png` (mid-action with clues)
3. `03.png` (Picture Revealed) — re-shoot with clean board behind, not blurred (fixes §3.1.3 issue)
4. `06.png` (Four Grid Sizes — variety)
5. `04.png` (Daily Picross — event)
6. NEW capture of Hint modal (booster) — show the `hint_pack` IAP options + rewarded-ad path
7. `05.png` (Stats — social-proof / retention proof)

`01.png` (20×20 difficulty) is arguably scope-flex but redundant with
the level-select 06; either drop or repurpose as an alt "for serious
solvers" frame in store A/B test.

---

- **BLOCKER:** screenshot 03 modal sits over a darkened/blurred board (SHIP_GAME §3.1.3 anti-pattern), opening line is an encyclopedia entry instead of a hook
- **POLISH:** rewrite §1 leader, insert relaxing/ASMR/brain/free keywords per §2, rename Hint→Magnifying Glass and Reset→Eraser plus add Smart Mark, add `navigator.vibrate` on fill+win to lock 3/3 ASMR, reorder screenshots to 07-02-03-06-04-NEW(booster)-05, capture a Hint modal screenshot, add picture-reveal sweep animation on winPuzzle
- **DEFER:** Picture Gallery meta-loop (~1 day, biggest distinguishing feature; competitive reference: Hungry Cat Picross), icon mid-reveal polish, season-pass UI inside the game
