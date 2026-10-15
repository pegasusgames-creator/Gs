# Family game shell — builder contract

Every game-track app is built on the family shell (Afterimage's `game.html`,
~500 KB). Almost all of it is shared, finished code: menu, shop, IAP grants,
lives, coins, settings, themes screen, stats, missions, overlays, i18n,
ads bridge and the growth shims. **A builder replaces only the game.** The
per-game parts are wrapped in named markers (`scripts/mark_shell_regions.py`):

```
CSS   /*@@REGION NAME*/ … /*@@END NAME*/
HTML  <!--@@REGION NAME--> … <!--@@END NAME-->
JS    //@@REGION NAME … //@@END NAME
```

Read a region without loading the file:
`python3 scripts/shell_region.py <App> NAME` (prints it) — or
`sed -n '/@@REGION NAME/,/@@END NAME/p' <App>/android/app/src/main/assets/game.html`.
Replace one with `python3 scripts/shell_region.py <App> NAME --set file.txt`
(keeps the markers). **Never read the whole game.html** — it is mostly
base64 fonts and shims you must not edit.

## Regions you own

| Region | What goes there |
|---|---|
| `PALETTE` | `:root{…}` Daylight tokens + `body.midnight{…}`. Keep the shared names (`--bg --app-bg --surface --text --text-mute --border --g-play --on-accent --btn-neutral-bg --menu-tile-* --accent --accent-dim`) and add your game's role vars (`--board-bg`, piece colours…). Light default (never dark), own colour family distinct from every sibling (see `scripts/app_themes.py`), text ≥ 4.5:1 on `--bg` and `--surface`. |
| `BOARD_CSS` | Styling for the board, pieces, HUD chips, controls, animations (+ `prefers-reduced-motion`). Tokens only; no hardcoded white-on-light; no z-index literals (use `var(--z-…)`). |
| `IDENTITY_CSS` | Menu identity: `--m-bg-top --m-vignette --m-cta-grad --m-cta-glow --m-glow --m-cta-glyph --m-tile-icon --m-motif --m-motif-size` (+ midnight restatement). Motif = your game's shapes at ~12-16 % alpha. |
| `MENU_TITLE` | `.menu-logo` wordmark (UPPERCASE name) + `.menu-sub` one-line hook. |
| `BOARD_HTML` | Everything inside the game screen between header and footer: HUD chips (`.chip`), the board element(s), on-screen controls. |
| `FOOTER` | `.game-footer` buttons. Keep `goMenu()` first; Undo/Hint/Reset or the game's own booster buttons. Max 4–5. Every button must call a real function. |
| `TUTORIAL_HTML` | Coachmark card `#tutorialOverlay` with `#tut-title #tut-body #tut-foot` (text set by `TUT_STEPS`). |
| `ROLES` | `const PIPE_COLORS = {role:'var(--role)', …}` — the colour roles themes may recolour. Keys must be CSS var names you use. |
| `SHOP` | Keep every SKU id (catalog = `metadata/iaps.json`; never drop one — restore must work). You may reword `name`/`desc` (e.g. "10 Hints" → "10 Bombs") so it names your booster truthfully. Prices must stay in the coin ladder. |
| `LEVELS` | `const CAMPAIGN = [...]` (and/or `LEVELS`) — ≥ 500 entries for leveled games, each mined by your generator and passed by your content gate (seed + par, or a compact board string). `const LEVELS = CAMPAIGN;` must remain. |
| `CHAPTERS` | `const _NAMES=[…10 names…]` — Level Select chapter titles (chapters of 50 are generated from the level count). |
| `ENGINE` | The whole game. Contract below. |
| `STATS` | Stats cards (`{icon,label,sub,value}`), worded for your game. |
| `THEMES` | 7 themes: `{id,name,emoji,unlockLevel|coinCost,palette:{<every ROLES key>: '#hex'}}`. Keep `id:'default'` first and `id:'midnight'` with `coinCost:800`. Unlock levels spread over the campaign. |
| `EVENT_THEME` | The coin-sink event theme line: `colors:[5 hex]`, `palette:{…ROLES keys…}`. |

