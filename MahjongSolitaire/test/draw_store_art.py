#!/usr/bin/env python3
"""draw_store_art.py — Mahjong Solitaire store icon + feature graphic, drawn
from our own shapes with PIL (no third-party tile art, no fonts with glyph
art). Focal element: ivory tiles on jade backs with the matching free pair lit
in gold — the core mechanic at a glance.

Writes MahjongSolitaire/store/icon_512_playstore.png (no alpha),
icon_1024_appstore.png (no alpha) and feature_graphic_1024x500.png.
Then run: python3 scripts/sync_launcher_icons.py MahjongSolitaire
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(os.path.dirname(HERE), 'store')
SS = 4  # supersampling

HONEY_A = (226, 192, 132)
HONEY_B = (196, 150, 88)
JADE = (47, 138, 104)
JADE_D = (29, 106, 78)
BONE = (239, 227, 198)
FACE = (255, 250, 240)
FACE2 = (243, 233, 210)
GOLD = (217, 142, 4)
RED = (192, 57, 43)
BLUE = (31, 94, 156)
GREEN = (36, 131, 74)
GREEN_D = (21, 92, 49)
INK = (43, 33, 22)


def wood(w, h, seed=7):
    """Radial honey gradient + soft vertical grain."""
    sw, sh = max(8, w // 8), max(8, h // 8)
    img = Image.new('RGB', (sw, sh))
    px = img.load()
    cx, cy = sw * 0.5, sh * 0.32
    rmax = math.hypot(max(cx, sw - cx), max(cy, sh - cy))
    for y in range(sh):
        for x in range(sw):
            t = min(1.0, math.hypot(x - cx, y - cy) / rmax)
            px[x, y] = tuple(int(HONEY_A[i] + (HONEY_B[i] - HONEY_A[i]) * t) for i in range(3))
    img = img.resize((w, h), Image.BICUBIC)
    g = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(g)
    rnd = random.Random(seed)
    x = 0
    while x < w:
        x += rnd.randint(int(w / 70) + 2, int(w / 28) + 3)
        d.line([(x + rnd.randint(-3, 3), 0), (x + rnd.randint(-8, 8), h)], fill=rnd.randint(10, 26), width=max(1, w // 400))
    g = g.filter(ImageFilter.GaussianBlur(max(1, w // 500)))
    dark = Image.new('RGB', (w, h), (90, 56, 20))
    return Image.composite(dark, img, g)


def tile(img, x, y, w, glow=False, face=None):
    """One tile at (x, y) top-left, width w: soft shadow (+ gold glow when lit),
    jade back, bone layer, ivory face."""
    h = int(w * 1.32)
    d = int(w * 0.11)
    r = int(w * 0.14)
    m = int(w * 0.35)
    lay = Image.new('RGBA', (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([m + d * 0.5, m + d * 0.9, m + w + d * 0.7, m + h + d * 1.0], r, fill=(60, 36, 10, 120))
    lay = lay.filter(ImageFilter.GaussianBlur(w * 0.05))
    if glow:
        gl = Image.new('RGBA', lay.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.rounded_rectangle([m - w * 0.05, m - w * 0.05, m + w - d + w * 0.05, m + h - d + w * 0.05], r + 6, fill=GOLD + (215,))
        gl = gl.filter(ImageFilter.GaussianBlur(w * 0.07))
        lay.alpha_composite(gl)
    img.alpha_composite(lay, (int(x - m), int(y - m)))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x, y, x + w, y + h], r, fill=JADE_D)
    draw.rounded_rectangle([x, y, x + w - d * 0.35, y + h - d * 0.35], r, fill=JADE)
    draw.rounded_rectangle([x, y, x + w - d * 0.55, y + h - d * 0.55], r, fill=BONE)
    fw, fh = w - d, h - d
    draw.rounded_rectangle([x, y, x + fw, y + fh], r, fill=FACE, outline=(GOLD if glow else (150, 128, 96)),
                           width=(max(4, w // 15) if glow else max(2, w // 90)))
    if face:
        face(draw, x, y, fw, fh)
    return h


def leaf(draw, bx, by, length, width, ang, col):
    """Pointed leaf from base (bx, by) along angle ang (degrees, 0 = up)."""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    pts = []
    for side in (1, -1):
        rng = range(0, 21) if side == 1 else range(20, -1, -1)
        for k in rng:
            t = k / 20.0
            off = math.sin(math.pi * t) ** 0.8 * width / 2 * side
            pts.append((bx + ux * length * t + nx * off, by + uy * length * t + ny * off))
    draw.polygon(pts, fill=col)


def face_target(draw, x, y, fw, fh):
    cx, cy, rr = x + fw / 2, y + fh / 2, fw * 0.3
    draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=RED)
    r2 = rr * 0.58
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=FACE, width=max(2, int(rr * 0.2)))
    r3 = rr * 0.2
    draw.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=FACE)


def face_sprout(draw, x, y, fw, fh):
    cx = x + fw / 2
    s = fw / 60.0
    draw.line([(cx, y + fh * 0.9), (cx, y + fh * 0.3)], fill=GREEN_D, width=max(3, int(4.5 * s)))
    leaf(draw, cx, y + fh * 0.60, 24 * s, 11 * s, -48, GREEN)
    leaf(draw, cx, y + fh * 0.50, 22 * s, 10 * s, 46, GREEN)
    leaf(draw, cx, y + fh * 0.78, 18 * s, 9 * s, -60, GREEN)
    rr = 7.5 * s
    draw.ellipse([cx - rr, y + fh * 0.24 - rr, cx + rr, y + fh * 0.24 + rr], fill=RED)


def face_dots2(draw, x, y, fw, fh):
    for (fy, col) in ((0.3, BLUE), (0.7, GREEN)):
        cx, cy, rr = x + fw / 2, y + fh * fy, fw * 0.18
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
        r2 = rr * 0.56
        draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=FACE, width=max(2, int(rr * 0.2)))


def face_bamboo3(draw, x, y, fw, fh):
    s = fw / 60.0
    for (fx, fy) in ((0.5, 0.3), (0.3, 0.7), (0.7, 0.7)):
        cx, cy, hh, ww = x + fw * fx, y + fh * fy, 26 * s, 8 * s
        draw.rounded_rectangle([cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2], ww / 2, fill=GREEN)
        draw.line([(cx - ww / 2, cy), (cx + ww / 2, cy)], fill=FACE, width=max(1, int(1.6 * s)))


def icon(size):
    S = size * SS
    img = wood(S, S).convert('RGBA')
    w = int(S * 0.34)
    # lower pair (matching, lit) + one raised tile between them
    gx = int(S * 0.5 - w - S * 0.012)
    y0 = int(S * 0.40)
    tile(img, gx, y0, w, glow=True, face=face_target)
    tile(img, gx + w + int(S * 0.024), y0, w, glow=True, face=face_target)
    tile(img, int(S * 0.5 - w * 0.47), int(S * 0.13), w, face=face_sprout)
    out = img.resize((size, size), Image.LANCZOS).convert('RGB')
    return out


def feature():
    W, H = 1024 * 2, 500 * 2
    img = wood(W, H, seed=11).convert('RGBA')
    d = ImageDraw.Draw(img)
    # a small stacked layout on the right: 3x2 base, two straddling tiles, one apex
    w = 212
    hh = int(w * 1.32)
    bx, by = 1230, 212
    base = [(0, 0, face_target, True), (1, 0, face_bamboo3, False), (2, 0, face_dots2, False),
            (0, 1, face_dots2, False), (1, 1, face_bamboo3, False), (2, 1, face_target, True)]
    for (c, r, f, lit) in base:
        tile(img, bx + c * w, by + r * hh, w, glow=lit, face=f)
    dz = int(w * 0.11)
    for (c, f) in ((0.5, face_sprout), (1.5, face_dots2)):
        tile(img, int(bx + c * w - dz), int(by + 0.5 * hh - dz), w, face=f)
    tile(img, int(bx + w - 2 * dz), int(by + 0.5 * hh - 2 * dz), w, face=face_sprout)
    d = ImageDraw.Draw(img)
    # wordmark
    try:
        f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 112)
        f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 48)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((110, 300), 'Mahjong', font=f1, fill=(21, 90, 67))
    d.text((110, 430), 'Solitaire', font=f1, fill=(21, 90, 67))
    d.text((114, 600), 'Big, clear tiles. 500 calm deals.', font=f2, fill=INK)
    d.text((114, 668), 'Every one can be cleared.', font=f2, fill=INK)
    return img.resize((1024, 500), Image.LANCZOS).convert('RGB')


if __name__ == '__main__':
    os.makedirs(STORE, exist_ok=True)
    icon(512).save(os.path.join(STORE, 'icon_512_playstore.png'))
    icon(1024).save(os.path.join(STORE, 'icon_1024_appstore.png'))
    feature().save(os.path.join(STORE, 'feature_graphic_1024x500.png'))
    print('wrote icon_512_playstore.png, icon_1024_appstore.png, feature_graphic_1024x500.png')
