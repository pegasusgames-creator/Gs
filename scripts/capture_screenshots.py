#!/usr/bin/env python3
"""
capture_screenshots.py — capture raw screenshots from the running Android emulator.

Boots the user's Android emulator if not already running, installs the
app's latest debug APK, navigates to each of 7 in-app states by sending
tap events via adb, and saves screenshots to:

    <AppName>/store/screenshots/phone/raw/01.png ... 07.png

Each screenshot is the actual app rendered by Android WebView with real
font rendering, real localStorage state from previous use, real status
bar etc. — produces "looks like a real phone" output, not headless
desktop Chromium approximations.

Usage:
    python3 capture_screenshots.py <AppName>
    python3 capture_screenshots.py <AppName> --slot 03    # one slot only
    python3 capture_screenshots.py <AppName> --no-launch  # use already-running emulator
    python3 capture_screenshots.py <AppName> --avd <name> # specify which AVD

How it works:
1. If no emulator is running, launch the user's first available AVD
2. Wait for boot complete
3. Install <App>/android/app/build/outputs/apk/debug/app-debug.apk
   (build it first with `./gradlew assembleDebug` in the app's android/ dir)
4. For each of 7 slots:
   - Force-stop and re-launch the app (clean state)
   - Wait for menu to render
   - Send tap sequence to navigate to the target state (Play, Daily, Stats…)
   - Wait for animations to settle
   - Capture via `adb shell screencap`
   - Pull the PNG to local raw/NN.png

Tap coordinates are computed from the app's known menu layout. If the
app has a custom layout (different button positions), edit DEFAULT_TAPS
at the top, or create a per-app override at <App>/test/screenshot_taps.json.

Requirements:
- adb in PATH
- emulator binary in PATH (or in $ANDROID_SDK_ROOT/emulator/)
- At least one AVD installed (`emulator -list-avds` shows it)
- The app's debug APK built (`./gradlew assembleDebug`)
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = (Path(__file__).resolve().parent.parent
             if Path(__file__).resolve().parent.name == "scripts"
             else Path(__file__).resolve().parent)


# Tap fractions for the default Pegasus Games menu layout (per
# QUALITY_PLAYBOOK §3.1: hero Play, secondary Daily, icon row of 3).
# Coordinates are FRACTIONS of screen w/h, converted to absolute coords
# at runtime once we know the device's actual size. Works across emulators
# of varying resolutions.
#
# Each slot's value is a list of operations:
#   ("tap", x_frac, y_frac, wait_ms_after)
#   ("wait", ms)
#   ("back",)  — sends BACK key
#
# For apps with non-default layouts (Layout B map, F direct-to-game,
# etc.), create <App>/test/screenshot_taps.json with the correct sequence.

DEFAULT_TAPS = {
    "01_deep_gameplay": [
        ("tap", 0.50, 0.50, 1500),  # Hero Play button → loads currentLevel
    ],
    "02_early_gameplay": [
        ("tap", 0.40, 0.72, 1500),  # Levels icon (left in icon row)
        ("tap", 0.30, 0.30, 1500),  # tap a low-numbered level (≈level 5)
    ],
    "03_level_complete": [
        # Most reliable path: Daily Challenge button.
        # The captured screen will be the daily mode opening — if app has
        # no daily, override per-app via screenshot_taps.json.
        ("tap", 0.50, 0.62, 2000),
    ],
    "04_missions_panel": [
        ("tap", 0.50, 0.72, 1500),  # center of icon row
    ],
    "05_stats": [
        ("tap", 0.72, 0.72, 1500),  # right of icon row
    ],
    "06_levels_grid": [
        ("tap", 0.40, 0.72, 1500),  # left of icon row
    ],
    "07_menu": [
        # Already on menu after force-stop + relaunch — capture as-is
    ],
}


def run(cmd, check=True, capture=True, timeout=60):
    """Run a subprocess command, return CompletedProcess or None on failure."""
    if isinstance(cmd, str):
        shell = True
        cmd_str = cmd
    else:
        shell = False
        cmd_str = " ".join(str(c) for c in cmd)
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture,
                                text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        print(f"  ✗ TIMEOUT: {cmd_str}")
        return None
    if check and result.returncode != 0:
        print(f"  ✗ FAILED: {cmd_str}")
        if result.stderr:
            print(f"    stderr: {result.stderr.strip()[:300]}")
        return None
    return result


def ensure_emulator_running(avd_name=None):
    """Boot an emulator if none is running. Wait for boot to complete."""
    result = run(["adb", "devices"], check=False)
    if result and "\tdevice" in result.stdout:
        print("  ✓ emulator already running")
        return True

    result = run(["emulator", "-list-avds"], check=False)
    if not result or result.returncode != 0:
        print("  ✗ `emulator` binary not found.")
        print("    Add $ANDROID_SDK_ROOT/emulator to PATH, or launch")
        print("    Android Studio's AVD manually then re-run with --no-launch.")
        return False

    avds = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    if not avds:
        print("  ✗ no AVDs installed. Create one in Android Studio AVD Manager.")
        return False

    chosen = avd_name if (avd_name and avd_name in avds) else avds[0]
    print(f"  Launching emulator: {chosen}")

    # Background-launch the emulator (don't wait for it to exit)
    subprocess.Popen(
        ["emulator", "-avd", chosen, "-no-snapshot-save"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print("  Waiting for emulator boot (up to 90s)...")
    run(["adb", "wait-for-device"], timeout=90, check=False)
    for _ in range(60):
        r = run(["adb", "shell", "getprop", "sys.boot_completed"], check=False)
        if r and r.stdout.strip() == "1":
            print("  ✓ emulator booted")
            time.sleep(2)  # extra settle for launcher
            return True
        time.sleep(2)
    print("  ✗ emulator boot timed out")
    return False


def get_screen_size():
    """Returns (width, height) of the connected device."""
    result = run(["adb", "shell", "wm", "size"], check=False)
    if not result or "Physical size" not in result.stdout:
        return (1080, 2400)  # safe default
    line = result.stdout.split("Physical size:")[1].split()[0]
    w, h = line.split("x")
    return (int(w), int(h))


def install_apk(app_dir):
    """Install the app's debug APK on the connected device."""
    apk = app_dir / "android/app/build/outputs/apk/debug/app-debug.apk"
    if not apk.exists():
        print(f"  ✗ debug APK not found: {apk}")
        print(f"    Build it first:")
        print(f"      cd {app_dir / 'android'} && ./gradlew assembleDebug")
        return False
    print(f"  Installing {apk.name}...")
    result = run(["adb", "install", "-r", str(apk)], timeout=120)
    return bool(result and result.returncode == 0)


