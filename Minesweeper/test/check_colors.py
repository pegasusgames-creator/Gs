#!/usr/bin/env python3
"""check_colors.py — Minesweeper number colours are readable and
colour-blind safe in every theme.

For each theme in Minesweeper/test/themes.json (and the same palettes in
game.html THEMES, which must match):
  * every number colour n1..n8 has >= 4.5:1 contrast on the open-cell colour;
  * the mine-count digits 1-5 stay pairwise distinguishable (CIE76 delta-E
    >= 14) under normal vision and simulated protanopia / deuteranopia /
    tritanopia (Machado et al. 2009, severity 1.0) — the digit itself always
    carries the number, colour is the second channel;
  * covered tiles differ from open cells (>= 2.4:1, so hidden vs. opened
    ground is never ambiguous) and the flag pennant reads on its open-colour
    halo (>= 2.4:1).

    python3 Minesweeper/test/check_colors.py
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
THEMES = json.loads((Path(__file__).parent / "themes.json").read_text())
GAME = BASE / "Minesweeper" / "android" / "app" / "src" / "main" / "assets" / "game.html"

MACHADO = {
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def hex_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delin(c):
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lum(h):
    r, g, b = (lin(c) for c in hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lab(rgb_lin):
    r, g, b = rgb_lin
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def sim(h, kind):
    v = [lin(c) for c in hex_rgb(h)]
    if kind == "normal":
        return v
    m = MACHADO[kind]
    out = [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]
    return [lin(delin(c)) for c in out]


def de(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5


def main():
    bad = []
    for tid, t in THEMES.items():
        if tid.startswith("_"):
            continue
        for k in range(1, 9):
            c = contrast(t[f"n{k}"], t["open"])
            if c < 4.5:
                bad.append(f"{tid}: n{k} {t[f'n{k}']} on {t['open']} = {c:.2f}:1 (< 4.5)")
        for kind in ("normal", "protan", "deutan", "tritan"):
            labs = {k: lab(sim(t[f"n{k}"], kind)) for k in range(1, 6)}
            for a in range(1, 6):
                for b in range(a + 1, 6):
                    d = de(labs[a], labs[b])
                    if d < 14:
                        bad.append(f"{tid}: n{a}/n{b} only dE {d:.1f} under {kind}")
        # flags are drawn with an open-colour halo: the halo must read on the
        # tile and the pennant inside it must read on the halo
        if contrast(t["open"], t["tile"]) < 2.4:
            bad.append(f"{tid}: flag halo {t['open']} on tile {t['tile']} = {contrast(t['open'], t['tile']):.2f}:1")
        if contrast(t["flag"], t["open"]) < 2.4:
            bad.append(f"{tid}: flag {t['flag']} on its halo {t['open']} = {contrast(t['flag'], t['open']):.2f}:1")
    # game.html must ship exactly these palettes
    if GAME.exists():
        html = GAME.read_text(encoding="utf-8")
        for tid, t in THEMES.items():
            if tid.startswith("_") or tid == "event":
                continue
            m = re.search(r"\{id:'%s'[^\n]*palette:\{([^}]*)\}" % re.escape(tid), html)
            if not m:
                bad.append(f"game.html THEMES has no '{tid}' theme")
                continue
            pal = dict(re.findall(r"'([\w-]+)':'(#[0-9a-fA-F]{6})'", m.group(1)))
            for k, v in t.items():
                if k == "name":
                    continue
                if pal.get(k, "").lower() != v.lower():
                    bad.append(f"game.html theme {tid}: {k}={pal.get(k)} but themes.json says {v}")
    for b in bad:
        print("✗ " + b)
    if bad:
        return 1
    print(f"colours OK — {len([k for k in THEMES if not k.startswith('_')])} palettes: numbers >= 4.5:1, "
          "digits 1-5 separable under protan/deutan/tritan simulation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
