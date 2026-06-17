package com.pegasusgames.afterimage;

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
import android.util.Base64;
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;

public class MainActivity extends Activity {

    // ── AdMob fallback ────────────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units
    private static final String ADMOB_BANNER_UNIT_ID       = "ca-app-pub-2759523698880843/4799635766";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-2759523698880843/3486554099";
    private static final String ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-2759523698880843/9125893586";

    // Play Console → Monetization setup → Licensing → base64-encoded RSA public
    // key. Used by verifyPurchaseSignature() to validate every purchase locally
    // before the reward is granted. Per-app and unique (never shared). Replace
    // the PASTE_ placeholder with this app's real key at release handoff.
    private static final String LICENSE_PUBLIC_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnQNSwlw4+5AQUq7j8MlA7OYBAs5JcW/HDjb9SYVgjcXwBWunOqkGD+bfGe1Mp5nWjNJcPY9nNj97saBcvufBFA7wiX5k+OXCYeZFSOkLxnYcg46RfDYNx7dLaDl160CkgdiulrjoBAiQ6qThhTcPfJymSyWS0dXf62HQe4Z1HlFTw3PhJSqAg8G7jvbxPVE5/+d3WGnXFoXrm55j3jaXwuPpMDZc4QQEQdcRFCNDRYmrWpWPuypn4aGA1dcbgL3Csn3KyUeA0+MFVlT7BUfB8Ag/cOGN6Euu67LmZdzXnh0ypmWxaHhs3EKEadlw0GC+C43a8epZHaDTSnMi3L//pwIDAQAB";

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
        "undo", "skip", "life", "free_coins"
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
        "com.pegasusgames.unblockpuzzle",
        "com.pegasusgames.pipeconnect",
        "com.pegasusgames.hunch",
        "com.pegasusgames.overlay"
    ));

    // AdMob objects
    private com.google.android.gms.ads.AdView admobBanner;
    private InterstitialAd admobInterstitial;
    private RewardedAd     admobRewarded;

    private WebView      webView;
    private FrameLayout  bannerContainer;
    private BillingClient billingClient;
    // ── Ad state (Part 2: FIFO reward queue + backoff + freshness + cadence) ──
    private final java.util.ArrayDeque<String> pendingRewardTypes = new java.util.ArrayDeque<>();
    private boolean interstitialLoading = false;
    private boolean rewardedLoading = false;
    private long interstitialLoadedAt = 0L;
    private long rewardedLoadedAt = 0L;
    private long lastInterstitialAt = 0L;
    private int interstitialFails = 0;
    private int rewardedFails = 0;
    private static final long AD_FRESH_MS = 50L * 60L * 1000L;        // discard ads >50 min old
    private static final long INTERSTITIAL_MIN_GAP_MS = 60L * 1000L;  // >=60s between interstitials
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

        initAdMob();
        setupBilling();
    }

    // ── AdMob fallback ────────────────────────────────────────────────────────
    private boolean _adsInitialized = false;

    // Google UMP consent must resolve BEFORE ads initialize (EEA/UK requirement).
    private void initAdMob() {
        com.google.android.ump.ConsentRequestParameters.Builder _pB =
            new com.google.android.ump.ConsentRequestParameters.Builder();
        boolean _dbg = (getApplicationInfo().flags
            & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;   // debug-only geography
        if (_dbg) {
            _pB.setConsentDebugSettings(
                new com.google.android.ump.ConsentDebugSettings.Builder(this)
                    .setDebugGeography(com.google.android.ump.ConsentDebugSettings
                        .DebugGeography.DEBUG_GEOGRAPHY_EEA)
                    .build());
        }
        com.google.android.ump.ConsentInformation _ci =
            com.google.android.ump.UserMessagingPlatform.getConsentInformation(this);
        _ci.requestConsentInfoUpdate(this, _pB.build(),
            () -> com.google.android.ump.UserMessagingPlatform
                .loadAndShowConsentFormIfRequired(this, e -> initAdsAfterConsent()),
            e -> initAdsAfterConsent());
    }

    // Original ad init, now gated behind consent.
    private void initAdsAfterConsent() {
        if (_adsInitialized) return;
        _adsInitialized = true;
        // Family puzzle game — cap served creatives at G (never adult/suggestive).
        // TODO: tagForChildDirectedTreatment / tagForUnderAgeOfConsent is a SEPARATE
        // manual COPPA / Play-Families decision — do NOT set it here without that call.
        MobileAds.setRequestConfiguration(
            new com.google.android.gms.ads.RequestConfiguration.Builder()
                .setMaxAdContentRating(
                    com.google.android.gms.ads.RequestConfiguration.MAX_AD_CONTENT_RATING_G)
                .build());
        MobileAds.initialize(this, s -> runOnUiThread(() -> {
            loadAdmobBanner(); loadAdmobInterstitial(); // rewarded is lazy-loaded (preloadRewarded)
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
        if (admobInterstitial != null || interstitialLoading) return; // one in flight/loaded at a time
        interstitialLoading = true;
        InterstitialAd.load(this, ADMOB_INTERSTITIAL_UNIT_ID, new AdRequest.Builder().build(),
            new InterstitialAdLoadCallback() {
                @Override public void onAdLoaded(InterstitialAd ad) {
                    admobInterstitial = ad;
                    interstitialLoading = false;
                    interstitialLoadedAt = System.currentTimeMillis();
                    interstitialFails = 0;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            admobInterstitial = null; loadAdmobInterstitial();
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            admobInterstitial = null; loadAdmobInterstitial();
                        }
                    });
                }
                @Override public void onAdFailedToLoad(LoadAdError e) {
                    admobInterstitial = null;
                    interstitialLoading = false;
                    // back off 8s/16s/32s/64s instead of re-requesting immediately
                    new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadAdmobInterstitial, backoffMs(interstitialFails++));
                }
            });
    }

    private void loadAdmobRewarded() {
        if (admobRewarded != null || rewardedLoading) return; // one in flight/loaded at a time
        rewardedLoading = true;
        RewardedAd.load(this, ADMOB_REWARDED_UNIT_ID, new AdRequest.Builder().build(),
            new RewardedAdLoadCallback() {
                @Override public void onAdLoaded(RewardedAd ad) {
                    admobRewarded = ad;
                    rewardedLoading = false;
                    rewardedLoadedAt = System.currentTimeMillis();
                    rewardedFails = 0;
                    ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                        @Override public void onAdDismissedFullScreenContent() {
                            pendingRewardTypes.clear();
                            admobRewarded = null; loadAdmobRewarded();
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            pendingRewardTypes.clear();
                            admobRewarded = null; loadAdmobRewarded();
                        }
                    });
                }
                @Override public void onAdFailedToLoad(LoadAdError e) {
                    admobRewarded = null;
                    rewardedLoading = false;
                    new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadAdmobRewarded, backoffMs(rewardedFails++));
                }
            });
    }

    // Exponential backoff for ad re-requests: 8s, 16s, 32s, then capped at 64s.
    private long backoffMs(int fails) {
        return Math.min(64000L, 8000L * (1L << Math.min(fails, 3)));
    }

    // ── Banner show/hide ──────────────────────────────────────────────────────
    private void hideBanner() {
        runOnUiThread(() -> {
            bannerContainer.setVisibility(android.view.View.GONE);
            if (admobBanner != null) admobBanner.pause();   // PART 1C: pause the AdView while hidden (menu/settings or ads-removed)
        });
    }
    private void showBanner() {
        runOnUiThread(() -> {
            bannerContainer.setVisibility(android.view.View.VISIBLE);
            if (admobBanner != null && bannerContainer.getVisibility() == android.view.View.VISIBLE) admobBanner.resume(); // PART 1C: don't resume a menu-hidden banner  // PART 1C: resume when shown on a gameplay screen
        });
    }

    // ── Interstitial show ─────────────────────────────────────────────────────
    private void showInterstitialAd() {
        runOnUiThread(() -> {
            long now = System.currentTimeMillis();
            if (now - lastInterstitialAt < INTERSTITIAL_MIN_GAP_MS) return; // >=60s apart
            if (admobInterstitial != null && now - interstitialLoadedAt > AD_FRESH_MS) {
                admobInterstitial = null; loadAdmobInterstitial(); return;  // stale -> refresh, skip
            }
            if (admobInterstitial != null) {
                lastInterstitialAt = now;
                admobInterstitial.show(MainActivity.this);
            } else {
                loadAdmobInterstitial();
            }
        });
    }

    // ── Rewarded show ─────────────────────────────────────────────────────────
    // Reward is granted ONLY in the reward callback, never in dismiss.
    private void showRewardedAd(String rewardType) {
        // extra_life is a synonym for life — route to the existing life branch.
        if ("extra_life".equals(rewardType)) rewardType = "life";
        if (!VALID_REWARD_TYPES.contains(rewardType)) return;
        final String type = rewardType;
        runOnUiThread(() -> {
            long now = System.currentTimeMillis();
            if (admobRewarded != null && now - rewardedLoadedAt > AD_FRESH_MS) {
                admobRewarded = null; loadAdmobRewarded();              // stale -> refresh
                webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                return;
            }
            if (admobRewarded != null) {
                pendingRewardTypes.addLast(type);   // FIFO: back-to-back triggers can't drop a reward
                admobRewarded.show(MainActivity.this, item -> {
                    String t = pendingRewardTypes.pollFirst();
                    if (t == null) return;
                    webView.evaluateJavascript(
                        "window.onAdReward && window.onAdReward('" + t + "');", null);
                });
            } else {
                loadAdmobRewarded();                // lazy: nothing ready -> start a load for next time
                webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
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
                if (r.getResponseCode() == BillingClient.BillingResponseCode.OK) { restorePurchases(); queryAndPushPrices(); }
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

    // PART 3B — localized IAP pricing: push BillingClient's locale-formatted
    // prices to the WebView (hardcoded $-strings are the fallback).
    private final java.util.Map<String, String> _localizedPrices =
        new java.util.concurrent.ConcurrentHashMap<>();

    private void queryAndPushPrices() {
        queryPriceType(BillingClient.ProductType.INAPP);
        queryPriceType(BillingClient.ProductType.SUBS);
    }

    private void queryPriceType(String type) {
        boolean wantSub = BillingClient.ProductType.SUBS.equals(type);
        java.util.List<QueryProductDetailsParams.Product> prods = new java.util.ArrayList<>();
        for (String sku : VALID_PRODUCTS) {
            if (SUBSCRIPTION_PRODUCTS.contains(sku) != wantSub) continue;
            prods.add(QueryProductDetailsParams.Product.newBuilder()
                .setProductId(sku).setProductType(type).build());
        }
        if (prods.isEmpty() || billingClient == null) return;
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(prods).build(),
            (res, qpdr) -> {
                for (ProductDetails pd : qpdr.getProductDetailsList()) {
                    String price = null;
                    if (pd.getOneTimePurchaseOfferDetails() != null) {
                        price = pd.getOneTimePurchaseOfferDetails().getFormattedPrice();
                    } else if (pd.getSubscriptionOfferDetails() != null
                               && !pd.getSubscriptionOfferDetails().isEmpty()) {
                        java.util.List<ProductDetails.PricingPhase> ph =
                            pd.getSubscriptionOfferDetails().get(0)
                              .getPricingPhases().getPricingPhaseList();
                        if (!ph.isEmpty()) price = ph.get(ph.size() - 1).getFormattedPrice();
                    }
                    if (price != null) _localizedPrices.put(pd.getProductId(), price);
                }
                pushPricesToWeb();
            });
    }

    private void pushPricesToWeb() {
        if (_localizedPrices.isEmpty() || webView == null) return;
        final String json = new org.json.JSONObject(_localizedPrices).toString();
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
    // public key is still a placeholder so local debug builds work before the
    // real key is pasted in.
    private boolean verifyPurchaseSignature(Purchase purchase) {
        if (LICENSE_PUBLIC_KEY == null || LICENSE_PUBLIC_KEY.startsWith("PASTE_")) {
            Log.w("IAP", "LICENSE_PUBLIC_KEY is placeholder — signature check skipped.");
            if ((getApplicationInfo().flags
                & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) == 0) {
                return false;  // PART 3A fail-closed: never grant on a placeholder key in release
            }
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
            Log.w("IAP", "Purchase signature verify error: " + e.getMessage());
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
        @JavascriptInterface public void preloadRewarded()              { runOnUiThread(() -> loadAdmobRewarded()); }
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
        if (admobBanner != null) admobBanner.resume();
        if (webView != null) webView.onResume();
    }

    @Override protected void onPause() {
        super.onPause();
        if (admobBanner != null) admobBanner.pause();
        if (webView != null) webView.onPause();
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        if (admobBanner != null) admobBanner.destroy();
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

    private String getDailyReminderTitle() { return "Afterimage"; }
    private String getDailyReminderBody()  { return "Your daily echo puzzle is ready!"; }

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
