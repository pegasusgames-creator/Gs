# Shipping a Game — End-to-End Workflow

**This is the master release workflow.** When the user says any of:

- "ship `<AppName>`"
- "release `<AppName>`"
- "prepare `<AppName>` for release"
- "get `<AppName>` ready for the Play Store"
- equivalent phrasing in any language

…Claude Code follows this document end to end without asking clarifying
questions. Only stop and ask if a hard blocker is hit (see "Hard
blockers" at the bottom).

---

## The principle

**Maximize what Claude Code can do alone. Minimize what the human has to
do.** When the human's input is required (filling Play Console forms,
clicking buttons in AdMob), generate a single hand-off document with
every value pre-filled and labeled so they paste, not type.

The user's debt pressure is real. They don't want to babysit each step.
Don't ask "should I do X?" — read the playbook, infer, do. Surface
decisions only when policy or safety actually require it.

---

## Phase 0 — Pre-flight (5 min)

Before touching the app, verify the foundation:

1. **Read these files in order if not already in context for this session:**
   - `CLAUDE.md` (project rules)
   - `QUALITY_PLAYBOOK.md` (quality bar)
   - `NOTIFICATIONS_IMPL.md` (only if game will ship with notifications)

2. **Verify the app folder exists and isn't blocked:**
   - `<AppName>/` directory present
   - Not on `BLOCKED_APPS` list in `pre_publish_check.py` (the 33
     placeholder clones). If on the list, the game.html must be rewritten
     in Phase 1 before anything else.

3. **Check current state of the app:**
   ```
   ls <AppName>/                        # confirm structure
   ls <AppName>/store/                  # what assets exist
   ls <AppName>/metadata/en-US/         # what listing copy exists
   wc -l <AppName>/android/app/src/main/assets/game.html
   ```
   Decide: is this a fresh app needing everything, or a partial app
   needing only some pieces? Make a written plan listing the missing
   pieces. Skip Phase steps for things that are already done correctly
   and pass the playbook checklist.

---

## Phase 0.5 — Cadence and genre check (1 min)

This is a quick safety check before committing time to Phase 1.

1. **List apps shipped or in active prep this week.** Look at git log for
   recent `versionCode 1` commits (new apps), or check `WaterSort/`,
   `Nonogram/`, etc., for AABs built in the last 7 days.

2. **Determine the current app's genre.** Use these clusters:
   - **Sort/pour puzzles**: BallSort, WaterSort, ColorSort, FruitSort
   - **Match/merge**: Match-3, Triple Match, Merge games, 2048 variants
   - **Connect/path puzzles**: PipeConnect, Nonogram, Bridges, Maze
   - **Word puzzles**: Wordle clones, Word Search, Crossword, Anagram
   - **Block/Tetris-style**: Block Blast, Wood Block, Sliding Tiles
   - **Logic grids**: Sudoku, Kakuro, Hitori, Picross, Skyscrapers
   - **Solitaire/cards**: Klondike, FreeCell, Spider, Mahjong
   - **Casual arcade**: Snake, Flappy, Stack, Helix
   - **Brain/memory**: Memory Match, Simon, Reaction tests
   - **Find/spot**: Hidden Object, Find the Difference, Spot It

3. **Check this week's mix.** If there's already a shipped or
   in-prep app from the same cluster within the last 7 days, **stop
   and surface to the user**. Recommend swapping to a different
   cluster for this week's second app. Per CLAUDE.md "Anti-suspension
   safeguards" rule #1: one app per cluster per 7-day window.

   Don't auto-pick a different app. The user decides. Frame:
   "Nonogram is in the Connect/path cluster, same as PipeConnect
   shipped 3 days ago. Suggest swapping to a Word, Logic grid, or
   Casual arcade game for this week's second slot."

4. **If the proposed app is a fresh cluster for this week**, proceed
   to Phase 1.

---

## Phase 1 — Game logic (the only step that can't be automated by template)

This is the part that requires real design thinking. Don't shortcut it.
The most common failure mode here: producing yet another app that fits
the Pegasus Games template (hero Play button, dark gradient, neutral
voice). Avoid this by completing the archetype-selection exercise
below before writing any code.

### 1.1 Decide the game's core mechanic

It must be genuinely different from every other shipped Pegasus Games
app. If the user said "ship Sudoku" the mechanic is decided. If the
user said "ship a puzzle game" ask what mechanic — that's the one
acceptable clarifying question at this phase.

### 1.2 Pick the four design archetypes (MANDATORY)

Open `docs/APP_ARCHETYPES.md` and pick one option from each of:

- **Layout archetype** (§1) — A through I. Check `app_themes.py` to see
  what other shipped apps use; pick a different one. **Do not pick
  Archetype A (template) unless this is a small utility app where it's
  genuinely best.** Per APP_ARCHETYPES §1, no more than 30% of shipped
  apps may use Archetype A.

- **Mascot pattern** (§2) — M0 through M4. Aim for the portfolio
  allocation: M0=30%, M1=30%, M2=20%, M3=10%, M4=10%. If shipping a
  flagship game, pick at least M1.

- **Copy voice** (§3) — V1 through V8. **Do not pick V1 (neutral
  functional)** for a flagship app. Match the voice to genre and
  audience but ensure variety across the portfolio.

- **Texture / finish** (§4) — T1 through T8. **At least 60% of shipped
  apps must NOT be T1 (flat clean) by month 6.** Currently 100% are.
  Pick something other than T1 unless the genre demands it.

Write these four choices down in `<AppName>/metadata/app_identity.md`
along with a 2-3 sentence description of the resulting feel. Example:

```markdown
# UnblockPuzzle Identity

- Layout: F (direct-to-game minimal)
- Mascot: M0 (no mascot — the blocks are the personality)
- Voice: V4 (snarky / dry) — "Try not to get stuck this time"
- Texture: T4 (wood grain on board, blocks have subtle wood grain too)
- Mood string: hardcore-classic-wood

The app should feel like a wooden puzzle box you'd find in a hipster
coffee shop. Spare, tactile, slightly intimidating. Not for casual
audiences — for players who actually like sliding-block puzzles.
```

### 1.3 Update the theme registry

Update or add this app's entry in `scripts/app_themes.py` to record
the four archetype choices. The schema:

