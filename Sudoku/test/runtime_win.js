(()=>{ localStorage.setItem('sd_tutorialDone','1'); loadLevel(0); for(let i=0;i<81;i++){ if(!L.puz[i]&&gVals[i]!==L.sol[i]){ sdSelect(i); sdInput(L.sol[i]); } } return gWon; })()
