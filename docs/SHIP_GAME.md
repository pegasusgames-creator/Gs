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

### 1.4.1 Consult the designer when stuck

If at any point during Phase 1 you (Claude Code) are uncertain about a
design decision — what mascot the app should have, which archetype
combination fits the mechanic, whether the planned layout will feel
templated — call `consult_designer.py` to get a second opinion from a
fresh Claude API session acting as the design reviewer:

```
python3 scripts/consult_designer.py archetype-pick --app <AppName> \\
    --mechanic "describe the gameplay mechanic in one sentence"

python3 scripts/consult_designer.py mascot --app <AppName> \\
    --mechanic "describe the gameplay mechanic"

python3 scripts/consult_designer.py custom --app <AppName> \\
    --question "Should the Stats screen for a Sudoku-style game use a
    grid layout or a list layout?"
```

Each call costs ~$0.05-0.30 in API spend. The designer has access to
the app's archetypes (from app_themes.py) and identity.md. For
mascot calls specifically, it can produce ready-to-paste SVG, an
image-gen prompt, or an OpenGameArt link depending on what's best.

Use this instead of:
- Defaulting to a safe template choice when unsure
- Shipping a mediocre design and listing it as a "known gap"
- Asking the user to manually relay design questions to a chat session

The `consult_designer.py` script handles the relay automatically. The
user does NOT need to be in the loop for design questions.

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

5. **Generate a dedicated keystore for this app** (per-app, not shared —
   per CLAUDE.md "Keystore management"):
   ```
   python3 scripts/migrate_to_per_app_keystores.py --app <AppName>
   ```
   This creates `<AppName>/android/keystore.jks` with random
   passwords, writes `<AppName>/android/keystore.properties` (gitignored)
   referencing it, and records the SHA1 fingerprint in
   `metadata/app_info.json:upload_key_sha1`.

   **DO NOT copy keystore.properties from another app.** This was the
   May 2026 Nonogram failure mode: Nonogram's first build was signed
   with WaterSort's keystore, permanently locking Nonogram's Play
   Console listing to WaterSort's upload key. The fix required a
   1-3 business day upload-key reset request from Google. Don't repeat
   it. Each app gets its own dedicated keystore generated fresh; never
   reuse another app's signing material.

   **After running the script: BACK UP the new keystore.jks immediately**
   (within 24 hours, before the first Play Console upload):
   - Google Drive (encrypted folder, pegasusgames@atomicmail.io account)
   - USB stick (physical, kept off the development machine)
   - Password manager entry with the SHA1 fingerprint and password
     copied from keystore.properties

   Until backed up, the keystore exists only on this machine. If the
   machine fails, the app is permanently locked from updates (or
   requires a Play Console upload-key reset, which can take 1-3 days
   and may be denied).

   The 5 already-shipped/keyed apps (WaterSort, Nonogram, Puzzle2048,
   PipeConnect, UnblockPuzzle) keep their existing per-app keystores —
   `migrate_to_per_app_keystores.py` exempts them from migration.

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

### Step 3.1 — Generate the icon

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

### Step 3.2 — Generate the feature graphic

```
python3 gen_feature.py <AppName>
```

Behavior: same theme as icon, 1024×500 horizontal, app name in the
theme's primary text color, mood tagline below.

Output:
```
<AppName>/store/feature_graphic_1024x500.png
```

### Step 3.3 — Capture raw screenshots from emulator

Run `python3 scripts/capture_screenshots.py <AppName>`. The script
boots the emulator, installs the debug APK, force-stops/relaunches the
app for each slot, executes a tap sequence, and saves each capture to
`<App>/store/screenshots/phone/raw/0N.png`.

**Pre-capture seed file required.** Create
`<App>/test/seed_screenshot_state.js` with the EXACT localStorage keys
this app's `game.html` reads. Generic templates with keys like 'coins'
or 'streak' will silently fail if the app uses different keys. To find
the real keys:

    grep -n "localStorage.setItem" <App>/android/app/src/main/assets/game.html

Then write the seed with realistic mid-game values. See QUALITY_PLAYBOOK
§7.1.5.5 for required state.

**Per-app tap overrides.** The default `DEFAULT_TAPS` in the script
target the standard Pegasus menu layout. Apps with different layouts
(custom Play button position, no Daily/Best buttons in the same place,
etc.) need overrides at `<App>/test/screenshot_taps.json`:

```json
{
  "01_deep_gameplay": [
    {"x": 0.50, "y": 0.55, "delay": 0.8},
    {"x": 0.30, "y": 0.40, "delay": 1.2}
  ],
  "03_level_complete": [
    {"x": 0.50, "y": 0.55, "delay": 0.8}
  ]
}
```

