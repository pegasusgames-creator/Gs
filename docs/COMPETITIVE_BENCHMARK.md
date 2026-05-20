# Competitive Benchmark — what successful analogs are doing in 2026

This doc compares Pegasus Games's portfolio to the actual top-grossing
casual mobile apps and turns the gaps into specific rules. Read this
before designing or polishing any flagship app.

The analogs studied (data current as of May 2026):

- **Royal Match** by Dream Games — $1.3B in 2025, top-grossing puzzle game,
  match-3 with castle-restoration meta-loop, runs King's Cup / Sky Race /
  Team Battle / Lightning Rush concurrent events
- **Block Blast!** by Hungry Studio — 300M+ downloads, #1 worldwide
  downloads Jan-Feb 2026, 8×8 block placement with global leaderboard
  and daily challenges
- **Water Sort variants** — multiple at 10M+ downloads each, all market
  the same hooks: ASMR, satisfying pour sounds, no Wi-Fi, brain training

## 1. Listing structure

Every successful analog opens with a hook in this exact pattern:

```
[Greeting/Hook in one bold sentence]
[2-3 sentences setting up the premise]

[Section header with emoji + CAPS title]
[2-3 sentences expanding the section]

[Repeat for 3-5 sections]

✨ FEATURES
• 6-10 scannable bullets with concrete claims
• Numbers where possible (8×8 board, 500 levels, 22 colors)

🎮 HOW TO PLAY
• 3-4 short steps
• Simple verbs (Drag, Tap, Match, Sort)

[Closing hook / call to relax / casual sign-off]
[NO "Download now" CTA — banned by Google Play]
```

### Examples worth studying

**Royal Match opening line** (the gold standard):
> "Welcome to Royal Match, the king of puzzle games! Swipe colors, solve
> match-3 puzzles and help King Robert decorate his castle. An exciting
> adventure is calling you!"

