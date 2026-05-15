# Release Handoff — Flappy Wings — Tap to Fly

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## ⚠️ CRITICAL: AdMob ID is a TEST ID; AppLovin is DISABLED

The AAB at
`FlappyBird/android/app/build/outputs/bundle/release/app-release.aab`
was built with:

- **Google's official test AdMob App ID** (`ca-app-pub-3940256099942544~3347511713`)
  in `AndroidManifest.xml` so the app launches and the AppLovin/AdMob
  mediation adapter doesn't crash on init.
- **AppLovin SDK key + 3 MAX unit IDs** zeroed out — when empty, the
  in-app `if (!MAX_SDK_KEY.isEmpty())` guard skips AppLovin init
  entirely. The app runs ad-free.

**DO NOT upload this AAB to Play production.** Test ads pay nothing
and ad-free with no AppLovin pays nothing either. Follow **Step 1**
below to set up real ad serving, paste IDs in, then rebuild the AAB
via **Step 6** before uploading.

---

## Step 1 — Set up ads (5–15 min depending on path)

This app was built around AppLovin MAX as the primary ad network with
AdMob as a mediation source. You have two paths:

### Path A — Stay on AppLovin MAX (recommended, matches current code)

1. Go to https://dash.applovin.com/account → copy your **MAX SDK Key**.
2. Apply for / verify your AppLovin app entry at
   https://dash.applovin.com/o/applications. Get 3 unit IDs:
   `flappybird_banner`, `flappybird_interstitial`, `flappybird_rewarded`.
3. Paste into
   `FlappyBird/android/app/src/main/java/com/pegasusgames/flappybird/MainActivity.java`:
   - `MAX_SDK_KEY` (currently `""`)
   - `BANNER_AD_UNIT_ID`, `INTERSTITIAL_AD_UNIT_ID`, `REWARDED_AD_UNIT_ID`
4. Re-add the `applovin.sdk.key` meta-data in
   `FlappyBird/android/app/src/main/AndroidManifest.xml` with the real key.
5. In AdMob, create an app entry too (the mediation adapter needs an
   AdMob App ID). Paste it into the manifest replacing the test ID
   `ca-app-pub-3940256099942544~3347511713`.

### Path B — Switch to AdMob-only

Easier if you don't have AppLovin approved yet. Create an AdMob app +
3 ad units at https://apps.admob.com/v2/apps/list, paste APP ID and
3 unit IDs in. Then strip the AppLovin SDK init block out of
`MainActivity.java` (or leave it — with empty key the guard already
skips it) and wire up AdMob's `MobileAds.initialize()` + load the
ads directly. This requires writing the AdMob ad code (banner +
interstitial + rewarded loaders) — match the pattern from
WaterSort/Nonogram/PipeConnect's `MainActivity.java`.

The 5 already-shipped flagships all use AdMob-only, so Path B keeps
FlappyBird consistent with the rest of the portfolio.

---

## Step 2 — Create Play Console app entry (5 min)

URL: https://play.google.com/console (use the org account, NOT personal)

Click **Create app**. Fill in:
- **App name:** `Flappy Wings — Tap to Fly`
- **Default language:** English (United States)
- **App or game:** Game
- **Free or paid:** Free
- **Declarations:** ✓ developer program policies, ✓ US export laws

Click **Create app**. You're now on the app's dashboard.

---

## Step 3 — Create the 5 IAP products (10 min)

Play Console → Flappy Wings — Tap to Fly → **Monetize → Products → In-app products**.

Click **Create product** for each row below. Activate after creating
(default state is Inactive).

| Product ID | Type | Name | Default price |
|---|---|---|---|
| `remove_ads` | Managed | Remove Ads | $2.99 |
| `coins_small` | Managed | 100 Coins | $0.99 |
| `coins_medium` | Managed | 400 Coins | $2.99 |
| `coins_large` | Managed | 800 Coins | $4.99 |
| `coins_mega` | Managed | 2000 Coins | $9.99 |

---

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → Flappy Wings — Tap to Fly → **Grow → Main store listing**.

**App name:**
```
Flappy Wings — Tap to Fly
```
The app name is shared across ALL locales (English globally per Pegasus
Games policy — see TRANSLATIONS.md §3).

**Short description (English baseline, 80 chars):**
```
Tap to flap through pipes. Unlock bird skins, earn medals.
```

**Full description (English baseline):**
Open `FlappyBird/metadata/en-US/full_description.txt` and paste the
entire contents.

**Graphics:**
- App icon → upload `FlappyBird/store/icon_512_playstore.png`
- Feature graphic → upload `FlappyBird/store/feature_graphic_1024x500.png`
- Phone screenshots → upload all 7 files in `FlappyBird/store/screenshots/phone/`
- 7-inch tablet → upload 2 file(s) in `FlappyBird/store/screenshots/tablet_7/`
- 10-inch tablet → upload 2 file(s) in `FlappyBird/store/screenshots/tablet_10/`

If Play Console rejects 2 tablet screenshots (Google requires min 4),
open `FlappyBird/wrap_tablet_screenshots.py`, uncomment the lines under
`EXTRA_SCREENSHOTS`, re-run, re-upload.

**Categorization:**
- App category: `GAME_ARCADE`
- Tags: pull from `FlappyBird/metadata/en-US/keywords.txt`

### 4.1 — Add localizations (10 min, repetitive but mechanical)

Pegasus Games ships in 11 locales. After saving the English baseline
above, scroll up to **Manage translations → Add your own translations**.

Add these 10 locales one at a time:

| Locale | Source folder |
|---|---|
| Arabic | `FlappyBird/metadata/ar/` |
| German (Germany) | `FlappyBird/metadata/de-DE/` |
| Spanish (Latin America) | `FlappyBird/metadata/es-419/` |
| French (France) | `FlappyBird/metadata/fr-FR/` |
| Hindi (India) | `FlappyBird/metadata/hi-IN/` |
| Indonesian | `FlappyBird/metadata/id/` |
| Italian (Italy) | `FlappyBird/metadata/it-IT/` |
| Japanese (Japan) | `FlappyBird/metadata/ja-JP/` |
| Portuguese (Brazil) | `FlappyBird/metadata/pt-BR/` |
| Turkish (Turkey) | `FlappyBird/metadata/tr-TR/` |
| Ukrainian | `FlappyBird/metadata/uk/` |
| Chinese (Simplified) | `FlappyBird/metadata/zh-CN/` |

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

Play Console → Flappy Wings — Tap to Fly → **Policy → App content**.

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
python3 build_release.py FlappyBird
```

Output AAB will be at:
```
FlappyBird/android/app/build/outputs/bundle/release/app-release.aab
```

The script verifies the AdMob ID is no longer the placeholder and that
the AAB is signed and complete.

---

## Step 7 — Upload the AAB (2 min)

Play Console → Flappy Wings — Tap to Fly → **Test and release → Production → Create new release → Upload**.

Drag in `app-release.aab`. Add release notes:
```
• 6 unlockable bird characters with unique colour designs
• Medal system: Starter, Bronze, Silver, Gold tiers
• Score history: last 10 runs saved automatically
• Day/night sky cycle during gameplay
• Particle burst on each pipe scored
• Screen shake on death
• Coin collection in pipe gaps
• Bird skin shop with coin unlock system
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
