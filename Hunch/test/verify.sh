#!/bin/sh
# Overlay level verification — campaign seed mine + 200-day daily QA with the
# verbatim prototype rule catalog + disambiguation (docs/prototypes/greenlight.html). Any FAIL or
# fallback > 0 is a blocker.
node "$(dirname "$0")/verify_levels.js" | tail -1
