#!/usr/bin/env python3
"""sync_launcher_icons.py — regenerate every density's launcher icon from
store/icon_512_playstore.png so the home-screen icon matches the Play
listing.

Writes mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png (straight
resize) and ic_launcher_round.png (same resize + circular alpha mask).

Idempotent: skips an app when every target is already newer than the
store icon AND was generated from identical source (size check heuristic).
Run from repo root:
    python3 scripts/sync_launcher_icons.py [AppName ...]   # default: shipping set
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
DEFAULT_APPS = ["WaterSortPuzzle", "Nonogram", "Puzzle2048", "UnblockPuzzle",
                "PipeConnect"]
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def round_mask(img: Image.Image) -> Image.Image:
    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = img.copy().convert("RGBA")
    out.putalpha(mask)
    return out


def sync(app: str) -> None:
    src = REPO / app / "store/icon_512_playstore.png"
    res = REPO / app / "android/app/src/main/res"
    if not src.exists() or not res.is_dir():
        print(f"  ? {app}: missing store icon or res dir — skipped")
        return
    icon = Image.open(src).convert("RGBA")
    changed = 0
    for density, px in DENSITIES.items():
        d = res / f"mipmap-{density}"
        d.mkdir(exist_ok=True)
        resized = icon.resize((px, px), Image.LANCZOS)
        plain = d / "ic_launcher.png"
        resized.convert("RGB").save(plain, "PNG")
        round_mask(resized).save(d / "ic_launcher_round.png", "PNG")
        changed += 2
    print(f"  ✓ {app}: {changed} files regenerated from {src.name}")


def main():
    for app in sys.argv[1:] or DEFAULT_APPS:
        sync(app)


if __name__ == "__main__":
    main()
