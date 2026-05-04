# Pegasus Games — Claude Code Instructions

Portfolio of ~200 Android apps/games sharing a common WebView wrapper.
Each top-level folder (except `_template/`, `_release/`, `docs/`,
`scripts/`) is one app with `game.html` inside `MainActivity.java`.
Read this file end-to-end before doing anything in here.

**Repo layout:**
- `Gs/CLAUDE.md` — this file (root)
- `Gs/docs/` — all `.md` reference docs (`SHIP_GAME.md`,
  `QUALITY_PLAYBOOK.md`, `APP_ARCHETYPES.md`, `TRANSLATIONS.md`,
  `NOTIFICATIONS_IMPL.md`)
- `Gs/scripts/` — all Python scripts (`pre_publish_check.py`,
  `build_release.py`, `gen_handoff.py`, `gen_translations.py`,
  `consult_designer.py`, `init_app_metadata.py`,
  `capture_screenshots.py`, `wrap_screenshots.py`,
  `wrap_tablet_screenshots.py`, `app_themes.py`,
  `dedup_similar_apps.py`, `fix_all_apps.py`,
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
- **`TRANSLATIONS.md`** — 11 locales (en + de, es-419, fr, hi, id, it,
  ja, pt-BR, tr, uk-UA). Russian excluded. Title stays English globally.
  Read in Phase 4.5.
- **`NOTIFICATIONS_IMPL.md`** — Java + JS reference for local notifications.
- **`pre_publish_check.py`** — guard script (auto-run by `build_release.py`)
- **`build_release.py`** — Phase 5/7/8 automation
- **`gen_handoff.py`** — generates per-app `RELEASE_HANDOFF.md`
- **`gen_translations.py`** — Phase 4.5 translations (needs `ANTHROPIC_API_KEY`)
- **`consult_designer.py`** — sub-agent design questions during Phase 1/8
- **`init_app_metadata.py`** — scaffolds metadata/store folders
- **`capture_screenshots.py`** — emulator-driven (uses `adb`)
- **`wrap_screenshots.py` / `wrap_tablet_screenshots.py`** — marketing frames
- **`app_themes.py`** — per-app palette + 4-archetype registry
- **`dedup_similar_apps.py`** — finds clusters with too-similar mechanics

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
    ├── de-DE/, es-419/, fr-FR/, hi-IN/, id-ID/, it-IT/, ja-JP/, pt-BR/,
    │   tr-TR/, uk-UA/                  # 10 more locales (TRANSLATIONS.md)
    ├── app_info.json                   # category, ads, audience, URLs
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
language, AdMob ID matches manifest+MainActivity, archetype presence
(four archetypes set in `app_themes.py` + `metadata/app_identity.md`
present), translations present (all 11 locales), menu button count ≤6.

If any blocker fails, stop. Do not build, do not upload, do not advance
to the next app.

---

## State of the apps (last audit)

- **Finished and release-ready (5):** WaterSort, Nonogram, PipeConnect,
  Puzzle2048, UnblockPuzzle. Game code done; metadata folders need full
  population.
- **Already shipped to Play Store (1):** WaterSort.
- **Recently deleted:** BallSortPuzzle (Apr 30 2026 — too similar to
  WaterSort, ~zero downloads). Play Store listing remains until manually
  unpublished.
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
  is genuinely rewritten.

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

- Two apps with duplicate `game.html`
- An app on `BLOCKED_APPS` whose `game.html` hasn't been rewritten
- App folder name ≠ `<title>` tag
- Shared AdMob IDs across apps
- Icons visually near-identical (same focal element, swapped colors)
- Two apps in same genre cluster shipping within 7 days
- Auto-generated listings via template substitution
- `game.html` under ~8KB planned for publishing
- Reused screenshots across multiple apps
- Any temptation to use Puppeteer / headless Chromium for screenshots
  — emulator-only per `QUALITY_PLAYBOOK.md` §7.0 and `SHIP_GAME.md` §3.6.
  If `capture_screenshots.py` can't run because no AVD, surface as
  hard blocker; do NOT write a Puppeteer fallback
- `keystore.properties` committed with real passwords
- Per-app `store/privacy-policy.html` (delete on sight)
- Privacy / support URL not matching canonical values
- `iaps.json` not matching MainActivity IAP IDs
- `content_rating.json` with `gambling_mechanics` set on a kids app
- "Just ship the placeholder app, I'll fix it later" — refuse
- Crash rate >1% or ANR >0.5% on any shipped app
- App designed without picking 4 archetypes from `APP_ARCHETYPES.md`
- Archetype combination A+M0+V1+T1 (the template — refuse without
  varying ≥2 of 4)
- Layout A used by >30% of shipped apps
- Texture T1 used by >40% of shipped apps after month 6
- `metadata/app_identity.md` missing or empty at Phase 5
- Missing any of the 11 locale folders in `metadata/`
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
