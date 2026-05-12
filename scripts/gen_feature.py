#!/usr/bin/env python3
"""
Generate WaterSort Puzzle feature graphic (1024x500).

Design per QUALITY_PLAYBOOK §7.1-7.2:
- Single dramatic scene (mid-pour action, not menu)
- Text kept small and in corner
- No emojis (Unicode glyphs only where they render reliably)
- Colors match app theme
- Clean composition drawing eye to ONE focal element
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Render at 2x for sharp downsampling
SUPER = 2
W = 1024 * SUPER
H = 500 * SUPER

C_RED    = (239, 58, 71)
C_ORANGE = (255, 111, 0)
C_YELLOW = (255, 193, 7)
C_GREEN  = (67, 199, 89)
C_CYAN   = (0, 188, 212)
C_BLUE   = (33, 150, 243)
C_PURPLE = (156, 39, 176)
C_PINK   = (233, 30, 99)

BG_TOP    = (8, 25, 44)
BG_MID    = (16, 52, 82)
BG_RIGHT  = (22, 75, 105)

GLASS = (235, 248, 255)

def _first_existing(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]  # let PIL raise if truly nothing is available

FONT_REG  = _first_existing(
    '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
FONT_LITE = _first_existing(
    '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')


def gradient_bg():
    """Horizontal gradient, slightly brighter on the right (where text lives)."""
    img = Image.new('RGB', (W, H), BG_TOP)
    px = img.load()
    # Linear horizontal gradient with vertical darkening near top/bottom
    for x in range(W):
        t = x / W  # 0 left, 1 right
        # lerp between BG_TOP (left) and BG_RIGHT (right) with midpoint BG_MID
        if t < 0.5:
            tt = t / 0.5
            r = int(BG_TOP[0] + (BG_MID[0] - BG_TOP[0]) * tt)
            g = int(BG_TOP[1] + (BG_MID[1] - BG_TOP[1]) * tt)
            b = int(BG_TOP[2] + (BG_MID[2] - BG_TOP[2]) * tt)
        else:
            tt = (t - 0.5) / 0.5
            r = int(BG_MID[0] + (BG_RIGHT[0] - BG_MID[0]) * tt)
            g = int(BG_MID[1] + (BG_RIGHT[1] - BG_MID[1]) * tt)
            b = int(BG_MID[2] + (BG_RIGHT[2] - BG_MID[2]) * tt)
        for y in range(H):
            # Slight vertical vignette
            vy = abs(y - H / 2) / (H / 2)
            darken = 1 - 0.12 * vy * vy
            px[x, y] = (int(r * darken), int(g * darken), int(b * darken))
    return img


def gradient_bg_fast():
    """Faster: build a 1-pixel-wide gradient strip and stretch."""
    strip = Image.new('RGB', (W, 1))
    sp = strip.load()
    for x in range(W):
        t = x / W
        if t < 0.5:
            tt = t / 0.5
            c = tuple(int(BG_TOP[i] + (BG_MID[i] - BG_TOP[i]) * tt) for i in range(3))
        else:
            tt = (t - 0.5) / 0.5
            c = tuple(int(BG_MID[i] + (BG_RIGHT[i] - BG_MID[i]) * tt) for i in range(3))
        sp[x, 0] = c
    img = strip.resize((W, H), Image.NEAREST)

    # Add vertical vignette
    vig = Image.new('L', (W, H), 0)
    vd = ImageDraw.Draw(vig)
    cx, cy = W // 2, H // 2
    steps = 40
    for i in range(steps):
        t = i / steps
        rx = int(W * 0.7 * (1 - t * 0.3))
        ry = int(H * 0.9 * (1 - t * 0.3))
        a = int(60 * t * t)
        vd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255 - a)
    dark = Image.new('RGB', (W, H), BG_TOP)
    img = Image.composite(img, dark, vig)
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


def draw_bubbles(canvas):
    """Decorative circles scattered around."""
    d = ImageDraw.Draw(canvas)
    bubbles = [
        (0.05, 0.18, 35),
        (0.08, 0.78, 50),
        (0.14, 0.42, 22),
        (0.22, 0.92, 18),
        (0.95, 0.15, 30),
        (0.97, 0.70, 40),
        (0.60, 0.90, 15),
        (0.72, 0.12, 25),
        (0.85, 0.88, 20),
        (0.44, 0.08, 18),
    ]
    for bx, by, br in bubbles:
        x = int(W * bx); y = int(H * by); r = br * SUPER
        d.ellipse([x - r, y - r, x + r, y + r],
                  outline=(255, 255, 255, 40), width=max(2, r // 12))


def build_feature_graphic():
    print(f'Rendering at {W}x{H}...')
    canvas = gradient_bg_fast().convert('RGBA')
    draw_bubbles(canvas)

    # ----------- LEFT HALF: flasks with mid-pour action -----------

    # Hero flask — center-left, largest
    fw_hero = int(H * 0.32)
    fh_hero = int(H * 0.70)
    hero = draw_flask_on_layer(
        fw_hero, fh_hero,
        [C_PURPLE, C_PINK, C_RED, C_ORANGE],
        padding=int(fw_hero * 0.2)
    )
    hx = int(W * 0.26) - hero.width // 2
    hy = H // 2 - hero.height // 2
    canvas.alpha_composite(hero, (hx, hy))

    # Left small flask — behind, smaller, tilted
    fw_left = int(H * 0.24)
    fh_left = int(H * 0.55)
    left = draw_flask_on_layer(
        fw_left, fh_left,
        [C_BLUE, C_CYAN, C_GREEN],
        padding=int(fw_left * 0.3)
    )
    left = left.rotate(-12, resample=Image.BICUBIC, expand=False)
    lx = int(W * 0.09) - left.width // 2
    ly = int(H * 0.52) - left.height // 2
    canvas.alpha_composite(left, (lx, ly))

    # Right tilted flask — mid-pour
    fw_right = int(H * 0.26)
    fh_right = int(H * 0.62)
    right = draw_flask_on_layer(
        fw_right, fh_right,
        [C_YELLOW, C_ORANGE, C_RED],
        padding=int(fw_right * 0.35)
    )
    right = right.rotate(35, resample=Image.BICUBIC, expand=False)
    rx = int(W * 0.42) - right.width // 2
    ry = int(H * 0.40) - right.height // 2
    canvas.alpha_composite(right, (rx, ry))

    # Stream of droplets from right-tilted flask arcing toward the hero
    stream = [
        (0.37, 0.40, C_RED,    0.020),
        (0.34, 0.37, C_RED,    0.016),
        (0.31, 0.36, C_RED,    0.012),
        (0.28, 0.38, C_ORANGE, 0.015),
        (0.38, 0.46, C_ORANGE, 0.013),
        (0.40, 0.52, C_RED,    0.010),
    ]
    for dx, dy, color, sz in stream:
        draw_droplet(canvas, int(W * dx), int(H * dy),
                     color, int(H * sz))

    # ----------- RIGHT HALF: title + tagline -----------
    d = ImageDraw.Draw(canvas)

    # Title "WATER SORT PUZZLE" — stacked, right-aligned-ish, consistent color
    title_font_big = ImageFont.truetype(FONT_REG, 120 * SUPER // 2)
    subtitle_font   = ImageFont.truetype(FONT_LITE, 32 * SUPER // 2)
    tag_font        = ImageFont.truetype(FONT_REG, 24 * SUPER // 2)

    # Measure and position "WATER"
    title_x = int(W * 0.56)
    title_y = int(H * 0.22)
    line_gap = 8 * SUPER

    lines = ['WATER', 'SORT', 'PUZZLE']
    colors_per_line = [
        (79, 195, 247),   # cyan (matches app accent)
        (105, 240, 174),  # mint green
        (255, 215, 0),    # gold
    ]

    y = title_y
    for line, color in zip(lines, colors_per_line):
        # Soft shadow for depth
        d.text((title_x + 4 * SUPER, y + 4 * SUPER), line,
               font=title_font_big, fill=(0, 0, 0, 100))
        d.text((title_x, y), line, font=title_font_big, fill=color)
        # Next line
        bbox = title_font_big.getbbox(line)
        y += (bbox[3] - bbox[1]) + line_gap

    # Tagline below title
    tagline = 'Sort the colors. Clear your mind.'
    tag_y = y + 18 * SUPER
    d.text((title_x, tag_y), tagline, font=subtitle_font, fill=(230, 240, 255, 255))

    # Feature badge below tagline — ASCII only, no Unicode glyphs that might
    # render as boxes. Poppins includes middle dot U+00B7 reliably so keep it.
    badge = '500 LEVELS   ·   DAILY CHALLENGE   ·   NO WI-FI NEEDED'
    badge_y = tag_y + 60 * SUPER // 2 + 20 * SUPER
    d.text((title_x, badge_y), badge, font=tag_font, fill=(255, 215, 0, 255))

    # Downsample to final dimensions
    out_w, out_h = 1024, 500
    out = canvas.resize((out_w, out_h), Image.LANCZOS)
    flat = Image.new('RGB', (out_w, out_h), BG_TOP)
    flat.paste(out, mask=out.split()[3])
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'WaterSortPuzzle', 'store')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'feature_graphic_1024x500.png')
    flat.save(path, 'PNG', optimize=True)
    print(f'  wrote {path} ({os.path.getsize(path) // 1024} KB)')


if __name__ == '__main__':
    build_feature_graphic()
