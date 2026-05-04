# NumberBase Identity

- **Category**: tool
- **Layout archetype**: I (toolbox / direct tool)
- **Mascot pattern**: M0 (no mascot — game elements carry the personality)
- **Voice**: V8 (direct minimal)
- **Texture**: T8 (brutalist / minimal)
- **Mood string**: tool-clean

The app should feel like: fast, no-friction utility — opens straight to the tool.

## Anti-pattern audit (APP_ARCHETYPES.md §5)

This file was auto-generated during the 2026-04-30 portfolio archetype
assignment pass. The four archetypes above were chosen so the app does
NOT default to the template signature (A/M0/V1/T1).

When the app's `game.html` is next touched (or built fresh), audit the
in-app design against the §5 anti-patterns:

- [ ] Center-aligned everything → use offset weight
- [ ] Same SVG icon set as other apps → vary icon family per app
- [ ] All-caps headlines on every screen → mixed case for body
- [ ] Generic templated currency icon → make it match the app theme
- [ ] Identical button shapes / sizes / spacings → vary
- [ ] Symmetric vertical column layout → break with side panels / FAB
- [ ] Generic "Level Complete!" celebration → app-specific phrasing
- [ ] Same loading / transition patterns → vary
- [ ] Identical settings screen → reorder, rename, add app-specific options

If 3+ of the above are hit, redesign before the next ship.

## Phase 8 self-check

Before declaring this app release-ready, all four of:

1. Side-by-side test (vs other shipped apps, do they look like different products?)
2. Voice-specificity test (does the menu copy reflect this app's voice archetype?)
3. Identity-element test (a single recognizable visual element)
4. Anonymous-screenshot test (could a user identify this app without title/name?)

must pass. See APP_ARCHETYPES.md §8.
