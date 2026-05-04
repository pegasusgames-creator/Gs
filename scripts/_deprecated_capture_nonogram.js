#!/usr/bin/env node
/**
 * DEPRECATED — DO NOT RUN.
 *
 * Headless Chromium / Puppeteer is no longer permitted for store
 * screenshot capture. See:
 *   - docs/QUALITY_PLAYBOOK.md §7.0 "Capture method: emulator only"
 *   - docs/SHIP_GAME.md §3.6 "Why emulator, not headless Chromium"
 *   - CLAUDE.md "Things to flag to the user"
 *
 * The canonical capture is `python3 scripts/capture_screenshots.py
 * Nonogram` against a real Android emulator. If no AVD is available,
 * surface that as a hard blocker — do NOT fall back to this file.
 *
 * Left in the repo only as a historical artifact so future readers can
 * see what the rejected approach looked like.
 */
process.stderr.write([
  'capture_nonogram.js is deprecated.',
  'Use: python3 scripts/capture_screenshots.py Nonogram',
  'See QUALITY_PLAYBOOK.md §7.0 for why headless Chromium is forbidden.',
  '',
].join('\n'));
process.exit(2);

/* eslint-disable */ /* Original Puppeteer source kept below for reference; never executed. */
const puppeteer = require('/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');

const BASE = '/home/pgs/Documents/Gs';
const HTML = `file://${BASE}/Nonogram/android/app/src/main/assets/game.html`;
const OUT  = path.join(BASE, 'Nonogram/store/screenshots/phone/raw');

fs.mkdirSync(OUT, { recursive: true });

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
    headless: 'new',
  });

  // SHIP_GAME §3.1.1 — pre-seed localStorage so Stats/Missions/Levels show
  // mid-game progression instead of zeros. Run BEFORE every page.goto so it
  // takes effect on the first paint.
  function seedScript() {
    try {
      const today = new Date().toISOString().slice(0, 10);
      localStorage.setItem('ls_v2', JSON.stringify({n: 7, d: today, ach: []}));
      // Engine state. Most apps store it under 'state' or 'nonogramState';
      // write both so whichever the game reads, it gets seeded.
      const completed = [];
      for (let i = 1; i <= 47; i++) completed.push(i);
      const threeStar = [1,2,3,5,6,8,11,15,18,22,27,33,40,46];
      const seeded = {
        currentLevel: 348,         // 348 is in the 20×20 band (largest grid)
        coins: 247,
        lives: 5,
        completedLevels: completed,
        threeStarLevels: threeStar,
        totalSolved: completed.length,
        starsEarned: completed.length * 2 + threeStar.length,
        dailyChallengeStreak: 7,
        unlocks: { themes: ['paper','ink','dawn'] },
      };
      localStorage.setItem('nonogramState', JSON.stringify(seeded));
      localStorage.setItem('state', JSON.stringify(seeded));
      // Mission progress (keys mirror the in-app mission ids):
      localStorage.setItem('mission_solver_progress', '3');
      localStorage.setItem('mission_dedicated_progress', '12');
      localStorage.setItem('mission_streak_progress', '1');
      localStorage.setItem('mission_perfectionist_done', 'true');
    } catch (e) {}
  }

  function hideOverlaysScript() {
    try {
      ['ls-overlay','tutOverlay','overlay-daily','overlay-error','overlay-nolives','overlay-win'].forEach(id => {
        const el = document.getElementById(id); if (el) el.style.display = 'none';
      });
    } catch (e) {}
  }

  async function shoot(file, action) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1080, height: 2400, deviceScaleFactor: 1 });
    // Inject seed BEFORE page load so the game reads pre-populated state.
    await page.evaluateOnNewDocument(seedScript);
    await page.goto(HTML, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.evaluate(hideOverlaysScript);
    await sleep(450);
    if (action) {
      try { await page.evaluate(action); } catch (e) {
        console.error(`action failed for ${file}:`, e.message);
      }
      await sleep(900);
      await page.evaluate(hideOverlaysScript);
      // Force layout recalc so canvas resizes after any screen swap.
      await page.evaluate(() => {
        if (typeof window.resizeCanvas === 'function') {
          try { window.resizeCanvas(); } catch (e) {}
        }
      });
      await sleep(250);
    }
    const dest = path.join(OUT, file);
    await page.screenshot({ path: dest, type: 'png' });
    await page.close();
    console.log(`wrote ${dest}`);
  }

  // Helper: fill ~60% of a level's solution into currentGrid for mid-progression.
  // Uses the in-app `__nonoFillSolution` helper (closes over the script-local
  // `currentGrid`/`drawCanvas` that aren't on window).
  function midProgressionAction(levelId, ratio) {
    return `(async function(){
      if (typeof window.startLevel !== 'function') return;
      window.startLevel(${levelId});
      if (typeof window.stopTimer === 'function') window.stopTimer();
      // Wait one frame so showScreen('game')'s setTimeout(resizeCanvas) fires
      await new Promise(r => requestAnimationFrame(() => r()));
      if (typeof window.__nonoFillSolution === 'function') {
        window.__nonoFillSolution(${ratio});
      }
    })();`;
  }

  // 07 — menu (no action needed)
  await shoot('07.png', () => { /* default screen is menu */ });

  // 06 — level select
  await shoot('06.png', () => { window.showScreen && window.showScreen('levelselect'); });

  // 05 — stats
  await shoot('05.png', () => { window.showScreen && window.showScreen('stats'); });

  // 04 — Daily Challenge (matches the "Daily Picross" headline)
  await shoot('04.png', new Function(`
    return (async function(){
      if (typeof window.startDailyChallenge === 'function') {
        try {
          window.startDailyChallenge();
          if (typeof window.stopTimer === 'function') window.stopTimer();
          await new Promise(r => requestAnimationFrame(() => r()));
          if (typeof window.__nonoFillSolution === 'function') {
            window.__nonoFillSolution(0.45);
          }
        } catch (e) {}
      } else if (window.showScreen) {
        window.showScreen('missions');
      }
    })();
  `));

  // 02 — early-mid gameplay: 10×10 grid (level 90 is in 10×10 band) at ~50% solve
  await shoot('02.png', new Function(midProgressionAction(90, 0.50)));

  // 01 — DEEP gameplay: 20×20 (largest grid the generator produces), 60% solved
  await shoot('01.png', new Function(midProgressionAction(348, 0.60)));

  // 03 — level complete: fully solve a small level then show the win overlay
  await shoot('03.png', new Function(`
    return (async function(){
      if (typeof window.startLevel === 'function') {
        try {
          window.startLevel(8);
          if (typeof window.stopTimer === 'function') window.stopTimer();
          await new Promise(r => requestAnimationFrame(() => r()));
          if (typeof window.__nonoFillSolution === 'function') {
            window.__nonoFillSolution(1.0);
          }
        } catch (e) {}
      }
      if (typeof window.showOverlay === 'function') {
        try { window.showOverlay('overlay-win'); return; } catch (e) {}
      }
      if (window.showScreen) window.showScreen('shop');
    })();
  `));

  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
