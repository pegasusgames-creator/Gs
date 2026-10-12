package com.pegasusgames.abclearning;

// ─────────────────────────────────────────────────────────────────────────────
// KIDS SHELL WRAPPER (Google Play Families) — see docs/KIDS_SHELL.md.
//
// This is the kids variant of the Pegasus WebView wrapper. Compared with the
// game wrapper it deliberately has:
//   * NO notifications (no NotificationHelper/Receiver, no POST_NOTIFICATIONS,
//     no AlarmManager) — Families policy + CLAUDE.md red line 9.
//   * AdMob BANNER ONLY, child-directed: TFCD + TFUA + max rating G set before
//     MobileAds.initialize; no interstitial, no rewarded, no mediation.
//   * NO Play Games Services, NO Firebase Analytics, NO sharing intents.
//   * openUrl / openPlayStore restricted to an allowlist (game.html also puts
//     every call behind the parental gate).
//   * A native TextToSpeech bridge (Android WebView has no speechSynthesis).
// Bridge methods the shared game JS may still call (showInterstitial,
// scheduleDailyReminder, submitScore, shareText, ...) stay as harmless no-ops
// so nothing throws. Gate: scripts/check_families_compliance.py.
// ─────────────────────────────────────────────────────────────────────────────

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;

// AdMob (banner only, child-directed)
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.RequestConfiguration;

// Google Play Billing
import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.ConsumeParams;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;

// Java
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import android.util.Base64;

public class MainActivity extends Activity {

    // ── AdMob (banner only) ───────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units. The AdMob app must be
    // marked "Designed for Families / child-directed" in the AdMob console.
    private static final String ADMOB_BANNER_UNIT_ID = "ca-app-pub-3940256099942544/6300978111";

    // Play Console → Monetization setup → Licensing → base64-encoded RSA public
    // key. Used by verifyPurchaseSignature() before any grant. Per-app, unique.
    private static final String LICENSE_PUBLIC_KEY = "PASTE_LICENSE_PUBLIC_KEY";

