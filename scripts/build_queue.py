#!/usr/bin/env python3
"""build_queue.py — read / update docs/build_queue.json (the finish-everything order).

  python3 scripts/build_queue.py next [N]          # next N todo apps (default 1)
  python3 scripts/build_queue.py set App status    # todo | building | done
  python3 scripts/build_queue.py stats
"""
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
Q = BASE / "docs/build_queue.json"


def load():
    return json.loads(Q.read_text(encoding="utf-8"))


def save(d):
    Q.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    a = sys.argv[1:]
    d = load()
    if not a or a[0] == "stats":
        c = Counter(x["status"] for x in d["apps"])
        print(dict(c), "building:", [x["app"] for x in d["apps"] if x["status"] == "building"])
        return 0
    if a[0] == "next":
        n = int(a[1]) if len(a) > 1 else 1
        for x in [x for x in d["apps"] if x["status"] == "todo"][:n]:
            print(x["app"], x["track"], x["model"])
        return 0
    if a[0] == "set" and len(a) == 3:
        for x in d["apps"]:
            if x["app"] == a[1]:
                x["status"] = a[2]
                save(d)
                print(f"{a[1]} -> {a[2]}")
                return 0
        print(f"{a[1]}: not in queue", file=sys.stderr)
        return 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
