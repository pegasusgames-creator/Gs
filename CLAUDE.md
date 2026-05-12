# Pegasus Games — Claude Code Instructions

Portfolio of ~200 Android apps/games sharing a common WebView wrapper.
Each top-level folder (except `_template/`, `_release/`, `docs/`,
`scripts/`) is one app with `game.html` inside `MainActivity.java`.
Read this file end-to-end before doing anything in here.

**Repo layout:**
- `Gs/CLAUDE.md` — this file (root)
- `Gs/README.md` — public repo description (root)
- `Gs/docs/` — all `.md` reference docs (`SHIP_GAME.md`,
  `QUALITY_PLAYBOOK.md`, `APP_ARCHETYPES.md`, `TRANSLATIONS.md`,
  `COMPETITIVE_BENCHMARK.md`, `NOTIFICATIONS_IMPL.md`)
- `Gs/scripts/` — all Python scripts (`pre_publish_check.py`,
  `build_release.py`, `gen_handoff.py`, `gen_translations.py`,
  `gen_store_paste.py`, `pepk_command.py`, `gen_upload_keystore.py`,
  `consult_designer.py`, `init_app_metadata.py`,
  `capture_screenshots.py`, `wrap_screenshots.py`,
  `wrap_tablet_screenshots.py`, `app_themes.py`,
  `dedup_similar_apps.py`, `cleanup_repo.py`, `fix_all_apps.py`,
  `prepare_for_publish.py`)
- `Gs/<AppName>/` — one folder per app

When this file references files by bare name (e.g. `SHIP_GAME.md` or
`pre_publish_check.py`), assume `docs/` or `scripts/` prefix
respectively. Run scripts from the repo root:
`python3 scripts/pre_publish_check.py <AppName>`.

## Companion files

- **`SHIP_GAME.md`** — MASTER RELEASE WORKFLOW. When user says "ship X" /
  "release X" / equivalent, read end-to-end and execute all 8 phases
  without asking unless `SHIP_GAME.md` "Hard blockers" hits.
- **`QUALITY_PLAYBOOK.md`** — Design / UX / gameplay / monetization bar.
  Read whenever touching visuals, gameplay, menu, onboarding, or money.
- **`APP_ARCHETYPES.md`** — Layout (9) × Mascot (5) × Voice (8) × Texture (8).
  Each new app picks one from each, recorded in `app_themes.py`. Read in
  Phase 1.
- **`TRANSLATIONS.md`** — 13 locales (en-US + ar, de-DE, es-419, fr-FR,
  hi-IN, id, it-IT, ja-JP, pt-BR, tr-TR, uk, zh-CN). Russian excluded.
  Indonesian uses `id` (not `id-ID`) and Ukrainian uses `uk` (not `uk-UA`)
  per Play Console. Title stays English globally. Read in Phase 4.5.
- **`COMPETITIVE_BENCHMARK.md`** — Analysis of top-grossing analogs
  (Royal Match, Block Blast, Water Sort variants) and the specific
  patterns Pegasus apps need to match: listing structure, ASMR keywords,
  meta-loops, booster economy, screenshot order, icon production. Read
  during Phase 1 of every flagship app.
- **`NOTIFICATIONS_IMPL.md`** — Java + JS reference for local notifications.
- **`pre_publish_check.py`** — guard script (auto-run by `build_release.py`)
- **`build_release.py`** — Phase 5/7/8 automation
- **`gen_handoff.py`** — generates per-app `RELEASE_HANDOFF.md`
- **`gen_translations.py`** — Phase 4.5 translations (needs `ANTHROPIC_API_KEY`)
- **`consult_designer.py`** — sub-agent design questions during Phase 1/8
- **`init_app_metadata.py`** — scaffolds metadata/store folders
- **`gen_store_paste.py`** — assembles `<App>/STORE_PASTE.md` from
  per-locale metadata. Uses Play Console's actual locale tags (`<uk>`,
  `<id>` — never `<uk-UA>` / `<id-ID>`). `pre_publish_check.py
  check_store_paste_locale_tags` blocks any STORE_PASTE.md that drifts
  back to BCP-47 country codes
- **`gen_upload_keystore.py`** — generates `<App>/android/upload-
  keystore.jks` + `upload_certificate.pem` and rewrites
  `keystore.properties` so gradle signs AABs with the upload key
  (which Play Console requires to differ from the app signing key).
  Run after PEPK setup, before first AAB build for that app
- **`pepk_command.py`** — prints the exact PEPK command for one app,
  pulling alias + password from `keystore.properties`. Refuses to run
  if `encryption_public_key.pem` or `pepk.jar` isn't already in
  `<App>/android/` (the human must download both from Play Console
  before this script can produce a useful output). The produced
  `.zip` is what gets uploaded under Play Console's "App signing"
  flow — registers the local keystore as the app's signing key with
  no upload-key reset wait
- **`capture_screenshots.py`** — emulator-driven (uses `adb`)
- **`wrap_screenshots.py` / `wrap_tablet_screenshots.py`** — marketing frames
- **`app_themes.py`** — per-app palette + 4-archetype registry
- **`dedup_similar_apps.py`** — finds clusters with too-similar mechanics
- **`cleanup_repo.py`** — moves BLOCKED clones + deleted apps OUT of the
  working tree (one-time cleanup script; run with `--dry-run` first)

