#!/bin/sh
# Afterimage level verification — re-runs the campaign seed mine + 200-day
# daily QA with the verbatim prototype solver. Any FAIL or fallback > 0 is
# a blocker. (Logic source of truth: docs/prototypes/ditto.html)
node "$(dirname "$0")/verify_levels.js" | tail -2