Coordinates are FRACTIONS of screen w/h, not absolute pixels.

**★ NEW post-capture verification (May 2026 Puzzle2048 fix).** The
script now hashes each capture as it produces it. If a new capture
matches a prior slot's hash within 4 hamming distance, the script
**fails immediately** with a message identifying which slots collided
and why. This catches the case where adb taps miss target buttons and
all 7 slots silently capture the menu/initial state.

When verification fails:
1. Open the captured PNGs in `raw/` to see what actually got captured
2. Identify which intended screen each slot SHOULD have shown
3. Edit `<App>/test/screenshot_taps.json` with the correct coordinates
4. Re-run the capture
5. Iterate until all 7 slots produce visually distinct content

This is iterative for new apps — first run will likely fail
verification on at least one slot. That's expected and correct
behavior. Far better than the old silent-failure mode where the
pipeline shipped 7 wrapped screenshots over 2 distinct images.

**Why emulator, not headless Chromium.** Headless desktop Chromium can
render game.html but produces output that looks like "browser tab,"
not "phone screen": different font rendering pipeline, no Android
status bar / system insets, no real WebView init. The emulator runs
the actual APK through real Android initialization and produces the
correct mobile look.

### Step 3.4 — Visual verification of raw captures

BEFORE wrapping, open all 7 raw PNGs and verify against
`metadata/screenshot_headlines.json`:

| Slot | Headline says | Image must show |
|---|---|---|
| 01 | (deep gameplay claim) | mid-progression board, 60-80% filled |
| 02 | (mid-action claim) | gameplay mid-move, NOT menu |
| 03 | (level-complete / score claim) | celebration UI with stars/coins |
| 04 | (variety / Daily claim) | the screen the headline names |
| 05 | (event / mission claim) | the screen the headline names |
| 06 | (booster / undo claim) | the relevant button or modal visible |
| 07 | (brand / scope claim) | typically the menu, OK |

If any slot's image doesn't match its headline, EITHER re-capture with
the right screen content OR change the headline to match what was
actually captured. Per QUALITY_PLAYBOOK §7.1.6 this is mandatory and
non-negotiable — the May 2026 Puzzle2048 audit found 5 of 7 slots
with mismatches; fixing this before upload prevents Misleading
Behavior policy strikes.

Per-screenshot checklist — for each PNG verify ALL items:

A. **Mobile-device proportions.** UI elements at the size they would
   appear on a real phone, not tiny against tall canvas.
B. **Playable area fills the canvas.** ≥50% of vertical space.
C. **No "fresh install" zeros.** Stats screen shows realistic numbers
   (247 coins, level 23, 7-day streak), NOT all zeros.
D. **No darkened-modal-over-blurred-menu.** Modal screens show the
   modal on a clean theme-colored background.
E. **Mid-progression content, not tutorial-tier.** Deep-gameplay
   slot shows complex board state.
F. **Mission/list panels show hierarchy** per QUALITY_PLAYBOOK §3.6:
   featured item visible, varied progress bars, completed items dimmed.

Iterate raw → fix underlying cause → re-capture until each slot
passes.

### Step 3.5 — Wrap (only after step 3.4 passes)

```
python3 scripts/wrap_screenshots.py <AppName>
```

Behavior: reads each raw screenshot from
`<AppName>/store/screenshots/phone/raw/`, wraps each in the per-app
theme's marketing frame (gradient bg + headline + subtitle + framed
device shot + footer), writes the final 1080×2400 versions to
`<AppName>/store/screenshots/phone/01.png` through `07.png`.

Headlines come from a per-app `metadata/screenshot_headlines.json`
file. If no headlines are registered, the script refuses to run and
asks Claude Code to write 7 distinct headlines for the app (5 words
max each, no banned phrases).

The wrapper now enforces the 4% headline-to-subtitle gap (was 2%, too
tight for heavy display fonts per Puzzle2048 audit). If subtitles
overflow the canvas width, wrap to 2 lines with shrink-to-fit
fallback per the existing logic.

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

### Step 3.6 — Tablet captures and wraps (MANDATORY, all apps)

Every app ships with phone, 7" tablet, AND 10" tablet screenshots
per QUALITY_PLAYBOOK §7.3. No skipping. Steps 3.3-3.5 above run for
phone; this step repeats them for both tablet sizes.

**Three surfaces, three distinct stories — applies to all NEW apps
(grandfathered: WaterSort, Nonogram, Puzzle2048 ship as-is, do not
retroactively rework).** Phone, tablet 7", and tablet 10" must each
be a fully distinct listing — they share the same app and brand, but
EVERY axis below must differ across the three:

