package com.google.android.ump;
public class ConsentDebugSettings { public @interface DebugGeography { int DEBUG_GEOGRAPHY_DISABLED=0; int DEBUG_GEOGRAPHY_EEA=1; int DEBUG_GEOGRAPHY_NOT_EEA=2; int DEBUG_GEOGRAPHY_REGULATED_US_STATE=3; int DEBUG_GEOGRAPHY_OTHER=4; }
  public static class Builder { public Builder(android.content.Context c){} public Builder setDebugGeography(int g){return this;} public Builder addTestDeviceHashedId(String id){return this;} public ConsentDebugSettings build(){return new ConsentDebugSettings();} } }
