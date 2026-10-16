(()=>{ try{localStorage.setItem('fw_tutorialDone','1');}catch(e){}
  showScreen('game'); loadLevel(0);
  fwTutStep=-1; var tov=document.getElementById('tutorialOverlay'); if(tov) tov.style.display='none';
  fwTap();
  var r=FW.world.birdR, half=FW.gates.capW/2, guard=0;
  while(fw.state==='fly' && fw.score<12 && guard++<30000){
    var prev=fw.score>0?fwGate(fw.course,fw.score-1):null, nx=fwGate(fw.course,fw.score);
    var inPrev=prev && fw.cam<prev.x+half+r+4;
    var g=inPrev?prev:nx, ahead=inPrev?fw.cam:Math.max(fw.cam,nx.x-half-r-30);
    var bottom=Math.min(fwGateCentre(g,ahead)+g.gap/2, FW.world.floorY);
    var yNext=fw.y+Math.min(fw.vy+FW.phys.gravity*FW_DT,FW.phys.maxFall)*FW_DT*4;
    if(fw.flapT>=9 && yNext+r+10>bottom) fwTap();
    fwStep();
  }
  while(fw.state==='fly' && guard++<60000) fwStep();
  while(fw.state==='crash' && fw.crashT<40) fwStep();
  fwFinish();
  return fw.score;
})()
