# Audit 2026-05-15 — open items

Follow-ups left after applying the WaterSortPuzzle / Nonogram / Puzzle2048
audit (Parts A–H). Nothing here blocks the three v2.0.3 / v1.1.3 builds;
these are deferrals, manual-review flags, and environment notes.

## Deferred work

- **C5 — Puzzle2048 `unlimited_undos` SKU (optional).** Not implemented.
  Adds catalog symmetry with WaterSort and an undo-based ARPU lever.
  To do it later: add `unlimited_undos` to `Puzzle2048/metadata/iaps.json`
  `one_time_products` ($4.99, non-consumable); the SKU flows into
  `MainActivity.java` `VALID_PRODUCTS` via `patchValidProducts`; add an
  `onPurchaseComplete` case `unlimited_undos` → `State.unlimitedUndo =
  true` + toast; guard the `doUndo` path to skip decrementing `undoPack`
  when `State.unlimitedUndo` or `isSeasonActive()`.

## Manual-review flags

- **B3 — Ukrainian calques (native-speaker review).** One literal
  calque was fixed automatically in `WaterSortPuzzle/metadata/uk/
  full_description.txt` ("Озвучте у навушниках, відключіть розум" →
  "Увімкни навушники й розслабся"). Still flagged for a native pass,
  NOT auto-retranslated:
  - `WaterSortPuzzle/metadata/uk/full_description.txt` line 3 — "потік"
    used for a "pour"/"flow" sense; reads slightly off.
  - `Nonogram/metadata/uk/full_description.txt` line 24 —
    "авторизаційний потік" is a literal calque of "login streak".
  - Recommend a full native pass of `uk/full_description.txt`,
    `uk/short_description.txt`, `uk/promotional_text.txt` for all three
    apps.

- **Part F — release-note translations.** The 36 localized
  `release_notes.txt` files (12 locales × 3 apps) are AI-translated.
  Per the audit's own lesson (CLAUDE.md "Common audit slips"), have the
  top-3-revenue locales reviewed by a native speaker before upload.

- **D1 — WaterSort tablet_10 slot 06.** Freshly captured on the
  `pegasus_tablet_10` AVD (level 64, ocean theme — a gameplay board).
  Eyeball `WaterSortPuzzle/store/screenshots/tablet_10/06.png` before
  upload to confirm it shows the board cleanly (screenshots are
  reviewed manually).

- **G3 — tesseract not installed.** `check_screenshot_headline_match`
  runs in degraded mode (WARNING, not BLOCKER) without OCR. It warned:
  `Puzzle2048` phone slot 6 headline "WEEKLY TOURNAMENT" — verify that
  screenshot shows the tournament panel, or re-headline it. Install
  `tesseract-ocr` to enable automated verification.

## Environment / build notes

- **B5 — AppLovin MAX.** Disabled in all three apps (AdMob-only by
  design). `MAX_SDK_KEY` + the four `MAX_*_UNIT_ID` constants in each
  `MainActivity.java` are intentionally blank with TODO markers. Fill
  them and flip `USE_APPLOVIN` once the AppLovin developer account is
  approved. Not a blocker — AdMob is live.

- **E2 — AAB location.** The three signed release AABs are at each
  app's `android/app/build/outputs/bundle/release/app-release.aab`,
  NOT mirrored into a `release_aabs/` folder. The task spec said
  `release_aabs/`; left per-app per the standing preference that AABs
  stay per-app. Say so if you want them mirrored.

## Minor

- **WaterSort `RELEASE_HANDOFF.md` Step 4** still says "upload all 7
  files" / "7 file(s)" for screenshots — stale after the menu-screenshot
  removal; the surfaces are now 6 phone / 6 tablet_7 / 6 tablet_10.
- **A4 naming.** The handoff IAP-table Names were filled from
  `iaps.json` (`1 Hour Unlimited Lives`, `Unlimited Lives Forever`),
  which differ slightly from the strings the audit text suggested
  (`1hr Unlimited Lives`, `Unlimited Lives`). `iaps.json` is the
  catalog source of truth, so its names were used.
- **WaterSort `test/screenshot_taps.json`** still has dead
  `*_07_menu` tap keys — `capture_screenshots.py` no longer has a
  slot 07, so they are unused (harmless).
