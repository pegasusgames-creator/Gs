#!/usr/bin/env python3
"""mark_shell_regions.py — label the per-game regions of a family game shell.

The family shell (Afterimage's game.html, ~500 KB) is mostly shared code:
menus, shop, IAP, lives, settings, overlays, i18n and the growth shims. A
builder replacing the game only needs the handful of regions that hold the
game itself. This script wraps each of them in a named marker pair so a
builder can read and replace one region without loading the whole file:

    CSS   /*@@REGION NAME*/ ... /*@@END NAME*/
    HTML  <!--@@REGION NAME--> ... <!--@@END NAME-->
    JS    //@@REGION NAME ... //@@END NAME

  PALETTE       :root Daylight tokens + body.midnight tokens (game colours)
  BOARD_CSS     board / pieces / controls styling
  IDENTITY_CSS  menu identity (--m-* tokens, motif)
  MENU_TITLE    menu wordmark + tagline
  BOARD_HTML    the in-game board zone (HUD chips, board, controls)
  FOOTER        in-game footer buttons
  TUTORIAL_HTML first-launch coachmark card
  ROLES         PIPE_COLORS: palette role -> CSS var (themes assign into it)
  SHOP          VALID_PRODUCTS / VALID_REWARD_TYPES / SHOP_PRODUCTS
  LEVELS        level data (CAMPAIGN / LEVELS) + difficulty bands
  CHAPTERS      Level Select chapter names
  ENGINE        the whole game engine (generator, board, input, win, hint,
                daily, endless, tutorial)
  STATS         Stats-screen cards
  THEMES        theme list (palette keys = ROLES keys)
  EVENT_THEME   coin-sink event theme palette

It also applies two shell fixes every builder needs:
  * theme palettes are applied for every key of PIPE_COLORS (was a
    hard-coded ['you','echo','plate','exit'] list);
  * a shared spendLife() helper for games with a fail state.

Idempotent. docs/GAME_SHELL.md is the contract for each region.

Usage:
    python3 scripts/mark_shell_regions.py App [App ...] [--check]
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

CSS, HTML, JS = "css", "html", "js"

# (name, style, start anchor, end anchor, end mode)
#   end mode "incl": region ends after the line holding the end anchor
#   end mode "excl": region ends before the line holding the end anchor
REGIONS = [
    ("PALETTE", CSS, ":root{\n  /* Daylight = light blueprint paper", "  --accent:#37e0e0;\n}", "incl"),
    ("BOARD_CSS", CSS, "/* ── Afterimage board ─", "/* ============ 2026-06-10 round-1: adaptive sizing via clamp() ============ */", "excl"),
    ("IDENTITY_CSS", CSS, "/* PART6: faint board-grid motif", "</style>", "excl"),
    ("MENU_TITLE", HTML, '  <div class="menu-logo">', '  <div class="menu-sub">', "incl"),
    ("BOARD_HTML", HTML, '  <div class="board-zone">', '  <div class="game-footer">', "excl"),
    ("FOOTER", HTML, '  <div class="game-footer">', '  <div id="tutorialOverlay"', "excl"),
    ("TUTORIAL_HTML", HTML, '  <div id="tutorialOverlay"', "\n</div>\n\n<!-- LEVEL SELECT -->", "excl"),
    ("ROLES", JS, "const PIPE_COLORS = {", "\n};", "incl"),
    ("SHOP", JS, "const VALID_PRODUCTS = new Set([", "  {id:'unlimited_lives_forever'", "incl2"),
    ("LEVELS", JS, "// LEVELS (", "const BANDS=", "incl"),
    ("CHAPTERS", JS, "  const _NAMES=[", "  const _NAMES=[", "incl"),
    ("ENGINE", JS, "// GAME ENGINE", "window.replayTutorial=", "incl"),
    ("STATS", JS, "  var stats=[\n    {icon:'🎯',label:'Levels Synced'", "\n  ];", "incl"),
    ("THEMES", JS, "  var THEMES=[", "\n  ];", "incl"),
    ("EVENT_THEME", JS, "    colors:['#ff4444','#ff8800','#ffdd00','#2ea043','#cc2200'], palette:", "    colors:['#ff4444','#ff8800','#ffdd00','#2ea043','#cc2200'], palette:", "incl"),
]

# Old fixed Level Select sections (pre-2026-10-15 shells) -> chapters of 50.
OLD_SECTIONS = re.compile(
    r"  const sections=\[\n    \{label:'Echo Basics — 1–20',range:\[0,20\]\},\n.*?\n  \];\n", re.S)
NEW_SECTIONS = """  // Chapters of 50 covering EVERY level (the old fixed list stopped at 60 of 500).
  const _N=(typeof LEVELS!=='undefined'?LEVELS:CAMPAIGN).length,_CH=50;
  const _NAMES=['Chapter 1','Chapter 2','Chapter 3','Chapter 4','Chapter 5','Chapter 6','Chapter 7','Chapter 8','Chapter 9','Chapter 10'];
  const sections=[];
  for(let s=0;s<_N;s+=_CH){const e=Math.min(_N,s+_CH);sections.push({label:(_NAMES[s/_CH]||('Chapter '+(s/_CH+1)))+' — '+(s+1)+'–'+e,range:[s,e]});}