```python
"<AppName>": {
    "bg_top_left": (...), "bg_top_right": (...), "bg_bottom": (...),
    "text_primary": (...), "text_accent": (...), "text_subtle": (...),
    "footer_tint": (...),
    "mood": "...",
    "layout_archetype": "F",       # from APP_ARCHETYPES §1
    "mascot_pattern": "M0",        # from APP_ARCHETYPES §2
    "voice": "V4",                 # from APP_ARCHETYPES §3
    "texture": "T4",               # from APP_ARCHETYPES §4
},
```

### 1.4 Audit against artificial-feel anti-patterns

Per APP_ARCHETYPES §5, the design plan must NOT hit 3 or more of these
anti-patterns:

- Center-aligned everything
- Same icon set as other apps
- All caps headlines on every screen
- Generic templated currency icon
- Identical button shapes / sizes / spacings to other apps
- Symmetric vertical column layout
- Generic "Level Complete!" celebration
- Same loading/transition patterns as other apps
- Identical settings screen structure

If 3 or more apply, redesign before writing code. This is the most
important step in this whole document. Apps that hit 3+ anti-patterns
read as templated AI output to actual users.

### 1.5 Write `<AppName>/android/app/src/main/assets/game.html`

Following the playbook. Default required features for any GAME (not
TOOL/TRACKER) are below — but the chosen archetype from §1.2 may
override or replace some of them. For example, if Layout = B
(map/journey), the "Hero menu + 2 secondary buttons + icon row" rule
doesn't apply because there's no menu. If Layout = F (direct-to-game),
many menu-related features are skipped.

Default feature set (override per archetype):
- Vivid color palette per `app_themes.py` entry
- Local Poppins font (4 weights in `assets/fonts/`) §1.2
- SVG icons throughout, NO emoji as UI §1.3 — and NOT the same SVG icons
  as other apps; vary icon family (line vs filled vs hand-drawn) per
  app per APP_ARCHETYPES §5
- Animated tutorial on first level §2.1
- First 3-5 levels trivially solvable §2.2
- First 20 levels don't decrement lives §2.3
- Hero menu + 2 secondary buttons + icon row §3.1 (UNLESS layout
  archetype overrides — see §1.2)
- Progress subtext under Play button §3.2 (UNLESS archetype overrides)
- Haptic feedback on key events §4.1
- Distinct held/selected state §4.3
- Tap micro-animations §4.5
- 3-star criterion per level §5.1
- Daily challenge §5.4
- Daily missions §5.5
- Login streak §5.3
- Cosmetic unlocks at level milestones §5.6
- Rewarded video options on every helpful moment §6.2
- Time-limited starter pack scaffolded §6.3
- More Games panel linking other Pegasus apps §9.1
- Settings: SFX/music/haptics toggles, reset progress, theme picker
  (with section ordering and labels appropriate to the chosen voice)
- localStorage state persistence on every event §8.3
- Offline-first §8.2
- Portrait lock §8.5

The voice from §1.2 controls all UI copy: button labels, modal
headers, tutorial text, push notification text. Don't write generic
copy then "translate" to the voice — write in the voice from the start.

The mascot from §1.2 must appear in the appropriate moments: if M2,
the mascot has 2-3 expressions and shows up on level complete + game
over + daily intro. If M3, the mascot lives on the gameplay screen
with idle animation.

### 1.6 Verify all levels are completable

The level generator must guarantee solvability. If it's a procedural
generator, embed a solver that runs against generated levels and
rejects unsolvable ones. If handcrafted, every level needs a known
solution. Test plan:
- Run a script that loads the game.html in a headless browser, plays
  every level by calling the in-game solver via JS, confirms each
  completes
- Or, embed `window.__verifyAllLevels()` in the game.html that returns
  a list of any failed levels. Call it from a Node.js test runner.
- Document the verification command in `<AppName>/test/verify.sh` so
  it can be re-run any time.

5. **Verify all buttons work.** Walk every screen path:
   - Menu → Play → in-game → pause → resume → win/lose
   - Menu → Daily Challenge → in-game → result
   - Menu → Levels → pick → play → return
   - Menu → Shop → each IAP triggers the buy flow stub
   - Menu → Stats / Missions / Settings / More Games / each back button
   - Settings → each toggle persists across reload
   - Watch-ad buttons trigger the rewarded ad stub
   - All confirm/cancel/X close buttons work
   This is hand-verified by reading each `onclick` handler. If any
   handler is missing or empty, fix before proceeding.

6. **Confirm folder name matches `<title>` tag and `android:label`.**

---

## Phase 2 — Wrapper integration (mostly templated)

1. **Create per-app package directories under
   `<AppName>/android/app/src/main/java/com/pegasusgames/<lowername>/`.**
   `<lowername>` is the lowercase no-spaces version of the app name.

2. **Copy and rename `MainActivity.java` and `NotificationReceiver.java`**
   from `_template/` (or from a known-good source app like
   BallSortPuzzle) into the new package directory. Update the `package`
   statement on line 1 of each file.

3. **Update `applicationId` in
   `<AppName>/android/app/build.gradle`:**
   ```
   applicationId "com.pegasusgames.<lowername>"
   versionCode   1
   versionName   "1.0.0"
   ```

4. **Update `android:label` and AdMob `APPLICATION_ID` in
   `<AppName>/android/app/src/main/AndroidManifest.xml`.** The AdMob
   APPLICATION_ID is a placeholder until Phase 4 — leave it as
   `__ADMOB_APP_ID_PLACEHOLDER__` for now. Same for the AppLovin SDK key
   meta-data — disable it (wrap in `if (false)` in MainActivity) until
   AppLovin is approved.

5. **Generate `<AppName>/keystore.properties`:**
   ```
   storeFile=../keystores/pegasus-upload.keystore
   storePassword=<from environment or vault>
   keyAlias=pegasus-upload
   keyPassword=<from environment or vault>
   ```
   Use the SAME upload keystore as Ball Sort and WaterSort (the one with
   SHA1 starting `EC:24:33:14:46`). All Pegasus Games apps share this
   upload key — that's the standard publisher pattern.

6. **Run `init_app_metadata.py <AppName>`** to scaffold the metadata/
   and store/ folders if not already present.

---

## Phase 3 — Visual assets (fully automated, MANDATORY per app)

**This phase is non-negotiable for every app.** A common Claude Code
failure is to skip the wrapping step and ship raw device screenshots,
producing the unprofessional "white text on dark navy" look that
identifies the app as low-effort indie work. The Play Store grid is
where install-conversion is won or lost — every app gets the full
treatment.

