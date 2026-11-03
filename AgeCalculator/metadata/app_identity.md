# Age Calculator Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: calculator (dates) — Google TOOLS, Apple UTILITIES
- **Layout archetype**: I (toolbox / direct tool) — opens straight on the calculator, no menu, three tabs: Age · Difference · People
- **Mascot pattern**: M0 (no mascot — the numbers carry the personality; identity element = the calendar page with a candle flame)
- **Voice**: V8 (direct minimal) — "Pick a date of birth", "Today is the birthday!"; no coaching, no guilt
- **Texture**: T8 (plain, minimal) — flat cards, one hero block, tabular numerals
- **Mood string**: tool-clean

Caramel-cream Daylight (`#FBF5EE`, caramel accent `#A8470F`) with a free warm-brown Dark; Ocean free, Forest / Plum / Rose
are Pro accents (24-hour rewarded trial). Deliberately far from HabitTracker's lavender-violet ring look and from the
portfolio's blue/green calculator family.

## What the app does (and the rules it states)
- Exact age in years / months / days plus total months, weeks, days and hours, born-on weekday, next birthday with
  weekday and countdown, Western + Chinese zodiac, milestones (1,000 / 5,000 / 10,000 / 15,000 / 20,000 / 25,000 /
  30,000 days, 1,000 weeks, 1 / 1.5 / 2 / 2.5 / 3 billion seconds, half-birthdays), date difference with weekday count,
  saved people with an optional weekly "who is coming up" reminder, shareable age-card text.
- Month maths: whole months are added to the start date with the day clamped to the month end (Jan 31 + 1 month = Feb 28/29),
  then the remaining days. A Feb 29 birthday is counted on Feb 28 in common years. Day / second milestones count from
  midnight at the start of the birth date. All dates are local calendar dates; supported range 1583-9999.
- `scripts/check_agecalculator_dates.py` runs the app's pure maths block under node against an independent Python
  reference (leap years, month-end borrows, century rules, invalid input, Chinese New Year table vs ICU).

## Pro (pro_lifetime, $5.99) and Remove ads ($2.99)
Pro: unlimited saved people (free: 3), custom milestones, extra accents, no ads. Both purchases non-consumable.

## Anti-pattern audit (APP_ARCHETYPES.md §5)
- [x] Not a symmetric centred column: hero block, tile grid, list groups
- [x] Own SVG icon set and illustrations (calendar, flag, gift, swap)
- [x] Mixed case body copy; caps only on section labels
- [x] No currency, no levels, no streaks, no guilt notifications
- [x] Opening line is the tool itself, not "Welcome to Age Calculator"
