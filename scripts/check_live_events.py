#!/usr/bin/env python3
"""check_live_events.py — every game that ships the growth stack must ship
the shared live-ops calendar (scripts/_growth_shim_events.html): a themed
collection event for all 12 months + Weekend Rush + Golden Hour, rendered
through the MENU shim's ribbon hook.

Bug class (audit 2026-10-03): each app carried its own SEASONAL_EVENTS stub
covering only Oct/Dec/Feb, and the banners promised things no code did —
"pumpkin theme + 5 bonus levels" (Unblock + PipeConnect family: only an
orphan flag), a "1.5× multiplier" (Puzzle2048: a variable nothing read),
"try the Halloween theme" (WaterSort: palette keys that never matched, so it
looked identical to Classic). 9 of 12 months had no event at all.

BLOCKS when a game with growth shim A:
  - lacks data-growth-shim="EVENTS", or its calendar misses a month;
  - its MENU shim does not render the ribbon (gEvents.renderRibbon);
  - re-enables a retired per-app seasonal banner (an injectSeasonalBanner /
    applyEvent body that no longer starts with `return;`).

Standalone:  python3 scripts/check_live_events.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
EV_BLOCK = re.compile(r'<script data-growth-shim="EVENTS">([\s\S]*?)</script>')
MENU_BLOCK = re.compile(r'<script data-growth-shim="MENU">([\s\S]*?)</script>')
RETIRED = re.compile(r'function\s+(injectSeasonalBanner|applyEvent)\s*\(\)\s*\{([\s\S]{0,400})')


def check_app(app: str):
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return [], []
    s = p.read_text(encoding="utf-8", errors="replace")
    if 'data-growth-shim="A"' not in s:
        return [], []
    bad = []
    m = EV_BLOCK.search(s)
    if not m:
        bad.append(f"{app}: live-ops EVENTS shim missing — run scripts/reinject_all_shims.py")
    else:
        months = {int(x) for x in re.findall(r'month:\s*(\d+)', m.group(1))}
        miss = sorted(set(range(1, 13)) - months)
        if miss:
            bad.append(f"{app}: EVENTS calendar misses month(s) {miss}")
    mm = MENU_BLOCK.search(s)
    if mm and "renderRibbon" not in mm.group(1):
        bad.append(f"{app}: MENU shim does not render the event ribbon")
    for fn, body in RETIRED.findall(s):
        # Code that runs before the retirement `return;` must not render a
        # banner, set the orphan theme flag or arm the never-read multiplier.
        code = re.sub(r'//[^\n]*', '', body).replace('if(!ev) return;', '').replace('if(!ev) return', '')
        live = code.split('return;', 1)[0]
        if re.search(r'createElement|xtheme_owned_|__seasonalMult', live):
            bad.append(f"{app}: per-app seasonal {fn} re-enabled (made false promises — EVENTS owns this)")
    return bad, []


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad = []
    for a in apps:
        b, _ = check_app(a)
        bad.extend(b)
    for line in bad:
        print("  ✗", line)
    if bad:
        print(f"live-events check: {len(bad)} blocker(s)")
        return 1
    print("live-events check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
