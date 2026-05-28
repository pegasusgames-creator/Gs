"""check_synth_header_scope — block when the MENU shim's synth top-bar
could leak onto non-menu screens.

Bug origin (2026-05-28 round-13): High-Scores screen on Puzzle2048
rendered the menu's lives/coins/+25/trophy synth header on top of its
native Back button + title, because the synth header was created inside
menuScreen but no rule scoped its visibility to menuScreen.active.

Static check: the MENU shim CSS must include a rule that hides
`[data-synth-menu-header]` whenever its hosting `.screen` lacks the
`.active` class. The CSS selector that satisfies this is
`.screen:not(.active) [data-synth-menu-header]` — block if missing.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']

SCOPE_RE = re.compile(
    r'\.screen:not\(\.active\)\s*\[data-synth-menu-header\]\s*\{[^}]*display\s*:\s*none',
    re.DOTALL,
)


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    if 'data-synth-menu-header' not in text:
        return ([], [f'{app}: MENU shim not present — skip'])
    if SCOPE_RE.search(text):
        return ([], [])
    return ([f'{app}: synth top-bar scope CSS missing — bar can leak to non-menu screens'], [])


def main() -> int:
    args = [a for a in sys.argv[1:] if a and a != '--all']
    apps = args if args else FLAGSHIPS
    bad, warn = [], []
    for a in apps:
        b, w = check_app(a)
        bad.extend(b); warn.extend(w)
    for line in bad:
        print('  ✗', line)
    for line in warn:
        print('  !', line)
    if bad:
        print(f'synth-header-scope check: {len(bad)} blocker(s)')
        return 1
    print('synth-header-scope check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
