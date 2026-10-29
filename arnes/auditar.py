"""Evaluación experta con evaluadores independientes y consolidación. Del vault: [[evaluacion-heuristica]]
(3–5 evaluadores independientes, sin ver las notas de los demás hasta terminar; severidad 0–4).

- comprensión: cada pantalla contra los criterios de UX writing W1–W10 (metodos/comprension/METODO.md).
- recorrido: la primera captura de cada pantalla recorrida contra las 10 heurísticas de Nielsen.

Cada evaluador es una sesión limpia sin perfil de cliente. Lo que marcan 2 o más es consenso; lo que
marca uno solo queda «a revisar». Es [INFERENCIA] experta simulada: no reemplaza al investigador, le
da una primera pasada para discutir.
"""

from __future__ import annotations

import collections
import json
import math
from concurrent.futures import ThreadPoolExecutor

from . import consumo, motor
from .guardia import limpiar
from .estudio import Estudio

W = {
    "W1": "Lo importante primero: la noticia que cambia la decisión está en el texto de mayor jerarquía",
    "W2": "Coherencia entre textos: ningún texto desmiente a otro en la misma pantalla",
    "W3": "Una idea por frase: sin frases partidas en varios tamaños ni ideas pegadas sin puntuación",
    "W4": "Lenguaje del cliente: sin términos internos",
    "W5": "Negativas dichas de frente: el «no» se dice claro, sin esconderlo ni culpar",
    "W6": "Causa y salida: dice por qué y qué puede hacer la persona",
    "W7": "El botón anticipa el resultado: el verbo describe lo que pasa al tocar",
    "W8": "Enlaces que se explican solos: el enlace dice a dónde lleva",
    "W9": "Ortografía y concordancia: signos, acentos, género y número",
    "W10": "Tamaño y contraste del texto que decide: lo que cambia la decisión se alcanza a leer",
}
NIELSEN = {
    "N1": "Visibilidad del estado del sistema", "N2": "Correspondencia entre el sistema y el mundo real",
    "N3": "Control y libertad del usuario", "N4": "Consistencia y estándares", "N5": "Prevención de errores",
    "N6": "Reconocer antes que recordar", "N7": "Flexibilidad y eficiencia de uso", "N8": "Diseño estético y minimalista",
    "N9": "Ayudar a reconocer, diagnosticar y recuperarse de errores", "N10": "Ayuda y documentación",
}
SISTEMA = """Eres una persona evaluadora experta en {tipo}, trabajando de forma independiente: no conoces las notas de otras personas evaluadoras.

- Evalúas solo lo que ves. No supongas funciones ni pasos que no aparezcan.
- Un elemento sin conexión en un prototipo no es un defecto de diseño.
- Severidad 0–4 (Nielsen): 0 no es problema · 1 cosmético · 2 menor · 3 importante · 4 crítico. Combina frecuencia, impacto y persistencia.
- Registra también lo que funciona bien.
- Escribe en español, frases cortas, sin jerga.
- Responde únicamente con un objeto JSON válido."""


def _esquema(criterios: dict, zonas: list[str] | None) -> dict:
    obs = {"type": "object", "additionalProperties": False,
           "required": ["criterio", "zona", "problema", "severidad", "recomendacion", "actual", "recomendado"],
           "properties": {"criterio": {"type": "string", "enum": list(criterios)},
                          "zona": {"type": "string", **({"enum": zonas} if zonas else {})},
                          "problema": {"type": "string"}, "severidad": {"type": "integer", "minimum": 0, "maximum": 4},
                          "recomendacion": {"type": "string"}, "actual": {"type": "string"}, "recomendado": {"type": "string"}}}
    return {"type": "object", "additionalProperties": False, "required": ["observaciones", "positivos"],
            "properties": {"observaciones": {"type": "array", "items": obs}, "positivos": {"type": "array", "items": {"type": "string"}}}}


def _material(e: Estudio) -> list[dict]:
    c = e.cfg
    if e.metodo == "comprension":
        out = []
        for pid, p in c["pantallas"].items():
            zs = c["zonas"].get(pid) or {}
            textos = "\n".join(f"- {k} ({z.get('rol', '')}): «{z['texto']}»" for k, z in zs.items() if z.get("texto"))
            out.append(dict(pantalla=pid, imagen=e.ruta(p["imagen"]), zonas=list(zs) + ["general"], contexto=f"Textos de la pantalla, por zona:\n{textos}"))
        return out
    vistas = {}
    tf = e.ruta("datos", "tecnico.json")
    if tf.exists():
        # web: las pantallas de la ruta mecánica (arnes tecnico), limpias y en orden, aunque ningún perfil llegue
        for p in json.loads(tf.read_text(encoding="utf-8")).get("pantallas") or []:
            if p.get("captura") and e.ruta(p["captura"]).exists():
                vistas[p["estado"]] = dict(pantalla=p["estado"], imagen=e.ruta(p["captura"]), zonas=None,
                                           contexto=f"Pantalla «{p['estado']}» del flujo, en orden de la ruta. Texto visible:\n"
                                                    f"{(p.get('texto') or '')[:1500]}")
    for f in sorted(e.sesiones_dir.glob("*.json")):
        s = json.loads(f.read_text(encoding="utf-8"))
        for p in s["pasos"]:
            if p.get("pantalla") and p.get("captura") and p["pantalla"] not in vistas:
                vistas[p["pantalla"]] = dict(pantalla=p["pantalla"], imagen=e.ruta(p["captura"]), zonas=None,
                                             contexto=f"Pantalla del flujo «{p['pantalla']}». Tarea del estudio: "
                                                      f"{' '.join(e.cfg['tareas'][0]['instruccion'].split())}")
    return list(vistas.values())


