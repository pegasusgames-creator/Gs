#!/usr/bin/env python3
"""
cleanup_repo.py — moves dead/blocked app folders OUT of the working tree.

Per CLAUDE.md state-of-apps: BallSort was deleted Apr 30 2026, and 33
placeholder Dice Roller clones are BLOCKED from publishing. But as of
the May 2026 audit (visible at github.com/pegasusgames-creator/Gs),
all 34 of these folders are still in the repo. They're liability:

- BallSort: confused state (deleted from app_themes.py, dedup, promo.json,
  CLAUDE.md, but folder remains)
- 33 BLOCKED clones: byte-identical Dice Roller game.html across all,
  one accidental override of pre_publish_check.py BLOCKED_APPS = account
  termination

This script moves them to <repo>/../_blocked_clones/ — out of the
working tree but preserved on disk in case they're needed later
(e.g., to rewrite a clone's game.html and reactivate it).

Usage:
    python3 scripts/cleanup_repo.py --dry-run    # show what would move
    python3 scripts/cleanup_repo.py --execute     # actually move

After running with --execute, commit the deletions:
    git add -A
    git commit -m "Move BLOCKED placeholder clones + BallSort out of working tree"
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = (Path(__file__).resolve().parent.parent
             if Path(__file__).resolve().parent.name == "scripts"
             else Path(__file__).resolve().parent)

# Folders to move out of the working tree.
# Sourced from CLAUDE.md "Placeholder clones — DO NOT PUBLISH (33)"
# section + BallSortPuzzle (deleted Apr 30 2026).
BLOCKED_APPS = [
    "DiceRoller",
    "EmotionFlash", "FindDifference", "FlashlightSOS", "FruitMerge",
    "GuitarChords", "HiddenObject", "JigsawPuzzle", "MahjongSolitaire",
    "MemoryCard", "Metronome", "MovieTrivia", "MultiplicationGame",
    "MusicTheory", "NumberMemory", "PasswordGen", "PatternSequence",
    "PianoKeyboard", "PinPull", "QRCodeGen", "RandomName",
    "RandomNumber", "RandomRecipe", "ScienceQuiz", "ScrewPuzzle",
    "SlidingTiles", "SolarSystem", "SportsQuiz", "Sumplete",
    "TripleMatch", "UkuleleChords", "WordScramble", "WordSearch",
]

DELETED_APPS = [
    "BallSortPuzzle",  # deleted Apr 30 2026 per CLAUDE.md
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be moved, don't actually do it")
    ap.add_argument("--execute", action="store_true",
                    help="actually perform the moves")
    args = ap.parse_args()

    if not args.dry_run and not args.execute:
        print("Specify either --dry-run or --execute")
        sys.exit(1)

    # Output directory is SIBLING of the repo, not inside it
    out_dir = REPO_ROOT.parent / "_blocked_clones"

    moves = []
    for app in BLOCKED_APPS:
        src = REPO_ROOT / app
        if src.is_dir():
            moves.append((app, src, out_dir / "blocked" / app))

    for app in DELETED_APPS:
        src = REPO_ROOT / app
        if src.is_dir():
            moves.append((app, src, out_dir / "deleted" / app))

    if not moves:
        print("Nothing to move. Repo is already clean.")
        return

    print(f"Found {len(moves)} folders to move:")
    print(f"  Destination: {out_dir}")
    print()

    for app, src, dest in moves:
        category = "BLOCKED" if "/blocked/" in str(dest) else "DELETED"
        print(f"  [{category}] {app}")

    if args.dry_run:
        print()
        print(f"DRY RUN — no changes made. Re-run with --execute to actually move.")
        return

    print()
    confirm = input(f"Move {len(moves)} folders to {out_dir}? Type YES: ")
    if confirm != "YES":
        print("Aborted.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "blocked").mkdir(exist_ok=True)
    (out_dir / "deleted").mkdir(exist_ok=True)

    for app, src, dest in moves:
        if dest.exists():
            print(f"  ! skipping {app} — already exists at destination")
            continue
        shutil.move(str(src), str(dest))
        print(f"  ✓ moved {app}")

    print()
    print(f"Done. {len(moves)} folders moved to {out_dir}.")
    print()
    print("Next steps:")
    print("  cd " + str(REPO_ROOT))
    print("  git add -A")
    print("  git status   # verify only the expected folders are removed")
    print("  git commit -m 'Move BLOCKED placeholder clones + BallSort out of working tree'")
    print("  git push")
    print()
    print("If you ever want to rewrite a BLOCKED clone with real gameplay:")
    print(f"  mv {out_dir}/blocked/<AppName> {REPO_ROOT}/")
    print("  # then rewrite game.html before running pre_publish_check.py")


if __name__ == "__main__":
    main()
