#!/usr/bin/env python3
"""
bulk_assign_archetypes.py — one-shot bulk assignment of design archetypes
(layout, mascot, voice, texture) and unique color palettes to every app
folder in the portfolio (except WaterSortPuzzle, which is grandfathered).

Writes:
  - scripts/app_themes.py THEMES dict (replaced)
  - <App>/metadata/app_identity.md  (one per app)

Run from repo root:
  python3 scripts/bulk_assign_archetypes.py
"""

import colorsys
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "_screenshot_tools", "__pycache__",
        "docs", "scripts", ".claude", ".git", "WaterSortPuzzle"}


# ---- App categorization --------------------------------------------------

KIDS = {"ABCLearning", "BasicMathKids", "CountingApp", "KidsColoring",
        "KidsDrum", "KidsPiano", "ShapesColors", "AnimalSounds",
        "DinosaurApp", "PhoneticApp", "TimesTable", "MultiplicationGame"}

TRIVIA = {"AnimalQuiz", "BibleQuiz", "CapitalCities", "EmojiQuiz", "FlagQuiz",
          "FoodQuiz", "FootballQuiz", "GeneralQuiz", "GeographyQuiz",
          "HistoryQuiz", "LogoQuiz", "MentalMathQuiz", "MovieTrivia",
          "MusicTheory", "ScienceQuiz", "SolarSystem", "SportsQuiz",
          "TrueOrFalse", "HarryPotterFan"}

TRACKER = {"BloodPressureLog", "BloodSugarLog", "BudgetPlanner",
           "ChoreChart", "ExpenseTracker", "FastingTimer", "FishingLog",
           "GolfScorecard", "GroceryList", "HabitTracker",
           "MedicationReminder", "MoodTracker", "PackingChecklist",
           "PackingList", "PeriodTracker", "PlantWater", "PomodoroTimer",
           "PushUpCounter", "QuitSmoking", "SavingsGoal", "ScoreTracker",
           "SleepTracker", "SobrietyCounter", "StepCounter", "TallyCounter",
           "WaterReminder", "WorkoutLog", "PostureReminder", "DartsScorer"}

TOOL = {"AgeCalculator", "AspectRatio", "BillSplit", "BMICalculator",
        "CompoundInterest", "CurrencyConverter", "DecisionMaker",
        "GPACalculator", "LoanCalculator", "PasswordGen", "PercentageCalc",
        "QRCodeGen", "RandomName", "RandomNumber", "RandomRecipe",
        "RecipeConverter", "RomanNumeralConverter", "SalaryCalculator",
        "ScientificCalc", "StopwatchTimer", "TextCase", "TimezoneConverter",
        "TipCalculator", "UnitConverter", "VATCalculator", "WorldClock",
        "CoinFlip", "NumberBase", "FlashlightSOS", "ChessClock"}

WELLNESS = {"BreathingExercise", "EyeRest", "WhiteNoise", "ZenGarden",
            "SatisfyingSlime"}

CREATIVE = {"DotArt", "PixelArt", "MandalaColor", "Kaleidoscope",
            "FlashcardMaker", "Fireworks"}

SOCIAL_PARTY = {"CharadesApp", "HeadsUpGame", "IceBreaker", "NeverHaveIEver",
                "SpinBottle", "ThisOrThat", "TruthOrDare", "TwentyQuestions",
                "TwoTruthsOneLie", "WouldYouRather"}

WORD = {"Connections", "Cryptogram", "Hangman", "SpellingBee", "WordConnect",
        "WordLadder", "WordleClone", "WordScramble", "WordSearch"}

ARCADE = {"BalloonPop", "BrickBreaker", "BubbleShooter", "FlappyBird",
          "NumberTap", "ReactionTime", "SnakeGame", "StroopTest", "TapColor",
          "TetrisGame", "WhackaMole", "ColorFill", "Minesweeper"}

MUSIC = {"DrumMachine", "GuitarChords", "Metronome", "MorseCode",
         "PianoKeyboard", "SoundBoard"}

