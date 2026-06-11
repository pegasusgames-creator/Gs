# Pegasus Games — Build the next three games (Claude Code task)

**Goal:** (1) add **Ditto**, **Green Light**, and **Stack** to the backlog as the next three greenlit builds, then (2) build each to a production, shippable state in the existing Pegasus single-file architecture. The mechanics are already prototyped and the hard parts (generators/solvers) are **verified working** — the job is production, not re-deriving rules.

> Prototypes (`ditto.html`, `greenlight.html`, `stack.html`) are vendored at `docs/prototypes/` — they are the **source of truth for game logic** (200+ daily seeds verified solvable). Port that logic *unchanged*; this doc adds the production layer around it.

Build order: **Ditto → Stack → Green Light**. One game at a time; after each: screenshot menu + gameplay + win on phone and 7" tablet, light + midnight, and stop for review before the next.

**Progress:**
- [x] Part 1 — backlog rows greenlit (docs/APP_IDEAS.txt, 2026-06-10)
- [x] Next-1 **Ditto → Afterimage** — built to reviewable state (2026-06-11, commit `feat(Afterimage)`). Post-review remaining: 13-locale metadata, store assets via `SCREENSHOT_STUDIO.md`, STORE_PASTE/COMPETITIVE_AUDIT rewrites, Firebase entry + real AdMob ids + PGS leaderboard at handoff, keystore 3-way backup, tablet-surface screenshots.
- [x] Next-2 **Stack → Overlay** — built to reviewable state (2026-06-11, commit `feat(Overlay)`). Same deferred list as Afterimage (locales, store assets via SCREENSHOT_STUDIO, handoff trio, keystore backup, tablets).
- [x] Next-3 **Green Light → Hunch** — built to reviewable state (2026-06-11, commit `feat(Hunch)`). Same deferred list (locales, store assets via SCREENSHOT_STUDIO, handoff trio, keystore backup, tablets).

---

## Part 1 — Backlog (done)

| Order | Codename | Mechanic (one line) | Slug / package | Aliases (dedup) |
|---|---|---|---|---|
| Next-1 | Ditto | move; a clone replays your moves 2 turns late; park it on a plate while you reach the exit | `afterimage` → com.pegasusgames.afterimage | ditto, echo, delayed clone, lag, time offset |
| Next-2 | Stack | slide 3 transparent sheets so the topmost-colour composite matches a target | `overlay` → com.pegasusgames.overlay | stack, overlay, transparencies, gels, layers, acetate |
| Next-3 | Green Light | deduce the board's hidden rule by testing patterns (green=obeys / red=breaks) | `hunch` → com.pegasusgames.hunch | green light, hidden rule, induction, rule guess, zendo |

### ⚠️ Naming / trademark (do not skip)
`Ditto`, `Stack`, and `Green Light` are **internal codenames only**. For store/display:
* **Ditto** collides with a Pokémon → ship as **Afterimage** (alts: Encore, Lagstep, Two-Step).
* **Stack** collides with Ketchapp's famous "Stack" (ASO poison) → ship as **Overlay** (alts: Acetate, Gels, Lightbox).
* **Green Light** is weak/ambiguous → ship as **Hunch** (alts: Aha, The Rule, Deduce).
Use the slug/package above and the suggested display name, but leave a `TODO(name): confirm with owner` in each `app_identity.md` and `strings.xml`. Don't submit to any store under a codename.

---

## Part 2 — Shared build conventions (apply to ALL three)