    // ── IAP — generated from metadata/iaps.json (never hand-curate) ──────────
    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "full_pack"
    ));

    // Kids catalog has no consumables and no subscriptions: every SKU is a
    // non-consumable acknowledged via acknowledgePurchase (within 3 days).
    private static final Set<String> CONSUMABLE_PRODUCTS = Collections.emptySet();

    // SKUs whose purchase removes the banner.
    private static final Set<String> AD_FREE_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "full_pack"
    ));

    // Only other LIVE Pegasus KIDS apps may ever be listed here (and in the
    // manifest <queries>). Empty until a sibling kids app is live.
    private static final Set<String> KIDS_PROMO_PACKAGES = Collections.emptySet();

    // External URLs the parent area may open (behind the parental gate).
    private static final String[] URL_ALLOWLIST = {
        "https://pegasusgames-creator.github.io/",
        "https://play.google.com/store/"
    };

    private static final int WEBVIEW_BG_COLOR = 0xFFfff6df;
    private static final String PREFS = "kids_shell";
    private static final String PREF_ADS_REMOVED = "ads_removed";

    private com.google.android.gms.ads.AdView admobBanner;
    private WebView       webView;
    private FrameLayout   bannerContainer;
    private BillingClient billingClient;
    private TextToSpeech  tts;
    private volatile boolean ttsReady = false;
    private boolean bannerWanted = true;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        RelativeLayout layout = new RelativeLayout(this);
        setContentView(layout);

        // Banner container at bottom
        bannerContainer = new FrameLayout(this);
        bannerContainer.setId(android.view.View.generateViewId());
        RelativeLayout.LayoutParams bp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, dpToPx(50));
        bp.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        layout.addView(bannerContainer, bp);
        if (adsRemoved()) bannerContainer.setVisibility(android.view.View.GONE);

        // WebView above banner
        webView = new WebView(this);
        RelativeLayout.LayoutParams wp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.MATCH_PARENT);
        wp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
        wp.addRule(RelativeLayout.ABOVE, bannerContainer.getId());
        layout.addView(webView, wp);
        bannerContainer.bringToFront();
        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setOverScrollMode(android.view.View.OVER_SCROLL_NEVER);

        if (0 != (getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE))
            WebView.setWebContentsDebuggingEnabled(true);
        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setMediaPlaybackRequiresUserGesture(false);
        ws.setCacheMode(WebSettings.LOAD_DEFAULT);
        ws.setAllowFileAccess(true);
        ws.setAllowFileAccessFromFileURLs(false);
        ws.setAllowUniversalAccessFromFileURLs(false);
        ws.setSupportMultipleWindows(false);
        ws.setJavaScriptCanOpenWindowsAutomatically(false);
        webView.setBackgroundColor(WEBVIEW_BG_COLOR);

        NativeBridge bridge = new NativeBridge();
        webView.addJavascriptInterface(bridge, "Android");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, android.webkit.WebResourceRequest req) {
                String u = (req != null && req.getUrl() != null) ? req.getUrl().toString() : "";
                // Kids: in-app navigation only. Nothing leaves the app from a
                // WebView link — external pages go through the gated openUrl().
                return !u.startsWith("file:///android_asset");
            }
            @Override public void onPageFinished(WebView view, String url) {
                runOnUiThread(() -> webView.evaluateJavascript(
                    "window.onNativeReady && window.onNativeReady(" + ttsReady + ");", null));
            }
        });
        webView.loadUrl("file:///android_asset/game.html");

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            try { getWindow().setDecorFitsSystemWindows(false); } catch (Exception ignored) {}
        }

        initTextToSpeech();
        initAdMob();
        setupBilling();
    }

    // ── Text-to-speech (letter names, phonics, words, praise) ────────────────
    private void initTextToSpeech() {
        try {
            tts = new TextToSpeech(this, status -> {
                ttsReady = (status == TextToSpeech.SUCCESS);
                if (ttsReady) {
                    tts.setLanguage(Locale.US);
                    tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                        @Override public void onStart(String id) {}
                        @Override public void onDone(String id) { speakDone(id); }
                        @Override public void onError(String id) { speakDone(id); }
                    });
                }
                runOnUiThread(() -> {
                    if (webView != null) webView.evaluateJavascript(
                        "window.onTtsReady && window.onTtsReady(" + ttsReady + ");", null);
                });
            });
        } catch (Throwable t) {
            ttsReady = false;
            Log.w("TTS", "TextToSpeech unavailable: " + t.getMessage());
        }
    }

    private void speakDone(final String id) {
        final String safe = id == null ? "" : id.replaceAll("[^A-Za-z0-9_-]", "");
        runOnUiThread(() -> {
            if (webView != null) webView.evaluateJavascript(
                "window.onSpeakDone && window.onSpeakDone('" + safe + "');", null);
        });
    }

    private boolean languageUsable(Locale loc) {
        if (tts == null || !ttsReady) return false;
        try {
            return tts.isLanguageAvailable(loc) >= TextToSpeech.LANG_AVAILABLE;
        } catch (Throwable t) {
            return false;
        }
    }

    // ── AdMob (child-directed banner) ────────────────────────────────────────
    private boolean adsInitialized = false;

    private void initAdMob() {
        if (adsRemoved()) return;   // never initialise ads for a family that paid
        com.google.android.ump.ConsentRequestParameters params =
            new com.google.android.ump.ConsentRequestParameters.Builder()
                .setTagForUnderAgeOfConsent(true)   // kids app: no consent form, no personalised ads
                .build();
        com.google.android.ump.ConsentInformation ci =
            com.google.android.ump.UserMessagingPlatform.getConsentInformation(this);
        ci.requestConsentInfoUpdate(this, params,
            () -> initAdsAfterConsent(),
            e -> initAdsAfterConsent());
    }

    private void initAdsAfterConsent() {
        if (adsInitialized) return;
        adsInitialized = true;
        // MUST be set before MobileAds.initialize: child-directed treatment,
        // under-age-of-consent and a G content ceiling on every request.
        MobileAds.setRequestConfiguration(
            new RequestConfiguration.Builder()
                .setTagForChildDirectedTreatment(
                    RequestConfiguration.TAG_FOR_CHILD_DIRECTED_TREATMENT_TRUE)
                .setTagForUnderAgeOfConsent(
                    RequestConfiguration.TAG_FOR_UNDER_AGE_OF_CONSENT_TRUE)
                .setMaxAdContentRating(RequestConfiguration.MAX_AD_CONTENT_RATING_G)
                .build());
        MobileAds.initialize(this, s -> runOnUiThread(this::loadAdmobBanner));
    }

    private void loadAdmobBanner() {
        if (adsRemoved() || admobBanner != null) return;
        admobBanner = new com.google.android.gms.ads.AdView(this);
        admobBanner.setAdSize(AdSize.BANNER);
        admobBanner.setAdUnitId(ADMOB_BANNER_UNIT_ID);
        bannerContainer.addView(admobBanner, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT,
            android.view.Gravity.CENTER));
        admobBanner.loadAd(new AdRequest.Builder().build());
        if (!bannerWanted) hideBanner();
    }

    private boolean adsRemoved() {
        return getSharedPreferences(PREFS, MODE_PRIVATE).getBoolean(PREF_ADS_REMOVED, false);
    }

    private void markAdsRemoved() {
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putBoolean(PREF_ADS_REMOVED, true).apply();
        runOnUiThread(() -> {
            bannerContainer.setVisibility(android.view.View.GONE);
            if (admobBanner != null) {
                bannerContainer.removeView(admobBanner);
                admobBanner.destroy();
                admobBanner = null;
            }
        });
    }

    // ── Banner show/hide (game.html hides it on tracing / game screens) ──────
    private void hideBanner() {
        bannerWanted = false;
        runOnUiThread(() -> {
            bannerContainer.setVisibility(android.view.View.GONE);
            if (admobBanner != null) admobBanner.pause();
        });
    }

    private void showBanner() {
        bannerWanted = true;
        if (adsRemoved()) return;
        runOnUiThread(() -> {
            bannerContainer.setVisibility(android.view.View.VISIBLE);
            if (admobBanner != null) admobBanner.resume();
        });
    }

    // ── Google Play Billing ───────────────────────────────────────────────────
    private void setupBilling() {
        billingClient = BillingClient.newBuilder(this)
            .setListener((r, purchases) -> {
                if (r.getResponseCode() == BillingClient.BillingResponseCode.OK && purchases != null)
                    for (Purchase p : purchases) handlePurchase(p);
            })
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .build();

        BillingClientStateListener l = new BillingClientStateListener() {
            @Override public void onBillingSetupFinished(BillingResult r) {
                if (r.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    restorePurchases();
                    queryAndPushPrices();
                }
            }
            @Override public void onBillingServiceDisconnected() {
                final BillingClientStateListener self = this;
                new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {
                    if (billingClient != null && !isFinishing()) billingClient.startConnection(self);
                }, 3000);
            }
        };
        billingClient.startConnection(l);
    }

    // Called only from game.html AFTER the parental gate passed.
    private void launchPurchase(String productId) {
        if (!VALID_PRODUCTS.contains(productId) || billingClient == null) return;
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(Arrays.asList(
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(productId).setProductType(BillingClient.ProductType.INAPP).build()
            )).build(),
            (r, queryResult) -> {
                java.util.List<ProductDetails> details = queryResult.getProductDetailsList();
                if (details.isEmpty()) {
                    runOnUiThread(() -> webView.evaluateJavascript(
                        "window.onPurchaseUnavailable && window.onPurchaseUnavailable('" + productId + "');", null));
                    return;
                }
                runOnUiThread(() ->
                    billingClient.launchBillingFlow(MainActivity.this,
                        BillingFlowParams.newBuilder().setProductDetailsParamsList(Arrays.asList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(details.get(0)).build()
                        )).build()));
            });
    }

    // Localized prices from Play (the $ strings in game.html are the fallback).
    private final java.util.Map<String, String> localizedPrices =
        new java.util.concurrent.ConcurrentHashMap<>();

    private void queryAndPushPrices() {
        java.util.List<QueryProductDetailsParams.Product> prods = new java.util.ArrayList<>();
        for (String sku : VALID_PRODUCTS) {
            prods.add(QueryProductDetailsParams.Product.newBuilder()
                .setProductId(sku).setProductType(BillingClient.ProductType.INAPP).build());
        }
        if (prods.isEmpty() || billingClient == null) return;
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(prods).build(),
            (res, qpdr) -> {
                for (ProductDetails pd : qpdr.getProductDetailsList()) {
                    if (pd.getOneTimePurchaseOfferDetails() != null)
                        localizedPrices.put(pd.getProductId(),
                            pd.getOneTimePurchaseOfferDetails().getFormattedPrice());
                }
                pushPricesToWeb();
            });
    }

    private void pushPricesToWeb() {
        if (localizedPrices.isEmpty() || webView == null) return;
        final String json = new org.json.JSONObject(localizedPrices).toString();
        runOnUiThread(() -> {
            if (webView != null) webView.evaluateJavascript(
                "window.onLocalizedPrices && window.onLocalizedPrices(" + json + ")", null);
        });
    }

    private void handlePurchase(Purchase purchase) {
        if (purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED) return;
        if (!verifyPurchaseSignature(purchase)) {
            Log.w("IAP", "Signature verification failed; reward NOT granted.");
            return;
        }

        boolean isConsumable = false;
        for (String id : purchase.getProducts()) {
            if (CONSUMABLE_PRODUCTS.contains(id)) { isConsumable = true; break; }
        }

        if (isConsumable) {
            billingClient.consumeAsync(
                ConsumeParams.newBuilder()
                    .setPurchaseToken(purchase.getPurchaseToken()).build(),
                (r, token) -> Log.i("IAP", "consumeAsync " + r.getResponseCode()));
        } else if (!purchase.isAcknowledged()) {
            billingClient.acknowledgePurchase(
                AcknowledgePurchaseParams.newBuilder()
                    .setPurchaseToken(purchase.getPurchaseToken()).build(),
                r -> {
                    if (r.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                        Log.i("IAP", "acknowledgePurchase OK for " + purchase.getProducts());
                    } else {
                        Log.w("IAP", "acknowledgePurchase failed (" + r.getResponseCode()
                                + "): " + r.getDebugMessage());
                    }
                });
        }

        for (String id : purchase.getProducts()) {
            if (!VALID_PRODUCTS.contains(id)) continue;
            if (AD_FREE_PRODUCTS.contains(id)) markAdsRemoved();
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onPurchaseSuccess && window.onPurchaseSuccess('" + id + "');", null));
        }
    }

    // RSA-SHA1 signature check against the app's Play Console public key.
    // Fail-closed in release while the key is still a placeholder.
    private boolean verifyPurchaseSignature(Purchase purchase) {
        if (LICENSE_PUBLIC_KEY == null || LICENSE_PUBLIC_KEY.startsWith("PASTE_")) {
            Log.w("IAP", "LICENSE_PUBLIC_KEY is placeholder — signature check skipped.");
            return (getApplicationInfo().flags
                & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;
        }
        String signedData = purchase.getOriginalJson();
        String signature  = purchase.getSignature();
        if (signedData == null || signature == null || signature.isEmpty()) return false;
        try {
            byte[] keyBytes = Base64.decode(LICENSE_PUBLIC_KEY, Base64.DEFAULT);
            PublicKey pub = KeyFactory.getInstance("RSA")
                .generatePublic(new X509EncodedKeySpec(keyBytes));
            Signature sig = Signature.getInstance("SHA1withRSA");
            sig.initVerify(pub);
            sig.update(signedData.getBytes("UTF-8"));
            return sig.verify(Base64.decode(signature, Base64.DEFAULT));
        } catch (NoSuchAlgorithmException | InvalidKeySpecException
                 | java.security.SignatureException | java.security.InvalidKeyException
                 | java.io.UnsupportedEncodingException | IllegalArgumentException e) {
            Log.w("IAP", "Purchase signature verify error: " + e.getMessage());
            return false;
        }
    }

    private void restorePurchases() {
        if (billingClient == null) return;
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build(),
            (r, purchases) -> { for (Purchase p : purchases) handlePurchase(p); });
    }

    private static boolean urlAllowed(String url) {
        if (url == null) return false;
        for (String prefix : URL_ALLOWLIST) if (url.startsWith(prefix)) return true;
        return false;
    }

    // ── JS Bridge ─────────────────────────────────────────────────────────────
    private class NativeBridge {
        // Purchases + links — game.html calls these only behind the parental gate.
        @JavascriptInterface public void purchase(String id)        { launchPurchase(id); }
        @JavascriptInterface public void restorePurchases()         { MainActivity.this.restorePurchases(); }
        @JavascriptInterface public void openUrl(String url) {
            if (!urlAllowed(url)) return;
            runOnUiThread(() -> {
                try {
                    startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                        android.net.Uri.parse(url)));
                } catch (Exception ignored) {}
            });
        }
        @JavascriptInterface public boolean isAppInstalled(String pkg) {
            if (pkg == null || !KIDS_PROMO_PACKAGES.contains(pkg)) return false;
            try { getPackageManager().getPackageInfo(pkg, 0); return true; }
            catch (Exception e) { return false; }
        }
        @JavascriptInterface public void openPlayStore(String pkg) {
            if (pkg == null || !KIDS_PROMO_PACKAGES.contains(pkg)) return;
            openUrl("https://play.google.com/store/apps/details?id=" + pkg);
        }

        // Banner (child-directed) — hidden on tracing / game screens.
        @JavascriptInterface public void hideBannerAd()              { hideBanner(); }
        @JavascriptInterface public void showBannerAd()              { showBanner(); }
        @JavascriptInterface public boolean isAdFree()               { return adsRemoved(); }

        // Speech (device TextToSpeech).
        @JavascriptInterface public boolean ttsAvailable()           { return ttsReady; }
        @JavascriptInterface public boolean ttsHasLanguage(String tag) {
            if (tag == null || tag.isEmpty()) return false;
            return languageUsable(Locale.forLanguageTag(tag));
        }
        @JavascriptInterface public void speak(String text, String tag, float rate, String id) {
            if (!ttsReady || tts == null || text == null || text.isEmpty()) { speakDone(id); return; }
            final String t = text.length() > 300 ? text.substring(0, 300) : text;
            final float r = Math.max(0.5f, Math.min(1.5f, rate));
            runOnUiThread(() -> {
                try {
                    Locale loc = (tag == null || tag.isEmpty()) ? Locale.US : Locale.forLanguageTag(tag);
                    tts.setLanguage(languageUsable(loc) ? loc : Locale.US);
                    tts.setSpeechRate(r);
                    tts.speak(t, TextToSpeech.QUEUE_FLUSH, null, id == null ? "u" : id);
                } catch (Throwable e) { speakDone(id); }
            });
        }
        @JavascriptInterface public void stopSpeaking() {
            runOnUiThread(() -> { try { if (tts != null) tts.stop(); } catch (Throwable ignored) {} });
        }

        @JavascriptInterface public void log(String msg)             { /* disabled in release */ }

        // ── Harmless no-ops (Families: no notifications, no rewarded or
        // interstitial ads, no Play Games, no analytics, no sharing). Kept so
        // shared JS that probes for them never throws. ──────────────────────
        @JavascriptInterface public void showInterstitial()          { }
        @JavascriptInterface public void preloadRewarded()           { }
        @JavascriptInterface public void showRewarded(String type) {
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onAdNotReady && window.onAdNotReady();", null));
        }
        @JavascriptInterface public void scheduleNotification(String title, String body, long delayMs) { }
        @JavascriptInterface public void cancelNotification()        { }
        @JavascriptInterface public void requestNotificationPermission() { }
        @JavascriptInterface public boolean hasNotificationPermission() { return false; }
        @JavascriptInterface public void scheduleDailyReminder(int hourOfDay, int minute) { }
        @JavascriptInterface public void scheduleStreakAtRisk(int streakDays) { }
        @JavascriptInterface public void scheduleLivesRefilled(long whenMillis) { }
        @JavascriptInterface public void scheduleWinBack(int dayOffset, String title, String body) { }
        @JavascriptInterface public void cancelAllNotifications()    { }
        @JavascriptInterface public void setNotificationsEnabled(boolean enabled) { }
        @JavascriptInterface public boolean getNotificationsEnabled() { return false; }
        @JavascriptInterface public void recordLastPlayed()          { }
        @JavascriptInterface public void shareText(String body)      { }
        @JavascriptInterface public void shareImage(String base64Png, String caption) { }
        @JavascriptInterface public void setLeaderboardSize(int n)   { }
        @JavascriptInterface public void submitScore(String leaderboardId, long score) { }
        @JavascriptInterface public void showLeaderboard(String leaderboardId) { }
        @JavascriptInterface public boolean signInPlayGames()        { return false; }
        @JavascriptInterface public boolean isPlayGamesAuthenticated() { return false; }
        @JavascriptInterface public void logEvent(String eventName, String params) { }
    }

    // ── Fullscreen ────────────────────────────────────────────────────────────
    private void applyFullscreen() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            getWindow().setDecorFitsSystemWindows(false);
            android.view.WindowInsetsController ic = getWindow().getInsetsController();
            if (ic != null) {
                ic.hide(android.view.WindowInsets.Type.statusBars() |
                        android.view.WindowInsets.Type.navigationBars());
                ic.setSystemBarsBehavior(
                    android.view.WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        } else {
            //noinspection deprecation
            getWindow().getDecorView().setSystemUiVisibility(
                android.view.View.SYSTEM_UI_FLAG_FULLSCREEN |
                android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        }
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) applyFullscreen();
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────
    @Override protected void onResume() {
        super.onResume();
        if (admobBanner != null && bannerWanted) admobBanner.resume();
        if (webView != null) webView.onResume();
    }

    @Override protected void onPause() {
        super.onPause();
        if (admobBanner != null) admobBanner.pause();
        if (webView != null) webView.onPause();
        try { if (tts != null) tts.stop(); } catch (Throwable ignored) {}
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        if (admobBanner != null) admobBanner.destroy();
        if (webView != null) { webView.stopLoading(); webView.destroy(); }
        if (billingClient != null) billingClient.endConnection();
        if (tts != null) { try { tts.shutdown(); } catch (Throwable ignored) {} }
    }

    @Override public void onBackPressed() {
        webView.evaluateJavascript("window.onBackPressed && window.onBackPressed();",
            v -> { if (v == null || v.equals("null") || v.equals("false")) super.onBackPressed(); });
    }

    private int dpToPx(int dp) {
        return (int) (dp * getResources().getDisplayMetrics().density);
    }
}
