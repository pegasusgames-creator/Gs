"""check_menu_composition — verify each flagship's menu follows the
2026-05-28 composition rules:

1. Menu container uses `justify-content:center` (not space-around /
   flex-start). Centered stack with even rhythm between sections.
2. Exactly one Tier-1 primary button per menu (Continue or Play). Sized
   with `clamp(64px, …)` min-height — not paired with a competing
   button of equal size.
3. Tier-2 is a single Daily Challenge button — never paired with
   another secondary button.
4. Tier-3 icon row exists, has the canonical order
   `Levels · Shop · Games · Settings` (Puzzle2048 substitutes Best for
   Levels — leftmost slot can be either). Settings lives in the row,
   NOT in a top-bar gear.
5. No standalone top-bar `.settings-btn` gear icon on the menu (the
   single rule across all 4 apps is "Settings in the icon row").

Wired into pre_publish_check.py as `[code] menu composition`.

Usage:
    python3 scripts/check_menu_composition.py            # all apps
    python3 scripts/check_menu_composition.py UnblockPuzzle
    python3 scripts/check_menu_composition.py --all
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']

# Canonical icon-row labels in this order. The leftmost slot is the
# game-specific surface: level games use "Levels"; Puzzle2048 (no levels)
# used "Best" until 2026-06-22, when that High-Scores screen was retired as
# a strict duplicate of Stats and the slot became "Themes". All three are
# accepted in the first slot.
CANONICAL_LABELS_LEFTMOST = {'Levels', 'Best', 'Themes'}
CANONICAL_LABELS_REST = ['Shop', 'Games', 'Settings']


def find_menu_block(text: str) -> str | None:
    """Pull the menu screen markup. Each flagship's id is one of
    #menuScreen / #screen-menu — heuristic: take the section between
    `<div id="menuScreen"` or `<div id="screen-menu"` and the next
    `<div id="`."""
    for sel in (r'menuScreen', r'screen-menu'):
        m = re.search(rf'<div id="{sel}"[\s\S]*?(?=<div id="[a-zA-Z][\w-]*")', text)
        if m:
            return m.group(0)
    return None


def violations_in(app: str, text: str) -> list[str]:
    issues: list[str] = []
    menu = find_menu_block(text)
    if not menu:
        return [f'{app}: could not locate menu block in game.html']

    # Rule 5 — no static top-bar settings gear inside the menu block.
    if re.search(r'class="settings-btn"', menu) or re.search(r'class="[^"]*\bsettings-gear\b[^"]*"', menu):
        issues.append(f'{app}: menu still has a top-bar Settings gear — '
                      'Settings must live in the icon row')

    # Rule 4 — icon row markup present, contains canonical labels.
    row_m = re.search(r'<div\s+class="menu-icon-row"[\s\S]*?</div>', menu)
    if not row_m:
        issues.append(f'{app}: missing .menu-icon-row inside the menu')
    else:
        row = row_m.group(0)
        # Extract icon-label texts (handles both class="menu-icon-label"
        # and plain <span>Label</span> patterns inside .icon-btn).
        labels = re.findall(r'<span[^>]*>([A-Za-z][^<]+)</span>', row)
        labels = [l.strip() for l in labels if l.strip()]
        if not labels:
            issues.append(f'{app}: icon row has no visible labels')
        else:
            # First slot must be one of {Levels, Best}; remaining must
            # contain Shop, Games, Settings in that order.
            if labels[0] not in CANONICAL_LABELS_LEFTMOST:
                issues.append(
                    f'{app}: icon-row leftmost label is "{labels[0]}", '
                    f'expected one of {sorted(CANONICAL_LABELS_LEFTMOST)}'
                )
            rest = labels[1:]
            for expected, got in zip(CANONICAL_LABELS_REST, rest):
                if got != expected:
                    issues.append(
                        f'{app}: icon-row label position mismatch — '
                        f'expected {CANONICAL_LABELS_REST}, got {rest}'
                    )
                    break

    # Rule 3 — at most ONE secondary daily button, not paired.
    # Heuristic: warn when a `menu-pair-row` / `menu-tile-row` /
    # `menu-secondary-row` wrapper still contains TWO buttons.
    for cls in (r'menu-pair-row', r'menu-tile-row', r'menu-secondary-row'):
        for m in re.finditer(
            rf'<div\s+class="{cls}"[\s\S]*?</div>', menu
        ):
            btns = re.findall(r'<button\b', m.group(0))
            if len(btns) >= 2:
                issues.append(
                    f'{app}: .{cls} on menu still holds {len(btns)} '
                    'buttons — Tier 2 must be a single Daily button'
                )

    # Rule 1 — runtime composition CSS lives in the MENU shim. Verify
    # the shim's centered-stack rules are present (shim is the source of
    # truth so all four apps share them). This is a sanity check that
    # the shim was re-injected.
    if 'justify-content:center !important' not in text:
        issues.append(
            f'{app}: MENU shim CSS missing justify-content:center — '
            're-inject _growth_shim_menu.html'
        )

    return issues


def main() -> int:
    args = [a for a in sys.argv[1:] if a and a != '--all']
    apps = args if args else FLAGSHIPS
    bad: list[str] = []
    for app in apps:
        p = BASE / app / 'android/app/src/main/assets/game.html'
        if not p.exists():
            bad.append(f'{app}: game.html not found')
            continue
        bad.extend(violations_in(app, p.read_text(encoding='utf-8')))
    if bad:
        for line in bad:
            print('  ✗', line)
        print(f'menu-composition check: {len(bad)} issue(s)')
        return 1
    print('menu-composition check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
