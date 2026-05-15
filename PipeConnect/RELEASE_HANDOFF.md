# Release Handoff — Pipe Connect

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## ⚠️ CRITICAL: AdMob IDs are TEST IDs, not real

The AAB at
`PipeConnect/android/app/build/outputs/bundle/release/app-release.aab`
was built with **Google's official test AdMob IDs** so the app
launches cleanly for screenshot capture and smoke-testing:

- App ID         `ca-app-pub-3940256099942544~3347511713`
- Banner         `ca-app-pub-3940256099942544/6300978111`
- Interstitial   `ca-app-pub-3940256099942544/1033173712`
- Rewarded       `ca-app-pub-3940256099942544/5224354917`

**DO NOT upload this AAB to Play production.** Test ads pay nothing.
Follow **Step 1** below to create real IDs, paste them in, then
rebuild the AAB via **Step 6** before uploading.

---

## Step 1 — Create the AdMob app entry (5 min)

URL: https://apps.admob.com/v2/apps/list

Click **Add app** → Android → "No, the app isn't published yet"
(switch to "Yes" once the Play listing exists).

Fill in:
- **App name:** `Pipe Connect`
- **App store:** Google Play (or Not yet listed if pre-publish)
- **User metrics:** Yes / Yes / Yes (recommended for casual games)

Click **Add**. AdMob will show a new APPLICATION ID like
`ca-app-pub-5695494884863768~XXXXXXXXXX`. **Copy that.** Then in
`PipeConnect/android/app/src/main/AndroidManifest.xml`, replace:

```
ca-app-pub-3940256099942544~3347511713
```

with your new APPLICATION ID.

Create 3 ad units (Apps → Pipe Connect → Ad units → Add ad unit):

| Name | Type |
|---|---|
| `PipeConnect_banner`        | Banner |
| `PipeConnect_interstitial`  | Interstitial |
| `PipeConnect_rewarded`      | Rewarded |

Each gives an ad unit ID like `ca-app-pub-…/XXXXXXXXXX`. Paste them
into
`PipeConnect/android/app/src/main/java/com/pegasusgames/pipeconnect/MainActivity.java`,
replacing the three `ca-app-pub-3940256099942544/…` test unit IDs
(`ADMOB_BANNER_UNIT_ID`, `ADMOB_INTERSTITIAL_UNIT_ID`,
`ADMOB_REWARDED_UNIT_ID`).

---

## Step 2 — Create Play Console app entry (5 min)

URL: https://play.google.com/console (use the org account, NOT personal)

Click **Create app**. Fill in:
- **App name:** `Pipe Connect`
- **Default language:** English (United States)
- **App or game:** Game
- **Free or paid:** Free
- **Declarations:** ✓ developer program policies, ✓ US export laws

Click **Create app**. You're now on the app's dashboard.

---

## Step 3 — Create the 12 IAP products (10 min)

Play Console → Pipe Connect → **Monetize → Products → In-app products**.

Click **Create product** for each row below. Activate after creating
(default state is Inactive).

| Product ID | Type | Name | Default price |
|---|---|---|---|
| `remove_ads` | Managed | Remove Ads | $2.99 |
| `coins_small` | Managed | 100 Coins | $0.99 |
| `coins_medium` | Managed | 400 Coins | $2.99 |
| `coins_large` | Managed | 800 Coins | $4.99 |
| `coins_mega` | Managed | 2000 Coins | $9.99 |
| `five_lives` | Managed | 5 Lives | $0.99 |
| `unlimited_lives_1h` | Managed | 1hr Unlimited | $1.99 |
| `unlimited_lives_forever` | Managed | Unlimited Lives | $4.99 |
| `hint_pack` | Managed | Hint Pack | $1.99 |
| `starter_pack` | Managed | Starter Pack | $0.99 |
| `season_pass_monthly` | Subscription | Season Pass | $4.99/mo |
| `weekly_pass` | Subscription | Weekly Pass | $1.99/wk |

