"""Reporte editorial de un recorrido: el template que Alexis definió con OU 2.0 PWA MVP (docs/REPORTE-EDITORIAL.md).

El texto sale de `editorial.yaml` (o, si no existe, de la narrativa); las cifras salen de las sesiones y del agregado.
El reporte de OU 2.0 se corrigió a mano dos veces (435/439 y 17–25) porque sus cifras estaban escritas en el HTML: aquí
cada conteo se calcula o queda ligado a la lista de sesiones que lo respalda, y `arnes verificar` lo recuenta.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from html import escape as esc
from math import floor
from pathlib import Path

import yaml
from PIL import Image

from ..estudio import Estudio
from .lecturas import Biblioteca, evidencias, limpiar

RECURSOS = Path(__file__).parent / "plantilla_editorial" / "assets"
AVATARES_PWA = ("bryan", "itzel", "rosalba", "arturo")
PALABRAS = {0: "cero", 1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez"}
ESTADOS = {"se_sostiene": ("Se sostiene", ""), "se_cae": ("Se cae", " no"), "no_concluyente": ("No concluyente", " nuance")}
MESES = "ene feb mar abr may jun jul ago sep oct nov dic".split()
RESULTADOS = {"exito": "sin fricción", "exito_con_friccion": "con fricción", "falso_exito": "cree que terminó", "abandono": "abandona",
              "atascado": "se atasca", "fallo_max_pasos": "no termina"}


def fecha_larga(f) -> str:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(f or ""))
    return f"{int(m[3])} {MESES[int(m[2]) - 1]} {m[1]}" if m else str(f or "")


def decimal(x: float) -> str:
    """Un decimal redondeando las mitades hacia arriba: 60.25 → 60.3, como se lee en el cálculo publicado."""
    return f"{floor(x * 10 + 0.5) / 10:.1f}"


def palabra(n: int, mayuscula: bool = False) -> str:
    t = PALABRAS.get(n, str(n))
    return t.capitalize() if mayuscula else t


def _sin_vacios(x):
    """La plantilla trae campos en blanco: lo que no se llenó cuenta como ausente y usa el valor por omisión."""
    if isinstance(x, dict):
        d = {k: v for k, v in ((k, _sin_vacios(v)) for k, v in x.items()) if v not in ("", None, [], {})}
        return d
    if isinstance(x, list):
        return [v for v in (_sin_vacios(i) for i in x) if v not in ("", None, [], {})]
    return x


def cargar(e: Estudio) -> dict:
    f = e.ruta("editorial.yaml")
    return _sin_vacios(yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


@dataclass
class Cifra:
    x: int
    y: int
    trazable: bool = True

    def texto(self, forma: str = "") -> str:
        return {"de": f"{self.x} de {self.y}", "x": str(self.x), "y": str(self.y)}.get(forma, f"{self.x}/{self.y}")


class Contexto:
    """Todo lo que el template necesita de un estudio, ya leído."""

    def __init__(self, e: Estudio, N: dict):
        self.e, self.N, self.c = e, N, e.cfg
        self.E = cargar(e)
        self.R = json.loads(e.ruta("datos", "agregado.json").read_text(encoding="utf-8"))
        self.sesiones = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(e.sesiones_dir.glob("*.json"))}
        self.metricas = self.R["metricas"]["sesiones"]
        self.panel = e.panel()
        self.marca = self.E.get("marca") or N.get("titulo_corto") or e.cfg.get("titulo") or e.dir.name
        tramos = self.E.get("tramos") or {}
        self.tareas = [dict(id=t["id"], nombre=(tramos.get(t["id"]) or {}).get("nombre") or f"Tarea {t['id']}") for t in e.cfg["tareas"]
                       if any(m["tarea"] == t["id"] for m in self.metricas)]

    def de_tarea(self, tarea=None) -> list[dict]:
        return [m for m in self.metricas if tarea is None or m["tarea"] == tarea]

    def cifra(self, d) -> Cifra | None:
        """Una cifra se calcula (`auto`), se liga a sesiones (`sesiones`, `hallazgo`) o queda sin traza (`valor` solo)."""
        if isinstance(d, str):
            d = (self.E.get("cifras") or {}).get(d) or self.automatica(d) or {"valor": d}
        tarea = d.get("tarea")
        base = self.de_tarea(tarea)
        if d.get("auto") == "completan":
            return Cifra(sum(1 for m in base if m["completa"]), len(base))
        if d.get("auto") == "abandonan":
            return Cifra(sum(1 for m in base if m["resultado"] == "abandono"), len(base))
        if d.get("hallazgo") or d.get("sesiones"):
            ids = d.get("sesiones")
            if d.get("hallazgo"):
                ids = next((h.get("sesiones") or [] for h in self.N.get("hallazgos") or [] if h.get("id") == d["hallazgo"]), [])
            elegidas = {m["sesion"] for m in base if m["sesion"] in ids}
            # sin tarea declarada, la base son las tareas donde ocurre: 8 de 8 de T1, no 8 de las 16 del estudio
            donde = {m["tarea"] for m in base if m["sesion"] in elegidas}
            return Cifra(len(elegidas), sum(1 for m in base if m["tarea"] in donde))
        m = re.match(r"\s*(\d+)\s*(?:/|de)\s*(\d+)\s*$", str(d.get("valor", "")))
        return Cifra(int(m[1]), int(m[2]), trazable=False) if m else None

    def automatica(self, nombre: str) -> dict | None:
        m = re.fullmatch(r"(completan|abandonan)(?:_(\w+))?", nombre)
        if m:
            return dict(auto=m[1], tarea=m[2]) if m[2] else dict(auto=m[1])
        return None

    def confianza(self, b: dict) -> dict:
        """Confianza antes y después dentro de cada sesión: la diferencia sale de pares, no de restar rangos."""
        filas = []
        for m in self.de_tarea(b.get("tarea")):
            pasos = self.sesiones[m["sesion"]]["pasos"]
            antes = next(((p.get("perfil") or {}).get("confianza") for p in pasos if p.get("pantalla") == b["antes"]), None)
            despues = next(((p.get("perfil") or {}).get("confianza") for p in pasos if p.get("pantalla") == b["despues"]), None)
            if antes is not None and despues is not None:
                filas.append(dict(sesion=m["sesion"], nombre=self.sesiones[m["sesion"]].get("nombre"), corrida=self.sesiones[m["sesion"]].get("corrida"),
                                  antes=antes, despues=despues, caida=antes - despues))
        if not filas:
            return dict(filas=[])
        media = lambda k: sum(f[k] for f in filas) / len(filas)  # noqa: E731
        return dict(filas=filas, antes=media("antes"), despues=media("despues"), caida=media("caida"),
                    minima=min(f["caida"] for f in filas), maxima=max(f["caida"] for f in filas))

    def orientacion(self, b: dict) -> dict:
        """Respuestas a «¿sabes en qué parte vas?»: se cuentan respuestas repetidas por sesión, nunca personas."""
        tareas = b.get("tareas") or [t["id"] for t in self.tareas]
        filas = [(m["tarea"], m["sesion"], m.get("sabe_donde_va") or {}) for m in self.metricas if m["tarea"] in tareas]
        filas = [f for f in filas if sum(f[2].values())]
        suma = {k: sum(f[2].get(k, 0) for f in filas) for k in ("si", "mas_o_menos", "no")}
        return dict(tareas=tareas, filas=filas, suma=suma, total=sum(suma.values()), dudas=suma["mas_o_menos"] + suma["no"], sesiones=len(filas))

    def inestables(self) -> tuple[int, int] | None:
        rep = (self.R.get("robustez") or {}).get("repetidas") or {}
        return (sum(1 for v in rep.values() if len(set(v)) > 1), len(rep)) if rep else None

    def enlace(self, clave: str) -> str:
        return clave if re.match(r"https?:", clave) else f"lecturas/{clave}.html"

    def t(self, texto) -> str:
        """Texto editorial → HTML seguro: `{{cifra}}`, `{{cifra|de}}`, `**negritas**` y `[texto](lectura)`."""
        s = esc(str(texto or ""), quote=False)

        def macro(m):
            c = self.cifra(m[1])
            if not c:
                raise ValueError(f"editorial.yaml: la cifra «{m[1]}» no existe")
            return c.texto(m[2] or "")

        s = re.sub(r"\{\{\s*([\w-]+)\s*(?:\|\s*(\w+)\s*)?\}\}", macro, s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{esc(self.enlace(m[2]))}">{m[1]}</a>', s)


def valor_html(ctx: Contexto, d) -> str:
    c = ctx.cifra(d)
    if c:
        return f"{c.x}<span>/{c.y}</span>"
    return esc(str(d.get("valor", "") if isinstance(d, dict) else d))


# ---- valores por omisión: un estudio sin editorial.yaml también sale con el template ---------------------------


def hallazgos_orden(N: dict) -> list[dict]:
    return sorted(N.get("hallazgos") or [], key=lambda h: -int(h.get("severidad", 0)))


def casos_automaticos(ctx: Contexto) -> list[dict]:
    casos = []
    for h in hallazgos_orden(ctx.N):
        for sid in h.get("sesiones") or []:
            pasos = (ctx.sesiones.get(sid) or {}).get("pasos") or []
            p = next((x for x in pasos if x.get("pantalla") == h.get("pantalla") and x.get("captura")), None)
            if p:
                casos.append(dict(id=f"evidencia-{h['id'].lower()}", sesion=sid, paso=p["n"], tema=h.get("donde", ""), titulo=h["titulo"],
                                  observacion=h.get("hallazgo"), interpretacion=h.get("interpretacion"), heuristica=h.get("heuristica", "")))
                break
        if len(casos) == 4:
            break
    return casos


def capitulos_automaticos(ctx: Contexto) -> list[dict]:
    caps = []
    for h in [x for x in hallazgos_orden(ctx.N) if int(x.get("severidad", 0)) >= 3][:4] or hallazgos_orden(ctx.N)[:2]:
        c = ctx.cifra(dict(hallazgo=h["id"]))
        caps.append(dict(etiqueta=h.get("donde") or h["id"], titulo=h["titulo"], intro=h.get("interpretacion"), hallazgos=[h["id"]], bloques=[
            dict(tipo="hallazgo", etiqueta=h.get("donde") or h["id"], cifra=dict(valor=c.texto()) if c and c.x else None,
                 titulo="Lo que se observó", texto=h.get("hallazgo")),
            dict(tipo="accion", texto=h.get("recomendacion"))]))
    return caps


def voces_automaticas(ctx: Contexto) -> list[dict]:
    """La cita de cada perfil en la narrativa, solo si aparece textual en una de sus sesiones."""
    voces = []
    for perfil, d in (ctx.N.get("perfiles") or {}).items():
        sid = next((s for s, x in ctx.sesiones.items() if x.get("integrante") == perfil and _cita_en(ctx, d.get("cita") or "", s)), None)
        if sid:
            voces.append(dict(sesion=sid, cita=d["cita"], momento=f"Tramo {ctx.sesiones[sid].get('tarea')}"))
    return voces


def senales_automaticas(ctx: Contexto) -> list[dict]:
    s = [dict(cifra=dict(auto="completan"), titulo="Llegan al final de su tramo.", texto="Completar el recorrido no garantiza comprender la decisión.",
              enlace="Ver el recorrido", destino="recorrido")]
    for k in (ctx.N.get("kpis") or [])[:2]:
        s.append(dict(cifra=dict(valor=k.get("valor")), titulo=k.get("etiqueta"), texto=k.get("detalle"), enlace="Leer los hallazgos", destino="hallazgos"))
    return s


# ---- bloques ----------------------------------------------------------------------------------------------------


def _capitulo(cuerpo: str, etiqueta: str, titulo: str, intro: str, id_: str = "") -> str:
    largo = ' class="largo"' if len(re.sub(r"<[^>]+>", "", titulo)) > 60 else ""
    id_html = f' id="{id_}"' if id_ else ""
    return (f'<section class="chapter"{id_html}><div class="wrap"><div class="chapter-head"><div><div class="chapter-number">{etiqueta}</div>'
            f'<h2{largo}>{titulo}</h2></div><p>{intro}</p></div>{cuerpo}</div></section>')


def _tarjeta_hallazgo(ctx: Contexto, b: dict) -> str:
    stat = f'<div class="stat num">{valor_html(ctx, b["cifra"])}</div>' if b.get("cifra") else ""
    fuente = f'<p class="source">{ctx.t(b["fuentes"])}</p>' if b.get("fuentes") else ""
    return (f'<article class="finding"><span class="kicker">{ctx.t(b.get("etiqueta"))}</span>{stat}<h3>{ctx.t(b.get("titulo"))}</h3>'
            f'<p>{ctx.t(b.get("texto"))}</p>{fuente}</article>')


def _tarjeta_confianza(ctx: Contexto, b: dict) -> str:
    d = ctx.confianza(b)
    if not d["filas"]:
        return ""
    n = len(d["filas"])
    return f'''<article class="finding confidence-finding"><span class="kicker">{ctx.t(b.get("etiqueta"))}</span><h3>{ctx.t(b.get("titulo"))}</h3><p class="confidence-scale"><strong>Escala de 0 a 100</strong><br>0 = menor confianza · 100 = mayor confianza</p><div class="confidence-comparison" aria-label="Confianza media de {n} corridas sintéticas, antes y después"><div class="confidence-level"><span class="confidence-label">{ctx.t(b.get("etiqueta_antes", "Antes"))}</span><strong class="confidence-value num">{decimal(d["antes"])}<small>/100</small></strong><div class="confidence-track" aria-hidden="true"><i style="width:{d["antes"]:.2f}%"></i></div></div><div class="confidence-level after"><span class="confidence-label">{ctx.t(b.get("etiqueta_despues", "Después"))}</span><strong class="confidence-value num">{decimal(d["despues"])}<small>/100</small></strong><div class="confidence-track" aria-hidden="true"><i style="width:{d["despues"]:.2f}%"></i></div></div></div><p class="confidence-average">Promedios de las mismas {n} corridas sintéticas, redondeados a un decimal.</p><p class="confidence-drop"><strong>{"≈" + str(round(d["caida"])) + " puntos menos" if d["caida"] >= 0 else "≈" + str(round(-d["caida"])) + " puntos más"}, en promedio.</strong> La {"caída" if d["caida"] >= 0 else "diferencia"} varía entre {d["minima"]} y {d["maxima"]} puntos según la corrida. Son puntos de la escala, no porcentajes.</p><p>{ctx.t(b.get("texto"))}</p><p class="confidence-definition">La cifra representa cuánto dice confiar el perfil sintético en el producto en ese momento. No es una medición con clientes reales.</p><p class="source"><a href="lecturas/confianza-calculo.html">Ver el cálculo de las {n} corridas ↗</a>{" · " + ctx.t(b["fuentes"]) if b.get("fuentes") else ""}</p></article>'''


def _tarjeta_orientacion(ctx: Contexto, b: dict) -> str:
    d = ctx.orientacion(b)
    if not d["total"]:
        return ""
    otro = f'<div class="orientation-other"><span>{ctx.t(b.get("otro_titulo"))}</span><p>{ctx.t(b.get("otro"))}</p></div>' if b.get("otro") else ""
    return f'''<article class="finding orientation-finding"><span class="kicker">{ctx.t(b.get("etiqueta", "Orientación · entender el avance"))}</span><p class="orientation-question"><span>La pregunta durante el recorrido</span>“¿Sabes en qué parte del proceso vas y cuánto te falta?”</p><div class="orientation-total num">{d["dudas"]} <span>de {d["total"]}</span></div><h3>Respuestas con dudas sobre el avance</h3><p>Se agrupan las respuestas <strong>“más o menos” y “no”</strong>. Este es el desglose completo:</p><dl class="orientation-breakdown"><div><dt>“Más o menos”</dt><dd>{d["suma"]["mas_o_menos"]} <span>respuestas</span></dd></div><div><dt>“No”</dt><dd>{d["suma"]["no"]} <span>respuestas</span></dd></div><div class="clear"><dt>“Sí”</dt><dd>{d["suma"]["si"]} <span>respuestas</span></dd></div></dl><p class="orientation-base"><strong>Base: {d["sesiones"]} sesiones sintéticas, {d["total"]} respuestas.</strong> {ctx.t(b.get("base", ""))} Cada sesión aporta varias respuestas a lo largo de sus pasos.</p><p class="source"><a href="lecturas/orientacion-calculo.html">Ver cómo se cuentan las respuestas ↗</a></p>{otro}</article>'''


def _panel(ctx: Contexto, p: dict) -> str:
    accion = f'<div class="action"><span>Decisión recomendada</span>{ctx.t(p["accion"])}</div>' if p.get("accion") else ""
    return (f'<article class="story-panel{" accent" if p.get("acento") else ""}"><span class="eyebrow">{ctx.t(p.get("etiqueta"))}</span>'
            f'<span class="big num">{valor_html(ctx, p["cifra"]) if p.get("cifra") else ""}</span><h3>{ctx.t(p.get("titulo"))}</h3><p>{ctx.t(p.get("texto"))}</p>{accion}</article>')


def bloque(ctx: Contexto, b: dict) -> str:
    tipo = b.get("tipo")
    if tipo == "historia":
        return '<div class="story-grid">' + "".join(_panel(ctx, p) for p in b["paneles"]) + "</div>"
    if tipo in ("hallazgo", "confianza", "orientacion"):
        return '<div class="duo solo">' + tarjeta(ctx, b) + "</div>"
    if tipo == "duo":
        return '<div class="duo">' + "".join(tarjeta(ctx, x) for x in b["tarjetas"]) + "</div>"
    if tipo == "accion":
        return f'<div class="action"><span>Decisión recomendada</span>{ctx.t(b.get("texto"))}</div>'
    if tipo == "nota":
        return f'<p class="caption">{ctx.t(b.get("texto"))}</p>'
    if tipo == "comparacion":
        return ('<div class="comparison">' + "".join(f'<article><span>{ctx.t(x.get("estado"))}</span><h3>{ctx.t(x.get("titulo"))}</h3><p>{ctx.t(x.get("texto"))}</p></article>'
                                                     for x in b["elementos"]) + "</div>")
    raise ValueError(f"editorial.yaml: bloque desconocido «{tipo}»")


def tarjeta(ctx: Contexto, b: dict) -> str:
    return {"confianza": _tarjeta_confianza, "orientacion": _tarjeta_orientacion}.get(b.get("tipo"), _tarjeta_hallazgo)(ctx, b)


# ---- secciones de la página -------------------------------------------------------------------------------------


def _portada(ctx: Contexto, casos: list[dict]) -> str:
    E, N = ctx.E, ctx.N
    P = E.get("portada") or {}
    titular = P.get("titular") or [ctx.marca]
    titular = [titular] if isinstance(titular, str) else titular
    h1 = esc(titular[0]) + (f"<br><span>{esc(titular[1])}</span>" if len(titular) > 1 else "")
    senales = P.get("senales") or senales_automaticas(ctx)
    metricas = "".join(f'<a class="urban-metric" href="lecturas/{esc(s.get("destino", "hallazgos"))}.html"><span class="urban-metric-value">{valor_html(ctx, s["cifra"])}</span><span class="urban-metric-copy"><strong>{ctx.t(s.get("titulo"))}</strong><span>{ctx.t(s.get("texto"))}</span><span class="urban-metric-link">{ctx.t(s.get("enlace", "Ver más"))} <span aria-hidden="true">↗</span></span></span></a>'
                       for s in senales[:3])
    enc = P.get("encabezado") or ["Lo esencial del estudio.", "Señales para entender qué pasó"]
    n = len(ctx.metricas)
    edicion = " · ".join(x for x in (E.get("medicion"), fecha_larga(ctx.c.get("fecha"))) if x)
    producto = esc(E.get("producto_nombre") or ctx.c.get("producto") or ctx.marca)
    return f'''<header class="microcosmos-hero" id="inicio" data-urban-hero>
  <div class="urban-stage">
    <div class="urban-panorama" aria-hidden="true">
      <img class="urban-poster" src="assets/urban-hero/poster.jpg" width="1920" height="1080" alt="" fetchpriority="high">
      <video id="urban-video" class="urban-video" width="1920" height="1080" autoplay muted loop playsinline preload="none" poster="assets/urban-hero/poster.jpg" data-src="assets/urban-hero/panorama.mp4" tabindex="-1" disablepictureinpicture></video>
    </div>
    <div class="urban-editorial">
      <p class="urban-edition">{producto} <span>{esc(edicion)}</span></p>
      <h1{' class="largo"' if len(" ".join(titular)) > 55 else ""}>{h1}</h1>
      <p class="urban-intro">{ctx.t(P.get("intro") or N.get("titular"))}</p>
      <div class="urban-actions">
        <a class="urban-cta" href="lecturas/hallazgos.html">{ctx.t(P.get("accion", "Leer los hallazgos"))} <span aria-hidden="true">↗</span></a>
        <a class="urban-method" href="lecturas/metodo.html">Investigación sintética · {n} sesiones · {len(ctx.panel)} perfiles <span aria-hidden="true">↗</span></a>
      </div>
    </div>
    <div class="urban-scene-footer">
      <span class="urban-caption">{ctx.t(P.get("escena", ""))}<small>Escena conceptual · no representa participantes del estudio</small></span>
      <button class="microcosmos-toggle" type="button" aria-controls="urban-video" aria-label="Reproducir animación" aria-pressed="false" hidden><span class="urban-control-icon" aria-hidden="true">▷</span><span class="urban-control-label">Reproducir animación</span></button>
    </div>
  </div>
  <div class="urban-evidence" aria-label="Señales principales del estudio">
    <div class="urban-evidence-heading"><p>{ctx.t(enc[0])}</p><span>{ctx.t(enc[1])}</span></div>
    <div class="urban-metrics">{metricas}</div>
    <p class="urban-evidence-note">Conteos de corridas sintéticas en tramos separados; no son una tasa de conversión de clientes. <a href="lecturas/metodo.html">Cómo se hizo el estudio ↗</a></p>
  </div>
</header>'''


def _apertura(ctx: Contexto) -> str:
    A = ctx.E.get("apertura") or {}
    c = ctx.cifra("completan")
    pregunta = A.get("pregunta") or ctx.c.get("pregunta_principal") or ctx.c.get("titulo")
    resumen = (f"{palabra(len(ctx.panel), True)} perfiles hicieron {palabra(len(ctx.tareas))} tramos del flujo, {palabra(int(ctx.c.get('corridas', 1)))} "
               f"{'vez' if int(ctx.c.get('corridas', 1)) == 1 else 'veces'} cada uno. Estos conteos describen corridas sintéticas, no clientes.")
    return (f'<div class="wrap opening"><div><span class="eyebrow">La pregunta que guio la prueba</span><p class="lead">{ctx.t(pregunta)}</p>'
            f'<p>{ctx.t(A.get("respuesta") or ctx.N.get("veredicto"))}</p></div><aside class="opening-aside"><strong class="num">{c.texto()}</strong>'
            f'<span>sesiones sintéticas llegaron al final definido para su tramo. Llegar no equivale a decidir con claridad.</span><span class="muted">{resumen}</span></aside></div>')


def _tramo(ctx: Contexto, i: int, t: dict) -> str:
    tid = t["id"]
    T = (ctx.E.get("tramos") or {}).get(tid) or {}
    ms = ctx.de_tarea(tid)
    hechas = sum(1 for m in ms if m["completa"])
    cuenta: dict = {}
    for m in ms:
        cuenta[m["resultado"]] = cuenta.get(m["resultado"], 0) + 1
    nota = T.get("nota") or " · ".join(f"{v} {RESULTADOS.get(k, k)}" for k, v in cuenta.items())
    barras = "".join('<i class="done"></i>' if j < hechas else "<i></i>" for j in range(len(ms)))
    return (f'<article class="journey-card"><div class="card-top"><span class="stage"><b>TRAMO {i:02d}</b>{esc(t["nombre"])}</span><a class="card-open" href="lecturas/tramo-{tid}.html" aria-label="Leer detalle: {esc(t["nombre"])}">↗</a></div>'
            f'<div class="value num">{hechas}<span>/{len(ms)}</span></div><h3>{ctx.t(T.get("logro", "Completan la tarea"))}</h3><p>{ctx.t(nota)}</p>'
            f'<div class="card-base"><div class="card-count"><span>Completan el tramo</span><span>{hechas} de {len(ms)} corridas</span></div><div class="card-bars" aria-hidden="true">{barras}</div></div></article>')


def _recorrido(ctx: Contexto) -> str:
    R = ctx.E.get("recorrido") or {}
    n = len(ctx.tareas)
    cada = len(ctx.de_tarea(ctx.tareas[0]["id"])) if n else 0
    cards = "".join(_tramo(ctx, i, t) for i, t in enumerate(ctx.tareas, 1))
    tension = R.get("tension") or []
    signal = ""
    if tension:
        signal = '<div class="signal">' + "".join(
            (f'<div>{"<span class=eyebrow style=color:#bbd2c9>La tensión central</span>" if j == 0 else ""}<b class="num">{ctx.t(x.get("cifra"))}</b><p>{ctx.t(x.get("texto"))}</p>'
             + (f'<small>{ctx.t(x["nota"])}</small>' if x.get("nota") else "") + "</div>") for j, x in enumerate(tension)) + "</div>"
    intro = R.get("intro") or (f"El protocolo separó el viaje en {palabra(n)} momentos para observar dónde se rompe la comprensión. Cada momento se probó "
                               f"{palabra(cada)} veces. Por eso estos números describen **tramos separados**, no un embudo de las mismas personas.")
    pie = ('<p class="caption">Cada tramo es una tarea del protocolo; aquí usamos nombres de acciones para que el resultado se entienda sin códigos. '
           'Fuente: <a href="lecturas/datos-agregados.html">datos agregados</a> y <a href="lecturas/protocolo.html">protocolo</a>.</p>')
    cuerpo = f'<div class="journey" data-n="{n}" aria-label="Resultados de los momentos del flujo">{cards}</div>{pie}{signal}'
    return _capitulo(cuerpo, "01 / El recorrido", ctx.t(R.get("titulo") or f"{ctx.cifra('completan').texto('de')} corridas llegan al final de su tramo."), ctx.t(intro), "recorrido")


def _tam(ctx: Contexto, captura: str) -> str:
    try:
        with Image.open(ctx.e.dir / captura) as im:
            return f' width="{im.width}" height="{im.height}"'
    except OSError:
        return ""


def _evidencias(ctx: Contexto, casos: list[dict], inv: dict) -> str:
    if not casos:
        return ""
    tarjetas = ""
    for c in casos:
        paso = next(p for p in ctx.sesiones[c["sesion"]]["pasos"] if p["n"] == c["paso"])
        cap = paso.get("captura")
        img = f'<img src="../{esc(cap)}" alt="{esc(c["titulo"])} · paso {c["paso"]}" loading="lazy"{_tam(ctx, cap)}>' if cap else ""
        tarjetas += (f'<article class="evidence-card"><div class="evidence-preview">{img}</div><div class="evidence-card-body"><span class="ev-kicker">{esc(c.get("tema", ""))}</span>'
                     f'<h3>{esc(c["titulo"])}</h3><p>{esc(c["sesion"])} · paso {c["paso"]}<br>Captura, {"video" if ctx.sesiones[c["sesion"]].get("video") else "sesión"} y mapa de toques</p><a href="lecturas/{esc(c["id"])}.html" aria-label="Ver evidencia: {esc(c["titulo"])}">Explorar el caso ↗</a></div></article>')
    grabadas = f'{inv["sesiones"]} sesiones con grabación' if inv["con_video"] == inv["sesiones"] else f'{inv["sesiones"]} sesiones · {inv["con_video"]} grabaciones'
    fin = (f'<div class="evidence-bottom"><p><strong>{grabadas} · {inv["mapas"]} mapas de acciones.</strong><br>Las capturas registran '
           f'{esc(material(ctx))}; los pensamientos son sintéticos. Los mapas agregan toques y escritura, no seguimiento de mirada.</p><a class="evidence-library-link" href="lecturas/evidencias.html">Explorar la biblioteca <span aria-hidden="true">↗</span></a></div>')
    intro = f"{palabra(len(casos), True)} momentos para contrastar la lectura del estudio con {material(ctx)}: la pantalla que se mostró, la acción registrada y lo que expresó el perfil sintético."
    cuerpo = f'<div class="evidence-cards">{tarjetas}</div>{fin}'
    return (f'<section class="chapter evidence-section" id="evidencias"><div class="wrap"><div class="chapter-head"><div><div class="chapter-number">La evidencia / Del hallazgo a la pantalla</div>'
            f'<h2>No te quedes con la conclusión. Mira qué pasó.</h2></div><p>{intro}</p></div>{cuerpo}</div></section>')


def material(ctx: Contexto) -> str:
    return ctx.E.get("material_nombre") or {"figma": "el prototipo"}.get(ctx.c.get("material"), "el producto")


def _voces(ctx: Contexto) -> str:
    V = ctx.E.get("voces") or voces_automaticas(ctx)
    if not V:
        return ""
    panel = {it.id: it for it in ctx.panel}
    tarjetas = ""
    for v in V:
        s = ctx.sesiones.get(v["sesion"]) or {}
        it = panel.get(s.get("integrante"))
        nombre = (s.get("nombre") or v["sesion"]).split()[0]
        cara = (f'<span class="avatar {esc(s.get("integrante"))}" role="img" aria-label="Retrato ilustrativo de {esc(nombre)}"></span>' if s.get("integrante") in AVATARES_PWA
                else f'<span class="avatar inicial" aria-hidden="true">{esc(nombre[:1])}</span>')
        edad = f" · {it.edad} años" if it and it.edad else ""
        tarjetas += (f'<article class="voice"><blockquote>{esc(v["cita"], quote=False)}</blockquote><footer>{cara}<span><b>{esc(nombre)}{edad}</b>{ctx.t(v.get("momento"))} · '
                     f'<a href="lecturas/{esc(v["sesion"])}.html">Ver sesión</a></span></footer></article>')
    titulo = ctx.E.get("voces_titulo") or ("Un momento que explica los datos." if len(V) == 1 else f"{palabra(len(V), True).replace('Una', 'Un')} momentos que explican los datos.")
    return f'''<section class="voices-section" aria-labelledby="voices-title"><div class="wrap"><div class="voices-header"><div><span class="eyebrow">Las voces detrás de la fricción</span><h2 id="voices-title">{ctx.t(titulo)}</h2></div><div class="voice-controls"><button type="button" id="prev-voice" aria-label="Ver comentarios anteriores">←</button><button type="button" id="next-voice" aria-label="Ver más comentarios">→</button></div></div><div class="voices" id="voices" tabindex="0" aria-label="Carrusel de comentarios sintéticos">{tarjetas}</div><p class="voices-note">Son pensamientos registrados en las sesiones de {palabra(len({(ctx.sesiones.get(v["sesion"]) or {}).get("integrante") for v in V}))} perfiles simulados. Los retratos son avatares generados para representar a esos perfiles; no son fotografías de participantes reales.</p></div></section>'''


def _capitulos(ctx: Contexto, voces: str) -> tuple[str, int]:
    caps = ctx.E.get("capitulos") or capitulos_automaticos(ctx)
    tras = int(ctx.E.get("voces_tras_capitulo", 1))
    salida, n = "", 1
    for i, c in enumerate(x for x in caps if not x.get("tras_hipotesis")):
        n += 1
        salida += _un_capitulo(ctx, c, n, "hallazgos" if i == 0 else "")
        if i + 1 == tras:
            salida += voces
    return (salida if sum(1 for x in caps if not x.get("tras_hipotesis")) >= tras else salida + voces), n


def _un_capitulo(ctx: Contexto, c: dict, n: int, id_: str = "") -> str:
    cuerpo = "".join(bloque(ctx, b) for b in c.get("bloques") or [])
    return _capitulo(cuerpo, f"{n:02d} / {ctx.t(c.get('etiqueta'))}", ctx.t(c.get("titulo")), ctx.t(c.get("intro")), id_)


def _tras_hipotesis(ctx: Contexto, n: int) -> tuple[str, int]:
    """Capítulos que van después de responder al protocolo, como la comparación con una medición anterior."""
    salida = ""
    for c in (x for x in ctx.E.get("capitulos") or [] if x.get("tras_hipotesis")):
        n += 1
        salida += _un_capitulo(ctx, c, n)
    return salida, n


def _hipotesis(ctx: Contexto, n: int) -> tuple[str, int]:
    hs = ctx.c.get("hipotesis") or []
    res = {h["id"]: h for h in ctx.N.get("hipotesis_resultado") or []}
    if not hs:
        return "", n
    n += 1
    H = ctx.E.get("hipotesis") or {}
    filas = ""
    for i, h in enumerate(hs, 1):
        r, x = res.get(h["id"]) or {}, H.get(h["id"]) or {}
        etiqueta, clase = ESTADOS.get(r.get("estado"), ("Sin resultado", " nuance"))
        if x.get("matiz"):
            etiqueta, clase = x["matiz"], " nuance"
        filas += (f'<article class="hypothesis"><span class="index">Hipótesis {i}</span><div><h3>{ctx.t(x.get("titulo") or h.get("texto"))}</h3><p>{ctx.t(x.get("texto") or r.get("evidencia"))}</p></div>'
                  f'<span class="status{clase}">{esc(etiqueta)}</span></article>')
    sos = sum(1 for h in hs if (res.get(h["id"]) or {}).get("estado") == "se_sostiene")
    resto = len(hs) - sos
    titulo = f"{palabra(len(hs), True)} hipótesis. {palabra(sos, True)} se {'sostiene' if sos == 1 else 'sostienen'}; {palabra(resto)} {'cambia' if resto == 1 else 'cambian'}."
    intro = "“Se sostiene” significa que estas corridas apoyan la hipótesis del protocolo. No implica que el patrón tenga la misma frecuencia en clientes reales."
    return _capitulo(filas, f"{n:02d} / Respuesta al protocolo", esc(titulo), intro, "hipotesis"), n


def _positivos(ctx: Contexto, n: int) -> tuple[str, int]:
    """Siempre hay hallazgos positivos: si ningún capítulo los compara, se muestran aquí."""
    if any(b.get("tipo") == "comparacion" for c in ctx.E.get("capitulos") or [] for b in c.get("bloques") or []):
        return "", n
    xs = (ctx.N.get("positivos") or [])[:3]
    if not xs:
        return "", n
    n += 1
    filas = "".join(f'<article><span>Funciona</span><p>{ctx.t(x.get("texto") if isinstance(x, dict) else x)}</p></article>' for x in xs)
    return _capitulo(f'<div class="comparison">{filas}</div>', f"{n:02d} / Lo que ya funciona", "Hay avances que conviene conservar.",
                     "Estos puntos funcionaron en las corridas sintéticas. Conviene protegerlos al corregir lo demás."), n


def _decisiones(ctx: Contexto, n: int) -> str:
    D = ctx.E.get("decisiones") or {}
    prio = D.get("prioridades") or [dict(titulo=h["titulo"], texto=h.get("recomendacion")) for h in hallazgos_orden(ctx.N)[:5]]
    filas = "".join(f'<div class="priority"><span class="n num">{i:02d}</span><h3>{ctx.t(p.get("titulo"))}</h3><p>{ctx.t(p.get("texto"))}</p></div>' for i, p in enumerate(prio, 1))
    return _capitulo(filas, f"{n + 1:02d} / Qué hacer ahora", ctx.t(D.get("titulo", "Qué conviene corregir primero.")),
                     ctx.t(D.get("intro", "El orden prioriza la severidad y los puntos donde el estudio observó abandono o caídas de confianza. Después conviene validar los cambios con personas.")),
                     "decisiones")


def _metodo(ctx: Contexto, claves: set[str]) -> str:
    from . import seccion_validar, texto_validar

    c, M = ctx.c, ctx.E.get("metodo") or {}
    corridas = int(c.get("corridas", 1))
    disp = c.get("dispositivo") or {}
    p1 = (f"Se hicieron **{len(ctx.metricas)} sesiones sintéticas**: {palabra(len(ctx.panel))} perfiles, {palabra(len(ctx.tareas))} tramos del recorrido y "
          f"{palabra(corridas)} {'corrida' if corridas == 1 else 'corridas'} por combinación." + (f" El dispositivo fue un {disp['emular']} emulado." if disp.get("emular") else ""))
    ine = ctx.inestables()
    if ine:
        p1 += f" {palabra(ine[0], True)} de {ine[1]} combinaciones perfil–tramo cambiaron de resultado entre corridas."
    parrafos = [p1] + (M.get("parrafos") or [x for x in (ctx.N.get("limitaciones") or [])[:2]])
    izq = "".join(f"<p>{ctx.t(p)}</p>" for p in parrafos)
    validar = [texto_validar(v) for v in ctx.N.get("validar_con_personas") or []]
    muestra = re.sub(r"<[^>]+>", " ", seccion_validar(ctx.e, ctx.N).split("</ul>")[-1]).strip()
    falta = M.get("falta") or ("La frecuencia de estos patrones en clientes reales y el efecto de las correcciones. " + " ".join(f"{v}." for v in validar[:2]))
    enlaces = [("evidencias", "Capturas, sesiones y mapas de toques"), ("protocolo", "Protocolo"), ("datos-agregados", "Datos agregados"), ("tecnico", "Auditoría técnica"),
               ("auditoria", "Evaluación heurística asistida por IA"), ("detalle", "Detalle completo"), ("tablero", "Tablero interactivo")]
    fuentes = "".join(f'<a href="lecturas/{k}.html">{t}</a>' for k, t in enlaces if k in claves)
    return f'''<aside class="method" id="metodo"><div class="wrap"><span class="eyebrow">Cómo leer este estudio</span><h2>Datos útiles, con límites visibles.</h2><div class="method-grid"><div>{izq}</div><div><details><summary>Qué puede afirmar este reporte</summary><p>Qué pasó en estas corridas, dónde se observaron dudas o abandonos y qué hipótesis del protocolo recibieron apoyo. Los comentarios son salidas de perfiles sintéticos y están enlazados a sus archivos de sesión.</p></details><details><summary>Qué falta comprobar</summary><p>{ctx.t(falta)}</p>{f"<p>{esc(muestra)}</p>" if muestra else ""}</details><details><summary>Fuentes y trazabilidad</summary><p>El detalle completo conserva hallazgos, recomendaciones y sesiones. El tablero interactivo sigue disponible para profundizar.</p></details><div class="source-links">{fuentes}</div></div></div></div></aside>'''


# ---- lecturas calculadas ------------------------------------------------------------------------------------------


def _bloques_de(ctx: Contexto, tipo: str):
    for c in ctx.E.get("capitulos") or []:
        for b in c.get("bloques") or []:
            for x in ([b] + (b.get("tarjetas") or [])):
                if x.get("tipo") == tipo:
                    yield x


def _lectura_hallazgos(ctx: Contexto) -> str:
    salida = ""
    for h in hallazgos_orden(ctx.N):
        ses = " · ".join(f'<a href="lecturas/{esc(s)}.html">{esc(s)}</a>' for s in h.get("sesiones") or [])
        salida += (f'<section id="{esc(h["id"])}"><h2>{esc(h["id"])} · {esc(h["titulo"])}</h2><p><small>{esc(h.get("donde", ""))} · severidad {h.get("severidad")}/4 · confianza {esc(h.get("confianza", "—"))}</small></p>'
                   f'<h3>Qué se observó</h3><p>{esc(h.get("hallazgo", ""))}</p><h3>Qué podría significar</h3><p>{esc(h.get("interpretacion", ""))}</p><h3>Qué conviene hacer</h3><p>{esc(h.get("recomendacion", ""))}</p>'
                   + (f"<p><small>Sesiones: {ses}</small></p>" if ses else "") + "</section>")
    return salida


def _lectura_confianza(ctx: Contexto, b: dict) -> str:
    d = ctx.confianza(b)
    filas = "".join(f'<tr><td><a href="lecturas/{f["sesion"]}.html">{esc(str(f["nombre"]))} · corrida {f["corrida"]}</a></td><td>{f["antes"]}/100</td><td>{f["despues"]}/100</td><td>{f["caida"]} puntos</td></tr>' for f in d["filas"])
    ej = d["filas"][0]
    return (f'<h2>Qué mide esta cifra</h2><p>En cada pantalla se pide al perfil sintético indicar, de 0 a 100, cuánto confía en el producto en ese momento. Es una valoración de la simulación, no una medición con clientes reales.</p>'
            f'<h2>Qué momentos se comparan</h2><p>Antes: {esc(b["antes"])}. Después: {esc(b["despues"])}. Se comparan esos dos registros dentro de cada corrida.</p>'
            f'<table><thead><tr><th>Sesión sintética</th><th>Antes</th><th>Después</th><th>Diferencia</th></tr></thead><tbody>{filas}</tbody></table>'
            f'<h2>Cómo se calcula</h2><p>Diferencia por corrida = confianza antes − confianza después. Por ejemplo, {esc(str(ej["nombre"]))} en la corrida {ej["corrida"]}: {ej["antes"]} − {ej["despues"]} = {ej["caida"]} puntos.</p>'
            f'<p>Promedio antes: {d["antes"]}/100. Promedio después: {d["despues"]}/100. Diferencia media: {d["caida"]} puntos. La diferencia menor es {d["minima"]} puntos y la mayor es {d["maxima"]}. No se restan los extremos de los rangos generales.</p>')


def _lectura_orientacion(ctx: Contexto, b: dict) -> str:
    d = ctx.orientacion(b)
    fila = lambda n, g: f'<tr><td>{n}</td><td>{g.get("mas_o_menos", 0)}</td><td>{g.get("no", 0)}</td><td>{g.get("si", 0)}</td><td>{sum(g.values())}</td></tr>'  # noqa: E731
    por_tarea = {}
    for t, _, g in d["filas"]:
        x = por_tarea.setdefault(t, {})
        for k, v in g.items():
            x[k] = x.get(k, 0) + v
    tabla = "<table><thead><tr><th>{}</th><th>Más o menos</th><th>No</th><th>Sí</th><th>Total</th></tr></thead><tbody>{}</tbody></table>"
    return (f'<h2>La pregunta que se repite</h2><blockquote>¿Sabes en qué parte del proceso vas y cuánto te falta?</blockquote><p>En cada paso con una respuesta registrada se cuenta una opción del perfil sintético: sí, más o menos o no. Una misma sesión aporta varias respuestas. Los conteos no representan personas distintas ni pantallas únicas.</p>'
            f'<h2>Cómo se obtiene el total</h2><p>{d["suma"]["mas_o_menos"]} “más o menos” + {d["suma"]["no"]} “no” = {d["dudas"]} respuestas con dudas. Al sumar las {d["suma"]["si"]} respuestas “sí”, la base es {d["total"]}.</p>'
            + tabla.format("Tramo", "".join(fila(t, g) for t, g in por_tarea.items()))
            + f'<h2>Comprobar las {d["sesiones"]} sesiones</h2>' + tabla.format("Sesión sintética", "".join(fila(f'<a href="lecturas/{s}.html">{s}</a>', g) for _, s, g in d["filas"]))
            + "<h2>Cómo interpretar este resultado</h2><p>Las sesiones más largas aportan más respuestas; esta métrica describe los pasos observados, no una proporción de clientes.</p>")


def _lecturas(ctx: Contexto, b: Biblioteca, nombre: str, casos: list[dict]) -> dict:
    e, N = ctx.e, ctx.N
    b.agregar("datos-agregados", "Los resultados, tramo por tramo", "aggregate",
              f"{len(ctx.metricas)} sesiones sintéticas · {len(ctx.panel)} perfiles · {len(ctx.tareas)} tramos.", ctx.R, "../datos/agregado.json")
    for clave, titulo, desc in (("tecnico", "Auditoría técnica", "Carga, accesibilidad, permisos y retoma en el entorno de pruebas."),
                                ("auditoria", "Evaluación heurística asistida por IA", "Evaluaciones independientes realizadas por modelos de IA. Observaciones consolidadas con criterios de usabilidad; no equivale a una revisión con especialistas humanos.")):
        f = e.ruta("datos", f"{clave}.json")
        if f.exists():
            b.agregar(clave, titulo, "json", desc, json.loads(f.read_text(encoding="utf-8")), f"../datos/{clave}.json")
    for sid, s in ctx.sesiones.items():
        b.agregar(sid, f"{s.get('nombre', s.get('integrante', 'Perfil'))} · {s.get('tarea', '')} · corrida {s.get('corrida', '')}", "session",
                  "Registro de un perfil sintético. Sus pensamientos no son testimonios de participantes reales.", s, f"../datos/sesiones/{sid}.json")
    b.agregar("sintesis", "Síntesis del estudio", "json", "Hallazgos, interpretación y recomendaciones del estudio.", N, "../narrativa.yaml")
    prot = e.ruta("PROTOCOLO.md")
    b.agregar("protocolo", "Cómo se diseñó la investigación", "markdown", "Objetivos, hipótesis, tareas y límites.",
              prot.read_text(encoding="utf-8") if prot.exists() else "Sin protocolo en el estudio.", "../PROTOCOLO.md")
    a = ctx.E.get("antecedente")
    if a:
        ruta = (e.dir / a["ruta"]).resolve()
        rel = "../" + a["ruta"]
        b.agregar("antecedente", a.get("titulo", "Medición anterior"), "markdown", a.get("descripcion", "Antecedente del estudio."), ruta.read_text(encoding="utf-8"), rel, rel)
    for sufijo, titulo in (("detalle", "Detalle completo"), ("tablero", "Tablero interactivo")):
        arch = f"{nombre}-{sufijo}.html"
        f = e.ruta("reporte", arch)
        if f.exists():
            cuerpo = re.search(r"<body[^>]*>([\s\S]*?)</body>", f.read_text(encoding="utf-8"), re.I)
            b.agregar(sufijo, titulo, "html", "Versión de lectura del documento. El archivo original conserva su presentación y sus gráficos interactivos.",
                      limpiar(cuerpo[1] if cuerpo else ""), arch)
    b.agregar("hallazgos", "Todos los hallazgos del estudio", "html", f"{len(N.get('hallazgos') or [])} hallazgos, de mayor a menor severidad.", _lectura_hallazgos(ctx))
    for t in ctx.tareas:
        ms = ctx.de_tarea(t["id"])
        hechas = sum(1 for m in ms if m["completa"])
        T = (ctx.E.get("tramos") or {}).get(t["id"]) or {}
        b.agregar(f"tramo-{t['id']}", t["nombre"], "stage", f"{t['id']} · {len(ms)} corridas sintéticas independientes.",
                  dict(total=len(ms), complete=hechas, heading=T.get("logro", "Completan la tarea"), description=T.get("nota", ""), sessions=ms), "../datos/agregado.json")
    conf = next(_bloques_de(ctx, "confianza"), None)
    if conf and ctx.confianza(conf)["filas"]:
        b.agregar("confianza-calculo", "La confianza, antes y después", "html", f"Escala de 0 a 100 · {len(ctx.confianza(conf)['filas'])} corridas sintéticas · cálculo comprobable por sesión.", _lectura_confianza(ctx, conf))
    ori = next(_bloques_de(ctx, "orientacion"), None)
    if ori and ctx.orientacion(ori)["total"]:
        b.agregar("orientacion-calculo", "Qué significa saber dónde van", "html", f"La pregunta, las opciones y la base del conteo · {ctx.orientacion(ori)['sesiones']} sesiones sintéticas.", _lectura_orientacion(ctx, ori))
    return evidencias(e, b, ctx.sesiones, casos)


# ---- armado -------------------------------------------------------------------------------------------------------


def construir(e: Estudio, N: dict, nombre: str) -> str:
    """Copia los recursos, genera las lecturas y devuelve el HTML principal."""
    reporte = e.ruta("reporte")
    shutil.copytree(RECURSOS, reporte / "assets", dirs_exist_ok=True)
    ctx = Contexto(e, N)
    principal = f"{nombre}.html"
    casos = ctx.E.get("casos") or casos_automaticos(ctx)
    b = Biblioteca(reporte, principal, ctx.marca)
    inv = _lecturas(ctx, b, nombre, casos)
    voces = _voces(ctx)
    capitulos, n = _capitulos(ctx, voces)
    hip, n = _hipotesis(ctx, n)
    tras, n = _tras_hipotesis(ctx, n)
    pos, n = _positivos(ctx, n)
    secciones = dict(recorrido=_recorrido(ctx), hipotesis=hip, decisiones=_decisiones(ctx, n))
    metodo = _metodo(ctx, set(b.manifiesto))
    secciones["metodo"] = metodo
    for clave, titulo, en in (("recorrido", "El recorrido", secciones["recorrido"]), ("hipotesis", "Las hipótesis", hip), ("decisiones", "Qué hacer ahora", secciones["decisiones"]), ("metodo", "Cómo leer este estudio", metodo)):
        if en:
            b.agregar(clave, titulo, "html", f"{ctx.marca} · investigación sintética.", limpiar(en), f"{principal}#{clave}", principal)
    fecha = fecha_larga(ctx.c.get("fecha"))
    b.cerrar(dict(principal=principal, marca=ctx.marca, fecha=fecha, material=material(ctx), corridas=int(ctx.c.get("corridas", 1)), tareas=ctx.tareas))
    enlaces_nav = [("recorrido", "Recorrido"), ("hallazgos", "Hallazgos")] + ([("hipotesis", "Hipótesis")] if hip else []) + [("decisiones", "Decisiones")]
    nav = "".join(f'<a href="lecturas/{k}.html">{t}</a>' for k, t in enlaces_nav) + '<a class="evidence-nav" href="lecturas/evidencias.html">Evidencias ↗</a>'
    titular = (ctx.E.get("portada") or {}).get("titular") or [ctx.marca]
    titulo_pag = titular if isinstance(titular, str) else titular[-1]
    desc = re.sub(r"\s+", " ", str(N.get("titular") or ""))[:200]
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="data:,">
  <meta name="description" content="{esc(desc)}">
  <title>{esc(titulo_pag)} · {esc(ctx.marca)}</title>
  <link rel="stylesheet" href="assets/editorial/editorial.css">
  <link rel="stylesheet" href="assets/urban-hero/hero.css">
  <link rel="stylesheet" href="assets/report-reader/reader.css">
  <link rel="stylesheet" href="assets/evidence/evidence.css">
</head>
<body>
<a class="skip" href="#contenido">Ir al contenido</a>
<nav class="nav" aria-label="Navegación del reporte"><div class="wrap"><a class="brand" href="#inicio">{esc(ctx.marca)} <span class="muted">/ Investigación sintética</span></a><div class="nav-links">{nav}</div></div></nav>
{_portada(ctx, casos)}
<main id="contenido">
  {_apertura(ctx)}
  {secciones["recorrido"]}
  {_evidencias(ctx, casos, inv)}
  {capitulos}
  {hip}
  {tras}
  {pos}
  {secciones["decisiones"]}
  {metodo}
</main><footer class="wrap end"><span>{esc(ctx.marca)} · Edición editorial · {esc(fecha)}</span><span>Investigación UX sintética · {esc(str(ctx.c.get("autor", "")))}</span></footer>
<script src="assets/urban-hero/video.js"></script>
<script src="assets/report-reader/manifest.js"></script>
<script src="assets/evidence/evidence.js"></script>
<script src="assets/report-reader/insights.js"></script>
<script src="assets/report-reader/reader.js"></script>
<script>
  const voices=document.getElementById('voices');
  if(voices){{document.getElementById('prev-voice').addEventListener('click',()=>voices.scrollBy({{left:-Math.min(voices.clientWidth*.8,456),behavior:'smooth'}}));
  document.getElementById('next-voice').addEventListener('click',()=>voices.scrollBy({{left:Math.min(voices.clientWidth*.8,456),behavior:'smooth'}}));}}
</script>
</body>
</html>
'''


# ---- verificación -------------------------------------------------------------------------------------------------


def _cita_en(ctx: Contexto, cita: str, sid: str | None) -> bool:
    norma = lambda x: re.sub(r"\W+", " ", x.lower()).strip()  # noqa: E731
    s = ctx.sesiones.get(sid or "")
    return bool(s) and norma(cita) in norma(" ".join((p.get("perfil") or {}).get("pensamiento") or "" for p in s["pasos"]))


def textos(x, ruta="editorial"):
    """Todas las cadenas de editorial.yaml con su ruta; las cifras declaradas se revisan aparte."""
    if isinstance(x, str):
        yield ruta, x
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in ("cifras", "cifra", "sesiones", "cita", "ruta"):
                yield from textos(v, f"{ruta}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from textos(v, f"{ruta}[{i}]")


def revisar(e: Estudio, N: dict) -> tuple[list, list, list]:
    """Control de `arnes verificar`: cifras, citas, casos, enlaces y cobertura. Devuelve (ok, avisos, errores)."""
    ok, avi, err = [], [], []
    ctx = Contexto(e, N)
    E = ctx.E
    if not (E.get("portada") or {}).get("titular"):
        avi.append("sin editorial.yaml: el reporte salió con portada y capítulos automáticos (metodos/recorrido/editorial.plantilla.yaml)")
    for nombre, d in (E.get("cifras") or {}).items():
        c = ctx.cifra(d)
        if not c:
            err.append(f"editorial: la cifra «{nombre}» no se puede calcular")
        elif not c.trazable:
            avi.append(f"editorial: la cifra «{nombre}» ({c.texto()}) no tiene sesiones que la respalden")
        elif d.get("valor") and str(d["valor"]) != c.texto():
            err.append(f"editorial: «{nombre}» dice {d['valor']} y los datos dicen {c.texto()}")
        else:
            ok.append(f"editorial: cifra «{nombre}» {c.texto()} recontada")
        faltan = [s for s in d.get("sesiones") or [] if s not in ctx.sesiones] if isinstance(d, dict) else []
        if faltan:
            err.append(f"editorial: «{nombre}» cita sesiones inexistentes {faltan[:4]}")
    for v in E.get("voces") or []:
        if _cita_en(ctx, v.get("cita", ""), v.get("sesion")):
            ok.append(f"editorial: cita de {v['sesion']} es textual")
        else:
            err.append(f"editorial: la cita «{v.get('cita', '')[:50]}…» no aparece textual en {v.get('sesion')}")
    for c in E.get("casos") or []:
        s = ctx.sesiones.get(c.get("sesion"))
        p = next((x for x in (s or {}).get("pasos", []) if x["n"] == c.get("paso")), None)
        if not p:
            err.append(f"editorial: el caso {c.get('id')} apunta a un paso que no existe ({c.get('sesion')} paso {c.get('paso')})")
        elif c.get("pantalla") and p.get("pantalla") != c["pantalla"]:
            err.append(f"editorial: el caso {c.get('id')} dice pantalla {c['pantalla']} y el paso registra {p.get('pantalla')}")
    if not E.get("casos") and E:
        avi.append("editorial: sin «casos»: se eligieron automáticamente de los hallazgos más severos")
    cubiertos = {h for c in E.get("capitulos") or [] for h in c.get("hallazgos") or []}
    if E.get("capitulos"):
        fuera = [h["id"] for h in N.get("hallazgos") or [] if int(h.get("severidad", 0)) >= 3 and h["id"] not in cubiertos]
        if fuera:
            avi.append(f"editorial: hallazgos de severidad 3–4 fuera de los capítulos: {', '.join(fuera)} (siguen en la lectura de hallazgos)")
    for ruta, t in textos(E):
        for m in re.finditer(r"(?<![\d/{$])\b(\d+)\s*(?:/|de)\s*(\d+)\b(?![\d/])", t):
            avi.append(f"{ruta}: «{m[0]}» está escrito a mano; usa una cifra de `cifras` para que se recuente")
    for b in _bloques_de(ctx, "confianza"):
        if not ctx.confianza(b)["filas"]:
            err.append(f"editorial: ninguna sesión de {b.get('tarea')} registra {b.get('antes')} y {b.get('despues')}")
    h = e.ruta("reporte", f"{e.entregable()}.html")
    if h.exists():
        malos = sorted({x for x in re.findall(r'(?:href|src)="((?:lecturas|assets)/[^"#]+)', h.read_text(encoding="utf-8")) if not (h.parent / x).exists()})
        (err if malos else ok).append(f"editorial: enlaces rotos {malos[:5]}" if malos else "editorial: enlaces y recursos locales presentes")
    return ok, avi, err
