#!/usr/bin/env node
// verify_nonogram_pregen.js — load Nonogram/.../game.html, extract
// PREGEN_15 and PREGEN_20 string arrays, run the uniqueness counter from
// _nonogram_solver.js, and (when --fix is passed) regenerate every
// non-unique board offline and rewrite the arrays in place.
//
// Usage:
//   node scripts/verify_nonogram_pregen.js          # report only
//   node scripts/verify_nonogram_pregen.js --fix    # rewrite game.html
//   node scripts/verify_nonogram_pregen.js --pregen10 [N]
//     # generate N (default 80) unique 10x10 solutions and write them as
//     # a fresh PREGEN_10 array next to PREGEN_15. Pairs with the
//     # buildLevels switch (A2) so 10x10 levels are all pre-verified.

'use strict';
const fs = require('fs');
const path = require('path');
const { computeClues, countSolutions, decodePregen, encodeSolution } =
  require('./_nonogram_solver.js');

const REPO = path.resolve(__dirname, '..');
const GAME = path.join(REPO, 'Nonogram/android/app/src/main/assets/game.html');
const FIX = process.argv.includes('--fix');

function extractArray(src, name){
  const m = src.match(new RegExp('const ' + name + ' = \\[([\\s\\S]*?)\\];'));
  if(!m) throw new Error('Could not find ' + name);
  const body = m[1];
  const strings = [];
  const re = /"([01]+)"/g;
  let mm;
  while((mm = re.exec(body)) !== null) strings.push(mm[1]);
  return { strings, raw: m[0] };
}

function rebuildArray(name, strings){
  const lines = strings.map(s => '  "' + s + '"').join(',\n');
  return 'const ' + name + ' = [\n' + lines + '\n];';
}

