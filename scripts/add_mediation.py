#!/usr/bin/env python3
"""add_mediation.py — Part 3 of the AppLovin->AdMob migration.

Adds the latest stable AdMob mediation adapters (Meta Audience Network, Unity
Ads, Mintegral, Pangle, InMobi) to the 8 AdMob apps, wires the two extra Maven
repos those adapters need, and writes a per-app MEDIATION_SETUP.md.

Versions (looked up 2026-06, Google's per-network mediation guides):
  Meta      com.google.ads.mediation:facebook:6.21.0.3
  Unity     com.google.ads.mediation:unity:4.18.0.0
  Mintegral com.google.ads.mediation:mintegral:17.1.61.0   (custom Maven repo)
  Pangle    com.google.ads.mediation:pangle:8.0.0.5.0       (custom Maven repo)
  InMobi    com.google.ads.mediation:inmobi:11.3.0.0

No app-manifest entry is strictly required: every network's credentials
(Meta placement, Unity game id, Mintegral app id/key, Pangle app id, InMobi
account id) are entered in the AdMob dashboard mediation groups, not the APK.
So no IDs are invented here — they live as TODO placeholders in MEDIATION_SETUP.md.

Usage:  python3 scripts/add_mediation.py [--dry-run] [App ...]
"""
import os
import re
import sys
import difflib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

APPS = [
    "Afterimage", "Hunch", "Overlay", "PipeConnect",
    "Nonogram", "Puzzle2048", "UnblockPuzzle", "WaterSortPuzzle",
]

PLAY_ADS = "    implementation 'com.google.android.gms:play-services-ads:25.3.0'"
ADAPTERS_BLOCK = PLAY_ADS + "\n" + "\n".join([
    "    // AdMob mediation adapters — network credentials live in the AdMob",
    "    // dashboard mediation groups (see MEDIATION_SETUP.md), not the APK.",
    "    implementation 'com.google.ads.mediation:facebook:6.21.0.3'",
    "    implementation 'com.google.ads.mediation:unity:4.18.0.0'",
    "    implementation 'com.google.ads.mediation:mintegral:17.1.61.0'",
    "    implementation 'com.google.ads.mediation:pangle:8.0.0.5.0'",
    "    implementation 'com.google.ads.mediation:inmobi:11.3.0.0'",
])

MINTEGRAL_REPO = "        maven { url 'https://dl-maven-android.mintegral.com/repository/mbridge_android_sdk_oversea' }"
PANGLE_REPO = "        maven { url 'https://artifact.bytedance.com/repository/pangle/' }"


def find_mainactivity(app):
    base = os.path.join(ROOT, app, "android", "app", "src", "main", "java")
    for dp, _, fs in os.walk(base):
        if "MainActivity.java" in fs:
            return os.path.join(dp, "MainActivity.java")
    return None


def ad_ids(app):
    j = find_mainactivity(app)
    t = open(j, encoding="utf-8").read()

    def grab(name):
        m = re.search(name + r'\s*=\s*"([^"]+)"', t)
        return m.group(1) if m else "(not found)"
    m = os.path.join(ROOT, app, "android", "app", "src", "main", "AndroidManifest.xml")
    mt = open(m, encoding="utf-8").read()
    appid = re.search(r'APPLICATION_ID"\s*\n?\s*android:value="([^"]+)"', mt)
    return {
        "app_id": appid.group(1) if appid else "(not found)",
        "banner": grab("ADMOB_BANNER_UNIT_ID"),
        "interstitial": grab("ADMOB_INTERSTITIAL_UNIT_ID"),
        "rewarded": grab("ADMOB_REWARDED_UNIT_ID"),
    }


def transform_settings(text):
    if "dl-maven-android.mintegral.com" in text:
        return text  # idempotent
    # add the two repos right after mavenCentral() inside dependencyResolutionManagement
    lines = text.split("\n")
    out = []
    added = False
    in_drm = False
    for line in lines:
        out.append(line)
        if "dependencyResolutionManagement" in line:
            in_drm = True
        if in_drm and not added and re.match(r"\s*mavenCentral\(\)\s*$", line):
            out.append(MINTEGRAL_REPO)
            out.append(PANGLE_REPO)
            added = True
            in_drm = False
    return "\n".join(out)


def transform_gradle(text):
    if "com.google.ads.mediation:facebook" in text:
        return text  # idempotent
    if PLAY_ADS not in text:
        raise RuntimeError("play-services-ads anchor not found")
    return text.replace(PLAY_ADS, ADAPTERS_BLOCK, 1)