All scripts below take an `<AppName>` argument and pull the per-app
color theme from `app_themes.py`. Run from the repo root, NOT from
inside the app folder:

```
cd <REPO_ROOT>
python3 gen_icon.py <AppName>
python3 gen_feature.py <AppName>
python3 wrap_screenshots.py <AppName>
python3 wrap_tablet_screenshots.py <AppName>
```

That's it. No script cloning, no inline editing, no manual color
adjustment. The theme registry handles per-app variation.

### Step 3.1 — Capture raw device screenshots first

Before wrapping, raw screenshots must exist at:

```
<AppName>/store/screenshots/phone/raw/01.png  (deep gameplay, ~60-80% board fill)
<AppName>/store/screenshots/phone/raw/02.png  (early-mid gameplay, simpler)
<AppName>/store/screenshots/phone/raw/03.png  (level complete celebration)
<AppName>/store/screenshots/phone/raw/04.png  (daily missions / similar)
<AppName>/store/screenshots/phone/raw/05.png  (stats / progression)
<AppName>/store/screenshots/phone/raw/06.png  (levels list)
<AppName>/store/screenshots/phone/raw/07.png  (menu)
```

#### Step 3.1.1 — Pre-screenshot state seeding (MANDATORY)

Before capturing, the game's localStorage MUST be pre-seeded with realistic
mid-game state. Otherwise the Stats / Missions / Levels screenshots show
"0/0/0" everywhere and look like a broken fresh install.

Create `<AppName>/test/seed_screenshot_state.js` containing:

```javascript
// Seeds localStorage with mid-game state for screenshot capture.
// Run this in headless Chromium BEFORE navigating to each modal/screen.
window.localStorage.setItem('coins', '247');
window.localStorage.setItem('currentLevel', '23');
window.localStorage.setItem('streak', '7');
window.localStorage.setItem('starsEarned', '34');
window.localStorage.setItem('totalSolved', '17');
// Mission progress (use the mission key names from your game.html):
window.localStorage.setItem('mission_solver_progress', '3');     // 3/5
window.localStorage.setItem('mission_dedicated_progress', '12'); // 12/20
window.localStorage.setItem('mission_streak_progress', '1');     // 1/3
window.localStorage.setItem('mission_perfectionist_done', 'true');
// Recently-played levels (for level select screen):
window.localStorage.setItem('completedLevels', JSON.stringify([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]));
window.localStorage.setItem('threeStarLevels', JSON.stringify([1,2,3,5,6,8,11,15]));
```

Adjust the keys to match what the actual `game.html` reads. Run this
script before each headless capture so the captured screen has real
data populated. If the game's localStorage schema doesn't match these
keys, update the seed script — the goal is "every visible number reflects
mid-game state, not zeros."

#### Step 3.1.2 — Pick the right level/state for each screenshot

For puzzle games where board complexity grows with level number:

- `01.png` (deep gameplay): pick a level number that produces the
  LARGEST board the game generates AND in mid-progression state (not
  blank, not nearly-solved). For Nonogram with grids up to N×N, capture
  level 30+ in the middle of solving. For Sudoku, capture a near-
  complete grid. For sort puzzles, capture with several tubes nearly
  done.
- `02.png` (early-mid): a level around 8-15 in early-progression state.
  Demonstrates the same mechanic at lower complexity.

For all screenshots, the playable area must occupy at least 50% of
the captured 1080×2400 canvas. If your in-app layout doesn't scale to
fill tall phones, FIX THAT FIRST per QUALITY_PLAYBOOK.md §1.5 — don't
ship screenshots with 60% empty space.

#### Step 3.1.3 — Modal screenshots without the darkened scrim

For screenshots showing modals (Daily Missions, Stats, Level Complete,
Shop), don't capture the modal-over-darkened-menu state. Reasons in
QUALITY_PLAYBOOK §7.1.5.

The game.html should support a query parameter like
`?screenshot=modal_missions` that, when set, renders the modal on a
clean background using the app's theme color directly — no scrim, no
faded menu visible behind. Each captured modal needs this clean-bg
render.

#### Step 3.1.4 — Mission/list screen population check

Per QUALITY_PLAYBOOK.md §3.6, modals showing lists of missions/items
must demonstrate visual hierarchy: featured item, active items with
non-zero progress, completed items with checkmarks, locked items
grayed out.

Before capturing the missions screenshot, verify the captured screen
shows:
- At least one featured/highlighted item visually distinct from others
- At least 2 missions with non-zero progress (1/5, 12/20, etc.)
- At least 1 completed mission visually different (checkmark, dimmed)
- NOT 8 identical cards stacked with all-zero progress

If the captured screen looks like 8 identical beige cards with 0/N
everywhere, the seed script didn't run or the in-app layout doesn't
implement hierarchy. Fix before continuing — this is the #1 "looks
AI-ish" signal.

Capture method (Pegasus Games uses Android emulator via adb — produces
real Android WebView output with proper font rendering and mobile chrome,
not desktop Chromium approximations):

```
python3 scripts/capture_screenshots.py <AppName>
```

What the script does:
1. Boots the user's Android emulator if not already running
   (`emulator -avd <name>` against the first installed AVD)
2. Waits for boot complete (up to 90s)
3. Builds and installs the app's debug APK from
   `<App>/android/app/build/outputs/apk/debug/app-debug.apk`
   (you must build it first: `cd <App>/android && ./gradlew assembleDebug`)
4. For each of 7 slots:
   - Force-stops and re-launches the app (clean menu state)
   - Sends a tap sequence via `adb shell input tap` to navigate to the
     target screen (Play, Daily Challenge, Levels, Stats, etc.)
   - Waits for animations to settle
   - Captures via `adb shell screencap` and pulls the PNG
5. Writes to `<App>/store/screenshots/phone/raw/01.png` through `07.png`

### Tap coordinates

Tap fractions for the default Pegasus Games menu layout (hero Play
button at 50%/50%, Daily Challenge at 50%/62%, icon row at 50%/72%) are
hardcoded in `DEFAULT_TAPS` at the top of `capture_screenshots.py`.

For apps with non-default layouts (Layout B = map/journey, Layout F =
direct-to-game, etc.), create a per-app override at
`<App>/test/screenshot_taps.json` with the correct tap sequence for
each slot. Format:

