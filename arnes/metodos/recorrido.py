"""Método 3 · Recorrido de un flujo interactivo (prototipo Figma o sitio web real) con perfiles sintéticos.

Consolida OU-PWA (prototipo y dev), entrecalles y el skill auditoria-prototipos-figma. Dos modos:

- **autónomo** (por defecto): en cada pantalla el perfil mira la captura, elige qué hacer y por qué;
  el arnés ejecuta el toque y le cuenta qué pasó. La RUTA y los TOQUES son reales sobre el material;
  lo que el perfil piensa y decide es [SIMULACIÓN].
- **guion** (`--guion`): ejecuta pasos escritos por el investigador, como en entrecalles. Sirve para
  reproducir una sesión exacta o grabar un video demostrativo.

Honestidad del método:
- Un toque sin respuesta en un prototipo NO es un defecto por sí solo: puede ser estado de
  prototipado (categoría B del skill de auditoría). Se registra y se clasifica después.
- El perfil ve numerados los elementos que responden. Un usuario real no los ve: es una ayuda del
  instrumento, declarada como [SUPUESTO METODOLÓGICO]. Por eso el perfil dice primero, con sus palabras,
  qué quiere hacer, y puede responder «lo que quiero tocar no está marcado» (marca 0).
- La duración de la sesión no es una medición de tiempo de tarea.
"""

from __future__ import annotations

import collections
import csv
import json
import time

from .. import motor
from ..estudio import Estudio
from .. import consumo
from ..guardia import limpiar
from ..navegador import Navegador, marcar, node_id, recortar

REGLAS_SESION = """

## Reglas de esta sesión de prueba

- Estás usando el producto en tu celular para cumplir una tarea. Actúa como lo harías tú, no como alguien que ya conoce la interfaz.
- Solo sabes lo que ves en la pantalla. No supongas pasos, funciones ni políticas que no aparezcan.
- Puedes dudar, no leer algo, equivocarte, volver atrás, malinterpretar o abandonar si tu perfil lo haría. No tienes que terminar.
- No intentes agradar a quien observa ni adivinar qué respuesta espera.
- Si el producto te pide datos, usa solo los datos de prueba que se te dan. Nunca inventes datos personales reales.
- Si algo cae fuera de lo que tu perfil cubre, usa la frase exacta de tu rol y anótalo en "sin_cobertura".
- Responde únicamente con un objeto JSON válido, sin texto antes ni después y sin bloque de código."""

ACCIONES = ["tocar", "escribir", "desplazar_abajo", "desplazar_arriba", "volver", "esperar", "abandonar", "terminar"]

PLANTILLA = """{
  "primera_impresion": "qué te parece esta pantalla al verla, en una frase",
  "que_miras_primero": "lo primero que te llama la atención",
  "interpretacion": "qué crees que está pasando o qué te pide esta pantalla",
  "pensamiento": "lo que piensas en voz alta, una o dos frases cortas",
  "intencion": "qué quieres hacer ahora, con tus palabras, antes de mirar los números",
  "accion": {"opcion": "tocar | escribir | desplazar_abajo | desplazar_arriba | volver | esperar | abandonar | terminar", "texto": "por qué lo haces"},
  "marca": "número del elemento que tocas o donde escribes; 0 si no aplica o si lo que quieres tocar no está marcado",
  "escribir": "el texto que escribes, solo si la acción es escribir",
  "progreso": {"opcion": "si | mas_o_menos | no", "texto": "¿sabes en qué parte del proceso vas y cuánto te falta?"},
  "confianza": "de 0 a 100, cuánto confías ahora en el producto",
  "friccion": "de 0 a 5: 0 ninguna, 1 mínima, 2 ligera, 3 importante, 4 severa, 5 abandono probable",
  "reglas": ["ids de las reglas conductuales de tu perfil que aplicaste, p. ej. B-07"],
  "sin_cobertura": ["lo que tu perfil no cubre, si aplica"]
}"""

ESQUEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["primera_impresion", "que_miras_primero", "interpretacion", "pensamiento", "intencion", "accion", "marca",
                 "escribir", "progreso", "confianza", "friccion", "reglas", "sin_cobertura"],
    "properties": {
        **{k: {"type": "string"} for k in ("primera_impresion", "que_miras_primero", "interpretacion", "pensamiento",
                                             "intencion", "escribir")},
        "accion": {"type": "object", "additionalProperties": False, "required": ["opcion", "texto"],
                   "properties": {"opcion": {"type": "string", "enum": ACCIONES}, "texto": {"type": "string"}}},
        "marca": {"type": "integer", "minimum": 0},
        "progreso": {"type": "object", "additionalProperties": False, "required": ["opcion", "texto"],
                     "properties": {"opcion": {"type": "string", "enum": ["si", "mas_o_menos", "no"]}, "texto": {"type": "string"}}},
        "confianza": {"type": "integer", "minimum": 0, "maximum": 100},
        "friccion": {"type": "integer", "minimum": 0, "maximum": 5},
        "reglas": {"type": "array", "items": {"type": "string"}},
        "sin_cobertura": {"type": "array", "items": {"type": "string"}},
    },
}

FORMATO = 'Responde con este formato, en primera persona; en "accion" elige una sola opción y explica en "texto":'

# Esfuerzo percibido al cerrar la tarea (Customer Effort Score, ver [[metricas-ux]]). Es [SIMULACIÓN] actitudinal:
# se reporta junto a la tasa de éxito, nunca sola.
ESQUEMA_CES = {"type": "object", "additionalProperties": False, "required": ["ces", "texto"],
               "properties": {"ces": {"type": "integer", "minimum": 1, "maximum": 7}, "texto": {"type": "string"}}}
# Pregunta de cierre de una tarea (`pregunta_cierre` en estudio.yaml): al llegar al fin, el perfil mira esa última
# pantalla y contesta sin actuar. Sirve cuando el prototipo no deja seguir (p. ej. una rama sin conectar).
ESQUEMA_CIERRE = {"type": "object", "additionalProperties": False, "required": ["respuesta", "por_que", "confianza"],
                  "properties": {"respuesta": {"type": "string"}, "por_que": {"type": "string"},
                                 "confianza": {"type": "integer", "minimum": 0, "maximum": 100}}}
RETOMA_TEXTO = r"contin[uú]a tu solicitud|retoma|sigue (con|donde)|guardamos tu (avance|progreso)|vuelve a donde"


def _pantalla_id(material: str, url: str, estado: str | None = None) -> str:
    """Figma: node-id. Web: el estado que declara la app (`pantalla` en estudio.yaml) o, si no hay, la URL."""
    if material == "figma":
        return node_id(url) or "?"
    if estado:
        return estado
    from urllib.parse import urlparse

    u = urlparse(url)
    return ((u.netloc + u.path).rstrip("/") + (f"#{u.fragment}" if u.fragment else "")) or url


def _fin_alcanzado(fin: dict | None, info: dict, material: str) -> bool:
    if not fin:
        return False
    ids = list(fin.get("node_ids") or []) + list(fin.get("pantallas") or [])
    if ids and _pantalla_id(material, info["url"], info.get("estado")) in {str(x).replace(":", "-") for x in ids}:
        return True
    if fin.get("url_contiene") and fin["url_contiene"] in info["url"]:
        return True
    if fin.get("texto_visible") and fin["texto_visible"].lower() in (info.get("texto") or "").lower():
        return True
    return False


