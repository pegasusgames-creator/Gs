# Utility shell — builder contract

Every utility-track app (`docs/portfolio_tracks.json` → `"utility"`: tools,
calculators, trackers, timers, reference guides, music tools, party decks,
creative toys, health logs) is built on the **utility shell** — HabitTracker's
`game.html` (~266 KB: one embedded Latin font 33 KB, 13-language strings
~105 KB, code ~125 KB). The shell is finished shared code: app bar, bottom
tabs, sheets/dialogs/toasts, onboarding, Settings, themes, i18n + RTL, IAP,
ads cadence, reminders, backup/restore, accessibility. **A builder replaces
only the tool.** Never read the whole file — read/replace one region:

```
python3 scripts/shell_region.py <App>                 # list regions + sizes
python3 scripts/shell_region.py <App> TOOL_CORE       # print one
python3 scripts/shell_region.py <App> TOOL_CORE --set core.js   # replace (markers kept)
```
Markers: CSS `/*@@REGION X*/…/*@@END X*/`, JS `//@@REGION X … //@@END X`.

## Scaffold

```
python3 scripts/scaffold_flagship.py <App> --name "<Store Name>" --version-name 2.0.0 \
    --from HabitTracker --replace-iaps [--pkg com.pegasusgames.<x>] [--reminder "…"]
cp HabitTracker/android/app/src/main/res/xml/{backup_rules,data_extraction_rules}.xml <App>/android/app/src/main/res/xml/
cp HabitTracker/android/app/src/main/res/drawable/ic_stat_check.xml <App>/android/app/src/main/res/drawable/
```
The two `cp` lines are needed until `scaffold_flagship.py` WRAPPER_FILES lists
those three resources (the manifest and NotificationReceiver reference them).
The scaffold renames the package, `'<pkg>_save'` key, `<title>`, and
`data-app-version`; the Java reads the app name from the manifest label.
Then set your `APP` config and replace the tool regions.

## Regions you own

| Region | What goes there |
|---|---|
| `FONT` | One `@font-face` (base64 woff2, Latin subset; data URI because file access is off). Swap the family per app for identity (`localize_google_fonts.py` approach); keep ≤ ~35 KB. Don't print it. |
| `PALETTE` | `:root` Daylight tokens + `html[data-theme="dark"]` + `html[data-accent="<id>"]` (light and dark) for each accent in `APP.accents`. Keep the names: `--bg --app-bg --surface --surface-2/3 --text --text-mute --text-faint --border --border-strong --accent --accent-2 --accent-soft --on-accent --g-play --btn-neutral-bg --danger --success --menu-tile-*`. Light default, own colour family (`scripts/app_themes.py`), every `--text*` ≥ 4.5:1 on `--bg`/`--surface`, `--on-accent` ≥ 4.5:1 on both gradient stops. |
| `TOOL_CSS` | Styles of the tool's screens. Tokens only, `var(--z-…)` only, `prefers-reduced-motion` is handled by the shell (`.reduce-motion`). Use logical properties (`padding-inline`, `inset-inline-end`) so Arabic RTL works. |
| `APP_CONFIG` | `const APP = {name, pkg, saveKey, tabs:[{id,icon,label}], onboarding:[{art,title,body}], proFeatures:[keys], accents:[{id,sw,pro}], reminder:{body,h,m}|null, interstitials, prices}`. 1 tab ⇒ no bottom nav. `reminder:null` for tools that must not nudge (calculators, converters — QUALITY_PLAYBOOK §11.7). |
| `TOOL_STRINGS` | `const TOOL_I18N = {en:{…}, ar:{…}, … zh:{…}}` — every tool string in all 13 languages (`en ar de es fr hi id it ja pt tr uk zh`), keys exactly as in `en`. Keys are 2-space indented (`check_lang_picker`). |
| `TOOL_ICONS` | `HICON` (your 24×24 stroke glyphs), `ART` = `{emblem, ob1, ob2, ob3}` inline SVGs (use `var(--accent)` etc. so they theme). Draw your own; no icon fonts. |
| `TOOL_CORE` | The tool. Contract below. |

