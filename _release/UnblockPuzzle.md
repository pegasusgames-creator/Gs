# Unblock Puzzle — Release Guide

Package: com.pegasusgames.unblockpuzzle
AdMob App ID: ca-app-pub-2759523698880843~3555759989
Current version: 7 / 1.5 → bump to 8 / 1.6
Status: UPDATE or NEW (check Play Console)

---

## AdMob (apps.admob.com)

Create 3 ad units under this app:
- banner (Adaptive Banner)
- interstitial (Interstitial)
- rewarded (Rewarded)

Paste the 3 Ad Unit IDs into MainActivity.java/kt.

---

## IAPs in Play Console

Full list for this app:

- remove_ads  ($2.99)
- coins_small  ($0.99)
- coins_large  ($2.99 or $3.99 — shop shows $3.99, set whichever you want)
- five_lives  ($0.99)
- unlimited_lives_1h  ($0.99)
- unlimited_lives_forever  ($4.99)
- hint_pack  ($0.99 — shop shows $0.99 for this game)
- starter_pack  ($0.99)
- season_pass_monthly  ($1.99/month, subscription)

Note: this game's shop shows coins_large at $3.99 — set the Play Console price to match what's displayed in-game.

Coin-spend items (no IAP needed, handled in-game with coins):
- coin_hint — 30 coins for 1 hint (handled in JS, no Play product needed)
- coin_life — 75 coins for 1 life (handled in JS, no Play product needed)

---

## Build

```
cd /home/pgs/Documents/Gs/UnblockPuzzle/android
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
Major update! 6 block color themes, weekly challenges, missions system, stats screen, streak bonuses, Season Pass (2× coins), Starter Pack, come-back banner, and tutorial for new players. 500 sliding block puzzles!

---

## Store Listing Suggestions

Short description (80 chars):
Slide blocks to free the red piece — 500 unblock puzzles to solve!

Full description opening:
Slide the blocks out of the way to free the red piece and escape through the exit. Easy to pick up, but increasingly clever puzzles will keep you thinking. With 500 levels ranging from beginner to expert, daily challenges, 6 themes, and weekly events, Unblock Puzzle is the sliding block game that never gets old.
