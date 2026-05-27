# Pegasus Games — Claude Code Instructions

Portfolio of ~200 Android apps/games sharing a common WebView wrapper.
Each top-level folder (except `_template/`, `_release/`, `docs/`,
`scripts/`) is one app with `game.html` inside `MainActivity.java`.
Read end-to-end before doing anything in here.

**Repo layout:**
- `CLAUDE.md` (this), `README.md` (public) — root
- `docs/` — `SHIP_GAME.md`, `QUALITY_PLAYBOOK.md`, `APP_ARCHETYPES.md`,
  `TRANSLATIONS.md`, `COMPETITIVE_BENCHMARK.md`, `NOTIFICATIONS_IMPL.md`,
  `IAP_CATALOG.md`
- `scripts/` — Python tools. Bare-name file refs in this doc resolve to
  `docs/` or `scripts/` accordingly. Run from repo root:
  `python3 scripts/pre_publish_check.py <AppName>`
- `<AppName>/` — one folder per app

**Key scripts:** `pre_publish_check.py` (master guard; runs every check
below), `build_release.py`, `gen_handoff.py`, `gen_translations.py`,
`gen_store_paste.py`, `consult_designer.py`, `init_app_metadata.py`,
`capture_screenshots.py`, `wrap_screenshots.py`,
`wrap_tablet_screenshots.py`, `app_themes.py`, `dedup_similar_apps.py`,
`cleanup_repo.py`, `fix_all_apps.py`, `prepare_for_publish.py`,
`migrate_to_per_app_keystores.py`.

**Standalone check modules** (run with `<App>` or `--all`, wired into
`pre_publish_check.py`): `check_iap_invariants.py`,
`check_iap_grant_parity.py`, `check_retention_features.py`,
`check_subscription_parity.py`, `check_subscription_routing.py`,
`check_coin_tier_ladder.py`, `check_booster_catalog.py`,
`check_menu_completeness.py`, `check_seasonal_events.py`.

## Companion files

- **`SHIP_GAME.md`** — MASTER RELEASE WORKFLOW. On "ship X" / "release
  X", read end-to-end and execute all 8 phases without asking unless a
  Hard Blocker hits.
- **`QUALITY_PLAYBOOK.md`** — design/UX/gameplay/monetization bar. Read
  when touching visuals, gameplay, menu, onboarding, or money.
- **`APP_ARCHETYPES.md`** — Layout (9) × Mascot (5) × Voice (8) ×
  Texture (8). Each new app picks one of each; recorded in
  `app_themes.py`. Read in Phase 1.
- **`TRANSLATIONS.md`** — 13 locales: `en-US`, `ar`, `de-DE`, `es-419`,
  `fr-FR`, `hi-IN`, `id`, `it-IT`, `ja-JP`, `pt-BR`, `tr-TR`, `uk`,
  `zh-CN`. Russian excluded. Indonesian is `id` (not `id-ID`);
  Ukrainian is `uk` (not `uk-UA`) per Play Console. Title stays
  English globally. Read in Phase 4.5.
- **`COMPETITIVE_BENCHMARK.md`** — top-grossing analogs (Royal Match,
  Block Blast, Water Sort) and the patterns flagship apps must match:
  listing structure, ASMR keywords, meta-loops, booster economy,
  screenshot order, icon production. Read in Phase 1 of every flagship.
- **`NOTIFICATIONS_IMPL.md`** — Java + JS reference for local
  notifications.
- **`IAP_CATALOG.md`** — canonical IAP descriptions (≤200 chars each).
  Source of truth for every `iaps.json` `description`.

**Script roles:** `gen_translations.py` uses `ANTHROPIC_API_KEY` (falls
back to `OPENAI_API_KEY`); has shrink-to-fit retry; writes
`.rejected` files only when even shrink overflows — hand-trim + rename
those before ship. `gen_store_paste.py` assembles
`<App>/STORE_PASTE.md` using Play Console's actual locale tags
(`<uk>`, `<id>` — never `<uk-UA>` / `<id-ID>`).
`pre_publish_check.py check_store_paste_locale_tags` blocks BCP-47
drift. `cleanup_repo.py` moves BLOCKED clones + deleted apps OUT of
the working tree (run with `--dry-run` first).

---

## Canonical contact info and URLs

Shared across **all apps**. Never invent per-app URLs/emails.

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

- **Per-app `store/privacy-policy.html` MUST NOT exist** — shared URL
  is source of truth. Delete any per-app copies on sight (legal
  liability if Play Console listing disagrees).
- **Per-app Data Safety forms ARE per-app** — shared policy is a
  superset; each app's Play Console form must reflect what THAT app
  does.
- Privacy URL must include `.html` (no trailing slash).

---

## Keystore management — per-app, single key, no PEPK

Every app has its OWN `<App>/android/keystore.jks` (gradle signs the
AAB). Password lives in `<App>/android/keystore.properties`
(gitignored). One keystore per app, no second "upload" keystore, no
PEPK. (May 2026: Nonogram was mistakenly signed with WaterSortPuzzle's
keystore, permanently locking Nonogram's upload key — that's why
shared keystores are forbidden.)

**How Play App Signing works here:** uploading an AAB signed with
`keystore.jks` to a brand-new listing auto-enrols the app — `keystore.jks`
becomes the **upload key** Play validates against; Play generates and
holds the actual **app signing key** server-side. We never opt into
PEPK, so the "app signing key ≠ upload key" error never applies.

**Current state (May 2026):** WaterSortPuzzle, Nonogram, Puzzle2048,
PipeConnect, UnblockPuzzle each have a dedicated `keystore.jks`. ~154
long-tail apps still share `pegasusgames-release.jks`
(fingerprint `E0:BD:7F:24:...`); migrate via
`scripts/migrate_to_per_app_keystores.py` BEFORE any of them ships.
Only keep using the shared keystore for apps already uploaded with it
(Play registers the upload key on first upload — reset takes
1-3 business days).

**Rules:**

1. **NEW app → new keystore.** SHIP_GAME Phase 1 setup:
   ```
   cd <App>/android
   keytool -genkey -v -keystore keystore.jks -keyalg RSA -keysize 2048 \
           -validity 10000 -alias <appname>
   ```
   Use a 16+ char alphanumeric password. `migrate_to_per_app_keystores.py
   --app NewApp` does this in one step.
2. **Back up 3 ways within 24 h** (and ALWAYS before first Play upload):
   local `<App>/android/keystore.jks` (gitignored), encrypted upload to
   Google Drive in `pegasusgames@atomicmail.io`, copy to dedicated USB
   stick labeled "Pegasus Keystores" kept physically separate.
3. `keystore.properties` is **gitignored** with a versioned
   `keystore.properties.template` next to it. Real file:
   `storeFile=keystore.jks`, `storePassword`, `keyAlias`, `keyPassword`.
   `storeFile` ALWAYS = `keystore.jks`. Lost password = lost keystore =
   upload-key reset. Record passwords + SHA1 in a password manager.
4. Record SHA1 in `<App>/metadata/app_info.json:upload_key_sha1` after
   first successful Play upload. Verify each future build:
   ```
   keytool -printcert -jarfile app/build/outputs/bundle/release/app-release.aab | grep SHA1
   ```
   `check_keystore_present` enforces.
5. **NEVER copy a `keystore.properties` between apps.** If missing,
   generate a NEW keystore — never reuse another app's. (This was the
   Nonogram failure mode.)
