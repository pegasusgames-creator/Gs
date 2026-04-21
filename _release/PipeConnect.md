# Pipe Connect — Release Guide

Package: com.pegasusgames.pipeconnect
AdMob App ID: ca-app-pub-2759523698880843~3090390974
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

No extras beyond the common set. Full list:

- remove_ads
- coins_small
- coins_large
- five_lives
- unlimited_lives_1h
- unlimited_lives_forever
- hint_pack
- starter_pack
- season_pass_monthly (subscription)

Note: PipeConnect uses VALID_REWARD_TYPES = hint / skip / life for rewarded ads. Make sure the rewarded ad unit is wired to all three reward types in MainActivity.

---

## Build

```
cd /home/pgs/Documents/Gs/PipeConnect/android
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
Major update! 6 pipe color themes, weekly challenges, missions system, stats screen, streak bonuses, Season Pass (2× coins), Starter Pack, come-back banner, and tutorial. 500 levels of pipe-connecting fun!

---

## Store Listing Suggestions

Short description (80 chars):
Connect matching colored pipes to fill the board — 500 flow puzzles!

Full description opening:
Draw lines to connect matching colored dots and fill every cell on the board. Sounds simple — but with hundreds of increasingly complex grids, Pipe Connect will challenge your logical thinking. 500 levels, 6 themes, daily challenges, and weekly events keep the puzzles fresh every day.