def _lista_zonas(material: str, zonas: list[dict]) -> str:
    if material == "figma":
        return ""
    lin = []
    for i, z in enumerate(zonas, 1):
        extra = []
        if z.get("tipo_input") == "range":
            extra.append(f"deslizador de {z.get('min')} a {z.get('max')}, ahora en {z.get('valor')}: para moverlo usa «escribir» "
                         "con el valor que quieres")
        elif z["editable"]:
            extra.append("se puede escribir" + (f"; ahora dice «{z['valor']}»" if z.get("valor") else ""))
        if z.get("marcado"):
            extra.append("seleccionado")
        if z.get("desactivado"):
            extra.append("desactivado")
        lin.append(f"{i}. {z.get('rol') or z['tipo']}{' (' + '; '.join(extra) + ')' if extra else ''}: «{z['etiqueta'] or 'sin texto'}»")
    return "Elementos marcados:\n" + "\n".join(lin) + "\n\n"


def _overlay(it, tarea, paso, p) -> str:
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    return ('<div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#C7F284">Sesión sintética · simulación</div>'
            f'<div style="font-size:16px;font-weight:700;margin-top:4px">{esc(it.nombre)}</div>'
            f'<div style="font-size:12px;opacity:.8">{esc(it.segmento)} · {esc(tarea["id"])} · paso {paso}</div>'
            f'<div style="margin-top:8px;padding:8px;border-radius:8px;background:rgba(255,255,255,.08)">«{esc(p.get("pensamiento", ""))}»</div>'
            f'<div style="margin-top:6px;font-size:12px">→ {esc(p.get("accion", {}).get("opcion", ""))} · confianza {p.get("confianza", "")} · fricción {p.get("friccion", "")}</div>'
            '<div style="margin-top:6px;font-size:10px;opacity:.6">Ruta y toques reales. Pensamiento y ritmo simulados.</div>')


def _subtitulo(it, tarea, paso, p) -> str:
    """Subtítulos de la ventana en vivo (web). La persona usuaria del arnés los ve; el perfil no: las capturas los ocultan."""
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    acc = (p.get("accion") or {}).get("opcion", "")
    return ('<div style="font-size:10px;letter-spacing:.08em;color:#C7F284">SESIÓN SINTÉTICA · SIMULACIÓN</div>'
            f'<b>{esc(it.nombre)}</b> · {esc(tarea["id"])} · paso {paso}<br>«{esc(p.get("pensamiento", ""))}»'
            f'<div style="opacity:.8;font-size:12px">→ {esc(acc)} · confianza {p.get("confianza", "")} · fricción {p.get("friccion", "")}</div>')


def _ruta_hasta(c: dict, tarea: dict) -> dict | None:
    """Acción mecánica que lleva la app al punto de partida de la tarea: los pasos de `ruta_mecanica` hasta ver la
    pantalla `inicia_en`. La ejecuta el arnés, no el perfil, y no cuenta en las métricas de la tarea."""
    if not tarea.get("inicia_en"):
        return None
    return {"tipo": "mecanico", "pasos": c.get("ruta_mecanica") or [], "hasta": tarea["inicia_en"]}


def simular(e: Estudio, integrante: str, tarea: str | None = None, corridas: int | None = None) -> dict:
    """Cuántas sesiones correría y cuántos tokens se esperan, sin abrir el navegador ni llamar al modelo.
    Los pasos por sesión salen de `pasos_esperados` de la tarea (p. ej. del recorrido mecánico) o, si falta,
    de `max_pasos` (techo: sobreestima)."""
    c = e.cfg
    ids = [it.id for it in e.panel()] if integrante == "todos" else [integrante]
    tareas = [t for t in c["tareas"] if not tarea or t["id"] == tarea]
    ncorr = corridas or c.get("corridas", 1)
    tot, filas = consumo.sumar(), []
    for t in tareas:
        pasos = int(t.get("pasos_esperados") or t.get("max_pasos") or c.get("max_pasos", 25))
        n = len(ids) * ncorr
        est = consumo.estimar_recorrido(pasos, n, captura=_captura_estimada(c), memoria=c.get("memoria", "completa"),
                                       capturas_por_paso=c.get("capturas_por_paso", 1 if c.get("memoria") == "bitacora" else 2))
        tot = consumo.sumar(tot, est)
        filas.append((t["id"], n, pasos, "pasos_esperados" if t.get("pasos_esperados") else "max_pasos (techo)", est))
    print(f"{len(ids)} perfil(es) × {ncorr} corrida(s):")
    for tid, n, pasos, origen, est in filas:
        print(f"  {tid}: {n} sesiones × ≈ {pasos} pasos ({origen}) → ≈ {consumo.texto(est)}")
    print(f"Total estimado: ≈ {consumo.texto(tot)} · modelo de consumo en arnes/consumo.py [SUPUESTO]")
    return tot


def sesion(e: Estudio, integrante: str, tarea: str | None = None, guion: bool = False, corridas: int | None = None,
           sala=None) -> list[dict]:
    c = e.cfg
    panel = {it.id: it for it in e.panel()}
    propia = sala is None and c.get("visible", True) and c.get("observacion", True)
    if propia:
        # sala de observación: página local con lo que piensa y decide cada perfil (arnes/observacion.py)
        from ..observacion import Sala

        sala = Sala(e.dir, titulo=(c.get("titulo") or e.dir.name) + ("" if integrante == "todos" else f" · {integrante}"))
        print(f"Sala de observación: {sala.abrir()}")
    try:
        if integrante == "todos":
            out = []
            for iid in panel:
                out += sesion(e, iid, tarea, guion, corridas, sala=sala)
            return out
        return _sesiones(e, panel, integrante, tarea, guion, corridas, sala)
    finally:
        if propia:
            sala.aviso("La corrida terminó. Esta página deja de actualizarse.")
            time.sleep(1.5)
            sala.cerrar()