6. **If a keystore is lost:** generate new + back up 3 ways FIRST,
   then Play Console → Setup → App integrity → App signing → Request
   upload key reset. Update `upload_key_sha1` after approval.

**`check_keystore_present` BLOCKS if:** `keystore.jks` missing;
`keystore.properties` missing or `storeFile ≠ keystore.jks`; actual
SHA1 ≠ `app_info.json:upload_key_sha1`. WARNS if `upload_key_sha1`
unset.

**Phase 7 upload flow:** `./gradlew :app:bundleRelease` →
`<App>/android/app/build/outputs/bundle/release/app-release.aab`,
signed with `keystore.jks`. Upload to Play Console — on a new listing
Play auto-enrols; for later releases sign with the same `keystore.jks`.

**PEPK quirk (Puzzle2048 only):** set up via Play's PEPK
export-and-upload, which permanently registered the original
`keystore.jks` (2026-04-21, alias `puzzle2048`) as the *app signing
key*. PEPK is irreversible, so Puzzle2048 needs a *different* upload
key forever. Resolution: a new upload keystore (2026-05-11, alias
`upload`) is now `keystore.jks`; the PEPK'd original is archived at
`keystore.jks.pepk-archive` (gitignored). On disk Puzzle2048 looks
identical to every other app — only `keyAlias=upload` (vs per-app
`<appname>` elsewhere). **Don't run PEPK on any other app.**

---

## Per-app folder structure

```
<AppName>/
├── android/                            # Android project
├── ios/                                # iOS scaffolding
├── store/
│   ├── icon_512_playstore.png          # 512×512 PNG, no alpha
│   ├── feature_graphic_1024x500.png    # 1024×500, no transparency
│   ├── icon_1024_appstore.png          # 1024×1024, no alpha
│   └── screenshots/
│       ├── phone/      raw/ + 01.png..06.png   # 1080×2400 · 6 distinct
│       ├── tablet_7/   raw/ + 01.png..06.png   # 1200×1920 · 6 distinct
│       ├── tablet_10/  raw/ + 01.png..06.png   # 1800×2560 · 6 distinct
│       └── iphone_6_9/                          # 1320×2868 (Apple req.)
├── test/
│   ├── seed_screenshot_state.js        # localStorage seed
│   └── screenshot_taps.json            # per-app tap overrides
└── metadata/
    ├── app_identity.md                 # 4-archetype + feel
    ├── screenshot_headlines.json       # 7 phone headlines
    ├── screenshot_headlines_tablet_7.json, _tablet_10.json
    ├── en-US/  title.txt (≤30) short_description.txt (≤80, Google)
    │           subtitle.txt (≤30, Apple) full_description.txt (≤4000)
    │           keywords.txt (≤100, Apple) promotional_text.txt (≤170)
    │           release_notes.txt (≤500)
    ├── ar/ de-DE/ es-419/ fr-FR/ hi-IN/ id/ it-IT/ ja-JP/
    │   pt-BR/ tr-TR/ uk/ zh-CN/        # 12 more locales
    ├── app_info.json                   # category, ads, audience, URLs, package_name
    ├── privacy.json                    # Data Safety + Apple Privacy
    ├── content_rating.json             # IARC + Apple age rating
    ├── iaps.json                       # IAP catalog (== MainActivity)
    └── review_notes.json               # store reviewer notes
```

JSON schemas in `SHIP_GAME.md` Phase 4. Don't invent fields; copy from
WaterSortPuzzle.

---

## Store requirements (2026)

Full limits in `SHIP_GAME.md` Phase 4. Highlights:

- **Google:** 512×512 icon (no alpha), 1024×500 feature graphic, 2-8
  phone screenshots (1080×2400 recommended), Data Safety, IARC rating,
  privacy URL — all mandatory. Org accounts are EXEMPT from the
  12-testers / 14-day closed-testing rule; promote directly to prod.
- **Apple:** iOS 26+ SDK (since 2026-04-28), 1024×1024 icon, 6.9"
  screenshots required (1320×2868), Privacy Nutrition Label, granular
  age rating since iOS 26 — all mandatory.
- **Both:** NO "#1", "Best", "Top", "Award winning", "Download now",
  "Install now", "% off" in copy or screenshots.

---

## IAP correctness invariants

Violating any invariant = released users tap Buy, get nothing, Google
still charges. `pre_publish_check.py check_iap_invariants` enforces;
`scripts/check_iap_invariants.py --all` standalone.

1. **VALID_PRODUCTS == `iaps.json` SKUs.** `MainActivity.java`'s
   `launchBillingFlow` rejects unlisted SKUs before Play opens.
   Generate `VALID_PRODUCTS` from `iaps.json`; never hand-curate.
2. **Every PURCHASED purchase acknowledged within 3 days.** Consumables
   via `consumeAsync`; non-consumables + subs via `acknowledgePurchase`.
   `CONSUMABLE_PRODUCTS` declares the path; both paths wired in
   `handlePurchase`. Unacknowledged = auto-refunded.
3. **`game.html` defines `window.onPurchaseSuccess`** (directly or as
   alias to `onPurchaseComplete`). Java's bridge calls
   `window.onPurchaseSuccess(id)`; undefined = silent drop on every
   purchase. The grant function must NEVER throw — a thrown exception
   looks identical to a failed purchase. (Historical bug: ~140 apps
   defined only `onPurchaseComplete`; the retention hook chained to
   undefined `_origPurchase = window.onPurchaseSuccess`, dropping every
   non-`season_pass` SKU on the floor.)
4. **Unhandled SKUs fall through to `window.iapDeferGrant(id)`** which
   writes `localStorage.pendingGrants`. `window.replayPendingGrants()`
   runs on each game load to drain the queue. Lets a SKU bought before
   its mechanic existed replay once added.

**Catalog rule:** SKUs hidden from shop UI per archetype
(`archetype.json`); catalog (`iaps.json`) NEVER filtered — restore
must work for existing buyers across all SKUs.

**Future apps:** SHIP_GAME Phase 2 generates `VALID_PRODUCTS` from
`iaps.json` and injects canonical `onPurchaseSuccess` alias +
`replayPendingGrants` safety net. Phase 5 re-asserts all four.

---

## Retention-feature parity

Every game selling `season_pass_monthly` MUST have, in `game.html`:

- `window.replayPendingGrants` on init (IAP invariant 4)
- wrapped `window.onPurchaseSuccess` → original
  `onPurchaseComplete`/switch (grants every known SKU fully), unknown
  SKUs → `pendingGrants`
- `isSeasonActive()` / `hasActiveSeasonPass()` + `isPremium()` /
  `isWeeklyActive()` helpers; `adsRemoved()` = `removeAds || isPremium()`
  gates every ad-show path
- hint counter (`hintCount`/`hintPack`) if `hint_pack` sold;
  `undoPack` counter if `undo_pack` sold; decrement skipped while a
  pass is active
- `starter_pack`, `season_pass_monthly`, `weekly_pass` handlers grant
  full advertised bundle (not partial)
- Free Coins menu surface (rewarded ad, 25 coins / 4 h cooldown)
- Continue button when last-progress exists
- theme progress strip + theme-unlock card with 6-chip palette preview
- 7-day login-streak reward ladder (replaces simpler streak UI)
- starter-pack-on-first-launch popup
- Restore Purchases + Privacy Policy in Settings; `MainActivity.java`
  exposes `@JavascriptInterface restorePurchases()` and
  `openUrl(String)`

