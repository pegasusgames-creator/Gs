#!/usr/bin/env node
/**
 * gen_screenshots_v2.js
 * Generates missing screenshots:
 * - phone/02_gameplay.png (1080x1920) — second screenshot via click interaction
 * - iphone_6_9/01_main.png (1320x2868)
 * - iphone_6_9/02_gameplay.png (1320x2868)
 * Skips apps that already have those files.
 */
const puppeteer = require('/home/pgs/.nvm/versions/node/v18.20.8/lib/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');

const BASE = '/home/pgs/Documents/Gs';
const SKIP = new Set(['_template', '_release', '__pycache__', '.git', '.idea', 'node_modules']);

const apps = fs.readdirSync(BASE)
  .filter(d => {
    if (SKIP.has(d) || d.startsWith('.') || d.startsWith('_')) return false;
    return fs.existsSync(path.join(BASE, d, 'android/app/src/main/assets/game.html'));
  })
  .sort();

const SIZES = [
  { key: 'phone',      width: 1080, height: 1920 },
  { key: 'iphone_6_9', width: 1320, height: 2868 },
];

async function screenshotApp(browser, app) {
  const htmlPath = `file://${BASE}/${app}/android/app/src/main/assets/game.html`;
  const ssRoot   = path.join(BASE, app, 'store', 'screenshots');
  const results  = [];

  for (const { key, width, height } of SIZES) {
    const dir = path.join(ssRoot, key);
    fs.mkdirSync(dir, { recursive: true });

    const s1 = path.join(dir, '01_main.png');
    const s2 = path.join(dir, '02_gameplay.png');
    const needS1 = !fs.existsSync(s1);
    const needS2 = !fs.existsSync(s2);
    if (!needS1 && !needS2) {
      results.push(`${key}: skip (both exist)`);
      continue;
    }

    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: 1 });
    try {
      await page.goto(htmlPath, { waitUntil: 'domcontentloaded', timeout: 12000 });
      await new Promise(r => setTimeout(r, 2500));

      if (needS1) {
        await page.screenshot({ path: s1, fullPage: false });
        results.push(`${key}: shot1 ok`);
      }

      if (needS2) {
        // Try to trigger some gameplay: click center, then a button
        try {
          // Click near center-bottom where buttons usually are
          await page.mouse.click(width / 2, height * 0.7);
          await new Promise(r => setTimeout(r, 800));
          // Try clicking the first visible button (if any)
          const btn = await page.$('button:not(#btn-remove-ads):not([style*="display: none"])');
          if (btn) {
            await btn.click();
            await new Promise(r => setTimeout(r, 800));
          }
        } catch (_) {}
        await new Promise(r => setTimeout(r, 500));
        await page.screenshot({ path: s2, fullPage: false });
        results.push(`${key}: shot2 ok`);
      }
    } catch (e) {
      results.push(`${key}: ERROR ${e.message.slice(0, 60)}`);
    }
    await page.close();
  }

  return `${app}: ${results.join(' | ')}`;
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  let done = 0;
  const errors = [];

  for (let i = 0; i < apps.length; i += 4) {
    const batch = apps.slice(i, i + 4);
    const results = await Promise.all(batch.map(app => screenshotApp(browser, app)));
    results.forEach(r => {
      if (r.includes('ERROR')) errors.push(r);
    });
    done += batch.length;
    if (done % 20 === 0 || done === apps.length) {
      process.stdout.write(`  ${done}/${apps.length} processed\n`);
    }
  }

  await browser.close();
  console.log(`\nDone: ${done} apps`);
  if (errors.length) {
    console.log('Errors:');
    errors.forEach(e => console.log(' ', e));
  }
})();