```json
{
  "01_deep_gameplay": [
    ["tap", 0.50, 0.50, 1500]
  ],
  "06_levels_grid": [
    ["tap", 0.85, 0.10, 1000],
    ["tap", 0.50, 0.50, 1500]
  ]
}
```

### Per-slot quality verification

After running, OPEN each output PNG and verify per the §3.6 iterative
checklist (mobile proportions, board fills canvas, no zeros, mid-
progression, hierarchy in panels). If any slot captured the wrong
screen, fix the tap fractions and re-capture just that slot:

```
python3 scripts/capture_screenshots.py <AppName> --slot 04
```

If the emulator wasn't running and you want to use one you're
launching manually:

```
python3 scripts/capture_screenshots.py <AppName> --no-launch
```

If the script can't find an APK to install:
```
cd <App>/android
./gradlew assembleDebug
cd ../..
python3 scripts/capture_screenshots.py <AppName>
```

### Why emulator, not headless Chromium — and why this is non-negotiable

**Store screenshots are emulator-only. Headless Chromium / Puppeteer captures
are forbidden.** This is a blocking policy, not a preference.

Headless desktop Chromium can render `game.html` but produces output that
looks like "browser tab," not "phone screen": different font rendering
pipeline, no Android status bar / system insets, no real WebView init,
desktop-style flexbox quirks (canvas-wrap collapsing, footers floating
off-place). The output reads as low-effort indie work on the Play Store
grid — exactly the failure mode the wrap script is supposed to prevent.

The emulator runs the actual APK through real Android initialization and
produces the correct mobile look. It also gives the app a chance to
populate localStorage organically — if the emulator has been used for
testing before, the app already has level progress, coin balances, and
other realistic mid-game state baked in.

**Rules:**

- The canonical capture command is `python3 scripts/capture_screenshots.py
  <App>` (boots an AVD if none is running, installs the debug APK, sends
  adb tap sequences, pulls screenshots via `screencap`).
- **Never write or re-run a Puppeteer / headless Chromium fallback** —
  even at a 1080×2400 viewport with `evaluateOnNewDocument` seeding, the
  output reads as web. Existing Puppeteer scripts in `scripts/` (e.g.
  `capture_nonogram.js`) are deprecated; do not use, do not extend.
- **If no emulator / AVD is available in the environment, STOP and surface
  to the user as a blocker.** Do not fall back to headless Chromium "to
  keep the ship moving." Fresh raw screenshots are a hard prerequisite
  for shipping per Phase 5; if they can't be captured legitimately,
  shipping pauses until the emulator is available.
- A user override ("just use Puppeteer this once") does NOT lift the
  rule. Refuse and resurface the emulator setup. The classifier scoring
  applies to the published asset; it doesn't care whose decision skipped
  the emulator.

Each raw screenshot must show DIFFERENT in-game content from the others.

### Step 3.2 — Generate the icon

```
python3 gen_icon.py <AppName>
```

Behavior: reads `app_themes.py` for `<AppName>`'s palette, generates
a 512×512 + 1024×1024 icon using the app's focal element from a
per-app config (or asks Claude Code to specify one if not registered).

The icon's focal element MUST differ from every other Pegasus Games
app's. If `gen_icon.py` detects via `pre_publish_check.py`'s
perceptual-hash check that the new icon is too similar to an existing
one, it refuses to write and prompts for a different focal element.

Output:
```
<AppName>/store/icon_512_playstore.png
<AppName>/store/icon_1024_appstore.png
```

### Step 3.3 — Generate the feature graphic

```
python3 gen_feature.py <AppName>
```

Behavior: same theme as icon, 1024×500 horizontal, app name in the
theme's primary text color, mood tagline below.

Output:
```
<AppName>/store/feature_graphic_1024x500.png
```

### Step 3.4 — Wrap phone screenshots (MANDATORY)

```
python3 wrap_screenshots.py <AppName>
```

Behavior: reads each raw screenshot from
`<AppName>/store/screenshots/phone/raw/`, wraps each in the per-app
theme's marketing frame (gradient bg + headline + subtitle + framed
device shot + footer), writes the final 1080×2400 versions to
`<AppName>/store/screenshots/phone/01.png` through `07.png` (replacing
any earlier non-wrapped versions).

Headlines come from a per-app `SCREENSHOTS_HEADLINES` registry (in
`app_themes.py` or a separate `app_listing_copy.py`). If no headlines
are registered, the script refuses to run and asks Claude Code to
write 7 distinct headlines for the app (5 words max each, no banned
phrases).

**Verify after running:**
- The wrapped `01.png` shows a colored background gradient (NOT just
  raw dark navy)
- Marketing headline visible at top
- Phone-frame border visible around the gameplay shot
- Footer brand text visible at bottom
- Different theme color than other apps in the portfolio (compare
  visually to BallSortPuzzle and WaterSort screenshots)

If the output looks like the raw device screenshot with no wrapping,
the script silently failed — investigate immediately, don't ship.

### Step 3.5 — Wrap tablet screenshots

```
python3 wrap_tablet_screenshots.py <AppName>
```

Same wrapping logic at 1200×1920 (7") and 1800×2560 (10"). Outputs to
`<AppName>/store/screenshots/tablet_7/` and `tablet_10/`.

Default 2 screenshots per tablet size. If Play Console rejects (Google
docs say min 4), open the script, set `MIN_SCREENSHOTS = 4`, re-run.

### Step 3.6 — Visual sanity check (ITERATIVE LOOP, MANDATORY)

This is not a one-pass step. After running the wrap scripts, OPEN each
generated screenshot using the `view` tool and check it against this
specific checklist. If anything fails, fix the underlying cause and
regenerate. Repeat until all 7 phone screenshots pass.

**Per-screenshot checklist** — open each, check ALL items:

A. **Mobile-device proportions.** UI elements (header text, buttons,
   icons) appear at the size they would on a real phone. If the header
   text looks tiny, the in-app layout isn't scaling — fix it before
   continuing (per QUALITY_PLAYBOOK §1.5 tall phone support).

B. **Playable area fills the canvas.** The board / game elements
   occupy at least 50% of the captured 1080×2400 vertical space. If
   the playable area is small and there's >40% empty background,
   FIX THE IN-APP LAYOUT first. Don't try to fix it with screenshot
   crops — the underlying app needs to scale.

C. **No "fresh install" zeros.** Stats screenshot shows realistic
   numbers (247 coins, level 23, 7-day streak), NOT all zeros. If
   zeros, the localStorage seed (Phase 3.1.1) didn't run. Fix and
   recapture.

