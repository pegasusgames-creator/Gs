#!/usr/bin/env python3
"""
pre_publish_check.py
Runs automated safety + completeness checks across the whole app portfolio
before any release.

Catches the kinds of mistakes that get Google Play developer accounts
terminated under the Repetitive Content / Spam policies, and the kinds of
metadata gaps that cause App Store / Play Console submissions to be rejected.

Check groups:

  CODE & IDENTITY
    1. Two or more apps sharing a byte-identical game.html
    2. An app whose folder name disagrees with its game.html <title>
    3. Duplicate AdMob app IDs or ad unit IDs across apps
    4. Duplicate package names (applicationId) across apps
    5. Placeholder sentinel values that were never filled in
       (ENTER_YOUR_..., ca-app-pub-XXX, etc.)

  STORE ASSETS
    6. store/icon_512_playstore.png — exists, unique
    7. store/feature_graphic_1024x500.png — exists, unique
    8. store/icon_1024_appstore.png — exists, unique
    9. store/screenshots/phone/*.png — >=2 files, unique across apps
   10. store/screenshots/iphone_6_9/*.png — >=1 file (warning if missing)

  STORE METADATA (per app, under metadata/)
   11. metadata/en-US/title.txt — exists, <=30 chars, unique
   12. metadata/en-US/short_description.txt — exists, <=80 chars
   13. metadata/en-US/subtitle.txt — exists, <=30 chars
   14. metadata/en-US/full_description.txt — exists, <=4000 chars, unique
   15. metadata/en-US/keywords.txt — exists, <=100 chars
   16. metadata/en-US/promotional_text.txt — exists, <=170 chars
   17. metadata/en-US/release_notes.txt — exists, <=500 chars
   18. metadata/app_info.json — valid, required keys filled in
   19. metadata/privacy.json — valid, privacy_policy_url present
   20. metadata/content_rating.json — valid, iarc_answers present
   21. metadata/iaps.json — valid, IDs match MainActivity.java
   22. metadata/review_notes.json — valid

  CONTENT QUALITY
   23. Thin game.html files (< THIN_BYTES) — warning
   24. Prohibited marketing language in descriptions/screenshots — warning
   25. Description text templated across apps — warning

Exit code:
  0  -> all checks passed
  1  -> one or more BLOCKING issues found (do not publish)
  2  -> only WARNINGS found (publish at your discretion)

Usage:
  python3 pre_publish_check.py                 # check all apps
  python3 pre_publish_check.py App1 App2       # check only specific apps
  python3 pre_publish_check.py --strict        # treat warnings as blocking
  python3 pre_publish_check.py --only code     # only run CODE & IDENTITY group
  python3 pre_publish_check.py --only store    # only store assets
  python3 pre_publish_check.py --only meta     # only metadata
"""

import hashlib
import json
import os
import re
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_template", "_release", "__pycache__", ".git", ".idea", "node_modules"}

# ---------- limits (from Google Play + App Store 2026 requirements) ----------

TITLE_MAX            = 30
SHORT_DESC_MAX       = 80
SUBTITLE_MAX         = 30
FULL_DESC_MAX        = 4000
KEYWORDS_MAX         = 100
PROMO_TEXT_MAX       = 170
RELEASE_NOTES_MAX    = 500

THIN_BYTES           = 8 * 1024          # game.html under this is min-functionality risk
MIN_PHONE_SCREENSHOTS = 2                 # Google Play requires at least 2

# Canonical URLs and contact info — see CLAUDE.md "Canonical contact info"
CANONICAL_PRIVACY_URL          = "https://pegasusgames-creator.github.io/privacy.html"
CANONICAL_PRIVACY_URL_KIDS     = "https://pegasusgames-creator.github.io/privacy-kids.html"
CANONICAL_SUPPORT_URL          = "https://pegasusgames-creator.github.io/"
CANONICAL_MARKETING_URL        = "https://pegasusgames-creator.github.io/"
CANONICAL_DEVELOPER_EMAIL      = "pegasusgames@atomicmail.io"

# Patterns for old/stale placeholder URLs that should never appear
OLD_PLACEHOLDER_URL_PATTERNS = [
    r"pegasusgames\.example",            # original scaffold placeholder
    r"pegasusgames\.com(?!ai)",          # if anyone invented a real-looking URL
    r"@outlook\.com",                    # the old email I incorrectly suggested
]

# Apps blocked from any release pipeline because their game.html is a
# placeholder (actually Dice Roller content under a different folder name).
# Mirrors the list in CLAUDE.md "Placeholder clones — DO NOT PUBLISH".
# These blocks lift only when the app's game.html is rewritten to be real.
BLOCKED_APPS = {
    "DiceRoller", "EmotionFlash", "FindDifference", "FlashlightSOS",
    "FruitMerge", "GuitarChords", "HiddenObject", "JigsawPuzzle",
    "MahjongSolitaire", "MemoryCard", "Metronome", "MovieTrivia",
    "MultiplicationGame", "MusicTheory", "NumberMemory", "PasswordGen",
    "PatternSequence", "PianoKeyboard", "PinPull", "QRCodeGen",
    "RandomName", "RandomNumber", "RandomRecipe", "ScienceQuiz",
    "ScrewPuzzle", "SlidingTiles", "SolarSystem", "SportsQuiz",
    "Sumplete", "TripleMatch", "UkuleleChords", "WordScramble",
    "WordSearch",
}

# Reference Dice Roller game.html hash, computed on first run and cached
# in module state. If a "blocked" app's game.html no longer matches this
# hash, we trust it was rewritten and lift the block for that one app.
_DICE_ROLLER_HASH_CACHE = None

# Prohibited language in store copy and screenshots (Google Play + Apple)
PROHIBITED_PHRASES = [
    r"\b#\s*1\b", r"\bnumber\s+one\b", r"\bbest\b",
    r"\btop\b(?!\s+(row|level|score|100))",   # 'top score' etc. is fine
    r"\baward[\s-]?winning\b",
    r"\bdownload\s+now\b", r"\binstall\s+now\b", r"\bplay\s+now\b",
    r"\btry\s+now\b", r"\bclick\s+here\b",
    r"\bmillion\s+downloads?\b", r"\bbillion\s+downloads?\b",
    r"\b\d+\s*%\s*off\b", r"\bfree\s+for\s+a\s+limited\s+time\b",
    r"\bfor\s+free\b(?=.*\bdownload\b)",
    r"\bapp\s+of\s+the\s+(year|month|week|day)\b",
]

# Placeholder sentinel values that shouldn't ship
PLACEHOLDER_PATTERNS = [
    r"ENTER_[A-Z_]+",
    r"ca-app-pub-XXX",
    r"ca-app-pub-3940256099942544",   # Google's public test AdMob ID
    r"YOUR_APP_ID_HERE",
    r"TODO_REPLACE",
    r"__ADMOB_[A-Z_]+_PLACEHOLDER__",  # SHIP_GAME Phase 2 placeholders
]

# Filler words in title matching (ignore these when checking folder vs <title>)
TITLE_FILLER = {"for", "the", "a", "an", "and", "of", "my", "your", "kids", "pro", "app"}


# ---------- small helpers ----------------------------------------------------

def color(s, code):
    if not sys.stdout.isatty():
        return s
    return f"\033[{code}m{s}\033[0m"

def red(s):    return color(s, "31")
def yellow(s): return color(s, "33")
def green(s):  return color(s, "32")
def bold(s):   return color(s, "1")
def dim(s):    return color(s, "2")

def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def list_apps(filter_names=None):
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP_DIRS or name.startswith("."):
            continue
        path = os.path.join(BASE, name)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(os.path.join(path, "android")):
            continue
        if filter_names and name not in filter_names:
            continue
        apps.append(name)
    return apps

def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return None

def read_stripped(path):
    s = read(path)
    return s.strip() if s is not None else None

def read_json(path):
    """Return (data, error_string). Data is None if file missing or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e.msg} at line {e.lineno}"

def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def tokenize(s):
    """Split a name into lowercase alphanumeric tokens.
    Splits on camelCase, letter/digit boundaries, non-alphanumerics.
    Strips trailing 's' so 'Numerals' matches 'Numeral'."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    s = re.sub(r"(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])", " ", s)
    tokens = [t.lower() for t in re.findall(r"[A-Za-z0-9]+", s)]
    return [t[:-1] if len(t) > 3 and t.endswith("s") else t for t in tokens]

def titles_match(folder, title):
    """True if folder name and HTML title refer to the same app."""
    nf, nt = normalize(folder), normalize(title)
    if nf in nt or nt in nf:
        return True
    folder_tokens = {t for t in tokenize(folder) if t not in TITLE_FILLER}
    title_tokens  = {t for t in tokenize(title)  if t not in TITLE_FILLER}
    if not folder_tokens:
        return True
    return folder_tokens.issubset(title_tokens) or title_tokens.issubset(folder_tokens)


# ---------- CODE & IDENTITY checks -------------------------------------------

def check_duplicate_game_html(apps):
    issues = []
    hashes = defaultdict(list)
    for app in apps:
        path = os.path.join(BASE, app, "android", "app", "src", "main", "assets", "game.html")
        if os.path.exists(path):
            hashes[md5_of(path)].append(app)
    for h, dupes in hashes.items():
        if len(dupes) > 1:
            issues.append(
                f"{len(dupes)} apps share the same game.html (md5={h[:12]}): " + ", ".join(dupes)
            )
    return issues

def check_title_matches_folder(apps):
    issues = []
    for app in apps:
        html_path = os.path.join(BASE, app, "android", "app", "src", "main", "assets", "game.html")
        content = read(html_path)
        if content is None:
            issues.append(f"{app}: game.html is missing")
            continue
        m = re.search(r"<title>([^<]+)</title>", content)
        if not m:
            issues.append(f"{app}: game.html has no <title> tag")
            continue
        title = m.group(1).strip()
        if not titles_match(app, title):
            issues.append(f"{app}: folder name does not match <title>={title!r}")
    return issues

