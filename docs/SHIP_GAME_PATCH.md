# PATCH for docs/SHIP_GAME.md

## Replace Phase 3 step 3 ("Capture raw screenshots") with this version

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

### Step 3.5 — Wrap (only after step 3.4 passes)

`python3 scripts/wrap_screenshots.py <AppName>`

The wrapper now enforces the 4% headline-to-subtitle gap (was 2%, too
tight for heavy display fonts per Puzzle2048 audit). If subtitles
overflow the canvas width, wrap to 2 lines with shrink-to-fit
fallback per the existing logic.

### Step 3.6 — Tablet captures and wraps (MANDATORY, all apps)

Every app ships with phone, 7" tablet, AND 10" tablet screenshots
per QUALITY_PLAYBOOK §7.3. No skipping. Steps 3.3-3.5 above run for
phone; this step repeats them for both tablet sizes.

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


## ADD to Phase 8 (Final verification) — new check 8.4

### 8.4 Screenshot-pipeline output verification

Run the full screenshot uniqueness + content match check:

    python3 scripts/pre_publish_check.py <AppName> --check screenshot_uniqueness

Must pass cleanly. This catches:
- Any two phone raws with hash distance ≤ 4 (= same screen captured twice)
- Tablet raws at phone resolution
- Tablet raws matching any phone raw (= phone captures placed in tablet wrap)

If this fails, the issues from Phase 3 weren't actually fixed. Don't
upload until they are.
