# Pegasus Games

Solo developer mobile app portfolio. ~100 Android apps and games on
Google Play, Ukrainian-developed.

This repository contains the source code for all apps in the portfolio.
Each top-level folder (e.g., `WaterSort/`, `Nonogram/`) is a single
Android + iOS app with a shared WebView wrapper architecture:

- `<App>/android/` — Android project (Java + WebView wrapper)
- `<App>/ios/` — iOS scaffolding (Swift)
- `<App>/android/app/src/main/assets/game.html` — the app's actual
  gameplay (HTML5 / JavaScript, single-file)
- `<App>/store/` — store listing assets (icons, screenshots, feature
  graphic)
- `<App>/metadata/` — store listing copy across 11 locales

## Architecture

Apps are HTML5 games loaded inside a thin native WebView shell. The
wrapper code (`MainActivity.java`, `NotificationReceiver.java`) is
shared across all apps. Each `game.html` is a single self-contained
file under 200KB with no external CDN dependencies.

This is the same architecture used by Voodoo, SayGames, and King for
their large-portfolio publishing.

## Documentation

The `docs/` folder contains the full development playbook:

- `CLAUDE.md` — top-level project rules (in repo root, not docs/)
- `docs/SHIP_GAME.md` — release workflow for shipping a new app
- `docs/QUALITY_PLAYBOOK.md` — design / UX / monetization standards
- `docs/APP_ARCHETYPES.md` — visual + voice variation system
- `docs/TRANSLATIONS.md` — 11-locale localization rules
- `docs/COMPETITIVE_BENCHMARK.md` — analysis of top-grossing analogs
- `docs/NOTIFICATIONS_IMPL.md` — local notifications reference

## Tooling

The `scripts/` folder contains automation:

- `pre_publish_check.py` — pre-build verification (run before every release)
- `build_release.py` — Phase 5/7/8 of SHIP_GAME automation
- `gen_handoff.py` — generates per-app release checklist
- `gen_translations.py` — Anthropic API translations for 10 locales
- `consult_designer.py` — sub-agent design questions
- `capture_screenshots.py` — emulator-driven Play Store screenshots
- `wrap_screenshots.py` — marketing-frame wrapping
- `init_app_metadata.py` — scaffolds metadata/ for a new app
- `dedup_similar_apps.py` — finds clusters with too-similar mechanics

## Public website

`https://pegasusgames-creator.github.io/`

Hosts:
- Privacy policy (general + kids variants)
- Cross-promotion config (`promo.json`)
- App support / contact

## Contact

Developer: pegasusgames@atomicmail.io

## License

Proprietary. All rights reserved.
