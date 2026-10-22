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
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || +st.opacity === 0) continue;
    const cx = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), cy = Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1);
    const top = document.elementFromPoint(cx, cy);
    if (top && !el.contains(top) && !top.contains(el)) continue;
    if (out.some(o => o.el.contains(el) && o.tipo !== 'label')) continue;
    const t = el.tagName.toLowerCase();
    const etiqueta = (el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder || el.title || el.name || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    out.push({ el, x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height),
               tocar: [Math.round(cx), Math.round(cy)], tipo: t, editable: t === 'input' || t === 'textarea' || el.isContentEditable, etiqueta });
  }
  return { marco: { x: 0, y: 0, w: innerWidth, h: innerHeight }, zonas: out.map(({ el, ...o }) => o) };
});
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


class Navegador:
    def __init__(self, sesion: str, material: str, cwd: Path, viewport: tuple[int, int] | None = None):
        if material not in ("figma", "web"):
            raise ValueError("material debe ser figma o web")
        self.sesion, self.material, self.cwd, self.viewport = sesion, material, Path(cwd), viewport
        self.cwd.mkdir(parents=True, exist_ok=True)

    def cli(self, *args, raw: bool = False, timeout: int = 180) -> str:
        cmd = [PW, f"-s={self.sesion}"] + (["--raw"] if raw else []) + list(map(str, args))
        r = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout

    def abrir(self, url: str, visible: bool = True):
        url = url_figma(url) if self.material == "figma" else url
        self.cli("open", *(["--headed"] if visible else []), url, timeout=240)
        if self.material == "web" and self.viewport:
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
        c = dict(material=self.material, captura=str(captura), accion=accion, overlay=overlay, **cfg)
        js = (JS_PASO.replace("__CFG__", json.dumps(c, ensure_ascii=False))
              .replace("__ZONAS__", JS_ZONAS_FIGMA if self.material == "figma" else JS_ZONAS_WEB)
              .replace("__SENALES__", JS_SENALES)
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
