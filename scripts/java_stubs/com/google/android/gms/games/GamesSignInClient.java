package com.google.android.gms.games;
public interface GamesSignInClient { com.google.android.gms.tasks.Task<AuthenticationResult> isAuthenticated(); com.google.android.gms.tasks.Task<AuthenticationResult> signIn(); }
