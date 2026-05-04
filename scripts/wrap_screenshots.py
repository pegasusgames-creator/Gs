#!/usr/bin/env python3
"""
wrap_screenshots.py — repo-root version.

Wraps raw device screenshots in marketing frames using the per-app theme
from app_themes.py. ONE script for all apps. No per-app cloning.

Usage:
    python3 wrap_screenshots.py <AppName>

Inputs:
    <AppName>/store/screenshots/phone/raw/01.png  (deep gameplay)
    <AppName>/store/screenshots/phone/raw/02.png  (early gameplay)
    <AppName>/store/screenshots/phone/raw/03.png  (level complete)
    <AppName>/store/screenshots/phone/raw/04.png  (daily missions)
    <AppName>/store/screenshots/phone/raw/05.png  (stats)
    <AppName>/store/screenshots/phone/raw/06.png  (levels list)
    <AppName>/store/screenshots/phone/raw/07.png  (menu)

Outputs (1080×2400):
    <AppName>/store/screenshots/phone/01.png ... 07.png

Headline copy comes from <AppName>/metadata/screenshot_headlines.json.
If that file doesn't exist, the script REFUSES to run and tells Claude
Code to write headlines first. We don't ship generic placeholder copy.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import theme registry
sys.path.insert(0, str(REPO_ROOT))
try:
    from app_themes import get_theme
except ImportError:
    print("ERROR: app_themes.py not found in repo root. Cannot determine theme.")
    sys.exit(1)

# ---------------------- output dimensions ----------------------
OUT_W = 1080
OUT_H = 2400
S = 2  # supersample factor for crisp text
W = OUT_W * S
H = OUT_H * S

# ---------------------- font discovery ----------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = {
    'heavy':  [os.path.join(_HERE, 'fonts/Poppins-Bold.ttf'),
               os.path.join(_HERE, '..', '_screenshot_tools/fonts/Poppins-ExtraBold.ttf'),
               '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
               '/Library/Fonts/Poppins-Bold.ttf',
               'Poppins-Bold.ttf'],
    'medium': [os.path.join(_HERE, 'fonts/Poppins-Medium.ttf'),
               os.path.join(_HERE, '..', '_screenshot_tools/fonts/Poppins-Regular.ttf'),
               '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
               '/Library/Fonts/Poppins-Medium.ttf',
               'Poppins-Medium.ttf'],
}


def pick_font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    print(f"WARNING: Poppins-{kind} not found, using default font")
    return ImageFont.load_default()


# ---------------------- image helpers ----------------------

def make_gradient_bg(theme):
    """Build a 3-stop diagonal gradient using the theme's bg colors."""
    # 2x2 base extended to W x H via bicubic resize — fast and smooth
    base = Image.new('RGB', (2, 2))
    base.putpixel((0, 0), theme["bg_top_left"])
    base.putpixel((1, 0), theme["bg_top_right"])
    base.putpixel((0, 1), theme["bg_bottom"])
    base.putpixel((1, 1), (
        (theme["bg_top_right"][0] + theme["bg_bottom"][0]) // 2,
        (theme["bg_top_right"][1] + theme["bg_bottom"][1]) // 2,
        (theme["bg_top_right"][2] + theme["bg_bottom"][2]) // 2,
    ))
    return base.resize((W, H), Image.BICUBIC)


