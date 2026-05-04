#!/usr/bin/env python3
"""Generate Nonogram feature graphic 1024x500: warm paper background with
the app name, tagline, and a small grid sample on the right side."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 500
BG_TOP = (250, 245, 232)
BG_MID = (242, 232, 210)
BG_BOTTOM = (220, 205, 175)
GRID_LINE = (170, 145, 110)
INK_RED = (200, 56, 56)
INK_DARK = (40, 35, 30)
WARM_GRAY = (90, 79, 67)


# 5x5 sample puzzle (a small bird shape)
PATTERN = [
    [0, 1, 1, 0, 0],
    [1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
]


def gradient_bg():
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        col = (
            int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
            int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
            int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
        )
        draw.line([(0, y), (W, y)], fill=col)
    return img


def add_grain(img):
    import random
    random.seed(11)
    noise = Image.new("L", (256, 256))
    px = noise.load()
    for y in range(256):
        for x in range(256):
            px[x, y] = 128 + random.randint(-10, 10)
    noise = noise.resize(img.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    return Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.08)


def get_font(size, bold=False, serif=True):
    """Try a few common system serif/sans fonts; fall back to default."""
    candidates = []
    if serif:
        candidates += [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_grid(img, top_left, cell_size, pattern):
    draw = ImageDraw.Draw(img)
    x0, y0 = top_left
    n = 5
    line_w = max(2, cell_size // 22)
    for i in range(n + 1):
        x = x0 + i * cell_size
        y = y0 + i * cell_size
        draw.line([(x, y0), (x, y0 + n * cell_size)], fill=GRID_LINE, width=line_w)
        draw.line([(x0, y), (x0 + n * cell_size, y)], fill=GRID_LINE, width=line_w)
    inset = max(2, cell_size // 9)
    for r in range(n):
        for c in range(n):
            if pattern[r][c]:
                draw.rectangle(
                    [x0 + c * cell_size + inset,
                     y0 + r * cell_size + inset,
                     x0 + (c + 1) * cell_size - inset,
                     y0 + (r + 1) * cell_size - inset],
                    fill=INK_RED,
                )


def main():
    img = gradient_bg()
    img = add_grain(img)
    draw = ImageDraw.Draw(img)

    # Title
    title_font   = get_font(96,  bold=True, serif=True)
    sub_font     = get_font(34, bold=False, serif=True)
    footer_font  = get_font(22, bold=False, serif=False)

    # Title positioned offset-left (anti-pattern: avoid center-everything)
    draw.text((60, 110), "Nonogram", fill=INK_RED, font=title_font)
    draw.text((64, 230), "Paint by numbers — today's puzzle.", fill=INK_DARK, font=sub_font)
    draw.text((64, 280), "Logic grids. No timers. Quiet pacing.", fill=WARM_GRAY, font=sub_font)

    # Footer brand mark
    draw.text((64, H - 52), "Pegasus Games", fill=WARM_GRAY, font=footer_font)

    # 5x5 sample grid on right side
    grid_size = 280
    cell = grid_size // 5
    grid_size = cell * 5
    grid_x = W - grid_size - 80
    grid_y = (H - grid_size) // 2 + 10

    # subtle paper card under grid
    pad = 30
    draw.rounded_rectangle(
        [grid_x - pad, grid_y - pad, grid_x + grid_size + pad, grid_y + grid_size + pad],
        radius=18,
        fill=(255, 252, 244),
        outline=(220, 200, 170),
        width=2,
    )

    draw_grid(img, (grid_x, grid_y), cell, PATTERN)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Nonogram", "store", "feature_graphic_1024x500.png"
    )
    img.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
