#!/usr/bin/env python3
"""Add _showInterstitial function and hook to apps that already had onPurchaseComplete."""
import os, re

BASE = '/home/pgs/Documents/Gs'

INTERSTITIAL_FN = '''
// Interstitial ad helper
var _interstitialCount = 0;
var _adsRemoved = false;
function _showInterstitial() {
  if (_adsRemoved) return;
  _interstitialCount++;
  if (_interstitialCount % 3 === 0 && window.Android) {
    try { Android.showInterstitial(); } catch(e) {}
  }
}
'''

HOOK_PATTERNS = [
    r'(function\s+calculate\s*\([^)]*\)\s*\{)',
    r'(function\s+calc\s*\([^)]*\)\s*\{)',
    r'(function\s+convert\s*\([^)]*\)\s*\{)',
    r'(function\s+next(?:Card|Word|Round|Question|Prompt)\s*\([^)]*\)\s*\{)',
    r'(function\s+show(?:Recipe|Method|Card|Result)\s*\([^)]*\)\s*\{)',
    r'(function\s+swipe\w*\s*\([^)]*\)\s*\{)',
    r'(function\s+getCard\s*\([^)]*\)\s*\{)',
    r'(function\s+update(?:Display|Stats|Counter)?\s*\(\s*\)\s*\{)',
    r'(function\s+start\s*\([^)]*\)\s*\{)',
    r'(function\s+submit\s*\([^)]*\)\s*\{)',
]

CLICK_FALLBACK = '''
// Show interstitial every 5 taps
var _tapCount = 0;
document.addEventListener('click', function() {
  _tapCount++;
  if (_tapCount % 5 === 0) _showInterstitial();
});
'''

apps = ['AgeCalculator','CocktailGuide','CoffeeGuide','HeadsUpGame',
        'IceBreaker','QuitSmoking','SobrietyCounter','TwoTruthsOneLie']

for app in apps:
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    with open(html_path) as f:
        content = f.read()

    if '_showInterstitial' in content:
        print(f'{app}: already has _showInterstitial')
        continue

    # Inject the function before last </script>
    pos = content.rfind('</script>')
    if pos == -1:
        print(f'{app}: ERROR no </script>')
        continue

    content = content[:pos] + INTERSTITIAL_FN + content[pos:]

    # Try to hook into a function
    hooked = False
    for pattern in HOOK_PATTERNS:
        new_content = re.sub(pattern, r'\1\n  _showInterstitial();', content, count=1)
        if new_content != content:
            content = new_content
            hooked = True
            break

    if not hooked:
        # Click-based fallback
        pos2 = content.rfind('</script>')
        content = content[:pos2] + CLICK_FALLBACK + content[pos2:]
        print(f'{app}: added + click fallback')
    else:
        print(f'{app}: added + function hook')

    with open(html_path, 'w') as f:
        f.write(content)

print('Done')
