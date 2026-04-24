# Notifications Implementation Reference

Reference code for local push notifications per `QUALITY_PLAYBOOK.md` §11.
Apply to all GAMES in the portfolio; do NOT apply to KIDS apps (§11.8) or
most TOOLS apps (§11.7 — exception for habit/tracker apps).

This is a **reference** — drop the pieces into each app's `MainActivity.java`
and `game.html` with per-app palette colors (notification glow, pre-prompt
overlay) adjusted to match the app's theme. Core logic is identical across
all apps.

All notifications are **local** via `AlarmManager`. No FCM, no server. See
§11.6 for why.

---

## Java — `MainActivity.java` additions

### 1. Constants and imports

Add to the imports block at the top of `MainActivity.java`:

```java
// Notifications
import android.Manifest;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.SharedPreferences;
import android.os.Build;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.util.Calendar;
```

Add to the class-level constants block:

```java
// Notification scheduling
private static final int REQ_DAILY_REMINDER       = 1001;
private static final int REQ_STREAK_AT_RISK       = 1002;
private static final int REQ_LIVES_REFILLED       = 1003;
private static final int REQ_RETURN_AFTER_ABSENCE = 1004;
private static final String PREF_NOTIFS_ENABLED   = "notifications_enabled";
private static final String PREF_LAST_PLAYED      = "last_played_ts";
private static final int POST_NOTIFS_REQUEST_CODE = 9001;
```

### 2. JS bridge methods (add to the JavaScriptInterface)

