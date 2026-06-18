#!/usr/bin/env python3
"""Pre-publish gate: every screenshot slot must be ACTUAL GAMEPLAY.

2026-06-18 policy (CLAUDE.md "Screenshot rules" + QUALITY_PLAYBOOK §7.1):
each store-screenshot slot — all 7 phone + 2 tablet_7 + 2 tablet_10 — is a
gameplay board at a distinct level. No other pages, no overlays. This gate
reads `test/screenshot_taps.json` and BLOCKS a slot whose tap ops:

  * navigate to a non-gameplay screen — `showScreen('themes')`,
    `Game.showScreen('statsScreen')`, level-select, shop, settings,
    missions, etc. (only the gameplay/board screen ids are allowed);
  * trigger a Level-Complete / win / game-over / no-lives / hint overlay
    (`...Overlay.classList.add('active')`, `win-overlay`, `overlay-*`);
  * open the Ranks / weekly-standings sheet (`openRanksSheet`,
    `switchRanksTab`, `showTournament[Modal]`);
  * inject a daily / streak banner or start the daily challenge
    (`_showDailyBanner`, `_injectDailyChip`, `startDailyChallenge`).

Only the per-slot arrays are inspected — keys starting with `_`
(`_setup_taps`, `_comment`, `_readiness_expr`) are seeding/cleaning and
exempt. Only applies to apps that ship `test/screenshot_taps.json`.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Screen ids that ARE gameplay — a showScreen() to any of these is fine.
ALLOWED_SCREENS = {
    "gamescreen", "game", "play", "playscreen", "screen-game",
    "screen-play", "gameplay", "board", "boardscreen",
}

# A showScreen('X') / Game.showScreen('X') / obj.showScreen("X") call.
_SHOW_SCREEN = re.compile(r"showScreen\(\s*['\"]([^'\"]+)['\"]")

# Overlay activation: an overlay/win/complete/game-over/get-ready id that
# gets .classList.add('active') OR .style.display set to a visible value.
_OVERLAY_ID = re.compile(
    r"['\"]([A-Za-z0-9_-]*"
    r"(?:[Oo]verlay|win-overlay|game-?over|get-?ready|level-?complete)"
    r"[A-Za-z0-9_-]*)['\"]")
_OVERLAY_ACTIVATE = re.compile(
    r"classList\.add\(\s*['\"]active['\"]"
    r"|\.style\.display\s*=\s*['\"](?:flex|block|grid)['\"]")

# Forbidden helper / feature calls — ranks sheet, tournament, daily banner,
# daily-challenge start, and the common non-gameplay screen openers
# (menu / shop / leaderboard / stats / level-select / themes / settings).
_FORBIDDEN_CALLS = re.compile(
    r"\b("
    r"openRanksSheet|switchRanksTab|showTournament(?:Modal)?|"
    r"_showDailyBanner|_injectDailyChip|recordWeeklyMetric|"
    r"startDailyChallenge|"
    r"showMenu|showShop|showStore|showLeaderboard|showStats(?:Screen)?|"
    r"showLevelSelect|openLevelSelect|showLevels|showThemes|showSettings"
    r")\s*\(")

# A .click() on a level-select / menu / shop / settings / stats button.
_NAV_BUTTON_CLICK = re.compile(
    r"getElementById\(\s*['\"][^'\"]*"
    r"(btn-levels|btn-menu|btn-shop|btn-settings|btn-stats|levels-btn|"
    r"menu-btn|level-select)[^'\"]*['\"]\s*\)[^;]*\.click\(")


def _slot_js(ops) -> str:
    """Concatenate the JS payloads of a slot's op list."""
    parts = []
    if not isinstance(ops, list):
        return ""
    for op in ops:
        if isinstance(op, list) and len(op) >= 2 and op[0] == "js":
            parts.append(str(op[1]))
    return "\n".join(parts)


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    taps_path = REPO / app / "test" / "screenshot_taps.json"
    if not taps_path.exists():
        return blockers, warnings
    try:
        taps = json.loads(taps_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        warnings.append(f"{app}: screenshot_taps.json unreadable ({e})")
        return blockers, warnings
    if not isinstance(taps, dict):
        return blockers, warnings

    for key, ops in taps.items():
        if key.startswith("_"):  # _setup_taps / _comment / _readiness_expr
            continue
        js = _slot_js(ops)
        if not js:
            continue

        for m in _SHOW_SCREEN.finditer(js):
            screen = m.group(1).strip().lower()
            if screen not in ALLOWED_SCREENS:
                blockers.append(
                    f"{app}: slot '{key}' navigates to non-gameplay screen "
                    f"showScreen('{m.group(1)}') — screenshots must be "
                    f"actual gameplay boards only (2026-06-18 policy)")

        if _OVERLAY_ACTIVATE.search(js) and _OVERLAY_ID.search(js):
            ov = _OVERLAY_ID.search(js).group(1)
            blockers.append(
                f"{app}: slot '{key}' activates overlay '{ov}' — no "
                f"win/level-complete/game-over overlay in any screenshot; "
                f"capture the board mid-play instead")

        m = _FORBIDDEN_CALLS.search(js)
        if m:
            blockers.append(
                f"{app}: slot '{key}' calls {m.group(1)}() — menu / shop / "
                f"leaderboard / stats / level-select / ranks / daily are not "
                f"gameplay; every slot is a distinct gameplay board")

        m = _NAV_BUTTON_CLICK.search(js)
        if m:
            blockers.append(
                f"{app}: slot '{key}' clicks the {m.group(1)} button — "
                f"navigates off gameplay; every slot is a distinct gameplay "
                f"board")

    return blockers, warnings


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(
            p.name for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "test" / "screenshot_taps.json").exists()
        )
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"✗ {line}")
            fail = 1
        for line in w:
            print(f"!  {line}")
    if not fail:
        print(f"[screenshots gameplay only] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
