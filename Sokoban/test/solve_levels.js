#!/usr/bin/env node
// solve_levels.js — offline solver for the Sokoban campaign (not shipped).
//
// Reads a JSON list of ASCII maps and writes/extends a cache
// {map: {lurd, moves, pushes, optimal}} using the SAME solver block the game
// ships (solver_core.js, embedded verbatim in game.html between the
// SOKO-SOLVER-BEGIN/END markers — verify_levels.py asserts they match).
//
// Weight 1 = A* in push space with move cost and a consistent heuristic, so
// the line found is MOVE-OPTIMAL ("optimal": true). Levels whose optimum is
// out of the node budget fall back to weighted A* (1.15 → 3): a valid but
// possibly longer line ("optimal": false = best-known). Either way the line
// is replayed by verify_levels.py before it can ship, so a stored hint can
// never be wrong.
//
//   node Sokoban/test/solve_levels.js maps.json Sokoban/test/data/solutions.json
'use strict';
const fs = require('fs');
const core = require('./solver_core.js');

const [, , mapsPath, cachePath, budgetArg] = process.argv;
const maps = JSON.parse(fs.readFileSync(mapsPath, 'utf8'));
let cache = {};
try { cache = JSON.parse(fs.readFileSync(cachePath, 'utf8')); } catch (e) {}
const BUDGET = +budgetArg || 400000;
const LADDER = [[1, BUDGET], [1.15, 1500000], [1.4, 1500000], [2, 1500000], [3, 1500000]];

let solved = 0, t0 = Date.now();
maps.forEach((m, i) => {
  if (cache[m] && cache[m].lurd) return;
  const lv = core.sokoParse(m);
  for (const [w, b] of LADDER) {
    const r = core.sokoSolve(lv, lv.player, lv.boxes.slice(), { budget: b, weight: w });
    if (r.lurd) {
      cache[m] = { lurd: r.lurd, moves: r.lurd.length, pushes: (r.lurd.match(/[UDLR]/g) || []).length, optimal: w === 1 };
      solved++;
      break;
    }
  }
  if (!cache[m]) process.stderr.write(`\nUNSOLVED map #${i}\n`);
  if (i % 10 === 0) process.stderr.write(`\r${i + 1}/${maps.length}  ${((Date.now() - t0) / 1000) | 0}s   `);
  if (i % 25 === 0) fs.writeFileSync(cachePath, JSON.stringify(cache));
});
fs.writeFileSync(cachePath, JSON.stringify(cache));
process.stderr.write(`\nsolved ${solved} new, cache ${Object.keys(cache).length}\n`);
