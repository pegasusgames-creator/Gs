#!/usr/bin/env python3
"""remove_applovin_longtail.py — replace AppLovin MAX with AdMob in every
long-tail app (the AppLovin-only wrapper), so AppLovin is gone portfolio-wide.

Every long-tail MainActivity carries the SAME AppLovin ad layer (verified
2026-10-12: one normalised structure across all 161 apps), with a placeholder
SDK key — those apps earned nothing. This swaps that layer for AdMob + Google
UMP consent, keeping the JS bridge (showInterstitial / showRewarded /
hideBannerAd / showBannerAd / purchase) byte-compatible for game.html:

  MainActivity.java
    * com.applovin imports            -> AdMob + UMP imports
    * MAX unit IDs                    -> Google TEST unit IDs (pre_publish_check
                                         blocks them; set real ones with
                                         scripts/set_app_ids.py)
    * MaxAdView / MaxInterstitialAd / MaxRewardedAd -> AdView / InterstitialAd / RewardedAd
    * AppLovinSdk.initialize          -> UMP consent -> MobileAds.initialize
    * interstitial / rewarded loaders -> AdMob load with capped backoff;
                                         a rewarded request with no fill now calls
                                         window.onAdNotReady(type) (was: silence)
    * startAutoRefresh/stopAutoRefresh -> AdView.resume()/pause()
    * FirebaseAnalytics in try/catch (app runs without google-services.json)
    * setWebContentsDebuggingEnabled(true) -> debuggable builds only
  app/build.gradle  — AppLovin deps -> play-services-ads + UMP; minSdk 24
                      (AppLovin 13.x already needed 24, so these builds were
                      failing); google-services plugin only when its json exists
  AndroidManifest   — drop applovin.sdk.key; AdMob APPLICATION_ID placeholder
                      -> Google TEST app ID (a malformed ID crashes AdMob at launch)
  settings.gradle   — drop the AppLovin maven repo
  proguard-rules    — drop the AppLovin-only Amazon stubs
  game.html         — the "AppLovin MAX / IAP bridge" comment

Every edit is an exact match against the shared template; an app whose file
deviates is reported and left untouched (nothing is half-migrated).

Usage:  python3 scripts/remove_applovin_longtail.py [--dry-run] [App ...]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", "node_modules"}

TEST_APP_ID = "ca-app-pub-3940256099942544~3347511713"
TEST_UNITS = {"BANNER_AD_UNIT_ID": "ca-app-pub-3940256099942544/6300978111",
              "INTERSTITIAL_AD_UNIT_ID": "ca-app-pub-3940256099942544/1033173712",
              "REWARDED_AD_UNIT_ID": "ca-app-pub-3940256099942544/5224354917"}

ADMOB_IMPORTS = """import com.google.android.gms.ads.AdError;
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
"""

INIT_OLD = """        // Init AppLovin MAX
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
"""
INIT_NEW = """        // Google UMP consent first (EEA/UK requirement), then AdMob.
        final ConsentInformation consent = UserMessagingPlatform.getConsentInformation(this);
        consent.requestConsentInfoUpdate(this, new ConsentRequestParameters.Builder().build(),
            () -> UserMessagingPlatform.loadAndShowConsentFormIfRequired(this, formError -> startAds(consent)),
            requestError -> startAds(consent));
        if (consent.canRequestAds()) startAds(consent);
