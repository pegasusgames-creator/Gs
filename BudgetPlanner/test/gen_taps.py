#!/usr/bin/env python3
"""Writes BudgetPlanner/test/screenshot_taps.json (11 real-use states: 7 phone, 2 tablet_7, 2 tablet_10).
The seed (window.shellLoadState, no reload) builds three months of envelopes, bills and goals relative to the
device clock, and defines bpSet() which sets theme/accent, loads a scenario and navigates with UI.tab / UI.go."""
import json, os

SEED = r"""(function(){
var cur=curKey(),p1=shiftKey(cur,-1),p2=shiftKey(cur,-2),dayN=today().getDate();
var E=[['rent','Rent','carry'],['groc','Groceries','reset'],['trans','Transport','reset'],['util','Utilities','reset'],['dine','Dining out','reset'],['fun','Fun','carry'],['sav','Savings','carry'],['hlth','Health','reset']];
var s={saveVersion:1,created:Date.now()-60*864e5,sessions:9,lastSeen:Date.now()-3600e3,onboarded:true,removeAds:true,pro:true,proTrialUntil:0,settings:{theme:'light',accent:'ocean',lang:'',textSize:1,haptics:true,reduceMotion:false,daily:{on:false,h:20,m:0}},ads:{last:0,breaks:0},tool:TOOL.defaults()};
var T=s.tool;T.cc='USD';
T.envs=E.map(function(e,i){return {id:e[0],name:e[1],roll:e[2],color:i};});
function M(k,inc,plan,sp,cap){var m={income:inc.map(function(x,i){return {id:'in'+k+i,name:x[0],c:Math.round(x[1]*100)};}),plan:{},spend:[],moves:[]};
 E.forEach(function(e,i){m.plan[e[0]]=plan[i]*100;});
 sp.forEach(function(x,i){var d=Math.min(x[2],cap||28);m.spend.push({id:'sp'+k+i,e:x[0],c:Math.round(x[1]*100),d:k+'-'+String(Math.max(1,d)).padStart(2,'0'),note:x[3]||''});});
 if(!cap){E.forEach(function(e,i){if(e[2]==='reset'){var sp0=0;m.spend.forEach(function(x){if(x.e===e[0])sp0+=x.c;});var rem=plan[i]*100-sp0;if(rem>0)m.spend.push({id:'adj'+k+i,e:e[0],c:rem,d:k+'-27',note:'Other'});}});}
 T.months[k]=m;}
M(p2,[['Paycheck',3000]],[1250,500,180,210,150,140,400,170],[['rent',1250,1],['groc',212.4,3],['groc',188.9,10],['groc',96.3,19],['trans',64,8],['trans',52,20],['util',204.5,15],['dine',71.2,12],['dine',58.4,24],['fun',60,14],['hlth',44,9]]);
M(p1,[['Paycheck',3000],['Freelance',280]],[1250,520,200,220,160,150,500,280],[['rent',1250,1],['groc',201.7,2],['groc',174.2,9],['groc',122.7,23],['trans',88,6],['trans',44.5,18],['util',216.3,16],['dine',86.1,11],['dine',64.2,25],['fun',88,13],['hlth',212,20]]);
M(cur,[['Paycheck',3000],['Freelance',350]],[1250,540,190,230,180,140,520,300],[['rent',1250,1,'November rent'],['groc',212.4,2,'Weekly shop'],['groc',96.15,3],['groc',58.7,4],['trans',62,2],['trans',41.5,4],['util',118.2,3],['dine',96.5,2,'Birthday dinner'],['dine',60,4],['fun',45,3,'Cinema'],['fun',22.99,4],['hlth',79,3,'Pharmacy']],dayN);
T.months[cur].moves=[];window.bpBaseSav=null;
T.bills=[['rent','Rent',1250,1,'rent',1,true],['phone','Phone plan',45.5,12,'util',1,true],['net','Internet',39.99,18,'util',1,false],['elec','Electricity',118.2,22,'util',1,false],['gym','Gym',29,27,'hlth',3,false]].map(function(b,i){var o={id:'b'+b[0],name:b[1],c:Math.round(b[2]*100),day:b[3],env:b[4],lead:b[5],paid:{},slot:i+1};if(b[6])o.paid[cur]='x';return o;});
T.goals=[['Emergency fund',500000,185000,shiftKey(cur,8)],['Summer trip',180000,62000,shiftKey(cur,4)],['New laptop',140000,90000,shiftKey(cur,2)]].map(function(g,i){return {id:'g'+i,name:g[0],target:g[1],saved:g[2],due:g[3]};});
window.bpSeed=T;
window.bpSet=function(o){UI.closeAll();S.settings.theme=o.theme||'light';S.settings.accent=o.accent||'ocean';S.settings.lang='';TD.m=cur;
 var mm=S.tool.months[cur];if(window.bpBaseSav==null){window.bpBaseSav=mm.plan.sav;}mm.plan.sav=o.left?Math.max(0,window.bpBaseSav-52000):window.bpBaseSav;mm.spend=mm.spend.filter(function(x){return x.id!=='spx';});if(o.over)mm.spend.push({id:'spx',e:'dine',c:4000,d:cur+'-'+String(Math.min(4,dayN)).padStart(2,'0'),note:'Concert tickets'});
 persist();applyLang();applyTheme();UI.buildNav();UI.tab(o.tab||'plan');if(o.go==='env')UI.go('env',{id:o.id});
 setTimeout(function(){var v=document.getElementById('view');if(!v||!o.scroll)return;var e=document.querySelector(o.scroll);if(e)v.scrollTop+=e.getBoundingClientRect().top-v.getBoundingClientRect().top-10;},500);return 'ok';};
return window.shellLoadState(s);})();"""


