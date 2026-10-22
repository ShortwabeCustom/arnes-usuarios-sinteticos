"""Conexión con el vault de Obsidian (base de conocimiento metodológico).

- `notas(metodo)`: las notas de concepto que se leen al diseñar el protocolo de ese método.
- `sintesis(estudio)`: escribe en 03-Sintesis/ lo que el estudio dejó, siguiendo las convenciones
  del vault (vault-equipo/CLAUDE.md): frontmatter `tipo: sintesis`, wikilinks, `## Fuentes`,
  `## Ver también`, entrada en 00-Indice/index.md y en 00-Indice/log.md, y un enlace desde las
  notas de concepto relacionadas.

El arnés no edita nada más del vault. Una síntesis se reescribe solo si la generó el arnés
(`generado_por: arnes` en el frontmatter); si no, se crea una versión nueva.
"""

from __future__ import annotations

import glob
import os
import re
import time
import unicodedata
from pathlib import Path

from .estudio import Estudio
from .personas import RAIZ
from .yamlx import cargar

MARCA = "generado_por: arnes"
SEV = {0: "sin problema", 1: "cosmético", 2: "menor", 3: "importante", 4: "crítico"}


def config() -> dict:
    return cargar((RAIZ / "conocimiento.yaml").read_text(encoding="utf-8"))


def vault() -> Path:
    """Ruta del vault, en este orden: `ARNES_VAULT`; la de conocimiento.yaml (admite ~ y comodines, para no guardar
    en el repositorio la carpeta de Google Drive, que lleva el correo de la cuenta); el submódulo `./vault`."""
    candidatos = [os.environ.get("ARNES_VAULT"), config()["vault"], str(RAIZ / "vault")]
    for patron in (os.path.expanduser(c) for c in candidatos if c):
        for v in map(Path, sorted(glob.glob(patron))):
            if (v / "02-Conceptos").is_dir():
                return v
    raise FileNotFoundError(
        "No encuentro el vault. Opciones: sincronizar Google Drive, definir ARNES_VAULT, "
        "o bajar el submódulo con `git submodule update --init vault`.")


def recordar_commit(V: Path) -> None:
    """Si el vault es un repositorio git, recuerda subir lo escrito (el arnés no hace commit en el vault)."""
    if (V / ".git").exists():
        print(f"  El vault es un repositorio git: revisa y sube los cambios con\n"
              f"  git -C \"{V}\" add -A && git -C \"{V}\" commit -m \"Síntesis: …\" && git -C \"{V}\" push")


def notas(metodo: str) -> list[Path]:
    c = config()
    base = vault() / "02-Conceptos"
    return [base / n for n in c["comun"] + c["metodos"].get(metodo, [])]


def titulo(slug: str) -> str:
    """Título real de una nota del vault (su primer «# »), o el slug legible si no la encuentra."""
    try:
        for f in (f for d in ("02-Conceptos", "01-Fuentes", "03-Sintesis") for f in (vault() / d).rglob(f"{slug}.md")):
            for linea in f.read_text(encoding="utf-8").splitlines():
                if linea.startswith("# "):
                    return linea[2:].strip()
    except FileNotFoundError:
        pass
    return slug.replace("-", " ")


def imprimir_notas(metodo: str, producto: str | None = None):
    extra = [vault() / n for n in (config().get("equipo") or {}).get("notas", [])]
    extra += [vault() / n for n in (config().get("productos", {}).get(producto, {}) or {}).get("notas", [])] if producto else []
    for p in notas(metodo) + extra:
        estado = "✓" if p.exists() else "✕ no existe"
        print(f"  {estado} [[{p.stem}]]  {p.relative_to(vault())}")


def _kebab(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:90]


def _cuerpo(e: Estudio, N: dict, nombre: str, enlaces: list[str]) -> str:
    c = e.cfg
    hoy = time.strftime("%Y-%m-%d")
    costo, n_llamadas = e.costo_total()
    n_ses = len(list(e.sesiones_dir.glob("*.json"))) if e.sesiones_dir.exists() else 0
    panel = f"biblioteca «{c.get('biblioteca')}», panel «{c.get('panel')}»" if e.metodo != "persona" else "—"
    hs = sorted(N.get("hallazgos") or [], key=lambda h: -int(h.get("severidad", 0)))
    hal = "\n".join(f"- **{h['titulo']}** — severidad {h.get('severidad')} ({SEV.get(int(h.get('severidad', 0)), '')}), "
                    f"confianza {h.get('confianza', '—')}. {h.get('hallazgo', '')}" for h in hs) or "- (sin hallazgos registrados)"
    apr = "\n".join(f"- {x}" for x in N.get("aprendizajes_metodo") or []) or "- (sin aprendizajes de método registrados en narrativa.yaml)"
    lim = "\n".join(f"- {x}" for x in N.get("limitaciones") or [])
    val = "\n".join(f"- {x}" for x in N.get("validar_con_personas") or [])
    reporte = e.ruta("reporte", f"{e.entregable()}.html")
    tags = ["research-sintetico", "estudio", e.metodo]
    return f"""---
tags: [{", ".join(tags)}]
tipo: sintesis
fuentes: []
actualizado: {hoy}
{MARCA}
estudio: "{e.dir}"
---

# {N.get('titular') or c.get('titulo')}

Síntesis del estudio **{c.get('titulo')}** ({c.get('fecha')}), corrido con el arnés de investigación UX
sintética. {N.get('veredicto', '').strip()}

> [!warning] Investigación sintética
> Los resultados vienen de perfiles sintéticos construidos sobre evidencia, no de personas. Son hipótesis a
> validar con usuarios reales (ver [[investigacion-con-usuarios-sinteticos]]).

## Qué se estudió

- **Pregunta:** {c.get('pregunta_principal', '—')}
- **Método:** {e.metodo} · {panel}
- **Sesiones:** {n_ses} guardadas · {n_llamadas} llamadas · US$ {costo}

## Hallazgos

{hal}

## Lo aprendido sobre el método

{apr}

## Límites

{lim}
{chr(10) + "## Para validar con personas" + chr(10) + chr(10) + val + chr(10) if val else ""}
## Fuentes

- Estudio: `{e.dir}`
- Reporte: `{reporte}`
- Protocolo: `{e.ruta('PROTOCOLO.md')}`

## Ver también

{chr(10).join(f"- [[{x}]]" for x in enlaces)}
"""


