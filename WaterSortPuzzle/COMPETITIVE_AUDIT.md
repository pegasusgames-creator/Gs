# WaterSort — Competitive Audit

> **STATUS: RESOLVED — 2026-05-12.** Every BLOCKER and POLISH item below
> was implemented in the May 2026 audit pass (leader-format hook + ASMR/
> brain/free keywords in `full_description`, boosters renamed Color
> Reveal / Steady Pour / Fresh Start + Extra Tube + Magic Wand added,
> theme progress strip + theme-unlock card on the menu, screenshots
> reordered + recaptured from the emulator, Continue / Free Coins /
> Weekly Tournament / 7-day login streak / Season+Weekly Pass / seasonal
> events all built, IAP catalog wired). Shipped as v2.0.0. DEFER items
> (3D-rendered icon, true social-proof slot) are still deferred. Kept
> for the record; not a live to-do list.


Audit date: 2026-05-04. Auditing the flagship sort-puzzle against the
top-of-genre listings (Water Sort Puzzle / IEC Global, Ball Sort / Ariel
Software) and against Pegasus Games' own quality bar.

## §1 — Listing structure

The current opening line in `metadata/en-US/full_description.txt` is the
title-style banner on line 1 followed by line 3:

> "Sort the colorful liquid into tubes and restore order to the chaos! A
> deeply satisfying, calming puzzle game that rewards patience, strategy,
> and that perfect 'aha!' moment."

This is a generic preamble, not a hook. It's a category description
("a deeply satisfying, calming puzzle game") wrapped around a verbal
restatement of the mechanic. The reader still doesn't know what they
will *feel* in the first thirty seconds. The phrases "rewards patience"
and "perfect aha! moment" are exactly the stock language top sort-puzzle
apps avoid.

Leader-format rewrite:

```
Pour. Settle. Watch the colors stack into clean stripes — one tap, one
flow, one breath at a time.

500 levels of pure pour-and-sort, no timer, no ads in your face. Just
you and the tubes.
```

## §2 — Keywords

| Term | Status | Excerpt |
|---|---|---|
| `relaxing` | PRESENT | line 21: "No timer, no stress — completely relaxing gameplay" |
| `satisfying` | PRESENT | line 3: "A deeply satisfying, calming puzzle game…" |
| `ASMR` | MISSING | — |
| `offline` | PRESENT | line 25: "Works completely offline" |
| `brain` | MISSING | — |
| `free` | MISSING | (only "freely" appears on line 64 inside an IAP description) |

**ASMR insertion** — replace line 20 ("Beautiful water sound effects and procedural ambient music") with: "ASMR water-pour sound effects and procedural ambient music — built for headphones". §6 confirms 3/3 sensory channels are live, so the claim is honest.

**brain insertion** — replace line 12 ("500 handcrafted levels — from gentle beginner puzzles to mind-bending expert challenges") with: "500 handcrafted brain-teaser levels — from gentle beginner puzzles to mind-bending expert challenges".

**free insertion** — add a leading bullet under "✨ FEATURES": "• Free to play — every one of the 500 levels included, no paywall". The IAP catalog only sells Remove Ads, coin packs, and lives, so this is verifiable.

## §3 — Meta-loop

Inventoried persistent progression in `game.html`:

- **Coins** (`State.coins`, lines 1915–1917) — per-level reward, not a loop
- **Level stars** (`State.levelStars`, line 1896) — per-level grade
- **Daily Challenge streak** (`State.dailyChallengeStreak`, lines 1062–1212)
- **Daily Login streak** + **Streak Saver** (line 19 of description)
- **Daily Missions** (3 fresh objectives/midnight, lines 3651–3845)
- **Stats screen** — vanity surface
- **Flask Themes** (`window._THEME_PALETTES` and `renderThemes` at line 4167) — themes unlock at completed-level thresholds, the active theme reskins the gameplay palette via the `_origColors` getter trick at lines 4154–4164
- **Subscription season pass** — referenced in wrapper IAP catalog but NOT exposed in `game.html` UI

