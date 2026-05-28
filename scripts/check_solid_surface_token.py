"""check_solid_surface_token — block when an app's :root or
html[data-theme="midnight"] block defines `--surface` as a
semi-transparent color (rgba with alpha < 1).

Bug origin (2026-05-28 round-13): WaterSort's `--surface` was
`rgba(255,255,255,0.10)` so the Ranks sheet (which uses --surface as
its panel bg) rendered as a near-black slab on top of the 62%-black
scrim — even though the user was on the light Daylight theme.

`--surface` must be a SOLID color (hex or rgb) — overlays use it as
panel/sheet/card backgrounds where transparency reads as dark.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']

SURF_DEF_RE = re.compile(r'--surface\s*:\s*([^;]+);')
# rgba with explicit alpha < 1, or just rgba with 4 args.
RGBA_TRANSPARENT = re.compile(r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*0?\.\d+\s*\)', re.IGNORECASE)


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    bad = []
    for m in SURF_DEF_RE.finditer(text):
        val = m.group(1).strip()
        if RGBA_TRANSPARENT.match(val):
            bad.append(f"{app}: --surface = '{val}' is semi-transparent — overlays will read as dark slab")
    return (bad, [])


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
        print(f'solid-surface-token check: {len(bad)} blocker(s)')
        return 1
    print('solid-surface-token check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
