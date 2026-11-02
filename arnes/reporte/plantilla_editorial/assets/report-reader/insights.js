/* Human-readable overviews. Original values remain available in labeled details. */
(() => {
  window.ReportInsights = {render(id, v, {el,link,url,table,objectTree}) {
    const box=el('div','insight-view');
    const paragraph=(title,text)=>{if(!text)return;box.append(el('h3','',title),el('p','',text));};
    const items=(title,values)=>{if(!values?.length)return;box.append(el('h3','',title));const ul=el('ul');values.forEach(x=>{const li=el('li');if(typeof x==='string')li.textContent=x;else if(x.que){li.append(el('strong','',x.que),el('p','',x.aprender||''));}else li.append(objectTree(x));ul.append(li);});box.append(ul);};
    const details=(title,value)=>{const d=el('details');d.append(el('summary','',title));const b=el('div','reader-branch');d.append(b);let ready=false;d.addEventListener('toggle',()=>{if(d.open&&!ready){ready=true;b.append(objectTree(value));}});return d;};
    const cards=rows=>{const list=el('div','insight-stats');for(const [value,label] of rows){const c=el('div');c.append(el('strong','',value),el('span','',label));list.append(c);}return list;};
    if(id==='sintesis'){
      paragraph('Conclusión del estudio',v.titular);paragraph('Qué ocurrió',v.veredicto);
      box.append(el('p','reader-note',v.kpis_nota));
      box.append(cards(v.kpis.map(k=>[k.valor,k.etiqueta])));
      box.append(el('h3','','Hallazgos y decisiones'));
      for(const h of v.hallazgos){const c=el('section','insight-finding');c.append(el('p','reader-eyebrow',`${h.id} · ${h.donde} · severidad ${h.severidad}/4`),el('h4','',h.titulo));for(const [label,key] of [['Lo observado','hallazgo'],['Interpretación','interpretacion'],['Qué cambiar','recomendacion']]){if(h[key])c.append(el('strong','',label),el('p','',h[key]));}const refs=el('div','insight-session-links');for(const sid of h.sesiones||[])refs.append(link(sid,url(`lecturas/${sid}.html`)));c.append(refs);box.append(c);}
      items('Lo que funcionó',v.positivos);items('Límites del estudio',v.limitaciones);items('Qué validar con personas',v.validar_con_personas);
      box.append(details('Consultar todos los apartados de la síntesis',v));
    }else if(id==='auditoria'){
      box.append(el('p','reader-note',`Evaluación heurística asistida por IA: ${v.evaluadores} evaluaciones independientes. Se considera coincidencia cuando al menos ${v.umbral_consenso} señalan el criterio. No son entrevistas ni evaluaciones de tres especialistas humanos. La severidad usa una escala de 0 a 4.`));
      box.append(cards([[v.consolidado.length,'observaciones consolidadas'],[v.consolidado.filter(x=>x.consenso).length,'con coincidencia entre evaluaciones']]));
      const label=el('label','insight-search','Buscar por pantalla, criterio o problema'),input=el('input');input.type='search';input.placeholder='Pantalla, criterio o problema…';label.append(input);box.append(label);
      const status=el('p','reader-status');status.setAttribute('role','status');const list=el('div');box.append(status,list);
      const normalized=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
      function draw(){list.replaceChildren();const q=normalized(input.value);const filtered=v.consolidado.filter(x=>normalized([x.pantalla,x.nombre_criterio,...x.problemas].join(' ')).includes(q));status.textContent=`${filtered.length} observaciones`;
        for(const x of filtered){const d=el('details');d.append(el('summary','',`${x.pantalla} · ${x.nombre_criterio} · ${x.evaluadores}/${x.de} evaluaciones`));const b=el('div','reader-branch');b.append(el('p','reader-status',`Severidad media: ${x.severidad_media}/4`));for(const [title,key] of [['Problemas identificados','problemas'],['Recomendaciones','recomendaciones'],['Redacciones propuestas','reescrituras']]){if(x[key]?.length){b.append(el('h4','',title));const ul=el('ul');for(const t of x[key]){const li=el('li');li.append(typeof t==='string'?document.createTextNode(t):objectTree(t));ul.append(li);}b.append(ul);}}d.append(b);list.append(d);}if(!filtered.length)list.append(el('p','','No hay coincidencias. Prueba otra pantalla o criterio.'));}
      input.addEventListener('input',draw);draw();box.append(el('h3','','Aspectos positivos por pantalla'),objectTree(v.positivos),details('Detalle de las evaluaciones y sus registros',v));
    }else if(id==='tecnico'){
      const r=v.resumen;box.append(el('p','reader-note',`Medición automática de ${window.ReportReaderConfig.material} · ${v.dispositivo} · ${v.fecha}. Los resultados de accesibilidad necesitan revisión manual adicional. Las pruebas técnicas de retoma son independientes de las sesiones sintéticas.`));
      box.append(cards([[r.pantallas,'pantallas revisadas'],[r.pasos_ruta,'acciones de la ruta técnica'],[r.toques_ruta,'toques'],[r.campos_ruta,'campos']]),el('h3','','Accesibilidad: problemas detectados'));
      for(const rule of r.reglas_wcag||[]){const c=el('section','insight-finding');c.append(el('h4','',rule.ayuda),el('p','',`Criterios: ${(rule.criterios||[]).join(', ')} · ${rule.pantallas.length} pantallas · ${rule.nodos} elementos.`),el('p','',`Pantallas: ${rule.pantallas.join(', ')}`),details('Revisar ejemplos y diagnóstico',rule.ejemplo));box.append(c);}
      box.append(el('h3','','Conservación del avance en la prueba técnica'),table(['Punto de salida','Al recargar','Al volver','¿Conserva el punto?'],v.retoma.map(x=>[x.punto,x.tras_recargar,x.tras_volver_a_entrar,x.conserva?'Sí':'No'])));
      box.append(details('Rendimiento y condiciones de carga',{condiciones:v.condiciones,umbrales:v.umbrales,carga:v.carga}),details('Instalación y funcionamiento de la PWA',v.pwa),details('Revisar las pantallas evaluadas',v.pantallas),details('Todos los resultados técnicos',v));
    }else return null;
    return box;
  }};
})();
