#!/usr/bin/env python3
"""
wrap_tablet_screenshots.py

Produces tablet-sized marketing screenshots for Play Store 7" and 10"
tablet slots, using the same visual language as wrap_screenshots.py (phone).

Dimensions (per Google Play 2026 specs):
- 7"  tablet: 1200 x 1920
- 10" tablet: 1800 x 2560

Outputs:
- store/screenshots/tablet_7/  -> 2 PNGs at 1200x1920
- store/screenshots/tablet_10/ -> 2 PNGs at 1800x2560

Note: Google's Play Console help page states a minimum of 4 screenshots
for tablet slots. This script produces 2 per size as requested. If Play
Console rejects the upload, two additional source screenshots are listed
in EXTRA_SCREENSHOTS — uncomment those entries to produce 4 per size.

Also note: tablet screenshots are OPTIONAL. If you skip them, tablet users
see your phone screenshots scaled up, which is fine for a portrait-only
casual puzzle game.

Usage:
    python3 wrap_tablet_screenshots.py
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_DIR = os.path.join(HERE, 'store', 'screenshots')
SRC_DIR   = os.path.join(STORE_DIR, 'phone')

OUT_7_DIR  = os.path.join(STORE_DIR, 'tablet_7')
OUT_10_DIR = os.path.join(STORE_DIR, 'tablet_10')

SIZE_7  = (1200, 1920)
SIZE_10 = (1800, 2560)

S = 2  # supersample

# ---- theme (identical to wrap_screenshots.py) ----
BG_TOP_LEFT  = (14, 49, 82)
BG_TOP_RIGHT = (12, 70, 105)
BG_BOT       = (6, 28, 50)
TEXT_PRIMARY = (255, 255, 255)
TEXT_ACCENT  = (105, 240, 174)
TEXT_SUB     = (200, 220, 240)
FOOTER_TINT  = (79, 195, 247)

FONT_CANDIDATES = {
    'heavy':   ['/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
                '/Library/Fonts/Poppins-Bold.ttf', 'Poppins-Bold.ttf'],
    'medium':  ['/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
                '/Library/Fonts/Poppins-Medium.ttf', 'Poppins-Medium.ttf'],
}


def pick_font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    print(f'WARNING: could not find Poppins-{kind}. Using default.')
    return ImageFont.load_default()


# ---- screenshot plan: 2 per tablet size ----
# The two strongest from the phone set: deep gameplay + emotional payoff.
# Good first-impression pair that conveys "it's a puzzle game with rewarding wins."
SCREENSHOTS = [
    # (source_filename, output_filename,       line1,   line2,        subtitle)
    ('03_main.png',     '01_gameplay.png',     'POUR',  'AND SORT',   '500 hand-crafted levels'),
    ('07_main.png',     '02_level_complete.png', 'EARN', 'YOUR STARS', 'Beat the par. Be the best.'),
]

# If Play Console rejects the 2-screenshot upload (Google's docs say 4
# minimum for tablets), uncomment these extra entries and re-run:
EXTRA_SCREENSHOTS = [
    # ('02_main.png',   '03_gameplay_early.png', 'RELAX', 'YOUR MIND',  'No timer. No pressure.'),
    # ('06_main.png',   '04_levels.png',         '500',   'LEVELS',     'From easy to expert'),
]


def make_gradient_bg(w, h):
    base = Image.new('RGB', (2, 2))
    base.putpixel((0, 0), BG_TOP_LEFT)
    base.putpixel((1, 0), BG_TOP_RIGHT)
    base.putpixel((0, 1), BG_BOT)
    base.putpixel((1, 1), (
        (BG_TOP_RIGHT[0] + BG_BOT[0]) // 2,
        (BG_TOP_RIGHT[1] + BG_BOT[1]) // 2,
        (BG_TOP_RIGHT[2] + BG_BOT[2]) // 2,
    ))
    return base.resize((w, h), Image.BICUBIC)


def draw_bubbles(img, w, h):
    draw = ImageDraw.Draw(img, 'RGBA')
    bubbles = [
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
        x = int(w * bx)
        y = int(h * by)
        r = int(w * br)
        wid = max(3, r // 10)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     outline=(255, 255, 255, 35), width=wid)


def frame_screenshot(shot, canvas_w, canvas_h):
    shot_w, shot_h = shot.size

    # On tablets the screenshot should be slightly smaller proportionally
    # (more breathing room, typical tablet layout)
    target_h = int(canvas_h * 0.58)
    ratio = shot_h / shot_w
    target_w = int(target_h / ratio)
    if target_w > int(canvas_w * 0.65):
        target_w = int(canvas_w * 0.65)
        target_h = int(target_w * ratio)

    resized = shot.resize((target_w, target_h), Image.LANCZOS)

    radius = int(target_w * 0.055)
    mask = Image.new('L', (target_w, target_h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, target_w, target_h], radius=radius, fill=255)

    pad = int(target_w * 0.08)
    frame_w = target_w + pad * 2
    frame_h = target_h + pad * 2
    frame = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))

    # Outer cyan glow
    glow_layer = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.rounded_rectangle(
        [pad - 6, pad - 6, pad + target_w + 6, pad + target_h + 6],
        radius=radius + 6,
        fill=(79, 195, 247, 90),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.6)))
    frame.alpha_composite(glow_layer)

    # Drop shadow
    shadow_layer = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.rounded_rectangle(
        [pad, pad + int(target_h * 0.03), pad + target_w, pad + target_h + int(target_h * 0.05)],
        radius=radius,
        fill=(0, 0, 0, 150),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.4)))
    frame.alpha_composite(shadow_layer)

    screenshot_rgba = resized.convert('RGBA')
    screenshot_rgba.putalpha(mask)
    frame.paste(screenshot_rgba, (pad, pad), screenshot_rgba)

    od = ImageDraw.Draw(frame)
    od.rounded_rectangle(
        [pad, pad, pad + target_w, pad + target_h],
        radius=radius,
        outline=(255, 255, 255, 120),
        width=3,
    )

    return frame, frame_w, frame_h


def draw_headline(img, line1, line2, subtitle, canvas_w, canvas_h):
    draw = ImageDraw.Draw(img, 'RGBA')

    max_width = int(canvas_w * 0.88)
    heavy_size = int(canvas_h * 0.075)

    while heavy_size > int(canvas_h * 0.04):
        test_font = pick_font('heavy', heavy_size)
        w1_test = test_font.getbbox(line1)[2] - test_font.getbbox(line1)[0]
        w2_test = test_font.getbbox(line2)[2] - test_font.getbbox(line2)[0]
        if max(w1_test, w2_test) <= max_width:
            break
        heavy_size -= int(canvas_h * 0.003)

    line_font = pick_font('heavy', heavy_size)
    sub_font  = pick_font('medium', int(canvas_h * 0.022))

    y = int(canvas_h * 0.045)

    bbox1 = line_font.getbbox(line1)
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]
    x1 = (canvas_w - w1) // 2 - bbox1[0]

    shadow_offset = int(canvas_h * 0.004)
    draw.text((x1 + shadow_offset, y + shadow_offset), line1,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x1, y), line1, font=line_font, fill=TEXT_ACCENT)

    y += h1 + int(canvas_h * 0.002)

    bbox2 = line_font.getbbox(line2)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (canvas_w - w2) // 2 - bbox2[0]

    draw.text((x2 + shadow_offset, y + shadow_offset), line2,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x2, y), line2, font=line_font, fill=TEXT_PRIMARY)

    y += h2 + int(canvas_h * 0.020)

    bbox3 = sub_font.getbbox(subtitle)
    w3 = bbox3[2] - bbox3[0]
    x3 = (canvas_w - w3) // 2 - bbox3[0]
    draw.text((x3, y), subtitle, font=sub_font, fill=TEXT_SUB)

    return y + (bbox3[3] - bbox3[1])


def draw_footer(img, canvas_w, canvas_h):
    draw = ImageDraw.Draw(img, 'RGBA')
    footer_text = 'WATER SORT PUZZLE'
    footer_font = pick_font('heavy', int(canvas_h * 0.020))
    bbox = footer_font.getbbox(footer_text)
    w = bbox[2] - bbox[0]
    x = (canvas_w - w) // 2 - bbox[0]
    y = int(canvas_h * 0.955)
    draw.text((x, y), footer_text, font=footer_font, fill=(*FOOTER_TINT, 200))


def build_one(src_path, out_path, line1, line2, subtitle, target_size):
    out_w, out_h = target_size
    # Supersampled canvas
    W = out_w * S
    H = out_h * S

    print(f'  [{out_w}x{out_h}] {os.path.basename(src_path)} -> {os.path.basename(out_path)}')

    canvas = make_gradient_bg(W, H).convert('RGBA')
    draw_bubbles(canvas, W, H)

    headline_bottom = draw_headline(canvas, line1, line2, subtitle, W, H)

    shot = Image.open(src_path)
    framed, fw, fh = frame_screenshot(shot, W, H)
    fx = (W - fw) // 2
    gap = int(H * 0.03)
    fy = headline_bottom + gap
    bottom_limit = int(H * 0.94) - fh
    if fy > bottom_limit:
        fy = bottom_limit
    canvas.alpha_composite(framed, (fx, fy))

    draw_footer(canvas, W, H)

    out = canvas.resize((out_w, out_h), Image.LANCZOS)
    flat = Image.new('RGB', (out_w, out_h), BG_BOT)
    flat.paste(out, mask=out.split()[3])
    flat.save(out_path, 'PNG', optimize=True)


def main():
    if not os.path.isdir(SRC_DIR):
        print(f'ERROR: source directory not found: {SRC_DIR}')
        print('Run this script from the WaterSort/ folder.')
        return

    os.makedirs(OUT_7_DIR, exist_ok=True)
    os.makedirs(OUT_10_DIR, exist_ok=True)

    all_screenshots = SCREENSHOTS + EXTRA_SCREENSHOTS

    print(f'Building {len(all_screenshots)} screenshots x 2 tablet sizes = '
          f'{len(all_screenshots) * 2} total...')
    print(f'  source: {SRC_DIR}')
    print(f'  output: {OUT_7_DIR}')
    print(f'          {OUT_10_DIR}')
    print()

    missing = []
    for src_name, out_name, h1, h2, sub in all_screenshots:
        src_path = os.path.join(SRC_DIR, src_name)
        if not os.path.exists(src_path):
            missing.append(src_name)
            continue
        # 7" tablet
        build_one(src_path, os.path.join(OUT_7_DIR, out_name),
                  h1, h2, sub, SIZE_7)
        # 10" tablet
        build_one(src_path, os.path.join(OUT_10_DIR, out_name),
                  h1, h2, sub, SIZE_10)

    if missing:
        print()
        print(f'WARNING: {len(missing)} source file(s) missing: {missing}')

    print()
    print('Done.')
    print()
    print('Upload to Play Console:')
    print('  7"  tablet slot  ->  store/screenshots/tablet_7/*.png')
    print('  10" tablet slot  ->  store/screenshots/tablet_10/*.png')
    print()
    print('If Play Console rejects the 2-screenshot upload (needs min 4),')
    print('open this script and uncomment the two lines in EXTRA_SCREENSHOTS,')
    print('then re-run.')


if __name__ == '__main__':
    main()