1. **Different in-app pages captured.** Don't capture the same
   screen type for all three surfaces. Vary which game state each
   surface shows: phone might lead with the active board + daily
   challenge + shop; tablet 7" might lead with the level select +
   power-up panel + win screen; tablet 10" might lead with the
   themes gallery + leaderboard + tutorial. The three listings
   together should cover ~10–12 distinct in-app moments, not the
   same 2–3 moments reframed three times.
2. **Different levels / boards / progress states.** Even when the
   same screen type is captured (e.g. "active board"), the level
   number, board layout, color palette in play, or progress state
   shown must differ across surfaces. Phone showing "level 3 mid-
   pour" + tablet 7" showing the same level 3 + tablet 10" showing
   the same level 3 is the failure mode — capture level 3 for
   phone, level 27 for tablet 7", level 84 for tablet 10".
3. **No raw slot reused across surfaces.** Standard allocation:
   - Phone:     raw/01–raw/07 (the 7 hero pages on phone AVD)
   - Tablet 7": raw/04 + raw/06 (captured FRESH on the 7" AVD,
     showing different levels/screens than phone slots)
   - Tablet 10": raw/02 + raw/05 (different from BOTH phone hero
     and tablet 7" content, captured FRESH on the 10" AVD)
4. **Different wrapper variant per surface.** Don't ship the same
   marketing frame (background gradient, headline placement, device
   mockup style, accent treatment) on all three surfaces with only
   the inner raw swapped:
   - Phone:     primary wrapper variant (full hero crop, top-aligned
     headline)
   - Tablet 7": secondary variant (split-pane layout or side-aligned
     headline, different accent texture)
   - Tablet 10": tertiary variant (landscape-friendly composition,
     larger device mockup, different gradient direction)
   Variant selection lives in `wrap_screenshots.py` /
   `wrap_tablet_screenshots.py`. If the scripts only emit one
   variant, add per-target variants before shipping the app — do not
   ship three identical frames.
5. **Per-surface headlines and subtext.** Phone reads
   `metadata/screenshot_headlines.json`. Tablets must have their own
   `metadata/screenshot_headlines_tablet_7.json` and
   `metadata/screenshot_headlines_tablet_10.json` files (already
   supported by `wrap_tablet_screenshots.py` line ~322 — when
   missing, it silently falls back to phone copy, which is the
   failure mode to avoid). Each file is the same schema as the phone
   one (array of `{line1, line2, subtitle}`), but every entry must be
   different copy from the phone version — different angle, different
   feature emphasized, different verb. Don't translate phone copy
   into "tablet voice" with synonym swaps; write fresh hooks that
   match what each surface's raw page actually shows. If a surface
   has only 2 wrapped slots (the Pegasus minimum), 2 fresh headlines
   per surface = 6 unique headlines per app.

**Enforcement state (May 2026):** `check_screenshot_uniqueness`
currently blocks tablet raws that match phone raws, and blocks tablet
raws below tablet resolution. It does NOT yet block tablet_7-vs-
tablet_10 raw collisions or wrapper-variant reuse across the three
surfaces — those rules are doc-only for now. Hold the bar manually
during Phase 3.6: pick distinct raw slots for each of the three
surfaces, and confirm visually that the three wrapped marketing
frames look like three different listings, not three copies of one.

For each tablet target:

1. Boot the tablet AVD if not already running:
   ```
   emulator -avd pegasus_tablet_7    # or pegasus_tablet_10
   ```
   Wait for full boot (animation finishes, home screen settled).

2. Capture with the target flag:
   ```
   python3 scripts/capture_screenshots.py <AppName> --target tablet_7
   python3 scripts/capture_screenshots.py <AppName> --target tablet_10
   ```
   The script writes to `<App>/store/screenshots/tablet_7/raw/0N.png`
   and `<App>/store/screenshots/tablet_10/raw/0N.png` respectively.
   Tap fractions are reused from `<App>/test/screenshot_taps.json`,
   but if tablet UI shifts buttons (some apps have side panels at
   tablet width), add tablet-specific overrides under
   `tablet_7_*` / `tablet_10_*` keys in that file.

3. Visual verification (per Step 3.4) — open the tablet raws, confirm
   each shows the in-app content the headline claims. Tablet captures
   must look DIFFERENT from phone captures (different aspect, different
   board sizing, different HUD positions) — if they look like
   stretched phone screens, the tablet AVD config is wrong or the app's
   in-app layout doesn't adapt to wider screens. Fix the in-app layout
   first, recapture.

4. Wrap:
   ```
   python3 scripts/wrap_tablet_screenshots.py <AppName>
   ```
   Reads from both `tablet_7/raw/` and `tablet_10/raw/`, writes wrapped
   PNGs to `tablet_7/0N.png` and `tablet_10/0N.png`.

