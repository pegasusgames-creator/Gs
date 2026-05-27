// Shared Nonogram solver primitives used by:
//   - scripts/verify_nonogram_pregen.js  (offline PREGEN re-verification)
//   - scripts/check_nonogram_unique.py    (pre-publish gate, via spawning node)
// Algorithm:
//   1. Generate all valid line-placements per row + per column.
//   2. Iteratively prune cells where every remaining row/col placement
//      agrees on cell state.
//   3. After propagation, count up to TWO complete solutions via DFS
//      branching on the first undetermined cell.
//   4. Return { unique, count, solutions } where count ∈ {0,1,2+}.
'use strict';

function lineRuns(line){
  const r=[]; let run=0;
  for(let i=0;i<line.length;i++){
    if(line[i]===1){ run++; } else if(run>0){ r.push(run); run=0; }
  }
  if(run>0) r.push(run);
  return r.length?r:[0];
}
function computeClues(solution, size){
  const rowClues=[], colClues=[];
  for(let r=0;r<size;r++){
    const row=[];
    for(let c=0;c<size;c++) row.push(solution[r*size+c]);
    rowClues.push(lineRuns(row));
  }
  for(let c=0;c<size;c++){
    const col=[];
    for(let r=0;r<size;r++) col.push(solution[r*size+c]);
    colClues.push(lineRuns(col));
  }
  return { rowClues, colClues };
}

// Enumerate every valid binary placement of `clues` into a line of length n.
function enumPlacements(n, clues){
  if(clues.length===1 && clues[0]===0){
    return [new Array(n).fill(0)];
  }
  const out=[];
  function rec(idx, pos, line){
    if(idx===clues.length){
      const filled = line.slice();
      while(filled.length<n) filled.push(0);
      out.push(filled);
      return;
    }
    const remaining = clues.slice(idx+1).reduce((a,b)=>a+b+1,0);
    const maxStart = n - clues[idx] - remaining;
    for(let p=pos; p<=maxStart; p++){
      const next = line.slice();
      while(next.length<p) next.push(0);
      for(let k=0;k<clues[idx];k++) next.push(1);
      if(idx<clues.length-1) next.push(0); // mandatory separator
      rec(idx+1, next.length, next);
    }
  }
  rec(0,0,[]);
  return out;
}

// Filter placements compatible with current known cells (-1 unknown, 0 empty, 1 filled).
function filterPlacements(placements, known){
  const out=[];
  for(const p of placements){
    let ok=true;
    for(let i=0;i<p.length;i++){
      if(known[i]!==-1 && known[i]!==p[i]){ ok=false; break; }
    }
    if(ok) out.push(p);
  }
  return out;
}

// Pure-deduction prune. Mutates grid in place. Returns true if any contradiction.
function prune(grid, size, rowPlc, colPlc){
  let changed=true;
  while(changed){
    changed=false;
    for(let r=0;r<size;r++){
      const known = grid.slice(r*size, r*size+size);
      const valid = filterPlacements(rowPlc[r], known);
      if(valid.length===0) return true;
      rowPlc[r] = valid;
      for(let c=0;c<size;c++){
        if(known[c]!==-1) continue;
        let all0=true, all1=true;
        for(const v of valid){
          if(v[c]===1) all0=false;
          if(v[c]===0) all1=false;
          if(!all0 && !all1) break;
        }
        if(all0){ grid[r*size+c]=0; changed=true; }
        else if(all1){ grid[r*size+c]=1; changed=true; }
      }
    }
    for(let c=0;c<size;c++){
      const known=[];
      for(let r=0;r<size;r++) known.push(grid[r*size+c]);
      const valid = filterPlacements(colPlc[c], known);
      if(valid.length===0) return true;
      colPlc[c] = valid;
      for(let r=0;r<size;r++){
        if(known[r]!==-1) continue;
        let all0=true, all1=true;
        for(const v of valid){
          if(v[r]===1) all0=false;
          if(v[r]===0) all1=false;
          if(!all0 && !all1) break;
        }
        if(all0){ grid[r*size+c]=0; changed=true; }
        else if(all1){ grid[r*size+c]=1; changed=true; }
      }
    }
  }
  return false;
}

// Count up to `cap` complete solutions to (rowClues, colClues) of given size.
// Returns { count, firstSolution }. `firstSolution` is the first complete grid found.
function countSolutions(rowClues, colClues, size, cap){
  cap = cap || 2;
  const rowPlc = rowClues.map(cl => enumPlacements(size, cl));
  const colPlc = colClues.map(cl => enumPlacements(size, cl));
  // Cheap guard: very wide lines blow up; we always cap branching depth instead.
  const initial = new Array(size*size).fill(-1);
  let found = 0;
  let firstSolution = null;

  function dfs(grid, rowPlcCopy, colPlcCopy){
    if(found >= cap) return;
    const g = grid.slice();
    const rp = rowPlcCopy.map(a => a.slice());
    const cp = colPlcCopy.map(a => a.slice());
    if(prune(g, size, rp, cp)) return;

    let undet = -1;
    for(let i=0;i<g.length;i++) if(g[i]===-1){ undet=i; break; }
    if(undet===-1){
      // complete
      if(found===0) firstSolution = g.slice();
      found++;
      return;
    }
    for(const v of [1, 0]){
      if(found >= cap) return;
      const g2 = g.slice();
      g2[undet] = v;
      dfs(g2, rp, cp);
    }
  }
  dfs(initial, rowPlc, colPlc);
  return { count: found, firstSolution };
}

// Decode a packed '0'/'1' string into a solution array.
function decodePregen(str){
  const out = new Array(str.length);
  for(let i=0;i<str.length;i++) out[i] = str.charCodeAt(i)===49 ? 1 : 0;
  return out;
}
function encodeSolution(sol){
  let s=''; for(let i=0;i<sol.length;i++) s += sol[i] ? '1' : '0';
  return s;
}

module.exports = {
  lineRuns, computeClues, enumPlacements, filterPlacements, prune,
  countSolutions, decodePregen, encodeSolution,
};
