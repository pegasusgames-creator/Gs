// Puzzle2048 — pre-screenshot localStorage seed.
//
// IMPORTANT: Puzzle2048 stores everything in ONE JSON blob keyed
// 'puzzle2048_save' (see game.html:SAVE_KEY). The patch documentation
// mentioned per-field 'p2048_*' keys, but those don't exist in the
// actual game — every field below lives inside puzzle2048_save.
//
// Schema lifted from game.html:defaultState() (around line 778). Run
// before each capture so the menu, Stats, and Best screens show
// realistic mid-game numbers instead of fresh-install zeros.

(function() {
  var seed = {
    score:                 247,
    bestScore:             512,
    grid:                  null,           // current run; null = no resume
    highestTile:           128,
    achieved2048:          false,
    coins:                 85,
    lives:                 5,
    maxLives:              5,
    lastLifeTime:          Date.now(),
    removeAds:             false,
    unlimitedLivesPermanent: false,
    unlimitedLivesExpiry:  0,
    undoPack:              3,              // shows "3 undos available" in Shop
    dailyChallengeDate:    new Date().toISOString().slice(0, 10),
    dailyChallengeStreak:  7,              // 🔥 7-day streak on Best screen
    dailyChallengeBest:    320,
    soundEnabled:          true,
    musicEnabled:          false,
    isDailyChallenge:      false,
    activeTheme:           'default',
    lastLevelProgress:     null,
  };
  try {
    localStorage.setItem('puzzle2048_save', JSON.stringify(seed));
    // Achievements stored separately under ls_v2 (see LS_KEY).
    localStorage.setItem('ls_v2', JSON.stringify({
      n:   7,                              // 7 achievements unlocked
      d:   new Date().toISOString().slice(0, 10),
      ach: [],
    }));
    // Daily missions are date-keyed; seed as if user has progress on today's set.
    localStorage.setItem('2048_missions_v1', JSON.stringify({
      date:     new Date().toISOString().slice(0, 10),
      progress: { mission_solver: 3, mission_dedicated: 12, mission_streak: 1 },
      claimed:  { mission_perfectionist: true },
    }));
    // Weekly event progress: 3 of 5 rounds played.
    var week = (function() {
      var d = new Date();
      var oneJan = new Date(d.getFullYear(), 0, 1);
      var days = Math.floor((d - oneJan) / 86400000);
      return d.getFullYear() + '_' + Math.ceil((days + oneJan.getDay() + 1) / 7);
    })();
    localStorage.setItem('xweekly_' + week, '3');
  } catch (e) {}
  // Apply to live State so the current session reflects the seed without reload.
  if (typeof State === 'object' && State) {
    Object.assign(State, seed);
    if (typeof updateUI === 'function')      updateUI();
    if (typeof updateMenuUI === 'function')  updateMenuUI();
  }
  return 'puzzle2048: seeded';
})();