---

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → Pipe Connect → **Grow → Main store listing**.

**App name:**
```
Pipe Connect
```
The app name is shared across ALL locales (English globally per Pegasus
Games policy — see TRANSLATIONS.md §3).

**Short description (English baseline, 80 chars):**
```
Connect the colored pipes and fill the grid! Relaxing logic puzzle.
```

**Full description (English baseline):**
Open `PipeConnect/metadata/en-US/full_description.txt` and paste the
entire contents.

**Graphics:**
- App icon → upload `PipeConnect/store/icon_512_playstore.png`
- Feature graphic → upload `PipeConnect/store/feature_graphic_1024x500.png`
- Phone screenshots → upload all 7 files in `PipeConnect/store/screenshots/phone/`
- 7-inch tablet → upload 2 file(s) in `PipeConnect/store/screenshots/tablet_7/`
- 10-inch tablet → upload 2 file(s) in `PipeConnect/store/screenshots/tablet_10/`

If Play Console rejects 2 tablet screenshots (Google requires min 4),
open `PipeConnect/wrap_tablet_screenshots.py`, uncomment the lines under
`EXTRA_SCREENSHOTS`, re-run, re-upload.

**Categorization:**
- App category: `GAME_PUZZLE`
- Tags: pull from `PipeConnect/metadata/en-US/keywords.txt`

### 4.1 — Add localizations (10 min, repetitive but mechanical)

Pegasus Games ships in 11 locales. After saving the English baseline
above, scroll up to **Manage translations → Add your own translations**.

Add these 10 locales one at a time:

| Locale | Source folder |
|---|---|
| Arabic | `PipeConnect/metadata/ar/` |
| German (Germany) | `PipeConnect/metadata/de-DE/` |
| Spanish (Latin America) | `PipeConnect/metadata/es-419/` |
| French (France) | `PipeConnect/metadata/fr-FR/` |
| Hindi (India) | `PipeConnect/metadata/hi-IN/` |
| Indonesian | `PipeConnect/metadata/id/` |
| Italian (Italy) | `PipeConnect/metadata/it-IT/` |
| Japanese (Japan) | `PipeConnect/metadata/ja-JP/` |
| Portuguese (Brazil) | `PipeConnect/metadata/pt-BR/` |
| Turkish (Turkey) | `PipeConnect/metadata/tr-TR/` |
| Ukrainian | `PipeConnect/metadata/uk/` |
| Chinese (Simplified) | `PipeConnect/metadata/zh-CN/` |

For each locale:
1. Click **Add language**, pick from the list above
2. Paste the contents of `<locale>/short_description.txt` into "Short description"
3. Paste `<locale>/full_description.txt` into "Full description"
4. Leave the title field empty or paste the English title verbatim
   (per TRANSLATIONS.md §3 — title stays English globally)
5. Reuse the same icon, feature graphic, and screenshots — they're
   not localized (English text in screenshots is fine; users in
   non-English markets are accustomed to it on Play Store)
6. Save

If any locale's `*.rejected` file exists in metadata/, that means
machine translation overflowed character limits. Edit the file down
to fit, rename to remove `.rejected`, then upload.

For Kids apps: only 4 locales required (en-US, es-419, pt-BR, fr-FR).
Each MUST have been reviewed by a native speaker — verify no
"# KIDS APP — REVIEW BY NATIVE SPEAKER" header remains in any file.

---

## Step 5 — Fill in policy & declarations (5 min)

Play Console → Pipe Connect → **Policy → App content**.

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
python3 build_release.py PipeConnect
```

Output AAB will be at:
```
PipeConnect/android/app/build/outputs/bundle/release/app-release.aab
```

The script verifies the AdMob ID is no longer the placeholder and that
the AAB is signed and complete.

---

## Step 7 — Upload the AAB (2 min)

Play Console → Pipe Connect → **Test and release → Production → Create new release → Upload**.

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
