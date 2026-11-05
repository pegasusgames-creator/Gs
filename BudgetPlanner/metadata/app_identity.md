# Budget Planner Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: planner / money (envelope budgeting) - Google TOOLS, Apple UTILITIES
- **Layout archetype**: I (toolbox / direct tool) - opens straight on the month plan, four tabs: Plan · Bills · Goals · Months
- **Mascot pattern**: M0 (no mascot - identity element = an envelope with a coin)
- **Voice**: V8 (direct, minimal) - "Left to assign", "Over by $X"; no coaching or guilt
- **Texture**: T2 (soft cards) - rounded white cards, one deep-blue hero block, tabular numerals
- **Mood string**: tool-clean

Sky-blueprint Daylight (`#EEF3F8`, deep blue accent `#1A5C9E`) with a free navy Dark; Teal free, Plum / Amber / Rose are Pro
accents (24-hour rewarded trial). Manrope face. Distinct from ExpenseTracker (quick logging of what you spent) in purpose
(planning monthly envelopes before spending), layout, palette and icon; distinct from BillSplit (green, one bill split between people).

## What the app does (and the rules it states)
- Per month: income lines, a planned amount per envelope, spending, and transfers between envelopes. Money is integer minor units.
- `Left to assign = income + money freed from earlier months - assigned`. So `assigned + left = income (+ freed)`.
- Envelope available = carried-in + planned + moved-in - moved-out - spent. Each envelope carries or resets at month end:
  carry keeps its leftover (or overspend) in the envelope; reset (and any unassigned money) returns to the pool next month.
  The money in the budget is always all income minus all spending, whatever the rollover rules and transfers.
- Overspend warnings (envelope >= 85% used, then over), move-money capped at the source's available amount.
- Bills: monthly, due day clamped to the month length, reminder on the day / 1 / 3 days before at 09:00 via
  `Reminders.enableAt` / `setAt` (re-armed on boot); mark paid records spending in the linked envelope (Undo).
- Savings goals: monthly amount = ceil(remaining / months left, current and target month inclusive); the schedule is spread
  largest-remainder so it adds up to the remaining amount to the cent.
- Month-over-month comparison and the envelopes that changed most; copy last month's income and plan; spread what is left.
- Currency picker is formatting only (no live rates); a different minor unit rescales the numbers and offers Undo. CSV export (Pro).
- `scripts/check_budgetplanner_math.py` runs the app's pure maths block under node against an independent Python Decimal/Fraction
  reference (4,000+ randomized multi-month budgets and edge cases) and blocks on any mismatch or violated invariant.

## Pro (pro_lifetime, $5.99) and Remove ads ($2.99)
Pro: unlimited envelopes (free 8) and goals (free 3), history beyond 3 months, CSV export, extra accents, no ads. Both non-consumable.
