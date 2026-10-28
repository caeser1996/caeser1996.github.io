  // playbook
  var PB=[
   {t:"Our AI pilot won't make it to production",d:"Demos impress, but answers are unreliable, costs are unknown and nobody will sign off.",
    dx:"Usually the model isn't the problem. Retrieval is ungrounded, there's no evaluation set, and no one owns quality.",
    s:["Define the decisions the AI supports and the cost of a wrong answer","Ground retrieval in a domain ontology and knowledge graph (GraphRAG)","Build an evaluation harness and tracing before adding features","Orchestrate agents with LangGraph: explicit state, tools via MCP, human checkpoints","Ship one workflow to production behind guardrails, then expand"],
    o:["Answers with citations","Measurable quality gates","Known cost per query","A path from pilot to platform"]},
   {t:"Our data is everywhere and means different things",d:"Every team has its own definition of a customer, a patient or revenue. Reports disagree. AI makes it worse.",
    dx:"It's a semantic problem, not a storage problem. Without a shared model, more pipelines just copy the confusion.",
    s:["Run domain workshops to capture core concepts and relationships","Formalise an ontology and controlled vocabularies, versioned like code","Map sources onto it: entity resolution and master data","Expose a semantic layer to BI, APIs and AI agents","Put data contracts and quality checks at the boundaries"],
    o:["One definition of truth","Reports that reconcile","AI-ready knowledge graph","Faster onboarding of new sources"]},
   {t:"Our platform buckles as we grow",d:"Latency spikes at peak, batch jobs overrun, incidents are frequent and every release feels risky.",
    dx:"Synchronous coupling and shared databases turn growth into contention. The architecture is fighting the load.",
    s:["Instrument first: find the real bottlenecks with tracing and load tests","Set SLOs and latency budgets for the critical paths","Move hot paths to an event-driven core with idempotent consumers","Redesign data access: indexes, aggregations, read models, caching","Automate deploys and rollbacks on Kubernetes with GitOps"],
    o:["1M+ tx/day headroom","Predictable latency","Fewer incidents","Safe, frequent releases"]},
   {t:"Our healthcare data won't interoperate",d:"EHRs, labs and claims arrive in different formats and codes. Every integration is a bespoke project.",
    dx:"Point-to-point integration doesn't scale. You need a standard exchange format and a standard analytical model.",
    s:["Inventory sources, code systems and PHI flows","Standardise exchange on HL7 FHIR; normalise to SNOMED, LOINC and RxNorm","Land analytics in OMOP CDM for reproducible research with OHDSI tools","Build in de-identification, consent, encryption and audit trails","Layer clinical AI only on governed, provenance-tracked data"],
    o:["Integrations in weeks, not months","Research-ready datasets","HIPAA-aligned by design","Trusted clinical AI"]},
   {t:"Cloud costs and complexity are out of control",d:"Environments were hand-built, nobody knows what's running, and the bill grows faster than revenue.",
    dx:"Without infrastructure as code and cost visibility, every environment drifts and waste is invisible.",
    s:["Map every resource to an owner, a service and a cost","Codify infrastructure in Terraform modules across AWS, Azure and GCP","Consolidate workloads onto a shared Kubernetes platform","Right-size, autoscale and route AI calls to the cheapest capable model","Report unit economics per transaction, tenant and token"],
    o:["Reproducible environments","Lower, predictable spend","Audit-ready infra","Portable, no lock-in"]},
   {t:"We don't have senior technical leadership",d:"The founders or executives are making technical bets without a trusted, experienced voice in the room.",
    dx:"You don't need a full-time CTO yet. You need CTO-grade judgement on the decisions that are expensive to reverse.",
    s:["Assess the team, architecture, roadmap and risk in the first month","Set a technical strategy tied to business milestones","Establish architecture governance: ADRs, reviews, standards","Hire and mentor senior engineers; design team topology","Represent technology to the board, investors and partners"],
    o:["Confident technical decisions","A team that scales","Investor-ready diligence","A clean handover to a full-time CTO"]}
  ];
  // tabs (content is pre-rendered in the HTML for crawlers; JS only switches panes)
  function bindTabs(list){
    if(!list)return;
    var ts=[].slice.call(list.querySelectorAll('[role=tab]'));
    function sel(i,focus){ts.forEach(function(t,j){var on=j===i;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!on;});if(focus)ts[i].focus();}
    ts.forEach(function(t,i){t.addEventListener('click',function(){sel(i);});
      t.addEventListener('keydown',function(e){var k={ArrowRight:1,ArrowDown:1,ArrowLeft:-1,ArrowUp:-1}[e.key];if(k){e.preventDefault();sel((i+k+ts.length)%ts.length,true);}});});
  }
  bindTabs(document.getElementById('ptabs'));bindTabs(document.getElementById('csTabs'));bindTabs(document.getElementById('dmtabs'));

  // assessor
  (function(){
    if(!document.getElementById('aq'))return;
    var EMAIL='sumantamukhopadhyaywork@gmail.com',ans={};
    var ENG={rev:['Architecture & AI readiness review','2–4 weeks · fixed scope'],cto:['Fractional CTO','ongoing · part-time'],build:['Build & hand-off','project · embedded'],adv:['Advisory & due diligence','retainer or one-off']};
    var XP=["Applies: production RAG and LangGraph agent systems, plus research-grade evaluation discipline.",
      "Applies: ontology engineering and standard data models from healthcare research platforms.",
      "Applies: re-architecting event-driven systems to sustain 1M+ transactions a day.",
      "Applies: hands-on OMOP CDM, OHDSI and clinical vocabularies, and published biomedical research.",
      "Applies: Terraform across AWS, Azure and GCP, and a self-hosted Kubernetes platform built from scratch.",
      "Applies: principal-level leadership, founder experience and mentoring engineers in public."];
    var LBL={who:{startup:'a startup',scaleup:'a scale-up',enterprise:'an enterprise',health:'a healthcare or life-sciences organisation',fintech:'a fintech or financial-services firm',commerce:'an e-commerce or marketplace business',investor:'an investor'},team:{s:'under 10 engineers',m:'10–50 engineers',l:'50+ engineers'},when:{explore:'exploring options',quarter:'this quarter',urgent:'urgent'}};
    function pick(){
      var p=+ans.pain,w=ans.who,u=ans.when,t=ans.team;
      if(w==='investor')return 'adv';
      if(p===5||(w==='startup'&&t==='s'))return 'cto';
      if(u==='urgent'&&(p===2||p===4))return 'build';
      if(w==='enterprise'&&u==='explore')return 'adv';
      if(u==='explore')return 'rev';
      return (p===0||p===1||p===3)?'rev':'build';
    }
    function render(){
      var ar=document.getElementById('ar');
      var n=['who','pain','team','when'].filter(function(k){return ans[k]!=null;}).length;
      if(ans.pain==null){return;}
      var P=PB[+ans.pain],e=ENG[pick()],fit=Math.round(n/4*100);
      var ctx=[ans.who&&LBL.who[ans.who],ans.team&&LBL.team[ans.team],ans.when&&LBL.when[ans.when]].filter(Boolean).join(' · ');
      var then=pick()==='rev'?'then build or fractional support if you want it':pick()==='build'?'starting with a 2-week stabilisation sprint':pick()==='cto'?'starting with a 30-day assessment':'scoped to the decision in front of you';
      ar.innerHTML='<div class="fade">'+
        '<div class="fit"><span>diagnosis '+fit+'% complete</span><div class="fm"><i style="width:0"></i></div></div>'+
        '<div class="rk">Your challenge'+(ctx?' · '+esc(ctx):'')+'</div><h3>'+esc(P.t)+'</h3>'+
        '<div class="blk"><div class="lb">Likely root cause</div><p>'+esc(P.dx)+'</p></div>'+
        '<div class="blk"><div class="lb">First 30 days</div><ol>'+P.s.slice(0,3).map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ol></div>'+
        '<div class="blk"><div class="lb">Relevant experience</div><p>'+esc(XP[+ans.pain])+'</p></div>'+
        '<div class="blk eng"><div><div class="lb">Recommended engagement</div><b>'+esc(e[0])+'</b></div><span class="mono" style="font-size:12px;color:var(--ink3)">'+esc(e[1])+'</span></div>'+
        '<div class="blk" style="padding-bottom:0"><div class="lb">Outcome</div><div class="pout">'+P.o.map(function(x){return '<span>'+esc(x)+'</span>';}).join('')+'</div></div>'+
        '<div class="actions"><button type="button" class="btn" id="abook">Book a meeting about this →</button><button type="button" class="btn ghost" id="asend">Email it instead</button><button type="button" class="btn ghost" id="areset">Start over</button></div>'+
        '<p class="anote2" id="anote2">Opens my calendar. Your diagnosis is copied so you can paste it into the booking notes.</p></div>';
      requestAnimationFrame(function(){var i=ar.querySelector('.fm i');if(i)i.style.width=fit+'%';});
      var note=document.getElementById('anote').value.trim();
      var body='Hi Sumanta,\n\nI used the challenge analyser on your site.\n\n'+
        'Who: '+(LBL.who[ans.who]||'-')+'\nChallenge: '+P.t+'\nTeam: '+(LBL.team[ans.team]||'-')+'\nTimeline: '+(LBL.when[ans.when]||'-')+
        '\nSuggested engagement: '+e[0]+' ('+then+')\n'+(note?'\nMore context:\n'+note+'\n':'')+'\nCould we set up a call?\n';
      var subj='Challenge: '+P.t;
      document.getElementById('asend').onclick=function(){openContact(subj,body);};
      document.getElementById('abook').onclick=function(){
        var summary='Challenge: '+P.t+'\nWho: '+(LBL.who[ans.who]||'-')+' | Team: '+(LBL.team[ans.team]||'-')+' | Timeline: '+(LBL.when[ans.when]||'-')+'\nSuggested: '+e[0]+(note?'\nContext: '+note:'');
        copyText(summary);window.open('https://calendar.app.google/fpARv4QHsYCLMo3a8','_blank','noopener');
        var n=document.getElementById('anote2');if(n){n.textContent='✓ Diagnosis copied. Paste it into the notes field when you book.';n.classList.add('ok');}
      };
      document.getElementById('areset').onclick=function(){ans={};document.querySelectorAll('.chip2').forEach(function(c){c.setAttribute('aria-pressed','false');});document.getElementById('anote').value='';
        ar.innerHTML='<div class="empty fade"><p>Pick your answers on the left and your diagnosis will build here.</p></div>';};
    }
    document.querySelectorAll('#aq .chips').forEach(function(g){
      g.addEventListener('click',function(ev){var b=ev.target.closest('.chip2');if(!b)return;
        g.querySelectorAll('.chip2').forEach(function(c){c.setAttribute('aria-pressed',c===b);});
        ans[g.dataset.q]=b.dataset.v;render();});
    });
    document.getElementById('anote').addEventListener('input',function(){if(ans.pain!=null)render();});
  })();

  // bench terminal typing
  (function(){
    var el=document.getElementById('benchTxt');if(!el)return;
    var L=[['c','# what is on the bench this week'],['p','$ nvidia-smi --query-gpu=name --format=csv,noheader'],['','NVIDIA GB10 · DGX Spark'],
      ['p','$ serve --model open-weight-70b --quant q4 --ctx 32k'],['g','✓ model loaded · 128 GB unified memory'],
      ['p','$ bench --suite rag-evals --compare hosted'],['','  latency, cost, quality   → logged per prompt'],['','  data leaves    local  never    hosted  every call'],
      ['p','$ finetune --method lora --data ./domain-ontology'],['g','✓ adapter ready · evals running…'],['c','# notes → client playbooks']];
    var still=matchMedia('(prefers-reduced-motion: reduce)').matches,started=false;
    function line(t){return t[0]?'<span class="'+t[0]+'">'+esc(t[1])+'</span>':esc(t[1]);}
    if(still){el.innerHTML=L.map(line).join('\n');return;}
    var o=new IntersectionObserver(function(es){if(!es[0].isIntersecting||started)return;started=true;o.disconnect();
      var i=0,c=0,done='';
      (function tick(){
        if(i>=L.length){el.innerHTML=done+'<span class="cur"></span>';return;}
        var t=L[i],typing=t[0]==='p';
        if(typing&&c<t[1].length){c+=2;el.innerHTML=done+'<span class="p">'+esc(t[1].slice(0,c))+'</span><span class="cur"></span>';setTimeout(tick,28);return;}
        done+=line(t)+'\n';i++;c=0;el.innerHTML=done+'<span class="cur"></span>';setTimeout(tick,typing?380:160);
      })();
    },{threshold:.3});o.observe(el);
  })();

  // headline word reveal
  var h=document.getElementById('heroH');
  if(h)(function wrap(node){
    Array.from(node.childNodes).forEach(function(n){
      if(n.nodeType===3){
        var f=document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(function(part){
          if(!part)return;
          if(/^\s+$/.test(part)){f.appendChild(document.createTextNode(part));return;}
          var w=document.createElement('span');w.className='w';var i=document.createElement('span');i.textContent=part;w.appendChild(i);f.appendChild(w);
        });
        n.replaceWith(f);
      }else if(n.nodeType===1){
        var w=document.createElement('span');w.className='w';n.replaceWith(w);var i=document.createElement('span');i.appendChild(n);w.appendChild(i);
      }
    });
  })(h);
  if(h)h.querySelectorAll('.w > span').forEach(function(s,i){s.style.transitionDelay=(0.15+i*0.07)+'s';});
  if(h)requestAnimationFrame(function(){requestAnimationFrame(function(){h.parentNode.classList.add('go');});});

  // tag stagger
  document.querySelectorAll('.layer').forEach(function(l){l.querySelectorAll('.tag').forEach(function(t,i){t.style.transitionDelay=(0.1+i*0.04)+'s';});});

  // counters
  var cio=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;cio.unobserve(e.target);
    var el=e.target,end=+el.dataset.count,suf=el.dataset.suffix||'',t0=performance.now(),d=1600;
    (function step(now){var p=Math.min(1,(now-t0)/d),v=Math.round(end*(1-Math.pow(1-p,3)));el.textContent=v+suf;if(p<1)requestAnimationFrame(step);})(t0);
  });},{threshold:.5});
  document.querySelectorAll('[data-count]').forEach(function(el){cio.observe(el);});

  // spotlight on cases
  document.querySelectorAll('.case').forEach(function(c){c.addEventListener('pointermove',function(e){var r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px');});});


  // knowledge-graph canvas
  (function(){
    var cv=document.getElementById('graph');if(!cv)return;var cx=cv.getContext('2d'),dpr=Math.min(2,devicePixelRatio||1),W,H,nodes=[],mouse={x:-1e4,y:-1e4};
    var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
    var labels=['Ontology','Entity','Agent','Embedding','Event','Graph','Policy','Model','Pipeline','Service','Cluster','Schema','Vector','Concept'];
    function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
    function size(){var r=cv.getBoundingClientRect();W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;cx.setTransform(dpr,0,0,dpr,0,0);}
    function init(){size();nodes=[];var n=Math.round(Math.min(70,Math.max(28,W*H/16000)));
      for(var i=0;i<n;i++)nodes.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25,r:Math.random()<.18?3.2:1.6,l:i<labels.length&&W>700?labels[i]:null});}
    function frame(){
      var ink=css('--ink'),acc=css('--accent');cx.clearRect(0,0,W,H);
      for(var i=0;i<nodes.length;i++){var a=nodes[i];
        if(!still){a.x+=a.vx;a.y+=a.vy;if(a.x<0||a.x>W)a.vx*=-1;if(a.y<0||a.y>H)a.vy*=-1;
          var dx=a.x-mouse.x,dy=a.y-mouse.y,dm=dx*dx+dy*dy;if(dm<14000){a.x+=dx*.012;a.y+=dy*.012;}}
        for(var j=i+1;j<nodes.length;j++){var b=nodes[j],d=Math.hypot(a.x-b.x,a.y-b.y);
          if(d<140){cx.globalAlpha=(1-d/140)*.35;cx.strokeStyle=(a.r>2||b.r>2)?acc:ink;cx.lineWidth=.7;cx.beginPath();cx.moveTo(a.x,a.y);cx.lineTo(b.x,b.y);cx.stroke();}}}
      cx.font='11px "IBM Plex Mono", monospace';
      nodes.forEach(function(a){cx.globalAlpha=a.r>2?.95:.5;cx.fillStyle=a.r>2?acc:ink;cx.beginPath();cx.arc(a.x,a.y,a.r,0,7);cx.fill();
        if(a.l){cx.globalAlpha=.55;cx.fillStyle=ink;cx.fillText(a.l,a.x+7,a.y-6);}});
      cx.globalAlpha=1;if(!still)requestAnimationFrame(frame);
    }
    cv.parentElement.addEventListener('pointermove',function(e){var r=cv.getBoundingClientRect();mouse.x=e.clientX-r.left;mouse.y=e.clientY-r.top;});
    cv.parentElement.addEventListener('pointerleave',function(){mouse.x=mouse.y=-1e4;});
    addEventListener('resize',init);init();frame();
    btn.addEventListener('click',function(){if(still)frame();});
  })();