Also replace these literals outside the regions (grep for them):
`aim_tutorialDone` (tutorial key → `<short>_tutorialDone`, also in `TUT_STEPS`
code), `aim_missions_v1` (→ `<short>_missions_v1`), `aim-play-sub` id (keep
the id; it is generic enough), the Settings footer line `Afterimage
<span data-app-version>` (→ your name), and any `Afterimage`/`echo` wording in
user-visible strings. `grep -n -i "afterimage\|echo\b" game.html | grep -v
"@@\|growth-shim\|afterimage_save'"` must be empty when you finish (the
shared shims legitimately mention other apps).

## ENGINE contract (what the shell calls)

Globals the shell reads: `L` (current level object or null), `levelIndex`
(0-based), `isDailyChallenge`, `isEndless`, `gWon`, `levelStarted`.

| Function | Must do |
|---|---|
| `loadLevel(idx)` | Build level `idx` (0-based), reset per-level state, set `#hdr-level` text, render, `updateAllUI()`, `save.lastLevelProgress={level:idx+1}; persist();`, `maybeShowTutorial()`. Must also set `isDailyChallenge=false; isEndless=false`. |
| `winLevel()` | Once per level (`if(gWon)return; gWon=true;`). `playComplete()`. Compute stars 1–3 from a fair metric (moves vs par, time, mistakes, hints used). Campaign: push to `save.completedLevels`, max into `save.levelStars[idx]`, advance `save.currentLevel` (cap `CAMPAIGN.length-1`). Daily: streak/date/coins block as in the shell copy. Coins `stars*5`. `save.lastLevelProgress=null; persist();` **`gGame.clear({level:idx+1,stars,isNew,perfect:stars===3,endless,coins})`** (or `{daily:true,…}`) — the growth stack hangs off this. Interstitial cadence: `interstitialCounter++; if(interstitialCounter%3===0&&interstitialCounter>3)safeShowInterstitial();`. Fill `#complete-stars`, `#complete-msg`, set `overlay-complete` `dataset.share=shareString(stars)`, `showOverlay('overlay-complete')`, `updateAllUI()`. |
| `undoMove()` / `resetLevel()` | If the game has them (footer buttons). |
| `useHint()` | The shell's booster entry: spend a `save.hintCount` (or free while `hasUnlimitedHints()`), else open `overlay-hint` (coins / rewarded ad). Keep `giveHint()`, `hasUnlimitedHints()` (`isPremium()`), `watchAdForHint()` (`requestRewardedAd('hint')`), `spendCoinsHint()` (25 coins). `giveHint()` must give a CORRECT next step (from your solver) and call `gGame.emit('hint')`. |
| `nextLevel()` `replayLevel()` `skipLevel()` | As in the shell copy (skip = rewarded `skip`). |
| `launchEndless()` | Post-campaign endless mode (generated boards, `isEndless=true`). |
| `startDailyChallenge()` / `launchDailyLevel()` | Daily board seeded by the date (same board for everyone that day, difficulty ramps Mon→Sun), `isDailyChallenge=true`. |
| `shareString(stars)` / `shareResult()` | Spoiler-free share text: `<Name> #<day or level> — <metric>` + emoji grid if natural. |
| `TUT_STEPS` + `maybeShowTutorial()` + `window.replayTutorial` | 3-step first-launch coachmark behind your `<short>_tutorialDone` key; queued, tap-to-advance. |
| `isLevelComplete()` (optional) | Used by `goMenu()` to store Continue. |
| `window.MENU_EMBLEM` | One `<svg>` string (~120 px) that reads the core mechanic at a glance. Shown on the menu. |
| `window.MENU_MOTIF` (optional) | `<g>` string of 6–9 outline shapes in a 430×880 viewBox, `stroke="currentColor" stroke-opacity="0.13"`. |

Shell helpers you can call: `save` (live state), `persist()`, `updateAllUI()`,
`showScreen(name)` (`'menu'|'game'|'levelselect'|'shop'|'settings'|'themes'|'stats'|'missions'`),
`showOverlay(id)`/`hideOverlay(id)`, `_showMsg(text)` (toast),
`playComplete()`, `playError()`, `getAudio()` (WebAudio — synthesize your
own SFX; no audio files), `requestRewardedAd(type)`, `safeShowInterstitial()`,
`adsRemoved()`, `isPremium()`, `addLives(n)`, **`spendLife()`** (fail-state
games: call when a run is lost; returns false and opens the no-lives sheet
when empty — pure puzzles with undo never spend lives), `mulberry32(seed)`,
`gGame` (CORE adapter: `gGame.clear`, `gGame.emit('gameover',{score})`,
`gGame.emit('best')`, `gGame.addCoins`).

