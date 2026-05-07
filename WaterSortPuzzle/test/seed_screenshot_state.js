// WaterSortPuzzle — pre-screenshot localStorage seed.
//
// WaterSort stores its main state in 'watersort_save' (see
// game.html:1064). Achievements live in 'ls_v2', missions in
// 'ws_missions_v1', and stats in 'ws_stats_v1'.
//
// The full watersort_save schema is broad — this seed populates the
// fields the menu/Stats/Missions screens read so screenshots show
// realistic mid-game numbers instead of fresh-install zeros.

(function() {
  var today = new Date().toISOString().slice(0, 10);

  // Main save state — schema mirrors the saveState() call site in
  // game.html. Fields not seeded here use the in-app defaults.
  var save = {
    currentLevel:         87,             // mid-portfolio progression
    completedLevels:      Array.from({length: 86}, function(_, i){return i + 1;}),
    levelStars: (function() {
      var s = {};
      for (var i = 1; i <= 86; i++) s[i] = (i % 4 === 0 ? 3 : (i % 3 === 0 ? 2 : 1));
      return s;
    })(),
    coins:                412,
    lives:                5,
    lastLifeTime:         Date.now(),
    removeAds:            false,
    soundEnabled:         true,
    musicEnabled:         false,
    activeTheme:          'default',
    dailyChallengeDate:   today,
    dailyChallengeStreak: 9,              // 🔥 streak on Stats screen
    bestStreak:           14,
    unlimitedLivesUntil:  0,
    unlimitedLivesForever: false,
  };
  try {
    localStorage.setItem('watersort_save', JSON.stringify(save));

    // Achievements (LS_KEY = 'ls_v2', schema {n,d,ach})
    localStorage.setItem('ls_v2', JSON.stringify({
      n:   9,
      d:   today,
      ach: ['first_solve', 'streak_3', 'streak_7', 'all_4_color', 'all_5_color',
            'no_undo_solve', 'speed_solve', 'comeback', 'collector_3'],
    }));

    // Missions — daily set with mid-progress
    localStorage.setItem('ws_missions_v1', JSON.stringify({
      date: today,
      progress: {
        mission_solver:    3,             // 3 / 5
        mission_dedicated: 12,            // 12 / 20
        mission_streak:    1,             // 1 / 3
      },
      claimed: { mission_perfectionist: true },
    }));

    // Stats screen aggregates (Levels solved, time-of-day patterns, etc.)
    localStorage.setItem('ws_stats_v1', JSON.stringify({
      levels_solved:     86,
      total_pours:       1247,
      total_undo:        34,
      total_play_time_s: 8420,
      sessions:          47,
      best_streak:       14,
      tubes_solved:      318,
      hour_histogram:    [0,0,0,0,0,0,1,2,4,3,5,6,3,2,1,2,5,8,12,9,6,4,2,1],
    }));

    // Language sticky
    localStorage.setItem('app_lang', 'en');
  } catch (e) {}

  return 'watersort: seeded';
})();
