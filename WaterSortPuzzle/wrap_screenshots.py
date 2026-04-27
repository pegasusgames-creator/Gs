#!/usr/bin/env python3
"""
wrap_screenshots.py

Takes raw device screenshots from store/screenshots/phone/ and produces
marketing-wrapped versions at 1080x2400 for the Play Store listing.

Design (per QUALITY_PLAYBOOK.md §7.1-7.2):
- Vibrant gradient background (teal/aqua matching app theme)
- Large Poppins Bold headline at the top (≤5 words, no prohibited marketing phrases)
- Raw screenshot centered below with subtle phone-frame treatment
- Small branded footer strip with tagline
- Consistent visual language across all 7 screenshots

Usage:
    python3 wrap_screenshots.py

Inputs:  store/screenshots/phone/01_main.png through 07_main.png
Outputs: store/screenshots/phone_wrapped/01_hero.png through 07_*.png

Outputs go to a NEW folder so you can compare before/after and decide
which set to upload. Replace the phone/ folder contents if you're happy.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------- paths ----------------------
HERE       = os.path.dirname(os.path.abspath(__file__))
STORE_DIR  = os.path.join(HERE, 'store', 'screenshots')
SRC_DIR    = os.path.join(STORE_DIR, 'phone')
OUT_DIR    = os.path.join(STORE_DIR, 'phone_wrapped')

# ---------------------- dimensions ----------------------
# Play Store recommended phone screenshot size
OUT_W = 1080
OUT_H = 2400

# Render at 2x supersampling for crisp text + downsample
S = 2
W = OUT_W * S
H = OUT_H * S

# ---------------------- theme ----------------------
# Brighter teal gradient for marketing frames (not as dark as the app itself)
# This is important — the Play Store grid looks washed if every screenshot
# is pure near-black.
BG_TOP_LEFT  = (14, 49, 82)     # slightly brighter than app
BG_TOP_RIGHT = (12, 70, 105)
BG_BOT       = (6, 28, 50)       # darker at bottom for depth

# Text colors matching the app's accent family
TEXT_PRIMARY   = (255, 255, 255)
TEXT_ACCENT    = (105, 240, 174)   # mint green (matches app title gradient)
TEXT_SUB       = (200, 220, 240)
FOOTER_TINT    = (79, 195, 247)    # cyan

# ---------------------- fonts ----------------------
# Try fonts in this order (Linux / mac / fallback)
FONT_CANDIDATES = {
    'heavy': [
        '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
        '/Library/Fonts/Poppins-Bold.ttf',
        'Poppins-Bold.ttf',
    ],
    'medium': [
        '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
        '/Library/Fonts/Poppins-Medium.ttf',
        'Poppins-Medium.ttf',
    ],
    'regular': [
        '/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf',
        '/Library/Fonts/Poppins-Regular.ttf',
        'Poppins-Regular.ttf',
    ],
}


def pick_font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    # Fallback: default PIL font (ugly but won't crash)
    print(f'WARNING: could not find Poppins-{kind}. Using default.')
    return ImageFont.load_default()


# ---------------------- marketing plan ----------------------
# One headline per screenshot. Kept under 5 words, no banned phrases
# (QUALITY_PLAYBOOK.md §7.2): no "#1", "Best", "Top", "Download Now",
# "Install Now", "% off", etc. Just clear, punchy, accurate.
#
# The source index determines the order — this is ALSO the reorder step.
# Lead with gameplay (former #3 and #2), then emotional payoff (#7),
# then content variety, then menu last (#1).

SCREENSHOTS = [
    # (source_filename,        output_filename,              headline_line1,       headline_line2,       subtitle)
    ('03_main.png',            '01_gameplay_deep.png',       'POUR',               'AND SORT',           '500 hand-crafted levels'),
    ('02_main.png',            '02_gameplay_early.png',      'RELAX',              'YOUR MIND',          'No timer. No pressure.'),
    ('07_main.png',            '03_level_complete.png',      'EARN',               'YOUR STARS',         'Beat the par. Be the best.'),
    ('04_main.png',            '04_daily_missions.png',      'DAILY',              'MISSIONS',           'Fresh goals every day'),
    ('05_main.png',            '05_stats.png',               'TRACK',              'YOUR STREAK',        'Build a daily habit'),
    ('06_main.png',            '06_levels.png',              '500',                'LEVELS',             'From easy to expert'),
    ('01_main.png',            '07_menu.png',                'PLAY',               'OFFLINE',            'No Wi-Fi needed'),
]

# ---------------------- helpers ----------------------

def make_gradient_bg():
    """Build a smooth diagonal gradient background with subtle bubble decoration."""
    bg = Image.new('RGB', (W, H), BG_TOP_LEFT)
    px = bg.load()
    for y in range(H):
        ty = y / H
        for x in range(W):
            tx = x / W
            # Diagonal gradient
            td = tx * 0.35 + ty * 0.65
            # lerp
            if td < 0.55:
                t = td / 0.55
                r = int(BG_TOP_LEFT[0] + (BG_TOP_RIGHT[0] - BG_TOP_LEFT[0]) * t)
                g = int(BG_TOP_LEFT[1] + (BG_TOP_RIGHT[1] - BG_TOP_LEFT[1]) * t)
                b = int(BG_TOP_LEFT[2] + (BG_TOP_RIGHT[2] - BG_TOP_LEFT[2]) * t)
            else:
                t = (td - 0.55) / 0.45
                r = int(BG_TOP_RIGHT[0] + (BG_BOT[0] - BG_TOP_RIGHT[0]) * t)
                g = int(BG_TOP_RIGHT[1] + (BG_BOT[1] - BG_TOP_RIGHT[1]) * t)
                b = int(BG_TOP_RIGHT[2] + (BG_BOT[2] - BG_TOP_RIGHT[2]) * t)
            px[x, y] = (r, g, b)
    return bg


def make_gradient_bg_fast():
    """Faster gradient using resized 1D strip — not as smooth but 100x faster."""
    # Build 2x2 base and resize (PIL does bilinear for us)
    base = Image.new('RGB', (2, 2))
    base.putpixel((0, 0), BG_TOP_LEFT)
    base.putpixel((1, 0), BG_TOP_RIGHT)
    base.putpixel((0, 1), BG_BOT)
    base.putpixel((1, 1), (
        (BG_TOP_RIGHT[0] + BG_BOT[0]) // 2,
        (BG_TOP_RIGHT[1] + BG_BOT[1]) // 2,
        (BG_TOP_RIGHT[2] + BG_BOT[2]) // 2,
    ))
    return base.resize((W, H), Image.BICUBIC)


def draw_bubbles(img):
    """Decorative background bubbles — thematic consistency with icon/feature graphic."""
    draw = ImageDraw.Draw(img, 'RGBA')
    bubbles = [
        # (x_frac, y_frac, radius_frac)
        (0.08, 0.06, 0.045),
        (0.92, 0.09, 0.035),
        (0.04, 0.28, 0.025),
        (0.95, 0.44, 0.050),
        (0.06, 0.58, 0.030),
        (0.93, 0.75, 0.022),
        (0.12, 0.90, 0.038),
        (0.88, 0.95, 0.028),
        (0.50, 0.04, 0.015),
    ]
    for bx, by, br in bubbles:
        x = int(W * bx)
        y = int(H * by)
        r = int(W * br)
        wid = max(3, r // 10)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     outline=(255, 255, 255, 35), width=wid)


def frame_screenshot(shot):
    """Subtle rounded-corner mask with soft glow behind it — gives the
    screenshot a 'device' feel without a full phone bezel."""
    shot_w, shot_h = shot.size

    # Target screenshot size on the output canvas (about 65% of height)
    # but preserve source aspect ratio
    target_h = int(H * 0.62)
    ratio    = shot_h / shot_w
    target_w = int(target_h / ratio)
    # Don't exceed 80% of canvas width
    if target_w > int(W * 0.78):
        target_w = int(W * 0.78)
        target_h = int(target_w * ratio)

    resized = shot.resize((target_w, target_h), Image.LANCZOS)

    # Create rounded corner mask
    radius = int(target_w * 0.055)
    mask = Image.new('L', (target_w, target_h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, target_w, target_h], radius=radius, fill=255)

    # Build the framed shot on a padded transparent canvas
    pad = int(target_w * 0.08)  # padding around shot for glow
    frame_w = target_w + pad * 2
    frame_h = target_h + pad * 2
    frame = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))

    # Outer glow (soft blue/cyan for consistency)
    glow_layer = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.rounded_rectangle(
        [pad - 6, pad - 6, pad + target_w + 6, pad + target_h + 6],
        radius=radius + 6,
        fill=(79, 195, 247, 90),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.6)))
    frame.alpha_composite(glow_layer)

    # Drop shadow below the screenshot (darker, offset down)
    shadow_layer = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.rounded_rectangle(
        [pad, pad + int(target_h * 0.03), pad + target_w, pad + target_h + int(target_h * 0.05)],
        radius=radius,
        fill=(0, 0, 0, 150),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.4)))
    frame.alpha_composite(shadow_layer)

    # Paste the screenshot using the rounded mask
    screenshot_rgba = resized.convert('RGBA')
    # Apply the corner mask as alpha
    screenshot_rgba.putalpha(mask)
    frame.paste(screenshot_rgba, (pad, pad), screenshot_rgba)

    # Thin bright outline around shot for definition
    od = ImageDraw.Draw(frame)
    od.rounded_rectangle(
        [pad, pad, pad + target_w, pad + target_h],
        radius=radius,
        outline=(255, 255, 255, 120),
        width=3,
    )

    return frame, frame_w, frame_h


def draw_headline(img, line1, line2, subtitle):
    draw = ImageDraw.Draw(img, 'RGBA')

    # Auto-fit headline font size so both lines fit within 88% of canvas width
    max_width = int(W * 0.88)
    heavy_size = int(H * 0.075)

    # Shrink until both lines fit
    while heavy_size > int(H * 0.04):
        test_font = pick_font('heavy', heavy_size)
        w1_test = test_font.getbbox(line1)[2] - test_font.getbbox(line1)[0]
        w2_test = test_font.getbbox(line2)[2] - test_font.getbbox(line2)[0]
        if max(w1_test, w2_test) <= max_width:
            break
        heavy_size -= int(H * 0.003)

    line1_font = pick_font('heavy', heavy_size)
    line2_font = pick_font('heavy', heavy_size)
    sub_font   = pick_font('medium', int(H * 0.022))

    # Top padding
    y = int(H * 0.045)

    # Measure and center line 1
    bbox1 = line1_font.getbbox(line1)
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]
    x1 = (W - w1) // 2 - bbox1[0]

    # Soft shadow under headline for punch
    shadow_offset = int(H * 0.004)
    draw.text((x1 + shadow_offset, y + shadow_offset), line1,
              font=line1_font, fill=(0, 0, 0, 180))
    draw.text((x1, y), line1, font=line1_font, fill=TEXT_ACCENT)

    y += h1 + int(H * 0.002)

    # Line 2
    bbox2 = line2_font.getbbox(line2)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (W - w2) // 2 - bbox2[0]

    draw.text((x2 + shadow_offset, y + shadow_offset), line2,
              font=line2_font, fill=(0, 0, 0, 180))
    draw.text((x2, y), line2, font=line2_font, fill=TEXT_PRIMARY)

    y += h2 + int(H * 0.020)

    # Subtitle
    bbox3 = sub_font.getbbox(subtitle)
    w3 = bbox3[2] - bbox3[0]
    x3 = (W - w3) // 2 - bbox3[0]
    draw.text((x3, y), subtitle, font=sub_font, fill=TEXT_SUB)

    return y + (bbox3[3] - bbox3[1])


def draw_footer(img):
    """Small brand footer strip at the bottom."""
    draw = ImageDraw.Draw(img, 'RGBA')
    footer_text = 'WATER SORT PUZZLE'
    footer_font = pick_font('heavy', int(H * 0.020))
    bbox = footer_font.getbbox(footer_text)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2 - bbox[0]
    y = int(H * 0.955)
    # Semi-translucent
    draw.text((x, y), footer_text, font=footer_font, fill=(*FOOTER_TINT, 200))


def build_one(src_path, headline1, headline2, subtitle, out_path):
    print(f'  {os.path.basename(src_path)} -> {os.path.basename(out_path)}')

    # 1. Background
    canvas = make_gradient_bg_fast().convert('RGBA')
    draw_bubbles(canvas)

    # 2. Headline area
    headline_bottom = draw_headline(canvas, headline1, headline2, subtitle)

    # 3. Screenshot frame — centered horizontally, below the headline
    shot = Image.open(src_path)
    framed, fw, fh = frame_screenshot(shot)
    fx = (W - fw) // 2
    # Place vertically below headline with a small gap
    gap = int(H * 0.03)
    fy = headline_bottom + gap
    # If it would overflow bottom, pull up
    bottom_limit = int(H * 0.94) - fh
    if fy > bottom_limit:
        fy = bottom_limit
    canvas.alpha_composite(framed, (fx, fy))

    # 4. Footer brand strip
    draw_footer(canvas)

    # 5. Downsample to output dimensions
    out = canvas.resize((OUT_W, OUT_H), Image.LANCZOS)
    flat = Image.new('RGB', (OUT_W, OUT_H), BG_BOT)
    flat.paste(out, mask=out.split()[3])
    flat.save(out_path, 'PNG', optimize=True)


def main():
    if not os.path.isdir(SRC_DIR):
        print(f'ERROR: source directory not found: {SRC_DIR}')
        print('Run this script from the WaterSort/ folder.')
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    print(f'Building {len(SCREENSHOTS)} wrapped screenshots...')
    print(f'  source: {SRC_DIR}')
    print(f'  output: {OUT_DIR}')
    print()

    missing = []
    for src_name, out_name, h1, h2, sub in SCREENSHOTS:
        src_path = os.path.join(SRC_DIR, src_name)
        if not os.path.exists(src_path):
            missing.append(src_name)
            continue
        out_path = os.path.join(OUT_DIR, out_name)
        build_one(src_path, h1, h2, sub, out_path)

    if missing:
        print()
        print(f'WARNING: {len(missing)} source file(s) missing: {missing}')

    print()
    print('Done.')
    print()
    print('Next steps:')
    print(f'  1. Review the wrapped screenshots in {OUT_DIR}')
    print(f'  2. If happy, replace {SRC_DIR}/ contents with them:')
    print(f'     rm {SRC_DIR}/*.png')
    print(f'     mv {OUT_DIR}/*.png {SRC_DIR}/')
    print(f'     rmdir {OUT_DIR}')
    print(f'  3. Upload the new set to Play Console Store listing → Graphics')


if __name__ == '__main__':
    main()
