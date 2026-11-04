#!/usr/bin/env node
// BillSplit runtime check — drives the REAL UI in headless Chromium with the mocked
// Android bridge (scripts/runtime/mock_bridge.js) and real input events:
// onboarding -> add items with real taps (who shares, custom shares) -> tax / tip entry ->
// the on-screen per-person totals add up to the bill to the cent -> people edit / remove + Undo ->
// share summary -> save to history (free limit 10 -> paywall -> Pro grant) -> CSV export (Pro) ->
// groups (free limit 3, load into a bill) -> history detail / re-open / delete + Undo ->
// currency switch (exponent change rescales + Undo) -> bad input never computes ->
// interstitial cadence -> backup round trip -> i18n completeness in all 13 languages, RTL, no overflow.
//
//   node BillSplit/test/runtime_check.js        (exit 1 on any failure)
// The split maths itself is gated by scripts/check_billsplit_math.py.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BillSplit/android/app/src/main/assets/game.html');
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
  const cents = s => parseInt(String(s).replace(/[^\d]/g, ''), 10);
  const personTotals = async () => (await p.locator('.pcard .pt').allInnerTexts()).map(cents);
  const heroTotal = async () => cents(await txt('.hero .tot'));
  const openSheet = async (sel) => { await tap(sel); await p.waitForSelector('.sheet'); await p.waitForTimeout(350); };
  const addItem = async (name, price, who, custom) => {   // who: [personIndex...]; custom: {index: n}
    await openSheet('[data-act="item-add"]');
    await p.locator('#ed-name').fill(name);
    await p.locator('#ed-price').fill(price);
    if (custom) await tap('[data-act="w-mode"][data-arg="custom"]');
    for (const i of who) await p.locator('.wsel').nth(i).tap();
    if (custom) for (const k of Object.keys(custom)) for (let n = 1; n < custom[k]; n++) await p.locator('[data-act="w-inc"]').nth(who.indexOf(+k)).tap();
    await p.waitForTimeout(150);
    await tap('[data-act="item-save"]'); await p.waitForTimeout(350);
  };
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. First launch.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(!(await p.locator('#onb').count()) && await ev(() => S.onboarded === true), 'onboarding completes');
  ok(await p.locator('[data-act="tab"]').count() === 3, 'three tabs: Split, Groups, History');
  ok(await p.locator('.hero').count() === 0 && await p.locator('#res .empty').isVisible(), 'empty bill shows the empty state, no total');
  ok(await p.locator('.pchip:not(.add)').count() === 2, 'a new bill starts with two people');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');

  // 2. Item validation, then a shared item with real taps.
  await openSheet('[data-act="item-add"]');
  await tap('[data-act="item-save"]');
  ok(await p.locator('.sheet').count() === 1 && /valid price/i.test(await txt('#toast')), 'saving without a price is rejected with a message');
  await p.locator('#ed-price').fill('abc'); await tap('[data-act="item-save"]');
  ok(await p.locator('.sheet').count() === 1, 'a non-numeric price is rejected');
  await p.locator('#ed-price').fill('10'); await tap('[data-act="item-save"]');
  ok(await p.locator('.sheet').count() === 1 && /at least one/i.test(await txt('#toast')), 'an item nobody shares is rejected');
  await tap('[data-act="w-all"]'); await p.locator('#ed-name').fill('Pizza'); await tap('[data-act="item-save"]'); await p.waitForTimeout(350);
  ok(await p.locator('.sheet').count() === 0 && await p.locator('.irow').count() === 1, 'a $10.00 pizza for everyone is saved');
  const t1 = await personTotals();
  ok(t1.length === 2 && t1[0] === 500 && t1[1] === 500 && await heroTotal() === 1000, 'two people split $10.00 -> $5.00 each; hero total $10.00');

  // 3. Three people: the odd cent. $10.00 / 3 -> 3.34 + 3.33 + 3.33, adds up exactly.
  await openSheet('[data-act="person-add"]'); await p.locator('#ed-name').fill('Cleo'); await tap('[data-act="person-save"]'); await p.waitForTimeout(300);
  ok(await p.locator('.pchip:not(.add)').count() === 3, 'a third person is added');
  ok(!/Person 3|Cleo/.test(await txt('.irow .rs')) && (await personTotals())[2] === 0, 'the existing item is not assigned to the new person until picked (explicit assignment); new person owes $0.00');
  await tap('.irow'); await p.waitForTimeout(350);
  await tap('[data-act="w-all"]'); await tap('[data-act="item-save"]'); await p.waitForTimeout(350);
  const t3 = await personTotals();
  ok(t3.join(',') === '334,333,333' && t3.reduce((a, b) => a + b, 0) === await heroTotal(), '$10.00 across 3 -> 3.34 / 3.33 / 3.33 and the hero total is $10.00');
  ok(/Adds up exactly/.test(await txt('.hero .chk')), 'the "adds up exactly" check is shown');

  // 4. Custom shares: 2 : 1 split of $9.00 between Person 1 and Person 2.
  await addItem('Wine', '9', [0, 1], { 0: 2 });
  ok(await txt('.irow:nth-child(2) .rs') === 'Person 1 ×2, Person 2', 'custom shares are summarised as "Person 1 ×2, Person 2"');
  const t4 = await personTotals();
  ok(t4.join(',') === '934,633,333' && await heroTotal() === 1900, 'Person 1 pays 3.34+6.00, Person 2 pays 3.33+3.00=6.33, Person 3 3.33; total $19.00');

  // 5. Tax and tip typed with real input events; proportional.
  await p.locator('#tax-in').fill('8.875'); await p.waitForTimeout(200);
  await tap('[data-act="tip-pre"][data-arg="18"]');
  const t5 = await personTotals(), hero5 = await heroTotal();
  ok(t5.reduce((a, b) => a + b, 0) === hero5, 'with tax 8.875% and tip 18% the per-person totals add up to the hero total (' + hero5 + ')');
  const exp5 = await ev(() => { const r = compute(S.tool.cur, S.tool.cc); return [r.subtotal, r.tax, r.tip, r.total]; });
  ok(exp5[0] === 1900 && exp5[1] === 169 && exp5[2] === 342 && exp5[3] === 2411, 'subtotal 19.00, tax 1.69 (8.875% rounded half-up), tip 3.42 (18% of items), total 24.11');
  await p.locator('#tax-in').fill('abc'); await p.waitForTimeout(200);
  ok(await ev(() => compute(S.tool.cur, S.tool.cc).tax) === 0 && await p.locator('#tax-err').isVisible(), 'invalid tax text is flagged and counts as 0, never NaN');
  await p.locator('#tax-in').fill('8.875'); await p.waitForTimeout(150);
  await tap('[data-act="tip-base"][data-arg="post"]'); await tap('[data-act="tax-dist"][data-arg="even"]'); await tap('[data-act="tip-dist"][data-arg="even"]');
  const t6 = await personTotals();
  ok(t6.reduce((a, b) => a + b, 0) === await heroTotal() && await ev(() => compute(S.tool.cur, S.tool.cc).tip) === 372, 'tip on items + tax = 18% of 20.69 = 3.72, shared evenly; totals still add up');
  await tap('[data-act="tax-mode"][data-arg="amt"]'); await p.locator('#tax-in').fill('2,50'); await p.waitForTimeout(200);
  ok(await ev(() => compute(S.tool.cc && S.tool.cur, S.tool.cc).tax) === 250, 'a fixed tax amount (comma decimal) of 2.50 is read');
  ok((await personTotals()).reduce((a, b) => a + b, 0) === await heroTotal(), 'fixed amount: totals add up');

  // 6. Person card expands to the items; rename + remove with Undo.
  await tap('.pc-h'); await p.waitForTimeout(200);
  ok(/Pizza/.test(await txt('.pc-d')) && /Wine/.test(await txt('.pc-d')), 'a person card expands to the items they share');
  await tap('.pchip:not(.add)'); await p.waitForTimeout(350);
  await p.locator('#ed-name').fill('Ana'); await tap('[data-act="person-save"]'); await p.waitForTimeout(300);
  ok(/Ana/.test(await txt('.pchip')) && /Ana/.test(await txt('.pcard')), 'renaming a person updates chips and results');
  await tap('.pchip:nth-child(3)'); await p.waitForTimeout(350); await tap('[data-act="person-del"]'); await p.waitForTimeout(300);
  ok(await p.locator('.pchip:not(.add)').count() === 2 && (await personTotals()).reduce((a, b) => a + b, 0) === await heroTotal(), 'removing a person keeps the remaining totals exact');
  await tap('#toast .ta'); await p.waitForTimeout(300);
  ok(await p.locator('.pchip:not(.add)').count() === 3, 'Undo brings the person back');

  // 7. Share summary.
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="share-sum"]');
  const sh = await calls('shareText'); if (!sh.length) console.log('   calls:', JSON.stringify(await ev(() => window.__calls.slice(-4))));
  ok(sh.length === 1 && sh[0][1][0].length > 0, 'share summary calls Android.shareText once');
  const full = await ev(() => summaryText(S.tool.cur, S.tool.cc, compute(S.tool.cur, S.tool.cc)));
  ok(full.split('\n').filter(l => /^(Ana|Person 2|Cleo):/.test(l)).length === 3 && /Bill Split/.test(full) && /Total \$/.test(full) && /largest remainder/.test(full), 'the summary has the total, one line per person and the rounding note');

  // 8. Save to history; free limit 10 -> paywall; Pro grant.
  await tap('[data-act="save-bill"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.history.length) === 1 && /Saved to history/.test(await txt('#toast')), 'save puts the bill in history');
  await tap('[data-act="save-bill"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.history.length) === 1, 'saving the same bill again updates it instead of duplicating');
  await ev(() => { const h = S.tool.history[0]; for (let i = 0; i < 9; i++) S.tool.history.push(Object.assign({}, clone(h), { id: 'f' + i })); persist(); S.tool.cur.savedId = ''; UI.refresh(); });
  await tap('[data-act="save-bill"]'); await p.waitForTimeout(400);
  ok(await ev(() => S.tool.history.length) === 10 && await p.locator('.sheet').count() === 1 && /unlimited/i.test(await txt('.sheet')), 'the 11th bill hits the free limit and opens the Pro paywall');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  await ev(() => UI.closeAll()); await tap('[data-act="save-bill"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && S.tool.history.length === 11), 'after Pro the 11th bill is saved');

  // 9. History list + detail + CSV.
  await tap('[data-act="tab"][data-arg="history"]');
  ok(await p.locator('.prow').count() === 11 && await p.locator('.pbar').count() === 0, 'history lists 11 bills; no free-limit bar for Pro');
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="csv"]');
  const csv = (await calls('shareText'))[0];
  const csvTxt = await ev(() => TOOL.csv());
  ok(csv && /^date,bill,currency,person,items,tax,tip,total/.test(csvTxt) && csvTxt.trim().split('\n').length === 1 + 11 * 3, 'CSV export shares a header + one row per person per bill (' + csvTxt.trim().split('\n').length + ' lines)');
  ok(await ev(() => csvCell('=1+1') === "'=1+1" && csvCell('a,b') === '"a,b"' && csvCell('say "hi"') === '"say ""hi"""'), 'CSV cells are quoted and formula-guarded');
  const rowSum = await ev(() => { const L = TOOL.csv().trim().split('\n').slice(1).map(l => l.split(',')); return L.slice(0, 3).map(c => Math.round(parseFloat(c[7]) * 100)); });
  ok(rowSum.length === 3, 'CSV rows carry decimal totals');
  await tap('.prow'); await p.waitForTimeout(300);
  ok(await p.locator('.hero').count() === 1 && await p.locator('.pcard').count() === 3, 'tapping a bill opens its detail with the per-person results');
  await tap('[data-act="bill-reopen"]'); await p.waitForTimeout(400);
  ok(await ev(() => UI.cur().id) === 'split' && await ev(() => S.tool.cur.savedId) === '' && await p.locator('.irow').count() === 2, 'Edit as a new bill loads it into the Split tab');
  await tap('[data-act="tab"][data-arg="history"]'); await tap('.prow'); await p.waitForTimeout(300);
  await tap('[data-act="bill-del"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.history.length) === 10 && await ev(() => UI.cur().id) === 'history', 'deleting from the detail goes back and removes it');
  await tap('#toast .ta'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.history.length) === 11, 'Undo restores the deleted bill');

  // 10. Groups: create, free limit (Pro off for this part), load into a bill with a confirm.
  await ev(() => { S.pro = false; S.removeAds = false; persist(); });
  await tap('[data-act="tab"][data-arg="groups"]');
  ok(await p.locator('.empty').isVisible(), 'groups starts empty');
  for (let g = 1; g <= 3; g++) {
    await openSheet('[data-act="group-new"]');
    await p.locator('#ed-gname').fill('Group ' + g);
    await p.locator('#gm-0').fill('Ana' + g); await p.locator('#gm-1').fill('Ben' + g);
    await tap('[data-act="g-mem-add"]'); await p.locator('#gm-2').fill('Cy' + g);
    await tap('[data-act="group-save"]'); await p.waitForTimeout(350);
  }
  ok(await ev(() => S.tool.groups.length) === 3 && await p.locator('.prow').count() === 3, 'three groups saved');
  await tap('[data-act="group-new"]'); await p.waitForTimeout(400);
  ok(await p.locator('#ed-gname').count() === 0 && /Unlimited|unlimited/.test(await txt('.sheet')), 'the 4th group opens the paywall on the free plan');
  await ev(() => UI.closeAll());
  await tap('.prow'); await p.waitForTimeout(350);
  await p.locator('#gm-1').fill(''); await tap('[data-act="group-save"]'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.groups[0].members.join()) === 'Ana1,Cy1', 'blank members are dropped on save');
  await tap('.prow'); await p.waitForTimeout(350);
  await tap('[data-act="group-use"]'); await p.waitForTimeout(350);
  ok(await p.locator('.dialog').count() === 1, 'using a group on a bill that has items asks before replacing the people');
  await tap('.dialog .btn-primary'); await p.waitForTimeout(450);
  ok(await ev(() => UI.cur().id) === 'split' && await ev(() => S.tool.cur.people.map(x => x.name).join()) === 'Ana1,Cy1' && await p.locator('.irow .rs.warn').count() === 2, 'the group replaces the people and items wait to be assigned');
  await tap('#toast .ta'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.cur.people.length) === 3, 'Undo restores the previous people');
  await tap('[data-act="people-to-group"]'); await p.waitForTimeout(400);
  ok(await p.locator('.sheet').count() === 1 && /Pro/.test(await txt('.sheet')), 'saving people as a 4th group hits the same limit');
  await ev(() => UI.closeAll());

  // 11. Currency: same exponent keeps cents; JPY rescales; Undo.
  await p.locator('[data-change="b-cur"]').selectOption('EUR'); await p.waitForTimeout(250);
  ok(/€/.test(await txt('.hero .tot')) && await heroTotal() > 0, 'switching to EUR formats the total in euros');
  const before = await ev(() => compute(S.tool.cur, S.tool.cc).total);
  await p.locator('[data-change="b-cur"]').selectOption('JPY'); await p.waitForTimeout(250);
  ok(await ev(() => compute(S.tool.cur, S.tool.cc).total) < before / 50 && /¥|￥/.test(await txt('.hero .tot')), 'JPY has no minor unit: amounts are rescaled, not multiplied by 100');
  const perSum = (await personTotals()).reduce((a, b) => a + b, 0);
  ok(perSum === await heroTotal(), 'JPY totals still add up exactly');
  await tap('#toast .ta'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.cc) === 'EUR' && await ev(() => compute(S.tool.cur, S.tool.cc).total) === before, 'Undo restores the amounts and currency');

  // 12. New bill + Undo.
  await tap('[data-act="new-bill"]'); await p.waitForTimeout(350);
  ok(await p.locator('.irow').count() === 0 && await p.locator('.pchip:not(.add)').count() === 2, 'New bill starts clean');
  await tap('#toast .ta'); await p.waitForTimeout(350);
  ok(await p.locator('.irow').count() === 2, 'Undo brings the draft back');

  // 13. Interstitials: natural breaks only, never first session, owners never.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');
  await ev(() => { S.sessions = 3; Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'later session: one interstitial, then the 3-minute floor holds');
  await ev(() => window.onPurchaseSuccess('remove_ads'));
  ok(await ev(() => S.removeAds === true), 'remove_ads grants ad-free');

  // 14. Backup round trip and import hygiene.
  const backup = await ev(() => Data.payload());
  const snap = await ev(() => JSON.stringify([S.tool.history.length, S.tool.groups.length, S.tool.cur.items.length]));
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('split'); });
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => JSON.stringify([S.tool.history.length, S.tool.groups.length, S.tool.cur.items.length])) === snap, 'backup restores bills, groups and the draft');
  ok(await ev(() => TOOL.validateImport({ cur: { people: [] }, groups: 'x', history: [] })) === false, 'a malformed backup is rejected');
  const mig = await ev(() => { const m = TOOL.migrate({ cc: 'zzz', cur: { people: [{ id: 'a', name: 'A' }], items: [{ id: 'i', c: -5, w: { a: 1 } }, { id: 'j', c: 100, w: { a: 500, ghost: 3 } }, { id: 'k', c: 1.5, w: { a: 1 } }], tax: { mode: 'x', txt: 'abc' } }, history: [{ id: 'h', at: 'x', bill: {} }] }); return [m.cur.items.length, m.cur.items[0].w.a, Object.keys(m.cur.items[0].w).length, m.history.length, m.cc.length]; });
  ok(mig.join() === '1,99,1,0,3', 'migrate drops bad items / orphan weights / bad history and clamps shares');

  // 15. Language: 13 languages complete; Arabic RTL; every screen renders with no missing string; no horizontal overflow.
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13, 'language picker lists 13 languages');
  const gaps = await ev(() => {
    const en = window.GAME_I18N.en, out = [];
    Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => {
      if (k in window.GAME_I18N[l]) return;
      const m = /^(.*)_(one|other)$/.exec(k);
      if (m && (m[1] + '_other') in window.GAME_I18N[l]) return;
      out.push(l + ':' + k);
    }));
    return out;
  });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' — missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.pro = true; S.tool.groups = [{ id: 'g', name: 'G', members: ['A', 'B'] }]; persist(); });
  const over = [];
  for (const l of langs) {
    await ev(L => { S.settings.lang = L === 'en' ? '' : L; persist(); applyLang(); applyTheme(); UI.buildNav(); UI.tab('split'); }, l);
    await p.waitForTimeout(120);
    await ev(() => { UI.tab('groups'); UI.tab('history'); UI.go('bill', { id: S.tool.history[0].id }); UI.back(); UI.tab('split'); });
    await p.waitForTimeout(100);
    for (const open of ['[data-act="item-add"]', '[data-act="person-add"]', '[data-act="load-group"]']) {
      await ev(() => UI.closeAll()); await tap(open); await p.waitForTimeout(350);
      if (await p.locator('.sheet').count() === 0) continue;
    }
    await ev(() => UI.closeAll());
    const w = await ev(() => [document.documentElement.scrollWidth, window.innerWidth, document.getElementById('view').scrollWidth, document.getElementById('view').clientWidth]);
    if (w[2] > w[3] + 1) over.push(l + ':' + w.join('/'));
  }
  const miss = await ev(() => [...window.__i18nMissing]);
  ok(miss.length === 0, 'no untranslated string rendered on Split, Groups, History, Bill or the sheets in any language' + (miss.length ? ': ' + miss.slice(0, 5).join(',') : ''));
  ok(over.length === 0, 'no horizontal overflow at 360px in any language' + (over.length ? ': ' + over.join(' ') : ''));
  await ev(() => { S.settings.lang = 'ar'; persist(); applyLang(); UI.tab('split'); });
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  ok(await ev(() => ['one', 'two', 'few', 'many', 'other'].every(k => 'people_n_' + k in window.GAME_I18N.ar)), 'Arabic has all plural forms for people');
  ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === '1.0.0', 'data-app-version present');

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
