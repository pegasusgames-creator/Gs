# DinosaurApp Identity

- **Track**: kids (Google Play Families, ages 3-8), built on the kids shell (`docs/KIDS_SHELL.md`)
- **Layout archetype**: E (animated character speaks: Tiko the baby dino suggests the next dinosaur in a speech bubble; four big picture tiles below)
- **Mascot pattern**: M3 (Tiko hatching from an eggshell cap: idle bob + blink, arms flap and hop on success, head tilt on a wrong tap, mouth moves while the voice speaks)
- **Voice**: V7 (educational warm) - "Let's meet Eoraptor!", "You found a Stegosaurus fossil!"
- **Texture**: T5 (hand-drawn / sketch: 39 original thick-outlined SVG creatures built by a tube-outline generator, 8 fossil-themed stickers, dotted sand paper background)
- **Mood string**: kids-bright

Warm sand paper (`#f7ecd0`) with a terracotta accent (`#b5481a`) and four bold tile colours (terracotta, blue, leaf, plum); Fern (light green) and Volcano (charcoal-red, the only dark theme, never the default) are the alternates.
Identity element: Tiko the hatchling in a speech bubble above four picture tiles (footprint, ruler, bone, star), and creatures drawn as thick-outlined round portrait stickers.

## Honesty notes
- Nobody knows how dinosaurs sounded: every roar is SYNTHESIZED by the app (WebAudio, no audio files, no recordings) and labelled "made-up roar, made by the app".
- Facts (length, weight, diet, period, fossil continent, size-compare ratios) are checked by `scripts/check_dinosaurapp_facts.py` against a palaeontology reference table.
- Pteranodon / Quetzalcoatlus (flying reptiles), Elasmosaurus / Mosasaurus (sea reptiles) and Dimetrodon (older than the dinosaurs) are labelled "not a dinosaur".

## Distinct from AnimalSounds
Different palette family (sand/terracotta vs lilac/teal), different mascot (hatchling vs fox), different screens (period-grouped book, size slider, fossil dig, shadow match vs sound board, habitats, quiz), different art generator and icon focal element (dinosaur silhouette on an egg-shaped badge).
