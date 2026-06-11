// Verbatim prototype logic (docs/prototypes/ditto.html) + production filters.
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const N=6,DIRS={U:[0,-1],D:[0,1],L:[-1,0],R:[1,0]},DK=['U','D','L','R'];
function step(walls,bp,cp,q,dir){
  const mv=(p,d)=>{if(d==null)return p;const[dx,dy]=DIRS[d];let nx=p[0]+dx,ny=p[1]+dy;if(nx<0||ny<0||nx>=N||ny>=N||walls.has(ny*N+nx))return p;return[nx,ny];};
  const nb=mv(bp,dir),nc=mv(cp,q[0]);
  const collide=(nb[0]===nc[0]&&nb[1]===nc[1])||(nb[0]===cp[0]&&nb[1]===cp[1]&&nc[0]===bp[0]&&nc[1]===bp[1]);
  return{nb,nc,nq:[q[1],dir],collide};
}
function solve(walls,bs,cs,exit,plate){
  const enc=(b,c,q)=>b+'|'+c+'|'+(q[0]??'n')+'|'+(q[1]??'n');
  let frontier=[[bs,cs,[null,null]]];const seen=new Set([enc(bs,cs,[null,null])]);let depth=0;
  while(frontier.length){depth++;const next=[];
    for(const[b,c,q]of frontier)for(const d of DK){
      const{nb,nc,nq,collide}=step(walls,b,c,q,d);if(collide)continue;
      const k=enc(nb,nc,nq);if(seen.has(k))continue;seen.add(k);
      if(nb[0]===exit[0]&&nb[1]===exit[1]&&nc[0]===plate[0]&&nc[1]===plate[1])return depth;
      next.push([nb,nc,nq]);
    }
    frontier=next;if(depth>40)break;
  }return -1;
}
// production: BFS shortest you->exit (walls only) for the plate-detour filter
function shortestPath(walls,from,to){
  const key=p=>p[1]*N+p[0];
  const prev=new Map([[key(from),null]]);
  let frontier=[from];
  while(frontier.length){
    const next=[];
    for(const p of frontier){
      if(p[0]===to[0]&&p[1]===to[1]){
        const path=[];let k=key(p),cur=p;
        while(cur){path.push(cur);cur=prev.get(key(cur));}
        return path;
      }
      for(const d of DK){const[dx,dy]=DIRS[d];const nx=p[0]+dx,ny=p[1]+dy;
        if(nx<0||ny<0||nx>=N||ny>=N||walls.has(ny*N+nx))continue;
        if(prev.has(ny*N+nx))continue;prev.set(ny*N+nx,p);next.push([nx,ny]);}
    }
    frontier=next;
  }
  return null;
}
// gen parameterized by band (production); core acceptance logic = prototype's
function gen(seed, band){
  const rnd=mulberry32(seed);
  for(let t=0;t<5000;t++){
    const walls=new Set();const nW=band.walls[0]+Math.floor(rnd()*(band.walls[1]-band.walls[0]+1));
    while(walls.size<nW)walls.add(Math.floor(rnd()*N*N));
    const cells=[];for(let i=0;i<N*N;i++)if(!walls.has(i))cells.push([i%N,Math.floor(i/N)]);
    const pick=()=>cells[Math.floor(rnd()*cells.length)];
    const bs=pick(),cs=pick(),exit=pick(),plate=pick();
    const key=p=>p[0]+','+p[1];
    if(new Set([bs,cs,exit,plate].map(key)).size<4)continue;
    const par=solve(walls,bs,cs,exit,plate);
    if(par<band.par[0]||par>band.par[1])continue;
    // plate must force a detour: not on the natural shortest you->exit line
    const sp=shortestPath(walls,bs,exit);
    if(sp&&sp.some(p=>p[0]===plate[0]&&p[1]===plate[1]))continue;
    return{walls:[...walls].sort((a,b)=>a-b),bs,cs,exit,plate,par};
  }
  return null;
}
const BANDS={easy:{par:[5,8],walls:[4,6]},med:{par:[9,13],walls:[6,9]},hard:{par:[14,20],walls:[8,12]}};
// ── campaign: 60 seeds, 20 per band, ascending par within band ──
const campaign=[];
for(const[bandName,count]of[['easy',20],['med',20],['hard',20]]){
  const found=[];
  for(let seed=1000;found.length<count*3&&seed<99999;seed++){
    const L=gen(seed,BANDS[bandName]);
    if(L)found.push({seed,par:L.par,band:bandName});
  }
  found.sort((a,b)=>a.par-b.par);
  // even spread across the band's par range
  const step_=Math.max(1,Math.floor(found.length/count));
  for(let i=0;i<count;i++)campaign.push(found[Math.min(i*step_,found.length-1)]);
}
console.log("CAMPAIGN="+JSON.stringify(campaign));
// ── daily QA: 200 days from 2026-06-10 (dayNum ~160) ──
function dayBand(day){const wd=new Date(Date.UTC(2026,0,1)+day*864e5).getUTCDay();return wd===1||wd===2?'easy':(wd===0||wd===6?'hard':'med');}
let ok=0,fallback=0,fail=0;
for(let day=160;day<360;day++){
  const seed=(day*2654435761%2147483647)+1;
  let L=gen(seed,BANDS[dayBand(day)]);
  if(!L){L=gen(seed,{par:[7,22],walls:[4,10]});if(L)fallback++;}
  if(L)ok++;else fail++;
}
console.log(`DAILY: ok=${ok} (band-fallbacks=${fallback}) fail=${fail} of 200`);
