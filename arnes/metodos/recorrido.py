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
from ..navegador import Navegador, marcar, node_id

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
RETOMA_TEXTO = r"contin[uú]a tu solicitud|retoma|sigue (con|donde)|guardamos tu (avance|progreso)|vuelve a donde"


def _pantalla_id(material: str, url: str) -> str:
    if material == "figma":
        return node_id(url) or "?"
    from urllib.parse import urlparse

    u = urlparse(url)
    return ((u.netloc + u.path).rstrip("/") + (f"#{u.fragment}" if u.fragment else "")) or url


def _fin_alcanzado(fin: dict | None, info: dict, material: str) -> bool:
    if not fin:
        return False
    if fin.get("node_ids") and _pantalla_id(material, info["url"]) in {str(x).replace(":", "-") for x in fin["node_ids"]}:
        return True
    if fin.get("url_contiene") and fin["url_contiene"] in info["url"]:
        return True
    if fin.get("texto_visible") and fin["texto_visible"].lower() in (info.get("texto") or "").lower():
        return True
    return False


def _lista_zonas(material: str, zonas: list[dict]) -> str:
    if material == "figma":
        return ""
    lin = [f"{i}. {z['tipo']}{' (se puede escribir)' if z['editable'] else ''}: «{z['etiqueta'] or 'sin texto'}»"
           for i, z in enumerate(zonas, 1)]
    return "Elementos marcados:\n" + "\n".join(lin) + "\n\n"


def _overlay(it, tarea, paso, p) -> str:
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    return ('<div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#C7F284">Sesión sintética · simulación</div>'
            f'<div style="font-size:16px;font-weight:700;margin-top:4px">{esc(it.nombre)}</div>'
            f'<div style="font-size:12px;opacity:.8">{esc(it.segmento)} · {esc(tarea["id"])} · paso {paso}</div>'
            f'<div style="margin-top:8px;padding:8px;border-radius:8px;background:rgba(255,255,255,.08)">«{esc(p.get("pensamiento", ""))}»</div>'
            f'<div style="margin-top:6px;font-size:12px">→ {esc(p.get("accion", {}).get("opcion", ""))} · confianza {p.get("confianza", "")} · fricción {p.get("friccion", "")}</div>'
            '<div style="margin-top:6px;font-size:10px;opacity:.6">Ruta y toques reales. Pensamiento y ritmo simulados.</div>')


def sesion(e: Estudio, integrante: str, tarea: str | None = None, guion: bool = False, corridas: int | None = None) -> list[dict]:
    c = e.cfg
    panel = {it.id: it for it in e.panel()}
    if integrante == "todos":
        out = []
        for iid in panel:
            out += sesion(e, iid, tarea, guion, corridas)
        return out
    ncorr = corridas or c.get("corridas", 1)
    it = panel[integrante]
    tareas = [t for t in c["tareas"] if not tarea or t["id"] == tarea]
    material = c["material"]
    disp = c.get("dispositivo", {})
    nav = Navegador(c.get("sesion_navegador", "arnes"), material, e.ruta("datos", "navegador"),
                    (disp.get("ancho", 360), disp.get("alto", 800)) if material == "web" else None)
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
        if not abierto:
            nav.abrir(t.get("url") or c["url"], visible=c.get("visible", True))
            abierto = True
            for a in c.get("preparacion", []):  # p. ej. descartar cookies antes de medir nada
                nav.paso(cap / "prep.png", a)
        elif c.get("reiniciar_entre_tareas", True) or n > 1:
            nav.paso(cap / "prep.png", {"tipo": "ir", "url": t.get("url") or c["url"]})
        if c.get("video", True):
            e.ruta("datos", "videos").mkdir(parents=True, exist_ok=True)
            nav.video(True, str(e.ruta("datos", "videos", f"{sid}.webm")))
        reg = dict(id=sid, tarea=t["id"], corrida=n, integrante=it.id, nombre=it.nombre, perfil=it.perfil, segmento=it.segmento,
                   ocean=it.ocean, modo="guion" if guion else "autonomo", material=material, modelo=modelo,
                   inicio=time.strftime("%Y-%m-%dT%H:%M:%S"), pasos=[], costo_usd=0.0)
        try:
            if guion:
                _guion(e, nav, it, t, cap, reg)
            else:
                _autonomo(e, nav, it, t, cap, reg, sistema, datos, modelo)
        finally:
            if c.get("video", True):
                nav.video(False)
                reg["video"] = f"datos/videos/{sid}.webm"
            reg["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            reg["costo_usd"] = round(reg["costo_usd"], 4)
            e.sesiones_dir.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
            with open(e.ruta("datos", "registro-sesiones.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(id=sid, ok=True, costo_usd=reg["costo_usd"], resultado=reg.get("resultado"),
                                        t=reg["fin"]), ensure_ascii=False) + "\n")
        print(f"{sid}: {reg.get('resultado')} en {len(reg['pasos'])} pasos · US$ {reg['costo_usd']}")
        registros.append(reg)
    if abierto and c.get("cerrar_al_terminar", True):
        nav.cerrar()
    e.marcar("sesiones", ultima=registros[-1]["id"] if registros else None)
    return registros


