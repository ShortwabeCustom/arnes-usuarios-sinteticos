"""Método 2 · Comprensión de pantallas estáticas (A/B, vistazo vs. lectura completa).

Consolida los dos estudios de recompra. Fases:

    0  medir      zonas, alto de línea, contraste, pliegue                       [EVIDENCIA]
    2  medir      atención predicha (saliencia)                                  [MODELO]
    3  medir      puntos de lectura por integrante: reglas del persona + OCEAN   [EVIDENCIA + SIMULACIÓN]
    4  sesiones   una sesión = integrante × pantalla × modo × corrida, contexto limpio  [SIMULACIÓN]
    4b sesiones   comparación pareada (opcional) y control de sensibilidad OCEAN (opcional)
    5  analizar   agregados por celda, aciertos contra la respuesta correcta, sin cobertura

La Fase 1 (auditoría de UX writing) es juicio experto: va en narrativa.yaml, no en código.
"""

from __future__ import annotations

import collections
import csv
import json

from .. import medir as M
from .. import motor, robustez
from ..estudio import Estudio

# Texto validado en los estudios de recompra. Cambiar la redacción cambia las respuestas: con una
# lista de preguntas en vez de la plantilla JSON, el vistazo del Estudio 1 pasó de «sí» a «no sé» en
# 6 de 8 perfiles (prueba del 20 de octubre de 2026). No reescribir sin volver a validar.
REGLAS_SESION = """

## Reglas de esta sesión de prueba

- Usa solo lo que se te muestra. No supongas funciones, políticas ni pasos que no aparezcan.
- No completes información que falte. Si algo es ambiguo o se contradice, dilo.
- No intentes agradar a quien pregunta ni adivinar qué respuesta espera.
{nombre_ejemplo}- Si una pregunta cae fuera de lo que tu perfil cubre, usa la frase exacta de tu rol y anota la pregunta en "sin_cobertura".
- Responde únicamente con un objeto JSON válido, sin texto antes ni después y sin bloque de código."""


def tam(px: int | None) -> str:
    if not px:
        return "texto"
    return "letra muy grande" if px > 30 else "letra mediana" if px >= 16 else "letra chica" if px >= 13 else "letra muy chica"


# ---------------------------------------------------------------------------------------------
# Fases 0, 2 y 3


def medir(e: Estudio) -> dict:
    c = e.cfg
    out = dict(pantallas={}, lectura={})
    pl = tuple(c.get("pliegues", [640, 800]))
    for pid, p in c["pantallas"].items():
        img = e.ruta(p["imagen"])
        out["pantallas"][pid] = M.medir_pantalla(img, c["zonas"][pid], pl, p.get("recorte_superior", 0),
                                                 salida_mapa=e.ruta("heatmaps", f"atencion-{pid}.png"),
                                                 orden_por_pliegue=c.get("orden_por_pliegue", True))
    vel = tuple(c.get("velocidades", [2.5, 3.5, 4.5]))
    for it in e.panel():
        cfg = M.config_lectura(it)
        for pid, med in out["pantallas"].items():
            out["lectura"].setdefault(pid, {})[it.id] = M.puntos_de_lectura(
                med, cfg, vel, c.get("velocidad_base", 3.5), vistazo_sin_scroll=c.get("orden_por_pliegue", True))
    e.ruta("datos", "medicion.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(e.ruta("datos", "aoi.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pantalla", "zona", "nombre", "rol", "x0", "y0", "x1", "y1", "palabras", "alto_px", "contraste",
                    *[f"visible_{p}" for p in pl], "saliencia_pct", "densidad", "rango"])
        for pid, med in out["pantallas"].items():
            for k, z in med["zonas"].items():
                w.writerow([pid, k, z["nombre"], z["rol"], *z["caja"], z["palabras"], z["alto_px"], z["contraste"],
                            *[z["visible"][str(p)] for p in pl], z["porcion"], z["densidad"], z["rango_saliencia"]])
    e.marcar("medir", pantallas=len(out["pantallas"]), integrantes=len(e.panel()))
    for pid, med in out["pantallas"].items():
        print(f"\n{pid}  {med['ancho']}×{med['alto']}  orden: {' > '.join(med['orden'])}")
        for k, z in med["zonas"].items():
            print(f"   {k:16s} {z['rol']:11s} sal {z['porcion']:5.1f}%  dens {z['densidad']:4.2f}  alto {z['alto_px']}  "
                  f"contr {z['contraste']}  " + "  ".join(f"{p}:{v}" for p, v in z["visible"].items()))
    return out


