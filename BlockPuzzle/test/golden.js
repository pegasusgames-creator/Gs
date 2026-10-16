#!/usr/bin/env node
// Golden traces of the REAL dealer: extracts the BPCORE block from game.html,
// runs it in node, and plays fixed seeds with the in-game greedy bot (plus a
// Refresh, a Bomb and a Revive per game). scripts/check_blockpuzzle_fair.py
// re-plays the same cases with its Python port and BLOCKS on any drift, and
// compares the block's sha256 so an edited dealer can't skip re-verification.
//   node BlockPuzzle/test/golden.js        (rewrites BlockPuzzle/test/golden.json)
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const HTML = path.join(__dirname, '..', 'android/app/src/main/assets/game.html');
const html = fs.readFileSync(HTML, 'utf8');
const a = html.indexOf('//@@BPCORE-BEGIN'), b = html.indexOf('//@@BPCORE-END');
if (a < 0 || b < 0) { console.error('BPCORE markers not found'); process.exit(1); }
const block = html.slice(a + '//@@BPCORE-BEGIN'.length, b);
const sha = crypto.createHash('sha256').update(block, 'utf8').digest('hex');
const api = new Function(block + '\nreturn {BP_CFG,bpNewState,bpDeal,bpApply,bpBotMove,bpReviveClear,bpBombClear,bpDailySeed};')();

function drive(mode, seed, opt) {
  const st = api.bpNewState(mode, seed, 0); st.log = [];
  api.bpDeal(st, 'tray');
  let revived = false, ref = false, bomb = false;
  while (st.moves < opt.max) {
    if (!ref && st.moves === opt.refreshAt) { ref = true; api.bpDeal(st, 'refresh'); }
    if (!bomb && st.moves === opt.bombAt) { bomb = true; api.bpBombClear(st, 3, 3); }
    const mv = api.bpBotMove(st);
    if (!mv) { if (!revived) { revived = true; api.bpReviveClear(st); api.bpDeal(st, 'revive'); continue; } break; }
    api.bpApply(st, mv.slot, mv.r, mv.c);
  }
  return { score: st.score, moves: st.moves, lines: st.lines, board: st.board.map(v => v ? 1 : 0).join(''), log: st.log };
}
const OPT = { max: 300, refreshAt: 7, bombAt: 13 };
const cases = [];
for (let i = 1; i <= 30; i++) cases.push({ mode: 'classic', seed: i * 7919, opt: OPT });
for (let d = 280; d < 300; d++) cases.push({ mode: 'daily', seed: api.bpDailySeed(d), day: d, opt: OPT });
for (const c of cases) c.out = drive(c.mode, c.seed, c.opt);
fs.writeFileSync(path.join(__dirname, 'golden.json'), JSON.stringify({ core_sha256: sha, cases }) + '\n');
console.log('golden.json: ' + cases.length + ' cases, core sha256 ' + sha.slice(0, 12));