D. **No darkened-modal-over-blurred-menu.** Modal screenshots show
   the modal on a clean theme-colored background. If you see ghost
   menu buttons faded behind the modal, the screenshot mode wasn't
   enabled. Fix and recapture.

E. **Mid-progression content, not tutorial-tier.** "Deep gameplay"
   screenshot shows complex board state (lots of pieces, advanced
   level), not Level 1 with a 5×5 grid. Recapture from a higher level.

F. **Marketing wrap visible.** Around the device-area screenshot:
   theme-colored gradient background, headline at top in accent color,
   subtitle below, app-name footer at bottom. If the screenshot looks
   like raw device output with no wrapping, the wrap script silently
   failed — debug.

G. **Mission/list panels show hierarchy.** Per QUALITY_PLAYBOOK §3.6:
   featured item visible, varied progress bars (not all 0/N), at least
   one completed item dimmed. If 8 identical cards stacked, fix the
   in-app layout AND seed state.

**Iterative process:**

```
for each screenshot 01-07:
    view <AppName>/store/screenshots/phone/{NN}.png
    check items A-G
    if any fail:
        fix underlying cause (in-app layout, seed script, query param, etc.)
        re-capture raw/{NN}.png
        re-run wrap_screenshots.py <AppName>
        view again
    else:
        mark passed
```

Do NOT proceed to Phase 4 until all 7 screenshots pass all 7 checks.

**Same brand language test (cross-app):**

After per-screenshot pass, look at `<AppName>` screenshots side-by-side
with WaterSort screenshots. They should:
- Use clearly different theme colors (not both teal-ish)
- Have visibly different in-game content (not both showing colored
  vertical bars)
- Use the same wrapping LAYOUT (same headline position, same footer
  style) — that's intentional brand consistency

If the three apps could be confused for each other at a thumbnail
size, the theme registry isn't producing enough variety. Surface this.

---

5. **Generate tablet screenshots.** Clone
   `wrap_tablet_screenshots.py` similarly. Run. Outputs go to
   `store/screenshots/tablet_7/` and `store/screenshots/tablet_10/`.
   Default 2 per size; uncomment EXTRA_SCREENSHOTS if Play Console
   rejects (Google requires min 4 — mention this when handing off).

---

## Phase 4 — Listing copy & metadata (fully automated)

Each piece must be HAND-WRITTEN for this app, not template-substituted
from another app. Claude Code generates these from the game's actual
mechanic, not a template.

1. **`metadata/en-US/title.txt`** — App name, ≤30 chars, exact match to
   `<title>` in game.html and `android:label`. Examples:
   - "Sudoku Master" not "Sudoku"
   - "Block Puzzle Jewel" not "Block Puzzle"

2. **`metadata/en-US/short_description.txt`** — 80 chars max. Format:
   `[verb] + [what] + [qualifier]`. Examples:
   - "Solve number grids. 500 levels of relaxing logic puzzle fun."
   - "Match wood blocks. 300 challenging levels, no internet needed."
   No banned phrases (#1, Best, Top Rated, Download Now, etc.).

3. **`metadata/en-US/subtitle.txt`** — 30 chars max. Tagline. Hand
   written.

4. **`metadata/en-US/full_description.txt`** — Up to 4000 chars.
   Structure per playbook §7.5:
   - 2-3 sentence hook
   - 2-3 feature paragraphs
   - 6-10 bullet points of specific features (with this app's actual
     numbers: levels, themes, languages, etc.)
   - Optional extras section listing IAP options
   - 1-2 sentence closing
   No banned phrases. No keyword stuffing.

5. **`metadata/en-US/keywords.txt`** — Up to 100 chars, comma-separated.
   This app's specific search terms.

6. **`metadata/en-US/promotional_text.txt`** — App Store only, 170 chars.

7. **`metadata/en-US/release_notes.txt`** — For v1.0:
   `Initial release · 500 hand-crafted levels · Daily challenges and missions · Play offline anywhere`

8. **`metadata/app_info.json`** — Per `init_app_metadata.py` template,
   with canonical URLs (already correct from scaffold).

9. **`metadata/privacy.json`** — Canonical privacy URL, Data Safety
   answers identical to Ball Sort/WaterSort (game with AdMob+Firebase+
   IAP, no other data collection):
   ```json
   "data_collected": ["device_ids", "app_interactions", "crash_logs"],
   "data_shared":    ["advertising_id"],
   "encrypted_in_transit":      true,
   "user_can_request_deletion": true
   ```

10. **`metadata/content_rating.json`** — For most puzzle/casual games:
    age 13+, no violence, no gambling, no user-generated content,
    contains ads, contains IAP. KIDS apps need different answers — see
    QUALITY_PLAYBOOK §10.4 / §11.8.

11. **`metadata/iaps.json`** — Standard 9 products from the Pegasus
    Games IAP catalog (remove_ads, coins_small/medium/large/huge,
    starter_pack, premium_themes, season_pass_monthly, hint_pack).
    Product IDs prefixed with `<lowername>_` to be unique per app.

12. **`metadata/review_notes.json`** — For Google: explain that this is
    a casual puzzle game with AdMob ads, no login required, no special
    test account needed. For Apple: same content, mention demo account
    not required.

---

## Phase 4.5 — Translations (REQUIRED for every app)

Every app ships with all 11 locales for store listing. Per
`TRANSLATIONS.md`. The 11 locales are: en-US, de-DE, es-419, fr-FR,
hi-IN, id-ID, it-IT, ja-JP, pt-BR, tr-TR, uk-UA. Russian is excluded.

### 4.5.1 — Generate store listing translations

After Phase 4 produces the English baseline, run:

```
python3 scripts/gen_translations.py <AppName>
```

Behavior:
- Reads `<App>/metadata/en-US/` source files
- Generates `<App>/metadata/<locale>/` for each of the 10 non-English
  locales using LLM translation with the app's chosen voice from
  `app_themes.py`
- Validates each translation against Play Store character limits
- Validates against banned phrases per target language
- Writes failures as `*.rejected` files for manual editing

If the script reports any failures, hand-edit the `.rejected` files
down to character limit, then rename to remove `.rejected` suffix.
Don't ship until all 10 non-English locales have valid files.

### 4.5.2 — In-game string translations (REQUIRED for new apps)

For new apps starting from app #3 (after WaterSort and the next
shipped app), all UI strings in `game.html` must be externalized to
per-locale JSON in `<App>/android/app/src/main/assets/i18n/`:

