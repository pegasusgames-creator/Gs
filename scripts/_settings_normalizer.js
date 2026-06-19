<script>/*PART1: universal settings normalizer v3 — triggers on the RENDERED screen via MutationObserver (no dependency on a global showScreen), flattens sections, collects rows by container children (any class), reorders after any shim appends*/
(function(){
  if(window.__setNormV3) return; window.__setNormV3=1;
  function txt(e){return (e.textContent||'').toLowerCase();}
  function hdr(t){var h=document.createElement('div');h.setAttribute('data-set-group','1');h.textContent=t;h.style.cssText='font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;opacity:.55;margin:14px 6px 4px;';return h;}
  var GROUPS=[['Preferences',['sound','music','haptic','vibrat','daily remind','reminder','notification','language','theme']],
              ['Help',['tutorial','how to play','privacy']],
              ['Purchases',['restore','manage sub']]];
  function isRow(e){ if(!e||e.nodeType!==1||e.hasAttribute('data-set-group'))return false; var c=(e.className||'')+''; if(/section-title|settings-header|screen-header|set-head|topbar|app-header|modal/.test(c))return false; if(/(^|\s)header(\s|$)/.test(c))return false; var t=(e.textContent||'').trim(); if(/^[←⬅]/.test(t))return false; return true; }
  var applying=false;
  function norm(){
    var scr=document.getElementById('screen-settings')||document.getElementById('settingsScreen'); if(!scr)return;
    var cont=scr.querySelector('.settings-scroll,.settings-list');
    if(!cont){var any=scr.querySelector('.settings-item,.setting-row,.set-row'); cont=any?any.parentNode:null;}
    if(!cont)return;
    applying=true;
    try{
      [].slice.call(scr.querySelectorAll('.settings-section')).forEach(function(sec){
        [].slice.call(sec.children).forEach(function(ch){ if(isRow(ch)) cont.appendChild(ch); });
      });
      [].slice.call(scr.children).forEach(function(ch){
        if(ch!==cont && isRow(ch) && (/(restore|manage|language|notif|reminder)/i.test(txt(ch)) || (ch.querySelector&&ch.querySelector('button,select,input,.toggle')))) cont.appendChild(ch);
      });
      [].slice.call(cont.querySelectorAll('[data-set-group]')).forEach(function(h){h.remove();});
      [].slice.call(scr.querySelectorAll('.settings-section')).forEach(function(s){ if(!s.querySelector('.settings-item,.setting-row,.set-row')) s.remove(); });
      var rows=[].slice.call(cont.children).filter(isRow);
      if(rows.length<2){applying=false;return;}
      rows.forEach(function(r){r._u=false;});
      function find(kw){for(var i=0;i<rows.length;i++){if(!rows[i]._u&&txt(rows[i]).indexOf(kw)>=0){rows[i]._u=true;return rows[i];}}return null;}
      var frag=document.createDocumentFragment();
      var bucket={Preferences:[],Help:[],Purchases:[]};
      var ASSIGN=[['Preferences',['sound','music','haptic','vibrat','daily remind','reminder','notification','language','theme'],true],
                  ['Purchases',['restore','manage sub'],true],
                  ['Help',['tutorial','how to play','privacy'],false]];
      ASSIGN.forEach(function(g){g[1].forEach(function(kw){ if(g[2]){var r;while((r=find(kw)))bucket[g[0]].push(r);} else {var r=find(kw);if(r)bucket[g[0]].push(r);} });});
      ['Preferences','Help','Purchases'].forEach(function(name){ if(bucket[name].length){frag.appendChild(hdr(name)); bucket[name].forEach(function(r){frag.appendChild(r);}); } });
      var footer=null,reset=null;
      rows.forEach(function(r){ if(!r._u){ if(!reset&&/(reset|clear progress|erase)/.test(txt(r))){reset=r;r._u=true;} else if(!footer&&/(version|^about | • |com\.pegasusgames)/.test(txt(r))){footer=r;r._u=true;} } });
      rows.forEach(function(r){ if(!r._u){ if(/(restore|manage sub)/.test(txt(r))){ try{r.style.display='none';}catch(e){} r._u=true; } else { frag.appendChild(r); r._u=true; } } });
      if(footer)frag.appendChild(footer);
      if(reset){frag.appendChild(hdr('Danger Zone'));
        try{reset.style.flexDirection='row';reset.style.alignItems='center';}catch(e){}
        var b=reset.querySelector('button'); if(b){var rlbl=reset.querySelector('.settings-label,.setting-label,.settings-item-label,.set-label');if(rlbl&&!rlbl.contains(b))b.textContent='Reset';b.style.cssText='padding:12px 22px;font-size:.84rem;white-space:nowrap;background:#b8332b;color:#fff;border:none;border-radius:10px;cursor:pointer;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,0.22);';}
        frag.appendChild(reset);}
      cont.appendChild(frag);
    }catch(e){}
    applying=false;
  }
  window.normalizeSettings=norm;
  function visible(){var s=document.getElementById('screen-settings')||document.getElementById('settingsScreen'); return s&&(s.classList.contains('active')||(s.offsetParent!==null&&getComputedStyle(s).display!=='none'));}
  var t=null; function sched(){if(applying)return;clearTimeout(t);t=setTimeout(function(){if(visible())norm();},110);}
  function attach(){var s=document.getElementById('screen-settings')||document.getElementById('settingsScreen'); if(!s)return false; new MutationObserver(function(){if(!applying)sched();}).observe(s,{attributes:true,attributeFilter:['class','style'],childList:true,subtree:true}); return true;}
  if(!attach()){var iv=setInterval(function(){if(attach())clearInterval(iv);},300);}
  var o=window.showScreen; if(typeof o==='function'){window.showScreen=function(){var r=o.apply(this,arguments);sched();return r;};}
  document.addEventListener('click',sched,true);
  if(document.readyState!=='loading')sched(); else document.addEventListener('DOMContentLoaded',sched);
})();
</script>
