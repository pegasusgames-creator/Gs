# IAP Catalog — Play Console form-ready content

Canonical IAP information for every Pegasus Games app. This is the
**source of truth** for what to paste into Google Play Console when
creating in-app products and subscriptions. Read this with `CLAUDE.md`
and the per-app `metadata/iaps.json`.

When shipping a new app, the `iaps.json` listed product IDs MUST exactly
match the IDs declared in `MainActivity.java`'s `VALID_PRODUCTS` set.
The titles and descriptions in this file are designed to fit Play
Console's character limits and to match what the in-game shop screen
shows the user.

**`description` is mandatory in every `iaps.json` entry** (one-time
products AND subscriptions). Play Console's "Опис" / Description field
is required when creating any IAP and accepts up to 200 characters. The
canonical text per product ID is the table below; copy it verbatim into
`iaps.json`. `init_app_metadata.py` writes the canonical descriptions for
new apps automatically, and `pre_publish_check.py check_iaps_descriptions`
blocks any app whose `iaps.json` is missing a description, exceeds 200
chars, or drifts from the catalog text.

---

## Play Console form structure (one-time products)

The "Create one-time product" wizard has two steps:

### Step 1 — Product details
| Field | Limit | What to enter |
|---|---|---|
| Product ID (Ідентифікатор продукту) | ≤136, lowercase+digits+`_`+`-`, immutable | exact ID from `iaps.json` |
| Tags (Теги) | ≤20 chars each, optional | leave blank |
| Default language | — | English (United States) — en-US |
| Name (Назва) | ≤55 | from the table below |
| Description (Опис) | ≤200 | from the table below |
| Tax category | — | keep default: *Digital goods sale* |
| Age restrictions (Вікові обмеження) | — | leave blank (matches IARC "Everyone") |
| Payment restrictions by location | — | keep default: not restricted |

### Step 2 — Purchase variant + Availability and pricing
| Field | What to enter |
|---|---|
| Purchase variant ID (Ідентифікатор варіанта покупки) | `base` |
| Purchase type (Тип покупки) | `Buy` (one-time purchase, NOT rental) |
| Tags | leave blank |
| Availability (Доступність) | All regions (Усі регіони) |
| Price | from the table below — set in USD, Play auto-converts to local currencies |

### Consumable vs Non-consumable
Asked during product creation (or under "Additional capabilities"). Each
product in the table below is tagged with the correct type.

- **Consumable** — user can re-purchase after using (coin packs, lives,
  hints, time-limited boosts, starter pack)
- **Non-consumable** — purchased once, persistent forever (remove ads,
  unlimited lives, unlimited undos)

---

## Canonical one-time product catalog

These are the standard products shared across the portfolio. Apps may
ship a **subset** of this catalog depending on what their `game.html`
shop offers — never invent new product IDs without first declaring them
in `MainActivity.java` `VALID_PRODUCTS` and in `iaps.json`.

| # | Product ID | Type | Price (USD) | Name (≤55) | Description (≤200) |
|---|---|---|---|---|---|
| 1 | `remove_ads` | Non-consumable | $2.99 | Remove Ads | Permanently removes all banner and interstitial ads. Rewarded ads remain available so you can still earn free coins and lives. |
| 2 | `coins_small` | Consumable | $0.99 | 100 Coins | Adds 100 coins to your wallet. Spend coins on hints, extra moves, and unlocking new themes. |
| 2b | `coins_medium` | Consumable | $4.99 | 600 Coins | Adds 600 coins to your wallet. Spend coins on hints, boosters, extra tubes, and unlocking new themes. |
| 3 | `coins_large` | Consumable | $2.99 | 500 Coins | Adds 500 coins to your wallet. Best value coin pack — spend on hints, extra moves, and unlocking new themes. |
| 3b | `coins_mega` | Consumable | $9.99 | 1400 Coins | Adds 1400 coins to your wallet. Our largest coin pack — spend on hints, boosters, extra tubes, and themes. |
| 4 | `five_lives` | Consumable | $0.99 | 5 Lives | Instantly refills your hearts to the maximum so you can keep playing without waiting for them to recharge. |
| 5 | `unlimited_lives_1h` | Consumable | $1.99 | 1 Hour Unlimited Lives | Play with unlimited lives for one full hour. Perfect for a long puzzle session without any interruption. |
| 6 | `unlimited_lives_forever` | Non-consumable | $4.99 | Unlimited Lives Forever | Never run out of lives again. Play as many levels as you want, whenever you want, with no waiting. |
| 7 | `unlimited_undos` | Non-consumable | $4.99 | Unlimited Undos | Undo any move at any time, as many times as you want. No more restarting a level after one small mistake. |
| 8 | `undo_pack` | Consumable | $0.99 | Undo Pack (10) | Adds 10 undos to your account. Take back any move at any time so one mistake never costs you a level. |
| 9 | `hint_pack` | Consumable | $1.99 | Hint Pack | Adds 10 hints to your account. Each hint reveals the next correct move on any level where you are stuck. |
| 10 | `starter_pack` | Consumable | $0.99 | Starter Pack | Best value for new players: 100 coins, 5 hints, and 5 lives bundled together. One-time purchase. |

