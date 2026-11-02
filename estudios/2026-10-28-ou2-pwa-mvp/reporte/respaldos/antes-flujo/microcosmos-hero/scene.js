/* Deterministic, mostly still stories. No pointer effects or frame-by-frame JS. */
(() => {
 'use strict';
 const root=document.querySelector('[data-microcosmos-hero]');
 if(!root||!window.MicrocosmosConfig||!window.MicrocosmosArt)return;
 const scene=root.querySelector('.microcosmos-scene');
 const button=root.querySelector('.microcosmos-toggle');
 const config=window.MicrocosmosConfig,art=window.MicrocosmosArt;
 const small=matchMedia('(max-width: 700px)'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let animations=[],userPaused=false,inView=true,savedTime=0;
 const ns='http://www.w3.org/2000/svg';
 function render(){
  savedTime=animations[0]?.currentTime??savedTime;
  animations.forEach(a=>a.cancel());animations=[];
  const mobile=small.matches;
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',(mobile?config.mobileViewBox:config.viewBox).join(' '));
  svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  svg.innerHTML=art.defs+art.environment(mobile);
  const people=config.people.filter(p=>!mobile||p.mobile).sort((a,b)=>(mobile?a.mobile[1]:a.y)-(mobile?b.mobile[1]:b.y));
  people.forEach(p=>{
   const [x,y]=mobile?p.mobile:[p.x,p.y];
   const person=document.createElementNS(ns,'g');
   person.setAttribute('class','mc-person');person.dataset.person=p.id;
   person.setAttribute('transform',`translate(${x} ${y})`);
   person.style.cssText=`--mc-cloth:${art.colors(p.fill)};--mc-skin:${p.fill==='blue'?'#d7bfa5':'#e1ccb5'};`;
   person.innerHTML=`<g class="mc-travel"><g class="mc-facing" style="transform:scaleX(${p.facing||1})">${art.figure(p)}</g></g>`;
   svg.append(person);
  });
  // Foreground plants provide depth; no hiding of route resets is needed.
  const front=document.createElementNS(ns,'g');front.classList.add('mc-foreground');
  front.innerHTML=mobile?'<path d="M171 223 Q161 208 166 199 Q181 199 179 216 M179 221 Q189 208 197 213 Q197 225 179 221Z" fill="#a3b99c"/>':'<path d="M335 539 Q324 520 332 508 Q350 509 345 530 M344 536 Q354 517 369 521 Q370 539 344 536Z" fill="#a3b99c"/>';
  svg.append(front);scene.replaceChildren(svg);
  if(!reduced.matches)sequence(mobile);
  sync();
 }
 function sequence(mobile){
  const tracks=new Map();
  function track(node,time,transform,easing='ease-in-out'){
   if(!node)return;
   if(!tracks.has(node))tracks.set(node,[]);
   tracks.get(node).push({offset:time/config.cycle,transform,easing});
  }
  const node=(id,selector)=>scene.querySelector(`[data-person="${id}"] ${selector}`);
  const rotate=(id,selector,times)=>times.forEach(([t,a])=>track(node(id,selector),t,`rotate(${a}deg)`));
  function walk(id,start,end,dx,dy){
   const travel=node(id,'.mc-travel'),facing=node(id,'.mc-facing');
   const forwardEnd=start+2.6,backStart=end-2.6;
   [[0,0,0],[start,0,0],[forwardEnd,dx,dy],[backStart,dx,dy],[end,0,0],[config.cycle,0,0]].forEach(([t,x,y])=>track(travel,t,`translate(${x}px,${y}px)`, 'linear'));
   [[0,1],[forwardEnd,1],[backStart-.5,-1],[end,-1],[end+.6,1],[config.cycle,1]].forEach(([t,x])=>track(facing,t,`scaleX(${x})`));
   for(const [segmentStart,segmentEnd] of [[start,forwardEnd],[backStart,end]]){
    for(const side of ['front','back']){
     const sign=side==='front'?1:-1;
     const hip=node(id,`.mc-leg-${side}`),knee=node(id,`.mc-knee-${side}`);
     track(hip,segmentStart,'rotate(0deg)');track(knee,segmentStart,'rotate(0deg)');
     const steps=8;
     for(let n=1;n<steps;n++){
      const t=segmentStart+(segmentEnd-segmentStart)*n/steps;
      track(hip,t,`rotate(${(n%2?18:-18)*sign}deg)`,'linear');
      track(knee,t,`rotate(${n%2===(side==='front'?0:1)?-26:0}deg)`,'linear');
     }
     track(hip,segmentEnd,'rotate(0deg)');track(knee,segmentEnd,'rotate(0deg)');
    }
   }
   rotate(id,'.mc-head',[[forwardEnd,0],[forwardEnd+.45,3],[backStart-.2,3],[backStart,0]]);
  }
  config.slots.forEach(slot=>{
   const t=slot.start;
   if(slot.name==='quiet'){
    rotate('reader','.mc-head',[[t,0],[t+.7,3],[t+1.8,3],[t+3,0]]);
    rotate('reader','.mc-phone-arm',[[t+.5,0],[t+1.2,-4],[t+1.7,-4],[t+2.4,0]]);
   }
   if(slot.name==='shared'){
    rotate('sharer','.mc-phone-arm',[[t,0],[t+1,-7],[t+3.5,-7],[t+4.5,0]]);
    rotate('companion','.mc-upper',[[t+.8,0],[t+1.8,4],[t+3.4,4],[t+5,0]]);
   }
   if(slot.name==='walk')walk('walker',t,t+slot.duration,...(mobile?config.mobileWalk:config.walk));
   if(slot.name==='pause')rotate('seated','.mc-foot',[[t,0],[t+.7,-6],[t+1.4,0],[t+2.1,-4],[t+3,0]]);
   if(slot.name==='encounter'){
    if(!mobile){
     const arriving=node('arriving','.mc-travel');
     [[0,0,0],[t,0,0],[t+2,-22,-7],[t+5,-22,-7],[t+8,0,0],[config.cycle,0,0]].forEach(([time,x,y])=>track(arriving,time,`translate(${x}px,${y}px)`,'ease-in-out'));
     // A few short steps, with a long still greeting between approach and return.
     for(const side of ['front','back']){
      const sign=side==='front'?1:-1;
      rotate('arriving',`.mc-leg-${side}`,[[t,0],[t+.4,16*sign],[t+.8,-16*sign],[t+1.2,16*sign],[t+1.6,-16*sign],[t+2,0],[t+5,0],[t+5.6,-16*sign],[t+6.2,16*sign],[t+6.8,-16*sign],[t+7.4,16*sign],[t+8,0]]);
     }
     [[0,-1],[t+4.6,-1],[t+5,1],[t+8,1],[t+8.6,-1],[config.cycle,-1]].forEach(([time,x])=>track(node('arriving','.mc-facing'),time,`scaleX(${x})`));
    }
    rotate('greeter','.mc-wave',[[t+1.5,0],[t+2,-7],[t+2.5,6],[t+3,-6],[t+3.5,0]]);
   }
  });
  // The single environmental action occurs during an otherwise quiet interval.
  const canopy=scene.querySelector('.mc-tree .mc-canopy');
  [[0,0],[27,0],[28,.7],[29,0],[config.cycle,0]].forEach(([t,a])=>track(canopy,t,`rotate(${a}deg)`));
  tracks.forEach((keys,element)=>{
   keys.sort((a,b)=>a.offset-b.offset);
   if(keys[0].offset>0)keys.unshift({offset:0,transform:'none'});
   if(keys.at(-1).offset<1)keys.push({offset:1,transform:'none'});
   const a=element.animate(keys,{duration:config.cycle*1000,iterations:Infinity,easing:'linear'});
   a.pause();a.currentTime=savedTime;animations.push(a);
  });
 }
 function sync(){
  const running=!userPaused&&!reduced.matches&&inView&&!document.hidden;
  animations.forEach(a=>running?a.play():a.pause());
  root.dataset.motion=reduced.matches?'reduced':running?'playing':'paused';
  button.disabled=reduced.matches;
  button.textContent=reduced.matches?'Animación en pausa':userPaused?'Reanudar animación':'Pausar animación';
  button.setAttribute('aria-label',button.textContent);
  button.setAttribute('aria-pressed',String(userPaused||reduced.matches));
 }
 button.addEventListener('click',()=>{userPaused=!userPaused;sync();});
 document.addEventListener('visibilitychange',sync);
 small.addEventListener('change',render);reduced.addEventListener('change',render);
 const observer=new IntersectionObserver(([entry])=>{inView=entry.isIntersecting;sync();});observer.observe(root);
 addEventListener('pagehide',()=>animations.forEach(a=>a.pause()));addEventListener('pageshow',sync);
 render();
})();
