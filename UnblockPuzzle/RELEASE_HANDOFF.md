# Release Handoff — Unblock Puzzle

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## Step 1 — Create AdMob app entry under canonical Pegasus Games account (5 min)

> ⚠️ **The code currently has stale AdMob IDs from publisher
> `2759523698880843` (an old account). The canonical Pegasus Games account
> used by WaterSort is publisher `5695494884863768`. Swap to the canonical
> account before publish.**

URL: https://apps.admob.com/v2/apps/list

Click **Add app** → choose **Android** → "No, the app isn't published yet"
(switch to "Yes" once on Play Store).

Fill in:
- **App name:** `Unblock Puzzle`
- **App store:** Google Play (or "Not yet listed" if pre-publish)
- **User metrics:** Yes / Yes / Yes (all enabled)

Click **Add**. AdMob shows you a new APPLICATION ID like
`ca-app-pub-5695494884863768~XXXXXXXXXX`.

**Copy it.** Paste into:
```
UnblockPuzzle/android/app/src/main/AndroidManifest.xml
```
Replace `ca-app-pub-2759523698880843~3555759989` with the new APPLICATION ID.

Then in AdMob, **Apps → Unblock Puzzle → Ad units → Add ad unit**, create three:

| Name | Format |
|---|---|
| `unblockpuzzle_banner` | Banner |
| `unblockpuzzle_interstitial` | Interstitial |
| `unblockpuzzle_rewarded` | Rewarded |

Each gives an ad unit ID like `ca-app-pub-5695494884863768/XXXXXXXXXX`.
Copy all three. Paste into:
```
UnblockPuzzle/android/app/src/main/java/com/pegasusgames/unblock/MainActivity.java
```
Replace these constants (currently still pointing at the old publisher
`2759523698880843`):
```java
ADMOB_BANNER_UNIT_ID       = "<paste banner ID>";
ADMOB_INTERSTITIAL_UNIT_ID = "<paste interstitial ID>";
ADMOB_REWARDED_UNIT_ID     = "<paste rewarded ID>";
```

---

## Step 2 — Create Play Console app entry (5 min)

URL: https://play.google.com/console (use the org account, NOT personal)

Click **Create app**. Fill in:
- **App name:** `Unblock Puzzle`
- **Default language:** English (United States)
- **App or game:** Game
- **Free or paid:** Free
- **Declarations:** ✓ developer program policies, ✓ US export laws

Click **Create app**. You're now on the app's dashboard.

---

## Step 3 — Create the 9 IAP products (10 min)

Play Console → Unblock Puzzle → **Monetize → Products → In-app products**.

Click **Create product** for each row below. Activate after creating
(default state is Inactive).

| Product ID | Type | Name | Default price |
|---|---|---|---|
| `unblockpuzzle_remove_ads` | Managed | Remove Ads | $1.99 |
| `unblockpuzzle_coins_small` | Managed | 100 Coins | $0.99 |
| `unblockpuzzle_coins_medium` | Managed | 500 Coins | $3.99 |
| `unblockpuzzle_coins_large` | Managed | 1200 Coins | $7.99 |
| `unblockpuzzle_coins_huge` | Managed | 3000 Coins | $14.99 |
| `unblockpuzzle_starter_pack` | Managed | Starter Pack | $0.99 |
| `unblockpuzzle_premium_themes` | Managed | Premium Themes | $2.99 |
| `unblockpuzzle_hint_pack` | Managed | Hint Pack | $1.99 |
| `unblockpuzzle_season_pass_monthly` | Subscription | Monthly Pass | $1.99/mo |

---

## Step 3.5 — Paste the IAP license public key (1 min) **REQUIRED**

Play Console → Unblock Puzzle → **Monetize → Monetization setup → Licensing**.

Copy the **Base64-encoded RSA public key** (one long ~390-char string).

Paste into:
```
UnblockPuzzle/android/app/src/main/java/com/pegasusgames/unblock/MainActivity.java
```
Replace the constant:
```java
private static final String LICENSE_PUBLIC_KEY = "PASTE_LICENSE_KEY_FROM_PLAY_CONSOLE_MONETIZE_LICENSING";
```
…with the real key. Without this, IAP signature verification is skipped
and the app is vulnerable to IAP-faker tools (Lucky Patcher, etc.). The
build script `pre_publish_check.py` blocks the build until this is real.

---

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → Unblock Puzzle → **Grow → Main store listing**.

**App name:**
```
Unblock Puzzle
```

**Short description (80 chars):**
```
Slide blocks to free the red piece! Classic addictive sliding puzzle.
```

**Full description:**
Open `UnblockPuzzle/metadata/en-US/full_description.txt` and paste the
entire contents.

**Graphics:**
- App icon → upload `UnblockPuzzle/store/icon_512_playstore.png`
- Feature graphic → upload `UnblockPuzzle/store/feature_graphic_1024x500.png`
- Phone screenshots → upload all 3 files in `UnblockPuzzle/store/screenshots/phone/`
- 7-inch tablet → upload 1 file(s) in `UnblockPuzzle/store/screenshots/tablet_7/`
- 10-inch tablet → upload 1 file(s) in `UnblockPuzzle/store/screenshots/tablet_10/`

If Play Console rejects 2 tablet screenshots (Google requires min 4),
open `UnblockPuzzle/wrap_tablet_screenshots.py`, uncomment the lines under
`EXTRA_SCREENSHOTS`, re-run, re-upload.

**Categorization:**
- App category: `GAME_PUZZLE`
- Tags: pull from `UnblockPuzzle/metadata/en-US/keywords.txt`

---

## Step 5 — Fill in policy & declarations (5 min)

Play Console → Unblock Puzzle → **Policy → App content**.

### App access
"All functionality is available without restrictions" → **Yes**

### Ads
- Contains ads: **Yes**

### Content rating questionnaire
Click **Start questionnaire**. Fill in:
- Email: `pegasusgames@atomicmail.io`
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
URL: `https://pegasusgames-creator.github.io/privacy.html`

### Developer contact
Email: `pegasusgames@atomicmail.io`
Website: `https://pegasusgames-creator.github.io/`

---

## Step 6 — Re-build the AAB with real AdMob IDs (3 min)

Now that Step 1 gave you real AdMob IDs and you've pasted them into the
manifest and MainActivity.java, rebuild:

```
python3 scripts/build_release.py UnblockPuzzle
```

Output AAB will be at:
```
UnblockPuzzle/android/app/build/outputs/bundle/release/app-release.aab
```

The script verifies the AdMob ID is no longer the placeholder and that
the AAB is signed and complete.

---

## Step 7 — Upload the AAB (2 min)

Play Console → Unblock Puzzle → **Test and release → Production → Create new release → Upload**.

Drag in `app-release.aab`. Add release notes:
```
Initial release.
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
