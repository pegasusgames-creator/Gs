"""check_menu_tile_tokens — verify each flagship's :root defines
`--menu-tile-bg / --menu-tile-border / --menu-tile-fg` so that the
chip + Missions/Stats + Tier-3 + Restore Purchases all share one
visual treatment.

Bug origin (round-14): MENU shim's chip CSS uses
`var(--menu-tile-bg, …)` etc. but apps shipped without those tokens
defined, so chips fell back to the generic --surface (or grey
neutral), producing the "Missions and Stats different color" /
"Shield Daily white boxes" complaints.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']
REQUIRED = ('--menu-tile-bg', '--menu-tile-border', '--menu-tile-fg')


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    miss = [t for t in REQUIRED if t + ':' not in text and t + ' :' not in text]
    if miss:
        return ([f'{app}: :root missing menu-tile tokens {miss}'], [])
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
        print(f'menu-tile-tokens check: {len(bad)} blocker(s)')
        return 1
    print('menu-tile-tokens check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
