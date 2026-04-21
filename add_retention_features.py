#!/usr/bin/env python3
"""
add_retention_features.py
Adds to all 6 games:
  1. Hint system upgrades (3 free + ad/IAP) for BallSort, WaterSort, Puzzle2048, PipeConnect, Nonogram
  2. Comeback bonus (3+ day absence → extra coins)
  3. Player titles (milestone notifications)
  4. Weekend 2x-coin event banner
  5. Weekly fake tournament / leaderboard
  6. Share button after level completion
  7. First-milestone level bonuses (levels 10, 25, 50, 100, 200)
  + shareText() added to all 6 NativeBridge Java files
Safe to re-run — skips if already injected.
"""

import os, re

BASE = "/home/pgs/Documents/Gs"
GAMES = ["BallSortPuzzle", "WaterSort", "Nonogram", "PipeConnect", "Puzzle2048", "UnblockPuzzle"]

JAVA_PACKAGES = {
    "BallSortPuzzle": "com.pegasusgames.ballsort",
    "WaterSort":      "com.pegasusgames.watersort",
    "Nonogram":       "com.pegasusgames.nonogram",
    "PipeConnect":    "com.pegasusgames.pipeconnect",
    "Puzzle2048":     "com.pegasusgames.puzzle2048",
    "UnblockPuzzle":  "com.pegasusgames.unblockpuzzle",
}

