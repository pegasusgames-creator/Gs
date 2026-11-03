#!/usr/bin/env python3
"""Block Puzzle store art — drawn from the game's own shapes (PIL only).

Focal element = the mechanic: a domino drops into the last gap of a row of
glossy glazed tiles on the rose tray, and the row lights up to clear.

    python3 BlockPuzzle/test/gen_store_art.py
writes store/icon_512_playstore.png, store/icon_1024_appstore.png and
store/feature_graphic_1024x500.png (RGB, no alpha). Then run
    python3 scripts/sync_launcher_icons.py BlockPuzzle
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parents[2]
STORE = BASE / "BlockPuzzle" / "store"
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

# Daylight "Rose Glaze" tokens (game.html PALETTE)
BG_TOP = (253, 240, 244)
BG_BOT = (239, 200, 214)
WELL = (239, 200, 214)
WELL_EDGE = (220, 162, 184)
SLOT = (248, 224, 233)
ACCENT = (180, 45, 98)
ACCENT_D = (125, 31, 71)
GLOW = (255, 207, 90)
TILES = {
    "c1": (47, 98, 192), "c2": (35, 147, 110), "c3": (212, 85, 63), "c4": (224, 155, 18),
    "c5": (132, 71, 176), "c6": (23, 142, 166), "c7": (111, 154, 31),
}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def vgrad(w, h, top, bot):
    im = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bot, y / max(1, h - 1)))
    return im


def row_glow(im, x, y, w, s):
    """Warm halo under a row that is about to clear (drawn before its tiles)."""
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    pad = int(s * 0.14)
    ImageDraw.Draw(g).rounded_rectangle([x - pad, y - pad, x + w + pad, y + s + pad], int(s * 0.3),
                                        fill=GLOW + (230,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.13)))


class Layer:
    """Draw semi-transparent shapes on a clear layer, then alpha-composite
    (PIL's ImageDraw on an RGBA image REPLACES pixels instead of blending)."""
    def __init__(self, im):
        self.im = im
        self.layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.layer)

    def __enter__(self):
        return self.d

    def __exit__(self, *a):
        self.im.alpha_composite(self.layer)


def tile(im, x, y, s, col):
    """One glazed tile: darker base lip, body, top sheen, gloss pill."""
    d = ImageDraw.Draw(im, "RGBA")
    r = int(s * 0.24)
    d.rounded_rectangle([x, y + s * 0.07, x + s, y + s], r, fill=shade(col, 0.70))
    d.rounded_rectangle([x, y, x + s, y + s * 0.9], r, fill=col)
    with Layer(im) as d:
        d.rounded_rectangle([x + s * 0.06, y + s * 0.05, x + s * 0.94, y + s * 0.5], int(r * 0.8),
                            fill=lerp(col, (255, 255, 255), 0.16) + (150,))
        d.rounded_rectangle([x + s * 0.16, y + s * 0.13, x + s * 0.44, y + s * 0.28], int(s * 0.08),
                            fill=(255, 255, 255, 165))


def slot(im, x, y, s):
    d = ImageDraw.Draw(im, "RGBA")
    r = int(s * 0.24)
    d.rounded_rectangle([x, y, x + s, y + s], r, fill=SLOT)
    with Layer(im) as d:
        d.rounded_rectangle([x, y, x + s, y + s * 0.18], r, fill=shade(WELL, 0.96) + (90,))


