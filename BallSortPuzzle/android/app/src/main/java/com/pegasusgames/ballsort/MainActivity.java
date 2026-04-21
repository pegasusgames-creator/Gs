package com.pegasusgames.ballsort;

import android.annotation.SuppressLint;
import android.app.Activity;
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

// AdMob (fallback when AppLovin not yet configured)
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

// Firebase Analytics
import com.google.firebase.analytics.FirebaseAnalytics;

// Play In-App Review
import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;
import com.google.android.gms.tasks.Task;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MainActivity extends Activity {

    // -------------------------------------------------------
    // AppLovin MAX — SDK Key + Ad Unit IDs
    // Get SDK Key: dash.applovin.com → Account → Keys → SDK Key
    // Get Ad Unit IDs: dash.applovin.com → Apps → Monetize → Ad Units
    // -------------------------------------------------------
    private static final String MAX_SDK_KEY              = "ENTER_YOUR_APPLOVIN_SDK_KEY_HERE";
    private static final String MAX_BANNER_UNIT_ID       = "ENTER_YOUR_MAX_BANNER_UNIT_ID";
    private static final String MAX_INTERSTITIAL_UNIT_ID = "ENTER_YOUR_MAX_INTER_UNIT_ID";
    private static final String MAX_REWARDED_UNIT_ID     = "ENTER_YOUR_MAX_REWARDED_UNIT_ID";

    // Auto-switch: uses AppLovin when IDs are filled in, falls back to AdMob otherwise.
    // No code change needed — just fill in the real IDs above when AppLovin is approved.
    private static final boolean USE_APPLOVIN = !MAX_SDK_KEY.startsWith("ENTER_");

    // -------------------------------------------------------
    // AdMob — Fallback Ad Unit IDs (used when AppLovin not configured)
    // Get from: apps.admob.com → Your App → Ad Units
    // -------------------------------------------------------
    private static final String ADMOB_BANNER_UNIT_ID       = "ca-app-pub-2759523698880843/2792117892";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-2759523698880843/5965076140";
    private static final String ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-2759523698880843/4788230421";

    // -------------------------------------------------------
    // IAP Product IDs — must match Google Play Console exactly
    // -------------------------------------------------------
    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "coins_small", "coins_large", "unlimited_undos",
        "five_lives", "unlimited_lives_1h", "unlimited_lives_forever",
        "hint_pack", "starter_pack", "season_pass_monthly"
    ));

    // Whitelist of valid reward types — prevents JS bridge abuse
    private static final Set<String> VALID_REWARD_TYPES = new HashSet<>(Arrays.asList(
        "undo", "skip", "life"
    ));

    // WebView background color — prevents white flash before HTML loads
    private static final int WEBVIEW_BG_COLOR = 0xFF1a1a2e;

    // -------------------------------------------------------
    // Ad objects — only the active path's objects are non-null
    // -------------------------------------------------------
    // AppLovin MAX
    private MaxAdView bannerAd;
    private MaxInterstitialAd interstitialAd;
    private MaxRewardedAd rewardedAd;
    // AdMob
    private com.google.android.gms.ads.AdView admobBanner;
    private InterstitialAd admobInterstitial;
    private RewardedAd admobRewarded;

    private WebView webView;
    private FrameLayout bannerContainer;
    private BillingClient billingClient;
    private String pendingRewardType;
    private FirebaseAnalytics firebaseAnalytics;
    private ReviewManager reviewManager;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        RelativeLayout layout = new RelativeLayout(this);
        setContentView(layout);

        // --- Banner container at bottom (holds either MaxAdView or AdView) ---
        bannerContainer = new FrameLayout(this);
        bannerContainer.setId(android.view.View.generateViewId());
        RelativeLayout.LayoutParams bannerContainerParams = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT,
            dpToPx(50)
        );
        bannerContainerParams.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        layout.addView(bannerContainer, bannerContainerParams);

        // --- WebView above banner container ---
        webView = new WebView(this);
        RelativeLayout.LayoutParams webParams = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT,
            RelativeLayout.LayoutParams.MATCH_PARENT
        );
        webParams.addRule(RelativeLayout.ABOVE, bannerContainer.getId());
        layout.addView(webView, webParams);

        // WebView hardening
        if (0 != (getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE)) {
            WebView.setWebContentsDebuggingEnabled(true);
        }
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
            @Override
            public void onPageFinished(WebView view, String url) {
                runOnUiThread(() ->
                    webView.evaluateJavascript("window.onAdMobLoaded && window.onAdMobLoaded();", null)
                );
            }
        });

        webView.loadUrl("file:///android_asset/game.html");

        applyFullscreen();

        // Firebase Analytics
        firebaseAnalytics = FirebaseAnalytics.getInstance(this);

        // Play In-App Review — pre-warm so it's ready when needed
        reviewManager = ReviewManagerFactory.create(this);

        // --- Initialize ads: AppLovin MAX or AdMob fallback ---
        // Notification channel
        NotificationHelper.createChannel(this);
        if (android.os.Build.VERSION.SDK_INT >= 33) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                    != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS}, 1001);
            }
        }

        if (USE_APPLOVIN) {
            initAppLovin();
        } else {
            initAdMob();
        }

        setupBilling();
    }

    // -------------------------------------------------------
    // APPLOVIN MAX — INIT + ADS
    // -------------------------------------------------------
    private void initAppLovin() {
        bannerAd = new MaxAdView(MAX_BANNER_UNIT_ID, this);
        bannerAd.setListener(new BannerListener());
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        );
        bannerContainer.addView(bannerAd, p);

        AppLovinSdkInitializationConfiguration initConfig =
            AppLovinSdkInitializationConfiguration.builder(MAX_SDK_KEY, this)
                .setMediationProvider(AppLovinMediationProvider.MAX)
                .build();
        AppLovinSdk.getInstance(this).initialize(initConfig, sdkConfig -> runOnUiThread(() -> {
            bannerAd.loadAd();
            loadInterstitialAd();
            loadRewardedAd();
        }));
    }

    private class BannerListener implements MaxAdViewAdListener {
        @Override public void onAdLoaded(MaxAd ad) { }
        @Override public void onAdLoadFailed(String unitId, MaxError error) { }
        @Override public void onAdClicked(MaxAd ad) { }
        @Override public void onAdExpanded(MaxAd ad) { }
        @Override public void onAdCollapsed(MaxAd ad) { }
        @Override public void onAdDisplayed(MaxAd ad) { }
        @Override public void onAdDisplayFailed(MaxAd ad, MaxError error) { }
        @Override public void onAdHidden(MaxAd ad) { }
    }

    private void loadInterstitialAd() {
        interstitialAd = new MaxInterstitialAd(MAX_INTERSTITIAL_UNIT_ID, this);
        interstitialAd.setListener(new MaxAdListener() {
            @Override public void onAdLoaded(MaxAd ad) { }
            @Override public void onAdLoadFailed(String unitId, MaxError error) { }
            @Override public void onAdDisplayed(MaxAd ad) { }
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError error) {
                interstitialAd.loadAd();
            }
            @Override public void onAdClicked(MaxAd ad) { }
            @Override public void onAdHidden(MaxAd ad) {
                interstitialAd.loadAd();
            }
        });
        interstitialAd.loadAd();
    }

    private void loadRewardedAd() {
        rewardedAd = MaxRewardedAd.getInstance(MAX_REWARDED_UNIT_ID, this);
        rewardedAd.setListener(new MaxRewardedAdListener() {
            @Override public void onAdLoaded(MaxAd ad) { }
            @Override public void onAdLoadFailed(String unitId, MaxError error) { }
            @Override public void onAdDisplayed(MaxAd ad) { }
            @Override public void onAdDisplayFailed(MaxAd ad, MaxError error) {
                rewardedAd.loadAd();
                runOnUiThread(() ->
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null)
                );
            }
            @Override public void onAdClicked(MaxAd ad) { }
            @Override public void onAdHidden(MaxAd ad) {
                rewardedAd.loadAd();
            }
            @Override public void onUserRewarded(MaxAd ad, MaxReward reward) {
                if (pendingRewardType == null) return;
                String js = "window.onAdReward && window.onAdReward('" + pendingRewardType + "');";
                runOnUiThread(() -> webView.evaluateJavascript(js, null));
                pendingRewardType = null;
            }
        });
        rewardedAd.loadAd();
    }

    // -------------------------------------------------------
    // ADMOB — FALLBACK INIT + ADS
    // -------------------------------------------------------
    private void initAdMob() {
        MobileAds.initialize(this, initStatus -> runOnUiThread(() -> {
            loadAdmobBanner();
            loadAdmobInterstitial();
            loadAdmobRewarded();
        }));
    }

    private void loadAdmobBanner() {
        admobBanner = new com.google.android.gms.ads.AdView(this);
        admobBanner.setAdSize(AdSize.BANNER);
        admobBanner.setAdUnitId(ADMOB_BANNER_UNIT_ID);
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.WRAP_CONTENT,
            android.view.Gravity.CENTER
        );
        bannerContainer.addView(admobBanner, p);
        admobBanner.loadAd(new AdRequest.Builder().build());
    }

    private void loadAdmobInterstitial() {
        InterstitialAd.load(this, ADMOB_INTERSTITIAL_UNIT_ID, new AdRequest.Builder().build(),
            new InterstitialAdLoadCallback() {
                @Override
                public void onAdLoaded(InterstitialAd ad) {
                    admobInterstitial = ad;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            admobInterstitial = null;
                            loadAdmobInterstitial(); // preload next
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            admobInterstitial = null;
                            loadAdmobInterstitial();
                        }
                    });
                }
                @Override
                public void onAdFailedToLoad(LoadAdError error) {
                    admobInterstitial = null;
                }
            }
        );
    }

    private void loadAdmobRewarded() {
        RewardedAd.load(this, ADMOB_REWARDED_UNIT_ID, new AdRequest.Builder().build(),
            new RewardedAdLoadCallback() {
                @Override
                public void onAdLoaded(RewardedAd ad) {
                    admobRewarded = ad;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            admobRewarded = null;
                            loadAdmobRewarded(); // preload next
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            admobRewarded = null;
                            loadAdmobRewarded();
                        }
                    });
                }
                @Override
                public void onAdFailedToLoad(LoadAdError error) {
                    admobRewarded = null;
                }
            }
        );
    }

    // -------------------------------------------------------
    // BANNER SHOW / HIDE
    // -------------------------------------------------------
    private void hideBanner() {
        runOnUiThread(() -> bannerContainer.setVisibility(android.view.View.GONE));
    }

    private void showBanner() {
        runOnUiThread(() -> bannerContainer.setVisibility(android.view.View.VISIBLE));
    }

    // -------------------------------------------------------
    // INTERSTITIAL SHOW
    // -------------------------------------------------------
    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (USE_APPLOVIN) {
                if (interstitialAd != null && interstitialAd.isReady()) {
                    interstitialAd.showAd();
                }
            } else {
                if (admobInterstitial != null) {
                    admobInterstitial.show(this);
                }
            }
        });
    }

    // -------------------------------------------------------
    // REWARDED SHOW
    // CRITICAL: reward granted ONLY in the reward callback, never in dismiss.
    // -------------------------------------------------------
    private void showRewardedAd(String rewardType) {
        if (!VALID_REWARD_TYPES.contains(rewardType)) return;
        pendingRewardType = rewardType;
        runOnUiThread(() -> {
            if (USE_APPLOVIN) {
                if (rewardedAd != null && rewardedAd.isReady()) {
                    rewardedAd.showAd();
                } else {
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                }
            } else {
                if (admobRewarded != null) {
                    admobRewarded.show(this, rewardItem -> {
                        if (pendingRewardType == null) return;
                        String js = "window.onAdReward && window.onAdReward('" + pendingRewardType + "');";
                        webView.evaluateJavascript(js, null);
                        pendingRewardType = null;
                    });
                } else {
                    webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                }
            }
        });
    }

    // -------------------------------------------------------
    // GOOGLE PLAY BILLING
    // -------------------------------------------------------
    private void setupBilling() {
        billingClient = BillingClient.newBuilder(this)
            .setListener((billingResult, purchases) -> {
                if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK
                        && purchases != null) {
                    for (Purchase purchase : purchases) handlePurchase(purchase);
                }
            })
            .enablePendingPurchases(
                PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
            )
            .build();

        BillingClientStateListener listener = new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(BillingResult result) {
                if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    restorePurchases();
                }
            }
            @Override
            public void onBillingServiceDisconnected() {
                final BillingClientStateListener self = this;
                new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {
                    if (billingClient != null && !isFinishing()) {
                        billingClient.startConnection(self);
                    }
                }, 3000);
            }
        };
        billingClient.startConnection(listener);
    }

    private void launchPurchase(String productId) {
        if (!VALID_PRODUCTS.contains(productId)) return;
        if ("season_pass_monthly".equals(productId)) { launchSubscription(productId); return; }
        List<QueryProductDetailsParams.Product> productList = Arrays.asList(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        );
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(productList).build(),
            (result, queryResult) -> {
                List<ProductDetails> details = queryResult.getProductDetailsList();
                if (!details.isEmpty()) {
                    BillingFlowParams params = BillingFlowParams.newBuilder()
                        .setProductDetailsParamsList(Arrays.asList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(details.get(0))
                                .build()
                        ))
                        .build();
                    runOnUiThread(() -> billingClient.launchBillingFlow(MainActivity.this, params));
                }
            }
        );
    }

    private void handlePurchase(Purchase purchase) {
        if (purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED) return;
        if (!purchase.isAcknowledged()) {
            billingClient.acknowledgePurchase(
                AcknowledgePurchaseParams.newBuilder()
                    .setPurchaseToken(purchase.getPurchaseToken())
                    .build(),
                r -> {}
            );
        }
        for (String productId : purchase.getProducts()) {
            if (!VALID_PRODUCTS.contains(productId)) continue;
            String js = "window.onPurchaseSuccess && window.onPurchaseSuccess('" + productId + "');";
            runOnUiThread(() -> webView.evaluateJavascript(js, null));
            if ("remove_ads".equals(productId)) hideBanner();
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
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP)
                .build(),
            (result, purchases) -> {
                for (Purchase p : purchases) handlePurchase(p);
            }
        );
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build(),
            (result, purchases) -> {
                for (Purchase p : purchases) handlePurchase(p);
            }
        );
    }

    // -------------------------------------------------------
    // JAVASCRIPT BRIDGE
    // -------------------------------------------------------
    private class NativeBridge {

        @JavascriptInterface
        public void showInterstitial() {
            showInterstitialAd();
        }

        @JavascriptInterface
        public void showRewarded(String rewardType) {
            showRewardedAd(rewardType);
        }

        @JavascriptInterface
        public void purchase(String productId) {
            launchPurchase(productId);
        }

        @JavascriptInterface
        public void hideBannerAd() {
            hideBanner();
        }

        @JavascriptInterface
        public void showBannerAd() {
            showBanner();
        }

        @JavascriptInterface
        public void shareText(String text) {
            if (text == null || text.trim().isEmpty()) return;
            final String safeText = text;
            runOnUiThread(() -> {
                android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_SEND);
                intent.setType("text/plain");
                intent.putExtra(android.content.Intent.EXTRA_TEXT, safeText);
                startActivity(android.content.Intent.createChooser(intent, "Share Result"));
            });
        }

        @JavascriptInterface
        public void log(String message) {
            // Logging disabled in release builds
        }


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
            if (android.os.Build.VERSION.SDK_INT >= 33) {
                if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                        != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS}, 1001);
                }
            }
        }

        @JavascriptInterface
        public void requestReview() {
            runOnUiThread(() -> requestInAppReview());
        }

        @JavascriptInterface
        public void logEvent(String eventName, String params) {
            if (firebaseAnalytics == null) return;
            if (!eventName.matches("[a-zA-Z0-9_]{1,40}")) return;
            Bundle bundle = new Bundle();
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

    // -------------------------------------------------------
    // IN-APP REVIEW
    // -------------------------------------------------------
    private void requestInAppReview() {
        if (reviewManager == null) return;
        Task<ReviewInfo> request = reviewManager.requestReviewFlow();
        request.addOnCompleteListener(task -> {
            if (!task.isSuccessful()) return;
            ReviewInfo reviewInfo = task.getResult();
            reviewManager.launchReviewFlow(this, reviewInfo);
        });
    }

    // -------------------------------------------------------
    // FULLSCREEN IMMERSIVE MODE
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
                android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            );
        }
    }

    // -------------------------------------------------------
    // LIFECYCLE
    // -------------------------------------------------------
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            applyFullscreen();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.startAutoRefresh();
        } else {
            if (admobBanner != null) admobBanner.resume();
        }
        if (webView != null) webView.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.stopAutoRefresh();
        } else {
            if (admobBanner != null) admobBanner.pause();
        }
        if (webView != null) webView.onPause();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (USE_APPLOVIN) {
            if (bannerAd != null) bannerAd.destroy();
        } else {
            if (admobBanner != null) admobBanner.destroy();
        }
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        if (billingClient != null) billingClient.endConnection();
    }

    @Override
    public void onBackPressed() {
        webView.evaluateJavascript(
            "window.onBackPressed && window.onBackPressed();",
            value -> {
                if (value == null || value.equals("null") || value.equals("false")) {
                    super.onBackPressed();
                }
            }
        );
    }

    // -------------------------------------------------------
    // UTIL
    // -------------------------------------------------------
    private int dpToPx(int dp) {
        return (int) (dp * getResources().getDisplayMetrics().density);
    }
}
