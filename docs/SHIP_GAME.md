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

## Phase 1 — Game logic (the only step that can't be automated by template)

This is the part that requires real design thinking. Don't shortcut it.

1. **Decide the game's core mechanic.** It must be genuinely different
   from every other shipped Pegasus Games app. If the user said "ship
   Sudoku" the mechanic is decided. If the user said "ship a puzzle game"
   ask what mechanic — that's the one acceptable clarifying question at
   this phase.

2. **Decide the visual theme.** Vivid saturated palette per
   QUALITY_PLAYBOOK §1.1, distinct from other apps in the portfolio.
   Pick 4–8 colors, write them down.

3. **Write `<AppName>/android/app/src/main/assets/game.html`** following
   the playbook. Required features for any GAME (not TOOL/TRACKER):
   - Vivid color palette §1.1
   - Local Poppins font (4 weights in `assets/fonts/`) §1.2
   - SVG icons throughout, no emoji as UI §1.3
   - Animated tutorial on first level §2.1
   - First 3-5 levels trivially solvable §2.2
   - First 20 levels don't decrement lives §2.3
   - Hero menu + 2 secondary buttons + icon row §3.1
   - Progress subtext under Play button §3.2
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
   - localStorage state persistence on every event §8.3
   - Offline-first §8.2
   - Portrait lock §8.5

4. **Verify all levels are completable.** The level generator must
   guarantee solvability. If it's a procedural generator, embed a solver
   that runs against generated levels and rejects unsolvable ones. If
   handcrafted, every level needs a known solution. Test plan:
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

## Phase 3 — Visual assets (fully automated)

Run scripts in this order. Each takes < 1 minute.

1. **Generate the icon.** Clone `gen_icon.py` to
   `<AppName>/gen_icon.py`, change the color palette and the focal
   element to match this app's theme, run:
   ```
   cd <AppName> && python3 gen_icon.py
   ```
   Outputs: `store/icon_512_playstore.png`, `store/icon_1024_appstore.png`.
   The focal element MUST differ from every other Pegasus Games app's
   icon focal element. If unsure what's been used: list focal elements
   from each shipped app's icon (check `store/icon_512_playstore.png`).

2. **Generate the feature graphic.** Clone `gen_feature.py` similarly,
   adjust headline text and palette, run:
   ```
   cd <AppName> && python3 gen_feature.py
   ```
   Outputs: `store/feature_graphic_1024x500.png`.

3. **Capture raw screenshots from the running app.** Use
   `adb screencap` on a connected device or emulator if available, or
   render via Puppeteer/Playwright headless if no device:
   - 7 screenshots minimum, sized 1080×2400 (or 1080×1920 if older spec)
   - Should capture: deep gameplay, easy gameplay, level complete,
     daily missions, stats screen, level select, menu — in that order.
   Save raw shots to `<AppName>/store/screenshots/phone/01_main.png`
   through `07_main.png`.

4. **Wrap the screenshots with marketing frames.** Clone
   `wrap_screenshots.py` to `<AppName>/wrap_screenshots.py`, customize
   the `SCREENSHOTS` list (headlines per shot) and the theme colors to
   match this app's palette, run:
   ```
   cd <AppName> && python3 wrap_screenshots.py
   ```
   Then promote the wrapped versions to be the canonical phone
   screenshots (the script's printed output explains how).

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

Hand the path to the user. Done.

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
   the placeholder," refuse. The block is non-negotiable.

3. **The user wants to publish more than 2-3 apps in the same week** —
   per CLAUDE.md "Shipping cadence." Surface this and confirm the user
   understands the velocity-spike risk.

4. **Pre-publish checks fail in a way that requires design decisions** —
   e.g., this app's icon is too similar to another's. Don't auto-pick
   a different palette; surface and ask.

5. **`keystore.properties` is missing or has placeholder values** — need
   the real upload keystore credentials. Ask once, expect them in env
   vars or a vault path. Never write keystore credentials into the repo.

6. **The user's intent suggests they don't actually want full release**
   — e.g., "I just want to test this build" → don't run Phase 6
   handoff, just build and stop.

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
