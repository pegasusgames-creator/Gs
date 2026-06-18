# Pegasus Games — Claude Code Instructions

Portfolio of ~200 Android apps/games on a shared WebView wrapper. Each top-level folder (except `_template/`, `_release/`, `docs/`, `scripts/`) is one app with `game.html` inside `MainActivity.java`. Read end-to-end before doing anything.

**Repo layout:** `CLAUDE.md` + `README.md` at root; `docs/` = `SHIP_GAME.md`, `QUALITY_PLAYBOOK.md`, `APP_ARCHETYPES.md`, `TRANSLATIONS.md`, `COMPETITIVE_BENCHMARK.md`, `NOTIFICATIONS_IMPL.md`, `IAP_CATALOG.md`; `scripts/` = Python tools (bare names in this doc resolve to `docs/` or `scripts/`). Run from repo root: `python3 scripts/pre_publish_check.py <AppName>`. Each app lives in `<AppName>/`.

**Key scripts:** `pre_publish_check.py` (master guard — runs every check below), `build_release.py`, `gen_handoff.py`, `gen_translations.py`, `gen_store_paste.py`, `consult_designer.py`, `init_app_metadata.py`, `capture_screenshots.py`, `wrap_screenshots.py`, `wrap_tablet_screenshots.py`, `app_themes.py`, `dedup_similar_apps.py`, `cleanup_repo.py`, `fix_all_apps.py`, `prepare_for_publish.py`, `migrate_to_per_app_keystores.py`.

## Companion files

- `SHIP_GAME.md` — MASTER RELEASE WORKFLOW. On "ship X" execute all 8 phases without asking unless Hard Blocker.
- `QUALITY_PLAYBOOK.md` — design/UX/gameplay/monetization bar.
- `APP_ARCHETYPES.md` — Layout (9) × Mascot (5) × Voice (8) × Texture (8). New app picks one each in `app_themes.py`. Phase 1.
- `TRANSLATIONS.md` — 13 locales: `en-US`, `ar`, `de-DE`, `es-419`, `fr-FR`, `hi-IN`, `id`, `it-IT`, `ja-JP`, `pt-BR`, `tr-TR`, `uk`, `zh-CN`. Russian excluded. **`id` (not `id-ID`); `uk` (not `uk-UA`).** Title stays English. Phase 4.5.
- `COMPETITIVE_BENCHMARK.md` — top-grossing analogs + patterns flagships match. Phase 1 of every flagship.
- `NOTIFICATIONS_IMPL.md` — Java + JS reference for local notifications.
- `IAP_CATALOG.md` — canonical IAP descriptions (≤200 chars).

**Scripts:** `gen_translations.py` uses `ANTHROPIC_API_KEY` (fallback `OPENAI_API_KEY`); writes `.rejected` on overflow (hand-trim + rename). `gen_store_paste.py` assembles `<App>/STORE_PASTE.md` with `<uk>`, `<id>` (never `<uk-UA>`/`<id-ID>`). `cleanup_repo.py` moves BLOCKED clones + deleted apps OUT (`--dry-run` first).

## Canonical contact info and URLs

Shared across all apps. Never invent per-app URLs/emails.

| Field | Value |
|---|---|
| Developer name | `Pegasus Games` |
| Developer email | `pegasusgames@atomicmail.io` |
| Privacy URL (general) | `https://pegasusgames-creator.github.io/privacy.html` |
| Privacy URL (kids) | `https://pegasusgames-creator.github.io/privacy-kids.html` |
| Support URL | `https://pegasusgames-creator.github.io/` |
| Marketing URL | `https://pegasusgames-creator.github.io/` |
| Cross-promo (general) | `https://pegasusgames-creator.github.io/promo.json` |
| Cross-promo (kids) | `https://pegasusgames-creator.github.io/promo-kids.json` |
| Copyright | `© 2026 Pegasus Games` |

**Per-app `store/privacy-policy.html` MUST NOT exist** (delete on sight; legal liability). **Per-app Data Safety forms ARE per-app** — shared policy is superset; each app's form reflects what THAT app does. Privacy URL must include `.html` (no trailing slash).

## Keystore management — per-app, single key, no PEPK

