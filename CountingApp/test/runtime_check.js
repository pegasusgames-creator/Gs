#!/usr/bin/env node
// CountingApp runtime check — drives the REAL UI in headless Chromium with the
// shared mocked Android bridge (scripts/runtime/mock_bridge.js), using real
// pointer input, and asserts the kids-shell contract:
//   * tracing a letter stroke-by-stroke completes it and awards its sticker
//   * a full "Find the letter" round (with a gentle wrong tap) awards a star sticker
//   * locked content asks for a grown-up and never reaches the store
//   * the parental gate refuses a wrong answer (no parent area, no store call)
//   * purchase only after the gate; onPurchaseSuccess grants full_pack / remove_ads
//   * restore + privacy link only after the gate; leaving the parent area re-locks it
//   * NO notification / interstitial / rewarded / sharing / Play Games bridge call, ever
//
//   node CountingApp/test/runtime_check.js
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const URL = 'file://' + path.join(REPO, 'CountingApp/android/app/src/main/assets/game.html');
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
  const screen = () => ev(() => KIDS.current());
  const modalOpen = id => ev(i => document.getElementById(i).classList.contains('open'), id);

  ok(await ev(() => KIDS.ready === true), 'shell boots to home');
  ok((await calls('hideBannerAd')).length + (await calls('showBannerAd')).length > 0, 'banner state synced with native on boot');

  // ── 1. Tap-to-count 3 with real taps ─────────────────────────────────────
  await tap('#homeTiles .tile:nth-child(1)');
  ok(await screen() === 'count', 'Count tile opens the number hub');
  await tap('[data-n="3"]');
  ok(await screen() === 'counter', 'tapping 3 opens the counting scene');
  ok(await ev(() => document.querySelectorAll('#cGrid .obj').length === 3), 'the scene shows exactly 3 objects');
  ok((await calls('hideBannerAd')).length > 0, 'banner state synced');
  for (let i = 0; i < 3; i++) await tap(`#cGrid .obj:nth-child(${i + 1})`);
  ok(await ev(() => document.querySelector('#ctNum').textContent === '3' && [...document.querySelectorAll('#cGrid .obj .cnum')].map(e => e.textContent).join() === '1,2,3'), 'each tap numbers its object 1, 2, 3');
  await p.waitForTimeout(4600);
  ok(await ev(() => KIDS.hasSticker('N_3')), 'counting all 3 awards the number sticker');
  ok(await modalOpen('m-reveal'), 'sticker reveal popup shown');
  await tap('#m-reveal [data-act="reveal-ok"]');
  ok(!(await modalOpen('m-reveal')), 'reveal popup closes on tap');
  await ev(() => KIDS.go('counter', { n: 20 })); await p.waitForTimeout(400);
  ok(await ev(() => document.querySelectorAll('#cGrid .obj').length === 20), '20 shows exactly 20 objects');

  // ── 2. Trace the digit 1 with a real finger drag ─────────────────────────
  await ev(() => KIDS.go('home')); await p.waitForTimeout(300);
  await tap('#homeTiles .tile:nth-child(3)');
  ok(await screen() === 'digits', 'Trace tile opens the digit grid');
  await tap('[data-d="1"]');
  ok(await screen() === 'trace', 'tapping 1 opens tracing');
  ok((await calls('hideBannerAd')).length > 0, 'banner hidden while tracing');
  const nStrokes = await ev(() => CF_TRACE.state().strokes.length);
  for (let i = 0; i < nStrokes; i++) {
    const pts = await ev(k => {
      const s = document.getElementById('trSvg'), m = s.getScreenCTM();
      return CF_TRACE.points(k).map(q => { const pt = s.createSVGPoint(); pt.x = q.x; pt.y = q.y; const r = pt.matrixTransform(m); return [r.x, r.y]; });
    }, i);
    await p.mouse.move(pts[0][0] + 4, pts[0][1] + 3); await p.mouse.down();
    for (let k = 0; k < pts.length; k++) await p.mouse.move(pts[k][0] + (k % 2 ? 5 : -5), pts[k][1] + (k % 3 ? 3 : -4));
    await p.mouse.up(); await p.waitForTimeout(250);
  }
  ok(await ev(() => !!KIDS.save.progress.traced['1']), '1 traced and saved');
  ok(await ev(() => document.getElementById('trStage').classList.contains('done')), 'tracing shows the done state');
  await p.waitForTimeout(4600);
  ok(await ev(() => !!KIDS.save.stickers.D_1), 'tracing 1 awards its sticker');
  await tap('#m-reveal [data-act="reveal-ok"]');
  await tap('#scr-trace [data-act="tr-again"]');
  await p.mouse.move(30, 690); await p.mouse.down(); await p.mouse.move(380, 700, { steps: 12 }); await p.mouse.up();
  ok(await ev(() => CF_TRACE.state().si === 0 && CF_TRACE.state().strokes[0].idx < 3), 'off-path scribble is ignored (no progress, no penalty)');

  // ── 3. One "How many?" round with real taps ──────────────────────────────
  await tap('#scr-trace [data-act="back"]'); await tap('#scr-digits [data-act="back"]');
  await tap('#homeTiles .tile:nth-child(4)');
  ok(await screen() === 'games', 'Games tile opens the games hub');
  await tap('[data-g="howmany"]');
  ok(await screen() === 'play', 'How many? starts');
  const wrong = await ev(() => CF_GAME.state().rd.options.find(x => x !== CF_GAME.state().rd.answer));
  await tap(`#playStage [data-act="ans"][data-v="${wrong}"]`);
  ok(await ev(() => CF_GAME.state().stars === 0 && CF_GAME.state().miss === 1), 'a wrong tap is gentle: no star lost, same question');
  for (let i = 0; i < 5; i++) {
    const info = await ev(() => { const r = CF_GAME.state().rd; return { a: r.answer, shown: document.querySelectorAll('#playStage .cluster .obj').length, lv: r.level }; });
    ok(info.shown === info.a && info.a <= 5, `turn ${i + 1}: ${info.shown} objects shown = answer ${info.a} (level ${info.lv} range)`);
    await tap(`#playStage [data-act="ans"][data-v="${info.a}"]`); await p.waitForTimeout(3600);
  }
  ok(await ev(() => KIDS.save.progress.rounds === 1), 'round finished and counted');
  await p.waitForTimeout(3600);
  ok(await ev(() => Object.keys(KIDS.save.stickers).some(k => k.indexOf('S_') === 0)), 'finishing a round awards a sea sticker');
  await tap('#m-reveal [data-act="reveal-ok"]');

  // ── 3b. Locked content -> ask a grown-up (never the store) ───────────────
  for (const [setup, sel, what] of [
    ["KIDS.go('songs')", '[data-s="5"]', 'the 5s song'],
    ["KIDS.go('count')", '[data-act="pick-hundred"]', 'counting to 100'],
    ["KIDS.go('games')", '[data-g="make"]', 'Make the number'],
    ["KIDS.go('games')", '[data-g="next"]', 'What comes next?']]) {
    await ev(setup); await p.waitForTimeout(300);
    const before = await screen();
    await tap(sel);
    ok(await modalOpen('m-ask') && await screen() === before, `locked ${what} asks for a grown-up and does not open`);
    await ev(() => Modal.close('m-ask')); await p.waitForTimeout(250);
  }
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="make"]'); await tap('#m-ask [data-act="ask-parent"]'); await p.waitForTimeout(300);
  ok(await modalOpen('m-gate'), 'grown-up button opens the parental gate');

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
  // full_pack: counting to 100, the 5s song and the other games open and work
  await ev(() => KIDS.go('count')); await p.waitForTimeout(300);
  await tap('[data-act="pick-hundred"]');
  ok(await screen() === 'hundred', 'counting to 100 opens after full_pack');
  await tap('[data-act="h-ten"]'); await tap('[data-act="h-ten"]'); await tap('[data-act="h-one"]');
  ok(await ev(() => CF_HUNDRED.state().n === 21 && document.querySelectorAll('#hChart .hc.t').length === 20 && document.querySelectorAll('#hChart .hc.o').length === 1), 'hundred chart: +10 +10 +1 shows 2 tens and 1 one (21)');
  await ev(() => KIDS.go('song', { s: 5 })); await p.waitForTimeout(300);
  ok(await ev(() => [...document.querySelectorAll('#songNums .sn')].map(e => e.textContent).join() === '5,10,15,20,25,30,35,40,45,50'), 'the 5s song shows 5..50');
  await tap('#songPlay'); await p.waitForTimeout(1300);
  ok(await ev(() => !!document.querySelector('#songNums .sn.on')), 'the song lights up its numbers while playing');
  await p.waitForTimeout(7500);
  ok(await ev(() => KIDS.hasSticker('SG_5')), 'finishing the 5s song awards its sticker');
  await tap('#m-reveal [data-act="reveal-ok"]');
  await ev(() => KIDS.go('play', { g: 'next', seed: 4, level: 3 })); await p.waitForTimeout(400);
  const nx = await ev(() => CF_GAME.state().rd);
  ok(nx.seq.length === 5 && nx.seq[nx.blank] === nx.answer && nx.seq[1] - nx.seq[0] === 5, 'What comes next? shows a 5s sequence with the blank holding the answer');
  await tap(`#playStage [data-act="ans"][data-v="${nx.answer}"]`);
  ok(await ev(() => CF_GAME.state().stars === 1), 'the right answer earns a star');
  await ev(() => KIDS.go('play', { g: 'make', seed: 2, level: 1 })); await p.waitForTimeout(400);
  const mk = await ev(() => CF_GAME.state().rd.answer);
  for (let i = 0; i < mk; i++) await tap('#playStage [data-act="mk-add"]');
  ok(await ev(() => CF_GAME.state().stars === 1 && document.querySelectorAll('#basket .bi').length === CF_GAME.state().rd.answer), `Make ${mk}: adding ${mk} objects wins the turn`);

  // ── 7. Families: forbidden bridge calls never happen ─────────────────────
  const all = await ev(() => window.__calls.map(c => c[0]));
  const bad = [...new Set(all.filter(n => FORBIDDEN.test(n)))];
  ok(bad.length === 0, 'no notification / interstitial / rewarded / share / Play Games call' + (bad.length ? ' — got ' + bad.join(', ') : ''));
  ok(errs.length === 0, 'no page errors' + (errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''));

  await br.close();
  console.log(fails ? `CountingApp runtime check: ${fails} failure(s)` : 'CountingApp runtime check: OK');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