def _autonomo(e, nav, it, t, cap, reg, sistema, datos, modelo):
    _bucle(e, nav, it, t, cap, reg, sistema, datos, modelo)
    ses = reg.pop("_ses", None)
    if ses and reg.get("resultado") != "fallo_max_pasos":
        r = motor.llamar(motor.Llamada(f"{reg['id']}-ces", "La sesión terminó. Pensando en todo lo que hiciste para esta tarea, "
                                       "¿qué tan fácil o difícil te resultó? Responde en JSON: «ces» de 1 (muy difícil) a 7 (muy fácil) "
                                       "y «texto» con una frase de por qué.", sistema, ESQUEMA_CES, [], [], reanudar=ses,
                                       modelo=modelo, persistir=True))
        reg["ces"] = r.salida
        reg["costo_usd"] += r.costo_usd


def _senales(info) -> dict:
    t = info.get("texto") or ""
    return dict(campos=info.get("campos"), progreso_visible=info.get("progreso"), errores_visibles=info.get("errores_validacion") or [],
                permisos=info.get("permisos") or [], host=info.get("host"), paginas=info.get("paginas"),
                palabras=len(t.split()) if t else None)


def _bucle(e, nav, it, t, cap, reg, sistema, datos, modelo):
    c = e.cfg
    material = c["material"]
    actual = cap / "siguiente.png"  # captura de la pantalla que el perfil va a ver en el próximo paso
    info = nav.paso(actual, instrumentar=True)
    texto_inicio = info.get("texto")
    retoma = t.get("retoma")
    ses, aviso, quietos = None, "", 0
    friccion_max, sin_resp = 0, 0
    for n in range(1, t.get("max_pasos", c.get("max_pasos", 25)) + 1):
        png, marcas = cap / f"p{n:02d}.png", cap / f"p{n:02d}-marcas.png"
        actual.replace(png)
        zonas = info.get("zonas", [])
        marcar(png, zonas, marcas)
        pid = _pantalla_id(material, info["url"])
        if _fin_alcanzado(t.get("fin"), info, material):
            reg["resultado"] = "exito" if friccion_max < 3 and not sin_resp else "exito_con_friccion"
            reg["pasos"].append(dict(n=n, pantalla=pid, url=info["url"], captura=str(png.relative_to(e.dir)), fin=True))
            return
        intro = ""
        if n == 1:
            intro = (f"{' '.join(t.get('escenario', '').split())}\n\nTu tarea: {' '.join(t['instruccion'].split())}\n\n"
                     f"Datos de prueba (ficticios) por si el producto te los pide:\n{datos}\n\n")
        prompt = (f"{intro}{aviso}Paso {n}. La pantalla actual es `{png.name}`: ábrela con Read y mírala como la verías en tu "
                  f"celular. En `{marcas.name}` está la misma pantalla con números sobre los {len(zonas)} elementos que responden "
                  f"al toque. Mira primero la limpia; usa la marcada solo para indicar dónde actúas.\n\n"
                  f"{_lista_zonas(material, zonas)}{FORMATO}\n\n{PLANTILLA}")
        r = motor.llamar(motor.Llamada(f"{reg['id']}-p{n}", prompt, sistema, ESQUEMA, ["Read"], [png, marcas],
                                       reanudar=ses, modelo=modelo, persistir=True))
        ses = r.session_id
        reg["_ses"] = ses
        reg["costo_usd"] += r.costo_usd
        p = r.salida
        op = p["accion"]["opcion"]
        friccion_max = max(friccion_max, p["friccion"])
        paso = dict(n=n, pantalla=pid, url=info["url"], captura=str(png.relative_to(e.dir)),
                    marcas=str(marcas.relative_to(e.dir)), zonas=len(zonas), perfil=p, modelo_id=r.modelo_id,
                    zonas_detalle=[{k: z[k] for k in ("x", "y", "w", "h", "tipo", "etiqueta")} for z in zonas],
                    texto_pantalla=info.get("texto") or None,
                    marco=info.get("marco"), **_senales(info))
        if op in ("abandonar", "terminar"):
            fin = _fin_alcanzado(t.get("fin"), info, material)
            reg["resultado"] = "abandono" if op == "abandonar" else ("exito" if fin else "falso_exito" if t.get("fin") else "terminado_sin_criterio")
            reg["pasos"].append(paso)
            return
        accion, desc = _traducir(op, p, zonas, info, material)
        paso["accion"] = accion
        m = p.get("marca", 0)
        if accion and accion["tipo"] in ("tocar", "escribir") and 0 < m <= len(zonas):
            paso["zona_tocada"] = {k: zonas[m - 1][k] for k in ("x", "y", "w", "h", "tipo", "etiqueta")}
        if accion is None:
            paso["respuesta"] = "fuera_de_marcas"
            aviso = f"Resultado del paso anterior: {desc}\n\n"
            reg["pasos"].append(paso)
            quietos += 1
            info = nav.paso(actual)
        else:
            antes = info
            info = nav.paso(actual, accion, overlay=_overlay(it, t, n, p) if c.get("video", True) else None)
            cambio = info["cambio_url"] or info["cambio_imagen"]
            paso["espera_ms"] = info.get("espera_ms")
            paso["host_despues"], paso["paginas_despues"] = info.get("host"), info.get("paginas")
            nuevos = sorted(set(info.get("errores_validacion") or []) - set(antes.get("errores_validacion") or []))
            if nuevos:
                paso["validacion_disparada"] = nuevos
            paso["respuesta"] = "si" if cambio else "no"
            paso["pantalla_despues"] = _pantalla_id(material, info["url"])
            if accion["tipo"] in ("tocar", "escribir") and not cambio:
                sin_resp += 1
            quietos = 0 if cambio else quietos + 1
            aviso = f"Resultado del paso anterior: {desc}: {'la pantalla cambió' if cambio else 'no pasó nada visible'}.\n\n"
            reg["pasos"].append(paso)
            if retoma and n == retoma.get("tras_paso") and "retoma" not in reg:
                info, nota = _interrumpir(e, nav, actual, t, info, texto_inicio, retoma, reg, material)
                aviso += nota
        if quietos >= c.get("max_sin_cambio", 4):
            reg["resultado"] = "atascado"
            return
    reg["resultado"] = "fallo_max_pasos"


