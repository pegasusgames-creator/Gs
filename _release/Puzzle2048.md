# 2048 Puzzle — Release Guide

Package: com.pegasusgames.puzzle2048
AdMob App ID: ca-app-pub-2759523698880843~3659701763
Current version: 7 / 1.5 → bump to 8 / 1.6
Status: UPDATE or NEW (check Play Console)

---

## AdMob (apps.admob.com)

Create 3 ad units under this app:
- banner (Adaptive Banner)
- interstitial (Interstitial)
- rewarded (Rewarded)

Paste the 3 Ad Unit IDs into MainActivity.java/kt.
VALID_REWARD_TYPES = undo / continue / life — make sure the rewarded ad callback passes these through correctly.

---

## IAPs in Play Console

No extras beyond the common set. Full list:

- remove_ads
- coins_small
- coins_large
- five_lives
- unlimited_lives_1h
- unlimited_lives_forever
- undo_pack  ← NOTE: this game uses undo_pack instead of hint_pack
- starter_pack
- season_pass_monthly (subscription)

Note: this game uses undo_pack (not hint_pack). Create it as:
  Product ID: undo_pack
  Price: $1.99
  Title: Undo Pack
  Description: Pack of extra undo moves

---

## Build

```
cd /home/pgs/Documents/Gs/Puzzle2048/android
# Edit app/build.gradle: versionCode 8, versionName "1.6"
./gradlew bundleRelease
```

AAB: app/build/outputs/bundle/release/app-release.aab

---

## Play Console Steps

If NEW app:
- Complete full store listing (see SHARED_SETUP.md)
- Upload to Internal Testing first, then promote to Production

If UPDATE:
1. Production → Create new release
2. Upload AAB
3. Add release notes
4. Review → Start rollout

### Release Notes

EN:
Major update! 6 tile color themes, weekly challenges, missions system, stats screen, streak bonuses, Season Pass (2× coins), Starter Pack, come-back banner, and tutorial. Merge your way to 2048 across 500 levels!

---

## Store Listing Suggestions

Short description (80 chars):
Swipe and merge tiles to reach 2048 — 500 guided puzzle levels!

Full description opening:
The classic 2048 game reimagined as a guided puzzle experience. Swipe tiles to merge matching numbers and work your way up to 2048 — and beyond. With 500 handcrafted levels, daily challenges, 6 beautiful themes, and a missions system to keep you motivated, this is the definitive 2048 experience on Android.
