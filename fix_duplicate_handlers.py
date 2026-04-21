#!/usr/bin/env python3
"""Remove duplicate/stub onPurchaseComplete and onAdMobLoaded handlers."""
import os, re

BASE = '/home/pgs/Documents/Gs'

apps = sorted([d for d in os.listdir(BASE)
               if os.path.isdir(f'{BASE}/{d}')
               and os.path.isfile(f'{BASE}/{d}/android/app/src/main/assets/game.html')
               and not d.startswith('_')])

fixed = 0
for app in apps:
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    with open(html_path) as f:
        content = f.read()

    original = content

    # Remove stub onPurchaseComplete (the ones that just console.log or do nothing useful)
    # These are single-line stubs that were the old placeholders
    content = re.sub(
        r"window\.onPurchaseComplete\s*=\s*function\s*\([^)]*\)\s*\{\s*(?:console\.log\([^)]*\)|)\s*\};\s*\n",
        '',
        content
    )

    # Remove legacy onAdMobLoaded (already handled but double-check)
    content = re.sub(
        r"window\.onAdMobLoaded\s*=\s*function\s*\(\)\s*\{[^}]*\};\s*\n?",
        '',
        content
    )

    if content != original:
        with open(html_path, 'w') as f:
            f.write(content)
        fixed += 1

print(f'Fixed duplicate handlers in {fixed} apps')
