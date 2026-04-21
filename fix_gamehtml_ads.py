#!/usr/bin/env python3
"""
Fix game.html files:
1. Apps with NO Android bridge at all - add Remove Ads button, showInterstitial, proper onPurchaseComplete
2. Apps with partial bridge (missing showInterstitial) - add showInterstitial at game events
3. Fix wrong titles (AnimalMerge, BlockPuzzle)
"""
import os, re

BASE = '/home/pgs/Documents/Gs'

# ── Pattern: inject "Remove Ads" button into header / before </body> ─────
# The Remove Ads button snippet to inject
REMOVE_ADS_BTN = '''<button id="btn-remove-ads" onclick="if(window.Android)Android.purchase('remove_ads')" style="position:fixed;top:8px;right:8px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.3);color:#fff;font-size:0.65rem;font-weight:700;padding:5px 10px;border-radius:20px;cursor:pointer;z-index:9999;letter-spacing:0.5px">Remove Ads</button>
'''

# The bridge snippet to inject before </script> closing or </body>
BRIDGE_SNIPPET = '''
// ── AppLovin MAX / IAP bridge ──────────────────────────────────────────
var _adsRemoved = false;
var _interstitialCount = 0;

function _showInterstitial() {
  if (_adsRemoved) return;
  _interstitialCount++;
  if (_interstitialCount % 3 === 0 && window.Android) {
    try { Android.showInterstitial(); } catch(e) {}
  }
}

window.onPurchaseComplete = function(sku) {
  if (sku === 'remove_ads') {
    _adsRemoved = true;
    var btn = document.getElementById('btn-remove-ads');
    if (btn) btn.style.display = 'none';
    if (window.Android) { try { Android.hideBannerAd(); } catch(e) {} }
  }
};

// Restore remove-ads state on load
if (window.Android) {
  try { if (Android.isPurchased && Android.isPurchased('remove_ads')) {
    _adsRemoved = true;
    var btn = document.getElementById('btn-remove-ads');
    if (btn) btn.style.display = 'none';
  }} catch(e) {}
}
'''

# ── Apps with NO Android calls at all (need full bridge + interstitial hooks) ──
NO_BRIDGE_APPS = [
    'AnagramFinder','BoggleGame','BubbleWrap','Cryptogram','DotArt','DrumMachine',
    'Fireworks','GhostWord','Hangman','Kaleidoscope','MandalaColor','PixelArt',
    'SatisfyingSlime','Sokoban','Solitaire','SoundBoard','SpellingBee','WhiteNoise',
    'WoodBlock','WordConnect','WordLadder','WordleClone','YarnSort','ZenGarden'
]

# ── Apps where we also need to add interstitial trigger (they have Android but no showInterstitial) ──
# (will be detected automatically)

def has_android_bridge(content):
    return 'Android.' in content or 'window.Android' in content

def has_interstitial(content):
    return 'showInterstitial' in content or 'interstitial' in content.lower()

def has_remove_ads_btn(content):
    return 'remove_ads' in content or 'Remove Ads' in content or 'removeAds' in content

def has_purchase_complete(content):
    return 'onPurchaseComplete' in content

def fix_app(app):
    html_path = f'{BASE}/{app}/android/app/src/main/assets/game.html'
    if not os.path.exists(html_path):
        return f'{app}: no game.html'

    with open(html_path) as f:
        content = f.read()

    original = content
    changed = False

    # Fix wrong title bugs
    if app == 'AnimalMerge' and '<title>Dice Roller</title>' in content:
        content = content.replace('<title>Dice Roller</title>', '<title>Animal Merge</title>')
        content = content.replace('<h1>Dice Roller</h1>', '<h1>🐾 Animal Merge</h1>')
        changed = True

    if app == 'BlockPuzzle' and '<title>Dice Roller</title>' in content:
        content = content.replace('<title>Dice Roller</title>', '<title>Block Puzzle</title>')
        content = content.replace('<h1>Dice Roller</h1>', '<h1>🧱 Block Puzzle</h1>')
        changed = True

    # Fix legacy onAdMobLoaded → proper AppLovin approach
    if 'window.onAdMobLoaded' in content:
        # Remove the legacy callback - AppLovin doesn't call this
        content = re.sub(
            r'window\.onAdMobLoaded\s*=\s*function\s*\(\)\s*\{[^}]*\};\s*',
            '',
            content
        )
        changed = True

    needs_full_bridge = not has_android_bridge(content)
    needs_remove_ads = not has_remove_ads_btn(content)
    needs_purchase_complete = not has_purchase_complete(content)
    needs_interstitial = not has_interstitial(content)

    # For apps missing the banner-ad div (placeholder), remove it if present
    # The real banner is injected natively by MainActivity
    if '<div class="banner" id="banner-ad">' in content:
        content = content.replace(
            '<div class="banner" id="banner-ad">Advertisement</div>',
            ''
        )
        # Remove the .banner CSS if it's just a placeholder
        content = re.sub(r'\s*\.banner\s*\{[^}]*\}\s*', '\n', content)
        changed = True

    # Inject Remove Ads button after <body>
    if needs_remove_ads:
        content = content.replace('<body>\n', f'<body>\n{REMOVE_ADS_BTN}', 1)
        if '<body>' not in content or REMOVE_ADS_BTN not in content:
            # Try inserting after <body ...>
            content = re.sub(r'(<body[^>]*>)', r'\1\n' + REMOVE_ADS_BTN.strip() + '\n', content, count=1)
        changed = True

    # Inject bridge snippet before </script></body>
    if needs_full_bridge or needs_purchase_complete:
        # Find the last </script> before </body>
        # Insert bridge before the final </script>
        last_script_pos = content.rfind('</script>')
        if last_script_pos != -1:
            content = content[:last_script_pos] + BRIDGE_SNIPPET + '\n' + content[last_script_pos:]
            changed = True

    # Add interstitial trigger - hook into common game completion patterns
    if needs_interstitial and changed:
        # Try to hook into newGame or reset or level complete patterns
        # Most apps have some form of "game over" or "next round" that we can hook
        # We'll add a generic hook by wrapping common function patterns

        # Pattern: function newGame() { ... } → add _showInterstitial() call
        patterns_to_hook = [
            (r'(function\s+newGame\s*\(\s*\)\s*\{)', r'\1\n  _showInterstitial();'),
            (r'(function\s+nextLevel\s*\(\s*\)\s*\{)', r'\1\n  _showInterstitial();'),
            (r'(function\s+resetGame\s*\(\s*\)\s*\{)', r'\1\n  _showInterstitial();'),
            (r'(function\s+startGame\s*\(\s*\)\s*\{)', r'\1\n  _showInterstitial();'),
            (r'(function\s+playAgain\s*\(\s*\)\s*\{)', r'\1\n  _showInterstitial();'),
        ]
        for pattern, replacement in patterns_to_hook:
            new_content = re.sub(pattern, replacement, content, count=1)
            if new_content != content:
                content = new_content
                break

    if changed:
        with open(html_path, 'w') as f:
            f.write(content)
        return f'{app}: fixed'
    return f'{app}: already OK'

# Process all apps
apps = sorted([d for d in os.listdir(BASE)
               if os.path.isdir(f'{BASE}/{d}')
               and os.path.isfile(f'{BASE}/{d}/android/app/src/main/assets/game.html')
               and not d.startswith('_')])

results = []
for app in apps:
    result = fix_app(app)
    results.append(result)
    if 'fixed' in result:
        print(result)

fixed = sum(1 for r in results if 'fixed' in r)
print(f'\nFixed: {fixed}/{len(apps)} apps')
