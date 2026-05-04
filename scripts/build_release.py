#!/usr/bin/env python3
"""
build_release.py — automated build pipeline for a single Pegasus Games app.

Runs Phase 5 (pre-publish checks), Phase 7 (gradle bundleRelease), and
Phase 8 (post-build verification) of SHIP_GAME.md. Use after Claude Code
has finished Phases 1-4 (game logic, wrapper, assets, metadata).

Usage:
    python3 build_release.py <AppName>
    python3 build_release.py <AppName> --skip-checks      # skip Phase 5 (not recommended)
    python3 build_release.py <AppName> --verify-only      # just check existing AAB

Requires gradle wrapper (`gradlew`) inside <AppName>/android/.
"""

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRE_CHECK_SCRIPT = Path(__file__).resolve().parent / "pre_publish_check.py"


def run(cmd, cwd=None, check=True):
    """Run a command, return CompletedProcess. cmd is a list."""
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check,
                          capture_output=True, text=True)


def fail(msg, code=1):
    print(f"\n✗ FAIL: {msg}")
    sys.exit(code)


def ok(msg):
    print(f"✓ {msg}")


def warn(msg):
    print(f"! {msg}")


# ---------- Phase 5: pre-publish checks ----------

def phase_5_checks(app_name):
    print(f"\n=== Phase 5: pre-publish checks for {app_name} ===")
    if not PRE_CHECK_SCRIPT.exists():
        fail(f"pre_publish_check.py not found at {PRE_CHECK_SCRIPT}")

    result = subprocess.run(
        ["python3", str(PRE_CHECK_SCRIPT), app_name],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # Heuristic: pre_publish_check.py exits non-zero when blocking issues exist
    if result.returncode != 0:
        fail("blocking checks failed — fix the issues above and re-run")

    ok("pre-publish checks pass")


# ---------- Phase 7: build the AAB ----------

def phase_7_build(app_name):
    print(f"\n=== Phase 7: building AAB for {app_name} ===")
    android_dir = REPO_ROOT / app_name / "android"
    if not android_dir.is_dir():
        fail(f"android directory not found: {android_dir}")

    gradlew = android_dir / "gradlew"
    if not gradlew.exists():
        fail(f"gradlew script not found at {gradlew}. Run gradle init first.")

    # Make sure gradlew is executable
    if not os.access(gradlew, os.X_OK):
        os.chmod(gradlew, 0o755)

    # Clean first to avoid stale artifacts
    print("\n[clean]")
    try:
        run(["./gradlew", "clean"], cwd=android_dir)
    except subprocess.CalledProcessError as e:
        warn(f"gradle clean failed (continuing): {e.stderr[:300] if e.stderr else ''}")

    # Build the release bundle
    print("\n[bundleRelease]")
    try:
        result = run(["./gradlew", "bundleRelease", "--no-daemon"],
                     cwd=android_dir, check=False)
        if result.returncode != 0:
            print(result.stdout[-2000:])
            print(result.stderr[-2000:])
            fail(f"gradlew bundleRelease failed (exit code {result.returncode})")
    except FileNotFoundError:
        fail("./gradlew not executable — check the file permissions")

    aab_path = (android_dir / "app" / "build" / "outputs" / "bundle"
                / "release" / "app-release.aab")
    if not aab_path.exists():
        fail(f"AAB not found at expected path: {aab_path}")

    size_mb = aab_path.stat().st_size / (1024 * 1024)
    ok(f"AAB built: {aab_path} ({size_mb:.1f} MB)")
    return aab_path


# ---------- Phase 8: post-build verification ----------

def phase_8_verify(app_name, aab_path):
    print(f"\n=== Phase 8: verifying AAB ===")

    if not aab_path.exists():
        fail(f"AAB not found: {aab_path}")

    issues = []
    info = {}

    with zipfile.ZipFile(aab_path) as z:
        names = z.namelist()

        # Check signing
        sig_files = [n for n in names if n.startswith("META-INF/") and
                     (n.endswith(".RSA") or n.endswith(".DSA")
                      or n.endswith(".EC"))]
        if not sig_files:
            issues.append("AAB is not signed (no META-INF/*.RSA found)")
        else:
            info['signing'] = sig_files[0]

        # Check manifest is present
        manifest_path = "base/manifest/AndroidManifest.xml"
        if manifest_path not in names:
            issues.append(f"manifest missing: {manifest_path}")
        else:
            manifest_bytes = z.read(manifest_path)

            # Check for unreplaced placeholders
            placeholders = [
                b"__ADMOB_APP_ID_PLACEHOLDER__",
                b"ENTER_YOUR_APPLOVIN_SDK_KEY_HERE",
                b"ENTER_BANNER_AD_UNIT_ID",
                b"ENTER_INTERSTITIAL_AD_UNIT_ID",
                b"ENTER_REWARDED_AD_UNIT_ID",
            ]
            for p in placeholders:
                if p in manifest_bytes:
                    issues.append(
                        f"manifest contains placeholder {p.decode()!r} — "
                        f"replace with real value before shipping"
                    )

            # Check for debuggable flag (extracting from binary protobuf is
            # imprecise; we check for the literal string "debuggable" in the
            # binary which only appears if explicitly set)
            if b"debuggable" in manifest_bytes:
                # Could still be false; warn rather than block
                warn("manifest contains 'debuggable' string — verify it's "
                     "android:debuggable=\"false\" not \"true\"")

            # Try to extract package name (it's stored as printable string)
            import re
            pkg_match = re.search(rb'com\.pegasusgames\.([a-z0-9_]+)',
                                  manifest_bytes)
            if pkg_match:
                info['package'] = pkg_match.group(0).decode()

            # Try to extract the AdMob APPLICATION_ID value
            admob_match = re.search(rb'ca-app-pub-\d+~\d+', manifest_bytes)
            if admob_match:
                info['admob_app_id'] = admob_match.group(0).decode()

        # Check dex (compiled Java) is present
        dex_path = "base/dex/classes.dex"
        if dex_path not in names:
            issues.append(f"dex missing: {dex_path}")

        # Check assets/game.html is present
        if "base/assets/game.html" not in names:
            issues.append("base/assets/game.html missing")
        else:
            html_size = z.getinfo("base/assets/game.html").file_size
            info['game_html_size_kb'] = html_size // 1024
            if html_size < 8000:
                issues.append(
                    f"game.html is only {html_size} bytes — minimum "
                    f"functionality risk (Google may flag as too thin)"
                )

        # Check fonts bundled
        font_count = sum(1 for n in names if n.startswith("base/assets/fonts/")
                         and n.endswith(".woff2"))
        info['font_count'] = font_count
        if font_count == 0:
            warn("no .woff2 fonts found in base/assets/fonts/ — "
                 "QUALITY_PLAYBOOK §1.2 requires local fonts (no CDN)")

        # Check architectures
        archs = set()
        for n in names:
            if n.startswith("base/lib/"):
                parts = n.split("/")
                if len(parts) >= 3:
                    archs.add(parts[2])
        info['architectures'] = sorted(archs)
        if "arm64-v8a" not in archs:
            issues.append("missing arm64-v8a — required for Play Store")

    # Print summary
    print()
    print(f"  size:           {aab_path.stat().st_size / (1024*1024):.1f} MB")
    print(f"  package:        {info.get('package', 'unknown')}")
    print(f"  AdMob app ID:   {info.get('admob_app_id', '(not found)')}")
    print(f"  signing:        {info.get('signing', 'NOT SIGNED')}")
    print(f"  game.html:      {info.get('game_html_size_kb', '?')} KB")
    print(f"  fonts:          {info.get('font_count', 0)} woff2 files")
    print(f"  architectures:  {info.get('architectures', [])}")

    if issues:
        print()
        for issue in issues:
            print(f"  ✗ {issue}")
        fail(f"{len(issues)} verification issue(s)")

    ok("AAB verification passed")
    return info


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name", help="App folder name (e.g., WaterSort)")
    ap.add_argument("--skip-checks", action="store_true",
                    help="skip Phase 5 pre-publish checks (not recommended)")
    ap.add_argument("--verify-only", action="store_true",
                    help="only run Phase 8 verification on existing AAB")
    args = ap.parse_args()

    app_name = args.app_name
    app_dir = REPO_ROOT / app_name
    if not app_dir.is_dir():
        fail(f"app directory not found: {app_dir}")

    aab_path = (app_dir / "android" / "app" / "build" / "outputs" / "bundle"
                / "release" / "app-release.aab")

    if args.verify_only:
        if not aab_path.exists():
            fail(f"no existing AAB to verify at {aab_path}")
        phase_8_verify(app_name, aab_path)
        return

    if not args.skip_checks:
        phase_5_checks(app_name)

    aab_path = phase_7_build(app_name)
    phase_8_verify(app_name, aab_path)

    print()
    print("=" * 60)
    print(f"  Build complete: {aab_path}")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. Open {app_name}/RELEASE_HANDOFF.md")
    print(f"  2. Follow the 7 manual steps to set up AdMob and Play Console")
    print(f"  3. Re-run this script after pasting real AdMob IDs")
    print(f"  4. Upload the resulting AAB to Play Console → Production")


if __name__ == "__main__":
    main()
