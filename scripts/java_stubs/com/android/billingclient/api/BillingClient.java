package com.android.billingclient.api;
public abstract class BillingClient {
  public @interface BillingResponseCode { int OK=0; int USER_CANCELED=1; int SERVICE_UNAVAILABLE=2; int BILLING_UNAVAILABLE=3; int ITEM_UNAVAILABLE=4; int DEVELOPER_ERROR=5; int ERROR=6; int ITEM_ALREADY_OWNED=7; int ITEM_NOT_OWNED=8; int SERVICE_DISCONNECTED=-1; int FEATURE_NOT_SUPPORTED=-2; int NETWORK_ERROR=12; }
  public @interface ProductType { String INAPP="inapp"; String SUBS="subs"; }
  public static Builder newBuilder(android.content.Context c){return new Builder();}
  public static final class Builder { public Builder setListener(PurchasesUpdatedListener l){return this;} public Builder enablePendingPurchases(PendingPurchasesParams p){return this;} public Builder enableAutoServiceReconnection(){return this;} public BillingClient build(){return null;} }
  public abstract void startConnection(BillingClientStateListener l); public abstract void endConnection(); public abstract boolean isReady();
  public abstract void queryProductDetailsAsync(QueryProductDetailsParams p, ProductDetailsResponseListener l);
  public abstract BillingResult launchBillingFlow(android.app.Activity a, BillingFlowParams p);
  public abstract void consumeAsync(ConsumeParams p, ConsumeResponseListener l);
  public abstract void acknowledgePurchase(AcknowledgePurchaseParams p, AcknowledgePurchaseResponseListener l);
  public abstract void queryPurchasesAsync(QueryPurchasesParams p, PurchasesResponseListener l); }
