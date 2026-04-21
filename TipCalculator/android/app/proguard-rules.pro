# Add project specific ProGuard rules here.

# Keep JavaScript interface methods
-keepclassmembers class com.pegasusgames.tipcalculator.MainActivity$NativeBridge {
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

# AppLovin MAX — suppress missing Amazon Privacy Pass stubs (optional dependency)
-dontwarn com.amazon.privacypass.**
-dontwarn com.amazon.**
-dontwarn kotlin.**
-dontwarn org.jetbrains.**
