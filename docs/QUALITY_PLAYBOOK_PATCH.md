# PATCH for docs/QUALITY_PLAYBOOK.md

## Replace section §7.1.5 "Capture quality" with this expanded version

### 7.1.5 Capture quality — what to actually show inside the frame [ALL, P0]

The marketing-frame wrapping (`wrap_screenshots.py`) gives you the
gradient and headline, but the SCREENSHOT INSIDE the frame is what
users evaluate. May 2026 Puzzle2048 audit found six common capture
failures, each producing a screenshot that looks unfinished even with
a perfect wrap:

**Empty / sparse boards.** Capturing level 1-2 of a puzzle when the
board is mostly empty wastes screenshot real estate. Per §7.1, slot 01
("deep gameplay") must show the LARGEST grid the level generator
produces, in mid-progression state, NOT a tutorial-tier early board.

**"How to Play" tutorial overlay visible.** The tutorial appears on
fresh installs and dismisses on first tap. If captured before
dismissing, the tutorial sits over the entire board and blocks the
gameplay you're trying to show. See §7.1.5.5 below for the seed
script that prevents this.

**Default first-install state ("0/0/0 everywhere").** Stats screen,
Missions screen, and Daily Challenge all show "0 levels played, 0
coins, 0 streak" on a fresh install. Reads as "developer forgot to
populate sample data." See §7.1.5.5.

**Tiny content in tall canvas.** Phone captures are 1080×2400 (9:20).
A 4×4 puzzle grid centered in that canvas leaves 60% of the screenshot
as dead space. The marketing-frame wrap doesn't fix this — the
screenshot inside the frame is still mostly empty. The in-app
gameplay layout must scale the playable area to fill tall phones (per
§1.5).

**Modals over darkened backgrounds.** Capturing a modal (Daily
Mission panel, Stats popup) shows a dark scrim over the menu behind.
The result is muddy and low-contrast. For modals, capture in a
dedicated screenshot mode where the background is replaced with the
app's solid theme color. See §7.1.5.4.

