(() => {
  'use strict';
  const base = new URL('../../', document.currentScript.src);
  const manifest = window.ReportReaderManifest;
  const data = window.ReportReaderData;
  const config = window.ReportReaderConfig;
  const mainFile = config.principal;
  const routes = new Map(), loads = new Map();
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const labels = {n_sesiones:'Sesiones sintéticas', resultados:'Resultados por tramo', wcag_258:'Tamaño de las áreas de interacción', primer_toque:'Primer toque', robustez:'Estabilidad entre corridas', metricas:'Métricas', embudo:'Resultados por tarea (bases independientes)', momentos:'Momentos del recorrido', sesiones:'Sesiones', completa:'Completa el tramo', pasos:'Pasos', ces:'Facilidad percibida (CES)', costo_usd:'Costo registrado en USD', tokens:'Tokens registrados', crudo:'Registros completos de evaluación', consolidado:'Observaciones consolidadas', positivos:'Hallazgos positivos', confianza:'Confianza', friccion:'Fricción', sabe_donde_va:'Orientación en el flujo', tiempo_estimado_s:'Tiempo estimado por el modelo (segundos)', espera_sistema_s:'Espera real del sistema (segundos)', tarea:'Tramo', integrante:'Perfil sintético', resultado:'Resultado', nombre:'Nombre del perfil', perfil:'Perfil', fecha:'Fecha', primera_impresion:'Primera impresión', que_miras_primero:'Qué llamó la atención primero', interpretacion:'Cómo interpreta la pantalla', pensamiento:'Pensamiento del perfil sintético', intencion:'Qué intenta hacer', accion:'Acción', opcion:'Opción elegida', progreso:'Comprensión del avance', recorte:'Origen del recorte de imagen', zonas_detalle:'Áreas de interacción detectadas', modelo_id:'Modelo utilizado', captura:'Archivo de la captura', marcas:'Imagen con áreas marcadas', inicio:'Inicio de la sesión', corrida:'Repetición', integrante:'Perfil sintético', recomendaciones:'Recomendaciones', problemas:'Problemas identificados', reescrituras:'Redacciones propuestas', evaluadores:'Evaluaciones que señalan el criterio', severidad_media:'Severidad media (0–4)', consenso:'Coincidencia entre evaluaciones'};
  const outcomes = {exito:'Completa sin fricción', exito_con_friccion:'Completa con fricción', abandono:'Abandona', fallo_max_pasos:'No completa · límite de pasos'};
  const label = key => labels[key] || key.replace(/_/g,' ').replace(/^./, c=>c.toUpperCase());
  const el = (tag, cls, text) => {const n=document.createElement(tag); if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;};
  const url = relative => new URL(relative,base).href;
  for(const [id,m] of Object.entries(manifest)) {
    routes.set(url(m.page),id);
    if(m.original && m.kind!=='stage' && !routes.has(url(m.original)))routes.set(url(m.original),id);
  }
  function readingURL(href){const resolved=new URL(href,base).href;const id=routes.get(resolved);return id?url(manifest[id].page):resolved;}
  function link(text,href,bypass=false) {const a=el('a','',text);a.href=readingURL(href);if(bypass){a.dataset.readerBypass='';a.target='_blank';a.rel='noopener';}return a;}
  function load(id) {
    if(Object.prototype.hasOwnProperty.call(data,id))return Promise.resolve(data[id]);
    if(!loads.has(id)) loads.set(id,new Promise((resolve,reject)=>{const s=el('script');s.src=url(manifest[id].data);s.onload=()=>resolve(data[id]);s.onerror=()=>{loads.delete(id);s.remove();reject(new Error('No se pudo cargar el documento local.'));};document.head.append(s);}));
    return loads.get(id);
  }
  function scalar(value){return value===null?'Sin registro':typeof value==='boolean'?(value?'Sí':'No'):String(value);}
  function objectTree(value, depth=0) {
    if(value===null || typeof value!=='object')return el('p','',scalar(value));
    const box=el('div','reader-tree');const list=el('dl','reader-properties');box.append(list);
    for(const [key,item] of Object.entries(value)) {
      const name=Array.isArray(value)?(item && (item.sesion||item.id||item.pantalla||item.nombre) || `Registro ${Number(key)+1}`):label(key);
      if(item && typeof item==='object') {
        const details=el('details');const n=Object.keys(item).length;
        details.append(el('summary','',`${name} · ${n} ${Array.isArray(item)?'registros':'campos'}`));
        const branch=el('div','reader-branch');details.append(branch);let filled=false;
        details.addEventListener('toggle',()=>{if(details.open&&!filled){filled=true;branch.append(objectTree(item,depth+1));}});
        box.append(details);
      } else {const row=el('div','reader-property');row.append(el('dt','',name),el('dd','',scalar(item)));list.append(row);}
    }
    return box;
  }
  function table(headers,rows){const wrap=el('div','reader-table-wrap'),t=el('table'),head=el('thead'),tr=el('tr');headers.forEach(h=>tr.append(el('th','',h)));head.append(tr);t.append(head);const body=el('tbody');for(const row of rows){const r=el('tr');for(const cell of row){const d=el('td');d.append(cell instanceof Node?cell:document.createTextNode(String(cell)));r.append(d);}body.append(r);}t.append(body);wrap.append(t);return wrap;}
  function note(){return el('div','reader-note','Estos conteos describen corridas de perfiles sintéticos en tramos separados. No representan una tasa de conversión de clientes ni testimonios de participantes reales.');}
  function summary(count,title,description){const b=el('div','reader-summary');b.append(el('strong','',count),el('h3','',title));if(description)b.append(el('p','',description));return b;}
  function sessionTable(sessions) {return table(['Sesión sintética','Resultado','Pasos'],sessions.map(s=>[link(s.sesion,url(`lecturas/${s.sesion}.html`)),outcomes[s.resultado]||s.resultado,s.pasos]));}
  function inline(text,container,sourceBase){
    const re=/(`[^`]+`|\*\*[^*]+\*\*|\[([^\]]+)\]\(([^)]+)\))/g;let offset=0,m;
    while((m=re.exec(text))){container.append(document.createTextNode(text.slice(offset,m.index)));if(m[0][0]==='`')container.append(el('code','',m[0].slice(1,-1)));else if(m[0].startsWith('**'))container.append(el('strong','',m[0].slice(2,-2)));else{let href;try{href=new URL(m[3],sourceBase); }catch{}if(href && ['file:','http:','https:'].includes(href.protocol))container.append(link(m[2],href.href));else container.append(document.createTextNode(m[2]));}offset=re.lastIndex;}container.append(document.createTextNode(text.slice(offset)));
  }
  function markdown(text,sourceBase,skipDocumentTitle=false) {
    const box=el('div');text=text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/,'');const lines=text.split(/\r?\n/);let list=null;
    for(let i=0;i<lines.length;i++){const line=lines[i];if(!line.trim()){list=null;continue;}
      if(line.startsWith('```')){const code=[];while(++i<lines.length&&!lines[i].startsWith('```'))code.push(lines[i]);box.append(el('pre','',code.join('\n')));continue;}
      if(line.includes('|') && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(lines[i+1]||'')){const cells=s=>s.trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim());const heads=cells(line);i+=2;const rows=[];while(i<lines.length&&lines[i].includes('|')){rows.push(cells(lines[i]).map(c=>{const span=el('span');inline(c,span,sourceBase);return span;}));i++;}i--;const t=table(heads,rows);box.append(t);continue;}
      const heading=line.match(/^(#{1,6})\s+(.+)/);if(heading){if(skipDocumentTitle&&heading[1].length===1){skipDocumentTitle=false;continue;}const h=el('h'+Math.min(heading[1].length+1,6));inline(heading[2],h,sourceBase);box.append(h);list=null;continue;}
      const bullet=line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)/);if(bullet){if(!list){list=el('ul');box.append(list);}const li=el('li');inline(bullet[1],li,sourceBase);list.append(li);continue;}
      if(/^---+$/.test(line)){box.append(el('hr'));continue;}
      const p=el('p');inline(line,p,sourceBase);box.append(p);list=null;
    }return box;
  }
  function htmlDocument(raw,m) {
    const box=el('div','reader-document');box.innerHTML=raw; // Generated by the local allow-list sanitizer, never raw source HTML.
    const firstTitle=box.querySelector('h1,h2');if(firstTitle?.textContent===m.title)firstTitle.remove();
    const originalBase=new URL(m.base,base);
    box.querySelectorAll('[href]').forEach(a=>{const original=a.getAttribute('href');if(original.startsWith('#')){const key=original.slice(1);if(manifest[key])a.href=url(manifest[key].page);else a.dataset.readerLocal=key;}else a.href=readingURL(new URL(original,originalBase).href);});
    box.querySelectorAll('img[src]').forEach(img=>{img.src=new URL(img.getAttribute('src'),originalBase).href;img.loading='lazy';});
    box.querySelectorAll('table').forEach(t=>{const w=el('div','reader-table-wrap');t.before(w);w.append(t);});
    return box;
  }
  function renderContent(id,value) {
    const m=manifest[id],box=el('div','reader-body');
    if(window.ReportInsights && ['sintesis','tecnico','auditoria'].includes(id)){box.append(window.ReportInsights.render(id,value,{el,link,url,table,objectTree}));}
    else if(window.ReportEvidence && ['evidence-case','evidence-library','heatmap'].includes(m.kind)){
      box.append(window.ReportEvidence.render(m.kind,value,{el,link,url,table,objectTree,load}));
    } else if(m.kind==='stage') {
      box.append(summary(`${value.complete}/${value.total}`,value.heading,value.description),note(),el('h3','',`Las ${value.total} corridas de este tramo`),sessionTable(value.sessions));
      box.append(link('Consultar todos los datos agregados ↗',url('lecturas/datos-agregados.html')));
    } else if(m.kind==='aggregate') {
      box.append(summary(`${value.metricas.sesiones.filter(s=>s.completa).length}/${value.n_sesiones}`,'Llegan al final de su tramo',`${config.tareas.length} tramos evaluados de forma independiente.`),note());
      box.append(table(['Tramo','Completan','Base'],config.tareas.map(t=>{const ss=value.metricas.sesiones.filter(s=>s.tarea===t.id);return[link(t.nombre,url(`lecturas/tramo-${t.id}.html`)),ss.filter(s=>s.completa).length,ss.length];})),el('h3','','Explorar el registro completo'),objectTree(value));
    } else if(m.kind==='session') {
      box.append(summary(outcomes[value.resultado]||value.resultado,`${value.pasos.length} pasos registrados`,`${value.nombre} · ${value.tarea} · corrida ${value.corrida}`),note());
      if(value.video){const d=el('details');d.append(el('summary','','Ver la grabación de esta sesión'));const wrap=el('div','ev-disclosure-body');d.append(wrap);let ready=false;d.addEventListener('toggle',()=>{if(d.open&&!ready){ready=true;const v=el('video','ev-video');v.controls=true;v.playsInline=true;v.preload='none';v.src=url('../'+value.video);v.setAttribute('aria-label','Grabación de '+id);if(value.pasos[0]?.captura)v.poster=url('../'+value.pasos[0].captura);v.addEventListener('play',()=>document.querySelectorAll('video').forEach(other=>{if(other!==v)other.pause();}));wrap.append(v,el('p','ev-note','Grabación vinculada a la sesión. Los pasos y pensamientos escritos a continuación permiten revisar su contenido. Si el video no se reproduce, abre el archivo original.'),link('Abrir grabación original ↗',url('../'+value.video),true));}if(!d.open)window.ReportEvidence?.pause(wrap);});box.append(d);}
      const overview=el('div','insight-stats');for(const [caption,text] of [['Perfil sintético',value.nombre],['Tramo',config.tareas.find(t=>t.id===value.tarea)?.nombre||value.tarea],['Repetición',`${value.corrida} de ${config.corridas}`]]){const item=el('div');item.append(el('span','',caption),el('strong','',text));overview.append(item);}box.append(overview,el('p','reader-note','Cada paso reúne lo que vio, pensó e hizo el perfil sintético. La confianza va de 0 a 100; la fricción registra la dificultad declarada. Son respuestas de simulación.'),el('h3','','Recorrido de la sesión'));
      for(const step of value.pasos){const row=el('section','reader-session-step');row.append(el('header','',`PASO ${String(step.n).padStart(2,'0')} / ${step.pantalla}`));const p=step.perfil||{};
        if(p.pensamiento){row.append(el('p','reader-step-label','Pensamiento del perfil sintético'));const q=el('blockquote');q.append(el('p','',p.pensamiento));row.append(q);}
        if(p.primera_impresion)row.append(el('p','reader-step-label','Primera impresión'),el('p','',p.primera_impresion));
        if(p.progreso?.texto)row.append(el('p','reader-step-label','Comprensión del avance'),el('p','',p.progreso.texto));
        if(p.accion?.texto)row.append(el('p','reader-step-label','Acción elegida'));
        if(p.accion?.texto)row.append(el('p','',p.accion.texto));
        row.append(el('p','reader-status',`Confianza: ${p.confianza ?? 'sin registro'}/100 · Fricción registrada: ${p.friccion ?? 'sin registro'}`));
        const d=el('details');d.append(el('summary','','Ver pantalla y detalle del paso'));const b=el('div','reader-branch');d.append(b);let ready=false;d.addEventListener('toggle',()=>{if(d.open&&!ready){ready=true;if(step.captura){const im=el('img');im.src=url('../'+step.captura);im.alt=`Pantalla ${step.pantalla} en el paso ${step.n}`;im.loading='lazy';im.style.maxWidth='300px';b.append(im);}b.append(objectTree(step));}});row.append(d);box.append(row);
      }
      const full=el('details');full.append(el('summary','','Ficha completa de la sesión'));const b=el('div','reader-branch');full.append(b);let filled=false;full.addEventListener('toggle',()=>{if(full.open&&!filled){filled=true;b.append(objectTree(value));}});box.append(full);
    } else if(m.kind==='markdown')box.append(markdown(value,new URL(m.base,base),id==='protocolo'));
    else if(m.kind==='html')box.append(htmlDocument(value,m));
    else box.append(objectTree(value));
    return box;
  }
  function toolbar(standalone=false){const bar=el('div','reader-toolbar'),brand=el('div');brand.append(el('strong','',`${config.marca} / Biblioteca del estudio`),el('small','',`Investigación sintética · ${config.fecha}`));bar.append(brand);const tools=el('div','reader-tools');
    if(standalone){const home=link('←',url(mainFile));home.className='reader-tool';home.dataset.readerBypass='';home.setAttribute('aria-label','Volver al reporte');tools.append(home);}
    else {const back=el('button','reader-tool','←');back.type='button';back.dataset.readerBack='';back.setAttribute('aria-label','Volver a la lectura anterior');back.hidden=true;back.onclick=goBack;const close=el('button','reader-tool','×');close.type='button';close.setAttribute('aria-label','Cerrar lectura');close.onclick=closeSheet;tools.append(back,close);}
    bar.append(tools);return bar;
  }
  let sheet=null,scroll=null,opener=null,history=[],generation=0,oldOverflow='',closeTimer;
  function buildSheet(){sheet=el('dialog','reader-sheet');sheet.setAttribute('aria-labelledby','reader-title');sheet.append(toolbar());scroll=el('div','reader-scroll');sheet.append(scroll);document.body.append(sheet);
    sheet.addEventListener('keydown',event=>{
      if(event.key!=='Tab')return;
      const items=[...sheet.querySelectorAll('a[href],button:not([disabled]),summary,input,select,textarea,video[controls],[tabindex="0"]')].filter(n=>n.getClientRects().length&&!n.hidden);
      const first=items[0],last=items[items.length-1];
      if(!first){event.preventDefault();sheet.focus();return;}
      if(event.shiftKey&&(document.activeElement===first||!items.includes(document.activeElement))){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    });
    sheet.addEventListener('cancel',e=>{e.preventDefault();closeSheet();});sheet.addEventListener('click',e=>{if(e.target===sheet && e.clientX>=sheet.getBoundingClientRect().right)closeSheet();});}
  function closeSheet(){if(!sheet?.open||sheet.classList.contains('is-closing'))return;window.ReportEvidence?.pause(sheet);generation++;sheet.classList.add('is-closing');clearTimeout(closeTimer);closeTimer=setTimeout(()=>{sheet.close();sheet.classList.remove('is-closing');document.body.style.overflow=oldOverflow;opener?.focus({preventScroll:true});history=[];},reduce.matches?0:200);}
  function goBack(){if(history.length<2)return;history.pop();const prev=history[history.length-1];fill(prev.id,scroll,false,prev.scroll);sheet.querySelector('[data-reader-back]').hidden=history.length<2;}
  async function fill(id,container,standalone=false,position=0){const token=++generation,m=manifest[id];window.ReportEvidence?.pause(container);container.replaceChildren();const h=el('header','reader-heading');h.append(el('p','reader-eyebrow',m.kind==='stage'?'El recorrido / detalle del tramo':m.kind==='session'?'Evidencia / sesión sintética':'Lectura del estudio'));const title=el(standalone?'h1':'h2','',m.title);if(!standalone)title.id='reader-title';title.tabIndex=-1;h.append(title,el('p','reader-description',m.description));const actions=el('div','reader-source-actions');if(!standalone)actions.append(link('Abrir como página ↗',url(m.page),true));h.append(actions);container.append(h);const status=el('p','','Cargando lectura…');status.setAttribute('role','status');container.append(status);
    if(!standalone)title.focus({preventScroll:true});
    try{const value=await load(id);if(token!==generation)return;status.replaceWith(renderContent(id,value));container.scrollTop=position;}catch(error){if(token===generation){status.textContent='No se pudo cargar esta lectura. Vuelve a intentarlo para ver su contenido.';const retry=el('button','reader-retry','Volver a cargar');retry.type='button';retry.onclick=()=>fill(id,container,standalone,position);status.append(retry);}}
  }
  function open(id,source){if(!sheet)buildSheet();if(!sheet.open){opener=source;oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden';history=[];sheet.showModal();}else if(history.length)history[history.length-1].scroll=scroll.scrollTop;
    history.push({id,scroll:0});sheet.querySelector('[data-reader-back]').hidden=history.length<2;fill(id,scroll);}
  document.addEventListener('click',e=>{if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;const a=e.target.closest('a[href]');if(!a||a.hasAttribute('data-reader-bypass')||a.hasAttribute('download'))return;
    if(a.dataset.readerLocal){const owner=a.closest('.reader-body');const target=[...owner.querySelectorAll('[data-source-id]')].find(n=>n.dataset.sourceId===a.dataset.readerLocal);if(target){e.preventDefault();target.scrollIntoView({behavior:reduce.matches?'auto':'smooth'});}return;}
    const id=a.dataset.reader || routes.get(a.href) || (a.hash && manifest[a.hash.slice(1)] && a.origin===location.origin && a.pathname===location.pathname ? a.hash.slice(1):null);
    if(id){e.preventDefault();open(id,a);}
  });
  document.querySelectorAll('a[href]').forEach(a=>{a.href=readingURL(a.href);});
  const standalone=document.body.dataset.readerPage;
  if(standalone && manifest[standalone]){document.body.append(toolbar(true));const content=el('main','reader-scroll');document.body.append(content);fill(standalone,content,true);}
})();
