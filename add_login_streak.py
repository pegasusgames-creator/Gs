#!/usr/bin/env python3
"""
add_login_streak.py
Injects a daily login streak system + achievement toasts into all 6 game.html files.
Safe to run multiple times — skips if already injected.
"""

import os

BASE = "/home/pgs/Documents/Gs"

GAMES = [
    "BallSortPuzzle",
    "WaterSort",
    "Nonogram",
    "PipeConnect",
    "Puzzle2048",
    "UnblockPuzzle",
]

# ─────────────────────────────────────────────────────────────────────────────
# CSS  (inserted before </style>)
# ─────────────────────────────────────────────────────────────────────────────
STREAK_CSS = """
/* ===== DAILY LOGIN STREAK ===== */
@keyframes ls-fire { 0%,100%{transform:scale(1) rotate(-4deg)} 50%{transform:scale(1.18) rotate(4deg)} }
@keyframes ls-card-in { from{transform:scale(0.85) translateY(30px);opacity:0} to{transform:none;opacity:1} }
#ls-overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.88);
  z-index:9999; display:none; align-items:center; justify-content:center;
  backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px);
}
#ls-card {
  background:linear-gradient(145deg,#1e1b4b 0%,#1a1a2e 100%);
  border:1px solid rgba(255,215,0,0.25); border-radius:26px;
  padding:30px 24px; max-width:320px; width:88%; text-align:center;
  box-shadow:0 24px 64px rgba(0,0,0,0.65); animation:ls-card-in 0.35s ease;
}
.ls-fire-icon { font-size:58px; display:block; margin-bottom:6px; animation:ls-fire 1s ease-in-out infinite; }
.ls-h1 { color:#fff; font-size:23px; font-weight:800; margin-bottom:3px; }
.ls-sub { color:rgba(255,255,255,0.45); font-size:12px; margin-bottom:18px; }
.ls-days-row { display:flex; justify-content:center; gap:5px; margin-bottom:18px; }
.ls-day-cell { display:flex; flex-direction:column; align-items:center; gap:3px; }
.ls-day-dot {
  width:36px; height:36px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700;
}
.ls-day-lbl { font-size:8px; color:rgba(255,255,255,0.35); }
.ls-reward-box {
  background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.22);
  border-radius:14px; padding:14px; margin-bottom:20px;
}
.ls-reward-lbl { color:rgba(255,255,255,0.45); font-size:11px; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; }
.ls-reward-amount { color:#ffd700; font-size:36px; font-weight:800; line-height:1; }
.ls-claim-btn {
  width:100%; padding:15px; border:none; border-radius:15px;
  background:linear-gradient(135deg,#ffd700,#f39c12);
  color:#1a1a00; font-size:18px; font-weight:800; cursor:pointer;
  letter-spacing:0.3px; transition:transform 0.1s;
}
.ls-claim-btn:active { transform:scale(0.96); }
/* Achievement pop */
#ls-ach-toast {
  position:fixed; top:72px; left:50%; transform:translateX(-50%) translateY(-24px);
  background:linear-gradient(135deg,#6c5ce7,#a29bfe); color:#fff;
  padding:10px 22px; border-radius:50px; font-size:13px; font-weight:700;
  opacity:0; transition:all 0.4s; z-index:10000;
  pointer-events:none; white-space:nowrap; box-shadow:0 4px 20px rgba(108,92,231,0.5);
}
#ls-ach-toast.ls-show { opacity:1; transform:translateX(-50%) translateY(0); }
"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML  (inserted before </body>)
# ─────────────────────────────────────────────────────────────────────────────
STREAK_HTML = """
<!-- ===== DAILY LOGIN STREAK OVERLAY ===== -->
<div id="ls-overlay">
  <div id="ls-card">
    <span class="ls-fire-icon" id="ls-fire-icon">🔥</span>
    <div class="ls-h1">Day <span id="ls-day-num">1</span> Streak!</div>
    <div class="ls-sub">Come back every day for bigger rewards</div>
    <div class="ls-days-row" id="ls-days-row"></div>
    <div class="ls-reward-box">
      <div class="ls-reward-lbl">Today's Bonus</div>
      <div class="ls-reward-amount" id="ls-reward-amount">+50 🪙</div>
    </div>
    <button class="ls-claim-btn" onclick="window.lsClaimStreak()">Claim Reward!</button>
  </div>