"""

ROLE_LOOP = "['you','echo','plate','exit'].forEach("
ROLE_LOOP_NEW = "Object.keys(PIPE_COLORS).forEach("

SPEND_ANCHOR = """function addLives(n){
  save.lives=Math.min(save.maxLives,save.lives+n);
  save.lastLifeTime=Date.now();
  persist();
}
"""
SPEND_LIFE = """// Fail-state games call spendLife() when a run is lost. Returns false (and
// opens the no-lives sheet) when the player is out of lives; unlimited-lives
// holders never spend one. Pure puzzles with undo/reset never call it.
function spendLife(){
  regenLives();
  if(hasUnlimitedLives())return true;
  if(save.lives<=0){showOverlay('overlay-nolives');return false;}
  if(save.lives>=save.maxLives)save.lastLifeTime=Date.now();
  save.lives--;persist();updateAllUI();
  try{if(window.gScheduleLivesRefilled)window.gScheduleLivesRefilled(save.lastLifeTime+(save.maxLives-save.lives)*30*60*1000);}catch(e){}
  return true;
}
"""


def markers(name: str, style: str):
    if style == CSS:
        return f"/*@@REGION {name}*/\n", f"/*@@END {name}*/\n"
    if style == HTML:
        return f"<!--@@REGION {name}-->\n", f"<!--@@END {name}-->\n"
    return f"//@@REGION {name}\n", f"//@@END {name}\n"


def line_start(s: str, i: int) -> int:
    return s.rfind("\n", 0, i) + 1


def line_end(s: str, i: int) -> int:
    j = s.find("\n", i)
    return len(s) if j < 0 else j + 1


def mark(s: str, app: str):
    missing = []
    if "function spendLife(" not in s and SPEND_ANCHOR in s:
        s = s.replace(SPEND_ANCHOR, SPEND_ANCHOR + SPEND_LIFE, 1)
    s = s.replace(ROLE_LOOP, ROLE_LOOP_NEW)
    s = OLD_SECTIONS.sub(NEW_SECTIONS, s, count=1)
    for name, style, start, end, mode in REGIONS:
        a, b = markers(name, style)
        if a in s:
            continue
        i = s.find(start)
        if i < 0:
            missing.append(name)
            continue
        i0 = line_start(s, i)
        if start.startswith("\n"):
            i0 = i + 1
        if mode == "incl2":
            # SHOP: through the end of the SHOP_PRODUCTS array that follows.
            j = s.find(end, i)
            j = s.find("\n];", j) if j >= 0 else -1
            if j < 0:
                missing.append(name)
                continue
            j1 = line_end(s, j + 1)
        else:
            j = s.find(end, i + (0 if start == end else len(start)))
            if j < 0:
                missing.append(name)
                continue
            if mode == "incl":
                j1 = line_end(s, j + len(end) - 1)
            else:
                j1 = line_start(s, j + 1 if end.startswith("\n") else j)
        s = s[:i0] + a + s[i0:j1] + b + s[j1:]
    return s, missing


def main() -> int:
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    check = "--check" in sys.argv
    if not args:
        print(__doc__)
        return 2
    rc = 0
    for app in args:
        p = BASE / app / "android/app/src/main/assets/game.html"
        if not p.exists():
            print(f"  ? {app}: no game.html")
            rc = 1
            continue
        s = p.read_text(encoding="utf-8")
        out, missing = mark(s, app)
        n = len(re.findall(r"@@REGION [A-Z_]+", out))
        if missing:
            print(f"  ! {app}: anchors not found for {', '.join(missing)}")
        if out != s and not check:
            p.write_text(out, encoding="utf-8")
        print(f"  {app}: {n} regions marked{' (would change)' if check and out != s else ''}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
