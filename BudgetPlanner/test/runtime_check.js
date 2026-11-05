#!/usr/bin/env node
// BudgetPlanner runtime check — drives the REAL UI in headless Chromium with the mocked Android bridge and real
// input events: onboarding -> starter envelopes -> income -> assign (left to assign hits zero) -> spend ->
// overspend warning -> move money to cover -> rollover to the next month -> bills (reminder + mark paid + Undo) ->
// goals (monthly amount, contribute) -> months comparison -> Pro limits + paywall -> CSV -> backup round trip ->
// i18n completeness in all 13 languages, RTL, no overflow.
//   node BudgetPlanner/test/runtime_check.js        (exit 1 on any failure)
// The envelope maths itself is gated by scripts/check_budgetplanner_math.py.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'BudgetPlanner/android/app/src/main/assets/game.html');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const SHOTS = process.env.SHOTS || '';
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 360, height: 640 }, isMobile: true, hasTouch: true, locale: 'en-US' });
  await ctx.addInitScript(mock);
  await ctx.addInitScript(() => { window.__fakeNow = new Date(2026, 10, 15, 10, 0, 0).getTime(); });   // 15 Nov 2026
  const p = await ctx.newPage();
  p.setDefaultTimeout(6000);
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(220); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  const txt = async (sel) => (await p.locator(sel).first().innerText()).replace(/\s+/g, ' ').trim();
  const shot = async n => { if (SHOTS) { fs.mkdirSync(SHOTS, { recursive: true }); await p.screenshot({ path: path.join(SHOTS, n + '.png') }); } };
  const fill = async (sel, v) => { await p.locator(sel).first().fill(v); await p.waitForTimeout(80); };
  const sheet = async () => { await p.waitForSelector('.sheet'); await p.waitForTimeout(350); };
  const num = s => parseInt(String(s).replace(/[^\d-]/g, ''), 10);
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. First launch.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await shot('00_onboarding');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(!(await p.locator('#onb').count()), 'onboarding completes');
  ok(await p.locator('[data-act="tab"]').count() === 4, 'four tabs: Plan, Bills, Goals, Months');
  ok(await p.locator('#view .empty').isVisible(), 'empty plan shows the empty state');
  await shot('01_empty');

  // 2. Starter envelopes, income, assigning to zero.
  await tap('[data-act="env-starter"]');
  ok(await p.locator('.bper').count() === 6, 'starter envelopes add six envelopes');
  await tap('#toast .ta'); ok(await p.locator('.bper').count() === 0, 'Undo removes the starter envelopes');
  await tap('[data-act="env-starter"]'); await ev(() => UI.closeLayer && 0);
  await tap('[data-act="inc-add"]'); await sheet();
  await fill('#ed-name', 'Paycheck'); await fill('#ed-amt', '3,000');
  await tap('[data-act="inc-save"]');
  ok(await txt('.bphero .tot') === '$3,000.00', 'Left to assign shows the whole income before assigning');
  const assign = async (i, v) => { await p.locator('[data-act="env-assign"]').nth(i).tap(); await sheet(); await fill('#ed-amt', v); await tap('[data-act="assign-save"]'); await p.waitForTimeout(250); };
  await assign(0, '1200'); await assign(1, '500'); await assign(2, '200'); await assign(3, '300');
  ok(await txt('.bphero .tot') === '$800.00', 'Left to assign falls as envelopes are planned');
  await p.locator('[data-act="env-assign"]').nth(4).tap(); await sheet();
  await tap('[data-act="assign-all"]'); await tap('[data-act="assign-save"]'); await p.waitForTimeout(250);
  ok(await txt('.bphero .tot') === '$0.00' && /job/i.test(await txt('.bphero .sub')), 'assigning the rest leaves $0.00 and says every bit has a job');
  await shot('02_assigned');
  const bad = await ev(() => { const r = calc(curKey()); return [r.assigned + r.left, r.income]; });
  ok(bad[0] === bad[1] && bad[0] === 300000, 'assigned + left equals income in the live data');
  await assign(5, '100');
  ok(/Over-assigned by \$100\.00/.test(await txt('.bphero .sub')), 'over-assigning is called out');
  await assign(5, '0');

  // 3. Spending, warnings, moving money.
  await tap('[data-act="env-open"][data-arg]'); await p.waitForTimeout(300);   // first envelope (Rent)
  ok(await txt('.bphero .tot') === '$1,200.00', 'envelope detail shows what is available');
  await tap('[data-act="sp-env-new"]'); await sheet();
  await fill('#ed-amt', '1,300'); await fill('#ed-note', 'Rent + late fee');
  await tap('[data-act="sp-save"]');
  ok(/over by \$100\.00/i.test(await txt('#toast')), 'overspending shows an over-by warning with the amount');
  ok(await txt('.bphero .tot') === '-$100.00' || /100\.00/.test(await txt('.bphero .tot')), 'available goes negative');
  await shot('03_over');
  ok(await p.locator('.bptx').count() === 1, 'the spending appears in the envelope activity');
  await tap('[data-act="mv-env"]'); await sheet();
  await tap('[data-act="mv-save"]'); ok(/Enter an amount/.test(await txt('#toast')), 'moving needs an amount');
  await tap('[data-act="mv-cover"]'); await tap('[data-act="mv-save"]');
  const tot1 = await ev(() => { const r = calc(curKey()); return [r.total, r.overN, r.spent]; });
  ok(tot1[0] === 300000 - 130000 && tot1[1] === 0 && tot1[2] === 130000, 'moving money covers the overspend and keeps the total');
  await tap('[data-act="mv-env"]'); await sheet();
  await fill('#ed-amt', '99999'); await tap('[data-act="mv-save"]');
  ok(/only has/.test(await txt('#toast')), 'moving more than is available is refused');
  await ev(() => UI.closeAll());
  await p.locator('[data-act="tx-del"]').first().tap(); await p.waitForTimeout(250);
  await tap('#toast .ta'); ok(await p.locator('.bptx').count() >= 1, 'deleting an entry can be undone');
  await ev(() => UI.back()); await p.waitForTimeout(300);

  // 4. Rollover to next month: carry vs reset.
  await ev(() => { S.tool.envs[1].roll = 'carry'; S.tool.envs[2].roll = 'reset'; persist(); });
  await ev(() => { const m = mdata(curKey(), true); m.spend.push({ id: 'sx1', e: S.tool.envs[1].id, c: 20000, d: curKey() + '-03', note: '' }); m.spend.push({ id: 'sx2', e: S.tool.envs[2].id, c: 5000, d: curKey() + '-04', note: '' }); persist(); });
  const nxt = await ev(() => { const k = shiftKey(curKey(), 1), r = calc(k); return { carry: r.rows.map(x => x.carry), freed: r.freed, total: r.total }; });
  ok(nxt.carry[1] === 30000 && nxt.carry[2] === 0, 'a carry envelope hands its leftover on, a reset one does not');
  ok(nxt.total === 300000 - 130000 - 25000, 'rollover leaves the total untouched');
  await tap('[data-act="tab"][data-arg="plan"]'); await tap('[data-act="m-next"]');
  ok(await p.locator('.bphero').count() === 1 && /December 2026/.test(await txt('.bpmt')), 'next month can be planned');
  ok(await p.locator('[data-act="copy-prev"]').count() === 1, 'an empty next month offers to start from this month');
  await tap('[data-act="copy-prev"]');
  ok(await p.locator('.bper').count() === 6 && await ev(() => calc(shiftKey(curKey(), 1)).assigned) === 300000, 'copy-prev fills income and plan');
  const cp = await ev(() => { const r = calc(shiftKey(curKey(), 1)); return r.assigned + r.left === r.income + r.freed; });
  ok(cp, 'assigned + left = income + freed next month');
  await shot('04_next_month');
  await tap('#toast .ta'); ok(await p.locator('[data-act="copy-prev"]').count() === 1, 'Undo restores the empty month');
  await tap('[data-act="m-today"]');
  ok(await p.locator('[data-act="m-next"][disabled]').count() === 0, 'back on this month');
  await tap('[data-act="m-next"]');
  ok(await p.locator('[data-act="m-next"][disabled]').count() === 1, 'planning is limited to one month ahead');
  await tap('[data-act="m-today"]');

  // 5. Spread what is left.
  await ev(() => { S.tool.months[curKey()].income.push({ id: 'ix', name: 'Gift', c: 10001 }); persist(); UI.refresh(); });
  await tap('[data-act="spread"]');
  const sp = await ev(() => { const r = calc(curKey()); return [r.left, r.assigned + r.left === r.income]; });
  ok(sp[0] === 0 && sp[1], 'spreading what is left assigns every cent, rounding included');
  await tap('#toast .ta'); ok(await ev(() => calc(curKey()).left) === 10001, 'Undo restores the unassigned amount');

  // 6. Bills with dated reminders.
  await tap('[data-act="tab"][data-arg="bills"]');
  ok(await p.locator('#view .empty').isVisible(), 'empty bills state');
  await tap('[data-act="bill-new"]'); await sheet();
  await fill('#ed-name', 'Phone'); await fill('#ed-amt', '45.50');
  await p.locator('#bl-day').selectOption('20'); await p.locator('#bl-env').selectOption({ index: 3 });
  await tap('[data-act="bl-lead"][data-arg="1"]');
  await tap('[data-act="bill-save"]'); await p.waitForTimeout(300);
  const dr = await calls('scheduleDatedReminder');
  ok(dr.length >= 1, 'saving a bill with a reminder schedules a dated reminder');
  const when = new Date(dr[dr.length - 1][1][1]);
  ok(when.getMonth() === 10 && when.getDate() === 19 && when.getHours() === 9, 'the reminder is for 09:00 the day before the due day (19 Nov)');
  ok(await p.locator('.bper').count() === 1 && /Days left: 5/.test(await txt('.bpchip')), 'the bill shows days left');
  await shot('05_bills');
  const spentBefore = await ev(() => calc(curKey()).spent);
  await tap('[data-act="bill-pay"]');
  ok(await p.locator('.bpchip.ok').count() === 1, 'mark paid shows Paid');
  ok(await ev(() => calc(curKey()).spent) === spentBefore + 4550, 'paying a bill records its amount as spending in its envelope');
  await tap('#toast .ta');
  ok(await ev(() => calc(curKey()).spent) === spentBefore && await p.locator('.bpchip.ok').count() === 0, 'Undo removes the payment');
  await tap('[data-act="bill-pay"]');
  const dr2 = await ev(() => [S.tool.bills[0].paid[curKey()] != null, billNext(S.tool.bills[0]).due.getMonth()]);
  ok(dr2[0] && dr2[1] === 11, 'after paying, the next reminder is for next month');
  await ev(() => { S.tool.bills[0].day = 31; }); 
  ok(await ev(() => billDue(S.tool.bills[0], 2026 * 12 + 10).getDate()) === 30, 'a day-31 bill falls on the 30th in November');
  ok(await ev(() => billDue(S.tool.bills[0], 2028 * 12 + 1).getDate()) === 29, '... and on the 29th in February of a leap year');
  await ev(() => { S.tool.bills[0].day = 20; });

  // 7. Goals.
  await tap('[data-act="tab"][data-arg="goals"]');
  await tap('[data-act="goal-new"]'); await sheet();
  await fill('#ed-name', 'Trip'); await fill('#ed-amt', '1000');
  await p.locator('[data-change="gl-m"]').selectOption('1'); await p.locator('[data-change="gl-y"]').selectOption('2027');
  ok(/\$250\.00 a month/.test(await txt('#gl-prev')), 'the sheet previews the monthly amount (Nov 2026 to Feb 2027 = 4 months)');
  await tap('[data-act="goal-save"]');
  ok(/\$250\.00 a month/.test(await txt('.bpneed')), 'the goal card shows the monthly amount needed');
  await ev(() => { S.tool.goals[0].target = 100000; S.tool.goals[0].due = '2027-01'; persist(); UI.refresh(); });
  ok(/\$333\.34 a month/.test(await txt('.bpneed b')) && /last month \$333\.33/.test(await txt('.bpneed small')), 'uneven goals round up and the last month takes the remainder');
  await tap('[data-act="goal-add"]'); await sheet();
  await tap('[data-act="contrib-month"]'); await tap('[data-act="contrib-save"]');
  ok(await ev(() => S.tool.goals[0].saved) === 33334, 'contributing this month\'s share adds it to the goal');
  ok(/\$222\.22 a month/.test(await txt('.bpneed b')), 'the monthly amount drops after contributing');
  await shot('06_goals');
  await tap('#toast .ta');
  await ev(() => { S.tool.goals[0].due = '2026-09'; persist(); UI.refresh(); });
  ok(/Target date passed/.test(await txt('.bpgf')), 'a goal past its date says so');
  await ev(() => { S.tool.goals[0].due = '2027-01'; S.tool.goals[0].saved = 100000; persist(); UI.refresh(); });
  ok(/Goal reached/.test(await txt('.bpgf')), 'a funded goal is marked reached');
  await ev(() => { S.tool.goals[0].saved = 0; persist(); });

  // 8. Months comparison.
  await ev(() => { const k = shiftKey(curKey(), -1), m = mdata(k, true); m.income.push({ id: 'p1', name: '', c: 280000 }); m.plan[S.tool.envs[1].id] = 40000; m.spend.push({ id: 'p2', e: S.tool.envs[1].id, c: 10000, d: k + '-05', note: '' }); persist(); });
  await tap('[data-act="tab"][data-arg="months"]');
  ok(await p.locator('.bpcmp .row').count() >= 4 && await p.locator('.bpmr').count() === 2, 'Months compares this month with last and lists both months');
  await shot('07_months');

  // 9. Free limits and the paywall.
  await ev(() => { S.pro = false; S.removeAds = false; persist(); while (S.tool.envs.length < 8) S.tool.envs.push({ id: 'z' + S.tool.envs.length, name: 'Z' + S.tool.envs.length, roll: 'reset', color: 0 }); persist(); });
  await tap('[data-act="tab"][data-arg="plan"]'); await tap('[data-act="env-new"]');
  ok(await p.locator('.pro-sheet').count() === 1 || await p.locator('.pro-hero').count() === 1, 'the 9th envelope opens the Pro paywall');
  ok(/up to 8 envelopes/.test(await txt('.pro-hero p')), '... with the envelope reason');
  await ev(() => UI.closeAll());
  await ev(() => { while (S.tool.goals.length < 3) S.tool.goals.push({ id: 'g' + S.tool.goals.length, name: 'G', target: 1000, saved: 0, due: '2027-06' }); persist(); });
  await ev(() => { UI.tab('goals'); }); await tap('[data-act="goal-new"]');
  ok(await p.locator('.pro-hero').count() === 1, 'the 4th goal opens the Pro paywall');
  await ev(() => UI.closeAll());
  await ev(() => { TD.m = curKey(); UI.tab('plan'); });
  await tap('[data-act="m-prev"]'); await tap('[data-act="m-prev"]');
  ok(/October|September|Oct|Sep/.test(await txt('.bpmt')) && await p.locator('.pro-hero').count() === 0, 'the last 3 months are free');
  await tap('[data-act="m-prev"]');
  ok(await p.locator('.pro-hero').count() === 1 && /last 3 months/.test(await txt('.pro-hero p')), 'older months open the Pro paywall');
  await ev(() => UI.closeAll());
  await ev(() => { window.__calls.length = 0; S.sessions = 3; S.ads = { last: 0, breaks: 0 }; });
  await ev(() => { window.onPurchaseSuccess('pro_lifetime'); });
  ok(await ev(() => S.pro === true && isPro()), 'pro_lifetime grants Pro');
  await ev(() => { TD.m = curKey(); UI.tab('plan'); UI.tab('months'); });
  ok(await p.locator('.bpmr').count() >= 2, 'Pro shows the whole history');
  await ev(() => { UI.tab('plan'); }); await tap('[data-act="env-new"]');
  ok(await p.locator('.pro-hero').count() === 0 && await p.locator('#ed-name').count() === 1, 'Pro has no envelope limit');
  await ev(() => UI.closeAll());
  const csv = await ev(() => TOOL.csv());
  ok(/^month,type,envelope,date,amount,note/.test(csv) && /Rent \+ late fee/.test(csv) && /income,,,3000\.00,Paycheck/.test(csv), 'CSV export holds income, plans and spending');
  ok(await ev(() => buildCsv.length >= 0 && csvCell('=SUM(A1)') === "'=SUM(A1)"), 'CSV cells are formula-guarded');

  // 10. Currency: a zero-decimal currency rescales, Undo restores.
  const before = await ev(() => JSON.stringify(S.tool));
  await ev(() => { UI.go('settings'); });
  await p.waitForTimeout(250);
  await p.locator('[data-change="b-cur"]').selectOption('JPY'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.cc) === 'JPY' && await ev(() => S.tool.goals[0].target) === 1000, 'changing to a zero-decimal currency rescales amounts');
  await tap('#toast .ta');
  ok(await ev(() => JSON.stringify(S.tool)) === before, 'Undo restores every amount exactly');
  await ev(() => { UI.back(); });

  // 11. Backup round trip and import hygiene.
  const backup = await ev(() => Data.payload());
  const snap = await ev(() => JSON.stringify([S.tool.envs.length, Object.keys(S.tool.months).length, S.tool.bills.length, S.tool.goals.length]));
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('plan'); });
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => JSON.stringify([S.tool.envs.length, Object.keys(S.tool.months).length, S.tool.bills.length, S.tool.goals.length])) === snap, 'backup restores envelopes, months, bills and goals');
  ok(await ev(() => TOOL.validateImport({ envs: 'x', months: {}, bills: [], goals: [] })) === false, 'a malformed backup is rejected');
  const mig = await ev(() => { const m = TOOL.migrate({ cc: 'zzz', envs: [{ id: 'a', name: 'A', roll: 'x' }, { id: 'a', name: 'dup' }],
    months: { '2026-11': { income: [{ c: -5 }, { id: 'i', c: 100 }], plan: { a: 50, ghost: 7 }, spend: [{ e: 'ghost', c: 5 }, { id: 's', e: 'a', c: 5, d: 'bad' }], moves: [{ f: 'a', t: 'a', c: 5 }] }, 'bad-key': {} },
    bills: [{ id: 'b', c: 100, day: 99, env: 'ghost', lead: 7 }], goals: [{ id: 'g', target: 0, due: '2027-01' }, { id: 'h', target: 10, due: 'x' }] });
    const mo = m.months['2026-11']; return [m.envs.length, m.envs[0].roll, Object.keys(m.months).length, mo.income.length, Object.keys(mo.plan).length, mo.spend.length, mo.spend[0].d, mo.moves.length, m.bills[0].day, m.bills[0].env === '', m.bills[0].lead, m.goals.length]; });
  ok(mig.join() === '1,reset,1,1,1,1,2026-11-01,0,31,true,-1,0', 'migrate drops bad rows, orphans and bad dates and clamps values: ' + mig.join());

  // 12. Interstitials: natural breaks only.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');

  // 13. Languages.
  const langs = await ev(() => Object.keys(window.LANG_NAMES));
  ok(langs.length === 13, 'language picker lists 13 languages');
  const gaps = await ev(() => {
    const en = window.GAME_I18N.en, out = [];
    Object.keys(window.LANG_NAMES).forEach(l => Object.keys(en).forEach(k => { if (!(k in window.GAME_I18N[l])) out.push(l + ':' + k); }));
    return out;
  });
  ok(gaps.length === 0, 'every string is translated in all 13 languages' + (gaps.length ? ' — missing ' + gaps.slice(0, 6).join(', ') : ''));
  await ev(() => { S.pro = true; persist(); });
  const over = [];
  for (const l of langs) {
    await ev(L => { S.settings.lang = L === 'en' ? '' : L; persist(); applyLang(); applyTheme(); UI.buildNav(); TD.m = curKey(); UI.tab('plan'); }, l);
    await p.waitForTimeout(120);
    await ev(() => { UI.tab('bills'); UI.tab('goals'); UI.tab('months'); UI.go('env', { id: S.tool.envs[0].id }); UI.back(); UI.tab('plan'); });
    await p.waitForTimeout(100);
    for (const open of ['sp-new', 'mv-new', 'inc-add', 'env-new']) {
      await ev(() => UI.closeAll()); await ev(a => ACT[a](document.body), open); await p.waitForTimeout(300);
    }
    await ev(() => { UI.closeAll(); openBill(S.tool.bills[0] && S.tool.bills[0].id); }); await p.waitForTimeout(300);
    await ev(() => { UI.closeAll(); openGoal(S.tool.goals[0] && S.tool.goals[0].id); }); await p.waitForTimeout(300);
    await ev(() => UI.closeAll());
    const w = await ev(() => [document.getElementById('view').scrollWidth, document.getElementById('view').clientWidth]);
    if (w[0] > w[1] + 1) over.push(l + ':' + w.join('/'));
    if (SHOTS && (l === 'ar' || l === 'ja' || l === 'de')) await shot('lang_' + l);
  }
  const miss = await ev(() => [...window.__i18nMissing]);
  ok(miss.length === 0, 'no untranslated string rendered in any language' + (miss.length ? ': ' + miss.slice(0, 5).join(',') : ''));
  ok(over.length === 0, 'no horizontal overflow at 360px in any language' + (over.length ? ': ' + over.join(' ') : ''));
  await ev(() => { S.settings.lang = 'ar'; persist(); applyLang(); UI.tab('plan'); });
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  { const vn = (fs.readFileSync(path.join(__dirname, '../android/app/build.gradle'), 'utf8').match(/versionName "([^"]+)"/) || [])[1];
    ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === vn, 'data-app-version matches versionName'); }

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