Shell-owned (don't edit): shell CSS, `#app` skeleton, `GAME_I18N` (shell strings),
`LANG_NAMES`, shell runtime, boot. Fix shell bugs in HabitTracker first, then
port (bug-class rule).

## TOOL_CORE contract

```js
const TOOL = {
  defaults() { return {...} },            // initial S.tool (your whole data model)
  migrate(tool, fromVersion) { return tool },   // normalise/upgrade; never drop data
  validateImport(tool) { return true },   // accept a backup's .tool?
  screens: { <tabId>: { title(p), subtitle?(p), actions?(p) -> [{icon,label,act,arg,tint}],
                        render(el, p), onLeave?(p) }, … },   // one per APP.tabs id + pushed screens
  csv?() -> string,            // Pro "Export CSV" row appears when defined
  settingsHtml?() -> html,     // your Settings group (rows via sRow / seg / sSwitch)
  syncReminders?(),            // re-arm your own reminder slots (boot + language change)
  onBoot?(), onNewDay?(), onGrant?(id), afterOnboarding?(),
};
```
Taps: every control is `<button data-act="name" data-arg="…">`; register
`ACT.name = (el, ev) => {…}`. `<select/input data-change="x">` → `CHANGE.x`,
`data-input="x"` → `INPUT.x`. No inline `onclick`. Re-render with
`UI.refresh()`; for animated controls update the element in place (see
`paintRow` in HabitTracker).

Shell API: `S` (live save; your data in `S.tool`), `persist()`,
`t(key, vars)` (`{name}` placeholders; plurals via `key_one/_few/_other` +
`Intl.PluralRules`), `fmtNum/fmtPct/fmtDate/fmtTime/weekdayName` (Intl, per
language), `dkey/pkey/today/todayKey/addDays` (local days, noon-safe),
`UI.tab(id) / UI.go(id, params) / UI.back() / UI.refresh()`,
`UI.sheet({title, body, foot, full, cls, onClose})`, `UI.closeLayer()`,
`UI.confirm({title, body, ok, danger}) → Promise<bool>`,
`UI.toast(msg, {action, onAction})` (use for **Undo** after every destructive
action), `UI.empty({art|icon, title, body, cta, act})`, `icon(name, size)`,
`sRow/sSwitch/seg`, `haptic('tap'|'success'|'reject')`, `announce(text)`,
`esc()`, `clone()`, `uid()`, `reducedMotion()`.
Screenshots/tests: `window.shellLoadState(saveObject)` replaces the live state
without a reload (a reload's pagehide-persist would overwrite a localStorage seed).

## Monetization (one catalog for every utility)

* `metadata/iaps.json` = `remove_ads` ($2.99) + `pro_lifetime` ($5.99), both
  non-consumable, no subscriptions; Java `VALID_PRODUCTS` matches,
  `CONSUMABLE_PRODUCTS`/`SUBSCRIPTION_PRODUCTS` empty, `AD_FREE_PRODUCTS` both.
  Reword only the descriptions (≤ 200 chars, name your Pro features truthfully).
* `window.onPurchaseSuccess(id)` → `grant(id)`: `remove_ads` → `S.removeAds`;
  `pro_lifetime` → `S.pro` + ad-free. Unknown ids → `pendingGrants`,
  `replayPendingGrants()` at boot. Restore = Settings row → `Android.restorePurchases()`.
  Gate Pro features with `if (!Pro.require('reason_key')) return;` (opens the
  paywall with that reason). `isPro()`, `adsRemoved()`.
* Ads: banner always unless `adsRemoved()`. Interstitial **only** via
  `Ads.naturalBreak('why')` at a natural break (saved a record, closed a
  detail, finished a session/round) — the helper enforces: not in the first
  session, ≥ 2 breaks and ≥ 3 min apart, never for owners (Java adds a 3-min floor).
  Never after every action, never on app open.
* Rewarded is opt-in only: `Ads.rewarded('theme_trial', cb)` (24-h Pro accents).
  Any new type must be added to Java `VALID_REWARD_TYPES`.

## Reminders, data, accessibility

* `Reminders.enable(slot, h, m, daysMask, title, body)` asks POST_NOTIFICATIONS
  **in context** (only after the user switches a reminder on) and schedules;
  `Reminders.set/cancel`. Slot 0 = the app-wide daily reminder (Settings row,
  shown when `APP.reminder`); slots 1–63 are yours (persisted in Java, re-armed
  after reboot/update). daysMask bit 0 = Sunday. No streak-at-risk / guilt nudges.
* Data is local only (WebView storage + Android Auto Backup rules). Settings →
  Back up shares/copies `{app, kind:'backup', v, settings, tool}` JSON; Restore
  pastes it back (confirm + Undo); purchases are never imported. Erase all data
  has confirm + Undo.
* Accessibility: 48 px targets, `aria-label` on icon buttons, `aria-pressed`
  on toggles, live region for toasts, system font scale × in-app Text size,
  reduced motion, RTL (`dir` set from language), Dark theme free.

## Per-category guide

| Category | Shape | Notes |
|---|---|---|
| Calculators / converters | 1 tab (nav hidden) or Calculator·History; `reminder:null`; history list with clear + Undo | Pro: history export (csv), extra units/themes, no ads. Natural break = after the 3rd saved result, never per keystroke. Format with `fmtNum` (locale separators). |
| Trackers / logs (expense, mood, water, sleep, workout) | Today/Log · History/Calendar · Stats | Copy HabitTracker's calendar/bars helpers; CSV export is the Pro hook; reminders opt-in. |
| Timers (Pomodoro, fasting, chess clock, stopwatch) | Timer · Presets · History | Keep the screen awake only while running (needs a wrapper flag — ask the lead); end-of-timer = local notification via a `Reminders.set` one-off slot; natural break = after a completed session. |
| Reference / guides (cocktails, chords, phrasebook, solar system) | Browse · Search · Favorites | Content lives in TOOL_CORE as data; facts must be checked (content gate script). Translate UI strings; content may stay English if the listing says so. |
| Party decks (truth or dare, charades, would you rather) | Play · Decks · Players | Big type, pass-the-phone flow, no ads mid-round (break = between rounds). Content gate: no duplicates, family-safe default deck, mature decks behind a toggle + rating. |
| Music / audio tools (metronome, piano, drum machine, white noise) | Tool · Presets | WebAudio synthesis only (no files), start on a user gesture, stop on `onAppPause`. Latency-sensitive: avoid re-rendering while playing. |
| Creative toys (kaleidoscope, slime, fireworks, zen garden) | Canvas full-screen, 1 tab | Respect `reducedMotion()`; save/share an image via `Android.shareImage` (text fallback today). |
| Health logs (BP, blood sugar, medication, period, BMI, sobriety) | Log · History · Stats | **No medical claims, no diagnosis, no dosing advice**; show "not medical advice — talk to a professional" in onboarding + listing. Units/locales exact. Play **Health apps declaration** is required for health/medical-adjacent apps (Play Console → App content); Data Safety still "not collected" because data stays on device. Kids never. |

## Per-app checklist

1. Scaffold (above) + the 3 resource copies; own keystore (`migrate_to_per_app_keystores.py --app <App>`).
2. `APP_CONFIG`, `PALETTE` (distinct family), `FONT` (optional swap), `TOOL_*` regions; `grep -n "Habit\|habit" game.html` outside your regions must be empty.
3. Strings in all 13 languages; no `__i18nMissing` at runtime (Arabic RTL + Japanese checked).
4. `metadata/` 13 locales (title English), JSON files, `iaps.json` descriptions, `app_identity.md` (4 archetypes; utilities default to Layout I), headlines ×3.
5. Store art with PIL (own focal element) → `python3 scripts/sync_launcher_icons.py <App>`.
6. `test/screenshot_taps.json` (11 real-use states via `shellLoadState` + `UI.tab/UI.go`, no Settings/paywall/onboarding), `test/runtime_check.js` (copy HabitTracker's, drive your tool's real flows), `test/register.json` (gate + app_theme).
7. Verify: `python3 scripts/check_utility_shell.py <App>`, `node scripts/runtime/smoke_all.js <App>`, `node <App>/test/runtime_check.js`, `node scripts/runtime/iap_grants.js <App>`, `python3 scripts/java_compile_check.py <App>`, `python3 scripts/gen_store_paste.py <App>`, `python3 scripts/pre_publish_check.py <App>`; drive the UI at 360×640, 412×915, 800×1280 in light/dark/accent + ar + ja and look at the PNGs.
