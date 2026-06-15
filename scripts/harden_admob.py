#!/usr/bin/env python3
"""harden_admob.py — Part 2 of the AppLovin->AdMob migration.

Stops wasted ad requests and fixes the rewarded show-rate on the 8 AdMob apps.
The AdMob load/show methods are byte-identical across all 8 (verified), so the
core changes are exact-string replacements in MainActivity.java; VALID_REWARD_TYPES
is widened per app from the strings that app's game.html actually sends.

What changes (per app):
  1. Reward routing: showRewardedAd normalises extra_life -> life (routes to the
     existing life branch) and VALID_REWARD_TYPES is widened to every reward
     string the game sends, so the ad is no longer dropped before it shows.
     The single overwrite-able pendingRewardType becomes a FIFO queue so two
     back-to-back rewarded triggers never drop the first reward.
  2. Backoff + single-inflight: interstitial AND rewarded retry on
     onAdFailedToLoad with exponential backoff (8s/16s/32s/64s cap) instead of
     hammering; never load when one is already loading or loaded.
  3. Lazy rewarded: not loaded at native init (truly lazy — no request until a
     rewarded is actually triggered). show() loads on demand and keeps the
     onAdNotReady fallback; reload-on-dismiss is native; the bridge exposes
     preloadRewarded() so a future game.html change can warm one on screen-open.
     (No game.html is touched here — those files carry unrelated in-flight edits;
     keeping Part 2 to MainActivity.java keeps the commit clean.)
  4. Freshness: before show(), an ad older than 50 min is discarded and reloaded.
  5. Banner: pause()/resume() already wired; no JS reload loop exists. Untouched.
  6. Interstitial cadence: a >=60s floor is enforced in showInterstitialAd so it
     holds for every app regardless of the per-game JS counter (which already
     counts by levels and skips the first clears via the growth shim).

Ad unit IDs, AdMob App ID, package names, signing and the game economy are
untouched.

Usage:  python3 scripts/harden_admob.py [--dry-run] [App ...]
"""
import os
import re
import sys
import difflib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

APPS = [
    "Afterimage", "Hunch", "Overlay", "PipeConnect",
    "Nonogram", "Puzzle2048", "UnblockPuzzle", "WaterSortPuzzle",
]

# ── exact current (post-Part-1) method texts -> hardened replacements ──────────

OLD_FIELD = re.compile(r"^[ \t]*private String\s+pendingRewardType;[ \t]*$", re.M)
NEW_FIELD = """\
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
    private static final long INTERSTITIAL_MIN_GAP_MS = 60L * 1000L;  // >=60s between interstitials"""

OLD_INTER = """\
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
    }"""
NEW_INTER = """\
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
    }"""

OLD_REWARDED = """\
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
    }"""
NEW_REWARDED = """\
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
    }"""

OLD_SHOW_INTER = """\
    private void showInterstitialAd() {
        runOnUiThread(() -> {
            if (admobInterstitial != null) admobInterstitial.show(this);
        });
    }"""
NEW_SHOW_INTER = """\
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
    }"""

OLD_SHOW_REW = """\
    private void showRewardedAd(String rewardType) {
        if (!VALID_REWARD_TYPES.contains(rewardType)) return;
        pendingRewardType = rewardType;
        runOnUiThread(() -> {
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
        });
    }"""
NEW_SHOW_REW = """\
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
    }"""

OLD_INIT_LOADS = "            loadAdmobBanner(); loadAdmobInterstitial(); loadAdmobRewarded();"
NEW_INIT_LOADS = "            loadAdmobBanner(); loadAdmobInterstitial(); // rewarded is lazy-loaded (preloadRewarded)"

OLD_BRIDGE = "        @JavascriptInterface public void showRewarded(String type)       { showRewardedAd(type); }"
NEW_BRIDGE = (OLD_BRIDGE + "\n" +
              "        @JavascriptInterface public void preloadRewarded()              { runOnUiThread(() -> loadAdmobRewarded()); }")

