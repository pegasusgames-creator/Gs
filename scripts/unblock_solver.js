#!/usr/bin/env node
'use strict';
/*
 * unblock_solver.js — BFS solver + solver-validated level generator for
 * UnblockPuzzle (6x6 sliding-block / Rush-Hour puzzle).
 *
 * Why this exists: the 2026-05-15 audit found 35/150 levels unsolvable and
 * 114/150 with a wrong `optimal` move count. Root cause — levels were
 * hand-authored with guessed move counts and no solver pass, and some put a
 * non-red horizontal block on the red car's exit row (row y=2), which can
 * never leave that row and permanently walls the exit lane.
 *
 * Board model (must match game.html exactly):
 *   - 6x6 grid. Red R = 2x1 horizontal, always on row y=2.
 *   - Win when red.x + red.w >= 6  (game.html checkWin()).
 *   - A block slides any number of empty cells along its axis; each
 *     reposition to a new cell = 1 move (game.html onPointerUp: one
 *     position change => moveCount++). Axis = horizontal if w>1, else
 *     vertical (matches game.html's `dragBlock.w > 1` test).
 *   - Block constructors: R(x)={x,y:2,w:2,h:1,isRed}; H(x,y,w)=1-row
 *     horizontal; V(x,y,h)=1-col vertical.
 *
 * HARD GENERATION RULE: no non-red horizontal block may occupy row y=2.
 *
 * CLI:
 *   node unblock_solver.js generate   — regenerate 150 levels, validate,
 *                                       splice into game.html, print report
 *   node unblock_solver.js check      — solve every level in game.html,
 *                                       assert solvable + optimal-exact
 */

const fs = require('fs');
const path = require('path');

const GRID = 6;
const HTML_PATH = path.join(__dirname, '..', 'UnblockPuzzle',
  'android', 'app', 'src', 'main', 'assets', 'game.html');

// ───────────────────────── seeded RNG ─────────────────────────
function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// ───────────────────────── core solver ─────────────────────────
// A block is {x,y,w,h,isRed}. Axis is horizontal iff w>1 (game rule).
function isHoriz(b) { return b.w > 1; }

function isWon(blocks) {
  for (const b of blocks) if (b.isRed) return b.x + b.w >= GRID;
  return false;
}

function stateKey(blocks) {
  let s = '';
  for (const b of blocks) s += (b.y * GRID + b.x) + ',';
  return s;
}

function buildOcc(blocks, skipIdx) {
  const g = new Uint8Array(GRID * GRID);
  for (let i = 0; i < blocks.length; i++) {
    if (i === skipIdx) continue;
    const b = blocks[i];
    for (let dy = 0; dy < b.h; dy++)
      for (let dx = 0; dx < b.w; dx++)
        g[(b.y + dy) * GRID + (b.x + dx)] = 1;
  }
  return g;
}

// Yields every state reachable in one move (one block slid along its axis).
function neighbors(blocks) {
  const out = [];
  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i];
    const g = buildOcc(blocks, i);
    if (isHoriz(b)) {
      for (let nx = b.x - 1; nx >= 0; nx--) {              // slide left
        if (g[b.y * GRID + nx]) break;
        out.push(cloneMove(blocks, i, nx, b.y));
      }
      for (let nx = b.x + 1; nx + b.w <= GRID; nx++) {     // slide right
        if (g[b.y * GRID + nx + b.w - 1]) break;
        out.push(cloneMove(blocks, i, nx, b.y));
      }
    } else {
      for (let ny = b.y - 1; ny >= 0; ny--) {              // slide up
        if (g[ny * GRID + b.x]) break;
        out.push(cloneMove(blocks, i, b.x, ny));
      }
      for (let ny = b.y + 1; ny + b.h <= GRID; ny++) {     // slide down
        if (g[(ny + b.h - 1) * GRID + b.x]) break;
        out.push(cloneMove(blocks, i, b.x, ny));
      }
    }
  }
  return out;
}