def get_package_name(app_dir):
    """Read applicationId from build.gradle."""
    gradle = app_dir / "android/app/build.gradle"
    if not gradle.exists():
        return None
    for line in gradle.read_text().splitlines():
        line = line.strip()
        if line.startswith("applicationId"):
            parts = line.split('"')
            if len(parts) >= 2:
                return parts[1]
    return None


def force_stop_and_launch(package_name, readiness_expr=None):
    """Kill the app, re-launch, and wait until the WebView script is ready.

    `readiness_expr` lets a per-app override wait for late-defined helpers
    (e.g. `__nonoFillSolution`) rather than just `startLevel`. Without a
    stricter check the script can race past JS that's still being parsed.

    Also forces a Page.navigate to file:///android_asset/game.html on the
    CDP — the Android WebView's CDP often initialises with the main
    execution context pinned to about:blank, so even though the visible
    URL is game.html, Runtime.evaluate ends up in the wrong context where
    `localStorage` is a SecurityError and globals like `startLevel` are
    undefined. The explicit navigate forces CDP to bind to the real page.
    """
    run(["adb", "shell", "am", "force-stop", package_name], check=False)
    time.sleep(0.6)
    run(["adb", "shell", "am", "start", "-n",
         f"{package_name}/.MainActivity"], check=False)
    time.sleep(2.0)  # baseline so the WebView exists before we connect
    _force_cdp_navigate(package_name)
    if readiness_expr:
        _wait_for_webview_ready(package_name, timeout=12.0,
                                 readiness_expr=readiness_expr)
    else:
        _wait_for_webview_ready(package_name, timeout=12.0)