**Scaffold by cloning, don't greenfield.** Copy an existing app repo as the skeleton, then strip only the game core. (Afterimage used PipeConnect — the freshest plumbing; any shipped app works.)
* **Keep verbatim:** the Android WebView wrapper (`MainActivity.java`, `NotificationReceiver/Helper`, `AndroidManifest`, `res/`), the growth shims (`data-growth-shim="A/B/D/E/F/G/MENU/SUBS"`), AdMob/notification config, the `:root` token theming + midnight, the metadata folder structure.
* **Replace:** the `#screen-game` markup + the game's JS core. Re-point the MENU shim's Continue/Daily to the new core.
* **Clone gotchas found building Afterimage (check every one on Overlay/Hunch):**
  - `build.gradle` **namespace** AND applicationId; signing config must tolerate missing `keystore.properties`.
  - New dedicated keystore (`keytool`, alias = slug); record SHA1; never copy another app's.
  - `google-services.json` is package-locked — re-point the client locally; real Firebase entry at handoff.
  - AdMob ids back to **test ids** (red line: never reuse another app's units).
  - G-shim `LEADERBOARD_ID` resets to `TODO_FROM_PLAY_CONSOLE` (the clone carries the donor's real id!).
  - Master shims need the new app's branches: save-key probe (A+MENU), seed offset (MENU `gameIdHash`), pkg heuristic (B `currentPkg`), sanity words, emblem illustration branch; add the package to `check_cross_promo_pkgs.CANONICAL`; then `reinject_all_shims.py`.
  - Legacy `body.midnight` hardcoded chrome colors from the donor need re-paletting to the new identity.
  - Audit-addendum functions are IIFE-scoped — export to `window` anything the main script calls.
  - Win path needs a **won-latch** (`gWon`) — input in the ~300ms before the win overlay shows can re-trigger the win handler.

**Reuse the family chrome:** MENU shim owner + menu-skin from `MENU_REDESIGN.md` + per-game `--m-*` tokens + emblem/motif. Save/continue contract: persist in localStorage so the shim's "Continue · …" works. Wire win path to existing coin/streak grants (`gOnAnyClear`, `gOnDailyDone`). Daily seed: `dayNum = floor((Date.now() - Date.UTC(2026,0,1)) / 864e5)`; seed `(day*2654435761%2147483647)+1`; **Daily + Endless** modes. Share = performance, not solution (Wordle rule), via `Android.shareText` with clipboard fallback.

**Quality floor:** interactive first-run tutorial (3–4 steps, replayable from settings); difficulty ramp Mon-easy→Sun-hard; phone + 7"/10" tablet; `prefers-reduced-motion`; colorblind-safe (Overlay adds shapes/letters); fully offline; key controls for desktop QA; 60fps low-end (transform/opacity only).

**Per-game `metadata/app_identity.md`** using the existing schema.

---

## Part 3 — Game specs (prototype = canonical; these are the production deltas)

### GAME 1 — Ditto → **Afterimage** (BUILT — see Progress)
6×6 grid; echo replays your move from 2 turns ago; win = you on exit AND echo on plate same turn; collision/swap = rejected move (shake+toast), never a loss. Solver = BFS over (b,c,q0,q1) → **Par** (true optimum, shown + scored: ≤par = 3★). Bands: easy par 5–8 · med 9–13 · hard 14–20, wall density ramps; reject plate on the natural shortest path. Controls: swipe/arrows/WASD/d-pad; full undo; reset; hint = next optimal move (coin/ad). Identity: *blueprint-echo* — light blueprint Daylight, prototype navy as Midnight; cyan you, coral echo (trail), gold plate, dashed-green exit; cube + dashed duplicate emblem. Share: `Afterimage #<day> — <moves> moves` (+ ⭐ if ≤ par).

### GAME 2 — Stack → **Overlay**
Three 5×5 sheets, offsets ∈ [−2,2]; composite = topmost non-transparent (sheet 3 over 2 over 1); match the target. Generator solvable by construction (prototype `gen()`): random sheets (4–8 cells), pick solution offsets, target = composite; require ≥6 colour cells; scramble start (≠ solution). **Production:** bias targets toward recognizable shapes (connected/symmetric/icons) — the snap-to-picture is the payoff; difficulty via colours, density, offset range (±1 → ±2). Drag sheets (snap to cell, clamp), arrows fallback, z-order legend; ghost outline on unmatched target cells. Identity: *darkroom* — near-black, magenta/cyan/amber gels, "develop" bloom animation on match + chime + haptic; three offset translucent squares emblem; **each colour also carries a tiny shape/letter** (colorblind). Share: `Overlay #<day> — <slides> slides 🟩` (no picture). Accept: always solvable, never solved at start, drag snapping clamped, colorblind toggle, develop fires only on exact match.

### GAME 3 — Green Light → **Hunch**
4×4 toggle lights; TEST → green (obeys hidden rule) / red (breaks); unlimited tests, history shelf; classify 3 mystery boards Obeys/Breaks; all 3 right = cracked; score = tests used. Rule catalog: prototype base (count / per-row-col / symmetry / adjacency / connectivity / comparison) **expanded to ≥15–18 rules across ≥5 categories** (exactly-N lit, diagonal symmetry, lit cell in every 2×2 block, equal halves, corners rule, no full row, 180° rotation…). **Critical production upgrade:** the 3 mystery boards must *uniquely identify* the day's rule against the whole catalog — brute-check that no other catalog rule classifies all 3 identically to the true rule. Wrong submit: show N/3, return to lab, tests keep counting (no hard fail). Identity: *signal lab* — dark slate, green/red status light, experiment shelf, traffic-light-over-grid emblem; calm/cerebral juice; onboarding hand-holds one full deduce→guess loop. Share: `Hunch #<day> — cracked in <tests> 🟢` (optional 🟢🔴 strip — order only).

---

## Part 4 — Global acceptance & process
- [ ] All growth shims, theming, wrapper, AdMob/notifications carried over and functional; MENU shim intact (no competing shim); menu-skin + emblem/tokens applied.
- [ ] Daily + Endless; daily seed identical across devices; spoiler-free share to clipboard/share sheet.
- [ ] Generators/solvers = verified prototype logic; 200 daily seeds spot-checked per game (Afterimage: `Afterimage/test/verify.sh`).
- [ ] Phone + 7"/10" tablet, light + midnight, reduced-motion, colorblind (Overlay), offline, 60fps low-end.
- [ ] Tutorial per game; `app_identity.md`, `STORE_PASTE.md`, `COMPETITIVE_AUDIT.md` drafted; `TODO(name)` for final store names.
- [ ] Screenshots (menu/gameplay/win, phone+tablet, both themes) for review before the next game. (Commits to main per repo convention — no feature branches.)
- After all three ship, extend `ALL_PROMO` so the 5+3 portfolio cross-promotes (only once each has a Play link).
