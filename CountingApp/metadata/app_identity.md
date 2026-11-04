# Counting Fun Identity

- **Track**: kids (Google Play Families, ages 3-8) on the kids shell (`docs/KIDS_SHELL.md`)
- **Layout archetype**: E (animated character speaks: Pebble suggests the next number to count in a speech bubble; four big picture tiles below)
- **Mascot pattern**: M3 (Pebble the penguin: idle bob + blink, beak moves while the voice speaks, flaps and hops on success, tilts to think on a gentle miss; also sits beside every activity)
- **Voice**: V7 (educational warm) -- "That makes 7! Great counting!", "Not quite. Tap each one and count again."
- **Texture**: T7 (storybook / illustrated: original outlined SVG art for eight counting objects, ten sea-animal stickers and number badges, dotted paper background)
- **Mood string**: kids-lagoon

Pale lagoon aqua (`#d6f1ef`) with a berry accent (`#b0246a`) and four bold tile colours (rose, ocean blue, sea green, amber). Sand (warm paper) and Night (deep navy, the only dark theme, never the default) are the alternates. Numerals use Andika. Identity element: things you tap and count with a pop (apples, fish, ducks, flowers), a hundred chart that fills with tens and ones, and skip-counting songs where every number lights up with its note.

## Distinct from siblings

- TallyCounter is the adult multi-counter tool; this is a kids counting game with a voice, stickers and a parental gate.
- BasicMathKids does plus/minus/compare up to 20 (mint, bunny, blocks and beads); Counting Fun never adds or subtracts. It counts 1-20 by tapping, 1-100 by tens and ones, skip-counts by 2/5/10 with songs and traces digits. Different palette family (aqua vs mint), mascot (penguin vs bunny), tile icons and boards.
- ABCLearning shares only the shell. Different palette family (aqua vs butter yellow), mascot (penguin vs owl).

## Anti-pattern audit (APP_ARCHETYPES.md section 5)

- [x] Not centre-stacked buttons: character-led home, 2x2 picture tiles
- [x] Own icon family (counting dots, music note, dotted digit, question blocks)
- [x] No currency at all (stickers, not coins)
- [x] No timers, lives or failure states; a wrong answer gets a gentle hint and another try
- [x] App-specific celebration: confetti + Pebble hop + spoken number + sticker reveal
- [x] Settings is a grown-ups area behind a hold-to-answer gate