def draw_decorations(img, theme):
    """Subtle decorative circles for visual texture."""
    draw = ImageDraw.Draw(img, 'RGBA')
    bubbles = [
        (0.08, 0.06, 0.045), (0.92, 0.09, 0.035),
        (0.04, 0.28, 0.025), (0.95, 0.44, 0.050),
        (0.06, 0.58, 0.030), (0.93, 0.75, 0.022),
        (0.12, 0.90, 0.038), (0.88, 0.95, 0.028),
    ]
    # Decoration color: light text color at low alpha — works on dark and
    # light themes because we use whichever text_primary is.
    tp = theme["text_primary"]
    deco = (tp[0], tp[1], tp[2], 35)
    for bx, by, br in bubbles:
        x = int(W * bx)
        y = int(H * by)
        r = int(W * br)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     outline=deco, width=max(3, r // 10))


def frame_screenshot(shot, theme):
    """Wrap a screenshot in a rounded-corner phone-frame with glow + shadow."""
    target_h = int(H * 0.62)
    ratio = shot.size[1] / shot.size[0]
    target_w = int(target_h / ratio)
    if target_w > int(W * 0.78):
        target_w = int(W * 0.78)
        target_h = int(target_w * ratio)

    resized = shot.resize((target_w, target_h), Image.LANCZOS)

    radius = int(target_w * 0.055)
    mask = Image.new('L', (target_w, target_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, target_w, target_h], radius=radius, fill=255)

    pad = int(target_w * 0.08)
    frame_w = target_w + pad * 2
    frame_h = target_h + pad * 2
    frame = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))

    # Outer glow using the theme's accent color
    glow = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    glow_color = (*theme["text_accent"], 90)
    ImageDraw.Draw(glow).rounded_rectangle(
        [pad - 6, pad - 6, pad + target_w + 6, pad + target_h + 6],
        radius=radius + 6, fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.6)))
    frame.alpha_composite(glow)

    # Drop shadow
    shadow = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [pad, pad + int(target_h * 0.03),
         pad + target_w, pad + target_h + int(target_h * 0.05)],
        radius=radius, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.4)))
    frame.alpha_composite(shadow)

    rgba = resized.convert('RGBA')
    rgba.putalpha(mask)
    frame.paste(rgba, (pad, pad), rgba)

    # Thin outline for definition
    ImageDraw.Draw(frame).rounded_rectangle(
        [pad, pad, pad + target_w, pad + target_h],
        radius=radius, outline=(255, 255, 255, 120), width=3)

    return frame, frame_w, frame_h


def draw_headline(img, line1, line2, subtitle, theme):
    draw = ImageDraw.Draw(img, 'RGBA')
    max_width = int(W * 0.88)
    heavy_size = int(H * 0.075)

    # Auto-fit to width
    while heavy_size > int(H * 0.04):
        f = pick_font('heavy', heavy_size)
        w1 = f.getbbox(line1)[2] - f.getbbox(line1)[0]
        w2 = f.getbbox(line2)[2] - f.getbbox(line2)[0]
        if max(w1, w2) <= max_width:
            break
        heavy_size -= int(H * 0.003)

    line_font = pick_font('heavy', heavy_size)

    sub_size = int(H * 0.022)
    while sub_size > int(H * 0.014):
        sf = pick_font('medium', sub_size)
        sw = sf.getbbox(subtitle)[2] - sf.getbbox(subtitle)[0]
        if sw <= max_width:
            break
        sub_size -= int(H * 0.001)
    sub_font = pick_font('medium', sub_size)

    y = int(H * 0.045)
    shadow_offset = int(H * 0.004)

    # Line 1 — accent color
    bbox1 = line_font.getbbox(line1)
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]
    x1 = (W - w1) // 2 - bbox1[0]
    draw.text((x1 + shadow_offset, y + shadow_offset), line1,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x1, y), line1, font=line_font, fill=theme["text_accent"])
    y += h1 + int(H * 0.002)

    # Line 2 — primary text color
    bbox2 = line_font.getbbox(line2)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (W - w2) // 2 - bbox2[0]
    draw.text((x2 + shadow_offset, y + shadow_offset), line2,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x2, y), line2, font=line_font, fill=theme["text_primary"])
    y += h2 + int(H * 0.020)

    # Subtitle — subtle color
    bbox3 = sub_font.getbbox(subtitle)
    w3 = bbox3[2] - bbox3[0]
    x3 = (W - w3) // 2 - bbox3[0]
    draw.text((x3, y), subtitle, font=sub_font, fill=theme["text_subtle"])
    return y + (bbox3[3] - bbox3[1])


def draw_footer(img, app_display_name, theme):
    draw = ImageDraw.Draw(img, 'RGBA')
    text = app_display_name.upper()
    font = pick_font('heavy', int(H * 0.020))
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2 - bbox[0]
    y = int(H * 0.955)
    draw.text((x, y), text, font=font,
              fill=(*theme["footer_tint"], 200))