LIFESTYLE = {"CocktailGuide", "CoffeeGuide", "Phrasebook"}


def category(app):
    if app in KIDS:        return "kids"
    if app in TRIVIA:      return "trivia"
    if app in TRACKER:     return "tracker"
    if app in TOOL:        return "tool"
    if app in WELLNESS:    return "wellness"
    if app in CREATIVE:    return "creative"
    if app in SOCIAL_PARTY:return "party"
    if app in WORD:        return "word"
    if app in ARCADE:      return "arcade"
    if app in MUSIC:       return "music"
    if app in LIFESTYLE:   return "lifestyle"
    return "puzzle"


# ---- Archetype profiles (Layout, Mascot, Voice, Texture) -----------------
# Each profile list rotates within its category by app-index. None match
# the template signature (A/M0/V1/T1).

PROFILES = {
    "kids": [
        ("E", "M3", "V7", "T7"),
        ("E", "M2", "V7", "T7"),
        ("C", "M3", "V7", "T7"),
        ("B", "M2", "V7", "T5"),
        ("E", "M3", "V7", "T5"),
    ],
    "trivia": [
        ("D", "M0", "V7", "T3"),
        ("G", "M0", "V8", "T3"),
        ("D", "M1", "V3", "T3"),
        ("G", "M0", "V2", "T8"),
        ("D", "M2", "V7", "T5"),
    ],
    "tracker": [
        ("I", "M0", "V5", "T2"),
        ("D", "M4", "V5", "T2"),
        ("I", "M0", "V8", "T8"),
        ("I", "M4", "V2", "T3"),
        ("D", "M0", "V5", "T3"),
    ],
    "tool": [
        ("I", "M0", "V8", "T8"),
        ("I", "M0", "V8", "T2"),
        ("I", "M0", "V8", "T3"),
        ("I", "M0", "V5", "T2"),
    ],
    "wellness": [
        ("I", "M4", "V5", "T2"),
        ("H", "M4", "V5", "T3"),
        ("C", "M4", "V5", "T7"),
        ("I", "M4", "V5", "T5"),
    ],
    "creative": [
        ("H", "M4", "V5", "T5"),
        ("H", "M2", "V3", "T5"),
        ("I", "M4", "V8", "T5"),
        ("H", "M0", "V5", "T7"),
    ],
    "party": [
        ("D", "M2", "V3", "T5"),
        ("A", "M2", "V3", "T6"),
        ("D", "M1", "V6", "T5"),
        ("C", "M2", "V3", "T7"),
    ],
    "word": [
        ("G", "M0", "V8", "T3"),
        ("D", "M0", "V8", "T8"),
        ("G", "M0", "V3", "T3"),
        ("F", "M0", "V8", "T3"),
    ],
    "arcade": [
        ("F", "M1", "V6", "T6"),
        ("A", "M1", "V6", "T6"),
        ("F", "M1", "V3", "T1"),
        ("F", "M0", "V6", "T8"),
        ("A", "M2", "V6", "T6"),
    ],
    "music": [
        ("I", "M0", "V8", "T6"),
        ("I", "M0", "V8", "T4"),
        ("A", "M1", "V3", "T6"),
        ("I", "M0", "V5", "T2"),
    ],
    "lifestyle": [
        ("D", "M0", "V3", "T3"),
        ("D", "M2", "V3", "T5"),
    ],
    "puzzle": [
        ("B", "M1", "V3", "T4"),
        ("F", "M0", "V4", "T4"),
        ("G", "M0", "V8", "T3"),
        ("C", "M2", "V3", "T7"),
        ("H", "M0", "V5", "T5"),
        ("B", "M2", "V3", "T4"),
        ("F", "M1", "V6", "T8"),
        ("D", "M0", "V8", "T2"),
        ("B", "M0", "V4", "T8"),
        ("F", "M2", "V3", "T5"),
        ("G", "M1", "V3", "T3"),
        ("H", "M4", "V5", "T2"),
        ("B", "M1", "V6", "T6"),
        ("C", "M3", "V3", "T7"),
        ("D", "M1", "V3", "T5"),
        ("F", "M0", "V8", "T6"),
    ],
}


