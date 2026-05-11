#!/usr/bin/env python3
"""
migrate_to_per_app_keystores.py — generate dedicated keystores for apps
currently using the shared pegasusgames-release.jks.

CONTEXT (May 2026 audit):
A scan of the repo found 154 apps signed with a single shared
keystore (pegasusgames-release.jks, alias pegasusgames, SHA1 starting
E0:BD:7F:24). Per CLAUDE.md "Keystore management — per-app, not global",
this is forbidden — one lost or compromised keystore should never block
or compromise more than one app.

This script generates a dedicated keystore for each app currently
using the shared one, updates that app's keystore.properties to point
at the new file, and prints a backup checklist.

CRITICAL: only run this for apps that have NOT YET been uploaded to
Play Console. Once an app uploads with one keystore, Play Console
permanently registers that keystore as the upload key. Switching to a
new keystore after that requires an upload-key reset request per app
(1-3 business days each, may be denied if rapid-fire).

USAGE:
    # Dry run — list what would change, don't touch anything
    python3 scripts/migrate_to_per_app_keystores.py --dry-run

    # Migrate one app
    python3 scripts/migrate_to_per_app_keystores.py --app NewApp

    # Migrate all apps that have never been uploaded (CHECK THE LIST)
    python3 scripts/migrate_to_per_app_keystores.py --execute --not-yet-uploaded

By default, this script REFUSES to migrate an app where
metadata/app_info.json has 'first_upload_at' set (indicating Play
Console has registered the upload key). Override with --force only if
you're certain.

REQUIRES:
    keytool (comes with the JDK)

WHAT IT DOES:
    For each app being migrated:
    1. Check the app has a keystore.properties currently pointing at
       the shared pegasusgames-release.jks
    2. Check metadata/app_info.json doesn't have 'first_upload_at' set
       (skip if it does)
    3. Generate <App>/android/keystore.jks via keytool with random
       passwords (16 chars alphanumeric)
    4. Write <App>/android/keystore.properties (gitignored) referencing
       the new keystore
    5. Verify .gitignore covers keystore.* (warn if not)
    6. Compute the new keystore's SHA1 and record in
       metadata/app_info.json:upload_key_sha1
    7. Print a backup reminder with the keystore path and password

After running, BACK UP each new keystore.jks to Google Drive + USB stick.
The keystore.properties is the ONLY place the password lives — losing it
means losing access to that app permanently (or going through the reset
process per app).
"""

import argparse
import json
import os
import secrets
import string
import subprocess
import sys
from pathlib import Path

REPO_ROOT = (Path(__file__).resolve().parent.parent
             if Path(__file__).resolve().parent.name == "scripts"
             else Path(__file__).resolve().parent)

# Apps that ALREADY have correct per-app keystores — never touch these
EXEMPT_APPS = {
    "WaterSort",       # 71:C7:86 — already shipped to Play Console
    "Nonogram",        # 99:32:85 — pending reset
    "Puzzle2048",      # 97:71:24 — already per-app
    "PipeConnect",     # 9A:DA:7D — already per-app
    "UnblockPuzzle",   # 1A:E6:BE — already per-app
    "_template",       # template scaffolding
    "_release",        # build artifacts
}


