#!/usr/bin/env python3
"""
Generate all store assets for all apps:
  - store/icon_512_playstore.png
  - store/feature_graphic_1024x500.png
  - store/privacy-policy.html
"""
import os, re, math
from PIL import Image, ImageDraw, ImageFont

BASE = '/home/pgs/Documents/Gs'
SANS_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
SANS_REG  = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'

# ── emoji → symbol map (for apps whose h1 doesn't have emoji) ──────────────
APP_EMOJI = {
    'ABCLearning':'🔤','AgeCalculator':'🎂','AnagramFinder':'🔡','AnimalMerge':'🐾',
    'AnimalQuiz':'🦁','AnimalSounds':'🐘','AspectRatio':'📐','BalloonPop':'🎈',
    'BallSortPuzzle':'🎱','BasicMathKids':'➕','BibleQuiz':'📖','BillSplit':'🧾',
    'Binairo':'0️⃣','BlockPuzzle':'🧱','BloodPressureLog':'💓','BloodSugarLog':'🩸',
    'BMICalculator':'⚖️','BoggleGame':'🔠','BPMTapper':'🥁','BreathingExercise':'🌬️',
    'BrickBreaker':'🧱','BubbleShooter':'🫧','BubbleWrap':'💢','BudgetPlanner':'💰',
    'CapitalCities':'🏙️','CharadesApp':'🎭','ChessClock':'♟️','ChoreChart':'🧹',
    'CocktailGuide':'🍹','CoffeeGuide':'☕','CoinFlip':'🪙','ColorBlockJam':'🟥',
    'ColorFill':'🎨','CompoundInterest':'📈','Connections':'🔗','CookingTimer':'🍳',
    'CountdownTimer':'⏳','CountingApp':'🔢','Cryptogram':'🔐','CurrencyConverter':'💱',
    'DartsScorer':'🎯','DecisionMaker':'🎲','DiceRoller':'🎲','DinosaurApp':'🦕',
    'DontTapWhite':'⬛','DotArt':'🎨','DrumMachine':'🥁','EggTimer':'🥚',
    'EmojiQuiz':'😀','EmojiSort':'😊','EmotionFlash':'💭','ExpenseTracker':'💳',
    'EyeRest':'👁️','FastingTimer':'⏱️','FindDifference':'🔍','Fireworks':'🎆',
    'FishingLog':'🎣','FlagQuiz':'🏳️','FlappyBird':'🐦','FlashcardMaker':'🗒️',
    'FlashlightSOS':'🔦','FoodQuiz':'🍕','FootballQuiz':'⚽','FruitMerge':'🍎',
    'FruitSort':'🍓','GPACalculator':'📊','GeneralQuiz':'❓','GeographyQuiz':'🌍',
    'GhostWord':'👻','GolfScorecard':'⛳','GroceryList':'🛒','GuitarChords':'🎸',
    'HabitTracker':'✅','Hangman':'🪢','HarryPotterFan':'⚡','HeadsUpGame':'🙆',
    'HiddenObject':'🔍','HistoryQuiz':'📜','IceBreaker':'🧊','InfiniteJumper':'🦘',
    'JigsawPuzzle':'🧩','Kaleidoscope':'🔮','KidsColoring':'🖍️','KidsDrum':'🥁',
    'KidsPiano':'🎹','KnotPuzzle':'🪢','LightsOut':'💡','LoanCalculator':'🏦',
    'LogoQuiz':'🏷️','MahjongSolitaire':'🀄','MandalaColor':'🌸','Mastermind':'🧠',
    'MedicationReminder':'💊','MeetingTimer':'⏱️','MemoryCard':'🃏','MentalMathQuiz':'🔢',
    'Metronome':'🎵','Minesweeper':'💣','MoodTracker':'😊','MorseCode':'📡',
    'MovieTrivia':'🎬','MultiplicationGame':'✖️','MusicTheory':'🎼','NeverHaveIEver':'🙋',
    'Nonogram':'🖼️','NumberBase':'🔢','NumberLink':'🔢','NumberMemory':'🧠',
    'NumberMerge':'🔢','NumberTap':'🔢','PackingChecklist':'✈️','PackingList':'🧳',
    'PasswordGen':'🔑','PatternSequence':'🔷','PercentageCalc':'%','PeriodTracker':'📅',
    'PhoneticApp':'📻','Phrasebook':'📗','PianoKeyboard':'🎹','PinPull':'📌',
    'PipeConnect':'🔧','PixelArt':'🎨','PlantWater':'🌱','PomodoroTimer':'🍅',
    'PostureReminder':'🧘','PushUpCounter':'💪','Puzzle2048':'2️⃣','QRCodeGen':'📷',
    'QuitSmoking':'🚭','RandomName':'🎲','RandomNumber':'🎲','RandomRecipe':'🍽️',
    'ReactionTime':'⚡','RecipeConverter':'🍴','RomanNumeralConverter':'🔢',
    'SalaryCalculator':'💵','SatisfyingSlime':'🫧','SavingsGoal':'🐷',
    'ScienceQuiz':'🔬','ScientificCalc':'🧮','ScoreTracker':'📊','ScrewPuzzle':'🔩',
    'ShapesColors':'🟦','SimonSays':'🟩','SleepTracker':'😴','SlidingTiles':'🧩',
    'SnakeGame':'🐍','SobrietyCounter':'🌟','Sokoban':'📦','SolarSystem':'🌍',
    'Solitaire':'🃏','SoundBoard':'🔊','SpellingBee':'🐝','SpinBottle':'🍾',
    'SportsQuiz':'🏆','StepCounter':'👟','StopwatchTimer':'⏱️','StroopTest':'🧠',
    'Sudoku':'🔢','Sumplete':'➕','TallyCounter':'🔢','TapColor':'🎨',
    'TetrisGame':'🟦','TextCase':'🔡','ThisOrThat':'🤔','TimesTable':'✖️',
    'TimezoneConverter':'🌐','TipCalculator':'💰','TripleMatch':'🃏','TrueOrFalse':'✅',
    'TruthOrDare':'🎯','TwentyQuestions':'❓','TwoTruthsOneLie':'🤫',
    'UkuleleChords':'🎸','UnblockPuzzle':'🔓','UnitConverter':'📏',
    'VATCalculator':'💶','WaterReminder':'💧','WaterSort':'💧','WhackaMole':'🔨',
    'WhiteNoise':'📻','WoodBlock':'🪵','WordConnect':'🔤','WordLadder':'🪜',
    'WordleClone':'🟩','WordScramble':'🔤','WordSearch':'🔍','WorkoutLog':'🏋️',
    'WorldClock':'🕐','WouldYouRather':'🤔','YarnSort':'🧶','ZenGarden':'🌿',
}

