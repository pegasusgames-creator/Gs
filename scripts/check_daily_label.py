"""check_daily_label — verify the MENU shim's `patchMenuButtons`
renders the Tier-2 Daily button as `Daily puzzle · <date>`, NOT as a
streak count.

Bug origin (2026-05-28 round-13): user wants the Daily button label
to communicate what's different about today (the date), not duplicate
the streak count which already lives on the streak chip.

Static check: shim source must contain the literal phrase
`Daily puzzle` AND a date variable (`getMonth()` / `getDate()`).
Block if it still appends a 🔥<streak> suffix instead.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']
SHIM_SRC = BASE / 'scripts' / '_growth_shim_menu.html'


def check_shim_source() -> list[str]:
    if not SHIM_SRC.exists():
        return ['_growth_shim_menu.html missing']
    s = SHIM_SRC.read_text(encoding='utf-8')
    issues = []
    if 'Daily puzzle' not in s:
        issues.append('shim source missing literal "Daily puzzle"')
    if 'getMonth(' not in s or 'getDate(' not in s:
        issues.append('shim source missing date computation for Daily label')
    # Old streak-suffix code shouldn't still be the rendered label.
    if re.search(r"newHtml\s*=\s*lbl\s*\+\s*\(streak", s):
        issues.append('shim still appends 🔥<streak> to Daily label — should be date-driven')
    return issues


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    if 'data-growth-shim="MENU"' not in text:
        return ([], [f'{app}: MENU shim not present — skip'])
    if 'Daily puzzle' not in text:
        return ([f'{app}: MENU shim out of date — re-inject _growth_shim_menu.html (missing "Daily puzzle")'], [])
    return ([], [])


def main() -> int:
    bad = check_shim_source()
    args = [a for a in sys.argv[1:] if a and a != '--all']
    apps = args if args else FLAGSHIPS
    warn = []
    for a in apps:
        b, w = check_app(a)
        bad.extend(b); warn.extend(w)
    for line in bad:
        print('  ✗', line)
    for line in warn:
        print('  !', line)
    if bad:
        print(f'daily-label check: {len(bad)} blocker(s)')
        return 1
    print('daily-label check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