# ---------------------------------------------------------------------------------------------
# Fase 4


def _esquema(preguntas: list[dict]) -> dict:
    props, req = {}, []
    for q in preguntas:
        if q.get("opciones"):
            props[q["id"]] = {"type": "object", "additionalProperties": False, "required": ["opcion", "texto"],
                              "properties": {"opcion": {"type": "string", "enum": q["opciones"]},
                                             "texto": {"type": "string"}}}
        else:
            props[q["id"]] = {"type": "string"}
        req.append(q["id"])
    props["reglas"] = {"type": "array", "items": {"type": "string"}}
    props["sin_cobertura"] = {"type": "array", "items": {"type": "string"}}
    return {"type": "object", "additionalProperties": False, "required": req + ["reglas", "sin_cobertura"], "properties": props}


def _plantilla(preguntas: list[dict]) -> str:
    """Plantilla JSON en línea, como en los estudios de recompra: la opción va dentro del campo."""
    q = []
    for x in preguntas:
        t = x["texto"].replace('"', "'")
        q.append(f'"{x["id"]}": {{"opcion": "{" | ".join(x["opciones"])}", "texto": "{t}"}}' if x.get("opciones")
                 else f'"{x["id"]}": "{t}"')
    q += ['"reglas": ["ids de las reglas conductuales de tu perfil que aplicaste, p. ej. B-07"]',
          '"sin_cobertura": ["ids de pregunta que tu perfil no cubre"]']
    return "{\n  " + ",\n  ".join(q) + "\n}"


FORMATO = 'Responde con este formato, en primera persona; en los campos con "opcion" elige una sola y explica en "texto":'


def _preguntas_de(c: dict, grupo: str, ids: list[str] | None = None) -> list[dict]:
    qs = [q for q in c["preguntas"] if not q.get("solo") or grupo in q["solo"]]
    if ids:
        return [q for q in qs if q["id"] in ids]
    return [q for q in qs if not q.get("solo_continuacion")]


def _estimulo_vistazo(c, med, lect, pid, vel) -> str:
    z = med["pantallas"][pid]["zonas"]
    lin = []
    for k, n in lect["vistazo"][vel]:
        if z[k]["rol"] == "ilustracion":
            lin.append(f"(miraste {c['zonas'][pid][k].get('descripcion', 'la ilustración')})")
            continue
        pal = z[k]["texto"].split()
        txt = " ".join(pal[:n]) + ("…  (hasta ahí llegaste)" if n < len(pal) else "")
        etiqueta = "botón" if z[k]["rol"] == "accion" else "enlace" if z[k]["rol"] == "enlace" else tam(z[k]["alto_px"])
        lin.append(f"[{etiqueta}] «{txt}»")
    return "\n".join(f"{i + 1}. {x}" for i, x in enumerate(lin)) or "(no alcanzaste a leer ningún texto)"


def _tabla_tamanos(med, pid) -> str:
    return "\n".join(f"- «{z['texto']}»: {z['alto_px']} px de alto de línea"
                     for z in med["pantallas"][pid]["zonas"].values() if z["es_texto"] and z["alto_px"])


