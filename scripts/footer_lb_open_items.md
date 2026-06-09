# Open items — footer clearance + leaderboard sizing

## setLeaderboardSize bridge is wired but unused (2026-05-29)

The `setLeaderboardSize(int n)` `@JavascriptInterface` method exists
on every `MainActivity` (WaterSort, Nonogram, Puzzle2048, UnblockPuzzle).
It is **not yet called from native code**. Until it is, every game
ships with the 1000-row floor from `Math.max(1000, ...)` in
`buildStandings()`.

### Wiring options (pick one)

1. **Firebase Remote Config** (preferred — fast iteration, no backend).
   - Add `firebase-config` dependency to each app's `build.gradle`.
   - On `MainActivity.onCreate`, after `firebaseAnalytics = ...`:
     ```java
     FirebaseRemoteConfig rc = FirebaseRemoteConfig.getInstance();
     rc.setDefaultsAsync(java.util.Map.of("leaderboard_total", 1000L));
     rc.fetchAndActivate().addOnCompleteListener(t -> {
       long n = rc.getLong("leaderboard_total");
       setLeaderboardSize((int) n);
     });
     ```
   - In Firebase console, set `leaderboard_total` to current install
     count rounded to the nearest 1000 (e.g., 5000 once an app has
     5k DAU). Reviewed monthly.

2. **Play Developer API** (more accurate but server-side).
   - Server reads `developerReportingApi.statistics_v1.statisticsService.timeline`
     for actual install/DAU figures.
   - Server pushes via Remote Config (still uses path 1's client code).
   - Required if we want the total to reflect actual MAU not a
     stale manual estimate.

3. **Skip dynamic — keep 1000 floor forever**. Cheapest. The 1000
   floor reads as "this game has thousands of players" without
   lying about exact figures.

## Action

- [ ] Decide between options 1 / 2 / 3.
- [ ] If 1 or 2: add Firebase Remote Config dep + wire on app launch.
- [ ] Verify roster updates after a fetch (Settings → Force-stop +
      relaunch; should see new rank ordering with new total).

## Related but separate

- UnblockPuzzle post-release cross-promo TODO: still no Play link,
  so it stays excluded from `PROMO_GAMES` / `CROSS_PROMO_PACKAGES`
  / `MORE_GAMES` in the other three apps until it ships.
