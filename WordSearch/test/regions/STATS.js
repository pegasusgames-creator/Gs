  var stats=[
    {icon:'🔎',label:'Puzzles Solved',sub:'campaign levels',value:completed},
    {icon:'⭐',label:'Three-Star Grids',sub:'under par, no hints',value:perfect},
    {icon:'🔤',label:'Words Found',sub:'every grid, every mode',value:save.wsWords|0},
    {icon:'🎁',label:'Bonus Words',sub:'hidden extras spotted',value:save.wsBonus|0},
    {icon:'✨',label:'Messages Revealed',sub:'hidden-message grids',value:save.wsMsgs|0},
    {icon:'🔥',label:'Daily Streak',sub:'days in a row',value:Math.max(save.dailyChallengeStreak||0,1)},
    {icon:'📋',label:'Current Level',sub:'keep searching!',value:(save.currentLevel||0)+1},
  ];
