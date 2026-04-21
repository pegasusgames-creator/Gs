package com.pegasusgames.headsupgame;

import com.applovin.sdk.AppLovinMediationProvider;
import com.applovin.sdk.AppLovinSdkInitializationConfiguration;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.RelativeLayout;

import com.applovin.mediation.MaxAd;
import com.applovin.mediation.MaxAdListener;
import com.applovin.mediation.MaxAdViewAdListener;
import com.applovin.mediation.MaxError;
import com.applovin.mediation.MaxReward;
import com.applovin.mediation.MaxRewardedAdListener;
import com.applovin.mediation.ads.MaxAdView;
import com.applovin.mediation.ads.MaxInterstitialAd;
import com.applovin.mediation.ads.MaxRewardedAd;
import com.applovin.sdk.AppLovinSdk;

import com.google.firebase.analytics.FirebaseAnalytics;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MainActivity extends Activity {

    // -------------------------------------------------------
    // AppLovin MAX ad unit IDs — create in MAX dashboard
    // -------------------------------------------------------
    private static final String BANNER_AD_UNIT_ID       = "ENTER_BANNER_AD_UNIT_ID";
    private static final String INTERSTITIAL_AD_UNIT_ID = "ENTER_INTERSTITIAL_AD_UNIT_ID";
    private static final String REWARDED_AD_UNIT_ID     = "ENTER_REWARDED_AD_UNIT_ID";

    // WebView background colour — Sunset Orange theme
    private static final int WEBVIEW_BG_COLOR = 0xFF080818;

    // -------------------------------------------------------
    // IAP PRODUCT IDs — must match Google Play Console
    // -------------------------------------------------------
    private static final String PRODUCT_REMOVE_ADS = "remove_ads";
    private static final Set<String> VALID_PRODUCTS =
        new HashSet<>(Arrays.asList("remove_ads"));

    private WebView           webView;
    private MaxAdView         bannerAd;
    private MaxInterstitialAd interstitialAd;
    private MaxRewardedAd     rewardedAd;
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
        bannerAd = new MaxAdView(BANNER_AD_UNIT_ID, this);
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

        WebView.setWebContentsDebuggingEnabled(true);
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

        firebaseAnalytics = FirebaseAnalytics.getInstance(this);

        // Init AppLovin MAX
        AppLovinSdkInitializationConfiguration initConfig =
            AppLovinSdkInitializationConfiguration.builder("ENTER_YOUR_APPLOVIN_SDK_KEY_HERE", this)
                .setMediationProvider(AppLovinMediationProvider.MAX)
                .build();
        AppLovinSdk.getInstance(this).initialize(initConfig, sdkConfig -> runOnUiThread(() -> {
            runOnUiThread(() -> bannerAd.startAutoRefresh());
            bannerAd.loadAd();
            setupInterstitial();
            setupRewarded();
        }));

        setupBilling();
    }

    // -------------------------------------------------------
    // Interstitial
    // -------------------------------------------------------
    private void setupInterstitial() {
        interstitialAd = new MaxInterstitialAd(INTERSTITIAL_AD_UNIT_ID, this);
        interstitialAd.setListener(new MaxAdListener() {
            @Override public void onAdLoaded(MaxAd ad) {}
            @Override public void onAdDisplayed(MaxAd ad) {}
            @Override public void onAdHidden(MaxAd ad) { interstitialAd.loadAd(); }
            @Override public void onAdClicked(MaxAd ad) {}
            @Override public void onAdLoadFailed(String id, MaxError e) {
                new android.os.Handler(android.os.Looper.getMainLooper())
                    .postDelayed(() -> interstitialAd.loadAd(), 3000);
            }
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError e) { interstitialAd.loadAd(); }
        });
        interstitialAd.loadAd();
    }

    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (interstitialAd != null && interstitialAd.isReady())
                interstitialAd.showAd();
        });
    }

    // -------------------------------------------------------
    // Rewarded
    // -------------------------------------------------------
    private void setupRewarded() {
        rewardedAd = MaxRewardedAd.getInstance(REWARDED_AD_UNIT_ID, this);
        rewardedAd.setListener(new MaxRewardedAdListener() {
            @Override public void onAdLoaded(MaxAd ad) {}
            @Override public void onAdDisplayed(MaxAd ad) {}
            @Override public void onAdHidden(MaxAd ad) { rewardedAd.loadAd(); }
            @Override public void onAdClicked(MaxAd ad) {}
            @Override public void onAdLoadFailed(String id, MaxError e) {
                new android.os.Handler(android.os.Looper.getMainLooper())
                    .postDelayed(() -> rewardedAd.loadAd(), 3000);
            }
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError e) {
                pendingRewardType = null;
                rewardedAd.loadAd();
            }
            @Override public void onUserRewarded(MaxAd ad, MaxReward reward) {
                // Grant reward ONLY here — never in onAdHidden
                final String type = pendingRewardType;
                pendingRewardType = null;
                if (type != null) {
                    runOnUiThread(() ->
                        webView.evaluateJavascript(
                            "window.onAdReward && window.onAdReward('" + type + "');", null));
                }
            }
        });
        rewardedAd.loadAd();
    }

    private void showRewardedAd(String rewardType) {
        runOnUiThread(() -> {
            if (rewardedAd != null && rewardedAd.isReady()) {
                pendingRewardType = rewardType;
                rewardedAd.showAd();
            }
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

    private void handlePurchase(Purchase purchase) {
        if (purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED) return;
        if (!purchase.isAcknowledged())
            billingClient.acknowledgePurchase(
                AcknowledgePurchaseParams.newBuilder()
                    .setPurchaseToken(purchase.getPurchaseToken()).build(), r -> {});
        for (String id : purchase.getProducts()) {
            if (!VALID_PRODUCTS.contains(id)) continue;
            runOnUiThread(() ->
                webView.evaluateJavascript(
                    "window.onPurchaseComplete && window.onPurchaseComplete('" + id + "');", null));
            if (id.equals(PRODUCT_REMOVE_ADS))
                runOnUiThread(() -> bannerAd.setVisibility(android.view.View.GONE));
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
        if (bannerAd != null) bannerAd.startAutoRefresh();
        if (webView != null) webView.onResume();
    }
    @Override protected void onPause() {
        super.onPause();
        if (bannerAd != null) bannerAd.stopAutoRefresh();
        if (webView != null) webView.onPause();
    }
    @Override protected void onDestroy() {
        super.onDestroy();
        if (bannerAd != null) bannerAd.destroy();
        if (webView != null) { webView.stopLoading(); webView.destroy(); }
        if (billingClient != null) billingClient.endConnection();
    }
}
