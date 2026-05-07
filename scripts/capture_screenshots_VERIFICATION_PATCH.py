#!/usr/bin/env python3
"""
PATCH for scripts/capture_screenshots.py — adds post-capture verification
that each slot's tap sequence actually navigated to a different screen.

The May 2026 Puzzle2048 audit found that 5 of 7 phone slots used the
same raw capture because adb taps missed their target buttons. The
script silently captured the menu/initial state for all of them and
moved on. The wrapper then put 7 different headlines over 2 distinct
images.

Fix: hash each capture as it's produced. If a new capture matches a
previous slot's hash, fail loudly and tell the user to inspect the tap
coordinates for that slot.

Add these imports at the top:
    import hashlib
    from PIL import Image  # already imported elsewhere

Replace the per-slot capture loop (currently around lines 250-280) with:
"""

# ---------- snippet to merge into capture_screenshots.py ----------

import hashlib
import sys

def _ahash(path):
    """Fast 8x8 perceptual hash for matching captures."""
    from PIL import Image
    img = Image.open(path).convert("L").resize((8, 8))
    pixels = list(img.getdata())
    avg = sum(pixels) / 64
    return sum((1 << i) for i, p in enumerate(pixels) if p > avg)


def _hamming(a, b):
    return bin(a ^ b).count("1")


def capture_with_verification(app_name, slot_filter=None, debug=False):
    """Capture each slot, verify it differs from prior captures.

    REPLACES the original `capture()` function. The diff vs original is
    just the 'verify against prior hashes' block after each save.
    """
    # ... (all existing setup: emulator boot, package detection, install) ...

    captured_hashes = {}  # slot_name -> ahash

    for slot in SLOTS:  # SLOTS list as before
        if slot_filter and slot["slot"] != slot_filter:
            continue

        # 1. Force-stop + relaunch app (clean state)
        run(["adb", "shell", "am", "force-stop", package])
        run(["adb", "shell", "am", "start", "-n",
             f"{package}/.MainActivity"])
        time.sleep(2.5)  # was 1.5; bumped because slow emulators sometimes
                          # hadn't finished menu render before taps fired,
                          # which is one cause of taps missing buttons

        # 2. Run tap sequence
        for op in slot["taps"]:
            run(["adb", "shell", "input", "tap",
                 str(int(op["x"] * SCREEN_W)),
                 str(int(op["y"] * SCREEN_H))])
            time.sleep(op.get("delay", 0.8))

        # 3. Wait for animations to settle
        time.sleep(slot.get("post_delay", 1.0))

        # 4. Capture
        out_path = OUT_DIR / f"{slot['slot']}.png"
        run(["adb", "shell", "screencap", "-p", "/sdcard/_cap.png"])
        run(["adb", "pull", "/sdcard/_cap.png", str(out_path)])
        run(["adb", "shell", "rm", "/sdcard/_cap.png"])

        # 5. ★ NEW: verify this capture is distinct from prior slots
        new_hash = _ahash(out_path)
        for prev_slot, prev_hash in captured_hashes.items():
            distance = _hamming(new_hash, prev_hash)
            if distance <= 4:
                print(f"\n  ✗ CAPTURE FAILED: slot {slot['slot']} matches "
                      f"slot {prev_slot} (perceptual distance {distance}).",
                      file=sys.stderr)
                print(f"    The tap sequence didn't navigate anywhere — "
                      f"the script is capturing the same screen twice.",
                      file=sys.stderr)
                print(f"    Common causes:", file=sys.stderr)
                print(f"      - tap coordinates wrong (button isn't where "
                      f"x={slot['taps']}, y=... clicks)", file=sys.stderr)
                print(f"      - emulator screen size differs from script's "
                      f"assumed {SCREEN_W}x{SCREEN_H}", file=sys.stderr)
                print(f"      - menu re-renders covered up the button before "
                      f"tap landed (increase post_delay for this slot)",
                      file=sys.stderr)
                print(f"    Inspect the captured PNG and adjust tap coords "
                      f"in screenshot_taps.json for this app.",
                      file=sys.stderr)
                # Don't continue — let the user fix it. Otherwise they'd
                # ship 7 wrapped screenshots with 2 distinct images.
                sys.exit(2)

        captured_hashes[slot["slot"]] = new_hash
        print(f"  ✓ slot {slot['slot']} → {out_path.name}")

    print(f"\nAll {len(captured_hashes)} slots captured with distinct content.")


# ---------- end snippet ----------


"""
ALSO ADD: a per-app override file. The default tap coordinates assume
a "Pegasus standard menu layout" that doesn't exist for every app.
Puzzle2048 has DAILY/BEST as primary buttons and three shop/themes/grid
icons in a row — different from the WaterSort layout the defaults
target.

Document at the top of capture_screenshots.py:

    Per-app overrides:
        Place <App>/test/screenshot_taps.json with shape:
        {
          "01_deep_gameplay": [
            {"x": 0.50, "y": 0.55, "delay": 0.8},
            {"x": 0.30, "y": 0.40, "delay": 1.2}
          ],
          "03_level_complete": [...]
        }
        These OVERRIDE DEFAULT_TAPS for that app. Coordinates are
        fractions of screen w/h, NOT absolute pixels.

    For each NEW app, the first capture run will likely fail
    verification — that's expected. Open the resulting PNGs, see what
    actually got captured, identify which screens you wanted, edit
    screenshot_taps.json with the correct coordinates, re-run.

    The verification check makes this an iterative loop instead of
    silently shipping bad captures.

ALSO ADD: pre-capture localStorage seed for tutorial-dismissed flags.
Each app's game.html has its own key. Generic seed_screenshot_state.js
must be supplemented with per-app keys. Document:

    Per-app localStorage seed:
        Place <App>/test/seed_screenshot_state.js with the EXACT keys
        that app's game.html reads. Don't rely on the generic template
        — every app uses different storage keys.
        
        For Puzzle2048 specifically (per audit):
        localStorage.setItem('p2048_tutorial_seen', 'true');
        localStorage.setItem('p2048_score', '247');
        localStorage.setItem('p2048_best', '512');
        localStorage.setItem('p2048_best_tile', '128');
        localStorage.setItem('p2048_coins', '85');
        ...
        Read the actual key names from game.html before populating.
"""