---

## Canonical contact info and URLs (use everywhere)

These are shared across **all apps**. Never invent per-app URLs/emails.

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

**Per-app `store/privacy-policy.html` files SHOULD NOT exist.** Single
shared URL is the source of truth. Delete any per-app copies on sight
(legal liability if Play Console listing disagrees).

**Per-app Data Safety forms ARE per-app** — the shared privacy policy is
a superset; each app's Play Console Data Safety form must accurately
reflect what THAT app does. Don't assume "shared policy = shared form."

The Privacy URL must include `.html` (no trailing slash).

---

## Keystore management — per-app, not global

Each app has its OWN upload keystore at `<App>/android/keystore.jks`,
with the password in `<App>/android/keystore.properties` (gitignored).

This is the OPPOSITE of the original "single shared upload keystore"
plan. We learned the hard way (May 2026: Nonogram's first upload was
mistakenly signed with WaterSort's keystore, permanently locking
Nonogram's Play Console listing to WaterSort's upload key and forcing
an upload-key reset request). A single shared keystore means one
mistake or loss cascades across the entire portfolio.

**Current state (May 2026 audit):**
- WaterSort, Nonogram, Puzzle2048, PipeConnect, UnblockPuzzle each
  have their own dedicated keystore (correct)
- 154 OTHER apps (mostly long-tail utility/quiz apps) still share
  `pegasusgames-release.jks` — this is forbidden going forward.
  Migrate via `scripts/migrate_to_per_app_keystores.py` BEFORE any of
  those 154 apps ships to Play Console
- `pegasusgames-release.jks` (the shared keystore, fingerprint
  E0:BD:7F:24:...) should ONLY be used for apps that have already
  been uploaded with it. Once Play Console has registered an upload
  key for an app, you cannot change it without a reset request

**Mandatory rules going forward:**

1. **Every NEW app gets its own keystore.** Add to SHIP_GAME Phase 1
   setup. Generate via:
   ```
   cd <App>/android
   keytool -genkey -v -keystore keystore.jks -keyalg RSA -keysize 2048 \
           -validity 10000 -alias <appname>
   ```
   Use a strong random password (16+ chars, alphanumeric).
   `migrate_to_per_app_keystores.py --app NewApp` does this in one
   step including alias selection and `keystore.properties` setup.

2. **Back up immediately, three ways.** Within 24 hours of generating
   a keystore (and ALWAYS before the first Play Console upload):
   - Local: `<App>/android/keystore.jks` (gitignored — never commit)
   - Cloud: encrypted upload to Google Drive in pegasusgames@atomicmail.io
   - Physical: copy to a dedicated USB stick (label it "Pegasus
     Keystores", keep it physically separate from the dev machine)
   The local copy is the working file. The other two are recovery
   paths. NEVER rely only on the local copy.

3. **`keystore.properties` is gitignored** but has a versioned
   `keystore.properties.template` next to it with placeholder values.
   The actual file contains: `storeFile`, `storePassword`, `keyAlias`,
   `keyPassword`. Losing the password = losing access to the keystore =
   needing an upload-key reset. Record passwords in a password manager
   alongside each app's SHA1 fingerprint.

4. **Record the SHA1 fingerprint per app** in
   `<App>/metadata/app_info.json` under `upload_key_sha1`. After first
   successful Play Console upload, this lets future builds verify
   they're signing with the correct keystore before re-uploading:
   ```
   keytool -printcert -jarfile app/build/outputs/bundle/release/app-release.aab | grep SHA1
   # must match app_info.json:upload_key_sha1
   ```
   `pre_publish_check.py check_keystore_present` enforces this.

5. **NEVER copy a keystore.properties from one app to another.** This
   was the Nonogram failure mode — Claude Code (or someone) likely
   copied WaterSort's keystore.properties into Nonogram/android/, the
   first build signed with WaterSort's key, Play Console registered it
   permanently. If a `keystore.properties` is missing, generate a NEW
   keystore for that app — never reuse another app's.

6. **If a keystore is lost,** request an upload-key reset in Play
   Console (Setup → App integrity → App signing → Request upload key
   reset). Takes 1-3 business days. Generate a new keystore AND BACK
   IT UP THREE WAYS FIRST, then submit the reset request with the new
   public certificate. Update `app_info.json:upload_key_sha1` after the
   reset is approved.

**Pre-publish enforcement** (in `pre_publish_check.py check_keystore_present`):
- BLOCKS if `<App>/android/keystore.jks` is missing
- BLOCKS if `keystore.properties` is missing
- BLOCKS if the keystore's actual SHA1 doesn't match
  `metadata/app_info.json:upload_key_sha1`
- WARNS if `app_info.json:upload_key_sha1` isn't set (records absence;
  fill in after first successful Play Console upload)

### Play Console "App signing settings" — REQUIRED before first AAB upload

Every new app in the Pegasus Games account is auto-enrolled in Play
App Signing with a Google-generated upload key (cert SHA-1
`EC:24:33:14:46:29:71:D1:4C:B0:2B:86:D0:4D:D4:FF:EC:6F:86:B5`,
owned by `O=Google, OU=Bundle & Delivery`). Google holds the private
key for that — uploading an AAB signed with the local `keystore.jks`
will be rejected. Two paths to fix it; the **PEPK option below is
preferred** because it avoids the 1-3 day Google approval wait of
the reset request.

