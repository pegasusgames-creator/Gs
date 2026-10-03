#!/usr/bin/env node
// Runtime smoke test: load every app's game.html in mobile-viewport headless
// Chromium with a mocked Android bridge and report any page error thrown on
// launch. Exit 1 if a non-blocked app throws.
//
//   node scripts/runtime/smoke_all.js [App ...]
//
// Needs Playwright + Chromium (npm i -D playwright; npx playwright install
// chromium). Found 2026-10-03: 23 apps threw on load (e.g. `var history`
// colliding with window.history), none caught by the static gates.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(__dirname, 'mock_bridge.js'), 'utf8');
const pp = fs.readFileSync(path.join(REPO, 'scripts', 'pre_publish_check.py'), 'utf8');
const blocked = new Set((pp.match(/BLOCKED_APPS = \{([\s\S]*?)\}/) || ['', ''])[1].match(/"([A-Za-z0-9]+)"/g)?.map(s => s.slice(1, -1)) || []);
const SKIP = new Set(['_template', '_release', 'docs', 'scripts', '_screenshot_tools']);
const apps = process.argv.slice(2).length ? process.argv.slice(2)
  : fs.readdirSync(REPO).filter(d => !SKIP.has(d) && !d.startsWith('.') && fs.existsSync(path.join(REPO, d, 'android/app/src/main/assets/game.html'))).sort();
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  for (const app of apps) {
    const ctx = await browser.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true });
    await ctx.addInitScript(mock);
    await ctx.route(/^https?:/, r => r.abort());   // offline, like the listings promise
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(String(e.message).slice(0, 160)));
    try { await page.goto('file://' + path.join(REPO, app, 'android/app/src/main/assets/game.html'), { timeout: 15000 }); } catch (e) { errs.push('load: ' + e.message.slice(0, 120)); }
    await page.waitForTimeout(2200);
    const uniq = [...new Set(errs)];
    if (uniq.length) {
      const tag = blocked.has(app) ? 'BLOCKED' : 'FAIL';
      if (!blocked.has(app)) failed++;
      console.log(`  ${tag === 'FAIL' ? '✗' : '-'} ${app}: ${uniq.slice(0, 2).join(' | ')}${tag === 'BLOCKED' ? ' (blocked placeholder)' : ''}`);
    }
    await ctx.close();
  }
  await browser.close();
  console.log(failed ? `runtime smoke: ${failed} app(s) throw on launch` : `runtime smoke: OK (${apps.length} apps)`);
  process.exit(failed ? 1 : 0);
})();
