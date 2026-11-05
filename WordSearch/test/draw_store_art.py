#!/usr/bin/env python3
"""draw_store_art.py — Word Search store icon + feature graphic, drawn from our
own shapes with PIL. Focal element: a paper letter grid with two translucent
highlighter capsules crossing it (WORD across, BIRD up the diagonal) — the
core mechanic at a glance, on the app's heather-dusk palette.

Writes WordSearch/store/icon_512_playstore.png (no alpha),
icon_1024_appstore.png (no alpha) and feature_graphic_1024x500.png.
Then run: python3 scripts/sync_launcher_icons.py WordSearch
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(os.path.dirname(HERE), 'store')
SS = 4  # supersampling
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

HEATHER_A = (239, 230, 240)
HEATHER_B = (214, 190, 222)
PLUM = (139, 63, 135)
PLUM_D = (95, 40, 105)
INDIGO = (106, 59, 156)
PAPER = (255, 252, 248)
INK = (42, 31, 49)
LEMON = (255, 207, 90)
MINT = (127, 209, 187)
ROSE = (245, 159, 179)
SKY = (143, 188, 240)

GRID = ['KETD', 'WORD', 'FINA', 'BLUH']


def font(px):
    return ImageFont.truetype(BOLD, px)


def gradient(w, h, a, b, radial=True):
    img = Image.new('RGB', (w, h))
    px = img.load()
    cx, cy = w * 0.42, h * 0.36
    rmax = math.hypot(max(cx, w - cx), max(cy, h - cy))
    for y in range(h):
        for x in range(w):
            t = math.hypot(x - cx, y - cy) / rmax if radial else y / h
            t = min(1.0, t) ** 1.2
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return img


def capsule(layer, p0, p1, thick, color, alpha):
    """Rounded highlighter stroke from p0 to p1 on an RGBA layer."""
    d = ImageDraw.Draw(layer)
    c = color + (alpha,)
    d.line([p0, p1], fill=c, width=int(thick))
    r = thick / 2
    for (x, y) in (p0, p1):
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)


def paper_card(size, cells, letters, caps, radius_frac=0.16, border=None):
    """Paper card with a letter grid and highlighter capsules (RGBA)."""
    S = size
    card = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    m = Image.new('L', (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * radius_frac), fill=255)
    base = Image.new('RGBA', (S, S), PAPER + (255,))
    # fine dot grain (T3 paper)
    g = ImageDraw.Draw(base)
    step = max(6, S // 90)
    for y in range(0, S, step):
        for x in range((y // step) % 2 * step // 2, S, step):
            g.point((x, y), fill=(225, 214, 226, 255))
    card.paste(base, (0, 0), m)
    pad = S * 0.08
    cs = (S - 2 * pad) / cells
    center = lambda r, c: (pad + (c + 0.5) * cs, pad + (r + 0.5) * cs)
    hl = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    for (r0, c0, r1, c1, col) in caps:
        capsule(hl, center(r0, c0), center(r1, c1), cs * 0.8, col, 200)
    card = Image.alpha_composite(card, Image.composite(hl, Image.new('RGBA', (S, S), (0, 0, 0, 0)), m))
    d = ImageDraw.Draw(card)
    f = font(int(cs * 0.6))
    for r, row in enumerate(letters):
        for c, ch in enumerate(row):
            x, y = center(r, c)
            d.text((x, y), ch, font=f, fill=INK + (255,), anchor='mm')
    if border:
        d.rounded_rectangle([border[1] // 2, border[1] // 2, S - 1 - border[1] // 2, S - 1 - border[1] // 2],
                            radius=int(S * radius_frac), outline=border[0] + (255,), width=border[1])
    return card


def shadow(card, blur, offset, opacity=90):
    a = card.split()[3].point(lambda v: v * opacity // 255)
    sh = Image.new('RGBA', card.size, (60, 20, 70, 0))
    sh.putalpha(a)
    pad = blur * 3
    big = Image.new('RGBA', (card.width + pad * 2, card.height + pad * 2), (0, 0, 0, 0))
    big.paste(sh, (pad + offset[0], pad + offset[1]), sh)
    return big.filter(ImageFilter.GaussianBlur(blur)), pad


def draw_icon(size):
    S = size * SS
    bg = gradient(S // 4, S // 4, HEATHER_A, HEATHER_B).resize((S, S), Image.BICUBIC).convert('RGBA')
    cs = int(S * 0.74)
    caps = [(1, 0, 1, 3, LEMON), (3, 0, 0, 3, MINT)]
    card = paper_card(cs, 4, GRID, caps, border=(PLUM, int(S * 0.022)))
    sh, pad = shadow(card, int(S * 0.025), (0, int(S * 0.022)))
    x = (S - cs) // 2
    y = (S - cs) // 2
    bg.alpha_composite(sh, (x - pad, y - pad))
    bg.alpha_composite(card, (x, y))
    return bg.convert('RGB').resize((size, size), Image.LANCZOS)


def draw_feature():
    W, H = 1024 * SS, 500 * SS
    bg = gradient(W // 8, H // 8, HEATHER_A, HEATHER_B).resize((W, H), Image.BICUBIC).convert('RGBA')
    # loose highlighter motif in the background
    mot = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for (x0, y0, x1, y1, col) in [(560, 70, 760, 40, ROSE), (820, 430, 990, 360, SKY), (600, 455, 700, 470, MINT)]:
        capsule(mot, (x0 * SS, y0 * SS), (x1 * SS, y1 * SS), 26 * SS, col, 70)
    bg = Image.alpha_composite(bg, mot)
    # tilted paper grid (left)
    letters = ['STARFI', 'HCOMET', 'ORBITS', 'MOONUB', 'JEWNIK', 'PLANET']
    LILAC = (191, 160, 234)
    caps = [(0, 0, 0, 3, SKY), (1, 1, 1, 5, ROSE), (2, 0, 2, 4, LEMON), (2, 5, 4, 3, MINT), (5, 0, 5, 5, LILAC)]
    cs = int(H * 0.78)
    card = paper_card(cs, 6, letters, caps, radius_frac=0.07, border=(PLUM, 3 * SS))
    card = card.rotate(-7, resample=Image.BICUBIC, expand=True)
    sh, pad = shadow(card, 14 * SS, (0, 10 * SS))
    cx, cy = int(W * 0.045), (H - card.height) // 2
    bg.alpha_composite(sh, (cx - pad, cy - pad))
    bg.alpha_composite(card, (cx, cy))
    d = ImageDraw.Draw(bg)
    tx = int(W * 0.515)
    avail = int(W * 0.955) - tx
    word = 'WORD SEARCH'
    fs = 90 * SS
    while d.textlength(word, font=font(fs)) > avail:
        fs -= SS
    fw = font(fs)
    tw = d.textlength(word, font=fw)
    ty = int(H * 0.27)
    # wordmark: clean 2-stop plum
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).text((tx, ty), word, font=fw, fill=255)
    grad = Image.new('RGBA', (W, H))
    gp = ImageDraw.Draw(grad)
    for x in range(tx, int(tx + tw) + 2):
        t = (x - tx) / max(1, tw)
        gp.line([(x, 0), (x, H)], fill=tuple(int(PLUM_D[i] + (PLUM[i] - PLUM_D[i]) * t) for i in range(3)) + (255,))
    bg.paste(grad, (0, 0), mask)
    sub = 'Calm themed word puzzles'
    ss = 34 * SS
    while d.textlength(sub, font=font(ss)) > avail:
        ss -= SS
    d.text((tx + 2 * SS, ty + int(fs * 1.25)), sub, font=font(ss), fill=INK)
    px = tx + 2 * SS
    py = ty + int(fs * 1.25) + int(ss * 1.9)
    f = font(22 * SS)
    for label in ['500 levels', '8 directions', 'offline']:
        lw = d.textlength(label, font=f)
        d.rounded_rectangle([px, py, px + lw + 32 * SS, py + 44 * SS], radius=22 * SS, fill=PAPER, outline=(214, 190, 222), width=2 * SS)
        d.text((px + 16 * SS, py + 22 * SS), label, font=f, fill=PLUM_D, anchor='lm')
        px += lw + 44 * SS
    return bg.convert('RGB').resize((1024, 500), Image.LANCZOS)


if __name__ == '__main__':
    draw_icon(512).save(os.path.join(STORE, 'icon_512_playstore.png'))
    draw_icon(1024).save(os.path.join(STORE, 'icon_1024_appstore.png'))
    draw_feature().save(os.path.join(STORE, 'feature_graphic_1024x500.png'))
    print('wrote icon_512_playstore.png, icon_1024_appstore.png, feature_graphic_1024x500.png')
