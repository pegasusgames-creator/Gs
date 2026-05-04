# Translations & Localization

Pegasus Games ships in **11 locales**: English baseline plus 10 markets
chosen by Play Store ROI (eCPM × audience size × market growth).

This doc covers:
- Which locales we support and why
- Store listing localization (the high-ROI lift)
- In-game string localization (the higher-effort lift)
- Title-stays-English rule
- Character limits per locale (some translations grow 30-50%)
- Kids program apps — extra rules
- The Russian-Ukrainian decision

---

## 1. The 11 locales

In the order they appear in metadata folders (by ISO code):

| Code | Language | Region | Why |
|---|---|---|---|
| `en-US` | English | United States | Baseline. Hand-written, source of all translations. |
| `de-DE` | German | Germany | High eCPM (~$2-3 ARPDAU on casual puzzles). Disciplined audience. |
| `es-419` | Spanish | Latin America | 400M+ Play Store users. High install volume. |
| `fr-FR` | French | France + Africa | Western Europe + Francophone Africa. |
| `hi-IN` | Hindi | India | Fastest-growing Play Store market. Lower eCPM but huge volume. |
| `id-ID` | Indonesian | Southeast Asia | Very high engagement on casual puzzles. |
| `it-IT` | Italian | Italy | Top-15 Play Store revenue country. Reliable casual gaming. |
| `ja-JP` | Japanese | Japan | Highest ARPU per user globally. Difficult market but rewarding. |
| `pt-BR` | Portuguese | Brazil | Huge casual gaming market, high install velocity. |
| `tr-TR` | Turkish | Turkey + MENA | Gateway to wider Middle East / North Africa traffic. |
| `uk-UA` | Ukrainian | Ukraine | Pegasus Games is a Ukrainian publisher. Home market is non-negotiable. |

### About Russian

We deliberately exclude `ru-RU` from the locale list. Pegasus Games is a
Ukrainian publisher; supporting Russian as a Play Store locale during the
ongoing war is a values choice. Some Russian-speakers in Ukraine,
Belarus, Kazakhstan, and EU diaspora communities install apps from
non-Russian locales (most often `en-US` or `uk-UA`), so the audience loss
is real but limited. Italian fills the slot vacated by Russian's
exclusion.

If, in the future, you change this stance, add `ru-RU` back via the
TRANSLATIONS.md update — don't ship a one-off "this app has Russian"
because then translation maintenance fragments per app.

---

## 2. What gets translated

Two scopes, separate decisions per app:

### Scope A — Store listing translations (REQUIRED for every app)

Every app ships with translations for these fields in all 11 locales:

- `short_description.txt` (≤80 chars in target language)
- `subtitle.txt` (≤30 chars in target language)
- `full_description.txt` (≤4000 chars in target language)
- `keywords.txt` (≤100 chars, comma-separated, target-language search terms)
- `release_notes.txt` (≤500 chars, target language)

These are stored at:
```
<App>/metadata/<locale>/short_description.txt
<App>/metadata/<locale>/subtitle.txt
<App>/metadata/<locale>/full_description.txt
<App>/metadata/<locale>/keywords.txt
<App>/metadata/<locale>/release_notes.txt
```

The Play Console upload flow accepts these directly (it expects exactly
this folder structure when you upload via the Publishing API or via
Fastlane).

### Scope B — In-game string translations (REQUIRED from app #3 onward)

For new apps starting from the 3rd app shipped (after WaterSort and the
next), every UI string in `game.html` must be externalized to a per-locale
JSON file:

```
<App>/android/app/src/main/assets/i18n/
  en.json
  de.json
  es.json
  fr.json
  hi.json
  id.json
  it.json
  ja.json
  pt.json
  tr.json
  uk.json
```

Each JSON is a flat key-value map:
```json
{
  "menu.play": "Play",
  "menu.daily_challenge": "Daily Challenge",
  "menu.levels": "Levels",
  "menu.shop": "Shop",
  "menu.settings": "Settings",
  "level.complete": "Level Complete!",
  "level.par_label": "Par",
  "level.moves_label": "Moves",
  "modal.no_lives_title": "Out of Lives",
  ...
}
```

The game's bootstrap reads `navigator.language` and loads the matching
locale, falling back to `en` for unsupported languages. Implementation
guidance is in `QUALITY_PLAYBOOK.md` §1.4 (to be added — see SHIP_GAME.md
Phase 1 for the immediate per-app instruction).