```
i18n/
  en.json   ← source of truth
  de.json
  es.json
  fr.json
  hi.json
  id.json
  it.json
  ja.json
  pt.json
  tr.json
  uk.json
```

Each is a flat key-value map. The `game.html` should:
- Detect `navigator.language` (or `navigator.languages[0]`)
- Map to a 2-letter code matching the i18n filenames (en/de/es/fr/hi/id/it/ja/pt/tr/uk)
- Fall back to `en` for unsupported languages
- Fetch the JSON, populate strings via a `t(key)` function

Implementation pattern:
```javascript
async function loadStrings() {
    const fullLang = navigator.language || 'en';
    const lang = fullLang.split('-')[0];
    const supported = ['en', 'de', 'es', 'fr', 'hi', 'id', 'it', 'ja', 'pt', 'tr', 'uk'];
    const code = supported.includes(lang) ? lang : 'en';
    const response = await fetch(`i18n/${code}.json`);
    return await response.json();
}
```

The English `i18n/en.json` is the source of truth — every key must
exist in en.json before being added to other locales. Translation of
in-game strings uses the same `gen_translations.py` workflow but with
`--scope=ingame` flag (the script auto-detects when run against an
i18n folder vs a metadata folder).

### 4.5.3 — Kids program apps

If the app has `kids_program: true` in `metadata/app_info.json`,
`gen_translations.py` automatically uses Kids mode:
- Generates only the 4 minimum locales (en-US, es-419, pt-BR, fr-FR)
  rather than all 11
- Adds a `# KIDS APP — REVIEW BY NATIVE SPEAKER BEFORE SHIPPING` header
  to each translated file
- Forces voice = V7 (educational warm) regardless of app's normal voice
- `pre_publish_check.py` blocks the build until those headers are
  removed (signaling native review happened)

For non-Kids apps, all 11 locales are generated and shipped without
human review (machine translation is fine for short marketing copy in
adult apps).

---

## Phase 5 — Pre-build verification (automated)

```
python3 pre_publish_check.py <AppName>
```

If any blocking check fails, STOP and report. Do NOT auto-fix and
continue silently — surface what failed and why. Common fixes happen
inline; structural issues (e.g., game.html duplicates another app)
require going back to Phase 1.

The new checks added recently:
- `blocked placeholder apps` (auto-blocks the 33 Dice Roller clones)
- `icon perceptual similarity` (catches near-identical icons)
- `cross-app asset similarity` (byte-identical assets)
- `screenshot template reuse` (same screenshots used across apps)
- `listing copy uniqueness` (template-substituted listings)
- `canonical privacy/support URLs`
- `no per-app privacy.html`
- `no old placeholder URLs`

---

## Phase 6 — AdMob and IAP setup (HUMAN STEPS — generate hand-off doc)

These cannot be automated. AdMob doesn't expose app creation via API; Play
Console doesn't expose IAP product creation via API in a useful way.

Generate a single document `<AppName>/RELEASE_HANDOFF.md` containing
EVERYTHING the human needs, in the order they need to do it, with all
values pre-filled. Format:

```markdown
# Release Handoff — <AppName>

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: 20-30 minutes.

## Step 1 — Create the AdMob app entry (5 min)

Go to: https://apps.admob.com/v2/apps/list

Click "Add app" → choose Android → "No, the app isn't published yet"
(if just creating; pick "Yes" once on Play Store).

Fill in:
- App name: <AppName>
- App store: Google Play (or Not yet listed if pre-publish)
- User metrics: Yes / Yes / Yes (recommended for casual games)

Click "Add". AdMob will show you a new APPLICATION ID like
`ca-app-pub-5695494884863768~XXXXXXXXXX`. **Copy that.** Paste into:

  <AppName>/android/app/src/main/AndroidManifest.xml
  Search for: __ADMOB_APP_ID_PLACEHOLDER__
  Replace with: ca-app-pub-5695494884863768~XXXXXXXXXX

Then create 3 ad units (Apps → <AppName> → Ad units → Add ad unit):

  Banner ad     — name "<AppName>_banner"        — Banner
  Interstitial  — name "<AppName>_interstitial"  — Interstitial
  Rewarded      — name "<AppName>_rewarded"      — Rewarded

Each will give you an ad unit ID like `ca-app-pub-...` /XXXXXXXXXX.
Copy them. Paste into:

  <AppName>/android/app/src/main/java/com/pegasusgames/<lowername>/MainActivity.java
  Replace these constants:
    BANNER_AD_UNIT_ID       = "ca-app-pub-5695494884863768/<banner-id>";
    INTERSTITIAL_AD_UNIT_ID = "ca-app-pub-5695494884863768/<inter-id>";
    REWARDED_AD_UNIT_ID     = "ca-app-pub-5695494884863768/<rewarded-id>";

## Step 2 — Create the Play Console app entry (5 min)

Go to: https://play.google.com/console/u/0/developers/<your-org-id>/apps

Click "Create app". Fill in:
- App name: <AppName>
- Default language: English (United States)
- App or game: Game
- Free or paid: Free
- Declarations: ✓ developer program policies, ✓ US export laws

Click "Create app". You're now on the dashboard for the new app.

## Step 3 — Create the 9 IAP products in Play Console (10 min)

Play Console → <AppName> → Monetize → Products → In-app products.
Click "Create product" 9 times, with these exact values:

| Product ID                          | Type      | Name                | Default price |
|-------------------------------------|-----------|---------------------|---------------|
| <lowername>_remove_ads              | Managed   | Remove Ads          | $1.99         |
| <lowername>_coins_small             | Managed   | 100 Coins           | $0.99         |
| <lowername>_coins_medium            | Managed   | 500 Coins           | $3.99         |
| <lowername>_coins_large             | Managed   | 1200 Coins          | $7.99         |
| <lowername>_coins_huge              | Managed   | 3000 Coins          | $14.99        |
| <lowername>_starter_pack            | Managed   | Starter Pack        | $0.99         |
| <lowername>_premium_themes          | Managed   | Premium Themes      | $2.99         |
| <lowername>_hint_pack               | Managed   | Hint Pack           | $1.99         |
| <lowername>_season_pass_monthly     | Subscription | Monthly Pass     | $1.99/mo      |

For each: Activate after creating. (Default state is Inactive.)

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → <AppName> → Grow → Main store listing.

Copy these from the prepared metadata:
- App name           → <AppName>/metadata/en-US/title.txt
- Short description  → <AppName>/metadata/en-US/short_description.txt
- Full description   → <AppName>/metadata/en-US/full_description.txt

Upload graphics:
- App icon           → <AppName>/store/icon_512_playstore.png
- Feature graphic    → <AppName>/store/feature_graphic_1024x500.png
- Phone screenshots  → <AppName>/store/screenshots/phone/*.png (7 files)
- 7-inch tablet      → <AppName>/store/screenshots/tablet_7/*.png (2 files; if rejected, regenerate with EXTRA_SCREENSHOTS uncommented)
- 10-inch tablet     → <AppName>/store/screenshots/tablet_10/*.png (2 files)

Categorization:
- App category: Games → <category from app_info.json>
- Tags: <from keywords.txt>

## Step 5 — Fill in policy/declarations forms (5 min)

Play Console → <AppName> → Policy → App content. Click each section,
fill these answers:

**App access:**
- "All functionality is available without restrictions" → Yes (no login required)

**Ads:**
- Contains ads: Yes

**Content rating:**
- Click Start questionnaire
- Email: pegasusgames@atomicmail.io
- Category: Game
- Answer all questions: No to everything (no violence, no sexual content,
  no profanity, no gambling, no user-generated content, no location sharing)
- Submit

**Target audience:**
- Target age groups: 13–15, 16–17, 18+
- "Does your app unintentionally appeal to children?": No (this is a
  general-audience puzzle game)

**Data safety:**
- Click Start
- Does your app collect or share any of the required user data types? Yes
- Is all of the user data collected by your app encrypted in transit? Yes
- Do you provide a way for users to request that their data is deleted? Yes
- Data types collected:
  - App activity → App interactions (Optional, Analytics)
  - App info and performance → Crash logs, Diagnostics, Other app
    performance data (Optional, Analytics + App functionality)
  - Device or other IDs → Device ID (Optional, Advertising/marketing
    + Analytics; ALSO marked as Shared with third parties)
- Submit

**Government apps:** No.
**News apps:** No.
**COVID-19 contact tracing:** No.
**Financial features:** No.
**Health features:** No.
**Privacy policy URL:** https://pegasusgames-creator.github.io/privacy.html
**Advertising ID declaration:** Yes (used for advertising and analytics).

## Step 6 — Update local code with the AdMob IDs from Step 1, then rebuild (3 min)

Once Steps 1-5 are done, rebuild the AAB so it has the real AdMob IDs
baked in:

```
cd <AppName>/android
./gradlew bundleRelease
```

Output: <AppName>/android/app/build/outputs/bundle/release/app-release.aab

## Step 7 — Upload AAB to Play Console (2 min)

Play Console → <AppName> → Test and release → Production → Create new
release → Upload.

Drag in app-release.aab. Add release notes from
<AppName>/metadata/en-US/release_notes.txt. Save → Review → Send for
review.

First-time review: 3-7 days. Subsequent updates: usually under 24 hours.

---

You're done. Game is in review.
```

