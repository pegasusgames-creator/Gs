# Quality Playbook

Design, UX, gameplay, and monetization guidance for every app in the Pegasus
Games portfolio. Referenced from `CLAUDE.md`.

Read this file when:

- Starting work on a new app or polishing an existing one
- Reviewing an app before release
- Asked to "improve" an app or "make it feel professional"
- Building out any screen that's currently just functional (menu, level complete, shop)

Each recommendation below is marked with its **genre scope**:

- `[ALL]` applies to every app in the portfolio
- `[GAMES]` applies to games only (puzzle, arcade, casual)
- `[TOOLS]` applies to utility apps (calculators, trackers, converters)
- `[KIDS]` applies only to apps targeting children

Each recommendation also has a **priority**:

- `P0` — do this before first publish; skipping this measurably hurts retention or revenue
- `P1` — do this within the first 2-3 update cycles
- `P2` — polish that compounds; do when time permits

---

## 1. Visual design

### 1.1 Color palettes [ALL, P0]

Every app's color palette must be **saturated and vivid**, not pastel/Material.
Pastels look medical and clinical. Casual app users associate vivid saturated
color with polish and fun.

**Bad** (desaturated/Material pastels):
```
red: #ff6b6b, blue: #4fc3f7, green: #66bb6a, yellow: #ffd54f
```

**Good** (vivid saturated):
```
red: #ef3a47, blue: #2196f3, green: #43c759, yellow: #ffc107
purple: #9c27b0, orange: #ff6f00, pink: #e91e63, teal: #00bcd4
```

