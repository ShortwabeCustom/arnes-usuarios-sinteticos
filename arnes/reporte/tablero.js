/* Tablero de investigación — vistas, gráficos SVG, filtros y cajón de evidencia (docs/TABLERO.md).
   Lee `D` (datos del estudio, insertados por arnes/reporte/tablero.py). Sin librerías externas. */
(() => {
  'use strict';
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const prom = (xs) => { const v = xs.filter((x) => x != null); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
  const r1 = (x) => (x == null ? '—' : (Math.round(x * 10) / 10).toString());

  const PERF = Object.fromEntries(D.perfiles.map((p, i) => [p.id, { ...p, color: i < 4 ? `var(--s${i + 1})` : 'var(--tinta-3)' }]));
  const H = Object.fromEntries(D.hallazgos.map((h) => [h.id, h]));
  const ESTADO = { positivo: ['✓', 'Positivo'], atencion: ['▲', 'Atención'], critico: ['✕', 'Crítico'], contexto: ['○', 'Contexto'] };
  const NODO = { normal: ['●', 'Normal'], atencion: ['▲', 'Atención'], alta: ['◆', 'Fricción alta'], critico: ['✕', 'Crítico'], sin: ['○', 'Sin observaciones'] };
  const CONF = { alta: 'Alta', media: 'Media', baja: 'Baja' };
  const HIP = { se_sostiene: ['✓', 'Se sostiene'], se_cae: ['✕', 'Se cae'], parcial: ['◐', 'Parcial'], no_concluyente: ['?', 'Evidencia insuficiente'] };
  const MAT = { si: ['●', 'Observado', 'm-si'], parcial: ['◐', 'Parcial', 'm-parcial'], no: ['○', 'No observado', 'm-no'], na: ['—', 'No aplica (auditoría)', 'm-na'] };
  const RES = { exito: 'Éxito', exito_con_friccion: 'Éxito con fricción', abandono: 'Abandono', falso_exito: 'Cree que terminó', fallo_max_pasos: 'Sin terminar', terminado_sin_criterio: 'Terminado sin criterio' };

  const est = { modo: 'investigacion', tarea: 'todas', perfil: 'todos', pestana: 'resumen', sev: 'todas', conf: 'todas',
    series: new Set(['general', ...D.perfiles.map((p) => p.id)]), tablaConf: matchMedia('(max-width: 640px)').matches };

  // ---------------------------------------------------------------- filtros y agregados
  const obsF = () => D.obs.filter((o) => (est.tarea === 'todas' || o.t === est.tarea) && (est.perfil === 'todos' || o.p === est.perfil));
  const porEtapa = (obs) => Object.fromEntries(D.etapas.map((e) => {
    const os = obs.filter((o) => o.e === e);
    return [e, { c: prom(os.map((o) => o.c)), f: prom(os.map((o) => o.f)), n: os.length, alta: os.filter((o) => (o.f || 0) >= 3).length,
      ses: new Set(os.map((o) => o.s)).size }];
  }));
  const estadoEtapa = (v) => (!v || !v.n ? 'sin' : v.f >= 3 || v.c < 45 ? 'critico' : v.f >= 2.5 ? 'alta' : v.f >= 1.5 || v.c < 55 ? 'atencion' : 'normal');
  const hallazgosF = () => D.hallazgos.filter((h) => {
    if (est.sev !== 'todas' && String(h.severidad) !== est.sev) return false;
    if (est.conf !== 'todas' && h.confianza !== est.conf) return false;
    if (est.tarea !== 'todas' && h.sesiones.length && !h.sesiones.some((s) => s.startsWith(est.tarea + '-'))) return false;
    if (est.perfil !== 'todos' && h.sesiones.length && !['si', 'parcial'].includes(h.matriz[est.perfil])) return false;
    return true;
  });
  const etapasDeHallazgos = () => {
    const m = {};
    for (const h of hallazgosF()) if (h.etapa) (m[h.etapa] = m[h.etapa] || []).push(h.id);
    return m;
  };

  // ---------------------------------------------------------------- piezas
  const etq = (t, cls = '') => `<span class="etq ${cls}">${esc(t)}</span>`;
  const sev = (h) => `<span class="sev s${h.severidad}">${h.severidad >= 3 ? '✕' : h.severidad === 2 ? '▲' : '○'} Severidad ${h.severidad} · ${esc(h.severidad_txt)}</span>`;
  const frec = (h) => (h.sesiones.length ? `${h.n_ses} de ${h.base} sesiones` : 'Auditoría');
  const estadoTxt = (k) => `<span class="estado ${k}">${ESTADO[k][0]} ${ESTADO[k][1]}</span>`;

  function kpi(k) {
    let v = '';
    if (k.partes) {
      v = `<div class="partes">${k.partes.map((p) => (k.id === 'sin_friccion' ? `<div><b class="num">${p.a}/${p.b}</b><small>${esc(p.t)}</small></div>`
        : `<div><b class="num">${r1(p.v)}</b><small>${esc(p.t)} · de 7</small></div>`)).join('')}</div>`;
    } else v = `<div class="v num">${esc(k.valor)}</div>`;
    return `<div class="kpi ${k.estado}">${estadoTxt(k.estado)}<div class="e">${esc(k.etiqueta)}</div>${v}
      ${k.comparador ? `<div class="cmp">${esc(k.comparador)}</div>` : ''}<div class="c">${esc(k.contexto || '')}</div>
      ${k.derivado ? etq('Métrica derivada', 'der') : ''}</div>`;
  }

  function mapaRecorrido(compacto = false) {
    const pe = porEtapa(obsF()), eh = etapasDeHallazgos();
    const nodos = D.etapas.map((e, i) => {
      const v = pe[e], k = estadoEtapa(v), hs = eh[e] || [];
      const txt = `${e}: ${NODO[k][1]}. Confianza media ${r1(v.c)} de 100, fricción media ${r1(v.f)} de 5, ${v.n} observaciones${hs.length ? ', hallazgos ' + hs.join(', ') : ''}.`;
      return `<div class="nodo" tabindex="0" role="listitem" aria-label="${esc(txt)}" data-tip="${esc(txt)}">
        <span class="punto p-${k === 'sin' ? 'normal' : k}" aria-hidden="true" title="${NODO[k][1]}">${NODO[k][0]}</span>
        <span class="nom">${i + 1}. ${esc(e)}</span>
        ${compacto ? '' : `<span class="dat num">Confianza ${r1(v.c)} · fricción ${r1(v.f)}</span>`}
        <span class="dat">${NODO[k][1]}${hs.length ? ' · ' + hs.join(' ') : ''}</span></div>`;
    }).join('');
    return `<div class="recorrido" role="list" aria-label="Recorrido por etapa">${nodos}</div>
      <div class="leyenda" aria-hidden="true"><span><i class="p-normal"></i>● Normal</span><span><i class="p-atencion"></i>▲ Atención (fricción ≥ 1.5 o confianza &lt; 55)</span>
      <span><i class="p-alta"></i>◆ Fricción alta (≥ 2.5)</span><span><i class="p-critico"></i>✕ Crítico (fricción ≥ 3 o confianza &lt; 45)</span></div>
      <p class="cap">Medias de las sesiones filtradas · ${etq('Métrica derivada', 'der')} · fricción de 0 a 5.</p>`;
  }

  function tarjetaTop(h, i) {
    return `<article class="item"><span class="orden">0${i + 1}</span><h3>${esc(h.titulo)}</h3>
      <div>${sev(h)} · <span class="cap">Confianza ${esc(CONF[h.confianza] || h.confianza)}</span></div>
      <dl><dt>Dónde</dt><dd>${esc(h.etapa || h.pantalla || '—')}</dd><dt>Evidencia</dt><dd class="num">${frec(h)}${h.metricas.c != null ? ` · confianza ${r1(h.metricas.c)}/100` : ''}</dd>
      <dt>Impacto</dt><dd>${h.impacto_usuario.length ? esc(h.impacto_usuario.join(' · ')) : '<span class="vacio-msg">Sin dato</span>'}</dd>
      <dt>Recomendación</dt><dd>${esc(h.recomendacion)}</dd>
      <dt>Prioridad</dt><dd class="num">${h.prioridad != null ? r1(h.prioridad) + ' ' + etq('Métrica derivada', 'der') : 'Sin dato'}</dd></dl>
      <button class="boton-ev" data-hallazgo="${esc(h.id)}">Ver evidencia →</button></article>`;
  }

  function tarjetaHallazgo(h) {
    const val = h.validacion || (D.validar.find((v) => v.hallazgo === h.id) || {}).que;
    return `<article class="hallazgo" id="hallazgo-${esc(h.id)}" aria-labelledby="t-${esc(h.id)}">
      <div><span class="hid">Hallazgo ${esc(h.id)}${h.etapa ? ' · ' + esc(h.etapa) : ''}</span><h3 id="t-${esc(h.id)}">${esc(h.titulo)}</h3>
        <div class="capa"><h4>Observación ${etq('Evidencia')}</h4><p>${esc(h.observacion)}</p></div>
        <div class="capa"><h4>Qué significa ${etq('Inferencia')}</h4><p>${esc(h.interpretacion)}</p></div>
        <div class="capa ahora"><h4>Qué hacer</h4><p>${esc(h.recomendacion)}</p></div>
        <div class="capa"><h4>Qué validar con personas</h4><p>${val ? esc(val) : '<span class="vacio-msg">Sin dato</span>'}</p></div>
        ${h.reescritura.length ? `<div class="capa"><h4>Reescritura sugerida</h4>${h.reescritura.map((r) => `<p>«${esc(r[0])}» → <b>«${esc(r[1])}»</b><br><span class="cap">${esc(r[2] || '')}</span></p>`).join('')}</div>` : ''}
      </div>
      <aside class="lado" aria-label="Datos del hallazgo">
        <div>${sev(h)}</div>
        <div class="fila"><span>Confianza de investigación</span><b>${esc(CONF[h.confianza] || h.confianza)}</b></div>
        <div class="fila"><span>Sesiones</span><b class="num">${frec(h)}</b></div>
        ${h.metricas.n ? `<div class="fila"><span>Observaciones en la pantalla</span><b class="num">${h.metricas.n}</b></div>
          <div class="fila"><span>Confianza media ahí</span><b class="num">${r1(h.metricas.c)}/100</b></div>
          <div class="fila"><span>Fricción media ahí</span><b class="num">${r1(h.metricas.f)}/5</b></div>` : ''}
        <div><span class="cap">Impacto en el usuario</span><div class="chips">${h.impacto_usuario.length ? h.impacto_usuario.map((x) => etq(x)).join('') : '<span class="vacio-msg">Sin dato</span>'}</div></div>
        <div class="fila"><span>Prioridad ${etq('Derivada', 'der')}</span><b class="num">${h.prioridad != null ? r1(h.prioridad) : '—'}</b></div>
        <div class="fila"><span>Impacto de negocio (1–5)</span><b class="num">${h.impacto_negocio ?? '—'}</b></div>
        ${h.heuristica ? `<div><span class="cap">Heurística</span><br>${esc(h.heuristica)}</div>` : ''}
        <div><span class="cap">Fuente</span><div class="chips">${h.fuente.map((f) => etq(f, f === 'Sesión sintética' ? 'sint' : '')).join('')}</div></div>
        ${h.oportunidad ? `<div class="fila"><span>Oportunidad</span><b>${esc(h.oportunidad)}</b></div>` : ''}
        <button class="boton-ev" data-hallazgo="${esc(h.id)}">Explorar evidencia →</button>
      </aside></article>`;
  }

  function validacion(v) {
    return `<article class="val"><h3>${esc(v.que)}</h3><dl><dt>Método</dt><dd>${esc(v.metodo)}</dd>
      <dt>Qué aprender</dt><dd>${v.aprender ? esc(v.aprender) : '<span class="vacio-msg">Sin dato</span>'}</dd>
      <dt>Muestra (UiX)</dt><dd class="num">${esc(v.muestra)}</dd><dt>Prioridad</dt><dd>${v.prioridad ? esc(v.prioridad) : '<span class="vacio-msg">Sin dato</span>'}</dd>
      ${v.hallazgo ? `<dt>Hallazgo</dt><dd><button class="ver-tabla" data-hallazgo="${esc(v.hallazgo)}">${esc(v.hallazgo)}</button></dd>` : ''}</dl></article>`;
  }

  // ---------------------------------------------------------------- gráficos
  function partir(t, n = 13) {
    const ps = t.split(' '), ls = ['']; for (const p of ps) { if ((ls[ls.length - 1] + ' ' + p).trim().length > n && ls[ls.length - 1]) ls.push(p); else ls[ls.length - 1] = (ls[ls.length - 1] + ' ' + p).trim(); }
    return ls.slice(0, 2);
  }

  function graficoConfianza() {
    const W = 980, Hh = 330, ml = 40, mr = 92, mt = 34, mb = 56, iw = W - ml - mr, ih = Hh - mt - mb;
    const ets = D.etapas, x = (i) => ml + (ets.length === 1 ? iw / 2 : (i * iw) / (ets.length - 1)), y = (v) => mt + ih - (v / 100) * ih;
    const base = D.obs.filter((o) => est.tarea === 'todas' || o.t === est.tarea);
    const series = [{ id: 'general', nombre: 'General', color: 'var(--general)', vals: ets.map((e) => prom(base.filter((o) => o.e === e).map((o) => o.c))) }]
      .concat(D.perfiles.map((p) => ({ id: p.id, nombre: p.nombre, color: PERF[p.id].color, vals: ets.map((e) => prom(base.filter((o) => o.e === e && o.p === p.id).map((o) => o.c))) })));
    const foco = est.perfil !== 'todos' ? est.perfil : null;
    let g = '';
    for (const v of [0, 25, 50, 75, 100]) g += `<line class="rej" x1="${ml}" x2="${ml + iw}" y1="${y(v)}" y2="${y(v)}"/><text x="${ml - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
    g += `<line class="base" x1="${ml}" x2="${ml + iw}" y1="${y(0)}" y2="${y(0)}"/>`;
    ets.forEach((e, i) => { partir(e).forEach((l, j) => { g += `<text x="${x(i)}" y="${mt + ih + 18 + j * 13}" text-anchor="middle">${esc(l)}</text>`; }); });
    // anotaciones: etapa de cada hallazgo prioritario
    const anot = D.top.map((id) => H[id]).filter((h) => h && ets.includes(h.etapa));
    const usadas = {};
    for (const h of anot) {
      const i = ets.indexOf(h.etapa), k = usadas[i] = (usadas[i] || 0) + 1;
      g += `<line class="anot-l" x1="${x(i)}" x2="${x(i)}" y1="${mt - 4}" y2="${y(0)}"/><text class="anot" x="${x(i) + 4 + (k - 1) * 26}" y="${mt - 10}">▼ ${esc(h.id)}</text>`;
    }
    const finales = [];
    for (const s of series) {
      if (!est.series.has(s.id)) continue;
      const tenue = foco && s.id !== foco && s.id !== 'general' ? ' tenue' : '';
      let d = '', abierto = false;
      s.vals.forEach((v, i) => { if (v == null) { abierto = false; return; } d += `${abierto ? 'L' : 'M'}${x(i)},${y(v)}`; abierto = true; });
      g += `<path class="linea${s.id === 'general' ? ' general' : ''}${tenue}" d="${d}" stroke="${s.color}"/>`;
      s.vals.forEach((v, i) => { if (v != null) g += `<circle class="${tenue}" cx="${x(i)}" cy="${y(v)}" r="${s.id === 'general' ? 4.5 : 4}" fill="${s.color}" stroke="var(--superficie)" stroke-width="2"/>`; });
      const ult = [...s.vals.keys()].reverse().find((i) => s.vals[i] != null);
      if (ult != null && !tenue) finales.push({ y: y(s.vals[ult]), x: x(ult), s });
    }
    finales.sort((a, b) => a.y - b.y);
    for (let i = 1; i < finales.length; i++) if (finales[i].y - finales[i - 1].y < 13) finales[i].y = finales[i - 1].y + 13;
    for (const f of finales) g += `<text x="${ml + iw + 8}" y="${f.y + 4}" style="fill:var(--tinta)">${esc(f.s.nombre)}</text>`;
    ets.forEach((e, i) => { g += `<rect class="zona-tip" x="${x(i) - iw / ets.length / 2}" y="${mt}" width="${iw / ets.length}" height="${ih}" fill="transparent" data-i="${i}"/>`; });
    const resumen = series.filter((s) => est.series.has(s.id)).map((s) => {
      const vs = s.vals.map((v, i) => [v, ets[i]]).filter((p) => p[0] != null), mn = vs.reduce((a, b) => (b[0] < a[0] ? b : a), vs[0] || [null, '']);
      return `${s.nombre}: mínima ${r1(mn[0])} en ${mn[1]}`;
    }).join('; ');
    const svg = `<svg class="grafico" viewBox="0 0 ${W} ${Hh}" role="img" aria-label="Confianza por etapa. ${esc(resumen)}">${g}</svg>`;
    const tabla = `<div class="desliza"><table class="tabla"><caption class="cap" style="text-align:left">Confianza media (0–100) por etapa</caption><thead><tr><th>Etapa</th>${series.map((s) => `<th>${esc(s.nombre)}</th>`).join('')}</tr></thead>
      <tbody>${ets.map((e, i) => `<tr><th scope="row">${esc(e)}</th>${series.map((s) => `<td class="n">${r1(s.vals[i])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    const botones = `<div class="botones" role="group" aria-label="Series visibles">${series.map((s) => `<button data-serie="${s.id}" aria-pressed="${est.series.has(s.id)}"><i style="background:${s.color}"></i>${esc(s.nombre)}</button>`).join('')}</div>`;
    return { html: `${botones}<div class="contenedor-linea">${est.tablaConf ? tabla : svg}</div>
      <button class="ver-tabla" data-accion="tabla-conf">${est.tablaConf ? 'Ver como gráfico' : 'Ver como tabla'}</button>
      <ul class="cap" style="margin:6px 0;padding-left:18px">${anot.map((h) => `<li><b style="color:var(--critico)">▼ ${esc(h.id)}</b> ${esc(h.etapa)}: ${esc(h.titulo)}</li>`).join('')}</ul>
      <p class="cap">${esc(resumen)}. ${etq('Métrica derivada', 'der')}</p>`, series, x, ets };
  }

  function mapaCalor() {
    const base = D.obs.filter((o) => est.tarea === 'todas' || o.t === est.tarea);
    const celdas = [];
    const filas = D.etapas.map((e) => {
      const tds = D.perfiles.map((p) => {
        const os = base.filter((o) => o.e === e && o.p === p.id), f = prom(os.map((o) => o.f)), c = prom(os.map((o) => o.c));
        if (f == null) return '<td class="vacio" aria-label="Sin observaciones">—</td>';
        const q = Math.min(5, Math.round(f)), peor = os.slice().sort((a, b) => (b.f - a.f) || (a.c - b.c))[0];
        const tip = `${e} · ${p.nombre}\nFricción media ${r1(f)} de 5 · confianza ${r1(c)}\n«${(peor.txt || '').slice(0, 140)}»`;
        celdas.push({ e, p: p.nombre, f, c, txt: peor.txt });
        const dim = est.perfil !== 'todos' && est.perfil !== p.id ? 'opacity:.35;' : '';
        return `<td style="background:var(--q${q});color:var(--qt${q});${dim}"><button data-tip="${esc(tip)}" aria-label="${esc(tip)}">${r1(f)}</button></td>`;
      }).join('');
      return `<tr><th scope="row">${esc(e)}</th>${tds}</tr>`;
    }).join('');
    const tabla = `<table class="calor solo-escritorio"><caption class="cap" style="text-align:left;padding-bottom:6px">Fricción media (0–5) por etapa y perfil</caption>
      <thead><tr><th></th>${D.perfiles.map((p) => `<th scope="col">${esc(p.nombre)}</th>`).join('')}</tr></thead><tbody>${filas}</tbody></table>
      <div class="escala solo-escritorio" aria-hidden="true">0 ${[0, 1, 2, 3, 4, 5].map((q) => `<span style="background:var(--q${q})"></span>`).join('')} 5</div>`;
    const lista = `<ol class="lista-num solo-movil">${celdas.sort((a, b) => b.f - a.f).slice(0, 10).map((x) => `<li><b>${esc(x.e)}</b> · ${esc(x.p)} — fricción ${r1(x.f)}, confianza ${r1(x.c)}</li>`).join('')}</ol>`;
    return tabla + lista;
  }

  function matrizPrioridad() {
    const W = 520, Hh = 320, ml = 70, mr = 20, mt = 20, mb = 46, iw = W - ml - mr, ih = Hh - mt - mb;
    const xs = { baja: 0, media: 1, alta: 2 }, x = (c) => ml + (xs[c] + 0.5) * (iw / 3), y = (s) => mt + ih - ((s - 0.5) / 4) * ih;
    let g = `<rect x="${ml + (2 * iw) / 3}" y="${mt}" width="${iw / 3}" height="${ih / 2}" fill="var(--critico-fondo)"/>
      <text x="${ml + iw - 6}" y="${mt + 14}" text-anchor="end" style="fill:var(--critico);font-weight:600">Actuar primero</text>`;
    for (let s = 1; s <= 4; s++) g += `<line class="rej" x1="${ml}" x2="${ml + iw}" y1="${y(s)}" y2="${y(s)}"/><text x="${ml - 8}" y="${y(s) + 4}" text-anchor="end">${s} ${['', 'Cosm.', 'Menor', 'Imp.', 'Crít.'][s]}</text>`;
    ['Baja', 'Media', 'Alta'].forEach((t, i) => { g += `<text x="${ml + (i + 0.5) * (iw / 3)}" y="${mt + ih + 18}" text-anchor="middle">${t}</text>`; });
    g += `<text x="${ml + iw / 2}" y="${Hh - 6}" text-anchor="middle">Confianza de investigación →</text>
      <text x="14" y="${mt + ih / 2}" transform="rotate(-90 14 ${mt + ih / 2})" text-anchor="middle">Severidad →</text>`;
    const grupos = {};
    for (const h of hallazgosF()) (grupos[`${h.confianza}|${h.severidad}`] = grupos[`${h.confianza}|${h.severidad}`] || []).push(h);
    for (const [k, hs] of Object.entries(grupos)) {
      hs.forEach((h, j) => {
        const cx = x(h.confianza) + (j - (hs.length - 1) / 2) * 34, cy = y(h.severidad);
        g += `<g class="punto-m" tabindex="0" role="button" data-hallazgo="${esc(h.id)}" aria-label="${esc(h.id)}: ${esc(h.titulo)}. Severidad ${h.severidad}, confianza ${esc(CONF[h.confianza])}" style="cursor:pointer">
          <circle cx="${cx}" cy="${cy}" r="15" fill="var(--superficie)" stroke="${h.severidad >= 3 ? 'var(--critico)' : h.severidad === 2 ? 'var(--atencion)' : 'var(--tinta-3)'}" stroke-width="2"/>
          <text x="${cx}" y="${cy + 4}" text-anchor="middle" style="fill:var(--tinta);font-weight:700">${esc(h.id)}</text></g>`;
      });
    }
    return `<svg class="grafico" viewBox="0 0 ${W} ${Hh}" role="img" aria-label="Matriz de severidad por confianza de investigación">${g}</svg>
      <p class="cap">Cada círculo es un hallazgo; clic o Enter abre su evidencia. El impacto de negocio no se mezcla aquí: va en cada tarjeta.</p>`;
  }

  function barrasMetricas() {
    const nombres = { pasos: 'Pasos', clics: 'Toques', campos: 'Campos solicitados', tiempo_completan_s: 'Tiempo estimado (s) · modelo', espera_sistema_s: 'Espera del sistema (s)' };
    const ts = Object.keys(D.metricas).filter((t) => est.tarea === 'todas' || t === est.tarea);
    return `<div class="barras">${Object.entries(nombres).map(([k, n]) => {
      const vals = ts.map((t) => D.metricas[t][k]).filter((v) => v != null), max = Math.max(...vals, 1);
      if (!vals.length) return '';
      return `<div class="barra-m"><div class="t">${esc(n)}</div>${ts.map((t) => { const v = D.metricas[t][k];
        return v == null ? '' : `<div class="fila"><span>${esc(t)}</span><div class="pista"><div class="relleno" style="width:${(100 * v) / max}%"></div></div><b class="num">${r1(v)}</b></div>`; }).join('')}</div>`;
    }).join('')}</div><p class="cap">Medianas por tarea, cada métrica en su propia escala. El tiempo es un modelo [SUPUESTO], no una medición.</p>`;
  }

  // ---------------------------------------------------------------- vistas
  const seccion = (titulo, pregunta, cuerpo, id = '') => `<section class="bloque"${id ? ` id="${id}"` : ''}><div class="titulo-sec"><h2>${esc(titulo)}</h2>${pregunta ? `<span class="pregunta">${esc(pregunta)}</span>` : ''}</div>${cuerpo}</section>`;

  function vistaResumen() {
    const top = D.top.map((id) => H[id]).filter(Boolean);
    const funciona = D.positivos.slice(0, 5);
    let h = seccion('Qué requiere atención', 'Los 3 hallazgos con mayor prioridad (severidad × frecuencia × confianza)',
      `<div class="top">${top.map(tarjetaTop).join('')}</div>`);
    h += seccion('Fricción del recorrido', '¿Dónde ocurre?', `<div class="tarjeta">${mapaRecorrido(true)}</div>`);
    h += `<div class="dos">${seccion('Qué cambiar primero', '', `<div class="tarjeta"><ol class="lista-num">${top.map((x) => `<li>${esc(x.recomendacion)} <span class="cap">(${esc(x.id)})</span></li>`).join('')}</ol></div>`)}
      ${seccion('Lo que ya funciona', '', `<div class="tarjeta"><ul class="lista-check">${funciona.map((p) => `<li><span>${esc(p)}</span></li>`).join('')}</ul></div>`)}</div>`;
    if (est.modo === 'ejecutivo') h += seccion('Qué validar con personas', 'Las sesiones sintéticas no cuentan como muestra', `<div class="rejilla-c">${D.validar.map(validacion).join('')}</div>`);
    else if (D.resumen.length) h += seccion('En resumen', '', `<div class="tarjeta"><ul class="lista-num" style="list-style:disc">${D.resumen.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>`);
    return h;
  }

  function vistaRecorrido() {
    const c = graficoConfianza();
    return seccion('Mapa del recorrido', '¿Dónde está el problema?', `<div class="tarjeta">${mapaRecorrido()}</div>`)
      + seccion('Confianza por etapa', '¿Dónde empieza a caer la confianza?', `<div class="tarjeta" id="caja-conf">${c.html}</div>`)
      + `<div class="dos">${seccion('Mapa de fricción', '¿Le pasa a todos o a algunos?', `<div class="tarjeta">${mapaCalor()}</div>`)}
        ${seccion('Costo del flujo por tarea', '¿Cuánto pide cada tarea?', `<div class="tarjeta">${barrasMetricas()}</div>`)}</div>`;
  }

  function vistaHallazgos() {
    const hs = hallazgosF().slice().sort((a, b) => (b.prioridad ?? -1) - (a.prioridad ?? -1) || b.severidad - a.severidad);
    const filtros = `<div class="filtros" role="group" aria-label="Filtros de hallazgos">
      <label class="control">Severidad <select data-filtro="sev"><option value="todas">Todas</option>${[4, 3, 2, 1].map((s) => `<option value="${s}" ${est.sev === String(s) ? 'selected' : ''}>${s} · ${['', 'Cosmético', 'Menor', 'Importante', 'Crítico'][s]}</option>`).join('')}</select></label>
      <label class="control">Confianza <select data-filtro="conf"><option value="todas">Todas</option>${['alta', 'media', 'baja'].map((c) => `<option value="${c}" ${est.conf === c ? 'selected' : ''}>${CONF[c]}</option>`).join('')}</select></label>
      <span class="cap">${hs.length} de ${D.hallazgos.length} hallazgos</span></div>`;
    const hip = D.hipotesis.map((x) => `<article class="hip"><span class="est ${x.estado}">${HIP[x.estado]?.[0] || '?'} ${esc(HIP[x.estado]?.[1] || x.estado)}</span>
      <b>Hipótesis ${esc(x.id)}</b><span>${esc(x.texto)}</span><details><summary>Ver análisis</summary><p class="cap">${esc(x.evidencia)}</p>
      <p class="cap"><b>Se sostiene si:</b> ${esc(x.sostiene)}<br><b>Se cae si:</b> ${esc(x.cae)}</p></details></article>`).join('');
    return `<div class="dos">${seccion('Prioridad', '¿Qué atiendo primero?', `<div class="tarjeta">${matrizPrioridad()}</div>`)}
      ${seccion('Hipótesis', '¿Qué se confirmó?', `<div class="rejilla-c" style="grid-template-columns:1fr">${hip}</div>`)}</div>`
      + seccion('Hallazgos', 'Observación → qué significa → qué hacer → qué validar', filtros + (hs.length ? hs.map(tarjetaHallazgo).join('') : '<p class="vacio-msg">Ningún hallazgo con estos filtros.</p>'));
  }

  function vistaPerfiles() {
    const sel = `<div class="perfiles-sel" role="group" aria-label="Elegir perfil">${D.perfiles.map((p) => {
      const ses = D.sesiones.filter((s) => s.p === p.id && (est.tarea === 'todas' || s.t === est.tarea));
      const ces = prom(ses.map((s) => s.ces)), cmin = Math.min(...ses.map((s) => s.cmin ?? 101));
      return `<button class="psel" data-perfil="${p.id}" aria-pressed="${est.perfil === p.id}"><span class="pn"><i style="background:${PERF[p.id].color}"></i>${esc(p.nombre)}</span>
        <span class="cap">${esc(p.segmento)} · ${esc(p.edad)} años</span><span class="cap num">CES medio ${r1(ces)} · confianza mínima ${cmin > 100 ? '—' : cmin}</span>
        <span class="cap">${ses.filter((s) => s.resultado === 'exito').length} de ${ses.length} sesiones sin fricción</span></button>`;
    }).join('')}</div><p class="cap">${etq('Perfil simulado', 'sint')} Elige un perfil para filtrar el recorrido, los gráficos, los hallazgos y las citas. Vuelve a tocarlo para ver a todos.</p>`;
    const hs = D.hallazgos;
    const matriz = `<div class="desliza"><table class="matriz"><caption class="cap" style="text-align:left;padding-bottom:6px">● observado en las 2 corridas · ◐ en una · ○ no observado · — no aplica (hallazgo de auditoría)</caption>
      <thead><tr><th>Hallazgo</th>${D.perfiles.map((p) => `<th scope="col" style="text-align:center">${esc(p.nombre)}</th>`).join('')}</tr></thead>
      <tbody>${hs.map((h) => `<tr class="clic" tabindex="0" data-hallazgo="${esc(h.id)}"><th scope="row"><b>${esc(h.id)}</b> ${esc(h.titulo)}</th>${D.perfiles.map((p) => {
        const m = MAT[h.matriz[p.id]]; return `<td class="c ${m[2]}" title="${m[1]}" aria-label="${esc(p.nombre)}: ${m[1]}">${m[0]}</td>`; }).join('')}</tr>`).join('')}</tbody></table></div>`;
    const visibles = est.perfil === 'todos' ? D.perfiles : D.perfiles.filter((p) => p.id === est.perfil);
    const citas = visibles.map((p) => {
      const t = D.perfiles_txt[p.id] || {};
      const bajas = D.obs.filter((o) => o.p === p.id && (est.tarea === 'todas' || o.t === est.tarea) && o.c != null).sort((a, b) => a.c - b.c).slice(0, 2);
      return `<div class="tarjeta"><h3 style="font-size:16px;display:flex;gap:8px;align-items:center"><i style="width:10px;height:10px;border-radius:50%;background:${PERF[p.id].color};display:inline-block"></i>${esc(p.completo)}</h3>
        <p class="cap">${esc(p.segmento)}</p>
        ${t.cita ? `<blockquote class="cita">«${esc(t.cita)}»<small>${etq('Perfil simulado', 'sint')} Frase sintética, no una cita de una persona</small></blockquote>` : ''}
        ${t.entiende ? `<p><b>Entiende:</b> ${esc(t.entiende)}</p>` : ''}${t.rompe ? `<p><b>Se rompe con:</b> ${esc(t.rompe)}</p>` : ''}
        <h4 class="cap" style="margin-top:10px">Momentos de menor confianza</h4>${bajas.map((o) => `<blockquote class="cita">«${esc(o.txt)}»<small>${esc(o.s)} · ${esc(o.e)} · confianza ${o.c} · fricción ${o.f}</small></blockquote>`).join('')}</div>`;
    }).join('');
    return seccion('¿El problema ocurre igual para todos?', '', sel) + seccion('Hallazgo × perfil', 'Se escanea en segundos', `<div class="tarjeta">${matriz}</div>`)
      + seccion('Lo que dijo cada perfil', 'Pensamiento en voz alta simulado', `<div class="dos">${citas}</div>`);
  }

  function vistaEvidencia() {
    const ses = D.sesiones.filter((s) => (est.tarea === 'todas' || s.t === est.tarea) && (est.perfil === 'todos' || s.p === est.perfil));
    const tabla = `<div class="desliza"><table class="tabla"><thead><tr><th>Sesión</th><th>Perfil</th><th>Tarea</th><th>Resultado</th><th>Pasos</th><th>CES</th><th>Confianza mínima</th></tr></thead>
      <tbody>${ses.map((s) => `<tr class="clic" tabindex="0" data-sesion="${esc(s.id)}"><td><b>${esc(s.id)}</b></td><td>${esc(PERF[s.p]?.nombre || s.p)}</td><td>${esc(s.t)}</td>
        <td>${esc(RES[s.resultado] || s.resultado)}</td><td class="n">${s.pasos}</td><td class="n">${s.ces ?? '—'}</td><td class="n">${s.cmin ?? '—'}</td></tr>`).join('')}</tbody></table></div>
      <p class="cap">${ses.length} sesiones sintéticas · clic o Enter abre la sesión paso a paso.</p>`;
    const aud = D.auditoria.slice(0, 40);
    const tAud = aud.length ? `<div class="desliza"><table class="tabla"><thead><tr><th>Pantalla</th><th>Criterio</th><th>Evaluadores</th><th>Severidad</th><th>Problema</th></tr></thead>
      <tbody>${aud.map((a) => `<tr><td>${esc(a.pantalla)}</td><td><b>${esc(a.criterio)}</b> <span class="cap">${esc(a.nombre)}</span></td><td class="n">${esc(a.ev)}</td><td class="n">${a.sev}</td><td>${esc(a.problema)}</td></tr>`).join('')}</tbody></table></div>
      <p class="cap">${D.auditoria.length} observaciones con consenso de ${D.auditoria_n?.evaluadores || 3} evaluadores ${etq('Modelo')}; se muestran ${aud.length}. El detalle completo está en el reporte en formato documento.</p>` : '<p class="vacio-msg">Sin auditoría.</p>';
    return seccion('Sesiones', 'Trazabilidad de cada hallazgo', `<div class="tarjeta">${tabla}</div>`)
      + seccion('Qué validar con personas', 'Las sesiones sintéticas no cuentan para esta muestra', `<div class="rejilla-c">${D.validar.map(validacion).join('')}</div>`)
      + seccion('Auditoría experta', 'Evaluación independiente con consenso', `<div class="tarjeta">${tAud}</div>`);
  }

  function vistaMetodologia() {
    const a = D.alcance;
    const etqs = [['Evidencia', 'Medido o visto en el material', ''], ['Simulación', 'Atribuido a un perfil sintético', 'sint'], ['Modelo', 'Salida de un modelo, igual para todos los perfiles', ''],
      ['Inferencia', 'Interpretación del equipo', ''], ['Supuesto', 'Decisión del método, declarada', ''], ['Métrica derivada', 'Calculada a partir de los datos', 'der'], ['Sin dato', 'No existe en los datos', '']];
    return seccion('Alcance', 'Investigación UX sintética', `<div class="tarjeta"><div class="kpis" style="grid-template-columns:repeat(4,minmax(0,1fr));margin:0">
        <div class="kpi contexto"><div class="e">Perfiles sintéticos</div><div class="v num">${a.perfiles}</div><div class="c">biblioteca ${esc(a.biblioteca)} · panel ${esc(a.panel)}</div></div>
        <div class="kpi contexto"><div class="e">Corridas por tarea</div><div class="v num">${a.corridas}</div><div class="c">«creer en lo que se repite»</div></div>
        <div class="kpi contexto"><div class="e">Sesiones sintéticas</div><div class="v num">${a.sesiones}</div><div class="c">${a.tareas} tareas</div></div>
        <div class="kpi contexto"><div class="e">Material</div><div class="v" style="font-size:18px">${esc(a.material)}</div><div class="c">estudio de prototipo</div></div></div>
        ${D.pregunta ? `<p style="margin-top:14px"><b>Pregunta:</b> ${esc(D.pregunta)}</p>` : ''}
        ${D.tareas.map((t) => `<p><b>${esc(t.id)}:</b> ${esc(t.escenario)} <i>«${esc(t.instruccion)}»</i></p>`).join('')}</div>`)
      + seccion('Etiquetas de evidencia', '', `<div class="tarjeta"><div class="chips" style="gap:10px">${etqs.map(([n, d, c]) => `<span>${etq(n, c)} <span class="cap">${esc(d)}</span></span>`).join('')}</div></div>`)
      + `<div class="dos">${seccion('Límites', 'Sin suavizar', `<div class="tarjeta"><ul class="lista-num" style="list-style:disc">${D.limitaciones.concat(D.tecnicas).map((x) => `<li>${esc(x)}</li>`).join('')}</ul>
          ${D.robustez.map((x) => `<p class="cap">▲ ${esc(x)}</p>`).join('')}</div>`)}
        ${seccion('Estado de prototipado', 'Lo no conectado no es defecto', `<div class="tarjeta"><ul class="lista-num" style="list-style:disc">${D.prototipado.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>`)}</div>`
      + `<div class="dos">${seccion('Lo aprendido sobre el método', '', `<div class="tarjeta"><ul class="lista-num" style="list-style:disc">${D.aprendizajes.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>`)}
        ${seccion('Fuentes y próximos pasos', '', `<div class="tarjeta"><ul class="lista-num" style="list-style:disc">${D.fuentes.map((f) => `<li><b>${esc(f.nombre)}</b> — ${esc(f.uso || '')}<br><span class="cap">${esc(f.ruta || '')}</span></li>`).join('')}</ul>
          <h4 class="cap" style="margin-top:12px">Próximos pasos</h4><ol class="lista-num">${D.proximos.map((x) => `<li>${esc(x)}</li>`).join('')}</ol>
          <p style="margin-top:12px"><a href="${esc(D.detalle)}">Reporte completo en formato documento →</a><br><span class="cap">Auditoría completa, guía de estilo, accesibilidad, demográficos, capturas y trazabilidad.</span></p></div>`)}</div>`;
  }

  const VISTAS = [['resumen', 'Resumen', vistaResumen], ['recorrido', 'Recorrido', vistaRecorrido], ['hallazgos', 'Hallazgos', vistaHallazgos],
    ['perfiles', 'Perfiles', vistaPerfiles], ['evidencia', 'Evidencia', vistaEvidencia], ['metodologia', 'Metodología', vistaMetodologia]];

  // ---------------------------------------------------------------- página
  function pintar() {
    const ej = est.modo === 'ejecutivo';
    if (ej) est.pestana = 'resumen';
    const vista = VISTAS.find((v) => v[0] === est.pestana);
    const conf = D.confianza ? (CONF[D.confianza] || D.confianza) : 'Sin dato';
    $('#app').innerHTML = `
    <header class="barra"><div class="env">
      <div class="marca"><b>${esc(D.producto || D.titulo)}</b><span>Investigación UX sintética</span></div>
      <div class="control"><span class="seg" role="group" aria-label="Modo de lectura">
        <button data-modo="ejecutivo" aria-pressed="${ej}">Ejecutivo</button><button data-modo="investigacion" aria-pressed="${!ej}">Investigación</button></span></div>
      <label class="control">Tarea <select data-global="tarea"><option value="todas">Todas</option>${D.tareas.map((t) => `<option value="${t.id}" ${est.tarea === t.id ? 'selected' : ''}>${t.id}</option>`).join('')}</select></label>
      <label class="control">Perfil <select data-global="perfil"><option value="todos">Todos</option>${D.perfiles.map((p) => `<option value="${p.id}" ${est.perfil === p.id ? 'selected' : ''}>${esc(p.nombre)}</option>`).join('')}</select></label>
    </div></header>
    <div class="env cabeza">
      <div class="sello">${esc(D.estudio)} · ${esc(D.fecha)}</div>
      <h1 class="veredicto">${esc(D.veredicto)}</h1>
      ${ej ? '' : `<p class="veredicto-detalle">${esc(D.detalle_veredicto)}</p>`}
      <div class="meta"><span>Confianza: <b>${esc(conf)}</b></span><span>Tipo: <b>Investigación sintética</b></span><span>Estado: <b>Requiere validación con personas</b></span>
        <span>Alcance: <b class="num">${D.alcance.sesiones} sesiones sintéticas · ${D.alcance.perfiles} perfiles</b></span></div>
      <div class="aviso" role="note"><span aria-hidden="true">◆</span><span><b>Investigación sintética.</b> Los resultados vienen de perfiles sintéticos construidos sobre evidencia, no de personas.
        Son hipótesis a validar con usuarios reales: «7 de 8 sesiones del panel», nunca porcentajes de clientes.</span></div>
      <div class="kpis">${D.kpis.map(kpi).join('')}</div>
      ${D.kpis_nota ? `<p class="cap">${esc(D.kpis_nota)}</p>` : ''}
    </div>
    ${ej ? '' : `<nav class="pestanas" aria-label="Áreas del reporte"><div class="env" role="tablist">${VISTAS.map((v, i) => `<button role="tab" aria-selected="${v[0] === est.pestana}" aria-controls="contenido" data-pestana="${v[0]}"><span class="n">0${i + 1}</span>${v[1]}</button>`).join('')}</div></nav>`}
    <main id="contenido" class="env" tabindex="-1" role="${ej ? 'main' : 'tabpanel'}">${vista[2]()}</main>
    <footer class="env cap" style="padding-bottom:40px">Arnés de investigación UX sintética · ${esc(D.entregable)} · ${esc(D.autor)} · <a href="${esc(D.detalle)}">Reporte completo</a></footer>
    <div class="tooltip" id="tip" role="tooltip"></div>`;
    enlazarTooltip();
  }

  // ---------------------------------------------------------------- tooltip
  function enlazarTooltip() {
    const tip = $('#tip');
    const mostrar = (el, x, y) => { tip.innerHTML = esc(el.dataset.tip).replace(/\n/g, '<br>'); tip.style.display = 'block';
      const r = tip.getBoundingClientRect(); tip.style.left = Math.min(x + 12, innerWidth - r.width - 8) + 'px'; tip.style.top = Math.min(y + 12, innerHeight - r.height - 8) + 'px'; };
    $$('[data-tip]').forEach((el) => {
      el.addEventListener('mousemove', (ev) => mostrar(el, ev.clientX, ev.clientY));
      el.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
      el.addEventListener('focus', () => { const r = el.getBoundingClientRect(); mostrar(el, r.left, r.bottom); });
      el.addEventListener('blur', () => { tip.style.display = 'none'; });
    });
    const caja = $('#caja-conf svg');
    if (caja) {
      const c = graficoConfianza();
      $$('.zona-tip', caja).forEach((z) => {
        const i = +z.dataset.i;
        const texto = () => `${c.ets[i]}\n` + c.series.filter((s) => est.series.has(s.id)).map((s) => `${s.nombre}: ${r1(s.vals[i])}`).join('\n');
        z.addEventListener('mousemove', (ev) => { tip.innerHTML = esc(texto()).replace(/\n/g, '<br>'); tip.style.display = 'block';
          tip.style.left = Math.min(ev.clientX + 12, innerWidth - 220) + 'px'; tip.style.top = (ev.clientY + 12) + 'px'; });
        z.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
      });
    }
  }

  // ---------------------------------------------------------------- cajón de evidencia
  let volverA = null;
  function abrirCajon(html, etiqueta) {
    cerrarCajon(true);
    volverA = document.activeElement;
    const velo = document.createElement('div'); velo.className = 'velo'; velo.dataset.cerrar = '1';
    const c = document.createElement('aside'); c.className = 'cajon'; c.setAttribute('role', 'dialog'); c.setAttribute('aria-modal', 'true'); c.setAttribute('aria-label', etiqueta);
    c.innerHTML = `<button class="cerrar" data-cerrar="1" aria-label="Cerrar">✕</button>${html}`;
    document.body.append(velo, c);
    requestAnimationFrame(() => { velo.classList.add('abierto'); c.classList.add('abierto'); $('.cerrar', c).focus(); });
  }
  function cerrarCajon(inmediato) {
    const c = $('.cajon'), v = $('.velo'); if (!c) return;
    c.remove(); v && v.remove();
    if (!inmediato && volverA && volverA.isConnected) volverA.focus();
  }
  function cajonHallazgo(id) {
    const h = H[id]; if (!h) return;
    const ses = h.sesiones.map((s) => `<button class="ver-tabla" data-sesion="${esc(s)}">${esc(s)}</button>`).join(' · ');
    abrirCajon(`<span class="hid cap">Hallazgo ${esc(h.id)} · ${esc(h.pantalla)}</span><h2>${esc(h.titulo)}</h2>
      <div class="chips">${sev(h)} ${etq('Confianza ' + (CONF[h.confianza] || h.confianza))} ${h.fuente.map((f) => etq(f, f === 'Sesión sintética' ? 'sint' : '')).join('')}</div>
      <h3>Sesiones que lo sustentan</h3><p>${ses || '<span class="vacio-msg">Hallazgo de auditoría: sin sesiones asociadas.</span>'}</p>
      <p class="cap num">${frec(h)}${h.metricas.n ? ` · ${h.metricas.n} observaciones en la pantalla · confianza media ${r1(h.metricas.c)} · fricción media ${r1(h.metricas.f)}` : ''}</p>
      ${h.capturas.length ? `<h3>Capturas</h3><div class="galeria">${h.capturas.map((c) => `<figure><img src="${c.src}" alt="Captura de ${esc(h.pantalla)} en la sesión ${esc(c.s)}"><figcaption>${esc(c.s)}</figcaption></figure>`).join('')}</div>` : ''}
      ${h.citas.length ? `<h3>Pensamientos ${etq('Perfil simulado', 'sint')}</h3>${h.citas.map((q) => `<blockquote class="cita">«${esc(q.txt)}»<small>${esc(PERF[q.p]?.nombre || q.p)} · ${esc(q.s)} · confianza ${q.c} · fricción ${q.f} · frase sintética, no una cita de una persona</small></blockquote>`).join('')}` : ''}
      ${h.auditoria.length ? `<h3>Auditoría ${etq('Modelo')}</h3>${h.auditoria.map((a) => `<p><b>${esc(a.criterio)}</b> ${esc(a.nombre)} · ${esc(a.ev)} · severidad ${a.sev}<br>${esc(a.problema)}</p>`).join('')}` : ''}
      <h3>Fuente</h3><p class="cap">Pantalla ${esc(h.pid || '—')}${h.heuristica ? ' · ' + esc(h.heuristica) : ''}${h.wcag ? ' · WCAG ' + esc(h.wcag) : ''}${h.walkthrough ? ' · cognitive walkthrough, pregunta ' + h.walkthrough : ''}</p>
      <p class="cap">${esc(h.evidencia)}</p>`, `Evidencia de ${h.id}`);
  }
  function cajonSesion(id) {
    const s = D.sesiones.find((x) => x.id === id); if (!s) return;
    abrirCajon(`<span class="cap">${etq('Sesión sintética', 'sint')} ${esc(s.t)}</span><h2>${esc(s.id)} · ${esc(PERF[s.p]?.completo || s.p)}</h2>
      <p class="num"><b>${esc(RES[s.resultado] || s.resultado)}</b> en ${s.pasos} pasos · CES ${s.ces ?? '—'} · confianza mínima ${s.cmin ?? '—'}</p>
      ${s.ces_txt ? `<blockquote class="cita">«${esc(s.ces_txt)}»<small>Calificación de facilidad · perfil simulado</small></blockquote>` : ''}
      ${s.cierre ? `<h3>Pregunta de cierre</h3><p><b>${esc(s.cierre.pregunta)}</b></p><blockquote class="cita">«${esc(s.cierre.respuesta)}» ${esc(s.cierre.por_que || '')}<small>Perfil simulado · confianza ${s.cierre.confianza ?? '—'}</small></blockquote>` : ''}
      <h3>Paso a paso</h3>${s.recorrido.map((p) => `<div class="paso"><span class="num pt">${p.n}</span><div><b>${esc(p.e)}</b> · ${esc(p.acc)}${p.r === 'no' ? ' · sin respuesta' : p.r === 'fuera_de_marcas' ? ' · fuera de las zonas' : ''}<br><span class="cap">«${esc(p.txt)}»</span></div><span class="num pt">conf. ${p.c}<br>fric. ${p.f}</span></div>`).join('')}`, `Sesión ${s.id}`);
  }

  // ---------------------------------------------------------------- eventos
  document.addEventListener('click', (ev) => {
    const t = ev.target.closest('[data-modo],[data-pestana],[data-hallazgo],[data-sesion],[data-serie],[data-perfil],[data-accion],[data-cerrar]');
    if (!t) return;
    if (t.dataset.cerrar) return cerrarCajon();
    if (t.dataset.modo) { est.modo = t.dataset.modo; return pintar(); }
    if (t.dataset.pestana) { est.pestana = t.dataset.pestana; pintar(); $(`[data-pestana="${est.pestana}"]`)?.focus(); return; }
    if (t.dataset.hallazgo) return cajonHallazgo(t.dataset.hallazgo);
    if (t.dataset.sesion) return cajonSesion(t.dataset.sesion);
    if (t.dataset.serie) { const s = t.dataset.serie; est.series.has(s) ? est.series.delete(s) : est.series.add(s); pintar(); $(`[data-serie="${s}"]`)?.focus(); return; }
    if (t.dataset.perfil) { est.perfil = est.perfil === t.dataset.perfil ? 'todos' : t.dataset.perfil; pintar(); $(`[data-perfil="${t.dataset.perfil}"]`)?.focus(); return; }
    if (t.dataset.accion === 'tabla-conf') { est.tablaConf = !est.tablaConf; pintar(); $('[data-accion="tabla-conf"]')?.focus(); }
  });
  document.addEventListener('change', (ev) => {
    const t = ev.target;
    if (t.dataset.global) { est[t.dataset.global] = t.value; pintar(); $(`[data-global="${t.dataset.global}"]`)?.focus(); }
    if (t.dataset.filtro) { est[t.dataset.filtro] = t.value; pintar(); $(`[data-filtro="${t.dataset.filtro}"]`)?.focus(); }
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') return cerrarCajon();
    const t = ev.target;
    if ((ev.key === 'Enter' || ev.key === ' ') && t.matches && t.matches('tr[data-sesion],tr[data-hallazgo],g[data-hallazgo]')) { ev.preventDefault(); t.dataset.sesion ? cajonSesion(t.dataset.sesion) : cajonHallazgo(t.dataset.hallazgo); }
    if (t.getAttribute && t.getAttribute('role') === 'tab' && (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft')) {
      const i = VISTAS.findIndex((v) => v[0] === est.pestana), j = (i + (ev.key === 'ArrowRight' ? 1 : -1) + VISTAS.length) % VISTAS.length;
      est.pestana = VISTAS[j][0]; pintar(); $(`[data-pestana="${est.pestana}"]`)?.focus();
    }
    if (ev.key === 'Tab' && $('.cajon')) {   // el foco se queda dentro del cajón
      const f = $$('button, a, [tabindex="0"]', $('.cajon')); if (!f.length) return;
      if (ev.shiftKey && document.activeElement === f[0]) { ev.preventDefault(); f[f.length - 1].focus(); }
      else if (!ev.shiftKey && document.activeElement === f[f.length - 1]) { ev.preventDefault(); f[0].focus(); }
    }
  });

  pintar();
})();
