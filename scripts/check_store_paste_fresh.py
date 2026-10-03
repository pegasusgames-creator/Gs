#!/usr/bin/env python3
"""check_store_paste_fresh.py — <App>/STORE_PASTE.md (the sheet the user
copies into Play Console) must belong to this app and match its metadata.

Bug class (audit 2026-10-03): Afterimage, Hunch and Overlay shipped a
STORE_PASTE.md that was a stale copy of PipeConnect's ("# PipeConnect —
store paste sheet", PipeConnect's descriptions, "Initial release." notes),
and WaterSort's still said "Polish & fixes." months after its notes were
rewritten. Pasting from them puts another game's copy on a listing — Red
Line 3 (templated listing copy) — or ships stale "What's new" text.

BLOCKS when STORE_PASTE.md exists and:
  - its title line names a different app, or
  - any <locale> block of RELEASE NOTES / SHORT DESCRIPTION / FULL
    DESCRIPTION differs from metadata/<locale>/<field>.txt.
Fix: python3 scripts/gen_store_paste.py <App> --force

Standalone:  python3 scripts/check_store_paste_fresh.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
SECTIONS = {
    "RELEASE NOTES": "release_notes.txt",
    "SHORT DESCRIPTION": "short_description.txt",
    "FULL DESCRIPTION": "full_description.txt",
}
TAG_DIR = {"id": "id", "uk": "uk"}


def check_app(app: str):
    p = BASE / app / "STORE_PASTE.md"
    if not p.exists():
        return [], []
    s = p.read_text(encoding="utf-8", errors="replace")
    bad = []
    first = s.splitlines()[0] if s else ""
    m = re.match(r"#\s*(\S+)\s+—", first)
    if m and m.group(1) != app:
        bad.append(f"{app}: STORE_PASTE.md is {m.group(1)}'s sheet — regenerate with gen_store_paste.py {app} --force")
        return bad, []
    for title, fname in SECTIONS.items():
        sec = re.search(r"## " + re.escape(title) + r"[^\n]*\n([\s\S]*?)(?=\n## |\Z)", s)
        if not sec:
            continue
        for loc, body in re.findall(r"<([a-zA-Z-]+)>\n([\s\S]*?)\n</\1>", sec.group(1)):
            f = BASE / app / "metadata" / TAG_DIR.get(loc, loc) / fname
            if not f.exists():
                continue
            want = f.read_text(encoding="utf-8", errors="replace").strip()
            if body.strip() != want:
                bad.append(f"{app}: STORE_PASTE.md {title} <{loc}> is stale vs metadata — regenerate with gen_store_paste.py {app} --force")
                break
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
        print(f"store-paste-fresh check: {len(bad)} blocker(s)")
        return 1
    print("store-paste-fresh check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
