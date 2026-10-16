#!/usr/bin/env node
// Solitaire (Klondike) deal miner.
//
// Mines WINNABLE draw-1 deals: every candidate seed is dealt by the game's own
// KLONDIKE CORE (extracted verbatim from game.html between /*KSCORE{*/ and
// /*}KSCORE*/ — one source of truth), solved by the core's full-knowledge DFS,
// and the solver's move list is replayed move-by-move with ksLegal/ksApply to
// four complete foundations before the deal is accepted.
//
// Difficulty is graded the way a person meets the deal: 24 randomized greedy
// playouts that never peek at face-down cards. Win rate (and the taps needed to
// turn every tableau card face-up) orders the campaign easy → hard and bands the
// daily pool.
//
//   node Solitaire/test/gen_levels.js mine  [want] [out.jsonl]   (append-only, resumable)
//   node Solitaire/test/gen_levels.js build [in.jsonl]           → test/levels.json + regions
'use strict';
const fs=require('fs'),path=require('path');
const HERE=__dirname,APP=path.resolve(HERE,'..');
const GAME=path.join(APP,'android/app/src/main/assets/game.html');
function loadCore(){
  const src=process.env.KSCORE?fs.readFileSync(process.env.KSCORE,'utf8'):fs.readFileSync(GAME,'utf8');
  const a=src.indexOf('/*KSCORE{*/'),b=src.indexOf('/*}KSCORE*/');
  if(a<0||b<0)throw new Error('KSCORE block not found');
  return new Function(src.slice(a,b)+';return {ksDeal,ksSolve,ksLegal,ksApply,ksWon,ksEncode,ksDecode,ksClone,ksRng,ksRank,ksSuit,ksStack,ksFlip,ksRed};')();
}
const K=loadCore();

// ── human-like greedy playout (no knowledge of face-down cards) ──
function playout(seed,rng){
  const S=K.ksDeal(seed,1);let moves=0,faceUpAt=-1,idle=0;
  const pick=a=>a[Math.floor(rng()*a.length)];
  const fnd=x=>S.f[K.ksSuit(x)]===K.ksRank(x);
  const allUp=()=>S.h.every(v=>v===0);
  for(let step=0;step<1500;step++){
    if(K.ksWon(S))return {won:true,moves,faceUpAt:faceUpAt<0?moves:faceUpAt};
    if(faceUpAt<0&&allUp())faceUpAt=moves;
    const cand=[];
    // 1 foundation plays that reveal or are low
    for(let c=0;c<7;c++){const col=S.t[c];if(!col.length)continue;const x=col[col.length-1];
      if(fnd(x)&&(K.ksRank(x)<=1||(col.length-1===S.h[c]&&S.h[c]>0)))cand.push({k:'m',s:c,d:8});}
    if(S.p>0&&fnd(S.T[S.p-1])&&K.ksRank(S.T[S.p-1])<=1)cand.push({k:'m',s:7,d:8});
    // 2 runs that turn a card face-up
    if(!cand.length){let best=-1;
      for(let c=0;c<7;c++){if(!S.t[c].length||S.h[c]===0)continue;
        for(let d=0;d<7;d++){if(d===c)continue;const m={k:'m',s:c,d};
          if(K.ksLegal(S,m)&&S.t[d].length>=0){const i=S.t[c].length-1;void i;
            // whole face-up run only
            const dst=S.t[d];const x=S.t[c][S.h[c]];
            const fits=dst.length?K.ksStack(x,dst[dst.length-1]):K.ksRank(x)===12;
            if(fits){if(S.h[c]>best){best=S.h[c];cand.length=0;}if(S.h[c]===best)cand.push(m);}}}}}
    // 3 waste → tableau
    if(!cand.length&&S.p>0)for(let d=0;d<7;d++){const m={k:'m',s:7,d};if(K.ksLegal(S,m))cand.push(m);}
    // 4 any foundation play
    if(!cand.length){for(let c=0;c<7;c++){const m={k:'m',s:c,d:8};if(K.ksLegal(S,m))cand.push(m);}
      const m={k:'m',s:7,d:8};if(K.ksLegal(S,m))cand.push(m);}
    if(cand.length){const m=pick(cand);K.ksApply(S,m);moves++;idle=0;continue;}
    // 5 stock
    if(S.p<S.T.length){K.ksApply(S,{k:'d'});moves++;continue;}
    if(S.p>0){if(++idle>1)break;K.ksApply(S,{k:'r'});moves++;continue;}
    break;
  }
  return {won:K.ksWon(S),moves,faceUpAt};
}
function grade(seed){
  const rng=K.ksRng(seed^0x5bd1e995);const r=()=>rng()/4294967296;
  let wins=0,fu=1e9,mv=[];
  for(let i=0;i<24;i++){const o=playout(seed,r);if(o.won){wins++;fu=Math.min(fu,o.faceUpAt);mv.push(o.moves);}}
  mv.sort((a,b)=>a-b);
  return {wr:wins/24,fu:wins?fu:-1,hm:wins?mv[mv.length>>1]:-1};
}
function verify(seed,enc){
  const S=K.ksDeal(seed,1);
  for(const m of K.ksDecode(enc)){if(!K.ksLegal(S,m))return false;K.ksApply(S,m);}
  return K.ksWon(S);
}

function mine(want,out){
  const have=fs.existsSync(out)?fs.readFileSync(out,'utf8').trim().split('\n').filter(Boolean).map(l=>JSON.parse(l)):[];
  const seen=new Set(have.map(r=>r.seed));let tried=have.length?Math.max(...have.map(r=>r.i))+1:0;
  const src=K.ksRng(20261016);for(let i=0;i<tried;i++)src();
  let ok=have.filter(r=>r.sol).length;const t0=Date.now();
  while(ok<want&&Date.now()-t0<9.5*60*1000){
    const seed=(src()&0x7fffffff)||1;const i=tried++;
    if(seen.has(seed))continue;seen.add(seed);
    const r=K.ksSolve(K.ksDeal(seed,1),250000);
    let rec={i,seed,sol:null,nodes:r.nodes};
    if(r.moves){const enc=K.ksEncode(r.moves);
      if(!verify(seed,enc))throw new Error('replay failed for '+seed);
      rec=Object.assign(rec,{sol:enc,par:r.moves.length},grade(seed));ok++;}
    fs.appendFileSync(out,JSON.stringify(rec)+'\n');
  }
  console.log('mined',ok,'winnable of',tried,'tried in',((Date.now()-t0)/1000).toFixed(0)+'s');
}
module.exports={K,playout,grade,verify};
if(require.main===module){
  const [cmd,a1,a2]=process.argv.slice(2);
  if(cmd==='mine')mine(+a1||900,a2||path.join(HERE,'mined.jsonl'));
  else if(cmd==='build')require('./build_levels.js').build(a1||path.join(HERE,'mined.jsonl'));
  else console.log('usage: gen_levels.js mine [want] [out] | build [in]');
}
