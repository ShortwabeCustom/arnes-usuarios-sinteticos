/* Local decorative video. User intent survives visibility changes. */
(() => {
 'use strict';
 const root=document.querySelector('[data-urban-hero]');
 if(!root)return;
 const video=root.querySelector('video'),button=root.querySelector('button');
 const label=button.querySelector('.urban-control-label'),icon=button.querySelector('.urban-control-icon');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),print=matchMedia('print');
 let intent='auto',visible=false,blocked=false,failed=false,hasFrame=false,request=0;
 const wantsMotion=()=>intent==='play'||(intent==='auto'&&!reduced.matches);
 const canRun=()=>wantsMotion()&&visible&&!document.hidden&&!print.matches&&!failed;
 function paint(){
  const playing=!video.paused&&!video.ended;
  root.dataset.motion=playing?'playing':blocked?'blocked':reduced.matches&&intent==='auto'?'reduced':'paused';
  root.dataset.frame=hasFrame&&!blocked?'video':'poster';
  const text=failed?'Vista estática':playing?'Pausar animación':'Reproducir animación';
  label.textContent=text;button.setAttribute('aria-label',text);
  button.setAttribute('aria-pressed',String(playing));
  icon.textContent=playing?'Ⅱ':'▷';button.disabled=failed;
 }
 async function sync(){
  const token=++request;
  if(!canRun()||blocked){video.pause();paint();return;}
  if(!video.paused){paint();return;}
  try{
   await video.play();
   if(token!==request)return;
   if(!canRun()){video.pause();paint();return;}
   blocked=false;paint();
  }catch(error){
   if(token!==request)return;
   if(error.name!=='AbortError'){blocked=true;hasFrame=false;}
   paint();
  }
 }
 // Source is attached only after disabling native autoplay when appropriate.
 // Playback is managed here so reduced motion cannot briefly autoplay at load.
 video.autoplay=false;video.muted=true;video.src=video.dataset.src;
 button.hidden=false;
 button.addEventListener('click',()=>{
  if(!video.paused){intent='pause';}else{intent='play';blocked=false;}
  sync();
 });
 video.addEventListener('playing',()=>{
  if(!canRun()){video.pause();return;}
  hasFrame=true;blocked=false;paint();
 });
 video.addEventListener('pause',paint);
 video.addEventListener('error',()=>{failed=true;hasFrame=false;paint();});
 reduced.addEventListener('change',()=>{
  if(reduced.matches){if(intent!=='pause')intent='auto';hasFrame=false;}
  sync();
 });
 print.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);
 new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;sync();},{threshold:0}).observe(root);
 addEventListener('pagehide',()=>{++request;video.pause();});addEventListener('pageshow',sync);
 paint();
})();
