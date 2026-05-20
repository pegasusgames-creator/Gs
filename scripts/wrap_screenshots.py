#!/usr/bin/env python3
"""
wrap_screenshots.py — repo-root version.

Wraps raw device screenshots in marketing frames using the per-app theme
from app_themes.py. ONE script for all apps. No per-app cloning.

Usage:
    python3 wrap_screenshots.py <AppName>

Inputs (one wrapped output per raw; menu / shop / settings screens are
NOT captured — every slot must show actual gameplay):
    <AppName>/store/screenshots/phone/raw/01.png  (deep / late-game board)
    <AppName>/store/screenshots/phone/raw/02.png  (early gameplay)
    <AppName>/store/screenshots/phone/raw/03.png  (level complete — 3-star + theme-unlock card)
    <AppName>/store/screenshots/phone/raw/04.png  (daily challenge active)
    <AppName>/store/screenshots/phone/raw/05.png  (another mid-game board)
    <AppName>/store/screenshots/phone/raw/06.png  (another gameplay state)
    (5-7 gameplay slots; the script wraps however many raws exist)

Outputs (1080×2400):
    <AppName>/store/screenshots/phone/01.png ... NN.png

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

# Import theme registry (lives next to this script in scripts/)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from app_themes import get_theme
except ImportError:
    print("ERROR: app_themes.py not found alongside this script. Cannot determine theme.")
    sys.exit(1)

# ---------------------- output dimensions ----------------------
OUT_W = 1080
OUT_H = 2400
S = 2  # supersample factor for crisp text
W = OUT_W * S
H = OUT_H * S

# ---------------------- font discovery ----------------------
_FONTS_DIR = str(Path(__file__).resolve().parent / 'fonts')
FONT_CANDIDATES = {
    'heavy':  [_FONTS_DIR + '/Poppins-Bold.ttf',
               '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
               '/Library/Fonts/Poppins-Bold.ttf',
               'Poppins-Bold.ttf'],
    'medium': [_FONTS_DIR + '/Poppins-Medium.ttf',
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


# ---------------------- per-slot wrapper variants ----------------------
# Each of the 7 screenshot slots gets a visually distinct marketing
# frame so no two wrapped shots look templated. Only two levers vary:
# the background (gradient direction + decoration pattern + theme
# colour) and headline placement (top vs bottom). The framed screenshot
# and the headline text always stay horizontally centered — no off-
# center nudging, no accent box behind the text.
VARIANTS = [
    {"gradient": "tl-br",      "headline": "top",    "deco": "bubbles"},
    {"gradient": "tr-bl",      "headline": "bottom", "deco": "corner"},
    {"gradient": "vertical",   "headline": "top",    "deco": "sparse"},
    {"gradient": "bl-tr",      "headline": "top",    "deco": "dots"},
    {"gradient": "horizontal", "headline": "bottom", "deco": "bubbles"},
    {"gradient": "tl-br",      "headline": "top",    "deco": "rings"},
    {"gradient": "tr-bl",      "headline": "bottom", "deco": "none"},
]


def variant_for(slot_index, surface_offset=0):
    """slot_index is 0-based; surface_offset rotates the table so the same
    slot number on phone vs tablet_7 vs tablet_10 gets a different layout."""
    return VARIANTS[(slot_index + surface_offset) % len(VARIANTS)]


# ---------------------- image helpers ----------------------

def make_gradient_bg(theme, direction="tl-br"):
    """3-stop gradient; corner placement varies by direction so each
    variant reads as a visually different background."""
    c1 = theme["bg_top_left"]
    c2 = theme["bg_top_right"]
    c3 = theme["bg_bottom"]
    mid = tuple((c1[i] + c3[i]) // 2 for i in range(3))
    # (TL, TR, BL, BR) corner colours per direction
    layouts = {
        "tl-br":      (c1, c2, mid, c3),
        "tr-bl":      (c2, c1, c3, mid),
        "bl-tr":      (mid, c3, c1, c2),
        "vertical":   (c1, c2, c3, c3),
        "horizontal": (c1, c3, c1, c3),
    }
    tl, tr, bl, br = layouts.get(direction, layouts["tl-br"])
    base = Image.new('RGB', (2, 2))
    base.putpixel((0, 0), tl)
    base.putpixel((1, 0), tr)
    base.putpixel((0, 1), bl)
    base.putpixel((1, 1), br)
    return base.resize((W, H), Image.BICUBIC)


def draw_decorations(img, theme, style="bubbles"):
    """Decorative texture; style varies per slot variant."""
    if style == "none":
        return
    draw = ImageDraw.Draw(img, 'RGBA')
    tp = theme["text_primary"]
    deco = (tp[0], tp[1], tp[2], 35)
    ac = theme["text_accent"]
    if style == "bubbles":
        for bx, by, br in [(0.08, 0.06, 0.045), (0.92, 0.09, 0.035),
                           (0.04, 0.28, 0.025), (0.95, 0.44, 0.050),
                           (0.06, 0.58, 0.030), (0.93, 0.75, 0.022),
                           (0.12, 0.90, 0.038), (0.88, 0.95, 0.028)]:
            x, y, r = int(W * bx), int(H * by), int(W * br)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=max(3, r // 10))
    elif style == "corner":
        for cx, cy in [(0.0, 0.0), (1.0, 1.0)]:
            for rr in (0.30, 0.42, 0.54):
                r = int(W * rr)
                x, y = int(W * cx), int(H * cy)
                draw.ellipse([x - r, y - r, x + r, y + r],
                             outline=deco, width=4)
    elif style == "dots":
        for gx in range(6):
            for gy in range(13):
                x = int(W * (0.07 + gx * 0.172))
                y = int(H * (0.05 + gy * 0.075))
                r = int(W * 0.007)
                draw.ellipse([x - r, y - r, x + r, y + r], fill=deco)
    elif style == "sidebar":
        bw = int(W * 0.13)
        draw.rectangle([W - bw, 0, W, H], fill=(ac[0], ac[1], ac[2], 26))
        draw.rectangle([W - bw - 6, 0, W - bw, H],
                       fill=(ac[0], ac[1], ac[2], 50))
    elif style == "sparse":
        for bx, by, br in [(0.12, 0.11, 0.10), (0.90, 0.40, 0.13),
                           (0.16, 0.83, 0.11)]:
            x, y, r = int(W * bx), int(H * by), int(W * br)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=5)
    elif style == "rings":
        x, y = int(W * 0.04), int(H * 0.96)
        for rr in (0.14, 0.22, 0.30, 0.38):
            r = int(W * rr)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=4)


def frame_screenshot(shot, theme, height_frac=0.62):
    """Wrap a screenshot in a rounded-corner phone-frame with glow + shadow."""
    target_h = int(H * height_frac)
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


def draw_headline(img, line1, line2, subtitle, theme, y_start=None):
    draw = ImageDraw.Draw(img, 'RGBA')
    if y_start is None:
        y_start = int(H * 0.045)
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
    # Subtitle bumped from H*0.022 → H*0.026 for legibility on light themes
    # (Nonogram cream paper). Stays comfortably below the heavy headline
    # so visual hierarchy is preserved.
    sub_font  = pick_font('medium', int(H * 0.026))

    y = y_start
    shadow_offset = int(H * 0.004)

    # Line 1 — accent color
    bbox1 = line_font.getbbox(line1)
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]
    x1 = (W - w1) // 2 - bbox1[0]
    draw.text((x1 + shadow_offset, y + shadow_offset), line1,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x1, y), line1, font=line_font, fill=theme["text_accent"])
    y += h1 + int(H * 0.005)

    # Line 2 — primary text color
    bbox2 = line_font.getbbox(line2)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (W - w2) // 2 - bbox2[0]
    draw.text((x2 + shadow_offset, y + shadow_offset), line2,
              font=line_font, fill=(0, 0, 0, 180))
    draw.text((x2, y), line2, font=line_font, fill=theme["text_primary"])
    # Wider gap between headline and subtitle (was H*0.020 — too cramped,
    # subtitle visually merged with the headline on Nonogram's cream bg).
    y += h2 + int(H * 0.040)

    # Subtitle — subtle color, shrink-to-fit then 2-line wrap if still too wide.
    # Bug fix (May 2026 audit): previous code rendered a single line with no
    # bounds check, so subtitles wider than `max_width` got centered on a
    # midpoint past the canvas edge — producing the "iving controls" /
    # "rom easy 4-tube" / "[…]al tiles combine" both-ends-clipped pattern.
    sub_text = subtitle
    sub_size = sub_font.size

    # Step 1: shrink font down to 75% of original before resorting to wrap
    # (raised floor with the larger base size — keeps the subtitle readable
    # even when the long copy forces a shrink)
    min_size = max(int(sub_size * 0.75), 28)
    while sub_size > min_size:
        bbox3 = sub_font.getbbox(sub_text)
        if bbox3[2] - bbox3[0] <= max_width:
            break
        sub_size -= 2
        sub_font = pick_font('medium', sub_size)

    # Step 2: if still too wide, wrap to 2 lines on word boundaries
    bbox3 = sub_font.getbbox(sub_text)
    if bbox3[2] - bbox3[0] > max_width:
        words = sub_text.split()
        # Find a split point near the middle that keeps both halves under max_width
        best_split = None
        for i in range(1, len(words)):
            line_a = " ".join(words[:i])
            line_b = " ".join(words[i:])
            ba = sub_font.getbbox(line_a)
            bb = sub_font.getbbox(line_b)
            if (ba[2] - ba[0] <= max_width and
                bb[2] - bb[0] <= max_width):
                # Prefer splits closest to the middle
                imbalance = abs(len(line_a) - len(line_b))
                if best_split is None or imbalance < best_split[0]:
                    best_split = (imbalance, line_a, line_b)
        if best_split:
            line_a, line_b = best_split[1], best_split[2]
            for line in (line_a, line_b):
                bb = sub_font.getbbox(line)
                w = bb[2] - bb[0]
                x = (W - w) // 2 - bb[0]
                draw.text((x, y), line, font=sub_font,
                          fill=theme["text_subtle"])
                y += (bb[3] - bb[1]) + int(H * 0.005)
            return y
        # Fallback: even one word is too wide. Truncate with ellipsis.
        while sub_text and sub_font.getbbox(sub_text + "…")[2] > max_width:
            sub_text = sub_text[:-1]
        sub_text += "…"

    bbox3 = sub_font.getbbox(sub_text)
    w3 = bbox3[2] - bbox3[0]
    x3 = (W - w3) // 2 - bbox3[0]
    draw.text((x3, y), sub_text, font=sub_font, fill=theme["text_subtle"])
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


def build_one(src_path, out_path, line1, line2, subtitle,
              app_display_name, theme, variant):
    canvas = make_gradient_bg(theme, variant["gradient"]).convert('RGBA')
    draw_decorations(canvas, theme, variant["deco"])

    bottom = variant["headline"] == "bottom"
    shot = Image.open(src_path)
    framed, fw, fh = frame_screenshot(
        shot, theme, height_frac=(0.52 if bottom else 0.62))

    # Framed screenshot always stays horizontally centered.
    fx = (W - fw) // 2

    if bottom:
        fy = int(H * 0.060)
        draw_headline(canvas, line1, line2, subtitle, theme,
                      y_start=fy + fh + int(H * 0.035))
    else:
        headline_bottom = draw_headline(canvas, line1, line2, subtitle, theme)
        fy = headline_bottom + int(H * 0.03)
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

    # Slot count follows how many raw captures exist. Menu / shop / settings
    # screens are no longer captured (every slot must show actual gameplay),
    # so a set may legitimately be 6 rather than 7.
    raw_files = sorted(p for p in raw_dir.glob("*.png") if p.stem.isdigit())
    n_slots = len(raw_files)
    if n_slots < 2:
        print(f"ERROR: need at least 2 raw screenshots, found {n_slots} in {raw_dir}")
        sys.exit(1)
    if len(headlines) < n_slots:
        print(f"ERROR: need {n_slots} headlines (one per raw screenshot), "
              f"found {len(headlines)} in {headlines_path}")
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

    print(f"\nWrapping {n_slots} screenshots for {app_name}...")
    print(f"  source: {raw_dir}")
    print(f"  output: {out_dir}")
    print()

    for i in range(n_slots):
        src = raw_dir / f"{i+1:02d}.png"
        out = out_dir / f"{i+1:02d}.png"
        if not src.exists():
            print(f"  WARNING: missing {src.name}, skipping")
            continue
        h = headlines[i]
        variant = variant_for(i)
        print(f"  {src.name} → {out.name}  ({h['line1']} {h['line2']})"
              f"  [{variant['gradient']}/{variant['headline']}/{variant['deco']}]")
        build_one(src, out, h['line1'], h['line2'], h['subtitle'],
                  app_display_name, theme, variant)

    print()
    print(f"✓ Done. Phone screenshots ready at {out_dir}")
    print("  Verify visually that the wrapped output has gradient bg, headline,")
    print("  framed gameplay shot, and footer — NOT raw device output.")


if __name__ == "__main__":
    main()
