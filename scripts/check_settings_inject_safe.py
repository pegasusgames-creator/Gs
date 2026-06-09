"""check_settings_inject_safe — block `insertBefore(row, container.firstChild)`
in the language-picker injection. Settings additions must `appendChild`
into the inner `.settings-list`, not `insertBefore` the screen root.

Bug origin (round-14): UnblockPuzzle rendered `Language English` as a
floating panel ABOVE the "Settings" title because injectLangSelector
used `container.insertBefore(row, container.firstChild)` on the screen
element — the row landed before the title.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']

BAD_PATTERN = re.compile(r'insertBefore\s*\(\s*row\s*,\s*container\.firstChild\s*\)')


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    if 'injectLangSelector' not in text:
        return ([], [])
    if BAD_PATTERN.search(text):
        return ([f'{app}: injectLangSelector still uses insertBefore(row, container.firstChild) — language row will float above Settings title'], [])
    return ([], [])


def main() -> int:
    args = [a for a in sys.argv[1:] if a and a != '--all']
    apps = args if args else FLAGSHIPS
    bad = []
    for a in apps:
        b, _ = check_app(a)
        bad.extend(b)
    for line in bad:
        print('  ✗', line)
    if bad:
        print(f'settings-inject-safe check: {len(bad)} blocker(s)')
        return 1
    print('settings-inject-safe check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