// Random binary solution generator for regen. We seed via Math.random()
// because this runs offline. Density: 40-60% filled to keep clues meaty.
function mulberry32(seed){
  return function(){
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function genRandomBoard(size, seed){
  const rng = mulberry32(seed);
  const cells = new Array(size*size);
  const fillProb = 0.45 + rng()*0.10;
  for(let i=0;i<cells.length;i++) cells[i] = rng() < fillProb ? 1 : 0;
  // avoid empty rows/cols which give degenerate boards
  let any0=false, any1=false;
  for(const v of cells){ if(v) any1=true; else any0=true; if(any0 && any1) break; }
  if(!any1) cells[Math.floor(cells.length/2)] = 1;
  if(!any0) cells[0] = 0;
  return cells;
}

function tryRegenUnique(size, attempts){
  attempts = attempts || 600;
  // Slightly time-capped per board: 15x15 fast (~ms), 20x20 can be slow.
  const cap = (size === 20) ? 200 : 600;
  let baseSeed = Date.now();
  for(let t=0; t<cap; t++){
    const sol = genRandomBoard(size, baseSeed + t*7919);
    const { rowClues, colClues } = computeClues(sol, size);
    // Quick reject: any row or column with empty clue can never deduce; skip.
    if (rowClues.some(c => c.length===1 && c[0]===0)) continue;
    if (colClues.some(c => c.length===1 && c[0]===0)) continue;
    const { count } = countSolutions(rowClues, colClues, size, 2);
    if(count === 1) return sol;
  }
  return null;
}

function pregen10Mode(){
  const argIdx = process.argv.indexOf('--pregen10');
  const wanted = parseInt(process.argv[argIdx+1] || '80', 10) || 80;
  const seen = new Set();
  const out = [];
  let seed = 17;
  let tries = 0;
  while(out.length < wanted && tries < 20000){
    tries++;
    seed += 7919;
    const sol = genRandomBoard(10, seed);
    const { rowClues, colClues } = computeClues(sol, 10);
    if (rowClues.some(c => c.length===1 && c[0]===0)) continue;
    if (colClues.some(c => c.length===1 && c[0]===0)) continue;
    const { count } = countSolutions(rowClues, colClues, 10, 2);
    if(count !== 1) continue;
    const enc = encodeSolution(sol);
    if(seen.has(enc)) continue;
    seen.add(enc);
    out.push(enc);
    if(out.length % 10 === 0) process.stderr.write(`  ...${out.length}/${wanted}\n`);
  }
  if(out.length < wanted){
    process.stderr.write(`  ! only generated ${out.length}/${wanted} unique boards in ${tries} tries\n`);
    process.exit(2);
  }
  // Splice the new PREGEN_10 array into game.html just BEFORE PREGEN_15.
  const src = fs.readFileSync(GAME, 'utf8');
  const arrStr = rebuildArray('PREGEN_10', out);
  const marker = 'const PREGEN_15 = [';
  if(src.indexOf(marker) < 0){ process.stderr.write('  ! no PREGEN_15 anchor\n'); process.exit(2); }
  let newSrc;
  if(src.indexOf('const PREGEN_10 = [') >= 0){
    const m = src.match(/const PREGEN_10 = \[[\s\S]*?\];/);
    newSrc = src.replace(m[0], arrStr);
  } else {
    newSrc = src.replace(marker, arrStr + '\n\n' + marker);
  }
  fs.writeFileSync(GAME, newSrc, 'utf8');
  process.stderr.write(`  Wrote PREGEN_10 with ${out.length} entries\n`);
  console.log(JSON.stringify({ pregen10: out.length, ok: true }));
  process.exit(0);
}

function main(){
  if(process.argv.includes('--pregen10')) return pregen10Mode();
  const src = fs.readFileSync(GAME, 'utf8');
  const SIZES = [
    { name: 'PREGEN_15', size: 15 },
    { name: 'PREGEN_20', size: 20 },
  ];
  // Re-include PREGEN_10 in the verification if it exists.
  if(src.indexOf('const PREGEN_10 = [') >= 0){
    SIZES.unshift({ name: 'PREGEN_10', size: 10 });
  }
  let dirty = false;
  let totalBad = 0;
  const replacements = [];
  for(const { name, size } of SIZES){
    process.stderr.write(`Checking ${name} (size ${size}x${size})...\n`);
    const { strings, raw } = extractArray(src, name);
    const newStrings = strings.slice();
    let bad = 0;
    for(let i=0; i<strings.length; i++){
      const sol = decodePregen(strings[i]);
      if(sol.length !== size*size){
        process.stderr.write(`  ! ${name}[${i}] length ${sol.length} != ${size*size}\n`);
        bad++;
        continue;
      }
      const { rowClues, colClues } = computeClues(sol, size);
      const { count } = countSolutions(rowClues, colClues, size, 2);
      if(count !== 1){
        bad++;
        process.stderr.write(`  ${count===0?'CONTRADICTION':'NON-UNIQUE'} ${name}[${i}]\n`);
        if(FIX){
          const fixed = tryRegenUnique(size, 600);
          if(fixed){
            newStrings[i] = encodeSolution(fixed);
            process.stderr.write(`    → regenerated\n`);
          } else {
            process.stderr.write(`    → FAILED to regen within attempts\n`);
          }
        }
      }
      if(i % 25 === 24) process.stderr.write(`  ...${i+1}/${strings.length}\n`);
    }
    process.stderr.write(`  ${name}: ${bad}/${strings.length} non-unique\n`);
    totalBad += bad;
    if(FIX && bad > 0){
      replacements.push({ raw, replacement: rebuildArray(name, newStrings) });
      dirty = true;
    }
  }
  if(FIX && dirty){
    let newSrc = src;
    for(const r of replacements){
      if(newSrc.indexOf(r.raw) < 0){
        process.stderr.write('  ! could not locate original array — bailing\n');
        process.exit(2);
      }
      newSrc = newSrc.replace(r.raw, r.replacement);
    }
    fs.writeFileSync(GAME, newSrc, 'utf8');
    process.stderr.write('  Wrote updated game.html\n');
  }
  console.log(JSON.stringify({ totalBad, fixed: FIX, ok: totalBad===0 }));
  process.exit(totalBad===0 ? 0 : (FIX ? 0 : 1));
}

main();
