# App Archetypes — beyond the template

This document is a reference catalog of distinct app personalities, menu
compositions, copy voices, and character/mascot patterns. Use it during
Phase 1 of `SHIP_GAME.md` to make sure each new app feels like a real
designed product, not a templated variant.

The problem this solves: If 100 apps all use the same menu structure
(hero Play button → secondary buttons → icon row), even with different
colors, users browsing the Pegasus Games portfolio will spot the
template instantly. Google's spam classifier will too. Each app needs
genuine identity beyond palette swaps.

This doc is structured as a menu of choices — each app picks one
archetype from each of: layout, mascot/character, copy voice, and
texture/finish. Combinations are explicitly discouraged from being
reused — if WaterSortPuzzle uses Layout A + Voice 2, the next sort puzzle
should use Layout C + Voice 4 even though it's the same genre.

---

## 1. Menu layout archetypes

Pick one per app. Track which apps use which in `app_themes.py` (each
theme entry should have a `layout_archetype` field).

### A — Hero Play, button stack (the template)
The default. One big Play button, two secondary, three icons. **Use
sparingly.** Best for: launch apps where you have no design budget,
small/utility apps. Avoid for hero/flagship games. Currently used by:
WaterSortPuzzle, BallSortPuzzle.

### B — Map / journey screen
No menu buttons at all. The home screen IS a horizontal/vertical scroll
showing levels as a path with the player's avatar at their current
position. Tap a level to play. Daily Challenge appears as a marker on
the path. Settings + Shop are tiny corner icons. Best for: progression-
heavy games (Sudoku, Nonogram, level-driven puzzles). Inspired by:
Royal Match, Candy Crush map screens.

### C — Hub world / room
The player has a "home" they can decorate or interact with. Buttons
disguised as objects: a clock = Daily Challenge, a chest = Rewards, a
book = Levels, a door = Shop. Best for: cozy / collection apps,
merge games. Inspired by: Merge Mansion, Gardenscapes.

### D — Vertical card feed
Menu is a scrollable feed of cards. Top card: today's challenge
(swipe-to-play). Next card: continue where you left off. Next: weekly
event. Next: shop offers. No traditional buttons. Best for: live-ops
heavy games, daily-engagement apps. Inspired by: Marvel Snap menu.

### E — Animated character speaks to you
The home screen is dominated by a character (mascot, avatar) that
speaks to the player. "Ready for level 47?" "You haven't played in 2
days — here's a free hint!" Buttons appear in speech bubbles or
pop-up panels. Best for: kids apps, casual story-driven games.

### F — Direct-to-game / minimal menu
No menu at all. App opens directly to the next playable level with a
small overlay showing level number + lives + coins. Tap-anywhere to
start. Settings/shop/etc. live behind a hamburger icon. Best for:
hardcore puzzle audiences who want zero friction. Inspired by:
Two Dots, Threes.

### G — Calendar / streak grid
Menu is a calendar showing your daily play streak, with today's
challenge highlighted. Tapping a past day replays that day's challenge.
Tapping today = play. Best for: daily-puzzle games (Wordle, Mini
Crossword variants).

### H — Workshop / inventory
The home screen shows the player's collected items, unlocked themes,
or earned badges as a visual collection. Play button is small in the
corner because the inventory IS the reward viewer. Best for: cosmetic-
heavy games, badge-collection apps.

### I — Toolbox (tools/utilities)
For non-game apps, no menu — open directly to the tool. Tabs along
the top or bottom switch between modes. Settings is a corner icon.
Best for: timers, calculators, trackers, tools.

### Constraint
At any point in time, no more than 30% of shipped apps should use
Archetype A. Across 100 apps, roughly: A=30%, B=15%, C=10%, D=10%,
E=10%, F=10%, G=5%, H=5%, I=5%.

---

## 2. Mascot / character patterns

Whether and how the app has a "personality presence" beyond the UI.

### M0 — None
No mascot, no character. The game elements (flasks, blocks, tiles)
ARE the personality. Currently most Pegasus Games apps. **Don't make
all apps M0.** That's a major source of the artificial feel.

