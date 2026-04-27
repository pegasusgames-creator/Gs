# Pegasus Games — Claude Code Instructions

This repo is a portfolio of ~200 Android apps/games sharing a common wrapper.
Before doing anything in here, read this file end to end.

## Companion files

- **`docs/SHIP_GAME.md`** — **MASTER RELEASE WORKFLOW.** When the user says
  "ship X" / "release X" / "prepare X for release" / equivalent in any
  language, **read this file end to end and execute it without asking
  clarifying questions** unless a hard blocker is hit (see
  `docs/SHIP_GAME.md` "Hard blockers"). Defines all 8 phases from initial
  game logic through signed AAB output and per-app `RELEASE_HANDOFF.md`
  generation. Authoritative spec for what "ready for release" means.
- **`docs/QUALITY_PLAYBOOK.md`** — Design, UX, gameplay, and monetization
  guidance for every app. **Read this whenever working on any app's
  visuals, gameplay, menu, onboarding, or monetization.** It covers
  color palettes, fonts, first-60-seconds onboarding, menu hierarchy,
  progression systems, ad placement rules, time-limited starter packs,
  store listing patterns, notifications, and per-app-type rules (games
  vs. tools vs. trackers vs. kids apps). Applies to all ~200 apps.
- **`docs/NOTIFICATIONS_IMPL.md`** — Reference Java + JS code for
  local-notification implementation per `docs/QUALITY_PLAYBOOK.md` §11.
  Read when adding or modifying notifications on any app.
- **`docs/LEVEL_DESIGN.md`** — **MANDATORY for any app with procedural
  levels.** Pure random shuffles do NOT produce solvable puzzles
  (WaterSort v1.6.2 shipped with 295 / 500 unsolvable levels). Use
  reverse-construction from the solved state and verify with a BFS
  solver before every release. Per-puzzle-type guidance for ball-sort,
  sliding-tile, sokoban, unblock, pipe-connect, nonogram.
- **`scripts/verify_watersort_levels.py`** — Reference solvability verifier
  for ball-sort-style puzzles. Run before every WaterSort release;
  copy and adapt for other puzzle apps (replicate the JS RNG, mirror
  the win/move rules, run BFS).
- **`docs/IAP_CATALOG.md`** — **MANDATORY for any Play Console IAP
  submission.** Single source of truth for IAP titles, descriptions,
  prices, types (Consumable/Non-consumable), Play Console form fields,
  and per-app product subsets. Every flagship app's IAPs come from
  this catalog. Avoids re-deriving 200-char descriptions every release.
- **`scripts/pre_publish_check.py`** — Pre-build verification script (run
  automatically by `scripts/build_release.py`).
- **`scripts/build_release.py`** — Automates Phase 5/7/8 of `docs/SHIP_GAME.md`:
  pre-publish checks → `gradlew bundleRelease` → AAB verification.
  Use: `python3 scripts/build_release.py <AppName>`.
- **`scripts/gen_handoff.py`** — Generates per-app `RELEASE_HANDOFF.md` (the
  20–30 min checklist for AdMob/Play Console/IAP setup that the human
  follows). Use: `python3 scripts/gen_handoff.py <AppName>`.
- **`scripts/init_app_metadata.py`** — Scaffolds the metadata/store folders for
  a new app.

---

## Canonical contact info and URLs (use these everywhere)

These values are shared across **all apps** in the portfolio. Hard-code them
into every `metadata/app_info.json`, `metadata/privacy.json`, and Play Console /
App Store Connect listing. **Do not invent per-app URLs or contact emails.**

| Field | Value |
|---|---|
| **Developer name** | `Pegasus Games` |
| **Developer email (public)** | `pegasusgames@atomicmail.io` |
| **Privacy Policy URL** (general apps) | `https://pegasusgames-creator.github.io/privacy.html` |
| **Privacy Policy URL** (kids apps) | `https://pegasusgames-creator.github.io/privacy-kids.html` *(when created)* |
| **Support URL** | `https://pegasusgames-creator.github.io/` |
| **Marketing URL** | `https://pegasusgames-creator.github.io/` |
| **Copyright** | `© 2026 Pegasus Games` |

**Notes:**

- The Support URL is the homepage with a Contact section. There is no
  dedicated `/support` page. Google's Support URL field accepts any URL where
  users can find a contact email — the homepage qualifies.
