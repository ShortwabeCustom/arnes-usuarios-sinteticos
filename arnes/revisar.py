"""Revisión del instrumento antes de correr sesiones. Del vault: [[preguntas-sugestivas]],
[[first-click-testing]], [[five-second-testing]], [[marco-de-metodos-de-investigacion-ux]].

Errores (bloquean `arnes sesiones` salvo `--forzar`): preguntas sugestivas o cargadas.
Avisos: lenguaje copiado de la interfaz, opciones sin salida neutra, sin pregunta abierta al inicio,
sin baseline, consigna que adelanta el resultado.
"""

from __future__ import annotations

import re

from .estudio import Estudio

# Los 5 tipos de Lyssna, más la versión cargada.
SUGESTIVAS = [
    (r"¿\s*no\s+(crees|cree|te parece|le parece|es cierto)", "coercitiva: «¿no crees…?» empuja a responder que sí"),
    (r"\b(verdad|cierto)\s*\?", "coercitiva: confirmación retórica al final («…, ¿verdad?»)"),
    (r"\b(obviamente|claramente|sin duda|evidentemente|seguro que)\b", "coercitiva: lenguaje absoluto"),
    (r"¿\s*(qué tanto|cuánto)\s+(te|le)\s+(gust|encant|disfrut|ayud|facilit)", "basada en suposiciones: asume que le gustó o le sirvió"),
    (r"\bsi\s+(te|le)\s+(gust|encant|sirv|disfrut)\w*.*¿", "de implicación directa: condiciona la pregunta a una respuesta positiva"),
    (r"\b(la mayoría|muchos|todos)\s+(de\s+)?(nuestros|los)\s+(usuarios|clientes)", "declaración interconectada: prueba social antes de preguntar"),
    (r"¿\s*(ya\s+)?(dejaste|dejó)\s+de\b", "cargada: cualquier respuesta admite un supuesto"),
    (r"\b(fácil|rápido|claro|sencillo|intuitivo)\b(?!.*\b(difícil|lento|confuso|complicado)\b)", "unilateral: nombra solo el polo positivo (preguntar «¿qué tan fácil o difícil…?»)"),
]
NEUTRAS = {"no_se", "ns", "igual", "neutra", "ninguna", "nada", "en_parte", "otro", "no_lo_dice"}


def _ngramas(t: str, n: int = 3) -> set[tuple]:
    w = re.findall(r"\w+", (t or "").lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def revisar(e: Estudio, imprimir: bool = True) -> tuple[list[str], list[str]]:
    c = e.cfg
    err, avi = [], []
    textos = []
    if e.metodo == "comprension":
        textos += [(f"pregunta {q['id']}", q["texto"]) for q in c.get("preguntas", [])]
        textos += [(f"pareada {q['id']}", q["texto"]) for q in (c.get("pareada") or {}).get("preguntas", [])]
        textos.append(("consigna", c.get("consigna", "")))
    elif e.metodo == "recorrido":
        for t in c.get("tareas", []):
            textos += [(f"tarea {t['id']} · instrucción", t.get("instruccion", "")), (f"tarea {t['id']} · escenario", t.get("escenario", ""))]
    for donde, t in textos:
        for pat, por in SUGESTIVAS:
            if re.search(pat, t or "", re.I):
                (avi if por.startswith("unilateral") else err).append(f"{donde}: {por} — «{' '.join(t.split())[:90]}»")
    if e.metodo == "comprension":
        qs = c.get("preguntas", [])
        primera = next((q for q in qs if not q.get("solo_continuacion")), None)
        if primera and primera.get("opciones"):
            avi.append("la primera pregunta es cerrada: conviene abrir con una abierta para no sembrar la respuesta")
        for q in qs:
            ops = set(q.get("opciones") or [])
            if ops and not ops & NEUTRAS:
                avi.append(f"pregunta {q['id']}: las opciones no tienen salida neutra («no_se», «igual», «en_parte»)")
        interfaz = set()
        for zs in (c.get("zonas") or {}).values():
            for z in (zs or {}).values():
                interfaz |= _ngramas(z.get("texto"))
        for q in qs:
            comun = _ngramas(q["texto"]) & interfaz
            if comun:
                avi.append(f"pregunta {q['id']}: repite texto de la pantalla («{' '.join(next(iter(comun)))}…»); se vuelve un juego de "
                           "coincidencia de palabras (first-click testing)")
        grupos = {}
        for pid, p in (c.get("pantallas") or {}).items():
            grupos.setdefault(p.get("grupo", "E"), []).append(p)
        for g, ps in grupos.items():
            if len(ps) == 1:
                avi.append(f"grupo {g}: una sola pantalla, sin comparación. Correr también el diseño actual como baseline")
            elif not any(p.get("baseline") for p in ps):
                avi.append(f"grupo {g}: ninguna variante marcada como `baseline: true` (diseño actual). Sin baseline, un acierto "
                           "bajo no se puede leer")
        cons = (c.get("consigna") or "").lower()
        for q in qs:
            for v in (q.get("correcta") or {}).values():
                for x in (v if isinstance(v, list) else [v] if isinstance(v, str) else []):
                    if len(x) > 3 and x.replace("_", " ") in cons:
                        avi.append(f"la consigna contiene «{x}», la respuesta correcta de {q['id']}: puede adelantar el resultado")
    if e.metodo == "recorrido":
        if not c.get("baseline_url") and not c.get("sin_baseline_porque"):
            avi.append("sin `baseline_url` (diseño actual) ni `sin_baseline_porque`: sin baseline, una tasa de completitud no se puede leer")
        for t in c.get("tareas", []):
            if not t.get("fin"):
                avi.append(f"tarea {t['id']}: sin `fin`; el arnés no puede saber si se completó")
            if not t.get("primer_toque"):
                avi.append(f"tarea {t['id']}: sin `primer_toque` esperado; no se mide el primer clic (87% vs 46% de éxito según si acierta)")
    if imprimir:
        for x in err:
            print(f"  ✕ {x}")
        for x in avi:
            print(f"  ! {x}")
        print(f"Instrumento: {len(err)} errores · {len(avi)} avisos" + ("" if not err else " — corregir antes de correr"))
    return err, avi
