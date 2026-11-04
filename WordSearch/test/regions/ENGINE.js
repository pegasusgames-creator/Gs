// GAME ENGINE
// ============================================================
// ━━ WORD SEARCH CORE ━━
// Campaign grids are STORED (CAMPAIGN, mined by test/gen_levels.py and
// verified by scripts/check_wordsearch_valid.py). Daily + Endless grids are
// built here by wsGen(), which applies the same rules on-device: every
// listed word exactly once on a straight line, no word inside another, and
// no blocklisted word readable in any direction (WS_BLOCK_H hashes).
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const WS_D=[[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]; // E SE S SW W NW N NE
const WS_B36='0123456789abcdefghijklmnopqrstuvwxyz';
const WS_ALL_DIRS=[0,1,2,3,4,5,6,7];
const WS_WORDS_FOR={6:[8,8],7:[8,10],8:[9,11],9:[10,12],10:[11,13],11:[12,14],12:[13,15],13:[14,17],14:[15,18],15:[16,20]};
const WS_FREQ=(function(){const f={E:13,T:9,A:8,O:8,I:7,N:7,S:6,H:6,R:6,D:4,L:4,C:3,U:3,M:2,W:2,F:2,G:2,Y:2,P:2,B:2,V:1,K:1};let s='';for(const k in f)s+=k.repeat(f[k]);return s;})();
const WS_BLOCK_SET=new Set(WS_BLOCK_H);
const WS_BLOCK_MAX=8;
function wsHash(s){let h=0x811c9dc5;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h>>>0;}
function wsCells(n,len,r,c,d){const out=[];for(let i=0;i<len;i++){const rr=r+WS_D[d][0]*i,cc=c+WS_D[d][1]*i;if(rr<0||cc<0||rr>=n||cc>=n)return null;out.push(rr*n+cc);}return out;}
function wsParsePlace(tok,n){const w=tok.slice(0,-3),p=tok.slice(-3);return{w:w,cells:wsCells(n,w.length,WS_B36.indexOf(p[0]),WS_B36.indexOf(p[1]),+p[2])};}
function wsPar(n,count){return Math.max(30,Math.round(count*(2+0.85*n)/5)*5);}
function wsShuffle(a,rnd){for(let i=a.length-1;i>0;i--){const j=Math.floor(rnd()*(i+1));const t=a[i];a[i]=a[j];a[j]=t;}return a;}
function wsRel(a,b){const ra=a.split('').reverse().join('');return a.indexOf(b)>=0||b.indexOf(a)>=0||ra.indexOf(b)>=0||b.indexOf(ra)>=0;}
const _wsLineCache={};
function wsLines(n){ // every straight line, all 8 reading directions
  if(_wsLineCache[n])return _wsLineCache[n];
  const base=[];
  for(let r=0;r<n;r++){const l=[];for(let c=0;c<n;c++)l.push(r*n+c);base.push(l);}
  for(let c=0;c<n;c++){const l=[];for(let r=0;r<n;r++)l.push(r*n+c);base.push(l);}
  for(let k=-(n-1);k<n;k++){const l=[];for(let r=0;r<n;r++){const c=r+k;if(c>=0&&c<n)l.push(r*n+c);}if(l.length>=2)base.push(l);}
  for(let k=0;k<2*n-1;k++){const l=[];for(let r=0;r<n;r++){const c=k-r;if(c>=0&&c<n)l.push(r*n+c);}if(l.length>=2)base.push(l);}
  const all=base.concat(base.map(l=>l.slice().reverse()));
  return(_wsLineCache[n]=all);
}
function wsCount(g,n,w){ // distinct cell-sets spelling w
  const seen=new Set();
  for(const l of wsLines(n)){let s='';for(const i of l)s+=g[i];let k=s.indexOf(w);
    while(k>=0){seen.add(l.slice(k,k+w.length).slice().sort((a,b)=>a-b).join(','));k=s.indexOf(w,k+1);}}
  return seen.size;
}
function wsBlocked(g,n){
  for(const l of wsLines(n)){for(let i=0;i<l.length;i++){let h=0x811c9dc5;
    for(let j=i;j<l.length&&j-i<WS_BLOCK_MAX;j++){h^=g[l[j]].charCodeAt(0);h=Math.imul(h,0x01000193)>>>0;if(j-i>=2&&WS_BLOCK_SET.has(h>>>0))return true;}}}
  return false;
}
// ── on-device generator (Daily + Endless) ──
function wsTryPlace(B,w,dirs,rnd,bias){
  const n=B.n,L=w.length,cands=[];let best=0;
  for(const d of dirs){const dr=WS_D[d][0],dc=WS_D[d][1],ax=d%4;
    for(let r=0;r<n;r++){const er=r+dr*(L-1);if(er<0||er>=n)continue;
      for(let c=0;c<n;c++){const ec=c+dc*(L-1);if(ec<0||ec>=n)continue;
        let ov=0,ok=true;
        for(let i=0;i<L;i++){const k=(r+dr*i)*n+(c+dc*i),ch=B.g[k];if(ch===null)continue;if(ch!==w[i]||B.ax[k].has(ax)){ok=false;break;}ov++;}
        if(ok&&ov<L){cands.push([ov,r,c,d]);if(ov>best)best=ov;}}}}
  if(!cands.length)return null;
  let pool=cands;if(bias>0&&rnd()<bias)pool=cands.filter(x=>x[0]===best);
  const[ov,r,c,d]=pool[Math.floor(rnd()*pool.length)];
  const cells=[];for(let i=0;i<L;i++){const k=(r+WS_D[d][0]*i)*n+(c+WS_D[d][1]*i);B.g[k]=w[i];B.ax[k].add(d%4);cells.push(k);}
  return{w:w,cells:cells};
}
function wsGen(seed,ti,n,count,dirs,mn,mx,withBonus){
  const rnd=mulberry32(seed>>>0||1),T=WS_THEMES[ti];
  const pool=T.w.filter(w=>w.length>=mn&&w.length<=mx);
  for(let att=0;att<250;att++){
    const order=wsShuffle(pool.slice(),rnd),chosen=[];
    for(const w of order){if(chosen.length>=count)break;if(chosen.some(p=>wsRel(w,p)))continue;chosen.push(w);}
    if(chosen.length<count)return null;
    const spare=order.filter(w=>chosen.indexOf(w)<0);
    chosen.sort((a,b)=>b.length-a.length);
    const B={n:n,g:new Array(n*n).fill(null),ax:Array.from({length:n*n},()=>new Set())};
    const placed=[];let fail=false;
    for(let w of chosen){
      let p=wsTryPlace(B,w,dirs,rnd,0.35);
      while(!p&&spare.length){const alt=spare.shift();if(placed.some(q=>wsRel(alt,q.w))||chosen.some(q=>q!==w&&wsRel(alt,q)))continue;w=alt;p=wsTryPlace(B,w,dirs,rnd,0.35);}
      if(!p){fail=true;break;}
      placed.push(p);
    }
    if(fail)continue;
    let bonus=null;
    if(withBonus){
      const bp=wsShuffle(T.w.filter(w=>w.length>=4&&w.length<=Math.min(n,9)&&!placed.some(q=>wsRel(w,q.w))),rnd);
      for(const w of bp.slice(0,12)){bonus=wsTryPlace(B,w,dirs,rnd,0.2);if(bonus)break;}
    }
    const letters=placed.map(p=>p.w).join('');
    for(let k=0;k<20;k++){
      const g=B.g.map(ch=>ch!==null?ch:(rnd()<0.5?letters[Math.floor(rnd()*letters.length)]:WS_FREQ[Math.floor(rnd()*WS_FREQ.length)]));
      if(wsBlocked(g,n))continue;
      if(placed.some(p=>wsCount(g,n,p.w)!==1))continue;
      if(bonus&&wsCount(g,n,bonus.w)!==1)continue;
      return{ti:ti,n:n,grid:g,words:placed.slice().sort((a,b)=>a.w<b.w?-1:1),bonus:bonus,msg:null};
    }
  }
  return null;
}
function wsFromEntry(e){
  const ti=e[0],n=e[1];
  return{ti:ti,n:n,grid:e[2].split(''),words:e[3].split(' ').map(t=>wsParsePlace(t,n)).sort((a,b)=>a.w<b.w?-1:1),
    bonus:e[4]?wsParsePlace(e[4],n):null,msg:e[5]||null};
}
function dayNum(){return Math.floor((Date.now()-Date.UTC(2026,0,1))/864e5);}
const WS_DAILY_SIZE=[14,8,9,10,11,12,13]; // by UTC weekday, Sunday first: Monday easiest
function wsDailySpec(day){
  const wd=new Date(Date.UTC(2026,0,1)+day*864e5).getUTCDay(),n=WS_DAILY_SIZE[wd],r=WS_WORDS_FOR[n];
  return{n:n,count:Math.round((r[0]+r[1])/2),dirs:(wd===1||wd===2)?[0,1,2,7,4,6]:WS_ALL_DIRS,ti:((day*7+3)%WS_THEMES.length+WS_THEMES.length)%WS_THEMES.length};
}
function genDaily(day){
  const s=wsDailySpec(day);
  for(let t=0;t<6;t++){const D=wsGen((day*2654435761%2147483647)+1+t*7919,(s.ti+t)%WS_THEMES.length,s.n,s.count,s.dirs,4,Math.min(s.n,12),true);if(D)return D;}
  return null;
}

// ── state ──
let levelIndex=0,L=null,gWon=false,levelStarted=false,interstitialCounter=0,isDailyChallenge=false,isEndless=false,dailyDay=0;
let gTime=0,gHints=0,gFoundN=0,gDone=false,gMsgShown=false,gAnchor=-1,gDrag=null,gCs=32;
const boardEl=document.getElementById('board');
const wsCellsEl=document.getElementById('ws-cells'),wsCapsEl=document.getElementById('ws-caps');
let _wsCellEls=[],_wsCurCap=null;
function wsBlockedUI(){return !!document.querySelector('.overlay.show');}
function wsTutUp(){const t=document.getElementById('tutorialOverlay');return !!(t&&t.style.display==='flex');}

// ── sound + haptics (synthesized; no audio files) ──
const WS_PENTA=[523.25,587.33,659.25,783.99,880,1046.5,1174.66,1318.51,1567.98];
function wsTone(freq,dur,vol,type,delay){if(!save.soundEnabled)return;try{const a=getAudio(),t=a.currentTime+(delay||0),o=a.createOscillator(),g=a.createGain();o.type=type||'triangle';o.frequency.setValueAtTime(freq,t);g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(vol,t+0.008);g.gain.exponentialRampToValueAtTime(0.0001,t+dur);o.connect(g).connect(a.destination);o.start(t);o.stop(t+dur+0.02);}catch(e){}}
let _wsTickT=0;
function wsSfxTick(k){const now=Date.now();if(now-_wsTickT<35)return;_wsTickT=now;wsTone(900+k*55,0.03,0.018,'sine');}
function wsSfxFound(len){for(let k=0;k<Math.min(len,6);k++)wsTone(WS_PENTA[(k*2)%9],0.2,0.06,'triangle',k*0.055);}
function wsSfxMiss(){wsTone(220,0.12,0.05,'sine');wsTone(165,0.16,0.04,'sine',0.06);}
function wsSfxBonus(){wsTone(1318.51,0.18,0.05,'sine');wsTone(1567.98,0.26,0.05,'sine',0.09);wsTone(2093,0.3,0.03,'sine',0.18);}
function wsSfxHint(){wsTone(1046.5,0.25,0.05,'sine');wsTone(1318.51,0.3,0.035,'sine',0.12);}
function wsBuzz(p){if(save.hapticsEnabled===false)return;try{if(navigator.vibrate)navigator.vibrate(p);}catch(e){}}

// ── board build + layout ──
function wsBuild(){
  const n=L.n;
  wsCellsEl.innerHTML='';wsCapsEl.innerHTML='';_wsCurCap=null;
  wsCellsEl.style.gridTemplateColumns='repeat('+n+',1fr)';wsCellsEl.style.gridTemplateRows='repeat('+n+',1fr)';
  _wsCellEls=[];
  for(let i=0;i<n*n;i++){const d=document.createElement('div');d.className='ws-cell';d.textContent=L.grid[i];d.dataset.i=i;wsCellsEl.appendChild(d);_wsCellEls.push(d);}
  boardEl.classList.toggle('ws-grid-lines',n<=9);
  wsRenderWords();wsLayout();
}
function wsLayout(){
  if(!L)return;
  const wrap=document.getElementById('ws-wrap');if(!wrap)return;
  const w=wrap.clientWidth,h=wrap.clientHeight;
  const size=Math.max(150,Math.min(w,h,760));
  gCs=Math.floor(size/L.n);
  boardEl.style.width=boardEl.style.height=(gCs*L.n)+'px';
  boardEl.style.setProperty('--cs',gCs+'px');
  wsDrawCaps();
}
window.addEventListener('resize',()=>{if(L)wsLayout();});
function wsCapStyle(el,a,b,thick){
  const n=L.n,ax=(a%n+0.5)*gCs,ay=(Math.floor(a/n)+0.5)*gCs,bx=(b%n+0.5)*gCs,by=(Math.floor(b/n)+0.5)*gCs;
  const len=Math.hypot(bx-ax,by-ay),t=gCs*(thick||0.8);
  el.style.width=(len+t)+'px';el.style.height=t+'px';
  el.style.left=(ax-t/2)+'px';el.style.top=(ay-t/2)+'px';
  el.style.transformOrigin=(t/2)+'px 50%';
  el.style.transform='rotate('+Math.atan2(by-ay,bx-ax)+'rad)';
}
function wsDrawCaps(){
  wsCapsEl.querySelectorAll('.ws-cap.done').forEach(e=>e.remove());
  L.words.forEach(w=>{if(!w.found)return;const el=document.createElement('div');el.className='ws-cap done';el.style.background='var(--'+w.col+')';wsCapStyle(el,w.cells[0],w.cells[w.cells.length-1]);wsCapsEl.appendChild(el);w._el=el;});
  if(L.bonus&&L.bonus.found){const el=document.createElement('div');el.className='ws-cap done bonus';wsCapStyle(el,L.bonus.cells[0],L.bonus.cells[L.bonus.cells.length-1],0.86);wsCapsEl.appendChild(el);}
}
function wsRenderWords(){
  const box=document.getElementById('ws-words');if(!box||!L)return;
  box.innerHTML='';
  L.words.forEach((w,i)=>{
    const s=document.createElement('span');
    s.className='ws-word'+(w.found?' found':'')+(w.hinted?' hinted':'');
    if(w.found){s.style.setProperty('--wc','var(--'+w.col+')');if(save.wsHideFound)s.style.display='none';}
    s.textContent=w.w;s.dataset.i=i;box.appendChild(s);
  });
  const lb=document.getElementById('ws-list-lb');if(lb)lb.textContent=save.wsHideFound?'Show all':'Hide found';
}
function wsFmt(s){s=Math.max(0,Math.floor(s));const m=Math.floor(s/60),x=s%60;return m+':'+(x<10?'0':'')+x;}
function wsRenderHud(){
  if(!L)return;
  const th=WS_THEMES[L.ti]||{n:'',e:''};
  const t=document.getElementById('ws-theme');if(t)t.textContent=th.e+' '+th.n;
  const c=document.getElementById('ws-count');if(c)c.textContent=L.words.filter(w=>w.found).length+'/'+L.words.length;
  const tm=document.getElementById('ws-time');if(tm)tm.textContent=wsFmt(gTime);
  const p=document.getElementById('ws-par');if(p)p.textContent=' / '+wsFmt(L.par);
  const tc=document.getElementById('ws-time-chip');if(tc)tc.classList.toggle('over',gTime>L.par);
  const b=document.getElementById('ws-bonus'),bt=document.getElementById('ws-bonus-txt');
  if(b){b.style.display=L.bonus?'':'none';if(L.bonus){b.classList.toggle('got',!!L.bonus.found);bt.textContent=L.bonus.found?L.bonus.w+' ✓':'?'.repeat(L.bonus.w.length);}}
  wsRenderTools();
}
function wsRenderTools(){
  const hb=document.getElementById('ws-hint-badge');if(!hb)return;
  if(hasUnlimitedHints()){hb.textContent='∞';hb.className='ws-badge';}
  else if((save.hintCount|0)>0){hb.textContent=save.hintCount|0;hb.className='ws-badge';}
  else{hb.textContent='+';hb.className='ws-badge plus';}
}
function wsFloat(txt){
  const z=document.getElementById('ws-wrap');if(!z)return;
  const d=document.createElement('div');d.className='ws-toast';d.textContent=txt;z.style.position='relative';z.appendChild(d);setTimeout(()=>d.remove(),1150);
}

// ── progress slots (one per mode) so Continue restores the board ──
function wsSlotKey(){return L?(L.mode==='camp'?'c':(L.mode==='daily'?'d':'e')):null;}
function wsSlotId(){return L.mode==='camp'?L.idx:(L.mode==='daily'?L.day:L.seed);}
function wsSave(){
  if(!L||gWon)return;
  const slots=save.wsSlots&&typeof save.wsSlots==='object'?save.wsSlots:{};
  slots[wsSlotKey()]={id:wsSlotId(),f:L.words.map((w,i)=>w.found?i:-1).filter(i=>i>=0),c:L.words.map(w=>w.col||''),
    h:gHints,hl:L.words.map((w,i)=>w.hinted?i:-1).filter(i=>i>=0),b:L.bonus&&L.bonus.found?1:0,t:Math.floor(gTime),
    n:L.n,ti:L.ti,seed:L.seed||0,bon:L.bonus?1:0};
  save.wsSlots=slots;persist();
}
function wsClearSlot(){if(!L)return;const s=save.wsSlots;if(s&&s[wsSlotKey()])delete s[wsSlotKey()];}
function wsRestore(){
  const s=save.wsSlots&&save.wsSlots[wsSlotKey()];
  if(!s||s.id!==wsSlotId())return;
  (s.f||[]).forEach(i=>{if(L.words[i]){L.words[i].found=true;L.words[i].col=(s.c&&s.c[i])||('f'+(1+(gFoundN%6)));gFoundN++;}});
  (s.hl||[]).forEach(i=>{if(L.words[i])L.words[i].hinted=true;});
  gHints=s.h|0;gTime=s.t|0;
  if(L.bonus&&s.b)L.bonus.found=true;
}

// ── start a board (campaign / daily / endless) ──
function wsStart(D,o){
  L=D;L.mode=o.mode;L.idx=o.idx;L.day=o.day;L.seed=o.seed;L.par=wsPar(L.n,L.words.length);
  L.words.forEach(w=>{w.found=false;w.hinted=false;w.col='';});
  if(L.bonus)L.bonus.found=false;
  gTime=0;gHints=0;gFoundN=0;gWon=false;gDone=false;gMsgShown=false;gAnchor=-1;gDrag=null;levelStarted=true;
  if(!o.fresh)wsRestore();else wsClearSlot();
  const mb=document.getElementById('ws-msgbar');if(mb){mb.style.display='none';mb.className='ws-msgbar';}
  wsBuild();wsRenderHud();
  wsMarkHints();
  // a board restored with every word found resumes at its ending
  if(L.words.every(w=>w.found))setTimeout(wsAllFound,250);
}
function loadLevel(idx){
  idx=Math.max(0,Math.min(idx|0,CAMPAIGN.length-1));
  levelIndex=idx;isDailyChallenge=false;isEndless=false;
  wsStart(wsFromEntry(CAMPAIGN[idx]),{mode:'camp',idx:idx});
  document.getElementById('hdr-level').textContent='Level '+(idx+1);
  updateAllUI();
  save.lastLevelProgress={level:idx+1};persist(); // display-numbered for the shim's Continue label
  requestAnimationFrame(wsLayout);
  maybeShowTutorial();
}
function isLevelComplete(){return !L||gWon;}

// ── input: drag (snaps to the 8 directions) or tap first + tap last ──
function wsPt(e){const r=boardEl.getBoundingClientRect();return{x:(e.clientX-r.left)/gCs,y:(e.clientY-r.top)/gCs};}
function wsCellOf(p){const n=L.n;const c=Math.min(n-1,Math.max(0,Math.floor(p.x))),r=Math.min(n-1,Math.max(0,Math.floor(p.y)));return r*n+c;}
function wsLine(a,d,k){const n=L.n,out=[];for(let i=0;i<=k;i++)out.push((Math.floor(a/n)+WS_D[d][0]*i)*n+(a%n+WS_D[d][1]*i));return out;}
function wsMaxSteps(a,d){const n=L.n;let k=0;let r=Math.floor(a/n),c=a%n;while(true){r+=WS_D[d][0];c+=WS_D[d][1];if(r<0||c<0||r>=n||c>=n)break;k++;}return k;}
function wsSnap(a,p){
  const n=L.n,vx=p.x-(a%n+0.5),vy=p.y-(Math.floor(a/n)+0.5);
  if(Math.hypot(vx,vy)<0.45)return[a];
  const oct=Math.round(Math.atan2(vy,vx)/(Math.PI/4));const d=((oct%8)+8)%8;
  const dr=WS_D[d][0],dc=WS_D[d][1];
  let k=Math.round((vx*dc+vy*dr)/((dr&&dc)?2:1));
  k=Math.max(0,Math.min(k,wsMaxSteps(a,d)));
  return wsLine(a,d,k);
}
function wsShowCur(cells){
  if(!_wsCurCap){_wsCurCap=document.createElement('div');_wsCurCap.className='ws-cap cur';wsCapsEl.appendChild(_wsCurCap);}
  wsCapStyle(_wsCurCap,cells[0],cells[cells.length-1],0.84);
}
function wsHideCur(miss){
  if(!_wsCurCap)return;const c=_wsCurCap;_wsCurCap=null;
  if(miss){c.className='ws-cap miss';setTimeout(()=>{c.style.opacity='0';},60);setTimeout(()=>c.remove(),420);}else c.remove();
}
function wsSetAnchor(i){
  if(gAnchor>=0&&_wsCellEls[gAnchor])_wsCellEls[gAnchor].classList.remove('anchor');
  gAnchor=i;if(i>=0&&_wsCellEls[i])_wsCellEls[i].classList.add('anchor');
}
boardEl.addEventListener('pointerdown',e=>{
  if(!L||gWon||gDone||wsBlockedUI())return;
  e.preventDefault();
  try{boardEl.setPointerCapture(e.pointerId);}catch(_){}
  const a=wsCellOf(wsPt(e));
  gDrag={a:a,sel:[a],moved:false,id:e.pointerId};
  wsShowCur([a]);wsSfxTick(0);
});
boardEl.addEventListener('pointermove',e=>{
  if(!gDrag||e.pointerId!==gDrag.id)return;
  const sel=wsSnap(gDrag.a,wsPt(e));
  if(sel.length!==gDrag.sel.length||sel[sel.length-1]!==gDrag.sel[gDrag.sel.length-1]){
    gDrag.sel=sel;if(sel.length>1)gDrag.moved=true;wsShowCur(sel);wsSfxTick(sel.length);
  }
});
function wsEndDrag(e){
  if(!gDrag||(e&&e.pointerId!==gDrag.id))return;
  const g=gDrag;gDrag=null;
  if(g.sel.length>1){wsSetAnchor(-1);wsCheck(g.sel);return;}
  // a tap: first tap anchors, second tap on the same line selects
  wsHideCur(false);
  const i=g.a;
  if(gAnchor<0){wsSetAnchor(i);return;}
  if(gAnchor===i){wsSetAnchor(-1);return;}
  const n=L.n,ar=Math.floor(gAnchor/n),ac=gAnchor%n,br=Math.floor(i/n),bc=i%n,dr=br-ar,dc=bc-ac;
  if(dr===0||dc===0||Math.abs(dr)===Math.abs(dc)){
    const k=Math.max(Math.abs(dr),Math.abs(dc)),d=WS_D.findIndex(v=>v[0]===Math.sign(dr)&&v[1]===Math.sign(dc));
    const sel=wsLine(gAnchor,d,k);wsSetAnchor(-1);wsShowCur(sel);wsCheck(sel);
  }else wsSetAnchor(i);
}
boardEl.addEventListener('pointerup',wsEndDrag);
boardEl.addEventListener('pointercancel',e=>{if(gDrag&&e.pointerId===gDrag.id){gDrag=null;wsHideCur(false);}});
boardEl.addEventListener('contextmenu',e=>e.preventDefault());

function wsCheck(sel){
  const s=sel.map(i=>L.grid[i]).join(''),rs=s.split('').reverse().join('');
  const w=L.words.find(x=>!x.found&&(x.w===s||x.w===rs));
  if(w){wsHideCur(false);wsFound(w);return;}
  if(L.bonus&&!L.bonus.found&&(L.bonus.w===s||L.bonus.w===rs)){wsHideCur(false);wsBonusFound();return;}
  const again=L.words.find(x=>x.found&&(x.w===s||x.w===rs));
  wsHideCur(true);
  if(again){wsFloat('Already found');return;}
  if(sel.length>=3){wsSfxMiss();wsBuzz(8);}
}
function wsPop(cells,stagger){cells.forEach((i,k)=>{const el=_wsCellEls[i];if(!el)return;setTimeout(()=>{el.classList.remove('pop');void el.offsetWidth;el.classList.add('pop');},k*(stagger||40));});}
function wsFound(w){
  w.found=true;w.col='f'+(1+(gFoundN%6));gFoundN++;
  const el=document.createElement('div');el.className='ws-cap done draw';el.style.background='var(--'+w.col+')';
  wsCapStyle(el,w.cells[0],w.cells[w.cells.length-1]);wsCapsEl.appendChild(el);w._el=el;
  if(w.hinted)_wsCellEls[w.cells[0]]&&_wsCellEls[w.cells[0]].classList.remove('hint','hint-flash');
  wsPop(w.cells);wsSfxFound(w.w.length);wsBuzz(14);
  save.wsWords=(save.wsWords|0)+1;
  wsRenderWords();wsRenderHud();
  if(L.words.every(x=>x.found)){wsAllFound();return;}
  wsSave();
}
function wsBonusFound(){
  L.bonus.found=true;
  const el=document.createElement('div');el.className='ws-cap done bonus draw';wsCapStyle(el,L.bonus.cells[0],L.bonus.cells[L.bonus.cells.length-1],0.86);wsCapsEl.appendChild(el);
  wsPop(L.bonus.cells,60);wsSfxBonus();wsBuzz([10,40,18]);
  save.coins=(save.coins|0)+10;save.wsBonus=(save.wsBonus|0)+1;persist();
  wsFloat('🎁 Bonus word '+L.bonus.w+'! +10 🪙');
  updateAllUI();wsRenderHud();wsSave();
}
function wsBonusInfo(){
  if(!L||!L.bonus)return;
  const th=WS_THEMES[L.ti]||{n:''};
  _showMsg(L.bonus.found?('Bonus word found: '+L.bonus.w):('A hidden '+L.bonus.w.length+'-letter '+th.n+' word is not on the list. Find it for +10 coins!'));
}
function wsToggleList(){save.wsHideFound=!save.wsHideFound;persist();wsRenderWords();requestAnimationFrame(wsLayout);}

// ── ending: every word found → (hidden message) → win ──
function wsLeftover(){const used=new Set();L.words.forEach(w=>w.cells.forEach(i=>used.add(i)));const out=[];for(let i=0;i<L.n*L.n;i++)if(!used.has(i))out.push(i);return out;}
function wsAllFound(){
  if(gWon||gDone)return;
  gDone=true;wsSetAnchor(-1);wsSave(); // stays resumable until the win (message levels wait for a tap)
  if(L.msg){
    wsLeftover().forEach(i=>_wsCellEls[i]&&_wsCellEls[i].classList.add('left'));
    const mb=document.getElementById('ws-msgbar');
    if(mb){mb.style.display='';mb.className='ws-msgbar';mb.textContent='✨ The '+wsLeftover().length+' leftover letters hide a message — tap to reveal';}
    wsTone(784,0.25,0.05,'sine');wsTone(1046.5,0.3,0.04,'sine',0.12);
    requestAnimationFrame(wsLayout);
    return;
  }
  setTimeout(winLevel,450);
}
function wsRevealMessage(){
  if(!L||!L.msg||!gDone||gMsgShown||gWon)return;
  gMsgShown=true;
  const left=wsLeftover(),mb=document.getElementById('ws-msgbar'),msg=L.msg;
  let shown='',li=0;const step=Math.max(40,Math.min(110,1600/left.length));
  mb.className='ws-msgbar done';mb.textContent='';
  for(let k=0;k<msg.length;k++){
    const ch=msg[k];
    if(ch===' '){shown+=' ';continue;}
    const cell=left[li++],snapshot=shown+ch,delay=li*step;shown=snapshot;
    setTimeout(()=>{if(_wsCellEls[cell]){_wsCellEls[cell].classList.remove('left');_wsCellEls[cell].classList.add('lit');}mb.textContent=snapshot;wsTone(WS_PENTA[li%9]||880,0.08,0.025,'sine');},delay);
  }
  save.wsMsgs=(save.wsMsgs|0)+1;persist();
  setTimeout(()=>{mb.textContent='“'+msg+'”';winLevel();},li*step+700);
}
function winLevel(){
  if(gWon)return;
  gWon=true;levelStarted=false;
  playComplete();wsBuzz([20,40,20,40,60]);
  const fast=gTime<=L.par,clean=gHints===0;
  const stars=1+(fast?1:0)+(clean?1:0);
  let _wasNew=false;
  if(isDailyChallenge){
    const today=new Date().toISOString().split('T')[0];
    if(save.dailyChallengeDate!==today){
      // A missed day restarts the streak (it used to only ever grow).
      var yesterday=new Date(Date.now()-86400000).toISOString().split('T')[0];
      save.dailyChallengeStreak=(save.dailyChallengeDate===yesterday)?(save.dailyChallengeStreak||0)+1:1;
      save.dailyChallengeDate=today;
      save.coins+=10*Math.min(save.dailyChallengeStreak,7);
      persist();
      if(window.gOnDailyDone){try{window.gOnDailyDone();}catch(e){}}
    }
  }else if(!isEndless){
    _wasNew=!save.completedLevels.includes(levelIndex);
    if(_wasNew)save.completedLevels.push(levelIndex);
    const prev=save.levelStars[levelIndex]||0;
    if(stars>prev)save.levelStars[levelIndex]=stars;
    if(save.currentLevel<=levelIndex)save.currentLevel=Math.min(levelIndex+1,CAMPAIGN.length-1);
  }
  const bt=save.wsBestTime&&typeof save.wsBestTime==='object'?save.wsBestTime:{};
  const newBest=!bt[L.n]||gTime<bt[L.n];if(newBest)bt[L.n]=Math.max(1,Math.floor(gTime));save.wsBestTime=bt;
  save.wsSolved=(save.wsSolved|0)+1;if(stars===3)save.wsPerfect=(save.wsPerfect|0)+1;
  wsClearSlot();
  save.coins+=stars*5;
  save.lastLevelProgress=null;
  persist();
  try{if(window.gGame)window.gGame.clear(isDailyChallenge?{daily:true,stars:stars,isNew:true,coins:stars*5}:{level:levelIndex+1,stars:stars,isNew:!!_wasNew,perfect:stars===3,endless:!!isEndless,coins:stars*5});}catch(e){}
  interstitialCounter++;
  if(interstitialCounter%3===0&&interstitialCounter>3)safeShowInterstitial();
  // celebration: every found highlight pops in a wave
  L.words.forEach((w,k)=>setTimeout(()=>wsPop(w.cells,25),k*70));
  const th=WS_THEMES[L.ti]||{n:''};
  const ov=document.getElementById('overlay-complete');
  const h2=ov.querySelector('h2');if(h2)h2.textContent=isDailyChallenge?'Daily grid solved! 🔎':'All words found! 🔎';
  const nb=ov.querySelector('.modal-btn.primary');
  if(nb)nb.textContent=isDailyChallenge?'Back to menu':(isEndless?'New random grid →':(levelIndex+1>=CAMPAIGN.length?'Endless grids →':'Next puzzle →'));
  document.getElementById('complete-stars').textContent='★'.repeat(stars)+'☆'.repeat(3-stars);
  let m=th.n+' · '+L.words.length+' words · '+wsFmt(gTime)+(fast?' (par '+wsFmt(L.par)+')':' (par '+wsFmt(L.par)+' — beat it for a ★)')+
    ' · '+(clean?'no hints':gHints+' hint'+(gHints>1?'s':''))+' · +'+(stars*5)+' coins';
  if(L.bonus)m+=L.bonus.found?' · 🎁 bonus '+L.bonus.w:' · missed bonus: '+L.bonus.w;
  document.getElementById('complete-msg').textContent=m;
  let rm=ov.querySelector('.ws-reveal-msg');
  if(L.msg){if(!rm){rm=document.createElement('p');rm.className='ws-reveal-msg';const sd=document.getElementById('complete-stars');sd.parentNode.insertBefore(rm,sd.nextSibling);}rm.textContent='✨ “'+L.msg+'”';rm.style.display='';}
  else if(rm)rm.style.display='none';
  ov.dataset.share=shareString(stars);
  setTimeout(()=>showOverlay('overlay-complete'),L.msg?900:700);
  updateAllUI();
}
function shareString(stars){
  const tail=' — '+((WS_THEMES[L.ti]||{n:''}).n)+' · '+L.words.length+' words · '+wsFmt(gTime)+' · '+'⭐'.repeat(stars||1);
  if(isDailyChallenge)return 'Word Search Daily #'+dailyDay+tail;
  if(isEndless)return 'Word Search Endless'+tail;
  return 'Word Search level '+(levelIndex+1)+tail;
}
function shareResult(){
  const ov=document.getElementById('overlay-complete');
  const txt=(ov&&ov.dataset.share)||shareString(1);
  if(window.Android&&window.Android.shareText){try{window.Android.shareText(txt);return;}catch(e){}}
  try{navigator.clipboard.writeText(txt);_showMsg('Copied!');}catch(e){}
}
function nextLevel(){
  hideOverlay('overlay-complete');
  if(isEndless){launchEndless(true);return;}
  if(isDailyChallenge){goMenu();return;}
  const next=levelIndex+1;
  if(next>=CAMPAIGN.length){launchEndless(true);return;}
  loadLevel(next);showScreen('game');requestAnimationFrame(wsLayout);
}
function replayLevel(){
  hideOverlay('overlay-complete');
  if(isDailyChallenge){launchDailyLevel(true);return;}
  if(isEndless&&L){wsStartEndless(L.seed,L.n,L.ti,!!L.bonus,true);return;}
  showScreen('game');loadLevel(levelIndex);
}
function skipLevel(){
  if(isDailyChallenge||isEndless)return;
  const next=levelIndex+1;
  if(next<CAMPAIGN.length){loadLevel(next);showScreen('game');}
}
function undoMove(){/* word search has nothing to undo — a found word stays found */}
function resetLevel(){if(!L||gWon)return;showOverlay('overlay-ws-restart');}
function wsDoRestart(){
  hideOverlay('overlay-ws-restart');if(!L)return;
  const h=gHints;
  L.words.forEach(w=>{w.found=false;w.col='';});if(L.bonus)L.bonus.found=false;
  gTime=0;gFoundN=0;gDone=false;gMsgShown=false;gWon=false;gHints=h;
  const mb=document.getElementById('ws-msgbar');if(mb)mb.style.display='none';
  wsBuild();wsRenderHud();wsMarkHints();wsSave();
}

// ── hint: flashes the FIRST LETTER of a word still to find ──
let _wsHintT=null;
function wsHintTarget(){if(!L||gWon||gDone)return null;return L.words.find(w=>!w.found&&!w.hinted)||null;}
function wsMarkHints(){if(!L)return;L.words.forEach(w=>{const el=_wsCellEls[w.cells[0]];if(el&&w.hinted&&!w.found)el.classList.add('hint');});}
function giveHint(){
  const w=wsHintTarget();
  if(!w){_showMsg(L&&!gDone?'Every remaining word already has its first letter marked.':'Nothing left to hint.');return;}
  try{if(window.gGame)window.gGame.emit('hint');}catch(e){}
  w.hinted=true;gHints++;
  const el=_wsCellEls[w.cells[0]];
  if(el){el.classList.add('hint');el.classList.remove('hint-flash');void el.offsetWidth;el.classList.add('hint-flash');clearTimeout(_wsHintT);_wsHintT=setTimeout(()=>el.classList.remove('hint-flash'),3100);}
  wsSfxHint();wsBuzz(10);
  wsRenderWords();wsRenderHud();wsSave();
  _showMsg('💡 '+w.w+' starts at the glowing letter');
}
function useHint(){
  if(!L||gWon)return;
  if(!wsHintTarget()){_showMsg(gDone?'All words found!':'Every remaining word already has its first letter marked.');return;}
  if(hasUnlimitedHints()){giveHint();return;}
  if(save.hintCount>0){save.hintCount--;persist();updateAllUI();giveHint();return;}
  showOverlay('overlay-hint');
}
function hasUnlimitedHints(){return (typeof isPremium==='function'&&isPremium())||(save.seasonPassUntil&&Date.now()<save.seasonPassUntil)||(save.weeklyPassUntil&&Date.now()<save.weeklyPassUntil);}
function watchAdForHint(){hideOverlay('overlay-hint');requestRewardedAd('hint');}
function spendCoinsHint(){
  if(save.coins<25){_showMsg('Not enough coins!');return;}
  if(!wsHintTarget()){hideOverlay('overlay-hint');return;}
  save.coins-=25;persist();updateAllUI();hideOverlay('overlay-hint');giveHint();
}

// ── ENDLESS: fresh on-device grids (10×10–13×13, all 8 directions), one ❤ each ──
function wsStartEndless(seed,n,ti,bonus,fresh){
  const r=WS_WORDS_FOR[n];
  const D=wsGen(seed,ti,n,Math.round((r[0]+r[1])/2),WS_ALL_DIRS,4,Math.min(n,12),bonus);
  if(!D){_showMsg('Could not build a grid — try again');return false;}
  isEndless=true;isDailyChallenge=false;
  showScreen('game');
  wsStart(D,{mode:'endless',seed:seed,fresh:fresh});
  document.getElementById('hdr-level').textContent='Endless';
  updateAllUI();requestAnimationFrame(wsLayout);
  wsSave();
  return true;
}
function launchEndless(fresh){
  const s=save.wsSlots&&save.wsSlots.e;
  if(!fresh&&s&&s.seed&&s.n){wsStartEndless(s.seed,s.n,s.ti|0,!!s.bon,false);_showMsg('Resumed your Endless grid');return;}
  if(typeof spendLife==='function'&&!spendLife())return;
  const seed=(Math.floor(Math.random()*2147483646)+1)>>>0,rnd=mulberry32(seed);
  const n=10+Math.floor(rnd()*4),ti=Math.floor(rnd()*WS_THEMES.length);
  wsStartEndless(seed,n,ti,rnd()<0.6,true);
}
// ── daily: same themed grid for everyone that day; grows Monday → Sunday ──
function startDailyChallenge(){
  const today=new Date().toISOString().split('T')[0];
  if(save.dailyChallengeDate===today){_showMsg('Today’s grid is solved — streak '+save.dailyChallengeStreak+'. A new one arrives tomorrow!');return;}
  launchDailyLevel();
}
function launchDailyLevel(fresh){
  dailyDay=dayNum();
  const D=genDaily(dailyDay);
  if(!D){_showMsg('Daily failed to build');return;}
  isDailyChallenge=true;isEndless=false;
  showScreen('game');
  wsStart(D,{mode:'daily',day:dailyDay,fresh:!!fresh});
  const dt=new Date(Date.UTC(2026,0,1)+dailyDay*864e5);
  document.getElementById('hdr-level').textContent='Daily · '+dt.toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'});
  updateAllUI();requestAnimationFrame(wsLayout);
}
// Finished the whole campaign → Play opens Endless instead of replaying 500.
(function(){
  const base=startGame;
  startGame=function(){
    if(save.completedLevels&&save.completedLevels.length>=CAMPAIGN.length){launchEndless();return;}
    return base.apply(this,arguments);
  };
})();
// keep the hint badge in sync with purchases / rewards
(function(){const base=updateAllUI;updateAllUI=function(){const r=base.apply(this,arguments);try{wsRenderTools();}catch(e){}return r;};})();

// ── timer (pauses off-screen, hidden, under overlays and the coachmark) ──
setInterval(function(){
  if(!L||gWon||gDone||document.hidden)return;
  const scr=document.getElementById('screen-game');if(!scr||!scr.classList.contains('active'))return;
  if(wsBlockedUI()||wsTutUp())return;
  gTime+=1;wsRenderHud();if(gTime%5===0)wsSave();
},1000);
document.addEventListener('visibilitychange',()=>{if(document.hidden&&L&&!gWon)wsSave();});
// re-measure when the game screen opens (the board is sized to the free space)
(function(){const base=showScreen;showScreen=function(name){const r=base.apply(this,arguments);if(name==='game')requestAnimationFrame(wsLayout);return r;};})();
addEventListener('keydown',e=>{
  if(!document.getElementById('screen-game').classList.contains('active')||!L)return;
  if(e.key==='h'||e.key==='H')useHint();
});

// ── overlays + settings row (built once) ──
(function(){
  function ov(id,html){const d=document.createElement('div');d.className='overlay';d.id=id;d.innerHTML='<div class="modal">'+html+'</div>';document.body.appendChild(d);return d;}
  ov('overlay-ws-restart','<h2>Restart puzzle?</h2><p>Clears the words you found and the timer. Hint marks stay.</p><div class="modal-btns">'+
    '<button class="modal-btn primary" onclick="wsDoRestart()">↺ Restart</button>'+
    '<button class="modal-btn secondary" onclick="hideOverlay(\'overlay-ws-restart\')">Keep searching</button></div>');
  // hint sheet copy matches this game (shell default spoke of "moves" / 10 coins)
  const hs=document.querySelector('#overlay-hint p');if(hs)hs.textContent='Flashes the first letter of a word you have not found yet.';
  document.querySelectorAll('#overlay-hint .modal-btn').forEach(b=>{if(/Coins/.test(b.textContent))b.textContent='🪙 25 Coins';});
  // Vibration toggle in Settings (after Music)
  const mus=document.getElementById('toggle-music');
  if(mus&&!document.getElementById('toggle-haptics')){
    const row=document.createElement('div');row.className='settings-item';
    row.innerHTML='<span class="settings-label">📳 Vibration</span><div class="toggle'+(save.hapticsEnabled===false?'':' on')+'" id="toggle-haptics" onclick="toggleSetting(\'hapticsEnabled\',\'toggle-haptics\');if(save.hapticsEnabled)wsBuzz(20)"></div>';
    const item=mus.closest('.settings-item');item.parentNode.insertBefore(row,item.nextSibling);
  }
  if(save.hapticsEnabled===undefined){save.hapticsEnabled=true;}
  // first run: 3 free hints to learn with
  if(!save.wsInit){save.wsInit=1;save.hintCount=(save.hintCount|0)+3;persist();}
  const back=window.onBackPressed;
  window.onBackPressed=function(){const el=document.getElementById('overlay-ws-restart');if(el&&el.classList.contains('show')){hideOverlay('overlay-ws-restart');return;}return back&&back.apply(this,arguments);};
})();

// ── tutorial: 3 sequential steps, once ──
const TUT_STEPS=[
  {t:'Swipe a word',b:'Drag from a word’s first letter to its last. The highlight snaps straight across, down or diagonally.'},
  {t:'Or tap, then tap',b:'Tap a first letter, then the last one. Found words are crossed off the list under the grid.'},
  {t:'Stars, hints, bonus',b:'Beat the par time without hints for 3 ★. 💡 Hint flashes a first letter. 🎁 grids hide an extra word worth coins.'}
];
function maybeShowTutorial(){
  if(localStorage.getItem('ws_tutorialDone')||levelIndex!==0||isDailyChallenge||isEndless)return;
  let stepI=0;const ov=document.getElementById('tutorialOverlay');const card=(ov&&ov.querySelector('div'))||ov;
  function show(){
    document.getElementById('tut-title').textContent=TUT_STEPS[stepI].t;
    document.getElementById('tut-body').textContent=TUT_STEPS[stepI].b;
    document.getElementById('tut-foot').textContent='Tap to continue · '+(stepI+1)+'/3';
    ov.style.display='flex';
  }
  function advance(){
    stepI++;
    if(stepI>=TUT_STEPS.length){ov.style.display='none';localStorage.setItem('ws_tutorialDone','1');card.removeEventListener('click',advance);return;}
    show();
  }
  card.addEventListener('click',advance);
  show();
}
window.replayTutorial=function(){localStorage.removeItem('ws_tutorialDone');showScreen('game');loadLevel(0);};

// ── menu emblem: a letter grid with a highlighter sweeping a word ──
window.MENU_EMBLEM='<svg viewBox="0 0 120 120" width="120" height="120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'+
  '<rect x="6" y="6" width="108" height="108" rx="18" fill="var(--board,#fffcf8)" stroke="var(--accent,#8b3f87)" stroke-width="4"/>'+
  '<rect x="11" y="40" width="98" height="22" rx="11" fill="var(--f1,#ffcf5a)" opacity=".8"/>'+
  '<rect x="13.5" y="90.5" width="125.7" height="21" rx="10.5" fill="var(--f2,#7fd1bb)" opacity=".72" transform="rotate(-46.5 24 101)"/>'+
  '<g font-family="Poppins,sans-serif" font-weight="800" font-size="17" text-anchor="middle" fill="var(--ink,#2a1f31)">'+
  '<text x="24" y="31">K</text><text x="48" y="31">E</text><text x="72" y="31">T</text><text x="96" y="31">D</text>'+
  '<text x="24" y="57">W</text><text x="48" y="57">O</text><text x="72" y="57">R</text><text x="96" y="57">D</text>'+
  '<text x="24" y="83">F</text><text x="48" y="83">I</text><text x="72" y="83">N</text><text x="96" y="83">A</text>'+
  '<text x="24" y="107">B</text><text x="48" y="107">L</text><text x="72" y="107">U</text><text x="96" y="107">H</text></g>'+
  '</svg>';
window.MENU_MOTIF='<g fill="none" stroke="currentColor" stroke-opacity="0.13" stroke-width="2">'+
  '<rect x="22" y="70" width="120" height="34" rx="17" transform="rotate(-12 82 87)"/>'+
  '<rect x="300" y="160" width="110" height="30" rx="15" transform="rotate(35 355 175)"/>'+
  '<rect x="280" y="660" width="128" height="32" rx="16" transform="rotate(-24 344 676)"/>'+
  '<circle cx="80" cy="740" r="30"/><path d="M101 761l22 22" stroke-width="6" stroke-linecap="round"/>'+
  '<text x="40" y="470" font-size="64" font-family="sans-serif" font-weight="700" stroke-width="1.6">A</text>'+
  '<text x="352" y="430" font-size="72" font-family="sans-serif" font-weight="700" stroke-width="1.6">W</text>'+
  '<text x="190" y="836" font-size="56" font-family="sans-serif" font-weight="700" stroke-width="1.6">Q</text>'+
  '<text x="360" y="560" font-size="48" font-family="sans-serif" font-weight="700" stroke-width="1.6">S</text></g>';
