# Builder brief — one game-track app

You are finishing ONE game of the Pegasus Games portfolio to production,
upload-ready quality. Your prompt names the app (`<App>`, its folder), its
store name, its brief, its content gate and its siblings. CLAUDE.md is
binding. The owner builds the APK on their own PC, so it must work first time.

## Shared worktree (other builders are working in other folders right now)

- Touch ONLY `<App>/` and your NEW gate `scripts/check_<app>_*.py`. Never edit
  shared files: `scripts/_growth_shim_*`, `pre_publish_check.py`,
  `scaffold_flagship.py`, `register_flagship.py`, `wire_growth_core.py`,
  `reinject_all_shims.py`, `app_themes.py`, existing `check_*.py`, `docs/`,
  `CLAUDE.md`, other apps. If one blocks you, say so in your report.
- Never run `git commit/add/stash/checkout/reset/clean/restore`. The lead commits.
- If `<App>` has no `android/` project or its game.html is not the family
  shell yet (`python3 scripts/shell_region.py <App>` lists no regions), run
  ONCE: `python3 scripts/scaffold_flagship.py <App> --name "<Name>"
  --version-name 2.0.0 --replace-iaps` (add `--pkg com.pegasusgames.<x>` for a
  folder with no android/; never change an existing applicationId). If the
  regions exist, never run it again — it overwrites game.html.
- CPU is shared (4 cores): run long jobs (mining, solvers) with `nice`,
  bounded to ≤ 10 min each, writing results to files.

## Token budget

game.html is ~500 KB of shared code (fonts, shims). Read `docs/GAME_SHELL.md`
first, then only the regions you need: `python3 scripts/shell_region.py <App>
NAME` (no NAME = list; `--set file` replaces). Never cat/Read the whole
game.html; use `grep -n` and narrow line ranges. Pipe big outputs through
`head`/`tail`/`wc`. Don't re-read files you just wrote.

## Resume

A previous builder may have started (sessions can be cut off). First check
`python3 scripts/shell_region.py <App> ENGINE | head -3` ("AFTERIMAGE CORE"
= untouched), `ls <App>/test <App>/metadata <App>/store`, `ls
scripts/check_<app>*` — reuse good work, finish what is missing.

The previous thin version is in git for ideas only:
`git show 3c62c1ae~1:<OldFolder>/android/app/src/main/assets/game.html`
(OldFolder differs for renamed apps — see docs/PORTFOLIO_PLAN.md).

## Quality bar

Compete with the category leader on feel: crisp at 360×640 up to 800×1280,
readable at arm's length, tactile feedback (animation, WebAudio SFX, haptics
via `navigator.vibrate` behind a Settings toggle), no dead buttons, no clipped
text, light default theme in its own colour family (check
`scripts/app_themes.py` and CLAUDE.md "Distinct light palette per app" so you
don't collide with a sibling), midnight + 5 other themes that visibly recolour
the board, honest copy. Levels 1–3 solvable in < 30 s, difficulty ramps,
≥ 500 levels for leveled games, every one passing your gate. Every SKU in
`metadata/iaps.json` must do what its description says in THIS game (reword
SHOP names/descriptions truthfully). Must differ from its siblings in
mechanic, layout, palette, icon focal element and copy (Repetitive Content
policy). No third-party trademarks or look-alike trade dress anywhere.

## Deliverables

Everything in docs/GAME_SHELL.md "Deliverables per game", plus
`<App>/test/register.json`:

```json
{"gate": ["scripts/check_<app>_<property>.py", "<short label>"],
 "app_theme": {"bg_top_left": [r,g,b], "bg_top_right": [r,g,b], "bg_bottom": [r,g,b],
   "text_primary": [r,g,b], "text_accent": [r,g,b], "text_subtle": [r,g,b],
   "footer_tint": [r,g,b], "mood": "<2-3 words>", "layout_archetype": "<A-I>",
   "mascot_pattern": "<M0-M4>", "voice": "<V1-V8>", "texture": "<T1-T8>"}}
```

(codes from docs/APP_ARCHETYPES.md — read only its tables; never A+M0+V1+T1).

## Verify

Run the "Verify before you finish" list in docs/GAME_SHELL.md. Play it
headlessly in Chromium with real input events (Playwright at
`/opt/node-tools/node_modules/playwright`, browser `/opt/pw-browsers`, mock
bridge `scripts/runtime/mock_bridge.js`) and LOOK at your screenshots (PNGs
under `/tmp/claude-0/-home-user-Gs/eb070d53-e68e-52f2-9131-df2ea4ae5c7c/scratchpad/<App>/`).
Fix what you see. `pre_publish_check.py <App>`: the only blockers allowed to
remain are test AdMob IDs / license key / leaderboard placeholders (the owner
pastes real IDs), screenshots not captured (emulator-only), and registry
items the lead wires (gate not in list, BLOCKED_APPS, app_themes,
PRE_RELEASE). Fix everything else.

## Final report (≤ 25 lines)

What you built (mechanic, levels, boosters, themes), gate + test results, the
remaining pre_publish blocker names, anything you could not do.
