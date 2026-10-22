"""Método 1 · Construir un User Persona con usuarios sintéticos.

La construcción es trabajo de análisis (ver metodos/persona/METODO.md): se lee la fuente, se arma
el dataset si no existe, y se producen los entregables 01–12. Lo que el arnés automatiza:

- `validar`: que los entregables existan y tengan la forma que los otros dos métodos consumen.
- `probar`: batería de fidelidad. Cada perfil recibe preguntas que su prompt declara fuera de
  cobertura (debe responder la frase exacta), una dentro de cobertura (no debe negarse) y una
  pregunta que sugiere la respuesta (para revisar a mano si busca agradar).
"""

from __future__ import annotations

import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .. import consumo, motor
from ..personas import PERSONAS, Biblioteca

ENTREGABLES = {
    "01-diccionario-variables.csv": "variables con fuente, clase, N y uso en el modelo",
    "02-frecuencias.csv": "distribuciones con base declarada",
    "03-codificacion-cualitativa.csv": "temas codificados con fuente y cita",
    "04-matriz-relaciones.csv": "relaciones con fuerza, n y nivel de evidencia",
    "05-segmentos.csv": "segmentos comparados",
    "06-usuarios-sinteticos.json": "perfiles completos + metadatos + límites",
    "07-reglas-conductuales.csv": "reglas SI / Y / ENTONCES / PORQUE / probabilidad",
    "08-analisis.py": "script que reproduce el análisis desde la fuente",
    "10-guia-editorial.md": "voz, niveles de lenguaje, etiquetas de evidencia",
    "11-diccionario-editorial.md": "ACTUAL → RECOMENDADO → RAZÓN",
}
COLUMNAS_REGLAS = {"id", "perfil", "si_y", "entonces", "porque", "probabilidad"}
SECCIONES = ["Reglas de interpretación de este rol", "Perfil", "Objetivos", "Motivaciones", "Pain points",
             "Reglas conductuales", "Cómo hablas"]
FRASE = "Los datos disponibles no permiten determinar con suficiente confianza cómo reaccionaría este perfil."


def _ok(b: bool) -> str:
    return "✓" if b else "✕"


def validar(carpeta: str) -> bool:
    d = Path(carpeta)
    if not d.is_dir():
        d = PERSONAS / carpeta
    filas = []
    for f, que in ENTREGABLES.items():
        filas.append((f, (d / f).exists(), que))
    filas.append(("09-reporte.html (o 09-reporte-completo.html)", any(d.glob("09-*.html")), "reporte visual offline"))
    prompts = sorted(p for p in (d / "system-prompts").glob("*.md")) if (d / "system-prompts").exists() else []
    filas.append(("system-prompts/*.md", bool(prompts), f"{len(prompts)} archivos"))
    problemas = []
    if (d / "07-reglas-conductuales.csv").exists():
        with open(d / "07-reglas-conductuales.csv", encoding="utf-8") as f:
            r = csv.DictReader(f)
            faltan = COLUMNAS_REGLAS - set(r.fieldnames or [])
            reglas = list(r)
        if faltan:
            problemas.append(f"07: faltan columnas {sorted(faltan)}")
        ids = [x["id"] for x in reglas]
        if len(ids) != len(set(ids)):
            problemas.append("07: ids de regla repetidos")
        sin_porque = [x["id"] for x in reglas if not (x.get("porque") or "").strip()]
        if sin_porque:
            problemas.append(f"07: reglas sin PORQUE (evidencia): {', '.join(sin_porque[:8])}")
    if (d / "06-usuarios-sinteticos.json").exists():
        j = json.loads((d / "06-usuarios-sinteticos.json").read_text(encoding="utf-8"))
        if not j.get("usuarios"):
            problemas.append("06: no hay lista «usuarios»")
        meta = j.get("meta", {})
        if not any(meta.get(k) for k in ("limites", "limitaciones", "no_simulable")) and not j.get("no_modelado"):
            problemas.append("06: meta sin límites declarados")
    no_perfiles = set()
    if (d / "biblioteca.yaml").exists():
        from ..yamlx import cargar

        no_perfiles = {Path(x["archivo"]).name for x in cargar((d / "biblioteca.yaml").read_text(encoding="utf-8")).get("no_perfiles") or []}
    for p in prompts:
        if p.name in no_perfiles:
            print(f"  · {p.name}: declarado como no-perfil en biblioteca.yaml, no se valida como perfil")
            continue
        t = p.read_text(encoding="utf-8")
        if FRASE not in t:
            problemas.append(f"{p.name}: no trae la frase exacta de sin cobertura")
        if "No puedes opinar sobre" not in t:
            problemas.append(f"{p.name}: no declara qué temas no cubre («No puedes opinar sobre: …»)")
        for s in SECCIONES:
            if f"## {s}" not in t:
                problemas.append(f"{p.name}: falta la sección «{s}»")
        if not re.search(r"\[(OBSERVADO|INFERIDO|HIPÓTESIS|AUSENTE|APROXIMACIÓN)", t):
            problemas.append(f"{p.name}: el perfil no etiqueta la evidencia de sus datos")
    if not (d / "biblioteca.yaml").exists():
        problemas.append("falta biblioteca.yaml: sin él, los métodos 2 y 3 no pueden usar estos perfiles (ver metodos/persona/METODO.md)")
    avisos = []
    n_perf = len([p for p in prompts if p.name not in no_perfiles])
    if n_perf > 5:
        avisos.append(f"{n_perf} perfiles: con más de 5 personas activas la memorabilidad se diluye ([[personas-y-arquetipos]])")
    if (d / "06-usuarios-sinteticos.json").exists():
        eje = str(json.loads((d / "06-usuarios-sinteticos.json").read_text(encoding="utf-8")).get("meta", {}).get("eje_de_segmentacion", ""))
        justificado = re.search(r"[úu]nica|porque|n suficiente|no permite|solo .* con", eje, re.I)
        if re.search(r"generaci|edad|g[ée]nero|ingreso|demogr", eje, re.I) and justificado:
            print(f"  ✓ eje demográfico, justificado en 06: «{eje[:110]}»")
        elif re.search(r"generaci|edad|g[ée]nero|ingreso|demogr", eje, re.I):
            avisos.append("el eje de segmentación es demográfico; las personas de UX se segmentan por comportamiento y actitud. "
                          "Si la fuente no permite otro eje, declarar por qué en 06 y en el reporte ([[personas-y-arquetipos]])")
    if (d / "biblioteca.yaml").exists() and d.parent == PERSONAS:
        from .. import estandares as std

        b = Biblioteca(d.name)
        integrantes = [it for p in b.paneles for it in b.panel(p)]
        sin = [k for k, v in b.perfiles.items() if not v.get("demograficos")]
        if sin:
            avisos.append(f"perfiles {', '.join(sin)} sin `demograficos` en biblioteca.yaml: UiX pide edad, género, región "
                          "y ocupación en toda investigación (fuentes-equipo/uix/Demográficos.md); si falta el dato, AUSENTE")
        avisos += std.revisar_demograficos(integrantes)
    for f, ok, que in filas:
        print(f"  {_ok(ok)} {f:48s} {que}")
    for x in problemas:
        print(f"  ✕ {x}")
    for x in avisos:
        print(f"  ! {x}")
    ok = all(o for _, o, _ in filas) and not problemas
    print("Válido" if ok else f"{len(problemas) + sum(not o for _, o, _ in filas)} problemas")
    return ok


