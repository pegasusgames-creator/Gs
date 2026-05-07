"""
PATCH for scripts/wrap_tablet_screenshots.py — adds resolution check
that prevents wrapping phone-resolution captures inside tablet canvases.

May 2026 Puzzle2048 audit found that tablet wraps embedded phone-aspect
device mockups inside tablet-aspect canvases — the result looks like a
phone running in a tablet emulator, not a tablet app. The reason: the
script reads from <App>/store/screenshots/phone/raw/ for tablet wraps
when the tablet directory is empty, OR the user pointed it at phone
raws.

Tablet wraps must use captures from a tablet emulator at tablet
resolution. The tablet emulator renders the in-app layout differently
(wider boards, side panels for some games, larger HUD elements), so
captures at tablet resolution show a fundamentally different in-app
layout from phone captures.

Add at the top of wrap_image() function:
"""

# ---------- snippet ----------

from PIL import Image

def wrap_tablet_image(raw_path, out_path, headline, subtitle, app_display_name,
                      theme, target_size):
    """Wrap a tablet raw screenshot.

    target_size: ("tablet_7", 1200, 1920) or ("tablet_10", 1800, 2560)
    """
    raw = Image.open(raw_path)
    rw, rh = raw.size

    # ★ NEW: enforce that the raw came from a tablet capture
    EXPECTED_MIN_WIDTH = {"tablet_7": 1200, "tablet_10": 1800}[target_size[0]]
    if rw < EXPECTED_MIN_WIDTH:
        raise ValueError(
            f"\n  ✗ {raw_path}: raw screenshot is only {rw}x{rh}, "
            f"too narrow for {target_size[0]} target.\n"
            f"    Tablet wraps must use raw captures from a TABLET emulator at\n"
            f"    {EXPECTED_MIN_WIDTH}px+ width, not phone captures rescaled.\n"
            f"    The in-app layout on a tablet emulator is genuinely different\n"
            f"    (different aspect ratio, possibly different HUD layout).\n\n"
            f"    To capture tablet raws:\n"
            f"      1. Boot a tablet AVD: emulator -avd <tablet_avd>\n"
            f"      2. Install the APK\n"
            f"      3. python3 scripts/capture_screenshots.py {raw_path.split('/')[0]} --target tablet_7\n"
            f"         (or tablet_10)\n"
            f"      4. Re-run this wrap script.\n\n"
            f"    DO NOT rescale phone captures — tablet users see this is wrong\n"
            f"    in 0.5 seconds and uninstall."
        )

    # Also guard against the aspect ratio being suspicious
    aspect = rh / rw
    expected_aspect_min = 1.55  # 1200x1920 = 1.6, allow some slack
    if aspect < expected_aspect_min:
        raise ValueError(
            f"{raw_path}: aspect ratio {aspect:.2f} is too short for tablet. "
            f"Tablet portrait should be ~1.6 (1200x1920) or ~1.42 (1800x2560). "
            f"This looks like a phone capture (typically 2.22 = 1080x2400) "
            f"that's been letterboxed."
        )

    # ... rest of original wrap logic continues ...

# ---------- end snippet ----------


"""
ALTERNATIVELY — and this is what I'd actually recommend for Pegasus:

DROP TABLET SCREENSHOTS ENTIRELY for the long-tail apps.

Google Play does NOT require tablet screenshots. They're optional.
Apps that don't have tablet screenshots get sorted to the bottom of
the tablet Play Store, but the vast majority of casual puzzle game
installs come from phone Play Store anyway.

Capturing+wrapping tablet screenshots well is 2-3x the work of phone
captures because the tablet emulator boots slower, the in-app layout
needs to be tested separately, and the capture pipeline needs separate
tap coordinate sets.

For a portfolio of 100 apps with one solo developer, the realistic
strategy:

  - Hero app (WaterSort): yes, tablet screenshots, well-curated, every
    one shot at real tablet resolution
  - Other 4 flagships: phone-only is fine
  - Long-tail apps: phone-only

Update SHIP_GAME.md Phase 3 to make tablet screenshots OPTIONAL and
explicitly recommend skipping for non-hero apps.
"""
