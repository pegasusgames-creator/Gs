#!/usr/bin/env python3
"""_upgrade_settings_normalizer_v3.py — replace the legacy v2 settings
normalizer (the `__settingsNorm` / "PART5: settings groups …" block, which
only fires once on showScreen('settings') and never re-runs after shims inject
rows) with the shared v3 master in scripts/_settings_normalizer.js (rendered-DOM
MutationObserver trigger + section flatten + canonical role order + dedup).

The 4 live apps already carry v3; this lifts the 4 unreleased apps to parity.
Idempotent: skips an app that already has v3.

Usage: python3 scripts/_upgrade_settings_normalizer_v3.py [AppName ...]
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_APPS = ["PipeConnect", "Hunch", "Afterimage", "Overlay"]

V2_RE = re.compile(
    r"<script>/\*PART5: settings groups \+ Reset-All-Data[\s\S]*?</script>"
)


def main():
    master = (REPO / "scripts/_settings_normalizer.js").read_text(encoding="utf-8").strip()
    apps = sys.argv[1:] or DEFAULT_APPS
    for app in apps:
        p = REPO / app / "android/app/src/main/assets/game.html"
        s = p.read_text(encoding="utf-8")
        if "universal settings normalizer v3" in s:
            print(f"  {app}: already v3 — skip")
            continue
        m = V2_RE.search(s)
        if not m:
            print(f"  ? {app}: no v2 block found — skip")
            continue
        s = s[: m.start()] + master + s[m.end():]
        p.write_text(s, encoding="utf-8")
        print(f"  {app}: upgraded v2 -> v3")


if __name__ == "__main__":
    main()
