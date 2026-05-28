"""check_continue_label — verify the MENU shim's hasResumableProgress
doesn't show 'Continue · 0' for 2048-style apps when no run is in
progress.

Bug origin (2026-05-28 round-13): Puzzle2048 menu showed
'Continue · 0' on a fresh-seeded game where score=0 — because the
shim treated bestScore>0 as "resumable progress". Real resume must
require an in-progress grid (non-zero tile) or a non-zero current
score.

Static check: shim source must include a grid-or-score guard inside
the 2048 branch of hasResumableProgress (looks for 'gridHasTile' or
'sc > 0').
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SHIM_SRC = BASE / 'scripts' / '_growth_shim_menu.html'


def check_shim() -> list[str]:
    if not SHIM_SRC.exists():
        return ['_growth_shim_menu.html missing']
    s = SHIM_SRC.read_text(encoding='utf-8')
    m = re.search(r"function\s+hasResumableProgress[\s\S]*?return false;\s*\}", s)
    if not m:
        return ['hasResumableProgress() function not found']
    body = m.group(0)
    if "'2048'" not in body:
        return ['hasResumableProgress missing 2048-specific branch']
    if 'gridHasTile' not in body and 'sc > 0' not in body:
        return ['hasResumableProgress 2048 branch lacks grid-or-score guard — risks "Continue · 0"']
    return []


def main() -> int:
    bad = check_shim()
    for line in bad:
        print('  ✗', line)
    if bad:
        print(f'continue-label check: {len(bad)} blocker(s)')
        return 1
    print('continue-label check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
