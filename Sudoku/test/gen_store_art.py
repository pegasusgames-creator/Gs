#!/usr/bin/env python3
"""
gen_store_art.py — Sudoku store art drawn with PIL from our own shapes.

  python3 Sudoku/test/gen_store_art.py

Writes store/icon_1024_appstore.png, store/icon_512_playstore.png (no alpha)
and store/feature_graphic_1024x500.png. Focal element = a 3×3 Sudoku box
mid-solve (givens in ink, the selected cell highlighted, pencil notes) on
the app's lilac-paper / indigo-ink palette. Then run
`python3 scripts/sync_launcher_icons.py Sudoku`.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
STORE = os.path.join(BASE, "Sudoku", "store")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER_TOP = (239, 236, 251)
PAPER_BOT = (214, 207, 244)
INK = (46, 42, 114)
GIVEN = (29, 26, 69)
ENTRY = (74, 65, 201)
CELL = (254, 253, 255)
LINE = (217, 213, 240)
SEL = (185, 177, 243)
SAME = (214, 209, 247)
NOTE = (97, 92, 140)
MUTE = (85, 80, 126)


def font(path, size):
    return ImageFont.truetype(path, size)


def gradient(w, h, top, bot, diag=True):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = ((x / w) * 0.35 + (y / h) * 0.65) if diag else y / h
            px[x, y] = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
    return img


def centered(d, xy, text, fnt, fill):
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((xy[0] - (r - l) / 2 - l, xy[1] - (b - t) / 2 - t), text, font=fnt, fill=fill)


def draw_box(size, cells, sel=None, notes=None, same=()):
    """A 3×3 Sudoku box: cells = 9 digits (0 empty)."""
    pad = int(size * 0.05)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * 0.14)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=INK)
    inner = [pad, pad, size - 1 - pad, size - 1 - pad]
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(inner, radius=r - pad, fill=255)
    cellw = (inner[2] - inner[0]) / 3
    grid = Image.new("RGBA", (size, size), LINE + (255,))
    g = ImageDraw.Draw(grid)
    lw = max(2, size // 120)
    fd = font(BOLD, int(cellw * 0.62))
    fn = font(BOLD, int(cellw * 0.22))
    for k in range(9):
        cx, cy = k % 3, k // 3
        x0 = inner[0] + cx * cellw + (lw if cx else 0)
        y0 = inner[1] + cy * cellw + (lw if cy else 0)
        x1 = inner[0] + (cx + 1) * cellw - (lw if cx < 2 else 0)
        y1 = inner[1] + (cy + 1) * cellw - (lw if cy < 2 else 0)
        bg = SEL if k == sel else (SAME if k in same else CELL)
        g.rectangle([x0, y0, x1, y1], fill=bg)
        v = cells[k]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if v:
            centered(g, (mx, my), str(v), fd, ENTRY if k == sel else GIVEN)
        elif notes and k in notes:
            for n in notes[k]:
                nx, ny = (n - 1) % 3, (n - 1) // 3
                centered(g, (x0 + (x1 - x0) * (nx + 0.5) / 3, y0 + (y1 - y0) * (ny + 0.5) / 3), str(n), fn, NOTE)
    img.paste(grid, (0, 0), mask)
    return img


def shadowed(base, layer, pos, blur, offset, alpha=90):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    a = layer.split()[3].point(lambda v: alpha if v > 0 else 0)
    col = Image.new("RGBA", layer.size, INK + (0,))
    col.putalpha(a)
    sh.paste(col, (pos[0] + offset[0], pos[1] + offset[1]), col)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh)
    base.alpha_composite(layer, pos)


def icon():
    S = 1024
    bg = gradient(S, S, PAPER_TOP, PAPER_BOT).convert("RGBA")
    # faint graph-paper ruling in the paper
    d = ImageDraw.Draw(bg)
    for k in range(0, S, 64):
        d.line([(k, 0), (k, S)], fill=(205, 199, 238, 255), width=2)
        d.line([(0, k), (S, k)], fill=(205, 199, 238, 255), width=2)
    box = draw_box(720, [5, 0, 3, 9, 8, 0, 0, 7, 0], sel=4,
                   notes={1: [1, 4], 5: [1, 4, 6], 6: [2, 4], 8: [1, 6]})
    shadowed(bg, box, (152, 140), 26, (0, 24))
    return bg.convert("RGB")


def feature():
    W, H = 1024, 500
    bg = gradient(W, H, PAPER_TOP, PAPER_BOT).convert("RGBA")
    d = ImageDraw.Draw(bg)
    for k in range(0, W, 40):
        d.line([(k, 0), (k, H)], fill=(222, 217, 245, 255), width=1)
    for k in range(0, H, 40):
        d.line([(0, k), (W, k)], fill=(222, 217, 245, 255), width=1)
    # right: a tilted full 9×9 grid mid-solve
    rng = random.Random(9)
    sol = [int(c) for c in "534678912672195348198342567859761423426853791713924856961537284287419635345286179"]
    G = 410
    grid = Image.new("RGBA", (G, G), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    g.rounded_rectangle([0, 0, G - 1, G - 1], radius=26, fill=INK)
    pad, thick, thin = 8, 5, 2
    cs = (G - 2 * pad - 2 * thick - 6 * thin) / 9
    fd = font(BOLD, int(cs * 0.6))
    fn = font(BOLD, int(cs * 0.22))
    sel = 40
    for i in range(81):
        r, c = divmod(i, 9)
        x0 = pad + c * cs + (c // 3) * thick + (c - c // 3) * thin
        y0 = pad + r * cs + (r // 3) * thick + (r - r // 3) * thin
        peer = (r == 4 or c == 4 or (r // 3 == 1 and c // 3 == 1))
        show = rng.random() < 0.52
        v = sol[i]
        same = show and v == sol[sel]
        bg_c = SEL if i == sel else (SAME if same else ((238, 236, 251) if peer else CELL))
        g.rectangle([x0, y0, x0 + cs, y0 + cs], fill=bg_c)
        if i == sel:
            centered(g, (x0 + cs / 2, y0 + cs / 2), str(v), fd, ENTRY)
        elif show:
            centered(g, (x0 + cs / 2, y0 + cs / 2), str(v), fd, GIVEN)
        elif rng.random() < 0.35:
            for n in sorted(rng.sample(range(1, 10), 2) + [v]):
                nx, ny = (n - 1) % 3, (n - 1) // 3
                centered(g, (x0 + cs * (nx + 0.5) / 3, y0 + cs * (ny + 0.5) / 3), str(n), fn, NOTE)
    grid = grid.rotate(-6, resample=Image.BICUBIC, expand=True)
    shadowed(bg, grid, (W - grid.width - 34, (H - grid.height) // 2 - 4), 18, (0, 16))
    d = ImageDraw.Draw(bg)
    d.text((60, 130), "SUDOKU", font=font(BOLD, 92), fill=INK)
    d.text((64, 258), "500 puzzles graded", font=font(BOLD, 30), fill=ENTRY)
    d.text((64, 298), "by solving technique", font=font(BOLD, 30), fill=ENTRY)
    d.text((64, 356), "Easy · Medium · Hard · Expert", font=font(REG, 24), fill=MUTE)
    return bg.convert("RGB")


def main():
    ic = icon()
    ic.save(os.path.join(STORE, "icon_1024_appstore.png"))
    ic.resize((512, 512), Image.LANCZOS).save(os.path.join(STORE, "icon_512_playstore.png"))
    feature().save(os.path.join(STORE, "feature_graphic_1024x500.png"))
    print("wrote icon_1024_appstore.png, icon_512_playstore.png, feature_graphic_1024x500.png")


if __name__ == "__main__":
    main()
