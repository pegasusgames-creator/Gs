#!/usr/bin/env python3
"""
fix_all_apps.py
Applies all Android fixes and creates iOS scaffolding for every app.

Android fixes:
  1. billing 6.2.0 → 8.0.0
  2. enablePendingPurchases() → PendingPurchasesParams API (billing 8 requirement)
  3. ProGuard: ballsort.MainActivity$AndroidBridge → correct package + NativeBridge
  4. Remove android:screenOrientation="portrait" from manifest
  5. Move inline fullscreen block out of onCreate → applyFullscreen() + onWindowFocusChanged
  6. Create res/xml/gma_ad_services_config.xml if missing

iOS scaffolding:
  - Copy _template/ios/ into each app's ios/ directory
  - Substitute ENTER_APP_NAME and ENTER_APP_ID with real values
  - Substitute Podfile target name
"""

import os
import re
import shutil

BASE = "/home/pgs/Documents/Gs"
TEMPLATE_IOS = os.path.join(BASE, "_template", "ios")

GMA_CONFIG = """\
<?xml version="1.0" encoding="utf-8"?>
<ad-services-config>
    <attribution-reporting allowAllToActivate="true" />
    <custom-audiences allowAllToActivate="true" />
    <topics allowAllToActivate="true" />
    <protected-signals allowAllToActivate="true" />
    <ad-selection-service allowAllToActivate="true" />
</ad-services-config>
"""

# The inline fullscreen block present in every app's onCreate
FULLSCREEN_BLOCK_PATTERN = re.compile(
    r"        // Fullscreen immersive\n"
    r"        if \(android\.os\.Build\.VERSION\.SDK_INT >= android\.os\.Build\.VERSION_CODES\.R\) \{\n"
    r"            getWindow\(\)\.setDecorFitsSystemWindows\(false\);\n"
    r"            android\.view\.WindowInsetsController ic = getWindow\(\)\.getInsetsController\(\);\n"
    r"            if \(ic != null\) \{\n"
    r"                ic\.hide\(android\.view\.WindowInsets\.Type\.statusBars\(\) \|\n"
    r"                        android\.view\.WindowInsets\.Type\.navigationBars\(\)\);\n"
    r"                ic\.setSystemBarsBehavior\(\n"
    r"                    android\.view\.WindowInsetsController\.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE\);\n"
    r"            \}\n"
    r"        \} else \{\n"
    r"            //noinspection deprecation\n"
    r"            getWindow\(\)\.getDecorView\(\)\.setSystemUiVisibility\(\n"
    r"                android\.view\.View\.SYSTEM_UI_FLAG_FULLSCREEN \|\n"
    r"                android\.view\.View\.SYSTEM_UI_FLAG_HIDE_NAVIGATION \|\n"
    r"                android\.view\.View\.SYSTEM_UI_FLAG_IMMERSIVE_STICKY\);\n"
    r"        \}\n"
)

APPLYFS_METHOD = """\
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

"""

ON_RESUME_PATTERN = re.compile(r"    @Override protected void onResume\(\)")


def fix_main_activity(path, pkg):
    with open(path, "r") as f:
        src = f.read()

    original = src

    # 1. Fix enablePendingPurchases()
    src = src.replace(
        ".enablePendingPurchases().build();",
        ".enablePendingPurchases(\n"
        "                PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()\n"
        "            ).build();"
    )

    # 2. Remove inline fullscreen block from onCreate
    src = FULLSCREEN_BLOCK_PATTERN.sub("", src)

    # 3. Inject applyFullscreen() + onWindowFocusChanged before onResume (if not already present)
    if "applyFullscreen()" not in src:
        src = ON_RESUME_PATTERN.sub(
            APPLYFS_METHOD + "    @Override protected void onResume()",
            src
        )

    if src != original:
        with open(path, "w") as f:
            f.write(src)
        return True
    return False


def fix_build_gradle(path):
    with open(path, "r") as f:
        src = f.read()
    original = src
    src = re.sub(
        r"implementation 'com\.android\.billingclient:billing:[^']*'",
        "implementation 'com.android.billingclient:billing:8.0.0'",
        src
    )
    if src != original:
        with open(path, "w") as f:
            f.write(src)
        return True
    return False


def fix_proguard(path, pkg):
    with open(path, "r") as f:
        src = f.read()
    original = src
    # Replace any hardcoded wrong class (ballsort.MainActivity$AndroidBridge or any $AndroidBridge)
    src = re.sub(
        r"-keepclassmembers class [^\s]+ \{",
        f"-keepclassmembers class {pkg}.MainActivity$NativeBridge {{",
        src,
        count=1
    )
    if src != original:
        with open(path, "w") as f:
            f.write(src)
        return True
    return False


