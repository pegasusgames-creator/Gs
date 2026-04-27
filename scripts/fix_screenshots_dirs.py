#!/usr/bin/env python3
"""
fix_screenshots_dirs.py
- Renames store/screenshots/tablet/tablet-7_*.png → store/screenshots/tablet_7/
- Moves store/screenshots/tablet/tablet-10_*.png → store/screenshots/tablet_10/
- Moves store/screenshots/phone/phone_*.png to be plain 01_, 02_ etc names (no-op if already fine)
- Also renames phone/phone_1-main.png → phone/01_main.png etc. for cleaner names
"""
import os, shutil, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_template", "_release", "__pycache__", ".git", ".idea", "node_modules"}


def fix_app(app):
    app_root = os.path.join(BASE, app)
    ss_root  = os.path.join(app_root, 'store', 'screenshots')
    old_tablet = os.path.join(ss_root, 'tablet')
    new_t7     = os.path.join(ss_root, 'tablet_7')
    new_t10    = os.path.join(ss_root, 'tablet_10')
    phone_dir  = os.path.join(ss_root, 'phone')
    moved = []

    # Split tablet/ into tablet_7/ and tablet_10/
    if os.path.isdir(old_tablet):
        for fname in os.listdir(old_tablet):
            if not fname.lower().endswith('.png'):
                continue
            src = os.path.join(old_tablet, fname)
            if 'tablet-10' in fname or 'tablet10' in fname:
                os.makedirs(new_t10, exist_ok=True)
                dst = os.path.join(new_t10, fname)
                shutil.move(src, dst)
                moved.append(f'tablet/{fname} -> tablet_10/')
            else:
                os.makedirs(new_t7, exist_ok=True)
                dst = os.path.join(new_t7, fname)
                shutil.move(src, dst)
                moved.append(f'tablet/{fname} -> tablet_7/')
        # Remove old empty tablet/ dir
        try:
            os.rmdir(old_tablet)
            moved.append('removed tablet/')
        except OSError:
            pass  # not empty — leave it

    # Rename phone screenshots to canonical 01_main.png, 02_gameplay.png names
    if os.path.isdir(phone_dir):
        pngs = sorted(f for f in os.listdir(phone_dir) if f.lower().endswith('.png'))
        for i, fname in enumerate(pngs, 1):
            # Already properly named?
            if re.match(r'^\d{2}_', fname):
                continue
            # phone_1-main.png → 01_main.png
            new_name = f'{i:02d}_main.png'
            src = os.path.join(phone_dir, fname)
            dst = os.path.join(phone_dir, new_name)
            if src != dst and not os.path.exists(dst):
                shutil.move(src, dst)
                moved.append(f'phone/{fname} -> phone/{new_name}')

    return moved


def list_apps():
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP_DIRS or name.startswith('.'):
            continue
        if not os.path.isdir(os.path.join(BASE, name, 'android')):
            continue
        apps.append(name)
    return apps


import re

if __name__ == '__main__':
    target = sys.argv[1:] if len(sys.argv) > 1 else list_apps()
    total = 0
    for app in target:
        moved = fix_app(app)
        if moved:
            print(f'{app}: {len(moved)} moves')
            total += len(moved)
    print(f'Done — {total} total moves')
