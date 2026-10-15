#!/usr/bin/env node
// gen_campaign.js — Sokoban level miner for chapters 3-10 (levels 101-500).
//
// Every level is built SOLVABLE BY CONSTRUCTION, then picked for depth:
//   1. room: a w×h interior is carved with random wall pieces (dominoes,
//      L-trominoes, bars, single blocks) under quality constraints — floor
//      stays connected, few dead-end pockets, few wide-open 3×3 areas (open
//      rooms make Sokoban trivial);
//   2. goals: n goal cells, loosely clustered (classic storage-room feel);
//   3. reverse search: BFS from the SOLVED state (every box on a goal, the
//      keeper in any free region) over box PULLS — the exact inverse of a
//      push — so every reached state is a start position with a known
//      push-optimal solution length (its BFS depth);
//   4. pick the deepest reachable state (ties broken by how often the
//      optimal line switches boxes — the "interesting" measure from Taylor &
//      Parberry 2011), reject rooms whose deepest state misses the band.
// Output: JSON [{map, band, pushes, switches}] on stdout. Deterministic.
// Move-optimal LURD solutions are computed afterwards by solve_levels.py,
// and scripts/check_sokoban_solvable.py re-proves every level with A*.
//
//   node Sokoban/test/gen_campaign.js > Sokoban/test/data/mined.json
//   node Sokoban/test/gen_campaign.js daily > Sokoban/test/data/daily.json
'use strict';

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// Chapters 3..10, 50 levels each. w/h = interior size range, boxes, the
// accepted push-optimal depth band, max open 3x3 windows, wall fraction.
const BANDS = [
  { n: 50, w: [6, 7], h: [6, 7], boxes: [2, 3], push: [9, 15],  open: 3, wall: [0.16, 0.24] },
  { n: 50, w: [6, 7], h: [6, 8], boxes: [3, 3], push: [12, 19], open: 2, wall: [0.18, 0.26] },
  { n: 50, w: [7, 8], h: [6, 8], boxes: [3, 3], push: [15, 23], open: 2, wall: [0.18, 0.27] },
  { n: 50, w: [7, 8], h: [7, 8], boxes: [3, 4], push: [18, 27], open: 1, wall: [0.20, 0.28] },
  { n: 50, w: [7, 8], h: [7, 9], boxes: [4, 4], push: [21, 31], open: 1, wall: [0.20, 0.28] },
  { n: 50, w: [8, 9], h: [7, 9], boxes: [4, 4], push: [24, 36], open: 1, wall: [0.20, 0.30] },
  { n: 50, w: [8, 9], h: [8, 9], boxes: [4, 5], push: [27, 42], open: 0, wall: [0.22, 0.30] },
  { n: 50, w: [8, 9], h: [8, 9], boxes: [5, 5], push: [30, 60], open: 0, wall: [0.22, 0.30] },
];
const STATE_CAP = 400000;

const PIECES = [
  [[0, 0]],
  [[0, 0], [1, 0]], [[0, 0], [0, 1]],
  [[0, 0], [1, 0], [0, 1]], [[0, 0], [1, 0], [1, 1]], [[0, 0], [0, 1], [1, 1]], [[1, 0], [0, 1], [1, 1]],
  [[0, 0], [1, 0], [2, 0]], [[0, 0], [0, 1], [0, 2]],
];