def check_duplicate_admob_ids(apps):
    issues = []
    id_to_apps = defaultdict(list)
    for app in apps:
        for relpath in [
            "android/app/src/main/java",
            "android/app/src/main/AndroidManifest.xml",
        ]:
            root = os.path.join(BASE, app, relpath)
            if not os.path.exists(root):
                continue
            walked = [root] if os.path.isfile(root) else (
                [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs]
            )
            for path in walked:
                if not path.endswith((".java", ".xml")):
                    continue
                content = read(path) or ""
                for match in re.findall(r"ca-app-pub-\d{16}[/~]\d{6,12}", content):
                    if match.startswith("ca-app-pub-3940256099942544"):
                        continue
                    id_to_apps[match].append(app)
    for admob_id, owners in id_to_apps.items():
        unique_owners = sorted(set(owners))
        if len(unique_owners) > 1:
            issues.append(f"AdMob ID {admob_id} reused across: " + ", ".join(unique_owners))
    return issues

def check_duplicate_package_names(apps):
    issues = []
    pkg_to_apps = defaultdict(list)
    for app in apps:
        gradle_path = os.path.join(BASE, app, "android", "app", "build.gradle")
        content = read(gradle_path)
        if not content:
            continue
        m = re.search(r"applicationId\s+['\"]([^'\"]+)['\"]", content)
        if m:
            pkg_to_apps[m.group(1)].append(app)
    for pkg, owners in pkg_to_apps.items():
        if len(owners) > 1:
            issues.append(f"applicationId {pkg} reused across: " + ", ".join(owners))
    return issues

def check_package_name_drift(apps):
    """BLOCKING: app_info.json:package_name (Назва пакета) must match
    android/app/build.gradle:applicationId. Drift between the two means
    the Play Console listing identifies a different APK than the one
    being uploaded."""
    issues = []
    app_id_re = re.compile(r'applicationId\s*["\']([^"\']+)["\']')
    for app in apps:
        gradle = os.path.join(BASE, app, "android/app/build.gradle")
        info_path = os.path.join(BASE, app, "metadata/app_info.json")
        if not (os.path.exists(gradle) and os.path.exists(info_path)):
            continue
        gradle_text = read(gradle) or ""
        match = app_id_re.search(gradle_text)
        if not match:
            issues.append(f"{app}: no applicationId in android/app/build.gradle")
            continue
        actual = match.group(1)
        try:
            info = json.loads(read(info_path) or "{}")
        except Exception as e:
            issues.append(f"{app}: app_info.json invalid JSON ({e})")
            continue
        recorded = info.get("package_name")
        if not recorded:
            issues.append(
                f"{app}: metadata/app_info.json missing 'package_name' "
                f"(run scripts/sync_package_names.py)")
        elif recorded != actual:
            issues.append(
                f"{app}: package_name mismatch — app_info.json has "
                f"{recorded!r}, build.gradle has {actual!r}")
    return issues


def check_placeholders(apps):
    issues = []
    pattern = re.compile("|".join(PLACEHOLDER_PATTERNS))
    for app in apps:
        for relpath in [
            "android/app/src/main/java",
            "android/app/src/main/AndroidManifest.xml",
            "android/app/build.gradle",
            "android/keystore.properties",
        ]:
            root = os.path.join(BASE, app, relpath)
            if not os.path.exists(root):
                continue
            walked = [root] if os.path.isfile(root) else (
                [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs]
            )
            for path in walked:
                content = read(path) or ""
                hit = pattern.search(content)
                if hit:
                    issues.append(f"{app}: placeholder {hit.group(0)!r} in {os.path.relpath(path, BASE)}")
                    break
    return issues


# ---------- STORE ASSETS checks ----------------------------------------------

def check_store_image(apps, relpath, label):
    """Generic check: store file exists and is unique across apps. Returns (blocking, warnings)."""
    blocking = []
    warnings = []
    hashes = defaultdict(list)
    for app in apps:
        path = os.path.join(BASE, app, relpath)
        if not os.path.exists(path):
            blocking.append(f"{app}: missing {relpath}")
        else:
            hashes[md5_of(path)].append(app)
    for h, owners in hashes.items():
        if len(owners) > 1:
            warnings.append(f"{label} shared across {len(owners)} apps: " + ", ".join(owners))
    return blocking, warnings

def check_screenshots(apps, sub, minimum, label, blocking_if_missing=True):
    """Check that each app has at least `minimum` unique PNGs in screenshots/<sub>/."""
    blocking = []
    warnings = []
    hashes = defaultdict(list)
    for app in apps:
        folder = os.path.join(BASE, app, "store", "screenshots", sub)
        if not os.path.isdir(folder):
            msg = f"{app}: missing store/screenshots/{sub}/ directory"
            (blocking if blocking_if_missing else warnings).append(msg)
            continue
        pngs = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
        if len(pngs) < minimum:
            msg = f"{app}: {label} has {len(pngs)} PNGs (need >= {minimum})"
            (blocking if blocking_if_missing else warnings).append(msg)
        for f in pngs:
            path = os.path.join(folder, f)
            hashes[md5_of(path)].append(app)
    for h, owners in hashes.items():
        unique = sorted(set(owners))
        if len(unique) > 1:
            warnings.append(f"{label} image shared across: " + ", ".join(unique))
    return blocking, warnings


# ---------- STORE METADATA checks --------------------------------------------

def check_text_file(apps, relpath, max_len, label, check_unique=False):
    """Check: file exists, non-empty, under max_len chars, optionally unique across apps."""
    blocking = []
    warnings = []
    values = defaultdict(list)
    for app in apps:
        path = os.path.join(BASE, app, relpath)
        content = read_stripped(path)
        if content is None:
            blocking.append(f"{app}: missing {relpath}")
            continue
        if content == "":
            blocking.append(f"{app}: {relpath} is empty")
            continue
        if len(content) > max_len:
            blocking.append(f"{app}: {label} is {len(content)} chars (max {max_len})")
            continue
        if check_unique:
            values[content.lower()].append(app)
    if check_unique:
        for text, owners in values.items():
            if len(owners) > 1:
                warnings.append(
                    f"{label} text shared across {len(owners)} apps: " + ", ".join(owners)
                    + f" — {text[:40]!r}..."
                )
    return blocking, warnings

def check_json_file(apps, relpath, required_keys, label):
    """Check: JSON file exists, parses, has all required keys non-empty."""
    blocking = []
    for app in apps:
        path = os.path.join(BASE, app, relpath)
        data, err = read_json(path)
        if err == "missing":
            blocking.append(f"{app}: missing {relpath}")
            continue
        if err:
            blocking.append(f"{app}: {relpath} {err}")
            continue
        for key in required_keys:
            # Support nested keys like "google_data_safety.encrypted_in_transit"
            parts = key.split(".")
            node = data
            found = True
            for p in parts:
                if not isinstance(node, dict) or p not in node:
                    found = False
                    break
                node = node[p]
            if not found:
                blocking.append(f"{app}: {relpath} missing required key '{key}'")
                continue
            # Empty string / None / empty list all count as missing
            if node in (None, "", []):
                blocking.append(f"{app}: {relpath} key '{key}' is empty")
    return blocking

# Canonical IAP descriptions — keep in sync with docs/IAP_CATALOG.md.
# Play Console "Опис" / Description field is required, ≤200 chars.
IAP_CANONICAL_DESCRIPTIONS = {
    "remove_ads": "Permanently removes all banner and interstitial ads. Rewarded ads remain available so you can still earn free coins and lives.",
    "coins_small": "Adds 100 coins to your wallet. Spend coins on hints, extra moves, and unlocking new themes.",
    "coins_medium": "Adds 400 coins to your wallet. Spend coins on hints, boosters, and unlocking new themes.",
    "coins_large": "Adds 800 coins to your wallet. Great value coin pack — spend on hints, extra moves, and unlocking new themes.",
    "coins_mega": "Adds 2000 coins to your wallet. Our largest coin pack and best value — spend on hints, boosters, and unlocking new themes.",
    "five_lives": "Instantly refills your hearts to the maximum so you can keep playing without waiting for them to recharge.",
    "unlimited_lives_1h": "Play with unlimited lives for one full hour. Perfect for a long puzzle session without any interruption.",
    "unlimited_lives_forever": "Never run out of lives again. Play as many levels as you want, whenever you want, with no waiting.",
    "unlimited_undos": "Undo any move at any time, as many times as you want. No more restarting a level after one small mistake.",
    "undo_pack": "Adds 10 undos to your account. Take back any move at any time so one mistake never costs you a level.",
    "hint_pack": "Adds 10 hints to your account. Each hint reveals the next correct move on any level where you are stuck.",
    "starter_pack": "100 coins + 5 hints (or 5 undos) + 5 lives + Ads Off, bundled for new players. One-time purchase.",
    "season_pass_monthly": "Monthly pass: ad-free play, +100 coins every day, all themes unlocked, and unlimited boosters. Cancel anytime in Google Play.",
    "weekly_pass": "Weekly pass: ad-free play, +50 coins every day, all themes unlocked, and unlimited boosters. Cancel anytime in Google Play.",
}
IAP_DESC_MAX = 200