---

## Subscription catalog

Subscriptions live under **Monetize → Subscriptions** in Play Console
(separate tab from In-app products). Each subscription needs a base plan
and at least one offer.

| # | Product ID | Name (≤55) | Description (≤200) | Billing period | Grace period | Price (USD) |
|---|---|---|---|---|---|---|
| 1 | `season_pass_monthly` | Season Pass | Monthly pass: ad-free play, +50 coins every day, all themes unlocked, and unlimited hints. Cancel anytime in Google Play. | 1 month (P1M) | 3 days | $1.99 |
| 2 | `weekly_pass` | Weekly Pass | Weekly pass: ad-free play, +100 coins every day, all themes unlocked, and unlimited hints. Cancel anytime in Google Play. | 1 week (P1W) | 3 days | $4.99 |

> Note: 2048-style games word the "unlimited hints" benefit as "unlimited undos" (they have no hint mechanic) and `starter_pack` as "100 coins + 5 undos + 5 lives + Ads Off" rather than "5 hints" — `check_iaps_descriptions` will surface that as a benign warning, not a blocker.

**Subscription form fields:**

| Field | Value |
|---|---|
| Subscription ID | `season_pass_monthly` |
| Name | Season Pass |
| Description | (from table above, ≤200) |
| Tax category | Digital goods sale |
| Base plan ID | `monthly-base` |
| Base plan type | Auto-renewing |
| Billing period | 1 month |
| Renewal type | Auto-renewing |
| Grace period | 3 days |
| Account hold | 30 days |
| Pause | optional, off |
| Resubscribe | on |
| Availability | All regions |
| Price | $1.99 USD (Play converts) |

---

## Per-app catalogs

Each app ships a SUBSET of the canonical catalog above. The exact subset
must match what the app's `game.html` shop offers and what
`MainActivity.java` `VALID_PRODUCTS` declares.

### Flagship games

| App | One-time product IDs | Subscriptions |
|---|---|---|
| **WaterSort** | `remove_ads`, `coins_small`, `coins_large`, `five_lives`, `unlimited_lives_1h`, `unlimited_lives_forever`, `unlimited_undos`, `hint_pack`, `starter_pack` | `season_pass_monthly` |
| **Nonogram** | `remove_ads`, `coins_small`, `coins_large`, `five_lives`, `unlimited_lives_1h`, `hint_pack`, `starter_pack` | `season_pass_monthly` |
| **PipeConnect** | `remove_ads`, `coins_small`, `coins_large`, `five_lives`, `unlimited_lives_1h`, `hint_pack`, `starter_pack` | `season_pass_monthly` |
| **Puzzle2048** | `remove_ads`, `coins_small`, `coins_large`, `five_lives`, `unlimited_lives_1h`, `hint_pack`, `starter_pack` | `season_pass_monthly` |
| **UnblockPuzzle** | `remove_ads`, `coins_small`, `coins_large`, `five_lives`, `unlimited_lives_1h`, `hint_pack`, `starter_pack` | `season_pass_monthly` |

> Before shipping any app, run:
> ```
> python3 pre_publish_check.py <AppName>
> ```
> The `[meta] iaps.json matches code` check confirms the
> `iaps.json` IDs are a subset of `VALID_PRODUCTS`. **Note:** that check
> currently only verifies one direction (json ⊆ code). If a code
> product is missing from json, the check passes but Play Console will
> have no product to sell. The `WaterSort/unlimited_undos` case from
> 2026-04-27 is the canonical example — always cross-check both ways
> manually before submission.

---

## Product naming conventions (for new IAPs not in this catalog)

If a future app introduces a new IAP type (e.g., `theme_pack_neon`),
follow these rules:

1. **ID format**: `lowercase_snake_case`, ≤40 chars.
2. **Name**: ≤55 chars, Title Case, no emoji, no trademark symbols.
3. **Description**: ≤200 chars, plain prose, ends in a period. State
   exactly what the user gets ("Adds X to your wallet" / "Permanently
   unlocks Y" / etc.). No marketing language ("amazing", "best",
   "premium experience").
4. **Add to** all four places: `MainActivity.java VALID_PRODUCTS`,
   `metadata/iaps.json`, this catalog, and the in-game shop UI.
5. **Choose Consumable vs Non-consumable** based on: does the user
   "use up" the purchase (Consumable) or unlock something forever
   (Non-consumable)?

---

## Why this lives in a single file

Every Play Console submission needs the same form fields with the same
character limits. Without a canonical reference, each new app submission
is a fresh round of "how do I word this in 200 chars". This file kills
that loop — copy-paste from the table, set price, click Save. Per-app
variations (which subset to ship, custom IAPs) live in the per-app
section above.