# ---- Color palette generation --------------------------------------------
# Each app gets a unique hue (rotated through HSL), with a brightness profile
# matching its category. This guarantees distinct bg_top_left across all
# apps deterministically.

# Brightness profile per category. Tuple of (sat, light) for top_left.
BRIGHTNESS = {
    "kids":      ("bright", (0.78, 0.62)),
    "tool":      ("light",  (0.30, 0.90)),
    "tracker":   ("light",  (0.32, 0.88)),
    "wellness":  ("light",  (0.28, 0.92)),
    "trivia":    ("medium", (0.55, 0.45)),
    "word":      ("light",  (0.20, 0.90)),
    "lifestyle": ("medium", (0.50, 0.40)),
    "creative":  ("medium", (0.60, 0.45)),
    "party":     ("medium", (0.65, 0.50)),
    "arcade":    ("dark",   (0.75, 0.20)),
    "music":     ("dark",   (0.60, 0.22)),
    "puzzle":    ("dark",   (0.70, 0.22)),
}


def hsl(h, s, l):
    """Convert HSL (h in degrees) to 0-255 RGB tuple."""
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def palette_for(idx, total, category):
    """Generate a palette dict for an app at sorted index `idx` of `total`.
    Hue is unique per index. Brightness tuned to category."""
    base_h = (idx * 360.0 / total) % 360
    profile, (sat, lit) = BRIGHTNESS[category]
    h2 = (base_h + 18) % 360
    h3 = (base_h - 12) % 360
    if profile == "dark":
        bg_tl = hsl(base_h, sat, lit)
        bg_tr = hsl(h2,     sat, min(0.40, lit + 0.10))
        bg_bo = hsl(h3,     sat, max(0.06, lit - 0.10))
        text_primary = (255, 255, 255)
        text_accent  = hsl((base_h + 60) % 360, 0.85, 0.65)
        text_subtle  = hsl(base_h, 0.35, 0.85)
        footer_tint  = hsl((base_h + 60) % 360, 0.75, 0.70)
    elif profile == "light":
        bg_tl = hsl(base_h, sat, lit)
        bg_tr = hsl(h2,     sat * 0.85, max(0.78, lit - 0.04))
        bg_bo = hsl(h3,     sat * 1.10, max(0.65, lit - 0.18))
        text_primary = hsl(base_h, 0.55, 0.18)
        text_accent  = hsl((base_h + 30) % 360, 0.75, 0.42)
        text_subtle  = hsl(base_h, 0.30, 0.40)
        footer_tint  = hsl((base_h + 30) % 360, 0.70, 0.45)
    elif profile == "bright":
        bg_tl = hsl(base_h, sat, lit)
        bg_tr = hsl(h2,     sat, min(0.75, lit + 0.10))
        bg_bo = hsl(h3,     sat, max(0.40, lit - 0.18))
        text_primary = hsl(base_h, 0.60, 0.18)
        text_accent  = hsl((base_h + 180) % 360, 0.80, 0.45)
        text_subtle  = hsl(base_h, 0.35, 0.30)
        footer_tint  = hsl((base_h + 180) % 360, 0.70, 0.50)
    else:  # medium
        bg_tl = hsl(base_h, sat, lit)
        bg_tr = hsl(h2,     sat, min(0.60, lit + 0.08))
        bg_bo = hsl(h3,     sat, max(0.20, lit - 0.18))
        text_primary = (255, 255, 255)
        text_accent  = hsl((base_h + 60) % 360, 0.85, 0.70)
        text_subtle  = hsl(base_h, 0.35, 0.85)
        footer_tint  = hsl((base_h + 60) % 360, 0.75, 0.72)
    return dict(
        bg_top_left=bg_tl, bg_top_right=bg_tr, bg_bottom=bg_bo,
        text_primary=text_primary, text_accent=text_accent,
        text_subtle=text_subtle, footer_tint=footer_tint,
    )


