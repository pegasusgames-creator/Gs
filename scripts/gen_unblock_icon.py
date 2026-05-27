#!/usr/bin/env python3
"""Generate UnblockPuzzle icon — no "UNBLOCK" text, just the slide-the-red-block visual.

Outputs:
  UnblockPuzzle/store/icon_512_playstore.png   (512x512, no alpha)
  UnblockPuzzle/store/icon_1024_appstore.png   (1024x1024, no alpha)
  UnblockPuzzle/android/app/src/main/res/mipmap-*/ic_launcher.png
  UnblockPuzzle/android/app/src/main/res/mipmap-*/ic_launcher_round.png
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent
APP_DIR = REPO / "UnblockPuzzle"

SUPER = 3
SIZE = 1024 * SUPER

# Lavender-peach palette per CLAUDE.md UnblockPuzzle row, with a deeper
# navy-violet board surface so the colored blocks read at 48px.
BG_TOP    = (38, 32, 64)
BG_BOT    = (18, 14, 38)
BOARD     = (52, 44, 78)
CELL      = (74, 64, 102)
CELL_LINE = (28, 22, 48)
RED       = (243, 88, 96)
RED_HI    = (255, 132, 140)
BLUE      = (108, 152, 230)
GREY      = (164, 174, 196)
EXIT_HI   = (255, 218, 92)


def radial_bg(size):
    img = Image.new('RGB', (size, size), BG_BOT)
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, int(size * 0.45)
    # Big soft radial halo from BG_TOP centered toward upper-middle.
    for r in range(int(size * 1.0), 0, -size // 100):
        t = r / (size * 1.0)
        col = (
            int(BG_BOT[0] + (BG_TOP[0] - BG_BOT[0]) * (1 - t)),
            int(BG_BOT[1] + (BG_TOP[1] - BG_BOT[1]) * (1 - t)),
            int(BG_BOT[2] + (BG_TOP[2] - BG_BOT[2]) * (1 - t)),
        )
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img


def rounded_rect(d, box, radius, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_icon(size, rounded_corner=True):
    """Generate one icon. If rounded_corner, mask to a circle/squircle."""
    img = radial_bg(size)
    d = ImageDraw.Draw(img)

    # 4x4 grid centered.
    grid_size = int(size * 0.74)
    grid_x = (size - grid_size) // 2
    grid_y = (size - grid_size) // 2 + int(size * 0.005)
    cell = grid_size // 4
    pad = int(cell * 0.10)

    # Board background card.
    bx0 = grid_x - cell // 5
    by0 = grid_y - cell // 5
    bx1 = grid_x + grid_size + cell // 5
    by1 = grid_y + grid_size + cell // 5
    rounded_rect(d, [bx0, by0, bx1, by1], radius=int(cell * 0.5), fill=BOARD)

    # Grid cells.
    for r in range(4):
        for c in range(4):
            x0 = grid_x + c * cell + pad
            y0 = grid_y + r * cell + pad
            x1 = x0 + cell - pad * 2
            y1 = y0 + cell - pad * 2
            rounded_rect(d, [x0, y0, x1, y1], radius=int(cell * 0.16),
                         fill=CELL, outline=CELL_LINE, width=max(2, size // 256))

    # Exit notch on the right edge, aligned with row 1 (the red car's row).
    exit_row = 1
    ex_y0 = grid_y + exit_row * cell + pad - cell // 8
    ex_y1 = grid_y + exit_row * cell + cell - pad + cell // 8
    ex_x0 = bx1 - cell // 7
    ex_x1 = bx1 + cell // 3
    rounded_rect(d, [ex_x0, ex_y0, ex_x1, ex_y1], radius=cell // 5,
                 fill=BG_BOT)

    # Red car spanning (row=1, col=0..1) — horizontal 2-cell.
    rx0 = grid_x + 0 * cell + pad
    ry0 = grid_y + 1 * cell + pad
    rx1 = grid_x + 2 * cell - pad
    ry1 = grid_y + 2 * cell - pad
    rounded_rect(d, [rx0, ry0, rx1, ry1], radius=int(cell * 0.22), fill=RED)
    # subtle gloss highlight
    gloss = [rx0 + cell // 6, ry0 + cell // 6,
             rx1 - cell // 6, ry0 + cell // 2 - cell // 8]
    rounded_rect(d, gloss, radius=int(cell * 0.16), fill=RED_HI)

    # Blue vertical block at (col=2, row=2..3).
    bx0p = grid_x + 2 * cell + pad
    by0p = grid_y + 2 * cell + pad
    bx1p = grid_x + 3 * cell - pad
    by1p = grid_y + 4 * cell - pad
    rounded_rect(d, [bx0p, by0p, bx1p, by1p], radius=int(cell * 0.22), fill=BLUE)

    # Grey vertical block at (col=2, row=0..1) — the blocker on the exit row.
    # Actually move it off the exit row to a non-blocking position:
    gx0 = grid_x + 2 * cell + pad
    gy0 = grid_y + 0 * cell + pad
    gx1 = grid_x + 3 * cell - pad
    gy1 = grid_y + 1 * cell - pad
    rounded_rect(d, [gx0, gy0, gx1, gy1], radius=int(cell * 0.22), fill=GREY)

    # Exit arrow: tail starts at the red car's right edge, arrow tip pierces
    # through the exit notch.
    tip_x = ex_x1 + cell // 6
    arrow_y = (ex_y0 + ex_y1) // 2
    tail_x = rx1 + cell // 4
    arrow_thick = int(cell * 0.18)
    # Shaft.
    d.rounded_rectangle(
        [tail_x, arrow_y - arrow_thick // 2,
         tip_x - arrow_thick, arrow_y + arrow_thick // 2],
        radius=arrow_thick // 2, fill=EXIT_HI,
    )
    # Head (triangle).
    head_h = int(arrow_thick * 1.7)
    d.polygon(
        [
            (tip_x, arrow_y),
            (tip_x - arrow_thick * 2, arrow_y - head_h),
            (tip_x - arrow_thick * 2, arrow_y + head_h),
        ],
        fill=EXIT_HI,
    )

    # Subtle outer rim for depth.
    rim = ImageDraw.Draw(img, 'RGBA')
    rim.rounded_rectangle(
        [int(size * 0.04), int(size * 0.04),
         int(size * 0.96), int(size * 0.96)],
        radius=int(size * 0.16),
        outline=(255, 255, 255, 24),
        width=max(2, size // 256),
    )
    return img


def downscale(img, to):
    return img.resize((to, to), Image.LANCZOS)


def save_no_alpha(img, path):
    if img.mode == 'RGBA':
        bg = Image.new('RGB', img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, 'PNG', optimize=True)


def main():
    master = make_icon(SIZE)

    # Store assets.
    save_no_alpha(downscale(master, 512), APP_DIR / "store" / "icon_512_playstore.png")
    save_no_alpha(downscale(master, 1024), APP_DIR / "store" / "icon_1024_appstore.png")

    # Launcher icons at standard densities.
    DENS = [
        ("mipmap-mdpi", 48),
        ("mipmap-hdpi", 72),
        ("mipmap-xhdpi", 96),
        ("mipmap-xxhdpi", 144),
        ("mipmap-xxxhdpi", 192),
    ]
    base = APP_DIR / "android/app/src/main/res"
    for d, sz in DENS:
        img_sq = downscale(master, sz)
        save_no_alpha(img_sq, base / d / "ic_launcher.png")
        # round icon — same square for now; Android renders the alpha mask.
        save_no_alpha(img_sq, base / d / "ic_launcher_round.png")

    print(f"  ✓ Wrote store + launcher icons (no UNBLOCK text)")


if __name__ == "__main__":
    main()
