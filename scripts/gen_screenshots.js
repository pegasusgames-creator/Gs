#!/usr/bin/env node
/**
 * Generate phone and tablet screenshots for all apps using Puppeteer.
 * Phone: 1080×1920, Tablet 7": 1200×1920, Tablet 10": 1600×2560
 */
const puppeteer = require('/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');

const BASE = '/home/pgs/Documents/Gs';

// Screenshot specs
const SIZES = {
  phone:    { width: 1080, height: 1920, dir: 'phone' },
  tablet7:  { width: 1200, height: 1920, dir: 'tablet' },
  tablet10: { width: 1600, height: 2560, dir: 'tablet' },
};

// Screenshot scenarios per app type — we capture 2-3 screenshots each
// For most apps: just screenshot the main page at load time (after 2s settle)

const apps = fs.readdirSync(BASE)
  .filter(d => {
    const htmlPath = path.join(BASE, d, 'android/app/src/main/assets/game.html');
    return fs.existsSync(htmlPath) && !d.startsWith('_');
  })
  .sort();

async function screenshotApp(browser, app) {
  const htmlPath = `file://${BASE}/${app}/android/app/src/main/assets/game.html`;
  const screenshotDir = `${BASE}/${app}/store/screenshots`;

  const phoneDir = path.join(screenshotDir, 'phone');
  const tabletDir = path.join(screenshotDir, 'tablet');
  fs.mkdirSync(phoneDir, { recursive: true });
  fs.mkdirSync(tabletDir, { recursive: true });

  // Skip if already has screenshots
  const phoneFiles = fs.existsSync(phoneDir) ? fs.readdirSync(phoneDir).filter(f => f.endsWith('.png')) : [];
  if (phoneFiles.length >= 2) {
    return `${app}: already has screenshots`;
  }

  const results = [];

  for (const [sizeName, spec] of Object.entries(SIZES)) {
    const page = await browser.newPage();
    await page.setViewport({ width: spec.width, height: spec.height, deviceScaleFactor: 1 });

    try {
      await page.goto(htmlPath, { waitUntil: 'domcontentloaded', timeout: 10000 });
      // Let app initialize
      await new Promise(r => setTimeout(r, 2000));

      const suffix = sizeName === 'tablet10' ? '-10' : (sizeName === 'tablet7' ? '-7' : '');
      const outDir = spec.dir === 'phone' ? phoneDir : tabletDir;
      const prefix = sizeName === 'tablet10' ? 'tablet-10_' : (sizeName === 'tablet7' ? 'tablet-7_' : 'phone_');

      // Screenshot 1: main screen
      const s1 = path.join(outDir, `${prefix}1-main.png`);
      await page.screenshot({ path: s1, fullPage: false });

      results.push(s1);
    } catch(e) {
      results.push(`${app}/${sizeName}: ERROR ${e.message.slice(0, 60)}`);
    }
    await page.close();
  }

  return `${app}: ${results.length} screenshots`;
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  let done = 0;
  const errors = [];

  // Process in batches of 5
  for (let i = 0; i < apps.length; i += 5) {
    const batch = apps.slice(i, i + 5);
    const results = await Promise.all(batch.map(app => screenshotApp(browser, app)));
    results.forEach(r => {
      if (r.includes('ERROR')) errors.push(r);
    });
    done += batch.length;
    if (done % 20 === 0 || done === apps.length) {
      console.log(`  ${done}/${apps.length} apps processed...`);
    }
  }

  await browser.close();

  console.log(`\nDone: ${done} apps`);
  if (errors.length) {
    console.log('Errors:');
    errors.forEach(e => console.log(' ', e));
  }
})();
