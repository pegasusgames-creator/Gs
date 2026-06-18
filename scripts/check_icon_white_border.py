#!/usr/bin/env python3
"""Pre-publish gate: launcher / store icons must be full-bleed (no white
padding). A rounded-rect icon baked onto a white square shows white space
around it once a launcher applies its own mask. This flags any
mipmap ic_launcher(_round) or store icon whose four corners are opaque
near-pure-white. Fix by extending the icon's background colour into the
corners (scripts/fix_icons.py) or shipping a proper adaptive icon.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from PIL import Image
except ImportError:
    Image = None


def white_corners(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    cs = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    return all(c[3] > 200 and c[0] >= 249 and c[1] >= 249 and c[2] >= 249
               for c in cs)


def check_app(app):
    if Image is None:
        return [], ["Pillow not installed — icon white-border check skipped"]
    blockers = []
    cands = [
        os.path.join(REPO, app, "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"),
        os.path.join(REPO, app, "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png"),
        os.path.join(REPO, app, "store/icon_512_playstore.png"),
    ]
    for p in cands:
        if os.path.isfile(p) and white_corners(p):
            blockers.append(f"{app}: {os.path.relpath(p, os.path.join(REPO, app))} "
                            f"has opaque white corners — icon shows white padding "
                            f"under a launcher/Play mask (make it full-bleed)")
    return blockers, []


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(d for d in os.listdir(REPO)
                      if os.path.isdir(os.path.join(REPO, d, "android"))
                      and not d.startswith(("_", ".")))
    fail = 0
    for app in apps:
        b, w = check_app(app)
        for line in b:
            print(f"✗ {line}"); fail = 1
        for line in w:
            print(f"!  {line}")
    if not fail:
        print(f"[icon white border] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
