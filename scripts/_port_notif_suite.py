#!/usr/bin/env python3
"""Port WaterSortPuzzle's full notification suite into the 3 sister apps.

The notification code lives in three places per app:
  - MainActivity.java         (constants + bridge methods + scheduleAlarm helpers)
  - NotificationReceiver.java (alarm receiver; identical across apps except pkg)
  - AndroidManifest.xml       (queries + receiver — already present)

This script is idempotent: re-running over an already-ported app should be a no-op.
Run from repo root:  python3 scripts/_port_notif_suite.py

It also:
  - Sets each target's CROSS_PROMO_PACKAGES list per the 2026-05-25 growth spec
    (no UnblockPuzzle/PipeConnect as targets — they're pre-release).
  - Adds scheduleWinBack to each target.

NOT TOUCHED here:
  - JS-side wiring (game.html) — done in a separate JS pass.
  - Manifest <queries> updates — done in Part B.
"""

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Per the 2026-05-25 spec — never include pre-release apps as cross-promo targets.
PROMO = {
    "Nonogram":      ['com.pegasusgames.watersortpuzzle', 'com.pegasusgames.puzzle2048'],
    "Puzzle2048":    ['com.pegasusgames.watersortpuzzle', 'com.pegasusgames.nonogram'],
    "UnblockPuzzle": ['com.pegasusgames.watersortpuzzle', 'com.pegasusgames.nonogram', 'com.pegasusgames.puzzle2048'],
}

APP_PKG = {
    "Nonogram":      "com.pegasusgames.nonogram",
    "Puzzle2048":    "com.pegasusgames.puzzle2048",
    "UnblockPuzzle": "com.pegasusgames.unblockpuzzle",
}

APP_TITLE = {
    "Nonogram":      "Nonogram",
    "Puzzle2048":    "Puzzle 2048",
    "UnblockPuzzle": "Unblock Puzzle",
}

APP_DAILY_BODY = {
    "Nonogram":      "Your daily nonogram challenge is ready!",
    "Puzzle2048":    "Your daily 2048 challenge is ready!",
    "UnblockPuzzle": "Your daily unblock challenge is ready!",
}


def java_path(app: str) -> Path:
    """Locate the MainActivity.java for an app (the per-app package subdir)."""
    base = REPO / app / "android" / "app" / "src" / "main" / "java" / "com" / "pegasusgames"
    subs = [p for p in base.iterdir() if p.is_dir()]
    assert len(subs) == 1, f"expected 1 package dir under {base}, got {subs}"
    return subs[0] / "MainActivity.java"


def receiver_path(app: str) -> Path:
    base = REPO / app / "android" / "app" / "src" / "main" / "java" / "com" / "pegasusgames"
    subs = [p for p in base.iterdir() if p.is_dir()]
    return subs[0] / "NotificationReceiver.java"


# The constants block injected just below the existing WEBVIEW_BG_COLOR (or
# whatever marker we hit). Idempotent: skipped if REQ_DAILY_REMINDER already present.
CONSTANTS_BLOCK = """
    // ── Notification scheduling (NOTIFICATIONS_IMPL.md §1) ────────────────────
    private static final int REQ_DAILY_REMINDER       = 1001;
    private static final int REQ_STREAK_AT_RISK       = 1002;
    private static final int REQ_LIVES_REFILLED       = 1003;
    private static final int REQ_RETURN_AFTER_ABSENCE = 1004;
    // Win-back chain — d3 / d7 / d14 / d30 fire if the user goes dark.
    private static final int REQ_WIN_BACK_D3          = 1005;
    private static final int REQ_WIN_BACK_D7          = 1006;
    private static final int REQ_WIN_BACK_D14         = 1007;
    private static final int REQ_WIN_BACK_D30         = 1008;
    private static final String PREF_NOTIFS_ENABLED   = "notifications_enabled";
    private static final String PREF_LAST_PLAYED      = "last_played_ts";
    private static final int NOTIF_CAP_PER_DAY        = 2;
    private static final int POST_NOTIFS_REQUEST_CODE = 9001;
"""

