"""Auditoría técnica de un producto web: lo que se mide sin ningún perfil ni modelo (0 tokens).

El arnés recorre la `ruta_mecanica` del estudio (acciones por rol y texto, como una persona que ya sabe el camino) en
un celular emulado y, en cada pantalla nueva, mide:

- **Accesibilidad automática** con axe-core (WCAG 2.0, 2.1 y 2.2, A y AA, más buenas prácticas): reglas que fallan,
  impacto, criterio WCAG y elementos afectados. axe encuentra una parte de los problemas (≈ 30–50 %); lo que no
  puede juzgar queda como «por revisar a mano».
- **Objetivos táctiles** (WCAG 2.5.8: 24 × 24 px; recomendación de plataforma: 44 × 44 px).
- **Formularios**: etiqueta, `autocomplete`, teclado (`inputmode`/`type`), obligatorios.
- **Texto**: tamaño mínimo, palabras y legibilidad en español (Szigriszt-Pazos, escala INFLESZ).
- **Teclado**: foco visible al recorrer con Tab (WCAG 2.4.7) y orden.
- **Reflujo** a 320 px de ancho sin desplazamiento horizontal (WCAG 1.4.10).
- **Errores**: de consola, de JavaScript y de red (4xx/5xx).
- **Esperas del sistema** de cada paso de la ruta (con CPU 4× más lenta, como un celular de gama media).

Y, una vez por estudio: **carga** en frío y con caché bajo red móvil lenta (TTFB, FCP, LCP, CLS, peso, peticiones,
tareas largas), **PWA** (manifiesto, service worker, funciona sin conexión, instalable) y **retoma** (recargar y
volver a entrar en los puntos de `tecnico.retoma_en`).

Todo es [EVIDENCIA] medida en el producto con un dispositivo emulado; las condiciones van en el resultado.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from .estudio import Estudio
from .navegador import JS_ZONAS_WEB, Navegador

VENDOR = Path(__file__).with_name("vendor") / "axe"

# Red móvil lenta y CPU de gama media: los valores de Lighthouse para móvil.
RED_LENTA = dict(offline=False, latency=150, downloadThroughput=1638.4 * 1024 / 8, uploadThroughput=750 * 1024 / 8)
CPU_LENTA = 4

# Umbrales de Core Web Vitals (web.dev): bueno · mejorable · malo.
UMBRALES = dict(lcp_ms=(2500, 4000), fcp_ms=(1800, 3000), cls=(0.1, 0.25), inp_ms=(200, 500), ttfb_ms=(800, 1800), tbt_ms=(200, 600))

JS_INIT = r"""() => {
  if (window.__arnesPerf) return;
  const P = window.__arnesPerf = { lcp: 0, cls: 0, lt: [], ev: [] };
  const obs = (type, fn, extra) => { try { new PerformanceObserver(l => l.getEntries().forEach(fn)).observe({ type, buffered: true, ...(extra || {}) }); } catch (e) {} };
  obs('largest-contentful-paint', e => { P.lcp = e.startTime; });
  obs('layout-shift', e => { if (!e.hadRecentInput) P.cls += e.value; });
  obs('longtask', e => P.lt.push([Math.round(e.startTime), Math.round(e.duration)]));
  obs('event', e => { if (e.interactionId) P.ev.push([e.name, Math.round(e.duration)]); }, { durationThreshold: 16 });
  const E = window.__arnesErr = [];
  addEventListener('error', e => E.push('JavaScript: ' + String(e.message || e.type).slice(0, 240)));
  addEventListener('unhandledrejection', e => E.push('Promesa rechazada: ' + String(e.reason && (e.reason.message || e.reason)).slice(0, 240)));
  const ce = console.error.bind(console);
  console.error = (...a) => { E.push('Consola: ' + a.map(x => (x && x.message) || String(x)).join(' ').slice(0, 240)); ce(...a); };
}"""

JS_CARGA = r"""
async (page) => {
  const C = __CFG__;
  await page.context().addInitScript(__INIT__);
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.enable');
  if (C.limpiar) { await cdp.send('Network.clearBrowserCache'); await cdp.send('Network.clearBrowserCookies'); }
  if (C.red) await cdp.send('Network.emulateNetworkConditions', C.red);
  if (C.cpu) await cdp.send('Emulation.setCPUThrottlingRate', { rate: C.cpu });
  const t0 = Date.now();
  await page.goto(C.url, { waitUntil: 'load', timeout: 90000 }).catch(() => {});
  await page.waitForTimeout(C.reposo_ms || 4000);
  const r = await page.evaluate(() => {
    const n = performance.getEntriesByType('navigation')[0] || {}, P = window.__arnesPerf || {};
    const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime;
    const res = performance.getEntriesByType('resource');
    const por = {}; for (const x of res) { const k = x.initiatorType || 'otro'; por[k] = por[k] || { n: 0, bytes: 0 }; por[k].n++; por[k].bytes += x.transferSize || 0; }
    const tbt = (P.lt || []).reduce((s, [, d]) => s + Math.max(0, d - 50), 0);
    return { ttfb_ms: Math.round(n.responseStart || 0), fcp_ms: fcp ? Math.round(fcp) : null, lcp_ms: P.lcp ? Math.round(P.lcp) : null,
      cls: Math.round((P.cls || 0) * 1000) / 1000, dcl_ms: Math.round(n.domContentLoadedEventEnd || 0), load_ms: Math.round(n.loadEventEnd || 0),
      tbt_ms: Math.round(tbt), tareas_largas: (P.lt || []).length, peticiones: res.length + 1,
      bytes: res.reduce((s, x) => s + (x.transferSize || 0), 0) + (n.transferSize || 0), documento_bytes: n.transferSize || 0, por_tipo: por,
      controlado_por_sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller) };
  });
  if (C.red) await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  if (C.cpu) await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  r.total_ms = Date.now() - t0;
  return JSON.stringify(r);
}
"""

JS_PWA = r"""
async (page) => {
  const C = __CFG__;
  const m = await page.evaluate(async () => {
    const l = document.querySelector('link[rel="manifest"]');
    const out = { https: location.protocol === 'https:', manifiesto_url: l ? l.href : null, viewport: (document.querySelector('meta[name=viewport]') || {}).content || null,
      theme_color: (document.querySelector('meta[name=theme-color]') || {}).content || null, lang: document.documentElement.lang || null,
      apple_touch_icon: !!document.querySelector('link[rel="apple-touch-icon"]'), titulo: document.title };
    if (l) { try { out.manifiesto = await (await fetch(l.href)).json(); } catch (e) { out.manifiesto_error = String(e); } }
    if (navigator.serviceWorker) { const regs = await navigator.serviceWorker.getRegistrations(); out.service_worker = regs.map(r => ({ scope: r.scope, activo: !!r.active }));
      out.controlado = !!navigator.serviceWorker.controller; }
    return out;
  });
  // sin conexión: ¿la app vuelve a abrir?
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  let off = { abre: false };
  try {
    await page.reload({ waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(2500);
    off = await page.evaluate((sel) => ({ abre: !!(sel ? document.querySelector(sel) : document.body.innerText.trim()),
      texto: document.body.innerText.trim().replace(/\s+/g, ' ').slice(0, 200) }), C.selector);
  } catch (e) { off = { abre: false, error: String(e.message || e).split('\n')[0] }; }
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await page.goto(C.url, { waitUntil: 'load' }).catch(() => {});
  m.sin_conexion = off;
  return JSON.stringify(m);
}
"""

JS_PANTALLA = r"""
async (page) => {
  const C = __CFG__;
  __ZONAS__
  if (!(await page.evaluate(() => !!window.axe))) {
    await page.addScriptTag({ path: C.axe });
    await page.evaluate((loc) => window.axe.configure({ locale: loc }), C.locale);
  }
  await page.screenshot({ scale: 'css', path: C.captura, style: '#arnes-capa{visibility:hidden!important}' });
  const ax = await page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
      resultTypes: ['violations', 'incomplete'], exclude: [['#arnes-capa']] });
    const v = r.violations.map(x => ({ id: x.id, impacto: x.impact, ayuda: x.help, tags: x.tags.filter(t => /^wcag\d|best-practice/.test(t)),
      nodos: x.nodes.length, ejemplos: x.nodes.slice(0, 3).map(n => ({ selector: String(n.target[0]).slice(0, 120), html: n.html.slice(0, 160), resumen: (n.failureSummary || '').slice(0, 300) })) }));
    const inc = r.incomplete.map(x => ({ id: x.id, impacto: x.impact, ayuda: x.help, nodos: x.nodes.length }));
    return { version: window.axe.version, violaciones: v, por_revisar: inc };
  });
  const z = await zonasWeb(page);
  const det = await page.evaluate(() => {
    const vis = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
    const campos = [...document.querySelectorAll('input:not([type=hidden]),select,textarea')].filter(vis).map(el => {
      const lab = (el.labels && el.labels[0] && el.labels[0].innerText.trim()) || el.getAttribute('aria-label') ||
        (el.getAttribute('aria-labelledby') ? (document.getElementById(el.getAttribute('aria-labelledby')) || {}).innerText : '') || '';
      return { etiqueta: String(lab).replace(/\s+/g, ' ').slice(0, 80), tipo: el.type || el.tagName.toLowerCase(), inputmode: el.inputMode || '',
        autocomplete: el.getAttribute('autocomplete') || '', obligatorio: el.required || el.getAttribute('aria-required') === 'true',
        maxlength: el.maxLength > 0 ? el.maxLength : null, placeholder: el.placeholder || '', describe: !!el.getAttribute('aria-describedby') };
    });
    let min = 99, chicos = 0, n = 0;
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) { const t = w.currentNode; if (!t.textContent.trim()) continue; const el = t.parentElement; if (!el || !vis(el) || el.closest('#arnes-capa')) continue;
      const f = parseFloat(getComputedStyle(el).fontSize); n++; if (f < min) min = f; if (f < 12) chicos++; }
    const se = document.scrollingElement || document.documentElement;
    return { campos, fuente_min_px: n ? min : null, textos_menores_12px: chicos, textos: n,
      desborde_horizontal: se.scrollWidth > innerWidth + 1, alto_documento: se.scrollHeight, alto_ventana: innerHeight,
      h1: document.querySelectorAll('h1').length, main: document.querySelectorAll('main,[role=main]').length,
      regiones_vivas: document.querySelectorAll('[aria-live]:not([aria-live=off]),[role=status],[role=alert],[role=progressbar]').length,
      texto: document.body.innerText.slice(0, 6000), titulo: document.title,
      red_fallida: performance.getEntriesByType('resource').filter(x => x.responseStatus >= 400).map(x => [x.responseStatus, x.name.slice(0, 160)]),
      interacciones: (window.__arnesPerf || {}).ev || [], errores: (window.__arnesErr || []).slice() };
  });
  // Teclado: Tab hasta 25 veces; ¿el foco se ve (cambia contorno, sombra, borde o fondo)?
  const foco = await page.evaluate(() => { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.scrollTo(0, 0); return true; });
  const pasosFoco = [];
  for (let i = 0; i < (C.tabs || 25); i++) {
    await page.keyboard.press('Tab');
    const f = await page.evaluate(() => {
      const el = document.activeElement; if (!el || el === document.body) return null;
      const s = getComputedStyle(el), clave = x => [x.outlineStyle, x.outlineWidth, x.outlineColor, x.boxShadow, x.borderColor, x.backgroundColor, x.textDecorationLine].join('|');
      const con = clave(s); const r = el.getBoundingClientRect();
      const c = el.cloneNode(false); c.style.cssText = 'position:absolute;left:-9999px;top:0'; el.parentNode.appendChild(c); const sin = clave(getComputedStyle(c)); c.remove();
      return { nombre: (el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder || el.tagName).trim().replace(/\s+/g, ' ').slice(0, 60),
        tag: el.tagName.toLowerCase(), visible: con !== sin, dentro: r.bottom > 0 && r.top < innerHeight && r.width > 0 };
    });
    if (!f) break;
    if (pasosFoco.length && pasosFoco[0].nombre === f.nombre && pasosFoco[0].tag === f.tag && i > 1) break;   // dio la vuelta
    pasosFoco.push(f);
  }
  await page.evaluate(() => { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.scrollTo(0, 0); });
  // Reflujo a 320 px (WCAG 1.4.10): ancho de 320 CSS px sin desplazamiento horizontal
  const vp = page.viewportSize();
  let reflujo = null;
  if (vp) {
    await page.setViewportSize({ width: 320, height: vp.height }); await page.waitForTimeout(400);
    reflujo = await page.evaluate(() => { const se = document.scrollingElement || document.documentElement;
      const cortados = [...document.querySelectorAll('button,a,input,h1,h2,p,label')].filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && (r.right > innerWidth + 1 || r.left < -1); }).length;
      return { desborde: se.scrollWidth > innerWidth + 1, ancho_documento: se.scrollWidth, elementos_fuera: cortados }; });
    await page.screenshot({ scale: 'css', path: C.captura.replace(/\.png$/, '-320.png'), style: '#arnes-capa{visibility:hidden!important}' });
    await page.setViewportSize(vp); await page.waitForTimeout(300);
  }
  return JSON.stringify({ axe: ax, zonas: z.zonas, ...det, foco: pasosFoco, reflujo_320: reflujo });
}
"""

JS_MARCA_PERF = r"""async (page) => JSON.stringify(await page.evaluate(() => {
  const P = window.__arnesPerf || { ev: [] }, E = window.__arnesErr || [];
  const r = { interacciones: P.ev.splice(0), errores: E.splice(0) }; return r; }))"""

JS_CPU = r"""async (page) => { const cdp = await page.context().newCDPSession(page); await cdp.send('Emulation.setCPUThrottlingRate', { rate: __RATE__ }); return 'ok'; }"""


# --- utilidades de texto ----------------------------------------------------------------------------------------------

def _silabas(palabra: str) -> int:
    """Sílabas aproximadas en español: grupos vocálicos, separando hiatos de vocales fuertes."""
    p = palabra.lower()
    p = re.sub(r"[^a-záéíóúüñ]", "", p)
    if not p:
        return 0
    grupos = re.findall(r"[aeiouáéíóúü]+", p)
    n = 0
    for g in grupos:
        fuertes = sum(1 for ch in g if ch in "aeoáéíóú")
        n += max(1, fuertes) if len(g) > 1 else 1
    return max(1, n)


def legibilidad(texto: str) -> dict | None:
    """Índice de Szigriszt-Pazos con la escala INFLESZ (Barrio-Cantalejo, 2008), la referencia para textos en español:
    206.835 − 62.3 · (sílabas / palabras) − (palabras / frases). < 40 muy difícil · 40–55 algo difícil · 55–65 normal ·
    65–80 bastante fácil · > 80 muy fácil. Se descartó Fernández-Huerta: castiga las frases cortas, que en una interfaz
    son botones y títulos. Con menos de 20 palabras no se calcula. [MÉTRICA DERIVADA, aproximada: sílabas por regla]"""
    limpio = re.sub(r"[\d$%.,:/()+\-–—#@*]+(?=\s|$)", " ", texto or "")
    palabras = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", limpio)
    if len(palabras) < 20:
        return None
    frases = max(1, len([f for f in re.split(r"[.!?¿¡\n]+", texto) if re.search(r"[A-Za-zÁÉÍÓÚáéíóúñ]{2,}", f)]))
    sil = sum(_silabas(w) for w in palabras)
    v = round(206.835 - 62.3 * sil / len(palabras) - len(palabras) / frases, 1)
    nivel = ("muy fácil" if v > 80 else "bastante fácil" if v >= 65 else "normal" if v >= 55 else "algo difícil" if v >= 40
             else "muy difícil")
    return dict(indice=v, nivel=nivel, palabras=len(palabras), frases=frases, escala="INFLESZ")


def estado_umbral(clave: str, valor) -> str | None:
    """bueno · mejorable · malo según los umbrales de Core Web Vitals."""
    if valor is None or clave not in UMBRALES:
        return None
    b, m = UMBRALES[clave]
    return "bueno" if valor <= b else "mejorable" if valor <= m else "malo"


def _js(plantilla: str, cfg: dict, **extra) -> str:
    s = plantilla.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)).replace("__INIT__", JS_INIT)
    for k, v in extra.items():
        s = s.replace(k, v)
    return s


# --- auditoría ------------------------------------------------------------------------------------------------------

def auditar(e: Estudio, visible: bool = False) -> dict:
    c = e.cfg
    if c.get("material") != "web":
        raise SystemExit("La auditoría técnica es para material web (un sitio o una PWA), no para prototipos de Figma.")
    ruta = c.get("ruta_mecanica") or []
    if not ruta:
        raise SystemExit("Falta `ruta_mecanica` en estudio.yaml: los pasos por rol y texto que recorren el flujo.")
    disp = c.get("dispositivo") or {}
    tec = c.get("tecnico") or {}
    url = c["url"]
    out_dir = e.ruta("datos", "tecnico")
    out_dir.mkdir(parents=True, exist_ok=True)
    nav = Navegador("arnes-tecnico", "web", e.ruta("datos", "navegador"), (disp.get("ancho", 412), disp.get("alto", 839)),
                    emular=disp.get("emular"), pantalla=c.get("pantalla"))
    sel = (c.get("pantalla") or {}).get("selector")
    locale = json.loads((VENDOR / "es.json").read_text(encoding="utf-8"))
    res = dict(fecha=time.strftime("%Y-%m-%d %H:%M"), url=url, dispositivo=disp.get("emular") or f"{disp.get('ancho')}×{disp.get('alto')}",
               condiciones=dict(red_carga="móvil lenta (150 ms de latencia, 1.6 Mbps de bajada, 750 kbps de subida)",
                                cpu_carga=f"{CPU_LENTA}× más lenta", cpu_ruta=f"{tec.get('cpu_ruta', CPU_LENTA)}× más lenta",
                                navegador="Chromium de Playwright con emulación de dispositivo"),
               umbrales=UMBRALES)
    print("Abriendo el producto en un celular emulado…")
    nav.abrir("about:blank", visible=visible)
    try:
        # 1 · carga en frío y con caché, bajo red móvil lenta
        url_carga = tec.get("url_carga") or url
        fria = nav.ejecutar(_js(JS_CARGA, dict(url=url_carga, limpiar=True, red=RED_LENTA, cpu=CPU_LENTA)), timeout=240)
        tibia = nav.ejecutar(_js(JS_CARGA, dict(url=url_carga, limpiar=False, red=RED_LENTA, cpu=CPU_LENTA)), timeout=240)
        res["carga"] = dict(fria=fria, con_cache=tibia)
        print(f"  carga en frío: LCP {fria.get('lcp_ms')} ms · CLS {fria.get('cls')} · {round((fria.get('bytes') or 0) / 1024)} KB · "
              f"{fria.get('peticiones')} peticiones")
        # 2 · PWA
        res["pwa"] = nav.ejecutar(_js(JS_PWA, dict(url=url, selector=sel)), timeout=120)
        print(f"  PWA: service worker {'sí' if res['pwa'].get('service_worker') else 'no'} · sin conexión "
              f"{'abre' if (res['pwa'].get('sin_conexion') or {}).get('abre') else 'no abre'}")
        # 3 · ruta mecánica con auditoría por pantalla
        res["pantallas"], res["ruta"] = _recorrer(e, nav, ruta, url, out_dir, locale, tec)
        # 4 · retoma
        res["retoma"] = [_retoma(e, nav, ruta, url, punto) for punto in tec.get("retoma_en") or []]
    finally:
        nav.cerrar()
    res["resumen"] = resumir(res)
    e.ruta("datos", "tecnico.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    e.marcar("tecnico", pantallas=len(res["pantallas"]))
    imprimir(res)
    return res


def _recorrer(e, nav, ruta, url, out_dir, locale, tec):
    pantallas, pasos, vistas = [], [], set()
    nav.paso(out_dir / "_tmp.png", {"tipo": "limpiar_datos", "url": url}, instrumentar=True)
    nav.ejecutar(JS_CPU.replace("__RATE__", str(tec.get("cpu_ruta", CPU_LENTA))))
    nav.ejecutar("async (page) => { await page.evaluate(" + JS_INIT + "); return 'ok'; }")

    def medir(info):
        est = info.get("estado") or info.get("url")
        if est in vistas:
            return
        vistas.add(est)
        cap = out_dir / f"{len(pantallas) + 1:02d}-{re.sub(r'[^A-Za-z0-9_-]', '_', str(est))[:40]}.png"
        cfg = dict(captura=str(cap), axe=str((VENDOR / "axe.min.js").resolve()), locale=locale, tabs=tec.get("tabs", 25))
        d = nav.ejecutar(_js(JS_PANTALLA, cfg, __ZONAS__=JS_ZONAS_WEB), timeout=240)
        if not isinstance(d, dict):
            print(f"  ! {est}: no se pudo auditar ({str(d)[:120]})")
            return
        d["legibilidad"] = legibilidad(d.get("texto", ""))
        d["objetivos"] = _objetivos(d.pop("zonas", []))
        d.update(estado=est, captura=str(cap.relative_to(e.dir)), paso_ruta=len(pasos))
        pantallas.append(d)
        v = d["axe"]["violaciones"]
        print(f"  {len(pantallas):02d} {est}: {len(v)} reglas WCAG fallan · {d['objetivos']['menores_24']} objetivos < 24 px · "
              f"foco visible {sum(f['visible'] for f in d['foco'])}/{len(d['foco'])}")

    info = nav.paso(out_dir / "_tmp.png")
    medir(info)
    for i, s in enumerate(ruta, 1):
        info = nav.paso(out_dir / "_tmp.png", {"tipo": "mecanico", "pasos": [s]}, max_ms=60000)
        extra = nav.ejecutar(JS_MARCA_PERF)
        # espera = lo que tardó en aparecer el elemento de este paso (carga del anterior) + lo que tardó en asentar
        espera = (info.get("espera_ms") or 0) + (info.get("espera_elemento_ms") or 0)
        pasos.append(dict(n=i, accion=s, estado=info.get("estado"), espera_ms=espera, vio_carga=info.get("vio_carga"),
                          error=info.get("error_accion"), interacciones=(extra or {}).get("interacciones") if isinstance(extra, dict) else None,
                          errores=(extra or {}).get("errores") if isinstance(extra, dict) else None))
        if info.get("error_accion"):
            print(f"  ! paso {i} de la ruta ({s}): {info['error_accion']}")
            break
        medir(info)
    (out_dir / "_tmp.png").unlink(missing_ok=True)
    nav.ejecutar(JS_CPU.replace("__RATE__", "1"))
    return pantallas, pasos


def _retoma(e, nav, ruta, url, punto: str) -> dict:
    """Llega a `punto`, recarga la página y luego vuelve a entrar por la URL: ¿a qué pantalla regresa la app?"""
    tmp = e.ruta("datos", "tecnico", "_tmp.png")
    nav.paso(tmp, {"tipo": "limpiar_datos", "url": url})
    a = nav.paso(tmp, {"tipo": "mecanico", "pasos": ruta, "hasta": punto}, max_ms=60000)
    if a.get("estado") != punto:
        return dict(punto=punto, error=f"la ruta no llegó (quedó en {a.get('estado')})")
    r = nav.paso(tmp, {"tipo": "recargar"})
    v = nav.paso(tmp, {"tipo": "ir", "url": url})
    tmp.unlink(missing_ok=True)
    out = dict(punto=punto, tras_recargar=r.get("estado"), tras_volver_a_entrar=v.get("estado"))
    out["conserva"] = out["tras_volver_a_entrar"] == punto
    print(f"  retoma en {punto}: recargar → {out['tras_recargar']} · volver a entrar → {out['tras_volver_a_entrar']}")
    return out


def _objetivos(zonas: list[dict]) -> dict:
    act = [z for z in zonas if z.get("tipo") != "label"]
    m24 = [z for z in act if z["w"] < 24 or z["h"] < 24]
    m44 = [z for z in act if z["w"] < 44 or z["h"] < 44]
    return dict(total=len(act), menores_24=len(m24), menores_44=len(m44),
                ejemplos_24=[dict(etiqueta=z.get("etiqueta"), w=z["w"], h=z["h"]) for z in m24[:5]],
                ejemplos_44=[dict(etiqueta=z.get("etiqueta"), w=z["w"], h=z["h"]) for z in m44[:5]])


# --- resumen --------------------------------------------------------------------------------------------------------

CRITERIO = re.compile(r"^wcag(\d)(\d)(\d+)$")


def criterios(tags: list[str]) -> list[str]:
    """['wcag143', 'wcag2aa'] → ['1.4.3']"""
    out = []
    for t in tags:
        m = CRITERIO.match(t)
        if m:
            out.append(".".join(m.groups()))
    return out


def resumir(res: dict) -> dict:
    P = res.get("pantallas") or []
    reglas: dict[str, dict] = {}
    for p in P:
        for v in p["axe"]["violaciones"]:
            r = reglas.setdefault(v["id"], dict(id=v["id"], ayuda=v["ayuda"], impacto=v["impacto"], criterios=criterios(v["tags"]),
                                                 practica="best-practice" in v["tags"], pantallas=[], nodos=0, ejemplo=v["ejemplos"][:1]))
            r["pantallas"].append(p["estado"])
            r["nodos"] += v["nodos"]
    orden = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
    lista = sorted(reglas.values(), key=lambda r: (orden.get(r["impacto"], 4), -len(r["pantallas"])))
    foco = [f for p in P for f in p.get("foco", [])]
    campos = [c for p in P for c in p.get("campos", [])]
    ruta = res.get("ruta") or []
    esperas = [x["espera_ms"] for x in ruta if x.get("espera_ms") is not None]
    inter = [d for x in ruta for _, d in (x.get("interacciones") or [])]
    errores = sorted({er for x in ruta for er in (x.get("errores") or [])} | {er for p in P for er in (p.get("errores") or [])})
    red = sorted({f"{s} {u}" for p in P for s, u in (p.get("red_fallida") or [])})
    leg = [p["legibilidad"]["indice"] for p in P if p.get("legibilidad")]
    fria = (res.get("carga") or {}).get("fria") or {}
    pwa = res.get("pwa") or {}
    man = pwa.get("manifiesto") or {}
    iconos = {s for i in man.get("icons") or [] for s in str(i.get("sizes", "")).split()}
    inp = max(inter) if inter else None
    return dict(
        pantallas=len(P),
        pasos_ruta=len(ruta), toques_ruta=sum(1 for x in ruta if not {"llenar", "teclear"} & set(x["accion"])),
        campos_ruta=sum(1 for x in ruta if {"llenar", "teclear"} & set(x["accion"])),
        espera_total_s=round(sum(esperas) / 1000, 1), espera_max_s=round(max(esperas) / 1000, 1) if esperas else None,
        pasos_con_carga=sum(1 for x in ruta if x.get("vio_carga")),
        reglas_wcag=[r for r in lista if not r["practica"]], buenas_practicas=[r for r in lista if r["practica"]],
        pantallas_sin_fallas=sum(1 for p in P if not [v for v in p["axe"]["violaciones"] if "best-practice" not in v["tags"]]),
        por_impacto={k: sum(1 for r in lista if r["impacto"] == k and not r["practica"]) for k in orden},
        objetivos_24=sum(p["objetivos"]["menores_24"] for p in P), objetivos_44=sum(p["objetivos"]["menores_44"] for p in P),
        objetivos_total=sum(p["objetivos"]["total"] for p in P),
        foco_visible=sum(1 for f in foco if f["visible"]), foco_total=len(foco),
        reflujo_320_falla=[p["estado"] for p in P if (p.get("reflujo_320") or {}).get("desborde")],
        desborde_412=[p["estado"] for p in P if p.get("desborde_horizontal")],
        fuente_min_px=min((p["fuente_min_px"] for p in P if p.get("fuente_min_px")), default=None),
        textos_menores_12=sum(p.get("textos_menores_12px", 0) for p in P),
        campos=len(campos), campos_sin_etiqueta=sum(1 for c in campos if not c["etiqueta"]),
        campos_sin_autocomplete=sum(1 for c in campos if not c["autocomplete"] and c["tipo"] not in ("range", "checkbox", "radio")),
        legibilidad_media=round(sum(leg) / len(leg), 1) if leg else None, legibilidad_pantallas=len(leg),
        sin_h1=[p["estado"] for p in P if not p.get("h1")], sin_main=[p["estado"] for p in P if not p.get("main")],
        errores=errores, red_fallida=red,
        inp_aprox_ms=inp, inp_estado=estado_umbral("inp_ms", inp),
        lcp_ms=fria.get("lcp_ms"), lcp_estado=estado_umbral("lcp_ms", fria.get("lcp_ms")),
        fcp_ms=fria.get("fcp_ms"), fcp_estado=estado_umbral("fcp_ms", fria.get("fcp_ms")),
        cls=fria.get("cls"), cls_estado=estado_umbral("cls", fria.get("cls")),
        ttfb_ms=fria.get("ttfb_ms"), ttfb_estado=estado_umbral("ttfb_ms", fria.get("ttfb_ms")),
        tbt_ms=fria.get("tbt_ms"), tbt_estado=estado_umbral("tbt_ms", fria.get("tbt_ms")),
        peso_kb=round((fria.get("bytes") or 0) / 1024), peticiones=fria.get("peticiones"),
        pwa=dict(https=pwa.get("https"), manifiesto=bool(man), nombre=man.get("name"), nombre_corto=man.get("short_name"),
                 display=man.get("display"), start_url=man.get("start_url"), icono_192="192x192" in iconos, icono_512="512x512" in iconos,
                 maskable=any("maskable" in str(i.get("purpose", "")) for i in man.get("icons") or []),
                 service_worker=bool(pwa.get("service_worker")), sin_conexion=(pwa.get("sin_conexion") or {}).get("abre"),
                 theme_color=pwa.get("theme_color"), lang=pwa.get("lang"), viewport=pwa.get("viewport")),
        retoma=res.get("retoma") or [],
    )


def imprimir(res: dict):
    s = res["resumen"]
    print(f"\nAuditoría técnica · {s['pantallas']} pantallas · ruta mínima de {s['pasos_ruta']} acciones "
          f"({s['campos_ruta']} campos) · espera total del sistema {s['espera_total_s']} s")
    print(f"WCAG (axe): {len(s['reglas_wcag'])} reglas fallan · {s['pantallas_sin_fallas']} de {s['pantallas']} pantallas sin fallas · "
          f"por impacto {s['por_impacto']}")
    for r in s["reglas_wcag"][:10]:
        print(f"  - [{r['impacto']}] {r['ayuda']} ({', '.join(r['criterios']) or 'sin criterio'}) · {len(r['pantallas'])} pantallas")
    print(f"Objetivos < 24 px: {s['objetivos_24']} · < 44 px: {s['objetivos_44']} de {s['objetivos_total']} · foco visible "
          f"{s['foco_visible']}/{s['foco_total']} · reflujo 320 px falla en {len(s['reflujo_320_falla'])}")
    print(f"Carga en frío (red lenta): LCP {s['lcp_ms']} ms ({s['lcp_estado']}) · FCP {s['fcp_ms']} ms · CLS {s['cls']} ({s['cls_estado']}) · "
          f"TBT {s['tbt_ms']} ms · {s['peso_kb']} KB · INP aprox. {s['inp_aprox_ms']} ms ({s['inp_estado']})")
    print(f"Legibilidad INFLESZ media: {s['legibilidad_media']} · errores: {len(s['errores'])} · red fallida: {len(s['red_fallida'])}")
    print(f"PWA: {s['pwa']}")