function makeRoom(rnd, band) {
  const w = band.w[0] + Math.floor(rnd() * (band.w[1] - band.w[0] + 1));
  const h = band.h[0] + Math.floor(rnd() * (band.h[1] - band.h[0] + 1));
  const W = w + 2, H = h + 2;
  const wall = new Uint8Array(W * H);
  for (let x = 0; x < W; x++) { wall[x] = 1; wall[(H - 1) * W + x] = 1; }
  for (let y = 0; y < H; y++) { wall[y * W] = 1; wall[y * W + W - 1] = 1; }
  const frac = band.wall[0] + rnd() * (band.wall[1] - band.wall[0]);
  const target = Math.round(w * h * frac);
  let placed = 0, tries = 0;
  while (placed < target && tries < 400) {
    tries++;
    const p = PIECES[Math.floor(rnd() * PIECES.length)];
    const ox = 1 + Math.floor(rnd() * w), oy = 1 + Math.floor(rnd() * h);
    const cells = [];
    let okp = true;
    for (const [dx, dy] of p) {
      const x = ox + dx, y = oy + dy;
      if (x < 1 || y < 1 || x > w || y > h) { okp = false; break; }
      const i = y * W + x; if (wall[i]) { okp = false; break; }
      cells.push(i);
    }
    if (!okp) continue;
    for (const i of cells) wall[i] = 1;
    if (!roomOk(wall, W, H, band, false)) { for (const i of cells) wall[i] = 0; continue; }
    placed += cells.length;
  }
  if (!roomOk(wall, W, H, band, true)) return null;
  return { W, H, wall };
}

function floorCells(wall, W, H) {
  const out = [];
  for (let i = 0; i < W * H; i++) if (!wall[i]) out.push(i);
  return out;
}

function roomOk(wall, W, H, band, final) {
  const fl = floorCells(wall, W, H);
  if (fl.length < 8) return false;
  // connected
  const seen = new Uint8Array(W * H); const st = [fl[0]]; seen[fl[0]] = 1; let n = 1;
  while (st.length) {
    const c = st.pop();
    for (const d of [1, -1, W, -W]) { const m = c + d; if (!wall[m] && !seen[m]) { seen[m] = 1; n++; st.push(m); } }
  }
  if (n !== fl.length) return false;
  // dead-end pockets (floor with 3 wall neighbours)
  let dead = 0;
  for (const c of fl) { let k = 0; for (const d of [1, -1, W, -W]) if (wall[c + d]) k++; if (k >= 3) dead++; if (k === 4) return false; }
  if (dead > 2) return false;
  if (final) {
    let open = 0;
    for (let y = 1; y + 2 < H - 1 + 1; y++) for (let x = 1; x + 2 < W - 1 + 1; x++) {
      let all = true;
      for (let dy = 0; dy < 3 && all; dy++) for (let dx = 0; dx < 3; dx++) if (wall[(y + dy) * W + x + dx]) { all = false; break; }
      if (all) open++;
    }
    if (open > band.open) return false;
  }
  return true;
}

// ── reverse BFS over pulls ─────────────────────────────────────────────
function reverseSearch(room, goals) {
  const { W, H, wall } = room;
  const N = W * H;
  const DIRS = [1, -1, W, -W];
  const mark = new Int32Array(N); let stamp = 0;
  const isBox = new Uint8Array(N);
  function setBoxes(bs, v) { for (const b of bs) isBox[b] = v; }
  function flood(p) {         // returns min index of the region, marks with stamp
    stamp++; let mn = p; const st = [p]; mark[p] = stamp;
    while (st.length) {
      const c = st.pop(); if (c < mn) mn = c;
      for (const d of DIRS) { const m = c + d; if (!wall[m] && !isBox[m] && mark[m] !== stamp) { mark[m] = stamp; st.push(m); } }
    }
    return mn;
  }
  const keyOf = (bs, p) => bs.join(',') + '|' + p;
  const info = new Map();          // key -> [depth, parentKey, movedBox(new pos)]
  let frontier = [];
  const gs = goals.slice().sort((a, b) => a - b);
  setBoxes(gs, 1);
  const regDone = new Set();
  for (let c = 0; c < N; c++) {
    if (wall[c] || isBox[c]) continue;
    const mn = flood(c);
    if (regDone.has(mn)) continue; regDone.add(mn);
    const k = keyOf(gs, mn); info.set(k, [0, null, -1]); frontier.push([gs, mn]);
  }
  setBoxes(gs, 0);
  let depth = 0, last = frontier;
  while (frontier.length && info.size < STATE_CAP) {
    const next = [];
    for (const [bs, p] of frontier) {
      const pk = keyOf(bs, p);
      setBoxes(bs, 1);
      flood(p); const reachStamp = stamp;
      const reach = mark.slice(); // snapshot (stamp comparison)
      for (let bi = 0; bi < bs.length; bi++) {
        const b = bs[bi];
        for (const d of DIRS) {
          const pc = b + d, back = b + 2 * d;
          if (reach[pc] !== reachStamp) continue;
          if (wall[back] || isBox[back]) continue;
          // pull: box b -> pc, keeper -> back
          isBox[b] = 0; isBox[pc] = 1;
          const nmn = flood(back);
          isBox[pc] = 0; isBox[b] = 1;
          const nbs = bs.slice(); nbs[bi] = pc; nbs.sort((a, c) => a - c);
          const k = keyOf(nbs, nmn);
          if (info.has(k)) continue;
          info.set(k, [depth + 1, pk, pc]);
          next.push([nbs, nmn]);
        }
      }
      setBoxes(bs, 0);
      if (info.size >= STATE_CAP) break;
    }
    if (!next.length) break;
    depth++; last = next; frontier = next;
  }
  return { depth, last, info, keyOf };
}

