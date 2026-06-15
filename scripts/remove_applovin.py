#!/usr/bin/env python3
"""remove_applovin.py — Part 1 of the AppLovin->AdMob migration.

Drops AppLovin MAX completely from every app that ships a real AdMob bridge
and collapses the dual-SDK wrapper down to AdMob-only. The apps already run
AdMob at runtime (USE_APPLOVIN evaluated false), so this removes dead code and
the now-unused dependency; it does NOT change ad behaviour.

Per-app values (package, AdMob unit IDs, AdMob App ID, IAP IDs, theme colours)
are never touched. AdMob classes were resolving transitively through the
AppLovin google-adapter, so we add a DIRECT play-services-ads dependency in its
place or the AdMob code would no longer compile.

Touches, per app:
  * android/app/build.gradle   — swap the 2 AppLovin deps for play-services-ads
  * .../MainActivity.java       — strip AppLovin imports, MAX_* constants,
                                  USE_APPLOVIN, Max* fields, the 4 AppLovin
                                  methods, and collapse every USE_APPLOVIN branch
                                  to its AdMob (else) arm
  * .../AndroidManifest.xml     — drop the stale "AppLovin disabled" comment

game.html carries no AppLovin-specific bridge calls, so it is left untouched.

Usage:  python3 scripts/remove_applovin.py [--dry-run] [App ...]
        (no app args  -> all 8 AdMob apps, live ones last)
"""
import os
import re
import sys
import difflib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

# Live apps LAST (build/commit order); the transform itself is identical.
APPS = [
    "Afterimage", "Hunch", "Overlay", "PipeConnect",   # not yet live
    "Nonogram", "Puzzle2048", "UnblockPuzzle", "WaterSortPuzzle",  # live
]

# Latest stable Google Mobile Ads SDK (2026-05-21). AdMob used to arrive
# transitively via com.applovin.mediation:google-adapter; pin it directly now.
PLAY_ADS_LINE = "    implementation 'com.google.android.gms:play-services-ads:25.3.0'"

AD_METHOD_STARTS = (
    "private void initAppLovin()",
    "private class BannerListener implements MaxAdViewAdListener",
    "private void loadInterstitialAd()",
    "private void loadRewardedAd()",
)


def find_mainactivity(app):
    base = os.path.join(ROOT, app, "android", "app", "src", "main", "java")
    for dp, _, fs in os.walk(base):
        if "MainActivity.java" in fs:
            return os.path.join(dp, "MainActivity.java")
    return None


def dedent4(line):
    return line[4:] if line[:4] == "    " else line.lstrip(" ")


def transform_java(text):
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()

        # --- drop AppLovin imports ---
        if s.startswith("import com.applovin."):
            i += 1
            continue

        # --- drop MAX_* constants and the USE_APPLOVIN flag ---
        if re.search(r"private static final String MAX_(SDK_KEY|BANNER_UNIT_ID|"
                     r"INTERSTITIAL_UNIT_ID|REWARDED_UNIT_ID)\b", line):
            i += 1
            continue
        if "private static final boolean USE_APPLOVIN" in line:
            # The whole AppLovin constants block sits directly above this line as
            # a contiguous comment run (the MAX_* decls between were already
            # dropped). Pop it back to the preceding blank line so no orphaned
            # comment fragments survive.
            while out and out[-1].strip().startswith("//"):
                out.pop()
            i += 1
            continue

        # --- drop the Max* field declarations ---
        if re.match(r"private Max(AdView|InterstitialAd|RewardedAd)\b", s):
            i += 1
            continue

        # --- drop AppLovin-only comments (headers, "paste SDK key", etc.) ---
        if s.startswith("//") and (re.search(r"applovin", s, re.I) or "MAX_" in s):
            i += 1
            continue
        # section-divider comment immediately above the AppLovin method block
        if s.startswith("//") and "AppLovin MAX" in s:
            i += 1
            continue

        # --- remove the 4 AppLovin methods (brace-matched) ---
        if any(s.startswith(p) for p in AD_METHOD_STARTS):
            brace = line.count("{") - line.count("}")
            i += 1
            while i < n and brace > 0:
                brace += lines[i].count("{") - lines[i].count("}")
                i += 1
            # swallow one trailing blank so removed methods don't stack blanks
            if i < n and lines[i].strip() == "":
                i += 1
            continue

        # --- collapse the init one-liner ---
        if "if (USE_APPLOVIN) initAppLovin();" in line:
            indent = line[:len(line) - len(line.lstrip(" "))]
            out.append(indent + "initAdMob();")
            i += 1
            continue

        # --- collapse the block branches: keep only the else (AdMob) arm ---
        if s == "if (USE_APPLOVIN) {":
            prev_brace = line.count("{") - line.count("}")  # == 1
            j = i + 1
            else_idx = None
            end_idx = None
            while j < n:
                lj = lines[j]
                if lj.strip() == "} else {" and prev_brace == 1 and else_idx is None:
                    else_idx = j
                prev_brace += lj.count("{") - lj.count("}")
                if prev_brace == 0:
                    end_idx = j
                    break
                j += 1
            if else_idx is None or end_idx is None:
                raise RuntimeError("Unbalanced USE_APPLOVIN block near line %d" % i)
            for k in range(else_idx + 1, end_idx):
                out.append(dedent4(lines[k]))
            i = end_idx + 1
            continue

        out.append(line)
        i += 1

    # collapse any run of 2+ blank lines (left by removed blocks) down to one
    collapsed = []
    blanks = 0
    for ln in out:
        if ln.strip() == "":
            blanks += 1
            if blanks >= 2:
                continue
        else:
            blanks = 0
        collapsed.append(ln)
    return "\n".join(collapsed)


