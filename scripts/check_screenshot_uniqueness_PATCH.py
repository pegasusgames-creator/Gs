"""
PATCH for pre_publish_check.py — paste BOTH functions in alongside the
other check_* functions, then register them in main() with:

    section("store", "screenshot uniqueness",   check_screenshot_uniqueness, apps)
    section("store", "screenshot completeness", check_screenshot_completeness, apps)

The uniqueness check catches the May 2026 Puzzle2048 capture-pipeline
failure (5 of 7 phone slots used the same raw because adb taps missed
their targets). The completeness check enforces the May 2026 mandatory-
tablets policy (every app must have phone + tablet_7 + tablet_10 sets
populated, or it doesn't ship).
"""

import hashlib
import os


def check_screenshot_uniqueness(apps):
    """BLOCKING: each phone slot must show distinct in-app content.

    The Puzzle2048 May 2026 capture failure: 5 of 7 slots used the same
    raw screenshot because adb taps missed their target buttons. The
    pipeline produced 7 wrapped screenshots with different headlines
    over visually identical phone content — a Play Store Misleading
    Behavior policy risk and an obvious tell that the app was
    unfinished.

    This check:
    1. Hashes each <App>/store/screenshots/phone/raw/NN.png and blocks
       if any two slots share a hash (or are perceptually within 4
       hamming distance).
    2. If <App>/store/screenshots/tablet_7/ or tablet_10/ exists with
       raw/ contents, hashes those too and blocks if any tablet raw
       matches any phone raw (tablet captures must be at tablet
       resolution, not rescaled phone captures).
    """
    blocking = []
    warnings = []

    try:
        from PIL import Image
    except ImportError:
        warnings.append("PIL not installed — skipping screenshot uniqueness check. "
                        "Run: pip install pillow")
        return blocking, warnings

    def ahash(path):
        """8x8 average hash — fast perceptual fingerprint."""
        try:
            img = Image.open(path).convert("L").resize((8, 8))
            pixels = list(img.getdata())
            avg = sum(pixels) / 64
            return sum((1 << i) for i, p in enumerate(pixels) if p > avg)
        except (IOError, OSError):
            return None

    def hamming(a, b):
        return bin(a ^ b).count("1")

    for app in apps:
        # Phone raws
        phone_raw_dir = os.path.join(app, "store", "screenshots", "phone", "raw")
        phone_hashes = {}
        if os.path.isdir(phone_raw_dir):
            for fname in sorted(os.listdir(phone_raw_dir)):
                if not fname.lower().endswith(".png"):
                    continue
                path = os.path.join(phone_raw_dir, fname)
                h = ahash(path)
                if h is None:
                    continue
                # Compare against previously-seen phone hashes
                for prev_name, prev_h in phone_hashes.items():
                    if hamming(h, prev_h) <= 4:
                        blocking.append(
                            f"{app}: phone raw {fname} is visually identical "
                            f"to {prev_name} (perceptual hash distance ≤ 4). "
                            f"capture_screenshots.py likely failed to navigate "
                            f"to a different in-app screen — adb taps missed "
                            f"their targets. Re-run capture, verify each slot "
                            f"shows distinct content per SHIP_GAME §3.6."
                        )
                        break
                phone_hashes[fname] = h

        # Tablet raws — none of them should match any phone raw
        for tablet_size in ("tablet_7", "tablet_10"):
            tablet_raw_dir = os.path.join(app, "store", "screenshots",
                                          tablet_size, "raw")
            if not os.path.isdir(tablet_raw_dir):
                continue
            for fname in sorted(os.listdir(tablet_raw_dir)):
                if not fname.lower().endswith(".png"):
                    continue
                path = os.path.join(tablet_raw_dir, fname)
                h = ahash(path)
                if h is None:
                    continue
                # Check resolution — tablet should be ≥1200 wide
                try:
                    w, _ = Image.open(path).size
                    if w < 1200:
                        blocking.append(
                            f"{app}: {tablet_size}/raw/{fname} is only "
                            f"{w}px wide — tablet captures must be at "
                            f"tablet resolution (1200×1920 for 7\", "
                            f"1800×2560 for 10\"). Phone resolution "
                            f"upscaled to a tablet canvas looks like a "
                            f"phone running in tablet emulation — "
                            f"obvious to reviewers."
                        )
                except (IOError, OSError):
                    pass
                # Check it doesn't match a phone raw
                for phone_name, phone_h in phone_hashes.items():
                    if hamming(h, phone_h) <= 4:
                        blocking.append(
                            f"{app}: {tablet_size}/raw/{fname} is visually "
                            f"identical to phone/raw/{phone_name}. Tablet "
                            f"captures must be SEPARATE captures from a "
                            f"tablet emulator (different in-app layout, "
                            f"different aspect ratio), not the phone raws "
                            f"placed inside a tablet wrap."
                        )
                        break

    return blocking, warnings


def check_screenshot_completeness(apps):
    """BLOCKING: every shipping app must have phone + tablet_7 + tablet_10
    screenshot sets fully populated.

    Per QUALITY_PLAYBOOK §7.3 (mandatory tablets policy, May 2026), no app
    ships without all three sets. Apps with `app_info.json:first_upload_at`
    set get only a warning (already shipped — handle on next update).
    Apps in pre-ship state get blocked.

    Counts wrapped PNGs (not raws) at:
      <App>/store/screenshots/phone/0N.png        — needs ≥2, ideally 7
      <App>/store/screenshots/tablet_7/0N.png     — needs ≥2, ideally 7
      <App>/store/screenshots/tablet_10/0N.png    — needs ≥2, ideally 7
    """
    blocking = []
    warnings = []
    REQUIRED_MIN = 7  # Pegasus standard; Play Console minimum is 2

    for app in apps:
        # Skip if not a real app folder
        if not os.path.isdir(os.path.join(app, "android")):
            continue

        # Already-shipped apps get warnings, pre-ship apps get blockers
        is_shipped = False
        info_path = os.path.join(app, "metadata", "app_info.json")
        if os.path.exists(info_path):
            try:
                import json
                with open(info_path) as f:
                    info = json.load(f)
                is_shipped = bool(info.get("first_upload_at"))
            except (IOError, ValueError):
                pass

        for set_name in ("phone", "tablet_7", "tablet_10"):
            set_dir = os.path.join(app, "store", "screenshots", set_name)
            if not os.path.isdir(set_dir):
                msg = (f"{app}: store/screenshots/{set_name}/ does not exist. "
                       f"Per QUALITY_PLAYBOOK §7.3, all apps require phone + "
                       f"tablet_7 + tablet_10 screenshots. Run: "
                       f"python3 scripts/capture_screenshots.py {app} "
                       f"--target {set_name}")
                (warnings if is_shipped else blocking).append(msg)
                continue

            # Count wrapped PNGs (NN.png at root of set, not raws)
            wrapped = [f for f in os.listdir(set_dir)
                       if f.endswith(".png") and not f.startswith(".")
                       and f[0:2].isdigit()]
            if len(wrapped) < 2:
                msg = (f"{app}: {set_name}/ has only {len(wrapped)} wrapped "
                       f"screenshot(s). Play Console requires ≥2; Pegasus "
                       f"standard is 7.")
                (warnings if is_shipped else blocking).append(msg)
            elif len(wrapped) < REQUIRED_MIN:
                warnings.append(
                    f"{app}: {set_name}/ has {len(wrapped)} wrapped "
                    f"screenshots (Pegasus standard is {REQUIRED_MIN}). "
                    f"Below standard but above Play Console minimum.")

    return blocking, warnings