**Two keystores per app (the Play App Signing reality):**

Play Console enforces that the **app signing key and upload key
MUST be different**. After completing PEPK in step 4, leaving step 5
empty means Play implicitly tries to make app signing key = upload
key, and the release page errors with "ключ завантаження має
відрізнятися від ключа розгортання". So every app actually needs
TWO keystores:

| File | SHA-1 example (Puzzle2048) | Role |
|---|---|---|
| `<App>/android/keystore.jks` | `97:71:24:...` | **App signing key** — uploaded encrypted via PEPK in step 4. Play uses this server-side to re-sign delivered APKs. Gradle does NOT use this for AAB signing. |
| `<App>/android/upload-keystore.jks` | `76:A0:1D:...` | **Upload key** — gradle signs AABs with this. Its public cert (`upload_certificate.pem`) is uploaded via step 5c. Play validates uploads against this cert. |

`<App>/android/keystore.properties` points gradle at the **upload**
keystore, not the app signing one — so `bundleRelease` produces an
AAB Play Console will accept.

**PEPK + upload-keystore setup (the one-time per-app flow):**

Before triggering bundleRelease for any app that has not yet been
uploaded to Play Console:

1. In Play Console for the app: **App integrity → App signing**.
2. Pick radio **"Експортувати й завантажити ключ зі сховища Java"**
   (Export and upload key from Java keystore) — NOT the default
   "Let Google manage" option.
3. Download both files into `<App>/android/`:
   - `encryption_public_key.pem` (step 1 link on the page)
   - `pepk.jar`                    (step 2 link on the page)
4. Run `python3 scripts/pepk_command.py <App>` to print the PEPK
   command. Run it; it produces `<App>/android/<alias>_pepk.zip`.
5. Upload that `.zip` via step 4 link in Play Console.
6. Run `python3 scripts/gen_upload_keystore.py <App>`. This
   generates a SEPARATE upload keystore + cert and rewrites
   `keystore.properties` to point gradle at it.
7. Upload `<App>/android/upload_certificate.pem` via step 5c link
   in Play Console.
8. Save. Done — the red "must differ" error clears, and any
   subsequent `bundleRelease` produces an AAB Play accepts.

**Reset request (fallback, takes 1-3 business days):**

Only needed if the app's first AAB was already uploaded with a
wrong-key AAB and Play has locked in the Google-generated upload
key. Submit `<App>/android/upload_cert_request.pem` (auto-generated
by `migrate_to_per_app_keystores.py`) via Play Console "Request
upload key reset". WaterSort and Nonogram already went through this
path. All other apps in the portfolio should use the PEPK +
upload-keystore flow above on their first Play Console listing
setup, BEFORE any AAB upload, to avoid the reset wait.

**Shipping flag:** SHIP_GAME.md Phase 7 (AAB build + upload) MUST
verify three things before kicking off bundleRelease:
1. `<App>/android/encryption_public_key.pem` and `pepk.jar` exist
   (PEPK prerequisites downloaded).
2. `<App>/android/upload-keystore.jks` and `upload_certificate.pem`
   exist (separate upload key generated).
3. `<App>/android/keystore.properties` `storeFile` points at
   `upload-keystore.jks` (so gradle signs AABs with the upload key).
If any of these isn't true, hard-block the upload step and run the
PEPK + gen_upload_keystore.py flow first.

---

## Per-app folder structure

```
<AppName>/
├── android/                            # Android project
├── ios/                                # iOS scaffolding
├── store/
│   ├── icon_512_playstore.png          # Google: 512×512 PNG, no alpha
│   ├── feature_graphic_1024x500.png    # Google: 1024×500, no transparency
│   ├── icon_1024_appstore.png          # Apple: 1024×1024, no alpha
│   └── screenshots/
│       ├── phone/                      # 2-8 portrait PNGs (1080×2400)
│       │   ├── raw/                    # captured by emulator (01-07.png)
│       │   └── 01.png ... 07.png       # wrapped marketing frames
│       ├── tablet_7/                   # Optional 7" (1200×1920)
│       ├── tablet_10/                  # Optional 10" (1800×2560)
│       └── iphone_6_9/                 # Apple required: 6.9" (1320×2868)
├── test/
│   ├── seed_screenshot_state.js        # localStorage seed (mid-game state)
│   └── screenshot_taps.json            # per-app tap overrides (optional)
└── metadata/
    ├── app_identity.md                 # 4-archetype choices + feel description
    ├── screenshot_headlines.json       # 7 headlines for marketing wrap
    ├── en-US/                          # baseline locale (always required)
    │   ├── title.txt                   # ≤30 chars (global; not translated)
    │   ├── short_description.txt       # ≤80 chars (Google)
    │   ├── subtitle.txt                # ≤30 chars (Apple)
    │   ├── full_description.txt        # ≤4000 chars
    │   ├── keywords.txt                # ≤100 chars (Apple, comma-sep)
    │   ├── promotional_text.txt        # ≤170 chars (Apple)
    │   └── release_notes.txt           # ≤500 chars
    ├── ar/, de-DE/, es-419/, fr-FR/, hi-IN/, id/, it-IT/, ja-JP/,
    │   pt-BR/, tr-TR/, uk/, zh-CN/     # 12 more locales (TRANSLATIONS.md)
    ├── app_info.json                   # category, ads, audience, URLs, package_name (Назва пакета)
    ├── privacy.json                    # Data Safety + Apple Privacy Labels
    ├── content_rating.json             # IARC + Apple age rating
    ├── iaps.json                       # IAP catalog (must match MainActivity)
    └── review_notes.json               # notes for store reviewers
```

