# Pegasus Games — Main-Menu Redesign (Claude Code task)

**Goal:** make all five game menus feel like *games* (world, depth, warmth, motion) instead of a settings/office screen, and make them read as one **family** while each keeps a distinct identity.

Apps: `Nonogram`, `Puzzle2048`, `UnblockPuzzle`, `WaterSortPuzzle`, and the new `PipeConnect`.

---

## How to run this

> Implement `docs/MENU_REDESIGN.md`. Do Part A first (shared skin) on **WaterSortPuzzle only**, stop, and show me a screenshot of the menu (light + midnight). After I approve, apply Part A to the other four, then Part B per app. One commit per app. Do not touch gameplay screens.

Work one app at a time. After each app, render the menu on a phone (≈1080×2400) **and** a 7" tablet viewport, in the default theme **and** `data-theme="midnight"`, and diff against the current menu so regressions are obvious.

---

## 0. Ground truth (verified — do not re-derive)

* Each app is a **single file**: `<App>/android/app/src/main/assets/game.html` (HTML+CSS+JS inline).
* Menus are **token-driven** via `:root` CSS custom properties: `--bg --surface --surface2 --border --accent --accent-dim --text --text-muted --menu-tile-bg --menu-tile-border --menu-tile-fg --coin --heart`. A `html[data-theme="midnight"]` block overrides them; 2048 and WaterSort define many more in-game palette themes too.
  * **Caveat found during implementation:** not every app defines every token (WaterSort lacks `--accent-dim`). A `var()` referencing an undefined custom property invalidates the whole declaration at computed-value time — so every skin default that touches potentially-missing tokens must carry a fallback chain, e.g. `var(--accent-dim, var(--accent, #888))`.
* **The menu layout is already unified** by one runtime owner: `<script data-growth-shim="MENU">`. It builds the resource bar, Tier-1 *Continue/Play*, Tier-2 *Daily*, the Tier-3 icon row, and the `[data-menu-illustration]` mini-preview. Its own comments state: *"STRUCTURE is universal … VISUAL DESIGN (colors, fonts, shapes) stays per-app."*
* **`CLAUDE.md` rule — "No competing runtime shims."** Do **not** add a second menu-building script or any `setInterval` injector. All visual work here is **static CSS** (and small additions to the existing `injectMenuIllustration()`), never a rival shim.
* Menu container id differs: **`#screen-menu`** (Nonogram, PipeConnect) vs **`#menuScreen`** (the other three). Always target **both**.
* Icon-tile class differs: **`.menu-icon-btn`** (Nono/2048/Unblock/Pipe) vs **`.icon-btn`** (WaterSort). Both sit in **`.menu-icon-row`**. Target both.
* Title class differs: `.menu-logo` (Nono, Pipe) · `.menu-title` (Unblock) · `.game-title h1` (2048, WaterSort).
* CTA is `.btn.btn-primary` everywhere (Nono also has `.btn-play`; Pipe uses `.menu-primary` — include it in the CTA selector union).