# ---- Mood string ---------------------------------------------------------

MOOD = {
    "kids":      "kids-bright",
    "tool":      "tool-clean",
    "tracker":   "tracker-soft",
    "wellness":  "wellness-calm",
    "trivia":    "trivia-knowledge",
    "word":      "word-paper",
    "lifestyle": "lifestyle-warm",
    "creative":  "creative-studio",
    "party":     "party-playful",
    "arcade":    "arcade-vivid",
    "music":     "music-stage",
    "puzzle":    "puzzle-deep",
}


# ---- Identity description -----------------------------------------------

LAYOUT_DESC = {
    "A": "hero Play button stack",
    "B": "map / journey screen",
    "C": "hub world / cozy room",
    "D": "vertical card feed",
    "E": "animated character speaks",
    "F": "direct-to-game minimal",
    "G": "calendar / streak grid",
    "H": "workshop / inventory",
    "I": "toolbox / direct tool",
}

MASCOT_DESC = {
    "M0": "no mascot — game elements carry the personality",
    "M1": "anthropomorphized game elements (eyes, smiles, reactions)",
    "M2": "static mascot with 2-3 expressions",
    "M3": "animated companion with idle + reactions",
    "M4": "spirit-of-the-app abstract motif (particles, flow)",
}

VOICE_DESC = {
    "V1": "neutral functional",
    "V2": "encouraging coach",
    "V3": "playful narrator",
    "V4": "snarky / dry",
    "V5": "calm / zen",
    "V6": "enthusiastic arcade",
    "V7": "educational warm",
    "V8": "direct minimal",
}

TEXTURE_DESC = {
    "T1": "flat clean",
    "T2": "soft glassmorphism",
    "T3": "subtle paper texture",
    "T4": "wood / material",
    "T5": "hand-drawn / sketch",
    "T6": "neon / arcade",
    "T7": "storybook / illustrated",
    "T8": "brutalist / minimal",
}

CATEGORY_FEEL = {
    "kids":      "warm and inviting; reads as a children's app at a glance",
    "tool":      "fast, no-friction utility — opens straight to the tool",
    "tracker":   "calm and supportive; encourages a daily habit without nagging",
    "wellness":  "quiet and contemplative; the app helps the user slow down",
    "trivia":    "curious and conversational; rewards thoughtful answers",
    "word":      "library / morning newspaper energy; serious but playful",
    "lifestyle": "magazine browse; rich visuals, taste-driven",
    "creative":  "art studio; tools are visible, output is the reward",
    "party":     "lively and casual; built for groups",
    "arcade":    "punchy, fast, celebratory; juice on every action",
    "music":     "performance instrument; tactile and responsive",
    "puzzle":    "thoughtful and tactile; each app's mechanic is the star",
}


def identity_md(app, cat, layout, mascot, voice, texture):
    feel = CATEGORY_FEEL[cat]
    return f"""# {app} Identity

- **Category**: {cat}
- **Layout archetype**: {layout} ({LAYOUT_DESC[layout]})
- **Mascot pattern**: {mascot} ({MASCOT_DESC[mascot]})
- **Voice**: {voice} ({VOICE_DESC[voice]})
- **Texture**: {texture} ({TEXTURE_DESC[texture]})
- **Mood string**: {MOOD[cat]}

The app should feel like: {feel}.

## Anti-pattern audit (APP_ARCHETYPES.md §5)

This file was auto-generated during the 2026-04-30 portfolio archetype
assignment pass. The four archetypes above were chosen so the app does
NOT default to the template signature (A/M0/V1/T1).

When the app's `game.html` is next touched (or built fresh), audit the
in-app design against the §5 anti-patterns:

- [ ] Center-aligned everything → use offset weight
- [ ] Same SVG icon set as other apps → vary icon family per app
- [ ] All-caps headlines on every screen → mixed case for body
- [ ] Generic templated currency icon → make it match the app theme
- [ ] Identical button shapes / sizes / spacings → vary
- [ ] Symmetric vertical column layout → break with side panels / FAB
- [ ] Generic "Level Complete!" celebration → app-specific phrasing
- [ ] Same loading / transition patterns → vary
- [ ] Identical settings screen → reorder, rename, add app-specific options

If 3+ of the above are hit, redesign before the next ship.

## Phase 8 self-check

Before declaring this app release-ready, all four of:

1. Side-by-side test (vs other shipped apps, do they look like different products?)
2. Voice-specificity test (does the menu copy reflect this app's voice archetype?)
3. Identity-element test (a single recognizable visual element)
4. Anonymous-screenshot test (could a user identify this app without title/name?)

must pass. See APP_ARCHETYPES.md §8.
"""


