package com.pegasusgames.sokoban;

import com.applovin.sdk.AppLovinMediationProvider;
import com.applovin.sdk.AppLovinSdkInitializationConfiguration;
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
import android.content.pm.PackageManager;
import android.os.Build;
import androidx.core.content.ContextCompat;
import android.Manifest;
import android.util.Log;
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
    private static final String BANNER_AD_UNIT_ID       = ""; // TODO: paste once AppLovin is approved
    private static final String INTERSTITIAL_AD_UNIT_ID = ""; // TODO: paste once AppLovin is approved
    private static final String REWARDED_AD_UNIT_ID     = ""; // TODO: paste once AppLovin is approved

    // WebView background colour — Sunset Orange theme
    private static final int WEBVIEW_BG_COLOR = 0xFF1a1400;

    // -------------------------------------------------------
    // IAP PRODUCT IDs — must match Google Play Console
    // -------------------------------------------------------
    private static final String PRODUCT_REMOVE_ADS = "remove_ads";
    private static final String MAX_SDK_KEY = ""; // TODO: paste SDK key once AppLovin is approved
    private static final Set<String> VALID_PRODUCTS =
        new HashSet<>(Arrays.asList(
        "coins_small", "coins_medium", "coins_large", "coins_mega",
        "five_lives", "hint_pack", "remove_ads",
        "season_pass_monthly", "starter_pack", "unlimited_lives_1h",
        "unlimited_lives_forever", "weekly_pass"
    ));
    // Subscriptions — routed through launchSubscription() (SUBS), never INAPP.
    private static final Set<String> SUBSCRIPTION_PRODUCTS = new HashSet<>(Arrays.asList(
        "season_pass_monthly", "weekly_pass"));

    // ── Notification scheduling (NOTIFICATIONS_IMPL.md §1) ───────────────────
    private static final int REQ_DAILY_REMINDER       = 1001;
    private static final int REQ_STREAK_AT_RISK       = 1002;
    private static final int REQ_LIVES_REFILLED       = 1003;
    private static final int REQ_RETURN_AFTER_ABSENCE = 1004;
    private static final int REQ_WIN_BACK_D3          = 1005;
    private static final int REQ_WIN_BACK_D7          = 1006;
    private static final int REQ_WIN_BACK_D14         = 1007;
    private static final int REQ_WIN_BACK_D30         = 1008;
    private static final String PREF_NOTIFS_ENABLED   = "notifications_enabled";
    private static final String PREF_LAST_PLAYED      = "last_played_ts";
    private static final int NOTIF_CAP_PER_DAY        = 2;
    private static final int POST_NOTIFS_REQUEST_CODE = 9001;
    // Cross-promo targets — LIVE Play Store apps only, excludes self.
    private static final java.util.Set<String> CROSS_PROMO_PACKAGES =
        new java.util.HashSet<>(java.util.Arrays.asList(
            "com.pegasusgames.watersortpuzzle",
            "com.pegasusgames.nonogram",
            "com.pegasusgames.puzzle2048",
            "com.pegasusgames.unblockpuzzle"));
    // SKUs that are CONSUMABLE — must be consumed via consumeAsync after each
    // purchase, otherwise the user can buy once and never re-buy. Anything in
    // VALID_PRODUCTS but NOT in this set is non-consumable / subscription and
    // acknowledged via acknowledgePurchase. Both flows must complete within
    // Play's 3-day window or the purchase is auto-refunded.
    private static final Set<String> CONSUMABLE_PRODUCTS = new HashSet<>(Arrays.asList(
        "coins_small", "coins_medium", "coins_large", "coins_mega",
        "five_lives", "hint_pack", "starter_pack", "unlimited_lives_1h"
    ));


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
        try { com.google.android.gms.games.PlayGamesSdk.initialize(this); }
        catch (Throwable e) { android.util.Log.d("PGS", "init no-op: "+e.getMessage()); }

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

        WebView.setWebContentsDebuggingEnabled(false);
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

        // Init AppLovin MAX (skipped until SDK key is provided).
        if (!MAX_SDK_KEY.isEmpty()) {
            AppLovinSdkInitializationConfiguration initConfig =
                AppLovinSdkInitializationConfiguration.builder(MAX_SDK_KEY, this)
                    .setMediationProvider(AppLovinMediationProvider.MAX)
                    .build();
            AppLovinSdk.getInstance(this).initialize(initConfig, sdkConfig -> runOnUiThread(() -> {
                runOnUiThread(() -> bannerAd.startAutoRefresh());
                bannerAd.loadAd();
                setupInterstitial();
                setupRewarded();
            }));
        }

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
                    billingClient.launchBillingFlow(this,
                        BillingFlowParams.newBuilder().setProductDetailsParamsList(Arrays.asList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(pd)
                                .setOfferToken(offers.get(0).getOfferToken()).build()
                        )).build()));
            });
    }

    private void launchPurchase(String productId) {
        if (!VALID_PRODUCTS.contains(productId)) return;
        if (SUBSCRIPTION_PRODUCTS.contains(productId)) { launchSubscription(productId); return; }
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
    }

    // -------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------
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

    private String getDailyReminderTitle() { return "Pipe Connect"; }
    private String getDailyReminderBody()  { return "Your daily pipe puzzle is ready!"; }

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