**Meta-loop verdict: PRESENT.** Flask-theme collection is a genuine cross-session progression — finish levels → unlock new flask palettes → swap to a new visual identity. The Daily Missions + Daily Challenge streak layer adds time-pressure with stakes (Streak Saver coin cost).

Weakness vs. genre leaders: theme unlocks are silent. There's no "Next theme unlocks at level 60" progress bar on the menu, so the loop's value is invisible until the player opens the Theme screen. Surfacing the next-unlock target on the home menu would make the loop felt, not just present. Polish, not structural.

## §5 — Booster economy

| UI label | Generic vs Named | Source |
|---|---|---|
| `Hint` (line 288) | Generic | First per-level use free, then nothing — no rewarded path on Hint, no IAP path |
| `Undo` (line 287) | Generic | First undo free, then rewarded ad OR `unlimited_undos` IAP ($3.99) |
| `Skip Level` (line 432) | Generic | Rewarded ad only (`showRewardedAd('skip', …)`, line 1995) |

All three are literal English verbs. No thematic naming, no booster shop, no booster icons connecting to the pour-and-sort fantasy.

Three named replacements:

1. **Color Reveal** — replaces "Hint." Glows the source-and-destination tube pair for the next correct pour. Scales: a "Triple Reveal" pack for 200 coins shows three moves ahead.
2. **Empty Tube** — new booster, no current equivalent. Adds one extra empty tube for the rest of this level only. Most-asked-for booster in sort-puzzle reviews; attacks the choke point where players quit. Cost: 50 coins or rewarded ad.
3. **Steady Pour** — replaces "Undo." Reverts the last pour without counting against the 3-star rating (current Undo penalizes stars 3 → 2 → 1 at line 1896). Reframes Undo from "I made a mistake" to "I'm being thoughtful."

## §6 — ASMR audit

**Sound** — Web Audio API at line 1244, six synthesized triggers:
- `pour` (1255): noise + bandpass 800Hz→400Hz over 250ms — real water-pour timbre
- `complete` (1284): ascending C/E/G/C2 sine arpeggio
- `select` (1307): 880Hz sine ping on tube pickup
- `error` (1275): 200Hz sawtooth on invalid pour
- `click` (1298): 600Hz menu tick
- `heartbeat` (1316): 80Hz double thump on last life
- Procedural ambient music engine at line 2859 (`_mCtx`/`_mGain` at 0.13)

**Haptic** — `navigator.vibrate` at line 1238, gated by `State.hapticsEnabled`:
- 10ms pulse on every successful pour (line 1700)
- `[30, 20, 30]` pattern on 3-star clear, 50ms otherwise (line 1926)
- 15ms confirmation when haptics toggled on (line 2432)

**Particle / animation:**
- Water splash particles at destination tube on every pour (`spawnWaterParticles`, line 1604; called from 1698)
- Celebration particle burst from each completed tube on level clear (lines 1851–1855)
- Level Complete card transform-in (`ls-card-in`, line 2900)
- Heart pulse on last-life (`heartPulse`, line 144)
- Active-level pulse on level-select map (`pulseLevel`, line 124)
- Tutorial pulse + animated hand demo (lines 4222–4224)
- Selected-tube glow at 1438; hint-tube cyan glow at 1442

**Score: 3/3 sensory channels live. WaterSort can honestly claim ASMR.**

## §7 — Icon production

`store/icon_512_playstore.png` — three flasks of differing heights, tilted inward, stratified bands of color (cool blues + green left, magenta/crimson/orange center, warm yellow/orange/red right). Background deep navy radial fade with two small bubble silhouettes. Thick white keyline on each flask, hand-painted stripe segmentation.

**Style classification: flat illustrated 2D.** No glass refraction, no caustic light, no specular highlight, no subsurface scattering. Reads cleanly at thumbnail size but has no visual depth.

