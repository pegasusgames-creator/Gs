# Nonogram Identity

- **Category**: puzzle (logic-grid)
- **Layout archetype**: G (calendar / streak grid)
- **Mascot pattern**: M0 (no mascot — the puzzle grid is the personality)
- **Voice**: V8 (direct minimal) — "Tap to fill. Long-press to mark empty."
- **Texture**: T3 (subtle paper texture / graph-paper warmth)
- **Mood string**: graph-paper-warm

The app should feel like the puzzle section of a serious newspaper. Warm
parchment, ink-red accents, no emoji-as-UI, contemplative pacing. NYT
Nonogram / "Today's puzzle" energy. Built for players who want the
quietest possible puzzle app on their phone.

## Anti-pattern audit (APP_ARCHETYPES.md §5)

Audit the in-app design against the §5 anti-patterns when game.html is
next touched:

- [ ] Center-aligned everything → use offset weight
- [ ] Same SVG icon set as other apps → vary icon family per app
- [ ] All-caps headlines on every screen → mixed case for body
- [ ] Generic templated currency icon → make coin a graphite-pencil mark
- [ ] Identical button shapes / sizes / spacings → vary
- [ ] Symmetric vertical column layout → break with calendar grid header
- [ ] Generic "Level Complete!" celebration → "Solved." (single word, V8)
- [ ] Same loading / transition patterns → ink-bleed transition
- [ ] Identical settings screen → reorder, add app-specific options

Hit 3+ → redesign before next ship.

## Phase 8 self-check

Before declaring this app release-ready, all four of:

1. Side-by-side test (vs WaterSort: ocean-blue dark vs paper cream — clearly different products)
2. Voice-specificity test (does the menu copy reflect V8 minimal voice?)
3. Identity-element test (warm cream + ink-red accent + grid-as-hero — recognizable)
4. Anonymous-screenshot test (without title, would a user identify the paper-grid look?)

must pass. See APP_ARCHETYPES.md §8.
