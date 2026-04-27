#!/usr/bin/env python3
"""
gen_handoff.py — generate RELEASE_HANDOFF.md for an app.

Produces a self-contained checklist the user can follow in 20-30 minutes
to complete AdMob setup, Play Console IAP creation, store listing
upload, and policy form completion. Every value is pre-filled from the
app's metadata files.

Usage:
    python3 gen_handoff.py <AppName>
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_PRIVACY = "https://pegasusgames-creator.github.io/privacy.html"
CANONICAL_SUPPORT = "https://pegasusgames-creator.github.io/"
CANONICAL_EMAIL   = "pegasusgames@atomicmail.io"

DEFAULT_IAPS = [
    ("remove_ads",            "Managed",      "Remove Ads",      "$1.99"),
    ("coins_small",           "Managed",      "100 Coins",       "$0.99"),
    ("coins_medium",          "Managed",      "500 Coins",       "$3.99"),
    ("coins_large",           "Managed",      "1200 Coins",      "$7.99"),
    ("coins_huge",            "Managed",      "3000 Coins",      "$14.99"),
    ("starter_pack",          "Managed",      "Starter Pack",    "$0.99"),
    ("premium_themes",        "Managed",      "Premium Themes",  "$2.99"),
    ("hint_pack",             "Managed",      "Hint Pack",       "$1.99"),
    ("season_pass_monthly",   "Subscription", "Monthly Pass",    "$1.99/mo"),
]


def read_text(path, default=""):
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return default


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name")
    args = ap.parse_args()

    app_name = args.app_name
    app_dir = REPO_ROOT / app_name
    if not app_dir.is_dir():
        print(f"ERROR: app directory not found: {app_dir}")
        sys.exit(1)

    lowername = app_name.lower().replace("_", "").replace("-", "")

    # Pull values from metadata files
    title         = read_text(app_dir / "metadata/en-US/title.txt", app_name)
    short_desc    = read_text(app_dir / "metadata/en-US/short_description.txt")
    full_desc     = read_text(app_dir / "metadata/en-US/full_description.txt")
    keywords      = read_text(app_dir / "metadata/en-US/keywords.txt")
    release_notes = read_text(app_dir / "metadata/en-US/release_notes.txt")
    app_info      = read_json(app_dir / "metadata/app_info.json")
    iaps_meta     = read_json(app_dir / "metadata/iaps.json", default=[])

    category = app_info.get("category_google", "GAME_PUZZLE")
    contains_ads = app_info.get("contains_ads", True)
    contains_iap = app_info.get("contains_iap", True)
    target_age = app_info.get("target_audience_min_age", 13)

    # Phone screenshots count
    phone_dir = app_dir / "store/screenshots/phone"
    phone_count = (len([f for f in phone_dir.iterdir() if f.suffix == ".png"])
                   if phone_dir.is_dir() else 0)

    # Tablet screenshots
    tablet_7 = app_dir / "store/screenshots/tablet_7"
    tablet_10 = app_dir / "store/screenshots/tablet_10"
    tablet_7_count = (len([f for f in tablet_7.iterdir() if f.suffix == ".png"])
                      if tablet_7.is_dir() else 0)
    tablet_10_count = (len([f for f in tablet_10.iterdir() if f.suffix == ".png"])
                       if tablet_10.is_dir() else 0)

    # Build IAP table from metadata or fallback to defaults
    iap_rows = []
    if iaps_meta and isinstance(iaps_meta, list):
        for entry in iaps_meta:
            iap_rows.append((
                f"{lowername}_{entry.get('id', '')}",
                entry.get("type", "Managed").capitalize(),
                entry.get("name", ""),
                entry.get("price", ""),
            ))
    else:
        for slug, type_, name, price in DEFAULT_IAPS:
            iap_rows.append((f"{lowername}_{slug}", type_, name, price))

    # Build the document
    doc = f"""# Release Handoff — {title}

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## Step 1 — Create AdMob app entry (5 min)

URL: https://apps.admob.com/v2/apps/list

Click **Add app** → choose **Android** → "No, the app isn't published yet"
(switch to "Yes" once on Play Store).

Fill in:
- **App name:** `{title}`
- **App store:** Google Play (or "Not yet listed" if pre-publish)
- **User metrics:** Yes / Yes / Yes (all enabled)

Click **Add**. AdMob shows you a new APPLICATION ID like
`ca-app-pub-5695494884863768~XXXXXXXXXX`.

**Copy it.** Paste into:
```
{app_name}/android/app/src/main/AndroidManifest.xml
```
Search for: `__ADMOB_APP_ID_PLACEHOLDER__`
Replace with: the new APPLICATION ID.

Then in AdMob, **Apps → {title} → Ad units → Add ad unit**, create three:

| Name | Format |
|---|---|
| `{lowername}_banner` | Banner |
| `{lowername}_interstitial` | Interstitial |
| `{lowername}_rewarded` | Rewarded |

Each gives an ad unit ID like `ca-app-pub-5695494884863768/XXXXXXXXXX`.
Copy all three. Paste into:
```
{app_name}/android/app/src/main/java/com/pegasusgames/{lowername}/MainActivity.java
```
Replace these constants:
```java
BANNER_AD_UNIT_ID       = "<paste banner ID>";
INTERSTITIAL_AD_UNIT_ID = "<paste interstitial ID>";
REWARDED_AD_UNIT_ID     = "<paste rewarded ID>";
```

---

## Step 2 — Create Play Console app entry (5 min)

