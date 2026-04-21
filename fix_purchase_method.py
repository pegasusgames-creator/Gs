#!/usr/bin/env python3
"""Fix apps using Android.purchaseRemoveAds() → Android.purchase('remove_ads')"""
import os, re

BASE = '/home/pgs/Documents/Gs'

apps = ['Binairo','ColorBlockJam','ColorFill','Connections','KnotPuzzle',
        'LightsOut','Mastermind','Minesweeper','NumberLink','NumberMerge','Sudoku']

for app in apps:
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    with open(html_path) as f:
        content = f.read()
    original = content

    # Fix the purchase call
    content = content.replace(
        "Android.purchaseRemoveAds()",
        "Android.purchase('remove_ads')"
    )
    # Fix onPurchaseComplete with no parameter → add parameter
    content = re.sub(
        r"window\.onPurchaseComplete\s*=\s*function\s*\(\s*\)\s*\{",
        "window.onPurchaseComplete = function(sku) {",
        content
    )

    if content != original:
        with open(html_path, 'w') as f:
            f.write(content)
        print(f'{app}: fixed')
    else:
        print(f'{app}: no change needed')

print('Done')
