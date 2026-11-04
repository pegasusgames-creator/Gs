#!/usr/bin/env node
// BloodSugarLog runtime check - drives the REAL UI in headless Chromium with the mocked
// Android bridge and real tap/input events: onboarding, mg/dL + mmol/L entry with exact
// conversion, range colouring at the edges, far-limit note, save/undo, history filter +
// edit + delete/undo, free limit (60) paywall, ranges screen (validation, per-context,
// reset), insights (time in range, averages, eA1C gating), doctor summary, CSV (Pro),
// weekly + dated reminders, purchases, backup, 13-language completeness, RTL + ja.
//   node BloodSugarLog/test/runtime_check.js       (exit 1 on any failure)
//   SHOTS=<dir> node ...                           also writes screenshots
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BloodSugarLog/android/app/src/main/assets/game.html');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const SHOTS = process.env.SHOTS || '';
const VP = (process.env.VP || '360x640').split('x').map(Number);
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: VP[0], height: VP[1] }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  const p = await ctx.newPage();
  p.setDefaultTimeout(6000);
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(220); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  const type = async (sel, v) => { await p.locator(sel).fill(v); await p.waitForTimeout(120); };
  const txt = async (sel) => (await p.locator(sel).first().innerText()).replace(/[\u2066\u2069]/g, '').replace(/\s+/g, ' ');
  const shot = async (n) => { if (SHOTS) { fs.mkdirSync(SHOTS, { recursive: true }); await p.screenshot({ path: path.join(SHOTS, n + '.png') }); } };
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. Onboarding, empty Log screen
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next');
  ok(/diagnosis/i.test(await txt('#onb')) && /insulin/i.test(await txt('#onb')), 'last onboarding card: no diagnosis, no dosing/insulin advice');
  await tap('#onb-next');
  ok(await ev(() => S.onboarded === true), 'onboarding completes');
  ok(/neutral default/i.test(await txt('.notice')), 'default-range notice asks the user to set the clinician ranges');
  ok(/not a medical device/i.test(await txt('.disc')), 'disclaimer visible on the Log screen');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');
  await shot('01_log_empty');

  // 2. mg/dL entry, colours at the edges of the default range (70-180, far 54/250)
  const chip = async () => txt('#g-res .cl');
  const probe = async (v) => { await type('#in-v', v); return (await p.locator('#g-res .cl').count()) ? chip() : txt('#g-res'); };
  ok((await probe('110')).includes('In range'), '110 mg/dL in range');
  ok((await txt('#g-res .alt')) .replace(/[\u2066\u2069]/g, '') === '110 mg/dL = 6.1 mmol/L', 'both units shown: ' + await txt('#g-res .alt'));
  ok((await probe('180')).includes('In range') && (await probe('181')).includes('Above range'), '180 in range, 181 above (upper end is inside)');
  ok((await probe('70')).includes('In range') && (await probe('69')).includes('Below range'), '70 in range, 69 below (lower end is inside)');
  ok((await probe('54')).includes('Below range') && (await probe('53')).includes('Far below'), '54 below, 53 far below');
  ok(/care team|emergency/i.test(await txt('#g-res')) , 'far-below shows the contact-your-care-team note, no dosing');
  ok((await probe('250')).includes('Above range') && (await probe('251')).includes('Far above'), '250 above, 251 far above');
  ok(/outside/.test(await probe('19')) && /outside/.test(await probe('601')), 'values outside 20-600 are rejected');
  await shot('02_log_far');

  // 3. mmol/L entry, exact conversion
  await type('#in-v', '');
  await tap('.unitbar [data-arg="mmol"]');
  ok(await ev(() => S.tool.unit) === 'mmol', 'unit switch to mmol/L');
  ok((await probe('5.5')).includes('In range') && (await txt('#g-res .alt')) === '99 mg/dL = 5.5 mmol/L', '5.5 mmol/L -> 99 mg/dL -> 5.5: ' + await txt('#g-res .alt'));
  ok((await probe('3,9')).includes('In range') && (await txt('#g-res .alt')) === '70 mg/dL = 3.9 mmol/L', 'comma decimal 3,9 mmol/L = 70 mg/dL, in range');
  ok((await probe('10.0')).includes('In range') && (await probe('10.1')).includes('Above range'), '10.0 mmol/L (180) in range, 10.1 (182) above');
  ok(/outside/.test(await probe('34')), '34 mmol/L rejected');
  await tap('.unitbar [data-arg="mg"]');

  // 4. Save with context, carbs, tags, note; undo
  await type('#in-v', '112');
  await tap('.cx[data-arg="f"]');
  await tap('[data-act="more-toggle"]');
  await type('#in-carbs', '45'); await tap('.cx[data-act="tog-tag"][data-arg="exercise"]'); await type('#in-note', 'before walk');
  await tap('[data-act="save-read"]'); await p.waitForTimeout(250);
  const e0 = await ev(() => S.tool.entries[0]);
  ok(e0 && e0.mg === 112 && e0.c === 'f' && e0.carbs === 45 && e0.note === 'before walk' && e0.tags.join() === 'exercise', 'reading saved with context, carbs, tag, note');
  ok(await p.locator('.group .erow').count() === 1 && (await txt('.group .erow')).includes('Fasting'), 'today list shows the reading with its context');
  await tap('#toast .ta'); await p.waitForTimeout(150);
  ok(await ev(() => S.tool.entries.length) === 0, 'Undo removes the just-saved reading');
  // Fill a believable history: 70 readings over 40 days (more than the 60 free ones)
  await ev(() => {
    const out = []; let seed = 7; const r = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
    const ctxs = ['f', 'b', 'a', 'a', 'n', 'o'];
    for (let d = 0; d < 40; d++) for (let k = 0; k < 2; k++) {
      const dt = new Date(); dt.setDate(dt.getDate() - d); dt.setHours(k ? 20 : 7 + (d % 3), 10, 0, 0);
      const c = ctxs[(d + k) % 6]; const mg = Math.round((c === 'a' ? 150 : c === 'f' ? 100 : 125) + (r() - .5) * 90);
      if (dt.getTime() < Date.now()) out.push({ id: 'h' + d + k, ts: dt.getTime(), mg: mg, c: c, carbs: c === 'a' ? 50 : null, note: d === 3 ? 'party' : '', tags: [] });
    }
    S.tool.entries = out.sort((a, b) => a.ts - b.ts); persist(); UI.tab('log');
  });
  const n80 = await ev(() => S.tool.entries.length);
  ok(n80 >= 70, 'seeded ' + n80 + ' readings over 40 days');
  await ev(() => { while (S.tool.entries.length > 59) S.tool.entries.shift(); persist(); UI.tab('log'); });

  // 5. Free limit 60
  await type('#in-v', '100'); await tap('[data-act="save-read"]');
  ok(await ev(() => S.tool.entries.length) === 60, '60th free reading saves');
  await type('#in-v', '101'); await tap('[data-act="save-read"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.length) === 60 && await p.locator('.pro-hero').isVisible(), '61st reading opens the Pro paywall (history stays at 60)');
  await ev(() => UI.closeLayer(true)); await p.waitForTimeout(200);

  // 6. History: filter, edit, delete + undo
  await tap('[data-act="tab"][data-arg="history"]'); await p.waitForTimeout(300);
  ok(await p.locator('.erow').count() > 10, 'history lists readings grouped by day');
  await tap('.cx[data-act="filt"][data-arg="f"]');
  const fr = await p.locator('.erow').count();
  ok(fr > 0 && await ev(() => document.querySelectorAll('.erow').length === S.tool.entries.filter(e => e.c === 'f').length), 'filter by Fasting shows only fasting readings (' + fr + ')');
  await tap('.cx[data-act="filt"][data-arg="all"]');
  await shot('03_history');
  await tap('.erow >> nth=0'); await p.waitForTimeout(350);
  await type('#ed-v', '131'); await tap('.cx[data-act="ed-ctx"][data-arg="a"]'); await type('#ed-note', 'edited'); await tap('[data-act="ed-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.entries.some(e => e.mg === 131 && e.note === 'edited' && e.c === 'a')), 'edit saves value, context, note');
  const nBefore = await ev(() => S.tool.entries.length);
  await tap('.erow >> nth=2'); await p.waitForTimeout(350);
  await tap('[data-act="ed-delete"]'); await p.waitForTimeout(250); await tap('.dialog .btn-danger'); await p.waitForTimeout(350);
  ok(await ev(() => S.tool.entries.length) === nBefore - 1, 'delete asks first, then removes');
  await tap('#toast .ta'); await p.waitForTimeout(200);
  ok(await ev(() => S.tool.entries.length) === nBefore, 'Undo brings it back');

  // 7. Ranges screen
  await tap('[data-act="tab"][data-arg="insights"]'); await p.waitForTimeout(300);
  await tap('[data-act="go"][data-arg="ranges"]'); await p.waitForTimeout(300);
  await type('[data-k="lo"]', '90'); await type('[data-k="hi"]', '80'); await tap('[data-act="rg-save"]');
  ok(/order/i.test(await txt('.msg.err')) && await ev(() => S.tool.ranges.lo) === 70, 'low > high is refused with a message');
  await type('[data-k="lo"]', '80'); await type('[data-k="hi"]', '130'); await tap('[data-act="rg-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => JSON.stringify([S.tool.ranges.lo, S.tool.ranges.hi, S.tool.ranges.set])) === '[80,130,true]', 'ranges 80-130 saved and marked as set');
  await tap('[data-act="go"][data-arg="ranges"]'); await tap('[data-act="rg-per"]');
  ok(await p.locator('.cgrp').count() === 4, 'per-meal-context ranges: four rows');
  await type('[data-k="a.lo"]', '80'); await type('[data-k="a.hi"]', '180'); await tap('[data-act="rg-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => JSON.stringify(S.tool.ranges.ctx.a)) === '{"lo":80,"hi":180}' && await ev(() => GL.classify(170, GL.rangeFor(S.tool.ranges, 'a'))) === 'in' && await ev(() => GL.classify(170, GL.rangeFor(S.tool.ranges, 'f'))) === 'h', 'after-meal range 80-180 applies only to after-meal readings');
  await shot('04_ranges');

  // 8. Insights
  await tap('[data-act="tab"][data-arg="insights"]'); await p.waitForTimeout(300);
  ok(await p.locator('.tiles3 .tl').count() === 3 && await p.locator('.tir i').count() >= 2, 'tiles and time-in-range bar render');
  ok(await p.locator('.chart > svg').count() === 2 && await p.locator('.hb-r').count() === 10, 'two charts and ten average rows (5 times of day + 5 meal contexts)');
  const st = await ev(() => { const w = inWindow(30); const s = GL.stats(w.map(toItem), S.tool.ranges); return [s.n, GL.pctInt(s.cls.in, s.n)]; });
  ok((await txt('.tiles3')).includes(st[1] + '%') && (await txt('.tiles3')).includes(String(st[0])), 'in-range % and count match the maths (' + st + ')');
  ok(/Estimate/.test(await txt('.badge.est')) && /28\.7/.test(await txt('body')), 'A1C card labelled Estimate with the ADAG formula');
  const a1 = await ev(() => { const a = a1cData(); return [a.ok, a.n, a.days, a.tenths]; });
  ok(a1[0] === true && /%/.test(await txt('.card .big')), 'eA1C shown with enough data: ' + a1.join('/') + ' -> ' + await txt('.card .big'));
  await shot('05_insights');
  await tap('.seg [data-act="per"][data-arg="7"]');
  ok(await ev(() => TD.per) === 7 && await p.locator('.seg [data-arg="7"][aria-pressed="true"]').count() === 1, 'period switch to 7 days');
  await ev(() => { const keep = S.tool.entries.filter(e => e.ts > Date.now() - 5 * 864e5); S.tool.entries = keep; persist(); UI.refresh(); });
  ok(await ev(() => a1cData().ok) === false && /at least 20 readings/.test(await txt('body')), 'with < 20 readings / < 10 days the eA1C is withheld and the requirement is stated');
  await ev(() => { window.__restore && 0; });

  // 9. Doctor summary + CSV
  await tap('[data-act="sum-open"]'); await p.waitForTimeout(350);
  const sumTxt = await ev(() => document.getElementById('sum-ta').value);
  ok(/Blood Sugar Log/.test(sumTxt) && /18\.0156/.test(sumTxt) && /Not a medical record/.test(sumTxt) && /Target range set by the user: 80–130/.test(sumTxt), 'summary names the app, factor, ranges set by the user and the disclaimer');
  await tap('[data-act="sum-share"]');
  ok((await calls('shareText')).length === 1, 'Share summary calls Android.shareText');
  await ev(() => UI.closeLayer(true));
  await ev(() => UI.go('settings')); await p.waitForTimeout(250);
  await tap('[data-act="csv"]'); await p.waitForTimeout(300);
  ok(await p.locator('.pro-hero').isVisible(), 'CSV export is behind the Pro paywall');
  await ev(() => UI.closeLayer(true)); await p.waitForTimeout(450);
  const buy0 = (await calls('purchase')).length;
  await ev(() => Pro.open('csv_pro')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buy0 + 1, 'Unlock Pro calls Android.purchase');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => isPro() && adsRemoved()), 'pro_lifetime grants Pro and ad-free');
  const csv = await ev(() => TOOL.csv()), lines = csv.trim().split('\n');
  ok(lines[0] === 'date,time,glucose_mg_dl,glucose_mmol_l,meal_context,carbs_g,range_class,tags,note' && lines.length === (await ev(() => S.tool.entries.length)) + 1, 'CSV header + one row per reading');
  ok(await ev(() => { const e = S.tool.entries[0]; const old = e.note; e.note = '=HYPERLINK("x")'; const c = TOOL.csv(); e.note = old; return c.includes("'=HYPERLINK"); }), 'CSV neutralises formula-looking notes');
  await ev(() => UI.back()); await p.waitForTimeout(200);

  // 10. Reminders: weekly and dated
  await ev(() => { window.__calls.length = 0; UI.tab('log'); }); await p.waitForTimeout(200);
  await tap('.ab-actions [data-arg="rem"]'); await p.waitForTimeout(300);
  ok(/No reminders/.test(await txt('.quiet')), 'reminders screen starts empty');
  await tap('[data-act="rem-add"]'); await p.waitForTimeout(300);
  await tap('.cx[data-act="rd-day"][data-arg="6"]');
  await p.locator('input[data-change="rd-time"]').fill('07:30'); await p.waitForTimeout(100);
  await tap('[data-act="rem-save"]'); await p.waitForTimeout(400);
  const sr = await calls('scheduleReminder');
  ok(sr.length === 1 && sr[0][1][0] === 1 && sr[0][1][1] === 7 && sr[0][1][2] === 30 && sr[0][1][3] === (62 | 64), 'weekly reminder (Mon-Sat 07:30) scheduled in slot 1 via scheduleReminder');
  await tap('[data-act="rem-add"]'); await tap('.seg [data-act="rd-kind"][data-arg="once"]');
  await p.locator('input[data-change="rd-when"]').fill('2099-03-04T09:15'); await p.waitForTimeout(100);
  await tap('[data-act="rem-save"]'); await p.waitForTimeout(400);
  const dr = await calls('scheduleDatedReminder');
  ok(dr.length === 1 && dr[0][1][0] === 2 && dr[0][1][2] === false, 'dated one-time reminder scheduled in slot 2 (not yearly)');
  ok(await p.locator('.remrow').count() === 2, 'both reminders listed');
  await tap('.remrow >> nth=0 >> .switch'); await p.waitForTimeout(250);
  ok((await calls('cancelReminder')).some(c => c[1][0] === 1) && await ev(() => S.tool.rems[0].on === false), 'switch off cancels the weekly reminder');
  await tap('[data-act="rem-add"]'); await tap('.seg [data-act="rd-kind"][data-arg="once"]');
  await p.locator('input[data-change="rd-when"]').fill('2001-01-01T09:00'); await tap('[data-act="rem-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.rems.length) === 2, 'a one-time reminder in the past is refused');
  await ev(() => UI.closeLayer(true));
  await shot('06_reminders');
  await ev(() => { S.tool.rems[1].ts = Date.now() - 1000; persist(); remSync(); });
  ok(await ev(() => S.tool.rems[1].on === false), 'a fired one-time reminder switches itself off on the next sync');

  // 11. Purchases, restore, ad cadence
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { window.onPurchaseSuccess('remove_ads'); });
  ok(await ev(() => S.removeAds === true && !S.pro), 'remove_ads grants ad-free only');
  await ev(() => window.onPurchaseSuccess('mystery_sku'));
  ok(await ev(() => JSON.stringify(S.pendingGrants || localStorage.pendingGrants || '')).then(v => v.includes('mystery_sku')), 'unknown SKU is parked in pendingGrants');
  await ev(() => { S.removeAds = false; S.sessions = 3; S.ads = { last: 0, breaks: 5 }; window.__calls.length = 0; Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'interstitial only at a natural break after the cadence is met');

  // 12. Backup round trip + foreign backup rejected
  const backup = await ev(() => Data.payload()), nE = await ev(() => S.tool.entries.length);
  await ev(() => { S.tool.entries = []; });
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  const dlg = await p.locator('.dialog .btn-danger').count(); if (dlg) { await tap('.dialog .btn-danger'); await p.waitForTimeout(300); }
  ok(await ev(() => S.tool.entries.length) === nE, 'backup restores every reading (' + nE + ')');
  ok(await ev(() => Data.parse('{"kind":"backup","app":"com.other"}')) === null, 'a backup from another app is rejected');
  ok(await ev(() => TOOL.migrate({ entries: [{ id: 'a', ts: Date.now(), mg: 5000, c: 'x' }, { id: 'b', ts: Date.now(), mg: 100, c: 'zz', carbs: 9999, tags: ['bogus', 'stress'] }], ranges: { lo: 200, hi: 100, vlo: 1, vhi: 9999 } }).entries.length === 1), 'migrate drops invalid entries and repairs ranges');

  // 13. Dark, accents, languages
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13, 'language picker lists 13 locales');
  const gaps = await ev(() => { const en = Object.assign({}, window.GAME_I18N.en); const out = []; Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); })); return out; });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' - missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.settings.theme = 'dark'; applyTheme(); UI.tab('log'); }); await p.waitForTimeout(250);
  await type('#in-v', '95'); await shot('07_dark_log');
  await ev(() => { UI.tab('insights'); }); await p.waitForTimeout(250); await shot('08_dark_insights');
  await ev(() => { S.settings.theme = 'light'; applyTheme(); });
  await ev(() => UI.go('settings')); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ar'); await p.waitForTimeout(300);
  await ev(() => UI.tab('log')); await p.waitForTimeout(250);
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  await type('#in-v', '120'); await shot('09_ar_log');
  await ev(() => UI.tab('insights')); await p.waitForTimeout(250); await shot('10_ar_insights');
  ok(await ev(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'no horizontal overflow in Arabic');
  await ev(() => UI.go('settings')); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').selectOption('ja'); await p.waitForTimeout(300);
  await ev(() => UI.tab('log')); await p.waitForTimeout(250); await type('#in-v', '120');
  ok((await txt('#g-res .cl')).length > 0, 'Japanese renders the range chip'); await shot('11_ja_log');
  await ev(() => UI.tab('history')); await p.waitForTimeout(200); await ev(() => UI.tab('insights')); await p.waitForTimeout(200);
  await ev(() => { UI.go('ranges'); }); await p.waitForTimeout(200); await ev(() => { UI.back(); UI.go('rem'); }); await p.waitForTimeout(200);
  await p.locator('select[data-change="set-lang"]').count();
  ok(await ev(() => window.__i18nMissing.size) === 0, 'no untranslated string was rendered');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version present');
  ok(await ev(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'no horizontal overflow at ' + VP.join('x'));
  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
