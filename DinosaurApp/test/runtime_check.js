#!/usr/bin/env node
// DinosaurApp runtime check - drives the REAL UI in headless Chromium with the
// shared mocked Android bridge (scripts/runtime/mock_bridge.js), using real
// pointer input, and asserts the kids-shell contract plus this app's own:
//   * the dinosaur book lists every creature, a card shows name / kind / period / food / place and plays ITS made-up roar
//   * a pterosaur / sea reptile / Dimetrodon card says it is NOT a dinosaur
//   * every one of the 39 roars renders non-silent, unclipped, 0.3-3.5 s and no two sound alike
//   * "How big?": the drawn lengths equal the stated lengths (dino vs bus / child / house) for every dinosaur and reference
//   * the fossil dig is cleared by really brushing the sand; shadow match works with a gentle wrong tap; stickers are awarded
//   * locked dinosaurs ask a grown-up and never reach the store; the parental gate refuses a wrong answer
//   * NO notification / interstitial / rewarded / sharing / Play Games bridge call, no audio files, no network
//
//   node DinosaurApp/test/runtime_check.js
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const mock = fs.readFileSync(path.join(REPO, 'scripts/runtime/mock_bridge.js'), 'utf8');
const FILE = path.join(REPO, 'DinosaurApp/android/app/src/main/assets/game.html');
const URL = 'file://' + FILE;
const FORBIDDEN = /Interstitial|Rewarded|schedule|Notification|recordLastPlayed|share|submitScore|Leaderboard|PlayGames|logEvent/i;
let fails = 0;
const ok = (cond, msg) => { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) fails++; };