def gen_password(n=16):
    """Generate a strong random password — alphanumeric only to avoid
    shell-escaping issues in keystore.properties."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(n))


def already_uploaded(app_dir: Path) -> bool:
    """Check whether app_info.json indicates this app has been uploaded
    to Play Console (and thus has a locked-in upload key)."""
    info_path = app_dir / "metadata" / "app_info.json"
    if not info_path.exists():
        return False
    try:
        info = json.loads(info_path.read_text())
    except (IOError, ValueError):
        return False
    return bool(info.get("first_upload_at"))


def uses_shared_keystore(app_dir: Path) -> bool:
    """Check whether this app currently points at pegasusgames-release.jks."""
    props_path = app_dir / "android" / "keystore.properties"
    if not props_path.exists():
        return False
    try:
        content = props_path.read_text()
    except IOError:
        return False
    return "pegasusgames-release.jks" in content or "pegasusgames" in content.lower()


def get_keystore_sha1(keystore_path: Path, password: str,
                       alias: str) -> str:
    """Read a keystore's SHA1 fingerprint via keytool."""
    try:
        result = subprocess.run(
            ["keytool", "-list", "-v",
             "-keystore", str(keystore_path),
             "-storepass", password,
             "-alias", alias],
            capture_output=True, text=True, timeout=15, check=False,
        )
        for line in result.stdout.splitlines():
            if "SHA1:" in line and "(" not in line:  # skip "Signature algorithm name: SHA1..." lines
                return line.split("SHA1:")[1].strip()
        # Fallback: SHA-1 with hyphen also acceptable
        for line in result.stdout.splitlines():
            if "SHA1" in line and ":" in line:
                return line.split("SHA1")[1].split(":", 1)[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


def generate_keystore(app_name: str, app_dir: Path, dry_run: bool):
    """Generate a fresh keystore for one app."""
    keystore_path = app_dir / "android" / "keystore.jks"
    props_path = app_dir / "android" / "keystore.properties"

    store_password = gen_password()
    # PKCS12 keystores (keytool's default since JDK 9) enforce
    # keyPassword == storePassword. Writing a different keyPassword to
    # keystore.properties causes "Given final block not properly padded"
    # at gradle signRelease time — the May 2026 migration hit this on
    # 166 apps. Always keep them equal.
    key_password = store_password
    alias = app_name.lower().replace(" ", "")[:30]

    print(f"  [{app_name}]")
    print(f"    keystore: {keystore_path}")
    print(f"    properties: {props_path}")
    print(f"    alias: {alias}")
    print(f"    storePassword: {store_password}")
    print(f"    keyPassword: {key_password} (=storePassword, required by PKCS12)")

    if dry_run:
        print(f"    DRY RUN — would generate keystore + write properties")
        return None

    # Don't overwrite an existing keystore
    if keystore_path.exists():
        print(f"    SKIP — keystore.jks already exists; not overwriting")
        return None

    keystore_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate keystore
    cmd = [
        "keytool", "-genkey", "-v",
        "-keystore", str(keystore_path),
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-alias", alias,
        "-storepass", store_password,
        "-keypass", key_password,
        "-dname", f"CN={app_name}, OU=PegasusGames, O=PegasusGames, "
                  f"L=Kyiv, ST=Kyiv, C=UA",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=30, check=False)
        if result.returncode != 0:
            print(f"    FAIL — keytool returned {result.returncode}")
            print(f"    stderr: {result.stderr.strip()[:300]}")
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"    FAIL — keytool not available or timed out: {e}")
        return None

    # Write keystore.properties
    props_content = (
        f"# Generated by migrate_to_per_app_keystores.py\n"
        f"# DO NOT COMMIT — file is gitignored.\n"
        f"# Backed up to: [TODO — fill in after backing up]\n"
        f"storeFile=keystore.jks\n"
        f"storePassword={store_password}\n"
        f"keyAlias={alias}\n"
        f"keyPassword={key_password}\n"
    )
    props_path.write_text(props_content)

    # Export the public certificate as upload_cert_request.pem so the
    # user has it ready to attach when requesting an upload-key reset
    # in Play Console. (Every new app in this account is auto-enrolled
    # in Play App Signing with a Google-generated upload key; switching
    # to the local key requires a per-app reset request, attaching this
    # PEM file.)
    pem_path = app_dir / "android" / "upload_cert_request.pem"
    try:
        subprocess.run([
            "keytool", "-export", "-rfc",
            "-keystore", str(keystore_path),
            "-storepass", store_password,
            "-alias", alias,
            "-file", str(pem_path),
        ], capture_output=True, text=True, timeout=15, check=True)
        print(f"    upload_cert_request.pem exported for Play Console reset")
    except (FileNotFoundError, subprocess.TimeoutExpired,
            subprocess.CalledProcessError) as e:
        print(f"    WARN — couldn't export upload_cert_request.pem: {e}")

    # Compute SHA1 and record in app_info.json
    sha1 = get_keystore_sha1(keystore_path, store_password, alias)
    if sha1:
        info_path = app_dir / "metadata" / "app_info.json"
        if info_path.exists():
            try:
                info = json.loads(info_path.read_text())
                info["upload_key_sha1"] = sha1
                info_path.write_text(json.dumps(info, indent=2) + "\n")
                print(f"    SHA1: {sha1}")
                print(f"    Recorded in metadata/app_info.json")
            except (IOError, ValueError) as e:
                print(f"    WARN — couldn't update app_info.json: {e}")
        else:
            print(f"    WARN — metadata/app_info.json doesn't exist; "
                  f"create it and add upload_key_sha1: {sha1}")
    return sha1