def transform_gradle(text):
    lines = text.split("\n")
    out = []
    for line in lines:
        if re.search(r"implementation\s+['\"]com\.applovin:applovin-sdk", line):
            out.append(PLAY_ADS_LINE)               # replace SDK line in place
            continue
        if re.search(r"implementation\s+['\"]com\.applovin\.mediation:google-adapter", line):
            continue                                # drop the adapter line
        out.append(line)
    return "\n".join(out)


def transform_manifest(text):
    """Drop the stale '<!-- AppLovin disabled ... -->' comment block."""
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if "<!--" in line and "-->" not in line:
            # gather the whole comment block
            block = [line]
            j = i + 1
            while j < n and "-->" not in lines[j]:
                block.append(lines[j])
                j += 1
            if j < n:
                block.append(lines[j])
            blob = "\n".join(block)
            if re.search(r"applovin", blob, re.I) or "MAX_ENABLED" in blob:
                i = j + 1
                continue
            out.extend(block)
            i = j + 1
            continue
        # single-line comment containing applovin
        if "<!--" in line and "-->" in line and (
                re.search(r"applovin", line, re.I) or "MAX_ENABLED" in line):
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def verify_java(text, app):
    problems = []
    for tok in ("applovin", "AppLovin", "USE_APPLOVIN", "MaxAd", "MAX_SDK_KEY",
                "MAX_BANNER", "MAX_INTERSTITIAL", "MAX_REWARDED",
                "initAppLovin", "BannerListener"):
        if tok in text:
            problems.append("residual token: %s" % tok)
    if text.count("{") != text.count("}"):
        problems.append("brace mismatch: %d { vs %d }"
                        % (text.count("{"), text.count("}")))
    # AdMob path must survive
    for need in ("initAdMob", "admobBanner", "loadAdmobInterstitial", "loadAdmobRewarded"):
        if need not in text:
            problems.append("MISSING AdMob symbol: %s" % need)
    return problems


def process(app, dry):
    changed = []
    # ---- gradle ----
    g = os.path.join(ROOT, app, "android", "app", "build.gradle")
    gt = open(g, encoding="utf-8").read()
    gt2 = transform_gradle(gt)
    if gt2 != gt:
        changed.append((g, gt, gt2))
    # ---- java ----
    j = find_mainactivity(app)
    jt = open(j, encoding="utf-8").read()
    jt2 = transform_java(jt)
    probs = verify_java(jt2, app)
    if probs:
        print("  !! %s verification FAILED:" % app)
        for p in probs:
            print("       - %s" % p)
        return False
    if jt2 != jt:
        changed.append((j, jt, jt2))
    # ---- manifest ----
    m = os.path.join(ROOT, app, "android", "app", "src", "main", "AndroidManifest.xml")
    mt = open(m, encoding="utf-8").read()
    mt2 = transform_manifest(mt)
    if mt2 != mt:
        changed.append((m, mt, mt2))

    for path, before, after in changed:
        rel = os.path.relpath(path, ROOT)
        if dry:
            diff = difflib.unified_diff(
                before.split("\n"), after.split("\n"),
                fromfile="a/" + rel, tofile="b/" + rel, lineterm="")
            print("\n".join(diff))
        else:
            open(path, "w", encoding="utf-8").write(after)
    if not dry:
        print("  %s: updated %d file(s)" % (app, len(changed)))
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
