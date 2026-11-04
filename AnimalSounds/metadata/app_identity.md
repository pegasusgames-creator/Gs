# Animal Sounds Identity

- **Track**: kids (Google Play Families, ages 3-8), built on the kids shell
  (`docs/KIDS_SHELL.md`)
- **Layout archetype**: E (animated character speaks: Fenn the fox suggests the
  next animal in a speech bubble; activities are big picture tiles below)
- **Mascot pattern**: M2 (Fenn the fox cub: idle bob + blink, ears flap and
  hop on success, head tilt on a wrong tap, mouth moves while the voice speaks)
- **Voice**: V7 (educational warm) - "Yes! That is the cow!", "Where does the
  frog live?"
- **Texture**: T7 (storybook / illustrated: 44 original outlined SVG animal
  portraits, 10 habitat icons and 10 star stickers, dotted paper background)
- **Mood string**: kids-lilac

Soft lilac paper (`#efe9ff`) with a deep teal accent (`#0e7a85`) and four bold
tile colours (brick, blue, leaf, grape); Meadow (light green) and Bedtime
(soft navy, the only dark theme, never the default) are the alternates.
Identity element: Fenn the fox in a speech bubble above four picture tiles,
and animals drawn as round portrait stickers.

## Honesty notes
- Animal sounds are SYNTHESIZED in the app with WebAudio (no audio files, no
  recordings). The listing and the parent area say so; never claim "real
  recordings".
- Habitat and diet facts are checked by `scripts/check_animalsounds_facts.py`.

## Anti-pattern audit (APP_ARCHETYPES.md section 5)
Offset weight (mascot + bubble), mixed-case labels, app-specific icon family
(animal portraits, habitat glyphs), app-specific celebration copy (five stars
and an animal sticker per right answer). Passes the side-by-side, voice,
identity-element and anonymous-screenshot tests.
