#!/usr/bin/env python3
"""check_families_compliance.py — Google Play Families gate for kids-track apps.

A kids-track app is one listed under "kids" in docs/portfolio_tracks.json OR
whose metadata/app_info.json has "kids_program": true (the kids flag; see
docs/KIDS_SHELL.md). Apps outside the kids track are skipped.

BLOCKS (any one can get a Families app rejected or the account flagged):
  manifest   POST_NOTIFICATIONS / RECEIVE_BOOT_COMPLETED / exact-alarm
             permissions, any <receiver>, Play Games APP_ID meta-data, the
             AD_ID permission not stripped (tools:node="remove"), location /
             camera / microphone / contacts / accounts permissions, <queries>
             packages that are not Pegasus KIDS apps
  gradle     Play Games, Firebase / google-services, ad-mediation adapters
             (com.google.ads.mediation, AppLovin, Meta, Unity, ironSource,
             Mintegral, Pangle, InMobi, Vungle, Chartboost)
  java       notifications (NotificationManager/Compat/Channel, AlarmManager),
             Play Games / Firebase APIs, interstitial / rewarded / app-open
             ads, share intents (ACTION_SEND / createChooser); missing
             child-directed RequestConfiguration (TFCD + TFUA + MAX rating G)
             set BEFORE MobileAds.initialize; cross-promo packages
             (KIDS_PROMO_PACKAGES / CROSS_PROMO_PACKAGES) that are not kids apps
  game.html  growth shims (data-growth-shim / GROWTH_CFG); bridge calls to
             notification / interstitial / rewarded / share / Play Games /
             analytics methods; external links (http <a href>, window.open,
             location.href=, target=_blank, mailto:, market://); purchase /
             restore / openUrl / openPlayStore reached without the parental
             gate (must go through gatedNative(), whose body checks Gate.ok())
  metadata   privacy URL != https://pegasusgames-creator.github.io/privacy-kids.html,
             missing kids flag / target_age_band, gambling mechanics
WARNS: openUrl in Java without a URL allowlist; subscriptions in iaps.json.

Standalone:  python3 scripts/check_families_compliance.py [App ...]
             (no args = every kids-track app). Exit 1 on any blocker.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
KIDS_PRIVACY = "https://pegasusgames-creator.github.io/privacy-kids.html"
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}

BAD_PERMS = ["POST_NOTIFICATIONS", "RECEIVE_BOOT_COMPLETED", "SCHEDULE_EXACT_ALARM", "USE_EXACT_ALARM",
             "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "ACCESS_BACKGROUND_LOCATION", "CAMERA",
             "RECORD_AUDIO", "READ_CONTACTS", "GET_ACCOUNTS", "READ_PHONE_STATE"]
BAD_DEPS = [(r"play-services-games", "Play Games Services"),
            (r"firebase", "Firebase"),
            (r"com\.google\.gms\.google-services|google-services['\"]", "google-services plugin (Firebase)"),
            (r"com\.google\.ads\.mediation", "AdMob mediation adapter"),
            (r"applovin", "AppLovin"), (r"facebook|audience-network", "Meta Audience Network"),
            (r"unity3d|unity-ads|unityads", "Unity Ads"), (r"ironsource|is\.com", "ironSource"),
            (r"mintegral|mbridge", "Mintegral"), (r"pangle|bytedance", "Pangle"),
            (r"inmobi", "InMobi"), (r"vungle|liftoff", "Vungle/Liftoff"), (r"chartboost", "Chartboost")]
BAD_JAVA = [(r"\bNotificationManager\b|\bNotificationCompat\b|\bNotificationChannel\b|\bAlarmManager\b", "notifications / alarms"),
            (r"com\.google\.android\.gms\.games|\bPlayGamesSdk\b|\bPlayGames\.", "Play Games Services"),
            (r"com\.google\.firebase|\bFirebaseAnalytics\b", "Firebase"),
            (r"\bInterstitialAd\b|\bRewardedAd\b|\bRewardedInterstitialAd\b|\bAppOpenAd\b", "interstitial / rewarded / app-open ads"),
            (r"ACTION_SEND\b|createChooser\s*\(", "share intents")]
BAD_BRIDGE = re.compile(
    r"\b(?:Android|NativeBridge|NB)\s*\.\s*(showInterstitial\w*|showRewarded\w*|preloadRewarded|schedule\w+|"
    r"requestNotificationPermission|setNotificationsEnabled|cancelAllNotifications|shareText|shareImage|"
    r"submitScore|showLeaderboard|signInPlayGames|logEvent)\s*\(")
BAD_JS_CALLS = re.compile(r"\b(requestRewardedAd|safeShowInterstitial|showRewardedAd|showInterstitialAd)\s*\(")
GATED = r"purchase|launchPurchase|launchBilling|buy|buyProduct|restorePurchases|openUrl|openPlayStore|openLink|openStore"
RAW_GATED = re.compile(r"\b(?:Android|NativeBridge|NB)\s*\.\s*(%s)\s*\(" % GATED)
RAW_NATIVE = re.compile(r"\bnative\(\s*['\"](%s)['\"]" % GATED)
EXT_LINKS = [(r"<a\b[^>]*href\s*=\s*['\"]\s*(?:https?:|//)", "<a href> to an external site"),
             (r"\bwindow\.open\s*\(", "window.open()"), (r"\blocation\.(?:href\s*=|assign\s*\(|replace\s*\()", "location navigation"),
             (r"target\s*=\s*['\"]_blank", "target=_blank link"), (r"mailto:", "mailto: link"), (r"market://", "market:// link")]


def strip_js_comments(s: str) -> str:
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    s = re.sub(r"<!--[\s\S]*?-->", "", s)
    return re.sub(r"(?m)(^|[^:\\'\"])//[^\n]*", r"\1", s)


def strip_java_comments(s: str) -> str:
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    return re.sub(r"(?m)//[^\n]*", "", s)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def kids_track():
    try:
        return set(json.loads(read(BASE / "docs/portfolio_tracks.json")).get("kids", []))
    except ValueError:
        return set()


def app_info(app):
    try:
        return json.loads(read(BASE / app / "metadata/app_info.json") or "{}")
    except ValueError:
        return {}


def is_kids(app, track=None):
    track = kids_track() if track is None else track
    return app in track or app_info(app).get("kids_program") is True


def kids_packages(track):
    out = set()
    for a in track:
        m = re.search(r'applicationId\s+["\']([^"\']+)', read(BASE / a / "android/app/build.gradle"))
        if m:
            out.add(m.group(1))
    return out


def gated_body(js: str) -> str:
    m = re.search(r"function\s+gatedNative\s*\([^)]*\)\s*\{", js)
    if not m:
        return ""
    depth, i = 1, m.end()
    while i < len(js) and depth:
        depth += {"{": 1, "}": -1}.get(js[i], 0)
        i += 1
    return js[m.start():i]


def check_app(app: str):
    bad, warn = [], []
    track = kids_track()
    if not is_kids(app, track):
        return bad, warn
    android = BASE / app / "android"
    man = read(android / "app/src/main/AndroidManifest.xml")
    gradle = read(android / "app/build.gradle") + "\n" + read(android / "build.gradle")
    java = "\n".join(strip_java_comments(read(f)) for f in sorted((android / "app/src/main/java").rglob("*.java")))
    html = read(BASE / app / "android/app/src/main/assets/game.html")
    kpk = kids_packages(track)

    # ── manifest
    man_nc = re.sub(r"<!--[\s\S]*?-->", "", man)
    for perm in BAD_PERMS:
        for m in re.finditer(r"<uses-permission[^>]*android\.permission\.%s\b[^>]*>" % perm, man_nc):
            if 'tools:node="remove"' not in m.group(0):
                bad.append(f"{app}: manifest requests {perm} (Families: no notifications / personal-data permissions)")
    if re.search(r"<receiver\b", man_nc):
        bad.append(f"{app}: manifest declares a <receiver> (kids apps carry no notification/boot receivers)")
    if "com.google.android.gms.games.APP_ID" in man_nc:
        bad.append(f"{app}: manifest has the Play Games APP_ID meta-data (no Play Games in kids apps)")
    if not re.search(r'com\.google\.android\.gms\.permission\.AD_ID"[^>]*tools:node="remove"', man_nc):
        bad.append(f'{app}: AD_ID permission not stripped — add <uses-permission android:name="com.google.android.gms.permission.AD_ID" tools:node="remove"/>')
    for pk in re.findall(r'<package\s+android:name="([^"]+)"', man_nc):
        if pk not in kpk:
            bad.append(f"{app}: manifest <queries> lists {pk}, which is not a Pegasus KIDS app (Families: no cross-promo to general-audience apps)")

    # ── gradle
    g_nc = strip_java_comments(gradle)
    for rx, label in BAD_DEPS:
        for line in g_nc.splitlines():
            if re.search(rx, line, re.I) and re.search(r"implementation|classpath|apply plugin|id\s*['\"]|api\s", line):
                bad.append(f"{app}: build.gradle pulls in {label} ({line.strip()[:90]})")
                break

    # ── java
    if java:
        for rx, label in BAD_JAVA:
            if re.search(rx, java):
                bad.append(f"{app}: MainActivity uses {label} (not allowed in a Families app)")
        if "MobileAds" in java:
            need = ["TAG_FOR_CHILD_DIRECTED_TREATMENT_TRUE", "TAG_FOR_UNDER_AGE_OF_CONSENT_TRUE", "MAX_AD_CONTENT_RATING_G"]
            miss = [n for n in need if n not in java]
            if miss:
                bad.append(f"{app}: AdMob RequestConfiguration missing {', '.join(miss)} (child-directed ads)")
            rc, init = java.find("setRequestConfiguration"), java.find("MobileAds.initialize")
            if rc < 0 or (init >= 0 and rc > init):
                bad.append(f"{app}: MobileAds.setRequestConfiguration must run BEFORE MobileAds.initialize")
        for setname in ("KIDS_PROMO_PACKAGES", "CROSS_PROMO_PACKAGES"):
            m = re.search(setname + r"\s*=\s*([^;]+);", java)
            if m:
                for pk in re.findall(r'"([a-z][\w.]+)"', m.group(1)):
                    if pk not in kpk:
                        bad.append(f"{app}: {setname} lists {pk}, which is not a Pegasus KIDS app")
        if re.search(r"\bvoid\s+openUrl\s*\(", java) and not re.search(r"urlAllowed|ALLOWLIST|URL_ALLOW", java):
            warn.append(f"{app}: Java openUrl() has no URL allowlist")
    else:
        bad.append(f"{app}: no Java sources found")

    # ── game.html
    if not html:
        bad.append(f"{app}: game.html missing")
    else:
        js = strip_js_comments(html)
        if "data-growth-shim" in html or "GROWTH_CFG" in html:
            bad.append(f"{app}: game.html carries the game growth shims (notifications, PGS, sharing, rewarded) — kids shell only")
        for m in sorted(set(BAD_BRIDGE.findall(js))):
            bad.append(f"{app}: game.html calls the bridge's {m}() (notifications / full-screen ads / sharing / Play Games are off-limits)")
        for m in sorted(set(BAD_JS_CALLS.findall(js))):
            bad.append(f"{app}: game.html calls {m}() (no interstitial or rewarded ads for children)")
        for rx, label in EXT_LINKS:
            if re.search(rx, js, re.I):
                bad.append(f"{app}: game.html has an ungated external link: {label}")
        body = gated_body(js)
        rest = js.replace(body, "") if body else js
        raw = sorted(set(RAW_GATED.findall(rest)) | set(RAW_NATIVE.findall(rest)))
        for m in raw:
            bad.append(f"{app}: game.html reaches {m}() without the parental gate — route it through gatedNative()")
        if re.search(r"\bgatedNative\s*\(", rest) or raw:
            if not body:
                bad.append(f"{app}: gatedNative() is not defined")
            elif "Gate.ok()" not in body:
                bad.append(f"{app}: gatedNative() does not check Gate.ok() before calling the store / a link")
        elif "restorePurchases" in js or "purchase" in js.lower():
            warn.append(f"{app}: no gatedNative() calls found — confirm purchases are unreachable")

    # ── metadata
    info = app_info(app)
    if info.get("kids_program") is not True:
        bad.append(f'{app}: metadata/app_info.json lacks "kids_program": true (the kids flag — docs/KIDS_SHELL.md)')
    if not re.fullmatch(r"\d{1,2}-\d{1,2}", str(info.get("target_age_band", ""))):
        bad.append(f'{app}: metadata/app_info.json lacks "target_age_band" (e.g. "3-8")')
    try:
        priv = json.loads(read(BASE / app / "metadata/privacy.json") or "{}")
    except ValueError:
        priv = {}
    if priv.get("privacy_policy_url") != KIDS_PRIVACY:
        bad.append(f"{app}: privacy_policy_url must be {KIDS_PRIVACY} (got {priv.get('privacy_policy_url')!r})")
    try:
        cr = json.loads(read(BASE / app / "metadata/content_rating.json") or "{}")
    except ValueError:
        cr = {}
    gm = (cr.get("iarc_answers") or {}).get("gambling_mechanics", "none")
    if gm not in ("none", False, None):
        bad.append(f"{app}: content_rating.json declares gambling mechanics ({gm}) — never in a kids app")
    try:
        iaps = json.loads(read(BASE / app / "metadata/iaps.json") or "{}")
    except ValueError:
        iaps = {}
    if iaps.get("subscriptions"):
        warn.append(f"{app}: kids app sells subscriptions — keep the kids catalog to one-time unlocks")
    return bad, warn


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    track = kids_track()
    if not apps:
        apps = sorted(a for a in track if (BASE / a).is_dir())
    checked, bad_all, warn_all = 0, [], []
    for a in apps:
        if a in SKIP or not (BASE / a).is_dir() or not is_kids(a, track):
            continue
        checked += 1
        b, w = check_app(a)
        bad_all += b
        warn_all += w
    for line in bad_all:
        print("  ✗", line)
    for line in warn_all:
        print("  ⚠", line)
    if bad_all:
        print(f"families compliance: {len(bad_all)} blocker(s)")
        return 1
    print(f"families compliance: OK ({checked} kids app{'s' if checked != 1 else ''})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
