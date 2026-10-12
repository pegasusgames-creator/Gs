#!/usr/bin/env python3
"""set_app_ids.py — paste an app's console IDs in one command.

Every new or migrated app ships with values the release gates catch:
Google TEST AdMob IDs, a PASTE_LICENSE_PUBLIC_KEY billing key and a
TODO leaderboard. This writes the real ones everywhere they live, after
validating them:

  --admob-app     ca-app-pub-<16 digits>~<10 digits>   AndroidManifest.xml
  --banner / --interstitial / --rewarded
                  ca-app-pub-<16 digits>/<10 digits>   MainActivity.java
                  (ADMOB_*_UNIT_ID in family apps, *_AD_UNIT_ID in the long tail)
  --license       base64 RSA key from Play Console -> Monetize with Play ->
                  Monetization setup -> Licensing        MainActivity.java
  --leaderboard   CgkI... from Play Console -> Play Games Services ->
                  Leaderboards                          wire_leaderboards.py + game.html
  --games-app-id  digits (only if this app uses its own Play Games project)
                                                        res/values/strings.xml

Refuses Google's test publisher, mixed publisher IDs, malformed values and
any AdMob ID already used by another app (Red Line 4). Pass only the flags
you have; the rest are left alone. --dry-run prints the edits.

Example:
  python3 scripts/set_app_ids.py Sudoku --admob-app ca-app-pub-1234567890123456~1234567890 \\
      --banner ca-app-pub-1234567890123456/1111111111 --interstitial ca-app-pub-1234567890123456/2222222222 \\
      --rewarded ca-app-pub-1234567890123456/3333333333 --license MIIBIjANBgkq... --leaderboard CgkIg4KVn8kGEAIQDA
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEST_PUB = "3940256099942544"
APP_RE = re.compile(r"^ca-app-pub-(\d{16})~(\d{10})$")
UNIT_RE = re.compile(r"^ca-app-pub-(\d{16})/(\d{10})$")
UNIT_NAMES = {"banner": ("ADMOB_BANNER_UNIT_ID", "BANNER_AD_UNIT_ID"),
              "interstitial": ("ADMOB_INTERSTITIAL_UNIT_ID", "INTERSTITIAL_AD_UNIT_ID"),
              "rewarded": ("ADMOB_REWARDED_UNIT_ID", "REWARDED_AD_UNIT_ID")}


def fail(msg: str) -> None:
    print(f"  ✗ {msg}")
    sys.exit(1)


def used_elsewhere(app: str, value: str) -> list:
    hits = []
    for p in BASE.glob("*/android/app/src/main/**/*"):
        if p.is_file() and p.suffix in (".java", ".xml") and not p.is_relative_to(BASE / app):
            try:
                if value in p.read_text(encoding="utf-8", errors="replace"):
                    hits.append(p.relative_to(BASE).parts[0])
            except OSError:
                pass
    return sorted(set(hits))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("app")
    for k in ("admob-app", "banner", "interstitial", "rewarded", "license", "leaderboard", "games-app-id"):
        ap.add_argument("--" + k)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = BASE / a.app / "android/app/src/main"
    manifest = root / "AndroidManifest.xml"
    java = next(iter(root.glob("java/**/MainActivity.java")), None)
    if not manifest.exists() or java is None:
        fail(f"{a.app}: no AndroidManifest.xml / MainActivity.java")

    pubs = set()
    if a.admob_app:
        m = APP_RE.match(a.admob_app) or fail(f"--admob-app must look like ca-app-pub-<16 digits>~<10 digits>")
        pubs.add(m.group(1))
    units = {}
    for k in UNIT_NAMES:
        v = getattr(a, k)
        if v:
            m = UNIT_RE.match(v) or fail(f"--{k} must look like ca-app-pub-<16 digits>/<10 digits>")
            pubs.add(m.group(1))
            units[k] = v
    if TEST_PUB in pubs:
        fail("those are Google's TEST ad IDs — use the IDs from your own AdMob account")
    if len(pubs) > 1:
        fail(f"AdMob IDs come from different publisher accounts: {sorted(pubs)}")
    if len(set(units.values())) != len(units):
        fail("banner / interstitial / rewarded must be three different ad units")
    for v in [x for x in [a.admob_app, *units.values()] if x]:
        others = used_elsewhere(a.app, v)
        if others:
            fail(f"{v} is already used by {', '.join(others)} (Red Line 4: never reuse AdMob IDs)")
    if a.license and not re.fullmatch(r"MIIB[A-Za-z0-9+/=]{200,}", a.license):
        fail("--license should be the base64 RSA public key starting with MIIB (Play Console -> Monetization setup)")
    if a.leaderboard and not re.fullmatch(r"Cgk[A-Za-z0-9_-]{8,}", a.leaderboard):
        fail("--leaderboard should look like CgkI... (Play Console -> Play Games Services -> Leaderboards)")
    if a.games_app_id and not re.fullmatch(r"\d{6,20}", a.games_app_id):
        fail("--games-app-id must be digits only")

    edits = {}
    ms = manifest.read_text(encoding="utf-8")
    if a.admob_app:
        ms, n = re.subn(r'(android:name="com\.google\.android\.gms\.ads\.APPLICATION_ID"\s+android:value=")[^"]*(")',
                        r"\g<1>%s\g<2>" % a.admob_app, ms)
        n or fail("AndroidManifest.xml has no com.google.android.gms.ads.APPLICATION_ID meta-data")
        edits[manifest] = ms
    js = java.read_text(encoding="utf-8")
    for k, v in units.items():
        hit = 0
        for name in UNIT_NAMES[k]:
            js, n = re.subn(r'(String\s+%s\s*=\s*")[^"]*(")' % name, r"\g<1>%s\g<2>" % v, js)
            hit += n
        hit or fail(f"MainActivity.java has no {' / '.join(UNIT_NAMES[k])} constant")
    if a.license:
        js, n = re.subn(r'(LICENSE_PUBLIC_KEY\s*=\s*")[^"]*(")', r"\g<1>%s\g<2>" % a.license, js)
        n or fail("MainActivity.java has no LICENSE_PUBLIC_KEY (long-tail wrapper — migrate it to the family wrapper first)")
    if units or a.license:
        edits[java] = js
    if a.games_app_id:
        sx = root / "res/values/strings.xml"
        s = sx.read_text(encoding="utf-8")
        s, n = re.subn(r'(<string name="games_app_id"[^>]*>)[^<]*(</string>)', r"\g<1>%s\g<2>" % a.games_app_id, s)
        n or fail("strings.xml has no games_app_id")
        edits[sx] = s
    if a.leaderboard:
        wl = BASE / "scripts/wire_leaderboards.py"
        s = wl.read_text(encoding="utf-8")
        line = f"    '{a.app}':".ljust(22) + f"'{a.leaderboard}',"
        if re.search(r"^\s*'%s':\s*'[^']*',\s*$" % re.escape(a.app), s, re.M):
            s = re.sub(r"^\s*'%s':\s*'[^']*',\s*$" % re.escape(a.app), line, s, flags=re.M)
        else:
            s = s.replace("\n}\nLINE_RE", f"\n{line}\n}}\nLINE_RE", 1)
        edits[wl] = s

    if not edits:
        fail("nothing to set — pass at least one ID flag")
    for p in edits:
        print(f"  {'would update' if a.dry_run else 'update'} {p.relative_to(BASE)}")
    if a.dry_run:
        return 0
    for p, s in edits.items():
        p.write_text(s, encoding="utf-8")
    if a.leaderboard:
        subprocess.run([sys.executable, str(BASE / "scripts/wire_leaderboards.py")], check=False)
    print(f"  ✓ {a.app}: IDs set — now rebuild (./gradlew :app:bundleRelease) and run pre_publish_check.py {a.app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
