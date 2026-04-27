#!/usr/bin/env python3
"""Generate store-listing.txt for apps G-N"""
import os

BASE = '/home/pgs/Documents/Gs'

LISTINGS = {
'GhostWord': {
'name': 'Ghost Word — Letter Bluffing Game',
'short': 'Add letters without completing a word. Don\'t be the ghost!',
'full': """The classic word bluffing game Ghost — now on Android! Take turns adding letters to a growing sequence without completing a real word. Spell a word = you lose!

👻 HOW TO PLAY
Players take turns adding one letter to a growing string. You must be thinking of a real word that starts with those letters. Complete a real word and you become a "ghost"! First player to collect G-H-O-S-T loses.

✨ FEATURES
• 2–4 player local hot-seat mode
• Massive word dictionary (50,000+ words)
• Challenge mode — call out a bluff!
• Ghost counter per player
• Works fully offline

A perfect party and travel game. Download free!""",
'new': '• Challenge / bluff system\n• 4-player support\n• Improved word dictionary',
'tags': 'ghost word, word game, bluffing game, party game, letters, spelling, ghost'
},
'GolfScorecard': {
'name': 'Golf Scorecard — Score Tracker',
'short': 'Track golf scores for up to 4 players. 9 or 18 holes.',
'full': """The cleanest golf scorecard app for your round! Track strokes, pars, and handicaps for up to 4 players across 9 or 18 holes.

⛳ FEATURES
• 9 or 18 hole scorecards
• Up to 4 players per round
• Enter par for each hole
• Automatic score vs par (over/under) calculation
• Running totals and final scores
• Net score with handicap option
• Round history — save and review past rounds
• Works fully offline

Whether you're playing casual rounds or tracking your handicap, this is the scorecard you need. Download free!""",
'new': '• Handicap net score calculation\n• Round history saved\n• 18-hole support',
'tags': 'golf scorecard, golf score, golf tracker, handicap, birdie, bogey, par, stroke play'
},
'GroceryList': {
'name': 'Grocery List — Shopping Planner',
'short': 'Smart grocery list with categories, quantities & checkoff.',
'full': """The grocery list that actually makes shopping easier! Organize items by category, add quantities, and check things off as you go.

🛒 FEATURES
• Add items with quantity and unit (kg, lbs, pieces, etc.)
• Auto-category sorting: Produce, Dairy, Meat, Bakery, etc.
• Check off items as you shop
• Reusable list templates for regular shops
• Multiple lists (weekly shop, party, etc.)
• Search to quickly find items
• Works fully offline
• No account needed

🛍️ CATEGORIES
Produce, Dairy, Meat & Fish, Bakery, Frozen, Drinks, Snacks, Cleaning, Personal Care, and Custom.

Download free and shop smarter!""",
'new': '• Multiple list support\n• Reusable templates\n• Auto-categorization',
'tags': 'grocery list, shopping list, supermarket, food list, shopping planner, organizer'
},
'GuitarChords': {
'name': 'Guitar Chords — Chord Library',
'short': 'Every guitar chord with diagrams. Learn & play instantly.',
'full': """The complete guitar chord reference app! Browse hundreds of chord diagrams for every key and chord type — open chords, barre chords, and advanced voicings.

🎸 FEATURES
• 500+ chord diagrams
• All major, minor, 7th, 9th, sus, diminished, augmented chords
• Every key (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
• Clear fretboard diagrams with finger positions
• Chord audio playback (hear the chord)
• Favorite chords for quick access
• Beginner-friendly open chord section
• Works fully offline

🎵 ALSO INCLUDES
• Common chord progressions
• Capo position guide
• Works for left-handed players (flip option)

Download free and start playing!""",
'new': '• Audio chord playback\n• Left-handed flip option\n• Chord progressions guide',
'tags': 'guitar chords, chord diagrams, guitar, learn guitar, music, fretboard, barre chords'
},
'HabitTracker': {
'name': 'Habit Tracker — Daily Goals',
'short': 'Build good habits. Track streaks, stay consistent.',
'full': """Build the habits that change your life! Habit Tracker helps you set daily goals, track your consistency, and build powerful streaks.

✅ FEATURES
• Add unlimited habits with custom names and icons
• Daily check-in with one tap
• Streak counter (current and best)
• Completion rate percentage per habit
• Weekly and monthly habit calendar view
• Reminder notifications per habit
• Categories: Health, Fitness, Mind, Learning, Productivity, Social
• Works fully offline

📊 STATS TRACKED
• Current streak
• Longest streak ever
• Total completions
• Monthly completion rate
• Best performance days

Download free and start building better habits!""",
'new': '• Monthly calendar view\n• Per-habit reminders\n• Completion rate stats',
'tags': 'habit tracker, daily goals, streak, routine, productivity, self improvement, habits'
},
'Hangman': {
'name': 'Hangman — Word Guessing Game',
'short': 'Classic hangman with 5000+ words. Guess before it\'s too late!',
'full': """The classic hangman word game with thousands of words across multiple categories! Guess letters to reveal the hidden word before the man is hanged.

🪢 HOW TO PLAY
A random word is chosen and shown as blank spaces. Tap letters to guess. Each wrong guess adds a body part to the gallows. Guess the word before 6 wrong guesses — or it's game over!

✨ FEATURES
• 5000+ words across 10 categories
• Categories: Animals, Countries, Food, Sports, Movies, Science, Tech, Geography, Famous People, Random
• Difficulty levels: Easy (short words), Hard (long words)
• Hint system: reveal one letter
• Score tracking
• Works fully offline

Download free and test your vocabulary!""",
'new': '• 10 word categories\n• Difficulty levels\n• Hint system added',
'tags': 'hangman, word game, guessing game, vocabulary, spelling, letters, classic game, puzzle'
},
'HarryPotterFan': {
'name': 'Harry Potter Fan Quiz',
'short': 'The ultimate HP trivia for true wizards. 500+ questions!',
'full': """Accio trivia! The ultimate Harry Potter fan quiz — test your knowledge of the wizarding world across all 7 books and 8 films!

⚡ FEATURES
• 500+ Harry Potter trivia questions
• Books AND movies coverage
• Categories: Spells, Characters, Creatures, Hogwarts, Quidditch, Horcruxes, Deathly Hallows
• 4 difficulty levels: Muggle → Prefect → Auror → Dumbledore
• House assignment quiz (Gryffindor, Slytherin, Ravenclaw, Hufflepuff)
• Daily question
• Score tracking
• Works fully offline

Do you know your Nargles from your Nargled Wrackspurts? Download free!""",
'new': '• House sorting quiz\n• New Deathly Hallows category\n• 100+ new questions',
'tags': 'harry potter, HP trivia, hogwarts, wizard, quiz, fan quiz, magic, hermione, dumbledore'
},
'HeadsUpGame': {
'name': 'Heads Up! — Party Guessing Game',
'short': 'Hold it to your head, act it out, guess before time\'s up!',
'full': """The party game everyone loves! Hold your phone to your forehead, and get your team to describe the word so you can guess it before the timer runs out!

🙆 HOW TO PLAY
Tilt phone down to your forehead — timer starts! Tilt up if you pass. Guess as many as possible in 60 seconds. Keep score as you go!

🎭 CATEGORIES
• Movies & TV
• Celebrities
• Animals
• Sports Stars
• Characters
• Animals
• Custom — add your own!

✨ FEATURES
• 500+ words included
• Adjustable timer (30/60/90 sec)
• Team score tracking
• Custom word lists
• Works fully offline

The perfect icebreaker and party game! Download free!""",
'new': '• Custom word lists\n• Adjustable timer\n• Score tracking per team',
'tags': 'heads up, party game, guessing game, charades, celebrities, group game, fun'
},
'HiddenObject': {
'name': 'Hidden Object — Find & Seek',
'short': 'Find hidden objects in detailed scenes. 100+ levels!',
'full': """A classic hidden object game with beautifully detailed scenes! Search through busy scenes and find all the listed objects before time runs out.

🔍 HOW TO PLAY
Each level gives you a scene packed with objects and a list of items to find. Tap each object as you spot it. Find them all to complete the level!

✨ FEATURES
• 100+ detailed scenes across multiple themes
• Themes: Bedroom, Kitchen, Garden, City, Forest, Beach, Library
• Timed and relaxed modes
• Zoom-in for detailed searching
• Hint: flash the location of one hidden item
• Star rating based on speed
• Works fully offline

Great for focus, relaxation, and sharpening your observation skills. Download free!""",
'new': '• 30 new scenes\n• Relaxed (no-timer) mode\n• Zoom-in feature',
'tags': 'hidden object, find it, seek, observation, puzzle, I spy, scenes, detail'
},
'HistoryQuiz': {
'name': 'History Quiz — World Events',
'short': 'Test your history knowledge! Ancient to modern events.',
'full': """Journey through time with the ultimate history quiz! From ancient civilizations to modern events — test your knowledge across every era.

📜 FEATURES
• 600+ history questions
• Eras: Ancient History, Medieval, Renaissance, Industrial Age, 20th Century, Modern History
• Regions: World, Europe, Americas, Asia, Africa
• Multiple choice with detailed explanations
• Learn mode with fact cards
• Daily history question
• Score tracking
• Works fully offline

📚 TOPICS COVERED
Wars and battles, empires and dynasties, famous rulers, revolutions, inventions, treaties, and pivotal moments that shaped civilization.

Download free and travel through history!""",
'new': '• Regional filter added\n• Detailed answer explanations\n• Learn mode with facts',
'tags': 'history quiz, world history, trivia, education, ancient history, wars, dates, events'
},
'IceBreaker': {
'name': 'Ice Breaker — Get to Know You',
'short': '200+ fun questions to break the ice at parties & meetings.',
'full': """Break the ice instantly! A collection of 200+ fun, thoughtful, and sometimes hilarious questions to spark conversation at parties, team meetings, first dates, or with new friends.

🧊 QUESTION CATEGORIES
• Getting to Know You (mild)
• Fun & Hypothetical
• Deep & Meaningful
• Work & Team Building
• Party Mode (light roast)
• Would You Rather
• Two Truths & a Lie

✨ FEATURES
• 200+ unique questions
• Swipe for next question
• Favorite questions to revisit
• Category filter
• Works fully offline

Perfect for team-building events, first dates, classrooms, and anywhere new people meet. Download free!""",
'new': '• Would You Rather category\n• Favorite questions\n• 50 new questions added',
'tags': 'ice breaker, get to know you, team building, party game, conversation starter, questions'
},
'InfiniteJumper': {
'name': 'Infinite Jumper — Hop & Climb',
'short': 'Jump on platforms and climb as high as possible!',
'full': """Jump, hop, and bounce your way to the top! Infinite Jumper is an addictive vertical platformer — land on platforms and keep climbing higher and higher!

🦘 HOW TO PLAY
Your character automatically bounces. Tilt or tap left/right to steer onto platforms. Don't fall! Platforms get smaller, move, and disappear the higher you go.

✨ FEATURES
• Endless vertical gameplay
• Multiple platform types: static, moving, bouncy, breakable
• Power-ups: spring, jetpack, shield
• High score tracking
• Unlockable characters
• Works fully offline

Simple controls, endless replay value. How high can you go? Download free!""",
'new': '• Moving and breakable platforms\n• Jetpack power-up\n• Unlockable characters',
'tags': 'infinite jumper, platformer, jump game, vertical, arcade, casual, climbing, endless'
},
'JigsawPuzzle': {
'name': 'Jigsaw Puzzle — Classic Puzzle',
'short': 'Beautiful jigsaw puzzles from 12 to 500 pieces!',
'full': """Relax with beautifully illustrated jigsaw puzzles! From quick 12-piece beginner puzzles to challenging 500-piece expert challenges.

🧩 FEATURES
• 100+ puzzle images
• Piece counts: 12, 25, 50, 100, 200, 500
• Categories: Nature, Animals, Landscapes, Art, Architecture
• Snap-to-place when close enough
• Ghost image overlay guide
• Rotation option for extra challenge
• Timer for competitive play
• Works fully offline

✨ GREAT FOR
• Relaxing brain training
• Family activity
• Screen time without pressure

Piece by piece, you'll build something beautiful. Download free!""",
'new': '• 500-piece puzzles added\n• Ghost guide overlay\n• Rotation option',
'tags': 'jigsaw puzzle, puzzle, pieces, relaxing, brain, nature, animals, classic puzzle'
},
'Kaleidoscope': {
'name': 'Kaleidoscope — Visual Art',
'short': 'Tap & move to create stunning kaleidoscope patterns!',
'full': """Create mesmerizing kaleidoscope art with just your finger! Tap and move to generate endlessly beautiful symmetric patterns in real time.

🔮 FEATURES
• Real-time kaleidoscope generation from touch
• Multiple symmetry modes: 4x, 6x, 8x, 12x, 16x
• 20+ color palettes
• Auto-animate mode for screensaver effect
• Save artwork to gallery
• Share creations
• Works fully offline

Totally hypnotic, totally relaxing. A perfect stress-relief visual toy. Download free!""",
'new': '• Auto-animate screensaver mode\n• Save to gallery\n• 6 new color palettes',
'tags': 'kaleidoscope, visual art, creative, relaxing, symmetric, patterns, stress relief, art'
},
'KidsColoring': {
'name': 'Kids Coloring — Paint & Draw',
'short': 'Fun digital coloring book for kids! 100+ pictures.',
'full': """A beautiful digital coloring book designed for young children! Tap to fill areas with color and bring fun pictures to life.

🖍️ FEATURES
• 100+ kid-friendly coloring pages
• Categories: Animals, Vehicles, Food, Fantasy, Holidays, Dinosaurs
• Tap-to-fill with any color
• Big, bold outlines — easy for small fingers
• 24-color palette
• Undo button
• Save and share completed pictures
• Works fully offline

🎨 DESIGNED FOR KIDS
• Simple, large tap areas
• No complex drawing needed
• Satisfying color fills
• Printable artwork (via share)

Download free and let the creativity flow!""",
'new': '• 30 new coloring pages\n• Holiday category\n• Save to gallery',
'tags': 'kids coloring, coloring book, children, paint, drawing, creative, animals, toddler'
},
'KidsDrum': {
'name': 'Kids Drum Set — Tap & Beat',
'short': 'A fun drum kit for kids! Tap pads to make drum sounds.',
'full': """A fun, colorful drum kit for kids! Tap the drum pads to make real drum sounds and let little musicians rock out!

🥁 FEATURES
• 8 colorful drum pads with real sound samples
• Pads: kick, snare, hi-hat, crash, ride, tom, cowbell, tambourine
• Big, easy-to-tap pads for small fingers
• Bright visual effects on each hit
• Record your beat and play it back
• Volume control
• Works fully offline

🎵 GREAT FOR
• Ages 2–8
• Introducing rhythm and music
• Free play and exploration
• Screen time that's actually musical

Download free and start drumming!""",
'new': '• Beat recording and playback\n• 2 new sound kits\n• Visual hit effects',
'tags': 'kids drum, drum kit, children, music, percussion, beat, rhythm, toddler, musical toy'
},
'KidsPiano': {
'name': 'Kids Piano — Learn Music Notes',
'short': 'Colorful piano for kids! Learn notes and play songs.',
'full': """A bright, fun piano app for young musicians! Kids can freely explore notes, learn the scale, and play along to simple songs.

🎹 FEATURES
• Full color-coded piano keyboard (2 octaves)
• Each key shows the note name (C, D, E, F, G, A, B)
• Learn mode: tap highlighted keys to play songs
• 10 simple children's songs included
• Record and playback mode
• Volume control
• Works fully offline

🎵 SONGS INCLUDED
Twinkle Twinkle, Happy Birthday, Mary Had a Little Lamb, Jingle Bells, Old MacDonald, and more.

Perfect for ages 2–8. Download free!""",
'new': '• 5 new songs added\n• Recording mode\n• Color-coded note labels',
'tags': 'kids piano, piano, music, children, notes, keyboard, learn piano, toddler, musical'
},
'KnotPuzzle': {
'name': 'Knot Puzzle — Untangle the Rope',
'short': 'Untangle knotted ropes by dragging nodes. Satisfying puzzle!',
'full': """Untangle the knots! Drag the nodes to rearrange a tangled rope or wire until no lines cross. Satisfying, calming, and surprisingly tricky.

🪢 HOW TO PLAY
You're given a tangled graph with crossing lines. Drag the nodes around to rearrange them until no lines overlap. When all crossings are cleared, the puzzle is solved!

✨ FEATURES
• 200+ levels from easy to expert
• Increasing node count as levels progress
• Smooth drag controls
• Hint system shows one valid move
• Satisfying completion animation
• Works fully offline

One of the most calming puzzle games you'll ever play. Download free!""",
'new': '• 80 new levels\n• Hint system\n• Smoother drag physics',
'tags': 'knot puzzle, untangle, rope puzzle, graph, logic, relaxing, casual, brain teaser'
},
'LightsOut': {
'name': 'Lights Out — Toggle Puzzle',
'short': 'Turn off all the lights! Classic toggle logic puzzle.',
'full': """The classic Lights Out puzzle game! Tap lights to toggle them — but every tap also flips the adjacent lights. Turn them ALL off to win!

💡 HOW TO PLAY
Tap any cell to toggle it on/off. But toggling also flips the cells above, below, left, and right. Figure out the minimum number of moves to turn every light off.

✨ FEATURES
• Grid sizes: 3×3, 4×4, 5×5, 6×6
• 100+ handcrafted puzzles
• Random puzzle generator
• Move counter and par display
• Hint system (shows optimal move)
• Works fully offline

Deceptively simple, deeply satisfying. Download free!""",
'new': '• 6×6 grid size\n• Optimal move hint\n• Random puzzle generator',
'tags': 'lights out, toggle puzzle, logic puzzle, grid, brain teaser, classic game, math puzzle'
},
'LoanCalculator': {
'name': 'Loan Calculator — EMI Planner',
'short': 'Calculate monthly loan payments, interest & total cost.',
'full': """Calculate your exact loan repayments before you sign anything! Loan Calculator shows your monthly payment (EMI), total interest paid, and total cost of the loan.

🏦 FEATURES
• Calculate monthly payment from loan amount, rate, and term
• Total interest and total cost display
• Amortization schedule (month-by-month breakdown)
• Comparison: change rate or term to compare scenarios
• Works with any currency
• Works fully offline

💡 USE CASES
• Home loans / mortgages
• Car loans
• Personal loans
• Student loans
• Business loans

Not financial advice — always consult a professional. Download free!""",
'new': '• Amortization schedule table\n• Scenario comparison\n• Total interest breakdown',
'tags': 'loan calculator, EMI, mortgage, interest, monthly payment, finance, amortization'
},
'LogoQuiz': {
'name': 'Logo Quiz — Guess the Brand',
'short': 'Recognize 500+ brand logos! Test your brand knowledge.',
'full': """How many logos can you identify? Logo Quiz shows you famous brand logos — some easy, some surprisingly tricky — and tests your brand recognition.

🏷️ FEATURES
• 500+ logos from global brands
• Categories: Tech, Food & Drink, Cars, Fashion, Sports, Entertainment, Retail
• Multiple choice and type-the-answer modes
• Difficulty levels: Famous → Common → Obscure
• Logo facts revealed after each answer
• Score tracking
• Works fully offline

From Apple to Zara — how many do you know? Download free!""",
'new': '• 100 new logos\n• Brand facts on answers\n• Obscure difficulty level',
'tags': 'logo quiz, brand quiz, logos, guess the brand, company logos, trivia, brand recognition'
},
'MahjongSolitaire': {
'name': 'Mahjong Solitaire — Classic Tile',
'short': 'Classic Mahjong tile-matching solitaire. 300+ layouts!',
'full': """The timeless classic! Match and clear all tiles from the board in this beautiful Mahjong Solitaire game.

🀄 HOW TO PLAY
Find two identical tiles where both sides are free (not blocked by other tiles). Match them to remove them from the board. Clear all tiles to win!

✨ FEATURES
• 300+ handcrafted layouts
• Classic tile set with animals, seasons, flowers, characters, circles, and bamboo
• Hint: flash one valid match
• Shuffle: rearrange when stuck
• Undo last move
• Timer and move counter
• Works fully offline

Relaxing, meditative, and endlessly replayable. Download free!""",
'new': '• 100 new layouts\n• Undo button\n• Shuffle when stuck',
'tags': 'mahjong solitaire, mahjong, tile matching, classic, relaxing, solitaire, puzzle'
},
'MandalaColor': {
'name': 'Mandala Coloring — Anti-Stress Art',
'short': 'Color intricate mandalas. Relaxing anti-stress art therapy.',
'full': """Relax, breathe, and color! Mandala Coloring gives you beautifully intricate mandala designs to color at your own pace — perfect digital art therapy.

🌸 FEATURES
• 80+ mandala coloring pages
• Tap-to-fill sections — no precise drawing needed
• 64-color palette
• Zoom in for detail work
• Undo/redo
• Save completed mandalas to gallery
• Share your artwork
• Works fully offline

🎨 GREAT FOR
• Stress and anxiety relief
• Mindfulness and meditation
• Creative relaxation
• Adults and older children

Proven to reduce stress and increase focus. Download free!""",
'new': '• 20 new mandala designs\n• Save and share\n• Zoom in for detail',
'tags': 'mandala, coloring, anti-stress, relaxing, art, mindfulness, meditation, adult coloring'
},
'Mastermind': {
'name': 'Mastermind — Code Cracker',
'short': 'Crack the secret color code in 10 guesses. Classic logic game!',
'full': """The classic code-breaking game! Deduce the secret 4-color sequence using logic and the clues given after each guess.

🧠 HOW TO PLAY
The app picks a secret sequence of 4 colored pegs. Make a guess and receive clues: black peg (right color, right position), white peg (right color, wrong position). Crack the code in 10 guesses or fewer!

✨ FEATURES
• Classic 4-peg, 6-color setup
• Advanced mode: 5 pegs, 8 colors
• Unlimited guesses or strict 10-guess mode
• Best score tracking (fewest guesses)
• Full hint explanation
• Works fully offline

The original deduction game — still brilliant after 50 years. Download free!""",
'new': '• Advanced 5-peg mode\n• Best-guess score tracking\n• Hint explanation system',
'tags': 'mastermind, code breaking, deduction, logic, colors, puzzle, classic game, peg game'
},
'MedicationReminder': {
'name': 'Medication Reminder — Pill Alarm',
'short': 'Never miss a dose. Set pill reminders with snooze.',
'full': """Never miss a medication dose! Medication Reminder helps you track all your medicines with customizable alarms and a daily dose log.

💊 FEATURES
• Add medications with name, dosage, and frequency
• Set reminder times (once, twice, or multiple daily)
• Snooze option for each alarm
• Daily dose log — mark each dose as taken
• Missed dose alert
• Weekly schedule view
• Multiple medications supported
• Works fully offline

Not a medical device. Always follow your doctor's instructions. Download free!""",
'new': '• Multiple daily reminders per medication\n• Missed dose tracking\n• Weekly schedule view',
'tags': 'medication reminder, pill reminder, medicine alarm, health, dose tracker, pharmacy'
},
'MeetingTimer': {
'name': 'Meeting Timer — Standup Clock',
'short': 'Time your standups and meetings. Each speaker gets a slot.',
'full': """Run tighter, more efficient meetings! Meeting Timer lets you allocate time per agenda item or speaker and keeps everyone on track.

⏱️ FEATURES
• Set a total meeting time
• Add agenda items or speakers with time slots
• Tap to move to next item
• Visual countdown for each item
• Total time remaining display
• Warning alerts at 1 minute and 30 seconds
• Overtime indicator
• Works fully offline

✅ GREAT FOR
• Daily standups
• Sprint planning
• Presentations
• Panel discussions
• Any timed agenda

Download free and reclaim your meeting time!""",
'new': '• Agenda item list\n• Per-speaker timer\n• Overtime indicator',
'tags': 'meeting timer, standup timer, agenda, presentation timer, productivity, time management'
},
'MemoryCard': {
'name': 'Memory Card — Flip & Match',
'short': 'Flip cards to find matching pairs! Classic memory game.',
'full': """The classic memory card game! Flip cards to reveal pictures, remember their positions, and match all pairs to win!

🃏 HOW TO PLAY
Cards are placed face-down. Flip two at a time. If they match, they stay turned over. If not, they flip back. Match all pairs to complete the level!

✨ FEATURES
• Grid sizes: 4×3, 4×4, 4×5, 6×6
• Multiple themes: Emoji, Animals, Fruits, Numbers, Flags
• Move counter and time tracker
• Best score per grid size
• Relaxed and competitive modes
• Works fully offline

Great for all ages! Helps develop concentration and memory. Download free!""",
'new': '• 6×6 hard mode\n• Flag card theme\n• Move counter scoring',
'tags': 'memory card, flip card, matching game, concentration, memory, pairs, brain training'
},
'MentalMathQuiz': {
'name': 'Mental Math Quiz — Brain Training',
'short': 'Speed math quiz! Addition, subtraction, multiplication.',
'full': """Train your brain with rapid-fire mental math! Mental Math Quiz improves your calculation speed and accuracy with timed arithmetic challenges.

🔢 FEATURES
• All four operations: +, −, ×, ÷
• Adjustable difficulty: 1-digit through 4-digit numbers
• Timed rounds: 30s, 60s, 2 minutes
• Score tracks correct answers per minute
• Personal best tracking
• Daily challenge with global ranking style scoring
• Works fully offline

📊 TRACKS YOUR PROGRESS
• Speed improvement over time
• Accuracy rate
• Best score per operation
• Daily streak

Download free and sharpen your mental arithmetic!""",
'new': '• 4-digit number difficulty\n• Daily challenge mode\n• Progress over time tracking',
'tags': 'mental math, arithmetic, brain training, math quiz, speed math, calculator, fast math'
},
'Metronome': {
'name': 'Metronome — Tempo & Beat Keeper',
'short': 'Precise metronome for musicians. 20–300 BPM, tap tempo.',
'full': """A clean, precise metronome for musicians of all levels! Set your tempo, time signature, and practice with a steady reliable beat.

🎵 FEATURES
• 20–300 BPM range
• Tap tempo button — tap to set the BPM
• Time signatures: 2/4, 3/4, 4/4, 5/4, 6/8, 7/8
• Accent on beat 1 option
• Visual pendulum display
• Audio tick with multiple metronome sounds
• Works fully offline
• Screen stays on during use

Perfect for guitar, piano, drums, violin, and all instruments. Download free!""",
'new': '• Tap tempo button\n• Multiple time signatures\n• 5 metronome click sounds',
'tags': 'metronome, tempo, BPM, musician, guitar, piano, drums, beat, practice, timing'
},
'Minesweeper': {
'name': 'Minesweeper — Classic Puzzle',
'short': 'Classic minesweeper. Reveal safe squares, flag the mines!',
'full': """The timeless classic that defined puzzle gaming! Clear the minefield using logic without hitting a single bomb.

💣 HOW TO PLAY
Tap to reveal a square. Numbers show how many mines are adjacent. Long-press to flag a mine. Reveal every safe square to win!

✨ FEATURES
• Difficulty levels: Easy (9×9), Medium (16×16), Hard (30×16)
• Custom grid and mine count
• Safe first tap — first tap is always safe
• Flag mode and question marks
• Best time tracking per difficulty
• Auto-reveal empty areas
• Works fully offline

The original logic puzzle game. Download free!""",
'new': '• Safe first tap guaranteed\n• Custom difficulty mode\n• Best time leaderboard',
'tags': 'minesweeper, classic game, logic, mines, bomb, puzzle, grid, Microsoft game'
},
'MoodTracker': {
'name': 'Mood Tracker — Daily Journal',
'short': 'Log your mood daily. See patterns and feel understood.',
'full': """Track how you feel every day and discover what affects your mood! Mood Tracker is a gentle, private daily mood journal.

😊 FEATURES
• 5-level mood scale: Great → Good → Okay → Bad → Terrible
• Optional note for each entry
• Mood tags (anxious, tired, grateful, energized, etc.)
• Calendar view of mood history
• Weekly and monthly mood trend charts
• Mood pattern insights (e.g. Mondays tend to be lower)
• All data stored privately on device
• Works fully offline

🌟 GREAT FOR
• Mental health awareness
• Therapy homework
• Identifying mood triggers
• Building self-awareness

Download free and start checking in with yourself!""",
'new': '• Mood pattern insights\n• Monthly trend charts\n• Tags system for context',
'tags': 'mood tracker, mood journal, mental health, daily mood, emotions, feelings, diary'
},
'MorseCode': {
'name': 'Morse Code — Translator & Flasher',
'short': 'Translate text to Morse code. Flash, beep & learn!',
'full': """Translate any text to Morse code — and back! Morse Code Translator also flashes the code using your screen and plays beep tones so you can actually transmit.

📡 FEATURES
• Text ↔ Morse code translation
• Screen flash output (SOS and custom messages)
• Audio beep output (adjustable speed and pitch)
• Learn Morse mode — shows each letter's code
• Speed control: slow learning mode to fast expert
• International Morse alphabet (A–Z, 0–9, punctuation)
• Works fully offline

Tap mode: tap to enter Morse manually and decode it! Download free!""",
'new': '• Audio beep with pitch control\n• Manual tap decode mode\n• Learn Morse mode',
'tags': 'morse code, translator, SOS, flashing, beep, telegraph, signal, emergency, learn morse'
},
'MovieTrivia': {
'name': 'Movie Trivia — Film Quiz',
'short': 'Test your film knowledge! 500+ movie trivia questions.',
'full': """Lights, camera, action! Test your movie knowledge with hundreds of questions covering all genres, decades, and the biggest blockbusters of all time.

🎬 FEATURES
• 500+ movie trivia questions
• Categories: Action, Comedy, Drama, Horror, Sci-Fi, Animated, Oscar Winners, 80s/90s Classics
• Multiple choice format
• Director and actor fact questions
• Box office record questions
• Daily movie question
• Score tracking
• Works fully offline

From classic cinema to modern blockbusters — can you score 100%? Download free!""",
'new': '• Classic films category (80s/90s)\n• Director questions added\n• Daily question mode',
'tags': 'movie trivia, film quiz, cinema, Hollywood, actors, directors, Oscars, movies quiz'
},
'MultiplicationGame': {
'name': 'Multiplication Game — Times Tables',
'short': 'Master times tables with fun multiplication games!',
'full': """Master multiplication the fun way! This game makes learning times tables engaging with progressive challenges and instant feedback.

✖️ FEATURES
• Times tables 1–12
• Multiple game modes:
  • Flash Quiz — quick-fire answers
  • Fill in the Blank — find the missing number
  • Timed Sprint — race the clock
• Choose specific tables to practice
• Star rating for each table mastered
• Daily multiplication challenge
• Works fully offline

📊 TRACKS PROGRESS
• Mastery level per table
• Speed improvement
• Accuracy rate
• Stars earned

Download free and never struggle with times tables again!""",
'new': '• Timed sprint mode\n• Per-table mastery tracking\n• Daily challenge',
'tags': 'multiplication, times tables, math game, kids, arithmetic, school, learning, 12 times'
},
'MusicTheory': {
'name': 'Music Theory — Learn & Quiz',
'short': 'Learn music theory fundamentals. Notes, scales, chords!',
'full': """Learn music theory without boring textbooks! Music Theory covers everything from reading notes to understanding chords, scales, intervals, and progressions — with interactive quizzes.

🎼 TOPICS COVERED
• Note names and values
• Staff and clef reading
• Major and minor scales
• Key signatures
• Intervals (semitones, octaves)
• Chord construction (triads, 7ths)
• Common chord progressions
• Rhythm and time signatures

✨ FEATURES
• Lessons with diagrams
• Interactive quizzes after each topic
• Piano keyboard visual reference
• Works fully offline

Whether you're a beginner or brushing up, this app covers the essentials. Download free!""",
'new': '• Chord construction lessons\n• Interactive staff quizzes\n• Rhythm module added',
'tags': 'music theory, learn music, notes, scales, chords, intervals, sheet music, piano theory'
},
'NeverHaveIEver': {
'name': 'Never Have I Ever — Party Game',
'short': '500+ Never Have I Ever prompts. Perfect party game!',
'full': """The classic party game with 500+ prompts! Take turns reading "Never Have I Ever..." statements and find out who's done the most wild things!

🙋 HOW TO PLAY
One person reads a prompt. Anyone who HAS done it takes a drink (or sits down, or loses a point — your rules!). The stories and laughs follow naturally.

🎮 MODES
• Classic — standard Never Have I Ever
• Spicy — for adults who want more daring prompts
• Safe — totally family-friendly
• Custom — add your own prompts

✨ FEATURES
• 500+ unique prompts
• 3 difficulty/spice levels
• Swipe for next prompt
• Works fully offline
• No account needed

Download free and get the party started!""",
'new': '• 200+ new prompts\n• Custom prompt mode\n• Family-safe filter',
'tags': 'never have I ever, party game, drinking game, fun, group game, adults, prompts'
},
}

skip = {'BallSortPuzzle','WaterSort','Nonogram','PipeConnect','Puzzle2048','UnblockPuzzle'}

TEMPLATE = """========================================
APP NAME
========================================
{name}

========================================
SHORT DESCRIPTION (80 chars max)
========================================
{short}

========================================
FULL DESCRIPTION
========================================
{full}

========================================
WHAT'S NEW (Release Notes for v1.0)
========================================
{new}

========================================
TAGS / KEYWORDS (for Play Store optimization)
========================================
{tags}
"""

written = 0
for app, data in LISTINGS.items():
    if app in skip:
        continue
    store_dir = f'{BASE}/{app}/store'
    if not os.path.isdir(store_dir):
        print(f'WARNING: no store dir for {app}')
        continue
    path = f'{store_dir}/store-listing.txt'
    with open(path, 'w') as f:
        f.write(TEMPLATE.format(**data))
    written += 1

print(f'Wrote {written} store listings (batch 2: G-N)')