Each app in the portfolio must still have a **distinct theme palette** (so the
6 flagship games don't look identical) — but within a theme, saturation should
always be high.

When rendering gradients on game objects (balls, tiles, blocks), the highlight
stop should be a **color-tinted lighter version**, not a white-washed version.
`lightenColor(hex, 60)` (pushes all RGB channels toward white) desaturates;
prefer multiplying by ~1.3 in HSL lightness instead, preserving hue.

### 1.2 Fonts [ALL, P0]

**Never use `Segoe UI`, `Arial`, or raw `system-ui` as the primary font.**
Segoe UI is a Windows font and simply doesn't exist on Android — the browser
falls back to a generic sans-serif which looks unbranded.

Use one of these free Google Fonts, embedded via `@font-face` from local
assets (not CDN — WebView loads from `file:///android_asset/`):

- **Fredoka** or **Fredoka One** — playful, rounded, ideal for game headers
- **Poppins** — clean modern, works for both UI and body text
- **Nunito** — soft rounded sans, good general-purpose
- **Rubik** — utilitarian, works for tool/utility apps

Pair: bold display font for titles + neutral sans for body. Never more than 2
font families per app.

### 1.3 Icons and emoji [ALL, P0]

**Never use system emoji as UI icons** (📅📋🛒📊🎮▶). They render differently on
every Android version, look inconsistent with the rest of the app, and are the
single clearest "indie / built quickly" signal.

Replace with either:
- Simple monochrome SVG icons matching the app's accent color
- Lucide icons (free, drop-in SVGs): https://lucide.dev
- Heroicons (free, drop-in SVGs): https://heroicons.com
- Custom drawn symbols in the app's visual style

Emoji IS fine in two places only: inside body/description text where it's
decorative (not functional), and in user-facing content the user explicitly
chooses (like a mood tracker where 😊 is a data value, not a UI button).

### 1.4 Visual polish baseline [GAMES, P0]

Every game screen should have:

- **Radial gradient fills** on game objects (balls, tiles, blocks) — not flat colors
- **White highlight** top-left of each object to simulate a light source (~30% opacity, ~30% size)
- **Subtle drop shadow** beneath held/active objects
- **Color-tinted glow** on selected state (not white glow)
- **Particle effects** on key events — match, merge, level complete, coin earned
- **Micro-animations** on every tap: scale to 0.95 on press, scale back to 1.0 on release, ~80ms each way

These are cheap to implement and are the difference between "HTML game in a
WebView" and "native-quality game."

### 1.5 Tall phone support [ALL, P0]

Modern Android phones are 20:9 to 21:9 aspect ratio. Every app must:

- Fill the full viewport height without dead zones
- Respect `env(safe-area-inset-top)` and `env(safe-area-inset-bottom)` for notch/gesture bars
- Scale game content proportionally, not fixed pixel sizes
- Test on Pixel 8 Pro (20:9) and Samsung S23 Ultra (19.5:9) equivalents in emulator before shipping

If the game has a canvas, it should re-measure on `resize` and `orientationchange`, not just on load.

---

## 2. First 60 seconds (onboarding)

The first 60 seconds decide whether a player keeps your app or uninstalls.
Getting this right matters more than any other feature.

### 2.1 Animated tutorial, not text [GAMES, P0]

**Never open with a text overlay explaining how to play.** Players don't read.
They dismiss and then don't know what to do.

Replace with an **animated finger pointer** showing the first move:

1. Show level 1 in a playable state
2. Wait 2 seconds so the player takes it in
3. Animate a translucent white hand tapping the source (source glows)
4. Animate the hand tapping the destination
5. Actually perform the move
6. Repeat if the player doesn't do it themselves within 5 seconds

The hand is a simple CSS/canvas element. It's 2-4 hours of work and is the
single biggest D1 retention improvement you can make.

### 2.2 First 3-5 levels must be trivial [GAMES, P0]

Level 1 must be winnable in **1-2 moves**. Levels 2-5 in 3-5 moves each. The
goal isn't challenge — it's giving the player the feeling of "I'm good at this"
before they've invested emotional energy.

Difficulty should ramp from level 6 onward, not level 1.

### 2.3 No friction walls in first 20 levels [GAMES, P0]

- **Lives should not decrement on failure for the first 20 levels.** Treat
  these as "tutorial levels." Players learning the mechanics will fail; that's
  normal; they shouldn't be locked out because of it.
- **No interstitial ads until after level 3.** First-session players seeing an
  ad before their first win uninstall at very high rates.
- **No IAP prompts in the first 5 levels.** The shop button can be visible but
  should not auto-open, and there should be no "Want to skip this level?" ads
  or popups.

### 2.4 First-session loot [GAMES, P1]

On first launch, give the player a small visible gift: 50-100 free coins, or
3 free hints, or a "Welcome pack" popup that grants a modest boost. Creates
the feeling of immediate value and seeds the coin economy.

---

## 3. Menu / home screen design

### 3.1 Hierarchy [ALL, P0]

Menu screens must have exactly **one dominant action**, not 2-3 competing
buttons. The hierarchy is:

1. **Primary** (Play, Start, Open): one large button, bright accent color, center
2. **Secondary** (Daily Challenge, Missions): two medium buttons side by side, muted
3. **Tertiary** (Shop, Stats, Themes, Settings): icon row at bottom or header

**Never make the Shop button visually dominant.** It signals "buy stuff before
you play," which hurts both retention and Google's automated "manipulative
design" review. Shop goes in the tertiary icon row, not the primary button
stack.

### 3.2 Progress cue on Play button [GAMES, P1]

The Play button should show the player's current state as subtext:

- Returning player: `▶ PLAY` / `Continue — Level 47`
- New player: `▶ PLAY` / `Start your first level`
- Completionist: `▶ PLAY` / `Level 47 — Top 25%`

This is a 30-minute change that noticeably improves D7 retention. Returning
players see their investment; new players see clear direction.

### 3.3 Daily features surface as banners, not menu items [GAMES, P1]

Daily Challenge, Daily Login Reward, Daily Missions should surface as
**pop-up banners on menu load** when there's a new one available, not as
buried menu buttons. After dismissing, they return to their regular menu spot.

The pop-up should auto-dismiss in 3 seconds if untouched, to avoid being
annoying for returning players who don't care.

### 3.4 Kill redundant destinations [ALL, P2]

If the Play button takes the player to their current level, a separate
"Levels" menu item is redundant for most users. Move level select into the
pause menu inside gameplay, or make it an icon. Fewer menu buttons = cleaner
hierarchy.

### 3.5 Tool/utility apps [TOOLS, P0]

For tool apps, the home screen IS the primary tool, not a menu. Open directly
to the calculator / tracker / converter. Menu / settings live behind an icon
in the header. The user's goal is to use the tool — don't make them navigate
to it.

### 3.6 List and card hierarchy in modals/panels [GAMES, P0]

Missions panels, daily-challenge lists, stats screens, achievement screens
and shop pages should NEVER read as "8 identical cards stacked." That's
the single most common signal of templated AI design.

**The mistake:** every item gets the same width, the same background tint,
the same internal layout (title + subtext + reward + progress). Eight of
them stacked = one giant beige rectangle with text lines. The user's eye
has nowhere to land.

**The fix — intentional visual hierarchy:**

1. **One featured item, top, larger.** The most important mission, today's
   challenge, the active offer — gets ~1.5× the height of regular items,
   a contrasting background tint, and possibly a glow or border. This is
   the item the player should notice first.

2. **Active items distinct from completed and locked.** Three states with
   visually different treatments:
   - **Active:** full color, progress bar visible, "Continue" or progress text
   - **Completed:** dimmed (60% opacity), checkmark icon, "Claimed!" text
   - **Locked:** grayscale, lock icon overlay, "Unlocks at level X"

   Don't render all three the same and just change a number. The eye
   should sort active vs completed vs locked in 0.3 seconds.

3. **Progress bars must show real progress.** "0/5" everywhere reads
   as broken. Capture screenshots from a state where some missions are
   1/5, some 3/20, one is fully complete. Show the progress system working.

4. **Variety in card density.** Not every card needs the same internal
   layout. Daily streak might be a horizontal pill of 7 day-circles.
   Coin reward might be a graphic of a chest. Trophy unlock might show
   the trophy art. Mix card content types so the panel doesn't feel
   like a database table.

5. **Use whitespace as separation, not just dividers.** Two missions
   stacked tight together with a 1px line between them blur into one
   visual object. 16-24px of empty space between cards reads as "two
   distinct items." For featured items, even more space above and below.

6. **Empty states must look intentional.** If a panel ends with empty
   space because there are no more items, fill that space with:
   - A summary card ("All daily missions complete! Come back tomorrow.")
   - A decorative element (mascot, illustration, abstract pattern)
   - A call-to-action ("Want more? Try Daily Challenge mode")

   Don't ship modals with 30% trailing empty cream/dark void.

**Example: Missions panel done right vs wrong**

Wrong (current Nonogram pattern, AI-ish):
```
[Season Pass — same width as missions, same card]
[Solver — Complete 5 puzzles — 30 coins — 0/5]
[Dedicated — Complete 20 puzzles — 80 coins — 0/20]
[Nonogram Pro — Complete 50 puzzles — 200 coins — 0/50]
[Streak Keeper — 3 daily challenges — 50 coins — 0/3]
[Coin Hoarder — Collect 100 coins — 40 coins — 0/100]
[Star Gazer — Earn 30 stars total — 60 coins — 0/30]
[Perfectionist — Solve a puzzle without errors — 25 coins — 0/1]
[No Hints — Solve 3 puzzles hint-free — 35 coins — 0/3]
[empty cream void to bottom of screen]
```

Right (designed):
```
═══════════════════════════════════════════
  TODAY'S CHALLENGE                  ★★★
  Solve 3 puzzles in under 5 minutes
  Reward: 100 coins + 1 free hint
  Progress: ●●○ (2/3)
═══════════════════════════════════════════

DAILY MISSIONS
─────────────
[Solver           progress 3/5  →  +30c]
[Dedicated        progress 12/20 →  +80c]
[Streak Keeper    progress 1/3  →  +50c]

WEEKLY MISSIONS  (refresh in 4d 2h)
─────────────
[Nonogram Pro     progress 17/50 → +200c]
[No Hints         progress 1/3  →  +35c]

✓ COMPLETED THIS WEEK
─────────────
[Perfectionist     ✓ claimed]
[Coin Hoarder      ✓ claimed]

─── Tomorrow brings new missions ───
```

The right version has: one featured today's-challenge with a distinct
treatment, missions grouped by frequency (daily/weekly), completed
section dimmed and pushed to bottom, footer message instead of empty
void, progress bars showing real progress not zeros.

**Check before shipping any modal/panel:**

- [ ] At least one item is visually distinct (featured, sized larger, or differently styled)
- [ ] Cards show real progress (NOT all 0/N)
- [ ] Active/completed/locked states are visually different
- [ ] No more than 5 visually-identical cards stacked
- [ ] Trailing empty space is filled with summary, mascot, or message
- [ ] Background tint of cards CONTRASTS with panel background (not "beige on beige")

If any fail, the panel reads as artificial. Redesign before shipping.

---

## 4. Gameplay feel

### 4.1 Haptics [ALL, P0]

Add `window.navigator.vibrate()` on key events. 10 minutes of work,
disproportionate impact on "native feel":

- Small tap (ball placed, button pressed): `navigator.vibrate(10)`
- Medium event (level complete, coin earned): `navigator.vibrate(50)`
- Celebration (star earned, milestone): `navigator.vibrate([30, 20, 30])`
- Failure (no moves, wrong move): `navigator.vibrate([20, 40, 20])`

Gate behind a "Haptics" toggle in settings (default on).

### 4.2 Audio [GAMES, P1]

Every game should have:

- **SFX on core actions** — tap, drop, match, level complete, coin earn
- **Background music toggle** (default off, because most players play muted — but should be available)
- All audio gated behind a settings toggle

Use Web Audio API with small (<10KB) synthesized sounds or tiny OGG files.
No external audio libraries. Audio mutes when the tab/app loses focus.

### 4.3 Selected / held states need to be obvious [GAMES, P0]

When a game object is selected or picked up, it must be **visibly distinct**
from unselected:

- Elevated (drop shadow)
- Slight scale up (~1.1x)
- Color-tinted glow matching the object's color
- Source dims (~70% opacity) to emphasize the transfer

Static glow alone is not enough. New players should see at a glance what's
"in their hand" vs. what's waiting.

### 4.4 Show valid drop targets [GAMES, P1]

When the player picks up an object, briefly pulse or outline every valid
destination. Accessibility win for learning players, accessibility for
experienced players who want to check their options.

Can be toggled off in settings as "Beginner Mode" — auto-disable after
level 30 if not explicitly enabled.

### 4.5 Responsive tap feedback [ALL, P0]

Every interactive element gets a `:active` / press state with:

- Scale down to 0.95
- Subtle color shift (darken accent by ~10%)
- ~80ms transition in, ~80ms back

Without this, the app feels dead. This applies to every button, every tile,
every tube — anything the user taps.

---

## 5. Progression and retention systems

### 5.1 Stars and mastery [GAMES, P0]

Every level must have a clear 3-star criterion, visible before and after play:

- **3 stars**: solve at or below par moves/time
- **2 stars**: solve within ~1.25x par
- **1 star**: just complete it

Par should be calculated from the level generator's optimal solve, not
hand-set. Show par on the game screen. Show the star breakdown on the level
complete overlay.

Players need a reason to replay completed levels. 3-star chase is the
strongest, simplest reason.

### 5.2 Level select shows mastery [GAMES, P1]

On level select, each completed level should show its star count (0-3). Add
a small badge to levels where the player is in the top 10% / 25% / 50% of
solvers. This surfaces the global comparison and drives replays.

### 5.3 Streaks and milestones [ALL, P0]

Every app should have a login streak counter that rewards the player for
returning. Rewards escalate for milestones:

- Day 1: small reward
- Day 3: medium + celebration animation
- Day 7: large + unlock something cosmetic
- Day 14: huge
- Day 30: exclusive unlock (theme, skin, badge)

Streaks should be protectable via a "streak saver" paid with in-game currency,
so a single missed day doesn't kill a long streak. This is a strong monetization
hook (players spend coins to preserve their streak → coins become valuable →
players consider buying coin packs).

### 5.4 Daily challenges [GAMES, P0]

Daily challenge concept: same level for all players worldwide, rotating every
24 hours. Features:

- Streak counter (consecutive days completed)
- Bonus coin reward for completion
- "X players completed today" social proof (can be fake-seeded for the first
  month; nobody will notice)
- Separate entry point from main progression (doesn't consume lives)

### 5.5 Daily missions [GAMES, P1]

3 fresh missions every 24 hours. Missions should be diverse:

- "Complete 3 levels" (easy, always achievable)
- "Solve a level in par moves" (skill, sometimes achievable)
- "Use 5 hints" (monetization vector — may trigger buying hint pack)

All three completed = bonus coin drop. Mission reset notification at midnight
local time.

### 5.6 Cosmetic unlocks [GAMES, P1]

Players unlock cosmetic themes / skins through progression milestones:
level 50, 100, 200, 350, 500. Gives long-term players something to chase
beyond levels. Cosmetics are free; they only unlock by playing. Paid
cosmetics come later (§6.4).

---

## 6. Monetization

### 6.1 Ad placement rules [ALL, P0]

Casual mobile standard, respect it:

- **No interstitials on first launch.** Ever. Guaranteed uninstall trigger.
- **No interstitials before the first level complete** in a new install.
- **Interstitial every 2-3 level completions**, not every one. Random within
  that range, not predictable.
- **Rewarded video, never interstitial, for player-helpful moments**:
  "Watch ad for 1 life," "Watch ad to undo," "Watch ad to double coins"
- **Banner always at the bottom**, never at the top. Never overlapping game canvas.
- **Ad-free grace period** for the first 3 sessions. User needs to bond with
  the game before being monetized.

### 6.2 Rewarded video is the primary monetization [ALL, P0]

For casual games, rewarded video typically earns 3-5x more per user than
interstitials, and users don't hate it. Build every system to have a rewarded
video option:

- Out of lives → "Watch ad for 1 life" (primary) + "Buy lives" (secondary)
- Stuck on level → "Watch ad for a hint" (primary) + "Buy hint pack" (secondary)
- Want more coins → "Watch ad for 50 coins" offer once per hour
- Level complete → "Watch ad to double your coin reward"

Always frame as *giving the player something*, not *interrupting the player*.

### 6.3 Time-limited starter pack [ALL, P0]

The single highest-converting IAP pattern in casual mobile:

1. Player installs, plays first session
2. On first shop visit OR after completing level 5, show a **one-time popup**
3. Popup contains a bundle: Remove Ads + 100 coins + 1-hour unlimited lives
4. Price: $0.99 (99¢ is the conversion sweet spot)
5. **Visible 24-hour countdown timer**
6. After timer expires, pack is gone forever
7. Never show this offer again to this player

Conversion on time-limited starter packs is 5-10x standard IAPs because of
loss aversion. This is the primary IAP for most casual apps.

### 6.4 Cosmetic sink for the coin economy [GAMES, P1]

Players accumulate coins and eventually have nothing compelling to spend them
on, which makes coins feel worthless and reduces motivation to buy coin packs.

Fix: sell cosmetic items (tube skins, ball styles, background themes) for
coins. Pure markup — costs nothing to produce, gives players a reason to
spend. Running low on coins after a cosmetic spree is what triggers coin
pack purchases.

### 6.5 Never use dark patterns [ALL, P0]

Never do any of these. They hurt long-term revenue and attract Google's
manipulative-design review:

- Pre-selected "Continue with ad" / confirmation bypasses
- Countdown timers on purchase decisions that are purely fabricated
- Hidden cancel buttons or tiny X icons on popups
- "You lost 500 coins! Buy more?" after a failure
- Auto-opening the shop after level fail
- Fake "limited quantity" on digital goods

Honest, clear monetization performs better over 30+ days than predatory
monetization performs in the first week.

### 6.6 Subscription [GAMES, P2]

The `season_pass_monthly` subscription ($1.99/mo) should offer sustained
value, not a one-time boost:

- 2x coins on every level for the subscription period
- Daily free hint (1/day)
- Exclusive monthly cosmetic
- No ads during the sub period

Avoid subscriptions that feel like rent-seeking. If the player's experience
gets worse when the sub expires (vs. not-better-than-baseline), they'll churn
and rate 1-star.

---

## 7. Store listing and screenshots

### 7.1 Screenshot order [ALL, P0]

The Play Store shows the first 3 screenshots in search results. Those 3 have
to sell the game. Order:

1. **Gameplay mid-action** — a dramatic in-progress state showing what the
   player does. Not the menu. Not an empty board.
2. **Level complete celebration** — stars, particles, coin reward. Shows the
   emotional payoff.
3. **Progression / themes / variety** — shows long-term content (many levels,
   unlockable themes).
4-8. Various gameplay, features, daily challenge, missions, stats.

Never lead with the menu screenshot. Never lead with the shop screenshot
(signals monetization-first).

### 7.1.5 Capture quality — what to actually show inside the frame [ALL, P0]

The marketing-frame wrapping (`wrap_screenshots.py`) gives you the
gradient and headline, but the SCREENSHOT INSIDE the frame is what
users evaluate. May 2026 Puzzle2048 audit found six common capture
failures, each producing a screenshot that looks unfinished even with
a perfect wrap:

**Empty / sparse boards.** Capturing level 1-2 of a puzzle when the
board is mostly empty wastes screenshot real estate. Per §7.1, slot 01
("deep gameplay") must show the LARGEST grid the level generator
produces, in mid-progression state, NOT a tutorial-tier early board.

**"How to Play" tutorial overlay visible.** The tutorial appears on
fresh installs and dismisses on first tap. If captured before
dismissing, the tutorial sits over the entire board and blocks the
gameplay you're trying to show. See §7.1.5.5 below for the seed
script that prevents this.

**Default first-install state ("0/0/0 everywhere").** Stats screen,
Missions screen, and Daily Challenge all show "0 levels played, 0
coins, 0 streak" on a fresh install. Reads as "developer forgot to
populate sample data." See §7.1.5.5.

**Tiny content in tall canvas.** Phone captures are 1080×2400 (9:20).
A 4×4 puzzle grid centered in that canvas leaves 60% of the screenshot
as dead space. The marketing-frame wrap doesn't fix this — the
screenshot inside the frame is still mostly empty. The in-app
gameplay layout must scale the playable area to fill tall phones (per
§1.5).

**Modals over darkened backgrounds.** Capturing a modal (Daily
Mission panel, Stats popup) shows a dark scrim over the menu behind.
The result is muddy and low-contrast. For modals, capture in a
dedicated screenshot mode where the background is replaced with the
app's solid theme color. See §7.1.5.4.

**★ NEW (Puzzle2048 May 2026 audit) — Same raw screenshot used in
multiple slots.** The pre-wrap raw captures must be VISUALLY DISTINCT
across the 7 slots. The Puzzle2048 audit found 7 wrapped screenshots
using only 2 distinct raw images: tap sequences in
`capture_screenshots.py` were missing target buttons, so 5 slots all
captured the same early-game board. Result: 7 different headlines
("REACH 2048", "NEW HIGH SCORE", "WEEKLY EVENT", "BEST TILES BEST
RUNS", "ONE FREE UNDO") over visually identical content — every claim
the headline made was a lie about what the screenshot showed.

`pre_publish_check.py check_screenshot_uniqueness` enforces this:
perceptual hashes of all 7 phone raws must differ by at least 4
hamming distance from each other. Identical or near-identical raws
across slots = blocking.

When this check fails, `capture_screenshots.py` taps are missing their
targets. Common causes:
- Tap coordinates assume a default Pegasus menu layout that this
  app doesn't use — set per-app overrides at
  `<App>/test/screenshot_taps.json`
- Emulator screen size differs from the script's assumed dimensions
  — check `adb shell wm size` and adjust DEFAULT_SCREEN_W/H
- Animations haven't settled before tap fires — increase post_delay
  per slot

The capture script ALSO checks this on the fly now and refuses to
continue past the first duplicate.


#### 7.1.5.5 Pre-screenshot localStorage seed (MANDATORY)

Every app gets a per-app file at `<App>/test/seed_screenshot_state.js`
containing localStorage assignments that pre-populate realistic
mid-game state. Without this, screenshots show fresh-install zeros
across Stats / Missions / Daily and the tutorial overlay covers the
gameplay screen.

**The seed script must use THIS app's actual localStorage keys** —
not a generic template. Every app's `game.html` has different storage
keys. Read the keys from the actual game code before writing the seed.

For Puzzle2048 specifically (real schema confirmed by reading
`game.html:defaultState()` — the keys live INSIDE one JSON blob keyed
`puzzle2048_save`, not as individual `p2048_*` keys):

```javascript
localStorage.setItem('puzzle2048_save', JSON.stringify({
  score:                247,
  bestScore:            512,
  highestTile:          128,
  achieved2048:         false,
  coins:                85,
  lives:                5,
  maxLives:             5,
  undoPack:             3,
  dailyChallengeDate:   new Date().toISOString().slice(0, 10),
  dailyChallengeStreak: 7,                  // shows on Best screen
  dailyChallengeBest:   320,
  // … rest of defaultState() schema
}));
// Achievements stored separately under 'ls_v2'; daily missions under
// '2048_missions_v1' (date-keyed). See Puzzle2048/test/seed_screenshot_state.js
// for the canonical seed used by capture_screenshots.py.
```

Generic-template seeds with keys like 'coins' or 'streak' will silently
do nothing if the app's actual keys are different. The May 2026 audit
caught this exact failure: a seed referencing `p2048_*` keys never
touched the real `puzzle2048_save` blob, so all captures showed fresh-
install zeros. Always grep `localStorage.setItem` and `localStorage.getItem`
in the actual game.html before writing the seed. Verify after seeding
by capturing slot 02 (menu) and confirming the displayed Score / Best /
Best Tile / coin count match the seeded values.

### 7.1.6 Headline ↔ image content match (MANDATORY) [ALL, P0]

Every wrapped screenshot is a TWO-PART CLAIM: the headline says X is
in the app, and the image must SHOW X is in the app. Screenshot 4 with
headline "WEEKLY EVENT 5 GAMES / Play five rounds this week" sitting
above an image of an early-game board with no event UI visible is
false on its face — the header asserts a feature the image doesn't
demonstrate.

**Required check before each app ships:** for each headline in
`metadata/screenshot_headlines.json`, verify the image at the
corresponding slot ACTUALLY SHOWS the feature claimed:

| Headline claim | Image must show |
|---|---|
| "DAILY CHALLENGE" | the daily mode UI mid-play, NOT the menu |
| "WEEKLY EVENT" | the weekly event panel/banner, NOT generic gameplay |
| "BEST TILES BEST RUNS" / Stats | the Stats screen, NOT a generic board |
| "ONE FREE UNDO" | an undo button visible OR a board state mid-undo |
| "NEW HIGH SCORE" | the score-celebration UI, NOT a quiet gameplay screen |
| "LEVEL COMPLETE" | the Level Complete modal with stars, NOT mid-play |

Numerical / capability claims still apply (these were the original
§7.1.6 rule and they remain in force):
- "500 LEVELS" → the level generator must produce ≥500 unique solvable levels
- "DAILY CHALLENGE" → the daily challenge mechanic must actually be implemented
- "OFFLINE PLAY" → the app must work fully without network (test with airplane mode)
- "25×25 GRIDS" → the largest level the generator produces must be ≥25×25
- "NO ADS" → the app must have no AdMob integration (different setup; rare)

If headline says it, image must show it. Otherwise either:
- Re-capture the slot with the correct screen content
- Change the headline to describe what's actually visible

This is part of SHIP_GAME §8.2 and is non-negotiable. Mismatches are a
Play Store Misleading Behavior policy risk and will be caught by
reviewers.

For Puzzle2048 May 2026 audit, 5 of 7 slots had this defect. Fix
before re-uploading.

### 7.2 Screenshot text overlays [ALL, P0]

Text overlays are fine if they clarify the screen, not if they oversell.

**OK**: "500 Levels", "Daily Challenge", "Unlock 6 Themes", "Sort by Color"

**Not OK** (prohibited by Google/Apple policy):
- "#1 Game", "Best Puzzle", "Top Rated"
- "Download Now", "Install Now", "Play Now"
- "50% Off", "Limited Time", "Free for today"
- Fake awards ("App of the Year 2025")
- "Million Downloads"

Text should be short (≤4 words), in the app's brand font, placed outside the
core game area so the actual gameplay is visible.

### 7.2.1 Header typography spacing [ALL, P0]

The marketing wrap header has three components stacked vertically:
headline line 1, headline line 2, subtitle. The vertical gaps between
them must respect the relative weights of the typography.

**Required gaps as fractions of canvas height (1080×2400 phone, 1200×1920
tablet 7", 1800×2560 tablet 10"):**

| Element pair | Phone gap | Tablet gap |
|---|---|---|
| Line 1 → Line 2 | 1.5% (~36px) | 1.5% |
| Line 2 → Subtitle | 4.0% (~96px) | 3.5% |
| Subtitle → device frame | 2.5% (~60px) | 3.0% |

The Puzzle2048 May 2026 audit found subtitle sitting too close to
the second headline line (descender of "EVERY RUN" almost touched the
subtitle). Root cause: the legacy 2.0% gap between line 2 and
subtitle didn't account for heavy display-font descenders at 140-180px
sizes.

The 4.0% gap is the new minimum. Heavier or italic display fonts
should bump to 4.5%. Tighter wrappers may try to reclaim the space —
don't. The breathing room is what makes the header read as designed
rather than crammed.

### 7.3 Tablet screenshots [ALL, P0]

**Every app gets phone, 7" tablet, AND 10" tablet screenshots.** No
exceptions, no per-tier scaling, no "skip for long-tail." If an app
ships, it ships with all three sets.

| Set | Resolution | Slot count | Required |
|---|---|---|---|
| Phone | 1080×2400 | 7 | YES |
| 7" tablet | 1200×1920 | 7 | YES |
| 10" tablet | 1800×2560 | 7 | YES |

The reasoning is operational: if the wrap pipeline supports tablets at
all (and it does — `wrap_tablet_screenshots.py` exists), then the
marginal cost per app is the cost of capturing tablet raws, which is
~10 minutes once the tablet AVD is configured and the app's tap
overrides are dialed in. That's worth it because tablet Play Store
listings without tablet screenshots get the "Phone screenshots only"
warning badge in some Play Store surfaces and rank lower for tablet
searches.

The previous "phone running in a tablet canvas" behavior — where
`wrap_tablet_screenshots.py` silently rescaled phone raws into tablet
aspect — is a worse outcome than no tablet screenshots at all, and is
now blocked by the resolution check added in May 2026.

**Tablet captures are SEPARATE captures.** A tablet emulator running
the same app produces a fundamentally different in-app layout —
wider boards, different HUD positioning, side panels in some games,
larger touch targets. The captures must come from a tablet AVD, not
from the phone AVD with phone raws rescaled.

**Required tablet AVD setup (one-time per machine):**

```
# In Android Studio AVD Manager, create two AVDs:
#   pegasus_tablet_7   — Pixel C profile or similar, 1200×1920 portrait
#   pegasus_tablet_10  — Nexus 10 profile or similar, 1800×2560 portrait
# Or via command line:
avdmanager create avd -n pegasus_tablet_7 -k "system-images;android-34;google_apis;x86_64" --device "pixel_c"
avdmanager create avd -n pegasus_tablet_10 -k "system-images;android-34;google_apis;x86_64" --device "Nexus 10"
```

Then `capture_screenshots.py --target tablet_7` and `--target tablet_10`
boot the matching AVD. Tap coordinate fractions usually still work
across phone/tablet because they're proportional, but per-app
verification is required because tablet UI sometimes shifts buttons
to side panels. Per-app tap override files at
`<App>/test/screenshot_taps.json` may need separate `tablet_7_*` and
`tablet_10_*` keys.

**`wrap_tablet_screenshots.py` rejects phone-resolution raws** as of
May 2026. Trying to wrap a 1080-wide phone capture into a tablet
canvas fails with an explicit error rather than producing the
"phone running in a tablet emulator" look that Puzzle2048 shipped in
April 2026.

**Migration plan for existing apps shipped without tablet screenshots:**
the 5 flagships (WaterSort, Nonogram, PipeConnect, Puzzle2048,
UnblockPuzzle) need full re-captures including tablet sets before any
v1.x update ships. Long-tail apps need tablet captures included in
their first SHIP_GAME run; no ship without all three sets.

### 7.4 Emoji and special glyphs in game.html [ALL, P1]

Many app icons and inline glyphs in game.html use Unicode emoji
codepoints (✨ ❤ ⚡ 🎯). When the device's font stack doesn't include
that emoji codepoint, the system renders a "tofu" rectangle (□) instead.
The Puzzle2048 May 2026 audit caught this on the menu's bottom
icon row and the weekly-event banner's coin glyph.

**Three options to prevent emoji fallback failures:**

1. **Replace emoji with inline SVG.** Most reliable; scales cleanly,
   no font dependency. Heavier in code but only ~200 bytes per glyph.
2. **Use Twemoji or Noto Color Emoji as a webfont** loaded inside
   game.html. Adds ~100-300KB but covers the whole emoji range.
3. **Stick to the safe codepoints:** ✓ ✗ ★ ☆ ♥ ♦ ◆ ◇ ● ○ — basic
   geometric shapes that virtually every system font supports. No
   color but always renders.

For new Pegasus apps, default to option 3 (safe codepoints) for inline
glyphs. Use option 1 (SVG) for the icon row of buttons because those
need to be distinct + recognizable at small sizes, where geometric
shapes are too generic.

NEVER use emoji in store listing copy — Play Store's editorial review
is uneven about emoji rendering across crawl tools and may flag listings.

### 7.5 Unique screenshots per app [ALL, P0]

Every app needs its own screenshot set showing THAT app's content. Never
reuse a screenshot template across apps with just the title/icon swapped —
this is one of the clearest Google spam-classifier signals.

If you use a design template (backgrounds, frames, text positions), the
actual gameplay screenshot inside the frame must be from each app
individually.

### 7.6 Icon principles [ALL, P0]

- Single clear focal element (one ball, one symbol, one game piece)
- High contrast against background
- Recognizable at 48x48 (icon size on Android home screen)
- No text in the icon (except possibly 1-2 letters like "2" for 2048)
- Distinct from the genre's most popular icons (don't ape Ball Sort's icon
  for a ball sort game — differentiate)
- Colored background, not white (stands out in the store grid)

Test: take your 512x512 icon, resize to 48x48, look at it on your own home
screen among your other apps. If it looks like a blob, redesign.

### 7.7 Description structure [ALL, P0]

Every full description follows the format used by current top-grossing
analogs (Royal Match, Block Blast, Water Sort variants — verified Apr 2026
by reading their live Play Store listings):

```
[OPENING HOOK — 1-2 sentences, opens with "Welcome to" or a strong
verb, names the player benefit, uses a brand emoji or "🧩" / "🎮"]

[HOW TO PLAY section — 3-4 bulleted steps, plain language]
🎮 HOW TO PLAY:
• Drag and drop X onto the Y
• Match Z to clear lines / sort colors / etc.
• Plan your moves to maximize score / minimize moves
• No time limit — play at your own pace

[FEATURES section — 6-10 bullets, EACH with leading emoji]
✨ FEATURES:
🔥 Classic Mode — endless play with increasing difficulty
🏆 Level Mode — complete 500+ challenging puzzles
🎯 Daily Challenges — fresh puzzle every day
📊 Global Leaderboard — compete with players worldwide
💎 Stunning Graphics — beautiful designs, smooth animations
🎵 Relaxing Music — calming background sounds
🌙 Dark Theme — easy on the eyes for night play
📴 Offline Play — no WiFi needed!

[KEYWORD-DENSITY section — purposefully repeats "offline games" /
"no wifi games" / "no internet games" 3-5 times. ASO play, not
elegance. Block Blast does this and it works.]
🌐 Play anywhere, anytime
Block Blast is designed for players who love offline games and want
fun without interruptions. If you are searching for no internet games,
this is a great choice for relaxing, passing time, and enjoying a
smart puzzle challenge wherever you are.

[PRO TIPS section — 3-5 short tips, treats player as someone leveling up]
✨ PRO TIPS:
• Plan ahead: visualize moves to keep board open
• Maximize combos: clear multiple lines for bonus
• Master the streak: consistent clears boost your score

[CLOSING — 1-2 sentences, casual, invites download without "Download
now" CTA which is banned]
🔥 Ready to test your brain? Discover why players love [App Name]
as their favorite [genre] game.
```

Strictly avoid:
- "#1", "Best", "Top Rated", "Award winning" — Google bans these
- "Download now", "Install now" — Google bans these
- "% off", "$X.XX value" — Google bans these
- Generic openers: "Welcome to [AppName]!" repeated across apps
  (template-fill detector trips on this — see CLAUDE.md anti-suspension
  safeguard #6)
- Keyword stuffing of brand names ("X Game, X Puzzle, X Challenge,
  X Adventure...")
- Repeating the app title more than 3 times

Specifically required for puzzle game listings:
- Reference ASMR / "satisfying" / "relaxing" / "stress-relief" at least
  once — this is what users search for in the genre
- Mention "offline" / "no wifi" / "no internet" at least 3 times across
  the description — proven ASO play in casual genre
- Specific numbers ("500 levels", "thousands of puzzles", "100+ themes")
  — vague claims convert worse

For utility/quiz/reference apps, replace gameplay sections with:
- HOW IT WORKS (instead of HOW TO PLAY)
- WHAT'S INCLUDED — bullet list of categories or feature scope
- Skip PRO TIPS section (utility users don't level up at calculation)

### 7.7.1 Hard rules — failure modes the May 2026 audit found in 5 of 5 flagships [ALL, P0]

The Royal-Match-format spec above existed in this playbook for months
and Claude Code still produced apps that failed it. So: hard rules,
checked by `pre_publish_check.py check_listing_floor` (added May 2026):

**Minimum length: 500 characters.** A 97-byte description ("2048 Puzzle
is the ultimate number merging game that's easy to learn but
impossible to put down!") or a 157-byte stub is below the casual-puzzle
floor and signals "abandoned app" to Google's listing-quality classifier.
Apps with sub-500-char descriptions will not rank.

**The opening line must be a HOOK, not a preamble.** Specifically the
opening must NOT be:

- An encyclopedia definition ("A nonogram is a logic grid…")
- A mechanic restatement ("Slide the colored blocks out of the way…")
- A category description ("a deeply satisfying, calming puzzle game")
- A genre cliché ("the ultimate X game, easy to learn but impossible
  to put down")
- A "Welcome to [AppName]!" template-fill

The opening must contain at least one sensory verb (Pour, Slide, Mark,
Trace, Watch, Feel, Chase, Fuse) and at least one specific outcome the
player will experience in the first thirty seconds (a click, a
satisfaction, a reveal, a streak). If those two requirements aren't met
in line 1, redo the opening before continuing.

**Honest claims only.** If the listing says "500+ LEVELS", `LEVELS.length`
in `game.html` must equal or exceed 500. If it says "ASMR", the §6 ASMR
audit must pass 2/3 (sound + haptic + animation). False numerical claims
are a Play Store Misleading Behavior policy trigger, not a stylistic
quibble. The May 2026 audit caught one of these (UnblockPuzzle screenshot
06: "500+ JAMS" with `LEVELS.length === 150`). Don't repeat it.

**Required keywords for casual puzzle apps.** Description must include
at least 4 of: `relaxing`, `satisfying`, `ASMR`, `offline`, `brain`,
`free`. Each must be honest — see ASMR rule above. Audit found all
5 audited apps missing 3+ of these.

When writing or rewriting a listing, run through this self-check
before saving:

- [ ] First line opens with a sensory verb, not a definition
- [ ] First line names a specific outcome the player will feel
- [ ] Total length ≥ 500 characters
- [ ] Includes ≥ 4 of the 6 required puzzle keywords (when applicable)
- [ ] Every numerical claim is verifiable in `game.html`
- [ ] No banned phrases (#1, Best, Download now, % off, etc.)

If any item fails, revise. This isn't optional polish — these were the
exact gaps Claude Code's May 2026 audit found in every audited app.

### 7.8 Short description (80 chars) [ALL, P0]

This is the single most-read piece of copy in the whole store listing. It
appears in search results and the app header.

Format: **[Verb] + [what] + [qualifier]** in 80 characters.

**Good**:
- "Sort colored balls into tubes. 500 brain-teasing levels." (54 chars)
- "Connect every pipe to win. 200 levels of flow puzzle fun." (56 chars)

**Bad**:
- "The best ball sorting game you've ever played!" (banned language, vague)
- "Ball Sort Puzzle by Pegasus Games — Free to play!" (wastes chars on name)

---

## 8. Technical polish

### 8.1 Load performance [ALL, P0]

First paint must happen within 1 second on mid-range Android (Moto G, Pixel
6a). If the app shows a blank/black screen for more than 1 second on launch,
drop rates spike.

- Keep `game.html` under 200KB (your current flagship games are 130-160KB — good)
- No external CDN fetches (all assets local)
- Lazy-load assets that aren't needed for the first screen
- Defer ad SDK initialization until after first paint

### 8.2 Offline play [ALL, P0]

Every game in the portfolio must be fully playable offline. The only network
calls should be:

- Ad requests (graceful fallback if offline)
- Analytics (batch and retry, never block UI)
- Firebase config (optional, cached)

No game logic should ever depend on network. "No internet" must never block
the player.

### 8.3 State persistence [ALL, P0]

Every game event (level complete, coin earned, streak incremented) must
persist to `localStorage` **immediately**, not on exit. App crashes happen,
users force-kill, Android kills background apps. If any of these lose progress,
players churn.

Write to `localStorage` in the same function that updates game state. Never
batch writes "at end of session."

### 8.4 Back button handling [ALL, P0]

Android hardware back button must always do something sensible:

- On game screen: go back to menu (with confirm if mid-level with progress)
- On menu: minimize app (not exit)
- On sub-screens (shop, stats): go back one level

Exposed via `MainActivity.java` calling a JS function; each game's JS
implements a back-button handler.

### 8.5 Portrait lock [GAMES, P0]

Every game locks to portrait orientation unless there's a specific landscape
gameplay reason. Landscape is unexpected and unwanted in casual mobile.

Verify `android:screenOrientation` is NOT set in AndroidManifest.xml (removing
this was done in `fix_all_apps.py` — don't add it back), and handle orientation
at the CSS/JS level with `@media (orientation: landscape)` showing a "Please
rotate to portrait" overlay.

---

## 9. Cross-promotion

### 9.1 "More Games" bar [ALL, P0, from app #2 onward]

Every app from the second one onward must have a "More Games" panel in
the menu (icon in the tertiary row) that opens a list of other Pegasus
Games apps with deeplinks to the Play Store.

This is the single best monetization lever a portfolio publisher has
that single-app devs don't. A user who plays one of your games and is
about to churn can be converted into a user of another one, at zero
cost.

### 9.2 Dynamic cross-promo config [ALL, P0]

The list of "More Games" entries must NOT be hardcoded inside each
app's `game.html`. If hardcoded, updating the list (e.g., adding a new
app, promoting a hit, removing a deprecated app) requires rebuilding
and re-uploading every shipped app — economically infeasible at 30+
apps, and Google Play update reviews delay it by days each.

Instead, fetch the cross-promo list from a remote JSON file at app
launch:

**URL**: `https://pegasusgames-creator.github.io/promo.json`

**Format**:
```json
{
  "version": 14,
  "games": [
    {
      "id": "ballsort",
      "packageId": "com.pegasusgames.ballsort",
      "name": "Ball Sort Puzzle",
      "desc": "Sort colorful balls into tubes!",
      "icon": "https://pegasusgames-creator.github.io/icons/ballsort.png",
      "featured": false,
      "weight": 1.0
    },
    {
      "id": "watersortpuzzle",
      "packageId": "com.pegasusgames.watersortpuzzle",
      "name": "Water Sort Puzzle",
      "desc": "Pour and sort colored water!",
      "icon": "https://pegasusgames-creator.github.io/icons/watersort.png",
      "featured": true,
      "weight": 2.0
    }
  ]
}
```

**Fields:**
- `id`, `packageId`, `name`, `desc`: standard cross-promo entry data
- `icon`: small icon URL hosted on GitHub Pages (PNG, square, ≤256×256)
- `featured`: if `true`, display this app in a hero slot at the top of
  the More Games panel with a "FEATURED" badge — used to promote hit
  apps across the portfolio
- `weight`: relative ordering weight (higher = appears earlier in the
  list); ties break by `id` alphabetical

**Behavior in app:**
- On app launch, fetch `promo.json` with a 3-second timeout
- If fetch succeeds, cache to `localStorage` with key `promo_config_v1`
- If fetch fails (offline, GitHub Pages outage, etc.), fall back to
  the cached version, or to the baked-in list as last resort
- Filter out the current app from the list (don't promote yourself)
- Render in the More Games panel ordered by `weight` desc

The baked-in fallback list is a snapshot of the JSON at the time the
app was built. Update it when ad-hoc rebuilding, but the dynamic fetch
is the source of truth.

**Why this works for the "hit app promotes losers" strategy:**
When one app starts converting well, you mark it `featured: true` and
bump its `weight` to 5.0 in the GitHub Pages JSON. Within hours, every
other app in the portfolio surfaces it as the hero promoted app. If
the hit is doing 5,000+ daily new installs, even a 1% click-through
on the hero slot drives 50+ daily installs per other app, free.

Conversely: when a low-quality app needs to be hidden (you've shipped
v1 but want to push v2 with better assets first), set its `weight` to
0 in `promo.json`. It disappears from the panel without any code
changes.

### 9.3 Hit app — portfolio-wide upgrade workflow [ALL, P1]

When one app starts performing meaningfully better than the rest
(e.g., D7 retention 2x portfolio average, install velocity 10x, IAP
conversion 3x), trigger a portfolio-wide upgrade pass:

1. **Mark the hit app `featured: true`** in `promo.json` with `weight: 5.0`
2. **Identify what's working** in the hit app — is it the icon? the
   first-60-seconds flow? the screenshot order? a specific monetization
   pattern? Read the analytics/AdMob data carefully.
3. **Ship the working pattern across the portfolio.** Specifically:
   - If the hit app's icon style is converting well, regenerate icons
     for the worst-performing apps using the same style elements
   - If the hit app's screenshot 1 is driving installs, update other
     apps' screenshot 1s to match the composition (different content,
     same composition pattern)
   - If a specific listing copy structure is winning, apply it to
     other listings (each one still hand-written to that app)
4. **Re-upload the upgraded apps** at a sustainable pace (2-3 per week
   per the cadence rules — don't dump 20 updates at once, that's a
   different velocity-spike trigger).

This is how the strategy works: the hit app pulls free traffic, the
upgraded prior apps convert that traffic better, the portfolio
compounds. Without this workflow, a hit just sits as one earner and
the rest of the portfolio is dead weight.

### 9.4 Organic rewards for installing other apps [ALL, P1]

Consider rewarding coins for installing another Pegasus Games app.
The reward triggers only after the user opens the new app at least
once (verify via Firebase Analytics event). Usually 50-200 coins per
install is right (don't go higher — Google's policy on "incentivized
installs" is gray; transparent small rewards are accepted, large
rewards approach manipulation).

This must be transparent ("Earn 50 coins by installing X"), not
deceptive.

### 9.5 What NOT to do [ALL, P0]

- Don't promote 10+ apps in the More Games panel. Cap at 6-8. Beyond
  that, users skim past. Use `weight` and `featured` to curate.
- Don't include apps with crash rate > 1% in the promo list. A user
  going from your stable app to a crashy one churns from both.
- Don't include suspended or unpublished apps. Filter at the JSON
  level — never relying on each app's local cache to know.
- Don't promote apps that violate Google's Families policy from a
  general-audience app, or vice versa. If you ship Kids apps, they
  need a separate `promo-kids.json` with only Kids-program-eligible
  apps in it.

---

## 10. App-specific guidance

The Pegasus Games portfolio spans multiple app types with fundamentally
different optimization profiles. Trying to apply puzzle-game quality
rules to a BMI calculator is wasted effort. Trying to skip them on a
flagship puzzle game is revenue-destroying. Use the right rules for
the app type.

### Portfolio-shape map

The portfolio breaks down approximately as:
- **~30 puzzle games** (BallSort, WaterSort, Nonogram, BlockPuzzle,
  PipeConnect, Puzzle2048, UnblockPuzzle, BrickBreaker, BubbleShooter,
  ColorBlockJam, FruitMerge, MahjongSolitaire, KnotPuzzle, etc.)
- **~12 quiz apps** (FlagQuiz, GeographyQuiz, FootballQuiz, EmojiQuiz,
  CapitalCities, MentalMathQuiz, etc.)
- **~22 utility / calculator apps** (BMICalculator, AgeCalculator,
  LoanCalculator, BillSplit, BudgetPlanner, MedicationReminder, etc.)
- **~10 reference / hobby apps** (CocktailGuide, GuitarChords,
  AnimalSounds, MorseCode, DartsScorer, etc.)
- **~6 kids apps** (ABCLearning, BasicMathKids, KidsColoring, KidsPiano,
  KidsDrum, CountingApp)
- **~4 timer / utility games** (DontTapWhite, FlappyBird, DiceRoller,
  CoinFlip)

These compete with completely different sets of analogs. Quality bar
and feature scope must reflect that. This section maps each type to
its real-world priorities.

### 10.1 Puzzle games — flagship tier [GAMES, P0]

**Real analogs:** Royal Match, Block Blast, Magic Sort, Nonogram.com,
Easybrain Sudoku. These compete on retention, live ops, and IAP funnel.

**Mandatory:**
- Daily challenge (§5.4)
- Par-move system (§5.1)
- Undo button (1 coin or free with rewarded video)
- Hint button (5 coins or free with rewarded video)
- Themes/skins unlockable through progression (§5.6)
- Streak system (§5.3)
- Time-limited starter pack with countdown (§6.3)

**Strongly recommended for the 1-2 designated flagship apps:**
- Mascot / character (M2 or M3 from APP_ARCHETYPES.md) — 100%
  artificial-feeling without one
- Meta-loop beyond level-clearing — castle restoration / theme
  collection / character progression
- 2-week content drop cadence (50 new levels / new theme / new event)
- Global leaderboard (Firebase Realtime DB)
- 2-3 concurrent live events (tournament, speed challenge, collection)
- Explicit ASMR / "satisfying" / "relaxing" audio design

**Designated flagship apps get full quality treatment.** Other puzzle
games in the portfolio meet the mandatory bar but skip the recommended
list. A solo dev cannot run live ops on 30 puzzle games. Pick 1-2 to
be hero, the rest are portfolio filler with cross-promo to the heroes.

### 10.2 Quiz apps [QUIZ, P0]

**Real analogs:** Logo Quiz Ultimate, World Geography Quiz, Movie Quiz —
the dozens of quiz apps that rank by depth-of-content + ASO.

**Quality bar:**
- ≥200 questions (Google ranks quiz apps partly by depth claimed in
  description; "200+ questions" should be honest)
- Categorized rounds (Easy / Medium / Hard, or thematic categories)
- Immediate "next question" flow — no menus between questions
- Share-your-score to social media
- Daily challenge with one question (low effort, drives retention)
- Listing copy emphasizes COUNT and BREADTH ("500 flag questions! All
  countries! Includes territories!")

**Skip:** mascot, meta-loop, leaderboards, live events, sophisticated
monetization. Quiz apps make money from search ranking + AdMob impressions
during gameplay, not from IAP funnels. A user playing FlagQuiz spends
3 minutes per session and shows 2 ads. That's the entire revenue model.

### 10.3 Calculator/converter apps [TOOLS, P0]

**Real analogs:** Calculator++ (50M+ installs, dev: Calculator++ Team),
Loan Calculator (CCSwe AB, 10M+), Currency Converter (50M+, etc).

**Quality bar:**
- Open directly to the tool, no menu (§3.5)
- Single screen — input, result, history. No tabs, no walkthrough.
- Correct math (this IS the entire product — bugs here = 1-star reviews)
- History of recent calculations (scroll to revisit)
- Unit/mode switcher in header, not a separate menu
- Banner ad at bottom, never interstitials (users close fast; interstitials
  on close = uninstall)
- Optional $1.99-2.99 IAP to remove banner

**Skip:** mascot, leaderboard, meta-loop, daily challenge, streaks,
themes, archetype self-check (the §10.3 rules ARE the archetype),
tutorial (a calculator doesn't need onboarding). All over-engineering
for a tool.

**Revenue model**: 30 utility apps × 100 installs/day each × 3 banner
impressions/session × $5 eCPM ≈ $45/day from one fresh install
cohort, compounding as installs accumulate. The math works because
each app is cheap to produce.

### 10.4 Tracker apps [TOOLS, P0]

**Real analogs:** Habit Tracker (CoBan Co, 5M+), Daylio Mood Tracker
(50M+), Zero Fasting (10M+).

**Quality bar:**
- Privacy-first messaging in description ("All data stays on your device.
  No account. No sync. Your data is yours.")
- Privacy first in implementation — no sync, no account, no server
- Clear data export (CSV / JSON) as a free feature
- "Delete all my data" button in Settings
- Streak mechanics ARE appropriate (users want to build habits)
- No interstitials between entries — users enter data multiple times
  per day; interstitials cause immediate uninstall
- Lock screen widgets / quick-add shortcuts where possible

**Quiz/calculator advice for monetization applies** (banner only, IAP
to remove ads, skip leaderboards/heroes/etc.) — but the data
ownership / privacy framing matters more for trackers than for any
other app type.

### 10.5 Kids apps — Designed for Families program [KIDS, P0]

**Real analogs:** Bini Bambini, Khan Academy Kids, Sago Mini.

Different rulebook entirely. Subject to Google's Designed for Families
requirements:

- **Mascot/character is non-negotiable.** ABCLearning without a
  friendly character is dead-on-arrival. M2 or M3 from APP_ARCHETYPES.
  This is one of the few cases where commissioning real character art
  (or DALL-E/Replicate) is justified.
- **No behavioral ads.** Only contextual / non-personalized, explicitly
  configured in AdMob.
- **No IAPs without parent gate.** Parent gate = simple math problem or
  "press and hold for 3 seconds" before any purchase flow.
- **COPPA compliance.** No data collection beyond absolute minimum.
  Data Safety form reflects this (no advertising IDs).
- **No external links** without parent gate. No social, no email, no web.
- **No push notifications.** Forbidden by Google Play Families program.
- **Native-speaker translation review** required before shipping (per
  TRANSLATIONS.md §5).
- **Age-appropriate content rating**: pass IARC at "Everyone" / "3+".
- **No dark patterns, ever.** Kids apps get reviewed strictly; one
  violation = removal.

If building a kids app, read Google Play's Families Policy in full
before starting, not after.

### 10.6 Reference / hobby apps [REFERENCE, P0]

**Real analogs:** All Recipes (10M+), Guitar Tuna (50M+), genre-specific
top apps with niche but loyal audiences.

**Quality bar:**
- **Data completeness is the entire product.** "200 cocktail recipes
  with photos" is the pitch. Half-finished is dead.
- Search / filter is mandatory (users come knowing what they want)
- Favorites / bookmarks
- Offline access to full database (no cloud fetch per item)
- Listing copy emphasizes COMPLETENESS and SPECIFICITY ("Every IPA-style
  cocktail. Every guitar chord in every key. All 50 US state birds.")

**Skip:** mascot, daily challenge, streaks, leaderboards, IAP funnels.
These apps rank on ASO + completeness and stay there. Limited revenue
ceiling but cheap to make and sticky for the niche audience.

### 10.7 Mini-games / hyper-casual [GAMES, P0]

**Real analogs:** Flappy Bird (the original spawned dozens), DontTapWhite-
style reflex games. Ad-supported, low retention, viral spike potential.

**Quality bar:**
- Single-screen game, no menu navigation
- Score-based, infinite play
- Aggressive interstitial cadence (every 2-3 deaths) — these are the
  one app type where high ad density is expected and tolerated
- "Beat your high score" is the entire meta-loop
- Share-score-to-social as a deliberate viral hook

**Skip:** levels, missions, IAP funnels, mascot, themes. These are
20-second-loop ad-impression machines. Optimize for that.

---

## 11. Notifications

Push notifications are one of the strongest retention tools in casual mobile —
and one of the fastest ways to earn 1-star reviews if done wrong. The payoff
curve is steep in both directions. Handled well, notifications lift D7
retention by 10-20%. Handled badly, they drop it by the same amount *and*
train users to permanently disable notifications from the entire portfolio.

All notifications in this portfolio are **local** (scheduled via Android's
AlarmManager through `NotificationHelper`). We do NOT use Firebase Cloud
Messaging or server-side push — it adds privacy surface, requires token
collection to be declared in Data Safety, and provides no benefit for this
type of casual app.

### 11.1 Permission handling [ALL, P0]

Android 13+ (API 33) requires explicit `POST_NOTIFICATIONS` runtime permission.
Asking wrong loses the opt-in forever — users who deny once almost never
reverse in Settings.

**Never request notification permission on first launch.** First launch is
about letting the user experience the app. Asking for permission cold = ~30%
opt-in; asking after positive bonding = ~65% opt-in.

**Correct flow:**

1. First session: no permission request. User plays.
2. **After first level complete** (or first equivalent positive milestone in
   non-game apps), show a custom in-app pre-prompt overlay:
   *"Want us to remind you about your daily challenge and streak? You can
   change this anytime in Settings."*
   Two buttons: [Enable Notifications] and [Maybe Later].
3. Only if user taps "Enable" → trigger the system permission dialog.
4. If user dismisses or taps "Maybe Later" → do not re-prompt for at least
   7 days. After 7 days, may re-prompt ONCE more after another positive
   moment. Never a third time.

This "soft ask before hard ask" pattern is standard industry practice
because it dramatically outperforms cold system prompts.

### 11.2 Notification types [GAMES, P0 unless noted]

Only implement these types. Adding other types has never materially improved
retention and almost always hurts it.

**Daily reminder [P0]** — one gentle reminder per day that something is
waiting in the app.

- **Time**: Evening of user's local timezone, 18:00-21:00 (the "I'm bored,
  something casual to do" window). For kids apps (§10.4): skip daily
  reminders entirely — inappropriate for under-13.
- **Content example**: "Your daily challenge is ready 💧" — vague teaser,
  not specific instruction.
- **Smart skip**: If the user opened the app that day already, cancel the
  scheduled notification for today. Implement via `AlarmManager.cancel()` on
  every app launch and re-schedule only if today's hasn't fired.
- **Frequency**: Exactly once per day. Not morning AND evening. Not twice.

**Streak-at-risk [P0]** — the highest-converting notification type.

- **Only if** user has a login streak of ≥3 days (below 3 days there's
  no emotional investment to leverage).
- **Time**: ~20:00-21:00 local time on a day the user hasn't yet opened
  the app. Fires only if the streak will break if they don't play today.
- **Content example**: "Your 7-day streak ends in 4 hours — keep it alive! 🔥"
- **Never fabricate streaks**. If the user doesn't actually have one, don't
  send. Fake urgency is the #1 cause of 1-star reviews mentioning
  notifications.

**Lives refilled [P1]** — fires when a user ran out of lives earlier and
their lives have now regenerated.

- Only if the user hit the "no lives" wall during the previous session
  (not just anyone whose lives were below max).
- Fires exactly once per refill cycle.
- Content example: "Your lives are back! Ready for another round? ❤️"

**Return-after-absence [P1]** — fires for users who were active but have
been away 3 days.

- **3 days absent**: one soft notification. Content: "We have new daily
  challenges for you. 🌊"
- **7 days absent**: one last-chance notification. Content: "It's been a
  while — come back to where you left off."
- **After day 7**: STOP. Do not send another notification to a churned user.
  They'll uninstall out of spite. Silence is the correct behavior.

**New feature / new content [P2]** — only a few times per year, when
shipping a meaningful update (new theme pack, new level pack, seasonal event).

- Content example: "New winter theme available ❄️"
- Global broadcast to active users. Never to absent users — re-engagement
  of churned users via feature pushes has terrible conversion.

### 11.3 Notifications to never send [ALL, P0]

- **Morning notifications** (before 9am local time). Waking someone up to a
  game notification earns an immediate mute.
- **More than 1 notification per day, ever.** The second notification on the
  same day triggers the user to disable notifications for the app — often
  permanently.
- **Notifications to users who already played today.** Pointless and
  annoying.
- **Fake urgency.** "Only 2 hours left!" on things that aren't actually
  expiring. Loss-aversion manipulation attracts app reviews that explicitly
  mention it and tank your rating.
- **Emotional manipulation copy.** "We miss you!" / "Don't you love us
  anymore?" / "Your tubes are lonely." Users find these cringe-inducing.
- **Vibration or sound at night.** All notifications scheduled for after
  21:00 must be silent (no vibrate, no sound). Use Android's
  `NotificationCompat.PRIORITY_LOW` for evening notifications.
- **Notifications when the app is in foreground.** Suppress them if the
  user is actively in the app.
- **Kids app daily reminders.** Children should not have apps pinging them
  to return. See §10.4.

### 11.4 Settings toggle [ALL, P0]

Settings screen must include a top-level toggle:

- **"Daily Reminders" (default ON, if permission was granted)**

One toggle is enough — don't add separate toggles for each notification type.
More toggles = more user confusion = more users disabling everything.

If the user disables the toggle, cancel all scheduled alarms via
`AlarmManager.cancel()`. If they re-enable, re-schedule the daily reminder
for the next appropriate window.

### 11.5 Measurement [ALL, P1]

Fire a Firebase Analytics event on three moments:

- `notification_scheduled(type)` — when a notification is queued
- `notification_fired(type)` — when it actually displayed (requires
  WorkManager or BroadcastReceiver logging)
- `notification_opened(type)` — when tapping the notification launched the
  app (track via intent extras)

After a month of data, check the open rate per type. Any type with <5% open
rate is annoying users more than helping — disable it.

### 11.6 Data Safety implications [ALL, P0]

Local notifications (AlarmManager) do NOT require any additional Data Safety
declarations. The notification scheduling happens entirely on-device — no
tokens, no server calls, no personal data leaves the device.

If ever migrating to FCM (not recommended for this portfolio), you would
need to declare:
- Device or other IDs → FCM token
- Purpose: Analytics + App functionality

### 11.7 Tools / utility apps [TOOLS, P0]

Tool apps (calculators, converters, trackers) should NOT have daily
reminders at all. Users open a calculator when they need a calculator. A
daily reminder to "use your calculator" is absurd and leads to uninstalls.

**Exception**: habit/mood/sleep/fasting trackers legitimately benefit from
daily reminders (the whole point of the app is to encourage a daily habit).
For these, implement the same daily-reminder pattern as games, but:
- Let user pick the time (their preferred habit time, not evening)
- Allow multiple reminder times per day if it's a multi-event tracker
  (meal tracker, medication tracker)
- No streak-at-risk notifications — don't guilt users about health habits

### 11.8 Kids apps [KIDS, P0]

Kids apps must NOT send any notifications. This is a Google Play Families
policy requirement. Children are a protected audience and receiving app
notifications is age-inappropriate. If the app targets Kids (ABCLearning,
KidsPiano, BasicMathKids etc.), disable notification scheduling entirely —
not just daily reminders, all notifications.

---

## 12. What NOT to do

Quick-reference list of things that will hurt the portfolio:

- Don't add features nobody asked for. Feature count does not equal quality.
- Don't ship a game with fewer than 50 levels (looks thin in the store).
- Don't ship a utility app under 8KB of game.html (flagged as min-functionality).
- Don't use Lorem Ipsum, placeholder text, or obvious stub content anywhere.
- Don't leave `TODO` comments in production code (ship with real implementations or cut the feature).
- Don't reuse screenshots, icons, or listing copy across apps. Frame
  templates and brand backgrounds CAN be reused — what cannot be reused is
  the inner gameplay shown in screenshots, the icon's focal element, or
  any of the listing text.
- Don't skip the IAP plumbing even for a free-to-play app (you want the
  option to add IAPs later without shipping an update).
- Don't A/B test by shipping different builds — use Play Console store
  listing experiments instead.
- Don't ignore your crash rate. 1% ANR or 1% crash rate will get you
  delisted from search results. Check weekly in Play Console.
- Don't ship multiple apps in a single calendar day, even if they're
  genuinely distinct. Spread releases across the week. Same-day publish
  spikes are a velocity signal even when content is fine.
  See `CLAUDE.md` → "Shipping cadence".
- Don't ship 2+ apps from the same genre cluster within 7 days (e.g. two
  ball-sort variants in the same week). Diversify across genres weekly.
- Don't accelerate cadence abruptly. 1, 2, 2, 2, 2, 3 across 6 weeks is
  fine; 1, 1, 5 is a velocity-spike flag.
- Don't add push notifications to a brand-new app in its v1.0 release.
  Ship the v1.0 without notifications, verify production stability, then
  add notifications in v1.1+. This lets you measure whether notifications
  actually lift retention vs. confounding it with other launch-day
  variables. See §11 for full notification rules.

---

## 13. Per-app review checklist

Before release, verify every item for the specific app:

**Visual**
- [ ] Saturated/vivid color palette, not pastel (§1.1)
- [ ] Custom font loaded, no Segoe UI fallback (§1.2)
- [ ] No system emoji as UI icons (§1.3)
- [ ] Gradients, shadows, particles on game objects (§1.4)
- [ ] Tall-phone aspect ratio verified (§1.5)

**First session**
- [ ] Animated tutorial, not text (§2.1)
- [ ] First 3-5 levels solvable in 1-5 moves (§2.2)
- [ ] First 20 levels don't consume lives (§2.3)
- [ ] No interstitial in session 1 (§2.3)
- [ ] First-session gift on launch (§2.4)

**Menu / navigation**
- [ ] One dominant Play button, others secondary (§3.1)
- [ ] Play button shows progress subtext (§3.2)
- [ ] Shop is not the second-brightest element (§3.1)
- [ ] Back button goes somewhere sensible (§8.4)

**Gameplay feel**
- [ ] Haptics on taps, successes, failures (§4.1)
- [ ] Selected/held states visibly distinct (§4.3)
- [ ] Active press state on every button (§4.5)

**Progression**
- [ ] 3-star criterion per level, visible (§5.1)
- [ ] Daily challenge hooked up (§5.4)
- [ ] Login streak with milestones (§5.3)
- [ ] Cosmetic unlocks at level milestones (§5.6)

**Monetization**
- [ ] Rewarded video options on every helpful moment (§6.2)
- [ ] Time-limited starter pack implemented (§6.3)
- [ ] No dark patterns (§6.5)
- [ ] IAP plumbing present even if ads-only launch (§12)

**Notifications** (may ship in first update, not required v1.0)
- [ ] Permission requested only AFTER first level complete, not on launch (§11.1)
- [ ] Daily reminder scheduled for 18:00-21:00 local time, with same-day skip (§11.2)
- [ ] Streak-at-risk notification for streaks ≥3 days only (§11.2)
- [ ] Notifications scheduled after 21:00 are silent (no vibrate/sound) (§11.3)
- [ ] Never more than 1 notification per day (§11.3)
- [ ] Settings toggle for "Daily Reminders" (default ON with permission) (§11.4)
- [ ] Kids apps: notifications fully disabled (§11.8)

**Technical**
- [ ] Offline playable (§8.2)
- [ ] State persists on every event (§8.3)
- [ ] Portrait lock via CSS (§8.5)
- [ ] Load to first paint < 1 second (§8.1)

**Store listing**
- [ ] Screenshot 1 = gameplay mid-action, not menu (§7.1)
- [ ] No banned phrases in screenshot text (§7.2)
- [ ] Screenshots unique to this app (§7.3)
- [ ] Icon recognizable at 48x48 (§7.4)
- [ ] Short description is verb + what + qualifier ≤80 chars (§7.6)

**Cross-promotion**
- [ ] "More Games" panel linking other Pegasus Games apps (§9.1)

Every item is blocking for a "polished" release. For a "shippable MVP"
release, only P0 items are blocking. P1 items are the next update; P2 items
are polish when time permits.