def fix_manifest(path):
    with open(path, "r") as f:
        src = f.read()
    original = src
    # Remove screenOrientation="portrait" line
    src = re.sub(r'\s*android:screenOrientation="portrait"\n?', "\n", src)
    if src != original:
        with open(path, "w") as f:
            f.write(src)
        return True
    return False


def ensure_gma_config(app_dir):
    xml_dir = os.path.join(app_dir, "android", "app", "src", "main", "res", "xml")
    xml_file = os.path.join(xml_dir, "gma_ad_services_config.xml")
    if not os.path.exists(xml_file):
        os.makedirs(xml_dir, exist_ok=True)
        with open(xml_file, "w") as f:
            f.write(GMA_CONFIG)
        return True
    return False


def scaffold_ios(app_dir, app_name, pkg_suffix, display_name):
    ios_dir = os.path.join(app_dir, "ios")
    if os.path.exists(ios_dir):
        return False  # already done

    os.makedirs(ios_dir, exist_ok=True)

    for fname in ["AppDelegate.swift", "ViewController.swift", "Info.plist", "Podfile", "IOS_SETUP.md"]:
        src_path = os.path.join(TEMPLATE_IOS, fname)
        dst_path = os.path.join(ios_dir, fname)
        with open(src_path, "r") as f:
            content = f.read()

        content = content.replace("ENTER_APP_NAME", display_name)
        content = content.replace("ENTER_APP_ID", pkg_suffix)
        content = content.replace("target 'GameApp'", f"target '{app_name}'")

        with open(dst_path, "w") as f:
            f.write(content)

    return True


def get_display_name(manifest_path):
    with open(manifest_path, "r") as f:
        src = f.read()
    m = re.search(r'android:label="([^"]+)"', src)
    return m.group(1) if m else None


def get_package(build_gradle_path):
    with open(build_gradle_path, "r") as f:
        src = f.read()
    m = re.search(r'applicationId\s+"([^"]+)"', src)
    return m.group(1) if m else None


# -------------------------------------------------------
# Main
# -------------------------------------------------------
results = {"billing": [], "mainactivity": [], "proguard": [], "manifest": [], "gma": [], "ios": [], "skipped": []}

for entry in sorted(os.listdir(BASE)):
    app_dir = os.path.join(BASE, entry)
    if not os.path.isdir(app_dir) or entry.startswith("_") or entry == "APP_IDEAS.txt":
        continue

    android_dir = os.path.join(app_dir, "android")
    if not os.path.isdir(android_dir):
        results["skipped"].append(entry)
        continue

    build_gradle = os.path.join(android_dir, "app", "build.gradle")
    manifest = os.path.join(android_dir, "app", "src", "main", "AndroidManifest.xml")

    if not os.path.exists(build_gradle):
        results["skipped"].append(entry)
        continue

    pkg = get_package(build_gradle)
    if not pkg:
        results["skipped"].append(f"{entry} (no pkg)")
        continue

    pkg_suffix = pkg.split(".")[-1]  # e.g. "tipcalculator"
    display_name = get_display_name(manifest) if os.path.exists(manifest) else entry

    # Find MainActivity.java
    java_src_dir = os.path.join(android_dir, "app", "src", "main", "java")
    main_activity = None
    for root, dirs, files in os.walk(java_src_dir):
        for f in files:
            if f == "MainActivity.java":
                main_activity = os.path.join(root, f)
                break

    proguard = os.path.join(android_dir, "app", "proguard-rules.pro")

    # Apply fixes
    if fix_build_gradle(build_gradle):
        results["billing"].append(entry)

    if main_activity and os.path.exists(main_activity):
        if fix_main_activity(main_activity, pkg):
            results["mainactivity"].append(entry)

    if os.path.exists(proguard):
        if fix_proguard(proguard, pkg):
            results["proguard"].append(entry)

    if os.path.exists(manifest):
        if fix_manifest(manifest):
            results["manifest"].append(entry)

    if ensure_gma_config(app_dir):
        results["gma"].append(entry)

    if scaffold_ios(app_dir, entry, pkg_suffix, display_name):
        results["ios"].append(entry)

# Summary
print("=" * 60)
print("FIX SUMMARY")
print("=" * 60)
print(f"Billing 8.0.0:          {len(results['billing'])} apps")
print(f"MainActivity fullscreen: {len(results['mainactivity'])} apps")
print(f"ProGuard NativeBridge:  {len(results['proguard'])} apps")
print(f"Manifest orientation:   {len(results['manifest'])} apps")
print(f"GMA config created:     {len(results['gma'])} apps")
print(f"iOS scaffolded:         {len(results['ios'])} apps")
print(f"Skipped (no android/):  {len(results['skipped'])} — {results['skipped']}")
print()
print("All done.")