def drop_shadow(im, box, radius, blur, alpha=70, offset=(0, 0)):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0] + offset[0], box[1] + offset[1], box[2] + offset[0], box[3] + offset[1]],
        radius, fill=(90, 18, 50, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    im.paste(sh, (0, 0), sh)


def board(im, x0, y0, cols, rows, cell, gap, filled, gap_cells=(), glow_row=None, pad=None):
    """Rose tray with a cols×rows window of cells. filled = {(r,c): colour key}."""
    pad = pad if pad is not None else int(cell * 0.28)
    w = cols * cell + (cols - 1) * gap + 2 * pad
    h = rows * cell + (rows - 1) * gap + 2 * pad
    drop_shadow(im, (x0, y0, x0 + w, y0 + h), int(cell * 0.5), cell * 0.4, 55, (0, int(cell * 0.25)))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], int(cell * 0.5), fill=WELL, outline=WELL_EDGE,
                        width=max(2, int(cell * 0.06)))
    if glow_row is not None:
        row_glow(im, x0 + pad, y0 + pad + glow_row * (cell + gap), cols * cell + (cols - 1) * gap, cell)
    for r in range(rows):
        for c in range(cols):
            x = x0 + pad + c * (cell + gap)
            y = y0 + pad + r * (cell + gap)
            if (r, c) in filled:
                tile(im, x, y, cell, TILES[filled[(r, c)]])
            else:
                slot(im, x, y, cell)
                if (r, c) in gap_cells:
                    d = ImageDraw.Draw(im, "RGBA")
                    dash = max(3, int(cell * 0.1))
                    for k in range(0, cell, dash * 2):
                        for (a, b) in (((x + k, y), (x + min(cell, k + dash), y)),
                                       ((x + k, y + cell), (x + min(cell, k + dash), y + cell)),
                                       ((x, y + k), (x, y + min(cell, k + dash))),
                                       ((x + cell, y + k), (x + cell, y + min(cell, k + dash)))):
                            d.line([a, b], fill=ACCENT, width=max(2, int(cell * 0.07)))
    return w, h, pad


def icon(size):
    S = size * 4                                     # supersample
    im = vgrad(S, S, BG_TOP, BG_BOT).convert("RGBA")
    # soft warm halo behind the board
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([S * 0.28, S * 0.02, S * 0.72, S * 0.36], fill=GLOW + (70,))
    halo = halo.filter(ImageFilter.GaussianBlur(S * 0.08))
    im.alpha_composite(halo)
    cols, rows = 5, 4
    cell = int(S * 0.112)
    gap = int(cell * 0.12)
    pad = int(cell * 0.3)
    bw = cols * cell + (cols - 1) * gap + 2 * pad
    x0 = (S - bw) // 2
    y0 = int(S * 0.34)
    filled = {(3, 0): "c1", (3, 1): "c5", (3, 4): "c2", (2, 0): "c6", (2, 4): "c3", (1, 4): "c3"}
    board(im, x0, y0, cols, rows, cell, gap, filled, gap_cells={(3, 2), (3, 3)}, glow_row=3, pad=pad)
    # glowing row edge sparks (the clear is about to fire)
    d = ImageDraw.Draw(im, "RGBA")
    ry = y0 + pad + 3 * (cell + gap) + cell // 2
    for sx, dx in ((x0 - cell * 0.32, -1), (x0 + bw + cell * 0.32, 1)):
        d.rounded_rectangle([sx - cell * 0.18, ry - cell * 0.07, sx + cell * 0.18, ry + cell * 0.07],
                            int(cell * 0.07), fill=GLOW + (255,))
    # the amber domino, lifted above its gap, with a shadow on the board
    dx = x0 + pad + 2 * (cell + gap)
    dy = int(S * 0.10)
    tilt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tile(tilt, dx, dy, cell, TILES["c4"])
    tile(tilt, dx + cell + gap, dy, cell, TILES["c4"])
    tilt = tilt.rotate(-7, center=(dx + cell + gap / 2, dy + cell / 2), resample=Image.BICUBIC)
    im.alpha_composite(tilt)
    # motion ticks between domino and gap
    tl = Layer(im)
    d = tl.d
    mx = dx + cell + gap / 2
    for k, (ox, ln) in enumerate(((0, 0.42), (-cell * 0.55, 0.3), (cell * 0.55, 0.3))):
        ty = dy + cell * 1.18
        d.line([(mx + ox, ty + cell * 0.04), (mx + ox * 1.08, ty + cell * ln)], fill=ACCENT + (200,),
               width=max(3, int(cell * 0.08)))
    tl.__exit__()
    return im.convert("RGB").resize((size, size), Image.LANCZOS)


