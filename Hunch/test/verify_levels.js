// Verbatim prototype core (docs/prototypes/greenlight.html) + production:
// 18-rule catalog across 6 categories + DISAMBIGUATING mystery boards
// (no other catalog rule classifies all 3 boards identically to the truth).
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const RULES=[
 // count
 {cat:'count',tier:0,name:'Exactly 6 cells are lit.',fn:g=>g.filter(x=>x).length===6},
 {cat:'count',tier:0,name:'Exactly 4 cells are lit.',fn:g=>g.filter(x=>x).length===4},
 {cat:'count',tier:0,name:'An even number of cells are lit (at least two).',fn:g=>{const n=g.filter(x=>x).length;return n>=2&&n%2===0;}},
 {cat:'count',tier:1,name:'An odd number of cells are lit.',fn:g=>g.filter(x=>x).length%2===1},
 // position / regions
 {cat:'position',tier:0,name:'All four corner cells are lit.',fn:g=>g[0]&&g[3]&&g[12]&&g[15]},
 {cat:'position',tier:0,name:'No corner cell is lit (and something is lit).',fn:g=>!g[0]&&!g[3]&&!g[12]&&!g[15]&&g.some(x=>x)},
 {cat:'position',tier:1,name:'Every lit cell is on the border (none in the middle four).',fn:g=>g.some(x=>x)&&!g[5]&&!g[6]&&!g[9]&&!g[10]},
 {cat:'position',tier:1,name:'Each 2x2 corner quadrant has at least one lit cell.',fn:g=>{const q=[[0,1,4,5],[2,3,6,7],[8,9,12,13],[10,11,14,15]];return q.every(c=>c.some(i=>g[i]));}},
 // rows / cols
 {cat:'rows',tier:1,name:'Exactly one cell is lit in every row.',fn:g=>{for(let r=0;r<4;r++){let c=0;for(let k=0;k<4;k++)if(g[r*4+k])c++;if(c!==1)return false;}return true;}},
 {cat:'rows',tier:1,name:'Exactly one cell is lit in every column.',fn:g=>{for(let c=0;c<4;c++){let n=0;for(let r=0;r<4;r++)if(g[r*4+c])n++;if(n!==1)return false;}return true;}},
 {cat:'rows',tier:0,name:'Every column has at least one lit cell.',fn:g=>{for(let c=0;c<4;c++){let any=false;for(let r=0;r<4;r++)if(g[r*4+c])any=true;if(!any)return false;}return true;}},
 {cat:'rows',tier:1,name:'No row is completely lit.',fn:g=>{for(let r=0;r<4;r++){let n=0;for(let k=0;k<4;k++)if(g[r*4+k])n++;if(n===4)return false;}return g.some(x=>x);}},
 // symmetry
 {cat:'symmetry',tier:1,name:'The pattern is mirror-symmetric: the left half mirrors the right.',fn:g=>{for(let r=0;r<4;r++)for(let c=0;c<2;c++)if(g[r*4+c]!==g[r*4+(3-c)])return false;return true;}},
 {cat:'symmetry',tier:2,name:'The pattern is the same upside-down (180 degree rotation).',fn:g=>{for(let i=0;i<8;i++)if(g[i]!==g[15-i])return false;return true;}},
 {cat:'symmetry',tier:2,name:'The top half mirrors the bottom half.',fn:g=>{for(let r=0;r<2;r++)for(let c=0;c<4;c++)if(g[r*4+c]!==g[(3-r)*4+c])return false;return true;}},
 // comparison
 {cat:'comparison',tier:1,name:'The top half has more lit cells than the bottom half.',fn:g=>{let t=0,b=0;for(let i=0;i<16;i++)if(g[i])(i<8?t++:b++);return t>b;}},
 {cat:'comparison',tier:2,name:'The left half and right half have the same number of lit cells.',fn:g=>{let l=0,r=0;for(let i=0;i<16;i++)if(g[i])((i%4)<2?l++:r++);return l===r&&(l+r)>0;}},
 // adjacency / connectivity
 {cat:'adjacency',tier:2,name:'No two lit cells touch side-by-side or top-to-bottom.',fn:g=>{if(!g.some(x=>x))return false;for(let r=0;r<4;r++)for(let c=0;c<4;c++){if(!g[r*4+c])continue;if(c<3&&g[r*4+c+1])return false;if(r<3&&g[(r+1)*4+c])return false;}return true;}},
 {cat:'adjacency',tier:2,name:'All lit cells form one connected group.',fn:g=>{const on=[];for(let i=0;i<16;i++)if(g[i])on.push(i);if(!on.length)return false;const seen=new Set([on[0]]),st=[on[0]];while(st.length){const i=st.pop(),r=(i/4|0),c=i%4;[[r-1,c],[r+1,c],[r,c-1],[r,c+1]].forEach(([nr,nc])=>{if(nr<0||nc<0||nr>=4||nc>=4)return;const j=nr*4+nc;if(g[j]&&!seen.has(j)){seen.add(j);st.push(j);}});}return seen.size===on.length;}},
];
// Disambiguating mystery boards: ≥1 pass + ≥1 fail vs the true rule AND no
// other catalog rule agrees with the truth on all three boards.
function mysteryBoards(ruleIdx,rnd){
  const rule=RULES[ruleIdx];
  for(let attempt=0;attempt<4000;attempt++){
    const out=[];let p=0,f=0,guard=0;
    while(out.length<3&&guard++<6000){
      const g=[];for(let i=0;i<16;i++)g.push(rnd()<0.4);
      const res=rule.fn(g);
      if(res&&p<2){out.push({g,res});p++;}
      else if(!res&&f<2){out.push({g,res});f++;}
    }
    if(out.length<3||p<1||f<1)continue;
    let ambiguous=false;
    for(let r2=0;r2<RULES.length;r2++){
      if(r2===ruleIdx)continue;
      if(out.every(m=>RULES[r2].fn(m.g)===m.res)){ambiguous=true;break;}
    }
    if(!ambiguous)return out;
  }
  return null;
}
// campaign: 60 levels, tier ramp 0→2, each rule recurs with distinct seeds
const order=[];
[0,1,2].forEach(t=>{RULES.forEach((r,i)=>{if(r.tier===t)order.push(i);});});
const campaign=[];
let li=0;
while(campaign.length<60){
  const ruleIdx=order[li%order.length];
  const seed=(9000+campaign.length*7331)>>>0;
  const rnd=mulberry32(seed);
  if(mysteryBoards(ruleIdx,rnd))campaign.push({rule:ruleIdx,seed});
  li++;
}
console.log("CAMPAIGN="+JSON.stringify(campaign));
// daily QA: 200 days; rule pool by weekday tier
function dayTier(day){const wd=new Date(Date.UTC(2026,0,1)+day*864e5).getUTCDay();return wd===1||wd===2?0:(wd===0||wd===6?2:1);}
let ok=0,fb=0,fail=0;
for(let day=160;day<360;day++){
  const seed=(day*2246822519)>>>0;
  const rnd=mulberry32(seed);
  const tier=dayTier(day);
  const pool=RULES.map((r,i)=>i).filter(i=>RULES[i].tier===tier);
  const ruleIdx=pool[Math.floor(rnd()*pool.length)];
  const m=mysteryBoards(ruleIdx,mulberry32((seed^0x9e3779b9)>>>0));
  if(m)ok++;else{const m2=mysteryBoards(ruleIdx,mulberry32(day+999));if(m2){ok++;fb++;}else fail++;}
}
console.log(`DAILY: ok=${ok} fallbacks=${fb} fail=${fail} of 200`);
console.log("rules:",RULES.length,"cats:",new Set(RULES.map(r=>r.cat)).size);