function cloneMove(blocks, i, nx, ny) {
  const c = new Array(blocks.length);
  for (let j = 0; j < blocks.length; j++) {
    const b = blocks[j];
    c[j] = (j === i)
      ? { x: nx, y: ny, w: b.w, h: b.h, isRed: b.isRed }
      : b;                                  // unchanged blocks shared
  }
  return c;
}

// BFS → minimum move count to win, or -1 if unsolvable (within maxDepth).
function solve(blocks, maxDepth = 60) {
  if (isWon(blocks)) return 0;
  const seen = new Set([stateKey(blocks)]);
  let frontier = [blocks];
  for (let depth = 1; depth <= maxDepth; depth++) {
    const next = [];
    for (const st of frontier) {
      for (const nb of neighbors(st)) {
        if (isWon(nb)) return depth;
        const k = stateKey(nb);
        if (seen.has(k)) continue;
        seen.add(k);
        next.push(nb);
      }
    }
    if (next.length === 0) return -1;        // reachable space exhausted
    frontier = next;
  }
  return -1;
}

// ───────────────────────── generator ─────────────────────────
function overlaps(blocks, nb) {
  for (const b of blocks)
    for (let dx = 0; dx < nb.w; dx++)
      for (let dy = 0; dy < nb.h; dy++) {
        const cx = nb.x + dx, cy = nb.y + dy;
        if (cx >= b.x && cx < b.x + b.w && cy >= b.y && cy < b.y + b.h)
          return true;
      }
  return false;
}

// Random valid board: red at x in 0..3 on row 2, then nBlocks-1 H/V blocks.
// HARD RULE enforced: a horizontal block is never placed on row y=2.
function generateBoard(rng, nBlocks) {
  const blocks = [{ x: Math.floor(rng() * 4), y: 2, w: 2, h: 1, isRed: true }];
  let tries = 0;
  while (blocks.length < nBlocks && tries < 240) {
    tries++;
    let nb;
    if (rng() < 0.5) {                       // vertical
      const h = rng() < 0.5 ? 2 : 3;
      nb = { x: Math.floor(rng() * GRID),
             y: Math.floor(rng() * (GRID - h + 1)),
             w: 1, h: h, isRed: false };
    } else {                                 // horizontal
      const w = rng() < 0.5 ? 2 : 3;
      const y = Math.floor(rng() * GRID);
      if (y === 2) continue;                 // never wall the exit lane
      nb = { x: Math.floor(rng() * (GRID - w + 1)), y: y,
             w: w, h: 1, isRed: false };
    }
    if (!overlaps(blocks, nb)) blocks.push(nb);
  }
  return blocks;
}

function shapeKey(blocks) {
  return blocks.map(b => b.x + '.' + b.y + '.' + b.w + '.' + b.h).join('|');
}

// Fill one difficulty band: random boards solved + filtered by depth window.
function generateBand(name, count, depthMin, depthMax, blkMin, blkMax, seed) {
  const rng = mulberry32(seed);
  const found = [];
  const seen = new Set();
  let attempts = 0, solves = 0, dMin = depthMin, dMax = depthMax;
  const MAX_ATTEMPTS = 1200000;
  while (found.length < count && attempts < MAX_ATTEMPTS) {
    attempts++;
    const n = blkMin + Math.floor(rng() * (blkMax - blkMin + 1));
    const blocks = generateBoard(rng, n);
    if (blocks.length < blkMin) continue;
    const k = shapeKey(blocks);
    if (seen.has(k)) continue;
    const d = solve(blocks);
    solves++;
    if (d >= dMin && d <= dMax) {
      seen.add(k);
      found.push({ blocks, optimal: d });
    }
    if (attempts % 120000 === 0 && found.length < count) {
      dMin = Math.max(2, dMin - 1);
      dMax = dMax + 2;
      console.error(`  [${name}] only ${found.length}/${count} after ` +
        `${attempts} tries — widening depth window to [${dMin},${dMax}]`);
    }
  }
  if (found.length < count)
    throw new Error(`band ${name}: only generated ${found.length}/${count}`);
  found.sort((a, b) => a.optimal - b.optimal);   // rising difficulty
  return { levels: found.slice(0, count), attempts, solves,
           widened: dMin !== depthMin || dMax !== depthMax,
           finalWindow: [dMin, dMax] };
}

