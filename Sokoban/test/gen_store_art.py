#!/usr/bin/env python3
"""gen_store_art.py — draws Sokoban's store art from the game's own shapes.

  store/icon_512_playstore.png   512x512  RGB (no alpha)
  store/icon_1024_appstore.png   1024x1024 RGB (no alpha)
  store/feature_graphic_1024x500.png

Focal element = the mechanic: the keeper shoving a wooden crate onto a teal
dock, on the clay/terracotta palette the game ships (PALETTE region). The
feature graphic pairs the wordmark with a real campaign board (level 104,
drawn tile-for-tile from LEVELS) so the art never shows a fake board.
Supersampled 4x then downscaled for clean edges. Then run
`python3 scripts/sync_launcher_icons.py Sokoban`.

    python3 Sokoban/test/gen_store_art.py
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
APP = HERE.parent
REPO = APP.parent
STORE = APP / "store"
GAME = APP / "android/app/src/main/assets/game.html"
FONT_XB = REPO / "_screenshot_tools/fonts/Poppins-ExtraBold.ttf"
FONT_MD = REPO / "scripts/fonts/Poppins-Medium.ttf"

BG_A, BG_B = (240, 160, 112), (172, 76, 40)
FLOOR, PLANK = (248, 236, 223), (234, 214, 195)
WALL, WALL_TOP = (156, 79, 51), (194, 109, 74)
CRATE, EDGE, DONE = (224, 160, 82), (142, 90, 36), (88, 166, 140)
DOCK, KEEPER = (42, 138, 125), (59, 111, 182)
INK, MUTE = (58, 33, 23), (122, 75, 57)
WHITE, PUPIL = (255, 255, 255), (29, 36, 51)


def gradient(w, h, a, b, diag=True):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            t = ((x / w) * 0.45 + (y / h) * 0.55) if diag else y / h
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return im


def crate(d, x, y, s, fill=CRATE, face=False):
    e = max(4, int(s * 0.085))
    r = int(s * 0.16)
    d.rounded_rectangle([x + s * 0.02, y + s * 0.06, x + s * 1.02, y + s * 1.06], r, fill=(60, 25, 10, 45))
    d.rounded_rectangle([x, y, x + s, y + s], r, fill=fill, outline=EDGE, width=e)
    if face:
        ey = y + s * 0.38
        for ex in (x + s * 0.34, x + s * 0.66):
            d.ellipse([ex - s * 0.07, ey - s * 0.07, ex + s * 0.07, ey + s * 0.07], fill=PUPIL)
        d.arc([x + s * 0.3, y + s * 0.38, x + s * 0.7, y + s * 0.72], 20, 160, fill=PUPIL, width=max(3, int(s * 0.06)))
        return
    i = e * 1.6
    d.line([x + i, y + i, x + s - i, y + s - i], fill=EDGE, width=e)
    d.line([x + s - i, y + i, x + i, y + s - i], fill=EDGE, width=e)


def keeper(d, x, y, s, look=(1, 0)):
    d.rounded_rectangle([x + s * 0.02, y + s * 0.06, x + s * 1.02, y + s * 1.06], int(s * 0.42), fill=(20, 30, 60, 45))
    d.rounded_rectangle([x, y, x + s, y + s], int(s * 0.42), fill=KEEPER)
    d.rounded_rectangle([x + s * 0.18, y + s * 0.07, x + s * 0.82, y + s * 0.2], int(s * 0.06), fill=(110, 150, 210))
    for ex in (x + s * 0.32, x + s * 0.68):
        ey = y + s * 0.42
        rr = s * 0.15
        d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=WHITE)
        pr = rr * 0.55
        px, py = ex + look[0] * rr * 0.4, ey + look[1] * rr * 0.4
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=PUPIL)


def dock(d, cx, cy, r, w):
    n = 14
    for k in range(n):
        a0 = k * 360 / n
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 360 / n * 0.6, fill=DOCK, width=w)
    rr = r * 0.32
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(120, 186, 176))


def icon(size):
    S = 4 * 1024
    im = gradient(S // 8, S // 8, BG_A, BG_B).resize((S, S), Image.BICUBIC)
    d = ImageDraw.Draw(im, "RGBA")
    # floor slab with planks
    d.rounded_rectangle([S * 0.08, S * 0.62, S * 0.92, S * 0.9], int(S * 0.06), fill=FLOOR)
    for k in range(1, 3):
        yy = S * 0.62 + k * S * 0.093
        d.line([S * 0.12, yy, S * 0.88, yy], fill=PLANK, width=int(S * 0.008))
    # teal glow + dock where the crate is headed
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * 0.62, S * 0.5, S * 0.96, S * 0.84], fill=140)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.035))
    im.paste(Image.new("RGB", (S, S), (150, 220, 205)), (0, 0), glow)
    d = ImageDraw.Draw(im, "RGBA")
    dock(d, S * 0.79, S * 0.67, S * 0.11, int(S * 0.024))
    crate(d, S * 0.335, S * 0.27, S * 0.38)
    for k, yy in enumerate((0.47, 0.55, 0.63)):
        d.rounded_rectangle([S * 0.03, S * yy, S * (0.075 + 0.015 * k), S * yy + S * 0.02], int(S * 0.01), fill=(255, 240, 228, 210))
    keeper(d, S * 0.1, S * 0.41, S * 0.235)
    # push arrow on the crate edge
    out = im.resize((size, size), Image.LANCZOS).convert("RGB")
    return out


def level_map(idx):
    html = GAME.read_text(encoding="utf-8")
    body = re.search(r"const LEVELS=\[(.*?)\n\];", html, re.S).group(1)
    return re.findall(r"`([^`]*)`", body)[idx]


def floor_cells(rows):
    start = next((x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch in "@+")
    seen, st = {start}, [start]
    while st:
        x, y = st.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in seen or not (0 <= n[1] < len(rows) and 0 <= n[0] < len(rows[n[1]])):
                continue
            if rows[n[1]][n[0]] == "#":
                continue
            seen.add(n); st.append(n)
    return seen


def board(d, mp, x0, y0, c):
    rows = mp.split("\n")
    fl = floor_cells(rows)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            X, Y = x0 + x * c, y0 + y * c
            if ch == "#":
                d.rounded_rectangle([X, Y, X + c, Y + c], int(c * 0.1), fill=WALL)
                d.rectangle([X + 2, Y + 2, X + c - 2, Y + c * 0.2], fill=WALL_TOP)
            elif (x, y) in fl:
                d.rectangle([X, Y, X + c, Y + c], fill=FLOOR)
                for k in (1, 2):
                    d.line([X, Y + k * c / 3, X + c, Y + k * c / 3], fill=PLANK, width=max(2, c // 22))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            X, Y = x0 + x * c, y0 + y * c
            if ch in ".+*":
                dock(d, X + c / 2, Y + c / 2, c * 0.3, max(3, int(c * 0.07)))
            if ch == "$":
                crate(d, X + c * 0.08, Y + c * 0.08, c * 0.84)
            if ch == "*":
                crate(d, X + c * 0.08, Y + c * 0.08, c * 0.84, fill=DONE, face=True)
            if ch in "@+":
                keeper(d, X + c * 0.12, Y + c * 0.12, c * 0.76, look=(0, 1))


def feature():
    W, H, k = 1024, 500, 4
    S = (W * k, H * k)
    im = gradient(W // 4, H // 4, (249, 235, 224), (240, 210, 190)).resize(S, Image.BICUBIC)
    d = ImageDraw.Draw(im, "RGBA")
    # faint crate/dock motif on the left
    for (x, y, s) in ((40, 330, 90), (400, 30, 70), (330, 380, 60)):
        d.rounded_rectangle([x * k, y * k, (x + s) * k, (y + s) * k], 12 * k, outline=(143, 61, 29, 34), width=4 * k)
        d.line([(x + 10) * k, (y + 10) * k, (x + s - 10) * k, (y + s - 10) * k], fill=(143, 61, 29, 34), width=4 * k)
        d.line([(x + s - 10) * k, (y + 10) * k, (x + 10) * k, (y + s - 10) * k], fill=(143, 61, 29, 34), width=4 * k)
    fx = ImageFont.truetype(str(FONT_XB), 92 * k)
    fm = ImageFont.truetype(str(FONT_MD), 30 * k)
    fs = ImageFont.truetype(str(FONT_MD), 22 * k)
    d.text((56 * k, 120 * k), "SOKOBAN", font=fx, fill=(122, 47, 20))
    d.text((60 * k, 240 * k), "Push every crate home.", font=fm, fill=INK)
    d.text((60 * k, 292 * k), "500 levels  ·  daily board  ·  free undo", font=fs, fill=MUTE)
    # real campaign board on the right, on a soft panel
    mp = level_map(103)
    rows = mp.split("\n")
    cols = max(len(r) for r in rows)
    c = int(min(400 / len(rows), 430 / cols)) * k
    bw, bh = cols * c, len(rows) * c
    bx, by = (W - 40) * k - bw, (H * k - bh) // 2
    sh = Image.new("L", S, 0)
    ImageDraw.Draw(sh).rounded_rectangle([bx - 8 * k, by + 4 * k, bx + bw + 8 * k, by + bh + 22 * k], 22 * k, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(14 * k))
    im.paste(Image.new("RGB", S, (120, 60, 30)), (0, 0), sh)
    d = ImageDraw.Draw(im, "RGBA")
    board(d, mp, bx, by, c)
    return im.resize((W, H), Image.LANCZOS).convert("RGB")


def main():
    STORE.mkdir(exist_ok=True)
    icon(512).save(STORE / "icon_512_playstore.png")
    icon(1024).save(STORE / "icon_1024_appstore.png")
    feature().save(STORE / "feature_graphic_1024x500.png")
    print("wrote icon_512_playstore.png, icon_1024_appstore.png, feature_graphic_1024x500.png")


if __name__ == "__main__":
    main()
