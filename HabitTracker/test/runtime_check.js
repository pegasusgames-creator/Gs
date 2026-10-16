#!/usr/bin/env node
// HabitTracker runtime check — drives the REAL UI in headless Chromium with the
// mocked Android bridge (scripts/runtime/mock_bridge.js) and real tap events:
// onboarding → create habit → check-in → streak → undo → free limit → purchase
// grant → restore → interstitial cadence → reminder permission flow →
// backup export/import → delete + undo → i18n completeness.
//
//   node HabitTracker/test/runtime_check.js        (exit 1 on any failure)
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'HabitTracker/android/app/src/main/assets/game.html');
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
  p.on('pageerror', e => errs.push(e.message));
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(220); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. First launch: onboarding, then the empty Today screen.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(!(await p.locator('#onb').count()) && await ev(() => S.onboarded === true), 'onboarding completes with "Get started"');
  ok(await p.locator('.empty').isVisible() && await p.locator('.sug').count() === 10, 'empty state with 10 suggestions');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');

  // 2. Create a habit through the editor.
  await tap('[data-act="new-habit"]'); await p.waitForTimeout(350);
  await p.locator('#ed-name').fill('Read 20 pages');
  await tap('[data-act="ed-icon"][data-arg="book"]');
  await tap('[data-act="ed-save"]'); await p.waitForTimeout(300);
  const h = await ev(() => S.tool.habits[0]);
  ok(h && h.name === 'Read 20 pages' && h.icon === 'book' && h.days === 127, 'habit created with name/icon/every day');

  // 3. Check-in with a real tap → done today, streak 1, persisted.
  await tap('.hrow .chk'); await p.waitForTimeout(300);
  ok(await ev(() => HB.done(S.tool.habits[0], todayKey())), 'tap on the circle checks the habit in');
  ok(await p.locator('.hrow .chk').getAttribute('aria-pressed') === 'true', 'check button reports aria-pressed=true');
  ok(await ev(() => HB.streak(S.tool.habits[0])) === 1, 'streak = 1 after the first check-in');
  ok(await ev(() => JSON.parse(localStorage.getItem('habittracker_save')).tool.log[S.tool.habits[0].id][todayKey()] === 1), 'check-in persisted to localStorage');
  ok((await calls('haptic')).length > 0, 'haptic feedback on check-in');

  // 4. Streak across past days (a skipped unscheduled day does not break it).
  await ev(() => { const hh = S.tool.habits[0]; for (let i = 1; i <= 6; i++) HB.set(hh, dkey(addDays(today(), -i)), 1); hh.created = dkey(addDays(today(), -10)); persist(); UI.refresh(); });
  ok(await ev(() => HB.streak(S.tool.habits[0])) === 7 && await ev(() => HB.best(S.tool.habits[0])) === 7, 'streak 7 after six past check-ins');
  ok((await p.locator('.hrow .hmt').textContent()).includes('7'), 'row shows the 7-day streak');
  await ev(() => { const hh = S.tool.habits[0]; hh.days = 127 & ~(1 << addDays(today(), -3).getDay()); HB.set(hh, dkey(addDays(today(), -3)), 0); MEMO.clear(); });
  ok(await ev(() => HB.streak(S.tool.habits[0])) === 6, 'an unscheduled, unchecked day is skipped, not a break');
  await ev(() => { S.tool.habits[0].days = 127; MEMO.clear(); persist(); UI.refresh(); });

  // 5. Uncheck → undo toast restores it.
  await tap('.hrow .chk');
  ok(!(await ev(() => HB.done(S.tool.habits[0], todayKey()))), 'second tap unchecks');
  await tap('#toast .ta');
  ok(await ev(() => HB.done(S.tool.habits[0], todayKey())), 'Undo restores the check-in');

  // 6. Count goal fills step by step; long-press opens the day sheet.
  await ev(() => { openEditor(null, { name: 'Water', icon: 'drop', target: 3, unit: 'glasses' }); });
  await p.waitForTimeout(300); await tap('[data-act="ed-save"]');
  await tap('.hrow[data-hid="' + await ev(() => S.tool.habits[1].id) + '"] .chk');
  ok(await ev(() => HB.cnt(S.tool.habits[1], todayKey())) === 1 && !(await ev(() => HB.done(S.tool.habits[1], todayKey()))), 'count goal: 1/3 after one tap');
  const box = await p.locator('.hrow[data-hid="' + await ev(() => S.tool.habits[1].id) + '"] .chk').boundingBox();
  await p.mouse.move(box.x + 20, box.y + 20); await p.mouse.down(); await p.waitForTimeout(650); await p.mouse.up(); await p.waitForTimeout(350);
  ok(await p.locator('.dsheet').isVisible(), 'long-press opens the day sheet');
  await tap('[data-act="ds-plus"]'); await tap('[data-act="ds-plus"]');
  await p.locator('#ds-note').fill('Felt great');
  await tap('[data-act="ds-save"]');
  ok(await ev(() => HB.done(S.tool.habits[1], todayKey()) && HB.note(S.tool.habits[1], todayKey()) === 'Felt great'), 'day sheet saves the count (3/3) and the note');

  // 7. Free plan: the 6th active habit opens the paywall instead of the editor.
  await ev(() => { for (let i = 0; i < 3; i++) S.tool.habits.push({ id: 'x' + i, name: 'Extra ' + i, icon: 'star', color: '#5B48D9', days: 127, target: 1, unit: '', created: todayKey(), archived: false, rem: { on: false, h: 9, m: 0 }, slot: 10 + i }); persist(); UI.refresh(); });
  await tap('[data-act="new-habit"]'); await p.waitForTimeout(350);
  ok(await p.locator('.pro-hero').isVisible() && !(await p.locator('#ed-body').count()), 'free limit (5) → paywall opens');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);

  // 8. Purchase grant exactly as the Java billing bridge delivers it.
  const buyCalls0 = (await calls('purchase')).length;
  await ev(() => Pro.open('limit_t')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buyCalls0 + 1, 'Unlock Pro button calls Android.purchase("pro_lifetime")');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && S.removeAds === true && isPro() && adsRemoved()), 'pro_lifetime grants Pro + ad-free');
  ok((await calls('hideBannerAd')).length > 0, 'banner hidden after the Pro grant');
  await tap('[data-act="new-habit"]'); await p.waitForTimeout(350);
  ok(await p.locator('#ed-body').count() === 1, 'Pro: the 6th habit opens the editor');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);
  await ev(() => window.onPurchaseSuccess('mystery_sku'));
  ok(await ev(() => JSON.parse(localStorage.getItem('pendingGrants') || '{}').mystery_sku > 0), 'unknown SKU parked in pendingGrants (never thrown away)');
  await ev(() => { localStorage.removeItem('pendingGrants'); window.onPurchaseSuccess('remove_ads'); });
  ok(await ev(() => S.removeAds === true), 'remove_ads grant is idempotent');

  // 9. Restore purchases: Settings row → bridge → re-grant on a wiped install.
  await ev(() => { S.pro = false; S.removeAds = false; persist(); });
  await tap('[data-act="go"][data-arg="settings"]');
  await p.evaluate(() => { document.getElementById('view').scrollTop = 99999; });
  await tap('[data-act="restore"]');
  ok((await calls('restorePurchases')).length >= 1, 'Restore purchases calls Android.restorePurchases()');
  await ev(() => { window.onPurchaseSuccess('pro_lifetime'); window.onRestoreComplete(1); }); await p.waitForTimeout(200);
  ok(await ev(() => S.pro === true) && (await p.locator('#toast .tm').textContent()).length > 0, 'restore re-grants Pro and confirms with a toast');
  ok(await p.locator('[data-act="privacy"]').count() === 1, 'Privacy policy row present');
  await tap('[data-act="privacy"]');
  ok((await calls('openUrl')).some(c => c[1][0] === 'https://pegasusgames-creator.github.io/privacy.html'), 'Privacy opens the canonical URL via Android.openUrl');

  // 10. Interstitial cadence: natural breaks only, never first session, >=3 min, never for owners.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');
  await ev(() => { S.sessions = 3; Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'later session: one interstitial, then the 3-minute floor holds');
  await ev(() => { S.ads.last = Date.now() - 200000; window.onPurchaseSuccess('remove_ads'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'Remove-Ads owner: never an interstitial');

  // 11. Reminders: permission asked in context, then scheduled (slot 0 = daily).
  await ev(() => { window.__calls.length = 0; UI.refresh(); });
  await tap('[data-act="toggle-daily"]'); await p.waitForTimeout(250);
  const sr = await calls('scheduleReminder');
  ok(await ev(() => S.settings.daily.on) && sr.length === 1 && sr[0][1][0] === 0 && sr[0][1][3] === 127, 'daily reminder → scheduleReminder(0, h, m, 127, …)');
  ok((await calls('hasNotificationPermission')).length >= 1, 'notification permission checked only after the switch was turned on');

  // 12. Backup: export payload → import into a wiped app → undo.
  const backup = await ev(() => Data.payload());
  const nHabits = await ev(() => S.tool.habits.length);
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('today'); });
  ok(await ev(() => S.tool.habits.length) === 0, 'tool data wiped for the import test');
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(nHabits === 5 && await ev(() => S.tool.habits.length) === nHabits && await ev(() => S.pro === false), 'import restores all ' + nHabits + ' habits (purchases are never imported)');
  ok(await ev(() => Data.parse('{"kind":"backup","app":"com.other"}')) === null, 'a backup from another app is rejected');

  // 13. Delete with confirm + undo.
  await tap('[data-act="tab"][data-arg="habits"]');
  await tap('.mrow .hmain'); await p.waitForTimeout(250);
  await tap('[data-act="edit-habit"]'); await p.waitForTimeout(350);
  await tap('[data-act="ed-delete"]'); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(350);
  ok(await ev(() => S.tool.habits.length) === nHabits - 1, 'delete removes the habit after confirmation');
  await tap('#toast .ta'); await p.waitForTimeout(200);
  ok(await ev(() => S.tool.habits.length) === nHabits && await ev(() => Object.keys(S.tool.log[S.tool.habits[0].id] || {}).length) > 0, 'Undo brings the habit back with its history');

  // 14. Theme / accent / language.
  await ev(() => { S.pro = false; S.removeAds = false; S.proTrialUntil = 0; persist(); UI.go('settings'); });
  await tap('[data-act="set-accent"][data-arg="forest"]'); await p.waitForTimeout(300);
  ok(await p.locator('.layer .sheet').isVisible() && await ev(() => document.documentElement.dataset.accent) === 'violet', 'locked Pro accent → trial/Pro sheet, accent unchanged');
  await tap('[data-act="theme-trial"]');
  ok((await calls('showRewarded')).some(c => c[1][0] === 'theme_trial'), 'rewarded trial requests type "theme_trial"');
  await ev(() => window.onAdReward('theme_trial')); await p.waitForTimeout(250);
  ok(await ev(() => document.documentElement.dataset.accent) === 'forest' && await ev(() => S.proTrialUntil > Date.now()), 'reward unlocks the Pro accent for 24 h');
  await tap('[data-act="set-theme"][data-arg="dark"]');
  ok(await ev(() => document.documentElement.dataset.theme) === 'dark', 'dark theme applies');
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13 && ['en', 'ar', 'de', 'es', 'fr', 'hi', 'id', 'it', 'ja', 'pt', 'tr', 'uk', 'zh'].every(l => langs.includes(l)), 'language picker lists the 13 listing locales');
  const gaps = await ev(() => { const en = window.GAME_I18N.en; const out = []; Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); })); return out; });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' — missing ' + gaps.slice(0, 6).join(', ') : ''));
  await p.locator('select[data-change="set-lang"]').selectOption('ar'); await p.waitForTimeout(300);
  ok(await ev(() => document.documentElement.dir) === 'rtl' && await ev(() => document.documentElement.lang) === 'ar', 'Arabic switches the layout to RTL');
  ok(await ev(() => window.__i18nMissing.size) === 0, 'no untranslated string was rendered');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '2.0.0', 'data-app-version present');

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