# ── color helpers ─────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    return tuple(int(a + (b-a)*t) for a, b in zip(c1, c2))

def gradient_bg(img, c1, c2, diagonal=True):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if diagonal:
                t = (x/w * 0.5 + y/h * 0.5)
            else:
                t = y/h
            color = lerp_color(c1, c2, t)
            draw.point((x,y), fill=color)

def rounded_mask(size, radius):
    mask = Image.new('L', size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return mask

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    line = ''
    for w in words:
        test = (line + ' ' + w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_text_centered(draw, text, font, cx, cy, color=(255,255,255), shadow=True):
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = cx - tw//2
    y = cy - th//2
    if shadow:
        draw.text((x+2, y+2), text, font=font, fill=(0,0,0,80))
    draw.text((x, y), text, font=font, fill=color)

# ── icon 512x512 ──────────────────────────────────────────────────────────
def make_icon(app_name, accent, accent2, emoji_str, title):
    size = 512
    img = Image.new('RGBA', (size, size), (0,0,0,0))

    try:
        c1 = hex_to_rgb(accent)
        c2 = hex_to_rgb(accent2) if accent2 != accent else tuple(max(0,v-40) for v in hex_to_rgb(accent))
    except:
        c1 = (76, 175, 80)
        c2 = (27, 94, 32)

    # Background gradient
    bg = Image.new('RGBA', (size, size))
    gradient_bg(bg, c1, c2)

    # Rounded corners mask
    mask = rounded_mask((size, size), 80)
    img.paste(bg, mask=mask)

    draw = ImageDraw.Draw(img)

    # Draw app initial letter(s) as large text
    initials = ''.join(w[0].upper() for w in title.split()[:2])
    if len(initials) == 1:
        initials = title[:2].upper()

    try:
        font_large = ImageFont.truetype(SANS_BOLD, 220)
        font_small = ImageFont.truetype(SANS_BOLD, 44)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # White circle background for letter
    draw.ellipse([106, 80, 406, 380], fill=(255,255,255,40))

    # Large initials
    draw_text_centered(draw, initials, font_large, size//2, 215, (255,255,255,230))

    # App name at bottom
    words = title.split()
    if len(words) <= 2:
        bottom_text = title.upper()
    else:
        # Two lines
        mid = len(words)//2
        bottom_text = ' '.join(words[:mid]).upper()

    draw_text_centered(draw, bottom_text, font_small, size//2, 420, (255,255,255,230))
    if len(words) > 2:
        line2 = ' '.join(words[len(words)//2:]).upper()
        draw_text_centered(draw, line2, font_small, size//2, 468, (255,255,255,230))

    return img

# ── feature graphic 1024x500 ─────────────────────────────────────────────
def make_feature(app_name, accent, accent2, title):
    W, H = 1024, 500
    img = Image.new('RGB', (W, H))

    try:
        c1 = hex_to_rgb(accent)
        c2 = hex_to_rgb(accent2) if accent2 != accent else tuple(max(0,v-50) for v in hex_to_rgb(accent))
    except:
        c1 = (76, 175, 80)
        c2 = (27, 94, 32)

    gradient_bg(img, c1, c2)
    draw = ImageDraw.Draw(img)

    # Decorative circles
    draw.ellipse([-100, -100, 300, 300], fill=(*lerp_color(c1, (255,255,255), 0.15), 255))
    draw.ellipse([750, 200, 1150, 600], fill=(*lerp_color(c2, (0,0,0), 0.1), 255))

    try:
        font_title = ImageFont.truetype(SANS_BOLD, 80)
        font_sub   = ImageFont.truetype(SANS_REG, 36)
        font_brand = ImageFont.truetype(SANS_BOLD, 28)
    except:
        font_title = ImageFont.load_default()
        font_sub   = font_title
        font_brand = font_title

    # App title (may need wrapping)
    words = title.split()
    if len(words) <= 2:
        lines = [title]
    elif len(words) <= 4:
        mid = (len(words)+1)//2
        lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
    else:
        lines = [' '.join(words[:3]), ' '.join(words[3:])]

    title_y = 160 if len(lines) == 1 else 130
    line_h = 95
    for i, line in enumerate(lines):
        draw_text_centered(draw, line.upper(), font_title, W//2, title_y + i*line_h)

    # Tagline
    taglines = {
        'ABCLearning':'Learn letters the fun way',
        'AgeCalculator':'Know your exact age instantly',
        'default':'Free · Fun · No Internet Required'
    }
    tag = taglines.get(app_name, taglines['default'])
    draw_text_centered(draw, tag, font_sub, W//2, title_y + len(lines)*line_h + 20, (255,255,255,180))

    # Brand
    draw_text_centered(draw, 'Pegasus Games', font_brand, W//2, H - 36, (255,255,255,150))

    return img

# ── privacy policy HTML ───────────────────────────────────────────────────
PRIVACY_TMPL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Privacy Policy — {title}</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.7; }}
  h1 {{ color: #1a1a2e; }}
  h2 {{ color: #333; margin-top: 30px; }}
  p {{ margin: 12px 0; }}
</style>
</head>
<body>

<h1>Privacy Policy</h1>
<p><strong>App:</strong> {title}<br>
<strong>Developer:</strong> Pegasus Games<br>
<strong>Last updated:</strong> April 2026</p>

<h2>1. Information We Collect</h2>
<p>{title} does not directly collect any personal information from users. The app stores data (settings, progress, preferences) locally on your device. This data never leaves your device and is not accessible to us.</p>

<h2>2. Third-Party Services</h2>
<p>The app uses the following third-party services that may collect data according to their own privacy policies:</p>
<ul>
  <li><strong>AppLovin MAX</strong> — used to display advertisements. AppLovin and its mediation partners (including Google AdMob) may collect device identifiers and usage data to serve ads. See AppLovin's privacy policy at <a href="https://www.applovin.com/privacy/">https://www.applovin.com/privacy/</a>.</li>
  <li><strong>Google AdMob</strong> — used as a mediation adapter within AppLovin MAX. Subject to Google's privacy policy at <a href="https://policies.google.com/privacy">https://policies.google.com/privacy</a>.</li>
  <li><strong>Google Play Billing</strong> — used to process in-app purchases. Purchase data is handled by Google Play. We receive only confirmation of a successful purchase; we do not receive payment details.</li>
  <li><strong>Firebase Analytics</strong> — used to collect anonymous app usage analytics. Subject to Google's privacy policy.</li>
</ul>

<h2>3. Advertising</h2>
<p>The app contains advertisements. These ads may be personalized based on your interests. You can opt out of personalized advertising through your device settings (Google → Ads → Opt out of Ads Personalization).</p>

<h2>4. In-App Purchases</h2>
<p>The app offers optional in-app purchases (e.g., removing ads). All transactions are processed securely through Google Play. We do not store or have access to your payment information.</p>

<h2>5. Children\'s Privacy</h2>
<p>This app is not directed at children under the age of 13. We do not knowingly collect personal information from children. If you are a parent or guardian and believe your child has provided personal information, please contact us and we will take steps to remove it.</p>

<h2>6. Data Security</h2>
<p>All app data is stored locally on your device. We do not transmit your personal data to any server. The app requires internet access only to load advertisements and process purchases.</p>

<h2>7. Changes to This Policy</h2>
<p>We may update this privacy policy from time to time. Any changes will be posted on this page with an updated date. Continued use of the app after changes constitutes acceptance of the new policy.</p>

<h2>8. Contact</h2>
<p>If you have any questions about this privacy policy, contact us at:<br>
<strong>pegasusgames.dev@gmail.com</strong></p>

</body>
</html>
'''

# ── main ──────────────────────────────────────────────────────────────────
def get_app_data(app):
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    if not os.path.exists(html_path):
        return None
    with open(html_path) as f:
        content = f.read()
    title_m = re.search(r'<title>(.*?)</title>', content)
    title = title_m.group(1) if title_m else app
    accent_m = re.search(r'--accent\s*:\s*(#[0-9a-fA-F]{3,8})', content)
    accent = accent_m.group(1) if accent_m else '#4CAF50'
    accent2_m = re.search(r'--accent2\s*:\s*(#[0-9a-fA-F]{3,8})', content)
    accent2 = accent2_m.group(1) if accent2_m else accent
    return {'title': title, 'accent': accent, 'accent2': accent2}

apps = sorted([d for d in os.listdir(BASE)
               if os.path.isdir(f'{BASE}/{d}')
               and os.path.isdir(f'{BASE}/{d}/store')
               and not d.startswith('_')])

skip = {'BallSortPuzzle','WaterSort','Nonogram','PipeConnect','Puzzle2048','UnblockPuzzle'}

done = 0
errors = []
for app in apps:
    store_dir = f'{BASE}/{app}/store'
    icon_path = f'{store_dir}/icon_512_playstore.png'
    feat_path = f'{store_dir}/feature_graphic_1024x500.png'
    priv_path = f'{store_dir}/privacy-policy.html'

    data = get_app_data(app)
    if not data:
        errors.append(f'{app}: no game.html')
        continue

    title = data['title']
    accent = data['accent']
    accent2 = data['accent2']
    emoji = APP_EMOJI.get(app, '🎮')

    # Fix wrong titles (copy-paste bugs)
    if app == 'AnimalMerge' and title == 'Dice Roller':
        title = 'Animal Merge'
    elif app == 'BlockPuzzle' and title == 'Dice Roller':
        title = 'Block Puzzle'

    # Generate icon
    if not os.path.exists(icon_path) or app not in skip:
        try:
            icon = make_icon(app, accent, accent2, emoji, title)
            icon.save(icon_path)
        except Exception as e:
            errors.append(f'{app} icon: {e}')

    # Generate feature graphic
    if not os.path.exists(feat_path) or app not in skip:
        try:
            feat = make_feature(app, accent, accent2, title)
            feat.save(feat_path)
        except Exception as e:
            errors.append(f'{app} feature: {e}')

    # Generate privacy policy
    if not os.path.exists(priv_path):
        try:
            with open(priv_path, 'w') as f:
                f.write(PRIVACY_TMPL.format(title=title))
        except Exception as e:
            errors.append(f'{app} privacy: {e}')

    done += 1
    if done % 20 == 0:
        print(f'  {done}/{len(apps)} done...')

print(f'Done: {done} apps')
if errors:
    print('Errors:')
    for e in errors:
        print(' ', e)
