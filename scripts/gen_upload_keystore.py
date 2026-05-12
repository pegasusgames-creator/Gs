#!/usr/bin/env python3
"""
gen_upload_keystore.py — generate a separate upload keystore for one
app (Play Console "App signing key must differ from upload key" rule).

Background — Pegasus Games Play Console flow:
  - Each app's <App>/android/keystore.jks is the APP SIGNING KEY,
    registered with Play Console via PEPK (Play encrypts the private
    key with their public key, we upload the encrypted bundle, Play
    decrypts on its side and uses it server-side to re-sign delivered
    APKs).
  - Play Console then requires a SEPARATE upload key. AABs uploaded
    to Play Console must be signed with the upload key, not the app
    signing key.

This script:
  1. Generates <App>/android/upload-keystore.jks with alias `upload`.
  2. Exports its public cert as <App>/android/upload_certificate.pem
     (for the human to upload at Play Console step 5c).
  3. Rewrites <App>/android/keystore.properties to point gradle at
     the upload keystore (so bundleRelease produces an AAB signed
     with the upload key, which is what Play accepts).
  4. Records both SHA1s in <App>/metadata/app_info.json:
     - upload_key_sha1       = upload keystore (what AABs are signed with)
     - app_signing_key_sha1  = original keystore.jks (Play's server-side key)

The original keystore.jks is preserved (renamed back-reference only;
file untouched). NEVER delete it — Play uses it server-side to sign
production deliveries.

Usage:
  python3 scripts/gen_upload_keystore.py <AppName>
  python3 scripts/gen_upload_keystore.py --all
"""
import argparse
import json
import os
import re
import subprocess
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
        if os.path.isfile(os.path.join(d, 'android', 'keystore.jks')):
            out.append(n)
    return out


def keystore_sha1(jks, storepass, alias):
    r = subprocess.run([
        'keytool', '-list', '-v', '-keystore', jks,
        '-storepass', storepass, '-alias', alias
    ], capture_output=True, text=True, timeout=15)
    for line in r.stdout.splitlines():
        if 'SHA1:' in line:
            return line.split('SHA1:')[1].strip()
    return None


def process(app):
    android = os.path.join(REPO, app, 'android')
    props_path = os.path.join(android, 'keystore.properties')
    app_signing_jks = os.path.join(android, 'keystore.jks')
    upload_jks  = os.path.join(android, 'upload-keystore.jks')
    upload_pem  = os.path.join(android, 'upload_certificate.pem')
    info_path = os.path.join(REPO, app, 'metadata', 'app_info.json')

    if not os.path.isfile(app_signing_jks):
        return f'{app}: app-signing keystore.jks missing'
    if not os.path.isfile(props_path):
        return f'{app}: keystore.properties missing'

    if os.path.isfile(upload_jks):
        return f'{app}: upload-keystore.jks already exists (skip — run gen_upload_keystore.py only on first setup)'

    # Read existing properties to get the original app-signing alias and
    # password (needed only to record app_signing_key_sha1).
    props_text = open(props_path).read()
    spm = re.search(r'^storePassword\s*=\s*(.+)$', props_text, re.M)
    alm = re.search(r'^keyAlias\s*=\s*(.+)$',     props_text, re.M)
    if not (spm and alm):
        return f'{app}: keystore.properties is malformed'
    app_signing_pw    = spm.group(1).strip()
    app_signing_alias = alm.group(1).strip()

    upload_pw = app_signing_pw + 'upload'

    # 1. Generate upload keystore
    r = subprocess.run([
        'keytool', '-genkeypair',
        '-keystore', upload_jks,
        '-keyalg', 'RSA', '-keysize', '2048',
        '-validity', '10000',
        '-alias', 'upload',
        '-storepass', upload_pw,
        '-keypass',   upload_pw,
        '-dname', f'CN={app}-Upload, OU=PegasusGames, O=PegasusGames, '
                  f'L=Kyiv, ST=Kyiv, C=UA',
    ], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return f'{app}: keytool genkeypair failed: {r.stderr.strip()[:200]}'

    # 2. Export upload public cert
    r = subprocess.run([
        'keytool', '-export', '-rfc',
        '-keystore', upload_jks,
        '-storepass', upload_pw,
        '-alias', 'upload',
        '-file', upload_pem,
    ], capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return f'{app}: keytool export failed: {r.stderr.strip()[:200]}'

    upload_sha1 = keystore_sha1(upload_jks, upload_pw, 'upload')
    app_signing_sha1 = keystore_sha1(app_signing_jks, app_signing_pw, app_signing_alias)

    # 3. Rewrite keystore.properties to point gradle at the upload
    new_props = (
        "# Two keys per Play App Signing:\n"
        "#   - keystore.jks: the APP SIGNING KEY, registered with Play via\n"
        "#     PEPK. Play uses this server-side to re-sign deliveries. Keep\n"
        "#     this file safe; never delete; back up to Google Drive + USB.\n"
        "#   - upload-keystore.jks: the UPLOAD KEY. Used by gradle to sign\n"
        "#     AABs that we upload to Play Console. Must differ from the app\n"
        "#     signing key (Play enforces this).\n"
        "# Gradle reads the entries below — signs AABs with the upload key.\n"
        f"storeFile=upload-keystore.jks\n"
        f"storePassword={upload_pw}\n"
        f"keyAlias=upload\n"
        f"keyPassword={upload_pw}\n"
        "\n"
        "# App-signing key reference (DO NOT use for gradle signing — Play\n"
        "# rejects AABs signed with the app-signing key):\n"
        f"# appSigningStoreFile=keystore.jks\n"
        f"# appSigningStorePassword={app_signing_pw}\n"
        f"# appSigningKeyAlias={app_signing_alias}\n"
    )
    open(props_path, 'w').write(new_props)

    # 4. Record both SHA1s in app_info.json
    if os.path.isfile(info_path):
        try:
            info = json.loads(open(info_path).read())
            info['upload_key_sha1']      = upload_sha1
            info['app_signing_key_sha1'] = app_signing_sha1
            open(info_path, 'w').write(json.dumps(info, indent=2) + '\n')
        except (IOError, ValueError) as e:
            return (f'{app}: keystore + cert ready, but failed to update '
                    f'app_info.json: {e}')

    return f'{app}: ✓ upload-keystore.jks ({upload_sha1}) + upload_certificate.pem'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    apps = list_apps() if args.all else args.apps
    if not apps:
        ap.print_help(); sys.exit(2)
    for app in apps:
        print(process(app))


if __name__ == '__main__':
    main()
