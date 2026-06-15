# Mediation setup — Afterimage

AdMob is the primary ad source; these adapters let AdMob mediate five extra
demand networks. **Do this in the AdMob dashboard** — the APK ships the adapter
code, but each network's credentials are entered server-side, never hard-coded.

## Ad units (this app)

| Format       | AdMob ad unit ID |
|--------------|------------------|
| App ID       | `ca-app-pub-3940256099942544~3347511713` |
| Banner       | `ca-app-pub-3940256099942544/6300978111` |
| Interstitial | `ca-app-pub-3940256099942544/1033173712` |
| Rewarded     | `ca-app-pub-3940256099942544/5224354917` |

## Adapters bundled (Gradle)

| Network              | Adapter artifact                              |
|----------------------|-----------------------------------------------|
| Meta Audience Network| `com.google.ads.mediation:facebook:6.21.0.3`  |
| Unity Ads            | `com.google.ads.mediation:unity:4.18.0.0`     |
| Mintegral            | `com.google.ads.mediation:mintegral:17.1.61.0`|
| Pangle               | `com.google.ads.mediation:pangle:8.0.0.5.0`   |
| InMobi               | `com.google.ads.mediation:inmobi:11.3.0.0`    |

Mintegral + Pangle resolve from custom Maven repos added to `settings.gradle`.

## Dashboard wiring (one mediation group per format)

For EACH ad unit above, create a mediation group in AdMob
(Mediation → Create mediation group), attach the ad unit, then add each network
as a line item. Map them like so:

| Format       | Mediation group name      | Networks to attach                         |
|--------------|---------------------------|--------------------------------------------|
| Banner       | `Afterimage-banner-mediation`       | Meta, Unity, Mintegral, Pangle, InMobi |
| Interstitial | `Afterimage-interstitial-mediation` | Meta, Unity, Mintegral, Pangle, InMobi |
| Rewarded     | `Afterimage-rewarded-mediation`     | Meta, Unity, Mintegral, Pangle, InMobi |

## Per-network credentials — fill in the dashboard (do NOT hard-code)

Create each app/placement in the network's own console, then paste the IDs into
the matching AdMob line item. Nothing below ships in the APK.

- Meta Audience Network — TODO: `<META_PLACEMENT_ID>` (per format) from
  developers.facebook.com → Audience Network.
- Unity Ads — TODO: `<UNITY_GAME_ID>` + `<UNITY_PLACEMENT_ID>` from the Unity
  Ads dashboard.
- Mintegral — TODO: `<MINTEGRAL_APP_ID>`, `<MINTEGRAL_APP_KEY>`,
  `<MINTEGRAL_UNIT_ID>` from the Mintegral console.
- Pangle — TODO: `<PANGLE_APP_ID>`, `<PANGLE_SLOT_ID>` from the Pangle console.
- InMobi — TODO: `<INMOBI_ACCOUNT_ID>`, `<INMOBI_PLACEMENT_ID>` from the InMobi
  console.

## Notes

- No AndroidManifest changes are required: these GMA adapters merge their own
  manifest entries, and all credentials are dashboard-side.
- Enable each network in the AdMob mediation group only after its line item has
  real credentials, or it will no-fill.
- Test with the AdMob mediation test suite before going live.