JSON schemas for `app_info.json`, `privacy.json`, `content_rating.json`,
`iaps.json`, `review_notes.json` are documented in `SHIP_GAME.md` Phase 4.
Don't invent fields; copy from a finished app (e.g. WaterSort).

---

## Store requirements (2026)

Detailed limits and field requirements are in `SHIP_GAME.md` Phase 4
(both stores). Highlights to know unprompted:

- Google: 512×512 icon (no alpha), 1024×500 feature graphic, 2-8 phone
  screenshots (1080×2400 recommended), Data Safety mandatory, IARC
  content rating mandatory, privacy policy URL mandatory
- Apple: build SDK iOS 26+ (since Apr 28 2026), 1024×1024 icon,
  6.9" screenshots required (1320×2868), Privacy Nutrition Label
  mandatory, granular age rating since iOS 26
- Both: NO "#1", "Best", "Top", "Award winning", "Download now",
  "Install now", "% off" in copy or screenshots
- Org accounts on Google Play are EXEMPT from the 12-testers /
  14-day closed-testing rule. Promote directly to production.

---

## IAP correctness invariants

Every app on Play has its IAP purchase flow validated against these
four invariants before any AAB is built. Violating any invariant
means released users tap Buy and get nothing while Google still
charges them. `pre_publish_check.py check_iap_invariants` enforces
all four; `scripts/check_iap_invariants.py --all` runs them
standalone.

**Invariant 1** — `VALID_PRODUCTS` in `MainActivity.java` MUST equal
the full set of SKU ids in `iaps.json`. `launchBillingFlow` checks
this set; an unlisted SKU is rejected before Play even opens the
purchase sheet. Source-of-truth flow: `iaps.json` → `VALID_PRODUCTS`
(generate from json, never hand-curate).

**Invariant 2** — Every PURCHASED purchase MUST be acknowledged
within 3 days. Consumable SKUs via `consumeAsync`, non-consumable
and subscription SKUs via `acknowledgePurchase`. Unacknowledged
purchases are auto-refunded by Play. The `CONSUMABLE_PRODUCTS` set
in `MainActivity.java` declares which path each SKU takes; both
`consumeAsync` and `acknowledgePurchase` MUST be wired in
`handlePurchase`.

**Invariant 3** — `game.html` MUST define `window.onPurchaseSuccess`
(directly or as alias to `onPurchaseComplete`). Java's bridge calls
`window.onPurchaseSuccess(id)`; if undefined every purchase silently
drops. The historical bug class (Nonogram + Puzzle2048 +
~140 long-tail apps): only `onPurchaseComplete` was defined; the
retention-features hook then chained to `_origPurchase =
window.onPurchaseSuccess` which was undefined; result was every
non-`season_pass` SKU dropped on the floor while Google charged for
it. The grant function must NEVER throw — a thrown exception in
the bridge looks identical to a failed purchase to the user.

**Invariant 4** — Unhandled SKUs (purchase succeeded but the
matching mechanic isn't in `game.html`, e.g. a utility app that
inherited the canonical IAP catalog without implementing lives or
hints) MUST fall through to a `window.iapDeferGrant(id)` that writes
to `localStorage.pendingGrants`, with `window.replayPendingGrants()`
called on each game load to drain the queue. This way a SKU bought
before its mechanic existed is replayed once the mechanic is added,
rather than being dropped forever.

**Catalog rule with teeth:** SKUs are hidden from the shop UI per
archetype (`archetype.json`). Catalog (`iaps.json`) is NEVER
filtered — restore-purchase must work for existing buyers across all
SKUs even on archetypes that no longer expose those SKUs in the
shop UI.

**Future apps** — `SHIP_GAME.md` Phase 1 records the archetype.
Phase 2 generates `VALID_PRODUCTS` directly from `iaps.json` (never
hard-codes it). Phase 2 also injects the canonical
`onPurchaseSuccess` alias + `replayPendingGrants` safety net into
`game.html`. `pre_publish_check.py check_iap_invariants` re-asserts
all four during Phase 5 and fails the build on any blocker.

---

## Retention-feature parity invariant

Every game that ships the retention stack (i.e. sells
`season_pass_monthly`) MUST have, in `game.html`:

- `window.replayPendingGrants` on init (IAP invariant 4)
- a wrapped `window.onPurchaseSuccess` that delegates to the original
  `onPurchaseComplete`/switch handler (which grants every known SKU
  fully) and defers unknown SKUs to `pendingGrants`
- an `isSeasonActive()` / `hasActiveSeasonPass()` helper and an
  `isPremium()` / `isWeeklyActive()` helper, with `adsRemoved()` =
  `removeAds || isPremium()` gating every ad-show path
- a hint counter (`hintCount` / `hintPack`) if `hint_pack` is sold; an
  `undoPack` counter if `undo_pack` is sold — and the decrement is
  skipped while a pass is active
