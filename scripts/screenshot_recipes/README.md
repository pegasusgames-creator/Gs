# Screenshot recipes

Per-app puppeteer scripts that drive `assets/game.html` in headless
Chrome and capture the seven raw screenshots
(`<App>/store/screenshots/phone/raw/01.png`–`07.png`) used by
`wrap_screenshots.py`.

## How to add a recipe for a new app

1. Copy `UnblockPuzzle.js` to `<AppName>.js`.
2. Change the `APP` constant to that app's path.
3. Look at the app's `game.html` for:
   - the `localStorage` save key and `defaultState()` shape
   - the `showScreen('...')` ids for menu, level select, stats,
     missions, daily, etc.
   - the function that loads a level (often `startLevel(idx)` or
     `loadLevel(n)`)
   - the win-overlay element id (often `winOverlay`) and which fields
     to populate (`winStars`, `winInfo`)
   - any boot-time popups guarded by localStorage flags (Starter Pack
     uses `xstarter_seen`, daily-streak overlays often use
     `ls_shown_today`)
4. Update the seed state in the recipe so stats / level select look
   populated (≥ ~80 levels completed, some coins, daily streak > 0).
5. Update the per-slot setup functions to call this app's specific
   navigation / level numbers / overlay ids.
6. Run with `node scripts/screenshot_recipes/<AppName>.js`.

## Run-time requirements

- Node 18+ with the global puppeteer install at
  `/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer`.
- Chrome / Chromium available on `PATH` (puppeteer auto-detects).
- No internet at run-time — `file://` URLs only.

## Why this approach

No Android emulator or device is available on the build box. Puppeteer
is the only working way to drive a WebView-style game.html through
seven distinct in-game states reproducibly. The seeded localStorage
ensures stats / level select aren't empty; the per-modal dismiss
helper prevents promo popups (Starter Pack, daily streak) from
covering screens during capture.