def mediation_md(app):
    ids = ad_ids(app)
    return """\
# Mediation setup — {app}

AdMob is the primary ad source; these adapters let AdMob mediate five extra
demand networks. **Do this in the AdMob dashboard** — the APK ships the adapter
code, but each network's credentials are entered server-side, never hard-coded.

## Ad units (this app)

| Format       | AdMob ad unit ID |
|--------------|------------------|
| App ID       | `{app_id}` |
| Banner       | `{banner}` |
| Interstitial | `{interstitial}` |
| Rewarded     | `{rewarded}` |

## Adapters bundled (Gradle)

| Network              | Adapter artifact                              |
|----------------------|-----------------------------------------------|
| Meta Audience Network| `com.google.ads.mediation:facebook:6.21.0.3`  |
| Unity Ads            | `com.google.ads.mediation:unity:4.18.0.0`     |
| Mintegral            | `com.google.ads.mediation:mintegral:17.1.61.0`|
| Pangle               | `com.google.ads.mediation:pangle:8.0.0.5.0`   |
| InMobi               | `com.google.ads.mediation:inmobi:11.3.0.0`    |

Mintegral + Pangle resolve from custom Maven repos added to `settings.gradle`.

## Dashboard wiring (one mediation group per format)

For EACH ad unit above, create a mediation group in AdMob
(Mediation → Create mediation group), attach the ad unit, then add each network
as a line item. Map them like so:

| Format       | Mediation group name      | Networks to attach                         |
|--------------|---------------------------|--------------------------------------------|
| Banner       | `{app}-banner-mediation`       | Meta, Unity, Mintegral, Pangle, InMobi |
| Interstitial | `{app}-interstitial-mediation` | Meta, Unity, Mintegral, Pangle, InMobi |
| Rewarded     | `{app}-rewarded-mediation`     | Meta, Unity, Mintegral, Pangle, InMobi |

## Per-network credentials — fill in the dashboard (do NOT hard-code)

Create each app/placement in the network's own console, then paste the IDs into
the matching AdMob line item. Nothing below ships in the APK.

- Meta Audience Network — TODO: `<META_PLACEMENT_ID>` (per format) from
  developers.facebook.com → Audience Network.
- Unity Ads — TODO: `<UNITY_GAME_ID>` + `<UNITY_PLACEMENT_ID>` from the Unity
  Ads dashboard.
- Mintegral — TODO: `<MINTEGRAL_APP_ID>`, `<MINTEGRAL_APP_KEY>`,
  `<MINTEGRAL_UNIT_ID>` from the Mintegral console.
- Pangle — TODO: `<PANGLE_APP_ID>`, `<PANGLE_SLOT_ID>` from the Pangle console.
- InMobi — TODO: `<INMOBI_ACCOUNT_ID>`, `<INMOBI_PLACEMENT_ID>` from the InMobi
  console.

## Notes

- No AndroidManifest changes are required: these GMA adapters merge their own
  manifest entries, and all credentials are dashboard-side.
- Enable each network in the AdMob mediation group only after its line item has
  real credentials, or it will no-fill.
- Test with the AdMob mediation test suite before going live.
""".format(app=app, **ids)


def process(app, dry):
    changed = []
    s = os.path.join(ROOT, app, "android", "settings.gradle")
    st = open(s, encoding="utf-8").read()
    st2 = transform_settings(st)
    if st2 != st:
        changed.append((s, st, st2))

    g = os.path.join(ROOT, app, "android", "app", "build.gradle")
    gt = open(g, encoding="utf-8").read()
    gt2 = transform_gradle(gt)
    if gt2 != gt:
        changed.append((g, gt, gt2))

    md = os.path.join(ROOT, app, "MEDIATION_SETUP.md")
    md_new = mediation_md(app)
    md_old = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
    if md_new != md_old:
        changed.append((md, md_old, md_new))

    for path, before, after in changed:
        rel = os.path.relpath(path, ROOT)
        if dry:
            diff = difflib.unified_diff(before.split("\n"), after.split("\n"),
                                        fromfile="a/" + rel, tofile="b/" + rel, lineterm="")
            print("\n".join(diff))
        else:
            open(path, "w", encoding="utf-8").write(after)
    if not dry:
        print("  %s: %d file(s)" % (app, len(changed)))
    return True


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    apps = [a for a in args if not a.startswith("--")] or APPS
    for app in apps:
        print("==== %s ====" % app)
        process(app, dry)


if __name__ == "__main__":
    main()
