# Portfolio plan — finishing every app (2026-10-12)

Every app in the repo is brought to production quality, one track at a time.
Each app gets: real, deep gameplay or a genuinely useful tool; a distinct
identity (palette, emblem, icon, feature graphic); 13-locale listing; IAP
catalog that matches what the code grants; AdMob-only wrapper (AppLovin is
gone); a content gate where content can be wrong (solvable / unique /
winnable / fair / factually checked); and an adversarial QA pass that plays
it with real input events. Uploading still follows the cadence rules in
CLAUDE.md (2–3 genuinely distinct apps a week, one per genre cluster per 7
days) — "finished" is not "published in a batch".

Shells (scaffolded with `scripts/scaffold_flagship.py --from <shell app>`):

| Track | Shell source | Apps | Notes |
|---|---|---|---|
| Game | Afterimage (family game shell) | 58 | levels or score; lives, coins, boosters, events, passes |
| Kids | ABCLearning (built first as the template) | 11 | Google Play Families: no push, child-directed ads only, parental gate on purchases and links, no Firebase / Play Games, privacy-kids URL |
| Utility | HabitTracker (built first as the template) | 92 | tool-first UI, settings, themes, remove_ads + Pro; reminders only where the tool needs them |

Already finished: WaterSortPuzzle, Nonogram, Puzzle2048, UnblockPuzzle,
PipeConnect, Afterimage, Hunch, Overlay. Pilot (building now): Sokoban,
FlappyWings, Sudoku, Solitaire, BlockPuzzle.

## Renamed for trademark safety (folder + title; Java package unchanged)

| Was | Now | Why |
|---|---|---|
| FlappyBird | FlappyWings | "Flappy Bird" mark |
| TetrisGame | BlockDrop | "Tetris" mark + Tetris look-and-feel is enforced (Tetris v. Xio) — the game must not be a falling-tetromino look-alike |
| WordleClone | WordGuess | "Wordle" (NYT) — also avoid the green/yellow tile look |
| HeadsUpGame | TiltGuess | "Heads Up!" (Warner Bros.) |
| HarryPotterFan | MythQuiz | Harry Potter fan content — becomes an original world-mythology quiz |
| LogoQuiz | SymbolQuiz | brand logos — becomes a quiz on public symbols (road signs, chemistry, laundry, music, maths) |
| Connections | WordGroups | "Connections" (NYT) |
| SpellingBee | WordHive | "Spelling Bee" puzzle (NYT) |
| Mastermind | CodeBreaker | "Mastermind" board-game mark |

## Game track (family shell)

Puzzle — Binairo · CodeBreaker · ColorFill · FindDifference · FruitSort ·
HiddenObject · JigsawPuzzle · KnotPuzzle · LightsOut · MahjongSolitaire ·
MemoryCard · Minesweeper · NumberLink · PinPull · PixelArt · ScrewPuzzle ·
SlidingTiles · Sumplete · YarnSort · WordGroups

Arcade / score — BalloonPop · BlockDrop · BrickBreaker · BubbleShooter ·
FruitMerge · NumberMemory · NumberTap · ReactionTime · SnakeGame · StroopTest ·
TapColor · WhackaMole

Word — Cryptogram · Hangman · WordConnect · WordGuess · WordHive · WordLadder ·
WordScramble · WordSearch

Trivia — AnimalQuiz · BibleQuiz · CapitalCities · EmojiQuiz · FlagQuiz ·
FoodQuiz · FootballQuiz · GeneralQuiz · GeographyQuiz · HistoryQuiz ·
MentalMathQuiz · MovieTrivia · MythQuiz · ScienceQuiz · SportsQuiz ·
SymbolQuiz · TrueOrFalse · TwentyQuestions

## Kids track (Families-compliant shell)

ABCLearning (template) · AnimalSounds · BasicMathKids · CountingApp (becomes a
kids counting game — TallyCounter is the adult tally tool) · DinosaurApp ·
EmotionFlash · KidsColoring · KidsDrum · KidsPiano · MultiplicationGame (kids
times-tables game — TimesTable is the adult study tool) · ShapesColors

## Utility track (tool shell)

HabitTracker (template) and every other app: tools, calculators, health
logs, timers, reference guides, music tools, party decks, creative toys.

## Siblings that must stay clearly distinct (Repetitive Content policy)

Each builder is told its sibling(s) and must differ in purpose, mechanic,
layout, palette, icon and copy — not just in content.

| Group | Distinct roles |
|---|---|
| WaterSortPuzzle · YarnSort · FruitSort | pour liquid · wind yarn spools onto a moving knitting queue · triple-match goods on shelves |
| PipeConnect · NumberLink | connect colour pairs (Flow) · fill one numbered 1..N path (Numbrix / Hidato) |
| FlagQuiz · CapitalCities · GeographyQuiz | name the flag · match country–capital pairs on a board · tap places on a world map |
| GeneralQuiz · TrueOrFalse · HistoryQuiz · ScienceQuiz | money-ladder MCQ · swipe true/false streaks · drag events into chronological order · experiments and periodic-table taps |
| TruthOrDare · NeverHaveIEver · WouldYouRather · ThisOrThat · IceBreaker · TwoTruthsOneLie | player turns + dares · fingers-down rounds · group vote tallies · bracket tournament · work/team conversation decks · bluff scoring |
| CharadesApp · TiltGuess | teams act out words with a timer · phone-on-forehead tilt guessing |
| SpinBottle · DecisionMaker | physics bottle for groups · weighted decision wheel and lists |
| TipCalculator · BillSplit · PercentageCalc · VATCalculator | one bill's tip · multi-person itemised split · percent toolkit · tax add/remove with country presets |
| PackingList · PackingChecklist | trip planner by destination/weather/duration · reusable checklists for any routine |
| TallyCounter · CountingApp | multi-counter tool · kids counting game |
| TimesTable · MultiplicationGame | adult study drills · kids arcade game |
| WorldClock · TimezoneConverter | live clocks and alarms per city · meeting-time planner across zones |
| ExpenseTracker · BudgetPlanner | log what you spent · plan monthly envelopes |
| CoinFlip · DiceRoller · RandomNumber · RandomName | 3D coin with streak stats · RPG dice sets · ranges and lotteries · name generator by style |
| KidsPiano · PianoKeyboard · KidsDrum · DrumMachine | kids songs with lights · full keyboard with lessons · kids pads · step sequencer |
| MorseCode · FlashlightSOS · PhoneticApp | Morse trainer · torch with SOS · NATO alphabet trainer |
| Fireworks · Kaleidoscope · SatisfyingSlime · ZenGarden · MandalaColor · DotArt · KidsColoring · PixelArt | each a different creative toy; PixelArt is the color-by-number game |
| MoodTracker · SleepTracker · WaterReminder · PostureReminder · EyeRest | different trackers/reminders with their own UI |
