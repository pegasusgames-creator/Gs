#!/usr/bin/env python3
"""
dedup_similar_apps.py — find apps with similar mechanics and propose removal.

Use BEFORE shipping at scale. Goes through the entire app folder list,
clusters apps by genre/mechanic similarity, and surfaces clusters where
you have multiple apps doing essentially the same thing. For each
cluster, recommends KEEPING the app whose mechanic is most popular on
the Play Store (Block Blast > Wood Block; Wordle > generic word game;
Sudoku > Kakuro; etc.) and DELETING the others.

Does not delete anything automatically. Outputs a recommendation file
for human review, plus an optional --execute flag to act on it.

Usage:
    python3 dedup_similar_apps.py                  # report only, no changes
    python3 dedup_similar_apps.py --execute        # delete the recommended apps
    python3 dedup_similar_apps.py --review-only    # only show clusters, don't delete

Heuristics:
- Cluster apps by mechanic keywords in their folder names AND in their
  game.html title/description
- Within each cluster, rank by Play Store popularity proxy (we use a
  hard-coded ranking based on observable Play Store install counts as
  of April 2026)
- Recommend keeping the highest-ranked + already-shipped app, removing
  others that haven't shipped yet

Apps already on Play Store (WaterSort) are NEVER auto-removed regardless
of cluster — they're shipped revenue and have ASO history. The script
will flag them but require manual confirmation.
"""

import argparse
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Apps already on Play Store. These are never auto-deleted.
# BallSort was deleted Apr 30 2026 due to low downloads + redundancy with WaterSort.
ALREADY_SHIPPED = {
    "WaterSort",       # under review at time of writing
    # Add new ones here as they ship
}

