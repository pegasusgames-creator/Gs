#!/usr/bin/env python3
"""_tracks.py — which product track an app belongs to.

  game     the family game shell (levels/score, lives, coins, growth shims)
  kids     the Families-compliant kids shell (ABCLearning template)
  utility  the tool shell (HabitTracker template)

Source of truth: docs/portfolio_tracks.json ("kids" / "utility" lists) plus
an app's own metadata/app_info.json "kids_program": true. Anything not listed
(including the 8 finished family games) is "game". Game-only gates (growth
baseline, menu hierarchy/composition/consistency, reward parity, gameplay-only
screenshots) run on game-track apps only; kids and utility apps have their
own gates (check_families_compliance.py, check_utility_shell.py).
"""
import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def _lists():
    try:
        return json.loads((BASE / "docs/portfolio_tracks.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=None)
def track_of(app: str) -> str:
    try:
        info = json.loads((BASE / app / "metadata/app_info.json").read_text(encoding="utf-8"))
        if info.get("kids_program") is True:
            return "kids"
    except Exception:
        pass
    lists = _lists()
    for t in ("kids", "utility"):
        if app in lists.get(t, []):
            return t
    return "game"


def is_game(app: str) -> bool:
    return track_of(app) == "game"
