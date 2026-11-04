# Basic Math for Kids Identity

- **Track**: kids (Google Play Families, ages 4-8) on the kids shell (`docs/KIDS_SHELL.md`)
- **Layout archetype**: E (animated character speaks: Bea suggests the next skill in a speech bubble; activities are big picture tiles below)
- **Mascot pattern**: M3 (Bea the bunny: idle bob + blink, talks while the voice speaks, hops and flaps her ears on success, tilts to think on a gentle miss; also sits beside every activity)
- **Voice**: V7 (educational warm) -- "3 plus 2 makes 5!", "Almost! Let's do it together."
- **Texture**: T7 (storybook / illustrated: original outlined SVG art for six counting objects, 12 friend stickers and 20 number cards, dotted paper background)
- **Mood string**: kids-mint

Mint paper (`#d8f1e2`) with a brick-coral accent (`#c4411f`) and four bold tile colours (brick, blue, leaf, grape). Peach (light) and Night (soft teal, the only dark theme, never the default) are the alternates. Numerals use Andika. Identity element: manipulatives you move (blue and orange blocks, ten-frame counters, bead frame, number-line hops) with Bea counting aloud.

## Distinct from siblings

- MultiplicationGame is times tables; CountingApp is counting 1-100. This app never multiplies and stops at 20; its core is moving objects to add, take away and compare.
- ABCLearning shares only the shell. Different palette family (mint vs butter yellow), mascot (bunny vs owl), tile icons, and activity boards.

## Anti-pattern audit (APP_ARCHETYPES.md section 5)

- [x] Not centre-stacked buttons: character-led home, 2x2 picture tiles
- [x] Own icon family (blocks, ten-frame, beads, number line)
- [x] No currency at all (stickers, not coins)
- [x] No timers, lives or failure states; a wrong answer triggers a guided count-along
- [x] App-specific celebration: confetti + Bea hop + spoken equation + sticker reveal
- [x] Settings is a grown-ups area behind a hold-to-answer gate
