# Kids shell — builder contract (Google Play Families)

Every kids-track app (`docs/portfolio_tracks.json` → `kids`) is built on the
kids shell: ABCLearning's lean single-file `game.html` (~210 KB incl. one
embedded font) plus its Families-safe Java wrapper. **A builder replaces only
the content regions**; the shell (screens router, voice, sound, parental gate,
parent area, IAP grants, sticker book, theme/i18n engine) is shared code.

```
python3 scripts/scaffold_flagship.py <App> --name "<Name>" --version-name 2.0.0 \
    --from ABCLearning --replace-iaps
```
copies the wrapper (MainActivity, manifest, gradle, res/values, res/xml) and
`game.html`, renames the package / `<title>` / `'abclearning_save'` /
`data-app-version`, resets AdMob + license IDs to placeholders, and takes the
kids IAP catalog (`remove_ads`, `full_pack`). It never injects growth shims.

## Regions (`python3 scripts/shell_region.py <App> [NAME] [--set file]`)

| Region | Kind | What goes there |
|---|---|---|
| `PALETTE` | CSS | `:root{…}` = first (light, default) theme + one `html[data-theme="<id>"]{…}` block per extra theme. Keep every shell token: `--bg --app-bg --bg-glow --bg-dots --surface --surface-2 --border --menu-tile-bg/-border/-fg --text --text-mute --ink --art-bg --accent --accent-d --accent-soft --on-accent --g-play --btn-neutral-bg --btn-shadow --on-tile --tile-1..4(-d) --guide --guide-line --good --star --star-d --shadow --scrim`. Text ≥ 4.5:1 on `--bg` and `--surface` in EVERY theme; white `--on-tile` on every `--tile-*`. Own colour family vs every sibling. |
| `CONTENT_CSS` | CSS | Styling for your screens. Tokens only, no z-index literals, `prefers-reduced-motion` is handled globally. Bottom action bars get class `game-footer`. |
| `HOME_TITLE` | HTML | Home wordmark (title stays English). |
| `HOME_TILES` | HTML | 2–4 big picture tiles (`<button class="tile cN" data-go="screen" data-arg='{…}'>` + icon + `data-i18n` label). No reading needed: icon must say it all. |
| `CONTENT_SCREENS` | HTML | `<section class="screen" data-screen="id">` per activity. Top bar = `.topbar` with `.rbtn` buttons (≥ 64 px, in-flow); helper row = `.helper` with an empty `.mascot` and `.bubble > .say-text` (the shell writes captions there). Content that is Latin text: class `latin`; boards: class `ltr` (RTL UI still mirrors chrome). |
| `APP_META` | JS | `const APP = {name, saveKey:'<low>_save', ageBand, privacyUrl (kids URL), products:[{id, price, icon, nameKey, descKey, grants:{flag:true}, includedBy}], themes:[{id,label,sw:[paper,accent]}]}`. Products == `metadata/iaps.json` == Java `VALID_PRODUCTS`. |
| `CONTENT_STRINGS` | JS | `const CONTENT_I18N = {en:{…}, ar:{…}, …13}` merged into `window.GAME_I18N` at boot. Placeholders `{x}`; a var passed as `{t:'spoken', c:'caption'}` is spoken by the English voice (letter names, words), a plain string in the UI language. Required keys: `mascotName`, tile labels, every prompt you speak, `p_full`, `p_full_d`, `progressLine`, sticker tab labels. |
| `CONTENT_DATA` | JS | Your content tables + `window.MASCOT_SVG` (class `pip` with `.p-all .p-eyes .p-beak .p-wl .p-wr` groups for idle/blink/talk/hop), `window.STICKER_PAGES` (`[{id,label,tab,items:[{id,ghost,label}]}]`, one page `special:true` for round rewards) and `window.stickerSvg(id)`. Original art only (own SVG). |
| `CONTENT_ENGINE` | JS | An IIFE using only `window.KIDS`: `K.defineScreen()` per screen (incl. `'home'` to set the bubble + `#nextChip`), actions in `K.acts`, and the hooks below. |

### Shell API — `window.KIDS` (`K`)

| Call | Does |
|---|---|
| `K.defineScreen(id, {enter(params, isRefresh), leave(), banner, back})` | `banner:false` on every activity (tracing, games); `back` = id, `[id, params]` or fn. `enter(p, true)` = re-render after language / purchase change — keep state. |
| `K.go(id, params)` / `K.back()` / `K.current()` / `K.refresh()` | Router (also stops speech, closes popups, syncs the banner). |
| `K.acts[name] = (btn, ev) => …` | Handler for `data-act="name"` (event delegation; never inline `onclick`). `data-go`/`data-arg` navigate without code. |
| `K.sayT(key, vars)` → `Promise<bool>` | Speak an i18n template (UI-language voice if installed, else English) + caption. Resolves `true` when finished, `false` if interrupted — chain only on `true`. |
| `K.sayEn(text, caption)` / `K.say(parts, caption)` / `K.stopVoice()` | English content speech / mixed parts `[{t, c, l}]`. |
| `K.sfx(name, x)` | WebAudio: `tap pop yes soft stroke tick(x 0..1) sparkle done whoosh`. `soft` is the only "wrong" sound — gentle, never a buzzer. |
| `K.celebrate()` / `K.mascot('happy'\|'think')` | Confetti + success chord + hop / head tilt. |
| `K.awardSticker(id)` / `K.awardNextSpecial()` / `K.hasSticker(id)` | Queue the reveal popup (one at a time). |
| `K.full()` / `K.adsRemoved()` / `K.askGrownUp()` | Entitlements; locked content → "Ask a grown-up" card → gate → parent shop. Never show a price to the child. |
| `K.save` / `K.persist()` | Live save; content data lives under `save.progress` only. `saveVersion` + `migrateSave()` are shell-owned. |
| `K.t(key, vars)`, `K.lang()`, `K.setTheme(id)`, `K.esc(s)`, `K.toast(msg)` | Helpers. |