def check_gitignore():
    """Verify .gitignore covers keystore files."""
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        return False
    content = gi.read_text()
    patterns = ["keystore.jks", "keystore.properties", "*.jks"]
    return any(p in content for p in patterns)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen, don't generate keystores")
    ap.add_argument("--execute", action="store_true",
                    help="actually generate keystores")
    ap.add_argument("--app", help="migrate only this single app")
    ap.add_argument("--not-yet-uploaded", action="store_true",
                    help="migrate all apps without first_upload_at set")
    ap.add_argument("--force", action="store_true",
                    help="override the 'already uploaded' safety check")
    args = ap.parse_args()

    if not args.dry_run and not args.execute:
        print("Specify --dry-run OR --execute")
        sys.exit(1)

    # Verify .gitignore covers keystores
    if not check_gitignore():
        print("WARN: .gitignore doesn't seem to cover keystore files.")
        print("      Add lines: keystore.jks / keystore.properties / *.jks")
        print()

    # Find candidate apps
    if args.app:
        candidates = [args.app]
    else:
        candidates = sorted([
            p.name for p in REPO_ROOT.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and not p.name.startswith("_")
            and (p / "android").is_dir()
        ])

    targets = []
    for app in candidates:
        if app in EXEMPT_APPS:
            continue
        app_dir = REPO_ROOT / app
        if not app_dir.is_dir():
            print(f"  SKIP {app} — not a directory")
            continue

        # Currently using shared keystore?
        if not uses_shared_keystore(app_dir):
            continue  # already has dedicated keystore or no signing config

        # Already uploaded to Play Console?
        if already_uploaded(app_dir) and not args.force:
            print(f"  BLOCK {app} — already uploaded to Play Console "
                  f"(first_upload_at set in app_info.json). Migrating now "
                  f"would require an upload-key reset. Use --force only if "
                  f"you've already requested the reset.")
            continue

        targets.append(app)

    if not targets:
        print("No apps to migrate.")
        return

    print(f"Migrating {len(targets)} apps from shared to per-app keystores:")
    print()

    sha1s = {}
    for app in targets:
        sha1 = generate_keystore(app, REPO_ROOT / app, dry_run=args.dry_run)
        if sha1:
            sha1s[app] = sha1
        print()

    if args.execute and sha1s:
        print()
        print("=" * 60)
        print("BACK UP THESE KEYSTORES IMMEDIATELY")
        print("=" * 60)
        print()
        print("Each keystore is at <App>/android/keystore.jks")
        print("Passwords are in <App>/android/keystore.properties (gitignored)")
        print()
        print("Required backups (do all three):")
        print("  1. Google Drive (encrypted folder, Pegasus Games email)")
        print("  2. USB stick (physical, kept off the development machine)")
        print("  3. Password manager entry per app with the SHA1 fingerprint")
        print()
        print("Apps migrated this run:")
        for app, sha1 in sha1s.items():
            print(f"  {app}: {sha1}")
        print()
        print("Until backed up, these keystores exist ONLY on this machine.")
        print("Loss of this machine = permanent loss of update access for")
        print(f"all {len(sha1s)} apps just migrated.")


if __name__ == "__main__":
    main()
