#!/usr/bin/env python3
"""
gen_appstore_icon.py
Generates store/icon_1024_appstore.png (1024x1024, no alpha) for all apps.
Scales from the existing 512x512 icon using high-quality upscaling.
Falls back to regenerating from scratch if 512 icon missing.
"""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_template", "_release", "__pycache__", ".git", ".idea", "node_modules"}

FONT_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FONT_REG  = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'

# Gradient palettes keyed by first letter of app name
PALETTES = [
    ((41, 128, 185), (142, 68, 173)),  # blue-purple
    ((39, 174, 96),  (26, 188, 156)),  # green-teal
    ((231, 76, 60),  (241, 196, 15)),  # red-yellow
    ((52, 73, 94),   (44, 62, 80)),    # dark slate
    ((230, 126, 34), (211, 84, 0)),    # orange
    ((41, 182, 246), (2, 136, 209)),   # light blue
    ((156, 39, 176), (233, 30, 99)),   # purple-pink
    ((0, 188, 212),  (0, 150, 136)),   # cyan-teal
]

def palette_for(app):
    idx = ord(app[0].upper()) % len(PALETTES)
    # shift by hash of full name for variety
    idx = (idx + len(app)) % len(PALETTES)
    return PALETTES[idx]

def initials(app):
    parts = re.findall(r'[A-Z][a-z]*', app)
    if len(parts) >= 2:
        return parts[0][0] + parts[1][0]
    return app[:2].upper()

def make_gradient(size, c1, c2):
    img = Image.new('RGB', (size, size))
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        for x in range(size):
            px[x, y] = (r, g, b)
    return img

def gen_icon_1024(app):
    src = os.path.join(BASE, app, 'store', 'icon_512_playstore.png')
    dst = os.path.join(BASE, app, 'store', 'icon_1024_appstore.png')

    if os.path.exists(dst):
        return f'{app}: already exists'

    if os.path.exists(src):
        # Scale up the 512x512 icon with high-quality resampling
        img = Image.open(src).convert('RGB')
        img = img.resize((1024, 1024), Image.LANCZOS)
        img.save(dst, 'PNG', optimize=True)
        return f'{app}: scaled from 512'
    else:
        # Regenerate from scratch
        c1, c2 = palette_for(app)
        img = make_gradient(1024, c1, c2)
        draw = ImageDraw.Draw(img)

        # Large initials
        letters = initials(app)
        try:
            font_big = ImageFont.truetype(FONT_BOLD, 380)
        except Exception:
            font_big = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), letters, font=font_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (1024 - tw) // 2 - bbox[0]
        y = (1024 - th) // 2 - bbox[1] - 60
        # Shadow
        draw.text((x + 6, y + 6), letters, fill=(0, 0, 0, 80), font=font_big)
        draw.text((x, y), letters, fill=(255, 255, 255), font=font_big)

        # App name below
        name_display = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', app)
        try:
            font_sm = ImageFont.truetype(FONT_REG, 70)
        except Exception:
            font_sm = ImageFont.load_default()
        nb = draw.textbbox((0, 0), name_display, font=font_sm)
        nx = (1024 - (nb[2] - nb[0])) // 2
        ny = y + th + 40
        draw.text((nx, ny), name_display, fill=(255, 255, 255, 200), font=font_sm)

        img.save(dst, 'PNG', optimize=True)
        return f'{app}: generated from scratch'

def list_apps():
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP_DIRS or name.startswith('.'):
            continue
        if not os.path.isdir(os.path.join(BASE, name, 'android')):
            continue
        apps.append(name)
    return apps

if __name__ == '__main__':
    target = sys.argv[1:] if len(sys.argv) > 1 else list_apps()
    for app in target:
        print(gen_icon_1024(app))
    print('Done')
