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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app_themes import get_theme

# Number of screenshots per tablet size (start with 2; bump to 4 if rejected)
MIN_SCREENSHOTS = 2

SIZE_7  = (1200, 1920)
SIZE_10 = (1800, 2560)
S = 2

_FONTS_DIR = str(Path(__file__).resolve().parent / 'fonts')
FONT_CANDIDATES = {
    'heavy':  [_FONTS_DIR + '/Poppins-Bold.ttf',
               '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
               '/Library/Fonts/Poppins-Bold.ttf', 'Poppins-Bold.ttf'],
    'medium': [_FONTS_DIR + '/Poppins-Medium.ttf',
               '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
               '/Library/Fonts/Poppins-Medium.ttf', 'Poppins-Medium.ttf'],
}


def pick_font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ── per-slot wrapper variants ──────────────────────────────────────
# Each tablet slot gets a visually distinct marketing frame so no two
# wrapped shots look templated. Only two levers vary: the background
# (gradient direction + decoration pattern + theme colour) and headline
# placement (top vs bottom). The framed screenshot and headline text
# always stay horizontally centered — no off-center nudging, no accent
# box behind the text. The table is rotated per surface (see
# SURFACE_OFFSETS) so slot N on tablet_7 differs from slot N on
# tablet_10 and on phone.
VARIANTS = [
    {"gradient": "tl-br",      "headline": "top",    "deco": "bubbles"},
    {"gradient": "tr-bl",      "headline": "bottom", "deco": "corner"},
    {"gradient": "vertical",   "headline": "top",    "deco": "sparse"},
    {"gradient": "bl-tr",      "headline": "top",    "deco": "dots"},
    {"gradient": "horizontal", "headline": "bottom", "deco": "bubbles"},
    {"gradient": "tl-br",      "headline": "top",    "deco": "rings"},
    {"gradient": "tr-bl",      "headline": "bottom", "deco": "none"},
]
# Phone uses offset 0; rotate the tablets so a given slot looks
# different across the three surfaces.
SURFACE_OFFSETS = {"tablet_7": 3, "tablet_10": 5}


def variant_for(slot_index, surface_offset):
    return VARIANTS[(slot_index + surface_offset) % len(VARIANTS)]


def make_gradient_bg(theme, w, h, direction="tl-br"):
    c1 = theme["bg_top_left"]
    c2 = theme["bg_top_right"]
    c3 = theme["bg_bottom"]
    mid = tuple((c1[i] + c3[i]) // 2 for i in range(3))
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
    return base.resize((w, h), Image.BICUBIC)


def draw_decorations(img, theme, w, h, style="bubbles"):
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
            x, y, r = int(w * bx), int(h * by), int(w * br)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=max(3, r // 10))
    elif style == "corner":
        for cx, cy in [(0.0, 0.0), (1.0, 1.0)]:
            for rr in (0.30, 0.42, 0.54):
                r = int(w * rr)
                x, y = int(w * cx), int(h * cy)
                draw.ellipse([x - r, y - r, x + r, y + r],
                             outline=deco, width=4)
    elif style == "dots":
        for gx in range(6):
            for gy in range(13):
                x = int(w * (0.07 + gx * 0.172))
                y = int(h * (0.05 + gy * 0.075))
                r = int(w * 0.007)
                draw.ellipse([x - r, y - r, x + r, y + r], fill=deco)
    elif style == "sidebar":
        bw = int(w * 0.13)
        draw.rectangle([w - bw, 0, w, h], fill=(ac[0], ac[1], ac[2], 26))
        draw.rectangle([w - bw - 6, 0, w - bw, h],
                       fill=(ac[0], ac[1], ac[2], 50))
    elif style == "sparse":
        for bx, by, br in [(0.12, 0.11, 0.10), (0.90, 0.40, 0.13),
                           (0.16, 0.83, 0.11)]:
            x, y, r = int(w * bx), int(h * by), int(w * br)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=5)
    elif style == "rings":
        x, y = int(w * 0.04), int(h * 0.96)
        for rr in (0.14, 0.22, 0.30, 0.38):
            r = int(w * rr)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=deco, width=4)


def frame_screenshot(shot, theme, w, h, height_frac=0.62):
    target_h = int(h * height_frac)
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


