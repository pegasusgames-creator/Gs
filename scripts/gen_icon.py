#!/usr/bin/env python3
"""Generate WaterSort Puzzle icon with 3 tilted flasks showing colored liquids."""
import math, os
from PIL import Image, ImageDraw, ImageFilter

SUPER = 3
SIZE = 1024 * SUPER

OUT_SIZES = [(512, 'icon_512_playstore.png'),
             (1024, 'icon_1024_appstore.png')]

C_RED    = (239, 58, 71)
C_ORANGE = (255, 111, 0)
C_YELLOW = (255, 193, 7)
C_GREEN  = (67, 199, 89)
C_CYAN   = (0, 188, 212)
C_BLUE   = (33, 150, 243)
C_PURPLE = (156, 39, 176)
C_PINK   = (233, 30, 99)

BG_TOP    = (8, 25, 44)
BG_MID    = (18, 55, 85)
BG_CENTER = (25, 88, 120)

GLASS = (235, 248, 255)


def radial_bg(size):
    w = size
    img = Image.new('RGB', (w, w), BG_TOP)
    cx = w // 2
    cy = int(w * 0.55)
    max_r = int(math.sqrt(cx * cx + (w - cy) ** 2) * 1.15)

    bright = Image.new('RGB', (w, w), BG_CENTER)
    mid_layer = Image.new('RGB', (w, w), BG_MID)

    cmask = Image.new('L', (w, w), 0)
    cd = ImageDraw.Draw(cmask)
    steps = 80
    for i in range(steps):
        t = i / steps
        r = int(max_r * 0.45 * (1 - t))
        a = int(180 * (1 - t) * (1 - t))
        cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)

    mmask = Image.new('L', (w, w), 0)
    md = ImageDraw.Draw(mmask)
    for i in range(steps):
        t = i / steps
        r = int(max_r * (0.9 - t * 0.4))
        a = int(255 * t * t)
        md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255 - a)

    img = Image.composite(mid_layer, img, mmask)
    img = Image.composite(bright, img, cmask)
    return img


