#!/usr/bin/env python3
"""check_reward_types_native.py — every rewarded-ad type game.html asks for
must be accepted by MainActivity.java's VALID_REWARD_TYPES.

Bug class (audit 2026-10-03): MainActivity.showRewardedAd() returns silently
for any type not in VALID_REWARD_TYPES — no ad, no reward, no onAdNotReady.
WaterSort (hero app) requested free_coins / hint / extra_tube / magic_wand
but whitelisted only undo/skip/life, so its Free Coins and booster ads never
played — and the dropped request left a pending callback that blocked every
later rewarded ad that session. The PipeConnect family requested 'hint'
without whitelisting it. check_reward_type_parity only compared JS to JS.

JS request sites recognised: showRewardedAd / safeShowRewarded /
safeShowRewardedCb / requestRewardedAd / Android.showRewarded with a string
literal, plus the adType argument of (simple)boosterChooser(...).
Java aliases: extra_life → life.

Standalone:  python3 scripts/check_reward_types_native.py [App ...]
"""
import glob
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
REQ = re.compile(r"(?:showRewardedAd|safeShowRewarded|safeShowRewardedCb|requestRewardedAd|"
                 r"Android\.showRewarded|showRewardedVideo)\(\s*['\"]([a-z_]+)['\"]")
CHOOSER = re.compile(r"(?:simpleBoosterChooser|boosterChooser)\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*[^,]+,\s*'([a-z_]+)'")
JAVA = re.compile(r"VALID_REWARD_TYPES\s*=\s*new\s+HashSet<>\(Arrays\.asList\(([^)]*)\)\)")
ALIAS = {"extra_life": "life"}


def check_app(app: str):
    gh = BASE / app / "android/app/src/main/assets/game.html"
    jfiles = glob.glob(str(BASE / app / "android/app/src/main/java/**/MainActivity.java"), recursive=True)
    if not gh.exists() or not jfiles:
        return [], []
    java = Path(jfiles[0]).read_text(encoding="utf-8", errors="replace")
    m = JAVA.search(java)
    if not m:
        return [], []
    allowed = set(re.findall(r'"([a-z_]+)"', m.group(1)))
    html = gh.read_text(encoding="utf-8", errors="replace")
    asked = set(REQ.findall(html)) | set(CHOOSER.findall(html))
    missing = sorted(t for t in asked if ALIAS.get(t, t) not in allowed)
    if missing:
        return [f"{app}: game.html requests rewarded type(s) {missing} that MainActivity.VALID_REWARD_TYPES "
                f"drops silently (allowed: {sorted(allowed)})"], []
    return [], []


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
        print(f"reward-types-native check: {len(bad)} blocker(s)")
        return 1
    print("reward-types-native check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