# ---- THEMES dict generation ---------------------------------------------

def list_apps():
    apps = []
    for n in sorted(os.listdir(REPO)):
        if n.startswith(".") or n in SKIP:
            continue
        p = REPO / n
        if not p.is_dir():
            continue
        if not (p / "android").is_dir():
            continue
        apps.append(n)
    return apps


def color_tuple(t):
    return f"({t[0]}, {t[1]}, {t[2]})"


def theme_entry(app, cat, layout, mascot, voice, texture, palette):
    p = palette
    return f"""    "{app}": {{
        "bg_top_left":  {color_tuple(p['bg_top_left'])},
        "bg_top_right": {color_tuple(p['bg_top_right'])},
        "bg_bottom":    {color_tuple(p['bg_bottom'])},
        "text_primary": {color_tuple(p['text_primary'])},
        "text_accent":  {color_tuple(p['text_accent'])},
        "text_subtle":  {color_tuple(p['text_subtle'])},
        "footer_tint":  {color_tuple(p['footer_tint'])},
        "mood": "{MOOD[cat]}",
        "layout_archetype": "{layout}",
        "mascot_pattern":   "{mascot}",
        "voice":            "{voice}",
        "texture":          "{texture}",
    }},
"""


WATERSORT_ENTRY = '''    # ===== GRANDFATHERED (already shipped before archetype system) =====
    "WaterSortPuzzle": {
        "bg_top_left":  (14, 49, 82),
        "bg_top_right": (12, 70, 105),
        "bg_bottom":    (6, 28, 50),
        "text_primary":  (255, 255, 255),
        "text_accent":   (105, 240, 174),
        "text_subtle":   (200, 220, 240),
        "footer_tint":   (79, 195, 247),
        "mood": "ocean-depth",
        "layout_archetype": "A",
        "mascot_pattern":   "M0",
        "voice":            "V1",
        "texture":          "T1",
        "grandfathered":    True,
    },

    # WaterSort key kept for backwards-compatibility with old scripts referring
    # to the short name (the actual folder is WaterSortPuzzle).
    "WaterSort": {
        "bg_top_left":  (14, 49, 82),
        "bg_top_right": (12, 70, 105),
        "bg_bottom":    (6, 28, 50),
        "text_primary":  (255, 255, 255),
        "text_accent":   (105, 240, 174),
        "text_subtle":   (200, 220, 240),
        "footer_tint":   (79, 195, 247),
        "mood": "ocean-depth",
        "layout_archetype": "A",
        "mascot_pattern":   "M0",
        "voice":            "V1",
        "texture":          "T1",
        "grandfathered":    True,
    },

'''


