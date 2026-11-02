/* Evidence is rendered from the study's local records; no simulated media. */
(() => {
  'use strict';
  const pause = root => root?.querySelectorAll('video').forEach(v => v.pause());
  function render(kind, value, api) {
    const {el,link,url,table}=api;
    const box=el('div','evidence-view');
    const a=(text,path,bypass=false)=>link(text,url(path),bypass);
    const note=text=>el('p','ev-note',text);
    const image=(src,alt,caption)=>{const f=el('figure','ev-figure'),im=el('img');im.src=url(src);im.alt=alt;im.loading='lazy';f.append(im,el('figcaption','',caption));return f;};
    const disclosure=(title,build)=>{const d=el('details','ev-disclosure');d.append(el('summary','',title));const body=el('div','ev-disclosure-body');d.append(body);let ready=false;d.addEventListener('toggle',()=>{if(d.open&&!ready){body.append(build());ready=true;}if(!d.open)pause(body);});return d;};
    const video=(v,sid)=>{
      const wrap=el('section','ev-recording');if(!v){wrap.append(note('Esta sesión no tiene una grabación vinculada. Consulta sus pasos y capturas.'));return wrap;}
      const player=el('video','ev-video');player.controls=true;player.preload='none';player.playsInline=true;player.setAttribute('aria-label','Grabación de la sesión sintética '+sid);if(v.poster)player.poster=url(v.poster);player.src=url(v.src);
      player.addEventListener('play',()=>document.querySelectorAll('video').forEach(other=>{if(other!==player)other.pause();}));
      const minutes=Math.floor((v.seconds||0)/60),seconds=Math.floor((v.seconds||0)%60);
      wrap.append(player,note(`Grabación vinculada a ${sid}${v.seconds ? ' · '+minutes+':'+String(seconds).padStart(2,'0') : ''}. ${v.audio===false?'Sin pista de audio. ':''}Usa los controles para reproducir y avanzar. El número de paso no equivale a un segundo del video.`));
      const fallback=note('Si el formato no se reproduce en tu navegador, abre el archivo o consulta el registro escrito de la sesión.');
      player.addEventListener('error',()=>{fallback.textContent='No se pudo reproducir el video aquí. Abre la grabación original o consulta las capturas y los pasos de la sesión.';fallback.setAttribute('role','status');});
      wrap.append(fallback,a('Abrir grabación original ↗',v.src,true),el('span','',' · '),a('Leer los pasos y pensamientos registrados ↗',`lecturas/${sid}.html`));return wrap;
    };
    const heatmap=m=>{
      const h=el('section','ev-map');
      h.append(note('Mapa de acciones del arnés en sesiones sintéticas. Agrupa toques y escritura sobre la primera captura de esta pantalla. Las acciones repetidas cuentan y las marcas pueden superponerse. No mide mirada, lectura ni atención.'));
      const stats=el('dl','ev-stats');[[m.actions,'acciones registradas'],[m.sessions,'sesiones que aportan acciones'],[m.responded,'con respuesta visible'],[m.unconfirmed,'sin respuesta confirmada']].forEach(([n,t])=>{const d=el('div');d.append(el('dt','',t),el('dd','',n));stats.append(d);});h.append(stats);
      h.append(image(m.image,'Mapa de acciones sobre la pantalla '+m.screen,'Verde: respuesta visible. Rojo: sin respuesta confirmada. Una respuesta visible no implica éxito, comprensión ni consentimiento.'));
      h.append(disclosure('Consultar las '+m.actions+' acciones y sus sesiones',()=>table(['Sesión','Paso','Acción','Respuesta'],m.rows.map(r=>[a(r.sid,`lecturas/${r.sid}.html`),r.step,r.action==='escribir'?'Escribir':'Tocar',r.response==='si'?'Visible':`Sin confirmar (${r.response||'sin registro'})`]))));return h;
    };
    if(kind==='evidence-case'){
      box.append(el('p','ev-kicker',`${value.topic} · ${value.sid} · paso ${value.step}`));
      box.append(image(value.image,`Pantalla ${value.screen}, paso ${value.step} de ${value.sid}`,`Captura de ${window.ReportReaderConfig.material} durante la sesión ${value.sid}.`));
      box.append(el('h3','','Qué muestra la pantalla'),el('p','',value.observation),el('h3','','Qué expresó el perfil sintético'));
      const quote=el('blockquote');quote.append(el('p','',value.thought));box.append(quote);
      if(value.nextThought){box.append(el('p','ev-kicker','En el siguiente paso'),el('blockquote','',value.nextThought));}
      box.append(note(value.limit));
      box.append(disclosure('Ver la grabación de esta sesión',()=>video(value.video,value.sid)));
      if(value.map)box.append(disclosure('Explorar el mapa de toques de esta pantalla',()=>{const m=el('div');m.append(note(value.map_note),heatmap(value.map));return m;}));
      box.append(el('h3','','Lectura UX y mejora propuesta'),el('p','ev-kicker',value.heuristic),el('p','',value.interpretation));
      if(value.expert.length)box.append(disclosure('Contrastar con la evaluación heurística del estudio',()=>{const e=el('div');e.append(note('Evaluación asistida por IA: tres evaluaciones independientes. Estos criterios corresponden a la pantalla completa; no prueban por sí solos la causa del comportamiento de una sesión.'));for(const x of value.expert){e.append(el('h4','',x.criterio+' · '+x.nombre_criterio),el('p','',`${x.evaluadores}/${x.de} evaluaciones señalan el criterio · severidad media ${x.severidad_media}/4.`));const list=el('ul');x.problemas.forEach(p=>list.append(el('li','',typeof p==='string'?p:JSON.stringify(p))));e.append(list);}e.append(a('Consultar la evaluación íntegra ↗','lecturas/auditoria.html'));return e;}));
      else box.append(note('La lectura UX anterior es una interpretación editorial de esta evidencia. La evaluación original no señaló criterios para este momento.'));
      box.append(a('Leer la sesión completa ↗',value.sessionPage),el('span','',' · '),a('Explorar todas las evidencias ↗','lecturas/evidencias.html'));
    }else if(kind==='heatmap')box.append(heatmap(value));
    else if(kind==='evidence-library'){
      box.append(note(`Capturas y grabaciones de ${window.ReportReaderConfig.material} recorrido por perfiles sintéticos. Los pensamientos proceden de simulaciones; los mapas muestran acciones del arnés. No son sesiones con clientes reales.`));
      const filters=el('div','ev-filters'),modes=el('div','ev-modes');modes.setAttribute('aria-label','Tipo de evidencia');
      let mode='cases';const buttons=[];
      const list=el('div','ev-library-grid'),status=el('p','ev-result-count');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
      const form=el('div','ev-filter-fields'),searchLabel=el('label','','Buscar evidencia'),search=el('input');search.type='search';search.placeholder='Tema, perfil o pantalla…';searchLabel.append(search);
      const selectLabel=el('label','','Tramo del recorrido'),select=el('select');[['','Todos los tramos'],...window.ReportReaderConfig.tareas.map((t,i)=>[t.id,`${String(i+1).padStart(2,'0')} · ${t.nombre}`])].forEach(([v,t])=>{const o=el('option','',t);o.value=v;select.append(o);});selectLabel.append(select);form.append(searchLabel,selectLabel);
      const norm=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
      function update(){pause(list);list.replaceChildren();selectLabel.hidden=mode==='maps';buttons.forEach(([key,b])=>b.setAttribute('aria-pressed',String(key===mode)));const q=norm(search.value);const items=value[mode].filter(x=>(mode==='maps'||!select.value||x.task===select.value)&&norm([x.title,x.topic,x.name,x.id,x.sid,x.task].filter(Boolean).join(' ')).includes(q));status.textContent=`${items.length} ${mode==='cases'?'hallazgos':mode==='sessions'?'sesiones':'mapas'} disponibles`;
        for(const x of items){const card=el('article','ev-library-card');
          if(mode==='cases'){card.append(image(x.image,x.title,`${x.sid} · paso ${x.step}`),el('p','ev-kicker',x.topic),el('h3','',x.title),a('Abrir evidencia ↗',`lecturas/${x.id}.html`));}
          else if(mode==='maps'){card.append(el('p','ev-kicker','Mapa de acciones'),el('h3','',x.screen),el('p','',`${x.actions} acciones · ${x.sessions} sesiones`),a('Ver mapa y leyenda ↗',`lecturas/${x.id}.html`));}
          else{card.append(el('p','ev-kicker',`${x.task} · corrida ${x.run}`),el('h3','',x.title),el('p','',`${x.id} · ${x.steps} registros de paso`),disclosure('Reproducir grabación',()=>video(x.video,x.id)),a('Explorar sesión y capturas ↗',x.page));}list.append(card);
        }if(!items.length)list.append(note('No hay coincidencias. Prueba otro nombre, pantalla o tramo.'));
      }
      [['cases',`Hallazgos · ${value.cases.length}`],['sessions',`Sesiones y videos · ${value.sessions.length}`],['maps',`Mapas de toques · ${value.maps.length}`]].forEach(([key,title])=>{const b=el('button','',title);b.type='button';b.onclick=()=>{mode=key;update();};buttons.push([key,b]);modes.append(b);});
      search.addEventListener('input',update);select.addEventListener('change',update);filters.append(modes,form);box.append(filters,status,list);update();
    }else return null;
    return box;
  }
  window.ReportEvidence={render,pause};
})();
