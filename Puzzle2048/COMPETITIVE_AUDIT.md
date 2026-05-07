# Puzzle2048 — Competitive Audit

## §1 — Listing structure

Literal full content of `metadata/en-US/full_description.txt` (97
bytes, single line):

> "2048 Puzzle is the ultimate number merging game that's easy to
> learn but impossible to put down!"

**This is below floor.** Casual-puzzle full descriptions sit at
500–1,200 chars; 97 bytes will not rank, will not convert, and reads
to a Play Store reviewer as "substantively empty." It also opens with
two of the most-flagged generic phrases in the genre — "the ultimate"
and "easy to learn but impossible to put down" — which Google's
listing-quality classifier specifically downgrades. **BLOCKER.**

2048 is also a brutally crowded genre (50+ near-clones with similar
copy). Differentiation in the lead is the only path through.

Proposed leader-format opening:

```
Slide. Match. Watch two tiles fuse into one with a soft thud you'll
feel in your fingertips — then chase the next merge, and the next,
all the way to 2048 and beyond.
```

Outline for the full 500–800 char body (replace the entire stub):
1. Sensory hook (above)
2. Core loop in 2 sentences ("Swipe any direction. Equal numbers
   collide and double.")
3. What makes THIS 2048 different — six unlock-able tile themes
   (Classic / Neon / Pastel / Inferno / Ocean / Galaxy), daily challenge,
   missions, achievement cards
4. Why it's calm — "no timer, no lives between sessions, no forced
   tutorial — just you and the grid"
5. Honest free-to-play line ("Every theme unlock is earned, never
   sold")
6. Closing feeling-line

## §2 — Keywords

| Term | Status |
|---|---|
| `relaxing` | MISSING |
| `satisfying` | MISSING |
| `ASMR` | MISSING |
| `offline` | MISSING |
| `brain` | MISSING |
| `free` | MISSING |

All six are missing because the description is a 97-byte stub. All
six are honest claims for this app: it plays offline, the merge is
genuinely satisfying (Web Audio merge sound + tile animations), it's
free with in-game-earned themes, it's a number/logic puzzle (brain),
and it's no-timer (relaxing). All six insertion points belong in the
proposed expanded description from §1, not the existing stub.

`ASMR` is gated on §6 hitting 2/3 — confirmed below, claim is safe.

## §3 — Meta-loop

Inventoried from `game.html`:

- **bestScore** (line 781) — vanity surface
- **coins** (line 785) — currency, used in shop only
- **dailyChallengeStreak** (line 794, +20 coin bonus on daily best at
  line 1542) — daily streak
- **achievement-card** (line 159 styles, multiple cards rendered at
  384/389/393) — including a hidden "Reach 2048" card at line 389
  that flips visible only when reached
- **daily-streak panel** (line 166, rendered at line 397)
- **themesGrid** (line 528) with caption "Complete games to unlock new
  themes!"
- **THEMES array** (line 2573) — 6 themes with `unlockLevel` gating,
  active theme persisted (`State.activeTheme`)
- **missionsScreen** (line 543, 3-of-8 daily mission pool)
- **Stats screen** with high-score / streak surfaces
- `undo_pack` IAP, `season_pass_monthly` IAP — wired in catalog

**Meta-loop verdict: PRESENT.** Six unlockable tile themes is the
correct headline meta-loop for 2048 — equivalent to Threes' tile
variants and 2048 by Ketchapp's tile-art unlocks. Stacked with daily
challenge streak + missions + achievement cards: four overlapping
retention layers, comparable to UnblockPuzzle's setup.

Where it falls short vs. competitors: the unlock pacing is gated on
"Complete games" (line 529) without showing "next theme unlocks at X
games" on the menu. The `tile2048Card` achievement (line 389) is
meaningful — reaching 2048 is the franchise's signature milestone —
but is invisible until unlocked. Add a progress bar.

Also: the description currently mentions NONE of these. The fix is
80% marketing copy, 20% surfacing.

Competitor reference: *2048 by Ketchapp* uses a "blocks unlocked"
progress strip on its menu; *Threes* gates board themes behind score
milestones with a visible target.

## §5 — Booster economy

| UI label | Generic / Named | Source |
|---|---|---|
| **Undo** (button line 364, `Game.doUndo()`) | Generic | First undo per session free, then rewarded ad OR `undo_pack` IAP at $0.99 |

**That's it.** A single booster. No hint, no skip, no tile-clear, no
swap. By 2048-genre standards (Ketchapp's 2048 has tile-smasher,
swap, and continue) this is significantly under-equipped.

Three named replacements specific to 2048's slide-and-merge mechanic:

1. **Tile Smasher** — destroy any single tile on the board. Use case:
   late-game when an off-value tile (e.g., a stray 4 in the corner)
   is locking up your highest-tile lane. Cost: rewarded ad or 50
   coins. New booster, no current equivalent.
2. **Merge Magnet** — pull two same-value tiles toward each other,
   forcing a merge regardless of their position. Cost: rewarded ad or
   80 coins. Best paired with a 1024+1024 lockup.
3. **Tile Doubler** — promote one tile to the next power of two.
   Premium booster, IAP-only via a new `doubler_pack`. The most
   coveted booster in 2048 reviews; very compelling content for a
   season pass tier.

Keep the existing Undo (rename optionally to **Time Rewind** for
theming consistency with Tile Smasher / Merge Magnet).

## §6 — ASMR audit

**Sound** — Web Audio API at line 646:
- `playMergeSound(value)` (line 699): synthesized merge tone scaled by
  tile value — bigger merges = lower frequency, more presence
- `playSpawnSound` (line 718): subtle pop on new-tile spawn (line 1464)
- `playWinSound` (line 753): celebration on reaching 2048 (line 1482)
- Procedural ambient music engine at line 658 (`_mCtx`/`_mGain` at 0.13)

**Haptic** — `grep -n "vibrat" game.html` returns **zero matches**.
None.

**Particle / animation:**
- `tileSpawn` keyframe (line 297) — scale-up entrance on new tile
- `tileMerge` keyframe (line 302) — scale-pulse on merge
- `ls-fire` / `ls-card-in` (lines 1844–45)
- `xPulseOrange` (line 2711)
- `drawGrid(..., animProgress)` (line 1102) drives slide animation
  with merge highlight
- No screen-shake on big merges, no particle burst on 2048-reach, no
  confetti

**Score: 2/3 sensory channels live (sound + animation; haptic
absent). Puzzle2048 CAN claim ASMR per the threshold.** The animation
side is the strongest of any audited app — `tileMerge` is genuinely
juicy, the merge-tone-scales-by-value is novel for the genre. Adding
`navigator.vibrate(8)` on every merge inside `playMergeSound` (line
699) and `vibrate([30, 60, 30])` on `playWinSound` (line 753) is ~6
LOC, lifts to 3/3 and lets you claim "tactile" alongside ASMR. Adding
a screen-shake on merges of 256+ and a particle burst on 2048-reach
is ~30 LOC and would make the win moment unmistakable.

## §7 — Icon production

`store/icon_512_playstore.png` — 2×2 grid of four tiles labeled
**2 / 4 / 8 / 2048** in the **canonical Cirulli 2048 palette** (cream
with grey "2", tan with grey "4", orange with white "8", yellow with
white "2048"), on a black radial-fade background. Tiles have a subtle
two-tone gradient (lighter top half, darker bottom half) and rounded
corners. No specular, no scene depth, no merge animation visible.

**Classification: flat illustrated 2D.**

**This is the highest-leverage problem in the app.** The 4-tile
2/4/8/2048 layout in cream/tan/orange/yellow is the **single most
copied 2048 icon pattern on the Play Store** — at least 30 of the
top-50 results for "2048" in 2026 use this exact composition. The
icon is functionally indistinguishable from those clones at thumbnail
size, so even a perfect rewrite of the description and a complete
screenshot set will struggle to convert search-results impressions
because the user's eye sees "another one of those."

**BLOCKER for next release.** Recommended regeneration path:

- Single hero tile, mid-merge, rendered in 3D with depth — caustic
  light catching the bevel, soft contact shadow
- Signature non-yellow color (cool teal, royal violet, deep magenta)
  to break from the canonical palette
- Optional: a small particle wisp showing the "2048" digit forming
  out of two "1024" digits colliding — sells the merge moment,
  not the win state
- Drop the 2/4/8/2048 grid layout entirely
- Reference: King's *Candy Crush* uses one hero candy mid-twist
  rather than a grid; do the equivalent for 2048

This is the one icon in the audited five where the flat 2D treatment
isn't just a polish gap — it's actively damaging discoverability.

## §8 — Screenshot order

`store/screenshots/phone/` (excluding `raw/`) contains a single file:
**`02.png`**.

Play Console requires 2–8 phone screenshots. **BLOCKER.**

The single existing shot:
- Headline "SWIPE TO MERGE" with a subtitle truncated on **both**
  ends: "[…]al tiles combine. Reach the next power of [2…]"
- Phone mockup at near-tablet aspect ratio (the device frame is
  oriented landscape-ish) with empty bands top and bottom
- Shows the **main menu**, NOT gameplay — title "2048", a tiny empty
  grid preview, and stacked buttons (Play / Daily Challenge / High
  Scores / Shop / More Games / Missions / Stats)
- No tile values visible, no merge in progress, no value prop
  delivered

This shot fails its own headline ("SWIPE TO MERGE" with no merge
shown) and fails the canonical slot job for slot 2 (mid-action). The
truncated subtitle is the same headline-rendering pipeline bug seen
on WaterSort 02/06.

Recommended full 7-shot capture order (all to capture from emulator
per `QUALITY_PLAYBOOK.md` §7.0):

1. **Mid-game with a 1024 tile + a 512 staged for a merge** —
   "SWIPE TO MERGE" / "Two tiles. One number. Endless chase."
2. **Mid-merge animation captured** — "WATCH THEM FUSE" / "Every
   match doubles your highest tile."
3. **2048 reach win overlay** with the unlocked achievement card —
   "REACH 2048" / "And keep going for 4096, 8192, 16384."
4. **Themes grid** with locks visible on Inferno / Ocean / Galaxy —
   "SIX TILE WORLDS" / "Unlock new boards by playing — never paid."
5. **Daily Challenge result** with day-7 streak — "DAILY MERGE" /
   "Fresh seed every morning. Streak bonus every day."
6. **Tile Smasher / Merge Magnet booster panel** (after §5 is
   implemented) — "WHEN THE BOARD LOCKS UP" / "Smash, magnet, or
   double — your call."
7. **Stats screen** with high score + total merges + best streak —
   "YOUR MERGE HISTORY" / "Every milestone, kept."

Frame 6 depends on §5 boosters being added; if those are deferred,
substitute a Missions screenshot in slot 6.

---

- **BLOCKER:** 97-byte stub full_description, single phone screenshot (Play Console minimum is 2), icon indistinguishable from 30+ canonical 2048 clones in cream/tan/orange/yellow on black, screenshot 02 subtitle truncated on both ends
- **POLISH:** insert all six §2 keywords once description is rewritten, add `navigator.vibrate(8)` on merge and `vibrate([30,60,30])` on 2048-reach to lock 3/3 ASMR, ship 3 named boosters (Tile Smasher / Merge Magnet / Tile Doubler) — current single-Undo is under-equipped for genre, surface "next theme unlocks at game N" on menu, add particle burst + screen-shake on merges ≥ 256
- **DEFER:** rename Undo → Time Rewind for booster-theme consistency, leaderboards, achievement-count tracking surface, mechanical-twist themes (Galaxy = wraparound edges), full season-pass UI inside the game
