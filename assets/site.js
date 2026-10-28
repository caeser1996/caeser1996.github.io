/* Shared behaviour for every page: theme, reveals, progress, contact modal, motion. */
  function esc(x){return x.replace(/&/g,'&amp;').replace(/</g,'&lt;');}
  var yr=document.getElementById('yr');if(yr)yr.textContent=new Date().getFullYear();
  var btn=document.getElementById('themeBtn');
  btn.addEventListener('click',function(){
    var cur=document.documentElement.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
    var nxt=cur==='dark'?'light':'dark';
    document.documentElement.setAttribute('data-theme',nxt);
    try{localStorage.setItem('theme',nxt);}catch(e){}
  });
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.08});
  document.querySelectorAll('.rise').forEach(function(el){io.observe(el);});


  // contact helpers
  var EMAIL_ADDR='sumantamukhopadhyaywork@gmail.com';
  function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove('on');},2600);}
  function copyText(x){
    function fb(){var ta=document.createElement('textarea');ta.value=x;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');}catch(e){}ta.remove();}
    if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(x).catch(fb);}else fb();
  }
  function openContact(subject,body){
    subject=subject||'Engagement enquiry';body=body||'Hi Sumanta,\n\n';
    var q='&su='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    document.getElementById('cmGmail').href='https://mail.google.com/mail/?view=cm&fs=1&to='+EMAIL_ADDR+q;
    document.getElementById('cmMailto').href='mailto:'+EMAIL_ADDR+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    var d=document.getElementById('contactModal');
    if(d.showModal){d.showModal();}else{location.href='mailto:'+EMAIL_ADDR;}
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest('[data-contact]');if(!a)return;e.preventDefault();openContact(a.getAttribute('data-contact'));
  });
  document.getElementById('cmCopy').addEventListener('click',function(){copyText(EMAIL_ADDR);toast('Email address copied');});
  var cm=document.getElementById('copyMail');if(cm)cm.addEventListener('click',function(){copyText(EMAIL_ADDR);toast('Email address copied');});
  document.getElementById('contactModal').addEventListener('click',function(e){if(e.target===this)this.close();});

  // scroll progress
  var pg=document.getElementById('progress');
  addEventListener('scroll',function(){var m=document.documentElement.scrollHeight-innerHeight;pg.style.transform='scaleX('+(m>0?scrollY/m:0)+')';},{passive:true});

  // progressive enhancement: smooth scroll, scroll-linked motion, magnetic buttons
  addEventListener('DOMContentLoaded',function(){
    var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(still)return;
    if(window.Lenis){
      var lenis=new Lenis({lerp:.1,smoothWheel:true});
      document.querySelectorAll('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){var id=a.getAttribute('href');if(id.length<2)return;var t=document.querySelector(id);if(!t)return;e.preventDefault();lenis.scrollTo(t,{offset:-70});});});
      if(window.gsap&&window.ScrollTrigger){lenis.on('scroll',ScrollTrigger.update);gsap.ticker.add(function(t){lenis.raf(t*1000);});gsap.ticker.lagSmoothing(0);}
      else{(function raf(t){lenis.raf(t);requestAnimationFrame(raf);})(0);}
    }
    if(window.gsap&&window.ScrollTrigger){
      gsap.registerPlugin(ScrollTrigger);
      if(document.getElementById('graph'))gsap.to('#graph',{yPercent:18,opacity:.35,ease:'none',scrollTrigger:{trigger:'.hero',start:'top top',end:'bottom top',scrub:true}});
      gsap.utils.toArray('section h2').forEach(function(h){
        gsap.fromTo(h,{clipPath:'inset(0 0 100% 0)',y:30},{clipPath:'inset(0 0 0% 0)',y:0,duration:1.1,ease:'power3.out',scrollTrigger:{trigger:h,start:'top 90%',once:true}});
      });
      gsap.utils.toArray('.practice,.dims,.langs,.engage,.inds,.ladder,.cases,.cards3').forEach(function(g){
        var kids=Array.prototype.slice.call(g.children);kids.forEach(function(k){k.classList.remove('rise');});
        gsap.fromTo(kids,{y:40,autoAlpha:0},{y:0,autoAlpha:1,duration:.9,ease:'power3.out',stagger:.08,scrollTrigger:{trigger:g,start:'top 85%',once:true}});
      });
      gsap.utils.toArray('.tier2').forEach(function(t,i){
        gsap.fromTo(t,{x:i%2?40:-40,autoAlpha:0},{x:0,autoAlpha:1,duration:.9,ease:'power3.out',scrollTrigger:{trigger:t,start:'top 90%',once:true}});
      });
      gsap.utils.toArray('.case.wide img').forEach(function(img){
        gsap.fromTo(img,{scale:1.08},{scale:1,ease:'none',scrollTrigger:{trigger:img,start:'top bottom',end:'bottom top',scrub:true}});
      });
      addEventListener('load',function(){ScrollTrigger.refresh();});
      setTimeout(function(){document.querySelectorAll('.rise').forEach(function(e){e.classList.add('in');});},6000);
      if(document.querySelector('.marquee'))gsap.to('.marquee .track',{xPercent:-8,ease:'none',scrollTrigger:{trigger:'.marquee',start:'top bottom',end:'bottom top',scrub:true}});
    }
    if(matchMedia('(pointer:fine)').matches){
      document.querySelectorAll('.mag').forEach(function(b){
        b.addEventListener('pointermove',function(e){var r=b.getBoundingClientRect(),x=(e.clientX-r.left-r.width/2)*.25,y=(e.clientY-r.top-r.height/2)*.35;b.style.transform='translate('+x+'px,'+y+'px)';});
        b.addEventListener('pointerleave',function(){b.style.transition='transform .4s cubic-bezier(.2,.7,.2,1)';b.style.transform='';setTimeout(function(){b.style.transition='';},400);});
      });
    }
  });

  // light knowledge-graph backdrop for sub-page heroes
  (function(){
    var cv=document.querySelector('.sub-graph');if(!cv)return;
    var cx=cv.getContext('2d'),dpr=Math.min(2,devicePixelRatio||1),W,H,N=[];
    var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
    function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
    function init(){var r=cv.getBoundingClientRect();W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;cx.setTransform(dpr,0,0,dpr,0,0);
      N=[];var n=Math.round(Math.min(46,Math.max(18,W*H/14000)));
      for(var i=0;i<n;i++)N.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.22,vy:(Math.random()-.5)*.22,r:Math.random()<.2?3:1.5});}
    function frame(){var ink=css('--ink'),acc=css('--accent');cx.clearRect(0,0,W,H);
      for(var i=0;i<N.length;i++){var a=N[i];if(!still){a.x+=a.vx;a.y+=a.vy;if(a.x<0||a.x>W)a.vx*=-1;if(a.y<0||a.y>H)a.vy*=-1;}
        for(var j=i+1;j<N.length;j++){var b=N[j],d=Math.hypot(a.x-b.x,a.y-b.y);if(d<130){cx.globalAlpha=(1-d/130)*.3;cx.strokeStyle=(a.r>2||b.r>2)?acc:ink;cx.lineWidth=.7;cx.beginPath();cx.moveTo(a.x,a.y);cx.lineTo(b.x,b.y);cx.stroke();}}}
      N.forEach(function(a){cx.globalAlpha=a.r>2?.9:.45;cx.fillStyle=a.r>2?acc:ink;cx.beginPath();cx.arc(a.x,a.y,a.r,0,7);cx.fill();});
      cx.globalAlpha=1;if(!still)requestAnimationFrame(frame);}
    addEventListener('resize',init);init();frame();
  })();

  // insights: topic filters
  (function(){
    var chips=document.querySelectorAll('.fchip');if(!chips.length)return;
    var posts=document.querySelectorAll('.posts .post'),count=document.querySelector('.fcount');
    chips.forEach(function(c){c.addEventListener('click',function(){
      var t=c.getAttribute('data-tag'),n=0;
      chips.forEach(function(x){x.setAttribute('aria-pressed',x===c);});
      posts.forEach(function(p){var on=!t||(' '+p.getAttribute('data-tags')+' ').indexOf(' '+t+' ')>-1;p.classList.toggle('hide',!on);if(on){n++;p.classList.add('in');}});
      if(count)count.textContent=n+(n===1?' article':' articles');
    });});
  })();

  // articles: copy link + table-of-contents highlight
  document.querySelectorAll('.copy-link').forEach(function(b){b.addEventListener('click',function(){copyText(b.getAttribute('data-url'));toast('Link copied');});});
  (function(){
    var links=document.querySelectorAll('.toc a[href^="#"]');if(!links.length||!('IntersectionObserver' in window))return;
    var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
    var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on');});var a=map[e.target.id];if(a)a.classList.add('on');}});},{rootMargin:'-20% 0px -70% 0px'});
    Object.keys(map).forEach(function(id){var h=document.getElementById(id);if(h)o.observe(h);});
  })();

  // mobile menu
  (function(){
    var b=document.getElementById('menuBtn'),n=b&&b.closest('nav');if(!b)return;
    var mq=matchMedia('(max-width:960px)'),fine=matchMedia('(hover:hover) and (pointer:fine)'),drops=[].slice.call(n.querySelectorAll('.nd')),hideT;
    function navh(){document.documentElement.style.setProperty('--navh',n.offsetHeight+'px');}
    navh();addEventListener('resize',navh);
    function set(o){n.classList.toggle('open',o);document.body.classList.toggle('menu-open',o&&mq.matches);b.setAttribute('aria-expanded',o);b.setAttribute('aria-label',o?'Close menu':'Open menu');if(!o)closeAll();}
    function openDrop(d,o){d.classList.toggle('open',o);d.querySelector('.nd-b').setAttribute('aria-expanded',o);}
    function closeAll(except){drops.forEach(function(d){if(d!==except)openDrop(d,false);});}
    b.addEventListener('click',function(){set(!n.classList.contains('open'));});
    drops.forEach(function(d){var btn=d.querySelector('.nd-b');
      btn.addEventListener('click',function(){var o=!d.classList.contains('open');if(!mq.matches)closeAll(d);openDrop(d,o);
        if(o&&!mq.matches){var f=d.querySelector('.nd-i');if(f&&btn.matches(':focus-visible'))f.focus();}});
      // hover intent on desktop pointers only
      d.addEventListener('pointerenter',function(e){if(e.pointerType!=='mouse'||mq.matches||!fine.matches)return;clearTimeout(hideT);closeAll(d);openDrop(d,true);});
      d.addEventListener('pointerleave',function(e){if(e.pointerType!=='mouse'||mq.matches)return;hideT=setTimeout(function(){openDrop(d,false);},160);});
      d.addEventListener('focusout',function(e){if(!mq.matches&&!d.contains(e.relatedTarget))openDrop(d,false);});});
    n.querySelectorAll('.nav-links a').forEach(function(a){a.addEventListener('click',function(){set(false);});});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){var o=drops.filter(function(d){return d.classList.contains('open');})[0];set(false);if(o)o.querySelector('.nd-b').focus();}});
    document.addEventListener('click',function(e){if(!n.contains(e.target))set(false);});
    mq.addEventListener&&mq.addEventListener('change',function(){set(false);});
    // mark the current section in the menu
    var path=location.pathname;n.querySelectorAll('.nd-i,.nd-l').forEach(function(a){if(a.getAttribute('href')===path)a.setAttribute('aria-current','page');});
  })();

  // analytics: anonymous interaction events for Google Analytics (no personal data is ever sent)
  (function(){
    function track(name,params){try{if(window.gtag)gtag('event',name,params||{});}catch(e){}}
    var P=location.pathname,TYPE=P==='/'?'home':P.indexOf('/insights/')===0?(P==='/insights/'?'insights_index':'insight'):P.indexOf('/case-studies/')===0?(P==='/case-studies/'?'case_studies_index':'case_study'):'service';
    function where(el){var s=el.closest('section[id],header,nav,footer,dialog,aside');return s?(s.id||s.tagName.toLowerCase()):'page';}
    function label(el){return (el.getAttribute('aria-label')||el.innerText||el.textContent||'').replace(/\s+/g,' ').trim().slice(0,80);}
    function slug(h){return h.replace(/^\/|\/$/g,'').split('/').pop()||'/';}
    var answered={};
    document.addEventListener('click',function(e){
      var el=e.target.closest('a,button,summary,[role=tab]');if(!el)return;
      var h=el.getAttribute('href')||'',base={page_type:TYPE,location:where(el),link_text:label(el)};
      if(h.indexOf('calendar.app.google')>-1)return track('book_call',base);
      if(el.id==='cmGmail')return track('contact_method',{method:'gmail',page_type:TYPE});
      if(el.id==='cmMailto')return track('contact_method',{method:'mail_app',page_type:TYPE});
      if(el.id==='cmCopy'||el.id==='copyMail')return track('contact_method',{method:'copy_email',page_type:TYPE});
      if(el.hasAttribute('data-contact'))return track('contact_open',Object.assign({subject:el.getAttribute('data-contact').slice(0,80)},base));
      if(h.indexOf('mailto:')===0)return track('contact_method',{method:'mailto_link',page_type:TYPE});
      if(el.closest('.share'))return track('share',{method:el.classList.contains('copy-link')?'copy_link':label(el).toLowerCase(),content_id:slug(P),page_type:TYPE});
      var qg=el.closest('[data-q]');if(qg&&el.dataset&&el.dataset.v){answered[qg.dataset.q]=1;track('assess_answer',{question:qg.dataset.q,answer:el.dataset.v});
        if(Object.keys(answered).length===4&&!answered._done){answered._done=1;track('assess_complete',{page_type:TYPE});}return;}
      if(el.classList.contains('fchip'))return track('filter_topic',{value:el.getAttribute('data-tag')||'all',page_type:TYPE});
      if(el.classList.contains('ucchip'))return track('filter_sector',{value:el.getAttribute('data-sector')||'all'});
      if(el.getAttribute('role')==='tab')return track('tab_view',{tab:label(el),location:where(el),page_type:TYPE});
      if(el.tagName==='SUMMARY')return track('faq_open',{question:label(el),page_type:TYPE});
      if(el.id==='themeBtn')return track('theme_toggle',{});
      if(el.id==='menuBtn')return track('menu_toggle',{});
      if(el.closest('.toc'))return track('toc_click',{section:label(el),content_id:slug(P)});
      if(h.indexOf('/case-studies/')===0&&h.length>15)return track('select_content',Object.assign({content_type:'case_study',content_id:slug(h)},base));
      if(h.indexOf('/insights/')===0&&h.length>11)return track('select_content',Object.assign({content_type:'insight',content_id:slug(h)},base));
      if(h.indexOf('#uc-')>-1||el.classList.contains('uc-more'))return track('select_content',Object.assign({content_type:'use_case',content_id:slug(h)},base));
      if(/^\/(fractional-cto|ai-architect|ontology-knowledge-graph|healthcare-data-architecture|technical-due-diligence|uae)\/$/.test(h))return track('select_content',Object.assign({content_type:'service',content_id:slug(h)},base));
      if(h==='/#assess'||h==='#assess')return track('assess_start_click',base);
      if(el.classList.contains('btn'))return track('cta_click',Object.assign({link_url:h},base));
    },true);
    // scroll depth milestones and read completion
    var marks=[25,50,75,100],hit={};
    addEventListener('scroll',function(){var m=document.documentElement.scrollHeight-innerHeight;if(m<=0)return;var pct=scrollY/m*100;
      marks.forEach(function(k){if(pct>=k-1&&!hit[k]){hit[k]=1;track('scroll_depth',{percent:k,page_type:TYPE,content_id:slug(P)});}});},{passive:true});
    var end=document.querySelector('#references,.refs,.pnav,.sub-cta');
    if(end&&'IntersectionObserver' in window&&(TYPE==='insight'||TYPE==='case_study')){
      var t0=Date.now(),o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){o.disconnect();
        track('read_complete',{content_type:TYPE,content_id:slug(P),seconds:Math.round((Date.now()-t0)/1000)});}});});o.observe(end);}
    // copying text from articles (what people find worth keeping)
    document.addEventListener('copy',function(){var s=String(getSelection()||'').trim();if(s.length>20)track('text_copy',{content_id:slug(P),page_type:TYPE,length:s.length});});
  })();

  // cookie and analytics consent banner (Google Consent Mode v2)
  (function(){
    function get(){try{return localStorage.getItem('consent');}catch(e){return null;}}
    function clearGa(){document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();
      if(n.indexOf('_ga')===0){var d=location.hostname.replace(/^www\./,'');
        ['', ';domain=.'+d, ';domain='+d].forEach(function(x){document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'+x;});}});}
    function apply(v){try{localStorage.setItem('consent',v);}catch(e){}
      try{if(window.gtag){gtag('consent','update',{analytics_storage:v});if(v==='granted')gtag('event','consent_update',{analytics:'granted'});}}catch(e){}
      if(v==='denied')clearGa();}
    var bar;
    function show(){
      if(!bar){bar=document.createElement('div');bar.className='cookie-bar';bar.setAttribute('role','dialog');bar.setAttribute('aria-live','polite');bar.setAttribute('aria-label','Cookie consent');
        bar.innerHTML='<div class="cookie-in"><p><b>Cookies and analytics.</b> I use Google Analytics cookies to understand which pages and case studies are useful. No names or emails are collected, and there is no advertising. <a href="/privacy/">Privacy and cookies</a></p>'+
          '<div class="cookie-btns"><button type="button" class="btn ghost sm" data-c="denied">Reject</button><button type="button" class="btn sm" data-c="granted">Accept analytics</button></div></div>';
        document.body.appendChild(bar);
        bar.addEventListener('click',function(e){var b=e.target.closest('[data-c]');if(!b)return;apply(b.getAttribute('data-c'));hide();});}
      requestAnimationFrame(function(){bar.classList.add('on');});
      var cur=get();bar.querySelectorAll('[data-c]').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-c')===cur);});
    }
    function hide(){if(bar)bar.classList.remove('on');}
    document.addEventListener('click',function(e){if(e.target.closest('[data-cookie-settings]')){e.preventDefault();show();}});
    if(!get())setTimeout(show,800);
  })();

  // space loader: shown once per session, removed as soon as the page is ready
  (function(){
    var h=document.documentElement;if(!h.classList.contains('boot'))return;
    var el=document.createElement('div');el.className='boot-ui';el.setAttribute('aria-hidden','true');
    el.innerHTML='<div class="boot-orb"><i></i><i></i><i></i></div><div class="boot-txt"><span>Initialising systems</span><b>000%</b></div>';
    document.body.appendChild(el);var b=el.querySelector('b'),n=0,t0=Date.now(),done=0;
    var tick=setInterval(function(){n=Math.min(done?100:96,n+(done?14:Math.random()*11+3));b.textContent=('00'+Math.floor(n)).slice(-3)+'%';
      if(n>=100){clearInterval(tick);h.classList.add('boot-out');setTimeout(function(){h.classList.remove('boot','boot-out');el.remove();},450);}},60);
    function ready(){setTimeout(function(){done=1;},Math.max(0,700-(Date.now()-t0)));}
    if(document.readyState==='complete')ready();else addEventListener('load',ready);
    setTimeout(function(){done=1;},1600);
  })();

  // ambient sound: generated live with Web Audio, off until the visitor switches it on
  (function(){
    var AC=window.AudioContext||window.webkitAudioContext,ctx,master,fx,on=false,timers=[],chordIx=0,voices=[];
    function pref(v){try{if(v===undefined)return localStorage.getItem('sound');localStorage.setItem('sound',v);}catch(e){return null;}}
    var CH=[[220,261.63,329.63,392,493.88],[174.61,220,261.63,329.63,392],[130.81,196,246.94,329.63,392],[164.81,196,246.94,293.66,369.99]];
    var PENT=[440,523.25,587.33,659.25,783.99,880,1046.5,1174.66];
    function build(){ctx=new AC();master=ctx.createGain();master.gain.value=0;
      var comp=ctx.createDynamicsCompressor();master.connect(comp);comp.connect(ctx.destination);
      // reverb from a decaying noise impulse
      var len=ctx.sampleRate*3.2,ir=ctx.createBuffer(2,len,ctx.sampleRate);
      for(var c=0;c<2;c++){var d=ir.getChannelData(c);for(var i=0;i<len;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/len,2.6);}
      var rev=ctx.createConvolver();rev.buffer=ir;var wet=ctx.createGain();wet.gain.value=.55;rev.connect(wet);wet.connect(master);
      var dl=ctx.createDelay(1);dl.delayTime.value=.42;var fb=ctx.createGain();fb.gain.value=.38;dl.connect(fb);fb.connect(dl);dl.connect(rev);
      fx={rev:rev,dl:dl};
      // pad: detuned saws through a slowly breathing low-pass filter
      var lp=ctx.createBiquadFilter();lp.type='lowpass';lp.frequency.value=700;lp.Q.value=.7;
      var lfo=ctx.createOscillator(),lg=ctx.createGain();lfo.frequency.value=.05;lg.gain.value=380;lfo.connect(lg);lg.connect(lp.frequency);lfo.start();
      var padG=ctx.createGain();padG.gain.value=.05;lp.connect(padG);padG.connect(master);padG.connect(rev);
      for(var v=0;v<5;v++){var g=ctx.createGain();g.gain.value=0;g.connect(lp);var oo=[];
        [-7,7].forEach(function(dt){var o=ctx.createOscillator();o.type='sawtooth';o.detune.value=dt;o.connect(g);o.start();oo.push(o);});voices.push({g:g,o:oo});}
      var sub=ctx.createOscillator(),sg=ctx.createGain();sub.type='sine';sub.frequency.value=55;sg.gain.value=.09;sub.connect(sg);sg.connect(master);sub.start();fx.sub=sub;}
    function chord(){var c=CH[chordIx++%CH.length],t=ctx.currentTime;
      voices.forEach(function(v,i){v.o.forEach(function(o){o.frequency.setTargetAtTime(c[i],t,1.2);});v.g.gain.setTargetAtTime(i<3?.5:.3,t,1.5);});
      fx.sub.frequency.setTargetAtTime(c[0]/4,t,2);}
    function ping(){if(!on)return;var t=ctx.currentTime,o=ctx.createOscillator(),g=ctx.createGain();o.type=Math.random()<.5?'sine':'triangle';
      o.frequency.value=PENT[Math.random()*PENT.length|0]*(Math.random()<.3?.5:1);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.05,t+.02);
      g.gain.exponentialRampToValueAtTime(.0001,t+2.4);o.connect(g);g.connect(fx.dl);g.connect(master);o.start(t);o.stop(t+2.5);
      timers.push(setTimeout(ping,1400+Math.random()*3200));}
    function start(){if(!AC)return;if(!ctx)build();ctx.resume();on=true;master.gain.setTargetAtTime(.5,ctx.currentTime,1.5);
      chord();timers.push(setInterval(chord,9000));ping();ui();}
    function stop(){on=false;timers.forEach(function(t){clearTimeout(t);clearInterval(t);});timers=[];if(ctx)master.gain.setTargetAtTime(0,ctx.currentTime,.4);ui();}
    function ui(){document.querySelectorAll('.snd').forEach(function(b){b.setAttribute('aria-pressed',on);b.classList.toggle('on',on);
      b.setAttribute('aria-label',on?'Turn ambient sound off':'Turn ambient sound on');});}
    // short effects for the arcade, only while sound is on
    function sfx(k){if(!on||!ctx)return;var t=ctx.currentTime,o=ctx.createOscillator(),g=ctx.createGain(),P={
      laser:['square',880,220,.08,.012],boom:['sawtooth',160,40,.35,.06],bigboom:['sawtooth',90,25,1.1,.12],hit:['sawtooth',300,60,.5,.09],
      power:['triangle',440,1320,.35,.06],mult:['triangle',660,990,.2,.05],shield:['sine',600,200,.3,.06],enemy:['square',300,180,.12,.015],over:['triangle',440,110,1.4,.08]}[k];
      if(!P)return;o.type=P[0];o.frequency.setValueAtTime(P[1],t);o.frequency.exponentialRampToValueAtTime(P[2],t+P[3]);
      g.gain.setValueAtTime(P[4],t);g.gain.exponentialRampToValueAtTime(.0001,t+P[3]);o.connect(g);g.connect(master);g.connect(fx.rev);o.start(t);o.stop(t+P[3]+.05);}
    window.SiteSound={sfx:sfx,wake:function(){if(pref()==='on'&&!on)start();}};
    document.addEventListener('click',function(e){var b=e.target.closest('.snd');if(!b)return;
      if(on){stop();pref('off');}else{start();pref('on');}try{if(window.gtag)gtag('event','sound_toggle',{state:on?'on':'off'});}catch(_){}});
    // browsers only allow audio after a gesture, so resume a saved preference on the first interaction
    if(pref()==='on'){var go=function(e){if(e.target.closest&&e.target.closest('.snd'))return;removeEventListener('pointerdown',go,true);removeEventListener('keydown',go,true);if(!on)start();};
      addEventListener('pointerdown',go,true);addEventListener('keydown',go,true);}
    document.addEventListener('visibilitychange',function(){if(ctx&&on){document.hidden?ctx.suspend():ctx.resume();}});
    ui();
  })();
  (function(){var b=document.querySelector('[data-arc-best]');if(!b)return;try{var v=+localStorage.getItem('arcBest');if(v)b.textContent=v.toLocaleString('en-GB');}catch(e){}})();

  // in-page sub-navigation: highlight the section in view
  (function(){
    var sn=document.querySelector('.subnav');if(!sn||!('IntersectionObserver' in window))return;
    var links=[].slice.call(sn.querySelectorAll('a')),map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
    var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on');});
      var a=map[e.target.id];if(a){a.classList.add('on');var r=a.parentNode;r.scrollTo({left:a.offsetLeft-r.clientWidth/2+a.clientWidth/2,behavior:'smooth'});}}});},{rootMargin:'-35% 0px -60% 0px'});
    Object.keys(map).forEach(function(id){var el=document.getElementById(id);if(el)o.observe(el);});
  })();

  // quick search: Ctrl/Cmd K or the search button; the index loads on first open
  (function(){
    var data=null,box,input,list,sel=0,items=[];
    function norm(x){return (x||'').toLowerCase();}
    function hl(t,q){if(!q)return esc(t);var i=norm(t).indexOf(q.split(' ')[0]);if(i<0)return esc(t);var w=q.split(' ')[0].length;
      return esc(t.slice(0,i))+'<mark>'+esc(t.slice(i,i+w))+'</mark>'+esc(t.slice(i+w));}
    function score(it,terms){var t=norm(it.t),hay=t+' '+norm(it.d)+' '+norm(it.g)+' '+norm(it.k),s=0;
      for(var i=0;i<terms.length;i++){var w=terms[i],p=t.indexOf(w);if(p===0)s+=12;else if(p>0)s+=t.charAt(p-1)===' '?8:5;else if(hay.indexOf(w)>-1)s+=2;else return 0;}
      return s+(it.k==='Page'||it.k==='Service'?1.5:0);}
    function render(){var q=norm(input.value).trim(),terms=q.split(/\s+/).filter(Boolean);
      if(!data){list.innerHTML='<div class="qs-empty">Loading…</div>';return;}
      items=terms.length?data.map(function(it){return [score(it,terms),it];}).filter(function(x){return x[0]>0;}).sort(function(a,b){return b[0]-a[0];}).slice(0,30).map(function(x){return x[1];})
        :data.filter(function(it){return it.k!=='Insight'&&it.k!=='Case study';}).concat(data.filter(function(it){return it.k==='Case study';}).slice(0,3),data.filter(function(it){return it.k==='Insight';}).slice(0,3));
      sel=0;list.innerHTML=items.length?items.map(function(it,i){var ext=it.u.indexOf('http')===0;
        return '<a href="'+esc(it.u)+'"'+(ext?' target="_blank" rel="noopener"':'')+' role="option" data-i="'+i+'"'+(i===0?' class="sel" aria-selected="true"':'')+'><b>'+hl(it.t,q)+'</b><span>'+esc(it.d||'')+'</span><i>'+esc(it.k)+'</i></a>';}).join('')
        :'<div class="qs-empty">Nothing found for “'+esc(input.value)+'”. Try “RAG”, “FHIR” or “Kubernetes”.</div>';}
    function move(d){var a=list.querySelectorAll('a');if(!a.length)return;a[sel].classList.remove('sel');a[sel].removeAttribute('aria-selected');sel=(sel+d+a.length)%a.length;
      a[sel].classList.add('sel');a[sel].setAttribute('aria-selected','true');a[sel].scrollIntoView({block:'nearest'});}
    function build(){box=document.createElement('div');box.className='qs';box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-label','Search the site');
      box.innerHTML='<div class="qs-box"><div class="qs-in"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'+
        '<input type="search" placeholder="Search pages, case studies and insights…" aria-label="Search" autocomplete="off" spellcheck="false"><kbd data-close>Esc</kbd></div>'+
        '<div class="qs-list" role="listbox"></div><div class="qs-foot"><span>↑↓ to move</span><span>↵ to open</span><span>esc to close</span></div></div>';
      document.body.appendChild(box);input=box.querySelector('input');list=box.querySelector('.qs-list');
      input.addEventListener('input',render);
      input.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){e.preventDefault();move(1);}else if(e.key==='ArrowUp'){e.preventDefault();move(-1);}
        else if(e.key==='Enter'){var a=list.querySelector('a.sel');if(a){e.preventDefault();a.click();}}});
      box.addEventListener('click',function(e){if(e.target===box||e.target.closest('[data-close]'))close();var a=e.target.closest('.qs-list a');
        if(a)try{if(window.gtag)gtag('event','search_select',{search_term:input.value.slice(0,80),link_url:a.getAttribute('href')});}catch(_){}});}
    var last;
    function open(){if(!box)build();last=document.activeElement;box.classList.add('on');document.body.style.overflow='hidden';input.value='';render();setTimeout(function(){input.focus();},10);
      if(!data)fetch('/assets/search.json').then(function(r){return r.json();}).then(function(d){data=d;render();}).catch(function(){list.innerHTML='<div class="qs-empty">Search is unavailable right now.</div>';});
      try{if(window.gtag)gtag('event','search_open',{});}catch(_){}}
    function close(){if(!box)return;box.classList.remove('on');document.body.style.overflow='';
      var t=input.value.trim();if(t)try{if(window.gtag)gtag('event','search',{search_term:t.slice(0,80)});}catch(_){}if(last&&last.focus)last.focus();}
    document.addEventListener('click',function(e){if(e.target.closest('[data-search]')){e.preventDefault();open();}});
    document.addEventListener('keydown',function(e){if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();box&&box.classList.contains('on')?close():open();}
      else if(e.key==='Escape'&&box&&box.classList.contains('on'))close();
      else if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test((document.activeElement||{}).tagName||'')&&!(box&&box.classList.contains('on'))){e.preventDefault();open();}});
    if(/Mac|iPhone|iPad/.test(navigator.platform||''))return;document.querySelectorAll('.kbtn kbd').forEach(function(k){k.textContent='Ctrl K';});
  })();
  // regions: live clocks and an office-hours chart drawn on the viewer's own 24-hour clock
  (function(){
    var cl=document.querySelectorAll('.rg-clock'),bars=document.querySelectorAll('.tz-bar'),dots=document.querySelectorAll('.rg-dot');if(!cl.length&&!bars.length)return;
    function offsetMin(tz){var d=new Date(),p=new Intl.DateTimeFormat('en-GB',{timeZone:tz,hourCycle:'h23',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}).formatToParts(d),o={};
      p.forEach(function(x){o[x.type]=x.value;});return Math.round((Date.UTC(+o.year,+o.month-1,+o.day,+o.hour,+o.minute)-d.getTime())/60000);}
    function mod(x){return ((x%1440)+1440)%1440;}
    var you=-new Date().getTimezoneOffset();
    function tick(){var now=new Date(),utc=now.getUTCHours()*60+now.getUTCMinutes();
      cl.forEach(function(c){try{c.textContent=now.toLocaleTimeString('en-GB',{timeZone:c.dataset.tz,hour:'2-digit',minute:'2-digit'});}catch(e){}});
      dots.forEach(function(d){try{var l=mod(utc+offsetMin(d.dataset.tz));var on=l>=540&&l<1080;d.classList.toggle('on',on);d.title=on?'Office hours':'Out of hours';}catch(e){}});
      bars.forEach(function(b){try{var start=mod(540-offsetMin(b.dataset.tz)+you);b.style.setProperty('--s',(start/1440*100)+'%');}catch(e){}});
      var n=document.querySelector('.tz-now'),t=document.querySelector('.tz');
      if(n&&t){n.style.setProperty('--n',(mod(utc+you)/1440*100)+'%');var first=t.querySelector('.tz-row'),last=t.querySelectorAll('.tz-row');
        if(first){var h=last[last.length-1].getBoundingClientRect().bottom-first.getBoundingClientRect().top;n.style.setProperty('--h',h+'px');}}}
    tick();setInterval(tick,30000);addEventListener('resize',tick);
  })();