- The Privacy Policy URL must include the `.html` extension. `…/privacy/` will
  404. The file lives at `pegasusgames-creator.github.io/privacy.html`.
- The privacy policy is a single shared document covering all general-audience
  apps in the portfolio (Voodoo / SayGames / King all use this pattern). When a
  Kids-targeted app ships (per Google Play Families program), use the separate
  `privacy-kids.html` URL with COPPA-compliant language — do not mix kids
  apps under the general policy.

**Per-app `store/privacy-policy.html` files SHOULD NOT exist.** The shared
URL on GitHub Pages is the single source of truth. If `scripts/init_app_metadata.py`
or any past script created a per-app HTML privacy policy, delete it. Stale
per-app copies create mismatches with what's declared in Play Console — a
real legal liability if the two disagree, and a Data Safety policy violation
risk.

**Per-app Data Safety / Privacy Nutrition Label answers ARE per-app.** The
shared privacy policy is a superset; each app's Play Console Data Safety form
must accurately reflect what THAT app actually does. Don't assume "shared
privacy policy = shared Data Safety form" — it does not.

---

## What this repo is

Each top-level folder (except `_template/`, `_release/`, and the `*.py` scripts)
is a single Android app. An app is an HTML5 game/utility (`game.html`) loaded
inside a thin native WebView wrapper (`MainActivity.java`). iOS scaffolding
exists in parallel.

The wrapper is intentionally shared across all apps. It handles:

- WebView setup and JS bridge (`NativeBridge`)
- AppLovin MAX + AdMob dual-fallback ad loading
- Google Play Billing v8 (IAPs: `remove_ads`, coin packs, lives, hint packs, starter pack, `season_pass_monthly` subscription)
- Firebase Analytics
- In-App Review prompt
- Daily notifications (`NotificationHelper` + `NotificationReceiver`)

---

## Per-app required folder structure

Every app must have this exact structure before it can be published. The
`scripts/pre_publish_check.py` script enforces it.

```
<AppName>/
├── android/                            # existing — the Android project
├── ios/                                # existing — the iOS scaffolding
├── store/
│   ├── icon_512_playstore.png          # Google: 512x512 PNG, no alpha, no rounded corners
│   ├── feature_graphic_1024x500.png    # Google: 1024x500 PNG, no transparency
│   ├── icon_1024_appstore.png          # Apple: 1024x1024 PNG, no alpha, no transparency
│   └── screenshots/
│       ├── phone/                      # Required: 2-8 portrait PNGs (1080x1920 or 1080x2400 recommended)
│       │   ├── 01_menu.png
│       │   ├── 02_gameplay.png
│       │   └── 03_progression.png
│       ├── tablet_7/                   # Optional: 7" tablet (1200x1920) — adds "Designed for tablet" badge
│       ├── tablet_10/                  # Optional: 10" tablet (1800x2560)
│       └── iphone_6_9/                 # Apple required: 6.9" iPhone (1320x2868), at least 1
│
└── metadata/
    ├── en-US/                          # Default locale — always required
    │   ├── title.txt                   # ≤30 chars (both stores)
    │   ├── short_description.txt       # ≤80 chars (Google only)
    │   ├── subtitle.txt                # ≤30 chars (Apple only)
    │   ├── full_description.txt        # ≤4000 chars (both stores)
    │   ├── keywords.txt                # ≤100 chars, comma-separated (Apple only)
    │   ├── promotional_text.txt        # ≤170 chars (Apple only, editable without new version)
    │   └── release_notes.txt           # ≤500 chars, what's new in the current version
    ├── <other-locales>/                # Optional — same file set per language (e.g. "es-ES/", "de-DE/", "fr-FR/")
    ├── app_info.json                   # Category, ads declaration, target audience, URLs
    ├── privacy.json                    # Privacy policy URL, Google Data Safety answers, Apple Privacy Labels
    ├── content_rating.json             # IARC questionnaire answers, Apple age rating
    ├── iaps.json                       # IAP product catalog (must match MainActivity.java)
    └── review_notes.json               # Notes for Google/Apple reviewers, demo account if needed
```

### JSON schemas (what each `.json` file must contain)

**`app_info.json`:**
```json
{
  "category_google": "GAME_PUZZLE",
  "category_apple_primary": "GAMES",
  "category_apple_subcategory": "PUZZLE",
  "contains_ads": true,
  "contains_iap": true,
  "target_audience_min_age": 13,
  "support_url": "https://pegasusgames.example/support",
  "marketing_url": "https://pegasusgames.example/ballsortpuzzle",
  "copyright": "© 2026 Pegasus Games"
}
```

