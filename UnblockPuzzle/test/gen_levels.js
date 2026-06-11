// UnblockPuzzle generator v2 — same semantics as check_unblock_solvable.py.
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const G=6;
function solve(specs, init, maxDepth){
  const n=specs.length;
  const redI=0; const rw=2;
  if(init[0][0]+rw>=G)return 0;
  const enc=p=>{let s='';for(let i=0;i<n;i++)s+=String.fromCharCode(p[i][0]*8+p[i][1]);return s;};
  const seen=new Set([enc(init)]);
  let frontier=[init];
  for(let depth=1;depth<=maxDepth;depth++){
    const nxt=[];
    for(const pos of frontier){
      const occ=new Uint8Array(G*G);
      for(let i=0;i<n;i++){const x=pos[i][0],y=pos[i][1];const w=specs[i][0],h=specs[i][1];
        for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++)occ[(y+dy)*G+x+dx]=1;}
      for(let i=0;i<n;i++){
        const x=pos[i][0],y=pos[i][1];const w=specs[i][0],h=specs[i][1],isRed=specs[i][2];
        for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++)occ[(y+dy)*G+x+dx]=0;
        if(w>1){
          for(let nx2=x-1;nx2>=0;nx2--){
            if(occ[y*G+nx2]){break;}
            const np=pos.slice();np[i]=[nx2,y];const k=enc(np);
            if(!seen.has(k)){seen.add(k);nxt.push(np);}
          }
          for(let nx2=x+1;nx2+w<=G;nx2++){
            if(occ[y*G+nx2+w-1]){break;}
            const np=pos.slice();np[i]=[nx2,y];const k=enc(np);
            if(!seen.has(k)){seen.add(k);if(isRed&&nx2+w>=G)return depth;nxt.push(np);}
          }
        }else{
          for(let ny=y-1;ny>=0;ny--){
            if(occ[ny*G+x]){break;}
            const np=pos.slice();np[i]=[x,ny];const k=enc(np);
            if(!seen.has(k)){seen.add(k);nxt.push(np);}
          }
          for(let ny=y+1;ny+h<=G;ny++){
            if(occ[(ny+h-1)*G+x]){break;}
            const np=pos.slice();np[i]=[x,ny];const k=enc(np);
            if(!seen.has(k)){seen.add(k);nxt.push(np);}
          }
        }
        for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++)occ[(y+dy)*G+x+dx]=1;
      }
    }
    if(!nxt.length)return -1;
    frontier=nxt;
  }
  return -1;
}
function candidate(seed, band){
  const rnd=mulberry32(seed);
  const specs=[[2,1,true]];
  const pos=[[Math.floor(rnd()*3),2]];
  const occ=new Uint8Array(G*G);
  occ[2*G+pos[0][0]]=1;occ[2*G+pos[0][0]+1]=1;
  const nBlocks=band.blocks[0]+Math.floor(rnd()*(band.blocks[1]-band.blocks[0]+1));
  for(let b=0;b<nBlocks;b++){
    let placed=false;
    for(let a=0;a<60&&!placed;a++){
      const vert=rnd()<0.55;
      const len=2+(rnd()<0.3?1:0);
      if(vert){
        const x=Math.floor(rnd()*G), y=Math.floor(rnd()*(G-len+1));
        let free=true;for(let d=0;d<len;d++)if(occ[(y+d)*G+x])free=false;
        if(!free)continue;
        for(let d=0;d<len;d++)occ[(y+d)*G+x]=1;
        specs.push([1,len,false]);pos.push([x,y]);placed=true;
      }else{
        let y=Math.floor(rnd()*G);
        if(y===2)continue;
        const x=Math.floor(rnd()*(G-len+1));
        let free=true;for(let d=0;d<len;d++)if(occ[y*G+x+d])free=false;
        if(!free)continue;
        for(let d=0;d<len;d++)occ[y*G+x+d]=1;
        specs.push([len,1,false]);pos.push([x,y]);placed=true;
      }
    }
    if(!placed)return null;
  }
  const opt=solve(specs,pos,band.opt[1]);     // cap at band max — cheap reject
  if(opt>=band.opt[0]&&opt<=band.opt[1])return{specs,pos,opt};
  return null;
}
const BANDS=[
  {count:100,blocks:[8,11], opt:[10,16]},
  {count:130,blocks:[9,12], opt:[14,21]},
  {count:120,blocks:[10,13],opt:[18,28]},
];
const out=[];let seed=50000;
for(const band of BANDS){
  const found=[];
  while(found.length<band.count&&seed<3000000){
    const L=candidate(seed++,band);
    if(L){found.push(L);if(found.length%20===0)console.error(`band opt${band.opt}: ${found.length}/${band.count} (seed ${seed})`);}
  }
  found.sort((a,b)=>a.opt-b.opt);
  out.push(...found);
  console.error(`band done: ${found.length}`);
}
console.error("generated:",out.length);
const lines=[];
out.forEach((L,i)=>{
  const parts=L.specs.map((s,j)=>{
    const x=L.pos[j][0],y=L.pos[j][1];
    if(s[2])return`R(${x})`;
    return s[0]>1?`H(${x},${y},${s[0]})`:`V(${x},${y},${s[1]})`;
  });
  lines.push(`// Level ${151+i}`);
  lines.push(`{blocks:[${parts.join(',')}],optimal:${L.opt}},`);
});
console.log(lines.join('\n'));
