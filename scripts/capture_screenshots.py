#!/usr/bin/env python3
"""
capture_screenshots.py — capture raw screenshots from the running Android emulator.

Boots the user's Android emulator if not already running, installs the
app's latest debug APK, navigates to each of 6 in-app GAMEPLAY states by
sending tap events via adb, and saves screenshots to:

    <AppName>/store/screenshots/phone/raw/01.png ... 06.png

The main menu / shop / settings are NOT captured — every store slot must
show actual gameplay (CLAUDE.md "Things to flag", QUALITY_PLAYBOOK §7.1).

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
4. For each of 6 slots:
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
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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
    # NOTE: no menu/shop/settings slot — every store screenshot must show
    # actual gameplay (CLAUDE.md "Things to flag", QUALITY_PLAYBOOK §7.1).
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


def _ahash(path):
    """Fast 17x16 dHash for matching captures (content-sensitive).

    Replaces 8x8 average hash (which collapsed visually-distinct
    screens like Nonogram's level 348 board vs daily challenge board
    to the same fingerprint, since both have similar overall light/
    dark distribution). dHash compares adjacent pixel pairs and is
    sensitive to content/edge structure rather than just brightness.
    Returns None if PIL unavailable or path unreadable.
    """
    if not HAS_PIL:
        return None
    try:
        img = Image.open(path).convert("L").resize((17, 16))
        pixels = list(img.getdata())
        h = 0
        for r in range(16):
            for c in range(16):
                left  = pixels[r * 17 + c]
                right = pixels[r * 17 + c + 1]
                if left > right:
                    h |= 1 << (r * 16 + c)
        return h
    except (IOError, OSError):
        return None


def _hamming(a, b):
    return bin(a ^ b).count("1")


# Per-target preferred AVD name. The user creates these via Part B
# of the May 2026 mandatory-tablets rollout; if they're not present,
# we fall back to the first AVD matching the form-factor profile, then
# to the first AVD overall.
TARGET_AVD_PREFIX = {
    "phone":     None,                 # any AVD is fine
    "tablet_7":  "pegasus_tablet_7",
    "tablet_10": "pegasus_tablet_10",
}


def _pick_avd(avds, target, explicit=None):
    if explicit and explicit in avds:
        return explicit
    preferred = TARGET_AVD_PREFIX.get(target)
    if preferred and preferred in avds:
        return preferred
    if target in ("tablet_7", "tablet_10"):
        # Prefer any AVD whose name suggests it's a tablet
        for a in avds:
            la = a.lower()
            if "tablet" in la or "pixel_c" in la or "nexus_10" in la:
                return a
    return avds[0]


def ensure_emulator_running(avd_name=None, target="phone"):
    """Boot an emulator if none is running. Wait for boot to complete.

    For tablet_7 / tablet_10 targets, prefers the matching pegasus_tablet_*
    AVD (created via SHIP_GAME Part B). Falls back to any tablet-profile
    AVD found via name heuristic, then to first AVD overall.
    """
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

    chosen = _pick_avd(avds, target, explicit=avd_name)
    print(f"  Launching emulator ({target}): {chosen}")

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
    # force-stop is async — wait until the process is actually gone, else
    # the launch below races the dying instance ("intent delivered to
    # currently running top-most instance") and the app never comes up.
    for _ in range(25):
        if not _get_app_pid(package_name):
            break
        time.sleep(0.2)
    time.sleep(0.4)
    # Cold-start via the LAUNCHER intent. `am start -n pkg/.MainActivity`
    # proved unreliable on some emulators (delivers to a stale task record
    # and the activity self-finishes); monkey's LAUNCHER launch is robust.
    run(["adb", "shell", "monkey", "-p", package_name,
         "-c", "android.intent.category.LAUNCHER", "1"], check=False)
    for _ in range(25):
        if _get_app_pid(package_name):
            break
        time.sleep(0.2)
    time.sleep(3.5)  # let MainActivity.loadUrl finish; skip _force_cdp_navigate
    # The MainActivity already loadUrl()s file:///android_asset/game.html;
    # forcing another Page.navigate via CDP can leave the icon row in a
    # detached state where adb taps reach the menu but onclick handlers
    # don't fire (Puzzle2048 May 2026 audit). Trust the natural load.
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
            # Prefer the app's own WebView page (file:///android_asset/
            # game.html) over AdMob/ad-network iframe pages, which also
            # expose a CDP target and otherwise sort first.
            def _is_game(pg):
                u = pg.get("url") or ""
                return ("android_asset" in u or "game.html" in u
                        or u.startswith("file://"))
            ordered = sorted(pages, key=lambda pg: 0 if _is_game(pg) else 1)
            for p in ordered:
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
        # Drain events until we see our response (id=1). Android WebView
        # CDP frequently emits `Page.frameRequestedNavigation` or
        # `Runtime.executionContextDestroyed` events ahead of the
        # response; reading just one recv() and re-sending the eval (the
        # old behavior) caused the JS to run TWICE — for Promise-based
        # slot JS this raced and reverted screen state right before
        # screencap.
        resp = None
        for _ in range(50):
            msg = _json.loads(ws.recv())
            if msg.get("id") == 1 and "result" in msg:
                resp = msg
                break
        ws.close()
        if resp is None:
            return False
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
        elif op[0] == "swipe":
            # ["swipe", x1_frac, y1_frac, x2_frac, y2_frac, duration_ms,
            #  optional_post_wait_ms]
            _, x1f, y1f, x2f, y2f, dur = op[:6]
            post_wait_ms = op[6] if len(op) >= 7 else 300
            x1 = int(screen_w * x1f); y1 = int(screen_h * y1f)
            x2 = int(screen_w * x2f); y2 = int(screen_h * y2f)
            run(["adb", "shell", "input", "swipe",
                 str(x1), str(y1), str(x2), str(y2), str(dur)],
                check=False)
            time.sleep(post_wait_ms / 1000.0)
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


def load_per_app_taps(app_dir, target="phone"):
    """If <App>/test/screenshot_taps_<target>.json exists, use that.
    Otherwise fall back to <App>/test/screenshot_taps.json."""
    if target != "phone":
        p_target = app_dir / "test" / f"screenshot_taps_{target}.json"
        if p_target.exists():
            return json.loads(p_target.read_text())
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
    ap.add_argument("--target", choices=["phone", "tablet_7", "tablet_10"],
                    default="phone",
                    help="capture target form factor — output goes to "
                         "<App>/store/screenshots/<target>/raw/")
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

    print(f"Target: {args.target}")
    print("Checking emulator...")
    if not args.no_launch:
        if not ensure_emulator_running(args.avd, target=args.target):
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

    # Grant POST_NOTIFICATIONS so the Android 13+ runtime-permission
    # dialog doesn't pop over the WebView and land in the screenshot.
    run(["adb", "shell", "pm", "grant", package,
         "android.permission.POST_NOTIFICATIONS"], check=False)

    taps = load_per_app_taps(app_dir, args.target) or DEFAULT_TAPS
    # If the per-app tap file has tablet_<N>_<slot> keys for this target,
    # prefer those; otherwise fall back to the phone (un-prefixed) keys.
    out_dir = app_dir / "store" / "screenshots" / args.target / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    SLOTS = [
        ("01", "01_deep_gameplay"),
        ("02", "02_early_gameplay"),
        ("03", "03_level_complete"),
        ("04", "04_missions_panel"),
        ("05", "05_stats"),
        ("06", "06_levels_grid"),
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
    captured_hashes = {}  # slot_num -> ahash, for verification
    for slot_num, tap_key in SLOTS:
        print(f"[{slot_num}] {tap_key}")
        # Always do force-stop+launch between slots. The cheaper "showScreen('menu')
        # via JS" path turned out to be unreliable on Android WebView CDP — JS
        # navigation calls didn't always take effect before screencap, leaving
        # the screen on whatever it was before. force_stop_and_launch is ~5s
        # slower per slot but produces consistent captures.
        force_stop_and_launch(package, readiness_expr=readiness_expr)
        # If the per-app file has a _setup_taps section, re-run it after each
        # launch to re-seed in-memory state (localStorage persists across
        # force-stop, but `state = Object.assign({}, DEFAULT_STATE)` runs
        # fresh on page load and only loadState() merges localStorage).
        if setup_ops:
            execute_taps(setup_ops, screen_w, screen_h, package_name=package)
        # Tablet-aware key lookup: tablet_7_03_level_complete falls back
        # to 03_level_complete when the per-app file doesn't ship a
        # tablet override.
        target_key = f"{args.target}_{tap_key}" if args.target != "phone" else tap_key
        ops = taps.get(target_key) or taps.get(tap_key, [])
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
            # ★ Post-capture verification: each slot must produce
            # visually distinct content from prior slots. If two slots
            # match, the tap sequence didn't navigate anywhere.
            new_hash = _ahash(out_path)
            if new_hash is not None:
                for prev_slot, prev_hash in captured_hashes.items():
                    distance = _hamming(new_hash, prev_hash)
                    # 24/256 ≈ 9% bit-difference; distinct in-app screens
                    # are usually 30+ apart, identical-screen captures < 5.
                    if distance <= 24:
                        print(f"\n  ✗ CAPTURE VERIFICATION FAILED: slot "
                              f"{slot_num} matches slot {prev_slot} "
                              f"(perceptual distance {distance}).",
                              file=sys.stderr)
                        print(f"    The tap sequence didn't navigate "
                              f"anywhere — same screen captured twice.",
                              file=sys.stderr)
                        print(f"    Common causes:", file=sys.stderr)
                        print(f"      - tap coordinates wrong for this app's "
                              f"layout (edit screenshot_taps.json)",
                              file=sys.stderr)
                        print(f"      - emulator screen size differs from "
                              f"the assumed {screen_w}x{screen_h}",
                              file=sys.stderr)
                        print(f"      - menu re-rendered between tap and "
                              f"capture (increase post-tap delay)",
                              file=sys.stderr)
                        print(f"    Inspect {out_path} and adjust per-app "
                              f"taps before re-running. (continuing)",
                              file=sys.stderr)
                        # Don't abort — let the run finish so the user can
                        # inspect ALL captured slots before iterating on
                        # tap coords. pre_publish_check.py also runs the
                        # uniqueness check and will block ship if any
                        # remain duplicated.
                        break
                captured_hashes[slot_num] = new_hash
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
