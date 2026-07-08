#!/usr/bin/env python3
"""Pre-publish gate: notification per-day cap must be ENFORCED in the receiver.

Bug class (audit 2026-07): the notification suite schedules a daily reminder
(~19:00), win-back (noon on d3/d7/d14/d30), streak-at-risk (20:30) and
lives-refilled with UNIQUE request codes, so each type never duplicates. But
on a single absent day, win-back + daily reminder + streak-at-risk can all
fire — 3 notifications the same day. MainActivity declared NOTIF_CAP_PER_DAY=2
but NEVER referenced it, and NotificationReceiver.onReceive showed every alarm
unconditionally, so the cap did not exist and the opt-out was only checked at
schedule time (not fire time).

Fix (in NotificationReceiver.onReceive, all 8 AdMob apps): re-check the
"notifications_enabled" pref at fire time AND keep a per-calendar-day counter
(notif_day_key / notif_day_count), dropping anything past the cap.

This gate scopes to apps whose MainActivity uses the growth notification suite
(scheduleWinBack) and BLOCKS if their NotificationReceiver does not enforce
both the fire-time opt-out re-check and the per-day counter.
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _receiver(app: str):
    for p in (REPO / app / "android/app/src/main/java").glob("**/NotificationReceiver.java"):
        return p
    return None


def _uses_suite(app: str) -> bool:
    for p in (REPO / app / "android/app/src/main/java").glob("**/MainActivity.java"):
        if "scheduleWinBack" in p.read_text(encoding="utf-8", errors="replace"):
            return True
    return False


def check_app(app: str):
    blockers: list[str] = []
    warnings: list[str] = []
    if not _uses_suite(app):
        return blockers, warnings  # not a growth-notification app
    nr = _receiver(app)
    if nr is None:
        blockers.append(f"{app}: uses scheduleWinBack but has no NotificationReceiver.java")
        return blockers, warnings
    src = nr.read_text(encoding="utf-8", errors="replace")
    # Fire-time opt-out re-check.
    if "notifications_enabled" not in src:
        blockers.append(
            f"{app}: NotificationReceiver does not re-check the "
            f"\"notifications_enabled\" opt-out at fire time")
    # Per-day counter + cap return.
    has_counter = "notif_day_count" in src and "notif_day_key" in src
    has_cap_return = ">=" in src and "NOTIF_CAP_PER_DAY" in src
    if not (has_counter and has_cap_return):
        blockers.append(
            f"{app}: NotificationReceiver does not enforce a per-day cap "
            f"(needs notif_day_key/notif_day_count + a NOTIF_CAP_PER_DAY guard) "
            f"— win-back + daily + streak can stack 3+/day")
    return blockers, warnings


def main():
    apps = sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(
            p.name for p in REPO.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))
            and (p / "android").is_dir())
    fail = 0
    checked = 0
    for app in apps:
        b, _ = check_app(app)
        if _uses_suite(app):
            checked += 1
        for line in b:
            print(f"✗ {line}")
            fail = 1
    if not fail:
        print(f"[notif cadence cap] {checked} growth-notification app(s) clean")
    return fail


if __name__ == "__main__":
    sys.exit(main())
