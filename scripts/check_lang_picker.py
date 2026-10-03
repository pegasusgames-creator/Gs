#!/usr/bin/env python3
"""check_lang_picker.py — every listing locale the game translates must be
selectable in its in-game language picker.

Bug class (audit 2026-10-03): all 8 shipping/finished games shipped a full
Ukrainian GAME_I18N block and a Ukrainian store listing (`uk`), but
window.LANG_NAMES — which builds the Settings language <select> — had no
`uk` entry. Auto-detect worked, but a player whose phone is set to another
language could never switch the game to Ukrainian.

BLOCKS: a listing locale (metadata/<locale>/ short code) that has a
GAME_I18N block but is missing from LANG_NAMES.
WARNS:  a listing locale with no GAME_I18N block at all (game UI falls back
to English for that market).

Standalone:  python3 scripts/check_lang_picker.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
NAMES_RE = re.compile(r"window\.LANG_NAMES\s*=\s*\{(.*?)\};", re.S)
I18N_RE = re.compile(r"window\.GAME_I18N\s*=\s*\{")


def check_app(app: str):
    gh = BASE / app / "android/app/src/main/assets/game.html"
    meta = BASE / app / "metadata"
    if not gh.exists() or not meta.is_dir():
        return [], []
    s = gh.read_text(encoding="utf-8", errors="replace")
    m, gi = NAMES_RE.search(s), I18N_RE.search(s)
    if not (m and gi and gi.start() < m.start()):
        return [], []
    blocks = set(re.findall(r"\n\s{2}([a-z]{2})\s*:\s*\{", s[gi.end():m.start()]))
    names = set(re.findall(r"\b([a-z]{2})\s*:\s*['\"]", m.group(1)))
    listing = sorted({d.name.split("-")[0] for d in meta.iterdir()
                      if d.is_dir() and re.fullmatch(r"[a-z]{2}(-[A-Z0-9]+)?", d.name)})
    bad = [f"{app}: listing locale '{c}' is translated in GAME_I18N but missing from the "
           f"LANG_NAMES language picker" for c in listing if c in blocks and c not in names]
    warn = [f"{app}: listing locale '{c}' has no GAME_I18N block (in-game UI falls back to English)"
            for c in listing if c not in blocks and c != "en"]
    return bad, warn


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    bad, warn = [], []
    for a in apps:
        b, w = check_app(a)
        bad.extend(b); warn.extend(w)
    for line in bad:
        print("  ✗", line)
    for line in warn:
        print("  ⚠", line)
    if bad:
        print(f"lang-picker check: {len(bad)} blocker(s)")
        return 1
    print("lang-picker check: OK" + (f" ({len(warn)} warning(s))" if warn else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
