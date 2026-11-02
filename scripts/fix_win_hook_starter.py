#!/usr/bin/env python3
"""fix_win_hook_starter.py — two retention-addendum fixes (2026-11-02).

1. hookWinOverlay() only treated a win overlay as open when it had class
   `active` or an inline display. The family game shell opens its win overlay
   with class `show`, so onLevelWin() never ran there: no session streak
   bonus, no Weekly Challenge progress (Afterimage, Hunch, Overlay,
   PipeConnect and every game built on that shell). `show` now counts.
2. maybeShowStarter() opened the Starter Pack modal 0.8 s after the 5th win
   — on top of the Level Complete overlay (CLAUDE.md popup choreography:
   popups queue, never stack). It now waits until the player is back on the
   menu with no overlay open, then goes through window.gPopupQueue.

A game that opens its win card with `show` on EVERY run but only counts some
runs as wins (FlappyWings: goal flights flash display:flex) takes
--starter-only so the hook keeps its own trigger.

Idempotent. Usage: python3 scripts/fix_win_hook_starter.py [--dry-run] [--starter-only] App ...
(no apps = every app whose game.html carries the retention addendum)
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

A1 = "var active=el.classList.contains('active')||el.style.display==='flex'||el.style.display==='block';"
B1 = "var active=el.classList.contains('active')||el.classList.contains('show')||el.style.display==='flex'||el.style.display==='block';"

A2 = "  setTimeout(function(){ var m=document.getElementById('starterPackModal'); if(m) m.style.display='flex'; },800);\n"
B2 = """  // Popup choreography: never over the win overlay or mid-level. Wait until
  // the player is back on the menu with nothing open, then queue it.
  var _spShow=function(){ var m=document.getElementById('starterPackModal'); if(m) m.style.display='flex'; };
  var _spWait=setInterval(function(){
    var menu=document.getElementById('menuScreen')||document.getElementById('screen-menu');
    if(!menu||!menu.classList.contains('active')) return;
    var open=[].some.call(document.querySelectorAll('.overlay.show,.overlay.active,[id*="verlay"].active,[id*="verlay"].show,.modal.show,.modal.active'),function(o){ return getComputedStyle(o).display!=='none'; });
    if(open) return;
    clearInterval(_spWait);
    if(window.gPopupQueue&&window.gPopupQueue.enqueueWithSelector) window.gPopupQueue.enqueueWithSelector('#starterPackModal',_spShow); else _spShow();
  },700);
"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    starter_only = "--starter-only" in sys.argv
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(p.relative_to(BASE).parts[0] for p in
                      BASE.glob("*/android/app/src/main/assets/game.html")
                      if "function hookWinOverlay" in p.read_text(encoding="utf-8", errors="replace"))
    for app in apps:
        p = BASE / app / "android/app/src/main/assets/game.html"
        s = p.read_text(encoding="utf-8")
        o = s
        if not starter_only:
            s = s.replace(A1, B1)
        if A2 in s and "_spWait" not in s:
            s = s.replace(A2, B2, 1)
        changed = s != o
        print(f"  {'would patch' if dry and changed else 'patched' if changed else 'ok'} {app}"
              f"  (hook {'show-aware' if B1 in s else 'n/a'}, starter {'queued' if '_spWait' in s else 'n/a'})")
        if changed and not dry:
            p.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
