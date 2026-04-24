# Water Sort Puzzle — Release Guide

Package: com.pegasusgames.watersortpuzzle
AdMob App ID: ca-app-pub-5695494884863768~4951744270
AdMob Banner:       ca-app-pub-5695494884863768/6958960514
AdMob Interstitial: ca-app-pub-5695494884863768/4267242200
AdMob Rewarded:     ca-app-pub-5695494884863768/6124390997
Current version: 10 / 1.6.2 (v1.6.2 adds local notifications — see NOTIFICATIONS_IMPL.md)
Status: UPDATE
AppLovin: disabled until developer approved (see MainActivity USE_APPLOVIN flag)

---

## AdMob (apps.admob.com)

Create 3 ad units under this app:
- banner (Adaptive Banner)
- interstitial (Interstitial)
- rewarded (Rewarded)

Paste the 3 Ad Unit IDs into MainActivity.java/kt.

---

## IAPs in Play Console

Create all common IAPs from SHARED_SETUP.md, PLUS:

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

Note: unlimited_lives_1h is referenced in game code — include it even if not prominently shown in shop UI.

---

## Build

```
cd /home/pgs/Documents/Gs/WaterSort/android
# build.gradle is already at versionCode 10, versionName "1.6.2"
./gradlew bundleRelease
```

AAB: app/build/outputs/bundle/release/app-release.aab

---

## Play Console Steps

If NEW app:
- Complete full store listing (see SHARED_SETUP.md)
- Upload to Internal Testing first, test IAPs and ads, then promote to Production

If UPDATE:
1. Production → Create new release
2. Upload AAB
3. Add release notes
4. Review → Start rollout

### Release Notes

EN (v1.6.2):
• Daily reminder notifications for your streak and daily challenge
• New setting: toggle reminders on/off from Settings
• Minor bug fixes and stability improvements

(See `metadata/en-US/release_notes.txt` for the shipping copy.)

---

## Store Listing Suggestions

Short description (80 chars):
Pour and sort colored water into matching flasks — relaxing puzzle fun!

Full description opening:
Can you sort all the colored water? Pour liquids between flasks until each one contains a single color. Simple to learn, endlessly satisfying to master. With 500 handcrafted levels, daily challenges, and 6 beautiful themes, Water Sort Puzzle will keep you coming back every day.
