package com.pegasusgames.unblockpuzzle;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class NotificationHelper {

    static final String CHANNEL_ID = "daily_reminder";
    static final int    NOTIF_ID   = 1001;

    static void createChannel(Context ctx) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID, "Daily Reminder", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Daily challenge reminder");
            ctx.getSystemService(NotificationManager.class).createNotificationChannel(ch);
        }
    }

    /** Schedule a notification delayMinutes from now. */
    static void schedule(Context ctx, int delayMinutes) {
        Intent intent = new Intent(ctx, NotificationReceiver.class);
        intent.putExtra("notif_id", NOTIF_ID);
        PendingIntent pi = PendingIntent.getBroadcast(
            ctx, NOTIF_ID, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
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
        ((AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE)).cancel(pi);
    }
}
