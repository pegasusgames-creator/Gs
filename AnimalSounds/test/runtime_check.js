#!/usr/bin/env node
// AnimalSounds runtime check - drives the REAL UI in headless Chromium with the
// shared mocked Android bridge (scripts/runtime/mock_bridge.js), using real
// pointer input, and asserts the kids-shell contract plus this app's own:
//   * tapping an animal on the sound board plays ITS synthesized sound and marks it heard
//   * every one of the 44 sounds renders non-silent, unclipped, 0.3-3.5 s and no two sound alike
//   * a full "Who says this?" round (with a gentle wrong tap) has no failure state and awards stickers
//   * locked animals / the second game ask a grown-up and never reach the store
//   * the parental gate refuses a wrong answer; purchase/restore/link only after the gate
//   * NO notification / interstitial / rewarded / sharing / Play Games bridge call, no audio files, no network
//
//   node AnimalSounds/test/runtime_check.js
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const FILE = path.join(REPO, 'AnimalSounds/android/app/src/main/assets/game.html');
const URL = 'file://' + FILE;
const FORBIDDEN = /Interstitial|Rewarded|schedule|Notification|recordLastPlayed|share|submitScore|Leaderboard|PlayGames|logEvent/i;
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const src = fs.readFileSync(FILE, 'utf8');
  ok(!/new Audio\(|<audio|\.(mp3|ogg|wav|m4a)\b/i.test(src), 'no audio files: every sound is synthesized');
  const br = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await br.newContext({ viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(mock);
  let netTried = 0;
  await ctx.route(/^https?:/, r => { netTried++; r.abort(); });
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
  const closeReveal = async () => { for (let i = 0; i < 3 && await modalOpen('m-reveal'); i++) await tap('#m-reveal [data-act="reveal-ok"]'); };

  ok(await ev(() => KIDS.ready === true), 'shell boots to home');
  ok((await calls('hideBannerAd')).length + (await calls('showBannerAd')).length > 0, 'banner state synced with native on boot');

  // 1. Sound board: a real tap plays that animal's own sound
  await tap('#homeTiles .tile:nth-child(1)');
  ok(await screen() === 'board', 'Sounds tile opens the sound board');
  ok(await ev(() => document.querySelectorAll('#boardGrid .atile').length === ANIMALS.length), 'board lists every animal (' + await ev(() => ANIMALS.length) + ')');
  await tap('[data-a="cow"]');
  ok(await ev(() => AS_SYNTH.last === 'cow' && AS_SYNTH.count >= 1), 'tapping the cow plays the cow sound');
  ok(await ev(() => !!KIDS.save.progress.heard.cow), 'the cow is marked as heard');
  await tap('[data-a="pig"]');
  ok(await ev(() => AS_SYNTH.last === 'pig'), 'tapping the pig plays a different sound');
  // locked animal: grown-up card, no sound
  const before = await ev(() => AS_SYNTH.count);
  await tap('[data-a="monkey"]');
  ok(await modalOpen('m-ask') && await ev(b => AS_SYNTH.count === b, before), 'a locked animal asks a grown-up and stays silent');
  await tap('#m-ask [data-act="ask-close"]');
  await ev(() => { document.getElementById('m-ask').classList.remove('open'); }); await p.waitForTimeout(300);
  // animal card with facts
  await tap('#scr-board [data-act="board-info"]');
  ok(await screen() === 'animal', 'the info button opens the animal card');
  ok(await ev(() => document.getElementById('cardName').textContent.length > 0 && document.getElementById('cardHab').textContent.length > 0 && document.getElementById('cardDiet').textContent.length > 0), 'card shows name, home and diet');
  await tap('#scr-animal [data-act="card-next"]');
  ok(await ev(() => document.getElementById('cardName').textContent === 'sheep'), 'next card is the sheep');
  await tap('#scr-animal [data-act="card-hab"]');
  ok(await screen() === 'habitat', 'the home chip opens the habitat page');
  ok(await ev(() => document.querySelectorAll('#habAnimals .atile').length === ANIMALS.filter(a => a.hab === 'farm').length), 'farm page lists its animals');
  await tap('#habAnimals [data-a="hen"]');
  ok(await ev(() => AS_SYNTH.last === 'hen'), 'a habitat page tile plays the sound too');

  // 2. Habitats hub: locked home asks a grown-up
  await ev(() => KIDS.go('habitats')); await p.waitForTimeout(300);
  await tap('[data-h="jungle"]');
  ok(await modalOpen('m-ask') && await screen() === 'habitats', 'locked jungle asks a grown-up and does not open');
  await ev(() => { document.getElementById('m-ask').classList.remove('open'); }); await p.waitForTimeout(300);

  // 3. The 44 sounds: audible, unclipped, distinct (offline render of the real synth)
  const feat = await ev(async () => {
    const out = {};
    for (const a of ANIMALS) {
      const d = AS_SYNTH.dur(a.id), sr = 22050, oc = new OfflineAudioContext(1, Math.ceil(sr * (d + 0.2)), sr), dest = oc.createGain();
      dest.gain.value = 0.9; dest.connect(oc.destination); AS_SYNTH.render(a.id, oc, dest, 0.02);
      const x = (await oc.startRendering()).getChannelData(0); let pk = 0, s2 = 0, zc = 0;
      for (let i = 0; i < x.length; i++) { const v = Math.abs(x[i]); if (v > pk) pk = v; s2 += x[i] * x[i]; if (i && x[i] * x[i - 1] < 0) zc++; }
      out[a.id] = { d: d, pk: pk, rms: Math.sqrt(s2 / x.length), zcr: zc / d };
    }
    return out;
  });
  const ids = Object.keys(feat);
  ok(ids.length >= 40, ids.length + ' animal sounds rendered');
  ok(ids.every(i => feat[i].rms > 0.03), 'every sound is audible (rms > 0.03): ' + ids.filter(i => feat[i].rms <= 0.03).join(','));
  ok(ids.every(i => feat[i].pk < 0.97), 'no sound clips (peak < 0.97): ' + ids.filter(i => feat[i].pk >= 0.97).join(','));
  ok(ids.every(i => feat[i].d >= 0.3 && feat[i].d <= 3.5), 'every sound lasts 0.3-3.5 s');
  const twins = [];
  for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) {
    const a = feat[ids[i]], b = feat[ids[j]];
    if (Math.abs(Math.log(a.zcr / b.zcr)) < 0.03 && Math.abs(a.d - b.d) < 0.06) twins.push(ids[i] + '/' + ids[j]);
  }
  ok(twins.length === 0, 'no two animal sounds are the same recipe' + (twins.length ? ' - ' + twins.join(', ') : ''));

  // 4. "Who says this?" round with real taps
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="who"]');
  ok(await screen() === 'play', 'Who says this? starts');
  ok(await ev(() => document.getElementById('qSpeaker') !== null && AS_GAME.state().opts.length === 3), 'a speaker button and three animal pictures are shown');
  ok(await ev(() => { const g = AS_GAME.state(); const w = ANI[g.target].word; return g.opts.filter(o => ANI[o].word === w).length === 1; }), 'distractors never share the target sound word');
  const T0 = await ev(() => AS_GAME.state().target);
  const wrong = await ev(() => AS_GAME.state().opts.find(x => x !== AS_GAME.state().target));
  await tap(`#playStage [data-v="${wrong}"]`);
  ok(await ev(t => AS_GAME.state().stars === 0 && AS_GAME.state().target === t, T0), 'a wrong tap is gentle: no star lost, same question');
  ok(await ev(w => document.querySelector(`#playStage [data-v="${w}"]`).disabled, wrong), 'the wrong picture fades away');
  for (let i = 0; i < 5; i++) {
    const T = await ev(() => AS_GAME.state().target);
    ok(await ev(t => FREE_HABS.indexOf(ANI[t].hab) >= 0, T), `turn ${i + 1}: ${T} comes from the free set`);
    await tap(`#playStage [data-v="${T}"]`); await p.waitForTimeout(3700); await closeReveal();
  }
  ok(await ev(() => KIDS.save.progress.rounds === 1), 'round finished and counted');
  await p.waitForTimeout(2500);
  ok(await ev(() => KIDS.hasSticker('S_paw')), 'finishing a round awards the first star sticker');
  await closeReveal();
  ok(await ev(() => Object.keys(KIDS.save.stickers).filter(k => k[0] === 'A').length >= 4), 'right answers award animal stickers');

  // 5. Second game locked until purchase
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="where"]');
  ok(await modalOpen('m-ask') && await screen() === 'games', 'Where does it live? asks a grown-up while locked');
  await tap('#m-ask [data-act="ask-parent"]'); await p.waitForTimeout(300);
  ok(await modalOpen('m-gate'), 'grown-up button opens the parental gate');

  // 6. Gate refuses a wrong answer
  const wrongAns = await ev(() => [...document.querySelectorAll('.gopt')].map(b => +b.dataset.v).find(v => v !== Gate.ans));
  await hold(`.gopt[data-v="${wrongAns}"]`, 1700);
  ok(!(await modalOpen('m-gate')) && await screen() !== 'parent' && await ev(() => !Gate.ok()), 'wrong answer closes the gate and the parent area stays locked');
  await ev(() => KIDS.go('home')); await p.waitForTimeout(300); await tap('#btnGrownups');
  let ans = await ev(() => Gate.ans);
  await tap(`.gopt[data-v="${ans}"]`);
  ok(await screen() !== 'parent' && await modalOpen('m-gate'), 'a quick tap on the right answer is not enough');
  await hold(`.gopt[data-v="${ans}"]`, 1700);
  ok(await screen() === 'parent', 'holding the right answer opens the parent area');
  ok((await calls('purchase')).length === 0 && (await calls('openUrl')).length === 0, 'no store / link call before a grown-up action');
  ok(await ev(() => /not recordings|nicht|recordings/i.test(document.querySelector('[data-i18n="ageNote"]').textContent)), 'parent area says the sounds are made by the app, not recordings');

  // 7. Purchase + grant
  await tap('#prodList [data-id="full_pack"]');
  ok((await calls('purchase')).some(c => c[1][0] === 'full_pack'), 'Buy (behind the gate) launches billing for full_pack');
  await ev(() => window.onPurchaseSuccess('full_pack')); await p.waitForTimeout(300);
  ok(await ev(() => KIDS.save.fullPack === true && KIDS.save.removeAds === true), 'onPurchaseSuccess(full_pack) unlocks everything + removes ads');
  await tap('#scr-parent [data-act="privacy"]');
  ok((await calls('openUrl')).some(c => c[1][0] === 'https://pegasusgames-creator.github.io/privacy-kids.html'), 'privacy link (behind the gate) opens the KIDS policy');
  await tap('#scr-parent [data-act="back"]');
  const nb = (await calls('purchase')).length;
  await ev(() => gatedNative('purchase', 'remove_ads')); await p.waitForTimeout(200);
  ok((await calls('purchase')).length === nb && await modalOpen('m-gate'), 'after leaving, a store call re-opens the gate instead');
  await ev(() => Gate.cancel()); await p.waitForTimeout(300);
  await tap('#btnGrownups'); ans = await ev(() => Gate.ans); await hold(`.gopt[data-v="${ans}"]`, 1700);
  await tap('#btnRestore');
  ok((await calls('restorePurchases')).length === 1, 'Restore purchases (behind the gate) calls the bridge');
  await ev(() => { KIDS.save.removeAds = false; KIDS.save.fullPack = false; window.onPurchaseSuccess('remove_ads'); window.onPurchaseSuccess('full_pack'); });
  ok(await ev(() => KIDS.save.removeAds && KIDS.save.fullPack), 'restored SKUs re-grant (idempotent)');
  await ev(() => window.onPurchaseSuccess('coins_small'));
  ok(await ev(() => !!JSON.parse(localStorage.getItem('pendingGrants') || '{}').coins_small), 'unknown SKU is parked in pendingGrants (never dropped)');

  // 8. Unlocked: monkey plays, Where does it live? works
  await ev(() => KIDS.go('board')); await p.waitForTimeout(300);
  ok(await ev(() => !document.querySelector('[data-a="monkey"]').classList.contains('locked')), 'all animals unlocked after full_pack');
  await tap('[data-a="monkey"]');
  ok(await ev(() => AS_SYNTH.last === 'monkey'), 'the monkey now plays its sound');
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="where"]');
  ok(await screen() === 'play', 'Where does it live? opens after the purchase');
  const W = await ev(() => { const g = AS_GAME.state(); const a = ANI[g.target]; return { t: g.target, bad: g.opts.find(h => [a.hab].concat(a.alt).indexOf(h) < 0), good: a.hab, ok: g.opts.every((h, i, o) => o.indexOf(h) === i) && g.opts.indexOf(a.hab) >= 0 && g.opts.filter(h => [a.hab].concat(a.alt).indexOf(h) >= 0).length === 1 }; });
  ok(W.ok, 'exactly one valid home among three distinct choices');
  await tap(`#playStage [data-v="${W.bad}"]`);
  ok(await ev(() => AS_GAME.state().stars === 0), 'a wrong home is gentle (no star lost)');
  await tap(`#playStage [data-v="${W.good}"]`);
  ok(await ev(() => AS_GAME.state().stars === 1), 'the right home earns a star');

  // 9. Families: forbidden bridge calls never happen
  const all = await ev(() => window.__calls.map(c => c[0]));
  const bad = [...new Set(all.filter(n => FORBIDDEN.test(n)))];
  ok(bad.length === 0, 'no notification / interstitial / rewarded / share / Play Games call' + (bad.length ? ' - got ' + bad.join(', ') : ''));
  ok(netTried === 0, 'nothing leaves the device (no network request)');
  ok(errs.length === 0, 'no page errors' + (errs.length ? ' - ' + errs.slice(0, 2).join(' | ') : ''));

  await br.close();
  console.log(fails ? `AnimalSounds runtime check: ${fails} failure(s)` : 'AnimalSounds runtime check: OK');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
