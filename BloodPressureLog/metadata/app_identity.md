# BloodPressureLog Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: health log - Google HEALTH_AND_FITNESS, Apple HEALTH_FITNESS
- **Layout archetype**: I (toolbox / direct tool) - opens on the entry form, no menu, three tabs: Log · History · Trends
- **Mascot pattern**: M0 (no mascot; identity element = a four-colour category dial with a pulse line)
- **Voice**: V5 (calm / zen) - neutral wording ("this reading falls in the Stage 1 category of the 2017 ACC/AHA guideline"), no praise or alarm; a calm "seek medical help" note at 180/120 or higher
- **Texture**: T2 (soft cards, clinical-soft light)
- **Mood string**: clinical-soft

Cool clinical blue Daylight (`#F1F6FA`, accent navy `#1F4E8C`) with a free dark theme; Plum free, Forest / Ember / Rose are Pro accents
(24-hour rewarded trial). Category colours (green / amber / orange / red / deep crimson) are tokens and never the only signal: every
reading also carries the category name. Distinct from BMICalculator's pine teal and HabitTracker's violet.

## What the app does (and the rules it states)
- Log systolic, diastolic, optional pulse, date-time, arm, position, tags and a note. Validation: systolic 50-300 and above diastolic
  30-200, pulse 20-250.
- Categories: 2017 ACC/AHA adult guideline - Normal (<120 and <80), Elevated (120-129 and <80), Stage 1 (130-139 or 80-89), Stage 2
  (>=140 or >=90), Hypertensive crisis (>180 and/or >120); the higher category wins. A calm "seek medical help" note appears at
  180/120 or higher (the brief's threshold). Wording is neutral and always followed by "not a diagnosis".
- Trends 7/30/90 days: chart with dashed 120/80 lines, averages (half-up whole mmHg), pulse average, morning (04:00-11:59) vs evening
  (17:00-23:59), readings by category, doctor summary text (shareable). CSV export (Pro) neutralises formula-looking notes.
- Reminders (opt-in, asked in context): daily morning / evening measurement and medication time (slots 1-3, `Reminders.set`), dated
  re-check and appointment reminders (slots 4-5, `Reminders.enableAt`).
- Local-only data, backup/restore, Pro (`pro_lifetime`): unlimited history (free 60), CSV, extra accents, no ads.
- `scripts/check_bloodpressurelog_categories.py` runs the app's pure `BP` block under node over a 56k-pair grid against a Python reference.