### M1 — Anthropomorphized game element
The flask has eyes. The block smiles when placed. The tile bounces
when matched. Tiny details, no full character. Adds personality
cheaply. Effort: 4-8 hours of art per app.

### M2 — Static mascot
A character drawn in 2-3 expressions (happy, thinking, surprised) that
appears at key moments: level complete, game over, daily challenge
intro. Doesn't move much, but is consistently present. Effort: 1-2
days of art per app (or use AI-generated sprites with consistency
prompting).

### M3 — Animated companion
A small character with idle animation, reactions to player actions
(taps, wins, fails), and contextual dialogue. Lives in the corner of
the gameplay screen. Effort: 3-5 days of art per app.

### M4 — Spirit-of-the-app abstract
Not a character, but a recurring abstract motif: drifting particles,
flowing water, glowing orbs, etc., that adds atmosphere without
needing character design. The "vibes" approach. Effort: 1-2 days of
particle/motion design.

### Allocation across portfolio
Aim for: M0 = 30%, M1 = 30%, M2 = 20%, M3 = 10%, M4 = 10%.

When picking an archetype, also pick whether mascot is named. Named
mascots (e.g., "Drippy" the water drop in WaterSortPuzzle) build
identification. Unnamed mascots are cheaper but disposable.

### How to actually produce mascots — the realistic options

Claude Code cannot generate raster images directly (no image generation
in the LLM). The mascot has to come from somewhere. Four practical
options, in order of preference for a solo Ukrainian publisher:

#### Option 1 — SVG mascots written as code

Claude Code can write SVG paths that draw simple stylized characters:
geometric blobs with eyes, abstract creatures, minimal animal
silhouettes. Two Dots and Threes use this approach successfully.

What works: **M1** (anthropomorphized game element) and **M4** (abstract
motif) are both fully achievable in pure SVG code by Claude Code with
no external assets.

What doesn't: M2 (static mascot with multiple expressions) is possible
in SVG but tedious, and M3 (animated companion) generally needs sprite
sheets.

For M1 specifically — adding eyes/expressions to existing game pieces —
Claude Code should default to this. Examples:
- WaterSortPuzzle flask with a small eye-pair visible through the water
- BlockPuzzle tetromino with a tiny face on the largest block
- Sudoku digit that briefly smiles when placed in the right cell

Claude Code should produce these inline as part of game.html without
any external dependencies. This is the M1 standard.

#### Option 2 — Image generation API call

For M2 mascots (static character with 2-3 expressions), Claude Code
can shell out to an image generation API:

- **DALL-E 3** via OpenAI API: ~$0.04 per 1024×1024 image, good for
  whimsical cartoon characters. Requires OPENAI_API_KEY.
- **Replicate**: ~$0.01-0.05 per image, hosts SDXL and other models.
  Requires REPLICATE_API_TOKEN.
- **Stability AI**: ~$0.04 per image, requires STABILITY_API_KEY.

Cost for M2 (3 expressions × 1 mascot per app × 50 apps over a year):
~$6-10 total. Negligible.

Claude Code should write a prompt template with consistency controls
(same character description across all 3 expressions, same color
palette, same art style, transparent background) and produce sprite
PNGs that go into `<App>/android/app/src/main/assets/mascot/`.

Recommended prompt template for casual game mascot:
```
Cute simple mascot character for a casual mobile puzzle game.
Character: <theme-appropriate description, e.g., "a smiling water drop
with tiny limbs">
Expression: <happy | thinking | surprised | sad>
Style: flat vector illustration, bright saturated colors, thick outlines,
white transparent background, centered, cartoon style, child-friendly.
No text, no UI elements. Square 1:1 aspect ratio.
```

If Claude Code is configured with one of these API keys (in the
environment or in a config file at `Gs/scripts/config/image_gen.env`),
it can call directly. If not configured, surface the API choice to
the user.

#### Option 3 — Pre-made asset libraries

CC0 (public domain) asset libraries:
- **Kenney.nl** — generic game assets, unlimited use, no attribution
- **OpenGameArt.org** — varied quality but lots of CC0/CC-BY mascots
- **Itch.io free assets** — many indie creators publish CC0 packs