### Hard constraints
1. **Additive only.** The skin sets *backgrounds, shadows, gradients, borders, pseudo-elements, filters, animations*. It must **never** set `width/height/flex/display/position:absolute` on menu children — the MENU shim owns layout (it uses `!important`; don't fight it).
2. **Scope to the menu.** Every selector is prefixed with `#screen-menu` / `#menuScreen`. Gameplay, level-select, shop, settings, overlays stay byte-for-byte unchanged.
3. **Token-first.** New skin variables are all named `--m-*` and default off, so an app with no overrides looks ~unchanged. Per-app identity = setting `--m-*` in that app's `:root` (+ `midnight`).
4. **Theme parity.** Every `--m-*` you set in `:root` you also set (or deliberately inherit) under `html[data-theme="midnight"]`, and sanity-check 2048/WaterSort's extra themes don't break (they inherit `--m-*` unless overridden — fine).
5. **Perf/battery (WebView).** Animate only `transform`/`opacity`/`background-position`. No JS rAF loops. Motifs = CSS gradients or one small inline-SVG data-URI (< ~2 KB). Honor `prefers-reduced-motion`. Animations live on `.active` only, so they auto-pause when the menu is hidden.

---

## Part A — Shared "menu-skin" layer (IDENTICAL in all five apps)

Insert this block **once per app**, at the very end of the **first `<style>` head** (right before `</style>` on the head block, so per-app `:root` tokens above it cascade in, and so the MENU shim's later CSS can still win on layout). Mark it so it's findable and idempotent:

```css
/* ===================== SHARED MENU SKIN v1 ===================== */
/* Family look: depth + world + motion. Additive only. Layout owned   */
/* by data-growth-shim="MENU". Per-app identity = --m-* tokens below.  */

/* ---- skin token defaults (overridden per app in :root) ---- */
:root{
  --m-bg-top: var(--surface);
  --m-vignette: rgba(0,0,0,0.16);
  --m-motif: none;                 /* CSS gradients or 1 inline-SVG data-URI */
  --m-grain-opacity: 0.05;
  --m-glow: rgba(0,0,0,0.18);      /* halo behind the illustration/emblem */
  --m-cta-grad: linear-gradient(135deg, var(--accent, #888), var(--accent-dim, var(--accent, #666)));
  --m-cta-glow: rgba(0,0,0,0.35);
  --m-cta-glyph: "";               /* set "▶ " on apps whose CTA lacks one  */
  --m-tile-grad: var(--menu-tile-bg, var(--surface, rgba(255,255,255,0.08)));
  --m-tile-icon: var(--accent, currentColor);
  --m-title-shadow: none;          /* title gradients stay per-app static CSS */
  --m-grain: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* ---- background: motif + base gradient, then vignette + grain ---- */
#screen-menu, #menuScreen{
  position: relative;
  background:
    var(--m-motif),
    radial-gradient(125% 85% at 50% 16%, var(--m-bg-top) 0%, var(--bg) 72%) !important;
  background-size: cover, cover;
  background-position: center;
}
#screen-menu::before, #menuScreen::before,
#screen-menu::after,  #menuScreen::after{
  content:""; position:absolute; inset:0; pointer-events:none; z-index:0;
}
#screen-menu::before, #menuScreen::before{               /* vignette */
  background: radial-gradient(135% 105% at 50% 38%, transparent 55%, var(--m-vignette) 100%);
}
#screen-menu::after, #menuScreen::after{                 /* film grain */
  background-image: var(--m-grain); background-size: 160px 160px;
  opacity: var(--m-grain-opacity); mix-blend-mode: overlay;
}
/* keep real menu content above the two decorative layers */
#screen-menu > *, #menuScreen > *{ position: relative; z-index: 1; }

/* ---- title: optional gradient/"logo" treatment ---- */
#screen-menu .menu-logo, #screen-menu .menu-title,
#menuScreen .menu-title, #menuScreen .game-title h1, #menuScreen .menu-logo{
  text-shadow: var(--m-title-shadow);
}
/* The skin must NOT declare `background` on titles: the shorthand resets
   background-clip and (being higher-specificity) beats each app's static
   `-webkit-background-clip:text`, painting a filled gradient box. Title
   gradients are edited in per-app static CSS during Part B. */

/* ---- mini-preview: halo + gentle idle float ---- */
#screen-menu [data-menu-illustration], #menuScreen [data-menu-illustration]{
  filter: drop-shadow(0 8px 22px var(--m-glow));
  animation: m-float 5.5s ease-in-out infinite;
}
@keyframes m-float{ 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

/* ---- CTA: hero gradient, depth, slow shine, optional play glyph ---- */
#screen-menu .btn-primary, #screen-menu .btn-play, #screen-menu .menu-primary,
#menuScreen .btn-primary, #menuScreen .btn-play, #menuScreen .menu-primary{
  position: relative; overflow: hidden; border: none;
  background: var(--m-cta-grad) !important;
  box-shadow: 0 12px 28px -8px var(--m-cta-glow),
              inset 0 1px 0 rgba(255,255,255,0.28),
              inset 0 -2px 0 rgba(0,0,0,0.12) !important;
}
#screen-menu .btn-primary::before, #menuScreen .btn-primary::before{
  content: var(--m-cta-glyph); font-weight: 900; margin-right: .15em;
}
#screen-menu .btn-primary::after, #menuScreen .btn-primary::after{
  content:""; position:absolute; top:0; left:-65%; width:45%; height:100%;
  background: linear-gradient(100deg, transparent, rgba(255,255,255,0.40), transparent);
  transform: skewX(-18deg); animation: m-shine 4.8s ease-in-out infinite;
}
@keyframes m-shine{ 0%,70%{left:-65%} 88%,100%{left:135%} }

/* ---- Tier-3 icons: FILLED tinted tiles (kills the "settings" look) ---- */
#screen-menu .menu-icon-btn, #menuScreen .menu-icon-btn, #menuScreen .icon-btn{
  background: var(--m-tile-grad) !important;
  border: 1px solid var(--menu-tile-border, rgba(255,255,255,0.15)) !important;
  border-radius: 16px !important;
  box-shadow: 0 5px 12px -5px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.20);
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}
#screen-menu .menu-icon-btn svg, #menuScreen .menu-icon-btn svg, #menuScreen .icon-btn svg{
  color: var(--m-tile-icon); stroke: currentColor; stroke-width: 2.1;
}
#screen-menu .menu-icon-btn:active, #menuScreen .menu-icon-btn:active, #menuScreen .icon-btn:active{
  transform: translateY(1px) scale(.96);
  box-shadow: 0 2px 6px -3px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.20);
}

/* ---- resource pills: a little weight ---- */
#screen-menu .stat-pill, #menuScreen .stat-pill,
#screen-menu .coin-display, #menuScreen .coin-display{
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), 0 2px 6px -3px rgba(0,0,0,0.25);
}

@media (prefers-reduced-motion: reduce){
  #screen-menu *, #menuScreen *{ animation: none !important; }
}
/* =================== END SHARED MENU SKIN v1 =================== */
```

That single block is what makes them a **family**: identical depth language, identical CTA/tile/illustration treatment, identical motion grammar — all re-colored by tokens. Don't customize it per app; customize via `--m-*` in Part B.

**Family clean-ups while you're here (optional but recommended):**
* Standardize the title element so the family selector always hits — e.g. give every menu title both its existing class and a shared `class="menu-logo"`, or confirm the union selector above already covers it (it does for all five today).
* WaterSort already ships a `▶` in its CTA label — set `--m-cta-glyph:""` there so it isn't doubled; set `"▶ "` on the others.

---

## Part B — Per-app identity ("a world, not a heading")

For each app, (1) drop the `--m-*` overrides into a `:root` block placed **after** the shared skin block (the skin's own `:root` defaults are same-specificity, so whichever comes later in the file wins — per-app tokens before the skin get silently re-defaulted) and a matching set under `html[data-theme="midnight"]`, (2) enrich its branch of `injectMenuIllustration()` so the mini-preview reads as that game's world, (3) apply the one-line title flourish. Keep structure identical.

### PipeConnect — *the template; give it the strongest treatment*
Brand = the pink→indigo→cyan wordmark gradient. World = flowing pipes with a liquid trickle.
```css
:root{
  --m-bg-top:#eef3f8; --m-vignette: rgba(40,60,90,0.15); --m-grain-opacity:.04;
  --m-cta-grad: linear-gradient(135deg,#ec4899 0%,#6366f1 48%,#22d3ee 100%);
  --m-cta-glow: rgba(99,102,241,.45); --m-glow: rgba(99,102,241,.30);
  --m-cta-glyph:"▶ "; --m-tile-icon:#6366f1;
  /* title: edit .menu-logo's own static gradient in place (skin leaves titles alone) */
  /* motif: faint flowing pipe strokes (replace path data with a real pipe knot) */
  --m-motif:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='420'%3E%3Cg fill='none' stroke='%236366f1' stroke-width='14' stroke-linecap='round' opacity='0.07'%3E%3Cpath d='M40 80 H200 a40 40 0 0 1 40 40 V300'/%3E%3Cpath d='M120 420 V260 a40 40 0 0 1 40 -40 H380'/%3E%3C/g%3E%3C/svg%3E");
}
html[data-theme="midnight"]{ --m-bg-top:#161b2e; --m-vignette:rgba(0,0,0,.5); }
```
* **Emblem:** add a small interlocking-pipe knot SVG above the wordmark (new `injectMenuIllustration` branch keyed on `pipe`). Use `currentColor` + one cyan fill for the "flow".
* CTA is already the hero; let the gradient + shine carry it.

### Nonogram — *restraint with personality* (don't make it loud; "quiet logic" is the brand)
World = a faded, half-completed pixel-art picture behind the chrome + newsprint texture.
```css
:root{
  --m-bg-top:#faf6ec; --m-vignette: rgba(80,60,40,0.16); --m-grain-opacity:.10; /* paper */
  --m-cta-grad: linear-gradient(135deg,#d24a44,#a32f2b);
  --m-cta-glow: rgba(168,47,43,.40); --m-glow: rgba(168,47,43,.22);
  --m-cta-glyph:"▶ "; --m-tile-icon:#c83838;
  /* motif: a faint pixel-art picture (a real revealed nonogram, low opacity) */
  --m-motif:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cg fill='%23c83838' opacity='0.05'%3E%3Crect x='60' y='40' width='30' height='30'/%3E%3Crect x='120' y='40' width='30' height='30'/%3E%3Crect x='90' y='70' width='30' height='30'/%3E%3Crect x='60' y='100' width='90' height='30'/%3E%3C/g%3E%3C/svg%3E");
}
html[data-theme="midnight"]{ --m-bg-top:#241f1b; --m-vignette:rgba(0,0,0,.45); --m-grain-opacity:.06; }
```
* Keep the Georgia serif logo. The win here is the faded pixel-picture motif (very on-theme: nonograms *reveal* pictures) + paper grain. Think *Good Sudoku*, not a hype banner.

### Puzzle2048 — *kawaii, alive*
World = drifting pastel tiles + soft clouds (it already has cloud/pastel themes).
```css
:root{
  --m-bg-top:#fff7d6; --m-vignette: rgba(120,90,30,0.12); --m-grain-opacity:.03;
  --m-cta-grad: linear-gradient(135deg,#f6c544,#e0a91e);
  --m-cta-glow: rgba(224,169,30,.45); --m-glow: rgba(224,169,30,.28);
  --m-cta-glyph:"▶ "; --m-tile-icon:#caa12e;
  /* title: edit .game-title h1's own static gradient in place */
  --m-motif:radial-gradient(circle at 18% 22%, #ffe08a55 0 6%, transparent 7%),
            radial-gradient(circle at 82% 30%, #ffd1dc55 0 5%, transparent 6%),
            radial-gradient(circle at 70% 78%, #c9f7d255 0 6%, transparent 7%);
}
html[data-theme="midnight"]{ --m-bg-top:#23201a; --m-vignette:rgba(0,0,0,.5); }
```
* 2048 already injects a native preview grid (the shim skips `[data-menu-illustration]` for it). Give a couple of those preview tiles a slow drift/pop via the shared `m-float`, and consider a tiny mascot peeking from a corner (one SVG).

### UnblockPuzzle — *one neon hero against calm*
World = a faint block grid with the signature **red block** glowing as the one hot accent.
```css
:root{
  --m-bg-top:#e9f3ec; --m-vignette: rgba(30,60,40,0.16); --m-grain-opacity:.04;
  --m-cta-grad: linear-gradient(135deg,#56a06c,#3c7a52);
  --m-cta-glow: rgba(60,122,82,.40); --m-glow: rgba(216,64,52,.30); /* red halo */
  --m-cta-glyph:"▶ "; --m-tile-icon:#4a8a5e;
  --m-title-shadow:0 1px 0 rgba(0,0,0,.06);
  /* motif: faint board lattice; the red hero block is added in the illustration */
  --m-motif:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cg stroke='%234a8a5e' stroke-width='2' opacity='0.06'%3E%3Cpath d='M0 60H240M0 120H240M0 180H240M60 0V240M120 0V240M180 0V240'/%3E%3C/g%3E%3C/svg%3E");
}
html[data-theme="midnight"]{ /* midnight flips accent to #ff6b35 already */
  --m-bg-top:#241a33; --m-cta-grad:linear-gradient(135deg,#ff8a4c,#e0542a);
  --m-cta-glow:rgba(255,107,53,.45); --m-glow:rgba(255,107,53,.35); --m-tile-icon:#ff8a4c;
}
```
* In the `unblock` illustration branch, make the red block **glow** (`filter:drop-shadow(0 0 8px #d84034)`) and nudge it toward the exit — that micro-story is the whole game in one image.

### WaterSortPuzzle — *tropical, liquid*
World = colored liquid slowly settling in faint tubes; ocean-to-sunset depth.
```css
:root{
  --m-bg-top:#4f80b8; --m-vignette: rgba(6,20,40,0.32); --m-grain-opacity:.03;
  --m-cta-grad: linear-gradient(135deg,#5ec8f5,#2f8fd8);
  --m-cta-glow: rgba(47,143,216,.5); --m-glow: rgba(79,195,247,.35);
  --m-cta-glyph:""; /* CTA already has ▶ */ --m-tile-icon:#bfe6ff;
  /* title: edit .game-title h1's own static gradient in place */
  /* warm sunset hint at the bottom for life, over the ocean base */
  --m-motif:linear-gradient(180deg, transparent 55%, rgba(255,170,90,0.10) 100%);
}
html[data-theme="midnight"]{ --m-bg-top:#102338; --m-vignette:rgba(0,0,0,.55); }
```
* The 3-flask illustration is good — add the shared float, and a very slow "settle" on one liquid layer (translateY 1–2px loop) so it feels alive without distracting.

---

## Implementation order & commits
1. **WaterSort** ← Part A only, screenshot, get sign-off (it's the highest-contrast case for the depth layers).
2. Roll Part A to the other four.
3. Part B per app, **one commit each**: `feat(menu): game-feel skin + <App> world`.
4. Build the new **PipeConnect** menu from the same head-CSS skin + its tokens so it ships consistent from day one.

## Acceptance checklist (per app)
- [ ] Menu no longer reads as a utility app: visible background world, depth (vignette/grain/shadows), hero CTA, filled icon tiles, ≥1 subtle idle motion.
- [ ] Side-by-side, all five share the **same** layout, CTA shape, tile shape, motion grammar (family), but **different** palette + world (identity).
- [ ] Light **and** midnight both correct; 2048/WaterSort extra themes don't regress.
- [ ] Phone + 7" tablet: nothing clipped or off-center (shim layout untouched).
- [ ] Gameplay / level-select / shop / settings / overlays pixel-unchanged.
- [ ] Smooth on a low-end device; `prefers-reduced-motion` disables animation; no new runtime shim (`grep -c data-growth-shim` unchanged); skin block is idempotent (guarded/dedup-able).
- [ ] No console errors; APK/WebView still loads `game.html` offline (all assets inline, no network).

## Notes / gotchas
- **body-scoped midnight (PipeConnect):** `--m-*` defaults that reference other
  tokens (e.g. `--m-tile-grad: var(--menu-tile-bg)`) resolve at the scope where
  they're DEFINED (`:root` = html). A `body.midnight{...}` override of
  `--menu-tile-bg` is invisible to them — restate the affected `--m-*` values
  inside `body.midnight` explicitly.
- The MENU shim sets layout with `!important`; the skin only uses `!important` on `background`/`box-shadow` of the menu container + CTA + tiles, never on box-model. If anything shifts position, you've touched layout — revert that line.
- Inline-SVG data-URIs must be URL-encoded (`#`→`%23`, `"`→`'`). Keep each < ~2 KB.
- The motif/emblem SVG paths above are **placeholders to make the mechanism real** — replace with proper art (a true pipe knot, a real revealed nonogram picture, etc.). The tokens and wiring are the deliverable; the final vector art is a quick polish pass.
