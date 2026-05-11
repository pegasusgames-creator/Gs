#!/usr/bin/env python3
"""
pepk_command.py — print the exact PEPK command for one app.

Background: every new Pegasus Games app on Play Console is auto-enrolled
in Play App Signing with a Google-generated upload key (cert SHA-1
EC:24:33:14:46:29:71:D1:4C:B0:2B:86:D0:4D:D4:FF:EC:6F:86:B5, owned by
Google's Bundle & Delivery team). The local keystore.jks doesn't match,
so AABs get rejected on upload.

The PEPK flow registers the local keystore as the app's signing key
without the 1-3 business day reset wait. The human:
  1. In Play Console: App integrity → App signing → "Export and upload
     key from Java keystore".
  2. Downloads encryption_public_key.pem + pepk.jar into <App>/android/.
  3. Runs the command this script prints (alias + password pulled from
     keystore.properties).
  4. Uploads the produced .zip via Play Console step 4. Saves. Done.

Usage:
    python3 scripts/pepk_command.py <AppName>
    python3 scripts/pepk_command.py --all       # print for every app

If --print-only, the command is just printed. Otherwise, this script
checks that the prerequisites (encryption_public_key.pem + pepk.jar)
are present in <App>/android/ and refuses to print the command if
either is missing — that's the most common cause of confusion.
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def list_apps():
    SKIP = {'_template','_release','docs','scripts','release_aabs',
            'BLOCKED_APPS','__pycache__','.git','.idea','node_modules'}
    out = []
    for n in sorted(os.listdir(REPO)):
        if n in SKIP or n.startswith('.'): continue
        d = os.path.join(REPO, n)
        if not os.path.isdir(d): continue
        if os.path.isfile(os.path.join(d, 'android', 'keystore.properties')):
            out.append(n)
    return out


def read_props(app):
    p = os.path.join(REPO, app, 'android', 'keystore.properties')
    if not os.path.isfile(p):
        return None
    text = open(p).read()
    out = {}
    for key in ('storePassword', 'keyAlias', 'keyPassword'):
        m = re.search(rf'^{key}\s*=\s*(.+)$', text, re.M)
        if m: out[key] = m.group(1).strip()
    return out


def cmd_for_app(app, print_only=False):
    android = os.path.join(REPO, app, 'android')
    props = read_props(app)
    if not props:
        return None, f'{app}: keystore.properties missing'
    alias = props.get('keyAlias', '?')
    sp    = props.get('storePassword', '?')
    kp    = props.get('keyPassword', sp)

    missing = []
    if not os.path.isfile(os.path.join(android, 'encryption_public_key.pem')):
        missing.append('encryption_public_key.pem')
    if not os.path.isfile(os.path.join(android, 'pepk.jar')):
        missing.append('pepk.jar')
    if missing and not print_only:
        return None, (f'{app}: prerequisites missing in {android}/: {missing}\n'
                      f'  Download them from Play Console → App integrity → App signing '
                      f'(radio: "Export and upload key from Java keystore")')

    cmd = (
        f'cd {android} && \\\n'
        f'java -jar pepk.jar \\\n'
        f'  --keystore=keystore.jks \\\n'
        f'  --alias={alias} \\\n'
        f'  --output={alias}_pepk.zip \\\n'
        f'  --include-cert \\\n'
        f'  --rsa-aes-encryption \\\n'
        f'  --encryption-key-path=encryption_public_key.pem \\\n'
        f'  --keystore-pass={sp} \\\n'
        f'  --key-pass={kp}'
    )
    return cmd, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true',
                    help='print command for every app (prerequisites check skipped)')
    args = ap.parse_args()
    if args.all:
        apps = list_apps()
        print_only = True
    elif args.apps:
        apps = args.apps
        print_only = False
    else:
        ap.print_help()
        sys.exit(2)

    any_err = False
    for app in apps:
        cmd, err = cmd_for_app(app, print_only=print_only)
        if err:
            print(f'# ERROR: {err}', file=sys.stderr)
            any_err = True
            continue
        print(f'# ── {app} ──')
        print(cmd)
        print(f'# → produces {app}/android/{read_props(app)["keyAlias"]}_pepk.zip')
        print(f'# Upload that .zip via Play Console → App signing → step 4')
        print()
    sys.exit(1 if any_err else 0)


if __name__ == '__main__':
    main()
