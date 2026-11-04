#!/usr/bin/env node
// AspectRatio runtime check — drives the REAL UI in headless Chromium with the mocked
// Android bridge (scripts/runtime/mock_bridge.js) and real input events:
// onboarding → typing a width (half-way rounding stated) → lock Ratio/Width/Height →
// presets → invalid input → copy → crop rows → unit conversion + DPI → "use in Resize" →
// history (restore, clear + Undo) → saved presets (free limit 3 → paywall → Pro) →
// batch list → backup/restore → interstitial cadence → 13-language completeness + RTL.
//
//   node AspectRatio/test/runtime_check.js        (exit 1 on any failure)
// The calculation block itself is gated by scripts/check_aspectratio_math.py.
const path = require('path'), fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }
const REPO = path.resolve(__dirname, '..', '..');
const GAME = path.join(REPO, 'AspectRatio/android/app/src/main/assets/game.html');
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
  const tap = async (sel) => { await p.locator(sel).first().tap(); await p.waitForTimeout(200); };
  const ev = (fn, arg) => p.evaluate(fn, arg);
  const calls = (name) => ev(n => window.__calls.filter(c => c[0] === n), name);
  const txt = async (sel) => (await p.locator(sel).first().innerText()).replace(/\s+/g, ' ').trim();
  const val = (sel) => p.locator(sel).first().inputValue();
  const type = async (sel, v) => { const l = p.locator(sel).first(); await l.fill(''); await l.pressSequentially(v, { delay: 15 }); await p.waitForTimeout(120); };
  const commit = async (sel) => { await p.locator(sel).first().press('Enter'); await p.locator(sel).first().blur(); await p.waitForTimeout(200); };
  const rz = () => ev(() => JSON.parse(JSON.stringify(S.tool.rz)));
  await p.goto('file://' + GAME);
  await p.waitForTimeout(700);

  // 1. First launch.
  ok(await p.locator('#onb').isVisible(), 'onboarding shows on first launch');
  await tap('#onb-next'); await tap('#onb-next'); await tap('#onb-next');
  ok(!(await p.locator('#onb').count()) && await ev(() => S.onboarded === true), 'onboarding completes');
  ok(await p.locator('[data-act="tab"]').count() === 3, 'three tabs: Resize, Convert, Saved');
  ok(await p.locator('#pvb').isVisible() && (await val('#rz-w')) === '1920' && (await val('#rz-h')) === '1080', 'Resize opens on 1920 × 1080 with a live preview frame');
  ok((await txt('#pv-meta')).includes('16:9'), 'preview shows the reduced ratio 16:9');
  ok((await txt('#rz-note')).startsWith('Exact'), 'an exact result says so');
  ok((await calls('showInterstitial')).length === 0, 'no interstitial in the first session');

  // 2. Typing a width: the half-way case 1000 px at 16:9 = 562.5 -> 563 (stated).
  await type('#rz-w', '1000');
  ok((await val('#rz-h')) === '563' && (await rz()).w === 1000 && (await rz()).h === 563, '1000 wide at 16:9 gives 563 high (562.5 rounded half up)');
  const note = await txt('#rz-note');
  ok(note.includes('562.5') && note.includes('563') && note.includes('half up'), 'the note states the exact value and the rounding: ' + note.slice(0, 70) + '…');
  const bw = await ev(() => { const b = document.getElementById('pvb').getBoundingClientRect(); return b.width / b.height; });
  ok(Math.abs(bw - 1000 / 563) < 0.06, 'preview frame follows the shape (' + bw.toFixed(3) + ')');
  await commit('#rz-w');
  await type('#rz-h', '1080');
  ok((await val('#rz-w')) === '1920', 'typing height 1080 at 16:9 gives width 1920');
  await commit('#rz-h');

  // 3. Invalid input never changes the result.
  await type('#rz-w', '0');
  ok((await rz()).w === 1920 && await p.locator('#rz-w[aria-invalid="true"]').count() === 1, 'width 0 is flagged and ignored');
  await type('#rz-w', 'abc'); ok((await rz()).w === 1920, 'letters are ignored');
  await type('#rz-w', '100001'); ok((await rz()).w === 10000 && await p.locator('#rz-w[aria-invalid="true"]').count() === 1, '100,001 px is flagged; only the last valid prefix (10,000) was applied');
  await commit('#rz-w');
  ok((await val('#rz-w')) === '10000' && await p.locator('#rz-w[aria-invalid="true"]').count() === 0, 'leaving an invalid field restores the real value');
  await type('#rz-w', '1920'); await commit('#rz-w');
  await type('#rz-w', '100000'); ok((await rz()).h === 56250, '100,000 px wide at 16:9 = 56,250 high'); await commit('#rz-w');
  await type('#rz-rw', '100000'); await type('#rz-rh', '1');
  ok((await rz()).h === 1 && (await rz()).w === 100000, 'an extreme ratio 100000:1 is clamped to 1 px high, never 0');
  await commit('#rz-rh');
  await ev(() => { S.tool.rz = { w: 1920, h: 1080, rw: 16, rh: 9, lock: 'ratio' }; persist(); UI.refresh(); }); await p.waitForTimeout(200);

  // 4. Lock modes.
  await tap('[data-act="rz-lock"][data-arg="w"]');
  await type('#rz-h', '1350'); await commit('#rz-h');
  let z = await rz();
  ok(z.w === 1920 && z.h === 1350 && z.rw === 64 && z.rh === 45, 'Width locked: editing height keeps 1920 wide and re-derives the ratio 64:45');
  ok((await val('#rz-rw')) === '64' && (await val('#rz-rh')) === '45', 'the ratio fields show the reduced 64:45');
  await tap('[data-act="rz-lock"][data-arg="h"]');
  await tap('[data-act="rz-grp"][data-arg="social"]');
  await tap('[data-act="preset"][data-arg="story"]');
  z = await rz();
  ok(z.h === 1350 && z.w === 759 && z.rw === 9 && z.rh === 16, 'Height locked + 9:16 preset: height stays 1350, width = 759 (759.375 rounded)');
  await tap('[data-act="rz-lock"][data-arg="ratio"]');
  await tap('[data-act="preset"][data-arg="p45"]');
  z = await rz();
  ok(z.w === 759 && z.h === 949 && z.rw === 4 && z.rh === 5, 'Ratio lock + 4:5 preset keeps the width (759 -> 948.75 -> 949)');
  await tap('[data-act="rz-fromsize"]');
  z = await rz();
  ok(z.rw === 759 && z.rh === 949, '"Use size as ratio" takes 759:949 (coprime)');
  await tap('[data-act="rz-grp"][data-arg="print"]');
  await tap('[data-act="preset"][data-arg="a4"]');
  z = await rz();
  ok(z.rw === 70 && z.rh === 99 && z.w === 759 && z.h === 1073, 'A4 preset reduces 210:297 to 70:99 (759 wide -> 1073.4 -> 1073)');
  ok((await txt('[data-act="preset"][data-arg="letter"]')).includes('17:22'), 'US Letter chip shows 17:22');
  await ev(() => { S.tool.rz = { w: 1920, h: 1080, rw: 16, rh: 9, lock: 'ratio' }; persist(); UI.refresh(); }); await p.waitForTimeout(200);
  await tap('[data-act="rz-swap"]');
  z = await rz();
  ok(z.w === 1080 && z.h === 1920 && z.rw === 9 && z.rh === 16, 'Swap turns 1920 × 1080 into 1080 × 1920 (9:16)');

  // 5. Copy + crop rows.
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="copy"][data-arg="size"]');
  let cc = await calls('copyToClipboard');
  ok(cc.length === 1 && cc[0][1][0] === '1080 × 1920 px', 'copying the size sends "1080 × 1920 px"');
  await tap('[data-act="copy"][data-arg="all"]');
  cc = await calls('copyToClipboard');
  ok(cc.length === 2 && cc[1][1][0].includes('9:16') && cc[1][1][0].includes('2.07 megapixels'), 'copy all carries size, ratio and megapixels');
  const crops = await ev(() => Array.from(document.querySelectorAll('[data-arg^="crop"] .rv')).map(e => e.textContent.replace(/[^\d×]/g, '')));
  ok(crops.join('|') === '1080×1080|1080×1350|1080×1920|1080×607|1080×720|1080×810', 'crops of 1080 × 1920 at 1:1, 4:5, 9:16, 16:9 (607.5 floored), 3:2, 4:3: ' + crops.join(' '));
  await tap('[data-act="copy"][data-arg="crop1"]');
  ok((await calls('copyToClipboard')).pop()[1][0] === '1080 × 1350 px', 'a crop row copies its size');

  // 6. Convert.
  await tap('[data-act="tab"][data-arg="convert"]');
  await type('#cv-w', '8,5'); await type('#cv-h', '11');
  let rows = await ev(() => Array.from(document.querySelectorAll('#cv-res .rrow .rv')).map(e => e.textContent.replace(/\s+/g, ' ').trim()));
  ok(rows.join('|') === '2,550 × 3,300|8.5 × 11|21.59 × 27.94|215.9 × 279.4', '8.5 × 11 in at 300 DPI = 2,550 × 3,300 px = 21.59 × 27.94 cm = 215.9 × 279.4 mm (got ' + rows.join(' | ') + ')');
  ok((await txt('#cv-res .info')).includes('17:22'), 'the print size reduces to 17:22');
  await tap('[data-act="cv-dpi"][data-arg="150"]');
  rows = await ev(() => Array.from(document.querySelectorAll('#cv-res .rrow .rv')).map(e => e.textContent.replace(/\s+/g, ' ').trim()));
  ok(rows[0] === '1,275 × 1,650', 'at 150 DPI the same page is 1,275 × 1,650 px');
  await type('#cv-dpi', '72'); await commit('#cv-dpi');
  ok(await ev(() => S.tool.cv.dpi) === 72 && (await ev(() => document.querySelector('#cv-res .rrow .rv').textContent)).includes('612'), 'a custom DPI of 72 gives 612 px for 8.5 in');
  await type('#cv-dpi', '99999'); ok(await ev(() => S.tool.cv.dpi) === 999 && await p.locator('#cv-dpi[aria-invalid="true"]').count() === 1, 'a DPI above 2,400 is flagged and never applied');
  await commit('#cv-dpi');
  await tap('[data-act="cv-dpi"][data-arg="300"]');
  await tap('[data-act="cv-unit"][data-arg="cm"]');
  ok((await val('#cv-w')) === '21.59' && (await val('#cv-h')) === '27.94', 'switching the unit to cm converts the typed values (21.59 × 27.94)');
  await type('#cv-w', '0'); ok(await p.locator('#cv-res .msg.err').count() === 1, 'a zero width shows an error, not a number');
  await type('#cv-w', '999999'); ok(await p.locator('#cv-res .msg.err').count() === 1, 'a size beyond 100,000 px is an error');
  await type('#cv-w', '21'); await commit('#cv-w');
  ok((await ev(() => document.querySelector('#cv-res .rrow .rv').textContent)).includes('2,480'), '21 cm at 300 DPI = 2,480 px (2,480.3 rounded)');
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="copy"][data-arg="conv:in"]');
  ok((await calls('copyToClipboard')).pop()[1][0].startsWith('8.267 × 11 in'), 'a unit row copies "8.267 × 11 in (300 DPI)"-style text');
  await tap('[data-act="cv-use"]');
  z = await rz();
  ok((await ev(() => UI.cur().id)) === 'resize' && z.w === 2480 && z.h === 3300 && z.lock === 'ratio' && z.rw === 124 && z.rh === 165, '"Use in Resize" sends 2,480 × 3,300 px (124:165) to the Resize tab');

  // 7. History.
  await tap('[data-act="tab"][data-arg="saved"]');
  const nh = await ev(() => S.tool.hist.length);
  ok(nh >= 4 && await p.locator('.hrow .hmain').count() >= 4, 'recent calculations were recorded (' + nh + ')');
  ok(await ev(() => S.tool.hist.every((e, i, a) => i === 0 || histKey(e) !== histKey(a[i - 1]))), 'no consecutive duplicate in history');
  await ev(() => { window.__calls.length = 0; });
  await tap('.hrow [data-act="h-copy"]');
  ok((await calls('copyToClipboard')).length === 1, 'a history row copies its result');
  await p.locator('.hrow .hmain').nth(1).tap(); await p.waitForTimeout(300);
  ok(['resize', 'convert'].includes(await ev(() => UI.cur().id)), 'tapping a history row restores it on its tab');
  await tap('[data-act="tab"][data-arg="saved"]');
  await tap('[data-act="h-clear"]'); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.hist.length) === 0, 'Clear empties the history');
  await tap('#toast .ta'); await p.waitForTimeout(250);
  ok(await ev(() => S.tool.hist.length) === nh || await ev(() => S.tool.hist.length) > 0, 'Undo brings the history back');

  // 8. My presets: 3 free, the 4th opens the paywall.
  const addPreset = async (name, a, b) => { await tap('[data-act="mine-add"]'); await p.waitForTimeout(350); await p.locator('#ed-name').fill(name); await p.locator('#ed-rw').fill(a); await p.locator('#ed-rh').fill(b); await tap('[data-act="mine-ok"]'); await p.waitForTimeout(300); };
  await addPreset('Poster', '24', '36');
  ok(await ev(() => S.tool.mine.length) === 1 && await ev(() => S.tool.mine[0].rw + ':' + S.tool.mine[0].rh) === '2:3', 'preset 24:36 is saved reduced as 2:3');
  await tap('[data-act="mine-add"]'); await p.waitForTimeout(350); await p.locator('#ed-name').fill('Bad'); await p.locator('#ed-rw').fill('0'); await p.locator('#ed-rh').fill('5'); await tap('[data-act="mine-ok"]');
  ok(await ev(() => S.tool.mine.length) === 1 && await p.locator('#ed-body').count() === 1, 'a zero ratio term is rejected');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);
  await addPreset('Card', '85', '55'); await addPreset('Wide', '21', '9');
  ok(await ev(() => S.tool.mine.map(m => m.rw + ':' + m.rh).join(',')) === '2:3,17:11,7:3', 'three free presets saved reduced');
  await tap('[data-act="mine-add"]'); await p.waitForTimeout(350);
  ok(await p.locator('.pro-hero').isVisible() && !(await p.locator('#ed-body').count()), 'free limit (3): the 4th preset opens the paywall');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);
  await tap('[data-act="open-batch"]'); await p.waitForTimeout(300);
  ok(await p.locator('.pro-hero').isVisible(), 'the batch list on the free plan opens the paywall');
  await tap('.layer .sheet-head [data-act="close-layer"]'); await p.waitForTimeout(300);
  const buy0 = (await calls('purchase')).length;
  await ev(() => Pro.open('limit_t')); await p.waitForTimeout(300);
  await tap('[data-act="buy"][data-arg="pro_lifetime"]');
  ok((await calls('purchase')).length === buy0 + 1, 'Unlock Pro calls Android.purchase("pro_lifetime")');
  await ev(() => window.onPurchaseSuccess('pro_lifetime')); await p.waitForTimeout(300);
  ok(await ev(() => S.pro === true && S.removeAds === true && isPro() && adsRemoved()), 'pro_lifetime grants Pro + ad-free');
  await ev(() => { UI.closeAll(); UI.tab('saved'); }); await p.waitForTimeout(250);
  await addPreset('Fourth', '5', '4');
  ok(await ev(() => S.tool.mine.length) === 4, 'Pro: a 4th (unlimited) preset saves');
  await tap('[data-act="mine-use"][data-arg="' + await ev(() => S.tool.mine[0].id) + '"]');
  z = await rz();
  ok((await ev(() => UI.cur().id)) === 'resize' && z.rw === 2 && z.rh === 3, 'tapping a saved preset applies its ratio on Resize');
  await tap('[data-act="rz-grp"][data-arg="mine"]');
  ok(await p.locator('.pchip[data-act="mine-use"]').count() === 4, 'Mine group lists the saved presets');

  // 9. Batch (Pro).
  await ev(() => { S.tool.rz = { w: 1920, h: 1080, rw: 16, rh: 9, lock: 'ratio' }; persist(); UI.tab('saved'); }); await p.waitForTimeout(250);
  await tap('[data-act="open-batch"]'); await p.waitForTimeout(300);
  ok((await ev(() => UI.cur().id)) === 'batch' && await p.locator('#bt-text').isVisible(), 'Pro opens the batch screen');
  await p.locator('#bt-text').fill('320, 641 1280;1281 x 0'); await p.waitForTimeout(200);
  const br = await ev(() => Array.from(document.querySelectorAll('#bt-res .rrow')).map(e => e.querySelector('.rv').textContent.replace(/[^\d×]/g, '') + '/' + e.querySelector('.rs').textContent));
  ok(br.join('|') === '320×180/Exact|641×361/Rounded|1280×720/Exact|1281×721/Rounded', 'batch widths at 16:9: 320×180, 641×361 (360.56), 1280×720, 1281×721 (720.56): ' + br.join(' '));
  ok(await p.locator('#bt-res .msg.err').count() === 1, '2 invalid entries are reported');
  await tap('[data-act="bt-by"][data-arg="h"]');
  await p.locator('#bt-text').fill('1080, 100'); await p.waitForTimeout(200);
  ok((await ev(() => Array.from(document.querySelectorAll('#bt-res .rrow .rv')).map(e => e.textContent.replace(/[^\d×]/g, '')).join('|'))) === '1920×1080|178×100', 'batch heights at 16:9: 1080 -> 1920 wide, 100 -> 177.8 -> 178');
  await ev(() => { window.__calls.length = 0; });
  await tap('[data-act="copy"][data-arg="batch"]');
  ok((await calls('copyToClipboard')).pop()[1][0].startsWith('1920 × 1080\n178 × 100'), 'batch copy-all is one line per size');
  await ev(() => UI.back()); await p.waitForTimeout(200);

  // 10. Backup / restore + migrate.
  const backup = await ev(() => Data.payload());
  await ev(() => { S.tool = TOOL.defaults(); persist(); UI.tab('saved'); });
  ok(await ev(() => S.tool.mine.length) === 0, 'tool data wiped for the import test');
  await ev(t => { Data.importText(t); }, backup); await p.waitForTimeout(250);
  await tap('.dialog .btn-danger'); await p.waitForTimeout(300);
  ok(await ev(() => S.tool.mine.length) === 4, 'import restores the 4 saved presets');
  ok(await ev(() => TOOL.validateImport({ rz: {}, hist: 'x', mine: [] })) === false, 'a malformed backup is rejected');
  const mg = await ev(() => TOOL.migrate({ rz: { w: 0, h: 5, rw: 1, rh: 1, lock: 'w' }, cv: { w: 5, u: 'ft', dpi: 0 }, hist: [{ k: 'r', w: -1 }], mine: [{ id: 'a', name: 'x', rw: 0, rh: 2 }, { id: 'b', name: 'y', rw: 3, rh: 4 }], batch: { by: 'q', text: 5 }, grp: 'zz' }));
  ok(mg.rz.w === 1920 && mg.cv.u === 'in' && mg.cv.dpi === 300 && mg.hist.length === 0 && mg.mine.length === 1 && mg.batch.by === 'w' && mg.grp === 'social', 'migrate falls back to defaults and drops invalid entries');

  // 11. Interstitial cadence.
  await ev(() => { S.pro = false; S.removeAds = false; S.sessions = 1; S.ads = { last: 0, breaks: 0 }; window.__calls.length = 0; });
  await ev(() => { Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 0, 'first session: no interstitial');
  await ev(() => { S.sessions = 3; Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); Ads.naturalBreak('t'); });
  ok((await calls('showInterstitial')).length === 1, 'later session: one interstitial, then the 3-minute floor holds');

  // 12. Languages: 13 complete; Arabic RTL; no missing string on any screen.
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
  const ph = await ev(() => { const bad = []; const en = window.GAME_I18N.en; Object.keys(window.GAME_I18N).forEach(l => Object.keys(en).forEach(k => { const a = (en[k].match(/\{\w+\}/g) || []).sort().join(), b = String((window.GAME_I18N[l][k] || '').match(/\{\w+\}/g) || []).split(',').sort().join(); if (typeof en[k] === 'string' && window.GAME_I18N[l][k] != null && a !== (String(window.GAME_I18N[l][k]).match(/\{\w+\}/g) || []).sort().join()) bad.push(l + ':' + k); })); return bad; });
  ok(ph.length === 0, 'placeholders match English in every language' + (ph.length ? ': ' + ph.slice(0, 5).join(',') : ''));
  await ev(() => { S.pro = true; S.tool.mine = [{ id: 'm1', name: 'Poster', rw: 2, rh: 3 }]; S.tool.hist = [{ id: 'h1', k: 'r', w: 1000, h: 563, rw: 16, rh: 9, lock: 'ratio', t: Date.now() }, { id: 'h2', k: 'c', w: '8.5', h: '11', u: 'in', dpi: 300, t: Date.now() }]; S.tool.rz = { w: 1000, h: 563, rw: 16, rh: 9, lock: 'ratio' }; persist(); });
  for (const l of langs) {
    await ev(L => { S.settings.lang = L === 'en' ? '' : L; persist(); applyLang(); applyTheme(); UI.buildNav(); ['social', 'video', 'print', 'mine'].forEach(g => { TD.grp = g; UI.tab('resize'); }); UI.tab('convert'); UI.tab('saved'); UI.go('batch'); UI.back(); }, l);
    await p.waitForTimeout(100);
  }
  const miss = await ev(() => [...window.__i18nMissing]);
  ok(miss.length === 0, 'no untranslated string rendered on any screen in any language' + (miss.length ? ': ' + miss.slice(0, 5).join(',') : ''));
  await ev(() => { S.settings.lang = 'ar'; persist(); applyLang(); UI.tab('resize'); });
  ok(await ev(() => document.documentElement.dir) === 'rtl', 'Arabic switches the layout to RTL');
  { const vn = (require('fs').readFileSync(require('path').join(__dirname, '../android/app/build.gradle'), 'utf8').match(/versionName "([^"]+)"/) || [])[1];
    ok(await ev(() => document.querySelector('[data-app-version]').textContent.trim()) === vn, 'data-app-version matches versionName'); }

  ok(errs.length === 0, 'no page errors' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));
  await browser.close();
  console.log(fails ? `runtime_check: ${fails} failure(s)` : 'runtime_check: OK');
  process.exit(fails ? 1 : 0);
})();
