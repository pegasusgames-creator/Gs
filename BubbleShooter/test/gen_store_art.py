#!/usr/bin/env python3
"""Bubble Shooter store art — drawn from the game's own shapes (PIL only).

Focal element = the mechanic: a glossy bubble leaves the launcher along a
dotted bank shot that bounces off the side wall, heading for a hanging
cluster of its colour, while a Pip waits in its glass bubble at the top.

    python3 BubbleShooter/test/gen_store_art.py
writes store/icon_512_playstore.png, store/icon_1024_appstore.png and
store/feature_graphic_1024x500.png (RGB, no alpha). Then run
    python3 scripts/sync_launcher_icons.py BubbleShooter
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parents[2]
STORE = BASE / "BubbleShooter" / "store"
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

# Daylight "Lime Soda" tokens (game.html PALETTE)
BG_TOP = (241, 248, 220)
BG_BOT = (214, 233, 168)
BOARD = (247, 251, 233)
EDGE = (195, 217, 141)
INK = (28, 39, 16)
ACCENT = (31, 91, 196)
ACCENT_D = (26, 63, 143)
PIP = (255, 241, 210)
PIP_INK = (59, 42, 28)
B = {1: (232, 67, 79), 2: (242, 189, 18), 3: (47, 168, 88), 4: (45, 127, 230), 5: (154, 85, 224), 6: (245, 131, 42)}


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(w, h, top, bot):
    im = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bot, y / max(1, h - 1)))
    return im


def over(im, fn):
    """Draw semi-transparent shapes on their own layer, then blend."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    im.alpha_composite(layer)


