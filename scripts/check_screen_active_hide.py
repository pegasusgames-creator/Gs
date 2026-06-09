"""check_screen_active_hide — block when MENU shim CSS sets
`#menuScreen{display:flex !important}` WITHOUT the `.active` qualifier.

Bug origin (round-14): without `.active`, `display:flex !important`
overrides each app's `.screen:not(.active){display:none}` rule, so
the menu's icon-row + chips bleed into the gameplay / settings screens.

Static check: require both
  (a) `#menuScreen.active` (or `#screen-menu.active`) in the
      flex-display rule, AND
  (b) `.screen:not(.active){display:none !important}` belt-and-braces
      rule in the shim CSS.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']
SHIM = BASE / 'scripts' / '_growth_shim_menu.html'

UNSCOPED_FLEX = re.compile(r'#menuScreen\s*,\s*#screen-menu\s*\{\s*display\s*:\s*flex\s*!important')
SCOPED_FLEX  = re.compile(r'#menuScreen\.active\s*,\s*#screen-menu\.active\s*\{\s*display\s*:\s*flex\s*!important')
NOT_ACTIVE_HIDE = re.compile(r'\.screen:not\(\.active\)\s*\{\s*display\s*:\s*none\s*!important')


def check_source() -> list[str]:
    if not SHIM.exists():
        return ['_growth_shim_menu.html missing']
    s = SHIM.read_text(encoding='utf-8')
    issues = []
    # Strip JS '+' concat boundaries so multi-line CSS reads as one blob.
    blob = re.sub(r"'\s*\+\s*\n\s*'", '', s)
    if UNSCOPED_FLEX.search(blob):
        issues.append('MENU shim sets display:flex !important on #menuScreen WITHOUT .active — leaks to other screens')
    if not SCOPED_FLEX.search(blob):
        issues.append('MENU shim missing #menuScreen.active{display:flex !important} — flex never applies')
    if not NOT_ACTIVE_HIDE.search(blob):
        issues.append('MENU shim missing .screen:not(.active){display:none !important} belt-and-braces hide')
    return issues


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([], [])
    text = p.read_text(encoding='utf-8')
    if 'data-growth-shim="MENU"' not in text:
        return ([], [])
    # If app's injected MENU shim is stale relative to source, the
    # source-level check above already failed; here we just confirm
    # the .active marker is present in the app's copy too.
    if '#menuScreen.active' not in text and '#screen-menu.active' not in text:
        return ([f'{app}: injected MENU shim is stale (no .active scope) — re-inject'], [])
    return ([], [])


def main() -> int:
    bad = check_source()
    args = [a for a in sys.argv[1:] if a and a != '--all']
    apps = args if args else FLAGSHIPS
    for a in apps:
        b, _ = check_app(a)
        bad.extend(b)
    for line in bad:
        print('  ✗', line)
    if bad:
        print(f'screen-active-hide check: {len(bad)} blocker(s)')
        return 1
    print('screen-active-hide check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
