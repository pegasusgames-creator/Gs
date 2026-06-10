# Release Handoff — Pipe Connect

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## ✅ Step 1 — AdMob: DONE (2026-06-10)

Real AdMob IDs are wired into the code and baked into the AAB:

- App ID         `ca-app-pub-5695494884863768~3214881924`
- Banner         `ca-app-pub-5695494884863768/5765562640`
- Interstitial   `ca-app-pub-5695494884863768/6329006131`
- Rewarded       `ca-app-pub-5695494884863768/7889499819`

Nothing left to do here. The AAB at
`PipeConnect/android/app/build/outputs/bundle/release/app-release.aab`
is the one to upload.

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

## ✅ Step 6 — Rebuild with real AdMob IDs: DONE (2026-06-10)

The release AAB was rebuilt after the real IDs were pasted in, is
signed with PipeConnect's dedicated keystore
(SHA1 `9A:DA:7D:B4:D1:4A:93:C6:4C:D3:85:2D:6D:58:1E:40:0F:E7:A5:36`),
and contains zero test AdMob IDs:

```
PipeConnect/android/app/build/outputs/bundle/release/app-release.aab
```

---

## Step 6.5 — Publish the Play Games leaderboard (2 min)

The leaderboard **"Highest Level Cleared in Pipe Connect"**
(`CgkIg4KVn8kGEAIQCA`, PGS project `225819574531`) exists but is in
**Draft**. In Play Console → Grow → Play Games Services →
Setup and management → Leaderboards, open it and click **Publish**
(it already shows "ready to publish"). Also confirm the PipeConnect
credential (`com.pegasusgames.pipeconnect`) is added under
PGS → Configuration → Credentials, same as the other 4 apps.

Until published, the in-game Ranks sheet just uses the synthetic
weekly standings (by design), so this is not a launch blocker.

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
