#!/usr/bin/env python3
"""check_ads_respect_pass.py — every interstitial call site must be gated by
adsRemoved() (Remove Ads OR an active Season/Weekly Pass), not by the raw
removeAds flag alone.

Bug class (audit 2026-10-03): PipeConnect / Afterimage / Hunch / Overlay
(safeShowInterstitial) and UnblockPuzzle (level-win path) checked only
`removeAds`, so Season Pass ($4.99/mo) and Weekly Pass ($1.99/wk)
subscribers — both sold as "ad-free" — still got interstitials.

For each line that calls `Android.showInterstitial(` (outside growth-shim
blocks and comments), the enclosing function body up to that line must
mention adsRemoved( / State.adsRemoved( / adsGone( — or the call must sit
in a function that is itself only reached through such a gate
(safeShowInterstitial / showInterstitial wrappers are checked directly).

Standalone:  python3 scripts/check_ads_respect_pass.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
CALL = re.compile(r'Android\.showInterstitial\s*\(')
GATE = re.compile(r'adsRemoved\s*\(|adsGone\s*\(')
SHIM_BLOCK = re.compile(r'<script data-growth-shim="[A-Z]+">[\s\S]*?</script>')


def check_app(app: str):
    p = BASE / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        return [], []
    s = SHIM_BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), p.read_text(encoding="utf-8", errors="replace"))
    # Only games that sell a pass can violate the promise.
    if "season_pass_monthly" not in s and "weekly_pass" not in s:
        return [], []
    lines = s.splitlines()
    bad = []
    for i, line in enumerate(lines):
        if not CALL.search(line) or line.strip().startswith("//"):
            continue
        # Walk back to the nearest function header (max 40 lines).
        window = []
        for j in range(i, max(-1, i - 40), -1):
            window.append(lines[j])
            # Stop at the enclosing NAMED function / method header — not at
            # an inline arrow callback (setTimeout(()=>{...}) wraps many calls).
            if j != i and re.search(r'\bfunction\b|^\s*(?!(?:if|for|while|switch|catch|else)\b)[A-Za-z_$][\w$]*\s*\([^)]*\)\s*\{', lines[j]):
                break
        if not GATE.search("\n".join(window)):
            bad.append(f"{app}:{i + 1}: interstitial not gated by adsRemoved() — pass holders would see ads")
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
        print(f"ads-respect-pass check: {len(bad)} blocker(s)")
        return 1
    print("ads-respect-pass check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
