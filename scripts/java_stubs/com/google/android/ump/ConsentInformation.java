package com.google.android.ump;
public interface ConsentInformation { void requestConsentInfoUpdate(android.app.Activity a, ConsentRequestParameters p, OnConsentInfoUpdateSuccessListener s, OnConsentInfoUpdateFailureListener f); boolean canRequestAds(); int getConsentStatus(); boolean isConsentFormAvailable();
  interface OnConsentInfoUpdateSuccessListener { void onConsentInfoUpdateSuccess(); }
  interface OnConsentInfoUpdateFailureListener { void onConsentInfoUpdateFailure(FormError e); } }
