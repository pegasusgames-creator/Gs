#!/usr/bin/env python3
"""check_utility_shell.py — every utility-track app ships the utility-shell essentials.

The utility track (docs/portfolio_tracks.json "utility": tools, calculators,
trackers, timers, reference, party decks, music tools, creative toys) is built
on the lean UTILITY SHELL (HabitTracker; docs/UTILITY_SHELL.md), not the game
shell. A tool that ships without the shell's money/consent/i18n plumbing is
the same "tap Buy, get nothing" / dead-link / English-only failure the game
gates catch — so this gate re-asserts the essentials for utilities, and keeps
the game growth stack (lives, coins, streak shields, win-backs, leaderboards)
OUT of tools, where it is meaningless and reads as a templated clone.

BLOCKS (per utility-track app):
  - no Restore Purchases control (`restorePurchases` never called);
  - privacy policy is not the canonical https://pegasusgames-creator.github.io/privacy.html;
  - no `window.onPurchaseSuccess`, or the grant path does not handle BOTH
    `remove_ads` and `pro_lifetime` (iaps.json must sell both too), or no
    `replayPendingGrants` / `pendingGrants` safety net;
  - an interstitial call (`showInterstitial`) without the cadence guard:
    an ad-free check (`adsRemoved()`), a never-in-the-first-session check
    (`sessions`) and a >= 3-minute floor (180000 ms) in the same function;
  - the language picker (`window.LANG_NAMES`) or the string table
    (`window.GAME_I18N`) misses any of the 13 listing languages;
  - no `<span data-app-version>` (the About/version line);
  - game growth shims (`data-growth-shim=` / `GROWTH_CFG`) are present.
WARNS: subscriptions in iaps.json (the shell sells one-time unlocks only);
  an app that is not on the shell yet (no "UTILITY SHELL" marker).

Usage:
  python3 scripts/check_utility_shell.py [App ...]   # only utility-track apps among them are checked
  python3 scripts/check_utility_shell.py             # every utility-track app with a game.html
  python3 scripts/check_utility_shell.py --shell-only  # only apps already on the shell
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PRIVACY = "https://pegasusgames-creator.github.io/privacy.html"
LANGS = ["en", "ar", "de", "es", "fr", "hi", "id", "it", "ja", "pt", "tr", "uk", "zh"]
SKUS = ("remove_ads", "pro_lifetime")
MARKER = "UTILITY SHELL"


def utility_apps():
    try:
        tracks = json.loads((BASE / "docs/portfolio_tracks.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return set(tracks.get("utility", []))


def _func_around(src: str, idx: int) -> str:
    """Text of the innermost function / method body that contains idx (approx.)."""
    starts = [m.start() for m in re.finditer(
        r"\bfunction\b|=>\s*\{|\b(?!(?:if|for|while|switch|catch|with)\b)[A-Za-z_$][\w$]*\s*\([^()]*\)\s*\{", src[:idx])]
    start = starts[-1] if starts else max(0, idx - 1500)
    depth, i = 0, src.find("{", start)
    if i < 0 or i > idx:
        return src[max(0, idx - 1500): idx + 300]
    j = i
    while j < len(src):
        c = src[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = src[start: j + 1]
    return body if start <= idx <= j else src[max(0, idx - 1500): idx + 300]


def check_app(app: str):
    blockers, warnings = [], []
    gh = BASE / app / "android/app/src/main/assets/game.html"
    if not gh.exists():
        return [f"{app}: no game.html"], warnings
    s = gh.read_text(encoding="utf-8", errors="replace")
    if MARKER not in s:
        warnings.append(f"{app}: not on the utility shell yet (no '{MARKER}' marker) — scaffold with "
                        f"scaffold_flagship.py {app} --from HabitTracker --replace-iaps")

    if "restorePurchases" not in s:
        blockers.append(f"{app}: no Restore Purchases control (restorePurchases is never called)")
    if PRIVACY not in s:
        blockers.append(f"{app}: privacy policy link is not the canonical {PRIVACY}")

    if not re.search(r"window\.onPurchaseSuccess\s*=|function\s+onPurchaseSuccess\s*\(", s):
        blockers.append(f"{app}: no window.onPurchaseSuccess — the Java billing bridge drops every purchase")
    for sku in SKUS:
        if not re.search(r"case\s*['\"]%s['\"]|['\"]%s['\"]\s*[:=)]" % (sku, sku), s):
            blockers.append(f"{app}: purchase grant does not handle '{sku}'")
    if "replayPendingGrants" not in s or "pendingGrants" not in s:
        blockers.append(f"{app}: no pendingGrants / replayPendingGrants safety net for unknown SKUs")
    try:
        iaps = json.loads((BASE / app / "metadata/iaps.json").read_text(encoding="utf-8"))
        ids = {p.get("id") for p in iaps.get("one_time_products", [])}
        for sku in SKUS:
            if sku not in ids:
                blockers.append(f"{app}: metadata/iaps.json does not sell '{sku}'")
        if iaps.get("subscriptions"):
            warnings.append(f"{app}: iaps.json lists subscriptions — the utility shell sells one-time unlocks only")
    except (OSError, ValueError):
        blockers.append(f"{app}: metadata/iaps.json missing or unreadable")

    for m in re.finditer(r"['\"]showInterstitial['\"]|\.showInterstitial\s*\(", s):
        line = s[s.rfind("\n", 0, m.start()) + 1: s.find("\n", m.start())]
        if re.search(r"(public|private)\s+void|@JavascriptInterface", line):
            continue
        body = _func_around(s, m.start())
        missing = [n for n, pat in (("adsRemoved()", r"adsRemoved\s*\("), ("first-session check", r"sessions"),
                                    (">= 3-minute floor", r"180000|3\s*\*\s*60\s*\*\s*1000"))
                   if not re.search(pat, body)]
        if missing:
            ln = s.count("\n", 0, m.start()) + 1
            blockers.append(f"{app}:{ln}: interstitial without the cadence guard (missing {', '.join(missing)})")

    nm = re.search(r"window\.LANG_NAMES\s*=\s*\{(.*?)\};", s, re.S)
    names = set(re.findall(r"\b([a-z]{2})\s*:\s*['\"]", nm.group(1))) if nm else set()
    miss = [l for l in LANGS if l not in names]
    if miss:
        blockers.append(f"{app}: language picker (window.LANG_NAMES) misses {miss}")
    gi = re.search(r"window\.GAME_I18N\s*=\s*\{", s)
    blocks = set(re.findall(r"\n\s{2}([a-z]{2})\s*:\s*\{", s[gi.end(): nm.start()] if gi and nm else ""))
    miss = [l for l in LANGS if l not in blocks]
    if miss:
        blockers.append(f"{app}: string table (window.GAME_I18N) has no block for {miss}")

    if not re.search(r"<span[^>]*\bdata-app-version\b", s):
        blockers.append(f"{app}: no <span data-app-version> (About / version line)")

    if re.search(r"data-growth-shim\s*=", s) or "GROWTH_CFG" in s:
        blockers.append(f"{app}: ships game growth shims (data-growth-shim / GROWTH_CFG) — utilities carry none")
    return blockers, warnings


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    util = utility_apps()
    apps = [a for a in args if a in util] if args else sorted(
        a for a in util if (BASE / a / "android/app/src/main/assets/game.html").exists())
    bad, warn = [], []
    for a in apps:
        if "--shell-only" in sys.argv:
            gh = BASE / a / "android/app/src/main/assets/game.html"
            if not gh.exists() or MARKER not in gh.read_text(encoding="utf-8", errors="replace"):
                continue
        b, w = check_app(a)
        bad.extend(b); warn.extend(w)
    for line in bad:
        print("  ✗", line)
    for line in warn:
        print("  ⚠", line)
    if bad:
        print(f"utility-shell check: {len(bad)} blocker(s)")
        return 1
    print(f"utility-shell check: OK ({len(apps)} utility app(s))" + (f", {len(warn)} warning(s)" if warn else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
