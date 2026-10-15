package com.pegasusgames.habittracker;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import java.util.Calendar;

public class NotificationReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID_LOUD   = "pegasus_games_default";
    private static final String CHANNEL_ID_SILENT = "pegasus_games_silent";

    @Override
    public void onReceive(Context ctx, Intent intent) {
        String action = intent.getAction();
        // Alarms are dropped on reboot / app update — re-arm the stored user reminders.
        if (Intent.ACTION_BOOT_COMPLETED.equals(action)
                || Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)) {
            NotificationHelper.rearmAll(ctx);
            return;
        }
        createChannels(ctx);

        String type  = intent.getStringExtra("type");
        String title = intent.getStringExtra("title");
        String body  = intent.getStringExtra("body");
        int reqCode  = intent.getIntExtra("requestCode", 0);
        int slot     = intent.getIntExtra("slot", -1);
        if (title == null || body == null) return;

        // A reminder the user set fires at the time they chose (normal channel);
        // app-initiated nudges go quiet in the evening.
        String channelId;
        if (slot >= 0) {
            channelId = NotificationHelper.CHANNEL_REMINDERS;
        } else {
            int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
            channelId = (hour >= 21 || hour < 9) ? CHANNEL_ID_SILENT : CHANNEL_ID_LOUD;
        }

        Intent launch = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName());
        if (launch != null) {
            launch.putExtra("notification_type", type);
            launch.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        }
        int piFlags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) piFlags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent contentIntent = PendingIntent.getActivity(ctx, reqCode, launch, piFlags);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(ctx, channelId)
            .setSmallIcon(R.drawable.ic_stat_check)
            .setColor(0xFF6A4FD6)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(channelId.equals(CHANNEL_ID_SILENT)
                ? NotificationCompat.PRIORITY_LOW : NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(contentIntent);

        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.notify(reqCode, builder.build());

        // Repeating user reminder: schedule its next occurrence.
        if (slot >= 0) NotificationHelper.armReminder(ctx, slot);
    }

    private void createChannels(Context ctx) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        NotificationChannel loud = new NotificationChannel(CHANNEL_ID_LOUD, "Reminders",
            NotificationManager.IMPORTANCE_DEFAULT);
        loud.setDescription("Daily check-in reminders");
        nm.createNotificationChannel(loud);
        NotificationChannel silent = new NotificationChannel(CHANNEL_ID_SILENT, "Evening reminders",
            NotificationManager.IMPORTANCE_LOW);
        silent.setDescription("Silent evening notifications");
        silent.setSound(null, null);
        silent.enableVibration(false);
        nm.createNotificationChannel(silent);
        NotificationHelper.createChannel(ctx);
    }
}