Every app has OWN `<App>/android/keystore.jks` + `keystore.properties` (gitignored). One keystore per app, no PEPK. (May 2026: Nono accidentally signed with WS's keystore → permanently locked upload key.)

**Play App Signing:** AAB signed with `keystore.jks` to new listing auto-enrols — `keystore.jks` = upload key; Play generates app signing key server-side. Never opt into PEPK.

**Current state:** WS, Nono, P2048, PipeConnect, UB each have dedicated keystore. ~154 long-tail apps share `pegasusgames-release.jks` (`E0:BD:7F:24:...`); migrate via `migrate_to_per_app_keystores.py` BEFORE shipping (reset 1-3 business days).

**Rules:**
1. **NEW app → new keystore.** `cd <App>/android && keytool -genkey -v -keystore keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias <appname>`. 16+ char alphanumeric password. `migrate_to_per_app_keystores.py --app NewApp` one-step.
2. **Back up 3 ways within 24h** + before first Play upload: local (gitignored); encrypted Google Drive in `pegasusgames@atomicmail.io`; USB "Pegasus Keystores".
3. `keystore.properties` (gitignored, `.template` next to it): `storeFile=keystore.jks`, `storePassword`, `keyAlias`, `keyPassword`. Record passwords + SHA1 in password manager.
4. Record SHA1 in `<App>/metadata/app_info.json:upload_key_sha1` after first upload. Verify: `keytool -printcert -jarfile app/build/outputs/bundle/release/app-release.aab | grep SHA1`.
5. **NEVER copy `keystore.properties` between apps.**
6. **If lost:** new keystore + 3-way backup FIRST, then Play Console → Setup → App integrity → App signing → Request upload key reset. Update `upload_key_sha1`.

`check_keystore_present` BLOCKS if `keystore.jks` missing, `keystore.properties` missing or `storeFile ≠ keystore.jks`, SHA1 mismatch. WARNS if `upload_key_sha1` unset.

**Phase 7 upload:** `./gradlew :app:bundleRelease` → `<App>/android/app/build/outputs/bundle/release/app-release.aab`.

**PEPK quirk (P2048 only):** PEPK export-and-upload permanently registered original `keystore.jks` (2026-04-21, alias `puzzle2048`) as app signing key. Irreversible. New upload keystore (2026-05-11, alias `upload`) is now `keystore.jks`; PEPK'd original at `keystore.jks.pepk-archive`. Only `keyAlias=upload` differs vs per-app `<appname>`. **Don't run PEPK on any other app.**

## Per-app folder structure

```
<AppName>/
├── android/   ios/
├── store/
│   ├── icon_512_playstore.png        # 512×512 no alpha
│   ├── feature_graphic_1024x500.png  # no transparency
│   ├── icon_1024_appstore.png        # 1024×1024 no alpha
│   └── screenshots/
│       ├── phone/      raw/ + 01..07.png   # 1080×2400 · 7 distinct
│       ├── tablet_7/   raw/ + 01..02.png   # 1200×1920 · 2 distinct
│       ├── tablet_10/  raw/ + 01..02.png   # 1800×2560 · 2 distinct
│       └── iphone_6_9/                      # 1320×2868 (Apple)
├── test/  seed_screenshot_state.js, screenshot_taps.json
└── metadata/
    ├── app_identity.md, screenshot_headlines.json + _tablet_7.json + _tablet_10.json
    ├── en-US/  title.txt (≤30) short_description.txt (≤80)
    │           subtitle.txt (≤30) full_description.txt (≤4000)
    │           keywords.txt (≤100) promotional_text.txt (≤170)
    │           release_notes.txt (≤500)
    ├── ar/ de-DE/ es-419/ fr-FR/ hi-IN/ id/ it-IT/ ja-JP/ pt-BR/ tr-TR/ uk/ zh-CN/
    ├── app_info.json (category, ads, audience, URLs, package)
    ├── privacy.json (Data Safety + Apple Privacy)
    ├── content_rating.json (IARC + Apple age rating)
    ├── iaps.json (IAP catalog == MainActivity)
    └── review_notes.json
```

JSON schemas in `SHIP_GAME.md` Phase 4. Don't invent fields; copy from WS.

## Store requirements (2026)

Full limits in `SHIP_GAME.md` Phase 4.
- **Google:** 512×512 icon (no alpha), 1024×500 feature graphic, 2-8 phone screenshots (1080×2400 recommended), Data Safety, IARC rating, privacy URL — all mandatory. Org accounts EXEMPT from 12-testers / 14-day closed-testing rule; promote directly to prod.
- **Apple:** iOS 26+ SDK (since 2026-04-28), 1024×1024 icon, 6.9" screenshots (1320×2868), Privacy Nutrition Label, granular age rating since iOS 26 — all mandatory.
- **Both:** NO "#1", "Best", "Top", "Award winning", "Download now", "Install now", "% off" in copy or screenshots.

## IAP correctness invariants

Violating any = tap Buy, get nothing, still charged. `check_iap_invariants` enforces.

1. **VALID_PRODUCTS == `iaps.json` SKUs.** `MainActivity.java`'s `launchBillingFlow` rejects unlisted SKUs. Generate `VALID_PRODUCTS` from `iaps.json`; never hand-curate.
2. **Every PURCHASED purchase acknowledged within 3 days.** Consumables via `consumeAsync`; non-consumables + subs via `acknowledgePurchase`. `CONSUMABLE_PRODUCTS` declares path; both wired in `handlePurchase`. Unacknowledged = auto-refunded.
3. **`game.html` defines `window.onPurchaseSuccess`** (directly or alias to `onPurchaseComplete`). Java bridge calls `window.onPurchaseSuccess(id)`; undefined = silent drop. Grant function MUST NEVER throw. Historical: ~140 apps defined only `onPurchaseComplete`; retention hook chained to undefined `_origPurchase = window.onPurchaseSuccess`, dropping every non-`season_pass` SKU.
4. **Unhandled SKUs fall through to `window.iapDeferGrant(id)`** which writes `localStorage.pendingGrants`. `window.replayPendingGrants()` runs each game load — lets a SKU bought before its mechanic existed replay once added.

**Catalog rule:** SKUs hidden from shop UI per archetype (`archetype.json`); catalog (`iaps.json`) NEVER filtered — restore must work for all SKUs.

**Future apps:** SHIP_GAME Phase 2 generates `VALID_PRODUCTS` from `iaps.json` + injects canonical `onPurchaseSuccess` alias + `replayPendingGrants` safety net. Phase 5 re-asserts.

## Retention-feature parity

Every game selling `season_pass_monthly` MUST have in `game.html`:
- `window.replayPendingGrants` on init (IAP invariant 4)
- wrapped `window.onPurchaseSuccess` → original `onPurchaseComplete`/switch (grants every known SKU fully), unknown → `pendingGrants`
- `isSeasonActive()`/`hasActiveSeasonPass()` + `isPremium()`/`isWeeklyActive()` helpers; `adsRemoved()` = `removeAds || isPremium()` gates every ad-show path
- hint counter (`hintCount`/`hintPack`) if `hint_pack` sold; `undoPack` counter if `undo_pack` sold; decrement skipped while pass active
- `starter_pack`, `season_pass_monthly`, `weekly_pass` handlers grant FULL bundle (not partial)
- Free Coins menu surface (rewarded ad, 25 coins / 4h cooldown)
- Continue button when last-progress exists
- theme progress strip + theme-unlock card with 6-chip palette preview
- 7-day login-streak reward ladder
- starter-pack-on-first-launch popup
- Restore Purchases + Privacy Policy in Settings; `MainActivity.java` exposes `@JavascriptInterface restorePurchases()` and `openUrl(String)`

Usually runtime-injected via audit-addendum `<script>` at bottom of `game.html` — static menu ≤6 tappable (`check_menu_button_count`). `check_retention_features` + `check_menu_completeness` enforce.

**Subscription/bundle promise parity.** Every IAP-description benefit needs a code flag. `season_pass_monthly $4.99/mo` ("ad-free + 100 daily coins + all themes + unlimited hints") requires `adsRemoved()`, `lastSeasonGrantDate` daily-grant, `isPremium()` theme unlock, premium-gated hint decrement. `weekly_pass $1.99/wk` ("+50 daily coins") requires `lastWeeklyGrantDate` +50 grant. Monthly priced ABOVE weekly AND grants bigger daily bonus — monthly = unambiguous best deal. 2048-style: word "unlimited hints" as "unlimited undos". `check_subscription_parity` enforces.

## Coin tier ladder

Every game selling any coin pack ships the full four-tier ladder (strictly monotonic: each tier costs more AND gives more coins AND better coins/$ rate):

| SKU | Price | Coins | Coins/$ |
|---|---|---|---|
| `coins_small`  | $0.99 |  100 | ~101 |
| `coins_medium` | $2.99 |  400 | ~134 |
| `coins_large`  | $4.99 |  800 | ~160 |
| `coins_mega`   | $9.99 | 2000 | ~200 (best value — anchor) |

Replaces pre-2026-05 layout where `coins_large` was a $2.99 cheap-anchor below `coins_medium` — confused returning buyers, forbidden. Partial ladders also forbidden. `check_coin_tier_ladder` blocks both. (`lives_5_coins`-style in-game-currency products don't count.)

## Booster catalog by genre

| Genre | Booster set |
|---|---|
| Sort-puzzle (Water Sort, etc.) | Color Reveal (hint), Steady Pour (undo), Fresh Start (restart), Extra Tube, Magic Wand |
| Picross (Nonogram, etc.)       | Hint, Undo, Reset, Check, Reveal Row, Reveal Cell |
| 2048-like                      | Undo, New Game, Magic Merge, Remove Tile |

Shop SKU catalog and in-game booster set must match (sold pack needs mechanic; booster button needs coins-or-ad cost). `check_booster_catalog` enforces by genre keyword.

## Seasonal events

Every game ships `SEASONAL_EVENTS` covering at least October (Halloween), December (Winter), February (Spring). On init in matching month: temporarily unlock event theme + inject 5 bonus levels with event palette (leveled games) OR grant 7-day 1.5× multiplier (non-leveled like 2048). Menu shows event banner while active. `check_seasonal_events` enforces.

## Weekly tournament (synthetic bracket)

Track best-metric-this-week (best-level for level games, best-score for 2048), map through per-game `WEEKLY_BRACKETS` (10/25/50/75% tiers), show "🏆 This week — <metric> · Top <pct>%", reset Monday 00:00 local, award 100 coins for top 25% / 250 for top 10%, granted at week rollover next time app opens within 7 days.

## Level count floor — 500 levels on release

**Every game with discrete levels ships ≥500 levels on release.** A thin
campaign (60, 120, 150) reads as unfinished next to category leaders and
caps retention/LTV. The bar is 500 *solvable, verified* levels, not 500
padded ones — generator-based games (Afterimage, Hunch, Overlay, PipeConnect,
WaterSort, Unblock, Sokoban, Nonogram) mine the count from their own seed
generator + acceptance test (so every level still passes its solvability /
uniqueness / par-optimality gate), then store the campaign list. Non-leveled
games (Puzzle2048-style score chase, FlappyBird) are exempt — the rule is
"has discrete levels", not "is a game".

`check_min_levels.py` enforces it: a `const CAMPAIGN`/`LEVELS` array under 500
BLOCKS for any app not yet live. Already-live apps released under the old bar
(WaterSortPuzzle, Nonogram, Puzzle2048, UnblockPuzzle) are grandfathered to a
WARN — expand them on their next content update, never regress a live level
set in a rush (changing live level data resets/raptures existing players'
progress; do it deliberately, behind the solvability gates, with a save
migration). Nonogram already meets the bar (500 pregen + runtime-unique).

## Red lines — never do these

Any one can terminate the developer account.

1. **No two apps with byte-identical `game.html`.** Replace gameplay logic immediately after copying `_template/`. Blocked.
2. **App folder name == `<title>` tag.** Folder `Metronome/` cannot contain `<title>Dice Roller</title>`.
3. **No templated store listing copy across apps.** Title / short / subtitle / full hand-written per app.
4. **No reused AdMob IDs, IAP product IDs, or package names.**
5. **No batch-publishing in short windows.** 2-3 unique apps/week sustained ceiling. Silence → 5+ in one week trips Google's velocity heuristic.
6. **No two apps shipping same window with visually identical store assets** (same icon focal, byte-identical feature graphic, screenshots that only swap inner gameplay over shared frame). `check_cross_app_asset_similarity` + `check_screenshot_template_reuse`.
7. **Don't "de-duplicate" wrapper code** (`MainActivity.java`, `NotificationReceiver.java`). Shared SDK infra (same pattern as Voodoo/SayGames/King). Google penalizes content similarity, not wrapper similarity.
8. **No committed secrets** (`keystore.properties` w/ real passwords, sensitive `google-services.json`). `.gitignore` them.
9. **No push notifications to Kids apps.** Play Families forbids. See `QUALITY_PLAYBOOK.md` §11.8.
10. **Never publish any of the 33 BLOCKED_APPS placeholder clones** without rewriting `game.html` first. Byte-identical Dice Roller `game.html` across 33 folders is the single highest-risk thing in this repo. `check_blocked_apps` — never override.

## Shipping cadence

**2 genuinely-distinct apps/week from week 1**, ramping to 3+/week. User upload ~30 min/app via `RELEASE_HANDOFF.md`.

Risk = **similarity between apps**, not velocity. Repetitive Content classifier triggers on: same `game.html` with renamed functions; same icon composition with swapped colors; same screenshots with swapped frame contents; same listing copy with template substitutions; same screen flows.

**"Unique enough" = all 5:** (1) `game.html` mechanic + state + level generation different; (2) icon focal element different; (3) feature graphic layout different; (4) screenshot inner content different (frame can be shared, gameplay can't); (5) listing copy hand-written. **Not capacity-limited** (don't vary): wrapper code, monetization stack, brand colors/fonts/footer, SDK versions.

**Anti-suspension:** one app per genre cluster per 7-day window; crash <1%, ANR <0.5% (50+ portfolio spike = account review); never publish from `BLOCKED_APPS`; opening-line variety (Google detects "Welcome to {AppName}!"); cross-promo required from app #2; AdMob stagger max 2/day, 5/week; reset icon palette pool every 10 apps (after 30 apps perceptual hash collisions force textured/patterned backgrounds).

**Sustaining 100+:** run `pre_publish_check.py` portfolio-wide weekly (N² pairwise); diversify ~⅓ puzzle / ~⅓ casual / ~⅓ utility. Fix at app #60 = fix that app's distinctness, not bypass the check.

## Required checks before any publish

Run `pre_publish_check.py <app>` — zero blocking. Covers all gates listed below + asset/metadata presence checks, canonical URL match, no `pegasusgames.example`/`@outlook.com`/`ENTER_*` placeholders, 4 archetypes set, all 13 locales, menu button count ≤6. **If any blocker fails: stop.** Retention-stack games (sell `season_pass_monthly`) additionally enforced; long-tail utility apps exempt.

## State of the apps (audit 2026-05-28)

- **Ad stack = AdMob + mediation (2026-06-15).** The 8 AdMob apps (WS, Nono, P2048, UB, PipeConnect, Afterimage, Hunch, Overlay) dropped AppLovin MAX entirely; ads run AdMob-only with mediation adapters for Meta/Unity/Mintegral/Pangle/InMobi (per-app `MEDIATION_SETUP.md` maps ad units→dashboard groups; network IDs are dashboard-side TODOs, none in the APK). Migration scripts: `remove_applovin.py` (Part 1), `harden_admob.py` (Part 2: FIFO reward queue, load backoff + single-inflight, lazy rewarded via `preloadRewarded()` bridge + the `ADPREP` game.html shim, 50-min freshness guard, 60s interstitial floor, and per-app `VALID_REWARD_TYPES` widened so `extra_life`/`free_coins`/`hint` rewarded ads actually show), `add_mediation.py` (Part 3). The other ~166 apps are AppLovin-MAX-only with placeholder IDs (no AdMob bridge) — untouched. Don't reintroduce `USE_APPLOVIN`/`Max*` to these 8.
- **Hero:** WaterSortPuzzle — meta-loop, live ops, real mascot.
- **Shipped (4):** WS (vc 38 / v2.1.15), Nono (vc 22 / v1.2.14), P2048 (vc 24 / v1.2.15), UB (vc 22 / v1.2.14, live 2026-05-29, 1+ downloads). Retention-complete. 13 locales; phone + tablet 7"/10". Next release: bump versionCode, rebuild AAB, upload.
- **In ship prep:** PipeConnect (vc 17 / v1.8.1). Full metadata, 13 locales, 4-tier ladder, dedicated keystore. AdMob test-IDs (`ca-app-pub-3940256099942544`) clear at RELEASE_HANDOFF Step 1. 3 blockers (2026-05-25): `weekly_pass` INAPP not SUBS; no Restore Purchases; interstitials not gated by counter. **2026-06-16: all 122 hand-authored levels were unsolvable — regenerated solvable-by-construction (see fix log); `check_pipeconnect_solvable` gate added.**
- **Deleted:** BallSortPuzzle (2026-04-30, too similar to WS); removed from `app_themes.py`/`dedup_similar_apps.py`/`promo.json`.
- **Unique but thin (~150):** matches folder, 5-20 KB. Needs game-logic expansion + metadata.
- **2026-05-12/13 coin/pass overhaul:** 4-tier ladder; `weekly_pass $1.99/wk` +50/day; `season_pass_monthly $4.99/mo` +100/day via `migrate_coin_ladder_2026_05.py`. Already-listed apps need Play Console price/grant re-entry.
- **Screenshots — gameplay-only, recaptured 2026-06-18.** All 4 shipping apps (WS/Nono/P2048/UB) recaptured so every one of the 11 slots is a distinct gameplay board (no Themes/Stats/Level-Select/Ranks/Missions/Daily/overlay slots — see Screenshot rules). The old WS/Nono/P2048 "reuse captured levels across surfaces" grandfathering is **retired**: each surface now has fully distinct raws + headlines + wrappers. NEW apps follow the same gameplay-only rule from the start.
- **DO NOT PUBLISH (33 placeholder clones):** DiceRoller, EmotionFlash, FindDifference, FlashlightSOS, FruitMerge, GuitarChords, HiddenObject, JigsawPuzzle, MahjongSolitaire, MemoryCard, Metronome, MovieTrivia, MultiplicationGame, MusicTheory, NumberMemory, PasswordGen, PatternSequence, PianoKeyboard, PinPull, QRCodeGen, RandomName, RandomNumber, RandomRecipe, ScienceQuiz, ScrewPuzzle, SlidingTiles, SolarSystem, SportsQuiz, Sumplete, TripleMatch, UkuleleChords, WordScramble, WordSearch. Blocked until `game.html` rewritten. Run `cleanup_repo.py`.

## Workflows

**Finishing a thin/new app:** `SHIP_GAME.md` Phases 1-8 authoritative. Don't reimplement steps inline.

**Modifying shared wrapper:** change in one app → test → write migration script (`fix_all_apps.py` pattern) → preserve per-app values (package, AdMob IDs, IAP IDs, theme colors) → `--dry-run` w/ diff → bump `versionCode` of all affected.

**Mass-change scripts:** `BASE` constant at repo root; iterate only real app dirs (skip `_template`, `_release`, `__pycache__`, hidden); preserve per-app values (`applicationId`, AdMob IDs, IAP IDs, package statements, `WEBVIEW_BG_COLOR`, icons, store assets, metadata); print intent; `--dry-run` for non-trivial; match `fix_all_apps.py`/`prepare_for_publish.py` style.

## DO NOT FINISH UNTIL EVERY DETAIL IS CHECKED

Before saying any task done, self-check ALL. Non-negotiable.

1. **Buttons.** Every button touched (or in a screen touched) tap-tested. Onclick wires to real function; function runs; screen navigates / state updates. `showScreen('foo')` only works if `#foo` exists AND app's `showScreen` accepts that id format (some prepend `screen-`, others don't).
2. **Color & tokens.** No hardcoded white on light or black on dark. No `color:white`/`#fff`/`rgba(255,255,255,*)` for body content. Use per-app `--text`/`--menu-tile-fg`/`--on-accent`/`--surface` so every theme reads. `check_theme_tokens.py` + `check_contrast.py` = 0 blockers.
3. **Layout.** "Free space at bottom" / "move that upper" / "preview should be in top half" → DOM order doesn't match intended visual order. Verify on every screen touched.
4. **Overlaps & croppings.** No element overlapping ad banner. No button text cut by viewport/safe-area/ad. Top-bar children in-flow (no `position:absolute`). When in doubt, increase bottom-padding and `adb screencap`.
5. **Levels solvable.** Any generated puzzle (Nono, Unblock, PipeConnect, Sumplete) passes offline solver gate. 1% unsolvable boards ship unsolvable boards.
6. **Popup choreography.** Multiple "first launch of day" popups QUEUE, not stack. One, await tap-to-dismiss, then next.
7. **Re-screencap after fix.** Static checks miss runtime regressions (CSS specificity, container-not-found, state-not-loaded). `adb screencap` AFTER rebuild + reinstall + relaunch. Compare side-by-side. Can't run emulator = hard blocker.

If ANY cannot be verified, NOT done. Fix or surface as Hard Blocker — do NOT mark "completed" or write a summary hiding the gap. Honest gaps are NOT a substitute for fixing — don't write a "Known gaps" section and proceed.

## Things to flag to the user

(Don't re-raise the 10 Red Lines.)

- Flagship "ready" without meta-loop (theme collection, achievements, world restoration). `COMPETITIVE_BENCHMARK.md` §3. Cheapest = theme collection (~1 day).
- `full_description.txt` opening with description not hook ("Welcome to Water Sort, the most relaxing pour-sort puzzle on Google Play"). §1 leader-format.
- Puzzle/sort listing missing "relaxing"/"satisfying"/"ASMR"/"offline" when applicable. §2.
- Two apps in same genre cluster shipping within 7 days. Auto-generated listings via template substitution. `game.html` <~8 KB at publish. Reused screenshots across apps.
- Puppeteer/headless Chromium for screenshots — **emulator-only**. No AVD = hard blocker.
- `keystore.properties` with real passwords committed. Per-app `store/privacy-policy.html` (delete). Privacy/support URL not matching canonical. `iaps.json` not matching `MainActivity` IDs / missing/>200ch/drifted descriptions. `content_rating.json:gambling_mechanics` on a kids app.
- "Just ship the placeholder" — **refuse**. Crash >1% or ANR >0.5%.
- App without 4 archetypes from `APP_ARCHETYPES.md`. Archetype A+M0+V1+T1 = template (refuse without varying ≥2 of 4). Layout A >30% shipped or Texture T1 >40% after month 6. `metadata/app_identity.md` missing/empty at Phase 5.
- Missing any 13 locale folders (`id` not `id-ID`; `uk` not `uk-UA`). Title translated. `*.rejected` translation file. Kids app translations with "# KIDS APP — REVIEW BY NATIVE SPEAKER" header. Request to add Russian (`ru-RU`) — excluded portfolio-wide.
- `i18n/<lang>.json` keys diverging from `en.json` — runtime fallback mid-screen looks broken.
- Screenshot violations (see Screenshot rules).

## Screenshot rules (mandatory)

- **7 phone / 2 tablet_7 / 2 tablet_10 distinct.** Phone = primary listing surface; tablets get 2 most-impactful each. (2026-06-08 policy.) `check_screenshot_completeness`.
- **GAMEPLAY ONLY — every single slot is an actual gameplay board at a DISTINCT level. No other pages, period.** (2026-06-18 policy — replaces the old "non-gameplay screen at most once" allowance.) Forbidden in EVERY slot across all 11 (phone + both tablets): main menu, Shop, Settings, "More Games", **Themes/palette screen, Stats, Level Select, Ranks/weekly-standings sheet, Missions, Daily banner, and any Level-Complete / win / game-over overlay**. A board with a celebration overlay on top is NOT "a level" — capture the board mid-play instead. Each of the 11 slots must be a different level/board (no repeated level number; for non-leveled games like 2048, a distinct board state). `check_screenshots_gameplay_only` BLOCKS any tap config that navigates to a non-gameplay screen or triggers an overlay.
- **Showcase every theme — on gameplay boards, never a Themes-screen shot.** Cycle a different theme per board slot (and ≥1 board in each UI theme) so the palettes appear *while the game is being played*. Locked themes (Inferno @150, Galaxy @200) unlocked via `_setup_taps` save-state seeding; applied per slot with `setActiveTheme`/`applyUITheme` in `<App>/test/screenshot_taps.json`. The Themes/palette *page itself* is never a slot.
- **3 surfaces fully distinct.** Each phone/tablet_7/tablet_10 = fully distinct listing. Vary: (1) levels/boards (no repeated level across the 11 slots); (2) theme per board; (3) wrapper variant; (4) headlines (phone: `metadata/screenshot_headlines.json`; tablets: `_tablet_7.json`/`_tablet_10.json` — `wrap_tablet_screenshots.py` falls back to phone copy when missing, the failure mode). (Prior WS/Nono/P2048 grandfathering retired 2026-06-18 when all 4 shipping apps were recaptured gameplay-only.)
- **NO tutorial/coachmark overlay.** Capture seed MUST set `tutorialDone=true` (or per-app equivalent) BEFORE screencap. `seed_screenshot_state.js` seeds every coachmark-dismissal key.
- **NO AdMob test banner.** Pipeline: (a) `screenshot` flavor disabling `bannerContainer.setVisibility(VISIBLE)`; (b) inject CSS hiding `#bannerContainer`/`.cross-promo-strip`; (c) `SCREENSHOT_MODE` boolean MainActivity reads to no-op banner load.
- **Headlines match content.** "Daily Missions" over plain gameplay = Play policy red flag.

## House style

- **Python:** stdlib only unless asked; docstring header; `BASE` constant; match `fix_all_apps.py`.
- **Java:** 4-space indent; grouped imports with section comments; match existing `MainActivity.java`.
- **HTML/CSS/JS in `game.html`:** single file; inline `<style>` + `<script>`; CSS custom properties for theme at top (`:root { --bg: ...; }`); no external CDN deps.
- **JSON:** 2-space indent, trailing newline, UTF-8, no comments.
- **Text metadata:** plain UTF-8, trim trailing whitespace, single trailing newline, no BOM.

## Scope note

User's long-term goal: all ~200 apps to flagship quality. ~1 app/week sustainably = 4 years for 200. When asked to "finish all of them," help one at a time at flagship bar rather than racing to ship thin versions of many. 30 polished apps out-earn 200 thin ones at fraction of policy risk.

## Growth/DAU baseline

Portfolio standard across WS/Nono/P2048/UB. New apps carry full set before Phase 8. JS = six runtime-injected shims at `scripts/_growth_shim_[a..g].html`, keyed by `data-growth-shim` (idempotent). `check_growth_features.py` enforces.

**(A) Notifications.** NativeBridge: `scheduleDailyReminder`, `scheduleStreakAtRisk`, `scheduleLivesRefilled`, `scheduleWinBack(d3/d7/d14/d30)`, `cancelAllNotifications`, `setNotificationsEnabled`/`getNotificationsEnabled`, `recordLastPlayed`, `hasNotificationPermission`/`requestNotificationPermission`. Shim: daily at rolling-avg play hour (default 19); streak-at-risk 20:30 day BEFORE reset (streak ≥3); lives-refilled on `window.gScheduleLivesRefilled`; win-back d3/d7/d14/d30 from session end (day-7 = +100 coins via `pendingWinBackReward`); 2/day cap; settings toggle; permission pre-prompt AFTER first level clear.

**(B) Cross-promo.** `CROSS_PROMO_PACKAGES` / `<queries>` / `PROMO_GAMES` lists OTHER **live** portfolio apps. **Pre-release NEVER targets.** Install reward 200 coins; double-sided welcome bonus 100 coins on first launch from sister app. Break-point card every 5th clear, max once/session, never two sessions in row.

**(D) Streak freeze + milestone.** `state._streakFreezes` default 1; auto-consume on 1-day miss. Refill +1 free every 7 days, buyable 200 coins. Menu chip: day 1=25🪙 · 3=100🪙 · 7=🎨 · 14=500🪙 · 30=🌟 + 1000🪙 · 100=🏆 5000🪙.

**(E) First-session retention.** Levels 1-3 solvable <30s. Loud first-clear: emoji-confetti + "You've got this! 499 more puzzles to go." No interstitial first 3 clears. Non-obvious genres (Nono, Unblock): 3-step coachmark on first launch behind `tutorialDone`. End session 1 (≥3 clears + tutorialDone): schedule daily reminder + "Come back tomorrow".

**(F) Virality.** Bridge `shareText(String)`, `shareImage(b64, caption)` via `ACTION_SEND`. Share-a-win on 3-star/high-score overlays. Wordle-style shareable daily on `overlay-daily`: `<Game> Daily YYYY-MM-DD ✅ solved in N moves` + Play link.

**(G) Leaderboards.** PGS v2 — `submitScore`, `showLeaderboard`, `signInPlayGames` on every NativeBridge. Submit on clear/high-score. Synthetic weekly bracket = fallback. `games_app_id` + JS `LEADERBOARD_ID` ship as placeholders.

## Menu — unified rules across all 4 shipping apps

ONE function renders on `showScreen('menuScreen')`. Owner: `scripts/_growth_shim_menu.html` (`renderMenu`). Shim D + G keep only non-menu wiring. Copy verbatim as `<script data-growth-shim="MENU">…</script>` at bottom of every shipping `game.html`. Idempotent. Re-inject via `/tmp/reinject_all_shims.py`. Shim bodies byte-identical; per-app diff via tokens.

**Top bar** (in-flow flex, no `position:absolute`): `[❤ lives] [🪙 coins] [🪙 +25 free-coins]  ← spacer →  [🏆 ranks]`. Free-coins icon: 24px circular, green `+25` when ready, greyed + countdown on 4h cooldown (reuses `claimFreeCoins`/`xClaimFreeCoins`/`showRewardedAd`). 🏆 ranks → 2-tab sheet (This Week + Leaderboard); reuses `showTournament`/`xShowTournament`/`showWeeklyEventInfo`/`weeklyEventBanner` click. **Settings NEVER in top bar.** Icons FLAT (`background:transparent; border:none`). Synth header HIDES native `.menu-header`/`.menu-coins`/`.menu-lives`/`.coin-display`/`.lives-display`; padding `14px 14px 4px; margin-bottom:14px`. ALWAYS shows BOTH lives + coins default 0 (P2048 drops ❤). At 380/330px widths icons shrink + lives-text → heart+number.

**Three tiers + chip row:**
1. **ONE dominant primary.** `Continue · Level N` (or `Continue · <score>` for 2048) when `hasResumableProgress()`, else `Play`. Patched from `#menuPlayBtn`/`.btn-primary`/`.menu-primary`/`.menu-tile-primary`/`.btn-play`. `min-height: clamp(64px, 8.5vh, 96px)`, font `clamp(1.18rem, 3.1vw, 1.5rem)`, width `clamp(280px, 78vw, 460px)`. `hasResumableProgress()` true on any: `state.lastLevelProgress`; `boardState`/`gameBoard` not gameOver; `currentLevel > 1`; `completedLevels.length > 0`; `levelsCompleted > 0`; `bestScore > 0`. For 2048: non-empty grid OR score > 0, NOT bestScore.
2. **Daily Challenge** SINGLE. Label `Daily puzzle · MMM DD`. If button has child class `menu-streak`/`daily-streak`/`[class*="streak"]` or id `menu-streak`, shim SKIPS streak suffix. Width `clamp(220px, 60vw, 340px)`. `min-height: clamp(44px, 6vh, 60px)`.
3. **`.menu-icon-row`** canonical `Levels · Shop · Games · Settings` (P2048: Best for Levels). Mixed-case. Settings ALWAYS here. Min 60×58 icon+label stacked.
4. **Chip row** below row, full-width, padding `0 16px`: `🛡 Streak Shield ×N` + `🎁 Claim Day N · +X 🪙` (or `🔥 Tomorrow: …` after claim). Backgrounds → `--menu-tile-*` tokens.

**Composition.** Container `justify-content:center` (NOT `flex-start`/`space-around`). `--menu-gap` (~14px). `#menuScreen > *{flex:0 0 auto}`. Title `clamp(22px, 5vw, 34px)`. Tagline `clamp(0.78rem, 2vw, 0.95rem)` at 78% opacity. `.menu-buttons { display:flex; flex-direction:column; gap:10px; max-width:420px; margin:0 auto; }`. **`.screen:not(.active)` unconditionally `display:none !important`** in shim CSS.

**Forbidden on menu:** static `xFreeCoinsBtn`/`xThemeStrip`/`xPassPromo`/`weeklyEventBanner` inside menu container; full-width promo banner; two competing large buttons; `.settings-btn`/`.settings-gear` inside menu; `.menu-pair-row`/`.menu-tile-row` with 2+ buttons; static "Level X/N" indicator at top; `justify-content:space-around` overrides; `position:absolute` on `[data-menu-icons]` or top-bar children; polling injectors (`injectMenuChips`/`injectButton`/`injectFreeCoins`/`injectThemeStrip`/`injectPassPromo`/`updateTournamentBanner`) in `setInterval`; rogue `data-growth-leaderboard-btn`; >2 rank-opening elements; sub/pass sales card; theme strip; tournament banner; full-width Free Coins; medal/second leaderboard icon; hardcoded per-button tints.

**Relocated (not removed from game):** Theme strip → Themes screen (`ensureThemeStrip` moves `xThemeStrip`/`xThemeStrip2048` to top of `themesScreen`/`screen-themes`). Season Pass promo → Shop + no-lives overlay (`injectPassPromo()` when `shopScreen`/`screen-shop`/`overlay-nolives` active). Seasonal-event → slim ribbon (`xSeasonBanner` ≤30px). Weekly Tournament → top-bar 🏆 only. The 4 calls (`injectFreeCoins`, `injectThemeStrip`, `injectPassPromo`, `updateTournamentBanner`) must NOT appear in `boot()` or `showScreen('menuScreen')`.

**Settings.** Language picker `appendChild` NEVER `insertBefore(firstChild)` — must be normal list item INSIDE `.settings-list` (same for Notifications toggle). Buttons use `--menu-tile-*`/`--surface` tokens — never hardcoded dark slabs. Notification ON/OFF: min-width 64px + 8px×22px padding + center-aligned. Restore Purchases reachable.

**Leaderboard synthetic by default.** 🏆 "Leaderboard" tab: player highlighted, week-seeded names from per-app `NAME_POOLS.{watersort, nonogram, puzzle2048, unblock}` (~60 each, distinct flavor). Seed `isoWeek * 7919 + appOffset` so two games NEVER render same standings side-by-side. `genFakeName(rng)` mixes 6 archetypes (first-name+suffix, lowercase word-pair, gamertag, tiny handle, name+emoji, non-Latin). `debugSanityGuard(rows)` warns on genre-keyword names. Score log-normal centered on player metric (~55% within ~20%); rank from population. Refreshes Monday. `Android.showLeaderboard(LEADERBOARD_ID)` only as "Compare on Play Games →" footer link. Copy: "Weekly Standings"/"This Week" — never "global"/"live"/"real-time". Renders rank-#1 → last (cap 1500) with Jump-to-me.

**Leaderboard floor.** `buildStandings()` MUST use `var total = Math.max(1000, (window.LEADERBOARD_TOTAL_OVERRIDE | 0));`. Native bridge `setLeaderboardSize(int)` (`@JavascriptInterface`). 1000 floor stands.

**Menu must pass (skin v2 gate — every NEW app, before merge).** The shared
skin is `scripts/_menu_skin.css` (single source — synced into every app by
`reinject_all_shims.py`; edit the master, never an embedded copy; grep
`SHARED MENU SKIN v2` to confirm rollout). A new app's menu ships only when
ALL true: (1) icon tiles **filled & brand-tinted with depth**, bold accent
glyphs — never thin outline-on-white ("settings app" tell); (2) background
motif **felt (~12-16% internal alpha)** and **masked out of the center**
(the skin's ::after mask); no dead mid-section between emblem and CTA;
(3) emblem **reads the core mechanic** in one glance; (4) hero CTA dominates
(gradient + depth + glyph + shine); (5) wordmark gradient clean — ≤3 stops,
no murky complementary midpoint, ≥4.5:1 vs bg; (6) reads as **family**
(shared skin/layout) yet **distinct** (own world/accent) vs every sibling;
(7) light + midnight (+ extra themes) correct, `prefers-reduced-motion`
respected, gameplay untouched, no competing shim. Per-app `--m-*` identity
tokens go AFTER the skin block; apps must define `--accent` (the v2 tile
tint reads it).

**Sizing.** Bottom-bar buttons at phone-resolution feel tiny on tablet. Add `@media (min-width: 600px)` + `@media (min-width: 900px)` for 10".

**Canvas symmetry.** Game-canvas drawings (P2048 grid) center internal layout AND ensure frame has equal padding all four sides. P2048 fix: draw frame at `(ox, oy)` not `(ox - gridPad, oy - gridPad)`.

## Theme tokens, never hardcoded

Every growth shim reads CSS tokens so same shim works on each app's Daylight + Midnight.

| Token | Used by | Daylight | Midnight |
|---|---|---|---|
| `--text` | shim body | dark on light | light on dark |
| `--text-mute` | secondary | 60-70% body | 55-62% body |
| `--surface` | shim panel/card | per-app warm/cool | per-app dark |
| `--border` | hairlines | 8-20% on bg | 10-15% on bg |
| `--g-play` | primary CTA gradient | per-app primary | per-app primary |
| `--on-accent` | text on `--g-play` | 4.5:1 AA | 4.5:1 AA |
| `--btn-neutral-bg` | OFF / disabled | per-app muted | per-app muted |

WS + P2048 ship full color block + `html[data-theme="midnight"]` override. Nono aliases `--text-mute` → `--text-muted`, `--g-play` → accent. UB shipped full set during May rebrand.

**HARDCODE whitelist:** Gold `#d29922`, `#c97f00`, `#ffd700`, `#fed130`. Heart red `#b8332b`, `#c83838`. Streak fire `#ff8c1a`. Badge green `#2ea043`. Decorative confetti/particle fills. `rgba(0,0,0,*)` modal dim. `rgba(255,255,255,*)` elevation.

Each overlay bg = `var(--surface, var(--app-bg, var(--bg, #161b22)))`, text = `var(--text, #e6edf3)`. **No hardcoded dark slabs.**

**z-index literals forbidden** in `game.html`. Scale: `--z-overlay-dim: 100`, `--z-banner: 200`, `--z-toast: 300`, `--z-confirm: 400`, `--z-tutorial: 500`, `--z-modal: 700`, `--z-critical: 800`.

`check_theme_tokens.py` greps shim blocks for hex/rgb after stripping `var()` fallbacks; fails outside whitelist.

**Contrast WCAG AA 4.5:1** (3:1 for ≥18pt or ≥14pt bold). UB's `--text-soft/--text-mute/--text-faint` on `#ece6f3` failed (3.74/2.65/1.76); raised to `#574766/#604f7b/#6c5b8c` (PASS). `check_contrast.py` parses `:root` text tokens (`--text*`, `--color-text*`, `--fg*`, `--label*`) against bg (`--app-bg`/`--bg`/`--background`/`--surface`); blocks <4.5:1.

## Distinct light palette per app

"Light" ≠ "beige". Each app picks own family + accent. Track in `app_themes.py`. Two apps with same base bg = Repetitive Content risk.

| App | Base bg | Family | Accent |
|---|---|---|---|
| WaterSortPuzzle | `#3d6a9e` | water-blue | sky-cyan + colored liquids |
| Nonogram | `#f5f0e6` | cream/paper | warm coral red `#c83838` |
| Puzzle2048 | `#f3ecd9` | warm cream / sand | gold `#edc22e` + `#f2a500` |
| UnblockPuzzle | `#e3efe5` | mint / sage | forest green `#4a8a5e` + red exit `#ec5f6e` |
| PipeConnect | `#eef4f8` | sky-blueprint | sky-blue + red |

WS = medium ocean blue (brand = "water"). Midnight ships as coin-purchased darker unlock (`#0a1628 / #0d2137`). All other apps: Daylight default + Midnight as paid shop unlock. UB swapped off lavender 2026-05-27 (clashed with Nono's pink/coral); P2048 swapped from dark-default-with-gold to warm cream.

**No dark default themes.** Light bg, soft accents, dark text on install. Dark UIs = coin-purchased "Midnight" (soft currency, not paid IAP).

**Light-mode CSS covers EVERY screen.** Audit any `color:white`/`rgba(255,255,255,…)`/`#fff` (invisible against light). Walk menu, gameplay, level select, shop, settings, stats, themes, missions, daily, level-complete before screenshotting. Midnight covers symmetric set including `.game-header` and `.game-footer`.

## Game footer + ad banner clearance (mandatory)

Every `.game-footer` MUST have adaptive override inside round-N "adaptive sizing via clamp()" CSS block — not just base rule. MUST include `padding-bottom: calc(clamp(...) + env(safe-area-inset-bottom, 0px) + 6px) !important;` (+6px buffers adaptive AdMob banners with rounded tops / soft shadows beyond 50dp). CSS comment "footer reserves room for the banner" is NOT a substitute — check BOTH comment + selector. Vertical padding symmetric (asymmetric top/bottom reads as "stuck"). For `#gameScreen` with `justify-content: space-between` (P2048), `margin-bottom` is absorbed by flex — use `transform: translateY(-Npx) !important` instead. `check_footer_clearance.py` enforces.

## Bug-class invariants — fix-everywhere + permanent gate

Bug in any of 4 shipping apps: (1) reproduce + understand; (2) fix in **all 4** in SAME commit; (3) memorialize as permanent `scripts/check_*.py` gate. New bug → write `check_<name>.py` detecting the class (not just literal regression); wire into `pre_publish_check.py`; add below.

**Active bug-class gates** (each in `pre_publish_check.py`):

`check_theme_tokens`, `check_menu_composition` (top-bar gear / paired Tier-2 / wrong icon labels), `check_menu_hierarchy` (static promos / missing tiers), `check_menu_shims` (polling injectors / abs top-bar / >2 ranks), `check_menu_consistency`, `check_synth_header_scope`, `check_save_key_probe`, `check_continue_label` (`Continue · 0` — 2048 needs grid OR score>0), `check_daily_label` (≠ `Daily puzzle · MMM DD`), `check_solid_surface_token`, `check_chip_token_tint`, `check_pastel_contrast` (`--surface` within 5% luminance of `--bg`), `check_footer_clearance`, `check_leaderboard_floor` (literal <1000 / missing override), `check_games_app_id` (non-digit/whitespace/placeholder PGS APP_ID), `check_ad_network_switch` (USE_APPLOVIN true with empty MAX ids → launch crash), `check_pgs_init` (games dep without PlayGamesSdk.initialize → silent PGS no-op), `check_cross_promo_pkgs` (typo'd com.pegasusgames.* id → dead store links/install detect), `check_notif_prompt_timing` (POST_NOTIFICATIONS outside the JS-gated bridge → launch-time dialog), `check_iap_invariants`, `check_iap_grant_parity`, `check_retention_features`, `check_subscription_parity`, `check_subscription_routing` (INAPP not SUBS), `check_subscription_disclosure`, `check_coin_tier_ladder`, `check_booster_catalog`, `check_menu_completeness`, `check_seasonal_events`, `check_keystore_present`, `check_screenshot_taps_valid` (test/screenshot_taps.json copied from another app — `_comment` names a different app, or `loadLevel(N)` ≥ the game's level count → empty/broken capture slots), `check_unblock_solvable` (exit-row block / wrong optimal), `check_pipeconnect_solvable` (flow level whose colour pairs can't all be joined by vertex-disjoint paths), `check_nonogram_unique`, `check_reward_type_parity`, `check_free_coins_single_source` (free_coins granted in BOTH an onAdReward branch AND a rewarded-callback body → double-grant / orphaned cooldown), `check_price_string_parity`, `check_iaps_descriptions`, `check_screenshot_completeness`, `check_screenshots_gameplay_only` (any screenshot_taps.json slot that navigates to a non-gameplay screen — Themes/Stats/Level-Select/Shop/Settings/Missions/Ranks — or triggers a win/level-complete/game-over overlay or injects a daily/streak banner), `check_no_test_ad_in_screenshots`, `check_screenshot_template_reuse`, `check_cross_app_asset_similarity`, `check_screenshot_headline_match`, `check_iap_display_name_table`, `check_restore_purchases_ui`, `check_interstitial_cadence`, `check_growth_features`, `check_description_claims` ("20+ languages" / "global leaderboard" / "unique solution"), `check_release_notes_match`, `check_store_paste_locale_tags` (`<uk-UA>`/`<id-ID>` drift), `check_prohibited_lang`, `check_blocked_apps`, `check_contrast`, `check_min_levels` (game with a `CAMPAIGN`/`LEVELS` array under the 500 release floor — BLOCKS unreleased, WARN-grandfathers live apps), `check_java_arglist_comma` (illegal trailing comma before `)` in any MainActivity.java → won't compile), `check_dead_handlers` (onclick= calls an undefined fn, or an `if(x) function(){}` strict-mode syntax botch that aborts the script), `check_sokoban_solvable` (Sokoban ASCII level with no player `@`, mismatched box/target counts, or A*-unsolvable), `check_screenshots_gameplay_only`.

## Memorialized fix log

Impl detail behind gates above.

- **Win checks vs CLUES/rules.** Alternate valid solutions must win. Nono `checkPuzzle`/`checkAutoWin` compare row+column run-length encoding against clues; stored solutions are witnesses for "X errors" only.
- **Procedural pregen.** Nono: 80 `PREGEN_10` + 150 `PREGEN_15` + 200 `PREGEN_20`; remainder runtime `_countSolutionsUpTo(...) === 1` (300-attempt budget + curated fallback). `verify_nonogram_pregen.js --fix` regenerates.
- **Unblock generator:** non-red horizontal block on red car's exit row walls exit. Stored `optimal` from solver only.
- **PipeConnect levels solvable-by-construction.** Win = each colour's two dots joined by a path (cells hold one colour ⇒ vertex-disjoint); full grid coverage is bonus-stars only. Original hand-authored levels 1-122 were almost all UNSOLVABLE (no disjoint connection exists); 2026-06-16 they were replaced wholesale via `PipeConnect/test/gen_levels.py` (Hamiltonian-path partition — the path is a witnessed full-board solution). `check_pipeconnect_solvable.py` gates it (connect-only solver decisive ≤7x7, large boards rely on the construction witness + WARN). Never ship a flow LEVELS array that hasn't passed the gate.
- **Rewarded-ad callbacks queue-based.** WS `_pendingAdCallbacks[]`; Nono+P2048 `_pendingRewardCbs[]`. New triggers no-op while non-empty. `onAdReward` drains in try/catch. `onAdNotReady`/`onAdDismissed` clear.
- **free_coins single source.** The Free Coins surface grants via a queued rewarded callback that `onAdReward` drains. A base `free_coins` branch in `onAdReward` that ALSO mutates coins double-pays (Nono shipped +25 then drained = +50, 2026-06-17) or, if it `return`s before the drain, orphans the callback so the 4h cooldown never stamps (P2048, repeatable). Fix: `onAdReward` only drains the queue for free_coins (WS model) — the callback is the lone grant. UB is a valid variant: it grants in the `onAdReward` override (returns before delegating) with a cooldown-only callback. `check_free_coins_single_source` BLOCKS only when BOTH an `onAdReward` branch and a rewarded-callback body grant coins.
- **Sub disclosure shim.** `_growth_shim_subs.html` (`data-growth-shim="SUBS"`) renders renewal disclosure under every Pass button. Settings has Manage Subscriptions row → `play.google.com/store/account/subscriptions` via `Android.openUrl`. 13 locales.
- **Sub routing.** Every sub through `SUBSCRIPTION_PRODUCTS` set, never hardcoded `.equals`.
- **Daily-streak min 1.** `getStats()` MUST be `Math.max(loginN, dailyChallengeStreak, 1)` LIVE in stats render path (not only `wsTrackLevelComplete`).
- **Shop ordering.** Section-based: `Spend Your Coins → Coins (packs) → Subscriptions → IAPs`. Array (WS): `type:'coin'` first. Static-HTML (Nono, P2048): coin-priced cards at top of `.shop-scroll`/`.shop-grid`.
- **`.footer-btn` discipline.** ONE base + theme overrides. No `.game-footer .game-btn` scoped rules. `.footer-btn { flex: 1 1 0; min-width: 0; }`. Long labels truncate or shorten.
- **AdMob banner stable.** `MATCH_PARENT, MATCH_PARENT` (not `WRAP_CONTENT`). After `bringToFront()`: `webView.setVerticalScrollBarEnabled(false)`, `setHorizontalScrollBarEnabled(false)`, `setOverScrollMode(OVER_SCROLL_NEVER)`.
- **Ad doesn't scroll on drag.** WebView `ALIGN_PARENT_TOP` + `ABOVE bannerContainer.getId()`, then `bannerContainer.bringToFront()`.
- **Tutorial/streak overlay serialized.** Tutorial wraps all steps in ONE queue entry (`runStepsSerially`). Use `window.gPopupQueue.enqueueWithSelector` from `_growth_shim_a.html`.
- **Bottom button bars.** P2048 `.game-btn`, Nono `.footer-btn` min-height 52-58px + `clamp(11-14px)` font, `--menu-tile-*` tokens.
- **More-Games "Claimed" badge** `#2ea043` bg + white text.
- **Cross-promo list maintenance.** On pre-release → live, remove from `check_growth_features.py::PRE_RELEASE`.
- **Screenshot capture is self-cleaning + per-app.** `capture_screenshots.py` runs a clean-JS step before every screencap: sets `tutorialDone`/`coachmarkDone`, calls `Android.hideBannerAd()` (no Test-Ad banner), and hides first-launch popups `#ls-overlay` (login streak) + `#starterPackModal` — intentional overlays (`overlay-complete/daily/hint/nolives`) untouched. Per-emulator prep: `settings put secure immersive_mode_confirmations confirmed`; **`pegasus_tablet_10` boots landscape (2560×1600) — rotate to portrait** via `settings put system user_rotation 1` (+`accelerometer_rotation 0`) → 1600×2560, and re-verify each raw is `h>w` (orientation can flip on an app's first launch). `wrap_screenshots.py --iphone` re-wraps 3 phone raws at 1320×2868 into `iphone_6_9/`. A per-app `test/screenshot_taps.json` must target ITS OWN game (valid `loadLevel` indices + real theme palette/CSS-var keys + `body.midnight` chrome); copying another app's config is gated by `check_screenshot_taps_valid` (memorialized 2026-06-16 — Afterimage/Hunch/Overlay shipped verbatim PipeConnect copies). For games whose fresh level is an empty board (Hunch), seed a representative mid-solve state so slots are distinct.
- **Screenshots are gameplay-only (2026-06-18).** Every store-screenshot slot — all 7 phone + 2 tablet_7 + 2 tablet_10 — must be an actual gameplay board at a *distinct* level; no Themes/Stats/Level-Select/Ranks/Missions/Daily pages and no win/level-complete/game-over overlays anywhere in the set (a celebration overlay on a board is not "a level" — shoot the board mid-play). This retired the earlier "each non-gameplay screen type at most once" allowance. The 4 shipping apps' `test/screenshot_taps.json` were rewritten so each slot calls only the per-app start-gameplay path (`_jumpTo`/`startLevel`/`initGame`/grid-set + `drawGrid`) at a unique level, and the matching `screenshot_headlines.json` lines were reworded off any theme/daily/weekly/missions/stats/3-star copy. `check_screenshots_gameplay_only.py` gates the class: it BLOCKS a tap config whose ops `showScreen(...)`/`Game.showScreen(...)` a non-gameplay screen, `classList.add('active')` a `*overlay*`/`win-overlay`, call the ranks sheet, or inject a daily/streak banner.
- **Verify in emulator.** After ANY UI change, `adb screencap` + send PNG BEFORE saying "fixed".
- **Java arg-list trailing comma = broken build (2026-06-18).** Editing a `CROSS_PROMO_PACKAGES`/`VALID_PRODUCTS` `Arrays.asList(...)` to remove entries can leave a dangling comma before `)`. Java (unlike JS/JSON) rejects it ("illegal start of expression") so `compileDebugJavaWithJavac` FAILS — and because nobody rebuilt, the 2026 cross-promo edit silently broke the build of all 8 AdMob apps (live ones included). Always rebuild after touching `MainActivity.java`; `check_java_arglist_comma.py` greps every `*.java` for `,\s*)` and BLOCKS.
- **Synthetic-leaderboard relabel must read the GLOBAL id (2026-06-18).** The "is this a placeholder id?" check in the MENU shim's `renderLeaderboardTab` referenced a bare `LEADERBOARD_ID` that is `var`-scoped to a *different* growth-shim IIFE — always `undefined` in the MENU shim, so `_lbPlaceholder` was always false and the bot bracket rendered as a real "Weekly" leaderboard with a "Compare on Play Games" link. Fix: read the exported `window._GROWTH_LEADERBOARD_ID`; missing/`TODO`/`PLACEHOLDER`/`ENTER_` ⇒ "Practice bracket" + not-a-global-ranking note. (Afterimage/Hunch/Overlay.)
- **Level count floor — 500 on release (2026-06-18).** Every game with discrete levels ships ≥500 *verified* levels (mined from its own seed generator + acceptance test, so each still passes solvability/uniqueness/par gates). Overlay regenerated to 500 (167 easy/167 med/166 hard) via the bit-exact port + the PART-5 optimal-cost reject — verified in-emulator (level 400 loads a valid board). `check_min_levels.py` BLOCKS unreleased level-games <500, WARN-grandfathers live apps; Afterimage/Hunch/PipeConnect/Sokoban + live WaterSort/Unblock are the tracked follow-up (each via its own generator; live apps need a save migration).
- **Sokoban levels need a player + must be solvable (2026-06-18).** The 50 hand-authored Sokoban maps had NO player char (`@`/`+`) — `parseLevel` defaults the player to (0,0), a wall, so every level was unplayable. Regenerated to 500 via `Sokoban/test/gen_levels.py` (REVERSE/pull generation — start solved, scramble with box pulls, so the reversed pulls are a guaranteed push solution; a bounded forward A* double-checks + bands difficulty). `check_sokoban_solvable.py` gates the class (no-player / box≠target / A*-unsolvable BLOCK; too-large WARN by construction). Sokoban also needed `minSdk 23→24` (AppLovin 13.6.3 requires 24) to compile — a separate pre-existing block.
- **All level games meet the 500 floor (2026-06-18).** Overlay/Afterimage/Hunch (own-generator harvest), PipeConnect (Hamiltonian gen extended, 1-122 preserved), Sokoban (new pull-generator) regenerated to 500; WaterSort (`LEVEL_SEEDS`) and UnblockPuzzle (IIFE `LEVELS`) were already at 500 (the gate just didn't recognise those array forms — now it counts `LEVEL_SEEDS` + the `{blocks:[...],optimal:N}` Rush-Hour signature). No live save migration was needed (the two live apps were already at 500).
- **Dead menu handlers + `if(x) function` syntax botch (2026-06-18).** A portfolio save-migration injected `if (saved) function migrateSave(){...}` — a function declaration as an `if` body, which is a strict-mode SyntaxError that aborts the ENTIRE script (Nonogram's menu was fully dead: `state`/handlers never defined). Fixed in Nonogram/Unblock/Afterimage/Hunch/Overlay/PipeConnect (sloppy-mode Annex B masked it in the non-strict ones). Also defined the dead `showSettings`/`buyLivesShop`/`watchAdForLife` onclick targets (Afterimage/Hunch/Overlay/PipeConnect) -> `showScreen('settings')` / `showScreen('shop')` / `requestRewardedAd('extra_life')`. `check_dead_handlers.py` gates both classes.
- **Keystore gitignore.** `*.jks`, `*.keystore`, `keystore.properties`, `*.pem`, `*.der`, `local.properties`, `google-services.json`, `release_aabs/` at repo + per-app roots. Externally-shared zips MUST exclude `**/keystore.*` and `**/*.pem`.
