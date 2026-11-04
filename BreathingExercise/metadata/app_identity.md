# BreathingExercise Identity

Utility-track app on the utility shell (docs/UTILITY_SHELL.md), built from HabitTracker's shell.

- **Category**: wellness / breathing timer - Google HEALTH_AND_FITNESS, Apple HEALTH_FITNESS
- **Layout archetype**: I (toolbox / direct tool) - opens on the breathing circle, three tabs: Breathe · Patterns · Progress
- **Mascot pattern**: M4 (abstract motif: the breathing orb with a guide ring)
- **Voice**: V5 (calm / zen) - plain, quiet wording ("may help you relax"), no medical or anxiety-treatment claims
- **Texture**: T2 (soft cards, seafoam light)
- **Mood string**: wellness-calm

Seafoam Daylight (`#EEF5F2`, accent deep teal `#1B6E63`) with a free dark theme; Sky is a free accent, Dusk / Sand / Lilac are Pro accents
(24-hour rewarded trial). Distinct from HabitTracker's violet and BloodPressureLog's navy.

## What the app does
- A large inhale / hold / exhale circle (rAF-timed, honours reduced motion), optional soft synthesized tones (WebAudio), spoken cues
  (speechSynthesis, in the app language) and haptic ticks. Screen kept awake while a session runs (best-effort Wake Lock).
- Patterns: Box 4-4-4-4, 4-7-8, Coherent 5.5, Physiological sigh 2-1-6, Calm 4-6; Pro adds custom patterns (inhale / hold / exhale / rest).
- Sessions of 1, 2, 3, 5 minutes (free) or 10, 15, 20, 30 (Pro) always finish on a full breath: cycles = floor(length / cycle), at least 1.
- Streak, best streak, minutes logged, 14-day chart, calendar; Pro: past months, 12-month chart, per-pattern totals, session history.
- Optional gentle daily reminder (shell slot 0, permission asked in context). Local-only data, backup/restore.
- `scripts/check_breathingexercise_patterns.py` runs the pure `BX` block under node against a Python reference.
