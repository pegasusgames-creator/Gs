# Release Guides — Pegasus Games

Start here: SHARED_SETUP.md covers AdMob, common IAPs, build process, and Play Console steps that apply to all 6 apps.

Then open the individual file for each app you're releasing.

## Files

- SHARED_SETUP.md — AdMob, common IAPs, build steps, Play Console new app checklist, post-launch
- BallSortPuzzle.md — com.pegasusgames.ballsort — v14→15
- WaterSort.md — com.pegasusgames.watersort — v7→8
- Nonogram.md — com.pegasusgames.nonogram — v7→8
- PipeConnect.md — com.pegasusgames.pipeconnect — v7→8
- Puzzle2048.md — com.pegasusgames.puzzle2048 — v7→8
- UnblockPuzzle.md — com.pegasusgames.unblockpuzzle — v7→8

## Order of operations

1. Bump version codes in all build.gradle files
2. Run bundleRelease for all 6 games
3. Set up AdMob ad units for any app that doesn't have them yet
4. Create IAPs in Play Console for each app (must be Active before publishing)
5. Upload AABs (Internal Testing first, then Production)
6. Link each app in AdMob after AAB is accepted