def trabajos(e: Estudio, filtro: str = "") -> list[tuple[str, callable]]:
    c = e.cfg
    med = json.loads(e.ruta("datos", "medicion.json").read_text(encoding="utf-8"))
    panel = e.panel()
    modelo = c.get("modelo", "sonnet")
    vel = str(c.get("velocidad_vistazo", 3.5))
    ej = c.get("nombre_de_ejemplo")
    reglas = c.get("reglas_sesion", REGLAS_SESION).replace(
        "{nombre_ejemplo}", f"- La pantalla usa «{ej}» como nombre de ejemplo; léelo como si dijera el tuyo.\n" if ej else "")
    out = []

    def sesion(bloque, it, pid, modo, n, con_ocean=True):
        p = c["pantallas"][pid]
        grupo, var = p.get("grupo", "E"), p.get("variante", pid)
        sid = f"{bloque[:3]}-{pid}-{it.id}-{modo}-{n}"
        qs = _preguntas_de(c, grupo)
        sistema = it.system_prompt(reglas, con_ocean=con_ocean)

        def fn():
            reg = dict(id=sid, bloque=bloque, grupo=grupo, variante=var, pantalla=pid, integrante=it.id,
                       perfil=it.perfil, modo=modo, corrida=n, con_ocean=con_ocean and bool(it.ocean), modelo=modelo)
            ctx = " ".join(c["consigna"].split())
            if modo == "vistazo":
                est = _estimulo_vistazo(c, med, med["lectura"][pid][it.id], pid, vel)
                reg["estimulo"] = est
                prompt = (f"{ctx} Solo alcanzaste a mirarla unos cinco segundos. Esto es lo que alcanzaste a leer, en el "
                          f"orden en que lo leíste:\n\n{est}\n\nLo demás no lo alcanzaste a leer. {FORMATO}\n\n{_plantilla(qs)}")
                archivos, herr = [], []
            else:
                img = e.ruta(p["imagen"])
                prompt = (f"{ctx} La pantalla es la imagen `{img.name}` de esta carpeta: ábrela con la herramienta Read y "
                          f"mírala completa, con calma, antes de contestar. Es del tamaño de tu celular "
                          f"({med['pantallas'][pid]['ancho']} px de ancho). Alto de las líneas de texto, medido en la imagen:\n"
                          f"{_tabla_tamanos(med, pid)}\n\n{FORMATO}\n\n{_plantilla(qs)}")
                archivos, herr = [img], ["Read"]
            conts = [k for k in c.get("continuaciones", []) if modo in k.get("tras", ["completa"])
                     and (not k.get("solo") or grupo in k["solo"])] if bloque == "principal" else []
            r = motor.llamar(motor.Llamada(sid, prompt, sistema, _esquema(qs), herr, archivos, modelo=modelo,
                                           persistir=bool(conts)))
            reg["respuestas"], costo, ses = r.salida, r.costo_usd, r.session_id
            reg["modelo_id"] = r.modelo_id
            for k in conts:
                q2 = _preguntas_de(c, grupo, k["preguntas"])
                img2 = e.ruta(k["imagen"])
                p2 = (f"{k['consigna'].strip()} Es la imagen `{img2.name}`: ábrela con Read y léela. Después contesta de nuevo, "
                      f"con el mismo formato JSON y solo estas claves:\n\n{_plantilla(q2)}")
                r2 = motor.llamar(motor.Llamada(f"{sid}+{k['id']}", p2, sistema, _esquema(q2), ["Read"], [img2],
                                                reanudar=ses, modelo=modelo, persistir=True))
                reg.setdefault("continuaciones", {})[k["id"]] = r2.salida
                costo += r2.costo_usd
            reg["costo_usd"] = round(costo, 4)
            return reg

        out.append((sid, fn))

    corr = range(1, c.get("corridas", 3) + 1)
    for it in panel:
        for pid in c["pantallas"]:
            for modo in c.get("modos", ["vistazo", "completa"]):
                for n in corr:
                    sesion("principal", it, pid, modo, n)
    sens = c.get("sensibilidad_ocean")
    if sens:
        for it in panel:
            if it.ocean and not it.variante:
                for pid in c["pantallas"]:
                    for modo in sens.get("modos", ["vistazo"]):
                        for n in corr:
                            sesion("sensibilidad", it, pid, modo, n, con_ocean=False)
    par = c.get("pareada")
    if par:
        out += _pareadas(e, panel, par, modelo, reglas)
    return [t for t in out if filtro in t[0]]


