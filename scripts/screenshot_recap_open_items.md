# Screenshot re-capture — open items (2026-06-08)

## 2026-06-16 update — emulator capture is now self-cleaning

`adb` + the three AVDs (`pegasus_phone`, `pegasus_tablet_7`,
`pegasus_tablet_10`) are now available in the dev environment, and the
capture pipeline no longer depends on per-app `_setup_taps` to clean the
frame. `scripts/capture_screenshots.py` now, right before every
screencap, runs a clean-JS step that:

- sets `tutorialDone` / `coachmarkDone` (no coachmark overlay),
- calls `Android.hideBannerAd()` (no "Test Ad" banner — works on any app
  whose `MainActivity` exposes the bridge; no-op otherwise), and
- hides the two first-launch popups that queue over gameplay on a fresh
  install: `#ls-overlay` (daily login-streak) and `#starterPackModal`.
  The intentional capture overlays (`overlay-complete/daily/hint/nolives`)
  are left alone.

Device prep that the operator still does once per fresh emulator boot:
`adb shell settings put secure immersive_mode_confirmations confirmed`
(kills the system "Viewing full screen" dialog), and for
**`pegasus_tablet_10` rotate to portrait** — it boots landscape
(2560×1600); `adb shell settings put system user_rotation 1` (after
`accelerometer_rotation 0`) gives the required 1600×2560. The raw must be
portrait or the tablet_10 wrap is distorted. (Orientation can transiently
flip on an app's first launch — verify each tablet_10 raw is
`h > w` and re-shoot the odd slot.)

`scripts/wrap_screenshots.py --iphone` re-wraps 3 phone raws at Apple's
1320×2868 into `store/screenshots/iphone_6_9/` (slots 1 / mid / last,
skipping the themes slot).

**Recaptured 2026-06-16 (all surfaces, 7 phone / 2 tab7 / 2 tab10 + 3
iPhone):** Afterimage, PipeConnect, Hunch, Overlay. PipeConnect because
its 122 levels were regenerated; Afterimage because its board was
polished; Hunch+Overlay because their `test/screenshot_taps.json` were
**verbatim copies of PipeConnect's** (referenced `loadLevel(72..120)`
that don't exist in those 60-level games, and applied PipeConnect dot
palettes that do nothing) — rewritten per-game with valid levels + each
app's real theme palette + `body.midnight` chrome. Hunch additionally
seeds a lit pattern + runs `doTest()` via `window._hunchFill(cells)`
because a fresh Hunch level is an empty grid (otherwise every slot is
near-identical). This copied-config class is now gated by
`scripts/check_screenshot_taps_valid.py`.

## Why this exists

The 2026-06-08 screenshot audit found 3 systemic problems across all 4
shipping apps that the *existing* wrapped screenshots ship with:

1. **Tutorial coachmark overlay covers gameplay** in every Nonogram and
   UnblockPuzzle store screenshot. Wrapped 01-06 phone + every tablet
   slot show a centered "Find the picture / Step 1 / 3" (Nonogram) or
   "Find the red car / Step 1 / 3" (UnblockPuzzle) panel with a dimmed
   board behind. The puzzle itself — the thing the listing sells — is
   invisible.
2. **AdMob "Test Ad" banner is visible at the bottom of every shot in
   all 4 apps** (or a cross-promo strip in UnblockPuzzle). Looks
   unprofessional and reads as "this app has more ads than gameplay".
3. **WaterSortPuzzle phone slot 04 headline/content mismatch.** Headline
   reads "DEEP-WATER PUZZLES / Late-game boards that test how far ahead
   you can see." but the captured raw shows Level 9. Headline checked
   against board level by `check_screenshot_headline_match`, currently
   warn-only because OCR isn't installed.

## What's already fixed in-repo

- **`_setup_taps` prefix** (all 4 apps) now sets
  `localStorage.setItem('tutorialDone','1')` +
  `localStorage.setItem('coachmarkDone','1')` +
  `if(window.Android&&Android.hideBannerAd)Android.hideBannerAd();`
  before the per-app seed runs. Identified via the
  `/*screenshot-clean-prefix*/` marker — idempotent.
- **WaterSortPuzzle phone 04 tap** changed from `_jumpTo(8,'ocean')` →
  `_jumpTo(95,'ocean')` to match the "Late-game" headline claim.
