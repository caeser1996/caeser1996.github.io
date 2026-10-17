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
