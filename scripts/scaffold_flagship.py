#!/usr/bin/env python3
"""scaffold_flagship.py — move an existing app onto the flagship shell.

Copies the AdMob-family Android wrapper (MainActivity / Notification* Java,
manifest, gradle, res/values, res/xml) and the full game.html shell (menus,
shop, IAP, lives, settings, overlays + every growth shim) from a finished
SOURCE app into TARGET, keeping TARGET's own identity:

  * applicationId / Java package (never changes once a listing exists)
  * versionCode (bumped by one) and a new versionName
  * mipmap / drawable launcher icons (regenerate from store/ later)

and resetting every per-app console ID to a value the release gates catch
until the owner pastes the real one with scripts/set_app_ids.py:

  * AdMob app ID + banner / interstitial / rewarded units -> Google test IDs
  * Play billing LICENSE_PUBLIC_KEY                        -> PASTE_LICENSE_PUBLIC_KEY
  * Play Games leaderboard ID (game.html)                   -> TODO_LEADERBOARD_ID

The Play Games APP_ID is the portfolio-wide project (games_app_id) and is
kept. Firebase is made OPTIONAL in the copy: the google-services plugin is
applied only when app/google-services.json exists, and FirebaseAnalytics is
created inside try/catch, so the app builds and runs without that file.

After this, the game core inside game.html (level data, board, input, win)
still belongs to SOURCE and must be replaced — this script only lays the
shell. metadata/iaps.json is replaced with SOURCE's catalog only when it is
a superset of TARGET's (never drop a SKU — restore must keep working).

Usage:
    python3 scripts/scaffold_flagship.py TARGET --name "Display Name" \\
        --version-name 2.0.0 [--from Afterimage] [--reminder "..."] [--dry-run]
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

TEST_APP_ID = "ca-app-pub-3940256099942544~3347511713"
TEST_UNITS = {
    "ADMOB_BANNER_UNIT_ID": "ca-app-pub-3940256099942544/6300978111",
    "ADMOB_INTERSTITIAL_UNIT_ID": "ca-app-pub-3940256099942544/1033173712",
    "ADMOB_REWARDED_UNIT_ID": "ca-app-pub-3940256099942544/5224354917",
}
# Wrapper files copied verbatim (then rewritten) from SOURCE/android.
WRAPPER_FILES = [
    "build.gradle", "settings.gradle", "gradle.properties",
    "gradle/wrapper/gradle-wrapper.jar", "gradle/wrapper/gradle-wrapper.properties",
    "gradlew", "gradlew.bat",
    "app/build.gradle", "app/proguard-rules.pro",
    "app/src/main/AndroidManifest.xml",
    "app/src/main/res/values/ids.xml", "app/src/main/res/values/strings.xml",
    "app/src/main/res/values/styles.xml", "app/src/main/res/xml/gma_ad_services_config.xml",
]


def pkg_of(app: str) -> str:
    g = (BASE / app / "android/app/build.gradle").read_text(encoding="utf-8")
    m = re.search(r'applicationId\s+["\']([^"\']+)["\']', g)
    if not m:
        raise SystemExit(f"{app}: no applicationId in app/build.gradle")
    return m.group(1)


def version_code_of(app: str) -> int:
    g = (BASE / app / "android/app/build.gradle").read_text(encoding="utf-8")
    m = re.search(r"versionCode\s+(\d+)", g)
    return int(m.group(1)) if m else 0


def java_dir(app: str, pkg: str) -> Path:
    return BASE / app / "android/app/src/main/java" / Path(*pkg.split("."))


def rewrite_java(src: str, src_pkg: str, pkg: str, reminder: str) -> str:
    s = src.replace(src_pkg, pkg)
    for k, v in TEST_UNITS.items():
        s = re.sub(r'(%s\s*=\s*")[^"]*(")' % k, r"\g<1>%s\g<2>" % v, s)
    s = re.sub(r'(LICENSE_PUBLIC_KEY\s*=\s*")[^"]*(")', r"\g<1>PASTE_LICENSE_PUBLIC_KEY\g<2>", s)
    if reminder:
        s = re.sub(r'(getDailyReminderBody\(\)\s*\{\s*return\s*")[^"]*(")',
                   lambda m: m.group(1) + reminder.replace('"', '\\"') + m.group(2), s)
    # Firebase optional: no google-services.json -> analytics stays null.
    s = s.replace("        firebaseAnalytics = FirebaseAnalytics.getInstance(this);",
                  "        try { firebaseAnalytics = FirebaseAnalytics.getInstance(this); }\n"
                  "        catch (Throwable t) { firebaseAnalytics = null; } // no google-services.json")
    return s


def rewrite_gradle_app(src: str, src_pkg: str, pkg: str, vc: int, vn: str) -> str:
    s = src.replace(src_pkg, pkg)
    s = re.sub(r"versionCode\s+\d+", f"versionCode {vc}", s)
    s = re.sub(r'versionName\s+"[^"]*"', f'versionName "{vn}"', s)
    s = s.replace("apply plugin: 'com.google.gms.google-services'",
                  "// Firebase is optional: drop app/google-services.json in to enable analytics.\n"
                  "if (file('google-services.json').exists()) { apply plugin: 'com.google.gms.google-services' }")
    return s


def rewrite_manifest(src: str, src_pkg: str, pkg: str, name: str, src_name: str) -> str:
    s = src.replace(src_pkg, pkg)
    s = s.replace(f'android:label="{src_name}"', f'android:label="{name}"')
    s = re.sub(r"ca-app-pub-\d{16}~\d+", TEST_APP_ID, s)
    return s


def rewrite_html(src: str, src_app: str, src_pkg: str, src_name: str, app: str, pkg: str,
                 name: str, vn: str) -> str:
    src_low, low = src_pkg.split(".")[-1], pkg.split(".")[-1]
    s = src.replace(src_pkg, pkg)
    s = s.replace(f"'{src_low}_save'", f"'{low}_save'").replace(f'"{src_low}_save"', f'"{low}_save"')
    s = re.sub(r"<title>[^<]*</title>", f"<title>{name}</title>", s, count=1)
    m = re.search(r"<script data-growth-config>window\.GROWTH_CFG=(\{.*?\});</script>", s)
    if m:
        cfg = json.loads(m.group(1))
        cfg.update(app=app, pkg=pkg, name=name, saveKey=f"{low}_save")
        s = s[:m.start(1)] + json.dumps(cfg, ensure_ascii=False, separators=(",", ":")) + s[m.end(1):]
    s = re.sub(r'(data-app-version=")[^"]*(")', r"\g<1>%s\g<2>" % vn, s)
    # Leaderboard IDs belong to SOURCE's Play Games entries.
    # Only quoted literals and the comment table — never inside base64 font data.
    s = re.sub(r"(?<=['\"\s])Cgk[A-Za-z0-9_-]{10,}(?=['\"\s])", "TODO_LEADERBOARD_ID", s)
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target")
    ap.add_argument("--name", required=True, help="store/display name (folder must match it)")
    ap.add_argument("--version-name", required=True)
    ap.add_argument("--from", dest="src", default="Afterimage")
    ap.add_argument("--reminder", default="", help="daily reminder notification text")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    app, src_app = a.target, a.src
    if not (BASE / app / "android").is_dir():
        raise SystemExit(f"{app}: no android/ folder")
    src_pkg, pkg = pkg_of(src_app), pkg_of(app)
    vc = version_code_of(app) + 1
    src_android, dst_android = BASE / src_app / "android", BASE / app / "android"
    src_name = re.search(r'android:label="([^"]+)"',
                         (src_android / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")).group(1)
    print(f"{app}: {pkg} → shell from {src_app} ({src_pkg}); versionCode {vc}, versionName {a.version_name}")

    plan = []
    for rel in WRAPPER_FILES:
        sp, dp = src_android / rel, dst_android / rel
        if not sp.exists():
            continue
        if rel in ("app/build.gradle",):
            out = rewrite_gradle_app(sp.read_text(encoding="utf-8"), src_pkg, pkg, vc, a.version_name)
        elif rel == "app/src/main/AndroidManifest.xml":
            out = rewrite_manifest(sp.read_text(encoding="utf-8"), src_pkg, pkg, a.name, src_name)
        elif rel == "settings.gradle":
            out = re.sub(r'rootProject\.name\s*=\s*"[^"]*"', f'rootProject.name = "{app}"',
                         sp.read_text(encoding="utf-8"))
        elif rel == "app/src/main/res/values/strings.xml":
            out = re.sub(r"\s*<!-- TODO\(name\)[\s\S]*?-->", "", sp.read_text(encoding="utf-8"))
        elif sp.suffix in (".jar",) or rel in ("gradlew", "gradlew.bat"):
            out = sp.read_bytes()
        else:
            out = sp.read_text(encoding="utf-8").replace(src_pkg, pkg)
        plan.append((dp, out))

    # Java: replace the whole package dir with SOURCE's classes.
    sj, dj = java_dir(src_app, src_pkg), java_dir(app, pkg)
    old_java = sorted(dj.glob("*.java")) if dj.exists() else []
    for f in sorted(sj.glob("*.java")):
        out = f.read_text(encoding="utf-8")
        out = rewrite_java(out, src_pkg, pkg, a.reminder) if f.name == "MainActivity.java" else out.replace(src_pkg, pkg)
        plan.append((dj / f.name, out))

    # game.html shell.
    sh = BASE / src_app / "android/app/src/main/assets/game.html"
    plan.append((BASE / app / "android/app/src/main/assets/game.html",
                 rewrite_html(sh.read_text(encoding="utf-8"), src_app, src_pkg, src_name, app, pkg,
                              a.name, a.version_name)))

    # Mediation notes (generic, per-app copy).
    mp = BASE / src_app / "MEDIATION_SETUP.md"
    if mp.exists():
        plan.append((BASE / app / "MEDIATION_SETUP.md",
                     mp.read_text(encoding="utf-8").replace(src_name, a.name).replace(src_app, app)))

    # IAP catalog: SOURCE's only when it is a superset of TARGET's.
    si, di = BASE / src_app / "metadata/iaps.json", BASE / app / "metadata/iaps.json"
    skus = lambda d: {p.get("id") for k in ("one_time_products", "subscriptions") for p in d.get(k, [])}
    sd = json.loads(si.read_text(encoding="utf-8"))
    dd = json.loads(di.read_text(encoding="utf-8")) if di.exists() else {}
    if skus(dd) <= skus(sd):
        plan.append((di, json.dumps(sd, indent=2, ensure_ascii=False) + "\n"))
    else:
        print(f"  ! {app}: iaps.json has SKUs outside {src_app}'s catalog {sorted(skus(dd) - skus(sd))} — kept as is")
    for extra in ("privacy.json", "content_rating.json", "review_notes.json"):
        if not (BASE / app / "metadata" / extra).exists() and (BASE / src_app / "metadata" / extra).exists():
            plan.append((BASE / app / "metadata" / extra,
                         (BASE / src_app / "metadata" / extra).read_text(encoding="utf-8")
                         .replace(src_pkg, pkg).replace(src_name, a.name)))

    for dp, out in plan:
        print(f"  {'would write' if a.dry_run else 'write'} {dp.relative_to(BASE)}")
    for f in old_java:
        if f.name not in {p.name for p in sj.glob('*.java')}:
            print(f"  {'would remove' if a.dry_run else 'remove'} {f.relative_to(BASE)}")
    if a.dry_run:
        return 0
    for dp, out in plan:
        dp.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(out, bytes):
            dp.write_bytes(out)
        else:
            dp.write_text(out, encoding="utf-8")
    for f in old_java:
        if f.name not in {p.name for p in sj.glob('*.java')}:
            f.unlink()
    shutil.copymode(src_android / "gradlew", dst_android / "gradlew")
    return 0


if __name__ == "__main__":
    sys.exit(main())