**`privacy.json`:**
```json
{
  "privacy_policy_url": "https://pegasusgames.example/privacy/ballsortpuzzle",
  "google_data_safety": {
    "data_collected": ["device_ids", "app_interactions", "crash_logs"],
    "data_shared": ["advertising_id"],
    "encrypted_in_transit": true,
    "user_can_request_deletion": true
  },
  "apple_privacy_labels": {
    "data_used_to_track_you": ["device_id", "advertising_data"],
    "data_linked_to_you": [],
    "data_not_linked_to_you": ["crash_data", "performance_data", "product_interaction"]
  }
}
```

**`content_rating.json`:**
```json
{
  "iarc_answers": {
    "violence": "none",
    "sexual_content": "none",
    "profanity": "none",
    "drugs_alcohol": "none",
    "gambling_mechanics": "none",
    "user_generated_content": false,
    "shares_user_location": false,
    "allows_user_interaction": false,
    "digital_purchases": true
  },
  "expected_google_rating": "Everyone",
  "apple_age_rating": "4+"
}
```

**`iaps.json`:**
```json
{
  "one_time_products": [
    {"id": "remove_ads",         "title": "Remove Ads",       "price_usd": 2.99},
    {"id": "coins_small",        "title": "100 Coins",         "price_usd": 0.99},
    {"id": "coins_large",        "title": "500 Coins",         "price_usd": 2.99},
    {"id": "five_lives",         "title": "5 Lives",           "price_usd": 0.99},
    {"id": "unlimited_lives_1h", "title": "1hr Unlimited",     "price_usd": 0.99},
    {"id": "hint_pack",          "title": "Hint Pack",         "price_usd": 1.99},
    {"id": "starter_pack",       "title": "Starter Pack",      "price_usd": 0.99}
  ],
  "subscriptions": [
    {"id": "season_pass_monthly", "title": "Season Pass",
     "price_usd": 1.99, "billing_period": "P1M", "grace_period_days": 3}
  ]
}
```

**`review_notes.json`:**
```json
{
  "google_review_notes": "No login required. All features accessible from main menu.",
  "apple_review_notes": "No login required. To test IAPs, use the Remove Ads button on the main menu.",
  "demo_account_required": false,
  "demo_username": "",
  "demo_password": "",
  "uses_third_party_content": false
}
```

---

## Store requirements reference (2026)

### Google Play

- **Account**: new personal accounts created after Nov 13, 2023 must run a closed test with **≥12 opted-in testers for 14 consecutive days** before production access. Organization accounts are exempt.
- **Title**: ≤30 chars
- **Short description**: ≤80 chars
- **Full description**: ≤4000 chars
- **App icon**: 512×512 PNG, no alpha, no rounded corners
- **Feature graphic**: 1024×500 PNG, no transparency
- **Phone screenshots**: 2–8, aspect ratio 16:9–9:16, min side 320px, max side 3840px, JPEG or 24-bit PNG no alpha. Recommended 1080×1920 or 1080×2400.
- **Tablet screenshots**: optional (7" and 10" each)
- **Promo video**: optional YouTube URL, 30s–1m recommended
- **Privacy policy URL**: required for all apps
- **Data Safety form**: mandatory — must match privacy policy
- **Content rating**: IARC questionnaire mandatory
- **Target audience**: required
- **Ads declaration**: required (yes/no)
- **Category**: required
- **Pricing & countries**: required
- **No prohibited language** in screenshots or description: no "#1", "Best", "Top", "Award winning", "Download now", "Install now", price/discount claims

### Apple App Store (iOS 26 SDK required from April 28, 2026)

- **Build SDK**: iOS 26 SDK or later
- **App name**: ≤30 chars
- **Subtitle**: ≤30 chars
- **Description**: ≤4000 chars
- **Keywords**: ≤100 chars, comma-separated (do NOT repeat the app name or category)
- **Promotional text**: ≤170 chars (can be updated without new version)
- **App icon**: 1024×1024 PNG, no alpha, no transparency
- **iPhone screenshots**: 1–10 per device size. Required: **6.9" (1320×2868)**. Optional: 6.5" (1284×2778 or 1242×2688). Smaller sizes auto-scaled.
- **iPad screenshots**: required if app supports iPad: **13" (2064×2752)**
- **App previews (videos)**: optional, up to 3 per device, 15–30s, ≤500MB, MOV/M4V/MP4
- **Privacy Nutrition Label**: required — declare all data your app + third-party SDKs collect
- **Age rating**: required (granular system since iOS 26)
- **Support URL**: required
- **Privacy policy URL**: required
- **Review notes**: required (explain non-obvious functionality)
- **Demo account**: required if app has login
- **Categories**: primary required, secondary optional

