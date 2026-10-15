package com.pegasusgames.habittracker;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import org.json.JSONObject;

import java.util.Calendar;

/**
 * Notification channel + alarm helpers.
 *
 * User reminders (utility shell): game.html calls
 * {@code Android.scheduleReminder(slot, hour, minute, daysMask, title, body)}.
 * The spec is persisted in SharedPreferences "reminders" so the alarm can be
 * re-armed for its next occurrence every time it fires, after a reboot and
 * after an app update (NotificationReceiver). Alarms are inexact
 * (setAndAllowWhileIdle) on purpose — exact alarms need SCHEDULE_EXACT_ALARM,
 * which Play restricts to alarm-clock / calendar apps.
 */
public class NotificationHelper {

    static final String CHANNEL_ID = "daily_reminder";
    static final String CHANNEL_REMINDERS = "user_reminders";
    static final int    NOTIF_ID   = 1001;
    static final int    MAX_SLOT   = 63;
    static final int    SLOT_BASE  = 2000;   // PendingIntent request code = SLOT_BASE + slot
    private static final String PREFS = "reminders";

    static void createChannel(Context ctx) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = ctx.getSystemService(NotificationManager.class);
            if (nm == null) return;
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID, "Daily Reminder", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Daily check-in reminder");
            nm.createNotificationChannel(ch);
            NotificationChannel r = new NotificationChannel(
                CHANNEL_REMINDERS, "Reminders you set", NotificationManager.IMPORTANCE_DEFAULT);
            r.setDescription("Reminders at the times you chose");
            nm.createNotificationChannel(r);
        }
    }

    /** Schedule a notification delayMinutes from now (legacy one-shot bridge). */
    static void schedule(Context ctx, int delayMinutes) {
        Intent intent = new Intent(ctx, NotificationReceiver.class);
        intent.putExtra("notif_id", NOTIF_ID);
        PendingIntent pi = PendingIntent.getBroadcast(
            ctx, NOTIF_ID, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        long at = System.currentTimeMillis() + (long) delayMinutes * 60_000L;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pi);
        } else {
            am.set(AlarmManager.RTC_WAKEUP, at, pi);
        }
    }

    static void cancel(Context ctx) {
        Intent intent = new Intent(ctx, NotificationReceiver.class);
        PendingIntent pi = PendingIntent.getBroadcast(
            ctx, NOTIF_ID, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(pi);
    }

    // ── User reminders ───────────────────────────────────────────────────────

    private static SharedPreferences prefs(Context ctx) {
        return ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static void saveReminder(Context ctx, int slot, int hour, int minute, int daysMask,
                             String title, String body) {
        try {
            JSONObject o = new JSONObject();
            o.put("h", Math.max(0, Math.min(23, hour)));
            o.put("m", Math.max(0, Math.min(59, minute)));
            o.put("d", daysMask & 0x7f);
            o.put("t", title);
            o.put("b", body);
            prefs(ctx).edit().putString("r" + slot, o.toString()).apply();
        } catch (Exception ignored) {}
    }

    static void removeReminder(Context ctx, int slot) {
        prefs(ctx).edit().remove("r" + slot).apply();
        cancelReminderAlarm(ctx, slot);
    }

    static void removeAllReminders(Context ctx) {
        for (int s = 0; s <= MAX_SLOT; s++) cancelReminderAlarm(ctx, s);
        prefs(ctx).edit().clear().apply();
    }

    /** Re-arm every stored reminder (boot, app update, app launch). */
    static void rearmAll(Context ctx) {
        for (int s = 0; s <= MAX_SLOT; s++) {
            if (prefs(ctx).contains("r" + s)) armReminder(ctx, s);
        }
    }

    /** Set the alarm for the next occurrence of the stored reminder in slot. */
    static void armReminder(Context ctx, int slot) {
        String raw = prefs(ctx).getString("r" + slot, null);
        if (raw == null) return;
        try {
            JSONObject o = new JSONObject(raw);
            long at = nextTrigger(o.getInt("h"), o.getInt("m"), o.getInt("d"),
                                  System.currentTimeMillis());
            Intent intent = new Intent(ctx, NotificationReceiver.class);
            intent.putExtra("type", "user_reminder");
            intent.putExtra("slot", slot);
            intent.putExtra("title", o.getString("t"));
            intent.putExtra("body", o.getString("b"));
            intent.putExtra("requestCode", SLOT_BASE + slot);
            PendingIntent pi = PendingIntent.getBroadcast(ctx, SLOT_BASE + slot, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
            if (am == null) return;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pi);
            } else {
                am.set(AlarmManager.RTC_WAKEUP, at, pi);
            }
        } catch (Exception ignored) {}
    }

    static void cancelReminderAlarm(Context ctx, int slot) {
        Intent intent = new Intent(ctx, NotificationReceiver.class);
        PendingIntent pi = PendingIntent.getBroadcast(ctx, SLOT_BASE + slot, intent,
            PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE);
        if (pi == null) return;
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(pi);
        pi.cancel();
    }

    /**
     * Next time strictly after {@code now} at hour:minute on a day enabled in
     * daysMask (bit 0 = Sunday … bit 6 = Saturday; 0 means every day).
     */
    static long nextTrigger(int hour, int minute, int daysMask, long now) {
        int mask = (daysMask & 0x7f) == 0 ? 0x7f : (daysMask & 0x7f);
        Calendar c = Calendar.getInstance();
        c.setTimeInMillis(now);
        c.set(Calendar.HOUR_OF_DAY, hour);
        c.set(Calendar.MINUTE, minute);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        for (int i = 0; i < 8; i++) {
            int dow = c.get(Calendar.DAY_OF_WEEK) - 1;   // 0 = Sunday
            if (c.getTimeInMillis() > now + 1000L && (mask & (1 << dow)) != 0) return c.getTimeInMillis();
            c.add(Calendar.DAY_OF_YEAR, 1);
        }
        return c.getTimeInMillis();
    }
}