Usually **runtime-injected** via an audit-addendum `<script>` at the
bottom of `game.html` — static menu is capped at 6 tappable elements
(`check_menu_button_count`). `check_retention_features` +
`check_menu_completeness` enforce.

## Subscription/bundle promise parity

Every IAP-description benefit needs a code flag.
`season_pass_monthly $4.99/mo` ("ad-free + 100 daily coins + all
themes + unlimited hints") requires `adsRemoved()`,
`lastSeasonGrantDate` daily-grant, `isPremium()` theme unlock,
premium-gated hint decrement. `weekly_pass $1.99/wk` ("+50 daily
coins") requires `lastWeeklyGrantDate` +50 grant. Monthly priced ABOVE
weekly AND grants the bigger daily bonus — monthly is the unambiguous
best deal; weekly is low-commitment entry. 2048-style games word
"unlimited hints" as "unlimited undos". `check_subscription_parity`
enforces.

## Coin tier ladder

Every game selling any coin pack ships the full four-tier ladder
(strictly monotonic: each tier costs more AND gives more coins AND a
better coins/$ rate):

| SKU | Price | Coins | Coins/$ |
|---|---|---|---|
| `coins_small`  | $0.99 |  100 | ~101 |
| `coins_medium` | $2.99 |  400 | ~134 |
| `coins_large`  | $4.99 |  800 | ~160 |
| `coins_mega`   | $9.99 | 2000 | ~200 (best value — anchor) |

Replaces pre-2026-05 layout where `coins_large` was a $2.99
cheap-anchor below `coins_medium` — confused returning buyers,
forbidden. Partial ladders also forbidden. `check_coin_tier_ladder`
blocks both. (`lives_5_coins`-style in-game-currency products don't
count.)

## Booster catalog by genre

| Genre | Booster set |
|---|---|
| Sort-puzzle (Water Sort, etc.) | Color Reveal (hint), Steady Pour (undo), Fresh Start (restart), Extra Tube, Magic Wand |
| Picross (Nonogram, etc.)       | Hint, Undo, Reset, Check, Reveal Row, Reveal Cell |
| 2048-like                      | Undo, New Game, Magic Merge, Remove Tile |

Shop SKU catalog and in-game booster set must match (sold pack needs
mechanic; booster button needs coins-or-ad cost).
`check_booster_catalog` enforces by genre keyword.

## Cross-cutting menu requirements

Every game's main menu surfaces (statically or injected): Continue (if
applicable) · Play · Daily Challenge/streak · Levels/Shop/Games row ·
Missions w/ count · Stats/High Scores · Free Coins (rewarded ad,
25/4h) · Weekly Tournament banner w/ synthetic bracket · theme
progress strip · season-pass active badge when applicable. Static
tappable elements capped at 6 — rest go in runtime injection.

## Seasonal events

Every game ships a `SEASONAL_EVENTS` constant covering at least
October (Halloween), December (Winter), February (Spring). On init in
matching month: temporarily unlock event theme + inject 5 bonus levels
with event palette (leveled games) OR grant a 7-day 1.5× multiplier
(non-leveled like 2048). Menu shows event banner while active.
`check_seasonal_events` enforces.

## Weekly tournament (synthetic bracket)

Replaces old "Weekly: play any 5 levels" banner. Track
best-metric-this-week (best-level for level games, best-score for
2048), map through per-game `WEEKLY_BRACKETS` (10/25/50/75% tiers),
show "🏆 This week — <metric> · Top <pct>%", reset Monday 00:00 local,
award 100 coins for top 25% / 250 for top 10%, granted at week
rollover next time app opens within 7 days.

---

## Red lines — never do these

Any one can terminate the developer account.

1. **No two apps with byte-identical `game.html`.** Replace gameplay
   logic immediately after copying `_template/`. Blocked.
2. **App folder name == `<title>` tag.** Folder `Metronome/` cannot
   contain `<title>Dice Roller</title>`.
3. **No templated store listing copy across apps.** Title / short /
   subtitle / full hand-written per app.
4. **No reused AdMob IDs, IAP product IDs, or package names.**
5. **No batch-publishing in short windows.** 2-3 unique apps/week
   sustained ceiling. Silence → 5+ in one week trips Google's velocity
   heuristic.
6. **No two apps shipping the same publish window with visually
   identical store assets** (same icon focal, byte-identical feature
   graphic, screenshots that only swap inner gameplay over a shared
   frame). `check_cross_app_asset_similarity` +
   `check_screenshot_template_reuse`.
7. **Don't "de-duplicate" wrapper code** (`MainActivity.java`,
   `NotificationReceiver.java`). It's shared SDK infra (same pattern
   as Voodoo/SayGames/King). Google penalizes content similarity, not
   wrapper similarity.
8. **No committed secrets** (`keystore.properties` w/ real passwords,
   sensitive `google-services.json`). `.gitignore` them.
9. **No push notifications to Kids apps.** Play Families forbids. See
   `QUALITY_PLAYBOOK.md` §11.8.
10. **Never publish any of the 33 BLOCKED_APPS placeholder clones**
    without rewriting `game.html` first. The byte-identical Dice
    Roller `game.html` across 33 folders is the single highest-risk
    thing in this repo. `check_blocked_apps` — never override.

---

## Shipping cadence

**2 genuinely-distinct apps/week from week 1**, ramping to 3+/week if
productivity allows. User upload work ~30 min/app via
`RELEASE_HANDOFF.md`.

Risk at this pace is **similarity between apps**, not velocity.
Google's Repetitive Content classifier triggers on: same `game.html`
with renamed functions; same icon composition with swapped colors;
same screenshots with swapped frame contents; same listing copy with
template substitutions; same screen flows/state machines.
`pre_publish_check.py` blocks all.

**"Unique enough" means all 5:**
1. `game.html` mechanic + state model + level generation different
2. Icon focal element different (flasks vs blocks vs tiles vs ropes)
3. Feature graphic layout different (not template with swapped
   content)
