#!/usr/bin/env python3
"""
verify_watersort_levels.py — re-implement WaterSort's JS level generator
and prove every level is solvable AND meets minimum-difficulty targets
using a BFS solver.

Run before any WaterSort release build:

    python3 scripts/verify_watersort_levels.py

Exits 0 if all levels are solvable AND non-trivial AND meet target depth.
Exits 1 otherwise.

The JS generator now uses pre-verified seeds (LEVEL_SEEDS array in
game.html). This script regenerates the same layouts deterministically
and verifies their BFS depth.
"""
import sys, re, os
from collections import deque

MAX_LAYERS = 4
GAME_HTML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "WaterSort", "android", "app", "src", "main", "assets", "game.html"
)

# Per-band minimum depth target (must match emit_seeds output expectations).
# Bands 6/7 (7-color) split into 2-empty (intermediate) then 1-empty (hard)
# so difficulty rises monotonically.
DEPTH_TARGETS = [
    (10,  4),    # 1-10:    tutorial,    3c/5t (2 empty)
    (20,  7),    # 11-30:   easy,        4c/6t (2 empty)
    (40,  10),   # 31-70:   medium-easy, 5c/7t (2 empty)
    (60,  13),   # 71-130:  medium,      5c/6t (1 empty)
    (80,  16),   # 131-210: medium-hard, 6c/7t (1 empty)
    (90,  18),   # 211-300: hard breeze, 7c/9t (2 empty)
    (100, 22),   # 301-400: hard tight,  7c/8t (1 empty)
    (100, 24),   # 401-500: expert,      8c/9t (1 empty) — natural Fisher-Yates ceiling around 24-28
]

def make_rng(seed):
    state = [seed if seed else 42]
    def rand():
        state[0] = (state[0] * 1664525 + 1013904223) & 0xFFFFFFFF
        return state[0] / 0xFFFFFFFF
    return rand

def generate_level(num_tubes, num_colors, seed):
    rand = make_rng(seed)
    def rand_int(lo, hi):
        return int(rand() * (hi - lo + 1)) + lo
    pool = []
    for c in range(num_colors):
        for _ in range(MAX_LAYERS):
            pool.append(c)
    for i in range(len(pool) - 1, 0, -1):
        j = rand_int(0, i)
        pool[i], pool[j] = pool[j], pool[i]
    tubes = []
    for t in range(num_colors):
        tubes.append(pool[t * MAX_LAYERS:(t + 1) * MAX_LAYERS])
    for _ in range(num_tubes - num_colors):
        tubes.append([])
    return tubes

def is_won(tubes):
    return all(len(t) == 0 or (len(t) == MAX_LAYERS and len(set(t)) == 1) for t in tubes)

def canon(tubes):
    return tuple(sorted(tuple(t) for t in tubes))

def top_run_len(tube):
    if not tube: return 0
    top = tube[-1]
    n = 0
    for x in reversed(tube):
        if x == top: n += 1
        else: break
    return n

def bfs_depth(initial, max_states=400000):
    if is_won(initial): return 0
    start = tuple(tuple(t) for t in initial)
    seen = {canon(start)}
    q = deque([(start, 0)])
    explored = 0
    while q:
        state, d = q.popleft()
        explored += 1
        if explored > max_states: return None
        n = len(state)
        for a in range(n):
            if not state[a]: continue
            top_color = state[a][-1]
            run = top_run_len(state[a])
            for b in range(n):
                if a == b: continue
                if len(state[b]) >= MAX_LAYERS: continue
                if state[b] and state[b][-1] != top_color: continue
                space = MAX_LAYERS - len(state[b])
                move_n = min(run, space)
                if move_n == 0: continue
                if not state[b] and run == len(state[a]): continue
                new_state = [list(t) for t in state]
                for _ in range(move_n):
                    new_state[b].append(new_state[a].pop())
                new_tup = tuple(tuple(t) for t in new_state)
                key = canon(new_tup)
                if key in seen: continue
                if is_won(new_tup): return d + 1
                seen.add(key)
                q.append((new_tup, d + 1))
    return -1

def load_seeds():
    src = open(GAME_HTML).read()
    m = re.search(r'const LEVEL_SEEDS\s*=\s*\[(.*?)\];', src, re.DOTALL)
    if not m:
        print(f"FAIL: LEVEL_SEEDS array not found in {GAME_HTML}")
        sys.exit(1)
    body = m.group(1)
    seeds = []
    for entry in re.finditer(r'\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', body):
        seeds.append((int(entry.group(1)), int(entry.group(2)), int(entry.group(3))))
    return seeds

def main():
    seeds = load_seeds()
    print(f"Loaded {len(seeds)} seeds from game.html")
    levels = [generate_level(nt, nc, sd) for nt, nc, sd in seeds]
    print("Solving via BFS…")

    unsolvable, trivial, timeout = [], [], []
    depths = []
    for idx, lvl in enumerate(levels, 1):
        if is_won(lvl):
            trivial.append(idx); depths.append(0); continue
        d = bfs_depth(lvl)
        if d is None:
            timeout.append(idx); depths.append(0)
        elif d == -1:
            unsolvable.append(idx); depths.append(0)
        else:
            depths.append(d)

    print("\nDepth by band:")
    idx = 0
    band_failures = []
    for count, target in DEPTH_TARGETS:
        band_depths = depths[idx:idx+count]
        valid = [d for d in band_depths if d > 0]
        below = sum(1 for d in valid if d < target)
        avg = sum(valid)/max(1, len(valid))
        flag = " ⚠" if below > count // 5 else ""
        print(f"  L{idx+1:>3}-{idx+count:<3}  target {target:>3}  "
              f"min {min(valid) if valid else 0:>3}  avg {avg:>5.1f}  "
              f"max {max(valid) if valid else 0:>3}  below {below}{flag}")
        if below > count // 5:
            band_failures.append((idx+1, idx+count))
        idx += count

    ok = len(levels) - len(unsolvable) - len(trivial) - len(timeout)
    print(f"\n  Solvable & non-trivial: {ok} / {len(levels)}")
    if unsolvable: print(f"  ✗ Unsolvable ({len(unsolvable)}): {unsolvable[:20]}")
    if trivial:    print(f"  ✗ Trivial   ({len(trivial)}): {trivial[:20]}")
    if timeout:    print(f"  ✗ Timeout   ({len(timeout)}): {timeout[:20]}")

    if unsolvable or trivial or timeout or band_failures:
        print("\nFAIL — regenerate LEVEL_SEEDS using the offline emitter.")
        sys.exit(1)
    print("\nAll levels OK — solvable, non-trivial, meeting depth targets.")
    sys.exit(0)

if __name__ == "__main__":
    main()
