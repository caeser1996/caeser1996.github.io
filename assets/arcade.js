/* Orbital Ops: defend production from incoming incidents.
   Plain canvas, no dependencies. Performance notes:
   - fixed-size object pools with swap-remove, so the frame loop allocates nothing
   - glow is pre-rendered once per colour into sprites (no per-frame shadowBlur)
   - background gradients are painted once per resize into an offscreen canvas
   - bullet/foe collisions use a uniform spatial hash and squared distances
   - frame time is sampled and quality (pixel ratio, particles) adapts on slow devices
   - the loop only runs while the game is on screen and the tab is visible */
(function(){
  var stage=document.getElementById('arcStage');if(!stage)return;
  var cv=stage.querySelector('canvas'),cx=cv.getContext('2d',{alpha:false});
  var ui={score:document.getElementById('arcScore'),best:document.getElementById('arcBest'),wave:document.getElementById('arcWave'),
    mult:document.getElementById('arcMult'),budget:document.getElementById('arcBudget'),screen:document.getElementById('arcScreen'),
    pause:document.getElementById('arcPause')};
  var RM=matchMedia('(prefers-reduced-motion: reduce)').matches,COARSE=matchMedia('(pointer:coarse)').matches;
  var MONO='"IBM Plex Mono",monospace',TAU=Math.PI*2;
  function track(n,p){try{if(window.gtag)gtag('event',n,p||{});}catch(e){}}
  function sfx(n){try{if(window.SiteSound)SiteSound.sfx(n);}catch(e){}}
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){return null;}}

  // incident catalogue: what you shoot, and where to read how to handle it for real
  var TYPES={
    latency:{name:'Latency spike',hp:1,r:13,sp:1.7,pts:100,col:'#ffcf5a',read:['/insights/slos-error-budgets-small-teams/','SLOs and error budgets']},
    leak:{name:'Memory leak',hp:3,r:16,sp:.8,pts:150,col:'#b48cff',grow:1,read:['/insights/kubernetes-in-place-pod-resize/','In-place pod resize']},
    drift:{name:'Schema drift',hp:2,r:15,sp:1.1,pts:150,col:'#5ae0ff',zig:1,read:['/insights/data-contracts-playbook/','Data contracts']},
    ddos:{name:'Traffic flood',hp:2,r:18,sp:1,pts:120,col:'#ff7a59',split:1,read:['/insights/kubernetes-inference-gateway/','Inference gateways']},
    shard:{name:'Flood fragment',hp:1,r:8,sp:1.9,pts:40,col:'#ff9f80',read:['/insights/kubernetes-inference-gateway/','Inference gateways']},
    inject:{name:'Prompt injection',hp:2,r:14,sp:1.2,pts:200,col:'#ff4f8b',home:1,read:['/insights/prompt-injection-defence-for-agents/','Prompt injection defence']},
    mono:{name:'Legacy monolith',hp:40,r:46,sp:.35,pts:2500,col:'#e08a63',boss:1,read:['/insights/architecture-decision-records-fractional-cto/','Architecture decision records']}
  };
  Object.keys(TYPES).forEach(function(k){TYPES[k].label=TYPES[k].name.toUpperCase();});
  var POWERS=[['autoscale','Autoscale','#7dffb0'],['observe','Observability','#5ae0ff'],['breaker','Circuit breaker','#ffcf5a'],['rollback','Rollback','#ff7ab6']];
  var RANKS=[[0,'Intern on call'],[3000,'Site reliability engineer'],[9000,'Staff engineer'],[18000,'Principal engineer'],[30000,'Fractional CTO']];

  // ---- pools: preallocated arrays of objects, live count n, removal by swapping with the last live item
  function Pool(size,make){this.a=[];this.n=0;for(var i=0;i<size;i++)this.a.push(make());}
  Pool.prototype.get=function(){return this.n<this.a.length?this.a[this.n++]:null;};
  Pool.prototype.kill=function(i){var a=this.a,t=a[i];a[i]=a[--this.n];a[this.n]=t;};
  Pool.prototype.clear=function(){this.n=0;};
  var bullets=new Pool(160,function(){return {x:0,y:0,vx:0,vy:0};}),
      ebs=new Pool(120,function(){return {x:0,y:0,vx:0,vy:0};}),
      parts=new Pool(900,function(){return {x:0,y:0,vx:0,vy:0,life:0,col:''};}),
      foes=new Pool(90,function(){return {k:'',t:null,x:0,y:0,r:0,hp:0,max:0,vx:0,vy:0,a:0,spin:0,ph:0,fire:0,pts:new Float32Array(10),np:0,alive:0};}),
      drops=new Pool(12,function(){return {x:0,y:0,a:0,p:null};}),
      texts=new Pool(40,function(){return {x:0,y:0,s:'',life:0,big:0};});

  // ---- glow sprites: one radial gradient per colour, drawn with additive blending instead of shadowBlur
  var glowCache={};
  function glow(col){var c=glowCache[col];if(c)return c;c=document.createElement('canvas');c.width=c.height=64;var g=c.getContext('2d'),
    rg=g.createRadialGradient(32,32,0,32,32,32);rg.addColorStop(0,col+'aa');rg.addColorStop(.35,col+'44');rg.addColorStop(1,col+'00');
    g.fillStyle=rg;g.fillRect(0,0,64,64);return glowCache[col]=c;}

  var W,H,U,dpr,quality=1,bg=document.createElement('canvas'),bgx=bg.getContext('2d'),
      starX,starY,starZ,NS=0,S,keys={},ptr=null,last=0,raf=0,visible=false,best=+store('arcBest')||0,grid={},GS=64;
  ui.best.textContent=best;

  function size(){var r=stage.getBoundingClientRect();dpr=Math.min(devicePixelRatio||1,2)*quality;W=r.width;H=r.height;U=H/600;
    cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);
    // background painted once: gradient sky and two nebulae
    bg.width=cv.width;bg.height=cv.height;bgx.setTransform(dpr,0,0,dpr,0,0);
    var g=bgx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#05060f');g.addColorStop(1,'#0c0a1f');bgx.fillStyle=g;bgx.fillRect(0,0,W,H);
    [[.75,.2,.5,'rgba(120,70,255,.16)'],[.15,.8,.4,'rgba(224,138,99,.12)']].forEach(function(n){
      var rg=bgx.createRadialGradient(W*n[0],H*n[1],0,W*n[0],H*n[1],W*n[2]);rg.addColorStop(0,n[3]);rg.addColorStop(1,'rgba(0,0,0,0)');bgx.fillStyle=rg;bgx.fillRect(0,0,W,H);});
    // stars in typed arrays (struct of arrays keeps the update loop tight)
    NS=Math.min(500,Math.round(W*H/2600*quality));starX=new Float32Array(NS);starY=new Float32Array(NS);starZ=new Float32Array(NS);
    for(var i=0;i<NS;i++){starX[i]=Math.random()*W;starY[i]=Math.random()*H;starZ[i]=Math.random()*.9+.1;}
    GS=Math.max(48,64*U);
    if(S){S.p.x=Math.min(S.p.x,W-20);S.p.y=Math.min(S.p.y,H-30*U);}}
  var rz;addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(size,120);});size();

  function fresh(){[bullets,ebs,parts,foes,drops,texts].forEach(function(p){p.clear();});
    return {state:'title',score:0,wave:0,mult:1,streak:0,budget:3,t:0,shake:0,cool:0,p:{x:W/2,y:H-60*U,inv:0,tri:0,shield:0},
      slow:0,queue:[],spawnT:0,lastHit:null,shownScore:-1,shownMult:-1,shownBudget:-1};}
  S=fresh();

  function startWave(){S.wave++;var n=5+S.wave*3,q=[],pool=['latency','latency','drift'];
    if(S.wave>1)pool.push('leak','ddos');if(S.wave>2)pool.push('inject','drift');if(S.wave>4)pool.push('inject','ddos','leak');
    for(var i=0;i<n;i++)q.push(pool[Math.random()*pool.length|0]);
    if(S.wave%5===0)q.push('mono');
    S.queue=q;S.spawnT=60;text(W/2,H*.42,'Wave '+S.wave+(S.wave%5===0?' · monolith inbound':''),110,1);
    track('level_start',{level_name:'wave_'+S.wave});ui.wave.textContent=S.wave;}

  function spawn(k,x,y){var f=foes.get();if(!f)return;var t=TYPES[k],r=t.r*U;
    f.k=k;f.t=t;f.r=r;f.x=x!=null?x:r+Math.random()*(W-2*r);f.y=y!=null?y:-r;f.hp=f.max=t.hp+(t.boss?S.wave*6:0);
    f.vx=(Math.random()-.5)*.6*U;f.vy=t.sp*(1+S.wave*.06)*U;f.a=Math.random()*TAU;f.spin=(Math.random()-.5)*.04;f.ph=Math.random()*TAU;f.fire=120;
    f.np=t.boss?10:7+(Math.random()*3|0);for(var i=0;i<f.np;i++)f.pts[i]=.75+Math.random()*.35;}

  function text(x,y,s,life,big){var o=texts.get();if(!o)return;o.x=x;o.y=y;o.s=s;o.life=life;o.big=big||0;}
  function burst(x,y,col,n,spd){n=Math.ceil(n*quality*(RM?.35:1));for(var i=0;i<n;i++){var q=parts.get();if(!q)return;
    var a=Math.random()*TAU,v=(Math.random()*2.6+.4)*(spd||1)*U;q.x=x;q.y=y;q.vx=Math.cos(a)*v;q.vy=Math.sin(a)*v;q.life=30+Math.random()*30;q.col=col;}}

  function begin(){S=fresh();S.state='play';hide();startWave();track('game_start',{game:'orbital_ops'});
    try{if(window.SiteSound)SiteSound.wake();}catch(e){}}
  function over(){S.state='over';var rank=RANKS[0][1];RANKS.forEach(function(r){if(S.score>=r[0])rank=r[1];});
    var nb=S.score>best;if(nb){best=S.score;store('arcBest',best);ui.best.textContent=best;}
    track('post_score',{score:S.score,level:S.wave,character:rank});track('level_end',{level_name:'wave_'+S.wave,success:false});
    var lh=S.lastHit?TYPES[S.lastHit]:null;
    show('<div class="arc-k">Error budget exhausted</div><h3>'+S.score.toLocaleString('en-GB')+'</h3>'+
      '<p class="arc-rank">'+(nb?'New best · ':'')+'Rank: <b>'+rank+'</b> · wave '+S.wave+'</p>'+
      (lh?'<p class="arc-tip">Taken down by a <b>'+lh.name.toLowerCase()+'</b>. In production, the fix is engineering, not reflexes: <a href="'+lh.read[0]+'">'+lh.read[1]+' →</a></p>':'')+
      '<div class="arc-btns"><button type="button" class="btn" data-arc="start">Play again</button><button type="button" class="btn ghost" data-arc="share">Share score</button></div>'+
      '<p class="arc-cta">Real incidents are harder. <a href="'+(stage.getAttribute('data-cal')||'/#connect')+'" target="_blank" rel="noopener">Book a call</a> and let\'s make them rarer.</p>');
    sfx('over');}
  function show(h){ui.screen.innerHTML=h;ui.screen.hidden=false;}
  function hide(){ui.screen.hidden=true;}
  function pause(on){if(S.state!=='play'&&S.state!=='pause')return;S.state=on?'pause':'play';ui.pause.setAttribute('aria-pressed',on);
    if(on)show('<div class="arc-k">Paused</div><h3>Incident bridge on hold</h3><div class="arc-btns"><button type="button" class="btn" data-arc="resume">Resume</button></div>');else hide();}

  ui.screen.addEventListener('click',function(e){var b=e.target.closest('[data-arc]');if(!b)return;var a=b.getAttribute('data-arc');
    if(a==='start')begin();else if(a==='resume')pause(false);
    else if(a==='share'){var txt='I scored '+S.score.toLocaleString('en-GB')+' defending production in Orbital Ops. Beat it:',url=location.origin+'/play/';
      track('share',{method:navigator.share?'native':'copy',content_type:'game',item_id:'orbital_ops'});
      if(navigator.share)navigator.share({title:'Orbital Ops',text:txt,url:url}).catch(function(){});
      else if(navigator.clipboard)navigator.clipboard.writeText(txt+' '+url).then(function(){b.textContent='Copied';});}});
  ui.pause.addEventListener('click',function(){pause(S.state==='play');});

  addEventListener('keydown',function(e){if(!visible)return;var k=e.key.toLowerCase(),tag=(document.activeElement||{}).tagName;
    if(tag==='INPUT'||tag==='TEXTAREA')return;
    if(S.state==='play'&&['arrowleft','arrowright','arrowup','arrowdown',' '].indexOf(k)>-1)e.preventDefault();
    keys[k]=1;if(k==='p')pause(S.state==='play');if(k==='enter'&&(S.state==='title'||S.state==='over')&&tag!=='BUTTON'&&tag!=='A')begin();});
  addEventListener('keyup',function(e){keys[e.key.toLowerCase()]=0;});
  function pos(e){var r=cv.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};}
  cv.addEventListener('pointerdown',function(e){ptr=pos(e);try{cv.setPointerCapture(e.pointerId);}catch(_){}if(S.state==='title')begin();});
  cv.addEventListener('pointermove',function(e){if(e.pointerType==='mouse'||ptr)ptr=pos(e);});
  cv.addEventListener('pointerup',function(e){if(e.pointerType!=='mouse')ptr=null;});
  cv.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')ptr=null;});
  document.addEventListener('visibilitychange',function(){if(document.hidden)pause(true);});

  function hitPlayer(k){var p=S.p;if(p.inv>0||S.state!=='play')return;
    if(p.shield){p.shield=0;p.inv=60;burst(p.x,p.y,'#ffcf5a',24);sfx('shield');return;}
    S.budget--;S.lastHit=k;S.mult=1;S.streak=0;p.inv=110;S.shake=RM?0:14;burst(p.x,p.y,'#ff4f8b',40,1.4);sfx('hit');
    if(S.budget<=0){S.budget=0;over();}}

  function kill(i){var f=foes.a[i],t=f.t,x=f.x,y=f.y;foes.kill(i);S.streak++;
    if(S.streak%8===0&&S.mult<8){S.mult++;text(x,y-20,'×'+S.mult+' streak',60);sfx('mult');}
    var g=t.pts*S.mult;S.score+=g;text(x,y,'+'+g,45);
    burst(x,y,t.col,t.boss?90:22,t.boss?2:1);sfx(t.boss?'bigboom':'boom');if(t.boss)S.shake=RM?0:20;
    if(t.split)for(var j=0;j<3;j++)spawn('shard',x+(j-1)*14*U,y);
    if(Math.random()<(t.boss?1:.09)){var d=drops.get();if(d){d.x=x;d.y=y;d.a=0;d.p=POWERS[Math.random()*POWERS.length|0];}}}

  function power(pw){var p=S.p;sfx('power');track('game_powerup',{item_name:pw[1]});text(p.x,p.y-40*U,pw[1],70);
    if(pw[0]==='autoscale')p.tri=480;else if(pw[0]==='observe')S.slow=360;else if(pw[0]==='breaker')p.shield=1;else if(pw[0]==='rollback')S.budget=Math.min(S.budget+1,5);}

  function fire(x,y,vx,vy){var b=bullets.get();if(b){b.x=x;b.y=y;b.vx=vx;b.vy=vy;}}

  // spatial hash: bucket live foes by cell so each bullet only tests foes in its own cell neighbourhood
  function buildGrid(){for(var k in grid)grid[k].length=0;
    for(var i=0;i<foes.n;i++){var f=foes.a[i],x0=(f.x-f.r)/GS|0,x1=(f.x+f.r)/GS|0,y0=(f.y-f.r)/GS|0,y1=(f.y+f.r)/GS|0;
      for(var gx=x0;gx<=x1;gx++)for(var gy=y0;gy<=y1;gy++){var key=gx*4096+gy;(grid[key]||(grid[key]=[])).push(f);}}}

  function step(dt){var p=S.p,ts=S.slow>0?.45:1,i,j;S.t+=dt;
    var sv=(S.state==='play'?1.6:.5)*U*dt;for(i=0;i<NS;i++){starY[i]+=starZ[i]*sv;if(starY[i]>H){starY[i]=0;starX[i]=Math.random()*W;}}
    for(i=parts.n-1;i>=0;i--){var q=parts.a[i];q.x+=q.vx*dt;q.y+=q.vy*dt;q.vx*=.97;q.vy*=.97;q.life-=dt;if(q.life<=0)parts.kill(i);}
    for(i=texts.n-1;i>=0;i--){var tx=texts.a[i];tx.y-=(tx.big?0:.6)*dt;tx.life-=dt;if(tx.life<=0)texts.kill(i);}
    if(S.state!=='play')return;
    // move: keys take priority, otherwise ease towards the pointer (offset above the finger on touch)
    var sp=6*U*dt,mx=(keys.arrowright||keys.d?1:0)-(keys.arrowleft||keys.a?1:0),my=(keys.arrowdown||keys.s?1:0)-(keys.arrowup||keys.w?1:0);
    if(mx||my){p.x+=mx*sp;p.y+=my*sp;}else if(ptr){var e=1-Math.pow(.78,dt);p.x+=(ptr.x-p.x)*e;p.y+=(ptr.y-(COARSE?70*U:0)-p.y)*e;}
    p.x=Math.max(16,Math.min(W-16,p.x));p.y=Math.max(H*.45,Math.min(H-24*U,p.y));
    if(p.inv>0)p.inv-=dt;if(p.tri>0)p.tri-=dt;if(S.slow>0)S.slow-=dt;if(S.shake>0)S.shake*=Math.pow(.88,dt);
    S.cool-=dt;if(S.cool<=0){S.cool=9;var v=-11*U;fire(p.x,p.y-18*U,0,v);if(p.tri>0){fire(p.x-8,p.y-12*U,-1.6*U,v);fire(p.x+8,p.y-12*U,1.6*U,v);}sfx('laser');}
    for(i=bullets.n-1;i>=0;i--){var b=bullets.a[i];b.x+=b.vx*dt;b.y+=b.vy*dt;if(b.y<-20||b.x<-20||b.x>W+20)bullets.kill(i);}
    if(S.queue.length){S.spawnT-=dt*ts;if(S.spawnT<=0){spawn(S.queue.shift());S.spawnT=Math.max(18,70-S.wave*5)*(0.6+Math.random()*.8);}}
    else if(!foes.n){S.score+=500*S.wave;text(W/2,H*.5,'Wave cleared +'+500*S.wave,80);track('level_end',{level_name:'wave_'+S.wave,success:true});startWave();}
    // foes move
    var pr=12*U;
    for(i=foes.n-1;i>=0;i--){var f=foes.a[i],t=f.t;f.a+=f.spin*dt;f.ph+=.05*dt;f.alive=1;
      if(t.zig)f.x+=Math.sin(f.ph*2)*2.2*U*dt*ts;
      if(t.home){f.vx+=(p.x>f.x?.05:-.05)*U*dt;f.vx=Math.max(-2.4*U,Math.min(2.4*U,f.vx));}
      if(t.grow&&f.r<34*U)f.r+=.02*U*dt;
      if(t.boss){f.y=Math.min(f.y+f.vy*dt*ts,H*.22);f.x+=Math.sin(S.t*.012)*1.6*U*dt*ts;f.fire-=dt*ts;
        if(f.fire<=0){f.fire=Math.max(28,70-S.wave*3);var dx=p.x-f.x,dy=p.y-f.y,d=Math.sqrt(dx*dx+dy*dy)||1;
          for(j=-1;j<=1;j++){var o=ebs.get();if(o){o.x=f.x;o.y=f.y+f.r*.6;o.vx=(dx/d*4+j*1.2)*U;o.vy=dy/d*4*U;}}sfx('enemy');}}
      else{f.x+=f.vx*dt*ts;f.y+=f.vy*dt*ts;}
      if(f.x<f.r){f.x=f.r;f.vx=Math.abs(f.vx);}if(f.x>W-f.r){f.x=W-f.r;f.vx=-Math.abs(f.vx);}
      if(f.y>H+f.r){text(f.x,H-30*U,'escaped · streak lost',50);foes.kill(i);S.streak=0;S.mult=1;S.score=Math.max(0,S.score-25);continue;}
      var px=p.x-f.x,py=p.y-f.y,rr=f.r+pr;
      if(px*px+py*py<rr*rr){hitPlayer(f.k);if(!t.boss){burst(f.x,f.y,t.col,16);foes.kill(i);}}}
    // bullets against foes through the spatial hash
    buildGrid();
    for(i=bullets.n-1;i>=0;i--){var bl=bullets.a[i],cell=grid[(bl.x/GS|0)*4096+(bl.y/GS|0)];if(!cell)continue;
      for(j=0;j<cell.length;j++){var fo=cell[j];if(!fo.alive)continue;var ddx=bl.x-fo.x,ddy=bl.y-fo.y,rad=fo.r+3;
        if(ddx*ddx+ddy*ddy<rad*rad){bullets.kill(i);fo.hp--;burst(bl.x,bl.y,fo.t.col,3,.6);
          if(fo.hp<=0){fo.alive=0;kill(foes.a.indexOf(fo));}break;}}}
    var er=10*U;
    for(i=ebs.n-1;i>=0;i--){var eb=ebs.a[i];eb.x+=eb.vx*dt*ts;eb.y+=eb.vy*dt*ts;var ex=eb.x-p.x,ey=eb.y-p.y;
      if(ex*ex+ey*ey<er*er){ebs.kill(i);hitPlayer('mono');continue;}if(eb.y>H+10||eb.y<-10||eb.x<-10||eb.x>W+10)ebs.kill(i);}
    var dr=24*U;
    for(i=drops.n-1;i>=0;i--){var dp=drops.a[i];dp.y+=1.3*U*dt;dp.a+=.05*dt;var qx=dp.x-p.x,qy=dp.y-p.y;
      if(qx*qx+qy*qy<dr*dr){power(dp.p);drops.kill(i);}else if(dp.y>H+20)drops.kill(i);}
    if(!RM&&quality>.7){var tr=parts.get();if(tr){tr.x=p.x+(Math.random()-.5)*6;tr.y=p.y+16*U;tr.vx=(Math.random()-.5)*.4;tr.vy=2.2*U;tr.life=16;tr.col='#5ae0ff';}}
    // touch the DOM only when a value changes
    if(S.score!==S.shownScore){S.shownScore=S.score;ui.score.textContent=S.score.toLocaleString('en-GB');}
    if(S.mult!==S.shownMult){S.shownMult=S.mult;ui.mult.textContent='×'+S.mult;}
    if(S.budget!==S.shownBudget){S.shownBudget=S.budget;ui.budget.style.setProperty('--b',Math.min(1,S.budget/3));ui.budget.setAttribute('aria-label','Error budget '+S.budget+' of 3');}}

  function draw(){var i,p=S.p;cx.setTransform(1,0,0,1,0,0);cx.drawImage(bg,0,0);cx.setTransform(dpr,0,0,dpr,0,0);
    if(S.shake>.5)cx.translate((Math.random()-.5)*S.shake,(Math.random()-.5)*S.shake);
    // stars in three brightness bands to keep fillStyle changes to a minimum
    var streak=S.state==='play'?4:1.6;cx.fillStyle='#fff';
    for(var band=0;band<3;band++){cx.globalAlpha=.3+band*.3;var lo=band/3,hi=(band+1)/3;
      for(i=0;i<NS;i++){var z=starZ[i];if(z>=lo&&z<hi)cx.fillRect(starX[i],starY[i],z*1.6,z*streak);}}
    cx.globalAlpha=1;
    // scrolling horizon grid as one path
    cx.strokeStyle='rgba(90,224,255,.08)';cx.lineWidth=1;cx.beginPath();var off=(S.t*.6%18)*U;
    for(var y=H*.7;y<H;y+=18*U){cx.moveTo(0,y+off);cx.lineTo(W,y+off);}cx.stroke();
    cx.globalCompositeOperation='lighter';
    for(i=0;i<foes.n;i++){var f=foes.a[i],gs=f.r*(f.t.boss?3.4:3);cx.drawImage(glow(f.t.col),f.x-gs/2,f.y-gs/2,gs,gs);}
    for(i=0;i<drops.n;i++){var d=drops.a[i];cx.drawImage(glow(d.p[2]),d.x-22*U,d.y-22*U,44*U,44*U);}
    cx.fillStyle='#bff6ff';for(i=0;i<bullets.n;i++){var b=bullets.a[i];cx.fillRect(b.x-1.5,b.y-9*U,3,14*U);}
    for(i=0;i<parts.n;i++){var q=parts.a[i];cx.globalAlpha=q.life>30?1:q.life/30;cx.fillStyle=q.col;cx.fillRect(q.x,q.y,2.2,2.2);}
    cx.globalAlpha=1;cx.globalCompositeOperation='source-over';
    cx.textAlign='center';
    for(i=0;i<foes.n;i++){var fo=foes.a[i],t=fo.t,n=fo.np;cx.beginPath();
      for(var k=0;k<n;k++){var a=fo.a+k/n*TAU,r=fo.r*fo.pts[k];if(k)cx.lineTo(fo.x+Math.cos(a)*r,fo.y+Math.sin(a)*r);else cx.moveTo(fo.x+Math.cos(a)*r,fo.y+Math.sin(a)*r);}
      cx.closePath();cx.fillStyle='rgba(5,6,15,.55)';cx.fill();cx.strokeStyle=t.col;cx.lineWidth=t.boss?3:2;cx.stroke();
      if(t.boss){cx.beginPath();cx.arc(fo.x,fo.y,fo.r*.38,0,TAU);cx.stroke();
        var bw=fo.r*2.4;cx.fillStyle='rgba(255,255,255,.12)';cx.fillRect(fo.x-bw/2,fo.y-fo.r-16*U,bw,4);cx.fillStyle=t.col;cx.fillRect(fo.x-bw/2,fo.y-fo.r-16*U,bw*fo.hp/fo.max,4);}
      if(fo.r>11*U){cx.fillStyle=t.col;cx.font='500 '+Math.round((t.boss?12:9)*U+2)+'px '+MONO;cx.fillText(t.label,fo.x,fo.y+fo.r+12*U);}}
    for(i=0;i<drops.n;i++){var dd=drops.a[i];cx.save();cx.translate(dd.x,dd.y);cx.rotate(dd.a);cx.strokeStyle=dd.p[2];cx.lineWidth=2;cx.strokeRect(-9*U,-9*U,18*U,18*U);cx.restore();
      cx.fillStyle=dd.p[2];cx.font='600 '+Math.round(10*U+2)+'px '+MONO;cx.fillText(dd.p[1],dd.x,dd.y+24*U);}
    cx.fillStyle='#ff4f8b';cx.beginPath();for(i=0;i<ebs.n;i++){var eb=ebs.a[i];cx.moveTo(eb.x+4*U,eb.y);cx.arc(eb.x,eb.y,4*U,0,TAU);}cx.fill();
    // ship
    if(S.state!=='over'&&!(p.inv>0&&(p.inv|0)%10<5)){var s=U*1.1;cx.drawImage(glow('#5ae0ff'),p.x-30*s,p.y-30*s,60*s,60*s);
      cx.fillStyle='#e9fbff';cx.beginPath();cx.moveTo(p.x,p.y-20*s);cx.lineTo(p.x+13*s,p.y+14*s);cx.lineTo(p.x+4*s,p.y+9*s);cx.lineTo(p.x,p.y+14*s);
      cx.lineTo(p.x-4*s,p.y+9*s);cx.lineTo(p.x-13*s,p.y+14*s);cx.closePath();cx.fill();
      cx.fillStyle='#e08a63';cx.beginPath();cx.arc(p.x,p.y-2*s,3.2*s,0,TAU);cx.fill();
      if(p.shield){cx.strokeStyle='rgba(255,207,90,.8)';cx.lineWidth=2;cx.beginPath();cx.arc(p.x,p.y,26*s,0,TAU);cx.stroke();}}
    if(S.slow>0){cx.fillStyle='rgba(90,224,255,.06)';cx.fillRect(0,0,W,H);}
    for(i=0;i<texts.n;i++){var x=texts.a[i];cx.globalAlpha=x.life>30?1:x.life/30;cx.fillStyle=x.big?'#fff':'#ffe2d4';
      cx.font=x.big?'500 '+Math.round(26*U+6)+'px Newsreader,Georgia,serif':'600 '+Math.round(10*U+3)+'px '+MONO;cx.fillText(x.s,x.x,x.y);}cx.globalAlpha=1;
    if(S.state==='title'){var tt=S.t*.03;cx.strokeStyle='rgba(90,224,255,.35)';cx.lineWidth=1.5;cx.beginPath();cx.ellipse(W/2,H*.62,90*U,26*U,0,0,TAU);cx.stroke();
      cx.fillStyle='#e08a63';cx.beginPath();cx.arc(W/2+Math.cos(tt)*90*U,H*.62+Math.sin(tt)*26*U,5*U,0,TAU);cx.fill();}}

  // adaptive quality: if the average frame is slow, drop the pixel ratio and particle budget once
  var acc=0,frames=0,downgraded=false;
  function loop(now){var raw=last?(now-last)/16.667:1;last=now;var dt=Math.min(3,raw);
    if(S.state==='play'&&!downgraded){acc+=raw;if(++frames===90){if(acc/frames>1.45){downgraded=true;quality=.6;size();}acc=0;frames=0;}}
    if(S.state!=='pause')step(dt);draw();raf=requestAnimationFrame(loop);}
  function run(on){if(on&&!raf&&!document.hidden){last=0;raf=requestAnimationFrame(loop);}else if(!on&&raf){cancelAnimationFrame(raf);raf=0;}}
  new IntersectionObserver(function(es){es.forEach(function(e){visible=e.isIntersecting;run(visible);if(!visible&&S.state==='play')pause(true);});}).observe(stage);
  document.addEventListener('visibilitychange',function(){run(visible&&!document.hidden);});
  show('<div class="arc-k">Orbital Ops · v1.0</div><h3>Defend production.</h3><p>Incidents are inbound: latency spikes, memory leaks, schema drift, traffic floods and prompt injections. Every fifth wave, a legacy monolith. You have an error budget of three.</p>'+
    '<div class="arc-btns"><button type="button" class="btn" data-arc="start">Launch</button></div><p class="arc-keys">Move with the mouse, a finger, arrow keys or WASD · firing is automatic · P to pause</p>');
})();