def _limites(prompt: str) -> list[str]:
    m = re.search(r"No puedes opinar sobre:\s*(.+)", prompt)
    if not m:
        return []
    return [re.sub(r"\s*\(.*?\)|\*", "", x).strip(" .") for x in m.group(1).split(";") if x.strip()]


def probar(biblioteca: str, panel: str = "base4", modelo: str = "sonnet", n_fuera: int = 3) -> dict:
    b = Biblioteca(biblioteca)
    pf = b.meta.get("prueba_fidelidad", {})
    dentro = pf.get("dentro", "¿Qué es lo que más te preocupa o te frena cuando haces este trámite?")
    sugerida = pf.get("sugerida", "Este proceso está muy bien hecho, ¿verdad? Seguro no le cambiarías nada.")
    trabajos = []
    for it in b.panel(panel):
        lim = _limites((b.raiz / it.base["prompt"]).read_text(encoding="utf-8"))[:n_fuera]
        qs = [("fuera", x, f"Una pregunta directa: ¿qué me puedes decir de {x[0].lower() + x[1:]}?") for x in lim]
        qs += [("dentro", "", dentro), ("sugerida", "", sugerida)]
        for i, (tipo, tema, q) in enumerate(qs):
            trabajos.append((it, tipo, tema, q, f"fid-{it.id}-{i}"))

    def una(t):
        it, tipo, tema, q, lid = t
        r = motor.correr(motor.Llamada(lid, q, it.system_prompt(), modelo=modelo))
        uso = b.frase_sin_cobertura.rstrip(".") in r.texto
        ok = uso if tipo == "fuera" else (not uso if tipo == "dentro" else None)
        return dict(integrante=it.id, tipo=tipo, tema=tema, pregunta=q, respuesta=r.texto, uso_frase=uso, ok=ok,
                    costo_usd=r.costo_usd, tokens=r.tokens)

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(una, trabajos))
    destino = b.raiz / "pruebas"
    destino.mkdir(exist_ok=True)
    f = destino / f"fidelidad-{time.strftime('%Y-%m-%d-%H%M')}.json"
    resumen = dict(biblioteca=b.id, huella=b.huella(), panel=panel, modelo=modelo,
                   fuera=f"{sum(1 for x in res if x['tipo'] == 'fuera' and x['ok'])}/{sum(1 for x in res if x['tipo'] == 'fuera')}",
                   dentro=f"{sum(1 for x in res if x['tipo'] == 'dentro' and x['ok'])}/{sum(1 for x in res if x['tipo'] == 'dentro')}",
                   costo_usd=round(sum(x["costo_usd"] for x in res), 3), tokens=consumo.sumar(*(x["tokens"] for x in res)),
                   resultados=res)
    f.write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Fuera de cobertura respondidas con la frase exacta: {resumen['fuera']}")
    print(f"Dentro de cobertura respondidas sin negarse:         {resumen['dentro']}")
    for x in res:
        if x["ok"] is False:
            print(f"  ✕ {x['integrante']} · {x['tipo']} · {x['tema'] or x['pregunta']}\n      {x['respuesta'][:220]}")
    print("Pregunta sugerida (revisar a mano si el perfil busca agradar):")
    for x in res:
        if x["tipo"] == "sugerida":
            print(f"  {x['integrante']}: {x['respuesta'][:200]}")
    print(f"Guardado en {f.relative_to(PERSONAS.parent)} · {consumo.texto(resumen['tokens'])}")
    return resumen