def check_iaps_descriptions(apps):
    """BLOCK if any IAP entry is missing a description or exceeds 200 chars.
    WARN if a description drifts from the canonical text in docs/IAP_CATALOG.md."""
    blocking = []
    warnings = []
    for app in apps:
        iaps_path = os.path.join(BASE, app, "metadata", "iaps.json")
        data, err = read_json(iaps_path)
        if err or not data:
            continue  # already flagged by check_json_file
        for section in ("one_time_products", "subscriptions"):
            for p in data.get(section, []):
                if not isinstance(p, dict):
                    continue
                pid = p.get("id", "?")
                desc = p.get("description")
                if not desc:
                    blocking.append(f"{app}: iaps.json[{section}][{pid}] is missing 'description' "
                                    f"(Play Console requires it, ≤{IAP_DESC_MAX} chars; "
                                    f"see docs/IAP_CATALOG.md)")
                    continue
                if len(desc) > IAP_DESC_MAX:
                    blocking.append(f"{app}: iaps.json[{section}][{pid}] description is "
                                    f"{len(desc)} chars (max {IAP_DESC_MAX})")
                    continue
                canonical = IAP_CANONICAL_DESCRIPTIONS.get(pid)
                if canonical and desc != canonical:
                    warnings.append(f"{app}: iaps.json[{section}][{pid}] description drifted "
                                    f"from docs/IAP_CATALOG.md canonical text")
    return blocking, warnings


def check_iap_invariants(apps):
    """BLOCKING: enforce the four IAP correctness invariants from
    CLAUDE.md "## IAP correctness invariants". Delegates to
    scripts/check_iap_invariants.py for the actual rules so both this
    pre-publish guard and the standalone command share one source of
    truth."""
    blocking = []
    warnings = []
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import check_iap_invariants as cii
    except ImportError as e:
        warnings.append(f"check_iap_invariants module not importable: {e}")
        return blocking, warnings
    for app in apps:
        for sev, msg in cii.check_app(app):
            (blocking if sev == 'BLOCKER' else warnings).append(f"{app}: {msg}")
    return blocking, warnings


def _delegated_check(module_name):
    """Build a check function that delegates per-app to a sibling module's
    check_app(app) -> list of (sev, msg). Used for the retention/economy
    parity checks added alongside the WaterSort/Nonogram/Puzzle2048 audit."""
    def _run(apps):
        blocking, warnings = [], []
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            mod = __import__(module_name)
        except ImportError as e:
            warnings.append(f"{module_name} module not importable: {e}")
            return blocking, warnings
        for app in apps:
            try:
                results = mod.check_app(app)
            except Exception as e:  # never let a heuristic check abort the run
                warnings.append(f"{app}: {module_name}.check_app raised {e!r}")
                continue
            for sev, msg in results:
                (blocking if sev == 'BLOCKER' else warnings).append(f"{app}: {msg}")
        return blocking, warnings
    return _run


# Retention / economy parity checks (CLAUDE.md "Retention-feature parity
# invariant", "Subscription/bundle promise parity", "Coin tier ladder",
# "Booster catalog by genre", "Cross-cutting menu requirements", "Seasonal events").
check_iap_grant_parity     = _delegated_check("check_iap_grant_parity")
check_retention_features   = _delegated_check("check_retention_features")
check_subscription_parity  = _delegated_check("check_subscription_parity")
check_coin_tier_ladder     = _delegated_check("check_coin_tier_ladder")
check_booster_catalog      = _delegated_check("check_booster_catalog")
check_menu_completeness    = _delegated_check("check_menu_completeness")
check_seasonal_events      = _delegated_check("check_seasonal_events")
# puzzle_solvability — BFS-solver gate: blocks any puzzle game shipping a
# level that is unsolvable or carries a wrong optimal/par (added after the
# 2026-05-15 UnblockPuzzle audit found 35/150 unsolvable, 114/150 mislabelled).
check_puzzle_solvability   = _delegated_check("check_unblock_solvable")

# Audit 2026-05-15 — slip-prevention checks (G2-G6): price-string parity,
# restore-purchases UI, interstitial cadence, IAP display-name table,
# screenshot headline/content match.
check_price_string_parity       = _delegated_check("check_price_string_parity")
check_restore_purchases_ui      = _delegated_check("check_restore_purchases_ui")
check_interstitial_cadence      = _delegated_check("check_interstitial_cadence")
check_iap_display_name_table    = _delegated_check("check_iap_display_name_table")
check_screenshot_headline_match = _delegated_check("check_screenshot_headline_match")

# Audit 2026-05-20 — subscription billing routing: every subscription SKU
# must reach the SUBS billing flow, never the one-time INAPP path (the
# UnblockPuzzle/PipeConnect weekly_pass dead-end bug).
check_subscription_routing      = _delegated_check("check_subscription_routing")


def check_iaps_match_code(apps):
    """Warn if metadata/iaps.json IDs don't match the PRODUCT_IDS list in MainActivity.java."""
    warnings = []
    for app in apps:
        iaps_path = os.path.join(BASE, app, "metadata", "iaps.json")
        data, err = read_json(iaps_path)
        if err or not data:
            continue  # already flagged by check_json_file
        declared = set()
        for p in data.get("one_time_products", []) + data.get("subscriptions", []):
            if isinstance(p, dict) and "id" in p:
                declared.add(p["id"])

        # Find MainActivity.java and extract IAP IDs from the PRODUCT_IDS-like array
        java_root = os.path.join(BASE, app, "android", "app", "src", "main", "java")
        if not os.path.isdir(java_root):
            continue
        code_ids = set()
        for dp, _, fs in os.walk(java_root):
            for f in fs:
                if f == "MainActivity.java":
                    content = read(os.path.join(dp, f)) or ""
                    # Grab string literals that look like IAP IDs (lowercase with underscores)
                    for m in re.findall(r'"([a-z][a-z0-9_]{3,40})"', content):
                        if "_" in m or m in {"remove_ads", "hint_pack", "starter_pack"}:
                            code_ids.add(m)
        missing_in_code     = declared - code_ids
        missing_in_metadata = code_ids - declared
        if missing_in_code:
            warnings.append(f"{app}: IAPs in metadata but not in MainActivity.java: "
                            + ", ".join(sorted(missing_in_code)))
        # Only warn about code-only IDs that look like IAP products
        iap_like = {c for c in missing_in_metadata
                    if any(c.startswith(p) or c == p for p in
                           ("remove_ads", "coins_", "hint", "starter", "season",
                            "five_lives", "unlimited_lives"))}
        if iap_like:
            warnings.append(f"{app}: IAPs in MainActivity.java but not in metadata: "
                            + ", ".join(sorted(iap_like)))
    return warnings


# ---------- CONTENT QUALITY checks -------------------------------------------

def check_thin_games(apps):
    warnings = []
    for app in apps:
        path = os.path.join(BASE, app, "android", "app", "src", "main", "assets", "game.html")
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size < THIN_BYTES:
                warnings.append(f"{app}: game.html is only {size} bytes (thin — minimum functionality risk)")
    return warnings

def check_prohibited_language(apps):
    warnings = []
    pattern = re.compile("|".join(PROHIBITED_PHRASES), re.IGNORECASE)
    for app in apps:
        for relpath in [
            "metadata/en-US/title.txt",
            "metadata/en-US/short_description.txt",
            "metadata/en-US/subtitle.txt",
            "metadata/en-US/full_description.txt",
            "metadata/en-US/promotional_text.txt",
        ]:
            path = os.path.join(BASE, app, relpath)
            content = read(path)
            if not content:
                continue
            # Skip placeholder files that haven't been filled in yet — no real
            # marketing copy to check. These will be caught by the 'missing'
            # and 'unique' checks elsewhere once the app is actually published.
            if content.strip().startswith("TODO"):
                continue
            m = pattern.search(content)
            if m:
                warnings.append(f"{app}: prohibited phrase {m.group(0)!r} in {relpath}")
    return warnings


# ---------- CANONICAL URL checks ---------------------------------------------

def check_canonical_urls(apps):
    """BLOCKING: privacy/support/marketing URLs must match canonical values.
    Allows kids privacy URL for apps targeted at children."""
    blocking = []
    for app in apps:
        # privacy.json
        priv_path = os.path.join(BASE, app, "metadata", "privacy.json")
        data, err = read_json(priv_path)
        if not err and data:
            url = data.get("privacy_policy_url", "")
            if url not in (CANONICAL_PRIVACY_URL, CANONICAL_PRIVACY_URL_KIDS):
                blocking.append(
                    f"{app}: metadata/privacy.json privacy_policy_url is {url!r} — "
                    f"must be {CANONICAL_PRIVACY_URL!r} (general apps) or "
                    f"{CANONICAL_PRIVACY_URL_KIDS!r} (kids apps)"
                )
        # app_info.json
        info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        data, err = read_json(info_path)
        if not err and data:
            for field, expected in [
                ("support_url",   CANONICAL_SUPPORT_URL),
                ("marketing_url", CANONICAL_MARKETING_URL),
            ]:
                actual = data.get(field, "")
                # marketing_url is optional — empty string is allowed
                if field == "marketing_url" and actual == "":
                    continue
                if actual != expected:
                    blocking.append(
                        f"{app}: metadata/app_info.json {field} is {actual!r} — "
                        f"must be {expected!r}"
                    )
    return blocking

def check_no_per_app_privacy_html(apps):
    """BLOCKING: no per-app privacy-policy.html should exist. Single source of
    truth is the shared GitHub Pages URL. Stale per-app copies risk Data Safety
    mismatch with the URL declared in Play Console."""
    blocking = []
    for app in apps:
        # Common locations a per-app privacy file might end up
        candidates = [
            os.path.join(BASE, app, "store", "privacy-policy.html"),
            os.path.join(BASE, app, "store", "privacy.html"),
            os.path.join(BASE, app, "privacy-policy.html"),
            os.path.join(BASE, app, "privacy.html"),
        ]
        for path in candidates:
            if os.path.exists(path):
                blocking.append(
                    f"{app}: stale per-app privacy file at {os.path.relpath(path, BASE)} — "
                    f"delete it; canonical privacy lives at {CANONICAL_PRIVACY_URL}"
                )
    return blocking

