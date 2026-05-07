# UnblockPuzzle — Competitive Audit

## §1 — Listing structure

Literal opening line of `metadata/en-US/full_description.txt`:

> "Slide the colored blocks out of the way to free the trapped red
> piece — and guide it to the exit."

This is a **mechanic preamble**, not a hook. Flat declarative voice, no
sensory anchor, no emotional pull. The follow-up "Easy to learn, hard
to master" is the most generic puzzle-app sentence in existence.

Proposed leader-format rewrite:

```
The red block is wedged in. Slide one piece, then another, until the
last lane opens and it slips out — a quiet, satisfying click of
release you can chase for 150 puzzles straight.
```

## §2 — Keywords

| Term | Status |
|---|---|
| `relaxing` | MISSING |
| `satisfying` | MISSING |
| `ASMR` | MISSING |
| `offline` | MISSING |
| `brain` | MISSING |
| `free` | PRESENT (line 15: "Lives system with free daily regeneration" — feature qualifier, not SEO sense) |

Insertion points:

- `relaxing` + `satisfying`: replace line 12 `• Smooth block sliding animations` with `• Smooth, satisfying block-slide animations — relaxing for evening play`
- `ASMR`: new bullet `• ASMR-style sound design — soft slide tones and a chime-arpeggio win cue` (sine 300 → 180 Hz slide swoosh + C-E-G-C win arpeggio at lines 1745–1765 back the claim)
- `offline`: rewrite line 14 to `• No timers, no pressure — fully offline, play at your pace anywhere` (WebView loads `assets/game.html` locally)
- `brain`: change line 4 "mind-bending" → "brain-bending"

## §3 — Meta-loop

Persistent progression in `game.html`:

- Coins
- `completedLevels`
- **6 unlockable Block Themes** — Classic / Neon (lvl 30) / Pastel
  (lvl 60) / Inferno (lvl 100) / Ocean (lvl 120) / Galaxy (lvl 150)
  (`THEMES` array lines 2675–2682, applied via `window.BLOCK_COLORS`)
- Daily Challenge streak
- Daily Login Streak with 3/7/14/30-day milestones
- Daily Missions (3-of-8 pool)
- Session Streak (3/5/10-in-a-row coin bonuses)
- Lives system
- Achievements / Stats screen

**Meta-loop is present and strong.** The 6-tier free Block Themes
system is the headline meta-loop — equivalent to Unblock Me by
Kiragames' "Themes" pack. Stacked with daily missions, login streak,
session streak, achievements: four overlapping retention layers.

**No new meta-loop needed.** The fix is in marketing copy — the
description currently mentions none of these. Add bullet:
`• 6 unlockable block themes — from Neon to Galaxy, earned by playing`.

## §5 — Booster economy

| Booster | Generic / Named | Source |
|---|---|---|
| **Hint** | Generic | `useHint()` line 1405; 3 free + rewarded ad + IAP `hint_pack` |
| **Reset** | Generic | `resetLevel()` line 1466, free unlimited |
| **Skip** | Generic | `onAdReward('skip')` line 1790 — **dead branch, no UI button calls it** |

Player-visible booster economy: exactly one item (Hint).

Three named replacements:

1. **Tow Truck** — auto-removes one non-red blocking piece for the rest
   of the puzzle. Stronger than Hint.
2. **Wedge** — locks one block in place for one move so it can't slide
   back. Cheap, atmospheric.
3. **Traffic Reset** — rename existing Reset; pair with horn-honk SFX.

## §6 — ASMR audit

**Sound:**
- Slide tone sine 300 → 180 Hz / 140 ms (line 1745, fired at 1274)
- Bump square 120 Hz / 80 ms (1751)
- Win 4-note C-E-G-C arpeggio (1756, fired at 1297)
- Ambient music drone (1697)

**Haptic:** zero. No `vibrate`, `haptic`, or `navigator.vibrate`
anywhere.

