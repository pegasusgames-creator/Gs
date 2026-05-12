# Pegasus Games

Solo developer mobile app portfolio. ~200 Android apps and games
targeting Google Play, Ukrainian-developed.

This repository contains the source code for all apps in the portfolio.
Each top-level folder (e.g., `WaterSortPuzzle/`, `Nonogram/`) is a single
Android + iOS app with a shared WebView wrapper architecture:

- `<App>/android/` — Android project (Java + WebView wrapper)
- `<App>/ios/` — iOS scaffolding (Swift)
- `<App>/android/app/src/main/assets/game.html` — the app's actual
  gameplay (HTML5 / JavaScript, single-file)
- `<App>/store/` — store listing assets (icons, screenshots, feature
  graphic)
- `<App>/metadata/` — store listing copy across 13 locales

## Architecture

Apps are HTML5 games loaded inside a thin native WebView shell. The
wrapper code (`MainActivity.java`, `NotificationReceiver.java`) is
shared across all apps. Each `game.html` is a single self-contained
file under ~200KB with no external CDN dependencies.

This is the same architecture used by Voodoo, SayGames, and King for
their large-portfolio publishing.

## Documentation

`CLAUDE.md` (repo root) is the top-level project rules — read it first.
The `docs/` folder contains the rest of the playbook:

- `docs/SHIP_GAME.md` — release workflow for shipping a new app (8 phases)
- `docs/QUALITY_PLAYBOOK.md` — design / UX / gameplay / monetization standards
- `docs/APP_ARCHETYPES.md` — visual + voice variation system
- `docs/TRANSLATIONS.md` — 13-locale localization rules
- `docs/COMPETITIVE_BENCHMARK.md` — analysis of top-grossing analogs
- `docs/NOTIFICATIONS_IMPL.md` — local notifications reference
- `docs/IAP_CATALOG.md` — Play Console form-ready IAP catalog

## Tooling

The `scripts/` folder contains automation:

- `pre_publish_check.py` — pre-build verification (run before every release;
  it runs the `check_*.py` modules — IAP invariants, IAP grant parity,
  retention-feature parity, subscription promise parity, coin tier ladder,
  booster catalog, menu completeness, seasonal events, screenshot uniqueness,
  keystore SHA1, …)
- `build_release.py` — Phase 5/7/8 of SHIP_GAME automation
- `gen_handoff.py` — generates per-app release checklist (`RELEASE_HANDOFF.md`)
- `gen_store_paste.py` — assembles per-app Play-Console paste content (`STORE_PASTE.md`)
- `gen_translations.py` — LLM translations into the 13 locales (Anthropic, or OpenAI fallback)
- `pepk_command.py` / `gen_upload_keystore.py` — Play App Signing setup per app
- `consult_designer.py` — sub-agent design questions
- `capture_screenshots.py` — emulator-driven Play Store screenshots (phone + tablet 7"/10")
- `wrap_screenshots.py` / `wrap_tablet_screenshots.py` — marketing-frame wrapping
- `gen_icon.py` / `gen_feature.py` / `gen_appstore_icon.py` — store image generation
- `init_app_metadata.py` — scaffolds metadata/ for a new app
- `dedup_similar_apps.py` — finds clusters with too-similar mechanics
- `app_themes.py` — per-app palette + 4-archetype registry

## Public website

`https://pegasusgames-creator.github.io/`

Hosts:
- Privacy policy (general + kids variants)
- Cross-promotion config (`promo.json` / `promo-kids.json`)
- App support / contact

## Contact

Developer: pegasusgames@atomicmail.io

## License

Proprietary. All rights reserved.
