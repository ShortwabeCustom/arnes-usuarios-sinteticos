"""Navegador para recorridos: envoltorio de playwright-cli que hace cada paso en una sola llamada.

Un paso = acción → asentar → captura → mapa de zonas activas → URL. Todo dentro de un `run-code`,
así no se pagan cinco procesos por toque.

Dos materiales, un solo modo de interacción (por coordenada):

- **figma**: el prototipo se dibuja en <canvas>, sin árbol de accesibilidad. Las zonas activas salen de los
  resaltados azules que Figma muestra al tocar fuera de un hotspot (dentro del overlay si hay uno abierto); el
  barrido de cursor queda de respaldo. No se cambia el tamaño de la ventana: el encuadre es parte del prototipo.
- **web**: sitio real. Las zonas son los elementos interactivos visibles y no tapados del DOM, y el
  viewport se fija al del dispositivo del estudio.

Lecciones heredadas del skill de auditoría que este módulo aplica:
- asentar por estabilidad de imagen, nunca con `sleep` fijo;
- un toque sin efecto NO declara un marco terminal: se registra como «sin respuesta» y el perfil
  decide qué hace después;
- el node-id (Figma) o la URL (web) es la señal de estado más barata;
- toda captura va en píxeles de página (`scale: 'css'`): en una pantalla Retina con la ventana visible, la captura
  saldría al doble y las zonas y los toques no coincidirían con la imagen (piloto de OU 2.0, 22/10/2026).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

# CLI de Playwright: el del repositorio (versión fija, bin/playwright-cli); PWCLI lo reemplaza.
PW = os.path.expanduser(os.environ.get("PWCLI") or str(Path(__file__).resolve().parent.parent / "bin" / "playwright-cli"))

JS_ZONAS_FIGMA = r"""
const zonasFigma = async (page) => page.evaluate(() => {
  const PASO = 12, MIN = 3;
  const cv = document.querySelector('canvas');
  if (!cv) return { error: 'no hay canvas', zonas: [] };
  const r = cv.getBoundingClientRect();
  const cols = Math.floor(r.width / PASO), filas = Math.floor(r.height / PASO), g = [];
  for (let j = 0; j < filas; j++) { const f = []; for (let i = 0; i < cols; i++) {
    const x = r.left + i * PASO + PASO / 2, y = r.top + j * PASO + PASO / 2;
    cv.dispatchEvent(new MouseEvent('mousemove', { clientX: x, clientY: y, bubbles: true, cancelable: true, view: window }));
    const el = document.elementFromPoint(x, y); f.push(el && getComputedStyle(el).cursor === 'pointer' ? 1 : 0);
  } g.push(f); }
  const v = g.map(f => f.map(() => false)), zonas = [];
  for (let j = 0; j < filas; j++) for (let i = 0; i < cols; i++) {
    if (!g[j][i] || v[j][i]) continue;
    let a0 = i, a1 = i, b0 = j, b1 = j, n = 0; const p = [[i, j]]; v[j][i] = true;
    while (p.length) { const [a, b] = p.pop(); n++; a0 = Math.min(a0, a); a1 = Math.max(a1, a); b0 = Math.min(b0, b); b1 = Math.max(b1, b);
      for (const [da, db] of [[1,0],[-1,0],[0,1],[0,-1]]) { const na = a + da, nb = b + db;
        if (na >= 0 && na < cols && nb >= 0 && nb < filas && g[nb][na] && !v[nb][na]) { v[nb][na] = true; p.push([na, nb]); } } }
    if (n < MIN) continue;
    const x = Math.round(r.left + a0 * PASO), y = Math.round(r.top + b0 * PASO), w = (a1 - a0 + 1) * PASO, h = (b1 - b0 + 1) * PASO;
    zonas.push({ x, y, w, h, tocar: [Math.round(x + w / 2), Math.round(y + h / 2)], tipo: 'zona', editable: false, etiqueta: '' });
  }
  zonas.sort((a, b) => (a.y - b.y) || (a.x - b.x));
  return { marco: { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) }, zonas };
});
"""

JS_ZONAS_WEB = r"""
const zonasWeb = async (page) => page.evaluate(() => {
  const sel = 'a[href],button,input:not([type=hidden]),select,textarea,summary,label[for],[role=button],[role=link],' +
              '[role=checkbox],[role=radio],[role=tab],[role=option],[role=menuitem],[role=switch],[onclick],[tabindex]:not([tabindex="-1"])';
  const out = [];
  for (const el of document.querySelectorAll(sel)) {
    if (el.closest('[id^="arnes-"]')) continue;              // subtítulos y marcas del arnés
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none') continue;
    let cx = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), cy = Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1);
    let top = document.elementFromPoint(cx, cy);
    if (top && top !== el && !el.contains(top)) {
      // un enlace partido en dos líneas: el centro de su caja cae en el texto de al lado; se prueba cada línea
      for (const q of el.getClientRects()) {
        if (q.width < 4 || q.height < 4) continue;
        const x = q.left + q.width / 2, y = q.top + q.height / 2, t = document.elementFromPoint(x, y);
        if (t && (t === el || el.contains(t))) { cx = Math.round(x); cy = Math.round(y); top = t; break; }
      }
    }
    // transparente: solo cuenta si es el que recibe el toque (p. ej. el campo real sobre las casillas de un código)
    if (+st.opacity === 0 && top !== el) continue;
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
"""

# Firma del estado de la página para asentar en web: pantalla, texto (sin cifras: una cuenta regresiva no es un cambio),
# valores de los campos y cuántos elementos hay. Sin animaciones finitas en curso (una hoja que sube) y sin
# `aria-busy`. Las animaciones infinitas (un spinner) no cuentan: el spinner es la espera, que se mide aparte.
JS_FIRMA = r"""
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
"""

JS_INSTRUMENTO = r"""
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
"""

JS_SENALES = r"""
const senales = async (page) => page.evaluate(() => {
  const vis = el => { const r = el.getBoundingClientRect(), st = getComputedStyle(el); return r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none'; };
  const txt = el => (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 160);
  const errores = [...document.querySelectorAll('[aria-invalid="true"],[role="alert"],[class*="error" i],[class*="invalid" i]')].filter(vis).map(txt).filter(Boolean);
  const campos = [...document.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=submit]):not([type=reset]),select,textarea')].filter(vis).length;
  const barra = [...document.querySelectorAll('[role="progressbar"],progress')].filter(vis).length;
  const m = (document.body.innerText || '').match(/paso\s+\d+\s+de\s+\d+|\b\d+\s*(?:de|\/)\s*\d+\s+pasos?\b/i);
  return { errores_validacion: [...new Set(errores)], campos, progreso: m ? m[0] : (barra ? 'barra de progreso' : null), permisos: window.__arnesPermisos || [] };
}).catch(() => ({}));
"""

JS_PISTAS = r"""
async (page) => {
  // Figma resalta en azul lo tocable cuando se toca algo que no lo es (hotspot hints). Captura antes, toque en el
  // punto que eligió Python (fondo, o dentro del overlay si hay uno abierto), captura con resaltados y, ya
  // apagados, una tercera para comprobar que el toque no cambió la pantalla.
  const C = __CFG__;
  await page.screenshot({ scale: 'css', path: C.base });
  await page.mouse.click(C.x, C.y);
  await page.waitForTimeout(C.pistas_ms || 160);
  await page.screenshot({ scale: 'css', path: C.pistas });
  await page.mouse.move(C.x, C.y);
  await page.waitForTimeout(700);
  await page.screenshot({ scale: 'css', path: C.despues });
  return JSON.stringify({ url: page.url() });
}
"""

JS_PASO = r"""
async (page) => {
  const C = __CFG__;
  __ZONAS__
  __SENALES__
  if (C.instrumentar) { await page.context().addInitScript(__INSTR__); await page.evaluate(__INSTR__).catch(() => {}); }
  const hash = (b) => { let h = 0; for (let i = 0; i < b.length; i += 97) h = (h * 31 + b[i]) | 0; return h + ':' + b.length; };
  const ov = async (html) => page.evaluate(({ html, pos }) => {
    let d = document.getElementById('arnes-ov');
    if (!html) { if (d) d.remove(); return; }
    if (!d) { d = document.createElement('div'); d.id = 'arnes-ov'; document.body.appendChild(d); }
    d.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;font:14px/1.45 -apple-system,"Segoe UI",sans-serif;' +
      'color:#EAF2EE;background:rgba(6,42,34,.95);border:1px solid #2E7D57;border-radius:12px;padding:12px 14px;max-width:260px;' + pos;
    d.innerHTML = html;
  }, { html, pos: C.overlay_pos || (C.material === 'figma' ? 'left:16px;top:16px' : 'right:12px;top:12px') }).catch(() => {});
  // En Figma la burbuja queda fija fuera del teléfono (la captura se recorta al teléfono): ocultarla y mostrarla en
  // cada sondeo hacía parpadear la ventana. En web cubre la pantalla, así que se oculta para capturar.
  const fija = C.material === 'figma';
  const url0 = page.url();
  if (fija && C.overlay && C.accion) await ov(C.overlay);
  const antes = C.accion ? await page.screenshot({ scale: 'css' }) : null;
  if (!fija && C.overlay && C.accion) await ov(C.overlay);
  const a = C.accion;
  if (a && a.tipo === 'recargar') await page.reload({ waitUntil: 'domcontentloaded' }).catch(() => {});
  if (a) {
    if (a.tipo === 'tocar' || a.tipo === 'escribir') {
      // Como una persona: llegar al botón, detenerse y tocar. Mover y hacer clic en el mismo instante hacía que
      // Figma tomara el toque como hecho fuera del botón (lo resaltaba en azul y no navegaba): piloto de OU 2.0.
      await page.mouse.move(a.x, a.y, { steps: 4 }); await page.waitForTimeout(C.pausa_toque_ms || 150);
      await page.mouse.down(); await page.waitForTimeout(60); await page.mouse.up();
      if (a.tipo === 'escribir') { await page.waitForTimeout(300); await page.keyboard.type(a.texto || '', { delay: 40 }); }
    } else if (a.tipo === 'desplazar') {
      await page.mouse.move(a.x, a.y); await page.mouse.wheel(0, a.dy);
    } else if (a.tipo === 'tecla') {
      await page.keyboard.press(a.tecla);
    } else if (a.tipo === 'volver') {
      await page.goBack().catch(() => {});
    } else if (a.tipo === 'arrastrar') {
      await page.mouse.move(a.x, a.y); await page.mouse.down(); await page.mouse.move(a.x2, a.y2, { steps: 12 }); await page.mouse.up();
    } else if (a.tipo === 'tocar_texto') {      // botones HTML fuera del prototipo: banner de cookies, avisos
      // clic por JavaScript: el clic de Playwright desplaza la página para mostrar el botón y movía todo el
      // prototipo hacia un lado (0 zonas en la primera pantalla del panel de OU 2.0)
      const b = page.getByRole('button', { name: a.texto }).first();
      await b.waitFor({ timeout: 8000 }).catch(() => {});
      const el = (await b.count()) ? b : page.getByText(a.texto, { exact: true }).first();
      await el.evaluate(n => n.click()).catch(() => {});
      await page.evaluate(() => { window.scrollTo(0, 0); document.scrollingElement && (document.scrollingElement.scrollLeft = 0); }).catch(() => {});
    } else if (a.tipo === 'ir') {
      await page.goto(a.url, { waitUntil: 'domcontentloaded' }).catch(() => {});
    }
  }
  // asentar: sondeo cada `pausa_ms` (300) hasta ver la misma imagen `estable` veces seguidas (≈ 0.6 s quieta),
  // con techo de `max_ms` para contenido que se mueve solo. La espera del sistema es el momento de la primera
  // captura de esa racha estable menos el momento de la acción: granularidad de una pausa.
  const t0 = Date.now(), pausa = C.pausa_ms || 300, estable = C.estable || 2, max = C.max_ms || 12000;
  let prev = null, tPrev = t0, racha = 0, tEstable = null, asentada = false, i = 0;
  while (Date.now() - t0 < max) {
    await page.waitForTimeout(pausa);
    if (C.overlay && !fija) await ov(null);
    const b = await page.screenshot({ scale: 'css' }), tb = Date.now();
    if (prev && hash(b) === hash(prev) && b.equals(prev)) {
      if (racha === 0) tEstable = tPrev;
      racha++;
      if (racha >= estable) { asentada = true; break; }
    } else { racha = 0; tEstable = null; }
    prev = b; tPrev = tb; i++;
    if (C.overlay && a && !fija) await ov(C.overlay);
  }
  const espera = asentada ? Math.max(0, tEstable - t0) : Date.now() - t0;
  if (C.overlay && !fija) await ov(null);
  await page.screenshot({ scale: 'css', path: C.captura });
  const z = C.material === 'figma' ? await zonasFigma(page) : await zonasWeb(page);
  if (C.material === 'figma' && z.marco) await page.mouse.move(z.marco.x + 3, z.marco.y + 3);
  const despues = await page.screenshot({ scale: 'css' });
  const texto = C.material === 'web' ? await page.evaluate(() => document.body.innerText.slice(0, 4000)).catch(() => '') : '';
  const sen = C.material === 'web' ? await senales(page) : {};
  return JSON.stringify({ url_antes: url0, url: page.url(), cambio_url: page.url() !== url0,
    cambio_imagen: antes ? !antes.equals(prev || despues) : null, asentada, intentos: i + 1,
    marco: z.marco, zonas: z.zonas || [], error: z.error || null, texto, espera_ms: a ? espera : null,
    host: (() => { try { return new URL(page.url()).host; } catch (e) { return ''; } })(), paginas: page.context().pages().length, ...sen });
}
"""


# Capa del arnés en web, dentro de una sombra cerrada: el texto, las zonas, la firma y axe no la ven, y las capturas la
# ocultan con `style`. Subtítulos arriba (quién es, qué piensa, qué hace) y un círculo donde cae el toque. Sustituye a
# la burbuja que se ocultaba y se mostraba en cada sondeo y hacía parpadear la ventana.
JS_CAPA = r"""
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
"""

JS_PASO_WEB = r"""
async (page) => {
  const C = __CFG__;
  __ZONAS__
  __SENALES__
  __FIRMA__
  __CAPA__
  if (C.instrumentar) { await page.context().addInitScript(__INSTR__); await page.evaluate(__INSTR__).catch(() => {}); }
  const oculta = { scale: 'css', style: '#arnes-capa{visibility:hidden!important}' };
  // avisos pasajeros (SMS simulado, toasts, alertas): una persona los ve aunque duren segundos; el perfil tarda
  // ≈ 20 s en decidir, así que el arnés los vigila y se los cuenta
  const SEL_AVISOS = C.avisos_sel || '[role=alert],[role=status],.notificacion,[class*="toast" i],[class*="snackbar" i],[class*="notific" i]';
  const avisos = async () => page.evaluate((sel) => [...document.querySelectorAll(sel)].filter(el => {
      const r = el.getBoundingClientRect(), st = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none' && !el.closest('#arnes-capa'); })
    .map(el => (el.getAttribute('aria-label') || el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 200)).filter(t => t.length > 3), SEL_AVISOS).catch(() => []);
  const avisosAntes = new Set(await avisos()), vistos = new Set();
  const mirarAvisos = async () => { for (const t of await avisos()) if (!avisosAntes.has(t)) vistos.add(t); };
  const url0 = page.url(), f0 = await firma(page, C), paginas0 = new Set(page.context().pages());
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
      if (movil) {       // deslizar con el dedo: la rueda del mouse no mueve las listas internas en un celular emulado
        const cdp = await page.context().newCDPSession(page);
        await cdp.send('Input.synthesizeScrollGesture', { x: a.x, y: a.y, yDistance: -a.dy, speed: 1200, gestureSourceType: 'touch' }).catch(() => {});
        await cdp.detach().catch(() => {});
      } else { await page.mouse.move(a.x, a.y); await page.mouse.wheel(0, a.dy); }
    } else if (a && a.tipo === 'esperar') {
      const t1 = Date.now(); while (Date.now() - t1 < (a.ms || 5000)) { await page.waitForTimeout(250); await mirarAvisos(); }
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
    await mirarAvisos();
    if (f.ocupado) vioCarga = true;
    if (prev && f.sig === prev && !f.ocupado && !f.anim) { if (racha === 0) tEstable = tPrev; racha++; if (racha >= estable) { asentada = true; break; } }
    else { racha = 0; tEstable = null; }
    prev = f.sig; tPrev = tf;
  }
  const espera = asentada ? Math.max(0, tEstable - t0) : Date.now() - t0;
  // un enlace con target=_blank abre otra pestaña: se mira qué abrió, se cierra y se vuelve a la app (en un teléfono
  // la persona vería esa página y regresaría)
  let pestana = null;
  if (a && !['esperar', 'recargar', 'ir', 'limpiar_datos'].includes(a.tipo)) await page.context().waitForEvent('page', { timeout: 1200 }).catch(() => {});
  for (const pg of page.context().pages()) {
    if (paginas0.has(pg) || pg === page) continue;
    await pg.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
    pestana = { url: pg.url(), titulo: (await pg.title().catch(() => '')).slice(0, 120) };
    await pg.close().catch(() => {});
  }
  if (pestana) await page.bringToFront().catch(() => {});
  // ventana de observación: si en los siguientes segundos aparece un aviso nuevo, la captura lo incluye
  if (a && C.observar_ms !== 0) {
    const t2 = Date.now(), n0 = vistos.size;
    while (Date.now() - t2 < (C.observar_ms || 3000)) {
      await page.waitForTimeout(250); await mirarAvisos();
      if (vistos.size > n0) { await page.waitForTimeout(700); break; }
    }
  }
  const enCaptura = await avisos();
  await page.screenshot({ ...oculta, path: C.captura });
  const z = await zonasWeb(page);
  const texto = await page.evaluate(() => document.body.innerText.slice(0, 4000)).catch(() => '');
  const sen = await senales(page);
  const despues = antes ? await page.screenshot(oculta) : null;
  return JSON.stringify({ url_antes: url0, url: page.url(), cambio_url: page.url() !== url0, estado_antes: f0.estado, estado: f.estado,
    cambio_estado: f.estado !== f0.estado, cambio_firma: f.sig !== f0.sig,
    cambio_imagen: antes ? !antes.equals(despues) : null, asentada, intentos: i, vio_carga: vioCarga, error_accion, espera_elemento_ms: esperaElemento,
    avisos_nuevos: [...vistos], avisos_idos: [...vistos].filter(t => !enCaptura.includes(t)), pestana_nueva: pestana,
    marco: z.marco, zonas: z.zonas || [], error: z.error || null, texto, espera_ms: a ? espera : null,
    host: (() => { try { return new URL(page.url()).host; } catch (e) { return ''; } })(), paginas: page.context().pages().length, ...sen });
}
"""


class Navegador:
    def __init__(self, sesion: str, material: str, cwd: Path, viewport: tuple[int, int] | None = None,
                 emular: str | None = None, pantalla: dict | None = None):
        """`emular`: dispositivo de Playwright («Pixel 7»): viewport, toque, densidad y agente de usuario de un celular.
        `pantalla`: {selector, atributo} que identifica la pantalla de una app de una sola página, donde la URL no
        cambia (p. ej. `.marco` y `data-estado`)."""
        if material not in ("figma", "web"):
            raise ValueError("material debe ser figma o web")
        self.sesion, self.material, self.cwd, self.viewport = sesion, material, Path(cwd), viewport
        self.emular, self.pantalla = emular, pantalla or {}
        self.cwd.mkdir(parents=True, exist_ok=True)

    def cli(self, *args, raw: bool = False, timeout: int = 180) -> str:
        cmd = [PW, f"-s={self.sesion}"] + (["--raw"] if raw else []) + list(map(str, args))
        r = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout

    def abrir(self, url: str, visible: bool = True):
        url = url_figma(url) if self.material == "figma" else url
        disp = ["--device", self.emular] if self.material == "web" and self.emular else []
        try:      # una sesión con el mismo nombre que quedó abierta (corrida cortada) impide abrir otra
            self.cli("close", timeout=30)
        except subprocess.TimeoutExpired:
            pass
        self.cli("open", *(["--headed"] if visible else []), *disp, url, timeout=240)
        if self.material == "web" and self.viewport and not self.emular:
            self.cli("resize", *self.viewport)

    def cerrar(self):
        self.cli("close")

    def paso(self, captura: Path, accion: dict | None = None, overlay: str | None = None, **cfg) -> dict:
        v = self._paso(captura, accion, overlay, **cfg)
        previa, disp = getattr(self, "_previa", None), getattr(self, "_dispositivo", None)
        if (self.material == "figma" and accion and accion.get("tipo") == "tocar" and previa and disp
                and node_id(v.get("url")) == node_id(v.get("url_antes"))
                and not cambio_visible(previa, captura, disp, umbral=0.002)):
            # En Figma un hotspot a veces no responde al primer toque (transición o carga en curso): se repite una
            # vez y se registra. [SUPUESTO METODOLÓGICO] Sin esto, el tiempo del prototipo contaría como fricción.
            time.sleep(0.8)
            v = self._paso(captura, accion, overlay, **cfg)
            v["reintento"] = True
        if self.material == "figma" and accion and previa and disp:
            # ¿cambió el teléfono? (la página completa también cambia por la burbuja, el carrusel o los resaltados)
            v["cambio_telefono"] = cambio_visible(previa, captura, disp, umbral=0.002)
        if self.material == "figma":
            # copia propia: quien llama puede renombrar o sobrescribir `captura` (recorrido usa siguiente.png),
            # y entonces la pantalla se compararía consigo misma y nunca se vería un overlay (piloto 2 de OU 2.0)
            self._previa = self.cwd / "_previa.png"
            shutil.copyfile(captura, self._previa)
        return v

    def _paso(self, captura: Path, accion: dict | None = None, overlay: str | None = None, **cfg) -> dict:
        if self.material == "figma" and accion and accion.get("tipo") == "ir":
            accion = dict(accion, url=url_figma(accion["url"]))
        c = dict(material=self.material, captura=str(captura), accion=accion, overlay=overlay, movil=bool(self.emular),
                 pantalla_sel=self.pantalla.get("selector"), pantalla_attr=self.pantalla.get("atributo"), **cfg)
        base = JS_PASO if self.material == "figma" else JS_PASO_WEB
        js = (base.replace("__CFG__", json.dumps(c, ensure_ascii=False))
              .replace("__ZONAS__", JS_ZONAS_FIGMA if self.material == "figma" else JS_ZONAS_WEB)
              .replace("__SENALES__", JS_SENALES).replace("__FIRMA__", JS_FIRMA).replace("__CAPA__", JS_CAPA)
              .replace("__INSTR__", "() => {" + JS_INSTRUMENTO + "}"))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, dir=self.cwd) as f:
            f.write(js)
        try:
            out = self.cli("run-code", "--filename", f.name, raw=True, timeout=300).strip()
        finally:
            os.unlink(f.name)
        try:
            v = json.loads(out)
            v = json.loads(v) if isinstance(v, str) else v
        except json.JSONDecodeError as e:
            raise RuntimeError(f"run-code no devolvió JSON: {out[:400]}") from e
        if self.material == "figma":
            v["lienzo"] = v.get("marco")
            if v["lienzo"] and not getattr(self, "_dispositivo", None):
                self._dispositivo = dispositivo(captura, v["lienzo"])
            if getattr(self, "_dispositivo", None):
                v["marco"] = self._dispositivo
            self._pistas(captura, v)
        return v

    def _pistas(self, captura: Path, v: dict) -> None:
        """Zonas tocables de Figma por sus resaltados. Si hay un overlay abierto, el toque va dentro de él (en
        la franja superior, sin interacción); si no, al fondo del lienzo, fuera del dispositivo."""
        marco = v.get("marco") or {}
        if not marco:
            v["deteccion"] = "sin lienzo"
            return
        ov = overlay_abierto(getattr(self, "_previa", None), captura, marco)
        lz = v.get("lienzo") or marco
        x, y = (ov["x"], ov["y"]) if ov else (lz["x"] + 6, lz["y"] + 6)   # fondo del lienzo, fuera del teléfono
        f = {k: captura.with_suffix(f".{k}.png") for k in ("base", "pistas", "despues")}
        js = JS_PISTAS.replace("__CFG__", json.dumps(dict(x=x, y=y, **{k: str(p) for k, p in f.items()})))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, dir=self.cwd) as t:
            t.write(js)
        try:
            self.cli("run-code", "--filename", t.name, raw=True, timeout=120)
        finally:
            os.unlink(t.name)
        if not f["base"].exists():
            v["deteccion"] = "sin captura de resaltados"
            return
        z = zonas_por_pistas(f["base"], f["pistas"], marco)
        v["pistas_alteraron"] = cambio_visible(f["base"], f["despues"], marco)
        v["overlay"] = bool(ov)
        for p in f.values():
            p.unlink(missing_ok=True)
        if z:
            v["zonas"], v["deteccion"] = z, "resaltados de Figma" + (" (dentro del overlay)" if ov else "")
        else:
            v["zonas"], v["deteccion"] = elegir_zonas_figma(v)

    def video(self, iniciar: bool, nombre: str | None = None) -> str:
        if iniciar:
            self.cli("video-start", *( [nombre] if nombre else []))
            return ""
        return self.cli("video-stop")

    def capitulo(self, titulo: str) -> None:
        """Marca de capítulo en el video (un paso del perfil): el video se recorre por pasos."""
        try:      # es un adorno del video: con la máquina cargada no debe tumbar la sesión
            self.cli("video-chapter", titulo[:120], timeout=30)
        except subprocess.TimeoutExpired:
            pass

    def ejecutar(self, js: str, timeout: int = 300) -> object:
        """Corre una función `async (page) => …` y devuelve su resultado (JSON si lo es)."""
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, dir=self.cwd) as f:
            f.write(js)
        try:
            out = self.cli("run-code", "--filename", f.name, raw=True, timeout=timeout).strip()
        finally:
            os.unlink(f.name)
        try:
            v = json.loads(out)
            return json.loads(v) if isinstance(v, str) and v[:1] in "[{" else v
        except json.JSONDecodeError:
            return out


def zonas_por_pistas(base: Path, pistas: Path, marco: dict | None = None) -> list[dict]:
    """Zonas tocables de Figma a partir de sus resaltados azules (hotspot hints): píxeles que se vuelven más azules
    entre la captura previa y la de los resaltados, agrupados en rectángulos."""
    import cv2
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(base).convert("RGB")).astype(int)
    b = np.asarray(Image.open(pistas).convert("RGB")).astype(int)
    if a.shape != b.shape:
        return []
    azul = (b[..., 2] - b[..., 0]) - (a[..., 2] - a[..., 0])
    m = ((azul > 25) & (np.abs(b - a).sum(axis=2) > 30)).astype(np.uint8)
    if marco:
        fuera = np.ones_like(m, dtype=bool)
        fuera[marco["y"]:marco["y"] + marco["h"], marco["x"]:marco["x"] + marco["w"]] = False
        m[fuera] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    zonas = []
    for i in range(1, n):
        x, y, w, h, area = (int(t) for t in st[i])
        if w < 8 or h < 8 or area < 120 or area / (w * h) < 0.35:
            continue
        zonas.append(dict(x=x, y=y, w=w, h=h, tocar=[x + w // 2, y + h // 2], tipo="zona", editable=False,
                          etiqueta=""))
    return sorted(zonas, key=lambda z: (z["y"], z["x"]))


def dispositivo(captura: Path, lienzo: dict) -> dict | None:
    """Rectángulo del teléfono dentro del lienzo de Figma: la franja de columnas no negras que contiene el centro
    (la burbuja del pensamiento queda a la izquierda, separada por fondo negro)."""
    import numpy as np

    if not lienzo or lienzo.get("w", 0) < 100 or lienzo.get("h", 0) < 100:
        return None                       # el lienzo aún no se dibuja: se intenta en la siguiente captura
    g = _gris(captura, lienzo) > 30
    if g.size == 0:
        return None
    cols = g.mean(axis=0) > 0.05
    c = len(cols) // 2
    if not cols[c]:
        return None
    x0, x1 = c, c
    while x0 > 0 and cols[x0 - 1]:
        x0 -= 1
    while x1 < len(cols) - 1 and cols[x1 + 1]:
        x1 += 1
    filas = np.where(g[:, x0:x1 + 1].mean(axis=1) > 0.05)[0]
    if not len(filas) or x1 - x0 < 100:
        return None
    return dict(x=lienzo["x"] + int(x0), y=lienzo["y"] + int(filas.min()), w=int(x1 - x0 + 1),
                h=int(filas.max() - filas.min() + 1))


def recortar(ruta: Path, marco: dict, margen: int = 6) -> list[int]:
    """Recorta la captura al teléfono (lo que vería una persona) y devuelve el origen del recorte en la página."""
    from PIL import Image

    im = Image.open(ruta)
    x0, y0 = max(0, marco["x"] - margen), max(0, marco["y"] - margen)
    x1, y1 = min(im.width, marco["x"] + marco["w"] + margen), min(im.height, marco["y"] + marco["h"] + margen)
    im.crop((x0, y0, x1, y1)).save(ruta)
    return [x0, y0]


def _gris(ruta: Path, marco: dict):
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(ruta).convert("L")).astype(int)
    return a[marco["y"]:marco["y"] + marco["h"], marco["x"]:marco["x"] + marco["w"]]


def cambio_visible(a: Path, b: Path, marco: dict, umbral: float = 0.03) -> bool:
    """¿Cambió más del `umbral` de los píxeles del lienzo entre dos capturas?"""
    import numpy as np

    x, y = _gris(a, marco), _gris(b, marco)
    return x.shape == y.shape and float(np.mean(np.abs(x - y) > 24)) > umbral


def overlay_abierto(previa: Path | None, actual: Path, marco: dict) -> dict | None:
    """Detecta un overlay (hoja inferior, modal) por el velo que oscurece la parte de arriba de la pantalla anterior.
    Devuelve el punto donde tocar sin cerrarlo: en la franja superior del overlay, donde suele ir la manija."""
    import numpy as np

    if not previa or not Path(previa).exists():
        return None
    a, b = _gris(previa, marco), _gris(actual, marco)
    if a.shape != b.shape:
        return None
    cols = np.where(np.abs(a - b).mean(axis=0) > 1)[0]
    if len(cols) < 20:
        return None
    x0, x1 = int(cols.min()), int(cols.max())
    cx = (x0 + x1) // 2
    franja = slice(max(0, cx - 30), cx + 30)
    da, db = a[:, franja].mean(axis=1), b[:, franja].mean(axis=1)
    oscuro = (da - db) > 12                   # filas que se oscurecieron: el velo
    if oscuro[: len(oscuro) // 3].mean() < 0.3:
        return None
    filas = np.where(~oscuro & (np.abs(da - db) > 12))[0]
    filas = filas[filas > np.argmax(oscuro)]
    if not len(filas):
        return None
    top = int(filas.min())
    return dict(x=marco["x"] + cx, y=marco["y"] + top + 8)


def elegir_zonas_figma(v: dict) -> tuple[list[dict], str]:
    """Si los resaltados no dieron zonas: el barrido de cursor, salvo que el cursor sea el mismo en todo el lienzo
    (prototipos táctiles: Figma muestra el cursor de dedo en todas partes)."""
    z, m = v.get("zonas") or [], v.get("marco") or {}
    area = max(1, m.get("w", 1) * m.get("h", 1))
    if z and sum(t["w"] * t["h"] for t in z) / area < 0.4:
        return z, "cursor"
    return [], "sin zonas detectadas"


def url_figma(url: str) -> str:
    """Link de prototipo listo para el arnés: sin la barra lateral de flujos (mueve el marco) y sin la interfaz de
    Figma (`hide-ui=1`: la barra de arriba y la de abajo aparecían y desaparecían con el mouse y la ventana
    parpadeaba)."""
    import re

    if "figma.com/proto" not in url:
        return url
    url = re.sub(r"([?&])show-proto-sidebar=1", r"\1show-proto-sidebar=0", url)
    for k, v in (("show-proto-sidebar", "0"), ("hide-ui", "1")):
        if f"{k}=" not in url:
            url += ("&" if "?" in url else "?") + f"{k}={v}"
    return url


def node_id(url: str) -> str | None:
    import re

    m = re.search(r"node-id=([0-9A-Za-z%:-]+)", url or "")
    return m.group(1).replace("%3A", "-").replace(":", "-") if m else None


def marcar(captura: Path, zonas: list[dict], destino: Path):
    """Copia de la captura con cada zona activa numerada (para que el perfil elija)."""
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(captura).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        fuente = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 15)
    except OSError:
        fuente = ImageFont.load_default()
    for i, z in enumerate(zonas, 1):
        x, y, w, h = z["x"], z["y"], z["w"], z["h"]
        d.rectangle([x, y, x + w, y + h], outline=(255, 64, 129), width=2)
        # la etiqueta va en la esquina derecha para no tapar el inicio del texto del elemento
        ancho = 22 + 8 * (i >= 10)
        tx, ty = min(x + w - ancho, im.width - ancho), max(y - 18, 0)
        d.rectangle([tx, ty, tx + ancho, ty + 18], fill=(255, 64, 129))
        d.text((tx + 4, ty + 1), str(i), fill="white", font=fuente)
    im.save(destino)
