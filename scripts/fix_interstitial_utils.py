#!/usr/bin/env python3
"""Add _showInterstitial() calls to utility apps that had no hookable game function."""
import os, re

BASE = '/home/pgs/Documents/Gs'

# Each app: the function to hook and the trigger pattern
HOOKS = {
    'AgeCalculator':   ('function calculate()', r'(function\s+calculate\s*\(\s*\)\s*\{)'),
    'CocktailGuide':   ('function showRecipe(', r'(function\s+showRecipe\s*\([^)]*\)\s*\{)'),
    'CoffeeGuide':     ('function showMethod(', r'(function\s+showMethod\s*\([^)]*\)\s*\{)'),
    'HeadsUpGame':     ('function nextCard(', r'(function\s+next(?:Card|Word|Round)\s*\([^)]*\)\s*\{)'),
    'IceBreaker':      ('function nextQuestion(', r'(function\s+next(?:Question|Prompt|Card)\s*\([^)]*\)\s*\{)'),
    'QuitSmoking':     ('function updateDisplay(', r'(function\s+updateDisplay\s*\(\s*\)\s*\{)'),
    'SobrietyCounter': ('function updateDisplay(', r'(function\s+updateDisplay\s*\(\s*\)\s*\{)'),
    'TwoTruthsOneLie': ('function nextRound(', r'(function\s+next(?:Round|Card|Question)\s*\([^)]*\)\s*\{)'),
}

for app, (desc, pattern) in HOOKS.items():
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    if not os.path.exists(html_path):
        print(f'{app}: file not found')
        continue

    with open(html_path) as f:
        content = f.read()

    # Check if bridge snippet exists (it should from earlier fix)
    if '_showInterstitial' not in content:
        print(f'{app}: bridge snippet missing — skipping')
        continue

    # Try to hook the pattern
    new_content = re.sub(pattern, r'\1\n  _showInterstitial();', content, count=1)

    if new_content != content:
        with open(html_path, 'w') as f:
            f.write(new_content)
        print(f'{app}: hooked {desc}')
    else:
        # Try a broader fallback — hook ANY function call that happens on user action
        # For simple utility apps, hook the calculate/convert/submit button handler
        fallbacks = [
            r'(function\s+calc\s*\([^)]*\)\s*\{)',
            r'(function\s+convert\s*\([^)]*\)\s*\{)',
            r'(function\s+submit\s*\([^)]*\)\s*\{)',
            r'(function\s+show\s*\([^)]*\)\s*\{)',
            r'(function\s+update\s*\([^)]*\)\s*\{)',
            r'(function\s+swipe(?:Next|Card|Left|Right)\s*\([^)]*\)\s*\{)',
            r'(function\s+getCard\s*\([^)]*\)\s*\{)',
            r'(function\s+start\s*\([^)]*\)\s*\{)',
        ]
        hooked = False
        for fb in fallbacks:
            new_content = re.sub(fb, r'\1\n  _showInterstitial();', content, count=1)
            if new_content != content:
                with open(html_path, 'w') as f:
                    f.write(new_content)
                m = re.search(fb, content)
                print(f'{app}: hooked via fallback ({m.group(1)[:40] if m else "?"})')
                hooked = True
                break
        if not hooked:
            # Last resort: add a counter-based interstitial on document click
            interstitial_click = '''
// Show interstitial on every 5th user interaction
var _tapCount = 0;
document.addEventListener('click', function() {
  _tapCount++;
  if (_tapCount % 5 === 0) _showInterstitial();
});
'''
            # Insert before last </script>
            pos = content.rfind('</script>')
            if pos != -1:
                new_content = content[:pos] + interstitial_click + content[pos:]
                with open(html_path, 'w') as f:
                    f.write(new_content)
                print(f'{app}: added click-counter interstitial (no hookable function found)')
            else:
                print(f'{app}: could not hook (no </script> found)')

print('Done')
