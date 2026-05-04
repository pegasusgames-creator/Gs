// Drive UnblockPuzzle game.html in headless Chrome and capture 7 distinct states.
const path = require('path');
const fs = require('fs');
const PUP = '/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer';
const puppeteer = require(PUP);

const APP = '/home/pgs/Documents/Gs/UnblockPuzzle';
const GAME_URL = 'file://' + APP + '/android/app/src/main/assets/game.html';
const OUT_DIR = APP + '/store/screenshots/phone/raw';
// 540×1200 CSS px @ DPR 2 → outputs 1080×2400 image but layout believes
// it's on a phone-sized device, so card sizes that look right on a real
// Android phone don't render comically small under headless Chrome.
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
  page.on('console', msg => {
    if (msg.type() === 'error') console.error('[page]', msg.text());
  });
  page.on('pageerror', e => console.error('[pageerror]', e.message));

  // Pre-seed save state so level select / stats / progress look populated.
  const seedState = {
    currentLevel: 88,
    completedLevels: Object.fromEntries(Array.from({length:87}, (_,i)=>[i, true])),
    levelStars: Object.fromEntries(Array.from({length:87}, (_,i)=>[i, (i % 3) === 0 ? 3 : (i % 3) === 1 ? 2 : 3])),
    levelMoves: Object.fromEntries(Array.from({length:87}, (_,i)=>[i, 8 + (i % 12)])),
    coins: 1240,
    lives: 5,
    lastLifeTime: Date.now(),
    removeAds: false,
    dailyChallengeDate: '',
    dailyChallengeStreak: 6,
    soundEnabled: true,
    musicEnabled: false,
    unlimitedLivesUntil: 0,
    activeTheme: 'default',
    lastLevelProgress: null
  };
  // Set localStorage by visiting the file's origin first.
  await page.goto(GAME_URL, { waitUntil: 'load' });
  await page.evaluate((s) => {
    localStorage.setItem('unblock_save', JSON.stringify(s));
    // Dismiss recurring promos so they don't cover the screen.
    localStorage.setItem('xstarter_seen', '1');
    localStorage.setItem('ls_shown_today', new Date().toDateString());
    // Pre-seed weekly bonus progress so the Missions panel shows real progress
    var d = new Date(); d.setHours(0,0,0,0); d.setDate(d.getDate()-d.getDay());
    var weekStart = d.toISOString().slice(0,10);
    localStorage.setItem('unblock_weekly_v1', JSON.stringify({weekStart: weekStart, progress: 4, claimed: false}));
  }, seedState);
  // Reload so state is consumed by loadState() at bootstrap.
  await page.goto(GAME_URL, { waitUntil: 'load' });
  await sleep(1500);

  async function dismissModals(keep) {
    keep = keep || [];
    await page.evaluate((keep) => {
      // starter pack uses inline display:flex to show
      ['starterPackModal', 'ls-overlay'].forEach(id => {
        if (keep.includes(id)) return;
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
      });
      // overlays use the .active class
      ['noLivesOverlay', 'hintOverlay', 'winOverlay'].forEach(id => {
        if (keep.includes(id)) return;
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
      });
    }, keep);
  }

  async function shoot(slot, setupFn, label, keep) {
    await dismissModals();
    await page.evaluate(setupFn);
    await sleep(700);
    await dismissModals(keep);
    await sleep(200);
    const out = path.join(OUT_DIR, slot + '.png');
    await page.screenshot({ path: out, type: 'png', captureBeyondViewport: false });
    const stat = fs.statSync(out);
    console.log(`  ${slot}.png  ${stat.size.toString().padStart(7)} B  ← ${label}`);
  }

  // 01 — deep gameplay (level 100)
  await shoot('01', () => { window.startLevel(99); }, 'deep gameplay (level 100)');
  // 02 — early gameplay (level 4)
  await shoot('02', () => { window.startLevel(3); }, 'early gameplay (level 4)');
  // 03 — level complete modal with 3 stars over a played level
  await shoot('03', () => {
    window.startLevel(45);
    // Fill the new structured win overlay (3-star, perfect solve, +25 coins)
    const row = document.getElementById('winStarsRow');
    if (row) row.querySelectorAll('.win-star').forEach(s => s.classList.remove('dim'));
    const rank = document.getElementById('winRank'); if (rank) rank.textContent = 'PERFECT SOLVE';
    const reward = document.getElementById('winReward'); if (reward) reward.textContent = '+25';
    const info = document.getElementById('winInfo'); if (info) info.textContent = 'Solved in 11 moves';
    document.getElementById('winOverlay').classList.add('active');
  }, 'level complete (3 stars)', ['winOverlay']);
  // 04 — Missions panel
  await shoot('04', () => { window.showScreen('missionsScreen'); }, 'missions panel');
  // 05 — Stats panel
  await shoot('05', () => { window.showScreen('statsScreen'); }, 'stats panel');
  // 06 — Level select grid
  await shoot('06', () => { window.showScreen('levelScreen'); }, 'level select grid');
  // 07 — Menu
  await shoot('07', () => { window.showScreen('menuScreen'); }, 'main menu');

  await browser.close();
  console.log('done');
})().catch(e => { console.error(e); process.exit(1); });
