#!/usr/bin/env python3
"""One-off icon generator for PipeConnect: 5x5 grid, three colored pipe
routes, light cream background. Used 2026-05-25 to replace the earlier
small-grid-on-dark-gray icon. Writes:
  PipeConnect/store/icon_512_playstore.png   (512x512, no alpha)
  PipeConnect/store/icon_1024_appstore.png   (1024x1024, no alpha)
Both PNGs use opaque cream background (Play Console rejects alpha).
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "PipeConnect" / "store"

BG = (238, 244, 248)           # #eef4f8 sky-pale (PipeConnect blueprint palette)
GRID_BG = (255, 255, 255)      # white cells
GRID_BORDER = (212, 226, 236)  # #d4e2ec sky-tinged
DOT_CENTER = (255, 255, 255, 230)

# Three pipe routes (red, blue, green) on a 5x5 grid. Each entry is a list
# of (row, col) cells; endpoints are the first and last cells, drawn as
# filled dots, with the connecting line as a thick rounded path.
ROUTES = [
    ((237, 87, 87), [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0)]),  # red
    ((79, 144, 224), [(4, 0), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 4)]),                 # blue
    ((92, 200, 124), [(0, 4), (1, 4)]),                                                          # green (short, top-right)
]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)

    # Grid square fills ~78% of canvas, centered
    grid_pad = int(size * 0.11)
    grid_size = size - 2 * grid_pad
    n = 5
    cell = grid_size / n
    grid_left = grid_pad
    grid_top = grid_pad

    # Soft drop-shadow under the grid card
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        (grid_left + int(size * 0.012), grid_top + int(size * 0.018),
         grid_left + grid_size + int(size * 0.012),
         grid_top + grid_size + int(size * 0.018)),
        radius=int(size * 0.06),
        fill=(80, 70, 50, 60),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(size * 0.018)))
    img.paste(shadow, (0, 0), shadow)
    d = ImageDraw.Draw(img)

    # Grid card background
    d.rounded_rectangle(
        (grid_left, grid_top,
         grid_left + grid_size, grid_top + grid_size),
        radius=int(size * 0.055),
        fill=GRID_BG,
        outline=GRID_BORDER,
        width=max(1, int(size * 0.006)),
    )

    # Inner cells
    border_w = max(1, int(size * 0.004))
    for r in range(n):
        for c in range(n):
            x0 = grid_left + c * cell
            y0 = grid_top + r * cell
            x1 = x0 + cell
            y1 = y0 + cell
            d.rectangle((x0, y0, x1, y1), outline=GRID_BORDER, width=border_w)

    # Routes
    line_w = int(cell * 0.55)
    dot_r = cell * 0.30

    def cell_center(r, c):
        return (grid_left + (c + 0.5) * cell, grid_top + (r + 0.5) * cell)

    for color, cells in ROUTES:
        # Path through cell centers — rounded join via simple thick line
        pts = [cell_center(r, c) for r, c in cells]
        if len(pts) >= 2:
            d.line(pts, fill=color, width=line_w, joint="curve")
        # Endpoints: filled circle with subtle outline + white pip
        for r, c in (cells[0], cells[-1]):
            cx, cy = cell_center(r, c)
            d.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r),
                      fill=color,
                      outline=(0, 0, 0, 40),
                      width=max(1, int(size * 0.003)))
            inner_r = dot_r * 0.32
            d.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
                      fill=(255, 255, 255))

    return img


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size, name in [(512, "icon_512_playstore.png"),
                       (1024, "icon_1024_appstore.png")]:
        path = OUT_DIR / name
        img = draw_icon(size)
        img.save(path, "PNG", optimize=True)
        print(f"wrote {path} ({size}x{size})")


if __name__ == "__main__":
    main()