</div>
<div id="ls-ach-toast"></div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# JAVASCRIPT  (inserted before </body> in its own <script> block)
# ─────────────────────────────────────────────────────────────────────────────
STREAK_JS = """
<script>
/* ===== DAILY LOGIN STREAK MODULE ===== */
(function() {
  var LS_KEY = 'ls_v2';
  var DAY_COINS = [20, 30, 40, 50, 60, 80, 120];
  var MILESTONES = {3:30, 7:100, 14:150, 30:300};
  var MILESTONE_LABELS = {3:'🌟 3-Day Streak! ', 7:'🏆 One Full Week! ', 14:'💎 Two Weeks! ', 30:'👑 Legend! '};

  function getData() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{"n":0,"d":"","ach":[]}'); }
    catch(e) { return {n:0, d:'', ach:[]}; }
  }
  function setData(v) { try { localStorage.setItem(LS_KEY, JSON.stringify(v)); } catch(e) {} }

  // Grant coins using whatever pattern this game uses
  function grantCoins(n) {
    try {
      if (typeof addCoins === 'function') { addCoins(n); return; }
      var s = (typeof State !== 'undefined') ? State
            : (typeof state !== 'undefined') ? state
            : (typeof save  !== 'undefined') ? save : null;
      if (!s) return;
      s.coins = (s.coins || 0) + n;
      if (typeof State !== 'undefined' && typeof State.save === 'function') State.save();
      else if (typeof saveState === 'function') saveState();
      else if (typeof persist   === 'function') persist();
      if      (typeof updateCoinDisplays === 'function') updateCoinDisplays();
      else if (typeof updateHUD          === 'function') updateHUD();
      else if (typeof renderMenu         === 'function') renderMenu();
    } catch(e) {}
  }

  function showAchievement(txt) {
    var el = document.getElementById('ls-ach-toast');
    if (!el) return;
    el.textContent = txt;
    el.classList.add('ls-show');
    setTimeout(function() { el.classList.remove('ls-show'); }, 3500);
  }

  function renderDays(n) {
    var row = document.getElementById('ls-days-row');
    if (!row) return;
    var pos = ((n - 1) % 7) + 1; // 1–7
    var html = '';
    for (var i = 1; i <= 7; i++) {
      var past    = i < pos;
      var current = i === pos;
      var bg  = current ? '#ffd700' : past ? '#4ecdc4' : 'rgba(255,255,255,0.1)';
      var fg  = (current || past) ? '#1a1a1a' : 'rgba(255,255,255,0.35)';
      var ico = current ? '⭐' : past ? '✓' : i;
      html += '<div class="ls-day-cell">'
            + '<div class="ls-day-dot" style="background:' + bg + ';color:' + fg + '">' + ico + '</div>'
            + '<div class="ls-day-lbl">+' + DAY_COINS[i-1] + '</div>'
            + '</div>';
    }
    row.innerHTML = html;
  }

  function showOverlay(n) {
    var pos   = ((n - 1) % 7) + 1;
    var coins = DAY_COINS[pos - 1];
    var el;
    el = document.getElementById('ls-day-num');    if (el) el.textContent = n;
    el = document.getElementById('ls-reward-amount'); if (el) el.textContent = '+' + coins + ' 🪙';
    el = document.getElementById('ls-fire-icon');
    if (el) el.textContent = n >= 7 ? '🔥' : n >= 3 ? '🔥' : '✨';
    renderDays(n);
    var ov = document.getElementById('ls-overlay');
    if (ov) { ov.style.display = 'flex'; }
  }

  window.lsClaimStreak = function() {
    var data = getData();
    var pos   = ((data.n - 1) % 7) + 1;
    var coins = DAY_COINS[pos - 1];
    grantCoins(coins);
    var ov = document.getElementById('ls-overlay');
    if (ov) ov.style.display = 'none';
    // Milestone bonus
    var mil = MILESTONES[data.n];
    if (mil && data.ach.indexOf(data.n) === -1) {
      data.ach.push(data.n);
      setData(data);
      setTimeout(function() {
        grantCoins(mil);
        showAchievement(MILESTONE_LABELS[data.n] + '+' + mil + ' 🪙 bonus!');
      }, 500);
    }
    if (window.Android) try { window.Android.logEvent('login_streak_claim', 'day=' + data.n); } catch(e) {}
  };

  function run() {
    var today = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
    var data  = getData();

    // Always cancel pending notif and reschedule for ~23h from now
    if (window.Android) {
      try { window.Android.cancelNotification(); } catch(e) {}
      try { window.Android.scheduleNotification(23 * 60); } catch(e) {}
    }

    if (data.d === today) return; // already logged in today

    var yesterday = new Date(Date.now() - 86400000).toLocaleDateString('en-CA');
    data.n = (data.d === yesterday) ? data.n + 1 : 1;
    data.d = today;
    setData(data);

    showOverlay(data.n);
    if (window.Android) try { window.Android.logEvent('login_streak_show', 'day=' + data.n); } catch(e) {}
  }

  // Small delay so the game fully initialises before we show the overlay
  setTimeout(run, 900);
})();
</script>
"""


def inject_game(game):
    html_path = os.path.join(BASE, game, "android", "app", "src", "main", "assets", "game.html")
    if not os.path.exists(html_path):
        print(f"  ✗ {game}: game.html not found at {html_path}")
        return

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    if "ls_v2" in html or "lsClaimStreak" in html:
        print(f"  ✓ {game}: already has login streak — skipped")
        return

    # 1. CSS — inject before last </style>
    css_block = "<style>\n" + STREAK_CSS.strip() + "\n</style>\n"
    if "</style>" in html:
        # Find the last </style> and insert our block before </body>
        pass  # handled below

    # 2. HTML + JS — inject before </body>
    injection = STREAK_CSS_BLOCK + STREAK_HTML.strip() + "\n" + STREAK_JS.strip() + "\n"
    if "</body>" in html:
        html = html.replace("</body>", injection + "\n</body>", 1)
    else:
        html += "\n" + injection

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✓ {game}: login streak injected")


# The CSS goes in a style block, placed before </body>
STREAK_CSS_BLOCK = "<style>\n" + STREAK_CSS.strip() + "\n</style>\n"


if __name__ == "__main__":
    print("Adding login streak to all games...\n")
    for game in GAMES:
        inject_game(game)
    print("\n✅ Done — login streak added to all games")
