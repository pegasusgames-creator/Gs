package com.pegasusgames.pipeconnect;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;

// AppLovin MAX SDK
import com.applovin.mediation.MaxAd;
import com.applovin.mediation.MaxAdListener;
import com.applovin.mediation.MaxAdViewAdListener;
import com.applovin.mediation.MaxError;
import com.applovin.mediation.MaxReward;
import com.applovin.mediation.MaxRewardedAdListener;
import com.applovin.mediation.ads.MaxAdView;
import com.applovin.mediation.ads.MaxInterstitialAd;
import com.applovin.mediation.ads.MaxRewardedAd;
import com.applovin.sdk.AppLovinMediationProvider;
import com.applovin.sdk.AppLovinSdk;
import com.applovin.sdk.AppLovinSdkInitializationConfiguration;

// AdMob fallback
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;

// Google Play Billing
import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryProductDetailsResult;
import com.android.billingclient.api.QueryPurchasesParams;

// Firebase
import com.google.firebase.analytics.FirebaseAnalytics;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MainActivity extends Activity {

    // ── AppLovin MAX ──────────────────────────────────────────────────────────
    // Get SDK Key: dash.applovin.com → Account → Keys → SDK Key
    // Get Ad Unit IDs: dash.applovin.com → Monetize → Ad Units
    private static final String MAX_SDK_KEY              = "ENTER_YOUR_APPLOVIN_SDK_KEY_HERE";
    private static final String MAX_BANNER_UNIT_ID       = "ENTER_YOUR_MAX_BANNER_UNIT_ID";
    private static final String MAX_INTERSTITIAL_UNIT_ID = "ENTER_YOUR_MAX_INTER_UNIT_ID";
    private static final String MAX_REWARDED_UNIT_ID     = "ENTER_YOUR_MAX_REWARDED_UNIT_ID";
    // Auto-switch: uses AppLovin when SDK key is real, AdMob otherwise
    private static final boolean USE_APPLOVIN = !MAX_SDK_KEY.startsWith("ENTER_");

    // ── AdMob fallback ────────────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units
    private static final String ADMOB_BANNER_UNIT_ID       = "__ADMOB_BANNER_UNIT_PLACEHOLDER__";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "__ADMOB_INTERSTITIAL_UNIT_PLACEHOLDER__";
    private static final String ADMOB_REWARDED_UNIT_ID     = "__ADMOB_REWARDED_UNIT_PLACEHOLDER__";

    // ── IAP ───────────────────────────────────────────────────────────────────
    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "coins_small", "coins_large", "hint_pack",
        "five_lives", "unlimited_lives_1h", "unlimited_lives_forever",
        "starter_pack", "season_pass_monthly"
    ));
    private static final Set<String> VALID_REWARD_TYPES = new HashSet<>(Arrays.asList(
        "undo", "skip", "life"
    ));

    private static final int WEBVIEW_BG_COLOR = 0xFF0f1923;

    // AppLovin MAX objects
    private MaxAdView         bannerAd;
    private MaxInterstitialAd interstitialAd;
    private MaxRewardedAd     rewardedAd;
    // AdMob objects
    private com.google.android.gms.ads.AdView admobBanner;
    private InterstitialAd admobInterstitial;
    private RewardedAd     admobRewarded;

    private WebView      webView;
    private FrameLayout  bannerContainer;
    private BillingClient billingClient;
    private String        pendingRewardType;
    private FirebaseAnalytics firebaseAnalytics;

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

        // WebView above banner
        webView = new WebView(this);
        RelativeLayout.LayoutParams wp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.MATCH_PARENT);
        wp.addRule(RelativeLayout.ABOVE, bannerContainer.getId());
        layout.addView(webView, wp);

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
        webView.setBackgroundColor(WEBVIEW_BG_COLOR);

        NativeBridge bridge = new NativeBridge();
        webView.addJavascriptInterface(bridge, "Android");
        webView.addJavascriptInterface(bridge, "NativeBridge");
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                runOnUiThread(() ->
                    webView.evaluateJavascript("window.onAdMobLoaded && window.onAdMobLoaded();", null));
            }
        });
        webView.loadUrl("file:///android_asset/game.html");

        // Prime the window so SDK calls don't NPE on mDecor before onWindowFocusChanged
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            try { getWindow().setDecorFitsSystemWindows(false); } catch (Exception ignored) {}
        }

        firebaseAnalytics = FirebaseAnalytics.getInstance(this);

        // Notification channel + runtime permission (API 33+)
        NotificationHelper.createChannel(this);
        if (Build.VERSION.SDK_INT >= 33) {
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1001);
            }
        }

        if (USE_APPLOVIN) initAppLovin(); else initAdMob();
        setupBilling();
    }

    // ── AppLovin MAX ──────────────────────────────────────────────────────────
    private void initAppLovin() {
        bannerAd = new MaxAdView(MAX_BANNER_UNIT_ID, this);
        bannerAd.setListener(new BannerListener());
        bannerContainer.addView(bannerAd, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));

        AppLovinSdkInitializationConfiguration cfg =
            AppLovinSdkInitializationConfiguration.builder(MAX_SDK_KEY, this)
                .setMediationProvider(AppLovinMediationProvider.MAX).build();
        AppLovinSdk.getInstance(this).initialize(cfg, c -> runOnUiThread(() -> {
            bannerAd.loadAd();
            loadInterstitialAd();
            loadRewardedAd();
        }));
    }

    private class BannerListener implements MaxAdViewAdListener {
        @Override public void onAdLoaded(MaxAd ad) {}
        @Override public void onAdLoadFailed(String id, MaxError e) {}
        @Override public void onAdClicked(MaxAd ad) {}
        @Override public void onAdExpanded(MaxAd ad) {}
        @Override public void onAdCollapsed(MaxAd ad) {}
        @Override public void onAdDisplayed(MaxAd ad) {}
        @Override public void onAdDisplayFailed(MaxAd ad, MaxError e) {}
        @Override public void onAdHidden(MaxAd ad) {}
    }

    private void loadInterstitialAd() {
        interstitialAd = new MaxInterstitialAd(MAX_INTERSTITIAL_UNIT_ID, this);
        interstitialAd.setListener(new MaxAdListener() {
            @Override public void onAdLoaded(MaxAd ad) {}
            @Override public void onAdLoadFailed(String id, MaxError e) {}
            @Override public void onAdDisplayed(MaxAd ad) {}
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError e) { interstitialAd.loadAd(); }
            @Override public void onAdClicked(MaxAd ad) {}
            @Override public void onAdHidden(MaxAd ad) { interstitialAd.loadAd(); }
        });
        interstitialAd.loadAd();
    }

    private void loadRewardedAd() {
        rewardedAd = MaxRewardedAd.getInstance(MAX_REWARDED_UNIT_ID, this);
        rewardedAd.setListener(new MaxRewardedAdListener() {
            @Override public void onAdLoaded(MaxAd ad) {}
            @Override public void onAdLoadFailed(String id, MaxError e) {}
            @Override public void onAdDisplayed(MaxAd ad) {}
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError e) {
                rewardedAd.loadAd();
                runOnUiThread(() ->
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null));
            }
            @Override public void onAdClicked(MaxAd ad) {}
            @Override public void onAdHidden(MaxAd ad) { rewardedAd.loadAd(); }
            @Override public void onUserRewarded(MaxAd ad, MaxReward r) {
                if (pendingRewardType == null) return;
                String js = "window.onAdReward && window.onAdReward('" + pendingRewardType + "');";
                runOnUiThread(() -> webView.evaluateJavascript(js, null));
                pendingRewardType = null;
            }
        });
        rewardedAd.loadAd();
    }

    // ── AdMob fallback ────────────────────────────────────────────────────────
    private void initAdMob() {
        MobileAds.initialize(this, s -> runOnUiThread(() -> {
            loadAdmobBanner(); loadAdmobInterstitial(); loadAdmobRewarded();
        }));
    }

    private void loadAdmobBanner() {
        admobBanner = new com.google.android.gms.ads.AdView(this);
        admobBanner.setAdSize(AdSize.BANNER);
        admobBanner.setAdUnitId(ADMOB_BANNER_UNIT_ID);
        bannerContainer.addView(admobBanner, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT,
            android.view.Gravity.CENTER));
        admobBanner.loadAd(new AdRequest.Builder().build());
    }

    private void loadAdmobInterstitial() {
        InterstitialAd.load(this, ADMOB_INTERSTITIAL_UNIT_ID, new AdRequest.Builder().build(),
            new InterstitialAdLoadCallback() {
                @Override public void onAdLoaded(InterstitialAd ad) {
                    admobInterstitial = ad;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            admobInterstitial = null; loadAdmobInterstitial();
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            admobInterstitial = null; loadAdmobInterstitial();
                        }
                    });
                }
                @Override public void onAdFailedToLoad(LoadAdError e) { admobInterstitial = null; }
            });
    }

    private void loadAdmobRewarded() {
        RewardedAd.load(this, ADMOB_REWARDED_UNIT_ID, new AdRequest.Builder().build(),
            new RewardedAdLoadCallback() {
                @Override public void onAdLoaded(RewardedAd ad) {
                    admobRewarded = ad;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            admobRewarded = null; loadAdmobRewarded();
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            admobRewarded = null; loadAdmobRewarded();
                        }
                    });
                }
                @Override public void onAdFailedToLoad(LoadAdError e) { admobRewarded = null; }
            });
    }

    // ── Banner show/hide ──────────────────────────────────────────────────────
    private void hideBanner() {
        runOnUiThread(() -> bannerContainer.setVisibility(android.view.View.GONE));
    }
    private void showBanner() {
        runOnUiThread(() -> bannerContainer.setVisibility(android.view.View.VISIBLE));
    }

    // ── Interstitial show ─────────────────────────────────────────────────────
    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (USE_APPLOVIN) {
                if (interstitialAd != null && interstitialAd.isReady()) interstitialAd.showAd();
            } else {
                if (admobInterstitial != null) admobInterstitial.show(this);
            }
        });
    }

    // ── Rewarded show ─────────────────────────────────────────────────────────
    // Reward is granted ONLY in the reward callback, never in dismiss.
    private void showRewardedAd(String rewardType) {
        if (!VALID_REWARD_TYPES.contains(rewardType)) return;
        pendingRewardType = rewardType;
        runOnUiThread(() -> {
            if (USE_APPLOVIN) {
                if (rewardedAd != null && rewardedAd.isReady()) {
                    rewardedAd.showAd();
                } else {
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                    pendingRewardType = null;
                }
            } else {
                if (admobRewarded != null) {
                    admobRewarded.show(this, item -> {
                        if (pendingRewardType == null) return;
                        String js = "window.onAdReward && window.onAdReward('" + pendingRewardType + "');";
                        webView.evaluateJavascript(js, null);
                        pendingRewardType = null;
                    });
                } else {
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                    pendingRewardType = null;
                }
            }
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
                if (r.getResponseCode() == BillingClient.BillingResponseCode.OK) restorePurchases();
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

    private void launchPurchase(String productId) {
        if (!VALID_PRODUCTS.contains(productId)) return;
        if ("season_pass_monthly".equals(productId)) { launchSubscription(productId); return; }
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(Arrays.asList(
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(productId).setProductType(BillingClient.ProductType.INAPP).build()
            )).build(),
            (r, queryResult) -> {
                java.util.List<ProductDetails> details = queryResult.getProductDetailsList();
                if (!details.isEmpty()) runOnUiThread(() ->
                    billingClient.launchBillingFlow(MainActivity.this,
                        BillingFlowParams.newBuilder().setProductDetailsParamsList(Arrays.asList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(details.get(0)).build()
                        )).build()));
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
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onPurchaseSuccess && window.onPurchaseSuccess('" + id + "');", null));
            if ("remove_ads".equals(id)) hideBanner();
        }
    }

    private void launchSubscription(String productId) {
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(Arrays.asList(
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(productId)
                    .setProductType(BillingClient.ProductType.SUBS).build()
            )).build(),
            (r, queryResult) -> {
                List<ProductDetails> details = queryResult.getProductDetailsList();
                if (details.isEmpty()) return;
                ProductDetails pd = details.get(0);
                List<ProductDetails.SubscriptionOfferDetails> offers = pd.getSubscriptionOfferDetails();
                if (offers == null || offers.isEmpty()) return;
                runOnUiThread(() ->
                    billingClient.launchBillingFlow(MainActivity.this,
                        BillingFlowParams.newBuilder().setProductDetailsParamsList(Arrays.asList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(pd)
                                .setOfferToken(offers.get(0).getOfferToken()).build()
                        )).build()));
            });
    }

    private void restorePurchases() {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build(),
            (r, purchases) -> { for (Purchase p : purchases) handlePurchase(p); });
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build(),
            (r, purchases) -> { for (Purchase p : purchases) handlePurchase(p); });
    }

    // ── JS Bridge ─────────────────────────────────────────────────────────────
    private class NativeBridge {
        @JavascriptInterface public void showInterstitial()              { showInterstitialAd(); }
        @JavascriptInterface public void showRewarded(String type)       { showRewardedAd(type); }
        @JavascriptInterface public void purchase(String id)             { launchPurchase(id); }
        @JavascriptInterface public void hideBannerAd()                  { hideBanner(); }
        @JavascriptInterface public void showBannerAd()                  { showBanner(); }
        @JavascriptInterface public void log(String msg)                 { /* disabled in release */ }

        @JavascriptInterface
        public void scheduleNotification(String title, String body, long delayMs) {
            int mins = Math.max(1, (int)(delayMs / 60000L));
            NotificationHelper.schedule(MainActivity.this, mins);
        }

        @JavascriptInterface
        public void cancelNotification() {
            NotificationHelper.cancel(MainActivity.this);
        }

        @JavascriptInterface
        public void requestNotificationPermission() {
            if (Build.VERSION.SDK_INT >= 33) {
                if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                        != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1001);
                }
            }
        }

        @JavascriptInterface
        public void logEvent(String eventName, String params) {
            if (firebaseAnalytics == null) return;
            if (!eventName.matches("[a-zA-Z0-9_]{1,40}")) return;
            android.os.Bundle bundle = new android.os.Bundle();
            if (params != null && !params.isEmpty()) {
                for (String pair : params.split("&")) {
                    String[] kv = pair.split("=", 2);
                    if (kv.length == 2 && kv[0].matches("[a-zA-Z0-9_]{1,40}")) {
                        String val = kv[1].length() > 100 ? kv[1].substring(0, 100) : kv[1];
                        bundle.putString(kv[0], val);
                    }
                }
            }
            firebaseAnalytics.logEvent(eventName, bundle);
        }
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
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.startAutoRefresh();
        } else {
            if (admobBanner != null) admobBanner.resume();
        }
        if (webView != null) webView.onResume();
    }

    @Override protected void onPause() {
        super.onPause();
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.stopAutoRefresh();
        } else {
            if (admobBanner != null) admobBanner.pause();
        }
        if (webView != null) webView.onPause();
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.destroy();
        } else {
            if (admobBanner != null) admobBanner.destroy();
        }
        if (webView != null) { webView.stopLoading(); webView.destroy(); }
        if (billingClient != null) billingClient.endConnection();
    }

    @Override public void onBackPressed() {
        webView.evaluateJavascript("window.onBackPressed && window.onBackPressed();",
            v -> { if (v == null || v.equals("null") || v.equals("false")) super.onBackPressed(); });
    }

    private int dpToPx(int dp) {
        return (int) (dp * getResources().getDisplayMetrics().density);
    }
}