REPLACEMENTS = [
    ("loadAdmobInterstitial", OLD_INTER, NEW_INTER),
    ("loadAdmobRewarded", OLD_REWARDED, NEW_REWARDED),
    ("showInterstitialAd", OLD_SHOW_INTER, NEW_SHOW_INTER),
    ("showRewardedAd", OLD_SHOW_REW, NEW_SHOW_REW),
    ("initAdMob load line", OLD_INIT_LOADS, NEW_INIT_LOADS),
    ("preloadRewarded bridge", OLD_BRIDGE, NEW_BRIDGE),
]


def find_mainactivity(app):
    base = os.path.join(ROOT, app, "android", "app", "src", "main", "java")
    for dp, _, fs in os.walk(base):
        if "MainActivity.java" in fs:
            return os.path.join(dp, "MainActivity.java")
    return None


def reward_strings(app):
    """Reward strings the app's game.html actually sends, normalised."""
    h = os.path.join(ROOT, app, "android", "app", "src", "main", "assets", "game.html")
    txt = open(h, encoding="utf-8").read()
    found = set(re.findall(r"showRewarded\(['\"]([a-z_]+)['\"]", txt))
    return {"life" if s == "extra_life" else s for s in found}


def widen_valid(text, app):
    m = re.search(r"VALID_REWARD_TYPES = new HashSet<>\(Arrays\.asList\((.*?)\)\)",
                  text, re.S)
    if not m:
        return text, []
    inner = m.group(1)
    existing = set(re.findall(r'"([^"]+)"', inner))
    missing = [s for s in sorted(reward_strings(app)) if s not in existing]
    if not missing:
        return text, []
    add = "".join(', "%s"' % s for s in missing)
    idx = inner.rfind('"')
    new_inner = inner[:idx + 1] + add + inner[idx + 1:]
    return text[:m.start(1)] + new_inner + text[m.end(1):], missing


def transform_java(text, app):
    notes = []
    # FIFO field + ad-state
    new = OLD_FIELD.sub(NEW_FIELD.replace("\\", "\\\\"), text, count=1)
    if new == text and not OLD_FIELD.search(text):
        raise RuntimeError("%s: pendingRewardType field not found" % app)
    text = new
    # method/line/bridge replacements
    for label, old, repl in REPLACEMENTS:
        if old not in text:
            raise RuntimeError("%s: anchor not found for %s" % (app, label))
        if text.count(old) != 1:
            raise RuntimeError("%s: anchor not unique for %s" % (app, label))
        text = text.replace(old, repl, 1)
    # widen reward allowlist
    text, missing = widen_valid(text, app)
    if missing:
        notes.append("VALID_REWARD_TYPES += %s" % ", ".join(missing))
    return text, notes


def verify_java(text, app):
    problems = []
    if "pendingRewardType " in text or "pendingRewardType;" in text or \
            re.search(r"\bpendingRewardType\b", text):
        problems.append("residual pendingRewardType (should be pendingRewardTypes queue)")
    if text.count("{") != text.count("}"):
        problems.append("brace mismatch")
    for need in ("pendingRewardTypes", "backoffMs(", "preloadRewarded",
                 "INTERSTITIAL_MIN_GAP_MS", "AD_FRESH_MS", 'extra_life'):
        if need not in text:
            problems.append("missing: %s" % need)
    return problems



def process(app, dry):
    changed = []
    j = find_mainactivity(app)
    jt = open(j, encoding="utf-8").read()
    jt2, notes = transform_java(jt, app)
    probs = verify_java(jt2, app)
    if probs:
        print("  !! %s verification FAILED: %s" % (app, "; ".join(probs)))
        return False
    if jt2 != jt:
        changed.append((j, jt, jt2))

    for path, before, after in changed:
        rel = os.path.relpath(path, ROOT)
        if dry:
            diff = difflib.unified_diff(before.split("\n"), after.split("\n"),
                                        fromfile="a/" + rel, tofile="b/" + rel, lineterm="")
            print("\n".join(diff))
        else:
            open(path, "w", encoding="utf-8").write(after)
    if not dry:
        print("  %s: %d file(s)%s" % (app, len(changed),
              ("  [" + "; ".join(notes) + "]") if notes else ""))
    return True


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    apps = [a for a in args if not a.startswith("--")] or APPS
    ok = True
    for app in apps:
        print("==== %s ====" % app)
        ok = process(app, dry) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