Claude Code can download a relevant pack, pick characters that match
the app's theme, and integrate. Less custom but legally clean and free.

For utility apps where the mascot doesn't need to be unique
(BloodPressureLog, FastingTimer), this is the right choice — no need
to commission custom art for a tracker.

#### Option 4 — Ask the user / ask Claude in chat

When Claude Code can't decide between options or wants creative input,
it can pause and surface the question to the user. The user can then
either:
- Bring the question to a Claude chat session (this works well — Claude
  in chat can write detailed image-gen prompts, design SVG mascots, or
  recommend specific OpenGameArt packs)
- Make the call themselves and paste the answer back
- Defer the mascot and ship the app as M0 for now, upgrade later

The pattern: Claude Code in the SHIP_GAME flow writes a "mascot brief"
to `<App>/metadata/mascot_brief.md` describing what the app needs:
- Character description (informed by game mechanic and chosen voice)
- Expressions needed (3 for M2: happy, thinking, surprised)
- Style notes (matches app's chosen texture archetype)
- Where the mascot will appear (which screens, which moments)

User reads brief, brings to a Claude chat, gets back either:
- SVG code (paste into game.html)
- DALL-E prompt (run yourself with OpenAI API)
- Specific OpenGameArt link (download and integrate)

Then user pastes the answer back to Claude Code, who proceeds with
integration.

### Default for new apps

Without explicit override:
- General-audience puzzle games: Claude Code defaults to M1
  (anthropomorphized game element via SVG, no external assets)
- Tools / utility apps: Claude Code defaults to M0 (no mascot —
  utility apps don't need character)
- Kids program apps: Claude Code surfaces "needs M2 or M3" to user
  because Kids apps benefit most from real characters, and these
  warrant the API-generation cost
- Flagship games (the user's hand-picked top-tier): user-specified

When Claude Code finishes Phase 1.2 (archetype selection), if the
chosen mascot pattern is M2 or M3, it MUST also pick the production
path (Option 1/2/3/4) and document it in `metadata/app_identity.md`.
Don't pick M2 with no plan for how to actually produce the art.

---

## 3. Copy voice archetypes

How the app talks to the player. Affects: button labels, modal copy,
tutorial text, push notification text, store listing voice.

### V1 — Neutral functional (the default; minimize use)
"Play", "Levels", "Settings", "Level 1 of 150", "Level Complete!".
Currently used by all Pegasus Games apps. Reads as templated.

### V2 — Encouraging coach
"Great pour!", "Nice thinking", "You've got this", "Almost there",
"Try this one — I think you'll like it". Used in: Headspace, Duolingo
(early Owl). Best for: brain training, learning, daily-habit apps.

### V3 — Playful narrator
"The water is restless", "Ah, a worthy challenger!", "You shall
overcome this puzzle", "Behold — Level 50!". Slightly theatrical,
gentle humor. Best for: cozy games, casual puzzles.

### V4 — Snarky / dry
"Took you long enough", "Hmm, an interesting choice", "Try not to
spill this time", "Daily challenge: incoming, whether you like it or
not". Used in: Two Dots, certain indie games. Best for: hardcore
audiences, niche puzzle fans.

### V5 — Calm / zen
"Take your time", "Breathe", "When you're ready", "Beautiful". Quiet
and supportive. Best for: meditation-adjacent apps, stress-relief
games.

### V6 — Enthusiastic / arcade
"AWESOME!", "PERFECT!", "BIG WIN!", "STREAK!", "NICE COMBO!". All caps
celebrations. Best for: arcade casual, action games.

### V7 — Educational warm
"Did you know?", "Here's a tip", "Try thinking about it this way",
"You're learning fast". Best for: kids apps, educational games.

### V8 — Direct / minimal
"Tap to begin", "Tap to continue", no extra words, no fluff. Best for:
tools, productivity apps, hardcore puzzles for purists.

### Allocation guidance
- Don't ship 5 V2 apps in a row — feels like the same brand voice
- Match voice to genre, but vary across genres (don't make all your
  word games V2)
- Ship at most one new app per voice per month

---

## 4. Texture / visual finish archetypes

The "feel" of surfaces and elements. Beyond color, this controls
whether an app reads as "AI-game-jam clean" vs "real designed product."

### T1 — Flat clean (the default; minimize use)
Pure flat fills, no textures, sharp corners or perfectly-rounded
corners. Smooth gradients. The current Pegasus Games look. Reads as
"AI-generated 2025 game" if used everywhere.

### T2 — Soft glassmorphism
Translucent panels with backdrop blur, gentle shadows, light reflective
edges. Buttons have a subtle "glass card" feel. Used in: macOS Sonoma,
modern fintech apps. Adds depth without complexity. Effort: CSS only.

### T3 — Subtle paper texture
Backgrounds and panels have a light noise/grain overlay simulating
paper. Slight imperfections in lines. Used in: many cozy puzzle games
(Connections, NYT puzzles). Adds warmth. Effort: one PNG noise overlay
asset.

### T4 — Wood/material themed
Backgrounds and panels look like wood, fabric, stone, or metal.
Inspired by board-game tactile aesthetic. Used in: physical-board
puzzle apps (Mahjong, chess, classic solitaire). Effort: themed
asset pack per app.

### T5 — Hand-drawn / sketch
UI elements have slightly imperfect lines as if hand-drawn. Buttons
look like they were sketched with a marker. Used in: Crayon Physics,
indie cozy games. Strong personality but takes longer to do well.

### T6 — Neon / arcade
Glowing edges, scanlines, retro CRT effects. Used in: arcade-style
games, retro revival. Effort: CSS filters and glow effects.

### T7 — Storybook / illustrated
Heavy illustration, painted backgrounds, stylized typography. Used
in: kids apps, narrative puzzle games. Effort: significant — needs
real illustration work.

### T8 — Brutalist / minimal
Stark contrast, monospace or display fonts, no rounded corners,
geometric shapes. Used in: certain word games (Wordle), brain
trainers. Effort: low — just CSS choices.

### Allocation guidance
At least 60% of shipped apps must NOT be T1 by month 6. Currently 100%
of Pegasus Games apps are T1.

---

## 5. Anti-patterns: what makes apps feel artificial

These are concrete things to AVOID when designing each app. Apps that
hit 3+ of these read as "templated AI output" to users:

- **Center-aligned everything.** Title centered, buttons centered, all
  modals centered. Real designs use offset weight.
- **Same icon set across all apps.** If three apps all use the same
  Lucide-style line icons in the same composition, they read as
  clones. Vary icon styles between apps (line vs filled vs hand-drawn
  vs photo-realistic).
- **All caps headlines on every screen.** "WATER SORT PUZZLE" /
  "POUR AND SORT" / "DAILY MISSIONS" — when every text element shouts,
  none stand out. Use mixed case for body, all-caps only for true
  emphasis.
- **Generic emoji-replacement icons.** Replacing "🪙" with an SVG coin
  is the right call, but if the SVG coin is generic (just a circle
  with a dollar sign), it reads as templated. Each app's currency
  icon should reflect the app theme: water droplets in WaterSortPuzzle,
  ruby gems in a fantasy puzzle, sand grains in a beach game.
- **Identical button shapes / sizes / spacings.** The default rounded-
  rect button is fine for most apps; don't use it for ALL apps. Vary
  button shapes: pill, rounded square, circle, hexagon, asymmetric.
- **Symmetric vertical layout.** Header, title, body, buttons, footer
  — every app has this column. Try: side panel for buttons, top tab
  bar, floating action button, full-screen background with overlay
  controls.
- **Generic celebration moments.** "Level Complete! ⭐⭐⭐ +8 coins" —
  every app does this. Differentiate: WaterSortPuzzle says "Crystal Clear!"
  and shows water settling; Sudoku says "Solved!" and the grid does a
  satisfying confirmation animation; word games say "You found it!"
  and the word fades into a journal of completed words.
- **Same loading/transition patterns.** Spinner → fade-in is the
  default. Vary: water-fill loading, ink-bleed transition, page-flip,
  curtain-pull.
- **Identical settings screen.** "Sound, Music, Haptics, Reset, About"
  — every app's settings reads identical. Vary the order, group
  differently, add app-specific settings (a Sudoku app might have
  "Pencil mode default", a sort puzzle might have "Auto-collapse
  cleared tubes").

---

## 6. Combination examples

To make the abstraction concrete, here are 5 example combinations
showing what each app's identity should look like:

### Example 1 — WaterSortPuzzle (current, shipped)
- Layout: A (hero Play, button stack) — fine for v1, plan B/D for v2
- Mascot: M0 → upgrade to M1 (animated water drop in flasks)
- Voice: V1 (neutral) → upgrade to V5 (calm/zen) — "Take your time"
- Texture: T1 (flat clean) → upgrade to T2 (soft glassmorphism)
- Result feel: zen, meditative, water-themed

### Example 2 — Sudoku (planned)
- Layout: G (calendar / streak grid) — daily puzzle pattern
- Mascot: M0 (no mascot — minimalist genre)
- Voice: V8 (direct minimal)
- Texture: T3 (subtle paper texture) — graph paper feel
- Result feel: serious, contemplative, NYT-puzzle-section adjacent

### Example 3 — BlockPuzzle (planned)
- Layout: B (map / journey)
- Mascot: M1 (anthropomorphized blocks with eyes)
- Voice: V6 (enthusiastic arcade)
- Texture: T4 (wood material theme)
- Result feel: tactile, satisfying, addictive

### Example 4 — Nonogram (planned)
- Layout: F (direct-to-game minimal)
- Mascot: M0
- Voice: V8 (direct)
- Texture: T8 (brutalist minimal)
- Result feel: pure puzzle, hardcore audience, no fluff

### Example 5 — KidsPiano (planned, Kids program)
- Layout: E (animated character)
- Mascot: M3 (full animated companion — friendly cartoon mouse)
- Voice: V7 (educational warm)
- Texture: T7 (storybook illustrated)
- Result feel: warm, inviting, child-appropriate

Across these 5: 5 different layouts, 4 different mascot levels, 5
different voices, 5 different textures. No two apps feel like the
same product.

---

## 7. How to use this doc

During SHIP_GAME.md Phase 1, after deciding the game's mechanic,
explicitly choose:

1. **Layout archetype** (from §1). Check `app_themes.py` to see what
   other apps use; pick a different one.
2. **Mascot pattern** (from §2). Decide if this app has a mascot, what
   level, and write a short character bio if M2+.
3. **Copy voice** (from §3). Write 5 sample button labels and 3 sample
   modal headers in the chosen voice. Reuse this voice consistently
   throughout the app.
4. **Texture finish** (from §4). Note CSS techniques and any asset
   work needed.

Then, against §5 anti-patterns, audit the planned design: does it hit
3+ of the artificial signals? If yes, adjust before writing code.

Update the app's entry in `app_themes.py` to record these four
choices, so cross-portfolio uniqueness can be checked
programmatically.

---

## 8. The artificial-detection self-check

Before declaring an app ready for Phase 5 (pre-publish checks), ask
these questions and record honest answers:

1. If I lay this app's screenshots next to BallSortPuzzle's and
   WaterSortPuzzle's, does any random viewer see "different products" or
   "three games by the same publisher with the same template"?
   - Same template → fix Phase 1 before continuing
   - Different products → proceed

2. Does the app's menu say something specific to its mechanic, beyond
   the genre name?
   - "Sort the colored water!" → templated, fix
   - "Each tube wants only one color. Sort them. Find peace." → has voice

3. Is there a single visual element a user would recognize 1 second
   after seeing it (mascot, distinctive shape, signature color combo,
   unusual layout)?
   - No → add one
   - Yes → proceed

4. If I removed the title and app name, could a user tell which
   Pegasus Games app this is from a single screenshot?
   - No → too generic, add identity
   - Yes → proceed

If all four pass, the app has earned its identity. If any fail, return
to Phase 1 and refine.
