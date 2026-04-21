#!/usr/bin/env python3
"""Generate store-listing.txt for apps N-Z"""
import os

BASE = '/home/pgs/Documents/Gs'

LISTINGS = {
'NumberBase': {
'name': 'Number Base Converter',
'short': 'Convert between binary, decimal, hex & octal instantly.',
'full': """Instantly convert numbers between binary, decimal, hexadecimal, and octal! Perfect for students, programmers, and electronics hobbyists.

🔢 FEATURES
• Convert between: Binary (base 2), Octal (base 8), Decimal (base 10), Hexadecimal (base 16)
• Any custom base (2–36)
• Real-time conversion as you type
• Copy any result to clipboard
• ASCII character display for hex values
• Step-by-step conversion explanation
• Works fully offline

✅ GREAT FOR
• Computer science students
• Programming and web development
• Electronics and microcontrollers
• Color code conversion (#RRGGBB)

Download free!""",
'new': '• Custom base support (2–36)\n• ASCII display\n• Step-by-step explanation',
'tags': 'number base, binary, hexadecimal, decimal, octal, converter, programmer, computer science'
},
'NumberLink': {
'name': 'Number Link — Path Puzzle',
'short': 'Connect matching numbers without crossing paths. Logic puzzle!',
'full': """Connect matching number pairs with paths that fill the entire grid! A deceptively simple logic puzzle that will have you hooked.

🔢 HOW TO PLAY
Draw paths to connect each pair of matching numbers. Paths can't cross each other. Every cell in the grid must be filled by a path. Only one solution exists!

✨ FEATURES
• 300+ levels from easy to expert
• Grid sizes: 5×5, 6×6, 7×7, 8×8, 9×9
• Auto-validate: shows conflicts in red
• Hint shows one correct segment
• Undo button
• Works fully offline

One of the most satisfying logic puzzles on Android. Download free!""",
'new': '• 9×9 grid size added\n• Conflict highlighting\n• 100 new levels',
'tags': 'number link, flow free, path puzzle, connect numbers, logic, grid puzzle, brain'
},
'NumberMemory': {
'name': 'Number Memory — Brain Training',
'short': 'Remember longer and longer number sequences. Train your memory!',
'full': """How many digits can you remember? Number Memory shows you a sequence of numbers, then hides them — type them back from memory!

🧠 HOW TO PLAY
A sequence of numbers appears briefly on screen. Remember them. When they disappear, type the sequence back in order. Correct = next level (longer sequence). Wrong = game over!

✨ FEATURES
• Start at 3 digits, work up to 20+
• Multiple game modes: digits only, mixed digits and letters
• Best score tracking
• Speed challenge: less time to memorize
• Daily memory test
• Works fully offline

Great for improving short-term memory and concentration. Download free!""",
'new': '• Alphanumeric mode (digits + letters)\n• Speed challenge mode\n• Daily test',
'tags': 'number memory, memory game, brain training, digits, sequence, recall, concentration'
},
'NumberMerge': {
'name': 'Number Merge — 2048 Style',
'short': 'Merge numbers to reach the highest tile! 2048-style puzzle.',
'full': """Slide and merge tiles to combine numbers and reach the highest score! A fresh twist on the classic 2048 mechanic.

🔢 HOW TO PLAY
Swipe to slide all tiles in one direction. When two tiles with the same number touch, they merge into double the value. Reach 2048, 4096, or higher!

✨ FEATURES
• Classic 4×4 grid gameplay
• Smooth swipe controls
• High score and best tile tracking
• Undo last move
• Daily challenge board
• Works fully offline

Addictive, strategic, and endlessly replayable. Download free!""",
'new': '• Undo last move\n• Daily challenge mode\n• Smooth swipe animations',
'tags': 'number merge, 2048, merge, tiles, puzzle, math, swipe, strategy, brain'
},
'NumberTap': {
'name': 'Number Tap — Speed Challenge',
'short': 'Tap numbers 1–25 in order as fast as you can!',
'full': """How fast can you tap numbers in order? Number Tap shows 25 scattered numbers — tap them in sequence as fast as possible!

🔢 HOW TO PLAY
25 numbers appear randomly on the screen. Tap 1, then 2, then 3... all the way to 25. Race the clock! Your time is your score.

✨ FEATURES
• Classic 1–25 tap challenge
• Millisecond precision timing
• Personal best tracking
• Increasing difficulty: smaller numbers, faster pace
• Daily leaderboard challenge
• Works fully offline

Trains focus, speed, and visual scanning. Great for all ages! Download free!""",
'new': '• Millisecond timer\n• Difficulty scaling\n• Daily leaderboard',
'tags': 'number tap, speed game, reaction, tapping, 1 to 25, focus, brain training, fast tap'
},
'PackingChecklist': {
'name': 'Packing Checklist — Travel List',
'short': 'Never forget anything! Smart packing checklist for travel.',
'full': """Pack smarter, not harder! Packing Checklist helps you prepare for any trip with customizable lists you can reuse for every journey.

✈️ FEATURES
• Pre-built packing templates (Beach, Business, Winter, Camping, etc.)
• Create custom lists for any trip type
• Check off items as you pack
• Add personal items to any template
• Set trip dates as a reminder
• Reuse saved templates
• Works fully offline

🧳 TEMPLATE CATEGORIES
Clothes & Shoes, Toiletries, Documents, Electronics, Health & Medicine, Beach Gear, Sports Equipment, Work Essentials, and more.

Download free and never leave home without it!""",
'new': '• Trip date reminder\n• 5 new templates\n• Custom item categories',
'tags': 'packing checklist, travel, packing list, trip, suitcase, luggage, vacation, travel app'
},
'PackingList': {
'name': 'Packing List — Trip Organizer',
'short': 'Organize packing for any trip. Templates for every occasion.',
'full': """Your complete trip packing companion! Packing List helps you organize everything you need for any type of trip with smart templates and checklists.

✈️ FEATURES
• Smart packing templates by trip type
• Per-person packing in one list (family trips)
• Weight and quantity tracking
• Check off items as packed
• Share list with travel companions
• Multiple active trips
• Works fully offline

Great for frequent travelers who want to start every trip organized. Download free!""",
'new': '• Per-person sub-lists for families\n• Share list feature\n• Weight tracking',
'tags': 'packing list, travel organizer, trip, luggage, suitcase, travel checklist, vacation'
},
'PasswordGen': {
'name': 'Password Generator — Secure Keys',
'short': 'Generate strong passwords. Customize length & characters.',
'full': """Generate uncrackable passwords instantly! Password Generator creates strong, random passwords with full control over length and character types.

🔑 FEATURES
• Adjustable length: 8–128 characters
• Toggle: uppercase, lowercase, numbers, symbols
• Exclude confusing characters (0/O, 1/l/I)
• Copy to clipboard with one tap
• Generate multiple passwords at once
• Password strength meter
• Memorable password option (word-based)
• Works fully offline — nothing sent over internet

✅ ALSO INCLUDES
• Passphrase generator (4 random words)
• PIN generator (4–12 digits)

No passwords are stored or transmitted. Download free!""",
'new': '• Passphrase generator added\n• Exclude ambiguous characters option\n• Strength meter',
'tags': 'password generator, secure password, random password, strong password, PIN, security'
},
'PatternSequence': {
'name': 'Pattern Sequence — Memory IQ',
'short': 'Memorize and repeat growing patterns. Brain training!',
'full': """Watch the pattern, remember it, repeat it! Pattern Sequence is a classic Simon-style memory and pattern recognition challenge.

🔷 HOW TO PLAY
Shapes or colors light up in a sequence. Watch carefully, then tap them back in the same order. Each correct round adds one more step to the pattern. How far can you go?

✨ FEATURES
• Color patterns (Simon-style)
• Shape sequence mode
• Number sequence mode
• Increasing speed as level rises
• High score tracking
• Daily pattern challenge
• Works fully offline

Great for memory training, focus, and pattern recognition. Download free!""",
'new': '• Shape sequence mode\n• Number sequence mode\n• Speed increases by level',
'tags': 'pattern sequence, memory game, Simon, brain training, pattern recognition, IQ, recall'
},
'PercentageCalc': {
'name': 'Percentage Calculator',
'short': 'Calculate percentages instantly. Tip, discount, VAT & more.',
'full': """The fastest percentage calculator on Android! Solve any percentage problem in seconds — tips, discounts, tax, markups, grade percentages, and more.

% FEATURES
• What is X% of Y? (e.g. 15% of 80 = 12)
• X is what % of Y? (e.g. 12 is what % of 80?)
• % increase / decrease between two values
• Tip calculator (% of bill)
• Discount calculator (% off price)
• VAT / tax calculator
• Works fully offline

One screen, all the percentage math you'll ever need. Download free!""",
'new': '• VAT/tax calculator mode\n• % increase/decrease calculator\n• Discount mode',
'tags': 'percentage calculator, percent, discount, tip, tax, VAT, math, calculator'
},
'PeriodTracker': {
'name': 'Period Tracker — Cycle Calendar',
'short': 'Track your menstrual cycle. Predictions & fertility window.',
'full': """A simple, private period and cycle tracker. Log periods, get accurate predictions, and understand your cycle.

📅 FEATURES
• Log period start and end dates
• Cycle length tracking and averaging
• Period prediction for next 3 cycles
• Fertile window display
• Ovulation day prediction
• PMS symptom reminders
• Mood and symptom logging
• All data stored privately on device
• Works fully offline

✅ TRACKS
• Average cycle length
• Period duration
• Fertile window
• Spotting days
• Symptoms and notes

Download free — your data stays on your phone!""",
'new': '• Fertile window display\n• Mood logging\n• 3-cycle future prediction',
'tags': 'period tracker, menstrual cycle, ovulation, fertility, women health, cycle calendar'
},
'PhoneticApp': {
'name': 'Phonetic Alphabet — NATO Code',
'short': 'Learn NATO phonetic alphabet. Alpha, Bravo, Charlie...',
'full': """Master the NATO phonetic alphabet! Essential for pilots, military, emergency services, and anyone who spells things out over the phone.

📻 FEATURES
• Complete NATO alphabet (Alpha through Zulu)
• Learn mode with letter → codeword cards
• Quiz mode: show codeword, type the letter
• Reverse quiz: show letter, type the codeword
• Spell any word in phonetic alphabet
• Audio pronunciation for each codeword
• Works fully offline

✅ MEMORIZATION TIPS INCLUDED
Mnemonic tricks and visual associations for every letter.

Alfa, Bravo, Charlie... can you get to Zulu? Download free!""",
'new': '• Spell-any-word mode\n• Audio pronunciation\n• Quiz with reverse mode',
'tags': 'phonetic alphabet, NATO, alpha bravo charlie, military, aviation, spelling, radio'
},
'Phrasebook': {
'name': 'Phrasebook — Travel Phrases',
'short': 'Essential phrases in 10 languages. Travel with confidence!',
'full': """Travel anywhere with confidence! Phrasebook gives you the most essential phrases in 10 languages — organized by situation, with pronunciation guides.

📗 LANGUAGES
Spanish, French, German, Italian, Portuguese, Japanese, Chinese (Mandarin), Korean, Arabic, Russian

✨ FEATURES
• 500+ phrases per language
• Categories: Greetings, Directions, Food & Ordering, Shopping, Hotel, Emergency, Numbers
• Pronunciation guide in romanized text
• Tap to hear audio pronunciation
• Favorites for quick access
• Works fully offline

🌍 GREAT FOR
• Travelers and backpackers
• Business trips
• Language learners

Download free and communicate anywhere!""",
'new': '• Korean and Arabic added\n• Audio pronunciation\n• Emergency phrases category',
'tags': 'phrasebook, travel phrases, language, translation, Spanish, French, Japanese, travel'
},
'PianoKeyboard': {
'name': 'Piano Keyboard — Play & Learn',
'short': 'Play piano on your phone! 3 octaves, learn songs & chords.',
'full': """A full piano keyboard that fits in your pocket! Play freely, learn songs, or practice chords — 3 octaves of real piano sound.

🎹 FEATURES
• 3-octave scrollable keyboard
• Real piano sound samples
• Highlight mode: shows which keys a song needs
• 20+ popular songs to learn (highlighted keys)
• Chord reference: tap any chord to see the notes highlighted
• Note labels toggle (C, D, E… visible or hidden)
• Works fully offline

🎵 SONGS INCLUDED
Für Elise, Ode to Joy, Happy Birthday, Twinkle Twinkle, Jingle Bells, Canon in D, Moonlight Sonata intro, and more.

Download free and start playing!""",
'new': '• Song learning mode with key highlights\n• Chord reference mode\n• Note label toggle',
'tags': 'piano keyboard, piano, keyboard, music, learn piano, songs, chords, instrument'
},
'PinPull': {
'name': 'Pin Pull — Physics Puzzle',
'short': 'Pull pins to fill jars with liquid. Satisfying physics puzzle!',
'full': """Pull pins in the right order to guide liquid into the jar! A satisfying physics-based puzzle that's easy to understand but tricky to master.

📌 HOW TO PLAY
Pull pins to release colored liquids. Guide the liquid into the target jars without mixing the wrong colors. Think before you pull — order matters!

✨ FEATURES
• 200+ levels with increasing complexity
• Multiple liquids and color mixing
• Bombs, locks, and special pin types
• One-tap undo
• Level replay for 3-star rating
• Works fully offline

Colorful, satisfying, and oddly addictive. Download free!""",
'new': '• Color mixing mechanics\n• Bomb and lock pins\n• 60 new levels',
'tags': 'pin pull, physics puzzle, liquid, pins, casual, satisfying, brain teaser, pull pins'
},
'PixelArt': {
'name': 'Pixel Art — Color by Number',
'short': 'Color pixels to create amazing pixel art! Relaxing & fun.',
'full': """Create beautiful pixel art by coloring numbered grids! Pixel Art is a relaxing color-by-number experience for all ages.

🎨 HOW TO PLAY
Each cell has a number. Tap a color from the palette that matches the number, then tap or drag across cells to fill them. Complete the grid to reveal the finished artwork!

✨ FEATURES
• 200+ pixel art pictures
• Categories: Animals, Pokemon-style, Food, Space, Pixel Characters, Logos
• Zoom in for precision coloring
• Auto-fill same-number cells
• Progress saved automatically
• Works fully offline

Satisfying, meditative, and rewarding. Download free!""",
'new': '• Auto-fill same-number cells\n• Space and Characters categories\n• 50 new pictures',
'tags': 'pixel art, color by number, coloring, pixel, relaxing, art, creative, number art'
},
'PlantWater': {
'name': 'Plant Watering Reminder',
'short': 'Never kill your plants again! Set watering reminders.',
'full': """Keep your plants alive! Plant Watering Reminder tracks all your plants and tells you exactly when each one needs water.

🌱 FEATURES
• Add plants with name, type, and photo
• Set individual watering frequency (daily, every 3 days, weekly, etc.)
• Countdown to next watering for each plant
• Tap to log a watering and reset the countdown
• Notification reminders
• Plant care tips per plant type
• Works fully offline

🪴 SUPPORTED PLANT TYPES
Succulents, cacti, tropical, herbs, ferns, orchids, and custom types with your own watering schedule.

Download free and keep your green friends happy!""",
'new': '• Plant photo support\n• Care tips per type\n• Notification reminders',
'tags': 'plant watering, plant reminder, houseplants, garden, succulent, plant care, reminder'
},
'PomodoroTimer': {
'name': 'Pomodoro Timer — Focus Sessions',
'short': 'Work 25 min, rest 5 min. The Pomodoro Technique timer.',
'full': """Boost your productivity with the proven Pomodoro Technique! Work for 25 minutes, take a 5-minute break, repeat. After 4 rounds, take a longer break.

🍅 HOW IT WORKS
• 25-minute work session
• 5-minute short break
• 15-minute long break (every 4 pomodoros)
• Repeat and stay in the zone!

✨ FEATURES
• Customizable work/break durations
• Completed pomodoro counter
• Daily session goal setting
• Notification sound when timer ends
• Session history log
• Works fully offline

Download free and stop procrastinating!""",
'new': '• Customizable durations\n• Daily goal tracking\n• Session history log',
'tags': 'pomodoro, focus timer, productivity, work timer, study timer, 25 minutes, technique'
},
'PostureReminder': {
'name': 'Posture Reminder — Sit Straight',
'short': 'Regular reminders to fix your posture and protect your back.',
'full': """Save your back from desk work! Posture Reminder sends gentle notifications to check and correct your posture throughout the day.

🧘 FEATURES
• Customizable reminder interval (15 min to 2 hours)
• Gentle notification: "Check your posture!"
• Quick posture exercise tips with each reminder
• Daily posture score
• Reminder streak tracker
• Smart pause: turns off during non-working hours
• Works fully offline

💡 POSTURE TIPS INCLUDED
• Sitting position guide
• Screen height and distance
• Shoulder and neck exercises
• Desk stretches

Download free and protect your spine!""",
'new': '• Posture exercises with reminders\n• Smart work hours scheduling\n• Daily streak',
'tags': 'posture reminder, sitting posture, back health, ergonomics, neck pain, desk worker'
},
'PushUpCounter': {
'name': 'Push-Up Counter — Fitness Tracker',
'short': 'Count push-ups automatically. Track your fitness progress!',
'full': """Count your push-ups and track your fitness progress! Push-Up Counter helps you build a consistent push-up habit with goals, streaks, and progress charts.

💪 FEATURES
• Manual tap counting or automatic (using phone proximity sensor)
• Daily push-up goal setting
• Streak counter for consecutive days
• Weekly and monthly totals
• Personal best tracking
• 30-day push-up challenge program
• Works fully offline

📊 TRACKS
• Today's count
• Weekly total
• Best single-day count
• Current streak

Download free and get stronger every day!""",
'new': '• Proximity sensor auto-counting\n• 30-day challenge program\n• Progress charts',
'tags': 'push-up counter, fitness, workout, push ups, exercise, strength, gym, training'
},
'QRCodeGen': {
'name': 'QR Code Generator & Scanner',
'short': 'Generate and scan QR codes for URLs, text, WiFi & more.',
'full': """Create any QR code in seconds and scan codes with your camera! QR Code Generator covers everything from simple URLs to WiFi passwords and contact cards.

📷 GENERATE QR CODES FOR
• Website URLs
• Plain text
• WiFi network (SSID + password)
• Phone numbers
• Email addresses
• Contact cards (vCard)
• Location coordinates

✨ FEATURES
• Instant QR generation
• Custom colors and logo overlay (optional)
• Save QR codes to gallery
• Share QR codes directly
• Built-in scanner
• History of generated codes
• Works offline for generation (scanner needs camera)

Download free!""",
'new': '• WiFi QR code generator\n• Custom colors\n• History of past codes',
'tags': 'QR code, QR generator, QR scanner, barcode, WiFi QR, URL QR, contact QR'
},
'QuitSmoking': {
'name': 'Quit Smoking — Stop Counter',
'short': 'Track your smoke-free journey. See money saved & health gains.',
'full': """Your personal quit smoking companion! Track every milestone, see the money you're saving, and watch your health improve day by day.

🚭 FEATURES
• Set your quit date and cigarettes per day smoked
• Live timer: days, hours, minutes smoke-free
• Money saved calculator (based on pack cost you enter)
• Health recovery timeline (lungs, heart, cancer risk reducing)
• Cigarettes avoided counter
• Daily motivational message
• Milestone badges: 1 day, 1 week, 1 month, 1 year
• Works fully offline

💪 HEALTH MILESTONES SHOWN
• 20 minutes: Blood pressure normalizes
• 8 hours: Oxygen levels normalize
• 48 hours: Taste and smell improving
• 2 weeks: Circulation improving
• 1 year: Heart disease risk halved
• 10 years: Lung cancer risk halved

You can do this. Download free!""",
'new': '• Health recovery timeline\n• Milestone badges\n• Money saved calculator',
'tags': 'quit smoking, stop smoking, smoke-free, cigarette counter, health, nicotine, quit'
},
'RandomName': {
'name': 'Random Name Picker — Wheel',
'short': 'Pick a random name from your list. Spin the wheel!',
'full': """Need to pick someone randomly? Random Name Picker is the fairest way to choose from a list — just enter names and spin!

🎲 FEATURES
• Add unlimited names to the list
• Spin the wheel animation
• Remove picked names to avoid repeats
• Save name lists for reuse
• Wheel customization (colors)
• Works fully offline

✅ GREAT FOR
• Teachers picking students
• Team and group assignments
• Prize draws and giveaways
• Chore assignments
• Deciding who goes first

Download free and let fate decide!""",
'new': '• Saved name lists\n• Remove picked names option\n• Wheel color customization',
'tags': 'random name picker, spin wheel, name selector, random, draw, teacher, giveaway'
},
'RandomNumber': {
'name': 'Random Number Generator',
'short': 'Generate random numbers in any range. Dice, lottery & more.',
'full': """Generate truly random numbers for anything! Random Number Generator is fast, flexible, and works completely offline.

🎲 FEATURES
• Set any min and max range
• Generate single or multiple numbers at once
• No-repeat mode (unique numbers only)
• Sort results in order
• History of last 50 results
• Quick presets: dice (1–6), coin (0–1), lottery (1–49), d20
• Works fully offline

✅ USE CASES
• Lottery number picking
• Dice simulation
• Random sampling
• Contest draws
• Games and decisions

Download free!""",
'new': '• No-repeat unique numbers mode\n• Lottery preset\n• Multiple number generation',
'tags': 'random number, generator, random, lottery, dice, number picker, randomizer'
},
'RandomRecipe': {
'name': 'Random Recipe — What to Cook?',
'short': 'Can\'t decide what to cook? Get a random recipe suggestion!',
'full': """Stop staring at the fridge! Random Recipe gives you a delicious meal idea based on what you're in the mood for — or completely at random.

🍽️ FEATURES
• 200+ recipes across all cuisines
• Filter by: Cuisine, Meal Type, Time, Difficulty, Dietary
• Swipe to get another random suggestion
• Full recipe with ingredients and steps
• Save favorites
• "I have these ingredients" filter
• Works fully offline

🌍 CUISINES
Italian, Mexican, Chinese, Indian, Japanese, American, Mediterranean, Thai, and more.

Download free and solve "what's for dinner" forever!""",
'new': '• Dietary filter (vegetarian, vegan, etc.)\n• Ingredient-based search\n• Favorites list',
'tags': 'random recipe, what to cook, meal ideas, recipe app, cooking, food, dinner ideas'
},
'ReactionTime': {
'name': 'Reaction Time — Speed Test',
'short': 'Test your reaction time in milliseconds. How fast are you?',
'full': """How fast are your reflexes? Reaction Time measures how quickly you can react to a stimulus — with millisecond precision.

⚡ HOW TO PLAY
Wait for the screen to change color, then tap as fast as you can! Your reaction time is displayed in milliseconds.

✨ FEATURES
• Millisecond-precision timing
• Average reaction time over multiple attempts
• Personal best tracking
• Fake-out mode: avoid tapping on fake signals
• Daily challenge: 10-tap average
• Comparison: "You're faster than X% of users"
• Works fully offline

🏆 REACTION TIME BENCHMARKS
• < 150ms: Elite athlete level
• 150–200ms: Excellent
• 200–250ms: Average
• > 300ms: Room to improve!

Download free and test your speed!""",
'new': '• Fake-out mode\n• 10-tap average daily challenge\n• Benchmark comparisons',
'tags': 'reaction time, reflex test, speed test, milliseconds, reflexes, response time, fast'
},
'RecipeConverter': {
'name': 'Recipe Converter — Scale Servings',
'short': 'Scale any recipe up or down. Convert cups to grams!',
'full': """Scale any recipe to any number of servings! Recipe Converter also converts between cups, tablespoons, grams, ounces, and ml for every ingredient.

🍴 FEATURES
• Enter recipe servings, scale to your target
• All ingredient amounts automatically recalculate
• Unit conversions: cups ↔ ml, oz ↔ grams, tbsp ↔ ml
• Ingredient-specific density conversions (flour ≠ sugar)
• Temperature converter (°F ↔ °C) for ovens
• Works fully offline

🥣 UNIT CONVERSIONS
Cups, tablespoons, teaspoons, fluid oz, ml, grams, ounces, pounds, kilograms.

Download free and scale your cooking perfectly!""",
'new': '• Ingredient density conversions\n• Temperature converter\n• Scale up to 50 servings',
'tags': 'recipe converter, scale recipe, cooking, cups to grams, unit converter, baking, scale'
},
'RomanNumeralConverter': {
'name': 'Roman Numeral Converter',
'short': 'Convert numbers to Roman numerals instantly and back.',
'full': """Convert any number to Roman numerals or decode any Roman numeral expression instantly!

🔢 FEATURES
• Number → Roman numerals (1 to 3,999,999)
• Roman numerals → Number
• Real-time conversion as you type
• Full numeral explanation breakdown (e.g. XIV = X + IV = 10 + 4)
• Common uses: clocks, dates, movies, royalty
• Works fully offline

📚 LEARN THE RULES
• How subtractive notation works (IV, IX, XL, etc.)
• All numeral values: I, V, X, L, C, D, M
• Extended numerals for large numbers

Download free!""",
'new': '• Step-by-step breakdown\n• Extended large number support\n• Real-time conversion',
'tags': 'Roman numerals, converter, numbers, history, Latin, clock, numeral, translation'
},
'SalaryCalculator': {
'name': 'Salary Calculator — Take-Home Pay',
'short': 'Calculate your net salary after tax. Hourly to annual.',
'full': """Find out exactly what you take home! Salary Calculator converts between hourly, weekly, monthly, and annual pay — and estimates your after-tax income.

💵 FEATURES
• Convert hourly ↔ weekly ↔ monthly ↔ annual salary
• Estimated take-home after income tax (configurable rate)
• Overtime calculator
• Works for multiple currencies
• Works fully offline

💡 USE CASES
• Compare job offers (hourly vs salary)
• Understand your net monthly pay
• Calculate value of a raise
• Freelance rate converter

Estimates only — consult a tax professional for exact figures. Download free!""",
'new': '• Hourly to annual conversion\n• Tax rate estimator\n• Overtime calculator',
'tags': 'salary calculator, take home pay, net salary, hourly rate, annual salary, tax, income'
},
'SatisfyingSlime': {
'name': 'Satisfying Slime — Stress Relief',
'short': 'Poke, stretch and swirl virtual slime. Oddly satisfying!',
'full': """Experience the ultimate virtual stress toy! Satisfying Slime lets you poke, swirl, and stretch colorful slime with realistic physics.

🫧 FEATURES
• Realistic slime physics simulation
• Tap to poke, swipe to stretch, rotate to swirl
• Multiple slime types: glossy, fluffy, crunchy, butter
• 15+ color options
• Glitter, foam beads, and charms add-ins
• Satisfying sound effects (mutable)
• Works fully offline

Perfect for stress relief, ASMR fans, fidgeters, and anyone who just needs to chill for a minute. Download free!""",
'new': '• Crunchy slime type added\n• Glitter effects\n• 5 new colors',
'tags': 'slime, satisfying, stress relief, ASMR, fidget, slime simulator, relaxing, sensory'
},
'SavingsGoal': {
'name': 'Savings Goal — Money Tracker',
'short': 'Set a savings target and track your progress to it.',
'full': """Reach your savings goals! Set a target amount, log every contribution, and watch your progress bar fill up toward your dream.

🐷 FEATURES
• Set a goal name, target amount, and target date
• Log deposits and track progress
• Visual progress bar
• Estimated completion date based on contribution pace
• Multiple simultaneous goals
• All data stored locally
• Works fully offline

🎯 GREAT FOR
• Emergency fund
• Vacation savings
• New phone or laptop
• Car down payment
• Wedding fund
• Any big purchase

Download free and start saving!""",
'new': '• Multiple goals at once\n• Estimated completion date\n• Deposit history',
'tags': 'savings goal, money tracker, savings app, financial goal, piggy bank, budget, target'
},
'ScienceQuiz': {
'name': 'Science Quiz — STEM Trivia',
'short': 'Test your science knowledge! Physics, chemistry, biology & more.',
'full': """From atoms to galaxies — Science Quiz tests your STEM knowledge across every science discipline!

🔬 FEATURES
• 600+ science questions
• Subjects: Physics, Chemistry, Biology, Astronomy, Earth Science, Technology
• Difficulty levels: Easy → Expert
• Answer explanations with each question
• Daily science question
• Score tracking
• Works fully offline

🔭 TOPICS INCLUDE
Newton's laws, periodic table, cell biology, evolution, quantum physics basics, solar system, ecosystems, and more.

Download free and geek out!""",
'new': '• Technology subject added\n• Answer explanations\n• Expert difficulty level',
'tags': 'science quiz, STEM, physics, chemistry, biology, trivia, education, science facts'
},
'ScientificCalc': {
'name': 'Scientific Calculator',
'short': 'Full scientific calculator with history, trig & constants.',
'full': """A full-featured scientific calculator with a clean interface! Handles everything from basic arithmetic to trigonometry, logarithms, and mathematical constants.

🧮 FEATURES
• Basic operations: +, −, ×, ÷
• Scientific: sin, cos, tan (and inverses), log, ln, exp
• Powers: x², x³, xⁿ, √, ∛
• Constants: π, e, φ (golden ratio)
• Brackets and order of operations
• Calculation history (last 20)
• Degree / radian mode toggle
• Works fully offline

Perfect for students, engineers, scientists, and anyone who needs more than a basic calculator. Download free!""",
'new': '• Calculation history\n• Golden ratio constant\n• Degree/radian mode toggle',
'tags': 'scientific calculator, calculator, trigonometry, math, sin cos tan, log, engineering'
},
'ScoreTracker': {
'name': 'Score Tracker — Game Scorekeeper',
'short': 'Track scores for any game. Up to 8 players or teams.',
'full': """Keep score for any game! Score Tracker works for card games, board games, sports, trivia nights, and any competition with up to 8 players or teams.

📊 FEATURES
• Up to 8 players or teams
• Add or subtract any point value
• Running total display
• Round-by-round history
• Set a target score (first to X wins)
• Sort by score
• New round button to reset per-round tracking
• Works fully offline

✅ GREAT FOR
• Card games (Rummy, Phase 10, Hearts)
• Board games (Scrabble, Ticket to Ride)
• Sports (darts, bowling, pool)
• Trivia nights
• Any competition!

Download free!""",
'new': '• 8-player support\n• Target score win condition\n• Round history log',
'tags': 'score tracker, scorekeeper, game score, card games, board games, points, scoreboard'
},
'ScrewPuzzle': {
'name': 'Screw Puzzle — Unscrew & Sort',
'short': 'Unscrew bolts and sort them by color. Satisfying puzzle!',
'full': """Unscrew the bolts, sort them by color, and clear the board! Screw Puzzle is a satisfying and surprisingly addictive sorting puzzle.

🔩 HOW TO PLAY
Boards have colored screws stacked in holes. Unscrew the top bolt and move it to a hole where it belongs. Group same-colored screws together to remove them. Clear all screws to win!

✨ FEATURES
• 300+ levels with increasing complexity
• Multiple screw colors and hole types
• No time limit — think at your own pace
• Undo button
• Daily new puzzle
• Works fully offline

Strangely satisfying. Deeply addictive. Download free!""",
'new': '• Daily puzzle\n• 100 new levels\n• New screw types',
'tags': 'screw puzzle, bolt, unscrew, sorting puzzle, casual, satisfying, brain teaser'
},
'ShapesColors': {
'name': 'Shapes & Colors — Kids Learning',
'short': 'Teach kids shapes and colors! Interactive learning for toddlers.',
'full': """Help your little one learn shapes and colors! Shapes & Colors is a bright, friendly learning app for toddlers and preschoolers.

🟦 FEATURES
• Learn 12 shapes: circle, square, triangle, star, heart, and more
• Learn 10 colors with real-world examples
• Tap shapes to hear their names
• Quiz mode: "Tap the circle!"
• Matching game: match shapes to outlines
• Color sorting game
• Works fully offline

Designed for ages 18 months–4 years. Large, bright, easy-to-tap elements. Download free!""",
'new': '• Color sorting game\n• Matching game mode\n• 4 new shapes',
'tags': 'shapes colors, kids learning, toddler, preschool, shapes, colors, education, children'
},
'SimonSays': {
'name': 'Simon Says — Memory Game',
'short': 'Watch the color sequence and repeat it! Classic Simon game.',
'full': """The classic Simon memory game! Watch the color sequence light up, then repeat it back in the same order. Each round adds one more step!

🟩 HOW TO PLAY
4 colored buttons flash in a sequence. Watch carefully, then tap them back in the same order. Correct = one more step added. Wrong = game over!

✨ FEATURES
• Classic 4-color Simon gameplay
• 5 speed settings
• Score = longest sequence completed
• Personal best tracking
• Flash and sound feedback
• Daily challenge mode
• Works fully offline

Easy to learn, surprisingly hard to master. Download free!""",
'new': '• Daily challenge mode\n• 5 difficulty speeds\n• Visual and audio feedback',
'tags': 'Simon Says, memory game, color sequence, classic, brain training, recall, Simon'
},
'SleepTracker': {
'name': 'Sleep Tracker — Rest Log',
'short': 'Log your sleep, track quality, and build better sleep habits.',
'full': """Improve your sleep, one night at a time! Sleep Tracker helps you log your sleep times, rate your quality, and identify patterns that affect how rested you feel.

😴 FEATURES
• Log bedtime and wake time with one tap
• Sleep quality rating (1–5 stars)
• Optional dream notes and mood on waking
• Weekly average sleep duration chart
• Best/worst sleep hours identified
• Bedtime reminder notification
• Sleep hygiene tips
• Works fully offline

📊 INSIGHTS
• Average sleep per night
• Days you hit 8 hours
• Best and worst sleep days of the week

Download free and start sleeping better!""",
'new': '• Weekly average chart\n• Bedtime reminder\n• Sleep pattern insights',
'tags': 'sleep tracker, sleep log, rest, insomnia, sleep quality, bedtime, health tracker'
},
'SlidingTiles': {
'name': 'Sliding Tiles — 15 Puzzle',
'short': 'Classic sliding tile puzzle. Sort 1–15 with fewest moves!',
'full': """The classic 15-puzzle! Slide tiles into order by moving them into the empty space. Simple concept, genuinely challenging execution.

🧩 HOW TO PLAY
You have a 4×4 grid with tiles numbered 1–15 and one empty space. Slide tiles into the empty space to rearrange them in order from 1–15.

✨ FEATURES
• Classic 3×3 (8-puzzle) and 4×4 (15-puzzle) modes
• 5×5 challenge mode
• Move counter and timer
• Best moves and best time tracking
• Scramble and solve animation
• Solve hint: shows next best move
• Works fully offline

A timeless puzzle that sharpens spatial reasoning. Download free!""",
'new': '• 5×5 challenge mode\n• Move hint system\n• Best time tracking',
'tags': 'sliding tiles, 15 puzzle, 8 puzzle, sliding puzzle, classic, logic, tile puzzle'
},
'SnakeGame': {
'name': 'Snake Game — Classic Arcade',
'short': 'Eat food, grow longer, don\'t hit yourself! Classic Snake.',
'full': """The original mobile game! Guide your snake to eat food, grow longer, and avoid hitting yourself or the walls.

🐍 HOW TO PLAY
Swipe to change direction. Eat the food dots to grow. Don't hit the walls or your own body! The longer you get, the harder it becomes.

✨ FEATURES
• Classic gameplay with modern smooth controls
• 4 grid sizes: small → extra large
• 3 speed settings
• Multiple snake skins to unlock
• High score tracking
• Power-ups: invincibility, slow-down, bonus food
• Works fully offline

Timeless fun that never gets old. Download free!""",
'new': '• Power-ups added\n• Snake skin unlockables\n• Smooth swipe controls',
'tags': 'snake game, classic snake, Nokia game, arcade, retro, eat, grow, casual'
},
'SobrietyCounter': {
'name': 'Sobriety Counter — Clean Days',
'short': 'Count your sober days. Track milestones and stay strong.',
'full': """Your personal sobriety companion. Count every day sober, celebrate milestones, and stay motivated on your journey to freedom.

🌟 FEATURES
• Set your sobriety start date
• Live counter: days, hours, minutes, seconds clean
• Milestone achievements: 1 day, 1 week, 1 month, 90 days, 1 year...
• Daily motivational quote
• Journal for personal notes
• Widget for home screen
• Works fully offline

💪 MILESTONES CELEBRATED
• 24 hours, 1 week, 30 days, 60 days, 90 days, 6 months, 1 year, and beyond.

Recovery is possible. You are not alone. Download free!""",
'new': '• Home screen widget\n• Daily motivation quotes\n• Personal journal',
'tags': 'sobriety counter, sober, clean days, recovery, addiction, alcohol, AA, 90 days'
},
'Sokoban': {
'name': 'Sokoban — Box Pushing Puzzle',
'short': 'Push boxes onto targets. Classic Japanese logic puzzle!',
'full': """The classic Japanese box-pushing puzzle! Push boxes onto the target squares using only your moves — with no undo of a bad push (in hard mode)!

📦 HOW TO PLAY
Move your character to push boxes onto marked target squares. You can only push (not pull) boxes. Plan every move carefully — bad moves can make puzzles unsolvable!

✨ FEATURES
• 300+ classic Sokoban levels
• Beginner to expert difficulty
• Full undo support
• Level restart button
• Move and push counters
• Classic and themed visual styles
• Works fully offline

A true classic of pure logic puzzles. Download free!""",
'new': '• 100 new levels\n• Themed visual styles\n• Move/push counter',
'tags': 'sokoban, box puzzle, push boxes, logic, Japanese puzzle, classic, brain teaser'
},
'SolarSystem': {
'name': 'Solar System — Space Explorer',
'short': 'Explore all 8 planets with facts, sizes & distances!',
'full': """Explore our solar system from your pocket! Solar System gives you beautiful, detailed information about every planet, moon, and major body in our cosmic neighborhood.

🌍 CONTENT
• All 8 planets with fact cards
• Size and distance comparisons
• Planet rotation and orbit speeds
• Notable moons per planet
• Dwarf planets: Pluto, Eris, Ceres
• The Sun, asteroid belt, and Kuiper belt
• Real scale comparisons

✨ FEATURES
• Interactive 3D-style planet viewer
• Fun facts for each planet
• Quiz mode: test your solar system knowledge
• Works fully offline

Perfect for curious minds of all ages. Download free!""",
'new': '• Dwarf planets added\n• Solar system quiz mode\n• Scale comparison visuals',
'tags': 'solar system, planets, space, astronomy, science, Earth, Mars, Jupiter, NASA, kids'
},
'Solitaire': {
'name': 'Solitaire — Classic Klondike',
'short': 'Classic Klondike solitaire. Draw 1 or 3, win conditions.',
'full': """The definitive classic Solitaire game! Clean interface, smooth card animations, and the proper Klondike rules you know and love.

🃏 HOW TO PLAY
Sort all cards into the four foundation piles by suit from Ace to King. Move cards between tableau columns using red-on-black, black-on-red alternating color rules.

✨ FEATURES
• Draw 1 and Draw 3 modes
• Auto-complete when near end
• Unlimited undo
• Hint system
• Win streak tracking
• Score mode and time mode
• Works fully offline

One of the most played card games of all time — now on your phone. Download free!""",
'new': '• Draw 1 and Draw 3 modes\n• Auto-complete feature\n• Win streak tracking',
'tags': 'solitaire, klondike, card game, classic, patience, cards, solo game'
},
'SoundBoard': {
'name': 'Soundboard — Funny Sound Effects',
'short': '100+ funny sound effects at your fingertips. Tap & laugh!',
'full': """Your instant sound effect machine! Tap any button to play a hilarious or classic sound effect — perfect for pranks, laughs, and parties.

🔊 SOUND CATEGORIES
• Funny (fart, rimshot, sad trombone, fail horn)
• Animals (cat, dog, cow, duck, lion)
• Crowd reactions (applause, boo, gasp, laughter)
• Classic (airhorn, notification, bell, alarm)
• Scary (scream, thunder, ghost, horror sting)
• Custom — record your own!

✨ FEATURES
• 100+ sounds included
• Play multiple sounds simultaneously
• Favorites section
• Works fully offline

Download free and add some sound effects to your life!""",
'new': '• Record custom sounds\n• Play multiple sounds at once\n• Favorites section',
'tags': 'soundboard, sound effects, funny, fart, airhorn, pranks, party, noises, reactions'
},
'SpellingBee': {
'name': 'Spelling Bee — Word Challenge',
'short': 'Spell as many words as possible from 7 letters. Daily puzzle!',
'full': """Make as many words as you can from just 7 letters! Spelling Bee is an addictive word puzzle where one letter must appear in every word you spell.

🐝 HOW TO PLAY
You get 7 letters arranged in a honeycomb. One center letter is required in every word. Find words of 4+ letters. Find the "pangram" (uses all 7 letters) for maximum points!

✨ FEATURES
• Fresh daily puzzle
• Archive of past puzzles
• Dictionary lookup for all valid words
• Pangram hint
• Score ranks from Beginner to Genius
• Works fully offline

Fans of NYT Spelling Bee will love this! Download free!""",
'new': '• Daily puzzle with archive\n• Pangram hint system\n• Score ranking tiers',
'tags': 'spelling bee, word puzzle, daily game, NYT, letters, vocabulary, word game, honeycomb'
},
'SpinBottle': {
'name': 'Spin the Bottle — Party Game',
'short': 'Spin the virtual bottle! Pairs people up for fun challenges.',
'full': """Spin the bottle for any party game! Point your phone flat, spin, and whoever it lands on is the chosen one!

🍾 HOW TO PLAY
Add player names. Place phone flat on a table. Tap spin — the bottle spins and points at a random player!

✨ FEATURES
• Add up to 10 players
• Realistic spinning animation
• Pair players for truth or dare, compliments, challenges, etc.
• Can be used as a random person selector
• Works fully offline

Spin the Bottle is a party classic that works for any group activity. Download free!""",
'new': '• Up to 10 players\n• Realistic spin physics\n• Works as random selector',
'tags': 'spin the bottle, party game, group game, spinner, random selector, fun, party'
},
'SportsQuiz': {
'name': 'Sports Quiz — All Sports Trivia',
'short': 'Test your sports knowledge! Football, NBA, tennis & more.',
'full': """The ultimate sports trivia app! Test your knowledge across every major sport with hundreds of questions.

🏆 SPORTS COVERED
• Football (Soccer) — Premier League, World Cup, Champions League
• Basketball (NBA)
• American Football (NFL)
• Baseball (MLB)
• Tennis
• Golf
• Olympics
• Formula 1
• Rugby
• Cricket

✨ FEATURES
• 700+ sports trivia questions
• Sport filter
• Difficulty levels
• Daily sports question
• Score tracking
• Works fully offline

Download free and prove you're the ultimate sports fan!""",
'new': '• F1 and cricket categories\n• Daily question mode\n• Difficulty levels',
'tags': 'sports quiz, football trivia, NBA, tennis, Olympics, sports knowledge, fan quiz'
},
'StepCounter': {
'name': 'Step Counter — Pedometer',
'short': 'Count your daily steps. Track distance and calories.',
'full': """Track your daily steps with the built-in pedometer! Step Counter uses your phone's motion sensor to count steps, estimate distance, and calculate calories burned.

👟 FEATURES
• Real-time step counting using accelerometer
• Daily step goal (default 10,000 steps)
• Distance estimate (adjustable stride length)
• Calories burned estimate
• Weekly step history chart
• Daily goal streak
• Works fully offline

📊 DAILY STATS
• Steps taken
• Distance (km or miles)
• Calories burned
• Goal completion percentage

Download free and get moving!""",
'new': '• Weekly step history chart\n• Calories estimate\n• Goal streak tracking',
'tags': 'step counter, pedometer, steps, walking, fitness, health, calorie counter, distance'
},
'StopwatchTimer': {
'name': 'Stopwatch & Timer — All in One',
'short': 'Stopwatch with laps, countdown timer, and interval timer.',
'full': """Three timer tools in one clean app! Stopwatch with lap tracking, countdown timer, and an interval timer for workouts.

⏱️ FEATURES
• Stopwatch: start/stop/reset with lap recording
• Countdown: set any hours/minutes/seconds
• Interval timer: set work and rest intervals with round count
• Loud alarm when countdown/interval finishes
• Screen stays on during use
• Works fully offline

✅ GREAT FOR
• Timing workouts and runs
• Cooking
• Presentations and standups
• Sports and games
• Any timed activity

Download free!""",
'new': '• Interval timer mode\n• Lap history\n• Screen always on option',
'tags': 'stopwatch, timer, countdown, interval timer, lap timer, workout timer, clock'
},
'StroopTest': {
'name': 'Stroop Test — Brain Challenge',
'short': 'Name the ink color, not the word! Classic cognitive test.',
'full': """The famous Stroop Effect test! Words appear in different ink colors — say the COLOR of the ink, not the word itself. Sounds easy. Your brain will disagree.

🧠 HOW TO PLAY
You see a color word (e.g. "RED") printed in blue ink. Tap the color of the ink (blue), not the word (red). Do it as fast as possible!

✨ FEATURES
• Classic Stroop test
• Reverse Stroop mode (tap the word, ignore the color)
• Timed rounds: 30s, 60s, 2 minutes
• Accuracy and speed score
• Personal best tracking
• Daily Stroop challenge
• Works fully offline

The Stroop Effect is a real psychological phenomenon. Download free and test your cognitive control!""",
'new': '• Reverse Stroop mode\n• Daily challenge\n• Accuracy percentage tracking',
'tags': 'stroop test, brain test, cognitive, psychology, color word, attention, reaction'
},
'Sudoku': {
'name': 'Sudoku — Classic Number Puzzle',
'short': 'Classic Sudoku with 1000+ puzzles. Easy to Expert levels.',
'full': """The world's most popular number puzzle! Fill the 9×9 grid so every row, column, and 3×3 box contains digits 1–9 exactly once.

🔢 FEATURES
• 1000+ Sudoku puzzles
• 4 difficulty levels: Easy, Medium, Hard, Expert
• Mistake highlighting (optional)
• Notes/pencil marks for candidates
• Undo and redo
• Auto-check for errors
• Hint: reveals one correct cell
• Daily Sudoku challenge
• Timer with best time tracking
• Works fully offline

From beginner to advanced — there's a puzzle for everyone. Download free!""",
'new': '• Daily challenge puzzle\n• Expert difficulty\n• Candidate notes/pencil marks',
'tags': 'sudoku, number puzzle, logic, 9x9 grid, brain teaser, daily puzzle, classic'
},
'Sumplete': {
'name': 'Sumplete — Number Deletion Puzzle',
'short': 'Delete numbers so rows and columns hit target sums exactly.',
'full': """The addictive number deletion puzzle! Keep or delete numbers in the grid so that every row and column adds up to its target sum.

➕ HOW TO PLAY
Each row and column shows a target sum. Tap numbers to delete them (or keep them). The remaining numbers in each line must total exactly the target. Only one solution is valid!

✨ FEATURES
• Grid sizes: 3×3 to 7×7
• 300+ puzzles
• Difficulty levels: Easy to Expert
• Hint: reveals correct keep/delete for one cell
• Daily Sumplete challenge
• Works fully offline

As addictive as Sudoku, but different enough to feel fresh. Download free!""",
'new': '• 7×7 grid size\n• Daily puzzle mode\n• Hint system',
'tags': 'sumplete, number puzzle, deletion puzzle, sum, logic, grid, brain teaser, daily'
},
'TallyCounter': {
'name': 'Tally Counter — Click Counter',
'short': 'Simple tally counter. Count anything with one big tap.',
'full': """The most satisfying tally counter on Android! One big button, one count. Simple and reliable for any counting task.

🔢 FEATURES
• Giant tap button — hard to miss
• +1 or custom increment per tap
• Decrement button to correct mistakes
• Set a target and see progress bar
• Multiple named counters (save and switch)
• Reset with confirmation
• Vibration feedback option
• Works fully offline

✅ USES
• People counting (events, doorways)
• Inventory
• Laps
• Prayer counting (tasbih, rosary)
• Reps at gym
• Anything countable!

Download free!""",
'new': '• Multiple saved counters\n• Target progress bar\n• Vibration feedback',
'tags': 'tally counter, click counter, count, tally, inventory, lap counter, clicker, manual'
},
'TapColor': {
'name': 'Tap Color — Reflex Game',
'short': 'Tap the matching color before time runs out! Fast reflexes!',
'full': """A fast, colorful reflex game! Tap the color shown before the timer runs out. Sounds easy — it gets wild fast!

🎨 HOW TO PLAY
A color name flashes on screen. Tap the matching colored button from the options shown. Get it right fast to keep your streak going!

✨ FEATURES
• Increasing speed as your streak grows
• Multiple game modes: Color Name match, Color Block match, Mixed
• High score tracking
• Daily color challenge
• Works fully offline

Trains visual processing speed, color recognition, and quick decision-making. Download free!""",
'new': '• Mixed mode combining word and color\n• Daily challenge\n• Speed progression',
'tags': 'tap color, reflex game, color game, speed, reaction, color recognition, fast tap'
},
'TetrisGame': {
'name': 'Block Drop — Tetris Style Puzzle',
'short': 'Drop and rotate blocks to clear lines! Classic Tetris-style game.',
'full': """The timeless block-dropping puzzle! Drop and rotate falling pieces to build complete lines and clear them before the stack reaches the top.

🟦 HOW TO PLAY
Pieces fall from the top — swipe to move left/right, tap to rotate, swipe down to drop faster. Complete a full horizontal line to clear it and score points. Game over when pieces reach the top!

✨ FEATURES
• Classic 7-piece tetromino set
• Smooth swipe and tap controls
• Ghost piece shows where block will land
• Hold piece slot
• Score multiplier for multi-line clears
• Level speed progression
• High score tracking
• Works fully offline

Download free and stack those blocks!""",
'new': '• Ghost piece preview\n• Hold piece slot\n• Multi-line clear multiplier',
'tags': 'tetris, block drop, tetrominoes, line clear, arcade, classic, falling blocks, puzzle'
},
'TextCase': {
'name': 'Text Case Converter',
'short': 'Convert text to UPPER, lower, Title, camelCase & more.',
'full': """Convert any text between case formats instantly! Paste your text and tap any format to transform it immediately.

🔡 CASE FORMATS
• UPPERCASE
• lowercase
• Title Case
• Sentence case
• camelCase
• PascalCase
• snake_case
• kebab-case
• SCREAMING_SNAKE_CASE
• dot.case
• Toggle (flip every letter's case)

✨ FEATURES
• Instant conversion
• Copy result to clipboard
• Convert multiple paragraphs at once
• Works fully offline

Download free and convert in one tap!""",
'new': '• PascalCase and kebab-case added\n• Multi-paragraph support\n• Copy to clipboard',
'tags': 'text case, case converter, uppercase, camelCase, snake_case, developer, text tool'
},
'ThisOrThat': {
'name': 'This or That — Quick Pick Game',
'short': 'Pick your preference: 200+ This or That dilemmas!',
'full': """Quick, fun, and endlessly debatable! This or That presents you with two options and you just have to pick one — no overthinking allowed!

🤔 FEATURES
• 200+ This or That questions
• Categories: Food, Travel, Entertainment, Life, Tech, Fun
• Timer challenge mode: answer 10 in 10 seconds
• See what percentage of people chose each option
• Competitive mode: compare answers with friends
• Works fully offline

✅ GREAT FOR
• Road trips and travel
• Parties and icebreakers
• Getting to know someone
• Just killing time

Download free and start picking!""",
'new': '• Community percentage results\n• Competitive compare mode\n• Timer challenge mode',
'tags': 'this or that, would you rather, preferences, choices, party game, icebreaker, fun'
},
'TimesTable': {
'name': 'Times Table — Multiplication Drill',
'short': 'Master the 12×12 times table. Drills, quizzes & speed tests!',
'full': """Master every times table from 1×1 to 12×12! Times Table offers flashcard drilling, quiz mode, and speed tests to build your multiplication fluency.

✖️ FEATURES
• Full 1–12 times table reference grid
• Drill mode: rapid-fire flashcards for any table
• Quiz mode: multiple choice for accuracy
• Speed test: how many correct in 60 seconds?
• Mastery tracker per table (0–100%)
• Star rating for each times table
• Works fully offline

📊 TRACKS PROGRESS
• Mastery per table
• Overall accuracy rate
• Speed improvement
• Daily practice streak

Download free and master multiplication!""",
'new': '• Mastery percentage per table\n• Speed test mode\n• Practice streak',
'tags': 'times table, multiplication, 12 times, maths, school, kids, arithmetic, drill, quiz'
},
'TimezoneConverter': {
'name': 'Timezone Converter — World Clock',
'short': 'Convert times between 500+ cities and time zones instantly.',
'full': """Plan calls, meetings, and travel across time zones with instant time conversion for 500+ cities worldwide!

🌐 FEATURES
• 500+ cities and time zones
• Convert any time to any time zone instantly
• Add multiple cities for comparison view
• Current time in all added cities
• DST (Daylight Saving Time) aware
• Meeting planner: find overlap times for groups
• Works offline with current device time

✅ GREAT FOR
• Remote team meeting planning
• International travel
• Calling friends and family abroad
• Stock market and trading hours

Download free!""",
'new': '• Meeting planner overlap tool\n• DST aware\n• 500+ cities',
'tags': 'timezone converter, world clock, time zones, DST, meeting planner, international, time'
},
'TipCalculator': {
'name': 'Tip Calculator — Bill & Gratuity',
'short': 'Calculate the perfect tip and split it between everyone.',
'full': """The cleanest tip calculator on Android! Enter the bill, choose your tip percentage, and split the total between as many people as you need.

💰 FEATURES
• Tip percentage: 10%, 15%, 18%, 20%, 25%, custom
• Split between 1–20 people
• Round up option per person
• Running total display
• Quick tip buttons for fast service
• Works fully offline

Perfect for restaurants, bars, taxis, hotel service, and any tipped service. Download free!""",
'new': '• Round up per person option\n• Quick tip buttons\n• Custom tip percentage',
'tags': 'tip calculator, gratuity, bill split, restaurant, tipping, service charge, calculator'
},
'TripleMatch': {
'name': 'Triple Match 3D — Sort & Collect',
'short': 'Collect 3 matching tiles to clear them. 3D puzzle game!',
'full': """Pick tiles from a stacked 3D pile and collect 3 matching ones to clear them from your tray! A beautifully satisfying sorting puzzle.

🃏 HOW TO PLAY
Tap tiles from the pile to add them to your 7-slot tray. When 3 matching tiles are in the tray, they auto-clear! Clear all tiles from the pile before the tray fills up.

✨ FEATURES
• Hundreds of levels with increasing complexity
• Beautifully illustrated tile designs
• Power-ups: shuffle, undo, extend tray
• Daily challenge level
• Works fully offline

One of the most addictive casual puzzle games. Download free!""",
'new': '• Daily challenge level\n• Power-up system\n• New tile design packs',
'tags': 'triple match, 3D match, tile matching, sort, collect, casual, puzzle, addictive'
},
'TrueOrFalse': {
'name': 'True or False — Trivia Quiz',
'short': 'Is it true or false? 500+ quick-fire fact questions!',
'full': """Quick-fire trivia with just two answers: True or False! Test your general knowledge with 500+ questions across every topic.

✅ FEATURES
• 500+ True/False questions
• Topics: Science, History, Geography, Pop Culture, Nature, Sports, Tech
• Timed mode: 5 seconds per question
• Untimed relaxed mode
• Streak tracking for consecutive correct answers
• Fact explanation after each answer
• Daily challenge
• Works fully offline

Fast, fun, and perfect for any spare moment. Download free!""",
'new': '• Fact explanations on answers\n• 5-second timed mode\n• Daily challenge',
'tags': 'true or false, trivia, quiz, facts, true false game, knowledge, brain teaser'
},
'TruthOrDare': {
'name': 'Truth or Dare — Party Game',
'short': '500+ truths and dares for all ages. Epic party game!',
'full': """The classic party game with 500+ Truth and Dare prompts for every age and occasion!

🎯 HOW TO PLAY
Players take turns choosing Truth (answer an honest question) or Dare (complete a challenge). Works for 2+ players of any age!

🎮 MODES
• Kids (completely family-safe)
• Teen (school-appropriate fun)
• Adult (mild — no inappropriate content)
• Party (funny, silly, active dares)
• Custom — add your own truths and dares!

✨ FEATURES
• 500+ unique prompts
• 4 age/spice modes
• Spin wheel to choose who goes next
• Works fully offline

Download free and get the party going!""",
'new': '• Custom prompts added\n• Spin wheel for player selection\n• 4 difficulty modes',
'tags': 'truth or dare, party game, fun, group game, friends, dares, truths, party night'
},
'TwentyQuestions': {
'name': '20 Questions — Yes or No Game',
'short': 'Think of something and let the AI guess it in 20 questions!',
'full': """The classic 20 Questions game! Think of an animal, object, or person — the app asks yes/no questions and tries to guess what you're thinking in 20 attempts.

❓ HOW TO PLAY
Think of something. The app asks binary questions (yes/no). Answer honestly. Can it guess your mystery item in 20 questions or fewer?

✨ FEATURES
• Smart question tree with 1000+ possible answers
• Categories: Animals, Objects, Food, Famous People, Places
• Categories mode or free-for-all
• Track how many questions it took
• Play against a friend in 2-player mode
• Works fully offline

Download free and see if you can stump it!""",
'new': '• 2-player competitive mode\n• Category selection\n• 1000+ answer database',
'tags': '20 questions, yes or no, guessing game, animal vegetable mineral, classic game'
},
'TwoTruthsOneLie': {
'name': 'Two Truths One Lie — Party Game',
'short': 'Share 2 truths and 1 lie. Can your friends spot the lie?',
'full': """The party game everyone loves! Share two true statements and one lie — can your friends (or AI mode) figure out which is the lie?

🤫 FEATURES
• Prompt cards to spark interesting truths
• AI guesser mode (play solo)
• Group scoring: points for stumping or guessing correctly
• 200+ pre-written examples for inspiration
• Custom round (write your own)
• Works fully offline

✅ GREAT FOR
• Icebreakers at parties
• Team building at work
• Getting to know new friends
• First date ideas

Download free and start lying (truthfully)!""",
'new': '• AI guesser solo mode\n• Group scoring system\n• 200+ example prompts',
'tags': 'two truths one lie, party game, icebreaker, bluffing, group game, social, fun'
},
'UkuleleChords': {
'name': 'Ukulele Chords — Chord Library',
'short': 'Every ukulele chord with clear diagrams. Learn & play!',
'full': """The complete ukulele chord reference! Browse hundreds of chord diagrams for every key — from simple 3-chord beginner songs to complex jazz voicings.

🎸 FEATURES
• 400+ chord diagrams for ukulele (GCEA tuning)
• All major, minor, 7th, sus, dim, aug chords
• Every key from A to G#
• Clear fretboard diagrams with finger numbers
• Audio chord playback
• Beginner chord section with the most-used chords
• Chord progression guide
• Works fully offline

🎵 ALSO INCLUDES
• Popular song chord progressions
• Baritone ukulele mode (DGBE tuning)
• Works for left-handed players (flip option)

Download free and start strumming!""",
'new': '• Audio playback\n• Baritone mode\n• Left-hand flip option',
'tags': 'ukulele chords, ukulele, chord diagrams, music, learn ukulele, strum, GCEA'
},
'UnitConverter': {
'name': 'Unit Converter — All Units',
'short': 'Convert length, weight, temperature, speed & 20 more units.',
'full': """The most comprehensive unit converter app! Convert between every unit of measurement across 25+ categories.

📏 CATEGORIES
Length, Weight/Mass, Temperature, Speed, Volume, Area, Time, Data (bytes/GB), Energy, Power, Pressure, Fuel Economy, Angle, Force, Frequency, and more.

✨ FEATURES
• Instant conversion as you type
• All unit combinations supported
• Search any unit by name
• Favorite units for quick access
• Works fully offline

🌍 SUPPORTS
Metric, Imperial, and US customary units. All scientific SI units included.

Download free!""",
'new': '• Search by unit name\n• Favorite units\n• 5 new categories added',
'tags': 'unit converter, measurement, length, weight, temperature, metric, imperial, convert'
},
'VATCalculator': {
'name': 'VAT Calculator — Tax Included',
'short': 'Calculate VAT / GST instantly. Add or remove tax from price.',
'full': """The fastest VAT/GST calculator! Add tax to a price or remove it — both ways, instantly.

💶 FEATURES
• Add VAT: enter price + rate, get total
• Remove VAT: enter gross price + rate, get net
• Common rate presets: 5%, 10%, 15%, 20%, 25%
• Custom rate for any country
• Multiple item calculation
• Works fully offline

🌍 WORKS FOR
VAT (UK, EU), GST (Australia, India, Canada), Sales Tax (USA), and any percentage-based tax system.

Download free!""",
'new': '• Add and remove VAT modes\n• Multiple item calculator\n• Country rate presets',
'tags': 'VAT calculator, GST, tax, sales tax, price including tax, excluding tax, percentage'
},
'WaterReminder': {
'name': 'Water Reminder — Stay Hydrated',
'short': 'Track daily water intake and get reminders to drink more.',
'full': """Stay properly hydrated every day! Water Reminder tracks your water intake and sends gentle reminders throughout the day.

💧 FEATURES
• Set your daily water goal (default 2000ml / 8 cups)
• Log each drink with one tap (cup, bottle, custom ml)
• Progress bar toward daily goal
• Customizable reminder schedule (every 1–3 hours)
• Weekly hydration history
• Adjusts goal for body weight
• Works fully offline

📊 DAILY STATS
• ML consumed today
• Glasses remaining
• Goal completion percentage
• Weekly average

Download free and drink more water!""",
'new': '• Weight-based goal calculation\n• Weekly history chart\n• Flexible reminder schedule',
'tags': 'water reminder, hydration, drink water, water tracker, health, daily water, 8 glasses'
},
'WhackaMole': {
'name': 'Whack-a-Mole — Tap Fast!',
'short': 'Tap moles as fast as they pop up! Classic arcade fun.',
'full': """The classic carnival game on your phone! Tap moles as they pop up from the holes before they hide again. Miss too many and it's game over!

🔨 HOW TO PLAY
Moles pop up randomly from 9 holes. Tap them before they disappear! More moles appear as the game progresses. Golden moles are worth extra points!

✨ FEATURES
• Classic 3×3 and 4×4 hole grids
• Progressive speed increase
• Golden moles for bonus points
• Miss counter
• High score tracking
• Works fully offline

Great for kids and adults who want fast reflex fun! Download free!""",
'new': '• Golden bonus moles\n• 4×4 hard mode\n• Speed progression system',
'tags': 'whack a mole, tap game, moles, arcade, reflex, kids game, carnival, fast tap'
},
'WhiteNoise': {
'name': 'White Noise — Sleep & Focus',
'short': 'White noise, rain, ocean & fan sounds for sleep and focus.',
'full': """Fall asleep faster, focus deeper, or mask distractions with soothing sound environments!

📻 SOUNDS INCLUDED
• White noise
• Pink noise
• Brown noise
• Rain (light, heavy, thunderstorm)
• Ocean waves
• Forest (birds, crickets)
• Fan (desk fan, box fan)
• Café ambiance
• Fireplace crackling

✨ FEATURES
• Mix up to 3 sounds simultaneously
• Volume control per sound layer
• Sleep timer (off after 15/30/60 minutes)
• Looping high-quality audio
• Works fully offline
• Screen can stay on or off

Download free and sleep better tonight!""",
'new': '• Multi-sound mixing\n• Sleep timer\n• Pink and brown noise added',
'tags': 'white noise, sleep sounds, rain sounds, focus, ASMR, ambient, noise, relaxing, sleep'
},
'WoodBlock': {
'name': 'Wood Block Puzzle — Classic',
'short': 'Place wooden blocks to fill lines. Relaxing & addictive!',
'full': """The relaxing wood block puzzle game! Drag and drop wooden pieces onto the grid to complete lines and score points. No timer, no pressure — just pure focus.

🪵 HOW TO PLAY
Drag block shapes from the bottom onto the 9×9 board. Complete full lines (horizontal or vertical) to clear them and score. Game over when no pieces can be placed.

✨ FEATURES
• Classic 9×9 block puzzle
• Wide variety of block shapes
• Line clear combo scoring
• No time pressure
• High score tracking
• Warm wood aesthetic
• Works fully offline

The perfect casual game for quiet moments. Download free!""",
'new': '• Combo scoring for multi-line clears\n• New block shape variety\n• High score tracking',
'tags': 'wood block puzzle, block game, casual, relaxing, tetris-like, grid, no timer, blocks'
},
'WordConnect': {
'name': 'Word Connect — Swipe & Spell',
'short': 'Swipe letters to form words. 500+ levels of word fun!',
'full': """Swipe across letters to form hidden words and fill in the crossword-style answer grid! Word Connect is a relaxing yet satisfying word puzzle.

🔤 HOW TO PLAY
A circle of letters is shown. Swipe from one letter to adjacent letters to spell words. Find all the words that fit the answer slots to complete the level!

✨ FEATURES
• 500+ levels from easy to expert
• Bonus words for extra coins
• Hint system (reveal one letter)
• Multiple daily bonus levels
• Score and star tracking
• Works fully offline

Great for vocabulary building and relaxed brain training. Download free!""",
'new': '• Daily bonus levels\n• Bonus word rewards\n• 100 new levels added',
'tags': 'word connect, word game, swipe, letters, vocabulary, crossword, word puzzle, spelling'
},
'WordLadder': {
'name': 'Word Ladder — Transform Words',
'short': 'Change one letter at a time to transform one word to another!',
'full': """Transform one word into another by changing just one letter at a time — but every step must be a real word!

🪜 HOW TO PLAY
You're given a start word and an end word. Change one letter at a time. Each intermediate word must be valid English. Reach the end word in as few steps as possible!

✨ FEATURES
• 300+ puzzles from easy to hard
• 3-letter, 4-letter, and 5-letter word ladders
• Optimal step counter (par comparison)
• Hint: suggests one valid next word
• Works fully offline

A classic word puzzle invented by Lewis Carroll. Download free!""",
'new': '• 5-letter word ladders\n• Par comparison scoring\n• Hint system',
'tags': 'word ladder, word game, letters, vocabulary, transform, word puzzle, Lewis Carroll'
},
'WordleClone': {
'name': 'Wordle — Daily Word Guess',
'short': 'Guess the 5-letter word in 6 tries. New word every day!',
'full': """The addictive daily word game! Guess the hidden 5-letter word in 6 attempts. Green = right letter, right spot. Yellow = right letter, wrong spot.

🟩 HOW TO PLAY
Type a 5-letter word. Letters turn green (correct position), yellow (wrong position), or grey (not in the word). Use the clues to narrow down the answer in 6 guesses!

✨ FEATURES
• New word every day
• 30-day archive to play past puzzles
• Unlimited mode (new random word anytime)
• Share your result grid
• Streak and win rate statistics
• Hard mode (must use all revealed hints)
• Works fully offline

Download free and start your streak!""",
'new': '• Archive of 30 past puzzles\n• Unlimited random mode\n• Hard mode',
'tags': 'wordle, word game, daily game, 5 letter word, guess, NYT Wordle, word puzzle'
},
'WordScramble': {
'name': 'Word Scramble — Unscramble!',
'short': 'Unscramble jumbled words as fast as you can! 2000+ words.',
'full': """Unscramble the jumbled letters to form the hidden word! Word Scramble is a fast, fun vocabulary challenge with 2000+ words across multiple categories.

🔤 HOW TO PLAY
A scrambled word is shown. Tap letters in the correct order to spell the original word before time runs out!

✨ FEATURES
• 2000+ words across 10 categories
• Timed and relaxed modes
• Hint: reveals one letter in place
• Difficulty levels: short words to long words
• Streak tracking for consecutive solves
• Daily Word Scramble challenge
• Works fully offline

Download free and get unscrambling!""",
'new': '• 10 word categories\n• Daily challenge mode\n• Tap-letter interface',
'tags': 'word scramble, unscramble, word game, jumble, letters, vocabulary, anagram, spelling'
},
'WordSearch': {
'name': 'Word Search — Find the Words',
'short': 'Classic word search puzzles! 100+ themed grids.',
'full': """The classic word search puzzle on your phone! Find hidden words in the letter grid — forwards, backwards, diagonal, and everything in between.

🔍 FEATURES
• 100+ themed word search puzzles
• Themes: Animals, Sports, Countries, Food, Nature, Movies, Music, Science
• Grid sizes: 10×10, 12×12, 15×15
• Timed mode or relaxed untimed play
• Highlight found words automatically
• Hints flash one unfound word
• Daily new puzzle
• Works fully offline

Great for all ages and skill levels! Download free!""",
'new': '• Daily word search\n• 15×15 large grid\n• 20 new themes',
'tags': 'word search, find the word, word puzzle, hidden words, grid, vocabulary, classic puzzle'
},
'WorkoutLog': {
'name': 'Workout Log — Exercise Tracker',
'short': 'Log every workout, track sets, reps & weight. Stay consistent.',
'full': """Track every workout and watch yourself get stronger! Workout Log makes it simple to record exercises, sets, reps, and weights — and see your progress over time.

🏋️ FEATURES
• Log any exercise with sets, reps, and weight
• Custom exercise library
• Workout templates for quick logging
• Progress charts: weight lifted over time per exercise
• Personal best (PR) tracking
• Rest timer between sets
• All data stored locally
• Works fully offline

💪 TRACKS
• Volume per session (total weight lifted)
• Personal records per exercise
• Workout frequency
• Training history

Download free and start getting stronger!""",
'new': '• Progress charts per exercise\n• Rest timer\n• Personal record tracking',
'tags': 'workout log, exercise tracker, gym, fitness, weights, sets reps, personal record, training'
},
'WorldClock': {
'name': 'World Clock — Multiple Timezones',
'short': 'See current time in any city worldwide. 500+ cities.',
'full': """See what time it is anywhere in the world, right now! World Clock displays the current time in multiple cities simultaneously.

🕐 FEATURES
• 500+ cities worldwide
• Add any number of cities to your dashboard
• Current time, day of week, and date for each city
• Time difference from your local time (+/- hours)
• DST (Daylight Saving Time) aware
• Sort by time difference or alphabetically
• Works offline using device time

✅ GREAT FOR
• Remote teams and international calls
• Travelers and expats
• Stock and forex traders
• Anyone with contacts abroad

Download free!""",
'new': '• DST aware\n• Time difference display\n• 500+ cities',
'tags': 'world clock, time zones, multiple clocks, international time, cities, travel, time'
},
'WouldYouRather': {
'name': 'Would You Rather — Dilemmas',
'short': '500+ Would You Rather dilemmas. Impossible choices!',
'full': """Impossible choices, endless debates! Would You Rather presents you with two options that are both good (or both terrible) — you have to pick one!

🤔 FEATURES
• 500+ Would You Rather questions
• Categories: Funny, Deep, Gross, Superpower, Food, Travel
• Timer mode: 5 seconds to decide!
• 2-player comparison mode (see if you match)
• Community results: which side is more popular?
• Works fully offline

✅ GREAT FOR
• Car trips and road games
• Parties and icebreakers
• Dating conversation starters
• Team building

Download free and make some impossible choices!""",
'new': '• Community popularity results\n• 2-player comparison mode\n• Gross and Superpower categories',
'tags': 'would you rather, dilemmas, party game, choices, debate, icebreaker, fun, hypothetical'
},
'YarnSort': {
'name': 'Yarn Sort — Untangle & Organize',
'short': 'Sort tangled yarn into matching color balls. Satisfying puzzle!',
'full': """Untangle the yarn and sort each color into its own ball! Yarn Sort is a satisfying, colorful sorting puzzle that's impossible to put down.

🧶 HOW TO PLAY
Strands of different colored yarn are tangled together. Tap to pull yarn and move it from one spool to another. Sort all colors into single-color spools to complete the level!

✨ FEATURES
• 200+ levels from easy to expert
• Increasing color count and complexity
• Smooth yarn physics animations
• Undo button
• Daily yarn puzzle
• Works fully offline

Cozy, colorful, and incredibly satisfying. Download free!""",
'new': '• Daily puzzle mode\n• 80 new levels\n• Smooth yarn physics',
'tags': 'yarn sort, sorting puzzle, color sort, satisfying, casual, relaxing, yarn, knitting'
},
'ZenGarden': {
'name': 'Zen Garden — Sand & Calm',
'short': 'Rake sand patterns in a virtual zen garden. Pure relaxation.',
'full': """Find your calm in a virtual zen garden. Draw patterns in sand, place stones, and create your own peaceful miniature landscape.

🌿 FEATURES
• Rake sand with your finger — draws smooth raking lines
• Place stones, pebbles, and plants
• Reset sand to smooth with one tap
• Multiple sand colors and garden themes
• Ambient nature soundscape (birds, water, wind)
• Save your zen garden as a photo
• Works fully offline

Mindfulness without instruction. Beauty without effort. Download free!""",
'new': '• Multiple garden themes\n• Ambient sounds\n• Save garden as photo',
'tags': 'zen garden, sand, relaxing, mindfulness, calm, stress relief, meditate, peaceful, ASMR'
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

print(f'Wrote {written} store listings (batch 3: N-Z)')