- `starter_pack`, `season_pass_monthly`, `weekly_pass` handlers that
  grant their full advertised bundle (not a partial one)
- a Free Coins menu surface (rewarded ad, 25 coins / 4 h cooldown)
- a Continue button when last-progress exists
- a theme progress strip on the menu + a theme-unlock celebration card
  with a 6-chip palette preview
- a 7-day login-streak reward ladder (replaces any simpler streak UI)
- a starter-pack-on-first-launch popup
- Restore Purchases + Privacy Policy links in Settings (and
  `MainActivity.java` must expose `@JavascriptInterface restorePurchases()`
  and `openUrl(String)`)

These are usually **injected at runtime** by an "audit addendum"
`<script>` block at the bottom of `game.html`, not added to the static
menu HTML — because the static menu is capped at 6 tappable elements
(`check_menu_button_count`). `pre_publish_check.py check_retention_features`
+ `check_menu_completeness` enforce this for any season-pass game.

## Subscription/bundle promise parity

Every benefit promised in an IAP description needs a corresponding code
flag. `season_pass_monthly` listing "ad-free + 50 daily coins + all
themes + unlimited hints" requires four honored flags
(`adsRemoved()`, `lastSeasonGrantDate` daily-grant, `isPremium()`
theme unlock, premium-gated hint decrement). `weekly_pass` at
`$4.99/week` with "+100 daily coins" requires the +100 grant path
(`lastWeeklyGrantDate`). `pre_publish_check.py check_subscription_parity`
enforces. 2048-style games word "unlimited hints" as "unlimited undos".

## Coin tier ladder

Every game that sells any coin pack ships the full four-tier ladder:

| SKU | Price | Coins | Coins/$ |
|---|---|---|---|
| `coins_small`  | $0.99 |  100 | ~101 |
| `coins_medium` | $4.99 |  600 | ~120 |
| `coins_large`  | $2.99 |  500 | ~167 (best value-per-dollar — the anchor) |
| `coins_mega`   | $9.99 | 1400 | ~140 |

A partial ladder is forbidden. `pre_publish_check.py check_coin_tier_ladder`
blocks it. (`lives_5_coins`-style in-game-currency products are not real
SKUs and don't count.)

## Booster catalog by genre

| Genre | Booster set |
|---|---|
| Sort-puzzle (Water Sort etc.) | Color Reveal (hint), Steady Pour (undo), Fresh Start (restart), Extra Tube, Magic Wand |
| Picross (Nonogram etc.)       | Hint, Undo, Reset, Check, Reveal Row, Reveal Cell |
| 2048-like                     | Undo, New Game, Magic Merge, Remove Tile |

The shop SKU catalog and the in-game booster set must match (a sold pack
needs the matching mechanic; a booster button needs a coins-or-ad cost).
`pre_publish_check.py check_booster_catalog` enforces by genre keyword.

## Cross-cutting menu requirements

Every game's main menu surfaces (statically or injected): Continue button
(when applicable) · Play button · Daily Challenge / streak indicator ·
Levels/Shop/Games (or equivalent) row · Missions button with count ·
Stats / High Scores · Free Coins button (rewarded ad, 25 / 4 h) · Weekly
Tournament banner with a synthetic bracket · theme progress strip ·
season-pass active badge when applicable. Static tappable elements still
capped at 6 — push the rest into runtime injection.

## Seasonal events

Every game ships a `SEASONAL_EVENTS` constant covering at least October
(Halloween), December (Winter), February (Spring). On init, if the
current month matches: temporarily unlock the event theme and inject 5
bonus levels with the event palette (leveled games) or grant a 7-day
1.5× multiplier (non-leveled games like 2048). The menu shows an event
banner while active. `pre_publish_check.py check_seasonal_events` enforces.

## Weekly tournament (synthetic bracket)

Every game replaces the old "Weekly: play any 5 levels" banner with a
synthetic-bracket leaderboard: track best-metric-this-week
(best-level for level games, best-score for 2048), map it through a
per-game `WEEKLY_BRACKETS` table (10 / 25 / 50 / 75 % tiers), show
"🏆 This week — <metric> · Top <pct>%", reset Monday 00:00 local, and
award 100 coins for finishing in the top 25 % / 250 for top 10 %,
granted at week rollover the next time the app opens within 7 days.

---

## Red lines — never do these

Any one of these can terminate the developer account.

1. **No two apps with byte-identical `game.html`.** Replace gameplay logic
   immediately after copying `_template/`. `pre_publish_check.py` blocks.
2. **App folder name must match `<title>` tag.** Folder `Metronome/` cannot
   contain `<title>Dice Roller</title>`.
3. **No templated store listing copy across apps.** Each app's title /
   short / subtitle / full descriptions are hand-written. Spam detector
   looks for this.
4. **No reused AdMob IDs, IAP product IDs, or package names** across apps.
   Every app gets its own AdMob app + units + IAP catalog.
5. **No batch-publishing in short windows.** 2-3 unique apps/week is the
   sustained ceiling. Spiking from silence to 5+ in one week trips
   Google's velocity heuristic.
6. **No two apps shipping the same publish window with visually identical
   store assets** — same icon focal element, byte-identical feature
   graphic layout, screenshots that only swap inner gameplay over a
   shared frame. `check_cross_app_asset_similarity` and
   `check_screenshot_template_reuse` enforce.
7. **Don't "de-duplicate" the shared wrapper code** (`MainActivity.java`,
   `NotificationReceiver.java`). It's shared SDK infrastructure (same
   pattern as Voodoo / SayGames / King). Google penalizes content
   similarity, not wrapper similarity.