// ───────────────────────── emit / splice ─────────────────────────
function blockToken(b) {
  if (b.isRed) return `R(${b.x})`;
  if (b.h === 1) return `H(${b.x},${b.y},${b.w})`;
  return `V(${b.x},${b.y},${b.h})`;
}

function levelLine(lvl) {
  // red first, then the rest in placement order
  const ordered = lvl.blocks.slice().sort((a, b) => (b.isRed ? 1 : 0) - (a.isRed ? 1 : 0));
  return `{blocks:[${ordered.map(blockToken).join(',')}],optimal:${lvl.optimal}}`;
}

function emitLevelsBody(bands) {
  const lines = [];
  let n = 0;
  for (const band of bands) {
    lines.push(`// ===== ${band.header} =====`);
    for (const lvl of band.levels) {
      n++;
      lines.push(`// Level ${n}`);
      lines.push(levelLine(lvl) + (n < 150 ? ',' : ','));
    }
  }
  return lines.join('\n');
}

function spliceIntoHtml(levelsBody) {
  const html = fs.readFileSync(HTML_PATH, 'utf8');
  const headMark = 'function V(x,y,h){return {x,y,w:1,h,isRed:false};}\n\nreturn [\n';
  const tailMark = '\n];\n})();';
  const iHead = html.indexOf(headMark);
  const iTail = html.indexOf(tailMark, iHead);
  if (iHead < 0 || iTail < 0)
    throw new Error('LEVELS IIFE markers not found in game.html');
  const out = html.slice(0, iHead + headMark.length) +
              levelsBody +
              html.slice(iTail);
  fs.writeFileSync(HTML_PATH, out);
}

// ───────────────────────── parse (for check) ─────────────────────────
function parseLevels(html) {
  const m = html.match(/return \[\n([\s\S]*?)\n\];\n\}\)\(\);/);
  if (!m) throw new Error('LEVELS array not found');
  const body = m[1];
  const levels = [];
  const lvlRe = /\{blocks:\[(.*?)\],optimal:(\d+)\}/g;
  let lm;
  while ((lm = lvlRe.exec(body))) {
    const blocks = [];
    const bRe = /R\((\d+)\)|H\((\d+),(\d+),(\d+)\)|V\((\d+),(\d+),(\d+)\)/g;
    let bm;
    while ((bm = bRe.exec(lm[1]))) {
      if (bm[1] !== undefined)
        blocks.push({ x: +bm[1], y: 2, w: 2, h: 1, isRed: true });
      else if (bm[2] !== undefined)
        blocks.push({ x: +bm[2], y: +bm[3], w: +bm[4], h: 1, isRed: false });
      else
        blocks.push({ x: +bm[5], y: +bm[6], w: 1, h: +bm[7], isRed: false });
    }
    levels.push({ blocks, optimal: +lm[2] });
  }
  return levels;
}

