# Keep JavaScript interface methods (registered as "Android")
-keepclassmembers class com.pegasusgames.abclearning.MainActivity$NativeBridge {
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
