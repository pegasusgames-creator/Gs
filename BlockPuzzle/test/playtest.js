#!/usr/bin/env node
// Headless play test with REAL touch input (CDP touch events → pointer
// events, pointerType 'touch', so the lifted-ghost offset path runs).
//   node BlockPuzzle/test/playtest.js [outDir] [WxH]
// Plays the tutorial board, then lets the in-game bot choose moves and
// performs each one as a finger drag; screenshots key moments.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const out = process.argv[2] || path.join(require('os').tmpdir(), 'bp_play');
const [W, H] = (process.argv[3] || '360x800').split('x').map(Number);
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(mock);
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
  await p.goto('file://' + path.join(REPO, 'BlockPuzzle/android/app/src/main/assets/game.html'));
  await p.waitForTimeout(2500);
  const cdp = await ctx.newCDPSession(p);
  const touch = async (type, x, y) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y }] });
  // dismiss first-launch popups the way a player would
  for (let k = 0; k < 6; k++) {
    const hit = await p.evaluate(() => {
      const re = /^(close|later|not now|maybe later|skip|got it|ok|claim.*|collect.*|let's go!?|keep current)!?$/i;
      const c = [...document.querySelectorAll('button')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 2 && getComputedStyle(e).visibility !== 'hidden' && re.test((e.innerText || '').trim()); });
      if (!c.length) return null; const r = c[0].getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    });
    if (!hit) break; await p.mouse.click(hit.x, hit.y); await p.waitForTimeout(400);
  }
  await p.screenshot({ path: path.join(out, '01_menu.png') });
  // tap PLAY
  const play = await p.evaluate(() => { const b = document.querySelector('#screen-menu .menu-primary'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; });
  await p.mouse.click(play.x, play.y); await p.waitForTimeout(900);
  await p.screenshot({ path: path.join(out, '02_tutorial.png') });
  // advance the 3 coachmarks by tapping the card
  for (let k = 0; k < 3; k++) { const c = await p.$('#tutorialOverlay > div'); if (c && await c.isVisible()) { await c.click(); await p.waitForTimeout(250); } }
  // drag helper: finger path that lands the ghost's top-left on (r,c)
  async function dragMove(mv, shotMid) {
    const g = await p.evaluate(m => {
      const sl = document.querySelector('.bp-slot[data-s="' + m.slot + '"]').getBoundingClientRect();
      const pc = BP_OR[bp.tray[m.slot][0]][bp.tray[m.slot][1]]; let h = 0, w = 0; for (const q of pc) { h = Math.max(h, q[0] + 1); w = Math.max(w, q[1] + 1); }
      const pw = w * bpV.cell + (w - 1) * bpV.gap, ph = h * bpV.cell + (h - 1) * bpV.gap, lift = bpV.cell * 1.15 + 18;
      const o = bpBoardOrigin(), pitch = bpV.cell + bpV.gap;
      return { sx: sl.left + sl.width / 2, sy: sl.top + sl.height / 2, tx: o.x + m.c * pitch + pw / 2, ty: o.y + m.r * pitch + ph + lift };
    }, mv);
    await touch('touchStart', g.sx, g.sy);
    const steps = 8;
    for (let i = 1; i <= steps; i++) { await touch('touchMove', g.sx + (g.tx - g.sx) * i / steps, g.sy + (g.ty - g.sy) * i / steps); await p.waitForTimeout(16); }
    await p.waitForTimeout(60);
    if (shotMid) await p.screenshot({ path: path.join(out, shotMid) });
    const pv = await p.evaluate(() => document.querySelectorAll('.bp-cell.pv').length);
    await touch('touchEnd', g.tx, g.ty);
    return pv;
  }
  const s0 = await p.evaluate(() => ({ score: bp.score, filled: bpFilled(bp.board) }));
  // tutorial move: the domino into the gap of the bottom row (clears it)
  const pv1 = await dragMove({ slot: 0, r: 7, c: 6 }, '03_dragging.png');
  await p.waitForTimeout(120);
  await p.screenshot({ path: path.join(out, '04_clear_fx.png') });
  await p.waitForTimeout(900);
  const s1 = await p.evaluate(() => ({ score: bp.score, filled: bpFilled(bp.board), lines: bp.lines }));
  console.log('tutorial drop: preview cells', pv1, 'score', s0.score, '→', s1.score, 'lines', s1.lines, 'filled', s0.filled, '→', s1.filled);
  // play on with bot-chosen moves executed as finger drags
  let moves = 0, fails = 0, maxCombo = 0;
  while (moves < 60) {
    const st = await p.evaluate(() => ({ stuck: bpStuck(bp), over: bp.over, mv: bpBotMove(bp), score: bp.score, combo: bp.combo }));
    if (st.over || st.stuck || !st.mv) break;
    const before = await p.evaluate(() => bp.moves);
    await dragMove(st.mv, moves === 12 ? '05_mid_drag.png' : null);
    await p.waitForTimeout(140);
    const after = await p.evaluate(() => ({ m: bp.moves, c: bp.combo }));
    if (after.m !== before + 1) { fails++; if (fails > 3) break; } else moves++;
    maxCombo = Math.max(maxCombo, after.c);
    if (moves === 20) await p.screenshot({ path: path.join(out, '06_mid_game.png') });
  }
  await p.waitForTimeout(700);
  const s2 = await p.evaluate(() => ({ score: bp.score, moves: bp.moves, lines: bp.lines, stuck: bpStuck(bp), goal: bp.goal, best: save.bestScore }));
  console.log('played', moves, 'drags, failed drops', fails, 'maxCombo', maxCombo, JSON.stringify(s2));
  await p.screenshot({ path: path.join(out, '07_after_play.png') });
  // Continue: leave to menu, come back, board/tray/score must be identical
  const snap = await p.evaluate(() => JSON.stringify([bp.board, bp.tray, bp.score]));
  await p.evaluate(() => goMenu()); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, '08_menu_resume.png') });
  await p.evaluate(() => startGame()); await p.waitForTimeout(500);
  const snap2 = await p.evaluate(() => JSON.stringify([bp.board, bp.tray, bp.score]));
  console.log('continue restores exact run:', snap === snap2);
  // reload the page (app killed) → still identical
  await p.reload(); await p.waitForTimeout(2500);
  await p.evaluate(() => { document.querySelectorAll('#ls-overlay,#starterPackModal').forEach(e => e.style.display = 'none'); startGame(); }); await p.waitForTimeout(500);
  const snap3 = await p.evaluate(() => JSON.stringify([bp.board, bp.tray, bp.score]));
  console.log('restores after app restart:', snap === snap3);
  // Bomb: arm (free Bomb tokens) and detonate by a real tap on the board
  const bombs0 = await p.evaluate(() => save.hintCount);
  await p.evaluate(() => useHint()); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '09_bomb_armed.png') });
  const bc = await p.evaluate(() => { const s = bpBestBombSpot(); const o = bpBoardOrigin(), pitch = bpV.cell + bpV.gap; return { x: o.x + (s.c + 1) * pitch + bpV.cell / 2, y: o.y + (s.r + 1) * pitch + bpV.cell / 2, f: bpFilled(bp.board) }; });
  await touch('touchStart', bc.x, bc.y); await p.waitForTimeout(60); await touch('touchEnd', bc.x, bc.y); await p.waitForTimeout(150);
  await p.screenshot({ path: path.join(out, '10_bomb_boom.png') });
  const bf = await p.evaluate(() => ({ f: bpFilled(bp.board), armed: bp.bomb, n: save.hintCount }));
  console.log('bomb: tokens', bombs0, '→', bf.n, 'filled', bc.f, '→', bf.f, 'armed after', bf.armed);
  // Rotate via coins, then tap a piece to turn it
  await p.evaluate(() => { save.coins = 500; bpRotateBtn(); }); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '11_rotate_sheet.png') });
  await p.evaluate(() => bpBoostB()); await p.waitForTimeout(200);
  const r0 = await p.evaluate(() => { const s = bp.tray.findIndex(x => x); return { s, o: bp.tray[s] && bp.tray[s][1], coins: save.coins }; });
  const slr = await p.evaluate(s => { const r = document.querySelector('.bp-slot[data-s="' + s + '"]').getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }, r0.s);
  await touch('touchStart', slr.x, slr.y); await p.waitForTimeout(40); await touch('touchEnd', slr.x, slr.y); await p.waitForTimeout(250);
  const r1 = await p.evaluate(s => bp.tray[s] && bp.tray[s][1], r0.s);
  console.log('rotate: coins', 500, '→', r0.coins, 'orientation', r0.o, '→', r1);
  // Refresh via coins
  const t0 = await p.evaluate(() => JSON.stringify(bp.tray));
  await p.evaluate(() => { bpRefreshBtn(); bpBoostB(); }); await p.waitForTimeout(300);
  console.log('refresh changed tray:', t0 !== await p.evaluate(() => JSON.stringify(bp.tray)));
  // force a no-room state, show the revive card
  await p.evaluate(() => { for (let i = 0; i < 64; i++) bp.board[i] = ((i % 8) + Math.floor(i / 8)) % 3 === 0 ? 0 : 1 + (i % 7); bp.tray = [[14, 0], [11, 0], [13, 0]]; bpRender(); bpRenderTray(true); bpQueueStuck(10); });
  await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, '12_no_room.png') });
  const card = await p.evaluate(() => document.getElementById('bp-stuck').classList.contains('show'));
  await p.evaluate(() => { bpReviveAd(); window.onAdReward('extra_life'); }); await p.waitForTimeout(500);
  const rv = await p.evaluate(() => ({ card: document.getElementById('bp-stuck').classList.contains('show'), stuck: bpStuck(bp), adRev: bp.adRev, filled: bpFilled(bp.board) }));
  console.log('no-room card shown:', card, '→ after ad revive', JSON.stringify(rv));
  await p.screenshot({ path: path.join(out, '13_revived.png') });
  // end the run → summary overlay
  await p.evaluate(() => bpEndRun()); await p.waitForTimeout(900);
  await p.screenshot({ path: path.join(out, '14_summary.png') });
  const sum = await p.evaluate(() => ({ title: document.getElementById('complete-title').textContent, msg: document.getElementById('complete-msg').textContent, played: save.gamesPlayed, best: save.bestScore }));
  console.log('summary', JSON.stringify(sum));
  // daily
  await p.evaluate(() => { hideOverlay('overlay-complete'); startDailyChallenge(); }); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(out, '15_daily_intro.png') });
  await p.evaluate(() => launchDailyLevel()); await p.waitForTimeout(500);
  const d = await p.evaluate(() => ({ mode: bp.mode, day: bp.day, goal: bp.goal, tray: JSON.stringify(bp.tray), hdr: document.getElementById('hdr-level').textContent }));
  console.log('daily', JSON.stringify(d));
  await p.screenshot({ path: path.join(out, '16_daily.png') });
  // themes: each recolours the board
  const themes = await p.evaluate(() => { save.bestScore = 99999; save.unlockedThemes = ['midnight', 'raku']; persist(); return window._THEMES_META.map(t => t.id); });
  for (const id of themes) {
    await p.evaluate(id => { showScreen('themes'); const cards = [...document.querySelectorAll('#themesGrid .theme-card')]; const i = window._THEMES_META.findIndex(t => t.id === id); cards[i].click(); showScreen('game'); bpLayout(); bpRender(); bpRenderTray(true); }, id);
    await p.waitForTimeout(250);
    await p.screenshot({ path: path.join(out, '17_theme_' + id + '.png') });
  }
  await p.evaluate(() => showScreen('themes')); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '18_themes_screen.png') });
  await p.evaluate(() => showScreen('settings')); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '19_settings.png') });
  await p.evaluate(() => showScreen('shop') || showShop()); await p.evaluate(() => showShop()); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '20_shop.png') });
  await p.evaluate(() => showScreen('stats')); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, '21_stats.png') });
  await p.evaluate(() => showScreen('menu')); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(out, '22_menu_midnight.png') });
  console.log(errs.length ? 'PAGE ERRORS: ' + errs.join(' | ') : 'no page errors');
  await browser.close();
})();
