#!/usr/bin/env python3
"""check_no_applovin.py — AppLovin is gone from the portfolio; keep it gone.

History: the 8 family games dropped AppLovin MAX on 2026-06-15
(remove_applovin.py); the 161 long-tail apps, whose AppLovin layer had a
placeholder SDK key and earned nothing, moved to AdMob + UMP on 2026-10-12
(remove_applovin_longtail.py). The old check_ad_network_switch gate (a
USE_APPLOVIN=true launch crash) is retired with it, as is the obsolete
prepare_for_publish.py that wrote an AppLovin-primary MainActivity.

BLOCKS any AppLovin / MAX reference in an app's Android sources, gradle
files, manifest, proguard rules or game.html — a copy-pasted wrapper or
template would silently bring the SDK (and its minSdk 24 / init crash
classes of bug) back.

Standalone:  python3 scripts/check_no_applovin.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
PAT = re.compile(r"applovin|\bMax(?:AdView|InterstitialAd|RewardedAd|Ad|Error|Reward)\b|USE_APPLOVIN", re.I)
SUFFIXES = (".java", ".kt", ".gradle", ".xml", ".pro", ".properties")


def check_app(app: str):
    root = BASE / app
    files = [p for p in (root / "android").rglob("*")
             if p.is_file() and p.suffix in SUFFIXES and "/build/" not in p.as_posix()] if (root / "android").is_dir() else []
    gh = root / "android/app/src/main/assets/game.html"
    if gh.exists():
        files.append(gh)
    bad = []
    for p in files:
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if PAT.search(line):
                bad.append(f"{app}: AppLovin reference in {p.relative_to(BASE)}:{i}: {line.strip()[:90]}")
                break
    return bad, []


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad = []
    for a in apps:
        bad.extend(check_app(a)[0])
    for line in bad:
        print("  ✗", line)
    if bad:
        print(f"no-applovin check: {len(bad)} blocker(s)")
        return 1
    print("no-applovin check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