GAME_NAMES = {
    "BallSortPuzzle": "Ball Sort Puzzle",
    "WaterSort":      "Water Sort",
    "Nonogram":       "Nonogram",
    "PipeConnect":    "Pipe Connect",
    "Puzzle2048":     "2048",
    "UnblockPuzzle":  "Unblock Puzzle",
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. JAVA — add shareText() to NativeBridge
# ─────────────────────────────────────────────────────────────────────────────

SHARE_TEXT_METHOD = """
        @JavascriptInterface
        public void shareText(String text) {
            runOnUiThread(() -> {
                android.content.Intent shareIntent = new android.content.Intent(
                        android.content.Intent.ACTION_SEND);
                shareIntent.setType("text/plain");
                shareIntent.putExtra(android.content.Intent.EXTRA_TEXT, text);
                startActivity(android.content.Intent.createChooser(shareIntent, "Share"));
            });
        }
"""

def patch_java_share(game):
    pkg = JAVA_PACKAGES[game]
    pkg_path = pkg.replace(".", "/")
    java_path = os.path.join(BASE, game, "android", "app", "src", "main", "java",
                             pkg_path, "MainActivity.java")
    if not os.path.exists(java_path):
        print(f"  ✗ {game}: MainActivity.java not found")
        return False
    with open(java_path, encoding="utf-8") as f:
        src = f.read()
    if "shareText" in src:
        return True  # already has it
    # Insert before the closing brace of NativeBridge class
    # Find the last @JavascriptInterface block then insert after it
    marker = "public void logEvent(String eventName, String params) {"
    if marker not in src:
        # Fallback: find closing of NativeBridge by looking for last @JavascriptInterface
        # Insert shareText before the class-closing brace pattern
        marker = "public void requestNotificationPermission() {"
    if marker in src:
        # Find the end of that method, then insert after it
        idx = src.index(marker)
        # Find the closing brace of this method (count braces)
        depth = 0
        pos = idx
        while pos < len(src):
            if src[pos] == '{':
                depth += 1
            elif src[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        insert_at = pos + 1
        src = src[:insert_at] + "\n" + SHARE_TEXT_METHOD + src[insert_at:]
        with open(java_path, "w", encoding="utf-8") as f:
            f.write(src)
        return True
    print(f"  ✗ {game}: Could not find insertion point for shareText")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 2. HINT SYSTEM — game-specific patches
# ─────────────────────────────────────────────────────────────────────────────

HINT_OVERLAY_HTML = """<!-- HINT PURCHASE OVERLAY -->
<div id="rf-hint-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:8888;align-items:center;justify-content:center;backdrop-filter:blur(6px);">
  <div style="background:linear-gradient(145deg,#1e1b4b,#1a1a2e);border:1px solid rgba(255,215,0,0.25);border-radius:22px;padding:28px 22px;max-width:300px;width:85%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.6);">
    <div style="font-size:48px;margin-bottom:8px;">💡</div>
    <div style="color:#fff;font-size:20px;font-weight:800;margin-bottom:6px;">Need a Hint?</div>
    <div style="color:rgba(255,255,255,0.5);font-size:13px;margin-bottom:20px;">No free hints remaining</div>
    <button onclick="window.rfHintWatchAd()" style="width:100%;padding:14px;margin-bottom:10px;border:none;border-radius:13px;background:linear-gradient(135deg,#6c5ce7,#a29bfe);color:#fff;font-size:16px;font-weight:700;cursor:pointer;">📺 Watch Ad (Free Hint)</button>
    <button onclick="window.rfHintBuyPack()" style="width:100%;padding:14px;margin-bottom:10px;border:none;border-radius:13px;background:linear-gradient(135deg,#ffd700,#f39c12);color:#1a1a00;font-size:16px;font-weight:700;cursor:pointer;">💰 Buy 10 Hints ($0.99)</button>
    <button onclick="window.rfHintSpendCoins()" style="width:100%;padding:14px;margin-bottom:10px;border:none;border-radius:13px;background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.7);font-size:16px;font-weight:700;cursor:pointer;" id="rf-hint-coin-btn">🪙 Spend 20 Coins</button>
    <button onclick="document.getElementById('rf-hint-overlay').style.display='none'" style="width:100%;padding:12px;border:none;border-radius:13px;background:transparent;color:rgba(255,255,255,0.4);font-size:15px;cursor:pointer;">Cancel</button>
  </div>
</div>"""

HINT_SYSTEM_JS = """
<script>
/* ===== HINT SYSTEM (rf) ===== */
(function(){
  var rfFreeHints = 3;
  var RF_HINT_AD_TYPE = 'hint';

  function rfGetCoins(){
    try{
      if(typeof State!=='undefined'&&typeof State.coins==='number') return State.coins;
      if(typeof state!=='undefined'&&typeof state.coins==='number') return state.coins;
      if(typeof save!=='undefined'&&typeof save.coins==='number') return save.coins;
    }catch(e){}
    return 0;
  }
  function rfSetCoins(n){
    try{
      if(typeof State!=='undefined'&&typeof State.coins==='number'){State.coins=n;if(typeof State.save==='function')State.save();else if(typeof saveState==='function')saveState();}
      else if(typeof state!=='undefined'&&typeof state.coins==='number'){state.coins=n;if(typeof saveState==='function')saveState();else if(typeof persist==='function')persist();}
      else if(typeof save!=='undefined'&&typeof save.coins==='number'){save.coins=n;if(typeof persist==='function')persist();}
      if(typeof updateCoinDisplays==='function')updateCoinDisplays();
      else if(typeof updateHUD==='function')updateHUD();
      else if(typeof updateAllUI==='function')updateAllUI();
    }catch(e){}
  }
  function rfUpdateHintBtn(){
    var btns=document.querySelectorAll('.rf-hint-count');
    btns.forEach(function(b){b.textContent=rfFreeHints>0?'('+rfFreeHints+')':'';});
  }
  function rfShowOverlay(){
    var o=document.getElementById('rf-hint-overlay');
    if(o){
      var coinBtn=document.getElementById('rf-hint-coin-btn');
      if(coinBtn) coinBtn.textContent='🪙 Spend 20 Coins ('+(rfGetCoins())+' available)';
      o.style.display='flex';
    }
  }
  window.rfUseHint=function(){
    if(rfFreeHints>0){rfFreeHints--;rfUpdateHintBtn();rfDoHint();return;}
    rfShowOverlay();
  };
  window.rfHintWatchAd=function(){
    document.getElementById('rf-hint-overlay').style.display='none';
    if(window.Android){
      try{
        // Use game's existing rewarded ad pattern
        if(typeof safeShowRewarded==='function'){safeShowRewarded(RF_HINT_AD_TYPE);return;}
        if(typeof requestRewardedAd==='function'){requestRewardedAd(RF_HINT_AD_TYPE);return;}
        if(typeof showRewardedAd==='function'){showRewardedAd(RF_HINT_AD_TYPE,function(){rfFreeHints++;rfDoHint();rfUpdateHintBtn();});return;}
        Android.showRewarded(RF_HINT_AD_TYPE);
      }catch(e){}
    } else { rfFreeHints++;rfDoHint();rfUpdateHintBtn(); }
  };
  window.rfHintBuyPack=function(){
    document.getElementById('rf-hint-overlay').style.display='none';
    if(window.Android){
      try{
        if(typeof safePurchase==='function'){safePurchase('hint_pack');return;}
        if(typeof purchase==='function'){purchase('hint_pack');return;}
        Android.purchase('hint_pack');
      }catch(e){}
    }
  };
  window.rfHintSpendCoins=function(){
    if(rfGetCoins()<20){
      var o=document.getElementById('rf-hint-overlay');if(o)o.style.display='none';
      if(typeof showToast==='function')showToast('Not enough coins!');
      return;
    }
    rfSetCoins(rfGetCoins()-20);
    document.getElementById('rf-hint-overlay').style.display='none';
    rfFreeHints++;rfDoHint();rfUpdateHintBtn();
  };
  // Called after ad reward if game uses VALID_REWARD_TYPES pattern
  var _origOnAdReward=window.onAdReward;
  window.onAdReward=function(type){
    if(type===RF_HINT_AD_TYPE){rfFreeHints+=3;rfUpdateHintBtn();rfDoHint();return;}
    if(typeof _origOnAdReward==='function')_origOnAdReward(type);
  };
  // Called after IAP
  var _origOnPurchaseComplete=window.onPurchaseComplete;
  window.onPurchaseComplete=function(productId){
    if(productId==='hint_pack'){rfFreeHints+=10;rfUpdateHintBtn();if(typeof showToast==='function')showToast('+10 Hints!');return;}
    if(typeof _origOnPurchaseComplete==='function')_origOnPurchaseComplete(productId);
  };
  function rfDoHint(){
    // Try game-specific hint functions
    try{
      if(typeof Game!=='undefined'&&typeof Game.showHint==='function'){Game.showHint();return;}
      if(typeof showHint==='function'){showHint();return;}
      if(typeof giveHint==='function'){giveHint();return;}
      if(typeof useHint==='function'&&window._rfHintActive){window._rfHintActive=false;useHint();return;}
    }catch(e){}
  }
  // Expose for use in updated hint buttons
  window._rfFreeHints=function(){return rfFreeHints;};
  rfUpdateHintBtn();
})();
</script>
"""

def patch_hints_ballsort_watersort(game, html):
    """Add freeHints gate to BallSort/WaterSort showHint()"""
    if "rf-hint-overlay" in html:
        return html, False

    # 1. Inject hint overlay HTML before </body>
    hint_inject = HINT_OVERLAY_HTML + "\n"

    # 2. Intercept Game.showHint after Game object is closed
    # Find the showHint method and wrap it
    # Insert hint count span into hint button
    html = re.sub(
        r'(<button[^>]*onclick="Game\.showHint\(\)"[^>]*>)(💡 Hint)',
        r'\1💡 Hint <span class="rf-hint-count" style="font-size:0.75em;opacity:0.8;"></span>',
        html
    )

    # Intercept Game.showHint: add a wrapper right before </script> of main script
    # We'll do it via the shared JS module instead (rfDoHint calls Game.showHint)
    # Replace onclick to use rfUseHint instead
    html = html.replace('onclick="Game.showHint()"', 'onclick="window.rfUseHint()"')

    # 3. Insert before </body>
    inject = hint_inject + HINT_SYSTEM_JS + "\n"
    html = html.replace("</body>", inject + "</body>", 1)
    return html, True


def patch_hints_puzzle2048(html):
    """Add full hint system to Puzzle2048"""
    if "rf-hint-overlay" in html:
        return html, False

    # 1. Add hint button to game-footer
    html = html.replace(
        '<button class="game-btn" onclick="Game.confirmNewGame()">↺ New</button>',
        '<button class="game-btn" onclick="Game.confirmNewGame()">↺ New</button>\n'
        '      <button class="game-btn" id="p2048-hint-btn" onclick="window.rfUseHint()" '
        'style="background:rgba(255,215,0,0.12);border-color:rgba(255,215,0,0.4);color:#ffd700;">'
        '💡 <span class="rf-hint-count" style="font-size:0.75em;opacity:0.8;"></span></button>'
    )

    # 2. Add 'hint' to VALID_REWARD_TYPES
    html = html.replace(
        "const VALID_REWARD_TYPES = new Set(['undo','continue','life']);",
        "const VALID_REWARD_TYPES = new Set(['undo','continue','life','hint']);"
    )

    # 3. Add hint_pack to VALID_PRODUCTS
    html = html.replace(
        "const VALID_PRODUCTS = new Set([\n  'remove_ads','coins_small','coins_large',\n  'undo_pack','five_lives','unlimited_lives_1h','unlimited_lives_forever'\n]);",
        "const VALID_PRODUCTS = new Set([\n  'remove_ads','coins_small','coins_large',\n  'undo_pack','five_lives','unlimited_lives_1h','unlimited_lives_forever','hint_pack'\n]);"
    )

    # 4. Add hint to shop
    html = html.replace(
        "  { id: 'undo_pack',",
        "  { id: 'hint_pack', name: 'Hint Pack', desc: '+10 hints', price: '$0.99', emoji: '💡', type: 'real' },\n  { id: 'undo_pack',"
    )

    # 5. Handle hint_pack in onPurchaseComplete
    hint_purchase_case = """    case 'hint_pack':
      State.hintPack = (State.hintPack || 0) + 10;
      showToast('+10 Hints!');
      break;
"""
    html = html.replace("    case 'undo_pack':", hint_purchase_case + "    case 'undo_pack':")

    # 6. Add rfDoHint for 2048 — show best move direction
    p2048_hint_js = """
<script>
/* 2048 hint: shows best direction */
(function(){
  var _pendingDir = null;
  window._rf2048HintDir = null;
  function tryMove(grid, dir) {
    var G = grid.map(function(r){return r.slice();});
    var score = 0;
    var moved = false;
    var SIZE = G.length;
    function slideRow(row) {
      var r = row.filter(function(x){return x>0;});
      for(var i=0;i<r.length-1;i++) if(r[i]===r[i+1]){score+=r[i]*2;r[i]*=2;r.splice(i+1,1);moved=true;}
      while(r.length<SIZE) r.push(0);
      return r;
    }
    if(dir==='left') G=G.map(slideRow);
    else if(dir==='right') G=G.map(function(r){return slideRow(r.reverse()).reverse();});
    else if(dir==='up') {
      for(var c=0;c<SIZE;c++){var col=G.map(function(r){return r[c];});col=slideRow(col);G.forEach(function(r,i){r[c]=col[i];});}
    } else {
      for(var c=0;c<SIZE;c++){var col=G.map(function(r){return r[c];}).reverse();col=slideRow(col).reverse();G.forEach(function(r,i){r[c]=col[i];});}
    }
    for(var i=0;i<SIZE;i++) for(var j=0;j<SIZE;j++) if(G[i][j]!==grid[i][j]) moved=true;
    return {score:score, moved:moved, grid:G};
  }
  window._rf2048Compute = function(grid) {
    var dirs = ['left','down','right','up'];
    var best = null, bestScore = -1;
    for(var i=0;i<dirs.length;i++){
      var r=tryMove(grid,dirs[i]);
      if(r.moved && r.score >= bestScore){bestScore=r.score;best=dirs[i];}
    }
    return best;
  };
})();
</script>
"""

    hint_inject = HINT_OVERLAY_HTML + "\n" + p2048_hint_js
    inject = hint_inject + HINT_SYSTEM_JS + "\n"

    # Also override rfDoHint for 2048 context by appending an override
    override = """
<script>
/* 2048-specific rfDoHint override */
(function(){
  var ARROWS = {left:'← Left',right:'→ Right',up:'↑ Up',down:'↓ Down'};
  window.rfDoHint_2048 = function(){
    if(typeof State==='undefined'||!State.grid) return;
    var dir = window._rf2048Compute(State.grid);
    if(!dir){if(typeof showToast==='function')showToast('No moves available!');return;}
    // Flash direction arrow overlay
    var ov = document.getElementById('rf-2048-arrow');
    if(!ov){
      ov=document.createElement('div');ov.id='rf-2048-arrow';
      ov.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);'+
        'background:rgba(0,0,0,0.85);color:#ffd700;font-size:52px;font-weight:900;'+
        'padding:20px 36px;border-radius:18px;z-index:7777;pointer-events:none;'+
        'opacity:0;transition:opacity 0.3s;';
      document.body.appendChild(ov);
    }
    ov.textContent = 'Best: ' + ARROWS[dir];
    ov.style.opacity='1';
    setTimeout(function(){ov.style.opacity='0';},2200);
    if(typeof showToast==='function')showToast('Best move: '+ARROWS[dir]);
  };
  // Monkey-patch rfDoHint to call 2048-specific version
  var _origRf=window.rfDoHint;
  // We override via the rfUseHint -> rfDoHint chain
  // Since the module uses the internal rfDoHint via closure, we hook Game/showHint
  if(typeof Game!=='undefined'){
    Game.showHint = window.rfDoHint_2048;
  } else {
    window.showHint = window.rfDoHint_2048;
  }
})();
</script>
"""

    html = html.replace("</body>", inject + override + "</body>", 1)
    return html, True


def patch_hints_pipeconnect(html):
    """Add freeHints gate to PipeConnect useHint()"""
    if "rf-hint-overlay" in html:
        return html, False

    # Add freeHints to defaultSave
    html = html.replace(
        "    soundEnabled:true,\n    musicEnabled:false\n  };\n}",
        "    soundEnabled:true,\n    musicEnabled:false,\n    freeHints:3\n  };\n}"
    )

    # Modify useHint() to check freeHints first
    old_use_hint = """function useHint(){
  showOverlay('overlay-hint');
}"""
    new_use_hint = """function useHint(){
  if(save.freeHints>0){save.freeHints--;persist();updateAllUI();giveHint();return;}
  showOverlay('overlay-hint');
}"""
    html = html.replace(old_use_hint, new_use_hint)

    # Update hint button to show count
    html = re.sub(
        r'(<button[^>]*onclick="useHint\(\)"[^>]*>)(💡 Hint)',
        r'\1💡 Hint <span class="rf-hint-count" style="font-size:0.75em;opacity:0.75;"></span>',
        html
    )

    # Update updateAllUI to refresh hint count (add to existing pattern)
    # Add count update in render/updateAllUI - we'll handle via shared module
    inject = HINT_OVERLAY_HTML + "\n" + HINT_SYSTEM_JS + "\n"
    html = html.replace("</body>", inject + "</body>", 1)
    return html, True


def patch_hints_nonogram(html):
    """Give Nonogram 3 free hints on first run"""
    if "rf-hint-overlay" in html:
        return html, False

    # Change default hintPack from 0 to 3 in defaultState
    html = html.replace("  hintPack: 0,", "  hintPack: 3,")

    # Also update the hint button to show count if not already
    # Nonogram already shows hintPack count - keep as is
    inject = HINT_OVERLAY_HTML + "\n" + HINT_SYSTEM_JS + "\n"
    html = html.replace("</body>", inject + "</body>", 1)
    return html, True


# ─────────────────────────────────────────────────────────────────────────────
# 3. SHARED RETENTION MODULE (CSS + HTML + JS)
# ─────────────────────────────────────────────────────────────────────────────

RETENTION_TEMPLATE = """
<!-- ===== RETENTION FEATURES ===== -->
<style>
/* Retention Module */
@keyframes rf-pop-in {{from{{transform:scale(0.85) translateY(24px);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes rf-shimmer {{0%{{background-position:-200% 0}}100%{{background-position:200% 0}}}}
#rf-comeback-ov,#rf-title-ov,#rf-tournament-ov {{
  position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:9000;
  display:none;align-items:center;justify-content:center;
  backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);
}}
.rf-card {{
  background:linear-gradient(145deg,#1e1b4b 0%,#1a1a2e 100%);
  border:1px solid rgba(255,215,0,0.2);border-radius:24px;
  padding:28px 22px;max-width:310px;width:86%;text-align:center;
  box-shadow:0 20px 56px rgba(0,0,0,0.65);animation:rf-pop-in 0.32s ease;
}}
.rf-card h2{{color:#fff;font-size:22px;font-weight:800;margin:8px 0 4px;}}
.rf-card .rf-sub{{color:rgba(255,255,255,0.45);font-size:13px;margin-bottom:18px;}}
.rf-coin-big{{color:#ffd700;font-size:40px;font-weight:800;line-height:1;margin-bottom:16px;}}
.rf-btn{{width:100%;padding:14px;border:none;border-radius:14px;
  background:linear-gradient(135deg,#ffd700,#f39c12);
  color:#1a1a00;font-size:17px;font-weight:800;cursor:pointer;transition:transform 0.1s;}}
.rf-btn:active{{transform:scale(0.97);}}
.rf-btn-ghost{{background:transparent;color:rgba(255,255,255,0.4);margin-top:8px;
  font-size:14px;cursor:pointer;border:none;width:100%;padding:10px;}}
/* Weekend banner */
#rf-weekend-banner{{
  position:fixed;top:0;left:0;right:0;z-index:500;
  background:linear-gradient(90deg,#e17055,#d63031,#e17055);
  background-size:200% 100%;animation:rf-shimmer 2.5s linear infinite;
  color:#fff;text-align:center;font-size:13px;font-weight:700;
  padding:6px;cursor:pointer;display:none;
}}
/* Share toast */
#rf-share-btn{{
  position:fixed;bottom:80px;right:16px;z-index:6000;
  background:linear-gradient(135deg,#00b894,#00cec9);
  color:#fff;border:none;border-radius:50px;
  padding:10px 18px;font-size:14px;font-weight:700;cursor:pointer;
  box-shadow:0 4px 16px rgba(0,184,148,0.4);
  opacity:0;transition:all 0.35s;pointer-events:none;
}}
#rf-share-btn.rf-visible{{opacity:1;pointer-events:auto;}}
/* Tournament leaderboard */
.rf-lb-row{{display:flex;align-items:center;gap:10px;padding:8px;border-radius:10px;margin-bottom:6px;}}
.rf-lb-row.rf-you{{background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.3);}}
.rf-lb-rank{{font-size:18px;width:28px;text-align:center;}}
.rf-lb-name{{flex:1;color:#fff;font-size:14px;font-weight:600;text-align:left;}}
.rf-lb-score{{color:#ffd700;font-size:14px;font-weight:800;}}
/* Player title toast */
#rf-title-toast{{
  position:fixed;top:72px;left:50%;transform:translateX(-50%) translateY(-20px);
  background:linear-gradient(135deg,#00b894,#00cec9);color:#fff;
  padding:10px 22px;border-radius:50px;font-size:13px;font-weight:700;
  opacity:0;transition:all 0.4s;z-index:10000;pointer-events:none;white-space:nowrap;
  box-shadow:0 4px 20px rgba(0,184,148,0.5);
}}
#rf-title-toast.rf-show{{opacity:1;transform:translateX(-50%) translateY(0);}}
</style>

<!-- Comeback bonus overlay -->
<div id="rf-comeback-ov">
  <div class="rf-card">
    <div style="font-size:52px;">🎉</div>
    <h2>Welcome Back!</h2>
    <div class="rf-sub" id="rf-comeback-sub">You were away for a few days</div>
    <div class="rf-coin-big" id="rf-comeback-coins">+100 🪙</div>
    <button class="rf-btn" onclick="window.rfClaimComeback()">Claim Bonus!</button>
  </div>
</div>

<!-- Title unlock overlay -->
<div id="rf-title-ov">
  <div class="rf-card">
    <div style="font-size:52px;">🏆</div>
    <h2>New Title Earned!</h2>
    <div class="rf-sub">You've unlocked a new rank</div>
    <div style="color:#ffd700;font-size:28px;font-weight:800;margin-bottom:18px;" id="rf-title-name">Expert 🎯</div>
    <button class="rf-btn" onclick="document.getElementById('rf-title-ov').style.display='none'">Awesome!</button>
  </div>
</div>

<!-- Tournament overlay -->
<div id="rf-tournament-ov">
  <div class="rf-card" style="max-width:340px;">
    <div style="font-size:40px;margin-bottom:6px;">🏆</div>
    <h2>Weekly Tournament</h2>
    <div class="rf-sub" id="rf-tourn-sub">Resets every Monday</div>
    <div id="rf-leaderboard" style="margin-bottom:16px;max-height:280px;overflow-y:auto;"></div>
    <button class="rf-btn-ghost" onclick="document.getElementById('rf-tournament-ov').style.display='none'">Close</button>
  </div>
</div>

<!-- Weekend banner -->
<div id="rf-weekend-banner" onclick="this.style.display='none'">
  🎉 WEEKEND BONUS: 2× Coins all weekend! Tap to dismiss
</div>

<!-- Share button -->
<button id="rf-share-btn" onclick="window.rfDoShare()">🔗 Share Result</button>

<!-- Title toast -->
<div id="rf-title-toast"></div>

<script>
/* ===== RETENTION MODULE ===== */
(function(){{
  var GAME_KEY = '{game_key}';
  var GAME_NAME = '{game_name}';
  var RF_KEY = 'rf_' + GAME_KEY;

  // ── Coin helpers ──────────────────────────────────────────────────────────
  function grantCoins(n){{
    try{{
      if(typeof addCoins==='function'){{addCoins(n);return;}}
      var s=(typeof State!=='undefined')?State:(typeof state!=='undefined')?state:(typeof save!=='undefined')?save:null;
      if(!s)return;
      s.coins=(s.coins||0)+n;
      if(typeof State!=='undefined'&&typeof State.save==='function')State.save();
      else if(typeof saveState==='function')saveState();
      else if(typeof persist==='function')persist();
      if(typeof updateCoinDisplays==='function')updateCoinDisplays();
      else if(typeof updateHUD==='function')updateHUD();
      else if(typeof updateAllUI==='function')updateAllUI();
    }}catch(e){{}}
  }}
  function getCoins(){{
    try{{
      var s=(typeof State!=='undefined')?State:(typeof state!=='undefined')?state:(typeof save!=='undefined')?save:null;
      return s?s.coins||0:0;
    }}catch(e){{return 0;}}
  }}
  function getLevels(){{
    try{{
      var s=(typeof State!=='undefined')?State:(typeof state!=='undefined')?state:(typeof save!=='undefined')?save:null;
      if(!s)return 0;
      if(typeof s.currentLevel==='number')return s.currentLevel;
      if(typeof s.completedLevels==='number')return s.completedLevels;
      if(Array.isArray(s.completedLevels))return s.completedLevels.length;
      if(s.completedLevels&&typeof s.completedLevels==='object')return Object.keys(s.completedLevels).length;
    }}catch(e){{}}
    return 0;
  }}
  function getData(){{try{{return JSON.parse(localStorage.getItem(RF_KEY)||'{{}}')}};catch(e){{return{{}}};}}
  function setData(d){{try{{localStorage.setItem(RF_KEY,JSON.stringify(d));}}catch(e){{}}}}

  // ── COMEBACK BONUS ────────────────────────────────────────────────────────
  function checkComeback(){{
    var ls=JSON.parse(localStorage.getItem('ls_v2')||'{{"d":""}}');
    if(!ls.d)return;
    var today=new Date().toLocaleDateString('en-CA');
    if(ls.d===today)return; // just logged in today
    var lastMs=new Date(ls.d).getTime();
    var diff=Math.round((Date.now()-lastMs)/86400000);
    if(diff<3)return;
    var d=getData();
    if(d.comeback_claimed===ls.d)return;
    var bonus=diff>=14?250:diff>=7?150:diff>=5?100:50;
    d.comeback_claimed=ls.d;
    setData(d);
    setTimeout(function(){{
      document.getElementById('rf-comeback-sub').textContent=
        'You were away for '+diff+' day'+(diff!==1?'s':'')+' — here\'s a reward!';
      document.getElementById('rf-comeback-coins').textContent='+'+bonus+' 🪙';
      document.getElementById('rf-comeback-ov').style.display='flex';
      window._rfComebackBonus=bonus;
    }},1800);
  }}
  window.rfClaimComeback=function(){{
    document.getElementById('rf-comeback-ov').style.display='none';
    grantCoins(window._rfComebackBonus||50);
    if(window.Android)try{{Android.logEvent('comeback_bonus','days='+window._rfComebackBonus);}}catch(e){{}}
  }};

  // ── PLAYER TITLES ─────────────────────────────────────────────────────────
  var TITLES=[
    [1,'Newcomer 🌱'],[10,'Explorer 🗺️'],[25,'Challenger ⚔️'],
    [50,'Expert 🎯'],[100,'Master 🏆'],[200,'Grandmaster 👑'],[500,'Legend 🌟']
  ];
  function checkTitle(){{
    var lvls=getLevels();
    var d=getData();
    var lastTitle=d.lastTitle||0;
    var newTitle=null;
    for(var i=TITLES.length-1;i>=0;i--){{
      if(lvls>=TITLES[i][0]&&TITLES[i][0]>lastTitle){{newTitle=TITLES[i];break;}}
    }}
    if(!newTitle)return;
    d.lastTitle=newTitle[0];
    setData(d);
    setTimeout(function(){{
      document.getElementById('rf-title-name').textContent=newTitle[1];
      document.getElementById('rf-title-ov').style.display='flex';
    }},2200);
  }}

  // ── WEEKEND EVENT ─────────────────────────────────────────────────────────
  function checkWeekend(){{
    var day=new Date().getDay();
    if(day===0||day===6){{
      var el=document.getElementById('rf-weekend-banner');
      if(el)el.style.display='block';
      // Patch grantCoins to double weekend rewards
      var _origGrant=window.addCoins;
      if(typeof _origGrant==='function'&&!window._rfWeekendPatched){{
        window._rfWeekendPatched=true;
        window.addCoins=function(n){{_origGrant(n*2);}};
      }}
    }}
  }}

  // ── WEEKLY TOURNAMENT ─────────────────────────────────────────────────────
  var FAKE_NAMES=['Alex K.','Sam R.','Jordan M.','Casey T.','Riley B.',
                   'Morgan L.','Drew H.','Jamie S.','Avery P.'];
  function weekNum(){{return Math.floor(Date.now()/(7*86400000));}}
  function seededRng(seed){{
    var s=seed;
    return function(){{s=(s*1664525+1013904223)&0xffffffff;return Math.abs(s)/0xffffffff;}};
  }}
  function buildLeaderboard(playerScore){{
    var wk=weekNum();
    var rng=seededRng(wk*31337+GAME_KEY.charCodeAt(0));
    var entries=FAKE_NAMES.map(function(name,i){{
      var base=Math.floor(rng()*120)+20;
      return{{name:name,score:base,you:false}};
    }});
    entries.push({{name:'You',score:playerScore,you:true}});
    entries.sort(function(a,b){{return b.score-a.score;}});
    return entries;
  }}
  function getWeekScore(){{
    var d=getData();
    var wk=weekNum();
    if(d.tournWeek!==wk){{d.tournWeek=wk;d.tournScore=0;setData(d);}}
    return d.tournScore||0;
  }}
  window.rfAddTournScore=function(n){{
    var d=getData();
    var wk=weekNum();
    if(d.tournWeek!==wk){{d.tournWeek=wk;d.tournScore=0;}}
    d.tournScore=(d.tournScore||0)+n;
    setData(d);
  }};
  window.rfShowTournament=function(){{
    var score=getWeekScore();
    var entries=buildLeaderboard(score);
    var html='';
    var medals=['🥇','🥈','🥉'];
    entries.forEach(function(e,i){{
      var rank=medals[i]||('#'+(i+1));
      html+='<div class="rf-lb-row'+(e.you?' rf-you':'')+'">'+
        '<div class="rf-lb-rank">'+rank+'</div>'+
        '<div class="rf-lb-name">'+(e.you?'<b>You</b>':e.name)+'</div>'+
        '<div class="rf-lb-score">'+e.score+' pts</div></div>';
    }});
    document.getElementById('rf-leaderboard').innerHTML=html;
    // Check if player won last week
    var d=getData();
    var wk=weekNum();
    if(d.tournWeek===wk-1&&d.tournScore>0){{
      var lastEntries=buildLeaderboard(d.tournScore);
      var rank=lastEntries.findIndex(function(e){{return e.you;}})+1;
      if(rank<=3){{
        var prizes=[0,150,100,50];
        var prize=prizes[rank]||0;
        if(prize>0&&!d.tournPrizeClaimed){{
          d.tournPrizeClaimed=wk;
          setData(d);
          grantCoins(prize);
          document.getElementById('rf-tourn-sub').textContent=
            '🏆 You placed #'+rank+' last week! +'+prize+' coins awarded!';
        }}
      }}
    }}
    document.getElementById('rf-tournament-ov').style.display='flex';
  }};
  // Add tournament button to menu if not there
  function addTournBtn(){{
    var menus=['#screen-menu .screen-btns','#menuScreen .menu-btns',
               '#screen-menu','#menuScreen','#mainMenu'];
    for(var i=0;i<menus.length;i++){{
      var el=document.querySelector(menus[i]);
      if(el){{
        var existing=document.getElementById('rf-tourn-menu-btn');
        if(!existing){{
          var btn=document.createElement('button');
          btn.id='rf-tourn-menu-btn';
          btn.onclick=window.rfShowTournament;
          btn.textContent='🏆 Weekly Tournament';
          btn.style.cssText='margin-top:8px;padding:12px 20px;border:1px solid rgba(255,215,0,0.35);'+
            'border-radius:14px;background:rgba(255,215,0,0.07);color:#ffd700;'+
            'font-size:15px;font-weight:700;cursor:pointer;width:80%;max-width:220px;display:block;margin-left:auto;margin-right:auto;';
          var refBtn=el.querySelector('button:last-child');
          if(refBtn)el.insertBefore(btn,refBtn.nextSibling);
          else el.appendChild(btn);
        }}
        break;
      }}
    }}
  }}

  // ── SHARE ─────────────────────────────────────────────────────────────────
  var rfShareText='';
  window.rfSetShareText=function(t){{rfShareText=t;var b=document.getElementById('rf-share-btn');if(b)b.classList.add('rf-visible');}};
  window.rfHideShareBtn=function(){{var b=document.getElementById('rf-share-btn');if(b)b.classList.remove('rf-visible');}};
  window.rfDoShare=function(){{
    var txt=rfShareText||('Just played '+GAME_NAME+'! 🎮 Try it on Google Play!');
    if(window.Android&&typeof Android.shareText==='function'){{Android.shareText(txt);return;}}
    try{{
      if(navigator.clipboard){{navigator.clipboard.writeText(txt);}}
      if(typeof showToast==='function')showToast('Result copied to clipboard!');
    }}catch(e){{}}
  }};

  // ── FIRST MILESTONE BONUS ──────────────────────────────────────────────────
  var MILESTONES=[10,25,50,100,200,500];
  var MILESTONE_REWARDS=[30,50,80,120,200,350];
  function checkMilestones(){{
    var lvls=getLevels();
    var d=getData();
    d.milestonesHit=d.milestonesHit||[];
    for(var i=0;i<MILESTONES.length;i++){{
      if(lvls>=MILESTONES[i]&&d.milestonesHit.indexOf(MILESTONES[i])===-1){{
        d.milestonesHit.push(MILESTONES[i]);
        setData(d);
        (function(coins,lvl){{
          setTimeout(function(){{
            grantCoins(coins);
            if(typeof showToast==='function')showToast('🎯 Milestone '+lvl+' levels! +'+coins+' 🪙');
          }},2500);
        }})(MILESTONE_REWARDS[i],MILESTONES[i]);
        break; // one at a time
      }}
    }}
  }}

  // ── TITLE TOAST ───────────────────────────────────────────────────────────
  function showTitleToast(txt){{
    var el=document.getElementById('rf-title-toast');
    if(!el)return;
    el.textContent=txt;
    el.classList.add('rf-show');
    setTimeout(function(){{el.classList.remove('rf-show');}},3500);
  }}

  // ── HOOK LEVEL COMPLETE ───────────────────────────────────────────────────
  // Patch the known completion functions to add share + tournament tracking
  function hookCompletion(){{
    var fns=[
      ['showLevelComplete',null],
      ['triggerWin',null],
      ['winPuzzle',null],
      ['checkLevelComplete',null],
    ];
    fns.forEach(function(pair){{
      var name=pair[0];
      if(typeof window[name]==='function'){{
        var orig=window[name];
        window[name]=function(){{
          orig.apply(this,arguments);
          onLevelDone();
        }};
      }}
    }});
    // Also try Game object methods
    if(typeof Game!=='undefined'){{
      ['showLevelComplete','onLevelComplete','showWin'].forEach(function(name){{
        if(typeof Game[name]==='function'){{
          var orig=Game[name].bind(Game);
          Game[name]=function(){{
            orig.apply(this,arguments);
            onLevelDone();
          }};
        }}
      }});
    }}
  }}

  function onLevelDone(){{
    var lvls=getLevels();
    // Share text
    window.rfSetShareText('Just solved level '+lvls+' of '+GAME_NAME+'! 🎮 '+
      'My streak is going strong! Can you beat me?\\n{store_link}');
    // Tournament points: 5 pts per level
    window.rfAddTournScore(5);
    // Check milestones and titles
    checkMilestones();
    checkTitle();
    // Auto-hide share after 8s
    setTimeout(window.rfHideShareBtn,8000);
  }}

  // ── INIT ──────────────────────────────────────────────────────────────────
  function init(){{
    setTimeout(function(){{
      checkComeback();
      checkWeekend();
      checkTitle();
      checkMilestones();
      hookCompletion();
      addTournBtn();
    }},1200);
  }}

  if(document.readyState==='loading'){{
    document.addEventListener('DOMContentLoaded',init);
  }} else {{
    setTimeout(init,400);
  }}
}})();
</script>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. MAIN INJECTION LOOP
# ─────────────────────────────────────────────────────────────────────────────

def inject_game(game):
    html_path = os.path.join(BASE, game, "android", "app", "src", "main", "assets", "game.html")
    if not os.path.exists(html_path):
        print(f"  ✗ {game}: game.html not found")
        return

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    changed = False
    hint_changed = False

    # ── Hint system ──────────────────────────────────────────────────────────
    if game in ("BallSortPuzzle", "WaterSort"):
        html, hint_changed = patch_hints_ballsort_watersort(game, html)
    elif game == "Puzzle2048":
        html, hint_changed = patch_hints_puzzle2048(html)
    elif game == "PipeConnect":
        html, hint_changed = patch_hints_pipeconnect(html)
    elif game == "Nonogram":
        html, hint_changed = patch_hints_nonogram(html)
    # UnblockPuzzle already has complete hint system — just inject retention module

    # ── Shared retention module ───────────────────────────────────────────────
    if "rfClaimComeback" not in html:
        module = make_retention_module(game)
        html = html.replace("</body>", module + "\n</body>", 1)
        changed = True

    if hint_changed:
        changed = True

    if not changed and "rfClaimComeback" in html:
        print(f"  ✓ {game}: already has retention features — skipped")
        return

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Java shareText ────────────────────────────────────────────────────────
    java_ok = patch_java_share(game)

    hints_status = "hint-upgraded, " if hint_changed else ""
    share_status = "shareText-added" if java_ok else "shareText-SKIPPED"
    print(f"  ✓ {game}: {hints_status}retention-module, {share_status}")


if __name__ == "__main__":
    print("Adding retention features to all games...\n")
    for game in GAMES:
        inject_game(game)
    print("\n✅ Done!")
    print("   Features: hint-upgrade, comeback-bonus, player-titles,")
    print("   weekend-2x-coins, weekly-tournament, share-button, milestone-bonuses")
    print("\n   Rebuild all AABs to apply changes.")
