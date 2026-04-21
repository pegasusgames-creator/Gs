# Nonogram Puzzle — Release Guide

Package: com.pegasusgames.nonogram
AdMob App ID: ca-app-pub-2759523698880843~8865461839
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

---

## Build

```
cd /home/pgs/Documents/Gs/Nonogram/android
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
Major update! 6 grid color themes, weekly challenges, missions system, stats screen, session streak bonuses, Season Pass, Starter Pack, come-back banner, and tutorial for new players. 500 puzzles total!

---

## Store Listing Suggestions

Short description (80 chars):
Solve pixel art grid puzzles — 500 nonograms from easy to expert!

Full description opening:
Nonogram Puzzle brings the classic paint-by-numbers logic game to your phone. Fill in the grid using row and column number clues to reveal hidden pixel art. With 500 hand-crafted puzzles ranging from 5×5 beginner grids to challenging 15×15 expert puzzles, plus daily challenges and 6 beautiful themes, there's always a new puzzle to solve.