def draw_headline(img, line1, line2, subtitle, theme, w, h,
                  y_start=None):
    draw = ImageDraw.Draw(img, 'RGBA')
    if y_start is None:
        y_start = int(h * 0.045)
    max_w = int(w * 0.88)
    size = int(h * 0.075)
    while size > int(h * 0.04):
        f = pick_font('heavy', size)
        if max(f.getbbox(line1)[2] - f.getbbox(line1)[0],
               f.getbbox(line2)[2] - f.getbbox(line2)[0]) <= max_w:
            break
        size -= int(h * 0.003)

    line_font = pick_font('heavy', size)
    sub_font  = pick_font('medium', int(h * 0.022))
    y = y_start
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

    # Headline-to-subtitle gap: 3.5% of canvas height (was 1.8%, too
    # tight on 2560-tall canvases — heavy display fonts crowded the
    # subtitle on the May 2026 Puzzle2048 audit). 3.5% gives proportional
    # breathing room; matches QUALITY_PLAYBOOK §7.2.1 tablet spec.
    y += int(h * 0.035)
    # Same fix as wrap_screenshots.py — shrink-then-wrap subtitle.
    sub_text = subtitle
    sub_size = sub_font.size
    min_size = max(int(sub_size * 0.70), 22)
    while sub_size > min_size:
        bb = sub_font.getbbox(sub_text)
        if bb[2] - bb[0] <= max_w:
            break
        sub_size -= 2
        sub_font = pick_font('medium', sub_size)

    bb = sub_font.getbbox(sub_text)
    if bb[2] - bb[0] > max_w:
        words = sub_text.split()
        best_split = None
        for i in range(1, len(words)):
            line_a = " ".join(words[:i])
            line_b = " ".join(words[i:])
            ba = sub_font.getbbox(line_a)
            bb_ = sub_font.getbbox(line_b)
            if (ba[2] - ba[0] <= max_w and
                bb_[2] - bb_[0] <= max_w):
                imbalance = abs(len(line_a) - len(line_b))
                if best_split is None or imbalance < best_split[0]:
                    best_split = (imbalance, line_a, line_b)
        if best_split:
            for line in (best_split[1], best_split[2]):
                ba = sub_font.getbbox(line)
                sw = ba[2] - ba[0]
                sx = (w - sw) // 2 - ba[0]
                draw.text((sx, y), line, font=sub_font,
                          fill=theme["text_subtle"])
                y += (ba[3] - ba[1]) + int(h * 0.004)
            return y
        while sub_text and sub_font.getbbox(sub_text + "…")[2] > max_w:
            sub_text = sub_text[:-1]
        sub_text += "…"

    bb = sub_font.getbbox(sub_text)
    sw = bb[2] - bb[0]
    sx = (w - sw) // 2 - bb[0]
    draw.text((sx, y), sub_text, font=sub_font, fill=theme["text_subtle"])
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


