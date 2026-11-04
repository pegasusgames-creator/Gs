#!/usr/bin/env node
// BasicMathKids runtime check -- drives the REAL UI in headless Chromium with the
// shared mocked Android bridge, using real pointer input, and asserts:
//   * a counting round (tap objects to count, a gentle wrong answer) awards stickers
//   * blocks are dragged with a real mouse; ten-frame taps; bead frame drag; number-line hops
//   * a comparing round and a Plus & minus round complete with five stars
//   * adaptive levels rise after correct streaks; free play stays within 10
//   * parental gate refusal, purchase/restore/privacy only behind the gate
//   * NO notification / interstitial / rewarded / sharing / Play Games bridge call, ever
//
//   node BasicMathKids/test/runtime_check.js
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const URL = 'file://' + path.join(REPO, 'BasicMathKids/android/app/src/main/assets/game.html');
const FORBIDDEN = /Interstitial|Rewarded|schedule|Notification|recordLastPlayed|share|submitScore|Leaderboard|PlayGames|logEvent/i;
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const br = await chromium.launch();
  const ctx = await br.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  await ctx.route(/^https?:/, r => r.abort());
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(URL); await p.waitForTimeout(900);
  const ev = (fn, a) => p.evaluate(fn, a);
  const calls = name => ev(n => window.__calls.filter(c => c[0] === n), name);
  async function tap(sel) {
    await p.locator(sel).first().scrollIntoViewIfNeeded({ timeout: 1500 }).catch(() => {});
    const b = await p.locator(sel).first().boundingBox();
    if (!b) throw new Error('not visible: ' + sel);
    await p.mouse.click(b.x + b.width / 2, b.y + b.height / 2); await p.waitForTimeout(420);
  }
  async function hold(sel, ms) {
    const b = await p.locator(sel).first().boundingBox();
    await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await p.mouse.down(); await p.waitForTimeout(ms); await p.mouse.up(); await p.waitForTimeout(400);
  }
  async function drag(from, to) {
    const a = await p.locator(from).first().boundingBox(), b = await p.locator(to).first().boundingBox();
    await p.mouse.move(a.x + a.width / 2, a.y + a.height / 2); await p.mouse.down();
    await p.mouse.move(a.x + a.width / 2 + 20, a.y + a.height / 2 + 20, { steps: 3 });
    await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(350);
  }
  const screen = () => ev(() => KIDS.current());
  const modalOpen = id => ev(i => document.getElementById(i).classList.contains('open'), id);
  const item = () => ev(() => BM.state().item);
  const quiet = () => ev(() => { KIDS.save.settings.voice = false; });
  const answerRight = async () => { const it = await item(); await tap(`#playStage .nopt[data-v="${it.answer}"], #playStage .panel[data-v="${it.answer}"]`); await p.waitForTimeout(1500); };
  async function round(label) {
    for (let i = 0; i < 5; i++) { await answerRight(); }
    await p.waitForTimeout(3600);
    ok(await ev(() => BM.state().stars === 5), label + ': five stars');
  }

  ok(await ev(() => KIDS.ready === true), 'shell boots to home');
  ok((await calls('hideBannerAd')).length + (await calls('showBannerAd')).length > 0, 'banner state synced with native on boot');
  await quiet();

  // 1. Counting: tap objects (real taps), one gentle wrong answer, five stars
  await tap('#homeTiles .tile:nth-child(1)');
  ok(await screen() === 'play' && await ev(() => BM.state().skill === 'count'), 'Count tile opens a counting round');
  ok((await calls('hideBannerAd')).length > 0, 'banner hidden while playing');
  const n0 = (await item()).answer;
  for (let i = 0; i < 3 && i < n0; i++) await tap(`#cnt .cobj:nth-child(${i + 1})`);
  ok(await ev(n => document.querySelectorAll('#cnt .cobj.on').length === Math.min(3, n), n0), 'tapping objects counts them one by one');
  ok(await ev(() => document.querySelector('#cnt .cobj.on .nb').textContent === '1'), 'first object shows 1');
  const wrongV = await ev(() => BM.state().item.options.find(x => x !== BM.state().item.answer));
  await tap(`#playStage .nopt[data-v="${wrongV}"]`);
  ok(await ev(() => BM.state().stars === 0 && BM.state().miss === 1), 'a wrong answer is gentle: no star lost, same question');
  await p.waitForTimeout(6500);
  ok(await ev(() => !BM.state().busy), 'guided counting demo ends and answers work again');
  await round('counting');
  ok(await ev(() => KIDS.save.progress.skills.count.rounds === 1), 'round counted in progress');
  ok(await modalOpen('m-reveal'), 'sticker reveal popup shown'); await tap('#m-reveal [data-act="reveal-ok"]');
  await p.waitForTimeout(700);
  ok(await ev(() => Object.keys(KIDS.save.stickers).some(k => k[0] === 'N') && !!KIDS.save.stickers.S_sun), 'round awards a number sticker and the first friend sticker');
  while (await modalOpen('m-reveal')) { await tap('#m-reveal [data-act="reveal-ok"]'); await p.waitForTimeout(500); }

  // 2. Adaptive + free cap
  ok(await ev(() => KIDS.save.progress.skills.count.lvl === 2), 'four first-try answers in a row raise counting to level 2');
  await ev(() => { KIDS.save.progress.skills.count.lvl = 4; KIDS.save.progress.skills.count.streak = 0; KIDS.go('play', { skill: 'count', seed: 9 }); }); await p.waitForTimeout(400);
  ok(await ev(() => BM.state().lv === 2 && BM.state().item.answer <= 10), 'free play is capped at numbers up to 10');

  // 3. Blocks: real drag with the mouse
  await ev(() => { KIDS.save.progress.skills.add = { lvl: 1 }; KIDS.go('play', { skill: 'add', tool: 'blocks', seed: 5 }); }); await p.waitForTimeout(500);
  const it = await item();
  await drag('#mat .pile[data-zone="pb"] .blk', '#mat .tray');
  ok(await ev(() => document.querySelectorAll('#mat .tray .blk').length === 1 && document.getElementById('cnt').textContent === '1'), 'dragging a block into the tray counts 1');
  await tap('#mat .pile[data-zone="pa"] .blk');
  ok(await ev(() => document.querySelectorAll('#mat .tray .blk').length === 2), 'tapping a block also moves it (no dragging needed)');
  await tap('#mat .tray .blk');
  ok(await ev(() => document.querySelectorAll('#mat .tray .blk').length === 1), 'tapping a block in the tray sends it back');
  await round('blocks add');
  await ev(() => KIDS.go('play', { skill: 'sub', tool: 'blocks', seed: 6 })); await p.waitForTimeout(500);
  const sub = await item(); const total = sub.a;
  await drag('#mat .pile[data-zone="gr"] .blk', '#mat .tray[data-zone="bag"]');
  ok(await ev(t => document.getElementById('cnt').textContent === String(t - 1), total), 'dragging a block into the bag leaves one fewer');

  // 4. Ten-frame, beads, number line
  await ev(() => KIDS.go('play', { skill: 'add', tool: 'frame', seed: 2 })); await p.waitForTimeout(500);
  const f = await item(); const startN = await ev(() => document.getElementById('cnt').textContent);
  await tap('#manip .cell:not(.on)');
  ok(await ev(s => document.getElementById('cnt').textContent === String(+s + 1), startN), 'tapping an empty ten-frame cell adds a counter');
  await ev(() => KIDS.go('play', { skill: 'add', tool: 'beads', seed: 3 })); await p.waitForTimeout(500);
  const bead0 = await ev(() => BM.manip().act);
  const rb = await p.locator('#rek .rk-row').first().boundingBox();
  await p.mouse.move(rb.x + rb.width * 0.3, rb.y + rb.height / 2); await p.mouse.down(); await p.mouse.move(rb.x + rb.width * 0.8, rb.y + rb.height / 2, { steps: 8 }); await p.mouse.up();
  ok(await ev(b => BM.manip().act > b && document.getElementById('cnt').textContent === String(BM.manip().act), bead0), 'dragging along the bead wire slides beads and updates the count');
  await ev(() => KIDS.go('play', { skill: 'line', tool: 'line', seed: 4, op: '+' })); await p.waitForTimeout(500);
  await tap('#hopBtn');
  ok(await ev(() => BM.manip().hops === 1 && BM.manip().pos === BM.state().item.a + 1), 'Hop moves the number-line marker one step');

  // 5. Comparing
  await ev(() => { KIDS.save.progress.skills.compare = { lvl: 1 }; KIDS.go('play', { skill: 'compare', seed: 8 }); }); await p.waitForTimeout(500);
  await round('comparing');
  await ev(() => { KIDS.save.progress.skills.compare = { lvl: 2 }; KIDS.save.progress.skills.compare.streak = 0; });

  // 6. A ready free player sees the lock card that asks a grown-up (never the store)
  await ev(() => { const s = KIDS.save.progress.skills; s.add = { lvl: 2, streak: 3, rounds: 0, trouble: 0, items: 0 }; KIDS.go('play', { skill: 'add', tool: 'blocks', seed: 12 }); }); await p.waitForTimeout(500);
  await round('free add');
  ok(await ev(() => !!document.querySelector('[data-act="more-nums"]')), 'ready free player gets the "bigger numbers" lock button');
  while (await modalOpen('m-reveal')) { await tap('#m-reveal [data-act="reveal-ok"]'); await p.waitForTimeout(500); }
  await tap('[data-act="more-nums"]');
  ok(await modalOpen('m-ask'), 'locked bigger numbers ask for a grown-up');
  await tap('#m-ask [data-act="ask-parent"]'); await p.waitForTimeout(300);
  ok(await modalOpen('m-gate'), 'grown-up button opens the parental gate');
  ok((await calls('purchase')).length === 0, 'no store call from the lock card');

  // ── 4. Gate refuses a wrong answer ───────────────────────────────────────
  const wrongAns = await ev(() => [...document.querySelectorAll('.gopt')].map(b => +b.dataset.v).find(v => v !== Gate.ans));
  await hold(`.gopt[data-v="${wrongAns}"]`, 1700);
  ok(!(await modalOpen('m-gate')), 'wrong answer closes the gate');
  ok(await screen() !== 'parent', 'wrong answer does NOT open the parent area');
  ok(await ev(() => !Gate.ok()), 'gate stays locked after a wrong answer');
  // a short tap on the right answer is not enough (press-and-hold required)
  await ev(() => KIDS.go('home')); await p.waitForTimeout(300); await tap('#btnGrownups');
  let ans = await ev(() => Gate.ans);
  await tap(`.gopt[data-v="${ans}"]`);
  ok(await screen() !== 'parent' && await modalOpen('m-gate'), 'a quick tap on the right answer is not enough');
  await hold(`.gopt[data-v="${ans}"]`, 1700);
  ok(await screen() === 'parent', 'holding the right answer opens the parent area');
  ok((await calls('purchase')).length === 0 && (await calls('openUrl')).length === 0, 'no store / link call before a grown-up action');

  // ── 5. Purchase + grant ──────────────────────────────────────────────────
  await tap('#prodList [data-id="full_pack"]');
  ok((await calls('purchase')).some(c => c[1][0] === 'full_pack'), 'Buy (behind the gate) launches billing for full_pack');
  await ev(() => window.onPurchaseSuccess('full_pack')); await p.waitForTimeout(300);
  ok(await ev(() => KIDS.save.fullPack === true && KIDS.save.removeAds === true), 'onPurchaseSuccess(full_pack) unlocks everything + removes ads');
  ok((await calls('hideBannerAd')).length > 0, 'banner hidden after purchase');
  ok(await ev(() => document.querySelector('#prodList [data-id="full_pack"]').disabled), 'shop shows full_pack as owned');
  await tap('#scr-parent [data-act="privacy"]');
  ok((await calls('openUrl')).some(c => c[1][0] === 'https://pegasusgames-creator.github.io/privacy-kids.html'), 'privacy link (behind the gate) opens the KIDS policy');

  // ── 6. Leaving re-locks; restore needs the gate again ────────────────────
  await tap('#scr-parent [data-act="back"]');
  const before = (await calls('purchase')).length;
  await ev(() => gatedNative('purchase', 'remove_ads')); await p.waitForTimeout(200);
  ok((await calls('purchase')).length === before && await modalOpen('m-gate'), 'after leaving, a store call re-opens the gate instead');
  await ev(() => Gate.cancel()); await p.waitForTimeout(300);
  await tap('#btnGrownups'); ans = await ev(() => Gate.ans); await hold(`.gopt[data-v="${ans}"]`, 1700);
  await tap('#btnRestore');
  ok((await calls('restorePurchases')).length === 1, 'Restore purchases (behind the gate) calls the bridge');
  await ev(() => { KIDS.save.removeAds = false; KIDS.save.fullPack = false; window.onPurchaseSuccess('remove_ads'); window.onPurchaseSuccess('full_pack'); });
  ok(await ev(() => KIDS.save.removeAds && KIDS.save.fullPack), 'restored SKUs re-grant (idempotent)');
  await ev(() => window.onPurchaseSuccess('coins_small'));
  ok(await ev(() => !!JSON.parse(localStorage.getItem('pendingGrants') || '{}').coins_small), 'unknown SKU is parked in pendingGrants (never dropped)');
  ok(await ev(() => KIDS.full()), 'full_pack makes full() true');
  await ev(() => KIDS.go('play', { skill: 'add', tool: 'frame', seed: 1 })); await p.waitForTimeout(300);
  ok(await ev(() => BM.state().item.max >= 5 && BM.state().lv === Math.min(BM.state().lv, 4)), 'full pack: play still works');

  // ── 7. Families: forbidden bridge calls never happen ─────────────────────
  const all = await ev(() => window.__calls.map(c => c[0]));
  const bad = [...new Set(all.filter(n => FORBIDDEN.test(n)))];
  ok(bad.length === 0, 'no notification / interstitial / rewarded / share / Play Games call' + (bad.length ? ' — got ' + bad.join(', ') : ''));
  ok(errs.length === 0, 'no page errors' + (errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''));

  await br.close();
  console.log(fails ? `BasicMathKids runtime check: ${fails} failure(s)` : 'BasicMathKids runtime check: OK');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
