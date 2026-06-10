package com.pegasusgames.watersortpuzzle;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;

// IAP signature verification
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;

// Notifications (NOTIFICATIONS_IMPL.md §1)
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.content.SharedPreferences;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.util.Calendar;

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
    // Disabled until this developer is approved on AppLovin. The app ships
    // AdMob-only for now. To re-enable when the SDK key is provided:
    //   1. Paste the real SDK key and unit IDs below
    //   2. Flip USE_APPLOVIN to true (or revert to the !startsWith("ENTER_") check)
    //   3. The "if (false /* MAX_ENABLED */)" blocks below will then short-circuit
    //      to the MAX paths again
    // Paste real values here and flip USE_APPLOVIN to true when the AppLovin
    // developer account is approved.
    private static final String MAX_SDK_KEY              = ""; // TODO: paste SDK key
    private static final String MAX_BANNER_UNIT_ID       = ""; // TODO: paste banner unit id
    private static final String MAX_INTERSTITIAL_UNIT_ID = ""; // TODO: paste interstitial unit id
    private static final String MAX_REWARDED_UNIT_ID     = ""; // TODO: paste rewarded unit id
    // MAX_ENABLED — AppLovin disabled; app uses AdMob only. Flip to true once
    // the SDK key above is real.
    private static final boolean USE_APPLOVIN = false;

    // ── AdMob fallback ────────────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units
    private static final String ADMOB_BANNER_UNIT_ID       = "ca-app-pub-5695494884863768/6958960514";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-5695494884863768/4267242200";
    private static final String ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-5695494884863768/6124390997";

    // ── IAP ───────────────────────────────────────────────────────────────────
    // Paste the app's base64 RSA public key from:
    //   Play Console → Monetize setup → Licensing → "Base64-encoded RSA public key"
    // While the placeholder remains, signature verification is SKIPPED (purchases
    // are still validated via PurchaseState + acknowledgement + productId
    // allowlist, but tampered Purchase objects could pass). Replace before
    // shipping.
    private static final String LICENSE_PUBLIC_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvM4nNdT26CS4M9E8DDh00zEpjKGm7NAx9X/0cjPelRUeZh/LGNrJgwn3DK2Vr6oC5wpPj448/9SnYlnJJqCVNnE98+MMxx0WEf/fBPbs/oPME/gpuv95QGISUUqSVztqZJWz3PTDhNHlkNAQhW35/9UESrV7H37UeZBtADFP0wdNjBWeJtcEJsI5TEvTN2dbhb/tdBms4sRwnN7mrRFkSJqgefy8d2YdG73f9d0S1kPe2dfAvCkx1QXHXj7IgtrqBO/IOKig6KT1oOH5s2Gpf/BGiV+doJ4JQ/Qlnj1EcBHlj7MaGZ4oGNxoZlmkZ7Er2qT4gasLC/DlZVR0htn5xQIDAQAB";

    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "coins_small", "coins_large", "unlimited_undos",
        "five_lives", "unlimited_lives_1h", "unlimited_lives_forever",
        "hint_pack", "starter_pack", "season_pass_monthly",
        "coins_medium", "coins_mega", "weekly_pass"
    ));

    // Subscription SKUs — routed through launchSubscription(), never the
    // one-time INAPP flow.
    private static final Set<String> SUBSCRIPTION_PRODUCTS = new HashSet<>(Arrays.asList(
        "season_pass_monthly", "weekly_pass"
    ));

    // SKUs that are CONSUMABLE — must be consumed via consumeAsync after each
    // purchase, otherwise the user can buy once and never re-buy. Anything in
    // VALID_PRODUCTS but NOT in this set is treated as non-consumable /
    // subscription and acknowledged via acknowledgePurchase. Both flows must
    // complete within Play's 3-day window or the purchase is auto-refunded.
    private static final Set<String> CONSUMABLE_PRODUCTS = new HashSet<>(Arrays.asList(
        "coins_small", "coins_large", "coins_medium", "coins_mega",
        "five_lives", "unlimited_lives_1h",
        "hint_pack", "starter_pack"
    ));

    // Cross-promo install verification — must match PROMO_GAMES in game.html
    // and the <queries> entries in AndroidManifest.xml.
    // Targets are LIVE Play Store apps only. UnblockPuzzle + PipeConnect added
    // here ONLY after they have Play links (currently both pre-release/in-review).
    private static final Set<String> CROSS_PROMO_PACKAGES = new HashSet<>(Arrays.asList(
        "com.pegasusgames.nonogram",
        "com.pegasusgames.puzzle2048",
        "com.pegasusgames.unblockpuzzle"
        // TODO post-release: "com.pegasusgames.pipeconnect" once it has a Play link
    ));
    private static final Set<String> VALID_REWARD_TYPES = new HashSet<>(Arrays.asList(
        "undo", "skip", "life"
    ));

    // Daylight default = medium ocean blue. (Midnight unlock = #0a1628.)
    private static final int WEBVIEW_BG_COLOR = 0xFF3d6a9e;

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
    private static final String PREF_SCHED_COUNT_DAY  = "sched_count_day";
    private static final String PREF_SCHED_COUNT_DATE = "sched_count_date";
    private static final int NOTIF_CAP_PER_DAY        = 2;
    private static final int POST_NOTIFS_REQUEST_CODE = 9001;

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

        // Banner container at bottom — themed background so empty space
        // around the ad blends with the WebView, not a black bar.
        bannerContainer = new FrameLayout(this);
        bannerContainer.setId(android.view.View.generateViewId());
        bannerContainer.setBackgroundColor(android.graphics.Color.TRANSPARENT);
        RelativeLayout.LayoutParams bp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, dpToPx(50));
        bp.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        layout.addView(bannerContainer, bp);
        layout.setBackgroundColor(WEBVIEW_BG_COLOR);

        // WebView above banner. Explicit ALIGN_PARENT_TOP + ABOVE so the
        // height is unambiguously (screen - banner) instead of MATCH_PARENT
        // with a constraint hint. Without this, the WebView occasionally
        // extends BEHIND the banner area and steals touch from the AdView.
        webView = new WebView(this);
        RelativeLayout.LayoutParams wp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.MATCH_PARENT);
        wp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
        wp.addRule(RelativeLayout.ABOVE, bannerContainer.getId());
        layout.addView(webView, wp);
        bannerContainer.bringToFront();
        // Kill any transient WebView scroll during cold-start render storm.
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

        // Create the legacy notification channel for back-compat with older
        // code paths; NotificationReceiver creates its own channels lazily.
        NotificationHelper.createChannel(this);
        // NOTE: Per QUALITY_PLAYBOOK §11.1, we do NOT request POST_NOTIFICATIONS
        // on first launch. The request is triggered by the JS pre-prompt
        // overlay after the first positive milestone (first level complete).

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
        // Register the emulator as a test device so production unit IDs serve
        // test ads in dev builds (otherwise live IDs return "no fill").
        boolean isDebuggable = (getApplicationInfo().flags
            & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;
        if (isDebuggable) {
            com.google.android.gms.ads.RequestConfiguration cfg =
                new com.google.android.gms.ads.RequestConfiguration.Builder()
                    .setTestDeviceIds(java.util.Arrays.asList(
                        com.google.android.gms.ads.AdRequest.DEVICE_ID_EMULATOR))
                    .build();
            MobileAds.setRequestConfiguration(cfg);
        }
        MobileAds.initialize(this, s -> runOnUiThread(() -> {
            loadAdmobBanner(); loadAdmobInterstitial(); loadAdmobRewarded();
        }));
    }

    private void loadAdmobBanner() {
        admobBanner = new com.google.android.gms.ads.AdView(this);
        admobBanner.setAdSize(AdSize.BANNER);
        admobBanner.setAdUnitId(ADMOB_BANNER_UNIT_ID);
        // Fill the container — WRAP_CONTENT lets the AdView re-measure
        // when the test creative finally fills, causing visible jitter
        // for the first ~60s while the cache warms.
        FrameLayout.LayoutParams admobLp = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT);
        bannerContainer.addView(admobBanner, admobLp);
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

    // RSA-SHA1 signature check against the app's Play Console public key.
    // Returns true if verified, false if invalid. Returns true (skip) when the
    // public key is still the placeholder so that local debug builds work
    // before the real key is pasted in.
    private boolean verifyPurchaseSignature(Purchase purchase) {
        if (LICENSE_PUBLIC_KEY == null || LICENSE_PUBLIC_KEY.startsWith("PASTE_")) {
            Log.w("WaterSort", "LICENSE_PUBLIC_KEY is placeholder — signature check skipped.");
            return true;
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
            Log.w("WaterSort", "Purchase signature verify error: " + e.getMessage());
            return false;
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
        @JavascriptInterface public void log(String msg)                 { /* disabled in release */ }
        // Open an arbitrary https URL in the system browser. Used for
        // the Manage Subscriptions deep link and the privacy policy.
        @JavascriptInterface
        public void openUrl(String url) {
            if (url == null || url.length() == 0) return;
            try {
                android.content.Intent i = new android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse(url));
                i.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
            } catch (Exception e) {
                /* no-op — JS will fall back to window.open */
            }
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

        // ── Notifications bridge (NOTIFICATIONS_IMPL.md §2) ───────────────────
        @JavascriptInterface
        public boolean hasNotificationPermission() {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true;
            return ContextCompat.checkSelfPermission(
                MainActivity.this,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED;
        }

        @JavascriptInterface
        public void requestNotificationPermission() {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return;
            runOnUiThread(() -> {
                ActivityCompat.requestPermissions(
                    MainActivity.this,
                    new String[]{ Manifest.permission.POST_NOTIFICATIONS },
                    POST_NOTIFS_REQUEST_CODE
                );
            });
        }

        @JavascriptInterface
        public void scheduleDailyReminder(int hourOfDay, int minute) {
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

            Calendar cal = Calendar.getInstance();
            cal.set(Calendar.HOUR_OF_DAY, hourOfDay);
            cal.set(Calendar.MINUTE, minute);
            cal.set(Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(Calendar.DAY_OF_YEAR, 1);
            }

            scheduleAlarm(
                REQ_DAILY_REMINDER,
                cal.getTimeInMillis(),
                "daily_reminder",
                getDailyReminderTitle(),
                getDailyReminderBody()
            );
        }

        @JavascriptInterface
        public void scheduleStreakAtRisk(int streakDays) {
            cancelScheduledAlarm(REQ_STREAK_AT_RISK);
            if (streakDays < 3) return; // §11.2: only for streaks >= 3
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

            Calendar cal = Calendar.getInstance();
            cal.set(Calendar.HOUR_OF_DAY, 20);
            cal.set(Calendar.MINUTE, 30);
            cal.set(Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(Calendar.DAY_OF_YEAR, 1);
            }

            String body = "Your " + streakDays + "-day streak ends in 4 hours — keep it alive! 🔥";
            scheduleAlarm(
                REQ_STREAK_AT_RISK,
                cal.getTimeInMillis(),
                "streak_at_risk",
                "Don't break your streak!",
                body
            );
        }

        @JavascriptInterface
        public void scheduleLivesRefilled(long whenMillis) {
            cancelScheduledAlarm(REQ_LIVES_REFILLED);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            if (whenMillis <= System.currentTimeMillis()) return;

            scheduleAlarm(
                REQ_LIVES_REFILLED,
                whenMillis,
                "lives_refilled",
                "Your lives are back!",
                "Ready for another round? ❤️"
            );
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

        // Schedule one entry in the win-back chain. Caller passes the day
        // offset (3/7/14/30); we map to a dedicated request code so the
        // chain can be cancelled atomically when the user returns.
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

            // Fire at noon local on the target day so it doesn't collide with
            // the streak-at-risk evening slot or the daily-ready morning slot.
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DAY_OF_YEAR, dayOffset);
            cal.set(Calendar.HOUR_OF_DAY, 12);
            cal.set(Calendar.MINUTE, 0);
            cal.set(Calendar.SECOND, 0);
            scheduleAlarm(req, cal.getTimeInMillis(), "win_back_d" + dayOffset, title, body);
        }

        @JavascriptInterface
        public void setNotificationsEnabled(boolean enabled) {
            getSharedPreferences("game", MODE_PRIVATE)
                .edit()
                .putBoolean(PREF_NOTIFS_ENABLED, enabled)
                .apply();
            if (!enabled) cancelAllNotifications();
        }

        @JavascriptInterface
        public boolean getNotificationsEnabled() {
            return getSharedPreferences("game", MODE_PRIVATE)
                .getBoolean(PREF_NOTIFS_ENABLED, true);
        }

        @JavascriptInterface
        public void recordLastPlayed() {
            getSharedPreferences("game", MODE_PRIVATE)
                .edit()
                .putLong(PREF_LAST_PLAYED, System.currentTimeMillis())
                .apply();
            // If played today, skip today's daily reminder
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
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

        // shareImage(base64) — best-effort. Writes the decoded PNG to the app's
        // external cache and shares via FileProvider when configured; otherwise
        // silently falls back to sharing the accompanying caption only. The JS
        // side passes a caption + base64; the share-a-win shim treats shareImage
        // as optional and the text-only path always works.
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
        // ── Play Games Services bridge (PGS v2) ───────────────────────────────
        // All three methods are defensive — they no-op when PGS isn't yet
        // configured (placeholder games_app_id in strings.xml, or PGS
        // initialization fails). The synthetic weekly-tournament fallback in
        // game.html stays active until real leaderboards are wired in Play
        // Console. See scripts/growth_open_items.md §B.
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
                // We cannot block here; return false synchronously and rely on the JS
                // side to call signInPlayGames() to attempt + retry on next call.
                return t != null && t.isComplete() && t.getResult() != null && t.getResult().isAuthenticated();
            } catch (Throwable e) { return false; }
        }



        // ── Cross-promo install verification ───────────────────────────────────
        // Used by the "More Games" reward flow in game.html. JS calls
        // openPlayStore(pkg) when the user taps a promo card, and later calls
        // isAppInstalled(pkg) to decide whether to grant the +50 coin reward.
        // Only packages in CROSS_PROMO_PACKAGES are checkable to prevent JS
        // from probing arbitrary installed apps via this bridge.
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
                Intent i = new Intent(Intent.ACTION_VIEW,
                    Uri.parse("https://play.google.com/store/apps/details?id=" + pkg));
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                try { startActivity(i); }
                catch (android.content.ActivityNotFoundException e) {
                    Log.w("WaterSort", "Could not open Play Store: " + e.getMessage());
                }
            });
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
        Intent intent = new Intent(this, NotificationReceiver.class);
        intent.putExtra("type", type);
        intent.putExtra("title", title);
        intent.putExtra("body", body);
        intent.putExtra("requestCode", requestCode);

        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent pi = PendingIntent.getBroadcast(this, requestCode, intent, flags);

        AlarmManager am = (AlarmManager) getSystemService(ALARM_SERVICE);
        if (am == null) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        } else {
            am.set(AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        }
    }

    private void cancelScheduledAlarm(int requestCode) {
        Intent intent = new Intent(this, NotificationReceiver.class);
        int flags = PendingIntent.FLAG_NO_CREATE;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent pi = PendingIntent.getBroadcast(this, requestCode, intent, flags);
        if (pi != null) {
            AlarmManager am = (AlarmManager) getSystemService(ALARM_SERVICE);
            if (am != null) am.cancel(pi);
            pi.cancel();
        }
    }

    private String getDailyReminderTitle() {
        return "Water Sort Puzzle";
    }

    private String getDailyReminderBody() {
        return "Your daily Water Sort challenge is ready!";
    }

    // ── Permission result callback (NOTIFICATIONS_IMPL.md §4) ─────────────────
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