def _sesiones(e, panel, integrante, tarea, guion, corridas, sala) -> list[dict]:
    c = e.cfg
    ncorr = corridas or c.get("corridas", 1)
    it = panel[integrante]
    tareas = [t for t in c["tareas"] if not tarea or t["id"] == tarea]
    material = c["material"]
    disp = c.get("dispositivo", {})
    # una sesión del navegador por perfil: varios perfiles pueden correr a la vez en procesos separados
    nav = Navegador(f'{c.get("sesion_navegador", "arnes")}-{integrante}', material, e.ruta("datos", "navegador"),
                    (disp.get("ancho", 360), disp.get("alto", 800)) if material == "web" else None,
                    emular=disp.get("emular"), pantalla=c.get("pantalla"))
    modelo = c.get("modelo", "sonnet")
    sistema = it.system_prompt(c.get("reglas_sesion", REGLAS_SESION))
    datos = "\n".join(f"- {k}: {v}" for k, v in (c.get("datos_prueba") or {}).items()) or "(ninguno)"
    registros = []
    abierto = False
    for t, n in [(t, n) for t in tareas for n in range(1, ncorr + 1)]:
        sid = f"{t['id']}-{it.id}{'-guion' if guion else ''}" + (f"-{n}" if ncorr > 1 else "")
        dst = e.sesiones_dir / f"{sid}.json"
        if dst.exists():
            print(f"ya existe {sid}; bórralo para repetir")
            registros.append(json.loads(dst.read_text(encoding="utf-8")))
            continue
        cap = e.ruta("datos", "capturas", sid)
        cap.mkdir(parents=True, exist_ok=True)
        url = t.get("url") or c["url"]
        if not abierto:
            nav.abrir(url, visible=c.get("visible", True))
            abierto = True
            for a in c.get("preparacion", []):  # p. ej. descartar cookies antes de medir nada
                nav.paso(cap / "prep.png", a)
        elif material == "web" and c.get("limpiar_datos", False):
            pass                                  # se limpia abajo, junto con la ruta mecánica
        elif c.get("reiniciar_entre_tareas", True) or n > 1:
            nav.paso(cap / "prep.png", {"tipo": "ir", "url": url})
        if material == "web" and c.get("limpiar_datos", False):
            # cada sesión empieza como alguien que nunca abrió la app: sin almacenamiento local ni solicitud guardada
            nav.paso(cap / "prep.png", {"tipo": "limpiar_datos", "url": url})
        ruta = _ruta_hasta(c, t)
        if ruta:
            if sala:
                sala.aviso(f"Preparando {t['id']}: el arnés lleva la app hasta «{t['inicia_en']}» (no cuenta en las métricas).")
            pre = nav.paso(cap / "prep.png", ruta, max_ms=60000)
            if _pantalla_id(material, pre["url"], pre.get("estado")) != t["inicia_en"]:
                raise RuntimeError(f"La ruta mecánica no llegó a «{t['inicia_en']}» (quedó en «{pre.get('estado')}»; "
                                   f"{pre.get('error_accion') or 'sin error'}). Revisa `ruta_mecanica` antes de gastar tokens.")
            if sala:
                sala.aviso("")
        if material == "figma":
            # esperar a que el prototipo termine de cargar y dibujarse (al abrir y al recargar entre tareas; con
            # hide-ui=1 tarda más): hasta ver zonas tocables, máximo ≈ 30 s
            for _ in range(10):
                if nav.paso(cap / "prep.png").get("zonas"):
                    break
                time.sleep(2)
        if c.get("video", True):
            e.ruta("datos", "videos").mkdir(parents=True, exist_ok=True)
            nav.video(True, str(e.ruta("datos", "videos", f"{sid}.webm")))
        reg = dict(id=sid, tarea=t["id"], corrida=n, integrante=it.id, nombre=it.nombre, perfil=it.perfil, segmento=it.segmento,
                   ocean=it.ocean, modo="guion" if guion else "autonomo", material=material, modelo=modelo,
                   inicio=time.strftime("%Y-%m-%dT%H:%M:%S"), pasos=[], costo_usd=0.0, tokens=consumo.sumar())
        if sala:
            pasos_est = int(t.get("pasos_esperados") or t.get("max_pasos") or c.get("max_pasos", 25))
            sala.iniciar_sesion(reg, t, t.get("max_pasos", c.get("max_pasos", 25)), consumo.total(consumo.estimar_recorrido(
                pasos_est, 1, captura=_captura_estimada(c), memoria=c.get("memoria", "completa"),
                capturas_por_paso=c.get("capturas_por_paso", 1 if c.get("memoria") == "bitacora" else 2))))
        try:
            if guion:
                _guion(e, nav, it, t, cap, reg)
            else:
                _autonomo(e, nav, it, t, cap, reg, sistema, datos, modelo, sala)
        finally:
            if c.get("video", True):
                nav.video(False)
                reg["video"] = f"datos/videos/{sid}.webm"
            reg["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            reg["costo_usd"] = round(reg["costo_usd"], 4)
            e.sesiones_dir.mkdir(parents=True, exist_ok=True)
            reg = limpiar(reg)   # sin correos, CURP ni tarjetas en lo que se guarda (arnes/guardia.py)
            dst.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
            with open(e.ruta("datos", "registro-sesiones.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(id=sid, ok=True, costo_usd=reg["costo_usd"], tokens=reg["tokens"], resultado=reg.get("resultado"),
                                        t=reg["fin"]), ensure_ascii=False) + "\n")
        if sala:
            sala.cerrar_sesion(reg, consumo.total(reg["tokens"]))
        print(f"{sid}: {reg.get('resultado')} en {len(reg['pasos'])} pasos · {consumo.texto(reg['tokens'])}")
        registros.append(reg)
    if abierto and c.get("cerrar_al_terminar", True):
        nav.cerrar()
    e.marcar("sesiones", ultima=registros[-1]["id"] if registros else None)
    return registros


def _captura_estimada(c: dict) -> tuple[int, int]:
    """Tamaño de la captura que verá el perfil, para estimar tokens: el teléfono recortado (Figma) o el viewport."""
    d = c.get("dispositivo") or {}
    if c.get("material") == "web":
        return (d.get("ancho", 412), d.get("alto", 839))
    return consumo.CAPTURA_TELEFONO


def _autonomo(e, nav, it, t, cap, reg, sistema, datos, modelo, sala=None):
    _bucle(e, nav, it, t, cap, reg, sistema, datos, modelo, sala)
    ses = reg.pop("_ses", None)
    bit = reg.pop("_bitacora", None)
    if (ses or bit) and reg.get("resultado") not in ("fallo_max_pasos", "fallo_instrumento"):
        pregunta = ("La sesión terminó. Pensando en todo lo que hiciste para esta tarea, ¿qué tan fácil o difícil te resultó? "
                    "Responde en JSON: «ces» de 1 (muy difícil) a 7 (muy fácil) y «texto» con una frase de por qué.")
        if bit:
            pregunta = _recuerdo(t, datos, bit) + pregunta
        r = motor.llamar(motor.Llamada(f"{reg['id']}-ces", pregunta, sistema, ESQUEMA_CES, [], [], reanudar=ses,
                                       modelo=modelo, persistir=bool(ses)))
        reg["ces"] = r.salida
        reg["costo_usd"] += r.costo_usd
        reg["tokens"] = consumo.sumar(reg["tokens"], r.tokens)


def _recuerdo(t: dict, datos: str, bitacora: list[str], ultimos: int = 40) -> str:
    """Modo bitácora: lo que el perfil sabe al empezar cada llamada (escenario, tarea, datos y su propio recorrido)."""
    s = (f"{' '.join(t.get('escenario', '').split())}\n\nTu tarea: {' '.join(t['instruccion'].split())}\n\n"
         f"Datos de prueba (ficticios) por si el producto te los pide:\n{datos}\n\n")
    if bitacora:
        omit = len(bitacora) - ultimos
        s += ("Lo que llevas hecho en esta tarea (tu memoria, en tus palabras):\n" + ("(…pasos anteriores…)\n" if omit > 0 else "")
              + "\n".join(bitacora[-ultimos:]) + "\n\n")
    return s


def _linea(n, pid, p, desc, resultado, avisos=(), pestana=None) -> str:
    extra = (f" Apareció y se fue un aviso: {' · '.join(f'«{a}»' for a in avisos)}." if avisos else "")
    extra += (f" Se abrió una pestaña con «{pestana.get('titulo')}» y volviste." if pestana else "")
    return (f"- Paso {n} ({pid}): pensaste «{p.get('pensamiento', '')}»; {desc}: {resultado}.{extra} "
            f"Confianza {p.get('confianza')}, fricción {p.get('friccion')}.")


def _recortar(material, info, png, marcas) -> list[int] | None:
    """Figma: el perfil ve solo el teléfono, como en su celular, y no la ventana de Figma ni la burbuja del arnés.
    Las coordenadas de zonas y toques siguen siendo de la página; `recorte` es el origen para dibujarlas encima."""
    if material != "figma" or not info.get("marco") or info.get("marco") == info.get("lienzo"):
        return None
    o = recortar(png, info["marco"])
    recortar(marcas, info["marco"])
    return o


