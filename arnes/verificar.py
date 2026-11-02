"""Control final antes de entregar (prompts maestros OU-PWA §25 y skill de auditoría, fase 5).

Errores (bloquean): cifras de KPI que no coinciden con los datos, hallazgos sin la cadena
hallazgo → interpretación → recomendación, falta de limitaciones, reporte desactualizado.
Avisos (no bloquean): palabras que la guía editorial prohíbe salvo evidencia explícita.
"""

from __future__ import annotations

import json
import re

from . import estandares as std
from .estudio import Estudio

# raíces: «demuestr» atrapa demuestra, demuestran, demostró no (se lista aparte)
PROHIBIDAS = ["el peor", "el número uno", r"universal\w*", r"demuestr\w*", r"demostr\w*", r"provoc\w*", r"fracas\w*",
              "todos los usuarios", "nadie", "siempre", "nunca", "es importante señalar", "cabe mencionar", "como podemos observar"]
SIMBOLOS = ["§"]
REQ = ["titular", "veredicto", "kpis", "resumen", "hallazgos", "limitaciones", "fuentes"]


def _x_de_y(v: str):
    m = re.match(r"\s*(\d+)\s*(?:de|/)\s*(\d+)\s*$", str(v))
    return (int(m.group(1)), int(m.group(2))) if m else None


def _textos(N: dict):
    for k, v in N.items():
        if isinstance(v, str):
            yield k, v
        elif isinstance(v, list):
            for i, x in enumerate(v):
                if isinstance(x, str):
                    yield f"{k}[{i}]", x
                elif isinstance(x, dict):
                    for kk, vv in x.items():
                        if isinstance(vv, str):
                            yield f"{k}[{i}].{kk}", vv