**Particle / animation:**
- 9-shard win confetti (332–340)
- 60-particle radial burst on solve (`spawnParticles` 1364)
- Hint-arrow pulse (1068)
- Ramp-eased slide animation (1123)
- Exit-arrow drop-shadow glow (51)

**Score 2/3 → can claim ASMR.** Polish: add `navigator.vibrate(8)`
before line 1746 and `vibrate(40)` before 1757 — 5 minutes of work,
3/3.

## §7 — Icon production

`store/icon_512_playstore.png` (9 KB): top-down 4-column grid with
horizontal red 2×1 block + vertical blue 1×3 + 2 grey blocks + yellow
arrow toward right-edge exit gap, "UNBLOCK" wordmark across bottom in
chunky purple sans-serif. Flat dark-navy background. No lighting, no
specular, no drop shadow. 4-px bevel as only depth cue.

**Classification: flat SVG / illustrated 2D.** Looks like an in-app
diagram. Wordmark at bottom is a Play Store anti-pattern (text
unreadable at 48 dp).

**POLISH not BLOCKER:** isometric-3D treatment with prominent red
car-block, ~30° tilted board, plastic specular highlights, exit-gap
glow, wordmark dropped. Acceptable as flat SVG for portfolio app #5;
UnblockPuzzle is not the hero.

## §8 — Screenshot order

| # | Headline | Content |
|---|---|---|
| 01 | "TIGHT JAMS / CLEVER MOVES" | Late-game crowded board, red block off-screen |
| 02 | "SLIDE BLOCKS / FREE THE RED" | Sparse Level 4 board (red + 1 green), Hint button |
| 03 | "ESCAPE MADE" | Win overlay: ESCAPED!, 3 stars, +25 coins |
| 04 | "DAILY SLIDES / DAILY REWARDS" | Missions screen + 4 achievement badges |
| 05 | "MOVES MADE / PERFECT SOLVES" | Stats: 87/150, 58 perfect, 6-day streak, 1240 coins |
| 06 | "500+ JAMS / TO ESCAPE" | Level Select grid 1–50 |
| 07 | "UNBLOCK THE / RED BLOCK" | Main menu, all entry points, weekly mission ticker |

vs. canonical (1=value-prop, 2=mid-action, 3=celebration, 4=variety,
5=event, 6=booster, 7=social-proof):

- **1: MISMATCH** — opens cold with no red block visible
- **2: MISMATCH** — tutorial frame, not mid-action
- **3: MATCH**
- **4: PARTIAL** — Missions reads as variety/meta-loop
- **5: MISMATCH** — Stats is retention-proof, not event
- **6: MISMATCH + CONTENT LIE.** Headline says "500+ JAMS" but
  `LEVELS.length` is 150 (confirmed: 150 `// Level N` markers). Hard
  SHIP_GAME §8.2 honesty fail and a Play Store Misleading Behavior
  policy risk.
- **7: MISMATCH** — menu is utility, not social proof

**Proposed reorder:** 07 → 02 → 01 → 03 → 04 → 05 → 06 (with frame 06
headline corrected to "150 JAMS").

---

- **BLOCKER:** screenshot-06 headline lies (claims "500+ JAMS", build has 150 levels) — must correct to "150 JAMS" or drop the count claim before next upload
- **POLISH:** add `relaxing` / `satisfying` / `ASMR` / `offline` / `brain` keywords to full_description per §2; rewrite opening hook per §1; reorder screenshots to 07-02-01-03-04-05-06; rename Reset to "Traffic Reset" and add Tow Truck + Wedge boosters; add `navigator.vibrate(8)` on slide and `vibrate(40)` on win to hit 3/3 ASMR; surface the 6-theme meta-loop and Missions/Stats in description bullets
- **DEFER:** commission isometric-3D icon to replace flat-SVG `icon_512_playstore.png`; wire `onAdReward('skip')` branch (line 1790) to a UI button or remove the dead code
