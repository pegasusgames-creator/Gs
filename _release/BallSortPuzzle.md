# Ball Sort Puzzle — Release Guide

Package: com.pegasusgames.ballsort
AdMob App ID: ca-app-pub-2759523698880843~9194379298
Current version: 14 / 1.9 → bump to 15 / 2.0
Status: UPDATE (already on Play Store)

---

## AdMob (apps.admob.com)

Create 3 ad units under this app:
- banner (Adaptive Banner)
- interstitial (Interstitial)
- rewarded (Rewarded)

Paste the 3 resulting Ad Unit IDs into MainActivity.java/kt in the corresponding showBannerAd / showInterstitial / showRewarded methods.

---

## IAPs in Play Console

Create all common IAPs from SHARED_SETUP.md, PLUS these extras:

| Product ID | Price | Title | Description |
|---|---|---|---|
| unlimited_undos | $1.99 | Unlimited Undos | Unlimited undo moves forever |

Full list for this app:
- remove_ads
- coins_small
- coins_large
- five_lives
- unlimited_lives_1h
- unlimited_lives_forever
- hint_pack
- starter_pack
- unlimited_undos
- season_pass_monthly (subscription)

---

## Build

```
cd /home/pgs/Documents/Gs/BallSortPuzzle/android
# Edit app/build.gradle: versionCode 15, versionName "2.0"
./gradlew bundleRelease
```

AAB: app/build/outputs/bundle/release/app-release.aab

---

## Play Console Update Steps

1. Open Ball Sort Puzzle in Play Console
2. Production → Create new release
3. Upload app-release.aab
4. Release notes (copy below)
5. Review release → Start rollout to Production

### Release Notes

EN:
Major update! New themes (6 color schemes), weekly challenges with coin rewards, missions system, stats screen, session streak bonuses, Season Pass (2x coins), Starter Pack offer, and Dragon theme coin sink. Bug fixes and performance improvements.

---

## Store Listing Suggestions

Short description (80 chars):
Sort colorful balls into matching tubes — 500 levels of satisfying puzzles!

Feature graphic text idea: "500 LEVELS • 6 THEMES • DAILY CHALLENGES"