def step(o):
    return [["js", "bpSet(%s);'ok';" % json.dumps(o), 1600]]


D = {
    "_comment": "BudgetPlanner (utility shell) screenshot capture - real-use budgeting states, never Settings/paywall/onboarding. _setup_taps seeds three months of envelopes, income, spending, bills and savings goals plus Pro + ad-free through window.shellLoadState (no reload) and defines bpSet(), which sets theme/accent, loads a scenario and navigates with UI.tab/UI.go. Phone 7 + tablet_7 2 + tablet_10 2 = 11 distinct states; headlines in metadata/screenshot_headlines*.json describe exactly these screens.",
    "_readiness_expr": "typeof UI !== 'undefined' && typeof window.shellLoadState === 'function' && typeof TOOL !== 'undefined' && typeof BE !== 'undefined'",
    "_setup_taps": [["js", SEED, 1500]],
    "01_left_to_assign_zero": step({"tab": "plan", "theme": "light", "accent": "ocean"}),
    "02_envelopes": step({"tab": "plan", "theme": "light", "accent": "teal", "scroll": ".bper"}),
    "03_overspend_detail": step({"go": "env", "id": "dine", "over": True, "theme": "dark", "accent": "ocean"}),
    "04_bills_due": step({"tab": "bills", "theme": "light", "accent": "plum"}),
    "05_savings_goals": step({"tab": "goals", "theme": "light", "accent": "amber"}),
    "06_month_compare": step({"tab": "months", "theme": "light", "accent": "rose"}),
    "07_money_left": step({"tab": "plan", "left": True, "theme": "dark", "accent": "teal"}),
    "tablet_7_01_plan": step({"tab": "plan", "theme": "light", "accent": "ocean", "scroll": ".bper"}),
    "tablet_7_02_goals": step({"tab": "goals", "theme": "dark", "accent": "plum"}),
    "tablet_10_01_envelope": step({"go": "env", "id": "groc", "theme": "light", "accent": "amber"}),
    "tablet_10_02_months": step({"tab": "months", "theme": "light", "accent": "teal"}),
}
if __name__ == "__main__":
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_taps.json")
    open(p, "w", encoding="utf8").write(json.dumps(D, indent=1, ensure_ascii=False) + "\n")
    print("wrote", p)
