#!/usr/bin/env python3
"""Remove stub onPurchaseComplete lines (single-line with console.log)."""
import os, re

BASE = '/home/pgs/Documents/Gs'

apps = ['AnagramFinder','BoggleGame','Cryptogram','GhostWord','Hangman',
        'SpellingBee','WordConnect','WordLadder','WordleClone']

for app in apps:
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    with open(html_path) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Skip the stub one-liner
        if re.match(r"\s*window\.onPurchaseComplete\s*=\s*function\s*\([^)]*\)\s*\{\s*console\.log\([^)]*\)\s*\};\s*$", line):
            continue
        new_lines.append(line)

    with open(html_path, 'w') as f:
        f.writelines(new_lines)
    print(f'{app}: cleaned')

print('Done')
