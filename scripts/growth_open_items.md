# Growth open items — 2026-05-25

Items the agent intentionally LEFT for manual handling, with the
reasons + the exact change needed when you pick them up. Items below
are NOT silently autopiloted (machine translation, English-as-default
listing copy, opening new Play Console SKUs are all explicit user
decisions).

---

## A. Cross-promo: turn UnblockPuzzle into a TARGET in the live games

UnblockPuzzle is currently in Play review (no Play link yet). Per the
2026-05-25 growth spec, it is excluded as a cross-promo TARGET in
WaterSortPuzzle / Nonogram / Puzzle2048. Once it goes live, do the
following (the TODO markers below all point at the same change):

1. `WaterSortPuzzle/android/app/src/main/java/com/pegasusgames/watersortpuzzle/MainActivity.java`
   → uncomment the `com.pegasusgames.unblockpuzzle` line in
     `CROSS_PROMO_PACKAGES`.
2. `WaterSortPuzzle/android/app/src/main/AndroidManifest.xml`
   → add `<package android:name="com.pegasusgames.unblockpuzzle" />`
     inside `<queries>`.
3. Same two changes in **Nonogram** and **Puzzle2048**.
4. `scripts/_growth_shim_b.html` → uncomment the UnblockPuzzle entry
   in `ALL_PROMO`.
5. Add the live Play link to the UnblockPuzzle share-text composer
   (Part F) — see "F. Share line for UnblockPuzzle" below.
6. Append an UnblockPuzzle row to each app's "More Games" list
   (`PROMO_GAMES` / `MORE_GAMES`) — installReward 200, welcomeBonus 100.

Once these six edits ship, also do the symmetric work for PipeConnect
if it has gone live too.

---

## B. Play Games Services — Play Console configuration required

The native code (PGS v2 dependency, NativeBridge `submitScore` /
`showLeaderboard` / `signInPlayGames`, JS hooks, menu Leaderboard
button) is wired in Part G, but each app needs **Play Console** setup
before leaderboards become real (until then, the synthetic
weekly-tournament bracket is the fallback — that's by design).

For each of the 4 apps:

1. Play Console → **Grow → Play Games Services → Create a new project**
   linked to the existing app listing.
2. Copy the **project ID** (numeric, looks like `123456789012`) into:
   `<App>/android/app/src/main/AndroidManifest.xml`
   → replace the placeholder
     `<meta-data android:name="com.google.android.gms.games.APP_ID"
                  android:value="@string/games_app_id" />`
     by writing the ID into `<App>/android/app/src/main/res/values/strings.xml`
     as `<string name="games_app_id">\ 123456789012</string>` (the
     leading backslash + space matters — Google's docs).
3. Create **one leaderboard per app** under PGS → Leaderboards.
   Recommended IDs:
   - WaterSortPuzzle: `level_progress`
   - Nonogram:        `level_progress`
   - Puzzle2048:      `best_score`
   - UnblockPuzzle:   `level_progress`
4. Copy each leaderboard's **leaderboard ID** (looks like
   `CgkI…`) into `<App>/android/app/src/main/assets/game.html` —
   replace `'TODO_FROM_PLAY_CONSOLE'` with the real string.
5. Publish the PGS project (separate from publishing the app).

The build still works without these — `Android.submitScore` and
`Android.showLeaderboard` no-op until the PGS project is configured.

---

## C. Localization gaps

Machine audit on 2026-05-25 found ALL 4 apps × 12 locales × 4 required
metadata files (title / short_description / full_description /
release_notes) PRESENT and non-empty. No locale gaps detected at scan
time.

Per the 2026-05-25 release-notes append (Part I), the new bullet
points are appended to **en-US/release_notes.txt only** in this pass —
the 12 non-English locales still carry the older release notes and
need a human-written localization pass before each app's next
versioned upload to Play Console.

Open files to localize:

- `WaterSortPuzzle/metadata/<locale>/release_notes.txt`
- `Nonogram/metadata/<locale>/release_notes.txt`
- `Puzzle2048/metadata/<locale>/release_notes.txt`
- `UnblockPuzzle/metadata/<locale>/release_notes.txt`

…for each `<locale>` in: ar de-DE es-419 fr-FR hi-IN id it-IT ja-JP
pt-BR tr-TR uk zh-CN.

---

## D. Tier-2 (pt-BR / id / hi-IN / tr-TR) hand-review

Audit found that all four apps' **pt-BR full_description.txt** contain
inline TODO/placeholder markers (literal "TODO" or "please review" or
similar). Per spec policy these are NOT auto-rewritten — a Brazilian
Portuguese native speaker should rewrite them so they read naturally
(not 1:1 calques from English).

- `WaterSortPuzzle/metadata/pt-BR/full_description.txt` — explicit-todo
- `Nonogram/metadata/pt-BR/full_description.txt` — explicit-todo
- `Puzzle2048/metadata/pt-BR/full_description.txt` — explicit-todo
- `UnblockPuzzle/metadata/pt-BR/full_description.txt` — explicit-todo

Indonesian (id), Hindi (hi-IN), and Turkish (tr-TR) full_descriptions
passed the machine audit (no obvious placeholders, reasonable length)
but a native speaker should still glance at each before Play Console
upload — calque-detection requires a fluent reader.

---

## E. ASMR / relax / brain keyword density

Per-app keyword presence in `en-US/full_description.txt`:

- WaterSortPuzzle: ok (5/7 markers present)
- Nonogram:        ok (6/7)
- **Puzzle2048:    THIN — only "offline" found; missing "asmr",
  "relax", "satisfying", "brain", "calm", "mindful"**. Auto-rewriting
  was rejected because not every keyword fits a competitive merge
  game (e.g. "ASMR" reads false for 2048). Hand-add the subset that
  fits naturally — "satisfying merge", "brain training", "calm
  offline play" all work for the genre.
- UnblockPuzzle:   ok (6/7)

---

## F. Share-text line for UnblockPuzzle (no Play link yet)

Per spec Part F2: the three live apps' share-a-win composer uses their
real Play link. UnblockPuzzle's composer is wired in Part F WITHOUT a
Play link — it brags + "search Unblock Puzzle by Pegasus Games"
instead. When UnblockPuzzle goes live, edit:

- `UnblockPuzzle/android/app/src/main/assets/game.html` — find the
  `_GROWTH_SHARE_LINK` constant and set it to
  `https://play.google.com/store/apps/details?id=com.pegasusgames.unblockpuzzle`.

---

## G. Reset progress on streak shield refill

The streak-shield refill (Part D) tops up a free shield once every 7
days of maintained streak. The default UI shows "🛡 Streak shield: N"
with a "Buy +1 for 200 🪙" button when N=0. If you'd rather rate-limit
purchases (e.g. max 3 owned at a time), edit the cap constant in the
Part D growth shim — currently uncapped on purpose.

---

## H. Win-back coin grant — per-app save shape

The Part A shim grants the Day-7 win-back +100 coins by writing into
the first JSON localStorage key from {save, state, gameState, progress}
that has a `coins` field. Test on each app once after a live install
that the credit appears on the menu after a 7-day-absent return.