- **`capture_screenshots.py SLOTS`** is now target-aware:
  `phone=7`, `tablet_7=2`, `tablet_10=2`. The 7th phone slot key is
  `07_depth` (each app picks its own meaning — themes grid, weekly
  bracket, daily challenge, etc. — never the menu).
- **Tablet wrapped + raw + headlines + tap-config trimmed** to 2 per
  surface per app. Picks:

  | App | tablet_7 kept (1, 2) | tablet_10 kept (1, 2) |
  |---|---|---|
  | WaterSortPuzzle | EASE INTO THE FLOW · BUILD UP TO SIX COLORS | QUICK CALM POURS · TANGLED SIX-COLOR BOARDS |
  | Nonogram | FIVE HUNDRED PUZZLES READY · TWENTY BY TWENTY | 500 HAND-CRAFTED · MASTER THE HARDEST BOARDS |
  | Puzzle2048 | TIGHT GRID STATES · CLIMB TO 1024 & BEYOND | MID-GAME GRIDS · 1024+ TILES STACKED |
  | UnblockPuzzle | BIG BOARD BIG BRAIN · TRACK EVERY SOLVE | DESK MODE DEEP FOCUS · 150 JAMS TO ESCAPE |

- **`check_screenshot_completeness`** now uses per-surface minimums
  (7/2/2) instead of a flat 6/surface. Already-shipped apps get
  warnings if under; pre-ship gets blocked.
- **CLAUDE.md + docs/QUALITY_PLAYBOOK.md** updated with the 7/2/2 rule
  and the new "no tutorial overlay / no test ad in screenshots"
  invariants.

## What needs the emulator (user action)

`adb` isn't available in the dev environment, so the actual re-capture
must happen on the user's machine. Sequence:

1. **Pick each app's 7th phone slot.** Suggested defaults:
   - WaterSortPuzzle → `07_themes_grid` (Themes screen with all unlocked palettes)
   - Nonogram → `07_weekly_bracket` (Ranks sheet → "This Week" tab)
   - Puzzle2048 → `07_weekly_bracket` (same — shows the new meta-loop)
   - UnblockPuzzle → `07_themes_grid` (6 block themes laid out)

   Add a `"07_<name>": [["js", "<screen-setup-JS>", <delay_ms>]]` entry
   to each app's `test/screenshot_taps.json`.

2. **Add the 7th phone headline.** Append one entry to each app's
   `metadata/screenshot_headlines.json` matching the new slot.

3. **Run the capture for every (app × surface) combo:**
   ```bash
   for app in WaterSortPuzzle Nonogram Puzzle2048 UnblockPuzzle; do
     for surf in phone tablet_7 tablet_10; do
       python3 scripts/capture_screenshots.py $app --target $surf
     done
   done
   ```
   The new `_setup_taps` prefix dismisses the coachmark + hides the
   banner before the first screencap; the existing per-slot JS taps
   already call `window._hideModals()`. No code changes required.

4. **Re-wrap:**
   ```bash
   for app in WaterSortPuzzle Nonogram Puzzle2048 UnblockPuzzle; do
     python3 scripts/wrap_screenshots.py $app
     python3 scripts/wrap_tablet_screenshots.py $app
   done
   ```

5. **Verify:** open each app's `store/screenshots/phone/01.png` ..
   `07.png` and `tablet_7/0{1,2}.png` + `tablet_10/0{1,2}.png` —
   confirm no coachmark, no Test Ad badge, headline matches content.

## Detection gates (proposed — not yet wired)

Two new pre-publish gates would catch this class of regression:

- **`check_no_coachmark_in_screenshots.py`** — perceptual-hash each
  wrapped slot against a "coachmark fingerprint" template (centered
  white card with rounded corners + "Step 1 / 3" text) and block if
  any slot matches above a threshold. Cheapest: detect the
  characteristic centered-bright-card pixel pattern.
- **`check_no_test_ad_in_screenshots.py`** — sample the bottom 50dp
  strip of each phone raw + check for the "Test Ad" yellow badge color
  (`#ffd700`-ish on dark) or the SAMSUNG creative's specific palette.

Both can be implemented as PNG pixel-region checks via Pillow without
new dependencies.

## Open question — gate the trim with assets

The 4 deleted raws per surface per app (32 wrapped + 32 raw total)
contained Test-Ad-bearing screenshots that can't be re-shipped without
a recapture. They're gone from the repo. If a user needs them back for
archival, they're recoverable from git history (commit before this
ship round). Otherwise the next release will use whatever the capture
run produces fresh.
