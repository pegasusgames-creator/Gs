package com.google.android.gms.ads;
public class RequestConfiguration { public static final String MAX_AD_CONTENT_RATING_G="G"; public static final String MAX_AD_CONTENT_RATING_PG="PG"; public static final String MAX_AD_CONTENT_RATING_T="T"; public static final String MAX_AD_CONTENT_RATING_MA="MA";
  public Builder toBuilder(){return new Builder();}
  public static class Builder { public Builder(){} public Builder setMaxAdContentRating(String r){return this;} public Builder setTestDeviceIds(java.util.List<String> ids){return this;} public Builder setTagForChildDirectedTreatment(int t){return this;} public Builder setTagForUnderAgeOfConsent(int t){return this;} public RequestConfiguration build(){return new RequestConfiguration();} } }
