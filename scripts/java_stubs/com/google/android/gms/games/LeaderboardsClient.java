package com.google.android.gms.games;
public interface LeaderboardsClient { void submitScore(String id, long score); com.google.android.gms.tasks.Task<android.content.Intent> getLeaderboardIntent(String id); com.google.android.gms.tasks.Task<android.content.Intent> getAllLeaderboardsIntent(); }
