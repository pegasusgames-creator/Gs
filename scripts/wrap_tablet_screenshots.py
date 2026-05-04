#!/usr/bin/env python3
"""
wrap_tablet_screenshots.py — repo-root version.

Wraps tablet screenshots using per-app theme from app_themes.py.

Usage:
    python3 wrap_tablet_screenshots.py <AppName>

Inputs:
    <AppName>/store/screenshots/phone/raw/01.png ... 07.png
    (Reuses phone raw screenshots — Play Console accepts portrait phone
    screenshots in tablet slots since the app is portrait-only.)

Outputs:
    <AppName>/store/screenshots/tablet_7/01.png, 02.png  (1200×1920)
    <AppName>/store/screenshots/tablet_10/01.png, 02.png (1800×2560)

Default 2 per size (Google docs say 4 minimum but 2 sometimes accepted).
If Play Console rejects, edit MIN_SCREENSHOTS below.

Headlines come from <AppName>/metadata/screenshot_headlines.json.
Uses the first 2 entries (deep gameplay + level complete are strongest).
"""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app_themes import get_theme

# Number of screenshots per tablet size (start with 2; bump to 4 if rejected)
MIN_SCREENSHOTS = 2

SIZE_7  = (1200, 1920)
SIZE_10 = (1800, 2560)
S = 2

_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = {
    'heavy':  [os.path.join(_HERE, 'fonts/Poppins-Bold.ttf'),
               os.path.join(_HERE, '..', '_screenshot_tools/fonts/Poppins-ExtraBold.ttf'),
               '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
               '/Library/Fonts/Poppins-Bold.ttf', 'Poppins-Bold.ttf'],
    'medium': [os.path.join(_HERE, 'fonts/Poppins-Medium.ttf'),
               os.path.join(_HERE, '..', '_screenshot_tools/fonts/Poppins-Regular.ttf'),
               '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
               '/Library/Fonts/Poppins-Medium.ttf', 'Poppins-Medium.ttf'],
}


def pick_font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_gradient_bg(theme, w, h):
    base = Image.new('RGB', (2, 2))
    base.putpixel((0, 0), theme["bg_top_left"])
    base.putpixel((1, 0), theme["bg_top_right"])
    base.putpixel((0, 1), theme["bg_bottom"])
    base.putpixel((1, 1), (
        (theme["bg_top_right"][0] + theme["bg_bottom"][0]) // 2,
        (theme["bg_top_right"][1] + theme["bg_bottom"][1]) // 2,
        (theme["bg_top_right"][2] + theme["bg_bottom"][2]) // 2,
    ))
    return base.resize((w, h), Image.BICUBIC)


def draw_decorations(img, theme, w, h):
    draw = ImageDraw.Draw(img, 'RGBA')
    bubbles = [
        (0.08, 0.06, 0.045), (0.92, 0.09, 0.035),
        (0.04, 0.28, 0.025), (0.95, 0.44, 0.050),
        (0.06, 0.58, 0.030), (0.93, 0.75, 0.022),
        (0.12, 0.90, 0.038), (0.88, 0.95, 0.028),
    ]
    tp = theme["text_primary"]
    deco = (tp[0], tp[1], tp[2], 35)
    for bx, by, br in bubbles:
        x = int(w * bx); y = int(h * by); r = int(w * br)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     outline=deco, width=max(3, r // 10))


def frame_screenshot(shot, theme, w, h):
    target_h = int(h * 0.62)
    ratio = shot.size[1] / shot.size[0]
    target_w = int(target_h / ratio)
    if target_w > int(w * 0.78):
        target_w = int(w * 0.78)
        target_h = int(target_w * ratio)
    resized = shot.resize((target_w, target_h), Image.LANCZOS)

    radius = int(target_w * 0.055)
    mask = Image.new('L', (target_w, target_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, target_w, target_h], radius=radius, fill=255)

    pad = int(target_w * 0.08)
    fw = target_w + pad * 2
    fh = target_h + pad * 2
    frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))

    glow = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [pad - 6, pad - 6, pad + target_w + 6, pad + target_h + 6],
        radius=radius + 6, fill=(*theme["text_accent"], 90))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.6)))
    frame.alpha_composite(glow)

    shadow = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [pad, pad + int(target_h * 0.03),
         pad + target_w, pad + target_h + int(target_h * 0.05)],
        radius=radius, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=int(pad * 0.4)))
    frame.alpha_composite(shadow)

    rgba = resized.convert('RGBA')
    rgba.putalpha(mask)
    frame.paste(rgba, (pad, pad), rgba)
    ImageDraw.Draw(frame).rounded_rectangle(
        [pad, pad, pad + target_w, pad + target_h],
        radius=radius, outline=(255, 255, 255, 120), width=3)
    return frame, fw, fh