### Both stores — what NOT to include

- Screenshots with "Download now" / "Install now" CTAs
- Ranking claims ("#1", "Best", "Top")
- Price/promotion claims ("50% off", "Free for today")
- Images suggesting partnership with another brand
- Real user data (names, phone numbers) in screenshots
- Copyrighted characters or IP
- Misleading functionality claims

---

## Red lines — never do these

These are not style preferences. Violating any one of these can get the whole
developer account terminated. Google's automated review hashes assets across
the portfolio.

1. **Never let two apps have byte-identical `game.html` files.**
   If you are copying a template to start a new app, the very next step is to
   replace its gameplay logic so the hash differs. Run `scripts/pre_publish_check.py`
   before every commit that touches `game.html`.

2. **Never let an app's folder name disagree with its `<title>` tag.**
   Folder `Metronome/` must contain a metronome. If `game.html` says
   `<title>Dice Roller</title>` inside the Metronome folder, that's a disaster.

3. **Never template store listing copy across apps.**
   Each app's `title.txt`, `short_description.txt`, `subtitle.txt`, and
   `full_description.txt` must be genuinely unique — not a find-and-replace
   template. Google's spam detector looks for this specifically. The guard
   script detects cross-app text duplication.

4. **Never reuse AdMob unit IDs, AdMob app IDs, IAP product IDs, or package names across apps.**
   Every app has its own AdMob app + ad units and its own IAP catalog.

5. **Never batch-publish many apps in a short window.**
   Sustained 2–3 unique apps per week is the realistic ceiling for this
   portfolio (org account, Claude-Code-assisted production). Spiking from
   silence to 5+ apps in a single week — especially in months 1–3 — trips
   Google's velocity-spike heuristics. Steady, predictable cadence is safer
   than bursts. See **"Shipping cadence"** section below for the actual
   schedule and why it works. NOTE: organization accounts on Google Play
   are exempt from the 12-testers / 14-day closed-testing requirement that
   applies to personal accounts created after Nov 2023, so apps can be
   promoted directly to production.

