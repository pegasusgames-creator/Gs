#!/usr/bin/env python3
"""wire_leaderboards.py — bake the per-app Play Games Services leaderboard
ID into each app's game.html, replacing the canonical
'TODO_FROM_PLAY_CONSOLE' placeholder. Re-run any time a leaderboard is
re-created in Play Console.

Hardcoded mapping (PGS project 225819574531, leaderboards created
2026-05-27). Add entries here when shipping a new app — every NEW app's
game.html starts with the placeholder.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

IDS = {
    'WaterSortPuzzle': 'CgkIg4KVn8kGEAIQAw',
    'Nonogram':        'CgkIg4KVn8kGEAIQBA',
    'Puzzle2048':      'CgkIg4KVn8kGEAIQBQ',
    'UnblockPuzzle':   'CgkIg4KVn8kGEAIQBg',
}
LINE_RE = re.compile(r"var LEADERBOARD_ID = '[^']*';")


def main():
    any_change = False
    for app, lid in IDS.items():
        p = REPO/app/'android/app/src/main/assets/game.html'
        if not p.exists():
            print(f'  ? {app}: no game.html — skipping'); continue
        s = p.read_text(encoding='utf-8')
        new = LINE_RE.sub(lambda _: f"var LEADERBOARD_ID = '{lid}';", s, count=1)
        if new == s:
            print(f'  - {app}: already {lid}')
        else:
            p.write_text(new, encoding='utf-8')
            any_change = True
            print(f'  ✓ {app}: wired {lid}')
    sys.exit(0 if not any_change else 0)


if __name__ == '__main__':
    main()
