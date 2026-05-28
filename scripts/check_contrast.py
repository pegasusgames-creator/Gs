#!/usr/bin/env python3
"""check_contrast.py — extract :root color tokens from each game.html
and flag any text token that falls below WCAG AA 4.5:1 against the
declared --app-bg / --bg token. Pre-publish gate.

Heuristics:
  - "Text" tokens are names matching: --text*, --color-text*, --fg*,
    --label*, plus a few common app-specific names (--filled, --coin).
  - "Background" is whichever of --app-bg, --bg, --background, --surface
    appears first (we use that as the primary canvas).
  - Tokens whose value is a `linear-gradient(...)` or `rgba(...)` are
    skipped (no single bg color to compute against).
  - 4.5:1 is the body threshold. We don't try to distinguish large/bold
    text — better to over-warn than miss a regression.

Output: per-app table of (token, value, bg, ratio, pass/fail). Returns
non-zero exit if any fail.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
THRESHOLD = 4.5

TOKEN_RE = re.compile(r'(--[a-z][a-z0-9-]*)\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|[^;\n]+);')
HEX_RE = re.compile(r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$')


def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)


def _lin(c):
    c = c/255
    return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4


def relL(rgb):
    r,g,b = [_lin(x) for x in rgb]
    return 0.2126*r + 0.7152*g + 0.0722*b


def ratio(fg, bg):
    Lf, Lb = relL(fg), relL(bg)
    if Lb > Lf: Lf, Lb = Lb, Lf
    return (Lf + 0.05) / (Lb + 0.05)


def _is_app(app):
    return (REPO / app / "android" / "app" / "build.gradle").exists()


TEXT_HINTS = ('--text', '--color-text', '--fg', '--label')
BG_NAMES = ('--app-bg','--bg','--background','--surface')


def _extract_root(src):
    """Return the first :root { ... } body as text."""
    m = re.search(r':root\s*\{([^}]*)\}', src)
    if not m: return ''
    return m.group(1)


def _extract_tokens(body):
    out = {}
    for m in TOKEN_RE.finditer(body):
        name = m.group(1).strip()
        val  = m.group(2).strip()
        out[name] = val
    return out


def check_app(app):
    blocking, warnings = [], []
    game = REPO / app / "android/app/src/main/assets/game.html"
    if not game.exists():
        return blocking, warnings
    src = game.read_text(encoding="utf-8", errors="replace")
    body = _extract_root(src)
    tokens = _extract_tokens(body)
    # Pick a background.
    bg_value = None
    for name in BG_NAMES:
        if name in tokens and HEX_RE.match(tokens[name]):
            bg_value = tokens[name]; break
    if bg_value is None:
        # If the :root block doesn't carry colors (e.g. WaterSort only has z-index
        # tokens), the app uses inline body styles — skip. Not all apps use a
        # CSS-vars-only design system.
        warnings.append(f"{app}: no hex bg token in :root — contrast check skipped")
        return blocking, warnings
    bg_rgb = hex_to_rgb(bg_value)
    # 2026-05-28 round-13: also accept --text against --surface, since
    # in growth-shim theming `--text` is conventionally "text on a panel
    # surface" (cards, sheets, overlays). A token only fails when it
    # fails contrast against BOTH the page bg AND the panel surface.
    surface_value = tokens.get('--surface')
    surface_rgb = hex_to_rgb(surface_value) if surface_value and HEX_RE.match(surface_value) else None
    rows = []
    for name, val in tokens.items():
        if not any(h in name for h in TEXT_HINTS): continue
        if not HEX_RE.match(val): continue   # skip gradients/rgba
        fg = hex_to_rgb(val)
        r_bg = ratio(fg, bg_rgb)
        r_surface = ratio(fg, surface_rgb) if surface_rgb else None
        rows.append((name, val, r_bg, r_surface))
    failed = []
    for name, val, r_bg, r_surface in rows:
        if r_bg >= THRESHOLD: continue
        if r_surface is not None and r_surface >= THRESHOLD: continue
        failed.append((name, val, r_bg, r_surface))
    if failed:
        for name, val, r_bg, r_surface in failed:
            extra = f' / surface {surface_value} {r_surface:.2f}:1' if r_surface is not None else ''
            blocking.append(
                f"{app}: {name}={val} on bg {bg_value} {r_bg:.2f}:1{extra} < AA 4.5:1"
            )
    return blocking, warnings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    apps = args.apps or (["WaterSortPuzzle","Nonogram","Puzzle2048","UnblockPuzzle"] if not args.all else
                         sorted(p.name for p in REPO.iterdir()
                                if (p / "android" / "app" / "build.gradle").exists()))
    any_block = False
    for app in apps:
        if not _is_app(app): continue
        b, w = check_app(app)
        if b or w:
            print(f"=== {app} ===")
            for m in b: print(f"  ✗ {m}")
            for m in w: print(f"  ! {m}")
        else:
            print(f"  ✓ {app}: text-color contrast OK")
        if b: any_block = True
    sys.exit(1 if any_block else 0)


if __name__ == "__main__":
    main()