"""

ADS_OLD_START = """    // -------------------------------------------------------
    // Interstitial
    // -------------------------------------------------------
    private void setupInterstitial() {"""
ADS_OLD_END = """    // -------------------------------------------------------
    // Billing
    // -------------------------------------------------------"""
ADS_NEW = """    // -------------------------------------------------------
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

"""

JAVA_SUBS = [
    ("        bannerAd = new MaxAdView(BANNER_AD_UNIT_ID, this);\n",
     "        bannerAd = new AdView(this);\n"
     "        bannerAd.setAdUnitId(BANNER_AD_UNIT_ID);\n"
     "        bannerAd.setAdSize(AdSize.BANNER);\n"),
    ("    private MaxAdView         bannerAd;\n", "    private AdView            bannerAd;\n"),
    ("    private MaxInterstitialAd interstitialAd;\n", "    private InterstitialAd    interstitialAd;\n"),
    ("    private MaxRewardedAd     rewardedAd;\n", "    private RewardedAd        rewardedAd;\n"),
    ("        if (bannerAd != null) bannerAd.startAutoRefresh();\n", "        if (bannerAd != null) bannerAd.resume();\n"),
    ("        if (bannerAd != null) bannerAd.stopAutoRefresh();\n", "        if (bannerAd != null) bannerAd.pause();\n"),
    ("        firebaseAnalytics = FirebaseAnalytics.getInstance(this);\n",
     "        try { firebaseAnalytics = FirebaseAnalytics.getInstance(this); }\n"
     "        catch (Throwable t) { firebaseAnalytics = null; } // no google-services.json\n"),
    ("        WebView.setWebContentsDebuggingEnabled(true);\n",
     "        WebView.setWebContentsDebuggingEnabled(\n"
     "            (getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0);\n"),
    (INIT_OLD, INIT_NEW),
]

# Present in only part of the long tail (74 apps already pass false).
OPTIONAL_SUBS = {"        WebView.setWebContentsDebuggingEnabled(true);\n"}


def migrate_java(s: str):
    out = s
    if "com.applovin" not in out:
        return None, "no AppLovin"
    out = re.sub(r"^import com\.applovin\.[\w.]+;\n", "", out, flags=re.M)
    # put AdMob imports where the first remaining import block starts after the package line
    out = re.sub(r"^(package [\w.]+;\n\n)", lambda m: m.group(1) + ADMOB_IMPORTS, out, count=1, flags=re.M)
    for old, new in JAVA_SUBS:
        if old not in out:
            if old in OPTIONAL_SUBS:
                continue
            return None, f"template mismatch: {old.strip().splitlines()[0][:60]!r}"
        out = out.replace(old, new, 1)
    a, b = out.find(ADS_OLD_START), out.find(ADS_OLD_END)
    if a < 0 or b < 0 or b < a:
        return None, "template mismatch: interstitial/rewarded block"
    out = out[:a] + ADS_NEW + out[b:]
    comment = re.compile(r"    // -+\n    // AppLovin MAX ad unit IDs[^\n]*\n    // -+\n")
    if not comment.search(out):
        return None, "template mismatch: MAX unit-ID comment"
    out = comment.sub("    // -------------------------------------------------------\n"
                      "    // AdMob ad unit IDs — Google TEST units until scripts/set_app_ids.py\n"
                      "    // sets the real ones (pre_publish_check blocks test IDs).\n"
                      "    // -------------------------------------------------------\n", out, count=1)
    for k, v in TEST_UNITS.items():
        out, n = re.subn(r'(private static final String %s\s*=\s*")[^"]*(")' % k, r"\g<1>%s\g<2>" % v, out)
        if n != 1:
            return None, f"template mismatch: {k}"
    if re.search(r"applovin|\bMax[A-Z]\w*", out, re.I):
        left = re.findall(r".*(?:applovin|\bMax[A-Z]\w*).*", out, re.I)[:2]
        return None, f"AppLovin left after migration: {left}"
    return out, "ok"


def migrate_gradle(s: str):
    old = re.compile(r"    // AppLovin MAX[^\n]*\n    implementation 'com\.applovin:applovin-sdk:[^']*'\n"
                     r"    implementation 'com\.applovin\.mediation:google-adapter:[^']*'\n")
    if not old.search(s):
        return None, "template mismatch: AppLovin deps"
    s = old.sub("    // Google Mobile Ads (AdMob) + UMP consent\n"
                "    implementation 'com.google.android.gms:play-services-ads:25.3.0'\n"
                "    implementation 'com.google.android.ump:user-messaging-platform:3.2.0'\n", s, count=1)
    s = re.sub(r"minSdk\s+23\b", "minSdk 24", s)
    s = s.replace("apply plugin: 'com.google.gms.google-services'",
                  "// Firebase is optional: drop app/google-services.json in to enable analytics.\n"
                  "if (file('google-services.json').exists()) { apply plugin: 'com.google.gms.google-services' }")
    return s, "ok"


def migrate_manifest(s: str):
    blk = re.compile(r"\s*<!-- AppLovin MAX SDK key[^>]*-->\s*<meta-data\s+android:name=\"applovin\.sdk\.key\"\s+"
                     r"android:value=\"[^\"]*\"\s*/>")
    if not blk.search(s):
        return None, "template mismatch: applovin.sdk.key"
    s = blk.sub("", s, count=1)
    s = s.replace("<!-- AdMob App ID — kept for AppLovin MAX mediation adapter -->",
                  "<!-- AdMob App ID — Google TEST ID until scripts/set_app_ids.py sets the real one -->")
    s = re.sub(r'(android:name="com\.google\.android\.gms\.ads\.APPLICATION_ID"\s+android:value=")[^"]*(")',
               r"\g<1>%s\g<2>" % TEST_APP_ID, s)
    return s, "ok"


def migrate_app(app: str, dry: bool):
    a = BASE / app / "android"
    jfiles = list((a / "app/src/main/java").rglob("MainActivity.java"))
    if not jfiles:
        return "no MainActivity"
    j = jfiles[0]
    files = {
        j: migrate_java,
        a / "app/build.gradle": migrate_gradle,
        a / "app/src/main/AndroidManifest.xml": migrate_manifest,
    }
    out = {}
    for p, fn in files.items():
        res, why = fn(p.read_text(encoding="utf-8"))
        if res is None:
            return why
        out[p] = res
    sg = a / "settings.gradle"
    if sg.exists():
        out[sg] = re.sub(r"\n\s*maven \{ url 'https://artifacts\.applovin\.com/android' \}", "",
                         sg.read_text(encoding="utf-8"))
    pg = a / "app/proguard-rules.pro"
    if pg.exists():
        out[pg] = re.sub(r"# AppLovin MAX[^\n]*\n-dontwarn com\.amazon\.privacypass\.\*\*\n-dontwarn com\.amazon\.\*\*\n",
                         "# Optional-dependency stubs\n", pg.read_text(encoding="utf-8"))
    gh = BASE / app / "android/app/src/main/assets/game.html"
    if gh.exists():
        out[gh] = gh.read_text(encoding="utf-8").replace("// ── AppLovin MAX / IAP bridge ──", "// ── Ads / IAP bridge ──")
    if not dry:
        for p, s in out.items():
            p.write_text(s, encoding="utf-8")
    return "ok"


def main() -> int:
    dry = "--dry-run" in sys.argv
    apps = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir() if d.is_dir() and d.name not in SKIP
                      and not d.name.startswith(".") and (d / "android").is_dir())
    done, failed = 0, []
    for app in apps:
        jf = list((BASE / app / "android/app/src/main/java").rglob("MainActivity.java"))
        if not jf or "com.applovin" not in jf[0].read_text(encoding="utf-8", errors="replace"):
            continue
        r = migrate_app(app, dry)
        if r == "ok":
            done += 1
            print(f"  {'would migrate' if dry else 'migrated'} {app}")
        else:
            failed.append((app, r))
    for app, why in failed:
        print(f"  ! {app}: {why} — left untouched")
    print(f"AppLovin -> AdMob: {done} app(s){' (dry run)' if dry else ''}, {len(failed)} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
