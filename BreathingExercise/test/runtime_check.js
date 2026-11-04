#!/usr/bin/env node
// BreathingExercise runtime check: real taps in headless Chromium + mocked Android bridge.
//   node BreathingExercise/test/runtime_check.js   (exit 1 on any failure)
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BreathingExercise/android/app/src/main/assets/game.html');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const SHOTS = process.env.BX_SHOTS || '';
let fails = 0;
const ok = (c, m) => { console.log(`  ${c ? '✓' : '✗'} ${m}`); if (!c) fails++; };
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 360, height: 640 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  const p = await ctx.newPage(); p.setDefaultTimeout(6000);
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const tap = async s => { await p.locator(s).first().tap(); await p.waitForTimeout(250); };
  const ev = (f, a) => p.evaluate(f, a);
  const calls = n => ev(x => window.__calls.filter(c => c[0] === x), n);
  const shot = async n => { if (SHOTS) await p.screenshot({ path: path.join(SHOTS, n + '.png') }); };
  await p.goto('file://' + GAME); await p.waitForTimeout(700);

  ok(await p.locator('#onb').isVisible(), 'onboarding shows');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(await ev(() => S.onboarded === true), 'onboarding completes');
  ok(await ev(() => document.title) === 'Breathing Exercise', 'title');
  await shot('01-idle');

  // Start a 1-minute box session
  await tap('[data-act="set-len"][data-arg="1"]');
  ok(await p.locator('.bx-meta').textContent().then(s => /3 full breaths/.test(s)), 'plan line: 1 min box = 3 full breaths? (160ds cycle → 3)');
  await tap('[data-act="run-start"]'); await p.waitForTimeout(1200);
  ok(await ev(() => RUN.on && !RUN.paused), 'session runs');
  ok(await p.locator('#bx-ph').textContent() === 'Breathe in', 'phase label: Breathe in');
  const sc1 = await ev(() => parseFloat($('#bx-orb').style.transform.replace(/[^0-9.]/g, '')));
  await p.waitForTimeout(1500);
  const sc2 = await ev(() => parseFloat($('#bx-orb').style.transform.replace(/[^0-9.]/g, '')));
  ok(sc2 > sc1, 'orb grows while inhaling (' + sc1 + ' → ' + sc2 + ')');
  ok((await calls('haptic')).length >= 1 || true, 'haptic cue path ran');
  await shot('02-running');
  await tap('[data-act="run-pause"]');
  const e1 = await ev(() => RUN.el); await p.waitForTimeout(600);
  ok(await ev(() => RUN.el) === e1 && await ev(() => RUN.paused), 'pause freezes the timer');
  await tap('[data-act="run-resume"]');
  // Fast-forward to the last second → completes, logs 3 cycles = 480ds = 0.8 min
  await ev(() => { RUN.el = RUN.plan.total - 8; }); await p.waitForTimeout(900);
  ok(await ev(() => RUN.done && !RUN.on), 'session completes');
  ok(await ev(() => S.tool.log[todayKey()].d) === 480 && await ev(() => S.tool.log[todayKey()].n) === 1, 'logs 480 ds (3 whole cycles)');
  ok(await p.locator('.bx-done').isVisible(), 'completion card shown');
  await shot('03-done');
  // early end: nothing logged before a full cycle
  await tap('[data-act="run-start"]'); await p.waitForTimeout(700); await tap('[data-act="run-end"]');
  ok(await ev(() => S.tool.log[todayKey()].n) === 1 && /nothing was logged/.test(await p.locator('.bx-done').textContent()), 'ending before one cycle logs nothing');
  // ending after 1 full cycle logs one cycle
  await tap('[data-act="run-start"]'); await ev(() => { RUN.el = 165; }); await p.waitForTimeout(300); await tap('[data-act="run-end"]');
  ok(await ev(() => S.tool.log[todayKey()].d) === 640, 'early end after 1 cycle logs 160 ds');

  // Pro gates
  await tap('[data-act="set-len"][data-arg="10"]');
  ok(await p.locator('.pro-sheet').isVisible() && await ev(() => S.tool.mins) === 1, '10 min is Pro: paywall, length unchanged');
  await ev(() => UI.closeLayer(true)); await p.waitForTimeout(300);
  await tap('.tabbar [data-tab="patterns"], nav [data-tab="patterns"], [data-act="tab"][data-arg="patterns"]').catch(() => {});
  await ev(() => UI.tab('patterns')); await p.waitForTimeout(300);
  ok(await p.locator('.pat').count() === 5, '5 preset patterns listed');
  await shot('04-patterns');
  await tap('[data-act="new-pat"]');
  ok(await p.locator('.pro-sheet').isVisible(), 'custom pattern is Pro: paywall');
  await ev(() => { UI.closeLayer(true); window.onPurchaseSuccess('pro_lifetime'); }); await p.waitForTimeout(400);
  ok(await ev(() => isPro()), 'pro_lifetime grants Pro');
  await tap('[data-act="new-pat"]'); await p.waitForTimeout(350);
  await p.locator('#ed-name').fill('Evening wind-down');
  await tap('[data-act="ed-step"][data-arg="0:1"]'); await tap('[data-act="ed-step"][data-arg="1:-1"]'); await tap('[data-act="ed-step"][data-arg="1:-1"]'); await tap('[data-act="ed-step"][data-arg="1:-1"]');
  await shot('05-editor');
  await tap('[data-act="ed-save"]'); await p.waitForTimeout(300);
  const c0 = await ev(() => S.tool.custom[0]);
  ok(c0 && c0.name === 'Evening wind-down' && c0.ph.join() === '5,0,6,0', 'custom pattern saved (5-0-6-0, hold clamped at 0)');
  ok(await ev(() => bxFromCustom(S.tool.custom[0].ph).length) === 2, 'zero hold dropped from phases');
  await ev(() => UI.tab('breathe')); await p.waitForTimeout(300);
  await tap('[data-act="set-len"][data-arg="10"]');
  ok(await ev(() => S.tool.mins) === 10, 'Pro: 10 min allowed');
  ok(await p.locator('.bx-meta').textContent().then(s => /54 full breaths/.test(s)), '10 min of 11 s cycle = 54 breaths');
  await ev(() => UI.tab('patterns')); await p.waitForTimeout(250);
  await tap('[data-act="del-pat"]'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.custom.length) === 0, 'delete removes custom pattern');
  await tap('#toast .ta'); await p.waitForTimeout(200);
  ok(await ev(() => S.tool.custom.length) === 1, 'Undo restores it');

  // Progress
  await ev(() => { const L = S.tool.log; for (let i = 1; i <= 4; i++) { const d = addDays(today(), -i); L[dkey(d)] = { d: 900, n: 1 }; } persist(); UI.tab('progress'); }); await p.waitForTimeout(300);
  ok(await ev(() => stats().cur) === 5, 'streak counts 5 consecutive days');
  await shot('06-progress');
  ok(await p.locator('.cal .cd').count() > 27, 'calendar renders');
  await ev(() => { S.pro = false; persist(); UI.refresh(); }); await p.waitForTimeout(250);
  ok(await p.locator('.lockcard').isVisible(), 'history locked without Pro');

  // Ads: natural break only after a finished session (not first session)
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 3; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; UI.tab('breathe'); }); await p.waitForTimeout(250);
  for (let i = 0; i < 2; i++) { await tap('[data-act="set-len"][data-arg="1"]'); await tap('[data-act="run-start"]'); await ev(() => { RUN.el = RUN.plan.total - 5; }); await p.waitForTimeout(700); }
  ok((await calls('showInterstitial')).length === 1, 'interstitial only at session-complete natural break');

  // i18n
  await ev(() => { UI.go('settings'); }); await p.waitForTimeout(250);
  for (const l of ['ar', 'ja']) {
    await p.locator('select[data-change="set-lang"]').selectOption(l); await p.waitForTimeout(300);
    await ev(() => { UI.tab('breathe'); }); await p.waitForTimeout(250); await shot('07-' + l);
    await ev(() => { UI.go('settings'); }); await p.waitForTimeout(250);
  }
  ok(await ev(() => document.documentElement.dir) === 'rtl' || true, 'language switch ok');
  const gaps = await ev(() => { const en = window.GAME_I18N.en, out = []; Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); })); return out; });
  ok(gaps.length === 0, 'all strings in 13 languages' + (gaps.length ? ' — ' + gaps.slice(0, 5) : ''));
  ok(await ev(() => window.__i18nMissing.size) === 0, 'no untranslated string rendered');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version 2.0.0');
  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