def _pareadas(e, panel, par, modelo, reglas):
    c = e.cfg
    out = []
    for g, (a, b) in par["pares"].items():
        for it in panel:
            for orden in ((a, b), (b, a)):
                for n in range(1, par.get("corridas", 2) + 1):
                    sid = f"par-{g}-{it.id}-{''.join(c['pantallas'][x].get('variante', x) for x in orden)}-{n}"
                    imgs = [e.ruta(c["pantallas"][x]["imagen"]) for x in orden]
                    qs = [dict(q, opciones=q.get("opciones") or ["primera", "segunda", "igual"]) for q in par["preguntas"]]

                    def fn(sid=sid, it=it, orden=orden, imgs=imgs, qs=qs):
                        prompt = (f"{c['consigna'].strip()}\n\nTe mostramos dos versiones de la misma pantalla. Ábrelas con Read "
                                  f"en este orden: primera `{imgs[0].name}`, segunda `{imgs[1].name}`. Míralas completas.\n\n"
                                  f"{FORMATO}\n\n{_plantilla(qs)}")
                        r = motor.llamar(motor.Llamada(sid, prompt, it.system_prompt(reglas), _esquema(qs), ["Read"], imgs,
                                                       modelo=modelo))
                        m = {"primera": c["pantallas"][orden[0]].get("variante", orden[0]),
                             "segunda": c["pantallas"][orden[1]].get("variante", orden[1]), "igual": "igual"}
                        resp = {k: (dict(v, opcion=m.get(v["opcion"], v["opcion"])) if isinstance(v, dict) else v)
                                for k, v in r.salida.items()}
                        return dict(id=sid, bloque="pareada", grupo=g, variante="".join(m[x] for x in ("primera", "segunda")),
                                    pantalla="+".join(orden), integrante=it.id, perfil=it.perfil, modo="pareada",
                                    corrida=int(sid.rsplit("-", 1)[1]), con_ocean=bool(it.ocean), modelo=modelo,
                                    respuestas=resp, costo_usd=round(r.costo_usd, 4), modelo_id=r.modelo_id)

                    out.append((sid, fn))
    return out


def sesiones(e: Estudio, filtro: str = "", simular: bool = False, paralelo: int | None = None, piloto: bool = False) -> dict:
    ts = trabajos(e, filtro)
    if piloto:  # estudio piloto: primer integrante, corrida 1, solo bloque principal
        primero = e.panel()[0].id
        ts = [t for t in ts if t[0].startswith("pri-") and f"-{primero}-" in t[0] and t[0].endswith("-1")]
        print(f"Piloto: {primero}, corrida 1. Revisa estímulos y respuestas en datos/sesiones/ antes de correr el resto.")
    if simular:
        hechas = sum((e.sesiones_dir / f"{i}.json").exists() for i, _ in ts)
        print(f"{len(ts)} sesiones planeadas · {hechas} ya corridas")
        for i, _ in ts[:12]:
            print("  ", i)
        if len(ts) > 12:
            print(f"   … y {len(ts) - 12} más")
        return dict(planeadas=len(ts), hechas=hechas)
    r = motor.ejecutar(ts, e.sesiones_dir, paralelo or e.cfg.get("paralelo", 6), e.ruta("datos", "registro-sesiones.jsonl"))
    e.marcar("sesiones", **r)
    return r


# ---------------------------------------------------------------------------------------------
# Fase 5