def draw_headline(img, line1, line2, subtitle, theme, w, h):
    draw = ImageDraw.Draw(img, 'RGBA')
    max_w = int(w * 0.88)
    size = int(h * 0.075)
    while size > int(h * 0.04):
        f = pick_font('heavy', size)
        if max(f.getbbox(line1)[2] - f.getbbox(line1)[0],
               f.getbbox(line2)[2] - f.getbbox(line2)[0]) <= max_w:
            break
        size -= int(h * 0.003)

    line_font = pick_font('heavy', size)

    sub_size = int(h * 0.022)
    while sub_size > int(h * 0.014):
        sf = pick_font('medium', sub_size)
        sw = sf.getbbox(subtitle)[2] - sf.getbbox(subtitle)[0]
        if sw <= max_w:
            break
        sub_size -= int(h * 0.001)
    sub_font = pick_font('medium', sub_size)
    y = int(h * 0.045)
    sh = int(h * 0.004)

    for line, color in [(line1, theme["text_accent"]),
                        (line2, theme["text_primary"])]:
        bb = line_font.getbbox(line)
        lw = bb[2] - bb[0]
        lh = bb[3] - bb[1]
        x = (w - lw) // 2 - bb[0]
        draw.text((x + sh, y + sh), line, font=line_font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=line_font, fill=color)
        y += lh + int(h * 0.002)

    y += int(h * 0.018)
    bb = sub_font.getbbox(subtitle)
    sw = bb[2] - bb[0]
    sx = (w - sw) // 2 - bb[0]
    draw.text((sx, y), subtitle, font=sub_font, fill=theme["text_subtle"])
    return y + (bb[3] - bb[1])


def draw_footer(img, app_display_name, theme, w, h):
    draw = ImageDraw.Draw(img, 'RGBA')
    text = app_display_name.upper()
    font = pick_font('heavy', int(h * 0.020))
    bb = font.getbbox(text)
    tw = bb[2] - bb[0]
    x = (w - tw) // 2 - bb[0]
    y = int(h * 0.955)
    draw.text((x, y), text, font=font, fill=(*theme["footer_tint"], 200))


def build_one(src, out, headline, subtitle, app_display_name, theme, target_size):
    out_w, out_h = target_size
    w = out_w * S
    h = out_h * S

    canvas = make_gradient_bg(theme, w, h).convert('RGBA')
    draw_decorations(canvas, theme, w, h)
    headline_bottom = draw_headline(canvas, headline['line1'], headline['line2'],
                                    subtitle, theme, w, h)

    shot = Image.open(src)
    frame, fw, fh = frame_screenshot(shot, theme, w, h)
    fx = (w - fw) // 2
    fy = headline_bottom + int(h * 0.03)
    if fy > int(h * 0.94) - fh:
        fy = int(h * 0.94) - fh
    canvas.alpha_composite(frame, (fx, fy))
    draw_footer(canvas, app_display_name, theme, w, h)

    final = canvas.resize((out_w, out_h), Image.LANCZOS)
    flat = Image.new('RGB', (out_w, out_h), theme["bg_bottom"])
    flat.paste(final, mask=final.split()[3])
    flat.save(out, 'PNG', optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name")
    args = ap.parse_args()

    app_dir = REPO_ROOT / args.app_name
    if not app_dir.is_dir():
        print(f"ERROR: app folder not found: {app_dir}")
        sys.exit(1)

    raw_dir = app_dir / "store" / "screenshots" / "phone" / "raw"
    if not raw_dir.is_dir():
        print(f"ERROR: raw screenshots not found: {raw_dir}")
        sys.exit(1)

    headlines_path = app_dir / "metadata" / "screenshot_headlines.json"
    if not headlines_path.exists():
        print(f"ERROR: headlines file not found: {headlines_path}")
        sys.exit(1)

    headlines = json.loads(headlines_path.read_text())
    theme = get_theme(args.app_name)
    print(f"Theme for {args.app_name}: {theme['mood']}")

    title_path = app_dir / "metadata" / "en-US" / "title.txt"
    app_display_name = (title_path.read_text().strip()
                        if title_path.exists() else args.app_name)

    # The 2 strongest screenshots: deep gameplay (raw/01) + level complete (raw/03)
    source_indices = [1, 3] if MIN_SCREENSHOTS == 2 else [1, 3, 2, 6]
    source_indices = source_indices[:MIN_SCREENSHOTS]

    for tablet_size, target, label in [(SIZE_7, "tablet_7", "7\""),
                                        (SIZE_10, "tablet_10", "10\"")]:
        out_dir = app_dir / "store" / "screenshots" / target
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nWrapping {MIN_SCREENSHOTS} screenshots for {label} tablet → {out_dir}")
        for slot, src_idx in enumerate(source_indices, 1):
            src = raw_dir / f"{src_idx:02d}.png"
            if not src.exists():
                print(f"  WARNING: missing {src.name}, skipping slot {slot}")
                continue
            out = out_dir / f"{slot:02d}.png"
            h = headlines[src_idx - 1]
            print(f"  raw/{src.name} → {out.name}  ({h['line1']} {h['line2']})")
            build_one(src, out, h, h['subtitle'], app_display_name,
                      theme, tablet_size)

    print(f"\n✓ Done.")


if __name__ == "__main__":
    main()