def verificar(e: Estudio) -> bool:
    N = e.narrativa()
    err, avi, ok = [], [], []
    if not N:
        print("✕ No hay narrativa.yaml (o está vacía).")
        return False
    for k in REQ:
        (ok if N.get(k) else err).append(f"narrativa: «{k}»" + ("" if N.get(k) else " falta"))
    if len(N.get("resumen") or []) > 10:
        err.append("resumen: más de 10 puntos (máximo 10)")
    agg_f = e.ruta("datos", "agregado.json")
    R = json.loads(agg_f.read_text(encoding="utf-8")) if agg_f.exists() else {}
    # cifras de KPI
    for k in N.get("kpis") or []:
        clave = k.get("verificar")
        if not clave:
            continue
        xy = _x_de_y(k["valor"])
        if e.metodo == "comprension":
            real = (R.get("aciertos") or {}).get(clave)
            real = (real["aciertos"], real["total"]) if real else None
        elif clave.startswith("metrica|"):  # recorrido: "metrica|T1|clics" → mediana de esa métrica
            _, t, nom = clave.split("|")
            m = ((R.get("metricas") or {}).get("tareas") or {}).get(t, {}).get(nom)
            real = None if m is None else (m.get("mediana") if isinstance(m, dict) else m)
            try:
                ok_num = real is not None and abs(float(str(k["valor"]).split()[0].replace(",", "")) - float(real)) < 0.051
            except ValueError:
                ok_num = False
            (ok if ok_num else err).append(f"KPI «{k['valor']} {k['etiqueta']}»" + (" recontado" if ok_num else f": los datos dicen {real}"))
            continue
        else:  # recorrido: "T1|exito" → sesiones con ese resultado / sesiones de la tarea
            t, res = clave.split("|")
            v = (R.get("resultados") or {}).get(t, {})
            real = (v.get(res, 0), sum(v.values())) if v else None
        if real is None:
            err.append(f"KPI «{k['valor']}»: la clave {clave} no existe en datos/agregado.json")
        elif xy != real:
            err.append(f"KPI «{k['valor']} {k['etiqueta']}»: los datos dicen {real[0]} de {real[1]}")
        else:
            ok.append(f"KPI «{k['valor']} {k['etiqueta']}» recontado")
            cel = ((R.get("estabilidad") or {}).get("celdas") or {}).get(clave) if e.metodo == "comprension" else None
            if cel and cel["inestables"]:
                avi.append(f"KPI «{k['valor']} {k['etiqueta']}»: {cel['inestables']} de {cel['perfiles']} perfiles cambian de respuesta "
                           "entre corridas en esa celda (creer en lo que se repite)")
            if e.metodo == "comprension" and not (R.get("estabilidad") or {}).get("global_"):
                avi.append(f"KPI «{k['valor']} {k['etiqueta']}»: una sola corrida por celda, no se sabe si se repite")
        if k.get("compara"):
            from .robustez import comparar

            cmp = comparar(R.get("aciertos") or {}, *k["compara"])
            if not cmp:
                err.append(f"KPI «{k['valor']}»: no encuentro las claves de `compara` en agregado.json")
            elif not cmp["clara"]:
                avi.append(f"KPI «{k['valor']} {k['etiqueta']}»: brecha de {abs(cmp['brecha']) * 100:.0f} puntos con intervalos que se "
                           f"solapan ({cmp['ic_a']} vs {cmp['ic_b']}). No presentarla como diferencia: es no concluyente")
    # hallazgos
    ids_ses = {p.stem for p in e.sesiones_dir.glob("*.json")} if e.sesiones_dir.exists() else set()
    for h in N.get("hallazgos") or []:
        hid = h.get("id", h.get("titulo", "?"))
        falta = [c for c in ("hallazgo", "interpretacion", "recomendacion", "evidencia") if not h.get(c)]
        if falta:
            err.append(f"hallazgo {hid}: falta {', '.join(falta)}")
        if not 0 <= int(h.get("severidad", -1)) <= 4:
            err.append(f"hallazgo {hid}: severidad fuera de 0–4")
        if h.get("confianza") not in ("alta", "media", "baja"):
            err.append(f"hallazgo {hid}: confianza debe ser alta, media o baja")
        if len(str(h.get("titulo", "")).split()) < 4:
            avi.append(f"hallazgo {hid}: el título parece un tema, no una conclusión")
        malas = [s for s in h.get("sesiones") or [] if s not in ids_ses]
        if malas:
            err.append(f"hallazgo {hid}: sesiones inexistentes {malas[:4]}")
        if h.get("walkthrough") and int(h["walkthrough"]) not in (1, 2, 3, 4):
            err.append(f"hallazgo {hid}: walkthrough debe ser 1–4 (las cuatro preguntas del cognitive walkthrough)")
        if h.get("oportunidad") and h["oportunidad"] not in std.oportunidades():
            err.append(f"hallazgo {hid}: oportunidad debe ser {', '.join(std.oportunidades())}")
        elif not h.get("oportunidad"):
            avi.append(f"hallazgo {hid}: sin «oportunidad» (Mantener · Mejorar · Incorporar · Hacer diferente)")
        if e.metodo == "recorrido" and h.get("categoria") not in ("A", "C"):
            err.append(f"hallazgo {hid}: en recorridos solo entran categorías A (diseño) o C (cableado); B y D van aparte")
    for x in (R.get("homogeneidad") or {}).get("alertas", []) + (R.get("robustez") or {}).get("alertas", []):
        avi.append(f"datos: {x}")
    # estándares de UiX
    e_n, a_n = std.revisar_naming(e.cfg, e.metodo)
    err += [f"naming: {x}" for x in e_n]
    avi += [f"naming: {x}" for x in a_n]
    if not e_n and not a_n:
        ok.append(f"naming de UiX: {e.entregable()}")
    avi += [f"demográficos: {x}" for x in std.revisar_demograficos(e.panel())]
    if not N.get("aprendizajes_metodo"):
        avi.append("sin «aprendizajes_metodo»: es lo que la síntesis lleva al vault")
    if not N.get("positivos"):
        avi.append("no hay hallazgos positivos («positivos»)")
    # reporte editorial (recorrido): cifras recontadas, citas textuales, casos y enlaces
    editoriales = []
    if e.metodo == "recorrido" and agg_f.exists() and not (N.get("presentacion") or {}).get("html_local"):
        from .reporte import editorial

        o_, a_, e_ = editorial.revisar(e, N)
        ok, avi, err = ok + o_, avi + a_, err + e_
        editoriales = list(editorial.textos(editorial.cargar(e)))
    # lenguaje
    for donde, t in list(_textos(N)) + editoriales:
        tl = t.lower()
        for w in PROHIBIDAS:
            m = re.search(rf"\b{w}\b", tl)
            if m:
                avi.append(f"{donde}: «{m.group(0)}» (guía editorial: solo con evidencia explícita)")
        for s in SIMBOLOS:
            if s in t:
                err.append(f"{donde}: símbolo críptico «{s}»")
    # sesiones fallidas
    reg = e.ruta("datos", "registro-sesiones.jsonl")
    if reg.exists():
        ult = {}
        for x in reg.read_text(encoding="utf-8").splitlines():
            if x.strip():
                j = json.loads(x)
                ult[j["id"]] = j
        fall = [i for i, j in ult.items() if not j.get("ok")]
        (err if fall else ok).append(f"sesiones fallidas sin repetir: {fall[:6]}" if fall else f"{len(ult)} sesiones registradas, ninguna fallida pendiente")
    # reporte
    rep = e.ruta("reporte", f"{e.entregable()}.html")
    if not rep.exists():
        err.append("no existe el reporte: corre `arnes reporte`")
    else:
        h = rep.read_text(encoding="utf-8")
        nar = e.ruta("narrativa.yaml")
        edi = e.ruta("editorial.yaml")
        if any(f.exists() and f.stat().st_mtime > rep.stat().st_mtime for f in (nar, agg_f)) or (edi.exists() and not (N.get("presentacion") or {}).get("html_local") and edi.stat().st_mtime > rep.stat().st_mtime):
            err.append("el reporte es más viejo que narrativa.yaml, editorial.yaml o agregado.json: vuelve a correr `arnes reporte`")
        # el reporte editorial lleva todos los hallazgos en sus lecturas, no en la página principal
        lecturas = rep.parent / "assets/report-reader/data"
        visibles = h + "".join(lecturas.joinpath(f).read_text(encoding="utf-8") for f in ("hallazgos.js", "sintesis.js") if lecturas.joinpath(f).exists())
        for x in N.get("hallazgos") or []:
            if x.get("id") and not re.search(rf'id=\\?"{x["id"]}\\?"|"id":"{x["id"]}"', visibles):
                err.append(f"el reporte no incluye el hallazgo {x['id']}")
        for need, msg in (('<meta charset="utf-8">', "charset"), ("Investigación sintética", "aviso de investigación sintética"),
                          ('<html lang="es">', "idioma")):
            (ok if need in h else err).append(f"reporte: {msg}")
        kb = len(h.encode()) / 1024
        (avi if kb > 12000 else ok).append(f"reporte: {kb:.0f} KB")
    for x in ok:
        print(f"  ✓ {x}")
    for x in avi:
        print(f"  ! {x}")
    for x in err:
        print(f"  ✕ {x}")
    print(f"\n{'LISTO PARA ENTREGAR' if not err else 'NO ENTREGAR TODAVÍA'} · {len(err)} errores · {len(avi)} avisos")
    if not err:
        e.marcar("verificar", avisos=len(avi))
    return not err
