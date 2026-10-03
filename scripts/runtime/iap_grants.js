#!/usr/bin/env node
// IAP grant test: for every SKU in <App>/metadata/iaps.json, start from a
// fresh save, fire window.onPurchaseSuccess(sku) exactly as the Java billing
// bridge does, and assert the purchase visibly changed the live save
// (coins / lives / hints / undos / ad-free / pass / unlimited lives).
// "Tap Buy, get nothing, still charged" is the worst monetization bug class.
//
//   node scripts/runtime/iap_grants.js [App ...]
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(__dirname, 'mock_bridge.js'), 'utf8');
const APPS = ['WaterSortPuzzle', 'Nonogram', 'Puzzle2048', 'UnblockPuzzle', 'PipeConnect', 'Afterimage', 'Hunch', 'Overlay'];
// What each SKU must change (any one field moving the right way passes).
const EXPECT = {
  remove_ads: ['removeAds'],
  coins_small: ['coins'], coins_medium: ['coins'], coins_large: ['coins'], coins_mega: ['coins'],
  five_lives: ['lives', 'livesBank', 'extraLives'],
  unlimited_lives_1h: ['unlimitedLivesExpiry', 'unlimitedLivesUntil'],
  unlimited_lives_forever: ['unlimitedLivesPermanent', 'unlimitedLivesForever'],
  unlimited_undos: ['unlimitedUndo', 'unlimitedUndos'],
  hint_pack: ['hintCount', 'hintPack', 'hints', 'coins'],
  undo_pack: ['undoPack'],
  starter_pack: ['coins'],
  season_pass_monthly: ['seasonPassUntil', 'seasonPassForever'],
  weekly_pass: ['weeklyPassUntil'],
};
function snapshot() {
  const s = window.gGame ? window.gGame.state() : {};
  const out = {};
  for (const k of Object.keys(s)) { const v = s[k]; if (typeof v === 'number' || typeof v === 'boolean') out[k] = v; }
  try { out.__ls_hints = parseInt(localStorage.getItem('xHintTokens') || '0', 10); } catch (e) {}
  return out;
}
(async () => {
  const browser = await chromium.launch();
  const apps = process.argv.slice(2).length ? process.argv.slice(2) : APPS;
  let failures = 0;
  for (const app of apps) {
    const iaps = JSON.parse(fs.readFileSync(path.join(REPO, app, 'metadata/iaps.json'), 'utf8'));
    const skus = ['one_time_products', 'subscriptions'].flatMap(k => (iaps[k] || []).map(p => p.id || p.product_id || p.sku));
    for (const sku of skus) {
      const ctx = await browser.newContext({ viewport: { width: 412, height: 915 } });
      await ctx.addInitScript(mock);
      await ctx.addInitScript(`localStorage.setItem('tutorialDone','1');`);
      const p = await ctx.newPage(); const errs = [];
      p.on('pageerror', e => errs.push(e.message.slice(0, 140)));
      await p.goto('file://' + path.join(REPO, app, 'android/app/src/main/assets/game.html'));
      await p.waitForTimeout(2300);
      // Spend a life + some coins first so refills/coin grants are observable.
      await p.evaluate(() => { const s = window.gGame.state(); if (typeof s.lives === 'number') s.lives = Math.max(0, s.lives - 2); window.gGame.persist(); });
      const before = await p.evaluate(snapshot);
      let threw = null;
      try { await p.evaluate(sku => { if (typeof window.onPurchaseSuccess !== 'function') throw new Error('onPurchaseSuccess undefined'); window.onPurchaseSuccess(sku); }, sku); } catch (e) { threw = e.message.slice(0, 120); }
      await p.waitForTimeout(500);
      const after = await p.evaluate(snapshot);
      const fields = EXPECT[sku] || [];
      const moved = fields.filter(f => after[f] !== undefined && after[f] !== before[f] && (typeof after[f] === 'boolean' ? after[f] : after[f] > (before[f] || 0)));
      const ok = !threw && moved.length > 0 && errs.length === 0;
      if (!ok) failures++;
      console.log(`  ${ok ? '✓' : '✗'} ${app} ${sku}: ${ok ? moved.map(f => f + ' ' + before[f] + '→' + after[f]).join(', ') : (threw || errs[0] || 'nothing changed (' + fields.join('/') + ')')}`);
      await ctx.close();
    }
  }
  await browser.close();
  console.log(failures ? `iap grants: ${failures} failure(s)` : 'iap grants: OK');
  process.exit(failures ? 1 : 0);
})();