def bubble(im, cx, cy, r, col):
    """Glossy bubble: radial light from upper-left, dark rim, specular."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hx, hy = cx - r * 0.34, cy - r * 0.4
    light = lerp(col, (255, 255, 255), 0.58)
    dark = lerp(col, (0, 0, 0), 0.3)
    steps = 40
    for s in range(steps, 0, -1):
        t = s / steps
        rr = r * t
        # centre drifts toward the highlight as the rings shrink
        ox = cx + (hx - cx) * (1 - t) * 0.9
        oy = cy + (hy - cy) * (1 - t) * 0.9
        c = lerp(col, dark, (t - 0.55) / 0.45) if t > 0.55 else lerp(light, col, t / 0.55)
        d.ellipse([ox - rr, oy - rr, ox + rr, oy + rr], fill=c + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=lerp(col, (0, 0, 0), 0.45) + (150,), width=max(2, int(r * 0.07)))
    spec = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(spec)
    sd.ellipse([cx - r * 0.6, cy - r * 0.58, cx - r * 0.02, cy - r * 0.24], fill=(255, 255, 255, 190))
    spec = spec.rotate(28, center=(cx - r * 0.3, cy - r * 0.4), resample=Image.BICUBIC)
    layer.alpha_composite(spec)
    im.alpha_composite(layer)
    over(im, lambda d2: d2.ellipse([cx + r * 0.3, cy + r * 0.22, cx + r * 0.44, cy + r * 0.36], fill=(255, 255, 255, 70)))


def pip(im, cx, cy, r):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for s in range(30, 0, -1):
        t = s / 30
        c = lerp((255, 255, 255), lerp(EDGE, (255, 255, 255), 0.4), t)
        d.ellipse([cx - r * t, cy - r * t, cx + r * t, cy + r * t], fill=c + (235,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=lerp(EDGE, (0, 0, 0), 0.35) + (255,), width=max(2, int(r * 0.07)))
    br, by = r * 0.5, cy + r * 0.1
    w = max(2, int(r * 0.06))
    for ex in (-0.32, 0.32):
        er = r * 0.16
        d.ellipse([cx + ex * r - er, by - 0.36 * r - er, cx + ex * r + er, by - 0.36 * r + er], fill=PIP + (255,), outline=PIP_INK + (255,), width=w)
    d.ellipse([cx - br, by - br, cx + br, by + br], fill=PIP + (255,), outline=PIP_INK + (255,), width=w)
    for ex in (-0.19, 0.19):
        er = r * 0.075
        d.ellipse([cx + ex * r - er, by - 0.04 * r - er, cx + ex * r + er, by - 0.04 * r + er], fill=PIP_INK + (255,))
    d.arc([cx - r * 0.12, by + r * 0.02, cx + r * 0.12, by + r * 0.2], 20, 160, fill=PIP_INK + (255,), width=w)
    im.alpha_composite(layer)
    def cheeks(d2):
        for ex in (-0.32, 0.32):
            er = r * 0.08
            d2.ellipse([cx + ex * r - er, by + 0.13 * r - er, cx + ex * r + er, by + 0.13 * r + er], fill=(242, 141, 154, 170))
        d2.ellipse([cx - r * 0.55, cy - r * 0.62, cx - r * 0.1, cy - r * 0.38], fill=(255, 255, 255, 190))
    over(im, cheeks)


def dots(im, pts, r, col, gap):
    d = ImageDraw.Draw(im)
    acc = gap * 0.6
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        t = acc
        while t < L:
            x, y = x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
            t += gap
        acc = t - L


def shadow(im, box, radius, blur, alpha):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, radius, fill=(30, 50, 10, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def icon(size):
    S = 4 * size
    im = gradient(S, S, BG_TOP, BG_BOT).convert("RGBA")
    u = S / 100.0
    # glass board panel (full-bleed background keeps the corners lime)
    shadow(im, [12 * u, 10 * u, 88 * u, 92 * u], 14 * u, 3 * u, 90)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([12 * u, 9 * u, 88 * u, 90 * u], 14 * u, fill=BOARD + (255,), outline=EDGE + (255,), width=int(2.2 * u))
    r = 8.2 * u
    # hanging cluster (two rows, hex offset)
    row0 = [(24, 4), (40, 2), (56, 1), (72, 1)]
    row1 = [(32, 3), (48, 1), (64, 1)]
    for x, c in row0:
        bubble(im, x * u, 21 * u, r, B[c])
    for x, c in row1:
        bubble(im, x * u, 35 * u, r, B[c])
    pip(im, 80 * u, 35 * u, r)
    # dotted bank shot: launcher -> left wall -> target gap
    lx, ly = 50 * u, 78 * u
    wall = 16.5 * u
    tx, ty = 56 * u, 49 * u
    by = ly - (lx - wall) * (ly - ty) / ((lx - wall) + (tx - wall))
    dots(im, [(lx, ly), (wall, by), (tx, ty)], 1.6 * u, ACCENT, 5.0 * u)
    over(im, lambda d2: d2.ellipse([tx - r, ty - r, tx + r, ty + r], outline=B[1] + (200,), width=int(1.4 * u)))
    # launcher cradle + loaded bubble
    d = ImageDraw.Draw(im)
    d.ellipse([lx - 14 * u, ly + 4 * u, lx + 14 * u, ly + 10 * u], fill=lerp(EDGE, (255, 255, 255), 0.3) + (255,))
    bubble(im, lx, ly, 9.5 * u, B[1])
    return im.convert("RGB").resize((size, size), Image.LANCZOS)


def feature():
    W, H = 1024, 500
    S = 2
    im = gradient(W * S, H * S, BG_TOP, BG_BOT).convert("RGBA")
    # faint fizz rings
    def fizz(d):
        for (x, y, r) in [(80, 440, 34), (150, 478, 14), (470, 60, 24), (516, 446, 12), (36, 84, 18)]:
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=INK + (34,), width=3 * S)
    over(im, fizz)
    # board slice on the right
    bx0, by0, bx1, by1 = 560, 36, 980, 470
    shadow(im, [bx0 * S, (by0 + 8) * S, bx1 * S, (by1 + 8) * S], 28 * S, 14 * S, 100)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([bx0 * S, by0 * S, bx1 * S, by1 * S], 28 * S, fill=BOARD + (255,), outline=EDGE + (255,), width=4 * S)
    D = 38.0
    rr = D / 2 * 0.97 * S
    rows = ["44112233355", "4112223355", "66P1225..5", "6611.2..5", "6..1......"]
    rh = D * math.sqrt(3) / 2
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            x = bx0 + 1 + (D / 2 if r % 2 == 0 else D) + c * D
            y = by0 + 8 + D / 2 + r * rh
            if ch == "P":
                pip(im, x * S, y * S, rr)
            else:
                bubble(im, x * S, y * S, rr, B[int(ch)])
    # bank shot to the gap beside the reds
    lx, ly = (bx0 + bx1) / 2, by1 - 58
    wall = bx1 - 18 - 1
    tx, ty = bx0 + 1 + D + 4 * D, by0 + 8 + D / 2 + 3 * rh
    yb = ly - (wall - lx) * (ly - ty) / ((wall - lx) + (wall - tx))
    dots(im, [(lx * S, (ly - 30) * S), (wall * S, yb * S), (tx * S, ty * S)], 4 * S, ACCENT, 15 * S)
    over(im, lambda d2: d2.ellipse([tx * S - rr, ty * S - rr, tx * S + rr, ty * S + rr], outline=B[1] + (210,), width=3 * S))
    d = ImageDraw.Draw(im)
    d.ellipse([(lx - 52) * S, (ly + 14) * S, (lx + 52) * S, (ly + 36) * S], fill=lerp(EDGE, (255, 255, 255), 0.3) + (255,))
    bubble(im, lx * S, ly * S, 24 * S, B[1])
    bubble(im, (lx - 82) * S, (ly + 8) * S, 15 * S, B[4])
    # wordmark + tagline on the left
    f1 = ImageFont.truetype(FONT_BLACK, 74 * S)
    f2 = ImageFont.truetype(FONT_BOLD, 30 * S)
    d.text((56 * S, 136 * S), "BUBBLE", font=f1, fill=ACCENT_D + (255,))
    d.text((56 * S, 214 * S), "SHOOTER", font=f1, fill=ACCENT + (255,))
    d.text((60 * S, 318 * S), "Aim · Bank · Pop · Rescue", font=f2, fill=INK + (255,))
    f3 = ImageFont.truetype(FONT_BOLD, 22 * S)
    d.rounded_rectangle([60 * S, 372 * S, 320 * S, 414 * S], 21 * S, fill=ACCENT + (255,))
    d.text((80 * S, 380 * S), "500 levels · 3 goals", font=f3, fill=(255, 255, 255, 255))
    return im.convert("RGB").resize((W, H), Image.LANCZOS)


def main():
    STORE.mkdir(parents=True, exist_ok=True)
    big = icon(1024)
    big.save(STORE / "icon_1024_appstore.png")
    big.resize((512, 512), Image.LANCZOS).save(STORE / "icon_512_playstore.png")
    feature().save(STORE / "feature_graphic_1024x500.png")
    print("wrote", STORE / "icon_1024_appstore.png", STORE / "icon_512_playstore.png", STORE / "feature_graphic_1024x500.png")


if __name__ == "__main__":
    main()
