# Shared Setup — All 6 Pegasus Games

## AdMob App IDs

| Game | Package ID | AdMob App ID |
|---|---|---|
| Ball Sort Puzzle | com.pegasusgames.ballsort | ca-app-pub-2759523698880843~9194379298 |
| Nonogram Puzzle | com.pegasusgames.nonogram | ca-app-pub-2759523698880843~8865461839 |
| Pipe Connect | com.pegasusgames.pipeconnect | ca-app-pub-2759523698880843~3090390974 |
| 2048 Puzzle | com.pegasusgames.puzzle2048 | ca-app-pub-2759523698880843~3659701763 |
| Unblock Puzzle | com.pegasusgames.unblockpuzzle | ca-app-pub-2759523698880843~3555759989 |
| Water Sort Puzzle | com.pegasusgames.watersortpuzzle | ca-app-pub-5695494884863768~4951744270 |

---

## AdMob Setup (do once per app at apps.admob.com)

1. Add app or select existing
2. Create 3 ad units per app:
   - **banner** — Banner / Adaptive — bottom of game screen
   - **interstitial** — Interstitial — shown when returning to menu
   - **rewarded** — Rewarded — "Watch ad for life/hint/skip" buttons
3. Copy the 3 Ad Unit IDs into MainActivity where showBannerAd / showInterstitial / showRewarded are called
4. Verify App ID matches AndroidManifest.xml
5. Add payment profile if not done: Payments → Add payment method
6. After first AAB is uploaded to Play Console, come back and link: AdMob → Apps → Link to Play Store
7. Use test ad unit IDs in debug builds until linked to avoid invalid traffic flags

---

## IAPs Common to All 6 Games

Create these in Play Console → Monetize → Products → In-app products for EVERY app:

### One-time products

| Product ID | Price | Title | Description |
|---|---|---|---|
| remove_ads | $2.99 | Remove Ads | Enjoy ad-free gameplay forever |
| coins_small | $0.99 | 100 Coins | Small coin pack |
| coins_large | $2.99 | 500 Coins | Best value coin pack |
| five_lives | $0.99 | 5 Lives | Restore 5 lives instantly |
| unlimited_lives_1h | $0.99 | 1 Hour Unlimited Lives | Play without limits for 1 hour |
| unlimited_lives_forever | $4.99 | Unlimited Lives Forever | Never run out of lives again |
| hint_pack | $1.99 | Hint Pack | Pack of hints to reveal answers |
| starter_pack | $0.99 | Starter Pack | Remove Ads + 100 coins + 1hr unlimited lives |

### Subscription (create under Subscriptions tab, not In-app products)

| Product ID | Price | Title | Description |
|---|---|---|---|
| season_pass_monthly | $1.99/month | Season Pass | 2x coins on every level for 30 days |

Subscription settings: billing period = 1 month, grace period = 3 days, create a base plan, set to Active.

All IAP statuses must be **Active** before publishing the app.

---

## Building Release AABs

For each game:

```
cd /home/pgs/Documents/Gs/[GAME]/android
./gradlew bundleRelease
```

Output: app/build/outputs/bundle/release/app-release.aab

Verify keystore.properties exists and has correct storeFile / storePassword / keyAlias / keyPassword before building.

---

## Version Bumps Required Before Building

| Game | Current versionCode | Current versionName | Set to |
|---|---|---|---|
| Ball Sort Puzzle | 14 | 1.9 | 15 / 2.0 |
| Nonogram | 7 | 1.5 | 8 / 1.6 |
| Pipe Connect | 7 | 1.5 | 8 / 1.6 |
| 2048 Puzzle | 7 | 1.5 | 8 / 1.6 |
| Unblock Puzzle | 7 | 1.5 | 8 / 1.6 |
| Water Sort | 7 | 1.5 | 8 / 1.6 |

Edit versionCode and versionName in android/app/build.gradle for each game before running bundleRelease.

---

## Play Console: New App Checklist (for first-time publishing)

### Store Listing
- App name (match android:label in manifest)
- Short description — 80 chars max
- Full description — 4000 chars max, unique per game
- App icon — 512x512 PNG, no alpha, no rounded corners
- Feature graphic — 1024x500 PNG
- Screenshots — minimum 2 phone screenshots at 1080x2400
  - Recommended screens: menu, gameplay, level select, shop, missions
- Category: Games → Puzzle

### App Content (all required)
- Privacy Policy URL — host one page covering all Pegasus Games apps (GitHub Pages works)
- Ads declaration: yes, app contains ads
- Target audience: 13+
- Data safety form: declare that AdMob (third-party SDK) collects device/advertising data; your app collects no user data server-side
- Content rating: complete IARC questionnaire → should receive Everyone or Everyone 10+

### Pricing & Distribution
- Free, all countries (adjust if needed)

### Release flow
1. Upload AAB to Internal Testing first
2. Add tester account: Play Console → Setup → License Testing (allows testing IAPs without real charges)
3. Test on real device: IAPs, ads, all screens, level completion
4. Promote to Production when verified

---

## Post-Launch Checklist (do within 48h of going live)

- [ ] Link app in AdMob to Play Store listing
- [ ] Monitor ANR & Crash rate in Play Console
- [ ] Check AdMob for policy violation emails (highest risk in first 7 days)
- [ ] Reply to first user reviews within 24h
- [ ] Verify IAPs are purchasable from a non-tester account
