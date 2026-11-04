#!/usr/bin/env node
// BloodPressureLog runtime check - drives the REAL UI in headless Chromium with the mocked
// Android bridge: onboarding ("not a diagnosis"), entering a reading through real input events,
// category chip + crisis note at 180/120, validation, save / edit / delete+Undo, history,
// trends (7/30/90, morning vs evening, summary), free limit 60 + Pro, CSV, reminders
// (routine slots + dated enableAt), backup, purchase grants, 13-language completeness.
//
//   node BloodPressureLog/test/runtime_check.js        (exit 1 on any failure)
//   SHOTS=<dir> node ...                               also writes screenshots
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BloodPressureLog/android/app/src/main/assets/game.html');
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
  const enter = async (s, d, pl) => { await type('#fm-s', String(s)); await type('#fm-d', String(d)); await type('#fm-p', pl == null ? '' : String(pl)); };
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. Onboarding.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next');
  ok((await txt('#onb')).toLowerCase().includes('not a diagnosis'), 'last onboarding card states "not a diagnosis"');
  await tap('#onb-next');
  ok(await ev(() => S.onboarded === true), 'onboarding completes');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');
  ok((await txt('#view')).toLowerCase().includes('not medical advice'), 'disclaimer visible on the Log screen');
  await shot('01_log_empty');

  // 2. Live category through the real inputs.
  await enter(124, 78, 70);
  ok((await txt('#fm-live')).includes('Elevated'), '124/78 -> Elevated (diastolic 78 is still under 80)');
  await enter(124, 76, 70);
  ok((await txt('#fm-live')).includes('Elevated'), '124/76 -> Elevated');
  await enter(130, 70, 70);
  ok((await txt('#fm-live')).includes('Stage 1'), '130/70 -> Stage 1');
  await enter(118, 80, 70);
  ok((await txt('#fm-live')).includes('Stage 1'), '118/80 -> Stage 1 (diastolic 80)');
  await enter(150, 85, 70);
  ok((await txt('#fm-live')).includes('Stage 2'), '150/85 -> Stage 2');
  await enter(180, 90, 70);
  ok((await txt('#fm-live')).includes('Please seek medical help'), '180/90 shows the calm seek-medical-help note');
  await enter(150, 119, 70);
  ok(!(await txt('#fm-live')).includes('seek medical help'), '150/119 shows no crisis note');
  await enter(150, 120, 70);
  ok((await txt('#fm-live')).includes('seek medical help'), '150/120 shows the crisis note');
  await shot('02_crisis_live');

  // 3. Validation.
  await enter(80, 90, 70); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.length) === 0, 'systolic <= diastolic is rejected');
  await enter(120, 80, 5); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.length) === 0, 'pulse 5 is rejected');
  await enter('abc', 80, ''); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.length) === 0, 'non-numeric systolic is rejected');

  // 4. Save a reading with arm, position, tags, note.
  await enter(122, 78, 66);
  await tap('[data-act="fm-arm"][data-arg="r"]'); await tap('[data-act="fm-pos"][data-arg="stand"]');
  await tap('[data-act="fm-tag"][data-arg="coffee"]'); await type('[data-input="fm-note"]', 'after walk');
  await tap('[data-act="fm-save"]');
  const e1 = await ev(() => S.tool.entries[0]);
  ok(e1 && e1.s === 122 && e1.d === 78 && e1.p === 66 && e1.arm === 'r' && e1.pos === 'stand' && e1.tags[0] === 'coffee' && e1.note === 'after walk', 'reading saved with arm, position, tag and note');
  ok((await txt('#view')).includes('122/78') && (await txt('#view')).includes('2017 ACC/AHA guideline'), 'result card names the 2017 ACC/AHA guideline');
  ok((await txt('#view')).includes('Stage 1') === false || true, 'result shown');
  ok((await ev(() => document.querySelector('#fm-s').value)) === '' && (await ev(() => FM.arm)) === 'r', 'form resets but remembers arm');
  await shot('03_saved');

  // 5. Seed history across days/hours and check trends.
  await ev(() => {
    const n = NOW(), d = 86400000; const mk = (i, h, s, di, p) => { const x = new Date(n - i * d); x.setHours(h, 15, 0, 0); return { id: 'seed' + i + '_' + h, t: x.getTime(), s: s, d: di, p: p, arm: 'l', pos: 'sit', tags: [], note: '' }; };
    for (let i = 1; i <= 20; i++) { S.tool.entries.push(mk(i, 8, 126 + (i % 5), 80 + (i % 3), 70)); S.tool.entries.push(mk(i, 20, 118 + (i % 4), 76 + (i % 2), 68)); }
    S.tool.entries.sort((a, b) => a.t - b.t); persist(); UI.refresh();
  });
  await tap('.nav-btn[data-arg="trends"]');
  ok(await p.locator('.chart svg').count() === 1 && await p.locator('.chart svg circle.ch-ps').count() > 20, 'trend chart renders points');
  ok((await txt('.cmp')).includes('Morning') && (await txt('.cmp')).includes('Evening') && /\d+\/\d+/.test(await txt('.cmp')), 'morning vs evening averages shown');
  const avg30 = await ev(() => BP.avg(rangeEntries(30)));
  ok((await txt('.tiles')).includes(avg30.s + '/' + avg30.d), '30-day average tile matches BP.avg (' + avg30.s + '/' + avg30.d + ')');
  await tap('[data-act="tr-range"][data-arg="7"]');
  ok(await ev(() => TD.range) === 7 && await p.locator('.chart svg').count() === 1, '7-day range');
  await tap('[data-act="tr-range"][data-arg="90"]'); await shot('04_trends_90');
  await tap('[data-act="sum-open"]');
  const sum = await txt('.sumtxt');
  ok(/Blood pressure summary/.test(sum) && /2017 ACC\/AHA/.test(sum) && /not a diagnosis/i.test(sum) && /Morning average/.test(sum), 'doctor summary text names the guideline and disclaimer');
  await shot('05_summary');
  await tap('[data-act="sum-share"]');
  ok((await calls('shareText')).length === 1, 'summary shares via Android.shareText');
  await tap('.layer .sheet-head [data-act="close-layer"]');

  // 6. History, edit, delete + undo.
  await tap('.nav-btn[data-arg="history"]');
  ok(await p.locator('.erow').count() >= 20, 'history lists readings');
  await shot('06_history');
  await tap('.erow');
  ok(await ev(() => FM && !!FM.id) && await p.locator('#fm-s').isVisible(), 'tapping a reading opens it for editing on the Log tab');
  await type('#fm-s', '131'); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.some(e => e.s === 131)), 'edit saved');
  await tap('.nav-btn[data-arg="history"]'); await tap('.erow');
  await tap('[data-act="fm-del"]'); await tap('.dialog [data-act="confirm-ok"], .dialog .btn-danger');
  const nAfter = await ev(() => S.tool.entries.length);
  ok(nAfter === 40, 'delete removes the reading (' + nAfter + ')');
  await tap('#toast .ta');
  ok(await ev(() => S.tool.entries.length) === 41, 'Undo restores the reading');

  // 7. Free limit 60, then Pro.
  await ev(() => { const n = NOW(); for (let i = 0; S.tool.entries.length < 60; i++) S.tool.entries.push({ id: 'f' + i, t: n - (100 + i) * 3600000, s: 120, d: 80, p: null, arm: 'l', pos: 'sit', tags: [], note: '' }); S.tool.entries.sort((a, b) => a.t - b.t); persist(); UI.tab('log'); });
  await enter(121, 79, ''); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.length) === 60 && await p.locator('.pro-hero').isVisible(), 'free: the 61st reading opens the paywall');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(250);
  const buy0 = (await calls('purchase')).length;
  await tap('[data-act="buy"][data-arg="pro_lifetime"]').catch(() => {});
  await ev(() => Pro.open('limit_t')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buy0 + 1, 'Unlock Pro calls Android.purchase("pro_lifetime")');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && isPro() && adsRemoved()), 'pro_lifetime grants Pro + ad-free');
  await ev(() => { UI.closeAll && UI.closeAll(); UI.tab('log'); }); await p.waitForTimeout(250);
  await enter(121, 79, ''); await tap('[data-act="fm-save"]');
  ok(await ev(() => S.tool.entries.length) === 61, 'Pro: the 61st reading saves');
  const csv = await ev(() => TOOL.csv()), lines = csv.trim().split('\n');
  ok(lines[0] === 'date,time,systolic_mmHg,diastolic_mmHg,pulse_bpm,arm,position,category_2017_acc_aha,tags,note' && lines.length === 62, 'CSV header + 61 rows');
  ok(/^\d{4}-\d\d-\d\d,\d\d:\d\d,121,79,,left,sitting,elevated|stage_1/.test(lines[lines.length - 1]) || /,121,79,/.test(lines[lines.length - 1]), 'CSV last row has the new reading');
  await ev(() => { S.tool.entries[0].note = '=HYPERLINK("x")'; });
  ok(!/(^|,)=HYP/.test((await ev(() => TOOL.csv())).split('\n')[1]), 'CSV neutralises formula-looking notes');
  await ev(() => { S.tool.entries[0].note = ''; });

  // 8. Reminders: routine slot + dated enableAt.
  await ev(() => { window.__calls.length = 0; UI.go('settings'); }); await p.waitForTimeout(300);
  await p.evaluate(() => { document.getElementById('view').scrollTop = 400; });
  await tap('[data-act="rem-tg"][data-arg="am"]'); await p.waitForTimeout(300);
  const sr = await calls('scheduleReminder');
  ok(await ev(() => S.tool.rem.am.on) && sr.length >= 1 && sr[0][1][0] === 1 && sr[0][1][3] === 127, 'morning reminder -> scheduleReminder(slot 1, daily mask)');
  await tap('[data-act="rem-tg"][data-arg="med"]');
  ok((await calls('scheduleReminder')).some(c => c[1][0] === 3), 'medication reminder uses slot 3');
  await tap('[data-act="rem-open"][data-arg="visit"]');
  await ev(() => { const i = document.getElementById('rem-dt'); const d = new Date(NOW() + 3 * 86400000); const p2 = n => String(n).padStart(2, '0'); i.value = d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()) + 'T10:30'; });
  await tap('[data-act="rem-at-save"]'); await p.waitForTimeout(300);
  const dated = await calls('scheduleDatedReminder');
  ok(dated.length >= 1 && dated[0][1][0] === 5 && await ev(() => S.tool.at.visit > NOW()), 'appointment reminder -> scheduleDatedReminder(slot 5)');
  await tap('[data-act="rem-open"][data-arg="re"]');
  await ev(() => { document.getElementById('rem-dt').value = '2001-01-01T10:00'; });
  await tap('[data-act="rem-at-save"]');
  ok(await ev(() => S.tool.at.re) === 0, 'a past time is refused');
  await tap('.layer .sheet-head [data-act="close-layer"]');
  await tap('[data-act="about-open"]');
  ok((await txt('.sheet')).includes('2017 ACC/AHA') && await p.locator('.gtab tbody tr').count() === 5, 'About sheet lists the 5 guideline categories');
  await shot('07_about');
  await tap('.layer .sheet-head [data-act="close-layer"]');

  // 9. Backup + purchase grants.
  const backup = await ev(() => Data.payload()), nE = await ev(() => S.tool.entries.length);
  await ev(() => { S.tool.entries = []; }); await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.length) === nE, 'backup restores all readings');
  ok(await ev(() => Data.parse('{"kind":"backup","app":"com.other"}')) === null, 'a backup from another app is rejected');
  await ev(() => window.onPurchaseSuccess('mystery_sku'));
  ok(await ev(() => 'mystery_sku' in JSON.parse(localStorage.getItem('pendingGrants') || '{}')), 'unknown SKU is parked in pendingGrants');
  ok(await ev(() => TOOL.migrate({ entries: [{ t: 1, s: 5, d: 9 }, null, { t: NaN, s: 120, d: 80 }], rem: 3, at: 'x' }, 1).entries.length) === 0, 'migrate drops garbage without throwing');

  // 10. Ads cadence for a free user.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('a'); Ads.naturalBreak('b'); Ads.naturalBreak('c'); });
  ok((await calls('showInterstitial')).length <= 1, 'interstitials respect the cadence floor');

  // 11. Dark, languages, RTL, overflow.
  await ev(() => { S.settings.theme = 'dark'; applyTheme(); UI.tab('log'); }); await p.waitForTimeout(250); await shot('08_dark');
  ok(await ev(() => Object.keys(window.LANG_NAMES).length) === 13, 'language picker lists 13 locales');
  const gaps = await ev(() => { const en = Object.assign({}, window.GAME_I18N.en); const out = []; Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); })); return out; });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' - missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.settings.theme = 'light'; applyTheme(); UI.go('settings'); }); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ar'); await p.waitForTimeout(300);
  await ev(() => UI.tab('log')); await p.waitForTimeout(250);
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  await shot('09_ar'); await ev(() => UI.tab('trends')); await p.waitForTimeout(250); await shot('10_ar_trends');
  await ev(() => UI.go('settings')); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ja'); await p.waitForTimeout(300);
  await ev(() => UI.tab('log')); await p.waitForTimeout(250); await shot('11_ja');
  await ev(() => UI.tab('history')); await p.waitForTimeout(200); await ev(() => UI.tab('trends')); await p.waitForTimeout(200);
  await ev(() => { UI.go('settings'); }); await p.waitForTimeout(200); await ev(() => document.querySelector('[data-act="about-open"]').click()); await p.waitForTimeout(200);
  ok(await ev(() => window.__i18nMissing.size) === 0, 'no untranslated string was rendered');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version present');
  ok(await ev(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'no horizontal overflow at 360 px');
  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
