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

# Per-app composition overrides, loaded from <app>/metadata/wrap_profile.json
# when present. Absent profile == empty dict == original behavior, so the
# grandfathered apps (WS/Nono/P2048/UB) are never restyled by a new profile.
PROFILE = {}


def tighten_board(shot):
    """Collapse the big near-uniform vertical gaps above/below a square game
    board so it fills far more of the framed phone. Detects 'empty' rows by
    low per-row colour variance and shrinks any empty run longer than
    `tighten_max_gap` (fraction of height) down to `tighten_keep`. Header,
    board and footer (all have content → variance) are preserved."""
    from PIL import ImageStat
    rgb = shot.convert('RGB')
    w, h = rgb.size
    thresh = PROFILE.get('tighten_var', 6.0)
    keep = int(h * PROFILE.get('tighten_keep', 0.022))
    max_gap = int(h * PROFILE.get('tighten_max_gap', 0.045))
    empties = [max(ImageStat.Stat(rgb.crop((0, y, w, y + 1))).stddev) < thresh
               for y in range(h)]
    segs = []
    y = 0
    while y < h:
        y0 = y
        run_empty = empties[y]
        while y < h and empties[y] == run_empty:
            y += 1
        if run_empty and (y - y0) > max_gap:
            segs.append((y0, y0 + keep))
        else:
            segs.append((y0, y))
    new_h = sum(b - a for a, b in segs)
    out = Image.new('RGB', (w, new_h), (255, 255, 255))
    cy = 0
    for a, b in segs:
        out.paste(rgb.crop((0, a, w, b)), (0, cy))
        cy += b - a
    return out

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

def _hex(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def make_gradient_bg(theme, direction="tl-br"):
    """3-stop gradient; corner placement varies by direction so each
    variant reads as a visually different background. A profile may supply
    `gradient_stops` (3 hex colours) to override the theme's murky defaults."""
    stops = PROFILE.get("gradient_stops")
    if stops:
        c1, c2, c3 = (_hex(stops[0]), _hex(stops[1]), _hex(stops[2]))
    else:
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


# ---------------------- v2 wrapper layers (profile: wrapper="v2") ----------
# A brighter, on-brand frame: an energetic gradient (set via gradient_stops),
# soft radial blobs in the game's route palette, faint rounded pipe-route
# motifs, and a halo behind the phone for depth. Gated by the profile so the
# grandfathered apps keep the original flat treatment.

import math as _math


def _radial_mask(diam, peak, falloff=1.7):
    """L-mode soft radial falloff (peak alpha at centre → 0 at edge)."""
    s = 72
    m = Image.new('L', (s, s), 0)
    px = m.load()
    c = (s - 1) / 2.0
    maxr = s / 2.0
    for y in range(s):
        for x in range(s):
            r = _math.hypot(x - c, y - c) / maxr
            px[x, y] = int(peak * max(0.0, 1.0 - r) ** falloff) if r < 1 else 0
    return m.resize((max(1, diam), max(1, diam)), Image.BICUBIC)


def draw_palette_blobs(canvas, blobs):
    """blobs: list of (cx_frac, cy_frac, radius_frac, '#hex', peak_alpha)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for cx, cy, rad, hexcol, peak in blobs:
        d = int(W * rad * 2)
        col = _hex(hexcol)
        tile = Image.new('RGBA', (d, d), (col[0], col[1], col[2], 0))
        tile.putalpha(_radial_mask(d, peak))
        layer.alpha_composite(tile, (int(W * cx) - d // 2, int(H * cy) - d // 2))
    canvas.alpha_composite(layer)


def draw_pipe_motifs(canvas, paths, hexcol, alpha, width_frac=0.02):
    """Faint rounded pipe-route motifs drifting behind the phone.
    paths: list of polylines, each a list of (x_frac, y_frac) points."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = _hex(hexcol)
    rgba = (col[0], col[1], col[2], alpha)
    lw = int(W * width_frac)
    for path in paths:
        pts = [(int(W * x), int(H * y)) for x, y in path]
        if len(pts) >= 2:
            d.line(pts, fill=rgba, width=lw, joint='curve')
        for ex, ey in (pts[0], pts[-1]):
            r = int(lw * 0.62)
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=rgba)
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius=3)))