def _senales(info) -> dict:
    t = info.get("texto") or ""
    return dict(campos=info.get("campos"), progreso_visible=info.get("progreso"), errores_visibles=info.get("errores_validacion") or [],
                permisos=info.get("permisos") or [], host=info.get("host"), paginas=info.get("paginas"),
                palabras=len(t.split()) if t else None)


def _bucle(e, nav, it, t, cap, reg, sistema, datos, modelo, sala=None):
    c = e.cfg
    material = c["material"]
    actual = cap / "siguiente.png"  # captura de la pantalla que el perfil va a ver en el próximo paso
    info = nav.paso(actual, instrumentar=True)
    texto_inicio = info.get("texto")
    retoma = t.get("retoma")
    ses, aviso, quietos = None, "", 0
    ligero, bitacora = c.get("memoria") == "bitacora", []
    friccion_max, sin_resp = 0, 0
    for n in range(1, t.get("max_pasos", c.get("max_pasos", 25)) + 1):
        png, marcas = cap / f"p{n:02d}.png", cap / f"p{n:02d}-marcas.png"
        actual.replace(png)
        zonas = info.get("zonas", [])
        marcar(png, zonas, marcas)
        recorte = _recortar(material, info, png, marcas)
        pid = _pantalla_id(material, info["url"], info.get("estado"))
        if _fin_alcanzado(t.get("fin"), info, material):
            reg["resultado"] = "exito" if friccion_max < 3 and not sin_resp else "exito_con_friccion"
            reg["pasos"].append(dict(n=n, pantalla=pid, url=info["url"], captura=str(png.relative_to(e.dir)), fin=True))
            if t.get("pregunta_cierre") and (ses or bitacora):
                cola = (f"Aquí termina la tarea; no toques nada. {' '.join(t['pregunta_cierre'].split())} Responde en JSON: "
                        "«respuesta» (qué harías o contestarías), «por_que» (en tus palabras) y «confianza» de 0 a 100.")
                if ligero:
                    ll = motor.Llamada(f"{reg['id']}-cierre", _recuerdo(t, datos, bitacora) + "Llegaste a la pantalla de la imagen. "
                                       + cola, sistema, ESQUEMA_CIERRE, modelo=modelo, imagenes=[png])
                else:
                    ll = motor.Llamada(f"{reg['id']}-cierre", f"Llegaste a esta pantalla: `{png.name}` (ábrela con Read). " + cola,
                                       sistema, ESQUEMA_CIERRE, ["Read"], [png], reanudar=ses, modelo=modelo, persistir=True)
                r = motor.llamar(ll)
                reg["cierre"] = dict(pregunta=t["pregunta_cierre"], **(r.salida or {}))
                reg["costo_usd"] += r.costo_usd
                reg["tokens"] = consumo.sumar(reg["tokens"], r.tokens)
            return
        if material == "figma" and not zonas:
            # sin zonas el perfil no puede tocar nada: se detecta otra vez y, si sigue en 0, se detiene ANTES de
            # llamar al modelo. Un abandono así sería del instrumento, no del producto (piloto de OU 2.0).
            info = nav.paso(png)
            zonas = info.get("zonas", [])
            marcar(png, zonas, marcas)
            recorte = _recortar(material, info, png, marcas)
            if not zonas:
                reg["resultado"] = "fallo_instrumento"
                reg["nota_instrumento"] = (f"Paso {n}: 0 zonas tocables en dos detecciones seguidas ({info.get('deteccion')}). "
                                           "Revisar la captura antes de interpretar nada.")
                reg["pasos"].append(dict(n=n, pantalla=pid, url=info["url"], captura=str(png.relative_to(e.dir)),
                                         sin_zonas=True))
                print(f"  ! {reg['nota_instrumento']}")
                return
        if ligero:
            # modo ligero: llamada nueva por paso con la bitácora de lo hecho y solo la pantalla actual, dentro del mensaje.
            # El costo crece lineal con los pasos, no con su cuadrado. [SUPUESTO METODOLÓGICO] (validar contra el modo completo)
            una = c.get("capturas_por_paso", 1) == 1
            prompt = (f"{_recuerdo(t, datos, bitacora)}{aviso}Paso {n}. "
                      + (f"La imagen es la pantalla actual, como la ves en tu celular, con números sobre los {len(zonas)} elementos "
                         "que responden al toque (en tu celular no los ves; úsalos solo para indicar dónde actúas).\n\n" if una else
                         f"La primera imagen es la pantalla actual, como la ves en tu celular; la segunda es la misma con números sobre "
                         f"los {len(zonas)} elementos que responden al toque. Usa la numerada solo para indicar dónde actúas.\n\n")
                      + f"{_lista_zonas(material, zonas)}{FORMATO}\n\n{PLANTILLA}")
            ll = motor.Llamada(f"{reg['id']}-p{n}", prompt, sistema, ESQUEMA, modelo=modelo, imagenes=[marcas] if una else [png, marcas])
        else:
            intro = ""
            if n == 1:
                intro = (f"{' '.join(t.get('escenario', '').split())}\n\nTu tarea: {' '.join(t['instruccion'].split())}\n\n"
                         f"Datos de prueba (ficticios) por si el producto te los pide:\n{datos}\n\n")
            prompt = (f"{intro}{aviso}Paso {n}. La pantalla actual es `{png.name}`: ábrela con Read y mírala como la verías en tu "
                      f"celular. En `{marcas.name}` está la misma pantalla con números sobre los {len(zonas)} elementos que responden "
                      f"al toque. Mira primero la limpia; usa la marcada solo para indicar dónde actúas.\n\n"
                      f"{_lista_zonas(material, zonas)}{FORMATO}\n\n{PLANTILLA}")
            ll = motor.Llamada(f"{reg['id']}-p{n}", prompt, sistema, ESQUEMA, ["Read"], [png, marcas],
                               reanudar=ses, modelo=modelo, persistir=True)
        if sala:
            sala.pantalla(n, pid, png, len(zonas))
        r = motor.llamar(ll)
        if ligero:
            reg["_bitacora"] = bitacora
        else:
            ses = r.session_id
            reg["_ses"] = ses
        reg["costo_usd"] += r.costo_usd
        reg["tokens"] = consumo.sumar(reg["tokens"], r.tokens)
        p = r.salida
        op = p["accion"]["opcion"]
        friccion_max = max(friccion_max, p["friccion"])
        paso = dict(n=n, pantalla=pid, url=info["url"], captura=str(png.relative_to(e.dir)),
                    marcas=str(marcas.relative_to(e.dir)), zonas=len(zonas), perfil=p, modelo_id=r.modelo_id,
                    zonas_detalle=[{k: z[k] for k in ("x", "y", "w", "h", "tipo", "etiqueta")} for z in zonas],
                    texto_pantalla=info.get("texto") or None,
                    marco=info.get("marco"), recorte=recorte, **_senales(info))
        if op in ("abandonar", "terminar"):
            fin = _fin_alcanzado(t.get("fin"), info, material)
            reg["resultado"] = "abandono" if op == "abandonar" else ("exito" if fin else "falso_exito" if t.get("fin") else "terminado_sin_criterio")
            reg["pasos"].append(paso)
            return
        accion, desc = _traducir(op, p, zonas, info, material)
        paso["accion"] = accion
        if sala:
            sala.decision(n, p, [accion["x"], accion["y"]] if accion and "x" in accion and accion["tipo"] != "desplazar" else None,
                          consumo.total(reg["tokens"]), recorte)
        if c.get("video", True) and material == "web":
            nav.capitulo(f"{it.nombre} · {t['id']} · paso {n} · {op}")
        m = p.get("marca", 0)
        if accion and accion["tipo"] in ("tocar", "escribir") and 0 < m <= len(zonas):
            paso["zona_tocada"] = {k: zonas[m - 1][k] for k in ("x", "y", "w", "h", "tipo", "etiqueta")}
        if accion is None:
            paso["respuesta"] = "fuera_de_marcas"
            aviso = f"Resultado del paso anterior: {desc}\n\n"
            bitacora.append(_linea(n, pid, p, desc, "no pasó nada"))
            reg["pasos"].append(paso)
            quietos += 1
            info = nav.paso(actual)
            if sala:
                sala.resultado_paso(n, "fuera_de_marcas", None, pid)
        else:
            antes = info
            sub = (_overlay if material == "figma" else _subtitulo)(it, t, n, p) if c.get("video", True) else None
            info = nav.paso(actual, accion, overlay=sub)
            if material == "web":
                cambio = bool(info["cambio_url"] or info.get("cambio_estado") or info.get("cambio_firma") or info.get("cambio_imagen")
                              or info.get("pestana_nueva"))
                if info.get("error_accion"):
                    paso["error_accion"] = info["error_accion"]
            else:
                cambio = info["cambio_url"] or info.get("cambio_telefono", info["cambio_imagen"])
            paso["espera_ms"] = info.get("espera_ms")
            if info.get("reintento"):
                paso["reintento"] = True   # el primer toque no respondió y se repitió una vez [SUPUESTO METODOLÓGICO]
            paso["host_despues"], paso["paginas_despues"] = info.get("host"), info.get("paginas")
            nuevos = sorted(set(info.get("errores_validacion") or []) - set(antes.get("errores_validacion") or []))
            if nuevos:
                paso["validacion_disparada"] = nuevos
            paso["respuesta"] = "si" if cambio else "no"
            paso["pantalla_despues"] = _pantalla_id(material, info["url"], info.get("estado"))
            if info.get("vio_carga"):
                paso["indicador_carga"] = True
            if sala:
                sala.resultado_paso(n, paso["respuesta"], info.get("espera_ms"), paso["pantalla_despues"])
            if accion["tipo"] in ("tocar", "escribir") and not cambio:
                sin_resp += 1
            quietos = 0 if cambio else quietos + 1
            aviso = f"Resultado del paso anterior: {desc}: {'la pantalla cambió' if cambio else 'no pasó nada visible'}.\n\n"
            if info.get("pestana_nueva"):
                pn = info["pestana_nueva"]
                paso["pestana_nueva"] = pn
                aviso = (f"Resultado del paso anterior: {desc}: se abrió una pestaña nueva del navegador con «{pn.get('titulo') or 'sin título'}» "
                         f"({pn.get('url')}). La miraste, la cerraste y volviste a la app, que sigue donde estabas.\n\n")
            if info.get("avisos_nuevos"):
                paso["avisos"] = info["avisos_nuevos"]
            if info.get("avisos_idos"):
                # el aviso apareció y se fue mientras el perfil «pensaba»: una persona lo habría visto [SUPUESTO METODOLÓGICO]
                aviso += ("Mientras tanto apareció un aviso en tu pantalla que ya se quitó: "
                          + " · ".join(f"«{x}»" for x in info["avisos_idos"]) + "\n\n")
            reg["pasos"].append(paso)
            bitacora.append(_linea(n, pid, p, desc, "la pantalla cambió" if cambio else "no pasó nada visible",
                                   info.get("avisos_idos") or [], info.get("pestana_nueva")))
            if retoma and n == retoma.get("tras_paso") and "retoma" not in reg:
                info, nota = _interrumpir(e, nav, actual, t, info, texto_inicio, retoma, reg, material)
                aviso += nota
                bitacora.append(f"(después del paso {n} saliste de la app y volviste a entrar)")
        if quietos >= c.get("max_sin_cambio", 4):
            reg["resultado"] = "atascado"
            return
    if _fin_alcanzado(t.get("fin"), info, material):
        # el último paso permitido llevó al fin: llegó, aunque ya no haya otro paso para verlo
        reg["resultado"] = "exito" if friccion_max < 3 and not sin_resp else "exito_con_friccion"
        reg["pasos"].append(dict(n=len(reg["pasos"]) + 1, pantalla=_pantalla_id(material, info["url"], info.get("estado")),
                                 url=info["url"], fin=True))
        return
    reg["resultado"] = "fallo_max_pasos"