URL: https://play.google.com/console (use the org account, NOT personal)

Click **Create app**. Fill in:
- **App name:** `{title}`
- **Default language:** English (United States)
- **App or game:** Game
- **Free or paid:** Free
- **Declarations:** ✓ developer program policies, ✓ US export laws

Click **Create app**. You're now on the app's dashboard.

---

## Step 3 — Create the {len(iap_rows)} IAP products (10 min)

Play Console → {title} → **Monetize → Products → In-app products**.

Click **Create product** for each row below. Activate after creating
(default state is Inactive).

| Product ID | Type | Name | Default price |
|---|---|---|---|
"""
    for pid, ptype, pname, price in iap_rows:
        doc += f"| `{pid}` | {ptype} | {pname} | {price} |\n"

    doc += f"""
---

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → {title} → **Grow → Main store listing**.

**App name:**
```
{title}
```

**Short description (80 chars):**
```
{short_desc}
```

**Full description:**
Open `{app_name}/metadata/en-US/full_description.txt` and paste the
entire contents.

**Graphics:**
- App icon → upload `{app_name}/store/icon_512_playstore.png`
- Feature graphic → upload `{app_name}/store/feature_graphic_1024x500.png`
- Phone screenshots → upload all {phone_count} files in `{app_name}/store/screenshots/phone/`
- 7-inch tablet → upload {tablet_7_count} file(s) in `{app_name}/store/screenshots/tablet_7/`
- 10-inch tablet → upload {tablet_10_count} file(s) in `{app_name}/store/screenshots/tablet_10/`

If Play Console rejects 2 tablet screenshots (Google requires min 4),
open `{app_name}/wrap_tablet_screenshots.py`, uncomment the lines under
`EXTRA_SCREENSHOTS`, re-run, re-upload.

**Categorization:**
- App category: `{category}`
- Tags: pull from `{app_name}/metadata/en-US/keywords.txt`

---

## Step 5 — Fill in policy & declarations (5 min)

Play Console → {title} → **Policy → App content**.

### App access
"All functionality is available without restrictions" → **Yes**

### Ads
- Contains ads: **Yes**

### Content rating questionnaire
Click **Start questionnaire**. Fill in:
- Email: `{CANONICAL_EMAIL}`
- Category: **Game**
- Answer all questions: **No** (no violence, no sexual content,
  no profanity, no gambling, no UGC, no location sharing, no controlled
  substances)
- Submit. Wait for IARC ratings.

### Target audience and content
- Target age groups: **13–15, 16–17, 18+** (general-audience puzzle game)
- "Does your app unintentionally appeal to children?": **No**

### News apps / Government apps / COVID-19 / Financial / Health
All: **No**.

### Data safety
Click **Start**. Answers:
- Does your app collect or share any of the required user data types? **Yes**
- Is all of the user data collected by your app encrypted in transit? **Yes**
- Do you provide a way for users to request that their data is deleted? **Yes**

Data types collected:
- **App activity → App interactions** — Optional, Analytics
- **App info and performance → Crash logs** — Optional, Analytics + App functionality
- **App info and performance → Diagnostics** — Optional, Analytics
- **App info and performance → Other app performance data** — Optional, Analytics
- **Device or other IDs → Device ID** — Optional, Advertising/marketing + Analytics, **also marked Shared with third parties**

Submit.

### Advertising ID declaration
Yes — used for **Advertising or marketing** + **Analytics**.

### Privacy policy
URL: `{CANONICAL_PRIVACY}`

### Developer contact
Email: `{CANONICAL_EMAIL}`
Website: `{CANONICAL_SUPPORT}`

---

## Step 6 — Re-build the AAB with real AdMob IDs (3 min)

Now that Step 1 gave you real AdMob IDs and you've pasted them into the
manifest and MainActivity.java, rebuild:

```
python3 build_release.py {app_name}
```

Output AAB will be at:
```
{app_name}/android/app/build/outputs/bundle/release/app-release.aab
```

The script verifies the AdMob ID is no longer the placeholder and that
the AAB is signed and complete.

---

## Step 7 — Upload the AAB (2 min)

Play Console → {title} → **Test and release → Production → Create new release → Upload**.

Drag in `app-release.aab`. Add release notes:
```
{release_notes}
```

Save → **Review release** → **Start rollout to Production**.

First-time review: **3–7 days**. Subsequent updates: usually under 24 hours.

---

You're done. Game is in review.

---

## If anything goes wrong

- **AAB upload fails with "signed by different certificate":** the
  upload key registered for this app slot doesn't match this AAB's
  signing key. Check Play Console → App integrity → App signing.
- **AdMob ad units not showing in app:** wait 24 hours after creating
  ad units (AdMob's caches take time to propagate), and confirm app is
  on Play Store under the same package name as in AdMob's "App store"
  setting.
- **IAP products not visible in app:** confirm products are Active in
  Play Console (not just Created), and that the app's package name in
  the AAB matches the package the products were created under.
- **Store listing rejected for screenshot text:** check that no
  screenshot text uses banned phrases (#1, Best, Top Rated, Download
  Now, % Off, etc. — see QUALITY_PLAYBOOK.md §7.2).
"""

    out_path = app_dir / "RELEASE_HANDOFF.md"
    out_path.write_text(doc)
    print(f"✓ Wrote {out_path}")
    print(f"  ({len(iap_rows)} IAP products, {phone_count} phone screenshots)")


if __name__ == "__main__":
    main()