def main():
    """Additive run: keep existing THEMES entries (and their hand-tuned
    palettes/archetypes) intact. Only ADD entries / fields for apps that
    don't already have them. Does not write app_identity.md if a real
    one already exists at that path."""
    sys.path.insert(0, str(REPO / "scripts"))
    from app_themes import THEMES as EXISTING_THEMES  # noqa

    apps = list_apps()
    n = len(apps)
    print(f"Found {n} apps to process (excluding WaterSortPuzzle).")

    cat_counters = {k: 0 for k in PROFILES.keys()}
    new_entries = []
    updated_apps = []
    skipped_apps = []
    by_cat = {}

    for idx, app in enumerate(apps):
        cat = category(app)
        profiles = PROFILES[cat]
        layout, mascot, voice, texture = profiles[cat_counters[cat] % len(profiles)]
        cat_counters[cat] += 1

        if app in EXISTING_THEMES:
            existing = EXISTING_THEMES[app]
            # Already complete? skip.
            if all(existing.get(f) for f in
                   ("layout_archetype", "mascot_pattern", "voice", "texture")):
                skipped_apps.append(app)
                by_cat.setdefault(cat, []).append(app)
                # Still write app_identity.md if missing
                identity_path = REPO / app / "metadata" / "app_identity.md"
                if not identity_path.exists():
                    identity_path.parent.mkdir(parents=True, exist_ok=True)
                    identity_path.write_text(identity_md(
                        app, cat,
                        existing["layout_archetype"], existing["mascot_pattern"],
                        existing["voice"], existing["texture"]))
                continue
            # Has palette but missing archetype fields → patch in-place
            updated_apps.append(app)
        else:
            # Brand new: full entry
            palette = palette_for(idx, n, cat)
            new_entries.append(theme_entry(app, cat, layout, mascot, voice, texture, palette))

        meta_dir = REPO / app / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        identity_path = meta_dir / "app_identity.md"
        if not identity_path.exists():
            identity_path.write_text(identity_md(app, cat, layout, mascot, voice, texture))
        by_cat.setdefault(cat, []).append(app)

    # ---- Patch existing entries in app_themes.py: add missing archetype fields
    themes_py = REPO / "scripts" / "app_themes.py"
    src = themes_py.read_text()

    for app in updated_apps:
        cat = category(app)
        profiles = PROFILES[cat]
        # Reset counter logic — find the same archetype this app would have
        # received in the rotation (use a hash of app name as deterministic idx).
        idx_in_cat = sum(ord(c) for c in app) % len(profiles)
        layout, mascot, voice, texture = profiles[idx_in_cat]

        # Find the entry block: from `"<app>": {` to its closing `},`
        marker = f'"{app}": {{'
        start = src.find(marker)
        if start < 0:
            continue
        end = src.find("\n    },", start)
        if end < 0:
            continue
        block = src[start:end]
        if '"layout_archetype"' in block:
            # already has fields — don't double-add
            continue
        # Insert archetype lines before closing brace (preserve indent of 8 spaces)
        addition = (
            f'\n        "layout_archetype": "{layout}",'
            f'\n        "mascot_pattern":   "{mascot}",'
            f'\n        "voice":            "{voice}",'
            f'\n        "texture":          "{texture}",'
        )
        # Trim trailing comma issues — find last non-empty line of block
        # The block already ends right before "\n    }," so we append before that.
        src = src[:end] + addition + src[end:]

    # ---- Append new entries before final closing brace of THEMES dict
    if new_entries:
        # Find closing of THEMES dict
        themes_start = src.find("THEMES = {")
        # Find the matching closing }: scan for "\n}\n" after themes_start
        close_idx = src.find("\n}\n", themes_start)
        if close_idx < 0:
            print("ERROR: could not find closing of THEMES dict", file=sys.stderr)
            sys.exit(1)
        # Insert new entries with a section comment
        section = "\n    # ===== AUTO-ASSIGNED (additive pass) =====\n" + "".join(new_entries)
        src = src[:close_idx] + section + src[close_idx:]

    themes_py.write_text(src)
    print(f"Updated {themes_py}")
    print(f"  Added {len(new_entries)} brand-new entries")
    print(f"  Patched {len(updated_apps)} existing entries (added archetype fields)")
    print(f"  Skipped {len(skipped_apps)} entries already complete")

    # Print category summary
    print("\nApps per category:")
    for cat, names in sorted(by_cat.items()):
        print(f"  {cat:10s}: {len(names):3d}")
    print(f"  {'TOTAL':10s}: {sum(len(v) for v in by_cat.values()):3d}")


if __name__ == "__main__":
    main()
