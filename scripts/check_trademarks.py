#!/usr/bin/env python3
"""check_trademarks.py — no third-party game / franchise trademarks in an
app's user-visible identity or listing text.

Bug class (audit 2026-10-03): the long tail carried listings and in-game
titles built on actively-enforced marks — "Wordle" (NYT; clones were mass-
removed from both stores in 2022), "Harry Potter Fan Quiz" (Warner Bros.),
"Heads Up!" (Warner Bros.' party game), "Classic Tetris-style game" (The
Tetris Company files takedowns for "Tetris" in listing text), an in-game
<title>Flappy Bird</title>. Google Play's Intellectual Property policy:
repeated IP strikes terminate the whole developer account — every app.

BLOCKS when a HIGH-risk mark appears in metadata/en-US title / subtitle /
short_description / full_description / keywords / promotional_text (what
store review reads). game.html's <title> is WARN-only: players never see it
and Red Line 2 ties it to the folder name, so it is fixed by renaming both
together. WARNS on MEDIUM marks (generic-ish names that are also
registered for a specific game) so a human decides.

Already-blocked placeholder clones are skipped (check_blocked_apps owns them).

Standalone:  python3 scripts/check_trademarks.py [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
HIGH = [
    r"wordle", r"harry\s*potter", r"hogwarts", r"heads\s*up!", r"tetris", r"flappy\s*bird",
    r"pok[eé]mon", r"minecraft", r"fortnite", r"roblox", r"candy\s*crush", r"angry\s*birds",
    r"scrabble", r"boggle", r"monopoly", r"yahtzee", r"jenga", r"pictionary", r"trivial\s*pursuit",
    r"connect\s*(?:four|4)", r"rubik", r"lego", r"disney", r"marvel", r"star\s*wars", r"nintendo",
    r"super\s*mario", r"zelda", r"pac-?\s*man", r"bejeweled", r"among\s*us", r"picross",
    r"flow\s*free", r"unblock\s*me", r"royal\s*match", r"block\s*blast", r"subway\s*surfers",
]
MEDIUM = [r"mastermind", r"spelling\s*bee", r"\bconnections\b", r"\bsimon\b", r"battleship"]
FIELDS = ["title.txt", "subtitle.txt", "short_description.txt", "full_description.txt",
          "keywords.txt", "promotional_text.txt"]


def blocked_apps():
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        import pre_publish_check as ppc  # noqa: E402
        return set(getattr(ppc, "BLOCKED_APPS", []))
    except Exception:
        return set()


def check_app(app: str, blocked=frozenset()):
    if app in blocked:
        return [], []
    texts = []
    gh = BASE / app / "android/app/src/main/assets/game.html"
    if gh.exists():
        m = re.search(r"<title>([^<]*)</title>", gh.read_text(encoding="utf-8", errors="replace"))
        if m:
            texts.append(("game.html <title>", m.group(1)))
    for f in FIELDS:
        p = BASE / app / "metadata" / "en-US" / f
        if p.exists():
            texts.append((f"metadata/en-US/{f}", p.read_text(encoding="utf-8", errors="replace")))
    bad, warn = [], []
    for where, txt in texts:
        for pat in HIGH:
            m = re.search(pat, txt, re.I)
            if m and where.endswith("<title>"):
                # The WebView <title> isn't shown to players, and Red Line 2
                # ties it to the folder name — fix both together (rename).
                warn.append(f"{app}: third-party trademark \"{m.group(0)}\" in {where} — rename folder + <title> before shipping")
            elif m:
                bad.append(f"{app}: third-party trademark \"{m.group(0)}\" in {where}")
        for pat in MEDIUM:
            m = re.search(pat, txt, re.I)
            if m and where.endswith(("title.txt", "<title>")):
                warn.append(f"{app}: \"{m.group(0)}\" in {where} is also a registered game name — confirm it's safe to use")
    return bad, warn


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
    blocked = blocked_apps()
    bad, warn = [], []
    for a in apps:
        b, w = check_app(a, blocked)
        bad.extend(b); warn.extend(w)
    for line in bad:
        print("  ✗", line)
    for line in warn:
        print("  ⚠", line)
    if bad:
        print(f"trademark check: {len(bad)} blocker(s)")
        return 1
    print("trademark check: OK" + (f" ({len(warn)} warning(s))" if warn else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
