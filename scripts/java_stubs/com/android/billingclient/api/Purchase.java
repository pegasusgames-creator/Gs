package com.android.billingclient.api;
public class Purchase { public int getPurchaseState(){return 0;} public java.util.List<String> getProducts(){return null;} public String getPurchaseToken(){return "";} public boolean isAcknowledged(){return false;} public String getOriginalJson(){return "";} public String getSignature(){return "";} public String getOrderId(){return "";}
  public @interface PurchaseState { int UNSPECIFIED_STATE=0; int PURCHASED=1; int PENDING=2; } }