def build_one(src, out, headline, subtitle, app_display_name, theme,
              target_size, variant):
    out_w, out_h = target_size

    # ★ Resolution guard (May 2026): tablet wraps must use captures from
    # a TABLET emulator, not phone captures rescaled. The April 2026
    # Puzzle2048 ship had this defect — phone raws inside a tablet
    # canvas read as "phone running in tablet emulation" to reviewers.
    # Threshold is 0.85 × target width — Nexus 10's native 1600 passes
    # the 1800 target, but a phone's 1080 still fails cleanly.
    raw_img = Image.open(src)
    rw, rh = raw_img.size
    min_width = int(out_w * 0.85)
    if rw < min_width:
        raise ValueError(
            f"\n  ✗ {src}: raw screenshot is only {rw}x{rh}, too narrow "
            f"for {out_w}x{out_h} target.\n"
            f"    Tablet wraps must use raw captures from a TABLET emulator at\n"
            f"    {out_w}px+ width, not phone captures rescaled.\n"
            f"    The in-app layout on a tablet emulator is genuinely different\n"
            f"    (different aspect ratio, possibly different HUD layout).\n\n"
            f"    To capture tablet raws:\n"
            f"      1. Boot a tablet AVD: emulator -avd pegasus_tablet_7\n"
            f"         (or pegasus_tablet_10)\n"
            f"      2. python3 scripts/capture_screenshots.py <App> --target tablet_7\n"
            f"      3. Re-run this wrap script.\n\n"
            f"    DO NOT rescale phone captures — tablet users see the\n"
            f"    mismatch in 0.5 seconds and uninstall."
        )
    aspect = rh / rw if rw else 0
    if aspect < 1.30:
        raise ValueError(
            f"{src}: aspect ratio {aspect:.2f} is too short for tablet "
            f"portrait. Expected ~1.6 (1200x1920) or ~1.42 (1800x2560). "
            f"This looks like a phone capture letterboxed into a tablet "
            f"frame. Re-capture from a tablet AVD."
        )

    w = out_w * S
    h = out_h * S

    canvas = make_gradient_bg(theme, w, h, variant["gradient"]).convert('RGBA')
    draw_decorations(canvas, theme, w, h, variant["deco"])

    bottom = variant["headline"] == "bottom"
    shot = Image.open(src)
    frame, fw, fh = frame_screenshot(
        shot, theme, w, h, height_frac=(0.52 if bottom else 0.62))

    # Framed screenshot always stays horizontally centered.
    fx = (w - fw) // 2

    if bottom:
        fy = int(h * 0.060)
        draw_headline(canvas, headline['line1'], headline['line2'],
                      subtitle, theme, w, h,
                      y_start=fy + fh + int(h * 0.035))
    else:
        headline_bottom = draw_headline(canvas, headline['line1'],
                                        headline['line2'], subtitle, theme,
                                        w, h)
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

    default_headlines_path = app_dir / "metadata" / "screenshot_headlines.json"
    if not default_headlines_path.exists():
        print(f"ERROR: headlines file not found: {default_headlines_path}")
        sys.exit(1)

    default_headlines = json.loads(default_headlines_path.read_text())
    theme = get_theme(args.app_name)
    print(f"Theme for {args.app_name}: {theme['mood']}")

    title_path = app_dir / "metadata" / "en-US" / "title.txt"
    app_display_name = (title_path.read_text().strip()
                        if title_path.exists() else args.app_name)

    # Per QUALITY_PLAYBOOK §7.3 (mandatory tablets, May 2026), tablet
    # captures are SEPARATE captures from a tablet emulator. They live
    # at <App>/store/screenshots/tablet_7/raw/ and tablet_10/raw/ —
    # NOT shared with phone/raw/. Each set has its own 7 slots.
    # If <App>/metadata/screenshot_headlines_<target>.json exists, use it
    # for that target's headlines (since tablet captures may show
    # different content than phone). Otherwise fall back to phone's headlines.
    any_wrapped = False
    for tablet_size, target, label in [(SIZE_7, "tablet_7", "7\""),
                                        (SIZE_10, "tablet_10", "10\"")]:
        raw_dir = app_dir / "store" / "screenshots" / target / "raw"
        if not raw_dir.is_dir():
            print(f"\n{label} tablet: no raw captures at {raw_dir}")
            print(f"  Skipping. To capture: emulator -avd pegasus_{target}")
            print(f"  then: python3 scripts/capture_screenshots.py "
                  f"{args.app_name} --target {target}")
            continue

        target_headlines_path = (app_dir / "metadata"
                                 / f"screenshot_headlines_{target}.json")
        if target_headlines_path.exists():
            headlines = json.loads(target_headlines_path.read_text())
            print(f"\n  using {target_headlines_path.name}")
        else:
            headlines = default_headlines

        out_dir = app_dir / "store" / "screenshots" / target
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nWrapping {label} tablet → {out_dir}")
        for slot in range(1, 8):
            src = raw_dir / f"{slot:02d}.png"
            if not src.exists():
                continue
            out = out_dir / f"{slot:02d}.png"
            if slot - 1 >= len(headlines):
                print(f"  WARNING: no headline for slot {slot}, skipping")
                continue
            h = headlines[slot - 1]
            variant = variant_for(slot - 1, SURFACE_OFFSETS[target])
            print(f"  raw/{src.name} → {out.name}  ({h['line1']} {h['line2']})"
                  f"  [{variant['gradient']}/{variant['headline']}/{variant['deco']}]")
            build_one(src, out, h, h['subtitle'], app_display_name,
                      theme, tablet_size, variant)
            any_wrapped = True

    if not any_wrapped:
        print(f"\n  No tablet raws found for {args.app_name}.")
        print(f"  Per QUALITY_PLAYBOOK §7.3, every shipping app needs phone +")
        print(f"  tablet_7 + tablet_10 screenshots. Capture tablet raws first.")
        sys.exit(1)

    print(f"\n✓ Done.")


if __name__ == "__main__":
    main()
