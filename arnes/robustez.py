"""Qué tan firme es lo que dicen las sesiones. Del vault: «creer en lo que se repite».

[[investigacion-con-usuarios-sinteticos]]: con muestras chicas, dos opciones cercanas no se distinguen
(n=20 y 50/50 → IC 95% de ~22 puntos); confiar en brechas grandes, no en el orden; correr 2–3 veces y
quedarse con lo que persiste. Y la población sintética tiende a colapsar: individuos creíbles, panel
poco diferenciado.

- `estabilidad`: por perfil y celda, ¿repite la misma respuesta entre corridas?
- `comparar`: brecha entre variantes con intervalo de Wilson; «clara» solo si los intervalos no se tocan.
- `homogeneidad`: ¿todos los perfiles dicen lo mismo? (cerradas: misma opción modal; abiertas: palabras compartidas)

Las corridas no son población: el intervalo dice si la brecha entre corridas es firme, no estima una
proporción de clientes.
"""

from __future__ import annotations

import collections
import math
import re

UMBRAL_ESTABLE = 2 / 3
UMBRAL_HOMOGENEO = 0.8  # proporción de celdas donde todo el panel coincide
UMBRAL_PALABRAS = 0.45  # parecido medio entre respuestas abiertas de perfiles distintos


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - m), min(1.0, c + m))


def estabilidad(agregado: dict) -> dict:
    """agregado: "bloque|grupo|var|integrante|modo|momento|q" → [opción por corrida]."""
    por_celda = collections.defaultdict(list)
    inestables = []
    for k, vals in agregado.items():
        vals = [v for v in vals if v]
        if len(vals) < 2:
            continue
        share = collections.Counter(vals).most_common(1)[0][1] / len(vals)
        b, g, v, i, m, mo, q = k.split("|")
        por_celda["|".join((b, g, v, m, mo, q))].append(share)
        if share < UMBRAL_ESTABLE:
            inestables.append(dict(clave=k, integrante=i, respuestas=vals))
    celdas = {k: dict(media=round(sum(x) / len(x), 2), perfiles=len(x), inestables=sum(s < UMBRAL_ESTABLE for s in x))
              for k, x in por_celda.items()}
    todas = [s for x in por_celda.values() for s in x]
    return dict(global_=round(sum(todas) / len(todas), 2) if todas else None, celdas=celdas, inestables=inestables)


def comparar(aciertos: dict, a: str, b: str) -> dict | None:
    x, y = aciertos.get(a), aciertos.get(b)
    if not x or not y:
        return None
    ia, ib = wilson(x["aciertos"], x["total"]), wilson(y["aciertos"], y["total"])
    pa, pb = x["aciertos"] / x["total"], y["aciertos"] / y["total"]
    clara = ia[0] > ib[1] or ib[0] > ia[1]
    return dict(a=a, b=b, pa=round(pa, 2), pb=round(pb, 2), brecha=round(pa - pb, 2),
                ic_a=[round(v, 2) for v in ia], ic_b=[round(v, 2) for v in ib], clara=clara)


def comparaciones(aciertos: dict) -> list[dict]:
    """Todas las variantes de un mismo grupo, modo, momento y pregunta, de a pares."""
    grupos = collections.defaultdict(list)
    for k in aciertos:
        b, g, v, m, mo, q = k.split("|")
        grupos[(b, g, m, mo, q)].append(k)
    out = []
    for ks in grupos.values():
        ks = sorted(ks)
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                r = comparar(aciertos, a, b)
                if r:
                    out.append(r)
    return out


def _palabras(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-záéíóúñü0-9$,]{4,}", (t or "").lower())}


def _parecido(a: str, b: str) -> float:
    A, B = _palabras(a), _palabras(b)
    return len(A & B) / len(A | B) if A and B else 0.0


def homogeneidad(agregado: dict, abiertas: dict | None = None) -> dict:
    """abiertas: "bloque|grupo|var|modo|momento|q" → {integrante: [textos]}."""
    modal = collections.defaultdict(dict)
    for k, vals in agregado.items():
        vals = [v for v in vals if v]
        if not vals:
            continue
        b, g, v, i, m, mo, q = k.split("|")
        modal["|".join((b, g, v, m, mo, q))][i] = collections.Counter(vals).most_common(1)[0][0]
    celdas = {k: len(set(d.values())) == 1 for k, d in modal.items() if len(d) >= 3}
    prop = round(sum(celdas.values()) / len(celdas), 2) if celdas else None
    par = []
    for k, d in (abiertas or {}).items():
        ints = list(d)
        for i, a in enumerate(ints):
            for b in ints[i + 1:]:
                for ta in d[a]:
                    for tb in d[b]:
                        par.append(_parecido(ta, tb))
    sim = round(sum(par) / len(par), 2) if par else None
    alertas = []
    if prop is not None and prop >= UMBRAL_HOMOGENEO:
        alertas.append(f"En {prop:.0%} de las celdas cerradas todos los perfiles eligen lo mismo: el panel casi no diferencia. "
                       "Puede ser que la pantalla sea inequívoca, o que la población sintética esté colapsando.")
    if sim is not None and sim >= UMBRAL_PALABRAS:
        alertas.append(f"Las respuestas abiertas de perfiles distintos comparten {sim:.0%} de sus palabras: revisar si suenan a la misma voz.")
    return dict(celdas_homogeneas=prop, parecido_abiertas=sim, alertas=alertas)
