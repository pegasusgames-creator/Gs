/*SOKO-SOLVER-BEGIN*/
// ── Sokoban core: level parsing + solver. This block is shared verbatim
// between game.html (hint fallback) and Sokoban/test/solve_levels.js (the
// offline move-optimal SOLUTIONS miner reads it OUT of game.html, so the
// shipped solver and the one that produced the stored lines never drift).
//
// Level grid: cols×rows cells, index i = y*cols + x. A cell is FLOOR only if
// the keeper can reach it ignoring crates; everything else (walls and the
// void outside the room) counts as a wall for movement.
function sokoParse(ascii) {
  const lines = ascii.split('\n');
  const rows = lines.length;
  let cols = 0; for (const l of lines) cols = Math.max(cols, l.length);
  const N = cols * rows;
  const wallCh = new Uint8Array(N), goal = new Uint8Array(N), boxes = [];
  let player = -1;
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
    const ch = lines[y][x] || ' ', i = y * cols + x;
    if (ch === '#') wallCh[i] = 1;
    else if (ch === '$') boxes.push(i);
    else if (ch === '*') { boxes.push(i); goal[i] = 1; }
    else if (ch === '.') goal[i] = 1;
    else if (ch === '@') player = i;
    else if (ch === '+') { player = i; goal[i] = 1; }
  }
  // interior = flood from the keeper through non-wall cells
  const floor = new Uint8Array(N);
  if (player >= 0) {
    const st = [player]; floor[player] = 1;
    while (st.length) {
      const c = st.pop(), x = c % cols, y = (c / cols) | 0;
      const nb = [x > 0 ? c - 1 : -1, x < cols - 1 ? c + 1 : -1, y > 0 ? c - cols : -1, y < rows - 1 ? c + cols : -1];
      for (const n of nb) if (n >= 0 && !wallCh[n] && !floor[n]) { floor[n] = 1; st.push(n); }
    }
  }
  const wall = new Uint8Array(N);
  for (let i = 0; i < N; i++) wall[i] = floor[i] ? 0 : 1;
  const lv = { cols, rows, N, wall, wallCh, floor, goal, boxes, player };
  sokoPrep(lv);
  return lv;
}
// Directions: index 0..3 = u,d,l,r (LURD letters).
const SOKO_DL = ['u', 'd', 'l', 'r'];
function sokoDelta(lv, k) { return k === 0 ? -lv.cols : k === 1 ? lv.cols : k === 2 ? -1 : 1; }
// Push distance (wall-only) from each cell to the nearest goal, by reverse
// pulls. -1 = dead square: a crate there can never reach any goal.
function sokoPrep(lv) {
  const N = lv.N, goals = [];
  for (let i = 0; i < N; i++) if (lv.goal[i] && !lv.wall[i]) goals.push(i);
  const pdg = goals.map(g0 => {
    const pd = new Int16Array(N).fill(-1), q = [g0]; pd[g0] = 0;
    for (let h = 0; h < q.length; h++) {
      const c = q[h];
      for (let k = 0; k < 4; k++) {
        const d = sokoDelta(lv, k), n = c + d, p = c + 2 * d;
        if (n < 0 || p < 0 || n >= N || p >= N) continue;
        if (lv.wall[n] || lv.wall[p] || pd[n] >= 0) continue;
        pd[n] = pd[c] + 1; q.push(n);
      }
    }
    return pd;
  });
  const pd = new Int16Array(N).fill(-1);
  for (const t of pdg) for (let i = 0; i < N; i++) if (t[i] >= 0 && (pd[i] < 0 || t[i] < pd[i])) pd[i] = t[i];
  lv.goals = goals; lv.pdg = pdg; lv.pd = pd;
}
// Lower bound on pushes: min-cost assignment of crates to distinct goals
// (bitmask DP, ≤ 8 crates). Infinity = no assignment exists (deadlock).
// One push moves one crate one step in the push graph, changing any of its
// goal distances by ≤ 1, so this bound is consistent for A*.
function sokoMatch(lv, bs) {
  const n = bs.length, G = lv.pdg, full = 1 << G.length;
  let dp = new Map([[0, 0]]);
  for (let i = 0; i < n; i++) {
    const nx = new Map(), b = bs[i];
    for (const [mask, v] of dp) {
      for (let j = 0; j < G.length; j++) {
        if (mask & (1 << j)) continue;
        const d = G[j][b]; if (d < 0) continue;
        const m2 = mask | (1 << j), nv = v + d, o = nx.get(m2);
        if (o === undefined || nv < o) nx.set(m2, nv);
      }
    }
    dp = nx; if (!dp.size) return Infinity;
  }
  let best = Infinity; for (const v of dp.values()) if (v < best) best = v;
  return best;
}
// 2×2 freeze: `cell` sits in a 2×2 block of walls/crates holding a crate that
// is not on a goal → every crate in that block is stuck forever.
function sokoFrozen(lv, isBox, cell) {
  const c = lv.cols;
  for (const o of [0, -1, -c, -c - 1]) {
    const a = cell + o, q = [a, a + 1, a + c, a + c + 1];
    let all = true, off = false;
    for (const x of q) {
      if (x < 0 || x >= lv.N) { all = false; break; }
      if (lv.wall[x]) continue;
      if (isBox[x]) { if (!lv.goal[x]) off = true; continue; }
      all = false; break;
    }
    if (all && off) return true;
  }
  return false;
}
// Keeper BFS over free cells. Returns Int16Array of distances (-1 = no).
function sokoReach(lv, isBox, from) {
  const d = new Int16Array(lv.N).fill(-1), q = [from]; d[from] = 0;
  for (let h = 0; h < q.length; h++) {
    const c = q[h];
    for (let k = 0; k < 4; k++) {
      const n = c + sokoDelta(lv, k);
      if (n < 0 || n >= lv.N || lv.wall[n] || isBox[n] || d[n] >= 0) continue;
      d[n] = d[c] + 1; q.push(n);
    }
  }
  return d;
}
// Shortest walk a→b avoiding crates, as lower-case LURD ('' if a===b, null).
function sokoWalk(lv, isBox, a, b) {
  if (a === b) return '';
  const prev = new Int32Array(lv.N).fill(-1), pk = new Int8Array(lv.N), q = [a]; prev[a] = a;
  for (let h = 0; h < q.length; h++) {
    const c = q[h]; if (c === b) break;
    for (let k = 0; k < 4; k++) {
      const n = c + sokoDelta(lv, k);
      if (n < 0 || n >= lv.N || lv.wall[n] || isBox[n] || prev[n] >= 0) continue;
      prev[n] = c; pk[n] = k; q.push(n);
    }
  }
  if (prev[b] < 0) return null;
  let s = '', c = b;
  while (c !== a) { s = SOKO_DL[pk[c]] + s; c = prev[c]; }
  return s;
}
// A* in push space with MOVE cost (walk to the push cell + 1). With
// weight 1 the heuristic (sum of push distances) is consistent, so the first
// solved node popped is move-optimal; weight > 1 trades optimality for speed
// (in-game hint fallback). Returns {lurd, expanded} or {lurd:null, ...}.
function sokoSolve(lv, player, boxes, opt) {
  opt = opt || {};
  const budget = opt.budget || 200000, W = opt.weight || 1;
  const N = lv.N, pd = lv.pd, goalCount = boxes.length;
  for (const b of boxes) if (pd[b] < 0) return { lurd: null, dead: true, expanded: 0 };
  const isBox = new Uint8Array(N);
  const nodesB = [], nodesP = [], nodesPar = [], nodesSrc = [], nodesK = [], nodesG = [];
  const seen = new Map();
  const heap = [];
  function hpush(f, id) {
    heap.push([f, id]); let i = heap.length - 1;
    while (i > 0) { const p = (i - 1) >> 1; if (heap[p][0] <= heap[i][0]) break; const t = heap[p]; heap[p] = heap[i]; heap[i] = t; i = p; }
  }
  function hpop() {
    const top = heap[0], last = heap.pop();
    if (heap.length) {
      heap[0] = last; let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1; let m = i;
        if (l < heap.length && heap[l][0] < heap[m][0]) m = l;
        if (r < heap.length && heap[r][0] < heap[m][0]) m = r;
        if (m === i) break; const t = heap[m]; heap[m] = heap[i]; heap[i] = t; i = m;
      }
    }
    return top;
  }
  const hOf = bs => sokoMatch(lv, bs);
  const b0 = boxes.slice().sort((a, b) => a - b);
  nodesB.push(b0); nodesP.push(player); nodesPar.push(-1); nodesSrc.push(-1); nodesK.push(-1); nodesG.push(0);
  seen.set(b0.join(',') + '|' + player, 0);
  const h0 = hOf(b0); if (h0 === Infinity) return { lurd: null, dead: true, expanded: 0 };
  hpush(W * h0, 0);
  let expanded = 0, goalId = -1;
  while (heap.length) {
    const [, id] = hpop();
    const bs = nodesB[id], g = nodesG[id], pl = nodesP[id];
    const key = bs.join(',') + '|' + pl;
    if (seen.get(key) !== id) continue;           // stale entry
    let solved = true; for (const b of bs) if (!lv.goal[b]) { solved = false; break; }
    if (solved) { goalId = id; break; }
    if (++expanded > budget) break;
    for (const b of bs) isBox[b] = 1;
    const reach = sokoReach(lv, isBox, pl);
    for (let bi = 0; bi < bs.length; bi++) {
      const b = bs[bi];
      for (let k = 0; k < 4; k++) {
        const d = sokoDelta(lv, k), src = b - d, dst = b + d;
        if (src < 0 || src >= N || dst < 0 || dst >= N) continue;
        if (reach[src] < 0 || lv.wall[dst] || isBox[dst] || pd[dst] < 0) continue;
        isBox[b] = 0; isBox[dst] = 1;
        const frozen = sokoFrozen(lv, isBox, dst);
        isBox[dst] = 0; isBox[b] = 1;
        if (frozen) continue;
        const nb = bs.slice(); nb[bi] = dst; nb.sort((a, c) => a - c);
        const hv = hOf(nb); if (hv === Infinity) continue;
        const ng = g + reach[src] + 1, nk = nb.join(',') + '|' + b;
        const old = seen.get(nk);
        if (old !== undefined && nodesG[old] <= ng) continue;
        const nid = nodesB.length;
        nodesB.push(nb); nodesP.push(b); nodesPar.push(id); nodesSrc.push(src); nodesK.push(k); nodesG.push(ng);
        seen.set(nk, nid);
        hpush(ng + W * hv, nid);
      }
    }
    for (const b of bs) isBox[b] = 0;
  }
  if (goalId < 0) return { lurd: null, expanded, exhausted: !heap.length };
  const chain = [];
  for (let id = goalId; nodesPar[id] >= 0; id = nodesPar[id]) chain.push(id);
  chain.reverse();
  let out = '';
  for (const id of chain) {
    const par = nodesPar[id];
    for (const b of nodesB[par]) isBox[b] = 1;
    out += sokoWalk(lv, isBox, nodesP[par], nodesSrc[id]) + SOKO_DL[nodesK[id]].toUpperCase();
    for (const b of nodesB[par]) isBox[b] = 0;
  }
  return { lurd: out, expanded, moves: nodesG[goalId] };
}
// Run-length LURD codec ('3rU2l' <-> 'rrrUll').
function sokoUnRLE(s) { return s.replace(/(\d+)([udlrUDLR])/g, (m, n, c) => c.repeat(+n)); }
function sokoRLE(s) { return s.replace(/([udlrUDLR])\1+/g, m => m.length + m[0]); }
/*SOKO-SOLVER-END*/
if (typeof module !== 'undefined') module.exports = { sokoMatch, sokoParse, sokoSolve, sokoRLE, sokoUnRLE, sokoFrozen, sokoReach, sokoWalk, sokoDelta };
