# Word Connect word lists

All three files are filtered (3-7 letters, a-z only) copies of lists from
**12dicts 6.0.2** by Alan Beale (http://wordlist.aspell.net/12dicts/),
which the author explicitly releases to the public domain ("I explicitly
release them to the public domain, but request acknowledgment of their
use"). The AGID-derived 12dicts lists (2of12inf, 2+2+3*) are NOT used.
The game credits 12dicts in Settings.

| File | Source | Used for |
|---|---|---|
| `3of6game_3to7.txt` | `International/3of6game.txt` (the list built for word games; markers `^ & $ + !` kept) | bonus-word dictionary (every valid word the player may swipe) |
| `2of5core_3to7.txt` | `Special/2of5core.txt` (core vocabulary marked important by 2 of 5 learner's dictionaries) | crossword answers (plus their inflections found in 3of6game) |
| `3esl_3to7.txt` | `American/3esl.txt` | reserve answer tier (only used if the core tier runs short) |

`../gen_levels.py` applies the family-friendly block lists (offensive words
are never accepted, not even as bonus words; sensitive-but-clean words are
kept out of the crossword answers) and writes the shipped LEVELS / DAILY
data into game.html. `scripts/check_wordconnect_valid.py` re-verifies the
shipped data.
