# Blood Sugar Log Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: health log - Google HEALTH_AND_FITNESS, Apple HEALTH_FITNESS
- **Layout archetype**: I (toolbox / direct tool) - opens straight on the entry card, no menu, three tabs: Log · Insights · History
- **Mascot pattern**: M0 (no mascot; identity element = a drop with a target band and a trend line inside)
- **Voice**: V8 (direct minimal) - neutral wording ("below range", "above range"; never "hypo/hyper", no praise or blame about numbers)
- **Texture**: T2 (soft, flat cards) - one entry card, filled range chips, tabular numerals
- **Mood string**: tool-clean

Citrine / honey Daylight (`#FFF9E1`, accent `#7A5200`) with a free warm-dark Dark; Ocean free, Berry / Slate / Ember are Pro
accents (24-hour rewarded trial). Range colours (blue below / green in / orange above / deep blue and crimson for far
below / far above) are tokens in PALETTE and are never the only signal: every class also has a text label and its own
shape (down triangle = below, circle = in range, up triangle = above). Figtree type. Distinct from BloodPressureLog
(clinical blue and red, systolic/diastolic line chart), BMICalculator's pine-teal gauge and HabitTracker's violet.

## What the app does (and the rules it states)
- Log a reading in mg/dL or mmol/L with meal context (fasting / before / after / bedtime / other), optional date-time,
  carbs (0-500 g), tags and a note. 1 mmol/L = 18.0156 mg/dL; a reading is stored as whole mg/dL (mmol/L x 18.0156, rounded
  half up) and shown in mmol/L with one decimal (mg/dL / 18.0156, rounded half up), so a 1-decimal mmol/L value round-trips.
- Target ranges are set by the USER (neutral default 70-180 mg/dL, far-below 54, far-above 250, optional per meal context;
  "set the ranges your clinician gave you"); both ends of the range are inside it. The app never recommends a target.
- A reading beyond the user's own far-below / far-above limit shows a neutral "contact your care team or local emergency
  number" note; there is no dosing, insulin or diagnosis feature of any kind.
- Insights: time in range as the share of READINGS (stated: spot checks, not time), readings over time, day-pattern chart,
  averages by time of day (night/morning/midday/afternoon/evening) and by meal context.
- Estimated A1C (ADAG: eA1C = (average mg/dL + 46.7) / 28.7, one decimal) only with >= 20 readings on >= 10 different days in
  the last 90 days; always labelled "Estimate" with the formula and a not-a-lab-result caveat.
- Doctor summary (plain text, free) and CSV export (Pro). Testing reminders: weekly (day mask + time) or one-time at a date,
  slots 1-12, opt-in, permission asked in context. Data stays on the device.
- Free: 60 readings. Pro (`pro_lifetime`): unlimited history, CSV export, extra accents, no ads.
- `scripts/check_bloodsugarlog_math.py` runs the app's pure `GL` block under node against an independent exact-rational Python
  reference (conversion, classification, per-context ranges, time in range, averages, A1C and its eligibility rule, parsing).

## Health apps declaration (Play Console > App content)
Blood glucose logbook; user-set ranges; not a medical device; no diagnosis, treatment, dosing or insulin advice; estimate
labelled as an estimate; no health data leaves the device (Data Safety: no health data collected). Not for children.
