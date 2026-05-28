"""check_chip_token_tint — verify [data-menu-chip] in MENU shim CSS
uses var(--surface) / var(--text) / var(--border) tokens for its
background, text, and border.

Bug origin (2026-05-28 round-13): chips were styled with a hardcoded
grey neutral box (`rgba(127,127,127,0.16)`) which the user called out
as "different color, make them all like Levels/Shop/Games".

Static check: shim source [data-menu-chip] block must include
`var(--surface` AND `var(--text` AND `var(--border` (the latter two
ensuring chip text matches the surface + edges are theme-driven).
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SHIM_SRC = BASE / 'scripts' / '_growth_shim_menu.html'


def check_shim() -> list[str]:
    if not SHIM_SRC.exists():
        return ['_growth_shim_menu.html missing']
    raw = SHIM_SRC.read_text(encoding='utf-8')
    # The shim CSS is built via JS string concatenation
    # ('rule {...}'+'more {...}'+...), so we strip the JS literal
    # boundaries and join all '+'-concatenated strings into one
    # logical CSS blob.
    blob = re.sub(r"'\s*\+\s*\n\s*'", '', raw)
    # Multiple [data-menu-chip] rules exist in the shim (one terse for
    # white-space, one verbose for styling). Combine ALL of them and
    # require the tokens to appear in the union.
    rules = re.findall(r"\[data-menu-chip\]\s*\{[^}]+\}", blob)
    if not rules:
        return ['[data-menu-chip] CSS rule not found in shim CSS blob']
    combined = '\n'.join(rules)
    miss = []
    if 'var(--surface' not in combined: miss.append('var(--surface)')
    if 'var(--text'    not in combined: miss.append('var(--text)')
    if 'var(--border'  not in combined: miss.append('var(--border)')
    if miss:
        return [f'chip rules missing tokens (across all [data-menu-chip] rules): {miss}']
    return []


def main() -> int:
    bad = check_shim()
    for line in bad:
        print('  ✗', line)
    if bad:
        print(f'chip-token-tint check: {len(bad)} blocker(s)')
        return 1
    print('chip-token-tint check: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