function switches(info, key) {
  // Walk the parent chain = the push-optimal line in FORWARD order. At state
  // k the keeper pushes the box sitting at info[k][2] back to the one cell
  // the parent has that k lacks; a "switch" = the next push moves a
  // different box than the one just pushed.
  const boxesOf = k => k.split('|')[0].split(',').map(Number);
  let n = 0, k = key, guard = 0;
  while (guard++ < 1000) {
    const cur = info.get(k); const parent = cur[1];
    if (parent == null) break;
    const pInfo = info.get(parent);
    if (pInfo[1] == null) break;              // parent = solved state
    const cb = boxesOf(k), pb = boxesOf(parent);
    const landed = pb.filter(x => cb.indexOf(x) < 0)[0];
    if (pInfo[2] !== landed) n++;
    k = parent;
  }
  return n;
}

function toAscii(room, boxes, goals, player) {
  const { W, H, wall } = room;
  // trim to the floor bounding box + 1 wall ring; walls not touching floor
  // (8-neighbourhood) become void so the outline follows the room shape.
  let x0 = W, y0 = H, x1 = 0, y1 = 0;
  for (let i = 0; i < W * H; i++) if (!wall[i]) { const x = i % W, y = (i / W) | 0; x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  x0--; y0--; x1++; y1++;
  const bset = new Set(boxes), gset = new Set(goals);
  const rows = [];
  for (let y = y0; y <= y1; y++) {
    let r = '';
    for (let x = x0; x <= x1; x++) {
      const i = y * W + x;
      if (wall[i]) {
        let touch = false;
        for (let dy = -1; dy <= 1 && !touch; dy++) for (let dx = -1; dx <= 1; dx++) {
          const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue;
          if (!wall[yy * W + xx]) { touch = true; break; }
        }
        r += touch ? '#' : ' ';
      } else if (bset.has(i)) r += gset.has(i) ? '*' : '$';
      else if (i === player) r += gset.has(i) ? '+' : '@';
      else r += gset.has(i) ? '.' : ' ';
    }
    rows.push(r.replace(/\s+$/, ''));
  }
  return rows.join('\n');
}

function pickGoals(rnd, room, nb) {
  const { W, H, wall } = room;
  const fl = floorCells(wall, W, H).filter(c => {
    // a box on c must be pullable out in some direction
    for (const d of [1, -1, W, -W]) if (!wall[c + d] && !wall[c + 2 * d]) return true;
    return false;
  });
  if (fl.length < nb + 4) return null;
  const goals = [];
  while (goals.length < nb) {
    let c;
    if (goals.length && rnd() < 0.55) {
      const near = fl.filter(x => goals.indexOf(x) < 0 && goals.some(g => Math.abs(g % W - x % W) + Math.abs(((g / W) | 0) - ((x / W) | 0)) <= 2));
      c = near.length ? near[Math.floor(rnd() * near.length)] : fl[Math.floor(rnd() * fl.length)];
    } else c = fl[Math.floor(rnd() * fl.length)];
    if (goals.indexOf(c) < 0) goals.push(c);
  }
  return goals;
}

function genLevel(rnd, band) {
  for (let attempt = 0; attempt < 60; attempt++) {
    const room = makeRoom(rnd, band);
    if (!room) continue;
    const nb = band.boxes[0] + Math.floor(rnd() * (band.boxes[1] - band.boxes[0] + 1));
    const goals = pickGoals(rnd, room, nb);
    if (!goals) continue;
    const R = reverseSearch(room, goals);
    if (R.depth < band.push[0]) continue;
    // candidates: the deepest layer, capped into the band
    let layer = R.depth;
    if (layer > band.push[1]) layer = band.push[1];
    const cands = [];
    for (const [k, v] of R.info) if (v[0] === layer) cands.push(k);
    if (!cands.length) continue;
    // score a sample by box switches; take the best
    let best = null, bestS = -1;
    const sample = cands.length > 40 ? Array.from({ length: 40 }, () => cands[Math.floor(rnd() * cands.length)]) : cands;
    for (const k of sample) {
      const s = switches(R.info, k);
      if (s > bestS) { bestS = s; best = k; }
    }
    if (bestS < Math.min(2, nb - 1)) continue;   // one box shoved all the way = dull
    const [bpart, ppart] = best.split('|');
    const boxes = bpart.split(',').map(Number);
    // no box may START on its goal set in a way that leaves nothing to do
    const onGoal = boxes.filter(b => goals.indexOf(b) >= 0).length;
    if (onGoal >= nb - 1 && nb > 1) continue;
    // keeper: a cell of the start region, farthest-ish from the boxes
    const { W, H, wall } = room;
    const isB = new Set(boxes);
    const reg = []; const seen = new Set([+ppart]); const st = [+ppart];
    while (st.length) { const c = st.pop(); reg.push(c); for (const d of [1, -1, W, -W]) { const m = c + d; if (!wall[m] && !isB.has(m) && !seen.has(m)) { seen.add(m); st.push(m); } } }
    const player = reg[Math.floor(rnd() * reg.length)];
    return { map: toAscii(room, boxes, goals, player), pushes: layer, switches: bestS, boxes: nb };
  }
  return null;
}

// Daily pool (mode "daily"): three weekday tiers mined with a different seed,
// so the daily board is never a campaign level. The game picks
// DAILY[tier][day % n] and applies one of the 8 board symmetries.
const DAILY_BANDS = [
  { n: 60, w: [6, 7], h: [6, 7], boxes: [2, 3], push: [10, 16], open: 3, wall: [0.16, 0.24] },   // Mon/Tue
  { n: 60, w: [7, 8], h: [7, 8], boxes: [3, 4], push: [16, 25], open: 1, wall: [0.20, 0.28] },   // Wed-Fri
  { n: 60, w: [8, 9], h: [7, 9], boxes: [4, 4], push: [22, 34], open: 1, wall: [0.20, 0.30] },   // Sat/Sun
];

function main() {
  const daily = process.argv[2] === 'daily';
  const bands = daily ? DAILY_BANDS : BANDS;
  const rnd = mulberry32(daily ? 20261015 : 20261012);
  const out = [];
  const seenMaps = new Set();
  bands.forEach((band, bi) => {
    let made = 0, fails = 0;
    while (made < band.n) {
      const L = genLevel(rnd, band);
      if (!L) { fails++; if (fails > 400) throw new Error('band ' + bi + ' starved'); continue; }
      if (seenMaps.has(L.map)) continue;
      seenMaps.add(L.map);
      L.band = bi; out.push(L); made++;
      process.stderr.write(`\rband ${bi} ${made}/${band.n}   `);
    }
    process.stderr.write('\n');
  });
  process.stdout.write(JSON.stringify(out));
}
if (require.main === module) main();
module.exports = { mulberry32, BANDS, DAILY_BANDS, genLevel, reverseSearch, makeRoom, switches, toAscii, pickGoals, roomOk };