def draw_flask_on_layer(width, height, layers_colors, padding=80):
    lw = width + padding * 2
    lh = height + padding * 2
    img = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    x0 = padding
    y0 = padding
    x1 = padding + width
    y1 = padding + height

    corner_r = int(width * 0.48)
    rim_h    = int(height * 0.04)
    rim_overhang = int(width * 0.06)
    wall_t   = int(width * 0.07)
    outline_w = max(3, int(width * 0.06))

    inner_x0 = x0 + wall_t
    inner_x1 = x1 - wall_t
    inner_y0 = y0 + rim_h + wall_t // 2
    inner_y1 = y1 - wall_t
    inner_r  = max(0, corner_r - wall_t)

    liquid_mask = Image.new('L', (lw, lh), 0)
    lmd = ImageDraw.Draw(liquid_mask)
    lmd.rounded_rectangle([inner_x0, inner_y0, inner_x1, inner_y1],
                          radius=inner_r, fill=255)

    liquid_img = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    lid = ImageDraw.Draw(liquid_img)
    n = len(layers_colors)
    cell_h = (inner_y1 - inner_y0) / 4.0
    start_y = inner_y1 - n * cell_h

    for i, color in enumerate(layers_colors):
        band_top = start_y + i * cell_h
        band_bot = band_top + cell_h
        lid.rectangle([inner_x0 - 2, band_top, inner_x1 + 2, band_bot + 2],
                      fill=(*color, 255))
        hl_h = cell_h * 0.15
        lighter = tuple(min(255, int(c * 1.3)) for c in color)
        lid.rectangle([inner_x0 - 2, band_top, inner_x1 + 2, band_top + hl_h],
                      fill=(*lighter, 180))
        sh_h = cell_h * 0.12
        darker = tuple(max(0, int(c * 0.75)) for c in color)
        lid.rectangle([inner_x0 - 2, band_bot - sh_h, inner_x1 + 2, band_bot + 2],
                      fill=(*darker, 150))

    clipped = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    clipped.paste(liquid_img, (0, 0), liquid_mask)
    img.alpha_composite(clipped)

    d.rounded_rectangle([x0, y0 + rim_h, x1, y1],
                        radius=corner_r, outline=GLASS, width=outline_w)
    d.rounded_rectangle(
        [x0 - rim_overhang, y0, x1 + rim_overhang, y0 + rim_h * 2],
        radius=rim_h, outline=GLASS, width=outline_w
    )

    shine = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    shine_w = max(4, int(width * 0.09))
    shine_x = x0 + int(width * 0.18)
    shine_y1 = y0 + rim_h + int(height * 0.08)
    shine_y2 = y0 + int(height * 0.72)
    sd.rounded_rectangle([shine_x, shine_y1, shine_x + shine_w, shine_y2],
                         radius=shine_w // 2, fill=(255, 255, 255, 80))
    shine = shine.filter(ImageFilter.GaussianBlur(radius=3))
    img.alpha_composite(shine)

    glimmer = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glimmer)
    g_w = int(width * 0.4)
    gx = x0 + int(width * 0.35)
    gy = y0 + int(rim_h * 0.4)
    gd.rounded_rectangle([gx, gy, gx + g_w, gy + max(3, outline_w // 2)],
                         radius=2, fill=(255, 255, 255, 200))
    glimmer = glimmer.filter(ImageFilter.GaussianBlur(radius=2))
    img.alpha_composite(glimmer)

    return img


def draw_droplet(canvas, x, y, color, size):
    glow = Image.new('RGBA', (size * 6, size * 6), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([size, size, size * 5, size * 5], fill=(*color, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=size))
    canvas.alpha_composite(glow, (x - size * 3, y - size * 3))

    d = ImageDraw.Draw(canvas)
    d.ellipse([x - size, y - int(size * 0.85), x + size, y + int(size * 1.0)],
              fill=(*color, 255))
    hr = int(size * 0.4)
    d.ellipse([x - hr, y - int(size * 0.5), x - hr + hr, y - int(size * 0.5) + hr],
              fill=(255, 255, 255, 200))


def draw_bubbles(canvas, size):
    d = ImageDraw.Draw(canvas)
    bubbles = [
        (0.08, 0.14, 0.038),
        (0.90, 0.10, 0.028),
        (0.04, 0.72, 0.050),
        (0.94, 0.80, 0.034),
        (0.18, 0.94, 0.022),
        (0.82, 0.48, 0.020),
        (0.06, 0.48, 0.016),
        (0.95, 0.30, 0.014),
    ]
    for bx, by, br in bubbles:
        x = int(size * bx); y = int(size * by); r = int(size * br)
        w = max(2, r // 8)
        d.ellipse([x - r, y - r, x + r, y + r],
                  outline=(255, 255, 255, 40), width=w)


def build_icon():
    print(f'Rendering at {SIZE}x{SIZE}...')
    canvas = radial_bg(SIZE).convert('RGBA')
    draw_bubbles(canvas, SIZE)

    fw = int(SIZE * 0.22)
    fh = int(SIZE * 0.56)

    left = draw_flask_on_layer(
        fw, fh,
        [C_BLUE, C_CYAN, C_GREEN],
        padding=int(fw * 0.3)
    )
    left = left.rotate(-10, resample=Image.BICUBIC, expand=False)
    lx = int(SIZE * 0.20) - left.width // 2
    ly = int(SIZE * 0.50) - left.height // 2
    canvas.alpha_composite(left, (lx, ly))

    right = draw_flask_on_layer(
        fw, fh,
        [C_YELLOW, C_ORANGE, C_RED],
        padding=int(fw * 0.3)
    )
    right = right.rotate(18, resample=Image.BICUBIC, expand=False)
    rx = int(SIZE * 0.80) - right.width // 2
    ry = int(SIZE * 0.48) - right.height // 2
    canvas.alpha_composite(right, (rx, ry))

    for dx_frac, dy_frac, color, sz_frac in [
        (0.66, 0.30, C_RED,    0.014),
        (0.61, 0.24, C_RED,    0.010),
        (0.69, 0.37, C_ORANGE, 0.013),
        (0.57, 0.20, C_RED,    0.008),
    ]:
        draw_droplet(canvas, int(SIZE * dx_frac), int(SIZE * dy_frac),
                     color, int(SIZE * sz_frac))

    fw_mid = int(SIZE * 0.26)
    fh_mid = int(SIZE * 0.66)
    middle = draw_flask_on_layer(
        fw_mid, fh_mid,
        [C_PURPLE, C_PINK, C_RED, C_ORANGE],
        padding=int(fw_mid * 0.2)
    )
    mx = SIZE // 2 - middle.width // 2
    my = int(SIZE * 0.56) - middle.height // 2
    canvas.alpha_composite(middle, (mx, my))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'WaterSortPuzzle', 'store')
    os.makedirs(out_dir, exist_ok=True)
    for target_size, name in OUT_SIZES:
        out = canvas.resize((target_size, target_size), Image.LANCZOS)
        flat = Image.new('RGB', (target_size, target_size), BG_TOP)
        flat.paste(out, mask=out.split()[3])
        path = os.path.join(out_dir, name)
        flat.save(path, 'PNG', optimize=True)
        print(f'  wrote {path} ({os.path.getsize(path) // 1024} KB)')


if __name__ == '__main__':
    build_icon()
