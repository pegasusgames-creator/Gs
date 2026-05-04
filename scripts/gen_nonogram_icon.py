#!/usr/bin/env python3
"""Generate Nonogram icon: 5x5 graph-paper grid with ink-red filled cells
forming a recognizable shape (a tiny pixel-art heart in this case).
Uses warm paper cream + ink red palette per APP_ARCHETYPES T3 texture."""
import os
from PIL import Image, ImageDraw, ImageFilter

SUPER = 3
SIZE = 1024 * SUPER

# Paper cream gradient
BG_TOP    = (250, 245, 232)   # bright cream
BG_MID    = (242, 232, 210)   # warm tan
BG_BOTTOM = (220, 205, 175)   # parchment

# Grid + ink
GRID_LINE   = (170, 145, 110)   # warm graphite
INK_RED     = (200, 56, 56)
INK_DARK    = (40, 35, 30)
PAPER_FOLD  = (235, 220, 195)

# 5x5 nonogram pattern: a heart (classic intro example)
HEART = [
    [0, 1, 0, 1, 0],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
]


def radial_bg(size):
    img = Image.new("RGB", (size, size), BG_TOP)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    max_r = int((cx ** 2 + cy ** 2) ** 0.5)
    # paint radial paper texture: brighter top-left, darker bottom-right
    for r in range(max_r, 0, -8):
        t = r / max_r
        col = (
            int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
            int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
            int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img


def add_paper_grain(img, intensity=12):
    """Lightweight grain by overlaying a low-res noise."""
    import random
    random.seed(7)
    w, h = img.size
    noise_w = 256
    noise = Image.new("L", (noise_w, noise_w))
    px = noise.load()
    for y in range(noise_w):
        for x in range(noise_w):
            px[x, y] = 128 + random.randint(-intensity, intensity)
    noise = noise.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    img2 = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.10)
    return img2


def draw_icon(size_out):
    img = radial_bg(SIZE)
    img = add_paper_grain(img)
    draw = ImageDraw.Draw(img)

    # Outer rounded card with subtle shadow
    margin = int(SIZE * 0.06)
    card_radius = int(SIZE * 0.14)

    # Subtle shadow under card
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(
        [margin + int(SIZE * 0.012), margin + int(SIZE * 0.020),
         SIZE - margin + int(SIZE * 0.012), SIZE - margin + int(SIZE * 0.020)],
        radius=card_radius,
        fill=(40, 30, 20, 35),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(SIZE * 0.012))
    img = img.convert("RGBA")
    img.alpha_composite(shadow)
    img = img.convert("RGB")

    draw = ImageDraw.Draw(img)
    # Card "page" — slightly different cream
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=card_radius,
        fill=(255, 252, 244),
        outline=PAPER_FOLD,
        width=int(SIZE * 0.005),
    )

    # 5x5 grid in the card
    grid_pad = int(SIZE * 0.16)
    grid_x0 = margin + grid_pad
    grid_y0 = margin + grid_pad
    grid_size = SIZE - 2 * margin - 2 * grid_pad
    cell = grid_size / 5
    line_w = int(SIZE * 0.006)

    # Light grid lines
    for i in range(6):
        x = int(grid_x0 + i * cell)
        y = int(grid_y0 + i * cell)
        # vertical
        draw.line([x, grid_y0, x, grid_y0 + grid_size], fill=GRID_LINE, width=line_w)
        # horizontal
        draw.line([grid_x0, y, grid_x0 + grid_size, y], fill=GRID_LINE, width=line_w)

    # Filled cells with INK_RED (drawn slightly inset, so grid lines remain visible)
    inset = int(cell * 0.10)
    for r in range(5):
        for c in range(5):
            if HEART[r][c]:
                x0 = int(grid_x0 + c * cell + inset)
                y0 = int(grid_y0 + r * cell + inset)
                x1 = int(grid_x0 + (c + 1) * cell - inset)
                y1 = int(grid_y0 + (r + 1) * cell - inset)
                draw.rectangle([x0, y0, x1, y1], fill=INK_RED)

    # Tiny clue numbers above and to the left of the grid (like real nonogram)
    # We'll draw small ink-dark digits that mimic clue counts
    try:
        from PIL import ImageFont
        font_size = int(cell * 0.35)
        # Use default font (no asset dependency)
        font = ImageFont.load_default()
    except Exception:
        font = None

    if font is not None:
        # Top clues: row sums for columns
        col_clues = []
        for c in range(5):
            col = [HEART[r][c] for r in range(5)]
            # group runs of 1s
            groups, run = [], 0
            for v in col:
                if v:
                    run += 1
                else:
                    if run: groups.append(run)
                    run = 0
            if run: groups.append(run)
            col_clues.append(groups or [0])

        for c, groups in enumerate(col_clues):
            cx = int(grid_x0 + c * cell + cell / 2)
            for i, g in enumerate(reversed(groups)):
                cy = int(grid_y0 - cell * 0.25 - i * cell * 0.30)
                if cy < margin: break
                draw.text((cx - cell * 0.06, cy - cell * 0.15),
                          str(g), fill=INK_DARK, font=font)

    # Resize to output size
    out = img.resize((size_out, size_out), Image.LANCZOS)
    return out


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "Nonogram", "store")
    os.makedirs(out_dir, exist_ok=True)
    icon_512  = draw_icon(512)
    icon_1024 = draw_icon(1024)
    p1 = os.path.join(out_dir, "icon_512_playstore.png")
    p2 = os.path.join(out_dir, "icon_1024_appstore.png")
    icon_512.save(p1)
    icon_1024.save(p2)
    print(f"Wrote {p1}")
    print(f"Wrote {p2}")


if __name__ == "__main__":
    main()
