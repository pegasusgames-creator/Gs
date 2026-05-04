#!/usr/bin/env python3
"""One-shot CSS color swap for Nonogram game.html: GitHub-dark → warm paper.

Replaces hardcoded color hex literals in a single pass to avoid double-
substitution. CSS variable names are unchanged — only their values move.
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "Nonogram/android/app/src/main/assets/game.html"

# ordered to avoid partial overlap; case-insensitive match handled by re flag.
SWAP = {
    "#0d1117": "#f5f0e6",   # bg paper cream
    "#161b22": "#ebe4d3",   # surface tan
    "#21262d": "#dcd3bd",   # surface2
    "#30363d": "#bdb091",   # border warm
    "#58a6ff": "#c83838",   # accent ink red
    "#1f4a7a": "#7a2828",   # accent-dim
    "#e6edf3": "#28231e",   # text near-black
    "#8b949e": "#5a4f43",   # text muted warm gray
    "#f85149": "#b8332b",   # error / heart
    "#3fb950": "#3a7a3e",   # success
    "#d29922": "#8a6818",   # coin graphite
}

# Also swap rgba(88,166,255, ...) which is the accent in glow shadows
RGBA_SWAP = [
    (re.compile(r"rgba\(\s*88\s*,\s*166\s*,\s*255", re.I), "rgba(200, 56, 56"),
    (re.compile(r"rgba\(\s*13\s*,\s*17\s*,\s*23",  re.I), "rgba(245, 240, 230"),
    (re.compile(r"rgba\(\s*22\s*,\s*27\s*,\s*34",  re.I), "rgba(235, 228, 211"),
    (re.compile(r"rgba\(\s*48\s*,\s*54\s*,\s*61",  re.I), "rgba(189, 176, 145"),
    (re.compile(r"rgba\(\s*230\s*,\s*237\s*,\s*243", re.I), "rgba(40, 35, 30"),
]

src = SRC.read_text()

# Build single regex covering all hex swaps for atomic substitution.
pattern = re.compile("|".join(re.escape(k) for k in SWAP.keys()), re.IGNORECASE)
def repl(m):
    return SWAP[m.group(0).lower()]
new = pattern.sub(repl, src)

for rgx, sub in RGBA_SWAP:
    new = rgx.sub(sub, new)

# Soften the radial gradient text-shadow glow on menu logo (was a blue glow,
# now should be subtle ink-red on cream).
SRC.write_text(new)

print(f"Updated {SRC}")
print(f"Original size: {len(src)} bytes")
print(f"New size:      {len(new)} bytes")
