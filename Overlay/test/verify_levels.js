// Verbatim prototype logic (docs/prototypes/stack.html) + production filters.
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const N=5;
function composite(sheets,offs){const out=new Array(N*N).fill(0);
  for(let r=0;r<N;r++)for(let c=0;c<N;c++)for(let s=2;s>=0;s--){const[dx,dy]=offs[s];const sc=c-dx,sr=r-dy;
    if(sc<0||sr<0||sc>=N||sr>=N)continue;const v=sheets[s][sr*N+sc];if(v){out[r*N+c]=v;break;}}
  return out;}
function eqOff(a,b){return a.every((o,i)=>o[0]===b[i][0]&&o[1]===b[i][1]);}
function arrSame(a,b){return a.every((v,i)=>v===b[i]);}
// production: recognizability — lit cells form ONE orthogonal group, or the
// lit MASK is left-right symmetric
function recognizable(t){
  const lit=[];for(let i=0;i<N*N;i++)if(t[i])lit.push(i);
  if(!lit.length)return false;
  const seen=new Set([lit[0]]);const st=[lit[0]];
  while(st.length){const i=st.pop();const r=Math.floor(i/N),c=i%N;
    [[r-1,c],[r+1,c],[r,c-1],[r,c+1]].forEach(([rr,cc])=>{
      if(rr<0||cc<0||rr>=N||cc>=N)return;const j=rr*N+cc;
      if(t[j]&&!seen.has(j)){seen.add(j);st.push(j);}});}
  if(seen.size===lit.length)return true;
  for(let r=0;r<N;r++)for(let c=0;c<N;c++){
    if(!!t[r*N+c]!==!!t[r*N+(N-1-c)])return false;}
  return true;
}
// PART 5: exhaustive optimum — fewest single-cell slides from `init` to ANY
// offset config (within the slider's [-R,R] travel) whose composite equals
// the target. The witness `sol` is only accepted when it IS this optimum, so
// the stored par (`lower`) can never overstate the true minimum.
function optimalCost(sheets,target,init,R){
  let opt=Infinity;
  for(let ax=-R;ax<=R;ax++)for(let ay=-R;ay<=R;ay++)
   for(let bx=-R;bx<=R;bx++)for(let by=-R;by<=R;by++)
    for(let cx=-R;cx<=R;cx++)for(let cy=-R;cy<=R;cy++){
      const off=[[ax,ay],[bx,by],[cx,cy]];
      if(arrSame(composite(sheets,off),target)){
        const c=Math.abs(ax-init[0][0])+Math.abs(ay-init[0][1])
               +Math.abs(bx-init[1][0])+Math.abs(by-init[1][1])
               +Math.abs(cx-init[2][0])+Math.abs(cy-init[2][1]);
        if(c<opt)opt=c;
      }
    }
  return opt;
}
function gen(seed,band){
  const rnd=mulberry32(seed);
  const R=band.range, NC=band.colors;
  for(let t=0;t<3000;t++){
    const sheets=[];for(let s=0;s<3;s++){const g=new Array(N*N).fill(0);
      let cnt=band.density[0]+Math.floor(rnd()*(band.density[1]-band.density[0]+1));
      while(cnt-->0)g[Math.floor(rnd()*N*N)]=1+Math.floor(rnd()*NC);sheets.push(g);}
    const ro=()=>Math.floor(rnd()*(2*R+1))-R;
    const sol=[];for(let s=0;s<3;s++)sol.push([ro(),ro()]);
    const target=composite(sheets,sol);
    if(target.filter(x=>x).length<6)continue;
    if(band.recog&&!recognizable(target))continue;
    let init,g=0;do{init=[];for(let s=0;s<3;s++)init.push([ro(),ro()]);}while(g++<60&&(eqOff(init,sol)||arrSame(composite(sheets,init),target)));
    if(arrSame(composite(sheets,init),target))continue;
    const lower=sol.reduce((a,o,i)=>a+Math.abs(o[0]-init[i][0])+Math.abs(o[1]-init[i][1]),0);
    if(lower<band.minLower)continue;
    if(optimalCost(sheets,target,init,R)<lower)continue; // PART 5: witness must be the true optimum
    return{sheets,target,init,sol,lower};
  }return null;}
const BANDS={
  easy:{colors:2,density:[4,6],range:1,recog:true,minLower:2},
  med: {colors:3,density:[5,7],range:2,recog:true,minLower:4},
  hard:{colors:3,density:[6,8],range:2,recog:true,minLower:7},
};
// campaign: 20 per band, ascending lower-bound within band
const campaign=[];
for(const[bn,count]of[['easy',20],['med',20],['hard',20]]){
  const found=[];
  for(let seed=2000;found.length<count*3&&seed<99999;seed++){
    const L=gen(seed,BANDS[bn]);
    if(L)found.push({seed,band:bn,lower:L.lower});
  }
  found.sort((a,b)=>a.lower-b.lower);
  const st=Math.max(1,Math.floor(found.length/count));
  for(let i=0;i<count;i++)campaign.push(found[Math.min(i*st,found.length-1)]);
}
console.log("CAMPAIGN="+JSON.stringify(campaign));
function dayBand(day){const wd=new Date(Date.UTC(2026,0,1)+day*864e5).getUTCDay();return wd===1||wd===2?'easy':(wd===0||wd===6?'hard':'med');}
let ok=0,fb=0,fail=0;
for(let day=160;day<360;day++){
  const seed=(day*40503+12345)>>>0;
  let L=gen(seed,BANDS[dayBand(day)]);
  if(!L){L=gen(seed,{colors:3,density:[4,8],range:2,recog:false,minLower:1});if(L)fb++;}
  if(L)ok++;else fail++;
}
console.log(`DAILY: ok=${ok} fallbacks=${fb} fail=${fail} of 200`);