# The full bridge-method block (smart schedulers + winBack + settings toggle).
# Replaces a slimmer existing requestNotificationPermission block — we anchor on
# the existing method and insert AFTER it.
BRIDGE_BLOCK = """
        @JavascriptInterface
        public boolean hasNotificationPermission() {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true;
            return ContextCompat.checkSelfPermission(
                MainActivity.this,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED;
        }

        @JavascriptInterface
        public void scheduleDailyReminder(int hourOfDay, int minute) {
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.set(java.util.Calendar.HOUR_OF_DAY, hourOfDay);
            cal.set(java.util.Calendar.MINUTE, minute);
            cal.set(java.util.Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(java.util.Calendar.DAY_OF_YEAR, 1);
            }
            scheduleAlarm(
                REQ_DAILY_REMINDER, cal.getTimeInMillis(),
                "daily_reminder",
                getDailyReminderTitle(), getDailyReminderBody());
        }

        @JavascriptInterface
        public void scheduleStreakAtRisk(int streakDays) {
            cancelScheduledAlarm(REQ_STREAK_AT_RISK);
            if (streakDays < 3) return;
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.set(java.util.Calendar.HOUR_OF_DAY, 20);
            cal.set(java.util.Calendar.MINUTE, 30);
            cal.set(java.util.Calendar.SECOND, 0);
            if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
                cal.add(java.util.Calendar.DAY_OF_YEAR, 1);
            }
            String body = "Your " + streakDays + "-day streak ends in 4 hours — keep it alive! 🔥";
            scheduleAlarm(REQ_STREAK_AT_RISK, cal.getTimeInMillis(),
                "streak_at_risk", "Don't break your streak!", body);
        }

        @JavascriptInterface
        public void scheduleLivesRefilled(long whenMillis) {
            cancelScheduledAlarm(REQ_LIVES_REFILLED);
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            if (whenMillis <= System.currentTimeMillis()) return;
            scheduleAlarm(REQ_LIVES_REFILLED, whenMillis,
                "lives_refilled", "Your lives are back!", "Ready for another round? ❤️");
        }

        @JavascriptInterface
        public void scheduleWinBack(int dayOffset, String title, String body) {
            if (title == null || body == null) return;
            if (!getSharedPreferences("game", MODE_PRIVATE)
                    .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
            int req;
            switch (dayOffset) {
                case 3:  req = REQ_WIN_BACK_D3;  break;
                case 7:  req = REQ_WIN_BACK_D7;  break;
                case 14: req = REQ_WIN_BACK_D14; break;
                case 30: req = REQ_WIN_BACK_D30; break;
                default: return;
            }
            cancelScheduledAlarm(req);
            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.add(java.util.Calendar.DAY_OF_YEAR, dayOffset);
            cal.set(java.util.Calendar.HOUR_OF_DAY, 12);
            cal.set(java.util.Calendar.MINUTE, 0);
            cal.set(java.util.Calendar.SECOND, 0);
            scheduleAlarm(req, cal.getTimeInMillis(),
                "win_back_d" + dayOffset, title, body);
        }

        @JavascriptInterface
        public void cancelAllNotifications() {
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
            cancelScheduledAlarm(REQ_STREAK_AT_RISK);
            cancelScheduledAlarm(REQ_LIVES_REFILLED);
            cancelScheduledAlarm(REQ_RETURN_AFTER_ABSENCE);
            cancelScheduledAlarm(REQ_WIN_BACK_D3);
            cancelScheduledAlarm(REQ_WIN_BACK_D7);
            cancelScheduledAlarm(REQ_WIN_BACK_D14);
            cancelScheduledAlarm(REQ_WIN_BACK_D30);
        }

        @JavascriptInterface
        public void setNotificationsEnabled(boolean enabled) {
            getSharedPreferences("game", MODE_PRIVATE).edit()
                .putBoolean(PREF_NOTIFS_ENABLED, enabled).apply();
            if (!enabled) cancelAllNotifications();
        }

        @JavascriptInterface
        public boolean getNotificationsEnabled() {
            return getSharedPreferences("game", MODE_PRIVATE)
                .getBoolean(PREF_NOTIFS_ENABLED, true);
        }

        @JavascriptInterface
        public void recordLastPlayed() {
            getSharedPreferences("game", MODE_PRIVATE).edit()
                .putLong(PREF_LAST_PLAYED, System.currentTimeMillis()).apply();
            cancelScheduledAlarm(REQ_DAILY_REMINDER);
        }
"""

