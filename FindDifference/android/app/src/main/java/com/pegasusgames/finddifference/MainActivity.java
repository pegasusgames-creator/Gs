package com.pegasusgames.finddifference;

import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import com.google.android.ump.ConsentInformation;
import com.google.android.ump.ConsentRequestParameters;
import com.google.android.ump.UserMessagingPlatform;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.ConsumeParams;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.RelativeLayout;


import com.google.firebase.analytics.FirebaseAnalytics;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MainActivity extends Activity {

    // -------------------------------------------------------
    // AdMob ad unit IDs — Google TEST units until scripts/set_app_ids.py
    // sets the real ones (pre_publish_check blocks test IDs).
    // -------------------------------------------------------
    private static final String BANNER_AD_UNIT_ID       = "ca-app-pub-3940256099942544/6300978111";
    private static final String INTERSTITIAL_AD_UNIT_ID = "ca-app-pub-3940256099942544/1033173712";
    private static final String REWARDED_AD_UNIT_ID     = "ca-app-pub-3940256099942544/5224354917";

    // WebView background colour — Sunset Orange theme
    private static final int WEBVIEW_BG_COLOR = 0xFF0a1818;

    // -------------------------------------------------------
    // IAP PRODUCT IDs — must match Google Play Console
    // -------------------------------------------------------
    private static final String PRODUCT_REMOVE_ADS = "remove_ads";
    private static final Set<String> VALID_PRODUCTS =
        new HashSet<>(Arrays.asList(
        "coins_large", "coins_small", "five_lives", "hint_pack", "remove_ads",
        "season_pass_monthly", "starter_pack", "unlimited_lives_1h",
        "unlimited_lives_forever"
    
    ));
    // SKUs that are CONSUMABLE — must be consumed via consumeAsync after each
    // purchase, otherwise the user can buy once and never re-buy. Anything in
    // VALID_PRODUCTS but NOT in this set is non-consumable / subscription and
    // acknowledged via acknowledgePurchase. Both flows must complete within
    // Play's 3-day window or the purchase is auto-refunded.
    private static final Set<String> CONSUMABLE_PRODUCTS = new HashSet<>(Arrays.asList(
        "coins_large", "coins_small", "five_lives", "hint_pack",
        "starter_pack", "unlimited_lives_1h"
    ));


    private WebView           webView;
    private AdView            bannerAd;
    private InterstitialAd    interstitialAd;
    private RewardedAd        rewardedAd;
    private String            pendingRewardType = null;
    private BillingClient     billingClient;
    private FirebaseAnalytics firebaseAnalytics;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        RelativeLayout layout = new RelativeLayout(this);
        setContentView(layout);


        // Banner ad (50 dp, pinned to bottom)
        int bannerId = android.view.View.generateViewId();
        bannerAd = new AdView(this);
        bannerAd.setAdUnitId(BANNER_AD_UNIT_ID);
        bannerAd.setAdSize(AdSize.BANNER);
        bannerAd.setId(bannerId);
        int bannerHeightPx = (int) (50 * getResources().getDisplayMetrics().density);
        RelativeLayout.LayoutParams bannerParams = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, bannerHeightPx);
        bannerParams.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        layout.addView(bannerAd, bannerParams);

        // WebView fills above the banner
        webView = new WebView(this);
        RelativeLayout.LayoutParams webParams = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT,
            RelativeLayout.LayoutParams.MATCH_PARENT);
        webParams.addRule(RelativeLayout.ABOVE, bannerId);
        layout.addView(webView, webParams);

        WebView.setWebContentsDebuggingEnabled(
            (getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0);
        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setCacheMode(WebSettings.LOAD_DEFAULT);
        ws.setAllowFileAccessFromFileURLs(false);
        ws.setAllowUniversalAccessFromFileURLs(false);

        webView.setBackgroundColor(WEBVIEW_BG_COLOR);
        NativeBridge bridge = new NativeBridge();
        webView.addJavascriptInterface(bridge, "Android");
        webView.addJavascriptInterface(bridge, "NativeBridge");
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                runOnUiThread(() ->
                    webView.evaluateJavascript(
                        "window.onNativeBridgeReady && window.onNativeBridgeReady();", null));
            }
        });
        webView.loadUrl("file:///android_asset/game.html");

        // Prime window before SDK init to prevent NPE on mDecor
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            try { getWindow().setDecorFitsSystemWindows(false); } catch (Exception ignored) {}
        }

        try { firebaseAnalytics = FirebaseAnalytics.getInstance(this); }
        catch (Throwable t) { firebaseAnalytics = null; } // no google-services.json

        // Google UMP consent first (EEA/UK requirement), then AdMob.
        final ConsentInformation consent = UserMessagingPlatform.getConsentInformation(this);
        consent.requestConsentInfoUpdate(this, new ConsentRequestParameters.Builder().build(),
            () -> UserMessagingPlatform.loadAndShowConsentFormIfRequired(this, formError -> startAds(consent)),
            requestError -> startAds(consent));
        if (consent.canRequestAds()) startAds(consent);

        setupBilling();
    }

    // -------------------------------------------------------
    // AdMob start (after consent)
    // -------------------------------------------------------
    private boolean adsStarted = false;
    private void startAds(ConsentInformation consent) {
        if (adsStarted || !consent.canRequestAds()) return;
        adsStarted = true;
        MobileAds.initialize(this, status -> runOnUiThread(() -> {
            bannerAd.loadAd(new AdRequest.Builder().build());
            loadInterstitial();
            loadRewarded();
        }));
    }

    private static long backoffMs(int attempt) { return Math.min(60000L, 3000L << Math.min(attempt, 4)); }

    // -------------------------------------------------------
    // Interstitial
    // -------------------------------------------------------
    private int interstitialRetry = 0;
    private void loadInterstitial() {
        InterstitialAd.load(this, INTERSTITIAL_AD_UNIT_ID, new AdRequest.Builder().build(),
            new InterstitialAdLoadCallback() {
                @Override public void onAdLoaded(InterstitialAd ad) { interstitialAd = ad; interstitialRetry = 0; }
                @Override public void onAdFailedToLoad(LoadAdError e) {
                    interstitialAd = null;
                    new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadInterstitial, backoffMs(interstitialRetry++));
                }
            });
    }

    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (interstitialAd == null) return;
            InterstitialAd ad = interstitialAd;
            interstitialAd = null;
            ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                @Override public void onAdDismissedFullScreenContent() { loadInterstitial(); }
                @Override public void onAdFailedToShowFullScreenContent(AdError e) { loadInterstitial(); }
            });
            ad.show(MainActivity.this);
        });
    }

    // -------------------------------------------------------
    // Rewarded
    // -------------------------------------------------------
    private int rewardedRetry = 0;
    private void loadRewarded() {
        RewardedAd.load(this, REWARDED_AD_UNIT_ID, new AdRequest.Builder().build(),
            new RewardedAdLoadCallback() {
                @Override public void onAdLoaded(RewardedAd ad) { rewardedAd = ad; rewardedRetry = 0; }
                @Override public void onAdFailedToLoad(LoadAdError e) {
                    rewardedAd = null;
                    new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadRewarded, backoffMs(rewardedRetry++));
                }
            });
    }

    private void notifyAdNotReady(String type) {
        runOnUiThread(() -> webView.evaluateJavascript(
            "window.onAdNotReady && window.onAdNotReady('" + type + "');", null));
    }

    private void showRewardedAd(String rewardType) {
        final String rt = rewardType == null ? "" : rewardType.replaceAll("[^A-Za-z0-9_]", "");
        runOnUiThread(() -> {
            if (rewardedAd == null) { notifyAdNotReady(rt); return; }
            RewardedAd ad = rewardedAd;
            rewardedAd = null;
            pendingRewardType = rt;
            ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                @Override public void onAdDismissedFullScreenContent() { pendingRewardType = null; loadRewarded(); }
                @Override public void onAdFailedToShowFullScreenContent(AdError e) {
                    pendingRewardType = null;
                    loadRewarded();
                    notifyAdNotReady(rt);
                }
            });
            ad.show(MainActivity.this, rewardItem -> {
                // Grant reward ONLY here — never on dismiss.
                final String type = pendingRewardType;
                pendingRewardType = null;
                if (type != null) runOnUiThread(() -> webView.evaluateJavascript(
                    "window.onAdReward && window.onAdReward('" + type + "');", null));
            });
        });
    }

    // -------------------------------------------------------
    // Billing
    // -------------------------------------------------------
    private void setupBilling() {
        billingClient = BillingClient.newBuilder(this)
            .setListener((result, purchases) -> {
                if (result.getResponseCode() == BillingClient.BillingResponseCode.OK
                        && purchases != null)
                    for (Purchase p : purchases) handlePurchase(p);
            })
            .enablePendingPurchases(
                PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
            ).build();

        BillingClientStateListener listener = new BillingClientStateListener() {
            @Override public void onBillingSetupFinished(BillingResult r) {
                if (r.getResponseCode() == BillingClient.BillingResponseCode.OK)
                    restorePurchases();
            }
            @Override public void onBillingServiceDisconnected() {
                final BillingClientStateListener self = this;
                new android.os.Handler(android.os.Looper.getMainLooper())
                    .postDelayed(() -> {
                        if (billingClient != null && !isFinishing())
                            billingClient.startConnection(self);
                    }, 3000);
            }
        };
        billingClient.startConnection(listener);
    }

    private void launchPurchase(String productId) {
        if (!VALID_PRODUCTS.contains(productId)) return;
        List<QueryProductDetailsParams.Product> list = Arrays.asList(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId).setProductType(BillingClient.ProductType.INAPP).build());
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(list).build(),
            (billingResult, queryResult) -> {
                List<ProductDetails> details = queryResult.getProductDetailsList();
                if (!details.isEmpty())
                    runOnUiThread(() -> billingClient.launchBillingFlow(this,
                        BillingFlowParams.newBuilder().setProductDetailsParamsList(
                            Arrays.asList(BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(details.get(0)).build())).build()));
            });
    }
    private void hideBanner() {
        runOnUiThread(() -> { if (bannerAd != null) bannerAd.setVisibility(android.view.View.GONE); });
    }


        private void handlePurchase(Purchase purchase) {
        if (purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED) return;

        boolean isConsumable = false;
        for (String id : purchase.getProducts()) {
            if (CONSUMABLE_PRODUCTS.contains(id)) { isConsumable = true; break; }
        }

        if (isConsumable) {
            billingClient.consumeAsync(
                ConsumeParams.newBuilder()
                    .setPurchaseToken(purchase.getPurchaseToken()).build(),
                (r, token) -> {
                    if (r.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                        Log.i("IAP", "consumeAsync OK for " + purchase.getProducts());
                    } else {
                        Log.w("IAP", "consumeAsync failed (" + r.getResponseCode()
                                + "): " + r.getDebugMessage());
                    }
                });
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
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onPurchaseSuccess && window.onPurchaseSuccess('" + id + "');", null));
            if ("remove_ads".equals(id)) hideBanner();
        }
    }
    private void restorePurchases() {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP).build(),
            (r, purchases) -> { for (Purchase p : purchases) handlePurchase(p); });
    }

    // -------------------------------------------------------
    // JS Bridge — registered as both "Android" and "NativeBridge"
    // -------------------------------------------------------
    private class NativeBridge {
        @JavascriptInterface
        public void showInterstitial() { showInterstitialAd(); }

        @JavascriptInterface
        public void showRewarded(String type) { showRewardedAd(type); }

        @JavascriptInterface
        public void hideBannerAd() {
            runOnUiThread(() -> bannerAd.setVisibility(android.view.View.GONE));
        }

        @JavascriptInterface
        public void showBannerAd() {
            runOnUiThread(() -> bannerAd.setVisibility(android.view.View.VISIBLE));
        }

        @JavascriptInterface
        public void purchase(String productId) { launchPurchase(productId); }

        @JavascriptInterface
        public void log(String msg) { /* disabled in release */ }
    }

    // -------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------
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
                android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            applyFullscreen();
        }
    }

    @Override protected void onResume() {
        super.onResume();
        if (bannerAd != null) bannerAd.resume();
        if (webView != null) webView.onResume();
    }
    @Override protected void onPause() {
        super.onPause();
        if (bannerAd != null) bannerAd.pause();
        if (webView != null) webView.onPause();
    }
    @Override protected void onDestroy() {
        super.onDestroy();
        if (bannerAd != null) bannerAd.destroy();
        if (webView != null) { webView.stopLoading(); webView.destroy(); }
        if (billingClient != null) billingClient.endConnection();
    }
}