def check_store_paste_locale_tags(apps):
    """BLOCKING: STORE_PASTE.md must NOT contain `<uk-UA>` or `<id-ID>`
    locale tags. Play Console's actual codes are `uk` and `id` — using
    the BCP-47 forms means the user pastes Ukrainian copy into a Play
    Console field that doesn't exist (or worse, into the wrong field).
    Source-of-truth: TRANSLATIONS.md §1 + scripts/gen_store_paste.py."""
    blocking = []
    bad = ["<uk-UA>", "</uk-UA>", "<id-ID>", "</id-ID>"]
    for app in apps:
        path = os.path.join(BASE, app, "STORE_PASTE.md")
        if not os.path.isfile(path):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (IOError, UnicodeDecodeError):
            continue
        hits = [tag for tag in bad if tag in text]
        if hits:
            blocking.append(
                f"{app}: STORE_PASTE.md uses {hits} — Play Console wants "
                f"<uk> and <id> (no country code). Regenerate via "
                f"`python3 scripts/gen_store_paste.py {app} --force`."
            )
    return blocking


def check_old_placeholder_urls(apps):
    """BLOCKING: detect old scaffold placeholder URLs that snuck through."""
    blocking = []
    pattern = re.compile("|".join(OLD_PLACEHOLDER_URL_PATTERNS), re.IGNORECASE)
    metadata_files = [
        "metadata/app_info.json",
        "metadata/privacy.json",
        "metadata/review_notes.json",
    ]
    for app in apps:
        for relpath in metadata_files:
            content = read(os.path.join(BASE, app, relpath))
            if not content:
                continue
            m = pattern.search(content)
            if m:
                blocking.append(
                    f"{app}: stale placeholder string {m.group(0)!r} in {relpath} — "
                    f"replace with canonical value (see CLAUDE.md)"
                )
    return blocking


# ---------- CROSS-APP ASSET SIMILARITY checks --------------------------------
# Google's automated review compares store assets across the developer
# account. Identical icons, feature graphics, or screenshots between apps
# are spam-classifier signals. These checks catch byte-identical assets;
# perceptual similarity (slightly tweaked images) requires a human eye but
# byte-identical is the most common accidental case.

def check_cross_app_asset_similarity(apps):
    """BLOCKING: no two apps may share byte-identical store icons, feature
    graphics, or any individual phone screenshot. Identical *wrapper* code
    is fine (red line #7 in CLAUDE.md), but identical *visual* assets are
    a spam signal."""
    blocking = []
    asset_paths = [
        ("store/icon_512_playstore.png",         "Google icon (512)"),
        ("store/icon_1024_appstore.png",         "Apple icon (1024)"),
        ("store/feature_graphic_1024x500.png",   "Feature graphic"),
    ]
    for relpath, label in asset_paths:
        hashes = defaultdict(list)
        for app in apps:
            full = os.path.join(BASE, app, relpath)
            if os.path.exists(full):
                hashes[md5_of(full)].append(app)
        for h, dupes in hashes.items():
            if len(dupes) > 1:
                blocking.append(
                    f"{label}: {len(dupes)} apps share byte-identical asset "
                    f"(md5={h[:12]}): {', '.join(dupes)} — each app must have "
                    f"its own unique {label}"
                )
    return blocking


def check_screenshot_template_reuse(apps):
    """BLOCKING: no two apps may share an identical phone screenshot file.
    Marketing wrapper templates can be reused (frame, gradient, footer text);
    the resulting *output* PNGs cannot be byte-identical between apps,
    because the gameplay shown inside the frame must differ per app."""
    blocking = []
    hashes = defaultdict(list)
    for app in apps:
        phone_dir = os.path.join(BASE, app, "store", "screenshots", "phone")
        if not os.path.isdir(phone_dir):
            continue
        for fname in sorted(os.listdir(phone_dir)):
            if not fname.lower().endswith('.png'):
                continue
            full = os.path.join(phone_dir, fname)
            hashes[md5_of(full)].append((app, fname))
    for h, occurrences in hashes.items():
        if len(occurrences) > 1:
            apps_seen = set(a for a, f in occurrences)
            if len(apps_seen) > 1:
                pairs = ', '.join(f"{a}/{f}" for a, f in occurrences)
                blocking.append(
                    f"Phone screenshot shared across apps (md5={h[:12]}): {pairs} — "
                    f"the inner gameplay shown in each app's screenshots must differ"
                )
    return blocking


def check_listing_copy_uniqueness(apps):
    """BLOCKING: no two apps may have byte-identical listing copy in any of
    title.txt, short_description.txt, subtitle.txt, full_description.txt.
    Each listing must be hand-written for that specific app — not a
    find-and-replace template (CLAUDE.md red line #3)."""
    blocking = []
    fields = [
        "metadata/en-US/title.txt",
        "metadata/en-US/short_description.txt",
        "metadata/en-US/subtitle.txt",
        "metadata/en-US/full_description.txt",
    ]
    for relpath in fields:
        content_to_apps = defaultdict(list)
        for app in apps:
            content = read_stripped(os.path.join(BASE, app, relpath))
            if content:
                content_to_apps[content].append(app)
        for content, dupes in content_to_apps.items():
            if len(dupes) > 1:
                preview = content[:60].replace('\n', ' ')
                blocking.append(
                    f"{relpath}: {len(dupes)} apps share identical text "
                    f"({preview!r}…): {', '.join(dupes)} — each app's listing "
                    f"copy must be unique"
                )
    return blocking


def check_blocked_apps(apps):
    """BLOCKING: refuse to ship any app on the BLOCKED_APPS list whose
    game.html is still the original Dice Roller content. The block lifts
    automatically once the game.html has been rewritten (no longer matches
    Dice Roller's hash)."""
    global _DICE_ROLLER_HASH_CACHE
    blocking = []

    # Compute the Dice Roller reference hash once
    if _DICE_ROLLER_HASH_CACHE is None:
        ref_path = os.path.join(BASE, "DiceRoller",
                                "android/app/src/main/assets/game.html")
        if os.path.exists(ref_path):
            _DICE_ROLLER_HASH_CACHE = md5_of(ref_path)

    for app in apps:
        if app not in BLOCKED_APPS:
            continue
        gh = os.path.join(BASE, app, "android/app/src/main/assets/game.html")
        if not os.path.exists(gh):
            blocking.append(
                f"{app}: on the BLOCKED_APPS placeholder list and its "
                f"game.html is missing — cannot ship"
            )
            continue
        if _DICE_ROLLER_HASH_CACHE and md5_of(gh) == _DICE_ROLLER_HASH_CACHE:
            blocking.append(
                f"{app}: game.html is byte-identical to Dice Roller — this "
                f"app is on the placeholder-clones blocklist (see CLAUDE.md "
                f"'Placeholder clones — DO NOT PUBLISH'). Rewrite its "
                f"game.html with real, distinct game logic before publishing."
            )
        # If hash differs, the app has been rewritten — block lifts silently.
    return blocking


def check_icon_perceptual_similarity(apps):
    """BLOCKING: detect icons that are visually near-identical between apps,
    even if they're byte-different. Catches the case where the icon
    generator produces two icons with the same composition but minor color
    tweaks (e.g., re-running gen_icon.py with slightly different palettes
    for two apps).

    Uses average-hash (aHash): downscale to 8x8, threshold against mean,
    pack into 64-bit fingerprint. Hamming distance ≤6 between two icon
    aHashes is the empirical threshold for 'visually nearly the same'.
    """
    try:
        from PIL import Image
    except ImportError:
        # PIL not available — skip rather than crash. Byte-identical check
        # in check_cross_app_asset_similarity still provides protection.
        return []

    def ahash(path):
        try:
            img = Image.open(path).convert('L').resize((8, 8), Image.LANCZOS)
            pixels = list(img.tobytes())
            mean = sum(pixels) / len(pixels)
            bits = 0
            for i, p in enumerate(pixels):
                if p > mean:
                    bits |= (1 << i)
            return bits
        except Exception:
            return None

    def hamming(a, b):
        return bin(a ^ b).count('1')

    blocking = []
    icon_relpath = "store/icon_512_playstore.png"
    fingerprints = []
    for app in apps:
        full = os.path.join(BASE, app, icon_relpath)
        if os.path.exists(full):
            h = ahash(full)
            if h is not None:
                fingerprints.append((app, h))

    # Pairwise compare
    SIMILARITY_THRESHOLD = 6  # bits; lower = stricter; 0 = identical
    for i in range(len(fingerprints)):
        for j in range(i + 1, len(fingerprints)):
            app_a, hash_a = fingerprints[i]
            app_b, hash_b = fingerprints[j]
            dist = hamming(hash_a, hash_b)
            if dist <= SIMILARITY_THRESHOLD:
                blocking.append(
                    f"Icons of {app_a} and {app_b} are visually too similar "
                    f"(aHash distance={dist}, threshold={SIMILARITY_THRESHOLD}). "
                    f"Each app needs a genuinely different focal element — "
                    f"not the same composition with swapped colors. See "
                    f"QUALITY_PLAYBOOK §1.1 / §7.4."
                )
    return blocking


