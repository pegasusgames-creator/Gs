#!/usr/bin/env python3
"""
Reusable phone-screenshot generator for Pegasus Games apps.

Renders <AppDir>/android/app/src/main/assets/game.html in headless Chrome at
1080x1920 for each requested state, then overlays a short marketing title in
Poppins on the bottom third. The app opts in by checking location.hash:

    #screenshot=menu
    #screenshot=gameplay
    #screenshot=shop
    #screenshot=stats
    ...

Ad banner is native (MainActivity.java) so it never shows in the HTML render.

Usage:
    python3 gen_screenshots.py <AppDir> [--specs specs.json]

Default specs live in a per-app file at
<AppDir>/store/screenshot_specs.json. If absent, the script captures a single
default-state screenshot named 01_main.png.

specs.json format:
    [
      {"hash": "menu",      "out": "01_menu.png",      "title": "Keep The Beat"},
      {"hash": "gameplay",  "out": "02_play.png",      "title": "60 Tempo Presets"},
      ...
    ]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_BOLD = str(ROOT / "fonts" / "Poppins-Bold.ttf")
FONT_XBOLD = str(ROOT / "fonts" / "Poppins-ExtraBold.ttf")
FONT_REG = str(ROOT / "fonts" / "Poppins-Regular.ttf")

W, H = 1080, 1920
CHROME = "google-chrome"


def render_state(game_html: Path, hash_state: str, out_png: Path, wait_ms: int = 1400):
    """Render game.html at 1080x1920 for a given #screenshot=STATE hash."""
    url = f"file://{game_html}#screenshot={hash_state}"
    # Use a unique user-data-dir so concurrent runs don't collide.
    with tempfile.TemporaryDirectory() as udd:
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--no-sandbox",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={W},{H}",
                f"--virtual-time-budget={wait_ms}",
                f"--user-data-dir={udd}",
                f"--screenshot={out_png}",
                url,
            ],
            check=True,
            capture_output=True,
        )
    # Normalize to exact dimensions (Chrome sometimes adds 1px).
    im = Image.open(out_png).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
        im.save(out_png)


def _wrap_for_width(draw, text, font, max_w):
    """Wrap text to fit within max_w pixels. Returns list of lines."""
    words = text.split()
    lines, cur = [], []
    for w in words:
        cand = (" ".join(cur + [w])).strip()
        if draw.textlength(cand, font=font) <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def overlay_title(png_path: Path, title: str, accent_hex: str = "#FFD700",
                  position: str = "bottom"):
    """Overlay a marketing title in Poppins ExtraBold with a contrast pad."""
    if not title:
        return
    im = Image.open(png_path).convert("RGBA")
    w, h = im.size

    # Autosize font: start at a modest size, prefer single-line fits.
    # Target: ~82% of width, ~9-11% of height for the whole band.
    max_w = int(w * 0.82)
    max_band_h = int(h * 0.13)
    size = 68
    while size > 30:
        font = ImageFont.truetype(FONT_XBOLD, size)
        draw = ImageDraw.Draw(im)
        lines = _wrap_for_width(draw, title, font, max_w)
        line_h = int(size * 1.15)
        total_h = line_h * len(lines) + (len(lines) - 1) * 4
        max_line_w = max(draw.textlength(l, font=font) for l in lines)
        if len(lines) <= 2 and max_line_w <= max_w and total_h + 40 <= max_band_h:
            break
        size -= 4

    pad_x, pad_y = 28, 18
    band_w = int(max_line_w) + pad_x * 2
    band_h = total_h + pad_y * 2
    band_x = (w - band_w) // 2
    if position == "top":
        band_y = int(h * 0.035)
    elif position == "center":
        band_y = (h - band_h) // 2
    elif position == "bottom":
        band_y = h - band_h - int(h * 0.035)
    else:  # "lower" (default) — sits in the lower third of dead space
        band_y = int(h * 0.78) - band_h // 2

    band = Image.new("RGBA", (band_w, band_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band)
    # Rounded dark band.
    bdraw.rounded_rectangle(
        [(0, 0), (band_w - 1, band_h - 1)],
        radius=20,
        fill=(14, 18, 28, 230),
    )
    # Accent underline.
    accent = tuple(int(accent_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    bdraw.rounded_rectangle(
        [(band_w // 2 - 44, band_h - 10), (band_w // 2 + 44, band_h - 6)],
        radius=2,
        fill=accent,
    )

    # Draw text lines centered inside the band.
    tdraw = ImageDraw.Draw(band)
    y = pad_y - 4
    for line in lines:
        lw = tdraw.textlength(line, font=font)
        tx = (band_w - lw) // 2
        tdraw.text((tx, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_h + 4

    im.alpha_composite(band, (band_x, band_y))
    im.convert("RGB").save(png_path, "PNG", optimize=True)


def gen_for_app(app_dir: Path, specs_file: Path = None, accent_hex: str = "#FFD700"):
    game_html = app_dir / "android/app/src/main/assets/game.html"
    if not game_html.exists():
        print(f"  [skip] no game.html in {app_dir.name}", file=sys.stderr)
        return

    out_dir = app_dir / "store/screenshots/phone"
    out_dir.mkdir(parents=True, exist_ok=True)

    if specs_file is None:
        specs_file = app_dir / "store/screenshot_specs.json"

    if specs_file.exists():
        specs = json.loads(specs_file.read_text())
    else:
        specs = [{"hash": "", "out": "01_main.png", "title": ""}]

    for spec in specs:
        out_png = out_dir / spec["out"]
        hash_state = spec.get("hash", "")
        print(f"  [render] {app_dir.name} :: {spec['out']} (hash={hash_state!r})")
        render_state(game_html, hash_state, out_png,
                     wait_ms=spec.get("wait_ms", 1400))
        if spec.get("title"):
            overlay_title(out_png, spec["title"],
                          accent_hex=spec.get("accent", accent_hex),
                          position=spec.get("position", "lower"))

    # Delete legacy placeholder if present.
    legacy = out_dir / "phone_1-main.png"
    if legacy.exists():
        legacy.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_dir", type=Path)
    ap.add_argument("--specs", type=Path, default=None)
    ap.add_argument("--accent", default="#FFD700")
    args = ap.parse_args()
    gen_for_app(args.app_dir.resolve(), args.specs, args.accent)


if __name__ == "__main__":
    main()