(async () => {
  const src = fs.readFileSync(FILE, 'utf8');
  ok(!/new Audio\(|<audio|\.(mp3|ogg|wav|m4a)\b/i.test(src), 'no audio files: every roar is synthesized');
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

  // 1. Dinosaur book
  await tap('#homeTiles .tile:nth-child(1)');
  ok(await screen() === 'dinos', 'Dinos tile opens the dinosaur book');
  ok(await ev(() => document.querySelectorAll('#dinoGrid .atile').length === DINOS.length), 'book lists every creature (' + await ev(() => DINOS.length) + ')');
  ok(await ev(() => document.querySelectorAll('#dinoGrid .sec').length === 4), 'book is grouped by 4 time periods');
  await tap('[data-a="tyrannosaurus"]');
  ok(await screen() === 'card', 'tapping a dinosaur opens its card');
  await p.waitForTimeout(500);
  ok(await ev(() => DW_SYNTH.last === 'tyrannosaurus' && DW_SYNTH.count >= 1), 'the card plays the T. rex roar');
  ok(await ev(() => !!KIDS.save.progress.heard.tyrannosaurus), 'the dinosaur is marked as met');
  ok(await ev(() => ['cardName', 'cardKind', 'chipPer', 'chipDiet', 'chipCont', 'cardSize'].every(i => document.getElementById(i).textContent.length > 0)), 'card shows name, kind, period, food, place and size');
  ok(await ev(() => /Cretaceous/.test(chipPer.textContent) && /meat/.test(chipDiet.textContent) && /North America/.test(chipCont.textContent) && /12 m/.test(cardSize.textContent)), 'T. rex card: Cretaceous, meat, North America, 12 m');
  ok(await ev(() => /made by the app/i.test(document.querySelector('.roar-note').textContent)), 'the card says the roar is made up and made by the app');
  await tap('#scr-card [data-act="card-next"]');
  ok(await ev(() => document.getElementById('cardName').textContent === 'Triceratops'), 'next card is Triceratops');
  // a pterosaur card says it is not a dinosaur
  await ev(() => KIDS.go('card', { a: 'pteranodon' })); await p.waitForTimeout(500);
  ok(await ev(() => /not a dinosaur/i.test(cardKind.textContent) && /flying reptile/i.test(cardKind.textContent)), 'Pteranodon is labelled "flying reptile - not a dinosaur"');
  for (const [id, re] of [['elasmosaurus', /sea reptile.*not a dinosaur/i], ['mosasaurus', /sea reptile.*not a dinosaur/i], ['dimetrodon', /not a dinosaur/i], ['quetzalcoatlus', /flying reptile.*not a dinosaur/i]]) {
    await ev(i => KIDS.go('card', { a: i }), id); await p.waitForTimeout(250);
    ok(await ev(r => new RegExp(r.s, r.f).test(cardKind.textContent), { s: re.source, f: re.flags }), id + ' card says it is not a dinosaur');
  }
  // locked dinosaur
  await ev(() => KIDS.go('dinos')); await p.waitForTimeout(300);
  const before = await ev(() => DW_SYNTH.count);
  await tap('[data-a="argentinosaurus"]');
  ok(await modalOpen('m-ask') && await ev(b => DW_SYNTH.count === b, before) && await screen() === 'dinos', 'a locked dinosaur asks a grown-up and stays silent');
  await ev(() => { document.getElementById('m-ask').classList.remove('open'); }); await p.waitForTimeout(300);

  // 2. The 39 roars: audible, unclipped, distinct (offline render of the real synth)
  const feat = await ev(async () => {
    const out = {};
    for (const a of DINOS) {
      const d = DW_SYNTH.dur(a.id), sr = 22050, oc = new OfflineAudioContext(1, Math.ceil(sr * (d + 0.2)), sr), dest = oc.createGain();
      dest.gain.value = 0.9; dest.connect(oc.destination); DW_SYNTH.render(a.id, oc, dest, 0.02);
      const x = (await oc.startRendering()).getChannelData(0); let pk = 0, s2 = 0, zc = 0;
      for (let i = 0; i < x.length; i++) { const v = Math.abs(x[i]); if (v > pk) pk = v; s2 += x[i] * x[i]; if (i && x[i] * x[i - 1] < 0) zc++; }
      out[a.id] = { d: d, pk: pk, rms: Math.sqrt(s2 / x.length), zcr: zc / d };
    }
    return out;
  });
  const ids = Object.keys(feat);
  ok(ids.length === 39, ids.length + ' roars rendered');
  ok(ids.every(i => feat[i].rms > 0.02), 'every roar is audible (rms > 0.02): ' + ids.filter(i => feat[i].rms <= 0.02).join(','));
  ok(ids.every(i => feat[i].pk < 0.97), 'no roar clips (peak < 0.97): ' + ids.filter(i => feat[i].pk >= 0.97).join(','));
  ok(ids.every(i => feat[i].d >= 0.3 && feat[i].d <= 3.5), 'every roar lasts 0.3-3.5 s');
  const twins = [];
  for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) {
    const a = feat[ids[i]], b = feat[ids[j]];
    if (Math.abs(Math.log(a.zcr / b.zcr)) < 0.03 && Math.abs(a.d - b.d) < 0.06) twins.push(ids[i] + '/' + ids[j]);
  }
  ok(twins.length === 0, 'no two roars are the same recipe' + (twins.length ? ' - ' + twins.join(', ') : ''));

  // 3. How big?  drawn lengths must equal the stated lengths
  await ev(() => KIDS.go('home')); await p.waitForTimeout(300);
  await tap('#homeTiles .tile:nth-child(2)');
  ok(await screen() === 'size', 'How big? tile opens the size compare');
  ok(await ev(() => document.getElementById('sizeRange').max === String(DW_SIZE.state().list.length - 1)), 'the slider spans the unlocked dinosaurs');
  const bad = [];
  for (const ref of ['bus', 'child', 'house']) {
    await ev(r => { document.querySelector('[data-r="' + r + '"]').click(); }, ref);
    const n = await ev(() => DW_SIZE.state().list.length);
    for (let i = 0; i < n; i++) {
      const r = await ev(([idx, rf]) => {
        const rg = document.getElementById('sizeRange'); rg.value = String(idx); rg.dispatchEvent(new Event('input', { bubbles: true }));
        const d = DW_SIZE.state().list[idx], st = document.getElementById('sizeStage'), gl = [...st.querySelectorAll('.gl')].map(g => parseFloat(g.style.left)), pad = 12;
        const dl = gl[0] - pad, rw = gl[1] - pad, R = DW_SIZE.ref[rf];
        const shown = parseFloat(document.querySelector('[data-r="' + rf + '"] .r-n').textContent.replace('×', ''));
        return { id: d.id, got: dl / rw, want: d.m / R.w, shown: shown, exp: d.m / SIZE_REF[rf] };
      }, [i, ref]);
      if (Math.abs(r.got - r.want) > 0.03 * r.want + 0.02 || Math.abs(r.shown - r.exp) > Math.max(0.06, 0.03 * r.exp) + 0.001) bad.push(`${r.id}/${ref}: drawn x${r.got.toFixed(2)} stated x${r.want.toFixed(2)} shown x${r.shown} expected x${r.exp.toFixed(2)}`);
    }
  }
  ok(bad.length === 0, 'drawn size ratios equal the stated lengths for every dinosaur and reference' + (bad.length ? ' - ' + bad.slice(0, 3).join('; ') : ''));
  await ev(() => { document.querySelector('[data-r="bus"]').click(); });
  await ev(() => { const rg = document.getElementById('sizeRange'); rg.value = String(DW_SIZE.state().list.findIndex(d => d.id === 'tyrannosaurus')); rg.dispatchEvent(new Event('input', { bubbles: true })); });
  ok(await ev(() => /×1\.0/.test(document.querySelector('[data-r="bus"] .r-n').textContent) && /12 m/.test(document.getElementById('sizeLine').textContent)), 'T. rex is as long as one school bus (x1.0, 12 m)');
  const w0 = await ev(() => DW_SIZE.state().idx);
  await tap('#scr-size [data-act="size-next"]');
  ok(await ev(w => DW_SIZE.state().idx === w + 1, w0), 'the next arrow moves the slider one dinosaur');

  // 4. Fossil dig: really brush the sand
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="dig"]');
  ok(await screen() === 'dig', 'Fossil dig starts');
  const T0 = await ev(() => DW_DIG.state().target);
  ok(await ev(() => DW_DIG.measure() < 0.05), 'the fossil starts buried under sand');
  async function brushAll() {
    const cb = await p.locator('#digCanvas').boundingBox();
    await p.mouse.move(cb.x + cb.width * 0.5, cb.y + cb.height * 0.5); await p.mouse.down();
    await p.mouse.move(cb.x + cb.width * 0.6, cb.y + cb.height * 0.55, { steps: 6 });
    return cb;
  }
  let cb = await brushAll();
  ok(await ev(() => DW_DIG.measure() > 0.01 && !DW_DIG.state().found), 'a short brush stroke clears a little sand but does not finish');
  const sweep = async cb => { for (let k = 0; k < 11; k++) { const y = cb.y + cb.height * (0.28 + k * 0.065); await p.mouse.move(cb.x + cb.width * 0.04, y, { steps: 2 }); await p.mouse.move(cb.x + cb.width * 0.96, y, { steps: 8 }); } await p.mouse.up(); await p.waitForTimeout(600); };
  await sweep(cb);
  ok(await ev(() => DW_DIG.state() && DW_DIG.state().stars >= 1), 'brushing the sand away uncovers the fossil and earns a star');
  await p.waitForTimeout(3800); await closeReveal();
  ok(await ev(t => KIDS.hasSticker('D_' + t), T0), 'finding a fossil awards that dinosaur sticker');
  ok(await ev(() => DW_DIG.state() && DW_DIG.state().target !== null && DW_DIG.state().pct < 0.2), 'a new fossil is buried for the next find');
  for (let n = 0; n < 2; n++) { cb = await brushAll(); await sweep(cb); await p.waitForTimeout(3800); await closeReveal(); }
  await p.waitForTimeout(2500); await closeReveal();
  ok(await ev(() => KIDS.save.progress.rounds === 1 && !!document.querySelector('#digStage .end-panel')), 'three fossils finish the dig round (end panel, round counted)');
  ok(await ev(() => KIDS.hasSticker('S_egg')), 'finishing the dig awards the first fossil sticker');

  // 5. Shadow match, with a gentle wrong tap
  await ev(() => KIDS.go('games')); await p.waitForTimeout(300);
  await tap('[data-g="match"]');
  ok(await screen() === 'match', 'Shadow match starts');
  ok(await ev(() => document.querySelectorAll('.mshadow').length === 4 && document.querySelectorAll('.mpic').length === 4), 'four shadows and four dinosaur pictures');
  const wrongPair = await ev(() => { const s = document.querySelectorAll('.mshadow'), pcs = [...document.querySelectorAll('.mpic')]; const sid = s[0].dataset.id; return { s: sid, p: pcs.find(x => x.dataset.id !== sid).dataset.id }; });
  await tap(`.mpic[data-id="${wrongPair.p}"]`); await tap(`.mshadow[data-id="${wrongPair.s}"]`);
  ok(await ev(() => DW_MATCH.state().stars === 0), 'a wrong match is gentle: no star lost, nothing breaks');
  for (let i = 0; i < 4; i++) {
    const id = await ev(() => document.querySelector('.mshadow:not(.done)').dataset.id);
    await tap(`.mpic[data-id="${id}"]`); await tap(`.mshadow[data-id="${id}"]`); await p.waitForTimeout(3300); await closeReveal();
  }
  await p.waitForTimeout(2500); await closeReveal();
  ok(await ev(() => KIDS.save.progress.rounds === 2 && KIDS.hasSticker('S_footprint')), 'finishing the match round counts and awards the next fossil sticker');

  // 6. Gate refuses a wrong answer, then purchase + restore only behind it
  await ev(() => KIDS.go('home')); await p.waitForTimeout(300); await tap('#btnGrownups');
  const wrongAns = await ev(() => [...document.querySelectorAll('.gopt')].map(b => +b.dataset.v).find(v => v !== Gate.ans));
  await hold(`.gopt[data-v="${wrongAns}"]`, 1700);
  ok(!(await modalOpen('m-gate')) && await screen() !== 'parent' && await ev(() => !Gate.ok()), 'wrong answer closes the gate and the parent area stays locked');
  await tap('#btnGrownups');
  let ans = await ev(() => Gate.ans);
  await tap(`.gopt[data-v="${ans}"]`);
  ok(await screen() !== 'parent' && await modalOpen('m-gate'), 'a quick tap on the right answer is not enough');
  await hold(`.gopt[data-v="${ans}"]`, 1700);
  ok(await screen() === 'parent', 'holding the right answer opens the parent area');
  ok((await calls('purchase')).length === 0 && (await calls('openUrl')).length === 0, 'no store / link call before a grown-up action');
  ok(await ev(() => /made up/i.test(document.querySelector('[data-i18n="ageNote"]').textContent)), 'parent area says the roars are made up, not recordings');
  await ev(() => { KIDS.save.fullPack = false; KIDS.save.removeAds = false; KIDS.persist(); });
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

  // 7. Unlocked: a premium dinosaur opens and roars
  await ev(() => KIDS.go('dinos')); await p.waitForTimeout(300);
  ok(await ev(() => !document.querySelector('[data-a="argentinosaurus"]').classList.contains('locked')), 'all dinosaurs unlocked after full_pack');
  await tap('[data-a="argentinosaurus"]'); await p.waitForTimeout(500);
  ok(await ev(() => DW_SYNTH.last === 'argentinosaurus'), 'Argentinosaurus now opens and roars');

  // 8. Families: forbidden bridge calls never happen
  const all = await ev(() => window.__calls.map(c => c[0]));
  const forb = [...new Set(all.filter(n => FORBIDDEN.test(n)))];
  ok(forb.length === 0, 'no notification / interstitial / rewarded / share / Play Games call' + (forb.length ? ' - got ' + forb.join(', ') : ''));
  ok(netTried === 0, 'nothing leaves the device (no network request)');
  ok(errs.length === 0, 'no page errors' + (errs.length ? ' - ' + errs.slice(0, 2).join(' | ') : ''));

  await br.close();
  console.log(fails ? `DinosaurApp runtime check: ${fails} failure(s)` : 'DinosaurApp runtime check: OK');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