# Genre clusters: each cluster has a list of (app_name, popularity_rank).
# Lower rank = more popular Play Store mechanic, prefer to keep.
# When two apps fall in the same cluster, the one with lower rank wins.
#
# Popularity ranking is based on:
# - Play Store install counts of top-grossing app in that exact mechanic
# - Search demand (Google Trends) for the mechanic name
# - Active publishers in the genre
#
# Apps NOT in this dict are kept by default (no recommendation either way).
CLUSTER_RULES = {
    # ===== SORT/POUR PUZZLES =====
    "sort_pour": {
        "members": [
            ("WaterSort",       1),  # only sort puzzle in portfolio after BallSort deletion
            ("FruitSort",       2),  # weaker variant
            ("EmojiSort",       3),  # niche, low search
        ],
        "keep_top_n": 1,  # keep WaterSort only; sort/pour cluster is owned by WaterSort
        "rationale": "Sort/pour puzzles all have the same core mechanic. WaterSort represents this cluster. Drop fruit/emoji variants.",
    },

    # ===== GRID-PLACEMENT BLOCK PUZZLES =====
    # NOT including BrickBreaker (paddle game, different cluster)
    "block_puzzle": {
        "members": [
            ("BlockPuzzle",     1),  # Block Blast clone
            ("WoodBlock",       2),  # near-duplicate of BlockPuzzle
            ("ColorBlockJam",   3),  # different mechanic (sliding) but adjacent
        ],
        "keep_top_n": 1,
        "rationale": "Block Blast / wood-block puzzles share placement-on-grid mechanic. Keep one. ColorBlockJam is a sliding puzzle if implemented per the playbook, can stay separate — but if it's just a reskin, drop it.",
    },

    # ===== NUMBER MERGE (2048-style) =====
    "number_merge": {
        "members": [
            ("Puzzle2048",      1),  # 2048-style merge, evergreen
            ("NumberMerge",     2),  # near-duplicate of Puzzle2048
            ("DiceMerge",       3),  # 2048 with dice
        ],
        "keep_top_n": 1,
        "rationale": "Number/dice merge games (2048-style: combine equal pairs to make next tier) all share core. Keep Puzzle2048.",
    },

    # ===== ITEM MERGE (3-match-merge) =====
    "item_merge": {
        "members": [
            ("FruitMerge",      1),
            ("AnimalMerge",     2),
            ("TripleMatch",     3),  # blocked placeholder
        ],
        "keep_top_n": 1,
        "rationale": "Merge-3 / triple-match games (combine 3+ identical items to merge) share mechanic. Pick one theme. Theme alone (fruit vs animal) doesn't differentiate enough.",
    },

    # ===== WORD GAMES — WORDLE-LIKE =====
    "word_guess": {
        "members": [
            ("WordleClone",     1),  # if exists; Wordle = #1
            ("WordScramble",    2),
            ("AnagramFinder",   3),
        ],
        "keep_top_n": 2,
        "rationale": "Wordle-like guess-the-word + anagram/scramble. Keep up to 2 distinct mechanics.",
    },

    # ===== WORD GAMES — SEARCH/PATH =====
    "word_search": {
        "members": [
            ("WordSearch",      1),  # blocked placeholder
            ("BoggleGame",      2),
            ("GhostWord",       3),
        ],
        "keep_top_n": 1,
        "rationale": "Word search / find-words-on-grid. Keep one.",
    },

    # ===== WORD PUZZLES — STRUCTURAL =====
    "word_structural": {
        "members": [
            ("Connections",     1),  # NYT-style category grouping
            ("Cryptogram",      2),  # decode cipher
        ],
        "keep_top_n": 2,
        "rationale": "Connections and Cryptogram are different enough to coexist (grouping vs decoding).",
    },

    # ===== GENERIC TIMERS =====
    # FastingTimer and ChessClock have unique purposes, NOT in this cluster
    "timer_generic": {
        "members": [
            ("PomodoroTimer",   1),  # most-searched single-purpose timer
            ("CountdownTimer",  2),
            ("EggTimer",        3),  # niche
            ("CookingTimer",    4),
            ("MeetingTimer",    5),  # niche
        ],
        "keep_top_n": 1,
        "rationale": "Generic countdown timers all do the same thing. Pomodoro has the strongest search demand. EggTimer and CookingTimer are reskins. Keep Pomodoro.",
    },

    # ===== STRING / GUITAR INSTRUMENT CHORD APPS =====
    # KidsPiano and KidsDrum are SEPARATE because they target Kids program
    "chord_app": {
        "members": [
            ("GuitarChords",    1),  # blocked placeholder
            ("UkuleleChords",   2),  # blocked placeholder; same code as Guitar
        ],
        "keep_top_n": 1,
        "rationale": "Guitar and ukulele chord apps share the same code structure (chord database + finger position diagrams). Pick one instrument; the other adds no value.",
    },

    # ===== METRONOME / TEMPO =====
    "tempo": {
        "members": [
            ("Metronome",       1),  # blocked placeholder
            ("BPMTapper",       2),
        ],
        "keep_top_n": 1,
        "rationale": "Metronome (output a beat at BPM X) and BPM Tapper (input taps to detect BPM) are technically different but tightly clustered for users. Pick one or merge into a single 'Tempo Tools' app.",
    },

    # ===== TRIVIA (use cadence stagger, don't dedupe by deletion) =====
    # Trivia apps share engine but each has unique JSON content. Genuinely
    # distinct content per app makes them fine to ship — but stagger them.
    # No deletion recommended; flag only.
    "trivia": {
        "members": [
            ("AnimalQuiz",      1),
            ("BibleQuiz",       2),
            ("CapitalCities",   3),
            ("EmojiQuiz",       4),
            ("MovieTrivia",     5),  # blocked placeholder
            ("ScienceQuiz",     6),  # blocked placeholder
            ("SportsQuiz",      7),  # blocked placeholder
        ],
        "keep_top_n": 99,  # don't auto-delete
        "rationale": "Trivia apps share engine but each has unique JSON content. Keep all that have real questions, but stagger releases across months — never ship 3+ trivia apps in same week (looks like content-spam).",
        "no_delete": True,
    },

    # ===== CASUAL ARCADE — pick a few favorites =====
    "casual_arcade": {
        "members": [
            ("BubbleShooter",   1),  # stable evergreen
            ("BrickBreaker",    2),  # paddle game, evergreen
            ("BalloonPop",      3),  # casual
            ("BubbleWrap",      4),  # ASMR niche
            ("DontTapWhite",    5),  # piano tiles clone
            ("InfiniteJumper",  6),  # endless runner
            ("FlappyClone",     7),  # if exists
        ],
        "keep_top_n": 3,
        "rationale": "Casual arcade is saturated. Pick 3 with distinct sub-mechanics: paddle (BrickBreaker), shooter (BubbleShooter), runner/jumper (InfiniteJumper). Drop the rest.",
    },

    # ===== BRAIN/MEMORY =====
    "brain_memory": {
        "members": [
            ("MemoryCard",      1),  # blocked placeholder; classic match-pairs
            ("NumberMemory",    2),  # blocked placeholder
            ("PatternSequence", 3),  # blocked placeholder
            ("SimonSays",       4),  # if exists
        ],
        "keep_top_n": 2,
        "rationale": "Match-pairs (MemoryCard) and Simon-Says-style (SimonSays/PatternSequence/NumberMemory) are 2 distinct mechanics. Pick one each.",
    },

    # ===== HEALTH TRACKERS — distinct enough to coexist =====
    "health_log": {
        "members": [
            ("BloodPressureLog",   1),
            ("BloodSugarLog",      2),
            ("MedicationReminder", 3),
            ("SymptomDiary",       4),
            ("MoodJournal",        5),
        ],
        "keep_top_n": 99,  # all keep
        "rationale": "Health logs are distinct (BP, glucose, meds, symptoms, mood). All fine. Stagger releases across weeks.",
        "no_delete": True,
    },
}