WaterSort and BallSortPuzzle don't need to be retrofitted unless they
ship a content update — at which point the in-app strings get
externalized as part of that update.

---

## 3. Title stays in English

The app's `<App>/metadata/en-US/title.txt` value is **the title for all
locales**. Do NOT translate the title.

Reasons:
- Casual puzzle game titles have become genre proper nouns on Play Store
  ("Water Sort Puzzle", "Block Blast", "Sudoku Master"). Localizing
  these loses search ranking in every market.
- Users in non-English markets searching for puzzle apps often search
  English genre names by habit (Hindi-speaking user types "block
  puzzle" not "ब्लॉक पहेली").
- Maintenance: 100 apps × 11 locales × evolving titles is a maintenance
  hellscape. One title globally is sane.

**Per-locale title.txt files should NOT exist.** The Play Console
listing reuses the en-US title for every other locale. The translation
generator script knows to skip title.txt.

The ONE exception: if Google Play's locale-specific listing requires a
title field to be filled (it does), `gen_translations.py` writes a
`title.txt` in each locale that contains the English title verbatim.
This satisfies the API requirement without actually translating.

---

## 4. Character limits per locale

Translations grow. Some examples of "Pour and sort the colored water"
(31 chars):

- de-DE: "Gieße und sortiere das farbige Wasser" (38 chars, +23%)
- fr-FR: "Versez et triez l'eau colorée" (29 chars, -6%)
- ja-JP: "色付きの水を注いで分類" (11 chars, -65%)
- ru-RU: "Наливай и сортируй цветную воду" (32 chars, baseline)
- de-DE compound words can balloon — single concept "Daily Challenge"
  becomes "Tägliche Herausforderung" (24 chars vs 15)

Implications for our store listing fields:

- **short_description.txt (limit 80 chars):** German, Russian if added,
  and Hungarian frequently overflow. Hindi often fits because Devanagari
  is denser. Japanese always fits.
- **subtitle.txt (limit 30 chars):** Tightest constraint. Many
  translations need rewriting rather than direct translation to fit. The
  script must validate and flag overflows.
- **full_description.txt (limit 4000 chars):** Almost never an issue.
  German might come close on long apps; just use shorter sentences.
- **release_notes.txt (limit 500 chars):** Easy to fit if you keep
  English notes under ~400 chars.

The `gen_translations.py` script validates each translation against the
target's character limit and refuses to write fields that overflow.
When that happens, it asks Claude Code (or the human) to write a
shorter version manually.

### Common-overflow languages to watch

When translating, expect overflow most often in:
- de-DE (compound words)
- fr-FR (article-heavy, e.g., "le jeu de sort des couleurs")
- it-IT (similar to French)
- es-419 (slightly longer than English)

Compact languages (rarely overflow):
- ja-JP (kanji density)
- hi-IN (Devanagari density)
- en-US (baseline)
- id-ID (similar to English length)

---

## 5. Kids program apps — extra rules

Apps in Google Play's Designed-for-Families program have stricter
localization requirements. Per Play Store policy:

### Kids-specific localization rules

1. **Kids apps must support at least 4 locales from day 1.** Pegasus's
   minimum-4 set is en-US, es-419, pt-BR, fr-FR (covers majority of Play
   Store family households). Other locales can be added later but the
   first 4 are required at submission.

2. **Translations must be reviewed for child-appropriateness.** Some
   words that are fine in adult apps are inappropriate for kids in some
   languages. Examples: certain Spanish slang for "quick", certain Hindi
   words for "dumb" used colloquially in adult apps. Machine-translation
   alone is not safe — for Kids apps, the translated `full_description`
   and any in-game UI strings must be reviewed by a native speaker
   before submission.

3. **Per-locale privacy policy:** Kids apps must link to a Kids-specific
   privacy policy. Pegasus has one at
   `https://pegasusgames-creator.github.io/privacy-kids.html`. This URL
   is the same across all locales — but the URL is what's localized in
   Play Console's Kids program form, even though the content is English.

4. **Per-locale content review:** Kids apps undergo Google review per
   locale, not just per app. A Kids app submitted in 11 locales gets
   reviewed 11 times. Plan release timing accordingly.

5. **No emoji in Kids app translations.** Adult apps can have emoji in
   `full_description` (sparingly). Kids apps cannot — Google's content
   reviewers flag emoji use as "potentially advertising-like" for Kids.

6. **Voice in Kids translations:** all 11 translations of a Kids app
   should use the V7 (Educational warm) voice from APP_ARCHETYPES §3.
   Not V4 (snarky) or V6 (enthusiastic arcade). The voice MUST be
   consistent across locales for Kids apps.

### Kids app translation workflow

For a Kids app, `gen_translations.py` flags itself as Kids mode (reads
the `target_audience_min_age` from `metadata/app_info.json`; if the
app is in the Kids program, mode = kids). In Kids mode:

- Only the 4 minimum locales are generated by default
- Each generated translation prefixes a header comment in the file:
  `# KIDS APP — REVIEW BY NATIVE SPEAKER BEFORE SHIPPING`
- The `pre_publish_check.py` blocks the build if any Kids-app
  translation file still has that header

Native review can be:
- A trusted bilingual friend / family member
- Paid Fiverr review ($5-15 per language for short copy)
- Native speaker on language-exchange apps

Don't ship Kids apps with unreviewed machine translations. The Play
Store Kids program review will catch awkward phrasings and reject.

---

## 6. Translation maintenance discipline

Once 11 locales are populated for an app, edits to the English baseline
must propagate to all other locales. Failure modes:

1. **Stale translations.** You edit `en-US/short_description.txt` to
   add a new feature mention. Other locales still describe the old
   version. Fix: run `gen_translations.py <App> --update` to find
   diverged fields.

2. **Drift over time.** App #1's German translation says "Tägliche
   Herausforderung" for "Daily Challenge"; app #2 says "Tägliches
   Rätsel"; app #3 says "Tagesspiel". The portfolio's German vocabulary
   becomes inconsistent. Fix: maintain `<repo>/scripts/translation_glossary.json`
   with stable translations for common app concepts (Daily Challenge,
   Level Complete, Out of Lives, etc.) and force `gen_translations.py`
   to use them.

3. **Stuck on a bad translation.** A reviewer once translated a key
   string oddly, you didn't catch it, now it's been live for 6 months
   and changing it might affect ASO. Fix: per-locale A/B testing on
   listing changes. Play Console supports this natively.

The glossary file is referenced by `gen_translations.py` during
generation and applied as a post-process: any glossary key found in a
translated string is replaced with the canonical version. Keeps voice
and terminology consistent across the portfolio.

---

## 7. When to translate vs when to skip

Always translate:
- All 11 store-listing locales for every app from day 1
- All 11 in-game locales for new apps from app #3 onward (per Scope B)

Sometimes skip in-game translation:
- Pure tools (calculator, timer, ruler) where UI is 5 buttons total —
  English is fine, users expect English in tools
- Single-word-input games (Wordle clone) where the dictionary is
  language-specific anyway
- Apps that ship as a quick experiment (week-1 throwaway test) — but
  store listing always gets translated

Never skip:
- Store listing translation in any of the 11 locales for any app you
  publish
- Store listing for Kids apps in any of the 4 minimum Kids locales
- In-game translation for any app entering the Kids program

---

## 8. Translation cost

For reference, doing all 11 locales for an app's store listing using
machine translation:
- Time: ~3 minutes via `gen_translations.py` API call
- API cost: ~$0.05-0.20 per app (negligible)

For 100 apps: ~$5-20 API spend, ~5 hours total wall-clock.

Hand-translation cost (Fiverr, professional native review):
- Per locale: $15-50 per app for short copy
- Per app for all 10 non-English locales: $150-500
- For 100 apps: $15k-50k

The phased approach: machine-translate everything, then commission
human review only for apps that start earning. For an app earning
$1000+/month in a specific locale, $30 of human review pays for itself
the same week.

---

## 9. How translations integrate with the workflow

- **`gen_translations.py <AppName>`** — runs at SHIP_GAME.md Phase 4.5
  (after Phase 4 hand-writes English listing). Generates all 11
  locale folders for store listing.
- **`pre_publish_check.py`** — verifies every shipped app has all 11
  locales populated for store listing. Warns (not blocks) if any are
  missing during the migration period; blocks for new apps from
  archetype-system rollout onward.
- **`gen_handoff.py`** — RELEASE_HANDOFF.md tells the user that Play
  Console requires uploading each locale's listing separately and
  walks through the bulk-upload approach.

In-game translation:
- The `i18n/` folder structure under `assets/` is part of
  SHIP_GAME.md Phase 1 (game.html scaffolding).
- `pre_publish_check.py` verifies all 11 `i18n/*.json` files exist
  for new apps and have key parity with the English file.
