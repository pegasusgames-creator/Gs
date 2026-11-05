#!/usr/bin/env node
// verify_runtime_boards.js — Daily + Endless grids are built on-device by
// wsGen(). This loads game.html headlessly, builds the Daily for 400
// consecutive days and 300 Endless grids (every size 10-13, random themes),
// dumps them, and hands them to the content gate's --boards mode, which
// re-checks each with the SAME rules as the campaign (every listed word and
// the bonus word exactly once on a straight line, no blocklisted word in any
// direction, words from the board's theme list, band directions).
//   node WordSearch/test/verify_runtime_boards.js
const path = require('path'), fs = require('fs'), { execFileSync } = require('child_process');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 412, height: 915 } });
  await ctx.addInitScript(mock); await ctx.route(/^https?:/, r => r.abort());
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.join(REPO, 'WordSearch/android/app/src/main/assets/game.html')); await p.waitForTimeout(1500);
  const boards = await p.evaluate(() => {
    const B36 = WS_B36, out = [];
    const enc = (w, n) => { const a = w.cells[0], b = w.cells[1] - a; const d = WS_D.findIndex(v => v[0] * n + v[1] === b); return w.w + B36[Math.floor(a / n)] + B36[a % n] + d; };
    const pack = (D, label, dirs) => ({ label, n: D.n, grid: D.grid.join(''), words: D.words.map(w => enc(w, D.n)), bonus: D.bonus ? enc(D.bonus, D.n) : '', theme: WS_THEMES[D.ti].w, dirs });
    const t0 = dayNum(); let fails = 0;
    for (let k = 0; k < 400; k++) { const d = t0 + k, s = wsDailySpec(d), D = genDaily(d); if (!D) { fails++; continue; } out.push(pack(D, 'daily ' + d, s.dirs)); }
    for (let k = 0; k < 300; k++) { const n = 10 + (k % 4), ti = (k * 7) % WS_THEMES.length, r = WS_WORDS_FOR[n];
      const D = wsGen(1000 + k * 7919, ti, n, Math.round((r[0] + r[1]) / 2), WS_ALL_DIRS, 4, Math.min(n, 12), k % 2 === 0);
      if (!D) { fails++; continue; } out.push(pack(D, 'endless ' + k, WS_ALL_DIRS)); }
    return { out, fails };
  });
  await browser.close();
  const f = path.join(require('os').tmpdir(), 'ws_runtime_boards.json');
  fs.writeFileSync(f, JSON.stringify(boards.out));
  console.log('built ' + boards.out.length + ' runtime boards, ' + boards.fails + ' generator failures, ' + errs.length + ' page errors');
  let rc = 0;
  try { process.stdout.write(execFileSync('python3', [path.join(REPO, 'scripts/check_wordsearch_valid.py'), '--boards', f]).toString()); } catch (e) { process.stdout.write(String(e.stdout || '')); rc = 1; }
  process.exit(rc || boards.fails || errs.length ? 1 : 0);
})();