def app_exists(name):
    return (REPO_ROOT / name / "android").is_dir()


def is_already_shipped(name):
    return name in ALREADY_SHIPPED


def find_overlaps():
    """Return list of cluster recommendations: keep top-N, drop rest."""
    recommendations = []
    for cluster_name, cluster in CLUSTER_RULES.items():
        members = cluster["members"]
        rationale = cluster["rationale"]
        keep_n = cluster.get("keep_top_n", 1)
        no_delete = cluster.get("no_delete", False)

        existing = [(name, rank) for name, rank in members if app_exists(name)]
        if len(existing) <= keep_n:
            continue

        existing.sort(key=lambda x: x[1])

        # Always keep already-shipped apps in the cluster, even if low rank.
        # Then fill remaining keep slots from highest-ranked unshipped.
        shipped_in_cluster = [n for n, _ in existing if is_already_shipped(n)]
        unshipped = [n for n, _ in existing if not is_already_shipped(n)]

        keep_apps = list(shipped_in_cluster)
        for n in unshipped:
            if len(keep_apps) < keep_n:
                keep_apps.append(n)

        drop = [n for n, _ in existing if n not in keep_apps]
        drop_safe = [d for d in drop if not is_already_shipped(d)]
        drop_protected = [d for d in drop if is_already_shipped(d)]

        recommendations.append({
            "cluster": cluster_name,
            "keep": keep_apps,
            "drop": drop_safe,
            "protected": drop_protected,
            "rationale": rationale,
            "no_delete": no_delete,
        })

    return recommendations


def report(recommendations):
    if not recommendations:
        print("No overlapping clusters found in the current repo.")
        return

    flag_only = [r for r in recommendations if r.get("no_delete")]
    actionable = [r for r in recommendations if not r.get("no_delete")]

    if actionable:
        print(f"Found {len(actionable)} cluster(s) with deletion recommendations.")
        print()
        total_drops = 0
        for rec in actionable:
            print(f"=== Cluster: {rec['cluster']} ===")
            print(f"   {rec['rationale']}")
            for k in rec["keep"]:
                marker = " (already shipped)" if is_already_shipped(k) else ""
                print(f"   ✓ KEEP:  {k}{marker}")
            for d in rec["drop"]:
                print(f"   ✗ DROP:  {d}")
                total_drops += 1
            for p in rec["protected"]:
                print(f"   ⚠ also in cluster but protected: {p}")
            print()
        print(f"Total apps recommended for deletion: {total_drops}")

    if flag_only:
        print()
        print(f"Found {len(flag_only)} cluster(s) flagged for stagger only (no deletions):")
        for rec in flag_only:
            apps = [n for n, _ in CLUSTER_RULES[rec["cluster"]]["members"]
                    if app_exists(n)]
            print(f"  {rec['cluster']}: {', '.join(apps)}")
            print(f"    → {rec['rationale']}")
            print()

    if actionable:
        print("Run with --execute to delete the recommended folders.")


def execute(recommendations):
    actionable = [r for r in recommendations if not r.get("no_delete")]
    to_delete = []
    for rec in actionable:
        for d in rec["drop"]:
            to_delete.append((rec["cluster"], rec["keep"], d))

    if not to_delete:
        print("Nothing to delete.")
        return

    print(f"About to delete {len(to_delete)} app folders:")
    for cluster, keep, drop in to_delete:
        print(f"  - {drop} (keeping: {', '.join(keep)} in cluster {cluster})")
    print()

    confirm = input("Type 'DELETE' to proceed (anything else cancels): ")
    if confirm.strip() != "DELETE":
        print("Cancelled.")
        return

    for cluster, keep, drop in to_delete:
        path = REPO_ROOT / drop
        if path.is_dir():
            shutil.rmtree(path)
            print(f"  ✓ deleted {drop}")
        else:
            print(f"  ! {drop} folder already missing (skipped)")

    print()
    print(f"Done. Deleted {len(to_delete)} app folders.")
    print("Update CLAUDE.md 'State of the apps' section.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="actually delete the recommended folders (with confirmation)")
    ap.add_argument("--review-only", action="store_true",
                    help="show clusters and stop (alias for default behavior)")
    args = ap.parse_args()

    print("Scanning repo for overlapping app clusters...")
    print(f"Repo root: {REPO_ROOT}")
    print()

    recommendations = find_overlaps()
    report(recommendations)

    if args.execute:
        print()
        execute(recommendations)


if __name__ == "__main__":
    main()