**★ NEW (Puzzle2048 May 2026 audit) — Same raw screenshot used in
multiple slots.** The pre-wrap raw captures must be VISUALLY DISTINCT
across the 7 slots. The Puzzle2048 audit found 7 wrapped screenshots
using only 2 distinct raw images: tap sequences in
`capture_screenshots.py` were missing target buttons, so 5 slots all
captured the same early-game board. Result: 7 different headlines
("REACH 2048", "NEW HIGH SCORE", "WEEKLY EVENT", "BEST TILES BEST
RUNS", "ONE FREE UNDO") over visually identical content — every claim
the headline made was a lie about what the screenshot showed.

`pre_publish_check.py check_screenshot_uniqueness` enforces this:
perceptual hashes of all 7 phone raws must differ by at least 4
hamming distance from each other. Identical or near-identical raws
across slots = blocking.

When this check fails, `capture_screenshots.py` taps are missing their
targets. Common causes:
- Tap coordinates assume a default Pegasus menu layout that this
  app doesn't use — set per-app overrides at
  `<App>/test/screenshot_taps.json`
- Emulator screen size differs from the script's assumed dimensions
  — check `adb shell wm size` and adjust DEFAULT_SCREEN_W/H
- Animations haven't settled before tap fires — increase post_delay
  per slot

The capture script ALSO checks this on the fly now and refuses to
continue past the first duplicate.


### 7.1.5.5 Pre-screenshot localStorage seed (MANDATORY)

Every app gets a per-app file at `<App>/test/seed_screenshot_state.js`
containing localStorage assignments that pre-populate realistic
mid-game state. Without this, screenshots show fresh-install zeros
across Stats / Missions / Daily and the tutorial overlay covers the
gameplay screen.

**The seed script must use THIS app's actual localStorage keys** —
not a generic template. Every app's `game.html` has different storage
keys. Read the keys from the actual game code before writing the seed.

For Puzzle2048 specifically (real keys observed in May 2026 audit):
```javascript
localStorage.setItem('p2048_tutorial_seen', 'true');     // dismisses How-to-Play
localStorage.setItem('p2048_score', '247');
localStorage.setItem('p2048_best', '512');
localStorage.setItem('p2048_best_tile', '128');
localStorage.setItem('p2048_coins', '85');
localStorage.setItem('p2048_lives', '5');
localStorage.setItem('p2048_streak', '7');
localStorage.setItem('p2048_weekly_progress', '3'); // out of 5
// per-mission progress:
localStorage.setItem('p2048_mission_merger_count', '47');  // partial
localStorage.setItem('p2048_mission_streak_count', '6');   // partial
```

Generic-template seeds with keys like 'coins' or 'streak' will silently
do nothing if the app's actual keys are different. Verify after seeding
by capturing slot 02 (menu) and confirming the displayed Score / Best /
Best Tile / coin count match the seeded values.


## Replace section §7.1.6 "Honesty in screenshot copy" with this stricter version

### 7.1.6 Headline ↔ image content match (MANDATORY)

Every wrapped screenshot is a TWO-PART CLAIM: the headline says X is
in the app, and the image must SHOW X is in the app. Screenshot 4 with
headline "WEEKLY EVENT 5 GAMES / Play five rounds this week" sitting
above an image of an early-game board with no event UI visible is
false on its face — the header asserts a feature the image doesn't
demonstrate.

**Required check before each app ships:** for each headline in
`metadata/screenshot_headlines.json`, verify the image at the
corresponding slot ACTUALLY SHOWS the feature claimed:

| Headline claim | Image must show |
|---|---|
| "DAILY CHALLENGE" | the daily mode UI mid-play, NOT the menu |
| "WEEKLY EVENT" | the weekly event panel/banner, NOT generic gameplay |
| "BEST TILES BEST RUNS" / Stats | the Stats screen, NOT a generic board |
| "ONE FREE UNDO" | an undo button visible OR a board state mid-undo |
| "NEW HIGH SCORE" | the score-celebration UI, NOT a quiet gameplay screen |
| "LEVEL COMPLETE" | the Level Complete modal with stars, NOT mid-play |

If headline says it, image must show it. Otherwise either:
- Re-capture the slot with the correct screen content
- Change the headline to describe what's actually visible

This is part of SHIP_GAME §8.2 and is non-negotiable. Mismatches are a
Play Store Misleading Behavior policy risk and will be caught by
reviewers.

For Puzzle2048 May 2026 audit, 5 of 7 slots had this defect. Fix
before re-uploading.


## Replace section §7.2 "Screenshot text overlays" — add spacing rule

### 7.2.1 Header typography spacing

The marketing wrap header has three components stacked vertically:
headline line 1, headline line 2, subtitle. The vertical gaps between
them must respect the relative weights of the typography.

**Required gaps as fractions of canvas height (1080×2400 phone, 1200×1920
tablet 7", 1800×2560 tablet 10"):**

| Element pair | Phone gap | Tablet gap |
|---|---|---|
| Line 1 → Line 2 | 1.5% (~36px) | 1.5% |
| Line 2 → Subtitle | 4.0% (~96px) | 3.5% |
| Subtitle → device frame | 2.5% (~60px) | 3.0% |

The Puzzle2048 May 2026 audit found subtitle sitting too close to
the second headline line (descender of "EVERY RUN" almost touched the
subtitle). Root cause: the legacy 2.0% gap between line 2 and
subtitle didn't account for heavy display-font descenders at 140-180px
sizes.

The 4.0% gap is the new minimum. Heavier or italic display fonts
should bump to 4.5%. Tighter wrappers may try to reclaim the space —
don't. The breathing room is what makes the header read as designed
rather than crammed.


## NEW section §7.3 — Tablet screenshots (MANDATORY)

### 7.3 Tablet screenshots [ALL, P0]

**Every app gets phone, 7" tablet, AND 10" tablet screenshots.** No
exceptions, no per-tier scaling, no "skip for long-tail." If an app
ships, it ships with all three sets.

| Set | Resolution | Slot count | Required |
|---|---|---|---|
| Phone | 1080×2400 | 7 | YES |
| 7" tablet | 1200×1920 | 7 | YES |
| 10" tablet | 1800×2560 | 7 | YES |

The reasoning is operational: if the wrap pipeline supports tablets at
all (and it does — `wrap_tablet_screenshots.py` exists), then the
marginal cost per app is the cost of capturing tablet raws, which is
~10 minutes once the tablet AVD is configured and the app's tap
overrides are dialed in. That's worth it because tablet Play Store
listings without tablet screenshots get the "Phone screenshots only"
warning badge in some Play Store surfaces and rank lower for tablet
searches.

The previous "phone running in a tablet canvas" behavior — where
`wrap_tablet_screenshots.py` silently rescaled phone raws into tablet
aspect — is a worse outcome than no tablet screenshots at all, and is
now blocked by the resolution check added in May 2026.

**Tablet captures are SEPARATE captures.** A tablet emulator running
the same app produces a fundamentally different in-app layout —
wider boards, different HUD positioning, side panels in some games,
larger touch targets. The captures must come from a tablet AVD, not
from the phone AVD with phone raws rescaled.

**Required tablet AVD setup (one-time per machine):**

```
# In Android Studio AVD Manager, create two AVDs:
#   pegasus_tablet_7   — Pixel C profile or similar, 1200×1920 portrait
#   pegasus_tablet_10  — Nexus 10 profile or similar, 1800×2560 portrait
# Or via command line:
avdmanager create avd -n pegasus_tablet_7 -k "system-images;android-34;google_apis;x86_64" --device "pixel_c"
avdmanager create avd -n pegasus_tablet_10 -k "system-images;android-34;google_apis;x86_64" --device "Nexus 10"
```

Then `capture_screenshots.py --target tablet_7` and `--target tablet_10`
boot the matching AVD. Tap coordinate fractions usually still work
across phone/tablet because they're proportional, but per-app
verification is required because tablet UI sometimes shifts buttons
to side panels. Per-app tap override files at
`<App>/test/screenshot_taps.json` may need separate `tablet_7_*` and
`tablet_10_*` keys.

**`wrap_tablet_screenshots.py` rejects phone-resolution raws** as of
May 2026. Trying to wrap a 1080-wide phone capture into a tablet
canvas fails with an explicit error rather than producing the
"phone running in a tablet emulator" look that Puzzle2048 shipped in
April 2026.

**Migration plan for existing apps shipped without tablet screenshots:**
the 5 flagships (WaterSort, Nonogram, PipeConnect, Puzzle2048,
UnblockPuzzle) need full re-captures including tablet sets before any
v1.x update ships. Long-tail apps need tablet captures included in
their first SHIP_GAME run; no ship without all three sets.


## NEW subsection §7.4 — Emoji rendering / glyph fallback

### 7.4 Emoji and special glyphs in game.html [ALL, P1]

Many app icons and inline glyphs in game.html use Unicode emoji
codepoints (✨ ❤ ⚡ 🎯). When the device's font stack doesn't include
that emoji codepoint, the system renders a "tofu" rectangle (□) instead.
The Puzzle2048 May 2026 audit caught this on the menu's bottom
icon row and the weekly-event banner's coin glyph.

**Three options to prevent emoji fallback failures:**

1. **Replace emoji with inline SVG.** Most reliable; scales cleanly,
   no font dependency. Heavier in code but only ~200 bytes per glyph.
2. **Use Twemoji or Noto Color Emoji as a webfont** loaded inside
   game.html. Adds ~100-300KB but covers the whole emoji range.
3. **Stick to the safe codepoints:** ✓ ✗ ★ ☆ ♥ ♦ ◆ ◇ ● ○ — basic
   geometric shapes that virtually every system font supports. No
   color but always renders.

For new Pegasus apps, default to option 3 (safe codepoints) for inline
glyphs. Use option 1 (SVG) for the icon row of buttons because those
need to be distinct + recognizable at small sizes, where geometric
shapes are too generic.

NEVER use emoji in store listing copy — Play Store's editorial review
is uneven about emoji rendering across crawl tools and may flag listings.
