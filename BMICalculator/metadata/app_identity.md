# BMI Calculator Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: health calculator and log - Google HEALTH_AND_FITNESS, Apple HEALTH_FITNESS
- **Layout archetype**: I (toolbox / direct tool) - opens straight on the calculator, no menu, three tabs: BMI · History · Goal
- **Mascot pattern**: M0 (no mascot; identity element = a dial gauge with the four WHO colour bands)
- **Voice**: V8 (direct minimal) - "Enter height and weight", neutral wording ("this value is categorised as..."); no coaching, no praise or blame about weight
- **Texture**: T8 (plain, minimal) - flat cards, one result block, tabular numerals
- **Mood string**: tool-clean

Pine-teal Daylight (`#EFF6F4`, accent `#0B6B63`) with a free deep-green Dark; Ocean free, Indigo / Plum / Sunset are Pro
accents (24-hour rewarded trial). Band colours (blue / green / amber / orange) are tokens in PALETTE and are never the only
signal: every band also has a text label. Distinct from AgeCalculator's caramel and HabitTracker's violet.

## What the app does (and the rules it states)
- Live BMI from metric (kg, cm) or imperial (lb, ft + in) input; the BMI is rounded half-up to one decimal, as displayed,
  and THEN banded, so the number and its category never disagree. WHO adult bands: <16 severe thinness, 16-16.99 moderate
  thinness, 17-18.49 mild thinness, 18.5-24.99 normal range, 25-29.99 pre-obese, 30-34.99 / 35-39.99 / >=40 obese class I / II / III.
- Gauge on a 15-40 scale with the 18.5 / 25 / 30 lines; healthy-weight range = weights giving BMI 18.5 to 24.9 at the height
  (min rounded up, max rounded down to 0.1 kg or lb) and the distance from it.
- Age under 18 (entered in the body-fat section): adult categories are hidden and replaced by a note.
- Body-fat estimate (optional, adults 18-99 with sex): Deurenberg et al. 1991, 1.20 x BMI + 0.23 x age - 10.8 x sex - 5.4
  (male 1, female 0); always labelled "Estimate", formula and caveats shown.
- History chart (BMI with the normal band, or weight with the goal line) + list with notes, one reading per day,
  edit note/date, delete with Undo; Goal: target weight, start weight, progress, BMI at the target, a neutral
  "talk to a health professional" note when the target is below BMI 18.5.
- `scripts/check_bmicalculator_math.py` runs the app's pure `BM` block under node against an independent exact-rational Python
  reference (band edges 18.5 / 25 / 30 / 35 / 40, healthy range, kg-lb-cm-ft-in conversions, Deurenberg, gauge, goal, number parsing).

## Health-apps declaration notes (docs/UTILITY_SHELL.md)
- No medical claims, no diagnosis, no dosing advice; "not a diagnosis / not medical advice" in onboarding, on the BMI tab, in
  Settings > About these numbers and in the listing; "BMI is not valid for children, pregnancy or athletes".
- Play Console > App content > **Health apps declaration** is required (health-adjacent); Data Safety stays "no health data collected"
  because readings stay on the device (WebView storage + Android Auto Backup only). Not a Kids app, audience 18+.
- Cites the WHO adult BMI classification; no "ideal weight", "obese-shaming" or weight-loss claims; goals are the user's own choice.

## Pro (pro_lifetime, $5.99) and Remove ads ($2.99)
Pro: unlimited history (free: 30 readings), CSV export, extra accents, no ads. Both purchases non-consumable.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] Not a symmetric centred column: result card, gauge, range card, list groups
- [x] Own SVG icon set and illustrations (dial, trend, target)
- [x] Mixed case body copy; caps only on section labels
- [x] No currency, no levels, no streaks, no guilt notifications; reminder is opt-in and neutral
- [x] Opening line is the tool itself, not "Welcome to BMI Calculator"