def _interrumpir(e, nav, actual, t, info, texto_inicio, retoma, reg, material):
    """Retoma de solicitud: sale del flujo y vuelve a entrar. «recargar» = recarga la página (misma sesión del
    navegador); «reabrir» = vuelve a entrar por la URL de inicio. Compara lo que ve después con lo que veía antes."""
    import re

    antes_pid, antes_txt = _pantalla_id(material, info["url"], info.get("estado")), info.get("texto")
    modo = retoma.get("modo", "recargar")
    accion = {"tipo": "recargar"} if modo == "recargar" else {"tipo": "ir", "url": t.get("url") or e.cfg["url"]}
    nuevo = nav.paso(actual, accion)
    pid, txt = _pantalla_id(material, nuevo["url"], nuevo.get("estado")), nuevo.get("texto")
    if material == "web" and nuevo.get("estado") and info.get("estado"):
        conserva, reinicia = pid == antes_pid, pid == e.cfg.get("pantalla_inicio")
    elif material == "web" and antes_txt is not None:
        conserva = txt == antes_txt
        reinicia = txt == texto_inicio
    else:
        conserva, reinicia = pid == antes_pid, False
    if conserva:
        res = "conserva_el_avance"
    elif re.search(RETOMA_TEXTO, txt or "", re.I):
        res = "ofrece_retomar"
    elif reinicia:
        res = "vuelve_al_inicio"
    else:
        res = "otra_pantalla"
    reg["retoma"] = dict(tras_paso=retoma.get("tras_paso"), modo=modo, pantalla_antes=antes_pid, pantalla_despues=pid,
                         resultado=res)
    return nuevo, ("Saliste del proceso (cerraste la página) y volviste a entrar más tarde. "
                   "La pantalla que ves ahora es la que te mostró al volver.\n\n")


