// PipeConnect level generator — solvable WITH full coverage by construction:
// a Hamiltonian path on the NxN grid (serpentine + seeded backbite moves)
// is cut into segments; segment endpoints become the dot pairs.
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const COLORS=['red','blue','green','yellow','purple','orange','pink','teal'];
function serpentine(N){
  const p=[];
  for(let r=0;r<N;r++){
    if(r%2===0)for(let c=0;c<N;c++)p.push(r*N+c);
    else for(let c=N-1;c>=0;c--)p.push(r*N+c);
  }
  return p;
}
function neighbors(i,N){
  const r=Math.floor(i/N),c=i%N,out=[];
  if(r>0)out.push(i-N);if(r<N-1)out.push(i+N);
  if(c>0)out.push(i-1);if(c<N-1)out.push(i+1);
  return out;
}
function backbite(path,N,rnd,steps){
  // classic Hamiltonian-path randomizer: pick an end, connect to a random
  // grid-neighbor inside the path, reverse the loop section.
  let p=path.slice();
  const idx=new Map();p.forEach((v,i)=>idx.set(v,i));
  for(let s=0;s<steps;s++){
    const fromHead=rnd()<0.5;
    if(!fromHead)p.reverse(),p.forEach((v,i)=>idx.set(v,i));
    const head=p[0];
    const nbs=neighbors(head,N).filter(n=>idx.get(n)>1);
    if(!nbs.length)continue;
    const n=nbs[Math.floor(rnd()*nbs.length)];
    const j=idx.get(n);
    // reverse p[0..j-1]
    const rev=p.slice(0,j).reverse();
    p=rev.concat(p.slice(j));
    p.forEach((v,i)=>idx.set(v,i));
  }
  return p;
}
function gen(seed,N,pairs){
  const rnd=mulberry32(seed);
  for(let t=0;t<60;t++){
    const path=backbite(serpentine(N),N,rnd,N*N*8);
    // cut into `pairs` segments, each length >= 3
    const total=N*N;
    if(pairs*3>total)return null;
    // random cut points with min seg length 3
    let lens=null;
    for(let a=0;a<200;a++){
      const cuts=new Set();
      while(cuts.size<pairs-1)cuts.add(3+Math.floor(rnd()*(total-3)));
      const cl=[...cuts].sort((x,y)=>x-y);
      const ls=[];let prev=0;
      for(const c of cl){ls.push(c-prev);prev=c;}
      ls.push(total-prev);
      if(ls.every(l=>l>=3)){lens=ls;break;}
    }
    if(!lens)continue;
    const dots=[];let at=0;let ok=true;
    lens.forEach((len,si)=>{
      const seg=path.slice(at,at+len);at+=len;
      const a=seg[0],b=seg[len-1];
      dots.push([Math.floor(a/N),a%N,COLORS[si]]);
      dots.push([Math.floor(b/N),b%N,COLORS[si]]);
    });
    // sanity: all dot cells distinct (guaranteed by partition) + pair endpoints not adjacent-trivial for most
    return {size:N,dots};
  }
  return null;
}
// 378 new levels (123-500): ramp sizes + pair counts
const PLAN=[
  {count:78, size:6, pairs:[5,6]},   // 123-200
  {count:100,size:7, pairs:[5,7]},   // 201-300
  {count:100,size:8, pairs:[6,8]},   // 301-400
  {count:100,size:9, pairs:[6,8]},   // 401-500
];
const out=[];let seed=70000;
for(const ph of PLAN){
  let made=0;
  while(made<ph.count&&seed<500000){
    const rnd=mulberry32(seed);
    const pairs=ph.pairs[0]+Math.floor(rnd()*(ph.pairs[1]-ph.pairs[0]+1));
    const L=gen(seed,ph.size,pairs);
    seed++;
    if(L){out.push(L);made++;}
  }
}
console.error("generated:",out.length);
// verify: every level's dots are on distinct cells, colors ≤8, full partition by construction
out.forEach((L,i)=>{
  const k=new Set(L.dots.map(d=>d[0]*L.size+d[1]));
  if(k.size!==L.dots.length)throw new Error('dup dot in level '+i);
});
console.error("verification: all dot sets valid");
const lines=[];
let n=123;
let curSize=0;
out.forEach(L=>{
  if(L.size!==curSize){curSize=L.size;lines.push(`// ${n}+: ${L.size}x${L.size}`);}
  lines.push(`{size:${L.size},dots:${JSON.stringify(L.dots).replace(/"/g,"'")}},`);
  n++;
});
console.log(lines.join('\n'));
