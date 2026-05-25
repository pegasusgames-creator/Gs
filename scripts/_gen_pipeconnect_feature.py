#!/usr/bin/env python3
"""One-off feature-graphic generator for PipeConnect, 1024x500. Cream
background, 5x5 grid with three pipe routes on the left, app name +
subtitle on the right. Replaces the dark navy feature graphic that
clashed with the new light default theme (2026-05-25 user policy)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "PipeConnect" / "store" / "feature_graphic_1024x500.png"

W, H = 1024, 500
BG = (238, 244, 248)           # #eef4f8 sky-pale
CARD_BG = (255, 255, 255)
GRID_BORDER = (212, 226, 236)  # #d4e2ec sky-tinged
TEXT_PRIMARY = (30, 58, 95)    # #1e3a5f deep ocean blue
TEXT_SOFT = (90, 115, 144)     # #5a7390
ACCENT_BLUE = (59, 109, 184)   # #3b6db8

ROUTES = [
    ((237, 87, 87), [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 2), (2, 1), (2, 0)]),
    ((79, 144, 224), [(4, 0), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 4)]),
    ((92, 200, 124), [(0, 4), (1, 4)]),
    ((255, 193, 84), [(4, 2), (4, 3)]),
]


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Subtle radial accent on the right side — soft sky-blue glow
    accent = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(accent)
    ad.ellipse((W * 0.55, -120, W + 120, H + 120), fill=(180, 215, 240, 90))
    accent = accent.filter(ImageFilter.GaussianBlur(60))
    img.paste(accent, (0, 0), accent)
    d = ImageDraw.Draw(img)

    # Left: grid card
    card_size = int(H * 0.78)
    card_left = int(W * 0.06)
    card_top = (H - card_size) // 2
    # Shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        (card_left + 6, card_top + 14,
         card_left + card_size + 6, card_top + card_size + 14),
        radius=28, fill=(70, 60, 40, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img.paste(shadow, (0, 0), shadow)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle(
        (card_left, card_top, card_left + card_size, card_top + card_size),
        radius=26, fill=CARD_BG, outline=GRID_BORDER, width=3)

    n = 5
    cell = card_size / n
    for r in range(n):
        for c in range(n):
            x0 = card_left + c * cell
            y0 = card_top + r * cell
            d.rectangle((x0, y0, x0 + cell, y0 + cell),
                        outline=GRID_BORDER, width=2)

    def center(r, c):
        return (card_left + (c + 0.5) * cell, card_top + (r + 0.5) * cell)

    line_w = int(cell * 0.55)
    dot_r = cell * 0.30
    for color, cells in ROUTES:
        pts = [center(r, c) for r, c in cells]
        if len(pts) >= 2:
            d.line(pts, fill=color, width=line_w, joint="curve")
        for r, c in (cells[0], cells[-1]):
            cx, cy = center(r, c)
            d.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r),
                      fill=color, outline=(0, 0, 0, 40), width=2)
            ir = dot_r * 0.32
            d.ellipse((cx - ir, cy - ir, cx + ir, cy + ir), fill=(255, 255, 255))

    # Right: text block
    text_left = card_left + card_size + int(W * 0.05)
    title_font = _font(78)
    sub_font = _font(28)
    tag_font = _font(22)

    d.text((text_left, int(H * 0.30)), "PIPE", font=title_font, fill=(237, 87, 87))
    d.text((text_left, int(H * 0.30) + 80), "CONNECT", font=title_font, fill=ACCENT_BLUE)
    d.text((text_left, int(H * 0.30) + 175),
           "Connect the dots. Fill the grid.",
           font=sub_font, fill=TEXT_PRIMARY)
    d.text((text_left, int(H * 0.30) + 215),
           "150 levels  ·  5x5 to 10x10  ·  Offline",
           font=tag_font, fill=TEXT_SOFT)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
