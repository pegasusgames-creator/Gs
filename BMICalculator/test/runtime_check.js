#!/usr/bin/env node
// BMICalculator runtime check - drives the REAL UI in headless Chromium with the
// mocked Android bridge and real tap/input events: onboarding, metric + imperial
// input, live BMI + band + gauge, healthy range, child note, save/update, history
// chart + note edit + delete/undo, free limit, goal, body-fat estimate, CSV (Pro),
// purchase grants, interstitial cadence, reminder, backup, 13-language completeness.
//
//   node BMICalculator/test/runtime_check.js        (exit 1 on any failure)
//   SHOTS=<dir> node ...                            also writes screenshots
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BMICalculator/android/app/src/main/assets/game.html');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const SHOTS = process.env.SHOTS || '';
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 360, height: 640 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  const p = await ctx.newPage();
  p.setDefaultTimeout(6000);
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(220); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  const type = async (sel, v) => { await p.locator(sel).fill(v); await p.waitForTimeout(120); };
  const txt = async (sel) => (await p.locator(sel).first().innerText()).replace(/\s+/g, ' ');
  const shot = async (n) => { if (SHOTS) { fs.mkdirSync(SHOTS, { recursive: true }); await p.screenshot({ path: path.join(SHOTS, n + '.png') }); } };
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. Onboarding, then the empty BMI screen.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next');
  ok((await txt('#onb')).toLowerCase().includes('not a diagnosis'), 'last onboarding card states "not a diagnosis"');
  await tap('#onb-next');
  ok(await ev(() => S.onboarded === true), 'onboarding completes');
  ok(await p.locator('#bmi-res .empty').isVisible(), 'empty state until height and weight are typed');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');

  // 2. Metric input -> live BMI, band, gauge, healthy range.
  await type('#in-w', '70'); await type('#in-h', '175');
  ok((await txt('#bmi-res .rbig b')) === '22.9', 'BMI 22.9 for 70 kg / 175 cm');
  ok((await txt('#bmi-res .chip')).includes('Normal range'), 'band "Normal range"');
  ok(await p.locator('#bmi-res .gauge .gmk').count() === 1, 'gauge marker shown');
  ok((await txt('#bmi-res .card .big')) === '56.7 – 76.2 kg', 'healthy range 56.7 - 76.2 kg at 175 cm (' + (await txt('#bmi-res .card .big')) + ')');
  ok((await txt('#bmi-res')).toLowerCase().includes('inside this range'), 'weight reported inside the range');
  ok(/not valid for children|not a diagnosis/i.test(await txt('body')), 'disclaimer visible on the BMI screen');
  await shot('01_calc_metric');
  // band edges through the real input: exactly 25.0 and 18.5
  await type('#in-w', '76.6'); await type('#in-h', '175'); // 25.01 -> 25.0
  ok((await txt('#bmi-res .chip')).includes('Pre-obese') && (await txt('#bmi-res .rbig b')) === '25.0', '25.0 is Pre-obese (overweight range)');
  await type('#in-w', '56.7'); // 18.51 -> 18.5
  ok((await txt('#bmi-res .chip')).includes('Normal range') && (await txt('#bmi-res .rbig b')) === '18.5', '18.5 is Normal range');
  await type('#in-w', '56.4'); // 18.41
  ok((await txt('#bmi-res .chip')).includes('Mild thinness'), '18.4 is Mild thinness');
  await type('#in-w', '95'); await type('#in-h', '175'); // 31.0
  ok((await txt('#bmi-res .chip')).includes('Obese class I') && (await txt('#bmi-res')).includes('above this range'), '31.0 is Obese class I, weight above the range');
  await type('#in-w', '1'); ok(await p.locator('#bmi-res .msg.err').count() === 1 && await ev(() => S.tool.cur.kg) === null, 'out-of-range weight shows an error, no result');
  await type('#in-w', '70,5'); ok(await ev(() => S.tool.cur.kg) === 70.5, 'comma decimal accepted');
  await type('#in-w', '70');

  // 3. Imperial: conversion round trip.
  await tap('.unitbar [data-arg="imperial"]');
  ok(await p.locator('#in-ft').count() === 1 && await p.locator('#in-in').count() === 1, 'imperial shows ft + in fields');
  ok((await p.locator('#in-w').inputValue()) === '154.3', 'weight converted to 154.3 lb');
  ok((await p.locator('#in-ft').inputValue()) === '5' && (await p.locator('#in-in').inputValue()) === '9', '175 cm shown as 5 ft 9 in');
  await type('#in-w', '154'); await type('#in-ft', '5'); await type('#in-in', '9');
  ok(Math.abs(await ev(() => S.tool.cur.cm) - 175.3) < 0.01 && (await txt('#bmi-res .rbig b')) === '22.7', 'imperial 154 lb / 5 ft 9 in -> BMI 22.7');
  ok((await txt('#bmi-res .card .big')).endsWith('lb'), 'healthy range in lb');
  await shot('02_calc_imperial');
  await tap('.unitbar [data-arg="metric"]');
  ok(Math.abs(parseFloat(await p.locator('#in-w').inputValue()) - 69.9) < 0.05, 'back to metric: weight ~69.9 kg');
  await type('#in-w', '70'); await type('#in-h', '175');

  // 4. Child note: under 18 hides the adult bands.
  await tap('[data-act="bf-toggle"]');
  await type('#in-age', '15');
  ok(await p.locator('#bmi-res .chip').count() === 0 && (await txt('#bmi-res')).includes('under 18'), 'age under 18: adult category hidden, note shown');
  // 5. Body-fat estimate (Deurenberg): 22.857*1.2 + .23*30 - 10.8 - 5.4 = 18.1 male
  await type('#in-age', '30'); await tap('#bf-box [data-act="sex"][data-arg="m"]');
  const bfTxt = await txt('#bf-box');
  ok(bfTxt.includes('≈ 18%') && bfTxt.includes('Estimate') && bfTxt.includes('Deurenberg'), 'body-fat estimate labelled "Estimate" with the formula named (' + bfTxt.slice(0, 80) + ')');
  await tap('#bf-box [data-act="sex"][data-arg="f"]');
  ok((await txt('#bf-box')).includes('≈ 29%'), 'female estimate 29%');
  await shot('03_bodyfat');
  await type('#in-age', '17'); ok((await txt('#bf-box')).includes('18 to 99'), 'no estimate for under 18');
  await type('#in-age', '30');

  // 6. Save a reading, replace the same day, history chart.
  await type('#in-note', 'baseline');
  await tap('[data-act="save-read"]'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.entries.length) === 1 && await ev(() => S.tool.entries[0].note) === 'baseline' && await ev(() => S.tool.entries[0].bf) !== null, 'reading saved with note + body-fat estimate');
  await type('#in-w', '71'); await tap('[data-act="save-read"]'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.entries.length) === 1 && await ev(() => S.tool.entries[0].kg) === 71 && await ev(() => S.tool.entries[0].note) === 'baseline', 'second save on the same day updates it (note kept)');
  await tap('#toast .ta'); await p.waitForTimeout(150);
  ok(await ev(() => S.tool.entries[0].kg) === 70, 'Undo restores the earlier reading');
  await ev(() => { const e = S.tool.entries[0], base = new Date(); for (let i = 1; i <= 5; i++) { const d = new Date(base.getFullYear(), base.getMonth(), base.getDate() - i * 9, 12); S.tool.entries.push({ id: 'h' + i, d: dkey(d), kg: 70 + i * 1.5 - (i > 3 ? 5 : 0), cm: 175, note: i === 2 ? 'holiday' : '', bf: null }); } S.tool.entries.sort((a, b) => a.d < b.d ? -1 : 1); persist(); });
  await tap('[data-act="tab"][data-arg="history"]'); await p.waitForTimeout(300);
  ok(await p.locator('.chart svg .ch-line').count() === 1 && await p.locator('.chart svg circle').count() === 6, 'history chart draws the line and 6 points');
  ok(await p.locator('.erow').count() === 6 && (await txt('.group')).includes('holiday'), 'list shows 6 readings with notes');
  await shot('04_history_bmi');
  await tap('.chart [data-act="chart"][data-arg="w"]');
  ok(await p.locator('.chart svg .ch-line').count() === 1, 'weight chart view');
  await shot('05_history_weight');
  // edit a note + delete with undo
  await tap('.erow >> nth=0'); await p.waitForTimeout(350);
  await type('#ed-note', 'edited'); await tap('[data-act="ed-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.some(e => e.note === 'edited')), 'note edited');
  await tap('.erow >> nth=2'); await p.waitForTimeout(350);
  await tap('[data-act="ed-delete"]'); await p.waitForTimeout(250); await tap('.dialog .btn-danger'); await p.waitForTimeout(350);
  ok(await ev(() => S.tool.entries.length) === 5, 'delete removes a reading after confirmation');
  await tap('#toast .ta'); await p.waitForTimeout(200);
  ok(await ev(() => S.tool.entries.length) === 6, 'Undo brings it back');

  // 7. Free limit: 30 readings, then the paywall.
  await ev(() => { const base = new Date(); for (let i = 1; i <= 30; i++) { const d = new Date(base.getFullYear(), base.getMonth(), base.getDate() - 100 - i, 12); S.tool.entries.push({ id: 'z' + i, d: dkey(d), kg: 72, cm: 175, note: '', bf: null }); } S.tool.entries.sort((a, b) => a.d < b.d ? -1 : 1); persist(); S.tool.entries.splice(30); persist(); });
  const n0 = await ev(() => S.tool.entries.length);
  await ev(() => { S.tool.entries.shift(); S.tool.entries.push(...[]); UI.tab('calc'); });
  await ev(() => { S.tool.entries = S.tool.entries.filter(e => e.d !== todayKey()); while (S.tool.entries.length < 30) { const d = new Date(2020, 0, S.tool.entries.length + 1, 12); S.tool.entries.push({ id: 'f' + S.tool.entries.length, d: dkey(d), kg: 70, cm: 175, note: '', bf: null }); } persist(); UI.tab('calc'); });
  await p.waitForTimeout(200);
  await tap('[data-act="save-read"]'); await p.waitForTimeout(350);
  ok(await p.locator('.pro-hero').isVisible() && await ev(() => S.tool.entries.length) === 30, 'free limit (30) -> paywall opens, nothing dropped');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);

  // 8. CSV is Pro; purchase grants exactly as the billing bridge delivers them.
  await ev(() => UI.go('settings')); await p.waitForTimeout(250);
  await p.evaluate(() => { document.getElementById('view').scrollTop = 600; });
  await tap('[data-act="csv"]'); await p.waitForTimeout(300);
  ok(await p.locator('.pro-hero').isVisible(), 'CSV export opens the paywall for free users');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(250);
  const buy0 = (await calls('purchase')).length;
  await ev(() => Pro.open('limit_t')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buy0 + 1, 'Unlock Pro calls Android.purchase("pro_lifetime")');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && S.removeAds === true && isPro() && adsRemoved()), 'pro_lifetime grants Pro + ad-free');
  await ev(() => UI.closeAll && UI.closeAll()); await ev(() => UI.tab('calc')); await p.waitForTimeout(250);
  await type('#in-w', '70'); await type('#in-h', '175');
  await tap('[data-act="save-read"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.length) === 31, 'Pro: the 31st reading saves');
  const csv = await ev(() => TOOL.csv());
  const lines = csv.trim().split('\n');
  ok(lines[0] === 'date,weight_kg,height_cm,bmi,who_band,body_fat_pct_estimate,note' && lines.length === 32 && /^\d{4}-\d{2}-\d{2},70,175,22\.9,normal,/.test(lines[lines.length - 1]), 'CSV has header + 31 rows with BMI and band');
  await ev(() => window.onPurchaseSuccess('mystery_sku'));
  ok(await ev(() => JSON.parse(localStorage.getItem('pendingGrants') || '{}').mystery_sku > 0), 'unknown SKU parked in pendingGrants');
  await ev(() => { S.pro = false; S.removeAds = false; persist(); UI.go('settings'); });
  await p.evaluate(() => { document.getElementById('view').scrollTop = 99999; });
  await tap('[data-act="restore"]');
  ok((await calls('restorePurchases')).length >= 1, 'Restore purchases calls Android.restorePurchases()');
  await ev(() => { window.onPurchaseSuccess('pro_lifetime'); window.onRestoreComplete(1); }); await p.waitForTimeout(200);
  ok(await ev(() => S.pro === true), 'restore re-grants Pro');
  ok(await p.locator('[data-act="privacy"]').count() === 1, 'Privacy policy row present');

  // 9. Interstitial cadence.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');
  await ev(() => { S.sessions = 3; Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'later session: one interstitial, then the 3-minute floor holds');

  // 10. Goal tab.
  await ev(() => { S.tool.entries = S.tool.entries.slice(-3); S.tool.entries.forEach((e, i) => { e.kg = [82, 79, 77][i]; e.d = dkey(addDays(today(), -(14 - i * 7))); }); persist(); UI.tab('goal'); });
  await p.waitForTimeout(250);
  await type('#in-gt', '70'); await tap('[data-act="goal-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.goal && S.tool.goal.kg) === 70 && await ev(() => S.tool.goal.start) === 77, 'goal saved, start defaults to the latest reading');
  ok(await p.locator('.prog').count() === 1 && (await txt('.gl')).length > 0, 'goal progress bar shown');
  ok(await ev(() => BM.goalProgress(82, 77, 70)) > 0.4, 'progress maths');
  await shot('06_goal');
  await tap('[data-act="goal-clear"]'); await p.waitForTimeout(250); await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.goal) === null, 'goal removed with confirm'); await tap('#toast .ta'); await p.waitForTimeout(200);
  ok(await ev(() => S.tool.goal && S.tool.goal.kg) === 70, 'Undo restores the goal');
  await ev(() => { S.tool.goal.kg = 50; persist(); UI.refresh(); }); await p.waitForTimeout(200);
  ok((await txt('#view')).includes('talk to a health professional'), 'a target below BMI 18.5 shows the neutral health-professional note');

  // 11. Weekly reminder (opt-in, permission in context).
  await ev(() => { window.__calls.length = 0; UI.go('settings'); }); await p.waitForTimeout(250);
  await tap('[data-act="wk-on"]'); await p.waitForTimeout(300);
  const sr = await calls('scheduleReminder');
  ok(await ev(() => S.tool.wk.on) && sr.length >= 1 && sr[0][1][0] === 1, 'weekly reminder -> scheduleReminder(slot 1, …) after the switch');

  // 12. Backup round trip.
  const backup = await ev(() => Data.payload()), nE = await ev(() => S.tool.entries.length);
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('calc'); });
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.length) === nE && await ev(() => S.tool.goal !== null), 'import restores readings and goal');
  ok(await ev(() => Data.parse('{"kind":"backup","app":"com.other"}')) === null, 'a backup from another app is rejected');
  ok(await ev(() => TOOL.migrate({ entries: [{ d: 'x', kg: 1e9, cm: 5 }, null], cur: { kg: 'a' }, units: 'zz' }, 1).entries.length) === 0, 'migrate drops garbage without throwing');

  // 13. Dark, accent, languages.
  await ev(() => { S.settings.theme = 'dark'; applyTheme(); UI.tab('calc'); }); await p.waitForTimeout(250);
  await shot('07_dark');
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13, 'language picker lists 13 locales');
  const gaps = await ev(() => { const en = Object.assign({}, window.GAME_I18N.en); const out = []; Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); })); return out; });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' - missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.settings.theme = 'light'; applyTheme(); });
  await ev(() => UI.go('settings')); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ar'); await p.waitForTimeout(300);
  await ev(() => UI.tab('calc')); await p.waitForTimeout(250);
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  await shot('08_ar');
  await ev(() => UI.tab('history')); await p.waitForTimeout(200); await shot('09_ar_history');
  await ev(() => UI.go('settings')); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ja'); await p.waitForTimeout(300);
  await ev(() => UI.tab('calc')); await p.waitForTimeout(250);
  ok((await txt('#bmi-res .chip')).length > 0, 'Japanese renders the band chip');
  await shot('10_ja');
  await ev(() => UI.tab('goal')); await p.waitForTimeout(200); await ev(() => UI.tab('history')); await p.waitForTimeout(200);
  ok(await ev(() => window.__i18nMissing.size) === 0, 'no untranslated string was rendered');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version present');
  ok(await ev(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'no horizontal overflow at 360 px');

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