def build_one(src_path, out_path, line1, line2, subtitle, app_display_name, theme):
    canvas = make_gradient_bg(theme).convert('RGBA')
    draw_decorations(canvas, theme)
    headline_bottom = draw_headline(canvas, line1, line2, subtitle, theme)

    shot = Image.open(src_path)
    framed, fw, fh = frame_screenshot(shot, theme)
    fx = (W - fw) // 2
    gap = int(H * 0.03)
    fy = headline_bottom + gap
    bottom_limit = int(H * 0.94) - fh
    if fy > bottom_limit:
        fy = bottom_limit
    canvas.alpha_composite(framed, (fx, fy))

    draw_footer(canvas, app_display_name, theme)

    out = canvas.resize((OUT_W, OUT_H), Image.LANCZOS)
    flat = Image.new('RGB', (OUT_W, OUT_H), theme["bg_bottom"])
    flat.paste(out, mask=out.split()[3])
    flat.save(out_path, 'PNG', optimize=True)


# ---------------------- main ----------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name", help="App folder name (e.g., WaterSort)")
    args = ap.parse_args()

    app_name = args.app_name
    app_dir = REPO_ROOT / app_name
    if not app_dir.is_dir():
        print(f"ERROR: app folder not found: {app_dir}")
        sys.exit(1)

    raw_dir = app_dir / "store" / "screenshots" / "phone" / "raw"
    if not raw_dir.is_dir():
        print(f"ERROR: raw screenshots folder not found: {raw_dir}")
        print("Capture device screenshots first; see SHIP_GAME.md Phase 3.1")
        sys.exit(1)

    headlines_path = app_dir / "metadata" / "screenshot_headlines.json"
    if not headlines_path.exists():
        print(f"ERROR: headlines file not found: {headlines_path}")
        print()
        print("Write 7 distinct marketing headlines for this app first.")
        print("File format (JSON):")
        print("  [")
        print('    {"line1": "POUR", "line2": "AND SORT", "subtitle": "500 hand-crafted levels"},')
        print('    {"line1": "RELAX", "line2": "YOUR MIND", "subtitle": "No timer. No pressure."},')
        print('    {"line1": "EARN", "line2": "YOUR STARS", "subtitle": "Beat the par."},')
        print("    ... 4 more ...")
        print("  ]")
        print()
        print("Each line1/line2 is ≤5 words. No banned phrases (#1, Best, Top,")
        print("Download Now, etc.) — see QUALITY_PLAYBOOK.md §7.2.")
        sys.exit(1)

    headlines = json.loads(headlines_path.read_text())
    if len(headlines) < 7:
        print(f"ERROR: need 7 headlines, found {len(headlines)} in {headlines_path}")
        sys.exit(1)

    theme = get_theme(app_name)
    print(f"Theme for {app_name}: {theme['mood']}")
    print(f"  bg gradient: {theme['bg_top_left']} → {theme['bg_top_right']} → {theme['bg_bottom']}")

    # App display name — try title.txt, fall back to folder name
    title_path = app_dir / "metadata" / "en-US" / "title.txt"
    if title_path.exists():
        app_display_name = title_path.read_text().strip()
    else:
        app_display_name = app_name

    out_dir = app_dir / "store" / "screenshots" / "phone"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nWrapping 7 screenshots for {app_name}...")
    print(f"  source: {raw_dir}")
    print(f"  output: {out_dir}")
    print()

    for i in range(7):
        src = raw_dir / f"{i+1:02d}.png"
        out = out_dir / f"{i+1:02d}.png"
        if not src.exists():
            print(f"  WARNING: missing {src.name}, skipping")
            continue
        h = headlines[i]
        print(f"  {src.name} → {out.name}  ({h['line1']} {h['line2']})")
        build_one(src, out, h['line1'], h['line2'], h['subtitle'],
                  app_display_name, theme)

    print()
    print(f"✓ Done. Phone screenshots ready at {out_dir}")
    print("  Verify visually that the wrapped output has gradient bg, headline,")
    print("  framed gameplay shot, and footer — NOT raw device output.")


if __name__ == "__main__":
    main()