6. **Never let two apps in the same publish window have visually
   indistinguishable store assets.**
   Beyond `game.html` byte-identity (red line #1), Google's image
   classifier compares icons, feature graphics, and screenshot composition
   across the developer account. Risk patterns to avoid:
   - Two apps shipping with the same icon focal element (e.g. "vibrant
     flask icon" — that's WaterSort's, no other app gets it).
   - Multiple apps with feature graphics whose layout is byte-identical
     (same gradient direction, same text position, same flask/tile
     arrangement).
   - Screenshot frames identical across apps with only the inner
     gameplay swapped. Frames CAN be consistent (it's brand identity),
     but the inner gameplay screenshot must be visually distinct per app
     — different colors, different layout, different content density.
   The `scripts/pre_publish_check.py` `check_cross_app_asset_similarity` and
   `check_screenshot_template_reuse` rules detect this.

7. **Never remove the shared wrapper code claiming it is duplicate.**
   The identical 543-line `MainActivity.java` across the flagship games is
   shared SDK infrastructure — same pattern used by Voodoo, SayGames, King.
   Do not "de-duplicate" it. Google's spam classifier penalizes
   *content* similarity (game.html, listings, assets), not *wrapper*
   similarity.

8. **Never commit secrets** (`keystore.properties` with real passwords,
   `google-services.json` if it contains sensitive keys). These belong in
   `.gitignore`.

9. **Never send push notifications to Kids apps.** Apps under the Google Play
   Families program are forbidden from sending notifications to children. See
   `docs/QUALITY_PLAYBOOK.md` §11.8. For general-audience apps, follow the
   notification rules in `docs/QUALITY_PLAYBOOK.md` §11 (no morning sends, no more
   than 1/day, no emotional manipulation, permission requested only after
   positive first-session moment).

10. **Never publish any of the 33 placeholder Dice Roller clones** (see
    "State of the apps → Placeholder clones" below) without first replacing
    their `game.html` with genuinely distinct gameplay logic. Their byte-
    identical `game.html` is the highest-risk single thing in this repo —
    publishing even 2 of them would cause cascading suspension across the
    portfolio. The `check_duplicate_game_html` rule blocks this, but rule
    bypasses or `--allow` flags must never be used to override it.

---

## Shipping cadence

Publishing pace matters. Wrong pace = suspension. Right pace = sustained
revenue growth. The reasoning below is empirical (based on observed
publisher patterns), not from official Google policy — Google's published
rules on this are deliberately vague.

### Target cadence by phase

| Phase | Window | Rate | Why |
|---|---|---|---|
| Phase 1 — Establishing reputation | Months 1–2 (now through end of June) | 1 unique app / week | New org account. Each new app is reviewed strictly. Gives time to QA each one and react to any flags. |
| Phase 2 — Sustained production | Months 3–4 (July, August) | 2 unique apps / week | Account has track record. Asset pipeline is automated (icon gen, screenshot wrap). Quality is sustainable. |
| Phase 3 — Steady state | Months 5+ (September onward) | 2–3 unique apps / week | Ceiling. Beyond this, quality of icons/screenshots/listings starts dropping and becomes the actual constraint. |

### What "unique" means in this context

Google's automated review compares apps within a single developer account
on multiple dimensions. An app counts as "unique" only if all of these
hold true compared to every other app in the portfolio:

1. **`game.html` content is genuinely different** — not a find-and-replace
   variant. Different mechanic, different state model, different
   level/content generation. Catches: `check_duplicate_game_html`.
2. **Icon focal element is different** — a different primary visual subject
   (flasks vs. blocks vs. tiles vs. ropes). Same artistic style across the
   portfolio is fine; same subject is not.
3. **Feature graphic composition is different** — different layout, not
   just different inner content in the same template.
4. **Screenshot inner content is different** — even if the marketing
   wrapper template is shared (which is fine, it's brand consistency),
   the screenshots inside the frames must show genuinely different
   gameplay.
5. **Store listing copy is hand-written, not template-substituted** —
   each app's `title.txt`, `short_description.txt`, `subtitle.txt`,
   `full_description.txt` must mention features specific to THAT app.

If any of those 5 dimensions are duplicated across two apps, those two
apps don't count as "two unique apps" for cadence purposes — they count
as one app shipped twice, which is what the spam classifier flags.

### Cadence rules of thumb

- **Don't ship multiple apps in the same calendar day.** Even if both are
  unique, same-day spike is a velocity signal. Spread releases over the
  week.
- **Don't ship 2+ apps from the same genre cluster within 7 days.** E.g.,
  don't release two ball-sort variants in the same week. Diversify across
  genres within each week.
- **Don't suddenly accelerate.** Going from 1/week to 5/week in week 6 is
  riskier than going 1, 1, 2, 2, 2, 2 over the same period. The
  classifier looks at velocity *delta*, not just absolute rate.
- **Don't ship anything until WaterSort has been live and crash-free for
  at least 7 days.** Account-level reputation is built one clean release
  at a time. Speed comes after stability is proven.

### What's NOT capacity-limited

- **Wrapper code identity across apps is fine.** All Pegasus Games apps
  share the same `MainActivity.java`. This is normal for publishers and
  not penalized.
- **Same monetization stack across apps is fine.** Same AdMob + IAP +
  Firebase setup is the industry norm.
- **Same brand colors / fonts / footer text across screenshots is fine.**
  Brand consistency is desirable. The thing that's NOT fine is the inner
  gameplay being identical.

### Why this is not "be paranoid, ship slowly"

You CAN ship 2/week sustained from week 5 onward. The corrected pace is
not "go slow." It's "go fast on the things that should be fast (writing
genuinely different game.html, generating distinct icons) and don't
shortcut the things that need to stay distinct."

The mistake-pattern that gets accounts suspended is not "shipping at 2 /
week." It's "shipping 2 / week where each new app's `game.html` is
80% identical to the previous one, with a swapped color theme and
renamed functions." Claude Code can produce that kind of output if the
prompt is lazy. Always feed Claude Code a fresh design intent for each
app, not "make another puzzle game like the last one."

---

## Required checks before any publish

Before suggesting `./gradlew bundleRelease` for any app — and before
suggesting upload to Play Console — Claude Code MUST first run
`pre_publish_check.py <app>` and confirm zero blocking issues. Do not
build or upload if any blocking check fails. The script covers:

- [ ] No duplicate `game.html` hashes across the portfolio
- [ ] App is not on the BLOCKED_APPS placeholder-clones list (or its
      `game.html` has been rewritten and no longer matches Dice Roller)
- [ ] Folder name matches `<title>` and `android:label`
- [ ] Unique package name, AdMob app ID, AdMob unit IDs, IAP product IDs
- [ ] Icons are not byte-identical AND not visually near-identical
      (perceptual aHash distance > 6) across apps
- [ ] Feature graphic and app-store icon are unique across apps
- [ ] Phone screenshots are unique across apps (not just shared wrapper
      template — the gameplay shown inside must differ)
- [ ] Listing copy (title, short_description, subtitle, full_description)
      is unique per app — never template-substituted
- [ ] `store/icon_512_playstore.png` exists (512×512)
- [ ] `store/feature_graphic_1024x500.png` exists (1024×500)
- [ ] `store/icon_1024_appstore.png` exists (1024×1024)
- [ ] `store/screenshots/phone/` contains ≥2 PNG files
- [ ] `metadata/en-US/title.txt` exists, ≤30 chars
- [ ] `metadata/en-US/short_description.txt` exists, ≤80 chars
- [ ] `metadata/en-US/full_description.txt` exists, ≤4000 chars
- [ ] `metadata/en-US/subtitle.txt` exists, ≤30 chars
- [ ] `metadata/en-US/keywords.txt` exists, ≤100 chars
- [ ] `metadata/en-US/release_notes.txt` exists, ≤500 chars
- [ ] `metadata/app_info.json` valid and filled in
- [ ] `metadata/privacy.json` valid, `privacy_policy_url` present
- [ ] `metadata/content_rating.json` valid
- [ ] `metadata/iaps.json` valid (IAP IDs match what's in `MainActivity.java`)
- [ ] `metadata/review_notes.json` valid
- [ ] Canonical privacy/support URLs match the values in this file
- [ ] No stale per-app `store/privacy-policy.html` (canonical lives at the
      shared GitHub Pages URL)
- [ ] No stale placeholder URLs (`pegasusgames.example`, old `@outlook.com`)
- [ ] No unreplaced `ENTER_*` placeholders anywhere in code or manifests
- [ ] Full description and screenshots don't contain prohibited language
      (#1, Best, Top Rated, Download Now, Install Now, % Off, etc.)
- [ ] `AndroidManifest.xml` AdMob App ID matches `MainActivity.java`

If any blocking check fails, stop and report. Do not proceed with the
build, do not suggest uploading, and do not advance to the next app.

The first three blocking checks above are the ones that matter most for
avoiding Repetitive Content suspension. The placeholder-clones blocklist
is enforced even if the developer says "just ship it" — the block lifts
automatically once the app's `game.html` is genuinely rewritten.

---

## State of the apps (as of last audit)

### Finished and release-ready (6)

BallSortPuzzle, WaterSort, Nonogram, PipeConnect, Puzzle2048, UnblockPuzzle.
Game code is done. Still need: full metadata folders populated per the structure above.

### Unique but thin (≈150)

Most other folders have a `game.html` that matches the folder name but is
only 5–20KB. Needs: real game logic expansion AND full metadata folder.

### Placeholder clones — DO NOT PUBLISH (33)

Contain a `game.html` that is actually Dice Roller wearing the wrong name:

  DiceRoller, EmotionFlash, FindDifference, FlashlightSOS, FruitMerge,
  GuitarChords, HiddenObject, JigsawPuzzle, MahjongSolitaire, MemoryCard,
  Metronome, MovieTrivia, MultiplicationGame, MusicTheory, NumberMemory,
  PasswordGen, PatternSequence, PianoKeyboard, PinPull, QRCodeGen,
  RandomName, RandomNumber, RandomRecipe, ScienceQuiz, ScrewPuzzle,
  SlidingTiles, SolarSystem, SportsQuiz, Sumplete, TripleMatch,
  UkuleleChords, WordScramble, WordSearch

Blocked from any release pipeline until their `game.html` is real.

---

## Workflows

### Finishing a placeholder or thin app

**Before writing any code: read `docs/QUALITY_PLAYBOOK.md`.** It defines the bar
every app in the portfolio must hit (vivid color palette, custom font, no
emoji as UI icons, animated tutorial, rewarded-video options on every helpful
moment, time-limited starter pack, "More Games" cross-promotion, etc.). A
"finished" app is one that passes the §13 per-app review checklist in the
playbook — not just one whose core mechanic works.

1. Read `docs/QUALITY_PLAYBOOK.md` in full (if not already done in this session)
2. Read `_template/game.html` for the current base pattern
3. Read a nearby finished game (e.g., `BallSortPuzzle`) for the progression/IAP integration pattern
4. Write the full game logic in `<APP>/android/app/src/main/assets/game.html` — new code, not copy-paste
5. Match the app's folder name to the `<title>` tag
6. Use a distinct color palette (vivid/saturated per playbook §1.1, not pastel)
7. Populate the full `metadata/` and `store/` folders per the structure above (use `scripts/init_app_metadata.py` to scaffold, then fill in)
8. Create AdMob app + ad units in the AdMob console; update unit IDs in `MainActivity.java` and the AdMob app ID in `AndroidManifest.xml`
9. Create IAP products in Play Console (must be Active)
10. Bump `versionCode` in `android/app/build.gradle`
11. Walk through the per-app review checklist in `docs/QUALITY_PLAYBOOK.md` §13
12. Run `scripts/pre_publish_check.py` — must pass all blocking checks

### Writing store listing copy for a new app

- The `title.txt` should be the actual app name, ≤30 chars. No "- Free", "- Best", etc.
- The `short_description.txt` (Google) is the single most important line — it's shown in search results. Focus on the core benefit in ≤80 chars. No CTAs, no ranking claims.
- The `full_description.txt` should be app-specific and benefit-focused. Do not copy another app's description and change the name. Do not stuff keywords. Around 500–1500 chars is the sweet spot for most casual games.
- The `keywords.txt` (Apple) should be comma-separated, no spaces between entries (save characters), and should NOT repeat the app title or category. Apple already indexes those.
- The `subtitle.txt` (Apple) is shown under the title; use it to reinforce the value proposition in different words than the title.

### Generating screenshots

- Source: actual in-app screens captured from a running device or emulator
- Required: menu screen, gameplay screen, and at least one of: shop, level select, achievements, settings
- Dimensions for Google: 1080×1920 or 1080×2400 PNG
- Dimensions for Apple 6.9": 1320×2868 PNG
- Add light marketing text overlays only if they genuinely clarify the screen (e.g. "Unlock 100+ levels")
- Do NOT use: "#1 game", "Best puzzle", "Download now", price claims, fake awards
- Each app's screenshot set must be unique — no swapping titles over a shared template

### Modifying the shared wrapper (MainActivity.java, NotificationHelper, etc.)

1. Write the change in one app first and test
2. Write a migration script (pattern: `scripts/fix_*.py` files) that applies to all apps
3. Preserve per-app values: package name, AdMob IDs, IAP IDs, colors
4. Dry-run with diff output before writing
5. Bump `versionCode` of all affected apps

### Adding a brand new game/app

**Before writing any code: read `docs/QUALITY_PLAYBOOK.md`.** Same standards apply
to brand new apps as to polishing existing ones.

**Anti-clone rule for new apps**: do NOT start a new app by saying
"make another game like X". The result will be 80% identical to X with
swapped colors — exactly the pattern Google's spam classifier flags.
Instead, start each new app from the *mechanic* (sudoku constraint
solving, tile-pair matching, line-clearing, jigsaw piece snapping —
genuinely different state models and input patterns), then design
visuals to fit that mechanic. The wrapper code is shared; the
`game.html` must not be a variant of an existing one.

1. Copy `_template/` to a new `<NewApp>/` folder
2. Rename the package path under `android/app/src/main/java/com/pegasusgames/<newapp>/`
3. Update `applicationId` in `android/app/build.gradle`
4. Update `android:label` in `AndroidManifest.xml`
5. Write real `game.html` following the playbook — vivid palette, proper
   font, no emoji icons, animated tutorial, etc. Confirm the new game's
   mechanic is genuinely different from every other published app in the
   portfolio (different state model, different player input pattern, not
   just a reskin).
6. Run `init_app_metadata.py <NewApp>` to scaffold the metadata/ and store/ folders
7. Fill in all the metadata files **with hand-written copy specific to
   THIS app** — never template-substitute another app's listing
8. Create AdMob + IAP products in the respective consoles
9. Create the actual screenshot and icon files (don't leave placeholder
   PNGs) following playbook §7. The icon's focal element must differ from
   every other Pegasus Games app's icon focal element.
10. Walk through the per-app review checklist in `docs/QUALITY_PLAYBOOK.md` §13
11. Run `pre_publish_check.py <NewApp>` — must pass, including the new
    `cross-app asset similarity` and `listing copy uniqueness` checks
12. Confirm the cadence rules in **"Shipping cadence"** above allow
    publishing this app this week given what else has shipped recently

### Making mass changes

Always write a Python script that:

- Defines a `BASE` constant pointing at the repo root
- Iterates only over actual app directories (skip `_template`, `_release`, `__pycache__`, hidden dirs)
- Preserves per-app unique values (`applicationId`, AdMob IDs, IAP IDs, package statements, `WEBVIEW_BG_COLOR`, icons, store assets, metadata text files)
- Prints what it's about to do before doing it; add a `--dry-run` flag for non-trivial scripts
- Follows the existing `scripts/fix_all_apps.py` / `scripts/prepare_for_publish.py` conventions

---

## Things to flag to the user

If you see any of these while working, stop and bring them up:

- An app whose `game.html` duplicates another app's
- An app on the BLOCKED_APPS placeholder-clones list whose `game.html`
  hasn't been rewritten yet
- An app whose folder name doesn't match its `<title>`
- An app with a shared AdMob unit ID or AdMob app ID with another app
- An icon that's visually near-identical to another app's icon (same
  focal element with swapped colors counts as the same icon, not a new one)
- A request to publish more than 2–3 apps in the same week
- A request to auto-generate Play Console listings from a template (string substitution across apps)
- An app with `game.html` under ~8KB planned for publishing
- A request to reuse screenshots across multiple apps
- A `keystore.properties` committed with real passwords
- A `privacy_policy_url` shared across many apps when the apps have different data practices
- A `store/privacy-policy.html` file inside any per-app folder (delete on sight; the canonical privacy policy lives at the shared URL — see "Canonical contact info and URLs" section)
- A privacy policy URL or support URL that doesn't match the canonical values in this file
- An app whose `iaps.json` doesn't match the product IDs declared in its `MainActivity.java`
- A `content_rating.json` with `gambling_mechanics` set for a game targeted at children (automatic rejection)
- A user request to "just ship the placeholder app, I'll fix it later" — say
  no. Placeholder clones violate Google's Repetitive Content policy and one
  publish is enough to risk the whole account.

---

## Useful existing scripts

- `scripts/fix_all_apps.py` — Android fixes (billing v8, ProGuard, manifest cleanup) + iOS scaffolding
- `scripts/prepare_for_publish.py` — AppLovin MAX upgrade, notification infrastructure, versionCode bumps (scoped to the 6 flagship games)
- `scripts/gen_store_assets.py` — generates store assets
- `scripts/add_retention_features.py` — adds retention hooks
- `scripts/add_translations.py` — i18n strings
- `scripts/pre_publish_check.py` — the guard script; run before every release
- `scripts/init_app_metadata.py` — scaffolds the metadata/ and store/ folder structure for an app (use when starting work on a new app)

---

## House style for generated code

- **Python**: stdlib only unless user asks otherwise; docstring header; `BASE` constant; match patterns in `scripts/fix_all_apps.py`.
- **Java**: match existing `MainActivity.java` formatting (4-space indent, grouped imports with section comments).
- **HTML/CSS/JS in `game.html`**: single file; inline `<style>` and `<script>`; CSS custom properties for theme at the top (`:root { --bg: ...; }`); no external CDN dependencies (WebView loads from local assets).
- **JSON metadata**: 2-space indent, trailing newline, UTF-8, no comments (valid JSON).
- **Text metadata**: plain UTF-8, trim trailing whitespace, single trailing newline, no BOM.

---

## One honest note on scope

The user's long-term goal is to finish all ~200 apps to the quality of the 6
flagship games, each with a complete `metadata/` folder. That's realistic
only at a specific scale — one person finishing ~1 app per week sustainably
is 4 years of work for 200 apps. When asked to "finish all of them," help
with one at a time and keep the quality bar at the flagship level rather
than racing to ship thin versions of many. The publisher with 30 polished
apps out-earns the publisher with 200 thin ones, and carries a fraction of
the policy risk.
