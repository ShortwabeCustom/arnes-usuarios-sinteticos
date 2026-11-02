/* Original, separable editorial art. Oblique furniture and small profile figures. */
(() => {
 const palette={blue:'#3048bf',paper:'#f7f3ea',sage:'#b6c5ac',ink:'#293934',leaf:'#8ca590',terrain:'#e5ead8',light:'#edf0e4'};
 const colors=fill=>palette[fill]||fill;
 function figure(p){
  const dress=['dress','skirt'].includes(p.family), long=p.family==='long', coat=p.family==='coat';
  const seated=p.pose==='seated',sit=p.pose==='sit';
  const hair={coat:'M-3-36 Q-6-43-1-44 Q4-45 5-39 L1-39 L0-41 L-3-38Z',dress:'M-4-37 Q-6-43-2-44 Q3-47 5-41 L5-35 L1-34 L1-40 L-2-39Z',cap:'M-5-40 Q-5-45 0-45 Q4-45 5-41 L9-40 L8-39 L-5-39Z',jacket:'M-4-39 Q-7-42-3-43 Q-4-47 0-45 Q4-48 5-44 Q9-43 6-39 L2-40 L0-42Z',long:'M-4-39 Q-5-46 0-45 Q6-46 6-39 L6-33 L2-32 L0-40Z',skirt:'M-4-38 Q-5-44 0-44 Q5-44 6-38 L2-39 L0-41Z M-4-42 Q-9-43-6-47 Q-2-48-2-44Z',knit:'M-5-40 L-4-44 L-1-43 L1-46 L4-43 L6-42 L5-38 L1-40 L-1-41Z',short:'M-4-40 Q-2-46 3-43 L6-39 L3-37 L0-41Z'}[p.family];
  const head=`<g class="mc-head"><g transform="translate(0 -33) scale(.8) translate(0 33)"><path d="M-2-32 L-2-37 L3-37 L4-32" fill="var(--mc-skin)"/><path d="M-4-40 Q-2-45 3-41 L5-37 L7-36 L4-35 Q4-31 0-33 L-3-36Z" fill="var(--mc-skin)"/><path d="${hair}" fill="var(--mc-ink)"/></g></g>`;
  const leg=(side,x)=>`<g class="mc-leg mc-leg-${side}"><path d="M${x-2}-16 L${x+2}-15 L${x+1}-7 L${x-2}-7Z" fill="var(--mc-blue)"/><g class="mc-knee mc-knee-${side}"><path d="M${x-2}-8 L${x+1}-8 L${x+1}-1 L${x-1} 0Z" fill="${dress?'var(--mc-skin)':'var(--mc-blue)'}"/><path d="M${x-1}-1 L${x+2}-1 L${x+5} 1 L${x-2} 1Z" fill="var(--mc-ink)"/></g></g>`;
  let legs=leg('back',-2)+leg('front',4);
  if(seated)legs='<path d="M-4-20 L6-20 L15-11 L11-8 L1-14 L-4-14Z" fill="var(--mc-blue)"/><g class="mc-foot"><path d="M11-10 L15-11 L17 0 L14 1Z" fill="var(--mc-blue)"/><path d="M14 0 L18-1 L21 1 L14 2Z" fill="var(--mc-ink)"/></g>';
  if(sit)legs='<path d="M-5-15 Q-12-10-5-8 L9-8 L15-5 L18-7 L11-12 L1-14Z" fill="var(--mc-blue)"/>';
  const torso=dress?'<path d="M-3-32 Q-8-31-7-26 L-9-12 Q-1-8 9-13 L6-27 L3-32Z" fill="var(--mc-cloth)"/>':`<path d="M-3-32 Q-7-31-7-26 L${coat||long?-8:-5} ${coat||long?-10:-16} Q0 ${coat||long?-8:-14} 8 ${coat||long?-11:-16} L6-27 L3-32Z" fill="var(--mc-cloth)"/>`;
  const pattern=p.family==='knit'?'<path d="M-5-26 L5-27 M-5-23 L6-24 M-5-20 L6-21" fill="none" stroke="var(--mc-blue)" stroke-width=".7"/>':p.family==='skirt'?'<path d="M-4-21 L-5-13 M0-21 L0-12 M4-21 L5-13" fill="none" stroke="var(--mc-paper)" stroke-width=".6"/>':p.family==='coat'?'<path d="M0-30 L1-11 M-5-18 L-2-18 M3-18 L6-19" fill="none" stroke="var(--mc-blue)" stroke-width=".6"/>':p.family==='long'?'<path d="M-2-29 L1-23 L3-30 M1-23 L2-12" fill="none" stroke="var(--mc-paper)" stroke-width=".65"/>':'';
  const phone=['phone','show','walk'].includes(p.pose);
  let front=phone?'<g class="mc-phone-arm"><path d="M4-29 L8-22 L13-27" fill="none" stroke="var(--mc-cloth)" stroke-width="3.1"/><path d="M12-27 L14-29" stroke="var(--mc-skin)" stroke-width="2"/><path d="M12-33 L16-32 L15-27 L11-28Z" fill="var(--mc-ink)"/><path d="M13-32 L15-32 L14-29 L12-29Z" fill="var(--mc-paper)" stroke="none"/></g>':'<g class="mc-arm"><path d="M5-29 L9-23 L8-16" stroke="var(--mc-cloth)" stroke-width="3.1" fill="none"/><path d="M8-17 L8-14" stroke="var(--mc-skin)" stroke-width="2"/></g>';
  if(p.pose==='greet')front='<g class="mc-wave"><path d="M5-28 L11-24 L13-32" fill="none" stroke="var(--mc-cloth)" stroke-width="3"/><path d="M13-32 L13-36 M11-34 L13-33 L15-35" stroke="var(--mc-skin)" fill="none" stroke-width="1.5"/></g>';
  if(seated||sit)front='<path d="M5-28 L10-21 L4-19" stroke="var(--mc-cloth)" stroke-width="3" fill="none"/><path d="M4-19 L1-18" stroke="var(--mc-skin)" stroke-width="1.5"/>';
  const bag=p.pose==='bag'?'<path d="M-11-17 Q-11-22-7-22 Q-3-21-4-17 M-13-17 L-3-18 L-2-7 L-13-7Z" fill="var(--mc-paper)" stroke="var(--mc-blue)" stroke-width=".7"/>':'';
  return `<g class="mc-person-art" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="4" cy="3" rx="10" ry="2.5" fill="var(--mc-ink)" opacity=".07"/><g class="mc-pose" ${sit?'transform="translate(0 8)"':''}>${legs}<g class="mc-upper"><g class="mc-arm-back"><path d="M-5-29 L-10-22 L-8-14" fill="none" stroke="var(--mc-cloth)" stroke-width="3"/><path d="M-8-14 L-7-12" stroke="var(--mc-skin)" stroke-width="1.8"/></g>${torso}${pattern}${head}${front}${bag}</g></g></g>`;
 }
 const defs=`<defs>
 <pattern id="mc-lines" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><path d="M0 0 L0 5" stroke="#9baf9f" stroke-width=".7" opacity=".5"/></pattern>
 <pattern id="mc-dots" width="10" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r=".65" fill="#79977d" opacity=".5"/></pattern>
 <pattern id="mc-leaves" width="18" height="21" patternUnits="userSpaceOnUse" patternTransform="rotate(-15)"><path d="M8 16 L8 7 M8 11 Q1 10 3 5 Q9 4 8 11 M8 14 Q14 13 14 8 Q9 8 8 14" fill="none" stroke="#6b8d79" stroke-width=".65" opacity=".6"/></pattern>
 </defs>`;
 function tree(x,y,s=1,style=0,mobile=false){return `<g class="mc-tree${mobile?' mc-mobile-tree':''}" transform="translate(${x} ${y}) scale(${s})"><ellipse cx="18" cy="16" rx="33" ry="9" fill="#293934" opacity=".045" transform="rotate(15)"/><path d="M0 12 L1-47 M1-9 L-15-25 M1-24 L14-37" stroke="#6f8877" stroke-width="2" fill="none"/><g class="mc-canopy"><path d="M-30-28 Q-47-52-24-64 Q-20-86 0-75 Q24-88 34-66 Q55-55 36-36 Q30-17 13-24 Q-8-9-30-28Z" fill="${style?'#b6c7ae':'#9baf9f'}"/><path d="M-30-28 Q-47-52-24-64 Q-20-86 0-75 Q24-88 34-66 Q55-55 36-36 Q30-17 13-24 Q-8-9-30-28Z" fill="url(#${style?'mc-lines':'mc-leaves'})"/><path d="M1-23 L0-61 M1-42 L-17-53 M0-48 L17-61" fill="none" stroke="#6b8873" stroke-width="1" opacity=".65"/></g></g>`;}
 function bench(x,y){return `<g transform="translate(${x} ${y})" class="mc-bench"><path d="M-13-11 L53 5 L65-2 L0-18Z" fill="#c8bd9f"/><path d="M-13-11 L53 5 L53 9 L-13-7Z" fill="#acaa8f"/><path d="M-9-9 L-9 3 M48 5 L48 16" stroke="#7b8473" stroke-width="2"/><path d="M-10-22 L56-6 L55-13 L-11-29Z" fill="#d5ccae"/><path d="M-7-25 L53-10" fill="none" stroke="#b6ae91"/></g>`;}
 function ground(mobile){return mobile?`<g class="mc-ground">
 <path d="M39 93 Q52 45 117 50 Q178 48 176 90 Q165 126 105 127 Q48 138 39 93Z" fill="#e5ead8"/>
 <path d="M258 55 Q316 28 382 75 Q431 119 374 142 Q324 165 274 124 Q237 98 258 55Z" fill="#e5ead8"/>
 <path d="M55 195 Q62 151 130 152 Q211 149 253 189 Q286 233 223 251 Q172 270 107 245 Q47 235 55 195Z" fill="#e5ead8"/>
 <path d="M290 210 Q317 157 379 172 Q427 183 415 232 Q400 268 342 262 Q301 253 290 210Z" fill="#e5ead8"/>
 <path d="M57 209 Q105 181 143 207 Q160 233 209 234" fill="none" stroke="#f7f3ea" stroke-width="12"/>
 <path d="M288 65 Q311 37 355 71 Q321 91 293 84Z" fill="url(#mc-lines)"/>
 </g>`:`<g class="mc-ground">
 <path d="M72 152 Q55 107 105 87 Q170 60 240 97 Q272 114 282 161 Q289 202 246 232 Q208 260 221 291 Q243 324 282 341 Q319 367 299 402 Q278 435 318 452 Q389 458 399 501 Q398 551 331 566 Q254 590 196 550 Q159 523 171 480 Q184 445 148 432 Q61 418 53 361 Q42 317 93 284 Q139 257 122 221 Q90 192 72 152Z" fill="#e5ead8"/>
 <path d="M382 74 Q415 43 467 72 Q500 87 541 94 Q628 87 661 139 Q688 183 652 229 Q628 256 645 286 Q716 305 707 370 Q704 419 668 434 Q665 455 704 460 Q749 478 723 514 Q700 545 652 533 Q618 523 613 490 Q605 462 564 451 Q518 437 476 471 Q451 501 480 524 Q502 541 486 551 Q439 564 408 533 Q383 506 401 468 Q421 431 477 408 Q502 394 483 368 Q451 323 494 283 Q520 257 489 231 Q436 207 448 164 Q463 138 420 132 Q368 132 367 107 Q363 89 382 74Z" fill="#e5ead8"/>
 <path d="M78 159 Q155 112 213 166 Q269 219 194 277 Q141 323 211 352 Q273 373 230 420 Q195 462 253 501 Q281 525 339 539" fill="none" stroke="#f7f3ea" stroke-width="21"/>
 <path d="M398 96 Q452 118 495 167 Q533 211 584 238 Q640 268 591 312 Q538 362 596 389 Q664 417 660 485" fill="none" stroke="#f7f3ea" stroke-width="24"/>
 <path d="M155 328 Q203 329 254 306" fill="none" stroke="#f7f3ea" stroke-width="12"/>
 <path d="M221 291 Q345 252 494 283" fill="none" stroke="#f7f3ea" stroke-width="18"/>
 <path d="M298 475 Q374 433 445 471" fill="none" stroke="#f7f3ea" stroke-width="17"/>
 <path d="M471 155 Q492 117 541 124 Q566 143 540 161 Q505 176 471 155Z" fill="url(#mc-lines)"/>
 <path d="M80 373 Q95 341 132 362 Q158 390 123 401 Q92 407 80 373Z" fill="url(#mc-dots)"/>
 <path d="M261 451 Q308 442 343 468 Q310 486 279 473Z" fill="url(#mc-dots)"/>
 </g>`;}
 function environment(mobile){return ground(mobile)+(mobile?
 tree(73,84,.52,0)+tree(375,100,.48,1)+tree(163,204,.44,1)+bench(325,219):
 tree(211,121,.72,1)+tree(116,321,.58,0)+tree(622,162,.7,0)+tree(367,100,.4,1)+tree(649,324,.7,1)+tree(218,481,.5,0)+tree(688,470,.45,1)+bench(543,350)+`<g transform="translate(284 502)"><path d="M-26-1 L0-16 L30 2 L3 17Z" fill="#d9e7ed"/><path d="M-21 0 L0-12 L25 2 M-12 6 L11-7" fill="none" stroke="#f7f3ea" stroke-width="2"/><ellipse cx="0" cy="0" rx="4" ry="2" fill="#f7f3ea"/></g>`)+
 (mobile?'<path d="M150 181 Q140 169 145 160 Q154 163 152 175 M156 183 Q164 169 173 175 Q170 185 156 183" fill="#a4b99d"/>':'<g fill="#9baf9f"><path transform="translate(18 64)" d="M220 309 Q201 294 208 281 Q226 284 225 304 M228 312 Q230 292 246 295 Q247 309 228 312Z"/><path d="M511 501 Q515 485 526 486 Q529 499 511 501 M509 499 Q491 492 495 481 Q509 479 509 499Z"/><path d="M176 174 Q167 167 171 158 Q182 159 180 174 M180 176 Q189 164 196 170 Q195 181 180 176"/></g>');}
 window.MicrocosmosArt={figure,defs,environment,palette,colors};
})();