---

## Phase 7 — Build the signed AAB (automated, run TWICE)

The AAB is built twice: once before the human goes to AdMob/Play Console
(so they can test the build works), once after they've pasted real IDs
in.

**First build (before Phase 6 hand-off):**
```
cd <AppName>/android && ./gradlew bundleRelease
```
This will succeed even with placeholder AdMob IDs — the placeholders
fail at runtime, not build time. Verify the AAB exists, is signed (look
for `META-INF/`), and has the expected `versionCode` and `versionName`.

**After Phase 6 (human has pasted real AdMob IDs):**
Re-run the build. This is the AAB that ships.

---

## Phase 8 — Final verification

After the second build:

```
python3 pre_publish_check.py <AppName>
unzip -p <AppName>/android/app/build/outputs/bundle/release/app-release.aab \
  base/manifest/AndroidManifest.xml | grep -aE "ca-app-pub|versionCode|versionName"
```

Confirm:
- AdMob APPLICATION_ID is the real one (not `__ADMOB_APP_ID_PLACEHOLDER__`)
- versionCode and versionName match what's in build.gradle
- AAB is in the expected location

### 8.1 Artificial-detection self-check (MANDATORY before declaring ready)

Per APP_ARCHETYPES §8, answer all four honestly. If any fail, the
app is NOT ready — return to Phase 1 and refine.

1. **Side-by-side test.** Lay this app's screenshots next to
   BallSortPuzzle's and WaterSort's. Does a viewer see "different
   products" or "three games by the same publisher with the same
   template"?
   - Same template → fix Phase 1 design choices. Different layout
     archetype, different mascot pattern, different texture finish.
   - Different products → pass.

2. **Voice-specificity test.** Does the app's menu say something
   specific to its mechanic, beyond just the genre name?
   - "Sort the colored water!" → templated, fix
   - "Each tube wants only one color. Sort them. Find peace." → has voice
   - Pass: the menu copy reflects the chosen voice archetype.

3. **Identity-element test.** Is there a single visual element a user
   would recognize 1 second after seeing it (mascot, distinctive
   shape, signature color combo, unusual layout)?
   - No → add one. Add a mascot, a distinctive icon style, an unusual
     menu composition.
   - Yes → pass.

4. **Anonymous-screenshot test.** If the title and app name were
   removed from a screenshot, could a user tell which Pegasus Games
   app it's from?
   - No → too generic, fix. Strengthen identity elements.
   - Yes → pass.

If all four pass, proceed to 8.2.

### 8.2 Headline honesty audit (MANDATORY)

Open `<AppName>/metadata/screenshot_headlines.json`. For EACH headline,
verify it's true given the actual shipped game.html:

- "500 LEVELS" / "500 PUZZLES" → grep the level generator. Must produce
  ≥500 unique solvable levels. If only produces ~150, change headline
  to "150 LEVELS" or fix generator.
- "25×25 GRIDS" / size claims → check the maximum grid size the level
  generator outputs. The headline must match or undersell, never oversell.
- "DAILY CHALLENGE" → grep for daily-challenge implementation. Must
  actually fetch a different puzzle each day; not a fake "daily" that
  shows the same puzzle.
- "OFFLINE" / "NO WIFI" → test in airplane mode. App must be fully
  playable without network for these headlines to be honest.