def sintesis(e: Estudio, simular: bool = False, enlazar: bool = True) -> Path:
    c = config()
    V = vault()
    N = e.narrativa()
    if not N:
        raise ValueError("El estudio no tiene narrativa.yaml: la síntesis sale de ahí")
    nombre = "estudio-" + _kebab(e.dir.name)
    destino = V / c["sintesis"] / f"{nombre}.md"
    if destino.exists() and MARCA not in destino.read_text(encoding="utf-8"):
        destino = destino.with_name(f"{nombre}-{time.strftime('%Y%m%d%H%M')}.md")
        nombre = destino.stem
    es = c["enlaces_sintesis"]
    prod = (c.get("productos", {}).get(e.cfg.get("guia_estilo"), {}) or {}).get("enlaces", []) if e.cfg.get("guia_estilo") else []
    enlaces = list(dict.fromkeys(es.get("comun", []) + es.get(e.metodo, []) + prod + list(N.get("conceptos") or [])))
    existentes = {p.stem: p for d in ("01-Fuentes", "02-Conceptos", "03-Sintesis") for p in (V / d).rglob("*.md")}
    existentes.pop(nombre, None)  # la síntesis no se enlaza a sí misma
    faltan = [x for x in enlaces if x not in existentes]
    if faltan:
        print(f"  ! sin nota en el vault (quedan como enlaces rotos): {', '.join(faltan)}")
    texto = _cuerpo(e, N, nombre, enlaces)
    hoy = time.strftime("%Y-%m-%d")
    linea_indice = f"- [[{nombre}]] — {N.get('titular') or e.cfg.get('titulo')} (estudio sintético, {e.metodo})"
    verbo = "actualizó" if destino.exists() else "archivó"
    entrada_log = (f"\n## [{hoy}] sintesis | {e.cfg.get('titulo')}\n\nEl arnés de investigación UX sintética {verbo} la síntesis "
                   f"[[{nombre}]] del estudio `{e.dir.name}` ({e.metodo}). "
                   f"{len(N.get('hallazgos') or [])} hallazgos, {len(N.get('aprendizajes_metodo') or [])} aprendizajes de método.\n")
    cambios = [f"{'actualiza' if destino.exists() else 'crea'} {destino.relative_to(V)}", "índice: entrada en «03 — Síntesis»", "log: entrada nueva"]
    a_enlazar = [existentes[x] for x in enlaces if x in existentes] if enlazar else []
    cambios += [f"enlace desde {p.relative_to(V)}" for p in a_enlazar if f"[[{nombre}]]" not in p.read_text(encoding="utf-8")]
    if simular:
        print("Simulación, sin escribir:\n" + "\n".join(f"  · {x}" for x in cambios))
        return destino
    destino.write_text(texto, encoding="utf-8")
    # índice
    ip = V / c["indice"]
    it = ip.read_text(encoding="utf-8")
    if f"[[{nombre}]]" in it:
        it = re.sub(rf"^- \[\[{re.escape(nombre)}\]\].*$", linea_indice, it, flags=re.M)
    else:
        it = it.replace("_(sin páginas aún — se irán agregando respuestas de valor archivadas de futuras consultas)_\n", "")
        it = re.sub(r"(## 03 — Síntesis\n)", rf"\1{linea_indice}\n", it, count=1)
    it = re.sub(r"^actualizado: .*$", f"actualizado: {hoy}", it, count=1, flags=re.M)
    ip.write_text(it, encoding="utf-8")
    # log
    lp = V / c["log"]
    lt = lp.read_text(encoding="utf-8")
    lt = re.sub(r"^actualizado: .*$", f"actualizado: {hoy}", lt, count=1, flags=re.M)
    lp.write_text(lt.rstrip("\n") + "\n" + entrada_log, encoding="utf-8")
    # enlaces desde conceptos: una línea en «Ver también», nada más
    for p in a_enlazar:
        t = p.read_text(encoding="utf-8")
        if f"[[{nombre}]]" in t:
            continue
        linea = f"- [[{nombre}]] — estudio sintético que aplicó este concepto"
        if "## Ver también" in t:
            t = re.sub(r"(## Ver también\n(?:\n)?)", rf"\1{linea}\n", t, count=1)
        else:
            t = t.rstrip("\n") + f"\n\n## Ver también\n\n{linea}\n"
        p.write_text(t, encoding="utf-8")
    e.marcar("sintesis", nota=str(destino.relative_to(V)))
    print("Escrito en el vault:\n" + "\n".join(f"  · {x}" for x in cambios))
    recordar_commit(V)
    return destino
