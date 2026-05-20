# Release Handoff — 2048 Puzzle

This is what YOU need to do manually before the AAB can be uploaded.
Everything else is already built. Estimated time: **20–30 minutes**.

Each step has all values pre-filled — paste, don't type.

---

## Step 1 — AdMob app entry (already done)

This app's AdMob app ID and ad unit IDs are already baked into
`Puzzle2048/android/app/src/main/AndroidManifest.xml` and
`Puzzle2048/android/app/src/main/java/com/pegasusgames/puzzle2048/MainActivity.java`.
**Skip directly to Step 2** unless you need to recreate the
AdMob entry from scratch (in which case follow the manual steps
in older handoff docs).

---

## Step 2 — Create Play Console app entry (5 min)

URL: https://play.google.com/console (use the org account, NOT personal)

Click **Create app**. Fill in:
- **App name:** `2048 Puzzle`
- **Default language:** English (United States)
- **App or game:** Game
- **Free or paid:** Free
- **Declarations:** ✓ developer program policies, ✓ US export laws

Click **Create app**. You're now on the app's dashboard.

---

## Step 3 — Create the 12 IAP products (10 min)

Play Console → 2048 Puzzle → **Monetize → Products → In-app products**.

Click **Create product** for each row below. Activate after creating
(default state is Inactive).

| Product ID | Type | Name | Default price |
|---|---|---|---|
| `remove_ads` | Managed | Remove Ads | $2.99 |
| `coins_small` | Managed | 100 Coins | $0.99 |
| `coins_large` | Managed | 800 Coins | $4.99 |
| `coins_medium` | Managed | 400 Coins | $2.99 |
| `coins_mega` | Managed | 2000 Coins | $9.99 |
| `five_lives` | Managed | 5 Lives | $0.99 |
| `unlimited_lives_1h` | Managed | 1hr Unlimited | $1.99 |
| `unlimited_lives_forever` | Managed | Unlimited Lives | $4.99 |
| `undo_pack` | Managed | Undo Pack (10) | $0.99 |
| `starter_pack` | Managed | Starter Pack | $0.99 |
| `season_pass_monthly` | Subscription | Season Pass | $4.99/mo |
| `weekly_pass` | Subscription | Weekly Pass | $1.99/wk |

---

## Step 4 — Fill in store listing (5 min, mostly copy-paste)

Play Console → 2048 Puzzle → **Grow → Main store listing**.

**App name:**
```
2048 Puzzle
```
The app name is shared across ALL locales (English globally per Pegasus
Games policy — see TRANSLATIONS.md §3).

**Short description (English baseline, 80 chars):**
```
Classic 4×4 2048 board. Daily challenge, weekly event, undo. Plays offline.
```

**Full description (English baseline):**
Open `Puzzle2048/metadata/en-US/full_description.txt` and paste the
entire contents.

**Graphics:**
- App icon → upload `Puzzle2048/store/icon_512_playstore.png`
- Feature graphic → upload `Puzzle2048/store/feature_graphic_1024x500.png`
- Phone screenshots → upload all 7 files in `Puzzle2048/store/screenshots/phone/`
- 7-inch tablet → upload 7 file(s) in `Puzzle2048/store/screenshots/tablet_7/`
- 10-inch tablet → upload 7 file(s) in `Puzzle2048/store/screenshots/tablet_10/`

If Play Console rejects 2 tablet screenshots (Google requires min 4),
open `Puzzle2048/wrap_tablet_screenshots.py`, uncomment the lines under
`EXTRA_SCREENSHOTS`, re-run, re-upload.

**Categorization:**
- App category: `GAME_PUZZLE`
- Tags: pull from `Puzzle2048/metadata/en-US/keywords.txt`

### 4.1 — Add localizations (10 min, repetitive but mechanical)

Pegasus Games ships in 11 locales. After saving the English baseline
above, scroll up to **Manage translations → Add your own translations**.

Add these 10 locales one at a time:

| Locale | Source folder |
|---|---|
| Arabic | `Puzzle2048/metadata/ar/` |
| German (Germany) | `Puzzle2048/metadata/de-DE/` |
| Spanish (Latin America) | `Puzzle2048/metadata/es-419/` |
| French (France) | `Puzzle2048/metadata/fr-FR/` |
| Hindi (India) | `Puzzle2048/metadata/hi-IN/` |
| Indonesian | `Puzzle2048/metadata/id/` |
| Italian (Italy) | `Puzzle2048/metadata/it-IT/` |
| Japanese (Japan) | `Puzzle2048/metadata/ja-JP/` |
| Portuguese (Brazil) | `Puzzle2048/metadata/pt-BR/` |
| Turkish (Turkey) | `Puzzle2048/metadata/tr-TR/` |
| Ukrainian | `Puzzle2048/metadata/uk/` |
| Chinese (Simplified) | `Puzzle2048/metadata/zh-CN/` |

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

Play Console → 2048 Puzzle → **Policy → App content**.

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
python3 build_release.py Puzzle2048
```

Output AAB will be at:
```
Puzzle2048/android/app/build/outputs/bundle/release/app-release.aab
```

The script verifies the AdMob ID is no longer the placeholder and that
the AAB is signed and complete.

---

## Step 7 — Upload the AAB (2 min)

Play Console → 2048 Puzzle → **Test and release → Production → Create new release → Upload**.

Drag in `app-release.aab`. Add release notes:
```
• Bigger coin packs — M 400 · L 800 · XL 2000; Weekly Pass now $1.99/week
• Starter Pack grants 5 undos and 5 lives
• Season Pass: +100 daily coins (was +50), all themes, unlimited undos; Weekly +50
• Magic Merge and Remove Tile boosters
• Weekly Tournament bracket
• Seasonal events
• Free Coins button
• Continue · current run
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
