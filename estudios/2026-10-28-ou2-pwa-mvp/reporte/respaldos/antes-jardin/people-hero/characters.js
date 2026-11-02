/* Small original editorial figures, with independently articulated knees and arms. */
(() => {
 const walkers=Array.from({length:18},(_,i)=>({
  id:i===13?'protagonist':`person-${i+1}`,layer:i<8?'back':'front',
  direction:i<8?-1:1,duration:i===13?30:i<8?70:54,
  scale:i<8?.66+(i%3)*.06:.88+(i%4)*.06,y:i<8?60+(i%3)*4:96+(i%2),
  hair:['part','bob','curl','bun','cap','short'][i%6],outfit:['coat','shirt','dress','knit','jacket'][i%5],
  ink:i%3===0?'#174f3f':'#234e61',fill:['#f7f3ea','#d9e7ed','#dbe9dc','#eee9de'][i%4],
  build:[.92,1.04,.87,1.12,1][i%5],step:.74+(i%5)*.065,
  phone:i%3!==1,hero:i===13,variant:i,
  density:(i<8?i<2:i<11||i===13)?'all':(i<8?i<5:i<15)?'tablet':'desktop'
 }));
 function character(p){
  const v=p.variant,skirt=p.outfit==='dress',coat=p.outfit==='coat';
  const hair={part:'M39 31 Q31 14 45 12 Q59 9 62 23 L57 26 L54 19 Q46 27 39 24Z',bob:'M34 39 Q28 13 43 12 Q59 9 61 27 L64 44 L54 46 L51 23 L41 28 L43 43Z',curl:'M36 29 Q27 26 32 20 Q28 12 36 12 Q35 5 43 9 Q49 2 54 10 Q63 6 64 16 Q71 20 62 27 L55 24 L53 18 L40 23Z',bun:'M36 29 Q29 19 38 14 Q47 7 56 17 L59 25 L50 21 L39 27Z M39 14 Q28 13 31 6 Q35 0 42 7 Q48 9 43 15Z',cap:'M31 24 Q29 11 44 10 Q58 8 61 21 L72 24 L71 27 L32 27Z',short:'M36 29 L31 18 L37 11 L43 14 L49 9 L58 14 L62 23 L54 24 L51 18 L39 24Z'}[p.hair];
  const leg=(side,x)=>`<g class="leg leg-${side}"><path d="M${x-6} 108 L${x+7} 108 L${x+4} 145 L${x-5} 145Z" fill="${skirt?'var(--paper)':'var(--cloth)'}"/><g class="shin shin-${side}"><path d="M${x-5} 140 L${x+4} 140 L${x+2} 176 L${x-4} 176Z" fill="${skirt?'var(--paper)':'var(--cloth)'}"/><path d="M${x-5} 173 L${x+3} 174 Q${x+7} 180 ${x+16} 179 L${x+17} 183 L${x-6} 183Z" fill="var(--ink)"/></g></g>`;
  const details=p.outfit==='knit'?'<path d="M31 69 L60 68 M30 77 L61 76 M30 85 L62 84 M31 93 L63 92" stroke-width="2.3"/>':p.outfit==='shirt'?'<path d="M39 49 L45 58 L51 50 M45 59 L48 106 M51 69 L60 68 L59 79 L52 79Z"/>':coat?'<path d="M38 48 L33 60 L45 72 L49 58 L59 66 L55 49 M45 71 L47 120 M30 96 L40 97 M53 97 L63 96"/>':'<path d="M38 49 Q45 58 55 49 M31 103 L63 103"/>';
  const arm=p.phone?`<g class="phone-arm"><path d="M57 58 Q65 72 67 80 L78 65 L83 70 Q74 94 65 93 Q55 88 49 70" fill="var(--cloth)"/><path d="M77 68 L78 60 Q82 55 85 62 L84 71Z" fill="var(--paper)"/><g class="phone"><path d="M76 48 L86 50 L83 66 L73 64Z" fill="var(--ink)"/><path d="M78 51 L83 52 L81 61 L76 60Z" fill="var(--paper)" stroke="none"/><g class="phone-message"><path d="M78 34 L89 34 M81 29 L88 27 M80 39 L86 41" fill="none" stroke="var(--green)"/></g></g></g>`:`<g class="arm arm-front"><path d="M58 58 Q65 77 62 97 L57 119 L51 117 L54 93 L49 68" fill="var(--cloth)"/><path d="M51 115 Q47 127 53 129 Q59 128 57 117" fill="var(--paper)"/>${v%2?'<g class="bag"><path d="M46 129 Q47 119 54 121 Q61 122 60 130 M40 130 L66 128 L68 151 L40 152Z" fill="var(--cloth)"/></g>':''}</g>`;
  return `<svg viewBox="0 0 100 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><ellipse cx="48" cy="187" rx="24" ry="2" fill="var(--ink)" opacity=".07"/><g class="body" stroke="var(--ink)" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round">
   ${leg('back',40)}${leg('front',54)}
   <g class="upper-body">
   <g class="arm arm-back"><path d="M33 57 Q23 78 28 102 L31 119 L36 118 L35 99 L42 66" fill="var(--cloth)"/><path d="M31 117 Q28 126 34 128 Q40 126 36 117" fill="var(--paper)"/></g>
   <path d="M39 47 Q29 50 27 62 L${coat?23:29} ${coat?125:skirt?139:110} Q47 ${coat?130:skirt?145:115} ${skirt?72:67} ${coat?123:skirt?137:109} L61 62 Q57 49 51 47Z" fill="${skirt?'var(--ink)':'var(--cloth)'}"/>
   <g fill="none" stroke="${skirt?'var(--paper)':'var(--ink)'}">${details}${coat?'<path d="M28 114 L32 115 M29 118 L33 119" stroke-width=".7"/>':''}</g>
   <g class="head"><path d="M41 36 L39 49 Q46 55 52 48 L50 37" fill="var(--paper)"/>
   ${['bob'].includes(p.hair)?`<path d="${hair}" fill="var(--ink)"/>`:''}
   <path d="M37 24 Q40 13 52 19 Q58 23 58 30 L64 34 L58 36 Q58 47 49 45 Q40 43 37 34Z" fill="var(--paper)"/><path d="${hair}" fill="var(--ink)"/>
   <path d="M39 31 Q33 27 35 34 Q37 38 41 36" fill="var(--paper)"/>
   <path d="M52 28 L56 29 M54 39 L58 39" fill="none"/><path class="eyes" d="M55 32 L56 32" stroke-width="1.8"/>
   ${v%4===0?'<path d="M49 29 L59 30 L59 35 L50 34Z M49 31 L39 29" fill="none" stroke-width=".8"/>':''}
   </g>${arm}
   ${v%4===2?'<path d="M29 57 Q14 59 17 89 L27 94 L32 65 M23 60 L19 87" fill="var(--cloth)"/>':''}
   </g></g></svg>`;
 }
 window.PeopleHeroArt={walkers,character};
})();
