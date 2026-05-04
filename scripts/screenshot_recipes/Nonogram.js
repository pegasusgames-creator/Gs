// Drive Nonogram game.html in headless Chrome and capture 7 distinct states.
const path = require('path');
const fs = require('fs');
const PUP = '/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer';
const puppeteer = require(PUP);

const APP = '/home/pgs/Documents/Gs/Nonogram';
const GAME_URL = 'file://' + APP + '/android/app/src/main/assets/game.html';
const OUT_DIR = APP + '/store/screenshots/phone/raw';
const VIEWPORT = { width: 540, height: 1200, deviceScaleFactor: 2 };

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
           '--hide-scrollbars', '--mute-audio', `--window-size=${VIEWPORT.width},${VIEWPORT.height}`]
  });
  const page = await browser.newPage();
  await page.setViewport(VIEWPORT);
  page.on('console', msg => { if (msg.type() === 'error') console.error('[page]', msg.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));

  // Nonogram uses an array of completed level IDs (not a map).
  const completed = Array.from({length: 32}, (_, i) => i + 1);
  const levelStars = {};
  for (const id of completed) levelStars[id] = (id % 3 === 0) ? 3 : 2;

  const seedState = {
    currentLevel: 33,
    completedLevels: completed,
    levelStars: levelStars,
    coins: 880,
    lives: 5,
    lastLifeTime: Date.now(),
    removeAds: false,
    hintPack: 3,
    soundEnabled: true,
    musicEnabled: false,
    dailyChallengeDate: '',
    dailyChallengeStreak: 5,
    unlimitedLivesUntil: 0,
    unlimitedLivesForever: false,
    activeTheme: 'default',
    lastLevelProgress: null
  };

  await page.goto(GAME_URL, { waitUntil: 'load' });
  await page.evaluate((s) => {
    localStorage.setItem('nonogram_state', JSON.stringify(s));
    localStorage.setItem('xstarter_seen', '1');
    localStorage.setItem('ls_shown_today', new Date().toDateString());
  }, seedState);
  await page.goto(GAME_URL, { waitUntil: 'load' });
  await sleep(1500);

  async function dismissModals(keep) {
    keep = keep || [];
    await page.evaluate((keep) => {
      ['starterPackModal', 'ls-overlay', 'tutOverlay'].forEach(id => {
        if (keep.includes(id)) return;
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
      });
      ['overlay-win', 'overlay-error', 'overlay-nolives', 'overlay-daily'].forEach(id => {
        if (keep.includes(id)) return;
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
      });
    }, keep);
  }

  async function shoot(slot, setupFn, label, keep) {
    await dismissModals();
    await page.evaluate(setupFn);
    await sleep(750);
    await dismissModals(keep);
    await sleep(200);
    const out = path.join(OUT_DIR, slot + '.png');
    await page.screenshot({ path: out, type: 'png', captureBeyondViewport: false });
    const stat = fs.statSync(out);
    console.log(`  ${slot}.png  ${stat.size.toString().padStart(7)} B  ← ${label}`);
  }

  // 01 — mid gameplay (Nonogram's showScreen takes name w/o 'screen-' prefix)
  await shoot('01', () => { window.startLevel(20); }, 'mid gameplay (level 20)');
  // 02 — early gameplay
  await shoot('02', () => { window.startLevel(5); }, 'early gameplay (level 5)');
  // 03 — win overlay (level complete)
  await shoot('03', () => {
    window.startLevel(15);
    const win = document.getElementById('overlay-win');
    const coins = document.getElementById('win-coins-text');
    const time = document.getElementById('win-time-text');
    if (coins) coins.textContent = '+25 🪙';
    if (time) time.textContent = 'Solved in 0:42';
    if (win) win.classList.add('active');
  }, 'level complete', ['overlay-win']);
  // 04 — missions panel
  await shoot('04', () => { window.showScreen('missions'); }, 'missions panel');
  // 05 — stats panel
  await shoot('05', () => { window.showScreen('stats'); }, 'stats panel');
  // 06 — level select grid
  await shoot('06', () => { window.showScreen('levelselect'); }, 'level select grid');
  // 07 — menu
  await shoot('07', () => { window.showScreen('menu'); }, 'main menu');

  await browser.close();
  console.log('done');
})().catch(e => { console.error(e); process.exit(1); });
