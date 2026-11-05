#!/usr/bin/env node
// playtest.js — drive Word Search headlessly with REAL input events.
//   node WordSearch/test/playtest.js <outDir> [width height]
// Plays level 1 by mouse drags (one tap-tap, one reversed drag, one miss),
// level 2 with a hint + restart, a hidden-message level, a 15×15 level by
// touch drags, the Daily and an Endless grid, Level Select, every theme and
// Midnight. Screenshots go to <outDir>; exits 1 on any page error or check.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const out = process.argv[2] || '/tmp/ws_play';
const W = +(process.argv[3] || 360), H = +(process.argv[4] || 800);
fs.mkdirSync(out, { recursive: true });
const fails = [];
const ok = (c, m) => { if (!c) { fails.push(m); console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); };

async function dismiss(p) {
  for (let k = 0; k < 6; k++) {
    const close = await p.$('#xEventsSheet [data-ev-close]');
    if (close && await close.isVisible()) { await close.click().catch(() => {}); await p.waitForTimeout(400); continue; }
    const card = await p.$('[data-growth-card] [data-card-ok]');
    if (card && await card.isVisible()) { await card.click().catch(() => {}); await p.waitForTimeout(400); continue; }
    const hit = await p.evaluate(() => {
      const inFixed = el => { for (let a = el; a && a !== document.body; a = a.parentElement) if (getComputedStyle(a).position === 'fixed') return true; return false; };
      const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && +s.opacity > 0.05; };
      const re = /^(close|later|not now|maybe later|skip|got it|ok|claim.*|collect.*|let's go!?|next →|keep current|no thanks)!?$/i;
      const c = [...document.querySelectorAll('button,[onclick]')].filter(e => vis(e) && inFixed(e) && re.test((e.innerText || '').trim()));
      if (!c.length) return null; const r = c[0].getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    });
    if (!hit) break;
    await p.mouse.click(hit.x, hit.y); await p.waitForTimeout(450);
  }
}
const centers = (p, cells) => p.evaluate(cs => {
  const r = document.getElementById('board').getBoundingClientRect(), n = L.n, s = r.width / n;
  return cs.map(i => ({ x: r.left + (i % n + 0.5) * s, y: r.top + (Math.floor(i / n) + 0.5) * s }));
}, cells);
async function drag(p, a, b, steps = 10) {
  await p.mouse.move(a.x, a.y); await p.mouse.down();
  for (let k = 1; k <= steps; k++) await p.mouse.move(a.x + (b.x - a.x) * k / steps + (k % 2 ? 2 : -2), a.y + (b.y - a.y) * k / steps + (k % 3 ? 1.5 : -1.5));
  await p.mouse.up(); await p.waitForTimeout(140);
}
async function touchDrag(p, cdp, a, b, steps = 8) {
  const pt = q => [{ x: q.x, y: q.y, id: 1 }];
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: pt(a) });
  for (let k = 1; k <= steps; k++) await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: pt({ x: a.x + (b.x - a.x) * k / steps, y: a.y + (b.y - a.y) * k / steps }) });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(140);
}
const words = p => p.evaluate(() => L.words.map(w => ({ w: w.w, cells: w.cells, found: w.found })));
async function solveAll(p, mode, cdp) {
  for (const w of await words(p)) {
    if (w.found) continue;
    const [a, b] = await centers(p, [w.cells[0], w.cells[w.cells.length - 1]]);
    if (mode === 'touch') await touchDrag(p, cdp, a, b); else await drag(p, a, b);
  }
  return (await words(p)).every(w => w.found);
}
const shot = (p, name) => p.screenshot({ path: path.join(out, name + '.png') });

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(mock);
  await ctx.route(/^https?:/, r => r.abort());
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message.slice(0, 200)));
  const cdp = await ctx.newCDPSession(p);
  await p.goto('file://' + path.join(REPO, 'WordSearch/android/app/src/main/assets/game.html'));
  await p.waitForTimeout(2600); await dismiss(p);
  await shot(p, '00_menu');
  // ── Play → level 1 + coachmark ──
  await p.click('#screen-menu .menu-primary, #screen-menu #menuPlayBtn, #screen-menu .btn-play', { timeout: 4000 }).catch(() => p.evaluate(() => startGame()));
  await p.waitForTimeout(900); await dismiss(p);
  ok(await p.evaluate(() => document.getElementById('screen-game').classList.contains('active') && L && L.n === 6), 'Play opens level 1 (6×6)');
  ok(await p.evaluate(() => document.getElementById('tutorialOverlay').style.display === 'flex'), 'coachmark shows on level 1');
  await shot(p, '01_level1_tutorial');
  for (let k = 0; k < 3; k++) { await p.click('#tutorialOverlay > div'); await p.waitForTimeout(200); }
  ok(await p.evaluate(() => localStorage.getItem('ws_tutorialDone') === '1'), 'coachmark completes after 3 taps');
  const t0 = Date.now();
  let ws = await words(p);
  // tap-tap the first word
  let [a, b] = await centers(p, [ws[0].cells[0], ws[0].cells[ws[0].cells.length - 1]]);
  await p.mouse.click(a.x, a.y); await p.waitForTimeout(120); await p.mouse.click(b.x, b.y); await p.waitForTimeout(200);
  ok((await words(p))[0].found, 'tap first + tap last finds ' + ws[0].w);
  // reversed drag on the second word
  [a, b] = await centers(p, [ws[1].cells[ws[1].cells.length - 1], ws[1].cells[0]]);
  await drag(p, a, b);
  ok((await words(p))[1].found, 'reversed drag finds ' + ws[1].w);
  // a deliberate miss (row of the board's first two letters if they are no word)
  const before = (await words(p)).filter(w => w.found).length;
  [a, b] = await centers(p, [0, 1]);
  await drag(p, a, b, 4);
  ok((await words(p)).filter(w => w.found).length === before, 'a non-word selection finds nothing');
  // drag the rest, screenshot half way
  ws = await words(p);
  let half = 0;
  for (const w of ws) {
    if (w.found) continue;
    const [x, y] = await centers(p, [w.cells[0], w.cells[w.cells.length - 1]]);
    await drag(p, x, y);
    if (++half === 3) await shot(p, '02_level1_midplay');
  }
  await p.waitForTimeout(1300);
  ok(await p.evaluate(() => document.getElementById('overlay-complete').classList.contains('show')), 'level 1 win overlay (' + ((Date.now() - t0) / 1000).toFixed(1) + 's of input)');
  console.log('    ' + await p.evaluate(() => document.getElementById('complete-stars').textContent + ' ' + document.getElementById('complete-msg').textContent));
  await shot(p, '03_level1_win');
  ok(await p.evaluate(() => save.completedLevels.includes(0) && save.currentLevel === 1), 'progress saved (currentLevel 2)');
  // ── level 2: hint + restart ──
  await p.click('#overlay-complete .modal-btn.primary'); await p.waitForTimeout(700); await dismiss(p);
  await p.waitForTimeout(1500); await dismiss(p);
  ok(await p.evaluate(() => levelIndex === 1 && !gWon), 'Next opens level 2');
  const hc = await p.evaluate(() => save.hintCount);
  await p.click('.game-footer .ws-tool:nth-child(2)'); await p.waitForTimeout(400);
  ok(await p.evaluate(h => save.hintCount === h - 1 && L.words.some(w => w.hinted) && !!document.querySelector('.ws-cell.hint'), hc), 'Hint spends a hint and marks a first letter');
  ok(await p.evaluate(() => { const w = L.words.find(x => x.hinted); return document.querySelector('.ws-cell.hint').dataset.i == w.cells[0]; }), 'hint marks the CORRECT first letter');
  await shot(p, '04_level2_hint');
  [a, b] = await centers(p, (await words(p)).filter(w => !w.found)[0].cells.filter((_, i, arr) => i === 0 || i === arr.length - 1));
  await drag(p, a, b);
  await p.click('.game-footer .ws-tool:nth-child(4)'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => document.getElementById('overlay-ws-restart').classList.contains('show')), 'Restart asks first');
  await shot(p, '05_restart_confirm');
  await p.click('#overlay-ws-restart .modal-btn.primary'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => L.words.every(w => !w.found) && gTime === 0), 'Restart clears found words + timer');
  // hide-found toggle
  await drag(p, ...(await centers(p, (await words(p))[0].cells.filter((_, i, arr) => i === 0 || i === arr.length - 1))));
  await p.click('.game-footer .ws-tool:nth-child(3)'); await p.waitForTimeout(250);
  ok(await p.evaluate(() => [...document.querySelectorAll('.ws-word.found')].every(e => e.style.display === 'none')), 'Hide found hides crossed-off words');
  await p.click('.game-footer .ws-tool:nth-child(3)'); await p.waitForTimeout(200);
  // ── hidden-message level (level 30) ──
  await p.evaluate(() => { hideOverlay('overlay-complete'); loadLevel(29); }); await p.waitForTimeout(400);
  ok(await p.evaluate(() => !!L.msg), 'level 30 carries a hidden message');
  await solveAll(p, 'mouse');
  await p.waitForTimeout(500);
  ok(await p.evaluate(() => gDone && !gWon && document.getElementById('ws-msgbar').style.display !== 'none'), 'all words found → message prompt waits for a tap');
  await shot(p, '06_message_prompt');
  await p.click('#ws-msgbar'); await p.waitForTimeout(2600);
  await shot(p, '07_message_revealed');
  ok(await p.evaluate(() => gWon && document.querySelector('.ws-reveal-msg') && document.querySelector('.ws-reveal-msg').textContent.includes(L.msg)), 'message revealed + shown on the win card');
  // ── bonus word level ──
  await p.evaluate(() => { hideOverlay('overlay-complete'); loadLevel(7); }); await p.waitForTimeout(400);
  const bon = await p.evaluate(() => L.bonus && L.bonus.cells);
  ok(!!bon, 'level 8 hides a bonus word');
  const coins0 = await p.evaluate(() => save.coins);
  [a, b] = await centers(p, [bon[0], bon[bon.length - 1]]); await drag(p, a, b);
  ok(await p.evaluate(c => L.bonus.found && save.coins === c + 10, coins0), 'finding the bonus word pays +10 coins');
  await shot(p, '08_bonus_found');
  // ── late level 15×15 by TOUCH drags ──
  await p.evaluate(() => loadLevel(479)); await p.waitForTimeout(500);
  await shot(p, '09_level480_15x15');
  ok(await solveAll(p, 'touch', cdp), 'level 480 (15×15) solved by touch drags');
  await p.waitForTimeout(1200); await shot(p, '10_level480_win');
  // ── mid level 12×12 midplay ──
  await p.evaluate(() => { hideOverlay('overlay-complete'); loadLevel(311); }); await p.waitForTimeout(400);
  let cnt = 0; for (const w of await words(p)) { if (cnt++ >= 6) break; const [x, y] = await centers(p, [w.cells[0], w.cells[w.cells.length - 1]]); await drag(p, x, y); }
  await shot(p, '11_level312_midplay');
  // ── Daily ──
  await p.evaluate(() => { hideOverlay('overlay-complete'); goMenu(); }); await p.waitForTimeout(500); await dismiss(p);
  await p.evaluate(() => { const b = document.getElementById('dailyChallengeBtn'); b.scrollIntoView(); });
  await p.click('#dailyChallengeBtn').catch(() => p.evaluate(() => startDailyChallenge()));
  await p.waitForTimeout(700); await dismiss(p);
  ok(await p.evaluate(() => isDailyChallenge && L && L.mode === 'daily'), 'Daily opens');
  await shot(p, '12_daily');
  ok(await solveAll(p, 'mouse'), 'Daily solved');
  await p.waitForTimeout(1300);
  ok(await p.evaluate(() => save.dailyChallengeDate === new Date().toISOString().split('T')[0]), 'Daily records today');
  await p.evaluate(() => hideOverlay('overlay-complete'));
  // ── Level Select + Endless ──
  await p.evaluate(() => showLevelSelect()); await p.waitForTimeout(400);
  await shot(p, '13_levelselect');
  const lives0 = await p.evaluate(() => save.lives);
  await p.evaluate(() => { const s = document.getElementById('ls-scroll'); s.scrollTop = s.scrollHeight; }); await p.waitForTimeout(200);
  await p.click('#ls-scroll button.ls-bubble'); await p.waitForTimeout(700);
  ok(await p.evaluate(l => isEndless && L && L.n >= 10 && save.lives === l - 1, lives0), 'Endless grid opens and costs one life');
  await shot(p, '14_endless');
  // ── Themes: unlock + apply each, board recolours ──
  await p.evaluate(() => { save.completedLevels = Array.from({ length: 300 }, (_, i) => i); save.coins = 5000; persist(); hideOverlay('overlay-complete'); loadLevel(150); });
  await p.waitForTimeout(400); await dismiss(p);
  { let c = 0; for (const w of await words(p)) { if (c++ >= 5) break; const [x, y] = await centers(p, [w.cells[0], w.cells[w.cells.length - 1]]); await drag(p, x, y); } }
  const boards = [];
  const ids = await p.evaluate(() => window._THEMES_META.map(t => t.id));
  for (const id of ids) {
    await dismiss(p); await p.evaluate(() => showScreen('themes')); await p.waitForTimeout(250);
    const i = ids.indexOf(id);
    await p.click('#themesGrid .theme-card >> nth=' + i); await p.waitForTimeout(250);
    await p.evaluate(() => showScreen('game')); await p.waitForTimeout(300);
    const cs = await p.evaluate(() => { const s = getComputedStyle(document.getElementById('board')); return s.backgroundColor + '|' + getComputedStyle(document.querySelector('.ws-cell')).color; });
    boards.push(cs);
    await shot(p, '15_theme_' + id);
  }
  ok(new Set(boards).size === ids.length, 'every theme recolours the board (' + new Set(boards).size + '/' + ids.length + ' distinct)');
  await p.evaluate(() => showScreen('themes')); await p.waitForTimeout(250); await shot(p, '16_themes_screen');
  await p.evaluate(() => goMenu()); await p.waitForTimeout(400); await dismiss(p); await shot(p, '17_menu_midnight');
  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.join(' | ') : ''));
  await browser.close();
  console.log(fails.length ? '✗ ' + fails.length + ' check(s) failed' : '✓ playtest passed');
  process.exit(fails.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
