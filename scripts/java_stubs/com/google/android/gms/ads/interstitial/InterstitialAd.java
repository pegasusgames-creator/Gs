package com.google.android.gms.ads.interstitial;
public abstract class InterstitialAd { public static void load(android.content.Context c, String id, com.google.android.gms.ads.AdRequest r, InterstitialAdLoadCallback cb){} public abstract void setFullScreenContentCallback(com.google.android.gms.ads.FullScreenContentCallback c); public abstract void show(android.app.Activity a); }