def _interrumpir(e, nav, actual, t, info, texto_inicio, retoma, reg, material):
    """Retoma de solicitud: sale del flujo y vuelve a entrar. «recargar» = recarga la página (misma sesión del
    navegador); «reabrir» = vuelve a entrar por la URL de inicio. Compara lo que ve después con lo que veía antes."""
    import re

    antes_pid, antes_txt = _pantalla_id(material, info["url"]), info.get("texto")
    modo = retoma.get("modo", "recargar")
    accion = {"tipo": "recargar"} if modo == "recargar" else {"tipo": "ir", "url": t.get("url") or e.cfg["url"]}
    nuevo = nav.paso(actual, accion)
    pid, txt = _pantalla_id(material, nuevo["url"]), nuevo.get("texto")
    if material == "web" and antes_txt is not None:
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
    centro = (marco["x"] + marco["w"] // 2, marco["y"] + marco["h"] // 2)
    if op in ("tocar", "escribir"):
        if not z:
            return None, f"quisiste {op} algo que no está entre los elementos que responden ({p.get('intencion', '')})"
        if op == "escribir" and material == "web" and z["editable"]:
            return dict(tipo="escribir", x=z["tocar"][0], y=z["tocar"][1], texto=p.get("escribir", "")), f"escribiste en el {m}"
        return dict(tipo="tocar", x=z["tocar"][0], y=z["tocar"][1]), f"tocaste el {m}"
    if op.startswith("desplazar"):
        return dict(tipo="desplazar", x=centro[0], y=centro[1], dy=500 if op.endswith("abajo") else -500), f"desplazaste hacia {op.split('_')[1]}"
    if op == "volver":
        if material == "web":
            return dict(tipo="volver"), "volviste atrás con el navegador"
        return None, "este prototipo no tiene botón de atrás del navegador; si hay uno en la pantalla, tócalo"
    return dict(tipo="esperar"), "esperaste"


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
                          costo_usd=s.get("costo_usd", 0)))
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
    base = {}
    for s in S:
        for p in s["pasos"]:
            a = p.get("accion") or {}
            if p.get("pantalla") and p.get("captura") and p["pantalla"] not in base:
                base[p["pantalla"]] = e.ruta(p["captura"])
            if a.get("tipo") in ("tocar", "escribir"):
                por[p["pantalla"]].append((a["x"], a["y"], p.get("respuesta") == "si", s["integrante"]))
    for pid, toques in por.items():
        if pid not in base or not base[pid].exists():
            continue
        im = Image.open(base[pid]).convert("RGBA")
        capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for x, y, ok, _ in toques:
            col = (34, 160, 90, 110) if ok else (210, 50, 40, 140)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col, outline=col[:3] + (255,), width=2)
        Image.alpha_composite(im, capa).convert("RGB").save(e.ruta("heatmaps", f"toques-{slug(pid)}.png"))
