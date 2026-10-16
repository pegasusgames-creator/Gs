// Builds the LEVELS region of game.html from mined deals (see gen_levels.js).
//   campaign : 500 deals — 10 quick openers (hunt) then the pool ordered easy → hard
//   KS_DAILY : 364 deals, index = day % 364; weekday bands (Mon/Tue easy,
//              Wed–Fri medium, Sat/Sun hard). 2026-01-01 (day 0) is a Thursday.
// Every entry is re-verified (replay to four complete foundations) before writing.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const HERE=__dirname,APP=path.resolve(HERE,'..'),BASE=path.resolve(APP,'..');
const {K,verify,grade,faceUpAt}=require('./gen_levels.js');
function read(f){return fs.existsSync(f)?fs.readFileSync(f,'utf8').trim().split('\n').filter(Boolean).map(l=>JSON.parse(l)):[];}
function diff(r){return (1-r.wr)*100+Math.log2((r.nodes||0)+1)*3+r.par/8;}
function build(inFile){
  const mined=read(inFile).filter(r=>r.sol);
  const easy=read(path.join(HERE,'easy.jsonl')).filter(r=>r.sol);
  const seen=new Set();const uniq=a=>a.filter(r=>!seen.has(r.seed)&&seen.add(r.seed));
  const openers=uniq(easy.sort((a,b)=>(a.fu-b.fu)||(b.wr-a.wr))).slice(0,10);
  let pool=uniq(easy.concat(mined));
  // keep the 854 shortest lines (smaller file, tighter par), then grade
  pool.sort((a,b)=>a.par-b.par);pool=pool.slice(0,854).sort((a,b)=>diff(a)-diff(b));
  const camp=[],daily=[];
  pool.forEach((r,i)=>{ (Math.floor(i*364/854)!==Math.floor((i+1)*364/854)?daily:camp).push(r); });
  if(camp.length!==490||daily.length!==364)throw new Error('split '+camp.length+'/'+daily.length);
  const campaign=openers.concat(camp);
  const bands={easy:daily.slice(0,104),med:daily.slice(104,260),hard:daily.slice(260)};
  const rng=K.ksRng(364);for(const k in bands){const a=bands[k];for(let i=a.length-1;i>0;i--){const j=rng()%(i+1);[a[i],a[j]]=[a[j],a[i]];}}
  const days=[];
  for(let i=0;i<364;i++){const wd=(4+i)%7;const b=(wd===1||wd===2)?'easy':(wd===0||wd===6)?'hard':'med';days.push(bands[b].shift());}
  // store whichever verified winning line turns every card face-up soonest:
  // par (shown in the HUD) = that line's moves until auto-finish takes over
  let swapped=0;
  for(const r of campaign.concat(days)){
    if(r.wr>0){const g=grade(r.seed);if(g.line&&verify(r.seed,g.line)&&faceUpAt(r.seed,g.line)<faceUpAt(r.seed,r.sol)){r.sol=g.line;swapped++;}}
    r.pfu=faceUpAt(r.seed,r.sol);
    if(!verify(r.seed,r.sol))throw new Error('verify '+r.seed);
  }
  console.log('lines swapped for a faster no-peek win:',swapped);
  const q=r=>"'"+r.seed+':'+r.sol+"'";
  const txt=[
    '// LEVELS — 500 numbered WINNABLE draw-1 Klondike deals + a 364-day Daily Deal pool.',
    '// Each entry is "<seed>:<winning line>": the seed deals the board through the',
    '// KLONDIKE CORE (ksDeal), the line is a solver-found win in the compact codec',
    '// (ksDecode). Mined + graded by test/gen_levels.js (greedy no-peek playouts order',
    '// the campaign easy → hard), built by test/build_levels.js and gated by',
    '// scripts/check_solitaire_winnable.py (re-deal + replay to four full foundations).',
    '// Par = moves of the stored line until every tableau card is face-up (the game',
    '// auto-finishes from there; auto-finish moves are not counted).',
    'const CAMPAIGN = [',
    campaign.map(q).join(',\n'),
    '];',
    'const LEVELS = CAMPAIGN; // length contract for level-select/addendum',
    '// KS_DAILY[day % 364] — Mon/Tue easy, Wed–Fri medium, Sat/Sun hard.',
    'const KS_DAILY = [',
    days.map(q).join(',\n'),
    '];',''].join('\n');
  const out=path.join(HERE,'levels_region.js');fs.writeFileSync(out,txt);
  fs.writeFileSync(path.join(HERE,'levels.json'),JSON.stringify({campaign:campaign.map(r=>({seed:r.seed,par:r.pfu,line:r.sol.length,wr:r.wr,fu:r.fu,nodes:r.nodes})),daily:days.map(r=>({seed:r.seed,par:r.pfu,wr:r.wr}))},null,1)+'\n');
  cp.execFileSync('python3',[path.join(BASE,'scripts/shell_region.py'),'Solitaire','LEVELS','--set',out],{stdio:'inherit'});
  fs.unlinkSync(out);
  const pars=campaign.map(r=>r.pfu);
  console.log('campaign',campaign.length,'daily',days.length,'opener fu',openers.map(r=>r.fu).join(','),
    'par first10',pars.slice(0,10).join(','),'last',pars.slice(-5).join(','),'bytes',txt.length);
}
module.exports={build};
