#!/usr/bin/env python3
"""check_growth_core.py — every game that ships the growth shims must route
them through the shared CORE adapter (window.gGame), never through guessed
localStorage keys.

Bug class (audit 2026-10-03): growth shims A/B/D/E/F/G probed the generic
keys ['save','state','gameState','progress'] — no shipping game uses any of
them — so in all 8 apps the notification permission was never requested,
the Day-7 win-back / welcome bonus coins were never paid, the streak shield
never worked, first-clear flow never fired, share text said "Level 0" and
no Play Games score was ever submitted. Static gates only proved the code
was PRESENT; nothing checked that it could reach the save.

BLOCKS when a game with growth shims:
  - lacks the CORE shim, or CORE does not precede Part A;
  - lacks window.GROWTH_CFG, its JSON is invalid, or its saveKey is not a
    key the game actually writes (localStorage.setItem / SAVE_KEY literal);
  - has any growth-shim block containing the generic probe array;
  - monkey-patches the Java bridge (`window.Android.showInterstitial =` /
    `Android.X = function`) — shadowed by the bridge's named-property
    interceptor on real WebViews, so the patch silently never runs;
  - never reports a win to the clear bus (no `gGame.clear(` call outside
    the shims).

Standalone:  python3 scripts/check_growth_core.py [App ...]
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}

GENERIC = re.compile(r"\[\s*'save'\s*,\s*'state'\s*,\s*'gameState'\s*,\s*'progress'\s*\]")
SHIM_BLOCK = re.compile(r'<script data-growth-shim="([A-Z]+)">([\s\S]*?)</script>')
CFG_RE = re.compile(r'<script data-growth-config>window\.GROWTH_CFG=(\{[\s\S]*?\});</script>')
BRIDGE_PATCH = re.compile(r'(?:window\.)?Android\.[A-Za-z_]+\s*=\s*function')


def strip_comments(js: str) -> str:
    js = re.sub(r'/\*[\s\S]*?\*/', '', js)
    return re.sub(r'(?m)^\s*//.*$|(?<=[;{}\s])//[^\n]*', '', js)


def check_app(app: str):
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return [], []
    s = p.read_text(encoding="utf-8", errors="replace")
    if 'data-growth-shim="A"' not in s:
        return [], []
    bad = []
    core = s.find('<script data-growth-shim="CORE">')
    a = s.find('<script data-growth-shim="A">')
    if core < 0:
        bad.append(f"{app}: growth CORE shim missing — run scripts/wire_growth_core.py")
    elif core > a:
        bad.append(f"{app}: CORE shim must come BEFORE Part A")
    m = CFG_RE.search(s)
    if not m:
        bad.append(f"{app}: window.GROWTH_CFG block missing — run scripts/wire_growth_core.py")
    else:
        try:
            cfg = json.loads(m.group(1))
            key = cfg.get("saveKey", "")
            writes = (re.search(r"localStorage\.setItem\(\s*['\"]" + re.escape(key) + r"['\"]", s)
                      or re.search(r"SAVE_KEY\s*=\s*['\"]" + re.escape(key) + r"['\"]", s)
                      or re.search(r"(?:KEY|key)\s*[:=]\s*['\"]" + re.escape(key) + r"['\"]", s))
            if not key or not writes:
                bad.append(f"{app}: GROWTH_CFG.saveKey '{key}' is not a key this game writes")
            if cfg.get("levelBase") not in (0, 1):
                bad.append(f"{app}: GROWTH_CFG.levelBase must be 0 or 1")
        except json.JSONDecodeError as e:
            bad.append(f"{app}: GROWTH_CFG is not valid JSON ({e})")
    for name, body in SHIM_BLOCK.findall(s):
        code = strip_comments(body)
        if GENERIC.search(code):
            bad.append(f"{app}: growth shim {name} probes the generic save keys — use window.gGame")
        if BRIDGE_PATCH.search(code):
            bad.append(f"{app}: growth shim {name} monkey-patches the Java bridge (never runs on device)")
    outside = SHIM_BLOCK.sub("", s)
    if "gGame.clear(" not in outside:
        bad.append(f"{app}: no win path reports to the clear bus (window.gGame.clear(...))")
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
        print(f"growth-core check: {len(bad)} blocker(s)")
        return 1
    print("growth-core check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
