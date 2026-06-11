# Pegasus Games — Screenshot Studio (Claude Code task)

**Goal:** a deterministic, code-only store-screenshot generator that replaces Gemini. It wraps each app's **real gameplay captures** (pixel-perfect — never regenerated) in a styled marketing frame, ships a **style library**, **decides the style per game**, and has a **richness/intensity dial** so output can be calm or eye-catching on demand. Reusable for every future app.

**This replaces `GEMINI_STYLE_PROMPTS.md` — delete it once this works.**

---

## How to run
Save as `docs/SCREENSHOT_STUDIO.md`, run at the workspace root:
> Implement `docs/SCREENSHOT_STUDIO.md`. Build `tools/screenshot-studio/`. Then run it for **WaterSortPuzzle** at `intensity:max` as the proof: auto-select its style, render all phone shots, show me the output + your style rationale before continuing to other surfaces/apps.

---

## 0. Ground truth (verified — don't re-derive)
- Captures exist at `store/screenshots/<surface>/raw/NN.png`. Surfaces + **exact output dims**: `phone 1080×2400`, `tablet_7 1200×1920`, `tablet_10 1800×2560`. (Bonus `feature 1024×500`, no device — §7.)
- The device **screen = the raw capture placed at native resolution** inside a code-drawn frame; never filtered/restyled/AI-regenerated. This is why Gemini is gone.
- Brand tokens are in each `game.html` `:root` (`--accent`, `--bg`, the menu-skin `--m-*`); identity is in `metadata/app_identity.md`. The wrapper pulls from these so store art and in-app art are one brand.
- Output replaces `store/screenshots/<surface>/NN.png`; keep a `…/_prev/` copy on first overwrite.

---

## 1. Architecture (`tools/screenshot-studio/`)
- `template.html` — one parameterized layout: background + decoration layer + **rich layer** (§3) + headline block + device mockup (rounded bezel, screen = `<img>` of raw, glow/shadow) + footer. CSS-variable driven; modules toggled by intensity.
- `styles.js` — the **style library** (§2): each style a `--s-*` token set + a `props`/`palette` hint for the rich layer.
- `layouts.js` — per-surface geometry (§5).
- `render.mjs` — **Playwright** headless Chromium: inject tokens+content, viewport = exact surface size with `deviceScaleFactor`, animations off, **bundled `woff2` fonts** (no system fonts, no network) → byte-deterministic. Render 2× then downscale with `sharp` for crisp text.
- `render_svg.py` — **cairosvg fallback** (same layout/tokens) when Chromium is unavailable. (Proven working.)
- `components/` — reusable SVG modules (§4): eyebrow, badge, rating, glow/halo, rim-light, floating-prop, light-rays, bokeh, sparkles, confetti, grain.
- `qa.mjs` — assertions (§6).
- per-app `store/screenshots/studio.config.json` (§5).

**Determinism:** fixed viewport+scale, animations off, bundled fonts, no network → re-running yields byte-identical PNGs. **Quality:** screen is the raw at native res, so it's sharp by construction.

---

## 2. Style library (token-driven; the app's `--accent` tunes each)
Margins-only decoration; never over device/headline. Each is a `--s-*` set so two apps sharing a style still differ by accent.

