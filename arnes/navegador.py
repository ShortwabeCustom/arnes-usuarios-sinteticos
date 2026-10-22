"""Navegador para recorridos: envoltorio de playwright-cli que hace cada paso en una sola llamada.

Un paso = acción → asentar → captura → mapa de zonas activas → URL. Todo dentro de un `run-code`,
así no se pagan cinco procesos por toque.

Dos materiales, un solo modo de interacción (por coordenada):

- **figma**: el prototipo se dibuja en <canvas>, sin árbol de accesibilidad. Las zonas activas se
  leen del cursor del canvas (`cursor: pointer`), con la misma rejilla de `hotspots.js` del skill
  auditoria-prototipos-figma. No se cambia el tamaño de la ventana: el encuadre es parte del prototipo.
- **web**: sitio real. Las zonas son los elementos interactivos visibles y no tapados del DOM, y el
  viewport se fija al del dispositivo del estudio.

Lecciones heredadas del skill de auditoría que este módulo aplica:
- asentar por estabilidad de imagen, nunca con `sleep` fijo;
- un toque sin efecto NO declara un marco terminal: se registra como «sin respuesta» y el perfil
  decide qué hace después;
- el node-id (Figma) o la URL (web) es la señal de estado más barata.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

PW = os.path.expanduser(os.environ.get("PWCLI", "~/.claude/skills/playwright/scripts/playwright_cli.sh"))

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
  }, { html, pos: C.overlay_pos || 'right:12px;top:12px' }).catch(() => {});
  const url0 = page.url();
  const antes = C.accion ? await page.screenshot() : null;
  if (C.overlay && C.accion) await ov(C.overlay);
  const a = C.accion;
  if (a && a.tipo === 'recargar') await page.reload({ waitUntil: 'domcontentloaded' }).catch(() => {});
  if (a) {
    if (a.tipo === 'tocar' || a.tipo === 'escribir') {
      await page.mouse.move(a.x, a.y); await page.mouse.down(); await page.mouse.up();
      if (a.tipo === 'escribir') { await page.waitForTimeout(300); await page.keyboard.type(a.texto || '', { delay: 40 }); }
    } else if (a.tipo === 'desplazar') {
      await page.mouse.move(a.x, a.y); await page.mouse.wheel(0, a.dy);
    } else if (a.tipo === 'tecla') {
      await page.keyboard.press(a.tecla);
    } else if (a.tipo === 'volver') {
      await page.goBack().catch(() => {});
    } else if (a.tipo === 'arrastrar') {
      await page.mouse.move(a.x, a.y); await page.mouse.down(); await page.mouse.move(a.x2, a.y2, { steps: 12 }); await page.mouse.up();
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
    if (C.overlay) await ov(null);
    const b = await page.screenshot(), tb = Date.now();
    if (prev && hash(b) === hash(prev) && b.equals(prev)) {
      if (racha === 0) tEstable = tPrev;
      racha++;
      if (racha >= estable) { asentada = true; break; }
    } else { racha = 0; tEstable = null; }
    prev = b; tPrev = tb; i++;
    if (C.overlay && a) await ov(C.overlay);
  }
  const espera = asentada ? Math.max(0, tEstable - t0) : Date.now() - t0;
  if (C.overlay) await ov(null);
  await page.screenshot({ path: C.captura });
  const z = C.material === 'figma' ? await zonasFigma(page) : await zonasWeb(page);
  if (C.material === 'figma' && z.marco) await page.mouse.move(z.marco.x + 3, z.marco.y + 3);
  const despues = await page.screenshot();
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
        self.cli("open", *(["--headed"] if visible else []), url, timeout=240)
        if self.material == "web" and self.viewport:
            self.cli("resize", *self.viewport)

    def cerrar(self):
        self.cli("close")

    def paso(self, captura: Path, accion: dict | None = None, overlay: str | None = None, **cfg) -> dict:
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
            return json.loads(v) if isinstance(v, str) else v
        except json.JSONDecodeError as e:
            raise RuntimeError(f"run-code no devolvió JSON: {out[:400]}") from e

    def video(self, iniciar: bool, nombre: str | None = None) -> str:
        if iniciar:
            self.cli("video-start", *( [nombre] if nombre else []))
            return ""
        return self.cli("video-stop")


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
