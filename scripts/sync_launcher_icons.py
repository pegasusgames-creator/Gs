#!/usr/bin/env python3
"""sync_launcher_icons.py — regenerate every density's launcher icon from
each app's store icon so the home-screen icon matches the Play listing.

Writes mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png (straight
resize) and ic_launcher_round.png (same resize + circular alpha mask).

Source per app (first that exists):
    store/icon_512_playstore.png   (canonical)
    store/icon_1024_appstore.png
    store/*icon*512*.png           (legacy per-app naming, e.g. foo_icon_512x512.png)
    store/*icon*1024*.png

By default runs over EVERY app dir in the repo (auto-discovered), skipping
infra dirs (_template, _release, _archive, docs, scripts, hidden, ...).
Apps with no store icon or no res dir are reported and skipped.

Run from repo root:
    python3 scripts/sync_launcher_icons.py            # all apps
    python3 scripts/sync_launcher_icons.py AppName ...  # only these
    python3 scripts/sync_launcher_icons.py --dry-run   # report, write nothing
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
SKIP_DIRS = {"docs", "scripts", "__pycache__"}


def is_app_dir(p: Path) -> bool:
    if not p.is_dir():
        return False
    if p.name.startswith((".", "_")):
        return False
    if p.name in SKIP_DIRS:
        return False
    return (p / "android/app/src/main/res").is_dir()


def discover_apps():
    return sorted(p.name for p in REPO.iterdir() if is_app_dir(p))


def find_source(app: str):
    store = REPO / app / "store"
    if not store.is_dir():
        return None
    candidates = [store / "icon_512_playstore.png", store / "icon_1024_appstore.png"]
    candidates += sorted(store.glob("*icon*512*.png"))
    candidates += sorted(store.glob("*icon*1024*.png"))
    for c in candidates:
        if c.exists():
            return c
    return None


def round_mask(img: Image.Image) -> Image.Image:
    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = img.copy().convert("RGBA")
    out.putalpha(mask)
    return out


def sync(app: str, dry_run: bool = False) -> str:
    res = REPO / app / "android/app/src/main/res"
    if not res.is_dir():
        return f"  ? {app}: no res dir — skipped"
    src = find_source(app)
    if src is None:
        return f"  ? {app}: no store icon found — skipped"
    if dry_run:
        return f"  → {app}: would sync from store/{src.name}"
    icon = Image.open(src).convert("RGBA")
    for density, px in DENSITIES.items():
        d = res / f"mipmap-{density}"
        d.mkdir(exist_ok=True)
        resized = icon.resize((px, px), Image.LANCZOS)
        resized.convert("RGB").save(d / "ic_launcher.png", "PNG")
        round_mask(resized).save(d / "ic_launcher_round.png", "PNG")
    return f"  ✓ {app}: 10 files regenerated from store/{src.name}"


def main():
    argv = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry_run = "--dry-run" in sys.argv
    apps = argv or discover_apps()
    synced = skipped = 0
    for app in apps:
        line = sync(app, dry_run)
        print(line)
        if line.strip().startswith("✓") or line.strip().startswith("→"):
            synced += 1
        else:
            skipped += 1
    print(f"\n{synced} synced, {skipped} skipped (of {len(apps)} apps)")


if __name__ == "__main__":
    main()