# Helpers (scheduleAlarm, cancelScheduledAlarm, getDailyReminderTitle/Body) live
# OUTSIDE the NativeBridge inner class. Inserted just before the closing brace
# of the file (find last `}`) or after dpToPx if present.
HELPERS_BLOCK_TMPL = """
    // ── Notifications helpers (NOTIFICATIONS_IMPL.md §3) ──────────────────────
    private void scheduleAlarm(int requestCode, long triggerAtMillis,
                                String type, String title, String body) {
        android.content.Intent intent = new android.content.Intent(this, NotificationReceiver.class);
        intent.putExtra("type", type);
        intent.putExtra("title", title);
        intent.putExtra("body", body);
        intent.putExtra("requestCode", requestCode);

        int flags = android.app.PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= android.app.PendingIntent.FLAG_IMMUTABLE;
        }
        android.app.PendingIntent pi = android.app.PendingIntent.getBroadcast(this, requestCode, intent, flags);

        android.app.AlarmManager am = (android.app.AlarmManager) getSystemService(ALARM_SERVICE);
        if (am == null) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(android.app.AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        } else {
            am.set(android.app.AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
        }
    }

    private void cancelScheduledAlarm(int requestCode) {
        android.content.Intent intent = new android.content.Intent(this, NotificationReceiver.class);
        int flags = android.app.PendingIntent.FLAG_NO_CREATE;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= android.app.PendingIntent.FLAG_IMMUTABLE;
        }
        android.app.PendingIntent pi = android.app.PendingIntent.getBroadcast(this, requestCode, intent, flags);
        if (pi != null) {
            android.app.AlarmManager am = (android.app.AlarmManager) getSystemService(ALARM_SERVICE);
            if (am != null) am.cancel(pi);
            pi.cancel();
        }
    }

    private String getDailyReminderTitle() { return __APP_TITLE__; }
    private String getDailyReminderBody()  { return __APP_BODY__; }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                            int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == POST_NOTIFS_REQUEST_CODE) {
            boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            webView.evaluateJavascript(
                "window.onNotificationPermissionResult && "
                + "window.onNotificationPermissionResult(" + granted + ");",
                null
            );
        }
    }
"""


def receiver_template(pkg: str) -> str:
    """The upgraded NotificationReceiver — loud/silent channel pick by hour,
    re-launches the app on tap, supports the (type,title,body,requestCode) payload
    the new bridge methods send."""
    return f"""package {pkg};

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import java.util.Calendar;

public class NotificationReceiver extends BroadcastReceiver {{
    private static final String CHANNEL_ID_LOUD   = "pegasus_games_default";
    private static final String CHANNEL_ID_SILENT = "pegasus_games_silent";

    @Override
    public void onReceive(Context ctx, Intent intent) {{
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) return;
        createChannels(ctx);

        String type  = intent.getStringExtra("type");
        String title = intent.getStringExtra("title");
        String body  = intent.getStringExtra("body");
        int reqCode  = intent.getIntExtra("requestCode", 0);
        if (title == null || body == null) return;

        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        String channelId = (hour >= 21 || hour < 9) ? CHANNEL_ID_SILENT : CHANNEL_ID_LOUD;

        Intent launch = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName());
        if (launch != null) {{
            launch.putExtra("notification_type", type);
            launch.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        }}
        int piFlags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) piFlags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent contentIntent = PendingIntent.getActivity(ctx, reqCode, launch, piFlags);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(ctx, channelId)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(channelId.equals(CHANNEL_ID_SILENT)
                ? NotificationCompat.PRIORITY_LOW : NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(contentIntent);

        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.notify(reqCode, builder.build());
    }}

    private void createChannels(Context ctx) {{
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        NotificationChannel loud = new NotificationChannel(CHANNEL_ID_LOUD, "Reminders",
            NotificationManager.IMPORTANCE_DEFAULT);
        loud.setDescription("Daily challenges, streak reminders, and game news");
        nm.createNotificationChannel(loud);
        NotificationChannel silent = new NotificationChannel(CHANNEL_ID_SILENT, "Evening reminders",
            NotificationManager.IMPORTANCE_LOW);
        silent.setDescription("Silent evening notifications");
        silent.setSound(null, null);
        silent.enableVibration(false);
        nm.createNotificationChannel(silent);
    }}
}}
"""