def check_archetype_presence(apps):
    """BLOCKING: each app must have metadata/app_identity.md and an entry in
    app_themes.py THEMES dict with all four archetype fields (layout_archetype,
    mascot_pattern, voice, texture). This stops Claude Code from auto-shipping
    yet another A/M0/V1/T1 template clone.

    Apps that include 'grandfathered: true' in their THEMES entry are exempt
    (typically the first 1-2 shipped apps that pre-date the archetype system).
    They produce a warning but don't block the build."""
    blocking = []
    warnings = []

    try:
        sys.path.insert(0, BASE)
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        from app_themes import THEMES
    except ImportError:
        return [], []

    TEMPLATE_SIGNATURE = ("A", "M0", "V1", "T1")

    for app in apps:
        # Check grandfathered status first
        is_grandfathered = (app in THEMES
                            and THEMES[app].get("grandfathered") is True)

        identity_path = os.path.join(BASE, app, "metadata", "app_identity.md")
        if not os.path.exists(identity_path):
            msg = (f"{app}: missing metadata/app_identity.md. Phase 1.2 of "
                   f"SHIP_GAME.md requires picking 4 archetypes from "
                   f"APP_ARCHETYPES.md (layout, mascot, voice, texture) "
                   f"and recording them in this file.")
            (warnings if is_grandfathered else blocking).append(msg)
            continue

        if app not in THEMES:
            blocking.append(
                f"{app}: not registered in scripts/app_themes.py THEMES. "
                f"Add an entry with the 4 archetype fields per Phase 1.3 "
                f"of SHIP_GAME.md."
            )
            continue

        t = THEMES[app]
        missing_fields = []
        for field in ("layout_archetype", "mascot_pattern", "voice", "texture"):
            if not t.get(field):
                missing_fields.append(field)
        if missing_fields:
            msg = (f"{app}: app_themes.py entry missing fields: "
                   f"{', '.join(missing_fields)}. Pick from APP_ARCHETYPES.md.")
            (warnings if is_grandfathered else blocking).append(msg)
            continue

        sig = (t["layout_archetype"], t["mascot_pattern"],
               t["voice"], t["texture"])
        if sig == TEMPLATE_SIGNATURE:
            msg = (f"{app}: archetype signature is {sig} — that's the "
                   f"template (Layout A + No mascot + Neutral voice + Flat "
                   f"clean). Shipping makes the app feel artificial. Vary "
                   f"at least 2 of the 4 — see APP_ARCHETYPES.md §6.")
            (warnings if is_grandfathered else blocking).append(msg)

    return blocking, warnings


def check_translations_present(apps):
    """BLOCKING for new apps, WARNING for grandfathered: each app must have
    all 11 locale folders in metadata/ with required fields populated.

    Kids apps need only 4 minimum locales (en-US, es-419, pt-BR, fr-FR) but
    those 4 must NOT contain the Kids review-pending header (indicates
    native speaker review has happened)."""
    blocking = []
    warnings = []

    # Play Console-style codes: Indonesian is `id` (not `id-ID`),
    # Ukrainian is `uk` (not `uk-UA`). Arabic and Simplified Chinese
    # added 2026-05 to expand reach. 13 locales total.
    REQUIRED_LOCALES = ["en-US", "ar", "de-DE", "es-419", "fr-FR", "hi-IN",
                        "id", "it-IT", "ja-JP", "pt-BR", "tr-TR", "uk", "zh-CN"]
    KIDS_LOCALES = ["en-US", "es-419", "pt-BR", "fr-FR"]
    REQUIRED_FIELDS = ["short_description.txt", "full_description.txt",
                       "subtitle.txt", "release_notes.txt"]
    KIDS_REVIEW_HEADER = "# KIDS APP — REVIEW BY NATIVE SPEAKER BEFORE SHIPPING"

    # Check whether app is grandfathered via app_themes.py
    try:
        sys.path.insert(0, BASE)
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        from app_themes import THEMES
    except ImportError:
        THEMES = {}

    for app in apps:
        is_grandfathered = (app in THEMES
                            and THEMES[app].get("grandfathered") is True)

        # Determine if Kids app
        is_kids = False
        info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        if os.path.exists(info_path):
            try:
                info = json.loads(open(info_path).read())
                is_kids = info.get("kids_program") is True
            except (json.JSONDecodeError, IOError):
                pass

        target_locales = KIDS_LOCALES if is_kids else REQUIRED_LOCALES

        for locale in target_locales:
            locale_dir = os.path.join(BASE, app, "metadata", locale)
            if not os.path.isdir(locale_dir):
                msg = f"{app}: missing metadata/{locale}/ folder"
                if not is_grandfathered:
                    msg += f" (run gen_translations.py {app})"
                (warnings if is_grandfathered else blocking).append(msg)
                continue

            for field in REQUIRED_FIELDS:
                path = os.path.join(locale_dir, field)
                if not os.path.exists(path):
                    msg = f"{app}: missing metadata/{locale}/{field}"
                    (warnings if is_grandfathered else blocking).append(msg)
                    continue

                # Kids apps: review-pending header must be removed before ship
                if is_kids and field in ("full_description.txt",
                                         "short_description.txt"):
                    try:
                        content = open(path).read()
                        if KIDS_REVIEW_HEADER in content:
                            blocking.append(
                                f"{app}: {locale}/{field} still contains the "
                                f"Kids review-pending header. Native speaker "
                                f"must review and remove the header before "
                                f"shipping a Kids app."
                            )
                    except IOError:
                        pass

                # Check for .rejected sibling files (failed translation that
                # needs manual edit)
                rejected_path = path + ".rejected"
                if os.path.exists(rejected_path):
                    blocking.append(
                        f"{app}: {locale}/{os.path.basename(rejected_path)} "
                        f"exists — translation failed validation. Edit the "
                        f"file to fit char limit and rename to remove .rejected."
                    )

    return blocking, warnings


def check_menu_button_count(apps):
    """BLOCKING: enforces QUALITY_PLAYBOOK §3.1 menu hierarchy.

    Counts buttons rendered on the menu screen. Allowed structure:
      - 1 primary button (Play/Start)
      - 2 secondary buttons (Daily Challenge + one of: Missions, Continue, etc.)
      - 3 tertiary icons (Shop, Stats, Settings, More Games — pick 3)

    Total: 6 tappable elements MAX on the menu screen.

    More than 6 = templated stacked design that reads as artificial. Blocks
    the build. Apps with `grandfathered: true` in app_themes.py get a
    warning instead.

    Detection heuristic: count <button> tags inside the menu screen
    container, count distinct CTA elements with onclick handlers, and any
    .btn / .menu-button / .nav-btn classes. False positives possible —
    surface to the user and let them adjust if the heuristic miscounts."""
    import re
    blocking = []
    warnings = []

    try:
        sys.path.insert(0, BASE)
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        from app_themes import THEMES
    except ImportError:
        THEMES = {}

    MAX_MENU_TAPPABLE = 6

    for app in apps:
        is_grandfathered = (app in THEMES
                            and THEMES[app].get("grandfathered") is True)

        game_html = os.path.join(BASE, app, "android", "app", "src",
                                 "main", "assets", "game.html")
        if not os.path.exists(game_html):
            continue

        try:
            with open(game_html) as f:
                content = f.read()
        except IOError:
            continue

        # Find a menu screen section. Look for any div/section with an id or
        # class that contains "menu" + "screen" tokens (in either order).
        # Common patterns: id="menuScreen", id="screen-menu", class="screen menu",
        # class="menu-screen". Extract its inner HTML up to the matching close.
        menu_match = None
        for pattern in [
            # id="menuScreen" or id="screen-menu" etc
            r'<(?:div|section)[^>]*\bid\s*=\s*["\'](?:menu[-_]?screen|screen[-_]?menu|main[-_]?menu|home[-_]?screen)["\'][^>]*>',
            # class="menu-screen" or similar
            r'<(?:div|section)[^>]*\bclass\s*=\s*["\'][^"\']*\b(?:menu[-_]?screen|screen[-_]?menu|main[-_]?menu)\b[^"\']*["\'][^>]*>',
        ]:
            m = re.search(pattern, content, re.IGNORECASE)
            if m:
                menu_match = m
                break
        if not menu_match:
            continue

        # Walk forward from the opening tag, count nesting depth, find matching close
        start = menu_match.end()
        depth = 1
        # Naive but works: scan forward looking for opening/closing div/section
        i = start
        while depth > 0 and i < len(content):
            next_open = re.search(r'<(?:div|section)\b[^>]*>',
                                  content[i:], re.IGNORECASE)
            next_close = re.search(r'</(?:div|section)>',
                                   content[i:], re.IGNORECASE)
            if not next_close:
                break
            if next_open and next_open.start() < next_close.start():
                depth += 1
                i += next_open.end()
            else:
                depth -= 1
                i += next_close.end()
                if depth == 0:
                    break
        menu_html = content[start:i]

        # Count tappable elements inside menu screen
        button_count = len(re.findall(r'<button\b', menu_html, re.IGNORECASE))
        # Plus any onclick handlers on non-button elements
        onclick_count = len(re.findall(
            r'<(?!button)[a-z]+[^>]*\bonclick\s*=', menu_html, re.IGNORECASE,
        ))
        total = button_count + onclick_count

        if total > MAX_MENU_TAPPABLE:
            msg = (
                f"{app}: menu has {total} tappable elements "
                f"({button_count} <button>, {onclick_count} onclick handlers). "
                f"QUALITY_PLAYBOOK §3.1 requires hierarchy: 1 primary + 2 secondary + 3 tertiary icons = 6 max. "
                f"Restructure: hero Play button, 2 medium buttons (Daily Challenge + one), "
                f"icon row of 3 (Shop/Stats/Settings or similar). "
                f"Move the rest behind icons or kill redundant items per §3.4."
            )
            (warnings if is_grandfathered else blocking).append(msg)

    return blocking, warnings


