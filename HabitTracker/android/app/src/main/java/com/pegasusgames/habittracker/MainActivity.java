package com.pegasusgames.habittracker;

// ─────────────────────────────────────────────────────────────────────────────
// UTILITY SHELL wrapper (docs/UTILITY_SHELL.md). Scaffold new tools from this
// app:  python3 scripts/scaffold_flagship.py <App> --from HabitTracker ...
//
// Differences from the game wrapper (Afterimage family):
//   * system bars stay VISIBLE (a tool must not hide the clock); the root view
//     is padded by the system-bar / cutout / keyboard insets, and game.html
//     colours the bars through setSystemBarColors(hex, lightBackground);
//   * no Play Games Services (PGS is for games only);
//   * user reminders: scheduleReminder(slot, h, m, daysMask, title, body) —
//     persisted, re-armed after every fire, after reboot and after updates;
//   * haptic(kind), copyToClipboard / readClipboard, getFontScale(),
//     openNotificationSettings() for the tool UI;
//   * IAP = remove_ads + pro_lifetime (both non-consumable, no subscriptions).
// ─────────────────────────────────────────────────────────────────────────────

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;
import androidx.core.content.ContextCompat;

// AdMob
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

// Firebase (optional — only active when app/google-services.json exists)
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

    // ── AdMob ─────────────────────────────────────────────────────────────────
    // Get from: apps.admob.com → Your App → Ad Units (scripts/set_app_ids.py)
    private static final String ADMOB_BANNER_UNIT_ID       = "ca-app-pub-3940256099942544/6300978111";
    private static final String ADMOB_INTERSTITIAL_UNIT_ID = "ca-app-pub-3940256099942544/1033173712";
    private static final String ADMOB_REWARDED_UNIT_ID     = "ca-app-pub-3940256099942544/5224354917";

    // Play Console → Monetization setup → Licensing → base64-encoded RSA public
    // key. Used by verifyPurchaseSignature() to validate every purchase locally
    // before the reward is granted. Per-app and unique (never shared). Replace
    // the PASTE_ placeholder with this app's real key at release handoff.
    private static final String LICENSE_PUBLIC_KEY = "PASTE_LICENSE_PUBLIC_KEY";

    // ── IAP ───────────────────────────────────────────────────────────────────
    // Generated from metadata/iaps.json — never hand-curate (IAP invariant 1).
    private static final Set<String> VALID_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "pro_lifetime"
    ));

    // The utility shell sells no subscriptions. A future SUBS SKU must be added
    // here AND to iaps.json "subscriptions" so it routes through launchSubscription().
    private static final Set<String> SUBSCRIPTION_PRODUCTS = new HashSet<>(Arrays.asList(
        /* none — utility apps sell one-time unlocks only */
    ));

    // SKUs that are CONSUMABLE — consumed via consumeAsync after each purchase.
    // Anything in VALID_PRODUCTS but NOT in this set is non-consumable and
    // acknowledged via acknowledgePurchase (Play auto-refunds after 3 days
    // otherwise). Both utility SKUs are permanent unlocks.
    private static final Set<String> CONSUMABLE_PRODUCTS = new HashSet<>(Arrays.asList(
        /* none — remove_ads and pro_lifetime are non-consumable */
    ));

    // Purchases that turn the banner + interstitials off for good.
    private static final Set<String> AD_FREE_PRODUCTS = new HashSet<>(Arrays.asList(
        "remove_ads", "pro_lifetime"
    ));

    // Every reward type game.html requests MUST be listed — an unlisted type is
    // dropped silently (no ad, no reward). Gate: scripts/check_reward_types_native.py
    private static final Set<String> VALID_REWARD_TYPES = new HashSet<>(Arrays.asList(
        "theme_trial"
    ));

    // Launch colour (before game.html paints): the Daylight background.
    private static final int WEBVIEW_BG_COLOR = 0xFFF3F0FA;

    // ── Notification scheduling (NOTIFICATIONS_IMPL.md §1) ────────────────────
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
    private static final String PREF_AD_FREE          = "ad_free";
    private static final String PREF_BAR_COLOR        = "bar_color";
    private static final String PREF_BAR_LIGHT        = "bar_light";
    private static final int POST_NOTIFS_REQUEST_CODE = 9001;
    // Cross-promo install verification — LIVE Play Store apps only (wrapper
    // infra shared with the game track; the utility shell links to the
    // developer page instead, so this list is informational here).
    private static final Set<String> CROSS_PROMO_PACKAGES = new HashSet<>(Arrays.asList(
        "com.pegasusgames.watersortpuzzle",
        "com.pegasusgames.nonogram",
        "com.pegasusgames.puzzle2048",
        "com.pegasusgames.unblockpuzzle"
    ));

    // AdMob objects
    private com.google.android.gms.ads.AdView admobBanner;
    private InterstitialAd admobInterstitial;
    private RewardedAd     admobRewarded;

    private RelativeLayout rootLayout;
    private WebView      webView;
    private FrameLayout  bannerContainer;
    private BillingClient billingClient;
    // ── Ad state (FIFO reward queue + backoff + freshness + cadence) ──────────
    private final java.util.ArrayDeque<String> pendingRewardTypes = new java.util.ArrayDeque<>();
    private boolean interstitialLoading = false;
    private boolean rewardedLoading = false;
    private long interstitialLoadedAt = 0L;
    private long rewardedLoadedAt = 0L;
    private long lastInterstitialAt = 0L;
    private int interstitialFails = 0;
    private int rewardedFails = 0;
    private static final long AD_FRESH_MS = 50L * 60L * 1000L;             // discard ads >50 min old
    private static final long INTERSTITIAL_MIN_GAP_MS = 3L * 60L * 1000L;  // >=3 min between interstitials
    // Banner visibility = wanted by game.html AND keyboard closed AND not ad-free.
    private boolean bannerWanted = true;
    private boolean imeVisible = false;
    private FirebaseAnalytics firebaseAnalytics;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        rootLayout = new RelativeLayout(this);
        setContentView(rootLayout);

        // Banner container at bottom
        bannerContainer = new FrameLayout(this);
        bannerContainer.setId(View.generateViewId());
        RelativeLayout.LayoutParams bp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, dpToPx(50));
        bp.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        rootLayout.addView(bannerContainer, bp);
        if (isAdFree()) { bannerWanted = false; bannerContainer.setVisibility(View.GONE); }

        // WebView above banner
        webView = new WebView(this);
        RelativeLayout.LayoutParams wp = new RelativeLayout.LayoutParams(
            RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.MATCH_PARENT);
        // ALIGN_PARENT_TOP + ABOVE so WebView height is unambiguously
        // (screen - banner) instead of MATCH_PARENT; banner must draw on top.
        wp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
        wp.addRule(RelativeLayout.ABOVE, bannerContainer.getId());
        rootLayout.addView(webView, wp);
        bannerContainer.bringToFront();
        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);

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
        // game.html scales its own type from getFontScale() (rem-based layout),
        // so the WebView must not multiply it a second time.
        ws.setTextZoom(100);

        // System bars: visible, coloured from the last theme game.html chose.
        SharedPreferences gp = getSharedPreferences("game", MODE_PRIVATE);
        int barColor = gp.getInt(PREF_BAR_COLOR, WEBVIEW_BG_COLOR);
        boolean barLight = gp.getBoolean(PREF_BAR_LIGHT, true);
        webView.setBackgroundColor(barColor);
        setupSystemBars();
        applySystemBarColors(barColor, barLight);

        NativeBridge bridge = new NativeBridge();
        webView.addJavascriptInterface(bridge, "Android");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, android.webkit.WebResourceRequest req) {
                String _u = (req != null && req.getUrl() != null) ? req.getUrl().toString() : "";
                if (_u.startsWith("file:///android_asset")) return false;   // keep in-app nav in the WebView
                try { startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse(_u))); } catch (Exception ignored) {}
                return true;   // external links open in the browser, never the app WebView
            }
            @Override public void onPageFinished(WebView view, String url) {
                runOnUiThread(() ->
                    webView.evaluateJavascript("window.onAdMobLoaded && window.onAdMobLoaded();", null));
            }
        });
        webView.loadUrl("file:///android_asset/game.html");

        try { firebaseAnalytics = FirebaseAnalytics.getInstance(this); }
        catch (Throwable t) { firebaseAnalytics = null; } // no google-services.json

        // Notification channel only. POST_NOTIFICATIONS is requested in context
        // by game.html (after the user turns a reminder on) via
        // requestNotificationPermission() — never at launch.
        NotificationHelper.createChannel(this);
        // Re-arm user reminders (covers force-stop / alarms dropped by the OS).
        NotificationHelper.rearmAll(this);

        initAdMob();
        setupBilling();
    }

    // ── System bars + insets ──────────────────────────────────────────────────
    // API 30+: draw behind the bars and pad the root by systemBars | cutout,
    // bottom = max(navigation bar, keyboard) so the focused input stays visible.
    // API 24-29: the decor keeps fitting the bars (adjustResize in the manifest
    // handles the keyboard) and only the bar colours are set.
    private void setupSystemBars() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) return;
        try {
            getWindow().setDecorFitsSystemWindows(false);
            getWindow().setStatusBarColor(Color.TRANSPARENT);
            getWindow().setNavigationBarColor(Color.TRANSPARENT);
            getWindow().setNavigationBarContrastEnforced(false);
        } catch (Exception ignored) {}
        rootLayout.setOnApplyWindowInsetsListener((v, insets) -> {
            android.graphics.Insets bars = insets.getInsets(
                android.view.WindowInsets.Type.systemBars()
                | android.view.WindowInsets.Type.displayCutout());
            android.graphics.Insets ime = insets.getInsets(android.view.WindowInsets.Type.ime());
            boolean imeOpen = ime.bottom > bars.bottom;
            v.setPadding(bars.left, bars.top, bars.right, Math.max(bars.bottom, ime.bottom));
            if (imeOpen != imeVisible) { imeVisible = imeOpen; applyBannerVisibility(); }
            return insets;
        });
        rootLayout.requestApplyInsets();
    }

    @SuppressWarnings("deprecation")
    private void applySystemBarColors(int color, boolean lightBackground) {
        rootLayout.setBackgroundColor(color);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            android.view.WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                int mask = android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                         | android.view.WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(lightBackground ? mask : 0, mask);
            }
            return;
        }
        getWindow().setStatusBarColor(color);
        getWindow().setNavigationBarColor(color);
        View decor = getWindow().getDecorView();
        int f = decor.getSystemUiVisibility();
        int light = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) light |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        decor.setSystemUiVisibility(lightBackground ? (f | light) : (f & ~light));
    }

    private boolean isAdFree() {
        return getSharedPreferences("game", MODE_PRIVATE).getBoolean(PREF_AD_FREE, false);
    }

    // ── AdMob ─────────────────────────────────────────────────────────────────
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

    private void initAdsAfterConsent() {
        if (_adsInitialized) return;
        _adsInitialized = true;
        // General-audience tool — cap served creatives at G.
        // tagForChildDirectedTreatment / tagForUnderAgeOfConsent is a SEPARATE
        // manual COPPA / Play-Families decision — do NOT set it here without that call.
        MobileAds.setRequestConfiguration(
            new com.google.android.gms.ads.RequestConfiguration.Builder()
                .setMaxAdContentRating(
                    com.google.android.gms.ads.RequestConfiguration.MAX_AD_CONTENT_RATING_G)
                .build());
        MobileAds.initialize(this, s -> runOnUiThread(() -> {
            // Ad-free owners never load a banner or interstitial; rewarded stays
            // lazy (preloadRewarded) for the optional theme trial.
            if (!isAdFree()) { loadAdmobBanner(); loadAdmobInterstitial(); }
        }));
    }

    private void loadAdmobBanner() {
        if (admobBanner != null) return;
        admobBanner = new com.google.android.gms.ads.AdView(this);
        admobBanner.setAdSize(AdSize.BANNER);
        admobBanner.setAdUnitId(ADMOB_BANNER_UNIT_ID);
        bannerContainer.addView(admobBanner, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT,
            android.view.Gravity.CENTER));
        admobBanner.loadAd(new AdRequest.Builder().build());
    }

    private void loadAdmobInterstitial() {
        if (admobInterstitial != null || interstitialLoading || isAdFree()) return;
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
                    new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadAdmobInterstitial, backoffMs(interstitialFails++));
                }
            });
    }

    private void loadAdmobRewarded() {
        if (admobRewarded != null || rewardedLoading) return;
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
                            webView.evaluateJavascript("window.onAdDismissed && window.onAdDismissed();", null);
                        }
                        @Override public void onAdFailedToShowFullScreenContent(com.google.android.gms.ads.AdError e) {
                            pendingRewardTypes.clear();
                            admobRewarded = null; loadAdmobRewarded();
                            webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null);
                        }
                    });
                }
                @Override public void onAdFailedToLoad(LoadAdError e) {
                    admobRewarded = null;
                    rewardedLoading = false;
                    if (rewardedFails < 4) new android.os.Handler(android.os.Looper.getMainLooper())
                        .postDelayed(MainActivity.this::loadAdmobRewarded, backoffMs(rewardedFails++));
                }
            });
    }

    // Exponential backoff for ad re-requests: 8s, 16s, 32s, then capped at 64s.
    private long backoffMs(int fails) {
        return Math.min(64000L, 8000L * (1L << Math.min(fails, 3)));
    }

    // ── Banner show/hide ──────────────────────────────────────────────────────
    private void applyBannerVisibility() {
        runOnUiThread(() -> {
            boolean show = bannerWanted && !imeVisible && !isAdFree();
            bannerContainer.setVisibility(show ? View.VISIBLE : View.GONE);
            if (admobBanner != null) { if (show) admobBanner.resume(); else admobBanner.pause(); }
        });
    }
    private void hideBanner() { bannerWanted = false; applyBannerVisibility(); }
    private void showBanner() {
        bannerWanted = true;
        runOnUiThread(() -> { if (_adsInitialized && admobBanner == null && !isAdFree()) loadAdmobBanner(); });
        applyBannerVisibility();
    }

    // ── Interstitial show ─────────────────────────────────────────────────────
    // game.html decides WHEN (Ads.naturalBreak: natural break, not first
    // session, >=3 min apart, never for ad-free owners); this is the native floor.
    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (isAdFree()) return;
            long now = System.currentTimeMillis();
            if (now - lastInterstitialAt < INTERSTITIAL_MIN_GAP_MS) return;
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
        if (!VALID_REWARD_TYPES.contains(rewardType)) {
            runOnUiThread(() -> webView.evaluateJavascript("window.onAdNotReady && window.onAdNotReady();", null));
            return;
        }
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
                rewardedFails = 0;
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
                else if (r.getResponseCode() == BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED)
                    restorePurchases();
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
        if (billingClient == null || !billingClient.isReady()) {
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onPurchaseUnavailable && window.onPurchaseUnavailable('" + productId + "');", null));
            return;
        }
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
                else runOnUiThread(() -> webView.evaluateJavascript(
                    "window.onPurchaseUnavailable && window.onPurchaseUnavailable('" + productId + "');", null));
            });
    }

    // Localized IAP pricing: push BillingClient's locale-formatted prices to the
    // WebView (the $-strings in game.html's PRODUCTS table are the fallback).
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
            if (AD_FREE_PRODUCTS.contains(id)) {
                getSharedPreferences("game", MODE_PRIVATE).edit().putBoolean(PREF_AD_FREE, true).apply();
                hideBanner();
            }
            runOnUiThread(() -> webView.evaluateJavascript(
                "window.onPurchaseSuccess && window.onPurchaseSuccess('" + id + "');", null));
        }
    }

    // RSA-SHA1 signature check against the app's Play Console public key.
    // Returns true if verified, false if invalid. Returns true (skip) when the
    // public key is still a placeholder AND the build is debuggable, so local
    // debug builds work before the real key is pasted in.
    private boolean verifyPurchaseSignature(Purchase purchase) {
        if (LICENSE_PUBLIC_KEY == null || LICENSE_PUBLIC_KEY.startsWith("PASTE_")) {
            Log.w("IAP", "LICENSE_PUBLIC_KEY is placeholder — signature check skipped.");
            if ((getApplicationInfo().flags
                & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) == 0) {
                return false;  // fail-closed: never grant on a placeholder key in release
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
        if (billingClient == null || !billingClient.isReady()) return;
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build(),
            (r, purchases) -> {
                for (Purchase p : purchases) handlePurchase(p);
                runOnUiThread(() -> webView.evaluateJavascript(
                    "window.onRestoreComplete && window.onRestoreComplete(" + purchases.size() + ");", null));
            });
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

        // System-bar colours follow the in-app theme (hex "#rrggbb").
        @JavascriptInterface
        public void setSystemBarColors(String hex, boolean lightBackground) {
            final int c;
            try { c = Color.parseColor(hex); } catch (Exception e) { return; }
            getSharedPreferences("game", MODE_PRIVATE).edit()
                .putInt(PREF_BAR_COLOR, c).putBoolean(PREF_BAR_LIGHT, lightBackground).apply();
            runOnUiThread(() -> { applySystemBarColors(c, lightBackground); webView.setBackgroundColor(c); });
        }

        // System font scale (Settings → Display → Font size); game.html scales rem from it.
        @JavascriptInterface
        public float getFontScale() { return getResources().getConfiguration().fontScale; }

        // Haptics through the view — honours the system "touch feedback" setting,
        // needs no VIBRATE permission. kind: "tap" | "success" | "reject".
        @JavascriptInterface
        public void haptic(String kind) {
            runOnUiThread(() -> {
                if (webView == null) return;
                int c = HapticFeedbackConstants.KEYBOARD_TAP;
                if ("success".equals(kind)) {
                    c = Build.VERSION.SDK_INT >= Build.VERSION_CODES.R
                        ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.LONG_PRESS;
                } else if ("reject".equals(kind)) {
                    c = Build.VERSION.SDK_INT >= Build.VERSION_CODES.R
                        ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS;
                }
                webView.performHapticFeedback(c);
            });
        }

        @JavascriptInterface
        public void copyToClipboard(String text) {
            if (text == null) return;
            runOnUiThread(() -> {
                ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("Habit Tracker", text));
            });
        }

        @JavascriptInterface
        public String readClipboard() {
            try {
                ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                if (cm == null || !cm.hasPrimaryClip()) return "";
                ClipData cd = cm.getPrimaryClip();
                if (cd == null || cd.getItemCount() == 0) return "";
                CharSequence s = cd.getItemAt(0).coerceToText(MainActivity.this);
                return s == null ? "" : s.toString();
            } catch (Exception e) { return ""; }
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

        // In-context permission ask (game.html calls this only after the user
        // turns a reminder on). Always answers through
        // window.onNotificationPermissionResult(granted).
        @JavascriptInterface
        public void requestNotificationPermission() {
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT >= 33
                        && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                           != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},
                        POST_NOTIFS_REQUEST_CODE);
                } else {
                    webView.evaluateJavascript("window.onNotificationPermissionResult && "
                        + "window.onNotificationPermissionResult(" + hasNotificationPermission() + ");", null);
                }
            });
        }

        @JavascriptInterface
        public boolean hasNotificationPermission() {
            boolean granted = Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU
                || ContextCompat.checkSelfPermission(MainActivity.this,
                       Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
            android.app.NotificationManager nm =
                (android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            return granted && (nm == null || nm.areNotificationsEnabled());
        }

        @JavascriptInterface
        public void openNotificationSettings() {
            runOnUiThread(() -> {
                android.content.Intent i;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    i = new android.content.Intent(android.provider.Settings.ACTION_APP_NOTIFICATION_SETTINGS);
                    i.putExtra(android.provider.Settings.EXTRA_APP_PACKAGE, getPackageName());
                } else {
                    i = new android.content.Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                        android.net.Uri.parse("package:" + getPackageName()));
                }
                try { startActivity(i); } catch (Exception ignored) {}
            });
        }

        // ── User reminders (utility shell) ────────────────────────────────────
        // slot 0..63 (0 = the app-wide daily check-in); daysMask bit 0 = Sunday …
        // bit 6 = Saturday (0 or 127 = every day). Persisted in SharedPreferences
        // "reminders" and re-armed after each fire, reboot and app update.
        @JavascriptInterface
        public void scheduleReminder(int slot, int hourOfDay, int minute, int daysMask,
                                     String title, String body) {
            if (slot < 0 || slot > NotificationHelper.MAX_SLOT || title == null || body == null) return;
            NotificationHelper.saveReminder(MainActivity.this, slot, hourOfDay, minute, daysMask, title, body);
            NotificationHelper.armReminder(MainActivity.this, slot);
        }

        @JavascriptInterface
        public void cancelReminder(int slot) {
            NotificationHelper.removeReminder(MainActivity.this, slot);
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
            String body = "Your " + streakDays + "-day streak ends at midnight.";
            scheduleAlarm(REQ_STREAK_AT_RISK, cal.getTimeInMillis(),
                "streak_at_risk", getDailyReminderTitle(), body);
        }

        @JavascriptInterface
        public void scheduleLivesRefilled(long whenMillis) {
            cancelScheduledAlarm(REQ_LIVES_REFILLED);   // games only — kept for wrapper parity
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
            NotificationHelper.removeAllReminders(MainActivity.this);
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
            if (pkg == null || !(CROSS_PROMO_PACKAGES.contains(pkg) || pkg.equals(getPackageName()))) return;
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

        // shareImage(base64) — best-effort text share (kept for wrapper parity).
        @JavascriptInterface
        public void shareImage(String base64Png, String caption) {
            shareText(caption == null ? "" : caption);
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

    // ── Lifecycle ─────────────────────────────────────────────────────────────
    @Override protected void onResume() {
        super.onResume();
        if (admobBanner != null && bannerContainer.getVisibility() == View.VISIBLE) admobBanner.resume();
        if (webView != null) {
            webView.onResume();
            webView.evaluateJavascript("window.onAppResume && window.onAppResume();", null);
        }
    }

    @Override protected void onPause() {
        super.onPause();
        if (admobBanner != null) admobBanner.pause();
        if (webView != null) {
            webView.evaluateJavascript("window.onAppPause && window.onAppPause();", null);
            webView.onPause();
        }
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

    private String getDailyReminderTitle() { return "Habit Tracker"; }
    private String getDailyReminderBody()  { return "Time to check in on today's habits."; }

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