8. **No committed secrets** (`keystore.properties` with real passwords,
   sensitive `google-services.json`). `.gitignore` them.
9. **No push notifications to Kids apps.** Google Play Families program
   forbids it. See `QUALITY_PLAYBOOK.md` §11.8.
10. **Never publish any of the 33 BLOCKED_APPS placeholder clones** without
    rewriting their `game.html` first. The byte-identical Dice Roller
    `game.html` across 33 folders is the single highest-risk thing in
    this repo. `check_blocked_apps` enforces; never override.

---

## Shipping cadence

**2 genuinely-distinct apps per week from week 1**, ramping to 3+/week if
Claude Code's productivity allows. User upload work is ~30 min/app via
`RELEASE_HANDOFF.md`.

The risk at this pace is NOT velocity — it's *similarity between apps*.
Google's Repetitive Content classifier triggers on:
- Same `game.html` with renamed functions
- Same icon composition with swapped colors
- Same screenshots with swapped frame contents
- Same listing copy with template substitutions
- Same screen flows / state machines

`pre_publish_check.py` blocks any of these automatically. Cadence ceiling
is set by Claude Code's per-app design effort, not an apps-per-week limit.

### What "unique enough" means

All 5 must hold:
1. `game.html` mechanic + state model + level generation genuinely different
2. Icon focal element different (flasks vs blocks vs tiles vs ropes)
3. Feature graphic layout different (not template with swapped content)
4. Screenshot inner content different (frame can be shared, gameplay can't)
5. Listing copy hand-written for THIS app

### What's NOT capacity-limited (don't try to vary these)

- Wrapper code (`MainActivity.java`) identical across apps — standard
- Same monetization stack (AdMob + IAP + Firebase)
- Same brand colors / fonts / footer text in marketing frames
- Same wrapper SDKs and versions

### Anti-suspension safeguards (mandatory at scale)

1. **One app per genre cluster per 7-day window.** Don't ship two
   ball-sort variants in the same week. Diversify across clusters.
2. **Crash rate <1%, ANR <0.5%** on every shipped app (check Play Console
   weekly). One crash spike at 50+ portfolio = account-level review.
3. **Never publish from `BLOCKED_APPS`** (the 33 Dice Roller clones).
4. **Listing copy variety in opening line.** Don't open every app's
   `full_description.txt` with "Welcome to {AppName}!" — Google detects
   template-fill patterns.
5. **Cross-promotion ("More Games" panel)** is GOOD signal — Google sees
   coherent publisher activity, not spam. Required from app #2 onward.
6. **Stagger AdMob app creation:** max 2/day, 5/week. Creating 5 in one
   day flags AdMob's anti-fraud system separately from Play Console.
7. **Reset icon palette pool every 10 apps.** Portfolio has ~20 distinct
   vivid hues; after 30 apps you start hitting perceptual hash collisions
   even with different focal elements. Use textured/patterned backgrounds
   to break hashes.

### Sustaining 100+ apps

- Run `pre_publish_check.py` against the FULL portfolio weekly (N²
  pairwise comparisons; new app distinct from latest may collide with #18)
- Diversify genres: ~⅓ puzzle, ~⅓ casual/hyper-casual, ~⅓ utility/tracker
- Watch crash rate weekly across the entire portfolio

The fix for any check blocking at the 60th app is *fix that app's
distinctness*, not bypass the check.

---

## Required checks before any publish

Run `pre_publish_check.py <app>` and confirm zero blocking. The script
covers all of: duplicate `game.html`, BLOCKED_APPS membership, folder/
title match, unique package + AdMob + IAP IDs, icon perceptual similarity,
feature graphic + screenshot uniqueness, listing copy uniqueness, all
required asset files present (icon 512, feature 1024×500, icon 1024,
≥2 phone screenshots), all metadata files valid, canonical URLs match,
no stale per-app `privacy-policy.html`, no `pegasusgames.example` /
`@outlook.com` placeholders, no `ENTER_*` placeholders, no prohibited
language, AdMob ID matches manifest+MainActivity, every `iaps.json`
entry has a canonical `description` (≤200 chars, from `IAP_CATALOG.md`),
archetype presence
(four archetypes set in `app_themes.py` + `metadata/app_identity.md`
present), translations present (all 13 locales), menu button count ≤6.

If any blocker fails, stop. Do not build, do not upload, do not advance
to the next app.

---

## State of the apps (last audit)

- **Hero app (1):** **WaterSort** is the official hero. All 5 flagships
  ship to flagship quality, but the hero app gets meta-loop, live ops,
  real mascot, and any other "above-baseline" investment. See
  `docs/COMPETITIVE_BENCHMARK.md` §10 for the rationale.
- **Finished and release-ready (5):** WaterSort, Nonogram, PipeConnect,
  Puzzle2048, UnblockPuzzle. Game code done; metadata folders need full
  population.
- **Already shipped to Play Store (1):** WaterSort.
- **Recently deleted:** BallSortPuzzle (Apr 30 2026 — too similar to
  WaterSort, ~zero downloads). Removed from `app_themes.py`,
  `dedup_similar_apps.py`, `promo.json`, CLAUDE.md state. **NOTE: as of
  May 2026 audit the BallSortPuzzle/ folder still exists in the repo
  working tree — run `cleanup_repo.py` to move it out.**
- **Unique but thin (~150):** `game.html` matches folder name but
  5-20KB. Needs game logic expansion + full metadata.
- **Placeholder clones — DO NOT PUBLISH (33):** DiceRoller, EmotionFlash,
  FindDifference, FlashlightSOS, FruitMerge, GuitarChords, HiddenObject,
  JigsawPuzzle, MahjongSolitaire, MemoryCard, Metronome, MovieTrivia,
  MultiplicationGame, MusicTheory, NumberMemory, PasswordGen,
  PatternSequence, PianoKeyboard, PinPull, QRCodeGen, RandomName,
  RandomNumber, RandomRecipe, ScienceQuiz, ScrewPuzzle, SlidingTiles,
  SolarSystem, SportsQuiz, Sumplete, TripleMatch, UkuleleChords,
  WordScramble, WordSearch. Blocked from release until `game.html`
  is genuinely rewritten. **NOTE: as of May 2026 audit all 33 still
  exist in the repo — run `cleanup_repo.py` to move them out.** Even
  with `BLOCKED_APPS` enforcement in `pre_publish_check.py`, having
  byte-identical Dice Roller `game.html` across 33 folders sitting in
  the working tree is one accidental override away from account
  termination.

---

## Workflows

### Finishing a thin app or new app

The primary workflow is `SHIP_GAME.md` Phases 1-8. Always start there.
Don't reimplement steps inline; the playbook is authoritative.

### Modifying the shared wrapper

1. Make change in one app first, test it
2. Write a migration script (see `fix_all_apps.py` pattern) for all apps
3. Preserve per-app values: package name, AdMob IDs, IAP IDs, theme colors
4. `--dry-run` flag with diff output before writing
5. Bump `versionCode` of all affected apps

### Mass-change scripts

- Define `BASE` constant pointing at repo root
- Iterate only over real app dirs (skip `_template`, `_release`,
  `__pycache__`, hidden)
- Preserve per-app unique values (`applicationId`, AdMob IDs, IAP IDs,
  package statements, `WEBVIEW_BG_COLOR`, icons, store assets, metadata)
- Print intent before doing; add `--dry-run` for non-trivial changes
- Match `fix_all_apps.py` / `prepare_for_publish.py` style

---

## Honest-gap handling: do not ship with known defects

Pattern to avoid: complete most of the work, list 2-3 "honestly surfaced
known gaps" at the end, hand off the build anyway. The user reads the
list, doesn't fix everything, ships with the gaps. Issues compound.

**Honest gaps are NOT a substitute for fixing them.** If during a
SHIP_GAME run you discover any of:

- Sparse / empty screenshot board / wasted canvas
- Headline doesn't match game capability
- Phase 8.3 functional smoke test wasn't run
- A button or screen path was not verified
- A required check was skipped because "the script doesn't support it"
- Any "verify before shipping" or "next-iteration polish" text

…STOP. Surface the specific defect with concrete options
("Three options: A fix headline / B extend generator / C remove claim —
which?"). Wait for the user. Do NOT write a "Known gaps" section and
proceed.

The "surfaced honestly" framing looks honest but operationally ships
the defect. Don't.

---

## Things to flag to the user

If you see any of these, stop and surface:

- A flagship app being declared "ready" without a meta-loop (theme
  collection, achievements, or world restoration). Per
  `COMPETITIVE_BENCHMARK.md` §3, no successful analog ships without
  one. Lowest-effort meta-loop is theme collection (~1 day work).
- A flagship app's `full_description.txt` opening with a description
  ("Pour and sort colored water") rather than a hook ("Welcome to
  Water Sort, the most relaxing pour-sort puzzle on Google Play").
  Per `COMPETITIVE_BENCHMARK.md` §1, the leader-format opening is
  required for every flagship.
- A puzzle/sort game listing missing the words "relaxing" /
  "satisfying" / "ASMR" / "offline" when the app actually has those
  qualities. Per `COMPETITIVE_BENCHMARK.md` §2, these are the keywords
  that drive ASO in casual puzzle. Use them when true.
- The hero app (currently WaterSort) being treated identically to
  other flagships in any sprint planning. Hero gets disproportionate
  investment — that's the point. See `COMPETITIVE_BENCHMARK.md` §9.
- Two apps with duplicate `game.html`
- An app on `BLOCKED_APPS` whose `game.html` hasn't been rewritten
- App folder name ≠ `<title>` tag
- Shared AdMob IDs across apps
- Icons visually near-identical (same focal element, swapped colors)
- Two apps in same genre cluster shipping within 7 days
- Auto-generated listings via template substitution
- `game.html` under ~8KB planned for publishing
- Reused screenshots across multiple apps
- **Shop / "More Games" / settings screens used as screenshots.**
  Every screenshot slot must show ACTUAL GAMEPLAY at a varied level
  — different board layouts, different progress states, different
  game phases. Capturing the shop or "More Games" panel is a
  wasted slot (Play Store users see "this app is mostly a paywall
  and a list of other apps" instead of "this is a fun puzzle") and
  is auto-blocked from May 2026. Use diverse level captures
  instead — e.g. an early-game level, a mid-game level, a late-game
  board, the daily challenge active, a streak banner state.
  This rule applies retroactively: WaterSort, Nonogram, and
  Puzzle2048 had slots showing shop / more-games and have been
  regenerated. No more grandfathering of those three.
- Phone, tablet 7", and tablet 10" listings reusing the same raw
  page, the same wrapper, or the same headline copy. **Each of the
  three surfaces must be a fully distinct listing**, AND every
  individual wrapped screenshot within each surface must have a
  unique raw + unique headline + visually distinct wrapper variant
  from every other slot in that surface. Varying ALL of:
    1. **Game pages captured** — different in-app screens (menu vs.
       active board vs. shop vs. results vs. daily challenge etc.),
       no overlap of which screen appears in two surfaces
    2. **Levels / boards shown** — even when the same screen type is
       captured, the level number / board layout / progress state must
       differ (don't ship "level 3 mid-pour" three times at three
       resolutions)
    3. **Wrapper variant** — different layout, headline placement,
       gradient direction, accent treatment (not one frame with
       different raws inside)
    4. **Headlines and subtext** — each surface gets its own headline
       set: phone reads from `metadata/screenshot_headlines.json`,
       tablets read from `metadata/screenshot_headlines_tablet_7.json`
       and `metadata/screenshot_headlines_tablet_10.json` (already
       supported by `wrap_tablet_screenshots.py` — it falls back to
       phone copy when the per-target files are missing, which is
       the failure mode to avoid). Different `line1` / `line2` /
       `subtitle` per slot; not just retitled phone headlines
  Tablet listings exist to tell a different story than phone, and
  Google's quality classifier flags portfolios that ship the same
  marketing frame three times. Applies to all NEW apps from this point
  on. The three already-shipped apps (WaterSort, Nonogram, Puzzle2048)
  are grandfathered — don't retroactively rework them. See
  `SHIP_GAME.md` Phase 3.6 for raw-slot allocation, wrapper variant
  selection, and per-target headline file authoring
- Any temptation to use Puppeteer / headless Chromium for screenshots
  — emulator-only per `QUALITY_PLAYBOOK.md` §7.0 and `SHIP_GAME.md` §3.6.
  If `capture_screenshots.py` can't run because no AVD, surface as
  hard blocker; do NOT write a Puppeteer fallback
- `keystore.properties` committed with real passwords
- Per-app `store/privacy-policy.html` (delete on sight)
- Privacy / support URL not matching canonical values
- `iaps.json` not matching MainActivity IAP IDs
- `iaps.json` entry missing `description`, exceeding 200 chars, or
  drifting from `docs/IAP_CATALOG.md` canonical text. Play Console
  requires a description on every IAP (≤200 chars). `init_app_metadata.py`
  scaffolds canonical descriptions; `pre_publish_check.py
  check_iaps_descriptions` enforces. Source of truth is `IAP_CATALOG.md`
- `content_rating.json` with `gambling_mechanics` set on a kids app
- "Just ship the placeholder app, I'll fix it later" — refuse
- Crash rate >1% or ANR >0.5% on any shipped app
- App designed without picking 4 archetypes from `APP_ARCHETYPES.md`
- Archetype combination A+M0+V1+T1 (the template — refuse without
  varying ≥2 of 4)
- Layout A used by >30% of shipped apps
- Texture T1 used by >40% of shipped apps after month 6
- `metadata/app_identity.md` missing or empty at Phase 5
- Missing any of the 13 locale folders in `metadata/` (note: Indonesian
  is `id`, Ukrainian is `uk` — Play Console codes, not `id-ID`/`uk-UA`)
- Title translated to non-English (must stay English globally)
- Any `*.rejected` translation file (failed validation; edit and rename)
- Kids app translated files still containing the
  "# KIDS APP — REVIEW BY NATIVE SPEAKER" header
- Request to add Russian (`ru-RU`) to a single app — excluded
  portfolio-wide; either change policy in TRANSLATIONS.md or skip
- In-game `i18n/<lang>.json` keys diverging from `en.json` — runtime
  fallback to English mid-screen looks broken

---

## House style for generated code

- **Python**: stdlib only unless asked; docstring header; `BASE`
  constant; match `fix_all_apps.py` patterns
- **Java**: 4-space indent, grouped imports with section comments,
  match existing `MainActivity.java`
- **HTML/CSS/JS in `game.html`**: single file; inline `<style>` and
  `<script>`; CSS custom properties for theme at top
  (`:root { --bg: ...; }`); no external CDN deps
- **JSON**: 2-space indent, trailing newline, UTF-8, no comments
- **Text metadata**: plain UTF-8, trim trailing whitespace, single
  trailing newline, no BOM

---

## One honest note on scope

User's long-term goal is finishing all ~200 apps to flagship quality.
That's ~1 app/week sustainably = 4 years for 200 apps. When asked to
"finish all of them," help with one at a time at the flagship bar
rather than racing to ship thin versions of many. The publisher with
30 polished apps out-earns the publisher with 200 thin ones, at a
fraction of the policy risk.