4. Screenshot inner content different (frame can be shared, gameplay
   can't)
5. Listing copy hand-written for THIS app

**Not capacity-limited** (don't try to vary): wrapper code identical
across apps; same monetization stack (AdMob + IAP + Firebase); same
brand colors/fonts/footer in marketing frames; same wrapper SDKs +
versions.

**Anti-suspension safeguards (mandatory at scale):**
1. One app per genre cluster per 7-day window.
2. Crash rate <1%, ANR <0.5% per app (one spike at 50+ portfolio =
   account-level review).
3. Never publish from `BLOCKED_APPS`.
4. Listing-copy opening-line variety. Don't open every
   `full_description.txt` with "Welcome to {AppName}!" — Google
   detects template-fill.
5. Cross-promotion ("More Games" panel) = GOOD signal; required from
   app #2 onward.
6. Stagger AdMob app creation: max 2/day, 5/week (separate anti-fraud
   system from Play Console).
7. Reset icon palette pool every 10 apps. ~20 distinct vivid hues
   exist; after 30 apps you hit perceptual hash collisions even with
   different focal elements. Use textured/patterned backgrounds to
   break hashes.

**Sustaining 100+ apps:** run `pre_publish_check.py` against the full
portfolio weekly (N² pairwise; new app distinct from latest may
collide with #18); diversify ~⅓ puzzle / ~⅓ casual / ~⅓ utility; watch
crash rate weekly across the portfolio. The fix for a check blocking
at app #60 is *fix that app's distinctness*, not bypass the check.

---

## Required checks before any publish

Run `pre_publish_check.py <app>` and confirm zero blocking. Covers:
duplicate `game.html`, BLOCKED_APPS membership, folder/title match,
unique package + AdMob + IAP IDs, icon perceptual similarity, feature
graphic + screenshot uniqueness, listing copy uniqueness, all required
assets present (icon 512, feature 1024×500, icon 1024, ≥2 phone
screenshots), metadata valid, canonical URLs match, no stale per-app
`privacy-policy.html`, no `pegasusgames.example` / `@outlook.com` /
`ENTER_*` placeholders, no prohibited language, AdMob ID matches
manifest+MainActivity, every `iaps.json` entry has canonical
`description` (≤200 chars from `IAP_CATALOG.md`), 4 archetypes set in
`app_themes.py` + `metadata/app_identity.md` present, all 13 locales
present, menu button count ≤6, keystore present + SHA1 matches
`upload_key_sha1`.

**For retention-stack games** (sell `season_pass_monthly`),
additionally enforces: IAP grant parity (literal grant ==
`iaps.json` description), retention parity (`replayPendingGrants`,
`isSeasonActive`, wrapped `onPurchaseSuccess`, hint/undo counters),
subscription promise parity, coin tier ladder (all 4 SKUs), booster
catalog, menu completeness (Continue / Free Coins / theme strip /
weekly tournament / Daily / Stats markers), `SEASONAL_EVENTS` table
covering Oct/Dec/Feb. Long-tail utility apps (no season pass, no coin
packs) exempt.

**If any blocker fails: stop.** Do not build, do not upload, do not
advance.

---

## State of the apps (last audit: 2026-05-15; state updated: 2026-05-20)

- **Hero (1):** **WaterSortPuzzle** — gets meta-loop, live ops, real
  mascot, any "above-baseline" investment. Don't treat as
  just-another-flagship in sprint planning. See
  `COMPETITIVE_BENCHMARK.md` §9-10.
- **Shipped to Play (3):** **WaterSortPuzzle** (v2.0.3), **Nonogram**
  (v1.1.3), **Puzzle2048** (v1.1.3) — all live on the Play Store as of
  2026-05-20. Audited + retention-complete: full coin ladder,
  Season/Weekly Pass w/ honored benefits, hint/undo counters, genre
  boosters, Free Coins, Continue, theme strip + unlock card, 7-day
  login ladder, weekly tournament, seasonal events, Restore/Privacy.
  All 13 locales translated; phone + tablet 7"/10" screenshots.
  `pre_publish_check` clean. Next release for each = bump versionCode,
  rebuild the AAB, upload (see each app's `RELEASE_HANDOFF.md`).
- **In Play review (1):** **UnblockPuzzle** (v1.1.1, versionCode 7) —
  uploaded 2026-05-25, awaiting Play review. Code clean,
  `pre_publish_check` clean (modulo iOS surfaces — user is
  Android-only), all 13 locales, phone + tablet 7"/10" screenshots
  showcasing all themes, real AdMob IDs + Play license key wired,
  solver-validated levels, dedicated keystore.
- **2026-05-12/13 coin/pass overhaul (portfolio-wide):** coin ladder
  rewritten to the four-tier ladder above (was `coins_small $0.99/100`,
  `coins_large $2.99/500` cheap-anchor). Passes swapped:
  `weekly_pass $1.99/wk` (+50/day), `season_pass_monthly $4.99/mo`
  (+100/day) — monthly is the unambiguous best deal in both price and
  per-day value. All ~155 apps' `iaps.json` + 5 flagships' grant logic
  & shop UI + every doc + enforcement scripts updated via
  `scripts/migrate_coin_ladder_2026_05.py`. Price + grant changes need
  re-entering in Play Console for any app already listed; the 3
  shipped builds (WaterSortPuzzle v2.0.3 / Nonogram v1.1.3 /
  Puzzle2048 v1.1.3) were built post-overhaul and carry the four-tier
  ladder natively.
- **Screenshots (grandfathered):** WaterSortPuzzle/Nonogram/Puzzle2048
  reuse same captured levels across phone + tablet 7" + tablet 10" —
  left as-is on purpose; **do NOT rework**. Every NEW app must give
  each of the 3 surfaces fully distinct raws + headlines + wrapper
  variants (see `SHIP_GAME.md` Phase 3.6).
- **In ship prep (1):** **PipeConnect** (v1.7.2). Full metadata, all
  13 locales, phone + tablet screenshots, four-tier coin ladder,
  dedicated keystore. Carries AdMob test-ID placeholders
  (`ca-app-pub-3940256099942544`) — those clear only when the user
  does the AdMob setup in `RELEASE_HANDOFF.md` Step 1 (Phase 6), so
  they always show as `pre_publish_check` blockers until upload prep.
  As of 2026-05-25 also has 3 unfixed code blockers: `weekly_pass`
  routed through INAPP not SUBS billing
  (`check_subscription_routing`), no Restore Purchases control in
  `game.html` (`check_restore_purchases_ui`), and interstitials aren't
  gated by a level/game counter (`check_interstitial_cadence`). Fix
  all three before shipping.
- **Recently deleted:** BallSortPuzzle (2026-04-30 — too similar to
  WaterSortPuzzle, ~zero downloads); removed from working tree, from
  `app_themes.py` / `dedup_similar_apps.py` / `promo.json`.
- **Unique but thin (~150):** `game.html` matches folder but
  5-20 KB. Needs game-logic expansion + metadata.
- **Placeholder clones — DO NOT PUBLISH (33):** DiceRoller,
  EmotionFlash, FindDifference, FlashlightSOS, FruitMerge,
  GuitarChords, HiddenObject, JigsawPuzzle, MahjongSolitaire,
  MemoryCard, Metronome, MovieTrivia, MultiplicationGame, MusicTheory,
  NumberMemory, PasswordGen, PatternSequence, PianoKeyboard, PinPull,
  QRCodeGen, RandomName, RandomNumber, RandomRecipe, ScienceQuiz,
  ScrewPuzzle, SlidingTiles, SolarSystem, SportsQuiz, Sumplete,
  TripleMatch, UkuleleChords, WordScramble, WordSearch. Blocked from
  release until `game.html` rewritten. **All 33 still in repo (May
  2026 audit)** — run `cleanup_repo.py` to move them out. Byte-identical
  Dice Roller `game.html` across 33 folders is one accidental override
  away from account termination, even with `BLOCKED_APPS` enforcement.

---

## Workflows

### Finishing a thin/new app
`SHIP_GAME.md` Phases 1-8 are authoritative. Don't reimplement steps
inline.

### Modifying the shared wrapper
1. Change in one app first, test
2. Write migration script (see `fix_all_apps.py` pattern) for all apps
3. Preserve per-app values: package, AdMob IDs, IAP IDs, theme colors
4. `--dry-run` w/ diff before writing
5. Bump `versionCode` of all affected apps

### Mass-change scripts
- `BASE` constant pointing at repo root
- Iterate only real app dirs (skip `_template`, `_release`,
  `__pycache__`, hidden)
- Preserve per-app values: `applicationId`, AdMob IDs, IAP IDs,
  package statements, `WEBVIEW_BG_COLOR`, icons, store assets, metadata
- Print intent before doing; `--dry-run` for non-trivial changes
- Match `fix_all_apps.py` / `prepare_for_publish.py` style

---

## Honest-gap handling: never ship with known defects

Pattern to avoid: complete most of the work → list 2-3 "honestly
surfaced known gaps" → hand off → user ships with gaps. Issues
compound.

**Honest gaps are NOT a substitute for fixing.** If during a SHIP_GAME
run you find any of:
- Sparse/empty screenshot board or wasted canvas
- Headline doesn't match game capability
- Phase 8.3 functional smoke test wasn't run
- A button or screen path not verified
- A required check skipped because "script doesn't support it"
- Any "verify before shipping" or "next-iteration polish" text

…STOP. Surface the defect with concrete options
("A fix headline / B extend generator / C remove claim — which?") and
wait for the user. Do NOT write a "Known gaps" section and proceed.

---

## Things to flag to the user

(Don't re-raise the 10 Red Lines; those are blocking, not surfacing.)

- Flagship app declared "ready" without a meta-loop (theme collection,
  achievements, world restoration). Per `COMPETITIVE_BENCHMARK.md` §3,
  no successful analog ships without one. Cheapest meta-loop is theme
  collection (~1 day).
- Flagship `full_description.txt` opening with a description ("Pour
  and sort colored water") instead of a hook ("Welcome to Water Sort,
  the most relaxing pour-sort puzzle on Google Play"). Per §1,
  leader-format opening required for every flagship.
- Puzzle/sort game listing missing "relaxing" / "satisfying" / "ASMR"
  / "offline" when the app has those qualities. Per §2, these drive
  ASO in casual puzzle.
- Two apps in same genre cluster shipping within 7 days.
- Auto-generated listings via template substitution.
- `game.html` <~8 KB planned for publishing.
- Reused screenshots across apps.
- **Main menu / Shop / "More Games" / Settings screens used as
  screenshots.** Every slot must show ACTUAL GAMEPLAY at varied levels
  (early/mid/late boards, daily-challenge active, streak banner). A
  main-menu shot wastes a slot (it shows buttons, not the game); a
  shop or More-Games panel reads as "this app is mostly a paywall and
  a list of other apps". `capture_screenshots.py` no longer captures a
  menu slot — it grabs 6 gameplay slots, and the wrap scripts wrap
  exactly the raws that exist. Auto-blocked from May 2026. Applies
  retroactively to WaterSortPuzzle/Nonogram/Puzzle2048 — their menu
  screenshots were removed 2026-05-20 (now 6 phone / 6 tablet-7 / 5
  tablet-10 gameplay slots); no more grandfathering of those three.
- **Screenshot set that doesn't show every theme.** If the app has a
  theme system (block/tile palettes and/or light-vs-dark UI themes),
  the screenshots MUST showcase ALL of them — cycle a different theme
  through the board slots and include at least one shot of each UI
  theme. Configure it in `<App>/test/screenshot_taps.json` via the
  app's theme hooks (`setActiveTheme` / `applyUITheme`), the same way
  WaterSortPuzzle/Nonogram/Puzzle2048 do. See `SHIP_GAME.md` Step 3.3.
- Phone, tablet 7", tablet 10" reusing same raw page, wrapper, or
  headline. **Each of the 3 surfaces = fully distinct listing**, AND
  every wrapped screenshot within a surface has unique raw + unique
  headline + visually distinct wrapper variant. Vary ALL of:
  1. **Game pages captured** — different in-app screens
     (menu vs board vs results vs daily etc.), no overlap across
     surfaces
  2. **Levels/boards** — even when same screen type, level # / layout
     / progress state differs
  3. **Wrapper variant** — different layout, headline placement,
     gradient direction, accent treatment (not one frame with different
     raws)
  4. **Headlines** — phone reads
     `metadata/screenshot_headlines.json`; tablets read
     `screenshot_headlines_tablet_7.json` and `_tablet_10.json`
     (`wrap_tablet_screenshots.py` falls back to phone copy when
     missing — that's the failure mode to avoid)
  WaterSortPuzzle/Nonogram/Puzzle2048 grandfathered — don't rework
  retroactively. See `SHIP_GAME.md` Phase 3.6.
- Any temptation to use Puppeteer / headless Chromium for screenshots —
  **emulator-only** per `QUALITY_PLAYBOOK.md` §7.0 + `SHIP_GAME.md`
  §3.6. If `capture_screenshots.py` can't run (no AVD), surface as
  hard blocker; don't write a Puppeteer fallback.
- `keystore.properties` committed w/ real passwords.
- Per-app `store/privacy-policy.html` (delete on sight).
- Privacy/support URL not matching canonical.
- `iaps.json` not matching `MainActivity` IAP IDs.
- `iaps.json` entry missing `description`, >200 chars, or drifting
  from `IAP_CATALOG.md`. Play requires a description on every IAP.
  `init_app_metadata.py` scaffolds canonical; `check_iaps_descriptions`
  enforces.
- `content_rating.json:gambling_mechanics` set on a kids app.
- "Just ship the placeholder app, I'll fix it later" — **refuse**.
- Crash >1% or ANR >0.5% on any shipped app.
- App designed without picking 4 archetypes from `APP_ARCHETYPES.md`.
- Archetype A+M0+V1+T1 (the template — refuse without varying ≥2 of 4).
- Layout A used by >30% of shipped apps. Texture T1 by >40% after
  month 6.
- `metadata/app_identity.md` missing or empty at Phase 5.
- Missing any of 13 locale folders (note: `id` not `id-ID`; `uk` not
  `uk-UA`).
- Title translated to non-English (must stay English globally).
- Any `*.rejected` translation file (failed validation; edit + rename).
- Kids app translated files still containing "# KIDS APP — REVIEW BY
  NATIVE SPEAKER" header.
- Request to add Russian (`ru-RU`) to a single app — excluded
  portfolio-wide; either change policy in `TRANSLATIONS.md` or skip.
- In-game `i18n/<lang>.json` keys diverging from `en.json` — runtime
  fallback to English mid-screen looks broken.

---

## House style for generated code

- **Python:** stdlib only unless asked; docstring header; `BASE`
  constant; match `fix_all_apps.py`.
- **Java:** 4-space indent; grouped imports with section comments;
  match existing `MainActivity.java`.
- **HTML/CSS/JS in `game.html`:** single file; inline `<style>` +
  `<script>`; CSS custom properties for theme at top
  (`:root { --bg: ...; }`); no external CDN deps.
- **JSON:** 2-space indent, trailing newline, UTF-8, no comments.
- **Text metadata:** plain UTF-8, trim trailing whitespace, single
  trailing newline, no BOM.

---

## Scope note

User's long-term goal is all ~200 apps to flagship quality. ~1
app/week sustainably = 4 years for 200. When asked to "finish all of
them," help one at a time at the flagship bar rather than racing to
ship thin versions of many. 30 polished apps out-earn 200 thin ones at
a fraction of the policy risk.

---

## Common audit slips to check before every release

Memorialized from the 2026-05-15 WaterSortPuzzle/Nonogram/Puzzle2048
audit and the 2026-05-20 PipeConnect/UnblockPuzzle ship-prep pass.
Each line is now enforced by a `pre_publish_check.py` check.

- **PRODUCTS-array price strings in `game.html` MUST match `iaps.json`
  `price_usd` to the cent.** `iaps.json` is the catalog source of
  truth; the `PRODUCTS` array is the in-game display source of truth —
  they drift independently, and a shop quoting below what Play charges
  is a Misleading-Behavior risk. `check_price_string_parity` enforces.
- **Procedurally generated puzzles MUST be validated solvable / uniquely
  determined before shipping** — never trust the generator without a
  solver pass. If runtime validation is too slow for startup, validate
  offline and bake the result (Nonogram levels 151-500). For Rush Hour /
  unblock games: a non-red horizontal block on the red car's exit row can
  never clear and permanently walls the exit. The generator must forbid
  horizontal blocks on the exit row. The UnblockPuzzle May 2026 incident
  shipped 35/150 unsolvable levels from this exact mistake. The stored
  `optimal` move count MUST come from the solver, never a hand-guess —
  114/150 were wrong. The `puzzle solvability` pre-publish gate
  (`check_unblock_solvable.py`) blocks both failure modes.
- **Every shipping app MUST have 6 distinct screenshots per device
  surface** — `phone/`, `tablet_7/`, `tablet_10/` each carry exactly 6
  wrapped slots with distinct raws + headlines (user policy 2026-05-25;
  was 4-floor / 7-aspirational before). 6/6/6 is the standard; counts
  below it block pre-ship apps and warn on already-shipped apps.
  `check_screenshot_completeness` enforces.
- **Each non-gameplay screen type may appear AT MOST ONCE across the
  18-slot screenshot set** (phone + tablet_7 + tablet_10 combined).
  The other 14+ slots are gameplay at different levels — never the
  same screen captured twice across surfaces, even with different
  themes. Example: if Stats lives in phone slot 6, tablet_7 + tablet_10
  must NOT also include a Stats slot. Same for Level Complete overlay,
  Themes panel, Level Select grid, Missions, Daily Challenge.
  (User policy 2026-05-25 — old approach reused Stats / Themes / Level
  Complete on each of the 3 surfaces, which read as visual filler.)
- **Every theme sold in the shop MUST appear in the screenshot set.**
  Locked themes (e.g. Inferno at level 150, Galaxy at level 200) get
  unlocked via `_setup_taps` save-state seeding so the screenshots can
  showcase them. Showcasing only a subset reads as "the rest aren't
  worth showing." (User policy 2026-05-25.)
- **No dark default themes — light, eye-pleasing design by default.**
  Every app's on-install UI MUST use a light background, soft accents,
  and dark text on light surfaces. Dark UIs ship as a **coin-purchased
  unlockable** named "Midnight" — bought with the in-game soft currency
  the player already farms (not as a paid IAP). Dark-on-install looks
  unfinished in the first 5 seconds, ASO thumbnails read as
  low-contrast, and dark+colorful palettes are fatiguing for the long
  sessions casual puzzle players actually run. Applies to every NEW
  app and to any app being re-themed. (User policy 2026-05-25.)
- **Every app needs a DISTINCT light palette — "light" ≠ "beige".**
  Don't copy the UnblockPuzzle lavender/peach pastel onto every new
  app — players who install two apps will think they're the same
  shell with different gameplay. Each app picks its own light family
  (cream, sky, mint, sand, lavender, lemon, sage, blush, lilac…) and
  its own accent hue. Track allocations in `scripts/app_themes.py`
  alongside the 4-archetype mix. When auditing, treat two new apps
  with the same base bg (`#ece6f3`, `#faf8f3`, etc.) as a Repetitive
  Content risk. Current allocations:
  | App | Base bg | Family | Accent |
  |---|---|---|---|
  | UnblockPuzzle | `#ece6f3` | lavender/peach | pink+coral |
  | PipeConnect | `#eef4f8` | sky-blueprint | sky-blue+red |
  (User policy 2026-05-25, after PipeConnect first ship reused the
  UnblockPuzzle cream/beige look.)
- **Light-mode CSS must cover EVERY screen, including stats, game
  header, and game footer.** When refactoring a dark→light theme,
  audit any element whose color is `color:white` / `rgba(255,255,255,…)`
  or hardcoded `#fff` text — those go invisible against a light
  surface. Run the app screen-by-screen (menu, gameplay, level select,
  shop, settings, stats, themes, missions, daily, level-complete
  overlay) before screenshotting. Likewise for Midnight: the dark
  override must cover the symmetric set, including `.game-header`
  and `.game-footer` containers — players otherwise see a cream
  header strip on a dark gameplay screen. (User policy 2026-05-25,
  after PipeConnect screenshots shipped with white-text stats and a
  cream-footer Midnight gameplay slot.)
- **Screenshot headlines MUST match screenshot content.** A "Daily
  Missions" headline over a plain gameplay board is a Play policy red
  flag. `check_screenshot_headline_match` enforces.
- **`RELEASE_HANDOFF.md` IAP tables MUST have every column populated.**
  An empty Name column means SKUs ship with blank display names.
  `check_iap_display_name_table` enforces.
- **Restore Purchases MUST be reachable from Settings in every game.**
  Refunds spike on reinstalls without it. `check_restore_purchases_ui`
  enforces.
- **Rewarded-ad callback handling MUST be queue-based, not overwrite.**
  A single pending-callback variable is a race that drops rewards.
- **Interstitial triggers MUST count levels/games played**, not only
  fire on "return to menu" — long uninterrupted sessions otherwise see
  zero interstitials. `check_interstitial_cadence` enforces.
- **Translations MUST be reviewed by native speakers for at least the
  top-3-revenue locales** — literal calques look amateur and depress
  conversion.
- **Every subscription SKU MUST be routed to the SUBS billing flow.**
  `launchPurchase()` in `MainActivity.java` picks INAPP vs SUBS per
  product ID; a subscription sent down the one-time INAPP path makes
  Play return no `ProductDetails`, so `launchBillingFlow()` never fires
  and the purchase sheet never opens — a sold SKU that cannot be
  bought. Route every subscription through a `SUBSCRIPTION_PRODUCTS`
  set, never a hardcoded single-SKU `.equals` (the 2026-05-20
  UnblockPuzzle/PipeConnect `weekly_pass` dead-end).
  `check_subscription_routing` enforces.

---

## Growth/DAU baseline every game ships with

(2026-05-25 — implemented across WaterSort/Nonogram/Puzzle2048/UnblockPuzzle
as a portfolio standard. New apps must carry the full set before Phase 8.
`scripts/check_growth_features.py` enforces. JS side is delivered as six
runtime-injected shims — see `scripts/_growth_shim_[a..g].html` — keyed by
`data-growth-shim` so re-injection is idempotent.)

**Notifications (Part A).** Every game's MainActivity NativeBridge exposes
`scheduleDailyReminder(h,m)`, `scheduleStreakAtRisk(streakDays)`,
`scheduleLivesRefilled(whenMillis)`, `scheduleWinBack(d3/d7/d14/d30, title,
body)`, `cancelAllNotifications`, `setNotificationsEnabled`,
`getNotificationsEnabled`, `recordLastPlayed`, `hasNotificationPermission`,
`requestNotificationPermission`. The JS shim wires:
- Daily reminder at the user's rolling-average play hour (default 19).
- Streak-at-risk fires at 20:30 the day BEFORE reset (only when streak ≥ 3).
- Lives-refilled when the game tells us (`window.gScheduleLivesRefilled`).
- Win-back chain d3 / d7 / d14 / d30 from session end; cancelled + rescheduled
  on every app open. Day-7 grants +100 coins via `pendingWinBackReward`.
- 2/day cap honored; settings toggle adds a Notifications on/off row.
- Permission pre-prompt fires only AFTER first level clear, never on launch.

**Cross-promo flywheel (Part B).** Each app's `CROSS_PROMO_PACKAGES`
(MainActivity) / `<queries>` (manifest) / `PROMO_GAMES` (game.html) lists
the OTHER live portfolio apps only. **Pre-release apps are NEVER cross-promo
targets** — leave commented TODO markers (`com.pegasusgames.unblockpuzzle`,
`com.pegasusgames.pipeconnect` are excluded as of 2026-05-25). Install
reward 200 coins on auto-detect; double-sided welcome bonus 100 coins on
first launch from a sister portfolio app. Break-point card every 5th clear,
max once/session, never two sessions in a row. Cross-promo is **additive**
to the AdMob interstitial cadence, not a replacement.

**Streak freeze + visible milestone (Part D).** `state._streakFreezes`
default 1; auto-consume on a 1-day miss (restore the streak, toast
"🛡 Streak shield used"). Refill +1 free every 7 days of maintained streak,
buyable for 200 coins. Menu shows the next-milestone reward chip:
day 1=25🪙 · day 3=100🪙 · day 7=🎨 theme · day 14=500🪙 · day 30=🌟 permanent
theme + 1000🪙 · day 100=🏆 5000🪙. Day 30 must visibly beat day 3.

**First-session retention (Part E).** Levels 1-3 trivially solvable in <30s
(per-app design audit — flagged in `scripts/growth_open_items.md`). Loud
first-clear celebration: emoji-confetti + "You've got this! 499 more puzzles
to go." No interstitial on the first 3 clears (wrap `Android.showInterstitial`).
For non-obvious genres (Nonogram, Unblock-style), 3-step coachmark on first
launch behind `tutorialDone`. At end of session 1 (≥3 clears + tutorialDone),
show "Come back tomorrow for your daily bonus" + schedule the daily reminder.

**Virality (Part F).** Native bridge `shareText(String)` and `shareImage(b64,
caption)` via `ACTION_SEND`. Share-a-win button injected on 3-star /
high-score celebration overlays. Wordle-style shareable daily result on
`overlay-daily` completion: `<Game> Daily YYYY-MM-DD ✅ solved in N moves`
+ Play link for live apps (no link for pre-release apps until they ship).

**Leaderboards (Part G).** Play Games Services v2 — `submitScore`,
`showLeaderboard`, `signInPlayGames` bridge methods on every NativeBridge.
Submit on every clear / high-score. Menu "🏆 Leaderboard" button. The
existing synthetic weekly-tournament bracket stays as the fallback — PGS
layers on top, never replaces it. The `games_app_id` in `strings.xml` and
the JS-side `LEADERBOARD_ID` ship as placeholders; real values land via
Play Console (see `scripts/growth_open_items.md §B`).

**Pre-publish enforcement.** `scripts/check_growth_features.py` runs every
publish: NativeBridge surface presence, manifest `<queries>`, six growth
shim markers (`data-growth-shim="A".."G"`), no-pre-release-in-cross-promo,
and warning on placeholder PGS / `games_app_id`. Wired into
`pre_publish_check.py` as `[code] growth baseline`.

---

## Main-menu information hierarchy (mandatory)

Every game's main menu MUST collapse to three visual tiers and surface
glanceable hooks as TOP-BAR ICONS, not full-width promotional banners.
The 2026-05-25 audit showed `WaterSortPuzzle/Nonogram/Puzzle2048/UnblockPuzzle`
all had ~11 tappable surfaces on the menu (Free Coins banner + Tournament
banner + Theme strip + Season Pass banner + 6 buttons) which torched the
visual hierarchy and pushed Play below the fold. The 2026-05-27 restructure
lands as a runtime-injected shim — no app-specific edits required.

**Three tiers:**
1. **Tier 1 — ONE dominant primary button.** Either `Continue · Level N`
   (or `Continue · <score>` for 2048) when state has resumable progress,
   else `Play`. Largest element on the menu. Patched by the shim from
   whichever class the app uses: `#menuPlayBtn` / `.btn-primary` /
   `.menu-primary` / `.menu-tile-primary` / `.btn-play`.
2. **Tier 2 — Daily Challenge with streak baked in.** Single secondary
   button, label format `Daily · 🔥N` when streak > 0. No separate
   streak chip / banner anywhere on the menu.
3. **Tier 3 — single icon row.** Levels / Shop / Games / Settings as
   compact icon-only buttons. Total static tappable count on menu ≤ 6.

**Top-bar icons (replace the old banners):**
- 🪙 Free Coins (24-pixel circular button, green `+25` badge when ready,
  greyed + countdown title while on 4-hour cooldown). Click reuses the
  existing `claimFreeCoins` / `xClaimFreeCoins` handler. Direct
  `showRewardedAd` fallback.
- 🏆 Tournament. Click reuses
  `showTournament` / `xShowTournament` / `showWeeklyEventInfo`. Falls
  back to clicking the existing `weeklyEventBanner` element when no
  named handler exists.

The shim auto-mounts these into `.menu-header` if one exists; if the
game's menu has no header container (UnblockPuzzle, Nonogram), it
synthesizes a top-right absolute-positioned host. At 380px / 330px
logical widths the icons shrink + the lives-text label collapses to
heart+number only — top bar always fits on one line.

**Removed from the menu but NOT removed from the game:**
- Theme strip — relocated to the Themes screen (shim moves
  `xThemeStrip` / `xThemeStrip2048` to top of `themesScreen` /
  `screen-themes` when active).
- Season Pass promo — auto-surfaces inside Shop and on the no-lives
  overlay (shim calls `injectPassPromo()` when `shopScreen` / `screen-shop`
  / `overlay-nolives` becomes active).
- Seasonal-event banner — slimmed to a one-line ribbon (`xSeasonBanner`
  styled to ≤30px tall).
- Weekly Tournament details — still reachable via the top-bar 🏆 icon;
  no full-width banner on the menu.

**Forbidden on the menu screen markup:**
- Static `id="xFreeCoinsBtn"` / `id="xThemeStrip"` / `id="xPassPromo"`
  / `id="weeklyEventBanner"` elements INSIDE the menu container. The
  shim hides them at runtime, but a static menu-bound copy is harder
  to remove cleanly and trips `check_menu_hierarchy`.
- Any additional full-width promotional banner. Stack-ranked goal:
  user opens app → sees ONE button → taps → in puzzle in <2s.

**Implementation.** Single shim file at
`scripts/_growth_shim_menu.html` — copy verbatim as
`<script data-growth-shim="MENU">…</script>` at the bottom of every
shipping `game.html`. Idempotent (no-op on second injection). New apps
get it via the SHIP_GAME Phase 1 scaffold. Existing apps re-inject
when the shim is updated; the `_growth_shim_menu` script in scripts/
is the source of truth.

**Pre-publish enforcement.** `scripts/check_menu_hierarchy.py` runs
every publish: shim marker present, no forbidden static banners inside
the menu container, Tier 1 primary button selector matches at least one
element, Tier 2 Daily button + Tier 3 icon row reachable. Wired into
`pre_publish_check.py` as `[code] menu hierarchy`.

---

## Review 2026-05 fixes — invariants

Memorialized from the 2026-05-27 full-review pass. Each line is now a
pre-publish gate. Reverse one of these and the gate blocks the ship.

- **Puzzle win checks validate against CLUES/rules, never a single
  stored solution.** A player who finds an alternate valid solution
  must always win. Nonogram `checkPuzzle` / `checkAutoWin` now compare
  the player's row+column run-length encoding against the level's
  clues. Stored solutions are kept only as witnesses for the
  "X errors found" counter.
- **Every procedurally-generated puzzle level is uniqueness-gated
  before shipping.** Nonogram ships 80 offline-validated `PREGEN_10`
  10x10 boards + 150 `PREGEN_15` + 200 `PREGEN_20`; remaining
  generated boards go through a runtime `_countSolutionsUpTo(...) === 1`
  gate with a 300-attempt budget and a curated fallback.
  `scripts/check_nonogram_unique.py` is a hard pre-publish blocker;
  `scripts/verify_nonogram_pregen.js --fix` regenerates any board that
  later regresses. The same uniqueness-gate principle applies to Rush
  Hour / unblock (`check_unblock_solvable.py`) and any future
  procedural genre.
- **Rewarded-ad reward type strings in JS must exactly match the
  `onAdReward` handler branches.** Bare `Android.showRewarded(type)`
  calls that name a string with no matching `type === 'X'` /
  `case 'X'` branch (or a queued callback in callback-queue apps) are
  blocked by `scripts/check_reward_type_parity.py`. A watched ad must
  always grant.
- **Subscriptions disclose auto-renew price/period + cancel path at
  the point of purchase.** Every Season Pass / Weekly Pass button
  carries renewal disclosure text right under it via
  `scripts/_growth_shim_subs.html` (idempotent
  `data-growth-shim="SUBS"`), and Settings carries a Manage
  Subscriptions row linking
  https://play.google.com/store/account/subscriptions via the
  `Android.openUrl` bridge. Localized across 13 locales.
  `scripts/check_subscription_disclosure.py` blocks publish.
- **Rewarded-ad callbacks are queue-based, never single-pointer.**
  WaterSort uses `_pendingAdCallbacks[]`; Nonogram, Puzzle2048 use
  `_pendingRewardCbs[]`. New triggers no-op while the queue is
  non-empty (chokepoint disable). `onAdReward` drains the queue in
  try/catch. `onAdNotReady` / `onAdDismissed` clear the queue. The
  single-pointer model drops rewards under any concurrency.
- **Store descriptions state only true capability.** Real language
  count (not "20+"), no "global rank" / "leaderboard" wording for the
  synthetic weekly bracket (use "personal-best challenge" instead),
  and no "unique solution" / "no guessing" unless the app is in
  `check_description_claims.SOLVER_VERIFIED_APPS`. Soft-warned by
  `scripts/check_description_claims.py`.
- **Release notes describe only changes present in the build.**
  Promising "cleaner main menu" requires the `showScreen('menuScreen')`
  branch to no longer call `injectFreeCoins` / `injectThemeStrip` /
  `injectPassPromo` / `updateTournamentBanner` (those relocated to
  top-bar icons + deeper screens). Warned by
  `scripts/check_release_notes_match.py`.
- **Keystores and passwords never committed or shipped in archives.**
  `*.jks`, `*.keystore`, `keystore.properties`, `*.pem`, `*.der`,
  `local.properties`, `google-services.json`, and `release_aabs/` are
  gitignored at both repo root and every per-app root. Any zip
  shared with a third party MUST exclude `**/keystore.*` and
  `**/*.pem`. `keystore.properties` stores its password in plaintext
  (gradle requirement) — gitignore enforces never-shared.
- **z-index literals are forbidden in `game.html`.** Use the
  portfolio-wide `:root` scale: `--z-overlay-dim: 100`, `--z-banner:
  200`, `--z-toast: 300`, `--z-confirm: 400`, `--z-tutorial: 500`,
  `--z-modal: 700`, `--z-critical: 800`. `scripts/zindex_normalize`
  (one-off) collapsed every literal; new code uses `var(--z-modal)`
  etc.

---

## No competing runtime shims

Memorialized from the 2026-05-27 menu regression where shim D's
`injectMenuChips`, shim G's `injectButton`, and the MENU shim each
polled the menu DOM on their own `setInterval(..., 1500)`, fighting
over the top bar. The floating PGS pill landed on top of the settings
gear; chips overlapped the static Missions/Stats cards; the menu was
visually broken across all four shipping apps.

**The rule:** menu structure is rendered by ONE function on
`showScreen('menuScreen')`, never by multiple polling injectors. New
menu features extend that one render — they do NOT add a new shim
with its own timer. The render owner is `scripts/_growth_shim_menu.html`
(`renderMenu`); shim D and shim G keep only their non-menu behavioral
wiring (streak auto-restore, score submission).

**Absolute positioning is banned in the top bar.** The top bar is an
in-flow flex row: `[❤ lives] [🪙 coins] → spacer → [🪙 free-coins]
[🏆 ranks] [⚙ settings]`. Any `position:absolute` child overlaps the
settings gear at narrow widths (the 2026-05-27 incident).

**One rank entry point.** Leaderboard + synthetic weekly tournament
merge behind a single 🏆 Ranks icon that opens a two-tab sheet
("This Week" + "Leaderboard"). No floating PGS pill, no separate
🥇 medal icon, no `data-growth-leaderboard-btn` element.

**Pre-publish enforcement.** `scripts/check_menu_shims.py` blocks
publish if any of these regress:
- a forbidden polling injector (`injectMenuChips`, `injectButton`,
  `injectFreeCoins`, `injectThemeStrip`, `injectPassPromo`,
  `updateTournamentBanner`) is wrapped in `setInterval(...)`
- the rogue `data-growth-leaderboard-btn` element exists anywhere
- more than two rank-opening UI elements
- `[data-menu-icons]` carries `position:absolute`
Wired into `pre_publish_check.py` as `[code] menu shim hygiene`.

---

## Menu monetization placement

Memorialized 2026-05-27 round-2 fix. The main menu must surface ONLY
primary gameplay actions, never paid offers or full-width
advertising banners. Specifically:

- **No subscription / pass sales card on the main menu.** Season Pass
  and Weekly Pass cards live in the Shop screen (where purchase
  intent is) and as a compact CTA on the no-lives overlay. The MENU
  shim's `maybeFirePassPromo` triggers `injectPassPromo` on those
  screens only.
- **No theme strip on the main menu.** The "Next theme: <name> at
  level <N>" line renders on the Themes screen instead — the MENU
  shim materializes it on `showScreen('themesScreen' | 'screen-themes')`
  via `ensureThemeStrip` (calls the app's existing `injectThemeStrip`
  then relocates the element).
- **No tournament banner on the main menu.** The synthetic weekly
  bracket content moves into the "This Week" tab of the 🏆 Ranks
  sheet that opens from the top-bar icon. The MENU shim calls
  `updateTournamentBanner` from `openRanksSheet` so the data is
  fresh when the user opens it.
- **No full-width Free Coins button on the main menu.** Free Coins
  is the top-bar 🪙 icon with a `+25` badge (greyed + countdown
  when on cooldown).
- **No medal / second leaderboard icon.** Exactly two icons on the
  right side: `[🪙 free-coins] [🏆 ranks]` then `[⚙ settings]`.

**The four offending calls must not appear in any app's `boot()`
function or the `showScreen('menuScreen')` branch** — they're
materialized via the MENU shim at the right screen instead. CSS
inside the MENU shim hides any element with id `xPassPromo`,
`xFreeCoinsBtn`, `weeklyEventBanner`, `xThemeStrip`,
`xThemeStrip2048`, `xSeasonPassPromo`, or `xWeeklyPassPromo` that
ends up inside the menu container, as belt-and-braces against future
regressions.
