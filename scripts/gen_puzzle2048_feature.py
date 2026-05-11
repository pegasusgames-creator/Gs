#!/usr/bin/env python3
"""Regenerate Puzzle2048 feature graphic at 1024x500 without emojis.

Matches the existing visual: dark brown gradient + 4x4 tile board on
left + big yellow "2048 PUZZLE" + tagline on right. Drops the three
"tofu" boxes (Emoji 13.0 coin glyphs that don't render on Android <11).
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

SUPER = 2
W = 1024 * SUPER
H = 500 * SUPER
OUT = '/home/pgs/Documents/Gs/Puzzle2048/store/feature_graphic_1024x500.png'

FONT_BOLD = '/home/pgs/Documents/Gs/scripts/fonts/Poppins-Bold.ttf'
FONT_MED  = '/home/pgs/Documents/Gs/scripts/fonts/Poppins-Medium.ttf'

# Tile colors matching the 2048 game palette (approx the screenshot)
TILE_COLORS = {
    2:    (255, 230, 200),
    4:    (240, 218, 170),
    8:    (245, 195, 140),
    16:   (235, 145,  85),
    32:   (240, 110,  75),
    64:   (235,  85,  60),
    128:  (235, 200, 100),
    256:  (235, 215, 130),
    512:  (240, 220, 110),
    1024: (240, 215,  85),
    2048: (240, 205,  60),
}

# 4x4 board values (left-to-right, top-to-bottom) — matches existing banner
BOARD = [
    [2048, 512, 128, 32],
    [1024, 256,  64, 16],
    [ 512, 128,  32,  8],
    [ 256,  64,  16,  4],
]

BG_LEFT   = (35, 20, 12)
BG_RIGHT  = (15, 12,  8)
GLOW      = (240, 175, 60)
TEXT_GOLD = (242, 188, 60)
TEXT_DIM  = (220, 215, 200)


def gradient_bg():
    img = Image.new('RGB', (W, H), BG_LEFT)
    px = img.load()
    cx, cy = int(W * 0.72), int(H * 0.55)   # right-of-center
    max_r  = int(W * 0.55)
    for y in range(H):
        for x in range(W):
            # Distance from glow center (used to lighten right side)
            d = math.hypot(x - cx, y - cy) / max_r
            d = max(0.0, min(1.0, d))
            t = x / W
            base = (
                int(BG_LEFT[0] + (BG_RIGHT[0] - BG_LEFT[0]) * t),
                int(BG_LEFT[1] + (BG_RIGHT[1] - BG_LEFT[1]) * t),
                int(BG_LEFT[2] + (BG_RIGHT[2] - BG_LEFT[2]) * t),
            )
            glow_strength = max(0, 1 - d) * 0.18
            px[x, y] = (
                int(base[0] + (GLOW[0] - base[0]) * glow_strength),
                int(base[1] + (GLOW[1] - base[1]) * glow_strength),
                int(base[2] + (GLOW[2] - base[2]) * glow_strength),
            )
    return img


def round_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_tile(canvas, x, y, size, value):
    color = TILE_COLORS.get(value, (200, 200, 200))
    d = ImageDraw.Draw(canvas)
    radius = int(size * 0.13)
    round_rect(d, (x, y, x + size, y + size), radius, color)
    # Tile number — sized so 4-digit values still fit
    digits = len(str(value))
    base = int(size * 0.55)
    fs = {1: base, 2: int(base * 0.85), 3: int(base * 0.65), 4: int(base * 0.45)}[digits]
    font = ImageFont.truetype(FONT_BOLD, fs)
    tw, th = text_size(d, str(value), font)
    # Dark text on lighter tiles, light text on darker ones — use luminance
    lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    text_color = (60, 40, 25) if lum > 180 else (255, 248, 235)
    d.text(
        (x + size / 2 - tw / 2, y + size / 2 - th / 2 - int(size * 0.05)),
        str(value), font=font, fill=text_color,
    )


def main():
    img = gradient_bg()
    d = ImageDraw.Draw(img)

    # ── Left: 4x4 tile board ───────────────────────────────────────
    board_w = int(W * 0.42)
    margin  = int(W * 0.04)
    board_x = margin
    board_y = (H - board_w) // 2
    # Board background (slightly darker)
    round_rect(d, (board_x, board_y, board_x + board_w, board_y + board_w),
               int(board_w * 0.05), (24, 18, 12))
    # Tiles
    pad = int(board_w * 0.025)
    tile_size = (board_w - pad * 5) // 4
    for row in range(4):
        for col in range(4):
            tx = board_x + pad + col * (tile_size + pad)
            ty = board_y + pad + row * (tile_size + pad)
            draw_tile(img, tx, ty, tile_size, BOARD[row][col])

    # ── Right: title + tagline ─────────────────────────────────────
    title_x_center = int(W * 0.74)
    # "2048" — big
    f_title = ImageFont.truetype(FONT_BOLD, int(H * 0.30))
    title_y = int(H * 0.12)
    # Use textbbox so we get tight metric height (ignoring leading)
    _, _, tw, _ = d.textbbox((0, 0), "2048", font=f_title)
    title_actual_h = f_title.getbbox("2048")[3] - f_title.getbbox("2048")[1]
    d.text((title_x_center - tw // 2, title_y), "2048",
           font=f_title, fill=TEXT_GOLD, anchor="lt")
    # "PUZZLE" — line BELOW "2048"
    f_subtitle = ImageFont.truetype(FONT_BOLD, int(H * 0.18))
    p_text = "PUZZLE"
    _, _, pw, _ = d.textbbox((0, 0), p_text, font=f_subtitle)
    sub_y = title_y + int(H * 0.28)
    d.text((title_x_center - pw // 2, sub_y), p_text,
           font=f_subtitle, fill=TEXT_GOLD, anchor="lt")

    # Tagline 1: "Merge the tiles."
    f_tag = ImageFont.truetype(FONT_MED, int(H * 0.065))
    line1 = "Merge the tiles."
    _, _, lw, _ = d.textbbox((0, 0), line1, font=f_tag)
    tag1_y = sub_y + int(H * 0.21)
    d.text((title_x_center - lw // 2, tag1_y), line1,
           font=f_tag, fill=TEXT_DIM, anchor="lt")

    # Tagline 2: "Endless fun" — short, no emojis
    f_tag2 = ImageFont.truetype(FONT_BOLD, int(H * 0.055))
    line2 = "Endless fun"
    _, _, l2w, _ = d.textbbox((0, 0), line2, font=f_tag2)
    tag2_y = tag1_y + int(H * 0.085)
    d.text((title_x_center - l2w // 2, tag2_y), line2,
           font=f_tag2, fill=TEXT_GOLD, anchor="lt")

    # Downsample for sharp edges
    img = img.resize((1024, 500), Image.LANCZOS)
    img.save(OUT, 'PNG', optimize=True)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == '__main__':
    main()
