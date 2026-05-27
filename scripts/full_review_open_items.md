# Full-review open items (2026-05-27)

Items surfaced by the Gs full-review pass that need human eyes — they are NOT
blockers for shipping the bundled 1.2.2 / 2.1.2 builds, but you should not let
them rot.

## Privacy URL manual verification (P0)
- Verify https://pegasusgames-creator.github.io/privacy.html resolves with a
  real policy (the canonical URL across every app). Open in a private window
  to check.

## AppLovin keys (P2 — user choice)
- AppLovin SDK key in `AndroidManifest.xml` for every app is intentionally
  left blank — user is on AdMob only, no AppLovin mediation. Keep as-is.

## Play Games Services placeholders (P1)
- Every app's `strings.xml` carries a `games_app_id` placeholder
  (`\ 0000000000000`). The growth shim G's `LEADERBOARD_ID` is still
  `TODO_FROM_PLAY_CONSOLE`. Both clear when leaderboards are wired in Play
  Console — see SHIP_GAME §B (post-publish setup).

## Ukrainian translation review (P2)
The 2026-05-27 calque sweep fixed:
- `WaterSortPuzzle/metadata/uk/full_description.txt:27` — "паром" (steam,
  literal calque of golf "par") → "цільового мінімуму". Confirmed natural
  Ukrainian wording.

Lines flagged for native review (subjective fluency check — not literal
calques):
- `WaterSortPuzzle/metadata/uk/full_description.txt:1` —
  Title-cased headline "Сортування Води" looks like English title-case
  imported into Ukrainian. Native speakers prefer "Сортування води" or
  a different framing. Low risk, deferred.
- All four apps' uk `full_description.txt` use "Натискайте" (formal) vs
  "Натискай" (informal) inconsistently across paragraphs. Pick a register
  per app and apply.

## Security note (G3 mirror)
- `keystore.properties` stores its passwords in plaintext (a gradle
  requirement) — every keystore file (`*.jks`, `*.keystore`,
  `keystore.properties`, `*.pem`, `*.der`, `local.properties`,
  `google-services.json`) is now in `.gitignore` at the repo root and every
  app root.
- Any archive zipped for sharing (Drive backup, support upload, USB stick)
  MUST exclude `**/keystore.*` and `**/*.pem`. The release_aabs/ folder
  contains signed AABs and is also gitignored.

## Subscription disclosure validation (C1)
- The 2026-05-27 SUBS shim adds auto-renew disclosure under every Season
  Pass / Weekly Pass button across all 4 apps and a Manage Subscriptions
  row in Settings. Verify in-emulator that the disclosure shows at the
  correct locale on a first install of each app.
