#!/usr/bin/env node
// ABCLearning runtime check — drives the REAL UI in headless Chromium with the
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
//   node ABCLearning/test/runtime_check.js
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const URL = 'file://' + path.join(REPO, 'ABCLearning/android/app/src/main/assets/game.html');
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
    await p.locator(sel).first().scrollIntoViewIfNeeded().catch(() => {});
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

  // ── 1. Trace "A": every stroke with a real finger drag ──────────────────
  await tap('#homeTiles .tile:nth-child(2)');
  ok(await screen() === 'letters', 'Trace tile opens the letter grid');
  await tap('[data-l="A"]');
  ok(await screen() === 'trace', 'tapping A opens tracing');
  ok((await calls('hideBannerAd')).length > 0, 'banner hidden while tracing');
  const nStrokes = await ev(() => ABC_TRACE.state().strokes.length);
  for (let i = 0; i < nStrokes; i++) {
    const pts = await ev(k => {
      const s = document.getElementById('trSvg'), m = s.getScreenCTM();
      return ABC_TRACE.points(k).map(q => { const pt = s.createSVGPoint(); pt.x = q.x; pt.y = q.y; const r = pt.matrixTransform(m); return [r.x, r.y]; });
    }, i);
    // forgiving: a wobbly finger a few px off the path still counts
    await p.mouse.move(pts[0][0] + 4, pts[0][1] + 3); await p.mouse.down();
    for (let k = 0; k < pts.length; k++) await p.mouse.move(pts[k][0] + (k % 2 ? 5 : -5), pts[k][1] + (k % 3 ? 3 : -4));
    await p.mouse.up(); await p.waitForTimeout(250);
  }
  ok(await ev(() => !!KIDS.save.progress.traced.A), 'A traced and saved');
  ok(await ev(() => document.getElementById('trStage').classList.contains('done')), 'tracing shows the done state');
  await p.waitForTimeout(4600);
  ok(await ev(() => !!KIDS.save.stickers.L_A), 'tracing A awards the apple sticker');
  ok(await modalOpen('m-reveal'), 'sticker reveal popup shown');
  await tap('#m-reveal [data-act="reveal-ok"]');
  ok(!(await modalOpen('m-reveal')), 'reveal popup closes on tap');
  // off-path scribble must not advance a stroke
  await tap('#scr-trace [data-act="tr-case"][data-v="lower"]');
  await p.mouse.move(30, 300); await p.mouse.down(); await p.mouse.move(380, 320, { steps: 12 }); await p.mouse.up();
  ok(await ev(() => ABC_TRACE.state().si === 0 && ABC_TRACE.state().strokes[0].idx < 3), 'off-path scribble is ignored (no progress, no penalty)');

  // ── 2. One "Find the letter" round with real taps ───────────────────────
  await tap('#scr-trace [data-act="back"]'); await tap('#scr-letters [data-act="back"]');
  await tap('#homeTiles .tile:nth-child(3)');
  ok(await screen() === 'games', 'Games tile opens the games hub');
  await tap('[data-g="find"]');
  ok(await screen() === 'play', 'Find the letter starts');
  const T0 = await ev(() => ABC_GAME.state().target);
  const wrong = await ev(() => ABC_GAME.state().opts.find(x => x !== ABC_GAME.state().target));
  await tap(`#playStage [data-v="${wrong}"]`);
  ok(await ev(t => ABC_GAME.state().stars === 0 && ABC_GAME.state().target === t, T0), 'a wrong tap is gentle: no star lost, same question');
  for (let i = 0; i < 5; i++) {
    const T = await ev(() => ABC_GAME.state().target);
    ok(await ev(t => FREE_LETTERS.indexOf(t) >= 0, T), `turn ${i + 1}: target ${T} is from the free set`);
    await tap(`#playStage [data-v="${T}"]`); await p.waitForTimeout(3600);
  }
  ok(await ev(() => KIDS.save.progress.rounds === 1), 'round finished and counted');
  await p.waitForTimeout(3600);
  ok(await ev(() => !!KIDS.save.stickers.S_star), 'finishing a round awards the next star sticker');
  await tap('#m-reveal [data-act="reveal-ok"]');

  // ── 3. Locked content → ask a grown-up (never the store) ─────────────────
  await ev(() => KIDS.go('letters', { mode: 'learn' })); await p.waitForTimeout(300);
  await tap('[data-l="K"]');
  ok(await modalOpen('m-ask'), 'locked letter K asks for a grown-up');
  ok(await screen() === 'letters', 'locked letter does not open');
  await tap('#m-ask [data-act="ask-parent"]'); await p.waitForTimeout(300);
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
  await ev(() => KIDS.go('letters', { mode: 'learn' })); await p.waitForTimeout(300);
  ok(await ev(() => !document.querySelector('[data-l="K"]').classList.contains('locked')), 'K-Z unlocked after full_pack');

  // ── 7. Families: forbidden bridge calls never happen ─────────────────────
  const all = await ev(() => window.__calls.map(c => c[0]));
  const bad = [...new Set(all.filter(n => FORBIDDEN.test(n)))];
  ok(bad.length === 0, 'no notification / interstitial / rewarded / share / Play Games call' + (bad.length ? ' — got ' + bad.join(', ') : ''));
  ok(errs.length === 0, 'no page errors' + (errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''));

  await br.close();
  console.log(fails ? `ABCLearning runtime check: ${fails} failure(s)` : 'ABCLearning runtime check: OK');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
