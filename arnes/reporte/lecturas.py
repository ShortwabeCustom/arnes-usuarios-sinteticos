"""Biblioteca de lecturas del reporte editorial: páginas HTML locales que se abren en el panel lateral.

Generaliza los constructores que se hicieron a mano para OU 2.0 PWA MVP. Las fuentes del estudio no se tocan: cada
lectura se serializa aparte, con escape de HTML, y carga por demanda sin servidor (docs/REPORTE-EDITORIAL.md).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from ..estudio import Estudio


class _Limpio(HTMLParser):
    """Conserva la semántica del documento, sin scripts, estilos ni atributos ejecutables."""

    PERMITIDOS = set("div section article aside header footer main h1 h2 h3 h4 h5 h6 p a ul ol li table thead tbody tr td th "
                     "blockquote strong b em i small span details summary pre code br hr figure figcaption img dl dt dd".split())
    OMITIDOS = ("script", "style", "svg", "canvas", "nav")

    def __init__(self):
        super().__init__()
        self.out, self.salto = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.OMITIDOS:
            self.salto += 1
            return
        if self.salto or tag not in self.PERMITIDOS:
            return
        seguros = []
        for k, v in attrs:
            if k == "id":
                seguros.append(("data-source-id", v))
            elif k in ("href", "src") and not re.match(r"\s*(javascript|data|vbscript):", v or "", re.I):
                seguros.append((k, v))
            elif k in ("alt", "colspan", "rowspan", "open"):
                seguros.append((k, v or ""))
        self.out.append("<" + tag + "".join(f' {k}="{escape(v, quote=True)}"' for k, v in seguros) + ">")

    def handle_endtag(self, tag):
        if tag in self.OMITIDOS:
            self.salto = max(0, self.salto - 1)
        elif not self.salto and tag in self.PERMITIDOS and tag not in ("img", "br", "hr"):
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.salto:
            self.out.append(escape(data))


def limpiar(crudo: str) -> str:
    p = _Limpio()
    p.feed(crudo)
    return "".join(p.out)


class Biblioteca:
    def __init__(self, reporte: Path, principal: str, marca: str):
        self.raiz, self.principal, self.marca = reporte, principal, marca
        self.paginas, self.datos = reporte / "lecturas", reporte / "assets/report-reader/data"
        for d in (self.paginas, self.datos):
            shutil.rmtree(d, ignore_errors=True)  # son generadas: una sesión borrada no debe dejar su página
            d.mkdir(parents=True)
        self.manifiesto: dict = {}

    def agregar(self, clave, titulo, tipo, descripcion, datos, original=None, base=None):
        self.manifiesto[clave] = dict(title=titulo, kind=tipo, description=descripcion, original=original,
                                      base=base or original or self.principal, page=f"lecturas/{clave}.html",
                                      data=f"assets/report-reader/data/{clave}.js")
        carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c") \
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        (self.datos / f"{clave}.js").write_text(f"window.ReportReaderData[{json.dumps(clave)}]={carga};\n", encoding="utf-8")
        (self.paginas / f"{clave}.html").write_text(f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(titulo)} · {escape(self.marca)}</title><link rel="icon" href="data:,"><link rel="stylesheet" href="../assets/report-reader/reader.css"><link rel="stylesheet" href="../assets/evidence/evidence.css"></head>
<body class="reader-standalone" data-reader-page="{clave}"><noscript><main class="reader-scroll"><h1>{escape(titulo)}</h1><p>{escape(descripcion)}</p><p>Activa JavaScript para explorar esta lectura y sus evidencias.</p><a href="../{self.principal}">Volver al reporte</a></main></noscript><script src="../assets/report-reader/manifest.js"></script><script src="../assets/evidence/evidence.js"></script><script src="../assets/report-reader/insights.js"></script><script src="../assets/report-reader/reader.js"></script></body></html>''', encoding="utf-8")

    def cerrar(self, config: dict):
        (self.raiz / "assets/report-reader/manifest.js").write_text(
            "window.ReportReaderData={};\nwindow.ReportReaderConfig=" + json.dumps(config, ensure_ascii=False, separators=(",", ":"))
            + ";\nwindow.ReportReaderManifest=" + json.dumps(self.manifiesto, ensure_ascii=False, separators=(",", ":")) + ";\n",
            encoding="utf-8")


def _videos(e: Estudio, sesiones: dict, raiz: Path) -> dict:
    """Duración de cada grabación; sin ffprobe la biblioteca funciona igual, sin ese dato."""
    cache_f = raiz / "assets/evidence/media-metadata.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    ffprobe = shutil.which("ffprobe")
    videos = {}
    for sid, s in sesiones.items():
        rel = s.get("video")
        ruta = e.dir / rel if rel else None
        if not ruta or not ruta.is_file():
            continue
        firma = [ruta.stat().st_size, ruta.stat().st_mtime_ns]
        if ffprobe and cache.get(sid, {}).get("signature") != firma:
            crudo = subprocess.check_output([ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                                             "-of", "json", str(ruta)], text=True)
            info = json.loads(crudo)
            cache[sid] = dict(signature=firma, duration=float(info["format"]["duration"]), streams=info["streams"])
        c = cache.get(sid) or {}
        videos[sid] = dict(src="../" + rel, seconds=c.get("duration"), audio=any(x["codec_type"] == "audio" for x in c.get("streams", [])),
                           poster="../" + s["pasos"][0]["captura"] if s["pasos"] and s["pasos"][0].get("captura") else None)
    cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return videos


def evidencias(e: Estudio, b: Biblioteca, sesiones: dict, casos: list[dict]) -> dict:
    """Casos curados, mapas de acciones y sesiones con grabación. Cada caso se resuelve contra su paso real."""
    f = e.ruta("datos", "auditoria.json")
    experta = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    videos = _videos(e, sesiones, b.raiz)
    acciones: dict = {}
    for sid, s in sesiones.items():
        for p in s["pasos"]:
            a = p.get("accion") or {}
            if a.get("tipo") in ("tocar", "escribir"):
                acciones.setdefault(p.get("pantalla"), []).append(dict(sid=sid, step=p["n"], action=a["tipo"], response=p.get("respuesta"),
                                                                       x=a.get("x"), y=a.get("y")))
    mapas = []
    for ruta in sorted(e.ruta("heatmaps").glob("toques-*.png")):
        pantalla = ruta.stem.removeprefix("toques-")
        filas = acciones.get(pantalla, [])
        cuenta = Counter(x["response"] for x in filas)
        m = dict(id="mapa-" + pantalla, title="Toques · " + pantalla, screen=pantalla, image="../heatmaps/" + ruta.name, actions=len(filas),
                 sessions=len({x["sid"] for x in filas}), responded=cuenta.get("si", 0), unconfirmed=len(filas) - cuenta.get("si", 0), rows=filas)
        b.agregar(m["id"], m["title"], "heatmap", "Acciones ejecutadas por el arnés durante sesiones sintéticas. No es seguimiento de mirada.", m)
        mapas.append(m)
    resueltos = []
    for c in casos:
        s = sesiones[c["sesion"]]
        paso = next(p for p in s["pasos"] if p["n"] == c["paso"])
        perfil = paso.get("perfil") or {}
        x = dict(id=c["id"], title=c["titulo"], topic=c.get("tema", ""), sid=c["sesion"], step=c["paso"], screen=paso.get("pantalla"),
                 heuristic=c.get("heuristica", ""), interpretation=c.get("interpretacion", ""), observation=c.get("observacion", ""),
                 limit=c.get("limite") or "Este caso muestra una sesión sintética: no permite estimar con qué frecuencia ocurriría con clientes reales.",
                 map_note=c.get("nota_mapa") or "Este mapa agrupa las acciones registradas en esta pantalla. No mide qué se leyó ni la atención visual.",
                 name=s.get("nombre"), task=s.get("tarea"), run=s.get("corrida"), image="../" + paso["captura"] if paso.get("captura") else None,
                 thought=perfil.get("pensamiento", ""), action=(perfil.get("accion") or {}).get("texto", ""), video=videos.get(c["sesion"]),
                 sessionPage=f"lecturas/{c['sesion']}.html", map=next((m for m in mapas if m["screen"] == paso.get("pantalla")), None))
        x["expert"] = [o for o in experta.get("consolidado", []) if o.get("pantalla") == x["screen"] and o.get("criterio") in (c.get("criterios") or [])]
        if c.get("siguiente"):
            x["nextThought"] = next(((p.get("perfil") or {}).get("pensamiento", "") for p in s["pasos"] if p["n"] == c["paso"] + 1), "")
        b.agregar(x["id"], x["title"], "evidence-case", f"Captura, grabación, toques y criterio UX · {x['sid']}", x, f"../datos/sesiones/{x['sid']}.json")
        resueltos.append(x)
    biblioteca = dict(cases=resueltos, maps=mapas, sessions=[
        dict(id=sid, title=s.get("nombre"), task=s.get("tarea"), run=s.get("corrida"), result=s.get("resultado"), steps=len(s["pasos"]),
             video=videos.get(sid), page=f"lecturas/{sid}.html") for sid, s in sesiones.items()])
    b.agregar("evidencias", "Biblioteca de evidencias", "evidence-library",
              f"Explora los casos, las {len(sesiones)} sesiones y los mapas de acciones. Todo conserva su fuente.", biblioteca)
    return dict(sesiones=len(sesiones), con_video=len(videos), mapas=len(mapas))
