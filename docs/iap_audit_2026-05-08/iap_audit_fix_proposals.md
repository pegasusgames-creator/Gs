# IAP audit fix proposals

Generated: 2026-05-08T17:28:26
Apps audited: 171
Total IAP entries: 1335
Anomalies surfaced: 695
Java cross-reference findings: 137

## Section 1: HIGH-confidence auto-applicable fixes

These will be applied automatically in Part E.

### unlimited_lives_1h — 142 app(s)
- ABCLearning/unlimited_lives_1h: $0.99 → $1.99
- _… and 141 more apps with the same change_
- Reason: same price as five_lives ($0.99) at less value — Anomaly 1 (same-price-different-value); spec ladder puts unlimited 1h at $1.99
- Confidence: HIGH

### unlimited_undos — 1 app(s)
- WaterSortPuzzle/unlimited_undos: $3.99 → $4.99
- Reason: $3.99 is off the spec's standard tier list; nearest on-tier price matching unlimited_lives_forever is $4.99
- Confidence: HIGH

## Section 2: LOW-confidence fixes for human review

These are surfaced but NOT applied automatically.

### cross_app_price_inconsistency — 1 case(s)
- [MAJOR] <portfolio-wide> / remove_ads: 'remove_ads' priced at multiple values: $2.99 (170 apps), $1.99 (1 apps)

### iap_in_json_missing_from_java — 137 case(s)
- [BLOCKER] ABCLearning / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] AnimalQuiz / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] AnimalSounds / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] AspectRatio / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BMICalculator / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BalloonPop / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BasicMathKids / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BibleQuiz / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] Binairo / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BlockPuzzle / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BloodPressureLog / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BloodSugarLog / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BreathingExercise / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BrickBreaker / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BubbleShooter / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] BudgetPlanner / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CapitalCities / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CharadesApp / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] ChessClock / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] ChoreChart / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CocktailGuide / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CoffeeGuide / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CompoundInterest / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] Connections / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CountingApp / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] Cryptogram / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] CurrencyConverter / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] DartsScorer / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] DecisionMaker / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- [BLOCKER] DiceRoller / coins_large,coins_small,five_lives,hint_pack,season_pass_monthly,starter_pack,unlimited_lives_1h,unlimited_lives_forever: iaps.json declares ['coins_large', 'coins_small', 'five_lives', 'hint_pack', 'season_pass_monthly', 'starter_pack', 'unlimited_lives_1h', 'unlimited_lives_forever'] but MainActivity.java VALID_PRODUCTS does not — purchase will fail
- _… and 107 more_

### mechanic_mismatch_hints — 131 case(s)
- [BLOCKER] ABCLearning / hint_pack: no 'hints' references found in game.html
- [BLOCKER] AnimalQuiz / hint_pack: no 'hints' references found in game.html
- [BLOCKER] AnimalSounds / hint_pack: no 'hints' references found in game.html
- [BLOCKER] AspectRatio / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BMICalculator / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BalloonPop / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BasicMathKids / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BibleQuiz / hint_pack: no 'hints' references found in game.html
- [BLOCKER] Binairo / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BlockPuzzle / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BloodPressureLog / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BloodSugarLog / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BreathingExercise / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BrickBreaker / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BubbleShooter / hint_pack: no 'hints' references found in game.html
- [BLOCKER] BudgetPlanner / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CapitalCities / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CharadesApp / hint_pack: no 'hints' references found in game.html
- [BLOCKER] ChessClock / hint_pack: no 'hints' references found in game.html
- [BLOCKER] ChoreChart / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CocktailGuide / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CoffeeGuide / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CompoundInterest / hint_pack: no 'hints' references found in game.html
- [BLOCKER] Connections / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CountingApp / hint_pack: no 'hints' references found in game.html
- [BLOCKER] CurrencyConverter / hint_pack: no 'hints' references found in game.html
- [BLOCKER] DartsScorer / hint_pack: no 'hints' references found in game.html
- [BLOCKER] DecisionMaker / hint_pack: no 'hints' references found in game.html
- [BLOCKER] DiceRoller / hint_pack: no 'hints' references found in game.html
- [BLOCKER] DinosaurApp / hint_pack: no 'hints' references found in game.html
- _… and 101 more_

### mechanic_mismatch_lives — 402 case(s)
- [BLOCKER] ABCLearning / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] ABCLearning / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] ABCLearning / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalQuiz / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalQuiz / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalQuiz / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalSounds / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalSounds / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AnimalSounds / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AspectRatio / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AspectRatio / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] AspectRatio / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BMICalculator / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BMICalculator / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BMICalculator / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BasicMathKids / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BasicMathKids / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BasicMathKids / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BibleQuiz / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BibleQuiz / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BibleQuiz / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] Binairo / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] Binairo / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] Binairo / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BlockPuzzle / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BlockPuzzle / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BlockPuzzle / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BloodPressureLog / five_lives: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BloodPressureLog / unlimited_lives_1h: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- [BLOCKER] BloodPressureLog / unlimited_lives_forever: no 'lives' / 'hearts' references found in game.html — user could buy a SKU the app can't grant
- _… and 372 more_

### mechanic_mismatch_undos — 2 case(s)
- [BLOCKER] Puzzle2048 / undo_pack: no 'undos' references found in game.html
- [BLOCKER] WaterSortPuzzle / unlimited_undos: no 'undos' references found in game.html

### missing_standard_skus — 16 case(s)
- [MINOR] AgeCalculator / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] CoinFlip / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] FlashlightSOS / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] GuitarChords / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] MemoryCard / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] Metronome / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] MusicTheory / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] PasswordGen / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] PianoKeyboard / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] RandomName / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] RandomNumber / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] RandomRecipe / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] StroopTest / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] TwentyQuestions / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] WordScramble / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']
- [MINOR] WordSearch / coin_packs,starter_pack,season_pass: app missing 3 standard buckets: ['coin_packs', 'starter_pack', 'season_pass']

