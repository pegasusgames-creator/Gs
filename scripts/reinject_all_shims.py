#!/usr/bin/env python3
"""reinject_all_shims.py — sync every app's embedded growth shims to the
masters in scripts/_growth_shim_*.html.

For each target app's game.html:
  - Every existing <script data-growth-shim="X">…</script> block (plus the
    HTML comment immediately preceding it, if any) is replaced verbatim with
    the master copy.
  - Shims the app doesn't have yet are APPENDED before </body> in canonical
    order (A, B, D, E, F, G, MENU, SUBS).
  - Afterwards run scripts/wire_leaderboards.py to re-bake per-app
    LEADERBOARD_IDs (the master G shim carries UnblockPuzzle's literal).

Idempotent. Usage:
    python3 scripts/reinject_all_shims.py [AppName ...]   # default: shipping set
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEFAULT_APPS = ["WaterSortPuzzle", "Nonogram", "Puzzle2048", "UnblockPuzzle",
                "PipeConnect"]

# Canonical injection order.
SHIMS = [
    ("A",    "_growth_shim_a.html"),
    ("B",    "_growth_shim_b.html"),
    ("D",    "_growth_shim_d.html"),
    ("E",    "_growth_shim_e.html"),
    ("F",    "_growth_shim_f.html"),
    ("G",    "_growth_shim_g.html"),
    ("MENU", "_growth_shim_menu.html"),
    ("SUBS", "_growth_shim_subs.html"),
]


def master_block(fname: str) -> str:
    """Full master file content (comment + script tag), trimmed."""
    return (REPO / "scripts" / fname).read_text(encoding="utf-8").strip()


LID_RE = re.compile(r"var LEADERBOARD_ID = '[^']*';")


def shim_block_re(key: str) -> re.Pattern:
    """Match the embedded "Growth shim" comment(s) + script block for one shim.

    The comment match uses [\s\S] (comments contain '>' chars) and a *
    quantifier so accidentally stacked duplicate comments collapse into one
    replacement. Anchored to "<!-- Growth shim" so unrelated comments above
    the block are never consumed.
    """
    return re.compile(
        r"(?:<!-- Growth shim(?:(?!-->)[\s\S])*?-->\s*)*"
        rf'<script data-growth-shim="{key}">[\s\S]*?</script>',
    )


def normalized(block: str) -> str:
    """Comparison form: per-app LEADERBOARD_ID literal treated as equal."""
    return LID_RE.sub("var LEADERBOARD_ID = '@';", block)


def process(app: str) -> None:
    p = REPO / app / "android/app/src/main/assets/game.html"
    if not p.exists():
        print(f"  ? {app}: no game.html — skipping")
        return
    s = p.read_text(encoding="utf-8")
    replaced, appended = [], []

    for key, fname in SHIMS:
        block = master_block(fname)
        pat = shim_block_re(key)
        m = pat.search(s)
        if m:
            if normalized(m.group(0)) != normalized(block):
                s = s[:m.start()] + block + s[m.end():]
                replaced.append(key)
        else:
            i = s.rfind("</body>")
            assert i > 0, f"{app}: </body> not found"
            s = s[:i] + "\n" + block + "\n\n" + s[i:]
            appended.append(key)

    p.write_text(s, encoding="utf-8")
    parts = []
    if replaced:
        parts.append(f"replaced {','.join(replaced)}")
    if appended:
        parts.append(f"appended {','.join(appended)}")
    print(f"  {app}: {'; '.join(parts) if parts else 'all shims current'}")


def main():
    apps = sys.argv[1:] or DEFAULT_APPS
    for app in apps:
        process(app)
    # Re-bake per-app leaderboard IDs over the freshly copied G shim.
    subprocess.run([sys.executable, str(REPO / "scripts/wire_leaderboards.py")],
                   check=True)


if __name__ == "__main__":
    main()
