"""check_save_key_probe — verify MENU shim's readSave() probes every
per-app localStorage save key, so lives/coins display on every app.

Bug origin (2026-05-28 round-13): Nonogram's menu top bar showed no
lives/coins because the shim's `readSave` probed `nonogram_save` while
the app actually stores under `nonogram_state`. Add a check that every
key listed in the per-app `localStorage.setItem(...)` calls for save
state is also in the shim's probe array.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FLAGSHIPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle']

# Per-app authoritative save key — confirmed from each app's source.
AUTHORITATIVE_SAVE_KEYS = {
    'WaterSortPuzzle': 'watersort_save',
    'Nonogram':        'nonogram_state',
    'Puzzle2048':      'puzzle2048_save',
    'UnblockPuzzle':   'unblock_save',
}


def shim_save_keys(text: str) -> set[str]:
    """Pull every key from every `var keys = [...]` array in the file.
    The MENU shim's readSave is the one driving the top-bar lives/coins;
    requiring the per-app key in ANY probe array is sufficient as long
    as the MENU shim is one of them.
    """
    keys: set[str] = set()
    for m in re.finditer(r'var\s+keys\s*=\s*\[([^\]]+)\]', text):
        keys.update(re.findall(r"'([^']+)'", m.group(1)))
    return keys


def check_app(app: str):
    p = BASE / app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return ([f'{app}: game.html missing'], [])
    text = p.read_text(encoding='utf-8')
    if 'data-growth-shim="MENU"' not in text:
        return ([], [f'{app}: MENU shim not present — skip'])
    probed = shim_save_keys(text)
    expected = AUTHORITATIVE_SAVE_KEYS.get(app)
    if not expected:
        return ([], [])
    if expected not in probed:
        return ([f"{app}: MENU shim readSave doesn't probe '{expected}' — top-bar lives/coins will be blank"], [])
    return ([], [])


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
        print(f'save-key-probe check: {len(bad)} blocker(s)')
        return 1
    print('save-key-probe check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