Inside `class NativeBridge` (or whatever it's named in your wrapper):

```java
@JavascriptInterface
public boolean hasNotificationPermission() {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true;
    return ContextCompat.checkSelfPermission(
        MainActivity.this,
        Manifest.permission.POST_NOTIFICATIONS
    ) == PackageManager.PERMISSION_GRANTED;
}

@JavascriptInterface
public void requestNotificationPermission() {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return;
    runOnUiThread(() -> {
        ActivityCompat.requestPermissions(
            MainActivity.this,
            new String[]{ Manifest.permission.POST_NOTIFICATIONS },
            POST_NOTIFS_REQUEST_CODE
        );
    });
}

@JavascriptInterface
public void scheduleDailyReminder(int hourOfDay, int minute) {
    cancelNotification(REQ_DAILY_REMINDER);
    if (!getSharedPreferences("game", MODE_PRIVATE)
            .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

    Calendar cal = Calendar.getInstance();
    cal.set(Calendar.HOUR_OF_DAY, hourOfDay);
    cal.set(Calendar.MINUTE, minute);
    cal.set(Calendar.SECOND, 0);
    if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
        cal.add(Calendar.DAY_OF_YEAR, 1);
    }

    scheduleAlarm(
        REQ_DAILY_REMINDER,
        cal.getTimeInMillis(),
        "daily_reminder",
        getDailyReminderTitle(),
        getDailyReminderBody()
    );
}

@JavascriptInterface
public void scheduleStreakAtRisk(int streakDays) {
    cancelNotification(REQ_STREAK_AT_RISK);
    if (streakDays < 3) return;  // §11.2: only for streaks >= 3
    if (!getSharedPreferences("game", MODE_PRIVATE)
            .getBoolean(PREF_NOTIFS_ENABLED, true)) return;

    Calendar cal = Calendar.getInstance();
    cal.set(Calendar.HOUR_OF_DAY, 20);  // 20:00 local
    cal.set(Calendar.MINUTE, 30);
    cal.set(Calendar.SECOND, 0);
    // If already past 20:30, schedule for tomorrow
    if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
        cal.add(Calendar.DAY_OF_YEAR, 1);
    }

    String body = "Your " + streakDays + "-day streak ends in 4 hours — keep it alive! 🔥";
    scheduleAlarm(
        REQ_STREAK_AT_RISK,
        cal.getTimeInMillis(),
        "streak_at_risk",
        "Don't break your streak!",
        body
    );
}

@JavascriptInterface
public void scheduleLivesRefilled(long whenMillis) {
    cancelNotification(REQ_LIVES_REFILLED);
    if (!getSharedPreferences("game", MODE_PRIVATE)
            .getBoolean(PREF_NOTIFS_ENABLED, true)) return;
    if (whenMillis <= System.currentTimeMillis()) return;

    scheduleAlarm(
        REQ_LIVES_REFILLED,
        whenMillis,
        "lives_refilled",
        "Your lives are back!",
        "Ready for another round? ❤️"
    );
}

@JavascriptInterface
public void cancelAllNotifications() {
    cancelNotification(REQ_DAILY_REMINDER);
    cancelNotification(REQ_STREAK_AT_RISK);
    cancelNotification(REQ_LIVES_REFILLED);
    cancelNotification(REQ_RETURN_AFTER_ABSENCE);
}

@JavascriptInterface
public void setNotificationsEnabled(boolean enabled) {
    getSharedPreferences("game", MODE_PRIVATE)
        .edit()
        .putBoolean(PREF_NOTIFS_ENABLED, enabled)
        .apply();
    if (!enabled) {
        cancelAllNotifications();
    }
}

@JavascriptInterface
public boolean getNotificationsEnabled() {
    return getSharedPreferences("game", MODE_PRIVATE)
        .getBoolean(PREF_NOTIFS_ENABLED, true);
}

@JavascriptInterface
public void recordLastPlayed() {
    getSharedPreferences("game", MODE_PRIVATE)
        .edit()
        .putLong(PREF_LAST_PLAYED, System.currentTimeMillis())
        .apply();
    // If played today, skip today's daily reminder
    cancelNotification(REQ_DAILY_REMINDER);
}
```

### 3. Private helper methods (add to MainActivity, not inside the bridge class)

```java
private void scheduleAlarm(int requestCode, long triggerAtMillis,
                            String type, String title, String body) {
    Intent intent = new Intent(this, NotificationReceiver.class);
    intent.putExtra("type", type);
    intent.putExtra("title", title);
    intent.putExtra("body", body);
    intent.putExtra("requestCode", requestCode);

    int flags = PendingIntent.FLAG_UPDATE_CURRENT;
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        flags |= PendingIntent.FLAG_IMMUTABLE;
    }

    PendingIntent pi = PendingIntent.getBroadcast(
        this, requestCode, intent, flags
    );

    AlarmManager am = (AlarmManager) getSystemService(ALARM_SERVICE);
    if (am == null) return;

    // Use setAndAllowWhileIdle for reliability across Doze mode
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
    } else {
        am.set(AlarmManager.RTC_WAKEUP, triggerAtMillis, pi);
    }
}

private void cancelNotification(int requestCode) {
    Intent intent = new Intent(this, NotificationReceiver.class);
    int flags = PendingIntent.FLAG_NO_CREATE;
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        flags |= PendingIntent.FLAG_IMMUTABLE;
    }
    PendingIntent pi = PendingIntent.getBroadcast(this, requestCode, intent, flags);
    if (pi != null) {
        AlarmManager am = (AlarmManager) getSystemService(ALARM_SERVICE);
        if (am != null) am.cancel(pi);
        pi.cancel();
    }
}

private String getDailyReminderTitle() {
    // Adjust per-app (e.g. "Ball Sort Puzzle", "Water Sort Puzzle")
    return getString(R.string.app_name);
}

private String getDailyReminderBody() {
    // Adjust per-app copy — keep vague, not instructional
    return "Your daily challenge is ready!";
}
```

### 4. Permission result handler

Override in `MainActivity`:

```java
@Override
public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                        int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == POST_NOTIFS_REQUEST_CODE) {
        boolean granted = grantResults.length > 0
            && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        // Callback into JS so game can react
        webView.evaluateJavascript(
            "window.onNotificationPermissionResult && "
            + "window.onNotificationPermissionResult(" + granted + ");",
            null
        );
    }
}
```

### 5. AndroidManifest.xml

Add (if not present from wrapper):

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<application>
    ...
    <receiver android:name=".NotificationReceiver"
              android:exported="false">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
        </intent-filter>
    </receiver>
</application>
```

### 6. NotificationReceiver.java

If your wrapper doesn't already have this or needs updating:

```java
package com.pegasusgames.<APP_NAME>;  // per-app package

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.net.Uri;
import androidx.core.app.NotificationCompat;
import java.util.Calendar;

public class NotificationReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID_LOUD   = "pegasus_games_default";
    private static final String CHANNEL_ID_SILENT = "pegasus_games_silent";

    @Override
    public void onReceive(Context ctx, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // Reschedule any daily reminders after boot — optional, simpler
            // to just re-schedule on next app open
            return;
        }

        createChannels(ctx);

        String type  = intent.getStringExtra("type");
        String title = intent.getStringExtra("title");
        String body  = intent.getStringExtra("body");
        int reqCode  = intent.getIntExtra("requestCode", 0);

        if (title == null || body == null) return;

        // §11.3: notifications after 21:00 must be silent
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        String channelId = (hour >= 21 || hour < 9)
            ? CHANNEL_ID_SILENT : CHANNEL_ID_LOUD;

        // Re-launch app on tap
        Intent launch = ctx.getPackageManager()
            .getLaunchIntentForPackage(ctx.getPackageName());
        if (launch != null) {
            launch.putExtra("notification_type", type);
            launch.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP
                           | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        }
        int piFlags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            piFlags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent contentIntent = PendingIntent.getActivity(
            ctx, reqCode, launch, piFlags
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(ctx, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // replace with per-app ic_notification
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(channelId.equals(CHANNEL_ID_SILENT)
                ? NotificationCompat.PRIORITY_LOW
                : NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(contentIntent);

        NotificationManager nm = (NotificationManager)
            ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.notify(reqCode, builder.build());
    }

    private void createChannels(Context ctx) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = (NotificationManager)
            ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        NotificationChannel loud = new NotificationChannel(
            CHANNEL_ID_LOUD, "Reminders",
            NotificationManager.IMPORTANCE_DEFAULT
        );
        loud.setDescription("Daily challenges, streak reminders, and game news");
        nm.createNotificationChannel(loud);

        NotificationChannel silent = new NotificationChannel(
            CHANNEL_ID_SILENT, "Evening reminders",
            NotificationManager.IMPORTANCE_LOW
        );
        silent.setDescription("Silent evening notifications");
        silent.setSound(null, null);
        silent.enableVibration(false);
        nm.createNotificationChannel(silent);
    }
}
```

---

## JavaScript — `game.html` additions

### 1. Permission pre-prompt overlay HTML

Insert near the bottom of `<body>`, styled to match app theme:

```html
<div id="notifPrePrompt" class="modal-overlay" style="display:none;">
  <div class="modal-card">
    <div class="modal-icon">🔔</div>
    <h2>Stay on track</h2>
    <p>Want us to remind you about your daily challenge and streak? You can change this anytime in Settings.</p>
    <button class="btn btn-primary" onclick="Notifications.onEnable()">Enable Reminders</button>
    <button class="btn btn-secondary" onclick="Notifications.onMaybeLater()">Maybe Later</button>
  </div>
</div>
```

### 2. Notifications controller (JS)

Add to `<script>` block in `game.html`:

```javascript
const Notifications = (() => {
  const LS_PROMPT_SHOWN_AT  = 'notif_prompt_shown_at';
  const LS_PROMPT_DISMISSED = 'notif_prompt_dismissed_count';
  const PROMPT_COOLDOWN_MS  = 7 * 24 * 60 * 60 * 1000; // 7 days

  function shouldShowPrompt() {
    // §11.1: only after first level complete, and only once per 7 days,
    // and max 2 total times
    const lastShown = parseInt(localStorage.getItem(LS_PROMPT_SHOWN_AT) || '0', 10);
    const dismissedCount = parseInt(localStorage.getItem(LS_PROMPT_DISMISSED) || '0', 10);

    if (!NativeBridge || !NativeBridge.hasNotificationPermission) return false;
    if (NativeBridge.hasNotificationPermission()) return false;
    if (dismissedCount >= 2) return false;
    if (Date.now() - lastShown < PROMPT_COOLDOWN_MS) return false;
    return true;
  }

  function showPrompt() {
    if (!shouldShowPrompt()) return;
    localStorage.setItem(LS_PROMPT_SHOWN_AT, Date.now().toString());
    document.getElementById('notifPrePrompt').style.display = 'flex';
  }

  function onEnable() {
    document.getElementById('notifPrePrompt').style.display = 'none';
    NativeBridge.requestNotificationPermission();
    // onNotificationPermissionResult will be called by Java
  }

  function onMaybeLater() {
    document.getElementById('notifPrePrompt').style.display = 'none';
    const n = parseInt(localStorage.getItem(LS_PROMPT_DISMISSED) || '0', 10);
    localStorage.setItem(LS_PROMPT_DISMISSED, (n + 1).toString());
  }

  function scheduleAll() {
    if (!NativeBridge || !NativeBridge.hasNotificationPermission()) return;
    if (!NativeBridge.getNotificationsEnabled()) return;

    // Daily reminder: 19:00 local time
    NativeBridge.scheduleDailyReminder(19, 0);

    // Streak-at-risk
    const streak = State.streak || 0;
    NativeBridge.scheduleStreakAtRisk(streak);
  }

  function onAppOpen() {
    // §11.2: same-day skip for daily reminder, done Java-side via recordLastPlayed
    NativeBridge.recordLastPlayed();
    scheduleAll();
  }

  function onLevelComplete(levelIndex) {
    // §11.1: request permission after first-level bond
    if (levelIndex === 0) {
      setTimeout(showPrompt, 2000); // after the level complete celebration
    }
    // Re-schedule (streak may have changed)
    scheduleAll();
  }

  function onLivesDepleted(refillAtMs) {
    if (!NativeBridge || !NativeBridge.hasNotificationPermission()) return;
    if (!NativeBridge.getNotificationsEnabled()) return;
    NativeBridge.scheduleLivesRefilled(refillAtMs);
  }

  function setEnabled(enabled) {
    NativeBridge.setNotificationsEnabled(enabled);
    if (enabled) scheduleAll();
  }

  function isEnabled() {
    return NativeBridge.getNotificationsEnabled()
      && NativeBridge.hasNotificationPermission();
  }

  return {
    onAppOpen, onLevelComplete, onLivesDepleted,
    onEnable, onMaybeLater,
    setEnabled, isEnabled, showPrompt,
  };
})();

// Called by Java after permission result
window.onNotificationPermissionResult = function(granted) {
  if (granted) {
    Notifications.setEnabled(true);
  }
};
```

### 3. Integration points

Find the right lines in existing `game.html` and call Notifications methods:

- **App start** (the main init function, after `State` loaded):
  ```javascript
  Notifications.onAppOpen();
  ```

- **Level complete handler** (after showing the celebration overlay):
  ```javascript
  Notifications.onLevelComplete(State.currentLevel);
  ```

- **When lives hit 0** (after the "no lives" overlay shows):
  ```javascript
  const refillAt = Date.now() + LIFE_REGEN_MS;
  Notifications.onLivesDepleted(refillAt);
  ```

### 4. Settings toggle (Settings screen HTML)

Add this row to the existing Settings screen, styled consistently:

```html
<div class="settings-row">
  <div class="settings-label">
    <div class="settings-title">Daily Reminders</div>
    <div class="settings-subtitle">Streak alerts and daily challenge</div>
  </div>
  <label class="toggle-switch">
    <input type="checkbox" id="notifToggle"
           onchange="Notifications.setEnabled(this.checked)">
    <span class="toggle-slider"></span>
  </label>
</div>
```

And in the settings-screen open handler:

```javascript
document.getElementById('notifToggle').checked = Notifications.isEnabled();
```

---

## Per-app customization checklist

When applying this to a new app, adjust these values:

- Package name in `NotificationReceiver.java` (e.g., `com.pegasusgames.watersort`)
- `getDailyReminderBody()` — match the app's tone and content (e.g. "Your
  daily Nonogram puzzle is ready!")
- Pre-prompt overlay copy — app-specific framing
- Notification icon — `ic_notification` should be a monochrome version of
  the app's icon (Android requires this for the status bar — full-color
  icons render as white blobs on Android 5+)
- Pre-prompt overlay colors match app theme
- Settings toggle styling matches existing Settings screen

Do NOT change:

- Timing logic (19:00 daily, 20:30 streak-at-risk)
- 3-day streak minimum for streak-at-risk
- 2-dismissal maximum for pre-prompt
- 7-day cooldown between pre-prompt shows
- 21:00+ silent channel routing

These rules apply identically across all apps per §11.