// ───────────────────────── CLI ─────────────────────────
function cmdGenerate() {
  const t0 = Date.now();
  const BANDS = [
    { name: 'Easy',   header: 'EASY 1-20',     count: 20,
      depth: [2, 4],   blk: [3, 4],  seed: 0x1A2B },
    { name: 'Medium', header: 'MEDIUM 21-50',  count: 30,
      depth: [5, 8],   blk: [4, 6],  seed: 0x3C4D },
    { name: 'Hard',   header: 'HARD 51-100',   count: 50,
      depth: [9, 14],  blk: [6, 8],  seed: 0x5E6F },
    { name: 'Expert', header: 'EXPERT 101-150', count: 50,
      depth: [15, 22], blk: [8, 11], seed: 0x7A8B },
  ];
  const bands = [];
  for (const b of BANDS) {
    process.stderr.write(`Generating ${b.name} (${b.count} levels, ` +
      `depth ${b.depth[0]}-${b.depth[1]}, ${b.blk[0]}-${b.blk[1]} blocks)…\n`);
    const r = generateBand(b.name, b.count, b.depth[0], b.depth[1],
                           b.blk[0], b.blk[1], b.seed);
    bands.push(Object.assign({ header: b.header, name: b.name,
      target: b.depth }, r));
  }

  // ── A3 VALIDATION GATE ──────────────────────────────────────────
  const all = [];
  bands.forEach(band => band.levels.forEach(l => all.push(l)));
  if (all.length !== 150) throw new Error(`expected 150, got ${all.length}`);
  let bad = 0;
  all.forEach((lvl, i) => {
    const d = solve(lvl.blocks);
    if (d < 0) { console.error(`GATE FAIL L${i + 1}: unsolvable`); bad++; }
    else if (d !== lvl.optimal) {
      console.error(`GATE FAIL L${i + 1}: optimal ${lvl.optimal} != solve ${d}`);
      bad++;
    }
    // re-assert the hard rule
    lvl.blocks.forEach(b => {
      if (!b.isRed && b.h === 1 && b.y === 2) {
        console.error(`GATE FAIL L${i + 1}: horizontal block on exit row`);
        bad++;
      }
    });
  });
  if (bad > 0) throw new Error(`A3 validation gate failed: ${bad} problem(s)`);

  // ── A4 splice ───────────────────────────────────────────────────
  spliceIntoHtml(emitLevelsBody(bands));

  // ── A5 report ───────────────────────────────────────────────────
  console.log('\n══════════ GENERATION REPORT ══════════');
  console.log(`All 150 levels regenerated, solver-validated, spliced into`);
  console.log(`game.html. Validation gate: PASS (0 unsolvable, 0 wrong`);
  console.log(`optimal, 0 horizontal-on-exit-row).\n`);
  let n = 0;
  for (const band of bands) {
    const hist = {};
    band.levels.forEach(l => { hist[l.optimal] = (hist[l.optimal] || 0) + 1; });
    const depths = band.levels.map(l => l.optimal);
    console.log(`${band.name}  (levels ${n + 1}-${n + band.levels.length})`);
    console.log(`  target depth ${band.target[0]}-${band.target[1]}` +
      (band.widened ? `  (widened to ${band.finalWindow[0]}-${band.finalWindow[1]})` : ''));
    console.log(`  actual depth ${Math.min(...depths)}-${Math.max(...depths)}` +
      `   distribution: ` +
      Object.keys(hist).sort((a, b) => a - b)
        .map(d => `${d}:${hist[d]}`).join('  '));
    console.log(`  board generations: ${band.attempts}   solver runs: ${band.solves}`);
    n += band.levels.length;
  }
  console.log(`\nTotal time: ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  console.log('═══════════════════════════════════════');
}

function cmdCheck() {
  const html = fs.readFileSync(HTML_PATH, 'utf8');
  const levels = parseLevels(html);
  let bad = 0;
  levels.forEach((lvl, i) => {
    const d = solve(lvl.blocks);
    if (d < 0) { console.log(`L${i + 1}: UNSOLVABLE`); bad++; }
    else if (d !== lvl.optimal) {
      console.log(`L${i + 1}: optimal ${lvl.optimal} != solver ${d}`); bad++;
    }
  });
  console.log(`${levels.length} levels checked, ${bad} problem(s).`);
  process.exit(bad ? 1 : 0);
}

if (require.main === module) {
  const cmd = process.argv[2];
  if (cmd === 'generate') cmdGenerate();
  else if (cmd === 'check') cmdCheck();
  else { console.error('usage: unblock_solver.js generate|check'); process.exit(2); }
}

module.exports = { solve, neighbors, isWon, generateBoard, parseLevels, GRID };
