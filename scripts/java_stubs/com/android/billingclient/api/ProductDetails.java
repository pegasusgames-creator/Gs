package com.android.billingclient.api;
public final class ProductDetails { public String getProductId(){return "";} public String getProductType(){return "";} public String getTitle(){return "";} public String getName(){return "";} public String getDescription(){return "";}
  public OneTimePurchaseOfferDetails getOneTimePurchaseOfferDetails(){return null;} public java.util.List<SubscriptionOfferDetails> getSubscriptionOfferDetails(){return null;}
  public static final class OneTimePurchaseOfferDetails { public String getFormattedPrice(){return "";} public long getPriceAmountMicros(){return 0;} public String getPriceCurrencyCode(){return "";} }
  public static final class SubscriptionOfferDetails { public String getOfferToken(){return "";} public PricingPhases getPricingPhases(){return null;} }
  public static final class PricingPhases { public java.util.List<PricingPhase> getPricingPhaseList(){return null;} }
  public static final class PricingPhase { public String getFormattedPrice(){return "";} public long getPriceAmountMicros(){return 0;} public String getBillingPeriod(){return "";} public String getPriceCurrencyCode(){return "";} } }
