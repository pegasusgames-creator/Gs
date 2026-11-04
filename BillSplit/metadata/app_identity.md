# Bill Split Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: calculator (money, multi-person) - Google TOOLS, Apple UTILITIES
- **Layout archetype**: I (toolbox / direct tool) - opens straight on the splitter, three tabs: Split · Groups · History
- **Mascot pattern**: M0 (no mascot - identity element = a receipt cut down a dashed line)
- **Voice**: V5 (calm) - "Who pays what", "Adds up exactly"; no coaching
- **Texture**: T2 (soft cards) - rounded white cards, one deep-green hero block, tabular numerals
- **Mood string**: tool-clean

Mint-sage Daylight (`#F0F6F1`, deep green accent `#17714A`) with a free green-black Dark; Ocean free, Plum / Amber / Rose are Pro accents
(24-hour rewarded trial). Figtree face. Distinct from TipCalculator (one bill's tip) in purpose (multi-person itemised split), layout,
palette and icon.

## What the app does (and the rules it states)
- Items with integer minor-unit prices, assigned to one or more people; shared items split evenly or by integer custom shares (1-99).
- Tax and tip as a percentage (up to 3 decimals, rounded half-up to a cent) or a fixed amount; shared in proportion to each
  person's items or evenly; tip base = items or items + tax.
- Rounding: items, tax and tip are each divided exactly (rational arithmetic) and rounded with the largest-remainder method;
  leftover cents go to the largest fractions, ties to the person listed first. Per-person totals add up to the bill exactly.
- Saved groups (free 3), bill history (free 10), currency picker (formatting only; changing between currencies with a different
  minor unit rescales the numbers and offers Undo), plain-text share summary via Android.shareText, CSV export (Pro).
- `scripts/check_billsplit_math.py` runs the app's pure maths block under node against an independent Python Decimal/Fraction
  reference (4,000+ randomized and edge cases, parser edge cases) and blocks on any mismatch or any total that does not add up.

## Pro (pro_lifetime, $5.99) and Remove ads ($2.99)
Pro: unlimited saved groups and history, CSV export, extra accents, no ads. Both purchases non-consumable.
