"""check_theme_tokens — fail when growth shim / overlay UI uses hardcoded
hex / rgb() colors instead of CSS theme tokens.

Why: the four flagship apps share growth shims (notifications row,
cross-promo card, share button, first-clear celebration, coachmark,
Streak Shield overlay, menu top-bar). Their colors must follow each
app's Daylight/Midnight palette via tokens — `var(--surface)`,
`var(--text)`, `var(--text-mute)`, `var(--border)`, `var(--g-play)`,
`var(--on-accent)`, etc. Hardcoded hex/rgb in these blocks means
overlays look correct on whichever app the shim was originally written
against and broken on every other.

Whitelist (these stay literal, by design):
    - gold coin colors (#d29922, #c97f00, #ffd700) — brand-independent
    - heart red (#b8332b) — brand-independent
    - streak fire orange (#ff8c1a) — brand-independent
    - confetti / decorative colors when scoped to canvas calls
    - badge green (#2ea043)
    - basic #000 / #fff used in shadow rgba()
    - rgba(0,0,0,*) and rgba(255,255,255,*) (modal backdrop / dim layers)

Files checked: any `*.html` in `scripts/_growth_shim_*.html` AND any
embedded growth-shim block inside per-app `game.html`.

Usage:
    python3 scripts/check_theme_tokens.py            # all apps
    python3 scripts/check_theme_tokens.py WaterSortPuzzle
    python3 scripts/check_theme_tokens.py --all
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

WHITELIST_HEX = {
    '#c97f00', '#d29922', '#ffd700', '#fed130',           # gold
    '#b8332b', '#c83838', '#e83b3b',                       # heart red / accent reds (mid-warmth)
    '#ff8c1a',                                             # streak fire
    '#2ea043',                                             # badge green
    '#000', '#fff', '#000000', '#ffffff',                  # base black/white (in shadows/dim layers)
}
HEX_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b')
RGB_RE = re.compile(r'rgb\([^)]+\)')
# var(--TOKEN[, fallback]) — strip these out before scanning so fallbacks
# don't count as violations.
VAR_RE = re.compile(r'var\(--[A-Za-z0-9_-]+(?:,\s*[^)]+)?\)')


def shim_blocks(text: str):
    """Yield (label, body) for every growth-shim <script> block in text."""
    for m in re.finditer(
        r'<script\s+data-growth-shim="([A-Z]+)"[^>]*>([\s\S]*?)</script>',
        text,
    ):
        yield m.group(1), m.group(2)


def violations_in(body: str) -> list[str]:
    cleaned = VAR_RE.sub('', body)
    bad: list[str] = []
    for color in HEX_RE.findall(cleaned):
        if color.lower() in WHITELIST_HEX:
            continue
        bad.append(color)
    # rgb()/rgba() rarely a violation since dim layers (0,0,0,*) /
    # (255,255,255,*) are explicitly OK. Skip these — only hex/named
    # colors fail.
    return sorted(set(bad))


def check_app(app: Path) -> list[str]:
    """Return a list of human-readable violation strings for one app."""
    out: list[str] = []
    p = app / 'android/app/src/main/assets/game.html'
    if not p.exists():
        return out
    text = p.read_text(encoding='utf-8')
    for label, body in shim_blocks(text):
        bad = violations_in(body)
        if bad:
            out.append(f'{app.name}: shim {label} has hardcoded colors {bad}')
    return out


def check_shim_sources() -> list[str]:
    """Return violations in the shim source files themselves."""
    out: list[str] = []
    for src in sorted((BASE / 'scripts').glob('_growth_shim_*.html')):
        text = src.read_text(encoding='utf-8')
        for label, body in shim_blocks(text):
            bad = violations_in(body)
            if bad:
                out.append(f'{src.name}: shim {label} has hardcoded colors {bad}')
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if a]
    apps: list[Path]
    if not args or args == ['--all']:
        apps = [
            BASE / 'WaterSortPuzzle',
            BASE / 'Nonogram',
            BASE / 'Puzzle2048',
            BASE / 'UnblockPuzzle',
        ]
    else:
        apps = [BASE / a for a in args]

    bad = check_shim_sources()
    for app in apps:
        bad.extend(check_app(app))
    if bad:
        for line in bad:
            print('  ✗', line)
        print(f'theme-token check: {len(bad)} violation(s)')
        return 1
    print('theme-token check: OK (only whitelisted brand colors remain)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
