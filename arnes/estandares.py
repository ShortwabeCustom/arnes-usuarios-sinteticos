"""Estándares de UiX (fuentes-equipo/uix/estandares.yaml): naming, semáforo de completitud, demográficos,
tamaño de muestra para validar con personas y matriz de decisión.

Los rangos de completitud y de muestra son de estudios con personas. En un estudio sintético se muestran como
referencia, nunca como resultado: las corridas de perfiles no son población.
"""

from __future__ import annotations

import re
import time
import unicodedata
from functools import lru_cache

from .personas import RAIZ
from .yamlx import cargar

RUTA = RAIZ / "fuentes-equipo" / "uix"


@lru_cache(maxsize=1)
def std() -> dict:
    return cargar((RUTA / "estandares.yaml").read_text(encoding="utf-8"))


def limpio(t: str) -> str:
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


# ---- naming -------------------------------------------------------------------------------------


def naming(cfg: dict, metodo: str, fecha: str | None = None) -> str | None:
    """proyecto-metodologia-tema_aaaa-mm-dd-vN a partir del bloque `uix` de estudio.yaml. None si no hay proyecto."""
    u = cfg.get("uix") or {}
    if not u.get("proyecto"):
        return None
    n = std()["naming"]
    met = u.get("metodologia") or n["por_metodo"].get(metodo, metodo)
    tema = limpio(u.get("tema") or "")
    suf = n["sufijo_sintetico"]
    if u.get("sufijo_sintetico", True) and not re.search(rf"(^|-){suf}(-wave\d+)?$", tema):
        tema = f"{tema}-{suf}".strip("-")
    fecha = str(u.get("fecha_fin") or fecha or time.strftime("%Y-%m-%d"))
    proyecto = limpio(u["proyecto"]).replace("-", "")   # un solo bloque: «OU PWA» → oupwa
    return f"{proyecto}-{met}-{tema}_{fecha}-v{int(u.get('version', 1))}"


def revisar_naming(cfg: dict, metodo: str) -> tuple[list[str], list[str]]:
    u = cfg.get("uix") or {}
    if not u.get("proyecto"):
        return [], ["Sin bloque `uix` (proyecto, tema): el reporte no sigue el naming de UiX."]
    n = std()["naming"]
    err, av = [], []
    met = u.get("metodologia") or n["por_metodo"].get(metodo)
    if met not in n["metodologias"]:
        err.append(f"Metodología «{met}» fuera de la lista de UiX: {', '.join(n['metodologias'])}.")
    for campo, norm in (("proyecto", limpio(u["proyecto"]).replace("-", "")), ("tema", limpio(u.get("tema") or ""))):
        v = str(u.get(campo) or "")
        if v and v != norm:
            av.append(f"`uix.{campo}` «{v}» se escribirá «{norm}» (minúsculas, sin espacios ni acentos).")
    if not u.get("tema"):
        err.append("Falta `uix.tema` (flujo, fase, paso, pantalla o componente).")
    nombre = naming(cfg, metodo)
    if nombre and not re.match(n["patron"], nombre):
        err.append(f"El nombre «{nombre}» no cumple {n['investigacion']}.")
    if u.get("sufijo_sintetico") is False:
        av.append("Sin sufijo «-sintetico» en el tema: el entregable puede confundirse con un estudio con personas.")
    return err, av


# ---- completitud --------------------------------------------------------------------------------


def semaforo(completan: int, total: int) -> dict | None:
    if not total:
        return None
    c = std()["completitud"]
    pct = round(100 * completan / total)
    s = next(x for x in c["semaforo"] if pct >= x["min"])
    interp = next(t for m, t in c["interpretacion"] if pct >= m)
    return dict(pct=pct, nivel=s["nivel"], accion=s["accion"], interpretacion=interp,
                promedio=c["promedio_referencia"])


# ---- demográficos -------------------------------------------------------------------------------


def generacion(edad) -> str | None:
    m = re.search(r"\d+", str(edad or ""))
    if not m:
        return None
    x = int(m.group())
    return next((f"{n}, {lo}-{hi} años" if hi < 200 else f"{n}, {lo}+ años" for n, lo, hi in std()["demograficos"]["generaciones"]
                 if lo <= x <= hi), None)


def region_de(estado: str) -> str | None:
    e = limpio(estado)
    for reg, estados in std()["demograficos"]["regiones"].items():
        if e in {limpio(x) for x in estados} | {limpio(reg)}:
            return reg
    return None


def demograficos(it) -> dict[str, dict]:
    """Los 4 datos obligatorios de UiX para un integrante: {campo: {valor, evidencia, detalle}}.
    Edad y género salen del integrante (las variantes los cambian); región y ocupación, de `demograficos` del perfil."""
    d = dict((it.base.get("demograficos") or {}))
    d.update(it.extra.get("demograficos") or {})
    out = {}
    ev = lambda k: (d.get(k) or {}).get("evidencia", "")  # noqa: E731
    edad = (d.get("edad") or {}).get("detalle") or (f"{it.edad} años" if str(it.edad).isdigit() else str(it.edad or ""))
    out["edad"] = dict(valor=generacion(it.edad), detalle=edad, evidencia=ev("edad"))
    out["genero"] = dict(valor=(it.genero or "").capitalize() or None, detalle="", evidencia=ev("genero"))
    for k in ("region", "ocupacion"):
        x = d.get(k) or {}
        val = x.get("valor")
        if k == "region" and val and val not in std()["demograficos"]["regiones"]:
            val = region_de(val) or val
        out[k] = dict(valor=val, detalle=x.get("detalle", ""), evidencia=x.get("evidencia", "AUSENTE" if not val else ""))
    for k in out:
        if not out[k]["valor"] and not out[k]["evidencia"]:
            out[k]["evidencia"] = "AUSENTE"
    return out


def revisar_demograficos(panel) -> list[str]:
    std_d = std()["demograficos"]
    av = []
    for it in panel:
        d = demograficos(it)
        falta = [k for k, v in d.items() if not v["valor"] and v["evidencia"] != "AUSENTE"]
        if falta:
            av.append(f"{it.id}: sin {', '.join(falta)} ni marca AUSENTE.")
        if d["genero"]["valor"] and d["genero"]["valor"] not in std_d["generos"]:
            av.append(f"{it.id}: género «{d['genero']['valor']}» fuera de las categorías de UiX.")
        if d["region"]["valor"] and d["region"]["valor"] not in std_d["regiones"]:
            av.append(f"{it.id}: región «{d['region']['valor']}» no es Norte, Centro-norte, Centro ni Sur.")
    return av


# ---- muestra y decisión -------------------------------------------------------------------------


def muestra(codigo: str) -> tuple[str, str] | None:
    m = std()["muestra"].get(codigo)
    if not m:
        return None
    lo, hi, por = m
    return f"{lo}–{hi} personas" if hi else f"{lo} o más personas", por


def decision(impacto: str, incertidumbre: str) -> str | None:
    return std()["decision"]["matriz"].get(f"{limpio(impacto)}-{limpio(incertidumbre)}")


def oportunidades() -> dict[str, str]:
    return std()["protocolo"]["oportunidades"]