Recommendation: **regenerate as a 3D-rendered glass-flask scene.** Three differently-sized flasks (keep current proportions — good silhouette brand identity), real refractive glass on the front face, layered liquid with a slight meniscus and a tiny foam ring where colors meet, soft contact shadows on the deep-navy floor, single mid-brightness rim light from upper-left so flask edges glint. Background stays ocean-depth navy. Reference Voodoo / SayGames sort-puzzle icon style — the flat illustrated look now reads as "low-effort clone" by both users and the Play Store ranking algorithm. Color stripes inside flasks should match the current vivid palette so the brand doesn't break.

## §8 — Screenshot order

| File | Visible content |
|---|---|
| `01.png` | Headline "DEEP-WATER PUZZLES" / sub "Late-game boards that test your foresight" — phone shows Level 220 mid-game board |
| `02.png` | Headline "TAP TO POUR / TAP TO UNDO" / sub "iving controls. Keep your hand on the scr…" (truncated) — Level 50 mid-action |
| `03.png` | Headline "BOARD CLEAR" / sub "Solve to keep your daily streak alive." — Level Complete with 3 stars and "+8 coins" |
| `04.png` | Headline "TODAY'S WATER GOALS" / sub "Three fresh missions every 24 hours." — phone shows Select Level grid, NOT missions |
| `05.png` | Headline "YOUR JOURNEY IN NUMBERS" / sub "Levels solved, stars, time-of-day patterns" — phone shows Daily Missions overlay |
| `06.png` | Headline "500+ POURS TO UNTANGLE" / sub "rom easy 4-tube starters to expert layout…" (truncated) — Select Level high-numbered |
| `07.png` | Headline "WATER SORT PUZZLE" / sub "Pour, sort, relax. One color at a time." — main menu |

| Slot | Expected | Actual | Verdict |
|---|---|---|---|
| 1 | value-prop | mid-game board | MISMATCH — leads with difficulty, not the offer |
| 2 | mid-action | mid-action | MATCH (subhead truncated) |
| 3 | celebration | Level Complete 3-star | MATCH |
| 4 | variety | image and headline contradict | MISMATCH (blocker) |
| 5 | event | image and headline contradict | MISMATCH (blocker) |
| 6 | booster/shop | level select grid | MISMATCH — no booster or shop shown |
| 7 | social-proof | main menu | Acceptable brand-close fallback |

Proposed reorder:
1. `07.png` (main menu) — value-prop
2. `02.png` (mid-action) — fix truncated "iving" → "Living"
3. `03.png` (Level Complete) — keep
4. NEW Daily Missions capture with three missions + at least one claimable, headline "TODAY'S WATER GOALS — three missions every 24 hours"
5. NEW Daily Challenge / streak capture with multi-day streak fire, headline "YOUR DAILY STREAK — don't break the chain"
6. NEW Shop capture with coin packs visible, headline "POWER UP — hints, undos, extra lives"
7. `01.png` repurposed as scope close, headline "500+ LEVELS — from gentle starts to expert tangles"

The truncated subheads on 02 and 06 are independent defects — the headline rendering pipeline is clipping mid-word. Fix in `screenshot_headlines.json` or the overlay generator regardless of reorder.

---

- **BLOCKER:** screenshot 04 image-headline contradiction, screenshot 05 image-headline contradiction, truncated subheads on 02 and 06
- **POLISH:** opening line of full_description (replace generic preamble with leader-format hook), insert ASMR/brain/free keywords honestly, name the three boosters (Color Reveal / Empty Tube / Steady Pour), surface "next theme unlocks at level X" on the main menu, reorder screenshots to put the menu first, capture real Shop and Daily-Streak screenshots
- **DEFER:** regenerate icon as 3D-rendered glass flask scene, build a season-pass UI inside the game to match the wrapper IAP catalog, add a true social-proof slot 7 once download numbers justify it
