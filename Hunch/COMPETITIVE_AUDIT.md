# PipeConnect — Competitive Audit

## §1 — Listing structure

`PipeConnect/metadata/en-US/full_description.txt` is **157 bytes**. Full
content quoted: *"Connect matching colored endpoints with pipes. Fill
every cell to solve the level. 150 levels from 5×5 to 10×10, daily
challenge, offline play, no timers."* No hook, no benefit framing, no
feature list, no closing line. Floor for casual puzzles is 500–800
chars; flagships sit near 1,200. **BLOCKER.**

Proposed opening:

```
Trace glowing pipes from dot to dot until every square on the grid
hums with color — no timer, no hurry, just the satisfying click of
a perfect connection.
```

Outline for the full 500–800 char body:
1. Sensory hook (above)
2. Two-sentence core loop ("Drag from dot to dot. Fill every square.")
3. Why-it-relaxes paragraph (offline, no timers, brain-friendly difficulty curve)
4. Progression (150 levels 5×5 → 10×10, Daily Challenge, six pipe palettes)
5. Modes/extras (missions, stats, hints)
6. Closing feeling-line

## §2 — Keywords

| Term | Status |
|---|---|
| `relaxing` | MISSING |
| `satisfying` | MISSING |
| `ASMR` | MISSING |
| `offline` | PRESENT |
| `brain` | MISSING |
| `free` | MISSING |

All insertion points belong in the proposed expanded description, not
the stub. `offline` is factually safe (all 150 levels embedded in the
`LEVELS` array). `brain` is safe (genuine constraint-satisfaction
puzzle). **`ASMR` should NOT be claimed yet — see §6.**

## §3 — Meta-loop

Inventoried from `game.html`:

- Level coins (`save.coins`)
- 1–3 stars per level (`save.levelStars`, line 1343)
- **Theme-collection ladder of six palettes** Classic → Neon → Pastel →
  Ocean → Inferno → Galaxy gated by 0/30/60/100/150/200 completed
  levels (line 2258)
- Daily challenge + streak (`save.dailyChallengeStreak`)
- Daily Login Streak with milestones at days 3/7/14/30 (line 1589)
- Daily Missions (3-of-8 pool, line 2300)
- Stats screen (line 2242)
- Starter pack (line 2508)
- `season_pass_monthly` subscription (line 2768)

The theme ladder IS the meta-loop. Recommendation: don't add a new one —
give each theme a **mechanical twist** so the cosmetic ladder evolves
into a *Flow Free* Bridges/Hexes/Warps-style mechanic ladder:

- Neon = glow trail on completed pipes
- Ocean = water-flow animation during draw
- Galaxy = wraparound edges (left edge connects to right)

This converts a passive cosmetic into the strongest reason to keep
playing past level 100.

## §5 — Booster economy

| UI label | Generic / Named | Source |
|---|---|---|
| **Hint** (`useHint`, line 1418) | Generic | Rewarded ad / 10 coins / `hint_pack` IAP |
| **Skip** (`skipLevel`, line 1408) | Generic | Rewarded ad |
| **Reset** (line 1375) | Generic | Free, costs a life after first try |
| **Lives** (regen) | Generic | IAP, ad |

Three named replacements:

1. **Wrench** (replaces Hint) — "Tighten a single joint — highlights
   the next correct cell on the path you've already started, not just
   the endpoints." Note: current `giveHint` only flashes the two
   endpoints, which is weak; the rename should ride a stronger algorithm.
2. **Pressure Test** (replaces Skip) — "Stress-test the level —
   auto-solves in five seconds with a watching-water animation so it
   feels earned, not skipped."
3. **Reroute** (new) — "Erase one full pipe of your choice without
   spending a life or resetting the whole board."

## §6 — ASMR audit

**Sound:** four Web Audio SFX —
- `playDragHiss` (line 620): 50ms noise burst on drag
- `playConnect` (line 637): 660 → 880 Hz chirp
- `playComplete` (line 653): four-note arpeggio
- `playError` (line 671): **dead code — no callers**
- Procedural ambient music (line 582)

**Haptic:** `vibrate(` / `navigator.vibrate` returns **zero matches**.
None.

**Particle / animation:** `@keyframes ls-fire`, `ls-card-in` (1527–28),
`xPulseOrange` (2387) — all UI chrome. **No flow animation, no
completion ripple, no confetti, no pipe pulse.** Pipes drawn as flat
round-cap strokes (`drawPipePath`, 1083).

**Score: 2/3 — do NOT claim "ASMR" in copy.** Use "satisfying" /
"calming" instead. Adding `navigator.vibrate(15)` on connect +
`vibrate([20, 40, 20])` on complete + a 400 ms canvas pulse on
completed pipes (~30 LOC) lifts the score to 3/3.

## §7 — Icon production

`store/icon_512_playstore.png` is 13,346 bytes. Flat 2D illustration:
red zigzag pipe (top) + blue mirrored-mountain pipe (bottom) with white
endpoint dots, on flat slate-grey panel inside a white circle on a
black rounded-square frame, with the word "PIPE" in light blue at the
bottom. No lighting, no specular, no depth, no gradient on the tubes.

**Classification: flat SVG.**

Recommend isometric-3D metallic tubes with top-left specular, a water
droplet at one endpoint, inner shadow on the grid panel, drop the
"PIPE" text. **POLISH, not BLOCKER** — PipeConnect isn't a hero app —
but it's the highest-leverage single visual upgrade.

## §8 — Screenshot order

`ls PipeConnect/store/screenshots/phone/` excluding `raw/`: only
`02.png`. Play Console requires 2–8. **BLOCKER.**

The single shot has headline "DRAG TO CONNECT" with a subtitle clipped
on both sides ("h endpoints to draw. Reset any line, any t…"), and the
device mockup shows the menu screen at near-tablet aspect with empty
gradient bars — fails its own value-prop job.

Recommended 7-shot capture order:
1. Gameplay mid-drag 7×7 — "TRACE EVERY COLOR"
2. 9×9 mid-game with hint highlight — "STUCK? TAP THE WRENCH"
3. Post-complete 3-star overlay — "STAR EVERY LEVEL"
4. Themes screen with progression locks visible — "UNLOCK 6 PIPE PALETTES"
5. Daily Challenge day-7 streak — "STREAK BONUS EVERY DAY"
6. Hint modal showing both ad/coin options — "FREE HINTS, NO PAYWALL"
7. Stats screen — "TRACK YOUR FLOW"

Capture via emulator + adb per `QUALITY_PLAYBOOK.md` §7.0 — no
Puppeteer.

---

- **BLOCKER:** 157-byte full_description, single-screenshot phone set, clipped headline subtitle on existing 02.png
- **POLISH:** flat-SVG icon upgrade to isometric 3D with sheen, booster rename to Wrench/Pressure Test/Reroute, hint algorithm beyond endpoint flash, add `navigator.vibrate` on connect/complete, add canvas pulse on completed pipes
- **DEFER:** mechanical twists per theme tier (glow/flow/wrap), `playError` dead code removal, season-pass content beyond cosmetic themes
