#!/usr/bin/env python3
"""localize_google_fonts.py — replace <link href="https://fonts.googleapis.com/…">
in an app's game.html with an inline <style data-local-fonts> block whose
@font-face rules embed the woff2 files as base64 data URIs.

Why (audit 2026-10-03): 25 apps (incl. Puzzle2048 and the PipeConnect
family) fetched Google Fonts at every launch. Offline — which the listings
promise — the title/UI fell back to a different system font than the store
screenshots show, and every launch sent the player's IP to a third party
(GDPR exposure; LG München 3 O 17493/20). Data URIs (not asset files) because
the WebView runs with setAllowFileAccessFromFileURLs(false) and @font-face
loads are CORS-checked, so file:// font files may be refused on device.

Only the Latin, Latin-ext, Cyrillic(+ext) and Vietnamese subsets are kept
(the listing locales that use Latin/Cyrillic script); other scripts (Arabic,
Devanagari, CJK) already render with the system font.

Needs network at authoring time (stdlib urllib). Idempotent: an app that no
longer links Google Fonts is skipped.

Usage:
    python3 scripts/localize_google_fonts.py [--dry-run] App [App ...]
    python3 scripts/localize_google_fonts.py --all
"""
import base64
import re
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
UA = ("Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Mobile Safari/537.36")
KEEP_SUBSETS = {"latin", "latin-ext", "cyrillic", "cyrillic-ext", "vietnamese"}
LINK_RE = re.compile(r'<link[^>]+href="(https://fonts\.googleapis\.com/css2?\?[^"]+)"[^>]*>\s*', re.I)
PRECONNECT_RE = re.compile(r'<link[^>]+rel="preconnect"[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*', re.I)
IMPORT_RE = re.compile(r"@import\s+url\(['\"]?(https://fonts\.googleapis\.com/[^'\")]+)['\"]?\);?\s*")
_cache = {}


def fetch(url: str) -> bytes:
    if url not in _cache:
        req = urllib.request.Request(url.replace("&amp;", "&"), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            _cache[url] = r.read()
    return _cache[url]


def inline_css(css_url: str) -> str:
    css = fetch(css_url).decode("utf-8")
    # Group by (family, style, subset, file): variable fonts serve ONE file for
    # every requested weight — embed it once with a weight range instead of
    # once per weight (that bloated some apps by ~1 MB).
    groups = {}
    for subset, block in re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css):
        if subset not in KEEP_SUBSETS:
            continue
        m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", block)
        fam = re.search(r"font-family:\s*([^;]+);", block)
        sty = re.search(r"font-style:\s*([^;]+);", block)
        wgt = re.search(r"font-weight:\s*(\d+)", block)
        if not (m and fam and wgt):
            continue
        key = (fam.group(1), sty.group(1) if sty else "normal", subset, m.group(1))
        g = groups.setdefault(key, {"block": block, "url": m.group(0), "weights": []})
        g["weights"].append(int(wgt.group(1)))
    out = []
    for (fam, sty, subset, url), g in groups.items():
        b64 = base64.b64encode(fetch(url)).decode("ascii")
        block = g["block"].replace(g["url"], "url(data:font/woff2;base64," + b64 + ")")
        lo, hi = min(g["weights"]), max(g["weights"])
        block = re.sub(r"font-weight:\s*\d+", "font-weight: " + (str(lo) if lo == hi else f"{lo} {hi}"), block)
        out.append(f"/* {subset} */\n" + block)
    if not out:
        raise RuntimeError(f"no usable @font-face in {css_url}")
    return "\n".join(out)


def process(app: str, dry: bool) -> None:
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    urls = LINK_RE.findall(s) + IMPORT_RE.findall(s)
    if not urls:
        return
    css = "\n".join(inline_css(u) for u in dict.fromkeys(urls))
    block = ("<style data-local-fonts>\n/* Google Fonts embedded locally (offline + no third-party "
             "request at launch) — scripts/localize_google_fonts.py */\n" + css + "\n</style>\n")
    s2 = PRECONNECT_RE.sub("", s)
    s2 = IMPORT_RE.sub("", s2)
    first = LINK_RE.search(s2)
    if first:
        s2 = s2[:first.start()] + block + LINK_RE.sub("", s2[first.start():])
    else:
        s2 = s2.replace("</head>", block + "</head>", 1)
    print(f"  {app}: {'would embed' if dry else 'embedded'} {len(urls)} Google Fonts stylesheet(s), +{(len(s2) - len(s)) // 1024} KB")
    if not dry:
        p.write_text(s2, encoding="utf-8")


def main() -> int:
    dry = "--dry-run" in sys.argv
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    for a in apps:
        try:
            process(a, dry)
        except Exception as e:  # noqa: BLE001 — report and continue
            print(f"  ! {a}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