What works: brand voice in line 1, character name in line 2 (King
Robert — anchor for the whole game), clear core mechanic ("swipe colors,
solve match-3"), explicit emotional hook ("exciting adventure"), all
in 30 words.

**Block Blast! opening line**:
> "🧩 Get ready for the most addictive block puzzle game of 2026! Block
> Blast combines classic puzzle gameplay with modern design to bring you
> hours of brain-teasing fun."

What works: emoji-led to grab attention in tiny store-listing thumbnails,
explicit time anchor ("of 2026") for ASO recency signals, comparison
("classic puzzle gameplay with modern design") that hits both nostalgia
and freshness.

**Water Sort variants' shared opening**:
> "Sort water color, think smart, and unwind anytime."

What works: short-description format compressed to 7 words, three
verbs that cover the full play arc (sort/think/unwind), no banned
language.

### Pegasus Games's listings should follow this pattern

Required from this point forward for every flagship app's
`metadata/en-US/full_description.txt`:

1. **Line 1: brand hook** — the genre with one specific differentiator.
   "Welcome to Water Sort Puzzle, the most relaxing pour-sort puzzle
   on Google Play."
2. **Line 2-3: core mechanic + emotional payoff** — what the player does
   and how it makes them feel.
3. **3-5 emoji-headered sections** covering: gameplay variety, brain
   training angle, ASMR/relaxing angle, offline play, daily challenge.
4. **Scannable feature bullets** with concrete numbers (NEVER "many
   levels" — always "500+ levels" or honest count).
5. **How to Play section** — 3-4 lines, each starting with a verb.
6. **Casual closing** — one line, no CTA, no "Download now."

The current Pegasus Games listings (per what we've seen) read like
instruction manuals. Royal Match's reads like a story invitation. The
difference is hookcraft, not vocabulary.

## 2. Keywords every analog uses (and why Pegasus should too)

Audit of leader listings shows these terms appearing across categories:

For puzzle/sort/match games:
- **"ASMR"** — explicitly used by Water Sort variants, Block Blast,
  Royal Match. Signals relaxation/satisfaction. Drives organic search
  in the relax-app vertical.
- **"satisfying"** — universal. Water Sort: "satisfying pour sounds."
  Block Blast: "satisfying clear animations." Royal Match: "satisfying
  cascading effects."
- **"relaxing"** — every leader uses this 3+ times in the description.
- **"no Wi-Fi"** / **"offline"** / **"no internet needed"** —
  Block Blast repeats this 6+ times in its description. Apparent
  keyword-stuffing because it works for ASO.
- **"brain training"** / **"brain teaser"** / **"sharpen your mind"** —
  positions the app for the self-improvement vertical, which has
  much higher CPI tolerance than pure casual.

For utility/tracker apps the keyword set is different:
- **"simple"** / **"easy"** / **"clean"** — positioning against
  bloated competitors
- **"private"** / **"data stays on your device"** — privacy-conscious
  framing; bonus: it's true for any app without a backend
- **"no ads"** (if you actually have an IAP to remove ads) /
  **"minimal ads"** otherwise

### Required for every flagship listing

The full_description.txt MUST contain at least:
- "relaxing" or "satisfying" (puzzle apps)
- "ASMR" if the app has any audio satisfaction elements
- "offline" / "no Wi-Fi" if the app actually works offline (most do)
- "brain" / "logic" / "puzzle" for puzzle apps
- "free to play" (true and acceptable)

These are not banned by Google. They are accurate descriptors
matching the actual app behavior. Use them.

## 3. The meta-loop gap

Every top-grossing casual game has a meta-loop OUTSIDE the core
gameplay that gives players a reason to come back tomorrow:

- **Royal Match**: castle restoration. Players earn stars from level
  completion, spend stars on castle improvements. The castle is the
  visible long-term progress.
- **Royal Kingdom**: kingdom expansion (same mechanic, different
  cosmetic frame).
- **Gardenscapes / Homescapes**: garden / house restoration.
- **Block Blast**: high-score chase + global leaderboard.
- **Water Sort variants**: theme unlocks (different bottle styles,
  different liquid effects).

Pegasus Games's current portfolio: NO meta-loop. Players complete
levels and get coins. Coins buy hints (consumable). No persistent
visible progress. No long-term goal.

### Recommended meta-loops per archetype (lowest-effort to highest)

**Lowest effort: Theme collection**
- Apps already have a theme picker (per QUALITY_PLAYBOOK §1.2)
- Convert it from "free choice" to "unlock as progression rewards"
- Player starts with 1 theme, unlocks new themes at levels 5/10/20/50/100
- Visible "Themes (3/12)" counter on menu drives completion drive
- Implementation: ~1 day of HTML/CSS/JS, zero new assets

**Medium effort: Achievement collection**
- 20-30 named achievements (First 10 Levels, No-Hint Hero, Streak
  Master, etc.)
- Visible progress bar on each, claim coins when complete
- Drives second-session return ("I was 1 short on No-Hint Hero")
- Implementation: ~1 day, mostly content writing

**High effort: World restoration**
- The Royal Match formula. Pick a thematic world (lighthouse,
  garden, bedroom, treehouse) that fits the mechanic
- Each level completion earns 1-3 stars
- Stars spent on visual restoration choices
- Visible cumulative progress drives long-term engagement
- Implementation: 1-2 weeks per app — only worth it for the hero app

### Recommended starting point

Add **Theme Collection** to all 5 flagship apps (WaterSortPuzzle, Nonogram,
PipeConnect, Puzzle2048, UnblockPuzzle). It's the lowest-effort
meta-loop with the highest organic-engagement signal. Add the
"Themes (3/12)" counter to the menu — visible progress is the lever.

Reserve **World Restoration** for the single hero app (recommend
WaterSortPuzzle since it already has data flowing).

## 4. Live ops cadence

The leaders run live events on a 2-week cadence:

- Royal Match: 100 new levels every 2 weeks + 1-2 themed events running
  concurrently (King's Cup, Sky Race, Team Battle, Lightning Rush)
- Royal Kingdom: same cadence, themed differently (Sand Museum,
  Bamboo Workshop, Spring Collection)
- Block Blast: weekly tournaments with leaderboard resets

This is impossible at 100-app scale. **Don't try.** The right
strategy:

- **Hero app (WaterSortPuzzle)**: real 2-week event cycle. Time-limited
  themes, weekend tournaments, holiday-themed level packs.
- **Other 4 flagships**: pure daily challenge + weekly leaderboard
  reset. No human-curated events.
- **Other 100+ apps**: daily challenge only.

Implementing live ops on the hero app:
- A `live_event.json` file fetched from
  `https://pegasusgames-creator.github.io/events.json` on app launch
- Schema: `{ "id": "spring_2026", "title": "Spring Pour", "starts":
  "2026-05-15", "ends": "2026-05-29", "level_pack": [...], "reward":
  {...} }`
- Game.html reads the active event, renders a banner on the menu,
  unlocks the level pack
- User maintains the JSON file — one update per 2 weeks = 1 hour of
  level design + a JSON commit

Cost-benefit: real live ops on the hero app could 2-3x its retention
if done well, which is the difference between WaterSortPuzzle earning $50/mo
and $200/mo. Worth the recurring 1 hour/2 weeks.

## 5. Booster economy

Royal Match has 4 explicit boosters, each named and visually distinct:

- **Light Ball** — clears all of one color
- **Propeller** — clears a row + column
- **TNT** — clears a 3×3 area
- **Rocket** — clears a row OR column

Each booster has its own icon, its own animation, its own pickup
sound. Players say "I have 3 Propellers saved up." Branded
boosters create vocabulary; vocabulary creates community.

Block Blast has 1 booster ("Bomb") that's a single-use button.
Simpler but still named.

Pegasus Games's flagships have: a generic "Hint" button. No
boosters. No names. No visual identity.

### Recommended booster set per genre

**Sort/pour games (WaterSortPuzzle)**:
- "Empty Tube" — adds an empty tube to the board
- "Color Reveal" — shows where one color belongs
- "Undo Move" — reverses last 3 moves

**Logic puzzles (Nonogram, Sudoku)**:
- "Reveal Cell" — shows one correct cell
- "Reveal Row/Column" — shows one full line
- "Mistake Check" — highlights any errors

**Match-3 / merge games**:
- "Hammer" — destroys one tile
- "Bomb" — clears 3×3
- "Color Burst" — clears all of one color

Each booster gets:
- A specific name (not "Power-up #1")
- A specific icon (SVG, not generic emoji)
- A specific sound + animation
- A specific in-app purchase pack ("3 Bombs for $0.99")

### Required for every flagship app

Booster system implemented before declaring app "flagship-quality."
Without named boosters, the app reads as a level-pack puzzle, not a
casual game. The leaders all have them. This is non-optional for
hero apps.

## 6. ASMR / satisfying angle

Top Water Sort variants are explicit:

> "Relaxing ASMR: Satisfying pouring sounds for a stress-free experience."
> "Juicy Visuals: High-quality 2D vector art with smooth liquid animations."

This is half the genre's appeal at this point. The mechanic is solved
(everyone has the same sort puzzle). The differentiator is the SENSE of
the pour — the audio, the haptics, the liquid physics.

Pegasus Games's wrapper has haptics. Probably has decent sound. But
none of the listings position the app as ASMR/satisfying/relaxing.

### Required: ASMR audit per flagship

For each flagship app, verify and explicitly market:

1. **Sound design** — every action has a specific sound (tap, drop,
   match, complete). Sounds are pitched-perfect, not synthetic. The
   leaders use real recorded sounds, not placeholder Web Audio API.
2. **Haptic design** — every action has a haptic (light tap on
   placement, medium on match, heavy on complete). Haptics are NOT
   the same intensity for all events.
3. **Visual satisfaction** — particle effects on match/complete, smooth
   tile/liquid animations (not snap-instant), satisfying cascade
   sequences.

If 2 of 3 are present, the listing should explicitly include the
ASMR keywords. If less than 2, the listing should NOT claim ASMR
(banned language risk: false advertising).

## 7. Icon production

Every analog uses one of:

- **3D-rendered character or object** (Royal Match: King Robert's face
  in a crown; Block Blast: glossy 3D blocks falling into a grid)
- **Hand-illustrated mascot in vivid colors** (Gardenscapes: Austin
  the butler with the garden)
- **Photorealistic object** (Water Sort variants: real glass tubes
  with liquid + light reflections)

Pegasus Games's icons (per audit data we've reviewed) appear to be
flat SVG with the focal element + gradient background. Same style as
thousands of other indie apps. Icon perceptual hash collision risk
goes up at portfolio scale.

### Required for the hero app

Replace the flat-SVG icon with one of:

1. **DALL-E 3 generated 3D-rendered icon** (~$0.04 per generation,
   iterate 10x = $0.40 per app, total cost negligible)
2. **Replicate / SDXL via API** (similar cost)
3. **Hand-commissioned art** ($30-100 from Fiverr) — only worth it
   if the app shows organic install signal first

Use `consult_designer.py` to generate an image-gen prompt sized
specifically for icons (1024×1024, no text, vivid colors, focal
element centered).

For non-hero apps, the flat-SVG approach is fine BUT vary the
focal element + texture pattern between every app. The
`pre_publish_check.py icon perceptual similarity` check enforces
this.

## 8. Screenshots

Top analogs follow a 7-screenshot order that maximizes conversion:

1. **Big claim screen** — "100 LEVELS / DAILY EVENTS / 4.7★ FROM
   2M PLAYERS" with gameplay in background. Sells the value prop.
2. **Mid-action gameplay** — board ~70% filled, dramatic moment,
   text overlay calls out the mechanic. Demonstrates the loop.
3. **Level Complete celebration** — stars, particles, coin reward.
   Shows emotional payoff.
4. **Variety / progression** — 6-9 thumbnails of different levels
   showing the game's range. Sells depth.
5. **Daily Challenge / event banner** — shows live ops content.
   Sells "always something new."
6. **Booster / power-up showcase** — names the boosters, shows them
   in action. Sells agency.
7. **Brand / community moment** — "Join 10M players worldwide" or
   leaderboard screenshot or themed event. Sells social proof.

Pegasus Games's current screenshots (per what we've seen): mostly
just "menu / gameplay / settings." Missing the value-prop framing,
missing the celebration moment, missing the variety grid, missing
the social proof.

### Required: re-capture flagship screenshots in this order

For each flagship app, produce all 7 screenshots in the order above.
The first 3 are most critical — they're shown without scrolling in
the Play Store search results.

The current `screenshot_headlines.json` schema needs to support
this 7-step structure. Add fields for:

- `value_prop_claim` (slot 1) — the big number/badge
- `social_proof` (slot 7) — the "10M players" line

If the app doesn't have the data to back claims (no real player
count, no real rating), use language that's true: "Built for puzzle
lovers" / "Perfect for relaxing breaks" instead of inventing numbers.

## 9. The honest assessment of Pegasus Games's competitive position

The leaders studied above are operations of 30-200+ people each
running on hundreds of millions in marketing spend. Pegasus Games is
one solo Ukrainian developer in debt with Claude Code as her
co-developer.

**You will not out-compete Royal Match on quality.** Don't try.

**You CAN out-compete most of the long tail of Water Sort clones**
because most of them are ALSO solo-dev shovelware with no design
investment. Your edge over them:

- A real archetype system (most clones are A+M0+V1+T1)
- Real translations (most clones are en-US only)
- A consult_designer pipeline (most clones don't iterate)
- A capture-from-emulator pipeline (most clones use static asset templates)

The realistic positioning: **Pegasus Games's hero app is the
"slightly nicer Water Sort"** in a sea of identical Water Sort clones.
Not competing with Royal Match — competing with the rank-300 Water
Sort variant that nobody iterated on after launch.

Set targets accordingly:
- Hero app realistic ceiling: 50-500 daily downloads, $50-500/month
  revenue at 12-month mark, IF live ops + meta-loop + ASMR polish all
  ship and the icon is real
- Portfolio realistic ceiling: $1k-5k/month combined across all 100
  apps once 30+ are shipped at flagship quality
- Hit-app upside: one app organically catching fire and reaching
  $5k-20k/month is plausible 1-year out, not certain

These numbers are realistic for the actual business this is. They're
not Royal Match numbers. They're enough to clear the $6k debt + cover
living expenses for a solo dev in Ukraine. That's the right target.

## 10. What to fix THIS WEEK (priority order)

1. **Delete the 33 BLOCKED_APPS folders from the repo.** They're
   liability. Move to `_blocked_clones/` outside the working tree.
2. **Delete BallSort folder from repo.** It was supposed to be gone
   Apr 30 — directory listing shows it's still there.
3. **Add a README to the repo root** describing what Pegasus Games
   is. Even a 5-sentence description.
4. **Pick WaterSortPuzzle as the official hero app.** Document the decision
   in CLAUDE.md State of apps section.
5. **Rewrite WaterSortPuzzle's full_description.txt** in the leader-format
   (hook + sections + scannable bullets + How to Play + closing). Use
   the Royal Match opening as the template.
6. **Add the ASMR/satisfying/relaxing keywords** to all 5 flagship
   listings (only for apps that genuinely have these qualities).
7. **Plan one meta-loop addition for WaterSortPuzzle** (recommend Theme
   Collection — lowest effort, highest signal-test value).
8. **Run consult_designer.py mascot --app WaterSortPuzzle** and pick the
   best returned option for a real mascot character.

That's a one-week sprint. Everything else (live ops, booster economy,
icon regeneration, world restoration meta-loop) can wait until you
see whether WaterSortPuzzle starts pulling installs after these changes.