Content hooks (assign on `window`): `homeNext()` (bubble chip), `mascotTap()`,
`progressText()` (parent area line), `stickerTap(id)`.
Test adapter: `window.gGame = {state, persist}` (for `scripts/runtime/*`; not
a growth shim).

## Parental gate
`Gate.open(cb)` shows "Grown-ups only": press **and hold** (1.5 s) the answer to
a×b with a,b ∈ 6..9 among four choices. A wrong answer closes the gate (no
retry on the same question). Passing opens the parent area for that visit only
(`leave()` re-locks). **Every** purchase, restore and external link goes
through `gatedNative(method, arg)`, which refuses (and opens the gate) unless
`Gate.ok()`. The Java side allow-lists `openUrl` hosts and only reaches the
store via `purchase(id)`. Never call `Android.purchase/openUrl/...` directly —
`check_families_compliance.py` blocks it.

## IAP pattern (kids catalog)
`full_pack` ($4.99: unlocks all premium content + removes ads) and
`remove_ads` ($2.99), both non-consumable (`CONSUMABLE_PRODUCTS` empty,
acknowledged via `acknowledgePurchase`), no subscriptions, no coins.
`window.onPurchaseSuccess(id)` applies `APP.products[i].grants` idempotently
(restore replays it); unknown SKUs → `localStorage.pendingGrants`, replayed on
boot. Java hides the banner itself for `AD_FREE_PRODUCTS`. Keep a generous
free set (ABC: A–J + one game) — free must feel complete, not a demo.

## Voice + audio
Android WebView has no `speechSynthesis`, so MainActivity exposes TTS:
`ttsAvailable() / ttsHasLanguage(tag) / speak(text, tag, rate, id) /
stopSpeaking()` → `window.onSpeakDone(id)`, `window.onTtsReady(ok)`. The shell
falls back to `speechSynthesis` in browsers and to caption-only pacing when no
voice exists (parent area shows a "install a voice" note). Voice on/off + slow
speed are parent settings. SFX are synthesized; no audio files, no network.

## Families checklist (gate: `python3 scripts/check_families_compliance.py <App>`)
- No notifications: no POST_NOTIFICATIONS / BOOT / alarm permission, no receiver, no NotificationHelper; notification bridge methods are no-ops.
- AdMob only (no mediation adapters), banner only, child-directed: `RequestConfiguration` TFCD + TFUA + `MAX_AD_CONTENT_RATING_G` **before** `MobileAds.initialize`; AD_ID permission stripped; ads never initialised once removed; banner hidden on activities, gate, popups and the parent area. AdMob console: mark the app child-directed.
- No interstitial / rewarded / app-open ads, no Play Games, no Firebase, no sharing, no accounts, no chat, no analytics, nothing leaves the device.
- Cross-promo only to other live Pegasus KIDS apps (`KIDS_PROMO_PACKAGES`, empty by default) and only behind the gate.
- Privacy URL `https://pegasusgames-creator.github.io/privacy-kids.html`; `metadata/app_info.json`: `"kids_program": true`, `"target_age_band": "3-8"` (+ `target_audience_min_age/max_age`) — **this is the kids flag** (also read by `gen_translations.py` / `pre_publish_check.py`).
- Content rating for children; no gambling mechanics; no timers that pressure, no failure states that punish, no lives/coins.
- Listing written for parents, no emoji, honest about language (ABC: "letters stay English A-Z in every language") and about the device TTS voice.

## Per-app checklist
1. Scaffold (above); `python3 scripts/migrate_to_per_app_keystores.py --app <App>` if it has no keystore.
2. Replace every region; change `WEBVIEW_BG_COLOR` (MainActivity) + `windowBackground` (styles.xml) to your `--bg`; no other wrapper edits.
3. `APP_META`: name, `saveKey` (scaffold renames it), products text keys, themes.
4. Strings for all 13 languages (`en ar de es fr hi id it ja pt tr uk zh`), keys == en.
5. `metadata/`: kids flag + age band, kids privacy URL, `iaps.json` reworded (≤200 chars) for your content, 13 locales, `screenshot_headlines*.json`, `app_identity.md` (4 archetypes).
6. Store art (`icon_512_playstore.png` RGB, `icon_1024_appstore.png`, `feature_graphic_1024x500.png`) from your own shapes → `python3 scripts/sync_launcher_icons.py <App>` and regenerate `mipmap-*/ic_launcher_foreground.png` + `ic_launcher_background` colour (adaptive icon).
7. `test/screenshot_taps.json` (11 distinct activity states via `KIDS.go(...)`), `test/runtime_check.js` (copy ABCLearning's: real pointer input, gate refusal, purchase/restore, forbidden-call scan), `test/register.json`.
8. Verify: `node scripts/runtime/smoke_all.js <App>`, `node <App>/test/runtime_check.js`, `node scripts/runtime/iap_grants.js <App>`, `python3 scripts/java_compile_check.py <App>`, `python3 scripts/check_families_compliance.py <App>`, `python3 scripts/gen_store_paste.py <App>`, `python3 scripts/pre_publish_check.py <App>`; drive it headlessly at 360×640, 412×915, 800×1280 in en / ar (RTL) / ja and look at every screen in every theme.
