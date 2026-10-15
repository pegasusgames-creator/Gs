# Keep JavaScript interface methods (registered as both "Android" and "NativeBridge")
-keepclassmembers class com.pegasusgames.pipeconnect.MainActivity$NativeBridge {
    public *;
}

# AdMob
-keep public class com.google.android.gms.ads.** { public *; }

# Play Billing
-keep class com.android.billingclient.** { *; }

# WebView
-keepclassmembers class * extends android.webkit.WebViewClient {
    public void *(android.webkit.WebView, java.lang.String, android.graphics.Bitmap);
    public boolean *(android.webkit.WebView, java.lang.String);
}

# Firebase Analytics
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.internal.firebase_analytics.** { *; }