def port_one(app: str) -> dict:
    """Apply Part A changes to a single app's MainActivity + NotificationReceiver.
    Returns a dict summarizing what changed."""
    result = {"app": app, "changes": []}
    mp = java_path(app)
    src = mp.read_text()

    # 1. Constants block — inject just before the AppLovin MAX objects line if absent.
    if "REQ_DAILY_REMINDER" not in src:
        # Anchor: WEBVIEW_BG_COLOR line is consistently present right above bgcolor.
        m = re.search(r"(private static final int WEBVIEW_BG_COLOR[^\n]*\n)", src)
        assert m, f"could not find WEBVIEW_BG_COLOR anchor in {mp}"
        src = src[:m.end()] + CONSTANTS_BLOCK + src[m.end():]
        result["changes"].append("constants block")

    # 2. CROSS_PROMO_PACKAGES — rewrite to the per-app spec.
    promo_lines = ",\n        ".join(f'"{p}"' for p in PROMO[app])
    block = (
        "    // Cross-promo install verification — must match CROSS_PROMO list in game.html\n"
        "    // and the <queries> entries in AndroidManifest.xml. Targets are LIVE Play\n"
        "    // Store apps only. Pre-release siblings (UnblockPuzzle, PipeConnect) added\n"
        "    // here ONLY after they have Play links.\n"
        "    private static final Set<String> CROSS_PROMO_PACKAGES = new HashSet<>(Arrays.asList(\n"
        f"        {promo_lines}\n"
        "    ));"
    )
    if "CROSS_PROMO_PACKAGES" in src:
        # Replace existing list — supports both single-line and multi-line forms.
        new = re.sub(
            r"(?ms)//[^\n]*Cross-promo[^\n]*\n(?:\s*//[^\n]*\n)*\s*private static final Set<String> CROSS_PROMO_PACKAGES\s*=\s*new HashSet<>\(Arrays\.asList\([^)]*\)\);",
            block, src, count=1,
        )
        if new != src:
            result["changes"].append("CROSS_PROMO_PACKAGES rewritten")
            src = new
    else:
        # Add right after the constants block we just inserted (or before AppLovin).
        m = re.search(r"\n(\s*// AppLovin MAX objects)", src)
        if m:
            src = src[:m.start()] + "\n" + block + "\n" + src[m.start():]
            result["changes"].append("CROSS_PROMO_PACKAGES added")

    # 3. Bridge methods — inject right after the existing requestNotificationPermission
    #    (every target has at least this one). Skip if scheduleDailyReminder present.
    if "scheduleDailyReminder" not in src:
        # Find the end of the existing requestNotificationPermission method.
        # It's a brace-balanced search starting at "public void requestNotificationPermission".
        anchor = re.search(r"public void requestNotificationPermission\s*\(\s*\)\s*\{", src)
        assert anchor, f"could not find requestNotificationPermission in {mp}"
        # Walk forward to the matching close brace.
        depth = 1
        i = anchor.end()
        while i < len(src) and depth > 0:
            c = src[i]
            if c == "{": depth += 1
            elif c == "}": depth -= 1
            i += 1
        # i now points just past the closing brace of requestNotificationPermission.
        src = src[:i] + "\n" + BRIDGE_BLOCK + src[i:]
        result["changes"].append("smart-schedule bridge methods")

    # 4. Helpers + onRequestPermissionsResult — inject before the FINAL closing brace.
    if "scheduleAlarm(" not in src or "cancelScheduledAlarm(" not in src or "onRequestPermissionsResult" not in src:
        helpers = HELPERS_BLOCK_TMPL.replace("__APP_TITLE__", f'"{APP_TITLE[app]}"').replace(
            "__APP_BODY__", f'"{APP_DAILY_BODY[app]}"')
        # Insert before the LAST `}` in the file (closes the class).
        last_brace = src.rfind("}")
        assert last_brace > 0
        src = src[:last_brace] + helpers + "\n" + src[last_brace:]
        result["changes"].append("helpers + onRequestPermissionsResult")

    # 5. Add ContextCompat / ActivityCompat / Manifest imports if hasNotificationPermission needs them.
    needed = [
        ("import androidx.core.content.ContextCompat;", "ContextCompat."),
        ("import androidx.core.app.ActivityCompat;",    "ActivityCompat."),
        ("import android.Manifest;",                     "Manifest.permission.POST_NOTIFICATIONS"),
    ]
    for imp, marker in needed:
        if marker in src and imp not in src:
            # Insert after the existing first `import ` line block.
            m = re.search(r"(\nimport [^\n]+;)\n\n", src)
            if m:
                src = src[:m.end(1)] + "\n" + imp + src[m.end(1):]
                result["changes"].append(f"import: {imp.split()[1]}")

    # Persist.
    if src != mp.read_text():
        mp.write_text(src)

    # 6. Rewrite NotificationReceiver.java with the upgraded version.
    rp = receiver_path(app)
    desired = receiver_template(APP_PKG[app])
    if rp.read_text() != desired:
        rp.write_text(desired)
        result["changes"].append("NotificationReceiver rewritten")

    return result


def main():
    for app in ("Nonogram", "Puzzle2048", "UnblockPuzzle"):
        r = port_one(app)
        print(f"{app}: {', '.join(r['changes']) if r['changes'] else 'no changes (idempotent)'}")


if __name__ == "__main__":
    main()