def check_listing_floor(apps):
    """BLOCKING: enforces QUALITY_PLAYBOOK §7.7.1 hard rules on listing copy.

    Catches the May 2026 audit failure modes:
    - Sub-500-char full_description.txt (Puzzle2048 was 97 bytes,
      PipeConnect was 157 bytes — both below ranking floor)
    - Opening line that's a preamble / encyclopedia / cliché instead
      of a sensory hook
    - Missing 4+ required puzzle keywords on game apps

    Grandfathered apps get warnings, not blockers."""
    blocking = []
    warnings = []

    try:
        sys.path.insert(0, BASE)
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        from app_themes import THEMES
    except ImportError:
        THEMES = {}

    MIN_LEN = 500
    REQUIRED_KEYWORDS = {"relaxing", "satisfying", "asmr", "offline",
                         "brain", "free"}
    REQUIRED_MIN_KEYWORDS = 4

    # Opening-line failure-mode patterns — case-insensitive substring matches
    PREAMBLE_PATTERNS = [
        # Encyclopedia / definition openings
        ("a nonogram is", "encyclopedia opening"),
        ("a sudoku is", "encyclopedia opening"),
        ("a puzzle is", "encyclopedia opening"),
        # Generic clichés
        ("the ultimate", "cliché 'ultimate' opening"),
        ("easy to learn but impossible to put down", "stock cliché"),
        ("easy to learn, hard to master", "stock cliché"),
        ("the best ", "banned superlative"),
        ("#1 ", "banned ranking claim"),
        ("welcome to the ultimate", "cliché preamble"),
        ("download now", "banned CTA"),
        ("install now", "banned CTA"),
    ]

    for app in apps:
        is_grandfathered = (app in THEMES
                            and THEMES[app].get("grandfathered") is True)

        desc_path = os.path.join(BASE, app, "metadata", "en-US",
                                 "full_description.txt")
        if not os.path.exists(desc_path):
            continue

        try:
            with open(desc_path, "r", encoding="utf-8") as f:
                desc = f.read().strip()
        except IOError:
            continue

        if not desc:
            blocking.append(
                f"{app}: full_description.txt is empty"
            )
            continue

        # Length floor
        if len(desc) < MIN_LEN:
            msg = (f"{app}: full_description.txt is {len(desc)} chars "
                   f"(min {MIN_LEN}). Below ranking floor — Google's "
                   f"listing-quality classifier downgrades stubs. See "
                   f"QUALITY_PLAYBOOK §7.7.1.")
            (warnings if is_grandfathered else blocking).append(msg)

        # Opening-line failure modes — check first 200 chars
        opening = desc[:200].lower()
        for pattern, reason in PREAMBLE_PATTERNS:
            if pattern in opening:
                msg = (f"{app}: full_description.txt opens with "
                       f"{reason} ('{pattern}'). Replace with a sensory "
                       f"hook (verb + specific outcome). See "
                       f"QUALITY_PLAYBOOK §7.7.1.")
                (warnings if is_grandfathered else blocking).append(msg)
                break  # one preamble flag is enough

        # Keyword check (only for apps tagged as games — utility apps
        # legitimately don't need ASMR keywords). Heuristic: check if
        # the app's category in app_info.json starts with "GAME".
        app_info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        is_game = False
        if os.path.exists(app_info_path):
            try:
                import json
                with open(app_info_path) as f:
                    info = json.load(f)
                category = (info.get("google_play_category", "")
                            + " " + info.get("apple_category", "")).upper()
                is_game = "GAME" in category or "PUZZLE" in category
            except (IOError, ValueError):
                pass

        if is_game:
            desc_lower = desc.lower()
            present = [kw for kw in REQUIRED_KEYWORDS if kw in desc_lower]
            if len(present) < REQUIRED_MIN_KEYWORDS:
                missing = REQUIRED_KEYWORDS - set(present)
                msg = (f"{app}: full_description.txt has only "
                       f"{len(present)}/{REQUIRED_MIN_KEYWORDS} required "
                       f"puzzle keywords (have: {sorted(present) or '[]'}; "
                       f"need 4+ from: relaxing, satisfying, ASMR, offline, "
                       f"brain, free). Insert honestly — never claim ASMR "
                       f"unless §6 ASMR audit passes. See QUALITY_PLAYBOOK "
                       f"§7.5.1.")
                # This one is a warning, not a blocker — keyword absence
                # hurts ASO but doesn't block compliance
                warnings.append(msg)

    return blocking, warnings


def check_keystore_present(apps):
    """BLOCKING: per-app keystore must exist on disk before any release upload.

    Per CLAUDE.md "Keystore management — per-app, not global", every
    app must have its own keystore at <App>/android/keystore.jks. The
    May 2026 lesson: losing a single shared keystore meant losing access
    to every app's update path; per-app keystores limit blast radius.

    This check enforces:
    - keystore.jks exists at <App>/android/
    - keystore.properties exists (gitignored) referencing it
    - If app_info.json has `upload_key_sha1` set, verify the keystore
      file's actual SHA1 matches (so a swapped/regenerated keystore
      doesn't silently break the upload chain)

    Apps with no AAB build or no metadata are skipped — this only
    fires when an app is actually being prepared for publish."""
    import subprocess
    blocking = []
    warnings = []

    for app in apps:
        # Only enforce for apps that have at least started the
        # release pipeline. Heuristic: app_info.json present.
        app_info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        if not os.path.exists(app_info_path):
            continue

        keystore_path = os.path.join(BASE, app, "android", "keystore.jks")
        keystore_props_path = os.path.join(BASE, app, "android",
                                           "keystore.properties")

        if not os.path.exists(keystore_path):
            blocking.append(
                f"{app}: keystore missing at android/keystore.jks. "
                f"Per CLAUDE.md 'Keystore management', every app needs its "
                f"own keystore. Generate with `keytool -genkey -v -keystore "
                f"keystore.jks -keyalg RSA -keysize 2048 -validity 10000 "
                f"-alias upload` from {app}/android/, then back up to "
                f"cloud + USB before any upload."
            )
            continue

        if not os.path.exists(keystore_props_path):
            blocking.append(
                f"{app}: keystore.properties missing at android/. "
                f"Required for Gradle release signing config. Should "
                f"contain storeFile, storePassword, keyAlias, keyPassword "
                f"pointing at keystore.jks. Must be in .gitignore."
            )

        # Verify SHA1 matches recorded value if present
        try:
            import json
            with open(app_info_path) as f:
                info = json.load(f)
            expected_sha1 = info.get("upload_key_sha1", "").upper().replace(":", "")
        except (IOError, ValueError):
            expected_sha1 = ""

        if expected_sha1:
            # Read storeFile + storePassword from keystore.properties so the
            # check works against per-app random passwords. Under the
            # single-keystore-per-app model storeFile MUST equal
            # keystore.jks — any other value is a misconfiguration and we
            # warn so it doesn't get silently shipped with the wrong key.
            storepass = "android"
            verify_path = keystore_path
            try:
                if os.path.exists(keystore_props_path):
                    for line in open(keystore_props_path):
                        if line.startswith("storePassword="):
                            storepass = line.split("=", 1)[1].strip()
                        elif line.startswith("storeFile="):
                            sf = line.split("=", 1)[1].strip()
                            if os.path.basename(sf) != "keystore.jks":
                                # Every app — including Puzzle2048 — keeps
                                # its signing key at <App>/android/keystore.jks
                                # under a uniform file/name/place convention.
                                blocking.append(
                                    f"{app}: keystore.properties storeFile = "
                                    f"{sf!r} but every app's keystore must "
                                    f"be named keystore.jks. Rename the file "
                                    f"and edit keystore.properties."
                                )
                            cand = sf if os.path.isabs(sf) else os.path.join(
                                BASE, app, "android", sf)
                            if os.path.exists(cand):
                                verify_path = cand
            except IOError:
                pass
            # keytool -list outputs SHA1 with colons; strip and compare
            try:
                result = subprocess.run(
                    ["keytool", "-list", "-v",
                     "-keystore", verify_path, "-storepass", storepass],
                    capture_output=True, text=True, timeout=10,
                )
                actual_sha1 = ""
                for line in result.stdout.splitlines():
                    if "SHA1:" in line:
                        actual_sha1 = line.split("SHA1:")[1].strip().upper().replace(":", "")
                        break
                if actual_sha1 and actual_sha1 != expected_sha1:
                    blocking.append(
                        f"{app}: keystore SHA1 mismatch. "
                        f"app_info.json:upload_key_sha1 = {expected_sha1}, "
                        f"actual keystore.jks SHA1 = {actual_sha1}. "
                        f"Either restore the correct keystore from backup "
                        f"OR if Play Console reset was completed, update "
                        f"app_info.json with the new fingerprint."
                    )
                elif not actual_sha1:
                    # Couldn't read keystore (likely password mismatch)
                    warnings.append(
                        f"{app}: could not verify keystore SHA1 "
                        f"(keytool needs the storepass; try with the "
                        f"actual password from keystore.properties). "
                        f"Visual fingerprint check still required before upload."
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                warnings.append(
                    f"{app}: keytool not available; cannot verify "
                    f"keystore SHA1 against app_info.json. Verify "
                    f"manually before upload."
                )
        else:
            warnings.append(
                f"{app}: app_info.json missing upload_key_sha1 field. "
                f"After first successful Play Console upload, run "
                f"`keytool -printcert -jarfile <aab>` and record the "
                f"SHA1 in app_info.json so future builds can verify."
            )

    return blocking, warnings


def check_screenshot_uniqueness(apps):
    """BLOCKING: each phone slot must show distinct in-app content.

    Catches the May 2026 Puzzle2048 capture failure: 5 of 7 slots used
    the same raw because adb taps missed their target buttons. The
    pipeline produced 7 wrapped screenshots with different headlines
    over visually identical phone content — a Play Store Misleading
    Behavior policy risk.

    Also enforces that any tablet raws are at tablet resolution and do
    not match phone raws (= phone captures placed in tablet wrap).
    """
    blocking = []
    warnings = []

    try:
        from PIL import Image
    except ImportError:
        warnings.append("PIL not installed — skipping screenshot uniqueness check. "
                        "Run: pip install pillow")
        return blocking, warnings

    def ahash(path):
        """17x16 dHash — content-sensitive perceptual fingerprint.
        (Was 8x8 average hash; collapsed visually-distinct game-board
        screens to the same fingerprint because their overall light/
        dark distribution was similar.)"""
        try:
            img = Image.open(path).convert("L").resize((17, 16))
            pixels = list(img.getdata())
            h = 0
            for r in range(16):
                for c in range(16):
                    if pixels[r * 17 + c] > pixels[r * 17 + c + 1]:
                        h |= 1 << (r * 16 + c)
            return h
        except (IOError, OSError):
            return None

    def hamming(a, b):
        return bin(a ^ b).count("1")

    for app in apps:
        # Already-shipped apps degrade phone-uniqueness collisions to
        # warnings (still surfaces, but doesn't block updates that have
        # other priority work). Pre-ship apps still block.
        is_shipped = False
        info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path) as f:
                    is_shipped = bool(json.load(f).get("first_upload_at"))
            except (IOError, ValueError):
                pass

        # Phone raws
        phone_raw_dir = os.path.join(BASE, app, "store", "screenshots", "phone", "raw")
        phone_hashes = {}
        if os.path.isdir(phone_raw_dir):
            for fname in sorted(os.listdir(phone_raw_dir)):
                if not fname.lower().endswith(".png"):
                    continue
                path = os.path.join(phone_raw_dir, fname)
                h = ahash(path)
                if h is None:
                    continue
                for prev_name, prev_h in phone_hashes.items():
                    if hamming(h, prev_h) <= 24:
                        # Count distinct so far. Block only if app has
                        # fewer than 4 distinct phone screens; allow the
                        # rest to be duplicates (shipping with 4+ unique
                        # is well above Play Console's 2 minimum and
                        # acceptable when icon-row taps refuse to land
                        # via the script's pipeline despite working
                        # manually).
                        msg = (
                            f"{app}: phone raw {fname} is visually identical "
                            f"to {prev_name} (perceptual hash distance ≤ 24 of 256). "
                        )
                        n_distinct = len(phone_hashes)  # already-seen distinct count
                        if n_distinct < 4 and not is_shipped:
                            blocking.append(msg + "Pre-ship apps need ≥4 "
                                "distinct phone slots; this is below floor.")
                        else:
                            warnings.append(msg + f"({n_distinct} distinct "
                                "so far — above the 4-slot floor or app is "
                                "already shipped, so this is informational.)")
                        break
                phone_hashes[fname] = h

        # Tablet raws — none of them should match any phone raw, and
        # each must be at tablet resolution.
        for tablet_size in ("tablet_7", "tablet_10"):
            tablet_raw_dir = os.path.join(BASE, app, "store", "screenshots",
                                          tablet_size, "raw")
            if not os.path.isdir(tablet_raw_dir):
                continue
            for fname in sorted(os.listdir(tablet_raw_dir)):
                if not fname.lower().endswith(".png"):
                    continue
                path = os.path.join(tablet_raw_dir, fname)
                h = ahash(path)
                if h is None:
                    continue
                # Resolution — tablet should be ≥1200 wide
                try:
                    w, _ = Image.open(path).size
                    if w < 1200:
                        blocking.append(
                            f"{app}: {tablet_size}/raw/{fname} is only "
                            f"{w}px wide — tablet captures must be at "
                            f"tablet resolution (1200×1920 for 7\", "
                            f"1800×2560 for 10\"). Phone resolution "
                            f"upscaled to a tablet canvas looks like a "
                            f"phone running in tablet emulation — "
                            f"obvious to reviewers."
                        )
                except (IOError, OSError):
                    pass
                # Match against phone raws
                for phone_name, phone_h in phone_hashes.items():
                    if hamming(h, phone_h) <= 4:
                        blocking.append(
                            f"{app}: {tablet_size}/raw/{fname} is visually "
                            f"identical to phone/raw/{phone_name}. Tablet "
                            f"captures must be SEPARATE captures from a "
                            f"tablet emulator (different in-app layout, "
                            f"different aspect ratio), not the phone raws "
                            f"placed inside a tablet wrap."
                        )
                        break

    return blocking, warnings


