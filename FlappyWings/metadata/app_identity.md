# Flappy Wings Identity

Shipping name **Flappy Wings** (store title "Flappy Wings: Paper Bird").
Package `com.pegasusgames.flappybird` (unchanged — the folder was renamed
from FlappyBird for trademark safety; the words of that third-party mark
appear nowhere in code, copy or metadata). Analog: the one-tap endless
flyer category — matched on feel (instant one-touch flight, score = gates,
medals, quick retry), differentiated by original art and trade dress, a
gentle verified ramp, a shared Daily course and honest second chances.

- Category: arcade (one-tap endless flyer, score game)
- Layout: A (hero Play + Daily tier; the family shell menu)
- Mascot: M1 (anthropomorphised game element — the folded red paper bird is the player and the emblem)
- Voice: V3 (playful narrator) — "Fold, flap and float through the sunset gates."
- Texture: T3 (paper — origami folds on the bird, paper-bird motif in the menu)
- Mood string: paper-sunset

Warm apricot sunset sky: Daylight chrome `#ffdcbf`, surfaces `#fff6ee`,
deep plum text `#3a1a2c`, coral→rose accent `#ff7a59`→`#d9407a` — a family
no sibling uses (WaterSort ocean blue, Nonogram cream/coral, 2048 sand/gold,
Unblock mint, PipeConnect sky, Afterimage blueprint, Sokoban terracotta peach,
Sudoku lilac). Midnight (800 coins) is a deep plum-indigo night sky.

Trade dress: the player is a red origami bird (no round yellow bird);
obstacles are scalloped white cloud columns capped by terracotta floating
islands with lanterns (no green tubes); the floor is a sea of clouds. Seven
sky skins recolour sky, sun, clouds, islands, feathers and the bird:
Apricot Dawn, Lilac Dusk, Mint Breeze, Rose Gold, Midnight, Storm Front,
Aurora (coins; Season/Weekly Pass unlocks all).

Content: no fixed level list. Every flight is a seeded course
(`fwGenNext` in game.html): endless = random seed, Daily = date seed with a
Mon→Sun target ramp (15 → 32). `scripts/check_flappywings_fair.py` flies
110 random courses through the full ramp + 180 gates at max difficulty and
every Daily course for 2026–2027 with a human-rate autopilot (every gap
passable), checks the ramp is monotonic and daily seeds deterministic, and
verifies JS == Python generator parity.

Economy: feathers = 1 coin each, medal bonus 5/15/30/60, Daily +10×streak.
Booster = Shield (`hintCount`, 25 coins) armed before take-off, absorbs one
hit. Hearts (lives) = mid-flight continues (max 3 per flight); one free
ad revive per flight (rewarded `extra_life`); new flights are always free.