def draw_phone_halo(canvas, cx, cy, diam, hexcol, peak):
    """Soft radial halo behind the phone so it lifts off the background."""
    col = _hex(hexcol)
    tile = Image.new('RGBA', (diam, diam), (col[0], col[1], col[2], 0))
    tile.putalpha(_radial_mask(diam, peak, falloff=1.3))
    canvas.alpha_composite(tile, (cx - diam // 2, cy - diam // 2))


# Default v2 ambient layout (fractions of W/H). Blob colours are the game's
# route palette; positions hug the edges so the phone column stays clean.
V2_BLOBS = [
    (0.10, 0.12, 0.30, '#ff5a5a', 70),   # red   top-left
    (0.90, 0.14, 0.26, '#ff9f1c', 64),   # orange top-right
    (0.96, 0.46, 0.30, '#ffd166', 56),   # yellow right
    (0.06, 0.52, 0.30, '#2ec4b6', 60),   # teal  left
    (0.12, 0.88, 0.30, '#3a86ff', 66),   # blue  bottom-left
    (0.90, 0.90, 0.28, '#c44fe0', 66),   # magenta bottom-right
    (0.50, 0.30, 0.34, '#7b2ff7', 40),   # violet centre wash (subtle)
]
V2_MOTIFS = [
    [(0.05, 0.20), (0.05, 0.30), (0.18, 0.30)],
    [(0.95, 0.30), (0.95, 0.40), (0.82, 0.40), (0.82, 0.47)],
    [(0.08, 0.70), (0.20, 0.70), (0.20, 0.62)],
    [(0.92, 0.66), (0.92, 0.78), (0.80, 0.78)],
]


# ---------------------- ambient decoration pieces (per-app) ----------------
# Restraint brief: 4-7 soft, blurred, low-opacity copies of an app's own
# signature game pieces, scattered in the corners/edges only (never the
# centre). Each app's wrap_profile.json supplies `pieces`; positions jitter
# per slot so no two screenshots look identical. Shapes are sampled from the
# app's real art + palette.

def _piece_tile(shape, size, hexcol, alpha, text=None):
    """Render one signature piece into a transparent square tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = _hex(hexcol)
    rgba = (col[0], col[1], col[2], alpha)
    light = (min(255, col[0] + 60), min(255, col[1] + 60), min(255, col[2] + 60),
             int(alpha * 0.85))
    w = max(2, int(size * 0.26))
    pad = int(size * 0.20)
    mid = size // 2
    if shape == 'pipe_straight':
        d.line([(pad, mid), (size - pad, mid)], fill=rgba, width=w, joint='curve')
        for px in (pad, size - pad):
            r = w // 2
            d.ellipse([px - r, mid - r, px + r, mid + r], fill=rgba)
    elif shape == 'pipe_elbow':
        pts = [(pad, pad), (pad, size - pad), (size - pad, size - pad)]
        d.line(pts, fill=rgba, width=w, joint='curve')
        for px, py in (pts[0], pts[-1]):
            r = w // 2
            d.ellipse([px - r, py - r, px + r, py + r], fill=rgba)
    elif shape == 'dot':
        r = int(size * 0.30)
        d.ellipse([mid - r, mid - r, mid + r, mid + r], fill=rgba)
        r2 = int(r * 0.42)
        d.ellipse([mid - r2, mid - r2, mid + r2, mid + r2], fill=light)
    elif shape == 'tile':            # rounded square (2048-style) + optional number
        rr = int(size * 0.16)
        box = [pad, pad, size - pad, size - pad]
        d.rounded_rectangle(box, radius=rr, fill=rgba)
        if text:
            # dark glyph on light tiles, white on saturated tiles (2048 rule)
            lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
            tcol = (119, 110, 101, alpha) if lum > 180 else (255, 255, 255, alpha)
            fsize = int(size * (0.34 if len(str(text)) <= 2 else
                                0.26 if len(str(text)) == 3 else 0.20))
            font = pick_font('heavy', fsize)
            tb = d.textbbox((0, 0), str(text), font=font)
            tx = (size - (tb[2] - tb[0])) // 2 - tb[0]
            ty = (size - (tb[3] - tb[1])) // 2 - tb[1]
            d.text((tx, ty), str(text), font=font, fill=tcol)
    elif shape == 'block':           # solid rounded block (unblock/sokoban)
        rr = int(size * 0.12)
        d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=rr,
                            fill=rgba)
        d.rounded_rectangle([pad + w // 3, pad + w // 3, size - pad - w // 3,
                            size - pad - w // 3], radius=rr, outline=light,
                            width=max(2, w // 5))
    elif shape == 'cell':            # filled nonogram cell cluster
        rr = int(size * 0.14)
        d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=rr,
                            fill=rgba)
    elif shape == 'tube':            # water-sort tube with a band
        rr = int(size * 0.42)
        x0, x1 = int(size * 0.34), int(size * 0.66)
        d.rounded_rectangle([x0, pad, x1, size - pad], radius=rr, outline=rgba,
                            width=max(3, w // 3))
        d.rounded_rectangle([x0, int(size * 0.55), x1, size - pad - w // 4],
                            radius=rr // 2, fill=rgba)
    elif shape == 'ring':            # hollow ring (lights-out / reaction)
        r = int(size * 0.32)
        d.ellipse([mid - r, mid - r, mid + r, mid + r], outline=rgba,
                  width=max(3, w // 2))
    # ---- kawaii / abundant vocabulary (crisp, full-colour) ----
    elif shape == 'blob':            # gooey slime blob with gloss
        d.ellipse([pad, int(size * 0.30), size - pad, size - pad], fill=rgba)
        d.ellipse([int(size * 0.28), pad, int(size * 0.80), int(size * 0.64)], fill=rgba)
        d.ellipse([pad, int(size * 0.46), int(size * 0.56), size - pad], fill=rgba)
        gloss = (255, 255, 255, int(alpha * 0.55))
        d.ellipse([int(size * 0.40), int(size * 0.40),
                   int(size * 0.60), int(size * 0.56)], fill=gloss)
    elif shape == 'sparkle':         # 4-point star
        arm, ww = int(size * 0.46), int(size * 0.11)
        d.polygon([(mid, mid - arm), (mid + ww, mid), (mid, mid + arm), (mid - ww, mid)], fill=rgba)
        d.polygon([(mid - arm, mid), (mid, mid + ww), (mid + arm, mid), (mid, mid - ww)], fill=rgba)
        d.ellipse([mid - ww, mid - ww, mid + ww, mid + ww], fill=(255, 255, 255, alpha))
    elif shape == 'heart':
        r, top = int(size * 0.20), int(size * 0.38)
        d.ellipse([mid - 2 * r, top - r, mid, top + r], fill=rgba)
        d.ellipse([mid, top - r, mid + 2 * r, top + r], fill=rgba)
        d.polygon([(mid - 2 * r + 2, top), (mid + 2 * r - 2, top), (mid, size - pad)], fill=rgba)
    elif shape == 'bubble':          # translucent bubble w/ highlight
        r = int(size * 0.30)
        d.ellipse([mid - r, mid - r, mid + r, mid + r],
                  fill=(col[0], col[1], col[2], int(alpha * 0.35)))
        d.ellipse([mid - r, mid - r, mid + r, mid + r], outline=rgba, width=max(3, int(size * 0.05)))
        hr = int(r * 0.30)
        hx, hy = mid - int(r * 0.4), mid - int(r * 0.4)
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255, int(alpha * 0.85)))
    elif shape == 'drip':            # teardrop
        r, by = int(size * 0.26), int(size * 0.62)
        d.ellipse([mid - r, by - r, mid + r, by + r], fill=rgba)
        d.polygon([(mid - int(r * 0.5), by - int(r * 0.3)),
                   (mid + int(r * 0.5), by - int(r * 0.3)), (mid, pad)], fill=rgba)
    elif shape == 'star':            # 5-point star
        R, r2 = size * 0.40, size * 0.40 * 0.42
        pts = []
        for k in range(10):
            ang = -_math.pi / 2 + k * _math.pi / 5
            rad = R if k % 2 == 0 else r2
            pts.append((mid + rad * _math.cos(ang), mid + rad * _math.sin(ang)))
        d.polygon(pts, fill=rgba)
    elif shape == 'burst':           # firework explosion
        R = size * 0.44
        lw = max(2, int(size * 0.035))
        for k in range(12):
            ang = k * 2 * _math.pi / 12
            ex, ey = mid + R * _math.cos(ang), mid + R * _math.sin(ang)
            d.line([(mid, mid), (ex, ey)], fill=rgba, width=lw)
            rr = int(size * 0.03)
            d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=rgba)
        c2 = int(size * 0.05)
        d.ellipse([mid - c2, mid - c2, mid + c2, mid + c2], fill=(255, 255, 255, alpha))
    elif shape == 'cloud':
        y = int(size * 0.56)
        d.ellipse([int(size * 0.10), y - int(size * 0.18), int(size * 0.46), y + int(size * 0.18)], fill=rgba)
        d.ellipse([int(size * 0.32), int(size * 0.28), int(size * 0.70), y + int(size * 0.16)], fill=rgba)
        d.ellipse([int(size * 0.54), y - int(size * 0.16), int(size * 0.90), y + int(size * 0.18)], fill=rgba)
        d.rounded_rectangle([int(size * 0.16), y, int(size * 0.84), y + int(size * 0.20)],
                            radius=int(size * 0.1), fill=rgba)
    elif shape == 'clock':
        r = int(size * 0.38)
        d.ellipse([mid - r, mid - r, mid + r, mid + r],
                  fill=(col[0], col[1], col[2], int(alpha * 0.16)))
        d.ellipse([mid - r, mid - r, mid + r, mid + r], outline=rgba, width=max(3, int(size * 0.05)))
        d.line([(mid, mid), (mid, mid - int(r * 0.6))], fill=rgba, width=max(3, int(size * 0.045)))
        d.line([(mid, mid), (mid + int(r * 0.45), mid)], fill=rgba, width=max(3, int(size * 0.045)))
        cc = int(size * 0.03)
        d.ellipse([mid - cc, mid - cc, mid + cc, mid + cc], fill=rgba)
    elif shape == 'shard':           # triangle (kaleidoscope)
        d.polygon([(mid, pad), (size - pad, size - pad), (pad, size - pad)], fill=rgba)
    return img


def draw_decoration_pieces(canvas, pieces, slot, layer='all'):
    """pieces: list of dicts {shape,x,y,size,color,alpha,rot,blur,shadow,front}.
    Positions + rotation jitter deterministically by slot so each screenshot
    varies. `layer` selects 'back' (default pieces, drawn behind the phone),
    'front' (pieces with front=true, drawn over the phone edge), or 'all'."""
    for i, p in enumerate(pieces):
        is_front = bool(p.get('front'))
        if layer == 'back' and is_front:
            continue
        if layer == 'front' and not is_front:
            continue
        size = max(8, int(W * p.get('size', 0.3)))
        tile = _piece_tile(p['shape'], size, p.get('color', '#ffffff'),
                           p.get('alpha', 60), text=p.get('num'))
        jx = ((slot * 37 + i * 53) % 7 - 3) / 100.0
        jy = ((slot * 29 + i * 41) % 7 - 3) / 100.0
        rot = p.get('rot', 0) + ((slot * 17 + i * 23) % 21 - 10)
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
        blur = p.get('blur', 8)
        if blur:
            tile = tile.filter(ImageFilter.GaussianBlur(radius=blur))
        cx = int(W * (p['x'] + jx)) - tile.width // 2
        cy = int(H * (p['y'] + jy)) - tile.height // 2
        if p.get('shadow'):
            # soft drop shadow from the piece silhouette (abundant/crisp style)
            alpha_ch = tile.split()[3].point(lambda a: int(a * 0.40))
            sh = Image.new('RGBA', tile.size, (25, 18, 40, 0))
            sh.putalpha(alpha_ch)
            sh = sh.filter(ImageFilter.GaussianBlur(radius=max(4, size // 22)))
            off = max(4, size // 26)
            canvas.alpha_composite(sh, (cx + off, cy + off))
        canvas.alpha_composite(tile, (cx, cy))


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
              app_display_name, theme, variant, slot=0):
    canvas = make_gradient_bg(theme, variant["gradient"]).convert('RGBA')
    v2 = PROFILE.get('wrapper') == 'v2'
    if PROFILE.get('blobs'):
        # Soft, blurred colour washes behind everything — fills out an
        # abundant background so it isn't just crisp stickers on flat gradient.
        draw_palette_blobs(canvas, PROFILE['blobs'])
    if PROFILE.get('pieces'):
        # On-theme decorations from THIS app's own pieces. Back layer draws
        # behind the phone; front pieces (front=true) draw after the phone so
        # they peek over its edge (abundant style). Density/opacity/blur are
        # set per-app in the profile.
        draw_decoration_pieces(canvas, PROFILE['pieces'], slot, layer='back')
    elif v2:
        draw_palette_blobs(canvas, PROFILE.get('blobs', V2_BLOBS))
        draw_pipe_motifs(canvas, PROFILE.get('motifs', V2_MOTIFS),
                         PROFILE.get('motif_color', '#ffffff'),
                         PROFILE.get('motif_alpha', 26))
    else:
        draw_decorations(canvas, theme, variant["deco"])

    bottom = variant["headline"] == "bottom"
    shot = Image.open(src_path)
    if PROFILE.get('tighten_board'):
        shot = tighten_board(shot)
    hf_top = PROFILE.get('height_frac_top', 0.62)
    hf_bottom = PROFILE.get('height_frac_bottom', 0.52)
    framed, fw, fh = frame_screenshot(
        shot, theme, height_frac=(hf_bottom if bottom else hf_top))

    # Framed screenshot always stays horizontally centered.
    fx = (W - fw) // 2

    if bottom:
        fy = int(H * 0.060)
        draw_headline(canvas, line1, line2, subtitle, theme,
                      y_start=fy + fh + int(H * 0.035))
    else:
        headline_bottom = draw_headline(canvas, line1, line2, subtitle, theme)
        fy = headline_bottom + int(H * PROFILE.get('headline_gap', 0.03))
        # Anchor: when there's slack below, drop the phone so the block sits
        # centered in the lower region instead of floating under the headline.
        bottom_limit = int(H * PROFILE.get('phone_bottom', 0.94)) - fh
        anchor = PROFILE.get('phone_anchor')
        if anchor is not None and fy < bottom_limit:
            fy = min(bottom_limit, fy + int((bottom_limit - fy) * anchor))
        if fy > bottom_limit:
            fy = bottom_limit

    if v2:
        # Halo behind the phone for separation/depth (drawn before the phone).
        draw_phone_halo(canvas, fx + fw // 2, fy + fh // 2,
                        int(fw * 1.55), PROFILE.get('halo_color', '#ffffff'),
                        PROFILE.get('halo_alpha', 64))
    canvas.alpha_composite(framed, (fx, fy))
    if PROFILE.get('pieces'):
        # Front decorations peek over the phone edge for depth (abundant).
        draw_decoration_pieces(canvas, PROFILE['pieces'], slot, layer='front')
    draw_footer(canvas, app_display_name, theme)

    out = canvas.resize((OUT_W, OUT_H), Image.LANCZOS)
    flat = Image.new('RGB', (OUT_W, OUT_H), theme["bg_bottom"])
    flat.paste(out, mask=out.split()[3])
    flat.save(out_path, 'PNG', optimize=True)


# ---------------------- main ----------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name", help="App folder name (e.g., WaterSort)")
    ap.add_argument("--iphone", action="store_true",
                    help="generate 3 Apple iPhone 6.9\" (1320x2868) shots into "
                         "store/screenshots/iphone_6_9/ instead of the phone set")
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

    global PROFILE
    profile_path = app_dir / "metadata" / "wrap_profile.json"
    PROFILE = json.loads(profile_path.read_text()) if profile_path.exists() else {}
    if PROFILE:
        print(f"Wrap profile: {profile_path.name} → {sorted(PROFILE)}")

    theme = get_theme(app_name)
    print(f"Theme for {app_name}: {theme['mood']}")
    print(f"  bg gradient: {theme['bg_top_left']} → {theme['bg_top_right']} → {theme['bg_bottom']}")

    # App display name — try title.txt, fall back to folder name
    title_path = app_dir / "metadata" / "en-US" / "title.txt"
    if title_path.exists():
        app_display_name = title_path.read_text().strip()
    else:
        app_display_name = app_name

    # iPhone 6.9" mode re-wraps 3 of the phone gameplay raws at Apple's
    # 1320x2868 canvas (App Store requires ≥1; we ship 3 like the other
    # apps). Same gameplay raws, re-framed for the taller iPhone aspect —
    # the frame layout differs, so these are genuinely distinct artifacts.
    if args.iphone:
        global OUT_W, OUT_H, W, H
        OUT_W, OUT_H = 1320, 2868
        W, H = OUT_W * S, OUT_H * S
        out_dir = app_dir / "store" / "screenshots" / "iphone_6_9"
        out_dir.mkdir(parents=True, exist_ok=True)
        # Pick 3 spread-out gameplay slots (skip the themes/non-gameplay
        # slot 6 when 7 exist). Prefer early/mid/late for variety.
        candidates = [i for i in range(n_slots) if (i + 1) != 6]
        if len(candidates) >= 3:
            picks = [candidates[0], candidates[len(candidates) // 2], candidates[-1]]
        else:
            picks = list(range(min(3, n_slots)))
        print(f"\nWrapping 3 iPhone 6.9\" shots for {app_name} ({OUT_W}x{OUT_H})...")
        print(f"  source raws: {[p + 1 for p in picks]}")
        for out_idx, i in enumerate(picks):
            src = raw_dir / f"{i+1:02d}.png"
            out = out_dir / f"{out_idx+1:02d}.png"
            if not src.exists():
                print(f"  WARNING: missing {src.name}, skipping")
                continue
            h = headlines[i]
            variant = variant_for(out_idx)
            print(f"  raw/{src.name} → {out.name}  ({h['line1']} {h['line2']})")
            build_one(src, out, h['line1'], h['line2'], h['subtitle'],
                      app_display_name, theme, variant, slot=out_idx)
        print()
        print(f"✓ Done. iPhone 6.9\" screenshots ready at {out_dir}")
        return

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
                  app_display_name, theme, variant, slot=i)

    print()
    print(f"✓ Done. Phone screenshots ready at {out_dir}")
    print("  Verify visually that the wrapped output has gradient bg, headline,")
    print("  framed gameplay shot, and footer — NOT raw device output.")


if __name__ == "__main__":
    main()
