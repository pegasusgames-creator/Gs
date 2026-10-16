#!/usr/bin/env node
// JS ↔ Python parity for the Flappy Wings course generator. Evaluates the
// SHIPPED generator (FW_TUNING + FW_GEN blocks + mulberry32, extracted from
// game.html) in a sandbox and prints the courses for the seeds given on the
// command line as JSON. scripts/check_flappywings_fair.py compares them with
// FlappyWings/test/gen_course.py gate-for-gate.
//   node FlappyWings/test/parity.js <gates> <seed> [seed ...]
const fs = require('fs'), path = require('path'), vm = require('vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'android/app/src/main/assets/game.html'), 'utf8');
const pick = (a, b) => { const m = html.match(new RegExp(a + '([\\s\\S]*?)' + b)); if (!m) throw new Error('markers ' + a); return m[1]; };
const tuning = pick('/\\*FW_TUNING_BEGIN\\*/', '/\\*FW_TUNING_END\\*/');
const gen = pick('/\\*FW_GEN_BEGIN\\*/', '/\\*FW_GEN_END\\*/');
const mul = html.match(/function mulberry32\(a\)\{[^\n]*\}/)[0];
const ctx = {};
vm.createContext(ctx);
vm.runInContext(mul + '\nconst FW=' + tuning + ';\n' + gen + '\nthis.fwCourse=fwCourse;this.fwGate=fwGate;this.fwDailySeed=fwDailySeed;', ctx);
const n = parseInt(process.argv[2], 10) || 50;
const out = {};
for (const sArg of process.argv.slice(3)) {
  let seed;
  if (sArg.startsWith('day:')) seed = ctx.fwDailySeed(parseInt(sArg.slice(4), 10));
  else seed = Number(sArg) >>> 0;
  const C = ctx.fwCourse(seed); ctx.fwGate(C, n - 1);
  out[sArg] = { seed, gates: C.gates.map(g => [g.x, g.c, g.gap, g.amp, g.phase, g.feather ? [g.feather.x, g.feather.y] : null]) };
}
process.stdout.write(JSON.stringify(out));
