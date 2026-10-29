
async (page) => {
  const C = {"material": "web", "captura": "/Users/alexisvaldez/Documents/claude/harness-usuarios-sinteticos/estudios/2026-10-28-ou2-pwa-mvp/datos/tecnico/_tmp.png", "accion": {"tipo": "mecanico", "pasos": [{"nombre": "¿En cuántas semanas quieres pagar?"}]}, "overlay": null, "movil": true, "pantalla_sel": ".marco", "pantalla_attr": "data-estado", "max_ms": 60000};
  
const zonasWeb = async (page) => page.evaluate(() => {
  const sel = 'a[href],button,input:not([type=hidden]),select,textarea,summary,label[for],[role=button],[role=link],' +
              '[role=checkbox],[role=radio],[role=tab],[role=option],[role=menuitem],[role=switch],[onclick],[tabindex]:not([tabindex="-1"])';
  const out = [];
  for (const el of document.querySelectorAll(sel)) {
    if (el.closest('[id^="arnes-"]')) continue;              // subtítulos y marcas del arnés
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || +st.opacity === 0) continue;
    const cx = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), cy = Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1);
    const top = document.elementFromPoint(cx, cy);
    if (top && !el.contains(top) && !top.contains(el) && !top.closest('[id^="arnes-"]')) continue;
    if (out.some(o => o.el.contains(el) && o.tipo !== 'label')) continue;
    const t = el.tagName.toLowerCase(), tipoInput = t === 'input' ? (el.type || 'text') : '';
    const lab = el.labels && el.labels[0] ? el.labels[0].innerText : '';
    const etiqueta = (el.getAttribute('aria-label') || lab || el.innerText || el.placeholder || el.title || el.name || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    const z = { el, x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height),
                tocar: [Math.round(cx), Math.round(cy)], tipo: t, editable: (t === 'input' && !['range', 'checkbox', 'radio', 'button', 'submit'].includes(tipoInput)) || t === 'textarea' || el.isContentEditable,
                etiqueta, rol: el.getAttribute('role') || '', desactivado: !!(el.disabled || el.getAttribute('aria-disabled') === 'true') };
    if (t === 'input' || t === 'textarea') { z.valor = String(el.value || '').slice(0, 60); z.tipo_input = tipoInput; }
    if (tipoInput === 'range') { z.min = +el.min || 0; z.max = +(el.max || 100); z.valor = el.value; }
    const marcado = el.getAttribute('aria-checked') || el.getAttribute('aria-selected') || (el.checked ? 'true' : null);
    if (marcado === 'true') z.marcado = true;
    out.push(z);
  }
  return { marco: { x: 0, y: 0, w: innerWidth, h: innerHeight }, zonas: out.map(({ el, ...o }) => o) };
});

  
const senales = async (page) => page.evaluate(() => {
  const vis = el => { const r = el.getBoundingClientRect(), st = getComputedStyle(el); return r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none'; };
  const txt = el => (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 160);
  const errores = [...document.querySelectorAll('[aria-invalid="true"],[role="alert"],[class*="error" i],[class*="invalid" i]')].filter(vis).map(txt).filter(Boolean);
  const campos = [...document.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=submit]):not([type=reset]),select,textarea')].filter(vis).length;
  const barra = [...document.querySelectorAll('[role="progressbar"],progress')].filter(vis).length;
  const m = (document.body.innerText || '').match(/paso\s+\d+\s+de\s+\d+|\b\d+\s*(?:de|\/)\s*\d+\s+pasos?\b/i);
  return { errores_validacion: [...new Set(errores)], campos, progreso: m ? m[0] : (barra ? 'barra de progreso' : null), permisos: window.__arnesPermisos || [] };
}).catch(() => ({}));

  
const firma = async (page, C) => page.evaluate((C) => {
  const raiz = C.pantalla_sel ? document.querySelector(C.pantalla_sel) : null;
  const estado = raiz ? (C.pantalla_attr ? raiz.getAttribute(C.pantalla_attr) : raiz.id) : null;
  const ocupado = !!document.querySelector('[aria-busy="true"]:not([id^="arnes-"])');
  const anim = document.getAnimations ? document.getAnimations().filter(a => {
    const t = a.effect && a.effect.target, h = t && t.getRootNode && t.getRootNode().host;
    if (h && h.id === 'arnes-capa') return false;
    const it = a.effect && a.effect.getTiming ? a.effect.getTiming().iterations : 1;
    return a.playState === 'running' && it !== Infinity; }).length : 0;
  const texto = (document.body.innerText || '').replace(/\d+/g, '#');
  const valores = [...document.querySelectorAll('input,textarea,select')].map(e => e.value).join('|');
  return { estado, ocupado, anim, sig: [estado, texto.length, texto.slice(0, 3000), valores, document.querySelectorAll('body *').length].join('§') };
}, C).catch(() => ({ estado: null, ocupado: false, anim: 0, sig: Math.random() }));

  
const capa = async (page, html, toque) => page.evaluate(({ html, toque }) => {
  let host = document.getElementById('arnes-capa');
  if (!host) {
    host = document.createElement('div'); host.id = 'arnes-capa';
    host.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none';
    const raiz = host.attachShadow({ mode: 'closed' }); window.__arnesRaiz = raiz;
    raiz.innerHTML = '<style>.sub{position:absolute;left:8px;right:8px;top:8px;font:13px/1.4 -apple-system,"Segoe UI",sans-serif;' +
      'color:#EAF2EE;background:rgba(6,42,34,.88);border:1px solid #2E7D57;border-radius:10px;padding:8px 10px;max-height:34%;overflow:hidden}' +
      '.sub:empty{display:none}.t{position:absolute;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;' +
      'border:3px solid #ff4081;background:rgba(255,64,129,.25);animation:t .7s ease-out forwards}' +
      '@keyframes t{from{transform:scale(.4);opacity:1}to{transform:scale(1.3);opacity:0}}</style><div class="sub"></div>';
    document.documentElement.appendChild(host);
  }
  const raiz = window.__arnesRaiz;
  if (html !== undefined && html !== null) raiz.querySelector('.sub').innerHTML = html;
  if (toque) { const d = document.createElement('div'); d.className = 't'; d.style.left = toque[0] + 'px'; d.style.top = toque[1] + 'px';
    raiz.appendChild(d); setTimeout(() => d.remove(), 800); }
}, { html, toque }).catch(() => {});

  if (C.instrumentar) { await page.context().addInitScript(() => {
if (!window.__arnesInst) { window.__arnesInst = 1; window.__arnesPermisos = [];
  const md = navigator.mediaDevices;
  if (md && md.getUserMedia) { const o = md.getUserMedia.bind(md); md.getUserMedia = (c) => { window.__arnesPermisos.push('cámara o micrófono'); return o(c); }; }
  if (navigator.geolocation) { const g = navigator.geolocation.getCurrentPosition.bind(navigator.geolocation);
    navigator.geolocation.getCurrentPosition = (...a) => { window.__arnesPermisos.push('ubicación'); return g(...a); };
    const w = navigator.geolocation.watchPosition.bind(navigator.geolocation);
    navigator.geolocation.watchPosition = (...a) => { window.__arnesPermisos.push('ubicación'); return w(...a); }; }
  if (window.Notification && Notification.requestPermission) { const n = Notification.requestPermission.bind(Notification);
    Notification.requestPermission = (...a) => { window.__arnesPermisos.push('notificaciones'); return n(...a); }; }
}
}); await page.evaluate(() => {
if (!window.__arnesInst) { window.__arnesInst = 1; window.__arnesPermisos = [];
  const md = navigator.mediaDevices;
  if (md && md.getUserMedia) { const o = md.getUserMedia.bind(md); md.getUserMedia = (c) => { window.__arnesPermisos.push('cámara o micrófono'); return o(c); }; }
  if (navigator.geolocation) { const g = navigator.geolocation.getCurrentPosition.bind(navigator.geolocation);
    navigator.geolocation.getCurrentPosition = (...a) => { window.__arnesPermisos.push('ubicación'); return g(...a); };
    const w = navigator.geolocation.watchPosition.bind(navigator.geolocation);
    navigator.geolocation.watchPosition = (...a) => { window.__arnesPermisos.push('ubicación'); return w(...a); }; }
  if (window.Notification && Notification.requestPermission) { const n = Notification.requestPermission.bind(Notification);
    Notification.requestPermission = (...a) => { window.__arnesPermisos.push('notificaciones'); return n(...a); }; }
}
}).catch(() => {}); }
  const oculta = { scale: 'css', style: '#arnes-capa{visibility:hidden!important}' };
  const url0 = page.url(), f0 = await firma(page, C);
  if (C.overlay !== null && C.overlay !== undefined) await capa(page, C.overlay, null);
  const antes = C.accion ? await page.screenshot(oculta) : null;
  const a = C.accion, movil = !!C.movil;
  const tocar = async (x, y) => {
    await capa(page, null, [x, y]);
    await page.mouse.move(x, y, { steps: 4 }); await page.waitForTimeout(C.pausa_toque_ms || 150);
    if (movil) await page.touchscreen.tap(x, y); else { await page.mouse.down(); await page.waitForTimeout(60); await page.mouse.up(); }
  };
  const porRol = (s) => {
    const l = s.selector ? page.locator(s.selector) : s.etiqueta ? page.getByLabel(s.etiqueta, { exact: !!s.exacto })
      : page.getByRole(s.rol || 'button', s.nombre ? { name: s.nombre, exact: !!s.exacto } : {});
    return s.ultimo ? l.last() : l.first(); };
  const mecanico = async (s) => {        // acciones del investigador por rol y texto (preparación, ruta mecánica)
    if (s.esperar_ms) { await page.waitForTimeout(s.esperar_ms); return; }
    const el = porRol(s), tw = Date.now();
    await el.waitFor({ state: 'visible', timeout: s.timeout || 15000 });
    esperaElemento += Date.now() - tw;     // lo que tardó en aparecer: espera del paso anterior (carga, validación)
    const b = await el.boundingBox();
    if (b) await capa(page, null, [b.x + b.width / 2, b.y + b.height / 2]);
    if (s.teclear_patron) {               // un código que la app muestra (p. ej. el SMS simulado): se lee de la pantalla
      const re = new RegExp(s.teclear_patron, 's'); let m = null; const t0 = Date.now();
      while (!m && Date.now() - t0 < (s.timeout || 15000)) { m = (await page.evaluate(() => document.body.innerText)).match(re); if (!m) await page.waitForTimeout(300); }
      if (!m) throw new Error('no apareció en pantalla el texto ' + s.teclear_patron);
      await el.click(); await page.keyboard.type(m[1] || m[0], { delay: 50 }); return;
    }
    if (s.llenar !== undefined) await el.fill(String(s.llenar));
    else if (s.teclear !== undefined) { await el.click(); await page.keyboard.type(String(s.teclear), { delay: 50 }); }
    else await el.click();
  };
  let error_accion = null, esperaElemento = 0;
  try {
    if (a && a.tipo === 'recargar') await page.reload({ waitUntil: 'domcontentloaded' });
    else if (a && a.tipo === 'ir') await page.goto(a.url, { waitUntil: 'domcontentloaded' });
    else if (a && a.tipo === 'limpiar_datos') {
      await page.evaluate(async () => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {}
        if (indexedDB.databases) for (const d of await indexedDB.databases()) await new Promise(ok => { const r = indexedDB.deleteDatabase(d.name); r.onsuccess = r.onerror = r.onblocked = () => ok(); }); });
      await page.goto(a.url, { waitUntil: 'domcontentloaded' });
    }
    else if (a && (a.tipo === 'tocar' || a.tipo === 'escribir')) {
      await tocar(a.x, a.y);
      if (a.tipo === 'escribir') {
        await page.waitForTimeout(300);
        // escribir reemplaza lo que había en el campo [SUPUESTO METODOLÓGICO]
        await page.evaluate(() => { const e = document.activeElement; if (e && e.select) e.select(); }).catch(() => {});
        await page.keyboard.type(a.texto || '', { delay: 45 });
      }
    } else if (a && a.tipo === 'desplazar') {
      await page.mouse.move(a.x, a.y); await page.mouse.wheel(0, a.dy);
    } else if (a && a.tipo === 'tecla') await page.keyboard.press(a.tecla);
    else if (a && a.tipo === 'volver') await page.goBack();
    else if (a && a.tipo === 'arrastrar') { await page.mouse.move(a.x, a.y); await page.mouse.down(); await page.mouse.move(a.x2, a.y2, { steps: 12 }); await page.mouse.up(); }
    else if (a && a.tipo === 'tocar_texto') await mecanico({ rol: 'button', nombre: a.texto });
    else if (a && a.tipo === 'mecanico') for (const s of a.pasos) {
      if (a.hasta) {         // esperar a que termine la carga en curso antes de decidir si ya se llegó
        let fx = await firma(page, C); const tw = Date.now();
        while (fx.ocupado && Date.now() - tw < (s.timeout || 15000)) { await page.waitForTimeout(250); fx = await firma(page, C); }
        if (fx.estado === a.hasta) break;
      }
      await mecanico(s); await page.waitForTimeout(s.pausa_ms || 350);
    }
  } catch (e) { error_accion = String(e.message || e).split('\n')[0].slice(0, 200); }
  // asentar: la misma firma `estable` veces seguidas, sin `aria-busy` ni animaciones finitas. La espera del sistema va
  // de la acción al primer sondeo de esa racha; si hubo indicador de carga se registra cuánto duró.
  const t0 = Date.now(), pausa = C.pausa_ms || 300, estable = C.estable || 2, max = C.max_ms || 30000;
  let prev = null, racha = 0, tEstable = null, asentada = false, i = 0, tPrev = t0, vioCarga = false, f = f0;
  while (Date.now() - t0 < max) {
    await page.waitForTimeout(pausa);
    f = await firma(page, C); const tf = Date.now(); i++;
    if (f.ocupado) vioCarga = true;
    if (prev && f.sig === prev && !f.ocupado && !f.anim) { if (racha === 0) tEstable = tPrev; racha++; if (racha >= estable) { asentada = true; break; } }
    else { racha = 0; tEstable = null; }
    prev = f.sig; tPrev = tf;
  }
  const espera = asentada ? Math.max(0, tEstable - t0) : Date.now() - t0;
  await page.screenshot({ ...oculta, path: C.captura });
  const z = await zonasWeb(page);
  const texto = await page.evaluate(() => document.body.innerText.slice(0, 4000)).catch(() => '');
  const sen = await senales(page);
  const despues = antes ? await page.screenshot(oculta) : null;
  return JSON.stringify({ url_antes: url0, url: page.url(), cambio_url: page.url() !== url0, estado_antes: f0.estado, estado: f.estado,
    cambio_estado: f.estado !== f0.estado, cambio_firma: f.sig !== f0.sig,
    cambio_imagen: antes ? !antes.equals(despues) : null, asentada, intentos: i, vio_carga: vioCarga, error_accion, espera_elemento_ms: esperaElemento,
    marco: z.marco, zonas: z.zonas || [], error: z.error || null, texto, espera_ms: a ? espera : null,
    host: (() => { try { return new URL(page.url()).host; } catch (e) { return ''; } })(), paginas: page.context().pages().length, ...sen });
}
