# Java signature stubs

Compile-time stand-ins for the Google SDK classes the app wrappers call
(AdMob, UMP, Play Billing 8, Play Games v2, Tasks, Firebase Analytics,
androidx core). Bodies are empty; only the public signatures matter.
`scripts/java_compile_check.py` compiles them, then every app's Java against
them plus the real Android framework (Robolectric android-all, API 35), so a
syntax or type error in a MainActivity is caught without the Android SDK.

When a wrapper starts calling a new SDK method, add its exact signature here
(copy it from the SDK reference) — a missing stub shows up as
"cannot find symbol" in the checker, never as a silent pass.
