#!/usr/bin/env python3
"""Remove the pure-white corner/border from rounded-rect-on-white app icons by
flood-filling the white from the 4 corners with the icon's own edge color
(making them full-bleed so the launcher's mask leaves no white space).
Safety: only near-pure-white (>=249 all channels) is filled; aborts if the
fill would consume >45% of the image (guards real light backgrounds)."""
import sys, glob, os
from collections import deque
from PIL import Image

WHITE = 249  # all channels >= this == border white (cream #f5f0e6 has B=230, safe)


def is_white(p):
    return p[0] >= WHITE and p[1] >= WHITE and p[2] >= WHITE and p[3] >= 200


def fix(path, dry=False):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if not any(is_white(px[x, y]) for x, y in corners):
        return None  # no white corner
    # bg color = the icon's DOMINANT non-white colour (the background fills more
    # of the icon than any single artwork colour), bucketed to reduce noise.
    def edge_color():
        from collections import Counter
        c = Counter()
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                p = px[x, y]
                if p[3] < 200 or is_white(p):
                    continue
                c[(p[0] // 8 * 8, p[1] // 8 * 8, p[2] // 8 * 8)] += 1
        if not c:
            return (20, 25, 40, 255)
        r, g, b = c.most_common(1)[0][0]
        return (r, g, b, 255)
    fill = edge_color()
    # BFS flood from corners over white
    seen = bytearray(w * h)
    dq = deque()
    for x, y in corners:
        if is_white(px[x, y]) and not seen[y * w + x]:
            seen[y * w + x] = 1; dq.append((x, y))
    filled = 0
    while dq:
        x, y = dq.popleft()
        px[x, y] = fill; filled += 1
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny*w+nx] and is_white(px[nx, ny]):
                seen[ny*w+nx] = 1; dq.append((nx, ny))
    frac = filled / (w * h)
    if frac > 0.45:
        return ("ABORT", round(frac, 2), fill)
    if not dry:
        im.save(path)
    return (round(frac, 3), fill)


if __name__ == "__main__":
    apps = sys.argv[1:] or ["Nonogram", "Puzzle2048", "UnblockPuzzle", "WaterSortPuzzle"]
    dry = "--dry" in apps
    apps = [a for a in apps if not a.startswith("--")]
    for app in apps:
        files = glob.glob(f"{app}/android/app/src/main/res/mipmap-*/ic_launcher*.png")
        files += [p for p in [f"{app}/store/icon_512_playstore.png",
                              f"{app}/store/icon_1024_appstore.png"] if os.path.isfile(p)]
        for f in sorted(files):
            r = fix(f, dry=dry)
            if r is not None:
                print(f"  {f.replace(app+'/','')}: {r}")
        print(f"{app}: processed {len(files)} files")