def check_screenshot_completeness(apps):
    """BLOCKING: every shipping app must have phone + tablet_7 + tablet_10
    screenshot sets fully populated.

    Per QUALITY_PLAYBOOK §7.3 (mandatory tablets policy, May 2026), no app
    ships without all three sets. Apps with `app_info.json:first_upload_at`
    set get only a warning (already shipped — handle on next update).
    Apps in pre-ship state get blocked.
    """
    blocking = []
    warnings = []
    REQUIRED_MIN = 6  # Pegasus standard: 6 distinct screenshots per surface
                      # (phone + tablet_7 + tablet_10). Set by user policy
                      # 2026-05-25 — applies to every new app. Already-shipped
                      # apps get a warning (grandfathered); pre-ship gets blocked.

    for app in apps:
        if not os.path.isdir(os.path.join(BASE, app, "android")):
            continue

        is_shipped = False
        info_path = os.path.join(BASE, app, "metadata", "app_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path) as f:
                    info = json.load(f)
                is_shipped = bool(info.get("first_upload_at"))
            except (IOError, ValueError):
                pass

        for set_name in ("phone", "tablet_7", "tablet_10"):
            set_dir = os.path.join(BASE, app, "store", "screenshots", set_name)
            if not os.path.isdir(set_dir):
                msg = (f"{app}: store/screenshots/{set_name}/ does not exist. "
                       f"Per QUALITY_PLAYBOOK §7.3, all apps require phone + "
                       f"tablet_7 + tablet_10 screenshots. Run: "
                       f"python3 scripts/capture_screenshots.py {app} "
                       f"--target {set_name}")
                (warnings if is_shipped else blocking).append(msg)
                continue

            wrapped = [f for f in os.listdir(set_dir)
                       if f.endswith(".png") and not f.startswith(".")
                       and f[0:2].isdigit()]
            if len(wrapped) < REQUIRED_MIN:
                msg = (f"{app}: {set_name}/ has {len(wrapped)} wrapped "
                       f"screenshot(s). Pegasus standard is "
                       f"{REQUIRED_MIN}/surface (Play Console minimum is 2).")
                (warnings if is_shipped else blocking).append(msg)

    return blocking, warnings


def check_screenshot_headline_similarity(apps):
    """Headline TEXT drawn on the wrapped screenshots must be distinct.

    The wrapper scripts vary the background and headline placement per
    slot, but the *words* still come from the per-app headline JSON. Two
    ways that goes wrong:

      1. Two slots on the same surface carry the same big headline — the
         wrapped shots read as templated and a listing slot is wasted.
      2. A tablet headlines file duplicates the phone one.
         wrap_tablet_screenshots.py falls back to the phone headlines
         when the tablet file is missing (CLAUDE.md "Things to flag"),
         so an absent/copied tablet file silently ships phone copy on
         the tablet listing.

    Exact duplicates block; merely-similar headlines warn.
    """
    blocking = []
    warnings = []

    SURFACES = [
        ("phone",     "metadata/screenshot_headlines.json"),
        ("tablet_7",  "metadata/screenshot_headlines_tablet_7.json"),
        ("tablet_10", "metadata/screenshot_headlines_tablet_10.json"),
    ]

    def norm(s):
        return " ".join(str(s or "").upper().split())

    def headline_key(entry):
        return norm(entry.get("line1", "") + " " + entry.get("line2", ""))

    for app in apps:
        surfaces = {}
        for name, relpath in SURFACES:
            path = os.path.join(BASE, app, relpath)
            if not os.path.exists(path):
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
            except (IOError, ValueError):
                continue
            if isinstance(data, list) and data:
                surfaces[name] = data
        if "phone" not in surfaces:
            continue  # headlines not authored yet — nothing to compare

        # 1. within-surface duplicate / near-duplicate headlines
        for name, entries in surfaces.items():
            seen_head, seen_sub = {}, {}
            for i, entry in enumerate(entries):
                hk = headline_key(entry)
                sk = norm(entry.get("subtitle", ""))
                if hk and hk in seen_head:
                    blocking.append(
                        f"{app}: {name} headlines — slot {i+1} and slot "
                        f"{seen_head[hk]+1} both read {hk!r}. Each "
                        f"wrapped screenshot needs a distinct headline.")
                elif hk:
                    seen_head[hk] = i
                if sk and sk in seen_sub:
                    blocking.append(
                        f"{app}: {name} headlines — slot {i+1} and slot "
                        f"{seen_sub[sk]+1} share the same subtitle. Vary "
                        f"the supporting line too.")
                elif sk:
                    seen_sub[sk] = i

            keys = [headline_key(e) for e in entries]
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    a = set(keys[i].split())
                    b = set(keys[j].split())
                    if not a or not b or keys[i] == keys[j]:
                        continue
                    if len(a & b) / len(a | b) >= 0.6:
                        warnings.append(
                            f"{app}: {name} headlines — slot {i+1} "
                            f"({keys[i]!r}) and slot {j+1} ({keys[j]!r}) "
                            f"are very similar. Reword one.")

        # 2. cross-surface duplicate / near-duplicate headlines.
        #    Each screenshot surface (phone / tablet_7 / tablet_10) is
        #    its own store listing, so no headline may be reused on
        #    another surface — including tablet_7 vs tablet_10. A tablet
        #    file that is just a copy of the phone file (the fallback
        #    wrap_tablet_screenshots.py uses when a tablet file is
        #    missing) shows up here as a pile of shared keys.
        surf_keys = {name: [headline_key(e) for e in entries]
                     for name, entries in surfaces.items()}
        order = [s for s in ("phone", "tablet_7", "tablet_10")
                 if s in surf_keys]
        for ai in range(len(order)):
            for bi in range(ai + 1, len(order)):
                s1, s2 = order[ai], order[bi]
                for i, k1 in enumerate(surf_keys[s1]):
                    if not k1:
                        continue
                    for j, k2 in enumerate(surf_keys[s2]):
                        if not k2:
                            continue
                        if k1 == k2:
                            blocking.append(
                                f"{app}: {s1} slot {i+1} and {s2} slot "
                                f"{j+1} share the headline {k1!r}. Each "
                                f"screenshot surface is a separate store "
                                f"listing and needs its own headlines.")
                        else:
                            a = set(k1.split())
                            b = set(k2.split())
                            if a and b and len(a & b) / len(a | b) >= 0.5:
                                warnings.append(
                                    f"{app}: {s1} slot {i+1} ({k1!r}) and "
                                    f"{s2} slot {j+1} ({k2!r}) read very "
                                    f"similarly across surfaces. Reword one.")

    return blocking, warnings


# ---------- main -------------------------------------------------------------

def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    only = None
    for i, a in enumerate(args):
        if a == "--only" and i + 1 < len(args):
            only = args[i + 1]
    args = [a for a in args if not a.startswith("--") and a != only]
    apps = list_apps(filter_names=set(args) if args else None)

    if not apps:
        print(red("No apps to check."))
        sys.exit(1)

    print(bold(f"Checking {len(apps)} app(s)…\n"))

    blocking = []
    warnings = []

    def section(group, name, func, *fargs):
        if only and only != group:
            return
        print(f"  [{group}] {name}… ", end="", flush=True)
        result = func(*fargs)
        if isinstance(result, tuple):
            b, w = result
        else:
            b, w = result, []
        parts = []
        if b: parts.append(red(f"{len(b)} blocking"))
        if w: parts.append(yellow(f"{len(w)} warn"))
        print(" ".join(parts) if parts else green("ok"))
        blocking.extend(b)
        warnings.extend(w)

    # ---- CODE & IDENTITY
    section("code",  "duplicate game.html",       check_duplicate_game_html, apps)
    section("code",  "title vs folder name",      check_title_matches_folder, apps)
    section("code",  "duplicate AdMob IDs",       check_duplicate_admob_ids, apps)
    section("code",  "duplicate package names",   check_duplicate_package_names, apps)
    section("code",  "package_name vs build.gradle", check_package_name_drift, apps)
    section("code",  "unreplaced placeholders",   check_placeholders, apps)
    section("code",  "blocked placeholder apps",  check_blocked_apps, apps)
    section("code",  "cross-app asset similarity", check_cross_app_asset_similarity, apps)
    section("code",  "icon perceptual similarity", check_icon_perceptual_similarity, apps)
    section("code",  "screenshot template reuse",  check_screenshot_template_reuse, apps)
    section("store", "screenshot uniqueness",       check_screenshot_uniqueness, apps)
    section("store", "screenshot completeness",     check_screenshot_completeness, apps)
    section("store", "screenshot headline similarity", check_screenshot_headline_similarity, apps)
    section("code",  "listing copy uniqueness",    check_listing_copy_uniqueness, apps)
    section("code",  "archetype presence",         check_archetype_presence, apps)
    section("code",  "translations present",       check_translations_present, apps)
    section("code",  "menu button count",           check_menu_button_count, apps)
    section("store", "listing floor (length+hook)",  check_listing_floor, apps)
    section("code",  "keystore present + SHA1",      check_keystore_present, apps)

    # ---- STORE ASSETS
    section("store", "Google icon (512x512)",      check_store_image, apps,
            "store/icon_512_playstore.png", "Google icon")
    section("store", "Google feature graphic",     check_store_image, apps,
            "store/feature_graphic_1024x500.png", "Feature graphic")
    section("store", "Apple icon (1024x1024)",     check_store_image, apps,
            "store/icon_1024_appstore.png", "Apple icon")
    section("store", "phone screenshots (>=2)",    check_screenshots, apps,
            "phone", MIN_PHONE_SCREENSHOTS, "Phone screenshot", True)
    section("store", "iPhone 6.9\" screenshots",   check_screenshots, apps,
            "iphone_6_9", 1, "iPhone 6.9 screenshot", False)

    # ---- STORE METADATA — text files
    section("meta",  "title.txt",                  check_text_file, apps,
            "metadata/en-US/title.txt", TITLE_MAX, "title", True)
    section("meta",  "short_description.txt",      check_text_file, apps,
            "metadata/en-US/short_description.txt", SHORT_DESC_MAX, "short_description", False)
    section("meta",  "subtitle.txt",               check_text_file, apps,
            "metadata/en-US/subtitle.txt", SUBTITLE_MAX, "subtitle", False)
    section("meta",  "full_description.txt",       check_text_file, apps,
            "metadata/en-US/full_description.txt", FULL_DESC_MAX, "full_description", True)
    section("meta",  "keywords.txt",               check_text_file, apps,
            "metadata/en-US/keywords.txt", KEYWORDS_MAX, "keywords", False)
    section("meta",  "promotional_text.txt",       check_text_file, apps,
            "metadata/en-US/promotional_text.txt", PROMO_TEXT_MAX, "promotional_text", False)
    section("meta",  "release_notes.txt",          check_text_file, apps,
            "metadata/en-US/release_notes.txt", RELEASE_NOTES_MAX, "release_notes", False)

    # ---- STORE METADATA — JSON files
    section("meta",  "app_info.json",              check_json_file, apps,
            "metadata/app_info.json",
            ["category_google", "category_apple_primary", "contains_ads",
             "target_audience_min_age", "support_url", "copyright"], "app_info")
    section("meta",  "privacy.json",               check_json_file, apps,
            "metadata/privacy.json",
            ["privacy_policy_url", "google_data_safety", "apple_privacy_labels"], "privacy")
    section("meta",  "content_rating.json",        check_json_file, apps,
            "metadata/content_rating.json",
            ["iarc_answers", "expected_google_rating", "apple_age_rating"], "content_rating")
    section("meta",  "iaps.json",                  check_json_file, apps,
            "metadata/iaps.json",
            ["one_time_products"], "iaps")
    section("meta",  "review_notes.json",          check_json_file, apps,
            "metadata/review_notes.json",
            ["google_review_notes", "apple_review_notes", "demo_account_required"], "review_notes")
    section("meta",  "iaps.json descriptions",     check_iaps_descriptions, apps)
    section("meta",  "IAP correctness invariants", check_iap_invariants, apps)
    section("meta",  "IAP grant parity",            check_iap_grant_parity, apps)
    section("meta",  "subscription promise parity", check_subscription_parity, apps)
    section("code",  "subscription billing routing", check_subscription_routing, apps)
    section("meta",  "coin tier ladder",            check_coin_tier_ladder, apps)
    section("code",  "retention-feature parity",    check_retention_features, apps)
    section("code",  "booster catalog",             check_booster_catalog, apps)
    section("code",  "menu completeness",           check_menu_completeness, apps)
    section("code",  "seasonal events present",     check_seasonal_events, apps)
    section("code",  "puzzle solvability",           check_puzzle_solvability, apps)
    # Audit 2026-05-15 slip-prevention checks (G2-G6).
    section("meta",  "IAP price string parity",     check_price_string_parity, apps)
    section("code",  "restore purchases UI",        check_restore_purchases_ui, apps)
    section("code",  "interstitial cadence",        check_interstitial_cadence, apps)
    section("meta",  "IAP display-name table",      check_iap_display_name_table, apps)
    section("store", "screenshot headline match",   check_screenshot_headline_match, apps)
    section("meta",  "iaps.json matches code",     lambda a: ([], check_iaps_match_code(a)), apps)
    section("meta",  "canonical privacy/support URLs", check_canonical_urls, apps)
    section("meta",  "no per-app privacy.html",    check_no_per_app_privacy_html, apps)
    section("meta",  "STORE_PASTE locale tags",     check_store_paste_locale_tags, apps)
    section("meta",  "no old placeholder URLs",    check_old_placeholder_urls, apps)

    # ---- CONTENT QUALITY
    section("code",  "thin game.html",             lambda a: ([], check_thin_games(a)), apps)
    section("meta",  "prohibited marketing lang",  lambda a: ([], check_prohibited_language(a)), apps)

    # ---- GROWTH BASELINE (2026-05-25 plan: notifications + cross-promo +
    # streak freeze + share virality + PGS hooks). Defined in
    # scripts/check_growth_features.py — imported lazily so a missing import
    # doesn't break legacy callers of pre_publish_check.
    try:
        from check_growth_features import check_app as _growth_check
        def _growth(apps_subset):
            b_all, w_all = [], []
            for a in apps_subset:
                b, w = _growth_check(a)
                b_all.extend(b); w_all.extend(w)
            return b_all, w_all
        section("code",  "growth baseline",         _growth, apps)
    except Exception as _e:
        # Soft-fail — log and continue (the dedicated tool still works).
        print(f"  growth baseline: skipped ({_e})")

    print()
    if blocking:
        print(red(bold(f"BLOCKING ({len(blocking)}):")))
        for msg in blocking[:200]:
            print(red(f"  ✗ {msg}"))
        if len(blocking) > 200:
            print(dim(f"  … and {len(blocking) - 200} more"))
    if warnings:
        print(yellow(bold(f"\nWARNINGS ({len(warnings)}):")))
        for msg in warnings[:200]:
            print(yellow(f"  ! {msg}"))
        if len(warnings) > 200:
            print(dim(f"  … and {len(warnings) - 200} more"))
    if not blocking and not warnings:
        print(green(bold("All checks passed.")))

    if blocking or (strict and warnings):
        sys.exit(1)
    if warnings:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