1. **editorial** — parchment `#f5f0e6→#ece2cf`, ink `#28231e`. Pinstripes 8% + outline circles + thin rule; serif display + serif-italic sub; warm soft shadow. *NYT Games / Monocle. Quiet, premium.*
2. **tropical** — ocean `#26d0ce→#1a5f7a→#0c1c30`, mint `#6fffe9`. Confetti + palm-leaf silhouettes; heavy sans; aqua/gold glow. *Summer poster.*
3. **kawaii** — pastels `#ffe5d9/#fff9c4/#ffe4ec`, candy pink+mint. Clouds, stars, sparkles; rounded sans; puffy pink shadow. *Sanrio / Animal Crossing.*
4. **synthwave** — `#0a0a14`, neon `#ff2e88`+`#2de2e6`. Neon grid horizon + sun; italic display + mono; neon edge glow. *Retro arcade.*
5. **blueprint** — navy `#0e1726`, cyan `#37e0e0`. Graph-paper grid, dashed measures, node dots; geometric sans + mono; thin cyan outline. *CAD/engineering.*
6. **darkroom** — near-black `#0c0b10`, gels magenta/cyan/amber. Spotlight + grain + light leaks; grotesk + small-caps; rim light, deep shadow. *Photo darkroom. Moody/premium.*
7. **riso** — duotone clay `#e3725a` + sage `#2f6b5e` on cream. Riso grain, organic blobs, halftone; grotesk + humanist; flat offset color shadow. *Risograph zine.*
8. **candy** — grape/cherry/lime, glossy. Vibrant diagonal + bokeh; glossy bubbles, sprinkles; chunky rounded heavy sans; bright halo+gloss. *Hyper-casual sweet.*
9. **swiss** — white/off-white, ONE bold app accent. Flat/2% tonal, one oversized accent shape, strict grid, whitespace; neo-grotesk tight; crisp neutral shadow. *Apple Editor's Choice. Restraint = standout.*
10. **aurora** — indigo `#0b1026→violet`, starfield, aurora ribbons. Constellation lines, glow orbs; light luminous sans, wide tracking; soft cosmic glow. *Meditative/ambient.*
11. **storybook** — warm paper, ink doodles, crayon accents. Hand-drawn squiggles, sketch icons, tape corners; marker display + friendly serif; sketchy outline. *Picture-book.*

Add more later by appending a token set — template/renderer don't change.

---

## 3. Richness system — the `intensity` dial
One setting per app (or per shot): **`minimal` | `balanced` | `max`**. It progressively turns on rich-layer modules. Default `balanced`.

| Module (built in §4) | minimal | balanced | max |
|---|---|---|---|
| Layered/brighter gradient + warm wash | base | + glow blooms | + 2nd accent wash |
| Glow bloom + halo behind device | – | soft | strong |
| Device rim-light + deeper shadow | soft | yes | yes |
| Headline gradient fill + outline | flat | gradient | gradient + outline |
| Eyebrow kicker (e.g. "★ POUR · SORT · RELAX") | – | optional | yes |
| Burst badge (e.g. "500+ LEVELS") | – | – | yes (1 only) |
| Footer ★ rating | – | optional | yes |
| Floating game props (§4) | – | 1–2 | 2–4 |
| Light rays / bokeh / sparkles | – | bokeh | rays+bokeh+sparkles |
| Confetti density | sparse | medium | dense (margins only) |
| Grain/texture | subtle | subtle | per-style |

**Per-style caps (brand integrity):** loud styles (tropical, candy, kawaii, synthwave) honor `max` fully. Quiet styles (**editorial, swiss, riso**) cap at "balanced," and their `max` means **more depth/detail, not more saturation** — paper/print texture, embossing, a faded subject motif (e.g. a revealed nonogram picture), a single oversized accent — never confetti/badges/neon. Don't let a quiet brand go loud.

---

## 4. Components (`components/`, SVG modules, original vectors only)
- **glow/halo** — radial bloom behind device; **rim-light** — bright inner stroke; **shadow** — stacked translucent offset rects (soft).
- **headline** — eyebrow (small tracked caps) + title (gradient `fill="url(#head)"`, outline via stroke layer behind, `paint-order:stroke`) + subtitle. Auto light/dark per contrast.
- **badge** — rotated burst sticker, 1 max; **rating** — ★ row.
- **floating-prop** — oversized vector of a real game element, partly behind the device for depth. Source from each app's existing in-game emblem/`injectMenuIllustration` SVG so props match the game: tropical→liquid tubes+droplets, kawaii→tiles+clouds, blueprint→pipe-knots/nodes, synthwave→chevrons/grid-shards, darkroom→gel swatches, editorial→(none; quiet).
- **ambience** — light-rays, bokeh, sparkles, confetti, grain. All margin-only.

---

## 5. Layout + config
**Geometry (`layouts.js`):** device centered; width ≈ phone 62% / tablet_7 58% / tablet_10 55%; headline top or bottom (per `pos`); footer bottom-center. **Decoration & props only in outer margins** — never within ~80px of device/headline, never over the screen.