def _traducir(op, p, zonas, info, material):
    m = p.get("marca", 0)
    z = zonas[m - 1] if 0 < m <= len(zonas) else None
    marco = info.get("marco") or {"x": 0, "y": 0, "w": 360, "h": 800}
    # deslizar donde va el pulgar (62 % de la altura): al centro caía en el encabezado de las hojas inferiores
    centro = (marco["x"] + marco["w"] // 2, marco["y"] + round(marco["h"] * (0.62 if material == "web" else 0.5)))
    if op in ("tocar", "escribir"):
        if not z:
            return None, f"quisiste {op} algo que no está entre los elementos que responden ({p.get('intencion', '')})"
        if op == "escribir" and material == "web" and z.get("tipo_input") == "range":
            # deslizador: se toca el punto de la barra que corresponde al valor pedido
            import re

            num = re.sub(r"[^0-9.]", "", p.get("escribir", "") or "")
            if num:
                lo, hi = float(z.get("min", 0)), float(z.get("max", 100))
                f = min(1.0, max(0.0, (float(num) - lo) / ((hi - lo) or 1)))
                margen = min(12, z["w"] // 10)
                return (dict(tipo="tocar", x=round(z["x"] + margen + f * (z["w"] - 2 * margen)), y=z["tocar"][1]),
                        f"moviste el deslizador {m} hacia {p.get('escribir')}")
        if op == "escribir" and material == "web" and z["editable"]:
            return dict(tipo="escribir", x=z["tocar"][0], y=z["tocar"][1], texto=p.get("escribir", "")), f"escribiste en el {m}"
        return dict(tipo="tocar", x=z["tocar"][0], y=z["tocar"][1]), f"tocaste el {m}"
    if op.startswith("desplazar"):
        return dict(tipo="desplazar", x=centro[0], y=centro[1], dy=500 if op.endswith("abajo") else -500), f"desplazaste hacia {op.split('_')[1]}"
    if op == "volver":
        if material == "web":
            return dict(tipo="volver"), "volviste atrás con el navegador"
        return None, "este prototipo no tiene botón de atrás del navegador; si hay uno en la pantalla, tócalo"
    return dict(tipo="esperar", ms=5000), "esperaste unos segundos"


def _guion(e, nav, it, t, cap, reg):
    """Guion en estudio.yaml: guiones.<integrante>.<tarea> = [{pantalla, dice, etiqueta, acciones: [[tipo, ...]]}]."""
    pasos = e.cfg["guiones"][it.id][t["id"]]
    info = nav.paso(cap / "p00.png")
    for n, s in enumerate(pasos, 1):
        for k, a in enumerate(s["acciones"]):
            tipo = a[0]
            acc = {"tocar": lambda a: dict(tipo="tocar", x=a[1], y=a[2]),
                   "desplazar": lambda a: dict(tipo="desplazar", x=info["marco"]["x"] + info["marco"]["w"] // 2,
                                               y=info["marco"]["y"] + info["marco"]["h"] // 2, dy=a[1]),
                   "arrastrar": lambda a: dict(tipo="arrastrar", x=a[1], y=a[2], x2=a[3], y2=a[4]),
                   "tecla": lambda a: dict(tipo="tecla", tecla=a[1]),
                   "observar": lambda a: None}[tipo](a)
            antes = info["url"]
            p = dict(pensamiento=s.get("dice", ""), accion={"opcion": tipo}, confianza="", friccion="")
            info = nav.paso(cap / f"p{n:02d}-{k}.png", acc, overlay=_overlay(it, t, n, p), pausa_ms=a[1] if tipo == "observar" else 1200)
            reg["pasos"].append(dict(n=n, pantalla=s.get("pantalla"), dice=s.get("dice"), etiqueta=s.get("etiqueta"),
                                     accion=acc, intencion=a[-1] if isinstance(a[-1], str) else "",
                                     respuesta="si" if (info["cambio_url"] or info["cambio_imagen"]) else "no",
                                     pantalla_antes=_pantalla_id(e.cfg["material"], antes),
                                     pantalla_despues=_pantalla_id(e.cfg["material"], info["url"]),
                                     captura=str((cap / f"p{n:02d}-{k}.png").relative_to(e.dir))))
    reg["resultado"] = "guion_completo"


# ---------------------------------------------------------------------------------------------
# Análisis


def analizar(e: Estudio) -> dict:
    S = list(motor.cargar(e.sesiones_dir).values())
    filas, pasos = [], []
    orden_pant, alcanzo = [], collections.defaultdict(set)
    for s in S:
        ps = s["pasos"]
        perf = [p["perfil"] for p in ps if p.get("perfil")]
        conf = [x["confianza"] for x in perf]
        fr = [x["friccion"] for x in perf]
        for p in ps:
            if p.get("pantalla") and p["pantalla"] not in orden_pant:
                orden_pant.append(p["pantalla"])
            if p.get("pantalla"):
                alcanzo[p["pantalla"]].add(s["id"])
            x = p.get("perfil") or {}
            pasos.append([s["id"], s["tarea"], s["integrante"], p["n"], p.get("pantalla"), (x.get("accion") or {}).get("opcion", ""),
                          p.get("respuesta", ""), x.get("confianza", ""), x.get("friccion", ""), x.get("pensamiento", p.get("dice", "")),
                          x.get("intencion", ""), " ".join(x.get("reglas", [])), p.get("captura", "")])
        filas.append(dict(sesion=s["id"], tarea=s["tarea"], integrante=s["integrante"], nombre=s["nombre"],
                          resultado=s.get("resultado"), pasos=len(ps),
                          toques=sum(1 for p in ps if (p.get("accion") or {}).get("tipo") in ("tocar", "escribir")),
                          sin_respuesta=sum(1 for p in ps if p.get("respuesta") == "no"),
                          fuera_de_marcas=sum(1 for p in ps if p.get("respuesta") == "fuera_de_marcas"),
                          pantallas=len({p.get("pantalla") for p in ps}),
                          confianza_inicial=conf[0] if conf else "", confianza_final=conf[-1] if conf else "",
                          confianza_min=min(conf) if conf else "", friccion_max=max(fr) if fr else "",
                          tokens=consumo.total(s.get("tokens"))))
    with open(e.ruta("datos", "resumen-sesiones.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]) if filas else ["sesion"])
        w.writeheader()
        w.writerows(filas)
    with open(e.ruta("datos", "pasos.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["sesion", "tarea", "integrante", "paso", "pantalla", "accion", "respuesta", "confianza",
                                  "friccion", "pensamiento", "intencion", "reglas", "captura"]] + pasos)
    por_tarea = collections.defaultdict(collections.Counter)
    for x in filas:
        por_tarea[x["tarea"]][x["resultado"]] += 1
    # momentos candidatos: caída de confianza >= 15 o fricción >= 3 (para que el investigador los revise)
    momentos = []
    for s in S:
        prev = None
        for p in s["pasos"]:
            x = p.get("perfil")
            if not x:
                continue
            if (prev is not None and prev - x["confianza"] >= 15) or x["friccion"] >= 3:
                momentos.append(dict(sesion=s["id"], paso=p["n"], pantalla=p.get("pantalla"), confianza=x["confianza"],
                                     caida=(prev - x["confianza"]) if prev is not None else 0, friccion=x["friccion"],
                                     pensamiento=x["pensamiento"]))
            prev = x["confianza"]
    from .. import metricas

    extra = dict(wcag_258=tamano_objetivos(e, S), primer_toque=primer_toque(e, S), robustez=robustez_recorrido(S),
                 metricas=metricas.calcular(S, e.cfg))
    res = dict(n_sesiones=len(S), resultados={t: dict(v) for t, v in por_tarea.items()}, **extra,
               embudo=[dict(pantalla=p, sesiones=len(alcanzo[p])) for p in orden_pant], momentos=momentos, sesiones=filas)
    e.ruta("datos", "agregado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    _heatmaps_toques(e, S)
    e.marcar("analizar", sesiones=len(S))
    for t, v in res["resultados"].items():
        print(t, dict(v))
    print("embudo:", " → ".join(f"{x['pantalla']}({x['sesiones']})" for x in res["embudo"]))
    print(f"{len(momentos)} momentos candidatos (caída de confianza ≥ 15 o fricción ≥ 3)")
    w = res["wcag_258"]
    print(f"WCAG 2.5.8 · objetivos bajo 24×24 px sin espaciado suficiente: {sum(len(x['fallan']) for x in w)} en {len(w)} pantallas"
          + (" (Figma: medición aproximada, rejilla de 12 px)" if e.cfg["material"] == "figma" else ""))
    for t, v in res["primer_toque"].items():
        print(f"primer toque {t}: {v['correcto']} de {v['total']} correctos" + (f" · completan {v['completan_si_correcto']} vs {v['completan_si_incorrecto']}" if v["total"] else ""))
    for a in res["robustez"]["alertas"]:
        print("! " + a)
    for t, m in res["metricas"]["tareas"].items():
        md = lambda k: (m.get(k) or {}).get("mediana", "—")  # noqa: E731
        print(f"métricas {t}: pasos {md('pasos')} · clics {md('clics')} · campos {md('campos')} · tiempo estimado (completan) "
              f"{md('tiempo_completan_s')} s · espera del sistema {md('espera_sistema_s')} s · validaciones {md('validaciones_disparadas')} · "
              f"cambios de dominio {md('cambios_dominio')} · otros canales {m['menciones_otro_canal'] or '—'} · retoma {m['retoma'] or '—'} · "
              f"estatus visible {m['estatus']['con_indicador']} de {m['estatus']['pantallas']} pantallas · CES {md('ces')}")
    return res


COMPLETAN = ("exito", "exito_con_friccion")


def tamano_objetivos(e: Estudio, S: list[dict], minimo: int = 24) -> list[dict]:
    """WCAG 2.2 · 2.5.8 Target Size (Minimum), AA: 24×24 px CSS, o espaciado tal que un círculo de 24 px
    centrado en el objetivo no toque otro objetivo ni otro círculo. Excepciones que el arnés no puede
    ver (enlace dentro de un texto, tamaño determinado por el navegador, control esencial) se revisan a mano."""
    ancho = (e.cfg.get("dispositivo") or {}).get("ancho", 360)
    vistas = {}
    for s in S:
        for p in s["pasos"]:
            if p.get("zonas_detalle") is not None and p.get("pantalla") not in vistas:
                vistas[p["pantalla"]] = p
    out = []
    for pid, p in vistas.items():
        marco = p.get("marco") or {"w": ancho}
        esc = (marco["w"] / ancho) if e.cfg["material"] == "figma" and marco.get("w") else 1.0
        zs = [dict(z, cx=z["x"] + z["w"] / 2, cy=z["y"] + z["h"] / 2, wc=z["w"] / esc, hc=z["h"] / esc) for z in p["zonas_detalle"]]
        r = minimo / 2 * esc
        fallan = []
        for i, z in enumerate(zs):
            if z["wc"] >= minimo and z["hc"] >= minimo:
                continue
            choca = False
            for j, o in enumerate(zs):
                if i == j:
                    continue
                dx = max(o["x"] - z["cx"], 0, z["cx"] - (o["x"] + o["w"]))
                dy = max(o["y"] - z["cy"], 0, z["cy"] - (o["y"] + o["h"]))
                chica_o = o["wc"] < minimo or o["hc"] < minimo
                if (dx * dx + dy * dy) ** 0.5 < r or (chica_o and ((z["cx"] - o["cx"]) ** 2 + (z["cy"] - o["cy"]) ** 2) ** 0.5 < 2 * r):
                    choca = True
                    break
            if choca:
                fallan.append(dict(etiqueta=z.get("etiqueta") or "", tipo=z.get("tipo"), ancho_css=round(z["wc"]), alto_css=round(z["hc"]),
                                   caja=[z["x"], z["y"], z["w"], z["h"]]))
        out.append(dict(pantalla=pid, captura=p.get("captura"), objetivos=len(zs), fallan=fallan,
                        aproximado=e.cfg["material"] == "figma"))
    return out


def primer_toque(e: Estudio, S: list[dict]) -> dict:
    """First-click testing: si el primer clic es correcto, 87% completa; si no, 46% (Bailey y Wolfson, vía el vault)."""
    out = {}
    esperado = {t["id"]: t.get("primer_toque") for t in e.cfg.get("tareas", [])}
    for t, exp in esperado.items():
        if not exp:
            continue
        ok = mal = ok_c = mal_c = 0
        for s in S:
            if s["tarea"] != t:
                continue
            p = next((p for p in s["pasos"] if (p.get("accion") or {}).get("tipo") in ("tocar", "escribir")), None)
            if not p:
                continue
            z = p.get("zona_tocada") or {}
            a = p["accion"]
            if exp.get("etiqueta_contiene"):
                acierta = exp["etiqueta_contiene"].lower() in (z.get("etiqueta") or "").lower()
            elif exp.get("caja_telefono"):
                # caja relativa a la esquina del teléfono: no depende de dónde quede el teléfono en la ventana
                m = p.get("marco") or {"x": 0, "y": 0}
                x0, y0, x1, y1 = exp["caja_telefono"]
                acierta = x0 <= a["x"] - m["x"] <= x1 and y0 <= a["y"] - m["y"] <= y1
            else:
                x0, y0, x1, y1 = exp["caja"]
                acierta = x0 <= a["x"] <= x1 and y0 <= a["y"] <= y1
            completa = s.get("resultado") in COMPLETAN
            if acierta:
                ok += 1
                ok_c += completa
            else:
                mal += 1
                mal_c += completa
        out[t] = dict(correcto=ok, total=ok + mal, completan_si_correcto=f"{ok_c} de {ok}", completan_si_incorrecto=f"{mal_c} de {mal}")
    return out


def robustez_recorrido(S: list[dict]) -> dict:
    """¿Se repite el resultado entre corridas del mismo perfil? ¿Todos los perfiles siguen la misma ruta?"""
    import collections

    por = collections.defaultdict(list)
    rutas = collections.defaultdict(dict)
    for s in S:
        por[(s["tarea"], s["integrante"])].append(s.get("resultado"))
        rutas[s["tarea"]][s["id"]] = tuple(p.get("pantalla") for p in s["pasos"])
    rep = {f"{t}|{i}": v for (t, i), v in por.items() if len(v) > 1}
    estables = [k for k, v in rep.items() if len(set(v)) == 1]
    alertas = []
    if rep and len(estables) < len(rep):
        alertas.append(f"{len(rep) - len(estables)} de {len(rep)} perfil-tareas cambian de resultado entre corridas: "
                       "reportar solo lo que se repite")
    for t, d in rutas.items():
        if len(d) >= 3 and len(set(d.values())) == 1:
            alertas.append(f"{t}: todas las sesiones siguieron exactamente la misma ruta. Puede ser un flujo lineal o un panel "
                           "que no diferencia")
    return dict(repetidas=rep, estables=len(estables), con_repeticion=len(rep), alertas=alertas)


def slug(s: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")[:80]


def _heatmaps_toques(e: Estudio, S: list[dict]):
    """Toques reales agregados por pantalla sobre su primera captura. Verde: respondió. Rojo: sin respuesta."""
    from PIL import Image, ImageDraw

    por = collections.defaultdict(list)
    base, origen = {}, {}
    for s in S:
        for p in s["pasos"]:
            a = p.get("accion") or {}
            if p.get("pantalla") and p.get("captura") and p["pantalla"] not in base:
                base[p["pantalla"]] = e.ruta(p["captura"])
                origen[p["pantalla"]] = p.get("recorte") or [0, 0]
            if a.get("tipo") in ("tocar", "escribir"):
                por[p["pantalla"]].append((a["x"], a["y"], p.get("respuesta") == "si", s["integrante"]))
    for pid, toques in por.items():
        if pid not in base or not base[pid].exists():
            continue
        im = Image.open(base[pid]).convert("RGBA")
        capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        ox, oy = origen.get(pid) or [0, 0]
        for x, y, ok, _ in toques:
            x, y = x - ox, y - oy
            col = (34, 160, 90, 110) if ok else (210, 50, 40, 140)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col, outline=col[:3] + (255,), width=2)
        Image.alpha_composite(im, capa).convert("RGB").save(e.ruta("heatmaps", f"toques-{slug(pid)}.png"))


# ---------------------------------------------------------------------------------------------
# Ensayo sin modelo (0 tokens)

JS_CAJA = r"""async (page) => { const s = __S__;
  const l = s.selector ? page.locator(s.selector) : s.etiqueta ? page.getByLabel(s.etiqueta, { exact: !!s.exacto })
    : page.getByRole(s.rol || 'button', s.nombre ? { name: s.nombre, exact: !!s.exacto } : {});
  const el = s.ultimo ? l.last() : l.first();
  await el.waitFor({ state: 'visible', timeout: __ESPERA__ }).catch(() => {});
  return JSON.stringify(await el.boundingBox().catch(() => null)); }"""


def ensayar(e: Estudio, visible: bool = False) -> dict:
    """Recorre la `ruta_mecanica` como lo haría un perfil (elementos numerados, toque en su centro, escribir, desplazar),
    sin llamar al modelo. Encuentra antes de gastar tokens lo que en OU 2.0 MVP costó 5.6 M: objetivos que el perfil no
    puede tocar, tareas cuyo fin no se alcanza y datos que la ruta usa pero los datos de prueba no traen. Da los pasos
    mínimos por tarea (para `pasos_esperados` y la estimación de tokens)."""
    import re

    c = e.cfg
    if c.get("material") != "web" or not c.get("ruta_mecanica"):
        raise SystemExit("El ensayo necesita material web y `ruta_mecanica` en estudio.yaml.")
    disp = c.get("dispositivo") or {}
    d = e.ruta("datos", "ensayo")
    d.mkdir(parents=True, exist_ok=True)
    nav = Navegador("arnes-ensayo", "web", e.ruta("datos", "navegador"), (disp.get("ancho", 412), disp.get("alto", 839)),
                    emular=disp.get("emular"), pantalla=c.get("pantalla"))
    tareas = c.get("tareas", [])
    inicio = {t.get("inicia_en"): t["id"] for t in tareas if t.get("inicia_en")}
    fines = {t["id"]: {str(x) for x in (t.get("fin") or {}).get("pantallas") or (t.get("fin") or {}).get("node_ids") or []} for t in tareas}
    actual = tareas[0]["id"] if tareas and not tareas[0].get("inicia_en") else None
    conteo, problemas, avisos_datos = {t["id"]: 0 for t in tareas}, [], []
    seguidos = 0                                  # pasos seguidos sin encontrar el objetivo: la ruta se desvió
    datos_txt = " ".join(str(v) for v in (c.get("datos_prueba") or {}).values()).lower()
    norm = lambda x: re.sub(r"[^a-z0-9áéíóúñ]", "", str(x).lower())  # noqa: E731
    png = d / "paso.png"
    nav.abrir(c["url"], visible=visible)
    try:
        info = nav.paso(png, {"tipo": "limpiar_datos", "url": c["url"]}, instrumentar=True)
        for i, s in enumerate(c["ruta_mecanica"], 1):
            est = info.get("estado")
            if est in inicio:
                actual = inicio[est]
            dato = s.get("llenar", s.get("teclear"))
            if dato is not None and norm(dato) and norm(dato) not in norm(datos_txt):
                avisos_datos.append(f"paso {i} ({est}): la ruta escribe «{dato}» y los datos de prueba no lo traen")
            if s.get("rol") == "radio" and est not in ("producto", "simulador") and s.get("nombre") and norm(s["nombre"]) not in norm(datos_txt):
                avisos_datos.append(f"paso {i} ({est}): la ruta elige «{s['nombre']}»; si es un dato personal, ponlo en datos_prueba "
                                    "(un perfil que no inventa datos se detiene)")
            caja, zona = None, None
            for intento in range(4):              # si no lo ve, desliza (hasta 3 veces)
                espera = (s.get("timeout") or 15000) if intento == 0 else 1000   # tras desplazar, ya cargó
                caja = nav.ejecutar(JS_CAJA.replace("__S__", json.dumps(s)).replace("__ESPERA__", str(espera)))
                info = nav.paso(png, observar_ms=0)
                m = info.get("marco") or {"w": 412, "h": 839}
                if isinstance(caja, dict):          # la zona visible del objetivo (la que un perfil vería numerada)
                    zona = next((z for z in info.get("zonas", []) if caja["x"] <= z["tocar"][0] <= caja["x"] + caja["width"]
                                 and caja["y"] <= z["tocar"][1] <= caja["y"] + caja["height"]), None)
                if zona or intento == 3:
                    break
                # como un perfil: desliza de a poco, hacia arriba si el objetivo quedó arriba (una lista dentro de una hoja)
                arriba = isinstance(caja, dict) and caja["y"] + caja["height"] / 2 < m["h"] * 0.45
                info = nav.paso(png, {"tipo": "desplazar", "x": m["w"] // 2, "y": round(m["h"] * 0.62), "dy": -200 if arriba else 300},
                                observar_ms=0)
                if actual:
                    conteo[actual] += 1
            print(f"  paso {i}/{len(c['ruta_mecanica'])} · {est} · {s.get('nombre') or s.get('etiqueta') or s.get('selector')}"
                  + ("" if zona else " · no encontrado"), flush=True)
            seguidos = 0 if zona else seguidos + 1
            if seguidos >= 3:
                problemas.append(f"la ruta se desvió: 3 pasos seguidos sin encontrar su objetivo (desde el paso {i - 2}); "
                                 "revisa la ruta antes de ese punto. Ensayo detenido.")
                break
            if not zona:
                problemas.append(f"paso {i} ({info.get('estado')}): «{s.get('nombre') or s.get('etiqueta') or s.get('selector')}» "
                                 + ("no aparece en pantalla" if not isinstance(caja, dict) else "no está entre los elementos que ve el perfil"))
                info = nav.paso(png, {"tipo": "mecanico", "pasos": [s]}, max_ms=60000)      # seguir con la ruta para revisar el resto
            else:
                texto = dato
                if s.get("teclear_patron"):
                    m = re.search(s["teclear_patron"], " ".join([info.get("texto") or ""] + (info.get("avisos_nuevos") or [])), re.S)
                    texto = (m.group(1) if m and m.groups() else m.group(0)) if m else None
                    if texto is None:
                        problemas.append(f"paso {i} ({info.get('estado')}): el perfil no tendría a la vista el texto {s['teclear_patron']}")
                if texto is not None and zona.get("editable"):
                    accion = dict(tipo="escribir", x=zona["tocar"][0], y=zona["tocar"][1], texto=str(texto))
                else:
                    accion = dict(tipo="tocar", x=zona["tocar"][0], y=zona["tocar"][1])
                info = nav.paso(png, accion, max_ms=60000)
            if actual:
                conteo[actual] += 1
            if info.get("error_accion"):
                problemas.append(f"paso {i}: {info['error_accion']}")
            if actual and info.get("estado") in fines.get(actual, set()):
                actual = inicio.get(info.get("estado"))   # la siguiente tarea empieza donde termina esta
    finally:
        nav.cerrar()
    png.unlink(missing_ok=True)
    res = dict(pasos_minimos=conteo, problemas=problemas, datos=avisos_datos)
    e.ruta("datos", "ensayo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Ensayo sin modelo (0 tokens):")
    for t in tareas:
        print(f"  {t['id']}: {conteo[t['id']]} pasos mínimos (pasos_esperados en estudio.yaml: {t.get('pasos_esperados', '—')})")
    for x in problemas:
        print("  ✕ " + x)
    for x in avisos_datos:
        print("  ! " + x)
    print("Sin problemas del instrumento." if not problemas else f"{len(problemas)} problemas: corrígelos antes del piloto.")
    return res
