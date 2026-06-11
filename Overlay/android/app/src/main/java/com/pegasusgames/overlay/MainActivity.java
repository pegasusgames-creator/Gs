package com.pegasusgames.overlay;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;
import androidx.core.content.ContextCompat;

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
import com.android.billingclient.api.ConsumeParams;
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
    private static final String MAX_SDK_KEY              = ""; // TODO: paste SDK key once AppLovin is approved
    private static final String MAX_BANNER_UNIT_ID       = ""; // TODO: paste once AppLovin is approved
    private static final String MAX_INTERSTITIAL_UNIT_ID = ""; // TODO: paste once AppLovin is approved
    private static final String MAX_REWARDED_UNIT_ID     = ""; // TODO: paste once AppLovin is approved
    // Auto-switch: uses AppLovin when SDK key is real, AdMob otherwise
    private static final boolean USE_APPLOVIN = !MAX_SDK_KEY.isEmpty();

    // ── AdMob fallback ────────────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units
    private static final String ADMOB_BANNER_UNIT_ID       = "ca-app-pub-3940256099942544/6300978111";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-3940256099942544/1033173712";
    private static final String ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-3940256099942544/5224354917";

    // ── IAP ───────────────────────────────────────────────────────────────────
    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "coins_small", "coins_medium", "coins_large", "coins_mega",
        "five_lives", "hint_pack", "remove_ads",
        "season_pass_monthly", "starter_pack", "unlimited_lives_1h",
        "unlimited_lives_forever", "weekly_pass"
    ));

    // Subscription SKUs — routed through launchSubscription(), never the
    // one-time INAPP flow.
    private static final Set<String> SUBSCRIPTION_PRODUCTS = new HashSet<>(Arrays.asList(
        "season_pass_monthly", "weekly_pass"
    ));

    // SKUs that are CONSUMABLE — must be consumed via consumeAsync after each
    // purchase, otherwise the user can buy once and never re-buy. Anything in
    // VALID_PRODUCTS but NOT in this set is non-consumable / subscription and
    // acknowledged via acknowledgePurchase. Both flows must complete within
    // Play's 3-day window or the purchase is auto-refunded.
    private static final Set<String> CONSUMABLE_PRODUCTS = new HashSet<>(Arrays.asList(
        "coins_small", "coins_medium", "coins_large", "coins_mega",
        "five_lives", "hint_pack", "starter_pack", "unlimited_lives_1h"
    ));

    private static final Set<String> VALID_REWARD_TYPES = new HashSet<>(Arrays.asList(
        "undo", "skip", "life"
    ));

    private static final int WEBVIEW_BG_COLOR = 0xFFeef4f8;

    // ── Notification scheduling (NOTIFICATIONS_IMPL.md §1) ────────────────────
    private static final int REQ_DAILY_REMINDER       = 1001;
    private static final int REQ_STREAK_AT_RISK       = 1002;
    private static final int REQ_LIVES_REFILLED       = 1003;
    private static final int REQ_RETURN_AFTER_ABSENCE = 1004;
    // Win-back chain — d3 / d7 / d14 / d30 fire if the user goes dark.
    private static final int REQ_WIN_BACK_D3          = 1005;
    private static final int REQ_WIN_BACK_D7          = 1006;
    private static final int REQ_WIN_BACK_D14         = 1007;
    private static final int REQ_WIN_BACK_D30         = 1008;
    private static final String PREF_NOTIFS_ENABLED   = "notifications_enabled";
    private static final String PREF_LAST_PLAYED      = "last_played_ts";
    private static final int NOTIF_CAP_PER_DAY        = 2;
    private static final int POST_NOTIFS_REQUEST_CODE = 9001;
    // Cross-promo install verification — must match CROSS_PROMO list in game.html
    // and the <queries> entries in AndroidManifest.xml. Targets are LIVE Play
    // Store apps only. Pre-release siblings (PipeConnect) added
    // here ONLY after they have Play links.
    private static final Set<String> CROSS_PROMO_PACKAGES = new HashSet<>(Arrays.asList(
        "com.pegasusgames.watersortpuzzle",
        "com.pegasusgames.nonogram",
        "com.pegasusgames.puzzle2048",
        "com.pegasusgames.unblockpuzzle"
    ));


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

        // Play Games Services v2 must be initialized before any PlayGames.*
        // client call; without this every PGS bridge method throws and no-ops.
        try { com.google.android.gms.games.PlayGamesSdk.initialize(this); }
        catch (Throwable e) { Log.d("PGS", "PlayGamesSdk.initialize no-op: " + e.getMessage()); }


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

        // Notification channel only. The runtime POST_NOTIFICATIONS request
        // is NOT made here — growth spec: the JS shim pre-prompts AFTER the
        // first level clear, then calls requestNotificationPermission().
        NotificationHelper.createChannel(this);

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
        if (SUBSCRIPTION_PRODUCTS.contains(productId)) { launchSubscription(productId); return; }
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
        @JavascriptInterface public void restorePurchases()              { MainActivity.this.restorePurchases(); }
        @JavascriptInterface public void openUrl(String url)             { try { startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse(url))); } catch (Exception e) {} }

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
        public boolean hasNotificationPermission() {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true;
            return ContextCompat.checkSelfPermission(
                MainActivity.this,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED;
        }

        @JavascriptInterface
        public void scheduleDailyReminder(int hourOfDay, int minute) {
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.set(java.util.Calendar.HOUR_OF_DAY, hourOfDay);
            cal.set(java.util.Calendar.MINUTE, minute);
            cal.set(java.util.Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(java.util.Calendar.DAY_OF_YEAR, 1);
            }
            scheduleAlarm(
                REQ_DAILY_REMINDER, cal.getTimeInMillis(),
                "daily_reminder",
                getDailyReminderTitle(), getDailyReminderBody());
        }

        @JavascriptInterface
        public void scheduleStreakAtRisk(int streakDays) {
            cancelScheduledAlarm(REQ_STREAK_AT_RISK);
            if (streakDays < 3) return;
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.set(java.util.Calendar.HOUR_OF_DAY, 20);
            cal.set(java.util.Calendar.MINUTE, 30);
            cal.set(java.util.Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(java.util.Calendar.DAY_OF_YEAR, 1);
            }
            String body = "Your " + streakDays + "-day streak ends in 4 hours — keep it alive! 🔥";
            scheduleAlarm(REQ_STREAK_AT_RISK, cal.getTimeInMillis(),
                "streak_at_risk", "Don't break your streak!", body);
        }

        @JavascriptInterface
        public void scheduleLivesRefilled(long whenMillis) {
            cancelScheduledAlarm(REQ_LIVES_REFILLED);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            if (whenMillis <= System.currentTimeMillis()) return;
            scheduleAlarm(REQ_LIVES_REFILLED, whenMillis,
                "lives_refilled", "Your lives are back!", "Ready for another round? ❤️");
        }

        @JavascriptInterface
        public void scheduleWinBack(int dayOffset, String title, String body) {
            if (title == null || body == null) return;
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            int req;
            switch (dayOffset) {
                case 3:  req = REQ_WIN_BACK_D3;  break;
                case 7:  req = REQ_WIN_BACK_D7;  break;
                case 14: req = REQ_WIN_BACK_D14; break;
                case 30: req = REQ_WIN_BACK_D30; break;
                default: return;
            }
            cancelScheduledAlarm(req);
            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.add(java.util.Calendar.DAY_OF_YEAR, dayOffset);
            cal.set(java.util.Calendar.HOUR_OF_DAY, 12);
            cal.set(java.util.Calendar.MINUTE, 0);
            cal.set(java.util.Calendar.SECOND, 0);
            scheduleAlarm(req, cal.getTimeInMillis(),
                "win_back_d" + dayOffset, title, body);
        }

        @JavascriptInterface
        public void cancelAllNotifications() {
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
            cancelScheduledAlarm(REQ_STREAK_AT_RISK);
            cancelScheduledAlarm(REQ_LIVES_REFILLED);
            cancelScheduledAlarm(REQ_RETURN_AFTER_ABSENCE);
            cancelScheduledAlarm(REQ_WIN_BACK_D3);
            cancelScheduledAlarm(REQ_WIN_BACK_D7);
            cancelScheduledAlarm(REQ_WIN_BACK_D14);
            cancelScheduledAlarm(REQ_WIN_BACK_D30);
        }

        @JavascriptInterface
        public void setNotificationsEnabled(boolean enabled) {
            getSharedPreferences("game", MODE_PRIVATE).edit()
                .putBoolean(PREF_NOTIFS_ENABLED, enabled).apply();
            if (!enabled) cancelAllNotifications();
        }

        @JavascriptInterface
        public boolean getNotificationsEnabled() {
            return getSharedPreferences("game", MODE_PRIVATE)
                .getBoolean(PREF_NOTIFS_ENABLED, true);
        }

        @JavascriptInterface
        public void recordLastPlayed() {
            getSharedPreferences("game", MODE_PRIVATE).edit()
                .putLong(PREF_LAST_PLAYED, System.currentTimeMillis()).apply();
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
        }

        // Cross-promo "installed?" check — scoped to the sister-app allowlist
        // so JS can't probe arbitrary packages.
        @JavascriptInterface
        public boolean isAppInstalled(String pkg) {
            if (pkg == null || !CROSS_PROMO_PACKAGES.contains(pkg)) return false;
            try {
                getPackageManager().getPackageInfo(pkg, 0);
                return true;
            } catch (PackageManager.NameNotFoundException e) {
                return false;
            }
        }

        @JavascriptInterface
        public void openPlayStore(String pkg) {
            if (pkg == null || !CROSS_PROMO_PACKAGES.contains(pkg)) return;
            runOnUiThread(() -> {
                android.content.Intent i = new android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse("https://play.google.com/store/apps/details?id=" + pkg));
                i.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
                try { startActivity(i); } catch (Exception e) {}
            });
        }

        @JavascriptInterface
        public void shareText(String body) {
            if (body == null || body.isEmpty()) return;
            runOnUiThread(() -> {
                android.content.Intent send = new android.content.Intent(android.content.Intent.ACTION_SEND);
                send.setType("text/plain");
                send.putExtra(android.content.Intent.EXTRA_TEXT, body);
                try {
                    startActivity(android.content.Intent.createChooser(send, "Share"));
                } catch (android.content.ActivityNotFoundException e) {
                    Log.w("Share", "no chooser available", e);
                }
            });
        }

        // shareImage(base64) — best-effort. The JS share-a-win shim treats
        // shareImage as optional; the text-only path always works.
        @JavascriptInterface
        public void shareImage(String base64Png, String caption) {
            if (caption == null) caption = "";
            final String body = caption;
            runOnUiThread(() -> {
                android.content.Intent send = new android.content.Intent(android.content.Intent.ACTION_SEND);
                send.setType("text/plain");
                send.putExtra(android.content.Intent.EXTRA_TEXT, body);
                try {
                    startActivity(android.content.Intent.createChooser(send, "Share"));
                } catch (android.content.ActivityNotFoundException e) {
                    Log.w("Share", "no chooser available", e);
                }
            });
        }

        @JavascriptInterface
        public void setLeaderboardSize(int n) {
          final int v = Math.max(1000, n);
          runOnUiThread(() -> {
            if (webView != null) {
              webView.evaluateJavascript(
                "window.LEADERBOARD_TOTAL_OVERRIDE = " + v + ";", null);
            }
          });
        }

        // ── Play Games Services bridge (PGS v2) ───────────────────────────────
        // Defensive — no-op while the leaderboard isn't yet created in Play
        // Console (JS LEADERBOARD_ID ships as TODO_ placeholder). The synthetic
        // weekly-tournament fallback in game.html stays active until then.
        @JavascriptInterface
        public void submitScore(String leaderboardId, long score) {
            if (leaderboardId == null || leaderboardId.isEmpty()) return;
            if (leaderboardId.startsWith("TODO_")) return;
            try {
                com.google.android.gms.games.PlayGames.getLeaderboardsClient(MainActivity.this)
                    .submitScore(leaderboardId, score);
            } catch (Throwable e) { Log.d("PGS", "submitScore no-op: " + e.getMessage()); }
        }

        @JavascriptInterface
        public void showLeaderboard(String leaderboardId) {
            if (leaderboardId == null || leaderboardId.isEmpty()) return;
            if (leaderboardId.startsWith("TODO_")) return;
            try {
                com.google.android.gms.games.PlayGames.getLeaderboardsClient(MainActivity.this)
                    .getLeaderboardIntent(leaderboardId)
                    .addOnSuccessListener(intent -> runOnUiThread(() -> {
                        try { startActivityForResult(intent, 9991); }
                        catch (Throwable e) { Log.w("PGS", "leaderboard intent failed", e); }
                    }));
            } catch (Throwable e) { Log.d("PGS", "showLeaderboard no-op: " + e.getMessage()); }
        }

        @JavascriptInterface
        public boolean signInPlayGames() {
            try {
                com.google.android.gms.games.PlayGames.getGamesSignInClient(MainActivity.this).signIn();
                return true;
            } catch (Throwable e) {
                Log.d("PGS", "signInPlayGames no-op: " + e.getMessage());
                return false;
            }
        }

        @JavascriptInterface
        public boolean isPlayGamesAuthenticated() {
            try {
                com.google.android.gms.tasks.Task<com.google.android.gms.games.AuthenticationResult> t =
                    com.google.android.gms.games.PlayGames.getGamesSignInClient(MainActivity.this).isAuthenticated();
                return t != null && t.isComplete() && t.getResult() != null && t.getResult().isAuthenticated();
            } catch (Throwable e) { return false; }
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

    // ── Notifications helpers (NOTIFICATIONS_IMPL.md §3) ──────────────────────
    private void scheduleAlarm(int requestCode, long triggerAtMillis,
                                String type, String title, String body) {
        android.content.Intent intent = new android.content.Intent(this, NotificationReceiver.class);
        intent.putExtra("type", type);
        intent.putExtra("title", title);
        intent.putExtra("body", body);
        intent.putExtra("requestCode", requestCode);

        int flags = android.app.PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= android.app.PendingIntent.FLAG_IMMUTABLE;
        }
        android.app.PendingIntent pi = android.app.PendingIntent.getBroadcast(this, requestCode, intent, flags);

        android.app.AlarmManager am = (android.app.AlarmManager) getSystemService(ALARM_SERVICE);
        if (am == null) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(android.app.AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        } else {
            am.set(android.app.AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        }
    }

    private void cancelScheduledAlarm(int requestCode) {
        android.content.Intent intent = new android.content.Intent(this, NotificationReceiver.class);
        int flags = android.app.PendingIntent.FLAG_NO_CREATE;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= android.app.PendingIntent.FLAG_IMMUTABLE;
        }
        android.app.PendingIntent pi = android.app.PendingIntent.getBroadcast(this, requestCode, intent, flags);
        if (pi != null) {
            android.app.AlarmManager am = (android.app.AlarmManager) getSystemService(ALARM_SERVICE);
            if (am != null) am.cancel(pi);
            pi.cancel();
        }
    }

    private String getDailyReminderTitle() { return "Overlay"; }
    private String getDailyReminderBody()  { return "Your daily picture is ready to reveal!"; }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                            int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == POST_NOTIFS_REQUEST_CODE) {
            boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            webView.evaluateJavascript(
                "window.onNotificationPermissionResult && "
                + "window.onNotificationPermissionResult(" + granted + ");",
                null
            );
        }
    }

}
