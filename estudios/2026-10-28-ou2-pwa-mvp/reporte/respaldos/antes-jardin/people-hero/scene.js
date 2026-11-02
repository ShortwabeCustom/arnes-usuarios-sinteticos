/* Scene lifecycle: routes via WAAPI, joint cycles via CSS, one lightweight rAF. */
(() => {
  'use strict';
  const root=document.querySelector('[data-people-hero]');
  if(!root||!window.PeopleHeroArt)return;
  const scene=root.querySelector('.people-scene');
  const toggle=root.querySelector('.people-toggle');
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  const fine=matchMedia('(hover: hover) and (pointer: fine)');
  const layers=['back','mid','front'].map(name=>{
    const el=document.createElement('div');el.className=`people-layer people-layer-${name}`;scene.append(el);return el;
  });
  let userPaused=false,visible=true,frame=0,lastTime=0,width=0;
  let targetX=0,targetY=0,pointerX=0,pointerY=0;
  const entries=window.PeopleHeroArt.walkers.map((data,index)=>{
    const el=document.createElement('div');
    el.className=`walker walker-${data.layer}${data.hero?' walker-hero':''}`;
    el.dataset.walker=data.id;
    el.dataset.density=data.density;
    el.style.cssText=`--gesture:${5+index%5*.7}s;--blink:${4.1+index%7*.47}s;--tilt:${[-2,1,0,2,-1][index%5]}deg;--ink:${data.layer==='back'?'#76918c':data.ink};--cloth:${data.fill};--trousers:${index%3===0?'#fafaf7':data.ink};--rear:${index%3===0?'#dbe0e7':data.ink};--scale:${data.scale};--build:${data.build};--facing:${data.direction};--step:${data.step*2}s;--phase:${-index*.237}s;--signal-delay:${-index*1.13}s;--arrival:${.25+index*.018}s;bottom:${100-data.y}%;`;
    el.innerHTML=`<div class="walker-presence"><div class="walker-proximity"><div class="walker-facing">${window.PeopleHeroArt.character(data)}</div></div></div>`;
    layers[['back','mid','front'].indexOf(data.layer)].append(el);
    const entry={data,el,animation:null,hover:false,rate:1};
    el.addEventListener('pointerenter',()=>{if(!fine.matches||motion.matches)return;entry.hover=true;el.classList.add('is-near');});
    el.addEventListener('pointerleave',()=>{entry.hover=false;el.classList.remove('is-near');});
    return entry;
  });
  const protagonist=entries.find(entry=>entry.data.hero);
  function running(){return !userPaused&&!motion.matches&&visible&&!document.hidden;}
  function layout(){
    const nextWidth=scene.clientWidth;
    if(nextWidth===width&&entries[0].animation)return;
    width=nextWidth;
    entries.forEach(entry=>{
      const {data,el}=entry;
      const lane=entries.filter(item=>item.data.layer===data.layer&&getComputedStyle(item.el).display!=='none');
      const slot=lane.indexOf(entry);
      const staticX=(slot+.5)/lane.length*width;
      entry.savedPhase=entry.animation?((Number(entry.animation.currentTime)||0)/(data.duration*1000))%1:undefined;
      entry.animation?.cancel();
      const outside=width<621?65:100;
      const desiredX=(slot+.5)/lane.length*(width+outside*2)-outside+(data.layer==='mid'?35:0);
      const initialPhase=data.direction===1?(desiredX+outside)/(width+outside*2):1-(desiredX+outside)/(width+outside*2);
      const phase=entry.savedPhase??(data.hero?.37:Math.max(0,Math.min(.99,initialPhase)));
      const start=data.direction===1?-outside:width+outside;
      const finish=data.direction===1?width+outside:-outside;
      const transform=x=>`translate3d(${x}px,0,0)`;
      const keys=data.hero?[
        {transform:transform(start),offset:0},
        {transform:transform(width*.43),offset:.32,easing:'cubic-bezier(.2,.7,.35,1)'},
        {transform:transform(width*.49),offset:.4},
        {transform:transform(width*.49),offset:.57,easing:'cubic-bezier(.65,0,.8,.3)'},
        {transform:transform(width*.55),offset:.65},
        {transform:transform(finish),offset:1},
      ]:[{transform:transform(start)},{transform:transform(finish)}];
      entry.animation=el.animate(keys,{duration:data.duration*1000,iterations:Infinity,easing:'linear'});
      entry.animation.currentTime=phase*data.duration*1000;
      el.style.setProperty('--static-x',`${Math.max(8,Math.min(width-70,staticX))}px`);
    });
    sync();
  }
  function tick(time){
    frame=0;
    if(!running())return;
    const dt=Math.min((time-lastTime)||16,50);lastTime=time;
    const blend=1-Math.exp(-dt/130);
    pointerX+=(targetX-pointerX)*blend;pointerY+=(targetY-pointerY)*blend;
    layers.forEach((layer,index)=>{const depth=[3,6,10][index];layer.style.transform=`translate3d(${pointerX*depth}px,${pointerY*depth}px,0)`;});
    entries.forEach(entry=>{
      const rate=entry.hover ? .72 : 1;
      if(Math.abs(entry.rate-rate)>.005){entry.rate+=(rate-entry.rate)*blend;entry.animation.updatePlaybackRate(entry.rate);}
    });
    const period=protagonist.data.duration*1000;
    const phase=(Number(protagonist.animation.currentTime)||0)%period/period;
    protagonist.el.classList.toggle('is-reading',phase>=.4&&phase<=.57);
    protagonist.el.classList.toggle('is-notified',phase>=.435&&phase<=.54);
    frame=requestAnimationFrame(tick);
  }
  function sync(){
    const play=running();
    scene.classList.toggle('is-paused',!play);
    scene.classList.toggle('is-reduced',motion.matches);
    entries.forEach(entry=>{
      if(play&&getComputedStyle(entry.el).display!=='none')entry.animation?.play();
      else entry.animation?.pause();
    });
    toggle.textContent=userPaused?'Reanudar movimiento':'Pausar movimiento';
    toggle.setAttribute('aria-pressed',String(userPaused));
    if(play&&!frame){lastTime=0;frame=requestAnimationFrame(tick);}
    if(!play){cancelAnimationFrame(frame);frame=0;}
    if(motion.matches){targetX=targetY=pointerX=pointerY=0;layers.forEach(layer=>layer.style.transform='none');}
  }
  toggle.addEventListener('click',()=>{userPaused=!userPaused;sync();});
  root.addEventListener('pointermove',event=>{
    if(!fine.matches||!running())return;
    // The hero fills the viewport width; no layout reads in pointermove.
    targetX=(event.clientX/innerWidth-.5)*2;targetY=(event.clientY/innerHeight-.5)*2;
  },{passive:true});
  root.addEventListener('pointerleave',()=>{targetX=targetY=0;});
  motion.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  const resize=new ResizeObserver(layout);resize.observe(scene);
  const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;sync();},{threshold:0});observer.observe(root);
  addEventListener('pagehide',()=>{cancelAnimationFrame(frame);entries.forEach(entry=>entry.animation?.pause());});
  addEventListener('pageshow',sync);
  layout();
})();
