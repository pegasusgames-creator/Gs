#!/usr/bin/env node
// Behavioural tests for the shared growth stack (CORE / A / B / D / E / F / G
// / MENU / EVENTS) in the 8 shipping + finished games. Drives each game's
// REAL win path in headless Chromium with a mocked Android bridge and asserts
// the promised behaviour actually happens. Exit 1 on any failure.
//
//   node scripts/runtime/growth_behaviour.js [App ...]
//
// Why: on 2026-10-03 every one of these features was present (static gates
// green) yet inert at runtime — shims probed save keys no game uses. Run
// this after touching any growth shim, a game's win path, or GROWTH_CFG.
const path = require('path'), fs = require('fs'), os = require('os');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(__dirname, 'mock_bridge.js'), 'utf8');

// Each game's real win path. WaterSort's lives in a private closure, so the
// test loads a temp copy that exposes it (production code is untouched).
const WIN = {
  WaterSortPuzzle: `(()=>{ Game.loadLevel(0); window.__t_showLevelComplete(); })()`,
  Nonogram: `(()=>{ startLevel(1); winPuzzle(); })()`,
  Puzzle2048: `(()=>{ Game.startNewGame(); State.grid=[[64,64,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,2]]; Game.doMove('left'); })()`,
  UnblockPuzzle: `(()=>{ startLevel(0); moveCount=3; triggerWin(); })()`,
  PipeConnect: `(()=>{ loadLevel(0); isLevelComplete=()=>true; allCellsFilled=()=>true; levelStarted=true; checkLevelComplete(); })()`,
  Afterimage: `(()=>{ loadLevel(0); gMoves=L.par; winLevel(); })()`,
  Hunch: `(()=>{ loadLevel(0); gTests=2; winLevel(); })()`,
  Overlay: `(()=>{ loadLevel(0); gMoves=L.lower; winLevel(); })()`,
};
function gameUrl(app) {
  const f = path.join(REPO, app, 'android/app/src/main/assets/game.html');
  if (app !== 'WaterSortPuzzle') return 'file://' + f;
  const src = fs.readFileSync(f, 'utf8').replace('function showLevelComplete() {',
    'window.__t_showLevelComplete = function(){ return showLevelComplete(); };\nfunction showLevelComplete() {');
  const tmp = path.join(os.tmpdir(), 'ws_test_game.html'); fs.writeFileSync(tmp, src); return 'file://' + tmp;
}
async function dismiss(p) {
  for (let k = 0; k < 6; k++) {
    const hit = await p.evaluate(() => {
      const inFixed = el => { for (let a = el; a && a !== document.body; a = a.parentElement) if (getComputedStyle(a).position === 'fixed') return true; return false; };
      const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && +s.opacity > 0.05; };
      const re = /^(close|later|not now|maybe later|skip|got it|ok|claim.*|collect.*|let's go!?|next →|keep current)!?$/i;
      const c = [...document.querySelectorAll('button,[onclick]')].filter(e => vis(e) && inFixed(e) && re.test((e.innerText || '').trim()));
      if (!c.length) return null; const r = c[0].getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    });
    if (!hit) break;
    await p.mouse.click(hit.x, hit.y); await p.waitForTimeout(450);
  }
}
async function open(browser, app, { pre = '', mockRet = {} } = {}) {
  const ctx = await browser.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(`window.__mockRet=${JSON.stringify(mockRet)};`);
  await ctx.addInitScript(mock);
  await ctx.addInitScript(`if(!sessionStorage.getItem('__pre')){sessionStorage.setItem('__pre','1');localStorage.setItem('tutorialDone','1');${pre}}`);
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message.slice(0, 160)));
  await p.goto(gameUrl(app)); await p.waitForTimeout(2600); await dismiss(p);
  return { ctx, p, errs };
}
(async () => {
  const browser = await chromium.launch();
  const apps = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(WIN);
  let failures = 0;
  const check = (app, name, ok, detail) => { if (!ok) failures++; console.log(`  ${ok ? '✓' : '✗'} ${app}: ${name}${ok ? '' : ' — ' + detail}`); };
  for (const app of apps) {
    // 1. first win → notification pre-prompt → permission request; PGS submit; clear counted; event tokens
    let { ctx, p, errs } = await open(browser, app, { mockRet: { hasNotificationPermission: false } });
    const before = await p.evaluate(() => ({ pts: window.gEvents ? gEvents.points() : -1 }));
    await p.evaluate(() => { window.__calls.length = 0; });
    try { await p.evaluate(WIN[app]); } catch (e) { errs.push('win path: ' + e.message.slice(0, 120)); }
    await p.waitForTimeout(3300);
    const ok = await p.$('[data-growth-card] [data-card-ok]');
    if (ok) { try { await ok.click({ timeout: 3000 }); } catch (e) {} await p.waitForTimeout(300); }
    const calls = await p.evaluate(() => window.__calls.map(c => c[0]));
    const after = await p.evaluate(() => ({ total: gGame.totalClears(), pts: window.gEvents ? gEvents.points() : -1 }));
    check(app, 'win reaches the clear bus', after.total >= 1, `totalClears=${after.total}`);
    check(app, 'notification permission requested after first win', calls.includes('requestNotificationPermission'), 'no requestNotificationPermission');
    check(app, 'Play Games score submitted', calls.includes('submitScore'), 'no submitScore');
    check(app, 'no interstitial during the first 3 clears', !calls.includes('showInterstitial'), 'showInterstitial called');
    check(app, 'event tokens earned', after.pts > before.pts, `points ${before.pts} → ${after.pts}`);
    check(app, 'no page errors', errs.length === 0, errs.join(' | '));
    await ctx.close();
    // 2. Day-7 win-back pays exactly 100, a 2-day gap pays nothing
    const coinsAfter = async (pre) => { const o = await open(browser, app, { pre }); await dismiss(o.p); const c = await o.p.evaluate(() => gGame.coins()); await o.ctx.close(); return c; };
    const base = await coinsAfter('');
    const wb = await coinsAfter(`localStorage.setItem('_gLastSeenAt', String(Date.now()-8*86400000));`);
    const short = await coinsAfter(`localStorage.setItem('_gLastSeenAt', String(Date.now()-2*86400000));`);
    check(app, 'Day-7 win-back pays +100 once', wb - base === 100, `delta ${wb - base}`);
    check(app, 'short absence pays nothing', short - base === 0, `delta ${short - base}`);
    // 3. ad-free pass: no interstitial for a Season Pass holder
    ({ ctx, p } = await open(browser, app, { pre: `localStorage.setItem('_growthClearsTotal','10');` }));
    const adCalls = await p.evaluate(() => {
      const s = gGame.state(); s.removeAds = false; s.seasonPassUntil = Date.now() + 864e5; window.__calls.length = 0;
      ['safeShowInterstitial', 'showInterstitial'].forEach(f => { try { if (typeof window[f] === 'function') window[f](); } catch (e) {} });
      return window.__calls.filter(c => c[0] === 'showInterstitial').length;
    });
    check(app, 'Season Pass holder gets no interstitial', adCalls === 0, `${adCalls} interstitial call(s)`);
    await ctx.close();
  }
  await browser.close();
  console.log(failures ? `growth behaviour: ${failures} failure(s)` : 'growth behaviour: OK');
  process.exit(failures ? 1 : 0);
})();
