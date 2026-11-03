#!/usr/bin/env node
// AgeCalculator runtime check — drives the REAL UI in headless Chromium with the
// mocked Android bridge (scripts/runtime/mock_bridge.js) and real input events:
// onboarding → exact age → invalid / future / reversed input → save people (free
// limit 3 → paywall → Pro grant) → custom milestones (Pro) → date difference →
// next birthday + Feb 29 → people order → weekly reminder → share → delete + undo →
// backup → interstitial cadence → i18n completeness in all 13 languages.
//
//   node AgeCalculator/test/runtime_check.js        (exit 1 on any failure)
// The calendar maths itself is gated by scripts/check_agecalculator_dates.py.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'AgeCalculator/android/app/src/main/assets/game.html');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 360, height: 640 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  const p = await ctx.newPage();
  p.setDefaultTimeout(6000);
  const errs = [];
  p.on('pageerror', e => errs.push(e.message + ' @ ' + String(e.stack || '').split('\n').slice(1, 3).join(' | ')));
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(220); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  const txt = async (sel) => (await p.locator(sel).first().innerText()).replace(/\s+/g, ' ').trim();
  const nums = async (sel) => (await p.locator(sel).allInnerTexts()).map(s => s.replace(/[^\d]/g, ''));
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. First launch: onboarding, then the empty Age screen.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(!(await p.locator('#onb').count()) && await ev(() => S.onboarded === true), 'onboarding completes with "Get started"');
  ok(await p.locator('.empty').isVisible() && await p.locator('.hero').count() === 0, 'empty state asks for a date of birth');
  ok(await p.locator('[data-act="tab"]').count() === 3, 'three tabs: Age, Difference, People');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');

  // 2. Exact age on a fixed "age on" date: Feb 29 2000 -> Nov 3 2026 = 26 y 8 m 5 d, 9,744 days.
  await p.locator('#q-birth').fill('2000-02-29');
  await p.locator('#q-ason').fill('2026-11-03'); await p.waitForTimeout(300);
  const big = (await nums('.hero .bt b')).join(',');
  ok(big === '26,8,5', 'hero shows 26 years, 8 months, 5 days (got ' + big + ')');
  const tiles = (await nums('.tiles .tile b')).join(',');
  const hrs = 233856 + await ev(() => (AM.iso(nowD()) === '2026-11-03' ? new Date(NOW()).getHours() : 0));   // "age on" today adds the hours elapsed today
  ok(tiles === '320,1392,9744,' + hrs, 'totals: 320 months, 1,392 weeks, 9,744 days, ' + hrs + ' hours (got ' + tiles + ')');
  const nb = await txt('.nb');
  ok(nb.includes('Sunday') && nb.includes('February 28, 2027'), 'next birthday of a Feb 29 baby in a common year: Sunday, Feb 28 2027');
  ok(nb.includes('Turns 27') && (await txt('.nb .cnt')).startsWith('117'), 'turns 27, 117 days to go');
  ok((await p.locator('.fine').allInnerTexts()).join(' ').includes('Feb 28'), 'the Feb 28 rule for Feb 29 birthdays is stated');
  const zs = await txt('.zs');
  ok(zs.includes('Pisces') && zs.includes('Dragon'), 'Feb 29 2000 = Pisces + Dragon (after Chinese New Year, Feb 5)');
  ok(await p.locator('.mrow').count() >= 5, 'milestone rows listed (' + (await p.locator('.mrow').count()) + ')');

  // 3. Invalid / future / reversed input never shows a number.
  await p.locator('#q-birth').fill('2099-01-01'); await p.waitForTimeout(250);
  ok(await p.locator('.msg.err').isVisible() && await p.locator('.hero').count() === 0, 'a birth date after the "age on" date shows an error, no age');
  await p.locator('#q-ason').fill(''); await p.waitForTimeout(250);
  ok((await txt('.msg.err')).includes('future'), 'with no "age on" date, a future birth date says it is in the future');
  await p.locator('#q-birth').fill('1990-05-15'); await p.waitForTimeout(250);
  ok(await p.locator('.hero').count() === 1, 'a valid date brings the result back');

  // 4. Save people: 3 free, the 4th opens the paywall.
  const savePerson = async (name) => { await tap('[data-act="save-person"]'); await p.waitForTimeout(350); await p.locator('#ed-name').fill(name); await tap('[data-act="ed-save"]'); await p.waitForTimeout(300); };
  await savePerson('Ana');
  ok(await ev(() => S.tool.people.length) === 1 && await ev(() => S.tool.people[0].birth) === '1990-05-15', 'person saved from the calculator with name + birth date');
  await p.locator('#q-birth').fill('1984-11-20'); await savePerson('Ben');
  await p.locator('#q-birth').fill('2016-02-29'); await savePerson('Cleo');
  ok(await ev(() => S.tool.people.length) === 3, 'three free people saved');
  await tap('[data-act="save-person"]'); await p.waitForTimeout(350);
  ok(await p.locator('.pro-hero').isVisible() && !(await p.locator('#ed-body').count()), 'free limit (3): the 4th person opens the paywall');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);

  // 5. Custom milestones are Pro.
  await tap('[data-act="cm-add"]'); await p.waitForTimeout(350);
  ok(await p.locator('.pro-hero').isVisible(), 'custom milestone on the free plan opens the paywall');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);
  const buy0 = (await calls('purchase')).length;
  await ev(() => Pro.open('limit_t')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buy0 + 1, 'Unlock Pro calls Android.purchase("pro_lifetime")');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && S.removeAds === true && isPro() && adsRemoved()), 'pro_lifetime grants Pro + ad-free');
  await ev(() => { UI.closeAll(); UI.tab('age'); S.tool.quick.birth = '1990-05-15'; S.tool.quick.asOf = ''; persist(); UI.refresh(); }); await p.waitForTimeout(300);
  await tap('[data-act="cm-add"]'); await p.waitForTimeout(350);
  await p.locator('#cm-n').fill('0'); await tap('[data-act="cm-save"]');
  ok(await ev(() => S.tool.quick.custom.length) === 0, 'amount 0 is rejected');
  await p.locator('#cm-n').fill('2500'); await tap('[data-act="cm-u"][data-arg="d"]'); await p.locator('#cm-n').fill('2500'); await tap('[data-act="cm-save"]'); await p.waitForTimeout(300);
  await tap('[data-act="ms-past"]'); await p.waitForTimeout(200);          // a 2,500-day mark of a 1990 birth is long past
  ok(await ev(() => S.tool.quick.custom.length) === 1 && (await p.locator('.mrow:has-text("Custom")').count()) === 1, 'Pro: custom milestone "2,500 days" added and listed');
  const d2500 = await ev(() => AM.iso(AM.addDays(AM.parse('1990-05-15'), 2500)));
  ok(d2500 === '1997-03-19' && (await txt('.mrow:has-text("Custom")')).includes('Mar 19, 1997'), 'custom 2,500 days after 1990-05-15 shows Mar 19, 1997 (got ' + d2500 + ')');
  await tap('[data-act="cm-del"]'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.quick.custom.length) === 0, 'custom milestone removed');
  await tap('#toast .ta'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.quick.custom.length) === 1, 'Undo brings it back');
  ok(await p.locator('.mrow.past').count() > 0, 'passed milestones can be shown');

  // 6. Share age card = plain text through the bridge.
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="share-card"]');
  const sh = await calls('shareText');
  ok(sh.length === 1 && sh[0][1][0].length > 0, 'share age card calls Android.shareText with the card text');
  ok((await ev(() => cardText('', AM.parse('1990-05-15'), AM.parse('2026-11-03'), AM.diff(AM.parse('1990-05-15'), AM.parse('2026-11-03')), nbSafe(AM.parse('1990-05-15'), AM.parse('2026-11-03'))))).includes('36 years, 5 months, 19 days'), 'age card text carries the exact age');

  // 7. Date difference: 2021-01-31 -> 2021-03-01 = 1 month 1 day, 29 days, 20 weekdays.
  await tap('[data-act="tab"][data-arg="diff"]'); await p.waitForTimeout(300);
  ok(await p.locator('.empty').isVisible(), 'Difference starts with a prompt');
  await p.locator('[data-change="d-from"]').fill('2021-01-31');
  await p.locator('[data-change="d-to"]').fill('2021-03-01'); await p.waitForTimeout(300);
  const dh = (await nums('.hero .bt b')).join(','), dt = (await nums('.tiles .tile b')).join(',');
  ok(dh === '0,1,1' && dt === '29,4,1,20', 'Jan 31 -> Mar 1 2021 = 0y 1m 1d; 29 days, 4 weeks, 1 month, 20 weekdays (got ' + dh + ' | ' + dt + ')');
  await p.locator('[data-change="d-from"]').fill('2021-03-01');
  await p.locator('[data-change="d-to"]').fill('2021-01-31'); await p.waitForTimeout(300);
  ok(await p.locator('.msg:not(.err)').count() === 1 && (await nums('.hero .bt b')).join(',') === '0,1,1', 'reversed dates are put in order and give the same answer');
  await tap('[data-act="d-swap"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.diff.from) === '2021-01-31', 'Swap exchanges the two dates');
  await p.locator('[data-change="d-to"]').fill('2021-01-31'); await p.waitForTimeout(250);
  ok((await txt('.hero .hl')).toLowerCase().includes('same'), 'same date = "Same day"');
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="d-share"]');
  ok((await calls('shareText')).length === 1, 'difference result can be shared');

  // 8. People: sorted by days to the next birthday; open, edit, delete + undo.
  await tap('[data-act="tab"][data-arg="people"]'); await p.waitForTimeout(300);
  const order = await ev(() => [...document.querySelectorAll('.prow .rl')].map(e => e.textContent));
  const want = await ev(() => { const N = nowD(); return S.tool.people.map(x => ({ n: x.name, d: nbSafe(AM.parse(x.birth), N).days })).sort((a, b) => a.d - b.d).map(x => x.n); });
  ok(order.length === 3 && order.join() === want.join(), 'people listed soonest birthday first (' + order.join(', ') + ')');
  ok(await p.locator('.pbar').count() === 0, 'Pro: no free-limit bar');
  await tap('.prow[data-arg="' + await ev(() => S.tool.people[1].id) + '"]'); await p.waitForTimeout(350);
  ok(await p.locator('.hero').count() === 1 && (await txt('.hero .hl')).toLowerCase().includes('ben'), 'person detail shows Ben\'s age');
  await tap('[data-act="edit-person"]'); await p.waitForTimeout(400);
  await p.locator('#ed-name').fill('Benjamin'); await tap('[data-act="ed-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.people[1].name) === 'Benjamin', 'editing a person renames them');
  await tap('[data-act="edit-person"]'); await p.waitForTimeout(400);
  await tap('[data-act="ed-delete"]'); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(350);
  ok(await ev(() => S.tool.people.length) === 2, 'delete removes the person after confirmation');
  await tap('#toast .ta'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.people.length) === 3 && await ev(() => S.tool.people[1].name) === 'Benjamin', 'Undo brings the person back');
  await ev(() => { UI.closeAll(); UI.tab('people'); }); await p.waitForTimeout(300);

  // 9. Weekly birthday check: permission in context, then scheduleReminder(slot 1, day mask).
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="wk-on"]'); await p.waitForTimeout(300);
  const sr = await calls('scheduleReminder');
  ok(await ev(() => S.tool.wk.on) && sr.length >= 1 && sr[sr.length - 1][1][0] === 1 && sr[sr.length - 1][1][3] === 1, 'weekly check -> scheduleReminder(1, 18, 0, Sunday mask 1, …)');
  ok((await calls('hasNotificationPermission')).length >= 1, 'notification permission checked only after the switch was turned on');
  await p.locator('[data-change="wk-dow"]').selectOption('3'); await p.waitForTimeout(200);
  ok((await calls('scheduleReminder')).pop()[1][3] === 8, 'choosing Wednesday re-arms with mask 8');
  await tap('[data-act="wk-on"]'); await p.waitForTimeout(250);
  ok((await calls('cancelReminder')).some(c => c[1][0] === 1) && !(await ev(() => S.tool.wk.on)), 'switching it off cancels slot 1');

  // 10. Backup: export payload -> wipe -> import.
  const backup = await ev(() => Data.payload());
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('people'); });
  ok(await ev(() => S.tool.people.length) === 0, 'tool data wiped for the import test');
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.people.length) === 3 && await ev(() => S.tool.people.every(x => AM.parse(x.birth))), 'import restores all 3 people with valid dates');
  ok(await ev(() => TOOL.validateImport({ people: [{ id: 'x', name: 'Z', birth: '2023-02-29' }] })) === false, 'a backup with an impossible date is rejected');
  ok(await ev(() => TOOL.migrate({ people: [{ id: 'a', name: 'A', birth: '2023-02-30' }, { id: 'b', name: 'B', birth: '2020-02-29' }], quick: { birth: 'junk' } }).people.length) === 1, 'migrate drops entries with invalid dates, keeps valid ones');

  // 11. Interstitial cadence: natural breaks only, never first session, owners never.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');
  await ev(() => { S.sessions = 3; Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'later session: one interstitial, then the 3-minute floor holds');
  await ev(() => window.onPurchaseSuccess('remove_ads'));
  ok(await ev(() => S.removeAds === true), 'remove_ads grants ad-free');

  // 12. Language: 13 languages complete; Arabic RTL; every screen renders with no missing string.
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13, 'language picker lists 13 languages');
  const gaps = await ev(() => {
    const en = window.GAME_I18N.en, out = [];
    Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => {
      if (k in window.GAME_I18N[l]) return;
      const m = /^(.*)_(one|other)$/.exec(k);                       // plural keys: the language needs _other
      if (m && (m[1] + '_other') in window.GAME_I18N[l]) return;
      out.push(l + ':' + k);
    }));
    return out;
  });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' — missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.tool.quick.birth = '1990-05-15'; S.tool.quick.asOf = ''; S.tool.quick.custom = [{ id: 'c9', n: 3, u: 'm' }]; S.tool.diff = { from: '2019-02-28', to: '' }; S.pro = true; persist(); });
  for (const l of langs) {
    await ev(L => { S.settings.lang = L === 'en' ? '' : L; persist(); applyLang(); applyTheme(); UI.buildNav(); UI.tab('age'); UI.tab('diff'); UI.tab('people'); UI.go('person', { id: S.tool.people[0].id }); UI.back(); UI.tab('age'); }, l);
    await p.waitForTimeout(120);
  }
  const miss = await ev(() => [...window.__i18nMissing]);
  ok(miss.length === 0, 'no untranslated string rendered on Age, Difference, People or Person in any language' + (miss.length ? ': ' + miss.slice(0, 5).join(',') : ''));
  await ev(() => { S.settings.lang = 'ar'; persist(); applyLang(); UI.tab('age'); });
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  const signs = await ev(() => Object.keys(window.GAME_I18N).every(l => ['zw', 'zc'].every(k => String(window.GAME_I18N[l][k] || '').split('|').length === 12)));
  ok(signs, 'every language names all 12 signs and all 12 animals');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version present');

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