def auditar(e: Estudio, evaluadores: int = 3, modelo: str = "sonnet", simular: bool = False) -> dict:
    if e.metodo not in ("comprension", "recorrido"):
        raise SystemExit("auditar aplica a comprensión (UX writing) y recorrido (heurísticas de Nielsen)")
    criterios = dict(W if e.metodo == "comprension" else NIELSEN)
    if e.cfg.get("guia_estilo"):  # criterios de la guía de voz y estilo del producto (G1…)
        from .estilo import guia

        criterios.update(guia(e.cfg["guia_estilo"]).get("criterios", {}))
    tipo = "UX writing y contenido" if e.metodo == "comprension" else "usabilidad (evaluación heurística)"
    mat = _material(e)
    if not mat:
        raise SystemExit("No hay pantallas que auditar (en recorrido, corre sesiones primero)")
    llamadas = [(m, k) for m in mat for k in range(1, evaluadores + 1)]
    print(f"{len(mat)} pantallas × {evaluadores} evaluadores = {len(llamadas)} llamadas")
    if simular:
        return {}
    lista = "\n".join(f"- {k}: {v}" for k, v in criterios.items())

    def una(t):
        m, k = t
        prompt = (f"Evalúa la pantalla `{m['imagen'].name}` (ábrela con Read) contra estos criterios:\n{lista}\n\n{m['contexto']}\n\n"
                  "Registra cada problema con su criterio, la zona, la severidad, una recomendación y, si es un texto, "
                  "la versión actual y la recomendada (si no aplica, deja esos dos campos vacíos).")
        r = motor.llamar(motor.Llamada(f"aud-{m['pantalla']}-{k}", prompt, SISTEMA.format(tipo=tipo),
                                       _esquema(criterios, m["zonas"]), ["Read"], [m["imagen"]], modelo=modelo))
        return m["pantalla"], k, r.salida, r.costo_usd, r.tokens

    with ThreadPoolExecutor(6) as ex:
        crudo = list(ex.map(una, llamadas))
    grupos = collections.defaultdict(list)
    positivos = collections.defaultdict(list)
    for pid, k, sal, *_ in crudo:
        for o in sal["observaciones"]:
            clave = (pid, o["criterio"], o["zona"] if e.metodo == "comprension" else "")
            grupos[clave].append(dict(o, evaluador=k))
        positivos[pid] += sal["positivos"]
    umbral = max(2, math.ceil(evaluadores / 2))
    cons = []
    for (pid, cr, zona), obs in grupos.items():
        ev = sorted({o["evaluador"] for o in obs})
        cons.append(dict(pantalla=pid, criterio=cr, nombre_criterio=criterios[cr], zona=zona, evaluadores=len(ev), de=evaluadores,
                         consenso=len(ev) >= umbral, severidad_media=round(sum(o["severidad"] for o in obs) / len(obs), 1),
                         problemas=[o["problema"] for o in obs], recomendaciones=[o["recomendacion"] for o in obs],
                         reescrituras=[[o["actual"], o["recomendado"]] for o in obs if o.get("actual") and o.get("recomendado")]))
    cons.sort(key=lambda x: (-x["evaluadores"], -x["severidad_media"]))
    res = dict(metodo=e.metodo, evaluadores=evaluadores, umbral_consenso=umbral, consolidado=cons,
               positivos={k: v for k, v in positivos.items()}, crudo=[dict(pantalla=p, evaluador=k, salida=s) for p, k, s, *_ in crudo],
               costo_usd=round(sum(x[3] for x in crudo), 3), tokens=consumo.sumar(*(x[4] for x in crudo)))
    res = limpiar(res)   # sin correos, CURP ni tarjetas que un evaluador cite de la pantalla
    e.ruta("datos", "auditoria.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    e.marcar("auditar", evaluadores=evaluadores, consenso=sum(x["consenso"] for x in cons), tokens=consumo.total(res["tokens"]))
    print(f"Consenso ({umbral}+ de {evaluadores}): {sum(x['consenso'] for x in cons)} · a revisar (1 evaluador): {sum(not x['consenso'] for x in cons)} · {consumo.texto(res['tokens'])}")
    for x in cons[:15]:
        print(f"  {'●' if x['consenso'] else '○'} {x['pantalla']:12s} {x['criterio']:4s} {x['zona'][:14]:14s} {x['evaluadores']}/{evaluadores} "
              f"sev {x['severidad_media']} · {x['problemas'][0][:90]}")
    return res