**Badge/prop placement (no text collisions — hard rule).** Compute the bounding boxes of headline, subtitle, device, and footer first. The badge and any floating prop may occupy **only** these zones: the two top corners *above* the headline, or the left/right side margins *beside the device* (the gutter between the device edge and the canvas edge), or the bottom corners above the footer. Place the badge in the first zone that fits with ≥24px clearance from every text/device box; **auto-reflow** through the zone list on collision; if none fits, **drop the badge** (never overlap text). One badge max. (The subtitle box is the one most often hit — include it explicitly.)

**`store/screenshots/studio.config.json`:**
```json
{ "style": null, "intensity": "max",
  "footer": "WATER SORT PUZZLE", "rating": "★★★★★",
  "props": ["tube","droplet"],
  "copy": {
    "phone": { "06": {"l1":"ONE COLOR","l2":"PER TUBE","sub":"Pour and sort until every tube is one clean shade.",
                       "pos":"top","eyebrow":"POUR · SORT · RELAX","badge":"500+ LEVELS"} },
    "tablet_7": {} } }
```
Missing copy → carry forward the headline from the current marketing PNG or leave `TODO(copy)`; never invent claims. `style`/`intensity` here are hard overrides.

---

## 6. QA / acceptance (`qa.mjs`, after every render)
- [ ] Dims **exact** per surface; <8 MB; RGB.
- [ ] **Screen pixel-identical to raw** in the device region (assert placed area == source crop).
- [ ] Headline WCAG AA vs sampled bg (≥4.5:1 body / ≥3:1 large); pick light/dark token to pass.
- [ ] **No overlaps (HARD FAIL):** badge, props, and decoration must not intersect the bounding box of the headline, **subtitle**, device, or footer (≥24px clearance). Render fails and reflows/drops the offending element rather than shipping the overlap.
- [ ] **Determinism:** re-render → 0-pixel diff.
- [ ] Quiet styles never exceed their cap (no badge/neon/confetti on editorial/swiss/riso).
- [ ] `STYLE_REGISTRY.md` updated; rationale logged; family reads related, each app distinct.
- [ ] Fully offline; bundled fonts.

---

## 7. Per-game STYLE SELECTION (Claude Code decides)
For each app: read `app_identity.md` (Mood, Category, Texture, Voice) + `:root --accent/--bg` + sample raw hues. Match via rubric, pick best fit, **tune the style's accent tokens to the app's accent**, keep portfolio variety (`STYLE_REGISTRY.md`), output a 2–3 sentence rationale; honor config overrides.

| Game feels… | Lead styles |
|---|---|
| quiet logic / deduction / number / word | editorial, swiss |
| bright casual / water / party | tropical, candy |
| cute / cozy / merge | kawaii, candy |
| fast / retro / sliding | synthwave, blueprint |
| spatial / wiring / flow | blueprint, aurora |
| light / reveal / moody-premium | darkroom, swiss |
| calm / nature / loops | riso, aurora |
| kids / story / trivia | storybook, kawaii |

**Seed picks (refine per rubric):** Nonogram→editorial · WaterSort→tropical · 2048→kawaii · Unblock→synthwave · PipeConnect→blueprint · Afterimage→blueprint · Overlay→darkroom · Hunch→swiss.

## 8. Adding a future app
1. Drop captures into `store/screenshots/<surface>/raw/`. 2. (Optional) write `studio.config.json` copy + pick `intensity`. 3. Run → auto-selects+tunes style, renders all surfaces, QAs, updates registry. 4. `--feature` emits the 1024×500 banner from the same tokens (no device).

## Notes
- Bundle real `woff2` fonts (don't depend on system fonts — that's what makes it deterministic + high quality across machines).
- All decoration/props/emblems are **original vectors** you author or the app's own in-game SVGs — no third-party/branded/AI-traced IP; keep the device mockup a generic rounded rect.
- Derive screenshot `--s-*` from the app's menu-skin `--m-*` so marketing and in-app stay one brand.