Score-chase games (`GROWTH_CFG.kind:'score'`): keep `save.bestScore` and
`save.gamesPlayed` (CORE reads them); on game over call
`gGame.emit('gameover',{score})`, update best + `gGame.emit('best')` on a new
best, and call `gGame.clear({stars, isNew:true, coins})` when a run beats the
run's target (so first-session rewards and missions fire). They still get a
Level Select of "stages" only if the brief says so — otherwise Play +
Daily + Endless is the loop, and `CAMPAIGN` may hold stage targets.

`GROWTH_CFG` (in `<script data-growth-config>` near the end): set
`kind`, `totalLevels`, `booster:{field:'hintCount',name,emoji,coins:25}`
to match your game. `levelBase:0`. Leave `pkg/saveKey/app/name` as scaffolded.

## Deliverables per game (folder-local only)

1. `game.html` regions above + literals; `<title>` == store name; folder name == app.
2. `test/` — generator (`gen_levels.py`/`.js`), offline verifier, and
   `test/runtime_win.js` = ONE JS expression that drives the REAL win path
   headlessly (e.g. `(()=>{ loadLevel(0); /* apply solution moves */ })()`;
   it must end in `winLevel()` being reached by playing, not by calling
   `winLevel()` on an unsolved board when avoidable).
3. Content gate `scripts/check_<app>_<property>.py` (stdlib; BLOCKS on any
   bad level; standalone `python3 scripts/check_x.py` prints OK/✗). Do NOT
   edit `pre_publish_check.py` — the integrator wires it.
4. `metadata/`: `app_identity.md`; 13 locales (`en-US ar de-DE es-419 fr-FR
   hi-IN id it-IT ja-JP pt-BR tr-TR uk zh-CN`) × `title.txt` (≤30, English
   everywhere) `short_description.txt` (≤80) `full_description.txt` (≤4000,
   opens with a hook, not "Welcome to…") `subtitle.txt` (≤30)
   `keywords.txt` (≤100) `promotional_text.txt` (≤170) `release_notes.txt`
   (≤500); `app_info.json`, `privacy.json`, `content_rating.json`,
   `review_notes.json` (copy shape from Afterimage, set this app's facts);
   `iaps.json` (scaffolded — keep SKUs, reword descriptions ≤200 for this
   game); `screenshot_headlines.json` (+ `_tablet_7`, `_tablet_10`).
   No "#1/Best/Top/Award/Download now/% off", no third-party trademarks, no
   claims the code does not back ("unique solution" only if gated).
5. `store/`: `icon_512_playstore.png` (no alpha), `icon_1024_appstore.png`,
   `feature_graphic_1024x500.png` — drawn with PIL from your own shapes
   (focal element = the mechanic; distinct from siblings), then
   `python3 scripts/sync_launcher_icons.py <App>`.
6. `test/screenshot_taps.json` — 11 gameplay-only slots at distinct levels
   and themes (copy the structure of `Afterimage/test/screenshot_taps.json`,
   rewrite every expression for your game). Screenshots themselves are
   captured on an emulator (`capture_screenshots.py`) — not here.
7. `metadata/STORE_PASTE.md` via `python3 scripts/gen_store_paste.py <App>`.

## Verify before you finish

```
python3 scripts/check_<your gate>.py
node scripts/runtime/smoke_all.js <App>
node scripts/runtime/growth_behaviour.js <App>
node scripts/runtime/iap_grants.js <App>
python3 scripts/java_compile_check.py <App>
python3 scripts/pre_publish_check.py <App>     # only screenshot/ID blockers may remain
```
Then drive it in headless Chromium with real input events (taps/swipes at
the board's coordinates) at 360×800 and 800×1280: play level 1 to the win,
a mid level, a late level, daily, undo/hint/reset, Level Select, Themes
(every theme recolours the board), midnight. Screenshot those to your
scratchpad and look at them. Fix what you see.
