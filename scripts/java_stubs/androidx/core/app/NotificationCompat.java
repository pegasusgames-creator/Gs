package androidx.core.app;
public class NotificationCompat { public static final int PRIORITY_LOW=-1; public static final int PRIORITY_DEFAULT=0; public static final int PRIORITY_HIGH=1;
  public abstract static class Style {}
  public static class BigTextStyle extends Style { public BigTextStyle(){} public BigTextStyle bigText(CharSequence c){return this;} }
  public static class Builder { public Builder(android.content.Context c, String channel){} public Builder setSmallIcon(int i){return this;} public Builder setContentTitle(CharSequence c){return this;} public Builder setContentText(CharSequence c){return this;} public Builder setStyle(Style s){return this;} public Builder setPriority(int p){return this;} public Builder setAutoCancel(boolean b){return this;} public Builder setContentIntent(android.app.PendingIntent p){return this;} public Builder setColor(int c){return this;} public android.app.Notification build(){return null;} } }