def feature():
    W, H = 1024, 500
    S = 2
    im = vgrad(W * S, H * S, BG_TOP, BG_BOT).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # faint outline motif of tray pieces on the left
    ink = ACCENT_D + (40,)
    u = 26 * S
    mlay = Layer(im)
    d = mlay.d
    for (px, py, cells) in ((44, 34, [(0, 0), (1, 0), (1, 1)]), (330, 52, [(0, 0), (0, 1), (0, 2), (1, 1)]),
                            (430, 400, [(0, 0), (0, 1), (1, 0), (1, 1)])):
        for (r, c) in cells:
            x, y = px * S + c * u, py * S + r * u
            d.rounded_rectangle([x, y, x + u - 4 * S, y + u - 4 * S], 6 * S, outline=ink, width=3 * S)
    mlay.__exit__()
    # board on the right: 8×8 mid-game with a row about to clear
    cell = 40 * S
    gap = 5 * S
    pad = 12 * S
    bw = 8 * cell + 7 * gap + 2 * pad
    x0 = W * S - bw - 46 * S
    y0 = (H * S - bw) // 2
    layout = [
        "........",
        "....55..",
        "....56..",
        "..3.666.",
        "..33..7.",
        "..33.477",
        "..444444",   # row 6: complete except cols 0-1 (the domino's gap)
        "........",
    ]
    filled = {}
    for r, row in enumerate(layout):
        for c, ch in enumerate(row):
            if ch != ".":
                filled[(r, c)] = "c" + ch
    # row 6 is complete except the two cells the hovering domino will fill
    for c in (0, 1):
        filled.pop((6, c), None)
    board(im, x0, y0, 8, 8, cell, gap, filled, gap_cells={(6, 0), (6, 1)}, glow_row=6, pad=pad)
    # hovering domino (vertical drop) above its gap, lifted
    dx = x0 + pad
    dy = y0 + pad + 4 * (cell + gap) + int(cell * 0.25)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    tile(layer, dx, dy, cell, TILES["c1"])
    tile(layer, dx + cell + gap, dy, cell, TILES["c1"])
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([dx + 4 * S, dy + cell * 1.1, dx + 2 * cell + gap - 4 * S, dy + cell * 1.6],
                                         12 * S, fill=(90, 18, 50, 80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)))
    im.alpha_composite(layer)
    # combo burst near the glowing row
    f_combo = ImageFont.truetype(FONT_BLACK, 34 * S)
    txt = "COMBO ×3"
    tw = d.textlength(txt, font=f_combo)
    cx = x0 + bw / 2
    cx = x0 + pad + 5 * (cell + gap)
    cy = y0 + pad + 2 * S
    d = ImageDraw.Draw(im, "RGBA")
    d.text((cx - tw / 2, cy), txt, font=f_combo, fill=GLOW, stroke_width=4 * S, stroke_fill=ACCENT_D)
    # wordmark + hook on the left
    f_word = ImageFont.truetype(FONT_BLACK, 76 * S)
    f_sub = ImageFont.truetype(FONT_BOLD, 28 * S)
    lx = 56 * S
    d.text((lx, 150 * S), "BLOCK", font=f_word, fill=ACCENT_D)
    d.text((lx, 232 * S), "PUZZLE", font=f_word, fill=ACCENT)
    d.text((lx + 2 * S, 336 * S), "Drop. Clear. Combo.", font=f_sub, fill=(61, 22, 38))
    # three tray pieces as a strip under the hook
    tx, ty, tc = lx + 2 * S, 392 * S, 22 * S
    for (cells, col) in (([(0, 0), (1, 0), (1, 1)], "c3"), ([(0, 0), (0, 1), (0, 2), (1, 1)], "c2"),
                         ([(0, 0), (0, 1), (1, 0), (1, 1)], "c4")):
        for (r, c) in cells:
            tile(im, tx + c * (tc + 3 * S), ty + r * (tc + 3 * S), tc, TILES[col])
        tx += 4 * (tc + 3 * S) + 14 * S
    return im.convert("RGB").resize((W, H), Image.LANCZOS)


def main():
    STORE.mkdir(parents=True, exist_ok=True)
    icon(512).save(STORE / "icon_512_playstore.png", optimize=True)
    icon(1024).save(STORE / "icon_1024_appstore.png", optimize=True)
    feature().save(STORE / "feature_graphic_1024x500.png", optimize=True)
    print("wrote", ", ".join(p.name for p in sorted(STORE.glob("*.png"))))


if __name__ == "__main__":
    main()
