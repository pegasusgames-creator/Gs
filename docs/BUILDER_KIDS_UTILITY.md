# Builder brief — one kids-track or utility-track app

You are finishing ONE app of the Pegasus Games portfolio to production,
upload-ready quality. Your prompt names the app (`<App>`, its folder), its
store name, its track (kids / utility) and its brief. CLAUDE.md is binding
where it applies to the track. The owner builds the APK on their own PC, so
it must work first time.

- **Kids** → contract `docs/KIDS_SHELL.md`, template `ABCLearning/`, gate
  `scripts/check_families_compliance.py`. Google Play Families rules are
  non-negotiable (no notifications, child-directed banner only, parental
  gate before every purchase/restore/link, no data collection).
- **Utility** → contract `docs/UTILITY_SHELL.md`, template `HabitTracker/`,
  gate `scripts/check_utility_shell.py`. Health/fitness/medical topics: no
  medical claims, add the health-apps declaration notes the doc lists.

## Shared worktree (other builders are working in other folders right now)

- Touch ONLY `<App>/` and (if your content can be wrong — facts, maths,
  conversions, quiz answers) a NEW gate `scripts/check_<app>_*.py`. Never edit
  shared files (`scripts/` other than your new gate, `docs/`, `CLAUDE.md`,
  templates, other apps). If one blocks you, say so in your report.
- Never run `git commit/add/stash/checkout/reset/clean/restore`. The lead commits.
- Scaffold ONCE if `<App>`'s game.html is not yet on your track's shell
  (`python3 scripts/shell_region.py <App>` lists no TOOL_CORE / CONTENT_ENGINE
  region): the exact command is in your contract doc (add `--pkg
  com.pegasusgames.<x>` only for a folder with no android/; never change an
  existing applicationId). If the regions exist, never run it again.
- CPU is shared (4 cores): bound long jobs (≤ 10 min, `nice`).

## Token budget

Read your contract doc, then only the regions you need via
`python3 scripts/shell_region.py <App> NAME` (no NAME = list; `--set file`
replaces). Never cat/Read the whole game.html; `grep -n` + narrow ranges.
Read the template app's regions for patterns the same way. Pipe big outputs
through `head`/`tail`/`wc`.

## Resume

A previous builder may have started. Check `python3 scripts/shell_region.py
<App>` and `ls <App>/test <App>/metadata <App>/store` first and finish what
is missing. The previous thin version is in git for ideas only:
`git show 3c62c1ae~1:<OldFolder>/android/app/src/main/assets/game.html`.

## Quality bar

Compete with the category leader on usefulness and feel: the core job done
fast and correctly, clean layout at 360×640 up to 800×1280, every string in
13 languages (Arabic RTL, Japanese checked), tokens only (WCAG AA), no dead
buttons, no clipped text, light default in its own colour family (check
`scripts/app_themes.py` so you don't collide with a sibling), honest copy,
no third-party trademarks. Must differ from its siblings (docs/PORTFOLIO_PLAN.md
"Siblings that must stay clearly distinct") in purpose, layout, palette,
icon focal element and copy. Content that can be wrong (facts, unit
conversions, formulas, quiz answers, reference data) is checked by a gate.

## Deliverables

Everything in your contract doc's per-app checklist, plus
`<App>/test/register.json` (`{"gate": [script, label] or null,
"app_theme": {...}}` — shape in docs/BUILDER_GAME.md).

## Verify

Your contract doc's verify list. Drive it headlessly with real input events
and LOOK at your screenshots (PNGs under
`/tmp/claude-0/-home-user-Gs/eb070d53-e68e-52f2-9131-df2ea4ae5c7c/scratchpad/<App>/`).
`pre_publish_check.py <App>`: only test AdMob IDs, uncaptured screenshots
(emulator-only), a missing keystore, and registry items the lead wires may
remain.

## Final report (≤ 20 lines)

What you built, gate + test results, remaining pre_publish blocker names,
anything you could not do.