- "FREE" → verify no required purchase to access core gameplay.
- Any number claim ("100 themes", "1000 levels") — verify the count
  in code.

If any headline overpromises, EITHER fix the game OR change the
headline. Don't ship with a mismatch — Google rejects on review and
this is straightforwardly false advertising.

This audit cannot be skipped just because "it's machine-generated copy."
Machine-generated false claims are still false claims.

### 8.3 Functional smoke test (MANDATORY)

Headless Chromium RENDERING an SVG cleanly is NOT proof the app works.
Before declaring ready, walk through every interactive path. Pegasus
Games has no Android device available, so the canonical method is
Playwright-driven click automation against the same headless Chromium
used for screenshot capture.

Run:
```
python3 scripts/smoke_test.py <AppName>
```

This script (to be added) walks the in-app flows by clicking each
button via Playwright, asserting the resulting state. It catches:
- Buttons that don't bind to handlers (silent JS errors)
- Modal flows that don't open the next screen
- Settings toggles that don't persist to localStorage
- Back-button navigation that crashes or skips screens

What Playwright CANNOT verify (real-device-only checks — must be
deferred to first user feedback or a future emulator setup):
- AdMob ad loading and rendering (no AdMob SDK in browser context)
- Google Play Billing IAP flow (Play Services not present)
- Real haptic feedback (device vibration)
- Notification permission prompt UI
- Background/foreground lifecycle on Android specifically
- Touch gestures that differ from mouse clicks (multi-touch, long-press
  edge cases)

For these device-only checks, take the pragmatic stance: ship to
production, monitor crash reports for the first 48 hours, fix any
issues that surface. This is what indie publishers do when they don't
have a device farm. The risk is real but bounded — typical first-day
production crash rate for a clean WebView wrapper is <1%.

The Playwright-driven smoke must verify (and fail the build if any of
these don't pass):

- [ ] `Game` global object exists after page load (no JS errors during init)
- [ ] Menu screen renders (menuScreen element visible)
- [ ] Play button click → screen changes to game / level
- [ ] Game canvas renders without errors
- [ ] Level Complete modal can be triggered via debug API and renders
- [ ] Daily Challenge button click → screen changes to daily mode
- [ ] Levels button click → level grid renders
- [ ] Shop button click → shop screen renders, IAP buttons present
- [ ] Settings button click → settings render, toggles present
- [ ] Each toggle persists state to localStorage when clicked
- [ ] Back button on each non-menu screen returns to menu
- [ ] No console errors thrown during the entire walkthrough

If ANY of these fail in Playwright, the app is NOT ready. Fix before
shipping. Real-device-only checks (ads, IAP, haptics, notifications)
are deferred but the user must acknowledge they're being deferred —
write the deferred list to `<App>/RELEASE_HANDOFF.md` "Deferred checks"
section so the user knows what to monitor in production.

If `smoke_test.py` doesn't exist yet, Claude Code can implement a
minimal version inline — Playwright + click each button by selector +
assert no console errors. The version that ships per-app should be at
least this minimal level, not skipped entirely.

If 8.1, 8.2, and 8.3 all pass, hand the path to the user. Done.

If any fail, do NOT proceed to handoff. The app is not ready. Return
to the appropriate Phase to fix.

---

## What Claude Code reports back to the user

After all phases, output ONE summary message:

```
✓ <AppName> ready for release.

Created:
- game.html (X lines, NN levels, all completable)
- icon_512_playstore.png (vivid <theme> palette, unique focal element)
- feature_graphic_1024x500.png
- 7 phone screenshots (wrapped with marketing frames)
- 4 tablet screenshots (2 each at 7" and 10")
- All metadata files
- Signed AAB at <path>

Pre-publish checks: PASS (no blocking issues)

Next: open RELEASE_HANDOFF.md and follow the 7 manual steps. ETA 20–30 min.
```

Don't dump a wall of detail. The handoff doc has the detail. The summary
just confirms what's done.

---

## Hard blockers — when to stop and ask

Stop and ask the user, do NOT proceed:

1. **The app's mechanic isn't determined** — if the user said "ship a
   puzzle game" without specifying what kind, ask which mechanic. This
   is the only acceptable Phase 1 question.

2. **The app is on the BLOCKED_APPS placeholder list AND the user
   doesn't want it rewritten** — if the user explicitly says "just ship
   the placeholder," refuse. The block is non-negotiable. The
   `check_blocked_apps` blocking check enforces this regardless.

3. **A second app from the same genre cluster shipping within 7 days**
   (Phase 0.5 of this workflow). Surface to the user, suggest a
   different cluster for this slot. The user can override; if they do,
   note it for the per-weekly portfolio audit.

4. **Pre-publish checks fail in a way that requires design decisions** —
   e.g., this app's icon is perceptually too similar to another's
   (`check_icon_perceptual_similarity` triggered). Don't auto-pick a
   different palette; surface the conflict, ask which to regenerate.

5. **`keystore.properties` is missing or has placeholder values** — need
   the real upload keystore credentials. Ask once, expect them in env
   vars or a vault path. Never write keystore credentials into the repo.

6. **The user's intent suggests they don't actually want full release**
   — e.g., "I just want to test this build" → don't run Phase 6
   handoff, just build and stop.

7. **The portfolio-level pre-publish check is failing on apps OTHER
   than the one being shipped.** If running `pre_publish_check.py`
   without arguments (full portfolio) shows blocking issues unrelated
   to the current app, surface them. Don't ship over an unstable
   portfolio.

---

## What this workflow does NOT do

To set expectations:

- **Does NOT create AdMob or Play Console accounts.** Those are one-time
  org-level setup. User has these already (Pegasus Games org account).
- **Does NOT handle iOS / App Store Connect.** Android only.
- **Does NOT recruit testers.** Org accounts are exempt from the 14-day
  closed-testing requirement, so this is unnecessary.
- **Does NOT call Google's Publishing API.** That requires per-app
  OAuth setup that isn't worth automating for a portfolio of this size.
  Manual web upload is faster end-to-end given the 7-step handoff is
  only 20-30 min.

---

## Updating this workflow

When something in the publish process changes (Google policy update,
new manifest requirement, new SDK version), update this file. It is the
authoritative reference for what "ready for release" means at Pegasus
Games. Code in `pre_publish_check.py` enforces a subset of these rules;
this doc is the broader human-readable specification.