def _force_cdp_navigate(package_name):
    """Force the CDP main frame to (re)load game.html so the execution
    context is bound to the file:// origin (not about:blank)."""
    try:
        import websocket  # type: ignore
        import json as _json
        ws_url = _devtools_ws_url(package_name)
        if not ws_url:
            return
        ws = websocket.create_connection(ws_url, timeout=3,
                                          suppress_origin=True)
        ws.send(_json.dumps({"id": 1, "method": "Page.enable"}))
        ws.recv()
        ws.send(_json.dumps({"id": 2, "method": "Page.navigate",
            "params": {"url": "file:///android_asset/game.html"}}))
        ws.recv()
        ws.close()
    except Exception:
        pass


def _wait_for_webview_ready(package_name, timeout=12.0,
                             readiness_expr="typeof startLevel === 'function'"):
    """Poll the WebView until `readiness_expr` evaluates to True, or timeout.

    The default checks for `startLevel` but apps that need late-defined
    helpers should pass a stricter expression (e.g.
    "typeof __nonoFillSolution === 'function'") via per-app config so the
    poll waits until ALL the JS hooks the screenshot taps will call are
    actually attached.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            import websocket  # type: ignore
            import json as _json
            import urllib.request
            ws_url = _devtools_ws_url(package_name)
            if not ws_url:
                time.sleep(0.5)
                continue
            ws = websocket.create_connection(ws_url, timeout=2,
                                              suppress_origin=True)
            ws.send(_json.dumps({"id": 1, "method": "Runtime.evaluate",
                "params": {"expression": readiness_expr,
                           "returnByValue": True}}))
            r = _json.loads(ws.recv())
            ws.close()
            if r.get("result", {}).get("result", {}).get("value") is True:
                return True
        except Exception:
            pass
        time.sleep(0.4)
    return False


def _devtools_ws_url(package_name):
    """Forward chrome_devtools_remote over adb and return the page WS URL.

    Requires the app's MainActivity to call setWebContentsDebuggingEnabled(true)
    on the WebView (true for Pegasus Games debug builds).
    """
    import json as _json
    import urllib.request
    socket_name = f"webview_devtools_remote_{_get_app_pid(package_name)}"
    # Try several common socket names — Android exposes per-PID sockets and
    # also a generic chrome_devtools_remote on the foreground WebView.
    for sock in (socket_name, "chrome_devtools_remote", "webview_devtools_remote"):
        run(["adb", "forward", "--remove", "tcp:9229"], check=False)
        r = run(["adb", "forward", "tcp:9229", f"localabstract:{sock}"], check=False)
        if r is None or r.returncode != 0:
            continue
        try:
            req = urllib.request.Request("http://127.0.0.1:9229/json")
            with urllib.request.urlopen(req, timeout=2) as resp:
                pages = _json.loads(resp.read().decode("utf-8"))
            for p in pages:
                if p.get("type") in ("page", "webview") and p.get("webSocketDebuggerUrl"):
                    return p["webSocketDebuggerUrl"]
        except Exception:
            continue
    return None


def _get_app_pid(package_name):
    r = run(["adb", "shell", "pidof", package_name], check=False)
    if r and r.stdout.strip():
        return r.stdout.strip().split()[0]
    return ""


def evaluate_js(package_name, js, timeout=5):
    """Inject JS into the running WebView via Chrome DevTools Protocol.

    Returns True on success, False otherwise. Used by per-app screenshot
    overrides for state seeding (e.g. window.__nonoFillSolution(0.6)) so
    the screenshot reflects mid-game state rather than first-launch zeros.
    """
    try:
        import websocket  # type: ignore
    except ImportError:
        print("    (skip js: install websocket-client to enable JS injection)")
        return False
    import json as _json
    ws_url = _devtools_ws_url(package_name)
    if not ws_url:
        print("    (skip js: no WebView devtools socket — debug build?)")
        return False
    try:
        # Android WebView's DevTools rejects non-whitelisted Origins. The
        # Chromium check accepts an empty/missing Origin header (treated
        # as same-origin), so override the default localhost Origin that
        # websocket-client adds.
        # Android WebView CDP rejects every Origin EXCEPT a missing one.
        # suppress_origin=True with no Origin entry in `header=` sends no
        # Origin header at all, which the WebView treats as same-origin.
        ws = websocket.create_connection(
            ws_url, timeout=timeout,
            suppress_origin=True,
        )
        ws.send(_json.dumps({
            "id": 1, "method": "Runtime.evaluate",
            "params": {"expression": js, "awaitPromise": True,
                       "returnByValue": True},
        }))
        resp = _json.loads(ws.recv())
        ws.close()
        # Some Android WebView CDP messages arrive as bare events
        # (`method` set, no `result` / `id`) ahead of the actual reply —
        # accept and re-read in that case.
        if "result" not in resp and "method" in resp:
            try:
                ws = websocket.create_connection(
                    ws_url, timeout=timeout, suppress_origin=True)
                ws.send(_json.dumps({
                    "id": 1, "method": "Runtime.evaluate",
                    "params": {"expression": js, "awaitPromise": True,
                               "returnByValue": True},
                }))
                resp = _json.loads(ws.recv())
                ws.close()
            except Exception:
                pass
        # CDP returns 200 OK even when the JS itself threw — surface that.
        ed = resp.get("result", {}).get("exceptionDetails")
        if ed:
            desc = (ed.get("exception", {}).get("description")
                    or ed.get("text") or str(ed))
            print(f"    (js threw: {desc.splitlines()[0][:120]})")
            return False
        return True
    except Exception as e:
        print(f"    (js error: {e})")
        return False


def execute_taps(operations, screen_w, screen_h, package_name=None):
    """Run a list of tap/wait/back/js operations."""
    for op in operations:
        if op[0] == "tap":
            _, x_frac, y_frac, wait_ms = op
            x = int(screen_w * x_frac)
            y = int(screen_h * y_frac)
            run(["adb", "shell", "input", "tap", str(x), str(y)], check=False)
            time.sleep(wait_ms / 1000.0)
        elif op[0] == "wait":
            time.sleep(op[1] / 1000.0)
        elif op[0] == "back":
            run(["adb", "shell", "input", "keyevent", "KEYCODE_BACK"],
                check=False)
            time.sleep(0.5)
        elif op[0] == "js":
            # ["js", "<expression>", optional_wait_ms]
            expr = op[1]
            wait_ms = op[2] if len(op) >= 3 else 400
            if package_name:
                ok = evaluate_js(package_name, expr)
                print(f"    js {'✓' if ok else '✗'}: {expr[:70]}")
            time.sleep(wait_ms / 1000.0)


def capture_to(out_path, package_name=None):
    """Capture device screen to local file via adb."""
    remote = "/sdcard/_screenshot.png"
    run(["adb", "shell", "screencap", "-p", remote], check=False)
    run(["adb", "pull", remote, str(out_path)], check=False)
    run(["adb", "shell", "rm", remote], check=False)
    return out_path.exists() and out_path.stat().st_size > 0


def load_per_app_taps(app_dir):
    """If <App>/test/screenshot_taps.json exists, use those overrides."""
    p = app_dir / "test" / "screenshot_taps.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name")
    ap.add_argument("--slot", help="capture only this slot (e.g., 03)")
    ap.add_argument("--no-launch", action="store_true",
                    help="don't auto-launch emulator (use already-running)")
    ap.add_argument("--avd", help="AVD name (default: first installed)")
    ap.add_argument("--no-reinstall", action="store_true",
                    help="skip APK reinstall (default: reinstall)")
    args = ap.parse_args()

    app_dir = REPO_ROOT / args.app_name
    if not app_dir.is_dir():
        print(f"ERROR: app directory not found: {app_dir}")
        sys.exit(1)

    package = get_package_name(app_dir)
    if not package:
        print(f"ERROR: could not read applicationId from "
              f"{app_dir}/android/app/build.gradle")
        sys.exit(1)
    print(f"Package: {package}")

    print("Checking emulator...")
    if not args.no_launch:
        if not ensure_emulator_running(args.avd):
            sys.exit(1)
    else:
        result = run(["adb", "devices"], check=False)
        if not result or "\tdevice" not in result.stdout:
            print("ERROR: no emulator running.")
            sys.exit(1)

    screen_w, screen_h = get_screen_size()
    print(f"Screen size: {screen_w}×{screen_h}")

    if not args.no_reinstall:
        if not install_apk(app_dir):
            sys.exit(1)

    taps = load_per_app_taps(app_dir) or DEFAULT_TAPS
    out_dir = app_dir / "store" / "screenshots" / "phone" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    SLOTS = [
        ("01", "01_deep_gameplay"),
        ("02", "02_early_gameplay"),
        ("03", "03_level_complete"),
        ("04", "04_missions_panel"),
        ("05", "05_stats"),
        ("06", "06_levels_grid"),
        ("07", "07_menu"),
    ]
    if args.slot:
        SLOTS = [s for s in SLOTS if s[0] == args.slot]
        if not SLOTS:
            print(f"ERROR: invalid slot {args.slot}")
            sys.exit(1)

    readiness_expr = taps.get("_readiness_expr") if isinstance(taps, dict) else None

    # Setup taps run once before the per-slot loop. Use this to seed
    # in-memory state so subsequent captures show mid-game numbers
    # instead of all-zeros first-launch. When a setup is present we
    # skip the force-stop between slots (which would wipe the seed)
    # and reset the screen via JS instead.
    setup_ops = taps.get("_setup_taps", []) if isinstance(taps, dict) else []
    use_persistent_session = bool(setup_ops)

    if use_persistent_session:
        print("[setup] launching app + seeding state…")
        force_stop_and_launch(package, readiness_expr=readiness_expr)
        execute_taps(setup_ops, screen_w, screen_h, package_name=package)
        print()

    print()
    for slot_num, tap_key in SLOTS:
        print(f"[{slot_num}] {tap_key}")
        if use_persistent_session:
            # Reset to menu via JS (cheap) instead of full force-stop wipe
            evaluate_js(package, "if(typeof showScreen==='function')showScreen('menu');")
            time.sleep(0.5)
        else:
            force_stop_and_launch(package, readiness_expr=readiness_expr)
        ops = taps.get(tap_key, [])
        if ops:
            execute_taps(ops, screen_w, screen_h, package_name=package)
        else:
            time.sleep(1)
        # SurfaceFlinger composite delay — empirically Pixel6_API34 races
        # for slots that load 20×20 grids; 2s is conservative.
        time.sleep(2.0)
        out_path = out_dir / f"{slot_num}.png"
        cap_pkg = package if use_persistent_session else None
        if capture_to(out_path, package_name=cap_pkg):
            kb = out_path.stat().st_size // 1024
            print(f"     ✓ {out_path.name} ({kb} KB)")
        else:
            print(f"     ✗ capture failed")
        print()

    print(f"Done. Output: {out_dir}")
    print()
    print("Verify each PNG against SHIP_GAME §3.6 checklist:")
    print("  - Mobile proportions look right")
    print("  - Playable area fills ≥50% of canvas")
    print("  - Real numbers showing (not all zeros)")
    print("  - Mid-progression content (not Level 1)")
    print()
    print("If a slot captured the wrong screen, edit DEFAULT_TAPS at the top")
    print(f"or create per-app override at {app_dir}/test/screenshot_taps.json.")


if __name__ == "__main__":
    main()