**`wrap_tablet_screenshots.py` rejects phone-resolution raws.** If
the wrap script errors with "raw screenshot is only 1080px wide, too
narrow for tablet_7 target", the tablet capture step didn't actually
run on a tablet AVD — phone raws got copied or rescaled into the
tablet folder. Don't work around with `--force`; fix by re-capturing
from a real tablet emulator. The April 2026 Puzzle2048 ship had this
defect and it's a tell that the build is unfinished.

5. Run uniqueness check, which now covers all three sets:
   ```
   python3 scripts/pre_publish_check.py <AppName> --check screenshot_uniqueness
   ```
   Blocks if any tablet raw matches a phone raw, or if tablet raws are
   below required resolution.

**One-time setup if tablet AVDs aren't installed:** see
QUALITY_PLAYBOOK §7.3 for the avdmanager commands. Total cost ~2 GB
disk per AVD, ~5 min setup.


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

Every app ships with all 13 locales for store listing. Per
`TRANSLATIONS.md`. The 13 locales are: en-US, ar, de-DE, es-419, fr-FR,
hi-IN, id, it-IT, ja-JP, pt-BR, tr-TR, uk, zh-CN. Russian is excluded.
Note: Indonesian uses `id` (not `id-ID`) and Ukrainian uses `uk` (not
`uk-UA`) — those are the codes Play Console accepts.

### 4.5.1 — Generate store listing translations

After Phase 4 produces the English baseline, run:

```
python3 scripts/gen_translations.py <AppName>
```

Behavior:
- Reads `<App>/metadata/en-US/` source files
- Generates `<App>/metadata/<locale>/` for each of the 12 non-English
  locales using LLM translation with the app's chosen voice from
  `app_themes.py`
- Validates each translation against Play Store character limits
- Validates against banned phrases per target language
- Writes failures as `*.rejected` files for manual editing

If the script reports any failures, hand-edit the `.rejected` files
down to character limit, then rename to remove `.rejected` suffix.
Don't ship until all 12 non-English locales have valid files.

If `ANTHROPIC_API_KEY` isn't set in the shell, fall back to writing
the translations directly (Claude Code is multilingual — short
marketing copy in any of the 12 target languages is in scope).

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
  rather than all 13
- Adds a `# KIDS APP — REVIEW BY NATIVE SPEAKER BEFORE SHIPPING` header
  to each translated file
- Forces voice = V7 (educational warm) regardless of app's normal voice
- `pre_publish_check.py` blocks the build until those headers are
  removed (signaling native review happened)

For non-Kids apps, all 13 locales are generated and shipped without
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

### 8.1.5 Designer review of screenshots (RECOMMENDED)

Before 8.2 honesty audit, get a fresh design eye on the wrapped
screenshots. Run:

```
python3 scripts/consult_designer.py screenshot-review --app <AppName>
```

This sends the 7 screenshots to a fresh Claude API session that
reviews each against the §3.6 quality checklist (mobile proportions,
50% canvas fill, real numbers, mid-progression, hierarchy in panels)
and returns per-slot pass/fail with specific fix recommendations.

Cost: ~$0.20 per call. Catches issues you missed during Phase 3.6's
own iterative loop because a fresh reviewer doesn't have the "I've
been staring at these for 20 minutes" blindness.

Treat the designer's BLOCKER findings as actual blockers — don't
ship through them. POLISH findings can be deferred but should be
written into `RELEASE_HANDOFF.md`'s "Deferred polish" section so the
user knows what's pending for the next version.

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

### 8.4 Screenshot-pipeline output verification

Run the full screenshot uniqueness + content match check:

    python3 scripts/pre_publish_check.py <AppName> --check screenshot_uniqueness

Must pass cleanly. This catches:
- Any two phone raws with hash distance ≤ 4 (= same screen captured twice)
- Tablet raws at phone resolution
- Tablet raws matching any phone raw (= phone captures placed in tablet wrap)

If this fails, the issues from Phase 3 weren't actually fixed. Don't
upload until they are.

If 8.1, 8.2, 8.3, and 8.4 all pass, hand the path to the user. Done.

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

5. **`<App>/android/keystore.jks` is missing** — the app needs its
   dedicated keystore generated. Run
   `python3 scripts/migrate_to_per_app_keystores.py --app <AppName>`
   (Phase 1 step 5). NEVER copy keystore.jks/keystore.properties from
   another app — that was the May 2026 Nonogram failure mode and
   required a 1-3 day Play Console reset to recover. If `keystore.jks`
   exists but the SHA1 doesn't match
   `metadata/app_info.json:upload_key_sha1`, surface to the user — do
   NOT auto-overwrite, the existing keystore may be the one Play
   Console has registered.

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