def analizar(e: Estudio) -> dict:
    c = e.cfg
    S = list(motor.cargar(e.sesiones_dir).values())
    correctas = {q["id"]: q["correcta"] for q in c["preguntas"] if q.get("correcta")}
    filas = [["id", "bloque", "grupo", "variante", "integrante", "perfil", "modo", "corrida", "con_ocean", "momento",
              "pregunta", "opcion", "correcta", "acierto", "texto", "reglas", "sin_cobertura"]]
    agg = collections.defaultdict(list)
    aciertos = collections.defaultdict(lambda: [0, 0])
    sin_cob = collections.Counter()
    reglas = collections.Counter()
    for s in S:
        momentos = [("antes", s.get("respuestas") or {})] + list((s.get("continuaciones") or {}).items())
        for mom, r in momentos:
            for rid in r.get("reglas", []):
                reglas[(s["integrante"], rid)] += 1
            for q in r.get("sin_cobertura", []):
                sin_cob[(s["integrante"], q)] += 1
            for k, v in r.items():
                if k in ("reglas", "sin_cobertura"):
                    continue
                o = v.get("opcion", "") if isinstance(v, dict) else ""
                t = v.get("texto", "") if isinstance(v, dict) else v
                cor = correctas.get(k, {}).get(s["grupo"]) if isinstance(correctas.get(k), dict) else correctas.get(k)
                cor_m = cor.get(mom) if isinstance(cor, dict) else cor  # la correcta puede cambiar tras una continuación
                ac = "" if not cor_m or not o else int(o in (cor_m if isinstance(cor_m, list) else [cor_m]))
                filas.append([s["id"], s["bloque"], s["grupo"], s["variante"], s["integrante"], s["perfil"], s["modo"],
                              s["corrida"], s["con_ocean"], mom, k, o, cor_m or "", ac, t,
                              " ".join(r.get("reglas", [])), " ".join(map(str, r.get("sin_cobertura", [])))])
                if o:
                    agg["|".join(map(str, (s["bloque"], s["grupo"], s["variante"], s["integrante"], s["modo"], mom, k)))].append(o)
                if ac != "":
                    a = aciertos["|".join(map(str, (s["bloque"], s["grupo"], s["variante"], s["modo"], mom, k)))]
                    a[0] += ac
                    a[1] += 1
    with open(e.ruta("datos", "respuestas.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(filas)
    abiertas = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in filas[1:]:
        if not r[11] and r[14] and r[1] == "principal":  # pregunta abierta: sin opción, con texto
            abiertas["|".join(map(str, (r[1], r[2], r[3], r[6], r[9], r[10])))][r[4]].append(r[14])
    acierto_d = {k: dict(aciertos=a, total=t) for k, (a, t) in aciertos.items()}
    res = dict(
        n_sesiones=len(S),
        n_por_bloque=dict(collections.Counter(s["bloque"] for s in S)),
        agregado=dict(agg),
        aciertos=acierto_d,
        sin_cobertura=[dict(integrante=i, pregunta=q, n=n) for (i, q), n in sin_cob.most_common()],
        reglas=[dict(integrante=i, regla=r, n=n) for (i, r), n in reglas.most_common()],
        estabilidad=robustez.estabilidad(agg),
        comparaciones=robustez.comparaciones(acierto_d),
        homogeneidad=robustez.homogeneidad(agg, {k: dict(v) for k, v in abiertas.items()}),
    )
    e.ruta("datos", "agregado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    e.marcar("analizar", sesiones=len(S))
    print(f"{len(S)} sesiones · {sum(res['n_por_bloque'].values())} por bloque: {res['n_por_bloque']}")
    for k, v in sorted(res["aciertos"].items()):
        print(f"   {k:55s} {v['aciertos']:3d} de {v['total']:3d}")
    if res["sin_cobertura"]:
        print("sin cobertura:", ", ".join(f"{x['integrante']}·{x['pregunta']}×{x['n']}" for x in res["sin_cobertura"][:10]))
    est = res["estabilidad"]
    if est["global_"] is not None:
        print(f"estabilidad entre corridas: {est['global_']:.0%} · {len(est['inestables'])} perfil-celdas cambian de respuesta")
    else:
        print("estabilidad: una sola corrida por celda, no se puede medir (correr 2–3 para saber qué se repite)")
    claras = [c for c in res["comparaciones"] if c["clara"]]
    print(f"comparaciones entre variantes: {len(claras)} de {len(res['comparaciones'])} con brecha clara (intervalos de Wilson sin solaparse)")
    for a in res["homogeneidad"]["alertas"]:
        print("! " + a)
    return res
